"""Real resolver/compiler/evaluator consumers of the additive aspect contract."""
from copy import copy, deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from systems.Parasara.engine.rules import aspect_contract_v2 as v2
from systems.Parasara.engine.rules.canonical import canonical_json_bytes, freeze_canonical
from systems.Parasara.engine.rules.evaluator_v2 import PredicateEvaluatorV2, ConditionEvaluatorV2
from systems.Parasara.engine.rules.dsl.compiler_v2 import RuleDslCompilerV2
from systems.Parasara.engine.rules.dsl import AnalysisSucceeded, CompilationSucceeded, CompilationFailed, RuleDslCompiler
from systems.Parasara.engine.rules.models import PredicateStatus as Status
from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext, state_canonical_bytes, PreparedCapability
from systems.Parasara.engine.rules.snapshot_adapter import prepare_predicate_snapshot, prepare_predicate_snapshot_v2
from systems.Parasara.engine.rules.rule_engine import RuleEngine
from systems.Parasara.engine.versioning import (
    RuleVersionResolver, compatibility_v1_config, SelectionPurpose, VersioningError,
    VersioningErrorCode, manifest_to_data, manifest_from_data, _verify_manifest_artifacts,
)
from tests.fwp01.test_input_contract import strict_payload, strict_snapshot

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).with_name("fixtures")
SOURCE = "tests/fwp01/fixtures/aspect-contract-v2.rules.yaml"


def resolve_v2(*, purpose=SelectionPurpose.NEW_EVALUATION):
    config = replace(compatibility_v1_config(), system="synthetic", rule_set_family="fwp01_aspect_v2",
                     rule_set_version="synthetic-v2", purpose=purpose)
    return RuleVersionResolver.for_test(catalog_path=FIXTURES / "aspect-contract-v2-catalog.json",
                                       repository_root=ROOT).resolve(config)


def v2_snapshot():
    return strict_snapshot(strict_payload(0, [10, 95, 1, 61, 120, 180, 240, 300, 150]))


@pytest.fixture
def run():
    authority = resolve_v2()
    snapshot = v2_snapshot()
    result = prepare_predicate_snapshot_v2(snapshot, resolved_versions=authority)
    assert result.succeeded and result.state.graph.readiness is v2.Readiness.READY
    return authority, snapshot, result.state, PredicateEvaluatorV2(resolved_versions=authority), PredicateEvaluationContext()


@pytest.mark.parametrize("filters,status,code", [
    ({"from_planet": "Mars", "to_planet": "Moon"}, Status.MATCHED, None),
    ({"from_planet": "Sun", "to_planet": "Sun"}, Status.UNMATCHED, None),
    ({"from_planet": "Rahu"}, Status.MISSING_CAPABILITY, "aspect_source_unsupported"),
    ({"from_planet": "Ketu", "from_house": 12}, Status.MISSING_CAPABILITY, "aspect_source_unsupported"),
    ({"to_planet": "Moon"}, Status.MATCHED, None),
    ({"to_house": 12}, Status.MISSING_CAPABILITY, "aspect_source_coverage_incomplete"),
    ({"from_house": 2}, Status.UNMATCHED, None),
    ({"from_house": 1, "to_house": 12}, Status.UNMATCHED, None),
    ({"from_planet": "Mars", "from_house": 1, "to_planet": "Moon", "to_house": 4}, Status.MATCHED, None),
    ({"from_planet": "Mars", "from_house": 2}, Status.UNMATCHED, None),
    ({"from_planet": "Mars", "to_planet": "Moon", "to_house": 5}, Status.UNMATCHED, None),
    ({"to_planet": "Mars", "to_house": 12}, Status.MISSING_CAPABILITY, "aspect_source_coverage_incomplete"),
    ({"from_house": 11, "to_planet": "Moon"}, Status.MISSING_CAPABILITY, "aspect_source_coverage_incomplete"),
    ({"from_planet": "Mars", "to_planet": "Mercury"}, Status.UNMATCHED, None),
    ({"from_house": True}, Status.INVALID_PARAMETERS, "invalid_parameters"),
    ({"to_house": 13}, Status.INVALID_PARAMETERS, "invalid_parameters"),
    ({"from_planet": "Pluto"}, Status.INVALID_PARAMETERS, "invalid_parameters"),
    ({"unknown": "private"}, Status.INVALID_PARAMETERS, "invalid_parameters"),
])
def test_outcomes_and_diagnostics(run, filters, status, code):
    authority, snapshot, state, evaluator, context = run
    result = evaluator.evaluate("ASPECT_EXISTS", filters, state, context)
    assert result.status is status and result.matched is (status is Status.MATCHED)
    assert tuple(e.code for e in result.errors) == (() if code is None else (code,))
    if code is not None:
        assert result.errors[0].recoverable
    if status in (Status.MATCHED, Status.UNMATCHED):
        assert result.trace_steps and result.evidence["coverage_complete"] == (not result.evidence["unavailable_sources"])


