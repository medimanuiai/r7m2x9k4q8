from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import math

import pytest

from systems.Parasara.engine.capability import CapabilityInspection, CapabilityReadiness
from systems.Parasara.engine.domain import (
    DASHA_TIMELINE_SCHEMA_VERSION,
    TRANSIT_SUMMARY_SCHEMA_VERSION,
    DashaPeriod,
    DashaTimeline,
    DashaTimelineFactory,
    DomainBuildProduced,
    DomainId,
    DomainIssue,
    DomainIssueSeverity,
    DomainPredictionFactory,
    DomainStatus,
    TimingOutputStatus,
    TransitPosition,
    TransitProducerEvidence,
    TransitRelationship,
    TransitSummary,
    TransitSummaryFactory,
    dasha_timeline_from_logical_json,
    prompt05_model_logical_json_bytes,
    transit_summary_from_logical_json,
)
from systems.Parasara.engine.domain.models import domain_prediction_from_logical_json
from systems.Parasara.engine.rules.canonical import CanonicalValueError
from systems.Parasara.engine.inference.models import EvidenceReference


def issue(code: str = "CAPABILITY_PARTIAL") -> DomainIssue:
    details = {"nested": ["one", {"two": 2}]}
    value = DomainIssue(
        issue_id=f"test.issue.{code.lower()}",
        code=code,
        severity=DomainIssueSeverity.WARNING,
        phase="test",
        message="A deterministic test issue.",
        recoverable=True,
        details=details,
    )
    details["nested"].append("mutated")
    return value


def test_domain_ids_and_statuses_are_closed():
    assert tuple(item.value for item in DomainId) == (
        "career", "wealth", "marriage", "children", "health", "safety",
    )
    assert tuple(item.value for item in DomainStatus) == (
        "evaluated", "partial", "insufficient_evidence", "unavailable",
        "not_supported", "not_requested", "failed",
    )
    with pytest.raises(ValueError):
        DomainId("education")


def test_nested_values_are_defensively_owned_and_deeply_immutable():
    value = issue()
    assert value.details["nested"] == ("one", value.details["nested"][1])
    with pytest.raises(TypeError):
        value.details["new"] = "no"
    with pytest.raises(FrozenInstanceError):
        value.message = "changed"


def test_career_prediction_serialization_is_one_way_and_replace_revalidates(career_source):
    _, _, _, outcome = career_source
    assert isinstance(outcome, DomainBuildProduced)
    prediction = outcome.prediction
    payload = prompt05_model_logical_json_bytes(prediction)
    with pytest.raises(CanonicalValueError, match="one-way presentation"):
        domain_prediction_from_logical_json(
            payload,
            source_inference_result=prediction.source_inference_result,
            source_inference_compatibility=prediction.source_inference_compatibility,
            source_evaluation_batch=prediction.source_evaluation_batch,
        )
    assert len(prediction.logical_digest) == 64
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(prediction, summary="Changed after digest construction")


def test_caller_supplied_digest_and_duplicate_model_ids_are_rejected(career_source):
    _, _, _, outcome = career_source
    prediction = outcome.prediction
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(prediction, logical_digest="0" * 64)
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(
            prediction,
            components=(prediction.components[0], prediction.components[0]),
            logical_digest="",
        )


@pytest.mark.parametrize(
    ("status", "code"),
    (
        (DomainStatus.UNAVAILABLE, "CAPABILITY_UNAVAILABLE"),
        (DomainStatus.NOT_SUPPORTED, "DOMAIN_NOT_SUPPORTED"),
        (DomainStatus.FAILED, "INTERPRETER_FAILURE"),
    ),
)
def test_non_evaluated_domain_statuses_are_typed(status, code):
    prediction = DomainPredictionFactory.status_only(
        domain=DomainId.WEALTH,
        status=status,
        engine_version="0.1.0",
        interpreter_version="1.0.0",
        narrative_version="1.0.0",
        issues=(issue(code),),
    )
    assert prediction.status is status
    assert prediction.score is prediction.confidence is prediction.agreement is None
    assert prediction.components == prediction.indicators == ()


def test_not_requested_is_distinct_and_does_not_claim_computation():
    prediction = DomainPredictionFactory.status_only(
        domain=DomainId.HEALTH,
        status=DomainStatus.NOT_REQUESTED,
        engine_version="0.1.0",
        interpreter_version="1.0.0",
        narrative_version="1.0.0",
    )
    assert prediction.status is DomainStatus.NOT_REQUESTED
    assert prediction.issues == ()
    assert prediction.source_inference_trace_id is None


def test_unavailable_status_cannot_fabricate_neutral_values():
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(
            DomainPredictionFactory.status_only(
                domain=DomainId.SAFETY,
                status=DomainStatus.UNAVAILABLE,
                engine_version="0.1.0",
                interpreter_version="1.0.0",
                narrative_version="1.0.0",
                issues=(issue("CAPABILITY_UNAVAILABLE"),),
            ),
            score=0.5,
            logical_digest="",
        )


