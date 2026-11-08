"""Immutable internal models for the bounded Prompt-07 Rule DSL."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import InitVar, dataclass, field
from decimal import Decimal, InvalidOperation
import re
from typing import Any, TypeAlias

from systems.Parasara.engine.rules.canonical import FrozenMapping, freeze_canonical
from systems.Parasara.engine.rules.rule_engine import ResolvedRule


DSL_SCHEMA_VERSION = "1.0.0"
COMPILED_RULE_SET_SCHEMA_VERSION = "1.0.0"

# This immutable projection is the sole source of truth for every normative
# Prompt-07 resource bound. Parser/compiler aliases below deliberately read
# from it so the runtime limits and compiler component fingerprint cannot
# drift independently.
DSL_RESOURCE_LIMITS = FrozenMapping({
    "source_bytes": 1_048_576,
    "yaml_documents": 1,
    "rules_per_document": 256,
    "dsl_source_artifacts_per_rule_set": 1,
    "macros_per_document": 128,
    "macro_parameters": 16,
    "mapping_entries": 64,
    "sequence_elements": 256,
    "string_code_points": 4_096,
    "identifier_code_points": 128,
    "source_id_code_points": 256,
    "integer_minimum": -(2**31),
    "integer_maximum": 2**31 - 1,
    "decimal_significant_digits": 38,
    "decimal_scale": 12,
    "decimal_magnitude": "1000000",
    "source_ast_depth": 64,
    "source_ast_nodes_per_rule": 4_096,
    "source_ast_nodes_per_document": 16_384,
    "logical_children_per_node": 256,
    "macro_expansion_depth": 16,
    "expanded_nodes_per_rule": 4_096,
    "expanded_nodes_per_document": 16_384,
    "diagnostics": 256,
    "compiler_cache_entries": 64,
})

MAX_SOURCE_BYTES = DSL_RESOURCE_LIMITS["source_bytes"]
MAX_YAML_DOCUMENTS = DSL_RESOURCE_LIMITS["yaml_documents"]
MAX_RULES = DSL_RESOURCE_LIMITS["rules_per_document"]
MAX_DSL_SOURCE_ARTIFACTS = DSL_RESOURCE_LIMITS["dsl_source_artifacts_per_rule_set"]
MAX_MACROS = DSL_RESOURCE_LIMITS["macros_per_document"]
MAX_MACRO_PARAMETERS = DSL_RESOURCE_LIMITS["macro_parameters"]
MAX_MAPPING_ENTRIES = DSL_RESOURCE_LIMITS["mapping_entries"]
MAX_SEQUENCE_ELEMENTS = DSL_RESOURCE_LIMITS["sequence_elements"]
MAX_STRING_LENGTH = DSL_RESOURCE_LIMITS["string_code_points"]
MAX_IDENTIFIER_LENGTH = DSL_RESOURCE_LIMITS["identifier_code_points"]
MAX_SOURCE_ID_LENGTH = DSL_RESOURCE_LIMITS["source_id_code_points"]
MIN_INTEGER = DSL_RESOURCE_LIMITS["integer_minimum"]
MAX_INTEGER = DSL_RESOURCE_LIMITS["integer_maximum"]
MAX_DECIMAL_SIGNIFICANT_DIGITS = DSL_RESOURCE_LIMITS["decimal_significant_digits"]
MAX_DECIMAL_SCALE = DSL_RESOURCE_LIMITS["decimal_scale"]
MAX_DECIMAL_MAGNITUDE = DSL_RESOURCE_LIMITS["decimal_magnitude"]
MAX_AST_DEPTH = DSL_RESOURCE_LIMITS["source_ast_depth"]
MAX_AST_NODES_PER_RULE = DSL_RESOURCE_LIMITS["source_ast_nodes_per_rule"]
MAX_AST_NODES_PER_DOCUMENT = DSL_RESOURCE_LIMITS["source_ast_nodes_per_document"]
MAX_LOGICAL_CHILDREN = DSL_RESOURCE_LIMITS["logical_children_per_node"]
MAX_MACRO_EXPANSION_DEPTH = DSL_RESOURCE_LIMITS["macro_expansion_depth"]
MAX_EXPANDED_NODES_PER_RULE = DSL_RESOURCE_LIMITS["expanded_nodes_per_rule"]
MAX_EXPANDED_NODES_PER_DOCUMENT = DSL_RESOURCE_LIMITS["expanded_nodes_per_document"]
MAX_DIAGNOSTICS = DSL_RESOURCE_LIMITS["diagnostics"]
MAX_COMPILER_CACHE_ENTRIES = DSL_RESOURCE_LIMITS["compiler_cache_entries"]

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SAFE_CODE = re.compile(r"^P07E[0-9]{3}_[A-Z0-9_]+$")
_FIELD_PATH = re.compile(r"^\$[A-Za-z0-9_.\[\]-]*$")
_MODEL_COMPILER_TOKEN = object()


def _sha(value: Any, name: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


def _tuple_of(values: Any, item_type: type, name: str) -> tuple:
    if not isinstance(values, tuple) or any(not isinstance(item, item_type) for item in values):
        raise TypeError(f"{name} must be an immutable {item_type.__name__} tuple")
    return values


class _ImmutableArgumentMapping(Mapping[str, Any]):
    """Small source-AST mapping that can retain typed parameter references."""

    __slots__ = ("_items", "_lookup")

    def __init__(self, value: Mapping[str, Any]) -> None:
        def freeze_item(item: Any) -> Any:
            if isinstance(item, list):
                return tuple(freeze_item(child) for child in item)
            if isinstance(item, tuple):
                return tuple(freeze_item(child) for child in item)
            if isinstance(item, MacroParameterReference):
                return item
            return item

        self._items = tuple((key, freeze_item(item)) for key, item in value.items())
        self._lookup = dict(self._items)

    def __getitem__(self, key: str) -> Any:
        return self._lookup[key]

    def __iter__(self):
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)


def _immutable_arguments(value: Mapping[str, Any]) -> Mapping[str, Any]:
    def contains_reference(item: Any) -> bool:
        if isinstance(item, MacroParameterReference):
            return True
        if isinstance(item, (list, tuple)):
            return any(contains_reference(child) for child in item)
        return False

    if any(contains_reference(item) for item in value.values()):
        return _ImmutableArgumentMapping(value)
    return FrozenMapping(value, path="$.arguments")


def _argument_projection(value: Any) -> Any:
    if isinstance(value, MacroParameterReference):
        return {"parameter": value.name}
    if isinstance(value, tuple):
        return [_argument_projection(item) for item in value]
    if isinstance(value, CanonicalDecimal):
        return {"$decimal": value.value}
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceSpan:
    source_id: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, str) or not self.source_id or len(self.source_id) > MAX_SOURCE_ID_LENGTH:
            raise ValueError("source_id must be a bounded logical identity")
        positions = (self.start_line, self.start_column, self.end_line, self.end_column)
        if any(type(value) is not int or value < 1 for value in positions):
            raise ValueError("source span positions must be positive integers")
        if (self.end_line, self.end_column) < (self.start_line, self.start_column):
            raise ValueError("source span end must not precede its start")

    def logical_projection(self) -> FrozenMapping:
        return FrozenMapping({
            "source_id": self.source_id,
            "start_line": self.start_line,
            "start_column": self.start_column,
            "end_line": self.end_line,
            "end_column": self.end_column,
        })


@dataclass(frozen=True, slots=True, kw_only=True)
class CanonicalDecimal:
    """Exact bounded base-10 value; binary floats never define identity."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value:
            raise TypeError("canonical decimal value must be a string")
        try:
            parsed = Decimal(self.value)
        except InvalidOperation as exc:
            raise ValueError("canonical decimal value is invalid") from exc
        if not parsed.is_finite():
            raise ValueError("canonical decimal value must be finite")
        if parsed == 0 and self.value.startswith("-"):
            raise ValueError("negative decimal zero is forbidden")

    def logical_projection(self) -> FrozenMapping:
        return FrozenMapping({"$decimal": self.value})

    def as_float(self) -> float:
        return float(Decimal(self.value))