def test_node_target_and_sign_only_target_house_semantics(run):
    _, _, state, evaluator, context = run
    # Mars eighth from Aries reaches Scorpio; use a known node target from stored facts.
    edge = next(e for e in state.graph.content["edges"] if e["target"] in ("Rahu", "Ketu"))
    assert evaluator.evaluate("ASPECT", {"from_planet": edge["source"], "to_planet": edge["target"]}, state, context).matched
    edge = next(e for e in state.graph.content["edges"] if e["target"] is None and not e["trace"]["matched_planets"])
    content = {**state.graph.content, "edges": (edge,)}
    narrowed = replace(state, graph=replace(state.graph, content=content))
    assert evaluator.evaluate("ASPECT", {"from_planet": edge["source"]}, narrowed, context).matched
    result = evaluator.evaluate("ASPECT", {"from_planet": edge["source"], "to_house": edge["trace"]["target_house"]}, narrowed, context)
    assert result.status is Status.UNMATCHED


def without_placements(state):
    old = state._legacy.capabilities[v2.PLACEMENT]
    missing = replace(old, readiness=v2.Readiness.MISSING, content=None, observed_version=None,
                      source_kind=None, content_empty=False)
    return replace(state, _legacy=replace(state._legacy, capabilities={**state._legacy.capabilities, v2.PLACEMENT: missing}))


@pytest.mark.parametrize("filters,code", [
    ({"from_planet": "Mars", "from_house": 1}, "aspect_source_placement_unavailable"),
    ({"from_house": 1}, "aspect_source_placement_unavailable"),
    ({"from_planet": "Mars", "to_planet": "Moon", "to_house": 4}, "aspect_target_placement_unavailable"),
    ({"to_house": 4}, "aspect_target_placement_unavailable"),
    ({"from_planet": "Rahu", "from_house": 1, "to_house": 4}, "aspect_source_unsupported"),
])
def test_missing_placement_never_reads_core_or_trace(run, filters, code):
    _, _, state, evaluator, context = run
    missing = without_placements(state)
    result = evaluator.evaluate("ASPECT", filters, missing, context)
    assert result.status is Status.MISSING_CAPABILITY and result.errors[0].code == code
    assert evaluator.evaluate("ASPECT", {"from_planet": "Mars", "to_planet": "Moon"}, missing, context).matched


@pytest.mark.parametrize("readiness", [v2.Readiness.MISSING, v2.Readiness.MALFORMED, v2.Readiness.VERSION_MISMATCH])
def test_unavailable_graph_and_invalid_parameters_first(run, readiness):
    _, _, state, evaluator, context = run
    graph = v2.AspectCapabilityV2(readiness=readiness,
        source_kind=None if readiness is v2.Readiness.MISSING else v2.SOURCE_KIND,
        observed_version="3.0.0" if readiness is v2.Readiness.VERSION_MISMATCH else None)
    unavailable = replace(state, graph=graph)
    assert evaluator.evaluate("ASPECT", {}, unavailable, context).status is Status.MISSING_CAPABILITY
    assert evaluator.evaluate("ASPECT", {"to_house": False}, unavailable, context).status is Status.INVALID_PARAMETERS
    assert evaluator.cache_size == 0


