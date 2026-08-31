from __future__ import annotations

from dataclasses import fields, replace
import json
from pathlib import Path

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.astrostate_api import freeze_astrostate
from systems.Parasara.engine.capability import CapabilityInspection, CapabilityReadiness
from systems.Parasara.engine.domain import (
    TRANSIT_SUMMARY_SCHEMA_VERSION,
    DomainBuildProduced,
    DomainBuildRejected,
    DomainIndicator,
    DomainPrediction,
    DomainPredictionFactory,
    TimingOutputStatus,
    TransitPosition,
    TransitProducerEvidence,
    TransitRelationship,
    TransitSummary,
    TransitSummaryFactory,
    YogaDiagnostic,
    YogaDiagnosticFactory,
    prompt05_model_logical_json_bytes,
    prompt05_model_to_logical_data,
    transit_summary_from_logical_json,
)
from systems.Parasara.engine.domain.models import domain_prediction_from_logical_data
from systems.Parasara.engine.enrichments.yoga_engine import (
    evaluate_yoga_diagnostics,
    build_yoga_snapshot,
    evaluate_yoga_snapshot,
    load_yoga_rule_source,
)
from systems.Parasara.engine.inference import InferenceStatus
from systems.Parasara.engine.inference.models import EvidenceReference
from systems.Parasara.engine.interpreters.career import (
    build_career_prediction,
    evaluate_career_batch,
    infer_career,
    interpret_career_domain,
    prepare_career_facts,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.output_assembler import OutputAssembler
from systems.Parasara.engine.rules.rule_match import RuleMatchStatus
from systems.Parasara.tools.generate_snapshot import _snapshot_assembly_input


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"


def career(name: str = "surya_test_chart.json"):
    astro = chart_to_astrostate(SuryaAdapter.load(FIXTURES / name))
    outcome = interpret_career_domain(astro)
    assert isinstance(outcome, DomainBuildProduced)
    batch = outcome.prediction.source_evaluation_batch
    inference = outcome.prediction.source_inference_result
    return astro, batch, inference, outcome.prediction


def yogas():
    astro = chart_to_astrostate(
        SuryaAdapter.load(FIXTURES / "golden_chart_01.json")
    )
    return astro, evaluate_yoga_diagnostics(astro)


def capability(readiness: CapabilityReadiness) -> CapabilityInspection:
    return CapabilityInspection(
        capability_id="transits.current",
        expected_version="1.0.0",
        observed_version="1.0.0",
        readiness=readiness,
        source_kind="transit_producer",
        content_empty=readiness is CapabilityReadiness.READY_EMPTY,
        issues=(),
    )


def test_compatibility_has_no_caller_controlled_source_duplicates():
    assert "source_career_compatibility" not in {
        item.name for item in fields(DomainPrediction)
    }
    assert "source_compatibility" not in {
        item.name for item in fields(YogaDiagnostic)
    }
    assert "matched" not in {
        item.name for item in fields(type(yogas()[1][0].compatibility))
    }


def test_career_direct_replace_digest_and_deserialization_attacks_fail():
    _, _, inference, prediction = career()
    forged = replace(prediction.career_compatibility, base_score=0.0)
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(prediction, career_compatibility=forged, logical_digest="")

    constructor = {item.name: getattr(prediction, item.name) for item in fields(prediction)}
    constructor.update(career_compatibility=forged, logical_digest="")
    with pytest.raises(ValueError, match="validated producer factory"):
        DomainPrediction(**constructor)

    copied = prompt05_model_to_logical_data(prediction)
    copied["career_compatibility"]["base_score"] = 0.0
    copied["logical_digest"] = ""
    with pytest.raises(ValueError, match="one-way presentation"):
        domain_prediction_from_logical_data(
            json.loads(json.dumps(copied)),
            source_inference_result=inference,
            source_inference_compatibility=prediction.source_inference_compatibility,
            source_evaluation_batch=prediction.source_evaluation_batch,
        )

    with pytest.raises(TypeError):
        replace(prediction, source_career_compatibility=forged, logical_digest="")


def test_yoga_truth_is_owned_only_by_the_retained_rule_match():
    _, diagnostics = yogas()
    diagnostic = diagnostics[0]
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(diagnostic, matched=not diagnostic.matched, logical_digest="")
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(
            diagnostic,
            status=(
                RuleMatchStatus.UNMATCHED
                if diagnostic.status is RuleMatchStatus.MATCHED
                else RuleMatchStatus.MATCHED
            ),
            logical_digest="",
        )
    with pytest.raises(TypeError):
        replace(
            diagnostic,
            source_compatibility=diagnostic.compatibility,
            logical_digest="",
        )
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(
            diagnostic.compatibility,
            evidence={"planet": "Pluto"},
        )


def test_every_indicator_retains_authoritative_rule_lineage():
    _, _, _, prediction = career()
    indicator = prediction.indicators[0]
    assert indicator.source_rule_match.rule_id == indicator.source_rule_id

    attacks = (
        {"source_rule_id": "forged.rule"},
        {"evidence_references": (
            replace(
                indicator.evidence_references[0],
                evidence_id="forged.evidence",
            ),
        )},
        {"source_rule_trace_id": "forged.rule.trace"},
        {"trace_id": "forged.indicator.trace"},
    )
    for changes in attacks:
        with pytest.raises(ValueError, match="evaluator-owned producer boundary"):
            replace(indicator, **changes)


def test_score_bearing_indicator_cannot_clear_its_contribution_identity():
    _, _, _, prediction = career()
    score_bearing = prediction.indicators[0]
    match = score_bearing.source_rule_match
    with pytest.raises(ValueError, match="evaluator-owned producer boundary"):
        replace(
            score_bearing,
            source_contribution_id=None,
            contribution=None,
            evidence_summary=match.evidence,
            trace_id=match.trace_id,
        )
    assert not hasattr(DomainPredictionFactory, "from_inference")


def transit_fixture():
    _, batch, inference, _ = career()
    position = TransitPosition(
        body_id="Sun",
        sign_id="Aries",
        longitude_degrees=1.0,
        source_fact_id="transit.fact.sun",
        order=0,
    )
    target = EvidenceReference(
        evidence_id="evidence.natal.ascendant",
        source_type="astrostate_fact",
        source_id="natal.ascendant",
        trace_id="astrostate.natal.ascendant",
        correlation_key="natal.ascendant",
        order=0,
    )
    rule_match = batch.rule_matches[0]
    producer = TransitSummaryFactory.producer_evidence(
        capability=capability(CapabilityReadiness.READY),
        positions=(position,),
        natal_target_references=(target,),
        rule_matches=(rule_match,),
        domain_effect_results=(inference,),
        producer_version="1.0.0",
        producer_schema_version="1.0.0",
        trace_id="transit.producer.test",
    )
    relationship = TransitRelationship(
        relationship_id="transit.relationship.sun.asc",
        source_body_id="Sun",
        natal_target_id=target.source_id,
        relationship_type="conjunction",
        source_fact_ids=(position.source_fact_id,),
        order=0,
    )
    summary = TransitSummaryFactory.from_calculator_output(
        status=TimingOutputStatus.AVAILABLE,
        reference_instant="2020-01-01T00:00:00+00:00",
        positions=(position,),
        natal_relationships=(relationship,),
        active_rule_match_ids=(rule_match.rule_id,),
        domain_effect_trace_ids=(inference.trace_id,),
        producer_evidence=producer,
        calculation_version="1.0.0",
        trace_id="transit.test",
    )
    return summary


def test_transit_catalog_and_fake_proof_attacks_fail():
    with pytest.raises((TypeError, ValueError)):
        TransitProducerEvidence(
            readiness="ready_empty",
            source_fact_ids=(),
            natal_target_ids=(),
            rule_match_ids=(),
            domain_effect_trace_ids=(),
        )
    with pytest.raises(ValueError, match="validated producer factory"):
        TransitProducerEvidence(
            capability=capability(CapabilityReadiness.READY_EMPTY),
            positions=(),
            natal_target_references=(),
            rule_matches=(),
            domain_effect_results=(),
            producer_version="1.0.0",
            producer_schema_version="1.0.0",
            trace_id="fake.ready.empty",
        )


def test_transit_reconciles_every_public_reference_to_typed_owners():
    summary = TransitSummaryFactory.unavailable()
    assert transit_summary_from_logical_json(
        prompt05_model_logical_json_bytes(summary)
    ) == summary
    assert summary.status is TimingOutputStatus.UNAVAILABLE
    assert summary.producer_evidence is None


def test_canonical_capability_cannot_mint_ready_empty_transit():
    with pytest.raises(ValueError, match="no authoritative producer"):
        TransitSummaryFactory.producer_evidence(
            capability=capability(CapabilityReadiness.READY_EMPTY),
            positions=(),
            producer_version="1.0.0",
            producer_schema_version="1.0.0",
            trace_id="transit.producer.empty",
        )


def test_multi_yoga_assembly_uses_only_typed_source_order():
    astro, diagnostics = yogas()
    snapshot = freeze_astrostate(astro).snapshot
    value = replace(_snapshot_assembly_input(snapshot), yogas=diagnostics)
    public = OutputAssembler().assemble(value)["diagnostics"]["yogas"]
    assert [item["yoga_id"] for item in public] == [
        item.yoga_id for item in diagnostics
    ]

    with pytest.raises(ValueError, match="source order"):
        replace(value, yogas=tuple(reversed(diagnostics)))
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(diagnostics[1].compatibility, source_order=0)


def test_yoga_evidence_cannot_override_typed_source_order():
    _, diagnostics = yogas()
    first = diagnostics[0]
    forged_match = replace(
        first.source_rule_match,
        evidence={**dict(first.source_rule_match.evidence), "source_order": 99},
    )
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(first, source_rule_match=forged_match, logical_digest="")


def neutral_insufficient(inference):
    return replace(
        inference,
        status=InferenceStatus.INSUFFICIENT_EVIDENCE,
        raw_score=0.0,
        normalized_score=0.5,
        confidence=0.0,
        agreement=0.0,
        positive_contributions=(),
        negative_contributions=(),
        neutral_contributions=(),
        mixed_contributions=(),
        components=(),
        conflicts=(),
        explanation_factors=(),
    )


def test_insufficient_and_missing_inference_are_distinct_closed_outcomes():
    _, batch, inference, _ = career("golden_chart_01.json")
    with pytest.raises(ValueError, match="begins with AstroState"):
        build_career_prediction(batch, neutral_insufficient(inference))

    missing = build_career_prediction(batch, None)
    assert isinstance(missing, DomainBuildRejected)
    assert missing.issues[0].code == "MISSING_INFERENCE_RESULT"

    with pytest.raises(ValueError, match="begins with AstroState"):
        build_career_prediction(
            batch, replace(inference, status=InferenceStatus.INSUFFICIENT_EVIDENCE)
        )


def test_insufficient_prediction_rejects_score_confidence_and_agreement_changes():
    _, batch, inference, _ = career("golden_chart_01.json")
    with pytest.raises(ValueError, match="begins with AstroState"):
        build_career_prediction(batch, neutral_insufficient(inference))
