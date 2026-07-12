import json
from pathlib import Path
from systems.Parasara.tools.generate_snapshot import generate
from .json_compare import compare_json
from typing import Any, Dict, Optional


def compare_snapshots(input_chart: str, golden_snapshot: str, ignore_keys=None, float_tol: float = 1e-6) -> Dict[str, Any]:
    """Generate snapshot for `input_chart` and compare full JSON against `golden_snapshot`.

    Returns dict with keys: matched (bool), diff (dict) and details.
    """
    tmp_out = Path('tests/tmp_snapshot.json')
    try:
        out = generate(input_chart, str(tmp_out))
    except Exception as e:
        return {'matched': False, 'error': f'generate_failed: {e}'}

    with open(golden_snapshot, 'r', encoding='utf-8') as fh:
        golden = json.load(fh)

    # Determine whether golden is a domain snapshot (career-only) or full engine output
    target = out
    if isinstance(golden, dict) and 'indicators' in golden:
        # golden is career indicators snapshot — compare `out['domains']['career']` to golden
        target = out.get('domains', {}).get('career', {})
    elif isinstance(golden, dict) and 'domains' not in golden and 'indicators' not in golden:
        # golden might be a nested career snapshot under top-level keys; fall back to full compare
        target = out

    if ignore_keys is None:
        ignore_keys = ['meta', 'generated_at', 'engine', '_run_id']

    matched, diffs = compare_json(golden, target, ignore_keys=ignore_keys, float_tol=float_tol)
    return {'matched': matched, 'diff': diffs, 'details': {}}
