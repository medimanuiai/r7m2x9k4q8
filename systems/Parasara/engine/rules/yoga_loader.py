from pathlib import Path
import yaml
from typing import Dict, Any, List
from systems.Parasara.engine.rules.loader import register_rule


REQUIRED_FIELDS = ['id', 'name', 'version', 'category', 'conditions', 'weights', 'evidence_required', 'provenance', 'sme_approved', 'tests']
DEFAULT_LEGACY_YOGA_RULES = Path(__file__).resolve().parents[2] / 'rules' / 'parashara' / 'v1'


def _load_yaml(path: str) -> List[Dict[str, Any]]:
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            docs = yaml.safe_load(fh)
            if isinstance(docs, list):
                return docs
            return []
    except Exception:
        return []


def validate_yoga_rule(rule: Dict[str, Any]) -> None:
    missing = [f for f in REQUIRED_FIELDS if f not in rule]
    if missing:
        raise ValueError(f"Yoga rule {rule.get('id','<unknown>')} missing required fields: {missing}")


def load_yoga_rules(rules_path: str = None) -> List[Dict[str, Any]]:
    """Load and validate yoga rules from the parashara v1 path and register them.

    Returns list of validated rules.
    """
    # Literal compatibility inspection path; production selection belongs only
    # to RuleVersionResolver and never depends on the process working directory.
    base = Path(rules_path) if rules_path is not None else DEFAULT_LEGACY_YOGA_RULES
    path = base / 'yogas.yaml'
    rules = _load_yaml(str(path))
    validated: List[Dict[str, Any]] = []
    for r in rules:
        try:
            validate_yoga_rule(r)
            # Preserve the supported generic-loader/Yoga interoperability API.
            register_rule(r)
            validated.append(r)
        except Exception:
            # skip invalid rules (loader is best-effort)
            continue
    return validated


if __name__ == '__main__':
    loaded = load_yoga_rules()
    print(f"Loaded {len(loaded)} yoga rules")
