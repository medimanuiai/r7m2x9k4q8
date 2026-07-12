#!/usr/bin/env python3
"""Lint rule YAML files for required metadata fields.

Usage: python tools/rules_lint.py [rules_dir]
"""
import sys
from pathlib import Path
import yaml

REQUIRED = ['id', 'name', 'author', 'created_date', 'source_reference', 'classical_reference', 'validation_status', 'sme_required', 'sme_approved']


def lint_file(p: Path):
    try:
        doc = yaml.safe_load(p.read_text())
        if isinstance(doc, list):
            docs = doc
        else:
            docs = [doc]
    except Exception as e:
        return False, f'parse_error: {e}'
    for d in docs:
        for f in REQUIRED:
            if f not in d:
                return False, f'missing_field:{f} in {p}'
    return True, 'ok'


def main():
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('systems/Parasara/rules')
    bad = []
    for p in base.rglob('*.yml'):
        ok, msg = lint_file(p)
        if not ok:
            bad.append((str(p), msg))
    if bad:
        print('Lint failures:')
        for b in bad:
            print(b[0], b[1])
        sys.exit(2)
    print('All rule files passed lint')


if __name__ == '__main__':
    main()
