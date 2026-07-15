"""WP03 contract tests for canonical freezing, JSON, round trips, and hashing."""

from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
import io
import json
import math
from pathlib import Path
import re
import socket
import subprocess
import sys
import threading
from types import MappingProxyType
from uuid import UUID

import pytest
from pydantic import BaseModel

from systems.Parasara.engine.rules.canonical import (
    CanonicalValueError,
    FrozenMapping,
    canonical_json_bytes,
    canonical_json_data,
    canonical_json_text,
    freeze_canonical,
    predicate_error_from_data,
    predicate_error_from_json,
    predicate_error_json_bytes,
    predicate_error_to_data,
    predicate_result_from_full_data,
    predicate_result_from_full_json,
    predicate_result_from_logical_data,
    predicate_result_from_logical_json,
    predicate_result_full_json_bytes,
    predicate_result_full_json_text,
    predicate_result_logical_json_bytes,
    predicate_result_logical_json_text,
    predicate_result_logical_sha256,
    predicate_result_to_full_data,
    predicate_result_to_logical_data,
    predicate_trace_step_from_data,
    predicate_trace_step_from_json,
    predicate_trace_step_json_bytes,
    predicate_trace_step_to_data,
)
from systems.Parasara.engine.rules.models import (
    PredicateError,
    PredicateResult,
    PredicateStatus,
    PredicateTraceStep,
)


class StringEnum(str, Enum):
    VALUE = "declared-value"


class IntegerEnum(Enum):
    VALUE = 1


@dataclass
class ArbitraryDataclass:
    value: int


class ArbitraryObject:
    pass


class PydanticObject(BaseModel):
    value: int


def make_error(code="missing_fact"):
    return PredicateError(
        code=code,
        message="Required fact is unavailable",
        predicate_id="PLANET_IN_HOUSE",
        details={"capability": "houses", "attempts": [1, 2]},
        recoverable=True,
    )


def make_trace(step_id="root/lookup", parent_step_id=None, error_code=None):
    return PredicateTraceStep(
        step_id=step_id,
        operation="lookup",
        details={"planet": "Mars", "expected": [1, 4]},
        observation={"actual": 2},
        parent_step_id=parent_step_id,
        error_code=error_code,
    )


def make_result(**overrides):
    values = {
        "matched": False,
        "predicate_id": "PLANET_IN_HOUSE",
        "predicate_version": "1.0.0",
        "inputs": {"planet": "Mars", "houses": [1, 4]},
        "evidence": {"actual": {"house": 2}},
        "trace_steps": (make_trace(),),
        "errors": (),
        "cache_hit": False,
        "evaluation_time_ms": None,
        "status": PredicateStatus.UNMATCHED,
    }
    values.update(overrides)
    return PredicateResult(**values)


def test_frozen_mapping_empty_nested_lookup_iteration_membership_and_safe_repr():
    empty = FrozenMapping()
    nested = FrozenMapping({"z": [2, {"b": True}], "a": {"x": None}})
    assert len(empty) == 0
    assert list(nested) == ["a", "z"]
    assert nested["z"] == (2, FrozenMapping({"b": True}))
    assert "a" in nested
    assert repr(empty) == "FrozenMapping(len=0)"
    assert repr(nested) == "FrozenMapping(len=2)"


def test_frozen_mapping_equality_and_hash_ignore_source_insertion_order():
    first = FrozenMapping({"z": [2, 3], "a": {"x": 1}})
    second = FrozenMapping({"a": {"x": 1}, "z": (2, 3)})
    assert first == second
    assert second == first
    assert hash(first) == hash(second)


def test_canonical_numeric_types_do_not_collapse_into_equal_values():
    integer = FrozenMapping({"value": 1})
    floating = FrozenMapping({"value": 1.0})
    assert integer != floating
    assert hash(integer) != hash(floating)
    assert canonical_json_bytes(integer) != canonical_json_bytes(floating)

    integer_result = make_result(evidence={"value": 1})
    float_result = make_result(evidence={"value": 1.0})
    assert integer_result != float_result
    assert predicate_result_logical_json_bytes(integer_result) != predicate_result_logical_json_bytes(float_result)


