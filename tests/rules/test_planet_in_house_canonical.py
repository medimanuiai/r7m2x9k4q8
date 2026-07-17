"""WP08 canonical PLANET_IN_HOUSE reference-predicate contract."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from systems.Parasara.engine.rules import planet_in_house as canonical_module
from systems.Parasara.engine.rules.canonical import (
    FrozenMapping,
    predicate_result_full_json_bytes,
    predicate_result_logical_json_bytes,
    predicate_result_logical_sha256,
    predicate_result_to_full_data,
    predicate_result_to_logical_data,
)
from systems.Parasara.engine.rules.capabilities import (
    CapabilityFactObservation,
    CapabilityFactState,
    CapabilityInspection,
    CapabilityReadiness,
)
from systems.Parasara.engine.rules.models import PredicateResult, PredicateStatus
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    PreparedAstroState,
    predicate_evaluation_context_json_bytes,
    prepare_predicate_state,
    prepared_state_json_bytes,
)
from systems.Parasara.engine.rules.registry import get_production_registry


def planet(name="Mars", *, house=1, sign="Aries"):
    return SimpleNamespace(name=name, house=house, sign=sign, degree=12.0)


def source(*, planets=None):
    return SimpleNamespace(
        planets=[planet()] if planets is None else planets,
        lagna_sign="Aries",
        enrichments={},
        derived=None,
        metadata={},
        diagnostics={},
    )


def prepared(value=None) -> PreparedAstroState:
    outcome = prepare_predicate_state(source() if value is None else value)
    assert outcome.succeeded and outcome.state is not None
    return outcome.state


def evaluate(params, state=None, context=None):
    return canonical_module.evaluate_planet_in_house(
        params,
        prepared() if state is None else state,
        PredicateEvaluationContext() if context is None else context,
    )


def logical(result):
    return predicate_result_to_logical_data(result)


def assert_canonical(result, status, matched=False):
    assert type(result) is PredicateResult
    assert result.predicate_id == "PLANET_IN_HOUSE"
    assert result.predicate_version == "1.0.0"
    assert result.status is status
    assert result.matched is matched
    assert result.cache_hit is False
    assert result.evaluation_time_ms is None


def test_reference_definition_and_valid_normalization():
    definition = get_production_registry().lookup("PLANET_IN_HOUSE")
    result = evaluate({"house": 1, "planet": "  mars "})
    assert definition is not None
    assert definition.predicate_version == result.predicate_version
    assert tuple(item.capability_id for item in definition.required_capabilities) == (
        "planets.house_placement",
        "planets.normalized",
    )
    assert_canonical(result, PredicateStatus.MATCHED, True)
    assert dict(result.inputs) == {"house": 1, "planet": "Mars"}


def test_parameter_mapping_order_is_logically_equivalent():
    first = evaluate({"planet": "Mars", "house": 1})
    second = evaluate({"house": 1, "planet": "Mars"})
    assert first == second
    assert predicate_result_logical_json_bytes(first) == predicate_result_logical_json_bytes(second)


@pytest.mark.parametrize(
    "params",
    [
        {"house": 1},
        {"planet": "Mars"},
        {"planet": None, "house": 1},
        {"planet": "Mars", "house": None},
        {"planet": "Mars", "house": 1, "extra": True},
        {"planet": "Pluto", "house": 1},
        {"planet": 1, "house": 1},
        {"planet": "Mars", "house": 0},
        {"planet": "Mars", "house": 13},
        {"planet": "Mars", "house": -1},
        {"planet": "Mars", "house": True},
        {"planet": "Mars", "house": 1.0},
        {"planet": "Mars", "house": "1"},
        {"planet": "Mars", "house": []},
        {"planet": "Mars", "house": {}},
    ],
)
def test_invalid_parameter_matrix_never_queries_facts(monkeypatch, params):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("prepared capability/fact query was not skipped")

    monkeypatch.setattr(canonical_module, "inspect_prepared_capability", forbidden)
    monkeypatch.setattr(canonical_module, "observe_prepared_planet", forbidden)
    monkeypatch.setattr(canonical_module, "observe_prepared_planet_house", forbidden)
    result = evaluate(params)
    assert_canonical(result, PredicateStatus.INVALID_PARAMETERS)
    assert result.inputs == FrozenMapping({})
    assert result.evidence == FrozenMapping({})
    assert [error.code for error in result.errors] == ["invalid_parameters"]
    assert result.errors[0].recoverable is True
    assert [step.step_id for step in result.trace_steps] == [
        "planet_in_house.parameters",
        "planet_in_house.result",
    ]


def test_unsafe_and_cyclic_values_fail_without_repr_or_raw_value():
    cyclic = []
    cyclic.append(cyclic)
    for raw in (object(), cyclic):
        result = evaluate({"planet": raw, "house": 1})
        payload = predicate_result_logical_json_bytes(result)
        assert_canonical(result, PredicateStatus.INVALID_PARAMETERS)
        assert b"0x" not in payload
        assert b"object at" not in payload


@pytest.mark.parametrize(
    ("actual", "expected", "status", "matched"),
    [(1, 1, PredicateStatus.MATCHED, True), (3, 1, PredicateStatus.UNMATCHED, False)],
)
def test_factual_match_and_unmatch_contract(actual, expected, status, matched):
    result = evaluate({"planet": "Mars", "house": expected}, prepared(source(planets=[planet(house=actual)])))
    assert_canonical(result, status, matched)
    assert dict(result.evidence) == {
        "actual_house": actual,
        "capabilities": (
            FrozenMapping(
                {
                    "capability_id": "planets.house_placement",
                    "expected_version": "1.0.0",
                    "issues": (),
                    "observed_version": "1.0.0",
                    "readiness": "ready",
                    "source_kind": "planet_house_fields",
                }
            ),
            FrozenMapping(
                {
                    "capability_id": "planets.normalized",
                    "expected_version": "1.0.0",
                    "issues": (),
                    "observed_version": "1.0.0",
                    "readiness": "ready",
                    "source_kind": "normalized_planets",
                }
            ),
        ),
        "equal": matched,
        "expected_house": expected,
        "planet": "Mars",
    }
    assert [step.step_id for step in result.trace_steps] == [
        "planet_in_house.parameters",
        "planet_in_house.capabilities",
        "planet_in_house.planet",
        "planet_in_house.house",
        "planet_in_house.result",
    ]
    assert [step.parent_step_id for step in result.trace_steps] == [
        None,
        "planet_in_house.parameters",
        "planet_in_house.capabilities",
        "planet_in_house.planet",
        "planet_in_house.house",
    ]


def test_absent_planet_is_missing_capability_not_false():
    result = evaluate({"planet": "Moon", "house": 1})
    assert_canonical(result, PredicateStatus.MISSING_CAPABILITY)
    assert result.evidence["entity_state"] == "absent_entity"
    assert "actual_house" not in result.evidence
    assert [error.code for error in result.errors] == ["missing_planet_entity"]
    decisive = next(step for step in result.trace_steps if step.step_id == "planet_in_house.planet")
    assert decisive.error_code == "missing_planet_entity"


def test_present_planet_with_unavailable_house_is_missing_capability():
    state = prepared(source(planets=[planet(house=None)]))
    result = evaluate({"planet": "Mars", "house": 1}, state)
    assert_canonical(result, PredicateStatus.MISSING_CAPABILITY)
    assert "actual_house" not in result.evidence
    assert [error.code for error in result.errors] == ["malformed_capability"]


def test_each_capability_failure_matrix_and_no_partial_fact_use(monkeypatch):
    original = canonical_module.inspect_prepared_capability

    cases = (
        (CapabilityReadiness.MISSING, None, None, False, ("missing_attribute",), "missing_capability"),
        (CapabilityReadiness.MALFORMED, "1.0.0", "prepared", False, ("invalid_house",), "malformed_capability"),
        (CapabilityReadiness.VERSION_MISMATCH, "2.0.0", "prepared", False, ("contract_version_mismatch",), "capability_version_mismatch"),
        (CapabilityReadiness.UNSUPPORTED, None, None, False, ("manifest_miss",), "unsupported_capability"),
        (CapabilityReadiness.READY_EMPTY, "1.0.0", "prepared", True, (), "ready_empty_not_allowed"),
    )
    for failed_capability in ("planets.house_placement", "planets.normalized"):
        for readiness, observed, source_kind, empty, issues, code in cases:
            def inspect(state, requirement, *, _readiness=readiness, _observed=observed, _source=source_kind, _empty=empty, _issues=issues):
                if requirement.capability_id == failed_capability:
                    return CapabilityInspection(
                        capability_id=requirement.capability_id,
                        expected_version=requirement.capability_version,
                        observed_version=_observed,
                        readiness=_readiness,
                        source_kind=_source,
                        content_empty=_empty,
                        issues=_issues,
                    )
                return original(state, requirement)

            monkeypatch.setattr(canonical_module, "inspect_prepared_capability", inspect)
            monkeypatch.setattr(
                canonical_module,
                "observe_prepared_planet",
                lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("fact query must not run")),
            )
            result = evaluate({"planet": "Mars", "house": 1})
            assert_canonical(result, PredicateStatus.MISSING_CAPABILITY)
            assert [error.code for error in result.errors] == [code]
            assert result.errors[0].details["capability_id"] == failed_capability
            assert "actual_house" not in result.evidence
            monkeypatch.undo()


def test_multiple_capability_failures_use_registry_order(monkeypatch):
    def inspect(_state, requirement):
        return CapabilityInspection(
            capability_id=requirement.capability_id,
            expected_version=requirement.capability_version,
            observed_version=None,
            readiness=CapabilityReadiness.MISSING,
            source_kind=None,
            content_empty=False,
            issues=("missing_attribute",),
        )

    monkeypatch.setattr(canonical_module, "inspect_prepared_capability", inspect)
    result = evaluate({"planet": "Mars", "house": 1})
    assert [error.details["capability_id"] for error in result.errors] == [
        "planets.house_placement",
        "planets.normalized",
    ]


def test_context_selection_is_factually_neutral():
    results = [
        evaluate({"planet": "Mars", "house": 1}, context=PredicateEvaluationContext(selected_planets=value))
        for value in (None, (), ("Moon",))
    ]
    assert results[0] == results[1] == results[2]


def test_ready_capabilities_but_unavailable_strict_house_fact(monkeypatch):
    monkeypatch.setattr(
        canonical_module,
        "observe_prepared_planet_house",
        lambda *_args, **_kwargs: CapabilityFactObservation(
            capability_id="planets.house_placement",
            capability_version="1.0.0",
            state=CapabilityFactState.ABSENT_ENTITY,
            entity_kind="planet",
            entity_id="Mars",
            value_present=False,
            issues=("entity_absent",),
        ),
    )
    result = evaluate({"planet": "Mars", "house": 1})
    assert_canonical(result, PredicateStatus.MISSING_CAPABILITY)
    assert result.evidence["entity_state"] == "present"
    assert result.evidence["fact_state"] == "absent_entity"
    assert "actual_house" not in result.evidence
    assert [error.code for error in result.errors] == ["missing_planet_house"]


def test_registry_handler_is_the_canonical_typed_implementation():

    mutable = source(planets=[planet(house=3)])
    assert evaluate({"planet": "Mars", "house": 3}, prepared(mutable)).matched is True
    assert evaluate({"planet": "Mars", "house": 1}, prepared(mutable)).matched is False
    registry = get_production_registry()
    handlers = tuple(registry.handler(item) for item in registry.exposed_ids())
    assert registry.exposed_ids() == (
        "ASPECT", "ASPECT_EXISTS", "FUNCTIONAL_ROLE", "HOUSE_OCCUPANT",
        "PLANET_EXALTED", "PLANET_IN_HOUSE",
    )
    assert len({id(handler) for handler in handlers}) == 5
    assert registry.handler("PLANET_IN_HOUSE") is canonical_module.evaluate_planet_in_house


def test_equivalent_states_and_source_mutation_are_isolated():
    first_source = source(planets=[planet(house=1)])
    state = prepared(first_source)
    before = evaluate({"planet": "Mars", "house": 1}, state)
    first_source.planets[0].house = 2
    after = evaluate({"planet": "Mars", "house": 1}, state)
    equivalent = evaluate({"planet": "Mars", "house": 1}, prepared(source(planets=[planet(house=1)])))
    assert before == after == equivalent


def test_inputs_state_context_and_result_are_deeply_immutable_and_unmodified():
    params = {"planet": "Mars", "house": 1}
    state = prepared()
    context = PredicateEvaluationContext(selected_planets=("Mars",))
    state_before = prepared_state_json_bytes(state)
    context_before = predicate_evaluation_context_json_bytes(context)
    result = evaluate(params, state, context)
    assert params == {"planet": "Mars", "house": 1}
    assert prepared_state_json_bytes(state) == state_before
    assert predicate_evaluation_context_json_bytes(context) == context_before
    with pytest.raises(TypeError):
        result.evidence["planet"] = "Moon"
    with pytest.raises(FrozenInstanceError):
        result.status = PredicateStatus.ERROR


def test_controlled_unexpected_failure_is_safe(monkeypatch):
    def fail(*_args, **_kwargs):
        raise RuntimeError("secret C:\\provider\\path 0xDEADBEEF")

    monkeypatch.setattr(canonical_module, "observe_prepared_planet", fail)
    result = evaluate({"planet": "Mars", "house": 1})
    assert_canonical(result, PredicateStatus.ERROR)
    assert result.evidence == FrozenMapping({})
    assert [error.code for error in result.errors] == ["predicate_execution_error"]
    assert result.errors[0].recoverable is False
    payload = predicate_result_logical_json_bytes(result)
    assert b"secret" not in payload and b"provider" not in payload and b"0x" not in payload


def test_projection_bytes_hashes_and_telemetry_boundary_are_exact():
    representatives = {
        "matched": evaluate({"planet": "Mars", "house": 1}),
        "unmatched": evaluate({"planet": "Mars", "house": 2}),
        "missing": evaluate({"planet": "Moon", "house": 1}),
        "invalid": evaluate({"planet": "Mars", "house": True}),
    }
    for result in representatives.values():
        logical_bytes = predicate_result_logical_json_bytes(result)
        full_bytes = predicate_result_full_json_bytes(result)
        assert json.loads(logical_bytes) == predicate_result_to_logical_data(result)
        assert json.loads(full_bytes) == predicate_result_to_full_data(result)
        assert predicate_result_logical_sha256(result) == hashlib.sha256(logical_bytes).hexdigest()
        warm = replace(result, cache_hit=True, evaluation_time_ms=1.25)
        assert warm == result
        assert predicate_result_logical_json_bytes(warm) == logical_bytes
        assert predicate_result_to_full_data(warm) != predicate_result_to_full_data(result)
    assert {name: hashlib.sha256(predicate_result_logical_json_bytes(value)).hexdigest() for name, value in representatives.items()} == {
        "matched": "86f6aaf742e99abed3d89b55db04445308f1821da3f2e85526dc0b495099e7de",
        "unmatched": "13f60d3b1bc516988e7c6e999fbc42114837cce220f146464c4571d3dd78c694",
        "missing": "813ec32e62f61c9fde774c50399c949700c4eb8e076efdbe943cf76f92f79f7f",
        "invalid": "3231dce442fc3bec26925948c362e5db0b28aa6abd8bb681ecdb4231605feb14",
    }
    assert {
        name: (
            len(predicate_result_full_json_bytes(value)),
            hashlib.sha256(predicate_result_full_json_bytes(value)).hexdigest(),
        )
        for name, value in representatives.items()
    } == {
        "matched": (2145, "f07653b335b8edda36f7fdbb29c5e59a46cf62090f5389654c07cd4a10d3c4be"),
        "unmatched": (2153, "79eadae226bf47719ec444ff424d23d266cfcc3ebec4ccd5e4e910ecbd5de577"),
        "missing": (2295, "8c27f9edd2ae5453db866377277310131cd3c473ca9b56879e2e9c870024aae7"),
        "invalid": (1047, "99b7acb0aedf87687143ff70a55a44d97af186e7e9d830070ba27e2d9c5d3368"),
    }


def test_unexpected_error_projection_has_exact_safe_bytes_and_hash(monkeypatch):
    monkeypatch.setattr(
        canonical_module,
        "observe_prepared_planet",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("private value")),
    )
    result = evaluate({"planet": "Mars", "house": 1})
    payload = predicate_result_logical_json_bytes(result)
    full_payload = predicate_result_full_json_bytes(result)
    assert hashlib.sha256(payload).hexdigest() == "493426b459b0139473e4489b65e3413f6e2ab8c61b83d675459d494bb539a18a"
    assert len(full_payload) == 1766
    assert hashlib.sha256(full_payload).hexdigest() == "868d30f0c1ab55fc165b32b2e3d2fdc8314b6f81a5fb7fe82ba4e661185d21c6"
    assert b"private" not in payload
    assert b"private" not in full_payload


def test_module_has_no_forbidden_imports_or_calls():
    path = Path(canonical_module.__file__)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    text = path.read_text(encoding="utf-8")
    forbidden_imports = {
        "AstroState", "Chart", "PlanetState", "compute_functional_roles", "os", "time",
        "random", "uuid", "subprocess", "pickle",
    }
    forbidden_calls = {"open", "repr", "id", "hash", "asdict"}
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not imports & forbidden_imports
    assert not calls & forbidden_calls
    assert not any(isinstance(node, (ast.Global, ast.Nonlocal)) for node in ast.walk(tree))
    assert "default=str" not in text
