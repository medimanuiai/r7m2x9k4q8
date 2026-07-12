#!/usr/bin/env python3
"""Watch `systems/` and `tests/` for changes and run the doc_check script automatically.

Usage: python scripts/watch_doc_check.py

This is a simple polling watcher (no extra deps). It writes a temp changed-files list
and invokes `python scripts/doc_check.py --changed-files <tmpfile>` when changes are detected.
"""
from __future__ import annotations
import time
from pathlib import Path
import subprocess
import sys
import tempfile

WATCH_PATHS = [Path('systems'), Path('tests')]
POLL_INTERVAL = 2.0  # seconds


def snapshot(paths: list[Path]) -> dict[str, float]:
    m = {}
    for p in paths:
        if not p.exists():
            continue
        for f in p.rglob('*'):
            if f.is_file():
                try:
                    m[str(f)] = f.stat().st_mtime
                except Exception:
                    pass
    return m


def diff_snapshots(old: dict[str, float], new: dict[str, float]) -> list[str]:
    changed = []
    # new or modified
    for path, mtime in new.items():
        if path not in old or old.get(path, 0) < mtime:
            changed.append(path)
    # deleted (not critical for doc check, but include)
    for path in old.keys():
        if path not in new:
            changed.append(path)
    return changed


def run_doc_check(changed_paths: list[str]) -> int:
    if not changed_paths:
        return 0
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as tmp:
        for p in changed_paths:
            # make paths relative to repo root
            tmp.write(str(Path(p).as_posix()) + '\n')
        tmp_path = tmp.name
    print('Running doc_check on', len(changed_paths), 'changed files...')
    try:
        res = subprocess.run([sys.executable, 'scripts/doc_check.py', '--changed-files', tmp_path])
        return res.returncode
    finally:
        try:
            Path(tmp_path).unlink()
        except Exception:
            pass


def main():
    print('Starting watcher: monitoring', ', '.join(p.as_posix() for p in WATCH_PATHS))
    last = snapshot(WATCH_PATHS)
    try:
        while True:
            time.sleep(POLL_INTERVAL)
            cur = snapshot(WATCH_PATHS)
            changed = diff_snapshots(last, cur)
            if changed:
                rc = run_doc_check(changed)
                if rc == 0:
                    print('Doc check passed.')
                else:
                    print('Doc check failed (exit code', rc, ').')
                last = cur
    except KeyboardInterrupt:
        print('\nWatcher stopped by user')


if __name__ == '__main__':
    main()
