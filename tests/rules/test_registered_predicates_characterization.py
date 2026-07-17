"""Typed characterization for the six registered predicate IDs."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.models import PredicateResult, PredicateStatus
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    prepare_predicate_state,
)
from systems.Parasara.engine.rules.registry import get_production_registry


EXPECTED_IDS = (
    "ASPECT",
    "ASPECT_EXISTS",
    "FUNCTIONAL_ROLE",
    "HOUSE_OCCUPANT",
    "PLANET_EXALTED",
    "PLANET_IN_HOUSE",
)


@pytest.fixture
def prepared_state():
    source = SimpleNamespace(
        planets=[
            SimpleNamespace(name="Mars", sign="Aries", degree=12.0, house=1),
            SimpleNamespace(name="Moon", sign="Cancer", degree=4.0, house=4),
            SimpleNamespace(name="Sun", sign="Aries", degree=10.0, house=1),
        ],
        lagna_sign="Aries",
        enrichments={
            "aspects": {
                "edges": [
                    {"source": "Mars", "target": "Moon", "aspect": "4th", "kind": "whole_sign"}
                ],
                "config_version": "legacy-v1",
            }
        },
        derived={"functional_roles": {"Mars": {"functional_role": "yogakaraka"}}},
        metadata={"exaltations": {"Sun": 10.0}},
        diagnostics={},
    )
    outcome = prepare_predicate_state(source)
    assert outcome.succeeded and outcome.state is not None
    return outcome.state


def test_registry_contains_exactly_six_ids_and_one_alias():
    registry = get_production_registry()
    assert registry.exposed_ids() == EXPECTED_IDS
    assert registry.lookup("ASPECT") is registry.lookup("ASPECT_EXISTS")


@pytest.mark.parametrize(
    ("predicate_id", "params", "selected", "status"),
    (
        ("ASPECT", {"from_planet": "Mars", "to_planet": "Moon"}, None, PredicateStatus.MATCHED),
        ("ASPECT_EXISTS", {"from_planet": "Moon", "to_planet": "Mars"}, None, PredicateStatus.UNMATCHED),
        ("PLANET_IN_HOUSE", {"planet": "Mars", "house": 1}, None, PredicateStatus.MATCHED),
        ("PLANET_IN_HOUSE", {"planet": "Mars", "house": 2}, None, PredicateStatus.UNMATCHED),
        ("HOUSE_OCCUPANT", {"planet": "Moon", "house": 4}, None, PredicateStatus.MATCHED),
        ("HOUSE_OCCUPANT", {"planet": "Moon", "house": 5}, None, PredicateStatus.UNMATCHED),
        ("FUNCTIONAL_ROLE", {"role_in": ["yogakaraka"]}, ("Mars",), PredicateStatus.MATCHED),
        ("FUNCTIONAL_ROLE", {"role_in": ["malefic"]}, ("Mars",), PredicateStatus.UNMATCHED),
        ("PLANET_EXALTED", {"planet": "Sun"}, None, PredicateStatus.MATCHED),
        ("PLANET_EXALTED", {"planet": "Moon"}, None, PredicateStatus.MISSING_CAPABILITY),
    ),
)
def test_matched_unmatched_and_nonfactual_results_are_typed(
    prepared_state, predicate_id, params, selected, status
):
    result = PredicateEvaluator().evaluate(
        predicate_id,
        params,
        prepared_state,
        PredicateEvaluationContext(selected_planets=selected),
    )
    assert type(result) is PredicateResult
    assert result.status is status
    assert result.matched is (status is PredicateStatus.MATCHED)
    assert result.predicate_version == "1.0.0"
    assert isinstance(result.trace_steps, tuple)
    assert isinstance(result.errors, tuple)


@pytest.mark.parametrize(
    "predicate_id",
    ("PLANET_IN_HOUSE", "HOUSE_OCCUPANT", "FUNCTIONAL_ROLE", "PLANET_EXALTED"),
)
def test_missing_required_parameters_are_explicitly_invalid(prepared_state, predicate_id):
    result = PredicateEvaluator().evaluate(
        predicate_id, {}, prepared_state, PredicateEvaluationContext()
    )
    assert result.status is PredicateStatus.INVALID_PARAMETERS
    assert result.errors[0].code == "invalid_parameters"


def test_alias_normalization_and_cache_are_deterministic(prepared_state):
    evaluator = PredicateEvaluator()
    context = PredicateEvaluationContext()
    params = {"from_planet": "Mars", "to_planet": "Moon"}
    first = evaluator.evaluate("aspect", params, prepared_state, context)
    second = evaluator.evaluate("ASPECT_EXISTS", params, prepared_state, context)
    assert first.predicate_id == second.predicate_id == "ASPECT_EXISTS"
    assert first == second
    assert first.cache_hit is False and second.cache_hit is True
