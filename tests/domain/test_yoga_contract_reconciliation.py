"""Prompt-02/WP17 reconciliation for RuleMatch-owned Yoga truth."""

from __future__ import annotations

from dataclasses import fields, replace

import pytest

from systems.Parasara.engine.domain import (
    YogaDiagnostic,
    YogaDiagnosticFactory,
    prompt05_model_to_logical_data,
)
from systems.Parasara.engine.domain.models import yoga_diagnostic_from_logical_data
from systems.Parasara.engine.enrichments.yoga_engine import (
    YogaDefinitionDisposition,
    YogaRuleSource,
    build_yoga_diagnostics,
    evaluate_yoga_diagnostics,
    project_yoga_compatibility,
)
from systems.Parasara.engine.rules.canonical import CanonicalValueError
from systems.Parasara.engine.rules.rule_match import RuleMatchStatus
from tests.wp17 import scenario_manifest as wp17


def _wp17_conflicting_batch():
    astro = wp17._astro()
    original = wp17.load_yoga_rule_source()
    source_name = "wp17-normal.yaml"
    source = YogaRuleSource(
        source_name=source_name,
        records=original.records,
        validation=wp17.validate_yoga_rules(
            list(original.records), source_name=source_name
        ),
    )
    preparation = wp17.prepare_legacy_yoga_state(astro, source)
    assert preparation.outcome.succeeded
    assert preparation.outcome.state is not None
    return wp17.evaluate_yoga_batch(
        preparation.outcome.state,
        wp17.PredicateEvaluationContext(),
        source,
        predicate_evaluator=wp17.PredicateEvaluator(),
        compatibility_graph=preparation.compatibility_graph,
    )


def _conflicting_record():
    batch = _wp17_conflicting_batch()
    record = next(
        item for item in batch.records if item.rule_match.rule_id == "rajayoga_naive"
    )
    assert record.condition_result is not None
    assert record.condition_result.matched is True
    return batch, record


def test_wp17_invalid_rulematch_cannot_be_overridden_or_mutated_by_condition_truth():
    batch, record = _conflicting_record()
    match = record.rule_match
    before = (
        match.status,
        match.matched,
        match.evidence,
        match.trace_id,
        match.trace_references,
    )

    assert match.status is RuleMatchStatus.INVALID
    assert match.matched is False
    public = project_yoga_compatibility(batch)
    assert [item["yoga_id"] for item in public] == [
        item.rule_match.rule_id for item in batch.records
    ]
    assert public[0]["matched"] is False
    assert (
        match.status,
        match.matched,
        match.evidence,
        match.trace_id,
        match.trace_references,
    ) == before


def test_condition_true_cannot_override_unmatched_rulematch():
    _, record = _conflicting_record()
    matched = replace(
        record.rule_match,
        status=RuleMatchStatus.MATCHED,
        matched=True,
        errors=(),
    )
    compatible = replace(
        record,
        rule_match=matched,
        definition_disposition=YogaDefinitionDisposition.VALID,
        definition_issues=(),
    )
    unmatched = replace(
        compatible.rule_match,
        status=RuleMatchStatus.UNMATCHED,
        matched=False,
        errors=(),
    )
    assert unmatched.evidence == compatible.rule_match.evidence
    assert unmatched.trace_id == compatible.rule_match.trace_id
    assert unmatched.trace_references == compatible.rule_match.trace_references
    with pytest.raises(ValueError, match="condition and RuleMatch outcomes must agree"):
        replace(compatible, rule_match=unmatched)


def test_invalid_disagreement_rejects_authoritative_yoga_diagnostic_construction():
    batch, record = _conflicting_record()
    assert record.rule_match.status is RuleMatchStatus.INVALID
    assert record.condition_result is not None
    assert record.condition_result.matched is True
    with pytest.raises(ValueError, match="inside canonical evaluation"):
        build_yoga_diagnostics(batch)
    assert not hasattr(YogaDiagnosticFactory, "from_evaluation_record")


def test_compatible_canonical_path_preserves_order_and_cannot_be_reconstructed():
    astro = wp17._astro("golden_chart_01.json")
    diagnostics = evaluate_yoga_diagnostics(astro)
    assert [item.yoga_id for item in diagnostics] == [
        "rajayoga_naive",
        "dhana_naive",
        "arishta_naive",
    ]
    for diagnostic in diagnostics:
        record = diagnostic.source_evaluation_record
        assert record.condition_result is not None
        assert diagnostic.matched is record.rule_match.matched
        assert diagnostic.status is record.rule_match.status
        assert diagnostic.evidence_summary == record.rule_match.evidence
        assert diagnostic.trace_id == record.rule_match.trace_id

    diagnostic = diagnostics[0]
    constructor = {
        item.name: getattr(diagnostic, item.name) for item in fields(diagnostic)
    }
    with pytest.raises(ValueError, match="validated producer factory"):
        YogaDiagnostic(**constructor)
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(diagnostic)
    with pytest.raises(CanonicalValueError, match="one-way presentation"):
        yoga_diagnostic_from_logical_data(
            prompt05_model_to_logical_data(diagnostic)
        )