def test_frozen_mapping_has_no_mutable_backing_escape_or_mutation_methods():
    frozen = FrozenMapping({"nested": {"items": [1]}})
    with pytest.raises(TypeError):
        frozen["new"] = 2
    with pytest.raises(AttributeError):
        frozen.update({"new": 2})
    with pytest.raises(TypeError):
        frozen._lookup["new"] = 2
    with pytest.raises(TypeError):
        frozen._items += (("new", 2),)


def test_recursive_freeze_isolates_mapping_list_and_tuple_from_caller_mutation():
    source = {"outer": [{"value": 1}], "tuple": ([2],)}
    frozen = freeze_canonical(source)
    source["outer"][0]["value"] = 9
    source["tuple"][0].append(3)
    assert frozen["outer"] == (FrozenMapping({"value": 1}),)
    assert frozen["tuple"] == ((2,),)


def test_repeated_acyclic_aliases_are_allowed_and_frozen_deterministically():
    shared = {"value": [1]}
    frozen = freeze_canonical({"left": shared, "right": shared})
    assert frozen["left"] == frozen["right"]
    assert frozen["left"] is not frozen["right"]


def test_direct_and_indirect_cycles_are_rejected_with_paths():
    direct = []
    direct.append(direct)
    with pytest.raises(CanonicalValueError, match=r"^\$\[0\]: cyclic value$"):
        freeze_canonical(direct)

    indirect = {"outer": []}
    indirect["outer"].append(indirect)
    with pytest.raises(CanonicalValueError, match=r"^\$\.outer\[0\]: cyclic value$"):
        freeze_canonical(indirect)


def test_string_enum_and_negative_zero_are_normalized_without_string_coercion():
    frozen = freeze_canonical({"enum": StringEnum.VALUE, "zero": -0.0})
    assert frozen["enum"] == "declared-value"
    assert type(frozen["enum"]) is str
    assert frozen["zero"] == 0.0
    assert math.copysign(1.0, frozen["zero"]) == 1.0


def test_strings_are_preserved_without_case_or_unicode_normalization():
    composed = "É"
    decomposed = "E\u0301"
    frozen = freeze_canonical({"upper": composed, "decomposed": decomposed})
    assert frozen["upper"] == composed
    assert frozen["decomposed"] == decomposed
    assert frozen["upper"] != frozen["decomposed"]


@pytest.mark.parametrize("value", [0.0, 1.25, -4.5])
def test_finite_floats_are_supported(value):
    assert freeze_canonical(value) == value


def unsafe_values():
    try:
        raise RuntimeError()
    except RuntimeError as exc:
        traceback_object = exc.__traceback__

    lock = threading.Lock()
    resource = io.StringIO("open")
    sock = socket.socket()
    values = [
        ({"value": math.nan}, "non-finite float"),
        ({"value": math.inf}, "non-finite float"),
        ({"value": -math.inf}, "non-finite float"),
        ({"value": {1, 2}}, "set"),
        ({"value": frozenset({1, 2})}, "set"),
        ({"value": b"bytes"}, "binary"),
        ({"value": bytearray(b"bytes")}, "binary"),
        ({"value": memoryview(b"bytes")}, "binary"),
        ({"value": Decimal("1.2")}, "decimal"),
        ({"value": 1 + 2j}, "complex"),
        ({"value": date(2026, 1, 1)}, "temporal"),
        ({"value": datetime(2026, 1, 1)}, "temporal"),
        ({"value": timedelta(days=1)}, "temporal"),
        ({"value": UUID(int=0)}, "uuid"),
        ({"value": Path("relative")}, "path"),
        ({"value": re.compile("x")}, "regex"),
        ({"value": json}, "module"),
        ({"value": ArbitraryObject}, "class"),
        ({"value": lambda: None}, "callable"),
        ({"value": (item for item in [1])}, "generator"),
        ({"value": iter([1])}, "iterator"),
        ({"value": RuntimeError()}, "exception"),
        ({"value": traceback_object}, "traceback"),
        ({"value": resource}, "open resource"),
        ({"value": lock}, "lock"),
        ({"value": sock}, "socket"),
        ({"value": ArbitraryObject()}, "custom object"),
        ({"value": ArbitraryDataclass(1)}, "dataclass"),
        ({"value": PydanticObject(value=1)}, "pydantic model"),
        ({"value": IntegerEnum.VALUE}, "non-string enum"),
    ]
    return values, (resource, sock)


