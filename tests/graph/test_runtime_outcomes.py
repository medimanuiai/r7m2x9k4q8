"""Behavioral dependency gates against every existing predicate outcome."""
from dataclasses import replace
from datetime import datetime, timezone

import pytest

from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.astrostate_api import freeze_astrostate, require_snapshot
from systems.Parasara.engine.rules.conditions import ConditionEvaluator
from systems.Parasara.engine.rules.models import PredicateStatus
from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext
from systems.Parasara.engine.rules.rule_engine import RuleEngine
from systems.Parasara.engine.inference import InferenceEngine, load_inference_config
from tests.dsl.test_compiler_authority import _StatusEvaluator
from tests.graph.conftest import document, dsl_payload
from tests.inference.test_inference_engine import completeness


def snapshot():
    return require_snapshot(freeze_astrostate(AstroState(metadata={}, location=None,
        lagna_sign="Aries", planets=[PlanetState(name="Mars", sign="Aries", degree=1.0, house=1)],
        houses=[], diagnostics={}, enrichments={"aspects": []}, derived=None),
        evaluation_context={"instant": "1970-01-01T00:00:00Z"}))


class Outcomes(_StatusEvaluator):
    def __init__(self, authority, statuses):
        super().__init__(authority, PredicateStatus.MATCHED)
        self.statuses, self.calls = statuses, []

    def evaluate(self, predicate_id, parameters, state, context, *, use_cache=True):
        i = parameters["house"] - 1
        self.calls.append(i)
        self._forced_status = self.statuses.get(i, PredicateStatus.MATCHED)
        return super().evaluate(predicate_id, parameters, state, context, use_cache=use_cache)


def execute(authority, plan, statuses=None):
    evaluator = Outcomes(authority, statuses or {})
    result = RuleEngine(resolved_versions=authority).evaluate_plan(plan=plan,
        condition_evaluator=ConditionEvaluator(evaluator), snapshot=snapshot(),
        context=PredicateEvaluationContext(evaluation_instant=datetime(1970, 1, 1, tzinfo=timezone.utc)))
    return result, evaluator.calls


@pytest.mark.parametrize("kind", ("requires_matches", "requires_absence", "optional_supports"))
@pytest.mark.parametrize("status", tuple(PredicateStatus))
def test_every_root_outcome_and_edge_kind(graph_pack, kind, status):
    _, authority, _, _, plan = graph_pack(document(2, [(0, 1, kind)]))
    result, calls = execute(authority, plan, {0: status})
    assert result.record is not None, result
    record = result.record
    assert len(record.matches) == len(record.traces) == 2
    factual = status in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED)
    passes = kind == "optional_supports" or status is (
        PredicateStatus.MATCHED if kind == "requires_matches" else PredicateStatus.UNMATCHED)
    decision = record.traces[1].decisions[0]
    expected = ("observed_" + (status.value if factual else "unavailable") if kind == "optional_supports"
        else "satisfied" if passes else "unsatisfied" if factual else "unavailable")
    assert decision.decision == expected
    assert decision.root_outcome == status.value
    assert calls == ([0, 1] if passes else [0])
    if not passes:
        match, trace = record.matches[1], record.traces[1]
        assert match.status.value == "skipped"
        assert match.predicate_results == () and match.condition_trace_id is None and dict(match.evidence) == {}
        assert trace.completion_kind == "dependency_skip" and trace.root_outcome is None
        assert trace.skip_reason == "dependency_" + expected


def test_unavailability_precedence_retains_all_decisions_and_roots(graph_pack):
    _, authority, _, _, plan = graph_pack(document(4, [(0, 2, "requires_matches"), (1, 2, "requires_absence")]))
    result, calls = execute(authority, plan, {0: PredicateStatus.UNMATCHED, 1: PredicateStatus.TIMEOUT})
    assert calls == [0, 1, 3]
    trace = result.record.traces[2]
    assert trace.gate == "unavailable"
    assert tuple(d.decision for d in trace.decisions) == ("unsatisfied", "unavailable")
    assert result.record.matches[1].errors[0].code == "condition_timeout"


