"""Emit canonical FWP01 scenario bytes, never logs or environment identities."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter, StrictInputError
from systems.Parasara.engine import astrostate_api, normalizer
from systems.Parasara.engine.astrostate_api import thaw_value, require_snapshot, snapshot_logical_bytes
from systems.Parasara.tools import surya_to_parasara as producer
from tests.fwp01.test_input_contract import strict_payload, strict_snapshot


def _issues(error):
    return [dict(path=item.path, code=item.code) for item in error.issues]


def _precision_scenarios():
    # Observe both binary64 neighbors and exact points, using the unchanged
    # Surya enumeration. These are compatibility/precision vectors, not new SME
    # astrology oracles. Every nakshatra/pada transition is included.
    boundaries = [30.0 * i for i in range(1, 13)]
    boundaries += [(360.0 / 27.0) * i / 4.0 for i in range(1, 108)]
    values = {0.0, math.nextafter(0.0, math.inf), 29.99996, 13.33334, 3.33334, 359.99996}
    for boundary in boundaries:
        values.update((math.nextafter(boundary, 0.0), boundary, math.nextafter(boundary, math.inf)))
    rows = []
    for value in sorted(values):
        planet = producer.build_planet_record("Sun", value, 35.25, retrograde=False, precision="strict_factual")
        lagna = producer.build_lagna_record(value, precision="strict_factual")
        model = SuryaAdapter.from_mapping_strict(strict_payload(value, [value, 41, 89, 105, 169, 211, 279, 319, 139]))
        source = value % 360.0
        assert planet["sidereal_longitude"] == lagna["sidereal_longitude"] == source
        assert planet["degree"] == lagna["degree"] == source - 30.0 * int(source // 30.0)
        legacy = producer.build_lagna_record(value)
        assert legacy == producer.build_lagna_record(value, precision="legacy_v1")
        rows.append(dict(source=value, planet=planet, lagna=lagna, legacy_lagna=legacy,
                         validated_lagna=model.lagna, validated_planet=model.planets[0]))
    invalid_sources = []
    for label, value in (("boolean", True), ("nan", float("nan")), ("infinity", float("inf")),
                         ("unrepresentable", 10 ** 5000), ("negative_subnormal", math.nextafter(0.0, -math.inf))):
        try:
            producer.build_lagna_record(value, precision="strict_factual")
        except ValueError as error:
            assert str(error) == "invalid_source_longitude"
            invalid_sources.append(dict(scenario=label, code="invalid_source_longitude"))
        else:
            raise AssertionError("invalid producer source accepted")
    return dict(transitions=rows, invalid_sources=invalid_sources)


def _batch_rows(batch):
    return [dict(index=row.index, issues=[dict(path=x.path, code=x.code) for x in row.issues],
                 digest=None if row.chart is None else require_snapshot(normalizer.build_strict_snapshot(row.chart)).logical_digest)
            for row in batch.records]


def _routing_scenarios(synthetic):
    valid = strict_payload()
    invalid = deepcopy(valid)
    invalid["planets"][0]["degree"] = 30
    records = [valid, invalid, valid]
    with patch.object(SuryaAdapter, "load", side_effect=AssertionError("legacy loader fallback")), \
         patch.object(normalizer, "chart_to_astrostate", side_effect=AssertionError("legacy construction fallback")):
        batch = _batch_rows(SuryaAdapter.from_mappings_strict(records))
        try:
            SuryaAdapter.from_mapping_strict(invalid)
        except StrictInputError as error:
            assert batch[1]["issues"] == _issues(error)
        else:
            raise AssertionError("strict failure became compatibility success")
        corrupted = SuryaAdapter.from_mapping_strict(valid)
        corrupted.planets[0]["degree"] = 30
        assert isinstance(normalizer.build_strict_snapshot(corrupted), astrostate_api.AstroStateBuildFailure)
        strict_generated = producer.generate_chart(12.9716, 77.5946,
            datetime(2001, 2, 3, 8, 55, tzinfo=timezone.utc),
            330, precision="strict_factual")
        generated_digest = strict_snapshot(strict_generated).logical_digest
    golden_path = ROOT / "systems/Parasara/fixtures/golden_chart_01.json"
    legacy = SuryaAdapter.load(str(golden_path))
    legacy_state = require_snapshot(astrostate_api.freeze_astrostate(normalizer.chart_to_astrostate(legacy)))
    try:
        SuryaAdapter.load_strict(str(golden_path))
    except StrictInputError as error:
        legacy_strict_errors = _issues(error)
    else:
        raise AssertionError("partial legacy chart accepted as strict")
    from systems.Parasara.tools.runner_api import _legacy_engine_chart
    with tempfile.TemporaryDirectory(prefix="fwp01-routing-") as temporary:
        single_path = Path(temporary) / "single.json"
        batch_path = Path(temporary) / "batch.json"
        single_path.write_text(json.dumps(valid), encoding="utf-8")
        assert SuryaAdapter.load_strict(str(single_path)) == SuryaAdapter.from_mapping_strict(valid)
        batch_path.write_text(json.dumps(records), encoding="utf-8")
        assert _batch_rows(SuryaAdapter.load_many_strict(str(batch_path))) == batch
        batch_path.write_text(json.dumps([{"input": json.loads(golden_path.read_text(encoding="utf-8"))}]), encoding="utf-8")
        assert len(SuryaAdapter.load_many(str(batch_path))[0].planets) == 3
        single_path.write_text(json.dumps(_legacy_engine_chart(synthetic)), encoding="utf-8")
        mvp = require_snapshot(astrostate_api.freeze_astrostate(normalizer.chart_to_astrostate(SuryaAdapter.load(str(single_path)))))
    return dict(strict_batch=batch, legacy_planets=len(legacy.planets), legacy_houses=len(legacy.houses),
                legacy_digest=legacy_state.logical_digest, legacy_strict_issues=legacy_strict_errors,
                legacy_mvp_digest=mvp.logical_digest, generated_strict_digest=generated_digest,
                strict_failure_did_not_fallback=True, file_mapping_results_equal=True)


def _mutation_and_projection_scenarios():
    from systems.Parasara.engine.rules.snapshot_adapter import prepare_predicate_snapshot
    from systems.Parasara.engine.rules.canonical_predicates import evaluate_aspect_exists
    from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext
    data = strict_payload(0, [10, 95, 1, 61, 120, 180, 240, 300, 150])
    expected = strict_snapshot(data).logical_digest
    model = SuryaAdapter.from_mapping_strict(data)
    data["planets"][0]["degree"] = 30
    state = require_snapshot(normalizer.build_strict_snapshot(model))
    model.planets[0]["motion"]["retrograde"] = True
    assert state.logical_digest == expected
    astro = normalizer.chart_to_astrostate_strict(SuryaAdapter.from_mapping_strict(
        strict_payload(0, [10, 95, 1, 61, 120, 180, 240, 300, 150])))
    shared = require_snapshot(astrostate_api.freeze_astrostate(astro))
    shared_bytes = snapshot_logical_bytes(shared)
    astro.enrichments["aspects"]["edges"].clear()
    astro.houses[0]["occupants"].append("Moon")
    astro.metadata["factual_sources"]["planets"]["Sun"]["motion"]["value"]["retrograde"] = True
    assert snapshot_logical_bytes(shared) == shared_bytes
    immutable_rejected = []
    for label, target, key in (("metadata", state.core.metadata, "factual_sources"),
                               ("graph", state.get_aspect_representation("whole_sign_graph").value, "edges")):
        try:
            target[key] = None
        except TypeError:
            immutable_rejected.append(label)
        else:
            raise AssertionError("published data was mutable")
    with patch.object(astrostate_api, "freeze_astrostate", side_effect=AssertionError("projection refroze state")):
        prepared = prepare_predicate_snapshot(state).state
        predicates = [dict(filters=filters, status=evaluate_aspect_exists(
            filters, prepared, PredicateEvaluationContext()).status.value)
            for filters in ({"from_planet": "Mars", "to_planet": "Moon"},
                            {"from_planet": "Rahu"}, {"from_planet": "Ketu"})]
    assert all(row["status"] == "missing_capability" for row in predicates)
    assert any(row.target_id == "Moon" for row in state.get_aspects_from("Mars", "whole_sign_graph").value)
    node_queries = [dict(planet=name, state=shared.get_aspects_from(name, "whole_sign_graph").state.value)
                    for name in ("Rahu", "Ketu")]
    assert all(row["state"] == "unsupported_capability" for row in node_queries)
    return dict(digest=expected, shared_digest=shared.logical_digest, mutable_input_isolated=True,
                immutable_rejected=immutable_rejected, node_queries=node_queries, predicates=predicates,
                predicate_contract_conflict=True, supported_mars_fact_preserved_in_general_snapshot=True)


def scenario_bytes():
    states = []
    for index in range(12):
        state = strict_snapshot(strict_payload(index * 30.0))
        states.append(dict(lagna=state.get_lagna().value, digest=state.logical_digest,
            houses=[thaw_value(state.get_house_summary(i).value) for i in range(1, 13)],
            capabilities=[dict(id=cap.capability_id, version=cap.capability_version,
                readiness=cap.readiness.value, issues=cap.issues) for cap in state.capabilities]))
    errors = []
    for label in ("degree_30", "missing_longitude", "duplicate", "partial_houses", "pada",
                  "missing_body", "wrong_house", "negative_degree", "longitude_360", "boolean_degree",
                  "non_finite", "huge_degree", "huge_ayanamsa", "surrogate"):
        data = strict_payload()
        if label == "degree_30": data["planets"][0]["degree"] = 30
        elif label == "missing_longitude": data["planets"][0].pop("sidereal_longitude")
        elif label == "duplicate": data["planets"][0]["name"] = "Moon"
        elif label == "partial_houses": data["houses"] = [dict(number=1, sign="Taurus")]
        elif label == "pada": data["planets"][0]["nakshatra"]["pada"] = 4
        elif label == "missing_body": data["planets"].pop()
        elif label == "wrong_house": data["planets"][0]["house"] = 1
        elif label == "negative_degree": data["planets"][0]["degree"] = -1
        elif label == "longitude_360": data["planets"][0]["sidereal_longitude"] = 360
        elif label == "boolean_degree": data["planets"][0]["degree"] = True
        elif label == "non_finite": data["planets"][0]["degree"] = float("inf")
        elif label == "huge_degree": data["planets"][0]["degree"] = 10 ** 5000
        elif label == "huge_ayanamsa": data["metadata"]["ayanamsa_degrees"] = 10 ** 5000
        else: data["metadata"]["birth_location"]["place_label"] = "\ud800"
        try:
            SuryaAdapter.from_mapping_strict(data)
        except StrictInputError as exc:
            errors.append(dict(scenario=label, issues=_issues(exc)))
            batch = SuryaAdapter.from_mappings_strict([strict_payload(), data, strict_payload()])
            assert batch.records[1].issues == exc.issues and len(batch.charts) == 2
        else:
            raise AssertionError("negative scenario succeeded")
    alias = strict_payload()
    alias["planets"][-1]["name"] = "Kethu"
    assert strict_snapshot(alias).logical_digest == strict_snapshot().logical_digest
    golden = ROOT / "systems/Parasara/tests/snapshots/output_golden_chart_01.json"
    from systems.Parasara.tools.surya_to_parasara import generate_chart
    synthetic = generate_chart(12.9716, 77.5946, datetime(2001, 2, 3, 8, 55, tzinfo=timezone.utc),
        330, timezone_name="Asia/Kolkata", place_label="Synthetic sample")
    synthetic_bytes = json.dumps(synthetic, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    value = dict(contract="fwp01.scenarios@1.0.0", states=states, errors=errors,
        precision=_precision_scenarios(), routing=_routing_scenarios(synthetic),
        mutation_and_projection=_mutation_and_projection_scenarios(),
        protected_snapshot_sha256=hashlib.sha256(golden.read_bytes()).hexdigest(),
        synthetic_mvp_sha256=hashlib.sha256(synthetic_bytes).hexdigest())
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def scenario_bytes_v2():
    """Separate V2 oracle; the original scenario function and bytes stay exact."""
    from tests.fwp01.test_aspect_contract_v2 import resolve_v2, v2_snapshot, SOURCE, without_placements, expanded_depth_payload, edge_consistency_outcome
    from systems.Parasara.engine.rules.aspect_contract_v2 import state_canonical_bytes_v2, state_sha256_v2
    from systems.Parasara.engine.rules.snapshot_adapter import prepare_predicate_snapshot_v2
    from systems.Parasara.engine.rules.evaluator_v2 import PredicateEvaluatorV2, ConditionEvaluatorV2
    from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext
    from systems.Parasara.engine.rules.dsl.compiler_v2 import RuleDslCompilerV2
    from systems.Parasara.engine.rules.rule_engine import RuleEngine
    from systems.Parasara.engine.rules.canonical import canonical_json_bytes
    authority, snapshot = resolve_v2(), v2_snapshot()
    state = prepare_predicate_snapshot_v2(snapshot, resolved_versions=authority).state
    evaluator, context = PredicateEvaluatorV2(resolved_versions=authority), PredicateEvaluationContext()
    cases = ({"from_planet": "Mars", "to_planet": "Moon"}, {"from_planet": "Sun", "to_planet": "Sun"},
        {"from_planet": "Rahu", "from_house": 1}, {"from_planet": "Ketu"}, {"to_planet": "Moon"},
        {"to_house": 12}, {"from_house": 2}, {"from_house": 11, "to_planet": "Moon"},
        {"from_planet": "Mars", "from_house": 1, "to_house": 4}, {"to_house": False})
    def project(result):
        return dict(status=result.status.value, matched=result.matched,
            errors=[dict(code=e.code, details=e.details) for e in result.errors],
            evidence=getattr(result, "evidence", getattr(result, "details", {})))
    rows = []
    for filters in cases:
        cold = evaluator.evaluate("ASPECT", filters, state, context)
        warm = evaluator.evaluate("ASPECT_EXISTS", filters, state, context)
        assert cold == warm
        rows.append(dict(filters=filters, result=project(cold), warm_cache_hit=warm.cache_hit))
    logical = ConditionEvaluatorV2(evaluator).evaluate(dict(type="NOT", children=[
        dict(type="ASPECT_EXISTS", params=dict(from_planet="Rahu"))]), state, context)
    missing = evaluator.evaluate("ASPECT", dict(from_planet="Mars", from_house=1), without_placements(state), context)
    compiled = RuleDslCompilerV2(resolved_versions=authority).compile_authorized(source_id=SOURCE).compiled_rule_set
    depth_result = RuleDslCompilerV2.analyze_source(source_id=SOURCE, payload=expanded_depth_payload(24))
    assert depth_result.diagnostics[0].code == "P07E404_COMPILED_DIGEST_MISMATCH"
    engine = RuleEngine(resolved_versions=authority)
    matches = [engine.evaluate_compiled_rule(rule, condition_evaluator=ConditionEvaluatorV2(evaluator),
        state=state, context=context, evaluation_snapshot_digest=snapshot.logical_digest, evaluation_context={})
        for rule in compiled.rules]
    consistency = []
    def rule_status(prepared, source_snapshot):
        result = engine.evaluate_compiled_rule(compiled.rules[0], condition_evaluator=ConditionEvaluatorV2(evaluator),
            state=prepared, context=context, evaluation_snapshot_digest=source_snapshot.logical_digest, evaluation_context={})
        return dict(status=result.status.value, errors=[e.code for e in result.errors])
    for route in ("preparation", "deserialization"):
        clean_snapshot, clean = edge_consistency_outcome(authority, route)
        row = dict(route=route, clean_rule=rule_status(clean.state, clean_snapshot))
        for mutation in ("forged_target", "unauthorized_offset"):
            source_snapshot, outcome = edge_consistency_outcome(authority, route, mutation=mutation)
            row[mutation] = dict(readiness=outcome.state.graph.readiness.value, issues=outcome.state.graph.issues,
                rule=rule_status(outcome.state, source_snapshot))
        _, wrapped = edge_consistency_outcome(authority, route, wrap=True)
        row["wraparound"] = [project(evaluator.evaluate("ASPECT", dict(from_planet="Mars", to_planet=target, to_house=house),
            wrapped.state, context)) for target, house in (("Sun", 10), ("Moon", 1))]
        consistency.append(row)
    return canonical_json_bytes(dict(contract="fwp01.scenarios@2.0.0", prepared_sha256=state_sha256_v2(state),
        manifest_sha256=authority.manifest_fingerprint_sha256, compiled_sha256=compiled.compiled_rule_set_sha256,
        cases=rows, unsupported_not=project(logical), missing_placement=project(missing),
        expanded_depth_diagnostic=depth_result.diagnostics[0].code,
        edge_consistency=consistency,
        rule_matches=[dict(rule_id=m.rule_id, status=m.status.value, errors=[e.code for e in m.errors]) for m in matches]))


if __name__ == "__main__":
    sys.stdout.buffer.write(scenario_bytes_v2() if sys.argv[1:] == ["--v2"] else scenario_bytes())
