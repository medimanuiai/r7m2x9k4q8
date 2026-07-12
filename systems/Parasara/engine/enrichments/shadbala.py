import os
import yaml
from typing import Dict, Any, List
from systems.Parasara.engine.astrostate import AstroState, PlanetState


def _load_table(fname: str) -> Dict[str, Any]:
    base = os.path.join(os.getcwd(), 'rules', 'parashara', 'strength_tables')
    path = os.path.join(base, fname)
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as fh:
        return yaml.safe_load(fh) or {}


_EXALT = _load_table('exaltation.yaml').get('exaltations', {})
_DEB = _load_table('debilitation.yaml').get('debilitations', {})
_OWN = _load_table('ownership.yaml').get('ownership', {})
_MOOLA = _load_table('moolatrikona.yaml').get('moolatrikona', {})
_DIG = _load_table('dig_bala.yaml').get('dig_bala', {})
_NAIS = _load_table('naisargika_bala.yaml').get('naisargika', {})
_CFG = _load_table('shadbala_config.yaml')


def _deg_distance(a: float, b: float) -> float:
    return abs(((a - b + 180) % 360) - 180)


def compute_sthana_bala(planet: PlanetState, astro: AstroState) -> Dict[str, Any]:
    trace: List[Dict[str, Any]] = []
    name = planet.name
    cfg = _CFG.get('sthana', {})
    base = float(cfg.get('base', 6.0))

    # uccha proximity
    ex_deg = _EXALT.get(name)
    uccha_factor = 0.5
    evidence = []
    if isinstance(ex_deg, (int, float)) and getattr(planet, 'degree', None) is not None:
        dist = _deg_distance(planet.degree, float(ex_deg))
        uccha_factor = max(0.0, 1.0 - (dist / 30.0))
        evidence.append({'type': 'exaltation_distance', 'ex_deg': ex_deg, 'planet_deg': planet.degree, 'dist': dist})
    else:
        # fallback to flags
        flags = getattr(planet, '__dict__', {}).get('flags') or {}
        if flags.get('exalted'):
            uccha_factor = 1.0
            evidence.append({'type': 'flags', 'exalted': True})
    # own sign bonus
    own_bonus = 0.0
    sign = getattr(planet, 'sign', None)
    owned = _OWN.get(name) or []
    if sign in owned:
        own_bonus = float(cfg.get('own_sign_bonus', 1.0))
        evidence.append({'type': 'own_sign', 'sign': sign})

    # moolatrikona
    moola_bonus = 0.0
    msign = _MOOLA.get(name)
    if msign and sign == msign:
        moola_bonus = float(cfg.get('moolatrikona_bonus', 0.0))
        evidence.append({'type': 'moolatrikona', 'sign': sign})

    value = float(base + own_bonus + moola_bonus + (cfg.get('uccha_weight', 0.6) * uccha_factor))

    trace.append({'component': 'sthana_bala', 'value': round(value, 4), 'formula_used': 'base+own+moola+uccha_weight*uccha_factor', 'input_factors': {'base': base, 'own_bonus': own_bonus, 'moola_bonus': moola_bonus, 'uccha_factor': uccha_factor}, 'evidence': evidence})

    return {'value': round(value, 4), 'formula_used': 'sthana_formula_v1', 'input_factors': {'base': base}, 'evidence': trace}


def compute_dig_bala(planet: PlanetState, astro: AstroState) -> Dict[str, Any]:
    trace = []
    house = int(getattr(planet, 'house') or 0)
    val = float(_DIG.get(str(house)) or _DIG.get(house) or float(_CFG.get('dig_default', 10.0)))
    trace.append({'component': 'dig_bala', 'value': val, 'formula_used': 'lookup_house_value', 'input_factors': {'house': house}, 'evidence': []})
    return {'value': round(val, 4), 'formula_used': 'dig_lookup', 'input_factors': {'house': house}, 'evidence': trace}


def compute_naisargika_bala(planet: PlanetState, astro: AstroState) -> Dict[str, Any]:
    name = planet.name
    val = float(_NAIS.get(name, 0.5))
    trace = [{'component': 'naisargika_bala', 'value': val, 'formula_used': 'table_lookup', 'input_factors': {}, 'evidence': [{'source_table_version': _CFG.get('versioning', {}).get('table_version')}] }]
    return {'value': round(val, 4), 'formula_used': 'naisargika_lookup', 'input_factors': {}, 'evidence': trace}