def test_condition_skip_and_dependency_skip_remain_distinct(graph_pack):
    _, authority, _, _, plan = graph_pack(document(3, [(0, 1, "requires_matches"), (1, 2, "requires_absence")]))
    result, calls = execute(authority, plan, {0: PredicateStatus.SKIPPED})
    assert calls == [0]
    assert [(t.completion_kind, t.root_outcome) for t in result.record.traces] == [
        ("condition_evaluated", "skipped"), ("dependency_skip", None), ("dependency_skip", None)]


def test_passed_required_gate_does_not_override_dependent_truth(graph_pack):
    _, authority, _, _, plan = graph_pack(document(2, [(0, 1, "requires_matches")]))
    result, calls = execute(authority, plan, {1: PredicateStatus.UNMATCHED})
    assert calls == [0, 1]
    assert result.record.traces[1].gate == "passed" and result.record.matches[1].status.value == "unmatched"


def test_optional_observation_does_not_copy_evidence_or_adjust_weight(graph_pack, monkeypatch):
    original = Outcomes.evaluate
    def facts(self, predicate_id, parameters, state, context, **kwargs):
        result = original(self, predicate_id, parameters, state, context, **kwargs)
        return replace(result, evidence={"synthetic_fact_owner": parameters["house"]})
    monkeypatch.setattr(Outcomes, "evaluate", facts)
    _, authority, _, _, plan = graph_pack(document(2, [(0, 1, "optional_supports")]))
    record = execute(authority, plan)[0].record
    assert [dict(m.predicate_results[0].evidence) for m in record.matches] == [
        {"synthetic_fact_owner": 1}, {"synthetic_fact_owner": 2}]
    assert [m.base_weight for m in record.matches] == [0.0, 0.0]
    assert all("dependency" not in k for m in record.matches for k in m.evidence)


def test_dependency_lineage_never_becomes_inference_evidence(graph_pack):
    payload = dsl_payload(2).replace(b"base_weight: 0.0", b"base_weight: 0.25")
    _, authority, _, _, plan = graph_pack(
        document(2, [(0, 1, "optional_supports")]), payload=payload,
    )
    record = execute(authority, plan)[0].record
    config = replace(load_inference_config(), system="synthetic")
    data = replace(completeness(), domain="synthetic")

    def infer(*matches):
        return InferenceEngine().aggregate(
            domain="synthetic", rule_matches=matches, timing_context=None,
            data_completeness=data, config=config,
        )

    root, dependent = record.matches
    assert all(any(ref.trace_type == "dependency" for ref in match.trace_references)
               for match in (root, dependent))
    assert record.traces[1].decisions[0].kind.value == "optional_supports"

    ordinary_root = replace(root, trace_references=tuple(
        ref for ref in root.trace_references if ref.trace_type != "dependency"))
    ordinary_dependent = replace(dependent, trace_references=tuple(
        ref for ref in dependent.trace_references if ref.trace_type != "dependency"))
    graph_result = infer(root, dependent)
    ordinary_result = infer(ordinary_root, ordinary_dependent)

    assert [item.final_contribution for item in graph_result.contributions] == [0.25, 0.25]
    assert graph_result.contributions == ordinary_result.contributions
    for contribution, match in zip(graph_result.contributions, (root, dependent)):
        assert contribution.evidence_references
        assert all(ref.source_type != "dependency" for ref in contribution.evidence_references)
        assert {ref.source_id for ref in contribution.evidence_references} == {
            predicate.predicate_id for predicate in match.predicate_results
        }


def test_largest_ledger_has_one_trace_per_node_and_decision_per_edge(graph_pack):
    edges = [(i, j, "optional_supports") for j in range(32, 160) for i in range(32)]
    _, authority, _, _, plan = graph_pack(document(256, edges))
    record, calls = execute(authority, plan)
    assert record.record is not None
    assert len(record.record.matches) == len(record.record.traces) == len(calls) == 256
    assert sum(len(t.decisions) for t in record.record.traces) == 4096
