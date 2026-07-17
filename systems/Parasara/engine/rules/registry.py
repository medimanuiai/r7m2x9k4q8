"""Immutable predicate definitions and deterministic Stage-01 registry bootstrap."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
import re
from typing import Any

from systems.Parasara.engine.rules.canonical import (
    FrozenMapping,
    canonical_json_bytes,
)
from systems.Parasara.engine.rules.capabilities import (
    CapabilityRequirement,
    get_production_capability_catalog,
    validate_registry_capabilities,
)
from systems.Parasara.engine.rules.parameters import (
    ASPECT_PARAMETER_SCHEMA,
    FUNCTIONAL_ROLE_PARAMETER_SCHEMA,
    HOUSE_OCCUPANT_PARAMETER_SCHEMA,
    PLANET_EXALTED_PARAMETER_SCHEMA,
    PLANET_IN_HOUSE_PARAMETER_SCHEMA,
    ParameterSchema,
)


_PREDICATE_ID = re.compile(r"^[A-Z][A-Z0-9_]*$")
_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_SCOPE = re.compile(r"^[a-z][a-z0-9_]*$")
_LOGICAL_OPERATORS = frozenset({"AND", "OR", "NOT"})


class PredicateDefinitionError(ValueError):
    """A predicate definition violates the locked metadata contract."""


class PredicateRegistryError(ValueError):
    """A registry operation or lookup violates the registry contract."""


class PredicateRegistryFrozenError(PredicateRegistryError):
    """Mutation was attempted after registry finalization."""


class CostClass(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def _validate_predicate_id(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not _PREDICATE_ID.fullmatch(value):
        raise PredicateDefinitionError(f"{field_name} must be a canonical uppercase ASCII predicate ID")
    if value in _LOGICAL_OPERATORS:
        raise PredicateDefinitionError(f"{field_name} cannot be a logical operator")
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class PredicateDefinition:
    """One immutable canonical predicate contract and its handler identity."""

    predicate_id: str
    predicate_version: str
    description: str
    parameter_schema: ParameterSchema
    required_capabilities: tuple[CapabilityRequirement, ...]
    cacheable: bool
    deterministic: bool
    cost_class: CostClass
    system_scope: str
    deprecated: bool = False
    replacement: str | None = None
    aliases: tuple[str, ...] = ()
    handler: Callable[..., Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        _validate_predicate_id(self.predicate_id, "predicate_id")
        if not isinstance(self.predicate_version, str) or not _SEMVER.fullmatch(self.predicate_version):
            raise PredicateDefinitionError("predicate_version must be Stage-01 MAJOR.MINOR.PATCH SemVer")
        if not isinstance(self.description, str) or not self.description or self.description.strip() != self.description:
            raise PredicateDefinitionError("description must be a non-empty trimmed string")
        if not isinstance(self.parameter_schema, ParameterSchema):
            raise PredicateDefinitionError("parameter_schema must be an executable ParameterSchema")
        if self.parameter_schema.predicate_id != self.predicate_id:
            raise PredicateDefinitionError("parameter schema predicate identity disagrees with definition")
        if self.parameter_schema.schema_version != self.predicate_version:
            raise PredicateDefinitionError("parameter schema version disagrees with predicate version")
        try:
            self.parameter_schema.metadata()
        except Exception as exc:
            raise PredicateDefinitionError("parameter schema metadata is not canonically fingerprintable") from exc
        if not isinstance(self.required_capabilities, tuple):
            raise PredicateDefinitionError("required_capabilities must be an immutable tuple")
        if any(not isinstance(item, CapabilityRequirement) for item in self.required_capabilities):
            raise PredicateDefinitionError("required_capabilities must contain CapabilityRequirement values")
        capability_ids = tuple(item.capability_id for item in self.required_capabilities)
        if len(set(capability_ids)) != len(capability_ids):
            raise PredicateDefinitionError("required_capabilities must be unique")
        if self.required_capabilities != tuple(
            sorted(self.required_capabilities, key=lambda item: (item.capability_id, item.when_parameters_present))
        ):
            raise PredicateDefinitionError("required_capabilities must use deterministic capability/condition order")
        if type(self.cacheable) is not bool or type(self.deterministic) is not bool:
            raise PredicateDefinitionError("cacheable and deterministic must be actual Booleans")
        if self.cacheable and not self.deterministic:
            raise PredicateDefinitionError("a nondeterministic predicate cannot be cacheable")
        try:
            cost_class = self.cost_class if isinstance(self.cost_class, CostClass) else CostClass(self.cost_class)
        except (TypeError, ValueError) as exc:
            raise PredicateDefinitionError("cost_class must be low, medium, or high") from exc
        object.__setattr__(self, "cost_class", cost_class)
        if not isinstance(self.system_scope, str) or not _SCOPE.fullmatch(self.system_scope):
            raise PredicateDefinitionError("system_scope must be a stable lowercase identifier")
        if type(self.deprecated) is not bool:
            raise PredicateDefinitionError("deprecated must be an actual Boolean")
        if self.replacement is not None:
            replacement = _validate_predicate_id(self.replacement, "replacement")
            if replacement == self.predicate_id:
                raise PredicateDefinitionError("replacement cannot reference the canonical predicate itself")
        if not isinstance(self.aliases, tuple):
            raise PredicateDefinitionError("aliases must be an immutable tuple")
        for alias in self.aliases:
            _validate_predicate_id(alias, "alias")
        if len(set(self.aliases)) != len(self.aliases):
            raise PredicateDefinitionError("aliases must be unique")
        if self.predicate_id in self.aliases:
            raise PredicateDefinitionError("aliases cannot include the canonical predicate ID")
        if self.replacement in self.aliases:
            raise PredicateDefinitionError("replacement cannot use an alias spelling")
        if self.aliases != tuple(sorted(self.aliases)):
            raise PredicateDefinitionError("aliases must use deterministic lexicographic order")
        if not callable(self.handler):
            raise PredicateDefinitionError("handler must be callable")


def _normalize_lookup_id(value: Any) -> str:
    if not isinstance(value, str):
        raise PredicateRegistryError("predicate lookup ID must be a string")
    normalized = value.strip().upper()
    if not normalized:
        raise PredicateRegistryError("predicate lookup ID cannot be blank")
    if not _PREDICATE_ID.fullmatch(normalized) or normalized in _LOGICAL_OPERATORS:
        raise PredicateRegistryError("predicate lookup ID is malformed or reserved")
    return normalized


class PredicateRegistry:
    """Validated registry with explicit build and frozen/read-only phases."""

    __slots__ = ("__definitions", "__aliases", "__handler_ids", "__frozen", "__ready")

    def __init__(self) -> None:
        self.__definitions: dict[str, PredicateDefinition] = {}
        self.__aliases: dict[str, str] = {}
        self.__handler_ids: dict[int, str] = {}
        self.__frozen = False
        self.__ready = False

    @property
    def is_frozen(self) -> bool:
        return self.__frozen

    @property
    def is_ready(self) -> bool:
        return self.__ready

    def _require_build_phase(self) -> None:
        if self.__frozen:
            raise PredicateRegistryFrozenError("predicate registry is finalized and read-only")

    def register(self, definition: PredicateDefinition) -> PredicateDefinition:
        self._require_build_phase()
        if not isinstance(definition, PredicateDefinition):
            raise PredicateRegistryError("registry accepts validated PredicateDefinition objects only")
        canonical_id = definition.predicate_id
        if canonical_id in self.__definitions or canonical_id in self.__aliases:
            raise PredicateRegistryError(f"duplicate or colliding predicate ID: {canonical_id}")
        collisions = set(definition.aliases) & (set(self.__definitions) | set(self.__aliases))
        if collisions:
            raise PredicateRegistryError(f"predicate alias collision: {min(collisions)}")
        handler_identity = id(definition.handler)
        if handler_identity in self.__handler_ids:
            raise PredicateRegistryError(
                "a handler already registered under another canonical ID; declare an alias instead"
            )

        # Mutate only after all definition, collision, and handler checks have passed.
        self.__definitions[canonical_id] = definition
        self.__handler_ids[handler_identity] = canonical_id
        for alias in definition.aliases:
            self.__aliases[alias] = canonical_id
        return definition

    def remove(self, predicate_id: str) -> PredicateDefinition:
        self._require_build_phase()
        normalized = _normalize_lookup_id(predicate_id)
        if normalized not in self.__definitions:
            raise PredicateRegistryError("only canonical definitions can be removed")
        item = self.__definitions.pop(normalized)
        self.__handler_ids.pop(id(item.handler), None)
        for alias in item.aliases:
            self.__aliases.pop(alias, None)
        return item

    def replace(self, definition: PredicateDefinition) -> PredicateDefinition:
        self._require_build_phase()
        if not isinstance(definition, PredicateDefinition):
            raise PredicateRegistryError("replacement must be a validated PredicateDefinition")
        if definition.predicate_id not in self.__definitions:
            raise PredicateRegistryError("replacement requires an existing canonical definition")
        old = self.remove(definition.predicate_id)
        try:
            return self.register(definition)
        except Exception:
            self.register(old)
            raise

    def reset(self) -> None:
        self._require_build_phase()
        self.__definitions.clear()
        self.__aliases.clear()
        self.__handler_ids.clear()
        self.__ready = False

    def finalize(self) -> "PredicateRegistry":
        self._require_build_phase()
        for item in self.__definitions.values():
            if item.replacement is not None and item.replacement not in self.__definitions:
                raise PredicateRegistryError(
                    f"replacement target is not a canonical definition: {item.replacement}"
                )

        for start in self.__definitions:
            seen: set[str] = set()
            current: str | None = start
            while current is not None:
                if current in seen:
                    raise PredicateRegistryError(f"predicate replacement cycle includes: {current}")
                seen.add(current)
                current = self.__definitions[current].replacement

        compatibility = validate_registry_capabilities(self, get_production_capability_catalog())
        if not compatibility.compatible:
            raise PredicateRegistryError(
                "predicate capability requirements are statically incompatible: "
                + compatibility.issues[0].code
            )

        self.__frozen = True
        self.__ready = True
        return self

    def lookup(self, predicate_id: Any) -> PredicateDefinition | None:
        normalized = _normalize_lookup_id(predicate_id)
        canonical_id = self.__aliases.get(normalized, normalized)
        return self.__definitions.get(canonical_id)

    def handler(self, predicate_id: Any) -> Callable[..., Any] | None:
        item = self.lookup(predicate_id)
        return None if item is None else item.handler

    def canonical_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self.__definitions))

    def exposed_ids(self) -> tuple[str, ...]:
        return tuple(sorted((*self.__definitions, *self.__aliases)))

    def canonical_definitions(self) -> tuple[PredicateDefinition, ...]:
        return tuple(self.__definitions[predicate_id] for predicate_id in self.canonical_ids())

    def metadata_snapshot(self) -> FrozenMapping:
        return FrozenMapping(
            {
                item.predicate_id: _definition_metadata(item)
                for item in self.canonical_definitions()
            }
        )


def _built_in_definitions() -> tuple[PredicateDefinition, ...]:
    # This explicit import is the one deterministic production bootstrap point.
    from systems.Parasara.engine.rules import canonical_predicates
    from systems.Parasara.engine.rules.planet_in_house import evaluate_planet_in_house

    return (
        PredicateDefinition(
            predicate_id="ASPECT_EXISTS",
            predicate_version="1.0.0",
            description="Reports whether an observed aspect edge satisfies the supplied filters.",
            parameter_schema=ASPECT_PARAMETER_SCHEMA,
            required_capabilities=(_requirement("aspects.whole_sign_graph"),),
            cacheable=True,
            deterministic=True,
            cost_class=CostClass.MEDIUM,
            system_scope="parasara",
            aliases=("ASPECT",),
            handler=canonical_predicates.evaluate_aspect_exists,
        ),
        PredicateDefinition(
            predicate_id="FUNCTIONAL_ROLE",
            predicate_version="1.0.0",
            description="Reports whether selected planets have an observed requested functional role.",
            parameter_schema=FUNCTIONAL_ROLE_PARAMETER_SCHEMA,
            required_capabilities=(
                _requirement("chart.lagna"),
                _requirement("planets.normalized"),
                _requirement("roles.functional"),
            ),
            cacheable=True,
            deterministic=True,
            cost_class=CostClass.MEDIUM,
            system_scope="parasara",
            handler=canonical_predicates.evaluate_functional_role,
        ),
        PredicateDefinition(
            predicate_id="HOUSE_OCCUPANT",
            predicate_version="1.0.0",
            description="Reports whether the requested planet occupies the requested house.",
            parameter_schema=HOUSE_OCCUPANT_PARAMETER_SCHEMA,
            required_capabilities=(
                _requirement("planets.house_placement"),
                _requirement("planets.normalized"),
            ),
            cacheable=True,
            deterministic=True,
            cost_class=CostClass.LOW,
            system_scope="parasara",
            handler=canonical_predicates.evaluate_house_occupant,
        ),
        PredicateDefinition(
            predicate_id="PLANET_EXALTED",
            predicate_version="1.0.0",
            description="Reports whether exaltation is observed for the requested planet.",
            parameter_schema=PLANET_EXALTED_PARAMETER_SCHEMA,
            required_capabilities=(
                _requirement("dignity.exaltation_facts"),
                _requirement("planets.normalized"),
            ),
            cacheable=True,
            deterministic=True,
            cost_class=CostClass.LOW,
            system_scope="parasara",
            handler=canonical_predicates.evaluate_planet_exalted,
        ),
        PredicateDefinition(
            predicate_id="PLANET_IN_HOUSE",
            predicate_version="1.0.0",
            description="Reports whether the requested planet occupies the requested house.",
            parameter_schema=PLANET_IN_HOUSE_PARAMETER_SCHEMA,
            required_capabilities=(
                _requirement("planets.house_placement"),
                _requirement("planets.normalized"),
            ),
            cacheable=True,
            deterministic=True,
            cost_class=CostClass.LOW,
            system_scope="parasara",
            handler=evaluate_planet_in_house,
        ),
    )


def _requirement(capability_id: str) -> CapabilityRequirement:
    return CapabilityRequirement(
        capability_id=capability_id,
        capability_version="1.0.0",
        required=True,
        when_parameters_present=(),
    )


_BOOTSTRAP_UNINITIALIZED = "uninitialized"
_BOOTSTRAP_BUILDING = "building"
_BOOTSTRAP_READY = "ready"
_BOOTSTRAP_FAILED = "failed"
_bootstrap_state = _BOOTSTRAP_UNINITIALIZED
_production_registry: PredicateRegistry | None = None


def bootstrap_production_registry() -> PredicateRegistry:
    """Build, finalize, and atomically publish the one production registry."""

    global _bootstrap_state, _production_registry
    if _bootstrap_state == _BOOTSTRAP_READY:
        if _production_registry is None or not _production_registry.is_ready:
            raise PredicateRegistryError("production registry readiness state is inconsistent")
        return _production_registry
    if _bootstrap_state == _BOOTSTRAP_BUILDING:
        raise PredicateRegistryError("recursive or partially initialized predicate bootstrap detected")
    if _bootstrap_state == _BOOTSTRAP_FAILED:
        raise PredicateRegistryError("predicate bootstrap previously failed; no partial registry was published")

    _bootstrap_state = _BOOTSTRAP_BUILDING
    try:
        candidate = PredicateRegistry()
        for item in _built_in_definitions():
            candidate.register(item)
        candidate.finalize()
    except Exception:
        _production_registry = None
        _bootstrap_state = _BOOTSTRAP_FAILED
        raise
    _production_registry = candidate
    _bootstrap_state = _BOOTSTRAP_READY
    return candidate


def get_production_registry() -> PredicateRegistry:
    return bootstrap_production_registry()


def _definition_metadata(item: PredicateDefinition) -> FrozenMapping:
    return FrozenMapping(
        {
            "aliases": item.aliases,
            "cacheable": item.cacheable,
            "cost_class": item.cost_class,
            "deprecated": item.deprecated,
            "description": item.description,
            "deterministic": item.deterministic,
            "parameter_schema": item.parameter_schema.metadata(),
            "predicate_id": item.predicate_id,
            "predicate_version": item.predicate_version,
            "replacement": item.replacement,
            "required_capabilities": tuple(
                requirement.metadata() for requirement in item.required_capabilities
            ),
            "system_scope": item.system_scope,
        }
    )


def predicate_registry_fingerprint_bytes(registry: PredicateRegistry | None = None) -> bytes:
    """Return stable registry evidence without callable repr or process identity."""

    current = get_production_registry() if registry is None else registry
    definitions = []
    for item in current.canonical_definitions():
        metadata = dict(_definition_metadata(item))
        metadata["handler_module"] = item.handler.__module__
        metadata["handler_qualified_name"] = item.handler.__qualname__
        definitions.append(metadata)
    return canonical_json_bytes(
        {
            "capability_catalog": get_production_capability_catalog().metadata_snapshot(),
            "capability_catalog_is_frozen": get_production_capability_catalog().is_frozen,
            "capability_catalog_is_ready": get_production_capability_catalog().is_ready,
            "canonical_ids": current.canonical_ids(),
            "definitions": definitions,
            "exposed_ids": current.exposed_ids(),
            "is_frozen": current.is_frozen,
            "is_ready": current.is_ready,
        }
    )


def predicate_registry_fingerprint_sha256(registry: PredicateRegistry | None = None) -> str:
    return hashlib.sha256(predicate_registry_fingerprint_bytes(registry)).hexdigest()


__all__ = (
    "CostClass",
    "PredicateDefinition",
    "PredicateDefinitionError",
    "PredicateRegistry",
    "PredicateRegistryError",
    "PredicateRegistryFrozenError",
    "bootstrap_production_registry",
    "get_production_registry",
    "predicate_registry_fingerprint_bytes",
    "predicate_registry_fingerprint_sha256",
)
