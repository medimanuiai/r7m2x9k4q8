"""Independent processes/hash seeds/CWD and unchanged public contract pins."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SCENARIO_SHA256 = "045d41542a85f2b8b0c327425ac889250b0cf2162c8406f117b8ea4cc8e472b3"
EXPECTED_V1_CORPUS_SHA256 = {
    "systems/Parasara/rules/parashara/v1/README.md": "ecd93c11df1f9a5ac720ebb28c44efb5b5671e0349bf4893bf442211b975707b",
    "systems/Parasara/rules/parashara/v1/calibration.json": "3aad2198cd1de8929db71c8f4e56a13238519259a271490707edb8030334e4ec",
    "systems/Parasara/rules/parashara/v1/derived_rules.yml": "c46f9616ac5e25b6f4ed73f453212ec86e81558f43c5c3984333a45dd38ad854",
    "systems/Parasara/rules/parashara/v1/m1_rules.yaml": "1cef3e2b030b67fb29db484225f6a542dc5620605d805ebb240ba1aa98775a52",
    "systems/Parasara/rules/parashara/v1/macros.yaml": "1652f9b31b673dee6162be5134b7580c34284fa58d99a078ae08b86c9226fceb",
    "systems/Parasara/rules/parashara/v1/primitives.yml": "644022b548cd04b9a7f5bd4b7a36cbd2f1b6cbf8348e520d5a3bd9cdc1da1a8f",
    "systems/Parasara/rules/parashara/v1/yogas.yaml": "861f4da0de228f2b61f37936475ae5bc39b701654f19b76994d6fa5dfab2ab82",
}


def _assert_exact_bytes(actual, expected):
    assert actual == expected


@pytest.mark.parametrize("seed", ["0", "1", "12345"])
def test_scenario_independent_process_seed_and_cwd(tmp_path, seed):
    result = subprocess.run([sys.executable, str(ROOT / "tests/graph/scenario_manifest.py")],
        cwd=tmp_path if seed != "0" else ROOT,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED=seed), capture_output=True, check=True)
    assert not result.stderr
    assert hashlib.sha256(result.stdout).hexdigest() == EXPECTED_SCENARIO_SHA256


def test_preserved_dsl_scenario_and_current_v1():
    from tools.validate_prompt07 import _current_v1_exact, EXPECTED_PROMPT07_SCENARIO_SHA256
    _current_v1_exact()
    result = subprocess.run([sys.executable, str(ROOT / "tests/dsl/scenario_manifest.py")],
        cwd=ROOT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), capture_output=True, check=True)
    assert hashlib.sha256(result.stdout).hexdigest() == EXPECTED_PROMPT07_SCENARIO_SHA256
    prefix = "systems/Parasara/rules/parashara/v1/"
    tracked = set(filter(None, subprocess.check_output(
        ["git", "ls-files", "-z", "--", prefix], cwd=ROOT).decode().split("\0")))
    assert tracked == set(EXPECTED_V1_CORPUS_SHA256)
    for relative, expected in EXPECTED_V1_CORPUS_SHA256.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected


@pytest.mark.parametrize(("approved", "changed"), (
    (b"alpha\nbeta\n", b"alpha\r\nbeta\r\n"),
    (b"alpha\r\nbeta\r\n", b"alpha\nbeta\n"),
    (b"alpha\nbeta\n", b"\xef\xbb\xbfalpha\nbeta\n"),
    (b"alpha\nbeta\n", b"alpha \nbeta\n"),
    (b"alpha\nbeta\n", b"alpha\n# comment\nbeta\n"),
))
def test_protected_corpus_rejects_every_byte_only_change(approved, changed):
    with pytest.raises(AssertionError):
        _assert_exact_bytes(changed, approved)


def test_runtime_dependency_trace_identity_and_ordered_view(graph_pack):
    from systems.Parasara.engine.rules.graph.runtime_contract import digest
    from systems.Parasara.engine.rules.rule_engine import RuleEngine
    from tests.graph.conftest import document, dsl_payload
    from tests.graph.test_runtime_outcomes import execute
    _, authority, _, _, plan = graph_pack(document(edges=[(2, 0, "optional_supports"), (1, 3, "optional_supports")]),
        payload=dsl_payload().replace(b"priority: 0", b"priority: 99", 1))
    record = execute(authority, plan)[0].record
    assert tuple(t.execution_ordinal for t in record.traces) == (2, 0, 1, 3)
    assert record.ordered_matches == RuleEngine.order_matches(record.matches)
    assert record.ordered_matches[0].rule_id == "synthetic.a"
    for i, trace in enumerate(record.traces):
        assert trace.trace_id == "graph." + digest(dict(contract="rule-dependency-trace@1.0.0",
            plan_sha256=plan.plan_sha256, source_order=i, snapshot_sha256=record.snapshot_sha256,
            context_sha256=record.context_sha256))
