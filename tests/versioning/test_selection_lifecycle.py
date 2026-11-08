"""Prompt-06 EngineConfig validation and lifecycle/selection-policy tests."""

from __future__ import annotations

import pytest

from systems.Parasara.engine.versioning import (
    EngineConfig,
    EngineMode,
    RuleVersionResolver,
    SelectionPurpose,
    VersioningError,
    VersioningErrorCode,
    compatibility_v1_config,
)

from tests.versioning.conftest import SyntheticCatalogBuilder


def test_compatibility_v1_config_is_literal_and_experimental() -> None:
    config = compatibility_v1_config()
    assert config.system == "parashara"
    assert config.rule_set_family == "parashara"
    assert config.rule_set_version == "v1"
    assert config.mode is EngineMode.EXPERIMENTAL
    assert config.purpose is SelectionPurpose.NEW_EVALUATION


@pytest.mark.parametrize("field_name", ["system", "rule_set_family", "rule_set_version"])
def test_engine_config_rejects_empty_values(field_name: str) -> None:
    kwargs = dict(
        config_schema_version="1.0.0",
        system="parashara",
        engine_version="0.1.0",
        rule_set_family="parashara",
        rule_set_version="v1",
        mode=EngineMode.EXPERIMENTAL,
        purpose=SelectionPurpose.NEW_EVALUATION,
        evaluation_instant="1970-01-01T00:00:00Z",
        output_schema_version="1.0.0",
        compatibility_profile="parasara_snapshot_v1",
    )
    kwargs[field_name] = ""
    with pytest.raises(ValueError):
        EngineConfig(**kwargs)


def test_engine_config_rejects_latest_alias() -> None:
    with pytest.raises(ValueError):
        EngineConfig(
            config_schema_version="1.0.0",
            system="parashara",
            engine_version="0.1.0",
            rule_set_family="parashara",
            rule_set_version="latest",
            mode=EngineMode.EXPERIMENTAL,
            purpose=SelectionPurpose.NEW_EVALUATION,
            evaluation_instant="1970-01-01T00:00:00Z",
            output_schema_version="1.0.0",
            compatibility_profile="parasara_snapshot_v1",
        )


def test_engine_config_rejects_non_iso_utc_evaluation_instant() -> None:
    with pytest.raises(VersioningError) as excinfo:
        EngineConfig(
            config_schema_version="1.0.0",
            system="parashara",
            engine_version="0.1.0",
            rule_set_family="parashara",
            rule_set_version="v1",
            mode=EngineMode.EXPERIMENTAL,
            purpose=SelectionPurpose.NEW_EVALUATION,
            evaluation_instant="not-an-instant",
            output_schema_version="1.0.0",
            compatibility_profile="parasara_snapshot_v1",
        )
    assert excinfo.value.code is VersioningErrorCode.INVALID_VERSIONING_DATA


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("condition_evaluator_identity", "fabricated-condition-evaluator"),
        ("condition_evaluator_version", "99.0.0"),
        ("condition_evaluator_contract", "fabricated-condition-contract@99"),
        ("condition_evaluator_content_sha256", "f" * 64),
    ],
)
def test_condition_evaluator_component_mismatch_is_rejected(
    synthetic_catalog: SyntheticCatalogBuilder,
    field_name: str,
    value: str,
) -> None:
    pack = synthetic_catalog.add(family="fam", version=field_name, **{field_name: value})
    with pytest.raises(VersioningError) as excinfo:
        pack.resolver.resolve(pack.config)
    assert excinfo.value.code is VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION


def test_unknown_rule_set_version_rejected_before_any_evaluation(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(family="fam", version="v1")
    unknown_config = EngineConfig(
        config_schema_version=pack.config.config_schema_version,
        system=pack.config.system,
        engine_version=pack.config.engine_version,
        rule_set_family=pack.config.rule_set_family,
        rule_set_version="does-not-exist",
        mode=pack.config.mode,
        purpose=pack.config.purpose,
        evaluation_instant=pack.config.evaluation_instant,
        output_schema_version=pack.config.output_schema_version,
        compatibility_profile=pack.config.compatibility_profile,
    )
    with pytest.raises(VersioningError) as excinfo:
        pack.resolver.resolve(unknown_config)
    assert excinfo.value.code is VersioningErrorCode.UNKNOWN_RULE_SET_VERSION


def test_archived_selection_rejected_for_new_evaluation(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(
        family="fam",
        version="archived",
        lifecycle="ARCHIVED",
        allowed_modes=("EXPERIMENTAL",),
        allowed_purposes=("NEW_EVALUATION", "REPLAY"),
        warning="archived synthetic pack",
    )
    with pytest.raises(VersioningError) as excinfo:
        pack.resolver.resolve(pack.config)
    assert excinfo.value.code is VersioningErrorCode.LIFECYCLE_SELECTION_FORBIDDEN


def test_unavailable_selection_rejected(synthetic_catalog: SyntheticCatalogBuilder) -> None:
    pack = synthetic_catalog.add(family="fam", version="v1", available=False)
    with pytest.raises(VersioningError) as excinfo:
        pack.resolver.resolve(pack.config)
    assert excinfo.value.code is VersioningErrorCode.RULE_SET_UNAVAILABLE


def test_strict_production_requires_sme_approval(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    unapproved = synthetic_catalog.add(
        family="fam",
        version="prod-unapproved",
        lifecycle="PRODUCTION",
        astrology_sme_approved=False,
        allowed_modes=("STRICT",),
        allowed_purposes=("NEW_EVALUATION",),
        mode=EngineMode.STRICT,
        purpose=SelectionPurpose.NEW_EVALUATION,
    )
    with pytest.raises(VersioningError) as excinfo:
        unapproved.resolver.resolve(unapproved.config)
    assert excinfo.value.code is VersioningErrorCode.LIFECYCLE_SELECTION_FORBIDDEN


def test_strict_production_succeeds_with_recorded_sme_approval(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    approved = synthetic_catalog.add(
        family="fam",
        version="prod-approved",
        lifecycle="PRODUCTION",
        astrology_sme_approved=True,
        astrology_sme_approval_evidence="synthetic-sme-approval-001",
        allowed_modes=("STRICT",),
        allowed_purposes=("NEW_EVALUATION",),
        mode=EngineMode.STRICT,
        purpose=SelectionPurpose.NEW_EVALUATION,
    )
    resolved = approved.resolver.resolve(approved.config)
    assert resolved.lifecycle.value == "PRODUCTION"
    assert resolved.warnings == ()


def test_deprecated_new_evaluation_carries_a_warning(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(
        family="fam",
        version="deprecated",
        lifecycle="DEPRECATED",
        allowed_modes=("EXPERIMENTAL",),
        allowed_purposes=("NEW_EVALUATION", "REPLAY", "ROLLBACK"),
        rollback_authorized=True,
        warning="deprecated synthetic pack",
    )
    resolved = pack.resolver.resolve(pack.config)
    assert resolved.warnings == ("deprecated synthetic pack",)


def test_lifecycle_only_change_leaves_manifest_fingerprint_unchanged(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    validated = synthetic_catalog.add(family="fam", version="v1", lifecycle="VALIDATED")
    deprecated = synthetic_catalog.add(
        family="fam",
        version="v1",
        lifecycle="DEPRECATED",
        allowed_purposes=("NEW_EVALUATION", "REPLAY", "ROLLBACK"),
        rollback_authorized=True,
        warning="now deprecated",
    )
    assert (
        validated.manifest.manifest_fingerprint_sha256
        == deprecated.manifest.manifest_fingerprint_sha256
    )
    resolved = deprecated.resolver.resolve(deprecated.config)
    assert resolved.lifecycle.value == "DEPRECATED"
    assert resolved.warnings == ("now deprecated",)


def test_evaluation_instant_mismatch_against_snapshot_context_is_fatal(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(family="fam", version="v1")

    class _FakeSnapshot:
        evaluation_context = {"instant": "2099-01-01T00:00:00Z"}

    with pytest.raises(VersioningError) as excinfo:
        pack.resolver.resolve(pack.config, snapshot=_FakeSnapshot())
    assert excinfo.value.code is VersioningErrorCode.EVALUATION_INSTANT_MISMATCH
