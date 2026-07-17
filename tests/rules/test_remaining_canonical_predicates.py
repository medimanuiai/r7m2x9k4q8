"""WP11 contracts for the remaining prepared-state predicate handlers."""

from __future__ import annotations

import ast
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from systems.Parasara.engine.rules.canonical import (
    condition_result_logical_json_bytes,
    predicate_result_full_json_bytes,
    predicate_result_logical_json_bytes,
)
from systems.Parasara.engine.rules.conditions import ConditionEvaluator
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.models import ConditionResult, PredicateResult, PredicateStatus
from systems.Parasara.engine.rules.prepared_state import (
    CapabilitySupply,
    PredicateEvaluationContext,
    PreparedAstroState,
    prepare_predicate_state,
)
from systems.Parasara.engine.rules.registry import get_production_registry
from systems.Parasara.engine.rules import canonical_predicates


def planet(name, *, house=1, sign="Aries", exalted=None):
    value = SimpleNamespace(name=name, house=house, sign=sign, degree=12.5)
    if exalted is not None:
        value.flags = {"exalted": exalted}
    return value


def source(*, planets=None, edges=None, roles=None, exaltations=None):
    return SimpleNamespace(
        planets=[planet("Sun"), planet("Moon", house=2, sign="Taurus")] if planets is None else planets,
        lagna_sign="Aries",
        enrichments={"aspects": {"edges": [] if edges is None else edges, "config_version": "legacy-v1"}},
        derived={"functional_roles": {"Sun": {"functional_role": "benefic"}} if roles is None else roles},
        metadata={"exaltations": {} if exaltations is None else exaltations},
        diagnostics={},
    )


def prepared(value=None, *, supplies=()) -> PreparedAstroState:
    outcome = prepare_predicate_state(source() if value is None else value, capability_supplies=supplies)
    assert outcome.succeeded and outcome.state is not None
    return outcome.state


def context(selected=None, *, instant=None):
    return PredicateEvaluationContext(selected_planets=selected, evaluation_instant=instant)


def assert_result(result, predicate_id, status, matched=False):
    assert type(result) is PredicateResult
    assert result.predicate_id == predicate_id
    assert result.predicate_version == "1.0.0"
    assert result.status is status
    assert result.matched is matched
    assert result.cache_hit is False


def test_six_ids_resolve_to_five_definitions_and_dispatch_handlers():
    registry = get_production_registry()
    assert registry.exposed_ids() == (
        "ASPECT", "ASPECT_EXISTS", "FUNCTIONAL_ROLE", "HOUSE_OCCUPANT",
        "PLANET_EXALTED", "PLANET_IN_HOUSE",
    )
    assert registry.lookup("ASPECT") is registry.lookup("ASPECT_EXISTS")
    assert set(canonical_predicates.CANONICAL_HANDLER_DISPATCH) == {
        "ASPECT_EXISTS", "FUNCTIONAL_ROLE", "HOUSE_OCCUPANT", "PLANET_EXALTED",
    }


@pytest.mark.parametrize(
    ("function", "predicate_id", "valid"),
    [
        (canonical_predicates.evaluate_house_occupant, "HOUSE_OCCUPANT", {"house": 1, "planet": "Sun"}),
        (canonical_predicates.evaluate_aspect_exists, "ASPECT_EXISTS", {}),
        (canonical_predicates.evaluate_functional_role, "FUNCTIONAL_ROLE", {"role_in": ["benefic"]}),
        (canonical_predicates.evaluate_planet_exalted, "PLANET_EXALTED", {"planet": "Sun"}),
    ],
)
def test_invalid_parameters_are_typed_and_skip_capability_inspection(monkeypatch, function, predicate_id, valid):
    monkeypatch.setattr(
        canonical_predicates,
        "inspect_prepared_capability",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("capability inspection must be skipped")),
    )
    invalid = dict(valid)
    invalid["unknown"] = True
    result = function(invalid, prepared(), context())
    assert_result(result, predicate_id, PredicateStatus.INVALID_PARAMETERS)
    assert dict(result.inputs) == {}
    assert dict(result.evidence) == {}
    assert [error.code for error in result.errors] == ["invalid_parameters"]


