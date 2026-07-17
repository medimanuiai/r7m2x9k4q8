#!/usr/bin/env python3
"""Bounded, non-mutating Prompt-01 Stage-01 validation entry point."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Callable, Sequence


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MANIFEST_SHA256 = (
    "01b53b093e62e328de7758ed543a2c8f3b06c3a97e0502d7e879730e8c10d256"
)
PROTECTED_PATHS = (
    "systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP00/requirements-stage01.in",
    "systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP00/requirements-stage01.lock.txt",
    "systems/Parasara/rules/parashara/v1/calibration.json",
    "systems/Parasara/rules/parashara/v1/derived_rules.yml",
    "systems/Parasara/rules/parashara/v1/m1_rules.yaml",
    "systems/Parasara/rules/parashara/v1/macros.yaml",
    "systems/Parasara/rules/parashara/v1/primitives.yml",
    "systems/Parasara/rules/parashara/v1/yogas.yaml",
    "systems/Parasara/fixtures/golden_chart_01.json",
    "systems/Parasara/fixtures/historical_pilot_candidates.json",
    "systems/Parasara/fixtures/output_golden_chart_01.json",
    "systems/Parasara/fixtures/sme_review_package_20.json",
    "systems/Parasara/fixtures/surya_generated_chart.json",
    "systems/Parasara/fixtures/surya_test_chart.json",
    "systems/Parasara/tests/fixtures/golden_career_snapshot.json",
    "systems/Parasara/tests/fixtures/golden_chart_01_career_snapshot.json",
    "systems/Parasara/tests/fixtures/surya_generated_chart_career_snapshot.json",
    "systems/Parasara/tests/snapshots/output_golden_chart_01.json",
    "tests/reports/artifacts/career_rule_traces.json",
    "tests/reports/artifacts/rule_traces.json",
    "tests/reports/coverage_report.json",
    "tests/tmp_snapshot.json",
    "tmp_generated_snapshot.json",
    "-",
)


class ValidationFailure(RuntimeError):
    """A bounded gate failed."""


@dataclass(frozen=True)
class Command:
    name: str
    argv: tuple[str, ...]


Runner = Callable[..., subprocess.CompletedProcess[bytes]]


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "NDASTRO_USE_SRTM": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": ".",
        }
    )
    return environment


def pytest_command(basetemp: Path, *paths: str, collect_only: bool = False) -> tuple[str, ...]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-o",
        "addopts=",
        "-p",
        "no:cacheprovider",
        "--basetemp",
        str(basetemp),
    ]
    if collect_only:
        command.append("--collect-only")
    command.extend(paths)
    return tuple(command)


def _execute(command: Command, runner: Runner = subprocess.run) -> bytes:
    result = runner(
        command.argv,
        cwd=ROOT,
        env=_environment(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        print(f"[FAIL] {command.name} (exit {result.returncode})")
        raise ValidationFailure(command.name)
    print(f"[PASS] {command.name} (exit 0)")
    return result.stdout


def _worktree_signature(runner: Runner = subprocess.run) -> tuple[int, str]:
    command = Command(
        "worktree inspection",
        ("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"),
    )
    payload = _execute(command, runner)
    return payload.count(b"\0"), _sha256(payload)


def _protected_manifest() -> tuple[tuple[str, int, str], ...]:
    rows = []
    for relative in PROTECTED_PATHS:
        path = ROOT / relative
        payload = path.read_bytes()
        rows.append((relative, len(payload), _sha256(payload)))
    return tuple(rows)


def _smoke(runner: Runner) -> None:
    _execute(
        Command(
            "import/version smoke",
            (
                sys.executable,
                "-c",
                (
                    "import sys, pytest, yaml, pydantic; "
                    "print(sys.version.split()[0], pytest.__version__, "
                    "yaml.__version__, pydantic.__version__)"
                ),
            ),
        ),
        runner,
    )
    print(f"  python={sys.version.split()[0]}")


def _collection(temp_root: Path, runner: Runner) -> tuple[int, str]:
    payload = _execute(
        Command(
            "ordered collection",
            pytest_command(temp_root / "collect", collect_only=True),
        ),
        runner,
    )
    node_ids = tuple(
        line for line in payload.decode("utf-8", "replace").splitlines() if "::" in line
    )
    digest = _sha256(("\n".join(node_ids) + "\n").encode("utf-8"))
    print(f"  nodes={len(node_ids)} node_id_sha256={digest}")
    return len(node_ids), digest


def _pytest_gate(name: str, temp_root: Path, runner: Runner, *paths: str) -> None:
    payload = _execute(
        Command(name, pytest_command(temp_root / name.replace(" ", "-"), *paths)),
        runner,
    )
    text = payload.decode("utf-8", "replace")
    summaries = []
    for line in text.splitlines():
        match = re.fullmatch(
            r"(\d+ passed)(?:, (\d+ skipped))?(?: in [0-9.]+s)?",
            line,
        )
        if match:
            summaries.append(match.groups())
    if summaries:
        passed, skipped = summaries[-1]
        suffix = f", {skipped}" if skipped else ""
        print(f"  {passed}{suffix}")


def _manifest(temp_root: Path, runner: Runner) -> str:
    payload = _execute(
        Command(
            "WP17 deterministic scenario manifest",
            (
                sys.executable,
                "tests/wp17/scenario_manifest.py",
                "--artifact-dir",
                str(temp_root / "manifest-artifacts"),
                "--repeats",
                "2",
            ),
        ),
        runner,
    )
    digest = _sha256(payload)
    if digest != EXPECTED_MANIFEST_SHA256:
        print("[FAIL] WP17 manifest contract (unexpected digest)")
        raise ValidationFailure("WP17 manifest contract")
    print(f"  manifest_sha256={digest}")
    return digest


def _rule_lint(runner: Runner) -> tuple[str, ...]:
    rules = ROOT / "systems/Parasara/rules/parashara/v1"
    expected = tuple(
        sorted(
            (
                path.resolve()
                for path in rules.rglob("*")
                if path.suffix.lower() in {".yml", ".yaml"}
            ),
            key=lambda path: str(path).casefold(),
        )
    )
    payload = _execute(
        Command(
            "rule lint",
            (
                sys.executable,
                "tools/rules_lint.py",
                "systems/Parasara/rules/parashara/v1",
            ),
        ),
        runner,
    )
    inspected = []
    prefix = "Inspected rule file: "
    for line in payload.decode("utf-8", "replace").splitlines():
        if line.startswith(prefix):
            inspected.append(Path(line[len(prefix) :]).resolve())
    if tuple(inspected) != expected or len(set(inspected)) != len(inspected):
        print("[FAIL] rule lint coverage (supported files not inspected exactly once)")
        raise ValidationFailure("rule lint coverage")
    names = tuple(path.name for path in expected)
    print(f"  inspected={len(names)} files={','.join(names)}")
    return names


def _snapshot(temp_root: Path, runner: Runner) -> str:
    generated = temp_root / "snapshot" / "generated.json"
    generated.parent.mkdir(parents=True, exist_ok=False)
    _execute(
        Command(
            "strict approved snapshot",
            (
                sys.executable,
                "systems/Parasara/tools/ci_snapshot_check.py",
                "--fixture",
                "systems/Parasara/fixtures/golden_chart_01.json",
                "--approved",
                "systems/Parasara/tests/snapshots/output_golden_chart_01.json",
                "--out",
                str(generated),
            ),
        ),
        runner,
    )
    generated_payload = generated.read_bytes()
    approved_payload = (
        ROOT / "systems/Parasara/tests/snapshots/output_golden_chart_01.json"
    ).read_bytes()
    if generated_payload != approved_payload:
        print("[FAIL] strict approved snapshot (bytes differ)")
        raise ValidationFailure("strict approved snapshot bytes")
    digest = _sha256(approved_payload)
    print(f"  snapshot_bytes={len(approved_payload)} snapshot_sha256={digest}")
    return digest


def validate(mode: str, runner: Runner = subprocess.run) -> int:
    if mode not in {"focused", "full"}:
        raise ValueError(f"unsupported mode: {mode}")
    before_worktree = _worktree_signature(runner)
    before_protected = _protected_manifest()
    print(
        "Prompt-01 Stage-01 validation "
        f"mode={mode} inherited_entries={before_worktree[0]} "
        f"worktree_sha256={before_worktree[1]}"
    )
    gate_failed = False
    try:
        with tempfile.TemporaryDirectory(prefix="prompt01-validation-") as temporary:
            temp_root = Path(temporary)
            _smoke(runner)
            if mode == "focused":
                _pytest_gate("WP19 contract tests", temp_root, runner, "tests/wp19")
                _pytest_gate("WP17 enforcement", temp_root, runner, "tests/wp17")
            else:
                _collection(temp_root, runner)
                _pytest_gate("WP17 enforcement", temp_root, runner, "tests/wp17")
                _pytest_gate("complete repository suite", temp_root, runner)
                _manifest(temp_root, runner)
                _rule_lint(runner)
                _snapshot(temp_root, runner)
    except ValidationFailure:
        gate_failed = True
    try:
        after_protected = _protected_manifest()
        after_worktree = _worktree_signature(runner)
    except (OSError, ValidationFailure):
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
    print("PROMPT_01_VALIDATION: COMPLETE")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("focused", "full"), nargs="?", default="full")
    arguments = parser.parse_args(argv)
    return validate(arguments.mode)


if __name__ == "__main__":
    raise SystemExit(main())
