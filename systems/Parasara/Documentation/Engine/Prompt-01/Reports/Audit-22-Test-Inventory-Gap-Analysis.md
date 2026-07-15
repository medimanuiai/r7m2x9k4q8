# Prompt-01 Audit-22: Test Inventory and Gap Analysis

## 1. Executive Summary

Audit-22 is **COMPLETE**. The authoritative Master Architecture and Prompt-01 DOCX files and all twenty-one prerequisite reports were available. Static discovery identified 28 Prompt-01-relevant test or test-support modules containing 45 test functions. One property module is not named for default pytest discovery, and one `test_` support module contains no tests. The classified inventory contains 9 unit, 4 contract, 7 integration, 1 architecture, 1 property, 3 snapshot/golden, 2 end-to-end, and 1 fixture-only module.

An isolated run of `tests/rules/test_predicate_result.py` was attempted with bytecode generation and pytest's cache disabled. The command stopped before collection because the active Python 3.13 environment does not have `pytest`. Consequently zero tests were executed: passed 0, failed 0, skipped 0, xfailed 0. CI configuration declares a Python 3.11 full-suite run and snapshot comparison, but no current run result or artifact was available; this report does not claim those tests pass.

Only five direct predicate-contract tests exist, all in one file. Across six registered predicate IDs, none has full coverage: one is partial, two have weak assertions, one is covered only through legacy/enrichment behavior, and two have no registered-predicate test coverage. No tests exist for the required PredicateStatus, PredicateError, or PredicateTraceStep models, deep immutability, canonical state identity, complete registry metadata, parameter schemas, capability/status distinctions, logical cache equivalence, complete condition semantics, deterministic trace/evidence, canonical round trips, or concurrency isolation.

The consolidated register contains 32 nonduplicated gap groups: 14 P0, 12 P1, 4 P2, and 2 P3. Eleven of twelve required architecture rules lack executable enforcement. Five fixture/global-isolation risks, six nondeterministic-test risks, and six snapshot/golden contract impacts were found. No implementation, tests, fixtures, snapshots, CI files, prior reports, or Audit-23 artifacts were modified.

## 2. Audit Scope and Method

The audit searched all repository test locations, pytest configuration, fixtures, snapshots, test framework utilities, CI workflows, and source references to predicate results, registries, evaluators, cache fields, Yoga, Career, evidence, trace, serialization, and determinism. Every counted test function and substantive assertion was inspected rather than inferred from filenames.

Coverage was mapped against Prompt-01 and the confirmed risks from Audits 1–21. Static results use `STATIC_FINDING`; the attempted run uses `TEST_BLOCKED_BY_ENVIRONMENT`. Safe commands exclude snapshot update, acceptance, record, rewrite, report generation, and fixed-path artifact utilities.

This is not a complete Parasara calculation-quality audit. Shadbala, varga, Surya accuracy, and unrelated domain tests were excluded unless they directly exercise a capability or boundary consumed by the current predicate/Yoga/domain paths.

## 3. Reconciliation with Audits 1–21

All expected reports exist. Their individual gap lists were normalized into the 32 groups in Section 23. Repeated names such as “deep immutability,” “cache mutation protection,” and “evidence defensive copying” were consolidated rather than counted three times.

Audits 1–4 identify registry, six-predicate, legacy return, and caller-path gaps. Audits 5–6 identify missing typed result/supporting-model tests. Audit 7 identifies parameter validation categories; Audit 8 capability distinctions; Audits 9–10 state identity and purity. Audit 11 supplies cache scenarios; Audits 12–14 condition/format/loader validation; Audits 15–16 Yoga/domain integration; Audits 17–19 typed error/evidence/trace; Audit 20 serialization; and Audit 21 repeatability, ordering, lifecycle, and concurrency.

Verification found no prior-audit gap that is now fully covered. Several are partially covered: basic PredicateResult construction, one cold/warm flag path, one matched predicate, one unmatched predicate, leaf condition delegation, Yoga loader shape, Yoga output structure, Career structure/snapshots, repeated assembled output, and the interpreter `Chart` architecture rule. The earlier gaps remain valid because assertions do not cover the required semantics.

## 4. Test-Suite and Fixture Inventory

