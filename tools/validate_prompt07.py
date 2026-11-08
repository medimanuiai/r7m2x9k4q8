#!/usr/bin/env python3
"""Bounded, non-mutating Prompt-07 Rule DSL validation entry point."""

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
from tools import validate_prompt06


EXPECTED_PROMPT07_SCENARIO_SHA256 = (
    "248bfabc5cc143ab4d64d5b297e5a3449b2573459f2bd22428708ec1c745beee"
)
V1_MANIFEST_SHA256 = "687c7bb19ce03671882e989db267d588a3c9beace1c42df25390ab643ebae265"
V1_MANIFEST_FINGERPRINT = "3e942f97cec7c24079faabc3db358b84177b752a8eb35a7b0d909f84a92d1220"
V1_CATALOG_SHA256 = "b4a94e0ff94209bf901e4f74573bb9fb95206116cdf6f9efcda189ccf7135a1a"
SNAPSHOT_SHA256 = "da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af"
PRIVATE_TRACKER_RELATIVE = "systems/Jyothishyam-Systems-and-Subsystems-Status.md"
PROMPT01_FOCUSED_PATHS = (
    "tests/rules/test_condition_evaluator.py",
    "tests/rules/test_condition_models.py",
    "tests/rules/test_definition_validation.py",
    "tests/rules/test_planet_in_house_canonical.py",
    "tests/rules/test_predicate_canonical.py",
    "tests/rules/test_predicate_capabilities.py",
    "tests/rules/test_predicate_evaluator_cache.py",
    "tests/rules/test_predicate_models.py",
    "tests/rules/test_predicate_parameters.py",
    "tests/rules/test_predicate_registry.py",
    "tests/rules/test_predicate_result.py",
    "tests/rules/test_registered_predicates_characterization.py",
    "tests/rules/test_remaining_canonical_predicates.py",
)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _prompt07_manifest(runner: base.Runner) -> str:
    payload = base._execute(base.Command(
        "Prompt-07 deterministic Rule DSL manifest",
        (sys.executable, "tests/dsl/scenario_manifest.py"),
    ), runner)
    digest = _sha256(payload)
    if digest != EXPECTED_PROMPT07_SCENARIO_SHA256:
        print("[FAIL] Prompt-07 Rule DSL manifest (unexpected digest)")
        print(f"  observed_prompt07_manifest_sha256={digest}")
        raise base.ValidationFailure("Prompt-07 Rule DSL manifest")
    print(f"  prompt07_manifest_sha256={digest}")
    return digest


