"""WP10 immutable condition models and canonical serialization contract."""

from dataclasses import FrozenInstanceError, fields, replace
import hashlib
import math

import pytest

from systems.Parasara.engine.rules.canonical import (
    CanonicalValueError,
    condition_result_from_full_data,
    condition_result_from_full_json,
    condition_result_from_logical_data,
    condition_result_from_logical_json,
    condition_result_full_json_bytes,
    condition_result_logical_json_bytes,
    condition_result_logical_sha256,
    condition_result_to_full_data,
    condition_result_to_logical_data,
)
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


def predicate(*, status=PredicateStatus.MATCHED, cache_hit=False, duration=None):
    errors = ()
    if status is PredicateStatus.ERROR:
        errors = (
            PredicateError(
                code="controlled_error",
                message="Controlled failure.",
                predicate_id="PLANET_IN_HOUSE",
                details={"phase": "test"},
                recoverable=False,
            ),
        )
    return PredicateResult(
        matched=status is PredicateStatus.MATCHED,
        predicate_id="PLANET_IN_HOUSE",
        predicate_version="1.0.0",
        inputs={"planet": "Mars", "house": 1},
        evidence={"available": True},
        trace_steps=(
            PredicateTraceStep(
                step_id="predicate.result",
                operation="final_disposition",
                details={"predicate_id": "PLANET_IN_HOUSE"},
                observation={"status": status.value},
            ),
        ),
        errors=errors,
        cache_hit=cache_hit,
        evaluation_time_ms=duration,
        status=status,
    )


def nested(*, duration=None, predicate_duration=None, cache_hit=False):
    leaf = predicate(duration=predicate_duration, cache_hit=cache_hit)
    inner = ConditionResult(
        node_id="condition.root.children.0",
        operator=ConditionOperator.NOT,
        matched=False,
        status=PredicateStatus.UNMATCHED,
        details={"operator": "NOT", "declared_child_count": 1},
        children=(
            ConditionChildResult(
                node_id="condition.root.children.0.children.0",
                child_index=0,
                disposition=ConditionNodeDisposition.EVALUATED,
                result=leaf,
            ),
        ),
        errors=(),
        trace_steps=(),
        evaluation_time_ms=duration,
    )
    return ConditionResult(
        node_id="condition.root",
        operator=ConditionOperator.AND,
        matched=False,
        status=PredicateStatus.UNMATCHED,
        details={"operator": "AND", "declared_child_count": 2},
        children=(
            ConditionChildResult(
                node_id="condition.root.children.0",
                child_index=0,
                disposition=ConditionNodeDisposition.EVALUATED,
                result=inner,
            ),
            ConditionChildResult(
                node_id="condition.root.children.1",
                child_index=1,
                disposition=ConditionNodeDisposition.SKIPPED,
                result=None,
                skip_reason="and_short_circuit_unmatched",
            ),
        ),
        errors=(),
        trace_steps=(),
        evaluation_time_ms=duration,
    )


def test_exact_enum_values_and_field_inventories():
    assert [item.value for item in ConditionOperator] == ["AND", "OR", "NOT"]
    assert [item.value for item in ConditionNodeDisposition] == ["evaluated", "skipped"]
    assert [item.name for item in fields(ConditionChildResult)] == [
        "node_id", "child_index", "disposition", "result", "skip_reason"
    ]
    assert [item.name for item in fields(ConditionResult)] == [
        "node_id", "operator", "matched", "status", "details", "children",
        "errors", "trace_steps", "evaluation_time_ms",
    ]


@pytest.mark.parametrize("status", list(PredicateStatus))
def test_condition_status_matched_invariant(status):
    errors = ()
    if status is PredicateStatus.ERROR:
        errors = (
            PredicateError("condition_error", "Condition failure.", "condition.root", {}, False),
        )
    result = ConditionResult(
        node_id="condition.root",
        operator=ConditionOperator.AND,
        matched=status is PredicateStatus.MATCHED,
        status=status,
        details={"operator": "AND", "declared_child_count": 1},
        children=(),
        errors=errors,
        trace_steps=(),
    )
    assert result.matched is (status is PredicateStatus.MATCHED)


