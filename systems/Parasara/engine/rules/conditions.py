"""Canonical current-format condition evaluation for Prompt-01 WP10.

This module is deliberately separate from the active legacy/Yoga condition
path.  It accepts only the bare ``type/children`` and ``type/params`` grammar
and reuses one caller-owned :class:`PredicateEvaluator` for all leaf work.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re
from time import perf_counter_ns
from typing import Any

from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.canonical import FrozenMapping
from systems.Parasara.engine.rules.models import (
    ConditionChildResult,
    ConditionNodeDisposition,
    ConditionOperator,
    ConditionResult,
    PredicateError,
    PredicateResult,
    PredicateStatus,
    PredicateTraceStep,
)
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    PreparedAstroState,
)
from systems.Parasara.engine.rules.registry import PredicateRegistryError, get_production_registry


MAX_CONDITION_DEPTH = 64
MAX_CONDITION_NODES = 4096
DEFAULT_ROOT_NODE_ID = "condition.root"

_ROOT_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,255}$")
_TYPE_ID = re.compile(r"^[A-Z][A-Z0-9_]*$")
_LOGICAL = {item.value: item for item in ConditionOperator}
_NONFACTUAL_PRECEDENCE = (
    PredicateStatus.ERROR,
    PredicateStatus.TIMEOUT,
    PredicateStatus.INVALID_PARAMETERS,
    PredicateStatus.MISSING_CAPABILITY,
    PredicateStatus.SKIPPED,
)


@dataclass(frozen=True, slots=True)
class _BoundaryFailure:
    code: str


def _elapsed(start: int) -> float:
    return max(0.0, (perf_counter_ns() - start) / 1_000_000.0)


def _normalized_type(value: Any) -> str | None:
    if type(value) is not str:
        return None
    normalized = value.strip().upper()
    return normalized if normalized else None


def _child_id(node_id: str, index: int) -> str:
    return f"{node_id}.children.{index}"


def _is_child_sequence(node: Any, value: Any) -> bool:
    """Admit raw list syntax or WP12's canonical immutable tuple only."""

    return type(value) is list or (
        isinstance(node, FrozenMapping) and type(value) is tuple
    )


def _preflight(root: Any) -> _BoundaryFailure | None:
    """Check tree-wide cycle/depth/count limits without validating leaf values."""

    count = 0

    def visit(node: Any, depth: int, active: set[int]) -> _BoundaryFailure | None:
        nonlocal count
        count += 1
        if count > MAX_CONDITION_NODES:
            return _BoundaryFailure("condition_node_limit")
        if depth > MAX_CONDITION_DEPTH:
            return _BoundaryFailure("condition_depth_limit")
        if not isinstance(node, Mapping):
            return None
        identity = id(node)
        if identity in active:
            return _BoundaryFailure("condition_cycle")
        active.add(identity)
        try:
            raw_children = node.get("children")
            if _is_child_sequence(node, raw_children):
                list_identity = id(raw_children)
                if list_identity in active:
                    return _BoundaryFailure("condition_cycle")
                active.add(list_identity)
                try:
                    for child in raw_children:
                        failure = visit(child, depth + 1, active)
                        if failure is not None:
                            return failure
                finally:
                    active.remove(list_identity)
        finally:
            active.remove(identity)
        return None

    try:
        return visit(root, 1, set())
    except RecursionError:
        return _BoundaryFailure("condition_depth_limit")


def preflight_condition_tree(root: Any) -> str | None:
    """Return the WP10 fatal tree-boundary code without evaluating a node.

    WP12 reuses this pure check so depth, count, and cycle policy cannot drift
    between definition validation and the defensive runtime boundary.
    """

    failure = _preflight(root)
    return None if failure is None else failure.code


def _trace(
    node_id: str,
    suffix: str,
    operation: str,
    *,
    details: Mapping[str, Any],
    observation: Any,
    parent: str | None = None,
    error_code: str | None = None,
) -> PredicateTraceStep:
    return PredicateTraceStep(
        step_id=f"{node_id}.trace.{suffix}",
        operation=operation,
        details=details,
        observation=observation,
        parent_step_id=parent,
        error_code=error_code,
    )


def _safe_error(
    *, node_id: str, code: str, message: str, details: Mapping[str, Any]
) -> PredicateError:
    return PredicateError(
        code=code,
        message=message,
        predicate_id=node_id,
        details=details,
        recoverable=False,
    )


def _boundary_failure(node_id: str, code: str) -> PredicateResult:
    error = _safe_error(
        node_id="CONDITION_BOUNDARY",
        code=code,
        message="The canonical condition boundary rejected the supplied node.",
        details={"node_id": node_id},
    )
    start = _trace(
        node_id, "start", "condition_boundary_validation",
        details={"node_id": node_id}, observation={"accepted": False}, error_code=code,
    )
    final = _trace(
        node_id, "final", "condition_final_disposition",
        details={"node_id": node_id},
        observation={"matched": False, "status": PredicateStatus.ERROR.value},
        parent=start.step_id, error_code=code,
    )
    return PredicateResult(
        matched=False,
        predicate_id="CONDITION_BOUNDARY",
        predicate_version="1.0.0",
        inputs={},
        evidence={},
        trace_steps=(start, final),
        errors=(error,),
        cache_hit=False,
        evaluation_time_ms=None,
        status=PredicateStatus.ERROR,
    )


