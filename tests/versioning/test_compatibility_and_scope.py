"""Prompt-06 compatibility discipline after the Prompt-07 extension."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from systems.Parasara.engine.rules.rule_engine import ResolvedRule, RuleEngine
from systems.Parasara.engine.rules.rule_match import RuleMatchStatus
from systems.Parasara.engine.versioning import (
    DEFAULT_RULE_SET_CATALOG,
    RuleVersionResolver,
    VersioningError,
    VersioningErrorCode,
    compatibility_v1_config,
)

from tests.versioning.conftest import SyntheticCatalogBuilder, build_rule_revision


ROOT = Path(__file__).resolve().parents[2]
VERSIONING_MODULE = ROOT / "systems" / "Parasara" / "engine" / "versioning.py"


def test_compatibility_facade_always_resolves_literal_v1_regardless_of_catalog_order() -> None:
    config = compatibility_v1_config()
    assert (config.system, config.rule_set_family, config.rule_set_version) == (
        "parashara", "parashara", "v1",
    )
    resolved_first = RuleVersionResolver().resolve(compatibility_v1_config())
    resolved_second = RuleVersionResolver().resolve(compatibility_v1_config())
    assert (
        resolved_first.manifest_fingerprint_sha256
        == resolved_second.manifest_fingerprint_sha256
    )


def test_v1_catalog_entry_is_not_production() -> None:
    catalog = json.loads(DEFAULT_RULE_SET_CATALOG.read_text(encoding="utf-8"))
    entries = [
        entry for entry in catalog["entries"]
        if (entry["system"], entry["family"], entry["version"]) == ("parashara", "parashara", "v1")
    ]
    assert len(entries) == 1
    assert entries[0]["lifecycle"] == "VALIDATED"
    assert entries[0]["astrology_sme_approved"] is False
    assert entries[0]["technical_validation_evidence"] == "prompt06-dual-python-validation"


def test_versioning_module_never_reads_environment_or_process_cwd() -> None:
    tree = ast.parse(VERSIONING_MODULE.read_text(encoding="utf-8"), filename=str(VERSIONING_MODULE))
    forbidden_calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in {"getenv", "environ", "getcwd"}:
            forbidden_calls.append(node.attr)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "input":
            forbidden_calls.append("input")
    assert forbidden_calls == []


def test_versioning_module_imports_no_network_or_process_modules() -> None:
    tree = ast.parse(VERSIONING_MODULE.read_text(encoding="utf-8"), filename=str(VERSIONING_MODULE))
    forbidden_roots = {"socket", "requests", "urllib", "subprocess", "http"}
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.append(node.module.split(".", 1)[0])
    assert not (set(found) & forbidden_roots)


def test_manifest_requires_absent_dsl_and_dependency_graph_components(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    pack = synthetic_catalog.add(family="fam", version="v1")
    assert pack.manifest.dsl is None
    assert pack.manifest.dependency_graph is None


def test_current_v1_has_no_dsl_or_graph_binding_and_graph_is_separate() -> None:
    resolved = RuleVersionResolver().resolve(compatibility_v1_config())
    assert resolved.manifest.dsl is None
    assert resolved.manifest.dependency_graph is None
    engine_root = ROOT / "systems" / "Parasara" / "engine"
    forbidden_names = {"dependency_graph", "graph_planner"}
    present = {
        path.stem
        for path in engine_root.rglob("*.py")
        if path.stem in forbidden_names
    }
    assert present == set()
    assert (engine_root / "rules/graph/compiler.py").is_file()


def test_supported_synthetic_dsl_component_does_not_enable_dependency_graph(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    payload = (ROOT / "tests/dsl/fixtures/minimal.yaml").read_bytes()
    pack = synthetic_catalog.add_dsl(
        source_id="synthetic/prompt07_fixture/fixture-v1/rules.yaml",
        payload=payload,
    )
    resolved = pack.resolver.resolve(pack.config)
    assert resolved.manifest.dsl is not None
    assert resolved.manifest.dependency_graph is None


def test_two_intentionally_different_synthetic_packs_coexist_in_both_orders(
    synthetic_catalog: SyntheticCatalogBuilder,
) -> None:
    one = synthetic_catalog.add(
        family="fam",
        version="one",
        rule_revisions=(build_rule_revision(rule_id="synthetic_rule", revision="1", base_weight=0.1),),
    )
    two = synthetic_catalog.add(
        family="fam",
        version="two",
        rule_revisions=(build_rule_revision(rule_id="synthetic_rule", revision="2", base_weight=0.2),),
    )
    resolved_one = one.resolver.resolve(one.config)
    resolved_two = two.resolver.resolve(two.config)

    def _matches_for(resolved) -> tuple[str, str, float]:
        engine = RuleEngine(resolved_versions=resolved)
        resolved_rule = ResolvedRule(
            system="synthetic",
            rule_id="synthetic_rule",
            rule_version=resolved.manifest.ordered_rule_revisions[0].revision,
            rule_family="synthetic",
            rule_set_version=resolved.manifest.rule_set_version,
            category="synthetic",
            domains=(),
            base_weight=resolved.manifest.ordered_rule_revisions[0].semantic_contract[
                "projections"
            ][0]["base_weight"],
            priority=0,
            context="natal",
            quality=None,
            provenance={},
            metadata={"domain_neutral": True},
            evaluation_plan_position=0,
        )
        match = engine.build_match(
            resolved_rule,
            None,
            evaluation_snapshot_digest="0" * 64,
            evaluation_context={},
            status_override=RuleMatchStatus.MATCHED,
        )
        return match.rule_set_version, match.rule_version, match.base_weight

    forward = (_matches_for(resolved_one), _matches_for(resolved_two))
    backward = (_matches_for(resolved_two), _matches_for(resolved_one))
    assert forward[0] == backward[1]
    assert forward[1] == backward[0]
    assert forward[0][0] == "one" and forward[0][1] == "1" and forward[0][2] == 0.1
    assert forward[1][0] == "two" and forward[1][1] == "2" and forward[1][2] == 0.2

    # Each authority still rejects the other's rule-set label.
    with pytest.raises(VersioningError) as excinfo:
        RuleEngine(resolved_versions=resolved_one).build_match(
            ResolvedRule(
                system="synthetic",
                rule_id="synthetic_rule",
                rule_version="2",
                rule_family="synthetic",
                rule_set_version="two",
                category="synthetic",
                domains=(),
                base_weight=0.2,
                priority=0,
                context="natal",
                quality=None,
                provenance={},
                metadata={"domain_neutral": True},
                evaluation_plan_position=0,
            ),
            None,
            evaluation_snapshot_digest="0" * 64,
            evaluation_context={},
            status_override=RuleMatchStatus.MATCHED,
        )
    assert excinfo.value.code is VersioningErrorCode.RULE_CONTENT_MISMATCH