@pytest.mark.parametrize("change", ["missing", "duplicate", "unknown", "order", "node_ready", "classical_unsupported", "issues", "node_edge", "duplicate_edge", "source_sign", "target_house", "artifact"])
def test_deserialization_rejects_malformed_coverage(run, change):
    authority, _, state, _, _ = run
    data = json.loads(v2.state_canonical_bytes_v2(state))
    graph = data["capabilities"][v2.GRAPH]["content"]
    rows = graph["source_support"]
    if change == "missing": rows.pop()
    elif change == "duplicate": rows[-1] = deepcopy(rows[0])
    elif change == "unknown": rows[-1]["source"] = "Pluto"
    elif change == "order": rows.reverse()
    elif change == "node_ready": rows[-1]["readiness"] = "ready"
    elif change == "classical_unsupported": rows[0]["readiness"] = "unsupported"
    elif change == "issues": rows[0]["issues"] = ["private"]
    elif change == "node_edge": graph["edges"][0]["source"] = "Rahu"
    elif change == "duplicate_edge": graph["edges"].append(deepcopy(graph["edges"][0]))
    elif change == "source_sign": graph["edges"][0]["trace"]["source_sign"] = "Pisces"
    elif change == "target_house": graph["edges"][0]["trace"]["source_house"] = 12
    elif change == "artifact": graph["edges"][0]["trace"]["authority"]["bundle_sha256"] = "0" * 64
    result = v2.state_from_canonical_bytes_v2(canonical_json_bytes(data), resolved_versions=authority)
    assert result.succeeded and result.state.graph.readiness is v2.Readiness.MALFORMED
    assert result.state.graph.content is None


def test_immutable_serialization_cache_and_coverage_identity(run):
    authority, snapshot, state, evaluator, context = run
    before = v2.state_canonical_bytes_v2(state)
    with pytest.raises(TypeError): state.graph.content["source_support"][0]["readiness"] = "unsupported"
    with pytest.raises(TypeError): state.graph.content["edges"][0]["source"] = "Rahu"
    restored = v2.state_from_canonical_bytes_v2(before, resolved_versions=authority)
    assert restored.succeeded and v2.state_canonical_bytes_v2(restored.state) == before
    filters = dict(from_planet="Mars", to_planet="Moon")
    with patch.object(Path, "read_bytes", side_effect=AssertionError("evaluation must be pure")):
        first = evaluator.evaluate("ASPECT", filters, state, context)
        warm = evaluator.evaluate("ASPECT_EXISTS", filters, state, context)
    assert first == warm and not first.cache_hit and warm.cache_hit and evaluator.cache_size == 1
    empty = replace(state, graph=replace(state.graph, readiness=v2.Readiness.READY_EMPTY,
        content={**state.graph.content, "edges": ()}))
    assert v2.state_sha256_v2(empty) != v2.state_sha256_v2(state)
    assert evaluator.evaluate("ASPECT", filters, empty, context).status is Status.UNMATCHED
    assert evaluator.cache_size == 2
    result = evaluator.evaluate("ASPECT", {}, empty, context)
    assert result.status is Status.MISSING_CAPABILITY and evaluator.cache_size == 2
    evaluator.freeze_cache()
    assert evaluator.cache_frozen
    evaluator.clear_cache()
    assert evaluator.cache_size == 0


@pytest.mark.parametrize("operator,status", [("NOT", Status.MISSING_CAPABILITY), ("AND", Status.MISSING_CAPABILITY), ("OR", Status.MATCHED)])
def test_logical_propagation(run, operator, status):
    _, _, state, evaluator, context = run
    missing = dict(type="ASPECT", params=dict(from_planet="Rahu"))
    matched = dict(type="ASPECT_EXISTS", params=dict(from_planet="Mars", to_planet="Moon"))
    children = [missing] if operator == "NOT" else [missing, matched]
    result = ConditionEvaluatorV2(evaluator).evaluate(dict(type=operator, children=children), state, context)
    assert result.status is status


