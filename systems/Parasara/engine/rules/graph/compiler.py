"""Sole graph compiler and deterministic planner for compiled DSL rules."""
from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping
import hashlib
import heapq
import re

from systems.Parasara.engine.rules.canonical import FrozenMapping
from systems.Parasara.engine.rules.graph.runtime_contract import GRAPH_CONTRACT_DATA, GRAPH_CONTRACT_SHA256, LIMITS, KINDS, digest
from systems.Parasara.engine.rules.graph.models import (
    RuleNodeKey, DependencyKind, DependencyDeclaration, DiagnosticCollector,
    GraphAnalysis, GraphAnalysisSucceeded, GraphCompilationFailed, GraphCompilationSucceeded,
    diagnostic, _new_plan,
)
from systems.Parasara.engine.rules.graph.parser import parse_graph_source

GRAPH_COMPILER_IMPLEMENTATION_MODULE_IDS = (
    "graph/__init__.py", "graph/models.py", "graph/parser.py", "graph/compiler.py", "graph/runtime_contract.py",
)
GRAPH_COMPILER_CONTENT_SHA256 = "b0b4166f8112861f5767a9cf23f307f89318da6eadb3653163a449f62de6c407"


def compiler_component_fingerprint_sha256(module_sources, *, contract_data=GRAPH_CONTRACT_DATA):
    if not isinstance(module_sources, Mapping) or set(module_sources) != set(GRAPH_COMPILER_IMPLEMENTATION_MODULE_IDS):
        raise ValueError("exact graph implementation module IDs required")
    rows = []
    for name in GRAPH_COMPILER_IMPLEMENTATION_MODULE_IDS:
        payload = module_sources[name]
        text = payload.decode("utf-8", "strict") if isinstance(payload, bytes) else payload
        if not isinstance(text, str):
            raise TypeError("module contents must be UTF-8 bytes or text")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        if name == "graph/compiler.py":
            text, count = re.subn(r'^GRAPH_COMPILER_CONTENT_SHA256 = "[0-9a-f]{64}"$',
                'GRAPH_COMPILER_CONTENT_SHA256 = "<SELF>"', text, flags=re.MULTILINE)
            if count != 1:
                raise ValueError("exactly one published graph digest literal required")
        rows.append(dict(module_id=name, content_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest()))
    return digest(dict(compiler_contract=contract_data, implementation_modules=rows))


def _topology(nodes, edges, collector):
    count = len(nodes)
    outgoing, incoming = [[] for _ in nodes], [[] for _ in nodes]
    for edge in edges:
        outgoing[edge.prerequisite].append(edge.dependent)
        incoming[edge.dependent].append(edge.prerequisite)
    for values in (*outgoing, *incoming):
        values.sort()
    indegree = [len(values) for values in incoming]
    ready = [i for i in range(count) if not indegree[i]]
    heapq.heapify(ready)
    order, depths = [], [1] * count
    while ready:
        current = heapq.heappop(ready)
        order.append(current)
        for target in outgoing[current]:
            depths[target] = max(depths[target], depths[current] + 1)
            indegree[target] -= 1
            if not indegree[target]:
                heapq.heappush(ready, target)
    if len(order) != count:
        # Iterative Kosaraju; all discovery sequences explicitly sorted.
        visited, finished = set(), []
        for root in range(count):
            if root in visited:
                continue
            visited.add(root)
            stack = [(root, iter(outgoing[root]))]
            while stack:
                node, neighbors = stack[-1]
                neighbor = next(neighbors, None)
                if neighbor is None:
                    finished.append(node)
                    stack.pop()
                elif neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, iter(outgoing[neighbor])))
        assigned, components = set(), []
        for root in reversed(finished):
            if root in assigned:
                continue
            assigned.add(root)
            stack, members = [root], []
            while stack:
                node = stack.pop()
                members.append(node)
                for neighbor in reversed(incoming[node]):
                    if neighbor not in assigned:
                        assigned.add(neighbor)
                        stack.append(neighbor)
            if len(members) > 1:
                components.append(tuple(sorted(members)))
        for members in sorted(components):
            start = members[0]
            allowed, visited, parent = set(members), {start}, {}
            stack = [(start, iter(outgoing[start]))]
            witness = None
            while stack and witness is None:
                node, neighbors = stack[-1]
                neighbor = next(neighbors, None)
                if neighbor is None:
                    stack.pop()
                elif neighbor == start:
                    chain = [node]
                    while chain[-1] != start:
                        chain.append(parent[chain[-1]])
                    witness = tuple(reversed(chain)) + (start,)
                elif neighbor in allowed and neighbor not in visited:
                    parent[neighbor] = node
                    visited.add(neighbor)
                    stack.append((neighbor, iter(outgoing[neighbor])))
            collector.add("P08E201_CYCLE", stage="cycles", node_source_order=start,
                details=dict(members=members, witness=witness))
        return ()
    if max(depths) > LIMITS["graph_depth"]:
        collector.add("P08E401_LIMIT_VIOLATION", stage="planning", details=dict(
            resource="graph_depth", limit=LIMITS["graph_depth"], observed=max(depths)))
    return tuple(order)


