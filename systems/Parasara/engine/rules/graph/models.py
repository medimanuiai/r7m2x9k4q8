"""Immutable graph descriptions, sealed plans and RuleEngine audit envelopes."""
from __future__ import annotations

from dataclasses import dataclass, field, fields, InitVar
from enum import Enum
import re
from typing import Any

from systems.Parasara.engine.rules.canonical import FrozenMapping, canonical_json_bytes
from systems.Parasara.engine.rules.models import PredicateStatus
from systems.Parasara.engine.rules.graph.runtime_contract import CONTRACTS, KINDS, LIMITS, MESSAGES, STAGES, GRAPH_CONTRACT_DATA, GRAPH_CONTRACT_SHA256, digest

_GRAPH_TOKEN = object()
_RECORD_TOKEN = object()


def _projection(value):
    return FrozenMapping({f.name: getattr(value, f.name) for f in fields(value) if not f.name.startswith("_")})


class DependencyKind(str, Enum):
    REQUIRES_MATCHES = KINDS[0]
    REQUIRES_ABSENCE = KINDS[1]
    OPTIONAL_SUPPORTS = KINDS[2]


@dataclass(frozen=True, slots=True, kw_only=True)
class GraphDiagnostic:
    code: str
    stage: str
    source_id: str
    field_path: str = "$"
    node_source_order: int | None = None
    prerequisite_source_order: int | None = None
    details: Any = field(default_factory=dict)
    message: str = field(init=False)

    def __post_init__(self):
        if self.code not in MESSAGES or self.stage not in STAGES:
            raise ValueError("unsupported graph diagnostic")
        if (not isinstance(self.source_id, str) or len(self.source_id) > LIMITS["source_id_code_points"]
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", self.source_id)
            or any(p in ("", ".", "..") for p in self.source_id.split("/"))
            or not isinstance(self.field_path, str) or not re.fullmatch(r"\$(?:\.[A-Za-z_][A-Za-z0-9_]*|\[[0-9]+\])*", self.field_path)):
            raise ValueError("unsafe diagnostic location")
        for position in (self.node_source_order, self.prerequisite_source_order):
            if position is not None and (type(position) is not int or not 0 <= position < LIMITS["nodes"]):
                raise ValueError("invalid diagnostic position")
        object.__setattr__(self, "message", MESSAGES[self.code])
        object.__setattr__(self, "details", FrozenMapping(self.details))
        allowed = {"resource", "limit", "observed", "expected", "rule_id", "revision", "members", "witness", "preparation_issues"}
        if not set(self.details) <= allowed:
            raise ValueError("unsupported diagnostic details")
        for key, value in self.details.items():
            if key in ("members", "witness"):
                if (not isinstance(value, tuple) or len(value) > LIMITS["cycle_witness_nodes"]
                    or any(type(i) is not int or not 0 <= i < LIMITS["nodes"] for i in value)):
                    raise ValueError("invalid cycle diagnostic")
            elif key == "preparation_issues":
                if (not isinstance(value, tuple) or len(value) >= LIMITS["diagnostics"]
                    or any(not isinstance(v, str) or not re.fullmatch(r"[a-z0-9_]+", v) for v in value)):
                    raise ValueError("invalid preparation diagnostic")
            elif type(value) is int:
                if value < 0:
                    raise ValueError("negative diagnostic count")
            elif (not isinstance(value, str) or len(value) > LIMITS["string_code_points"]
                  or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.@/-]*", value)):
                raise ValueError("unsafe diagnostic detail")

    def to_logical_data(self):
        return _projection(self)


def diagnostic(code, *, stage="authorization", source_id="graph", **kwargs):
    return GraphDiagnostic(code=code, stage=stage, source_id=source_id, **kwargs)


def versioning_diagnostic(error, *, stage="authorization"):
    data = error.details.get("graph_diagnostic")
    if data is not None:
        return GraphDiagnostic(**{k: v for k, v in data.items() if k != "message"})
    return diagnostic(error.details.get("graph_code", "P08E302_AUTHORITY_MISMATCH"), stage=stage)


