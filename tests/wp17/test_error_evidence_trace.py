"""Cross-layer status, evidence, error, and trace truthfulness matrix."""

from __future__ import annotations

import re
from types import SimpleNamespace

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.interpreters.career import (
    evaluate_career_batch,
    prepare_career_facts,
    project_career_compatibility,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules.canonical import (
    condition_result_logical_json_bytes,
    predicate_result_logical_json_bytes,
)
from systems.Parasara.engine.rules.conditions import ConditionEvaluator
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.models import (
    ConditionNodeDisposition,
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
from tests.testing_framework.typed_rule_evaluation import evaluate_typed_rule_surfaces
from tests.wp17.test_purity_safety import FIXTURES, _predicate_source


SAFE_CODE = re.compile(r"^[a-z][a-z0-9_]*$")


def _state():
    outcome = prepare_predicate_state(_predicate_source())
    assert outcome.succeeded and outcome.state is not None
    return outcome.state


def _result(status: PredicateStatus) -> PredicateResult:
    error = ()
    if status not in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED):
        error = (
            PredicateError(
                code=f"controlled_{status.value}",
                message="Controlled safe outcome.",
                predicate_id="PLANET_IN_HOUSE",
                details={"status": status.value},
                recoverable=True,
            ),
        )
    return PredicateResult(
        matched=status is PredicateStatus.MATCHED,
        predicate_id="PLANET_IN_HOUSE",
        predicate_version="1.0.0",
        inputs={"planet": "Mars", "house": 1},
        evidence=(
            {"expected_house": 1, "actual_house": 1}
            if status in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED)
            else {}
        ),
        trace_steps=(
            PredicateTraceStep(
                step_id=f"controlled.{status.value}",
                operation="controlled_status",
                details={"status": status.value},
                observation={"matched": status is PredicateStatus.MATCHED},
                error_code=error[0].code if error else None,
            ),
        ),
        errors=error,
        cache_hit=False,
        evaluation_time_ms=None,
        status=status,
    )


class _StatusEvaluator(PredicateEvaluator):
    def __init__(self, statuses):
        super().__init__()
        self.statuses = list(statuses)

    def evaluate(self, *_args, **_kwargs):
        return _result(self.statuses.pop(0))


def test_predicate_statuses_never_collapse_nonfactual_outcomes_to_unmatched():
    state = _state()
    evaluator = PredicateEvaluator()
    cases = (
        (
            PredicateStatus.MATCHED,
            evaluator.evaluate(
                "PLANET_IN_HOUSE",
                {"planet": "Mars", "house": 1},
                state,
                PredicateEvaluationContext(),
            ),
        ),
        (
            PredicateStatus.UNMATCHED,
            evaluator.evaluate(
                "PLANET_IN_HOUSE",
                {"planet": "Mars", "house": 2},
                state,
                PredicateEvaluationContext(),
            ),
        ),
        (
            PredicateStatus.MISSING_CAPABILITY,
            evaluator.evaluate(
                "PLANET_IN_HOUSE",
                {"planet": "Jupiter", "house": 1},
                state,
                PredicateEvaluationContext(),
            ),
        ),
        (
            PredicateStatus.INVALID_PARAMETERS,
            evaluator.evaluate(
                "PLANET_IN_HOUSE", {}, state, PredicateEvaluationContext()
            ),
        ),
        (
            PredicateStatus.ERROR,
            evaluator.evaluate(
                "UNKNOWN_PREDICATE", {}, state, PredicateEvaluationContext()
            ),
        ),
        (PredicateStatus.TIMEOUT, _result(PredicateStatus.TIMEOUT)),
        (PredicateStatus.SKIPPED, _result(PredicateStatus.SKIPPED)),
    )
    assert [result.status for _expected, result in cases] == [
        expected for expected, _result_value in cases
    ]
    for expected, result in cases:
        assert result.matched is (expected is PredicateStatus.MATCHED)
        if expected not in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED):
            assert result.status is not PredicateStatus.UNMATCHED
            assert result.errors
            if expected is PredicateStatus.MISSING_CAPABILITY:
                assert "actual_house" not in result.evidence
                assert result.evidence["entity_state"] == "absent_entity"
            else:
                assert result.evidence == {}
        for error in result.errors:
            assert SAFE_CODE.fullmatch(error.code)
            assert len(error.message) <= 128
            assert "\n" not in error.message


