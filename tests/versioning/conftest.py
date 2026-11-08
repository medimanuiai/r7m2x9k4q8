"""Synthetic, non-astrology rule-set/catalog builders for Prompt-06 tests.

These helpers never touch the real v1 corpus or catalog. Every synthetic
manifest/catalog is written under ``tmp_path`` and loaded only through the
test-only ``RuleVersionResolver.for_test`` constructor, which applies the
same schema/digest verification as the production resolver.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from pathlib import Path
from typing import Any, Mapping, Sequence

import pytest

from systems.Parasara.engine.rules.canonical import canonical_json_bytes
from systems.Parasara.engine.rules.registry import predicate_registry_fingerprint_sha256
from systems.Parasara.engine.versioning import (
    CONDITION_EVALUATOR_COMPATIBILITY_CONTRACT,
    CONDITION_EVALUATOR_CONTENT_SHA256,
    CONDITION_EVALUATOR_IDENTITY,
    CONDITION_EVALUATOR_VERSION,
    EVALUATION_CONTRACT_VERSION,
    PREDICATE_LIBRARY_IDENTITY,
    PREDICATE_LIBRARY_VERSION,
    VERSIONING_SCHEMA_VERSION,
    ComponentIdentity,
    EngineConfig,
    EngineMode,
    EvaluationVersionManifest,
    RuleRevisionIdentity,
    RuleVersionResolver,
    SelectionPurpose,
    manifest_fingerprint_sha256,
    manifest_to_data,
)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _draft_manifest(**fields: Any) -> EvaluationVersionManifest:
    """Compute the correct fingerprint without a circular constructor call."""

    draft = object.__new__(EvaluationVersionManifest)
    for name, value in fields.items():
        object.__setattr__(draft, name, value)
    fingerprint = manifest_fingerprint_sha256(draft)
    return EvaluationVersionManifest(**fields, manifest_fingerprint_sha256=fingerprint)


def _engine_contract_digest(artifact_id: str, record_id: str) -> str:
    return _sha256(canonical_json_bytes({
        "artifact_id": artifact_id,
        "contract_version": record_id,
    }))


def build_rule_revision(
    *,
    rule_id: str,
    revision: str = "1",
    source_artifact_id: str = "synthetic.source",
    source_record_id: str = "synthetic",
    source_order: int = 0,
    rule_family: str = "synthetic",
    category: str = "synthetic",
    domains: Sequence[str] = (),
    base_weight: float = 0.1,
    priority: int = 0,
    context: str = "natal",
    semantic_contract: Mapping[str, Any] | None = None,
) -> RuleRevisionIdentity:
    """Build one synthetic rule identity whose projection authorizes a matching ResolvedRule."""

    if semantic_contract is not None:
        contract: dict[str, Any] = dict(semantic_contract)
    else:
        contract = {
            "projections": [{
                "rule_family": rule_family,
                "category": category,
                "domains": list(domains),
                "base_weight": base_weight,
                "priority": priority,
                "context": context,
            }],
        }
    return RuleRevisionIdentity(
        rule_id=rule_id,
        revision=revision,
        semantic_content_sha256=_sha256(canonical_json_bytes(contract)),
        source_artifact_id=source_artifact_id,
        source_artifact_semantic_sha256=_engine_contract_digest(source_artifact_id, source_record_id),
        source_order=source_order,
        materialization_contract_id=None,
        materialization_bindings=None,
        execution_projections=("synthetic",),
        semantic_contract=contract,
    )


@dataclass(frozen=True)
class SyntheticPack:
    """One resolvable synthetic (resolver, config, manifest) tuple."""

    resolver: RuleVersionResolver
    config: EngineConfig
    manifest: EvaluationVersionManifest
    manifest_file_sha256: str
    manifest_relative_path: str
    dsl_source_id: str | None = None
    dsl_source_path: Path | None = None


class SyntheticCatalogBuilder:
    """Accumulates synthetic catalog entries under one shared ``tmp_path`` root."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._entries: list[dict[str, Any]] = []
        self._catalog_relative = "config/versioning/synthetic_rule_sets.json"

    @property
    def catalog_path(self) -> Path:
        return self.root / self._catalog_relative

    def resolver(self) -> RuleVersionResolver:
        return RuleVersionResolver.for_test(
            catalog_path=self.catalog_path, repository_root=self.root
        )

    def add(
        self,
        *,
        system: str = "synthetic",
        family: str = "synthetic",
        version: str = "test-v1",
        engine_version: str = "9.9.9",
        output_schema_version: str = "1.0.0",
        compatibility_profile: str = "synthetic_profile_v1",
        rule_revisions: Sequence[RuleRevisionIdentity] = (),
        condition_evaluator_identity: str = CONDITION_EVALUATOR_IDENTITY,
        condition_evaluator_version: str = CONDITION_EVALUATOR_VERSION,
        condition_evaluator_contract: str = CONDITION_EVALUATOR_COMPATIBILITY_CONTRACT,
        condition_evaluator_content_sha256: str = CONDITION_EVALUATOR_CONTENT_SHA256,
        lifecycle: str = "VALIDATED",
        technical_validation_evidence: str = "synthetic-test-evidence",
        astrology_sme_approved: bool = False,
        astrology_sme_approval_evidence: str | None = None,
        available: bool = True,
        replay_available: bool = True,
        rollback_authorized: bool = False,
        warning: str | None = None,
        allowed_modes: Sequence[str] = ("EXPERIMENTAL",),
        allowed_purposes: Sequence[str] = ("NEW_EVALUATION",),
        mode: EngineMode = EngineMode.EXPERIMENTAL,
        purpose: SelectionPurpose = SelectionPurpose.NEW_EVALUATION,
        evaluation_instant: str = "1970-01-01T00:00:00Z",
        inference_payload: Mapping[str, Any] | None = None,
        tamper_manifest_after_write: bool = False,
        _dsl_component: ComponentIdentity | None = None,
        _source_artifacts: Sequence[Mapping[str, Any]] | None = None,
        _dsl_source_id: str | None = None,
        _graph_component: ComponentIdentity | None = None,
    ) -> SyntheticPack:
        """Write one manifest + inference artifact and append one catalog entry."""

        manifest_relative = f"rules/{family}/{version}/manifest.json"
        inference_relative = f"config/inference/{family}_{version}_config.json"

        inference_path = self.root / inference_relative
        inference_path.parent.mkdir(parents=True, exist_ok=True)
        payload = (
            inference_payload
            if inference_payload is not None
            else {"synthetic": True, "family": family, "version": version}
        )
        inference_bytes = canonical_json_bytes(payload)
        inference_path.write_bytes(inference_bytes)

        engine = ComponentIdentity(
            identity="synthetic-engine",
            version=engine_version,
            compatibility_contract=EVALUATION_CONTRACT_VERSION,
        )
        predicate_library = ComponentIdentity(
            identity=PREDICATE_LIBRARY_IDENTITY,
            version=PREDICATE_LIBRARY_VERSION,
            compatibility_contract="predicate-result@1.0.0",
            content_sha256=predicate_registry_fingerprint_sha256(),
        )
        condition_evaluator = ComponentIdentity(
            identity=condition_evaluator_identity,
            version=condition_evaluator_version,
            compatibility_contract=condition_evaluator_contract,
            content_sha256=condition_evaluator_content_sha256,
        )
        inference = ComponentIdentity(
            identity="synthetic-inference",
            version="synthetic-1.0.0",
            compatibility_contract="inference-result@1.0.0",
            artifact_path=inference_relative,
            content_sha256=_sha256(inference_bytes),
        )
        source_artifacts = [] if _source_artifacts is None else list(_source_artifacts)
        if _source_artifacts is None:
            for artifact_id in sorted({item.source_artifact_id for item in rule_revisions}):
                artifact_relative = f"synthetic/{family}_{version}_{artifact_id}.json"
                artifact_path = self.root / artifact_relative
                artifact_path.parent.mkdir(parents=True, exist_ok=True)
                artifact_path.write_bytes(canonical_json_bytes({"artifact_id": artifact_id}))
                source_artifacts.append({
                    "artifact_id": artifact_id,
                    "path": artifact_relative,
                    "format": "engine-contract",
                    "record_ids": ("synthetic",),
                    "semantic_content_sha256": _engine_contract_digest(artifact_id, "synthetic"),
                })
        manifest = _draft_manifest(
            manifest_schema_version=VERSIONING_SCHEMA_VERSION,
            system=system,
            engine=engine,
            rule_set_family=family,
            rule_set_version=version,
            ordered_rule_revisions=tuple(rule_revisions),
            ordered_source_artifacts=tuple(source_artifacts),
            predicate_library=predicate_library,
            condition_evaluator=condition_evaluator,
            inference=inference,
            knowledge_data=(),
            output_schema_version=output_schema_version,
            compatibility_profile=compatibility_profile,
            dsl=_dsl_component,
            dependency_graph=_graph_component,
        )
        manifest_path = self.root / manifest_relative
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_bytes = canonical_json_bytes(manifest_to_data(manifest, include_fingerprint=True))
        manifest_path.write_bytes(manifest_bytes)
        manifest_file_sha256 = _sha256(manifest_bytes)
        if tamper_manifest_after_write:
            # Corrupt the file only after the catalog's expected digest is fixed,
            # so resolution must fail on a genuine digest mismatch.
            manifest_path.write_bytes(manifest_bytes.replace(b"synthetic", b"tampered", 1))

        entry = {
            "system": system,
            "family": family,
            "version": version,
            "manifest_path": manifest_relative,
            "manifest_file_sha256": manifest_file_sha256,
            "lifecycle": lifecycle,
            "technical_validation_evidence": technical_validation_evidence,
            "astrology_sme_approved": astrology_sme_approved,
            "astrology_sme_approval_evidence": astrology_sme_approval_evidence,
            "available": available,
            "replay_available": replay_available,
            "rollback_authorized": rollback_authorized,
            "warning": warning,
            "allowed_modes": list(allowed_modes),
            "allowed_purposes": list(allowed_purposes),
        }
        self._entries = [
            item
            for item in self._entries
            if (item["system"], item["family"], item["version"]) != (system, family, version)
        ]
        self._entries.append(entry)
        self._write_catalog()

        config = EngineConfig(
            config_schema_version=VERSIONING_SCHEMA_VERSION,
            system=system,
            engine_version=engine_version,
            rule_set_family=family,
            rule_set_version=version,
            mode=mode,
            purpose=purpose,
            evaluation_instant=evaluation_instant,
            output_schema_version=output_schema_version,
            compatibility_profile=compatibility_profile,
        )
        return SyntheticPack(
            resolver=self.resolver(),
            config=config,
            manifest=manifest,
            manifest_file_sha256=manifest_file_sha256,
            manifest_relative_path=manifest_relative,
            dsl_source_id=_dsl_source_id,
            dsl_source_path=(None if _dsl_source_id is None else self.root / _dsl_source_id),
        )

    def add_dsl(self, *, source_id: str, payload: bytes, _graph_component=None, **selection) -> SyntheticPack:
        """Create one resolver-authorized synthetic Prompt-07 DSL pack."""

        from systems.Parasara.engine.rules.dsl import (
            AnalysisSucceeded,
            DSL_CANONICALIZATION_CONTRACT,
            DSL_COMPATIBILITY_CONTRACT,
            DSL_COMPILER_CONTENT_SHA256,
            DSL_COMPILER_IDENTITY,
            DSL_COMPILER_VERSION,
            DSL_MACRO_EXPANSION_CONTRACT,
            DSL_SCHEMA_VERSION,
            COMPILED_RULE_SET_SCHEMA_VERSION,
            RuleDslCompiler,
        )

        result = RuleDslCompiler.analyze_source(source_id=source_id, payload=payload)
        if not isinstance(result, AnalysisSucceeded):
            raise AssertionError(tuple((item.code, item.field_path) for item in result.diagnostics))
        analyzed = result.analyzed_rule_set
        artifact_id = f"dsl.{analyzed.document.rule_set_family}.{analyzed.document.rule_set_version}"
        source_path = self.root / source_id
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_bytes(payload)
        revisions = tuple(
            RuleRevisionIdentity(
                rule_id=item.resolved_rule.rule_id,
                revision=item.resolved_rule.rule_version,
                semantic_content_sha256=item.compiled_semantic_sha256,
                source_artifact_id=artifact_id,
                source_artifact_semantic_sha256=analyzed.canonical_dsl_sha256,
                source_order=index,
                materialization_contract_id=None,
                materialization_bindings=None,
                execution_projections=item.resolved_rule.domains or ("synthetic",),
                semantic_contract=item.semantic_contract,
            )
            for index, item in enumerate(analyzed.rules)
        )
        component = ComponentIdentity(
            identity=DSL_COMPILER_IDENTITY,
            version=DSL_COMPILER_VERSION,
            compatibility_contract=DSL_COMPATIBILITY_CONTRACT,
            content_sha256=DSL_COMPILER_CONTENT_SHA256,
            metadata={
                "canonicalization_contract": DSL_CANONICALIZATION_CONTRACT,
                "compiled_artifact_schema_version": COMPILED_RULE_SET_SCHEMA_VERSION,
                "dsl_schema_version": DSL_SCHEMA_VERSION,
                "macro_expansion_contract": DSL_MACRO_EXPANSION_CONTRACT,
            },
        )
        artifact = {
            "artifact_id": artifact_id,
            "path": source_id,
            "format": "rule-dsl-yaml",
            "record_ids": tuple(item.resolved_rule.rule_id for item in analyzed.rules),
            "semantic_content_sha256": analyzed.canonical_dsl_sha256,
            "expanded_ast_sha256": analyzed.expanded_ast_sha256,
            "compiled_rule_set_sha256": analyzed.compiled_rule_set_sha256,
        }
        return self.add(
            system=analyzed.document.system,
            family=analyzed.document.rule_set_family,
            version=analyzed.document.rule_set_version,
            rule_revisions=revisions,
            _dsl_component=component,
            _source_artifacts=(artifact,),
            _dsl_source_id=source_id,
            _graph_component=_graph_component,
            **selection,
        )

    def add_graph(self, *, source_id, payload, graph_source_id, graph_payload, **selection):
        """Build a synthetic graph manifest without changing existing DSL defaults."""
        from systems.Parasara.engine.rules.dsl import RuleDslCompiler, AnalysisSucceeded
        from systems.Parasara.engine.rules.graph import (
            RuleGraphCompiler, GraphAnalysisSucceeded, GRAPH_CONTRACT_DATA,
            GRAPH_CONTRACT_SHA256, GRAPH_COMPILER_CONTENT_SHA256,
        )
        dsl = RuleDslCompiler.analyze_source(source_id=source_id, payload=payload)
        assert isinstance(dsl, AnalysisSucceeded), dsl
        doc = dsl.analyzed_rule_set.document
        graph = RuleGraphCompiler.analyze_source(source_id=graph_source_id, payload=graph_payload,
            analyzed_rule_set=dsl.analyzed_rule_set,
            dsl_source_artifact_id=f"dsl.{doc.rule_set_family}.{doc.rule_set_version}")
        assert isinstance(graph, GraphAnalysisSucceeded), graph
        analysis = graph.analysis
        path = self.root / graph_source_id
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(graph_payload)
        component = ComponentIdentity(identity=GRAPH_CONTRACT_DATA["identity"], version=GRAPH_CONTRACT_DATA["version"],
            compatibility_contract=GRAPH_CONTRACT_DATA["compatibility_contract"],
            content_sha256=GRAPH_COMPILER_CONTENT_SHA256, artifact_path=graph_source_id,
            logical_sha256=analysis.graph_sha256, metadata=dict(graph_schema_version="1.0.0",
                graph_contract_sha256=GRAPH_CONTRACT_SHA256, declarations_sha256=analysis.declarations_sha256,
                plan_sha256=analysis.plan_sha256))
        return self.add_dsl(source_id=source_id, payload=payload, _graph_component=component, **selection)

    def _write_catalog(self) -> None:
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "catalog_schema_version": VERSIONING_SCHEMA_VERSION,
            "entries": self._entries,
            "migration_inventory": [],
        }
        self.catalog_path.write_bytes(canonical_json_bytes(payload))


@pytest.fixture
def synthetic_catalog(tmp_path: Path) -> SyntheticCatalogBuilder:
    return SyntheticCatalogBuilder(tmp_path)
