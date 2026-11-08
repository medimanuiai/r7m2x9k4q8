"""Exact protected public bytes and retained predecessor identities."""
from pathlib import Path
import hashlib
import json
from copy import deepcopy

import pytest

from systems.Parasara.tools.generate_snapshot import generate

ROOT = Path(__file__).resolve().parents[2]


def test_protected_snapshot_generation_and_prepared_module_bytes(tmp_path):
    output = tmp_path / "snapshot.json"
    generate(str(ROOT / "systems/Parasara/fixtures/golden_chart_01.json"), str(output))
    expected = ROOT / "systems/Parasara/tests/snapshots/output_golden_chart_01.json"
    assert output.read_bytes() == expected.read_bytes()
    assert len(output.read_bytes()) == 4041
    assert hashlib.sha256(output.read_bytes()).hexdigest() == "da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af"
    prepared = ROOT / "systems/Parasara/engine/rules/prepared_state.py"
    assert hashlib.sha256(prepared.read_bytes()).hexdigest() == "a2fca2dd17edd7092e8bee1cc8431891400d09f979a90f4f44d17b71c9466970"


@pytest.fixture
def historical_inventory(tmp_path, monkeypatch):
    from tools import validate_fwp01 as validator
    initial = dict(hashes={"authorized.py": "before", "unrelated.md": "unchanged"}, errors=[],
        head="head", branch="main", branches="refs", index="index", staged="")
    payload = json.dumps(initial, sort_keys=True).encode()
    path = tmp_path / "original.json"
    path.write_bytes(payload)
    # Supply a fixture trust anchor, independently of the caller's optional
    # checksum. Production is anchored to the real original evidence digest.
    monkeypatch.setattr(validator, "ORIGINAL_BASELINE_SHA256", hashlib.sha256(payload).hexdigest())
    monkeypatch.setattr(validator, "allowed_paths", lambda: {"authorized.py"})
    return validator, initial, path


def test_missing_historical_inventory_is_explicitly_incomplete(historical_inventory):
    validator, current, _ = historical_inventory
    result = validator.historical_scope(None, current)
    assert result["status"] == "INCOMPLETE"
    assert result["issues"] == ["original_baseline_missing"]
    assert "scope" not in result


def test_invalid_unreadable_and_replacement_baselines_cannot_pass(historical_inventory, monkeypatch):
    validator, current, path = historical_inventory
    original_read = Path.read_bytes
    def denied(target):
        if target == path:
            raise PermissionError("private path must not appear")
        return original_read(target)
    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", denied)
        result = validator.historical_scope(path, current)
        assert result == dict(status="FAIL", issues=["original_baseline_unreadable"])
    path.write_bytes(b"{")
    assert validator.historical_scope(path, current)["status"] == "FAIL"
    # Even a matching caller-provided checksum cannot authorize a new baseline.
    replacement = json.dumps(current, indent=2).encode()
    path.write_bytes(replacement)
    result = validator.historical_scope(path, current, hashlib.sha256(replacement).hexdigest())
    assert result == dict(status="FAIL", issues=["original_baseline_hash_mismatch"])


def test_historical_scope_allows_authorized_changes_but_rejects_unrelated_change(historical_inventory):
    validator, initial, path = historical_inventory
    current = deepcopy(initial)
    current["hashes"]["authorized.py"] = "after"
    result = validator.historical_scope(path, current)
    assert result["status"] == "PASS"
    assert result["scope"]["changed"] == ["authorized.py"]
    current["hashes"]["unrelated.md"] = "unauthorized historical change"
    result = validator.historical_scope(path, current)
    assert result["status"] == "FAIL"
    assert result["scope"]["unauthorized"] == ["unrelated.md"]


def test_original_unreadable_entry_remains_unverified_after_a_later_read(historical_inventory, monkeypatch):
    validator, initial, path = historical_inventory
    initial["errors"] = [dict(path="historical.docx", error="PermissionError")]
    payload = json.dumps(initial, sort_keys=True).encode()
    path.write_bytes(payload)
    monkeypatch.setattr(validator, "ORIGINAL_BASELINE_SHA256", hashlib.sha256(payload).hexdigest())
    current = deepcopy(initial)
    current["errors"] = []
    current["hashes"]["historical.docx"] = "new session hash cannot prove historical preservation"
    result = validator.historical_scope(path, current)
    assert result["status"] == "INCOMPLETE"
    assert result["scope"]["unreadable"] == ["historical.docx"]
    assert result["scope"]["changed"] == []


def test_current_session_preservation_does_not_replace_missing_history(historical_inventory, monkeypatch):
    validator, initial, path = historical_inventory
    monkeypatch.setattr(validator, "v2_allowed_paths", lambda: {"authorized.py"})
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    current = deepcopy(initial)
    current["hashes"]["authorized.py"] = "V2 implementation"
    result = validator.current_session_scope(path, current, digest)
    assert result["status"] == "PASS" and result["historical_preservation"] == "UNVERIFIED"
    assert validator.historical_scope(None, current)["status"] == "INCOMPLETE"
    current["hashes"]["unrelated.md"] = "unauthorized"
    assert validator.current_session_scope(path, current, digest)["status"] == "FAIL"
    assert validator.current_session_scope(path, current, "0" * 64)["status"] == "FAIL"
