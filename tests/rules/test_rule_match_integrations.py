"""Prompt-02 Yoga and Career integration coverage for universal RuleMatch."""

from __future__ import annotations

from pathlib import Path

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.enrichments.yoga_engine import (
    evaluate_yoga_batch,
    load_yoga_rule_source,
    prepare_legacy_yoga_state,
    project_yoga_compatibility,
)
from systems.Parasara.engine.interpreters.career import (
    evaluate_career_batch,
    prepare_career_facts,
    project_career_compatibility,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext
from systems.Parasara.engine.rules.rule_match import RuleMatch, RuleMatchStatus


REPO_ROOT = Path(__file__).resolve().parents[2]
SURYA_TEST = REPO_ROOT / "systems" / "Parasara" / "fixtures" / "surya_test_chart.json"


def _astro():
    return chart_to_astrostate(SuryaAdapter.load(str(SURYA_TEST)))


def test_yoga_wrapper_contains_one_universal_match_and_preserves_public_projection():
    astro = _astro()
    source = load_yoga_rule_source()
    prepared = prepare_legacy_yoga_state(astro, source)
    batch = evaluate_yoga_batch(
        prepared.outcome.state,
        PredicateEvaluationContext(),
        source,
        compatibility_graph=prepared.compatibility_graph,
    )
    assert all(isinstance(item.rule_match, RuleMatch) for item in batch.records)
    assert len(batch.rule_matches) == len(batch.records) == 3
    assert {item.system for item in batch.rule_matches} == {"parashara"}
    assert {item.rule_family for item in batch.rule_matches} == {"yoga"}
    assert any(item.status is RuleMatchStatus.INVALID for item in batch.rule_matches)
    rows = project_yoga_compatibility(batch)
    assert [row["yoga_id"] for row in rows] == [item.yoga_id for item in batch.records]
    assert [row["trace_id"] for row in rows] == [item.rule_match.trace_id for item in batch.records]


def test_career_wrapper_contains_one_universal_match_without_absorbing_scores():
    batch = evaluate_career_batch(prepare_career_facts(_astro()))
    assert all(isinstance(item.rule_match, RuleMatch) for item in batch.candidates)
    assert len(batch.rule_matches) == len(batch.candidates)
    assert all(item.domains == ("career",) for item in batch.rule_matches)
    assert all(item.context == "natal" for item in batch.rule_matches)
    for item in batch.rule_matches:
        logical_keys = set(item.metadata) | set(item.evidence)
        assert not logical_keys & {
            "adjusted_score", "contribution", "score", "confidence", "final_contribution"
        }
    public = project_career_compatibility(batch)
    assert set(public) == {
        "summary", "score", "confidence", "components", "indicators",
        "evidence", "scoring", "trace_id",
    }
