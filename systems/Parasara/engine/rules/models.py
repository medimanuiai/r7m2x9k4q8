"""Canonical immutable predicate-domain models introduced by Prompt-01 WP02.

WP03 supplies the shared project-owned freeze/serialization subsystem.  The
models are the sole factual predicate-result contract used by the active
evaluator.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
import math
from numbers import Real
from typing import Any, Optional

from systems.Parasara.engine.rules.canonical import (
    FrozenMapping,
    _canonical_equal,
    freeze_canonical,
)


class PredicateStatus(str, Enum):
    """Terminal status of a canonical predicate evaluation."""

    MATCHED = "matched"
    UNMATCHED = "unmatched"
    MISSING_CAPABILITY = "missing_capability"
    INVALID_PARAMETERS = "invalid_parameters"
    ERROR = "error"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


class ConditionOperator(str, Enum):
    """Canonical logical operators supported by the current-format boundary."""

    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class ConditionNodeDisposition(str, Enum):
    """Whether one declared condition child was evaluated or short-circuited."""

    EVALUATED = "evaluated"
    SKIPPED = "skipped"


def _require_nonempty_string(name: str, value: Any) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must be non-empty")


def _require_optional_nonempty_string(name: str, value: Any) -> None:
    if value is not None:
        _require_nonempty_string(name, value)


def _freeze_mapping(name: str, value: Any) -> Mapping:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    frozen = freeze_canonical(value, path=f"$.{name}")
    if not isinstance(frozen, FrozenMapping):
        raise TypeError(f"{name} must be a mapping")
    return frozen


@dataclass(frozen=True)
class PredicateError:
    """Immutable internal error information for one predicate."""

    code: str
    message: str
    predicate_id: str
    details: Mapping[str, Any]
    recoverable: bool

    __hash__ = None

    def __post_init__(self) -> None:
        _require_nonempty_string("code", self.code)
        _require_nonempty_string("message", self.message)
        _require_nonempty_string("predicate_id", self.predicate_id)
        if type(self.recoverable) is not bool:
            raise TypeError("recoverable must be a Boolean")
        object.__setattr__(self, "details", _freeze_mapping("details", self.details))


@dataclass(frozen=True, eq=False)
class PredicateTraceStep:
    """One deterministic, path-identified logical predicate trace step."""

    step_id: str
    operation: str
    details: Mapping[str, Any]
    observation: Any
    parent_step_id: Optional[str] = None
    error_code: Optional[str] = None

    __hash__ = None

    def __post_init__(self) -> None:
        _require_nonempty_string("step_id", self.step_id)
        _require_nonempty_string("operation", self.operation)
        _require_optional_nonempty_string("parent_step_id", self.parent_step_id)
        _require_optional_nonempty_string("error_code", self.error_code)
        object.__setattr__(self, "details", _freeze_mapping("details", self.details))
        object.__setattr__(self, "observation", freeze_canonical(self.observation, path="$.observation"))

    def __eq__(self, other):
        if not isinstance(other, PredicateTraceStep):
            return NotImplemented
        return (
            self.step_id == other.step_id
            and self.operation == other.operation
            and self.details == other.details
            and _canonical_equal(self.observation, other.observation)
            and self.parent_step_id == other.parent_step_id
            and self.error_code == other.error_code
        )


@dataclass(frozen=True, eq=False, kw_only=True)
class PredicateResult:
    """Canonical ten-field logical result for factual predicates.

    Equality is logical: cache warmth and evaluation duration are deliberately
    excluded.  Instances remain unhashable until WP03 supplies canonical
    logical projection and hashing.
    """

    matched: bool
    predicate_id: str
    predicate_version: str
    inputs: Mapping[str, Any] = field(default_factory=dict)
    evidence: Mapping[str, Any] = field(default_factory=dict)
    trace_steps: tuple[PredicateTraceStep, ...] = field(default_factory=tuple)
    errors: tuple[PredicateError, ...] = field(default_factory=tuple)
    cache_hit: bool = False
    evaluation_time_ms: Optional[float] = None
    status: PredicateStatus

    __hash__ = None

    def __post_init__(self) -> None:
        if type(self.matched) is not bool:
            raise TypeError("matched must be a Boolean")
        if type(self.cache_hit) is not bool:
            raise TypeError("cache_hit must be a Boolean")
        _require_nonempty_string("predicate_id", self.predicate_id)
        _require_nonempty_string("predicate_version", self.predicate_version)
        if not isinstance(self.status, PredicateStatus):
            raise TypeError("status must be a PredicateStatus")

        if self.matched is not (self.status is PredicateStatus.MATCHED):
            raise ValueError("matched is true exactly when status is matched")

        if self.evaluation_time_ms is not None:
            value = self.evaluation_time_ms
            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError("evaluation_time_ms must be numeric or None")
            if not math.isfinite(value) or value < 0:
                raise ValueError("evaluation_time_ms must be finite and nonnegative")

        if not isinstance(self.trace_steps, (tuple, list)):
            raise TypeError("trace_steps must be a sequence")
        if not all(isinstance(step, PredicateTraceStep) for step in self.trace_steps):
            raise TypeError("trace_steps must contain only PredicateTraceStep values")
        if not isinstance(self.errors, (tuple, list)):
            raise TypeError("errors must be a sequence")
        if not all(isinstance(error, PredicateError) for error in self.errors):
            raise TypeError("errors must contain only PredicateError values")

        errors = tuple(self.errors)
        if self.status is PredicateStatus.ERROR and not errors:
            raise ValueError("error status requires at least one PredicateError")
        if self.status in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED) and errors:
            raise ValueError("ordinary factual statuses cannot carry errors")

        object.__setattr__(self, "inputs", _freeze_mapping("inputs", self.inputs))
        object.__setattr__(self, "evidence", _freeze_mapping("evidence", self.evidence))
        object.__setattr__(self, "trace_steps", tuple(self.trace_steps))
        object.__setattr__(self, "errors", errors)

    def _logical_values(self):
        return (
            self.matched,
            self.predicate_id,
            self.predicate_version,
            self.inputs,
            self.evidence,
            self.trace_steps,
            self.errors,
            self.status,
        )

    def __eq__(self, other):
        if not isinstance(other, PredicateResult):
            return NotImplemented
        return self._logical_values() == other._logical_values()


_CONDITION_SKIP_REASONS = frozenset(
    {"and_short_circuit_unmatched", "or_short_circuit_matched"}
)


@dataclass(frozen=True)
class ConditionChildResult:
    """One position-preserving child outcome in a canonical logical tree."""

    node_id: str
    child_index: int
    disposition: ConditionNodeDisposition
    result: PredicateResult | "ConditionResult" | None
    skip_reason: str | None = None

    __hash__ = None

    def __post_init__(self) -> None:
        _require_nonempty_string("node_id", self.node_id)
        if type(self.child_index) is not int:
            raise TypeError("child_index must be a non-Boolean integer")
        if self.child_index < 0:
            raise ValueError("child_index must be nonnegative")
        if not isinstance(self.disposition, ConditionNodeDisposition):
            raise TypeError("disposition must be a ConditionNodeDisposition")

        if self.disposition is ConditionNodeDisposition.EVALUATED:
            if not isinstance(self.result, (PredicateResult, ConditionResult)):
                raise TypeError("evaluated child requires one canonical result")
            if self.skip_reason is not None:
                raise ValueError("evaluated child cannot have a skip_reason")
        else:
            if self.result is not None:
                raise ValueError("skipped child cannot have an evaluated result")
            if self.skip_reason not in _CONDITION_SKIP_REASONS:
                raise ValueError("skipped child requires a locked skip_reason")


@dataclass(frozen=True, eq=False, kw_only=True)
class ConditionResult:
    """Deeply immutable logical-node result with recursive child preservation.

    Logical equality excludes this node's evaluation duration.  Descendant
    telemetry is excluded by the logical equality contracts of the nested
    ``ConditionResult`` and ``PredicateResult`` values.
    """

    node_id: str
    operator: ConditionOperator
    matched: bool
    status: PredicateStatus
    details: Mapping[str, Any] = field(default_factory=dict)
    children: tuple[ConditionChildResult, ...] = field(default_factory=tuple)
    errors: tuple[PredicateError, ...] = field(default_factory=tuple)
    trace_steps: tuple[PredicateTraceStep, ...] = field(default_factory=tuple)
    evaluation_time_ms: Optional[float] = None

    __hash__ = None

    def __post_init__(self) -> None:
        _require_nonempty_string("node_id", self.node_id)
        if not isinstance(self.operator, ConditionOperator):
            raise TypeError("operator must be a ConditionOperator")
        if type(self.matched) is not bool:
            raise TypeError("matched must be a Boolean")
        if not isinstance(self.status, PredicateStatus):
            raise TypeError("status must be a PredicateStatus")
        if self.matched is not (self.status is PredicateStatus.MATCHED):
            raise ValueError("matched is true exactly when status is matched")

        if self.evaluation_time_ms is not None:
            value = self.evaluation_time_ms
            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError("evaluation_time_ms must be numeric or None")
            if not math.isfinite(value) or value < 0:
                raise ValueError("evaluation_time_ms must be finite and nonnegative")

        if not isinstance(self.children, (tuple, list)):
            raise TypeError("children must be a sequence")
        if not all(isinstance(child, ConditionChildResult) for child in self.children):
            raise TypeError("children must contain only ConditionChildResult values")
        children = tuple(self.children)
        if any(child.child_index != index for index, child in enumerate(children)):
            raise ValueError("children must be stored in zero-based declared order")
        if len({child.node_id for child in children}) != len(children):
            raise ValueError("child node IDs must be unique")

        if not isinstance(self.errors, (tuple, list)):
            raise TypeError("errors must be a sequence")
        if not all(isinstance(error, PredicateError) for error in self.errors):
            raise TypeError("errors must contain only PredicateError values")
        errors = tuple(self.errors)
        if self.status is PredicateStatus.ERROR and not errors:
            raise ValueError("error status requires at least one PredicateError")
        if self.status in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED) and errors:
            raise ValueError("ordinary factual statuses cannot carry errors")

        if not isinstance(self.trace_steps, (tuple, list)):
            raise TypeError("trace_steps must be a sequence")
        if not all(isinstance(step, PredicateTraceStep) for step in self.trace_steps):
            raise TypeError("trace_steps must contain only PredicateTraceStep values")

        details = _freeze_mapping("details", self.details)
        if details.get("operator") != self.operator.value:
            raise ValueError("details must identify the canonical operator")
        declared_count = details.get("declared_child_count")
        if type(declared_count) is not int or declared_count < 0:
            raise ValueError("details must identify a nonnegative declared child count")

        object.__setattr__(self, "details", details)
        object.__setattr__(self, "children", children)
        object.__setattr__(self, "errors", errors)
        object.__setattr__(self, "trace_steps", tuple(self.trace_steps))

    def _logical_values(self):
        return (
            self.node_id,
            self.operator,
            self.matched,
            self.status,
            self.details,
            self.children,
            self.errors,
            self.trace_steps,
        )

    def __eq__(self, other):
        if not isinstance(other, ConditionResult):
            return NotImplemented
        return self._logical_values() == other._logical_values()