def test_house_occupant_match_unmatch_missing_and_separate_cache_identity():
    state = prepared(source(planets=[planet("Mars", house=3)]))
    matched = canonical_predicates.evaluate_house_occupant({"house": 3, "planet": "mars"}, state, context())
    unmatched = canonical_predicates.evaluate_house_occupant({"house": 1, "planet": "Mars"}, state, context())
    missing = canonical_predicates.evaluate_house_occupant({"house": 1, "planet": "Moon"}, state, context())
    assert_result(matched, "HOUSE_OCCUPANT", PredicateStatus.MATCHED, True)
    assert_result(unmatched, "HOUSE_OCCUPANT", PredicateStatus.UNMATCHED)
    assert_result(missing, "HOUSE_OCCUPANT", PredicateStatus.MISSING_CAPABILITY)
    assert dict(matched.inputs) == {"house": 3, "planet": "Mars"}
    assert matched.evidence["requested_occupant"] == "Mars"
    assert matched.evidence["actual_house"] == matched.evidence["expected_house"] == 3
    assert [step.step_id for step in matched.trace_steps] == [
        "house_occupant.parameters", "house_occupant.capabilities", "house_occupant.planet",
        "house_occupant.house", "house_occupant.result",
    ]
    evaluator = PredicateEvaluator()
    first = evaluator.evaluate("HOUSE_OCCUPANT", {"house": 3, "planet": "Mars"}, state, context())
    second = evaluator.evaluate("PLANET_IN_HOUSE", {"house": 3, "planet": "Mars"}, state, context())
    assert first.matched and second.matched
    assert evaluator.cache_size == 2
    assert {key.predicate_id for key in evaluator.cache.keys()} == {"HOUSE_OCCUPANT", "PLANET_IN_HOUSE"}


def aspect_state(edges):
    return prepared(
        source(
            planets=[planet("Sun", house=1), planet("Moon", house=2)],
            edges=edges,
        )
    )


def test_aspect_filters_empty_graph_order_duplicates_and_target_none():
    duplicate = {"source": "Sun", "target": "Moon", "aspect": "7th", "kind": "whole_sign"}
    state = aspect_state([duplicate, duplicate, {"source": "Sun", "target": None, "kind": "open"}])
    any_edge = canonical_predicates.evaluate_aspect_exists({}, state, context())
    all_filters = canonical_predicates.evaluate_aspect_exists(
        {"from_house": 1, "to_house": 2, "from_planet": "Sun", "to_planet": "Moon"}, state, context()
    )
    target_none = canonical_predicates.evaluate_aspect_exists({"to_planet": "Moon"}, state, context())
    empty = canonical_predicates.evaluate_aspect_exists({}, aspect_state([]), context())
    assert_result(any_edge, "ASPECT_EXISTS", PredicateStatus.MATCHED, True)
    assert_result(all_filters, "ASPECT_EXISTS", PredicateStatus.MATCHED, True)
    assert_result(target_none, "ASPECT_EXISTS", PredicateStatus.MATCHED, True)
    assert_result(empty, "ASPECT_EXISTS", PredicateStatus.UNMATCHED)
    assert all_filters.evidence["matched_indexes"] == (0, 1)
    expected_edge = {**duplicate, "from_house": 1, "to_house": 2}
    assert tuple(dict(edge) for edge in all_filters.evidence["matched_edges"]) == (expected_edge, expected_edge)
    assert any_edge.evidence["matched_indexes"] == (0, 1, 2)
    assert empty.evidence["edge_count"] == 0
    assert empty.evidence["matched_indexes"] == ()


def test_aspect_aliases_share_canonical_result_and_cache_entry():
    state = aspect_state([{"source": "Sun", "target": "Moon", "aspect": "7th"}])
    evaluator = PredicateEvaluator()
    alias = evaluator.evaluate(" aspect ", {"from_planet": "sun"}, state, context())
    canonical = evaluator.evaluate("ASPECT_EXISTS", {"from_planet": "Sun"}, state, context(selected=("Moon",)))
    assert alias.predicate_id == canonical.predicate_id == "ASPECT_EXISTS"
    assert alias.cache_hit is False and canonical.cache_hit is True
    assert evaluator.cache_size == 1
    assert evaluator.cache.keys()[0].predicate_id == "ASPECT_EXISTS"


@pytest.mark.parametrize("role", ["benefic", "malefic", "functional_malefic", "yogakaraka", "functional_benefic", "functional_neutral"])
def test_functional_role_preserves_each_vocabulary_value(role):
    state = prepared(source(planets=[planet("Sun")], roles={"Sun": {"functional_role": role}}))
    result = canonical_predicates.evaluate_functional_role({"role_in": [role]}, state, context())
    assert_result(result, "FUNCTIONAL_ROLE", PredicateStatus.MATCHED, True)
    assert result.evidence["matched_planets"] == ("Sun",)


