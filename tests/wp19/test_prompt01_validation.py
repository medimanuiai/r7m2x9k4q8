from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from tools import validate_prompt01


def _result(returncode=0, stdout=b""):
    return subprocess.CompletedProcess(("command",), returncode, stdout=stdout)


def test_pytest_command_uses_current_interpreter_and_isolated_options(tmp_path):
    command = validate_prompt01.pytest_command(
        tmp_path / "pytest", "tests/wp17", collect_only=True
    )
    assert command[0] == sys.executable
    assert command[1:4] == ("-m", "pytest", "-q")
    assert ("-o", "addopts=") == command[4:6]
    assert ("-p", "no:cacheprovider") == command[6:8]
    assert command[8:10] == ("--basetemp", str(tmp_path / "pytest"))
    assert command[-2:] == ("--collect-only", "tests/wp17")


def test_environment_is_bounded(monkeypatch):
    monkeypatch.setenv("PYTHONPATH", "unsafe")
    environment = validate_prompt01._environment()
    assert environment["PYTHONDONTWRITEBYTECODE"] == "1"
    assert environment["PYTHONPATH"] == "."
    assert environment["NDASTRO_USE_SRTM"] == "0"


def test_command_failure_propagates_without_child_payload(capsys):
    payload = (
        b"C:\\Users\\person\\chart.json TOKEN=secret "
        b'raw_chart={"birth_time":"private"}'
    )

    def runner(*_args, **_kwargs):
        return _result(7, payload)

    with pytest.raises(validate_prompt01.ValidationFailure):
        validate_prompt01._execute(
            validate_prompt01.Command("bounded failure", ("ignored",)), runner
        )
    output = capsys.readouterr().out
    assert output == "[FAIL] bounded failure (exit 7)\n"
    assert "secret" not in output
    assert "chart" not in output


def test_snapshot_command_requires_unique_explicit_out(tmp_path, monkeypatch):
    approved = (
        validate_prompt01.ROOT
        / "systems/Parasara/tests/snapshots/output_golden_chart_01.json"
    ).read_bytes()
    seen = {}

    def runner(argv, **_kwargs):
        seen["argv"] = tuple(argv)
        out = Path(argv[argv.index("--out") + 1])
        out.write_bytes(approved)
        return _result(0, b"Snapshots match\n")

    digest = validate_prompt01._snapshot(tmp_path, runner)
    assert "--out" in seen["argv"]
    assert "tmp_generated_snapshot.json" not in seen["argv"]
    assert "--update" not in seen["argv"]
    assert digest == validate_prompt01._sha256(approved)


def test_rule_lint_proves_each_supported_file_exactly_once():
    rules = (
        validate_prompt01.ROOT / "systems/Parasara/rules/parashara/v1"
    ).resolve()
    files = sorted(
        (
            path.resolve()
            for path in rules.rglob("*")
            if path.suffix.lower() in {".yml", ".yaml"}
        ),
        key=lambda path: str(path).casefold(),
    )
    output = "\n".join(f"Inspected rule file: {path}" for path in files).encode()

    def runner(*_args, **_kwargs):
        return _result(0, output)

    assert validate_prompt01._rule_lint(runner) == tuple(path.name for path in files)


def test_supported_modes_are_explicit():
    with pytest.raises(SystemExit) as raised:
        validate_prompt01.main(["unknown"])
    assert raised.value.code == 2
