"""Canonical identity, caching, and unchanged-v1 compatibility."""

from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from systems.Parasara.engine.rules.canonical import canonical_json_bytes, canonical_json_data
from systems.Parasara.engine.rules.dsl import compiler as compiler_module
from systems.Parasara.engine.rules.dsl import (
    AnalysisSucceeded,
    CompilationFailed,
    CompilationSucceeded,
    DSL_COMPILER_CONTENT_SHA256,
    DSL_COMPILER_CONTRACT_DATA,
    DSL_COMPILER_IMPLEMENTATION_MODULE_IDS,
    DSL_RESOURCE_LIMITS,
    RuleDslCompiler,
    compiler_component_fingerprint_sha256,
)
from systems.Parasara.engine.versioning import ResolvedEvaluationVersions, RuleVersionResolver


ROOT = Path(__file__).resolve().parents[2]
V1_MANIFEST_SHA256 = "687c7bb19ce03671882e989db267d588a3c9beace1c42df25390ab643ebae265"
V1_FINGERPRINT = "3e942f97cec7c24079faabc3db358b84177b752a8eb35a7b0d909f84a92d1220"
SNAPSHOT_SHA256 = "da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af"


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def test_line_endings_comments_and_mapping_presentation_do_not_change_semantic_identities(minimal_payload):
    lf = RuleDslCompiler.analyze_source(source_id="synthetic/a.yaml", payload=minimal_payload)
    crlf = RuleDslCompiler.analyze_source(
        source_id="synthetic/a.yaml",
        payload=minimal_payload.replace(b"\n", b"\r\n") + b"# non-semantic\r\n",
    )
    assert isinstance(lf, AnalysisSucceeded) and isinstance(crlf, AnalysisSucceeded)
    assert lf.analyzed_rule_set.source_file_sha256 != crlf.analyzed_rule_set.source_file_sha256
    assert lf.analyzed_rule_set.canonical_dsl_sha256 == crlf.analyzed_rule_set.canonical_dsl_sha256
    assert lf.analyzed_rule_set.compiled_rule_set_sha256 == crlf.analyzed_rule_set.compiled_rule_set_sha256


def test_mapping_order_and_block_flow_presentation_are_semantically_equivalent(minimal_payload):
    original = minimal_payload.decode("utf-8")
    _, rules = original.split("macros: []\n", 1)
    reordered = (
        'system: synthetic\ndsl_version: "1.0.0"\ndsl: parasara-rule-dsl\n'
        'rule_set: {version: fixture-v1, family: prompt07_fixture}\nmacros: []\n'
        + rules
    )
    block = (
        "    when:\n"
        "      predicate:\n"
        "        id: PLANET_IN_HOUSE\n"
        '        version: "1.0.0"\n'
        "        arguments:\n"
        "          planet: Mars\n"
        "          house: 10"
    )
    flow = (
        '    when: {predicate: {arguments: {house: 10, planet: Mars}, '
        'version: "1.0.0", id: PLANET_IN_HOUSE}}'
    )
    variants = (
        RuleDslCompiler.analyze_source(source_id="synthetic/original.yaml", payload=minimal_payload),
        RuleDslCompiler.analyze_source(source_id="synthetic/reordered.yaml", payload=reordered),
        RuleDslCompiler.analyze_source(source_id="synthetic/flow.yaml", payload=original.replace(block, flow)),
    )
    assert all(isinstance(item, AnalysisSucceeded) for item in variants)
    identities = {
        (item.analyzed_rule_set.canonical_dsl_sha256, item.analyzed_rule_set.expanded_ast_sha256,
         item.analyzed_rule_set.compiled_rule_set_sha256)
        for item in variants
    }
    assert len(identities) == 1


