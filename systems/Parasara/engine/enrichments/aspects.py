import os
from typing import Dict, Any, List
import yaml
from systems.Parasara.engine.astrostate import AstroState

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']


def _load_aspect_table() -> Dict[str, Any]:
    path = os.path.join('rules', 'parashara', 'aspects.yaml')
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        return {}


def _sign_index(name: str) -> int:
    if name in SIGNS:
        return SIGNS.index(name)
    return -1


def compute_aspect_graph(astro: AstroState) -> Dict[str, Any]:
    """Compute a whole-sign AspectGraph from the given AstroState.

    Returns a dict with 'edges' list and 'by_planet' map. Each edge includes
    explainability trace and sign-level reasoning.
    """
    table = _load_aspect_table().get('planets', {})
    # default offsets
    default_offsets = table.get('default', {}).get('offsets', [7])

    # build quick access to planet positions
    planets = getattr(astro, 'planets', []) or []
    name_to_planet = {p.name: p for p in planets}

    # map sign -> list of planet names in that sign
    sign_map: Dict[str, List[str]] = {}
    for p in planets:
        if getattr(p, 'sign', None) is None:
            continue
        sign_map.setdefault(p.sign, []).append(p.name)

    edges: List[Dict[str, Any]] = []
    by_planet: Dict[str, List[Dict[str, Any]]] = {}

    for p in planets:
        if p.sign is None:
            continue
        pname = p.name
        src_idx = _sign_index(p.sign)
        offsets = table.get(pname, {}).get('offsets', default_offsets)
        if not offsets:
            offsets = default_offsets
        for off in offsets:
            # offsets are 1-based (7 means 7th sign counting inclusive)
            tgt_idx = (src_idx + (off - 1)) % 12
            tgt_sign = SIGNS[tgt_idx]
            reason = f"{pname} has configured offsets {offsets}; offset {off} -> {tgt_sign}"
            targets = sign_map.get(tgt_sign, [])
            trace = {
                'source_planet': pname,
                'source_sign': p.sign,
                'source_degree': getattr(p, 'degree', None),
                'offset': int(off),
                'target_sign': tgt_sign,
                'matched_planets': targets,
                'explanation': reason,
            }
            # produce edges for each matched planet
            if targets:
                for tname in targets:
                    edge = {
                        'source': pname,
                        'target': tname,
                        'aspect': f"{off}th",
                        'kind': 'whole-sign',
                        'trace': trace,
                    }
                    edges.append(edge)
                    by_planet.setdefault(pname, []).append(edge)
            else:
                # record non-matching trace as well
                edge = {
                    'source': pname,
                    'target': None,
                    'aspect': f"{off}th",
                    'kind': 'whole-sign',
                    'trace': trace,
                }
                edges.append(edge)
                by_planet.setdefault(pname, []).append(edge)

    graph = {'edges': edges, 'by_planet': by_planet, 'config_version': _load_aspect_table().get('version')}
    # attach into astro.enrichments for downstream consumers
    try:
        if getattr(astro, 'enrichments', None) is None:
            astro.enrichments = {}
        astro.enrichments['aspects'] = graph
    except Exception:
        pass

    return graph
from typing import List, Dict, Any
from systems.Parasara.engine.astrostate import AstroState


PARASARA_ASPECTS = {
    'Sun': [7],
    'Moon': [7],
    'Mars': [4, 7, 8],
    'Mercury': [7],
    'Jupiter': [5, 7, 9],
    'Venus': [7],
    'Saturn': [3, 7, 10],
}


def compute_parashara_aspects(astro) -> List[Dict[str, Any]]:
    """Return list of aspect edges: source planet -> target planet with type and evidence.

    Uses house numbers for simple whole-sign aspects: a planet in house H aspects houses (H+offset-1)%12+1
    """
    res = []
    # build map house->planets
    house_map = {}
    for p in getattr(astro, 'planets', []) or []:
        h = getattr(p, 'house', None)
        if not h:
            continue
        house_map.setdefault(h, []).append(p.name)

    for p in getattr(astro, 'planets', []) or []:
        src = p.name
        h = getattr(p, 'house', None)
        if not h:
            continue
        aspects = PARASARA_ASPECTS.get(src, [])
        # allow Rahu/Ketu configuration via astro.metadata.parashara.nodes
        if src in ('Rahu', 'Ketu'):
            node_cfg = {}
            try:
                node_cfg = getattr(astro, 'metadata', {}).get('parashara', {}).get('nodes', {}) or {}
            except Exception:
                node_cfg = {}
            # node_cfg can set 'aspects' list, else default to 7th-only
            aspects = node_cfg.get(src, aspects) if isinstance(node_cfg, dict) else aspects
        for off in aspects:
            target_house = ((h - 1 + (off - 1)) % 12) + 1
            targets = house_map.get(target_house, [])
            for t in targets:
                if t == src:
                    continue
                edge = {
                    'source': src,
                    'target': t,
                    'aspect_type': f'parashara_{off}th',
                    'offset': off,
                    'target_house': target_house,
                    'evidence': {'source_house': h, 'target_house': target_house}
                }
                res.append(edge)
    return res
def compute_basic_aspects(astro: AstroState, conjunction_orb: float = 1.0) -> List[Dict[str, Any]]:
    """Compute very small-scope aspects for M1: basic conjunctions.

    Strategy (M1): report a `conjunction` when two planets share the same sign
    or when their normalized degree difference is within `conjunction_orb` degrees.
    This is intentionally conservative; full Parāśara aspects are M2.
    """
    aspects: List[Dict[str, Any]] = []
    planets = [p for p in astro.planets if getattr(p, 'name', None)]
    for i, a in enumerate(planets):
        for b in planets[i+1:]:
            a_sign = getattr(a, 'sign', None)
            b_sign = getattr(b, 'sign', None)
            a_deg = getattr(a, 'degree', None)
            b_deg = getattr(b, 'degree', None)
            # same sign -> conjunction
            if a_sign and b_sign and a_sign == b_sign:
                aspects.append({'from': a.name, 'to': b.name, 'type': 'conjunction', 'reason': 'same_sign'})
                aspects.append({'from': b.name, 'to': a.name, 'type': 'conjunction', 'reason': 'same_sign'})
                continue
            # degree proximity
            try:
                if a_deg is not None and b_deg is not None:
                    diff = abs((a_deg % 360) - (b_deg % 360))
                    diff = min(diff, 360 - diff)
                    if diff <= conjunction_orb:
                        aspects.append({'from': a.name, 'to': b.name, 'type': 'conjunction', 'reason': f'degree_within_{conjunction_orb}'} )
                        aspects.append({'from': b.name, 'to': a.name, 'type': 'conjunction', 'reason': f'degree_within_{conjunction_orb}'} )
            except Exception:
                continue

    return aspects