def test_functional_role_selection_missing_policy_and_all_matches():
    state = prepared(
        source(
            planets=[planet("Sun"), planet("Moon", house=2), planet("Mars", house=3)],
            roles={
                "Sun": {"functional_role": "benefic"},
                "Moon": {"functional_role": "malefic"},
            },
        )
    )
    matched = canonical_predicates.evaluate_functional_role(
        {"role_in": ["benefic", "malefic"]}, state, context()
    )
    empty = canonical_predicates.evaluate_functional_role({"role_in": ["benefic"]}, state, context(selected=()))
    unavailable = canonical_predicates.evaluate_functional_role(
        {"role_in": ["functional_neutral"]}, state, context(selected=("Mars",))
    )
    decisive = canonical_predicates.evaluate_functional_role(
        {"role_in": ["benefic"]}, state, context(selected=("Sun", "Mars"))
    )
    assert_result(matched, "FUNCTIONAL_ROLE", PredicateStatus.MATCHED, True)
    assert matched.evidence["matched_planets"] == ("Sun", "Moon")
    assert len(matched.evidence["candidates"]) == 3
    assert_result(empty, "FUNCTIONAL_ROLE", PredicateStatus.UNMATCHED)
    assert empty.evidence["selection_policy"] == "explicit_empty"
    assert empty.evidence["candidates"] == ()
    assert_result(unavailable, "FUNCTIONAL_ROLE", PredicateStatus.MISSING_CAPABILITY)
    assert [error.code for error in unavailable.errors] == ["missing_functional_role_fact"]
    assert_result(decisive, "FUNCTIONAL_ROLE", PredicateStatus.MATCHED, True)
    assert decisive.evidence["candidates"][1]["fact_state"] == "absent_entity"


def test_functional_role_context_isolation_and_neutral_instant_sharing():
    state = prepared(source(planets=[planet("Sun"), planet("Moon", house=2)], roles={
        "Sun": {"functional_role": "benefic"}, "Moon": {"functional_role": "malefic"},
    }))
    evaluator = PredicateEvaluator()
    instant = datetime(2025, 1, 1, tzinfo=timezone.utc)
    first = evaluator.evaluate("FUNCTIONAL_ROLE", {"role_in": ["benefic"]}, state, context(("Sun",)))
    neutral = evaluator.evaluate("FUNCTIONAL_ROLE", {"role_in": ["benefic"]}, state, context(("Sun",), instant=instant))
    isolated = evaluator.evaluate("FUNCTIONAL_ROLE", {"role_in": ["benefic"]}, state, context(("Moon",)))
    assert first.cache_hit is False and neutral.cache_hit is True and isolated.cache_hit is False
    assert evaluator.cache_size == 2
    assert {key.context_relevance for key in evaluator.cache.keys()} == {"selected_planets"}


@pytest.mark.parametrize(
    ("value", "matched", "rule"),
    [(True, True, "explicit_flag_boolean"), (False, False, "explicit_flag_boolean"),
     (12.5, True, "configured_metadata_entry"), (0, True, "configured_metadata_entry")],
)
def test_exaltation_preserves_flag_and_metadata_meanings(value, matched, rule):
    if type(value) is bool:
        state = prepared(source(planets=[planet("Sun", exalted=value)], exaltations=None))
    else:
        state = prepared(source(planets=[planet("Sun")], exaltations={"Sun": value}))
    result = canonical_predicates.evaluate_planet_exalted({"planet": "Sun"}, state, context())
    status = PredicateStatus.MATCHED if matched else PredicateStatus.UNMATCHED
    assert_result(result, "PLANET_EXALTED", status, matched)
    assert result.evidence["interpretation_rule"] == rule
    assert result.evidence["records"][0]["value"] == value


def test_exaltation_absent_entity_fact_and_unsupported_source_are_nonfactual():
    base = prepared(source(planets=[planet("Sun")], exaltations={}))
    absent_entity = canonical_predicates.evaluate_planet_exalted({"planet": "Moon"}, base, context())
    absent_fact = canonical_predicates.evaluate_planet_exalted({"planet": "Sun"}, base, context())
    supplied = CapabilitySupply(
        capability_id="dignity.exaltation_facts", capability_version="1.0.0",
        source_kind="future_source", content={"Sun": 1},
    )
    supplied_source = source(planets=[planet("Sun")])
    supplied_source.metadata = {}
    unsupported = canonical_predicates.evaluate_planet_exalted(
        {"planet": "Sun"}, prepared(supplied_source, supplies=(supplied,)), context()
    )
    assert_result(absent_entity, "PLANET_EXALTED", PredicateStatus.MISSING_CAPABILITY)
    assert_result(absent_fact, "PLANET_EXALTED", PredicateStatus.MISSING_CAPABILITY)
    assert_result(unsupported, "PLANET_EXALTED", PredicateStatus.MISSING_CAPABILITY)
    assert [error.code for error in unsupported.errors] == ["unsupported_exaltation_source"]


