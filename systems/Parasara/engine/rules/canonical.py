"""Strict canonical values and serialization for predicate-domain models.

This module is internal to the predicate subsystem and does not publish
canonical models through domain/public APIs.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import is_dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
import hashlib
from io import IOBase
import json
import math
import re
from types import GeneratorType, MappingProxyType, ModuleType, TracebackType
from typing import Any, TYPE_CHECKING

from _thread import LockType, RLock
from pydantic import BaseModel

if TYPE_CHECKING:
    from systems.Parasara.engine.rules.models import (
        ConditionChildResult,
        ConditionResult,
        PredicateError,
        PredicateResult,
        PredicateTraceStep,
    )


class CanonicalValueError(ValueError):
    """A safe path-aware canonical-value or canonical-input failure."""


_SAFE_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_RLOCK_TYPE = type(RLock())


def _key_path(path: str, key: str) -> str:
    return f"{path}.{key}" if _SAFE_KEY.fullmatch(key) else f"{path}[key]"


class FrozenMapping(Mapping):
    """Project-owned immutable mapping for canonical predicate values."""

    __slots__ = ("_items", "_lookup", "_hash")

    def __init__(self, value: Mapping | None = None, *, path: str = "$") -> None:
        source = {} if value is None else value
        frozen = freeze_canonical(source, path=path)
        if not isinstance(frozen, FrozenMapping):
            raise CanonicalValueError(f"{path}: expected mapping")
        object.__setattr__(self, "_items", frozen._items)
        object.__setattr__(self, "_lookup", frozen._lookup)
        object.__setattr__(self, "_hash", frozen._hash)

    @classmethod
    def _from_frozen_items(cls, items) -> "FrozenMapping":
        instance = object.__new__(cls)
        ordered = tuple(items)
        object.__setattr__(instance, "_items", ordered)
        object.__setattr__(instance, "_lookup", MappingProxyType(dict(ordered)))
        object.__setattr__(
            instance,
            "_hash",
            hash(("mapping", tuple((key, _canonical_hash(value)) for key, value in ordered))),
        )
        return instance

    def __setattr__(self, name, value):
        raise TypeError("FrozenMapping attributes cannot be reassigned")

    def __getitem__(self, key):
        return self._lookup[key]

    def __iter__(self):
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"FrozenMapping(len={len(self)})"

    def __eq__(self, other):
        if not isinstance(other, FrozenMapping):
            if not isinstance(other, Mapping):
                return NotImplemented
            try:
                other = freeze_canonical(other)
            except CanonicalValueError:
                return False
        return _canonical_equal(self, other)

    def __hash__(self) -> int:
        return self._hash


def _canonical_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, FrozenMapping):
        if len(left._items) != len(right._items):
            return False
        return all(
            left_key == right_key and _canonical_equal(left_value, right_value)
            for (left_key, left_value), (right_key, right_value) in zip(left._items, right._items)
        )
    if isinstance(left, tuple):
        return len(left) == len(right) and all(
            _canonical_equal(left_item, right_item)
            for left_item, right_item in zip(left, right)
        )
    return left == right


def _canonical_hash(value: Any) -> int:
    if isinstance(value, FrozenMapping):
        return value._hash
    if isinstance(value, tuple):
        return hash(("array", tuple(_canonical_hash(item) for item in value)))
    return hash((type(value).__name__, value))


def _has_runtime_type(value: Any, module: str, name: str) -> bool:
    """Recognize an unsupported operational type without importing its module."""

    return any(
        item.__module__ == module and item.__name__ == name
        for item in type(value).__mro__
    )


def _unsupported_category(value: Any) -> str:
    if isinstance(value, (set, frozenset)):
        return "set"
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "binary"
    if isinstance(value, Decimal):
        return "decimal"
    if isinstance(value, complex):
        return "complex"
    if isinstance(value, (datetime, date, timedelta)):
        return "temporal"
    if _has_runtime_type(value, "uuid", "UUID"):
        return "uuid"
    if _has_runtime_type(value, "pathlib", "PurePath"):
        return "path"
    if isinstance(value, re.Pattern):
        return "regex"
    if isinstance(value, ModuleType):
        return "module"
    if isinstance(value, type):
        return "class"
    if isinstance(value, GeneratorType):
        return "generator"
    if isinstance(value, BaseException):
        return "exception"
    if isinstance(value, TracebackType):
        return "traceback"
    if isinstance(value, IOBase):
        return "open resource"
    if isinstance(value, (LockType, _RLOCK_TYPE)):
        return "lock"
    if _has_runtime_type(value, "socket", "socket"):
        return "socket"
    if isinstance(value, BaseModel):
        return "pydantic model"
    if is_dataclass(value) and not isinstance(value, type):
        return "dataclass"
    if isinstance(value, Iterator):
        return "iterator"
    if callable(value):
        return "callable"
    return "custom object"


def freeze_canonical(value: Any, *, path: str = "$") -> Any:
    """Recursively freeze one value under the locked canonical policy."""

    if not isinstance(path, str) or not path:
        raise ValueError("path must be a non-empty string")
    return _freeze(value, path, set())


def _freeze(value: Any, path: str, active: set[int]) -> Any:
    if isinstance(value, Enum):
        if type(value.value) is not str:
            raise CanonicalValueError(f"{path}: unsupported non-string enum")
        return value.value

    if value is None or type(value) in (bool, int, str):
        return value

    if type(value) is float:
        if not math.isfinite(value):
            raise CanonicalValueError(f"{path}: unsupported non-finite float")
        return 0.0 if value == 0.0 else value

    if isinstance(value, Mapping):
        identity = id(value)
        if identity in active:
            raise CanonicalValueError(f"{path}: cyclic value")
        active.add(identity)
        try:
            keys = list(value.keys())
            for key in keys:
                if type(key) is not str:
                    raise CanonicalValueError(f"{path}[key]: non-string mapping key")
            return FrozenMapping._from_frozen_items(
                (key, _freeze(value[key], _key_path(path, key), active))
                for key in sorted(keys)
            )
        finally:
            active.remove(identity)

    if isinstance(value, (list, tuple)):
        identity = id(value)
        if identity in active:
            raise CanonicalValueError(f"{path}: cyclic value")
        active.add(identity)
        try:
            return tuple(_freeze(item, f"{path}[{index}]", active) for index, item in enumerate(value))
        finally:
            active.remove(identity)

    category = _unsupported_category(value)
    raise CanonicalValueError(f"{path}: unsupported {category}")


def _to_json_data(value: Any) -> Any:
    if isinstance(value, FrozenMapping):
        return {key: _to_json_data(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_to_json_data(item) for item in value]
    return value


def canonical_json_data(value: Any) -> Any:
    """Return a fresh JSON-compatible projection of one canonical value."""

    return _to_json_data(freeze_canonical(value))


def canonical_json_text(value: Any) -> str:
    """Return strict compact canonical JSON text for a supported value."""

    data = canonical_json_data(value)
    return json.dumps(
        data,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Return strict UTF-8 canonical JSON bytes without BOM or newline."""

    return canonical_json_text(value).encode("utf-8")


