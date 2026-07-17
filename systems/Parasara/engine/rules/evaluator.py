"""Instance-owned canonical predicate evaluator and bounded logical-result cache."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping
from dataclasses import dataclass, replace
import hashlib
import re
from threading import RLock
from time import perf_counter_ns
from typing import Any

from systems.Parasara.engine.rules.canonical import (
    FrozenMapping,
    canonical_json_bytes,
    freeze_canonical,
)
from systems.Parasara.engine.rules.models import (
    PredicateError,
    PredicateResult,
    PredicateStatus,
    PredicateTraceStep,
)
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    PreparedAstroState,
    prepared_state_sha256,
)
from systems.Parasara.engine.rules.registry import (
    PredicateDefinition,
    PredicateRegistryError,
    get_production_registry,
)


DEFAULT_CACHE_CAPACITY = 256
_MIGRATED_PREDICATES = frozenset({
    "ASPECT_EXISTS",
    "FUNCTIONAL_ROLE",
    "HOUSE_OCCUPANT",
    "PLANET_EXALTED",
    "PLANET_IN_HOUSE",
})
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_PREDICATE_ID = re.compile(r"^[A-Z][A-Z0-9_]*$")
_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def predicate_definition_fingerprint_bytes(definition: PredicateDefinition) -> bytes:
    """Project only definition fields that can change predicate behavior."""

    if not isinstance(definition, PredicateDefinition):
        raise TypeError("definition must be a PredicateDefinition")
    return canonical_json_bytes(
        {
            "parameter_schema": definition.parameter_schema.metadata(),
            "predicate_id": definition.predicate_id,
            "predicate_version": definition.predicate_version,
            "required_capabilities": tuple(
                requirement.metadata() for requirement in definition.required_capabilities
            ),
            "system_scope": definition.system_scope,
        }
    )


def predicate_definition_fingerprint_sha256(definition: PredicateDefinition) -> str:
    return _sha256(predicate_definition_fingerprint_bytes(definition))


def _invoke_handler(
    definition: PredicateDefinition,
    parameters: Mapping[str, Any],
    state: PreparedAstroState,
    context: PredicateEvaluationContext,
) -> PredicateResult:
    """Keep the sole registered-handler invocation inside the typed evaluator."""

    return definition.handler(parameters, state, context)


@dataclass(frozen=True, slots=True)
class PredicateCacheKey:
    """Typed content/version identity for one canonical predicate behavior."""

    system_scope: str
    predicate_id: str
    predicate_version: str
    definition_sha256: str
    parameters_sha256: str
    prepared_state_sha256: str
    context_relevance: str
    relevant_context_sha256: str

    def __post_init__(self) -> None:
        if not isinstance(self.system_scope, str) or not self.system_scope:
            raise ValueError("system_scope must be non-empty")
        if not isinstance(self.predicate_id, str) or not _PREDICATE_ID.fullmatch(self.predicate_id):
            raise ValueError("predicate_id must be canonical")
        if not isinstance(self.predicate_version, str) or not _SEMVER.fullmatch(self.predicate_version):
            raise ValueError("predicate_version must be SemVer")
        if not isinstance(self.context_relevance, str) or not self.context_relevance:
            raise ValueError("context_relevance must be non-empty")
        for name in (
            "definition_sha256",
            "parameters_sha256",
            "prepared_state_sha256",
            "relevant_context_sha256",
        ):
            if not _SHA256.fullmatch(getattr(self, name)):
                raise ValueError(f"{name} must be lowercase SHA-256")


def predicate_cache_key_to_data(key: PredicateCacheKey) -> FrozenMapping:
    if not isinstance(key, PredicateCacheKey):
        raise TypeError("key must be a PredicateCacheKey")
    return FrozenMapping(
        {
            "context_relevance": key.context_relevance,
            "definition_sha256": key.definition_sha256,
            "parameters_sha256": key.parameters_sha256,
            "predicate_id": key.predicate_id,
            "predicate_version": key.predicate_version,
            "prepared_state_sha256": key.prepared_state_sha256,
            "relevant_context_sha256": key.relevant_context_sha256,
            "system_scope": key.system_scope,
        }
    )


def predicate_cache_key_json_bytes(key: PredicateCacheKey) -> bytes:
    return canonical_json_bytes(predicate_cache_key_to_data(key))


def predicate_cache_key_sha256(key: PredicateCacheKey) -> str:
    return _sha256(predicate_cache_key_json_bytes(key))


def build_predicate_cache_key(
    definition: PredicateDefinition,
    normalized_parameters: Mapping[str, Any],
    state: PreparedAstroState,
    *,
    relevant_context: Mapping[str, Any],
    context_relevance: str = "none",
) -> PredicateCacheKey:
    """Build a canonical key after parameter validation and context selection."""

    if not isinstance(definition, PredicateDefinition):
        raise TypeError("definition must be a PredicateDefinition")
    if not isinstance(state, PreparedAstroState):
        raise TypeError("state must be PreparedAstroState")
    if state.system_scope != definition.system_scope:
        raise ValueError("state and definition system scopes must agree")
    if not isinstance(normalized_parameters, Mapping):
        raise TypeError("normalized_parameters must be a mapping")
    if not isinstance(relevant_context, Mapping):
        raise TypeError("relevant_context must be a mapping")
    if not isinstance(context_relevance, str) or not context_relevance:
        raise ValueError("context_relevance must be non-empty")

    parameters = freeze_canonical(normalized_parameters, path="$.normalized_parameters")
    selected_context = freeze_canonical(relevant_context, path="$.relevant_context")
    return PredicateCacheKey(
        system_scope=definition.system_scope,
        predicate_id=definition.predicate_id,
        predicate_version=definition.predicate_version,
        definition_sha256=predicate_definition_fingerprint_sha256(definition),
        parameters_sha256=_sha256(canonical_json_bytes(parameters)),
        prepared_state_sha256=prepared_state_sha256(state),
        context_relevance=context_relevance,
        relevant_context_sha256=_sha256(canonical_json_bytes(selected_context)),
    )


class PredicateResultCache:
    """Synchronized deterministic LRU of immutable telemetry-free results."""

    __slots__ = ("_capacity", "_entries", "_frozen", "_lock")

    def __init__(self, *, capacity: int = DEFAULT_CACHE_CAPACITY) -> None:
        if type(capacity) is not int:
            raise TypeError("capacity must be a non-Boolean integer")
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._entries: OrderedDict[PredicateCacheKey, PredicateResult] = OrderedDict()
        self._frozen = False
        self._lock = RLock()

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._entries)

    @property
    def frozen(self) -> bool:
        with self._lock:
            return self._frozen

    def get(self, key: PredicateCacheKey) -> PredicateResult | None:
        if not isinstance(key, PredicateCacheKey):
            raise TypeError("key must be a PredicateCacheKey")
        with self._lock:
            if self._frozen:
                return self._entries.get(key)
            value = self._entries.pop(key, None)
            if value is not None:
                self._entries[key] = value
            return value

    def peek(self, key: PredicateCacheKey) -> PredicateResult | None:
        if not isinstance(key, PredicateCacheKey):
            raise TypeError("key must be a PredicateCacheKey")
        with self._lock:
            return self._entries.get(key)

    def put(self, key: PredicateCacheKey, result: PredicateResult) -> bool:
        if not isinstance(key, PredicateCacheKey):
            raise TypeError("key must be a PredicateCacheKey")
        if not isinstance(result, PredicateResult):
            raise TypeError("result must be a canonical PredicateResult")
        if result.status not in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED):
            return False
        stored = replace(result, cache_hit=False, evaluation_time_ms=None)
        with self._lock:
            if self._frozen:
                return False
            self._entries.pop(key, None)
            self._entries[key] = stored
            while len(self._entries) > self._capacity:
                self._entries.popitem(last=False)
            return True

    def clear(self) -> None:
        """Remove retained values even after freeze; frozen state remains set."""

        with self._lock:
            self._entries.clear()

    def freeze(self) -> None:
        with self._lock:
            self._frozen = True

    def keys(self) -> tuple[PredicateCacheKey, ...]:
        with self._lock:
            return tuple(self._entries)


def _start_telemetry() -> int:
    return perf_counter_ns()


def _elapsed_milliseconds(start: int) -> float:
    return max(0.0, (perf_counter_ns() - start) / 1_000_000.0)


def _safe_predicate_id(requested: Any) -> str:
    if isinstance(requested, str):
        normalized = requested.strip().upper()
        if _PREDICATE_ID.fullmatch(normalized):
            return normalized
    return "UNKNOWN"


def _error_result(
    predicate_id: str,
    predicate_version: str,
    code: str,
    message: str,
    *,
    duration: float,
) -> PredicateResult:
    error = PredicateError(
        code=code,
        message=message,
        predicate_id=predicate_id,
        details={"predicate_id": predicate_id},
        recoverable=False,
    )
    execution = PredicateTraceStep(
        step_id="predicate_evaluator.execution",
        operation="canonical_evaluation",
        details={"predicate_id": predicate_id},
        observation={"completed": False},
        error_code=code,
    )
    final = PredicateTraceStep(
        step_id="predicate_evaluator.result",
        operation="final_disposition",
        details={"predicate_id": predicate_id},
        observation={"matched": False, "status": PredicateStatus.ERROR.value},
        parent_step_id=execution.step_id,
    )
    return PredicateResult(
        matched=False,
        predicate_id=predicate_id,
        predicate_version=predicate_version,
        inputs={},
        evidence={},
        trace_steps=(execution, final),
        errors=(error,),
        cache_hit=False,
        evaluation_time_ms=duration,
        status=PredicateStatus.ERROR,
    )


class PredicateEvaluator:
    """Explicit canonical evaluator with an isolated cache instance."""

    __slots__ = ("_cache",)

    def __init__(self, *, capacity: int = DEFAULT_CACHE_CAPACITY) -> None:
        self._cache = PredicateResultCache(capacity=capacity)

    @property
    def cache(self) -> PredicateResultCache:
        return self._cache

    @property
    def capacity(self) -> int:
        return self._cache.capacity

    @property
    def cache_size(self) -> int:
        return self._cache.size

    @property
    def cache_frozen(self) -> bool:
        return self._cache.frozen

    def clear_cache(self) -> None:
        self._cache.clear()

    def freeze_cache(self) -> None:
        self._cache.freeze()

    def evaluate(
        self,
        predicate_id: Any,
        parameters: Any,
        state: PreparedAstroState,
        context: PredicateEvaluationContext,
        *,
        use_cache: bool = True,
    ) -> PredicateResult:
        if type(use_cache) is not bool:
            raise TypeError("use_cache must be a Boolean")
        start = _start_telemetry()
        requested_id = _safe_predicate_id(predicate_id)
        try:
            definition = get_production_registry().lookup(predicate_id)
        except (PredicateRegistryError, TypeError, ValueError):
            definition = None
        if definition is None:
            return _error_result(
                requested_id,
                "0.0.0",
                "unknown_predicate",
                "The requested canonical predicate is unknown.",
                duration=_elapsed_milliseconds(start),
            )
        canonical_id = definition.predicate_id
        version = definition.predicate_version
        if canonical_id not in _MIGRATED_PREDICATES:
            return _error_result(
                canonical_id,
                version,
                "predicate_not_migrated",
                "The predicate is not available on the canonical evaluator boundary.",
                duration=_elapsed_milliseconds(start),
            )
        if not isinstance(state, PreparedAstroState) or not isinstance(context, PredicateEvaluationContext):
            return _error_result(
                canonical_id,
                version,
                "canonical_boundary_type_mismatch",
                "Canonical evaluation requires prepared state and typed context.",
                duration=_elapsed_milliseconds(start),
            )
        if state.system_scope != definition.system_scope or context.system_scope != definition.system_scope:
            return _error_result(
                canonical_id,
                version,
                "canonical_boundary_scope_mismatch",
                "Canonical state, context, and predicate scopes must agree.",
                duration=_elapsed_milliseconds(start),
            )

        validation = definition.parameter_schema.validate(parameters)
        if not validation.valid:
            result = _invoke_handler(definition, parameters, state, context)
            return replace(
                result,
                cache_hit=False,
                evaluation_time_ms=_elapsed_milliseconds(start),
            )
        normalized = validation.normalized_inputs
        if normalized is None:
            return _error_result(
                canonical_id,
                version,
                "parameter_validation_contract_error",
                "Canonical parameter validation did not produce normalized inputs.",
                duration=_elapsed_milliseconds(start),
            )
        if canonical_id == "FUNCTIONAL_ROLE":
            relevant_context = {"selected_planets": context.selected_planets}
            context_relevance = "selected_planets"
        else:
            relevant_context = {}
            context_relevance = "none"
        key = build_predicate_cache_key(
            definition,
            normalized,
            state,
            relevant_context=relevant_context,
            context_relevance=context_relevance,
        )
        if use_cache:
            stored = self._cache.get(key)
            if stored is not None:
                return replace(
                    stored,
                    cache_hit=True,
                    evaluation_time_ms=_elapsed_milliseconds(start),
                )

        result = _invoke_handler(definition, normalized, state, context)
        if use_cache and definition.cacheable and definition.deterministic:
            self._cache.put(key, result)
        return replace(
            result,
            cache_hit=False,
            evaluation_time_ms=_elapsed_milliseconds(start),
        )


__all__ = (
    "DEFAULT_CACHE_CAPACITY",
    "PredicateCacheKey",
    "PredicateEvaluator",
    "PredicateResultCache",
    "build_predicate_cache_key",
    "predicate_cache_key_json_bytes",
    "predicate_cache_key_sha256",
    "predicate_cache_key_to_data",
    "predicate_definition_fingerprint_bytes",
    "predicate_definition_fingerprint_sha256",
)