| Test File | Framework | Level | Subject | Fixtures | Markers | Skip/Xfail | Snapshot/Golden | CI Status | Safe Command | Execution Status | Prompt-01 Coverage |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `tests/rules/test_predicate_result.py` | pytest | `CONTRACT` | result/evaluator/cache/leaf/serialization | local AstroState factory | none | none | No | included by wildcard | `python -m pytest -p no:cacheprovider tests/rules/test_predicate_result.py -q` | `TEST_BLOCKED_BY_ENVIRONMENT` | five weak/partial core tests |
| `systems/Parasara/tests/test_astrostates_enforced.py` | pytest/AST | `ARCHITECTURE` | interpreter avoids `Chart` | repository source tree | none | none | No | included by wildcard | targeted pytest file | `TEST_NOT_EXECUTED` | one active boundary rule |
| `systems/Parasara/tests/test_career_interpreter.py` | pytest | `INTEGRATION` | Career output structure | golden chart via conftest | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | domain shape only |
| `systems/Parasara/tests/test_career_snapshot.py` | pytest | `SNAPSHOT_OR_GOLDEN` | Career indicator IDs | chart + Career golden | none | none | Yes | included | targeted pytest file | `TEST_NOT_EXECUTED` | partial compatibility |
| `systems/Parasara/tests/test_additional_snapshots.py` | pytest | `SNAPSHOT_OR_GOLDEN` | two Career fixture sets | two charts/two goldens | none | none | Yes | included | targeted pytest file | `TEST_NOT_EXECUTED` | indicator-ID compatibility |
| `systems/Parasara/tests/test_derived_models.py` | pytest | `UNIT` | DerivedState construction | golden chart | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | prepared-state shape |
| `systems/Parasara/tests/test_derived_state.py` | pytest | `UNIT` | house/role derived facts | golden chart | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | indirect predicate capabilities |
| `systems/Parasara/tests/test_functional_role_table.py` | pytest | `UNIT` | table override | golden chart/CWD files | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | FUNCTIONAL_ROLE provider only |
| `systems/Parasara/tests/test_phase1_phase2_enrichments.py` | pytest | `INTEGRATION` | IDs/precision/normalizer enrichments | local Chart objects | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | partial normalization/capability |
| `systems/Parasara/tests/test_phase2_normalizer.py` | pytest | `CONTRACT` | normalized AstroState structure | fixture directory | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | no readiness/digest/immutability |
| `systems/Parasara/tests/test_rule_runtime.py` | pytest | `UNIT` | legacy boolean/dict runtime | golden chart | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | legacy behavior only |
| `systems/Parasara/tests/test_rule_runtime_merge.py` | pytest | `INTEGRATION` | registry/rule merge provenance | rule directory/global registry | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | loader/runtime legacy path |
| `systems/Parasara/tests/test_validator_and_adapter.py` | pytest | `CONTRACT` | Surya adapter/schema validator | historical fixtures, `tmp_path` | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | raw-to-state input boundary only |
| `systems/Parasara/tests/test_vertical_slice_career.py` | pytest | `END_TO_END` | full Career snapshot equality | chart + approved snapshot + `tmp_path` | none | none | Yes | included | targeted pytest file | `TEST_NOT_EXECUTED` | strongest public compatibility guard |
| `tests/determinism_test.py` | pytest | `CONTRACT` | repeated assembled-output hashes | golden chart; writes configured output path through generator | none | none | indirect | included by `*_test.py` | targeted pytest file only after output isolation | `TEST_NOT_EXECUTED` | broad output repeatability, not predicates/Yoga |
| `tests/enrichments/test_aspects.py` | pytest | `UNIT` | aspect graph/evidence | JSON chart/local AstroState | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | ASPECT capability, not registered handler |
| `tests/enrichments/test_parashara_aspects.py` | pytest | `UNIT` | aspect offsets/config | in-memory data | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | provider semantics only |
| `tests/enrichments/test_functional_roles_matrix.py` | pytest | `INTEGRATION` | role tables across lagna | filesystem YAML, synthetic state | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | provider behavior; order/CWD untested |
| `tests/enrichments/test_integration_aspects_consumers.py` | pytest | `INTEGRATION` | aspect consumers/legacy Yoga | chart fixture | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | different Yoga module/API path |
| `tests/enrichments/test_yoga_engine_rule_driven.py` | pytest | `INTEGRATION` | active rule-driven Yoga | chart, YAML, global registries | none | none | No | included | targeted pytest file with isolated globals | `TEST_NOT_EXECUTED` | output IDs/types only |
| `tests/enrichments/test_yoga_loader.py` | pytest | `UNIT` | Yoga load/register/top-level fields | `yogas.yaml`, global registry | none | none | No | included | targeted pytest file with isolated registry | `TEST_NOT_EXECUTED` | partial loader validation |
| `tests/test_framework_integration.py` | pytest | `END_TO_END` | custom regression/report framework | Career goldens; writes report | none | none | Yes | included | unsafe without redirected report path | `TEST_NOT_EXECUTED` | framework smoke only |
| `tests/test_rule_coverage.py` | pytest | `INTEGRATION` | instrumentation coverage scan | golden chart/global loader | none | none | No | included | targeted pytest file with isolated globals | `TEST_NOT_EXECUTED` | non-semantic assertions |
| `tests/dasha/test_vimshottari.py` | pytest | `UNIT` | Dasha structure | golden chart metadata | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | time-capability structure only |
| `tests/dasha/test_vimshottari_boundaries.py` | pytest | `UNIT` | nakshatra fractions | in-memory states | none | none | No | included | targeted pytest file | `TEST_NOT_EXECUTED` | no clock fallback assertion |
| `tests/dasha/test_vimshottari_golden.py` | pytest | `SNAPSHOT_OR_GOLDEN` | Dasha lords/durations | chart + Dasha golden | none | none | Yes | included | targeted pytest file | `TEST_NOT_EXECUTED` | ignores start/end clock behavior |
| `tests/property_tests.py` | pytest/Hypothesis | `PROPERTY` | score ranges | generated chart; fixed output file | none | none | No | **not default-discovered** | unsafe until output uses `tmp_path` | `TEST_NOT_EXECUTED` | indirect capability only |
| `tests/testing_framework/test_case_builder.py` | support module | `TEST_FIXTURE_ONLY` | testcase construction/loading | JSON testcase file | none | none | Yes | importable, zero tests | N/A | `STATIC_FINDING` | no assertions |

External dependencies include pytest, Pydantic, PyYAML, and Hypothesis for the property module. No relevant test has an active pytest marker, skip, or xfail. The repository CI installs `requirements-dev.txt` and runs pytest under Python 3.11, but current CI outcome was not available.

Supporting test-like scripts not counted as test modules include `tests/testing_framework/determinism_audit.py`, `rule_coverage.py`, `snapshot_runner.py`, `json_compare.py`, `generate_full_artifacts.py`, and `systems/Parasara/tools/ci_snapshot_check.py`. They are assessed in later sections because several write fixed artifact paths or provide weaker normalization than their names imply.

## 5. Test Execution Results

