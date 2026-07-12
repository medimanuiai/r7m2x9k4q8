import json
from typing import Dict, Any
from tests.testing_framework.instrumentation import summary, reset
from systems.Parasara.engine.rules import loader


def run_rule_coverage_scan(astro: Any, out_path: str = None) -> Dict[str, Any]:
    """Execute the rule set over the given astro by triggering runtime.evaluate_rule_with_score
    for each registered rule id so that instrumentation records hits.
    This is a synthetic harness to force rule execution for coverage purposes.
    """
    reset()
    # ensure rules loaded from standard path
    rules_path = 'systems/Parasara/rules/parashara/v1'
    loader.load_rules_from_dir(rules_path)
    rules = loader.RULE_REGISTRY
    for rid, rule in list(rules.items()):
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
