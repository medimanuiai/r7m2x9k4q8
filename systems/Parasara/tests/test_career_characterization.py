"""WP01 characterization contract for active Career/public output behavior."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.interpreters.career import interpret_career
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules import engine, loader, runtime
from systems.Parasara.tools.generate_snapshot import generate


REPO_ROOT = Path(__file__).resolve().parents[3]
RULES_DIR = REPO_ROOT / "systems" / "Parasara" / "rules" / "parashara" / "v1"
GOLDEN_INPUT = REPO_ROOT / "systems" / "Parasara" / "fixtures" / "golden_chart_01.json"
SURYA_TEST = REPO_ROOT / "systems" / "Parasara" / "fixtures" / "surya_test_chart.json"
APPROVED_OUTPUT = REPO_ROOT / "systems" / "Parasara" / "tests" / "snapshots" / "output_golden_chart_01.json"
APPROVED_CAREER = REPO_ROOT / "systems" / "Parasara" / "tests" / "fixtures" / "golden_chart_01_career_snapshot.json"


@pytest.fixture(autouse=True)
def isolated_rule_globals():
    rules = deepcopy(loader.RULE_REGISTRY)
    predicate_registry = dict(engine.PREDICATE_REGISTRY)
    predicate_cache = dict(engine._CACHE)
    loader.load_rules_from_dir(str(RULES_DIR))
    engine.clear_cache()
    try:
        yield
    finally:
        loader.RULE_REGISTRY.clear()
        loader.RULE_REGISTRY.update(rules)
        engine.PREDICATE_REGISTRY.clear()
        engine.PREDICATE_REGISTRY.update(predicate_registry)
        engine._CACHE.clear()
        engine._CACHE.update(predicate_cache)


def load_astro(path):
    return chart_to_astrostate(SuryaAdapter.load(str(path)))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_candidate_membership_order_and_golden_career_contract(monkeypatch):
    astro = load_astro(GOLDEN_INPUT)
    state_before = astro.model_dump(mode="python")
    candidates = []
    original = runtime.evaluate_rule_with_score

    def recording_evaluator(candidate_astro, rule):
        candidates.append(deepcopy(rule))
        return original(candidate_astro, rule)

    monkeypatch.setattr(runtime, "evaluate_rule_with_score", recording_evaluator)
    actual = interpret_career(astro)
    approved = json.loads(APPROVED_CAREER.read_text(encoding="utf-8"))

    assert [rule["id"] for rule in candidates] == [
        "strong_in_10_Sun",
        "strong_in_10_Moon",
        "strong_in_10_Mars",
        "rajayoga_naive",
    ]
    assert actual == approved
    assert list(actual) == [
        "summary",
        "score",
        "confidence",
        "components",
        "indicators",
        "evidence",
        "scoring",
        "trace_id",
    ]
    assert actual["score"] == 0.735
    assert actual["confidence"] == 0.3
    assert actual["components"] == [
        {"type": "planet", "planet": "Moon", "house": 4, "weight": 0.21},
        {"type": "planet", "planet": "Mars", "house": 1, "weight": 0.26},
    ]
    assert actual["indicators"] == []
    assert actual["evidence"] == []
    assert actual["scoring"] == {
        "base_score": 0.735,
        "total_contribution": 0.0,
        "final_score": 0.735,
        "formula": "final = min(1.0, base_score + sum(contributions))",
    }
    assert astro.model_dump(mode="python") == state_before


def test_approved_public_golden_is_consumed_read_only(tmp_path):
    approved_hash_before = sha256(APPROVED_OUTPUT)
    approved = json.loads(APPROVED_OUTPUT.read_text(encoding="utf-8"))
    output_path = tmp_path / "generated-output.json"

    generated = generate(str(GOLDEN_INPUT), str(output_path))

    assert generated == approved
    assert json.loads(output_path.read_text(encoding="utf-8")) == approved
    assert sha256(APPROVED_OUTPUT) == approved_hash_before


def test_nonempty_career_result_freezes_order_rounding_evidence_and_repeatability():
    astro = load_astro(SURYA_TEST)
    state_before = astro.model_dump(mode="python")

    first = interpret_career(astro)
    second = interpret_career(astro)

    assert second == first
    assert astro.model_dump(mode="python") == state_before
    assert list(first) == [
        "summary",
        "score",
        "confidence",
        "components",
        "indicators",
        "evidence",
        "scoring",
        "trace_id",
    ]
    assert first["summary"] == "Career score 0.907 (confidence 0.427)"
    assert first["score"] == 0.907
    assert first["confidence"] == 0.427
    assert first["trace_id"] == "career_001"
    assert first["components"] == [
        {"type": "planet", "planet": "Moon", "house": 1, "weight": 0.01},
        {"type": "planet", "planet": "Mars", "house": 10, "weight": -0.04},
        {"type": "planet", "planet": "Venus", "house": 10, "weight": 0.21},
        {"type": "planet", "planet": "Saturn", "house": 1, "weight": 0.01},
        {"type": "house", "house": 10, "weight": 0.085, "occupants": ["Mars", "Venus"]},
        {"type": "rule", "rule_id": "10th_lord_Venus", "weight": 0.18},
        {"type": "rule", "rule_id": "rajayoga_naive", "weight": 0.18},
    ]
    assert [row["rule_id"] for row in first["indicators"]] == ["10th_lord_Venus", "rajayoga_naive"]
    assert [row["contribution"] for row in first["indicators"]] == [0.18, 0.18]
    assert first["indicators"][0]["evidence"] == {"lord": "Venus", "dignity": "own_sign"}
    assert first["indicators"][1]["evidence"] == {"occ1": ["Moon"], "occ10": ["Venus"]}
    assert [row["rule_id"] for row in first["evidence"]] == ["10th_lord_Venus", "rajayoga_naive"]
    assert [row["contribution"] for row in first["evidence"]] == [0.18, 0.18]
    assert first["scoring"] == {
        "base_score": 0.547,
        "total_contribution": 0.36,
        "final_score": 0.907,
        "formula": "final = min(1.0, base_score + sum(contributions))",
    }
    assert [Path(indicator["context"]["_source_file"]).name for indicator in first["indicators"]] == [
        "derived_rules.yml",
        "yogas.yaml",
    ]
