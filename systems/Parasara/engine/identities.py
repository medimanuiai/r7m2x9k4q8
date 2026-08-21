"""Canonical Parāśara entity identities shared by factual APIs and rules."""

from __future__ import annotations


CANONICAL_PLANETS = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
)

_PLANET_BY_ASCII_CASE = {value.lower(): value for value in CANONICAL_PLANETS}
_PLANET_ALIASES = {"kethu": "Ketu"}


def normalize_planet_id(value: object) -> str:
    """Return one canonical planet identity or reject malformed input."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError("planet_id must be a non-empty string")
    normalized = value.strip().lower()
    found = _PLANET_ALIASES.get(normalized) or _PLANET_BY_ASCII_CASE.get(normalized)
    if found is None:
        raise ValueError("planet_id is not in the canonical planet catalog")
    return found


__all__ = ("CANONICAL_PLANETS", "normalize_planet_id")
