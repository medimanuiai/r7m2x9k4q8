import uuid
from typing import Dict, Any, List, Tuple
from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.rules.loader import RULE_REGISTRY
from systems.Parasara.engine.rules.yoga_loader import load_yoga_rules
from systems.Parasara.engine.rules.engine import evaluate_condition, clear_cache
import systems.Parasara.engine.rules.predicates as _preds  # registers predicates
from systems.Parasara.engine.enrichments import aspects as aspects_mod
from systems.Parasara.engine.enrichments import varga as varga_mod
from systems.Parasara.engine.enrichments.functional_roles import compute_functional_roles
from systems.Parasara.engine.enrichments.planet_strengths import compute_planet_strengths


def _make_trace_id() -> str:
    return str(uuid.uuid4())


def _planet_by_name(astro: AstroState, name: str) -> PlanetState:
    return next((p for p in getattr(astro, 'planets', []) if p.name == name), None)


def _eval_aspect_condition(params: Dict[str, Any], astro: AstroState, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Return (matched, evidence) for ASPECT condition.

    params: from_house, to_house (optional)
    """
    edges = getattr(astro, 'enrichments', {}).get('aspects', {}) or {}
    edges = edges.get('edges', []) if isinstance(edges, dict) else []
    matched_edges = []
    matched_planets = []
    for e in edges:
        try:
            src = e.get('source')
            tgt = e.get('target')
            if not src or not tgt:
                continue
            src_p = _planet_by_name(astro, src)
            tgt_p = _planet_by_name(astro, tgt)
            if not src_p or not tgt_p:
                continue
            ok = True
            if 'from_house' in params:
                ok = ok and (getattr(src_p, 'house', None) == params.get('from_house'))
            if 'to_house' in params:
                ok = ok and (getattr(tgt_p, 'house', None) == params.get('to_house'))
            if ok:
                matched_edges.append(e)
                matched_planets.extend([src, tgt])
        except Exception:
            continue
    evidence = {'matched_edges': matched_edges, 'matched_planets': list(set(matched_planets))}
    return (len(matched_edges) > 0, evidence)


def _eval_functional_role_condition(params: Dict[str, Any], astro: AstroState, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    # ensure functional roles computed
    froles = compute_functional_roles(astro)
    role_in = params.get('role_in', []) or []
    # if context has candidate planets, restrict
    candidates = context.get('planets') or [p.name for p in getattr(astro, 'planets', [])]
    matched = []
    for pn in candidates:
        prow = froles.get(pn, {})
        if prow and prow.get('functional_role') in role_in:
            matched.append(pn)
    evidence = {'matched_planets': matched}
    return (len(matched) > 0, evidence)


def _eval_house_lords_combination(params: Dict[str, Any], astro: AstroState, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    # simplistic mutual check: lord of house A occupies house B and vice versa
    houses = params.get('houses', [])
    relation = params.get('relation')
    houses_data = getattr(astro, 'houses', []) or []
    # map house number -> lord
    house_lords = {h.get('number'): h.get('lord') for h in houses_data if isinstance(h, dict)}
    if len(houses) < 2:
        return (False, {'reason': 'need_at_least_two_houses'})
    a, b = houses[0], houses[1]
    lord_a = house_lords.get(a)
    lord_b = house_lords.get(b)
    if not lord_a or not lord_b:
        return (False, {'reason': 'missing_lords', 'lords': house_lords})
    # find occupancy: get house number of lord planets
    pa = _planet_by_name(astro, lord_a)
    pb = _planet_by_name(astro, lord_b)
    if relation == 'mutual':
        ok = (getattr(pa, 'house', None) == b) and (getattr(pb, 'house', None) == a)
        evidence = {'lord_a': lord_a, 'lord_b': lord_b, 'pa_house': getattr(pa, 'house', None), 'pb_house': getattr(pb, 'house', None)}
        return (ok, evidence)
    return (False, {'reason': 'unsupported_relation', 'relation': relation})


def _eval_house_occupant(params: Dict[str, Any], astro: AstroState, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    house = params.get('house')
    planet = params.get('planet')
    p = _planet_by_name(astro, planet)
    ok = p is not None and getattr(p, 'house', None) == house
    return (ok, {'planet': planet, 'house': house})


def _eval_condition(node: Dict[str, Any], astro: AstroState, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    t = node.get('type')
    if t in ('AND', 'OR'):
        children = node.get('children', []) or []
        results = []
        evidences = []
        for c in children:
            ok, ev = _eval_condition(c, astro, context)
            results.append(ok)
            evidences.append(ev)
        if t == 'AND':
            return (all(results), {'children': evidences})
        else:
            return (any(results), {'children': evidences})
    elif t == 'ASPECT':
        return _eval_aspect_condition(node.get('params', {}), astro, context)
    elif t == 'FUNCTIONAL_ROLE':
        return _eval_functional_role_condition(node.get('params', {}), astro, context)
    elif t == 'HOUSE_LORDS_COMBINATION':
        return _eval_house_lords_combination(node.get('params', {}), astro, context)
    elif t == 'HOUSE_OCCUPANT':
        return _eval_house_occupant(node.get('params', {}), astro, context)
    else:
        return (False, {'reason': 'unknown_condition_type', 'type': t})


def evaluate_yoga_rules(astro: AstroState) -> List[Dict[str, Any]]:
    # ensure rules loaded
    if not RULE_REGISTRY:
        load_yoga_rules()

    matches: List[Dict[str, Any]] = []
    # ensure vargas and aspects present
    try:
        varga_mod.integrate_vargas_into_astro(astro)
        aspects_mod.compute_aspect_graph(astro)
    except Exception:
        pass

    # compute functional roles for evidence
    try:
        compute_functional_roles(astro)
    except Exception:
        pass

    # clear predicate cache per evaluation run
    clear_cache()

    for rid, rule in RULE_REGISTRY.items():
        cond = rule.get('conditions')
        if not cond:
            continue
        pr = evaluate_condition(cond, astro, {})
        matched = pr.matched
        evidence = pr.evidence or {}
        # collect planets/houses/aspects from evidence
        planets = evidence.get('matched_planets') or []
        # if nested children, flatten
        if not planets and isinstance(evidence.get('children'), list):
            for ch in evidence.get('children'):
                if isinstance(ch, dict) and ch.get('matched_planets'):
                    planets.extend(ch.get('matched_planets'))

        aspects_used = []
        if isinstance(evidence.get('matched_edges'), list):
            aspects_used = evidence.get('matched_edges')

        ym = {
            'yoga_id': rid,
            'name': rule.get('name'),
            'matched': bool(matched),
            'planets': list(set(planets)),
            'houses': rule.get('conditions', {}).get('params', {}).get('houses') or [],
            'aspects_used': aspects_used,
            'evidence': evidence,
            'trace_id': _make_trace_id(),
        }
        matches.append(ym)

    try:
        if getattr(astro, 'enrichments', None) is None:
            astro.enrichments = {}
        astro.enrichments['yogas'] = matches
    except Exception:
        pass

    return matches
