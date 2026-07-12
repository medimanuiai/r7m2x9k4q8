from typing import List, Dict, Any


def compute_data_completeness(astro) -> float:
    """Simple completeness metric (0..1) for M1.

    Checks presence of key fields (lagna, planets, houses, metadata.birth_datetime_utc).
    """
    score = 0.0
    checks = 0
    passed = 0

    checks += 1
    if getattr(astro, 'lagna_sign', None):
        passed += 1

    checks += 1
    if getattr(astro, 'planets', None) and len(astro.planets) >= 1:
        passed += 1

    checks += 1
    if getattr(astro, 'houses', None) and len(astro.houses) >= 1:
        passed += 1

    checks += 1
    md = getattr(astro, 'metadata', {}) or {}
    if md.get('birth_datetime_utc'):
        passed += 1

    if checks == 0:
        return 0.0
    return float(passed) / float(checks)


def compute_rule_coverage(rule_matches: List[Dict[str, Any]], total_rules_evaluated: int) -> float:
    if total_rules_evaluated <= 0:
        return 0.0
    matched = sum(1 for r in rule_matches if r.get('matched'))
    return min(1.0, float(matched) / float(total_rules_evaluated))


def compute_evidence_strength(rule_matches: List[Dict[str, Any]]) -> float:
    if not rule_matches:
        return 0.0
    scores = []
    for r in rule_matches:
        # prefer adjusted_score, then base_score
        s = r.get('adjusted_score') or r.get('base_score') or 0.0
        try:
            scores.append(float(s))
        except Exception:
            scores.append(0.0)
    if not scores:
        return 0.0
    # normalize to 0..1 assuming scores are already in that range for M1
    avg = sum(scores) / len(scores)
    return max(0.0, min(1.0, float(avg)))


def compute_confidence(rule_matches: List[Dict[str, Any]], total_rules: int, astro) -> float:
    """M1 heuristic confidence:
    confidence = 0.4 * ruleCoverage + 0.3 * evidenceStrength + 0.3 * dataCompleteness
    """
    rc = compute_rule_coverage(rule_matches, total_rules)
    es = compute_evidence_strength(rule_matches)
    dc = compute_data_completeness(astro)
    conf = 0.4 * rc + 0.3 * es + 0.3 * dc
    return max(0.0, min(1.0, conf))