def _require_model(value: Any, model_type: type, path: str) -> None:
    if not isinstance(value, model_type):
        raise TypeError(f"{path} must be {model_type.__name__}")


def predicate_error_to_data(error: "PredicateError") -> dict[str, Any]:
    from systems.Parasara.engine.rules.models import PredicateError

    _require_model(error, PredicateError, "error")
    return {
        "code": error.code,
        "message": error.message,
        "predicate_id": error.predicate_id,
        "details": canonical_json_data(error.details),
        "recoverable": error.recoverable,
    }


def predicate_trace_step_to_data(step: "PredicateTraceStep") -> dict[str, Any]:
    from systems.Parasara.engine.rules.models import PredicateTraceStep

    _require_model(step, PredicateTraceStep, "step")
    return {
        "step_id": step.step_id,
        "operation": step.operation,
        "details": canonical_json_data(step.details),
        "observation": canonical_json_data(step.observation),
        "parent_step_id": step.parent_step_id,
        "error_code": step.error_code,
    }


def predicate_result_to_logical_data(result: "PredicateResult") -> dict[str, Any]:
    from systems.Parasara.engine.rules.models import PredicateResult

    _require_model(result, PredicateResult, "result")
    return {
        "matched": result.matched,
        "predicate_id": result.predicate_id,
        "predicate_version": result.predicate_version,
        "inputs": canonical_json_data(result.inputs),
        "evidence": canonical_json_data(result.evidence),
        "trace_steps": [predicate_trace_step_to_data(step) for step in result.trace_steps],
        "errors": [predicate_error_to_data(error) for error in result.errors],
        "status": result.status.value,
    }


