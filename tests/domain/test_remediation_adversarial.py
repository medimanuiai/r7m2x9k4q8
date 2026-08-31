from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from systems.Parasara.engine.capability import CapabilityInspection, CapabilityReadiness
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.domain import (
    DASHA_TIMELINE_SCHEMA_VERSION,
    TRANSIT_SUMMARY_SCHEMA_VERSION,
    DashaPeriod,
    DashaTimeline,
    DomainIssue,
    DomainIssueSeverity,
    TimingOutputStatus,
    TransitSummaryFactory,
    TransitSummary,
)
from systems.Parasara.engine.enrichments.yoga_engine import (
    evaluate_yoga_diagnostics,
)
from systems.Parasara.engine.inference import InferenceStatus
from systems.Parasara.engine.interpreters.career import build_career_prediction
from systems.Parasara.engine.normalizer import chart_to_astrostate


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "systems" / "Parasara" / "fixtures" / "golden_chart_01.json"


def test_career_compatibility_cannot_override_its_authoritative_projection(career_source):
    prediction = career_source[3].prediction
    forged = replace(prediction.career_compatibility, base_score=0.0)
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(prediction, career_compatibility=forged, logical_digest="")


def test_yoga_compatibility_and_evidence_cannot_contradict_rule_source():
    astro = chart_to_astrostate(SuryaAdapter.load(FIXTURE))
    diagnostic = evaluate_yoga_diagnostics(astro)[0]
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(diagnostic, matched=not diagnostic.matched, logical_digest="")
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(diagnostic, evidence_summary={"forged": True}, logical_digest="")


def test_domain_component_and_narrative_require_exact_source_lineage(career_source):
    prediction = career_source[3].prediction
    component = prediction.components[0]
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(
            prediction,
            components=(replace(component, contribution_ids=()), *prediction.components[1:]),
            logical_digest="",
        )
    narrative = prediction.narrative_sections[0]
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(
            prediction,
            narrative_sections=(replace(narrative, source_rule_ids=("forged.rule",)),),
            logical_digest="",
        )
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(
            prediction,
            narrative_sections=(replace(narrative, source_trace_ids=("forged.trace",)),),
            logical_digest="",
        )


def test_caller_forged_insufficient_inference_cannot_mint_authority(career_source):
    _, batch, inference, _ = career_source
    with pytest.raises(ValueError, match="begins with AstroState"):
        build_career_prediction(
            batch,
            replace(
                inference,
                status=InferenceStatus.INSUFFICIENT_EVIDENCE,
                raw_score=0.0,
                normalized_score=0.5,
                confidence=0.0,
                agreement=0.0,
                positive_contributions=(),
                negative_contributions=(),
                neutral_contributions=(),
                mixed_contributions=(),
                components=(),
                conflicts=(),
                explanation_factors=(),
            ),
        )


def _period(
    period_id: str,
    start: str,
    end: str,
    seconds: int,
    *,
    level: str,
    parent: str | None,
    order: int,
) -> DashaPeriod:
    return DashaPeriod(
        period_id=period_id,
        lord="Sun",
        start_utc=start,
        end_utc=end,
        duration_seconds=seconds,
        level=level,
        parent_id=parent,
        order=order,
    )


def test_dasha_rejects_overlap_and_active_period_outside_reference_instant():
    maha = _period(
        "dasha.maha.sun", "2020-01-01T00:00:00+00:00",
        "2020-01-11T00:00:00+00:00", 864000,
        level="mahadasha", parent=None, order=0,
    )
    antar_one = _period(
        "dasha.antar.sun", "2020-01-01T00:00:00+00:00",
        "2020-01-07T00:00:00+00:00", 518400,
        level="antardasha", parent=maha.period_id, order=1,
    )
    antar_two = _period(
        "dasha.antar.moon", "2020-01-06T00:00:00+00:00",
        "2020-01-10T00:00:00+00:00", 345600,
        level="antardasha", parent=maha.period_id, order=2,
    )
    with pytest.raises(ValueError, match="cannot overlap"):
        DashaTimeline(
            dasha_timeline_schema_version=DASHA_TIMELINE_SCHEMA_VERSION,
            status=TimingOutputStatus.AVAILABLE,
            system="vimshottari",
            reference_instant="2020-01-06T12:00:00+00:00",
            periods=(maha, antar_one, antar_two),
            active_mahadasha_id=maha.period_id,
            active_antardasha_id=antar_one.period_id,
            active_pratyantardasha_id=None,
            calculation_version="1.0.0",
            issues=(),
            trace_id="dasha.overlap",
        )
    valid = DashaTimeline(
        dasha_timeline_schema_version=DASHA_TIMELINE_SCHEMA_VERSION,
        status=TimingOutputStatus.AVAILABLE,
        system="vimshottari",
        reference_instant="2020-01-02T00:00:00+00:00",
        periods=(maha, antar_one),
        active_mahadasha_id=maha.period_id,
        active_antardasha_id=antar_one.period_id,
        active_pratyantardasha_id=None,
        calculation_version="1.0.0",
        issues=(),
        trace_id="dasha.valid",
    )
    with pytest.raises(ValueError, match="does not contain"):
        replace(valid, reference_instant="2020-01-09T00:00:00+00:00", logical_digest="")


def test_transit_ready_empty_cannot_be_manufactured_without_a_real_producer():
    with pytest.raises(ValueError, match="no authoritative producer"):
        TransitSummaryFactory.producer_evidence(
            capability=CapabilityInspection(
                capability_id="transits.current",
                expected_version="1.0.0",
                observed_version="1.0.0",
                readiness=CapabilityReadiness.READY_EMPTY,
                source_kind="transit_producer",
                content_empty=True,
                issues=(),
            ),
            positions=(),
            producer_version="1.0.0",
            producer_schema_version="1.0.0",
            trace_id="transit.producer.ready-empty",
        )


@pytest.mark.parametrize(
    "message",
    (
        "Internal failure at /home/service/app.py.",
        "Internal failure in systems/Parasara/engine/domain/models.py.",
        "Internal failure at C:/work/repository/file.py.",
    ),
)
def test_domain_issue_rejects_platform_and_repository_paths(message):
    with pytest.raises(ValueError, match="filesystem paths"):
        DomainIssue(
            issue_id="issue.safe-boundary",
            code="INTERPRETER_FAILURE",
            severity=DomainIssueSeverity.ERROR,
            phase="test",
            message=message,
            recoverable=False,
        )


def test_snapshot_tool_delegates_bytes_to_output_assembler():
    source = (
        ROOT / "systems" / "Parasara" / "tools" / "generate_snapshot.py"
    ).read_text(encoding="utf-8")
    assert "import json" not in source
    assert "json.dumps" not in source
    assert "snapshot_json_bytes" in source


def test_career_builder_does_not_reaggregate_public_scores():
    source = (
        ROOT / "systems" / "Parasara" / "engine" / "interpreters" / "career.py"
    ).read_text(encoding="utf-8")
    body = source[source.index("def build_career_prediction("):source.index("def interpret_career_domain(")]
    assert "sum(" not in body
    assert "baseline.final_contribution" not in body
