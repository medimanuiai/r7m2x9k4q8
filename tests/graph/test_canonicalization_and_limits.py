"""Independent projection oracles and locked resource acceptance boundaries."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from systems.Parasara.engine.rules.canonical import canonical_json_bytes, canonical_json_data
from systems.Parasara.engine.rules.graph.compiler import (
    GRAPH_COMPILER_CONTENT_SHA256, GRAPH_COMPILER_IMPLEMENTATION_MODULE_IDS,
    compiler_component_fingerprint_sha256,
)
from systems.Parasara.engine.rules.graph.models import DiagnosticCollector
from systems.Parasara.engine.rules.graph.parser import parse_graph_source, ParsedGraph, valid_source_id
from systems.Parasara.engine.rules.graph.runtime_contract import GRAPH_CONTRACT_DATA, GRAPH_CONTRACT_SHA256, LIMITS
from tests.graph.conftest import analyze, codes, document, dsl_payload

ROOT = Path(__file__).resolve().parents[2]


def sha(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def modules():
    return {name: (ROOT / "systems/Parasara/engine/rules" / name).read_bytes()
            for name in GRAPH_COMPILER_IMPLEMENTATION_MODULE_IDS}


def test_exact_canonical_hash_dependency_graph():
    data = document(edges=[(2, 0, "requires_matches"), (1, 3, "optional_supports")])
    a = analyze(data).analysis
    d = sha({"contract": "rule-dependency-declarations@1.0.0", "document": data})
    n = sha({"contract": "rule-dependency-nodes@1.0.0", "nodes": [node.to_logical_data() for node in a.nodes]})
    e = sha({"contract": "rule-dependency-edges@1.0.0", "edges": [
        {"prerequisite": 1, "dependent": 3, "kind": "optional_supports"},
        {"prerequisite": 2, "dependent": 0, "kind": "requires_matches"}]})
    g = sha({"contract": "rule-dependency-graph@1.0.0", "declarations_sha256": d, "nodes_sha256": n, "edges_sha256": e})
    p = sha({"contract": "rule-execution-plan@1.0.0", "graph_sha256": g,
        "dsl_compiled_rule_set_sha256": a.dsl_compiled_rule_set_sha256,
        "graph_compiler_content_sha256": GRAPH_COMPILER_CONTENT_SHA256,
        "graph_contract_sha256": GRAPH_CONTRACT_SHA256, "execution_order": [1, 2, 0, 3]})
    assert (a.declarations_sha256, a.nodes_sha256, a.edges_sha256, a.graph_sha256, a.plan_sha256) == (d, n, e, g, p)
    assert a.bound_rule_sha256(0) == sha({"contract": "graph-bound-rule@1.0.0", "node": a.nodes[0].to_logical_data(),
        "dependencies": [{"prerequisite": a.nodes[2].to_logical_data(), "kind": "requires_matches"}]})
    assert "manifest_fingerprint" not in canonical_json_bytes(a.to_logical_data()).decode()


def test_permutation_format_invariance_and_semantic_sensitivity():
    data = document(edges=[(0, 3, "requires_matches"), (1, 3, "requires_matches")])
    a = analyze(data).analysis
    data["rules"].reverse()
    data["rules"][0]["requires_matches"].reverse()
    b = analyze(payload=json.dumps(data, indent=4, sort_keys=True).replace("synthetic", "\\u0073ynthetic").encode()).analysis
    assert a.source_raw_sha256 != b.source_raw_sha256
    assert a.to_logical_data() == b.to_logical_data()
    c = analyze(data, dsl=dsl_payload().replace(b"house: 1", b"house: 9", 1)).analysis
    assert c.declarations_sha256 == a.declarations_sha256 and c.nodes_sha256 != a.nodes_sha256
    assert c.plan_sha256 != a.plan_sha256
    data["rules"][0]["requires_absence"] = data["rules"][0].pop("requires_matches")
    data["rules"][0]["requires_matches"] = []
    assert analyze(data).analysis.declarations_sha256 != a.declarations_sha256
    changed_node = replace(a.nodes[0], source_order=1)
    assert replace(a, nodes=(changed_node, *a.nodes[1:])).nodes_sha256 != a.nodes_sha256


def test_published_component_fingerprint_and_newline_equivalence():
    sources = modules()
    assert compiler_component_fingerprint_sha256(sources) == GRAPH_COMPILER_CONTENT_SHA256
    crlf = {k: v.decode().replace("\r\n", "\n").replace("\n", "\r\n") for k, v in sources.items()}
    assert compiler_component_fingerprint_sha256(crlf) == GRAPH_COMPILER_CONTENT_SHA256
    with pytest.raises(ValueError): compiler_component_fingerprint_sha256({})
    for name in sources:
        assert compiler_component_fingerprint_sha256(dict(sources, **{name: sources[name] + b"\n# semantic module coverage\n"})) != GRAPH_COMPILER_CONTENT_SHA256
    for name in LIMITS:
        contract = canonical_json_data(GRAPH_CONTRACT_DATA)
        contract["resource_limits"][name] += 1
        assert compiler_component_fingerprint_sha256(sources, contract_data=contract) != GRAPH_COMPILER_CONTENT_SHA256


@pytest.mark.parametrize("resource", ["source_bytes", "json_depth", "mapping_entries", "array_elements", "string_code_points"])
def test_parser_limit_and_plus_one(resource):
    def payload(size):
        if resource == "source_bytes":
            base = json.dumps(document()).encode()
            return base + b" " * (size - len(base))
        if resource == "json_depth": return ("[" * size + "\"x\"" + "]" * size).encode()
        if resource == "mapping_entries": return json.dumps({str(i): "x" for i in range(size)}).encode()
        if resource == "array_elements": return json.dumps(["x"] * size).encode()
        return json.dumps("x" * size).encode()
    at = parse_graph_source(source_id="synthetic/a.json", payload=payload(LIMITS[resource]))
    above = parse_graph_source(source_id="synthetic/a.json", payload=payload(LIMITS[resource] + 1))
    assert isinstance(at, ParsedGraph) or "P08E401_LIMIT_VIOLATION" not in codes(at)
    assert codes(above) == ("P08E401_LIMIT_VIOLATION",)
    assert above.diagnostics[0].details == {"resource": resource, "limit": LIMITS[resource], "observed": LIMITS[resource] + 1}


def test_source_identifier_boundaries():
    assert valid_source_id("a" * 251 + ".json")
    assert not valid_source_id("a" * 252 + ".json")
    data = document()
    data["system"] = "a" * 128
    assert isinstance(parse_graph_source(source_id="a.json", payload=json.dumps(data)), ParsedGraph)
    data["system"] += "a"
    assert codes(analyze(data))


@pytest.mark.parametrize("count", [64, 65])
def test_depth_acceptance_boundary(count):
    result = analyze(document(count, [(i, i+1, "optional_supports") for i in range(count-1)]), dsl=dsl_payload(count))
    if count == 64: assert result.analysis.execution_order == tuple(range(count))
    else:
        assert codes(result) == ("P08E401_LIMIT_VIOLATION",)
        assert result.diagnostics[0].details["resource"] == "graph_depth"


@pytest.mark.parametrize("incoming", [32, 33])
def test_incoming_edge_boundary(incoming):
    result = analyze(document(34, [(i, 33, "optional_supports") for i in range(incoming)]), dsl=dsl_payload(34))
    assert (result.analysis is not None) == (incoming == 32)


@pytest.mark.parametrize("edge_count", [4096, 4097])
def test_total_edges_boundary(edge_count):
    edges = [(i, j, "optional_supports") for j in range(32, 161) for i in range(32)][:edge_count]
    result = analyze(document(161, edges), dsl=dsl_payload(161))
    if edge_count == 4096: assert len(result.analysis.edges) == 4096
    else: assert result.diagnostics[0].details["resource"] == "edges"


def test_node_minimum_maximum_and_plus_one():
    assert analyze(document(256), dsl=dsl_payload(256)).analysis.execution_order == tuple(range(256))
    assert codes(analyze(document(257))) == ("P08E401_LIMIT_VIOLATION",)
    assert "P08E107_MEMBERSHIP_MISMATCH" in codes(analyze(document(0)))


@pytest.mark.parametrize("count", [255, 256, 257])
def test_diagnostics_cap(count):
    collector = DiagnosticCollector("synthetic/a.json")
    for _ in range(count): collector.add("P08E003_SCHEMA_MISMATCH", stage="schema")
    diagnostics = collector.finish()
    assert len(diagnostics) == min(count, 256)
    assert (diagnostics[-1].code == "P08E999_DIAGNOSTIC_LIMIT") == (count > 255)


def test_maximum_cycle_witness_is_bounded():
    result = analyze(document(256, [(i, (i+1) % 256, "optional_supports") for i in range(256)]), dsl=dsl_payload(256))
    assert codes(result) == ("P08E201_CYCLE",)
    assert result.diagnostics[0].details["witness"] == tuple(range(256)) + (0,)


@pytest.mark.parametrize("capacity", [-1, 2, True])
def test_cache_capacity_outside_zero_one_rejected(graph_pack, capacity):
    from systems.Parasara.engine.rules.graph import RuleGraphCompiler
    _, authority, _, _, _ = graph_pack()
    with pytest.raises(ValueError): RuleGraphCompiler(resolved_versions=authority, cache_capacity=capacity)
