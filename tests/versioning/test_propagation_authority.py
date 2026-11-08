"""Prompt-06 authority propagation, anti-relabeling, and no-mid-run-replacement tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.astrostate_api import AstroStateBuildSuccess, freeze_astrostate
from systems.Parasara.engine.domain import DomainBuildProduced, YogaDiagnosticFactory
from systems.Parasara.engine.enrichments.yoga_engine import (
    evaluate_yoga_diagnostics,
    evaluate_yoga_snapshot,
    load_yoga_rule_source,
)
from systems.Parasara.engine.interpreters.career import interpret_career_domain
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.output_assembler import EngineMetadata, OutputAssembler
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.rule_engine import ResolvedRule, RuleEngine
from systems.Parasara.engine.versioning import (
    RuleVersionResolver,
    VersioningError,
    VersioningErrorCode,
    compatibility_v1_config,
)
from systems.Parasara.tools.generate_snapshot import _snapshot_assembly_input

from tests.versioning.conftest import SyntheticCatalogBuilder, build_rule_revision


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"


def _astro(name: str = "golden_chart_01.json"):
    return chart_to_astrostate(SuryaAdapter.load(str(FIXTURES / name)))


def _v1_authority():
    return RuleVersionResolver().resolve(compatibility_v1_config())


def _snapshot():
    build = freeze_astrostate(_astro())
    assert isinstance(build, AstroStateBuildSuccess)
    return build.snapshot


def test_career_authority_propagates_to_domain_prediction() -> None:
    resolved = _v1_authority()
    outcome = interpret_career_domain(_astro(), resolved_versions=resolved)
    assert isinstance(outcome, DomainBuildProduced)
    prediction = outcome.prediction
    assert prediction.engine_version == resolved.manifest.engine.version
    assert prediction.rule_set_version == resolved.manifest.rule_set_version
    assert prediction.inference_version == resolved.manifest.inference.version
    assert prediction.source_authority.resolved_versions is resolved
    assert prediction.source_authority.ledger.resolved_versions is resolved


def test_career_binds_authority_before_every_rule_match(monkeypatch) -> None:
    resolved = _v1_authority()
    observed = []
    original = RuleEngine.build_match

    def probe(self, *args, **kwargs):
        observed.append(self.resolved_versions is resolved)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(RuleEngine, "build_match", probe)
    outcome = interpret_career_domain(_astro(), resolved_versions=resolved)
    assert isinstance(outcome, DomainBuildProduced)
    assert observed and all(observed)


def test_public_career_accepts_engine_config_selection() -> None:
    config = compatibility_v1_config()
    outcome = interpret_career_domain(_astro(), engine_config=config)
    assert isinstance(outcome, DomainBuildProduced)
    assert outcome.prediction.source_authority.resolved_versions.config == config


def test_yoga_authority_propagates_and_reconciles_every_diagnostic() -> None:
    resolved = _v1_authority()
    diagnostics = evaluate_yoga_diagnostics(_astro(), resolved_versions=resolved)
    assert diagnostics
    for diagnostic in diagnostics:
        assert diagnostic.rule_set_version == resolved.manifest.rule_set_version
        # Authority reconciliation must not fail for any active Yoga row.
        resolved.authorize_rule(diagnostic.source_rule_match)
        assert diagnostic.source_evaluation_record.resolved_versions is resolved


def test_altered_yoga_source_is_rejected_under_unchanged_v1_authority(tmp_path) -> None:
    source_path = ROOT / "systems" / "Parasara" / "rules" / "parashara" / "v1" / "yogas.yaml"
    altered_path = tmp_path / "yogas.yaml"
    altered_path.write_text(
        source_path.read_text(encoding="utf-8").replace(
            "from_house: 1", "from_house: 2", 1
        ),
        encoding="utf-8",
    )
    source = load_yoga_rule_source(altered_path)
    with pytest.raises(VersioningError):
        evaluate_yoga_snapshot(_snapshot(), source, resolved_versions=_v1_authority())


def test_output_assembler_validates_engine_metadata_against_authority() -> None:
    resolved = _v1_authority()
    metadata = EngineMetadata(
        name="jyothishyam-parashara",
        engine_version=resolved.manifest.engine.version,
        rule_set_family=resolved.manifest.rule_set_family,
        rule_set_version=resolved.manifest.rule_set_version,
        public_meta_engine_version="jyothishyam-parashara@0.1.0",
        generated_at=None,
        resolved_versions=resolved,
    )
    resolved.authorize_engine_metadata(metadata)
    tampered = EngineMetadata(
        name="jyothishyam-parashara",
        engine_version="9.9.9-relabeled",
        rule_set_family=resolved.manifest.rule_set_family,
        rule_set_version=resolved.manifest.rule_set_version,
        public_meta_engine_version="jyothishyam-parashara@0.1.0",
        generated_at=None,
        resolved_versions=resolved,
    )
    with pytest.raises(VersioningError) as excinfo:
        resolved.authorize_engine_metadata(tampered)
    assert excinfo.value.code is VersioningErrorCode.AUTHORITY_MISMATCH


def test_same_label_distinct_authority_is_rejected_downstream() -> None:
    authority_a = _v1_authority()
    authority_b = _v1_authority()
    assert authority_a is not authority_b
    assembly_input = _snapshot_assembly_input(
        _snapshot(), resolved_versions=authority_a
    )
    assembler = OutputAssembler()
    assert assembler.assemble(assembly_input, resolved_versions=authority_a)
    with pytest.raises(VersioningError) as excinfo:
        assembler.assemble(assembly_input, resolved_versions=authority_b)
    assert excinfo.value.code is VersioningErrorCode.AUTHORITY_MISMATCH

    diagnostics = evaluate_yoga_diagnostics(_astro(), resolved_versions=authority_a)
    record = diagnostics[0].source_evaluation_record
    with pytest.raises(VersioningError) as factory_error:
        YogaDiagnosticFactory._from_evaluation_record(
            record, resolved_versions=authority_b
        )
    assert factory_error.value.code is VersioningErrorCode.AUTHORITY_MISMATCH


def test_require_same_rejects_a_different_resolved_authority(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    first = synthetic_catalog.add(family="fam", version="one")
    second = synthetic_catalog.add(family="fam", version="two")
    resolved_one = first.resolver.resolve(first.config)
    resolved_two = second.resolver.resolve(second.config)
    resolved_one.require_same(resolved_one)
    with pytest.raises(VersioningError) as excinfo:
        resolved_one.require_same(resolved_two)
    assert excinfo.value.code is VersioningErrorCode.AUTHORITY_MISMATCH


def test_rule_engine_rejects_mid_run_authority_replacement(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    first = synthetic_catalog.add(family="fam", version="one")
    second = synthetic_catalog.add(family="fam", version="two")
    resolved_one = first.resolver.resolve(first.config)
    resolved_two = second.resolver.resolve(second.config)
    engine = RuleEngine(resolved_versions=resolved_one)
    with pytest.raises(VersioningError) as excinfo:
        engine.require_authority(resolved_two)
    assert excinfo.value.code is VersioningErrorCode.AUTHORITY_MISMATCH


def test_predicate_evaluator_rejects_mid_run_authority_replacement(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    first = synthetic_catalog.add(family="fam", version="one")
    second = synthetic_catalog.add(family="fam", version="two")
    resolved_one = first.resolver.resolve(first.config)
    resolved_two = second.resolver.resolve(second.config)
    evaluator = PredicateEvaluator(resolved_versions=resolved_one)
    with pytest.raises(VersioningError) as excinfo:
        evaluator.require_authority(resolved_two)
    assert excinfo.value.code is VersioningErrorCode.AUTHORITY_MISMATCH


def test_legacy_unbound_engine_has_no_authority_to_require(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(family="fam", version="v1")
    resolved = pack.resolver.resolve(pack.config)
    engine = RuleEngine()
    with pytest.raises(ValueError):
        engine.require_authority(resolved)


def test_caller_relabeling_a_copied_rule_cannot_pass_reconciliation(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(
        family="fam",
        version="v1",
        rule_revisions=(build_rule_revision(rule_id="synthetic_rule_a", revision="1"),),
    )
    resolved = pack.resolver.resolve(pack.config)
    resolved_rule = ResolvedRule(
        system="synthetic",
        rule_id="synthetic_rule_a",
        rule_version="1",
        rule_family="synthetic",
        rule_set_version=resolved.manifest.rule_set_version,
        category="synthetic",
        domains=(),
        base_weight=0.1,
        priority=0,
        context="natal",
        quality=None,
        provenance={},
        metadata={},
        evaluation_plan_position=0,
    )
    # A caller-copied identity with a relabeled revision cannot reconcile.
    relabeled = ResolvedRule(
        system="synthetic",
        rule_id="synthetic_rule_a",
        rule_version="2-relabeled",
        rule_family="synthetic",
        rule_set_version=resolved.manifest.rule_set_version,
        category="synthetic",
        domains=(),
        base_weight=0.1,
        priority=0,
        context="natal",
        quality=None,
        provenance={},
        metadata={},
        evaluation_plan_position=0,
    )
    resolved.authorize_rule(resolved_rule)
    with pytest.raises(VersioningError) as excinfo:
        resolved.authorize_rule(relabeled)
    assert excinfo.value.code is VersioningErrorCode.RULE_NOT_IN_MANIFEST