def test_compiled_rules_reach_existing_rule_engine_and_authority_is_exact(run):
    authority, snapshot, state, evaluator, context = run
    compiler = RuleDslCompilerV2(resolved_versions=authority)
    compilation = compiler.compile_authorized(source_id=SOURCE)
    assert isinstance(compilation, CompilationSucceeded)
    assert compiler.compile_authorized(source_id=SOURCE).compiled_rule_set is compilation.compiled_rule_set
    expected = ("matched", "missing_capability", "unmatched", "matched")
    matches = []
    engine = RuleEngine(resolved_versions=authority)
    for rule, status in zip(compilation.compiled_rule_set.rules, expected):
        match = engine.evaluate_compiled_rule(rule, condition_evaluator=ConditionEvaluatorV2(evaluator),
            state=state, context=context, evaluation_snapshot_digest=snapshot.logical_digest, evaluation_context={})
        assert match.status.value == status
        matches.append(match)
    assert matches[1].errors[0].code == "aspect_source_unsupported"
    for other in (copy(authority), resolve_v2()):
        with pytest.raises((ValueError, VersioningError)):
            engine.evaluate_compiled_rule(compilation.compiled_rule_set.rules[0],
                condition_evaluator=ConditionEvaluatorV2(PredicateEvaluatorV2(resolved_versions=other)),
                state=state, context=context, evaluation_snapshot_digest=snapshot.logical_digest, evaluation_context={})
        with pytest.raises(ValueError):
            evaluator.evaluate("ASPECT", {}, replace(state, _authority=other), context)
    assert isinstance(RuleDslCompiler(resolved_versions=authority).compile_authorized(source_id=SOURCE), CompilationFailed)


def test_compiler_binds_v2_and_conditional_placement_before_semantics(run):
    authority, _, _, _, _ = run
    analysis = RuleDslCompilerV2.analyze_source(source_id=SOURCE, payload=(ROOT / SOURCE).read_bytes())
    assert isinstance(analysis, AnalysisSucceeded)
    for index, rule in enumerate(analysis.analyzed_rule_set.rules):
        binding = rule.predicate_bindings[0]
        assert binding.predicate_version == "2.0.0"
        assert [(c.capability_id, c.capability_version) for c in binding.required_capabilities] == (
            [(v2.GRAPH, "2.0.0"), (v2.PLACEMENT, "1.0.0")] if index == 3 else [(v2.GRAPH, "2.0.0")])
    payload = (ROOT / SOURCE).read_bytes().replace(b"id: ASPECT_EXISTS", b"id: ASPECT")
    assert not isinstance(RuleDslCompilerV2.analyze_source(source_id=SOURCE, payload=payload), AnalysisSucceeded)
    assert not isinstance(RuleDslCompiler.analyze_source(source_id=SOURCE, payload=(ROOT / SOURCE).read_bytes()), AnalysisSucceeded)


def revised_manifest(authority, mutate):
    data = manifest_to_data(authority.manifest, include_fingerprint=False)
    mutate(data)
    data["manifest_fingerprint_sha256"] = hashlib.sha256(canonical_json_bytes(data)).hexdigest()
    return manifest_from_data(data)


@pytest.mark.parametrize("component", ["predicate_library", "condition_evaluator", "dsl"])
def test_mixed_profile_and_graph_rejected_before_analysis(run, component):
    authority, _, _, _, _ = run
    def mutate(data):
        selected = data[component] if component != "dsl" else data["future_components"]["dsl"]
        selected["version"] = "1.0.0"
    manifest = revised_manifest(authority, mutate)
    with patch.object(RuleDslCompilerV2, "analyze_source", side_effect=AssertionError("must reject before analysis")):
        with pytest.raises(VersioningError) as error: _verify_manifest_artifacts(manifest, ROOT)
    assert error.value.code is VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION


def test_v2_graph_and_exact_replay_and_v1_default_preserved(run):
    authority, _, state, _, _ = run
    from systems.Parasara.engine.rules.graph import GRAPH_CONTRACT_DATA, GRAPH_COMPILER_CONTENT_SHA256, GRAPH_CONTRACT_SHA256
    def mutate(data):
        data["future_components"]["dependency_graph"] = dict(identity=GRAPH_CONTRACT_DATA["identity"], version=GRAPH_CONTRACT_DATA["version"],
            compatibility_contract=GRAPH_CONTRACT_DATA["compatibility_contract"], content_sha256=GRAPH_COMPILER_CONTENT_SHA256,
            artifact_path="missing/graph.json", logical_sha256="0" * 64,
            metadata=dict(graph_schema_version="1.0.0", graph_contract_sha256=GRAPH_CONTRACT_SHA256,
                          declarations_sha256="0" * 64, plan_sha256="0" * 64))
    manifest = revised_manifest(authority, mutate)
    with patch.object(RuleDslCompilerV2, "analyze_source", side_effect=AssertionError("graph must reject first")):
        with pytest.raises(VersioningError) as error: _verify_manifest_artifacts(manifest, ROOT)
    assert error.value.code is VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION
    replay = resolve_v2(purpose=SelectionPurpose.REPLAY)
    assert replay.manifest_fingerprint_sha256 == authority.manifest_fingerprint_sha256
    original = RuleVersionResolver().resolve(compatibility_v1_config())
    assert original.manifest_fingerprint_sha256 == "3e942f97cec7c24079faabc3db358b84177b752a8eb35a7b0d909f84a92d1220"
    with pytest.raises(ValueError): PredicateEvaluatorV2(resolved_versions=original)
    snapshot = v2_snapshot()
    before = state_canonical_bytes(prepare_predicate_snapshot(snapshot).state)
    assert before == state_canonical_bytes(prepare_predicate_snapshot(snapshot).state)
    assert prepare_predicate_snapshot(snapshot).state.capabilities[v2.GRAPH].readiness is v2.Readiness.MISSING
    assert len(state.capabilities) == 7
    assert hashlib.sha256((ROOT / "systems/Parasara/engine/rules/prepared_state.py").read_bytes()).hexdigest() == "a2fca2dd17edd7092e8bee1cc8431891400d09f979a90f4f44d17b71c9466970"
    golden = (ROOT / "systems/Parasara/tests/snapshots/output_golden_chart_01.json").read_bytes()
    assert len(golden) == 4041 and hashlib.sha256(golden).hexdigest() == "da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af"


def test_missing_historical_v2_source_fails_without_v1_fallback(run):
    authority, _, _, _, _ = run
    def mutate(data):
        data["rule_set"]["ordered_source_artifacts"][0]["path"] = "missing/historical-v2.yaml"
    manifest = revised_manifest(authority, mutate)
    with pytest.raises(VersioningError) as error: _verify_manifest_artifacts(manifest, ROOT)
    assert error.value.code is VersioningErrorCode.HISTORICAL_CONTENT_UNAVAILABLE


def test_deserialized_version_mismatch_and_fatal_unsafe_core(run):
    authority, _, state, evaluator, context = run
    data = json.loads(v2.state_canonical_bytes_v2(state))
    data["capabilities"][v2.GRAPH]["capability_version"] = "3.0.0"
    result = v2.state_from_canonical_bytes_v2(canonical_json_bytes(data), resolved_versions=authority)
    assert result.succeeded and result.state.graph.readiness is v2.Readiness.VERSION_MISMATCH
    error = evaluator.evaluate("ASPECT", {}, result.state, context)
    assert error.status is Status.MISSING_CAPABILITY and error.errors[0].code == "capability_version_mismatch"
    data = json.loads(v2.state_canonical_bytes_v2(state))
    data["planets"][0]["planet_id"] = "Pluto"
    failure = v2.state_from_canonical_bytes_v2(canonical_json_bytes(data), resolved_versions=authority)
    assert not failure.succeeded and failure.state is None and failure.issues[0].code == "invalid_canonical_v2_state"