def test_evidence_reports_observed_values_and_trace_lineage_is_repeatable():
    state = _state()
    evaluator = PredicateEvaluator()
    matched = evaluator.evaluate(
        "PLANET_IN_HOUSE",
        {"planet": "Mars", "house": 1},
        state,
        PredicateEvaluationContext(),
    )
    unmatched = PredicateEvaluator().evaluate(
        "PLANET_IN_HOUSE",
        {"planet": "Mars", "house": 2},
        state,
        PredicateEvaluationContext(),
    )
    repeated = PredicateEvaluator().evaluate(
        "PLANET_IN_HOUSE",
        {"planet": "Mars", "house": 1},
        state,
        PredicateEvaluationContext(),
    )
    assert matched.evidence["expected_house"] == 1
    assert matched.evidence["actual_house"] == 1
    assert unmatched.evidence["expected_house"] == 2
    assert unmatched.evidence["actual_house"] == 1
    assert predicate_result_logical_json_bytes(matched) == predicate_result_logical_json_bytes(
        repeated
    )
    assert [step.step_id for step in matched.trace_steps] == [
        step.step_id for step in repeated.trace_steps
    ]
    assert matched.trace_steps[0].parent_step_id is None
    assert all(
        step.parent_step_id == parent.step_id
        for parent, step in zip(matched.trace_steps, matched.trace_steps[1:])
    )

    node = {
        "type": "AND",
        "children": [
            {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 2}},
            {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 1}},
        ],
    }
    first = ConditionEvaluator(PredicateEvaluator()).evaluate(
        node, state, PredicateEvaluationContext()
    )
    second = ConditionEvaluator(PredicateEvaluator()).evaluate(
        node, state, PredicateEvaluationContext()
    )
    assert isinstance(first, ConditionResult)
    assert condition_result_logical_json_bytes(first) == condition_result_logical_json_bytes(
        second
    )
    assert first.children[1].disposition is ConditionNodeDisposition.SKIPPED
    assert first.children[1].result is None
    assert first.children[1].node_id == "condition.root.children.1"


def test_yoga_and_career_retain_nonfactual_typed_outcomes_before_lossy_projection():
    golden = chart_to_astrostate(
        SuryaAdapter.load(str(FIXTURES / "golden_chart_01.json"))
    )
    surfaces = evaluate_typed_rule_surfaces(golden)
    assert [record.status for record in surfaces.yoga.records] == [
        PredicateStatus.UNMATCHED,
        PredicateStatus.ERROR,
        PredicateStatus.MISSING_CAPABILITY,
    ]
    assert surfaces.yoga.records[1].definition_issues
    assert surfaces.yoga.records[2].condition_result is not None

    astro = AstroState(
        metadata={},
        location=None,
        lagna_sign="Aries",
        planets=[
            PlanetState(
                name="Mars",
                sign="Aries",
                degree=1.0,
                house=10,
                strength=None,
            )
        ],
        houses=[],
        diagnostics={},
        enrichments={
            "house_summaries": [
                {"number": 10, "lord": None, "occupants": ["Mars"]}
            ]
        },
        derived=None,
    )
    career = evaluate_career_batch(prepare_career_facts(astro))
    assert career.candidates[0].status is PredicateStatus.MISSING_CAPABILITY
    assert career.candidates[0].fact.errors[0].code == "missing_planet_strength_fact"
    assert career.candidates[0].contribution == 0.0
    public = project_career_compatibility(career)
    assert public["indicators"] == []
    assert public["evidence"] == []
