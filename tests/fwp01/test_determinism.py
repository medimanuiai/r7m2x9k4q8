"""Canonical bytes independent of mutation, ordering, CWD and hash seed."""
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

from tests.fwp01.scenario_manifest import scenario_bytes, scenario_bytes_v2
from tests.fwp01.test_input_contract import strict_payload, strict_snapshot

EXPECTED_SCENARIO_SHA256 = "7a647689108173e5ef3a7344439506a4d65dabb26a24d5ef2b23eb9d2fe117da"
EXPECTED_V2_SCENARIO_SHA256 = "9c9838fba6ce3ad54b5ecd495740369a7aacb548142682a6b55a456e946e895c"


def test_input_identity_and_mapping_order_do_not_change_logical_bytes():
    data = strict_payload()
    expected = strict_snapshot(data).logical_digest
    reordered = deepcopy(data)
    reordered["planets"].reverse()
    reordered = dict(reversed(list(reordered.items())))
    assert strict_snapshot(reordered).logical_digest == expected


def test_manifest_executes_precision_routing_mutation_and_contract_conflict():
    manifest = json.loads(scenario_bytes())
    transitions = {row["source"]: row for row in manifest["precision"]["transitions"]}
    for boundary in (30.0 * i for i in range(1, 13)):
        assert {math.nextafter(boundary, 0.0), boundary, math.nextafter(boundary, math.inf)} <= transitions.keys()
    for value in (0.0, 29.99996, 13.33334, 3.33334, 359.99996):
        assert transitions[value]["planet"]["sidereal_longitude"] == value
        assert 0 <= transitions[value]["planet"]["degree"] < 30
    assert transitions[29.99996]["legacy_lagna"]["degree"] == 30.0
    assert transitions[360.0]["planet"]["sidereal_longitude"] == 0.0
    routing = manifest["routing"]
    assert [row["index"] for row in routing["strict_batch"]] == [0, 1, 2]
    assert routing["strict_batch"][1]["issues"] and routing["strict_batch"][1]["digest"] is None
    assert routing["strict_batch"][0]["digest"] == routing["strict_batch"][2]["digest"]
    assert routing["legacy_planets"] == 3 and routing["legacy_houses"] == 2
    mutation = manifest["mutation_and_projection"]
    assert mutation["mutable_input_isolated"]
    assert mutation["immutable_rejected"] == ["metadata", "graph"]
    assert mutation["predicate_contract_conflict"]
    assert all(row["status"] == "missing_capability" for row in mutation["predicates"])


def test_manifest_is_repeatable_and_cwd_hashseed_independent(tmp_path):
    expected = scenario_bytes()
    assert scenario_bytes() == expected
    script = Path(__file__).with_name("scenario_manifest.py").resolve()
    environment = dict(os.environ, PYTHONHASHSEED="42", PYTHONDONTWRITEBYTECODE="1", NDASTRO_USE_SRTM="0")
    result = subprocess.run([sys.executable, "-B", str(script)], cwd=tmp_path,
        env=environment, capture_output=True, check=True)
    assert not result.stderr
    assert result.stdout == expected
    assert hashlib.sha256(expected).hexdigest() == EXPECTED_SCENARIO_SHA256


def test_validator_keeps_seed_cwd_repetitions_on_current_interpreter(monkeypatch):
    from tools import validate_fwp01 as validator

    expected = scenario_bytes()
    calls = []

    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, stdout=expected, stderr=b"")

    monkeypatch.setattr(validator.subprocess, "run", run)
    assert validator.scenario_matrix() == EXPECTED_SCENARIO_SHA256
    assert len(calls) == 16
    assert {argv[0] for argv, _ in calls} == {sys.executable}
    assert {kwargs["env"]["PYTHONHASHSEED"] for _, kwargs in calls} == {"0", "1", "42", "random"}
    assert len({kwargs["cwd"] for _, kwargs in calls}) == 2


def test_separate_v2_oracle_runs_real_predicates_compiler_and_rule_engine():
    value = scenario_bytes_v2()
    assert hashlib.sha256(value).hexdigest() == EXPECTED_V2_SCENARIO_SHA256
    manifest = json.loads(value)
    assert [row["result"]["status"] for row in manifest["cases"]] == [
        "matched", "unmatched", "missing_capability", "missing_capability", "matched",
        "missing_capability", "unmatched", "missing_capability", "matched", "invalid_parameters"]
    assert manifest["expanded_depth_diagnostic"] == "P07E404_COMPILED_DIGEST_MISMATCH"
    assert manifest["unsupported_not"]["status"] == "missing_capability"
    assert [row["status"] for row in manifest["rule_matches"]] == ["matched", "missing_capability", "unmatched", "matched"]
    assert [row["route"] for row in manifest["edge_consistency"]] == ["preparation", "deserialization"]
    for row in manifest["edge_consistency"]:
        assert row["clean_rule"]["status"] == "unmatched"
        for mutation in ("forged_target", "unauthorized_offset"):
            assert row[mutation] == dict(readiness="malformed", issues=["aspect_coverage_contradictory"],
                rule=dict(status="missing_capability", errors=["malformed_capability"]))
        assert [result["status"] for result in row["wraparound"]] == ["matched", "matched"]


def test_validator_keeps_v2_seed_cwd_repetitions_on_current_interpreter(monkeypatch):
    from tools import validate_fwp01 as validator
    expected = scenario_bytes_v2()
    calls = []
    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, stdout=expected, stderr=b"")
    monkeypatch.setattr(validator.subprocess, "run", run)
    assert validator.scenario_matrix("v2") == EXPECTED_V2_SCENARIO_SHA256
    assert len(calls) == 16
    assert all(argv[0] == sys.executable and argv[-1] == "--v2" for argv, _ in calls)
    assert {kwargs["env"]["PYTHONHASHSEED"] for _, kwargs in calls} == {"0", "1", "42", "random"}
    assert len({kwargs["cwd"] for _, kwargs in calls}) == 2