def _logical_failure(
    node_id: str,
    operator: ConditionOperator,
    code: str,
    declared_count: int,
) -> ConditionResult:
    error = _safe_error(
        node_id=node_id,
        code=code,
        message="The canonical logical node definition is invalid.",
        details={"node_id": node_id, "operator": operator.value},
    )
    start = _trace(
        node_id, "start", "condition_start",
        details={"node_id": node_id, "operator": operator.value},
        observation={"accepted": False}, error_code=code,
    )
    final = _trace(
        node_id, "final", "condition_final_disposition",
        details={"node_id": node_id, "operator": operator.value},
        observation={"matched": False, "status": PredicateStatus.ERROR.value},
        parent=start.step_id, error_code=code,
    )
    return ConditionResult(
        node_id=node_id,
        operator=operator,
        matched=False,
        status=PredicateStatus.ERROR,
        details={
            "operator": operator.value,
            "declared_child_count": declared_count,
            "evaluated_child_count": 0,
            "skipped_child_count": 0,
            "decisive_child_id": None,
            "decisive_child_index": None,
            "precedence_status": PredicateStatus.ERROR.value,
            "precedence_source_child_id": None,
        },
        children=(),
        errors=(error,),
        trace_steps=(start, final),
        evaluation_time_ms=None,
    )


def _failure_outcome(node: Any, node_id: str, code: str):
    if isinstance(node, Mapping):
        normalized = _normalized_type(node.get("type"))
        operator = _LOGICAL.get(normalized or "")
        if operator is not None:
            children = node.get("children")
            declared_count = len(children) if type(children) is list else 0
            return _logical_failure(node_id, operator, code, declared_count)
    return _boundary_failure(node_id, code)


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
        definition = get_production_registry().lookup(normalized)
    except (PredicateRegistryError, TypeError, ValueError):
        definition = None
    if definition is None:
        return _BoundaryFailure("unknown_condition_type")
    if "params" not in node:
        return _BoundaryFailure("condition_params_missing")
    if not isinstance(node["params"], Mapping):
        return _BoundaryFailure("condition_params_not_mapping")
    return normalized, None, None


def _highest_status(children: tuple[ConditionChildResult, ...]) -> tuple[PredicateStatus, ConditionChildResult] | None:
    for status in _NONFACTUAL_PRECEDENCE:
        for child in children:
            if child.result is not None and child.result.status is status:
                return status, child
    return None


def _summary_error(
    node_id: str, status: PredicateStatus, source: ConditionChildResult
) -> PredicateError:
    child_errors = source.result.errors if source.result is not None else ()
    return _safe_error(
        node_id=node_id,
        code=f"condition_child_{status.value}",
        message="A child produced the selected non-factual condition status.",
        details={
            "child_node_id": source.node_id,
            "child_status": status.value,
            "child_error_codes": tuple(error.code for error in child_errors),
        },
    )


def _evaluate_node(
    node: Any,
    node_id: str,
    state: PreparedAstroState,
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


def evaluate_condition_canonical(
    node: Any,
    state: PreparedAstroState,
    context: PredicateEvaluationContext,
    predicate_evaluator: PredicateEvaluator,
    *,
    root_node_id: str = DEFAULT_ROOT_NODE_ID,
) -> PredicateResult | ConditionResult:
    """Evaluate one raw current-format condition without touching legacy paths."""

    if type(root_node_id) is not str:
        raise TypeError("root_node_id must be a string")
    if not _ROOT_ID.fullmatch(root_node_id):
        raise ValueError("root_node_id must be a stable path identifier")
    if not isinstance(state, PreparedAstroState):
        return _boundary_failure(root_node_id, "condition_state_type_mismatch")
    if not isinstance(context, PredicateEvaluationContext):
        return _boundary_failure(root_node_id, "condition_context_type_mismatch")
    if not isinstance(predicate_evaluator, PredicateEvaluator):
        return _boundary_failure(root_node_id, "condition_evaluator_type_mismatch")
    try:
        failure = _preflight(node)
    except Exception:
        return _boundary_failure(root_node_id, "condition_preflight_error")
    if failure is not None:
        return _failure_outcome(node, root_node_id, failure.code)
    try:
        return _evaluate_node(node, root_node_id, state, context, predicate_evaluator)
    except Exception:
        return _boundary_failure(root_node_id, "condition_evaluator_error")


class ConditionEvaluator:
    """Small instance facade binding one explicit WP09 predicate evaluator."""

    __slots__ = ("_predicate_evaluator",)

    def __init__(self, predicate_evaluator: PredicateEvaluator) -> None:
        if not isinstance(predicate_evaluator, PredicateEvaluator):
            raise TypeError("predicate_evaluator must be a PredicateEvaluator")
        self._predicate_evaluator = predicate_evaluator

    @property
    def predicate_evaluator(self) -> PredicateEvaluator:
        return self._predicate_evaluator

    def evaluate(
        self,
        node: Any,
        state: PreparedAstroState,
        context: PredicateEvaluationContext,
        *,
        root_node_id: str = DEFAULT_ROOT_NODE_ID,
    ) -> PredicateResult | ConditionResult:
        return evaluate_condition_canonical(
            node, state, context, self._predicate_evaluator, root_node_id=root_node_id
        )


__all__ = (
    "DEFAULT_ROOT_NODE_ID", "MAX_CONDITION_DEPTH", "MAX_CONDITION_NODES",
    "ConditionEvaluator", "evaluate_condition_canonical", "preflight_condition_tree",
)
