"""V2 binding and semantic identity, using Prompt-07 parser/AST/macro owners."""
from __future__ import annotations
from dataclasses import replace
from types import SimpleNamespace
from ..conditions import preflight_condition_tree
from .compiler import RuleDslCompiler, _Analyzer, _COMPILER_CONTRACT_DATA as _v1_contract
from ..aspect_contract_v2 import (
    get_registry_v2, get_capability_catalog_v2, registry_fingerprint,
    require_v2_authority, implementation_digest, CONDITION_COMPATIBILITY_CONTRACT,
)
from ..evaluator_v2 import CONDITION_CONTENT_SHA256
from .compiler import (
    AnalysisSucceeded,
    AnalyzedRule,
    AnalyzedRuleSet,
    COMPILED_RULE_SET_SCHEMA_VERSION,
    CompilationFailed,
    CompilationSucceeded,
    DSL_CANONICALIZATION_CONTRACT,
    DSL_COMPATIBILITY_CONTRACT,
    DSL_COMPILER_IDENTITY,
    DSL_MACRO_EXPANSION_CONTRACT,
    DSL_SCHEMA_VERSION,
    FrozenMapping,
    MAX_EXPANDED_NODES_PER_DOCUMENT,
    MAX_EXPANDED_NODES_PER_RULE,
    MAX_SOURCE_BYTES,
    MacroExpansionTrace,
    ParsedYamlFailed,
    ResolvedRule,
    RuleSourceIdentity,
    _DiagnosticCollector,
    _ast_data,
    _binding_data,
    _capability_data,
    _document_data,
    _new_compiled_rule,
    _new_compiled_rule_set,
    _source_id_valid,
    _value_data,
    canonical_json_bytes,
    hashlib,
    parse_yaml_source,
)

DSL_COMPILER_VERSION = "2.0.0"
DSL_COMPILER_CONTENT_SHA256 = implementation_digest(
    "dsl/compiler_v2.py", "dsl/compiler.py", "dsl/parser.py", "dsl/models.py",
    "aspect_contract_v2.py", "evaluator_v2.py", "registry.py", "parameters.py",
    "conditions.py", "canonical.py", "prepared_state.py", "definition_validation.py",
    "capabilities.py", "../capability.py", "../versioning.py",
)
_COMPILER_CONTRACT_DATA = FrozenMapping({
    **dict(_v1_contract), "version": DSL_COMPILER_VERSION,
    "profile": "source_scoped_aspects_v2",
    "implementation_sha256": DSL_COMPILER_CONTENT_SHA256,
})


def _validate_lowered_v2(node, *, source):
    if preflight_condition_tree(node) is not None:
        return SimpleNamespace(valid=False, definition=None)
    def visit(item):
        kind = item["type"]
        if kind in ("AND", "OR", "NOT"):
            return {"type": kind, "children": tuple(visit(ch) for ch in item["children"])}
        definition = get_registry_v2().lookup(kind)
        if definition is None or kind != definition.predicate_id:
            raise ValueError("noncanonical V2 leaf")
        result = definition.parameter_schema.validate(item["params"])
        if not result.valid:
            raise ValueError("invalid V2 arguments")
        return {"type": kind, "params": result.normalized_inputs}
    try:
        normalized = FrozenMapping(visit(node))
        return SimpleNamespace(valid=True, definition=SimpleNamespace(normalized_condition=normalized))
    except (KeyError, ValueError, TypeError):
        return SimpleNamespace(valid=False, definition=None)


