"""Varga extraction utilities.

Provides deterministic mathematical varga mapping helpers for Dn charts.
Implements D9 (navamsa) and D60 mappings and basic typed summaries.
"""
from typing import Dict, List, Any
from pydantic import BaseModel


VARGA_DEGREES = {
    'D1': 1,
    'D3': 3,
    'D7': 7,
    'D9': 9,
    'D10': 10,
    'D12': 12,
    'D60': 60,
}


RASHI_NAMES = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]


class VargaPart(BaseModel):
    part_index: int
    varga_longitude: float
    rashi_index: int
    rashi_name: str


class VargaSummary(BaseModel):
    varga: str
    parts: List[VargaPart]


def _part_index(longitude: float, n: int) -> int:
    """Return the 0-based part index for an `n` varga at given longitude."""
    pos = (float(longitude) % 360.0) * n / 360.0
    return int(pos) % n


def _varga_rashi_index_from_part(part_index: int, n: int) -> int:
    """Map a varga part index (0..n-1) to a rashi index (0..11) deterministically."""
    return int((part_index * 12) / n) % 12


def varga_parts_for(longitude: float, varga: str) -> List[Dict[str, Any]]:
    """Return a list of varga part dicts for the given longitude and varga name.

    This produces deterministic, mathematical varga partitions and maps each
    partition to a rashi index+name. It is a mathematically consistent
    mapping useful for rule predicates and Phase-1 determinism.
    """
    n = VARGA_DEGREES.get(varga.upper(), 1)
    parts: List[Dict[str, Any]] = []
    try:
        base = float(longitude) % 360.0
    except Exception:
        return parts

    # compute the specific part the planet falls into
    part_idx = _part_index(base, n)
    # compute representative longitude for that part (middle of part)
    part_size = 360.0 / n
    varga_lon = round((part_idx + 0.5) * part_size + 0.0, 4) % 360.0
    rashi_idx = _varga_rashi_index_from_part(part_idx, n)
    parts.append({
        'part_index': part_idx,
        'varga_longitude': varga_lon,
        'rashi_index': rashi_idx,
        'rashi_name': RASHI_NAMES[rashi_idx]
    })
    return parts


def varga_summary_for_planet(planet_longitude: float) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    # D1 is the base (natal) longitude; other vargas return partition parts.
    out['D1'] = [round(float(planet_longitude) % 360.0, 4)]
    for v in ['D9', 'D60']:
        out[v] = varga_parts_for(planet_longitude, v)
    return out
