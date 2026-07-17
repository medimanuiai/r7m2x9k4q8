"""WP13 typed Yoga integration and one-way compatibility contracts."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import fields, replace
import json
from pathlib import Path
from uuid import UUID

import pytest
import yaml

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.enrichments import aspects, functional_roles, varga
from systems.Parasara.engine.enrichments.yoga_engine import (
    DEFAULT_YOGA_RULE_PATH,
    YogaDefinitionDisposition,
    YogaEvaluationBatch,
    YogaEvaluationRecord,
    YogaRuleSource,
    evaluate_yoga_batch,
    evaluate_yoga_rules,
    load_yoga_rule_source,
    prepare_legacy_yoga_state,
    project_yoga_compatibility,
    yoga_batch_full_json_bytes,
    yoga_batch_logical_json_bytes,
    yoga_batch_logical_sha256,
    yoga_batch_from_full_json,
    yoga_batch_from_logical_json,
    yoga_batch_from_preparation_failure,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.definition_validation import validate_yoga_rules
from systems.Parasara.engine.rules.loader import RULE_REGISTRY
from systems.Parasara.engine.rules.models import ConditionResult, PredicateStatus
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    prepared_state_json_bytes,
    prepared_state_sha256,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SURYA_TEST = REPO_ROOT / "systems" / "Parasara" / "fixtures" / "surya_test_chart.json"


def _astro():
    return chart_to_astrostate(SuryaAdapter.load(str(SURYA_TEST)))


def _typed_fixture():
    astro = _astro()
    source = load_yoga_rule_source()
    preparation = prepare_legacy_yoga_state(astro, source)
    assert preparation.outcome.succeeded
    batch = evaluate_yoga_batch(
        preparation.outcome.state,
        PredicateEvaluationContext(),
        source,
        predicate_evaluator=PredicateEvaluator(),
        compatibility_graph=preparation.compatibility_graph,
    )
    return astro, source, preparation, batch


def test_explicit_source_is_stable_strict_ordered_and_registry_independent(monkeypatch, tmp_path):
    before = deepcopy(RULE_REGISTRY)
    monkeypatch.chdir(tmp_path)
    source = load_yoga_rule_source()

    assert DEFAULT_YOGA_RULE_PATH.is_absolute()
    assert [row["id"] for row in source.records] == [
        "rajayoga_naive", "dhana_naive", "arishta_naive"
    ]
    assert [rule.rule_id for rule in source.validation.rules] == [
        "rajayoga_naive", "arishta_naive"
    ]
    issue = source.validation.issues
    assert [(item.code, item.source.rule_id, item.source.rule_index, item.node_path, item.predicate_id) for item in issue] == [
        ("unknown_predicate", "dhana_naive", 1, "condition.root.children.0", "HOUSE_LORDS_COMBINATION")
    ]
    assert RULE_REGISTRY == before


def test_model_field_inventory_and_disposition_values_are_exact():
    assert [item.value for item in YogaDefinitionDisposition] == ["valid", "invalid"]
    assert [item.name for item in fields(YogaEvaluationRecord)] == [
        "yoga_id", "name", "rule_version", "source",
        "definition_disposition", "definition_issues", "condition_result",
        "matched", "status", "trace_reference", "compatibility_evidence",
        "compatibility_houses", "evaluation_time_ms",
    ]
    assert [item.name for item in fields(YogaEvaluationBatch)] == [
        "schema_version", "evaluator_version", "prepared_state_digest",
        "records", "batch_issues", "total_duration_ms",
    ]


def test_legacy_preparation_is_isolated_once_only_and_has_no_varga(monkeypatch):
    astro = _astro()
    source = load_yoga_rule_source()
    before = astro.model_dump(mode="python")
    calls = {"aspects": 0, "roles": 0, "varga": 0}

    real_aspects = aspects.compute_aspect_graph
    real_roles = functional_roles.compute_functional_roles

    def aspect_spy(*args, **kwargs):
        calls["aspects"] += 1
        return real_aspects(*args, **kwargs)

    def role_spy(*args, **kwargs):
        calls["roles"] += 1
        return real_roles(*args, **kwargs)

    monkeypatch.setattr(aspects, "compute_aspect_graph", aspect_spy)
    monkeypatch.setattr(functional_roles, "compute_functional_roles", role_spy)
    monkeypatch.setattr(varga, "integrate_vargas_into_astro", lambda *a, **k: calls.__setitem__("varga", calls["varga"] + 1))

    prepared = prepare_legacy_yoga_state(astro, source)
    assert prepared.outcome.succeeded
    assert calls == {"aspects": 1, "roles": 1, "varga": 0}
    assert astro.model_dump(mode="python") == before
    assert prepared.compatibility_graph is not None


def test_typed_batch_retains_every_row_invalid_error_tree_and_shared_evaluator():
    _, _, _, batch = _typed_fixture()

    assert isinstance(batch, YogaEvaluationBatch)
    assert len(batch.records) == 3
    assert [record.yoga_id for record in batch.records] == [
        "rajayoga_naive", "dhana_naive", "arishta_naive"
    ]
    assert [record.definition_disposition for record in batch.records] == [
        YogaDefinitionDisposition.VALID,
        YogaDefinitionDisposition.INVALID,
        YogaDefinitionDisposition.VALID,
    ]
    assert [record.matched for record in batch.records] == [True, False, False]
    assert [record.status for record in batch.records] == [
        PredicateStatus.MATCHED, PredicateStatus.ERROR, PredicateStatus.UNMATCHED
    ]
    dhana = batch.records[1]
    assert dhana.definition_issues[0].code == "unknown_predicate"
    assert isinstance(dhana.condition_result, ConditionResult)
    first = dhana.condition_result.children[0].result
    assert first is not None and first.status is PredicateStatus.ERROR
    assert first.errors[0].code == "unknown_condition_type"
    assert batch.records[2].condition_result.children[1].result is None
    assert batch.records[2].condition_result.children[1].skip_reason == "and_short_circuit_unmatched"


def test_invalid_unknown_or_leaf_remains_error_but_later_match_is_decisive():
    astro = _astro()
    records = yaml.safe_load(DEFAULT_YOGA_RULE_PATH.read_text(encoding="utf-8"))
    records[1]["conditions"]["children"][1]["params"] = {
        "from_house": 1,
        "to_house": 10,
    }
    source = YogaRuleSource(
        source_name="synthetic-invalid-or.yaml",
        records=tuple(records),
        validation=validate_yoga_rules(records, source_name="synthetic-invalid-or.yaml"),
    )
    preparation = prepare_legacy_yoga_state(astro, source)
    batch = evaluate_yoga_batch(
        preparation.outcome.state,
        PredicateEvaluationContext(),
        source,
        predicate_evaluator=PredicateEvaluator(),
        compatibility_graph=preparation.compatibility_graph,
    )
    dhana = batch.records[1]
    assert dhana.definition_disposition is YogaDefinitionDisposition.INVALID
    assert dhana.definition_issues[0].code == "unknown_predicate"
    assert dhana.status is PredicateStatus.MATCHED and dhana.matched
    assert dhana.condition_result.children[0].result.status is PredicateStatus.ERROR
    assert dhana.condition_result.children[1].result.status is PredicateStatus.MATCHED


def test_logical_and_full_serialization_round_trip_and_telemetry_exclusion():
    _, _, _, batch = _typed_fixture()
    logical = yoga_batch_logical_json_bytes(batch)
    full = yoga_batch_full_json_bytes(batch)
    logical_round_trip = yoga_batch_from_logical_json(logical)
    full_round_trip = yoga_batch_from_full_json(full)

    assert logical_round_trip == batch
    assert full_round_trip == batch
    changed = replace(
        batch,
        total_duration_ms=999.0,
        records=tuple(replace(row, evaluation_time_ms=888.0) for row in batch.records),
    )
    assert changed == batch
    assert yoga_batch_logical_json_bytes(changed) == logical
    assert yoga_batch_logical_sha256(changed) == yoga_batch_logical_sha256(batch)
    assert yoga_batch_full_json_bytes(changed) != full


def test_projection_is_exact_ordered_deterministic_fresh_and_uuid5_shaped():
    _, _, _, batch = _typed_fixture()
    first = project_yoga_compatibility(batch)
    second = project_yoga_compatibility(batch)

    assert first == second
    assert first is not second and first[0] is not second[0]
    assert [list(row) for row in first] == [[
        "yoga_id", "name", "matched", "planets", "houses",
        "aspects_used", "evidence", "trace_id"
    ]] * 3
    assert [row["yoga_id"] for row in first] == [
        "rajayoga_naive", "dhana_naive", "arishta_naive"
    ]
    assert [row["matched"] for row in first] == [True, False, False]
    assert first[0]["planets"] == ["Sun", "Mars"]
    matched_edges = first[0]["evidence"]["children"][0]["matched_edges"]
    assert [edge["source"] for edge in matched_edges] == ["Saturn", "Saturn"]
    assert list(matched_edges[0]) == ["source", "target", "aspect", "kind", "trace"]
    assert list(matched_edges[0]["trace"]) == [
        "source_planet", "source_sign", "source_degree", "offset",
        "target_sign", "matched_planets", "explanation",
    ]
    assert first[1]["evidence"]["children"][0] == {
        "predicate": "HOUSE_LORDS_COMBINATION", "reason": "unknown_predicate"
    }
    assert list(first[1]["evidence"]["children"][0]) == ["reason", "predicate"]
    assert first[2]["evidence"]["children"] == [{}, {"matched_planets": ["Moon", "Saturn"]}]
    assert all(UUID(row["trace_id"]).version == 5 for row in first)

    first[0]["evidence"]["children"].clear()
    assert project_yoga_compatibility(batch)[0]["evidence"]["children"]


def test_public_wrapper_attaches_independent_copy_and_is_repeat_deterministic():
    astro = _astro()
    before = astro.model_dump(mode="python")
    first = evaluate_yoga_rules(astro)
    first_digest = prepared_state_sha256(prepare_legacy_yoga_state(astro, load_yoga_rule_source()).outcome.state)
    second = evaluate_yoga_rules(astro)
    second_digest = prepared_state_sha256(prepare_legacy_yoga_state(astro, load_yoga_rule_source()).outcome.state)

    assert first == second
    assert astro.enrichments["yogas"] == second
    assert astro.enrichments["yogas"] is not second
    assert astro.enrichments["yogas"][0] is not second[0]
    assert first_digest == second_digest
    assert before["planets"] == astro.model_dump(mode="python")["planets"]

    second[0]["planets"].append("Jupiter")
    assert "Jupiter" not in astro.enrichments["yogas"][0]["planets"]


def test_prepared_typed_api_never_mutates_and_cache_warmth_is_logically_neutral():
    astro = _astro()
    source = load_yoga_rule_source()
    preparation = prepare_legacy_yoga_state(astro, source)
    state = preparation.outcome.state
    context = PredicateEvaluationContext()
    evaluator = PredicateEvaluator()
    state_before = prepared_state_json_bytes(state)

    cold = evaluate_yoga_batch(
        state, context, source, predicate_evaluator=evaluator,
        compatibility_graph=preparation.compatibility_graph,
    )
    warm = evaluate_yoga_batch(
        state, context, source, predicate_evaluator=evaluator,
        compatibility_graph=preparation.compatibility_graph,
    )

    assert prepared_state_json_bytes(state) == state_before
    assert cold == warm
    assert yoga_batch_logical_json_bytes(cold) == yoga_batch_logical_json_bytes(warm)
    assert project_yoga_compatibility(cold) == project_yoga_compatibility(warm)
    assert yoga_batch_full_json_bytes(cold) != yoga_batch_full_json_bytes(warm)


def test_public_compatibility_json_is_fully_deterministic():
    astro = _astro()
    one = json.dumps(evaluate_yoga_rules(astro), ensure_ascii=False, separators=(",", ":"))
    two = json.dumps(evaluate_yoga_rules(astro), ensure_ascii=False, separators=(",", ":"))
    assert one == two


def test_public_output_is_independent_of_cwd(monkeypatch, tmp_path):
    expected = evaluate_yoga_rules(_astro())
    monkeypatch.chdir(tmp_path)
    actual = evaluate_yoga_rules(_astro())
    assert actual == expected


def test_duplicate_and_malformed_synthetic_rows_are_retained_as_typed_issues(tmp_path):
    path = tmp_path / "synthetic.yaml"
    payload = """
