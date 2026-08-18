#!/usr/bin/env python3
"""Bounded, non-mutating Prompt-03 InferenceEngine validation entry point."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
import tempfile
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import validate_prompt01 as base
from tools import validate_prompt02


EXPECTED_PROMPT03_SCENARIO_SHA256 = (
    "f57bc28504988ecf5ccfbf82de4bc495d2e69a91dfd476997cda5c89a563786e"
)


def _inference_manifest(runner: base.Runner) -> str:
    payload = base._execute(base.Command(
        "Prompt-03 deterministic inference manifest",
        (sys.executable, "tests/inference/scenario_manifest.py"),
    ), runner)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_PROMPT03_SCENARIO_SHA256:
        print("[FAIL] Prompt-03 inference manifest (unexpected digest)")
        raise base.ValidationFailure("Prompt-03 inference manifest")
    print(f"  inference_manifest_sha256={digest}")
    return digest


def validate(mode: str, runner: base.Runner = base.subprocess.run) -> int:
    if mode not in {"focused", "full"}:
        raise ValueError(f"unsupported mode: {mode}")
    before_worktree = base._worktree_signature(runner)
    before_protected = base._protected_manifest()
    print(
        "Prompt-03 InferenceEngine validation "
        f"mode={mode} inherited_entries={before_worktree[0]} "
        f"worktree_sha256={before_worktree[1]}"
    )
    gate_failed = False
    try:
        with tempfile.TemporaryDirectory(prefix="prompt03-validation-") as temporary:
            temp_root = Path(temporary)
            base._smoke(runner)
            base._pytest_gate("Prompt-03 focused contract", temp_root, runner, "tests/inference")
            base._pytest_gate(
                "Prompt-02 preserved contract", temp_root, runner,
                "tests/rules/test_rule_match_contract.py",
                "tests/rules/test_rule_match_integrations.py",
            )
            _inference_manifest(runner)
            if mode == "focused":
                base._pytest_gate("WP17 enforcement", temp_root, runner, "tests/wp17")
            else:
                base._collection(temp_root, runner)
                base._pytest_gate("WP17 enforcement", temp_root, runner, "tests/wp17")
                base._pytest_gate("complete repository suite", temp_root, runner)
                validate_prompt02._prompt02_manifest(temp_root, runner)
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
    print("PROMPT_03_VALIDATION: COMPLETE")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("focused", "full"), nargs="?", default="full")
    arguments = parser.parse_args(argv)
    return validate(arguments.mode)


if __name__ == "__main__":
    raise SystemExit(main())
