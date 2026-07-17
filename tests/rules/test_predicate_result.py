"""Canonical public predicate/condition boundary smoke contracts."""

from __future__ import annotations

from types import SimpleNamespace

from systems.Parasara.engine.rules.canonical import (
    predicate_result_full_json_bytes,
    predicate_result_from_full_data,
    predicate_result_to_full_data,
)
from systems.Parasara.engine.rules.conditions import ConditionEvaluator
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.models import (
    ConditionResult,
    PredicateResult,
    PredicateStatus,
)
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    prepare_predicate_state,
)


def _state():
    source = SimpleNamespace(
        planets=[SimpleNamespace(name="Mars", sign="Aries", degree=0.0, house=7)],
        lagna_sign="Aries",
        enrichments={},
        derived=None,
        metadata={},
        diagnostics={},
    )
    outcome = prepare_predicate_state(source)
    assert outcome.succeeded and outcome.state is not None
    return outcome.state


def test_planet_in_house_returns_typed_result_and_instance_cache_telemetry():
    evaluator = PredicateEvaluator()
    params = {"planet": "Mars", "house": 7}
    first = evaluator.evaluate(
        "PLANET_IN_HOUSE", params, _state(), PredicateEvaluationContext()
    )
    second = evaluator.evaluate(
        "PLANET_IN_HOUSE", params, _state(), PredicateEvaluationContext()
    )

    assert isinstance(first, PredicateResult)
    assert first.status is PredicateStatus.MATCHED and first.matched
    assert first.predicate_id == "PLANET_IN_HOUSE"
    assert first.cache_hit is False
    assert second.cache_hit is True


def test_missing_exaltation_fact_is_nonfactual_not_boolean_false():
    result = PredicateEvaluator().evaluate(
        "PLANET_EXALTED",
        {"planet": "Mars"},
        _state(),
        PredicateEvaluationContext(),
    )
    assert result.status is PredicateStatus.MISSING_CAPABILITY
    assert result.matched is False
    assert result.errors


def test_planet_sign_is_not_reinterpreted_as_canonical_exaltation():
    source = SimpleNamespace(
        planets=[SimpleNamespace(name="Sun", sign="Aries", degree=10.0, house=1)],
        lagna_sign="Aries",
        enrichments={},
        derived=None,
        metadata={},
        diagnostics={},
    )
    outcome = prepare_predicate_state(source)
    assert outcome.succeeded and outcome.state is not None
    result = PredicateEvaluator().evaluate(
        "PLANET_EXALTED",
        {"planet": "Sun"},
        outcome.state,
        PredicateEvaluationContext(),
    )
    assert result.status is PredicateStatus.MISSING_CAPABILITY
    assert result.matched is False


def test_condition_boundary_returns_typed_recursive_result():
    result = ConditionEvaluator(PredicateEvaluator()).evaluate(
        {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 7}},
        _state(),
        PredicateEvaluationContext(),
    )
    assert isinstance(result, PredicateResult)
    logical = ConditionEvaluator(PredicateEvaluator()).evaluate(
        {
            "type": "AND",
            "children": [
                {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 7}},
                {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 1}},
            ],
        },
        _state(),
        PredicateEvaluationContext(),
    )
    assert isinstance(logical, ConditionResult)
    assert logical.status is PredicateStatus.UNMATCHED


def test_full_serialization_round_trips_without_permissive_string_coercion():
    result = PredicateEvaluator().evaluate(
        "PLANET_IN_HOUSE",
        {"planet": "Mars", "house": 7},
        _state(),
        PredicateEvaluationContext(),
    )
    data = predicate_result_to_full_data(result)
    restored = predicate_result_from_full_data(data)
    payload = predicate_result_full_json_bytes(result)
    assert restored == result
    assert payload.startswith(b"{") and payload.endswith(b"}")
    assert b"PredicateResult" not in payload
