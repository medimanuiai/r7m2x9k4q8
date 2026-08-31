from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.capability import CapabilityInspection, CapabilityReadiness
from systems.Parasara.engine.domain import (
    DomainBuildProduced,
    DomainPredictionFactory,
    TimingOutputStatus,
    TransitPosition,
    TransitSummaryFactory,
    compatibility_value,
    prompt05_model_to_logical_data,
    transit_summary_from_logical_data,
)
from systems.Parasara.engine.domain.models import (
    domain_prediction_from_logical_data,
    yoga_diagnostic_from_logical_data,
)
from systems.Parasara.engine.enrichments.yoga_engine import (
    build_yoga_snapshot,
    evaluate_yoga_snapshot,
    evaluate_yoga_diagnostics,
    load_yoga_rule_source,
)
from systems.Parasara.engine.inference import (
    EvidenceReference,
    InferenceCompatibilityProjection,
)
from systems.Parasara.engine.interpreters.career import (
    build_career_prediction,
    evaluate_career_batch,
    infer_career,
    interpret_career_domain,
    prepare_career_facts,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"
ENGINE = ROOT / "systems" / "Parasara" / "engine"


def career_prediction():
    astro = chart_to_astrostate(SuryaAdapter.load(FIXTURES / "surya_test_chart.json"))
    outcome = interpret_career_domain(astro)
    assert isinstance(outcome, DomainBuildProduced)
    batch = outcome.prediction.source_evaluation_batch
    inference = outcome.prediction.source_inference_result
    return batch, inference, outcome.prediction


def reconstruct(prediction, data, *, batch=None):
    return domain_prediction_from_logical_data(
        data,
        source_inference_result=prediction.source_inference_result,
        source_inference_compatibility=prediction.source_inference_compatibility,
        source_evaluation_batch=(
            prediction.source_evaluation_batch if batch is None else batch
        ),
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("base_score", 0.0),
        ("total_contribution", 0.0),
        ("formula", "attacker_formula"),
        ("public_trace_id", "attacker.trace"),
        ("precision", 1),
        ("source_batch_digest", "0" * 64),
    ),
)
def test_career_scalar_projection_attacks_fail(field_name, value):
    _, _, prediction = career_prediction()
    data = prompt05_model_to_logical_data(prediction)
    data["career_compatibility"][field_name] = value
    data["logical_digest"] = ""
    with pytest.raises(ValueError):
        reconstruct(prediction, data)


def test_career_context_evidence_and_coordinated_replace_attacks_fail():
    batch, _, prediction = career_prediction()
    profile = prediction.career_compatibility
    first = profile.indicators[0]
    assert first.context != compatibility_value({"forged": True})
    for field_name in ("context", "evidence"):
        data = prompt05_model_to_logical_data(prediction)
        data["career_compatibility"]["indicators"][0][field_name] = {
            "entries": [{"key": "forged", "value": {"value": True}}]
        }
        data["logical_digest"] = ""
        with pytest.raises(ValueError, match="one-way presentation"):
            reconstruct(prediction, data)

    forged_batch = replace(batch, base_score=batch.base_score + 0.001)
    forged_profile = replace(
        profile,
        source_batch_digest=forged_batch.logical_digest,
        formula="attacker_formula",
    )
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(
            prediction,
            career_compatibility=forged_profile,
            source_evaluation_batch=forged_batch,
            logical_digest="",
        )


def test_career_logical_reconstruction_requires_sources_and_rejects_tampering():
    batch, inference, prediction = career_prediction()
    data = prompt05_model_to_logical_data(prediction)
    with pytest.raises(ValueError, match="one-way presentation"):
        domain_prediction_from_logical_data(
            data, source_inference_result=inference
        )

    data["career_compatibility"]["formula"] = "attacker_formula"
    data["logical_digest"] = ""
    with pytest.raises(ValueError, match="one-way presentation"):
        domain_prediction_from_logical_data(
            data,
            source_inference_result=inference,
            source_inference_compatibility=prediction.source_inference_compatibility,
            source_evaluation_batch=batch,
        )


def test_contribution_free_indicator_rejects_forged_parent_rulematch():
    batch, _, prediction = career_prediction()
    source = prediction.indicators[0]
    forged_match = replace(
        source.source_rule_match,
        evidence={**dict(source.source_rule_match.evidence), "forged": True},
    )
    with pytest.raises(ValueError, match="evaluator-owned producer boundary"):
        replace(
            source,
            source_contribution_id=None,
            contribution=None,
            evidence_summary=forged_match.evidence,
            source_rule_match=forged_match,
            trace_id=forged_match.trace_id,
        )
    data = prompt05_model_to_logical_data(prediction)
    indicator = data["indicators"][0]
    indicator["source_contribution_id"] = None
    indicator["contribution"] = None
    indicator["source_rule_match"]["evidence"]["forged"] = True
    indicator["evidence_summary"] = indicator["source_rule_match"]["evidence"]
    indicator["trace_id"] = indicator["source_rule_match"]["trace_id"]
    data["logical_digest"] = ""
    with pytest.raises(ValueError, match="one-way presentation"):
        reconstruct(prediction, data, batch=batch)