class DiagnosticCollector:
    def __init__(self, source_id):
        self.source_id, self.items, self.suppressed = source_id, [], False

    def add(self, code, **kwargs):
        if len(self.items) >= LIMITS["diagnostics"] - 1:
            self.suppressed = True
        else:
            self.items.append(diagnostic(code, source_id=self.source_id, **kwargs))

    def finish(self):
        def key(d):
            return (STAGES.index(d.stage), LIMITS["nodes"] if d.node_source_order is None else d.node_source_order,
                    LIMITS["nodes"] if d.prerequisite_source_order is None else d.prerequisite_source_order,
                    d.code, d.field_path, canonical_json_bytes(d.details))
        result = tuple(sorted(self.items, key=key))
        if self.suppressed:
            result += (diagnostic("P08E999_DIAGNOSTIC_LIMIT", stage="schema", source_id=self.source_id),)
        return result


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleNodeKey:
    system: str
    rule_set_family: str
    rule_set_version: str
    rule_id: str
    revision: str
    dsl_compiled_semantic_sha256: str
    source_artifact_id: str
    source_identity: str
    source_artifact_semantic_sha256: str
    source_order: int

    def __post_init__(self):
        if type(self.source_order) is not int or not 0 <= self.source_order < LIMITS["nodes"]:
            raise ValueError("invalid source position")
        grammars = GRAPH_CONTRACT_DATA["identity_grammars"]
        for name in ("system", "rule_set_family", "rule_set_version", "rule_id", "revision"):
            value = getattr(self, name)
            grammar = grammars[name if name in ("rule_id", "revision") else "identity"]
            if not isinstance(value, str) or len(value) > LIMITS["identifier_code_points"] or not re.fullmatch(grammar, value):
                raise ValueError("invalid node identity")
        for value in (self.source_artifact_id, self.source_identity):
            if not isinstance(value, str) or len(value) > LIMITS["source_id_code_points"] or not re.fullmatch(grammars["identity"], value):
                raise ValueError("invalid node source identity")
        for name in ("dsl_compiled_semantic_sha256", "source_artifact_semantic_sha256"):
            if not isinstance(getattr(self, name), str) or not re.fullmatch(r"[0-9a-f]{64}", getattr(self, name)):
                raise ValueError("invalid node digest")

    def to_logical_data(self):
        return _projection(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class DependencyDeclaration:
    prerequisite: int
    dependent: int
    kind: DependencyKind

    def __post_init__(self):
        if not isinstance(self.kind, DependencyKind) or any(type(i) is not int or not 0 <= i < LIMITS["nodes"] for i in (self.prerequisite, self.dependent)):
            raise ValueError("invalid dependency")

    def to_logical_data(self):
        return _projection(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class GraphAnalysis:
    source_id: str
    source_raw_sha256: str
    document: FrozenMapping
    nodes: tuple[RuleNodeKey, ...]
    edges: tuple[DependencyDeclaration, ...]
    execution_order: tuple[int, ...]
    dsl_compiled_rule_set_sha256: str

    def __post_init__(self):
        if not isinstance(self.document, FrozenMapping):
            object.__setattr__(self, "document", FrozenMapping(self.document))
        if not isinstance(self.source_id, str):
            raise TypeError("graph source identity must be a string")
        for value in (self.source_raw_sha256, self.dsl_compiled_rule_set_sha256):
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError("invalid analysis digest")
        for name, cls in (("nodes", RuleNodeKey), ("edges", DependencyDeclaration), ("execution_order", int)):
            if not isinstance(getattr(self, name), tuple) or any(type(v) is not cls for v in getattr(self, name)):
                raise TypeError("graph collections must be immutable typed tuples")

    @property
    def declarations_sha256(self):
        return digest(dict(contract=CONTRACTS["declarations"], document=self.document))

    @property
    def nodes_projection(self):
        return FrozenMapping(dict(contract=CONTRACTS["nodes"], nodes=tuple(n.to_logical_data() for n in self.nodes)))

    @property
    def edges_projection(self):
        return FrozenMapping(dict(contract=CONTRACTS["edges"], edges=tuple(e.to_logical_data() for e in self.edges)))

    @property
    def nodes_sha256(self):
        return digest(self.nodes_projection)

    @property
    def edges_sha256(self):
        return digest(self.edges_projection)

    @property
    def graph_projection(self):
        return FrozenMapping(dict(contract=CONTRACTS["graph"], declarations_sha256=self.declarations_sha256,
            nodes_sha256=self.nodes_sha256, edges_sha256=self.edges_sha256))

    @property
    def graph_sha256(self):
        return digest(self.graph_projection)

    @property
    def plan_projection(self):
        from systems.Parasara.engine.rules.graph.compiler import GRAPH_COMPILER_CONTENT_SHA256
        return FrozenMapping(dict(contract=CONTRACTS["plan"], graph_sha256=self.graph_sha256,
            dsl_compiled_rule_set_sha256=self.dsl_compiled_rule_set_sha256,
            graph_compiler_content_sha256=GRAPH_COMPILER_CONTENT_SHA256,
            graph_contract_sha256=GRAPH_CONTRACT_SHA256, execution_order=self.execution_order))

    @property
    def plan_sha256(self):
        return digest(self.plan_projection)

    def bound_rule_sha256(self, position):
        return digest(dict(contract=CONTRACTS["bound_rule"], node=self.nodes[position].to_logical_data(),
            dependencies=tuple(dict(prerequisite=self.nodes[e.prerequisite].to_logical_data(), kind=e.kind)
                for e in self.edges if e.dependent == position)))

    def to_logical_data(self):
        return FrozenMapping(dict(declarations=self.document, nodes=self.nodes_projection,
            edges=self.edges_projection, graph=self.graph_projection, plan=self.plan_projection))


class _Sealed:
    __slots__ = ()

    def __copy__(self):
        raise TypeError("authoritative graph objects cannot be copied")

    def __deepcopy__(self, memo):
        raise TypeError("authoritative graph objects cannot be copied")

    def __reduce_ex__(self, protocol):
        raise TypeError("authoritative graph objects cannot be pickled")


@dataclass(frozen=True, slots=True, kw_only=True, eq=False)
class ValidatedRuleGraph(_Sealed):
    analysis: GraphAnalysis
    _factory_token: InitVar[Any] = None

    def __post_init__(self, _factory_token):
        if _factory_token is not _GRAPH_TOKEN or not isinstance(self.analysis, GraphAnalysis):
            raise ValueError("validated graphs require RuleGraphCompiler")

    def to_logical_data(self):
        return self.analysis.to_logical_data()


@dataclass(frozen=True, slots=True, kw_only=True, eq=False)
class RuleExecutionPlan(_Sealed):
    graph: ValidatedRuleGraph
    compiled_rule_set: Any
    resolved_versions: Any = field(repr=False)
    _factory_token: InitVar[Any] = None

    def __post_init__(self, _factory_token):
        if _factory_token is not _GRAPH_TOKEN or not isinstance(self.graph, ValidatedRuleGraph):
            raise ValueError("plans require RuleGraphCompiler")

    @property
    def execution_order(self):
        return self.graph.analysis.execution_order

    @property
    def plan_sha256(self):
        return self.graph.analysis.plan_sha256

    def to_logical_data(self):
        return self.graph.analysis.plan_projection


def _new_plan(analysis, compiled_rule_set, resolved_versions):
    return RuleExecutionPlan(graph=ValidatedRuleGraph(analysis=analysis, _factory_token=_GRAPH_TOKEN),
        compiled_rule_set=compiled_rule_set, resolved_versions=resolved_versions, _factory_token=_GRAPH_TOKEN)


@dataclass(frozen=True, slots=True, kw_only=True)
class DependencyDecision:
    prerequisite: int
    dependent: int
    kind: DependencyKind
    prerequisite_trace_id: str
    completion_kind: str
    root_outcome: str | None
    rule_match_status: str
    decision: str

    def __post_init__(self):
        DependencyDeclaration(prerequisite=self.prerequisite, dependent=self.dependent, kind=self.kind)
        if self.completion_kind not in ("condition_evaluated", "dependency_skip"):
            raise ValueError("invalid completion kind")
        outcome = self.root_outcome if self.completion_kind == "condition_evaluated" else "dependency_skip"
        policy = GRAPH_CONTRACT_DATA["outcome_policy"]
        if (outcome not in policy or outcome not in (*tuple(s.value for s in PredicateStatus), "dependency_skip")
            or (self.completion_kind == "dependency_skip" and self.root_outcome is not None)):
            raise ValueError("invalid dependency outcome")
        row = policy[outcome]
        if self.rule_match_status != row[0] or self.decision != row[KINDS.index(self.kind) + 1]:
            raise ValueError("inconsistent dependency decision")
        if not isinstance(self.prerequisite_trace_id, str) or not self.prerequisite_trace_id:
            raise ValueError("missing prerequisite rule trace")

    def to_logical_data(self):
        return _projection(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleExecutionTrace:
    trace_id: str
    plan_sha256: str
    source_order: int
    execution_ordinal: int
    decisions: tuple[DependencyDecision, ...]
    gate: str
    condition_evaluated: bool
    completion_kind: str
    root_outcome: str | None
    skip_reason: str | None

    def __post_init__(self):
        if not isinstance(self.decisions, tuple) or any(not isinstance(d, DependencyDecision) for d in self.decisions):
            raise TypeError("trace decisions must be immutable")
        if (len(self.decisions) > LIMITS["dependencies_per_node"]
            or any(type(p) is not int or not 0 <= p < LIMITS["nodes"] for p in (self.source_order, self.execution_ordinal))
            or not re.fullmatch(r"[0-9a-f]{64}", self.plan_sha256)
            or not re.fullmatch(r"graph\.[0-9a-f]{64}", self.trace_id)):
            raise ValueError("invalid trace bounds or identity")
        if self.gate not in ("passed", "unsatisfied", "unavailable") or type(self.condition_evaluated) is not bool:
            raise ValueError("invalid gate")
        if self.gate == "passed":
            if (not self.condition_evaluated or self.completion_kind != "condition_evaluated"
                or self.root_outcome not in tuple(s.value for s in PredicateStatus) or self.skip_reason is not None):
                raise ValueError("invalid condition completion")
        elif (self.condition_evaluated or self.completion_kind != "dependency_skip"
              or self.root_outcome is not None or self.skip_reason != "dependency_" + self.gate):
            raise ValueError("invalid dependency skip")
        if any(d.dependent != self.source_order for d in self.decisions):
            raise ValueError("decision belongs to another node")

    def to_logical_data(self):
        return FrozenMapping({f.name: (tuple(d.to_logical_data() for d in self.decisions) if f.name == "decisions" else getattr(self, f.name)) for f in fields(self)})


@dataclass(frozen=True, slots=True, kw_only=True, eq=False)
class GraphEvaluationRecord(_Sealed):
    resolved_versions: Any = field(repr=False)
    plan: RuleExecutionPlan
    snapshot_sha256: str
    context_sha256: str
    matches: tuple
    traces: tuple[RuleExecutionTrace, ...]
    _factory_token: InitVar[Any] = None

    def __post_init__(self, _factory_token):
        from systems.Parasara.engine.rules.rule_match import RuleMatch
        if _factory_token is not _RECORD_TOKEN:
            raise ValueError("graph evaluation records require RuleEngine")
        self.resolved_versions.authorize_execution_plan(self.plan)
        count = len(self.plan.graph.analysis.nodes)
        if (not isinstance(self.matches, tuple) or not isinstance(self.traces, tuple)
            or len(self.matches) != count or len(self.traces) != count
            or any(not isinstance(m, RuleMatch) for m in self.matches)
            or any(not isinstance(t, RuleExecutionTrace) for t in self.traces)):
            raise ValueError("incomplete graph ledger")
        for i, (n, m, t) in enumerate(zip(self.plan.graph.analysis.nodes, self.matches, self.traces)):
            if (n.rule_id, n.revision, i) != (m.rule_id, m.rule_version, t.source_order):
                raise ValueError("inconsistent graph ledger membership")
        from systems.Parasara.engine.rules.graph.runtime_contract import dependency_trace_id
        for sha in (self.snapshot_sha256, self.context_sha256):
            if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
                raise ValueError("invalid evaluation identity")
        plan_sha = self.plan.plan_sha256
        for i, trace in enumerate(self.traces):
            incoming = tuple(e for e in self.plan.graph.analysis.edges if e.dependent == i)
            if (trace.plan_sha256 != plan_sha or trace.execution_ordinal != self.plan.execution_order.index(i)
                or trace.trace_id != dependency_trace_id(plan_sha, i, self.snapshot_sha256, self.context_sha256)
                or tuple((d.prerequisite, d.dependent, d.kind) for d in trace.decisions)
                    != tuple((e.prerequisite, e.dependent, e.kind) for e in incoming)):
                raise ValueError("inconsistent graph trace")
            for decision in trace.decisions:
                prior = self.traces[decision.prerequisite]
                if (decision.prerequisite_trace_id != self.matches[decision.prerequisite].trace_id
                    or (decision.completion_kind, decision.root_outcome) != (prior.completion_kind, prior.root_outcome)
                    or prior.execution_ordinal >= trace.execution_ordinal):
                    raise ValueError("inconsistent prerequisite provenance")

    @property
    def ordered_matches(self):
        from systems.Parasara.engine.rules.rule_engine import RuleEngine
        return RuleEngine.order_matches(self.matches)

    def to_logical_data(self):
        from systems.Parasara.engine.rules.rule_match import rule_match_to_logical_data
        return FrozenMapping(dict(plan_sha256=self.plan.plan_sha256, snapshot_sha256=self.snapshot_sha256,
            context_sha256=self.context_sha256, matches=tuple(rule_match_to_logical_data(m) for m in self.matches),
            traces=tuple(t.to_logical_data() for t in self.traces)))


def _new_evaluation_record(**kwargs):
    return GraphEvaluationRecord(**kwargs, _factory_token=_RECORD_TOKEN)


@dataclass(frozen=True, slots=True)
class GraphAnalysisSucceeded:
    analysis: GraphAnalysis
    diagnostics: tuple = ()

    def __post_init__(self):
        if type(self.analysis) is not GraphAnalysis or self.diagnostics != () or type(self.diagnostics) is not tuple:
            raise ValueError("analysis success requires immutable analysis and no diagnostics")


@dataclass(frozen=True, slots=True)
class GraphCompilationSucceeded:
    plan: RuleExecutionPlan
    diagnostics: tuple = ()

    def __post_init__(self):
        if type(self.plan) is not RuleExecutionPlan or self.diagnostics != () or type(self.diagnostics) is not tuple:
            raise ValueError("compilation success requires an issued plan and no diagnostics")


@dataclass(frozen=True, slots=True)
class GraphCompilationFailed:
    diagnostics: tuple[GraphDiagnostic, ...]
    plan: None = None
    analysis: None = None

    def __post_init__(self):
        if (self.plan is not None or self.analysis is not None or not isinstance(self.diagnostics, tuple)
            or not self.diagnostics or len(self.diagnostics) > LIMITS["diagnostics"]
            or any(not isinstance(d, GraphDiagnostic) for d in self.diagnostics)):
            raise ValueError("failure requires immutable diagnostics")


@dataclass(frozen=True, slots=True)
class GraphEvaluationProduced:
    record: GraphEvaluationRecord

    def __post_init__(self):
        if type(self.record) is not GraphEvaluationRecord:
            raise ValueError("evaluation success requires a sealed record")


@dataclass(frozen=True, slots=True)
class GraphEvaluationFailed:
    diagnostics: tuple[GraphDiagnostic, ...]
    record: None = None

    def __post_init__(self):
        if (self.record is not None or not isinstance(self.diagnostics, tuple) or not self.diagnostics
            or len(self.diagnostics) > LIMITS["diagnostics"]
            or any(not isinstance(d, GraphDiagnostic) for d in self.diagnostics)):
            raise ValueError("failure requires bounded immutable diagnostics and no record")
