"""Immutable WP15 Career-only factual and candidate contracts.

These models deliberately stop at the Career compatibility boundary.  They
are not a shared rule-match, domain prediction, or public output model.
"""

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
    canonical_json_data,
    freeze_canonical,
    condition_result_from_full_data,
    condition_result_from_logical_data,
    condition_result_to_full_data,
    condition_result_to_logical_data,
    predicate_error_from_data,
    predicate_error_to_data,
    predicate_result_from_full_data,
    predicate_result_from_logical_data,
    predicate_result_to_full_data,
    predicate_result_to_logical_data,
    predicate_trace_step_from_data,
    predicate_trace_step_to_data,
)
from systems.Parasara.engine.rules.models import (
    ConditionResult,
    PredicateError,
    PredicateResult,
    PredicateStatus,
    PredicateTraceStep,
)
from systems.Parasara.engine.rules.prepared_state import (
    PreparedAstroState,
    prepared_capability_to_data,
)


CAREER_SCHEMA_VERSION = "1.0.0"
CAREER_FACT_VERSION = "1.0.0"
CAREER_EVALUATOR_VERSION = "1.0.0"


class CareerFactKind(str, Enum):
    """Exact factual groups executed by the current Career interpreter."""

    STRONG_IN_HOUSE = "strong_in_house"
    HOUSE_LORD_STATUS = "house_lord_status"
    RAJAYOGA_COMPATIBILITY = "rajayoga_compatibility"
    BASE_KENDRA_STRENGTH = "base_kendra_strength"
    TENTH_HOUSE_OCCUPANT_STRENGTH = "tenth_house_occupant_strength"


