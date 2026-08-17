"""Immutable universal result contract for one evaluated Parāśara rule.

The generic Rule Engine is the only active producer of :class:`RuleMatch`.
This module owns the value contract and its canonical logical serializer; it
does not evaluate predicates, score results, infer conclusions, or narrate.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
from numbers import Real
import re
from typing import Any

from systems.Parasara.engine.rules.canonical import (
    CanonicalValueError,
    FrozenMapping,
    canonical_json_bytes,
    freeze_canonical,
    predicate_result_from_logical_data,
    predicate_result_to_logical_data,
)
from systems.Parasara.engine.rules.models import PredicateResult


RULE_MATCH_SCHEMA_VERSION = "1.0.0"


class RuleMatchStatus(str, Enum):
    MATCHED = "matched"
    UNMATCHED = "unmatched"
    SKIPPED = "skipped"
    EXCLUDED = "excluded"
    MISSING_CAPABILITY = "missing_capability"
    INVALID = "invalid"
    ERROR = "error"


_FORBIDDEN_KEYS = frozenset(
    {
        "adjusted_weight",
        "adjusted_score",
        "confidence",
        "conflict",
        "conflict_result",
        "conflicts",
        "contribution",
        "context_multiplier",
        "domain_prediction",
        "final_contribution",
        "final_score",
        "narrative",
        "normalized_score",
        "priority_multiplier",
        "quality_multiplier",
        "score",
    }
)
_RULE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


def _nonempty(name: str, value: Any) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must be nonempty")


def _optional_nonempty(name: str, value: Any) -> None:
    if value is not None:
        _nonempty(name, value)


def _mapping(name: str, value: Any) -> FrozenMapping:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    frozen = freeze_canonical(value, path=f"$.{name}")
    if not isinstance(frozen, FrozenMapping):
        raise TypeError(f"{name} must be a mapping")
    _reject_forbidden_fields(frozen, path=f"$.{name}")
    return frozen


def _reject_forbidden_fields(value: Any, *, path: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in _FORBIDDEN_KEYS:
                raise ValueError(f"{path}.{key} belongs to inference or presentation, not RuleMatch")
            _reject_forbidden_fields(child, path=f"{path}.{key}")
    elif isinstance(value, tuple):
        for index, child in enumerate(value):
            _reject_forbidden_fields(child, path=f"{path}[{index}]")


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleMatchError:
    code: str
    message: str
    phase: str
    recoverable: bool
    details: Mapping[str, Any] = field(default_factory=dict)
    source_predicate_id: str | None = None
    source_trace_id: str | None = None

    def __post_init__(self) -> None:
        for name in ("code", "message", "phase"):
            _nonempty(name, getattr(self, name))
        if type(self.recoverable) is not bool:
            raise TypeError("recoverable must be a Boolean")
        _optional_nonempty("source_predicate_id", self.source_predicate_id)
        _optional_nonempty("source_trace_id", self.source_trace_id)
        object.__setattr__(self, "details", _mapping("details", self.details))


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleTraceReference:
    trace_id: str
    trace_type: str
    relation: str
    order: int

    def __post_init__(self) -> None:
        for name in ("trace_id", "trace_type", "relation"):
            _nonempty(name, getattr(self, name))
        if type(self.order) is not int or self.order < 0:
            raise ValueError("order must be a nonnegative integer")


def _trace_sort_key(reference: RuleTraceReference) -> tuple[Any, ...]:
    return (reference.order, reference.trace_type, reference.trace_id, reference.relation)


@dataclass(frozen=True, eq=False, slots=True, kw_only=True)
class RuleMatch:
    rule_match_schema_version: str
    system: str
    rule_id: str
    rule_version: str
    rule_family: str
    rule_set_version: str
    category: str
    domains: tuple[str, ...]
    status: RuleMatchStatus
    matched: bool
    base_weight: float
    priority: int
    context: str
    quality: float | None
    predicate_results: tuple[PredicateResult, ...]
    evidence: Mapping[str, Any]
    provenance: Mapping[str, Any]
    metadata: Mapping[str, Any]
    trace_id: str
    condition_trace_id: str | None
    trace_references: tuple[RuleTraceReference, ...] = ()
    errors: tuple[RuleMatchError, ...] = ()

    __hash__ = None

    def __post_init__(self) -> None:
        for name in (
            "rule_match_schema_version",
            "system",
            "rule_id",
            "rule_version",
            "rule_family",
            "rule_set_version",
            "category",
            "context",
            "trace_id",
        ):
            _nonempty(name, getattr(self, name))
        if not _RULE_ID.fullmatch(self.rule_id):
            raise ValueError("rule_id must satisfy the canonical loader identity contract")
        _optional_nonempty("condition_trace_id", self.condition_trace_id)
        if not isinstance(self.status, RuleMatchStatus):
            raise TypeError("status must be a RuleMatchStatus")
        if type(self.matched) is not bool or self.matched is not (
            self.status is RuleMatchStatus.MATCHED
        ):
            raise ValueError("matched is true exactly when status is MATCHED")
        if (
            isinstance(self.base_weight, bool)
            or not isinstance(self.base_weight, Real)
            or not math.isfinite(self.base_weight)
        ):
            raise TypeError("base_weight must be finite numeric")
        object.__setattr__(self, "base_weight", float(self.base_weight))
        if self.quality is not None:
            if (
                isinstance(self.quality, bool)
                or not isinstance(self.quality, Real)
                or not math.isfinite(self.quality)
            ):
                raise TypeError("quality must be finite numeric or None")
            object.__setattr__(self, "quality", float(self.quality))
        if type(self.priority) is not int:
            raise TypeError("priority must be a non-Boolean integer")
        if not isinstance(self.domains, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.domains
        ):
            raise TypeError("domains must be an immutable tuple of nonempty strings")
        normalized_domains = tuple(sorted(set(self.domains)))
        if normalized_domains != self.domains:
            raise ValueError("domains must be unique and sorted")
        if not isinstance(self.predicate_results, tuple) or any(
            not isinstance(item, PredicateResult) for item in self.predicate_results
        ):
            raise TypeError("predicate_results must be an immutable PredicateResult tuple")
        if not isinstance(self.trace_references, tuple) or any(
            not isinstance(item, RuleTraceReference) for item in self.trace_references
        ):
            raise TypeError("trace_references must be an immutable RuleTraceReference tuple")
        if tuple(sorted(self.trace_references, key=_trace_sort_key)) != self.trace_references:
            raise ValueError("trace_references must use canonical order")
        if not isinstance(self.errors, tuple) or any(
            not isinstance(item, RuleMatchError) for item in self.errors
        ):
            raise TypeError("errors must be an immutable RuleMatchError tuple")
        if self.status is RuleMatchStatus.ERROR and not self.errors:
            raise ValueError("ERROR status requires at least one RuleMatchError")
        if self.status in (
            RuleMatchStatus.MISSING_CAPABILITY,
            RuleMatchStatus.INVALID,
            RuleMatchStatus.ERROR,
        ) and not self.errors and not self.trace_references:
            raise ValueError("non-factual status requires typed error or trace evidence")
        frozen_metadata = _mapping("metadata", self.metadata)
        if not self.domains and frozen_metadata.get("domain_neutral") is not True:
            raise ValueError("empty domains require explicit domain_neutral metadata")
        object.__setattr__(self, "evidence", _mapping("evidence", self.evidence))
        object.__setattr__(self, "provenance", _mapping("provenance", self.provenance))
        object.__setattr__(self, "metadata", frozen_metadata)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RuleMatch):
            return NotImplemented
        return rule_match_to_logical_data(self) == rule_match_to_logical_data(other)


def rule_match_error_to_data(value: RuleMatchError) -> dict[str, Any]:
    return {
        "code": value.code,
        "message": value.message,
        "phase": value.phase,
        "recoverable": value.recoverable,
        "details": value.details,
        "source_predicate_id": value.source_predicate_id,
        "source_trace_id": value.source_trace_id,
    }


def rule_trace_reference_to_data(value: RuleTraceReference) -> dict[str, Any]:
    return {
        "trace_id": value.trace_id,
        "trace_type": value.trace_type,
        "relation": value.relation,
        "order": value.order,
    }


def rule_match_to_logical_data(value: RuleMatch) -> FrozenMapping:
    if not isinstance(value, RuleMatch):
        raise TypeError("value must be a RuleMatch")
    return FrozenMapping(
        {
            "rule_match_schema_version": value.rule_match_schema_version,
            "system": value.system,
            "rule_id": value.rule_id,
            "rule_version": value.rule_version,
            "rule_family": value.rule_family,
            "rule_set_version": value.rule_set_version,
            "category": value.category,
            "domains": value.domains,
            "status": value.status.value,
            "matched": value.matched,
            "base_weight": value.base_weight,
            "priority": value.priority,
            "context": value.context,
            "quality": value.quality,
            "predicate_results": tuple(
                predicate_result_to_logical_data(item) for item in value.predicate_results
            ),
            "evidence": value.evidence,
            "provenance": value.provenance,
            "metadata": value.metadata,
            "trace_id": value.trace_id,
            "condition_trace_id": value.condition_trace_id,
            "trace_references": tuple(
                rule_trace_reference_to_data(item) for item in value.trace_references
            ),
            "errors": tuple(rule_match_error_to_data(item) for item in value.errors),
        }
    )


def rule_match_logical_json_bytes(value: RuleMatch) -> bytes:
    return canonical_json_bytes(rule_match_to_logical_data(value))


def rule_match_logical_sha256(value: RuleMatch) -> str:
    return hashlib.sha256(rule_match_logical_json_bytes(value)).hexdigest()


class _DuplicateJsonKey(ValueError):
    pass


def rule_match_from_logical_json(payload: str | bytes) -> RuleMatch:
    """Strictly deserialize canonical RuleMatch JSON without duplicate keys."""

    if type(payload) is bytes:
        try:
            payload = payload.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise CanonicalValueError("malformed RuleMatch UTF-8") from exc
    if type(payload) is not str:
        raise TypeError("RuleMatch JSON input must be text or bytes")

    def unique_object(items):
        value = {}
        for key, child in items:
            if key in value:
                raise _DuplicateJsonKey
            value[key] = child
        return value

    def reject_constant(_value):
        raise CanonicalValueError("non-finite RuleMatch JSON number")

    try:
        data = json.loads(
            payload,
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except _DuplicateJsonKey as exc:
        raise CanonicalValueError("duplicate RuleMatch JSON object key") from exc
    except CanonicalValueError:
        raise
    except (json.JSONDecodeError, UnicodeError, RecursionError) as exc:
        raise CanonicalValueError("malformed RuleMatch JSON") from exc
    return rule_match_from_logical_data(data)


def _strict_keys(value: Any, expected: set[str], name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise CanonicalValueError(f"{name} has missing or unknown keys")
    return value


def rule_match_from_logical_data(value: Any) -> RuleMatch:
    data = _strict_keys(
        value,
        {
            "rule_match_schema_version", "system", "rule_id", "rule_version",
            "rule_family", "rule_set_version", "category", "domains", "status",
            "matched", "base_weight", "priority", "context", "quality",
            "predicate_results", "evidence", "provenance", "metadata", "trace_id",
            "condition_trace_id", "trace_references", "errors",
        },
        "RuleMatch",
    )
    try:
        if not isinstance(data["trace_references"], (list, tuple)):
            raise CanonicalValueError("RuleMatch trace_references must be a sequence")
        if not isinstance(data["errors"], (list, tuple)):
            raise CanonicalValueError("RuleMatch errors must be a sequence")
        references = tuple(
            RuleTraceReference(**_strict_keys(
                item,
                {"trace_id", "trace_type", "relation", "order"},
                "trace reference",
            ))
            for item in data["trace_references"]
        )
        errors = tuple(
            RuleMatchError(**_strict_keys(
                item,
                {
                    "code", "message", "phase", "recoverable", "details",
                    "source_predicate_id", "source_trace_id",
                },
                "RuleMatch error",
            ))
            for item in data["errors"]
        )
        status = RuleMatchStatus(data["status"])
        return RuleMatch(
            rule_match_schema_version=data["rule_match_schema_version"],
            system=data["system"],
            rule_id=data["rule_id"],
            rule_version=data["rule_version"],
            rule_family=data["rule_family"],
            rule_set_version=data["rule_set_version"],
            category=data["category"],
            domains=tuple(data["domains"]),
            status=status,
            matched=data["matched"],
            base_weight=data["base_weight"],
            priority=data["priority"],
            context=data["context"],
            quality=data["quality"],
            predicate_results=tuple(
                predicate_result_from_logical_data(item) for item in data["predicate_results"]
            ),
            evidence=data["evidence"],
            provenance=data["provenance"],
            metadata=data["metadata"],
            trace_id=data["trace_id"],
            condition_trace_id=data["condition_trace_id"],
            trace_references=references,
            errors=errors,
        )
    except (TypeError, ValueError, CanonicalValueError) as exc:
        raise CanonicalValueError("invalid RuleMatch logical data") from exc


__all__ = (
    "RULE_MATCH_SCHEMA_VERSION",
    "RuleMatch",
    "RuleMatchError",
    "RuleMatchStatus",
    "RuleTraceReference",
    "rule_match_from_logical_data",
    "rule_match_from_logical_json",
    "rule_match_logical_json_bytes",
    "rule_match_logical_sha256",
    "rule_match_to_logical_data",
)
