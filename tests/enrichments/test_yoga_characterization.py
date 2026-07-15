"""WP01 characterization contract for the active Yoga evaluation path."""

from copy import deepcopy
from pathlib import Path
from uuid import UUID

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.enrichments.yoga_engine import evaluate_yoga_rules
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules import engine
from systems.Parasara.engine.rules.loader import RULE_REGISTRY
from systems.Parasara.engine.rules.yoga_loader import load_yoga_rules
import systems.Parasara.engine.rules.predicates as _predicates  # noqa: F401


REPO_ROOT = Path(__file__).resolve().parents[2]
YOGA_RULES = REPO_ROOT / "systems" / "Parasara" / "rules" / "parashara" / "v1"
SURYA_TEST = REPO_ROOT / "systems" / "Parasara" / "fixtures" / "surya_test_chart.json"


@pytest.fixture(autouse=True)
def isolated_rule_engine_globals():
    rule_registry = deepcopy(RULE_REGISTRY)
    predicate_registry = dict(engine.PREDICATE_REGISTRY)
    predicate_cache = dict(engine._CACHE)
    RULE_REGISTRY.clear()
    engine.clear_cache()
    load_yoga_rules(str(YOGA_RULES))
    try:
        yield
    finally:
        RULE_REGISTRY.clear()
        RULE_REGISTRY.update(rule_registry)
        engine.PREDICATE_REGISTRY.clear()
        engine.PREDICATE_REGISTRY.update(predicate_registry)
        engine._CACHE.clear()
        engine._CACHE.update(predicate_cache)


def prepared_surya_test():
    return chart_to_astrostate(SuryaAdapter.load(str(SURYA_TEST)))


def without_trace_ids(value):
    if isinstance(value, dict):
        return {key: without_trace_ids(item) for key, item in value.items() if key != "trace_id"}
    if isinstance(value, list):
        return [without_trace_ids(item) for item in value]
    return value


def test_loader_exposes_the_current_three_rule_set_in_file_order():
    loaded = load_yoga_rules(str(YOGA_RULES))
    assert [(row["id"], row["name"], row["version"], row["category"]) for row in loaded] == [
        ("rajayoga_naive", "Naive Raja Yoga", 1, "rajayoga"),
        ("dhana_naive", "Naive Dhana Yoga", 1, "dhana"),
        ("arishta_naive", "Naive Arishta Yoga", 1, "arishta"),
    ]
    assert list(RULE_REGISTRY) == ["rajayoga_naive", "dhana_naive", "arishta_naive"]


def test_active_yoga_path_freezes_firing_nonfiring_shape_and_evidence_order():
    astro = prepared_surya_test()
    rows = evaluate_yoga_rules(astro)

    assert [row["yoga_id"] for row in rows] == ["rajayoga_naive", "dhana_naive", "arishta_naive"]
    assert [row["name"] for row in rows] == ["Naive Raja Yoga", "Naive Dhana Yoga", "Naive Arishta Yoga"]
    assert [row["matched"] for row in rows] == [True, False, False]
    assert astro.enrichments["yogas"] == rows

    for row in rows:
        assert list(row) == [
            "yoga_id",
            "name",
            "matched",
            "planets",
            "houses",
            "aspects_used",
            "evidence",
            "trace_id",
        ]
        assert isinstance(row["matched"], bool)
        assert isinstance(row["planets"], list)
        assert isinstance(row["houses"], list)
        assert isinstance(row["aspects_used"], list)
        assert isinstance(row["evidence"], dict)
        UUID(row["trace_id"])
        assert row["houses"] == []
        assert row["aspects_used"] == []

    raja, dhana, arishta = rows
    assert set(raja["planets"]) == {"Sun", "Mars"}
    assert [edge["source"] for edge in raja["evidence"]["children"][0]["matched_edges"]] == [
        "Saturn",
        "Saturn",
    ]
    assert [edge["target"] for edge in raja["evidence"]["children"][0]["matched_edges"]] == [
        "Mars",
        "Venus",
    ]
    assert raja["evidence"]["children"][1] == {"matched_planets": ["Sun", "Mars"]}
    assert set(dhana["planets"]) == set()
    assert dhana["evidence"]["children"][0] == {
        "predicate": "HOUSE_LORDS_COMBINATION",
        "reason": "unknown_predicate",
    }
    assert dhana["evidence"]["children"][1] == {}
    assert set(arishta["planets"]) == {"Moon", "Saturn"}
    assert arishta["evidence"]["children"] == [{}, {"matched_planets": ["Moon", "Saturn"]}]


def test_repeat_evaluation_changes_only_trace_identity_and_does_not_drift_registries():
    astro = prepared_surya_test()
    registry_before = deepcopy(RULE_REGISTRY)
    predicate_ids_before = list(engine.PREDICATE_REGISTRY)

    first = evaluate_yoga_rules(astro)
    first_state = astro.model_dump(mode="python")
    second = evaluate_yoga_rules(astro)
    second_state = astro.model_dump(mode="python")

    assert without_trace_ids(second) == without_trace_ids(first)
    assert [row["trace_id"] for row in second] != [row["trace_id"] for row in first]
    assert without_trace_ids(second_state) == without_trace_ids(first_state)
    assert RULE_REGISTRY == registry_before
    assert list(engine.PREDICATE_REGISTRY) == predicate_ids_before