def predicate_result_to_full_data(result: "PredicateResult") -> dict[str, Any]:
    data = predicate_result_to_logical_data(result)
    data["cache_hit"] = result.cache_hit
    data["evaluation_time_ms"] = result.evaluation_time_ms
    return data


def predicate_error_json_text(error: "PredicateError") -> str:
    return canonical_json_text(predicate_error_to_data(error))


def predicate_error_json_bytes(error: "PredicateError") -> bytes:
    return predicate_error_json_text(error).encode("utf-8")


def predicate_trace_step_json_text(step: "PredicateTraceStep") -> str:
    return canonical_json_text(predicate_trace_step_to_data(step))


def predicate_trace_step_json_bytes(step: "PredicateTraceStep") -> bytes:
    return predicate_trace_step_json_text(step).encode("utf-8")


def predicate_result_logical_json_text(result: "PredicateResult") -> str:
    return canonical_json_text(predicate_result_to_logical_data(result))


def predicate_result_logical_json_bytes(result: "PredicateResult") -> bytes:
    return predicate_result_logical_json_text(result).encode("utf-8")


def predicate_result_full_json_text(result: "PredicateResult") -> str:
    return canonical_json_text(predicate_result_to_full_data(result))


def predicate_result_full_json_bytes(result: "PredicateResult") -> bytes:
    return predicate_result_full_json_text(result).encode("utf-8")


def _canonical_object(data: Any, expected_keys: set[str], *, path: str) -> FrozenMapping:
    frozen = freeze_canonical(data, path=path)
    if not isinstance(frozen, FrozenMapping):
        raise CanonicalValueError(f"{path}: expected object")
    keys = set(frozen)
    missing = expected_keys - keys
    unknown = keys - expected_keys
    if missing:
        raise CanonicalValueError(f"{path}: missing required keys")
    if unknown:
        raise CanonicalValueError(f"{path}: unknown keys")
    return frozen


def _canonical_array(value: Any, *, path: str) -> tuple:
    frozen = freeze_canonical(value, path=path)
    if not isinstance(frozen, tuple):
        raise CanonicalValueError(f"{path}: expected array")
    return frozen


_ERROR_KEYS = {"code", "message", "predicate_id", "details", "recoverable"}
_TRACE_KEYS = {"step_id", "operation", "details", "observation", "parent_step_id", "error_code"}
_LOGICAL_RESULT_KEYS = {
    "matched",
    "predicate_id",
    "predicate_version",
    "inputs",
    "evidence",
    "trace_steps",
    "errors",
    "status",
}
_FULL_RESULT_KEYS = _LOGICAL_RESULT_KEYS | {"cache_hit", "evaluation_time_ms"}


def predicate_error_from_data(data: Any) -> "PredicateError":
    from systems.Parasara.engine.rules.models import PredicateError

    value = _canonical_object(data, _ERROR_KEYS, path="$")
    return PredicateError(
        code=value["code"],
        message=value["message"],
        predicate_id=value["predicate_id"],
        details=value["details"],
        recoverable=value["recoverable"],
    )


def predicate_trace_step_from_data(data: Any) -> "PredicateTraceStep":
    from systems.Parasara.engine.rules.models import PredicateTraceStep

    value = _canonical_object(data, _TRACE_KEYS, path="$")
    return PredicateTraceStep(
        step_id=value["step_id"],
        operation=value["operation"],
        details=value["details"],
        observation=value["observation"],
        parent_step_id=value["parent_step_id"],
        error_code=value["error_code"],
    )


def _status_from_value(value: Any):
    from systems.Parasara.engine.rules.models import PredicateStatus

    if type(value) is not str:
        raise CanonicalValueError("$.status: expected string status")
    try:
        return PredicateStatus(value)
    except ValueError as exc:
        raise CanonicalValueError("$.status: invalid predicate status") from exc


def _result_from_data(data: Any, *, full: bool) -> "PredicateResult":
    from systems.Parasara.engine.rules.models import PredicateResult

    expected = _FULL_RESULT_KEYS if full else _LOGICAL_RESULT_KEYS
    value = _canonical_object(data, expected, path="$")
    traces = _canonical_array(value["trace_steps"], path="$.trace_steps")
    errors = _canonical_array(value["errors"], path="$.errors")
    return PredicateResult(
        matched=value["matched"],
        predicate_id=value["predicate_id"],
        predicate_version=value["predicate_version"],
        inputs=value["inputs"],
        evidence=value["evidence"],
        trace_steps=tuple(predicate_trace_step_from_data(item) for item in traces),
        errors=tuple(predicate_error_from_data(item) for item in errors),
        cache_hit=value["cache_hit"] if full else False,
        evaluation_time_ms=value["evaluation_time_ms"] if full else None,
        status=_status_from_value(value["status"]),
    )