def test_every_exposed_id_is_a_canonical_condition_leaf_and_unknown_remains_error():
    state = prepared(source(
        planets=[planet("Sun", house=1, exalted=True), planet("Moon", house=2)],
        edges=[{"source": "Sun", "target": "Moon", "aspect": "7th"}],
        roles={"Sun": {"functional_role": "benefic"}, "Moon": {"functional_role": "malefic"}},
    ))
    nodes = {
        "ASPECT": {"from_planet": "Sun"},
        "ASPECT_EXISTS": {"to_planet": "Moon"},
        "FUNCTIONAL_ROLE": {"role_in": ["benefic"]},
        "HOUSE_OCCUPANT": {"house": 1, "planet": "Sun"},
        "PLANET_EXALTED": {"planet": "Sun"},
        "PLANET_IN_HOUSE": {"planet": "Sun", "house": 1},
    }
    evaluator = ConditionEvaluator(PredicateEvaluator())
    for predicate_id, params in nodes.items():
        result = evaluator.evaluate({"type": predicate_id, "params": params}, state, context())
        assert type(result) is PredicateResult
        assert result.status is not PredicateStatus.ERROR
        assert all(error.code != "predicate_not_migrated" for error in result.errors)
    for predicate_id in ("UNKNOWN", "HOUSE_LORDS_COMBINATION"):
        result = evaluator.evaluate({"type": predicate_id, "params": {}}, state, context())
        assert result.status is PredicateStatus.ERROR
        assert [error.code for error in result.errors] == ["unknown_condition_type"]


def test_mixed_condition_preserves_all_six_exposed_leaves_and_five_cache_entries():
    state = prepared(source(
        planets=[planet("Sun", house=1, exalted=True), planet("Moon", house=2)],
        edges=[{"source": "Sun", "target": "Moon", "aspect": "7th"}],
        roles={"Sun": {"functional_role": "benefic"}, "Moon": {"functional_role": "malefic"}},
    ))
    predicate_evaluator = PredicateEvaluator()
    evaluator = ConditionEvaluator(predicate_evaluator)
    tree = {
        "type": "AND",
        "children": [
            {"type": "ASPECT", "params": {"from_planet": "Sun"}},
            {"type": "ASPECT_EXISTS", "params": {"from_planet": "Sun"}},
            {"type": "FUNCTIONAL_ROLE", "params": {"role_in": ["benefic"]}},
            {"type": "HOUSE_OCCUPANT", "params": {"house": 1, "planet": "Sun"}},
            {"type": "PLANET_EXALTED", "params": {"planet": "Sun"}},
            {"type": "PLANET_IN_HOUSE", "params": {"planet": "Sun", "house": 1}},
        ],
    }
    result = evaluator.evaluate(tree, state, context())
    assert type(result) is ConditionResult
    assert result.status is PredicateStatus.MATCHED
    assert [child.result.predicate_id for child in result.children] == [
        "ASPECT_EXISTS", "ASPECT_EXISTS", "FUNCTIONAL_ROLE", "HOUSE_OCCUPANT",
        "PLANET_EXALTED", "PLANET_IN_HOUSE",
    ]
    assert result.children[1].result.cache_hit is True
    assert predicate_evaluator.cache_size == 5
    payload = condition_result_logical_json_bytes(result)
    assert len(payload) == 17121
    assert hashlib.sha256(payload).hexdigest() == "f12996360f946a50be485422e1531525b4a8958f51ce90d07da8cde5853b100d"


def test_results_are_deterministic_deeply_immutable_and_telemetry_neutral():
    state = aspect_state([{"source": "Sun", "target": "Moon", "aspect": "7th"}])
    result = canonical_predicates.evaluate_aspect_exists({}, state, context())
    equivalent = canonical_predicates.evaluate_aspect_exists({}, state, context(selected=("Moon",)))
    assert result == equivalent
    assert predicate_result_logical_json_bytes(result) == predicate_result_logical_json_bytes(equivalent)
    warm = replace(result, cache_hit=True, evaluation_time_ms=2.5)
    assert warm == result
    assert predicate_result_logical_json_bytes(warm) == predicate_result_logical_json_bytes(result)
    with pytest.raises(TypeError):
        result.evidence["matched_indexes"] = ()