| Command | Scope | Executed | Result | Tests Collected | Passed | Failed | Skipped | Xfailed | Duration | Environment Blocker | Files Changed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -p no:cacheprovider tests/rules/test_predicate_result.py -q` | five direct predicate tests | Yes | `TEST_BLOCKED_BY_ENVIRONMENT` | 0 | 0 | 0 | 0 | 0 | 1.3 s | `No module named pytest` under Python 3.13 | none |

No test function executed, so there is no pass/fail evidence from this audit. Static discovery and report validation commands executed successfully. The command disabled bytecode and pytest cache; repository status confirmed only the Audit-22 report was introduced by this task.

## 6. PredicateResult and Supporting-Model Tests

`tests/rules/test_predicate_result.py:14-75` covers returned type, one true match, one false match, cache flag transition, non-null timing, an exception producing at least one error, leaf condition type/match, and `asdict` plus `json.dumps(default=str)`. Assertions are implementation-specific and weak: they do not inspect error codes/details, logical equality, complete evidence, trace, or JSON content.

Missing model scenarios total 22: required/default fields; invalid fields/types; predicate version; status membership/serialization; matched/status invariants; deep immutability; nested mutation rejection; defensive copying; logical equality/hashability; normalization; telemetry separation; canonical JSON; round trip; repeated serialization; unsupported values; stable PredicateError codes/recoverability/safe conversion/immutable details; and PredicateTraceStep ordering/immutability. PredicateStatus, PredicateError, PredicateTraceStep, and ConditionResult do not exist and therefore have no tests.

The existing exception test preserves raw mutable error-list behavior, and the serialization test endorses `default=str`; both are `LEGACY_BEHAVIOR_ONLY` for the future contract.

## 7. Registered Predicate Tests

| Predicate ID | Test Files | Matched | Unmatched | Invalid Params | Missing Capability | Missing Entity | Exception | Evidence | Trace | Cache | Purity | Determinism | Coverage Status | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ASPECT` | enrichment aspect tests only | indirect provider | No | No | No | No | No | provider edges only | provider trace, not predicate | No | No | provider repeated graph once | `NO_COVERAGE` | P0 |
| `ASPECT_EXISTS` | none direct | No | No | No | No | No | No | No | No | No | No | No | `NO_COVERAGE` | P0 |
| `PLANET_IN_HOUSE` | `test_predicate_result.py` | Yes | No | No | No | No | No | only ID/match | empty unchecked | flag only | No | No | `PARTIALLY_COVERED` | P0 |
| `HOUSE_OCCUPANT` | Yoga integration indirectly | weak indirect | No | No | No | No | No | dict type only downstream | UUID nonempty downstream | indirect global clear | No | No | `WEAK_ASSERTIONS` | P0 |
| `FUNCTIONAL_ROLE` | provider/table tests; Yoga indirect | provider behavior | No direct | No | No | No | No | provider role only | No | No | No I/O/purity test | No | `LEGACY_BEHAVIOR_ONLY` | P0 |
| `PLANET_EXALTED` | `test_predicate_result.py` | No | Yes | No | No | missing planet not distinguished | No | empty error only | No | No | No | No | `WEAK_ASSERTIONS` | P0 |

Coverage counts are full 0, partial 1, weak 2, legacy-only 1, and no coverage 2. None covers predicate version, invalid/unknown parameters, capability status, complete matched/unmatched evidence, typed trace, purity, or repeated logical equality. The synthetic `RAISE_TEST` handler covers only “some error exists” and does not establish any registered predicate's exception behavior.

## 8. Registry Tests

The exception test dynamically registers `RAISE_TEST` and removes it afterward (`test_predicate_result.py:39-55`), proving only that decorator insertion can make a callable reachable. Cleanup is not protected by `finally`, no cache entry is removed, and no registry fixture isolates failures.

Eighteen registry scenarios are missing: required ID/version; callable validation; duplicate rejection and compatibility; aliases; case/whitespace normalization; parameter schemas; required capabilities; cacheable/deterministic metadata; system/plugin scope; deprecation/replacement; deterministic enumeration; import-order behavior; test registration isolation; reset/freeze; and registry/cache invalidation. Yoga loader registration tests exercise the rule registry, not predicate metadata.

## 9. Parameter and Capability Tests

Parameter-validation gaps total 17: missing required, explicit None, wrong types, invalid ranges/values, unknown keys, aliases, conflicts, defaults, case normalization, planet identity, house 1–12, role values, bool/int ambiguity, numeric strings, canonical result inputs, canonical cache identity, and unsupported/nonfinite/custom values. Existing predicate tests supply only valid dictionaries.

Capability gaps total 12: present/true; present/false; missing; None; empty; malformed; missing entity with capability present; version mismatch; missing capability distinct from unmatched; preparation before evaluation; no recomputation; and no state mutation. Aspect/functional-role tests validate providers but do not call each registered predicate through the generic evaluator across these states.

## 10. AstroState Boundary and Purity Tests

`test_astrostates_enforced.py:5-32` is the only executable architecture test. It checks `Chart` references under interpreters, not predicates, Yoga, rules, or direct raw Surya access. Normalizer/derived tests assert structure and selected values but not predicate readiness, immutability, digest, or isolation.

Combined AstroState/purity gaps total 21: normalized-only predicate access; no raw Surya access across predicate modules; readiness lifecycle; deep state immutability; caller-input isolation; deterministic/equivalent/different-state digest behavior; version coverage; no memory identity; evaluation-order independence; no AstroState/enrichment/parameter/nested-value/global mutation; no implicit clock/randomness/I/O/external service; no enrichment execution; and no domain scoring/narrative. No fixture snapshots state before/after predicate calls.

## 11. Cache Tests

`test_planet_in_house_true_and_cache` verifies only cold `cache_hit=False`, warm `cache_hit=True`, and non-null cold timing. It does not compare logical fields. Seventeen cache scenarios remain: cold/warm logical, evidence, error, and trace equality; predicate-version isolation; state-digest isolation; equivalent-state behavior; parameter canonicalization; context isolation; capability/enrichment versions; mutation protection; invalid/error caching policy; stale missing-capability recovery; clear/lifecycle; test isolation; concurrency; and cached-object immutability.

