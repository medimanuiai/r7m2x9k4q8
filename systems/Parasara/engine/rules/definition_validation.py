"""Immutable WP12 validation for current F1 Yoga and direct F2 conditions.

This module validates definitions only.  It never evaluates a predicate,
prepares chart state, touches an evaluator cache, or registers Yoga rules.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from pathlib import Path
import re
from typing import Any

import yaml
from yaml.constructor import ConstructorError

from systems.Parasara.engine.rules.canonical import (
    FrozenMapping,
    canonical_json_bytes,
)
from systems.Parasara.engine.rules.capabilities import (
    CapabilityCatalog,
    CapabilityCatalogMiss,
    get_production_capability_catalog,
    capability_catalog_fingerprint_bytes,
    validate_registry_capabilities,
)
from systems.Parasara.engine.rules.conditions import (
    DEFAULT_ROOT_NODE_ID,
    preflight_condition_tree,
)
from systems.Parasara.engine.rules.parameters import ParameterValidationIssue
from systems.Parasara.engine.rules.registry import (
    PredicateRegistry,
    PredicateRegistryError,
    get_production_registry,
    predicate_registry_fingerprint_bytes,
)


DEFINITION_SCHEMA_VERSION = "1.0.0"

_LOGICAL_OPERATORS = frozenset({"AND", "OR", "NOT"})
_PREDICATE_ID = re.compile(r"^[A-Z][A-Z0-9_]*$")
_RULE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_SOURCE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,255}$")
_NODE_PATH = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,4095}$")
_SAFE_CODE = re.compile(r"^[a-z][a-z0-9_]{0,127}$")
_PARAMETER_NAME = re.compile(r"^[a-z][a-z0-9_]{0,127}$")
_CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_SAFE_DETAIL_KEY = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_SAFE_DETAIL_VALUE = re.compile(r"^[A-Za-z0-9_$.-]{1,128}$")

_EXPECTED_CANONICAL_IDS = (
    "ASPECT_EXISTS", "FUNCTIONAL_ROLE", "HOUSE_OCCUPANT",
    "PLANET_EXALTED", "PLANET_IN_HOUSE",
)
_EXPECTED_EXPOSED_IDS = (
    "ASPECT", "ASPECT_EXISTS", "FUNCTIONAL_ROLE", "HOUSE_OCCUPANT",
    "PLANET_EXALTED", "PLANET_IN_HOUSE",
)

YOGA_REQUIRED_FIELDS = (
    "id", "name", "version", "category", "conditions", "weights",
    "evidence_required", "provenance", "sme_approved", "tests",
)
YOGA_ALLOWED_FIELDS = frozenset((*YOGA_REQUIRED_FIELDS, "description"))


class DefinitionIssueSeverity(str, Enum):
    ERROR = "error"


class ValidatedNodeKind(str, Enum):
    LOGICAL = "logical"
    PREDICATE = "predicate"


_ISSUE_MESSAGES = {
    "definition_registry_unready": "The predicate registry is not finalized and ready for definition validation.",
    "definition_registry_incompatible": "The predicate registry does not match the finalized production contract.",
    "capability_catalog_unready": "The capability catalog is not finalized and ready for definition validation.",
    "capability_catalog_incompatible": "The predicate capability declarations do not match the finalized catalog.",
    "condition_cycle": "The condition definition contains a cycle.",
    "condition_depth_limit": "The condition definition exceeds the maximum depth.",
    "condition_node_limit": "The condition definition exceeds the maximum node count.",
    "condition_preflight_error": "The condition definition could not be inspected safely.",
    "condition_node_not_mapping": "A condition node must be a mapping.",
    "condition_type_missing": "A condition node requires a type field.",
    "condition_type_not_string": "A condition node type must be a string.",
    "condition_type_blank": "A condition node type must not be blank.",
    "condition_unknown_fields": "A condition node contains unsupported fields.",
    "condition_children_missing": "A logical condition requires a children field.",
    "condition_children_not_list": "Logical condition children must be a list.",
    "condition_empty_operator": "AND and OR require at least one child.",
    "condition_not_arity": "NOT requires exactly one child.",
    "condition_params_missing": "A predicate condition requires a params field.",
    "condition_params_not_mapping": "Predicate parameters must be a mapping.",
    "unknown_operator": "The condition references an unsupported logical operator.",
    "unknown_predicate": "The condition references an unknown predicate.",
    "predicate_capability_incompatible": "A predicate capability requirement is absent or version-incompatible.",
    "parameter_invalid_container": "Predicate parameters must use the declared parameter mapping.",
    "parameter_missing_required": "A required predicate parameter is missing.",
    "parameter_unknown_parameter": "A predicate parameter is not declared by the canonical schema.",
    "parameter_invalid_type": "A predicate parameter has an unsupported type.",
    "parameter_invalid_value": "A predicate parameter has an unsupported value.",
    "parameter_conflicting_alias": "Canonical and alias parameter names conflict.",
    "parameter_duplicate_value": "A predicate parameter collection contains a duplicate value.",
    "yoga_document_root_not_list": "A Yoga YAML document root must be a list.",
    "yoga_rule_not_mapping": "A Yoga rule record must be a mapping.",
    "yoga_rule_missing_field": "A Yoga rule is missing a required top-level field.",
    "yoga_rule_unknown_fields": "A Yoga rule contains unsupported top-level fields.",
    "yoga_rule_id_invalid": "A Yoga rule ID must be a nonempty stable identifier.",
    "yoga_conditions_not_mapping": "The plural Yoga conditions field must contain exactly one mapping.",
    "duplicate_rule_id": "A later Yoga rule duplicates an earlier rule ID.",
    "yoga_path_not_absolute": "Strict Yoga file validation requires an explicit absolute path.",
    "yoga_file_missing": "The supplied Yoga rule file does not exist.",
    "yoga_file_unreadable": "The supplied Yoga rule file could not be read.",
    "yoga_invalid_yaml": "The supplied Yoga rule file is not valid YAML.",
    "yoga_unsafe_yaml": "The supplied Yoga rule file contains an unsupported YAML construct.",
    "yoga_unsafe_content": "The supplied Yoga rule contains unsupported noncanonical content.",
}


def _validate_source_name(value: Any) -> str:
    if not isinstance(value, str) or not _SOURCE_NAME.fullmatch(value):
        raise ValueError("source_name must be a safe logical relative identity")
    if value.startswith(("/", "\\")) or "\\" in value or ":" in value:
        raise ValueError("source_name must not be a filesystem path")
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("source_name must not contain traversal segments")
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleSourceIdentity:
    source_name: str
    rule_id: str | None = None
    rule_index: int | None = None

    def __post_init__(self) -> None:
        _validate_source_name(self.source_name)
        if self.rule_id is not None and (
            not isinstance(self.rule_id, str) or not _RULE_ID.fullmatch(self.rule_id)
        ):
            raise ValueError("rule_id must be a stable identifier when present")
        if self.rule_index is not None and (
            type(self.rule_index) is not int or self.rule_index < 0
        ):
            raise ValueError("rule_index must be a nonnegative integer when present")


def _safe_detail(value: Any, *, depth: int = 0) -> Any:
    if depth > 3:
        raise ValueError("issue details exceed the safe nesting bound")
    if value is None or type(value) is bool:
        return value
    if type(value) is int and 0 <= value <= 1_000_000:
        return value
    if isinstance(value, str) and _SAFE_DETAIL_VALUE.fullmatch(value):
        return value
    if type(value) in (list, tuple) and len(value) <= 16:
        return tuple(_safe_detail(item, depth=depth + 1) for item in value)
    if isinstance(value, Mapping) and len(value) <= 12:
        items: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not _SAFE_DETAIL_KEY.fullmatch(key):
                raise ValueError("issue detail keys must be safe identifiers")
            items[key] = _safe_detail(item, depth=depth + 1)
        return FrozenMapping(items)
    raise ValueError("issue details contain unsafe or unbounded content")


@dataclass(frozen=True, slots=True, kw_only=True)
class DefinitionIssue:
    code: str
    message: str
    node_path: str
    source: RuleSourceIdentity
    predicate_id: str | None = None
    parameter_name: str | None = None
    details: FrozenMapping = field(default_factory=FrozenMapping)
    severity: DefinitionIssueSeverity = DefinitionIssueSeverity.ERROR

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not _SAFE_CODE.fullmatch(self.code):
            raise ValueError("issue code must be a stable identifier")
        if self.code not in _ISSUE_MESSAGES or self.message != _ISSUE_MESSAGES[self.code]:
            raise ValueError("issue message must be the fixed message for its code")
        if not isinstance(self.node_path, str) or not _NODE_PATH.fullmatch(self.node_path):
            raise ValueError("node_path must be a stable logical path")
        if not isinstance(self.source, RuleSourceIdentity):
            raise TypeError("source must be RuleSourceIdentity")
        if self.predicate_id is not None and (
            not isinstance(self.predicate_id, str) or not _PREDICATE_ID.fullmatch(self.predicate_id)
        ):
            raise ValueError("predicate_id must be canonical syntax when present")
        if self.parameter_name is not None and (
            not isinstance(self.parameter_name, str) or not _PARAMETER_NAME.fullmatch(self.parameter_name)
        ):
            raise ValueError("parameter_name must be canonical when present")
        try:
            severity = self.severity if isinstance(self.severity, DefinitionIssueSeverity) else DefinitionIssueSeverity(self.severity)
        except (TypeError, ValueError) as exc:
            raise ValueError("WP12 issues support error severity only") from exc
        object.__setattr__(self, "severity", severity)
        object.__setattr__(self, "details", _safe_detail(self.details))


@dataclass(frozen=True, slots=True, kw_only=True)
class ValidatedNodeBinding:
    node_id: str
    node_path: str
    node_kind: ValidatedNodeKind
    requested_type: str
    canonical_type: str
    predicate_version: str | None
    parameters: FrozenMapping
    required_capabilities: tuple[tuple[str, str], ...]
    child_count: int | None

    def __post_init__(self) -> None:
        if not _NODE_PATH.fullmatch(self.node_id) or self.node_id != self.node_path:
            raise ValueError("node identity and path must be the same stable WP10 path")
        try:
            kind = self.node_kind if isinstance(self.node_kind, ValidatedNodeKind) else ValidatedNodeKind(self.node_kind)
        except (TypeError, ValueError) as exc:
            raise ValueError("node_kind is unsupported") from exc
        object.__setattr__(self, "node_kind", kind)
        if not isinstance(self.requested_type, str) or not _PREDICATE_ID.fullmatch(self.requested_type):
            raise ValueError("requested_type must be normalized canonical syntax")
        if not isinstance(self.canonical_type, str) or not _PREDICATE_ID.fullmatch(self.canonical_type):
            raise ValueError("canonical_type must be canonical syntax")
        if not isinstance(self.parameters, FrozenMapping):
            object.__setattr__(self, "parameters", FrozenMapping(self.parameters))
        if not isinstance(self.required_capabilities, tuple) or any(
            not isinstance(item, tuple) or len(item) != 2 or
            not isinstance(item[0], str) or not _CAPABILITY_ID.fullmatch(item[0]) or
            not isinstance(item[1], str) or not _SEMVER.fullmatch(item[1])
            for item in self.required_capabilities
        ):
            raise ValueError("required_capabilities must be ordered ID/version pairs")
        if kind is ValidatedNodeKind.LOGICAL:
            if self.canonical_type not in _LOGICAL_OPERATORS or self.predicate_version is not None:
                raise ValueError("logical bindings cannot carry predicate identity")
            if self.parameters or self.required_capabilities or type(self.child_count) is not int:
                raise ValueError("logical bindings carry only a child count")
        else:
            if self.canonical_type in _LOGICAL_OPERATORS or not isinstance(self.predicate_version, str):
                raise ValueError("predicate bindings require canonical ID and version")
            if self.child_count is not None:
                raise ValueError("predicate bindings cannot carry a child count")


@dataclass(frozen=True, slots=True, kw_only=True)
class ValidatedConditionDefinition:
    source: RuleSourceIdentity
    normalized_condition: FrozenMapping
    node_bindings: tuple[ValidatedNodeBinding, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.source, RuleSourceIdentity):
            raise TypeError("source must be RuleSourceIdentity")
        if not isinstance(self.normalized_condition, FrozenMapping):
            object.__setattr__(self, "normalized_condition", FrozenMapping(self.normalized_condition))
        if not isinstance(self.node_bindings, tuple) or not self.node_bindings or any(
            not isinstance(item, ValidatedNodeBinding) for item in self.node_bindings
        ):
            raise ValueError("node_bindings must be a nonempty immutable preorder tuple")
        paths = tuple(item.node_path for item in self.node_bindings)
        if paths[0] != DEFAULT_ROOT_NODE_ID or len(set(paths)) != len(paths):
            raise ValueError("node_bindings require one unique root-first path sequence")
        if self.normalized_condition.get("type") != self.node_bindings[0].canonical_type:
            raise ValueError("normalized root type must agree with the root binding")


@dataclass(frozen=True, slots=True, kw_only=True)
class DefinitionValidationOutcome:
    valid: bool
    definition: ValidatedConditionDefinition | None
    issues: tuple[DefinitionIssue, ...]

    def __post_init__(self) -> None:
        if type(self.valid) is not bool or not isinstance(self.issues, tuple) or any(
            not isinstance(item, DefinitionIssue) for item in self.issues
        ):
            raise TypeError("definition validation outcome fields have invalid types")
        if self.valid:
            if not isinstance(self.definition, ValidatedConditionDefinition) or self.issues:
                raise ValueError("valid outcomes contain one definition and no issues")
        elif self.definition is not None or not self.issues:
            raise ValueError("invalid outcomes contain issues and no definition")


@dataclass(frozen=True, slots=True, kw_only=True)
class ValidatedYogaRule:
    rule_id: str
    source: RuleSourceIdentity
    rule: FrozenMapping
    condition: ValidatedConditionDefinition

    def __post_init__(self) -> None:
        if not isinstance(self.rule_id, str) or not _RULE_ID.fullmatch(self.rule_id):
            raise ValueError("validated Yoga rule ID is invalid")
        if not isinstance(self.source, RuleSourceIdentity) or not isinstance(
            self.condition, ValidatedConditionDefinition
        ):
            raise TypeError("validated Yoga rule source/condition types are invalid")
        if not isinstance(self.rule, FrozenMapping):
            object.__setattr__(self, "rule", FrozenMapping(self.rule))


@dataclass(frozen=True, slots=True, kw_only=True)
class YogaRuleSetValidationOutcome:
    valid: bool
    rules: tuple[ValidatedYogaRule, ...]
    issues: tuple[DefinitionIssue, ...]

    def __post_init__(self) -> None:
        if type(self.valid) is not bool or not isinstance(self.rules, tuple) or not isinstance(self.issues, tuple):
            raise TypeError("Yoga validation outcome containers are invalid")
        if any(not isinstance(item, ValidatedYogaRule) for item in self.rules) or any(
            not isinstance(item, DefinitionIssue) for item in self.issues
        ):
            raise TypeError("Yoga validation outcome elements are invalid")
        if self.valid is bool(self.issues):
            raise ValueError("Yoga validation is true exactly when issues are empty")


def _source_to_data(value: RuleSourceIdentity) -> dict[str, Any]:
    return {
        "source_name": value.source_name,
        "rule_id": value.rule_id,
        "rule_index": value.rule_index,
    }


def _semantic_binding_data(binding: ValidatedNodeBinding) -> dict[str, Any]:
    return {
        "node_id": binding.node_id,
        "node_path": binding.node_path,
        "node_kind": binding.node_kind.value,
        "canonical_type": binding.canonical_type,
        "predicate_version": binding.predicate_version,
        "parameters": binding.parameters,
        "required_capabilities": tuple(
            {"capability_id": item[0], "capability_version": item[1]}
            for item in binding.required_capabilities
        ),
        "child_count": binding.child_count,
    }


def definition_semantic_projection(value: ValidatedConditionDefinition) -> FrozenMapping:
    if not isinstance(value, ValidatedConditionDefinition):
        raise TypeError("value must be ValidatedConditionDefinition")
    return FrozenMapping({
        "definition_schema_version": DEFINITION_SCHEMA_VERSION,
        "normalized_condition": value.normalized_condition,
        "node_bindings": tuple(_semantic_binding_data(item) for item in value.node_bindings),
    })


def definition_source_projection(value: ValidatedConditionDefinition) -> FrozenMapping:
    return FrozenMapping({
        "semantic_definition": definition_semantic_projection(value),
        "source": _source_to_data(value.source),
    })


def definition_issue_projection(value: DefinitionIssue) -> FrozenMapping:
    if not isinstance(value, DefinitionIssue):
        raise TypeError("value must be DefinitionIssue")
    return FrozenMapping({
        "code": value.code,
        "message": value.message,
        "node_path": value.node_path,
        "source": _source_to_data(value.source),
        "predicate_id": value.predicate_id,
        "parameter_name": value.parameter_name,
        "details": value.details,
        "severity": value.severity.value,
    })


def definition_issues_json_bytes(values: tuple[DefinitionIssue, ...]) -> bytes:
    if not isinstance(values, tuple) or any(not isinstance(item, DefinitionIssue) for item in values):
        raise TypeError("values must be an immutable DefinitionIssue tuple")
    return canonical_json_bytes(tuple(definition_issue_projection(item) for item in values))


def definition_issues_sha256(values: tuple[DefinitionIssue, ...]) -> str:
    return hashlib.sha256(definition_issues_json_bytes(values)).hexdigest()


def definition_semantic_json_bytes(value: ValidatedConditionDefinition) -> bytes:
    return canonical_json_bytes(definition_semantic_projection(value))


def definition_source_json_bytes(value: ValidatedConditionDefinition) -> bytes:
    return canonical_json_bytes(definition_source_projection(value))


def definition_semantic_sha256(value: ValidatedConditionDefinition) -> str:
    return hashlib.sha256(definition_semantic_json_bytes(value)).hexdigest()


def definition_source_sha256(value: ValidatedConditionDefinition) -> str:
    return hashlib.sha256(definition_source_json_bytes(value)).hexdigest()


def _issue(
    code: str,
    source: RuleSourceIdentity,
    node_path: str,
    *,
    predicate_id: str | None = None,
    parameter_name: str | None = None,
    details: Mapping[str, Any] | None = None,
) -> DefinitionIssue:
    return DefinitionIssue(
        code=code,
        message=_ISSUE_MESSAGES[code],
        node_path=node_path,
        source=source,
        predicate_id=predicate_id,
        parameter_name=parameter_name,
        details=FrozenMapping({} if details is None else details),
    )


def _boundary_issue(
    source: RuleSourceIdentity,
    registry: PredicateRegistry | None,
    catalog: CapabilityCatalog | None,
) -> DefinitionIssue | None:
    try:
        current_registry = get_production_registry() if registry is None else registry
    except Exception:
        return _issue("definition_registry_unready", source, DEFAULT_ROOT_NODE_ID)
    if not isinstance(current_registry, PredicateRegistry) or not current_registry.is_ready or not current_registry.is_frozen:
        return _issue("definition_registry_unready", source, DEFAULT_ROOT_NODE_ID)
    if current_registry.canonical_ids() != _EXPECTED_CANONICAL_IDS or current_registry.exposed_ids() != _EXPECTED_EXPOSED_IDS:
        return _issue("definition_registry_incompatible", source, DEFAULT_ROOT_NODE_ID)
    if registry is not None and predicate_registry_fingerprint_bytes(current_registry) != predicate_registry_fingerprint_bytes():
        return _issue("definition_registry_incompatible", source, DEFAULT_ROOT_NODE_ID)
    try:
        current_catalog = get_production_capability_catalog() if catalog is None else catalog
    except Exception:
        return _issue("capability_catalog_unready", source, DEFAULT_ROOT_NODE_ID)
    if not isinstance(current_catalog, CapabilityCatalog) or not current_catalog.is_ready or not current_catalog.is_frozen:
        return _issue("capability_catalog_unready", source, DEFAULT_ROOT_NODE_ID)
    if catalog is not None and capability_catalog_fingerprint_bytes(current_catalog) != capability_catalog_fingerprint_bytes():
        return _issue("capability_catalog_incompatible", source, DEFAULT_ROOT_NODE_ID)
    try:
        compatibility = validate_registry_capabilities(current_registry, current_catalog)
    except Exception:
        return _issue("capability_catalog_incompatible", source, DEFAULT_ROOT_NODE_ID)
    if not compatibility.compatible:
        return _issue("capability_catalog_incompatible", source, DEFAULT_ROOT_NODE_ID)
    return None


def _parameter_issue(
    item: ParameterValidationIssue,
    source: RuleSourceIdentity,
    node_path: str,
) -> DefinitionIssue:
    return _issue(
        f"parameter_{item.code.value}", source, node_path,
        predicate_id=item.predicate_id,
        parameter_name=item.parameter_name,
        details={"expected": item.expected},
    )


def validate_condition_definition(
    node: Any,
    *,
    source: RuleSourceIdentity,
    registry: PredicateRegistry | None = None,
    catalog: CapabilityCatalog | None = None,
) -> DefinitionValidationOutcome:
    """Validate one direct F2 node and return immutable canonical bindings."""

    if not isinstance(source, RuleSourceIdentity):
        raise TypeError("source must be RuleSourceIdentity")
    boundary = _boundary_issue(source, registry, catalog)
    if boundary is not None:
        return DefinitionValidationOutcome(valid=False, definition=None, issues=(boundary,))
    current_registry = get_production_registry() if registry is None else registry
    current_catalog = get_production_capability_catalog() if catalog is None else catalog

    try:
        fatal_code = preflight_condition_tree(node)
    except Exception:
        fatal_code = "condition_preflight_error"
    if fatal_code is not None:
        return DefinitionValidationOutcome(
            valid=False, definition=None,
            issues=(_issue(fatal_code, source, DEFAULT_ROOT_NODE_ID),),
        )

    issues: list[DefinitionIssue] = []
    bindings: list[ValidatedNodeBinding] = []

    def visit(current: Any, node_path: str) -> FrozenMapping | None:
        if not isinstance(current, Mapping):
            issues.append(_issue("condition_node_not_mapping", source, node_path))
            return None
        try:
            keys = tuple(current.keys())
        except Exception:
            issues.append(_issue("condition_node_not_mapping", source, node_path))
            return None
        if "type" not in keys:
            issues.append(_issue("condition_type_missing", source, node_path))
            if keys:
                issues.append(_issue("condition_unknown_fields", source, node_path))
            return None
        try:
            raw_type = current["type"]
        except Exception:
            issues.append(_issue("condition_type_not_string", source, node_path))
            return None
        if type(raw_type) is not str:
            issues.append(_issue("condition_type_not_string", source, node_path))
            return None
        normalized_type = raw_type.strip().upper()
        if not normalized_type:
            issues.append(_issue("condition_type_blank", source, node_path))
            return None

        if normalized_type in _LOGICAL_OPERATORS:
            unknown = set(keys) - {"type", "children"}
            if unknown or any(type(key) is not str for key in keys):
                issues.append(_issue("condition_unknown_fields", source, node_path))
            if "children" not in keys:
                issues.append(_issue("condition_children_missing", source, node_path))
                return None
            try:
                children = current["children"]
            except Exception:
                issues.append(_issue("condition_children_not_list", source, node_path))
                return None
            if type(children) is not list:
                issues.append(_issue("condition_children_not_list", source, node_path))
                return None
            if normalized_type in ("AND", "OR") and not children:
                issues.append(_issue("condition_empty_operator", source, node_path))
            if normalized_type == "NOT" and len(children) != 1:
                issues.append(_issue("condition_not_arity", source, node_path))
            binding = ValidatedNodeBinding(
                node_id=node_path, node_path=node_path,
                node_kind=ValidatedNodeKind.LOGICAL,
                requested_type=normalized_type, canonical_type=normalized_type,
                predicate_version=None, parameters=FrozenMapping(),
                required_capabilities=(), child_count=len(children),
            )
            bindings.append(binding)
            normalized_children = tuple(
                visit(child, f"{node_path}.children.{index}")
                for index, child in enumerate(children)
            )
            if any(item is None for item in normalized_children):
                return None
            return FrozenMapping({"type": normalized_type, "children": normalized_children})

        if "children" in keys and "params" not in keys:
            issues.append(_issue("unknown_operator", source, node_path))
            return None

        unknown = set(keys) - {"type", "params"}
        if unknown or any(type(key) is not str for key in keys):
            issues.append(_issue("condition_unknown_fields", source, node_path))
            return None
        try:
            definition = current_registry.lookup(normalized_type)
        except (PredicateRegistryError, TypeError, ValueError):
            definition = None
        if definition is None:
            safe_id = normalized_type if _PREDICATE_ID.fullmatch(normalized_type) else None
            issues.append(_issue("unknown_predicate", source, node_path, predicate_id=safe_id))
            return None
        if "params" not in keys:
            issues.append(_issue(
                "condition_params_missing", source, node_path,
                predicate_id=definition.predicate_id,
            ))
            return None
        try:
            parameters = current["params"]
        except Exception:
            parameters = None
        if not isinstance(parameters, Mapping):
            issues.append(_issue(
                "condition_params_not_mapping", source, node_path,
                predicate_id=definition.predicate_id,
            ))
            return None
        outcome = definition.parameter_schema.validate(parameters)
        if not outcome.valid:
            issues.extend(_parameter_issue(item, source, node_path) for item in outcome.issues)
            return None
        assert outcome.normalized_inputs is not None
        capability_pairs: list[tuple[str, str]] = []
        for requirement in definition.required_capabilities:
            found = current_catalog.lookup(requirement.capability_id)
            if isinstance(found, CapabilityCatalogMiss) or found.capability_version != requirement.capability_version:
                issues.append(_issue(
                    "predicate_capability_incompatible", source, node_path,
                    predicate_id=definition.predicate_id,
                ))
                return None
            capability_pairs.append((requirement.capability_id, requirement.capability_version))
        bindings.append(ValidatedNodeBinding(
            node_id=node_path, node_path=node_path,
            node_kind=ValidatedNodeKind.PREDICATE,
            requested_type=normalized_type,
            canonical_type=definition.predicate_id,
            predicate_version=definition.predicate_version,
            parameters=outcome.normalized_inputs,
            required_capabilities=tuple(capability_pairs),
            child_count=None,
        ))
        return FrozenMapping({"type": definition.predicate_id, "params": outcome.normalized_inputs})

    normalized = visit(node, DEFAULT_ROOT_NODE_ID)
    if issues:
        return DefinitionValidationOutcome(valid=False, definition=None, issues=tuple(issues))
    assert normalized is not None
    definition = ValidatedConditionDefinition(
        source=source, normalized_condition=normalized, node_bindings=tuple(bindings)
    )
    return DefinitionValidationOutcome(valid=True, definition=definition, issues=())


def _document_issue(code: str, source_name: str) -> YogaRuleSetValidationOutcome:
    identity = RuleSourceIdentity(source_name=source_name)
    return YogaRuleSetValidationOutcome(
        valid=False, rules=(), issues=(_issue(code, identity, "yoga.document"),)
    )


def validate_yoga_rules(
    records: Any,
    *,
    source_name: str,
    registry: PredicateRegistry | None = None,
    catalog: CapabilityCatalog | None = None,
) -> YogaRuleSetValidationOutcome:
    """Strictly validate parsed F1 Yoga records without registration/evaluation."""

    _validate_source_name(source_name)
    if type(records) is not list:
        return _document_issue("yoga_document_root_not_list", source_name)
    validated: list[ValidatedYogaRule] = []
    all_issues: list[DefinitionIssue] = []
    first_ids: set[str] = set()

    for index, record in enumerate(records):
        base_source = RuleSourceIdentity(source_name=source_name, rule_index=index)
        if not isinstance(record, Mapping):
            all_issues.append(_issue("yoga_rule_not_mapping", base_source, "yoga.rule"))
            continue
        try:
            keys = tuple(record.keys())
        except Exception:
            all_issues.append(_issue("yoga_rule_not_mapping", base_source, "yoga.rule"))
            continue
        try:
            raw_id = record["id"] if "id" in keys else None
        except Exception:
            raw_id = None
        rule_id = raw_id if isinstance(raw_id, str) and _RULE_ID.fullmatch(raw_id) else None
        rule_source = RuleSourceIdentity(
            source_name=source_name, rule_id=rule_id, rule_index=index
        )
        record_issues: list[DefinitionIssue] = []
        for required in YOGA_REQUIRED_FIELDS:
            if required not in keys:
                record_issues.append(_issue(
                    "yoga_rule_missing_field", rule_source, "yoga.rule",
                    details={"field": required},
                ))
        if any(type(key) is not str for key in keys) or set(keys) - YOGA_ALLOWED_FIELDS:
            record_issues.append(_issue("yoga_rule_unknown_fields", rule_source, "yoga.rule"))
        if "id" in keys and rule_id is None:
            record_issues.append(_issue("yoga_rule_id_invalid", rule_source, "yoga.rule"))

        duplicate = False
        if rule_id is not None:
            if rule_id in first_ids:
                duplicate = True
                record_issues.append(_issue("duplicate_rule_id", rule_source, "yoga.rule"))
            else:
                first_ids.add(rule_id)

        condition_outcome: DefinitionValidationOutcome | None = None
        if "conditions" in keys:
            try:
                condition_node = record["conditions"]
            except Exception:
                condition_node = None
            if not isinstance(condition_node, Mapping):
                record_issues.append(_issue(
                    "yoga_conditions_not_mapping", rule_source, DEFAULT_ROOT_NODE_ID
                ))
            else:
                condition_outcome = validate_condition_definition(
                    condition_node, source=rule_source, registry=registry, catalog=catalog
                )
                record_issues.extend(condition_outcome.issues)

        if not record_issues and not duplicate and condition_outcome is not None and condition_outcome.valid:
            assert rule_id is not None and condition_outcome.definition is not None
            normalized_record = dict(record)
            normalized_record["conditions"] = condition_outcome.definition.normalized_condition
            try:
                frozen_record = FrozenMapping(normalized_record)
            except Exception:
                record_issues.append(_issue("yoga_unsafe_content", rule_source, "yoga.rule"))
            else:
                validated.append(ValidatedYogaRule(
                    rule_id=rule_id,
                    source=rule_source,
                    rule=frozen_record,
                    condition=condition_outcome.definition,
                ))
        all_issues.extend(record_issues)

    return YogaRuleSetValidationOutcome(
        valid=not all_issues,
        rules=tuple(validated),
        issues=tuple(all_issues),
    )


def validate_yoga_rule_file(
    path: str | Path,
    *,
    source_name: str | None = None,
    registry: PredicateRegistry | None = None,
    catalog: CapabilityCatalog | None = None,
) -> YogaRuleSetValidationOutcome:
    """Parse and strictly validate one explicit YAML file without side effects."""

    supplied = Path(path)
    logical_name = supplied.name if source_name is None else source_name
    _validate_source_name(logical_name)
    if not supplied.is_absolute():
        return _document_issue("yoga_path_not_absolute", logical_name)
    if not supplied.exists() or not supplied.is_file():
        return _document_issue("yoga_file_missing", logical_name)
    try:
        payload = supplied.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return _document_issue("yoga_file_unreadable", logical_name)
    try:
        records = yaml.safe_load(payload)
    except ConstructorError:
        return _document_issue("yoga_unsafe_yaml", logical_name)
    except yaml.YAMLError:
        return _document_issue("yoga_invalid_yaml", logical_name)
    return validate_yoga_rules(
        records, source_name=logical_name, registry=registry, catalog=catalog
    )


__all__ = (
    "DEFINITION_SCHEMA_VERSION", "DefinitionIssue", "DefinitionIssueSeverity",
    "DefinitionValidationOutcome", "RuleSourceIdentity", "ValidatedConditionDefinition",
    "ValidatedNodeBinding", "ValidatedNodeKind", "ValidatedYogaRule",
    "YogaRuleSetValidationOutcome", "definition_semantic_json_bytes",
    "definition_issue_projection", "definition_issues_json_bytes",
    "definition_issues_sha256",
    "definition_semantic_projection", "definition_semantic_sha256",
    "definition_source_json_bytes", "definition_source_projection",
    "definition_source_sha256", "validate_condition_definition",
    "validate_yoga_rule_file", "validate_yoga_rules",
)