def _cross_environment_determinism(runner: base.Runner) -> str:
    digests: set[str] = set()
    for seed in ("0", "12345"):
        environment = base._environment()
        environment["PYTHONHASHSEED"] = seed
        result = runner(
            (sys.executable, "tests/dsl/scenario_manifest.py"),
            cwd=ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode:
            print(f"[FAIL] Prompt-07 manifest under PYTHONHASHSEED={seed}")
            raise base.ValidationFailure("Prompt-07 hash-seed determinism")
        digests.add(_sha256(result.stdout))
    with tempfile.TemporaryDirectory(prefix="prompt07-cwd-") as alternate_cwd:
        result = runner(
            (sys.executable, str(ROOT / "tests/dsl/scenario_manifest.py")),
            cwd=alternate_cwd,
            env=base._environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode:
            print("[FAIL] Prompt-07 manifest under an alternate working directory")
            raise base.ValidationFailure("Prompt-07 CWD determinism")
        digests.add(_sha256(result.stdout))
    if digests != {EXPECTED_PROMPT07_SCENARIO_SHA256}:
        print("[FAIL] Prompt-07 manifest is not stable across process/hash seed/CWD")
        raise base.ValidationFailure("Prompt-07 cross-environment determinism")
    print(f"  cross_environment_sha256={EXPECTED_PROMPT07_SCENARIO_SHA256}")
    return EXPECTED_PROMPT07_SCENARIO_SHA256


def _current_v1_exact() -> None:
    manifest = (ROOT / "systems/Parasara/rules/parashara/v1/rule-set-manifest.json").read_bytes()
    catalog = (ROOT / "systems/Parasara/config/versioning/parashara_rule_sets_v1.json").read_bytes()
    snapshot = (ROOT / "systems/Parasara/tests/snapshots/output_golden_chart_01.json").read_bytes()
    if (
        _sha256(manifest) != V1_MANIFEST_SHA256
        or V1_MANIFEST_FINGERPRINT.encode("ascii") not in manifest
        or b'"dsl": null' not in manifest
        or b'"dependency_graph": null' not in manifest
        or _sha256(catalog) != V1_CATALOG_SHA256
        or len(snapshot) != 4_041
        or _sha256(snapshot) != SNAPSHOT_SHA256
    ):
        print("[FAIL] current v1 manifest/catalog or approved snapshot changed")
        raise base.ValidationFailure("current v1 protection")
    print(f"[PASS] current v1 exact fingerprint={V1_MANIFEST_FINGERPRINT}")
    print(f"  snapshot_bytes={len(snapshot)} snapshot_sha256={SNAPSHOT_SHA256}")


def _repository_boundaries(runner: base.Runner) -> None:
    tracked = base._execute(base.Command(
        "private tracker git-ls-files exclusion",
        ("git", "ls-files", "--", PRIVATE_TRACKER_RELATIVE),
    ), runner)
    ignored = runner(
        ("git", "check-ignore", "-v", "--", PRIVATE_TRACKER_RELATIVE),
        cwd=ROOT,
        env=base._environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    status = runner(
        ("git", "status", "--porcelain=v1", "--untracked-files=all"),
        cwd=ROOT,
        env=base._environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if status.returncode:
        print("[FAIL] repository status inspection")
        raise base.ValidationFailure("repository status inspection")
    status_rows = status.stdout.decode("utf-8", "replace").splitlines()
    staged_rows = tuple(row for row in status_rows if row[:1] not in {" ", "?"})
    deleted_rows = tuple(row for row in status_rows if "D" in row[:2])
    base._execute(base.Command("git diff check", ("git", "diff", "--check")), runner)
    if tracked.strip() or ignored.returncode or staged_rows or deleted_rows:
        print("[FAIL] tracker/staging/deletion repository boundary")
        raise base.ValidationFailure("Prompt-07 repository boundary")
    misplaced_graph_modules = tuple(
        path for path in (ROOT / "systems/Parasara").rglob("*.py")
        if path.name in {"dependency_graph.py", "graph_planner.py"}
    )
    dsl_sources = tuple((ROOT / "systems/Parasara/engine/rules/dsl").glob("*.py"))
    if misplaced_graph_modules or any(
        "requires_matches" in path.read_text(encoding="utf-8")
        or "optional_supports" in path.read_text(encoding="utf-8") for path in dsl_sources
    ):
        print("[FAIL] dependency graph crossed the separate opt-in DSL boundary")
        raise base.ValidationFailure("dependency graph isolation")
    _current_v1_exact()
    print("[PASS] private tracker ignored/untracked/unstaged; graph opt-in and current-v1 boundary preserved")


def validate(mode: str, runner: base.Runner = subprocess.run) -> int:
    if mode not in {"focused", "full"}:
        raise ValueError(f"unsupported mode: {mode}")
    before_worktree = base._worktree_signature(runner)
    before_protected = base._protected_manifest()
    before_exports = validate_prompt04._personal_export_manifest()
    print(
        "Prompt-07 Rule DSL validation "
        f"mode={mode} inherited_entries={before_worktree[0]} "
        f"worktree_sha256={before_worktree[1]}"
    )
    gate_failed = False
    try:
        with tempfile.TemporaryDirectory(prefix="prompt07-validation-") as temporary:
            temp_root = Path(temporary)
            base._smoke(runner)
            base._pytest_gate("Prompt-07 focused contracts", temp_root, runner, "tests/dsl")
            base._pytest_gate("Prompt-06 preserved contracts", temp_root, runner, "tests/versioning")
            base._pytest_gate(
                "Prompt-01 condition predicate definition contracts",
                temp_root, runner, *PROMPT01_FOCUSED_PATHS,
            )
            base._pytest_gate(
                "Prompt-02 preserved contract", temp_root, runner,
                "tests/rules/test_rule_match_contract.py",
                "tests/rules/test_rule_match_integrations.py",
            )
            base._pytest_gate("Prompt-03 preserved contract", temp_root, runner, "tests/inference")
            base._pytest_gate("Prompt-04 preserved contract", temp_root, runner, "tests/astrostate")
            base._pytest_gate("Prompt-05 preserved contract", temp_root, runner, "tests/domain")
            base._pytest_gate("WP17 current Prompt-01 integrity", temp_root, runner, "tests/wp17")
            validate_prompt02._prompt02_manifest(temp_root, runner)
            validate_prompt03._inference_manifest(runner)
            validate_prompt04._prompt04_manifest(runner)
            validate_prompt05._prompt05_manifest(runner)
            validate_prompt06._prompt06_manifest(runner)
            _prompt07_manifest(runner)
            _cross_environment_determinism(runner)
            _current_v1_exact()
            _repository_boundaries(runner)
            if mode == "full":
                validate_prompt05._repository_collection(temp_root, runner)
                base._pytest_gate(
                    "complete repository suite", temp_root, runner,
                    "tests", "systems/Parasara/tests",
                )
                base._rule_lint(runner)
                base._snapshot(temp_root, runner)
    except (OSError, base.ValidationFailure):
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
    print("PROMPT_07_VALIDATION: COMPLETE")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("focused", "full"), default="full")
    arguments = parser.parse_args(argv)
    return validate(arguments.mode)


if __name__ == "__main__":
    raise SystemExit(main())
