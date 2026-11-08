"""Prompt-06 predicate-cache isolation across incompatible fingerprints."""

from __future__ import annotations

from types import SimpleNamespace

from systems.Parasara.engine.rules.evaluator import (
    PredicateEvaluator,
    PredicateResultCache,
    build_predicate_cache_key,
    predicate_cache_key_sha256,
)
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    prepare_predicate_state,
)
from systems.Parasara.engine.rules.registry import get_production_registry

from tests.versioning.conftest import SyntheticCatalogBuilder


def _source():
    return SimpleNamespace(
        planets=[SimpleNamespace(name="Mars", house=1, sign="Aries", degree=12.0)],
        lagna_sign="Aries",
        enrichments={},
        derived=None,
        metadata={},
    )


def _prepared_state():
    outcome = prepare_predicate_state(_source())
    assert outcome.succeeded and outcome.state is not None
    return outcome.state


def _two_authorities(synthetic_catalog: SyntheticCatalogBuilder):
    one = synthetic_catalog.add(family="fam", version="one")
    resolved_one = one.resolver.resolve(one.config)
    two = synthetic_catalog.add(family="fam", version="two")
    resolved_two = two.resolver.resolve(two.config)
    return resolved_one, resolved_two


def test_identical_executable_components_produce_the_same_component_fingerprint(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    resolved_one, resolved_two = _two_authorities(synthetic_catalog)
    assert resolved_one.predicate_component_fingerprint_sha256 == (
        resolved_two.predicate_component_fingerprint_sha256
    )


def test_shared_cache_cannot_return_a_result_created_under_an_incompatible_fingerprint(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    resolved_one, resolved_two = _two_authorities(synthetic_catalog)
    state = _prepared_state()
    definition = get_production_registry().lookup("PLANET_IN_HOUSE")
    assert definition is not None
    validation = definition.parameter_schema.validate({"planet": "Mars", "house": 1})
    assert validation.valid and validation.normalized_inputs is not None

    key_one = build_predicate_cache_key(
        definition,
        validation.normalized_inputs,
        state,
        relevant_context={},
        predicate_component_fingerprint_sha256="1" * 64,
    )
    key_two = build_predicate_cache_key(
        definition,
        validation.normalized_inputs,
        state,
        relevant_context={},
        predicate_component_fingerprint_sha256="2" * 64,
    )
    assert key_one != key_two
    assert predicate_cache_key_sha256(key_one) != predicate_cache_key_sha256(key_two)

    shared_cache = PredicateResultCache(capacity=8)
    evaluator_one = PredicateEvaluator(
        predicate_component_fingerprint_sha256="1" * 64
    )
    evaluator_one._cache = shared_cache  # exercise one truly shared storage instance
    result_one = evaluator_one.evaluate(
        "PLANET_IN_HOUSE", {"planet": "Mars", "house": 1}, state, PredicateEvaluationContext()
    )
    assert shared_cache.peek(key_one) is not None
    assert shared_cache.peek(key_two) is None

    evaluator_two = PredicateEvaluator(
        predicate_component_fingerprint_sha256="2" * 64
    )
    evaluator_two._cache = shared_cache
    result_two = evaluator_two.evaluate(
        "PLANET_IN_HOUSE", {"planet": "Mars", "house": 1}, state, PredicateEvaluationContext()
    )
    assert result_two.cache_hit is False
    assert shared_cache.peek(key_two) is not None

    assert result_one.matched is result_two.matched is True
    assert result_one.status is result_two.status


def test_predicate_evaluator_instances_are_isolated_by_default() -> None:
    state = _prepared_state()
    first = PredicateEvaluator(capacity=4)
    second = PredicateEvaluator(capacity=4)
    first.evaluate("PLANET_IN_HOUSE", {"planet": "Mars", "house": 1}, state, PredicateEvaluationContext())
    assert first.cache_size == 1
    assert second.cache_size == 0
