"""Immutable Prompt-05 domain, diagnostic, and timing output contracts.

This module maps and validates already-authoritative values.  It performs no
astrology, rule evaluation, inference arithmetic, timing calculation, or
public-output assembly.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import InitVar, dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import math
from numbers import Real
import re
from typing import Any, TypeVar

from systems.Parasara.engine.capability import (
    CapabilityInspection,
    CapabilityReadiness,
)
from systems.Parasara.engine.inference.models import (
    CapabilityAvailability,
    ConflictRecord,
    ContributionSign,
    DataCompleteness,
    EvidenceReference,
    InferenceCompatibilityProjection,
    InferenceResult,
    InferenceStatus,
    inference_result_logical_sha256,
    inference_result_from_logical_data,
    inference_model_to_logical_data,
)
from systems.Parasara.engine.rules.canonical import (
    CanonicalValueError,
    FrozenMapping,
    canonical_json_bytes,
    canonical_json_data,
    freeze_canonical,
)
from systems.Parasara.engine.rules.rule_match import (
    RuleMatch,
    RuleMatchStatus,
    rule_match_from_logical_data,
    rule_match_to_logical_data,
)


DOMAIN_PREDICTION_SCHEMA_VERSION = "1.0.0"
YOGA_DIAGNOSTIC_SCHEMA_VERSION = "1.0.0"
DASHA_TIMELINE_SCHEMA_VERSION = "1.0.0"
TRANSIT_SUMMARY_SCHEMA_VERSION = "1.0.0"

_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:@+/-]{0,255}$")
_CODE = re.compile(r"^[A-Z][A-Z0-9_]{1,127}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_WINDOWS_PATH = re.compile(r"(?i)(?<![A-Za-z0-9])[A-Z]:[\\/]")
_UNC_PATH = re.compile(r"(?:^|\s)(?:\\\\|//)[^\\/\s]+[\\/][^\s]+")
_POSIX_PATH = re.compile(
    r"(?i)(?<![:A-Za-z0-9])/(?:home|users|root|tmp|var|etc|opt|srv|mnt|workspace|workspaces|repo|repos)(?:/|\b)"
)
_REPOSITORY_PATH = re.compile(
    r"(?i)(?:^|\s)(?:systems/parasara|frontend/|tests/|tools/|documentation/ai-prompt)(?:/|\b)"
)
_TRACEBACK_FRAGMENT = re.compile(
    r"Traceback \(most recent call last\)|\bFile\s+[\"'][^\"']+[\"'],\s+line\s+\d+"
)


class DomainId(str, Enum):
    CAREER = "career"
    WEALTH = "wealth"
    MARRIAGE = "marriage"
    CHILDREN = "children"
    HEALTH = "health"
    SAFETY = "safety"


DOMAIN_ORDER = tuple(DomainId)


class DomainStatus(str, Enum):
    EVALUATED = "evaluated"
    PARTIAL = "partial"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    UNAVAILABLE = "unavailable"
    NOT_SUPPORTED = "not_supported"
    NOT_REQUESTED = "not_requested"
    FAILED = "failed"


class NarrativeSectionType(str, Enum):
    HEADLINE = "headline"
    SUPPORTING_FACTORS = "supporting_factors"
    CHALLENGING_FACTORS = "challenging_factors"
    TIMING_NOTES = "timing_notes"
    CONFIDENCE_NOTE = "confidence_note"
    LIMITATIONS = "limitations"


_NARRATIVE_ORDER = {item: index for index, item in enumerate(NarrativeSectionType)}


class DomainIssueSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


class TimingOutputStatus(str, Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    NOT_REQUESTED = "not_requested"
    FAILED = "failed"


class TimingProducerReadiness(str, Enum):
    READY = "ready"
    READY_EMPTY = "ready_empty"
    PARTIAL = "partial"


def _text(name: str, value: Any, *, optional: bool = False, limit: int = 256) -> None:
    if optional and value is None:
        return
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value.strip() or value != value.strip():
        raise ValueError(f"{name} must be a canonical nonempty string")
    if len(value) > limit or "\x00" in value:
        raise ValueError(f"{name} exceeds the safe text contract")


def _identity(name: str, value: Any, *, optional: bool = False) -> None:
    if optional and value is None:
        return
    _text(name, value)
    if not _IDENTITY.fullmatch(value):
        raise ValueError(f"{name} must be a canonical identity")


def _schema_version(name: str, value: Any) -> None:
    _text(name, value)
    if not _SEMVER.fullmatch(value):
        raise ValueError(f"{name} must be strict SemVer")


def _finite(
    name: str,
    value: Any,
    *,
    lower: float | None = None,
    upper: float | None = None,
) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise TypeError(f"{name} must be finite numeric")
    normalized = 0.0 if float(value) == 0.0 else float(value)
    if lower is not None and normalized < lower:
        raise ValueError(f"{name} must be >= {lower}")
    if upper is not None and normalized > upper:
        raise ValueError(f"{name} must be <= {upper}")
    return normalized


def _optional_unit(name: str, value: Any) -> float | None:
    return None if value is None else _finite(name, value, lower=0.0, upper=1.0)


def _tuple_of(name: str, value: Any, kind: type, *, nonempty: bool = False) -> tuple:
    if not isinstance(value, tuple) or any(not isinstance(item, kind) for item in value):
        raise TypeError(f"{name} must be an immutable {kind.__name__} tuple")
    if nonempty and not value:
        raise ValueError(f"{name} must be nonempty")
    return value


def _strings(
    name: str,
    value: Any,
    *,
    sorted_unique: bool = False,
    nonempty: bool = False,
) -> tuple[str, ...]:
    values = _tuple_of(name, value, str, nonempty=nonempty)
    for index, item in enumerate(values):
        _text(f"{name}[{index}]", item)
    if len(set(values)) != len(values):
        raise ValueError(f"{name} must be unique")
    if sorted_unique and tuple(sorted(values)) != values:
        raise ValueError(f"{name} must be sorted")
    return values


def _mapping(name: str, value: Any) -> FrozenMapping:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    frozen = freeze_canonical(value, path=f"$.{name}")
    if not isinstance(frozen, FrozenMapping):
        raise TypeError(f"{name} must be a mapping")
    return frozen


def _order(name: str, value: Any) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


def _utc(name: str, value: str) -> datetime:
    _text(name, value)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 instant") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(f"{name} must carry a UTC offset")
    return parsed


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainIssue:
    issue_id: str
    code: str
    severity: DomainIssueSeverity
    phase: str
    message: str
    recoverable: bool
    capability_id: str | None = None
    source_rule_id: str | None = None
    source_trace_id: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _identity("issue_id", self.issue_id)
        if not isinstance(self.code, str) or not _CODE.fullmatch(self.code):
            raise ValueError("code must be an uppercase safe code")
        if not isinstance(self.severity, DomainIssueSeverity):
            raise TypeError("severity must be DomainIssueSeverity")
        _identity("phase", self.phase)
        _text("message", self.message, limit=512)
        if any(pattern.search(self.message) for pattern in (
            _WINDOWS_PATH,
            _UNC_PATH,
            _POSIX_PATH,
            _REPOSITORY_PATH,
            _TRACEBACK_FRAGMENT,
        )):
            raise ValueError("message must not expose stack traces or filesystem paths")
        if type(self.recoverable) is not bool:
            raise TypeError("recoverable must be a Boolean")
        for name in ("capability_id", "source_rule_id", "source_trace_id"):
            _identity(name, getattr(self, name), optional=True)
        object.__setattr__(self, "details", _mapping("details", self.details))


class CareerComponentKind(str, Enum):
    PLANET = "planet"
    HOUSE = "house"


@dataclass(frozen=True, slots=True, kw_only=True)
class CompatibilityScalar:
    value: str | int | float | bool | None

    def __post_init__(self) -> None:
        if self.value is not None and not isinstance(
            self.value, (str, int, float, bool)
        ):
            raise TypeError("compatibility scalar has an unsupported type")
        if isinstance(self.value, float) and not math.isfinite(self.value):
            raise ValueError("compatibility scalar must be finite")


@dataclass(frozen=True, slots=True, kw_only=True)
class CompatibilitySequence:
    items: tuple[CompatibilityValue, ...]

    def __post_init__(self) -> None:
        _tuple_of("items", self.items, (CompatibilityScalar, CompatibilitySequence, CompatibilityObject))


@dataclass(frozen=True, slots=True, kw_only=True)
class CompatibilityEntry:
    key: str
    value: CompatibilityValue

    def __post_init__(self) -> None:
        _text("key", self.key)
        if not isinstance(
            self.value, (CompatibilityScalar, CompatibilitySequence, CompatibilityObject)
        ):
            raise TypeError("compatibility entry has an unsupported value")


@dataclass(frozen=True, slots=True, kw_only=True)
class CompatibilityObject:
    entries: tuple[CompatibilityEntry, ...]

    def __post_init__(self) -> None:
        _tuple_of("entries", self.entries, CompatibilityEntry)
        keys = tuple(item.key for item in self.entries)
        if len(set(keys)) != len(keys):
            raise ValueError("compatibility object keys must be unique")


CompatibilityValue = CompatibilityScalar | CompatibilitySequence | CompatibilityObject


def compatibility_value(value: Any) -> CompatibilityValue:
    """Own an arbitrary JSON value as an explicit, order-preserving typed tree."""

    if isinstance(value, Mapping):
        return CompatibilityObject(entries=tuple(
            CompatibilityEntry(key=key, value=compatibility_value(item))
            for key, item in value.items()
        ))
    if isinstance(value, (list, tuple)):
        return CompatibilitySequence(items=tuple(compatibility_value(item) for item in value))
    return CompatibilityScalar(value=value)


def compatibility_value_to_python(value: CompatibilityValue) -> Any:
    """Project the typed compatibility tree to a fresh public JSON value."""

    if isinstance(value, CompatibilityObject):
        return {
            item.key: compatibility_value_to_python(item.value)
            for item in value.entries
        }
    if isinstance(value, CompatibilitySequence):
        return [compatibility_value_to_python(item) for item in value.items]
    if isinstance(value, CompatibilityScalar):
        return value.value
    raise TypeError("value must be a typed compatibility value")


def _ordered_compatibility_to_python(value: Any) -> Any:
    kind, content = value
    if kind == "mapping":
        return {
            key: _ordered_compatibility_to_python(item) for key, item in content
        }
    if kind == "sequence":
        return [_ordered_compatibility_to_python(item) for item in content]
    if kind == "scalar":
        return content
    raise ValueError("invalid ordered compatibility source")


def _freeze_ordered_compatibility_validation(value: Any) -> tuple[Any, Any]:
    if isinstance(value, Mapping):
        return (
            "mapping",
            tuple(
                (key, _freeze_ordered_compatibility_validation(item))
                for key, item in value.items()
            ),
        )
    if isinstance(value, (list, tuple)):
        return (
            "sequence",
            tuple(_freeze_ordered_compatibility_validation(item) for item in value),
        )
    return ("scalar", value)


def _career_legacy_evidence(candidate: Any) -> dict[str, Any]:
    evidence = candidate.compatibility_evidence
    rule_type = candidate.definition.rule_type
    if rule_type == "strong_in_10":
        return {
            "planet": evidence.get("planet"),
            "house": evidence.get("house"),
            "strength": evidence.get("strength"),
        }
    if rule_type == "lord_status":
        return {
            "lord": evidence.get("lord"),
            "dignity": evidence.get("dignity"),
        }
    return {
        "occ1": list(evidence.get("occ1", ())),
        "occ10": list(evidence.get("occ10", ())),
    }
    raise TypeError("value must be a typed compatibility value")


@dataclass(frozen=True, slots=True, kw_only=True)
class CareerComponentCompatibility:
    component_id: str
    kind: CareerComponentKind
    planet: str | None
    house: int
    weight: float
    occupants: tuple[str, ...]
    source_fact_trace_ids: tuple[str, ...]
    order: int

    def __post_init__(self) -> None:
        _identity("component_id", self.component_id)
        if not isinstance(self.kind, CareerComponentKind):
            raise TypeError("kind must be CareerComponentKind")
        _identity("planet", self.planet, optional=True)
        if type(self.house) is not int or not 1 <= self.house <= 12:
            raise ValueError("house must be an integer in [1, 12]")
        object.__setattr__(self, "weight", _finite("weight", self.weight))
        _strings("occupants", self.occupants)
        _strings("source_fact_trace_ids", self.source_fact_trace_ids)
        _order("order", self.order)
        if self.kind is CareerComponentKind.PLANET:
            if self.planet is None or self.occupants:
                raise ValueError("planet compatibility requires planet and no occupants")
        elif self.planet is not None:
            raise ValueError("house compatibility cannot carry a planet")


@dataclass(frozen=True, slots=True, kw_only=True)
class CareerIndicatorCompatibility:
    indicator_id: str
    context: CompatibilityObject
    evidence: CompatibilityObject
    order: int

    def __post_init__(self) -> None:
        _identity("indicator_id", self.indicator_id)
        if not isinstance(self.context, CompatibilityObject):
            raise TypeError("context must be CompatibilityObject")
        if not isinstance(self.evidence, CompatibilityObject):
            raise TypeError("evidence must be CompatibilityObject")
        _order("order", self.order)


@dataclass(frozen=True, slots=True, kw_only=True)
class CareerCompatibilityProjection:
    profile_id: str
    source_batch_digest: str
    base_score: float
    total_contribution: float
    formula: str
    public_trace_id: str
    precision: int
    components: tuple[CareerComponentCompatibility, ...]
    indicators: tuple[CareerIndicatorCompatibility, ...]

    def __post_init__(self) -> None:
        if self.profile_id != "career_public_v1":
            raise ValueError("unsupported Career compatibility profile")
        if not isinstance(self.source_batch_digest, str) or not _SHA256.fullmatch(self.source_batch_digest):
            raise ValueError("source_batch_digest must be lowercase SHA-256")
        object.__setattr__(self, "base_score", _finite("base_score", self.base_score, lower=0.0, upper=1.0))
        object.__setattr__(
            self,
            "total_contribution",
            _finite("total_contribution", self.total_contribution),
        )
        _text("formula", self.formula, limit=512)
        _identity("public_trace_id", self.public_trace_id)
        if type(self.precision) is not int or not 0 <= self.precision <= 12:
            raise ValueError("precision must be an integer in [0, 12]")
        _tuple_of("components", self.components, CareerComponentCompatibility)
        _tuple_of("indicators", self.indicators, CareerIndicatorCompatibility)
        if tuple(sorted(self.components, key=lambda item: (item.order, item.component_id))) != self.components:
            raise ValueError("Career compatibility components use non-canonical order")
        if tuple(sorted(self.indicators, key=lambda item: (item.order, item.indicator_id))) != self.indicators:
            raise ValueError("Career compatibility indicators use non-canonical order")
        for name, values, attr in (
            ("component", self.components, "component_id"),
            ("indicator", self.indicators, "indicator_id"),
        ):
            identities = tuple(getattr(item, attr) for item in values)
            if len(set(identities)) != len(identities):
                raise ValueError(f"duplicate Career compatibility {name} identity")


_YOGA_COMPATIBILITY_FACTORY_TOKEN = object()


@dataclass(frozen=True, slots=True, kw_only=True)
class YogaCompatibilityProjection:
    name: str
    source_order: int
    evidence: Mapping[str, Any]
    houses: tuple[Any, ...]
    _factory_token: InitVar[object | None] = None

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _YOGA_COMPATIBILITY_FACTORY_TOKEN:
            raise ValueError(
                "Yoga compatibility requires the validated producer factory"
            )
        _text("name", self.name)
        _order("source_order", self.source_order)
        object.__setattr__(self, "evidence", _mapping("evidence", self.evidence))
        frozen_houses = freeze_canonical(self.houses, path="$.houses")
        if not isinstance(frozen_houses, tuple):
            raise TypeError("houses must be an immutable tuple")
        object.__setattr__(self, "houses", frozen_houses)


def _build_yoga_compatibility_projection(
    *,
    name: str,
    source_order: int,
    evidence: Mapping[str, Any],
    houses: tuple[Any, ...],
) -> YogaCompatibilityProjection:
    """Internal construction boundary for approved Yoga presentation data."""

    return YogaCompatibilityProjection(
        name=name,
        source_order=source_order,
        evidence=evidence,
        houses=houses,
        _factory_token=_YOGA_COMPATIBILITY_FACTORY_TOKEN,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainComponent:
    component_id: str
    domain: DomainId
    label: str
    score: float
    weight: float | None
    confidence: float | None
    source_inference_component_id: str
    contribution_ids: tuple[str, ...]
    contributing_rule_ids: tuple[str, ...]
    evidence_references: tuple[EvidenceReference, ...]
    trace_id: str
    order: int

    def __post_init__(self) -> None:
        for name in ("component_id", "source_inference_component_id", "trace_id"):
            _identity(name, getattr(self, name))
        if not isinstance(self.domain, DomainId):
            raise TypeError("domain must be DomainId")
        _text("label", self.label)
        object.__setattr__(self, "score", _finite("score", self.score, lower=0.0, upper=1.0))
        if self.weight is not None:
            object.__setattr__(self, "weight", _finite("weight", self.weight))
        object.__setattr__(self, "confidence", _optional_unit("confidence", self.confidence))
        _strings("contribution_ids", self.contribution_ids)
        _strings("contributing_rule_ids", self.contributing_rule_ids)
        _tuple_of("evidence_references", self.evidence_references, EvidenceReference)
        _order("order", self.order)


_DOMAIN_INDICATOR_FACTORY_TOKEN = object()


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainIndicator:
    indicator_id: str
    domain: DomainId
    source_rule_id: str
    source_rule_version: str
    source_contribution_id: str | None
    label: str
    direction: ContributionSign
    contribution: float | None
    context: str
    priority: int
    evidence_summary: Mapping[str, Any]
    evidence_references: tuple[EvidenceReference, ...]
    source_rule_trace_id: str
    trace_id: str
    order: int
    source_rule_match: RuleMatch = field(repr=False, compare=False)
    _factory_token: InitVar[object | None] = None

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _DOMAIN_INDICATOR_FACTORY_TOKEN:
            raise ValueError("DomainIndicator requires the evaluator-owned producer boundary")
        for name in (
            "indicator_id", "source_rule_id", "source_rule_version",
            "source_rule_trace_id", "trace_id",
        ):
            _identity(name, getattr(self, name))
        _identity("source_contribution_id", self.source_contribution_id, optional=True)
        if not isinstance(self.domain, DomainId):
            raise TypeError("domain must be DomainId")
        _text("label", self.label)
        if not isinstance(self.direction, ContributionSign):
            raise TypeError("direction must be ContributionSign")
        if self.contribution is not None:
            object.__setattr__(self, "contribution", _finite("contribution", self.contribution))
        _identity("context", self.context)
        if type(self.priority) is not int:
            raise TypeError("priority must be an integer")
        object.__setattr__(self, "evidence_summary", _mapping("evidence_summary", self.evidence_summary))
        _tuple_of("evidence_references", self.evidence_references, EvidenceReference)
        _order("order", self.order)
        if not isinstance(self.source_rule_match, RuleMatch):
            raise TypeError("source_rule_match must be RuleMatch")


def _build_domain_indicator(**values: Any) -> DomainIndicator:
    """Private construction hook used only inside an authoritative evaluator run."""

    return DomainIndicator(
        **values,
        _factory_token=_DOMAIN_INDICATOR_FACTORY_TOKEN,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class NarrativeSection:
    section_id: str
    section_type: NarrativeSectionType
    text: str
    source_rule_ids: tuple[str, ...]
    source_indicator_ids: tuple[str, ...]
    source_issue_ids: tuple[str, ...]
    source_trace_ids: tuple[str, ...]
    template_id: str
    template_version: str
    order: int

    def __post_init__(self) -> None:
        _identity("section_id", self.section_id)
        if not isinstance(self.section_type, NarrativeSectionType):
            raise TypeError("section_type must be NarrativeSectionType")
        _text("text", self.text, limit=2048)
        for name in (
            "source_rule_ids", "source_indicator_ids", "source_issue_ids",
            "source_trace_ids",
        ):
            _strings(name, getattr(self, name))
        if not any((self.source_rule_ids, self.source_indicator_ids, self.source_issue_ids, self.source_trace_ids)):
            raise ValueError("narrative section requires typed source lineage")
        _identity("template_id", self.template_id)
        _identity("template_version", self.template_version)
        _order("order", self.order)


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainTimingReference:
    status: CapabilityAvailability
    evaluation_instant: str | None
    dasha_timeline_digest: str | None
    transit_summary_digest: str | None
    source_rule_ids: tuple[str, ...]
    source_trace_ids: tuple[str, ...]
    issues: tuple[DomainIssue, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.status, CapabilityAvailability):
            raise TypeError("status must be CapabilityAvailability")
        if self.evaluation_instant is not None:
            _utc("evaluation_instant", self.evaluation_instant)
        for name in ("dasha_timeline_digest", "transit_summary_digest"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not _SHA256.fullmatch(value)):
                raise ValueError(f"{name} must be lowercase SHA-256 or None")
        _strings("source_rule_ids", self.source_rule_ids)
        _strings("source_trace_ids", self.source_trace_ids)
        _tuple_of("issues", self.issues, DomainIssue)
        if self.status is CapabilityAvailability.UNAVAILABLE and not self.issues:
            raise ValueError("unavailable timing requires a typed issue")
        if self.status is CapabilityAvailability.AVAILABLE and (
            self.evaluation_instant is None
            or (self.dasha_timeline_digest is None and self.transit_summary_digest is None)
        ):
            raise ValueError("available timing requires an instant and supplied timing digest")


_DOMAIN_PREDICTION_FACTORY_TOKEN = object()


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainPrediction:
    domain_prediction_schema_version: str
    system: str
    domain: DomainId
    status: DomainStatus
    summary: str | None
    score: float | None
    confidence: float | None
    agreement: float | None
    components: tuple[DomainComponent, ...]
    indicators: tuple[DomainIndicator, ...]
    conflicts: tuple[ConflictRecord, ...]
    timing: DomainTimingReference | None
    narrative_sections: tuple[NarrativeSection, ...]
    data_completeness: DataCompleteness | None
    missing_data: tuple[str, ...]
    issues: tuple[DomainIssue, ...]
    source_inference_trace_id: str | None
    trace_id: str
    engine_version: str
    rule_set_version: str | None
    inference_version: str | None
    interpreter_version: str
    narrative_version: str
    career_compatibility: CareerCompatibilityProjection | None
    logical_digest: str = ""
    source_inference_result: InferenceResult | None = field(
        default=None, repr=False, compare=False
    )
    source_inference_compatibility: InferenceCompatibilityProjection | None = field(
        default=None, repr=False, compare=False
    )
    source_evaluation_batch: Any | None = field(default=None, repr=False, compare=False)
    source_authority: Any | None = field(default=None, repr=False, compare=False)
    _factory_token: InitVar[object | None] = None

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _DOMAIN_PREDICTION_FACTORY_TOKEN:
            raise ValueError("DomainPrediction requires the validated producer factory")
        _schema_version("domain_prediction_schema_version", self.domain_prediction_schema_version)
        if self.system != "parashara":
            raise ValueError("system must be parashara")
        if not isinstance(self.domain, DomainId):
            raise TypeError("domain must be DomainId")
        if not isinstance(self.status, DomainStatus):
            raise TypeError("status must be DomainStatus")
        _text("summary", self.summary, optional=True, limit=2048)
        for name in ("score", "confidence", "agreement"):
            object.__setattr__(self, name, _optional_unit(name, getattr(self, name)))
        _tuple_of("components", self.components, DomainComponent)
        _tuple_of("indicators", self.indicators, DomainIndicator)
        _tuple_of("conflicts", self.conflicts, ConflictRecord)
        if self.timing is not None and not isinstance(self.timing, DomainTimingReference):
            raise TypeError("timing must be DomainTimingReference or None")
        _tuple_of("narrative_sections", self.narrative_sections, NarrativeSection)
        if self.data_completeness is not None and not isinstance(self.data_completeness, DataCompleteness):
            raise TypeError("data_completeness must be DataCompleteness or None")
        _strings("missing_data", self.missing_data, sorted_unique=True)
        _tuple_of("issues", self.issues, DomainIssue)
        _identity("source_inference_trace_id", self.source_inference_trace_id, optional=True)
        for name in ("trace_id", "engine_version", "interpreter_version", "narrative_version"):
            _identity(name, getattr(self, name))
        _identity("rule_set_version", self.rule_set_version, optional=True)
        _identity("inference_version", self.inference_version, optional=True)
        if self.career_compatibility is not None and not isinstance(
            self.career_compatibility, CareerCompatibilityProjection
        ):
            raise TypeError("career_compatibility must be CareerCompatibilityProjection or None")
        if self.source_inference_compatibility is not None and not isinstance(
            self.source_inference_compatibility, InferenceCompatibilityProjection
        ):
            raise TypeError(
                "source_inference_compatibility must be an InferenceCompatibilityProjection or None"
            )
        self._validate_ids_and_order()
        self._validate_status_and_inference()
        _set_or_validate_digest(self)

    def _validate_ids_and_order(self) -> None:
        def unique(name: str, values: tuple, attr: str) -> None:
            identities = tuple(getattr(item, attr) for item in values)
            if len(set(identities)) != len(identities):
                raise ValueError(f"duplicate {name} identities")

        unique("component", self.components, "component_id")
        unique("indicator", self.indicators, "indicator_id")
        unique("narrative", self.narrative_sections, "section_id")
        unique("issue", self.issues, "issue_id")
        if tuple(sorted(self.components, key=lambda item: (item.order, item.component_id))) != self.components:
            raise ValueError("components use non-canonical order")
        if tuple(sorted(
            self.indicators,
            key=lambda item: (
                item.order, -item.priority, item.source_rule_id,
                item.source_rule_version, item.indicator_id,
            ),
        )) != self.indicators:
            raise ValueError("indicators use non-canonical order")
        if tuple(sorted(
            self.narrative_sections,
            key=lambda item: (item.order, _NARRATIVE_ORDER[item.section_type], item.section_id),
        )) != self.narrative_sections:
            raise ValueError("narrative sections use non-canonical order")
        if any(item.domain is not self.domain for item in (*self.components, *self.indicators)):
            raise ValueError("component/indicator domain mismatch")
        issue_ids = {item.issue_id for item in self.issues}
        indicator_ids = {item.indicator_id for item in self.indicators}
        for section in self.narrative_sections:
            if not set(section.source_issue_ids).issubset(issue_ids):
                raise ValueError("narrative has an unresolved issue reference")
            if not set(section.source_indicator_ids).issubset(indicator_ids):
                raise ValueError("narrative has an unresolved indicator reference")

    def _validate_status_and_inference(self) -> None:
        evaluated = {
            DomainStatus.EVALUATED,
            DomainStatus.PARTIAL,
            DomainStatus.INSUFFICIENT_EVIDENCE,
        }
        source = self.source_inference_result
        if self.status in evaluated:
            if source is None:
                raise ValueError("evaluated domain status requires one InferenceResult")
            expected_status = {
                InferenceStatus.EVALUATED: DomainStatus.EVALUATED,
                InferenceStatus.PARTIAL: DomainStatus.PARTIAL,
                InferenceStatus.INSUFFICIENT_EVIDENCE: DomainStatus.INSUFFICIENT_EVIDENCE,
                InferenceStatus.FAILED: DomainStatus.FAILED,
            }[source.status]
            if self.status is not expected_status:
                raise ValueError("domain and inference statuses disagree")
            if source.system != self.system or source.domain != self.domain.value:
                raise ValueError("domain/system does not reconcile to InferenceResult")
            if (
                self.score != source.normalized_score
                or self.confidence != source.confidence
                or self.agreement != source.agreement
                or self.conflicts != source.conflicts
                or self.data_completeness != source.data_completeness
                or self.source_inference_trace_id != source.trace_id
                or self.rule_set_version != source.rule_set_version
                or self.inference_version != source.inference_version
            ):
                raise ValueError("domain values do not reconcile to InferenceResult")
            if self.summary is None:
                raise ValueError("evaluated domain requires a summary")
            source_components = {item.component_id: item for item in source.components}
            source_contributions = {item.contribution_id: item for item in source.contributions}
            source_rules = {item.rule_id for item in source.contributions}
            parent_matches = {}
            authority = self.source_authority
            if self.domain is DomainId.CAREER:
                if (
                    authority is None
                    or authority.__class__.__module__
                    != "systems.Parasara.engine.interpreters.career"
                    or authority.__class__.__name__ != "_CareerInferenceEvaluation"
                ):
                    raise ValueError(
                        "evaluated Career domain requires its private same-run authority"
                    )
                if (
                    self.source_inference_result is not authority.inference_result
                    or self.source_inference_compatibility
                    is not authority.compatibility_projection
                    or self.source_evaluation_batch is not authority.batch
                ):
                    raise ValueError("Career sources are detached from the same-run authority")
                parent_matches = {
                    (item.rule_id, item.rule_version, item.trace_id): item
                    for item in authority.ledger.rule_matches
                }
            source_trace_ids = {
                source.trace_id,
                source.data_completeness.trace_id,
                *(item.trace_id for item in source.contributions),
                *(item.source_rule_trace_id for item in source.contributions),
                *(evidence.trace_id for item in source.contributions for evidence in item.evidence_references if evidence.trace_id),
                *(item.trace_id for item in source.components),
                *(evidence.trace_id for item in source.components for evidence in item.evidence_references if evidence.trace_id),
            }
            for item in self.components:
                component = source_components.get(item.source_inference_component_id)
                if component is None:
                    raise ValueError("unresolved inference component reference")
                if item.score != component.normalized_value:
                    raise ValueError("component score does not reconcile to inference")
                if (
                    item.contribution_ids != component.contribution_ids
                    or item.contributing_rule_ids != component.rule_ids
                    or item.evidence_references != component.evidence_references
                    or item.trace_id != component.trace_id
                ):
                    raise ValueError("component lineage does not reconcile to inference")
            for item in self.indicators:
                rule_match = item.source_rule_match
                if parent_matches:
                    authoritative_match = parent_matches.get((
                        rule_match.rule_id,
                        rule_match.rule_version,
                        rule_match.trace_id,
                    ))
                    if authoritative_match is None or canonical_json_data(
                        rule_match_to_logical_data(rule_match)
                    ) != canonical_json_data(
                        rule_match_to_logical_data(authoritative_match)
                    ):
                        raise ValueError(
                            "indicator RuleMatch is not owned by the evaluation batch"
                        )
                if (
                    rule_match.system != self.system
                    or self.domain.value not in rule_match.domains
                    or item.source_rule_id != rule_match.rule_id
                    or item.source_rule_version != rule_match.rule_version
                    or item.source_rule_trace_id != rule_match.trace_id
                ):
                    raise ValueError("indicator does not reconcile to authoritative RuleMatch")
                if item.source_contribution_id is None:
                    if item.contribution is not None:
                        raise ValueError("score-bearing indicator requires a contribution identity")
                    if any(
                        contribution.rule_id == rule_match.rule_id
                        and contribution.rule_version == rule_match.rule_version
                        and contribution.source_rule_trace_id == rule_match.trace_id
                        for contribution in source.contributions
                    ):
                        raise ValueError(
                            "indicator cannot discard its authoritative contribution identity"
                        )
                    if (
                        canonical_json_data(item.evidence_summary)
                        != canonical_json_data(rule_match.evidence)
                        or item.trace_id != rule_match.trace_id
                    ):
                        raise ValueError("diagnostic indicator lineage does not reconcile to RuleMatch")
                    continue
                contribution = source_contributions.get(item.source_contribution_id)
                if contribution is None:
                    raise ValueError("unresolved indicator contribution reference")
                if (
                    item.source_rule_id != contribution.rule_id
                    or item.source_rule_version != contribution.rule_version
                    or item.contribution != contribution.final_contribution
                    or item.direction is not contribution.sign
                    or item.source_rule_trace_id != contribution.source_rule_trace_id
                    or item.context != contribution.context
                    or item.priority != contribution.priority
                    or item.evidence_references != contribution.evidence_references
                    or item.trace_id != contribution.trace_id
                ):
                    raise ValueError("indicator does not reconcile to contribution")
            for section in self.narrative_sections:
                if not set(section.source_rule_ids).issubset(source_rules):
                    raise ValueError("narrative has an unresolved rule reference")
                if not set(section.source_trace_ids).issubset(source_trace_ids):
                    raise ValueError("narrative has an unresolved trace reference")
                if (
                    section.section_type
                    not in (
                        NarrativeSectionType.LIMITATIONS,
                        NarrativeSectionType.CONFIDENCE_NOTE,
                    )
                    and not section.source_rule_ids
                    and not section.source_indicator_ids
                ):
                    raise ValueError("substantive narrative requires rule or indicator lineage")
            if self.domain is DomainId.CAREER:
                projection = self.career_compatibility
                if projection is None:
                    raise ValueError("evaluated Career domain requires typed compatibility")
                inference_projection = self.source_inference_compatibility
                batch = self.source_evaluation_batch
                if inference_projection is None or batch is None:
                    raise ValueError(
                        "evaluated Career domain requires retained inference and evaluation sources"
                    )
                if (
                    batch.__class__.__module__
                    != "systems.Parasara.engine.interpreters.career_models"
                    or batch.__class__.__name__ != "CareerEvaluationBatch"
                ):
                    raise TypeError("source_evaluation_batch must be CareerEvaluationBatch")
                if projection.source_batch_digest != batch.logical_digest:
                    raise ValueError("Career compatibility batch digest does not reconcile")
                if (
                    inference_projection.source_result_digest
                    != inference_result_logical_sha256(source)
                    or inference_projection.source_config_digest
                    != authority.config_fingerprint
                    or projection.profile_id != inference_projection.profile_id
                    or projection.base_score != inference_projection.base_score
                    or projection.total_contribution
                    != inference_projection.total_contribution
                    or projection.formula != inference_projection.formula
                    or projection.public_trace_id
                    != inference_projection.public_trace_id
                    or projection.precision != inference_projection.precision
                ):
                    raise ValueError(
                        "Career compatibility values do not reconcile to InferenceEngine"
                    )
                component_ids = tuple(item.component_id for item in self.components)
                indicator_ids = tuple(item.indicator_id for item in self.indicators)
                if tuple(item.component_id for item in projection.components) != component_ids:
                    raise ValueError("Career compatibility components do not reconcile")
                if tuple(item.indicator_id for item in projection.indicators) != indicator_ids:
                    raise ValueError("Career compatibility indicators do not reconcile")
                weights = {item.component_id: item.weight for item in self.components}
                if any(item.weight != weights[item.component_id] for item in projection.components):
                    raise ValueError("Career compatibility weights do not reconcile")
                self._validate_career_evaluation_source(batch, projection)
            elif any(
                value is not None
                for value in (
                    self.career_compatibility,
                    self.source_inference_compatibility,
                    self.source_evaluation_batch,
                    self.source_authority,
                )
            ):
                raise ValueError("only Career may carry Career compatibility sources")
            required_missing = tuple(sorted({
                *source.data_completeness.missing_required,
                *source.data_completeness.missing_optional,
            }))
            if self.missing_data != required_missing:
                raise ValueError("missing_data does not reconcile to completeness")
            if self.status is DomainStatus.PARTIAL and not self.issues:
                raise ValueError("partial domain requires typed issues")
            if self.status is DomainStatus.INSUFFICIENT_EVIDENCE and not self.issues:
                raise ValueError("insufficient evidence requires a typed issue")
            if self.status is DomainStatus.INSUFFICIENT_EVIDENCE and (
                source.raw_score != 0.0
                or source.normalized_score != 0.5
                or source.confidence != 0.0
                or source.agreement != 0.0
                or source.contributions
                ):
                raise ValueError(
                    "insufficient inference must preserve Prompt-03 neutral semantics"
                )
        else:
            if any(value is not None for value in (self.score, self.confidence, self.agreement)):
                raise ValueError("non-evaluated status cannot carry score/confidence/agreement")
            if any((self.components, self.indicators, self.conflicts, self.narrative_sections)):
                raise ValueError("non-evaluated status cannot carry evaluated presentation")
            if any(
                value is not None
                for value in (
                    self.career_compatibility,
                    self.source_inference_compatibility,
                    self.source_evaluation_batch,
                    self.source_authority,
                )
            ):
                raise ValueError("non-evaluated status cannot carry Career compatibility")
            if self.data_completeness is not None or self.missing_data:
                raise ValueError("non-evaluated status cannot claim completeness")
            if self.status is not DomainStatus.FAILED and source is not None:
                raise ValueError("non-evaluated status cannot retain InferenceResult")
            if self.status is DomainStatus.FAILED and source is not None:
                if source.status is not InferenceStatus.FAILED:
                    raise ValueError("failed domain can retain only failed inference")
                if self.source_inference_trace_id != source.trace_id:
                    raise ValueError("failed inference trace mismatch")
            elif self.source_inference_trace_id is not None:
                raise ValueError("non-evaluated status cannot claim inference trace")
            if self.status in (
                DomainStatus.UNAVAILABLE,
                DomainStatus.NOT_SUPPORTED,
                DomainStatus.FAILED,
            ) and not self.issues:
                raise ValueError("status requires a typed issue")

    def _validate_career_evaluation_source(
        self,
        batch: Any,
        projection: CareerCompatibilityProjection,
    ) -> None:
        """Reconcile every Career presentation value to its retained typed batch."""

        facts_by_id = {item.fact_id: item for item in batch.component_facts}
        for component, presentation in zip(
            self.components, projection.components
        ):
            fact = facts_by_id.get(component.component_id)
            if fact is None:
                raise ValueError("Career compatibility component lacks a source fact")
            evidence = fact.evidence
            is_planet = fact.fact_kind.value == "base_kendra_strength"
            expected_kind = CareerComponentKind.PLANET if is_planet else CareerComponentKind.HOUSE
            expected_planet = str(evidence["planet"]) if is_planet else None
            expected_house = int(evidence["house"]) if is_planet else 10
            expected_occupants = () if is_planet else tuple(
                str(item) for item in evidence["occupants"]
            )
            expected_trace_ids = tuple(step.step_id for step in fact.trace_steps)
            if (
                component.component_id != fact.fact_id
                or presentation.kind is not expected_kind
                or presentation.planet != expected_planet
                or presentation.house != expected_house
                or presentation.weight != float(evidence["weight"])
                or presentation.occupants != expected_occupants
                or presentation.source_fact_trace_ids != expected_trace_ids
                or presentation.order != component.order
            ):
                raise ValueError("Career component does not reconcile to evaluation fact")

        candidates = {
            f"career.indicator.{item.definition.candidate_id}": item
            for item in batch.candidates
        }
        presentation_by_id = {
            item.indicator_id: item for item in projection.indicators
        }
        authoritative_matches = {
            (item.rule_id, item.rule_version, item.trace_id): item
            for item in batch.rule_matches
        }
        for indicator in self.indicators:
            candidate = candidates.get(indicator.indicator_id)
            presentation = presentation_by_id.get(indicator.indicator_id)
            if candidate is None or presentation is None:
                raise ValueError("Career indicator lacks an evaluation source")
            match_key = (
                indicator.source_rule_match.rule_id,
                indicator.source_rule_match.rule_version,
                indicator.source_rule_match.trace_id,
            )
            authoritative_match = authoritative_matches.get(match_key)
            if authoritative_match is None or canonical_json_data(
                rule_match_to_logical_data(indicator.source_rule_match)
            ) != canonical_json_data(rule_match_to_logical_data(authoritative_match)):
                raise ValueError(
                    "Career indicator RuleMatch is not owned by the evaluation batch"
                )
            expected_context = _ordered_compatibility_to_python(
                candidate.definition.compatibility_context
            )
            expected_evidence = _career_legacy_evidence(candidate)
            expected_summary = {
                "legacy_context_ordered": candidate.definition.compatibility_context,
                "legacy_evidence_ordered": _freeze_ordered_compatibility_validation(
                    expected_evidence
                ),
            }
            if (
                (
                    indicator.source_contribution_id is not None
                    and canonical_json_data(indicator.evidence_summary)
                    != canonical_json_data(expected_summary)
                )
                or canonical_json_data(
                    compatibility_value_to_python(presentation.context)
                )
                != canonical_json_data(expected_context)
                or canonical_json_data(
                    compatibility_value_to_python(presentation.evidence)
                )
                != canonical_json_data(expected_evidence)
                or presentation.order != indicator.order
            ):
                raise ValueError(
                    "Career indicator compatibility does not reconcile to evaluation batch"
                )


_YOGA_DIAGNOSTIC_FACTORY_TOKEN = object()


@dataclass(frozen=True, slots=True, kw_only=True)
class YogaDiagnostic:
    yoga_diagnostic_schema_version: str
    yoga_id: str
    name: str
    category: str
    matched: bool
    status: RuleMatchStatus
    strength: float | None
    domains: tuple[DomainId, ...]
    source_rule_match: RuleMatch
    evidence_summary: Mapping[str, Any]
    compatibility: YogaCompatibilityProjection
    trace_id: str
    rule_version: str
    rule_set_version: str
    logical_digest: str = ""
    source_evaluation_record: Any | None = field(default=None, repr=False, compare=False)
    _factory_token: InitVar[object | None] = None

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _YOGA_DIAGNOSTIC_FACTORY_TOKEN:
            raise ValueError("YogaDiagnostic requires the validated producer factory")
        _schema_version("yoga_diagnostic_schema_version", self.yoga_diagnostic_schema_version)
        for name in ("yoga_id", "category", "trace_id", "rule_version", "rule_set_version"):
            _identity(name, getattr(self, name))
        _text("name", self.name)
        if type(self.matched) is not bool or not isinstance(self.status, RuleMatchStatus):
            raise TypeError("matched/status types are invalid")
        if self.strength is not None:
            object.__setattr__(self, "strength", _finite("strength", self.strength, lower=0.0, upper=1.0))
        _tuple_of("domains", self.domains, DomainId)
        if tuple(sorted(set(self.domains), key=DOMAIN_ORDER.index)) != self.domains:
            raise ValueError("domains must be unique and in canonical domain order")
        if not isinstance(self.source_rule_match, RuleMatch):
            raise TypeError("source_rule_match must be RuleMatch")
        if not isinstance(self.compatibility, YogaCompatibilityProjection):
            raise TypeError("compatibility must be YogaCompatibilityProjection")
        record = self.source_evaluation_record
        if record is None:
            raise ValueError("YogaDiagnostic requires its authoritative evaluation record")
        if (
            record.__class__.__module__
            != "systems.Parasara.engine.enrichments.yoga_engine"
            or record.__class__.__name__ != "YogaEvaluationRecord"
        ):
            raise TypeError("source_evaluation_record must be YogaEvaluationRecord")
        match = self.source_rule_match
        authoritative_match = record.rule_match
        if canonical_json_data(rule_match_to_logical_data(match)) != canonical_json_data(
            rule_match_to_logical_data(authoritative_match)
        ):
            raise ValueError("YogaDiagnostic does not retain the evaluation RuleMatch")
        if (
            record.condition_result is not None
            and record.condition_result.matched is not authoritative_match.matched
        ):
            raise ValueError("Yoga condition truth disagrees with its RuleMatch")
        if (
            self.yoga_id != match.rule_id
            or self.matched is not authoritative_match.matched
            or self.status is not authoritative_match.status
            or self.trace_id != match.trace_id
            or self.rule_version != match.rule_version
            or self.rule_set_version != match.rule_set_version
            or self.category != match.category
            or tuple(item.value for item in self.domains) != match.domains
        ):
            raise ValueError("YogaDiagnostic does not reconcile to RuleMatch")
        object.__setattr__(self, "evidence_summary", _mapping("evidence_summary", self.evidence_summary))
        if canonical_json_data(self.evidence_summary) != canonical_json_data(match.evidence):
            raise ValueError("Yoga evidence summary does not reconcile to RuleMatch")
        if self.compatibility.name != self.name:
            raise ValueError("Yoga compatibility name does not reconcile")
        if (
            self.name != record.name
            or self.compatibility.source_order != record.source_index
            or
            canonical_json_data(self.compatibility.evidence)
            != canonical_json_data(record.compatibility_evidence)
            or canonical_json_data(self.compatibility.houses)
            != canonical_json_data(record.compatibility_houses)
        ):
            raise ValueError(
                "Yoga compatibility evidence does not reconcile to evaluation record"
            )
        _set_or_validate_digest(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class DashaPeriod:
    period_id: str
    lord: str
    start_utc: str
    end_utc: str
    duration_seconds: int
    level: str
    parent_id: str | None
    order: int

    def __post_init__(self) -> None:
        _identity("period_id", self.period_id)
        _identity("lord", self.lord)
        start = _utc("start_utc", self.start_utc)
        end = _utc("end_utc", self.end_utc)
        if end <= start:
            raise ValueError("period end must be after start")
        if type(self.duration_seconds) is not int or self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be a positive integer")
        if int((end - start).total_seconds()) != self.duration_seconds:
            raise ValueError("duration_seconds must agree with supplied chronology")
        if self.level not in {"mahadasha", "antardasha", "pratyantardasha"}:
            raise ValueError("level must be a supported Dasha period level")
        _identity("parent_id", self.parent_id, optional=True)
        if self.level == "mahadasha" and self.parent_id is not None:
            raise ValueError("mahadasha cannot have a parent")
        if self.level != "mahadasha" and self.parent_id is None:
            raise ValueError("nested Dasha period requires a parent")
        _order("order", self.order)


@dataclass(frozen=True, slots=True, kw_only=True)
class DashaTimeline:
    dasha_timeline_schema_version: str
    status: TimingOutputStatus
    system: str
    reference_instant: str | None
    periods: tuple[DashaPeriod, ...]
    active_mahadasha_id: str | None
    active_antardasha_id: str | None
    active_pratyantardasha_id: str | None
    calculation_version: str | None
    issues: tuple[DomainIssue, ...]
    trace_id: str
    logical_digest: str = ""

    def __post_init__(self) -> None:
        _schema_version("dasha_timeline_schema_version", self.dasha_timeline_schema_version)
        if not isinstance(self.status, TimingOutputStatus):
            raise TypeError("status must be TimingOutputStatus")
        _identity("system", self.system)
        if self.reference_instant is not None:
            _utc("reference_instant", self.reference_instant)
        _tuple_of("periods", self.periods, DashaPeriod)
        for name in (
            "active_mahadasha_id", "active_antardasha_id",
            "active_pratyantardasha_id", "calculation_version",
        ):
            _identity(name, getattr(self, name), optional=True)
        _tuple_of("issues", self.issues, DomainIssue)
        _identity("trace_id", self.trace_id)
        self._validate_periods_and_status()
        _set_or_validate_digest(self)

    def _validate_periods_and_status(self) -> None:
        ids = tuple(item.period_id for item in self.periods)
        if len(set(ids)) != len(ids):
            raise ValueError("Dasha period IDs must be unique")
        if tuple(sorted(self.periods, key=lambda item: (item.order, item.start_utc, item.period_id))) != self.periods:
            raise ValueError("Dasha periods use non-canonical order")
        by_id = {item.period_id: item for item in self.periods}
        parsed = {
            item.period_id: (_utc("start_utc", item.start_utc), _utc("end_utc", item.end_utc))
            for item in self.periods
        }
        for item in self.periods:
            if item.parent_id is not None:
                parent = by_id.get(item.parent_id)
                expected = "mahadasha" if item.level == "antardasha" else "antardasha"
                if parent is None or parent.level != expected or parent.order >= item.order:
                    raise ValueError("Dasha parent reference is unresolved or invalid")
                item_start, item_end = parsed[item.period_id]
                parent_start, parent_end = parsed[parent.period_id]
                if item_start < parent_start or item_end > parent_end:
                    raise ValueError("nested Dasha period must remain within its parent")
        groups: dict[tuple[str, str | None], list[DashaPeriod]] = {}
        for item in self.periods:
            groups.setdefault((item.level, item.parent_id), []).append(item)
        for siblings in groups.values():
            chronological = sorted(siblings, key=lambda item: (*parsed[item.period_id], item.period_id))
            ordered = sorted(siblings, key=lambda item: (item.order, item.period_id))
            if tuple(item.period_id for item in ordered) != tuple(
                item.period_id for item in chronological
            ):
                raise ValueError("Dasha sibling periods must use chronological order")
            for previous, current in zip(chronological, chronological[1:]):
                if parsed[current.period_id][0] < parsed[previous.period_id][1]:
                    raise ValueError("Dasha sibling periods cannot overlap")
        for name, level in (
            ("active_mahadasha_id", "mahadasha"),
            ("active_antardasha_id", "antardasha"),
            ("active_pratyantardasha_id", "pratyantardasha"),
        ):
            value = getattr(self, name)
            if value is not None and (value not in by_id or by_id[value].level != level):
                raise ValueError(f"{name} does not resolve to a supplied {level}")
        active_ids = tuple(
            value for value in (
                self.active_mahadasha_id,
                self.active_antardasha_id,
                self.active_pratyantardasha_id,
            ) if value is not None
        )
        if self.active_antardasha_id is not None and self.active_mahadasha_id is None:
            raise ValueError("active antardasha requires an active mahadasha")
        if self.active_pratyantardasha_id is not None and (
            self.active_mahadasha_id is None or self.active_antardasha_id is None
        ):
            raise ValueError("active pratyantardasha requires its active ancestors")
        if self.reference_instant is not None:
            instant = _utc("reference_instant", self.reference_instant)
            if any(not (parsed[value][0] <= instant < parsed[value][1]) for value in active_ids):
                raise ValueError("active Dasha period does not contain reference instant")
        for parent_id, child_id in zip(active_ids, active_ids[1:]):
            if by_id[child_id].parent_id != parent_id:
                raise ValueError("active Dasha hierarchy is inconsistent")
        active = self.status in (TimingOutputStatus.AVAILABLE, TimingOutputStatus.PARTIAL)
        if active:
            if self.reference_instant is None or not self.periods or self.calculation_version is None:
                raise ValueError("available/partial Dasha requires instant, periods, and calculation version")
            if self.status is TimingOutputStatus.PARTIAL and not self.issues:
                raise ValueError("partial Dasha requires typed issues")
        else:
            if self.periods or any((
                self.active_mahadasha_id,
                self.active_antardasha_id,
                self.active_pratyantardasha_id,
                self.calculation_version,
            )):
                raise ValueError("unavailable/not-requested/failed Dasha must be empty")
            if self.status in (TimingOutputStatus.UNAVAILABLE, TimingOutputStatus.FAILED) and not self.issues:
                raise ValueError("unavailable/failed Dasha requires a typed issue")


@dataclass(frozen=True, slots=True, kw_only=True)
class TransitPosition:
    body_id: str
    longitude_degrees: float
    sign_id: str
    source_fact_id: str
    order: int

    def __post_init__(self) -> None:
        for name in ("body_id", "sign_id", "source_fact_id"):
            _identity(name, getattr(self, name))
        object.__setattr__(
            self,
            "longitude_degrees",
            _finite("longitude_degrees", self.longitude_degrees, lower=0.0),
        )
        if self.longitude_degrees >= 360.0:
            raise ValueError("longitude_degrees must be less than 360")
        _order("order", self.order)


@dataclass(frozen=True, slots=True, kw_only=True)
class TransitRelationship:
    relationship_id: str
    source_body_id: str
    natal_target_id: str
    relationship_type: str
    source_fact_ids: tuple[str, ...]
    order: int

    def __post_init__(self) -> None:
        for name in (
            "relationship_id", "source_body_id", "natal_target_id",
            "relationship_type",
        ):
            _identity(name, getattr(self, name))
        _strings("source_fact_ids", self.source_fact_ids, sorted_unique=True, nonempty=True)
        _order("order", self.order)


_TRANSIT_PRODUCER_FACTORY_TOKEN = object()


@dataclass(frozen=True, slots=True, kw_only=True)
class TransitProducerEvidence:
    capability: CapabilityInspection
    positions: tuple[TransitPosition, ...]
    natal_target_references: tuple[EvidenceReference, ...]
    rule_matches: tuple[RuleMatch, ...]
    domain_effect_results: tuple[InferenceResult, ...]
    producer_version: str
    producer_schema_version: str
    trace_id: str
    logical_digest: str = ""
    _factory_token: InitVar[object | None] = None

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _TRANSIT_PRODUCER_FACTORY_TOKEN:
            raise ValueError(
                "transit producer evidence requires the validated producer factory"
            )
        if not isinstance(self.capability, CapabilityInspection):
            raise TypeError("capability must be CapabilityInspection")
        if (
            self.capability.capability_id != "transits.current"
            or self.capability.expected_version != self.producer_schema_version
            or self.capability.observed_version != self.producer_schema_version
            or self.capability.source_kind != "transit_producer"
            or self.capability.readiness
            not in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY)
        ):
            raise ValueError("transit producer capability is not authoritative")
        _tuple_of("positions", self.positions, TransitPosition)
        _tuple_of(
            "natal_target_references",
            self.natal_target_references,
            EvidenceReference,
        )
        _tuple_of("rule_matches", self.rule_matches, RuleMatch)
        _tuple_of("domain_effect_results", self.domain_effect_results, InferenceResult)
        for name in ("producer_version", "producer_schema_version", "trace_id"):
            _identity(name, getattr(self, name))
        if self.capability.content_empty is not (not self.positions):
            raise ValueError("transit producer readiness does not reconcile to positions")
        if len({item.source_fact_id for item in self.positions}) != len(self.positions):
            raise ValueError("transit producer positions require unique factual identities")
        if len({item.source_id for item in self.natal_target_references}) != len(
            self.natal_target_references
        ):
            raise ValueError("transit producer natal targets require unique identities")
        if len({item.rule_id for item in self.rule_matches}) != len(self.rule_matches):
            raise ValueError("transit producer RuleMatches require unique identities")
        if len({item.trace_id for item in self.domain_effect_results}) != len(
            self.domain_effect_results
        ):
            raise ValueError("transit producer domain results require unique traces")
        _set_or_validate_digest(self)


def _build_transit_producer_evidence(
    *,
    capability: CapabilityInspection,
    positions: tuple[TransitPosition, ...],
    natal_target_references: tuple[EvidenceReference, ...],
    rule_matches: tuple[RuleMatch, ...],
    domain_effect_results: tuple[InferenceResult, ...],
    producer_version: str,
    producer_schema_version: str,
    trace_id: str,
    logical_digest: str = "",
) -> TransitProducerEvidence:
    """Internal constructor reached only from validated producer boundaries."""

    return TransitProducerEvidence(
        capability=capability,
        positions=positions,
        natal_target_references=natal_target_references,
        rule_matches=rule_matches,
        domain_effect_results=domain_effect_results,
        producer_version=producer_version,
        producer_schema_version=producer_schema_version,
        trace_id=trace_id,
        logical_digest=logical_digest,
        _factory_token=_TRANSIT_PRODUCER_FACTORY_TOKEN,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class TransitSummary:
    transit_summary_schema_version: str
    status: TimingOutputStatus
    reference_instant: str | None
    positions: tuple[TransitPosition, ...]
    natal_relationships: tuple[TransitRelationship, ...]
    active_rule_match_ids: tuple[str, ...]
    domain_effect_trace_ids: tuple[str, ...]
    producer_evidence: TransitProducerEvidence | None
    calculation_version: str | None
    issues: tuple[DomainIssue, ...]
    trace_id: str
    logical_digest: str = ""

    def __post_init__(self) -> None:
        _schema_version("transit_summary_schema_version", self.transit_summary_schema_version)
        if not isinstance(self.status, TimingOutputStatus):
            raise TypeError("status must be TimingOutputStatus")
        if self.reference_instant is not None:
            _utc("reference_instant", self.reference_instant)
        _tuple_of("positions", self.positions, TransitPosition)
        _tuple_of("natal_relationships", self.natal_relationships, TransitRelationship)
        _strings("active_rule_match_ids", self.active_rule_match_ids, sorted_unique=True)
        _strings("domain_effect_trace_ids", self.domain_effect_trace_ids, sorted_unique=True)
        if self.producer_evidence is not None and not isinstance(
            self.producer_evidence, TransitProducerEvidence
        ):
            raise TypeError("producer_evidence must be TransitProducerEvidence or None")
        _identity("calculation_version", self.calculation_version, optional=True)
        _tuple_of("issues", self.issues, DomainIssue)
        _identity("trace_id", self.trace_id)
        self._validate_relationships_and_status()
        _set_or_validate_digest(self)

    def _validate_relationships_and_status(self) -> None:
        if self.status in (TimingOutputStatus.AVAILABLE, TimingOutputStatus.PARTIAL):
            raise ValueError(
                "transit capability is unavailable because no authoritative producer is installed"
            )
        body_ids = tuple(item.body_id for item in self.positions)
        relationship_ids = tuple(item.relationship_id for item in self.natal_relationships)
        if len(set(body_ids)) != len(body_ids) or len(set(relationship_ids)) != len(relationship_ids):
            raise ValueError("transit position/relationship identities must be unique")
        if tuple(sorted(self.positions, key=lambda item: (item.order, item.body_id))) != self.positions:
            raise ValueError("transit positions use non-canonical order")
        if tuple(sorted(self.natal_relationships, key=lambda item: (item.order, item.relationship_id))) != self.natal_relationships:
            raise ValueError("transit relationships use non-canonical order")
        position_fact_ids = {item.source_fact_id for item in self.positions}
        producer = self.producer_evidence
        producer_positions = () if producer is None else producer.positions
        producer_fact_ids = {item.source_fact_id for item in producer_positions}
        producer_target_ids = (
            set()
            if producer is None
            else {item.source_id for item in producer.natal_target_references}
        )
        producer_rule_ids = (
            set() if producer is None else {item.rule_id for item in producer.rule_matches}
        )
        producer_domain_trace_ids = (
            set()
            if producer is None
            else {item.trace_id for item in producer.domain_effect_results}
        )
        for item in self.natal_relationships:
            if item.source_body_id not in body_ids or not set(item.source_fact_ids).issubset(position_fact_ids):
                raise ValueError("transit relationship has unresolved position/fact references")
            if producer is None or item.natal_target_id not in producer_target_ids:
                raise ValueError("transit relationship has unresolved natal target reference")
        if producer is not None:
            if self.positions != producer_positions or position_fact_ids != producer_fact_ids:
                raise ValueError("transit positions do not reconcile to producer output")
            if not set(self.active_rule_match_ids).issubset(producer_rule_ids):
                raise ValueError("transit has unresolved producer rule reference")
            if not set(self.domain_effect_trace_ids).issubset(
                producer_domain_trace_ids
            ):
                raise ValueError("transit has unresolved producer domain trace reference")
        active = self.status in (TimingOutputStatus.AVAILABLE, TimingOutputStatus.PARTIAL)
        if active:
            if self.reference_instant is None or self.calculation_version is None:
                raise ValueError("available/partial transit requires instant and calculation version")
            if producer is None:
                raise ValueError("available/partial transit requires producer evidence")
            if self.status is TimingOutputStatus.AVAILABLE:
                expected = (
                    CapabilityReadiness.READY
                    if self.positions
                    else CapabilityReadiness.READY_EMPTY
                )
                if producer.capability.readiness is not expected:
                    raise ValueError("transit readiness does not reconcile to supplied positions")
            elif producer.capability.readiness is not CapabilityReadiness.READY:
                raise ValueError("partial transit requires nonempty producer output")
            if self.status is TimingOutputStatus.PARTIAL and not self.issues:
                raise ValueError("partial transit requires typed issues")
        else:
            if any((
                self.positions,
                self.natal_relationships,
                self.active_rule_match_ids,
                self.domain_effect_trace_ids,
                self.producer_evidence,
                self.calculation_version,
            )):
                raise ValueError("unavailable/not-requested/failed transit must be empty")
            if self.status in (TimingOutputStatus.UNAVAILABLE, TimingOutputStatus.FAILED) and not self.issues:
                raise ValueError("unavailable/failed transit requires a typed issue")


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainBuildProduced:
    prediction: DomainPrediction

    def __post_init__(self) -> None:
        if not isinstance(self.prediction, DomainPrediction):
            raise TypeError("prediction must be DomainPrediction")


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainBuildRejected:
    domain: DomainId
    issues: tuple[DomainIssue, ...]
    trace_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.domain, DomainId):
            raise TypeError("domain must be DomainId")
        _tuple_of("issues", self.issues, DomainIssue, nonempty=True)
        _identity("trace_id", self.trace_id)


DomainBuildOutcome = DomainBuildProduced | DomainBuildRejected


_TOP_LEVEL = (DomainPrediction, YogaDiagnostic, DashaTimeline, TransitSummary)


def _enum(value: Any) -> Any:
    return value.value if isinstance(value, Enum) else value


def _logical_value(value: Any, *, include_digest: bool) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, FrozenMapping):
        return canonical_json_data(value)
    if isinstance(value, Mapping):
        return canonical_json_data(value)
    if isinstance(value, tuple):
        return [_logical_value(item, include_digest=include_digest) for item in value]
    if isinstance(value, RuleMatch):
        return canonical_json_data(rule_match_to_logical_data(value))
    if isinstance(value, InferenceResult):
        return inference_model_to_logical_data(value)
    if isinstance(value, (EvidenceReference, ConflictRecord, DataCompleteness)):
        return inference_model_to_logical_data(value)
    if isinstance(value, CapabilityInspection):
        return {
            item.name: _logical_value(
                getattr(value, item.name), include_digest=include_digest
            )
            for item in fields(value)
        }
    if isinstance(value, DomainIssue):
        return {
            item.name: _logical_value(getattr(value, item.name), include_digest=include_digest)
            for item in fields(value)
        }
    if isinstance(value, (
        CompatibilityScalar, CompatibilitySequence, CompatibilityEntry,
        CompatibilityObject,
        CareerComponentCompatibility, CareerIndicatorCompatibility,
        CareerCompatibilityProjection, YogaCompatibilityProjection,
        DomainComponent, DomainIndicator, NarrativeSection, DomainTimingReference,
        DashaPeriod, TransitPosition, TransitRelationship, TransitProducerEvidence,
    )):
        return {
            item.name: _logical_value(getattr(value, item.name), include_digest=include_digest)
            for item in fields(value)
            if item.name != "logical_digest" or include_digest
        }
    if isinstance(value, _TOP_LEVEL):
        data = {}
        for item in fields(value):
            if item.name in {
                "source_inference_result",
                "source_inference_compatibility",
                "source_evaluation_batch",
                "source_authority",
                "source_evaluation_record",
            }:
                continue
            if item.name == "logical_digest" and not include_digest:
                continue
            data[item.name] = _logical_value(
                getattr(value, item.name), include_digest=include_digest
            )
        return data
    return value


def prompt05_model_to_logical_data(value: Any) -> dict[str, Any]:
    """Return a fresh canonical JSON-safe projection including its digest."""

    if not isinstance(value, _TOP_LEVEL):
        raise TypeError("value must be a top-level Prompt-05 model")
    return canonical_json_data(_logical_value(value, include_digest=True))


def prompt05_model_logical_json_bytes(value: Any) -> bytes:
    return canonical_json_bytes(prompt05_model_to_logical_data(value))


def prompt05_model_logical_sha256(value: Any) -> str:
    if not isinstance(value, _TOP_LEVEL):
        raise TypeError("value must be a top-level Prompt-05 model")
    return value.logical_digest


def _expected_digest(value: Any) -> str:
    return hashlib.sha256(
        canonical_json_bytes(_logical_value(value, include_digest=False))
    ).hexdigest()


def _set_or_validate_digest(value: Any) -> None:
    supplied = value.logical_digest
    expected = _expected_digest(value)
    if supplied:
        if not isinstance(supplied, str) or not _SHA256.fullmatch(supplied):
            raise ValueError("logical_digest must be lowercase SHA-256")
        if supplied != expected:
            raise ValueError("logical_digest does not match canonical logical content")
    object.__setattr__(value, "logical_digest", expected)


def _strict_json(payload: str | bytes) -> Any:
    if isinstance(payload, bytes):
        try:
            payload = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CanonicalValueError("malformed Prompt-05 UTF-8") from exc
    if not isinstance(payload, str):
        raise TypeError("Prompt-05 JSON must be text or bytes")

    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in values:
            if key in result:
                raise CanonicalValueError("duplicate Prompt-05 JSON key")
            result[key] = item
        return result

    try:
        return json.loads(
            payload,
            object_pairs_hook=pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                CanonicalValueError(f"nonfinite JSON constant: {value}")
            ),
        )
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise CanonicalValueError("malformed Prompt-05 JSON") from exc


T = TypeVar("T")


def _keys(data: Any, kind: type[T], *, exclude: tuple[str, ...] = ()) -> Mapping[str, Any]:
    expected = {item.name for item in fields(kind)} - set(exclude)
    if not isinstance(data, Mapping) or set(data) != expected:
        raise CanonicalValueError(f"invalid {kind.__name__} fields")
    return data


def _issue_from_data(data: Any) -> DomainIssue:
    value = _keys(data, DomainIssue)
    return DomainIssue(
        **{
            **value,
            "severity": DomainIssueSeverity(value["severity"]),
        }
    )


def _evidence_from_data(data: Any) -> EvidenceReference:
    value = _keys(data, EvidenceReference)
    return EvidenceReference(**value)


def _career_component_compatibility_from_data(data: Any) -> CareerComponentCompatibility:
    value = _keys(data, CareerComponentCompatibility)
    return CareerComponentCompatibility(
        **{
            **value,
            "kind": CareerComponentKind(value["kind"]),
            "occupants": tuple(value["occupants"]),
            "source_fact_trace_ids": tuple(value["source_fact_trace_ids"]),
        }
    )


def _career_indicator_compatibility_from_data(data: Any) -> CareerIndicatorCompatibility:
    value = _keys(data, CareerIndicatorCompatibility)
    return CareerIndicatorCompatibility(
        **{
            **value,
            "context": _compatibility_value_from_data(value["context"], CompatibilityObject),
            "evidence": _compatibility_value_from_data(value["evidence"], CompatibilityObject),
        }
    )


def _compatibility_value_from_data(
    data: Any,
    expected: type[CompatibilityValue] | None = None,
) -> CompatibilityValue:
    if isinstance(data, Mapping) and set(data) == {"entries"}:
        entries = tuple(
            CompatibilityEntry(
                key=_keys(item, CompatibilityEntry)["key"],
                value=_compatibility_value_from_data(
                    _keys(item, CompatibilityEntry)["value"]
                ),
            )
            for item in data["entries"]
        )
        result: CompatibilityValue = CompatibilityObject(entries=entries)
    elif isinstance(data, Mapping) and set(data) == {"items"}:
        result = CompatibilitySequence(items=tuple(
            _compatibility_value_from_data(item) for item in data["items"]
        ))
    elif isinstance(data, Mapping) and set(data) == {"value"}:
        result = CompatibilityScalar(value=data["value"])
    else:
        raise CanonicalValueError("invalid typed compatibility value")
    if expected is not None and not isinstance(result, expected):
        raise CanonicalValueError("typed compatibility value has the wrong kind")
    return result


def _career_compatibility_from_data(data: Any) -> CareerCompatibilityProjection:
    value = _keys(data, CareerCompatibilityProjection)
    return CareerCompatibilityProjection(
        **{
            **value,
            "components": tuple(
                _career_component_compatibility_from_data(item)
                for item in value["components"]
            ),
            "indicators": tuple(
                _career_indicator_compatibility_from_data(item)
                for item in value["indicators"]
            ),
        }
    )


def _yoga_compatibility_from_data(data: Any) -> YogaCompatibilityProjection:
    value = _keys(data, YogaCompatibilityProjection)
    return _build_yoga_compatibility_projection(
        **{**value, "houses": tuple(value["houses"])}
    )


def _component_from_data(data: Any) -> DomainComponent:
    value = _keys(data, DomainComponent)
    return DomainComponent(
        **{
            **value,
            "domain": DomainId(value["domain"]),
            "contribution_ids": tuple(value["contribution_ids"]),
            "contributing_rule_ids": tuple(value["contributing_rule_ids"]),
            "evidence_references": tuple(_evidence_from_data(item) for item in value["evidence_references"]),
        }
    )


def _indicator_from_data(data: Any) -> DomainIndicator:
    value = _keys(data, DomainIndicator)
    return DomainIndicator(
        **{
            **value,
            "domain": DomainId(value["domain"]),
            "direction": ContributionSign(value["direction"]),
            "evidence_references": tuple(_evidence_from_data(item) for item in value["evidence_references"]),
            "source_rule_match": rule_match_from_logical_data(
                value["source_rule_match"]
            ),
        }
    )


def _narrative_from_data(data: Any) -> NarrativeSection:
    value = _keys(data, NarrativeSection)
    return NarrativeSection(
        **{
            **value,
            "section_type": NarrativeSectionType(value["section_type"]),
            "source_rule_ids": tuple(value["source_rule_ids"]),
            "source_indicator_ids": tuple(value["source_indicator_ids"]),
            "source_issue_ids": tuple(value["source_issue_ids"]),
            "source_trace_ids": tuple(value["source_trace_ids"]),
        }
    )


def _timing_reference_from_data(data: Any) -> DomainTimingReference:
    value = _keys(data, DomainTimingReference)
    return DomainTimingReference(
        **{
            **value,
            "status": CapabilityAvailability(value["status"]),
            "source_rule_ids": tuple(value["source_rule_ids"]),
            "source_trace_ids": tuple(value["source_trace_ids"]),
            "issues": tuple(_issue_from_data(item) for item in value["issues"]),
        }
    )


def domain_prediction_from_logical_data(
    data: Any,
    *,
    source_inference_result: InferenceResult | None = None,
    source_inference_compatibility: InferenceCompatibilityProjection | None = None,
    source_evaluation_batch: Any | None = None,
) -> DomainPrediction:
    raise CanonicalValueError(
        "DomainPrediction dictionaries are one-way presentation DTOs"
    )


def domain_prediction_from_logical_json(
    payload: str | bytes,
    *,
    source_inference_result: InferenceResult | None = None,
    source_inference_compatibility: InferenceCompatibilityProjection | None = None,
    source_evaluation_batch: Any | None = None,
) -> DomainPrediction:
    return domain_prediction_from_logical_data(
        _strict_json(payload),
        source_inference_result=source_inference_result,
        source_inference_compatibility=source_inference_compatibility,
        source_evaluation_batch=source_evaluation_batch,
    )


def yoga_diagnostic_from_logical_data(
    data: Any,
    *,
    source_evaluation_record: Any | None = None,
) -> YogaDiagnostic:
    raise CanonicalValueError(
        "YogaDiagnostic dictionaries are one-way presentation DTOs"
    )


def yoga_diagnostic_from_logical_json(
    payload: str | bytes,
    *,
    source_evaluation_record: Any | None = None,
) -> YogaDiagnostic:
    return yoga_diagnostic_from_logical_data(
        _strict_json(payload), source_evaluation_record=source_evaluation_record
    )


def _period_from_data(data: Any) -> DashaPeriod:
    return DashaPeriod(**_keys(data, DashaPeriod))


def dasha_timeline_from_logical_data(data: Any) -> DashaTimeline:
    value = _keys(data, DashaTimeline)
    return DashaTimeline(
        **{
            **value,
            "status": TimingOutputStatus(value["status"]),
            "periods": tuple(_period_from_data(item) for item in value["periods"]),
            "issues": tuple(_issue_from_data(item) for item in value["issues"]),
        }
    )


def dasha_timeline_from_logical_json(payload: str | bytes) -> DashaTimeline:
    return dasha_timeline_from_logical_data(_strict_json(payload))


def _position_from_data(data: Any) -> TransitPosition:
    return TransitPosition(**_keys(data, TransitPosition))


def _relationship_from_data(data: Any) -> TransitRelationship:
    value = _keys(data, TransitRelationship)
    return TransitRelationship(**{**value, "source_fact_ids": tuple(value["source_fact_ids"])})


def _transit_producer_from_data(data: Any) -> TransitProducerEvidence:
    value = _keys(data, TransitProducerEvidence)
    capability = _keys(value["capability"], CapabilityInspection)
    return _build_transit_producer_evidence(
        **{
            **value,
            "capability": CapabilityInspection(
                **{
                    **capability,
                    "readiness": CapabilityReadiness(capability["readiness"]),
                    "issues": tuple(capability["issues"]),
                }
            ),
            "positions": tuple(_position_from_data(item) for item in value["positions"]),
            "natal_target_references": tuple(
                _evidence_from_data(item) for item in value["natal_target_references"]
            ),
            "rule_matches": tuple(
                rule_match_from_logical_data(item) for item in value["rule_matches"]
            ),
            "domain_effect_results": tuple(
                inference_result_from_logical_data(item)
                for item in value["domain_effect_results"]
            ),
        }
    )


def transit_summary_from_logical_data(data: Any) -> TransitSummary:
    value = _keys(data, TransitSummary)
    return TransitSummary(
        **{
            **value,
            "status": TimingOutputStatus(value["status"]),
            "positions": tuple(_position_from_data(item) for item in value["positions"]),
            "natal_relationships": tuple(_relationship_from_data(item) for item in value["natal_relationships"]),
            "active_rule_match_ids": tuple(value["active_rule_match_ids"]),
            "domain_effect_trace_ids": tuple(value["domain_effect_trace_ids"]),
            "producer_evidence": (
                None
                if value["producer_evidence"] is None
                else _transit_producer_from_data(value["producer_evidence"])
            ),
            "issues": tuple(_issue_from_data(item) for item in value["issues"]),
        }
    )


def transit_summary_from_logical_json(payload: str | bytes) -> TransitSummary:
    return transit_summary_from_logical_data(_strict_json(payload))


__all__ = (
    "DASHA_TIMELINE_SCHEMA_VERSION",
    "DOMAIN_ORDER",
    "DOMAIN_PREDICTION_SCHEMA_VERSION",
    "TRANSIT_SUMMARY_SCHEMA_VERSION",
    "YOGA_DIAGNOSTIC_SCHEMA_VERSION",
    "DashaPeriod",
    "DashaTimeline",
    "CareerCompatibilityProjection",
    "CareerComponentCompatibility",
    "CareerComponentKind",
    "CareerIndicatorCompatibility",
    "CompatibilityEntry",
    "CompatibilityObject",
    "CompatibilityScalar",
    "CompatibilitySequence",
    "CompatibilityValue",
    "DomainBuildOutcome",
    "DomainBuildProduced",
    "DomainBuildRejected",
    "DomainComponent",
    "DomainId",
    "DomainIndicator",
    "DomainIssue",
    "DomainIssueSeverity",
    "DomainPrediction",
    "DomainStatus",
    "DomainTimingReference",
    "NarrativeSection",
    "NarrativeSectionType",
    "TimingOutputStatus",
    "TimingProducerReadiness",
    "TransitPosition",
    "TransitProducerEvidence",
    "TransitRelationship",
    "TransitSummary",
    "YogaDiagnostic",
    "YogaCompatibilityProjection",
    "compatibility_value",
    "compatibility_value_to_python",
    "dasha_timeline_from_logical_data",
    "dasha_timeline_from_logical_json",
    "prompt05_model_logical_json_bytes",
    "prompt05_model_logical_sha256",
    "prompt05_model_to_logical_data",
    "transit_summary_from_logical_data",
    "transit_summary_from_logical_json",
)