def predicate_result_from_logical_data(data: Any) -> "PredicateResult":
    return _result_from_data(data, full=False)


def predicate_result_from_full_data(data: Any) -> "PredicateResult":
    return _result_from_data(data, full=True)


class _DuplicateJsonKey(ValueError):
    pass


def _object_without_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKey
        result[key] = value
    return result


def _reject_json_constant(value):
    raise CanonicalValueError("$: unsupported non-finite float")


def _load_strict_json(payload: str | bytes) -> Any:
    if type(payload) is bytes:
        try:
            text = payload.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise CanonicalValueError("$: malformed UTF-8") from exc
    elif type(payload) is str:
        text = payload
    else:
        raise TypeError("JSON input must be text or bytes")

    try:
        data = json.loads(
            text,
            object_pairs_hook=_object_without_duplicates,
            parse_constant=_reject_json_constant,
        )
    except _DuplicateJsonKey as exc:
        raise CanonicalValueError("$: duplicate JSON object key") from exc
    except CanonicalValueError:
        raise
    except (json.JSONDecodeError, UnicodeError, RecursionError) as exc:
        raise CanonicalValueError("$: malformed JSON text") from exc

    frozen = freeze_canonical(data)
    return _to_json_data(frozen)


def predicate_error_from_json(payload: str | bytes) -> "PredicateError":
    return predicate_error_from_data(_load_strict_json(payload))


def predicate_trace_step_from_json(payload: str | bytes) -> "PredicateTraceStep":
    return predicate_trace_step_from_data(_load_strict_json(payload))


def predicate_result_from_logical_json(payload: str | bytes) -> "PredicateResult":
    return predicate_result_from_logical_data(_load_strict_json(payload))


def predicate_result_from_full_json(payload: str | bytes) -> "PredicateResult":
    return predicate_result_from_full_data(_load_strict_json(payload))


def predicate_result_logical_sha256(result: "PredicateResult") -> str:
    """Return the persisted logical identity of a canonical result."""

    return hashlib.sha256(predicate_result_logical_json_bytes(result)).hexdigest()


def _condition_child_to_data(child: "ConditionChildResult", *, full: bool) -> dict[str, Any]:
    from systems.Parasara.engine.rules.models import (
        ConditionChildResult,
        ConditionNodeDisposition,
        ConditionResult,
        PredicateResult,
    )

    _require_model(child, ConditionChildResult, "child")
    kind = None
    projected = None
    if child.disposition is ConditionNodeDisposition.EVALUATED:
        if isinstance(child.result, PredicateResult):
            kind = "predicate"
            projected = (
                predicate_result_to_full_data(child.result)
                if full
                else predicate_result_to_logical_data(child.result)
            )
        elif isinstance(child.result, ConditionResult):
            kind = "condition"
            projected = _condition_result_to_data(child.result, full=full)
        else:  # pragma: no cover - the model invariant prevents this branch
            raise TypeError("evaluated child has an unsupported result")
    return {
        "node_id": child.node_id,
        "child_index": child.child_index,
        "disposition": child.disposition.value,
        "result_kind": kind,
        "result": projected,
        "skip_reason": child.skip_reason,
    }


def _condition_result_to_data(result: "ConditionResult", *, full: bool) -> dict[str, Any]:
    from systems.Parasara.engine.rules.models import ConditionResult

    _require_model(result, ConditionResult, "result")
    data = {
        "node_id": result.node_id,
        "operator": result.operator.value,
        "matched": result.matched,
        "status": result.status.value,
        "details": canonical_json_data(result.details),
        "children": [_condition_child_to_data(child, full=full) for child in result.children],
        "errors": [predicate_error_to_data(error) for error in result.errors],
        "trace_steps": [predicate_trace_step_to_data(step) for step in result.trace_steps],
    }
    if full:
        data["evaluation_time_ms"] = result.evaluation_time_ms
    return data


def condition_result_to_logical_data(result: "ConditionResult") -> dict[str, Any]:
    """Project a recursive condition tree without condition/leaf telemetry."""

    return _condition_result_to_data(result, full=False)


def condition_result_to_full_data(result: "ConditionResult") -> dict[str, Any]:
    """Project a recursive condition tree including approved telemetry."""

    return _condition_result_to_data(result, full=True)


