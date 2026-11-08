"""Authority-bound V2 evaluator; protected result and logical semantics retained."""
from __future__ import annotations
from collections import OrderedDict
from dataclasses import replace
from threading import RLock
import hashlib
from .evaluator import PredicateEvaluator, predicate_definition_fingerprint_sha256, _error_result
from .conditions import ConditionEvaluator, DEFAULT_ROOT_NODE_ID, _ROOT_ID, _preflight, _boundary_failure
from .canonical import canonical_json_bytes
from .prepared_state import context_sha256
from .aspect_contract_v2 import (
    PreparedAstroStateV2, get_registry_v2, require_v2_authority,
    state_sha256_v2, registry_fingerprint, implementation_digest,
)
from .conditions import (
    Any,
    ConditionChildResult,
    ConditionNodeDisposition,
    ConditionOperator,
    ConditionResult,
    Mapping,
    PredicateEvaluationContext,
    PredicateRegistryError,
    PredicateResult,
    PredicateStatus,
    _BoundaryFailure,
    _LOGICAL,
    _TYPE_ID,
    _child_id,
    _elapsed,
    _failure_outcome,
    _highest_status,
    _is_child_sequence,
    _safe_error,
    _summary_error,
    _trace,
    perf_counter_ns,
)


def _validate_node(node: Any) -> tuple[str, ConditionOperator | None, list | None] | _BoundaryFailure:
    if not isinstance(node, Mapping):
        return _BoundaryFailure("condition_node_not_mapping")
    keys = tuple(node.keys())
    if any(type(key) is not str for key in keys):
        return _BoundaryFailure("condition_unknown_fields")
    if "type" not in node:
        return _BoundaryFailure("condition_unknown_fields" if keys else "condition_type_missing")
    raw_type = node["type"]
    if type(raw_type) is not str:
        return _BoundaryFailure("condition_type_not_string")
    normalized = raw_type.strip().upper()
    if not normalized:
        return _BoundaryFailure("condition_type_blank")

    operator = _LOGICAL.get(normalized)
    if operator is not None:
        if set(keys) - {"type", "children"}:
            return _BoundaryFailure("condition_unknown_fields")
        if "children" not in node:
            return _BoundaryFailure("condition_children_missing")
        children = node["children"]
        if not _is_child_sequence(node, children):
            return _BoundaryFailure("condition_children_not_list")
        if operator in (ConditionOperator.AND, ConditionOperator.OR) and not children:
            return _BoundaryFailure("condition_empty_operator")
        if operator is ConditionOperator.NOT and len(children) != 1:
            return _BoundaryFailure("condition_not_arity")
        return normalized, operator, children

    if "children" in node and not (set(keys) - {"type", "children"}):
        return _BoundaryFailure("unknown_condition_type")
    if set(keys) - {"type", "params"}:
        return _BoundaryFailure("condition_unknown_fields")
    if not _TYPE_ID.fullmatch(normalized):
        return _BoundaryFailure("unknown_condition_type")
    try:
        definition = get_registry_v2().lookup(normalized)
    except (PredicateRegistryError, TypeError, ValueError):
        definition = None
    if definition is None:
        return _BoundaryFailure("unknown_condition_type")
    if "params" not in node:
        return _BoundaryFailure("condition_params_missing")
    if not isinstance(node["params"], Mapping):
        return _BoundaryFailure("condition_params_not_mapping")
    return normalized, None, None

