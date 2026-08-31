from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.astrostate import AstroState
from systems.Parasara.engine.domain import (
    DomainBuildProduced,
    DomainBuildRejected,
    DomainId,
    DomainStatus,
    YogaDiagnostic,
    prompt05_model_logical_json_bytes,
)
from systems.Parasara.engine.domain.models import yoga_diagnostic_from_logical_json
from systems.Parasara.engine.enrichments.yoga_engine import (
    build_yoga_snapshot,
    evaluate_yoga_snapshot,
    evaluate_yoga_diagnostics,
    load_yoga_rule_source,
    project_yoga_compatibility,
)
from systems.Parasara.engine.interpreters.career import (
    build_career_prediction,
    interpret_career,
    interpret_career_domain,
    project_career_compatibility,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.output_assembler import (
    project_career_prediction_compatibility,
    project_yoga_diagnostics_compatibility,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"


def compact(value) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def test_career_outcome_reconciles_exactly_to_one_inference(career_source):
    _, batch, inference, outcome = career_source
    assert isinstance(outcome, DomainBuildProduced)
    prediction = outcome.prediction
    assert prediction.domain is DomainId.CAREER
    assert prediction.status is DomainStatus.EVALUATED
    assert prediction.score == inference.normalized_score
    assert prediction.confidence == inference.confidence
    assert prediction.agreement == inference.agreement
    assert prediction.conflicts == inference.conflicts
    assert prediction.data_completeness == inference.data_completeness
    assert prediction.source_inference_trace_id == inference.trace_id
    assert prediction.rule_set_version == inference.rule_set_version
    assert prediction.inference_version == inference.inference_version
    assert prediction.source_inference_result is inference
    assert tuple(item.component_id for item in prediction.components) == tuple(
        item.fact_id for item in batch.component_facts
    )


def test_career_build_rejects_a_broken_domain_reference(career_source):
    _, batch, inference, _ = career_source
    with pytest.raises(ValueError, match="begins with AstroState"):
        build_career_prediction(batch, replace(inference, domain="wealth"))


def test_career_public_wrapper_is_only_a_projection_of_typed_result(career_source):
    astro, batch, inference, outcome = career_source
    assert isinstance(outcome, DomainBuildProduced)
    expected = project_career_prediction_compatibility(outcome.prediction)
    assert project_career_compatibility(batch, inference) == expected
    assert interpret_career(astro) == expected
    assert isinstance(interpret_career_domain(astro), DomainBuildProduced)


def test_all_locked_career_public_hashes_are_exact():
    expected = {
        "golden_chart_01.json": (403, "74442a0726173dcac3c521f1e67542443c16c43fbb39e7bded27f9e1601e3be3"),
        "surya_test_chart.json": (3495, "fee279260217eabb6a0f037d48d306888571fdf4c1c259630eca4337b5df9974"),
        "surya_generated_chart.json": (584, "169cf5ce5ac9d8e678b160daf23293f365f2ab192a02a7aad90caab4da839dd9"),
    }
    for fixture, locked in expected.items():
        astro = chart_to_astrostate(SuryaAdapter.load(FIXTURES / fixture))
        payload = compact(interpret_career(astro))
        assert (len(payload), hashlib.sha256(payload).hexdigest()) == locked


def test_canonical_empty_astro_preserves_neutral_insufficient_evidence():
    astro = AstroState(
        metadata={}, location=None, lagna_sign=None, planets=[], houses=[],
        diagnostics={}, enrichments={},
    )
    outcome = interpret_career_domain(astro)
    assert isinstance(outcome, DomainBuildProduced)
    assert outcome.prediction.status is DomainStatus.INSUFFICIENT_EVIDENCE
    assert (
        outcome.prediction.score,
        outcome.prediction.confidence,
        outcome.prediction.agreement,
    ) == (0.5, 0.0, 0.0)
    assert {item.code for item in outcome.prediction.issues} == {
        "INSUFFICIENT_EVIDENCE"
    }


def yoga_batch(fixture: str = "golden_chart_01.json"):
    astro = chart_to_astrostate(SuryaAdapter.load(FIXTURES / fixture))
    source = load_yoga_rule_source()
    build = build_yoga_snapshot(astro, source)
    return evaluate_yoga_snapshot(build.snapshot, source)


def test_yoga_diagnostics_retain_rulematch_identity_status_domains_and_digest():
    batch = yoga_batch()
    astro = chart_to_astrostate(SuryaAdapter.load(FIXTURES / "golden_chart_01.json"))
    diagnostics = evaluate_yoga_diagnostics(astro)
    assert len(diagnostics) == len(batch.records)
    for record, diagnostic in zip(batch.records, diagnostics):
        assert isinstance(diagnostic, YogaDiagnostic)
        assert diagnostic.source_rule_match == record.rule_match
        assert "compatibility_projection" not in diagnostic.source_rule_match.metadata
        assert "compatibility_evidence" not in diagnostic.source_rule_match.evidence
        assert diagnostic.compatibility.evidence == record.compatibility_evidence
        assert diagnostic.yoga_id == record.rule_match.rule_id
        assert tuple(item.value for item in diagnostic.domains) == record.rule_match.domains
        with pytest.raises(ValueError, match="one-way presentation"):
            yoga_diagnostic_from_logical_json(
                prompt05_model_logical_json_bytes(diagnostic),
                source_evaluation_record=diagnostic.source_evaluation_record,
            )


def test_yoga_diagnostic_projection_is_exact_and_preserves_source_order():
    batch = yoga_batch()
    astro = chart_to_astrostate(SuryaAdapter.load(FIXTURES / "golden_chart_01.json"))
    diagnostics = evaluate_yoga_diagnostics(astro)
    assert project_yoga_diagnostics_compatibility(diagnostics) == project_yoga_compatibility(batch)
    assert [item.yoga_id for item in diagnostics] == [item.yoga_id for item in batch.records]


def test_locked_yoga_public_hash_is_exact_after_typed_projection():
    batch = yoga_batch()
    payload = compact(project_yoga_compatibility(batch))
    assert (len(payload), hashlib.sha256(payload).hexdigest()) == (
        696,
        "de21d839d01db93b50f5eceef745886a78a12da4ab44b892c8409f62077300f0",
    )
