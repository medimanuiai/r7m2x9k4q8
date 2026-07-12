from typing import Dict, Any, List
from systems.Parasara.engine.astrostate import AstroState
from systems.Parasara.engine.rules import runtime
from systems.Parasara.engine import explainability
from systems.Parasara.engine import confidence as confidence_mod


def interpret_career(astro: AstroState) -> Dict[str, Any]:
    """Minimal career interpreter for M1 vertical slice.

    Strategy (minimal):
    - Consider planets in kendras (1,4,7,10) and average their strengths as a proxy score.
    - Add simple rule checks (lord_of_house for house 10 if present) as indicators.
    """
    kendra = {1, 4, 7, 10}
    kendra_planets = [p for p in astro.planets if p.house in kendra]
    strengths = [p.strength or 0.0 for p in kendra_planets]
    if strengths:
        base_score = sum(strengths) / len(strengths)
    else:
        base_score = 0.5

    indicators: List[Dict[str, Any]] = []
    evidence_list: List[Dict[str, Any]] = []
    contributions: List[float] = []
    components: List[Dict[str, Any]] = []

    # Use rule runtime to generate structured matches (RuleMatch-like) and consume them.
    house_summaries = astro.enrichments.get('house_summaries', [])
    house10 = next((h for h in house_summaries if h.get('number') == 10), None)
    house10_lord = house10.get('lord') if house10 else None

    # Compose a set of candidate rules for M1. The runtime returns structured matches
    # and associated evidence; the interpreter converts match.score -> contribution.
    candidate_rules = []
    # strong planet in 10th (per-planet)
    for p in astro.planets:
        candidate_rules.append({'id': f'strong_in_10_{p.name}', 'type': 'strong_in_10', 'planet': p.name, 'house': 10})
    # 10th lord status
    if house10_lord:
        candidate_rules.append({'id': f'10th_lord_{house10_lord}', 'type': 'lord_status', 'lord': house10_lord})
    # naive rajayoga rule
    candidate_rules.append({'id': 'rajayoga_naive', 'type': 'rajayoga_naive'})

    # Evaluate candidate rules via runtime
    for r in candidate_rules:
        try:
            match = runtime.evaluate_rule_with_score(astro, r)
        except Exception:
            # fallback to the legacy simple evaluator
            raw = runtime.evaluate_rule(astro, r)
            match = {'rule_id': r.get('id'), 'matched': bool(raw.get('match')), 'adjusted_score': 0.05 if raw.get('match') else 0.0, 'evidence': raw.get('evidence'), 'context': r}

        matched = bool(match.get('matched'))
        # support both 'adjusted_score' (RuleMatch) and legacy 'score'
        contrib = float(match.get('adjusted_score') if match.get('adjusted_score') is not None else match.get('score', 0.0))

        if matched and contrib > 0:
            contributions.append(contrib)
            rule_id = match.get('rule_id') or r.get('id')
            indicators.append({'rule_id': rule_id, 'contribution': contrib, 'evidence': match.get('evidence'), 'context': match.get('context')})
            # adapt eval_result for explainability helper
            eval_result = {'match': matched, 'evidence': match.get('evidence')}
            evidence_list.append(explainability.evidence_for_rule(rule_id, match.get('context'), eval_result, contrib))

    # assemble typed components for explainability
    # Planet components: deviation from neutral baseline (0.5)
    for p in kendra_planets:
        weight = round(float((p.strength or 0.0) - 0.5), 3)
        components.append({'type': 'planet', 'planet': p.name, 'house': p.house, 'weight': weight})

    # House components: include 10th house summary as a house-level component
    if house10:
        occ = house10.get('occupants', [])
        # average occupant strength
        occ_strengths = []
        for name in occ:
            pl = next((x for x in astro.planets if x.name == name), None)
            if pl and getattr(pl, 'strength', None) is not None:
                occ_strengths.append(float(pl.strength))
        house_strength = round(sum(occ_strengths) / len(occ_strengths), 3) if occ_strengths else 0.0
        house_weight = round(float(house_strength - 0.5), 3) if occ_strengths else 0.0
        components.append({'type': 'house', 'house': 10, 'weight': house_weight, 'occupants': occ})

    # Rule components: include matched rule contributions as components
    for ind in indicators:
        # indicators already contain rule_id and contribution
        components.append({'type': 'rule', 'rule_id': ind.get('rule_id'), 'weight': round(float(ind.get('contribution') or 0.0), 3)})

    scoring = explainability.scoring_breakdown(base_score, contributions)
    final = scoring.get('final_score', base_score)

    # compute a heuristic confidence using rule matches and data completeness
    # total_rules evaluated ~= number of candidate rules we attempted
    total_rules = max(1, len(candidate_rules))
    confidence = confidence_mod.compute_confidence([{'matched': i.get('matched') if isinstance(i, dict) else i} for i in []], total_rules, astro)
    # Fallback: if we have indicator-derived evidence_list, use its length to adjust
    if evidence_list:
        # create a lightweight rule_matches list from evidence_list
        rm = []
        for e in evidence_list:
            rm.append({'matched': True, 'adjusted_score': e.get('contribution')})
        confidence = confidence_mod.compute_confidence(rm, total_rules, astro)

    summary_text = f"Career score {round(float(final),3)} (confidence {round(float(confidence),3)})"

    return {
        'summary': summary_text,
        'score': round(float(final), 3),
        'confidence': round(float(confidence), 3),
        'components': components,
        'indicators': indicators,
        'evidence': evidence_list,
        'scoring': scoring,
        'trace_id': 'career_001'
    }
