"""Prompt-03 Career/Yoga migration and public compatibility tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from dataclasses import replace

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.inference import InferenceEngine, InferenceResult
from systems.Parasara.engine.interpreters.career import (
    career_inference_rule_matches,
    evaluate_career_batch,
    infer_career,
    interpret_career,
    prepare_career_facts,
    project_career_compatibility,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"
APPROVED = ROOT / "systems" / "Parasara" / "tests" / "fixtures"


def astro(name: str):
    return chart_to_astrostate(SuryaAdapter.load(str(FIXTURES / name)))


def test_career_calls_shared_engine_once_and_projects_result_values(monkeypatch):
    calls = []
    original = InferenceEngine.aggregate

    def counted(self, **kwargs):
        calls.append(kwargs)
        return original(self, **kwargs)

    monkeypatch.setattr(InferenceEngine, "aggregate", counted)
    output = interpret_career(astro("surya_test_chart.json"))
    assert len(calls) == 1
    assert calls[0]["domain"] == "career"
    assert output["score"] == 0.907
    assert output["confidence"] == 0.427


def test_career_base_and_yoga_are_typed_contributions_with_complete_lineage():
    batch = evaluate_career_batch(prepare_career_facts(astro("surya_test_chart.json")))
    result = infer_career(batch)
    assert isinstance(result, InferenceResult)
    values = {item.rule_id: item for item in result.contributions}
    assert values["career.base_kendra_strength"].final_contribution == batch.base_score - 0.5
    assert values["rajayoga_naive"].base_weight == 1.0
    assert values["rajayoga_naive"].final_contribution == 0.18
    assert values["rajayoga_naive"].evidence_references
    assert values["rajayoga_naive"].source_rule_trace_id
    assert len(career_inference_rule_matches(batch)) == len(batch.candidates) + 1


def test_projection_does_not_recompute_when_result_is_supplied(monkeypatch):
    batch = evaluate_career_batch(prepare_career_facts(astro("surya_test_chart.json")))
    result = infer_career(batch)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("projection attempted a second inference")

    monkeypatch.setattr(InferenceEngine, "aggregate", forbidden)
    output = project_career_compatibility(batch, result)
    assert output["score"] == result.normalized_score
    assert output["confidence"] == result.confidence


def test_historical_adjusted_score_and_contribution_fields_are_inert():
    batch = evaluate_career_batch(prepare_career_facts(astro("surya_test_chart.json")))
    expected = infer_career(batch)
    altered_candidates = tuple(
        replace(
            item,
            adjusted_score=0.999,
            contribution=0.999 if item.matched else 0.0,
        )
        for item in batch.candidates
    )
    altered = replace(batch, candidates=altered_candidates)
    assert infer_career(altered) == expected


def test_all_locked_career_fixtures_remain_byte_identical():
    pairs = (
        (
            "golden_chart_01.json", "golden_chart_01_career_snapshot.json",
            "74442a0726173dcac3c521f1e67542443c16c43fbb39e7bded27f9e1601e3be3",
        ),
        (
            "surya_generated_chart.json", "surya_generated_chart_career_snapshot.json",
            "169cf5ce5ac9d8e678b160daf23293f365f2ab192a02a7aad90caab4da839dd9",
        ),
    )
    for fixture, approved, expected_digest in pairs:
        actual = interpret_career(astro(fixture))
        expected = json.loads((APPROVED / approved).read_text(encoding="utf-8"))
        assert actual == expected
        payload = json.dumps(actual, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        assert hashlib.sha256(payload).hexdigest() == expected_digest
