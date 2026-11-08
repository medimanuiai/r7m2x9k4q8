"""Prompt-06 canonical manifest content, fingerprint, and comparison tests."""

from __future__ import annotations

import pytest

from systems.Parasara.engine.versioning import (
    DEFAULT_RULE_SET_CATALOG,
    RuleVersionResolver,
    VersioningError,
    VersioningErrorCode,
    compare_manifests,
    compatibility_v1_config,
    manifest_canonical_json_bytes,
    manifest_fingerprint_sha256,
    manifest_from_data,
    manifest_to_data,
)
from systems.Parasara.engine.rules.canonical import canonical_json_data
from systems.Parasara.engine.rules.dsl import DSL_COMPILER_IDENTITY

from tests.versioning.conftest import SyntheticCatalogBuilder, build_rule_revision


def test_v1_manifest_resolves_and_fingerprint_is_deterministic() -> None:
    resolved = RuleVersionResolver().resolve(compatibility_v1_config())
    manifest = resolved.manifest
    assert resolved.manifest_fingerprint_sha256 == manifest_fingerprint_sha256(manifest)
    # Recomputing from the manifest's own canonical bytes reproduces the identical digest.
    roundtrip = manifest_from_data(manifest_to_data(manifest))
    assert roundtrip.manifest_fingerprint_sha256 == manifest.manifest_fingerprint_sha256
    assert manifest_canonical_json_bytes(roundtrip) == manifest_canonical_json_bytes(manifest)


def test_v1_catalog_lifecycle_is_validated_and_not_sme_approved() -> None:
    resolved = RuleVersionResolver().resolve(compatibility_v1_config())
    assert resolved.lifecycle.value == "VALIDATED"
    assert resolved.catalog_entry["astrology_sme_approved"] is False


def test_fingerprint_excludes_itself_and_changes_with_content(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    base = synthetic_catalog.add(family="fam", version="base")
    changed = synthetic_catalog.add(
        family="fam",
        version="changed",
        rule_revisions=(build_rule_revision(rule_id="synthetic_rule_a"),),
    )
    assert base.manifest.manifest_fingerprint_sha256 != changed.manifest.manifest_fingerprint_sha256
    # The fingerprint field itself never contributes to its own hashed payload.
    logical = manifest_to_data(base.manifest, include_fingerprint=False)
    assert "manifest_fingerprint_sha256" not in logical


def test_manifest_digest_mismatch_is_fatal_before_evaluation(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(family="fam", version="tampered", tamper_manifest_after_write=True)
    with pytest.raises(VersioningError) as excinfo:
        pack.resolver.resolve(pack.config)
    assert excinfo.value.code is VersioningErrorCode.MANIFEST_DIGEST_MISMATCH


def test_compare_manifests_reports_added_removed_changed_and_reordered_rules(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    rule_a = build_rule_revision(rule_id="synthetic_rule_a", source_order=0)
    rule_b = build_rule_revision(rule_id="synthetic_rule_b", source_order=1)
    rule_a_changed = build_rule_revision(
        rule_id="synthetic_rule_a",
        source_order=0,
        semantic_contract={"note": "synthetic-non-astrology-rule-changed"},
    )
    old = synthetic_catalog.add(family="fam", version="old", rule_revisions=(rule_a, rule_b))
    new = synthetic_catalog.add(
        family="fam", version="new", rule_revisions=(rule_a_changed,)
    )
    diff = compare_manifests(old.manifest, new.manifest)
    assert canonical_json_data(diff["removed_rules"]) == [
        {"rule_id": "synthetic_rule_b", "revision": "1"}
    ]
    assert canonical_json_data(diff["changed_rules"]) == [
        {"rule_id": "synthetic_rule_a", "revision": "1"}
    ]
    assert canonical_json_data(diff["added_rules"]) == []
    assert diff["rule_order_changed"] is True
    assert diff["old_manifest_fingerprint_sha256"] == old.manifest.manifest_fingerprint_sha256
    assert diff["new_manifest_fingerprint_sha256"] == new.manifest.manifest_fingerprint_sha256
    # compare_manifests is a pure diagnostic: it never mutates or re-validates content.
    same = compare_manifests(old.manifest, old.manifest)
    assert canonical_json_data(same["added_rules"]) == []
    assert canonical_json_data(same["removed_rules"]) == []
    assert canonical_json_data(same["changed_rules"]) == []
    assert same["rule_order_changed"] is False


def test_default_catalog_path_is_module_root_anchored() -> None:
    assert DEFAULT_RULE_SET_CATALOG.is_file()
    assert DEFAULT_RULE_SET_CATALOG.name == "parashara_rule_sets_v1.json"


def test_rule_identity_for_rejects_unauthorized_rule(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(
        family="fam",
        version="v1",
        rule_revisions=(build_rule_revision(rule_id="synthetic_rule_a"),),
    )

    class _Fake:
        rule_id = "synthetic_rule_unknown"
        rule_version = "1"

    with pytest.raises(VersioningError) as excinfo:
        pack.manifest.rule_identity_for(_Fake())
    assert excinfo.value.code is VersioningErrorCode.RULE_NOT_IN_MANIFEST


def test_synthetic_dsl_manifest_roundtrips_with_exact_component_and_artifact_digests(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    from pathlib import Path

    payload = (Path(__file__).resolve().parents[1] / "dsl/fixtures/minimal.yaml").read_bytes()
    pack = synthetic_catalog.add_dsl(
        source_id="synthetic/prompt07_fixture/fixture-v1/rules.yaml",
        payload=payload,
    )
    resolved = pack.resolver.resolve(pack.config)
    assert resolved.manifest.dsl is not None
    assert resolved.manifest.dsl.identity == DSL_COMPILER_IDENTITY
    artifact = resolved.manifest.ordered_source_artifacts[0]
    assert artifact["format"] == "rule-dsl-yaml"
    assert len(artifact["semantic_content_sha256"]) == 64
    assert len(artifact["expanded_ast_sha256"]) == 64
    assert len(artifact["compiled_rule_set_sha256"]) == 64
    roundtrip = manifest_from_data(manifest_to_data(resolved.manifest))
    assert manifest_canonical_json_bytes(roundtrip) == manifest_canonical_json_bytes(resolved.manifest)


def test_unsupported_non_null_dependency_graph_remains_rejected(synthetic_catalog: SyntheticCatalogBuilder) -> None:
    pack = synthetic_catalog.add(family="fam", version="v1")
    data = manifest_to_data(pack.manifest)
    data["future_components"]["dependency_graph"] = data["engine"]
    with pytest.raises(ValueError):
        manifest_from_data(data)
def test_supported_synthetic_graph_component_roundtrips(tmp_path):
    import json
    from tests.graph.conftest import document, dsl_payload
    builder = SyntheticCatalogBuilder(tmp_path)
    pack = builder.add_graph(source_id="synthetic/rules.yaml", payload=dsl_payload(),
        graph_source_id="synthetic/dependencies.json", graph_payload=json.dumps(document()).encode())
    restored = manifest_from_data(manifest_to_data(pack.manifest))
    assert restored.dependency_graph == pack.manifest.dependency_graph
    assert restored.dsl is not None
    assert pack.resolver.resolve(pack.config).manifest == restored