The current test explicitly preserves cache flag variability without verifying the Prompt-01 rule that telemetry is excluded from deterministic logical comparisons.

## 12. Condition Evaluator and Format Tests

One leaf delegation test verifies a PredicateResult and true match (`test_predicate_result.py:58-64`). There are no direct AND, OR, NOT, nested, eager/short-circuit, order, skipped, child-preservation, status, evidence, error, trace, unknown predicate/operator, empty/malformed, cycle/depth, or format-variant tests. Nineteen missing scenario groups are counted.

Yoga integration incidentally evaluates current AND/OR YAML, but assertions only check rule IDs, dictionary evidence, and nonempty UUIDs. They do not establish logical semantics or distinguish loader/compiler formats.

## 13. Rule Loader and Validation Tests

`test_yoga_loader.py` proves three IDs load, one rule is globally registered, and missing top-level fields raise. `test_rule_runtime_merge.py` proves generic loader provenance appears in a legacy runtime context. Neither covers deterministic file discovery, malformed/JSON inputs, duplicates, condition AST validation, predicate metadata, source locations, or compile/runtime agreement.

Fourteen loader gaps remain: YAML and JSON policy; malformed source; condition normalization; known/unknown predicates; parameter schema/version/capability checks; logical-operator validation; duplicate rule IDs; deterministic registry initialization; multi-file order; source diagnostics; raw-runtime bypass prevention; CI linter/runtime parity; and stale imported-registry behavior. Future DSL compilation beyond Prompt-01 is excluded.

## 14. Yoga Integration Tests

`test_yoga_engine_rule_driven.py:17-37` reaches the active `evaluate_yoga_rules` path but asserts presence of three rule IDs, evidence dictionary type, and nonempty trace ID—not whether rules matched. It therefore treats matched and unmatched rows alike and accepts random UUIDs. `test_integration_aspects_consumers.py` exercises a different Yoga API path and cannot prove generic predicate integration.

Thirteen Yoga gaps remain: registry/generic evaluator use as enforced architecture; actual match; non-match; missing capability; invalid parameters; predicate error; evidence/error/trace preservation; inactive tuple evaluator/bypass prohibition; no state mutation; deterministic rule/planet ordering and trace identity; cache compatibility; and repeated output equality.

## 15. Domain Integration Tests

Career structure and snapshot tests cover score/confidence ranges, component/indicator/evidence list shapes, indicator IDs, and one exact full snapshot. They do not prove that Career consumes generic PredicateResult/ConditionResult; current Career remains on legacy RuleMatch dictionaries.

Twelve domain gaps remain: generic predicate integration; no direct-handler/runtime bypass; no tuple/raw-boolean contract; matched/unmatched; missing capability; typed error behavior; evidence/trace preservation; scoring compatibility under adapter migration; confidence compatibility; cold/warm equivalence; deterministic repeated output at the domain boundary; and explicit public serialization compatibility. Other domains are stubbed and not expanded into future behavior tests.

## 16. Error, Evidence and Trace Tests

The exception test checks only `len(errors) >= 1`. Predicate evidence is not asserted at all. Aspect provider trace tests concern enrichment trace dictionaries, while Yoga tests require a nonempty random ID. No predicate trace-step content is tested.

Fifteen consolidated scenario gaps remain: stable error codes/messages/details/recoverability; raw exception/stack safety; status/error propagation; deterministic error ordering; matched and unmatched expected/actual evidence; missing-capability evidence; evidence immutability/JSON safety/order; typed trace steps; parent-child identities; deterministic step order; short-circuit/skipped traces; cold/warm logical trace; and Yoga/domain preservation.

## 17. Serialization Tests

The sole direct result test uses `asdict` and `json.dumps(default=str)` and asserts only that a string is returned. Snapshot tests validate selected or full current outputs but not PredicateResult, condition results, model round trips, or internal/public separation.

Thirteen serialization gaps remain: canonical result JSON; stable enum values; immutable mappings; tuple normalization; telemetry exclusion; condition serialization; Yoga typed adapter; domain/output adapter; round trip; deterministic repeated serialization; public/internal filtering; schema-version compatibility; and unsupported/non-JSON-safe value rejection.

## 18. Determinism Tests

`tests/determinism_test.py:7-15` repeats the assembled snapshot and compares sorted-key JSON hashes. The snapshot hardcodes Yoga empty and does not expose PredicateResult/cache telemetry. It does not compare equivalent states, subprocesses, load order, test order, or concurrency. Its generator/output behavior also requires isolation before safe execution.

Eleven determinism gaps remain: direct repeated predicate evaluation; equivalent AstroState instances; cold/warm logical equivalence; explicit context time; no implicit clock; no random logical IDs; semantic collection ordering; test/load-order independence; cross-process stability; serial/parallel equivalence if supported; and canonical logical serialization/snapshot comparison. Audit-21's 26 fine-grained categories map into these eleven consolidated requirement groups.

## 19. Architecture Enforcement Tests

