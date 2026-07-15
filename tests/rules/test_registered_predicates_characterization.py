"""WP01 characterization contract for the registered predicate surface."""

from copy import deepcopy
from dataclasses import asdict, fields

import pytest

from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.rules import engine
import systems.Parasara.engine.rules.predicates as _predicates  # noqa: F401


EXPECTED_IDS = {
    "ASPECT",
    "ASPECT_EXISTS",
    "PLANET_IN_HOUSE",
    "HOUSE_OCCUPANT",
    "FUNCTIONAL_ROLE",
    "PLANET_EXALTED",
}

ASPECT_EDGE = {
    "source": "Mars",
    "target": "Moon",
    "aspect": "4th",
    "kind": "whole_sign",
}


@pytest.fixture(autouse=True)
def isolated_predicate_globals():
    registry = dict(engine.PREDICATE_REGISTRY)
    cache = dict(engine._CACHE)
    engine.clear_cache()
    try:
        yield
    finally:
        engine.PREDICATE_REGISTRY.clear()
        engine.PREDICATE_REGISTRY.update(registry)
        engine._CACHE.clear()
        engine._CACHE.update(cache)


@pytest.fixture
def prepared_astro():
    return AstroState(
        metadata={"exaltations": {"Sun": 10.0}},
        location=None,
        lagna_sign="Aries",
        planets=[
            PlanetState(name="Mars", sign="Aries", degree=12.0, house=1),
            PlanetState(name="Moon", sign="Cancer", degree=4.0, house=4),
            PlanetState(name="Sun", sign="Aries", degree=10.0, house=1),
        ],
        houses=[],
        enrichments={
            "aspects": {"edges": [deepcopy(ASPECT_EDGE)]},
            "functional_roles": {"Mars": ["yogakaraka"]},
        },
    )


def logical_result(result):
    value = asdict(result)
    value.pop("cache_hit")
    value.pop("evaluation_time_ms")
    return value


def test_registry_contains_exactly_the_six_current_public_ids():
    assert set(engine.PREDICATE_REGISTRY) == EXPECTED_IDS
    assert engine.PREDICATE_REGISTRY["ASPECT"] is engine.PREDICATE_REGISTRY["ASPECT_EXISTS"]


@pytest.mark.parametrize(
    ("predicate_id", "params", "matched", "result_id", "evidence"),
    [
        (
            "ASPECT",
            {"from_planet": "Mars", "to_planet": "Moon"},
            True,
            "ASPECT_EXISTS",
            {"matched_edges": [ASPECT_EDGE]},
        ),
        (
            "ASPECT_EXISTS",
            {"from_planet": "Moon", "to_planet": "Mars"},
            False,
            "ASPECT_EXISTS",
            {},
        ),
        ("PLANET_IN_HOUSE", {"planet": "Mars", "house": 1}, True, "PLANET_IN_HOUSE", {"planet": "Mars", "house": 1}),
        ("PLANET_IN_HOUSE", {"planet": "Mars", "house": 2}, False, "PLANET_IN_HOUSE", {}),
        ("HOUSE_OCCUPANT", {"planet": "Moon", "house": 4}, True, "HOUSE_OCCUPANT", {"planet": "Moon", "house": 4}),
        ("HOUSE_OCCUPANT", {"planet": "Moon", "house": 5}, False, "HOUSE_OCCUPANT", {}),
        (
            "FUNCTIONAL_ROLE",
            {"planets": ["Mars"], "role_in": ["yogakaraka"]},
            True,
            "FUNCTIONAL_ROLE",
            {"matched_planets": ["Mars"]},
        ),
        (
            "FUNCTIONAL_ROLE",
            {"planets": ["Mars"], "role_in": ["functional_malefic"]},
            False,
            "FUNCTIONAL_ROLE",
            {},
        ),
        ("PLANET_EXALTED", {"planet": "Sun"}, True, "PLANET_EXALTED", {"planet": "Sun", "exaltation_degree": 10.0}),
        ("PLANET_EXALTED", {"planet": "Moon"}, False, "PLANET_EXALTED", {}),
    ],
)
def test_matched_and_unmatched_return_contracts_are_exact(
    prepared_astro, predicate_id, params, matched, result_id, evidence
):
    state_before = deepcopy(prepared_astro.__dict__)
    params_before = deepcopy(params)

    context = {"planets": ["Mars"]} if predicate_id == "FUNCTIONAL_ROLE" else {}
    first = engine.evaluate_predicate(predicate_id, params, prepared_astro, context)
    second = engine.evaluate_predicate(predicate_id, params, prepared_astro, context)

    assert [field.name for field in fields(engine.PredicateResult)] == [
        "matched",
        "predicate_id",
        "inputs",
        "evidence",
        "trace_steps",
        "errors",
        "cache_hit",
        "evaluation_time_ms",
    ]
    assert first.matched is matched
    assert first.predicate_id == result_id
    assert first.inputs == params
    assert first.evidence == evidence
    assert first.trace_steps == []
    assert first.errors == []
    assert first.cache_hit is False
    assert isinstance(first.evaluation_time_ms, float)
    assert first.evaluation_time_ms >= 0
    assert second.cache_hit is True
    assert logical_result(second) == logical_result(first)
    assert params == params_before
    assert prepared_astro.__dict__ == state_before


@pytest.mark.parametrize(
    ("predicate_id", "result_id", "matched", "evidence"),
    [
        ("ASPECT", "ASPECT_EXISTS", True, {"matched_edges": [ASPECT_EDGE]}),
        ("ASPECT_EXISTS", "ASPECT_EXISTS", True, {"matched_edges": [ASPECT_EDGE]}),
        ("PLANET_IN_HOUSE", "PLANET_IN_HOUSE", False, {}),
        ("HOUSE_OCCUPANT", "HOUSE_OCCUPANT", False, {}),
        ("FUNCTIONAL_ROLE", "FUNCTIONAL_ROLE", False, {}),
        ("PLANET_EXALTED", "PLANET_EXALTED", False, {}),
    ],
)
def test_missing_parameters_preserve_current_safe_result(prepared_astro, predicate_id, result_id, matched, evidence):
    result = engine.evaluate_predicate(predicate_id, {}, prepared_astro, {})
    assert result.matched is matched
    assert result.predicate_id == result_id
    assert result.inputs == {}
    assert result.evidence == evidence
    assert result.trace_steps == []
    assert result.errors == []


def test_predicate_name_is_normalized_but_input_mapping_is_preserved(prepared_astro):
    params = {"planet": "Mars", "house": 1}
    result = engine.evaluate_predicate("planet_in_house", params, prepared_astro, {})
    assert result.predicate_id == "PLANET_IN_HOUSE"
    assert result.inputs == params
    assert result.matched is True


def test_equivalent_fresh_state_repeats_the_same_logical_result(prepared_astro):
    params = {"planet": "Sun"}
    first = engine.evaluate_predicate("PLANET_EXALTED", params, prepared_astro, {})
    engine.clear_cache()
    equivalent_state = deepcopy(prepared_astro)
    second = engine.evaluate_predicate("PLANET_EXALTED", params, equivalent_state, {})

    # This records current behavior only. Whether metadata alone should imply
    # exaltation is a deferred semantic decision, not a WP01 correction.
    assert first.matched is True
    assert logical_result(second) == logical_result(first)
    assert second.cache_hit is False
