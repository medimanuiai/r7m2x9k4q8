"""Fresh-process/hash-seed/CWD determinism gate for the explicit WP17 manifest."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from tests.wp17.scenario_manifest import SCENARIO_ORDER


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tests" / "wp17" / "scenario_manifest.py"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def test_manifest_matches_across_repeats_processes_hash_seeds_and_safe_cwds(tmp_path):
    fixed_paths = (
        ROOT / "tests" / "reports" / "artifacts" / "rule_traces.json",
        ROOT / "tests" / "reports" / "artifacts" / "career_rule_traces.json",
        ROOT / "tests" / "reports" / "coverage_report.json",
    )
    before = {
        path: path.read_bytes() if path.exists() else None for path in fixed_paths
    }
    dimensions = (
        ("seed-1-cwd-a", "1", "cwd-a"),
        ("seed-8675309-cwd-a", "8675309", "cwd-a"),
        ("seed-1-cwd-b", "1", "cwd-b"),
        ("seed-8675309-cwd-b", "8675309", "cwd-b"),
    )
    outputs = []
    for label, seed, cwd_name in dimensions:
        cwd = tmp_path / cwd_name
        cwd.mkdir(exist_ok=True)
        artifact_dir = tmp_path / "artifacts" / label
        environment = os.environ.copy()
        environment.update(
            {
                "NDASTRO_USE_SRTM": "0",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": seed,
                "PYTHONPATH": str(ROOT),
            }
        )
        completed = subprocess.run(
            (
                sys.executable,
                str(RUNNER),
                "--artifact-dir",
                str(artifact_dir),
                "--repeats",
                "2",
            ),
            cwd=cwd,
            env=environment,
            capture_output=True,
            check=True,
        )
        assert completed.stderr == b""
        outputs.append(completed.stdout)

    assert len(set(outputs)) == 1
    payload = outputs[0]
    manifest = json.loads(payload)
    assert manifest["manifest_version"] == "1.0.0"
    assert tuple(item["name"] for item in manifest["scenarios"]) == SCENARIO_ORDER
    assert all(item["logical_byte_length"] > 0 for item in manifest["scenarios"])
    assert all(SHA256.fullmatch(item["logical_sha256"]) for item in manifest["scenarios"])
    assert payload.endswith(b"\n")
    assert b"\r" not in payload
    assert str(ROOT).encode("utf-8") not in payload
    assert manifest["scenarios"][5] == {
        "logical_byte_length": 532,
        "logical_sha256": "697e4e4dd7d5b383572b24449e713078f17ab135afa1fd6c202752eb6304cb4e",
        "name": "06.yoga.explicit_permutations",
        "public_byte_length": 527,
        "public_sha256": "1c49e3aa9c25d67b39681980c335ab9dc7287a22c6cfb6c666a5651c6df29f5f",
    }
    assert (len(payload), hashlib.sha256(payload).hexdigest()) == (
        1899,
        "06330b43cac062239e0670d1e48ab00c328ee270af64023b2017b819dc7b3017",
    )
    assert {
        path: path.read_bytes() if path.exists() else None for path in fixed_paths
    } == before
