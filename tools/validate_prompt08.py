#!/usr/bin/env python3
"""Non-mutating Prompt-08 acceptance, composed with all predecessor gates."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import validate_prompt01 as base
from tools import validate_prompt07 as previous
from tests.graph.test_determinism_compatibility import EXPECTED_SCENARIO_SHA256

RELEVANT_IGNORED = (
    previous.PRIVATE_TRACKER_RELATIVE,
    "systems/Parasara/tests/snapshots/generated_surya_parasara_output.json",
    "systems/Parasara/tests/snapshots/generated_vertical_slice_career.json",
    "systems/SuryaSiddhanta/ndastro_engine/data/ephemeris/de440t.bsp",
    ".git/info/exclude",
)


def _git(*args):
    return subprocess.check_output(("git", *args), cwd=ROOT)


def inventory():
    names = set(filter(None, _git("ls-files", "-z", "--cached", "--others", "--exclude-standard").decode("utf-8").split("\0")))
    names.update(RELEVANT_IGNORED)
    hashes = {}
    for name in sorted(names):
        path = ROOT / name
        if path.is_file():
            with path.open("rb") as stream:
                hashes[name] = hashlib.file_digest(stream, "sha256").hexdigest()
        elif not path.is_dir():
            hashes[name] = None
    return dict(hashes=hashes, head=_git("rev-parse", "HEAD").decode().strip(),
        branch=_git("branch", "--show-current").decode().strip(),
        branches=_git("for-each-ref", "--format=%(refname):%(objectname)", "refs/heads").decode(),
        index=hashlib.sha256(_git("ls-files", "--stage", "-z")).hexdigest(),
        staged=_git("diff", "--cached", "--name-status").decode())


def signature(state):
    return hashlib.sha256(json.dumps(state["hashes"], sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def _runner(argv, **kwargs):
    result = subprocess.run(argv, **kwargs)
    if result.returncode:
        print(result.stdout.decode("utf-8", "replace")[-20000:] if result.stdout else "", flush=True)
    elif "pytest" in argv:
        text = result.stdout.decode("utf-8", "replace")
        summaries = [line for line in text.splitlines() if re.search(r"\d+ (passed|(?:tests? )?collected|skipped)", line)]
        if not summaries:
            raise base.ValidationFailure("pytest did not report acceptance counts")
        print("  pytest_summary=" + summaries[-1].strip("= "), flush=True)
    return result


def boundaries():
    previous._repository_boundaries(_runner)
    patterns = [line.strip() for line in (ROOT / ".git/info/exclude").read_text().splitlines()
                if line.strip() and not line.startswith("#")]
    if patterns != [previous.PRIVATE_TRACKER_RELATIVE]:
        raise base.ValidationFailure("local exclusion must name only the private tracker")
    sources = [p.relative_to(ROOT).as_posix() for root in ("systems/Parasara/engine/rules/graph", "tests/graph")
               for p in (ROOT / root).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    ignored = subprocess.run(("git", "check-ignore", "--stdin"), cwd=ROOT,
        input=("\n".join(sources) + "\n").encode(), capture_output=True)
    if ignored.returncode != 1 or ignored.stdout:
        raise base.ValidationFailure("graph implementation must not be hidden by ignore rules")
    if _git("diff", "--cached", "--name-only").strip() or _git("diff", "--name-only", "--diff-filter=D").strip():
        raise base.ValidationFailure("staging/deletion boundary")
    prepared = "systems/Parasara/engine/rules/prepared_state.py"
    if (ROOT / prepared).read_bytes().replace(b"\r\n", b"\n") != _git("show", "HEAD:" + prepared).replace(b"\r\n", b"\n"):
        raise base.ValidationFailure("prepared_state logical preservation")


def component():
    from systems.Parasara.engine.rules.graph.compiler import (
        GRAPH_COMPILER_CONTENT_SHA256, GRAPH_COMPILER_IMPLEMENTATION_MODULE_IDS,
        compiler_component_fingerprint_sha256,
    )
    from systems.Parasara.engine.rules.graph.runtime_contract import GRAPH_CONTRACT_SHA256
    sources = {name: (ROOT / "systems/Parasara/engine/rules" / name).read_bytes()
               for name in GRAPH_COMPILER_IMPLEMENTATION_MODULE_IDS}
    if compiler_component_fingerprint_sha256(sources) != GRAPH_COMPILER_CONTENT_SHA256:
        raise base.ValidationFailure("graph component implementation fingerprint")
    print(f"[PASS] graph_component_sha256={GRAPH_COMPILER_CONTENT_SHA256} contract_sha256={GRAPH_CONTRACT_SHA256}", flush=True)


def scenario():
    with tempfile.TemporaryDirectory(prefix="prompt08-cwd-") as temporary:
        for seed in ("0", "1", "12345"):
            environment = base._environment()
            environment["PYTHONHASHSEED"] = seed
            result = _runner((sys.executable, str(ROOT / "tests/graph/scenario_manifest.py")),
                cwd=ROOT if seed == "0" else temporary, env=environment,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            observed = hashlib.sha256(result.stdout).hexdigest()
            if result.returncode or result.stderr or observed != EXPECTED_SCENARIO_SHA256:
                raise base.ValidationFailure("graph scenario process/hash-seed/CWD identity")
    print(f"[PASS] prompt08_scenario_sha256={EXPECTED_SCENARIO_SHA256} platform={platform.system()}", flush=True)


def validate(mode):
    before = inventory()
    print(f"Prompt-08 mode={mode} python={platform.python_version()} platform={platform.system()} files={len(before['hashes'])} worktree_sha256={signature(before)}", flush=True)
    failed = False
    try:
        if sys.version_info[:2] not in ((3, 11), (3, 14)):
            raise base.ValidationFailure("required Python lane")
        if before["branch"] != "main" or before["head"] != "ec6b49a164389aada4e741561d75cb866527e6cf" or before["staged"]:
            raise base.ValidationFailure("implementation branch/HEAD/index boundary")
        component()
        boundaries()
        with tempfile.TemporaryDirectory(prefix="prompt08-validation-") as temporary:
            base._pytest_gate("Prompt-08 focused contracts", Path(temporary), _runner, "tests/graph")
            scenario()
            # Prompt-07 composes all earlier contracts, scenarios, collection,
            # full suite, lint and strict snapshot without a second full run.
            if previous.validate(mode, runner=_runner):
                raise base.ValidationFailure("composed Prompt-01 through Prompt-07 gates")
            if mode == "focused":
                base._snapshot(Path(temporary), _runner)
        boundaries()
    except (OSError, subprocess.SubprocessError, base.ValidationFailure) as exc:
        print(f"[FAIL] {exc}", flush=True)
        failed = True
    after = inventory()
    print(f"worktree_after_sha256={signature(after)}", flush=True)
    if before != after:
        changed = sorted(k for k in before["hashes"].keys() | after["hashes"].keys() if before["hashes"].get(k) != after["hashes"].get(k))
        print(f"[FAIL] byte or Git state mutation: {changed}", flush=True)
        failed = True
    else:
        print("[PASS] every inventoried byte, branch, HEAD, index and exclusion preserved", flush=True)
    print("PROMPT_08_VALIDATION: " + ("FAILED" if failed else "COMPLETE"), flush=True)
    return int(failed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("focused", "full"), default="full")
    return validate(parser.parse_args(argv).mode)


if __name__ == "__main__":
    raise SystemExit(main())
