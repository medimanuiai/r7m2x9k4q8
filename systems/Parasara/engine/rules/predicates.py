from typing import Tuple, Dict, Any
from systems.Parasara.engine.astrostate import AstroState
from systems.Parasara.engine.enrichments import aspects as aspects_mod
from systems.Parasara.engine.enrichments.functional_roles import compute_functional_roles
from systems.Parasara.engine.rules.engine import register_predicate, PredicateResult


def _planet_by_name(astro: AstroState, name: str):
    return next((p for p in getattr(astro, 'planets', []) or [] if p.name == name), None)


@register_predicate('ASPECT')
@register_predicate('ASPECT_EXISTS')
def aspect_exists(params: Dict[str, Any], astro: AstroState, context: Dict[str, Any]) -> PredicateResult:
    # params: from_house, to_house (optional), from_planet, to_planet
    graph = getattr(astro, 'enrichments', {}).get('aspects', {}) or {}
    edges = graph.get('edges', []) if isinstance(graph, dict) else []
    matched = []
    for e in edges:
        try:
            src = e.get('source')
            tgt = e.get('target')
            src_p = _planet_by_name(astro, src)
            tgt_p = _planet_by_name(astro, tgt)
            ok = True
            if 'from_house' in params:
                ok = ok and (getattr(src_p, 'house', None) == params.get('from_house'))
            if 'to_house' in params:
                ok = ok and (getattr(tgt_p, 'house', None) == params.get('to_house'))
            if 'from_planet' in params:
                ok = ok and (src == params.get('from_planet'))
            if 'to_planet' in params:
                ok = ok and (tgt == params.get('to_planet'))
            if ok:
                matched.append(e)
        except Exception:
            continue
    return PredicateResult(
        matched=(len(matched) > 0),
        predicate_id='ASPECT_EXISTS',
        inputs=params or {},
        evidence={'matched_edges': matched} if matched else {},
        trace_steps=[],
        errors=[],
        cache_hit=False,
        evaluation_time_ms=None,
    )


@register_predicate('PLANET_IN_HOUSE')
def planet_in_house(params: Dict[str, Any], astro: AstroState, context: Dict[str, Any]) -> PredicateResult:
    name = params.get('planet')
    house = params.get('house')
    p = _planet_by_name(astro, name)
    ok = p is not None and getattr(p, 'house', None) == house
    evidence = {'planet': name, 'house': house} if ok else {}
    return PredicateResult(matched=ok, predicate_id='PLANET_IN_HOUSE', inputs=params or {}, evidence=evidence, trace_steps=[], errors=[], cache_hit=False, evaluation_time_ms=None)


@register_predicate('HOUSE_OCCUPANT')
def house_occupant(params: Dict[str, Any], astro: AstroState, context: Dict[str, Any]) -> PredicateResult:
    house = params.get('house')
    planet = params.get('planet')
    p = _planet_by_name(astro, planet)
    ok = p is not None and getattr(p, 'house', None) == house
    evidence = {'planet': planet, 'house': house} if ok else {}
    return PredicateResult(matched=ok, predicate_id='HOUSE_OCCUPANT', inputs=params or {}, evidence=evidence, trace_steps=[], errors=[], cache_hit=False, evaluation_time_ms=None)


@register_predicate('FUNCTIONAL_ROLE')
def functional_role(params: Dict[str, Any], astro: AstroState, context: Dict[str, Any]) -> PredicateResult:
    role_in = params.get('role_in', []) or []
    # optionally restrict by planets in context
    candidates = context.get('planets') or [p.name for p in getattr(astro, 'planets', []) or []]
    froles = compute_functional_roles(astro)
    matched = []
    for pn in candidates:
        prow = froles.get(pn, {})
        if prow and prow.get('functional_role') in role_in:
            matched.append(pn)
    evidence = {'matched_planets': matched} if matched else {}
    return PredicateResult(matched=(len(matched) > 0), predicate_id='FUNCTIONAL_ROLE', inputs=params or {}, evidence=evidence, trace_steps=[], errors=[], cache_hit=False, evaluation_time_ms=None)


@register_predicate('PLANET_EXALTED')
def planet_exalted(params: Dict[str, Any], astro: AstroState, context: Dict[str, Any]) -> PredicateResult:
    pname = params.get('planet')
    p = _planet_by_name(astro, pname)
    if not p:
        return PredicateResult(matched=False, predicate_id='PLANET_EXALTED', inputs=params or {}, evidence={}, trace_steps=[], errors=[], cache_hit=False, evaluation_time_ms=None)
    raw = getattr(p, '__dict__', {})
    flags = raw.get('flags') if isinstance(raw, dict) else None
    if isinstance(flags, dict) and flags.get('exalted'):
        return PredicateResult(matched=True, predicate_id='PLANET_EXALTED', inputs=params or {}, evidence={'planet': pname, 'exalted_flag': True}, trace_steps=[], errors=[], cache_hit=False, evaluation_time_ms=None)
    # check metadata exaltations mapping
    exmap = getattr(astro, 'metadata', {}).get('exaltations', {}) or {}
    exdeg = exmap.get(pname)
    evidence = {'planet': pname, 'exaltation_degree': exdeg} if exdeg is not None else {}
    return PredicateResult(matched=(exdeg is not None), predicate_id='PLANET_EXALTED', inputs=params or {}, evidence=evidence, trace_steps=[], errors=[], cache_hit=False, evaluation_time_ms=None)
