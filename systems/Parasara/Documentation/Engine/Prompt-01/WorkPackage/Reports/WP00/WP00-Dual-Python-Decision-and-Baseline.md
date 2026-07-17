# WP00 — Dual-Python Decision Record and Reproducible Baseline

**Date:** 2026-07-14  
**Verdict:** BLOCKED  
**Scope:** Environment, dependency, collection, baseline, rule-lint, and no-update snapshot evidence only  
**WP01 readiness:** NOT READY  
**WP02 readiness:** NOT READY

## 1. Executive outcome

WP00 established separate Python 3.14 and Python 3.11 virtual environments from one repository-owned dependency source. Interpreter isolation, required imports, editable local SuryaSiddhanta installation, dependency consistency, collection, targeted tests, safe baseline execution, rule lint, and no-update snapshot comparison are reproducible in both lanes.

The baseline is blocked. Python 3.14 and Python 3.11 produce the same four failures in the final non-mutating suite, the same two rule-lint failures, and byte-identical generated snapshots that differ from the approved snapshot. Because Python 3.11 is the current CI compatibility contract, WP01 and WP02 must not begin until these failures receive an explicitly approved disposition.

No production implementation, test assertion, rule, weight, astrology table, public schema, approved snapshot, golden file, or CI workflow was changed.

## 2. Repository and platform inspection

| Item | Observed value |
|---|---|
| Operating system | Microsoft Windows NT 10.0.26200.0 |
| Architecture | x64 OS, x64 process |
| Shell | Windows PowerShell 5.1.26100.8655 |
| Git branch | `main` |
| Initial working tree | dirty; 28 entries, all preserved as user state |
| Environment convention | `jyothishyam_env/`, ignored by `.gitignore:60` |
| Safe temporary location | unique paths below ignored `jyothishyam_env/` |
| Current CI Python | 3.11 from `.github/workflows/ci.yaml` |
| Current CI test command | `PYTHONPATH=. python -m pytest -q -n auto || PYTHONPATH=. python -m pytest -q` |

Actual required-reference paths:

- locked decisions: `systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- final consolidation: `systems/Parasara/Documentation/Engine/Prompt-01/Audits/Prompt-01-Final-Audit-Consolidation.md`;
- audits 01–25: `systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-*.md`.

The prompt's reference paths differ from the repository. Audits 21–23 supplied the determinism, test-inventory, CI, fixed-output, and environment evidence used here.

## 3. Locked runtime decisions

- Python 3.14 is the primary Prompt-01 development target.
- Python 3.11 remains supported and is the current CI baseline.
- New code must run in both lanes without version-specific logical differences.
- Dependency declarations are shared; environments and resolved evidence remain separate.
- WP01 must validate both lanes.
- WP02 may not begin with an unresolved architecture-relevant Python 3.14 incompatibility.
- WP19 owns the final enforced CI matrix; WP00 does not change CI.

## 4. Interpreter and isolation matrix

| Check | Python 3.14 lane | Python 3.11 lane |
|---|---|---|
| Exact version | 3.14.6 | 3.11.9 |
| Base executable | `%LOCALAPPDATA%\Programs\Python\Python314\python.exe` | `%LOCALAPPDATA%\Programs\Python\Python311\python.exe` |
| Virtual environment | `jyothishyam_env/prompt01-py314` | `jyothishyam_env/prompt01-py311` |
| Explicit executable | `jyothishyam_env/prompt01-py314/Scripts/python.exe` | `jyothishyam_env/prompt01-py311/Scripts/python.exe` |
| `sys.prefix != sys.base_prefix` | PASS | PASS |
| Git ignored | PASS | PASS |
| pip | 26.1.2 | 24.0 |
| `pip check` | PASS | PASS |
| Editable package | `ndastro-engine==0.26.0` | `ndastro-engine==0.26.0` |
| Global/cross-environment leakage | not observed | not observed |

| Core package | Python 3.14 | Python 3.11 |
|---|---:|---:|
| pytest | 9.1.1 | 9.1.1 |
| PyYAML | 6.0.3 | 6.0.3 |
| Pydantic | 2.13.4 | 2.13.4 |
| pytest-cov | 7.1.0 | 7.1.0 |
| pytest-mock | 3.15.1 | 3.15.1 |
| pytest-xdist | 3.6.1 | 3.6.1 |
| FastAPI | 0.139.0 | 0.139.0 |
| Hypothesis | 6.156.1 | 6.156.1 |
| jsonschema | 4.26.0 | 4.26.0 |
| Skyfield | 1.54 | 1.54 |
| NumPy | 2.5.1 | 2.4.6 |

NumPy is the only resolved runtime-version difference and is explicitly pinned by interpreter marker.

## 5. Dependency sources and compatibility

Declarations inspected: root `requirements-dev.txt`, `systems/Parasara/requirements.txt`, `systems/SuryaSiddhanta/pyproject.toml`, and `systems/Parasara/Documentation/evidence/licenses.json`.

WP00 owns:

- `requirements-stage01.in`, the direct Stage-01 versions;
- `requirements-stage01.lock.txt`, the complete resolved set;
- editable `systems/SuryaSiddhanta`, installed separately with `--no-deps`.

| File | SHA-256 |
|---|---|
| `requirements-stage01.in` | `CF0FE472528E74EEBC954D1B3380BAB04BEB5D168FDFFF71497B9D967B78A595` |
| `requirements-stage01.lock.txt` | `75BF8788C2A1FC33C7FC0A65B0F62E04FEA570160F7D9BCAEE06A8F783647D8B` |

### SRTM

`srtm==0.3.6` is classified `DEPENDENCY_INCOMPATIBILITY`. Its metadata excludes Python 3.11, and bundled PyO3 0.22.6 rejects Python 3.14. It is optional accuracy-integration tooling: the application lazily imports it, documents a JSON fallback, and the accuracy test skips when it is absent. The lock retains it only for Python 3.12–3.13 and both WP00 lanes use `NDASTRO_USE_SRTM=0`.

No WP02 architecture impact was found. No opportunistic version change was used to make either lane appear green.

## 6. Validation matrix

All commands used explicit venv executables, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=.`, `NDASTRO_USE_SRTM=0`, disabled pytest cache, and ignored `--basetemp` paths where applicable.

