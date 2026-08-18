"""Prompt-03 shared aggregation, confidence, conflict, and determinism tests."""

from __future__ import annotations

from dataclasses import replace
import json
import math
import random

import pytest

from systems.Parasara.engine.inference import (
    CapabilityAvailability,
    ContributionSign,
    DataCompleteness,
    InferenceEngine,
    InferenceStatus,
    inference_config_logical_json_bytes,
    inference_model_logical_json_bytes,
    inference_result_from_logical_json,
    inference_result_logical_json_bytes,
    load_inference_config,
)
from systems.Parasara.engine.rules.canonical import CanonicalValueError
from systems.Parasara.engine.rules.rule_match import (
    RULE_MATCH_SCHEMA_VERSION,
    RuleMatch,
    RuleMatchError,
    RuleMatchStatus,
    RuleTraceReference,
)


def completeness(score: float = 1.0, *, partial: bool = False) -> DataCompleteness:
    return DataCompleteness(
        domain="career",
        d1=CapabilityAvailability.PARTIAL if partial else CapabilityAvailability.AVAILABLE,
        d9=CapabilityAvailability.NOT_REQUIRED,
        d10=CapabilityAvailability.NOT_REQUIRED,
        aspects=CapabilityAvailability.NOT_REQUIRED,
        functional_roles=CapabilityAvailability.NOT_REQUIRED,
        shadbala=CapabilityAvailability.NOT_REQUIRED,
        dasha=CapabilityAvailability.NOT_REQUIRED,
        transits=CapabilityAvailability.NOT_REQUIRED,
        rule_pack=CapabilityAvailability.AVAILABLE,
        required_capabilities=("d1", "rule_pack"),
        missing_required=("d1",) if partial else (),
        missing_optional=(),
        completeness_score=score,
        trace_id=f"completeness.{score}.{partial}",
    )


def match(
    rule_id: str,
    weight: float,
    *,
    status: RuleMatchStatus = RuleMatchStatus.MATCHED,
    priority: int = 0,
    category: str = "career",
    correlation: str | None = None,
    quality: float | None = None,
    rule_set: str = "v1",
    metadata: dict | None = None,
) -> RuleMatch:
    logical_metadata = dict(metadata or {})
    logical_metadata["evaluation_plan_position"] = 0
    if correlation is not None:
        logical_metadata["correlation_key"] = correlation
    errors = ()
    references = (RuleTraceReference(
        trace_id=f"trace.fact.{rule_id}", trace_type="test_fact", relation="fact", order=0,
    ),)
    if status is RuleMatchStatus.ERROR:
        errors = (RuleMatchError(
            code="controlled_error", message="Controlled error.", phase="test",
            recoverable=True, details={}, source_trace_id=f"trace.fact.{rule_id}",
        ),)
    return RuleMatch(
        rule_match_schema_version=RULE_MATCH_SCHEMA_VERSION,
        system="parashara",
        rule_id=rule_id,
        rule_version="1.0",
        rule_family="test",
        rule_set_version=rule_set,
        category=category,
        domains=("career",),
        status=status,
        matched=status is RuleMatchStatus.MATCHED,
        base_weight=weight,
        priority=priority,
        context="natal",
        quality=quality,
        predicate_results=(),
        evidence={"fact_id": f"fact.{rule_id}"},
        provenance={"source": "test"},
        metadata=logical_metadata,
        trace_id=f"trace.rule.{rule_id}",
        condition_trace_id=None,
        trace_references=references,
        errors=errors,
    )


def aggregate(*rules: RuleMatch, data: DataCompleteness | None = None, config=None):
    return InferenceEngine().aggregate(
        domain="career",
        rule_matches=rules,
        timing_context=None,
        data_completeness=data or completeness(),
        config=config or load_inference_config(),
    )


def test_no_match_is_explicitly_insufficient_and_unavailable_never_contributes():
    result = aggregate(
        match("unmatched", 0.8, status=RuleMatchStatus.UNMATCHED),
        match("unavailable", -0.9, status=RuleMatchStatus.MISSING_CAPABILITY),
    )
    assert result.status is InferenceStatus.INSUFFICIENT_EVIDENCE
    assert result.raw_score == 0.0
    assert result.normalized_score == 0.5
    assert result.confidence == 0.0
    assert result.contributions == ()
    assert result.excluded_rule_ids == ("unmatched",)
    assert result.unavailable_rule_ids == ("unavailable",)


def test_positive_negative_neutral_and_explicit_mixed_contributions_reconcile():
    result = aggregate(
        match("positive", 0.2, priority=4),
        match("negative", -0.1, priority=3),
        match("neutral", 0.0, priority=2),
        match("mixed", 0.4, priority=1, metadata={
            "inference_sign": "mixed", "mixed_net_multiplier": -0.25,
        }),
    )
    assert [item.sign for item in result.positive_contributions] == [ContributionSign.POSITIVE]
    assert [item.sign for item in result.negative_contributions] == [ContributionSign.NEGATIVE]
    assert [item.sign for item in result.neutral_contributions] == [ContributionSign.NEUTRAL]
    assert [item.sign for item in result.mixed_contributions] == [ContributionSign.MIXED]
    assert result.raw_score == math.fsum(item.final_contribution for item in result.contributions)
    assert result.normalized_score == 0.5
    assert math.fsum(item.raw_contribution for item in result.components) == result.raw_score
    assert all(item.evidence_references and item.source_rule_trace_id for item in result.contributions)


