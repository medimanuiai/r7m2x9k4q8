"""Single deterministic compiler owner for the bounded Prompt-07 Rule DSL."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping, Sequence
from dataclasses import replace
import hashlib
import re
from typing import Any

from systems.Parasara.engine.rules.canonical import FrozenMapping, canonical_json_bytes
from systems.Parasara.engine.rules.capabilities import (
    CapabilityCatalogMiss,
    get_production_capability_catalog,
)
from systems.Parasara.engine.rules.definition_validation import (
    RuleSourceIdentity,
    validate_condition_definition,
)
from systems.Parasara.engine.rules.dsl.models import (
    AllNode,
    AnalysisSucceeded,
    AnalyzedRule,
    AnalyzedRuleSet,
    AnyNode,
    CanonicalDecimal,
    CapabilityReference,
    CompilationFailed,
    CompilationSucceeded,
    COMPILED_RULE_SET_SCHEMA_VERSION,
    DslDiagnostic,
    DslDocument,
    DSL_RESOURCE_LIMITS,
    DSL_SCHEMA_VERSION,
    ExpressionNode,
    MacroCallNode,
    MacroDeclaration,
    MacroExpansionTrace,
    MacroParameter,
    MacroParameterReference,
    MAX_AST_DEPTH,
    MAX_AST_NODES_PER_DOCUMENT,
    MAX_AST_NODES_PER_RULE,
    MAX_COMPILER_CACHE_ENTRIES,
    MAX_DIAGNOSTICS,
    MAX_EXPANDED_NODES_PER_DOCUMENT,
    MAX_EXPANDED_NODES_PER_RULE,
    MAX_IDENTIFIER_LENGTH,
    MAX_INTEGER,
    MAX_LOGICAL_CHILDREN,
    MAX_MACRO_EXPANSION_DEPTH,
    MAX_MACRO_PARAMETERS,
    MAX_MACROS,
    MAX_RULES,
    MAX_SEQUENCE_ELEMENTS,
    MAX_SOURCE_BYTES,
    MAX_SOURCE_ID_LENGTH,
    MIN_INTEGER,
    NotNode,
    PredicateBinding,
    PredicateCallNode,
    RuleDeclaration,
    SourceSpan,
    _new_compiled_rule,
    _new_compiled_rule_set,
)
from systems.Parasara.engine.rules.dsl.parser import ParsedYaml, ParsedYamlFailed, parse_yaml_source
from systems.Parasara.engine.rules.evaluator import predicate_definition_fingerprint_sha256
from systems.Parasara.engine.rules.parameters import (
    CANONICAL_PLANETS,
    FUNCTIONAL_ROLE_VALUES,
    ParameterIssueCode,
)
from systems.Parasara.engine.rules.registry import (
    get_production_registry,
    predicate_registry_fingerprint_sha256,
)
from systems.Parasara.engine.rules.rule_engine import ResolvedRule


DSL_COMPILER_IDENTITY = "parashara-rule-dsl-compiler"
DSL_COMPILER_VERSION = "1.0.0"
DSL_COMPATIBILITY_CONTRACT = "resolved-rule+condition@1.0.0"
DSL_CANONICALIZATION_CONTRACT = "parasara-rule-dsl-canonical@1.0.0"
DSL_MACRO_EXPANSION_CONTRACT = "parasara-rule-macro-expansion@1.0.0"

_LOWER_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")
_GENERAL_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.@/-]{0,127}$")
_RULE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.{}<>-]{0,127}$")
_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_PREDICATE_ID = re.compile(r"^[A-Z][A-Z0-9_]*$")
_CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
_PARAMETER_NAME = re.compile(r"^[a-z][a-z0-9_]*$")

_STAGE_ORDINAL = {
    "source": 0,
    "parse": 1,
    "schema": 2,
    "ast": 3,
    "binding": 4,
    "macro": 5,
    "expanded": 6,
    "canonicalization": 7,
    "authorization": 8,
}

_MESSAGES = {
    "P07E101_UNKNOWN_FIELD": "A mapping contains a field outside its exact DSL schema.",
    "P07E102_MISSING_FIELD": "A required DSL field is absent.",
    "P07E103_INVALID_FIELD_VALUE": "A DSL value violates its field contract.",
    "P07E104_INVALID_NUMERIC_VALUE": "A numeric value violates its canonical range.",
    "P07E105_DUPLICATE_RULE_REVISION": "A rule ID and revision pair is duplicated.",
    "P07E201_UNKNOWN_OPERATOR": "The expression operator is not supported by DSL 1.0.0.",
    "P07E202_AST_DEPTH_LIMIT": "The expression depth exceeds the bounded AST limit.",
    "P07E203_AST_NODE_LIMIT": "The expression node count exceeds the bounded AST limit.",
    "P07E211_UNKNOWN_PREDICATE": "The predicate ID is not a canonical registered predicate.",
    "P07E212_PREDICATE_VERSION_MISMATCH": "The predicate version does not match the registered definition.",
    "P07E213_INVALID_ARGUMENT_NAME": "Predicate arguments do not match canonical parameter names.",
    "P07E214_ARGUMENT_TYPE_MISMATCH": "A predicate argument does not satisfy its registered type.",
    "P07E215_PREDICATE_CAPABILITY_MISMATCH": "Predicate capabilities do not match the registry, catalog, or rule assertion.",
    "P07E301_DUPLICATE_MACRO_REVISION": "A macro ID and revision pair is duplicated.",
    "P07E302_MACRO_NOT_FOUND": "The exact macro ID and revision is not declared.",
    "P07E303_MACRO_ARGUMENT_MISMATCH": "Macro arguments do not match its declared parameters.",
    "P07E304_MACRO_ARGUMENT_TYPE_MISMATCH": "A macro argument does not satisfy its declared type.",
    "P07E305_MACRO_PARAMETER_NOT_FOUND": "A macro body references an undeclared parameter.",
    "P07E306_MACRO_DIRECT_RECURSION": "A macro directly invokes itself.",
    "P07E307_MACRO_CYCLE": "The macro call graph contains an indirect cycle.",
    "P07E308_MACRO_EXPANSION_DEPTH_LIMIT": "Macro expansion exceeds the maximum nested call depth.",
    "P07E309_MACRO_EXPANDED_NODE_LIMIT": "Macro expansion exceeds the bounded node budget.",
    "P07E401_COMPILER_VERSION_MISMATCH": "The selected manifest does not pin this DSL compiler contract.",
    "P07E402_MANIFEST_AUTHORIZATION_FAILURE": "The resolved Prompt-06 authority does not authorize this DSL operation.",
    "P07E403_SOURCE_DIGEST_MISMATCH": "The canonical DSL digest differs from the authorized source artifact.",
    "P07E404_COMPILED_DIGEST_MISMATCH": "Expanded or compiled semantics differ from the authorized manifest.",
    "P07E999_DIAGNOSTIC_LIMIT": "Additional diagnostics were deterministically suppressed.",
}

DSL_COMPILER_IMPLEMENTATION_MODULE_IDS = (
    "dsl/models.py",
    "dsl/parser.py",
    "dsl/compiler.py",
)
_COMPILER_DIGEST_LITERAL = re.compile(
    r'^DSL_COMPILER_CONTENT_SHA256 = "[0-9a-f]{64}"$',
    flags=re.MULTILINE,
)

DSL_COMPILER_CONTRACT_DATA = FrozenMapping({
    "identity": DSL_COMPILER_IDENTITY,
    "version": DSL_COMPILER_VERSION,
    "compatibility_contract": DSL_COMPATIBILITY_CONTRACT,
    "dsl_schema_version": DSL_SCHEMA_VERSION,
    "compiled_artifact_schema_version": COMPILED_RULE_SET_SCHEMA_VERSION,
    "canonicalization_contract": DSL_CANONICALIZATION_CONTRACT,
    "macro_expansion_contract": DSL_MACRO_EXPANSION_CONTRACT,
    "grammar": {
        "capability_id": _CAPABILITY_ID.pattern,
        "general_identifier": _GENERAL_IDENTIFIER.pattern,
        "lower_identifier": _LOWER_IDENTIFIER.pattern,
        "parameter_name": _PARAMETER_NAME.pattern,
        "predicate_id": _PREDICATE_ID.pattern,
        "rule_id": _RULE_ID.pattern,
        "semver": _SEMVER.pattern,
    },
    "operators": ("all", "any", "macro", "not", "predicate"),
    "parameter_adapters": {
        "house": {"minimum": 1, "maximum": 12},
        "planet": {"canonical_values": CANONICAL_PLANETS, "casefold": True, "strip": True},
        "role_collection": {
            "canonical_values": FUNCTIONAL_ROLE_VALUES,
            "nonempty": True,
            "sorted_unique": True,
        },
    },
    "resource_limits": DSL_RESOURCE_LIMITS,
    "scalar_contract": {
        "booleans": ("false", "true"),
        "decimal_pattern": r"-?(0|[1-9][0-9]*)\.[0-9]+",
        "integer_pattern": r"0|-?[1-9][0-9]*",
        "negative_zero_rejected": True,
        "quoted_scalars_are_strings": True,
    },
    "stage_order": _STAGE_ORDINAL,
})
_COMPILER_CONTRACT_DATA = DSL_COMPILER_CONTRACT_DATA


def compiler_component_fingerprint_sha256(
    module_sources: Mapping[str, bytes | str],
    *,
    contract_data: Mapping[str, Any] = DSL_COMPILER_CONTRACT_DATA,
) -> str:
    """Fingerprint normalized implementation sources plus locked contracts.

    The helper is deliberately pure: callers provide logical module IDs and
    contents, so no CWD, absolute path, environment, or filesystem state can
    enter the component identity. The published digest line is self-masked to
    avoid a circular source hash.
    """

    if not isinstance(module_sources, Mapping) or tuple(sorted(module_sources)) != tuple(
        sorted(DSL_COMPILER_IMPLEMENTATION_MODULE_IDS)
    ):
        raise ValueError("module_sources must contain the exact compiler implementation module IDs")
    modules = []
    for module_id in DSL_COMPILER_IMPLEMENTATION_MODULE_IDS:
        payload = module_sources[module_id]
        if isinstance(payload, bytes):
            text = payload.decode("utf-8", errors="strict")
        elif isinstance(payload, str):
            text = payload
        else:
            raise TypeError("compiler module source must be bytes or str")
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        if module_id == "dsl/compiler.py":
            normalized, replacements = _COMPILER_DIGEST_LITERAL.subn(
                'DSL_COMPILER_CONTENT_SHA256 = "<SELF>"', normalized
            )
            if replacements != 1:
                raise ValueError("compiler source must contain one published digest literal")
        modules.append({
            "module_id": module_id,
            "content_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        })
    projection = {
        "compiler_contract": contract_data,
        "implementation_modules": modules,
    }
    return hashlib.sha256(canonical_json_bytes(projection)).hexdigest()


DSL_COMPILER_CONTENT_SHA256 = "c23b99b54b825f45c94dc0120cb2110451da4eaf44193b5fe91172d7e0d1f1ff"


class _DiagnosticCollector:
    __slots__ = ("source_id", "_items", "_ordinal", "_suppressed")

    def __init__(self, source_id: str) -> None:
        self.source_id = source_id
        self._items: list[DslDiagnostic] = []
        self._ordinal = 0
        self._suppressed = False

    def add(
        self,
        code: str,
        *,
        stage: str,
        field_path: str,
        span: SourceSpan | None = None,
        rule: RuleDeclaration | None = None,
        macro: MacroDeclaration | None = None,
        node_id: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        if len(self._items) >= MAX_DIAGNOSTICS - 1:
            self._suppressed = True
            self._ordinal += 1
            return
        self._items.append(DslDiagnostic(
            code=code,
            message=_MESSAGES[code],
            stage=stage,
            source_id=self.source_id,
            source_span=span,
            rule_id=None if rule is None else rule.rule_id,
            rule_revision=None if rule is None else rule.revision,
            macro_id=None if macro is None else macro.macro_id,
            node_id=node_id,
            field_path=field_path,
            details={} if details is None else details,
            discovery_ordinal=self._ordinal,
            rule_source_order=2**31 - 1 if rule is None else rule.source_order,
            macro_source_order=2**31 - 1 if macro is None else macro.source_order,
        ))
        self._ordinal += 1

    def finish(self) -> tuple[DslDiagnostic, ...]:
        items = sorted(self._items, key=lambda item: (
            _STAGE_ORDINAL[item.stage],
            item.source_id,
            2**31 - 1 if item.source_span is None else item.source_span.start_line,
            2**31 - 1 if item.source_span is None else item.source_span.start_column,
            item.rule_source_order,
            item.macro_source_order,
            item.code,
            item.field_path,
            item.discovery_ordinal,
        ))
        if self._suppressed:
            items = items[: MAX_DIAGNOSTICS - 1]
            items.append(DslDiagnostic(
                code="P07E999_DIAGNOSTIC_LIMIT",
                message=_MESSAGES["P07E999_DIAGNOSTIC_LIMIT"],
                stage="canonicalization",
                source_id=self.source_id,
                field_path="$",
                details={"limit": MAX_DIAGNOSTICS},
                discovery_ordinal=self._ordinal,
            ))
        return tuple(items)

    @property
    def has_errors(self) -> bool:
        return bool(self._items) or self._suppressed

    @property
    def has_errors(self) -> bool:
        return bool(self._items) or self._suppressed


def _value_data(value: Any) -> Any:
    if isinstance(value, CanonicalDecimal):
        return {"$decimal": value.value}
    if isinstance(value, MacroParameterReference):
        return {"parameter": value.name}
    if isinstance(value, Mapping):
        return {key: _value_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_value_data(item) for item in value]
    return value


def _capability_data(values: tuple[CapabilityReference, ...]) -> list[dict[str, str]]:
    return [{"id": item.capability_id, "version": item.capability_version} for item in values]


def _binding_data(value: PredicateBinding) -> dict[str, Any]:
    return dict(value.logical_projection())


def _ast_data(node: ExpressionNode, *, include_macro: bool = True) -> dict[str, Any]:
    if isinstance(node, PredicateCallNode):
        output = {
            "kind": "predicate",
            "predicate_id": node.predicate_id,
            "predicate_version": node.predicate_version,
            "arguments": _value_data(node.arguments),
            "required_capabilities": _capability_data(node.required_capabilities),
        }
        if node.binding is not None:
            output["binding_sha256"] = hashlib.sha256(
                canonical_json_bytes(_binding_data(node.binding))
            ).hexdigest()
        return output
    if isinstance(node, AllNode):
        return {"kind": "all", "children": [_ast_data(item, include_macro=include_macro) for item in node.children]}
    if isinstance(node, AnyNode):
        return {"kind": "any", "children": [_ast_data(item, include_macro=include_macro) for item in node.children]}
    if isinstance(node, NotNode):
        return {"kind": "not", "child": _ast_data(node.child, include_macro=include_macro)}
    if isinstance(node, MacroCallNode) and include_macro:
        return {
            "kind": "macro",
            "macro_id": node.macro_id,
            "macro_revision": node.macro_revision,
            "arguments": _value_data(node.arguments),
        }
    raise TypeError("expanded AST cannot contain macro calls")


def _document_data(document: DslDocument) -> dict[str, Any]:
    def macro_data(item: MacroDeclaration) -> dict[str, Any]:
        output = {
            "id": item.macro_id,
            "revision": item.revision,
            "parameters": [{"name": value.name, "type": value.parameter_type} for value in item.parameters],
            "body": _ast_data(item.body),
        }
        if item.label is not None:
            output["label"] = item.label
        if item.description is not None:
            output["description"] = item.description
        return output

    def rule_data(item: RuleDeclaration) -> dict[str, Any]:
        output = {
            "id": item.rule_id,
            "revision": item.revision,
            "family": item.family,
            "category": item.category,
            "domains": list(item.domains),
            "label": item.label,
            "priority": item.priority,
            "base_weight": _value_data(item.base_weight),
            "context": item.context,
            "requires": _capability_data(item.requires),
            "evidence": {"mode": item.evidence_mode},
            "when": _ast_data(item.when),
        }
        if item.quality is not None:
            output["quality"] = _value_data(item.quality)
        if item.provenance:
            output["provenance"] = dict(item.provenance)
        if item.presentation:
            output["presentation"] = dict(item.presentation)
        if item.governance_ref is not None:
            output["governance_ref"] = item.governance_ref
        return output

    return {
        "dsl": document.dsl,
        "dsl_version": document.dsl_version,
        "system": document.system,
        "rule_set": {"family": document.rule_set_family, "version": document.rule_set_version},
        "macros": [macro_data(item) for item in document.macros],
        "rules": [rule_data(item) for item in document.rules],
    }


def _source_id_valid(source_id: Any) -> bool:
    if not isinstance(source_id, str) or not source_id or len(source_id) > MAX_SOURCE_ID_LENGTH:
        return False
    if not source_id.endswith(".yaml") or "\\" in source_id or source_id.startswith("/") or ":" in source_id:
        return False
    parts = source_id.split("/")
    return all(part not in {"", ".", ".."} for part in parts)


class _Analyzer:
    _ROOT_FIELDS = ("dsl", "dsl_version", "system", "rule_set", "macros", "rules")
    _RULE_FIELDS = (
        "id", "revision", "family", "category", "domains", "label", "priority",
        "base_weight", "context", "requires", "evidence", "when", "quality",
        "provenance", "presentation", "governance_ref",
    )
    _REQUIRED_RULE_FIELDS = _RULE_FIELDS[:12]
    _MACRO_FIELDS = ("id", "revision", "parameters", "body", "label", "description")
    _PROVENANCE_FIELDS = (
        "source_ref", "source_title", "edition", "chapter", "section", "verse",
        "translation", "interpretive_notes", "tradition_profile", "author_id", "reviewer_id",
    )
    _PRESENTATION_FIELDS = ("description", "narrative_key", "tags")

    def __init__(self, *, source_id: str, parsed: ParsedYaml, payload: bytes) -> None:
        self.source_id = source_id
        self.parsed = parsed
        self.payload = payload
        self.diagnostics = _DiagnosticCollector(source_id)
        self.source_node_count = 0
        self.expanded_node_count = 0
        self.registry = get_production_registry()
        self.catalog = get_production_capability_catalog()

    def span(self, path: str) -> SourceSpan | None:
        return self.parsed.span_for(path)

    def issue(self, code: str, path: str, stage: str = "schema", **kwargs: Any) -> None:
        self.diagnostics.add(code, stage=stage, field_path=path, span=self.span(path), **kwargs)

    def check_mapping(
        self,
        value: Any,
        *,
        path: str,
        fields: Sequence[str],
        required: Sequence[str],
    ) -> Mapping[str, Any] | None:
        if not isinstance(value, Mapping):
            self.issue("P07E103_INVALID_FIELD_VALUE", path)
            return None
        for name in required:
            if name not in value:
                self.issue("P07E102_MISSING_FIELD", f"{path}.{name}")
        for name in sorted(set(value) - set(fields)):
            self.issue("P07E101_UNKNOWN_FIELD", f"{path}.{name}")
        return value

    def text(self, value: Any, *, path: str, pattern: re.Pattern[str] | None = None) -> str | None:
        if not isinstance(value, str) or not value or len(value) > MAX_IDENTIFIER_LENGTH or value != value.strip():
            self.issue("P07E103_INVALID_FIELD_VALUE", path)
            return None
        if pattern is not None and not pattern.fullmatch(value):
            self.issue("P07E103_INVALID_FIELD_VALUE", path)
            return None
        return value

    def sequence(self, value: Any, *, path: str, maximum: int, nonempty: bool = False) -> list[Any] | None:
        if not isinstance(value, list) or (nonempty and not value) or len(value) > maximum:
            self.issue("P07E103_INVALID_FIELD_VALUE", path)
            return None
        return value

    def capability_refs(self, value: Any, path: str) -> tuple[CapabilityReference, ...]:
        rows = self.sequence(value, path=path, maximum=MAX_SEQUENCE_ELEMENTS)
        if rows is None:
            return ()
        output: list[CapabilityReference] = []
        for index, row in enumerate(rows):
            item_path = f"{path}[{index}]"
            mapping = self.check_mapping(row, path=item_path, fields=("id", "version"), required=("id", "version"))
            if mapping is None or "id" not in mapping or "version" not in mapping:
                continue
            capability_id = self.text(mapping["id"], path=f"{item_path}.id", pattern=_CAPABILITY_ID)
            version = self.text(mapping["version"], path=f"{item_path}.version", pattern=_SEMVER)
            if capability_id is not None and version is not None:
                output.append(CapabilityReference(capability_id=capability_id, capability_version=version))
        pairs = tuple((item.capability_id, item.capability_version) for item in output)
        if pairs != tuple(sorted(set(pairs))):
            self.issue("P07E103_INVALID_FIELD_VALUE", path)
        return tuple(output)

    def argument_value(self, value: Any, path: str, *, allow_parameter: bool) -> Any | None:
        if isinstance(value, Mapping):
            if allow_parameter and set(value) == {"parameter"}:
                name = self.text(value["parameter"], path=f"{path}.parameter", pattern=_PARAMETER_NAME)
                return None if name is None else MacroParameterReference(name=name)
            self.issue("P07E103_INVALID_FIELD_VALUE", path)
            return None
        if isinstance(value, list):
            if not value or any(isinstance(item, (Mapping, list)) or isinstance(item, CanonicalDecimal) for item in value):
                self.issue("P07E103_INVALID_FIELD_VALUE", path)
                return None
            return tuple(value)
        if isinstance(value, (str, bool, int, CanonicalDecimal)):
            return value
        self.issue("P07E103_INVALID_FIELD_VALUE", path)
        return None

    def arguments(self, value: Any, path: str, *, allow_parameter: bool) -> dict[str, Any]:
        if not isinstance(value, Mapping):
            self.issue("P07E103_INVALID_FIELD_VALUE", path)
            return {}
        output: dict[str, Any] = {}
        for key in value:
            if not isinstance(key, str) or not _PARAMETER_NAME.fullmatch(key):
                self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.{key}")
                continue
            converted = self.argument_value(value[key], f"{path}.{key}", allow_parameter=allow_parameter)
            if converted is not None:
                output[key] = converted
        return output

    def expression(
        self,
        value: Any,
        *,
        path: str,
        node_id: str,
        allow_parameter: bool,
        depth: int = 1,
    ) -> tuple[ExpressionNode | None, int]:
        if depth > MAX_AST_DEPTH:
            self.issue("P07E202_AST_DEPTH_LIMIT", path, stage="ast", node_id=node_id)
            return None, 0
        self.source_node_count += 1
        if self.source_node_count > MAX_AST_NODES_PER_DOCUMENT:
            self.issue("P07E203_AST_NODE_LIMIT", path, stage="ast", node_id=node_id)
            return None, 0
        if not isinstance(value, Mapping) or len(value) != 1:
            self.issue("P07E201_UNKNOWN_OPERATOR", path, stage="ast", node_id=node_id)
            return None, 1
        operator = next(iter(value))
        span = self.span(path) or self.parsed.span_for("$")
        assert span is not None
        if operator == "predicate":
            item = self.check_mapping(
                value[operator], path=f"{path}.predicate",
                fields=("id", "version", "arguments"), required=("id", "version", "arguments"),
            )
            if item is None:
                return None, 1
            predicate_id = item.get("id")
            version = item.get("version")
            if not isinstance(predicate_id, str):
                self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.predicate.id")
                predicate_id = "INVALID"
            if not isinstance(version, str):
                self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.predicate.version")
                version = "0.0.0"
            arguments = self.arguments(item.get("arguments"), f"{path}.predicate.arguments", allow_parameter=allow_parameter)
            return PredicateCallNode(
                node_id=node_id, source_span=span, predicate_id=predicate_id,
                predicate_version=version, arguments=arguments, binding=None,
                required_capabilities=(),
            ), 1
        if operator in {"all", "any"}:
            children = self.sequence(
                value[operator], path=f"{path}.{operator}",
                maximum=MAX_LOGICAL_CHILDREN, nonempty=True,
            )
            if children is None:
                return None, 1
            nodes: list[ExpressionNode] = []
            total = 1
            for index, child in enumerate(children):
                child_node, count = self.expression(
                    child, path=f"{path}.{operator}[{index}]",
                    node_id=f"{node_id}.{operator}.{index:06d}",
                    allow_parameter=allow_parameter, depth=depth + 1,
                )
                total += count
                if child_node is not None:
                    nodes.append(child_node)
            if not nodes:
                return None, total
            cls = AllNode if operator == "all" else AnyNode
            return cls(node_id=node_id, source_span=span, children=tuple(nodes)), total
        if operator == "not":
            child, count = self.expression(
                value[operator], path=f"{path}.not", node_id=f"{node_id}.not",
                allow_parameter=allow_parameter, depth=depth + 1,
            )
            return (None, count + 1) if child is None else (NotNode(node_id=node_id, source_span=span, child=child), count + 1)
        if operator == "macro":
            item = self.check_mapping(
                value[operator], path=f"{path}.macro",
                fields=("id", "revision", "arguments"), required=("id", "revision", "arguments"),
            )
            if item is None:
                return None, 1
            macro_id = item.get("id")
            revision = item.get("revision")
            if not isinstance(macro_id, str):
                self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.macro.id")
                macro_id = "invalid"
            if not isinstance(revision, str):
                self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.macro.revision")
                revision = "0.0.0"
            arguments = self.arguments(item.get("arguments"), f"{path}.macro.arguments", allow_parameter=allow_parameter)
            return MacroCallNode(
                node_id=node_id, source_span=span, macro_id=macro_id,
                macro_revision=revision, arguments=arguments,
            ), 1
        self.issue("P07E201_UNKNOWN_OPERATOR", path, stage="ast", node_id=node_id)
        return None, 1

    def macro_declaration(self, value: Any, index: int) -> MacroDeclaration | None:
        path = f"$.macros[{index}]"
        mapping = self.check_mapping(value, path=path, fields=self._MACRO_FIELDS, required=self._MACRO_FIELDS[:4])
        if mapping is None:
            return None
        macro_id = self.text(mapping.get("id"), path=f"{path}.id", pattern=_LOWER_IDENTIFIER)
        revision = self.text(mapping.get("revision"), path=f"{path}.revision", pattern=_SEMVER)
        params_raw = self.sequence(mapping.get("parameters"), path=f"{path}.parameters", maximum=MAX_MACRO_PARAMETERS)
        parameters: list[MacroParameter] = []
        if params_raw is not None:
            for position, raw in enumerate(params_raw):
                param_path = f"{path}.parameters[{position}]"
                item = self.check_mapping(raw, path=param_path, fields=("name", "type"), required=("name", "type"))
                if item is None:
                    continue
                name = self.text(item.get("name"), path=f"{param_path}.name", pattern=_PARAMETER_NAME)
                kind = item.get("type")
                if kind not in {"house", "planet", "role_collection"}:
                    self.issue("P07E103_INVALID_FIELD_VALUE", f"{param_path}.type")
                    kind = None
                if name is not None and kind is not None:
                    parameters.append(MacroParameter(name=name, parameter_type=kind, source_span=self.span(param_path) or self.span(path)))
        names = tuple(item.name for item in parameters)
        if len(set(names)) != len(names):
            self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.parameters")
        body, count = self.expression(
            mapping.get("body"), path=f"{path}.body", node_id=f"macros.{index:06d}.body", allow_parameter=True,
        )
        if count > MAX_AST_NODES_PER_RULE:
            self.issue("P07E203_AST_NODE_LIMIT", f"{path}.body", stage="ast")
        label = mapping.get("label")
        description = mapping.get("description")
        for name, text in (("label", label), ("description", description)):
            if text is not None and not isinstance(text, str):
                self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.{name}")
        if macro_id is None or revision is None or body is None:
            return None
        return MacroDeclaration(
            macro_id=macro_id, revision=revision, parameters=tuple(parameters), body=body,
            source_span=self.span(path) or self.span("$"), source_order=index,
            label=label if isinstance(label, str) else None,
            description=description if isinstance(description, str) else None,
        )

    def rule_declaration(self, value: Any, index: int) -> RuleDeclaration | None:
        path = f"$.rules[{index}]"
        mapping = self.check_mapping(value, path=path, fields=self._RULE_FIELDS, required=self._REQUIRED_RULE_FIELDS)
        if mapping is None:
            return None
        rule_id = self.text(mapping.get("id"), path=f"{path}.id", pattern=_RULE_ID)
        revision = self.text(mapping.get("revision"), path=f"{path}.revision", pattern=_SEMVER)
        family = self.text(mapping.get("family"), path=f"{path}.family", pattern=_LOWER_IDENTIFIER)
        category = self.text(mapping.get("category"), path=f"{path}.category", pattern=_LOWER_IDENTIFIER)
        context = self.text(mapping.get("context"), path=f"{path}.context", pattern=_LOWER_IDENTIFIER)
        if context is not None and context != "natal":
            self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.context")
        label = mapping.get("label")
        if not isinstance(label, str) or not label:
            self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.label")
            label = None
        priority = mapping.get("priority")
        if type(priority) is not int or not MIN_INTEGER <= priority <= MAX_INTEGER:
            self.issue("P07E104_INVALID_NUMERIC_VALUE", f"{path}.priority")
            priority = None
        base_weight = mapping.get("base_weight")
        if not isinstance(base_weight, CanonicalDecimal):
            self.issue("P07E104_INVALID_NUMERIC_VALUE", f"{path}.base_weight")
            base_weight = None
        quality = mapping.get("quality")
        if quality is not None and (
            not isinstance(quality, CanonicalDecimal)
            or not 0.0 <= quality.as_float() <= 1.0
        ):
            self.issue("P07E104_INVALID_NUMERIC_VALUE", f"{path}.quality")
            quality = None
        domains_raw = self.sequence(
            mapping.get("domains"), path=f"{path}.domains", maximum=MAX_SEQUENCE_ELEMENTS
        )
        domains: tuple[str, ...] = ()
        if domains_raw is not None:
            if any(not isinstance(item, str) or not _LOWER_IDENTIFIER.fullmatch(item) for item in domains_raw):
                self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.domains")
            else:
                domains = tuple(domains_raw)
                if domains != tuple(sorted(set(domains))):
                    self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.domains")
        requires = self.capability_refs(mapping.get("requires"), f"{path}.requires")
        evidence = self.check_mapping(
            mapping.get("evidence"), path=f"{path}.evidence", fields=("mode",), required=("mode",),
        )
        evidence_mode = None if evidence is None else evidence.get("mode")
        if evidence_mode != "predicate_trace_references":
            self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.evidence.mode")
            evidence_mode = None
        provenance: Mapping[str, Any] = {}
        if "provenance" in mapping:
            item = self.check_mapping(
                mapping["provenance"], path=f"{path}.provenance",
                fields=self._PROVENANCE_FIELDS, required=(),
            )
            if item is not None:
                for name, value in item.items():
                    if not isinstance(value, str) or not value:
                        self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.provenance.{name}")
                provenance = dict(item)
        presentation: Mapping[str, Any] = {}
        if "presentation" in mapping:
            item = self.check_mapping(
                mapping["presentation"], path=f"{path}.presentation",
                fields=self._PRESENTATION_FIELDS, required=(),
            )
            if item is not None:
                for name in ("description", "narrative_key"):
                    if name in item and (not isinstance(item[name], str) or not item[name]):
                        self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.presentation.{name}")
                tags = item.get("tags")
                if tags is not None and (
                    not isinstance(tags, list) or any(not isinstance(tag, str) or not tag for tag in tags)
                    or tuple(tags) != tuple(sorted(set(tags)))
                ):
                    self.issue("P07E103_INVALID_FIELD_VALUE", f"{path}.presentation.tags")
                presentation = dict(item)
        governance_ref = mapping.get("governance_ref")
        if governance_ref is not None and self.text(governance_ref, path=f"{path}.governance_ref", pattern=_GENERAL_IDENTIFIER) is None:
            governance_ref = None
        when, count = self.expression(
            mapping.get("when"), path=f"{path}.when", node_id=f"rules.{index:06d}.when", allow_parameter=False,
        )
        if count > MAX_AST_NODES_PER_RULE:
            self.issue("P07E203_AST_NODE_LIMIT", f"{path}.when", stage="ast")
        required_values = (rule_id, revision, family, category, label, priority, base_weight, context, evidence_mode, when)
        if any(item is None for item in required_values):
            return None
        return RuleDeclaration(
            rule_id=rule_id, revision=revision, family=family, category=category,
            domains=domains, label=label, priority=priority, base_weight=base_weight,
            context=context, requires=requires, evidence_mode=evidence_mode, when=when,
            source_span=self.span(path) or self.span("$"), source_order=index,
            quality=quality, provenance=provenance, presentation=presentation,
            governance_ref=governance_ref,
        )

    def build_document(self) -> DslDocument | None:
        root = self.check_mapping(
            self.parsed.value, path="$", fields=self._ROOT_FIELDS, required=self._ROOT_FIELDS,
        )
        if root is None:
            return None
        dsl = root.get("dsl")
        if "dsl" in root and dsl != "parasara-rule-dsl":
            self.issue("P07E103_INVALID_FIELD_VALUE", "$.dsl")
            dsl = None
        version = root.get("dsl_version")
        if "dsl_version" in root and version != DSL_SCHEMA_VERSION:
            self.issue("P07E103_INVALID_FIELD_VALUE", "$.dsl_version")
            version = None
        system = (
            self.text(root.get("system"), path="$.system", pattern=_LOWER_IDENTIFIER)
            if "system" in root else None
        )
        rule_set = (
            self.check_mapping(
                root.get("rule_set"), path="$.rule_set", fields=("family", "version"), required=("family", "version"),
            )
            if "rule_set" in root else None
        )
        family = None if rule_set is None else self.text(rule_set.get("family"), path="$.rule_set.family", pattern=_LOWER_IDENTIFIER)
        set_version = None if rule_set is None else self.text(rule_set.get("version"), path="$.rule_set.version", pattern=_GENERAL_IDENTIFIER)
        if isinstance(set_version, str) and set_version.casefold() == "latest":
            self.issue("P07E103_INVALID_FIELD_VALUE", "$.rule_set.version")
            set_version = None
        macro_rows = (
            self.sequence(root.get("macros"), path="$.macros", maximum=MAX_MACROS)
            if "macros" in root else None
        )
        rule_rows = (
            self.sequence(root.get("rules"), path="$.rules", maximum=MAX_RULES, nonempty=True)
            if "rules" in root else None
        )
        macros = tuple(
            item for item in (
                self.macro_declaration(value, index) for index, value in enumerate(macro_rows or [])
            ) if item is not None
        )
        rules = tuple(
            item for item in (
                self.rule_declaration(value, index) for index, value in enumerate(rule_rows or [])
            ) if item is not None
        )
        macro_keys = [(item.macro_id, item.revision) for item in macros]
        seen_macros: set[tuple[str, str]] = set()
        for item, key in zip(macros, macro_keys):
            if key in seen_macros:
                self.diagnostics.add(
                    "P07E301_DUPLICATE_MACRO_REVISION", stage="macro",
                    field_path=f"$.macros[{item.source_order}]", span=item.source_span, macro=item,
                )
            seen_macros.add(key)
        seen_rules: set[tuple[str, str]] = set()
        for item in rules:
            key = (item.rule_id, item.revision)
            if key in seen_rules:
                self.diagnostics.add(
                    "P07E105_DUPLICATE_RULE_REVISION", stage="schema",
                    field_path=f"$.rules[{item.source_order}]", span=item.source_span, rule=item,
                )
            seen_rules.add(key)
        if any(item is None for item in (dsl, version, system, family, set_version)) or not rules:
            return None
        return DslDocument(
            dsl=dsl, dsl_version=version, system=system,
            rule_set_family=family, rule_set_version=set_version,
            macros=macros, rules=rules, source_id=self.source_id,
            source_span=self.span("$"),
        )

    def normalize_kind(self, value: Any, kind: str) -> tuple[Any | None, bool]:
        if kind == "house":
            return (value, True) if type(value) is int and 1 <= value <= 12 else (None, False)
        if kind == "planet":
            if not isinstance(value, str):
                return None, False
            found = {item.casefold(): item for item in CANONICAL_PLANETS}.get(value.strip().casefold())
            return (found, True) if found is not None else (None, False)
        if kind == "role_collection":
            if not isinstance(value, tuple) or not value or len(set(value)) != len(value):
                return None, False
            if any(not isinstance(item, str) or item not in FUNCTIONAL_ROLE_VALUES for item in value):
                return None, False
            return tuple(sorted(value)), True
        return None, False

    def bind_predicate(
        self,
        node: PredicateCallNode,
        *,
        path: str,
        rule: RuleDeclaration | None,
        macro: MacroDeclaration | None,
        parameter_types: Mapping[str, str] | None = None,
    ) -> PredicateCallNode | None:
        if not _PREDICATE_ID.fullmatch(node.predicate_id) or node.predicate_id not in self.registry.canonical_ids():
            self.diagnostics.add(
                "P07E211_UNKNOWN_PREDICATE", stage="binding", field_path=f"{path}.predicate.id",
                span=node.source_span, rule=rule, macro=macro, node_id=node.node_id,
                details={"predicate_id": node.predicate_id if isinstance(node.predicate_id, str) else "invalid"},
            )
            return None
        definition = self.registry.lookup(node.predicate_id)
        assert definition is not None
        if node.predicate_version != definition.predicate_version:
            self.diagnostics.add(
                "P07E212_PREDICATE_VERSION_MISMATCH", stage="binding",
                field_path=f"{path}.predicate.version", span=node.source_span,
                rule=rule, macro=macro, node_id=node.node_id,
                details={"expected": definition.predicate_version, "observed": node.predicate_version},
            )
            return None
        specs = definition.parameter_schema.specifications
        canonical_names = {item.name for item in specs}
        supplied_names = set(node.arguments)
        missing = [item.name for item in specs if item.required and item.name not in supplied_names]
        unknown = sorted(supplied_names - canonical_names)
        for name in missing + unknown:
            self.diagnostics.add(
                "P07E213_INVALID_ARGUMENT_NAME", stage="binding",
                field_path=f"{path}.predicate.arguments.{name}", span=node.source_span,
                rule=rule, macro=macro, node_id=node.node_id, details={"argument": name},
            )
        if missing or unknown:
            return None
        if parameter_types is not None:
            partial_arguments: dict[str, Any] = {}
            partial_valid = True
            for spec in specs:
                if spec.name not in node.arguments:
                    if spec.has_default:
                        partial_arguments[spec.name] = spec.default
                    continue
                value = node.arguments[spec.name]
                if isinstance(value, MacroParameterReference):
                    declared = parameter_types.get(value.name)
                    if declared is None:
                        partial_valid = False
                        self.diagnostics.add(
                            "P07E305_MACRO_PARAMETER_NOT_FOUND", stage="macro",
                            field_path=f"{path}.predicate.arguments.{spec.name}", span=node.source_span,
                            rule=rule, macro=macro, node_id=node.node_id, details={"parameter": value.name},
                        )
                    elif declared != spec.kind.value:
                        partial_valid = False
                        self.diagnostics.add(
                            "P07E304_MACRO_ARGUMENT_TYPE_MISMATCH", stage="macro",
                            field_path=f"{path}.predicate.arguments.{spec.name}", span=node.source_span,
                            rule=rule, macro=macro, node_id=node.node_id,
                            details={"expected": spec.kind.value, "observed": declared},
                        )
                    else:
                        partial_arguments[spec.name] = value
                else:
                    normalized, valid = self.normalize_kind(value, spec.kind.value)
                    if not valid:
                        partial_valid = False
                        self.diagnostics.add(
                            "P07E214_ARGUMENT_TYPE_MISMATCH", stage="binding",
                            field_path=f"{path}.predicate.arguments.{spec.name}", span=node.source_span,
                            rule=rule, macro=macro, node_id=node.node_id,
                            details={"expected": spec.kind.value},
                        )
                    else:
                        partial_arguments[spec.name] = normalized
            if not partial_valid:
                return None
            capabilities: list[CapabilityReference] = []
            for requirement in definition.required_capabilities:
                found = self.catalog.lookup(requirement.capability_id)
                if isinstance(found, CapabilityCatalogMiss) or found.capability_version != requirement.capability_version:
                    self.diagnostics.add(
                        "P07E215_PREDICATE_CAPABILITY_MISMATCH", stage="binding",
                        field_path=path, span=node.source_span, rule=rule, macro=macro, node_id=node.node_id,
                    )
                    return None
                capabilities.append(CapabilityReference(
                    capability_id=requirement.capability_id,
                    capability_version=requirement.capability_version,
                ))
            schema_sha = hashlib.sha256(canonical_json_bytes(definition.parameter_schema.metadata())).hexdigest()
            binding = PredicateBinding(
                predicate_id=definition.predicate_id,
                predicate_version=definition.predicate_version,
                arguments=partial_arguments,
                parameter_schema_sha256=schema_sha,
                definition_sha256=predicate_definition_fingerprint_sha256(definition),
                required_capabilities=tuple(capabilities),
                system_scope=definition.system_scope,
            )
            return replace(
                node,
                arguments=partial_arguments,
                binding=binding,
                required_capabilities=tuple(capabilities),
            )
        raw_arguments = {
            key: (value.value if isinstance(value, CanonicalDecimal) else list(value) if isinstance(value, tuple) else value)
            for key, value in node.arguments.items()
        }
        outcome = definition.parameter_schema.validate(raw_arguments)
        if not outcome.valid:
            for item in outcome.issues:
                code = (
                    "P07E213_INVALID_ARGUMENT_NAME"
                    if item.code in {ParameterIssueCode.MISSING_REQUIRED, ParameterIssueCode.UNKNOWN_PARAMETER, ParameterIssueCode.CONFLICTING_ALIAS}
                    else "P07E214_ARGUMENT_TYPE_MISMATCH"
                )
                self.diagnostics.add(
                    code, stage="binding",
                    field_path=f"{path}.predicate.arguments.{item.parameter_name or 'unknown'}",
                    span=node.source_span, rule=rule, macro=macro, node_id=node.node_id,
                    details={"expected": item.expected, "reason": item.code.value},
                )
            return None
        assert outcome.normalized_inputs is not None
        capabilities: list[CapabilityReference] = []
        for requirement in definition.required_capabilities:
            found = self.catalog.lookup(requirement.capability_id)
            if isinstance(found, CapabilityCatalogMiss) or found.capability_version != requirement.capability_version:
                self.diagnostics.add(
                    "P07E215_PREDICATE_CAPABILITY_MISMATCH", stage="binding",
                    field_path=path, span=node.source_span, rule=rule, macro=macro, node_id=node.node_id,
                )
                return None
            capabilities.append(CapabilityReference(
                capability_id=requirement.capability_id,
                capability_version=requirement.capability_version,
            ))
        schema_sha = hashlib.sha256(canonical_json_bytes(definition.parameter_schema.metadata())).hexdigest()
        binding = PredicateBinding(
            predicate_id=definition.predicate_id,
            predicate_version=definition.predicate_version,
            arguments=outcome.normalized_inputs,
            parameter_schema_sha256=schema_sha,
            definition_sha256=predicate_definition_fingerprint_sha256(definition),
            required_capabilities=tuple(capabilities),
            system_scope=definition.system_scope,
        )
        return PredicateCallNode(
            node_id=node.node_id, source_span=node.source_span,
            predicate_id=definition.predicate_id, predicate_version=definition.predicate_version,
            arguments=outcome.normalized_inputs, binding=binding,
            required_capabilities=tuple(capabilities),
            expansion_provenance=node.expansion_provenance,
        )

    def validate_macro_body(
        self,
        node: ExpressionNode,
        macro: MacroDeclaration,
        macros: Mapping[tuple[str, str], MacroDeclaration],
        path: str,
    ) -> ExpressionNode:
        parameter_types = {item.name: item.parameter_type for item in macro.parameters}
        if isinstance(node, PredicateCallNode):
            bound = self.bind_predicate(
                node, path=path, rule=None, macro=macro, parameter_types=parameter_types
            )
            return node if bound is None else bound
        elif isinstance(node, (AllNode, AnyNode)):
            children = tuple(
                self.validate_macro_body(child, macro, macros, f"{path}.children[{index}]")
                for index, child in enumerate(node.children)
            )
            return replace(node, children=children)
        elif isinstance(node, NotNode):
            return replace(
                node,
                child=self.validate_macro_body(node.child, macro, macros, f"{path}.not"),
            )
        elif isinstance(node, MacroCallNode):
            target = macros.get((node.macro_id, node.macro_revision))
            if target is None:
                self.diagnostics.add(
                    "P07E302_MACRO_NOT_FOUND", stage="macro", field_path=path,
                    span=node.source_span, macro=macro, node_id=node.node_id,
                )
            else:
                expected = {item.name: item for item in target.parameters}
                supplied = set(node.arguments)
                for name in [item.name for item in target.parameters if item.name not in supplied] + sorted(supplied - set(expected)):
                    self.diagnostics.add(
                        "P07E303_MACRO_ARGUMENT_MISMATCH", stage="macro",
                        field_path=f"{path}.macro.arguments.{name}", span=node.source_span,
                        macro=macro, node_id=node.node_id, details={"argument": name},
                    )
                for name in sorted(supplied & set(expected)):
                    value = node.arguments[name]
                    if isinstance(value, MacroParameterReference):
                        current_kind = parameter_types.get(value.name)
                        if current_kind is None:
                            self.diagnostics.add(
                                "P07E305_MACRO_PARAMETER_NOT_FOUND", stage="macro",
                                field_path=f"{path}.macro.arguments.{name}", span=node.source_span,
                                macro=macro, node_id=node.node_id, details={"parameter": value.name},
                            )
                        elif current_kind != expected[name].parameter_type:
                            self.diagnostics.add(
                                "P07E304_MACRO_ARGUMENT_TYPE_MISMATCH", stage="macro",
                                field_path=f"{path}.macro.arguments.{name}", span=node.source_span,
                                macro=macro, node_id=node.node_id,
                                details={"expected": expected[name].parameter_type, "observed": current_kind},
                            )
                    elif not self.normalize_kind(value, expected[name].parameter_type)[1]:
                        self.diagnostics.add(
                            "P07E304_MACRO_ARGUMENT_TYPE_MISMATCH", stage="macro",
                            field_path=f"{path}.macro.arguments.{name}", span=node.source_span,
                            macro=macro, node_id=node.node_id,
                        )
        return node

    def bind_source_tree(
        self,
        node: ExpressionNode,
        *,
        rule: RuleDeclaration,
        path: str,
    ) -> ExpressionNode:
        """Bind direct source predicates while preserving source macro calls."""

        if isinstance(node, PredicateCallNode):
            bound = self.bind_predicate(node, path=path, rule=rule, macro=None)
            return node if bound is None else bound
        if isinstance(node, (AllNode, AnyNode)):
            return replace(
                node,
                children=tuple(
                    self.bind_source_tree(
                        child,
                        rule=rule,
                        path=f"{path}.children[{index}]",
                    )
                    for index, child in enumerate(node.children)
                ),
            )
        if isinstance(node, NotNode):
            return replace(
                node,
                child=self.bind_source_tree(node.child, rule=rule, path=f"{path}.not"),
            )
        return node

    def resolve_macro_types(
        self,
        node: ExpressionNode,
        macros: Mapping[tuple[str, str], MacroDeclaration],
        stack: tuple[tuple[str, str], ...] = (),
    ) -> ExpressionNode:
        if isinstance(node, MacroCallNode):
            key = (node.macro_id, node.macro_revision)
            target = macros.get(key)
            if target is None or key in stack:
                return node
            body = self.resolve_macro_types(target.body, macros, (*stack, key))
            return replace(node, static_result_type=body.static_result_type)
        if isinstance(node, (AllNode, AnyNode)):
            return replace(
                node,
                children=tuple(self.resolve_macro_types(child, macros, stack) for child in node.children),
            )
        if isinstance(node, NotNode):
            return replace(node, child=self.resolve_macro_types(node.child, macros, stack))
        return node

    def rebase_node_ids(self, node: ExpressionNode, node_id: str) -> ExpressionNode:
        if isinstance(node, PredicateCallNode):
            return replace(node, node_id=node_id)
        if isinstance(node, AllNode):
            return replace(
                node,
                node_id=node_id,
                children=tuple(
                    self.rebase_node_ids(child, f"{node_id}.all.{index:06d}")
                    for index, child in enumerate(node.children)
                ),
            )
        if isinstance(node, AnyNode):
            return replace(
                node,
                node_id=node_id,
                children=tuple(
                    self.rebase_node_ids(child, f"{node_id}.any.{index:06d}")
                    for index, child in enumerate(node.children)
                ),
            )
        if isinstance(node, NotNode):
            return replace(node, node_id=node_id, child=self.rebase_node_ids(node.child, f"{node_id}.not"))
        return replace(node, node_id=node_id)

    def charge_expanded(
        self,
        *,
        budget: list[int],
        rule: RuleDeclaration,
        path: str,
        node: ExpressionNode,
    ) -> bool:
        budget[0] += 1
        self.expanded_node_count += 1
        if budget[0] > MAX_EXPANDED_NODES_PER_RULE or self.expanded_node_count > MAX_EXPANDED_NODES_PER_DOCUMENT:
            self.diagnostics.add(
                "P07E309_MACRO_EXPANDED_NODE_LIMIT", stage="expanded", field_path=path,
                span=node.source_span, rule=rule, node_id=node.node_id,
                details={
                    "document_limit": MAX_EXPANDED_NODES_PER_DOCUMENT,
                    "rule_limit": MAX_EXPANDED_NODES_PER_RULE,
                },
            )
            return False
        return True

    def detect_cycles(self, macros: tuple[MacroDeclaration, ...]) -> None:
        macro_map = {(item.macro_id, item.revision): item for item in macros}

        def calls(node: ExpressionNode) -> tuple[tuple[str, str], ...]:
            if isinstance(node, MacroCallNode):
                return ((node.macro_id, node.macro_revision),)
            if isinstance(node, (AllNode, AnyNode)):
                return tuple(found for child in node.children for found in calls(child))
            if isinstance(node, NotNode):
                return calls(node.child)
            return ()

        graph = {key: tuple(call for call in calls(value.body) if call in macro_map) for key, value in macro_map.items()}
        emitted: set[tuple[str, str]] = set()
        for start, declaration in macro_map.items():
            if start in graph[start]:
                self.diagnostics.add(
                    "P07E306_MACRO_DIRECT_RECURSION", stage="macro",
                    field_path=f"$.macros[{declaration.source_order}].body", span=declaration.source_span,
                    macro=declaration,
                )
                emitted.add(start)
                continue
            stack: list[tuple[tuple[str, str], tuple[tuple[str, str], ...]]] = [(start, ())]
            while stack:
                current, ancestors = stack.pop()
                if current in ancestors:
                    cycle = ancestors[ancestors.index(current):]
                    for member in cycle:
                        if member in emitted:
                            continue
                        item = macro_map[member]
                        self.diagnostics.add(
                            "P07E307_MACRO_CYCLE", stage="macro",
                            field_path=f"$.macros[{item.source_order}].body", span=item.source_span,
                            macro=item, details={"cycle": tuple(value[0] for value in cycle)},
                        )
                        emitted.add(member)
                    break
                for target in reversed(graph.get(current, ())):
                    stack.append((target, (*ancestors, current)))

    def substitute(self, value: Any, env: Mapping[str, Any]) -> tuple[Any | None, bool]:
        if isinstance(value, MacroParameterReference):
            return (env[value.name], True) if value.name in env else (None, False)
        if isinstance(value, tuple):
            output = []
            for item in value:
                converted, valid = self.substitute(item, env)
                if not valid:
                    return None, False
                output.append(converted)
            return tuple(output), True
        return value, True

    def expand(
        self,
        node: ExpressionNode,
        *,
        rule: RuleDeclaration,
        macros: Mapping[tuple[str, str], MacroDeclaration],
        env: Mapping[str, Any],
        path: str,
        depth: int,
        provenance: tuple[SourceSpan, ...],
        traces: list[MacroExpansionTrace],
        budget: list[int],
    ) -> ExpressionNode | None:
        if isinstance(node, PredicateCallNode):
            if not self.charge_expanded(budget=budget, rule=rule, path=path, node=node):
                return None
            arguments: dict[str, Any] = {}
            for name, value in node.arguments.items():
                converted, valid = self.substitute(value, env)
                if not valid:
                    self.diagnostics.add(
                        "P07E305_MACRO_PARAMETER_NOT_FOUND", stage="macro",
                        field_path=f"{path}.predicate.arguments.{name}", span=node.source_span,
                        rule=rule, node_id=node.node_id,
                    )
                    return None
                arguments[name] = converted
            candidate = PredicateCallNode(
                node_id=node.node_id, source_span=node.source_span,
                predicate_id=node.predicate_id, predicate_version=node.predicate_version,
                arguments=arguments, binding=None, required_capabilities=(),
                expansion_provenance=provenance,
            )
            return self.bind_predicate(candidate, path=path, rule=rule, macro=None)
        if isinstance(node, (AllNode, AnyNode)):
            if not self.charge_expanded(budget=budget, rule=rule, path=path, node=node):
                return None
            children: list[ExpressionNode] = []
            for index, child in enumerate(node.children):
                expanded = self.expand(
                    child, rule=rule, macros=macros, env=env,
                    path=f"{path}.children[{index}]", depth=depth, provenance=provenance,
                    traces=traces, budget=budget,
                )
                if expanded is not None:
                    children.append(expanded)
            if len(children) != len(node.children):
                return None
            cls = AllNode if isinstance(node, AllNode) else AnyNode
            return cls(
                node_id=node.node_id, source_span=node.source_span, children=tuple(children),
                expansion_provenance=provenance,
            )
        if isinstance(node, NotNode):
            if not self.charge_expanded(budget=budget, rule=rule, path=path, node=node):
                return None
            child = self.expand(
                node.child, rule=rule, macros=macros, env=env,
                path=f"{path}.not", depth=depth, provenance=provenance, traces=traces,
                budget=budget,
            )
            return None if child is None else NotNode(
                node_id=node.node_id, source_span=node.source_span, child=child,
                expansion_provenance=provenance,
            )
        assert isinstance(node, MacroCallNode)
        if depth >= MAX_MACRO_EXPANSION_DEPTH:
            self.diagnostics.add(
                "P07E308_MACRO_EXPANSION_DEPTH_LIMIT", stage="macro", field_path=path,
                span=node.source_span, rule=rule, node_id=node.node_id,
            )
            return None
        target = macros.get((node.macro_id, node.macro_revision))
        if target is None:
            self.diagnostics.add(
                "P07E302_MACRO_NOT_FOUND", stage="macro", field_path=path,
                span=node.source_span, rule=rule, node_id=node.node_id,
            )
            return None
        expected = {item.name: item for item in target.parameters}
        supplied = set(node.arguments)
        mismatches = [item.name for item in target.parameters if item.name not in supplied] + sorted(supplied - set(expected))
        for name in mismatches:
            self.diagnostics.add(
                "P07E303_MACRO_ARGUMENT_MISMATCH", stage="macro",
                field_path=f"{path}.macro.arguments.{name}", span=node.source_span,
                rule=rule, node_id=node.node_id, details={"argument": name},
            )
        if mismatches:
            return None
        next_env: dict[str, Any] = {}
        for parameter in target.parameters:
            value, valid = self.substitute(node.arguments[parameter.name], env)
            if valid:
                value, valid = self.normalize_kind(value, parameter.parameter_type)
            if not valid:
                self.diagnostics.add(
                    "P07E304_MACRO_ARGUMENT_TYPE_MISMATCH", stage="macro",
                    field_path=f"{path}.macro.arguments.{parameter.name}", span=node.source_span,
                    rule=rule, node_id=node.node_id, details={"expected": parameter.parameter_type},
                )
                return None
            next_env[parameter.name] = value
        ordinal = len(traces)
        expanded_root = f"{node.node_id}.expanded.{ordinal:06d}"
        traces.append(MacroExpansionTrace(
            macro_id=target.macro_id, macro_revision=target.revision,
            call_node_id=node.node_id, call_span=node.source_span,
            definition_span=target.source_span,
            canonical_arguments_sha256=hashlib.sha256(canonical_json_bytes(_value_data(next_env))).hexdigest(),
            expansion_ordinal=ordinal, expanded_root_node_id=expanded_root,
        ))
        body = self.rebase_node_ids(target.body, expanded_root)
        return self.expand(
            body, rule=rule, macros=macros, env=next_env,
            path=f"{path}.macro.expanded", depth=depth + 1,
            provenance=(*provenance, node.source_span, target.source_span), traces=traces,
            budget=budget,
        )

    def ast_count(self, root: ExpressionNode) -> int:
        stack = [root]
        count = 0
        while stack:
            node = stack.pop()
            count += 1
            if isinstance(node, (AllNode, AnyNode)):
                stack.extend(reversed(node.children))
            elif isinstance(node, NotNode):
                stack.append(node.child)
        return count

    def bindings(self, root: ExpressionNode) -> tuple[PredicateBinding, ...]:
        found: list[PredicateBinding] = []
        stack = [root]
        while stack:
            node = stack.pop()
            if isinstance(node, PredicateCallNode):
                if node.binding is not None:
                    found.append(node.binding)
            elif isinstance(node, (AllNode, AnyNode)):
                stack.extend(reversed(node.children))
            elif isinstance(node, NotNode):
                stack.append(node.child)
        return tuple(found)

    def lower(self, node: ExpressionNode) -> dict[str, Any]:
        if isinstance(node, PredicateCallNode):
            return {"type": node.predicate_id, "params": dict(node.arguments)}
        if isinstance(node, AllNode):
            return {"type": "AND", "children": [self.lower(child) for child in node.children]}
        if isinstance(node, AnyNode):
            return {"type": "OR", "children": [self.lower(child) for child in node.children]}
        if isinstance(node, NotNode):
            return {"type": "NOT", "children": [self.lower(node.child)]}
        raise TypeError("macro calls must be eliminated before lowering")

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
            validated = validate_condition_definition(
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
            "predicate_library_content_sha256": predicate_registry_fingerprint_sha256(),
            "condition_evaluator": {
                "identity": "parashara-condition-evaluator",
                "version": "1.0.0",
                "compatibility_contract": "condition-result@1.0.0",
                "content_sha256": "23392015e5a5d75be8f15ef9fd6aeb79073ab1a60b2c3bca4f5cd3fcc25b4068",
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


class RuleDslCompiler:
    """The only owner of Prompt-07 parse/bind/expand/canonicalize/lower."""

    __slots__ = ("_resolved_versions", "_cache", "_cache_capacity")

    def __init__(self, *, resolved_versions: Any, cache_capacity: int = MAX_COMPILER_CACHE_ENTRIES) -> None:
        from systems.Parasara.engine.versioning import ResolvedEvaluationVersions

        if not isinstance(resolved_versions, ResolvedEvaluationVersions):
            raise TypeError("resolved_versions must be ResolvedEvaluationVersions")
        if type(cache_capacity) is not int or not 0 <= cache_capacity <= MAX_COMPILER_CACHE_ENTRIES:
            raise ValueError("cache_capacity must be between 0 and 64")
        self._resolved_versions = resolved_versions
        self._cache: OrderedDict[tuple[str, ...], Any] = OrderedDict()
        self._cache_capacity = cache_capacity

    @property
    def cache_capacity(self) -> int:
        return self._cache_capacity

    @property
    def cache_size(self) -> int:
        return len(self._cache)

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
        return _Analyzer(
            source_id=source_id, parsed=parsed.document, payload=payload_bytes,
        ).analyze()

    def _authorization_failure(self, code: str, source_id: str, details: Mapping[str, Any] | None = None) -> CompilationFailed:
        collector = _DiagnosticCollector(source_id)
        collector.add(code, stage="authorization", field_path="$", details={} if details is None else details)
        return CompilationFailed(compiled_rule_set=None, diagnostics=collector.finish())

    @staticmethod
    def _cache_key(*, manifest: Any, analyzed: AnalyzedRuleSet) -> tuple[str, ...]:
        """Return the exact Section 11.5 cache-key tuple."""

        component = manifest.dsl
        assert component is not None
        key = [
            manifest.manifest_fingerprint_sha256,
            analyzed.source_file_sha256,
            analyzed.canonical_dsl_sha256,
            DSL_SCHEMA_VERSION,
            component.identity,
            component.version,
            component.content_sha256 or "",
            component.compatibility_contract,
            DSL_CANONICALIZATION_CONTRACT,
            DSL_MACRO_EXPANSION_CONTRACT,
            manifest.predicate_library.identity,
            manifest.predicate_library.version,
            manifest.predicate_library.content_sha256 or "",
            manifest.predicate_library.compatibility_contract,
            manifest.condition_evaluator.identity,
            manifest.condition_evaluator.version,
            manifest.condition_evaluator.content_sha256 or "",
            manifest.condition_evaluator.compatibility_contract,
        ]
        for artifact in manifest.ordered_source_artifacts:
            key.extend((
                artifact["artifact_id"],
                artifact["semantic_content_sha256"],
                artifact.get("expanded_ast_sha256", ""),
                artifact.get("compiled_rule_set_sha256", ""),
            ))
        return tuple(key)

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


__all__ = (
    "DSL_COMPILER_IDENTITY", "DSL_COMPILER_VERSION", "DSL_COMPATIBILITY_CONTRACT",
    "DSL_CANONICALIZATION_CONTRACT", "DSL_MACRO_EXPANSION_CONTRACT",
    "DSL_COMPILER_CONTENT_SHA256", "DSL_COMPILER_IMPLEMENTATION_MODULE_IDS",
    "DSL_COMPILER_CONTRACT_DATA",
    "compiler_component_fingerprint_sha256", "RuleDslCompiler",
)
