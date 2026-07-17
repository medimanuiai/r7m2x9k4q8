from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_blocking_workflow_is_safe_dual_lane_and_authoritative():
    path = ROOT / ".github/workflows/ci.yaml"
    text = path.read_text(encoding="utf-8")
    assert yaml.safe_load(text)
    assert "python-version: ['3.11', '3.14']" in text
    assert "requirements-stage01.lock.txt" in text
    assert "python tools/validate_prompt01.py full" in text
    assert "Prompt-01 required gate" in text
    for forbidden in (
        "|| true",
        "continue-on-error",
        "upload-artifact",
        "GITHUB_TOKEN",
        "create_snapshot_pr",
        "--update",
        "tests/reports",
        "-n auto",
    ):
        assert forbidden not in text


def test_snapshot_workflow_uses_lock_and_explicit_temporary_output():
    path = ROOT / ".github/workflows/parasara-snapshot-compare.yml"
    text = path.read_text(encoding="utf-8")
    assert yaml.safe_load(text)
    assert "requirements-stage01.lock.txt" in text
    assert "--out \"$RUNNER_TEMP/parasara-snapshot.json\"" in text
    assert "upload-artifact" not in text
    assert "GITHUB_TOKEN" not in text