def test_condition_rejects_contradictory_status_and_invalid_telemetry():
    base = dict(
        node_id="condition.root", operator=ConditionOperator.AND,
        details={"operator": "AND", "declared_child_count": 1}, children=(),
        errors=(), trace_steps=(),
    )
    with pytest.raises(ValueError):
        ConditionResult(matched=True, status=PredicateStatus.UNMATCHED, **base)
    for value in (True, -1, math.inf, math.nan, "1"):
        with pytest.raises((TypeError, ValueError)):
            ConditionResult(
                matched=False, status=PredicateStatus.UNMATCHED,
                evaluation_time_ms=value, **base,
            )


def test_child_evaluated_and_skipped_invariants():
    leaf = predicate()
    evaluated = ConditionChildResult(
        node_id="condition.root.children.0", child_index=0,
        disposition=ConditionNodeDisposition.EVALUATED, result=leaf,
    )
    skipped = ConditionChildResult(
        node_id="condition.root.children.1", child_index=1,
        disposition=ConditionNodeDisposition.SKIPPED, result=None,
        skip_reason="or_short_circuit_matched",
    )
    assert evaluated.result is leaf and evaluated.skip_reason is None
    assert skipped.result is None
    invalid = [
        dict(disposition=ConditionNodeDisposition.EVALUATED, result=None, skip_reason=None),
        dict(disposition=ConditionNodeDisposition.EVALUATED, result=leaf, skip_reason="x"),
        dict(disposition=ConditionNodeDisposition.SKIPPED, result=leaf, skip_reason="and_short_circuit_unmatched"),
        dict(disposition=ConditionNodeDisposition.SKIPPED, result=None, skip_reason=None),
        dict(disposition=ConditionNodeDisposition.SKIPPED, result=None, skip_reason="unknown"),
    ]
    for values in invalid:
        with pytest.raises((TypeError, ValueError)):
            ConditionChildResult(node_id="condition.root.children.0", child_index=0, **values)


def test_mixed_predicate_and_nested_children_are_deeply_immutable_and_isolated():
    details = {"operator": "AND", "declared_child_count": 2, "nested": [1, {"x": True}]}
    result = nested()
    mixed = replace(
        result,
        details=details,
        children=(
            ConditionChildResult(
                node_id="condition.root.children.0", child_index=0,
                disposition=ConditionNodeDisposition.EVALUATED, result=predicate(),
            ),
            ConditionChildResult(
                node_id="condition.root.children.1", child_index=1,
                disposition=ConditionNodeDisposition.EVALUATED,
                result=result.children[0].result,
            ),
        ),
    )
    details["nested"][1]["x"] = False
    assert mixed.details["nested"][1]["x"] is True
    assert isinstance(mixed.children[0].result, PredicateResult)
    assert isinstance(mixed.children[1].result, ConditionResult)
    with pytest.raises(FrozenInstanceError):
        mixed.node_id = "changed"
    with pytest.raises(TypeError):
        mixed.details["new"] = True


def test_unsafe_values_cycles_and_invalid_typed_collections_are_rejected():
    cycle = {}
    cycle["self"] = cycle
    for details in ({"unsafe": object()}, cycle):
        with pytest.raises(CanonicalValueError):
            replace(nested(), details=details)
    with pytest.raises(TypeError):
        replace(nested(), children=(object(),))
    with pytest.raises(TypeError):
        replace(nested(), trace_steps=(object(),))
    with pytest.raises(TypeError):
        replace(nested(), errors=(object(),))


def test_logical_equality_and_bytes_exclude_all_recursive_telemetry():
    cold = nested(duration=1.25, predicate_duration=2.5, cache_hit=False)
    warm = nested(duration=99.0, predicate_duration=0.01, cache_hit=True)
    assert cold == warm
    assert condition_result_to_logical_data(cold) == condition_result_to_logical_data(warm)
    assert condition_result_logical_json_bytes(cold) == condition_result_logical_json_bytes(warm)
    assert condition_result_logical_sha256(cold) == condition_result_logical_sha256(warm)
    assert condition_result_to_full_data(cold) != condition_result_to_full_data(warm)
    assert condition_result_full_json_bytes(cold) != condition_result_full_json_bytes(warm)