def compute_drik_bala(planet: PlanetState, astro: AstroState) -> Dict[str, Any]:
    name = planet.name
    total = 0.0
    # Expect aspects to be stored as an AspectGraph under astro.enrichments['aspects']
    aspects_graph = getattr(astro, 'enrichments', {}).get('aspects', {}) or {}
    aspects = aspects_graph.get('edges', []) if isinstance(aspects_graph, dict) else []
    cfg = _CFG.get('drik', {})
    default_w = float(cfg.get('default_aspect_weight', 2.0))
    evidence = []
    for a in aspects:
        try:
            if a.get('source') == name:
                w = a.get('weight') if isinstance(a.get('weight'), (int, float)) else default_w
                total += float(w)
                # include aspect trace evidence if present
                evidence.append({'aspect_edge': a, 'weight_used': w, 'edge_trace': a.get('trace')})
        except Exception:
            continue
    trace = [{'component': 'drik_bala', 'value': total, 'formula_used': 'sum_aspect_weights', 'input_factors': {'aspect_count': len(evidence)}, 'evidence': evidence}]
    return {'value': round(total, 4), 'formula_used': 'drik_sum', 'input_factors': {'default_weight': default_w}, 'evidence': trace}


def compute_kala_bala(planet: PlanetState, astro: AstroState) -> Dict[str, Any]:
    cfg = _CFG.get('kala', {})
    is_day = getattr(astro, 'metadata', {}).get('is_day')
    val = float(cfg.get('day_bonus') if is_day else cfg.get('night_bonus'))
    trace = [{'component': 'kala_bala', 'value': val, 'formula_used': 'day_night_bonus', 'input_factors': {'is_day': is_day}, 'evidence': []}]
    return {'value': round(val, 4), 'formula_used': 'kala_daynight', 'input_factors': {'is_day': is_day}, 'evidence': trace}


def compute_cheshta_bala(planet: PlanetState, astro: AstroState) -> Dict[str, Any]:
    cfg = _CFG.get('cheshta', {})
    base = float(cfg.get('base', 10.0))
    raw = getattr(planet, '__dict__', {})
    motion = raw.get('motion') if isinstance(raw, dict) else None
    val = base
    evidence = []
    if isinstance(motion, dict):
        if motion.get('retrograde'):
            val += float(cfg.get('retro_bonus', 8.0))
            evidence.append({'retrograde': True})
        speed = motion.get('speed')
        if speed:
            maxs = getattr(astro, 'metadata', {}).get('max_speed', {}).get(planet.name, 1.0)
            norm = min(float(cfg.get('speed_scale', 10.0)), (float(speed) / max(float(maxs), 0.0001)) * float(cfg.get('speed_scale', 10.0)))
            val += norm
            evidence.append({'speed': speed, 'max_speed': maxs, 'norm_added': norm})
    trace = [{'component': 'cheshta_bala', 'value': val, 'formula_used': 'base+retro+speed_norm', 'input_factors': {'base': base}, 'evidence': evidence}]
    return {'value': round(val, 4), 'formula_used': 'cheshta_formula', 'input_factors': {'base': base}, 'evidence': trace}


def compute_shadbala_for_planet(planet: PlanetState, astro: AstroState) -> Dict[str, Any]:
    trace: List[Dict[str, Any]] = []
    sth = compute_sthana_bala(planet, astro)
    dig = compute_dig_bala(planet, astro)
    kala = compute_kala_bala(planet, astro)
    ches = compute_cheshta_bala(planet, astro)
    nais = compute_naisargika_bala(planet, astro)
    drik = compute_drik_bala(planet, astro)

    weights = _CFG.get('weights', {})
    total = (sth['value'] * float(weights.get('sthana', 1.0)) + dig['value'] * float(weights.get('dig', 0.6)) + kala['value'] * float(weights.get('kala', 0.5)) + ches['value'] * float(weights.get('cheshta', 0.4)) + nais['value'] * float(weights.get('naisargika', 0.8)) + drik['value'] * float(weights.get('drik', 0.3)))

    trace.extend(sth.get('evidence', []))
    trace.extend(dig.get('evidence', []))
    trace.extend(kala.get('evidence', []))
    trace.extend(ches.get('evidence', []))
    trace.extend(nais.get('evidence', []))
    trace.extend(drik.get('evidence', []))

    confidence = 0.0
    if trace:
        confidence = min(1.0, 0.2 + 0.15 * len(trace))

    return {
        'planet': planet.name,
        'sthana_bala': sth,
        'dig_bala': dig,
        'kala_bala': kala,
        'cheshta_bala': ches,
        'naisargika_bala': nais,
        'drik_bala': drik,
        'total_rupas': round(float(total), 4),
        'confidence': round(float(confidence), 3),
        'calculation_trace': trace,
    }


def compute_shadbala(astro: AstroState) -> Dict[str, Any]:
    res = {}
    for p in astro.planets:
        if not getattr(p, 'name', None):
            continue
        res[p.name] = compute_shadbala_for_planet(p, astro)
    return res
