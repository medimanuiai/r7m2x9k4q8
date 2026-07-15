"""WP02 contract tests for canonical immutable predicate-domain models."""

from dataclasses import FrozenInstanceError, fields, replace
import io
import json
import math

import pytest

from systems.Parasara.engine.rules.canonical import CanonicalValueError
from systems.Parasara.engine.rules import engine
from systems.Parasara.engine.rules.models import (
    PredicateError,
    PredicateResult,
    PredicateStatus,
    PredicateTraceStep,
)


STATUSES = [
    PredicateStatus.MATCHED,
    PredicateStatus.UNMATCHED,
    PredicateStatus.MISSING_CAPABILITY,
    PredicateStatus.INVALID_PARAMETERS,
    PredicateStatus.ERROR,
    PredicateStatus.TIMEOUT,
    PredicateStatus.SKIPPED,
]


def make_error(code="predicate_failure"):
    return PredicateError(
        code=code,
        message="Safe predicate failure",
        predicate_id="PLANET_IN_HOUSE",
        details={"phase": "evaluation"},
        recoverable=False,
    )


def make_trace(step_id="root/planet", operation="lookup_planet"):
    return PredicateTraceStep(
        step_id=step_id,
        operation=operation,
        details={"planet": "Mars"},
        observation={"present": True},
    )


def make_result(**overrides):
    values = {
        "matched": False,
        "predicate_id": "PLANET_IN_HOUSE",
        "predicate_version": "1.0.0",
        "inputs": {"planet": "Mars", "house": 1},
        "evidence": {"actual_house": 2},
        "trace_steps": (make_trace(),),
        "errors": (),
        "cache_hit": False,
        "evaluation_time_ms": None,
        "status": PredicateStatus.UNMATCHED,
    }
    values.update(overrides)
    return PredicateResult(**values)


def test_status_has_exactly_the_seven_locked_string_values():
    assert list(PredicateStatus) == STATUSES
    assert [status.value for status in PredicateStatus] == [
        "matched",
        "unmatched",
        "missing_capability",
        "invalid_parameters",
        "error",
        "timeout",
        "skipped",
    ]
    assert all(isinstance(status, str) for status in PredicateStatus)
    assert len(PredicateStatus.__members__) == 7
    assert json.dumps(PredicateStatus.MATCHED) == '"matched"'


@pytest.mark.parametrize("status", STATUSES)
def test_status_constructs_deterministically_from_each_exact_value(status):
    assert PredicateStatus(status.value) is status


@pytest.mark.parametrize("value", ["evaluated", "unknown", "success", "MATCHED", "", None])
def test_status_rejects_invalid_or_alias_values(value):
    with pytest.raises((ValueError, TypeError)):
        PredicateStatus(value)


def test_models_have_exact_locked_field_inventories():
    assert [field.name for field in fields(PredicateError)] == [
        "code",
        "message",
        "predicate_id",
        "details",
        "recoverable",
    ]
    assert [field.name for field in fields(PredicateTraceStep)] == [
        "step_id",
        "operation",
        "details",
        "observation",
        "parent_step_id",
        "error_code",
    ]
    assert [field.name for field in fields(PredicateResult)] == [
        "matched",
        "predicate_id",
        "predicate_version",
        "inputs",
        "evidence",
        "trace_steps",
        "errors",
        "cache_hit",
        "evaluation_time_ms",
        "status",
    ]


@pytest.mark.parametrize("status", STATUSES)
def test_valid_result_constructs_for_every_status(status):
    errors = (make_error(),) if status is PredicateStatus.ERROR else ()
    result = make_result(
        matched=status is PredicateStatus.MATCHED,
        status=status,
        errors=errors,
    )
    assert result.status is status
    assert result.matched is (status is PredicateStatus.MATCHED)


