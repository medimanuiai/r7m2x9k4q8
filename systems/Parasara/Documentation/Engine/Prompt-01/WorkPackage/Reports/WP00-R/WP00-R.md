# WP00-R — Baseline Blocker Remediation Completion Report

**Date:** 2026-07-14  
**Verdict:** `COMPLETE`  
**WP01_READY:** `YES`

WP00-R completed the investigation, permitted harness/tooling remediation, and the subsequently owner-approved minimal production/rule remediation. No astrology table, approved snapshot, public schema, dependency, or CI workflow was changed. The dual-Python baseline is deterministic and green.

## 1. Authoritative inputs and environment

The actual reference paths used were:

- `systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Prompt-01-Locked-Decisions-and-Execution-Plan.md`
- `systems/Parasara/Documentation/Engine/Prompt-01/Audits/Prompt-01-Final-Audit-Consolidation.md`
- `systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/WP00/WP00-Dual-Python-Decision-and-Baseline.md`
- `systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/WP00/requirements-stage01.in`
- `systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/WP00/requirements-stage01.lock.txt`
- `systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-15-Yoga-Engine.md`
- `systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-16-Domain-Runtime.md`
- `systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-21-Determinism.md`
- `systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-22-Test-Inventory-Gap-Analysis.md`
- `systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-23-CI-Validation.md`

The formerly open duplicate WP00-R prompt under `WorkPackage/WP00/` no longer exists. One authoritative WP00-R prompt was present. The branch was `main`; unrelated pre-existing documentation changes were preserved.

Runtime lanes:

| Lane | Interpreter | Version | Dependency integrity |
|---|---|---:|---|
| primary | `jyothishyam_env/prompt01-py314/Scripts/python.exe` | 3.14.6 | `pip check`: no broken requirements; imports OK |
| compatibility | `jyothishyam_env/prompt01-py311/Scripts/python.exe` | 3.11.9 | `pip check`: no broken requirements; imports OK |

Both lanes used `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=.`, and `NDASTRO_USE_SRTM=0`. Critical versions were identical: PyYAML 6.0.3, Pydantic 2.13.4, pytest 9.1.1. Because the managed user temp directory is inaccessible, every pytest command using `tmp_path` used a unique `--basetemp` below ignored `jyothishyam_env/`.

## 2. Test-count reconciliation

Before WP00-R, both lanes collected the same 58 node IDs.

The `50 passed, 4 failed, 2 skipped` probe selected 56 nodes by excluding only:

- `tests/determinism_test.py::test_determinism_runs`
- `systems/Parasara/tests/test_career_snapshot.py::test_career_snapshot_matches_golden`

The final WP00 safe command selected 54 nodes by additionally excluding:

- `systems/Parasara/tests/test_additional_snapshots.py::test_additional_snapshots_match`
- `tests/test_framework_integration.py::test_framework_smoke_run`

Those two additionally excluded nodes passed when safely redirected, so the exact change was from 50 to 48 passes while the same four failures and two skips remained. The discrepancy is therefore selection scope, not nondeterminism.

WP00-R added five linter tests, so final collection is 63 identical node IDs in both lanes. The five additions are:

- `tests/tools/test_rules_lint.py::test_discovery_is_recursive_deterministic_and_deduplicated`
- `tests/tools/test_rules_lint.py::test_lint_supports_existing_yml_and_yoga_yaml_formats`
- `tests/tools/test_rules_lint.py::test_empty_generic_yaml_matches_runtime_loader_behavior`
- `tests/tools/test_rules_lint.py::test_malformed_supported_extensions_fail_command`
- `tests/tools/test_rules_lint.py::test_repository_yogas_file_is_discovered_once`

Pre-approval repeated full-baseline result, including all formerly unsafe writers:

| Lane | Repetition 1 | Repetition 2 |
|---|---:|---:|
| Python 3.14 | 57 passed, 4 failed, 2 skipped | 57 passed, 4 failed, 2 skipped |
| Python 3.11 | 57 passed, 4 failed, 2 skipped | 57 passed, 4 failed, 2 skipped |