def test_representative_logical_bytes_and_hashes_are_exact():
    cases = {
        "house": canonical_predicates.evaluate_house_occupant(
            {"house": 1, "planet": "Sun"}, prepared(source(planets=[planet("Sun")])), context()
        ),
        "aspect": canonical_predicates.evaluate_aspect_exists(
            {"from_planet": "Sun"},
            aspect_state([{"source": "Sun", "target": "Moon", "aspect": "7th"}]),
            context(),
        ),
        "role": canonical_predicates.evaluate_functional_role(
            {"role_in": ["benefic"]},
            prepared(source(planets=[planet("Sun")], roles={"Sun": {"functional_role": "benefic"}})),
            context(),
        ),
        "exalted": canonical_predicates.evaluate_planet_exalted(
            {"planet": "Sun"}, prepared(source(planets=[planet("Sun", exalted=True)])), context()
        ),
    }
    assert {
        name: (len(payload := predicate_result_logical_json_bytes(result)), hashlib.sha256(payload).hexdigest())
        for name, result in cases.items()
    } == {
        "house": (2215, "027b92af98aa3e79ac7af6a735a2fba2bd291b77e20dee9ee535a79ff0bf2db9"),
        "aspect": (1922, "b950f9413e5fea809b03d13c660263204c1ab23cb175f2a964e6c166e71c68e3"),
        "role": (2889, "e17d85b154cb4aa60e7ea0d9096910ef7280bd3bb90bf0430eeaeb6e8193c7f2"),
        "exalted": (2620, "d9e397f2004374384be092cadce7d6045596bbed84f4c746a3f5c5d747753aa3"),
    }
    assert {
        name: (len(payload := predicate_result_full_json_bytes(result)), hashlib.sha256(payload).hexdigest())
        for name, result in cases.items()
    } == {
        "house": (2259, "1546d328331c664e8dc5121b1c5b59edb50d5ec78dc075adba768855a36804bc"),
        "aspect": (1966, "657c10947c620396b91d1391a6f3c5ae8476c503a94b912f2ec4c95946d4d38b"),
        "role": (2933, "eb50fbafbf3d517cd955e7a6db09f702d36d5ee33152c2895ebdcee28757d87f"),
        "exalted": (2664, "e1fdf5c7ec3d06c7f19e935994eb8434096a6ac20d13b8d4051815d14c780687"),
    }


def test_capability_and_conflicting_source_failures_never_become_false():
    missing_graph_source = source()
    missing_graph_source.enrichments = {"aspects": []}
    missing_roles_source = source()
    missing_roles_source.derived = None
    conflict_source = source(planets=[planet("Sun", exalted=True)], exaltations={"Sun": False})
    cases = (
        canonical_predicates.evaluate_aspect_exists({}, prepared(missing_graph_source), context()),
        canonical_predicates.evaluate_functional_role(
            {"role_in": ["benefic"]}, prepared(missing_roles_source), context()
        ),
        canonical_predicates.evaluate_planet_exalted(
            {"planet": "Sun"}, prepared(conflict_source), context()
        ),
    )
    assert all(result.status is PredicateStatus.MISSING_CAPABILITY for result in cases)
    assert all(result.matched is False and result.errors for result in cases)


@pytest.mark.parametrize(
    ("function", "predicate_id", "params"),
    [
        (canonical_predicates.evaluate_house_occupant, "HOUSE_OCCUPANT", {"house": 1, "planet": "Sun"}),
        (canonical_predicates.evaluate_aspect_exists, "ASPECT_EXISTS", {}),
        (canonical_predicates.evaluate_functional_role, "FUNCTIONAL_ROLE", {"role_in": ["benefic"]}),
        (canonical_predicates.evaluate_planet_exalted, "PLANET_EXALTED", {"planet": "Sun"}),
    ],
)
def test_unexpected_defects_are_safe_typed_errors(monkeypatch, function, predicate_id, params):
    monkeypatch.setattr(
        canonical_predicates,
        "_inspect",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("secret C:\\provider\\path 0xBAD")),
    )
    result = function(params, prepared(), context())
    assert_result(result, predicate_id, PredicateStatus.ERROR)
    assert [error.code for error in result.errors] == ["predicate_execution_error"]
    payload = predicate_result_logical_json_bytes(result)
    assert b"secret" not in payload and b"provider" not in payload and b"0xBAD" not in payload


def test_handler_module_has_no_producer_io_time_random_or_reflection_paths():
    path = Path("systems/Parasara/engine/rules/canonical_predicates.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    } | {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    text = path.read_text(encoding="utf-8")
    assert not imports & {"os", "pathlib", "random", "time", "uuid", "importlib", "inspect"}
    for forbidden in (
        "compute_functional_roles", "open(", "getcwd", "listdir", "glob(",
        "legacy_planet_flags]", "legacy_metadata_exaltations]",
    ):
        assert forbidden not in text
