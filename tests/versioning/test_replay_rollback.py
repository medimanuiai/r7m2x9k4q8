"""Prompt-06 deterministic replay and rollback-policy tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.astrostate_api import AstroStateBuildSuccess, freeze_astrostate
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules.canonical import canonical_json_data
from systems.Parasara.engine.versioning import (
    EngineMode,
    SelectionPurpose,
    VersioningError,
    VersioningErrorCode,
)
from systems.Parasara.tools.generate_snapshot import (
    assemble_snapshot_output,
    evaluate_snapshot_record,
    replay_evaluation,
)

from tests.versioning.conftest import SyntheticCatalogBuilder


ROOT = Path(__file__).resolve().parents[2]


def _snapshot():
    chart = SuryaAdapter.load(
        str(ROOT / "systems" / "Parasara" / "fixtures" / "golden_chart_01.json")
    )
    build = freeze_astrostate(chart_to_astrostate(chart))
    assert isinstance(build, AstroStateBuildSuccess)
    return build.snapshot


def test_canonical_evaluation_creates_record_and_fresh_replay_matches_digest() -> None:
    snapshot = _snapshot()
    record = evaluate_snapshot_record(snapshot)
    replayed = replay_evaluation(record)
    assert record.snapshot is snapshot
    assert record.domain_results
    assert record.rule_match_trace_ids
    assert record.output_sha256 == replayed.output_sha256
    assert replayed.resolved_versions is not record.resolved_versions
    assert replayed.replay_of_manifest_sha256 == (
        record.resolved_versions.manifest_fingerprint_sha256
    )
    assert assemble_snapshot_output(snapshot) == canonical_json_data(record.public_output)


@pytest.mark.parametrize(
    "code",
    [
        VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
        VersioningErrorCode.HISTORICAL_CONTENT_UNAVAILABLE,
    ],
)
def test_replay_rejects_altered_or_missing_historical_content_without_fallback(code) -> None:
    record = evaluate_snapshot_record(_snapshot())

    class RejectingHistoricalResolver:
        def resolve(self, config, *, snapshot=None):
            assert config.rule_set_version == record.resolved_versions.config.rule_set_version
            assert config.evaluation_instant == record.evaluation_instant
            assert config.purpose is SelectionPurpose.REPLAY
            raise VersioningError(code, "synthetic historical-content failure")

    with pytest.raises(VersioningError) as excinfo:
        replay_evaluation(record, resolver=RejectingHistoricalResolver())
    assert excinfo.value.code is code


def test_replay_of_retained_production_content_succeeds(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(
        family="fam",
        version="prod",
        lifecycle="PRODUCTION",
        astrology_sme_approved=True,
        astrology_sme_approval_evidence="synthetic-sme-001",
        allowed_modes=("EXPERIMENTAL",),
        allowed_purposes=("NEW_EVALUATION", "REPLAY"),
        purpose=SelectionPurpose.REPLAY,
    )
    resolved = pack.resolver.resolve(pack.config)
    assert resolved.lifecycle.value == "PRODUCTION"


def test_replay_of_deprecated_and_archived_content_succeeds(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    deprecated = synthetic_catalog.add(
        family="fam",
        version="deprecated",
        lifecycle="DEPRECATED",
        allowed_modes=("EXPERIMENTAL",),
        allowed_purposes=("NEW_EVALUATION", "REPLAY", "ROLLBACK"),
        rollback_authorized=True,
        replay_available=True,
        purpose=SelectionPurpose.REPLAY,
        warning="deprecated synthetic pack",
    )
    archived = synthetic_catalog.add(
        family="fam",
        version="archived",
        lifecycle="ARCHIVED",
        allowed_modes=("EXPERIMENTAL",),
        allowed_purposes=("REPLAY",),
        replay_available=True,
        purpose=SelectionPurpose.REPLAY,
        warning="archived synthetic pack",
    )
    assert deprecated.resolver.resolve(deprecated.config).lifecycle.value == "DEPRECATED"
    assert archived.resolver.resolve(archived.config).lifecycle.value == "ARCHIVED"


def test_replay_fails_when_historical_content_is_not_replayable(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(
        family="fam",
        version="not-replayable",
        lifecycle="DEPRECATED",
        allowed_modes=("EXPERIMENTAL",),
        allowed_purposes=("NEW_EVALUATION", "REPLAY"),
        replay_available=False,
        purpose=SelectionPurpose.REPLAY,
        warning="not replayable",
    )
    with pytest.raises(VersioningError) as excinfo:
        pack.resolver.resolve(pack.config)
    assert excinfo.value.code is VersioningErrorCode.HISTORICAL_CONTENT_UNAVAILABLE


def test_replay_fails_for_missing_manifest_file(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(
        family="fam",
        version="missing-content",
        lifecycle="ARCHIVED",
        allowed_modes=("EXPERIMENTAL",),
        allowed_purposes=("REPLAY",),
        replay_available=True,
        purpose=SelectionPurpose.REPLAY,
        warning="archived synthetic pack",
    )
    (pack.resolver._repository_root / pack.manifest_relative_path).unlink()
    with pytest.raises(VersioningError) as excinfo:
        pack.resolver.resolve(pack.config)
    assert excinfo.value.code is VersioningErrorCode.HISTORICAL_CONTENT_UNAVAILABLE


def test_rollback_succeeds_for_an_exact_production_target(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(
        family="fam",
        version="prod",
        lifecycle="PRODUCTION",
        astrology_sme_approved=True,
        astrology_sme_approval_evidence="synthetic-sme-001",
        allowed_modes=("EXPERIMENTAL",),
        allowed_purposes=("NEW_EVALUATION", "ROLLBACK"),
        rollback_authorized=True,
        purpose=SelectionPurpose.ROLLBACK,
    )
    resolved = pack.resolver.resolve(pack.config)
    assert resolved.lifecycle.value == "PRODUCTION"


def test_rollback_to_deprecated_requires_rollback_purpose_and_authorization(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    authorized = synthetic_catalog.add(
        family="fam",
        version="deprecated-authorized",
        lifecycle="DEPRECATED",
        allowed_modes=("EXPERIMENTAL",),
        allowed_purposes=("NEW_EVALUATION", "ROLLBACK"),
        rollback_authorized=True,
        purpose=SelectionPurpose.ROLLBACK,
        warning="rollback to deprecated content",
    )
    resolved = authorized.resolver.resolve(authorized.config)
    assert resolved.warnings == ("rollback to deprecated content",)

    unauthorized = synthetic_catalog.add(
        family="fam",
        version="deprecated-unauthorized",
        lifecycle="DEPRECATED",
        allowed_modes=("EXPERIMENTAL",),
        allowed_purposes=("NEW_EVALUATION", "ROLLBACK"),
        rollback_authorized=False,
        purpose=SelectionPurpose.ROLLBACK,
        warning="rollback target not authorized",
    )
    with pytest.raises(VersioningError) as excinfo:
        unauthorized.resolver.resolve(unauthorized.config)
    assert excinfo.value.code is VersioningErrorCode.LIFECYCLE_SELECTION_FORBIDDEN


def test_rollback_to_archived_or_unapproved_target_is_rejected(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    archived = synthetic_catalog.add(
        family="fam",
        version="archived",
        lifecycle="ARCHIVED",
        allowed_modes=("EXPERIMENTAL",),
        allowed_purposes=("ROLLBACK",),
        rollback_authorized=True,
        purpose=SelectionPurpose.ROLLBACK,
        warning="archived synthetic pack",
    )
    with pytest.raises(VersioningError) as excinfo:
        archived.resolver.resolve(archived.config)
    assert excinfo.value.code is VersioningErrorCode.LIFECYCLE_SELECTION_FORBIDDEN

    validated = synthetic_catalog.add(
        family="fam",
        version="validated-not-rollback-target",
        lifecycle="VALIDATED",
        allowed_modes=("EXPERIMENTAL",),
        allowed_purposes=("NEW_EVALUATION", "ROLLBACK"),
        rollback_authorized=True,
        purpose=SelectionPurpose.ROLLBACK,
    )
    with pytest.raises(VersioningError) as excinfo:
        validated.resolver.resolve(validated.config)
    assert excinfo.value.code is VersioningErrorCode.LIFECYCLE_SELECTION_FORBIDDEN
