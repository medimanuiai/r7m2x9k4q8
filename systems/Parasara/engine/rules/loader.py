import os
import yaml
from typing import Dict, Any

RULE_REGISTRY: Dict[str, Dict[str, Any]] = {}


def load_rules_from_dir(rules_dir: str) -> Dict[str, Dict[str, Any]]:
    """Load YAML rule files from a directory tree into RULE_REGISTRY.

    This function is lightweight and intended for M1: it loads declarative
    rule metadata (id, type, base_score, priority, etc.) into memory.
    """
    global RULE_REGISTRY
    RULE_REGISTRY = {}
    if not os.path.exists(rules_dir):
        return RULE_REGISTRY

    for root, dirs, files in os.walk(rules_dir):
        for f in files:
            if not f.endswith(('.yml', '.yaml')):
                continue
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    docs = yaml.safe_load(fh)
                    if isinstance(docs, list):
                        for r in docs:
                            rid = r.get('id')
                            if rid:
                                r['_source_file'] = path
                                RULE_REGISTRY[rid] = r
            except Exception:
                # ignore parse errors for now; loader is best-effort in M1
                continue
    return RULE_REGISTRY


def get_rule(rule_id: str) -> Dict[str, Any]:
    return RULE_REGISTRY.get(rule_id)


def register_rule(rule: Dict[str, Any]):
    rid = rule.get('id')
    if rid:
        RULE_REGISTRY[rid] = rule