| Requirement | Enforcement Type | File | Symbol/Rule | Active in CI | Bypass Risk | Coverage Status | Missing Enforcement | Priority |
|---|---|---|---|---|---|---|---|---|
| Interpreters do not reference raw `Chart` | AST pytest | `systems/Parasara/tests/test_astrostates_enforced.py` | `test_interpreters_do_not_use_chart_directly` | configured by wildcard; current result unknown | scan limited to interpreter directory/name patterns | `PARTIALLY_COVERED` | extend boundary contract beyond `Chart` identifier | P1 |
| No active tuple-return predicate | none | — | — | No | legacy adapters remain | `NO_COVERAGE` | AST/registry contract check | P0 |
| No raw-boolean predicate | none | — | — | No | legacy runtime primitives remain | `NO_COVERAGE` | callable return-contract enforcement | P0 |
| No tuple-unpacking caller | none | — | — | No | caller bypass can reappear | `NO_COVERAGE` | static architecture rule | P1 |
| No prohibited direct-handler bypass | none | — | — | No | Yoga/domain parallel paths | `NO_COVERAGE` | call-graph/static rule | P0 |
| No predicate import of domain interpreters | none | — | — | No | layer inversion | `NO_COVERAGE` | import rule | P1 |
| No raw Surya access in predicates | none | — | — | No | boundary bypass | `NO_COVERAGE` | import/AST rule | P0 |
| No enrichment execution in predicates | none | — | — | No | `FUNCTIONAL_ROLE` currently violates | `NO_COVERAGE` | call/import rule | P0 |
| No AstroState mutation during evaluation | none | — | — | No | Yoga mutates state | `NO_COVERAGE` | before/after contract plus static check | P0 |
| No untyped predicate errors | none | — | — | No | mutable dict errors remain | `NO_COVERAGE` | model/return inspection | P0 |
| Logical operators are not registered predicates | none | — | — | No | namespace collision | `NO_COVERAGE` | registry metadata rule | P1 |
| All predicates declare required metadata | none | — | — | No | registry stores callables only | `NO_COVERAGE` | registry completeness test | P0 |

Eleven architecture-enforcement gaps are counted. The existing interpreter test is useful but partial; CI configuration includes it only if collection succeeds.

## 20. Test Quality and Isolation

Assertion weaknesses include type/presence checks instead of semantics, `assert 'Moon' in targets or True` in `tests/enrichments/test_aspects.py:59`, coverage counts constrained only to be nonnegative, Yoga IDs checked for presence rather than deterministic value, and Career snapshots often comparing indicator IDs only.

Five mutable/leaking fixture risks are counted:

1. process-global predicate registration/cache with manual, non-finally cleanup;
2. process-global rule/Yoga registries with no fixture reset;
3. mutable AstroState/enrichment objects reused within integration calls without before/after guards;
4. fixed paths such as `tests/tmp_snapshot.json` and `tests/tmp_prop_chart.json`;
5. CI/framework generators that write repository-root or `tests/reports` artifacts during validation.

Six nondeterministic-test risks are counted: performance timing asserted only as non-null; random Yoga UUID accepted; filesystem `os.listdir`/YAML/global registry order; parallel CI against shared globals/fixed files; divergent float/key/list normalization; and repeated-output testing that excludes the active Yoga result and logical cache projection.

No relevant skip/xfail protects missing dependencies. `pytest -n auto || pytest` can mask a parallel-only failure by passing serially, and CI report/snapshot-PR steps use `|| true`, so auxiliary validation failures do not fail the job.

## 21. Snapshot and Golden Tests

Six snapshot/golden impacts are counted:

| Artifact | Generator | Consumer | Data Covered | Telemetry/Normalization | Contract | Prompt-01 Impact |
|---|---|---|---|---|---|---|
| `systems/Parasara/tests/snapshots/output_golden_chart_01.json` | `generate_snapshot.generate` | vertical slice and CI comparator | full current public output | generated_at null; writer sorts keys; CI rounds floats | public/golden | exact structural changes |
| Career fixture family under `systems/Parasara/tests/fixtures/` | generator/manual | Career/additional tests | indicators and selected domain output | list order retained | compatibility golden | typed adapter may alter IDs/evidence/scores |
| `tests/dasha/golden_vimshottari_01.json` | manual/generator | Dasha golden test | lord/duration only | ignores start/end clock fallback | internal golden | does not catch implicit time |
| `tests/tmp_snapshot.json` | snapshot runner | framework comparisons | generated full/domain output | comparator ignores selected keys/tolerance | untracked/fixed temp contract | leaking fixed path |
| rule/domain/explainability artifacts under `tests/reports` | full-artifact generator | reports/SME/CI upload | legacy rule traces/domain summaries | registry/list order retained | persisted internal | migration changes shape/order |
| public JSON schema plus CI snapshot workflow | manual schema/CI generator | CI/public consumers | coarse output schema and approved snapshot | normalization differs from exact test | public contract | no PredicateResult/status/version schema |

No snapshot was generated or updated. Update/sign/PR helpers are explicitly unsafe for this audit. `ci_snapshot_check.py` writes `tmp_generated_snapshot.json` when `--out` is omitted, so its CI validation is not read-only.

## 22. Prompt-01 Requirement Traceability