@pytest.mark.parametrize(
    ("matched", "status"),
    [
        (False, PredicateStatus.MATCHED),
        (True, PredicateStatus.UNMATCHED),
        (True, PredicateStatus.MISSING_CAPABILITY),
        (True, PredicateStatus.INVALID_PARAMETERS),
        (True, PredicateStatus.ERROR),
        (True, PredicateStatus.TIMEOUT),
        (True, PredicateStatus.SKIPPED),
    ],
)
def test_matched_status_truth_table_rejects_contradictions(matched, status):
    errors = (make_error(),) if status is PredicateStatus.ERROR else ()
    with pytest.raises(ValueError):
        make_result(matched=matched, status=status, errors=errors)


def test_error_status_requires_at_least_one_typed_error():
    with pytest.raises(ValueError):
        make_result(status=PredicateStatus.ERROR, errors=())
    assert make_result(status=PredicateStatus.ERROR, errors=(make_error(),)).errors


@pytest.mark.parametrize("status", [PredicateStatus.MATCHED, PredicateStatus.UNMATCHED])
def test_ordinary_factual_statuses_reject_errors(status):
    with pytest.raises(ValueError):
        make_result(
            matched=status is PredicateStatus.MATCHED,
            status=status,
            errors=(make_error(),),
        )


@pytest.mark.parametrize(("field_name", "value"), [("matched", 1), ("cache_hit", 0)])
def test_result_boolean_fields_are_strict(field_name, value):
    with pytest.raises(TypeError):
        make_result(**{field_name: value})


@pytest.mark.parametrize("field_name", ["predicate_id", "predicate_version"])
@pytest.mark.parametrize("value", ["", "   ", 1, None])
def test_result_identity_and_version_require_nonempty_strings(field_name, value):
    with pytest.raises((TypeError, ValueError)):
        make_result(**{field_name: value})


def test_result_requires_a_predicate_status_instance():
    with pytest.raises(TypeError):
        make_result(status="unmatched")


@pytest.mark.parametrize("value", [None, 0, 12, 0.0, 12.5])
def test_result_accepts_none_or_finite_nonnegative_telemetry(value):
    assert make_result(evaluation_time_ms=value).evaluation_time_ms == value


@pytest.mark.parametrize("value", [-1, -0.1, True, False, math.nan, math.inf, -math.inf, "1"])
def test_result_rejects_invalid_telemetry(value):
    with pytest.raises((TypeError, ValueError)):
        make_result(evaluation_time_ms=value)


@pytest.mark.parametrize(
    ("field_name", "value"),
    [("inputs", None), ("evidence", None), ("trace_steps", None), ("errors", None)],
)
def test_result_rejects_none_for_required_collections(field_name, value):
    with pytest.raises(TypeError):
        make_result(**{field_name: value})


def test_result_rejects_invalid_trace_and_error_elements():
    with pytest.raises(TypeError):
        make_result(trace_steps=({"step_id": "root"},))
    with pytest.raises(TypeError):
        make_result(errors=({"code": "failure"},))


def test_result_defaults_are_independent_empty_immutable_values():
    first = PredicateResult(
        matched=False,
        predicate_id="A",
        predicate_version="1",
        status=PredicateStatus.UNMATCHED,
    )
    second = PredicateResult(
        matched=False,
        predicate_id="A",
        predicate_version="1",
        status=PredicateStatus.UNMATCHED,
    )
    assert dict(first.inputs) == dict(first.evidence) == {}
    assert first.trace_steps == first.errors == ()
    assert first.cache_hit is False
    assert first.evaluation_time_ms is None
    assert first.inputs is not second.inputs
    assert first.evidence is not second.evidence


@pytest.mark.parametrize("field_name", ["code", "message", "predicate_id"])
@pytest.mark.parametrize("value", ["", "   ", 1, None])
def test_error_rejects_empty_or_invalid_strings(field_name, value):
    values = {
        "code": "failure",
        "message": "Safe failure",
        "predicate_id": "PREDICATE",
        "details": {},
        "recoverable": False,
    }
    values[field_name] = value
    with pytest.raises((TypeError, ValueError)):
        PredicateError(**values)


