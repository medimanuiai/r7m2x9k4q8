#!/usr/bin/env python3
"""Bounded, non-mutating Prompt-05 Typed Domain Models validation."""

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
from tools import validate_prompt03
from tools import validate_prompt04


EXPECTED_PROMPT05_SCENARIO_SHA256 = (
    "f6d90db74309127e99d55e17c542214b05bb385b8ec62447c1baef53c393ba92"
)


def _prompt05_manifest(runner: base.Runner) -> str:
    payload = base._execute(base.Command(
        "Prompt-05 deterministic typed-domain manifest",
        (sys.executable, "tests/domain/scenario_manifest.py"),
    ), runner)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_PROMPT05_SCENARIO_SHA256:
        print("[FAIL] Prompt-05 typed-domain manifest (unexpected digest)")
        print(f"  observed_prompt05_manifest_sha256={digest}")
        raise base.ValidationFailure("Prompt-05 typed-domain manifest")
    print(f"  prompt05_manifest_sha256={digest}")
    return digest


def _repository_collection(temp_root: Path, runner: base.Runner) -> tuple[int, str]:
    payload = base._execute(
        base.Command(
            "ordered repository collection",
            base.pytest_command(
                temp_root / "collect",
                "tests",
                "systems/Parasara/tests",
                collect_only=True,
            ),
        ),
        runner,
    )
    node_ids = tuple(
        line for line in payload.decode("utf-8", "replace").splitlines()
        if "::" in line
    )
    digest = hashlib.sha256(("\n".join(node_ids) + "\n").encode("utf-8")).hexdigest()
    print(f"  nodes={len(node_ids)} node_id_sha256={digest}")
    return len(node_ids), digest


def validate(mode: str, runner: base.Runner = base.subprocess.run) -> int:
    if mode not in {"focused", "full"}:
        raise ValueError(f"unsupported mode: {mode}")
    before_worktree = base._worktree_signature(runner)
    before_protected = base._protected_manifest()
    before_exports = validate_prompt04._personal_export_manifest()
    print(
        "Prompt-05 Typed Domain Models validation "
        f"mode={mode} inherited_entries={before_worktree[0]} "
        f"worktree_sha256={before_worktree[1]}"
    )
    gate_failed = False
    try:
        with tempfile.TemporaryDirectory(prefix="prompt05-validation-") as temporary:
            temp_root = Path(temporary)
            base._smoke(runner)
            base._pytest_gate(
                "Prompt-05 focused contracts", temp_root, runner, "tests/domain"
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
            _prompt05_manifest(runner)
            if mode == "full":
                _repository_collection(temp_root, runner)
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
    print("PROMPT_05_VALIDATION: COMPLETE")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("focused", "full"), nargs="?", default="full")
    arguments = parser.parse_args(argv)
    return validate(arguments.mode)


if __name__ == "__main__":
    raise SystemExit(main())