def _nonempty(name: str, value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _duration(value: Any) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError("evaluation_time_ms must be numeric or None")
    if not math.isfinite(value) or value < 0:
        raise ValueError("evaluation_time_ms must be finite and nonnegative")


def _mapping(name: str, value: Any) -> FrozenMapping:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    frozen = freeze_canonical(value, path=f"$.{name}")
    if not isinstance(frozen, FrozenMapping):
        raise TypeError(f"{name} must be a mapping")
    return frozen


def freeze_ordered_compatibility(value: Any) -> tuple:
    """Freeze mappings without losing the insertion order needed publicly."""

    active: set[int] = set()

    def visit(item: Any, path: str) -> tuple:
        if isinstance(item, Mapping):
            identity = id(item)
            if identity in active:
                raise CanonicalValueError(f"{path}: cyclic value")
            active.add(identity)
            try:
                pairs = []
                for key, child in item.items():
                    if type(key) is not str:
                        raise CanonicalValueError(f"{path}: non-string mapping key")
                    pairs.append((key, visit(child, f"{path}.{key}")))
                return ("mapping", tuple(pairs))
            finally:
                active.remove(identity)
        if isinstance(item, (list, tuple)):
            identity = id(item)
            if identity in active:
                raise CanonicalValueError(f"{path}: cyclic value")
            active.add(identity)
            try:
                return ("sequence", tuple(visit(child, f"{path}[]") for child in item))
            finally:
                active.remove(identity)
        scalar = freeze_canonical(item, path=path)
        if isinstance(scalar, (FrozenMapping, tuple)):
            raise CanonicalValueError(f"{path}: unsupported compatibility scalar")
        return ("scalar", scalar)

    return visit(value, "$.compatibility_context")


def _validate_ordered_compatibility(value: Any) -> tuple:
    if not isinstance(value, tuple) or len(value) != 2 or value[0] not in ("mapping", "sequence", "scalar"):
        raise TypeError("compatibility_context must be an ordered frozen value")
    kind, content = value
    if kind == "mapping":
        if not isinstance(content, tuple):
            raise TypeError("ordered mapping content must be a tuple")
        keys = []
        for item in content:
            if not isinstance(item, tuple) or len(item) != 2 or type(item[0]) is not str:
                raise TypeError("ordered mapping items must be key/value tuples")
            keys.append(item[0])
            _validate_ordered_compatibility(item[1])
        if len(set(keys)) != len(keys):
            raise ValueError("ordered mapping keys must be unique")
    elif kind == "sequence":
        if not isinstance(content, tuple):
            raise TypeError("ordered sequence content must be a tuple")
        for item in content:
            _validate_ordered_compatibility(item)
    else:
        freeze_canonical(content, path="$.compatibility_context.scalar")
    return value


def thaw_ordered_compatibility(value: tuple) -> Any:
    """Return detached mutable compatibility containers in original order."""

    kind, content = _validate_ordered_compatibility(value)
    if kind == "mapping":
        return {key: thaw_ordered_compatibility(item) for key, item in content}
    if kind == "sequence":
        return [thaw_ordered_compatibility(item) for item in content]
    return content


@dataclass(frozen=True, slots=True, kw_only=True)
class CareerPlanetFact:
    planet_id: str
    source_index: int
    house: int | None
    strength: Any
    strength_present: bool
    enriched_strength: Any
    enriched_strength_present: bool
    dignity: Any
    dignity_present: bool
    enriched_dignity: Any
    enriched_dignity_present: bool

    def __post_init__(self) -> None:
        _nonempty("planet_id", self.planet_id)
        if type(self.source_index) is not int or self.source_index < 0:
            raise ValueError("source_index must be a nonnegative integer")
        if self.house is not None and (type(self.house) is not int or not 1 <= self.house <= 12):
            raise ValueError("house must be 1..12 or None")
        for name in ("strength_present", "enriched_strength_present", "dignity_present", "enriched_dignity_present"):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be a Boolean")
        for name, present in (
            ("strength", self.strength_present),
            ("enriched_strength", self.enriched_strength_present),
            ("dignity", self.dignity_present),
            ("enriched_dignity", self.enriched_dignity_present),
        ):
            value = getattr(self, name)
            if not present and value is not None:
                raise ValueError(f"absent {name} must be None")
            if present:
                freeze_canonical(value, path=f"$.{name}")


@dataclass(frozen=True, slots=True, kw_only=True)
class CareerHouse10Fact:
    lord: Any
    lord_present: bool
    occupants: tuple[Any, ...]
    occupants_present: bool

    def __post_init__(self) -> None:
        if type(self.lord_present) is not bool or type(self.occupants_present) is not bool:
            raise TypeError("house fact presence fields must be Booleans")
        if not self.lord_present and self.lord is not None:
            raise ValueError("absent lord must be None")
        if not isinstance(self.occupants, tuple):
            raise TypeError("occupants must be a tuple")
        frozen = freeze_canonical(self.occupants, path="$.occupants")
        object.__setattr__(self, "occupants", frozen)


@dataclass(frozen=True, slots=True, kw_only=True)
class CareerPreparedFacts:
    schema_version: str
    fact_version: str
    planets: tuple[CareerPlanetFact, ...]
    planets_by_id: Mapping[str, Any]
    house10: CareerHouse10Fact | None
    predicate_state: PreparedAstroState | None
    completeness: Mapping[str, Any]
    preparation_errors: tuple[PredicateError, ...] = ()

    def __post_init__(self) -> None:
        _nonempty("schema_version", self.schema_version)
        _nonempty("fact_version", self.fact_version)
        if not isinstance(self.planets, tuple) or any(not isinstance(item, CareerPlanetFact) for item in self.planets):
            raise TypeError("planets must be an immutable CareerPlanetFact tuple")
        if tuple(item.source_index for item in self.planets) != tuple(range(len(self.planets))):
            raise ValueError("planets must retain contiguous source order")
        if len({item.planet_id for item in self.planets}) != len(self.planets):
            raise ValueError("planet identities must be unique")
        object.__setattr__(self, "planets_by_id", _mapping("planets_by_id", self.planets_by_id))
        if self.house10 is not None and not isinstance(self.house10, CareerHouse10Fact):
            raise TypeError("house10 must be a CareerHouse10Fact or None")
        if self.predicate_state is not None and not isinstance(self.predicate_state, PreparedAstroState):
            raise TypeError("predicate_state must be prepared or None")
        object.__setattr__(self, "completeness", _mapping("completeness", self.completeness))
        if not isinstance(self.preparation_errors, tuple) or any(not isinstance(item, PredicateError) for item in self.preparation_errors):
            raise TypeError("preparation_errors must be a PredicateError tuple")
        if self.preparation_errors and self.predicate_state is not None:
            raise ValueError("failed preparation cannot retain predicate state")


@dataclass(frozen=True, eq=False, slots=True, kw_only=True)
class CareerFactResult:
    fact_id: str
    fact_version: str
    fact_kind: CareerFactKind
    matched: bool
    status: PredicateStatus
    inputs: Mapping[str, Any] = field(default_factory=dict)
    evidence: Mapping[str, Any] = field(default_factory=dict)
    errors: tuple[PredicateError, ...] = ()
    trace_steps: tuple[PredicateTraceStep, ...] = ()
    backing_result: PredicateResult | ConditionResult | None = None
    evaluation_time_ms: float | None = None

    def __post_init__(self) -> None:
        _nonempty("fact_id", self.fact_id)
        _nonempty("fact_version", self.fact_version)
        if not isinstance(self.fact_kind, CareerFactKind):
            raise TypeError("fact_kind must be CareerFactKind")
        if type(self.matched) is not bool or not isinstance(self.status, PredicateStatus):
            raise TypeError("matched/status types are invalid")
        if self.matched is not (self.status is PredicateStatus.MATCHED):
            raise ValueError("matched is true exactly when status is matched")
        object.__setattr__(self, "inputs", _mapping("inputs", self.inputs))
        object.__setattr__(self, "evidence", _mapping("evidence", self.evidence))
        if not isinstance(self.errors, tuple) or any(not isinstance(item, PredicateError) for item in self.errors):
            raise TypeError("errors must be a PredicateError tuple")
        if self.status in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED) and self.errors:
            raise ValueError("factual statuses cannot carry errors")
        if self.status not in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED) and not self.errors:
            raise ValueError("non-factual statuses require a typed error")
        if not isinstance(self.trace_steps, tuple) or any(not isinstance(item, PredicateTraceStep) for item in self.trace_steps):
            raise TypeError("trace_steps must be a PredicateTraceStep tuple")
        if self.backing_result is not None and not isinstance(self.backing_result, (PredicateResult, ConditionResult)):
            raise TypeError("backing_result must be canonical or None")
        _duration(self.evaluation_time_ms)

    def __eq__(self, other):
        if not isinstance(other, CareerFactResult):
            return NotImplemented
        return _fact_to_data(self, full=False) == _fact_to_data(other, full=False)