def test_non_string_root_key_is_rejected_without_exposing_key_or_value():
    with pytest.raises(CanonicalValueError) as caught:
        freeze_canonical({1: "secret"})
    assert str(caught.value) == "$[key]: non-string mapping key"
    assert "secret" not in str(caught.value)


def test_every_locked_unsupported_category_is_rejected_with_safe_stable_paths():
    values, resources = unsafe_values()
    try:
        for value, category in values:
            with pytest.raises(CanonicalValueError) as caught:
                freeze_canonical(value)
            assert str(caught.value) == f"$.value: unsupported {category}"
            assert "0x" not in str(caught.value)
    finally:
        for resource in resources:
            resource.close()


def test_non_string_nested_key_error_uses_a_safe_logical_path():
    with pytest.raises(CanonicalValueError) as caught:
        freeze_canonical({"outer": [{2: "secret"}]})
    assert str(caught.value) == "$.outer[0][key]: non-string mapping key"
    assert "secret" not in str(caught.value)


def test_model_projections_have_exact_keys_values_and_explicit_nulls():
    error = make_error()
    root = make_trace()
    result = make_result(errors=(error,), status=PredicateStatus.MISSING_CAPABILITY)

    error_data = predicate_error_to_data(error)
    trace_data = predicate_trace_step_to_data(root)
    logical = predicate_result_to_logical_data(result)
    full = predicate_result_to_full_data(result)

    assert set(error_data) == {"code", "message", "predicate_id", "details", "recoverable"}
    assert set(trace_data) == {
        "step_id",
        "operation",
        "details",
        "observation",
        "parent_step_id",
        "error_code",
    }
    assert trace_data["parent_step_id"] is None
    assert trace_data["error_code"] is None
    assert set(logical) == {
        "matched",
        "predicate_id",
        "predicate_version",
        "inputs",
        "evidence",
        "trace_steps",
        "errors",
        "status",
    }
    assert logical["status"] == "missing_capability"
    assert set(full) == set(logical) | {"cache_hit", "evaluation_time_ms"}
    assert isinstance(logical["trace_steps"], list)
    assert isinstance(logical["errors"], list)
    assert isinstance(logical["inputs"], dict)


def test_empty_projection_collections_remain_explicit_objects_and_arrays():
    result = PredicateResult(
        matched=False,
        predicate_id="P",
        predicate_version="1",
        status=PredicateStatus.UNMATCHED,
    )
    data = predicate_result_to_logical_data(result)
    assert data["inputs"] == {}
    assert data["evidence"] == {}
    assert data["trace_steps"] == []
    assert data["errors"] == []