| Requirement | Source | Existing Tests | Test Symbols | Coverage Status | Missing Scenarios | Assertion Strength | Recommended Test File | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|---|---|---|
| Typed immutable PredicateResult | Prompt-01; Audits 5–6 | predicate result file | five symbols | `LEGACY_BEHAVIOR_ONLY` | fields/status/version/deep immutability | Weak | `tests/rules/test_predicate_models.py` | `IN_SCOPE` | P0 | Yes |
| PredicateStatus invariants | Prompt-01; Audit 5 | none | — | `NO_COVERAGE` | enum/matched consistency/serialization | None | `tests/rules/test_predicate_models.py` | `IN_SCOPE` | P0 | Yes |
| Typed PredicateError | Prompt-01; Audit 17 | exception weak test | `test_predicate_exception_becomes_structured_failure` | `WEAK_ASSERTIONS` | codes/details/recovery/safety | Weak | `tests/rules/test_predicate_errors.py` | `IN_SCOPE` | P0 | Yes |
| Typed PredicateTraceStep | Prompt-01; Audit 19 | none | — | `NO_COVERAGE` | construction/order/immutability/lineage | None | `tests/rules/test_predicate_traces.py` | `IN_SCOPE` | P0 | Yes |
| Complete registry metadata | Prompt-01; Audit 1 | dynamic registration only | exception test decorator | `LEGACY_BEHAVIOR_ONLY` | all metadata/lifecycle | Weak | `tests/rules/test_predicate_registry.py` | `IN_SCOPE` | P0 | Yes |
| Six registered predicate behaviors | Audits 2,18 | one matched, one unmatched, indirect providers | listed Section 7 | `WEAK_ASSERTIONS` | complete positive/negative/error matrices | Weak | `tests/rules/test_registered_predicates.py` | `IN_SCOPE` | P0 | Yes |
| Parameter validation/canonicalization | Prompt-01; Audit 7 | none | — | `NO_COVERAGE` | 17 categories | None | `tests/rules/test_predicate_parameters.py` | `IN_SCOPE` | P0 | Yes |
| Capability/status handling | Prompt-01; Audit 8 | provider tests only | enrichment tests | `LEGACY_BEHAVIOR_ONLY` | 12 predicate-level states | Weak | `tests/rules/test_predicate_capabilities.py` | `IN_SCOPE` | P0 | Yes |
| AstroState digest/boundary | Architecture; Audit 9 | normalizer plus interpreter AST | several | `PARTIALLY_COVERED` | readiness/digest/identity/order | Mixed | `tests/rules/test_predicate_astrostate_boundary.py` | `IN_SCOPE` | P0 | Yes |
| Predicate purity | Prompt-01; Audit 10 | none direct | — | `NO_COVERAGE` | mutation/I/O/time/random/enrichment | None | `tests/rules/test_predicate_purity.py` | `IN_SCOPE` | P1 | Yes |
| Typed digest/version cache | Prompt-01; Audit 11 | flag-only cache test | `test_planet_in_house_true_and_cache` | `WEAK_ASSERTIONS` | 17 scenarios | Weak | `tests/rules/test_predicate_cache.py` | `IN_SCOPE` | P0 | Yes |
| Typed condition semantics | Prompt-01; Audits 12–13 | leaf only; Yoga indirect | leaf test | `WEAK_ASSERTIONS` | operators/nesting/status/preservation | Weak | `tests/rules/test_condition_evaluator.py` | `IN_SCOPE` | P0 | Yes |
| Rule load/compile validation | Prompt-01; Audit 14 | Yoga loader/provenance | four tests | `PARTIALLY_COVERED` | deterministic semantic validation | Moderate top-level only | `tests/rules/test_rule_validation.py` | `IN_SCOPE` | P0 | Yes |
| Yoga generic integration | Prompt-01; Audit 15 | Yoga rule-driven | one test | `WEAK_ASSERTIONS` | match/error/preservation/isolation | Weak | `tests/enrichments/test_yoga_predicate_integration.py` | `IN_SCOPE` | P0 | Yes |
| Domain compatibility | Prompt-01; Audit 16 | Career structure/snapshots | four tests | `PARTIALLY_COVERED` | typed integration/cold-warm/errors | Moderate shape only | `systems/Parasara/tests/test_career_predicate_compatibility.py` | `TEMPORARY_COMPATIBILITY` | P1 | Yes |
| Deterministic factual evidence | Prompt-01; Audit 18 | provider traces/types | enrichment/Yoga tests | `LEGACY_BEHAVIOR_ONLY` | expected/actual/immutable/order | Weak | `tests/rules/test_predicate_evidence.py` | `IN_SCOPE` | P1 | Yes |
| Canonical serialization/round trip | Prompt-01; Audit 20 | default-str plus snapshots | serialization test | `LEGACY_BEHAVIOR_ONLY` | canonical/internal/public/round trip | Weak | `tests/rules/test_predicate_serialization.py` | `IN_SCOPE` | P1 | Yes |
| End-to-end determinism | Prompt-01; Audit 21 | output hash | `test_determinism_runs` | `PARTIALLY_COVERED` | predicate/cache/Yoga/process/order | Moderate but wrong boundary | `tests/rules/test_predicate_determinism.py` | `IN_SCOPE` | P1 | Yes |
| Architecture enforcement | Master Architecture; Audits 1–21 | one interpreter AST test | one symbol | `PARTIALLY_COVERED` | 11 rules | Moderate narrow scan | `systems/Parasara/tests/test_predicate_architecture.py` | `IN_SCOPE` | P1 | Yes |
| Snapshot/public compatibility | Audits 16,20 | exact/ID snapshots and CI script | snapshot tests | `PARTIALLY_COVERED` | schema/version/telemetry policy | Mixed | `systems/Parasara/tests/test_output_schema_compatibility.py` | `TEMPORARY_COMPATIBILITY` | P2 | No |

## 23. Consolidated Test-Gap Register