def test_published_compiler_fingerprint_binds_modules_contracts_and_limits(tmp_path, monkeypatch):
    dsl_root = ROOT / "systems/Parasara/engine/rules/dsl"
    sources = {
        f"dsl/{name}": (dsl_root / name).read_bytes()
        for name in ("models.py", "parser.py", "compiler.py")
    }
    assert tuple(sources) == DSL_COMPILER_IMPLEMENTATION_MODULE_IDS
    assert compiler_component_fingerprint_sha256(sources) == DSL_COMPILER_CONTENT_SHA256

    changed_source = dict(sources)
    changed_source["dsl/parser.py"] = changed_source["dsl/parser.py"].replace(
        b'if value == "true":', b'if value == "TRUE":', 1
    )
    assert changed_source["dsl/parser.py"] != sources["dsl/parser.py"]
    assert compiler_component_fingerprint_sha256(changed_source) != DSL_COMPILER_CONTENT_SHA256

    for limit_name, value in DSL_RESOURCE_LIMITS.items():
        changed_contract = canonical_json_data(DSL_COMPILER_CONTRACT_DATA)
        changed_contract["resource_limits"][limit_name] = (
            "999999" if isinstance(value, str) else value + 1
        )
        assert (
            compiler_component_fingerprint_sha256(sources, contract_data=changed_contract)
            != DSL_COMPILER_CONTENT_SHA256
        ), limit_name
    assert canonical_json_data(DSL_COMPILER_CONTRACT_DATA)["resource_limits"] == canonical_json_data(
        DSL_RESOURCE_LIMITS
    )

    crlf_sources = {key: value.replace(b"\n", b"\r\n") for key, value in sources.items()}
    monkeypatch.chdir(tmp_path)
    assert compiler_component_fingerprint_sha256(crlf_sources) == DSL_COMPILER_CONTENT_SHA256
    with pytest.raises(ValueError):
        compiler_component_fingerprint_sha256({str((dsl_root / key.split("/")[-1]).resolve()): value for key, value in sources.items()})


def test_compiler_cache_is_instance_local_bounded_and_logically_stable(resolved_dsl_pack):
    compiler = resolved_dsl_pack.compiler
    first = resolved_dsl_pack.compilation
    second = compiler.compile_authorized(source_id=resolved_dsl_pack.pack.dsl_source_id)
    assert isinstance(second, CompilationSucceeded)
    assert second.compiled_rule_set is first.compiled_rule_set
    assert compiler.cache_size == 1 and compiler.cache_capacity == 64

    fresh = RuleDslCompiler(resolved_versions=resolved_dsl_pack.resolved)
    third = fresh.compile_authorized(source_id=resolved_dsl_pack.pack.dsl_source_id)
    assert isinstance(third, CompilationSucceeded)
    assert third.compiled_rule_set is not first.compiled_rule_set
    assert canonical_json_bytes(third.compiled_rule_set.logical_projection()) == canonical_json_bytes(
        first.compiled_rule_set.logical_projection()
    )


def test_cache_key_explicitly_binds_every_component_and_artifact_field(
    resolved_dsl_pack, minimal_payload, monkeypatch
):
    manifest = resolved_dsl_pack.resolved.manifest
    analyzed = RuleDslCompiler.analyze_source(
        source_id=resolved_dsl_pack.pack.dsl_source_id, payload=minimal_payload
    )
    assert isinstance(analyzed, AnalysisSucceeded)
    analyzed_set = analyzed.analyzed_rule_set

    def key(*, manifest_fingerprint=manifest.manifest_fingerprint_sha256,
            analyzed_value=analyzed_set, dsl=manifest.dsl,
            predicate=manifest.predicate_library,
            condition=manifest.condition_evaluator,
            artifacts=manifest.ordered_source_artifacts):
        projected = SimpleNamespace(
            manifest_fingerprint_sha256=manifest_fingerprint,
            dsl=dsl,
            predicate_library=predicate,
            condition_evaluator=condition,
            ordered_source_artifacts=artifacts,
        )
        return RuleDslCompiler._cache_key(manifest=projected, analyzed=analyzed_value)

    baseline = key()
    assert key(manifest_fingerprint="0" * 64) != baseline
    assert key(analyzed_value=replace(analyzed_set, source_file_sha256="0" * 64)) != baseline
    assert key(analyzed_value=replace(analyzed_set, canonical_dsl_sha256="0" * 64)) != baseline
    for contract_name in (
        "DSL_SCHEMA_VERSION",
        "DSL_CANONICALIZATION_CONTRACT",
        "DSL_MACRO_EXPANSION_CONTRACT",
    ):
        with monkeypatch.context() as patch:
            patch.setattr(compiler_module, contract_name, "changed-contract")
            assert key() != baseline
    for field in ("identity", "version", "content_sha256", "compatibility_contract"):
        assert key(dsl=replace(manifest.dsl, **{field: "0" * 64 if field == "content_sha256" else "changed"})) != baseline
        assert key(predicate=replace(manifest.predicate_library, **{field: "0" * 64 if field == "content_sha256" else "changed"})) != baseline
        assert key(condition=replace(manifest.condition_evaluator, **{field: "0" * 64 if field == "content_sha256" else "changed"})) != baseline
    for field in ("artifact_id", "semantic_content_sha256", "expanded_ast_sha256", "compiled_rule_set_sha256"):
        artifact = dict(manifest.ordered_source_artifacts[0])
        artifact[field] = "0" * 64 if field.endswith("sha256") else "changed.artifact"
        assert key(artifacts=(artifact,)) != baseline


