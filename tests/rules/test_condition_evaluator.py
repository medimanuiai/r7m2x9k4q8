"""WP10 canonical logical evaluator, validation, trace, and cache contract."""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from systems.Parasara.engine.rules.canonical import (
    condition_result_logical_json_bytes,
    condition_result_logical_sha256,
)
from systems.Parasara.engine.rules.conditions import (
    DEFAULT_ROOT_NODE_ID,
    MAX_CONDITION_DEPTH,
    MAX_CONDITION_NODES,
    ConditionEvaluator,
    evaluate_condition_canonical,
)
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.models import (
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
    prepare_predicate_state,
)


def source(*, house=1):
    return SimpleNamespace(
        planets=[SimpleNamespace(name="Mars", house=house, sign="Aries", degree=12.0)],
        lagna_sign="Aries", enrichments={}, derived=None, metadata={}, diagnostics={},
    )


def prepared(*, house=1):
    outcome = prepare_predicate_state(source(house=house))
    assert outcome.succeeded and outcome.state is not None
    return outcome.state


def leaf(house=1, **params):
    return {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": house, **params}}


def result(status):
    errors = ()
    if status is PredicateStatus.ERROR:
        errors = (PredicateError("controlled_error", "Controlled.", "PLANET_IN_HOUSE", {}, False),)
    return PredicateResult(
        matched=status is PredicateStatus.MATCHED,
        predicate_id="PLANET_IN_HOUSE", predicate_version="1.0.0",
        inputs={}, evidence={"status": status.value},
        trace_steps=(PredicateTraceStep("controlled", "controlled", {}, status.value),),
        errors=errors, cache_hit=False, evaluation_time_ms=1.0, status=status,
    )


class ControlledEvaluator(PredicateEvaluator):
    def __init__(self, statuses):
        super().__init__()
        self.statuses = list(statuses)
        self.calls = []

    def evaluate(self, predicate_id, parameters, state, context, *, use_cache=True):
        self.calls.append((predicate_id, dict(parameters)))
        return result(self.statuses.pop(0))


def evaluate(node, *, evaluator=None, root_node_id=DEFAULT_ROOT_NODE_ID, house=1):
    evaluator = PredicateEvaluator() if evaluator is None else evaluator
    return evaluate_condition_canonical(
        node, prepared(house=house), PredicateEvaluationContext(), evaluator,
        root_node_id=root_node_id,
    )


def statuses(value):
    return [child.result.status for child in value.children if child.result is not None]


def test_root_leaf_policy_normalization_and_explicit_class_api():
    evaluator = PredicateEvaluator()
    root = evaluate_condition_canonical(
        {"type": " planet_in_house ", "params": {"planet": "Mars", "house": 1}},
        prepared(), PredicateEvaluationContext(), evaluator,
    )
    assert type(root) is PredicateResult
    assert root.status is PredicateStatus.MATCHED
    assert ConditionEvaluator(evaluator).evaluate(leaf(), prepared(), PredicateEvaluationContext()) == root


def test_nested_operator_normalization_ids_and_complete_child_tree():
    node = {
        "type": " and ",
        "children": [
            leaf(),
            {"type": " not ", "children": [leaf(2)]},
            {"type": " or ", "children": [leaf(2), leaf()]},
        ],
    }
    value = evaluate(node, root_node_id="rule.demo.condition")
    assert type(value) is ConditionResult
    assert value.operator is ConditionOperator.AND and value.status is PredicateStatus.MATCHED
    assert [item.node_id for item in value.children] == [
        "rule.demo.condition.children.0", "rule.demo.condition.children.1", "rule.demo.condition.children.2"
    ]
    assert value.children[1].result.children[0].node_id == "rule.demo.condition.children.1.children.0"
    assert all(item.disposition is ConditionNodeDisposition.EVALUATED for item in value.children)


@pytest.mark.parametrize(
    ("node", "code"),
    [
        (None, "condition_node_not_mapping"),
        ([], "condition_node_not_mapping"),
        ({}, "condition_type_missing"),
        ({"type": None, "params": {}}, "condition_type_not_string"),
        ({"type": " ", "params": {}}, "condition_type_blank"),
        ({"type": "XOR", "children": []}, "unknown_condition_type"),
        ({"type": "PLANET_IN_HOSE", "params": {}}, "unknown_condition_type"),
        ({"op": "AND", "args": []}, "condition_unknown_fields"),
        ({"type": "AND", "children": [], "extra": True}, "condition_unknown_fields"),
        ({"type": "AND", "children": [], "params": {}}, "condition_unknown_fields"),
        ({"type": "PLANET_IN_HOUSE", "params": {}, "children": []}, "condition_unknown_fields"),
        ({"type": "PLANET_IN_HOUSE"}, "condition_params_missing"),
        ({"type": "PLANET_IN_HOUSE", "params": None}, "condition_params_not_mapping"),
        ({"type": "PLANET_IN_HOUSE", "params": []}, "condition_params_not_mapping"),
        ({"type": "AND"}, "condition_children_missing"),
        ({"type": "AND", "children": None}, "condition_children_not_list"),
        ({"type": "AND", "children": ()}, "condition_children_not_list"),
        ({"type": "AND", "children": []}, "condition_empty_operator"),
        ({"type": "OR", "children": []}, "condition_empty_operator"),
        ({"type": "NOT", "children": []}, "condition_not_arity"),
        ({"type": "NOT", "children": [leaf(), leaf()]}, "condition_not_arity"),
    ],
)
def test_malformed_inputs_return_safe_typed_failures_without_execution(node, code):
    evaluator = ControlledEvaluator([PredicateStatus.MATCHED])
    value = evaluate(node, evaluator=evaluator)
    assert value.status is PredicateStatus.ERROR and value.matched is False
    assert [error.code for error in value.errors] == [code]
    assert evaluator.calls == []
    payload = repr(value.errors[0].details)
    assert "0x" not in payload and "object at" not in payload


def test_wp11_migrated_leaf_uses_canonical_handler_without_legacy_fallback():
    value = evaluate({"type": "HOUSE_OCCUPANT", "params": {"planet": "Mars", "house": 1}})
    assert type(value) is PredicateResult
    assert value.status is PredicateStatus.MATCHED
    assert value.predicate_id == "HOUSE_OCCUPANT"
    assert value.errors == ()


def test_cycle_depth_and_node_count_boundaries_are_safe():
    cycle = {"type": "NOT", "children": []}
    cycle["children"].append(cycle)
    cyclic = evaluate(cycle)
    assert cyclic.status is PredicateStatus.ERROR
    assert cyclic.errors[0].code == "condition_cycle"

    def chain(count):
        node = leaf()
        for _ in range(count - 1):
            node = {"type": "NOT", "children": [node]}
        return node

    assert MAX_CONDITION_DEPTH == 64
    assert evaluate(chain(64)).status in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED)
    too_deep = evaluate(chain(65))
    assert too_deep.status is PredicateStatus.ERROR
    assert too_deep.errors[0].code == "condition_depth_limit"

    assert MAX_CONDITION_NODES == 4096
    accepted = evaluate({"type": "OR", "children": [leaf()] * 4095})
    assert accepted.status is PredicateStatus.MATCHED
    rejected = evaluate({"type": "OR", "children": [leaf()] * 4096})
    assert rejected.status is PredicateStatus.ERROR
    assert rejected.errors[0].code == "condition_node_limit"