| Validation | Python 3.14 | Python 3.11 |
|---|---|---|
| import smoke + `pip check` | PASS, exit 0 | PASS, exit 0 |
| collection | PASS, 58 collected | PASS, 58 collected |
| predicate target | 5 passed, exit 0, 1.88 s | 5 passed, exit 0, 1.42 s |
| Yoga target | 4 passed, exit 0, 1.51 s | 4 passed, exit 0, 1.33 s |
| Career target | 1 passed, 1 failed, exit 1, 1.71 s | 1 passed, 1 failed, exit 1, 1.80 s |
| fresh predicate + Yoga process | 9 passed, exit 0, 1.53 s | 9 passed, exit 0, 1.32 s |
| final safe baseline | 48 passed, 4 failed, 2 skipped, exit 1, 3.53 s | 48 passed, 4 failed, 2 skipped, exit 1, 2.74 s |
| rule lint | 2 file failures, exit 2 | 2 file failures, exit 2 |
| no-update snapshot | differs, exit 3 | differs, exit 3 |
| generated cross-lane hash | identical | identical |
| prohibited-path status | clean | clean |

Collection emits an existing `PytestUnknownMarkWarning` because `pytest.mark.surya` is not registered.

Targeted commands:

```powershell
& <venv-python> -m pytest -p no:cacheprovider -q --basetemp=<ignored-temp> tests/rules/test_predicate_result.py
& <venv-python> -m pytest -p no:cacheprovider -q --basetemp=<ignored-temp> tests/enrichments/test_yoga_loader.py tests/enrichments/test_yoga_engine_rule_driven.py
& <venv-python> -m pytest -p no:cacheprovider -q --basetemp=<ignored-temp> systems/Parasara/tests/test_career_interpreter.py systems/Parasara/tests/test_vertical_slice_career.py
```

The isolated Yoga target passes, but `test_yoga_engine_rule_driven` fails in full discovery order. This is evidence of existing registry/global-state or test-order dependence, not a green Yoga baseline.

## 7. Final non-mutating baseline

Four existing test modules write fixed tracked paths:

1. `tests/determinism_test.py` writes tracked `-` 100 times;
2. `systems/Parasara/tests/test_career_snapshot.py` writes `-`;
3. `systems/Parasara/tests/test_additional_snapshots.py` writes `-`;
4. `tests/test_framework_integration.py` writes `tests/tmp_snapshot.json` through `snapshot_runner`.

The artifacts were restored after discovery. The final safe command excludes exactly those writers:

```powershell
& <venv-python> -m pytest -p no:cacheprovider -q --basetemp=<ignored-temp> `
  --ignore=tests/determinism_test.py `
  --ignore=systems/Parasara/tests/test_career_snapshot.py `
  --ignore=systems/Parasara/tests/test_additional_snapshots.py `
  --ignore=tests/test_framework_integration.py
```

Each lane ran 54 tests: 48 passed, 4 failed, 2 skipped, 0 errors.

An initial Python 3.14 probe had two `tmp_path` setup errors because the managed user temp directory was inaccessible. An explicit ignored `--basetemp` resolved them without source changes; classification: `ENVIRONMENT_ERROR`.

## 8. Failure register

