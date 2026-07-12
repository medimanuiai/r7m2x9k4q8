#!/usr/bin/env python3
"""Create a branch and PR for updated snapshots using GITHUB_TOKEN.

This script is intended to run in CI. It detects git changes under
`tests/reports` or `systems/Parasara/tests/snapshots` and, if present,
commits them to a new branch and opens a PR against `pilot`.
"""
import os
import sys
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def run(cmd: str) -> int:
    print('$', cmd)
    return os.system(cmd)


def repo_changed() -> bool:
    # list changed files
    rc = os.popen('git status --porcelain').read().strip()
    return bool(rc)


def create_branch_and_push(branch: str) -> None:
    run(f'git config user.email "actions@github.com"')
    run(f'git config user.name "GitHub Actions"')
    run(f'git checkout -b {branch}')
    run('git add tests/reports || true')
    run('git add systems/Parasara/tests/snapshots || true')
    run('git commit -m "chore: update golden snapshots from CI" || true')
    # set auth remote
    repo = os.environ.get('GITHUB_REPOSITORY')
    token = os.environ.get('GITHUB_TOKEN')
    if not repo or not token:
        print('Missing GITHUB_REPOSITORY or GITHUB_TOKEN; cannot push')
        return
    remote = f'https://x-access-token:{token}@github.com/{repo}.git'
    run(f'git remote set-url origin {remote}')
    run(f'git push origin {branch}')


def create_pr(title: str, body: str, head: str, base: str = 'pilot') -> None:
    repo = os.environ.get('GITHUB_REPOSITORY')
    token = os.environ.get('GITHUB_TOKEN')
    if not repo or not token:
        print('Missing GITHUB_REPOSITORY or GITHUB_TOKEN; cannot create PR')
        return
    url = f'https://api.github.com/repos/{repo}/pulls'
    payload = json.dumps({'title': title, 'body': body, 'head': head, 'base': base}).encode('utf-8')
    req = Request(url, data=payload, headers={'Authorization': f'token {token}', 'Content-Type': 'application/json'})
    try:
        resp = urlopen(req)
        data = resp.read().decode('utf-8')
        print('PR created:', data)
    except HTTPError as e:
        print('Failed to create PR:', e.read().decode('utf-8'))


def main():
    if not repo_changed():
        print('No changes to commit.')
        return
    ts = int(time.time())
    branch = f'ci/snapshot-update-{ts}'
    create_branch_and_push(branch)
    title = 'CI: Update golden snapshots'
    body = 'Automated update of golden snapshots from CI run.'
    create_pr(title, body, branch)


if __name__ == '__main__':
    main()