| Gap ID | Area | Missing Scenario | Confirmed By Audits | Existing Partial Coverage | Risk | Recommended Test File | Recommended Level | Scope | Priority | Blocks Implementation | Blocks Completion |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G01 | result model | complete typed construction/invariants | 5,6,22 | current dataclass type | invalid contract migration | `test_predicate_models.py` | CONTRACT | `IN_SCOPE` | P0 | Yes | Yes |
| G02 | status | enum and matched/status consistency | 5,17 | none | error becomes factual nonmatch | `test_predicate_models.py` | CONTRACT | `IN_SCOPE` | P0 | Yes | Yes |
| G03 | error model | stable typed safe errors | 6,17 | some error exists | unsafe/unstable diagnostics | `test_predicate_errors.py` | CONTRACT | `IN_SCOPE` | P0 | Yes | Yes |
| G04 | trace model | typed ordered immutable steps | 6,19 | UUID/nonempty provider traces | no auditable lineage | `test_predicate_traces.py` | CONTRACT | `IN_SCOPE` | P0 | Yes | Yes |
| G05 | immutability | deep freeze/copy/hash behavior | 5,6,18 | frozen outer dataclass only | cache/result mutation | `test_predicate_immutability.py` | CONTRACT | `IN_SCOPE` | P0 | Yes | Yes |
| G06 | registry metadata | version/schema/capability/cache flags | 1 | dynamic name registration | incomplete identity | `test_predicate_registry.py` | CONTRACT | `IN_SCOPE` | P0 | Yes | Yes |
| G07 | registry lifecycle | duplicates/freeze/import/reset/isolation | 1,14,21 | manual pop only | test/load-order drift | `test_predicate_registry.py` | ARCHITECTURE | `IN_SCOPE` | P0 | Yes | Yes |
| G08 | parameters | validation and canonicalization matrix | 7,11 | valid dictionaries only | silent false/cache collision | `test_predicate_parameters.py` | CONTRACT | `IN_SCOPE` | P0 | Yes | Yes |
| G09 | capabilities | status distinctions/readiness/version | 8,9 | provider tests | missing facts misclassified | `test_predicate_capabilities.py` | CONTRACT | `IN_SCOPE` | P0 | Yes | Yes |
| G10 | AstroState identity | digest/equivalence/version/isolation | 9,11,21 | normalizer shapes | stale/wrong cache selection | `test_predicate_astrostate_boundary.py` | CONTRACT | `IN_SCOPE` | P0 | Yes | Yes |
| G11 | purity | no mutation/I/O/time/random/recompute | 10 | no direct tests | hidden inputs/side effects | `test_predicate_purity.py` | ARCHITECTURE | `IN_SCOPE` | P1 | No | Yes |
| G12 | cache identity | digest/version/context/canonical key | 11 | flag transition | stale logical result | `test_predicate_cache.py` | CONTRACT | `IN_SCOPE` | P0 | Yes | Yes |
| G13 | cache equivalence | logical/evidence/error/trace cold-warm | 11,18,19,21 | cache flags | warmth changes logical content | `test_predicate_cache.py` | CONTRACT | `IN_SCOPE` | P1 | No | Yes |
| G14 | condition operators | AND/OR/NOT/nested/order/short circuit | 12,13 | leaf only | rule firing changes | `test_condition_evaluator.py` | CONTRACT | `IN_SCOPE` | P0 | Yes | Yes |
| G15 | condition preservation | status/children/evidence/errors/traces | 12,17–19 | Yoga dict type | semantic loss | `test_condition_evaluator.py` | CONTRACT | `IN_SCOPE` | P1 | No | Yes |
| G16 | loader/compiler | deterministic semantic validation | 13,14 | top-level Yoga fields | invalid rules activate/order drifts | `test_rule_validation.py` | CONTRACT | `IN_SCOPE` | P0 | Yes | Yes |
| G17 | Yoga path | enforce registry/generic evaluator/no bypass | 4,15 | active integration call | parallel legacy semantics | `test_yoga_predicate_integration.py` | INTEGRATION | `IN_SCOPE` | P0 | Yes | Yes |
| G18 | Yoga safety | match/nonmatch/errors/preservation/order/state/cache | 15,17–21 | IDs/types only | nondeterministic/mutating output | `test_yoga_predicate_integration.py` | INTEGRATION | `IN_SCOPE` | P1 | No | Yes |
| G19 | domain compatibility | typed integration/scoring/confidence/cold-warm | 16 | Career snapshots | public score regression | `test_career_predicate_compatibility.py` | INTEGRATION | `TEMPORARY_COMPATIBILITY` | P1 | No | Yes |
| G20 | error behavior | unknown/invalid/exception/precedence/strict mode | 17 | synthetic exception | swallowed/raw errors | `test_predicate_errors.py` | CONTRACT | `IN_SCOPE` | P1 | No | Yes |
| G21 | evidence | complete factual expected/actual/immutability | 18 | provider evidence shapes | misleading/nonrepeatable facts | `test_predicate_evidence.py` | CONTRACT | `IN_SCOPE` | P1 | No | Yes |
| G22 | trace behavior | lineage/skips/cache/Yoga preservation | 19 | random IDs only | unauditable execution | `test_predicate_traces.py` | CONTRACT | `IN_SCOPE` | P1 | No | Yes |
| G23 | serialization | canonical JSON/round trip/unsupported values | 20 | `default=str` | lossy/unstable wire format | `test_predicate_serialization.py` | CONTRACT | `IN_SCOPE` | P1 | No | Yes |
| G24 | public schema | versioned internal/public field policy | 20 | snapshots/skeletal schema | consumer breakage/leakage | `test_output_schema_compatibility.py` | CONTRACT | `TEMPORARY_COMPATIBILITY` | P2 | No | No |
| G25 | determinism | repeat/state/cache/order/process scenarios | 21 | assembled output hash | nondeterminism survives | `test_predicate_determinism.py` | CONTRACT | `IN_SCOPE` | P1 | No | Yes |
| G26 | concurrency | registry/cache/state serial-parallel policy | 11,21 | none | races/order differences | `test_predicate_concurrency.py` | INTEGRATION | `IN_SCOPE` | P2 | No | No |
| G27 | architecture | eleven missing executable rules | 1–21 | interpreter Chart scan | regressions bypass contract | `test_predicate_architecture.py` | ARCHITECTURE | `IN_SCOPE` | P1 | No | Yes |
| G28 | fixtures | prepared/missing/malformed/equivalent isolated states | 7–11,22 | ad hoc local states | gaps hard to test/reuse leaks | `tests/rules/conftest.py` | TEST_FIXTURE_ONLY | `IN_SCOPE` | P1 | No | Yes |
| G29 | snapshot governance | one normalization/update/telemetry policy | 16,20,21 | exact and tolerant paths differ | false pass/failure | `test_snapshot_contract.py` | SNAPSHOT_OR_GOLDEN | `TEMPORARY_COMPATIBILITY` | P2 | No | No |
| G30 | cross-process | subprocess logical serialization equality | 20,21 | none | process identity/repr drift | `test_predicate_determinism.py` | INTEGRATION | `IN_SCOPE` | P2 | No | No |
| G31 | explicit Dasha clock | missing/invalid birth time injection | 21 | structure/golden durations | wall-clock logical drift | `test_vimshottari_context.py` | CONTRACT | `OUT_OF_SCOPE_FUTURE_STAGE` | P3 | No | No |
| G32 | future inference/domains | universal typed trace/serialization integration | 16,19,20 | Career legacy only | later-stage incompatibility | future domain suites | INTEGRATION | `OUT_OF_SCOPE_FUTURE_STAGE` | P3 | No | No |

