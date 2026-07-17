"""Cross-model strict serialization and public compatibility matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.enrichments.yoga_engine import (
    evaluate_yoga_batch,
    load_yoga_rule_source,
    prepare_legacy_yoga_state,
    project_yoga_compatibility,
    yoga_batch_from_full_json,
    yoga_batch_from_logical_json,
    yoga_batch_full_json_bytes,
    yoga_batch_logical_json_bytes,
    yoga_batch_logical_sha256,
    yoga_batch_to_logical_data,
)
from systems.Parasara.engine.interpreters.career import (
    evaluate_career_batch,
    interpret_career,
    prepare_career_facts,
    project_career_compatibility,
)
from systems.Parasara.engine.interpreters.career_models import (
    career_evaluation_batch_from_json_bytes,
    career_evaluation_batch_full_json_bytes,
    career_evaluation_batch_logical_json_bytes,
    career_evaluation_batch_logical_sha256,
    career_evaluation_batch_to_logical_data,
    career_prepared_facts_json_bytes,
    career_prepared_facts_sha256,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules.canonical import (
    CanonicalValueError,
    FrozenMapping,
    canonical_json_bytes,
    condition_result_from_full_json,
    condition_result_from_logical_json,
    condition_result_full_json_bytes,
    condition_result_logical_json_bytes,
    condition_result_logical_sha256,
    condition_result_to_logical_data,
    predicate_result_from_full_json,
    predicate_result_from_logical_json,
    predicate_result_full_json_bytes,
    predicate_result_logical_json_bytes,
    predicate_result_logical_sha256,
    predicate_result_to_logical_data,
)
from systems.Parasara.engine.rules.conditions import ConditionEvaluator
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.models import ConditionResult
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    prepare_predicate_state,
    prepared_state_json_bytes,
    prepared_state_sha256,
    prepared_state_to_data,
)
from tests.testing_framework.generate_full_artifacts import run_rules_and_trace
from tests.testing_framework.rule_coverage import run_rule_coverage_scan


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"


def _astro(name="surya_test_chart.json"):
    return chart_to_astrostate(SuryaAdapter.load(str(FIXTURES / name)))


def _predicate_state():
    source = SimpleNamespace(
        planets=[
            SimpleNamespace(name="Mars", sign="Aries", degree=12.0, house=1),
            SimpleNamespace(name="Moon", sign="Cancer", degree=4.0, house=4),
        ],
        lagna_sign="Aries",
        enrichments={
            "aspects": {
                "edges": [{"source": "Mars", "target": "Moon", "kind": "whole_sign"}],
                "config_version": "legacy-v1",
            }
        },
        derived={"functional_roles": {"Mars": {"functional_role": "yogakaraka"}}},
        metadata={"exaltations": {}},
        diagnostics={},
    )
    outcome = prepare_predicate_state(source)
    assert outcome.succeeded and outcome.state is not None
    return outcome.state


def _models():
    state = _predicate_state()
    evaluator = PredicateEvaluator()
    predicate = evaluator.evaluate(
        "PLANET_IN_HOUSE",
        {"planet": "Mars", "house": 1},
        state,
        PredicateEvaluationContext(),
    )
    condition = ConditionEvaluator(PredicateEvaluator()).evaluate(
        {
            "type": "AND",
            "children": [
                {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 1}},
                {
                    "type": "OR",
                    "children": [
                        {"type": "HOUSE_OCCUPANT", "params": {"planet": "Moon", "house": 5}},
                        {"type": "HOUSE_OCCUPANT", "params": {"planet": "Moon", "house": 4}},
                    ],
                },
            ],
        },
        state,
        PredicateEvaluationContext(),
    )
    assert isinstance(condition, ConditionResult)

    astro = _astro()
    yoga_source = load_yoga_rule_source()
    preparation = prepare_legacy_yoga_state(astro, yoga_source)
    assert preparation.outcome.succeeded and preparation.outcome.state is not None
    yoga = evaluate_yoga_batch(
        preparation.outcome.state,
        PredicateEvaluationContext(),
        yoga_source,
        predicate_evaluator=PredicateEvaluator(),
        compatibility_graph=preparation.compatibility_graph,
    )
    career_prepared = prepare_career_facts(astro)
    career = evaluate_career_batch(career_prepared)
    return state, predicate, condition, yoga, career_prepared, career


def _assert_compact_strict_json(payload: bytes):
    assert isinstance(payload, bytes)
    assert payload.startswith((b"{", b"["))
    assert payload.endswith((b"}", b"]"))
    assert b"\n" not in payload and b"\r" not in payload
    assert b"NaN" not in payload and b"Infinity" not in payload
    assert json.loads(payload.decode("utf-8")) is not None


def _contains_key(value, key):
    if isinstance(value, dict):
        return key in value or any(_contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, key) for item in value)
    return False


def test_cross_model_logical_full_round_trip_hash_and_telemetry_matrix():
    state, predicate, condition, yoga, career_prepared, career = _models()
    cases = (
        (
            "predicate",
            predicate,
            predicate_result_logical_json_bytes,
            predicate_result_full_json_bytes,
            predicate_result_from_logical_json,
            predicate_result_from_full_json,
            predicate_result_logical_sha256,
        ),
        (
            "condition",
            condition,
            condition_result_logical_json_bytes,
            condition_result_full_json_bytes,
            condition_result_from_logical_json,
            condition_result_from_full_json,
            condition_result_logical_sha256,
        ),
        (
            "yoga",
            yoga,
            yoga_batch_logical_json_bytes,
            yoga_batch_full_json_bytes,
            yoga_batch_from_logical_json,
            yoga_batch_from_full_json,
            yoga_batch_logical_sha256,
        ),
        (
            "career",
            career,
            career_evaluation_batch_logical_json_bytes,
            career_evaluation_batch_full_json_bytes,
            lambda payload: career_evaluation_batch_from_json_bytes(payload, full=False),
            lambda payload: career_evaluation_batch_from_json_bytes(payload, full=True),
            career_evaluation_batch_logical_sha256,
        ),
    )
    for name, model, logical_fn, full_fn, logical_parse, full_parse, sha_fn in cases:
        logical = logical_fn(model)
        full = full_fn(model)
        _assert_compact_strict_json(logical)
        _assert_compact_strict_json(full)
        restored_logical = logical_parse(logical)
        restored_full = full_parse(full)
        assert logical_fn(restored_logical) == logical, name
        assert full_fn(restored_full) == full, name
        assert sha_fn(model) == hashlib.sha256(logical).hexdigest(), name
        assert len(sha_fn(model)) == 64 and sha_fn(model) == sha_fn(model).lower()

        logical_data = json.loads(logical)
        assert not _contains_key(logical_data, "cache_hit"), name
        assert not _contains_key(logical_data, "evaluation_time_ms"), name
        assert not _contains_key(logical_data, "total_duration_ms"), name

    prepared_payloads = (
        (prepared_state_json_bytes(state), prepared_state_sha256(state)),
        (
            career_prepared_facts_json_bytes(career_prepared),
            career_prepared_facts_sha256(career_prepared),
        ),
    )
    for payload, digest in prepared_payloads:
        _assert_compact_strict_json(payload)
        assert digest == hashlib.sha256(payload).hexdigest()


def test_strict_parsers_reject_duplicate_keys_nonfinite_and_malformed_utf8():
    parsers = (
        predicate_result_from_logical_json,
        condition_result_from_logical_json,
        yoga_batch_from_logical_json,
        lambda payload: career_evaluation_batch_from_json_bytes(payload, full=False),
    )
    for parser in parsers:
        with pytest.raises((CanonicalValueError, ValueError)):
            parser(b'{"duplicate":1,"duplicate":2}')
        with pytest.raises((CanonicalValueError, ValueError)):
            parser(b'{"value":NaN}')
        with pytest.raises((CanonicalValueError, ValueError)):
            parser(b"\xff")
    with pytest.raises(CanonicalValueError):
        canonical_json_bytes({"unsupported": object()})
    with pytest.raises(CanonicalValueError):
        canonical_json_bytes({"nonfinite": float("inf")})


def test_parsed_and_projected_values_are_deeply_immutable_or_fresh():
    state, predicate, condition, yoga, _career_prepared, career = _models()
    restored_predicate = predicate_result_from_full_json(
        predicate_result_full_json_bytes(predicate)
    )
    restored_condition = condition_result_from_full_json(
        condition_result_full_json_bytes(condition)
    )
    restored_yoga = yoga_batch_from_full_json(yoga_batch_full_json_bytes(yoga))
    restored_career = career_evaluation_batch_from_json_bytes(
        career_evaluation_batch_full_json_bytes(career), full=True
    )
    assert isinstance(restored_predicate.inputs, FrozenMapping)
    assert isinstance(restored_condition.details, FrozenMapping)
    assert isinstance(restored_yoga.records[0].compatibility_evidence, FrozenMapping)
    assert isinstance(restored_career.candidates[0].fact.inputs, FrozenMapping)
    with pytest.raises((TypeError, AttributeError)):
        restored_predicate.inputs["planet"] = "Changed"
    with pytest.raises((TypeError, AttributeError)):
        restored_condition.details["changed"] = True

    state_data = prepared_state_to_data(state)
    predicate_data = predicate_result_to_logical_data(predicate)
    condition_data = condition_result_to_logical_data(condition)
    yoga_data = yoga_batch_to_logical_data(yoga)
    career_data = career_evaluation_batch_to_logical_data(career)
    assert all(
        value is not None
        for value in (state_data, predicate_data, condition_data, yoga_data, career_data)
    )
    yoga_public_a = project_yoga_compatibility(yoga)
    yoga_public_b = project_yoga_compatibility(yoga)
    career_public_a = project_career_compatibility(career)
    career_public_b = project_career_compatibility(career)
    yoga_public_a[0]["evidence"].clear()
    career_public_a["components"].clear()
    assert yoga_public_b == project_yoga_compatibility(yoga)
    assert career_public_b == project_career_compatibility(career)


def test_public_compatibility_order_and_exact_bytes_remain_separate_from_canonical_sorting():
    _state, _predicate, _condition, yoga, _career_prepared, career = _models()
    yoga_public = project_yoga_compatibility(yoga)
    career_public = project_career_compatibility(career)
    yoga_bytes = json.dumps(
        yoga_public, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    career_bytes = json.dumps(
        career_public, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    assert list(yoga_public[0]) == [
        "yoga_id",
        "name",
        "matched",
        "planets",
        "houses",
        "aspects_used",
        "evidence",
        "trace_id",
    ]
    assert list(career_public) == [
        "summary",
        "score",
        "confidence",
        "components",
        "indicators",
        "evidence",
        "scoring",
        "trace_id",
    ]
    assert (len(yoga_bytes), hashlib.sha256(yoga_bytes).hexdigest()) == (
        1361,
        "d6ad3c317cd8f5388e0630e528238f099910499a2863f9c14aab13e7b5de079e",
    )
    assert (len(career_bytes), hashlib.sha256(career_bytes).hexdigest()) == (
        3495,
        "fee279260217eabb6a0f037d48d306888571fdf4c1c259630eca4337b5df9974",
    )


def test_wp16_tooling_artifact_and_coverage_serialization_contract(tmp_path):
    astro = _astro("golden_chart_01.json")
    first = tmp_path / "first"
    second = tmp_path / "second"
    run_rules_and_trace(astro, first)
    run_rules_and_trace(astro, second)
    expected = {
        "rule_traces.json": (
            35303,
            "35d58eab17166e69e2a81205578bf08908d24d9e517ce88b79d2ec3a92b8fd9d",
        ),
        "career_rule_traces.json": (
            38791,
            "00a67afca63e868354af064a3ad629b655ee662d5c1900119836594c60b8fe88",
        ),
    }
    for name, identity in expected.items():
        first_bytes = (first / name).read_bytes()
        second_bytes = (second / name).read_bytes()
        assert first_bytes == second_bytes
        assert (len(first_bytes), hashlib.sha256(first_bytes).hexdigest()) == identity

    first_coverage = first / "coverage.json"
    second_coverage = second / "coverage.json"
    run_rule_coverage_scan(astro, str(first_coverage))
    run_rule_coverage_scan(astro, str(second_coverage))
    coverage = first_coverage.read_bytes()
    assert coverage == second_coverage.read_bytes()
    assert (len(coverage), hashlib.sha256(coverage).hexdigest()) == (
        727,
        "60c9e72b2d3b0c45056242df2fcf36e2a06d6d2fc98c9b85696173bb573f33ae",
    )

    golden_public = json.dumps(
        interpret_career(astro), ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    assert (len(golden_public), hashlib.sha256(golden_public).hexdigest()) == (
        403,
        "74442a0726173dcac3c521f1e67542443c16c43fbb39e7bded27f9e1601e3be3",
    )
