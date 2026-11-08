"""Supported construction and execution APIs cannot mint graph authority."""
import copy
from dataclasses import replace
from datetime import datetime, timezone
import pickle

import pytest

from systems.Parasara.engine.rules.conditions import ConditionEvaluator
from systems.Parasara.engine.rules.graph import RuleGraphCompiler
from systems.Parasara.engine.rules.rule_engine import RuleEngine
from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext
from systems.Parasara.engine.versioning import VersioningError, manifest_from_data, manifest_to_data
from tests.graph.test_runtime_outcomes import execute, Outcomes, snapshot


@pytest.mark.parametrize("operation", [copy.copy, copy.deepcopy, pickle.dumps, replace])
def test_graph_plan_and_compiled_objects_cannot_be_recreated(graph_pack, operation):
    _, _, compiled, _, plan = graph_pack()
    for value in (plan, plan.graph, compiled, *compiled.rules):
        with pytest.raises((TypeError, ValueError)):
            operation(value)


def test_identical_labels_are_not_same_authority(graph_pack):
    pack, authority, compiled, compiler, plan = graph_pack()
    other = pack.resolver.resolve(pack.config)
    assert other.manifest_fingerprint_sha256 == authority.manifest_fingerprint_sha256
    assert RuleGraphCompiler(resolved_versions=other).compile_authorized(compiled_rule_set=compiled).plan is None
    result, calls = execute(other, plan)
    assert result.record is None and calls == []
    assert compiler.compile_authorized(compiled_rule_set=compiled).plan is plan


@pytest.mark.parametrize("entry", ["build_match", "evaluate_compiled_rule"])
def test_direct_execution_is_rejected(graph_pack, entry):
    _, authority, compiled, _, _ = graph_pack()
    engine = RuleEngine(resolved_versions=authority)
    with pytest.raises(VersioningError) as exc:
        if entry == "build_match":
            engine.build_match(compiled.rules[0].resolved_rule, None,
                evaluation_snapshot_digest="0" * 64, evaluation_context={})
        else:
            engine.evaluate_compiled_rule(compiled.rules[0], condition_evaluator=None, state=None,
                context=None, evaluation_snapshot_digest="0" * 64, evaluation_context={})
    assert exc.value.details["graph_code"] == "P08E307_DIRECT_EXECUTION_BYPASS"


def test_coordinated_plan_replacement_and_adoption_are_rejected(graph_pack):
    _, authority, _, _, plan = graph_pack()
    analysis = replace(plan.graph.analysis, execution_order=tuple(reversed(plan.execution_order)))
    assert analysis.plan_sha256 != plan.plan_sha256
    with pytest.raises(ValueError):
        replace(plan.graph, analysis=analysis)
    with pytest.raises(ValueError):
        type(plan)(graph=plan.graph, compiled_rule_set=plan.compiled_rule_set, resolved_versions=authority)
    for untrusted in (plan.to_logical_data(), analysis, plan.compiled_rule_set.rules, None):
        assert execute(authority, untrusted)[0].record is None
    with pytest.raises(TypeError):
        RuleEngine(resolved_versions=authority).evaluate_plan(plan=plan, condition_evaluator=None,
            snapshot=snapshot(), context=None, prerequisite_matches=())


@pytest.mark.parametrize("change", ["dsl", "identity", "version", "content_sha256", "logical_sha256", "declarations_sha256", "plan_sha256", "graph_contract_sha256", "artifact_path"])
def test_manifest_component_and_digest_changes_fail(graph_pack, change):
    pack, _, _, _, _ = graph_pack()
    data = manifest_to_data(pack.manifest)
    graph = data["future_components"]["dependency_graph"]
    if change == "dsl": data["future_components"]["dsl"] = None
    elif change in graph["metadata"]: graph["metadata"][change] = "f" * 64
    elif change.endswith("sha256"): graph[change] = "f" * 64
    elif change == "artifact_path": graph[change] = "../unauthorized.json"
    else: graph[change] = "unsupported"
    # Even coordinated fingerprints cannot bypass component/source resolution.
    from systems.Parasara.engine.versioning import _verify_manifest_artifacts
    from systems.Parasara.engine.rules.graph.runtime_contract import digest
    data["manifest_fingerprint_sha256"] = digest({k: v for k, v in data.items() if k != "manifest_fingerprint_sha256"})
    with pytest.raises((ValueError, VersioningError)) as exc:
        altered = manifest_from_data(data)
        _verify_manifest_artifacts(altered, pack.dsl_source_path.parent.parent)
    expected = {"logical_sha256": "P08E305_GRAPH_DIGEST_MISMATCH",
        "declarations_sha256": "P08E304_DECLARATION_DIGEST_MISMATCH", "plan_sha256": "P08E306_PLAN_DIGEST_MISMATCH"}
    if change in expected:
        assert exc.value.details["graph_code"] == expected[change]