def test_exact_recursive_projection_shape_and_round_trip():
    result = nested(duration=3.0, predicate_duration=4.0, cache_hit=True)
    logical = condition_result_to_logical_data(result)
    full = condition_result_to_full_data(result)
    assert list(logical) == [
        "node_id", "operator", "matched", "status", "details", "children",
        "errors", "trace_steps",
    ]
    assert list(full) == [*logical, "evaluation_time_ms"]
    assert logical["children"][0]["result_kind"] == "condition"
    assert logical["children"][0]["result"]["children"][0]["result_kind"] == "predicate"
    assert logical["children"][1] == {
        "node_id": "condition.root.children.1",
        "child_index": 1,
        "disposition": "skipped",
        "result_kind": None,
        "result": None,
        "skip_reason": "and_short_circuit_unmatched",
    }
    assert "cache_hit" not in condition_result_logical_json_bytes(result).decode()
    assert condition_result_from_logical_data(logical) == result
    assert condition_result_from_full_data(full) == result
    assert condition_result_from_logical_json(condition_result_logical_json_bytes(result)) == result
    assert condition_result_from_full_json(condition_result_full_json_bytes(result)) == result
    assert len(condition_result_logical_json_bytes(result)) == 1183
    assert condition_result_logical_sha256(result) == "b823a4a2869cd5b33cc6ba178f7b12c40ed28a78e1e8e904bc28ee64fb454245"
    assert len(condition_result_full_json_bytes(result)) == 1275
    assert hashlib.sha256(condition_result_full_json_bytes(result)).hexdigest() == "c009e064f1466ff57994684aa3f217bd6659c9af2302d2c9df79b79a8dcec898"


def test_equivalent_mapping_insertion_order_serializes_identically():
    first = nested()
    second = replace(
        first,
        details={"declared_child_count": 2, "operator": "AND"},
    )
    assert first == second
    assert condition_result_logical_json_bytes(first) == condition_result_logical_json_bytes(second)


@pytest.mark.parametrize("projection", ["logical", "full"])
def test_deserialization_rejects_unknown_missing_or_unsafe_values(projection):
    result = nested()
    data = (
        condition_result_to_logical_data(result)
        if projection == "logical"
        else condition_result_to_full_data(result)
    )
    parser = condition_result_from_logical_data if projection == "logical" else condition_result_from_full_data
    data["unknown"] = True
    with pytest.raises(CanonicalValueError):
        parser(data)
    data.pop("unknown")
    data.pop("node_id")
    with pytest.raises(CanonicalValueError):
        parser(data)


def test_child_order_status_and_skip_reason_change_logical_identity():
    base = nested()
    ordered = replace(
        base,
        children=(
            ConditionChildResult(
                node_id="condition.root.children.0", child_index=0,
                disposition=ConditionNodeDisposition.EVALUATED,
                result=predicate(status=PredicateStatus.MATCHED),
            ),
            ConditionChildResult(
                node_id="condition.root.children.1", child_index=1,
                disposition=ConditionNodeDisposition.EVALUATED,
                result=predicate(status=PredicateStatus.UNMATCHED),
            ),
        ),
    )
    reordered = replace(
        ordered,
        children=(
            replace(ordered.children[0], result=ordered.children[1].result),
            replace(ordered.children[1], result=ordered.children[0].result),
        ),
    )
    assert condition_result_logical_sha256(ordered) != condition_result_logical_sha256(reordered)
    variants = (
        replace(base, status=PredicateStatus.MISSING_CAPABILITY),
        replace(
            base,
            children=(base.children[0], replace(base.children[1], skip_reason="or_short_circuit_matched")),
        ),
    )
    base_hash = condition_result_logical_sha256(base)
    assert all(condition_result_logical_sha256(item) != base_hash for item in variants)
