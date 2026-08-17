#!/usr/bin/env python3
"""Bounded, non-mutating Prompt-02 RuleMatch validation entry point.

Prompt-01's validator and frozen Stage-01 manifest identity remain unchanged.
This validator reuses its gates while supplying the intentional Prompt-02
internal serialization identity only for the manifest check in this process.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import validate_prompt01 as base


EXPECTED_PROMPT02_MANIFEST_SHA256 = (
    "75b65d2cd1420c6261aadbb8159d10fb8c641137ce08d29f2a651952e5cdfaf7"
)


def _prompt02_manifest(temp_root: Path, runner: base.Runner) -> str:
    historical_digest = base.EXPECTED_MANIFEST_SHA256
    try:
        base.EXPECTED_MANIFEST_SHA256 = EXPECTED_PROMPT02_MANIFEST_SHA256
        return base._manifest(temp_root, runner)
    finally:
        base.EXPECTED_MANIFEST_SHA256 = historical_digest


def validate(mode: str, runner: base.Runner = base.subprocess.run) -> int:
    if mode not in {"focused", "full"}:
        raise ValueError(f"unsupported mode: {mode}")
    before_worktree = base._worktree_signature(runner)
    before_protected = base._protected_manifest()
    print(
        "Prompt-02 RuleMatch validation "
        f"mode={mode} inherited_entries={before_worktree[0]} "
        f"worktree_sha256={before_worktree[1]}"
    )
    gate_failed = False
    try:
        with tempfile.TemporaryDirectory(prefix="prompt02-validation-") as temporary:
            temp_root = Path(temporary)
            base._smoke(runner)
            base._pytest_gate(
                "Prompt-02 focused contract",
                temp_root,
                runner,
                "tests/rules/test_rule_match_contract.py",
                "tests/rules/test_rule_match_integrations.py",
            )
            if mode == "focused":
                base._pytest_gate("WP19 contract tests", temp_root, runner, "tests/wp19")
                base._pytest_gate("WP17 enforcement", temp_root, runner, "tests/wp17")
            else:
                base._collection(temp_root, runner)
                base._pytest_gate("WP17 enforcement", temp_root, runner, "tests/wp17")
                base._pytest_gate("complete repository suite", temp_root, runner)
                _prompt02_manifest(temp_root, runner)
                base._rule_lint(runner)
                base._snapshot(temp_root, runner)
    except base.ValidationFailure:
        gate_failed = True
    try:
        after_protected = base._protected_manifest()
        after_worktree = base._worktree_signature(runner)
    except (OSError, base.ValidationFailure):
        print("[FAIL] post-validation mutation inspection")
        return 1
    if after_protected != before_protected:
        print("[FAIL] protected artifacts changed")
        return 1
    if after_worktree != before_worktree:
        print("[FAIL] worktree changed during validation")
        return 1
    print(f"[PASS] protected artifacts unchanged ({len(before_protected)} files)")
    print("[PASS] inherited worktree unchanged")
    if gate_failed:
        return 1
    print("PROMPT_02_VALIDATION: COMPLETE")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("focused", "full"), nargs="?", default="full")
    arguments = parser.parse_args(argv)
    return validate(arguments.mode)


if __name__ == "__main__":
    raise SystemExit(main())