def periods() -> tuple[DashaPeriod, ...]:
    return (
        DashaPeriod(
            period_id="dasha.maha.sun", lord="Sun",
            start_utc="2020-01-01T00:00:00+00:00",
            end_utc="2020-01-11T00:00:00+00:00",
            duration_seconds=864000, level="mahadasha", parent_id=None, order=0,
        ),
        DashaPeriod(
            period_id="dasha.antar.moon", lord="Moon",
            start_utc="2020-01-01T00:00:00+00:00",
            end_utc="2020-01-06T00:00:00+00:00",
            duration_seconds=432000, level="antardasha",
            parent_id="dasha.maha.sun", order=1,
        ),
        DashaPeriod(
            period_id="dasha.prat.mars", lord="Mars",
            start_utc="2020-01-01T00:00:00+00:00",
            end_utc="2020-01-02T00:00:00+00:00",
            duration_seconds=86400, level="pratyantardasha",
            parent_id="dasha.antar.moon", order=2,
        ),
    )


def test_dasha_available_round_trip_and_reference_validation():
    value = DashaTimelineFactory.from_calculator_output(
        status=TimingOutputStatus.AVAILABLE,
        system="vimshottari",
        reference_instant="2020-01-01T12:00:00+00:00",
        periods=periods(),
        active_mahadasha_id="dasha.maha.sun",
        active_antardasha_id="dasha.antar.moon",
        active_pratyantardasha_id="dasha.prat.mars",
        calculation_version="1.0.0",
        trace_id="dasha.test",
    )
    assert dasha_timeline_from_logical_json(
        prompt05_model_logical_json_bytes(value)
    ) == value
    with pytest.raises(ValueError, match="does not resolve"):
        replace(value, active_antardasha_id="dasha.missing", logical_digest="")


@pytest.mark.parametrize("status", [TimingOutputStatus.NOT_REQUESTED, TimingOutputStatus.FAILED])
def test_dasha_nonavailable_statuses_are_not_ready_empty(status):
    issues = () if status is TimingOutputStatus.NOT_REQUESTED else (issue("INTERPRETER_FAILURE"),)
    value = DashaTimeline(
        dasha_timeline_schema_version=DASHA_TIMELINE_SCHEMA_VERSION,
        status=status,
        system="vimshottari",
        reference_instant=None,
        periods=(),
        active_mahadasha_id=None,
        active_antardasha_id=None,
        active_pratyantardasha_id=None,
        calculation_version=None,
        issues=issues,
        trace_id=f"dasha.{status.value}",
    )
    assert value.periods == ()
    assert value.status is status


def test_transit_available_construction_is_closed_without_a_real_producer():
    position = TransitPosition(
        body_id="Sun", longitude_degrees=-0.0, sign_id="Aries",
        source_fact_id="transit.fact.sun", order=0,
    )
    assert position.longitude_degrees == 0.0
    assert math.copysign(1.0, position.longitude_degrees) == 1.0
    relationship = TransitRelationship(
        relationship_id="transit.relationship.sun.asc",
        source_body_id="Sun",
        natal_target_id="natal.ascendant",
        relationship_type="conjunction",
        source_fact_ids=("transit.fact.sun",),
        order=0,
    )
    with pytest.raises(ValueError, match="no authoritative producer"):
        TransitSummaryFactory.producer_evidence(
        capability=CapabilityInspection(
            capability_id="transits.current",
            expected_version="1.0.0",
            observed_version="1.0.0",
            readiness=CapabilityReadiness.READY,
            source_kind="transit_producer",
            content_empty=False,
            issues=(),
        ),
        positions=(position,),
        natal_target_references=(EvidenceReference(
            evidence_id="evidence.natal.ascendant",
            source_type="astrostate_fact",
            source_id="natal.ascendant",
            trace_id="astrostate.natal.ascendant",
            correlation_key="natal.ascendant",
            order=0,
        ),),
        producer_version="1.0.0",
        producer_schema_version="1.0.0",
        trace_id="transit.producer.test",
    )
    assert relationship.source_fact_ids == ("transit.fact.sun",)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_transit_numbers_are_rejected(bad):
    with pytest.raises(TypeError, match="finite"):
        TransitPosition(
            body_id="Sun", longitude_degrees=bad, sign_id="Aries",
            source_fact_id="transit.fact.sun", order=0,
        )


def test_unavailable_timing_models_are_distinct_from_available_empty():
    dasha = DashaTimelineFactory.unavailable()
    transit = TransitSummaryFactory.unavailable()
    assert dasha.status is transit.status is TimingOutputStatus.UNAVAILABLE
    assert dasha.issues and transit.issues
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
        trace_id="transit.producer.empty",
    )
    assert transit.positions == ()
