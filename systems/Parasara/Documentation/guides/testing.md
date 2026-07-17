# Parāśara Testing Guide

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-17

## Scope

The repository contains system-level Parāśara tests under `systems/Parasara/tests`, cross-system tests under `tests`, golden snapshots, property and determinism checks, coverage instrumentation, and snapshot tooling.

This guide describes the implemented Prompt-01 validation boundary and the
remaining test layers. WP19 contains the dated complete-suite evidence; it is
not scientific, release, privacy, or publication approval.

## Test layers

- Adapter, normalization, derived-state, rule-runtime, Career, and vertical-slice tests: `systems/Parasara/tests/`.
- PredicateResult tests: `tests/rules/test_predicate_result.py`.
- Dasha tests: `tests/dasha/`.
- Aspect, varga, strength, Yoga, and functional-role tests: `tests/enrichments/`.
- Property and determinism checks: `tests/property_tests.py` and `tests/determinism_test.py`.
- Shared testing utilities: `tests/testing_framework/`.
- Approved and generated Parāśara snapshots share `systems/Parasara/tests/snapshots/`; approval must be established by workflow/evidence, not inferred from directory placement.

## Authoritative Stage-01 command

From repository root in either supported Python environment:

```text
python tools/validate_prompt01.py full
```

This is the authoritative Prompt-01 gate. It uses the current interpreter,
resets subprocesses to repository root, sets `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONPATH=.`, and `NDASTRO_USE_SRTM=0`, disables configured parallel addopts
and pytest cache, and uses unique OS-temporary output paths. It fails on the
first failed gate and never retries in a weaker mode.

Full mode runs import/version smoke, ordered collection reporting, WP17
architecture/safety enforcement, complete pytest, the explicit WP17 manifest
(including Yoga permutations and loader orders), exact supported-file rule
lint, strict no-update snapshot bytes, and protected artifact/worktree checks.
WP18 performance remains dated descriptive evidence, not a blocking threshold.

Python 3.11 is the baseline lane and Python 3.14 is the forward lane. Both must
pass with identical collection and contractual hashes. Hosted CI pins the
minor versions and prints the resolved patch version; it does not claim local
patch identity.

## Focused developer commands

From the repository root in PowerShell:

```powershell
python tools/validate_prompt01.py focused
```

For a single module, preserve the same isolation pattern:

```powershell
$env:PYTHONPATH='.'
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest -q -o addopts= -p no:cacheprovider --basetemp <unique-os-temp> <test-path>
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

`.github/workflows/ci.yaml` installs the WP00 Stage-01 lock plus editable
SuryaSiddhanta without dependencies and runs the authoritative full command in
Python 3.11 and 3.14. It has no fallback, snapshot update, credentialed
mutation, report-tree upload, or failure suppression. The aggregate check is
`Prompt-01 Stage-01 / Prompt-01 required gate`.

`.github/workflows/parasara-snapshot-compare.yml` is supplemental. It uses the
same lock and an explicit runner-temporary `--out`; it publishes nothing.

## Makefile limitations

`systems/Parasara/Makefile` is not a complete canonical command interface:

- `validate-schemas` installs dependencies and is therefore environment-changing;
- its repository-relative paths require verification when invoked with `make -C systems/Parasara`;
- `test` covers only `systems/Parasara/tests`;
- `snapshot` currently prints `No snapshots implemented yet` even though snapshot tooling exists elsewhere.

Prefer the authoritative command documented here until the Makefile is
separately corrected and verified.

## Stage guidance

The two optional full-suite skips are recorded capability/environment skips,
not failures or production-readiness evidence. Logical hashes exclude permitted
telemetry. Snapshot equality is compatibility evidence only. WP18 performance
does not prove historical no-regression.