@pytest.mark.parametrize("value", [0, 1, "false", None])
def test_error_recoverable_is_a_strict_boolean(value):
    with pytest.raises(TypeError):
        PredicateError("failure", "Safe failure", "PREDICATE", {}, value)


def test_error_details_are_deeply_immutable_and_isolated_from_caller_mutation():
    original = {"nested": {"items": ["one", {"values": ["a", "b"]}]}}
    error = PredicateError("failure", "Safe failure", "PREDICATE", original, True)
    original["nested"]["items"][0] = "changed"
    original["nested"]["items"][1]["values"].append("c")

    assert error.details["nested"]["items"][0] == "one"
    assert error.details["nested"]["items"][1]["values"] == ("a", "b")
    with pytest.raises(TypeError):
        error.details["new"] = "value"
    with pytest.raises(TypeError):
        error.details["nested"]["items"][1]["values"] += ("c",)


def test_error_details_reject_unsafe_runtime_objects():
    try:
        raise RuntimeError()
    except RuntimeError as exc:
        traceback_object = exc.__traceback__
        unsafe_values = [exc, traceback_object, lambda: None, io.StringIO("open")]

    for unsafe in unsafe_values:
        with pytest.raises((TypeError, CanonicalValueError)):
            PredicateError("failure", "Safe failure", "PREDICATE", {"unsafe": unsafe}, False)


@pytest.mark.parametrize("unordered", [{1, 2}, frozenset({1, 2})])
def test_canonical_model_collections_reject_unordered_sets(unordered):
    with pytest.raises(CanonicalValueError, match=r"^\$\.details\.values: unsupported set$"):
        PredicateError("failure", "Safe failure", "PREDICATE", {"values": unordered}, False)


def test_trace_supports_valid_root_and_child_steps():
    root = make_trace()
    child = PredicateTraceStep(
        step_id="root/planet/house",
        operation="compare_house",
        details={"expected": 1},
        observation={"actual": 2},
        parent_step_id=root.step_id,
        error_code="house_mismatch",
    )
    assert root.parent_step_id is None
    assert root.error_code is None
    assert child.parent_step_id == root.step_id
    assert child.error_code == "house_mismatch"


@pytest.mark.parametrize("field_name", ["step_id", "operation"])
@pytest.mark.parametrize("value", ["", "   ", 1, None])
def test_trace_rejects_invalid_required_identifiers(field_name, value):
    values = {
        "step_id": "root",
        "operation": "lookup",
        "details": {},
        "observation": None,
    }
    values[field_name] = value
    with pytest.raises((TypeError, ValueError)):
        PredicateTraceStep(**values)


@pytest.mark.parametrize("field_name", ["parent_step_id", "error_code"])
@pytest.mark.parametrize("value", ["", "   ", 1])
def test_trace_rejects_invalid_optional_references(field_name, value):
    values = {
        "step_id": "root",
        "operation": "lookup",
        "details": {},
        "observation": None,
        field_name: value,
    }
    with pytest.raises((TypeError, ValueError)):
        PredicateTraceStep(**values)


def test_trace_details_and_observation_are_deeply_immutable_and_isolated():
    details = {"expected": {"houses": [1, 4]}}
    observation = {"actual": [{"house": 2}]}
    trace = PredicateTraceStep("root", "compare", details, observation)
    details["expected"]["houses"].append(7)
    observation["actual"][0]["house"] = 10

    assert trace.details["expected"]["houses"] == (1, 4)
    assert trace.observation["actual"][0]["house"] == 2
    with pytest.raises(TypeError):
        trace.details["expected"] = {}
    with pytest.raises(TypeError):
        trace.observation["actual"][0]["house"] = 3


def test_result_preserves_semantic_trace_tuple_order():
    first = make_trace("root/1")
    second = make_trace("root/2")
    result = make_result(trace_steps=[first, second])
    assert result.trace_steps == (first, second)


