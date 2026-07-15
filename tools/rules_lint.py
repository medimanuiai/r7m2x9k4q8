#!/usr/bin/env python3
"""Lint rule YAML files for required metadata fields.

Usage: python tools/rules_lint.py [rules_dir]
"""
import sys
from pathlib import Path
from typing import Iterable, List
import yaml

REQUIRED = ['id', 'name', 'author', 'created_date', 'source_reference', 'classical_reference', 'validation_status', 'sme_required', 'sme_approved']
YOGA_REQUIRED = ['id', 'name', 'version', 'category', 'conditions', 'weights', 'evidence_required', 'provenance', 'sme_approved', 'tests']


def normalize_rule_paths(paths: Iterable[Path]) -> List[Path]:
    """Resolve, de-duplicate, and deterministically order supported rule paths."""
    unique = {Path(path).resolve() for path in paths if Path(path).suffix.lower() in {'.yml', '.yaml'}}
    return sorted(unique, key=lambda path: str(path).casefold())


def discover_rule_files(base: Path) -> List[Path]:
    candidates = list(base.rglob('*.yml')) + list(base.rglob('*.yaml'))
    return normalize_rule_paths(candidates)


def lint_file(p: Path):
    try:
        doc = yaml.safe_load(p.read_text(encoding='utf-8'))
        if doc is None and p.suffix.lower() == '.yaml' and p.name != 'yogas.yaml':
            return True, 'ok'
        if not isinstance(doc, list):
            return False, f'unsupported_format: expected a list in {p}'
        docs = doc
    except Exception as e:
        return False, f'parse_error: {e}'
    if p.name == 'yogas.yaml':
        required = YOGA_REQUIRED
    elif p.suffix.lower() == '.yml':
        required = REQUIRED
    else:
        required = ['id']
    for d in docs:
        if not isinstance(d, dict):
            return False, f'unsupported_format: expected a mapping in {p}'
        for f in required:
            if f not in d:
                return False, f'missing_field:{f} in {p}'
    return True, 'ok'


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    base = Path(args[0]) if args else Path('systems/Parasara/rules')
    bad = []
    for p in discover_rule_files(base):
        print(f'Inspected rule file: {p}')
        ok, msg = lint_file(p)
        if not ok:
            bad.append((str(p), msg))
    if bad:
        print('Lint failures:')
        for b in bad:
            print(b[0], b[1])
        return 2
    print('All rule files passed lint')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