def test_canonical_json_policy_has_exact_expected_utf8_bytes():
    result = PredicateResult(
        matched=False,
        predicate_id="P",
        predicate_version="1",
        inputs={"z": [2, -0.0], "a": "Śiva"},
        status=PredicateStatus.UNMATCHED,
        cache_hit=True,
        evaluation_time_ms=1.5,
    )
    logical_expected = (
        '{"errors":[],"evidence":{},"inputs":{"a":"Śiva","z":[2,0.0]},'
        '"matched":false,"predicate_id":"P","predicate_version":"1",'
        '"status":"unmatched","trace_steps":[]}'
    ).encode("utf-8")
    full_expected = (
        '{"cache_hit":true,"errors":[],"evaluation_time_ms":1.5,"evidence":{},'
        '"inputs":{"a":"Śiva","z":[2,0.0]},"matched":false,'
        '"predicate_id":"P","predicate_version":"1","status":"unmatched",'
        '"trace_steps":[]}'
    ).encode("utf-8")
    assert predicate_result_logical_json_bytes(result) == logical_expected
    assert predicate_result_full_json_bytes(result) == full_expected
    assert b"\\u015a" not in logical_expected
    assert not logical_expected.startswith(b"\xef\xbb\xbf")
    assert not logical_expected.endswith(b"\n")


def test_general_canonical_json_data_text_bytes_are_strict_and_deterministic():
    source = {"z": [True, None], "a": "text"}
    assert canonical_json_data(source) == {"a": "text", "z": [True, None]}
    assert canonical_json_text(source) == '{"a":"text","z":[true,null]}'
    assert canonical_json_bytes(source) == b'{"a":"text","z":[true,null]}'
    with pytest.raises(CanonicalValueError):
        canonical_json_text({"bad": ArbitraryObject()})


def test_mapping_order_and_repeated_calls_produce_identical_bytes():
    first = make_result(inputs={"b": 2, "a": 1})
    second = make_result(inputs={"a": 1, "b": 2})
    assert predicate_result_logical_json_bytes(first) == predicate_result_logical_json_bytes(second)
    assert predicate_result_logical_json_bytes(first) == predicate_result_logical_json_bytes(first)


def test_telemetry_changes_only_full_bytes():
    cold = make_result(cache_hit=False, evaluation_time_ms=1.0)
    warm = replace(cold, cache_hit=True, evaluation_time_ms=2.0)
    assert predicate_result_logical_json_bytes(cold) == predicate_result_logical_json_bytes(warm)
    assert predicate_result_full_json_bytes(cold) != predicate_result_full_json_bytes(warm)


def test_error_trace_and_result_round_trip_through_data_and_json():
    error = make_error()
    root = make_trace()
    child = make_trace("root/child", root.step_id, "missing_fact")
    result = make_result(
        status=PredicateStatus.MISSING_CAPABILITY,
        trace_steps=(root, child),
        errors=(error,),
        cache_hit=True,
        evaluation_time_ms=3.5,
    )

    assert predicate_error_from_data(predicate_error_to_data(error)) == error
    assert predicate_error_from_json(predicate_error_json_bytes(error)) == error
    assert predicate_trace_step_from_data(predicate_trace_step_to_data(child)) == child
    assert predicate_trace_step_from_json(predicate_trace_step_json_bytes(child)) == child

    logical = predicate_result_from_logical_data(predicate_result_to_logical_data(result))
    assert logical == result
    assert logical.cache_hit is False
    assert logical.evaluation_time_ms is None

    full = predicate_result_from_full_data(predicate_result_to_full_data(result))
    assert full == result
    assert full.cache_hit is True
    assert full.evaluation_time_ms == 3.5
    assert predicate_result_from_logical_json(predicate_result_logical_json_bytes(result)) == result
    assert predicate_result_from_full_json(predicate_result_full_json_text(result)).cache_hit is True


@pytest.mark.parametrize("status", list(PredicateStatus))
def test_logical_round_trip_supports_every_status(status):
    errors = (make_error(),) if status is PredicateStatus.ERROR else ()
    result = make_result(
        matched=status is PredicateStatus.MATCHED,
        status=status,
        errors=errors,
    )
    restored = predicate_result_from_logical_json(predicate_result_logical_json_text(result))
    assert restored == result


