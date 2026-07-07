import json
from typing import Dict
from tests.testing_framework.instrumentation import summary, reset
from systems.Parasara.engine.rules import loader


def run_rule_coverage_scan(astro, out_path: str = None) -> Dict:
    """Execute the rule set over the given astro by triggering runtime.evaluate_rule_with_score
    for each registered rule id so that instrumentation records hits.
    This is a synthetic harness to force rule execution for coverage purposes.
    """
    reset()
    # ensure rules loaded
    rules = loader.RULE_REGISTRY
    for rid, rule in rules.items():
        # call runtime.evaluate_rule_with_score lazily to trigger evaluation
        try:
            from systems.Parasara.engine.rules import runtime
            runtime.evaluate_rule_with_score(astro, {'id': rid, 'type': rule.get('type')})
        except Exception:
            continue
    rep = summary()
    if out_path:
        with open(out_path, 'w', encoding='utf-8') as fh:
            json.dump(rep, fh, indent=2)
    return rep
