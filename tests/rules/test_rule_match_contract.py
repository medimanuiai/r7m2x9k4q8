"""Prompt-02 universal RuleMatch contract and Rule Engine ownership tests."""

from __future__ import annotations

import ast
from dataclasses import fields, replace
from pathlib import Path
from uuid import UUID

import pytest

from systems.Parasara.engine.rules.models import (
    ConditionChildResult,
    ConditionNodeDisposition,
    ConditionOperator,
    ConditionResult,
    PredicateResult,
    PredicateStatus,
    PredicateTraceStep,
)
from systems.Parasara.engine.rules.canonical import CanonicalValueError
from systems.Parasara.engine.rules.rule_engine import ResolvedRule, RuleEngine
from systems.Parasara.engine.rules.rule_match import (
    RULE_MATCH_SCHEMA_VERSION,
    RuleMatch,
    RuleMatchError,
    RuleMatchStatus,
    RuleTraceReference,
    rule_match_from_logical_data,
    rule_match_from_logical_json,
    rule_match_logical_json_bytes,
    rule_match_logical_sha256,
    rule_match_to_logical_data,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _resolved(
    rule_id: str = "rule.alpha",
    *,
    priority: int = 5,
    position: int = 0,
    domains: tuple[str, ...] = ("career", "health"),
    metadata=None,
) -> ResolvedRule:
    return ResolvedRule(
        system="parashara",
        rule_id=rule_id,
        rule_version="1.2.0",
        rule_family="yoga",
        rule_set_version="v1",
        category="rajayoga",
        domains=domains,
        base_weight=0.75,
        priority=priority,
        context="natal",
        quality=0.9,
        provenance={"source": "rules/parashara/v1/test.yaml", "line": 7},
        metadata={} if metadata is None else metadata,
        evaluation_plan_position=position,
    )


def _build(engine: RuleEngine, resolved: ResolvedRule, result, **kwargs) -> RuleMatch:
    return engine.build_match(
        resolved,
        result,
        evaluation_snapshot_digest="0" * 64,
        evaluation_context={"evaluation_mode": "test"},
        **kwargs,
    )


def _predicate(status: PredicateStatus = PredicateStatus.MATCHED) -> PredicateResult:
    error = ()
    if status not in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED):
        from systems.Parasara.engine.rules.models import PredicateError

        error = (PredicateError(
            code=f"controlled_{status.value}",
            message="Controlled factual result.",
            predicate_id="PLANET_IN_HOUSE",
            details={"status": status.value},
            recoverable=True,
        ),)
    return PredicateResult(
        matched=status is PredicateStatus.MATCHED,
        predicate_id="PLANET_IN_HOUSE",
        predicate_version="1.0.0",
        inputs={"planet": "Jupiter", "house": 10},
        evidence={"actual_house": 10},
        trace_steps=(PredicateTraceStep(
            step_id="predicate.planet_in_house",
            operation="planet_in_house",
            details={"house": 10},
            observation={"actual_house": 10},
        ),),
        errors=error,
        cache_hit=False,
        evaluation_time_ms=None,
        status=status,
    )


def test_rule_match_field_and_status_inventory_is_exact():
    assert RULE_MATCH_SCHEMA_VERSION == "1.0.0"
    assert [item.value for item in RuleMatchStatus] == [
        "matched", "unmatched", "skipped", "excluded",
        "missing_capability", "invalid", "error",
    ]
    assert [item.name for item in fields(RuleMatch)] == [
        "rule_match_schema_version", "system", "rule_id", "rule_version",
        "rule_family", "rule_set_version", "category", "domains", "status",
        "matched", "base_weight", "priority", "context", "quality",
        "predicate_results", "evidence", "provenance", "metadata", "trace_id",
        "condition_trace_id", "trace_references", "errors",
    ]
    assert [item.name for item in fields(RuleMatchError)] == [
        "code", "message", "phase", "recoverable", "details",
        "source_predicate_id", "source_trace_id",
    ]
    assert [item.name for item in fields(RuleTraceReference)] == [
        "trace_id", "trace_type", "relation", "order",
    ]


def test_rule_engine_constructs_all_statuses_with_authoritative_matched_invariant():
    engine = RuleEngine()
    matched = _build(engine, _resolved(), _predicate())
    unmatched = _build(engine, _resolved("rule.unmatched"), _predicate(PredicateStatus.UNMATCHED))
    assert matched.status is RuleMatchStatus.MATCHED and matched.matched
    assert unmatched.status is RuleMatchStatus.UNMATCHED and not unmatched.matched
    with pytest.raises(ValueError, match="matched is true exactly"):
        replace(matched, matched=False)

    for status in (
        RuleMatchStatus.SKIPPED,
        RuleMatchStatus.EXCLUDED,
        RuleMatchStatus.MISSING_CAPABILITY,
        RuleMatchStatus.INVALID,
        RuleMatchStatus.ERROR,
    ):
        errors = ()
        if status in (
            RuleMatchStatus.MISSING_CAPABILITY,
            RuleMatchStatus.INVALID,
            RuleMatchStatus.ERROR,
        ):
            errors = (RuleMatchError(
                code=f"controlled_{status.value}",
                message="Controlled non-factual rule outcome.",
                phase="rule_evaluation",
                recoverable=True,
                details={},
            ),)
        value = _build(
            engine,
            _resolved(f"rule.{status.value}"),
            None,
            status_override=status,
            errors=errors,
        )
        assert value.status is status and not value.matched


