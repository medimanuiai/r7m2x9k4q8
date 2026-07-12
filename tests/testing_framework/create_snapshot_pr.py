#!/usr/bin/env python3
"""Helper to create a branch with updated snapshot and open a PR using GitHub CLI if available.

Usage: create_snapshot_pr.py snapshot_path branch_name "PR title" "PR body"
"""
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print('RUN:', cmd)
    res = subprocess.run(cmd, shell=True)
    return res.returncode


def create_pr(snapshot_path: str, branch: str, title: str, body: str):
    p = Path(snapshot_path)
    if not p.exists():
        raise SystemExit('Snapshot not found: ' + snapshot_path)
    # create branch
    rc = run(f'git checkout -b {branch}')
    if rc != 0:
        print('Failed to create branch; attempting to continue')
    run(f'git add {str(p)}')
    run('git commit -m "Update golden snapshot" || true')
    run(f'git push origin {branch}')
    # try to open PR with gh CLI
    try:
        rc = run(f'gh pr create --title "{title}" --body "{body}" --base pilot')
        if rc != 0:
            print('gh CLI failed or not configured; please create PR manually')
    except Exception:
        print('gh CLI not available; please create PR manually')


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage: create_snapshot_pr.py snapshot_path branch title body')
        raise SystemExit(2)
    create_pr(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
