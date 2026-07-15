You are implementing **WP00-R — Baseline Blocker Remediation** for Prompt-01 in the Parasara system.

## Purpose

Resolve or formally disposition the blockers discovered by WP00 so that WP01 can begin with a trustworthy, deterministic baseline.

WP00-R is a prerequisite remediation package. It is not WP01 and must not implement the future PredicateResult architecture.

## Required references

Read before making changes:

- the repository file named `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- the repository file named `Prompt-01-Final-Audit-Consolidation.md`;
- `systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/WP00/WP00-Dual-Python-Decision-and-Baseline.md`
- `systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/WP00/requirements-stage01.in`
- `systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/WP00/requirements-stage01.lock.txt`
- the relevant Audit-15, Audit-16, Audit-21, Audit-22, and Audit-23 reports.

Locate the first two references by exact filename rather than assuming a directory. If any other listed path differs, locate it by filename. Record every actual path used and stop if duplicate authoritative-looking copies disagree.

## Runtime matrix

Use the environments established by WP00:

- Python 3.14.x — primary target;
- Python 3.11.x — compatibility/current-CI baseline.

Run every diagnostic and validation command in both lanes. Use explicit environment interpreter paths and preserve the WP00 environment variables, including `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=.`, and `NDASTRO_USE_SRTM=0` where applicable.

Do not recreate or re-resolve the environments unless their integrity check fails.

## Initial blocker register

Investigate all of the following:

1. reported safe-suite counts of `50 passed, 4 failed, 2 skipped` and `48 passed, 4 failed, 2 skipped`; the current WP00 report contains a provisional explanation based on selection/exclusion scope, which WP00-R must acknowledge and independently verify against exact node IDs;
2. `test_functional_role_table.py::test_scopio_table_override_mercury` expecting `functional_malefic` but receiving `functional_neutral`;
3. `test_vertical_slice_career.py::test_vertical_slice_matches_snapshot` differing from the approved snapshot;
4. `test_integration_aspects_consumers.py::test_aspectgraph_identity_and_consumers` referencing absent `detect_yogas_from_aspect_graph`;
5. `test_yoga_engine_rule_driven.py::test_rule_driven_yoga_engine_matches_yaml_rules` not returning `rajayoga_naive`;
6. the unsafe Career snapshot test also omitting `rajayoga_naive`;
7. Yoga behavior changing with test/discovery order;
8. missing required `name` metadata in `derived_rules.yml` and `primitives.yml`;
9. approved snapshot drift in functional roles/scores, Shadbala fields, and house pressure/score values;
10. four unsafe writers identified by WP00: `tests/determinism_test.py`, `systems/Parasara/tests/test_career_snapshot.py`, `systems/Parasara/tests/test_additional_snapshots.py`, and `tests/test_framework_integration.py`; verify the exact artifact path and write behavior of each;
11. unregistered `pytest.mark.surya`;
12. `tools/rules_lint.py` scans `*.yml` but not `*.yaml`, so the active `yogas.yaml` is excluded and rule lint can report a false pass;
13. any additional blocker reproducibly exposed while resolving the above.

Do not assume that related failures share one cause. Prove the causal relationship.

## Mandatory Phase 1 — Reproduce and reconcile

Before editing:

1. Record Git branch and working-tree state; preserve unrelated changes.
2. Verify both environment interpreter paths, versions, `pip check`, and critical imports.
3. Re-run collection in both lanes with identical commands.
4. Re-run the WP00 safe suite in both lanes using fresh unique temporary directories.
5. Start from WP00's provisional explanation for the `50` versus `48` passed-count difference. Independently verify it by recording the exact collected, excluded, selected, skipped, failed, and passed node IDs for each command. Confirm or correct the explanation before remediation; do not treat the discrepancy as an unknown root cause unless node-ID evidence disproves the report.
6. Run each failing test individually in a fresh process.
7. Run each failure with its containing module and with the complete safe suite.
8. Run Yoga-related tests individually, in normal collection order, in reverse node-ID order, and in three explicit recorded node-ID permutations. Do not use randomization or seeds. After collecting the ordered Yoga node-ID list, define and record: permutation A = odd-indexed IDs followed by even-indexed IDs; permutation B = even-indexed IDs followed by odd-indexed IDs; permutation C = the list rotated at its midpoint. Invoke pytest with the complete node-ID sequence for each permutation.
9. Capture registry/cache/global-state snapshots before and after Yoga/rule tests to locate leakage.
10. Re-run snapshot generation to ignored temporary paths and compare hashes across Python versions and repeated processes.

Classify every blocker as one of:

- `TEST_HARNESS_DEFECT`;
- `GLOBAL_STATE_OR_ORDER_DEFECT`;
- `PRODUCTION_REGRESSION_AGAINST_APPROVED_CONTRACT`;
- `STALE_OR_INVALID_TEST_EXPECTATION`;
- `RULE_METADATA_DEFECT`;
- `DEPENDENCY_OR_ENVIRONMENT_DEFECT`;
- `ASTROLOGY_SEMANTIC_AMBIGUITY`;
- `PUBLIC_GOLDEN_DECISION_REQUIRED`.

Record evidence for the classification before implementing a fix.

## Permitted remediation

You may make minimal, evidence-backed changes to:

- test fixtures, cleanup, temporary-path handling, and deterministic setup;
- pytest marker registration;
- test commands/configuration that eliminate repository writes without weakening coverage;
- validation tooling and its focused tests, limited to making the existing rule linter discover both `.yml` and `.yaml` files deterministically without duplicate processing;
- rule metadata that is required by the existing schema and demonstrably does not change rule meaning or firing, but only after explicit owner approval of the proposed diff;
- production code only to restore an already approved, documented, or golden-tested compatibility contract, only when the regression cause is proven, and only after explicit owner approval of the proposed diff;
- documentation and the WP00-R completion report.

Before any production, rule-data, astrology-table, scoring, or astrology-semantic edit, stop and request explicit owner approval. The approval request must contain:

1. the approved contract being restored;
2. evidence the current behavior is a regression rather than an intended change;
3. the smallest possible patch;
4. before/after targeted test evidence;
5. the planned tests proving that unrelated Yoga firing, Career scoring, and public output remain unchanged.

Do not interpret this prompt as advance approval for those edits. Investigation, reproduction, test-harness fixes, temporary-path fixes, marker registration, and documentation may proceed without that additional approval when they do not alter production or rule behavior.

## Prohibited remediation

Do not:

- implement PredicateResult, PredicateStatus, new registry metadata, capability models, cache redesign, condition redesign, or any WP01+ architecture;
- update, accept, regenerate in place, or weaken approved snapshots/golden files;
- change astrology tables, rules, weights, scoring formulas, or domain behavior merely to make a test pass;
- select new aspect, conjunction, exaltation, functional-role, or house-lord semantics;
- delete failing tests, add broad skips/xfails, loosen equality, increase tolerances, or replace semantic assertions with shape checks;
- hide failures with `|| true`, serial fallback, exclusions, or altered discovery patterns;
- commit generated reports, caches, virtual environments, or temporary outputs;
- modify dependency versions unless a reproduced dependency defect makes it necessary and the change is separately justified for both Python lanes.

## Blocker-specific requirements

### Test writers targeting `-`

For each of the four identified writers, determine the exact tracked or fixed output it can create or overwrite, including why `-` is interpreted as a filename where applicable. Redirect generated output through `tmp_path` or explicit ignored temporary paths. Preserve the same assertions and production invocation semantics. Add regression assertions proving no tracked/fixed repository artifact is created or modified.

### Global state and Yoga order dependence

Identify every mutable registry, cache, loader singleton, environment dependency, and import-time side effect involved. Prefer deterministic production initialization when the existing contract requires it; otherwise use robust `yield`/`finally` fixture isolation. Tests must pass individually and in multiple recorded orders without relying on a prior test to initialize state.

Do not solve order dependence by forcing one test order.

### Missing Yoga API

Determine whether `detect_yogas_from_aspect_graph` is:

- an approved public/current API accidentally removed;
- a stale test for a retired API; or
- a dormant alternative path outside the active architecture.

Use repository callers, documentation, history available in the working tree, and audit evidence. Restore it only if the approved contract requires it. Otherwise update the stale test to the active supported path without reducing its behavioral assertion, and explain why.

### `rajayoga_naive`

Trace YAML discovery, loader registration, condition evaluation, required enrichments, global-state lifecycle, and output filtering. Do not force the ID into output. Restore it only if the existing valid rule and fixture conditions genuinely require it. Verify both firing and non-firing cases and deterministic row order.

### Functional-role failure

Trace the effective configuration source, spelling/fixture (`scopio` versus `scorpio`), current-working-directory dependence, override loading, and cache/state preparation. Preserve the currently approved functional-role table; do not invent a semantic answer. If reports and approved fixtures conflict, classify `ASTROLOGY_SEMANTIC_AMBIGUITY` and stop that fix for owner review.

### Rule metadata

Determine whether missing `name` values are rule-schema defects and prepare the smallest proposed metadata diff using stable descriptive names derived from existing IDs/descriptions. Request explicit owner approval before editing either rule file. After approval, prove rule firing and serialized public output are unchanged.

### Rule-linter `.yaml` coverage

Update the existing validation tool minimally so rule discovery includes both `*.yml` and `*.yaml`.

Requirements:

1. discover both extensions recursively over the same intended rule roots;
2. normalize and de-duplicate discovered paths before validation so no file can be processed twice;
3. use deterministic path ordering;
4. retain the existing validation behavior and exit-code contract for `.yml` files;
5. validate `.yaml` files according to their actual supported rule format; do not force `yogas.yaml` through an incompatible schema merely because its extension is now discovered;
6. add focused temporary-directory tests containing one `.yml`, one `.yaml`, irrelevant extensions, nested files, and a duplicate-discovery scenario;
7. prove malformed content in either supported extension fails the command;
8. prove the repository's active `yogas.yaml` is discovered and inspected;
9. run the tool and focused tests in both Python lanes;
10. do not modify `yogas.yaml` or any rule file as part of the linter-tool correction. Any rule-file change remains separately owner-approval gated.

The linter must report which supported files were inspected, or expose an equivalent deterministic machine-verifiable discovery result in tests, so final validation can prove coverage rather than infer it from an exit code.

### Snapshot drift

Treat the approved snapshot as the compatibility contract. Do not update it. Produce a field-level diff grouped into:

- deterministic metadata/telemetry;
- functional roles and Career scores;
- Shadbala;
- house pressure/scores;
- Yoga membership/order;
- all other fields.

Trace each difference to a specific cause. Restore existing approved behavior only where evidence proves a regression. Any genuine contract change or astrology-semantic ambiguity requires explicit owner approval and remains blocked.

### Pytest marker

Register `surya` in the repository's pytest marker configuration with a clear description. Do not suppress unknown-marker warnings globally.

## Validation after each fix

For every fix:

1. run its focused test in both Python lanes;
2. run the containing module in both lanes;
3. run relevant neighboring Yoga/Career/rule tests;
4. run test-order permutations when global state is involved;
5. verify no tracked artifact was written;
6. inspect the minimal diff before continuing.

## Final validation

Run in both Python 3.14 and Python 3.11:

1. import smoke and `pip check`;
2. full collection;
3. complete safe suite with no exclusions for the four formerly unsafe writer tests;
4. targeted predicate, Yoga, Career, functional-role, aspect, determinism, and snapshot modules;
5. Yoga tests individually, in normal collection order, reverse node-ID order, and the three explicit recorded node-ID permutations defined in Phase 1; invoke pytest with full node-ID lists and do not depend on a random-order plugin;
6. focused rule-linter discovery/validation tests proving `.yml`, `.yaml`, recursion, deterministic ordering, de-duplication, existing `.yml` behavior, and failure propagation in both lanes;
7. repository rule lint with captured evidence that the active `yogas.yaml` path was actually inspected exactly once;
8. approved snapshot comparison in strict no-update mode;
9. two fresh-process repetitions of the full baseline;
10. repository status and artifact scan.

The same node IDs must be collected in both lanes. Report exact counts; do not summarize only as “passed.”

## Gate policy

WP01 may begin only if:

- the pass-count discrepancy is explained;
- both environments remain reproducible;
- the complete safe baseline is deterministic and has no unexplained failures;
- rule lint passes;
- rule lint demonstrably inspects supported `.yml` and `.yaml` files, including the active `yogas.yaml`, exactly once per run;
- no test writes tracked artifacts;
- Yoga behavior is independent of discovery/execution order;
- the approved snapshot comparison passes without modifying the approved file; and
- no unresolved astrology-semantic or public-contract decision remains relevant to WP01 characterization.

If any condition is not met, verdict is `BLOCKED`. Do not authorize WP01.

## Completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/WP00-R/WP00-R.md`

Include:

1. verdict: `COMPLETE`, `BLOCKED`, or `INCOMPLETE`;
2. before/after blocker register;
3. reconciliation of all test counts and exact node IDs;
4. root cause and classification for every blocker;
5. files changed with justification;
6. production-change compatibility proof, if any;
7. Yoga order/global-state experiments and results;
8. field-level snapshot-drift analysis;
9. commands and exact results for both Python lanes;
10. rule-lint and artifact-write evidence;
11. rule-linter discovery evidence listing the supported files inspected, including `yogas.yaml`, plus focused dual-lane test results;
12. unresolved decisions requiring owner or astrology-SME review;
13. explicit `WP01_READY: YES` or `WP01_READY: NO`.

At the end, provide a concise summary with the verdict, fixed and unresolved blockers, files changed, exact test/lint/snapshot results for both lanes, and WP01 readiness. Do not proceed to WP01.