def test_condition_leaf_order_is_exact_and_skipped_branches_are_not_fabricated():
    first = _predicate(PredicateStatus.UNMATCHED)
    condition = ConditionResult(
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
                result=first,
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
        evaluation_time_ms=None,
    )
    value = _build(RuleEngine(), _resolved(), condition)
    assert value.predicate_results == (first,)
    assert value.condition_trace_id == "condition.root"
    assert [(item.order, item.trace_type, item.trace_id) for item in value.trace_references] == [
        (0, "condition", "condition.root"),
        (1, "predicate", "predicate.planet_in_house"),
    ]


def test_canonical_round_trip_hash_and_nested_immutability_are_stable():
    value = _build(
        RuleEngine(),
        _resolved(domains=("health", "career", "health")),
        _predicate(),
        evidence={"facts": ({"planet": "Jupiter", "house": 10},)},
        additional_trace_references=(RuleTraceReference(
            trace_id="consumer.fact.1",
            trace_type="consumer_fact",
            relation="compatibility",
            order=99,
        ),),
    )
    data = rule_match_to_logical_data(value)
    restored = rule_match_from_logical_data(data)
    restored_from_json = rule_match_from_logical_json(rule_match_logical_json_bytes(value))
    assert value.domains == ("career", "health")
    assert restored == value
    assert restored_from_json == value
    assert rule_match_logical_json_bytes(restored) == rule_match_logical_json_bytes(value)
    assert len(rule_match_logical_sha256(value)) == 64
    assert UUID(value.trace_id).version == 5
    with pytest.raises(TypeError):
        value.evidence["facts"] = ()
    with pytest.raises(CanonicalValueError):
        rule_match_from_logical_json('{"rule_id":"a","rule_id":"b"}')

    malformed = dict(rule_match_to_logical_data(value))
    malformed["trace_references"] = {"not": "a sequence"}
    with pytest.raises(CanonicalValueError, match="invalid RuleMatch logical data"):
        rule_match_from_logical_data(malformed)


def test_cache_and_runtime_telemetry_do_not_change_normalized_rule_match():
    cold = _predicate()
    warm = replace(cold, cache_hit=True, evaluation_time_ms=12.5)
    first = _build(RuleEngine(), _resolved(), cold)
    second = _build(RuleEngine(), _resolved(), warm)
    assert first.predicate_results[0].cache_hit is False
    assert second.predicate_results[0].cache_hit is True
    assert rule_match_logical_json_bytes(first) == rule_match_logical_json_bytes(second)


@pytest.mark.parametrize(
    "forbidden",
    [
        "adjusted_weight", "final_contribution", "score", "confidence",
        "conflict_result", "normalized_score", "narrative",
    ],
)
def test_inference_and_presentation_fields_are_rejected(forbidden):
    with pytest.raises(ValueError, match="not RuleMatch"):
        _build(
            RuleEngine(),
            _resolved(metadata={"nested": {forbidden: 1}}),
            _predicate(),
        )


def test_collection_order_is_priority_then_identity_version_then_plan_position():
    engine = RuleEngine()
    values = (
        _build(engine, _resolved("rule.z", priority=9, position=2), _predicate()),
        _build(engine, _resolved("rule.a", priority=10, position=1), _predicate()),
        _build(engine, _resolved("rule.b", priority=9, position=0), _predicate()),
    )
    assert [item.rule_id for item in engine.order_matches(values)] == [
        "rule.a", "rule.b", "rule.z"
    ]


def test_only_generic_rule_engine_constructs_active_rule_matches():
    calls = []
    engine_root = REPO_ROOT / "systems" / "Parasara" / "engine"
    for path in engine_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "RuleMatch":
                calls.append(path.relative_to(REPO_ROOT).as_posix())
    assert sorted(set(calls)) == [
        "systems/Parasara/engine/rules/rule_engine.py",
        "systems/Parasara/engine/rules/rule_match.py",
    ]


def test_prompt02_validator_does_not_redefine_prompt01_manifest(monkeypatch):
    from tools import validate_prompt01, validate_prompt02

    historical = "01b53b093e62e328de7758ed543a2c8f3b06c3a97e0502d7e879730e8c10d256"
    observed = []

    def record_manifest(_temp_root, _runner):
        observed.append(validate_prompt01.EXPECTED_MANIFEST_SHA256)
        return "manifest"

    assert validate_prompt01.EXPECTED_MANIFEST_SHA256 == historical
    monkeypatch.setattr(validate_prompt01, "_manifest", record_manifest)
    assert validate_prompt02._prompt02_manifest(Path("."), None) == "manifest"
    assert observed == [validate_prompt02.EXPECTED_PROMPT02_MANIFEST_SHA256]
    assert validate_prompt01.EXPECTED_MANIFEST_SHA256 == historical
