"""Prompt-05 R4 supported-operation attacks against evaluated authority."""

from __future__ import annotations

from dataclasses import fields, replace
import json
from pathlib import Path

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine import domain as domain_api
from systems.Parasara.engine.domain import (
    DomainBuildProduced,
    DomainIndicator,
    DomainPrediction,
    DomainPredictionFactory,
    YogaDiagnostic,
    YogaDiagnosticFactory,
    prompt05_model_logical_json_bytes,
    prompt05_model_to_logical_data,
)
from systems.Parasara.engine.domain.models import (
    domain_prediction_from_logical_data,
    domain_prediction_from_logical_json,
    yoga_diagnostic_from_logical_data,
    yoga_diagnostic_from_logical_json,
)
from systems.Parasara.engine.enrichments.yoga_engine import (
    build_yoga_diagnostics,
    build_yoga_snapshot,
    evaluate_yoga_diagnostics,
    evaluate_yoga_snapshot,
    load_yoga_rule_source,
    project_yoga_compatibility,
)
from systems.Parasara.engine.inference import (
    InferenceCompatibilityProjection,
    InferenceEngine,
    inference_config_logical_sha256,
    load_inference_config,
)
from systems.Parasara.engine.interpreters.career import (
    build_career_prediction,
    evaluate_career_batch,
    infer_career,
    interpret_career_domain,
    prepare_career_facts,
    project_career_compatibility,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules.canonical import CanonicalValueError
from systems.Parasara.engine.rules.rule_match import RuleMatchStatus


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"


@pytest.fixture
def career_values():
    astro = chart_to_astrostate(
        SuryaAdapter.load(FIXTURES / "surya_test_chart.json")
    )
    outcome = interpret_career_domain(astro)
    assert isinstance(outcome, DomainBuildProduced)
    prediction = outcome.prediction
    return (
        astro,
        prediction.source_evaluation_batch,
        prediction.source_inference_result,
        prediction,
    )


@pytest.fixture
def yoga_values():
    astro = chart_to_astrostate(
        SuryaAdapter.load(FIXTURES / "golden_chart_01.json")
    )
    diagnostics = evaluate_yoga_diagnostics(astro)
    return astro, diagnostics[0]


def _alternate_config(**compatibility_changes):
    config = load_inference_config()
    compatibility = {
        **dict(config.career_compatibility),
        **compatibility_changes,
    }
    normalization_changes = compatibility.pop("_normalization", {})
    return replace(
        config,
        career_compatibility=compatibility,
        normalization={**dict(config.normalization), **normalization_changes},
    )


def test_r4_attack_01_original_inference_plus_alternate_formula_rejected(career_values):
    _, batch, _, _ = career_values
    alternate = _alternate_config(public_formula="attacker_formula")
    generic = infer_career(batch, config=alternate)
    assert generic.domain == "career"
    assert not hasattr(InferenceEngine, "compatibility_projection")
    with pytest.raises(ValueError, match="begins with AstroState"):
        build_career_prediction(batch, generic)


def test_r4_attack_02_alternate_baseline_or_category_cannot_change_authority(career_values):
    _, batch, _, prediction = career_values
    alternate = _alternate_config(
        baseline_category="attacker_category",
        baseline_neutral=0.125,
    )
    generic = infer_career(batch, config=alternate)
    assert inference_config_logical_sha256(alternate) != (
        prediction.source_authority.config_fingerprint
    )
    with pytest.raises(ValueError, match="begins with AstroState"):
        build_career_prediction(batch, generic)


def test_r4_attack_03_alternate_precision_cannot_change_public_rounding(career_values):
    _, batch, _, prediction = career_values
    alternate = _alternate_config(_normalization={"precision": 1})
    generic = infer_career(batch, config=alternate)
    assert prediction.career_compatibility.precision == 3
    with pytest.raises(ValueError, match="begins with AstroState"):
        build_career_prediction(batch, generic)


def test_r4_attack_04_coordinated_config_projection_and_digest_rejected(career_values):
    _, batch, _, prediction = career_values
    alternate = _alternate_config(public_formula="coordinated_formula")
    generic = infer_career(batch, config=alternate)
    forged_profile = replace(
        prediction.career_compatibility,
        formula="coordinated_formula",
        source_batch_digest=replace(batch, base_score=0.0).logical_digest,
    )
    with pytest.raises(ValueError, match="validated producer factory"):
        replace(
            prediction,
            career_compatibility=forged_profile,
            source_inference_result=generic,
            logical_digest="",
        )


def test_r4_attack_05_direct_or_replaced_inference_projection_rejected(career_values):
    projection = career_values[3].source_inference_compatibility
    values = {item.name: getattr(projection, item.name) for item in fields(projection)}
    with pytest.raises(ValueError, match="authoritative InferenceEngine"):
        InferenceCompatibilityProjection(**values)
    with pytest.raises(ValueError, match="authoritative InferenceEngine"):
        replace(projection, formula="forged")


def test_r4_attack_06_replaced_batch_and_unmatched_rule_evidence_rejected(career_values):
    _, batch, inference, _ = career_values
    candidate = next(item for item in batch.candidates if not item.rule_match.matched)
    forged_match = replace(
        candidate.rule_match,
        evidence={**dict(candidate.rule_match.evidence), "forged": True},
    )
    forged_batch = replace(
        batch,
        candidates=(
            *batch.candidates[: candidate.definition.source_index],
            replace(candidate, rule_match=forged_match),
            *batch.candidates[candidate.definition.source_index + 1 :],
        ),
    )
    with pytest.raises(ValueError, match="begins with AstroState"):
        build_career_prediction(forged_batch, inference)


def test_r4_attack_07_contribution_free_indicator_parent_replacement_rejected(career_values):
    _, batch, _, prediction = career_values
    indicator = prediction.indicators[0]
    with pytest.raises(ValueError, match="evaluator-owned producer boundary"):
        replace(
            indicator,
            source_contribution_id=None,
            contribution=None,
            evidence_summary=indicator.source_rule_match.evidence,
            trace_id=indicator.source_rule_match.trace_id,
        )
    with pytest.raises(ValueError, match="begins with AstroState"):
        build_career_prediction(replace(batch, base_score=0.0), prediction.source_inference_result)


def test_r4_attack_08_score_bearing_indicator_detached_from_ledger_rejected(career_values):
    indicator = career_values[3].indicators[0]
    with pytest.raises(ValueError, match="evaluator-owned producer boundary"):
        replace(indicator, source_rule_id="detached.rule")
    assert not hasattr(DomainPredictionFactory, "from_inference")


def test_r4_attack_09_replaced_yoga_record_compatibility_evidence_rejected(yoga_values):
    _, diagnostic = yoga_values
    record = diagnostic.source_evaluation_record
    forged_record = replace(record, compatibility_evidence={"forged": True})
    batch = _yoga_batch_for_record(record)
    forged_batch = replace(
        batch,
        records=(forged_record, *batch.records[1:]),
    )
    with pytest.raises(ValueError, match="inside canonical evaluation"):
        build_yoga_diagnostics(forged_batch)
    assert not hasattr(YogaDiagnosticFactory, "from_evaluation_record")


def _yoga_batch_for_record(record):
    astro = chart_to_astrostate(
        SuryaAdapter.load(FIXTURES / "golden_chart_01.json")
    )
    source = load_yoga_rule_source()
    build = build_yoga_snapshot(astro, source)
    batch = evaluate_yoga_snapshot(build.snapshot, source)
    return replace(batch, records=(record, *batch.records[1:]))


def test_r4_attack_10_coordinated_yoga_logical_reconstruction_rejected(yoga_values):
    _, diagnostic = yoga_values
    data = prompt05_model_to_logical_data(diagnostic)
    data["matched"] = not data["matched"]
    data["source_rule_match"]["matched"] = data["matched"]
    data["logical_digest"] = ""
    with pytest.raises(CanonicalValueError, match="one-way presentation"):
        yoga_diagnostic_from_logical_data(
            json.loads(json.dumps(data)),
            source_evaluation_record=diagnostic.source_evaluation_record,
        )


def test_r4_attack_11_condition_truth_disagreement_cannot_become_authority(yoga_values):
    _, diagnostic = yoga_values
    record = diagnostic.source_evaluation_record
    match = record.rule_match
    forged_match = replace(
        match,
        matched=not match.matched,
        status=(
            RuleMatchStatus.MATCHED
            if not match.matched
            else RuleMatchStatus.UNMATCHED
        ),
    )
    with pytest.raises(ValueError, match="must agree"):
        replace(record, rule_match=forged_match)


def test_r4_attack_12_direct_and_replace_evaluated_objects_rejected(career_values, yoga_values):
    prediction = career_values[3]
    indicator = prediction.indicators[0]
    diagnostic = yoga_values[1]
    for value in (prediction, indicator, diagnostic):
        constructor = {item.name: getattr(value, item.name) for item in fields(value)}
        with pytest.raises(ValueError):
            value.__class__(**constructor)
        with pytest.raises(ValueError):
            replace(value)


def test_r4_attack_13_public_dictionaries_cannot_be_reintroduced_as_authority(career_values, yoga_values):
    prediction = career_values[3]
    diagnostic = yoga_values[1]
    with pytest.raises(CanonicalValueError, match="one-way presentation"):
        domain_prediction_from_logical_data(prompt05_model_to_logical_data(prediction))
    with pytest.raises(CanonicalValueError, match="one-way presentation"):
        domain_prediction_from_logical_json(prompt05_model_logical_json_bytes(prediction))
    with pytest.raises(CanonicalValueError, match="one-way presentation"):
        yoga_diagnostic_from_logical_json(prompt05_model_logical_json_bytes(diagnostic))


def test_r4_attack_14_public_helpers_cannot_mint_caller_authority(career_values):
    _, batch, inference, _ = career_values
    assert "build_career_prediction" not in domain_api.__all__
    assert "domain_prediction_from_logical_data" not in domain_api.__all__
    assert "yoga_diagnostic_from_logical_data" not in domain_api.__all__
    assert not hasattr(DomainPredictionFactory, "from_inference")
    assert not hasattr(YogaDiagnosticFactory, "from_evaluation_record")
    with pytest.raises(ValueError, match="begins with AstroState"):
        build_career_prediction(batch, inference)
    assert isinstance(project_career_compatibility(batch, inference), dict)