Final post-approval result: both fresh repetitions in both lanes collected the same 63 nodes and produced **61 passed, 2 skipped, 0 failed**. This is the controlling WP00-R baseline result.

Exact pre-approval failures (historical evidence; every node below passes in the final post-approval baseline):

- `systems/Parasara/tests/test_career_snapshot.py::test_career_snapshot_matches_golden`
- `systems/Parasara/tests/test_functional_role_table.py::test_scopio_table_override_mercury`
- `systems/Parasara/tests/test_vertical_slice_career.py::test_vertical_slice_matches_snapshot`
- `tests/enrichments/test_yoga_engine_rule_driven.py::test_rule_driven_yoga_engine_matches_yaml_rules`

Exact skips:

- `tests/SuryaSiddhanta/test_integration_accuracy.py::test_integration_accuracy`
- `tests/surya/test_positions.py::test_positions_against_skyfield`

## 3. Before/after blocker register

| Blocker | Classification | Before | After/disposition |
|---|---|---|---|
| 50-versus-48 pass count | `TEST_HARNESS_DEFECT` | inconsistent-looking reports | resolved by exact node selection evidence |
| Scorpio Mercury role | `ASTROLOGY_SEMANTIC_AMBIGUITY` | expected malefic, runtime neutral | resolved by owner-selected compatibility contract and deterministic legacy-table precedence |
| approved vertical snapshot | `PUBLIC_GOLDEN_DECISION_REQUIRED` | strict mismatch | resolved without changing the golden; generated bytes now match |
| absent `detect_yogas_from_aspect_graph` | `STALE_OR_INVALID_TEST_EXPECTATION` | test called nonexistent API | fixed to active public `evaluate_yoga_rules`; behavioral assertions retained |
| Yoga omits `rajayoga_naive` after rule-runtime test | `GLOBAL_STATE_OR_ORDER_DEFECT` | full-suite failure, isolated pass | resolved by identity-preserving registry clear |
| Career fixture omits `rajayoga_naive` | `PUBLIC_GOLDEN_DECISION_REQUIRED` | generated IDs differ from approved Career fixture | resolved through the existing matched factual rule after typed version normalization |
| Yoga test order | `TEST_HARNESS_DEFECT` plus production global-state defect | loader test depended on predecessor; production registry leaked | loader initialization and identity-preserving production fix completed; all recorded orders pass |
| missing rule metadata | `RULE_METADATA_DEFECT` | linter fails `derived_rules.yml` and `primitives.yml` | resolved with owner-approved legacy/unverified metadata; lint passes |
| snapshot functional/Shadbala/house drift | `PUBLIC_GOLDEN_DECISION_REQUIRED` and `ASTROLOGY_SEMANTIC_AMBIGUITY` | strict mismatch | resolved through compatibility projection and table precedence; golden unchanged |
| four unsafe writers | `TEST_HARNESS_DEFECT` | wrote `-`, `tests/tmp_snapshot.json`, and `tests/testrun_report.html` | fixed with `tmp_path`; repository artifacts unchanged |
| unregistered `surya` | `TEST_HARNESS_DEFECT` | unknown-marker warning | fixed with explicit marker registration |
| linter ignored `.yaml` | `TEST_HARNESS_DEFECT` | false coverage | fixed with deterministic dual-extension discovery and tests |
| managed default pytest temp | `DEPENDENCY_OR_ENVIRONMENT_DEFECT` | WinError 5 | consistently avoided with explicit ignored `--basetemp` |

## 4. Root-cause evidence

### 4.1 Functional-role conflict

Pre-approval historical evidence: the test name misspells “Scorpio” as `scopio`, but sets `chart.lagna.sign = 'Scorpio'`; spelling was not causal. At reproduction time, `functional_roles._load_table_for_lagna` used CWD-relative precedence:

1. `rules/parashara/functional_roles/Scorpio.yaml`
2. `systems/Parasara/enrichment_tables/functional_roles/Scorpio.yaml`

The then-preferred table declared Mercury `functional_neutral`, score 0.5. The legacy table declared Mercury `functional_malefic`, score 0.25, which is the value protected by the existing test and approved outputs. Before owner approval, selecting between them was intentionally recorded as unresolved rather than inferred.