@dataclass(frozen=True, slots=True, kw_only=True)
class DslDiagnostic:
    code: str
    message: str
    stage: str
    source_id: str
    source_span: SourceSpan | None = None
    rule_id: str | None = None
    rule_revision: str | None = None
    macro_id: str | None = None
    node_id: str | None = None
    field_path: str = "$"
    details: Mapping[str, Any] = field(default_factory=dict)
    severity: str = "error"
    discovery_ordinal: int = field(default=0, repr=False, compare=False)
    rule_source_order: int = field(default=2**31 - 1, repr=False, compare=False)
    macro_source_order: int = field(default=2**31 - 1, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not _SAFE_CODE.fullmatch(self.code):
            raise ValueError("diagnostic code must be a Prompt-07 code")
        if not isinstance(self.message, str) or not self.message:
            raise ValueError("diagnostic message must be nonempty")
        if not isinstance(self.stage, str) or not self.stage:
            raise ValueError("diagnostic stage must be nonempty")
        if not isinstance(self.source_id, str) or not self.source_id:
            raise ValueError("diagnostic source_id must be nonempty")
        if self.source_span is not None and not isinstance(self.source_span, SourceSpan):
            raise TypeError("diagnostic source_span must be SourceSpan or None")
        if not isinstance(self.field_path, str) or not _FIELD_PATH.fullmatch(self.field_path):
            raise ValueError("diagnostic field_path must be safe and rooted")
        if self.severity != "error":
            raise ValueError("Prompt-07 diagnostics have error severity")
        object.__setattr__(self, "details", FrozenMapping(self.details, path="$.details"))

    def logical_projection(self) -> FrozenMapping:
        return FrozenMapping({
            "code": self.code,
            "message": self.message,
            "stage": self.stage,
            "source_id": self.source_id,
            "source_span": None if self.source_span is None else self.source_span.logical_projection(),
            "rule_id": self.rule_id,
            "rule_revision": self.rule_revision,
            "macro_id": self.macro_id,
            "node_id": self.node_id,
            "field_path": self.field_path,
            "details": self.details,
            "severity": self.severity,
        })


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilityReference:
    capability_id: str
    capability_version: str

    def logical_projection(self) -> FrozenMapping:
        return FrozenMapping({"id": self.capability_id, "version": self.capability_version})


@dataclass(frozen=True, slots=True, kw_only=True)
class MacroParameterReference:
    name: str

    def logical_projection(self) -> FrozenMapping:
        return FrozenMapping({"parameter": self.name})


@dataclass(frozen=True, slots=True, kw_only=True)
class PredicateBinding:
    predicate_id: str
    predicate_version: str
    arguments: Mapping[str, Any]
    parameter_schema_sha256: str
    definition_sha256: str
    required_capabilities: tuple[CapabilityReference, ...]
    system_scope: str

    def __post_init__(self) -> None:
        if not isinstance(self.arguments, Mapping):
            raise TypeError("binding arguments must be a mapping")
        object.__setattr__(self, "arguments", _immutable_arguments(self.arguments))
        _sha(self.parameter_schema_sha256, "parameter_schema_sha256")
        _sha(self.definition_sha256, "definition_sha256")
        _tuple_of(self.required_capabilities, CapabilityReference, "required_capabilities")

    def logical_projection(self) -> FrozenMapping:
        return FrozenMapping({
            "predicate_id": self.predicate_id,
            "predicate_version": self.predicate_version,
            "arguments": {key: _argument_projection(item) for key, item in self.arguments.items()},
            "parameter_schema_sha256": self.parameter_schema_sha256,
            "definition_sha256": self.definition_sha256,
            "required_capabilities": tuple(item.logical_projection() for item in self.required_capabilities),
            "system_scope": self.system_scope,
        })


@dataclass(frozen=True, slots=True, kw_only=True)
class PredicateCallNode:
    node_id: str
    source_span: SourceSpan
    predicate_id: str
    predicate_version: str
    arguments: Mapping[str, Any]
    binding: PredicateBinding | None
    required_capabilities: tuple[CapabilityReference, ...]
    static_result_type: str = "predicate_result"
    expansion_provenance: tuple[SourceSpan, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.arguments, Mapping):
            raise TypeError("predicate arguments must be a mapping")
        object.__setattr__(self, "arguments", _immutable_arguments(self.arguments))
        _tuple_of(self.required_capabilities, CapabilityReference, "required_capabilities")
        _tuple_of(self.expansion_provenance, SourceSpan, "expansion_provenance")
        if self.static_result_type != "predicate_result":
            raise ValueError("predicate nodes have predicate_result static type")


@dataclass(frozen=True, slots=True, kw_only=True)
class AllNode:
    node_id: str
    source_span: SourceSpan
    children: tuple["ExpressionNode", ...]
    static_result_type: str = "condition_result"
    expansion_provenance: tuple[SourceSpan, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.children, tuple) or not self.children:
            raise ValueError("all nodes require an immutable nonempty child tuple")
        _tuple_of(self.expansion_provenance, SourceSpan, "expansion_provenance")


@dataclass(frozen=True, slots=True, kw_only=True)
class AnyNode:
    node_id: str
    source_span: SourceSpan
    children: tuple["ExpressionNode", ...]
    static_result_type: str = "condition_result"
    expansion_provenance: tuple[SourceSpan, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.children, tuple) or not self.children:
            raise ValueError("any nodes require an immutable nonempty child tuple")
        _tuple_of(self.expansion_provenance, SourceSpan, "expansion_provenance")


@dataclass(frozen=True, slots=True, kw_only=True)
class NotNode:
    node_id: str
    source_span: SourceSpan
    child: "ExpressionNode"
    static_result_type: str = "condition_result"
    expansion_provenance: tuple[SourceSpan, ...] = ()

    def __post_init__(self) -> None:
        _tuple_of(self.expansion_provenance, SourceSpan, "expansion_provenance")


@dataclass(frozen=True, slots=True, kw_only=True)
class MacroCallNode:
    node_id: str
    source_span: SourceSpan
    macro_id: str
    macro_revision: str
    arguments: Mapping[str, Any]
    static_result_type: str = "condition_result"
    expansion_provenance: tuple[SourceSpan, ...] = ()

    def __post_init__(self) -> None:
        # Macro source arguments may contain typed MacroParameterReference values,
        # which are intentionally outside the generic canonical freezer.
        if not isinstance(self.arguments, Mapping):
            raise TypeError("macro arguments must be a mapping")
        object.__setattr__(self, "arguments", _immutable_arguments(self.arguments))
        _tuple_of(self.expansion_provenance, SourceSpan, "expansion_provenance")


ExpressionNode: TypeAlias = PredicateCallNode | AllNode | AnyNode | NotNode | MacroCallNode
ExpandedExpressionNode: TypeAlias = PredicateCallNode | AllNode | AnyNode | NotNode


@dataclass(frozen=True, slots=True, kw_only=True)
class MacroParameter:
    name: str
    parameter_type: str
    source_span: SourceSpan


@dataclass(frozen=True, slots=True, kw_only=True)
class MacroDeclaration:
    macro_id: str
    revision: str
    parameters: tuple[MacroParameter, ...]
    body: ExpressionNode
    source_span: SourceSpan
    source_order: int
    label: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        _tuple_of(self.parameters, MacroParameter, "parameters")


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleDeclaration:
    rule_id: str
    revision: str
    family: str
    category: str
    domains: tuple[str, ...]
    label: str
    priority: int
    base_weight: CanonicalDecimal
    context: str
    requires: tuple[CapabilityReference, ...]
    evidence_mode: str
    when: ExpressionNode
    source_span: SourceSpan
    source_order: int
    quality: CanonicalDecimal | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    presentation: Mapping[str, Any] = field(default_factory=dict)
    governance_ref: str | None = None

    def __post_init__(self) -> None:
        _tuple_of(self.domains, str, "domains")
        _tuple_of(self.requires, CapabilityReference, "requires")
        object.__setattr__(self, "provenance", FrozenMapping(self.provenance, path="$.provenance"))
        object.__setattr__(self, "presentation", FrozenMapping(self.presentation, path="$.presentation"))


@dataclass(frozen=True, slots=True, kw_only=True)
class DslDocument:
    dsl: str
    dsl_version: str
    system: str
    rule_set_family: str
    rule_set_version: str
    macros: tuple[MacroDeclaration, ...]
    rules: tuple[RuleDeclaration, ...]
    source_id: str
    source_span: SourceSpan

    def __post_init__(self) -> None:
        _tuple_of(self.macros, MacroDeclaration, "macros")
        _tuple_of(self.rules, RuleDeclaration, "rules")


@dataclass(frozen=True, slots=True, kw_only=True)
class MacroExpansionTrace:
    macro_id: str
    macro_revision: str
    call_node_id: str
    call_span: SourceSpan
    definition_span: SourceSpan
    canonical_arguments_sha256: str
    expansion_ordinal: int
    expanded_root_node_id: str

    def __post_init__(self) -> None:
        _sha(self.canonical_arguments_sha256, "canonical_arguments_sha256")
        if type(self.expansion_ordinal) is not int or self.expansion_ordinal < 0:
            raise ValueError("expansion_ordinal must be nonnegative")


@dataclass(frozen=True, slots=True, kw_only=True)
class AnalyzedRule:
    resolved_rule: ResolvedRule
    expanded_condition_ast: ExpandedExpressionNode
    lowered_condition: FrozenMapping
    predicate_bindings: tuple[PredicateBinding, ...]
    required_capabilities: tuple[CapabilityReference, ...]
    expanded_ast_sha256: str
    compiled_semantic_sha256: str
    semantic_contract: Mapping[str, Any]
    macro_expansion_trace: tuple[MacroExpansionTrace, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.resolved_rule, ResolvedRule):
            raise TypeError("resolved_rule must be the existing ResolvedRule")
        if not isinstance(self.lowered_condition, FrozenMapping):
            object.__setattr__(self, "lowered_condition", FrozenMapping(self.lowered_condition))
        _tuple_of(self.predicate_bindings, PredicateBinding, "predicate_bindings")
        _tuple_of(self.required_capabilities, CapabilityReference, "required_capabilities")
        _tuple_of(self.macro_expansion_trace, MacroExpansionTrace, "macro_expansion_trace")
        _sha(self.expanded_ast_sha256, "expanded_ast_sha256")
        _sha(self.compiled_semantic_sha256, "compiled_semantic_sha256")
        object.__setattr__(self, "semantic_contract", FrozenMapping(self.semantic_contract))


@dataclass(frozen=True, slots=True, kw_only=True)
class AnalyzedRuleSet:
    document: DslDocument
    rules: tuple[AnalyzedRule, ...]
    source_file_sha256: str
    canonical_dsl_sha256: str
    expanded_ast_sha256: str
    compiled_rule_set_sha256: str
    canonical_dsl_projection: FrozenMapping

    def __post_init__(self) -> None:
        _tuple_of(self.rules, AnalyzedRule, "rules")
        for name in ("source_file_sha256", "canonical_dsl_sha256", "expanded_ast_sha256", "compiled_rule_set_sha256"):
            _sha(getattr(self, name), name)
        if not isinstance(self.canonical_dsl_projection, FrozenMapping):
            object.__setattr__(self, "canonical_dsl_projection", FrozenMapping(self.canonical_dsl_projection))

    def logical_projection(self) -> FrozenMapping:
        return FrozenMapping({
            "system": self.document.system,
            "rule_set_family": self.document.rule_set_family,
            "rule_set_version": self.document.rule_set_version,
            "canonical_dsl_sha256": self.canonical_dsl_sha256,
            "expanded_ast_sha256": self.expanded_ast_sha256,
            "compiled_rule_set_sha256": self.compiled_rule_set_sha256,
            "rules": tuple({
                "rule_id": item.resolved_rule.rule_id,
                "revision": item.resolved_rule.rule_version,
                "expanded_ast_sha256": item.expanded_ast_sha256,
                "compiled_semantic_sha256": item.compiled_semantic_sha256,
                "lowered_condition": item.lowered_condition,
            } for item in self.rules),
        })


@dataclass(frozen=True, slots=True, kw_only=True)
class CompiledRule:
    compiled_rule_schema_version: str
    resolved_rule: ResolvedRule
    expanded_condition_ast: ExpandedExpressionNode
    lowered_condition: FrozenMapping
    predicate_bindings: tuple[PredicateBinding, ...]
    required_capabilities: tuple[CapabilityReference, ...]
    source_identity: str
    source_file_sha256: str
    canonical_dsl_sha256: str
    expanded_ast_sha256: str
    compiled_semantic_sha256: str
    macro_expansion_trace: tuple[MacroExpansionTrace, ...]
    resolved_versions: Any = field(repr=False, compare=False)
    _factory_token: InitVar[object | None] = None
    _compiler_seal: object = field(init=False, repr=False, compare=False)

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _MODEL_COMPILER_TOKEN:
            raise ValueError("CompiledRule requires RuleDslCompiler")
        if self.compiled_rule_schema_version != COMPILED_RULE_SET_SCHEMA_VERSION:
            raise ValueError("unsupported compiled rule schema version")
        if not isinstance(self.resolved_rule, ResolvedRule) or not isinstance(self.lowered_condition, FrozenMapping):
            raise TypeError("compiled rule lowering fields are invalid")
        _tuple_of(self.predicate_bindings, PredicateBinding, "predicate_bindings")
        _tuple_of(self.required_capabilities, CapabilityReference, "required_capabilities")
        _tuple_of(self.macro_expansion_trace, MacroExpansionTrace, "macro_expansion_trace")
        for name in ("source_file_sha256", "canonical_dsl_sha256", "expanded_ast_sha256", "compiled_semantic_sha256"):
            _sha(getattr(self, name), name)
        object.__setattr__(self, "_compiler_seal", _MODEL_COMPILER_TOKEN)

    def is_compiler_sealed(self) -> bool:
        return self._compiler_seal is _MODEL_COMPILER_TOKEN

    def __copy__(self):
        raise TypeError("sealed compiled rules cannot be copied")

    def __deepcopy__(self, memo):
        raise TypeError("sealed compiled rules cannot be copied")

    def logical_projection(self) -> FrozenMapping:
        return FrozenMapping({
            "compiled_rule_schema_version": self.compiled_rule_schema_version,
            "rule_id": self.resolved_rule.rule_id,
            "revision": self.resolved_rule.rule_version,
            "source_identity": self.source_identity,
            "source_file_sha256": self.source_file_sha256,
            "canonical_dsl_sha256": self.canonical_dsl_sha256,
            "expanded_ast_sha256": self.expanded_ast_sha256,
            "compiled_semantic_sha256": self.compiled_semantic_sha256,
            "lowered_condition": self.lowered_condition,
            "predicate_bindings": tuple(item.logical_projection() for item in self.predicate_bindings),
            "required_capabilities": tuple(item.logical_projection() for item in self.required_capabilities),
        })


@dataclass(frozen=True, slots=True, kw_only=True)
class CompiledRuleSet:
    compiled_rule_set_schema_version: str
    system: str
    rule_set_family: str
    rule_set_version: str
    source_identity: str
    source_file_sha256: str
    canonical_dsl_sha256: str
    expanded_ast_sha256: str
    compiled_rule_set_sha256: str
    rules: tuple[CompiledRule, ...]
    resolved_versions: Any = field(repr=False, compare=False)
    compiler_identity: str
    compiler_version: str
    compiler_content_sha256: str
    manifest_fingerprint_sha256: str
    _factory_token: InitVar[object | None] = None
    _compiler_seal: object = field(init=False, repr=False, compare=False)

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _MODEL_COMPILER_TOKEN:
            raise ValueError("CompiledRuleSet requires RuleDslCompiler")
        if self.compiled_rule_set_schema_version != COMPILED_RULE_SET_SCHEMA_VERSION:
            raise ValueError("unsupported compiled rule-set schema version")
        _tuple_of(self.rules, CompiledRule, "rules")
        for name in ("source_file_sha256", "canonical_dsl_sha256", "expanded_ast_sha256", "compiled_rule_set_sha256", "compiler_content_sha256", "manifest_fingerprint_sha256"):
            _sha(getattr(self, name), name)
        object.__setattr__(self, "_compiler_seal", _MODEL_COMPILER_TOKEN)

    def is_compiler_sealed(self) -> bool:
        return self._compiler_seal is _MODEL_COMPILER_TOKEN

    def __copy__(self):
        raise TypeError("sealed compiled rule sets cannot be copied")

    def __deepcopy__(self, memo):
        raise TypeError("sealed compiled rule sets cannot be copied")

    def logical_projection(self) -> FrozenMapping:
        return FrozenMapping({
            "compiled_rule_set_schema_version": self.compiled_rule_set_schema_version,
            "system": self.system,
            "rule_set_family": self.rule_set_family,
            "rule_set_version": self.rule_set_version,
            "source_identity": self.source_identity,
            "source_file_sha256": self.source_file_sha256,
            "canonical_dsl_sha256": self.canonical_dsl_sha256,
            "expanded_ast_sha256": self.expanded_ast_sha256,
            "compiled_rule_set_sha256": self.compiled_rule_set_sha256,
            "compiler_identity": self.compiler_identity,
            "compiler_version": self.compiler_version,
            "compiler_content_sha256": self.compiler_content_sha256,
            "manifest_fingerprint_sha256": self.manifest_fingerprint_sha256,
            "rules": tuple({
                "rule_id": item.resolved_rule.rule_id,
                "revision": item.resolved_rule.rule_version,
                "expanded_ast_sha256": item.expanded_ast_sha256,
                "compiled_semantic_sha256": item.compiled_semantic_sha256,
                "lowered_condition": item.lowered_condition,
            } for item in self.rules),
        })


@dataclass(frozen=True, slots=True, kw_only=True)
class AnalysisSucceeded:
    analyzed_rule_set: AnalyzedRuleSet
    diagnostics: tuple[DslDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.analyzed_rule_set, AnalyzedRuleSet) or self.diagnostics:
            raise ValueError("successful analysis requires one rule set and no diagnostics")


@dataclass(frozen=True, slots=True, kw_only=True)
class CompilationSucceeded:
    compiled_rule_set: CompiledRuleSet
    diagnostics: tuple[DslDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.compiled_rule_set, CompiledRuleSet) or self.diagnostics:
            raise ValueError("successful compilation requires one rule set and no diagnostics")


@dataclass(frozen=True, slots=True, kw_only=True)
class CompilationFailed:
    compiled_rule_set: None
    diagnostics: tuple[DslDiagnostic, ...]

    def __post_init__(self) -> None:
        if self.compiled_rule_set is not None or not self.diagnostics:
            raise ValueError("failed compilation requires diagnostics and no rule set")
        _tuple_of(self.diagnostics, DslDiagnostic, "diagnostics")


def _new_compiled_rule(**fields: Any) -> CompiledRule:
    return CompiledRule(**fields, _factory_token=_MODEL_COMPILER_TOKEN)


def _new_compiled_rule_set(**fields: Any) -> CompiledRuleSet:
    return CompiledRuleSet(**fields, _factory_token=_MODEL_COMPILER_TOKEN)


__all__ = (
    "AllNode", "AnalysisSucceeded", "AnalyzedRule", "AnalyzedRuleSet", "AnyNode",
    "CanonicalDecimal", "CapabilityReference", "CompilationFailed", "CompilationSucceeded",
    "CompiledRule", "CompiledRuleSet", "DslDiagnostic", "DslDocument", "ExpressionNode",
    "ExpandedExpressionNode", "MacroCallNode", "MacroDeclaration", "MacroExpansionTrace",
    "MacroParameter", "MacroParameterReference", "NotNode", "PredicateBinding",
    "PredicateCallNode", "RuleDeclaration", "SourceSpan",
    "DSL_SCHEMA_VERSION", "COMPILED_RULE_SET_SCHEMA_VERSION", "DSL_RESOURCE_LIMITS",
    "MAX_SOURCE_BYTES", "MAX_YAML_DOCUMENTS", "MAX_DSL_SOURCE_ARTIFACTS",
    "MAX_RULES", "MAX_MACROS", "MAX_MACRO_PARAMETERS", "MAX_MAPPING_ENTRIES",
    "MAX_SEQUENCE_ELEMENTS", "MAX_STRING_LENGTH", "MAX_IDENTIFIER_LENGTH",
    "MAX_SOURCE_ID_LENGTH", "MIN_INTEGER", "MAX_INTEGER",
    "MAX_DECIMAL_SIGNIFICANT_DIGITS", "MAX_DECIMAL_SCALE", "MAX_DECIMAL_MAGNITUDE",
    "MAX_AST_DEPTH", "MAX_AST_NODES_PER_RULE",
    "MAX_AST_NODES_PER_DOCUMENT", "MAX_MACRO_EXPANSION_DEPTH",
    "MAX_EXPANDED_NODES_PER_RULE", "MAX_EXPANDED_NODES_PER_DOCUMENT",
    "MAX_LOGICAL_CHILDREN", "MAX_DIAGNOSTICS", "MAX_COMPILER_CACHE_ENTRIES",
)
