import json
from typing import Any, Dict, List, Tuple


def _remove_ignored(obj: Any, ignore_keys: List[str]) -> Any:
    if isinstance(obj, dict):
        # unused helper — removed
        return obj
    # fallback: reconstruct properly


def _clean(obj: Any, ignore_keys: List[str]) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ignore_keys:
                continue
            out[k] = _clean(v, ignore_keys)
        return out
    elif isinstance(obj, list):
        return [_clean(v, ignore_keys) for v in obj]
    else:
        return obj


def _float_close(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol


def compare_json(a: Any, b: Any, ignore_keys: List[str] = None, float_tol: float = 1e-6) -> Tuple[bool, Dict]:
    """Compare two JSON-serializable objects with options.

    - ignore_keys: list of keys to remove at any dict level (non-recursive key names).
    - float_tol: absolute tolerance for floating point comparisons.

    Returns (matched, diff_details).
    diff_details contains path->(left,right) for first differences.
    """
    if ignore_keys is None:
        ignore_keys = []

    ca = _clean(a, ignore_keys)
    cb = _clean(b, ignore_keys)

    diffs = {}

    def _cmp(x, y, path=''):
        if type(x) != type(y):
            diffs[path] = (x, y)
            return False
        if isinstance(x, dict):
            # compare keys
            xkeys = set(x.keys())
            ykeys = set(y.keys())
            for k in sorted(xkeys.union(ykeys)):
                if k not in x:
                    diffs[f"{path}/{k}"] = (None, y.get(k))
                    return False
                if k not in y:
                    diffs[f"{path}/{k}"] = (x.get(k), None)
                    return False
                if not _cmp(x[k], y[k], f"{path}/{k}"):
                    return False
            return True
        if isinstance(x, list):
            if len(x) != len(y):
                diffs[path] = (f'len={len(x)}', f'len={len(y)}')
                return False
            for i, (xi, yi) in enumerate(zip(x, y)):
                if not _cmp(xi, yi, f"{path}[{i}]"):
                    return False
            return True
        if isinstance(x, float):
            if not _float_close(x, y, float_tol):
                diffs[path] = (x, y)
                return False
            return True
        else:
            if x != y:
                diffs[path] = (x, y)
                return False
            return True

    matched = _cmp(ca, cb, '')
    return matched, diffs


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('Usage: json_compare.py expected.json actual.json')
        sys.exit(2)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        exp = json.load(f)
    with open(sys.argv[2], 'r', encoding='utf-8') as f:
        act = json.load(f)
    m, d = compare_json(exp, act, ignore_keys=['generated_at', 'meta', 'engine'])
    print('MATCH' if m else 'DIFF')
    if not m:
        print(d)
