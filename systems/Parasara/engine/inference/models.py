"""Immutable generic inference contracts and canonical serialization."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
from numbers import Real
from typing import Any

from systems.Parasara.engine.rules.canonical import (
    CanonicalValueError,
    FrozenMapping,
    canonical_json_bytes,
    freeze_canonical,
)


INFERENCE_SCHEMA_VERSION = "1.0.0"


class InferenceStatus(str, Enum):
    EVALUATED = "evaluated"
    PARTIAL = "partial"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    FAILED = "failed"


class ContributionSign(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class ConflictSide(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    TIED = "tied"
    NONE = "none"


class CapabilityAvailability(str, Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    NOT_REQUIRED = "not_required"


def _text(name: str, value: Any, *, optional: bool = False) -> None:
    if optional and value is None:
        return
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")


def _finite(name: str, value: Any, *, lower: float | None = None, upper: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise TypeError(f"{name} must be finite numeric")
    result = float(value)
    if lower is not None and result < lower:
        raise ValueError(f"{name} must be >= {lower}")
    if upper is not None and result > upper:
        raise ValueError(f"{name} must be <= {upper}")
    return 0.0 if result == 0.0 else result


def _strings(name: str, value: Any, *, sorted_unique: bool = False) -> tuple[str, ...]:
    if not isinstance(value, tuple) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise TypeError(f"{name} must be an immutable tuple of nonempty strings")
    if sorted_unique and tuple(sorted(set(value))) != value:
        raise ValueError(f"{name} must be unique and sorted")
    return value


def _mapping(name: str, value: Any) -> FrozenMapping:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    frozen = freeze_canonical(value, path=f"$.{name}")
    if not isinstance(frozen, FrozenMapping):
        raise TypeError(f"{name} must be a mapping")
    return frozen


@dataclass(frozen=True, slots=True, kw_only=True)
class InferenceError:
    code: str
    message: str
    phase: str
    recoverable: bool
    details: Mapping[str, Any] = field(default_factory=dict)
    source_rule_id: str | None = None
    source_trace_id: str | None = None

    def __post_init__(self) -> None:
        for name in ("code", "message", "phase"):
            _text(name, getattr(self, name))
        if type(self.recoverable) is not bool:
            raise TypeError("recoverable must be a Boolean")
        _text("source_rule_id", self.source_rule_id, optional=True)
        _text("source_trace_id", self.source_trace_id, optional=True)
        object.__setattr__(self, "details", _mapping("details", self.details))


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceReference:
    evidence_id: str
    source_type: str
    source_id: str
    trace_id: str | None
    correlation_key: str
    order: int

    def __post_init__(self) -> None:
        for name in ("evidence_id", "source_type", "source_id", "correlation_key"):
            _text(name, getattr(self, name))
        _text("trace_id", self.trace_id, optional=True)
        if type(self.order) is not int or self.order < 0:
            raise ValueError("order must be a nonnegative integer")


@dataclass(frozen=True, slots=True, kw_only=True)
class Contribution:
    contribution_id: str
    rule_id: str
    rule_version: str
    rule_set_version: str
    domain: str
    category: str
    context: str
    sign: ContributionSign
    base_weight: float
    rule_quality: float
    evidence_strength: float
    context_multiplier: float
    priority_multiplier: float
    final_contribution: float
    priority: int
    evidence_references: tuple[EvidenceReference, ...]
    correlation_keys: tuple[str, ...]
    source_rule_trace_id: str
    trace_id: str

    def __post_init__(self) -> None:
        for name in (
            "contribution_id", "rule_id", "rule_version", "rule_set_version", "domain",
            "category", "context", "source_rule_trace_id", "trace_id",
        ):
            _text(name, getattr(self, name))
        if not isinstance(self.sign, ContributionSign):
            raise TypeError("sign must be ContributionSign")
        for name in ("base_weight", "context_multiplier", "priority_multiplier", "final_contribution"):
            object.__setattr__(self, name, _finite(name, getattr(self, name)))
        for name in ("rule_quality", "evidence_strength"):
            object.__setattr__(self, name, _finite(name, getattr(self, name), lower=0.0, upper=1.0))
        if type(self.priority) is not int:
            raise TypeError("priority must be an integer")
        if not isinstance(self.evidence_references, tuple) or not self.evidence_references or any(
            not isinstance(item, EvidenceReference) for item in self.evidence_references
        ):
            raise ValueError("each contribution requires immutable evidence references")
        _strings("correlation_keys", self.correlation_keys, sorted_unique=True)


@dataclass(frozen=True, slots=True, kw_only=True)
class ConflictRecord:
    conflict_id: str
    domain: str
    positive_rule_ids: tuple[str, ...]
    negative_rule_ids: tuple[str, ...]
    highest_priority: int
    resolution_method: str
    winning_side: ConflictSide
    unresolved: bool
    confidence_impact: float
    rationale_code: str
    trace_id: str

    def __post_init__(self) -> None:
        for name in ("conflict_id", "domain", "resolution_method", "rationale_code", "trace_id"):
            _text(name, getattr(self, name))
        _strings("positive_rule_ids", self.positive_rule_ids, sorted_unique=True)
        _strings("negative_rule_ids", self.negative_rule_ids, sorted_unique=True)
        if not self.positive_rule_ids or not self.negative_rule_ids:
            raise ValueError("a conflict requires positive and negative rules")
        if type(self.highest_priority) is not int:
            raise TypeError("highest_priority must be an integer")
        if not isinstance(self.winning_side, ConflictSide):
            raise TypeError("winning_side must be ConflictSide")
        if type(self.unresolved) is not bool:
            raise TypeError("unresolved must be a Boolean")
        object.__setattr__(self, "confidence_impact", _finite("confidence_impact", self.confidence_impact, lower=0.0, upper=1.0))


@dataclass(frozen=True, slots=True, kw_only=True)
class InferenceComponent:
    component_id: str
    domain: str
    category: str
    raw_contribution: float
    normalized_value: float
    contribution_ids: tuple[str, ...]
    rule_ids: tuple[str, ...]
    evidence_references: tuple[EvidenceReference, ...]
    trace_id: str

    def __post_init__(self) -> None:
        for name in ("component_id", "domain", "category", "trace_id"):
            _text(name, getattr(self, name))
        object.__setattr__(self, "raw_contribution", _finite("raw_contribution", self.raw_contribution))
        object.__setattr__(self, "normalized_value", _finite("normalized_value", self.normalized_value, lower=0.0, upper=1.0))
        _strings("contribution_ids", self.contribution_ids)
        _strings("rule_ids", self.rule_ids)
        if not isinstance(self.evidence_references, tuple) or any(not isinstance(item, EvidenceReference) for item in self.evidence_references):
            raise TypeError("evidence_references must be an immutable tuple")


@dataclass(frozen=True, slots=True, kw_only=True)
class ExplanationFactor:
    factor_id: str
    factor_type: str
    direction: ContributionSign
    magnitude: float
    source_rule_ids: tuple[str, ...]
    evidence_references: tuple[EvidenceReference, ...]
    trace_id: str

    def __post_init__(self) -> None:
        for name in ("factor_id", "factor_type", "trace_id"):
            _text(name, getattr(self, name))
        if not isinstance(self.direction, ContributionSign):
            raise TypeError("direction must be ContributionSign")
        object.__setattr__(self, "magnitude", _finite("magnitude", self.magnitude, lower=0.0))
        _strings("source_rule_ids", self.source_rule_ids, sorted_unique=True)
        if not isinstance(self.evidence_references, tuple) or any(not isinstance(item, EvidenceReference) for item in self.evidence_references):
            raise TypeError("evidence_references must be an immutable tuple")


_CAPABILITY_FIELDS = (
    "d1", "d9", "d10", "aspects", "functional_roles", "shadbala",
    "dasha", "transits", "rule_pack",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class DataCompleteness:
    domain: str
    d1: CapabilityAvailability
    d9: CapabilityAvailability
    d10: CapabilityAvailability
    aspects: CapabilityAvailability
    functional_roles: CapabilityAvailability
    shadbala: CapabilityAvailability
    dasha: CapabilityAvailability
    transits: CapabilityAvailability
    rule_pack: CapabilityAvailability
    required_capabilities: tuple[str, ...]
    missing_required: tuple[str, ...]
    missing_optional: tuple[str, ...]
    completeness_score: float
    trace_id: str

    def __post_init__(self) -> None:
        _text("domain", self.domain)
        _text("trace_id", self.trace_id)
        for name in _CAPABILITY_FIELDS:
            if not isinstance(getattr(self, name), CapabilityAvailability):
                raise TypeError(f"{name} must be CapabilityAvailability")
        for name in ("required_capabilities", "missing_required", "missing_optional"):
            _strings(name, getattr(self, name), sorted_unique=True)
            if any(item not in _CAPABILITY_FIELDS for item in getattr(self, name)):
                raise ValueError(f"{name} contains an unknown capability")
        if not set(self.missing_required).issubset(self.required_capabilities):
            raise ValueError("missing_required must be a subset of required_capabilities")
        if set(self.missing_optional) & set(self.required_capabilities):
            raise ValueError("missing_optional cannot contain required capabilities")
        for name in (*self.missing_required, *self.missing_optional):
            if getattr(self, name) in (CapabilityAvailability.AVAILABLE, CapabilityAvailability.NOT_REQUIRED):
                raise ValueError("missing capability lists disagree with availability")
        object.__setattr__(self, "completeness_score", _finite("completeness_score", self.completeness_score, lower=0.0, upper=1.0))


@dataclass(frozen=True, slots=True, kw_only=True)
class TimingContext:
    context_id: str
    context_version: str
    multipliers: Mapping[str, Any] = field(default_factory=dict)
    trace_id: str = "timing.none"

    def __post_init__(self) -> None:
        for name in ("context_id", "context_version", "trace_id"):
            _text(name, getattr(self, name))
        object.__setattr__(self, "multipliers", _mapping("multipliers", self.multipliers))


@dataclass(frozen=True, slots=True, kw_only=True)
class InferenceResult:
    inference_schema_version: str
    inference_version: str
    system: str
    rule_set_version: str
    domain: str
    status: InferenceStatus
    raw_score: float
    normalized_score: float
    confidence: float
    agreement: float
    positive_contributions: tuple[Contribution, ...]
    negative_contributions: tuple[Contribution, ...]
    neutral_contributions: tuple[Contribution, ...]
    mixed_contributions: tuple[Contribution, ...]
    components: tuple[InferenceComponent, ...]
    conflicts: tuple[ConflictRecord, ...]
    data_completeness: DataCompleteness
    explanation_factors: tuple[ExplanationFactor, ...]
    excluded_rule_ids: tuple[str, ...]
    unavailable_rule_ids: tuple[str, ...]
    errors: tuple[InferenceError, ...]
    trace_id: str

    def __post_init__(self) -> None:
        for name in ("inference_schema_version", "inference_version", "system", "rule_set_version", "domain", "trace_id"):
            _text(name, getattr(self, name))
        if not isinstance(self.status, InferenceStatus):
            raise TypeError("status must be InferenceStatus")
        object.__setattr__(self, "raw_score", _finite("raw_score", self.raw_score))
        for name in ("normalized_score", "confidence", "agreement"):
            object.__setattr__(self, name, _finite(name, getattr(self, name), lower=0.0, upper=1.0))
        for name in ("positive_contributions", "negative_contributions", "neutral_contributions", "mixed_contributions"):
            values = getattr(self, name)
            if not isinstance(values, tuple) or any(not isinstance(item, Contribution) for item in values):
                raise TypeError(f"{name} must be an immutable Contribution tuple")
        if not isinstance(self.components, tuple) or any(not isinstance(item, InferenceComponent) for item in self.components):
            raise TypeError("components must contain InferenceComponent values")
        if not isinstance(self.conflicts, tuple) or any(not isinstance(item, ConflictRecord) for item in self.conflicts):
            raise TypeError("conflicts must contain ConflictRecord values")
        if not isinstance(self.data_completeness, DataCompleteness):
            raise TypeError("data_completeness must be DataCompleteness")
        if not isinstance(self.explanation_factors, tuple) or any(not isinstance(item, ExplanationFactor) for item in self.explanation_factors):
            raise TypeError("explanation_factors must contain ExplanationFactor values")
        _strings("excluded_rule_ids", self.excluded_rule_ids, sorted_unique=True)
        _strings("unavailable_rule_ids", self.unavailable_rule_ids, sorted_unique=True)
        if not isinstance(self.errors, tuple) or any(not isinstance(item, InferenceError) for item in self.errors):
            raise TypeError("errors must contain InferenceError values")

    @property
    def contributions(self) -> tuple[Contribution, ...]:
        return (
            *self.positive_contributions,
            *self.negative_contributions,
            *self.neutral_contributions,
            *self.mixed_contributions,
        )


def _data(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, FrozenMapping):
        return {key: _data(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_data(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {name: _data(getattr(value, name)) for name in value.__dataclass_fields__}
    return value


_INFERENCE_MODEL_TYPES = (
    InferenceError, EvidenceReference, Contribution, ConflictRecord,
    InferenceComponent, ExplanationFactor, DataCompleteness, TimingContext,
    InferenceResult,
)


def inference_model_to_logical_data(value: Any) -> dict[str, Any]:
    """Canonically project any Prompt-03 inference value."""

    if not isinstance(value, _INFERENCE_MODEL_TYPES):
        raise TypeError("value must be a Prompt-03 inference model")
    return _data(value)


def inference_model_logical_json_bytes(value: Any) -> bytes:
    return canonical_json_bytes(inference_model_to_logical_data(value))


def inference_result_to_logical_data(value: InferenceResult) -> dict[str, Any]:
    if not isinstance(value, InferenceResult):
        raise TypeError("value must be InferenceResult")
    return inference_model_to_logical_data(value)


def inference_result_logical_json_bytes(value: InferenceResult) -> bytes:
    return canonical_json_bytes(inference_result_to_logical_data(value))


def inference_result_logical_sha256(value: InferenceResult) -> str:
    return hashlib.sha256(inference_result_logical_json_bytes(value)).hexdigest()


def _strict(value: Any, cls: type, **overrides: Any) -> Any:
    if not isinstance(value, Mapping) or set(value) != set(cls.__dataclass_fields__):
        raise CanonicalValueError(f"invalid {cls.__name__} fields")
    return cls(**{**value, **overrides})


def _evidence(value: Any) -> EvidenceReference:
    return _strict(value, EvidenceReference)


def _contribution(value: Any) -> Contribution:
    return _strict(
        value,
        Contribution,
        sign=ContributionSign(value["sign"]),
        evidence_references=tuple(_evidence(item) for item in value["evidence_references"]),
        correlation_keys=tuple(value["correlation_keys"]),
    )


def inference_result_from_logical_data(value: Any) -> InferenceResult:
    try:
        if not isinstance(value, Mapping) or set(value) != set(InferenceResult.__dataclass_fields__):
            raise CanonicalValueError("invalid InferenceResult fields")
        completeness = _strict(
            value["data_completeness"], DataCompleteness,
            **{name: CapabilityAvailability(value["data_completeness"][name]) for name in _CAPABILITY_FIELDS},
            required_capabilities=tuple(value["data_completeness"]["required_capabilities"]),
            missing_required=tuple(value["data_completeness"]["missing_required"]),
            missing_optional=tuple(value["data_completeness"]["missing_optional"]),
        )
        components = tuple(_strict(
            item, InferenceComponent,
            contribution_ids=tuple(item["contribution_ids"]), rule_ids=tuple(item["rule_ids"]),
            evidence_references=tuple(_evidence(ref) for ref in item["evidence_references"]),
        ) for item in value["components"])
        conflicts = tuple(_strict(
            item, ConflictRecord,
            positive_rule_ids=tuple(item["positive_rule_ids"]), negative_rule_ids=tuple(item["negative_rule_ids"]),
            winning_side=ConflictSide(item["winning_side"]),
        ) for item in value["conflicts"])
        factors = tuple(_strict(
            item, ExplanationFactor,
            direction=ContributionSign(item["direction"]), source_rule_ids=tuple(item["source_rule_ids"]),
            evidence_references=tuple(_evidence(ref) for ref in item["evidence_references"]),
        ) for item in value["explanation_factors"])
        errors = tuple(_strict(item, InferenceError) for item in value["errors"])
        return InferenceResult(
            inference_schema_version=value["inference_schema_version"],
            inference_version=value["inference_version"], system=value["system"],
            rule_set_version=value["rule_set_version"], domain=value["domain"],
            status=InferenceStatus(value["status"]), raw_score=value["raw_score"],
            normalized_score=value["normalized_score"], confidence=value["confidence"],
            agreement=value["agreement"],
            positive_contributions=tuple(_contribution(item) for item in value["positive_contributions"]),
            negative_contributions=tuple(_contribution(item) for item in value["negative_contributions"]),
            neutral_contributions=tuple(_contribution(item) for item in value["neutral_contributions"]),
            mixed_contributions=tuple(_contribution(item) for item in value["mixed_contributions"]),
            components=components, conflicts=conflicts, data_completeness=completeness,
            explanation_factors=factors, excluded_rule_ids=tuple(value["excluded_rule_ids"]),
            unavailable_rule_ids=tuple(value["unavailable_rule_ids"]), errors=errors,
            trace_id=value["trace_id"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise CanonicalValueError("invalid InferenceResult logical data") from exc


def inference_result_from_logical_json(payload: str | bytes) -> InferenceResult:
    if isinstance(payload, bytes):
        try:
            payload = payload.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise CanonicalValueError("malformed InferenceResult UTF-8") from exc
    if not isinstance(payload, str):
        raise TypeError("InferenceResult JSON must be text or bytes")
    def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in items:
            if key in value:
                raise CanonicalValueError("duplicate InferenceResult JSON key")
            value[key] = item
        return value
    try:
        value = json.loads(
            payload,
            object_pairs_hook=unique_object,
            parse_constant=lambda _value: (_ for _ in ()).throw(CanonicalValueError("non-finite number")),
        )
    except CanonicalValueError:
        raise
    except (json.JSONDecodeError, RecursionError) as exc:
        raise CanonicalValueError("malformed InferenceResult JSON") from exc
    return inference_result_from_logical_data(value)


__all__ = (
    "INFERENCE_SCHEMA_VERSION", "CapabilityAvailability", "ConflictRecord", "ConflictSide",
    "Contribution", "ContributionSign", "DataCompleteness", "EvidenceReference",
    "ExplanationFactor", "InferenceComponent", "InferenceError", "InferenceResult",
    "InferenceStatus", "TimingContext", "inference_result_from_logical_data",
    "inference_model_logical_json_bytes", "inference_model_to_logical_data",
    "inference_result_from_logical_json", "inference_result_logical_json_bytes",
    "inference_result_logical_sha256", "inference_result_to_logical_data",
)