def test_trace_has_no_telemetry_or_random_identity_fields():
    assert {field.name for field in fields(PredicateTraceStep)} == {
        "step_id",
        "operation",
        "details",
        "observation",
        "parent_step_id",
        "error_code",
    }


@pytest.mark.parametrize(
    "model",
    [
        make_error(),
        make_trace(),
        make_result(),
    ],
)
def test_model_fields_are_frozen(model):
    with pytest.raises(FrozenInstanceError):
        model.__setattr__(next(iter(model.__dataclass_fields__)), "changed")


def test_status_member_state_is_immutable():
    with pytest.raises(AttributeError):
        PredicateStatus.MATCHED.value = "changed"


def test_result_deep_freezes_all_caller_owned_values_and_resists_later_mutation():
    inputs = {"planets": ["Mars"]}
    evidence = {"nested": {"houses": [1, 2]}}
    error_details = {"attempts": [1]}
    trace_details = {"expected": [1]}
    observation = {"actual": [2]}
    error = PredicateError("failure", "Safe failure", "PREDICATE", error_details, True)
    trace = PredicateTraceStep("root", "compare", trace_details, observation)
    result = PredicateResult(
        matched=False,
        predicate_id="PREDICATE",
        predicate_version="1",
        inputs=inputs,
        evidence=evidence,
        trace_steps=[trace],
        errors=[error],
        status=PredicateStatus.MISSING_CAPABILITY,
    )

    inputs["planets"].append("Moon")
    evidence["nested"]["houses"].append(3)
    error_details["attempts"].append(2)
    trace_details["expected"].append(4)
    observation["actual"].append(5)

    assert result.inputs["planets"] == ("Mars",)
    assert result.evidence["nested"]["houses"] == (1, 2)
    assert result.errors[0].details["attempts"] == (1,)
    assert result.trace_steps[0].details["expected"] == (1,)
    assert result.trace_steps[0].observation["actual"] == (2,)


def test_logical_equality_excludes_cache_and_duration_telemetry():
    cold = make_result(cache_hit=False, evaluation_time_ms=1.25)
    warm = replace(cold, cache_hit=True, evaluation_time_ms=99.0)
    assert cold == warm
    assert warm == cold


@pytest.mark.parametrize(
    "override",
    [
        {"predicate_id": "HOUSE_OCCUPANT"},
        {"predicate_version": "2.0.0"},
        {"inputs": {"planet": "Moon"}},
        {"evidence": {"actual_house": 3}},
        {"trace_steps": (make_trace("different"),)},
    ],
)
def test_logical_equality_detects_every_nontelemetry_content_difference(override):
    assert make_result() != make_result(**override)


def test_logical_equality_detects_status_match_and_error_differences():
    assert make_result() != make_result(matched=True, status=PredicateStatus.MATCHED, evidence={"actual_house": 1})
    first = make_result(status=PredicateStatus.ERROR, errors=(make_error("first"),))
    second = make_result(status=PredicateStatus.ERROR, errors=(make_error("second"),))
    assert first != second


def test_logical_equality_is_symmetric_transitive_and_stable_after_caller_mutation():
    source = {"planet": ["Mars"]}
    first = make_result(inputs=source)
    second = make_result(inputs={"planet": ["Mars"]})
    third = make_result(inputs={"planet": ["Mars"]})
    source["planet"].append("Moon")
    assert first == second and second == first
    assert first == second and second == third and first == third


@pytest.mark.parametrize("model", [make_error(), make_trace(), make_result()])
def test_canonical_models_are_deliberately_unhashable_until_wp03(model):
    with pytest.raises(TypeError):
        hash(model)


def test_legacy_runtime_result_remains_a_separate_eight_field_compatibility_type():
    assert PredicateResult is not engine.PredicateResult
    assert [field.name for field in fields(engine.PredicateResult)] == [
        "matched",
        "predicate_id",
        "inputs",
        "evidence",
        "trace_steps",
        "errors",
        "cache_hit",
        "evaluation_time_ms",
    ]
