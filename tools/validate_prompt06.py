#!/usr/bin/env python3
"""Bounded, non-mutating Prompt-06 Rule Versioning validation entry point.

Composes the Prompt-01/WP17 and Prompt-02 through Prompt-05 validators,
executes ``tests/versioning``, and adds Prompt-06 specific manifest,
cross-environment determinism, and private-tracker-exclusion checks.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import validate_prompt01 as base
from tools import validate_prompt02
from tools import validate_prompt03
from tools import validate_prompt04
from tools import validate_prompt05


EXPECTED_PROMPT06_SCENARIO_SHA256 = (
    "4299d7792cfaf440751937ae6e5393631ab48df7a294a5f42cb9f4e493a21763"
)
PRIVATE_TRACKER_RELATIVE = "systems/Jyothishyam-Systems-and-Subsystems-Status.md"


def _prompt06_manifest(runner: base.Runner) -> str:
    payload = base._execute(base.Command(
        "Prompt-06 deterministic rule-versioning manifest",
        (sys.executable, "tests/versioning/scenario_manifest.py"),
    ), runner)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_PROMPT06_SCENARIO_SHA256:
        print("[FAIL] Prompt-06 rule-versioning manifest (unexpected digest)")
        print(f"  observed_prompt06_manifest_sha256={digest}")
        raise base.ValidationFailure("Prompt-06 rule-versioning manifest")
    print(f"  prompt06_manifest_sha256={digest}")
    return digest


def _cross_environment_determinism(runner: base.Runner) -> str:
    """Prove the manifest is stable across hash seeds, subprocesses, and CWD."""

    digests: set[str] = set()
    for seed in ("0", "12345"):
        environment = base._environment()
        environment["PYTHONHASHSEED"] = seed
        result = runner(
            (sys.executable, "tests/versioning/scenario_manifest.py"),
            cwd=ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode:
            print(f"[FAIL] Prompt-06 manifest under PYTHONHASHSEED={seed}")
            raise base.ValidationFailure("Prompt-06 hash-seed determinism")
        digests.add(hashlib.sha256(result.stdout).hexdigest())
    with tempfile.TemporaryDirectory(prefix="prompt06-cwd-") as alternate_cwd:
        result = runner(
            (sys.executable, str(ROOT / "tests" / "versioning" / "scenario_manifest.py")),
            cwd=alternate_cwd,
            env=base._environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode:
            print("[FAIL] Prompt-06 manifest under an alternate working directory")
            raise base.ValidationFailure("Prompt-06 CWD determinism")
        digests.add(hashlib.sha256(result.stdout).hexdigest())
    if digests != {EXPECTED_PROMPT06_SCENARIO_SHA256}:
        print("[FAIL] Prompt-06 manifest is not stable across hash seed/CWD/subprocess")
        raise base.ValidationFailure("Prompt-06 cross-environment determinism")
    print(f"  cross_environment_sha256={EXPECTED_PROMPT06_SCENARIO_SHA256}")
    return EXPECTED_PROMPT06_SCENARIO_SHA256


def _private_tracker_excluded(runner: base.Runner) -> None:
    tracked = base._execute(
        base.Command(
            "private tracker git-ls-files exclusion",
            ("git", "ls-files", "--", PRIVATE_TRACKER_RELATIVE),
        ),
        runner,
    )
    if tracked.strip():
        print("[FAIL] private tracker is tracked by git")
        raise base.ValidationFailure("private tracker tracked")
    staged = base._execute(
        base.Command(
            "private tracker staged exclusion",
            ("git", "diff", "--cached", "--name-only", "--", PRIVATE_TRACKER_RELATIVE),
        ),
        runner,
    )
    if staged.strip():
        print("[FAIL] private tracker is staged")
        raise base.ValidationFailure("private tracker staged")
    print("[PASS] private tracker is untracked and unstaged")


def validate(mode: str, runner: base.Runner = base.subprocess.run) -> int:
    if mode not in {"focused", "full"}:
        raise ValueError(f"unsupported mode: {mode}")
    before_worktree = base._worktree_signature(runner)
    before_protected = base._protected_manifest()
    before_exports = validate_prompt04._personal_export_manifest()
    print(
        "Prompt-06 Rule Versioning validation "
        f"mode={mode} inherited_entries={before_worktree[0]} "
        f"worktree_sha256={before_worktree[1]}"
    )
    gate_failed = False
    try:
        with tempfile.TemporaryDirectory(prefix="prompt06-validation-") as temporary:
            temp_root = Path(temporary)
            base._smoke(runner)
            base._pytest_gate(
                "Prompt-06 focused contracts", temp_root, runner, "tests/versioning"
            )
            base._pytest_gate(
                "Prompt-05 preserved contract", temp_root, runner, "tests/domain"
            )
            base._pytest_gate(
                "Prompt-02 preserved contract", temp_root, runner,
                "tests/rules/test_rule_match_contract.py",
                "tests/rules/test_rule_match_integrations.py",
            )
            base._pytest_gate(
                "Prompt-03 preserved contract", temp_root, runner, "tests/inference"
            )
            base._pytest_gate(
                "Prompt-04 preserved contract", temp_root, runner, "tests/astrostate"
            )
            base._pytest_gate(
                "WP17 current Prompt-01 integrity", temp_root, runner, "tests/wp17"
            )
            validate_prompt02._prompt02_manifest(temp_root, runner)
            validate_prompt03._inference_manifest(runner)
            validate_prompt04._prompt04_manifest(runner)
            validate_prompt05._prompt05_manifest(runner)
            _prompt06_manifest(runner)
            _cross_environment_determinism(runner)
            _private_tracker_excluded(runner)
            if mode == "full":
                validate_prompt05._repository_collection(temp_root, runner)
                base._pytest_gate(
                    "complete repository suite",
                    temp_root,
                    runner,
                    "tests",
                    "systems/Parasara/tests",
                )
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
    if not validate_prompt04._personal_exports_unchanged(before_exports):
        print("[FAIL] protected personal exports changed")
        return 1
    if after_worktree != before_worktree:
        print("[FAIL] worktree changed during validation")
        return 1
    print(f"[PASS] protected artifacts unchanged ({len(before_protected)} files)")
    print(f"[PASS] protected personal exports unchanged ({len(before_exports)} present files)")
    print("[PASS] inherited worktree unchanged")
    if gate_failed:
        return 1
    print("PROMPT_06_VALIDATION: COMPLETE")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("focused", "full"), default="full")
    arguments = parser.parse_args(argv)
    return validate(arguments.mode)


if __name__ == "__main__":
    raise SystemExit(main())