Final disposition: the owner selected the existing functional-role tests and approved goldens as the Prompt-01 compatibility contract. Production now resolves both table roots from `__file__` and consults the existing legacy Parasara table first, eliminating CWD dependence without changing either table. The functional-role target and strict golden comparison pass in both Python lanes.

### 4.2 Missing Yoga API

Repository callers and history contain no production implementation of `detect_yogas_from_aspect_graph`; history finds only the initial import commit and the only caller was the failing test. Audit-15 identifies exactly one active public Yoga surface, `yoga.evaluate_yoga_rules`, and labels the absent symbol a stale test-only path. The test now calls `evaluate_yoga_rules` while retaining its list, trace, aspects, graph-identity, and Shadbala evidence checks.

### 4.3 Yoga registry identity leak

Pre-approval historical evidence: `yoga_engine.py` imports the dictionary object with `from ...loader import RULE_REGISTRY`. `loader.load_rules_from_dir()` then executed `RULE_REGISTRY = {}`, rebinding the loader module name while `yoga_engine` continued holding the old object.

Both lanes produced the same state snapshot:

- initial: loader registry and Yoga registry have the same object ID, lengths 0/0;
- Yoga load first: same object, lengths 3/3;
- generic load: different object IDs, lengths 13/3, identity false;
- Yoga reload: loader remains 13 while the Yoga-held object remains 3.

With a fresh initially empty object, the pre-approval run of `test_rule_runtime_merge` before the Yoga engine gave one pass then one Yoga failure; reversing those two nodes gave two passes. This proved a production global-state defect rather than a rule-firing or fixture failure.

The recorded minimal production patch was:

```diff
 def load_rules_from_dir(rules_dir):
-    global RULE_REGISTRY
-    RULE_REGISTRY = {}
+    RULE_REGISTRY.clear()
```

Approved contract: preserve the current valid Yoga rule set, firing, row order, and externally consumed keys, independent of unrelated test execution. Historical before evidence remains `1 passed, 1 failed` in both lanes for generic-loader then Yoga; the process-local pre-edit simulation produced `2 passed` in both lanes.

Final disposition: the owner approved and production now uses `RULE_REGISTRY.clear()`. Post-approval validation completed the previously planned matrix: the two-node trigger passes in both orders, all five Yoga permutations pass, both complete baseline repetitions pass, Career targets pass, and the strict snapshot/hash comparison matches the unchanged approved bytes.

### 4.4 Career `rajayoga_naive`

The Career interpreter actively appends candidate `{'id': 'rajayoga_naive', 'type': 'rajayoga_naive'}` and runtime requires natural benefics in both houses 1 and 10. The approved Career fixture contains the rule with Moon in house 1 and Venus in house 10. Pre-approval generation returned only `10th_lord_Venus`; this was recorded as a public-golden decision rather than repaired by forcing an identifier into output.

Final disposition: the owner made the approved Career fixture authoritative. Investigation showed that the existing factual rule matched, but integer rule version `1` failed the typed `RuleMatch` string boundary and the interpreter's fallback then omitted the result. Normalizing that existing version to `str` allows the factual match to be returned. No condition, planet, house, score, rule identifier, fixture, or golden was changed. The Career snapshot and full baseline now pass in both lanes.

## 5. Yoga order experiments

Ordered Yoga IDs:

1. `tests/enrichments/test_yoga_loader.py::test_load_yoga_rules`
2. `tests/enrichments/test_yoga_loader.py::test_rule_registered`
3. `tests/enrichments/test_yoga_loader.py::test_validator_detects_missing_fields`
4. `tests/enrichments/test_yoga_engine_rule_driven.py::test_rule_driven_yoga_engine_matches_yaml_rules`
5. `tests/enrichments/test_integration_aspects_consumers.py::test_aspectgraph_identity_and_consumers`

Defined permutations:

- normal: 1,2,3,4,5
- reverse: 5,4,3,2,1
- A, odd then even: 1,3,5,2,4
- B, even then odd: 2,4,1,3,5
- C, midpoint rotation: 3,4,5,1,2

