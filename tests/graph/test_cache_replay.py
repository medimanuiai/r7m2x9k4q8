"""Cache reauthorization and retained-artifact graph reconstruction."""
from dataclasses import replace
import json

import pytest

from systems.Parasara.engine.rules.dsl import RuleDslCompiler
from systems.Parasara.engine.rules.graph import RuleGraphCompiler
from systems.Parasara.engine.rules.canonical import canonical_json_bytes, canonical_json_data
from systems.Parasara.engine.versioning import SelectionPurpose, VersioningError
from tests.graph.conftest import document, dsl_payload
from tests.graph.test_runtime_outcomes import execute
from tests.versioning.conftest import SyntheticCatalogBuilder


@pytest.mark.parametrize("capacity", [0, 1])
def test_disabled_cold_warm_and_format_eviction(graph_pack, tmp_path, capacity):
    _, authority, compiled, _, plan = graph_pack()
    compiler = RuleGraphCompiler(resolved_versions=authority, cache_capacity=capacity)
    cold = compiler.compile_authorized(compiled_rule_set=compiled).plan
    warm = compiler.compile_authorized(compiled_rule_set=compiled).plan
    assert cold is warm is plan
    assert compiler.cache_size == capacity
    path = tmp_path / "synthetic/dependencies.json"
    path.write_text(json.dumps(json.loads(path.read_text()), indent=3), encoding="utf-8")
    assert compiler.compile_authorized(compiled_rule_set=compiled).plan is plan
    assert compiler.cache_size == capacity
    assert canonical_json_bytes(execute(authority, cold)[0].record.to_logical_data()) == canonical_json_bytes(execute(authority, warm)[0].record.to_logical_data())


@pytest.mark.parametrize("changed", ["graph", "dsl", "missing"])
def test_cache_hit_reauthorizes_and_failure_evicts(graph_pack, tmp_path, changed):
    _, _, compiled, compiler, _ = graph_pack()
    assert compiler.cache_size == 1
    if changed == "dsl":
        path = tmp_path / "synthetic/rules.yaml"
        path.write_bytes(path.read_bytes().replace(b"house: 1", b"house: 9"))
    else:
        path = tmp_path / "synthetic/dependencies.json"
        if changed == "missing": path.unlink()
        else:
            data = document(edges=[(0, 1, "requires_matches")])
            path.write_text(json.dumps(data), encoding="utf-8")
    failed = compiler.compile_authorized(compiled_rule_set=compiled)
    assert failed.plan is None and compiler.cache_size == 0


def compile_pack(pack, purpose=None):
    config = replace(pack.config, purpose=purpose) if purpose else pack.config
    authority = pack.resolver.resolve(config)
    compiled = RuleDslCompiler(resolved_versions=authority).compile_authorized(source_id=pack.dsl_source_id).compiled_rule_set
    plan = RuleGraphCompiler(resolved_versions=authority).compile_authorized(compiled_rule_set=compiled).plan
    assert plan is not None
    return authority, plan


def test_two_versions_in_both_orders_and_fresh_replay(tmp_path):
    builder = SyntheticCatalogBuilder(tmp_path)
    packs = [builder.add_graph(source_id=f"synthetic/{v}/rules.yaml", payload=dsl_payload(version=v),
        graph_source_id=f"synthetic/{v}/dependencies.json", graph_payload=json.dumps(document(version=v,
        edges=[(0, 1, kind)])).encode(), allowed_purposes=("NEW_EVALUATION", "REPLAY"))
        for v, kind in (("one", "requires_matches"), ("two", "requires_absence"))]
    def run(pack, purpose=None):
        authority, plan = compile_pack(pack, purpose)
        return canonical_json_bytes(execute(authority, plan)[0].record.to_logical_data())
    forward = [run(p) for p in packs]
    backward = [run(p) for p in reversed(packs)]
    assert forward == list(reversed(backward)) and forward[0] != forward[1]
    assert [run(p, SelectionPurpose.REPLAY) for p in packs] == forward
    (tmp_path / "synthetic/one/dependencies.json").unlink()
    with pytest.raises(VersioningError) as caught:
        compile_pack(packs[0], SelectionPurpose.REPLAY)
    assert caught.value.code.value == "HISTORICAL_CONTENT_UNAVAILABLE"
    assert canonical_json_data(caught.value.details) == {
        "graph_code": "P08E301_UNAUTHORIZED_SOURCE",
        "graph_diagnostic": {
            "code": "P08E301_UNAUTHORIZED_SOURCE",
            "message": "The selected authority does not authorize this graph source.",
            "stage": "source",
            "source_id": "synthetic/one/dependencies.json",
            "field_path": "$",
            "node_source_order": None,
            "prerequisite_source_order": None,
            "details": {},
        },
    }
    assert str(tmp_path) not in str(caught.value.details)


