#!/usr/bin/env python3
"""Bounded, non-mutating Prompt-04 AstroState API validation entry point.

The historical Prompt-01 full validator and digest remain untouched.  Current
integrity is composed through WP17, Prompt-02, Prompt-03, and Prompt-04 gates.
"""

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


EXPECTED_PROMPT04_SCENARIO_SHA256 = (
    "440a459cc60e9575874341e7c6673e714585ae79123957c9c19ccd175cb7930b"
)
PERSONAL_EXPORTS = tuple(
    ROOT / "systems" / "Parasara" / "Documentation" / "Engine" / "MVP" / f"Manohar-try{index}.json"
    for index in range(1, 5)
)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _personal_export_manifest(
    paths: Sequence[Path] = PERSONAL_EXPORTS,
) -> tuple[tuple[str, int, str], ...]:
    """Capture only exports present at validator startup.

    Personal exports are intentionally untracked and absent in clean CI
    checkouts.  Absolute paths are retained only inside this process so any
    initially present file can still be protected against rename/deletion.
    """

    return tuple(
        (str(path.resolve()), path.stat().st_size, _sha256(path.read_bytes()))
        for path in paths
        if path.is_file()
    )


def _personal_exports_unchanged(
    baseline: tuple[tuple[str, int, str], ...],
) -> bool:
    for raw_path, expected_size, expected_digest in baseline:
        path = Path(raw_path)
        if not path.is_file():
            return False
        if path.stat().st_size != expected_size or _sha256(path.read_bytes()) != expected_digest:
            return False
    return True


def _prompt04_manifest(runner: base.Runner) -> str:
    payload = base._execute(base.Command(
        "Prompt-04 deterministic snapshot/query manifest",
        (sys.executable, "tests/astrostate/scenario_manifest.py"),
    ), runner)
    digest = _sha256(payload)
    if digest != EXPECTED_PROMPT04_SCENARIO_SHA256:
        print("[FAIL] Prompt-04 snapshot/query manifest (unexpected digest)")
        print(f"  observed_prompt04_manifest_sha256={digest}")
        raise base.ValidationFailure("Prompt-04 snapshot/query manifest")
    print(f"  prompt04_manifest_sha256={digest}")
    return digest


def validate(mode: str, runner: base.Runner = base.subprocess.run) -> int:
    if mode not in {"focused", "full"}:
        raise ValueError(f"unsupported mode: {mode}")
    before_worktree = base._worktree_signature(runner)
    before_protected = base._protected_manifest()
    before_exports = _personal_export_manifest()
    print(
        "Prompt-04 AstroState API validation "
        f"mode={mode} inherited_entries={before_worktree[0]} "
        f"worktree_sha256={before_worktree[1]}"
    )
    gate_failed = False
    try:
        with tempfile.TemporaryDirectory(prefix="prompt04-validation-") as temporary:
            temp_root = Path(temporary)
            base._smoke(runner)
            base._pytest_gate(
                "Prompt-02 preserved contract", temp_root, runner,
                "tests/rules/test_rule_match_contract.py",
                "tests/rules/test_rule_match_integrations.py",
            )
            base._pytest_gate("Prompt-03 preserved contract", temp_root, runner, "tests/inference")
            base._pytest_gate("Prompt-04 focused contract", temp_root, runner, "tests/astrostate")
            base._pytest_gate("WP17 current Prompt-01 integrity", temp_root, runner, "tests/wp17")
            validate_prompt02._prompt02_manifest(temp_root, runner)
            validate_prompt03._inference_manifest(runner)
            _prompt04_manifest(runner)
            if mode == "full":
                base._collection(temp_root, runner)
                base._pytest_gate("complete repository suite", temp_root, runner)
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
    if not _personal_exports_unchanged(before_exports):
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
    print("PROMPT_04_VALIDATION: COMPLETE")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("focused", "full"), nargs="?", default="full")
    arguments = parser.parse_args(argv)
    return validate(arguments.mode)


if __name__ == "__main__":
    raise SystemExit(main())
