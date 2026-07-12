from typing import Dict, Any, List, Tuple
from systems.Parasara.engine.astrostate import AstroState, PlanetState

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']


def _sign_index_from_longitude(lon: float) -> Tuple[int, str, float]:
    """Return (sign_index, sign_name, degree_within_sign) for a longitude in degrees."""
    lon = float(lon) % 360.0
    sign_idx = int(lon // 30) % 12
    deg_in_sign = lon - (sign_idx * 30)
    return sign_idx, SIGNS[sign_idx], deg_in_sign


def compute_navamsa_for_longitude(lon: float) -> Dict[str, Any]:
    """Compute Navamsa (D9) placement for a given absolute longitude.

    Algorithm:
    - navamsa_size = 30/9 = 3.333... degrees
    - nav_in_sign = floor(deg_in_sign / navamsa_size)  (0..8)
    - nav_sign_index = (sign_index*3 + nav_in_sign) % 12  (classical mapping)
    """
    sign_idx, sign_name, deg_in_sign = _sign_index_from_longitude(lon)
    nav_size = 30.0 / 9.0
    nav_in_sign = int(deg_in_sign // nav_size)
    # clamp
    if nav_in_sign < 0:
        nav_in_sign = 0
    if nav_in_sign > 8:
        nav_in_sign = 8

    nav_sign_index = (sign_idx * 3 + nav_in_sign) % 12
    nav_sign = SIGNS[nav_sign_index]
    # degree within the navamsa sign: distance from beginning of that navamsa slice
    start_of_nav_in_sign = nav_in_sign * nav_size
    deg_into_navamsa = deg_in_sign - start_of_nav_in_sign
    # normalize to 0..30 for the navamsa sign
    deg_in_nav_sign = (nav_sign_index * 30) + deg_into_navamsa

    return {
        'nav_sign': nav_sign,
        'nav_sign_index': int(nav_sign_index),
        'nav_in_sign': int(nav_in_sign),
        'degree_into_navamsa': round(float(deg_into_navamsa), 6),
        'degree_in_nav_sign': round(float(deg_in_nav_sign % 30.0), 6),
    }


def compute_d9(astro: AstroState) -> Dict[str, Any]:
    """Compute D9 placements for planets and lagna (if available) and return a mapping.

    Output mapping planet -> { navamsa: {...}, source_longitude: float }
    """
    out: Dict[str, Any] = {}
    # planets
    for p in getattr(astro, 'planets', []) or []:
        try:
            lon = None
            # if planet has canonical longitude field, use it; else try sign+degree
            if hasattr(p, 'degree') and getattr(p, 'degree', None) is not None and getattr(p, 'sign', None) is not None:
                # compute absolute longitude from sign and degree
                sign_idx = SIGNS.index(p.sign) if p.sign in SIGNS else None
                if sign_idx is not None:
                    lon = sign_idx * 30.0 + float(p.degree)
            if lon is None:
                # fallback: skip
                continue
            nav = compute_navamsa_for_longitude(lon)
            out[p.name] = {'navamsa': nav, 'source_longitude': round(float(lon % 360.0), 6)}
        except Exception:
            continue

    # lagna
    try:
        if getattr(astro, 'lagna_degree', None) is not None and getattr(astro, 'lagna_sign', None) is not None:
            # prefer lagna_degree if absolute provided
            ld = float(astro.lagna_degree)
            # if lagna_degree is relative to sign, add sign index
            if isinstance(astro.lagna_sign, str) and astro.lagna_sign in SIGNS:
                sign_idx = SIGNS.index(astro.lagna_sign)
                lon = sign_idx * 30.0 + ld
            else:
                lon = ld
            out['lagna'] = {'navamsa': compute_navamsa_for_longitude(lon), 'source_longitude': round(float(lon % 360.0), 6)}
    except Exception:
        pass

    return out


def _compute_division_for_longitude(lon: float, n: int) -> Dict[str, Any]:
    """Generic Dn computation: divide each sign into `n` equal parts and map to a sign index.

    This uses the widely-used mapping: div_sign_index = (sign_index * n + div_in_sign) % 12
    where div_in_sign = floor(deg_in_sign / (30/n)).
    Returns sign name, sign index, division index, degree into division, degree in target sign.
    """
    sign_idx, sign_name, deg_in_sign = _sign_index_from_longitude(lon)
    part_size = 30.0 / float(n)
    div_in_sign = int(deg_in_sign // part_size)
    if div_in_sign < 0:
        div_in_sign = 0
    if div_in_sign >= n:
        div_in_sign = n - 1
    target_index = (sign_idx * n + div_in_sign) % 12
    target_sign = SIGNS[target_index]
    start_of_div = div_in_sign * part_size
    deg_into_div = deg_in_sign - start_of_div
    deg_in_target_sign = (target_index * 30) + deg_into_div
    return {
        'n': n,
        'target_sign': target_sign,
        'target_sign_index': int(target_index),
        'div_in_sign': int(div_in_sign),
        'part_size': round(float(part_size), 8),
        'degree_into_division': round(float(deg_into_div), 6),
        'degree_in_target_sign': round(float(deg_in_target_sign % 30.0), 6),
    }


def compute_d3(astro: AstroState) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for p in getattr(astro, 'planets', []) or []:
        try:
            if getattr(p, 'degree', None) is None or getattr(p, 'sign', None) is None:
                continue
            sign_idx = SIGNS.index(p.sign)
            lon = sign_idx * 30.0 + float(p.degree)
            out[p.name] = {'d3': _compute_division_for_longitude(lon, 3), 'source_longitude': round(float(lon % 360.0), 6)}
        except Exception:
            continue
    # lagna
    try:
        if getattr(astro, 'lagna_degree', None) is not None and getattr(astro, 'lagna_sign', None) is not None:
            ld = float(astro.lagna_degree)
            sign_idx = SIGNS.index(astro.lagna_sign)
            lon = sign_idx * 30.0 + ld
            out['lagna'] = {'d3': _compute_division_for_longitude(lon, 3), 'source_longitude': round(float(lon % 360.0), 6)}
    except Exception:
        pass
    return out


def compute_d7(astro: AstroState) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for p in getattr(astro, 'planets', []) or []:
        try:
            if getattr(p, 'degree', None) is None or getattr(p, 'sign', None) is None:
                continue
            sign_idx = SIGNS.index(p.sign)
            lon = sign_idx * 30.0 + float(p.degree)
            out[p.name] = {'d7': _compute_division_for_longitude(lon, 7), 'source_longitude': round(float(lon % 360.0), 6)}
        except Exception:
            continue
    try:
        if getattr(astro, 'lagna_degree', None) is not None and getattr(astro, 'lagna_sign', None) is not None:
            ld = float(astro.lagna_degree)
            sign_idx = SIGNS.index(astro.lagna_sign)
            lon = sign_idx * 30.0 + ld
            out['lagna'] = {'d7': _compute_division_for_longitude(lon, 7), 'source_longitude': round(float(lon % 360.0), 6)}
    except Exception:
        pass
    return out


def compute_d30(astro: AstroState) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for p in getattr(astro, 'planets', []) or []:
        try:
            if getattr(p, 'degree', None) is None or getattr(p, 'sign', None) is None:
                continue
            sign_idx = SIGNS.index(p.sign)
            lon = sign_idx * 30.0 + float(p.degree)
            out[p.name] = {'d30': _compute_division_for_longitude(lon, 30), 'source_longitude': round(float(lon % 360.0), 6)}
        except Exception:
            continue
    try:
        if getattr(astro, 'lagna_degree', None) is not None and getattr(astro, 'lagna_sign', None) is not None:
            ld = float(astro.lagna_degree)
            sign_idx = SIGNS.index(astro.lagna_sign)
            lon = sign_idx * 30.0 + ld
            out['lagna'] = {'d30': _compute_division_for_longitude(lon, 30), 'source_longitude': round(float(lon % 360.0), 6)}
    except Exception:
        pass
    return out


def integrate_vargas_into_astro(astro: AstroState) -> AstroState:
    """Compute vargas (D3/D7/D9/D30) and attach results into `astro.enrichments['vargas']`.

    This function mutates the given AstroState enrichments map and also
    annotates individual PlanetState.vargas for convenient consumption.
    """
    if not isinstance(astro, AstroState):
        return astro

    vout: Dict[str, Any] = {}
    try:
        vout['D3'] = compute_d3(astro)
        vout['D7'] = compute_d7(astro)
        vout['D9'] = compute_d9(astro)
        vout['D30'] = compute_d30(astro)
    except Exception:
        # best-effort: return astro unchanged on error
        return astro

    # attach to astro.enrichments
    if getattr(astro, 'enrichments', None) is None:
        astro.enrichments = {}
    astro.enrichments['vargas'] = vout

    # annotate planets
    name_map = {p.name: p for p in getattr(astro, 'planets', []) or []}
    for vname, mapping in vout.items():
        for pname, info in mapping.items():
            if pname in name_map:
                ps = name_map[pname]
                if ps.vargas is None:
                    ps.vargas = {}
                ps.vargas[vname] = info

    return astro
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