Pre-approval, permutation B failed because node 2 assumed node 1 had initialized the registry. After node 2 explicitly calls `load_yoga_rules`, every permutation is `5 passed` in both lanes.

Final post-approval disposition: the identity-preserving production fix also resolves the separate generic-loader trigger. Generic-loader then Yoga and Yoga then generic-loader are both `2 passed` in Python 3.14 and Python 3.11. No Yoga failure or unresolved order gate remains.

Historical mutable-state inventory: loader `RULE_REGISTRY`, predicate `PREDICATE_REGISTRY`, rule-engine global cache, Yoga's formerly stale imported registry reference, import-time predicate decorator registration, then-CWD-dependent Yoga/rule paths, and Yoga preparation mutations to vargas, aspects, and `astro.enrichments['yogas']`. No evidence implicated environment variables or dependency versions in the observed Yoga failure. The WP00-R fixes addressed the proven registry identity and deterministic functional-table path defects without introducing an ordering mechanism.

## 6. Snapshot-drift analysis

Two fresh processes per lane generated the identical SHA-256:

`D6BBB699A46DE0BE0256206461DB8163E1D15A09E324A2879784DAC2B87CD33D`

The approved file SHA-256 is:

`DA2059BA3CFB92EED267F93D1E41585DAC1422D68F685022C8609CFD04AD57AF`

There are exactly 12 leaf differences, all under `diagnostics`:

| Group | Path | Approved | Generated | Traced cause |
|---|---|---:|---:|---|
| functional roles | `planet_strengths.Mars.functional_role` | yogakaraka | functional_benefic | legacy Aries table versus preferred root table |
| functional roles | `planet_strengths.Mars.functional_score` | 0.85 | 0.6 | same table precedence |
| functional roles | `planet_strengths.Moon.functional_role` | functional_neutral | functional_benefic | same table precedence |
| functional roles | `planet_strengths.Moon.functional_score` | 0.56 | 0.7 | same table precedence |
| functional roles | `planet_strengths.Sun.functional_score` | 0.68 | 0.65 | same table precedence |
| Shadbala | `planet_strengths.Mars.shadbala` | absent | six-field object | current planet-strength assembly emits Shadbala |
| Shadbala | `planet_strengths.Moon.shadbala` | absent | six-field object | current planet-strength assembly emits Shadbala |
| Shadbala | `planet_strengths.Sun.shadbala` | absent | six-field object | current planet-strength assembly emits Shadbala |
| house pressure | `houses[0].benefic_pressure` | 0.646 | 0.456 | downstream of role/score inputs |
| house score | `houses[0].house_score` | 0.823 | 0.728 | downstream formula |
| house pressure | `houses[1].benefic_pressure` | 0.0 | 0.497 | downstream of role/score inputs |
| house score | `houses[1].house_score` | 0.5 | 0.748 | downstream formula |

Grouped zero-difference results:

- deterministic metadata/telemetry: none;
- Career domain scores/components/indicators: none in this full approved snapshot;
- Yoga membership/order: none;
- all other fields: none.

This was the pre-approval drift. After owner selection of the approved golden as the contract, repository-anchored legacy table precedence restores the role/house values and the legacy public projection omits internal Shadbala detail. The strict comparator now exits 0 in both lanes and four fresh generated files are byte-identical to the unchanged approved file.

## 7. Rule linter

The linter now:

- discovers `.yml` and `.yaml` recursively;
- resolves, de-duplicates, and case-insensitively sorts paths;
- retains the existing metadata schema for `.yml`;
- validates `yogas.yaml` using the active Yoga loader schema;
- validates other runtime YAML lists by the generic loader's required `id` and accepts an empty/comment-only macro file as the runtime loader does;
- prints every inspected path.

Focused tests: `5 passed` in Python 3.14 and `5 passed` in Python 3.11. They prove recursion, ordering, de-duplication, irrelevant-extension exclusion, legacy `.yml`, Yoga `.yaml`, empty runtime YAML, malformed `.yml`/`.yaml` failure, and active Yoga discovery.

