from typing import Any, Dict
from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.rules import loader
from systems.Parasara.engine.models import RuleMatch
import os
import time
from tests.testing_framework.instrumentation import record_rule, record_predicate


def in_sign(planet: PlanetState, sign: str) -> bool:
    """Return True if the planet is in the given sign."""
    if planet.sign:
        res = (planet.sign or '').lower() == (sign or '').lower()
        try:
            record_predicate('in_sign', bool(res))
        except Exception:
            pass
        return res
    # fallback: compute rashi from normalized degree if available
    try:
        deg = planet.degree_norm if hasattr(planet, 'degree_norm') else planet.degree
        if deg is not None:
            signs = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
            idx = int((deg % 360) // 30)
            rname = signs[idx]
            res = (rname or '').lower() == (sign or '').lower()
            try:
                record_predicate('in_sign', bool(res))
            except Exception:
                pass
            return res
    except Exception:
        pass
    return False


def in_house(planet: PlanetState, house: int) -> bool:
    """Return True if the planet occupies the given house number."""
    res = planet.house == house
    try:
        record_predicate('in_house', bool(res))
    except Exception:
        pass
    return res


def lord_of_house(astro: AstroState, planet_name: str, house: int) -> bool:
    """Return True if the named planet is recorded as the lord of the house in AstroState.houses.

    AstroState.houses is expected to be a list of dicts with keys including 'number' and 'lord'.
    """
    res = False
    for h in astro.houses or []:
        if h.get('number') == house:
            res = (h.get('lord') or '').lower() == (planet_name or '').lower()
            break
    try:
        record_predicate('lord_of_house', bool(res))
    except Exception:
        pass
    return res


def is_exalted(planet: PlanetState, exalted_sign: str) -> bool:
    """Minimal exaltation check by sign match. Real exaltation uses degree-based rules.
    This function is intentionally simple for Phase-1.
    """
    res = in_sign(planet, exalted_sign)
    try:
        record_predicate('is_exalted', bool(res))
    except Exception:
        pass
    return res


def evaluate_rule(astro: AstroState, rule: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate a tiny rule dict against an AstroState and return match + evidence.

    Supported rule shapes (minimal):
    - {"type": "in_sign", "planet": "Mars", "sign": "Aries"}
    - {"type": "in_house", "planet": "Mars", "house": 1}
    - {"type": "lord_of_house", "planet": "Mars", "house": 1}
    - {"type": "is_exalted", "planet": "Sun", "sign": "Aries"}
    """
    planet_name = rule.get('planet')
    planet = next((p for p in astro.planets if p.name == planet_name), None)
    if planet is None:
        return {'match': False, 'evidence': {'reason': 'planet_not_found', 'planet': planet_name}}

    rtype = rule.get('type')
    if rtype == 'in_sign':
        sign = rule.get('sign')
        match = in_sign(planet, sign)
        return {'match': match, 'evidence': {'planet': planet.name, 'sign': planet.sign, 'expected_sign': sign}}
    if rtype == 'in_house':
        house = rule.get('house')
        match = in_house(planet, house)
        return {'match': match, 'evidence': {'planet': planet.name, 'house': planet.house, 'expected_house': house}}
    if rtype == 'lord_of_house':
        house = rule.get('house')
        match = lord_of_house(astro, planet_name, house)
        return {'match': match, 'evidence': {'planet': planet.name, 'house': house}}
    if rtype == 'is_exalted':
        sign = rule.get('sign')
        match = is_exalted(planet, sign)
        return {'match': match, 'evidence': {'planet': planet.name, 'sign': planet.sign, 'expected_exalted_sign': sign}}

    return {'match': False, 'evidence': {'reason': 'unsupported_rule_type', 'type': rtype}}


def evaluate_rule_with_score(astro: AstroState, rule: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate a rule and return a structured RuleMatch-like dict.

    Returned fields:
    - rule_id: generated id or rule['id']
    - matched: bool
    - score: float (0.0..1.0) representing rule contribution magnitude
    - evidence: same as evaluate_rule
    - context: original rule dict

    This function preserves `evaluate_rule` behavior but adds a simple scoring
    policy suitable for M1. The interpreter should consume these matches.
    """
    # ensure rule registry is populated (lazy load) so runtime sees any seeded rules
    try:
        if not loader.RULE_REGISTRY:
            # prefer repository-relative path from current working directory
            rules_path = os.path.join(os.getcwd(), 'systems', 'Parasara', 'rules', 'parashara', 'v1')
            if os.path.exists(rules_path):
                loader.load_rules_from_dir(rules_path)
    except Exception:
        pass

    rid = rule.get('id') or f"rule_{rule.get('type')}"
    # if rule references a registered rule id, expand it (keep provided overrides)
    reg = None
    try:
        reg = loader.get_rule(rid)
    except Exception:
        reg = None
    # If no rule with exact id, try to find a registered rule by type
    if not reg:
        rtype = rule.get('type')
        try:
            for rr in loader.RULE_REGISTRY.values():
                if rr.get('type') == rtype:
                    reg = rr
                    break
        except Exception:
            reg = None
    if reg:
        # merge registered rule metadata into runtime rule context
        merged = dict(reg)
        merged.update(rule)
        # If runtime called by type (no explicit id), keep the type as the context id
        # so tests that assert by-type merging observe the rule type as id.
        merged['id'] = rule.get('id') or rule.get('type') or reg.get('id')
        rule = merged
    # Implement direct evaluation for higher-level M1 rule types so that
    # interpreters receive meaningful RuleMatch results instead of falling
    # back to unsupported predicate evaluation.
    rtype = rule.get('type')
    evidence = {}
    matched = False
    score = 0.0

    try:
        if rtype in ('in_sign', 'in_house', 'lord_of_house', 'is_exalted'):
            base = evaluate_rule(astro, rule)
            matched = bool(base.get('match'))
            evidence = base.get('evidence')
            # small default score for primitive predicates
            score = 0.05 if matched else 0.0

        elif rtype in ('strong_in_10', 'strong_in_house'):
            planet_name = rule.get('planet')
            house = rule.get('house', 10 if rtype == 'strong_in_10' else rule.get('house'))
            p = next((x for x in astro.planets if x.name == planet_name), None)
            if p and getattr(p, 'house', None) == house:
                # read structured strength if available
                astr = astro.enrichments.get('planet_strengths', {})
                pinfo = astr.get(p.name) if isinstance(astr, dict) else None
                p_strength = None
                if isinstance(pinfo, dict):
                    p_strength = pinfo.get('strength')
                if p_strength is None:
                    p_strength = float(getattr(p, 'strength', 0.0) or 0.0)
                matched = (p_strength >= 0.75)
                evidence = {'planet': p.name, 'house': house, 'strength': p_strength}
                score = 0.2 if matched else 0.05

        elif rtype == 'lord_status':
            # Check whether specified lord (or 10th lord) is own_sign/exalted
            lord = rule.get('lord') or rule.get('planet')
            if not lord and rule.get('house'):
                # derive lord from astro.houses
                h = next((hh for hh in astro.houses or [] if hh.get('number') == rule.get('house')), None)
                lord = h.get('lord') if h else None
            if lord:
                lp = next((x for x in astro.planets if x.name == lord), None)
                if lp:
                    # check dignity via enrichments or planet field
                    astr = astro.enrichments.get('planet_strengths', {})
                    pinfo = astr.get(lp.name) if isinstance(astr, dict) else None
                    dignity = None
                    if isinstance(pinfo, dict):
                        dignity = pinfo.get('dignity')
                    dignity = dignity or getattr(lp, 'dignity', None)
                    matched = dignity in ('own_sign', 'exalted')
                    evidence = {'lord': lord, 'dignity': dignity}
                    score = 0.18 if matched else 0.05

        elif rtype == 'rajayoga_naive':
            benefic_names = {'Jupiter', 'Venus', 'Mercury', 'Moon'}
            occ1 = [p for p in astro.planets if p.house == 1 and p.name in benefic_names]
            occ10 = [p for p in astro.planets if p.house == 10 and p.name in benefic_names]
            matched = bool(occ1 and occ10)
            evidence = {'occ1': [p.name for p in occ1], 'occ10': [p.name for p in occ10]}
            score = 0.18 if matched else 0.0

        elif rtype == 'aspect_on_house' or rtype == 'afflict_house':
            # Example: Jupiter aspect on 10th — rule may include 'planet': 'Jupiter' and 'house': 10
            planet = rule.get('planet')
            house = rule.get('house')
            aspects = astro.enrichments.get('aspects', []) or []
            targets = [p.name for p in astro.planets if p.house == house]
            matched = any((a.get('from') == planet and a.get('to') in targets) for a in aspects)
            evidence = {'planet': planet, 'house': house, 'targets': targets}
            score = rule.get('base_score') or ( -0.08 if rtype == 'afflict_house' else 0.12 ) if matched else 0.0

        else:
            # fallback to base evaluator for unknown types
            base = evaluate_rule(astro, rule)
            matched = bool(base.get('match'))
            evidence = base.get('evidence')
            score = 0.05 if matched else 0.0
    except Exception:
        matched = False
        evidence = {'error': 'evaluation_failed'}
        score = 0.0

    # construct a RuleMatch object for consistent schema
    rm = RuleMatch(
        rule_id=rid,
        rule_version=rule.get('version'),
        rule_family=rule.get('family'),
        matched=bool(matched),
        priority=rule.get('priority'),
        context=rule,
        base_score=rule.get('base_score'),
        adjusted_score=round(float(score), 3),
        confidence=None,
        evidence=evidence,
        trace_id=rule.get('trace_id'),
        provenance={'source': rule.get('_source_file')} if rule.get('_source_file') else None,
        evaluation_time_ms=None,
    )
    # record rule execution for coverage
    try:
        record_rule(rm.rule_id or '')
    except Exception:
        pass
    # Pydantic V2: export model to dict using model_dump
    try:
        d = rm.model_dump()
    except Exception:
        # fallback for older Pydantic versions
        d = rm.dict()
    return d


# Try to auto-load the standard parashara v1 rule set on import (best-effort)
try:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    rules_path = os.path.join(repo_root, 'systems', 'Parasara', 'rules', 'parashara', 'v1')
    if os.path.exists(rules_path):
        loader.load_rules_from_dir(rules_path)
except Exception:
    pass
