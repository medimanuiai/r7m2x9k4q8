"""CI snapshot comparator.

Generates a snapshot from a fixture using the snapshot generator and compares
it against the approved snapshot. Exits non-zero on mismatch and prints a
readable diff to stdout.

Usage:
  python systems/Parasara/tools/ci_snapshot_check.py --fixture <fixture.json> --approved <approved_snapshot.json>
"""
import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from systems.Parasara.tools.generate_snapshot import generate


def normalize(obj: Any, float_precision: int = 3):
    """Recursively normalize JSON-like structure: sort keys for dicts and
    round floats to the given precision so tiny FP diffs don't break CI."""
    if isinstance(obj, dict):
        return {k: normalize(obj[k], float_precision) for k in sorted(obj.keys())}
    if isinstance(obj, list):
        return [normalize(v, float_precision) for v in obj]
    if isinstance(obj, float):
        if math.isfinite(obj):
            return round(obj, float_precision)
        return obj
    return obj


def compare_json(a: Any, b: Any) -> bool:
    return normalize(a) == normalize(b)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--fixture', required=True)
    p.add_argument('--approved', required=True)
    p.add_argument('--out', required=False, default=None, help='Optional path to write generated snapshot')
    args = p.parse_args()

    fixture = Path(args.fixture)
    approved = Path(args.approved)

    if not fixture.exists():
        print(f'Fixture not found: {fixture}', file=sys.stderr)
        sys.exit(2)
    if not approved.exists():
        print(f'Approved snapshot not found: {approved}', file=sys.stderr)
        sys.exit(2)

    generated = generate(str(fixture), args.out or str(Path('.').resolve() / 'tmp_generated_snapshot.json'))
    approved_obj = json.loads(approved.read_text())

    ok = compare_json(generated, approved_obj)
    if ok:
        print('Snapshots match')
        sys.exit(0)
    else:
        print('Snapshots differ — printing generated vs approved (normalized)')
        print('\n--- GENERATED ---')
        print(json.dumps(normalize(generated), indent=2, sort_keys=True))
        print('\n--- APPROVED ---')
        print(json.dumps(normalize(approved_obj), indent=2, sort_keys=True))
        sys.exit(3)


if __name__ == '__main__':
    main()
