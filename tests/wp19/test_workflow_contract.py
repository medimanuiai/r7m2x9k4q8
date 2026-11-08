from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_blocking_workflow_is_safe_single_python_and_authoritative():
    path = ROOT / ".github/workflows/ci.yaml"
    text = path.read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    assert 'strategy' not in workflow['jobs']['validate']
    assert text.count("runs-on: windows-latest") == 2
    assert "ubuntu-latest" not in text
    assert "shell: pwsh" in text
    assert "python-version-file: '.python-version'" in text
    assert (ROOT / '.python-version').read_text(encoding='utf-8').strip() == '3.11.9'
    assert 'matrix' not in text
    assert '3.14' not in text
    assert "requirements-stage01.lock.txt" in text
    assert "python tools/validate_prompt03.py full" in text
    assert "python tools/validate_prompt05.py full" in text
    assert "python tools/validate_prompt02.py full" not in text
    assert "python tools/validate_prompt01.py full" not in text
    assert "Prompt-03 required gate" in text
    assert "$env:VALIDATION_RESULT -ne 'success'" in text
    for forbidden in (
        "|| true",
        "continue-on-error",
        "upload-artifact",
        "GITHUB_TOKEN",
        "create_snapshot_pr",
        "--update",
        "tests/reports",
        "-n auto",
        'test "$VALIDATION_RESULT"',
    ):
        assert forbidden not in text


def test_snapshot_workflow_uses_lock_and_explicit_temporary_output():
    path = ROOT / ".github/workflows/parasara-snapshot-compare.yml"
    text = path.read_text(encoding="utf-8")
    assert yaml.safe_load(text)
    assert "runs-on: windows-latest" in text
    assert "ubuntu-latest" not in text
    assert "shell: pwsh" in text
    assert "python-version-file: '.python-version'" in text
    assert 'matrix' not in text
    assert '3.14' not in text
    assert "requirements-stage01.lock.txt" in text
    assert "$env:PYTHONPATH = '.'" in text
    assert "$snapshotOutput = Join-Path $env:RUNNER_TEMP" in text
    assert "--out $snapshotOutput" in text
    assert "PYTHONPATH=." not in text
    assert "upload-artifact" not in text
    assert "GITHUB_TOKEN" not in text