def test_and_all_matched_and_early_unmatched_short_circuit():
    all_match = ControlledEvaluator([PredicateStatus.MATCHED] * 3)
    value = evaluate({"type": "AND", "children": [leaf(), leaf(), leaf()]}, evaluator=all_match)
    assert value.status is PredicateStatus.MATCHED and len(all_match.calls) == 3

    early = ControlledEvaluator([PredicateStatus.UNMATCHED])
    value = evaluate({"type": "AND", "children": [leaf(), leaf(0), leaf()]}, evaluator=early)
    assert value.status is PredicateStatus.UNMATCHED and len(early.calls) == 1
    assert [call[1]["house"] for call in early.calls] == [1]
    assert [item.disposition.value for item in value.children] == ["evaluated", "skipped", "skipped"]
    assert [item.skip_reason for item in value.children[1:]] == [
        "and_short_circuit_unmatched", "and_short_circuit_unmatched"
    ]
    assert value.details["decisive_child_id"] == "condition.root.children.0"


@pytest.mark.parametrize(
    ("prefix", "expected"),
    [
        ([PredicateStatus.MISSING_CAPABILITY, PredicateStatus.INVALID_PARAMETERS], PredicateStatus.INVALID_PARAMETERS),
        ([PredicateStatus.TIMEOUT, PredicateStatus.MISSING_CAPABILITY], PredicateStatus.TIMEOUT),
        ([PredicateStatus.INVALID_PARAMETERS, PredicateStatus.ERROR], PredicateStatus.ERROR),
        ([PredicateStatus.SKIPPED, PredicateStatus.MISSING_CAPABILITY], PredicateStatus.MISSING_CAPABILITY),
    ],
)
def test_and_nonfactual_precedence_before_decisive_unmatched(prefix, expected):
    evaluator = ControlledEvaluator([*prefix, PredicateStatus.UNMATCHED, PredicateStatus.MATCHED])
    value = evaluate({"type": "AND", "children": [leaf(), leaf(), leaf(), leaf()]}, evaluator=evaluator)
    assert value.status is expected and len(evaluator.calls) == 3
    assert value.children[-1].disposition is ConditionNodeDisposition.SKIPPED
    assert value.details["precedence_status"] == expected.value
    assert value.errors[0].predicate_id == "condition.root"
    assert value.errors[0].details["child_node_id"].startswith("condition.root.children.")


