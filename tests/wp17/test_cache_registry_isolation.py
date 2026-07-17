"""WP17 cache identity/bounds and registry isolation enforcement."""

from __future__ import annotations

from dataclasses import replace

import pytest

from systems.Parasara.engine.rules.canonical import (
    predicate_result_logical_json_bytes,
)
from systems.Parasara.engine.rules.evaluator import (
    PredicateEvaluator,
    predicate_cache_key_to_data,
)
from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext
from systems.Parasara.engine.rules.registry import (
    PredicateRegistry,
    PredicateRegistryError,
    PredicateRegistryFrozenError,
    get_production_registry,
    predicate_registry_fingerprint_bytes,
)
from tests.wp17.test_purity_safety import _prepared_predicate_state


def test_cache_key_identity_alias_cold_warm_and_telemetry_are_isolated():
    state = _prepared_predicate_state()
    evaluator = PredicateEvaluator(capacity=4)
    parameters = {"from_planet": "Mars", "to_planet": "Moon"}
    cold = evaluator.evaluate(
        "ASPECT", parameters, state, PredicateEvaluationContext()
    )
    warm = evaluator.evaluate(
        "ASPECT_EXISTS", parameters, state, PredicateEvaluationContext()
    )
    assert cold.cache_hit is False and warm.cache_hit is True
    assert predicate_result_logical_json_bytes(cold) == predicate_result_logical_json_bytes(
        warm
    )
    assert cold == warm
    key = evaluator.cache.keys()[0]
    assert set(predicate_cache_key_to_data(key)) == {
        "context_relevance",
        "definition_sha256",
        "parameters_sha256",
        "predicate_id",
        "predicate_version",
        "prepared_state_sha256",
        "relevant_context_sha256",
        "system_scope",
    }
    assert key.predicate_id == "ASPECT_EXISTS"

    changed_telemetry = replace(
        warm, cache_hit=False, evaluation_time_ms=999_999.0
    )
    assert changed_telemetry == warm
    assert predicate_result_logical_json_bytes(changed_telemetry) == (
        predicate_result_logical_json_bytes(warm)
    )


def test_cache_bound_eviction_and_nonfactual_policy_are_deterministic():
    state = _prepared_predicate_state()
    evaluator = PredicateEvaluator(capacity=2)
    context = PredicateEvaluationContext()
    first = evaluator.evaluate(
        "PLANET_IN_HOUSE", {"planet": "Mars", "house": 1}, state, context
    )
    second = evaluator.evaluate(
        "HOUSE_OCCUPANT", {"planet": "Moon", "house": 4}, state, context
    )
    first_key, second_key = evaluator.cache.keys()
    assert first.matched and second.matched
    evaluator.evaluate(
        "PLANET_IN_HOUSE", {"planet": "Mars", "house": 2}, state, context
    )
    assert evaluator.cache_size == 2
    assert first_key not in evaluator.cache.keys()
    assert second_key in evaluator.cache.keys()
    reevaluated = evaluator.evaluate(
        "PLANET_IN_HOUSE", {"planet": "Mars", "house": 1}, state, context
    )
    assert reevaluated.cache_hit is False

    size = evaluator.cache_size
    missing = evaluator.evaluate(
        "PLANET_IN_HOUSE", {"planet": "Jupiter", "house": 1}, state, context
    )
    invalid = evaluator.evaluate("PLANET_IN_HOUSE", {}, state, context)
    error = evaluator.evaluate("UNKNOWN_PREDICATE", {}, state, context)
    assert [missing.status.value, invalid.status.value, error.status.value] == [
        "missing_capability",
        "invalid_parameters",
        "error",
    ]
    assert evaluator.cache_size == size


def test_isolated_registry_cannot_contaminate_or_rebind_canonical_registry():
    canonical = get_production_registry()
    identity = id(canonical)
    fingerprint = predicate_registry_fingerprint_bytes(canonical)
    definition = canonical.lookup("PLANET_IN_HOUSE")
    assert definition is not None

    isolated = PredicateRegistry()
    isolated.register(definition)
    with pytest.raises(PredicateRegistryError) as first:
        isolated.register(definition)
    isolated.finalize()
    with pytest.raises(PredicateRegistryFrozenError):
        isolated.remove("PLANET_IN_HOUSE")

    repeated = PredicateRegistry()
    repeated.register(definition)
    with pytest.raises(PredicateRegistryError) as second:
        repeated.register(definition)
    assert str(first.value) == str(second.value)
    assert id(get_production_registry()) == identity
    assert predicate_registry_fingerprint_bytes(canonical) == fingerprint
