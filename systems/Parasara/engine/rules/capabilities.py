"""Versioned predicate capabilities and read-only compatibility inspection.

WP06 deliberately keeps this boundary separate from predicate execution.  The
adapters classify existing Stage-01 shapes; they never prepare or mutate them.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
import math
import re
from typing import Any

from systems.Parasara.engine.rules.canonical import (
    FrozenMapping,
    canonical_json_bytes,
    freeze_canonical,
)
from systems.Parasara.engine.rules.models import PredicateError
from systems.Parasara.engine.rules.parameters import (
    CANONICAL_PLANETS,
    FUNCTIONAL_ROLE_VALUES,
)


_CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_PARAMETER_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_SAFE_CODE = re.compile(r"^[a-z][a-z0-9_]*$")
_SIGNS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)
_MISSING = object()
_CONTRACT_VERSION = "1.0.0"


class CapabilityDefinitionError(ValueError):
    pass


class CapabilityCatalogError(ValueError):
    pass


class CapabilityCatalogFrozenError(CapabilityCatalogError):
    pass


class CapabilityRequirementError(ValueError):
    pass


class ContentKind(str, Enum):
    COLLECTION = "collection"
    MAPPING = "mapping"
    SCALAR = "scalar"
    GRAPH = "graph"
    ENTITY_FIELDS = "entity_fields"


class EmptyPolicy(str, Enum):
    READY_EMPTY = "ready_empty"
    EMPTY_NOT_READY = "empty_not_ready"


class CapabilityReadiness(str, Enum):
    READY = "ready"
    READY_EMPTY = "ready_empty"
    MISSING = "missing"
    MALFORMED = "malformed"
    VERSION_MISMATCH = "version_mismatch"
    UNSUPPORTED = "unsupported"


class CapabilityFactState(str, Enum):
    PRESENT = "present"
    ABSENT_ENTITY = "absent_entity"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    MALFORMED_CAPABILITY = "malformed_capability"
    VERSION_MISMATCH = "version_mismatch"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"


def _valid_capability_id(value: Any, *, error_type: type[ValueError]) -> str:
    if not isinstance(value, str) or not _CAPABILITY_ID.fullmatch(value):
        raise error_type("capability_id must be a canonical lowercase ASCII dotted identifier")
    return value


def _valid_version(value: Any, *, error_type: type[ValueError]) -> str:
    if not isinstance(value, str) or not _SEMVER.fullmatch(value):
        raise error_type("capability_version must be strict MAJOR.MINOR.PATCH SemVer")
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilityDefinition:
    capability_id: str
    capability_version: str
    description: str
    system_scope: str
    content_kind: ContentKind
    empty_policy: EmptyPolicy
    recoverable_when_missing: bool

    def __post_init__(self) -> None:
        _valid_capability_id(self.capability_id, error_type=CapabilityDefinitionError)
        _valid_version(self.capability_version, error_type=CapabilityDefinitionError)
        if not isinstance(self.description, str) or not self.description or self.description.strip() != self.description:
            raise CapabilityDefinitionError("description must be a non-empty trimmed factual string")
        if self.system_scope != "parasara":
            raise CapabilityDefinitionError("system_scope must be parasara")
        if not isinstance(self.content_kind, ContentKind):
            raise CapabilityDefinitionError("content_kind must be a ContentKind")
        if not isinstance(self.empty_policy, EmptyPolicy):
            raise CapabilityDefinitionError("empty_policy must be an EmptyPolicy")
        if type(self.recoverable_when_missing) is not bool:
            raise CapabilityDefinitionError("recoverable_when_missing must be an actual Boolean")

    def metadata(self) -> FrozenMapping:
        return FrozenMapping(
            {
                "capability_id": self.capability_id,
                "capability_version": self.capability_version,
                "description": self.description,
                "system_scope": self.system_scope,
                "content_kind": self.content_kind,
                "empty_policy": self.empty_policy,
                "recoverable_when_missing": self.recoverable_when_missing,
            }
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilityCatalogMiss:
    capability_id: str
    readiness: CapabilityReadiness = CapabilityReadiness.UNSUPPORTED

    def __post_init__(self) -> None:
        _valid_capability_id(self.capability_id, error_type=CapabilityCatalogError)
        if self.readiness is not CapabilityReadiness.UNSUPPORTED:
            raise CapabilityCatalogError("catalog miss readiness must be unsupported")


def _normalize_lookup_id(value: Any) -> str:
    if not isinstance(value, str):
        raise CapabilityCatalogError("capability lookup ID must be a string")
    normalized = value.strip().lower()
    if not _CAPABILITY_ID.fullmatch(normalized):
        raise CapabilityCatalogError("capability lookup ID is malformed")
    return normalized


class CapabilityCatalog:
    __slots__ = ("__definitions", "__frozen", "__ready")

    def __init__(self) -> None:
        self.__definitions: dict[str, CapabilityDefinition] = {}
        self.__frozen = False
        self.__ready = False

    @property
    def is_frozen(self) -> bool:
        return self.__frozen

    @property
    def is_ready(self) -> bool:
        return self.__ready

    def register(self, definition: CapabilityDefinition) -> CapabilityDefinition:
        if self.__frozen:
            raise CapabilityCatalogFrozenError("capability catalog is finalized and read-only")
        if not isinstance(definition, CapabilityDefinition):
            raise CapabilityCatalogError("catalog accepts CapabilityDefinition objects only")
        if definition.capability_id in self.__definitions:
            raise CapabilityCatalogError("duplicate capability definition")
        self.__definitions[definition.capability_id] = definition
        return definition

    def finalize(self) -> "CapabilityCatalog":
        if self.__frozen:
            raise CapabilityCatalogFrozenError("capability catalog is already finalized")
        self.__frozen = True
        self.__ready = True
        return self

    def lookup(self, capability_id: Any) -> CapabilityDefinition | CapabilityCatalogMiss:
        normalized = _normalize_lookup_id(capability_id)
        return self.__definitions.get(normalized) or CapabilityCatalogMiss(capability_id=normalized)

    def capability_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self.__definitions))

    def definitions(self) -> tuple[CapabilityDefinition, ...]:
        return tuple(self.__definitions[item] for item in self.capability_ids())

    def metadata_snapshot(self) -> FrozenMapping:
        return FrozenMapping({item.capability_id: item.metadata() for item in self.definitions()})


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilityRequirement:
    capability_id: str
    capability_version: str
    required: bool
    when_parameters_present: tuple[str, ...]

    def __post_init__(self) -> None:
        _valid_capability_id(self.capability_id, error_type=CapabilityRequirementError)
        _valid_version(self.capability_version, error_type=CapabilityRequirementError)
        if type(self.required) is not bool:
            raise CapabilityRequirementError("required must be an actual Boolean")
        if not isinstance(self.when_parameters_present, tuple):
            raise CapabilityRequirementError("when_parameters_present must be an immutable tuple")
        if any(not isinstance(item, str) or not _PARAMETER_NAME.fullmatch(item) for item in self.when_parameters_present):
            raise CapabilityRequirementError("conditional parameter names must be canonical")
        if len(set(self.when_parameters_present)) != len(self.when_parameters_present):
            raise CapabilityRequirementError("conditional parameter names must be unique")
        if self.when_parameters_present != tuple(sorted(self.when_parameters_present)):
            raise CapabilityRequirementError("conditional parameter names must be sorted")

    def metadata(self) -> FrozenMapping:
        return FrozenMapping(
            {
                "capability_id": self.capability_id,
                "capability_version": self.capability_version,
                "required": self.required,
                "when_parameters_present": self.when_parameters_present,
            }
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilityCompatibilityIssue:
    predicate_id: str
    capability_id: str
    code: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilityCompatibilityResult:
    compatible: bool
    issues: tuple[CapabilityCompatibilityIssue, ...]

    def __post_init__(self) -> None:
        if type(self.compatible) is not bool or not isinstance(self.issues, tuple):
            raise TypeError("compatibility result fields have invalid types")
        if self.compatible is bool(self.issues):
            raise ValueError("compatible is true exactly when issues are empty")


def validate_predicate_capabilities(definition: Any, catalog: CapabilityCatalog | None = None) -> CapabilityCompatibilityResult:
    current = get_production_capability_catalog() if catalog is None else catalog
    predicate_id = getattr(definition, "predicate_id", "UNKNOWN")
    requirements = getattr(definition, "required_capabilities", None)
    issues: list[CapabilityCompatibilityIssue] = []
    if not isinstance(requirements, tuple):
        return CapabilityCompatibilityResult(
            compatible=False,
            issues=(CapabilityCompatibilityIssue(predicate_id=predicate_id, capability_id="invalid.requirements", code="invalid_requirement_container"),),
        )
    seen: dict[str, str] = {}
    schema = getattr(definition, "parameter_schema", None)
    parameter_names = {item.name for item in getattr(schema, "specifications", ())}
    for item in requirements:
        if not isinstance(item, CapabilityRequirement):
            issues.append(CapabilityCompatibilityIssue(predicate_id=predicate_id, capability_id="invalid.requirement", code="invalid_requirement_type"))
            continue
        if item.capability_id in seen:
            code = "conflicting_requirement_version" if seen[item.capability_id] != item.capability_version else "duplicate_requirement"
            issues.append(CapabilityCompatibilityIssue(predicate_id=predicate_id, capability_id=item.capability_id, code=code))
        else:
            seen[item.capability_id] = item.capability_version
        found = current.lookup(item.capability_id)
        if isinstance(found, CapabilityCatalogMiss):
            issues.append(CapabilityCompatibilityIssue(predicate_id=predicate_id, capability_id=item.capability_id, code="unknown_capability"))
        elif found.capability_version != item.capability_version:
            issues.append(CapabilityCompatibilityIssue(predicate_id=predicate_id, capability_id=item.capability_id, code="capability_version_mismatch"))
        for parameter in item.when_parameters_present:
            if parameter not in parameter_names:
                issues.append(CapabilityCompatibilityIssue(predicate_id=predicate_id, capability_id=item.capability_id, code="unknown_conditional_parameter"))
    return CapabilityCompatibilityResult(compatible=not issues, issues=tuple(issues))


def validate_registry_capabilities(registry: Any, catalog: CapabilityCatalog | None = None) -> CapabilityCompatibilityResult:
    issues = tuple(
        issue
        for definition in registry.canonical_definitions()
        for issue in validate_predicate_capabilities(definition, catalog).issues
    )
    return CapabilityCompatibilityResult(compatible=not issues, issues=issues)


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilityInspection:
    capability_id: str
    expected_version: str
    observed_version: str | None
    readiness: CapabilityReadiness
    source_kind: str | None
    content_empty: bool
    issues: tuple[str, ...]

    def __post_init__(self) -> None:
        _valid_capability_id(self.capability_id, error_type=ValueError)
        _valid_version(self.expected_version, error_type=ValueError)
        if self.observed_version is not None:
            _valid_version(self.observed_version, error_type=ValueError)
        if not isinstance(self.readiness, CapabilityReadiness):
            raise TypeError("readiness must be CapabilityReadiness")
        if self.source_kind is not None and (
            not isinstance(self.source_kind, str) or not _SAFE_CODE.fullmatch(self.source_kind)
        ):
            raise ValueError("source_kind must be a safe non-empty identifier")
        if type(self.content_empty) is not bool or not isinstance(self.issues, tuple) or any(
            type(item) is not str or not _SAFE_CODE.fullmatch(item) for item in self.issues
        ):
            raise TypeError("inspection content_empty/issues have invalid types")
        if self.readiness is CapabilityReadiness.READY and self.content_empty:
            raise ValueError("ready content must be nonempty")
        if self.readiness is CapabilityReadiness.READY_EMPTY and not self.content_empty:
            raise ValueError("ready_empty content must be explicitly empty")
        if self.readiness in (CapabilityReadiness.MISSING, CapabilityReadiness.UNSUPPORTED):
            if self.observed_version is not None or self.source_kind is not None or self.content_empty:
                raise ValueError("missing/unsupported inspection cannot claim observed content")
        elif self.source_kind is None:
            raise ValueError("present or malformed content requires a safe source kind")
        if self.readiness is CapabilityReadiness.VERSION_MISMATCH and self.observed_version is None:
            raise ValueError("version mismatch requires an observed version")
        if self.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY) and self.issues:
            raise ValueError("ready inspections cannot contain issues")


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilityFactObservation:
    capability_id: str
    capability_version: str
    state: CapabilityFactState
    entity_kind: str | None
    entity_id: str | None
    value_present: bool
    value: Any = None
    issues: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _valid_capability_id(self.capability_id, error_type=ValueError)
        _valid_version(self.capability_version, error_type=ValueError)
        if not isinstance(self.state, CapabilityFactState) or type(self.value_present) is not bool:
            raise TypeError("observation state/value_present have invalid types")
        if (self.entity_kind is None) is not (self.entity_id is None):
            raise ValueError("entity kind and ID must be supplied together")
        if self.entity_kind is not None:
            if not _SAFE_CODE.fullmatch(self.entity_kind) or self.entity_id.strip() != self.entity_id or not self.entity_id:
                raise ValueError("entity identity must be canonical")
            if self.entity_kind == "planet" and self.entity_id not in CANONICAL_PLANETS:
                raise ValueError("planet entity ID must use the canonical planet catalog")
        if self.state is CapabilityFactState.PRESENT:
            if not self.value_present or self.value is None:
                raise ValueError("present observation requires value_present")
            object.__setattr__(self, "value", freeze_canonical(self.value, path="$.value"))
        elif self.value_present or self.value is not None:
            raise ValueError("non-present observation cannot carry a value")
        if not isinstance(self.issues, tuple) or any(
            type(item) is not str or not _SAFE_CODE.fullmatch(item) for item in self.issues
        ):
            raise TypeError("issues must be an immutable string tuple")


def _inspection(capability_id: str, expected: str, readiness: CapabilityReadiness, *, source: str | None = None, empty: bool = False, issues: tuple[str, ...] = (), observed: str | None = None) -> CapabilityInspection:
    if readiness not in (CapabilityReadiness.MISSING, CapabilityReadiness.UNSUPPORTED):
        observed = _CONTRACT_VERSION if observed is None else observed
    return CapabilityInspection(
        capability_id=capability_id,
        expected_version=expected,
        observed_version=observed,
        readiness=readiness,
        source_kind=source,
        content_empty=empty,
        issues=issues,
    )


def _attr(value: Any, name: str) -> Any:
    try:
        return getattr(value, name)
    except AttributeError:
        return _MISSING


def _versioned(result: CapabilityInspection, expected: str) -> CapabilityInspection:
    if result.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY) and result.observed_version != expected:
        return _inspection(result.capability_id, expected, CapabilityReadiness.VERSION_MISMATCH, source=result.source_kind, empty=result.content_empty, issues=("contract_version_mismatch",), observed=result.observed_version)
    return result


def _planet_rows(astro: Any) -> tuple[Any, tuple[str, ...]]:
    planets = _attr(astro, "planets")
    if planets is _MISSING:
        return _MISSING, ("missing_attribute",)
    if planets is None:
        return None, ("explicit_none",)
    if not isinstance(planets, (list, tuple)):
        return planets, ("wrong_container_type",)
    names: list[str] = []
    for row in planets:
        name = _attr(row, "name")
        if name not in CANONICAL_PLANETS:
            return planets, ("malformed_planet",)
        if name in names:
            return planets, ("duplicate_planet_id",)
        names.append(name)
        sign = _attr(row, "sign")
        if sign is not _MISSING and sign is not None and sign not in _SIGNS:
            return planets, ("malformed_planet_sign",)
        degree = _attr(row, "degree")
        if degree is not _MISSING and degree is not None and (isinstance(degree, bool) or not isinstance(degree, (int, float)) or not math.isfinite(degree)):
            return planets, ("malformed_planet_degree",)
    return planets, ()


def _inspect_planets(astro: Any, capability_id: str, expected: str) -> CapabilityInspection:
    planets, issues = _planet_rows(astro)
    if planets is _MISSING or planets is None:
        return _inspection(capability_id, expected, CapabilityReadiness.MISSING, issues=issues)
    if issues:
        return _versioned(_inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="normalized_planets", empty=isinstance(planets, (list, tuple)) and not planets, issues=issues), expected)
    if not planets:
        return _versioned(_inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="normalized_planets", empty=True, issues=("empty_not_ready",)), expected)
    return _versioned(_inspection(capability_id, expected, CapabilityReadiness.READY, source="normalized_planets"), expected)


def _inspect_placements(astro: Any, capability_id: str, expected: str) -> CapabilityInspection:
    base = _inspect_planets(astro, capability_id, expected)
    if base.readiness is not CapabilityReadiness.READY:
        return base
    planets, _ = _planet_rows(astro)
    for row in planets:
        house = _attr(row, "house")
        if house is _MISSING or house is None:
            return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="planet_house_fields", issues=("house_unavailable",))
        if isinstance(house, bool) or not isinstance(house, int) or not 1 <= house <= 12:
            return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="planet_house_fields", issues=("invalid_house",))
    return _versioned(_inspection(capability_id, expected, CapabilityReadiness.READY, source="planet_house_fields"), expected)


def _enrichments(astro: Any) -> tuple[Any, tuple[str, ...]]:
    value = _attr(astro, "enrichments")
    if value is _MISSING:
        return _MISSING, ("missing_enrichments",)
    if value is None:
        return None, ("explicit_none",)
    if not isinstance(value, Mapping):
        return value, ("wrong_enrichments_type",)
    if "aspects" not in value:
        return _MISSING, ("missing_aspects_key",)
    if value["aspects"] is None:
        return None, ("explicit_none",)
    return value["aspects"], ()


def _inspect_basic_aspects(astro: Any, capability_id: str, expected: str) -> CapabilityInspection:
    value, issues = _enrichments(astro)
    if value is _MISSING or value is None:
        return _inspection(capability_id, expected, CapabilityReadiness.MISSING, issues=issues)
    if isinstance(value, Mapping):
        return _inspection(capability_id, expected, CapabilityReadiness.MISSING, issues=("representation_mismatch",))
    if not isinstance(value, list):
        return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="legacy_basic_conjunction_list", issues=("wrong_representation_type",))
    for edge in value:
        if not isinstance(edge, Mapping) or any(
            not isinstance(edge.get(key), str) for key in ("from", "to", "type")
        ):
            return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="legacy_basic_conjunction_list", empty=not value, issues=("malformed_edge",))
    status = CapabilityReadiness.READY_EMPTY if not value else CapabilityReadiness.READY
    return _versioned(_inspection(capability_id, expected, status, source="legacy_basic_conjunction_list", empty=not value), expected)


def _inspect_graph(astro: Any, capability_id: str, expected: str) -> CapabilityInspection:
    value, issues = _enrichments(astro)
    if value is _MISSING or value is None:
        return _inspection(capability_id, expected, CapabilityReadiness.MISSING, issues=issues)
    if isinstance(value, list):
        return _inspection(capability_id, expected, CapabilityReadiness.MISSING, issues=("representation_mismatch",))
    if not isinstance(value, Mapping):
        return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="legacy_whole_sign_graph", issues=("wrong_representation_type",))
    if "edges" not in value:
        return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="legacy_whole_sign_graph", empty=not value, issues=("missing_edges",))
    edges = value["edges"]
    if not isinstance(edges, (list, tuple)):
        return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="legacy_whole_sign_graph", issues=("wrong_edges_type",))
    for edge in edges:
        if not isinstance(edge, Mapping) or not isinstance(edge.get("source"), str) or (edge.get("target") is not None and not isinstance(edge.get("target"), str)):
            return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="legacy_whole_sign_graph", empty=not edges, issues=("malformed_edge",))
    observed = value.get("capability_version", _CONTRACT_VERSION)
    if not isinstance(observed, str) or not _SEMVER.fullmatch(observed):
        return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="legacy_whole_sign_graph", empty=not edges, issues=("invalid_capability_version",))
    status = CapabilityReadiness.READY_EMPTY if not edges else CapabilityReadiness.READY
    return _versioned(_inspection(capability_id, expected, status, source="legacy_whole_sign_graph", empty=not edges, observed=observed), expected)


def _inspect_lagna(astro: Any, capability_id: str, expected: str) -> CapabilityInspection:
    value = _attr(astro, "lagna_sign")
    if value is _MISSING:
        return _inspection(capability_id, expected, CapabilityReadiness.MISSING, issues=("missing_attribute",))
    if value is None:
        return _inspection(capability_id, expected, CapabilityReadiness.MISSING, issues=("explicit_none",))
    if value == "":
        return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="astro_lagna_sign", empty=True, issues=("empty_not_ready",))
    if value not in _SIGNS:
        return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="astro_lagna_sign", issues=("unknown_sign",))
    return _versioned(_inspection(capability_id, expected, CapabilityReadiness.READY, source="astro_lagna_sign"), expected)


def _role_mapping(astro: Any) -> tuple[Any, tuple[str, ...]]:
    derived = _attr(astro, "derived")
    if derived is _MISSING or derived is None:
        return _MISSING, ("prepared_roles_absent",)
    if not isinstance(derived, Mapping):
        return derived, ("wrong_derived_type",)
    if "functional_roles" not in derived:
        return _MISSING, ("prepared_roles_absent",)
    value = derived["functional_roles"]
    if value is None:
        return None, ("explicit_none",)
    return value, ()


def _inspect_roles(astro: Any, capability_id: str, expected: str) -> CapabilityInspection:
    value, issues = _role_mapping(astro)
    if value is _MISSING or value is None:
        return _inspection(capability_id, expected, CapabilityReadiness.MISSING, issues=issues)
    if not isinstance(value, Mapping):
        return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="derived_functional_roles", issues=("wrong_role_mapping_type",))
    for name, row in value.items():
        if name not in CANONICAL_PLANETS or not isinstance(row, Mapping) or row.get("functional_role") not in FUNCTIONAL_ROLE_VALUES:
            return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="derived_functional_roles", empty=not value, issues=("malformed_role_fact",))
    status = CapabilityReadiness.READY_EMPTY if not value else CapabilityReadiness.READY
    return _versioned(_inspection(capability_id, expected, status, source="derived_functional_roles", empty=not value), expected)


def _exaltation_sources(astro: Any) -> tuple[Any, Any, tuple[str, ...]]:
    flag_values: dict[str, Any] = {}
    planets = _attr(astro, "planets")
    if isinstance(planets, (list, tuple)):
        for row in planets:
            name = _attr(row, "name")
            raw = _attr(row, "__dict__")
            flags = raw.get("flags", _MISSING) if isinstance(raw, Mapping) else _MISSING
            if flags is not _MISSING:
                if not isinstance(flags, Mapping) or "exalted" not in flags or type(flags["exalted"]) is not bool or name not in CANONICAL_PLANETS:
                    return None, None, ("malformed_planet_flags",)
                flag_values[name] = flags["exalted"]
    metadata = _attr(astro, "metadata")
    metadata_values = _MISSING
    if isinstance(metadata, Mapping) and "exaltations" in metadata:
        metadata_values = metadata["exaltations"]
        if not isinstance(metadata_values, Mapping):
            return None, None, ("malformed_exaltations_mapping",)
        for name, value in metadata_values.items():
            if name not in CANONICAL_PLANETS or isinstance(value, bool) is False and not isinstance(value, (int, float)) or isinstance(value, float) and not math.isfinite(value):
                return None, None, ("malformed_exaltation_fact",)
    flags_source = flag_values if flag_values else _MISSING
    if flags_source is not _MISSING and metadata_values is not _MISSING:
        for name in set(flags_source) & set(metadata_values):
            left, right = flags_source[name], metadata_values[name]
            if type(left) is not type(right) or left != right:
                return flags_source, metadata_values, ("conflicting_sources",)
    return flags_source, metadata_values, ()


def _inspect_exaltation(astro: Any, capability_id: str, expected: str) -> CapabilityInspection:
    flags, metadata, issues = _exaltation_sources(astro)
    if issues:
        return _inspection(capability_id, expected, CapabilityReadiness.MALFORMED, source="legacy_exaltation_sources", issues=issues)
    if flags is _MISSING and metadata is _MISSING:
        return _inspection(capability_id, expected, CapabilityReadiness.MISSING, issues=("exaltation_sources_absent",))
    source = "legacy_planet_flags" if metadata is _MISSING else ("legacy_metadata_exaltations" if flags is _MISSING else "legacy_exaltation_sources")
    size = (0 if flags is _MISSING else len(flags)) + (0 if metadata is _MISSING else len(metadata))
    status = CapabilityReadiness.READY_EMPTY if size == 0 else CapabilityReadiness.READY
    return _versioned(_inspection(capability_id, expected, status, source=source, empty=size == 0), expected)


_INSPECTORS = {
    "planets.normalized": _inspect_planets,
    "planets.house_placement": _inspect_placements,
    "aspects.basic_conjunction_list": _inspect_basic_aspects,
    "aspects.whole_sign_graph": _inspect_graph,
    "chart.lagna": _inspect_lagna,
    "roles.functional": _inspect_roles,
    "dignity.exaltation_facts": _inspect_exaltation,
}


def inspect_capability(astro: Any, requirement: CapabilityRequirement, catalog: CapabilityCatalog | None = None) -> CapabilityInspection:
    if not isinstance(requirement, CapabilityRequirement):
        raise CapabilityRequirementError("inspection requires CapabilityRequirement")
    current = get_production_capability_catalog() if catalog is None else catalog
    found = current.lookup(requirement.capability_id)
    if isinstance(found, CapabilityCatalogMiss):
        return _inspection(requirement.capability_id, requirement.capability_version, CapabilityReadiness.UNSUPPORTED, issues=("catalog_miss",))
    return _INSPECTORS[found.capability_id](astro, found.capability_id, requirement.capability_version)


def capability_catalog_fingerprint_bytes(catalog: CapabilityCatalog | None = None) -> bytes:
    current = get_production_capability_catalog() if catalog is None else catalog
    return canonical_json_bytes(
        {
            "definitions": current.metadata_snapshot(),
            "is_frozen": current.is_frozen,
            "is_ready": current.is_ready,
        }
    )


def capability_catalog_fingerprint_sha256(catalog: CapabilityCatalog | None = None) -> str:
    return hashlib.sha256(capability_catalog_fingerprint_bytes(catalog)).hexdigest()


def capability_inspection_to_data(inspection: CapabilityInspection) -> FrozenMapping:
    if not isinstance(inspection, CapabilityInspection):
        raise TypeError("inspection must be CapabilityInspection")
    return FrozenMapping(
        {
            "capability_id": inspection.capability_id,
            "expected_version": inspection.expected_version,
            "observed_version": inspection.observed_version,
            "readiness": inspection.readiness,
            "source_kind": inspection.source_kind,
            "content_empty": inspection.content_empty,
            "issues": inspection.issues,
        }
    )


def capability_inspection_json_bytes(inspection: CapabilityInspection) -> bytes:
    return canonical_json_bytes(capability_inspection_to_data(inspection))


def capability_fact_observation_to_data(observation: CapabilityFactObservation) -> FrozenMapping:
    if not isinstance(observation, CapabilityFactObservation):
        raise TypeError("observation must be CapabilityFactObservation")
    return FrozenMapping(
        {
            "capability_id": observation.capability_id,
            "capability_version": observation.capability_version,
            "state": observation.state,
            "entity_kind": observation.entity_kind,
            "entity_id": observation.entity_id,
            "value_present": observation.value_present,
            "value": observation.value,
            "issues": observation.issues,
        }
    )


def capability_fact_observation_json_bytes(observation: CapabilityFactObservation) -> bytes:
    return canonical_json_bytes(capability_fact_observation_to_data(observation))


def _unavailable_observation(inspection: CapabilityInspection, entity_kind: str | None, entity_id: str | None) -> CapabilityFactObservation:
    states = {
        CapabilityReadiness.MISSING: CapabilityFactState.CAPABILITY_UNAVAILABLE,
        CapabilityReadiness.MALFORMED: CapabilityFactState.MALFORMED_CAPABILITY,
        CapabilityReadiness.VERSION_MISMATCH: CapabilityFactState.VERSION_MISMATCH,
        CapabilityReadiness.UNSUPPORTED: CapabilityFactState.UNSUPPORTED_CAPABILITY,
    }
    return CapabilityFactObservation(
        capability_id=inspection.capability_id,
        capability_version=inspection.expected_version,
        state=states[inspection.readiness],
        entity_kind=entity_kind,
        entity_id=entity_id,
        value_present=False,
        issues=inspection.issues,
    )


def observe_capability_fact(astro: Any, requirement: CapabilityRequirement, *, entity_kind: str | None = None, entity_id: str | None = None, catalog: CapabilityCatalog | None = None) -> CapabilityFactObservation:
    inspection = inspect_capability(astro, requirement, catalog)
    if inspection.readiness not in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
        return _unavailable_observation(inspection, entity_kind, entity_id)
    capability_id = inspection.capability_id
    value = _MISSING
    if capability_id in ("planets.normalized", "planets.house_placement"):
        planets, _ = _planet_rows(astro)
        row = next((item for item in planets if _attr(item, "name") == entity_id), _MISSING)
        if row is not _MISSING:
            value = (
                _attr(row, "house")
                if capability_id == "planets.house_placement"
                else {
                    "name": _attr(row, "name"),
                    "sign": None if _attr(row, "sign") is _MISSING else _attr(row, "sign"),
                    "degree": None if _attr(row, "degree") is _MISSING else _attr(row, "degree"),
                    "house": None if _attr(row, "house") is _MISSING else _attr(row, "house"),
                }
            )
    elif capability_id == "roles.functional":
        roles, _ = _role_mapping(astro)
        if entity_id in roles:
            value = roles[entity_id]["functional_role"]
    elif capability_id == "dignity.exaltation_facts":
        flags, metadata, _ = _exaltation_sources(astro)
        if flags is not _MISSING and entity_id in flags:
            value = flags[entity_id]
        if metadata is not _MISSING and entity_id in metadata:
            value = metadata[entity_id]
    elif capability_id == "chart.lagna":
        value = _attr(astro, "lagna_sign")
    if value is _MISSING:
        return CapabilityFactObservation(capability_id=capability_id, capability_version=requirement.capability_version, state=CapabilityFactState.ABSENT_ENTITY, entity_kind=entity_kind, entity_id=entity_id, value_present=False, issues=("entity_absent",))
    return CapabilityFactObservation(capability_id=capability_id, capability_version=requirement.capability_version, state=CapabilityFactState.PRESENT, entity_kind=entity_kind, entity_id=entity_id, value_present=True, value=value, issues=())


_DIAGNOSTICS = {
    CapabilityReadiness.MISSING: ("missing_capability", "A required predicate capability is unavailable.", True),
    CapabilityReadiness.MALFORMED: ("malformed_capability", "A required predicate capability is malformed.", False),
    CapabilityReadiness.VERSION_MISMATCH: ("capability_version_mismatch", "A required predicate capability has an incompatible version.", True),
    CapabilityReadiness.UNSUPPORTED: ("unsupported_capability", "A required predicate capability is unsupported.", False),
}


def capability_error(predicate_id: str, inspection: CapabilityInspection, *, entity_kind: str | None = None, entity_id: str | None = None) -> PredicateError:
    if inspection.readiness not in _DIAGNOSTICS:
        raise ValueError("diagnostic adapter requires an unavailable inspection")
    from systems.Parasara.engine.rules.registry import get_production_registry

    definition = get_production_registry().lookup(predicate_id)
    canonical_id = predicate_id if definition is None else definition.predicate_id
    code, message, recoverable = _DIAGNOSTICS[inspection.readiness]
    details = {
        "predicate_id": canonical_id,
        "capability_id": inspection.capability_id,
        "expected_version": inspection.expected_version,
        "observed_version": inspection.observed_version,
        "readiness": inspection.readiness.value,
        "source_kind": inspection.source_kind,
        "entity_kind": entity_kind,
        "entity_id": entity_id,
        "issues": inspection.issues,
    }
    return PredicateError(code=code, message=message, predicate_id=canonical_id, details=details, recoverable=recoverable)


def _definition(capability_id: str, description: str, kind: ContentKind, policy: EmptyPolicy) -> CapabilityDefinition:
    return CapabilityDefinition(
        capability_id=capability_id,
        capability_version=_CONTRACT_VERSION,
        description=description,
        system_scope="parasara",
        content_kind=kind,
        empty_policy=policy,
        recoverable_when_missing=True,
    )


_PRODUCTION_CATALOG: CapabilityCatalog | None = None


def get_production_capability_catalog() -> CapabilityCatalog:
    global _PRODUCTION_CATALOG
    if _PRODUCTION_CATALOG is None:
        candidate = CapabilityCatalog()
        definitions = (
            _definition("planets.normalized", "Canonical normalized planet facts.", ContentKind.COLLECTION, EmptyPolicy.EMPTY_NOT_READY),
            _definition("planets.house_placement", "Canonical planet house-placement fields.", ContentKind.ENTITY_FIELDS, EmptyPolicy.EMPTY_NOT_READY),
            _definition("aspects.basic_conjunction_list", "Legacy normalized basic conjunction list.", ContentKind.COLLECTION, EmptyPolicy.READY_EMPTY),
            _definition("aspects.whole_sign_graph", "Legacy whole-sign aspect graph envelope.", ContentKind.GRAPH, EmptyPolicy.READY_EMPTY),
            _definition("chart.lagna", "Canonical chart Lagna sign.", ContentKind.SCALAR, EmptyPolicy.EMPTY_NOT_READY),
            _definition("roles.functional", "Explicit prepared functional-role facts.", ContentKind.MAPPING, EmptyPolicy.READY_EMPTY),
            _definition("dignity.exaltation_facts", "Legacy explicit exaltation facts.", ContentKind.MAPPING, EmptyPolicy.READY_EMPTY),
        )
        for item in definitions:
            candidate.register(item)
        candidate.finalize()
        _PRODUCTION_CATALOG = candidate
    return _PRODUCTION_CATALOG


__all__ = (
    "CapabilityCatalog", "CapabilityCatalogError", "CapabilityCatalogFrozenError",
    "CapabilityCatalogMiss", "CapabilityCompatibilityIssue", "CapabilityCompatibilityResult",
    "CapabilityDefinition", "CapabilityDefinitionError", "CapabilityFactObservation",
    "CapabilityFactState", "CapabilityInspection", "CapabilityReadiness",
    "CapabilityRequirement", "CapabilityRequirementError", "ContentKind", "EmptyPolicy",
    "capability_catalog_fingerprint_bytes", "capability_catalog_fingerprint_sha256",
    "capability_error", "capability_fact_observation_json_bytes",
    "capability_fact_observation_to_data", "capability_inspection_json_bytes",
    "capability_inspection_to_data", "get_production_capability_catalog", "inspect_capability",
    "observe_capability_fact", "validate_predicate_capabilities", "validate_registry_capabilities",
)