@pytest.mark.parametrize("lifecycle", ["PRODUCTION", "DEPRECATED", "ARCHIVED"])
def test_lifecycle_replay_rollback_and_semantic_identity(tmp_path, lifecycle):
    builder = SyntheticCatalogBuilder(tmp_path)
    common = dict(source_id="synthetic/rules.yaml", payload=dsl_payload(),
        graph_source_id="synthetic/dependencies.json", graph_payload=json.dumps(document()).encode(),
        allowed_purposes=("NEW_EVALUATION", "REPLAY", "ROLLBACK"), rollback_authorized=True,
        astrology_sme_approved=True, astrology_sme_approval_evidence="synthetic-only", replay_available=True)
    initial = builder.add_graph(**common)
    original = compile_pack(initial)[1]
    changed = builder.add_graph(**common, lifecycle=lifecycle, warning="synthetic lifecycle")
    replay = compile_pack(changed, SelectionPurpose.REPLAY)[1]
    assert replay.plan_sha256 == original.plan_sha256
    if lifecycle == "ARCHIVED":
        with pytest.raises(VersioningError): compile_pack(changed, SelectionPurpose.ROLLBACK)
    else:
        assert compile_pack(changed, SelectionPurpose.ROLLBACK)[1].plan_sha256 == original.plan_sha256


def test_one_issued_plan_cannot_be_replaced_by_equivalent_compiled_set(graph_pack):
    pack, authority, _, compiler, plan = graph_pack()
    fresh = RuleDslCompiler(resolved_versions=authority).compile_authorized(source_id=pack.dsl_source_id).compiled_rule_set
    assert fresh is not plan.compiled_rule_set
    assert compiler.compile_authorized(compiled_rule_set=fresh).plan is None
    assert compiler.cache_size == 0 and authority._issued_graph_plan is plan
    with pytest.raises(VersioningError): authority._issue_execution_plan(plan)


def test_hit_reauthorization_invokes_each_authority_check_and_evicts_on_rejection(graph_pack, monkeypatch):
    from systems.Parasara.engine.versioning import VersioningErrorCode
    _, authority, compiled, compiler, _ = graph_pack()
    called = []
    original = type(authority).authorize_graph_analysis
    def refuse(self, analysis):
        called.append(analysis)
        original(self, analysis)
        raise VersioningError(VersioningErrorCode.AUTHORITY_MISMATCH, "Synthetic revoked authority")
    monkeypatch.setattr(type(authority), "authorize_graph_analysis", refuse)
    assert compiler.compile_authorized(compiled_rule_set=compiled).plan is None
    assert called and compiler.cache_size == 0


def test_exact_cache_projection(graph_pack):
    from systems.Parasara.engine.versioning import manifest_to_data
    from systems.Parasara.engine.rules.graph import GRAPH_COMPILER_CONTENT_SHA256, GRAPH_CONTRACT_SHA256
    from systems.Parasara.engine.rules.graph.runtime_contract import digest
    _, authority, compiled, compiler, plan = graph_pack()
    manifest = authority.manifest
    data = manifest_to_data(manifest)
    analysis = plan.graph.analysis
    assert compiler._cache_key(manifest=manifest, analysis=analysis) == (
        manifest.manifest_fingerprint_sha256, analysis.source_raw_sha256, analysis.declarations_sha256,
        compiled.compiled_rule_set_sha256, GRAPH_COMPILER_CONTENT_SHA256, GRAPH_CONTRACT_SHA256,
        digest(data["future_components"]["dsl"]), digest(data["predicate_library"]),
        digest(data["condition_evaluator"]), digest(data["rule_set"]["ordered_source_artifacts"]))