@pytest.mark.parametrize(
    "mutator",
    [
        lambda data: data.pop("predicate_id"),
        lambda data: data.update({"unknown": 1}),
        lambda data: data.update({"status": "unknown"}),
        lambda data: data.update({"matched": 1}),
        lambda data: data.update({"matched": True, "status": "unmatched"}),
        lambda data: data.update({"trace_steps": {}}),
        lambda data: data.update({"errors": {}}),
    ],
)
def test_result_data_round_trip_rejects_missing_unknown_wrong_types_and_invariants(mutator):
    data = predicate_result_to_logical_data(make_result())
    mutator(data)
    with pytest.raises((CanonicalValueError, TypeError, ValueError)):
        predicate_result_from_logical_data(data)


def test_error_and_trace_data_round_trip_reject_missing_unknown_and_wrong_containers():
    error = predicate_error_to_data(make_error())
    error.pop("code")
    with pytest.raises(CanonicalValueError):
        predicate_error_from_data(error)
    trace = predicate_trace_step_to_data(make_trace())
    trace["unknown"] = 1
    with pytest.raises(CanonicalValueError):
        predicate_trace_step_from_data(trace)
    with pytest.raises(CanonicalValueError):
        predicate_error_from_data([])
    with pytest.raises(CanonicalValueError):
        predicate_trace_step_from_data("trace")


@pytest.mark.parametrize(
    "payload",
    [
        '{"matched":false,"matched":true}',
        "{malformed",
        b"\xff",
    ],
)
def test_strict_json_input_rejects_duplicate_keys_malformed_json_and_utf8(payload):
    with pytest.raises(CanonicalValueError):
        predicate_result_from_logical_json(payload)


def test_logical_sha256_format_stability_telemetry_independence_and_sensitivity():
    base = make_result()
    digest = predicate_result_logical_sha256(base)
    assert re.fullmatch(r"[0-9a-f]{64}", digest)
    assert digest == predicate_result_logical_sha256(base)
    assert digest == predicate_result_logical_sha256(replace(base, cache_hit=True, evaluation_time_ms=8.0))

    variants = [
        make_result(matched=True, status=PredicateStatus.MATCHED, evidence={"actual": {"house": 1}}),
        make_result(predicate_id="HOUSE_OCCUPANT"),
        make_result(predicate_version="2.0.0"),
        make_result(inputs={"planet": "Moon"}),
        make_result(evidence={"actual": {"house": 3}}),
        make_result(trace_steps=(make_trace("different"),)),
        make_result(status=PredicateStatus.ERROR, errors=(make_error(),)),
    ]
    assert all(predicate_result_logical_sha256(item) != digest for item in variants)
    with pytest.raises(TypeError):
        hash(base)


def test_canonical_bytes_and_hash_are_stable_in_a_fresh_process():
    expected_bytes = predicate_result_logical_json_bytes(make_result()).hex()
    expected_hash = predicate_result_logical_sha256(make_result())
    script = (
        "from systems.Parasara.engine.rules.models import PredicateResult,PredicateStatus,PredicateTraceStep;"
        "from systems.Parasara.engine.rules.canonical import predicate_result_logical_json_bytes,predicate_result_logical_sha256;"
        "t=PredicateTraceStep(step_id='root/lookup',operation='lookup',details={'planet':'Mars','expected':[1,4]},observation={'actual':2});"
        "r=PredicateResult(matched=False,predicate_id='PLANET_IN_HOUSE',predicate_version='1.0.0',inputs={'planet':'Mars','houses':[1,4]},evidence={'actual':{'house':2}},trace_steps=(t,),status=PredicateStatus.UNMATCHED);"
        "print(predicate_result_logical_json_bytes(r).hex());print(predicate_result_logical_sha256(r))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.splitlines() == [expected_bytes, expected_hash]


def test_model_construction_uses_the_single_public_frozen_mapping_policy():
    result = make_result()
    error = make_error()
    trace = make_trace()
    assert isinstance(result.inputs, FrozenMapping)
    assert isinstance(result.evidence, FrozenMapping)
    assert isinstance(error.details, FrozenMapping)
    assert isinstance(trace.details, FrozenMapping)
    assert isinstance(trace.observation, FrozenMapping)