class RuleGraphCompiler:
    __slots__ = ("_resolved_versions", "_cache", "_cache_capacity")

    def __init__(self, *, resolved_versions, cache_capacity=LIMITS["cache_entries"]):
        from systems.Parasara.engine.versioning import ResolvedEvaluationVersions
        if not isinstance(resolved_versions, ResolvedEvaluationVersions):
            raise TypeError("graph compiler requires resolved authority")
        if type(cache_capacity) is not int or not 0 <= cache_capacity <= LIMITS["cache_entries"]:
            raise ValueError("graph cache capacity must be 0 or 1")
        self._resolved_versions, self._cache_capacity = resolved_versions, cache_capacity
        self._cache = OrderedDict()

    @property
    def cache_size(self):
        return len(self._cache)

    @property
    def cache_capacity(self):
        return self._cache_capacity

    @staticmethod
    def analyze_source(*, source_id, payload, analyzed_rule_set, dsl_source_artifact_id):
        from systems.Parasara.engine.rules.dsl import AnalyzedRuleSet
        positions = ({r.resolved_rule.rule_id: i for i, r in enumerate(analyzed_rule_set.rules)}
            if isinstance(analyzed_rule_set, AnalyzedRuleSet) else {})
        parsed = parse_graph_source(source_id=source_id, payload=payload, rule_positions=positions)
        if isinstance(parsed, GraphCompilationFailed):
            return parsed
        c = DiagnosticCollector(source_id)
        doc = parsed.document
        if not isinstance(analyzed_rule_set, AnalyzedRuleSet):
            return GraphCompilationFailed((diagnostic("P08E107_MEMBERSHIP_MISMATCH", stage="membership", source_id=source_id),))
        dsl = analyzed_rule_set
        for name in ("system", "rule_set_family", "rule_set_version"):
            if doc[name] != getattr(dsl.document, name):
                c.add("P08E103_VERSION_MISMATCH", stage="membership", field_path="$." + name)
        count = len(dsl.rules)
        graph_count = len(doc["rules"])
        if graph_count < LIMITS["nodes_minimum"]:
            c.add("P08E401_LIMIT_VIOLATION", stage="membership", details=dict(
                resource="nodes", limit=LIMITS["nodes_minimum"], observed=graph_count))
        elif graph_count > LIMITS["nodes"]:
            c.add("P08E401_LIMIT_VIOLATION", stage="membership", details=dict(
                resource="nodes", limit=LIMITS["nodes"], observed=graph_count))
        if graph_count != count or len({r.resolved_rule.rule_id for r in dsl.rules}) != count:
            c.add("P08E107_MEMBERSHIP_MISMATCH", stage="membership")
        if not isinstance(dsl_source_artifact_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.@/-]{0,255}", dsl_source_artifact_id):
            c.add("P08E107_MEMBERSHIP_MISMATCH", stage="membership")
        by_id = {r.resolved_rule.rule_id: i for i, r in enumerate(dsl.rules)}
        rows, seen = {}, set()
        for row in sorted(doc["rules"], key=lambda r: (by_id.get(r["rule_id"], LIMITS["nodes"]), r["rule_id"], r["revision"])):
            i = by_id.get(row["rule_id"])
            if i is None or row["rule_id"] in seen:
                c.add("P08E107_MEMBERSHIP_MISMATCH", stage="membership", node_source_order=i)
            elif row["revision"] != dsl.rules[i].resolved_rule.rule_version:
                c.add("P08E102_REVISION_MISMATCH", stage="membership", node_source_order=i)
            else:
                rows[i] = row
            seen.add(row["rule_id"])
        for i, r in enumerate(dsl.rules):
            if r.resolved_rule.evaluation_plan_position != i:
                c.add("P08E107_MEMBERSHIP_MISMATCH", stage="membership", node_source_order=i)
        if c.items:
            return GraphCompilationFailed(c.finish())
        nodes = tuple(RuleNodeKey(system=doc["system"], rule_set_family=doc["rule_set_family"], rule_set_version=doc["rule_set_version"],
            rule_id=r.resolved_rule.rule_id, revision=r.resolved_rule.rule_version, dsl_compiled_semantic_sha256=r.compiled_semantic_sha256,
            source_artifact_id=dsl_source_artifact_id, source_identity=dsl.document.source_id,
            source_artifact_semantic_sha256=dsl.canonical_dsl_sha256, source_order=i) for i, r in enumerate(dsl.rules))
        edges = []
        for i in range(count):
            row, pairs = rows[i], {}
            total = sum(len(row[k]) for k in KINDS)
            if total > LIMITS["dependencies_per_node"]:
                c.add("P08E401_LIMIT_VIOLATION", stage="edges", node_source_order=i, details=dict(
                    resource="dependencies_per_node", limit=LIMITS["dependencies_per_node"], observed=total))
            for kind in KINDS:
                references = sorted(row[kind], key=lambda r: (by_id.get(r["rule_id"], LIMITS["nodes"]), r["rule_id"], r["revision"]))
                for ref in references:
                    j = by_id.get(ref["rule_id"])
                    kwargs = dict(stage="edges", node_source_order=i, prerequisite_source_order=j,
                        field_path=f"$.rules[{i}].{kind}")
                    if j is None:
                        c.add("P08E101_UNKNOWN_DEPENDENCY", **kwargs, details=dict(ref))
                    elif ref["revision"] != nodes[j].revision:
                        c.add("P08E102_REVISION_MISMATCH", **kwargs, details=dict(ref))
                    elif j in pairs:
                        c.add("P08E104_DUPLICATE_DEPENDENCY" if pairs[j] == kind else "P08E105_CONFLICTING_DEPENDENCY", **kwargs)
                    elif i == j:
                        c.add("P08E106_SELF_DEPENDENCY", **kwargs)
                    elif dsl.rules[i].resolved_rule.domains != dsl.rules[j].resolved_rule.domains:
                        c.add("P08E108_CROSS_DOMAIN_DEPENDENCY", **kwargs)
                    else:
                        edges.append(DependencyDeclaration(prerequisite=j, dependent=i, kind=DependencyKind(kind)))
                    if j is not None:
                        pairs[j] = kind
        total = sum(sum(len(r[k]) for k in KINDS) for r in rows.values())
        if total > LIMITS["edges"]:
            c.add("P08E401_LIMIT_VIOLATION", stage="edges", details=dict(resource="edges", limit=LIMITS["edges"], observed=total))
        if c.items:
            return GraphCompilationFailed(c.finish())
        edges = tuple(sorted(edges, key=lambda e: (e.prerequisite, e.dependent, KINDS.index(e.kind))))
        order = _topology(nodes, edges, c)
        if c.items:
            return GraphCompilationFailed(c.finish())
        normalized = dict(doc)
        normalized["rules"] = tuple(dict(rule_id=r["rule_id"], revision=r["revision"], **{
            k: tuple(sorted(r[k], key=lambda ref: (ref["rule_id"], ref["revision"]))) for k in KINDS
        }) for r in sorted(doc["rules"], key=lambda r: (r["rule_id"], r["revision"])))
        return GraphAnalysisSucceeded(GraphAnalysis(source_id=source_id, source_raw_sha256=parsed.source_raw_sha256,
            document=FrozenMapping(normalized), nodes=nodes, edges=edges, execution_order=order,
            dsl_compiled_rule_set_sha256=dsl.compiled_rule_set_sha256))

    @staticmethod
    def _cache_key(*, manifest, analysis):
        from systems.Parasara.engine.versioning import _component_to_data
        return (manifest.manifest_fingerprint_sha256, analysis.source_raw_sha256, analysis.declarations_sha256,
            analysis.dsl_compiled_rule_set_sha256, GRAPH_COMPILER_CONTENT_SHA256, GRAPH_CONTRACT_SHA256,
            digest(_component_to_data(manifest.dsl)), digest(_component_to_data(manifest.predicate_library)),
            digest(_component_to_data(manifest.condition_evaluator)), digest(manifest.ordered_source_artifacts))

    def compile_authorized(self, *, compiled_rule_set):
        from systems.Parasara.engine.versioning import VersioningError, _graph_error
        from systems.Parasara.engine.rules.dsl import RuleDslCompiler, AnalysisSucceeded, MAX_SOURCE_BYTES
        authority = self._resolved_versions
        try:
            authority.authorize_compiled_rule_set(compiled_rule_set)
            payload = authority.load_authorized_graph_source()
            artifact = authority.manifest.ordered_source_artifacts[0]
            # Reuse DSL analysis solely to construct graph keys, never evaluate or re-lower in graph code.
            dsl_payload = authority.load_authorized_dsl_source(source_id=artifact["path"],
                compiler_identity=(compiled_rule_set.compiler_identity, compiled_rule_set.compiler_version,
                    authority.manifest.dsl.compatibility_contract, compiled_rule_set.compiler_content_sha256),
                compiler_metadata=authority.manifest.dsl.metadata, max_bytes=MAX_SOURCE_BYTES)
            dsl = RuleDslCompiler.analyze_source(source_id=artifact["path"], payload=dsl_payload)
            if not isinstance(dsl, AnalysisSucceeded):
                raise _graph_error(diagnostic("P08E302_AUTHORITY_MISMATCH"))
            authority.authorize_dsl_analysis(dsl.analyzed_rule_set)
            result = self.analyze_source(source_id=authority.manifest.dependency_graph.artifact_path, payload=payload,
                analyzed_rule_set=dsl.analyzed_rule_set, dsl_source_artifact_id=artifact["artifact_id"])
            if isinstance(result, GraphCompilationFailed):
                self._cache.clear()
                return result
            analysis = result.analysis
            authority.authorize_graph_analysis(analysis)
            key = self._cache_key(manifest=authority.manifest, analysis=analysis)
            plan = self._cache.get(key)
            if plan is None:
                plan = authority._issued_graph_plan
                if plan is None:
                    plan = _new_plan(analysis, compiled_rule_set, authority)
                    authority._issue_execution_plan(plan)
            if plan.compiled_rule_set is not compiled_rule_set:
                raise _graph_error(diagnostic("P08E302_AUTHORITY_MISMATCH"))
            authority.authorize_execution_plan(plan)
            if self._cache_capacity:
                self._cache.clear()
                self._cache[key] = plan
            return GraphCompilationSucceeded(plan)
        except VersioningError as exc:
            self._cache.clear()
            from systems.Parasara.engine.rules.graph.models import versioning_diagnostic
            return GraphCompilationFailed((versioning_diagnostic(exc),))