def test_signed_weight_applies_sign_once_and_quality_fallback_is_visible():
    result = aggregate(match("negative", -0.4, quality=None))
    contribution = result.negative_contributions[0]
    assert contribution.base_weight == -0.4
    assert contribution.rule_quality == 1.0
    assert contribution.evidence_strength == 1.0
    assert contribution.context_multiplier == 1.0
    assert contribution.priority_multiplier == 1.0
    assert contribution.final_contribution == -0.4
    assert result.normalized_score == 0.1


def test_exact_conflict_preserves_both_sides_and_penalizes_confidence_once():
    positive = match("support", 0.2, category="same", correlation="fact.support")
    negative = match("challenge", -0.2, category="same", correlation="fact.challenge")
    without_conflict = aggregate(positive)
    result = aggregate(positive, negative)
    assert len(result.conflicts) == 1
    conflict = result.conflicts[0]
    assert conflict.unresolved is True
    assert conflict.winning_side.value == "tied"
    assert conflict.positive_rule_ids == ("support",)
    assert conflict.negative_rule_ids == ("challenge",)
    assert result.normalized_score == 0.5
    assert result.agreement == 0.0
    assert result.confidence == round(without_conflict.confidence - 0.1, 3)


def test_priority_then_quality_resolves_conflict_without_removing_loser():
    result = aggregate(
        match("support", 0.2, category="same", priority=10, quality=0.5),
        match("challenge", -0.8, category="same", priority=1, quality=1.0),
    )
    assert result.conflicts[0].winning_side.value == "positive"
    assert result.conflicts[0].unresolved is False
    assert {item.rule_id for item in result.contributions} == {"support", "challenge"}


def test_duplicate_evidence_never_increases_independence_credit():
    base = load_inference_config()
    confidence = dict(base.confidence)
    weights = {name: 0.0 for name in confidence["factor_weights"]}
    weights["independent_evidence"] = 1.0
    confidence["factor_weights"] = weights
    confidence["unresolved_conflict_penalty"] = 0.0
    independent_config = replace(base, confidence=confidence)
    one = aggregate(match("one", 0.1, correlation="shared"), config=independent_config)
    duplicate = aggregate(
        match("one", 0.1, correlation="shared"),
        match("two", 0.1, correlation="shared"),
        config=independent_config,
    )
    independent = aggregate(
        match("one", 0.1, correlation="one"),
        match("two", 0.1, correlation="two"),
        config=independent_config,
    )
    assert one.confidence == 1.0
    assert duplicate.confidence == 0.5
    assert independent.confidence == 1.0


def test_missing_required_data_is_partial_and_cannot_increase_confidence():
    complete = aggregate(match("support", 0.2), data=completeness(1.0))
    partial = aggregate(match("support", 0.2), data=completeness(0.5, partial=True))
    assert partial.status is InferenceStatus.PARTIAL
    assert partial.confidence < complete.confidence
    assert partial.negative_contributions == ()


def test_shuffle_repeat_round_trip_and_canonical_bytes_are_identical():
    rules = [match("b", -0.1, priority=1), match("a", 0.2, priority=2), match("c", 0.0)]
    first = aggregate(*rules)
    random.Random(42).shuffle(rules)
    second = aggregate(*rules)
    first_bytes = inference_result_logical_json_bytes(first)
    assert inference_result_logical_json_bytes(second) == first_bytes
    assert inference_result_from_logical_json(first_bytes) == first
    assert isinstance(first.errors, tuple)
    decoded = json.loads(first_bytes)
    assert decoded["status"] == first.status.value
    with pytest.raises(CanonicalValueError):
        inference_result_from_logical_json('{"status":1,"status":2}')


def test_mixed_rule_set_versions_and_invalid_domain_are_typed_failures():
    mixed = aggregate(match("one", 0.1, rule_set="v1"), match("two", 0.1, rule_set="v2"))
    assert mixed.status is InferenceStatus.FAILED
    assert mixed.errors[-1].code == "incompatible_rule_set_versions"
    wrong = replace(match("scope", 0.1), domains=("wealth",))
    scoped = aggregate(wrong)
    assert scoped.status is InferenceStatus.FAILED
    assert scoped.errors[-1].code == "invalid_domain_scope"


def test_configuration_and_completeness_are_defensively_immutable():
    config = load_inference_config()
    assert inference_config_logical_json_bytes(config)
    with pytest.raises(TypeError):
        config.confidence["precision"] = 9
    data = completeness()
    assert json.loads(inference_model_logical_json_bytes(data))["domain"] == "career"
    with pytest.raises((AttributeError, TypeError)):
        data.completeness_score = 0.0
