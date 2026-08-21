"""Immutable post-construction AstroState factual boundary.

The mutable Pydantic ``AstroState`` remains a construction compatibility model.
This module defensively copies already-produced facts, validates their ownership,
publishes a frozen snapshot, and exposes side-effect-free typed queries.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
import hashlib
import json
import math
import re
from types import MappingProxyType
from typing import Any, Generic, Iterator, TypeVar

from systems.Parasara.engine.capability import (
    CapabilityFactState,
    CapabilityInspection,
    CapabilityReadiness,
)
from systems.Parasara.engine.identities import CANONICAL_PLANETS, normalize_planet_id


SNAPSHOT_SCHEMA_VERSION = "1.0.0"
SNAPSHOT_PRODUCER_VERSION = "1.0.0"
NORMALIZATION_COMPATIBILITY_VERSION = "1.0.0"
SYSTEM_SCOPE = "parasara"

_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
_SAFE_CODE = re.compile(r"^[a-z][a-z0-9_]*$")
_VARGA_ID = re.compile(r"^D([1-9]|[1-9][0-9]|1[0-9][0-9])$")
_SIGNS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)
_MISSING = object()


class AstroCanonicalValueError(ValueError):
    """One source value cannot enter the bounded immutable snapshot."""


class FrozenMap(Mapping[str, Any]):
    """Small recursively immutable, deterministically ordered mapping."""

    __slots__ = ("_items", "_lookup", "_hash")

    def __init__(self, value: Mapping[str, Any] | None = None, *, path: str = "$") -> None:
        source = {} if value is None else value
        frozen = _freeze_value(source, path=path, active=set())
        if not isinstance(frozen, FrozenMap):
            raise AstroCanonicalValueError(f"{path}: expected mapping")
        object.__setattr__(self, "_items", frozen._items)
        object.__setattr__(self, "_lookup", frozen._lookup)
        object.__setattr__(self, "_hash", frozen._hash)

    @classmethod
    def _from_items(cls, items: Iterator[tuple[str, Any]]) -> "FrozenMap":
        instance = object.__new__(cls)
        ordered = tuple(items)
        object.__setattr__(instance, "_items", ordered)
        object.__setattr__(instance, "_lookup", MappingProxyType(dict(ordered)))
        object.__setattr__(instance, "_hash", hash(tuple((key, _frozen_hash(value)) for key, value in ordered)))
        return instance

    def __getitem__(self, key: str) -> Any:
        return self._lookup[key]

    def __iter__(self) -> Iterator[str]:
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __hash__(self) -> int:
        return self._hash

    def __setattr__(self, name: str, value: Any) -> None:
        raise TypeError("FrozenMap attributes cannot be reassigned")

    def __repr__(self) -> str:
        return f"FrozenMap(len={len(self)})"


def _frozen_hash(value: Any) -> int:
    if isinstance(value, FrozenMap):
        return hash(value)
    if isinstance(value, tuple):
        return hash(tuple(_frozen_hash(item) for item in value))
    return hash((type(value), value))


def _freeze_value(value: Any, *, path: str, active: set[int]) -> Any:
    if isinstance(value, Enum):
        return value.value
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise AstroCanonicalValueError(f"{path}: non-finite number")
        return 0.0 if value == 0.0 else value
    if isinstance(value, Mapping):
        identity = id(value)
        if identity in active:
            raise AstroCanonicalValueError(f"{path}: cyclic mapping")
        active.add(identity)
        try:
            if any(type(key) is not str for key in value):
                raise AstroCanonicalValueError(f"{path}: mapping keys must be strings")
            return FrozenMap._from_items(
                (key, _freeze_value(value[key], path=f"{path}.{key}", active=active))
                for key in sorted(value)
            )
        finally:
            active.remove(identity)
    if isinstance(value, (list, tuple)):
        identity = id(value)
        if identity in active:
            raise AstroCanonicalValueError(f"{path}: cyclic sequence")
        active.add(identity)
        try:
            return tuple(
                _freeze_value(item, path=f"{path}[{index}]", active=active)
                for index, item in enumerate(value)
            )
        finally:
            active.remove(identity)
    raise AstroCanonicalValueError(f"{path}: unsupported source value")


def freeze_value(value: Any, *, path: str = "$") -> Any:
    return _freeze_value(value, path=path, active=set())


def thaw_value(value: Any) -> Any:
    if isinstance(value, FrozenMap):
        return {key: thaw_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [thaw_value(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {item.name: thaw_value(getattr(value, item.name)) for item in fields(value)}
    return value


def _safe_issue_codes(value: Any, *, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{field_name} must be an immutable issue sequence")
    result = tuple(value)
    if any(type(item) is not str or not _SAFE_CODE.fullmatch(item) for item in result):
        raise TypeError(f"{field_name} must contain safe issue codes")
    if result != tuple(sorted(result)) or len(result) != len(set(result)):
        raise ValueError(f"{field_name} must be unique and deterministically ordered")
    return result


def _evaluation_context(value: Any) -> FrozenMap:
    """Freeze the one currently supported factual evaluation-context field."""

    if isinstance(value, FrozenMap):
        source = {key: value[key] for key in value}
    elif isinstance(value, Mapping):
        source = dict(value)
    else:
        raise ValueError("evaluation_context must be a mapping")
    if set(source) - {"instant"}:
        raise ValueError("evaluation_context contains an unsupported field")
    instant = source.get("instant")
    if instant is not None and (not isinstance(instant, str) or not instant.strip()):
        raise ValueError("evaluation_context.instant must be a non-empty string")
    return FrozenMap(source, path="$.evaluation_context")


@dataclass(frozen=True, slots=True, kw_only=True)
class PlanetFact:
    planet_id: str
    sign: str | None
    degree: float | None
    normalized_longitude: float | None

    def __post_init__(self) -> None:
        if normalize_planet_id(self.planet_id) != self.planet_id:
            raise ValueError("planet fact identity must be canonical")
        if self.sign is not None and self.sign not in _SIGNS:
            raise ValueError("planet fact sign is invalid")
        for name in ("degree", "normalized_longitude"):
            value = getattr(self, name)
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
            ):
                raise ValueError(f"planet fact {name} must be finite")
            if value is not None:
                object.__setattr__(self, name, 0.0 if float(value) == 0.0 else float(value))
        if self.normalized_longitude is not None and not 0.0 <= self.normalized_longitude < 360.0:
            raise ValueError("planet fact normalized longitude is out of range")


@dataclass(frozen=True, slots=True, kw_only=True)
class HouseFact:
    house_number: int
    sign: str | None

    def __post_init__(self) -> None:
        _house_number(self.house_number)
        if self.sign is not None and self.sign not in _SIGNS:
            raise ValueError("house fact sign is invalid")


@dataclass(frozen=True, slots=True, kw_only=True)
class AspectFact:
    representation: str
    source_kind: str
    source_id: str
    target_kind: str
    target_id: str | int | None
    target_sign: str | None
    aspect_kind: str
    configuration_version: str | None

    def __post_init__(self) -> None:
        if self.representation not in ("basic_conjunction_list", "whole_sign_graph"):
            raise ValueError("aspect representation is invalid")
        if self.source_kind != "planet" or normalize_planet_id(self.source_id) != self.source_id:
            raise ValueError("aspect source identity is invalid")
        if self.target_kind == "planet":
            if normalize_planet_id(self.target_id) != self.target_id:
                raise ValueError("aspect target planet is invalid")
        elif self.target_kind == "sign":
            if self.target_id not in _SIGNS:
                raise ValueError("aspect target sign is invalid")
        else:
            raise ValueError("aspect target kind is invalid")
        if self.target_sign is not None and self.target_sign not in _SIGNS:
            raise ValueError("aspect target_sign is invalid")
        if self.representation == "basic_conjunction_list":
            if (
                self.target_kind != "planet"
                or self.target_sign is not None
                or self.configuration_version is not None
            ):
                raise ValueError("basic aspect representation fields are contradictory")
        elif self.target_sign is None:
            raise ValueError("whole-sign aspect requires a target sign")
        elif self.target_kind == "sign" and self.target_id != self.target_sign:
            raise ValueError("whole-sign aspect target identity must match target_sign")
        if not isinstance(self.aspect_kind, str) or not self.aspect_kind:
            raise ValueError("aspect kind must be non-empty")
        if self.configuration_version is not None and not isinstance(self.configuration_version, str):
            raise ValueError("aspect configuration version must be a string")


@dataclass(frozen=True, slots=True, kw_only=True)
class VargaPositionFact:
    planet_id: str
    varga_id: str
    position: Any

    def __post_init__(self) -> None:
        if normalize_planet_id(self.planet_id) != self.planet_id:
            raise ValueError("varga planet identity must be canonical")
        if _varga_id(self.varga_id) != self.varga_id:
            raise ValueError("varga identity must be canonical")
        object.__setattr__(self, "position", freeze_value(self.position, path="$.position"))


@dataclass(frozen=True, slots=True, kw_only=True)
class VargaFact:
    varga_id: str
    positions: tuple[VargaPositionFact, ...]

    def __post_init__(self) -> None:
        if _varga_id(self.varga_id) != self.varga_id:
            raise ValueError("varga identity must be canonical")
        positions = tuple(self.positions)
        if any(not isinstance(item, VargaPositionFact) or item.varga_id != self.varga_id for item in positions):
            raise TypeError("varga positions must be canonical VargaPositionFact values")
        if len({item.planet_id for item in positions}) != len(positions):
            raise ValueError("varga positions must contain unique planets")
        order = {value: index for index, value in enumerate(CANONICAL_PLANETS)}
        if positions != tuple(sorted(positions, key=lambda item: order[item.planet_id])):
            raise ValueError("varga positions must use canonical planet order")
        object.__setattr__(self, "positions", positions)


@dataclass(frozen=True, slots=True, kw_only=True)
class FunctionalRoleFact:
    planet_id: str
    value: str
    source_kind: str
    factual_scope: str

    def __post_init__(self) -> None:
        if normalize_planet_id(self.planet_id) != self.planet_id:
            raise ValueError("functional-role identity must be canonical")
        if not isinstance(self.value, str):
            raise TypeError("functional-role value must be a string")
        for value in (self.source_kind, self.factual_scope):
            if not isinstance(value, str) or not _SAFE_CODE.fullmatch(value):
                raise ValueError("functional-role metadata must be safe")


@dataclass(frozen=True, slots=True, kw_only=True)
class DignityFact:
    planet_id: str
    value: str | None
    value_present: bool
    enriched_value: str | None
    enriched_value_present: bool
    source_kind: str

    def __post_init__(self) -> None:
        if normalize_planet_id(self.planet_id) != self.planet_id:
            raise ValueError("dignity identity must be canonical")
        if type(self.value_present) is not bool or type(self.enriched_value_present) is not bool:
            raise TypeError("dignity presence flags must be Booleans")
        if self.value is not None and not isinstance(self.value, str):
            raise TypeError("dignity value must be a string or None")
        if self.enriched_value is not None and not isinstance(self.enriched_value, str):
            raise TypeError("enriched dignity value must be a string or None")
        if self.value_present is not (self.value is not None):
            raise ValueError("dignity value presence flag is contradictory")
        if self.enriched_value_present is not (self.enriched_value is not None):
            raise ValueError("enriched dignity presence flag is contradictory")
        if not isinstance(self.source_kind, str) or not _SAFE_CODE.fullmatch(self.source_kind):
            raise ValueError("dignity source kind must be safe")


@dataclass(frozen=True, slots=True, kw_only=True)
class StrengthFact:
    planet_id: str
    value: Any
    source_kind: str
    factual_scope: str

    def __post_init__(self) -> None:
        if normalize_planet_id(self.planet_id) != self.planet_id:
            raise ValueError("strength identity must be canonical")
        for value in (self.source_kind, self.factual_scope):
            if not isinstance(value, str) or not _SAFE_CODE.fullmatch(value):
                raise ValueError("strength metadata must be safe")
        object.__setattr__(self, "value", freeze_value(self.value, path="$.value"))


@dataclass(frozen=True, slots=True, kw_only=True)
class GeneralCapabilityDefinition:
    capability_id: str
    capability_version: str
    description: str
    content_kind: str
    empty_policy: str
    system_scope: str
    source_kind: str
    recoverable_when_unavailable: bool
    factual_scope: str
    core_path: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not _CAPABILITY_ID.fullmatch(self.capability_id):
            raise ValueError("general capability ID must be canonical")
        if not isinstance(self.capability_version, str) or not _SEMVER.fullmatch(self.capability_version):
            raise ValueError("general capability version must use strict SemVer")
        if not isinstance(self.description, str) or not self.description:
            raise ValueError("general capability description must be non-empty")
        for name in ("content_kind", "empty_policy", "source_kind", "factual_scope"):
            value = getattr(self, name)
            if not isinstance(value, str) or not _SAFE_CODE.fullmatch(value):
                raise ValueError(f"general capability {name} must be safe")
        if self.system_scope != SYSTEM_SCOPE or type(self.recoverable_when_unavailable) is not bool:
            raise ValueError("general capability scope/recoverability is invalid")
        if self.core_path is not None and (
            not isinstance(self.core_path, str) or not self.core_path.startswith("core.")
        ):
            raise ValueError("general capability core_path is invalid")


def _definition(
    capability_id: str,
    description: str,
    content_kind: str,
    empty_policy: str,
    source_kind: str,
    *,
    factual_scope: str = "factual",
    core_path: str | None = None,
) -> GeneralCapabilityDefinition:
    return GeneralCapabilityDefinition(
        capability_id=capability_id,
        capability_version="1.0.0",
        description=description,
        content_kind=content_kind,
        empty_policy=empty_policy,
        system_scope=SYSTEM_SCOPE,
        source_kind=source_kind,
        recoverable_when_unavailable=True,
        factual_scope=factual_scope,
        core_path=core_path,
    )


_GENERAL_CAPABILITY_DEFINITIONS = tuple(sorted((
    _definition("chart.metadata", "Bounded normalized chart metadata.", "mapping", "ready_empty", "core_reference", core_path="core.metadata"),
    _definition("chart.location", "Bounded normalized chart location.", "mapping", "empty_not_ready", "core_reference", core_path="core.location"),
    _definition("chart.lagna", "Canonical chart Lagna sign.", "scalar", "empty_not_ready", "core_reference", core_path="core.lagna"),
    _definition("planets.normalized", "Canonical normalized planet facts.", "collection", "empty_not_ready", "core_reference", core_path="core.planets"),
    _definition("planets.house_placement", "Canonical planet house-placement fields.", "entity_fields", "empty_not_ready", "planet_house_fields"),
    _definition("houses.normalized", "Canonical normalized house facts.", "collection", "empty_not_ready", "core_reference", core_path="core.houses"),
    _definition("houses.lords", "Existing normalized house-lord facts.", "entity_fields", "ready_empty", "house_summaries"),
    _definition("houses.occupants", "Existing normalized house-occupant facts.", "entity_fields", "ready_empty", "house_summaries"),
    _definition("houses.summaries", "Existing bounded house summary rows.", "mapping", "ready_empty", "house_summaries", factual_scope="legacy_compatibility"),
    _definition("chart.lagna_summary", "Existing bounded Lagna diagnostic facts.", "mapping", "ready_empty", "lagna_summary", factual_scope="legacy_compatibility"),
    _definition("aspects.basic_conjunction_list", "Legacy normalized basic conjunction list.", "collection", "ready_empty", "legacy_basic_conjunction_list"),
    _definition("aspects.whole_sign_graph", "Legacy whole-sign aspect graph envelope.", "graph", "ready_empty", "legacy_whole_sign_graph"),
    _definition("dignity.exaltation_facts", "Legacy explicit exaltation facts.", "mapping", "ready_empty", "legacy_exaltation_sources"),
    _definition("dignity.planet", "Existing planet dignity compatibility facets.", "entity_fields", "ready_empty", "planet_and_strength_rows", factual_scope="legacy_compatibility"),
    _definition("vargas.positions", "Existing normalized per-planet varga positions.", "mapping", "ready_empty", "planet_varga_fields"),
    _definition("roles.functional", "Explicit prepared functional-role facts.", "mapping", "ready_empty", "derived_functional_roles"),
    _definition("strengths.planet", "Existing bounded planet strength facts.", "entity_fields", "ready_empty", "planet_and_strength_rows", factual_scope="legacy_composite"),
    _definition("strengths.shadbala", "Existing partial Shadbala component payloads.", "entity_fields", "ready_empty", "legacy_strength_rows", factual_scope="legacy_partial_proxy"),
    _definition("dasha.current", "Integrated current Dasha fact.", "mapping", "empty_not_ready", "integrated_dasha", factual_scope="unavailable_without_supply"),
    _definition("transits.current", "Integrated current transit facts.", "collection", "ready_empty", "integrated_transits", factual_scope="unavailable_without_supply"),
), key=lambda item: item.capability_id))
_GENERAL_DEFINITION_BY_ID = {item.capability_id: item for item in _GENERAL_CAPABILITY_DEFINITIONS}


def get_general_capability_catalog() -> tuple[GeneralCapabilityDefinition, ...]:
    return _GENERAL_CAPABILITY_DEFINITIONS


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilitySnapshot:
    capability_id: str
    capability_version: str
    readiness: CapabilityReadiness
    source_kind: str | None
    content: Any
    content_empty: bool
    issues: tuple[str, ...]
    factual_scope: str
    core_path: str | None = None

    def __post_init__(self) -> None:
        definition = _GENERAL_DEFINITION_BY_ID.get(self.capability_id)
        if definition is None:
            raise ValueError("capability snapshot ID must be in the general catalog")
        if self.capability_version != definition.capability_version:
            raise ValueError("capability snapshot version must match the general catalog")
        if not isinstance(self.readiness, CapabilityReadiness):
            raise TypeError("capability snapshot readiness is invalid")
        if self.core_path != definition.core_path:
            raise ValueError("capability snapshot core reference must match its definition")
        if self.core_path is not None and self.content is not None:
            raise ValueError("core-backed capability cannot store independent content")
        issues = _safe_issue_codes(self.issues, field_name="capability issues")
        object.__setattr__(self, "issues", issues)
        if self.content is not None:
            object.__setattr__(
                self, "content",
                freeze_value(self.content, path=f"$.capabilities.{self.capability_id}.content"),
            )
        if not isinstance(self.factual_scope, str) or not _SAFE_CODE.fullmatch(self.factual_scope):
            raise ValueError("capability factual scope must be safe")
        if self.source_kind is not None and (
            not isinstance(self.source_kind, str) or not _SAFE_CODE.fullmatch(self.source_kind)
        ):
            raise ValueError("capability source kind must be safe")
        if type(self.content_empty) is not bool:
            raise TypeError("capability content_empty must be a Boolean")
        content = self.content
        content_is_empty = isinstance(content, (tuple, FrozenMap)) and len(content) == 0
        if self.core_path is not None and self.source_kind not in (None, definition.source_kind):
            raise ValueError("core-backed capability source must match its definition")
        if self.readiness in (CapabilityReadiness.MISSING, CapabilityReadiness.UNSUPPORTED):
            if self.source_kind is not None or self.content is not None or self.content_empty:
                raise ValueError("missing capability cannot contain source content")
        elif self.source_kind is None:
            raise ValueError("observed capability requires a source kind")
        if self.readiness is CapabilityReadiness.READY:
            if self.content_empty:
                raise ValueError("ready capability cannot be empty")
            if self.core_path is None and (content is None or content_is_empty):
                raise ValueError("non-core ready capability requires nonempty content")
        elif self.readiness is CapabilityReadiness.READY_EMPTY:
            if definition.empty_policy != "ready_empty":
                raise ValueError("capability catalog does not permit ready-empty content")
            if not self.content_empty:
                raise ValueError("ready_empty capability must be empty")
            if self.core_path is None and not content_is_empty:
                raise ValueError("non-core ready_empty capability requires empty content")
        elif content is not None:
            raise ValueError("unready capability cannot carry factual content")
        if self.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
            if self.issues:
                raise ValueError("ready capability cannot carry issues")
        elif not self.issues:
            raise ValueError("unready capability requires a safe issue")


@dataclass(frozen=True, slots=True, kw_only=True)
class AstroCore:
    metadata: FrozenMap
    location: FrozenMap | None
    lagna_sign: str | None
    lagna_degree: float | None
    planets: tuple[PlanetFact, ...]
    houses: tuple[HouseFact, ...]

    def __post_init__(self) -> None:
        metadata = FrozenMap(self.metadata, path="$.core.metadata")
        location = None if self.location is None else FrozenMap(self.location, path="$.core.location")
        if self.lagna_sign is not None and self.lagna_sign not in _SIGNS:
            raise ValueError("core Lagna sign is invalid")
        lagna_degree = self.lagna_degree
        if lagna_degree is not None and (
            isinstance(lagna_degree, bool) or not isinstance(lagna_degree, (int, float))
            or not math.isfinite(float(lagna_degree))
        ):
            raise ValueError("core Lagna degree must be finite")
        if self.lagna_sign is None and lagna_degree is not None:
            raise ValueError("core Lagna degree requires a Lagna sign")
        planets = tuple(self.planets)
        houses = tuple(self.houses)
        if any(not isinstance(item, PlanetFact) for item in planets):
            raise TypeError("core planets must be PlanetFact values")
        if any(not isinstance(item, HouseFact) for item in houses):
            raise TypeError("core houses must be HouseFact values")
        if len({item.planet_id for item in planets}) != len(planets):
            raise ValueError("core planets must be unique")
        if len({item.house_number for item in houses}) != len(houses):
            raise ValueError("core houses must be unique")
        planet_order = {value: index for index, value in enumerate(CANONICAL_PLANETS)}
        if planets != tuple(sorted(planets, key=lambda item: planet_order[item.planet_id])):
            raise ValueError("core planets must use canonical order")
        if houses != tuple(sorted(houses, key=lambda item: item.house_number)):
            raise ValueError("core houses must use numeric order")
        object.__setattr__(self, "metadata", metadata)
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "lagna_degree", None if lagna_degree is None else float(lagna_degree))
        object.__setattr__(self, "planets", planets)
        object.__setattr__(self, "houses", houses)


@dataclass(frozen=True, slots=True, kw_only=True)
class AstroStateVersions:
    schema_version: str = SNAPSHOT_SCHEMA_VERSION
    producer_version: str = SNAPSHOT_PRODUCER_VERSION
    normalization_version: str = NORMALIZATION_COMPATIBILITY_VERSION

    def __post_init__(self) -> None:
        for value in (self.schema_version, self.producer_version, self.normalization_version):
            if not isinstance(value, str) or not _SEMVER.fullmatch(value):
                raise ValueError("AstroState versions must use strict SemVer")


@dataclass(frozen=True, slots=True, kw_only=True)
class ConstructionIssue:
    code: str
    path: str
    capability_id: str | None = None
    entity_kind: str | None = None
    entity_id: str | None = None
    recoverable: bool = True
    fatal: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not _SAFE_CODE.fullmatch(self.code):
            raise ValueError("construction issue code must be safe")
        if not isinstance(self.path, str) or not self.path.startswith("$"):
            raise ValueError("construction issue path must be rooted")
        if self.capability_id is not None and not _CAPABILITY_ID.fullmatch(self.capability_id):
            raise ValueError("construction issue capability ID must be canonical")
        if (self.entity_kind is None) is not (self.entity_id is None):
            raise ValueError("construction issue entity identity must be complete")
        if type(self.recoverable) is not bool or type(self.fatal) is not bool:
            raise TypeError("construction issue flags must be Booleans")
        if self.fatal and self.recoverable:
            raise ValueError("fatal construction issues cannot be recoverable")


@dataclass(frozen=True, slots=True, kw_only=True)
class AstroCapabilitySupply:
    capability_id: str
    capability_version: str
    source_kind: str
    content: Any
    factual_scope: str = "factual"

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not _CAPABILITY_ID.fullmatch(self.capability_id):
            raise ValueError("supply capability_id must be canonical")
        if not isinstance(self.capability_version, str) or not _SEMVER.fullmatch(self.capability_version):
            raise ValueError("supply capability_version must be strict SemVer")
        if not isinstance(self.source_kind, str) or not _SAFE_CODE.fullmatch(self.source_kind):
            raise ValueError("supply source_kind must be safe")
        if not isinstance(self.factual_scope, str) or not _SAFE_CODE.fullmatch(self.factual_scope):
            raise ValueError("supply factual_scope must be safe")
        object.__setattr__(
            self, "content",
            freeze_value(self.content, path=f"$.capability_supplies.{self.capability_id}.content"),
        )


def _freeze_query_value(value: Any, *, path: str) -> Any:
    immutable_fact_types = (
        PlanetFact, HouseFact, AspectFact, VargaPositionFact, VargaFact,
        FunctionalRoleFact, DignityFact, StrengthFact, GeneralCapabilityDefinition,
    )
    if isinstance(value, immutable_fact_types):
        return value
    if isinstance(value, tuple):
        return tuple(
            _freeze_query_value(item, path=f"{path}[{index}]")
            for index, item in enumerate(value)
        )
    return freeze_value(value, path=path)


T = TypeVar("T")


@dataclass(frozen=True, slots=True, kw_only=True)
class AstroQueryResult(Generic[T]):
    capability_id: str
    capability_version: str
    state: CapabilityFactState
    entity_kind: str | None
    entity_id: str | None
    value_present: bool
    value: T | None
    issues: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not _CAPABILITY_ID.fullmatch(self.capability_id):
            raise ValueError("query capability_id must be canonical")
        if not isinstance(self.capability_version, str) or not _SEMVER.fullmatch(self.capability_version):
            raise ValueError("query capability_version must be strict SemVer")
        if not isinstance(self.state, CapabilityFactState):
            raise TypeError("query state must be CapabilityFactState")
        if (self.entity_kind is None) is not (self.entity_id is None):
            raise ValueError("query entity identity must be complete")
        if type(self.value_present) is not bool:
            raise TypeError("query value_present/issues have invalid types")
        issues = _safe_issue_codes(self.issues, field_name="query issues")
        object.__setattr__(self, "issues", issues)
        if self.state is CapabilityFactState.PRESENT:
            if not self.value_present or self.value is None or self.issues:
                raise ValueError("present query result requires one issue-free value")
            object.__setattr__(self, "value", _freeze_query_value(self.value, path="$.value"))
        elif self.value_present or self.value is not None:
            raise ValueError("non-present query result cannot carry a value")


@dataclass(frozen=True, slots=True, kw_only=True)
class AstroStateSnapshot:
    schema_version: str
    producer_version: str
    normalization_version: str
    system_scope: str
    evaluation_context: FrozenMap
    core: AstroCore
    capabilities: tuple[CapabilitySnapshot, ...]
    construction_issues: tuple[ConstructionIssue, ...]

    def __post_init__(self) -> None:
        if self.system_scope != SYSTEM_SCOPE:
            raise ValueError("system_scope must be parasara")
        for version in (self.schema_version, self.producer_version, self.normalization_version):
            if not _SEMVER.fullmatch(version):
                raise ValueError("snapshot versions must use strict SemVer")
        context = _evaluation_context(self.evaluation_context)
        if not isinstance(self.core, AstroCore):
            raise TypeError("snapshot core must be AstroCore")
        capabilities = tuple(self.capabilities)
        if any(not isinstance(item, CapabilitySnapshot) for item in capabilities):
            raise TypeError("snapshot capabilities must be CapabilitySnapshot values")
        issues = tuple(self.construction_issues)
        if any(not isinstance(item, ConstructionIssue) for item in issues):
            raise TypeError("snapshot construction issues must be typed")
        identities = tuple(item.capability_id for item in capabilities)
        if identities != tuple(sorted(identities)) or len(set(identities)) != len(identities):
            raise ValueError("snapshot capabilities must be unique and sorted")
        if identities != tuple(item.capability_id for item in _GENERAL_CAPABILITY_DEFINITIONS):
            raise ValueError("snapshot must contain the complete general capability catalog")
        for capability in capabilities:
            definition = _GENERAL_DEFINITION_BY_ID[capability.capability_id]
            if capability.capability_version != definition.capability_version:
                raise ValueError("snapshot capability version must match the composed catalog")
            if definition.core_path is not None:
                expected_readiness, expected_empty = _core_capability_state(
                    definition.core_path, self.core,
                )
                if (
                    capability.readiness is not expected_readiness
                    or capability.content_empty is not expected_empty
                    or capability.content is not None
                ):
                    raise ValueError(
                        f"core-backed capability {capability.capability_id} contradicts AstroCore"
                    )
            _validate_snapshot_aspect_capability(capability, self.core)
        if tuple(sorted(issues, key=_issue_key)) != issues or len(set(issues)) != len(issues):
            raise ValueError("construction issues must be deterministically ordered")
        object.__setattr__(self, "evaluation_context", context)
        object.__setattr__(self, "capabilities", capabilities)
        object.__setattr__(self, "construction_issues", issues)

    @property
    def logical_digest(self) -> str:
        return hashlib.sha256(snapshot_logical_bytes(self)).hexdigest()

    def _capability(self, capability_id: str) -> CapabilitySnapshot:
        return next(item for item in self.capabilities if item.capability_id == capability_id)

    def inspect_capability(self, capability_id: str, expected_version: str | None = None) -> CapabilityInspection:
        normalized = _normalize_capability_id(capability_id)
        if expected_version is not None and not _SEMVER.fullmatch(expected_version):
            raise ValueError("expected_version must use strict SemVer")
        definition = _GENERAL_DEFINITION_BY_ID.get(normalized)
        expected = expected_version or (definition.capability_version if definition else "1.0.0")
        if definition is None:
            return CapabilityInspection(
                capability_id=normalized, expected_version=expected, observed_version=None,
                readiness=CapabilityReadiness.UNSUPPORTED, source_kind=None,
                content_empty=False, issues=("catalog_miss",),
            )
        capability = self._capability(normalized)
        if expected != capability.capability_version:
            return CapabilityInspection(
                capability_id=normalized, expected_version=expected,
                observed_version=capability.capability_version,
                readiness=CapabilityReadiness.VERSION_MISMATCH,
                source_kind=capability.source_kind or definition.source_kind,
                content_empty=capability.content_empty,
                issues=("contract_version_mismatch",),
            )
        return CapabilityInspection(
            capability_id=normalized, expected_version=expected,
            observed_version=(None if capability.readiness in (CapabilityReadiness.MISSING, CapabilityReadiness.UNSUPPORTED) else capability.capability_version),
            readiness=capability.readiness, source_kind=capability.source_kind,
            content_empty=capability.content_empty, issues=capability.issues,
        )

    def inspect_capabilities(self, required_capability_ids: Any) -> tuple[CapabilityInspection, ...]:
        if not isinstance(required_capability_ids, (list, tuple)):
            raise ValueError("required_capability_ids must be a list or tuple")
        requests: list[tuple[str, str | None]] = []
        for item in required_capability_ids:
            if isinstance(item, str):
                requests.append((_normalize_capability_id(item), None))
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                requests.append((_normalize_capability_id(item[0]), item[1]))
            else:
                raise ValueError("capability request must be an ID or ID/version pair")
        if len({item[0] for item in requests}) != len(requests):
            raise ValueError("capability requests must be unique")
        return tuple(self.inspect_capability(item, version) for item, version in sorted(requests))

    def list_capabilities(self) -> tuple[GeneralCapabilityDefinition, ...]:
        return _GENERAL_CAPABILITY_DEFINITIONS

    def get_planet(self, planet_id: Any) -> AstroQueryResult[PlanetFact]:
        canonical = normalize_planet_id(planet_id)
        found = next((item for item in self.core.planets if item.planet_id == canonical), None)
        return self._entity_result("planets.normalized", "planet", canonical, found)

    def get_planets(self) -> AstroQueryResult[tuple[PlanetFact, ...]]:
        order = {value: index for index, value in enumerate(CANONICAL_PLANETS)}
        value = tuple(sorted(self.core.planets, key=lambda item: order[item.planet_id]))
        return self._collection_result("planets.normalized", value)

    def get_house(self, house_number: Any) -> AstroQueryResult[HouseFact]:
        number = _house_number(house_number)
        found = next((item for item in self.core.houses if item.house_number == number), None)
        return self._entity_result("houses.normalized", "house", str(number), found)

    def get_houses(self) -> AstroQueryResult[tuple[HouseFact, ...]]:
        return self._collection_result("houses.normalized", tuple(sorted(self.core.houses, key=lambda item: item.house_number)))

    def get_lagna(self) -> AstroQueryResult[str]:
        return self._entity_result("chart.lagna", "chart", "lagna", self.core.lagna_sign)

    def get_chart_metadata(self) -> AstroQueryResult[FrozenMap]:
        """Return bounded chart metadata without exposing a mutable source map."""

        return self._entity_result("chart.metadata", "chart", "metadata", self.core.metadata)

    def get_location(self) -> AstroQueryResult[FrozenMap]:
        return self._entity_result("chart.location", "chart", "location", self.core.location)

    def get_lagna_summary(self) -> AstroQueryResult[FrozenMap]:
        return self._entity_result(
            "chart.lagna_summary", "chart", "lagna_summary",
            self._capability("chart.lagna_summary").content,
        )

    def get_planet_house(self, planet_id: Any) -> AstroQueryResult[int]:
        canonical = normalize_planet_id(planet_id)
        content = self._content_mapping("planets.house_placement")
        value = None if content is None else content.get(canonical)
        return self._entity_result("planets.house_placement", "planet", canonical, value)

    def get_planet_dignity(self, planet_id: Any) -> AstroQueryResult[DignityFact]:
        canonical = normalize_planet_id(planet_id)
        content = self._content_mapping("dignity.planet")
        row = None if content is None else content.get(canonical)
        value = None if row is None else DignityFact(
            planet_id=canonical,
            value=row["value"], value_present=row["value_present"],
            enriched_value=row["enriched_value"],
            enriched_value_present=row["enriched_value_present"],
            source_kind=self._capability("dignity.planet").source_kind or "planet_and_strength_rows",
        )
        return self._entity_result("dignity.planet", "planet", canonical, value)

    def get_house_lord(self, house_number: Any) -> AstroQueryResult[str]:
        number = _house_number(house_number)
        content = self._content_mapping("houses.lords")
        value = None if content is None else content.get(str(number))
        return self._entity_result("houses.lords", "house", str(number), value)

    def get_occupants(self, house_number: Any) -> AstroQueryResult[tuple[str, ...]]:
        number = _house_number(house_number)
        content = self._content_mapping("houses.occupants")
        raw = None if content is None else content.get(str(number))
        if raw is not None:
            order = {value: index for index, value in enumerate(CANONICAL_PLANETS)}
            raw = tuple(sorted(raw, key=lambda item: order[item]))
        return self._entity_result("houses.occupants", "house", str(number), raw)

    def get_house_summary(self, house_number: Any) -> AstroQueryResult[FrozenMap]:
        number = _house_number(house_number)
        content = self._content_mapping("houses.summaries")
        value = None if content is None else content.get(str(number))
        return self._entity_result("houses.summaries", "house", str(number), value)

    def get_house_summaries(self) -> AstroQueryResult[tuple[FrozenMap, ...]]:
        content = self._content_mapping("houses.summaries")
        values = () if content is None else tuple(
            content[str(number)] for number in range(1, 13) if str(number) in content
        )
        return self._entity_result("houses.summaries", "collection", "houses.summaries", values)

    def get_aspects_from(self, planet_id: Any, representation: Any) -> AstroQueryResult[tuple[AspectFact, ...]]:
        canonical = normalize_planet_id(planet_id)
        capability_id = _aspect_capability_id(representation)
        if not any(item.planet_id == canonical for item in self.core.planets):
            return self._entity_result(capability_id, "planet", canonical, None)
        return self._aspect_result(capability_id, "planet", canonical, lambda item: item.source_id == canonical)

    def get_aspects_to_planet(self, planet_id: Any, representation: Any) -> AstroQueryResult[tuple[AspectFact, ...]]:
        canonical = normalize_planet_id(planet_id)
        capability_id = _aspect_capability_id(representation)
        if not any(item.planet_id == canonical for item in self.core.planets):
            return self._entity_result(capability_id, "planet", canonical, None)
        return self._aspect_result(capability_id, "planet", canonical, lambda item: item.target_kind == "planet" and item.target_id == canonical)

    def get_aspects_to_house(self, house_number: Any, representation: Any) -> AstroQueryResult[tuple[AspectFact, ...]]:
        number = _house_number(house_number)
        capability_id = _aspect_capability_id(representation)
        house = next((item for item in self.core.houses if item.house_number == number), None)
        if house is None:
            return self._entity_result(capability_id, "house", str(number), None)
        return self._aspect_result(
            capability_id, "house", str(number),
            lambda item: (
                item.representation == "whole_sign_graph"
                and house.sign is not None
                and item.target_sign == house.sign
            ),
        )

    def get_aspect_representation(self, representation: Any) -> AstroQueryResult[Any]:
        """Explicit immutable compatibility view of one aspect representation."""

        capability_id = _aspect_capability_id(representation)
        capability = self._capability(capability_id)
        return self._entity_result(
            capability_id, "representation", capability_id, capability.content,
        )

    def get_varga(self, varga_id: Any) -> AstroQueryResult[VargaFact]:
        canonical = _varga_id(varga_id)
        content = self._content_mapping("vargas.positions")
        raw = None if content is None else content.get(canonical)
        value = None
        if raw is not None:
            value = VargaFact(
                varga_id=canonical,
                positions=tuple(
                    VargaPositionFact(planet_id=planet, varga_id=canonical, position=raw[planet])
                    for planet in CANONICAL_PLANETS if planet in raw
                ),
            )
        return self._entity_result("vargas.positions", "varga", canonical, value)

    def get_vargas(self) -> AstroQueryResult[tuple[VargaFact, ...]]:
        content = self._content_mapping("vargas.positions")
        values = () if content is None else tuple(
            VargaFact(
                varga_id=varga_id,
                positions=tuple(
                    VargaPositionFact(
                        planet_id=planet, varga_id=varga_id,
                        position=content[varga_id][planet],
                    )
                    for planet in CANONICAL_PLANETS if planet in content[varga_id]
                ),
            )
            for varga_id in sorted(content)
        )
        return self._entity_result("vargas.positions", "collection", "vargas.positions", values)

    def get_planet_in_varga(self, planet_id: Any, varga_id: Any) -> AstroQueryResult[VargaPositionFact]:
        planet = normalize_planet_id(planet_id)
        varga = _varga_id(varga_id)
        content = self._content_mapping("vargas.positions")
        positions = None if content is None else content.get(varga)
        raw = None if positions is None else positions.get(planet)
        value = None if raw is None else VargaPositionFact(planet_id=planet, varga_id=varga, position=raw)
        return self._entity_result("vargas.positions", "planet_varga", f"{planet}:{varga}", value)

    def get_functional_role(self, planet_id: Any) -> AstroQueryResult[FunctionalRoleFact]:
        canonical = normalize_planet_id(planet_id)
        content = self._content_mapping("roles.functional")
        raw = None if content is None else content.get(canonical)
        value = None if raw is None else FunctionalRoleFact(
            planet_id=canonical, value=raw,
            source_kind=self._capability("roles.functional").source_kind or "derived_functional_roles",
            factual_scope=self._capability("roles.functional").factual_scope,
        )
        return self._entity_result("roles.functional", "planet", canonical, value)

    def get_functional_roles(self) -> AstroQueryResult[tuple[FunctionalRoleFact, ...]]:
        content = self._content_mapping("roles.functional")
        values = () if content is None else tuple(
            FunctionalRoleFact(
                planet_id=planet, value=content[planet],
                source_kind=self._capability("roles.functional").source_kind or "derived_functional_roles",
                factual_scope=self._capability("roles.functional").factual_scope,
            )
            for planet in CANONICAL_PLANETS if planet in content
        )
        return self._entity_result("roles.functional", "collection", "roles.functional", values)

    def get_exaltation_facts(self, planet_id: Any) -> AstroQueryResult[tuple[Any, ...]]:
        canonical = normalize_planet_id(planet_id)
        content = self._capability("dignity.exaltation_facts").content
        rows = () if content is None else tuple(item for item in content if item["planet_id"] == canonical)
        if not rows and self._capability("dignity.exaltation_facts").readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
            return self._entity_result("dignity.exaltation_facts", "planet", canonical, None)
        return self._entity_result("dignity.exaltation_facts", "planet", canonical, rows)

    def get_planet_strength(self, planet_id: Any) -> AstroQueryResult[StrengthFact]:
        canonical = normalize_planet_id(planet_id)
        content = self._content_mapping("strengths.planet")
        raw = None if content is None else content.get(canonical)
        value = None if raw is None else StrengthFact(
            planet_id=canonical, value=raw,
            source_kind=self._capability("strengths.planet").source_kind or "planet_and_strength_rows",
            factual_scope=self._capability("strengths.planet").factual_scope,
        )
        return self._entity_result("strengths.planet", "planet", canonical, value)

    def get_shadbala(self, planet_id: Any) -> AstroQueryResult[StrengthFact]:
        canonical = normalize_planet_id(planet_id)
        content = self._content_mapping("strengths.shadbala")
        raw = None if content is None else content.get(canonical)
        value = None if raw is None else StrengthFact(
            planet_id=canonical, value=raw,
            source_kind=self._capability("strengths.shadbala").source_kind or "legacy_strength_rows",
            factual_scope=self._capability("strengths.shadbala").factual_scope,
        )
        return self._entity_result("strengths.shadbala", "planet", canonical, value)

    def get_current_dasha(self) -> AstroQueryResult[Any]:
        return self._entity_result("dasha.current", "evaluation", "current", self._capability("dasha.current").content)

    def get_current_transits(self) -> AstroQueryResult[Any]:
        return self._entity_result("transits.current", "evaluation", "current", self._capability("transits.current").content)

    def _content_mapping(self, capability_id: str) -> FrozenMap | None:
        content = self._capability(capability_id).content
        return content if isinstance(content, FrozenMap) else None

    def _collection_result(self, capability_id: str, value: Any) -> AstroQueryResult[Any]:
        return self._entity_result(capability_id, "collection", capability_id, value)

    def _entity_result(self, capability_id: str, entity_kind: str, entity_id: str, value: Any) -> AstroQueryResult[Any]:
        capability = self._capability(capability_id)
        unavailable = {
            CapabilityReadiness.MISSING: CapabilityFactState.CAPABILITY_UNAVAILABLE,
            CapabilityReadiness.MALFORMED: CapabilityFactState.MALFORMED_CAPABILITY,
            CapabilityReadiness.VERSION_MISMATCH: CapabilityFactState.VERSION_MISMATCH,
            CapabilityReadiness.UNSUPPORTED: CapabilityFactState.UNSUPPORTED_CAPABILITY,
        }
        if capability.readiness in unavailable:
            return AstroQueryResult(
                capability_id=capability_id, capability_version=capability.capability_version,
                state=unavailable[capability.readiness], entity_kind=entity_kind,
                entity_id=entity_id, value_present=False, value=None, issues=capability.issues,
            )
        if value is None:
            return AstroQueryResult(
                capability_id=capability_id, capability_version=capability.capability_version,
                state=CapabilityFactState.ABSENT_ENTITY, entity_kind=entity_kind,
                entity_id=entity_id, value_present=False, value=None, issues=("entity_absent",),
            )
        return AstroQueryResult(
            capability_id=capability_id, capability_version=capability.capability_version,
            state=CapabilityFactState.PRESENT, entity_kind=entity_kind,
            entity_id=entity_id, value_present=True, value=value, issues=(),
        )

    def _aspect_result(self, capability_id: str, entity_kind: str, entity_id: str, predicate: Any) -> AstroQueryResult[tuple[AspectFact, ...]]:
        capability = self._capability(capability_id)
        if capability.readiness not in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
            return self._entity_result(capability_id, entity_kind, entity_id, None)
        values = tuple(item for item in _aspect_facts(capability) if predicate(item))
        return self._entity_result(capability_id, entity_kind, entity_id, values)


@dataclass(frozen=True, slots=True, kw_only=True)
class AstroStateBuildSuccess:
    snapshot: AstroStateSnapshot
    issues: tuple[ConstructionIssue, ...] = ()

    def __post_init__(self) -> None:
        issues = tuple(self.issues)
        if any(not isinstance(item, ConstructionIssue) for item in issues):
            raise TypeError("successful build issues must be typed")
        if not isinstance(self.snapshot, AstroStateSnapshot) or any(item.fatal for item in issues):
            raise ValueError("successful build requires one snapshot and no fatal issue")
        if tuple(sorted(issues, key=_issue_key)) != issues or len(set(issues)) != len(issues):
            raise ValueError("successful build issues must be unique and deterministically ordered")
        object.__setattr__(self, "issues", issues)


@dataclass(frozen=True, slots=True, kw_only=True)
class AstroStateBuildFailure:
    issues: tuple[ConstructionIssue, ...]

    def __post_init__(self) -> None:
        issues = tuple(self.issues)
        if any(not isinstance(item, ConstructionIssue) for item in issues):
            raise TypeError("failed build issues must be typed")
        if not issues or not any(item.fatal for item in issues):
            raise ValueError("failed build requires at least one fatal issue")
        if tuple(sorted(issues, key=_issue_key)) != issues or len(set(issues)) != len(issues):
            raise ValueError("failed build issues must be deterministically ordered")
        object.__setattr__(self, "issues", issues)


AstroStateBuildOutcome = AstroStateBuildSuccess | AstroStateBuildFailure


class _BuildFailure(Exception):
    def __init__(self, issue: ConstructionIssue):
        self.issue = issue


def _fatal(code: str, path: str, capability_id: str | None = None, entity_kind: str | None = None, entity_id: str | None = None) -> _BuildFailure:
    return _BuildFailure(ConstructionIssue(
        code=code, path=path, capability_id=capability_id,
        entity_kind=entity_kind, entity_id=entity_id,
        recoverable=False, fatal=True,
    ))


def _attribute(value: Any, name: str, default: Any = _MISSING) -> Any:
    try:
        return getattr(value, name)
    except AttributeError:
        if isinstance(value, Mapping):
            return value.get(name, default)
        return default


def _mapping(value: Any, *, path: str) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="python")
    elif hasattr(value, "dict"):
        value = value.dict()
    if not isinstance(value, Mapping):
        raise _fatal("invalid_mapping", path)
    return dict(value)


def _finite_optional(value: Any, *, path: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise _fatal("invalid_number", path)
    return 0.0 if float(value) == 0.0 else float(value)


def _house_number(value: Any) -> int:
    if type(value) is not int or not 1 <= value <= 12:
        raise ValueError("house_number must be an integer from 1 through 12")
    return value


def _varga_id(value: Any) -> str:
    if not isinstance(value, str) or not _VARGA_ID.fullmatch(value.strip().upper()):
        raise ValueError("varga_id must use canonical D-number notation")
    return value.strip().upper()


def _normalize_capability_id(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("capability_id must be a string")
    normalized = value.strip().lower()
    if not _CAPABILITY_ID.fullmatch(normalized):
        raise ValueError("capability_id must be canonical")
    return normalized


def _aspect_capability_id(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("aspect representation must be explicit")
    normalized = value.strip().lower()
    aliases = {
        "basic_conjunction_list": "aspects.basic_conjunction_list",
        "aspects.basic_conjunction_list": "aspects.basic_conjunction_list",
        "whole_sign_graph": "aspects.whole_sign_graph",
        "aspects.whole_sign_graph": "aspects.whole_sign_graph",
    }
    if normalized not in aliases:
        raise ValueError("aspect representation must select basic_conjunction_list or whole_sign_graph")
    return aliases[normalized]


def _is_canonical_planet(value: Any) -> bool:
    try:
        return isinstance(value, str) and normalize_planet_id(value) == value
    except ValueError:
        return False


def _valid_basic_aspect_row(
    value: Any,
    planet_ids: frozenset[str] | set[str] | None = None,
) -> bool:
    valid = bool(
        isinstance(value, Mapping)
        and _is_canonical_planet(value.get("from"))
        and _is_canonical_planet(value.get("to"))
        and isinstance(value.get("type"), str)
        and value.get("type")
    )
    if not valid or planet_ids is None:
        return valid
    return value["from"] in planet_ids and value["to"] in planet_ids


def _valid_whole_sign_aspect_row(
    value: Any,
    planet_signs: Mapping[str, str | None] | None = None,
) -> bool:
    if not isinstance(value, Mapping) or not _is_canonical_planet(value.get("source")):
        return False
    target = value.get("target")
    if target is not None and not _is_canonical_planet(target):
        return False
    trace = value.get("trace")
    target_sign = trace.get("target_sign") if isinstance(trace, Mapping) else None
    kind = value.get("aspect", value.get("kind"))
    if not bool(target_sign in _SIGNS and isinstance(kind, str) and kind):
        return False
    if planet_signs is None:
        return True
    if value["source"] not in planet_signs:
        return False
    if target is not None and (
        target not in planet_signs or planet_signs[target] != target_sign
    ):
        return False
    return True


def _core_capability_state(
    core_path: str,
    core: AstroCore,
) -> tuple[CapabilityReadiness, bool]:
    if core_path == "core.metadata":
        empty = len(core.metadata) == 0
        return (
            CapabilityReadiness.READY_EMPTY if empty else CapabilityReadiness.READY,
            empty,
        )
    if core_path == "core.location":
        return (
            (CapabilityReadiness.MISSING, False)
            if core.location is None
            else (CapabilityReadiness.READY, False)
        )
    if core_path == "core.lagna":
        return (
            (CapabilityReadiness.MISSING, False)
            if core.lagna_sign is None
            else (CapabilityReadiness.READY, False)
        )
    if core_path == "core.planets":
        return (
            (CapabilityReadiness.READY, False)
            if core.planets
            else (CapabilityReadiness.MISSING, False)
        )
    if core_path == "core.houses":
        return (
            (CapabilityReadiness.READY, False)
            if core.houses
            else (CapabilityReadiness.MISSING, False)
        )
    raise ValueError("capability definition contains an unknown core reference")


def _validate_snapshot_aspect_capability(
    capability: CapabilitySnapshot,
    core: AstroCore,
) -> None:
    if capability.readiness not in (
        CapabilityReadiness.READY,
        CapabilityReadiness.READY_EMPTY,
    ):
        return
    planet_signs = {item.planet_id: item.sign for item in core.planets}
    if capability.capability_id == "aspects.basic_conjunction_list":
        if not isinstance(capability.content, tuple) or not all(
            _valid_basic_aspect_row(row, set(planet_signs))
            for row in capability.content
        ):
            raise ValueError("published basic aspects must reference snapshot-owned planets")
    elif capability.capability_id == "aspects.whole_sign_graph":
        content = capability.content
        edges = content.get("edges") if isinstance(content, Mapping) else None
        if not isinstance(edges, tuple) or not all(
            _valid_whole_sign_aspect_row(row, planet_signs) for row in edges
        ):
            raise ValueError("published whole-sign aspects must match snapshot-owned planets")


def _issue_key(issue: ConstructionIssue) -> tuple[Any, ...]:
    return (
        not issue.fatal, issue.path, issue.capability_id or "",
        issue.entity_kind or "", issue.entity_id or "", issue.code,
    )


def _missing_capability(definition: GeneralCapabilityDefinition, issues: tuple[str, ...] = ("capability_unavailable",)) -> CapabilitySnapshot:
    return CapabilitySnapshot(
        capability_id=definition.capability_id,
        capability_version=definition.capability_version,
        readiness=CapabilityReadiness.MISSING,
        source_kind=None, content=None, content_empty=False,
        issues=issues, factual_scope=definition.factual_scope,
        core_path=definition.core_path,
    )


def _ready_capability(
    capability_id: str,
    content: Any,
    *,
    source_kind: str,
    factual_scope: str | None = None,
    core_path: str | None = None,
    empty: bool | None = None,
) -> CapabilitySnapshot:
    definition = _GENERAL_DEFINITION_BY_ID[capability_id]
    frozen = None if core_path is not None else freeze_value(content, path=f"$.capabilities.{capability_id}.content")
    if empty is None:
        empty = False if core_path is not None else isinstance(frozen, (tuple, FrozenMap)) and len(frozen) == 0
    if empty and definition.empty_policy == "empty_not_ready":
        return CapabilitySnapshot(
            capability_id=capability_id,
            capability_version=definition.capability_version,
            readiness=CapabilityReadiness.MALFORMED,
            source_kind=source_kind, content=None, content_empty=True,
            issues=("empty_not_ready",), factual_scope=factual_scope or definition.factual_scope,
            core_path=core_path,
        )
    readiness = CapabilityReadiness.READY_EMPTY if empty else CapabilityReadiness.READY
    return CapabilitySnapshot(
        capability_id=capability_id, capability_version=definition.capability_version,
        readiness=readiness, source_kind=source_kind, content=frozen,
        content_empty=empty, issues=(),
        factual_scope=factual_scope or definition.factual_scope,
        core_path=core_path,
    )


def _malformed_capability(
    capability_id: str,
    source_kind: str,
    issue: str,
    *,
    empty: bool = False,
) -> CapabilitySnapshot:
    definition = _GENERAL_DEFINITION_BY_ID[capability_id]
    return CapabilitySnapshot(
        capability_id=capability_id,
        capability_version=definition.capability_version,
        readiness=CapabilityReadiness.MALFORMED,
        source_kind=source_kind, content=None, content_empty=empty,
        issues=(issue,), factual_scope=definition.factual_scope,
        core_path=definition.core_path,
    )


def _copy_supplies(value: Any) -> tuple[AstroCapabilitySupply, ...]:
    if value is None:
        return ()
    if isinstance(value, Mapping):
        result = tuple(value[key] for key in sorted(value))
        if any(not isinstance(item, AstroCapabilitySupply) for item in result):
            raise ValueError("capability_supplies must contain AstroCapabilitySupply values")
        if any(key != item.capability_id for key, item in zip(sorted(value), result)):
            raise ValueError("capability supply key mismatch")
    elif isinstance(value, (list, tuple)):
        result = tuple(value)
        if any(not isinstance(item, AstroCapabilitySupply) for item in result):
            raise ValueError("capability_supplies must contain AstroCapabilitySupply values")
    else:
        raise ValueError("capability_supplies must be a mapping, list, or tuple")
    ids = tuple(item.capability_id for item in result)
    if len(ids) != len(set(ids)):
        raise ValueError("capability supplies must be unique")
    return tuple(sorted(result, key=lambda item: item.capability_id))


def _normalize_supply_content(capability_id: str, content: Any) -> Any:
    if capability_id == "roles.functional":
        if not isinstance(content, Mapping):
            raise ValueError("invalid role supply")
        roles: dict[str, str] = {}
        for raw_id, raw_value in content.items():
            planet = normalize_planet_id(raw_id)
            value = raw_value.get("functional_role") if isinstance(raw_value, Mapping) else raw_value
            if not isinstance(value, str) or planet in roles:
                raise ValueError("invalid role supply")
            roles[planet] = value
        return roles
    return content


def freeze_astrostate(
    construction_state: Any,
    *,
    capability_supplies: Any = None,
    versions: AstroStateVersions | None = None,
    evaluation_context: Mapping[str, Any] | None = None,
) -> AstroStateBuildOutcome:
    """Purely validate/copy one completed mutable construction state."""

    try:
        if construction_state is None or any(
            _attribute(construction_state, name) is _MISSING
            for name in ("metadata", "location", "lagna_sign", "planets", "houses", "enrichments", "derived")
        ):
            raise _fatal("invalid_construction_input", "$")
        current_versions = AstroStateVersions() if versions is None else versions
        if not isinstance(current_versions, AstroStateVersions):
            raise _fatal("invalid_versions", "$.versions")
        try:
            supplies = _copy_supplies(capability_supplies)
        except ValueError:
            raise _fatal("invalid_capability_supplies", "$.capability_supplies")

        metadata_source = _mapping(_attribute(construction_state, "metadata"), path="$.metadata")
        location_source = _attribute(construction_state, "location")
        location = None if location_source is None else FrozenMap(_mapping(location_source, path="$.location"), path="$.core.location")
        if location is not None:
            metadata_source.pop("birth_location", None)
        metadata = FrozenMap(metadata_source, path="$.core.metadata")
        lagna_sign = _attribute(construction_state, "lagna_sign")
        if lagna_sign is not None and lagna_sign not in _SIGNS:
            raise _fatal("invalid_lagna_sign", "$.lagna_sign", "chart.lagna")
        lagna_degree = _finite_optional(_attribute(construction_state, "lagna_degree", None), path="$.lagna_degree")

        raw_planets = _attribute(construction_state, "planets")
        if not isinstance(raw_planets, (list, tuple)):
            raise _fatal("invalid_planet_collection", "$.planets", "planets.normalized")
        planets: list[PlanetFact] = []
        placement: dict[str, int] = {}
        planet_rows: dict[str, Any] = {}
        vargas: dict[str, dict[str, Any]] = {}
        seen: set[str] = set()
        for index, row in enumerate(raw_planets):
            try:
                planet_id = normalize_planet_id(_attribute(row, "name"))
            except ValueError:
                raise _fatal("invalid_planet_id", f"$.planets[{index}]", "planets.normalized")
            if planet_id in seen:
                raise _fatal("duplicate_planet_id", f"$.planets[{index}]", "planets.normalized", "planet", planet_id)
            seen.add(planet_id)
            sign = _attribute(row, "sign", None)
            if sign is not None and sign not in _SIGNS:
                raise _fatal("invalid_planet_sign", f"$.planets[{index}].sign", "planets.normalized", "planet", planet_id)
            degree = _finite_optional(_attribute(row, "degree", None), path=f"$.planets[{index}].degree")
            normalized = _finite_optional(_attribute(row, "degree_norm", None), path=f"$.planets[{index}].degree_norm")
            if normalized is None and degree is not None:
                normalized = degree % 360.0
            if normalized is not None and not 0.0 <= normalized < 360.0:
                raise _fatal("invalid_normalized_longitude", f"$.planets[{index}].degree_norm", "planets.normalized", "planet", planet_id)
            planets.append(PlanetFact(planet_id=planet_id, sign=sign, degree=degree, normalized_longitude=normalized))
            house = _attribute(row, "house", None)
            if house is not None:
                try:
                    placement[planet_id] = _house_number(house)
                except ValueError:
                    raise _fatal("invalid_planet_house", f"$.planets[{index}].house", "planets.house_placement", "planet", planet_id)
            planet_rows[planet_id] = row
            raw_vargas = _attribute(row, "vargas", None)
            if raw_vargas is not None:
                if not isinstance(raw_vargas, Mapping):
                    raise _fatal("invalid_varga_mapping", f"$.planets[{index}].vargas", "vargas.positions", "planet", planet_id)
                for raw_varga, position in raw_vargas.items():
                    try:
                        varga_id = _varga_id(raw_varga)
                    except ValueError:
                        raise _fatal("invalid_varga_id", f"$.planets[{index}].vargas", "vargas.positions", "planet", planet_id)
                    vargas.setdefault(varga_id, {})[planet_id] = position

        raw_houses = _attribute(construction_state, "houses")
        if not isinstance(raw_houses, (list, tuple)):
            raise _fatal("invalid_house_collection", "$.houses", "houses.normalized")
        houses: list[HouseFact] = []
        core_lords: dict[str, Any] = {}
        core_occupants: dict[str, tuple[str, ...]] = {}
        seen_houses: set[int] = set()
        for index, row in enumerate(raw_houses):
            data = _mapping(row, path=f"$.houses[{index}]")
            try:
                number = _house_number(data.get("number"))
            except ValueError:
                raise _fatal("invalid_house_number", f"$.houses[{index}].number", "houses.normalized")
            if number in seen_houses:
                raise _fatal("duplicate_house_number", f"$.houses[{index}]", "houses.normalized", "house", str(number))
            seen_houses.add(number)
            sign = data.get("sign")
            if sign is not None and sign not in _SIGNS:
                raise _fatal("invalid_house_sign", f"$.houses[{index}].sign", "houses.normalized", "house", str(number))
            houses.append(HouseFact(house_number=number, sign=sign))
            if "lord" in data:
                core_lords[str(number)] = data["lord"]
            if "occupants" in data:
                try:
                    core_occupants[str(number)] = tuple(normalize_planet_id(item) for item in data["occupants"])
                except (TypeError, ValueError):
                    raise _fatal("invalid_house_occupants", f"$.houses[{index}].occupants", "houses.occupants", "house", str(number))

        core = AstroCore(
            metadata=metadata, location=location, lagna_sign=lagna_sign,
            lagna_degree=lagna_degree,
            planets=tuple(sorted(planets, key=lambda item: CANONICAL_PLANETS.index(item.planet_id))),
            houses=tuple(sorted(houses, key=lambda item: item.house_number)),
        )
        definitions = _GENERAL_CAPABILITY_DEFINITIONS
        capability_by_id = {item.capability_id: _missing_capability(item) for item in definitions}
        if planets:
            capability_by_id["planets.normalized"] = _ready_capability("planets.normalized", None, source_kind="core_reference", core_path="core.planets")
        if houses:
            capability_by_id["houses.normalized"] = _ready_capability("houses.normalized", None, source_kind="core_reference", core_path="core.houses")
        capability_by_id["chart.metadata"] = _ready_capability("chart.metadata", None, source_kind="core_reference", core_path="core.metadata", empty=not metadata)
        if location is not None:
            capability_by_id["chart.location"] = _ready_capability("chart.location", None, source_kind="core_reference", core_path="core.location")
        if lagna_sign is not None:
            capability_by_id["chart.lagna"] = _ready_capability("chart.lagna", None, source_kind="core_reference", core_path="core.lagna")
        if planets and len(placement) == len(planets):
            capability_by_id["planets.house_placement"] = _ready_capability("planets.house_placement", placement, source_kind="planet_house_fields")
        elif planets and placement:
            capability_by_id["planets.house_placement"] = CapabilitySnapshot(
                capability_id="planets.house_placement", capability_version="1.0.0",
                readiness=CapabilityReadiness.MALFORMED, source_kind="planet_house_fields",
                content=None, content_empty=False, issues=("house_unavailable",),
                factual_scope="factual",
            )

        enrichments = _mapping(_attribute(construction_state, "enrichments"), path="$.enrichments")
        derived_raw = _attribute(construction_state, "derived")
        derived = {} if derived_raw is None else _mapping(derived_raw, path="$.derived")

        canonical_ids = enrichments.get("canonical_planet_ids")
        if isinstance(canonical_ids, Mapping):
            for planet_id in seen:
                expected = planet_id.lower()
                if planet_id in canonical_ids and canonical_ids[planet_id] != expected:
                    raise _fatal("contradictory_canonical_planet_id", "$.enrichments.canonical_planet_ids", "planets.normalized", "planet", planet_id)
        normalized_degrees = enrichments.get("normalized_degrees")
        if isinstance(normalized_degrees, Mapping):
            for fact in planets:
                if fact.planet_id in normalized_degrees and normalized_degrees[fact.planet_id] != fact.normalized_longitude:
                    raise _fatal("contradictory_normalized_longitude", "$.enrichments.normalized_degrees", "planets.normalized", "planet", fact.planet_id)

        summaries = enrichments.get("house_summaries", raw_houses)
        summary_lords: dict[str, Any] = {}
        summary_occupants: dict[str, tuple[str, ...]] = {}
        summary_content: dict[str, Any] = {}
        if isinstance(summaries, (list, tuple)):
            for index, row in enumerate(summaries):
                data = _mapping(row, path=f"$.enrichments.house_summaries[{index}]")
                try:
                    number = _house_number(data.get("number"))
                except ValueError:
                    raise _fatal("invalid_house_summary", f"$.enrichments.house_summaries[{index}]", "houses.normalized")
                key = str(number)
                summary_content[key] = data
                if "lord" in data:
                    summary_lords[key] = data["lord"]
                    if key in core_lords and core_lords[key] != data["lord"]:
                        raise _fatal("contradictory_house_lord", f"$.enrichments.house_summaries[{index}].lord", "houses.lords", "house", key)
                if "occupants" in data:
                    try:
                        values = tuple(normalize_planet_id(item) for item in data["occupants"])
                    except (TypeError, ValueError):
                        raise _fatal("invalid_house_occupants", f"$.enrichments.house_summaries[{index}].occupants", "houses.occupants", "house", key)
                    summary_occupants[key] = values
                    if key in core_occupants and core_occupants[key] != values:
                        raise _fatal("contradictory_house_occupants", f"$.enrichments.house_summaries[{index}].occupants", "houses.occupants", "house", key)
        lords = summary_lords or core_lords
        occupants = summary_occupants or core_occupants
        if isinstance(summaries, (list, tuple)):
            capability_by_id["houses.lords"] = _ready_capability("houses.lords", lords, source_kind="house_summaries", empty=not lords)
            capability_by_id["houses.occupants"] = _ready_capability("houses.occupants", occupants, source_kind="house_summaries", empty=not occupants)
            capability_by_id["houses.summaries"] = _ready_capability("houses.summaries", summary_content, source_kind="house_summaries", factual_scope="legacy_compatibility", empty=not summary_content)

        diagnostics = _mapping(_attribute(construction_state, "diagnostics"), path="$.diagnostics")
        if "lagna_summary" in diagnostics:
            capability_by_id["chart.lagna_summary"] = _ready_capability(
                "chart.lagna_summary", diagnostics["lagna_summary"],
                source_kind="lagna_summary", factual_scope="legacy_compatibility",
                empty=not diagnostics["lagna_summary"],
            )

        strength_rows = enrichments.get("planet_strengths")
        strength_map = strength_rows if isinstance(strength_rows, Mapping) else {}
        dignity_content: dict[str, Any] = {}
        strength_content: dict[str, Any] = {}
        shadbala_content: dict[str, Any] = {}
        for fact in planets:
            row = planet_rows[fact.planet_id]
            enriched = strength_map.get(fact.planet_id)
            enriched_map = enriched if isinstance(enriched, Mapping) else {}
            dignity = _attribute(row, "dignity", None)
            strength = _attribute(row, "strength", None)
            dignity_content[fact.planet_id] = {
                "value": dignity, "value_present": dignity is not None,
                "enriched_value": enriched_map.get("dignity"),
                "enriched_value_present": "dignity" in enriched_map,
            }
            strength_content[fact.planet_id] = {
                "value": strength, "value_present": strength is not None,
                "enriched_value": enriched_map.get("strength"),
                "enriched_value_present": "strength" in enriched_map,
                "detail": enriched_map,
            }
            if "shadbala" in enriched_map:
                shadbala_content[fact.planet_id] = enriched_map["shadbala"]
        capability_by_id["dignity.planet"] = _ready_capability("dignity.planet", dignity_content, source_kind="planet_and_strength_rows", empty=not dignity_content)
        capability_by_id["strengths.planet"] = _ready_capability("strengths.planet", strength_content, source_kind="planet_and_strength_rows", factual_scope="legacy_composite", empty=not strength_content)
        if shadbala_content:
            capability_by_id["strengths.shadbala"] = _ready_capability("strengths.shadbala", shadbala_content, source_kind="legacy_strength_rows", factual_scope="legacy_partial_proxy")
        capability_by_id["vargas.positions"] = _ready_capability("vargas.positions", vargas, source_kind="planet_varga_fields", empty=not vargas)

        aspect_value = enrichments.get("aspects", _MISSING)
        if isinstance(aspect_value, list):
            if not all(_valid_basic_aspect_row(row, seen) for row in aspect_value):
                raise _fatal(
                    "invalid_basic_aspect_content",
                    "$.enrichments.aspects",
                    "aspects.basic_conjunction_list",
                )
            capability_by_id["aspects.basic_conjunction_list"] = _ready_capability(
                "aspects.basic_conjunction_list", aspect_value,
                source_kind="legacy_basic_conjunction_list", empty=not aspect_value,
            )
        elif isinstance(aspect_value, Mapping):
            edges = aspect_value.get("edges")
            planet_signs = {item.planet_id: item.sign for item in planets}
            valid = (
                isinstance(edges, (list, tuple))
                and all(_valid_whole_sign_aspect_row(row, planet_signs) for row in edges)
                and (
                    aspect_value.get("config_version") is None
                    or (
                        not isinstance(aspect_value.get("config_version"), bool)
                        and isinstance(aspect_value.get("config_version"), (str, int))
                    )
                )
            )
            if not valid:
                raise _fatal(
                    "invalid_whole_sign_aspect_content",
                    "$.enrichments.aspects",
                    "aspects.whole_sign_graph",
                )
            capability_by_id["aspects.whole_sign_graph"] = _ready_capability(
                "aspects.whole_sign_graph", aspect_value,
                source_kind="legacy_whole_sign_graph", empty=not edges,
            )
        elif aspect_value is not _MISSING and aspect_value is not None:
            raise _fatal("invalid_aspect_representation", "$.enrichments.aspects")
        relationships = derived.get("relationships")
        derived_aspects = relationships.get("aspects") if isinstance(relationships, Mapping) else _MISSING
        if isinstance(derived_aspects, list):
            existing = capability_by_id["aspects.basic_conjunction_list"]
            if not all(_valid_basic_aspect_row(row, seen) for row in derived_aspects):
                raise _fatal(
                    "invalid_basic_aspect_content",
                    "$.derived.relationships.aspects",
                    "aspects.basic_conjunction_list",
                )
            frozen_derived = freeze_value(derived_aspects, path="$.derived.relationships.aspects")
            if existing.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
                if frozen_derived is not None and existing.content != frozen_derived:
                    raise _fatal("contradictory_basic_aspects", "$.derived.relationships.aspects", "aspects.basic_conjunction_list")
            elif frozen_derived is not None:
                capability_by_id["aspects.basic_conjunction_list"] = _ready_capability("aspects.basic_conjunction_list", derived_aspects, source_kind="derived_relationships", empty=not derived_aspects)

        roles = derived.get("functional_roles")
        if isinstance(roles, Mapping):
            role_content: dict[str, str] = {}
            for raw_planet, raw_row in roles.items():
                try:
                    planet = normalize_planet_id(raw_planet)
                except ValueError:
                    raise _fatal("invalid_functional_role_entity", "$.derived.functional_roles", "roles.functional")
                value = raw_row.get("functional_role") if isinstance(raw_row, Mapping) else raw_row
                if not isinstance(value, str):
                    raise _fatal("invalid_functional_role", "$.derived.functional_roles", "roles.functional", "planet", planet)
                role_content[planet] = value
            capability_by_id["roles.functional"] = _ready_capability("roles.functional", role_content, source_kind="derived_functional_roles", empty=not role_content)

        exaltation_rows: list[dict[str, Any]] = []
        metadata_exaltations = metadata_source.get("exaltations")
        if metadata_exaltations is not None:
            if not isinstance(metadata_exaltations, Mapping):
                raise _fatal("invalid_exaltation_mapping", "$.metadata.exaltations", "dignity.exaltation_facts")
            for raw_planet, value in metadata_exaltations.items():
                try:
                    planet = normalize_planet_id(raw_planet)
                except ValueError:
                    raise _fatal("invalid_exaltation_entity", "$.metadata.exaltations", "dignity.exaltation_facts")
                exaltation_rows.append({"planet_id": planet, "source_kind": "legacy_metadata_exaltations", "value": value})
        if metadata_exaltations is not None:
            exaltation_rows.sort(key=lambda item: (CANONICAL_PLANETS.index(item["planet_id"]), item["source_kind"]))
            capability_by_id["dignity.exaltation_facts"] = _ready_capability("dignity.exaltation_facts", exaltation_rows, source_kind="legacy_metadata_exaltations", empty=not exaltation_rows)

        for supply in supplies:
            definition = _GENERAL_DEFINITION_BY_ID.get(supply.capability_id)
            if definition is None:
                raise _fatal("unknown_capability_supply", "$.capability_supplies", supply.capability_id)
            if definition.core_path is not None:
                raise _fatal(
                    "core_capability_supply_not_allowed", "$.capability_supplies",
                    supply.capability_id,
                )
            if supply.capability_version != definition.capability_version:
                capability_by_id[supply.capability_id] = CapabilitySnapshot(
                    capability_id=supply.capability_id,
                    capability_version=definition.capability_version,
                    readiness=CapabilityReadiness.VERSION_MISMATCH,
                    source_kind=supply.source_kind, content=None, content_empty=False,
                    issues=("supplied_version_mismatch",), factual_scope=supply.factual_scope,
                )
                continue
            try:
                normalized_content = _normalize_supply_content(supply.capability_id, supply.content)
                supplied = _ready_capability(
                    supply.capability_id, normalized_content,
                    source_kind=supply.source_kind, factual_scope=supply.factual_scope,
                )
                _validate_snapshot_aspect_capability(supplied, core)
            except (AstroCanonicalValueError, TypeError, ValueError):
                raise _fatal("invalid_capability_supply", "$.capability_supplies", supply.capability_id)
            existing = capability_by_id[supply.capability_id]
            if existing.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY) and existing.content != supplied.content:
                raise _fatal("contradictory_capability_supply", "$.capability_supplies", supply.capability_id)
            capability_by_id[supply.capability_id] = supplied

        try:
            context = _evaluation_context({} if evaluation_context is None else evaluation_context)
        except (AstroCanonicalValueError, ValueError):
            raise _fatal("invalid_evaluation_context", "$.evaluation_context")
        issues = tuple(sorted((
            ConstructionIssue(
                code=("malformed_capability" if item.readiness is CapabilityReadiness.MALFORMED else "capability_unavailable"),
                path=f"$.capabilities.{item.capability_id}",
                capability_id=item.capability_id, recoverable=True, fatal=False,
            )
            for item in capability_by_id.values()
            if item.readiness in (
                CapabilityReadiness.MISSING,
                CapabilityReadiness.MALFORMED,
                CapabilityReadiness.VERSION_MISMATCH,
            )
        ), key=_issue_key))
        snapshot = AstroStateSnapshot(
            schema_version=current_versions.schema_version,
            producer_version=current_versions.producer_version,
            normalization_version=current_versions.normalization_version,
            system_scope=SYSTEM_SCOPE,
            evaluation_context=context,
            core=core,
            capabilities=tuple(capability_by_id[key] for key in sorted(capability_by_id)),
            construction_issues=issues,
        )
        return AstroStateBuildSuccess(snapshot=snapshot, issues=issues)
    except _BuildFailure as failure:
        return AstroStateBuildFailure(issues=(failure.issue,))
    except AstroCanonicalValueError:
        issue = ConstructionIssue(code="unsafe_canonical_content", path="$", recoverable=False, fatal=True)
        return AstroStateBuildFailure(issues=(issue,))


def require_snapshot(outcome: AstroStateBuildOutcome) -> AstroStateSnapshot:
    if isinstance(outcome, AstroStateBuildFailure):
        raise ValueError("AstroState snapshot construction failed")
    return outcome.snapshot


def _aspect_facts(capability: CapabilitySnapshot) -> tuple[AspectFact, ...]:
    if capability.content is None:
        return ()
    rows: Any
    config_version = None
    if capability.capability_id == "aspects.basic_conjunction_list":
        rows = capability.content
        result = []
        for row in rows:
            result.append(AspectFact(
                representation="basic_conjunction_list", source_kind="planet",
                source_id=normalize_planet_id(row["from"]), target_kind="planet",
                target_id=normalize_planet_id(row["to"]), target_sign=None,
                aspect_kind=row["type"],
                configuration_version=None,
            ))
        return tuple(result)
    rows = capability.content["edges"]
    raw_config_version = capability.content.get("config_version")
    config_version = None if raw_config_version is None else str(raw_config_version)
    result = []
    for row in rows:
        target = row.get("target")
        target_sign = row["trace"]["target_sign"]
        result.append(AspectFact(
            representation="whole_sign_graph", source_kind="planet",
            source_id=normalize_planet_id(row["source"]),
            target_kind="planet" if target is not None else "sign",
            target_id=(normalize_planet_id(target) if target is not None else target_sign),
            target_sign=target_sign,
            aspect_kind=row.get("aspect", row.get("kind", "whole_sign")),
            configuration_version=config_version,
        ))
    return tuple(result)


def snapshot_logical_projection(snapshot: AstroStateSnapshot) -> dict[str, Any]:
    if not isinstance(snapshot, AstroStateSnapshot):
        raise TypeError("snapshot must be AstroStateSnapshot")
    return {
        "schema_version": snapshot.schema_version,
        "producer_version": snapshot.producer_version,
        "normalization_version": snapshot.normalization_version,
        "system_scope": snapshot.system_scope,
        "evaluation_context": thaw_value(snapshot.evaluation_context),
        "core": thaw_value(snapshot.core),
        "capabilities": [thaw_value(item) for item in snapshot.capabilities],
        "construction_issues": [thaw_value(item) for item in snapshot.construction_issues],
    }


def snapshot_logical_bytes(snapshot: AstroStateSnapshot) -> bytes:
    return json.dumps(
        snapshot_logical_projection(snapshot), ensure_ascii=False,
        allow_nan=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def snapshot_logical_sha256(snapshot: AstroStateSnapshot) -> str:
    return hashlib.sha256(snapshot_logical_bytes(snapshot)).hexdigest()


def astro_query_result_to_data(result: AstroQueryResult[Any]) -> dict[str, Any]:
    if not isinstance(result, AstroQueryResult):
        raise TypeError("result must be AstroQueryResult")
    return {
        "capability_id": result.capability_id,
        "capability_version": result.capability_version,
        "state": result.state.value,
        "entity_kind": result.entity_kind,
        "entity_id": result.entity_id,
        "value_present": result.value_present,
        "value": thaw_value(result.value),
        "issues": list(result.issues),
    }


def astro_query_result_json_bytes(result: AstroQueryResult[Any]) -> bytes:
    return json.dumps(
        astro_query_result_to_data(result), ensure_ascii=False,
        allow_nan=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def snapshot_from_logical_bytes(payload: bytes) -> AstroStateSnapshot:
    """Restore one snapshot from its strict logical projection."""

    if not isinstance(payload, bytes):
        raise TypeError("snapshot payload must be bytes")
    try:
        data = json.loads(
            payload.decode("utf-8"),
            parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite number")),
        )
        core_data = data["core"]
        core = AstroCore(
            metadata=FrozenMap(core_data["metadata"], path="$.core.metadata"),
            location=(
                None if core_data["location"] is None
                else FrozenMap(core_data["location"], path="$.core.location")
            ),
            lagna_sign=core_data["lagna_sign"],
            lagna_degree=core_data["lagna_degree"],
            planets=tuple(PlanetFact(**item) for item in core_data["planets"]),
            houses=tuple(HouseFact(**item) for item in core_data["houses"]),
        )
        capabilities = tuple(
            CapabilitySnapshot(
                capability_id=item["capability_id"],
                capability_version=item["capability_version"],
                readiness=CapabilityReadiness(item["readiness"]),
                source_kind=item["source_kind"],
                content=(
                    None if item["content"] is None
                    else freeze_value(item["content"], path=f"$.capabilities.{item['capability_id']}.content")
                ),
                content_empty=item["content_empty"],
                issues=tuple(item["issues"]),
                factual_scope=item["factual_scope"],
                core_path=item.get("core_path"),
            )
            for item in data["capabilities"]
        )
        issues = tuple(ConstructionIssue(**item) for item in data["construction_issues"])
        snapshot = AstroStateSnapshot(
            schema_version=data["schema_version"],
            producer_version=data["producer_version"],
            normalization_version=data["normalization_version"],
            system_scope=data["system_scope"],
            evaluation_context=FrozenMap(data["evaluation_context"], path="$.evaluation_context"),
            core=core, capabilities=capabilities, construction_issues=issues,
        )
    except (KeyError, TypeError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid AstroState snapshot payload") from exc
    if snapshot_logical_bytes(snapshot) != payload:
        raise ValueError("snapshot payload is not canonical")
    return snapshot


__all__ = (
    "AstroCapabilitySupply", "AstroCore", "AstroQueryResult",
    "AstroStateBuildFailure", "AstroStateBuildOutcome", "AstroStateBuildSuccess",
    "AstroStateSnapshot", "AstroStateVersions", "AspectFact", "CapabilitySnapshot",
    "ConstructionIssue", "DignityFact", "FrozenMap", "FunctionalRoleFact",
    "GeneralCapabilityDefinition", "HouseFact", "NORMALIZATION_COMPATIBILITY_VERSION",
    "PlanetFact", "SNAPSHOT_PRODUCER_VERSION", "SNAPSHOT_SCHEMA_VERSION",
    "SYSTEM_SCOPE", "StrengthFact", "VargaFact", "VargaPositionFact",
    "astro_query_result_json_bytes", "astro_query_result_to_data",
    "freeze_astrostate", "freeze_value",
    "get_general_capability_catalog", "require_snapshot", "snapshot_logical_bytes",
    "snapshot_from_logical_bytes", "snapshot_logical_projection", "snapshot_logical_sha256", "thaw_value",
)