def _evaluate_node(
    node: Any,
    node_id: str,
    state: PreparedAstroStateV2,
    context: PredicateEvaluationContext,
    predicate_evaluator: PredicateEvaluator,
):
    validation = _validate_node(node)
    if isinstance(validation, _BoundaryFailure):
        return _failure_outcome(node, node_id, validation.code)
    normalized, operator, children_nodes = validation
    if operator is None:
        try:
            return predicate_evaluator.evaluate(normalized, node["params"], state, context)
        except Exception:
            error = _safe_error(
                node_id=normalized,
                code="condition_leaf_evaluator_error",
                message="The canonical leaf evaluator failed safely.",
                details={"node_id": node_id, "predicate_id": normalized},
            )
            execution = _trace(
                node_id, "leaf", "condition_leaf_evaluation",
                details={"node_id": node_id, "predicate_id": normalized},
                observation={"completed": False}, error_code=error.code,
            )
            return PredicateResult(
                matched=False,
                predicate_id=normalized,
                predicate_version="0.0.0",
                inputs={}, evidence={}, trace_steps=(execution,), errors=(error,),
                cache_hit=False, evaluation_time_ms=None, status=PredicateStatus.ERROR,
            )

    assert children_nodes is not None
    started = perf_counter_ns()
    start_step = _trace(
        node_id, "start", "condition_start",
        details={"node_id": node_id, "operator": operator.value},
        observation={"declared_child_count": len(children_nodes)},
    )
    traces = [start_step]
    children: list[ConditionChildResult] = []
    decisive: ConditionChildResult | None = None
    short_reason: str | None = None

    for index, child_node in enumerate(children_nodes):
        child_node_id = _child_id(node_id, index)
        outcome = _evaluate_node(child_node, child_node_id, state, context, predicate_evaluator)
        child = ConditionChildResult(
            node_id=child_node_id,
            child_index=index,
            disposition=ConditionNodeDisposition.EVALUATED,
            result=outcome,
        )
        children.append(child)
        traces.append(
            _trace(
                node_id, f"child.{index}", "condition_child_result",
                details={"child_index": index, "child_node_id": child_node_id},
                observation={"matched": outcome.matched, "status": outcome.status.value},
                parent=start_step.step_id,
            )
        )
        if operator is ConditionOperator.AND and outcome.status is PredicateStatus.UNMATCHED:
            decisive = child
            short_reason = "and_short_circuit_unmatched"
        elif operator is ConditionOperator.OR and outcome.status is PredicateStatus.MATCHED:
            decisive = child
            short_reason = "or_short_circuit_matched"
        if short_reason is not None:
            traces.append(
                _trace(
                    node_id, "short_circuit", "condition_short_circuit",
                    details={"child_index": index, "child_node_id": child_node_id},
                    observation={"reason": short_reason}, parent=start_step.step_id,
                )
            )
            for skipped_index in range(index + 1, len(children_nodes)):
                skipped_id = _child_id(node_id, skipped_index)
                children.append(
                    ConditionChildResult(
                        node_id=skipped_id,
                        child_index=skipped_index,
                        disposition=ConditionNodeDisposition.SKIPPED,
                        result=None,
                        skip_reason=short_reason,
                    )
                )
                traces.append(
                    _trace(
                        node_id, f"child.{skipped_index}", "condition_child_skipped",
                        details={"child_index": skipped_index, "child_node_id": skipped_id},
                        observation={"reason": short_reason}, parent=start_step.step_id,
                    )
                )
            break

    child_tuple = tuple(children)
    precedence = _highest_status(child_tuple)
    if operator is ConditionOperator.NOT:
        only = child_tuple[0]
        assert only.result is not None
        if only.result.status is PredicateStatus.MATCHED:
            final_status = PredicateStatus.UNMATCHED
        elif only.result.status is PredicateStatus.UNMATCHED:
            final_status = PredicateStatus.MATCHED
        else:
            final_status = only.result.status
            precedence = (final_status, only)
    elif operator is ConditionOperator.OR and decisive is not None:
        final_status = PredicateStatus.MATCHED
        precedence = None
    elif operator is ConditionOperator.AND and decisive is not None:
        prior = tuple(child for child in child_tuple[: decisive.child_index] if child.result is not None)
        precedence = _highest_status(prior)
        final_status = precedence[0] if precedence is not None else PredicateStatus.UNMATCHED
    elif precedence is not None:
        final_status = precedence[0]
    elif operator is ConditionOperator.AND:
        final_status = PredicateStatus.MATCHED
    else:
        final_status = PredicateStatus.UNMATCHED

    if precedence is not None:
        traces.append(
            _trace(
                node_id, "precedence", "condition_status_precedence",
                details={"child_node_id": precedence[1].node_id},
                observation={"status": precedence[0].value}, parent=start_step.step_id,
            )
        )
    traces.append(
        _trace(
            node_id, "final", "condition_final_disposition",
            details={"node_id": node_id, "operator": operator.value},
            observation={
                "matched": final_status is PredicateStatus.MATCHED,
                "status": final_status.value,
            },
            parent=start_step.step_id,
        )
    )
    skipped_count = sum(
        child.disposition is ConditionNodeDisposition.SKIPPED for child in child_tuple
    )
    errors = ()
    if precedence is not None:
        errors = (_summary_error(node_id, precedence[0], precedence[1]),)
    return ConditionResult(
        node_id=node_id,
        operator=operator,
        matched=final_status is PredicateStatus.MATCHED,
        status=final_status,
        details={
            "operator": operator.value,
            "declared_child_count": len(children_nodes),
            "evaluated_child_count": len(child_tuple) - skipped_count,
            "skipped_child_count": skipped_count,
            "decisive_child_id": decisive.node_id if decisive is not None else None,
            "decisive_child_index": decisive.child_index if decisive is not None else None,
            "precedence_status": precedence[0].value if precedence is not None else None,
            "precedence_source_child_id": precedence[1].node_id if precedence is not None else None,
        },
        children=child_tuple,
        errors=errors,
        trace_steps=tuple(traces),
        evaluation_time_ms=_elapsed(started),
    )

