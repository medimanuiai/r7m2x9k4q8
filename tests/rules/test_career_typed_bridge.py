"""WP15 immutable Career factual bridge and compatibility contract."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.interpreters.career import (
    evaluate_career_batch,
    interpret_career,
    prepare_career_facts,
    project_career_compatibility,
)
from systems.Parasara.engine.interpreters.career_models import (
    CareerCandidateDefinition,
    CareerCandidateEvaluation,
    CareerEvaluationBatch,
    CareerFactKind,
    CareerFactResult,
    career_evaluation_batch_from_json_bytes,
    career_evaluation_batch_full_json_bytes,
    career_evaluation_batch_logical_json_bytes,
    career_evaluation_batch_logical_sha256,
    career_prepared_facts_json_bytes,
    career_prepared_facts_sha256,
    freeze_ordered_compatibility,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules.canonical import FrozenMapping
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.models import (
    PredicateError,
    PredicateResult,
    PredicateStatus,
    PredicateTraceStep,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"
APPROVED = ROOT / "systems" / "Parasara" / "tests" / "fixtures"
CAREER_SOURCE = ROOT / "systems" / "Parasara" / "engine" / "interpreters" / "career.py"
MODELS_SOURCE = ROOT / "systems" / "Parasara" / "engine" / "interpreters" / "career_models.py"


def load_astro(name: str):
    return chart_to_astrostate(SuryaAdapter.load(str(FIXTURES / name)))


def compact_json(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


@pytest.mark.parametrize(
    ("fixture", "approved", "byte_count", "digest"),
    (
        ("golden_chart_01.json", "golden_chart_01_career_snapshot.json", 403, "74442a0726173dcac3c521f1e67542443c16c43fbb39e7bded27f9e1601e3be3"),
        ("surya_test_chart.json", "golden_career_snapshot.json", 3495, "fee279260217eabb6a0f037d48d306888571fdf4c1c259630eca4337b5df9974"),
        ("surya_generated_chart.json", "surya_generated_chart_career_snapshot.json", 584, "169cf5ce5ac9d8e678b160daf23293f365f2ab192a02a7aad90caab4da839dd9"),
    ),
)
def test_complete_public_fixture_bytes_are_unchanged(fixture, approved, byte_count, digest):
    actual = interpret_career(load_astro(fixture))
    expected = json.loads((APPROVED / approved).read_text(encoding="utf-8"))
    payload = compact_json(actual)

    # The original surya-test artifact intentionally froze an earlier absolute-
    # path registry state; its existing test locks indicator IDs only.  WP01's
    # active explicitly loaded registry capture is the byte/hash contract below.
    if fixture != "surya_test_chart.json":
        assert actual == expected
    else:
        assert [row["rule_id"] for row in actual["indicators"]] == [
            row["rule_id"] for row in expected["indicators"]
        ]
    assert list(actual) == [
        "summary", "score", "confidence", "components", "indicators",
        "evidence", "scoring", "trace_id",
    ]
    assert len(payload) == byte_count
    assert hashlib.sha256(payload).hexdigest() == digest


def test_prepared_snapshot_and_candidate_inventory_are_exact_and_immutable():
    astro = load_astro("surya_test_chart.json")
    before = astro.model_dump(mode="python")
    prepared = prepare_career_facts(astro)
    batch = evaluate_career_batch(prepared)

    assert astro.model_dump(mode="python") == before
    assert prepared.schema_version == "1.0.0"
    assert prepared.fact_version == "1.0.0"
    assert prepared.preparation_errors == ()
    assert tuple(item.planet_id for item in prepared.planets) == (
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"
    )
    assert [item.definition.candidate_id for item in batch.candidates] == [
        "strong_in_10_Sun", "strong_in_10_Moon", "strong_in_10_Mars",
        "strong_in_10_Mercury", "strong_in_10_Jupiter", "strong_in_10_Venus",
        "strong_in_10_Saturn", "strong_in_10_Rahu", "strong_in_10_Ketu",
        "10th_lord_Venus", "rajayoga_naive",
    ]
    assert [item.definition.source_index for item in batch.candidates] == list(range(11))
    assert len(batch.candidates) == batch.confidence_denominator == 11
    assert [item.status for item in batch.candidates] == [
        PredicateStatus.UNMATCHED, PredicateStatus.UNMATCHED, PredicateStatus.UNMATCHED,
        PredicateStatus.UNMATCHED, PredicateStatus.UNMATCHED, PredicateStatus.UNMATCHED,
        PredicateStatus.UNMATCHED, PredicateStatus.UNMATCHED, PredicateStatus.UNMATCHED,
        PredicateStatus.MATCHED, PredicateStatus.MATCHED,
    ]
    assert [item.adjusted_score for item in batch.candidates] == [
        0.0, 0.0, 0.05, 0.0, 0.0, 0.05, 0.0, 0.0, 0.0, 0.18, 0.18
    ]
    assert [item.contribution for item in batch.candidates] == [
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.18, 0.18
    ]
    assert all(
        isinstance(item.fact.backing_result, PredicateResult)
        for item in batch.candidates[:9]
    )
    assert all(item.fact.backing_result is None for item in batch.candidates[9:])
    assert isinstance(prepared.planets_by_id, FrozenMapping)
    with pytest.raises((TypeError, AttributeError)):
        prepared.planets_by_id["Mars"] = None

    astro.planets[2].strength = 1.0
    astro.enrichments["house_summaries"][9]["occupants"].append("Sun")
    assert prepared.planets_by_id["Mars"]["strength"] == 0.46
    assert prepared.house10 is not None
    assert prepared.house10.occupants == ("Mars", "Venus")


def test_catalog_merge_sources_context_order_and_score_metadata_are_locked():
    batch = evaluate_career_batch(prepare_career_facts(load_astro("surya_test_chart.json")))
    strong, lord, rajayoga = batch.candidates[0], batch.candidates[-2], batch.candidates[-1]

    assert strong.definition.source_identity == "m1_rules.yaml:strong_planet_in_10"
    assert strong.definition.base_score == 0.2
    assert strong.definition.matched_score == 0.2
    assert strong.definition.unmatched_score == 0.05
    assert lord.definition.source_identity == "derived_rules.yml:lord_status_10th"
    assert lord.definition.base_score == 0.18
    assert rajayoga.definition.source_identity == "yogas.yaml:rajayoga_naive"
    assert rajayoga.definition.base_score is None

    public = project_career_compatibility(batch)
    assert list(public["indicators"][0]["context"]) == [
        "id", "name", "author", "created_date", "source_reference",
        "classical_reference", "validation_status", "sme_required",
        "sme_approved", "type", "house", "base_score", "_source_file", "lord",
    ]
    assert list(public["indicators"][1]["context"]) == [
        "id", "name", "version", "category", "provenance", "sme_approved",
        "description", "conditions", "weights", "evidence_required", "tests",
        "_source_file", "type",
    ]
    conditions = public["indicators"][1]["context"]["conditions"]
    assert list(conditions) == ["type", "children"]
    assert list(conditions["children"][0]) == ["type", "params"]


def test_registry_runtime_cwd_and_cache_warmth_cannot_change_career(monkeypatch, tmp_path):
    from systems.Parasara.engine.rules import loader

    astro = load_astro("surya_test_chart.json")
    expected = interpret_career(astro)
    registry_before = deepcopy(loader.RULE_REGISTRY)
    loader.RULE_REGISTRY.clear()
    monkeypatch.chdir(tmp_path)
    try:
        prepared = prepare_career_facts(astro)
        evaluator = PredicateEvaluator(capacity=32)
        cold = evaluate_career_batch(prepared, evaluator=evaluator)
        warm = evaluate_career_batch(prepared, evaluator=evaluator)
        actual = project_career_compatibility(warm)
    finally:
        loader.RULE_REGISTRY.clear()
        loader.RULE_REGISTRY.update(registry_before)

    assert actual == expected
    assert career_evaluation_batch_logical_json_bytes(cold) == career_evaluation_batch_logical_json_bytes(warm)
    assert career_evaluation_batch_logical_sha256(cold) == career_evaluation_batch_logical_sha256(warm)
    assert career_evaluation_batch_full_json_bytes(cold) == career_evaluation_batch_full_json_bytes(warm)
    assert evaluator.cache_size == 9


def _minimal_astro(*, strength):
    return AstroState(
        metadata={}, location=None, lagna_sign="Aries",
        planets=[PlanetState(name="Mars", sign="Aries", degree=1.0, house=10, strength=strength)],
        houses=[], diagnostics={},
        enrichments={"house_summaries": [{"number": 10, "lord": None, "occupants": ["Mars"]}]},
        derived=None,
    )


def test_present_zero_is_factual_but_absent_strength_is_nonfactual_and_both_contribute_zero():
    zero = evaluate_career_batch(prepare_career_facts(_minimal_astro(strength=0.0)))
    absent = evaluate_career_batch(prepare_career_facts(_minimal_astro(strength=None)))

    assert zero.candidates[0].status is PredicateStatus.UNMATCHED
    assert zero.candidates[0].fact.evidence["strength"] == 0.0
    assert zero.candidates[0].adjusted_score == 0.05
    assert zero.candidates[0].contribution == 0.0
    assert absent.candidates[0].status is PredicateStatus.MISSING_CAPABILITY
    assert absent.candidates[0].fact.errors[0].code == "missing_planet_strength_fact"
    assert absent.candidates[0].adjusted_score == 0.05
    assert absent.candidates[0].contribution == 0.0
    assert project_career_compatibility(zero)["indicators"] == []
    assert project_career_compatibility(absent)["indicators"] == []


def test_models_enforce_status_invariants_and_retain_all_nonfactual_statuses():
    trace = PredicateTraceStep(
        step_id="career.test", operation="controlled_status", details={}, observation={"safe": True}
    )
    definition = CareerCandidateDefinition(
        candidate_id="controlled", rule_type="strong_in_10", rule_version="1.0",
        source_identity="controlled:definition", normalized_parameters={"planet": "Mars", "house": 10},
        compatibility_context=freeze_ordered_compatibility({}), base_score=0.2, matched_score=0.2,
        unmatched_score=0.05, source_index=0,
    )
    for status in (
        PredicateStatus.MISSING_CAPABILITY, PredicateStatus.INVALID_PARAMETERS,
        PredicateStatus.ERROR, PredicateStatus.TIMEOUT, PredicateStatus.SKIPPED,
    ):
        error = PredicateError(
            code=f"controlled_{status.value}", message="Controlled safe status.",
            predicate_id="career.fact.controlled", details={"status": status.value}, recoverable=True,
        )
        fact = CareerFactResult(
            fact_id="career.fact.controlled", fact_version="1.0.0",
            fact_kind=CareerFactKind.STRONG_IN_HOUSE, matched=False, status=status,
            inputs={"planet": "Mars", "house": 10}, evidence={}, errors=(error,),
            trace_steps=(trace,), backing_result=None, evaluation_time_ms=None,
        )
        evaluation = CareerCandidateEvaluation(
            definition=definition, fact=fact, matched=False, status=status,
            adjusted_score=0.0, contribution=0.0, compatibility_evidence={},
            trace_lineage=("career.test",), evaluation_time_ms=None,
        )
        assert evaluation.status is status
        assert evaluation.contribution == 0.0

    with pytest.raises(ValueError):
        CareerFactResult(
            fact_id="career.fact.invalid", fact_version="1.0.0",
            fact_kind=CareerFactKind.STRONG_IN_HOUSE, matched=True,
            status=PredicateStatus.UNMATCHED, inputs={}, evidence={}, errors=(),
            trace_steps=(trace,), backing_result=None, evaluation_time_ms=None,
        )


def test_prepared_and_batch_serialization_are_strict_stable_and_round_trip():
    prepared = prepare_career_facts(load_astro("surya_test_chart.json"))
    batch = evaluate_career_batch(prepared)
    logical = career_evaluation_batch_logical_json_bytes(batch)
    full = career_evaluation_batch_full_json_bytes(batch)
    restored = career_evaluation_batch_from_json_bytes(full, full=True)

    assert logical.startswith(b"{") and logical.endswith(b"}") and b"\n" not in logical
    assert full.startswith(b"{") and full.endswith(b"}") and b"\n" not in full
    assert restored == batch
    assert career_evaluation_batch_logical_json_bytes(restored) == logical
    assert career_prepared_facts_sha256(prepared) == hashlib.sha256(career_prepared_facts_json_bytes(prepared)).hexdigest()
    assert len(career_prepared_facts_sha256(prepared)) == 64


def test_public_projection_is_one_way_fresh_and_does_not_feed_batch_identity():
    batch = evaluate_career_batch(prepare_career_facts(load_astro("surya_test_chart.json")))
    identity = career_evaluation_batch_logical_sha256(batch)
    first = project_career_compatibility(batch)
    second = project_career_compatibility(batch)
    first["components"][0]["planet"] = "Changed"
    first["indicators"][0]["context"]["lord"] = "Changed"

    assert second["components"][0]["planet"] == "Moon"
    assert second["indicators"][0]["context"]["lord"] == "Venus"
    assert career_evaluation_batch_logical_sha256(batch) == identity


def test_safe_catastrophic_preparation_policy_preserves_public_schema():
    prepared = prepare_career_facts(SimpleNamespace())
    batch = evaluate_career_batch(prepared)
    public = project_career_compatibility(batch)

    assert prepared.preparation_errors[0].code == "career_preparation_failed"
    assert batch.batch_errors[0].code == "career_preparation_failed"
    assert public == {
        "summary": "Career score 0.5 (confidence 0.0)",
        "score": 0.5,
        "confidence": 0.0,
        "components": [],
        "indicators": [],
        "evidence": [],
        "scoring": {
            "base_score": 0.5, "total_contribution": 0.0, "final_score": 0.5,
            "formula": "final = min(1.0, base_score + sum(contributions))",
        },
        "trace_id": "career_001",
    }


def test_injected_evaluator_defects_are_safe_typed_and_keep_every_candidate(monkeypatch):
    astro = load_astro("surya_test_chart.json")
    prepared = prepare_career_facts(astro)

    def fail(*_args, **_kwargs):
        raise RuntimeError("secret raw exception and path must not escape")

    monkeypatch.setattr(PredicateEvaluator, "evaluate", fail)
    batch = evaluate_career_batch(prepared, evaluator=PredicateEvaluator())
    public = project_career_compatibility(batch)

    assert len(batch.candidates) == batch.confidence_denominator == 11
    assert all(item.status is PredicateStatus.ERROR for item in batch.candidates[:9])
    assert all(item.contribution == 0.0 for item in batch.candidates[:9])
    assert batch.candidates[0].fact.errors[0].code == "career_candidate_evaluation_failed"
    assert "secret" not in career_evaluation_batch_full_json_bytes(batch).decode("utf-8")
    assert [row["rule_id"] for row in public["indicators"]] == [
        "10th_lord_Venus", "rajayoga_naive"
    ]


def test_career_static_architecture_rejects_legacy_runtime_loader_raw_provider_and_direct_handlers():
    forbidden_imports = {
        "runtime", "loader", "surya_adapter", "yoga", "canonical_predicates", "planet_in_house"
    }
    forbidden_calls = {
        "evaluate_rule_with_score", "evaluate_rule", "load_rules_from_dir", "get_rule",
        "evaluate_planet_in_house", "evaluate_house_occupant",
    }
    for path in (CAREER_SOURCE, MODELS_SOURCE):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        called = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imported.update(alias.name for alias in node.names)
                imported.add((node.module or "").split(".")[-1])
            elif isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[-1] for alias in node.names)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called.add(node.func.attr)
        assert imported.isdisjoint(forbidden_imports)
        assert called.isdisjoint(forbidden_calls)
        assert "RULE_REGISTRY" not in source
        assert "os.getcwd" not in source
        assert "except Exception:\n            matched = False" not in source