class _AnalyzerV2(_Analyzer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.registry = get_registry_v2()
        self.catalog = get_capability_catalog_v2()

    def bind_predicate(self, node, **kwargs):
        # The shared binder consumes V2 definitions before computing any binding.
        result = super().bind_predicate(node, **kwargs)
        if result is None or result.predicate_id != "ASPECT_EXISTS":
            return result
        active = any(result.arguments.get(key) is not None for key in ("from_house", "to_house"))
        capabilities = tuple(c for c in result.required_capabilities
            if active or c.capability_id != "planets.house_placement")
        return replace(result, required_capabilities=capabilities,
            binding=replace(result.binding, required_capabilities=capabilities))

    def analyze(self) -> AnalysisSucceeded | CompilationFailed:
        document = self.build_document()
        if document is None:
            return CompilationFailed(compiled_rule_set=None, diagnostics=self.diagnostics.finish())
        macros = {(item.macro_id, item.revision): item for item in document.macros}
        bound_macros = tuple(
            replace(
                item,
                body=self.validate_macro_body(
                    item.body, item, macros, f"$.macros[{item.source_order}].body"
                ),
            )
            for item in document.macros
        )
        macros = {(item.macro_id, item.revision): item for item in bound_macros}
        bound_macros = tuple(
            replace(item, body=self.resolve_macro_types(item.body, macros)) for item in bound_macros
        )
        macros = {(item.macro_id, item.revision): item for item in bound_macros}
        document = replace(
            document,
            macros=bound_macros,
            rules=tuple(
                replace(
                    item,
                    when=self.resolve_macro_types(
                        self.bind_source_tree(
                            item.when,
                            rule=item,
                            path=f"$.rules[{item.source_order}].when",
                        ),
                        macros,
                    ),
                )
                for item in document.rules
            ),
        )
        self.detect_cycles(document.macros)
        if self.diagnostics.has_errors:
            return CompilationFailed(compiled_rule_set=None, diagnostics=self.diagnostics.finish())

        analyzed_rules: list[AnalyzedRule] = []
        expanded_total = 0
        for rule in document.rules:
            traces: list[MacroExpansionTrace] = []
            budget = [0]
            expanded = self.expand(
                rule.when, rule=rule, macros=macros, env={},
                path=f"$.rules[{rule.source_order}].when", depth=0,
                provenance=(), traces=traces, budget=budget,
            )
            if expanded is None:
                continue
            count = self.ast_count(expanded)
            expanded_total += count
            if count > MAX_EXPANDED_NODES_PER_RULE:
                self.diagnostics.add(
                    "P07E309_MACRO_EXPANDED_NODE_LIMIT", stage="expanded",
                    field_path=f"$.rules[{rule.source_order}].when", span=rule.source_span, rule=rule,
                )
                continue
            if expanded_total > MAX_EXPANDED_NODES_PER_DOCUMENT:
                self.diagnostics.add(
                    "P07E309_MACRO_EXPANDED_NODE_LIMIT", stage="expanded",
                    field_path="$.rules", span=rule.source_span, rule=rule,
                )
                continue
            bindings = self.bindings(expanded)
            capabilities_by_pair = {
                (cap.capability_id, cap.capability_version): cap
                for binding in bindings for cap in binding.required_capabilities
            }
            capabilities = tuple(capabilities_by_pair[key] for key in sorted(capabilities_by_pair))
            if tuple((item.capability_id, item.capability_version) for item in rule.requires) != tuple(
                (item.capability_id, item.capability_version) for item in capabilities
            ):
                self.diagnostics.add(
                    "P07E215_PREDICATE_CAPABILITY_MISMATCH", stage="binding",
                    field_path=f"$.rules[{rule.source_order}].requires", span=rule.source_span, rule=rule,
                )
                continue
            lowered_raw = self.lower(expanded)
            validated = _validate_lowered_v2(
                lowered_raw,
                source=RuleSourceIdentity(
                    source_name=self.source_id, rule_id=rule.rule_id, rule_index=rule.source_order,
                ),
            )
            if not validated.valid or validated.definition is None:
                self.diagnostics.add(
                    "P07E404_COMPILED_DIGEST_MISMATCH", stage="expanded",
                    field_path=f"$.rules[{rule.source_order}].when", span=rule.source_span, rule=rule,
                    details={"reason": "lowering_validation_disagreement"},
                )
                continue
            lowered = validated.definition.normalized_condition
            expanded_projection = _ast_data(expanded, include_macro=False)
            expanded_sha = hashlib.sha256(canonical_json_bytes(expanded_projection)).hexdigest()
            resolved_rule = ResolvedRule(
                system=document.system, rule_id=rule.rule_id, rule_version=rule.revision,
                rule_family=rule.family, rule_set_version=document.rule_set_version,
                category=rule.category, domains=rule.domains,
                base_weight=rule.base_weight.as_float(), priority=rule.priority,
                context=rule.context,
                quality=None if rule.quality is None else rule.quality.as_float(),
                provenance=rule.provenance,
                metadata={
                    "label": rule.label,
                    "presentation": rule.presentation,
                    "governance_ref": rule.governance_ref,
                    "dsl": {
                        "schema_version": DSL_SCHEMA_VERSION,
                        "source_id": self.source_id,
                        "evidence_mode": rule.evidence_mode,
                    },
                },
                evaluation_plan_position=rule.source_order,
            )
            execution_projection = {
                "rule_family": rule.family,
                "category": rule.category,
                "domains": list(rule.domains),
                "base_weight": rule.base_weight.as_float(),
                "priority": rule.priority,
                "context": rule.context,
            }
            resolved_rule_projection = {
                "system": document.system,
                "rule_id": rule.rule_id,
                "rule_version": rule.revision,
                "rule_family": rule.family,
                "rule_set_version": document.rule_set_version,
                "category": rule.category,
                "domains": list(rule.domains),
                "base_weight": _value_data(rule.base_weight),
                "priority": rule.priority,
                "context": rule.context,
                "quality": None if rule.quality is None else _value_data(rule.quality),
                "evidence_mode": rule.evidence_mode,
                "evaluation_plan_position": rule.source_order,
            }
            semantic_contract = {
                # Prompt-06 consumes this existing runtime-float projection.
                # The complete exact DSL identity lives beside it so decimal
                # source semantics never depend on Python float formatting.
                "projections": [execution_projection],
                "dsl_compiled": {
                    "compiled_rule_schema_version": COMPILED_RULE_SET_SCHEMA_VERSION,
                    "resolved_rule": resolved_rule_projection,
                    "condition": lowered,
                    "expanded_ast_sha256": expanded_sha,
                    "predicate_bindings": [_binding_data(item) for item in bindings],
                    "required_capabilities": _capability_data(capabilities),
                    "evidence_mode": rule.evidence_mode,
                    "quality": None if rule.quality is None else _value_data(rule.quality),
                    "evaluation_plan_position": rule.source_order,
                    "compiler_contract": _COMPILER_CONTRACT_DATA,
                },
            }
            semantic_sha = hashlib.sha256(canonical_json_bytes(semantic_contract)).hexdigest()
            analyzed_rules.append(AnalyzedRule(
                resolved_rule=resolved_rule, expanded_condition_ast=expanded,
                lowered_condition=lowered, predicate_bindings=bindings,
                required_capabilities=capabilities, expanded_ast_sha256=expanded_sha,
                compiled_semantic_sha256=semantic_sha, semantic_contract=semantic_contract,
                macro_expansion_trace=tuple(traces),
            ))
        if self.diagnostics.has_errors or len(analyzed_rules) != len(document.rules):
            return CompilationFailed(compiled_rule_set=None, diagnostics=self.diagnostics.finish())
        canonical_projection = FrozenMapping(_document_data(document))
        canonical_dsl_sha = hashlib.sha256(canonical_json_bytes(canonical_projection)).hexdigest()
        expanded_set_data = [
            {
                "rule_id": item.resolved_rule.rule_id,
                "revision": item.resolved_rule.rule_version,
                "expanded_ast_sha256": item.expanded_ast_sha256,
            }
            for item in analyzed_rules
        ]
        expanded_set_sha = hashlib.sha256(canonical_json_bytes(expanded_set_data)).hexdigest()
        compiled_set_data = {
            "compiler_contract": _COMPILER_CONTRACT_DATA,
            "system": document.system,
            "rule_set_family": document.rule_set_family,
            "rule_set_version": document.rule_set_version,
            "expanded_ast_sha256": expanded_set_sha,
            "predicate_library_content_sha256": registry_fingerprint(),
            "condition_evaluator": {
                "identity": "parashara-condition-evaluator",
                "version": "2.0.0",
                "compatibility_contract": CONDITION_COMPATIBILITY_CONTRACT,
                "content_sha256": CONDITION_CONTENT_SHA256,
            },
            "rules": [
                {
                    "rule_id": item.resolved_rule.rule_id,
                    "revision": item.resolved_rule.rule_version,
                    "compiled_semantic_sha256": item.compiled_semantic_sha256,
                }
                for item in analyzed_rules
            ],
        }
        compiled_set_sha = hashlib.sha256(canonical_json_bytes(compiled_set_data)).hexdigest()
        return AnalysisSucceeded(analyzed_rule_set=AnalyzedRuleSet(
            document=document, rules=tuple(analyzed_rules),
            source_file_sha256=hashlib.sha256(self.payload).hexdigest(),
            canonical_dsl_sha256=canonical_dsl_sha,
            expanded_ast_sha256=expanded_set_sha,
            compiled_rule_set_sha256=compiled_set_sha,
            canonical_dsl_projection=canonical_projection,
        ))


class RuleDslCompilerV2(RuleDslCompiler):
    def __init__(self, *, resolved_versions, cache_capacity=64):
        require_v2_authority(resolved_versions)
        super().__init__(resolved_versions=resolved_versions, cache_capacity=cache_capacity)

    @classmethod
    def analyze_source(cls, *, source_id: str, payload: bytes | str) -> AnalysisSucceeded | CompilationFailed:
        if not _source_id_valid(source_id):
            collector = _DiagnosticCollector("invalid-source")
            collector.add(
                "P07E103_INVALID_FIELD_VALUE", stage="source", field_path="$.source_id",
                details={"expected": "repository_relative_dot_yaml"},
            )
            return CompilationFailed(compiled_rule_set=None, diagnostics=collector.finish())
        parsed = parse_yaml_source(source_id=source_id, payload=payload)
        if isinstance(parsed, ParsedYamlFailed):
            return CompilationFailed(compiled_rule_set=None, diagnostics=(parsed.diagnostic,))
        payload_bytes = payload.encode("utf-8", errors="strict") if isinstance(payload, str) else payload
        return _AnalyzerV2(
            source_id=source_id, parsed=parsed.document, payload=payload_bytes,
        ).analyze()

    def compile_authorized(self, *, source_id: str) -> CompilationSucceeded | CompilationFailed:
        try:
            payload = self._resolved_versions.load_authorized_dsl_source(
                source_id=source_id, compiler_identity=(
                    DSL_COMPILER_IDENTITY,
                    DSL_COMPILER_VERSION,
                    DSL_COMPATIBILITY_CONTRACT,
                    DSL_COMPILER_CONTENT_SHA256,
                ),
                compiler_metadata={
                    "canonicalization_contract": DSL_CANONICALIZATION_CONTRACT,
                    "compiled_artifact_schema_version": COMPILED_RULE_SET_SCHEMA_VERSION,
                    "dsl_schema_version": DSL_SCHEMA_VERSION,
                    "macro_expansion_contract": DSL_MACRO_EXPANSION_CONTRACT,
                },
                max_bytes=MAX_SOURCE_BYTES,
            )
        except Exception as exc:
            return self._authorization_failure(
                "P07E401_COMPILER_VERSION_MISMATCH"
                if getattr(getattr(exc, "details", {}), "get", lambda *_: None)("dsl_code") == "compiler"
                else "P07E402_MANIFEST_AUTHORIZATION_FAILURE",
                source_id if isinstance(source_id, str) and source_id else "invalid-source",
            )
        analysis = self.analyze_source(source_id=source_id, payload=payload)
        if isinstance(analysis, CompilationFailed):
            return analysis
        analyzed = analysis.analyzed_rule_set
        try:
            self._resolved_versions.authorize_dsl_analysis(analyzed)
        except Exception as exc:
            reason = getattr(getattr(exc, "details", {}), "get", lambda *_: None)("dsl_code")
            code = "P07E403_SOURCE_DIGEST_MISMATCH" if reason == "source" else "P07E404_COMPILED_DIGEST_MISMATCH"
            return self._authorization_failure(code, source_id)
        manifest = self._resolved_versions.manifest
        key = self._cache_key(manifest=manifest, analyzed=analyzed)
        cached = self._cache.get(key)
        if cached is not None:
            expected_identity = (
                source_id,
                analyzed.source_file_sha256,
                analyzed.canonical_dsl_sha256,
                analyzed.expanded_ast_sha256,
                analyzed.compiled_rule_set_sha256,
                DSL_COMPILER_IDENTITY,
                DSL_COMPILER_VERSION,
                DSL_COMPILER_CONTENT_SHA256,
                manifest.manifest_fingerprint_sha256,
            )
            observed_identity = (
                cached.source_identity,
                cached.source_file_sha256,
                cached.canonical_dsl_sha256,
                cached.expanded_ast_sha256,
                cached.compiled_rule_set_sha256,
                cached.compiler_identity,
                cached.compiler_version,
                cached.compiler_content_sha256,
                cached.manifest_fingerprint_sha256,
            )
            try:
                if observed_identity != expected_identity:
                    raise ValueError("cached compiled identity changed")
                self._resolved_versions.authorize_compiled_rule_set(cached)
            except Exception:
                self._cache.pop(key, None)
                return self._authorization_failure("P07E404_COMPILED_DIGEST_MISMATCH", source_id)
            self._cache.move_to_end(key)
            return CompilationSucceeded(compiled_rule_set=cached)
        rules = tuple(_new_compiled_rule(
            compiled_rule_schema_version=COMPILED_RULE_SET_SCHEMA_VERSION,
            resolved_rule=item.resolved_rule,
            expanded_condition_ast=item.expanded_condition_ast,
            lowered_condition=item.lowered_condition,
            predicate_bindings=item.predicate_bindings,
            required_capabilities=item.required_capabilities,
            source_identity=source_id,
            source_file_sha256=analyzed.source_file_sha256,
            canonical_dsl_sha256=analyzed.canonical_dsl_sha256,
            expanded_ast_sha256=item.expanded_ast_sha256,
            compiled_semantic_sha256=item.compiled_semantic_sha256,
            macro_expansion_trace=item.macro_expansion_trace,
            resolved_versions=self._resolved_versions,
        ) for item in analyzed.rules)
        compiled = _new_compiled_rule_set(
            compiled_rule_set_schema_version=COMPILED_RULE_SET_SCHEMA_VERSION,
            system=analyzed.document.system,
            rule_set_family=analyzed.document.rule_set_family,
            rule_set_version=analyzed.document.rule_set_version,
            source_identity=source_id,
            source_file_sha256=analyzed.source_file_sha256,
            canonical_dsl_sha256=analyzed.canonical_dsl_sha256,
            expanded_ast_sha256=analyzed.expanded_ast_sha256,
            compiled_rule_set_sha256=analyzed.compiled_rule_set_sha256,
            rules=rules,
            resolved_versions=self._resolved_versions,
            compiler_identity=DSL_COMPILER_IDENTITY,
            compiler_version=DSL_COMPILER_VERSION,
            compiler_content_sha256=DSL_COMPILER_CONTENT_SHA256,
            manifest_fingerprint_sha256=manifest.manifest_fingerprint_sha256,
        )
        try:
            self._resolved_versions.authorize_compiled_rule_set(compiled)
        except Exception:
            return self._authorization_failure("P07E404_COMPILED_DIGEST_MISMATCH", source_id)
        if self._cache_capacity:
            self._cache[key] = compiled
            self._cache.move_to_end(key)
            while len(self._cache) > self._cache_capacity:
                self._cache.popitem(last=False)
        return CompilationSucceeded(compiled_rule_set=compiled)