def test_cache_hit_repeats_compiled_artifact_authorization(resolved_dsl_pack, monkeypatch):
    authority = resolved_dsl_pack.resolved
    calls = []
    original = ResolvedEvaluationVersions.authorize_compiled_rule_set

    def recording_authorization(self, value):
        calls.append(value)
        return original(self, value)

    monkeypatch.setattr(ResolvedEvaluationVersions, "authorize_compiled_rule_set", recording_authorization)
    compiler = RuleDslCompiler(resolved_versions=authority)
    first = compiler.compile_authorized(source_id=resolved_dsl_pack.pack.dsl_source_id)
    second = compiler.compile_authorized(source_id=resolved_dsl_pack.pack.dsl_source_id)
    assert isinstance(first, CompilationSucceeded) and isinstance(second, CompilationSucceeded)
    assert first.compiled_rule_set is second.compiled_rule_set
    assert calls == [first.compiled_rule_set, first.compiled_rule_set]


def test_cache_hit_fails_closed_when_artifact_reauthorization_fails(resolved_dsl_pack, monkeypatch):
    authority = resolved_dsl_pack.resolved
    calls = 0
    original = ResolvedEvaluationVersions.authorize_compiled_rule_set

    def reject_cached_artifact(self, value):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ValueError("synthetic cache-hit authority rejection")
        return original(self, value)

    monkeypatch.setattr(ResolvedEvaluationVersions, "authorize_compiled_rule_set", reject_cached_artifact)
    compiler = RuleDslCompiler(resolved_versions=authority)
    first = compiler.compile_authorized(source_id=resolved_dsl_pack.pack.dsl_source_id)
    second = compiler.compile_authorized(source_id=resolved_dsl_pack.pack.dsl_source_id)
    assert isinstance(first, CompilationSucceeded)
    assert isinstance(second, CompilationFailed)
    assert tuple(item.code for item in second.diagnostics) == ("P07E404_COMPILED_DIGEST_MISMATCH",)
    assert calls == 2
    assert compiler.cache_size == 0


def test_compiler_cache_evicts_at_exact_sixty_four_entry_bound(resolved_dsl_pack, minimal_payload):
    compiler = RuleDslCompiler(resolved_versions=resolved_dsl_pack.resolved)
    source_path = resolved_dsl_pack.pack.dsl_source_path
    source_id = resolved_dsl_pack.pack.dsl_source_id
    assert source_path is not None and source_id is not None
    first = None
    for index in range(65):
        source_path.write_bytes(minimal_payload + f"\n# cache variant {index}\n".encode("ascii"))
        result = compiler.compile_authorized(source_id=source_id)
        assert isinstance(result, CompilationSucceeded)
        if index == 0:
            first = result.compiled_rule_set
    assert compiler.cache_capacity == 64
    assert compiler.cache_size == 64

    source_path.write_bytes(minimal_payload + b"\n# cache variant 0\n")
    repeated = compiler.compile_authorized(source_id=source_id)
    assert isinstance(repeated, CompilationSucceeded)
    assert repeated.compiled_rule_set is not first
    assert compiler.cache_size == 64


def test_per_rule_digest_binds_complete_resolved_rule_semantics(minimal_payload):
    def compile_rule(payload, *, rule_id=None):
        result = RuleDslCompiler.analyze_source(source_id="synthetic/identity.yaml", payload=payload)
        assert isinstance(result, AnalysisSucceeded)
        if rule_id is None:
            return result.analyzed_rule_set.rules[0]
        return next(item for item in result.analyzed_rule_set.rules if item.resolved_rule.rule_id == rule_id)

    baseline = compile_rule(minimal_payload)
    baseline_digest = baseline.compiled_semantic_sha256
    variants = (
        minimal_payload.replace(b"system: synthetic", b"system: alternate"),
        minimal_payload.replace(b"synthetic.mars_in_tenth", b"synthetic.other_in_tenth"),
        minimal_payload.replace(b'revision: "1.0.0"', b'revision: "1.0.1"', 1),
        minimal_payload.replace(b"version: fixture-v1", b"version: fixture-v2"),
        minimal_payload.replace(b"    family: synthetic", b"    family: alternate"),
        minimal_payload.replace(b"    category: placement", b"    category: alternate"),
        minimal_payload.replace(b"    domains: [synthetic]", b"    domains: [alternate]"),
        minimal_payload.replace(b"    base_weight: 0.25", b"    base_weight: 0.26"),
        minimal_payload.replace(b"    priority: 10", b"    priority: 11"),
        minimal_payload.replace(b"    base_weight: 0.25", b"    base_weight: 0.25\n    quality: 0.5"),
        minimal_payload.replace(b"          house: 10", b"          house: 9"),
    )
    assert all(compile_rule(payload).compiled_semantic_sha256 != baseline_digest for payload in variants)

    resolved_projection = baseline.semantic_contract["dsl_compiled"]["resolved_rule"]
    assert resolved_projection == {
        "system": "synthetic",
        "rule_id": "synthetic.mars_in_tenth",
        "rule_version": "1.0.0",
        "rule_family": "synthetic",
        "rule_set_version": "fixture-v1",
        "category": "placement",
        "domains": ["synthetic"],
        "base_weight": {"$decimal": "0.25"},
        "priority": 10,
        "context": "natal",
        "quality": None,
        "evidence_mode": "predicate_trace_references",
        "evaluation_plan_position": 0,
    }

    text = minimal_payload.decode("utf-8")
    prefix, rule_block = text.split("rules:\n", 1)
    filler = rule_block.replace("synthetic.mars_in_tenth", "synthetic.filler", 1)
    moved = compile_rule(
        (prefix + "rules:\n" + filler + rule_block).encode("utf-8"),
        rule_id="synthetic.mars_in_tenth",
    )
    assert moved.resolved_rule.evaluation_plan_position == 1
    assert moved.compiled_semantic_sha256 != baseline_digest