def test_six_capabilities_and_non_aspect_results_and_v1_replay_stay_exact(run):
    authority, snapshot, state, evaluator, context = run
    from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
    from systems.Parasara.engine.rules.registry import get_production_registry, predicate_registry_fingerprint_sha256
    legacy = prepare_predicate_snapshot(snapshot).state
    for key in legacy.capabilities:
        if key != v2.GRAPH:
            assert state.capabilities[key] == legacy.capabilities[key]
    before = state_canonical_bytes(legacy)
    registry_before = predicate_registry_fingerprint_sha256()
    old = PredicateEvaluator()
    for name, parameters in (("PLANET_IN_HOUSE", dict(planet="Mars", house=1)),
        ("HOUSE_OCCUPANT", dict(planet="Mars", house=2)),
        ("PLANET_EXALTED", dict(planet="Mars")),
        ("FUNCTIONAL_ROLE", dict(planet="Mars", role="benefic"))):
        assert evaluator.evaluate(name, parameters, state, context) == old.evaluate(name, parameters, legacy, context)
    assert state_canonical_bytes(prepare_predicate_snapshot(snapshot).state) == before
    assert predicate_registry_fingerprint_sha256() == registry_before
    assert get_production_registry().lookup("ASPECT").predicate_version == "1.0.0"
    assert v2.get_registry_v2().lookup("ASPECT").predicate_version == "2.0.0"
    replay = RuleVersionResolver().resolve(replace(compatibility_v1_config(), purpose=SelectionPurpose.REPLAY))
    assert replay.manifest_fingerprint_sha256 == "3e942f97cec7c24079faabc3db358b84177b752a8eb35a7b0d909f84a92d1220"


def test_cache_capacity_context_separation_and_uncached_results(run):
    authority, _, state, _, context = run
    evaluator = PredicateEvaluatorV2(resolved_versions=authority, capacity=1)
    filters = dict(from_planet="Mars", to_planet="Moon")
    assert not evaluator.evaluate("ASPECT", filters, state, context, use_cache=False).cache_hit
    assert evaluator.cache_size == 0
    evaluator.evaluate("ASPECT", filters, state, context)
    assert evaluator.cache_size == evaluator.cache.size == 1
    changed = replace(context, selected_planets=("Moon",))
    assert not evaluator.evaluate("ASPECT", filters, state, changed).cache_hit
    assert evaluator.cache_size == 1
    assert not evaluator.evaluate("ASPECT", filters, state, context).cache_hit
    with pytest.raises(TypeError): evaluator.cache.get(object())
    with pytest.raises(TypeError): evaluator.evaluate("ASPECT", filters, state, context, use_cache=1)


@pytest.mark.parametrize("field,value", [("readiness", "illegal"), ("content_empty", True), ("source_kind", "legacy_whole_sign_graph")])
def test_illegal_envelope_metadata_is_typed_malformed(run, field, value):
    authority, _, state, _, _ = run
    data = json.loads(v2.state_canonical_bytes_v2(state))
    data["capabilities"][v2.GRAPH][field] = value
    result = v2.state_from_canonical_bytes_v2(canonical_json_bytes(data), resolved_versions=authority)
    assert result.succeeded and result.state.graph.readiness is v2.Readiness.MALFORMED


def test_edges_are_copied_before_external_mutation(run):
    _, _, state, _, _ = run
    raw = json.loads(v2.state_canonical_bytes_v2(state))["capabilities"][v2.GRAPH]["content"]
    copied = replace(state.graph, content=raw)
    before = canonical_json_bytes(copied.content)
    raw["edges"].clear()
    raw["source_support"].reverse()
    assert canonical_json_bytes(copied.content) == before


def expanded_depth_payload(outer_depth):
    document = yaml.safe_load((ROOT / SOURCE).read_bytes())
    def nested(value, count):
        for _ in range(count):
            value = {"not": value}
        return value
    document["rules"] = document["rules"][:1]
    document["macros"] = [dict(id="deep", revision="1.0.0", parameters=[],
        body=nested(document["rules"][0]["when"], 40))]
    document["rules"][0]["when"] = nested(
        {"macro": {"id": "deep", "revision": "1.0.0", "arguments": {}}}, outer_depth)
    return yaml.safe_dump(document, sort_keys=False)


@pytest.mark.parametrize("outer_depth,accepted", [(23, True), (24, False)])
def test_expanded_condition_depth_uses_existing_limit(outer_depth, accepted):
    result = RuleDslCompilerV2.analyze_source(source_id=SOURCE, payload=expanded_depth_payload(outer_depth))
    assert isinstance(result, AnalysisSucceeded) is accepted
    if not accepted:
        assert result.diagnostics[0].code == "P07E404_COMPILED_DIGEST_MISMATCH"


