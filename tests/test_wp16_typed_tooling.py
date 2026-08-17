"""WP16 typed artifact generation and compatibility safety contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from tests.testing_framework import typed_rule_evaluation
from tests.testing_framework.generate_full_artifacts import run_rules_and_trace


FIXTURE = Path("systems/Parasara/fixtures/golden_chart_01.json")


def _astro():
    return chart_to_astrostate(SuryaAdapter.load(str(FIXTURE)))


def test_artifacts_are_typed_ordered_repeatable_and_detached(tmp_path):
    fixed_paths = tuple(
        Path("tests/reports/artifacts") / name
        for name in ("rule_traces.json", "career_rule_traces.json")
    )
    before = {path: path.read_bytes() if path.exists() else None for path in fixed_paths}
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    yoga, career = run_rules_and_trace(_astro(), first_dir)
    first_yoga_bytes = (first_dir / "rule_traces.json").read_bytes()
    first_career_bytes = (first_dir / "career_rule_traces.json").read_bytes()

    assert [(row["rule_match"]["rule_id"], row["rule_match"]["status"]) for row in yoga] == [
        ("rajayoga_naive", "unmatched"),
        ("dhana_naive", "invalid"),
        ("arishta_naive", "missing_capability"),
    ]
    assert [row["definition"]["candidate_id"] for row in career] == [
        "strong_in_10_Sun",
        "strong_in_10_Moon",
        "strong_in_10_Mars",
        "rajayoga_naive",
    ]
    assert list(yoga[0]) == [
        "compatibility_evidence", "compatibility_houses", "condition_result",
        "condition_result_kind", "definition_disposition", "definition_issues",
        "name", "rule_match", "source",
    ]
    assert list(career[0]) == [
        "adjusted_score", "compatibility_evidence", "contribution", "definition", "fact",
        "rule_match", "trace_lineage",
    ]
    assert hashlib.sha256(first_yoga_bytes).hexdigest() == (
        "866dbee7630cd426503b0cce33af9f97eb0363577687e2f937ba4ca1a9a1cef6"
    )
    assert hashlib.sha256(first_career_bytes).hexdigest() == (
        "bca793f779ecf6fec0cb9d8e2e33736e01d7cf6ff45303e05f8b9ed0c9950f22"
    )

    yoga[0]["rule_match"]["status"] = "changed"
    career[0]["definition"]["candidate_id"] = "changed"
    run_rules_and_trace(_astro(), second_dir)
    assert (second_dir / "rule_traces.json").read_bytes() == first_yoga_bytes
    assert (second_dir / "career_rule_traces.json").read_bytes() == first_career_bytes
    assert {
        path: path.read_bytes() if path.exists() else None for path in fixed_paths
    } == before


def test_artifact_failure_projection_does_not_leak_raw_exception(monkeypatch, tmp_path):
    monkeypatch.setattr(
        typed_rule_evaluation,
        "prepare_legacy_yoga_state",
        lambda *_a, **_k: (_ for _ in ()).throw(
            RuntimeError("private path C:/secret/owner.txt")
        ),
    )
    yoga, _career = run_rules_and_trace(_astro(), tmp_path)
    payload = json.dumps(yoga, ensure_ascii=False)
    assert [row["rule_match"]["status"] for row in yoga] == [
        "error", "invalid", "error"
    ]
    assert "private path" not in payload
    assert "secret" not in payload
    assert "RuntimeError" not in payload
