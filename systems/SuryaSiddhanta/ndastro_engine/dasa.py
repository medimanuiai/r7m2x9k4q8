"""Dasa calculation module.

This module provides a core, library-first implementation for multi-level dasa
calculations using sidereal Moon longitude at birth.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Literal, TypeAlias

from ndastro_engine import config as _engine_config
from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from ndastro_engine.constants import DEGREE_PER_NAKSHATRA
from ndastro_engine.core import get_planet_position, ts
from ndastro_engine.enums import Nakshatras, Planets
from ndastro_engine.utils import normalize_degree

if TYPE_CHECKING:
    from collections.abc import Callable

DasaType: TypeAlias = Literal["vimshottari"]

_LEVEL_NAMES = {1: "maha", 2: "antara", 3: "pratyantara", 4: "sookshma"}
_MAX_DASA_LEVEL = 4


@dataclass(frozen=True)
class DasaBirthInfo:
    """Birth information needed for dasa calculations."""

    sidereal_moon_longitude: float
    janma_nakshatra: Nakshatras
    nakshatra_progress_fraction: float
    nakshatra_remaining_fraction: float
    start_lord: str


@dataclass(frozen=True)
class DasaContext:
    """Shared birth context for dasa calculations."""

    birth_datetime: datetime
    lat: float
    lon: float
    ayanamsa_system: AyanamsaSystem = "lahiri"
    dasa_type: str = "vimshottari"  # accepts DasaType or any custom registered name


@dataclass(frozen=True)
class DasaPeriod:
    """A single dasa period with optional nested children."""

    dasa_type: str
    level: int
    level_name: str
    lord: str
    start_utc: datetime
    end_utc: datetime
    children: tuple[DasaPeriod, ...] = ()


@dataclass(frozen=True)
class RunningDasa:
    """Running dasa period at each level."""

    maha: DasaPeriod | None
    antara: DasaPeriod | None
    pratyantara: DasaPeriod | None
    sookshma: DasaPeriod | None


@dataclass(frozen=True)
class DasaQuery:
    """Timeline generation and lookup options."""

    levels: int = 4
    years: float | None = None


@dataclass(frozen=True)
class _PeriodBuildContext:
    """Internal context for nested period construction."""

    dasa_type: str
    levels: int
    definition: DasaDefinition


@dataclass(frozen=True)
class DasaDefinition:
    """Public definition for a dasa system.

    Use with register_dasa_type() to add custom dasa systems.
    """

    lords: tuple[str, ...]
    years_by_lord: dict[str, float]
    cycle_years: float
    start_lord_resolver: Callable[[Nakshatras], str]


_VIMSHOTTARI_LORDS = (
    Planets.KETHU.name,
    Planets.VENUS.name,
    Planets.SUN.name,
    Planets.MOON.name,
    Planets.MARS.name,
    Planets.RAHU.name,
    Planets.JUPITER.name,
    Planets.SATURN.name,
    Planets.MERCURY.name,
)

_VIMSHOTTARI_YEARS = {
    Planets.KETHU.name: 7.0,
    Planets.VENUS.name: 20.0,
    Planets.SUN.name: 6.0,
    Planets.MOON.name: 10.0,
    Planets.MARS.name: 7.0,
    Planets.RAHU.name: 18.0,
    Planets.JUPITER.name: 16.0,
    Planets.SATURN.name: 19.0,
    Planets.MERCURY.name: 17.0,
}


def _vimshottari_start_lord(nakshatra: Nakshatras) -> str:
    return nakshatra.owner.name


_DASA_DEFINITIONS: dict[str, DasaDefinition] = {
    "vimshottari": DasaDefinition(
        lords=_VIMSHOTTARI_LORDS,
        years_by_lord=_VIMSHOTTARI_YEARS,
        cycle_years=120.0,
        start_lord_resolver=_vimshottari_start_lord,
    ),
}

# Immutable snapshot of built-in names used to prevent overwriting them.
_BUILTIN_DASA_TYPES: frozenset[str] = frozenset(_DASA_DEFINITIONS)


def get_supported_dasa_types() -> tuple[str, ...]:
    """Return all registered dasa system names, including any custom ones."""
    return tuple(_DASA_DEFINITIONS.keys())


def register_dasa_type(name: str, definition: DasaDefinition) -> None:
    """Register a custom dasa type with the engine.

    Registered types become available as valid dasa_type values in all dasa
    calculation functions. Built-in types cannot be overwritten.

    Args:
        name (str): Unique identifier for the dasa type.
        definition (DasaDefinition): The dasa system definition.

    Raises:
        ValueError: If name is empty, contains leading/trailing whitespace,
            or conflicts with a built-in system name.

    """
    if not name or name != name.strip():
        msg = "name must be a non-empty string without leading/trailing whitespace"
        raise ValueError(msg)
    if name in _BUILTIN_DASA_TYPES:
        msg = f"Cannot overwrite built-in dasa type: {name!r}"
        raise ValueError(msg)
    _DASA_DEFINITIONS[name] = definition


def _apply_traditional_lahiri_shift(dt: datetime) -> datetime:
    """Advance *dt* by Delta-T to replicate the double-DeltaT application in traditional platforms.

    JHora, DrikPanchang, and AstroSage pre-convert UT to TT before calling
    ``swe.calc_ut()``, which then adds Delta-T a second time.  This advances the
    effective computation time by one Delta-T interval (≈ 69 s in 2025), shifting
    the Moon position forward by the same amount.

    Delta-T is taken from Skyfield's built-in IERS table (``t.tt - t.ut1``).
    """
    t = ts.utc(dt)
    return dt + timedelta(seconds=(t.tt - t.ut1) * 86400.0)


def _compute_traditional_lahiri_sidereal_moon(
    birth_utc: datetime,
    lat: float,
    lon: float,
) -> float:
    """Compute sidereal Moon for ``true_lahiri`` mode using only Skyfield.

    Replicates both systematic deviations present in traditional platforms:

    1. The Moon is computed at ``birth_utc + Delta-T`` (double-DT bug).
    2. The ayanamsa uses IAU-1940 Lahiri constants (``SIDM_LAHIRI_1940``) evaluated
       at the TT Julian Date of ``birth_utc`` via
       :func:`ndastro_engine.ayanamsa.get_ayanamsa` with ``"true_lahiri"``.

    ``get_ayanamsa(birth_utc, "true_lahiri")`` internally calls
    ``ts.utc(birth_utc).tt`` which is the TT Julian Date — equivalent to
    ``jd_ut + Delta-T`` used by Swiss Ephemeris internally, so both approaches
    produce numerically identical ayanamsa values.
    """
    effective_time = _apply_traditional_lahiri_shift(birth_utc)
    moon_trop = get_planet_position(Planets.MOON, lat, lon, effective_time).longitude
    ayan = get_ayanamsa(birth_utc, "true_lahiri")
    return normalize_degree(moon_trop - ayan)


def get_dasa_birth_info(context: DasaContext) -> DasaBirthInfo:
    """Compute Dasa-relevant birth info from sidereal Moon longitude."""
    _validate_inputs(levels=1, dasa_type=context.dasa_type)

    birth_utc = _as_utc_datetime(context.birth_datetime)
    if context.ayanamsa_system == "true_lahiri":
        # Use the JHora-compatible sidereal Moon (Skyfield + SE SIDM_LAHIRI_1940).
        sidereal_moon_longitude = _compute_traditional_lahiri_sidereal_moon(birth_utc, context.lat, context.lon)
    else:
        moon_pos = get_planet_position(Planets.MOON, context.lat, context.lon, birth_utc)
        ayanamsa = get_ayanamsa(birth_utc, context.ayanamsa_system)
        sidereal_moon_longitude = normalize_degree(moon_pos.longitude - ayanamsa)

    nakshatra_number = int(sidereal_moon_longitude // DEGREE_PER_NAKSHATRA) + 1
    janma_nakshatra = Nakshatras(nakshatra_number)
    progress_fraction = Nakshatras.planet_advancement(sidereal_moon_longitude) / DEGREE_PER_NAKSHATRA
    remaining_fraction = 1.0 - progress_fraction

    definition = _DASA_DEFINITIONS[context.dasa_type]
    start_lord = definition.start_lord_resolver(janma_nakshatra)

    return DasaBirthInfo(
        sidereal_moon_longitude=sidereal_moon_longitude,
        janma_nakshatra=janma_nakshatra,
        nakshatra_progress_fraction=progress_fraction,
        nakshatra_remaining_fraction=remaining_fraction,
        start_lord=start_lord,
    )


def get_dasa_timeline(context: DasaContext, query: DasaQuery | None = None) -> list[DasaPeriod]:
    """Generate dasa timeline from birth time with up to 4 levels.

    Levels:
    1 = Mahadasa
    2 = Antardasa
    3 = Pratyantardasa
    4 = Sookshmadasa
    """
    timeline_query = query or DasaQuery()
    _validate_inputs(levels=timeline_query.levels, dasa_type=context.dasa_type)

    birth_utc = _as_utc_datetime(context.birth_datetime)
    birth_info = get_dasa_birth_info(
        DasaContext(
            birth_datetime=birth_utc,
            lat=context.lat,
            lon=context.lon,
            ayanamsa_system=context.ayanamsa_system,
            dasa_type=context.dasa_type,
        )
    )

    definition = _DASA_DEFINITIONS[context.dasa_type]
    build_context = _PeriodBuildContext(dasa_type=context.dasa_type, levels=timeline_query.levels, definition=definition)
    first_lord = birth_info.start_lord
    first_full_years = definition.years_by_lord[first_lord]
    elapsed_first_years = birth_info.nakshatra_progress_fraction * first_full_years

    total_years = timeline_query.years if timeline_query.years is not None else (definition.cycle_years - elapsed_first_years)
    if total_years <= 0:
        msg = "years must be greater than 0"
        raise ValueError(msg)

    horizon_end = birth_utc + timedelta(days=total_years * _engine_config.settings.dasa_year_length)

    periods: list[DasaPeriod] = []
    sequence = _rotated_sequence(definition.lords, birth_info.start_lord)

    # First Mahadasa started before birth; show full period from its start.
    first_lord = sequence[0]
    first_full_years = definition.years_by_lord[first_lord]
    elapsed_days = birth_info.nakshatra_progress_fraction * first_full_years * _engine_config.settings.dasa_year_length
    remaining_days = birth_info.nakshatra_remaining_fraction * first_full_years * _engine_config.settings.dasa_year_length

    first_start = birth_utc - timedelta(days=elapsed_days)
    first_end = min(birth_utc + timedelta(days=remaining_days), horizon_end)

    if first_end > first_start:
        periods.append(_build_period(build_context, first_lord, first_start, first_end, level=1))
        current_start = first_end
    else:
        current_start = first_start

    seq_index = 1
    while current_start < horizon_end:
        lord = sequence[seq_index % len(sequence)]
        full_duration = timedelta(days=definition.years_by_lord[lord] * _engine_config.settings.dasa_year_length)
        end = min(current_start + full_duration, horizon_end)
        periods.append(_build_period(build_context, lord, current_start, end, level=1))
        current_start = end
        seq_index += 1

    return periods


def get_running_dasa(query_datetime: datetime, context: DasaContext, query: DasaQuery | None = None) -> RunningDasa:
    """Get currently running dasa at all four levels for a timestamp."""
    query_utc = _as_utc_datetime(query_datetime)
    timeline = get_dasa_timeline(
        context,
        DasaQuery(
            levels=_MAX_DASA_LEVEL,
            years=(query.years if query is not None else None),
        ),
    )

    maha = _find_period(query_utc, timeline)
    antara = _find_period(query_utc, maha.children if maha else ())
    pratyantara = _find_period(query_utc, antara.children if antara else ())
    sookshma = _find_period(query_utc, pratyantara.children if pratyantara else ())

    return RunningDasa(maha=maha, antara=antara, pratyantara=pratyantara, sookshma=sookshma)


def _build_period(
    context: _PeriodBuildContext,
    lord: str,
    start_utc: datetime,
    end_utc: datetime,
    level: int,
) -> DasaPeriod:
    children: tuple[DasaPeriod, ...] = ()
    if level < context.levels and end_utc > start_utc:
        children = _build_children(
            context=context,
            parent_lord=lord,
            parent_start=start_utc,
            parent_end=end_utc,
            next_level=level + 1,
        )

    return DasaPeriod(
        dasa_type=context.dasa_type,
        level=level,
        level_name=_LEVEL_NAMES[level],
        lord=lord,
        start_utc=start_utc,
        end_utc=end_utc,
        children=children,
    )


def _build_children(
    context: _PeriodBuildContext,
    parent_lord: str,
    parent_start: datetime,
    parent_end: datetime,
    next_level: int,
) -> tuple[DasaPeriod, ...]:
    child_lords = _rotated_sequence(context.definition.lords, parent_lord)
    parent_seconds = (parent_end - parent_start).total_seconds()

    children: list[DasaPeriod] = []
    cursor = parent_start

    for idx, child_lord in enumerate(child_lords):
        if idx == len(child_lords) - 1:
            child_end = parent_end
        else:
            fraction = context.definition.years_by_lord[child_lord] / context.definition.cycle_years
            duration = timedelta(seconds=parent_seconds * fraction)
            child_end = min(cursor + duration, parent_end)

        children.append(
            _build_period(
                context=context,
                lord=child_lord,
                start_utc=cursor,
                end_utc=child_end,
                level=next_level,
            )
        )
        cursor = child_end

    return tuple(children)


def _find_period(query_utc: datetime, periods: tuple[DasaPeriod, ...] | list[DasaPeriod]) -> DasaPeriod | None:
    for period in periods:
        if period.start_utc <= query_utc < period.end_utc:
            return period
    return None


def _rotated_sequence(sequence: tuple[str, ...], start_lord: str) -> tuple[str, ...]:
    start_index = sequence.index(start_lord)
    return sequence[start_index:] + sequence[:start_index]


def _as_utc_datetime(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _validate_inputs(levels: int, dasa_type: str) -> None:
    if dasa_type not in _DASA_DEFINITIONS:
        msg = f"Unsupported dasa_type: {dasa_type!r}. Registered types: {list(_DASA_DEFINITIONS)}"
        raise ValueError(msg)

    if levels < 1 or levels > _MAX_DASA_LEVEL:
        msg = f"levels must be between 1 and {_MAX_DASA_LEVEL}"
        raise ValueError(msg)


__all__ = [
    "DasaBirthInfo",
    "DasaContext",
    "DasaDefinition",
    "DasaPeriod",
    "DasaQuery",
    "DasaType",
    "RunningDasa",
    "get_dasa_birth_info",
    "get_dasa_timeline",
    "get_running_dasa",
    "get_supported_dasa_types",
    "register_dasa_type",
]