def test_context_and_evaluator_authority_are_verified_before_execution(graph_pack):
    pack, authority, _, _, plan = graph_pack()
    other = pack.resolver.resolve(pack.config)
    engine = RuleEngine(resolved_versions=authority)
    for owner, context in ((other, PredicateEvaluationContext(evaluation_instant=datetime(1970, 1, 1, tzinfo=timezone.utc))),
                           (authority, PredicateEvaluationContext()),
                           (authority, PredicateEvaluationContext(evaluation_instant=datetime(1970, 1, 2, tzinfo=timezone.utc)))):
        evaluator = Outcomes(owner, {})
        result = engine.evaluate_plan(plan=plan, condition_evaluator=ConditionEvaluator(evaluator),
            snapshot=snapshot(), context=context)
        assert result.record is None and evaluator.calls == []


def test_fatal_failure_discards_completed_nodes_and_unexpected_bugs_propagate(graph_pack, monkeypatch):
    _, authority, _, _, plan = graph_pack()
    original = RuleEngine._compiled_match
    def invalid(self, compiled, result, **kwargs):
        match = original(self, compiled, result, **kwargs)
        if compiled.resolved_rule.evaluation_plan_position == 1:
            from systems.Parasara.engine.rules.rule_match import RuleMatchStatus
            return replace(match, status=RuleMatchStatus.EXCLUDED, matched=False)
        return match
    monkeypatch.setattr(RuleEngine, "_compiled_match", invalid)
    result, calls = execute(authority, plan)
    assert calls == [0, 1] and result.record is None
    assert result.diagnostics[0].code == "P08E308_RUNTIME_INVARIANT"
    def bug(*args, **kwargs): raise RuntimeError("synthetic programming bug")
    monkeypatch.setattr(RuleEngine, "_compiled_match", bug)
    with pytest.raises(RuntimeError, match="synthetic programming bug"):
        execute(authority, plan)


def test_sealed_record_cannot_be_copied_replaced_or_deserialized(graph_pack):
    _, authority, _, _, plan = graph_pack()
    record = execute(authority, plan)[0].record
    for operation in (copy.copy, copy.deepcopy, pickle.dumps, replace):
        with pytest.raises((TypeError, ValueError)): operation(record)


def test_runtime_uses_sealed_plan_without_reading_changed_disk(graph_pack, tmp_path, monkeypatch):
    _, authority, _, _, plan = graph_pack()
    (tmp_path / "synthetic/dependencies.json").write_bytes(b"invalid after compilation")
    def forbidden(*args, **kwargs): raise AssertionError("runtime recompiled or read graph")
    monkeypatch.setattr(RuleGraphCompiler, "analyze_source", forbidden)
    monkeypatch.setattr(type(authority), "load_authorized_graph_source", forbidden)
    assert execute(authority, plan)[0].record is not None


def test_preparation_failure_publishes_bounded_diagnostic_without_matches(graph_pack, monkeypatch):
    from systems.Parasara.engine.rules import snapshot_adapter
    from systems.Parasara.engine.rules.prepared_state import PreparationIssue, PreparationOutcome
    _, authority, _, _, plan = graph_pack()
    monkeypatch.setattr(snapshot_adapter, "prepare_predicate_snapshot", lambda _: PreparationOutcome(
        succeeded=False, state=None, issues=(PreparationIssue(code="synthetic_failure", path="$"),)))
    result, calls = execute(authority, plan)
    assert result.record is None and calls == []
    assert result.diagnostics[0].details["preparation_issues"] == ("synthetic_failure",)


def test_multiple_graph_artifacts_cannot_be_selected(graph_pack):
    pack, _, _, _, _ = graph_pack()
    data = manifest_to_data(pack.manifest)
    component = data["future_components"]["dependency_graph"]
    data["future_components"]["dependency_graph"] = [component, component]
    with pytest.raises(TypeError, match="component must be a mapping"): manifest_from_data(data)