- id: duplicate
  name: First
  version: 1
  category: test
  conditions: {type: HOUSE_OCCUPANT, params: {planet: Sun, house: 1}}
  weights: {base: 1}
  evidence_required: 1
  provenance: test
  sme_approved: false
  tests: []
- id: duplicate
  name: Second
  version: 1
  category: test
  conditions: {type: HOUSE_OCCUPANT, params: {planet: Moon, house: 2}}
  weights: {base: 1}
  evidence_required: 1
  provenance: test
  sme_approved: false
  tests: []
- not-a-rule
"""
    path.write_text(payload, encoding="utf-8")
    source = load_yoga_rule_source(path.resolve(), source_name="synthetic.yaml")
    assert len(source.records) == 3
    assert [(issue.code, issue.source.rule_index) for issue in source.validation.issues] == [
        ("duplicate_rule_id", 1),
        ("yoga_rule_not_mapping", 2),
    ]


def test_preparation_failure_is_safe_typed_and_preserves_public_rows(monkeypatch):
    import systems.Parasara.engine.enrichments.yoga_engine as yoga_engine

    astro = _astro()
    source = load_yoga_rule_source()
    monkeypatch.setattr(
        aspects,
        "compute_aspect_graph",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("private detail")),
    )
    preparation = prepare_legacy_yoga_state(astro, source)
    assert not preparation.outcome.succeeded
    assert preparation.outcome.issues[0].code == "yoga_aspect_preparation_failed"
    batch = yoga_batch_from_preparation_failure(source, preparation.outcome.issues)
    assert len(batch.records) == 3
    assert all(record.status is PredicateStatus.ERROR for record in batch.records)
    assert batch.batch_issues == preparation.outcome.issues

    rows = yoga_engine.evaluate_yoga_rules(astro)
    assert len(rows) == 3
    assert [row["matched"] for row in rows] == [False, False, False]


def test_active_public_path_never_calls_generic_loader_or_tuple_helpers(monkeypatch):
    import systems.Parasara.engine.enrichments.yoga_engine as yoga_engine
    import systems.Parasara.engine.rules.yoga_loader as yoga_loader

    def forbidden(*args, **kwargs):
        raise AssertionError("legacy path reached")

    monkeypatch.setattr(yoga_loader, "load_yoga_rules", forbidden)
    monkeypatch.setattr(varga, "integrate_vargas_into_astro", forbidden)

    assert all(
        not hasattr(yoga_engine, name)
        for name in (
            "_eval_aspect_condition",
            "_eval_functional_role_condition",
            "_eval_house_lords_combination",
            "_eval_house_occupant",
            "_eval_condition",
        )
    )

    rows = evaluate_yoga_rules(_astro())
    assert [row["matched"] for row in rows] == [True, False, False]
