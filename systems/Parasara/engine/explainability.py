from typing import Dict, Any, List


def evidence_for_rule(rule_id: str, rule: Dict[str, Any], eval_result: Dict[str, Any], contribution: float) -> Dict[str, Any]:
    return {
        'rule_id': rule_id,
        'rule': rule,
        'match': bool(eval_result.get('match')),
        'evidence': eval_result.get('evidence'),
        'contribution': round(float(contribution), 3),
    }


def scoring_breakdown(base_score: float, contributions: List[float]) -> Dict[str, Any]:
    total_contrib = sum(contributions)
    final = min(1.0, float(base_score) + float(total_contrib))
    return {
        'base_score': round(float(base_score), 3),
        'total_contribution': round(float(total_contrib), 3),
        'final_score': round(float(final), 3),
        'formula': 'final = min(1.0, base_score + sum(contributions))'
    }