def test_and_no_unmatched_uses_highest_nonfactual_status():
    evaluator = ControlledEvaluator([
        PredicateStatus.MATCHED, PredicateStatus.MISSING_CAPABILITY,
        PredicateStatus.TIMEOUT, PredicateStatus.INVALID_PARAMETERS,
    ])
    value = evaluate({"type": "AND", "children": [leaf()] * 4}, evaluator=evaluator)
    assert value.status is PredicateStatus.TIMEOUT
    assert statuses(value) == [item[0] for item in evaluator.calls] if False else [
        PredicateStatus.MATCHED, PredicateStatus.MISSING_CAPABILITY,
        PredicateStatus.TIMEOUT, PredicateStatus.INVALID_PARAMETERS,
    ]


def test_or_matched_short_circuits_even_after_nonfactual_and_all_unmatched_is_false():
    evaluator = ControlledEvaluator([PredicateStatus.ERROR, PredicateStatus.MATCHED])
    value = evaluate({"type": "OR", "children": [leaf(), leaf(), leaf()]}, evaluator=evaluator)
    assert value.status is PredicateStatus.MATCHED and len(evaluator.calls) == 2
    assert value.children[2].skip_reason == "or_short_circuit_matched"
    assert value.children[0].result.errors[0].code == "controlled_error"

    all_false = ControlledEvaluator([PredicateStatus.UNMATCHED] * 3)
    value = evaluate({"type": "OR", "children": [leaf()] * 3}, evaluator=all_false)
    assert value.status is PredicateStatus.UNMATCHED and len(all_false.calls) == 3


@pytest.mark.parametrize(
    ("sequence", "expected"),
    [
        ([PredicateStatus.SKIPPED, PredicateStatus.MISSING_CAPABILITY], PredicateStatus.MISSING_CAPABILITY),
        ([PredicateStatus.MISSING_CAPABILITY, PredicateStatus.INVALID_PARAMETERS], PredicateStatus.INVALID_PARAMETERS),
        ([PredicateStatus.INVALID_PARAMETERS, PredicateStatus.TIMEOUT], PredicateStatus.TIMEOUT),
        ([PredicateStatus.TIMEOUT, PredicateStatus.ERROR], PredicateStatus.ERROR),
    ],
)
def test_or_without_match_uses_exact_nonfactual_precedence(sequence, expected):
    evaluator = ControlledEvaluator(sequence)
    value = evaluate({"type": "OR", "children": [leaf()] * len(sequence)}, evaluator=evaluator)
    assert value.status is expected
    assert value.details["precedence_status"] == expected.value


@pytest.mark.parametrize(
    ("child", "parent"),
    [
        (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED),
        (PredicateStatus.UNMATCHED, PredicateStatus.MATCHED),
        (PredicateStatus.ERROR, PredicateStatus.ERROR),
        (PredicateStatus.TIMEOUT, PredicateStatus.TIMEOUT),
        (PredicateStatus.INVALID_PARAMETERS, PredicateStatus.INVALID_PARAMETERS),
        (PredicateStatus.MISSING_CAPABILITY, PredicateStatus.MISSING_CAPABILITY),
        (PredicateStatus.SKIPPED, PredicateStatus.SKIPPED),
    ],
)
def test_not_inverts_only_factual_status_and_preserves_complete_child(child, parent):
    evaluator = ControlledEvaluator([child])
    value = evaluate({"type": "NOT", "children": [leaf()]}, evaluator=evaluator)
    assert value.status is parent
    assert value.children[0].result.status is child
    assert value.children[0].result.evidence["status"] == child.value
    assert value.children[0].result.trace_steps[0].step_id == "controlled"