@dataclass(frozen=True, slots=True, kw_only=True)
class CareerCandidateDefinition:
    candidate_id: str
    rule_type: str
    rule_version: str | None
    source_identity: str
    normalized_parameters: Mapping[str, Any]
    compatibility_context: tuple
    base_score: float | None
    matched_score: float
    unmatched_score: float
    source_index: int

    def __post_init__(self) -> None:
        for name in ("candidate_id", "rule_type", "source_identity"):
            _nonempty(name, getattr(self, name))
        if self.rule_version is not None:
            _nonempty("rule_version", self.rule_version)
        object.__setattr__(self, "normalized_parameters", _mapping("normalized_parameters", self.normalized_parameters))
        object.__setattr__(self, "compatibility_context", _validate_ordered_compatibility(self.compatibility_context))
        for name in ("base_score", "matched_score", "unmatched_score"):
            value = getattr(self, name)
            if value is not None and (isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value)):
                raise TypeError(f"{name} must be finite numeric or None")
        if type(self.source_index) is not int or self.source_index < 0:
            raise ValueError("source_index must be a nonnegative integer")


@dataclass(frozen=True, eq=False, slots=True, kw_only=True)
class CareerCandidateEvaluation:
    definition: CareerCandidateDefinition
    fact: CareerFactResult
    matched: bool
    status: PredicateStatus
    adjusted_score: float
    contribution: float
    compatibility_evidence: Mapping[str, Any]
    trace_lineage: tuple[str, ...]
    evaluation_time_ms: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.definition, CareerCandidateDefinition) or not isinstance(self.fact, CareerFactResult):
            raise TypeError("candidate evaluation requires typed definition and fact")
        if type(self.matched) is not bool or self.matched is not self.fact.matched:
            raise ValueError("candidate matched must agree with fact")
        if self.status is not self.fact.status:
            raise ValueError("candidate status must agree with fact")
        for name in ("adjusted_score", "contribution"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
                raise TypeError(f"{name} must be finite numeric")
        if not self.matched and self.contribution != 0.0:
            raise ValueError("unmatched/non-factual candidates contribute zero")
        object.__setattr__(self, "compatibility_evidence", _mapping("compatibility_evidence", self.compatibility_evidence))
        if not isinstance(self.trace_lineage, tuple) or any(not isinstance(item, str) or not item for item in self.trace_lineage):
            raise TypeError("trace_lineage must be a nonempty-string tuple")
        _duration(self.evaluation_time_ms)

    def __eq__(self, other):
        if not isinstance(other, CareerCandidateEvaluation):
            return NotImplemented
        return _evaluation_to_data(self, full=False) == _evaluation_to_data(other, full=False)


@dataclass(frozen=True, eq=False, slots=True, kw_only=True)
class CareerEvaluationBatch:
    schema_version: str
    evaluator_version: str
    prepared_facts_sha256: str
    candidates: tuple[CareerCandidateEvaluation, ...]
    base_facts: tuple[CareerFactResult, ...]
    component_facts: tuple[CareerFactResult, ...]
    base_score: float
    confidence_denominator: int
    completeness: Mapping[str, Any]
    batch_errors: tuple[PredicateError, ...] = ()
    evaluation_time_ms: float | None = None

    def __post_init__(self) -> None:
        _nonempty("schema_version", self.schema_version)
        _nonempty("evaluator_version", self.evaluator_version)
        if not isinstance(self.prepared_facts_sha256, str) or len(self.prepared_facts_sha256) != 64:
            raise ValueError("prepared_facts_sha256 must be lowercase SHA-256")
        try:
            int(self.prepared_facts_sha256, 16)
        except ValueError as exc:
            raise ValueError("prepared_facts_sha256 must be lowercase SHA-256") from exc
        for name, kind in (("candidates", CareerCandidateEvaluation), ("base_facts", CareerFactResult), ("component_facts", CareerFactResult)):
            values = getattr(self, name)
            if not isinstance(values, tuple) or any(not isinstance(item, kind) for item in values):
                raise TypeError(f"{name} must be an immutable typed tuple")
        if tuple(item.definition.source_index for item in self.candidates) != tuple(range(len(self.candidates))):
            raise ValueError("candidate evaluations must retain source order")
        candidate_ids = tuple(item.definition.candidate_id for item in self.candidates)
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("candidate definitions must be unique")
        if isinstance(self.base_score, bool) or not isinstance(self.base_score, Real) or not math.isfinite(self.base_score):
            raise TypeError("base_score must be finite numeric")
        if type(self.confidence_denominator) is not int or self.confidence_denominator < 0:
            raise ValueError("confidence_denominator must be a nonnegative integer")
        if self.confidence_denominator != len(self.candidates):
            raise ValueError("every candidate remains in the confidence denominator")
        object.__setattr__(self, "completeness", _mapping("completeness", self.completeness))
        if not isinstance(self.batch_errors, tuple) or any(not isinstance(item, PredicateError) for item in self.batch_errors):
            raise TypeError("batch_errors must be a PredicateError tuple")
        _duration(self.evaluation_time_ms)

    def __eq__(self, other):
        if not isinstance(other, CareerEvaluationBatch):
            return NotImplemented
        return career_evaluation_batch_to_logical_data(self) == career_evaluation_batch_to_logical_data(other)


def _planet_to_data(item: CareerPlanetFact) -> dict[str, Any]:
    return {
        "planet_id": item.planet_id, "source_index": item.source_index,
        "house": item.house,
        "strength": item.strength, "strength_present": item.strength_present,
        "enriched_strength": item.enriched_strength,
        "enriched_strength_present": item.enriched_strength_present,
        "dignity": item.dignity, "dignity_present": item.dignity_present,
        "enriched_dignity": item.enriched_dignity,
        "enriched_dignity_present": item.enriched_dignity_present,
    }


def career_prepared_facts_to_data(value: CareerPreparedFacts) -> dict[str, Any]:
    if not isinstance(value, CareerPreparedFacts):
        raise TypeError("value must be CareerPreparedFacts")
    return {
        "schema_version": value.schema_version,
        "fact_version": value.fact_version,
        "planets": [_planet_to_data(item) for item in value.planets],
        "planets_by_id": canonical_json_data(value.planets_by_id),
        "house10": None if value.house10 is None else {
            "lord": value.house10.lord, "lord_present": value.house10.lord_present,
            "occupants": list(value.house10.occupants),
            "occupants_present": value.house10.occupants_present,
        },
        "predicate_state": None if value.predicate_state is None else {
            "schema_version": value.predicate_state.schema_version,
            "producer_version": value.predicate_state.producer_version,
            "normalization_version": value.predicate_state.normalization_version,
            "system_scope": value.predicate_state.system_scope,
            "capabilities": {
                capability_id: canonical_json_data(prepared_capability_to_data(
                    value.predicate_state.capabilities[capability_id]
                ))
                for capability_id in ("planets.normalized", "planets.house_placement")
            },
        },
        "completeness": canonical_json_data(value.completeness),
        "preparation_errors": [predicate_error_to_data(item) for item in value.preparation_errors],
    }


def career_prepared_facts_json_bytes(value: CareerPreparedFacts) -> bytes:
    return canonical_json_bytes(career_prepared_facts_to_data(value))


def career_prepared_facts_sha256(value: CareerPreparedFacts) -> str:
    return hashlib.sha256(career_prepared_facts_json_bytes(value)).hexdigest()


def _backing_to_data(value: PredicateResult | ConditionResult | None, *, full: bool) -> Any:
    if value is None:
        return None
    if isinstance(value, PredicateResult):
        return {"kind": "predicate", "result": predicate_result_to_full_data(value) if full else predicate_result_to_logical_data(value)}
    return {"kind": "condition", "result": condition_result_to_full_data(value) if full else condition_result_to_logical_data(value)}


def _fact_to_data(value: CareerFactResult, *, full: bool) -> dict[str, Any]:
    data = {
        "fact_id": value.fact_id, "fact_version": value.fact_version,
        "fact_kind": value.fact_kind.value, "matched": value.matched,
        "status": value.status.value, "inputs": canonical_json_data(value.inputs),
        "evidence": canonical_json_data(value.evidence),
        "errors": [predicate_error_to_data(item) for item in value.errors],
        "trace_steps": [predicate_trace_step_to_data(item) for item in value.trace_steps],
        "backing_result": _backing_to_data(value.backing_result, full=full),
    }
    if full:
        data["evaluation_time_ms"] = value.evaluation_time_ms
    return data


def _definition_to_data(value: CareerCandidateDefinition) -> dict[str, Any]:
    return {
        "candidate_id": value.candidate_id, "rule_type": value.rule_type,
        "rule_version": value.rule_version, "source_identity": value.source_identity,
        "normalized_parameters": canonical_json_data(value.normalized_parameters),
        "compatibility_context": canonical_json_data(value.compatibility_context),
        "base_score": value.base_score, "matched_score": value.matched_score,
        "unmatched_score": value.unmatched_score, "source_index": value.source_index,
    }


def _evaluation_to_data(value: CareerCandidateEvaluation, *, full: bool) -> dict[str, Any]:
    data = {
        "definition": _definition_to_data(value.definition),
        "fact": _fact_to_data(value.fact, full=full),
        "matched": value.matched, "status": value.status.value,
        "adjusted_score": value.adjusted_score, "contribution": value.contribution,
        "compatibility_evidence": canonical_json_data(value.compatibility_evidence),
        "trace_lineage": list(value.trace_lineage),
    }
    if full:
        data["evaluation_time_ms"] = value.evaluation_time_ms
    return data


def _batch_to_data(value: CareerEvaluationBatch, *, full: bool) -> dict[str, Any]:
    if not isinstance(value, CareerEvaluationBatch):
        raise TypeError("value must be CareerEvaluationBatch")
    data = {
        "schema_version": value.schema_version,
        "evaluator_version": value.evaluator_version,
        "prepared_facts_sha256": value.prepared_facts_sha256,
        "candidates": [_evaluation_to_data(item, full=full) for item in value.candidates],
        "base_facts": [_fact_to_data(item, full=full) for item in value.base_facts],
        "component_facts": [_fact_to_data(item, full=full) for item in value.component_facts],
        "base_score": value.base_score,
        "confidence_denominator": value.confidence_denominator,
        "completeness": canonical_json_data(value.completeness),
        "batch_errors": [predicate_error_to_data(item) for item in value.batch_errors],
    }
    if full:
        data["evaluation_time_ms"] = value.evaluation_time_ms
    return data


def career_evaluation_batch_to_logical_data(value: CareerEvaluationBatch) -> dict[str, Any]:
    return _batch_to_data(value, full=False)


def career_evaluation_batch_to_full_data(value: CareerEvaluationBatch) -> dict[str, Any]:
    return _batch_to_data(value, full=True)


def career_evaluation_batch_logical_json_bytes(value: CareerEvaluationBatch) -> bytes:
    return canonical_json_bytes(career_evaluation_batch_to_logical_data(value))


def career_evaluation_batch_full_json_bytes(value: CareerEvaluationBatch) -> bytes:
    return canonical_json_bytes(career_evaluation_batch_to_full_data(value))


def career_evaluation_batch_logical_sha256(value: CareerEvaluationBatch) -> str:
    return hashlib.sha256(career_evaluation_batch_logical_json_bytes(value)).hexdigest()


def _status(value: Any) -> PredicateStatus:
    try:
        return PredicateStatus(value)
    except (TypeError, ValueError) as exc:
        raise CanonicalValueError("invalid Career predicate status") from exc


def _fact_from_data(value: Mapping[str, Any], *, full: bool) -> CareerFactResult:
    backing = value["backing_result"]
    if backing is None:
        canonical_backing = None
    elif backing["kind"] == "predicate":
        canonical_backing = predicate_result_from_full_data(backing["result"]) if full else predicate_result_from_logical_data(backing["result"])
    elif backing["kind"] == "condition":
        canonical_backing = condition_result_from_full_data(backing["result"]) if full else condition_result_from_logical_data(backing["result"])
    else:
        raise CanonicalValueError("unknown Career backing result kind")
    try:
        fact_kind = CareerFactKind(value["fact_kind"])
    except (TypeError, ValueError) as exc:
        raise CanonicalValueError("invalid Career fact kind") from exc
    return CareerFactResult(
        fact_id=value["fact_id"], fact_version=value["fact_version"], fact_kind=fact_kind,
        matched=value["matched"], status=_status(value["status"]), inputs=value["inputs"],
        evidence=value["evidence"],
        errors=tuple(predicate_error_from_data(item) for item in value["errors"]),
        trace_steps=tuple(predicate_trace_step_from_data(item) for item in value["trace_steps"]),
        backing_result=canonical_backing,
        evaluation_time_ms=value["evaluation_time_ms"] if full else None,
    )


def _definition_from_data(value: Mapping[str, Any]) -> CareerCandidateDefinition:
    def tuples(item: Any) -> Any:
        if isinstance(item, list):
            return tuple(tuples(child) for child in item)
        return item
    return CareerCandidateDefinition(
        candidate_id=value["candidate_id"], rule_type=value["rule_type"],
        rule_version=value["rule_version"], source_identity=value["source_identity"],
        normalized_parameters=value["normalized_parameters"],
        compatibility_context=tuples(value["compatibility_context"]),
        base_score=value["base_score"], matched_score=value["matched_score"],
        unmatched_score=value["unmatched_score"], source_index=value["source_index"],
    )


def _evaluation_from_data(value: Mapping[str, Any], *, full: bool) -> CareerCandidateEvaluation:
    return CareerCandidateEvaluation(
        definition=_definition_from_data(value["definition"]),
        fact=_fact_from_data(value["fact"], full=full), matched=value["matched"],
        status=_status(value["status"]), adjusted_score=value["adjusted_score"],
        contribution=value["contribution"], compatibility_evidence=value["compatibility_evidence"],
        trace_lineage=tuple(value["trace_lineage"]),
        evaluation_time_ms=value["evaluation_time_ms"] if full else None,
    )


def career_evaluation_batch_from_data(value: Any, *, full: bool) -> CareerEvaluationBatch:
    if not isinstance(value, Mapping):
        raise CanonicalValueError("Career batch must be an object")
    expected = {
        "schema_version", "evaluator_version", "prepared_facts_sha256", "candidates",
        "base_facts", "component_facts", "base_score", "confidence_denominator",
        "completeness", "batch_errors",
    } | ({"evaluation_time_ms"} if full else set())
    if set(value) != expected:
        raise CanonicalValueError("Career batch has missing or unknown keys")
    return CareerEvaluationBatch(
        schema_version=value["schema_version"], evaluator_version=value["evaluator_version"],
        prepared_facts_sha256=value["prepared_facts_sha256"],
        candidates=tuple(_evaluation_from_data(item, full=full) for item in value["candidates"]),
        base_facts=tuple(_fact_from_data(item, full=full) for item in value["base_facts"]),
        component_facts=tuple(_fact_from_data(item, full=full) for item in value["component_facts"]),
        base_score=value["base_score"], confidence_denominator=value["confidence_denominator"],
        completeness=value["completeness"],
        batch_errors=tuple(predicate_error_from_data(item) for item in value["batch_errors"]),
        evaluation_time_ms=value["evaluation_time_ms"] if full else None,
    )


class _DuplicateKey(ValueError):
    pass


def _strict_json(payload: str | bytes) -> Any:
    if type(payload) is bytes:
        try:
            payload = payload.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise CanonicalValueError("malformed Career UTF-8") from exc
    if type(payload) is not str:
        raise TypeError("Career JSON input must be text or bytes")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise _DuplicateKey
            result[key] = value
        return result

    def constant(_value):
        raise CanonicalValueError("non-finite Career JSON number")

    try:
        return json.loads(payload, object_pairs_hook=pairs, parse_constant=constant)
    except _DuplicateKey as exc:
        raise CanonicalValueError("duplicate Career JSON key") from exc
    except json.JSONDecodeError as exc:
        raise CanonicalValueError("malformed Career JSON") from exc


def career_evaluation_batch_from_json_bytes(payload: str | bytes, *, full: bool) -> CareerEvaluationBatch:
    return career_evaluation_batch_from_data(_strict_json(payload), full=full)


__all__ = (
    "CAREER_EVALUATOR_VERSION", "CAREER_FACT_VERSION", "CAREER_SCHEMA_VERSION",
    "CareerCandidateDefinition", "CareerCandidateEvaluation", "CareerEvaluationBatch",
    "CareerFactKind", "CareerFactResult", "CareerHouse10Fact", "CareerPlanetFact",
    "CareerPreparedFacts", "career_evaluation_batch_from_data",
    "career_evaluation_batch_from_json_bytes", "career_evaluation_batch_full_json_bytes",
    "career_evaluation_batch_logical_json_bytes", "career_evaluation_batch_logical_sha256",
    "career_evaluation_batch_to_full_data", "career_evaluation_batch_to_logical_data",
    "career_prepared_facts_json_bytes", "career_prepared_facts_sha256",
    "career_prepared_facts_to_data", "freeze_ordered_compatibility",
    "thaw_ordered_compatibility",
)