def test_canonical_decimal_spelling_is_exact_and_float_independent(minimal_payload):
    baseline = RuleDslCompiler.analyze_source(source_id="synthetic/decimal-a.yaml", payload=minimal_payload)
    equivalent = RuleDslCompiler.analyze_source(
        source_id="synthetic/decimal-b.yaml", payload=minimal_payload.replace(b"0.25", b"0.2500")
    )
    assert isinstance(baseline, AnalysisSucceeded) and isinstance(equivalent, AnalysisSucceeded)
    left = baseline.analyzed_rule_set.rules[0]
    right = equivalent.analyzed_rule_set.rules[0]
    assert left.resolved_rule.base_weight == right.resolved_rule.base_weight == 0.25
    assert left.semantic_contract == right.semantic_contract
    assert left.compiled_semantic_sha256 == right.compiled_semantic_sha256
    assert left.semantic_contract["dsl_compiled"]["resolved_rule"]["base_weight"] == {
        "$decimal": "0.25"
    }

    quality_a = RuleDslCompiler.analyze_source(
        source_id="synthetic/quality-a.yaml",
        payload=minimal_payload.replace(b"    context: natal\n", b"    context: natal\n    quality: 0.5\n"),
    )
    quality_b = RuleDslCompiler.analyze_source(
        source_id="synthetic/quality-b.yaml",
        payload=minimal_payload.replace(b"    context: natal\n", b"    context: natal\n    quality: 0.5000\n"),
    )
    assert isinstance(quality_a, AnalysisSucceeded) and isinstance(quality_b, AnalysisSucceeded)
    quality_left = quality_a.analyzed_rule_set.rules[0]
    quality_right = quality_b.analyzed_rule_set.rules[0]
    assert quality_left.semantic_contract == quality_right.semantic_contract
    assert quality_left.compiled_semantic_sha256 == quality_right.compiled_semantic_sha256
    assert quality_left.semantic_contract["dsl_compiled"]["resolved_rule"]["quality"] == {
        "$decimal": "0.5"
    }


def test_current_v1_manifest_catalog_and_snapshot_are_exact():
    manifest_path = ROOT / "systems/Parasara/rules/parashara/v1/rule-set-manifest.json"
    catalog_path = ROOT / "systems/Parasara/config/versioning/parashara_rule_sets_v1.json"
    snapshot = ROOT / "systems/Parasara/tests/snapshots/output_golden_chart_01.json"
    assert digest(manifest_path.read_bytes()) == V1_MANIFEST_SHA256
    assert b'"dsl": null' in manifest_path.read_bytes()
    assert b'"dependency_graph": null' in manifest_path.read_bytes()
    assert V1_FINGERPRINT.encode() in manifest_path.read_bytes()
    assert digest(catalog_path.read_bytes()) == "b4a94e0ff94209bf901e4f74573bb9fb95206116cdf6f9efcda189ccf7135a1a"
    assert len(snapshot.read_bytes()) == 4041 and digest(snapshot.read_bytes()) == SNAPSHOT_SHA256
    resolved = RuleVersionResolver().resolve(__import__(
        "systems.Parasara.engine.versioning", fromlist=["compatibility_v1_config"]
    ).compatibility_v1_config())
    assert resolved.manifest.dsl is None and resolved.manifest.dependency_graph is None
