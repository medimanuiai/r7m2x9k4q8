"""Immutable predicate-owned prepared facts, queries, context, and digests."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib
import math
import re
from types import MappingProxyType
from typing import Any

from systems.Parasara.engine.rules.canonical import (
    CanonicalValueError,
    FrozenMapping,
    canonical_json_bytes,
    freeze_canonical,
)
from systems.Parasara.engine.rules.capabilities import (
    CapabilityCatalogMiss,
    CapabilityFactObservation,
    CapabilityFactState,
    CapabilityInspection,
    CapabilityReadiness,
    CapabilityRequirement,
    EmptyPolicy,
    get_production_capability_catalog,
    inspect_capability,
)
from systems.Parasara.engine.rules.parameters import (
    CANONICAL_PLANETS,
    FUNCTIONAL_ROLE_VALUES,
)


PREPARED_STATE_SCHEMA_VERSION = "1.0.0"
PREPARATION_CONTRACT_VERSION = "1.0.0"
NORMALIZATION_COMPATIBILITY_VERSION = "1.0.0"
SYSTEM_SCOPE = "parasara"

_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_SAFE_CODE = re.compile(r"^[a-z][a-z0-9_]*$")
_CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
_SIGNS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)
_PLANET_LOOKUP = {item.lower(): item for item in CANONICAL_PLANETS}
_MISSING = object()
_CAPABILITY_CATALOG = get_production_capability_catalog()


def _require_semver(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not _SEMVER.fullmatch(value):
        raise ValueError(f"{field_name} must be strict MAJOR.MINOR.PATCH SemVer")
    return value


def _canonical_planet(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped or not stripped.isascii():
        return None
    return _PLANET_LOOKUP.get(stripped.lower())


def _attribute(value: Any, name: str) -> Any:
    try:
        return getattr(value, name)
    except AttributeError:
        return _MISSING


def _safe_issues(value: tuple[str, ...]) -> tuple[str, ...]:
    if not isinstance(value, tuple) or any(
        type(item) is not str or not _SAFE_CODE.fullmatch(item) for item in value
    ):
        raise TypeError("issues must be an immutable tuple of safe codes")
    if len(set(value)) != len(value):
        raise ValueError("issues must not contain duplicate codes")
    return value


def _content_is_empty(capability_id: str, content: Any) -> bool:
    if capability_id == "aspects.whole_sign_graph":
        return isinstance(content, Mapping) and "edges" in content and len(content["edges"]) == 0
    if isinstance(content, (str, tuple, Mapping)):
        return len(content) == 0
    return False


def _validate_prepared_content(capability_id: str, content: Any) -> None:
    if capability_id == "planets.normalized":
        if not isinstance(content, tuple):
            raise ValueError("normalized planet content must be a tuple")
        identities: list[str] = []
        for row in content:
            if not isinstance(row, Mapping) or set(row) != {"planet_id", "house", "sign"}:
                raise ValueError("malformed normalized planet content")
            PreparedPlanet(planet_id=row["planet_id"], house=row["house"], sign=row["sign"])
            identities.append(row["planet_id"])
        if len(set(identities)) != len(identities) or tuple(identities) != tuple(
            item for item in CANONICAL_PLANETS if item in identities
        ):
            raise ValueError("normalized planet content has invalid identity ordering")
        return
    if capability_id == "planets.house_placement":
        if not isinstance(content, Mapping) or any(
            planet_id not in CANONICAL_PLANETS or type(house) is not int or not 1 <= house <= 12
            for planet_id, house in content.items()
        ):
            raise ValueError("malformed house-placement content")
        return
    if capability_id == "aspects.basic_conjunction_list":
        if not isinstance(content, tuple) or any(
            not isinstance(edge, Mapping)
            or any(not isinstance(edge.get(key), str) for key in ("from", "to", "type"))
            for edge in content
        ):
            raise ValueError("malformed basic Aspect content")
        return
    if capability_id == "aspects.whole_sign_graph":
        if not isinstance(content, Mapping) or "edges" not in content or not isinstance(content["edges"], tuple):
            raise ValueError("malformed whole-sign graph content")
        for edge in content["edges"]:
            if (
                not isinstance(edge, Mapping)
                or not isinstance(edge.get("source"), str)
                or (edge.get("target") is not None and not isinstance(edge.get("target"), str))
                or any(key in edge and not isinstance(edge[key], str) for key in ("aspect", "kind"))
            ):
                raise ValueError("malformed whole-sign graph edge")
        return
    if capability_id == "chart.lagna":
        if content not in _SIGNS:
            raise ValueError("malformed Lagna content")
        return
    if capability_id == "roles.functional":
        if not isinstance(content, Mapping) or any(
            planet_id not in CANONICAL_PLANETS or role not in FUNCTIONAL_ROLE_VALUES
            for planet_id, role in content.items()
        ):
            raise ValueError("malformed functional-role content")
        return
    if capability_id == "dignity.exaltation_facts":
        if not isinstance(content, tuple):
            raise ValueError("malformed exaltation content")
        identities: list[tuple[str, str]] = []
        for row in content:
            if not isinstance(row, Mapping) or set(row) != {"planet_id", "source_kind", "value"}:
                raise ValueError("malformed exaltation record")
            value = row["value"]
            if (
                row["planet_id"] not in CANONICAL_PLANETS
                or not isinstance(row["source_kind"], str)
                or not _SAFE_CODE.fullmatch(row["source_kind"])
                or (type(value) is not bool and not isinstance(value, (int, float)))
                or (isinstance(value, float) and not math.isfinite(value))
            ):
                raise ValueError("malformed exaltation record")
            identities.append((row["planet_id"], row["source_kind"]))
        expected = tuple(sorted(identities, key=lambda item: (CANONICAL_PLANETS.index(item[0]), item[1])))
        if len(set(identities)) != len(identities) or tuple(identities) != expected:
            raise ValueError("exaltation records have invalid identity ordering")
        return
    raise ValueError("unsupported prepared capability content")


@dataclass(frozen=True, slots=True, kw_only=True)
class PreparedStateVersions:
    schema_version: str = PREPARED_STATE_SCHEMA_VERSION
    producer_version: str = PREPARATION_CONTRACT_VERSION
    normalization_version: str = NORMALIZATION_COMPATIBILITY_VERSION

    def __post_init__(self) -> None:
        _require_semver(self.schema_version, "schema_version")
        _require_semver(self.producer_version, "producer_version")
        _require_semver(self.normalization_version, "normalization_version")


@dataclass(frozen=True, slots=True, kw_only=True)
class PreparedPlanet:
    planet_id: str
    house: int | None
    sign: str | None

    def __post_init__(self) -> None:
        if self.planet_id not in CANONICAL_PLANETS:
            raise ValueError("planet_id must be a canonical planet")
        if self.house is not None and (type(self.house) is not int or not 1 <= self.house <= 12):
            raise ValueError("house must be a strict integer from 1 through 12 or None")
        if self.sign is not None and self.sign not in _SIGNS:
            raise ValueError("sign must be a canonical sign or None")


@dataclass(frozen=True, slots=True, kw_only=True)
class PreparedCapability:
    capability_id: str
    capability_version: str
    observed_version: str | None
    readiness: CapabilityReadiness
    source_kind: str | None
    content_empty: bool
    content: Any
    issues: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not _CAPABILITY_ID.fullmatch(self.capability_id):
            raise ValueError("capability_id must be canonical")
        _require_semver(self.capability_version, "capability_version")
        if self.observed_version is not None:
            _require_semver(self.observed_version, "observed_version")
        if not isinstance(self.readiness, CapabilityReadiness):
            raise TypeError("readiness must be CapabilityReadiness")
        if self.source_kind is not None and (
            not isinstance(self.source_kind, str) or not _SAFE_CODE.fullmatch(self.source_kind)
        ):
            raise ValueError("source_kind must be a safe identifier")
        if type(self.content_empty) is not bool:
            raise TypeError("content_empty must be an actual Boolean")
        _safe_issues(self.issues)

        found = _CAPABILITY_CATALOG.lookup(self.capability_id)
        if isinstance(found, CapabilityCatalogMiss):
            if self.readiness is not CapabilityReadiness.UNSUPPORTED:
                raise ValueError("unknown capability must be explicitly unsupported")
        elif self.capability_version != found.capability_version:
            raise ValueError("capability_version must match the production catalog")
        if (
            not isinstance(found, CapabilityCatalogMiss)
            and self.readiness is CapabilityReadiness.READY_EMPTY
            and found.empty_policy is not EmptyPolicy.READY_EMPTY
        ):
            raise ValueError("catalog policy does not allow ready_empty")

        ready = self.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY)
        if ready:
            if self.content is None:
                raise ValueError("ready capability requires explicit canonical content")
            object.__setattr__(self, "content", freeze_canonical(self.content, path="$.content"))
            _validate_prepared_content(self.capability_id, self.content)
            if self.readiness is CapabilityReadiness.READY and self.content_empty:
                raise ValueError("ready capability content cannot be empty")
            if self.readiness is CapabilityReadiness.READY_EMPTY and not self.content_empty:
                raise ValueError("ready_empty capability requires explicit empty content")
            if _content_is_empty(self.capability_id, self.content) is not self.content_empty:
                raise ValueError("content_empty must match canonical content")
            if self.issues:
                raise ValueError("ready capability cannot contain issues")
            if self.source_kind is None or self.observed_version != self.capability_version:
                raise ValueError("ready capability requires a matching observed version and source")
        elif self.content is not None:
            raise ValueError("unavailable capability cannot carry factual content")
        if self.readiness not in (CapabilityReadiness.MISSING, CapabilityReadiness.UNSUPPORTED) and self.source_kind is None:
            raise ValueError("observed capability requires a source kind")
        if self.readiness is CapabilityReadiness.VERSION_MISMATCH:
            if self.observed_version is None or self.observed_version == self.capability_version:
                raise ValueError("version mismatch requires a distinct observed version")
        if self.readiness in (CapabilityReadiness.MISSING, CapabilityReadiness.UNSUPPORTED):
            if self.observed_version is not None or self.source_kind is not None or self.content_empty:
                raise ValueError("missing or unsupported capability cannot claim source content")


class PreparedCapabilityMapping(Mapping[str, PreparedCapability]):
    """Small immutable mapping that can own prepared model objects."""

    __slots__ = ("_items", "_lookup")

    def __init__(self, value: Mapping[str, PreparedCapability] | Sequence[PreparedCapability]):
        if isinstance(value, Mapping):
            items = tuple(value.items())
        else:
            items = tuple((item.capability_id, item) for item in value)
        if any(type(key) is not str or not isinstance(item, PreparedCapability) for key, item in items):
            raise TypeError("capabilities require string keys and PreparedCapability values")
        if any(key != item.capability_id for key, item in items):
            raise ValueError("capability mapping key must match capability identity")
        keys = tuple(key for key, _ in items)
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate capability identity")
        ordered = tuple(sorted(items, key=lambda pair: pair[0]))
        object.__setattr__(self, "_items", ordered)
        object.__setattr__(self, "_lookup", MappingProxyType(dict(ordered)))

    def __setattr__(self, name: str, value: Any) -> None:
        raise TypeError("PreparedCapabilityMapping is immutable")

    def __getitem__(self, key: str) -> PreparedCapability:
        return self._lookup[key]

    def __iter__(self) -> Iterator[str]:
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Mapping) or len(self) != len(other):
            return False
        return all(key in other and value == other[key] for key, value in self._items)


@dataclass(frozen=True, slots=True, kw_only=True)
class PreparedAstroState:
    schema_version: str
    producer_version: str
    normalization_version: str
    system_scope: str
    lagna_sign: str | None
    planets: tuple[PreparedPlanet, ...]
    capabilities: PreparedCapabilityMapping | Mapping[str, PreparedCapability]

    def __post_init__(self) -> None:
        _require_semver(self.schema_version, "schema_version")
        _require_semver(self.producer_version, "producer_version")
        _require_semver(self.normalization_version, "normalization_version")
        if self.system_scope != SYSTEM_SCOPE:
            raise ValueError("system_scope must be parasara")
        if self.lagna_sign is not None and self.lagna_sign not in _SIGNS:
            raise ValueError("lagna_sign must be canonical or None")
        if not isinstance(self.planets, tuple) or any(not isinstance(item, PreparedPlanet) for item in self.planets):
            raise TypeError("planets must be an immutable PreparedPlanet tuple")
        identities = tuple(item.planet_id for item in self.planets)
        if len(set(identities)) != len(identities):
            raise ValueError("duplicate prepared planet identity")
        expected_order = tuple(item for item in CANONICAL_PLANETS if item in identities)
        if identities != expected_order:
            raise ValueError("prepared planets must use canonical catalog order")
        if not isinstance(self.capabilities, PreparedCapabilityMapping):
            object.__setattr__(self, "capabilities", PreparedCapabilityMapping(self.capabilities))
        expected_capabilities = _CAPABILITY_CATALOG.capability_ids()
        if tuple(self.capabilities) != expected_capabilities:
            raise ValueError("prepared state must contain the complete production capability manifest")
        lagna = self.capabilities["chart.lagna"]
        expected_lagna = lagna.content if lagna.readiness is CapabilityReadiness.READY else None
        if self.lagna_sign != expected_lagna:
            raise ValueError("lagna_sign must agree with the chart.lagna capability")
        normalized = self.capabilities["planets.normalized"]
        expected_planets = (
            tuple(prepared_planet_to_data(item) for item in self.planets)
            if normalized.readiness is CapabilityReadiness.READY
            else None
        )
        if normalized.content != expected_planets:
            raise ValueError("planets must agree with the planets.normalized capability")
        placements = self.capabilities["planets.house_placement"]
        if placements.readiness is CapabilityReadiness.READY:
            expected_placements = FrozenMapping({item.planet_id: item.house for item in self.planets})
            if placements.content != expected_placements:
                raise ValueError("planets must agree with the house-placement capability")


@dataclass(frozen=True, slots=True, kw_only=True)
class PreparationIssue:
    code: str
    path: str
    capability_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not _SAFE_CODE.fullmatch(self.code):
            raise ValueError("preparation issue code must be safe")
        if not isinstance(self.path, str) or not self.path.startswith("$"):
            raise ValueError("preparation issue path must be safe and rooted")
        if self.capability_id is not None and not _CAPABILITY_ID.fullmatch(self.capability_id):
            raise ValueError("preparation issue capability_id must be canonical")


@dataclass(frozen=True, slots=True, kw_only=True)
class PreparationOutcome:
    succeeded: bool
    state: PreparedAstroState | None
    issues: tuple[PreparationIssue, ...]

    def __post_init__(self) -> None:
        if type(self.succeeded) is not bool or not isinstance(self.issues, tuple):
            raise TypeError("preparation outcome fields have invalid types")
        if any(not isinstance(item, PreparationIssue) for item in self.issues):
            raise TypeError("preparation issues must be typed")
        if self.succeeded is not (self.state is not None and not self.issues):
            raise ValueError("successful preparation has one state and no fatal issues")


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilitySupply:
    capability_id: str
    capability_version: str
    source_kind: str
    content: Any

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not _CAPABILITY_ID.fullmatch(self.capability_id):
            raise ValueError("supply capability_id must be canonical")
        _require_semver(self.capability_version, "capability_version")
        if not isinstance(self.source_kind, str) or not _SAFE_CODE.fullmatch(self.source_kind):
            raise ValueError("supply source_kind must be safe")


def _fatal(code: str, path: str, capability_id: str | None = None) -> PreparationOutcome:
    return PreparationOutcome(
        succeeded=False,
        state=None,
        issues=(PreparationIssue(code=code, path=path, capability_id=capability_id),),
    )


def _requirement(capability_id: str, version: str) -> CapabilityRequirement:
    return CapabilityRequirement(
        capability_id=capability_id,
        capability_version=version,
        required=True,
        when_parameters_present=(),
    )


def _prepared_planets(astro: Any, inspection: CapabilityInspection) -> tuple[PreparedPlanet, ...]:
    if inspection.readiness is not CapabilityReadiness.READY:
        return ()
    rows = _attribute(astro, "planets")
    prepared: list[PreparedPlanet] = []
    for planet_id in CANONICAL_PLANETS:
        row = next((item for item in rows if _attribute(item, "name") == planet_id), _MISSING)
        if row is _MISSING:
            continue
        house = _attribute(row, "house")
        sign = _attribute(row, "sign")
        valid_house = house if type(house) is int and 1 <= house <= 12 else None
        prepared.append(
            PreparedPlanet(
                planet_id=planet_id,
                house=valid_house,
                sign=None if sign is _MISSING or sign is None else sign,
            )
        )
    return tuple(prepared)


def _graph_projection(value: Mapping) -> FrozenMapping:
    edges = []
    for index, edge in enumerate(value["edges"]):
        projected: dict[str, Any] = {"source": edge["source"], "target": edge.get("target")}
        for key in ("aspect", "kind"):
            if key in edge:
                if not isinstance(edge[key], str):
                    raise ValueError("malformed_graph_projection")
                projected[key] = edge[key]
        edges.append(projected)
    content: dict[str, Any] = {"edges": edges}
    for key in ("capability_version", "config_version"):
        if key in value:
            content[key] = value[key]
    return FrozenMapping(content, path="$.capabilities.aspects.whole_sign_graph.content")


def _exaltation_projection(astro: Any) -> tuple[FrozenMapping, ...]:
    records: list[dict[str, Any]] = []
    rows = _attribute(astro, "planets")
    if isinstance(rows, (list, tuple)):
        for row in rows:
            planet_id = _attribute(row, "name")
            raw = _attribute(row, "__dict__")
            flags = raw.get("flags", _MISSING) if isinstance(raw, Mapping) else _MISSING
            if isinstance(flags, Mapping) and planet_id in CANONICAL_PLANETS and "exalted" in flags:
                records.append({"planet_id": planet_id, "source_kind": "legacy_planet_flags", "value": flags["exalted"]})
    metadata = _attribute(astro, "metadata")
    if isinstance(metadata, Mapping) and isinstance(metadata.get("exaltations", _MISSING), Mapping):
        for planet_id, value in metadata["exaltations"].items():
            records.append({"planet_id": planet_id, "source_kind": "legacy_metadata_exaltations", "value": value})
    planet_order = {value: index for index, value in enumerate(CANONICAL_PLANETS)}
    records.sort(key=lambda item: (planet_order[item["planet_id"]], item["source_kind"]))
    return tuple(FrozenMapping(item) for item in records)


def _compatibility_content(
    astro: Any,
    capability_id: str,
    inspection: CapabilityInspection,
    planets: tuple[PreparedPlanet, ...],
) -> Any:
    if inspection.readiness not in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
        return None
    if capability_id == "planets.normalized":
        return tuple(FrozenMapping({"planet_id": p.planet_id, "house": p.house, "sign": p.sign}) for p in planets)
    if capability_id == "planets.house_placement":
        return FrozenMapping({p.planet_id: p.house for p in planets})
    if capability_id == "chart.lagna":
        return _attribute(astro, "lagna_sign")
    if capability_id.startswith("aspects."):
        value = _attribute(astro, "enrichments")["aspects"]
        if capability_id == "aspects.basic_conjunction_list":
            return freeze_canonical(value, path="$.capabilities.aspects.basic_conjunction_list.content")
        return _graph_projection(value)
    if capability_id == "roles.functional":
        roles = _attribute(astro, "derived")["functional_roles"]
        return FrozenMapping({planet_id: roles[planet_id]["functional_role"] for planet_id in roles})
    if capability_id == "dignity.exaltation_facts":
        return _exaltation_projection(astro)
    raise ValueError("unsupported_capability_projection")


def _capability_from_inspection(
    astro: Any,
    capability_id: str,
    inspection: CapabilityInspection,
    planets: tuple[PreparedPlanet, ...],
) -> PreparedCapability:
    try:
        content = _compatibility_content(astro, capability_id, inspection, planets)
    except ValueError as exc:
        if str(exc) != "malformed_graph_projection":
            raise
        return PreparedCapability(
            capability_id=capability_id,
            capability_version=inspection.expected_version,
            observed_version=inspection.observed_version,
            readiness=CapabilityReadiness.MALFORMED,
            source_kind=inspection.source_kind,
            content_empty=inspection.content_empty,
            content=None,
            issues=("malformed_graph_projection",),
        )
    return PreparedCapability(
        capability_id=capability_id,
        capability_version=inspection.expected_version,
        observed_version=inspection.observed_version,
        readiness=inspection.readiness,
        source_kind=inspection.source_kind,
        content_empty=inspection.content_empty,
        content=content,
        issues=inspection.issues,
    )


def _normalize_role_supply(content: Any) -> tuple[Any, tuple[str, ...]]:
    if not isinstance(content, Mapping):
        return None, ("wrong_role_mapping_type",)
    result: dict[str, str] = {}
    for raw_planet, raw_value in content.items():
        planet_id = _canonical_planet(raw_planet)
        value = raw_value.get("functional_role") if isinstance(raw_value, Mapping) else raw_value
        if planet_id is None or value not in FUNCTIONAL_ROLE_VALUES or planet_id in result:
            return None, ("malformed_role_fact",)
        result[planet_id] = value
    return FrozenMapping(result), ()


def _normalize_supply_content(supply: CapabilitySupply, empty_policy: EmptyPolicy) -> tuple[Any, bool, tuple[str, ...]]:
    capability_id = supply.capability_id
    content = supply.content
    issues: tuple[str, ...] = ()
    normalized: Any = None
    if capability_id == "roles.functional":
        normalized, issues = _normalize_role_supply(content)
    elif capability_id == "chart.lagna":
        if content in _SIGNS:
            normalized = content
        else:
            issues = ("unknown_sign",)
    elif capability_id == "planets.house_placement":
        if not isinstance(content, Mapping):
            issues = ("wrong_placement_mapping_type",)
        else:
            result: dict[str, int] = {}
            for raw_planet, house in content.items():
                planet_id = _canonical_planet(raw_planet)
                if planet_id is None or planet_id in result or type(house) is not int or not 1 <= house <= 12:
                    issues = ("malformed_placement_fact",)
                    break
                result[planet_id] = house
            if not issues:
                normalized = FrozenMapping(result)
    elif capability_id == "planets.normalized":
        if not isinstance(content, (list, tuple)):
            issues = ("wrong_planet_collection_type",)
        else:
            rows: list[PreparedPlanet] = []
            seen: set[str] = set()
            for item in content:
                if not isinstance(item, Mapping):
                    issues = ("malformed_planet",)
                    break
                planet_id = _canonical_planet(item.get("planet_id", item.get("name")))
                try:
                    row = PreparedPlanet(planet_id=planet_id or "", house=item.get("house"), sign=item.get("sign"))
                except (TypeError, ValueError):
                    issues = ("malformed_planet",)
                    break
                if planet_id in seen:
                    issues = ("duplicate_planet_id",)
                    break
                seen.add(planet_id)
                rows.append(row)
            if not issues:
                rows.sort(key=lambda row: CANONICAL_PLANETS.index(row.planet_id))
                normalized = tuple(FrozenMapping({"planet_id": row.planet_id, "house": row.house, "sign": row.sign}) for row in rows)
    elif capability_id == "aspects.basic_conjunction_list":
        if not isinstance(content, (list, tuple)):
            issues = ("wrong_representation_type",)
        elif any(not isinstance(edge, Mapping) or any(not isinstance(edge.get(key), str) for key in ("from", "to", "type")) for edge in content):
            issues = ("malformed_edge",)
        else:
            normalized = freeze_canonical(content, path="$.supplies.aspects.basic_conjunction_list.content")
    elif capability_id == "aspects.whole_sign_graph":
        if not isinstance(content, Mapping) or not isinstance(content.get("edges"), (list, tuple)):
            issues = ("wrong_representation_type",)
        elif any(not isinstance(edge, Mapping) or not isinstance(edge.get("source"), str) or (edge.get("target") is not None and not isinstance(edge.get("target"), str)) for edge in content["edges"]):
            issues = ("malformed_edge",)
        else:
            try:
                normalized = _graph_projection(content)
            except ValueError:
                issues = ("malformed_graph_projection",)
    elif capability_id == "dignity.exaltation_facts":
        records = []
        if isinstance(content, Mapping):
            content = tuple({"planet_id": key, "source_kind": supply.source_kind, "value": value} for key, value in content.items())
        if not isinstance(content, (list, tuple)):
            issues = ("wrong_exaltation_content_type",)
        else:
            for item in content:
                if not isinstance(item, Mapping):
                    issues = ("malformed_exaltation_fact",)
                    break
                planet_id = _canonical_planet(item.get("planet_id"))
                source_kind = item.get("source_kind")
                value = item.get("value", _MISSING)
                if planet_id is None or not isinstance(source_kind, str) or not _SAFE_CODE.fullmatch(source_kind) or value is _MISSING or isinstance(value, bool) is False and not isinstance(value, (int, float)) or isinstance(value, float) and not math.isfinite(value):
                    issues = ("malformed_exaltation_fact",)
                    break
                records.append({"planet_id": planet_id, "source_kind": source_kind, "value": value})
            if not issues:
                records.sort(key=lambda item: (CANONICAL_PLANETS.index(item["planet_id"]), item["source_kind"]))
                normalized = tuple(FrozenMapping(item) for item in records)
    else:
        issues = ("unsupported_supply_projection",)

    if issues:
        return None, False, issues
    empty = len(normalized) == 0 if not isinstance(normalized, str) else normalized == ""
    if capability_id == "aspects.whole_sign_graph":
        empty = len(normalized["edges"]) == 0
    if empty and empty_policy is EmptyPolicy.EMPTY_NOT_READY:
        return None, True, ("empty_not_ready",)
    return normalized, empty, ()


def _capability_from_supply(supply: CapabilitySupply) -> PreparedCapability:
    definition = _CAPABILITY_CATALOG.lookup(supply.capability_id)
    if isinstance(definition, CapabilityCatalogMiss):
        raise LookupError("unknown_capability_supply")
    if supply.capability_version != definition.capability_version:
        return PreparedCapability(
            capability_id=supply.capability_id,
            capability_version=definition.capability_version,
            observed_version=supply.capability_version,
            readiness=CapabilityReadiness.VERSION_MISMATCH,
            source_kind=supply.source_kind,
            content_empty=False,
            content=None,
            issues=("supplied_version_mismatch",),
        )
    content, empty, issues = _normalize_supply_content(supply, definition.empty_policy)
    if issues:
        return PreparedCapability(
            capability_id=supply.capability_id,
            capability_version=definition.capability_version,
            observed_version=definition.capability_version,
            readiness=CapabilityReadiness.MALFORMED,
            source_kind=supply.source_kind,
            content_empty=empty,
            content=None,
            issues=issues,
        )
    return PreparedCapability(
        capability_id=supply.capability_id,
        capability_version=definition.capability_version,
        observed_version=definition.capability_version,
        readiness=CapabilityReadiness.READY_EMPTY if empty else CapabilityReadiness.READY,
        source_kind=supply.source_kind,
        content_empty=empty,
        content=content,
        issues=(),
    )


def _copy_supplies(value: Any) -> tuple[CapabilitySupply, ...]:
    if value is None:
        return ()
    if isinstance(value, Mapping):
        supplies = tuple(value[key] for key in sorted(value))
        if any(not isinstance(item, CapabilitySupply) for item in supplies):
            raise TypeError("invalid_capability_supply")
        if any(key != item.capability_id for key, item in zip(sorted(value), supplies)):
            raise ValueError("supply_key_mismatch")
    elif isinstance(value, (list, tuple)):
        supplies = tuple(value)
        if any(not isinstance(item, CapabilitySupply) for item in supplies):
            raise TypeError("invalid_capability_supply")
    else:
        raise TypeError("invalid_capability_supplies")
    identities = tuple(item.capability_id for item in supplies)
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate_capability_supply")
    return tuple(sorted(supplies, key=lambda item: item.capability_id))


def prepare_predicate_state(
    astro: Any,
    *,
    capability_supplies: Any = None,
    versions: PreparedStateVersions | None = None,
) -> PreparationOutcome:
    """Read and defensively snapshot compatibility facts without executing producers."""

    required_attributes = ("planets", "lagna_sign", "enrichments", "derived", "metadata")
    if astro is None or any(_attribute(astro, name) is _MISSING for name in required_attributes):
        return _fatal("invalid_preparation_input", "$")
    if versions is None:
        versions = PreparedStateVersions()
    elif not isinstance(versions, PreparedStateVersions):
        return _fatal("invalid_preparation_versions", "$.versions")
    try:
        supplies = _copy_supplies(capability_supplies)
    except (TypeError, ValueError) as exc:
        code = str(exc) if _SAFE_CODE.fullmatch(str(exc)) else "invalid_capability_supplies"
        return _fatal(code, "$.capability_supplies")

    catalog = _CAPABILITY_CATALOG
    for supply in supplies:
        if isinstance(catalog.lookup(supply.capability_id), CapabilityCatalogMiss):
            return _fatal("unknown_capability_supply", "$.capability_supplies", supply.capability_id)

    planet_requirement = _requirement("planets.normalized", catalog.lookup("planets.normalized").capability_version)
    planet_inspection = inspect_capability(astro, planet_requirement, catalog)
    if "duplicate_planet_id" in planet_inspection.issues:
        return _fatal("duplicate_planet_id", "$.planets", "planets.normalized")
    try:
        planets = _prepared_planets(astro, planet_inspection)
        capabilities: dict[str, PreparedCapability] = {}
        for definition in catalog.definitions():
            inspection = inspect_capability(astro, _requirement(definition.capability_id, definition.capability_version), catalog)
            capabilities[definition.capability_id] = _capability_from_inspection(
                astro, definition.capability_id, inspection, planets
            )
        for supply in supplies:
            existing = capabilities[supply.capability_id]
            if existing.readiness is not CapabilityReadiness.MISSING:
                capabilities[supply.capability_id] = PreparedCapability(
                    capability_id=existing.capability_id,
                    capability_version=existing.capability_version,
                    observed_version=existing.observed_version,
                    readiness=CapabilityReadiness.MALFORMED,
                    source_kind=existing.source_kind,
                    content_empty=existing.content_empty,
                    content=None,
                    issues=("conflicting_supply",),
                )
            else:
                capabilities[supply.capability_id] = _capability_from_supply(supply)
        lagna_capability = capabilities["chart.lagna"]
        lagna_sign = lagna_capability.content if lagna_capability.readiness is CapabilityReadiness.READY else None
        state = PreparedAstroState(
            schema_version=versions.schema_version,
            producer_version=versions.producer_version,
            normalization_version=versions.normalization_version,
            system_scope=SYSTEM_SCOPE,
            lagna_sign=lagna_sign,
            planets=planets,
            capabilities=capabilities,
        )
    except CanonicalValueError:
        return _fatal("unsafe_canonical_content", "$.capabilities")
    except (LookupError, TypeError, ValueError):
        return _fatal("invalid_preparation_contract", "$")
    return PreparationOutcome(succeeded=True, state=state, issues=())


def inspect_prepared_capability(state: PreparedAstroState, requirement: CapabilityRequirement) -> CapabilityInspection:
    if not isinstance(state, PreparedAstroState):
        raise TypeError("state must be PreparedAstroState")
    if not isinstance(requirement, CapabilityRequirement):
        raise TypeError("requirement must be CapabilityRequirement")
    capability = state.capabilities._lookup.get(requirement.capability_id)
    if capability is None:
        return CapabilityInspection(
            capability_id=requirement.capability_id,
            expected_version=requirement.capability_version,
            observed_version=None,
            readiness=CapabilityReadiness.UNSUPPORTED,
            source_kind=None,
            content_empty=False,
            issues=("manifest_miss",),
        )
    if requirement.capability_version != capability.capability_version:
        return CapabilityInspection(
            capability_id=capability.capability_id,
            expected_version=requirement.capability_version,
            observed_version=capability.capability_version,
            readiness=CapabilityReadiness.VERSION_MISMATCH,
            source_kind=capability.source_kind or "prepared_manifest",
            content_empty=capability.content_empty,
            issues=("contract_version_mismatch",),
        )
    return CapabilityInspection(
        capability_id=capability.capability_id,
        expected_version=requirement.capability_version,
        observed_version=capability.observed_version,
        readiness=capability.readiness,
        source_kind=capability.source_kind,
        content_empty=capability.content_empty,
        issues=capability.issues,
    )


def find_prepared_planet(state: PreparedAstroState, planet_id: Any) -> PreparedPlanet | None:
    canonical = _canonical_planet(planet_id)
    if canonical is None:
        return None
    capability = state.capabilities["planets.normalized"]
    if capability.readiness not in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
        return None
    return next((item for item in state.planets if item.planet_id == canonical), None)


def observe_prepared_planet(state: PreparedAstroState, planet_id: Any) -> CapabilityFactObservation:
    canonical = _canonical_planet(planet_id)
    if canonical is None:
        raise ValueError("planet_id must normalize to the canonical catalog")
    capability = state.capabilities["planets.normalized"]
    planet = next((item for item in state.planets if item.planet_id == canonical), _MISSING)
    value = prepared_planet_to_data(planet) if planet is not _MISSING else _MISSING
    return _observation(
        state,
        _requirement("planets.normalized", capability.capability_version),
        entity_kind="planet",
        entity_id=canonical,
        value=value,
    )


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


def _observation(
    state: PreparedAstroState,
    requirement: CapabilityRequirement,
    *,
    entity_kind: str | None,
    entity_id: str | None,
    value: Any = _MISSING,
) -> CapabilityFactObservation:
    inspection = inspect_prepared_capability(state, requirement)
    if inspection.readiness not in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
        return _unavailable_observation(inspection, entity_kind, entity_id)
    if value is _MISSING:
        return CapabilityFactObservation(
            capability_id=requirement.capability_id,
            capability_version=requirement.capability_version,
            state=CapabilityFactState.ABSENT_ENTITY,
            entity_kind=entity_kind,
            entity_id=entity_id,
            value_present=False,
            issues=("entity_absent",),
        )
    return CapabilityFactObservation(
        capability_id=requirement.capability_id,
        capability_version=requirement.capability_version,
        state=CapabilityFactState.PRESENT,
        entity_kind=entity_kind,
        entity_id=entity_id,
        value_present=True,
        value=value,
        issues=(),
    )


def observe_prepared_planet_house(state: PreparedAstroState, planet_id: Any) -> CapabilityFactObservation:
    canonical = _canonical_planet(planet_id)
    if canonical is None:
        raise ValueError("planet_id must normalize to the canonical catalog")
    capability = state.capabilities["planets.house_placement"]
    value = capability.content[canonical] if capability.content is not None and canonical in capability.content else _MISSING
    return _observation(state, _requirement("planets.house_placement", capability.capability_version), entity_kind="planet", entity_id=canonical, value=value)


def observe_prepared_lagna(state: PreparedAstroState) -> CapabilityFactObservation:
    capability = state.capabilities["chart.lagna"]
    value = capability.content if capability.content is not None else _MISSING
    return _observation(state, _requirement("chart.lagna", capability.capability_version), entity_kind=None, entity_id=None, value=value)


def retrieve_prepared_aspects(state: PreparedAstroState, requirement: CapabilityRequirement) -> CapabilityFactObservation:
    if requirement.capability_id not in ("aspects.basic_conjunction_list", "aspects.whole_sign_graph"):
        raise ValueError("requirement must identify an Aspect representation")
    capability = state.capabilities._lookup.get(requirement.capability_id)
    value = _MISSING if capability is None or capability.content is None else capability.content
    return _observation(state, requirement, entity_kind=None, entity_id=None, value=value)


def observe_prepared_functional_role(state: PreparedAstroState, planet_id: Any) -> CapabilityFactObservation:
    canonical = _canonical_planet(planet_id)
    if canonical is None:
        raise ValueError("planet_id must normalize to the canonical catalog")
    capability = state.capabilities["roles.functional"]
    value = capability.content[canonical] if capability.content is not None and canonical in capability.content else _MISSING
    return _observation(state, _requirement("roles.functional", capability.capability_version), entity_kind="planet", entity_id=canonical, value=value)


def observe_prepared_exaltation_fact(state: PreparedAstroState, planet_id: Any) -> CapabilityFactObservation:
    canonical = _canonical_planet(planet_id)
    if canonical is None:
        raise ValueError("planet_id must normalize to the canonical catalog")
    capability = state.capabilities["dignity.exaltation_facts"]
    records = _MISSING
    if capability.content is not None:
        selected = tuple(
            FrozenMapping({"source_kind": item["source_kind"], "value": item["value"]})
            for item in capability.content
            if item["planet_id"] == canonical
        )
        if selected:
            records = selected
    return _observation(state, _requirement("dignity.exaltation_facts", capability.capability_version), entity_kind="planet", entity_id=canonical, value=records)


def prepared_planet_to_data(value: PreparedPlanet) -> FrozenMapping:
    return FrozenMapping({"planet_id": value.planet_id, "house": value.house, "sign": value.sign})


def prepared_capability_to_data(value: PreparedCapability) -> FrozenMapping:
    return FrozenMapping({
        "capability_id": value.capability_id,
        "capability_version": value.capability_version,
        "observed_version": value.observed_version,
        "readiness": value.readiness,
        "source_kind": value.source_kind,
        "content_empty": value.content_empty,
        "content": value.content,
        "issues": value.issues,
    })


def state_canonical_projection(state: PreparedAstroState) -> FrozenMapping:
    if not isinstance(state, PreparedAstroState):
        raise TypeError("state must be PreparedAstroState")
    return FrozenMapping({
        "schema_version": state.schema_version,
        "producer_version": state.producer_version,
        "normalization_version": state.normalization_version,
        "system_scope": state.system_scope,
        "lagna_sign": state.lagna_sign,
        "planets": tuple(prepared_planet_to_data(item) for item in state.planets),
        "capabilities": {
            capability_id: prepared_capability_to_data(state.capabilities[capability_id])
            for capability_id in state.capabilities
        },
    })


def state_canonical_bytes(state: PreparedAstroState) -> bytes:
    return canonical_json_bytes(state_canonical_projection(state))


def state_sha256(state: PreparedAstroState) -> str:
    return hashlib.sha256(state_canonical_bytes(state)).hexdigest()


class EvaluationMode(str, Enum):
    DEFAULT = "default"


@dataclass(frozen=True, slots=True, kw_only=True)
class PredicateEvaluationContext:
    system_scope: str = SYSTEM_SCOPE
    evaluation_mode: EvaluationMode = EvaluationMode.DEFAULT
    selected_planets: tuple[str, ...] | None = None
    evaluation_instant: datetime | None = None

    def __post_init__(self) -> None:
        if self.system_scope != SYSTEM_SCOPE:
            raise ValueError("system_scope must be parasara")
        if not isinstance(self.evaluation_mode, EvaluationMode):
            raise TypeError("evaluation_mode must be EvaluationMode")
        if self.selected_planets is not None:
            if not isinstance(self.selected_planets, tuple):
                raise TypeError("selected_planets must be an immutable tuple or None")
            normalized = tuple(_canonical_planet(item) for item in self.selected_planets)
            if any(item is None for item in normalized):
                raise ValueError("selected planets must normalize to the canonical catalog")
            if len(set(normalized)) != len(normalized):
                raise ValueError("selected planets must be unique")
            ordered = tuple(item for item in CANONICAL_PLANETS if item in normalized)
            object.__setattr__(self, "selected_planets", ordered)
        if self.evaluation_instant is not None:
            if not isinstance(self.evaluation_instant, datetime):
                raise TypeError("evaluation_instant must be datetime or None")
            offset = self.evaluation_instant.utcoffset()
            if self.evaluation_instant.tzinfo is None or offset != timedelta(0):
                raise ValueError("evaluation_instant must be timezone-aware UTC")
            object.__setattr__(self, "evaluation_instant", self.evaluation_instant.astimezone(timezone.utc))


def _instant_text(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def context_canonical_projection(context: PredicateEvaluationContext) -> FrozenMapping:
    if not isinstance(context, PredicateEvaluationContext):
        raise TypeError("context must be PredicateEvaluationContext")
    return FrozenMapping({
        "system_scope": context.system_scope,
        "evaluation_mode": context.evaluation_mode,
        "selected_planets": context.selected_planets,
        "evaluation_instant": _instant_text(context.evaluation_instant),
    })


def context_canonical_bytes(context: PredicateEvaluationContext) -> bytes:
    return canonical_json_bytes(context_canonical_projection(context))


def context_sha256(context: PredicateEvaluationContext) -> str:
    return hashlib.sha256(context_canonical_bytes(context)).hexdigest()


# Descriptive public aliases keep state/context identity explicit at call sites.
prepared_state_to_data = state_canonical_projection
prepared_state_json_bytes = state_canonical_bytes
prepared_state_sha256 = state_sha256
predicate_evaluation_context_to_data = context_canonical_projection
predicate_evaluation_context_json_bytes = context_canonical_bytes
predicate_evaluation_context_sha256 = context_sha256


__all__ = (
    "NORMALIZATION_COMPATIBILITY_VERSION", "PREPARATION_CONTRACT_VERSION",
    "PREPARED_STATE_SCHEMA_VERSION", "SYSTEM_SCOPE", "CapabilitySupply", "EvaluationMode",
    "PredicateEvaluationContext", "PreparationIssue", "PreparationOutcome", "PreparedAstroState",
    "PreparedCapability", "PreparedCapabilityMapping", "PreparedPlanet", "PreparedStateVersions",
    "context_canonical_bytes", "context_canonical_projection", "context_sha256",
    "find_prepared_planet", "inspect_prepared_capability", "observe_prepared_exaltation_fact",
    "observe_prepared_functional_role", "observe_prepared_lagna", "observe_prepared_planet",
    "observe_prepared_planet_house",
    "prepare_predicate_state", "prepared_capability_to_data", "prepared_planet_to_data",
    "prepared_state_json_bytes", "prepared_state_sha256", "prepared_state_to_data",
    "predicate_evaluation_context_json_bytes", "predicate_evaluation_context_sha256",
    "predicate_evaluation_context_to_data", "retrieve_prepared_aspects", "state_canonical_bytes",
    "state_canonical_projection", "state_sha256",
)