def condition_result_logical_json_text(result: "ConditionResult") -> str:
    return canonical_json_text(condition_result_to_logical_data(result))


def condition_result_logical_json_bytes(result: "ConditionResult") -> bytes:
    return condition_result_logical_json_text(result).encode("utf-8")


def condition_result_full_json_text(result: "ConditionResult") -> str:
    return canonical_json_text(condition_result_to_full_data(result))


def condition_result_full_json_bytes(result: "ConditionResult") -> bytes:
    return condition_result_full_json_text(result).encode("utf-8")


_CONDITION_CHILD_KEYS = {
    "node_id", "child_index", "disposition", "result_kind", "result", "skip_reason"
}
_CONDITION_LOGICAL_KEYS = {
    "node_id", "operator", "matched", "status", "details", "children", "errors", "trace_steps"
}
_CONDITION_FULL_KEYS = _CONDITION_LOGICAL_KEYS | {"evaluation_time_ms"}


def _condition_operator(value: Any):
    from systems.Parasara.engine.rules.models import ConditionOperator

    if type(value) is not str:
        raise CanonicalValueError("$.operator: expected string operator")
    try:
        return ConditionOperator(value)
    except ValueError as exc:
        raise CanonicalValueError("$.operator: invalid condition operator") from exc


def _condition_disposition(value: Any):
    from systems.Parasara.engine.rules.models import ConditionNodeDisposition

    if type(value) is not str:
        raise CanonicalValueError("$.disposition: expected string disposition")
    try:
        return ConditionNodeDisposition(value)
    except ValueError as exc:
        raise CanonicalValueError("$.disposition: invalid child disposition") from exc


def _condition_child_from_data(data: Any, *, full: bool) -> "ConditionChildResult":
    from systems.Parasara.engine.rules.models import (
        ConditionChildResult,
        ConditionNodeDisposition,
    )

    value = _canonical_object(data, _CONDITION_CHILD_KEYS, path="$.children[]")
    disposition = _condition_disposition(value["disposition"])
    kind = value["result_kind"]
    raw_result = value["result"]
    parsed = None
    if disposition is ConditionNodeDisposition.EVALUATED:
        if kind == "predicate":
            parsed = _result_from_data(raw_result, full=full)
        elif kind == "condition":
            parsed = _condition_result_from_data(raw_result, full=full)
        else:
            raise CanonicalValueError("$.children[]: invalid evaluated result kind")
    elif kind is not None or raw_result is not None:
        raise CanonicalValueError("$.children[]: skipped child cannot carry a result")
    return ConditionChildResult(
        node_id=value["node_id"],
        child_index=value["child_index"],
        disposition=disposition,
        result=parsed,
        skip_reason=value["skip_reason"],
    )


def _condition_result_from_data(data: Any, *, full: bool) -> "ConditionResult":
    from systems.Parasara.engine.rules.models import ConditionResult

    expected = _CONDITION_FULL_KEYS if full else _CONDITION_LOGICAL_KEYS
    value = _canonical_object(data, expected, path="$")
    children = _canonical_array(value["children"], path="$.children")
    errors = _canonical_array(value["errors"], path="$.errors")
    traces = _canonical_array(value["trace_steps"], path="$.trace_steps")
    return ConditionResult(
        node_id=value["node_id"],
        operator=_condition_operator(value["operator"]),
        matched=value["matched"],
        status=_status_from_value(value["status"]),
        details=value["details"],
        children=tuple(_condition_child_from_data(child, full=full) for child in children),
        errors=tuple(predicate_error_from_data(error) for error in errors),
        trace_steps=tuple(predicate_trace_step_from_data(step) for step in traces),
        evaluation_time_ms=value["evaluation_time_ms"] if full else None,
    )


def condition_result_from_logical_data(data: Any) -> "ConditionResult":
    return _condition_result_from_data(data, full=False)


def condition_result_from_full_data(data: Any) -> "ConditionResult":
    return _condition_result_from_data(data, full=True)


def condition_result_from_logical_json(payload: str | bytes) -> "ConditionResult":
    return condition_result_from_logical_data(_load_strict_json(payload))


def condition_result_from_full_json(payload: str | bytes) -> "ConditionResult":
    return condition_result_from_full_data(_load_strict_json(payload))


def condition_result_logical_sha256(result: "ConditionResult") -> str:
    return hashlib.sha256(condition_result_logical_json_bytes(result)).hexdigest()
