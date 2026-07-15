# Parāśara Testing Guide

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-13

## Scope

The repository contains system-level Parāśara tests under `systems/Parasara/tests`, cross-system tests under `tests`, golden snapshots, property and determinism checks, coverage instrumentation, and snapshot tooling.

This guide describes where those layers live. It does not claim that the complete suite currently passes.

## Test layers

- Adapter, normalization, derived-state, rule-runtime, Career, and vertical-slice tests: `systems/Parasara/tests/`.
- PredicateResult tests: `tests/rules/test_predicate_result.py`.
- Dasha tests: `tests/dasha/`.
- Aspect, varga, strength, Yoga, and functional-role tests: `tests/enrichments/`.
- Property and determinism checks: `tests/property_tests.py` and `tests/determinism_test.py`.
- Shared testing utilities: `tests/testing_framework/`.
- Approved and generated Parāśara snapshots share `systems/Parasara/tests/snapshots/`; approval must be established by workflow/evidence, not inferred from directory placement.

## Targeted test commands

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH='.'
python -m pytest systems/Parasara/tests
python -m pytest tests/rules/test_predicate_result.py
```

These commands execute project code. Pytest and Python may write `.pytest_cache`, `__pycache__`, temporary files, or plugin artifacts. They are non-destructive test commands, not strictly read-only inspection.

To reduce repository-local test artifacts during a constrained targeted run:

```powershell
$env:PYTHONPATH='.'
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest -p no:cacheprovider tests/rules/test_predicate_result.py
```

Use the repository's configured Python environment when required. Do not install packages merely to run a documentation check or read-only audit.

## Read-only audits

Read-only audits may search and inspect source/tests but must not execute pytest unless the audit instructions explicitly permit test execution. They must not run snapshot generators, report generators, approval helpers, formatters, or dependency installation.

## Mutating workflows

Snapshot generators and approval tools write files. Do not run them during read-only audits or ordinary test verification.

Relevant mutating tools include `systems/Parasara/tools/generate_snapshot.py`, `tests/testing_framework/approve_snapshot.py`, and snapshot PR/signoff helpers.

Additional effects to note:

- `systems/Parasara/tools/ci_snapshot_check.py` writes `tmp_generated_snapshot.json` in the repository root unless `--out` is supplied.
- `systems/Parasara/tools/surya_to_parasara.py` writes a chart and can also write a generated snapshot.
- The vertical-slice pytest writes generated JSON under pytest's temporary directory rather than the approved snapshot path.
- Coverage and full-report helpers write under `tests/reports/` or their configured destination.

Snapshot changes require deliberate review; never auto-approve broad drift after an internal contract migration.

## Acceptance boundaries

- A test file's presence does not prove it passes.
- A passing unit test does not establish classical or astronomical correctness.
- Scientific validation, SME approval, deterministic replay, schema validation, and regression stability are separate gates.
- Full-repository tests may require optional system dependencies; stage prompts must record the exact commands actually executed.
- Snapshot equality is regression evidence, not proof that the approved snapshot is astrologically correct.

## Current CI behavior

- `.github/workflows/ci.yaml` installs development dependencies, runs the repository test suite, and then runs coverage/report and snapshot-PR helpers with failures suppressed for those helper commands.
- `.github/workflows/parasara-snapshot-compare.yml` runs a blocking comparison against `output_golden_chart_01.json` for relevant changes.
- No active workflow step was verified for `tools/rules_lint.py`.

## Makefile limitations

`systems/Parasara/Makefile` is not a complete canonical command interface:

- `validate-schemas` installs dependencies and is therefore environment-changing;
- its repository-relative paths require verification when invoked with `make -C systems/Parasara`;
- `test` covers only `systems/Parasara/tests`;
- `snapshot` currently prints `No snapshots implemented yet` even though snapshot tooling exists elsewhere.

Prefer explicit commands documented here until the Makefile is corrected and verified.

## Stage guidance

Stage-specific audits and implementation prompts define their own permitted commands and required evidence. This guide must not duplicate live audit filenames or transient completion status.