Repository lint inspects each of these exactly once in both lanes:

1. `systems/Parasara/rules/parashara/v1/derived_rules.yml`
2. `systems/Parasara/rules/parashara/v1/m1_rules.yaml`
3. `systems/Parasara/rules/parashara/v1/macros.yaml`
4. `systems/Parasara/rules/parashara/v1/primitives.yml`
5. `systems/Parasara/rules/parashara/v1/yogas.yaml`

Before approval it exited 2 because `derived_rules.yml` and `primitives.yml` failed first at missing `name`. The approved metadata-only patch added the following stable names:

- `lord_status_10th`: “10th House Lord Status”
- `rajayoga_naive_01`: “Naive Raja Yoga 01”
- `aspect_on_10_jupiter`: “Jupiter Aspect on 10th House”
- `in_house_mars_1`: “Mars in 1st House”
- `in_sign_moon_own`: “Moon in Own Sign”
- `strong_in_10_mars`: “Strong Mars in 10th House”

Unknown provenance/governance facts are explicitly `legacy-unverified`; the only source claim is repository commit `8a04e1c3a5284030e8306b8d0ae11bcb1744fc26`, with `sme_required: true` and `sme_approved: false`. Final repository lint exits 0 in both lanes and inspects all five supported files exactly once.

## 8. Unsafe-writer remediation and artifact evidence

`generate(input, '-')` treats `-` as an ordinary `Path`, so the three direct callers wrote the repository-root tracked file named `-`; determinism did so 100 times. They now write named files below `tmp_path`. The framework runner formerly wrote `tests/tmp_snapshot.json`, and its smoke test wrote `tests/testrun_report.html`; it now passes unique output paths below `tmp_path` and writes the report there.

Regression assertions compare the old fixed/tracked artifact bytes before and after. After focused and two full runs in both lanes:

- `git status --short -- '-' tests/tmp_snapshot.json tests/testrun_report.html systems/Parasara/tests/snapshots` is empty;
- production/rule diffs are limited to the owner-approved files listed below, and no approved-snapshot diff exists;
- the four formerly unsafe nodes ran as part of the full baseline;
- no generated file appeared in tracked repository locations.

## 9. Files changed

- `pytest.ini` — register `surya` marker.
- `tests/determinism_test.py` — redirect 100 snapshot writes and assert `-` unchanged.
- `systems/Parasara/tests/test_career_snapshot.py` — redirect output and assert `-` unchanged.
- `systems/Parasara/tests/test_additional_snapshots.py` — redirect both outputs and assert `-` unchanged.
- `tests/testing_framework/snapshot_runner.py` — accept an explicit output path.
- `tests/testing_framework/regression_runner.py` — route each generated snapshot to a unique supplied directory.
- `tests/test_framework_integration.py` — use `tmp_path` and assert both former fixed artifacts unchanged.
- `tests/enrichments/test_integration_aspects_consumers.py` — replace stale Yoga API with documented active API.
- `tests/enrichments/test_yoga_loader.py` — make registry setup independent of predecessor tests.
- `tools/rules_lint.py` — dual-extension deterministic discovery and format-aware inspection reporting.
- `tests/tools/test_rules_lint.py` — focused linter coverage.
- `systems/Parasara/engine/rules/loader.py` — preserve registry object identity when reloading.
- `systems/Parasara/engine/enrichments/functional_roles.py` — deterministic repository-anchored compatibility-table precedence.
- `systems/Parasara/engine/rules/runtime.py` — normalize legacy numeric rule versions at the typed boundary.
- `systems/Parasara/tools/generate_snapshot.py` — preserve the approved legacy diagnostic projection while retaining internal Shadbala data.
- `systems/Parasara/rules/parashara/v1/derived_rules.yml` — approved metadata-only completion for three legacy rules.
- `systems/Parasara/rules/parashara/v1/primitives.yml` — approved metadata-only completion for three legacy rules.
- this report.

`git diff --check` passes for the changed tracked files. Unrelated pre-existing working-tree changes were not modified or restored.

## 10. Commands and exact results