def test_validation_offsets_match_the_existing_pinned_artifact():
    payload = (ROOT / "rules/parashara/aspects.yaml").read_bytes()
    table = yaml.safe_load(payload)
    # Prompt-06 knowledge pins hash canonical YAML content, not raw file bytes.
    assert hashlib.sha256(canonical_json_bytes(table)).hexdigest() == v2._ASPECT_ARTIFACT_SHA256
    assert table["version"] == 1
    assert set(v2._PINNED_CLASSICAL_OFFSETS) == set(v2.CANONICAL_PLANETS[:7])
    for source in v2.CANONICAL_PLANETS[:7]:
        row = table["planets"].get(source, table["planets"]["default"])
        assert v2._PINNED_CLASSICAL_OFFSETS[source] == tuple(row["offsets"])


def mutate_edge_consistency(edges, mutation):
    source, offset = ("Sun", 7) if mutation in ("unauthorized_offset", "missing_matched_planet") else ("Mars", 4)
    edge = next(e for e in edges if e["source"] == source and e["target"] is None and e["trace"]["offset"] == offset)
    # Construction rows can share trace objects; isolate exactly one corrupt row.
    edge["trace"] = deepcopy(edge["trace"])
    trace = edge["trace"]
    if mutation in ("forged_target", "unauthorized_offset", "sign_only_sign"):
        edge["target"] = None if mutation == "sign_only_sign" else "Moon"
        trace.update(target_sign="Gemini", target_house=3, matched_planets=["Moon", "Mercury"])
        if mutation == "unauthorized_offset":
            # Aries -> Gemini is a valid third offset, but Sun has only seventh.
            edge["aspect"] = "3th"
            trace["offset"] = 3
    elif mutation == "sign_only_house":
        trace["target_house"] = 3
    elif mutation == "matched_planets":
        trace["matched_planets"] = ["Moon"]
    elif mutation == "missing_matched_planet":
        trace["matched_planets"] = []
    else:
        raise AssertionError("unknown edge-consistency mutation")


def edge_consistency_outcome(authority, route, *, mutation=None, wrap=False):
    from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
    from systems.Parasara.engine.normalizer import chart_to_astrostate_strict
    from systems.Parasara.engine.astrostate_api import freeze_astrostate, require_snapshot
    values = [10, 95, 271, 61, 120, 180, 240, 300, 150] if wrap else [10, 65, 1, 61, 120, 180, 240, 300, 150]
    astro = chart_to_astrostate_strict(SuryaAdapter.from_mapping_strict(strict_payload(90 if wrap else 0, values)))
    if route == "preparation" and mutation:
        mutate_edge_consistency(astro.enrichments["aspects"]["edges"], mutation)
    snapshot = require_snapshot(freeze_astrostate(astro))
    result = prepare_predicate_snapshot_v2(snapshot, resolved_versions=authority)
    if route == "deserialization":
        data = json.loads(v2.state_canonical_bytes_v2(result.state))
        if mutation:
            mutate_edge_consistency(data["capabilities"][v2.GRAPH]["content"]["edges"], mutation)
        result = v2.state_from_canonical_bytes_v2(canonical_json_bytes(data), resolved_versions=authority)
    return snapshot, result


@pytest.mark.parametrize("route", ["preparation", "deserialization"])
@pytest.mark.parametrize("mutation", ["forged_target", "unauthorized_offset", "sign_only_sign", "sign_only_house", "matched_planets", "missing_matched_planet"])
def test_contradictory_edges_are_unavailable_before_evaluation(route, mutation):
    authority = resolve_v2()
    _, outcome = edge_consistency_outcome(authority, route, mutation=mutation)
    assert outcome.succeeded and not outcome.issues
    graph = outcome.state.graph
    assert graph.readiness is v2.Readiness.MALFORMED and graph.content is None
    assert graph.issues == ("aspect_coverage_contradictory",)
    evaluator = PredicateEvaluatorV2(resolved_versions=authority)
    node = dict(type="ASPECT_EXISTS", params=dict(from_planet="Mars", to_planet="Moon"))
    result = ConditionEvaluatorV2(evaluator).evaluate(node, outcome.state, PredicateEvaluationContext())
    assert result.status is Status.MISSING_CAPABILITY and not result.matched
    assert result.errors[0].code == "malformed_capability"
    assert result.errors[0].details["issues"] == graph.issues
    negated = ConditionEvaluatorV2(evaluator).evaluate(dict(type="NOT", children=[node]), outcome.state, PredicateEvaluationContext())
    assert negated.status is Status.MISSING_CAPABILITY and not negated.matched
    assert evaluator.cache_size == 0