Totals: 32 gap groups; P0=14, P1=12, P2=4, P3=2. The following area counts are finer missing-scenario counts and intentionally overlap the consolidated groups: model 22, registry 18, parameters 17, capabilities 12, AstroState/purity 21, cache 17, condition 19, loader 14, Yoga 13, domain 12, error/evidence/trace 15, serialization 13, determinism 11, architecture enforcement 11.

## 24. Priority and Recommended Test Locations

P0 tests should precede risky implementation: typed models/status/errors/traces, registry metadata/lifecycle, parameter/capability validation, canonical state identity, cache identity, complete condition operators, loader validation, and Yoga path enforcement. These protect existing valid facts while preventing silent preservation of noncompliant behavior.

P1 tests complete Prompt-01: purity, cache logical equivalence, condition preservation, Yoga/domain compatibility, error/evidence/trace semantics, canonical serialization, determinism, architecture rules, and isolated fixtures. P2 covers public schema/snapshot governance, concurrency policy, and subprocess checks. P3 remains with Dasha context and future universal domain/inference stages.

Recommended organization:

- `tests/rules/` for models, registry, parameters, capabilities, cache, conditions, errors, evidence, trace, serialization, determinism, purity, and concurrency;
- `tests/enrichments/test_yoga_predicate_integration.py` for Yoga compatibility;
- `systems/Parasara/tests/test_career_predicate_compatibility.py` for current domain regression;
- `systems/Parasara/tests/test_predicate_architecture.py` for static enforcement;
- `tests/rules/conftest.py` for fresh prepared/missing/malformed/equivalent state fixtures;
- existing snapshot directories only after an explicit approval workflow.

## 25. Unresolved Testing Questions

1. Which P0 tests must be written against the approved target models before implementation versus introduced atomically with those models?
2. What is the canonical logical comparison projection for cache/determinism tests, and which telemetry fields are excluded?
3. What exact semantic ordering should tests assert for conditions, evidence, Yoga rows, errors, traces, and domain contributions?
4. Should the registry expose a supported isolated test registry/reset API, or should tests construct independent registry instances?
5. Is concurrent evaluation supported in Prompt-01; if not, should architecture tests assert explicit rejection?
6. Which legacy Career snapshot fields must remain byte/structure compatible during the typed adapter migration?
7. Should `tests/property_tests.py` be renamed for collection and rewritten to use `tmp_path`, or remain an explicit optional suite?
8. Should CI fail rather than fall back to serial execution when parallel-only race failures occur?
9. Should snapshot CI require an explicit temporary output path and fail auxiliary report/snapshot automation instead of using `|| true`?
10. What current CI run is authoritative for baseline pass/fail evidence before Prompt-01 changes begin?

## 26. Audit-22 Conclusion

Audit-22 is COMPLETE. Twenty-eight relevant test/test-support modules contain 45 test functions, classified as 9 unit, 4 contract, 7 integration, 1 architecture, 1 property, 3 snapshot/golden, 2 end-to-end, and 1 fixture-only module. The isolated five-test command was blocked before collection because pytest is unavailable; executed/passed/failed/skipped/xfailed test counts are all zero.

Across six registered predicates, coverage is full 0, partial 1, weak 2, legacy-only 1, and none 2. Fine-grained scenario gaps are model 22, registry 18, parameters 17, capabilities 12, AstroState/purity 21, cache 17, condition 19, loader 14, Yoga 13, domain 12, error/evidence/trace 15, serialization 13, determinism 11, and architecture 11. Five fixture-isolation risks, six nondeterministic-test risks, and six snapshot/golden impacts were recorded. The 32 consolidated gap groups total 14 P0, 12 P1, 4 P2, and 2 P3. Exactly this report was created; Audit-23 was not started.

| Metric | Count |
|---|---:|
| Prompt-01-relevant test/test-support modules | 28 |
| Statically discovered test functions | 45 |
| Default-discoverable test functions among them | 44 |
| Unit modules | 9 |
| Contract modules | 4 |
| Integration modules | 7 |
| Architecture modules | 1 |
| Property modules | 1 |
| Snapshot/golden modules | 3 |
| End-to-end modules | 2 |
| Fixture-only modules | 1 |
| Tests executed | 0 |
| Tests passed | 0 |
| Tests failed | 0 |
| Tests skipped | 0 |
| Tests xfailed | 0 |
| Registered predicates | 6 |
| Predicates fully covered | 0 |
| Predicates partially covered | 1 |
| Predicates with weak assertions | 2 |
| Predicates with legacy-only coverage | 1 |
| Predicates with no coverage | 2 |
| Model test gaps | 22 |
| Registry test gaps | 18 |
| Parameter-validation gaps | 17 |
| Capability gaps | 12 |
| AstroState/purity gaps | 21 |
| Cache gaps | 17 |
| Condition gaps | 19 |
| Loader gaps | 14 |
| Yoga integration gaps | 13 |
| Domain integration gaps | 12 |
| Error/evidence/trace gaps | 15 |
| Serialization gaps | 13 |
| Determinism gaps | 11 |
| Architecture-enforcement gaps | 11 |
| Mutable or leaking fixture risks | 5 |
| Nondeterministic test risks | 6 |
| Snapshot/golden impacts | 6 |
| Consolidated test-gap groups | 32 |
| P0 test gaps | 14 |
| P1 test gaps | 12 |
| P2 test gaps | 4 |
| P3 test gaps | 2 |
