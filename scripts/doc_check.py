#!/usr/bin/env python3
"""
Usage: python scripts/doc_check.py --base main

Checks changed files against system docs. Exits non-zero if a system
has code/test changes but no docs updates under its Documentation folder.
"""
from __future__ import annotations
import subprocess, sys, argparse, pathlib

def git_changed_files(base='main'):
    # ensure base fetched (best-effort)
    try:
        subprocess.run(['git', 'fetch', 'origin', base], check=False, stdout=subprocess.DEVNULL)
    except Exception:
        pass
    try:
        out = subprocess.check_output(['git', 'diff', '--name-only', f'origin/{base}...HEAD'], stderr=subprocess.STDOUT)
        return [p.decode().strip() for p in out.splitlines() if p.strip()]
    except subprocess.CalledProcessError as e:
        # Not a git repo or git command failed
        raise RuntimeError('git diff failed — not a git repository or git not available') from e

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base', default='main', help='Base branch to diff against')
    p.add_argument('--changed-files', help='Path to a newline-separated file with changed file paths (one per line). Use when not running in a git repo.')
    args = p.parse_args()
    if args.changed_files:
        cf = pathlib.Path(args.changed_files)
        if not cf.exists():
            print(f'Changed files list not found: {cf}', file=sys.stderr)
            return 3
        changed = [line.strip() for line in cf.read_text().splitlines() if line.strip()]
    else:
        try:
            changed = git_changed_files(args.base)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            print('Either run this inside a git repository, or provide --changed-files <path>', file=sys.stderr)
            return 1
    if not changed:
        print('No changed files found.')
        return 0

    systems_touched = {}
    for path in changed:
        parts = pathlib.Path(path).parts
        if len(parts) >= 2 and parts[0] in ('systems', 'tests'):
            system = parts[1]
            systems_touched.setdefault(system, []).append(path)

    errors = []
    for system, files in systems_touched.items():
        docs_prefixes = [
            f'systems/{system}/Documentation/',
            f'tests/{system}/Documentation/',
        ]
        has_doc_change = any(any(p.startswith(prefix) for prefix in docs_prefixes) for p in changed)
        if not has_doc_change:
            errors.append((system, files))

    if errors:
        print('Documentation check failed. The following systems were changed but no docs were updated:')
        for system, files in errors:
            print(f'- {system}: changed files:')
            for f in files[:20]:
                print(f'    {f}')
        print('\nPlease update the corresponding docs under:')
        print('  systems/<System>/Documentation/ or tests/<System>/Documentation/')
        return 2

    print('Documentation check passed.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