def test_indicator_logical_reconstruction_rejects_clearing_and_fabrication():
    batch, inference, prediction = career_prediction()
    data = prompt05_model_to_logical_data(prediction)
    indicator = data["indicators"][0]
    indicator["source_contribution_id"] = None
    indicator["contribution"] = None
    indicator["evidence_summary"] = indicator["source_rule_match"]["evidence"]
    indicator["trace_id"] = indicator["source_rule_match"]["trace_id"]
    indicator["source_rule_match"]["evidence"]["forged"] = True
    data["logical_digest"] = ""
    with pytest.raises(ValueError):
        domain_prediction_from_logical_data(
            data,
            source_inference_result=inference,
            source_inference_compatibility=prediction.source_inference_compatibility,
            source_evaluation_batch=batch,
        )


def test_yoga_retains_original_record_and_rejects_direct_and_logical_attacks():
    astro = chart_to_astrostate(SuryaAdapter.load(FIXTURES / "golden_chart_01.json"))
    diagnostic = evaluate_yoga_diagnostics(astro)[0]
    record = diagnostic.source_evaluation_record
    assert diagnostic.source_rule_match is record.rule_match
    assert "compatibility_projection" not in diagnostic.source_rule_match.metadata
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(diagnostic, name="Forged Yoga", logical_digest="")

    data = prompt05_model_to_logical_data(diagnostic)
    data["compatibility"]["evidence"] = {"forged": True}
    data["logical_digest"] = ""
    with pytest.raises(ValueError):
        yoga_diagnostic_from_logical_data(
            data, source_evaluation_record=record
        )


def test_transit_cannot_mint_or_deserialize_ready_empty_without_a_producer():
    capability = CapabilityInspection(
        capability_id="transits.current",
        expected_version="9.9.9",
        observed_version="9.9.9",
        readiness=CapabilityReadiness.READY_EMPTY,
        source_kind="transit_producer",
        content_empty=True,
        issues=(),
    )
    with pytest.raises(ValueError, match="no authoritative producer"):
        TransitSummaryFactory.producer_evidence(
            capability=capability,
            positions=(),
            producer_version="attacker-9.9.9",
            producer_schema_version="9.9.9",
            trace_id="attacker.transit",
        )
    batch, inference, _ = career_prediction()
    with pytest.raises(ValueError, match="no authoritative producer"):
        TransitSummaryFactory.producer_evidence(
            capability=capability,
            positions=(TransitPosition(
                body_id="FakeBody",
                longitude_degrees=1.0,
                sign_id="FakeSign",
                source_fact_id="fake.fact",
                order=0,
            ),),
            natal_target_references=(EvidenceReference(
                evidence_id="fake.target.evidence",
                source_type="fake",
                source_id="fake.target",
                trace_id="fake.target.trace",
                correlation_key="fake.target",
                order=0,
            ),),
            rule_matches=(batch.rule_matches[0],),
            domain_effect_results=(inference,),
            producer_version="attacker-9.9.9",
            producer_schema_version="9.9.9",
            trace_id="fake.producer.trace",
        )
    with pytest.raises(ValueError, match="no authoritative producer"):
        TransitSummaryFactory.from_calculator_output(
            status=TimingOutputStatus.AVAILABLE,
            reference_instant="2020-01-01T00:00:00+00:00",
            positions=(),
            natal_relationships=(),
            active_rule_match_ids=(),
            domain_effect_trace_ids=(),
            producer_evidence=None,
            calculation_version="attacker-9.9.9",
            trace_id="attacker.transit",
        )

    data = prompt05_model_to_logical_data(TransitSummaryFactory.unavailable())
    data.update(
        status="available",
        reference_instant="2020-01-01T00:00:00+00:00",
        calculation_version="attacker-9.9.9",
        issues=[],
        trace_id="attacker.transit",
        logical_digest="",
    )
    with pytest.raises(ValueError, match="no authoritative producer"):
        transit_summary_from_logical_data(data)


def test_inference_projection_is_sealed_and_aggregation_stays_in_engine():
    with pytest.raises(ValueError, match="authoritative InferenceEngine"):
        InferenceCompatibilityProjection(
            profile_id="career_public_v1",
            source_result_digest="0" * 64,
            source_config_digest="0" * 64,
            base_score=0.5,
            total_contribution=0.0,
            formula="forged",
            public_trace_id="career.inference",
            precision=3,
        )

    for relative in (
        "output_assembler.py",
        "domain/factories.py",
        "domain/models.py",
    ):
        module = ast.parse((ENGINE / relative).read_text(encoding="utf-8"))
        calls = {
            node.func.id if isinstance(node.func, ast.Name) else node.func.attr
            for node in ast.walk(module)
            if isinstance(node, ast.Call)
            and isinstance(node.func, (ast.Name, ast.Attribute))
        }
        assert not {"sum", "fsum", "aggregate"} & calls, relative

    engine_source = (ENGINE / "inference" / "engine.py").read_text(encoding="utf-8")
    career_source = (ENGINE / "interpreters" / "career.py").read_text(encoding="utf-8")
    assert "total_contribution = math.fsum(" in engine_source
    post_inference = career_source[career_source.index("def _career_domain_components("):]
    assert "base_score +=" not in post_inference
    assert "sum(" not in post_inference