class _V2ResultCache:
    """Synchronized bounded cache whose keys belong exclusively to V2."""
    def __init__(self, capacity):
        self._capacity, self._frozen = capacity, False
        self._entries, self._lock = OrderedDict(), RLock()

    @property
    def capacity(self):
        return self._capacity

    @property
    def size(self):
        with self._lock:
            return len(self._entries)

    @property
    def frozen(self):
        with self._lock:
            return self._frozen

    @staticmethod
    def _validate_key(key):
        if not isinstance(key, str) or len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
            raise TypeError("V2 cache key must be a canonical digest")

    def get(self, key):
        self._validate_key(key)
        with self._lock:
            result = self._entries.get(key)
            if result is not None and not self._frozen:
                self._entries.move_to_end(key)
            return result

    def peek(self, key):
        self._validate_key(key)
        with self._lock:
            return self._entries.get(key)

    def put(self, key, result):
        self._validate_key(key)
        if not isinstance(result, PredicateResult):
            raise TypeError("V2 cache requires a PredicateResult")
        if result.status not in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED):
            return False
        with self._lock:
            if self._frozen or not self._capacity:
                return False
            self._entries[key] = replace(result, cache_hit=False, evaluation_time_ms=None)
            self._entries.move_to_end(key)
            while len(self._entries) > self._capacity:
                self._entries.popitem(last=False)
            return True

    def clear(self):
        with self._lock:
            self._entries.clear()

    def freeze(self):
        with self._lock:
            self._frozen = True

    def keys(self):
        with self._lock:
            return tuple(self._entries)


class PredicateEvaluatorV2(PredicateEvaluator):
    """An isolated bounded LRU; only definitive results enter this cache."""
    def __init__(self, *, resolved_versions, capacity=256):
        require_v2_authority(resolved_versions)
        super().__init__(resolved_versions=resolved_versions, capacity=capacity)
        self._cache = _V2ResultCache(capacity)

    def evaluate(self, predicate_id, parameters, state, context, *, use_cache=True):
        if type(use_cache) is not bool:
            raise TypeError("use_cache must be a Boolean")
        if not isinstance(state, PreparedAstroStateV2) or not isinstance(context, PredicateEvaluationContext):
            return _error_result("UNKNOWN", "0.0.0", "canonical_boundary_type_mismatch",
                "V2 evaluation requires typed state and context.", duration=0)
        state.require_authority(self._resolved_versions)
        try:
            definition = get_registry_v2().lookup(predicate_id)
        except (ValueError, TypeError):
            definition = None
        if definition is None:
            return _error_result("UNKNOWN", "0.0.0", "unknown_predicate", "Unknown predicate.", duration=0)
        # Every V2 key includes the full V2 digest, including source coverage.
        # Non-aspect handlers receive only the unchanged six-capability view.
        handler_state = state if definition.predicate_id == "ASPECT_EXISTS" else state._legacy
        validation = definition.parameter_schema.validate(parameters)
        if not validation.valid:
            return definition.handler(parameters, handler_state, context)
        key = hashlib.sha256(canonical_json_bytes({
            "profile": "source_scoped_aspects_v2", "registry": registry_fingerprint(),
            "components": self.predicate_component_fingerprint_sha256,
            "manifest": self._resolved_versions.manifest.manifest_fingerprint_sha256,
            "definition": predicate_definition_fingerprint_sha256(definition),
            "predicate_version": definition.predicate_version,
            "inputs": validation.normalized_inputs, "context": context_sha256(context),
            "state": state_sha256_v2(state),
        })).hexdigest()
        if use_cache:
            cached = self._cache.get(key)
            if cached is not None:
                return replace(cached, cache_hit=True)
        result = definition.handler(validation.normalized_inputs, handler_state, context)
        if use_cache and definition.cacheable and definition.deterministic:
            self._cache.put(key, result)
        return result


class ConditionEvaluatorV2(ConditionEvaluator):
    def __init__(self, predicate_evaluator):
        if not isinstance(predicate_evaluator, PredicateEvaluatorV2):
            raise TypeError("V2 conditions require a V2 predicate evaluator")
        super().__init__(predicate_evaluator)

    def evaluate(self, node, state, context, *, root_node_id=DEFAULT_ROOT_NODE_ID):
        if not isinstance(root_node_id, str) or not _ROOT_ID.fullmatch(root_node_id):
            raise ValueError("invalid condition root identifier")
        if not isinstance(state, PreparedAstroStateV2) or not isinstance(context, PredicateEvaluationContext):
            return _boundary_failure(root_node_id, "condition_state_type_mismatch")
        state.require_authority(self.predicate_evaluator._resolved_versions)
        failure = _preflight(node)
        if failure is not None:
            return _failure_outcome(node, root_node_id, failure.code)
        return _evaluate_node(node, root_node_id, state, context, self.predicate_evaluator)


CONDITION_CONTENT_SHA256 = implementation_digest(
    "evaluator_v2.py", "aspect_contract_v2.py", "conditions.py", "models.py",
    "evaluator.py", "canonical.py", "prepared_state.py", "registry.py", "parameters.py",
    "capabilities.py", "canonical_predicates.py", "../capability.py", "../versioning.py",
)