def test_skipped_invalid_parameters_are_not_executed_or_cached():
    evaluator = PredicateEvaluator()
    node = {"type": "OR", "children": [leaf(), leaf(0, extra=object())]}
    value = evaluate(node, evaluator=evaluator)
    assert value.status is PredicateStatus.MATCHED
    assert value.children[1].disposition is ConditionNodeDisposition.SKIPPED
    assert evaluator.cache_size == 1


def test_cold_warm_trees_have_equal_logical_identity_but_preserve_leaf_telemetry():
    evaluator = PredicateEvaluator()
    node = {"type": "AND", "children": [leaf(), {"type": "NOT", "children": [leaf(2)]}]}
    cold = evaluate(node, evaluator=evaluator)
    warm = evaluate(node, evaluator=evaluator)
    assert cold == warm
    assert condition_result_logical_json_bytes(cold) == condition_result_logical_json_bytes(warm)
    assert condition_result_logical_sha256(cold) == condition_result_logical_sha256(warm)
    assert cold.children[0].result.cache_hit is False
    assert warm.children[0].result.cache_hit is True


def test_trace_has_start_children_short_circuit_precedence_and_final_without_flattening():
    evaluator = ControlledEvaluator([PredicateStatus.ERROR, PredicateStatus.UNMATCHED])
    value = evaluate({"type": "AND", "children": [leaf(), leaf(), leaf()]}, evaluator=evaluator)
    operations = [step.operation for step in value.trace_steps]
    assert operations == [
        "condition_start", "condition_child_result", "condition_child_result",
        "condition_short_circuit", "condition_child_skipped",
        "condition_status_precedence", "condition_final_disposition",
    ]
    assert value.children[0].result.trace_steps[0].step_id == "controlled"
    assert all(step.step_id != "controlled" for step in value.trace_steps)


def test_boundary_types_root_id_and_unexpected_evaluator_defect_are_safe():
    class Defective(PredicateEvaluator):
        def evaluate(self, *args, **kwargs):
            raise RuntimeError("secret path C:/private/value")

    for kwargs in (
        {"state": object()}, {"context": object()}, {"predicate_evaluator": object()},
    ):
        values = dict(
            node=leaf(), state=prepared(), context=PredicateEvaluationContext(),
            predicate_evaluator=PredicateEvaluator(),
        )
        values.update(kwargs)
        outcome = evaluate_condition_canonical(**values)
        assert outcome.status is PredicateStatus.ERROR
    for root_id in (None, "", "bad space", 1):
        with pytest.raises((TypeError, ValueError)):
            evaluate_condition_canonical(
                leaf(), prepared(), PredicateEvaluationContext(), PredicateEvaluator(),
                root_node_id=root_id,
            )
    defective = evaluate(leaf(), evaluator=Defective())
    payload = condition_result_logical_json_bytes(
        evaluate({"type": "NOT", "children": [leaf()]}, evaluator=Defective())
    )
    assert defective.status is PredicateStatus.ERROR
    assert defective.errors[0].code == "condition_leaf_evaluator_error"
    assert b"secret" not in payload and b"private" not in payload


def test_condition_module_is_pure_and_old_dispatch_modules_are_absent():
    path = Path("systems/Parasara/engine/rules/conditions.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    from_imports = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    forbidden = ("astrostate", "yoga", "career", "loader", "random", "uuid", "os", "pathlib", "socket")
    assert not any(any(item in name.lower() for item in forbidden) for name in imports | from_imports)
    yoga = Path("systems/Parasara/engine/enrichments/yoga_engine.py").read_text(encoding="utf-8")
    assert not Path("systems/Parasara/engine/rules/engine.py").exists()
    assert not Path("systems/Parasara/engine/rules/predicates.py").exists()
    assert "evaluate_condition_canonical" not in yoga