| Failure | Classification | Architecture/continuation impact |
|---|---|---|
| Scorpio Mercury expected malefic, got neutral | `PROJECT_INCOMPATIBILITY` | astrology semantic baseline blocker |
| Career vertical slice differs from approved snapshot | `PROJECT_INCOMPATIBILITY` | public-output/golden blocker |
| missing `detect_yogas_from_aspect_graph` | `PROJECT_INCOMPATIBILITY` | active Yoga API/test mismatch |
| `rajayoga_naive` absent in full suite | `PROJECT_INCOMPATIBILITY` | registry/global-state/order blocker |
| Career snapshot omits `rajayoga_naive` | `PROJECT_INCOMPATIBILITY` | Career/Yoga compatibility blocker |
| two rule files missing `name` | `PROJECT_INCOMPATIBILITY` | rule-governance blocker |
| linter ignores `*.yaml` | `TOOLING_INCOMPATIBILITY` | validation coverage gap |
| unregistered `surya` marker | `TOOLING_INCOMPATIBILITY` | test-governance gap |
| four fixed tracked-output tests | `TOOLING_INCOMPATIBILITY` | blocks safe full discovery |
| default pytest temp permission | `ENVIRONMENT_ERROR` | no architecture impact |
| SRTM unsupported in both lanes | `DEPENDENCY_INCOMPATIBILITY` | optional only; no WP02 impact found |

The four identical safe-suite failures are:

- `systems/Parasara/tests/test_functional_role_table.py::test_scopio_table_override_mercury`;
- `systems/Parasara/tests/test_vertical_slice_career.py::test_vertical_slice_matches_snapshot`;
- `tests/enrichments/test_integration_aspects_consumers.py::test_aspectgraph_identity_and_consumers`;
- `tests/enrichments/test_yoga_engine_rule_driven.py::test_rule_driven_yoga_engine_matches_yaml_rules`.

## 9. Rule lint and no-update snapshot

Rule lint:

```powershell
& <venv-python> tools/rules_lint.py systems/Parasara/rules
```

Both lanes report missing `name` in:

- `systems/Parasara/rules/parashara/v1/derived_rules.yml`;
- `systems/Parasara/rules/parashara/v1/primitives.yml`.

The linter scans only `*.yml`, missing active `yogas.yaml`.

Snapshot comparison:

```powershell
& <venv-python> systems/Parasara/tools/ci_snapshot_check.py `
  --fixture systems/Parasara/fixtures/golden_chart_01.json `
  --approved systems/Parasara/tests/snapshots/output_golden_chart_01.json `
  --out <ignored-temporary-output>
```

Both lanes exit 3. Generated outputs are byte-identical with SHA-256 `D6BBB699A46DE0BE0256206461DB8163E1D15A09E324A2879784DAC2B87CD33D`, but differ from the approved snapshot in functional roles/scores, Shadbala fields, and house pressure/score values. Nothing was updated or approved.

## 10. Reproduction

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe" -m venv jyothishyam_env/prompt01-py314
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" -m venv jyothishyam_env/prompt01-py311

& jyothishyam_env/prompt01-py314/Scripts/python.exe -m pip install -r systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/WP00/requirements-stage01.lock.txt
& jyothishyam_env/prompt01-py311/Scripts/python.exe -m pip install -r systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/WP00/requirements-stage01.lock.txt

& jyothishyam_env/prompt01-py314/Scripts/python.exe -m pip install --no-deps -e systems/SuryaSiddhanta
& jyothishyam_env/prompt01-py311/Scripts/python.exe -m pip install --no-deps -e systems/SuryaSiddhanta
```

For validation:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = '.'
$env:NDASTRO_USE_SRTM = '0'
& <venv-python> -m pytest -p no:cacheprovider --collect-only -q
```

## 11. Files and protected-path proof

WP00 deliverables are under the user-designated subfolder:

- `systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/WP00/requirements-stage01.in`;
- `systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/WP00/requirements-stage01.lock.txt`;
- `systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/WP00/WP00-Dual-Python-Decision-and-Baseline.md`.

Virtual environments and temporary outputs are ignored below `jyothishyam_env/`.

After final validation and restoration, scoped status/diff checks were clean for tracked `-`, `tests/tmp_snapshot.json`, tests, production engine source, rules, schemas, approved snapshots, and workflows. Unrelated pre-existing changes were preserved.

## 12. Readiness verdict

WP00 evidence is complete, but the verdict is **BLOCKED**.

WP01 is **not ready** because the Python 3.11 safe baseline, rule lint, and approved golden comparison fail, and Yoga exhibits discovery-order/global-state sensitivity.

WP02 is **not ready** because WP01 characterization protection does not exist and unresolved project failures could obscure migration regressions. The optional SRTM limitation alone is non-architectural, but it does not override the mandatory Python 3.11 blockers.

Do not proceed to WP01 until a maintainer explicitly approves a package that resolves or formally dispositions the project, tooling, fixed-output, lint, and golden blockers without weakening tests or changing approved semantics.