All pytest invocations used the environment variables and unique ignored `--basetemp` described above.

| Command class | Python 3.14 | Python 3.11 |
|---|---:|---:|
| `pip check` + import smoke | pass | pass |
| `pytest --collect-only -q -o addopts=` | 63 collected | 63 collected, identical IDs |
| focused linter tests | 5 passed | 5 passed |
| Yoga normal/reverse/A/B/C | 5 passed in every order | 5 passed in every order |
| generic-loader then Yoga | 2 passed | 2 passed |
| Yoga then generic-loader | 2 passed | 2 passed |
| simulated identity-preserving production patch | 2 passed | 2 passed |
| full baseline repetition 1 | 61 passed, 2 skipped | 61 passed, 2 skipped |
| full baseline repetition 2 | 61 passed, 2 skipped | 61 passed, 2 skipped |
| targeted predicate/Yoga/Career/role/aspect/writer set | 21 passed | 21 passed |
| repository rule lint | exit 0; five files inspected once | exit 0; identical |
| strict approved snapshot, two processes | exit 0; exact match both | exit 0; exact match both |
| snapshot repeated-process hash | DA2059BA...57AF both runs | DA2059BA...57AF both runs |

## 11. Approval and SME decisions — final disposition

The owner granted all WP00-R-specific decisions: preserve registry identity, use explicit unverified legacy metadata, treat existing functional-role tests and approved outputs as the compatibility contract, and treat the approved Career fixture as authoritative. Each was implemented minimally and validated without changing tests, astrology tables, rules' factual/scoring fields, or approved goldens. No unresolved decision remains relevant to the WP01 baseline gate.

## 12. Gate conclusion

All WP00-R gates pass: the count discrepancy is explained; both environments are reproducible; all 63 collected nodes are identical; two fresh full runs per lane have no failures; rule lint passes and proves `.yml`/`.yaml` coverage; tracked artifacts are unchanged; Yoga passes every recorded order and both generic-loader trigger orders; Career and functional-role contracts pass; and strict snapshots match the unchanged approved bytes. WP00-R authorizes readiness only and does not start WP01.

**VERDICT: COMPLETE**  
**WP01_READY: YES**

## Appendix A — Owner-approved implementation log recorded before edits

The owner subsequently authorized production and rule remediation while retaining all approved tests and goldens as compatibility contracts. Before applying those edits, the following minimal diffs were recorded:

1. **Yoga registry identity contract:** in `engine/rules/loader.py`, replace the `RULE_REGISTRY = {}` rebind with `RULE_REGISTRY.clear()`. This preserves references held by Yoga without changing loaded rule content.
2. **Functional-role/golden contract:** in `engine/enrichments/functional_roles.py`, resolve table roots from `__file__` rather than CWD and consult the existing legacy Parasara table before the root rule-table fallback. This restores the exact table source expected by the functional-role test and approved diagnostic golden without editing either table.
3. **Career factual-rule contract:** in `engine/rules/runtime.py`, normalize an existing numeric rule version to `str` at the typed `RuleMatch` boundary. The duplicate `rajayoga_naive` YAML record currently supplies integer version `1`, which raises validation after its factual condition already matched; normalization allows the existing factual result to be returned and never forces the ID.
4. **Approved public projection contract:** in `tools/generate_snapshot.py`, omit internal `shadbala` detail only from the legacy public diagnostic projection. Internal `compute_planet_strengths` and its Shadbala tests remain unchanged.
5. **Legacy rule-governance contract:** add required metadata to the six existing records in `derived_rules.yml` and `primitives.yml`. Names are deterministic expansions of IDs; repository commit `8a04e1c3a5284030e8306b8d0ae11bcb1744fc26` is the only verifiable source. Unknown authorship, date, and classical reference are explicitly `legacy-unverified`; validation is `legacy-unverified`, `sme_required: true`, and `sme_approved: false`. No condition, type, planet, house, sign, or score changes.

These proposals were recorded before the corresponding edits, as required. Their placement as an appendix does not indicate chronology; the final evidence and verdict above supersede earlier pre-approval evidence where explicitly marked.