@pytest.mark.parametrize("route", ["preparation", "deserialization"])
def test_forged_edge_cannot_change_the_clean_sealed_rule_to_matched(route):
    authority = resolve_v2()
    snapshot, clean = edge_consistency_outcome(authority, route)
    _, forged = edge_consistency_outcome(authority, route, mutation="forged_target")
    compiled = RuleDslCompilerV2(resolved_versions=authority).compile_authorized(source_id=SOURCE)
    assert isinstance(compiled, CompilationSucceeded)
    rule = compiled.compiled_rule_set.rules[0]
    evaluator = ConditionEvaluatorV2(PredicateEvaluatorV2(resolved_versions=authority))
    engine = RuleEngine(resolved_versions=authority)
    def evaluate(state):
        return engine.evaluate_compiled_rule(rule, condition_evaluator=evaluator,
            state=state, context=PredicateEvaluationContext(), evaluation_snapshot_digest=snapshot.logical_digest,
            evaluation_context={})
    assert evaluate(clean.state).status.value == "unmatched"
    rejected = evaluate(forged.state)
    assert rejected.status.value == "missing_capability"
    assert rejected.errors[0].code == "malformed_capability"
    assert rejected.errors[0].details["issues"] == ("aspect_coverage_contradictory",)
    assert evaluate(clean.state).status.value == "unmatched"


@pytest.mark.parametrize("route", ["preparation", "deserialization"])
def test_valid_wraparound_sign_and_planet_edges_remain_available(route):
    authority = resolve_v2()
    _, outcome = edge_consistency_outcome(authority, route, wrap=True)
    assert outcome.succeeded and outcome.state.graph.readiness is v2.Readiness.READY
    edges = outcome.state.graph.content["edges"]
    # Capricorn's fourth reaches Aries; house seven's seventh reaches house one.
    assert any(e["source"] == "Mars" and e["target"] == "Sun" and e["trace"]["offset"] == 4
        and e["trace"]["target_sign"] == "Aries" and e["trace"]["target_house"] == 10 for e in edges)
    assert any(e["source"] == "Mars" and e["target"] is None and e["trace"]["offset"] == 4
        and e["trace"]["matched_planets"] == ("Sun",) for e in edges)
    evaluator = PredicateEvaluatorV2(resolved_versions=authority)
    context = PredicateEvaluationContext()
    for target, house in (("Sun", 10), ("Moon", 1)):
        result = evaluator.evaluate("ASPECT", dict(from_planet="Mars", to_planet=target, to_house=house), outcome.state, context)
        assert result.status is Status.MATCHED and not result.errors
    for node in ("Rahu", "Ketu"):
        result = evaluator.evaluate("ASPECT", dict(from_planet=node), outcome.state, context)
        assert result.status is Status.MISSING_CAPABILITY and result.errors[0].code == "aspect_source_unsupported"


@pytest.mark.parametrize("route", ["preparation", "deserialization"])
def test_valid_empty_target_sign_edge_remains_an_aspect(route):
    authority = resolve_v2()
    _, outcome = edge_consistency_outcome(authority, route)
    edge = next(e for e in outcome.state.graph.content["edges"] if e["source"] == "Mars"
        and e["trace"]["offset"] == 8 and e["target"] is None)
    assert edge["trace"]["target_sign"] == "Scorpio" and edge["trace"]["matched_planets"] == ()
    state = replace(outcome.state, graph=replace(outcome.state.graph, content={**outcome.state.graph.content, "edges": (edge,)}))
    evaluator = PredicateEvaluatorV2(resolved_versions=authority)
    assert evaluator.evaluate("ASPECT", dict(from_planet="Mars"), state, PredicateEvaluationContext()).status is Status.MATCHED
