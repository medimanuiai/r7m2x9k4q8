#!/usr/bin/env python3
"""Read-only FWP01 acceptance; an unreadable inventory is never a pass."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import validate_prompt01 as base
from tools import validate_prompt07 as predecessor
from tools import validate_prompt08 as graph

SPEC = "systems/Parasara/Documentation/Engine/Functional-Work-Packages/FWP01/requirements/FWP01-Core-Input-and-Enrichment-Closure.md"
# User-authorized reconciled parent and bounded V2 extension.
SPEC_SHA256 = "01b53a590a2459c34c011751c3c220544ea97979e72a76fa8df836fc78b4c11b"
ADDENDUM = SPEC.replace("FWP01-Core-Input-and-Enrichment-Closure.md", "FWP01-Aspect-Contract-v2-Addendum.md")
ADDENDUM_SHA256 = "ddc1c3967433f0f1cf6bdffb4f043a23ec4efc5b0cb8147b602ea257a6f2436f"
EVIDENCE = ROOT / "systems/Parasara/Documentation/Engine/Functional-Work-Packages/FWP01/Reports/Aspect-Contract-v2-Implementation"
TRACKER = predecessor.PRIVATE_TRACKER_RELATIVE
# Immutable original implementation inventory, retained in OS temporary evidence.
# A remediation/session inventory cannot replace this historical authority.
ORIGINAL_BASELINE_SHA256 = "63615ed483e778b9264ce85e18b1d35c221606d6287aaa4f490131c8ff27450f"


def git(*args):
    return subprocess.check_output(("git", *args), cwd=ROOT)


def inventory():
    names = set(filter(None, git("ls-files", "--cached", "--others", "--exclude-standard", "-z").decode().split("\0")))
    names.update(graph.RELEVANT_IGNORED)
    hashes, errors = {}, []
    for name in sorted(names):
        path = ROOT / name
        try:
            if path.is_file():
                with path.open("rb") as stream:
                    hashes[name] = hashlib.file_digest(stream, "sha256").hexdigest()
            elif not path.is_dir():
                hashes[name] = None
        except OSError as exc:
            errors.append(dict(path=name, error=type(exc).__name__))
    return dict(hashes=hashes, errors=errors,
        head=git("rev-parse", "HEAD").decode().strip(),
        branch=git("branch", "--show-current").decode().strip(),
        branches=git("for-each-ref", "--format=%(refname):%(objectname)", "refs/heads").decode(),
        index=hashlib.sha256(git("ls-files", "--stage", "-z")).hexdigest(),
        staged=git("diff", "--cached", "--name-status").decode())


def allowed_paths():
    text = (ROOT / SPEC).read_text(encoding="utf-8")
    result = {TRACKER}
    for heading, following in (("10.1", "10.2"), ("10.2", "10.3"), ("10.4", "10.5"), ("10.5", "10.6")):
        block = text.split("### " + heading + " ", 1)[1].split("### " + following + " ", 1)[0]
        result.update(block.split("```text\n", 1)[1].split("```", 1)[0].strip().splitlines())
    return result | v2_allowed_paths()


def v2_allowed_paths():
    text = (ROOT / ADDENDUM).read_text(encoding="utf-8")
    scope = text.split("## 5. ", 1)[1].split("## 6. ", 1)[0]
    blocks = re.findall(r"```text\n(.*?)```", scope, re.DOTALL)
    return {TRACKER} | {line for block in blocks for line in block.strip().splitlines()}


def current_session_scope(path, current, expected_sha256):
    if not path or not expected_sha256:
        return dict(status="INCOMPLETE", issues=["current_session_inventory_missing"])
    payload = Path(path).read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != expected_sha256:
        return dict(status="FAIL", issues=["current_session_inventory_hash_mismatch"])
    scope = compare_baseline(json.loads(payload), current, v2_allowed_paths())
    status = ("FAIL" if scope["unauthorized"] or scope["deleted"] or not scope["git_preserved"]
              else "INCOMPLETE" if scope["unreadable"] else "PASS")
    return dict(status=status, baseline_sha256=digest, scope=scope,
                historical_preservation="UNVERIFIED")


def compare_baseline(before, after, allowed=()):
    allowed = set(allowed)
    unreadable = {row["path"] for state in (before, after) for row in state["errors"]}
    changed = sorted(name for name in before["hashes"].keys() | after["hashes"].keys()
        if name not in unreadable and before["hashes"].get(name) != after["hashes"].get(name))
    unauthorized = [name for name in changed if name not in allowed]
    deleted = [name for name in before["hashes"] if name not in after["hashes"] and name not in unreadable]
    git_preserved = all(before[key] == after[key] for key in ("head", "branch", "branches", "index", "staged"))
    return dict(changed=changed, unauthorized=unauthorized, deleted=deleted,
        git_preserved=git_preserved, unreadable=sorted(unreadable))


def historical_scope(baseline, current, expected_sha256=None):
    """No acceptance-grade scope result without the authentic original inventory."""
    if not baseline:
        return dict(status="INCOMPLETE", issues=["original_baseline_missing"])
    try:
        payload = Path(baseline).read_bytes()
    except OSError:
        return dict(status="FAIL", issues=["original_baseline_unreadable"])
    digest = hashlib.sha256(payload).hexdigest()
    if digest != ORIGINAL_BASELINE_SHA256 or (expected_sha256 is not None and digest != expected_sha256):
        return dict(status="FAIL", issues=["original_baseline_hash_mismatch"])
    try:
        initial = json.loads(payload)
        scope = compare_baseline(initial, current, allowed_paths())
    except (ValueError, TypeError, KeyError, AttributeError):
        return dict(status="FAIL", issues=["original_baseline_invalid"])
    status = ("FAIL" if scope["unauthorized"] or scope["deleted"] or not scope["git_preserved"]
              else "INCOMPLETE" if scope["unreadable"] else "PASS")
    return dict(status=status, issues=["historical_inventory_unreadable"] if status == "INCOMPLETE" else [],
                baseline_sha256=digest, scope=scope)


def runner(argv, **kwargs):
    result = subprocess.run(argv, **kwargs)
    if result.returncode:
        print((result.stdout or b"").decode("utf-8", "replace")[-16000:], flush=True)
    elif "pytest" in argv:
        summaries = [line for line in result.stdout.decode("utf-8", "replace").splitlines()
                     if re.search(r"\d+ (passed|(?:tests? )?collected|skipped)", line)]
        if not summaries:
            raise base.ValidationFailure("pytest counts unavailable")
        print("  " + summaries[-1].strip("= "), flush=True)
    return result


def scenario_matrix(profile="v1"):
    from tests.fwp01.test_determinism import EXPECTED_SCENARIO_SHA256, EXPECTED_V2_SCENARIO_SHA256
    pinned = EXPECTED_V2_SCENARIO_SHA256 if profile == "v2" else EXPECTED_SCENARIO_SHA256
    expected = None
    script = str(ROOT / "tests/fwp01/scenario_manifest.py")
    runs = 0
    with tempfile.TemporaryDirectory(prefix="fwp01-cwd-") as alternate:
        for seed in ("0", "1", "42", "random"):
            for cwd in (ROOT, Path(alternate)):
                for _ in range(2):
                    environment = base._environment()
                    environment["PYTHONHASHSEED"] = seed
                    # PYTHONPATH is absolute when the script executes outside ROOT.
                    environment["PYTHONPATH"] = str(ROOT)
                    result = subprocess.run((sys.executable, "-B", script, *(("--v2",) if profile == "v2" else ())), cwd=cwd,
                        env=environment, capture_output=True, check=False)
                    if result.returncode or result.stderr:
                        raise base.ValidationFailure("FWP01 scenario process")
                    digest = hashlib.sha256(result.stdout).hexdigest()
                    if digest != pinned:
                        raise base.ValidationFailure("FWP01 pinned scenario digest")
                    if expected is None:
                        expected = result.stdout
                    if result.stdout != expected:
                        raise base.ValidationFailure("FWP01 scenario seed/CWD/repetition drift")
                    runs += 1
    print(f"[PASS] fwp01_scenario_sha256={digest} local_runs={runs} python={platform.python_version()}", flush=True)
    return digest


def repository_boundaries():
    if hashlib.sha256((ROOT / SPEC).read_bytes()).hexdigest() != SPEC_SHA256:
        raise base.ValidationFailure("approved specification hash")
    if hashlib.sha256((ROOT / ADDENDUM).read_bytes()).hexdigest() != ADDENDUM_SHA256:
        raise base.ValidationFailure("approved V2 addendum hash")
    if git("branch", "--show-current").decode().strip() != "main" or git("rev-parse", "HEAD").decode().strip() != "ec6b49a164389aada4e741561d75cb866527e6cf":
        raise base.ValidationFailure("branch/HEAD boundary")
    if git("diff", "--cached", "--name-status").strip():
        raise base.ValidationFailure("staging boundary")
    if git("ls-files", "--", TRACKER).strip() or subprocess.run(("git", "check-ignore", "-q", "--", TRACKER), cwd=ROOT).returncode:
        raise base.ValidationFailure("private tracker policy")
    base._execute(base.Command("git diff check", ("git", "diff", "--check")), runner)
    for name in allowed_paths():
        path = ROOT / name
        if name == TRACKER or not path.is_file():
            continue
        if any(line.rstrip() != line for line in path.read_text(encoding="utf-8").splitlines()):
            # Inherited whitespace is not a new FWP01 defect. Check only new
            # files here; git diff --check covers changed lines in tracked files.
            if not git("ls-files", "--", name).strip():
                raise base.ValidationFailure("untracked source whitespace")
    graph.boundaries()


def validate(args):
    before = inventory()
    report = dict(python=platform.python_version(), stages={},
        inventory_before_errors=before["errors"], approved_specification_sha256=SPEC_SHA256,
        approved_addendum_sha256=ADDENDUM_SHA256)
    failed, incomplete = False, bool(before["errors"])

    def gate(name, function):
        nonlocal failed
        try:
            value = function()
            if type(value) is int and value:
                raise base.ValidationFailure(name)
            report["stages"][name] = "PASS"
            print("[PASS] " + name, flush=True)
            return value
        except (OSError, ValueError, subprocess.SubprocessError, base.ValidationFailure) as exc:
            failed = True
            report["stages"][name] = "FAIL"
            print(f"[FAIL] {name}: {type(exc).__name__}", flush=True)
            return None

    if platform.python_version() != (ROOT / ".python-version").read_text(encoding="utf-8").strip():
        raise base.ValidationFailure("selected project Python version mismatch")
    gate("repository boundaries", repository_boundaries)
    history = historical_scope(args.baseline, before, args.baseline_sha256)
    report["historical_scope"] = history
    report["stages"]["implementation scope"] = history["status"]
    if "scope" in history:
        report["implementation_scope"] = history["scope"]
    failed |= history["status"] == "FAIL"
    incomplete |= history["status"] == "INCOMPLETE"
    print(f"[{history['status']}] original implementation scope", flush=True)
    session = current_session_scope(args.session_baseline, before, args.session_baseline_sha256)
    report["current_session_scope"] = session
    failed |= session["status"] == "FAIL"
    incomplete |= session["status"] == "INCOMPLETE"
    with tempfile.TemporaryDirectory(prefix="fwp01-validation-") as temporary:
        temp_root = Path(temporary)
        gate("FWP01 focused suite", lambda:
             base._pytest_gate("FWP01 focused", temp_root, runner, "tests/fwp01"))
        report["scenario_sha256"] = gate("scenario determinism matrix", scenario_matrix)
        report["v2_scenario_sha256"] = gate("V2 scenario determinism matrix", lambda: scenario_matrix("v2"))
        # The unchanged Prompt-08 full validator composes 01-07, one full suite,
        # all component/scenario gates, lint and a no-update public snapshot.
        gate("Prompt-01 through Prompt-08 full composition", lambda: graph.validate("full"))
    gate("final repository boundaries", repository_boundaries)
    after = inventory()
    preservation = compare_baseline(before, after)
    report["validation_preservation"] = preservation
    report["inventory_after_errors"] = after["errors"]
    if preservation["unauthorized"] or preservation["deleted"] or not preservation["git_preserved"]:
        failed = True
    incomplete |= bool(after["errors"])
    report["overall"] = "FAIL" if failed else "INCOMPLETE" if incomplete else "PASS"
    if args.report:
        target = Path(args.report).resolve()
        temporary_root = Path(tempfile.gettempdir()).resolve()
        temporary = target.is_relative_to(temporary_root) and not target.is_relative_to(ROOT)
        governed = target.parent == EVIDENCE.resolve() and target.suffix == ".log"
        if not (temporary or governed):
            raise base.ValidationFailure("report must use temporary storage or the governed V2 evidence folder")
        if governed and (git("ls-files", "--", target.relative_to(ROOT).as_posix()).strip() or
                subprocess.run(("git", "check-ignore", "-q", "--", str(target)), cwd=ROOT).returncode):
            raise base.ValidationFailure("private validation evidence must remain ignored and untracked")
        target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("FWP01_VALIDATION: " + report["overall"], flush=True)
    for item in after["errors"]:
        print(f"[UNVERIFIED] {item['path']} ({item['error']})", flush=True)
    return 1 if failed else 2 if incomplete else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", help="Original pinned implementation inventory; absent evidence makes validation INCOMPLETE")
    parser.add_argument("--baseline-sha256", help="Optional additional checksum; cannot replace the pinned original digest")
    parser.add_argument("--session-baseline", help="Separate current-session inventory; never historical proof")
    parser.add_argument("--session-baseline-sha256", help="Checksum captured before implementation")
    parser.add_argument("--report")
    try:
        return validate(parser.parse_args())
    except (OSError, ValueError, base.ValidationFailure) as exc:
        print("FWP01_VALIDATION: FAIL (" + type(exc).__name__ + ")", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
