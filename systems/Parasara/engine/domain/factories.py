"""Controlled Prompt-05 mappings from authoritative typed source values."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import re
from typing import Any

from systems.Parasara.engine.domain.models import (
    DASHA_TIMELINE_SCHEMA_VERSION,
    DOMAIN_PREDICTION_SCHEMA_VERSION,
    TRANSIT_SUMMARY_SCHEMA_VERSION,
    YOGA_DIAGNOSTIC_SCHEMA_VERSION,
    DashaPeriod,
    DashaTimeline,
    CareerCompatibilityProjection,
    DomainBuildRejected,
    DomainComponent,
    DomainId,
    DomainIndicator,
    DomainIssue,
    DomainIssueSeverity,
    DomainPrediction,
    DomainStatus,
    DomainTimingReference,
    NarrativeSection,
    NarrativeSectionType,
    TimingOutputStatus,
    TransitProducerEvidence,
    TransitPosition,
    TransitRelationship,
    TransitSummary,
    YogaDiagnostic,
    YogaCompatibilityProjection,
    _DOMAIN_PREDICTION_FACTORY_TOKEN,
    _YOGA_DIAGNOSTIC_FACTORY_TOKEN,
    _build_yoga_compatibility_projection,
)
from systems.Parasara.engine.capability import CapabilityInspection
from systems.Parasara.engine.inference.models import (
    EvidenceReference,
    InferenceCompatibilityProjection,
    InferenceResult,
    InferenceStatus,
)
from systems.Parasara.engine.rules.canonical import canonical_json_bytes, canonical_json_data
from systems.Parasara.engine.rules.rule_match import RuleMatch, RuleMatchStatus


_UNSAFE_CODE = re.compile(r"[^A-Z0-9_]+")
_DOMAIN_INFERENCE_FACTORY_TOKEN = object()
_CAREER_DOMAIN_FACTORY_TOKEN = object()


def _stable_id(prefix: str, *values: Any) -> str:
    digest = hashlib.sha256(canonical_json_bytes((prefix, *values))).hexdigest()[:24]
    return f"{prefix}.{digest}"


def _code(value: str, fallback: str) -> str:
    candidate = _UNSAFE_CODE.sub("_", value.upper()).strip("_")
    if not candidate or not candidate[0].isalpha() or len(candidate) < 2:
        return fallback
    return candidate[:128]


def _inference_issues(result: InferenceResult) -> tuple[DomainIssue, ...]:
    issues = []
    for index, error in enumerate(result.errors):
        issues.append(DomainIssue(
            issue_id=_stable_id("domain.issue", result.trace_id, index, error.code),
            code=_code(error.code, "INTERPRETER_FAILURE"),
            severity=(
                DomainIssueSeverity.WARNING
                if error.recoverable
                else DomainIssueSeverity.ERROR
            ),
            phase=error.phase,
            message=error.message,
            recoverable=error.recoverable,
            source_rule_id=error.source_rule_id,
            source_trace_id=error.source_trace_id or result.trace_id,
            details=error.details,
        ))
    if result.status is InferenceStatus.PARTIAL and not issues:
        issues.append(DomainIssue(
            issue_id=_stable_id("domain.issue", result.trace_id, "partial"),
            code="CAPABILITY_PARTIAL",
            severity=DomainIssueSeverity.WARNING,
            phase="inference",
            message="The domain evaluation completed with explicitly incomplete data.",
            recoverable=True,
            source_trace_id=result.trace_id,
            details={
                "missing_required": result.data_completeness.missing_required,
                "missing_optional": result.data_completeness.missing_optional,
            },
        ))
    if result.status is InferenceStatus.INSUFFICIENT_EVIDENCE:
        issues.append(DomainIssue(
            issue_id=_stable_id("domain.issue", result.trace_id, "insufficient_evidence"),
            code="INSUFFICIENT_EVIDENCE",
            severity=DomainIssueSeverity.INFO,
            phase="inference",
            message="No score-bearing evidence was available for this domain evaluation.",
            recoverable=True,
            source_trace_id=result.trace_id,
            details={"inference_status": result.status.value},
        ))
    if result.status is InferenceStatus.FAILED and not issues:
        issues.append(DomainIssue(
            issue_id=_stable_id("domain.issue", result.trace_id, "failed"),
            code="INTERPRETER_FAILURE",
            severity=DomainIssueSeverity.ERROR,
            phase="inference",
            message="The authoritative inference result failed validation.",
            recoverable=False,
            source_trace_id=result.trace_id,
            details={},
        ))
    return tuple(issues)


class DomainPredictionFactory:
    """Validate presentation projections against one immutable InferenceResult."""

    @staticmethod
    def _from_inference(
        result: InferenceResult,
        *,
        domain: DomainId,
        summary: str | None,
        components: Sequence[DomainComponent] = (),
        indicators: Sequence[DomainIndicator] = (),
        narrative_sections: Sequence[NarrativeSection] = (),
        timing: DomainTimingReference | None = None,
        engine_version: str,
        interpreter_version: str,
        narrative_version: str,
        additional_issues: Sequence[DomainIssue] = (),
    ) -> DomainPrediction:
        if domain is DomainId.CAREER:
            raise ValueError(
                "Career DomainPrediction requires its interpreter-owned producer boundary"
            )
        return DomainPredictionFactory._from_inference_internal(
            result,
            domain=domain,
            summary=summary,
            components=components,
            indicators=indicators,
            narrative_sections=narrative_sections,
            timing=timing,
            engine_version=engine_version,
            interpreter_version=interpreter_version,
            narrative_version=narrative_version,
            additional_issues=additional_issues,
            career_compatibility=None,
            source_inference_compatibility=None,
            source_evaluation_batch=None,
            _factory_token=_DOMAIN_INFERENCE_FACTORY_TOKEN,
        )

    @staticmethod
    def _from_career_evaluation(
        evaluation: Any,
        *,
        domain: DomainId,
        summary: str | None,
        components: Sequence[DomainComponent] = (),
        indicators: Sequence[DomainIndicator] = (),
        narrative_sections: Sequence[NarrativeSection] = (),
        timing: DomainTimingReference | None = None,
        engine_version: str,
        interpreter_version: str,
        narrative_version: str,
        additional_issues: Sequence[DomainIssue] = (),
    ) -> DomainPrediction:
        if (
            evaluation.__class__.__module__
            != "systems.Parasara.engine.interpreters.career"
            or evaluation.__class__.__name__ != "_CareerInferenceEvaluation"
        ):
            raise TypeError("evaluation must be the private Career same-run value")
        if domain is not DomainId.CAREER:
            raise ValueError("Career producer boundary accepts only Career")
        return DomainPredictionFactory._from_inference_internal(
            evaluation.inference_result,
            domain=domain,
            summary=summary,
            components=components,
            indicators=indicators,
            narrative_sections=narrative_sections,
            timing=timing,
            engine_version=engine_version,
            interpreter_version=interpreter_version,
            narrative_version=narrative_version,
            additional_issues=additional_issues,
            career_compatibility=evaluation.career_compatibility,
            source_inference_compatibility=evaluation.compatibility_projection,
            source_evaluation_batch=evaluation.batch,
            source_authority=evaluation,
            _factory_token=_DOMAIN_INFERENCE_FACTORY_TOKEN,
        )

    @staticmethod
    def _from_inference_internal(
        result: InferenceResult,
        *,
        domain: DomainId,
        summary: str | None,
        components: Sequence[DomainComponent] = (),
        indicators: Sequence[DomainIndicator] = (),
        narrative_sections: Sequence[NarrativeSection] = (),
        timing: DomainTimingReference | None = None,
        engine_version: str,
        interpreter_version: str,
        narrative_version: str,
        additional_issues: Sequence[DomainIssue] = (),
        career_compatibility: CareerCompatibilityProjection | None = None,
        source_inference_compatibility: InferenceCompatibilityProjection | None = None,
        source_evaluation_batch: Any | None = None,
        source_authority: Any | None = None,
        _factory_token: object | None = None,
    ) -> DomainPrediction:
        if _factory_token is not _DOMAIN_INFERENCE_FACTORY_TOKEN:
            raise ValueError("DomainPrediction requires the validated producer factory")
        if not isinstance(result, InferenceResult):
            raise TypeError("result must be InferenceResult")
        if not isinstance(domain, DomainId):
            raise TypeError("domain must be DomainId")
        if result.domain != domain.value:
            raise ValueError("InferenceResult domain mismatch")
        if not isinstance(components, Sequence) or isinstance(components, (str, bytes)):
            raise TypeError("components must be a sequence")
        if not isinstance(indicators, Sequence) or isinstance(indicators, (str, bytes)):
            raise TypeError("indicators must be a sequence")
        if not isinstance(narrative_sections, Sequence) or isinstance(narrative_sections, (str, bytes)):
            raise TypeError("narrative_sections must be a sequence")
        if not isinstance(additional_issues, Sequence) or isinstance(additional_issues, (str, bytes)):
            raise TypeError("additional_issues must be a sequence")
        status = {
            InferenceStatus.EVALUATED: DomainStatus.EVALUATED,
            InferenceStatus.PARTIAL: DomainStatus.PARTIAL,
            InferenceStatus.INSUFFICIENT_EVIDENCE: DomainStatus.INSUFFICIENT_EVIDENCE,
            InferenceStatus.FAILED: DomainStatus.FAILED,
        }[result.status]
        issues = (*_inference_issues(result), *tuple(additional_issues))
        trace_id = _stable_id(
            "domain",
            domain.value,
            result.trace_id,
            interpreter_version,
            narrative_version,
        )
        if status is DomainStatus.FAILED:
            return DomainPrediction(
                domain_prediction_schema_version=DOMAIN_PREDICTION_SCHEMA_VERSION,
                system=result.system,
                domain=domain,
                status=status,
                summary=None,
                score=None,
                confidence=None,
                agreement=None,
                components=(),
                indicators=(),
                conflicts=(),
                timing=None,
                narrative_sections=(),
                data_completeness=None,
                missing_data=(),
                issues=tuple(issues),
                source_inference_trace_id=result.trace_id,
                trace_id=trace_id,
                engine_version=engine_version,
                rule_set_version=result.rule_set_version,
                inference_version=result.inference_version,
                interpreter_version=interpreter_version,
                narrative_version=narrative_version,
                career_compatibility=None,
                source_inference_result=result,
                source_inference_compatibility=None,
                source_evaluation_batch=None,
                source_authority=None,
                _factory_token=_DOMAIN_PREDICTION_FACTORY_TOKEN,
            )
        missing = tuple(sorted({
            *result.data_completeness.missing_required,
            *result.data_completeness.missing_optional,
        }))
        return DomainPrediction(
            domain_prediction_schema_version=DOMAIN_PREDICTION_SCHEMA_VERSION,
            system=result.system,
            domain=domain,
            status=status,
            summary=summary,
            score=result.normalized_score,
            confidence=result.confidence,
            agreement=result.agreement,
            components=tuple(sorted(
                components, key=lambda item: (item.order, item.component_id)
            )),
            indicators=tuple(sorted(
                indicators,
                key=lambda item: (
                    item.order, -item.priority, item.source_rule_id,
                    item.source_rule_version, item.indicator_id,
                ),
            )),
            conflicts=result.conflicts,
            timing=timing,
            narrative_sections=tuple(sorted(
                narrative_sections,
                key=lambda item: (
                    item.order,
                    tuple(NarrativeSectionType).index(item.section_type),
                    item.section_id,
                ),
            )),
            data_completeness=result.data_completeness,
            missing_data=missing,
            issues=tuple(issues),
            source_inference_trace_id=result.trace_id,
            trace_id=trace_id,
            engine_version=engine_version,
            rule_set_version=result.rule_set_version,
            inference_version=result.inference_version,
            interpreter_version=interpreter_version,
            narrative_version=narrative_version,
            career_compatibility=career_compatibility,
            source_inference_result=result,
            source_inference_compatibility=source_inference_compatibility,
            source_evaluation_batch=source_evaluation_batch,
            source_authority=source_authority,
            _factory_token=_DOMAIN_PREDICTION_FACTORY_TOKEN,
        )

    @staticmethod
    def missing_inference(
        *,
        domain: DomainId,
        phase: str = "domain_mapping",
    ) -> DomainBuildRejected:
        """Return the closed typed rejection for an unexpectedly absent result."""

        if not isinstance(domain, DomainId):
            raise TypeError("domain must be DomainId")
        trace_id = _stable_id("domain.reject", domain.value, "missing_inference")
        return DomainBuildRejected(
            domain=domain,
            issues=(DomainIssue(
                issue_id=_stable_id("domain.issue", domain.value, "missing_inference"),
                code="MISSING_INFERENCE_RESULT",
                severity=DomainIssueSeverity.FATAL,
                phase=phase,
                message="The authoritative inference result was not supplied.",
                recoverable=False,
                details={"domain": domain.value},
            ),),
            trace_id=trace_id,
        )

    @staticmethod
    def status_only(
        *,
        domain: DomainId,
        status: DomainStatus,
        engine_version: str,
        interpreter_version: str,
        narrative_version: str,
        issues: Sequence[DomainIssue] = (),
        summary: str | None = None,
        rule_set_version: str | None = None,
    ) -> DomainPrediction:
        if status in {
            DomainStatus.EVALUATED,
            DomainStatus.PARTIAL,
            DomainStatus.INSUFFICIENT_EVIDENCE,
        }:
            raise ValueError("evaluated statuses require from_inference")
        trace_id = _stable_id(
            "domain", domain.value, status.value, engine_version, interpreter_version
        )
        return DomainPrediction(
            domain_prediction_schema_version=DOMAIN_PREDICTION_SCHEMA_VERSION,
            system="parashara",
            domain=domain,
            status=status,
            summary=summary,
            score=None,
            confidence=None,
            agreement=None,
            components=(),
            indicators=(),
            conflicts=(),
            timing=None,
            narrative_sections=(),
            data_completeness=None,
            missing_data=(),
            issues=tuple(issues),
            source_inference_trace_id=None,
            trace_id=trace_id,
            engine_version=engine_version,
            rule_set_version=rule_set_version,
            inference_version=None,
            interpreter_version=interpreter_version,
            narrative_version=narrative_version,
            career_compatibility=None,
            source_inference_compatibility=None,
            source_evaluation_batch=None,
            source_authority=None,
            _factory_token=_DOMAIN_PREDICTION_FACTORY_TOKEN,
        )


class YogaDiagnosticFactory:
    @staticmethod
    def _from_evaluation_record(
        record: Any,
        *,
        strength: float | None = None,
    ) -> YogaDiagnostic:
        if (
            record.__class__.__module__
            != "systems.Parasara.engine.enrichments.yoga_engine"
            or record.__class__.__name__ != "YogaEvaluationRecord"
        ):
            raise TypeError("record must be YogaEvaluationRecord")
        rule_match = record.rule_match
        if not isinstance(rule_match, RuleMatch):
            raise TypeError("record.rule_match must be RuleMatch")
        try:
            domains = tuple(
                sorted(
                    (DomainId(item) for item in rule_match.domains),
                    key=lambda item: tuple(DomainId).index(item),
                )
            )
        except ValueError as exc:
            raise ValueError("Yoga RuleMatch contains an unauthorized domain") from exc
        evidence = record.compatibility_evidence
        houses = record.compatibility_houses
        if (
            record.condition_result is not None
            and record.condition_result.matched is not rule_match.matched
        ):
            raise ValueError("Yoga condition truth disagrees with its RuleMatch")
        compatibility = _build_yoga_compatibility_projection(
            name=record.name,
            source_order=record.source_index,
            evidence=evidence,
            houses=houses,
        )
        return YogaDiagnostic(
            yoga_diagnostic_schema_version=YOGA_DIAGNOSTIC_SCHEMA_VERSION,
            yoga_id=rule_match.rule_id,
            name=record.name,
            category=rule_match.category,
            matched=rule_match.matched,
            status=rule_match.status,
            strength=strength,
            domains=domains,
            source_rule_match=rule_match,
            evidence_summary=rule_match.evidence,
            compatibility=compatibility,
            trace_id=rule_match.trace_id,
            rule_version=rule_match.rule_version,
            rule_set_version=rule_match.rule_set_version,
            source_evaluation_record=record,
            _factory_token=_YOGA_DIAGNOSTIC_FACTORY_TOKEN,
        )


def _timing_issue(kind: str, status: TimingOutputStatus) -> DomainIssue:
    code = {
        TimingOutputStatus.UNAVAILABLE: "CAPABILITY_UNAVAILABLE",
        TimingOutputStatus.PARTIAL: "CAPABILITY_PARTIAL",
        TimingOutputStatus.NOT_REQUESTED: "DOMAIN_NOT_REQUESTED",
        TimingOutputStatus.FAILED: "INTERPRETER_FAILURE",
        TimingOutputStatus.AVAILABLE: "CAPABILITY_PARTIAL",
    }[status]
    return DomainIssue(
        issue_id=_stable_id("domain.issue", kind, status.value),
        code=code,
        severity=(
            DomainIssueSeverity.ERROR
            if status is TimingOutputStatus.FAILED
            else DomainIssueSeverity.INFO
        ),
        phase="timing_output",
        message={
            TimingOutputStatus.UNAVAILABLE: f"The integrated {kind} producer is unavailable.",
            TimingOutputStatus.NOT_REQUESTED: f"The {kind} output was not requested.",
            TimingOutputStatus.FAILED: f"The {kind} output producer failed.",
            TimingOutputStatus.PARTIAL: f"The {kind} output is partial.",
            TimingOutputStatus.AVAILABLE: f"The {kind} output is available.",
        }[status],
        recoverable=status is not TimingOutputStatus.FAILED,
        capability_id=f"{kind}.current",
        details={"status": status.value},
    )


class DashaTimelineFactory:
    @staticmethod
    def unavailable() -> DashaTimeline:
        return DashaTimeline(
            dasha_timeline_schema_version=DASHA_TIMELINE_SCHEMA_VERSION,
            status=TimingOutputStatus.UNAVAILABLE,
            system="vimshottari",
            reference_instant=None,
            periods=(),
            active_mahadasha_id=None,
            active_antardasha_id=None,
            active_pratyantardasha_id=None,
            calculation_version=None,
            issues=(_timing_issue("dasha", TimingOutputStatus.UNAVAILABLE),),
            trace_id="dasha.unavailable",
        )

    @staticmethod
    def from_calculator_output(
        *,
        status: TimingOutputStatus,
        system: str,
        reference_instant: str,
        periods: Sequence[DashaPeriod],
        calculation_version: str,
        active_mahadasha_id: str | None = None,
        active_antardasha_id: str | None = None,
        active_pratyantardasha_id: str | None = None,
        issues: Sequence[DomainIssue] = (),
        trace_id: str,
    ) -> DashaTimeline:
        if status not in (TimingOutputStatus.AVAILABLE, TimingOutputStatus.PARTIAL):
            raise ValueError("calculator output factory accepts available/partial only")
        supplied_issues = tuple(issues)
        if status is TimingOutputStatus.PARTIAL and not supplied_issues:
            supplied_issues = (_timing_issue("dasha", status),)
        return DashaTimeline(
            dasha_timeline_schema_version=DASHA_TIMELINE_SCHEMA_VERSION,
            status=status,
            system=system,
            reference_instant=reference_instant,
            periods=tuple(periods),
            active_mahadasha_id=active_mahadasha_id,
            active_antardasha_id=active_antardasha_id,
            active_pratyantardasha_id=active_pratyantardasha_id,
            calculation_version=calculation_version,
            issues=supplied_issues,
            trace_id=trace_id,
        )


class TransitSummaryFactory:
    @staticmethod
    def producer_evidence(
        *,
        capability: CapabilityInspection,
        positions: Sequence[TransitPosition],
        natal_target_references: Sequence[EvidenceReference] = (),
        rule_matches: Sequence[RuleMatch] = (),
        domain_effect_results: Sequence[InferenceResult] = (),
        producer_version: str,
        producer_schema_version: str,
        trace_id: str,
    ) -> TransitProducerEvidence:
        raise ValueError(
            "transit capability is unavailable because no authoritative producer is installed"
        )

    @staticmethod
    def unavailable() -> TransitSummary:
        return TransitSummary(
            transit_summary_schema_version=TRANSIT_SUMMARY_SCHEMA_VERSION,
            status=TimingOutputStatus.UNAVAILABLE,
            reference_instant=None,
            positions=(),
            natal_relationships=(),
            active_rule_match_ids=(),
            domain_effect_trace_ids=(),
            producer_evidence=None,
            calculation_version=None,
            issues=(_timing_issue("transits", TimingOutputStatus.UNAVAILABLE),),
            trace_id="transits.unavailable",
        )

    @staticmethod
    def from_calculator_output(
        *,
        status: TimingOutputStatus,
        reference_instant: str,
        positions: Sequence[TransitPosition],
        natal_relationships: Sequence[TransitRelationship],
        active_rule_match_ids: Sequence[str],
        domain_effect_trace_ids: Sequence[str],
        producer_evidence: TransitProducerEvidence,
        calculation_version: str,
        issues: Sequence[DomainIssue] = (),
        trace_id: str,
    ) -> TransitSummary:
        raise ValueError(
            "transit capability is unavailable because no authoritative producer is installed"
        )


__all__ = (
    "DashaTimelineFactory",
    "DomainPredictionFactory",
    "TransitSummaryFactory",
    "YogaDiagnosticFactory",
)
