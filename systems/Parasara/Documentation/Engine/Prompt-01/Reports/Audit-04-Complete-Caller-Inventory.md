# Prompt-01 Audit-04: Complete Caller Inventory

## 1. Executive Summary

This audit identifies **47 caller/consumer symbols or configuration surfaces** across the central predicate engine, Yoga, legacy rule runtime, Career, output assembly, CLI/API integration, CI, tests, and tooling. The inventory counts **22 direct callers** of an audited predicate/evaluator/helper API and **25 indirect or dynamically resolved consumers**. Eighteen are on active production paths, twenty-seven are test/tool-only paths, one is dormant but referenced, and one is confirmed unused.

The active central chain is `yogas.yaml -> evaluate_yoga_rules -> evaluate_condition -> evaluate_predicate -> registry handler`. No repository code directly calls one of the five registered handler functions outside `evaluate_predicate`; the **registered-handler bypass count is zero**. The central chain is nevertheless not migration-safe: logical aggregation reduces child results, and Yoga consumes only `.matched` and `.evidence`.

The active legacy chain is `Career -> evaluate_rule_with_score -> evaluate_rule/inline facts -> raw bool or dictionaries`. It bypasses the registry without directly invoking registered handlers. That chain reaches the snapshot generator, Python API runner, frontend HTTP route, CI snapshots, and regression tests, so a contract change can alter Career score, confidence, indicators, evidence, public JSON, and golden outputs.

Countable findings total **4 P0, 7 P1, 4 P2, and 2 P3**. Twenty-three caller rows require direct migration; none has unknown migration status. No production code, tests, rules, fixtures, snapshots, or prior reports were modified.

## 2. Audit Scope and Method

The audit read the three prior reports and applied the Master Architecture predicate/rule boundaries and Prompt-01 sections 3-31 and 35-37. Repository-wide searches covered Python, TypeScript, YAML/YML, JSON artifacts, GitHub workflows, tests, scripts, decorators, imports/re-exports, registry access, evaluator calls, cache calls, field access, serialization, tuple unpacking, raw truthiness, mocks/monkeypatches, and direct handler names.

Caller counting is symbol/surface based. A function is counted once even if it calls an API repeatedly. Closely coupled tests in one test function are one caller; separate test functions are separate callers. Declarative Yoga conditions and the GitHub workflow count as dynamic/configuration surfaces because they initiate execution without a Python call expression. A “direct caller” directly invokes a registered handler through dynamic registry resolution, a predicate/condition evaluator, a legacy predicate-like helper/evaluator, or a domain/Yoga boundary whose return contract is audited. “Indirect/dynamic” means downstream output/serialization, re-export, rule loading, configuration dispatch, or an upstream harness.

Static caller/reference evidence establishes every status; unknown usage count is zero. Tests were not run because Audit-2 already attempted the targeted suite with `python -B -m pytest -p no:cacheprovider ...` and the available interpreter reported `No module named pytest`. No generator was executed because the snapshot/artifact tools write files.

## 3. Reconciliation with Audits 1–3

Audit-1 found one true predicate registry and two bypass mechanisms. Audit-2 found six registered IDs/five handlers and twelve unregistered predicate-like/condition helpers. Audit-3 found five tuple producers, two tuple consumers, four raw-boolean producers, three raw-boolean consumers, and eleven active legacy paths. Audit-4 confirms those counts and adds their complete upstream/downstream caller graph.

No new registered predicate, direct registered-handler call, tuple-unpacking production Yoga caller, mock, monkeypatch, fixture-injected handler, or alternate cache was found. New caller categories beyond the Audit-3 migration inventory are mostly indirect consumers: output assembly, API/frontend serialization, CI, snapshot regression, determinism/performance tooling, and rule-loading/configuration surfaces.

Audit-3 counted `record_predicate` as an active legacy consumer because production `runtime.py` imports it from the test framework. Audit-4 retains that classification. Audit-2 classifies the four raw-boolean primitives as temporary compatibility pending an architecture decision; Audit-4 does not prescribe their automatic deletion, but records every caller that must be preserved or migrated.

## 4. Predicate Registry and Evaluator Callers

`systems/Parasara/engine/rules/predicates.py:12-99` calls `register_predicate` through decorators at module import. This is dynamic registration rather than result consumption. `systems/Parasara/engine/rules/engine.py:54-132` is the sole registry lookup and sole caller of registered handler objects (`fn(...)` at line 79). No test or production module imports or invokes `aspect_exists`, `planet_in_house`, `house_occupant`, `functional_role`, or `planet_exalted` directly.

`evaluate_predicate` expects either `PredicateResult` or legacy tuple. It reads no handler result fields before its type branch, synthesizes timing/cache telemetry, and caches a `dataclasses.replace` copy. Tuple conversion loses source errors/status/trace/version. Unexpected raw bool/dict/None becomes an invalid-return `PredicateResult`.

Direct callers of `evaluate_predicate` are central `evaluate_condition` (`engine.py:160-162`) and four tests in `tests/rules/test_predicate_result.py`: `test_planet_in_house_true_and_cache`, `test_planet_exalted_false`, `test_predicate_exception_becomes_structured_failure`, and `test_predicateresult_serialization`. Tests use `.matched`, `.errors`, `.cache_hit`, or `asdict`; none mutates result data.

## 5. Condition Evaluator Callers

Three symbols call `evaluate_condition`:

- `evaluate_condition` recursively calls itself for `AND`/`OR` (`engine.py:142-159`) and calls `evaluate_predicate` for leaves. It reads child `.matched`, `.evidence`, `.errors`, identity, and timing, but replaces child traces with summaries and drops cache state/status/version/full child objects.
- `evaluate_yoga_rules` calls it for every loaded rule (`yoga_engine.py:150-156`), reading only `.matched` and `.evidence`.
- `test_evaluate_condition_returns_predicate_result` calls it directly and asserts only type and `.matched` (`test_predicate_result.py:58-64`).

Changing logical nodes to `ConditionResult` requires direct migration of all three. Central recursion and Yoga must preserve child results and distinguish errors/missing capabilities from false. The test must assert the new boundary rather than `PredicateResult` identity.

## 6. Direct Predicate-Handler Callers

There is exactly one caller of registered handler objects: `evaluate_predicate`, which retrieves the callable from `PREDICATE_REGISTRY` and invokes it dynamically (`engine.py:58-79`). It is the approved generic boundary, not a bypass.

No direct registered-handler bypass exists. Direct-name searches find only the five definitions; similarly named functional-role enrichment uses are unrelated to handler invocation. The legacy runtime calls its own raw-boolean helpers and recomputes overlapping facts, but never calls registered handler functions.

The direct handler-bypass count reported by this audit is therefore **0**. This does not mean all factual execution is centralized: `runtime.evaluate_rule` and `evaluate_rule_with_score` remain separate dispatchers.

## 7. Yoga Engine Callers

The Yoga call graph is:

```text
systems/Parasara/rules/parashara/v1/yogas.yaml
  -> yoga_loader.load_yoga_rules / RULE_REGISTRY
  -> yoga_engine.evaluate_yoga_rules
  -> engine.evaluate_condition
  -> engine.evaluate_predicate
  -> registered handler
```

YAML condition IDs at `yogas.yaml:14-18,41-45,68-72` are dynamic callers. `ASPECT`, `FUNCTIONAL_ROLE`, and `HOUSE_OCCUPANT` resolve; `HOUSE_LORDS_COMBINATION` does not and becomes a cached unknown/false result. `load_yoga_rules` validates rule-level fields but not predicate IDs or contracts (`yoga_loader.py:21-45`).

`evaluate_yoga_rules` clears the predicate cache, evaluates conditions, keeps match/evidence, discards typed errors/trace/cache/status/version, creates random trace IDs, and writes Yoga matches to `astro.enrichments` (`yoga_engine.py:128-188`). A missing capability or predicate error is therefore liable to be emitted as an ordinary nonmatch.

`systems/Parasara/engine/enrichments/yoga.py:1-3` re-exports `evaluate_yoga_rules`; the Yoga integration test imports this surface and calls it (`tests/enrichments/test_yoga_engine_rule_driven.py:17-37`). The local tuple `_eval_condition` family is confirmed unused; its only caller is self-recursion/local dispatch.

## 8. Domain Runtime Callers

`interpret_career` is the active domain consumer (`systems/Parasara/engine/interpreters/career.py:8-116`). It constructs candidate rule dictionaries, calls `evaluate_rule_with_score`, falls back on any exception to `evaluate_rule`, converts dictionary fields through `bool`/`float`, and supports both `adjusted_score` and legacy `score`. Only matched positive contributions reach indicators/evidence. Predicate errors, missing-capability status, trace, version, and unmatched evidence are unavailable or discarded.

`explainability.evidence_for_rule` consumes a Career-created `{'match','evidence'}` adapter and retains only match, evidence, rule, and contribution (`explainability.py:4-11`). `confidence.compute_rule_coverage` and `compute_evidence_strength` consume rule dictionaries by `matched` and score fields (`confidence.py:35-57`); they do not consume predicate errors/evidence/trace/version.

The output assembler calls Career at `generate_snapshot.py:14-40`. Preserving domain scoring requires the typed migration to keep the exact match and adjusted-score decisions of this chain while adding richer predicate information.

## 9. Rule Loader, Compiler and Rule-Engine Callers

There is no separate rule compiler. `load_yoga_rules` and generic `loader.load_rules_from_dir` populate the mutable `RULE_REGISTRY`; they do not validate conditions against `PREDICATE_REGISTRY`. `evaluate_yoga_rules` dynamically consumes condition trees from that registry.

The legacy rule engine consists of:

- `is_exalted`, which calls raw-boolean `in_sign` (`runtime.py:64-73`);
- `evaluate_rule`, which directly calls four raw-boolean factual helpers and returns `{'match','evidence'}` (`76-108`);
- `evaluate_rule_with_score`, which calls `evaluate_rule` for primitive/fallback types and recomputes other facts inline before serializing `RuleMatch` to dict (`111-269`).

These consumers bypass the central registry, lack predicate versions/status/traces, and collapse many exceptions to `matched=False`. Their migration scope remains the temporary-compatibility decision recorded by Audit-2; callers cannot simply switch return types without preserving rule scoring.

## 10. Inference and Output Consumers

No universal Inference Engine consumes `PredicateResult` directly. Current confidence helpers consume only rule dictionaries. Output propagation is:

```text
interpret_career
  -> generate_snapshot.assemble_output / generate
  -> runner_api.main
  -> frontend POST route
```

`generate` JSON-serializes the full domain dictionary (`generate_snapshot.py:43-50`). `runner_api.main` wraps it with a raw `surya_chart` and serializes stdout (`runner_api.py:90-102`). `frontend/app/api/astro/generate/route.ts:23-69` spawns that runner, parses stdout, and returns JSON. These are active production consumers. They do not inspect predicate fields, but any internal schema/score/evidence change propagates to the public response.

The API runner accesses raw Surya chart data only before/alongside normalization and returns it as a separate output member; no predicate/result consumer accesses raw Surya JSON after receiving a predicate result.

## 11. Cache Consumers

The sole cache implementation and logical reader is `evaluate_predicate` (`engine.py:24-25,39-57,75-76,113-131`). It returns the cached object directly and stores copies with `cache_hit=True`.

`evaluate_yoga_rules` and all five predicate-result test functions call `clear_cache` (`yoga_engine.py:147-148`; `test_predicate_result.py:14-70`). Thus there are seven cache consumers when the evaluator, Yoga, and five tests are counted. Only `test_planet_in_house_true_and_cache` reads `cache_hit`; other callers are insensitive to telemetry today.

Prompt-01 cache changes can break the warm-cache test and any equality/serialization assumptions. Yoga’s per-run clear behavior must be preserved or deliberately replaced with digest/version isolation. Deep immutability is compatible with current code because no caller mutates result fields; only the evaluator creates replacements.

## 12. Serialization Consumers

Nine material serialization consumers are identified:

1. `evaluate_rule_with_score` serializes `RuleMatch` with `model_dump`/`dict` (`runtime.py:263-269`).
2. `test_predicateresult_serialization` uses `dataclasses.asdict` then `json.dumps` (`test_predicate_result.py:67-74`).
3. `generate_snapshot.generate` writes sorted JSON (`generate_snapshot.py:43-50`).
4. `runner_api.main` serializes snapshot plus raw chart (`runner_api.py:90-102`).
5. The frontend route parses and reserializes runner output (`route.ts:51-64`).
6. `ci_snapshot_check.main` normalizes and prints/compares generated JSON (`ci_snapshot_check.py:38-68`).
7. `test_determinism_runs` canonicalizes output with sorted `json.dumps` and hashes it (`tests/determinism_test.py:7-15`).
8. `generate_full_artifacts.run_rules_and_trace` serializes rule dictionaries (`generate_full_artifacts.py:51-79`).
9. `synthesize_domain_prediction` serializes downstream contributor/evidence dictionaries (`generate_full_artifacts.py:82-103`).

Canonical typed serialization may not remain compatible with `asdict`, mutable lists/dicts, Pydantic `.dict`, or current snapshot shapes. Snapshot policy must prevent broad unreviewed golden updates.

## 13. Test, Fixture and Tooling Callers

Direct typed tests are the five functions in `tests/rules/test_predicate_result.py`. Yoga tests call loader and Yoga re-export. Legacy tests directly call primitives/evaluators at `systems/Parasara/tests/test_rule_runtime.py:12-33`, `test_rule_runtime_merge.py:9-19`, and `test_career_interpreter.py:6-17`.

Snapshot/output tests and tools indirectly consume predicate effects:

- `test_additional_snapshots_match`, `test_career_snapshot_matches_golden`, and `test_vertical_slice_matches_snapshot` compare Career indicators or full JSON;
- `test_determinism_runs` hashes full output;
- `snapshot_runner.compare_snapshots`, `regression_runner.run_regression`, and `test_framework_smoke_run` generate/compare output;
- `perf.measure_runs`, `update_and_sign`, `generate_full_report.main`, `surya_to_parasara.main --run-snapshot`, and `ci_snapshot_check.main` invoke the generator;
- `generate_full_artifacts` and `run_rule_coverage_scan` call the legacy runtime directly;
- `.github/workflows/parasara-snapshot-compare.yml:28-32` runs the CI snapshot comparator.

No predicate-related monkeypatch or mock was found. `RAISE_TEST` is the only test-local dynamic predicate; its caller registers, evaluates, reads `.matched/.errors`, and manually removes the global registry entry.

## 14. Legacy and Compatibility Callers

Legacy tuple callers are `evaluate_predicate`’s compatibility branch and unused Yoga `_eval_condition`. Raw-truthiness consumers are `runtime.evaluate_rule`, `evaluate_rule_with_score`, Career, `synthesize_domain_prediction`, and the direct primitive runtime test. The combined tuple-unpacking/raw-truthiness caller count is **7**.

The generic tuple adapter is reachable but has no current production tuple handler. The legacy Yoga tuple caller is confirmed unused. Active raw-boolean/dictionary callers are runtime, Career, instrumentation, artifact generation, and rule coverage.

`record_predicate` is a compatibility consumer with unusual ownership: production runtime imports it from `tests/testing_framework/instrumentation.py:21-25`. It accepts only name plus bool, discarding evidence/errors/status/trace/version and mutating global counters.

## 15. Information-Loss and Error-Handling Boundaries

Twelve caller rows discard evidence entirely or for unmatched paths: Career, both confidence helpers, four typed tests that do not inspect evidence, the legacy evaluator test, two indicator-only snapshot tests, performance tooling, and rule coverage. Three typed-result callers discard available errors: Yoga, the matched/cache test, and the condition test. Five paths treat errors or exceptions as ordinary nonmatches: condition/Yoga aggregation, `evaluate_rule_with_score`, Career fallback, artifact fallback, and snapshot-runner generation failure.

The highest-impact boundaries are:

- condition aggregation reduces full child results (`engine.py:142-159`);
- Yoga drops all fields except match/evidence (`yoga_engine.py:154-177`);
- legacy runtime converts errors/unsupported types to false dictionaries (`runtime.py:76-108,237-240`);
- Career catches every score-wrapper exception and silently falls back (`career.py:47-56`);
- confidence and explainability cannot recover fields already discarded;
- output/snapshot consumers freeze resulting scores/evidence into JSON.

No caller mutates `.inputs`, `.evidence`, `.errors`, or `.trace_steps`. Deep immutability is therefore low direct breakage risk, but callers expecting dictionaries/lists or using `asdict` require serializer/API migration.

## 16. Prompt-01 Compatibility Assessment

### Contract-impact matrix

| Caller | Deep Immutability | Mandatory Version | Typed Status | Typed Errors | Typed Traces | ConditionResult | Tuple Removal | Serialization Change | Regression Risk | Required Action |
|---|---|---|---|---|---|---|---|---|---|---|
| `evaluate_predicate` | Compatible; uses `replace` | Must populate/validate | Must create/preserve | Must type | Must preserve | N/A | Remove/isolate branch | Cache/result serializer changes | High | DIRECT_MIGRATION_REQUIRED |
| `evaluate_condition` | Compatible reads only | Must preserve child | Must aggregate | Must retain typed | Must retain full child trace | Required | Legacy local path unaffected | New condition serializer | High | DIRECT_MIGRATION_REQUIRED |
| `evaluate_yoga_rules` | Reads only | Currently discarded | Currently discarded | Currently discarded | Currently discarded | Must consume | No active tuple | Yoga evidence/trace may change | Critical | DIRECT_MIGRATION_REQUIRED |
| Yoga loader/YAML | N/A | Must validate references | Must permit policies | Loader must surface | N/A | Condition schema changes | N/A | Validation errors change | Critical | INDIRECT_MIGRATION_REQUIRED |
| `evaluate_rule` | N/A bool/dict | Absent | Absent | Absent | Absent | Potential consumer | Raw bool contract remains | Dict shape may change | Critical | DIRECT_MIGRATION_REQUIRED / boundary decision |
| `evaluate_rule_with_score` | Dict/model boundary | Predicate version absent | Discarded | Collapsed | Absent | Potential consumer | Must not rely on bool | Rule serialization must remain stable | Critical | DIRECT_MIGRATION_REQUIRED |
| `interpret_career` | Dict reads only | Discarded | Discarded | Broad fallback | Discarded | Indirect | Raw bool/dict fallback removal | Public domain JSON sensitive | Critical | DIRECT_MIGRATION_REQUIRED |
| Explainability | Dict reads only | Discarded | Discarded | Discarded | Discarded | Indirect | N/A | Evidence schema sensitive | High | DIRECT_MIGRATION_REQUIRED |
| Confidence helpers | Dict reads only | Ignored | `matched` only | Ignored | Ignored | Indirect | N/A | Scores must remain stable | High | INDIRECT_MIGRATION_REQUIRED |
| Predicate-result tests | `asdict` risk | Add assertions | Add assertions | Typed equality changes | Typed equality changes | Condition test changes | Add rejection test | Canonical serializer required | High | DIRECT_MIGRATION_REQUIRED |
| Runtime/Yoga tests | Tuple/dict assumptions | Absent | Absent | Absent | Absent | Yoga expected | Legacy assertions change | Snapshot effects | High | DIRECT_MIGRATION_REQUIRED |
| Snapshot generator | Dict compatible | May appear in output | May appear | May appear | May appear | Indirect | N/A | Golden JSON sensitive | Critical | INDIRECT_MIGRATION_REQUIRED |
| API/frontend | JSON only | Schema addition visible | Visible | Visible | Visible | Indirect | N/A | Public response changes | High | INDIRECT_MIGRATION_REQUIRED |
| CI/golden tests | Structural compare | New field breaks | New field breaks | New field breaks | New field breaks | Indirect | N/A | Byte/structural diffs | Critical | INDIRECT_MIGRATION_REQUIRED |
| Artifact/coverage tools | Dict/truthiness | Ignored | Ignored | Ad hoc fallback | Ignored | Indirect | Raw bool/dict dependencies | Artifact schema changes | Medium | DIRECT_MIGRATION_REQUIRED |
| `record_predicate` | N/A | Discarded | bool only | Discarded | Discarded | N/A | Bool contract | Coverage report changes | Medium | DIRECT_MIGRATION_REQUIRED |

Deep immutability itself breaks no observed mutation call site. Mandatory version/status/typed error/trace changes instead break constructors, aggregators, consumers that discard fields, and serialization/golden expectations.

## 17. Caller Migration Risks and Priorities

### Complete caller inventory

| File | Symbol | Category | Called API | Resolution Type | Current Expectation | Consumption Pattern | Evidence Handling | Error Handling | Status Handling | Trace Handling | Serialization | Active Path | Tests | Migration Needed | Scope | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `systems/Parasara/engine/rules/predicates.py:12-99` | Module decorators | REGISTRY_LOOKUP | `register_predicate` | Dynamic | Decorator returns handler | Import side effects | N/A | No validation | None | None | No | ACTIVE_PRODUCTION_PATH | Import via Yoga/tests | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | Metadata signature changes every registration |
| `engine.py:54-132` | `evaluate_predicate` | GENERIC_PREDICATE_EVALUATOR; CACHE_LAYER | Registry handler | Dynamic | Typed result or tuple | Type branch/cache | Preserves typed; tuple evidence only | Converts exceptions | None | Typed branch only | No canonical API | ACTIVE_PRODUCTION_PATH | Direct tests | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P0 | Central contract/cache boundary |
| `engine.py:135-162` | `evaluate_condition` | CONDITION_EVALUATOR | Self; `evaluate_predicate` | Direct | `PredicateResult` | Reads child fields | Partial | Flattens | None | Rebuilds summary | No | ACTIVE_PRODUCTION_PATH | Condition/Yoga | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P0 | Logical result migration |
| `rules/yoga_loader.py:27-45` | `load_yoga_rules` | RULE_LOADER_OR_COMPILER | YAML; `register_rule` | Indirect | Rule dicts | Validates top-level only | Forwards condition dict | Swallows invalid rules | None | None | YAML load | ACTIVE_PRODUCTION_PATH | Loader tests | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P0 | Unknown predicates accepted |
| `rules/parashara/v1/yogas.yaml:11-74` | Condition nodes | RULE_LOADER_OR_COMPILER | Condition IDs | Dynamic | Bool-like condition outcome | String dispatch | Declarative only | Unknown becomes false | None | None | YAML | ACTIVE_PRODUCTION_PATH | Yoga integration | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P0 | Rule firing changes |
| `enrichments/yoga_engine.py:128-188` | `evaluate_yoga_rules` | YOGA_ENGINE; CACHE_LAYER | `clear_cache`; `evaluate_condition` | Direct | `PredicateResult` | Reads matched/evidence | Preserves evidence only | Discards | Discards | Discards | Builds Yoga dicts | ACTIVE_PRODUCTION_PATH | Yoga integration | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P0 | Errors become nonmatches |
| `enrichments/yoga.py:1-3` | Re-export | OTHER | `evaluate_yoga_rules` | Indirect | Yoga function | Alias surface | N/A | N/A | N/A | N/A | No | DORMANT_BUT_REFERENCED | Yoga test imports | NO_CHANGE_EXPECTED | IN_SCOPE | P3 | Public import surface |
| `yoga_engine.py:102-125` | Legacy `_eval_condition` | LEGACY_OR_COMPATIBILITY | Local tuple helpers | Direct | `(bool, dict)` | Tuple unpack | Partial | None | None | None | No | CONFIRMED_UNUSED | None | REMOVE_AFTER_CALLER_VERIFICATION | TEMPORARY_COMPATIBILITY | P2 | Dormant duplicate |
| `rules/runtime.py:64-73` | `is_exalted` | LEGACY_OR_COMPATIBILITY | `in_sign` | Direct | `bool` | Direct assignment | None | Swallows via child | None | None | No | ACTIVE_PRODUCTION_PATH | Primitive tests | TEMPORARY_ADAPTER_REQUIRED | TEMPORARY_COMPATIBILITY | P1 | Composed fact loses provenance |
| `runtime.py:76-108` | `evaluate_rule` | RULE_ENGINE; LEGACY_OR_COMPATIBILITY | Four bool helpers | Direct | `bool` | Builds match/evidence dict | Partial | Missing/unknown false | None | None | Dict | ACTIVE_PRODUCTION_PATH | Runtime tests | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P0 | Active factual bypass |
| `runtime.py:111-269` | `evaluate_rule_with_score` | RULE_ENGINE; OUTPUT_OR_SERIALIZATION | `evaluate_rule`; inline facts | Direct | Dict/raw branch state | Truthiness/model dump | Partial | Exception -> false | None | No predicate trace | Rule dict | ACTIVE_PRODUCTION_PATH | Merge/Career | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P0 | Score behavior sensitive |
| `interpreters/career.py:8-116` | `interpret_career` | DOMAIN_RUNTIME | Runtime evaluators | Direct | Rule dict | `.get`, bool, fallback | Matched only downstream | Broad fallback | Discards | Discards | Domain dict | ACTIVE_PRODUCTION_PATH | Career/snapshots | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P0 | Score/confidence/public output |
| `engine/explainability.py:4-11` | `evidence_for_rule` | INFERENCE_ENGINE | Career adapter dict | Direct | Match/evidence dict | `.get` | Preserves supplied | Discards | Discards | Discards | Dict | ACTIVE_PRODUCTION_PATH | Career test indirect | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P2 | Explanation loss |
| `engine/confidence.py:35-39` | `compute_rule_coverage` | INFERENCE_ENGINE | Rule dict list | Indirect | `matched` keys | Truthiness count | Discards | Discards | Collapsed to bool | Discards | No | ACTIVE_PRODUCTION_PATH | Career indirect | INDIRECT_MIGRATION_REQUIRED | OUT_OF_SCOPE_FUTURE_STAGE | P2 | Confidence change |
| `confidence.py:42-57` | `compute_evidence_strength` | INFERENCE_ENGINE | Rule dict list | Indirect | Score keys | Numeric fallback | Discards actual evidence | Discards | Discards | Discards | No | ACTIVE_PRODUCTION_PATH | Career indirect | INDIRECT_MIGRATION_REQUIRED | OUT_OF_SCOPE_FUTURE_STAGE | P2 | Confidence change |
| `tools/generate_snapshot.py:14-40` | `assemble_output` | OUTPUT_OR_SERIALIZATION | `interpret_career` | Direct | Domain dict | Embeds result | Preserves public evidence | Domain errors absent | N/A | N/A | Dict | ACTIVE_PRODUCTION_PATH | Snapshot suite | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P0 | Public JSON/golden drift |
| `generate_snapshot.py:43-50` | `generate` | OUTPUT_OR_SERIALIZATION | `assemble_output` | Indirect | Full output dict | JSON write/return | Preserves current | Exceptions propagate | N/A | N/A | JSON | ACTIVE_PRODUCTION_PATH | Many | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P0 | Central downstream fan-out |
| `tools/runner_api.py:25-115` | `main` | OUTPUT_OR_SERIALIZATION | `generate` | Indirect | Snapshot dict | Wraps/JSON stdout | Preserves snapshot | Converts to process error | N/A | N/A | JSON | ACTIVE_PRODUCTION_PATH | Frontend route | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | API schema |
| `frontend/.../route.ts:23-69` | `POST` | OUTPUT_OR_SERIALIZATION | Python runner | Indirect | JSON stdout | Parse/re-emit | Preserves JSON | HTTP 500 | N/A | N/A | JSON | ACTIVE_PRODUCTION_PATH | No located test | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | External response compatibility |
| `tools/ci_snapshot_check.py:38-68` | `main` | SCRIPT_OR_TOOL | `generate` | Indirect | Full output dict | Normalize/compare | Structural | Fails CI | N/A | N/A | JSON | ACTIVE_TEST_PATH_ONLY | Workflow | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P2 | Golden diffs |
| `.github/workflows/parasara-snapshot-compare.yml:28-32` | Snapshot job | SCRIPT_OR_TOOL | CI comparator | Dynamic | Exit status | Runs command | Indirect | Job failure | N/A | N/A | Snapshot | ACTIVE_TEST_PATH_ONLY | CI itself | NO_CHANGE_EXPECTED | IN_SCOPE | P3 | Blocks merges on drift |
| `tests/rules/test_predicate_result.py:14-27` | `test_planet_in_house_true_and_cache` | TEST_OR_FIXTURE; CACHE_LAYER | `clear_cache`; `evaluate_predicate` | Direct | Typed result | Reads matched/cache | Discards | Discards | None | Discards | No | ACTIVE_TEST_PATH_ONLY | Self | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | Cache/version assertions needed |
| `test_predicate_result.py:30-36` | `test_planet_exalted_false` | TEST_OR_FIXTURE; CACHE_LAYER | Evaluator | Direct | Typed result | Reads matched/errors | Discards | Reads empty | None | Discards | No | ACTIVE_TEST_PATH_ONLY | Self | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | Typed errors/status change |
| `test_predicate_result.py:39-55` | `test_predicate_exception...` | TEST_OR_FIXTURE; CACHE_LAYER | Register/evaluator/registry | Direct | Typed failure | Reads matched/errors; pops registry | Discards | Reads list | None | Discards | No | ACTIVE_TEST_PATH_ONLY | Self | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | Dynamic registration/leak |
| `test_predicate_result.py:58-64` | `test_evaluate_condition...` | TEST_OR_FIXTURE; CACHE_LAYER | Condition evaluator | Direct | `PredicateResult` | Reads matched | Discards | Discards | None | Discards | No | ACTIVE_TEST_PATH_ONLY | Self | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | Must expect ConditionResult |
| `test_predicate_result.py:67-74` | `test_predicateresult_serialization` | TEST_OR_FIXTURE; CACHE_LAYER | Evaluator | Direct | Dataclass | `asdict`/JSON | Serializes | Serializes | None | Serializes | Yes | ACTIVE_TEST_PATH_ONLY | Self | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | Canonical serializer replaces asdict |
| `tests/enrichments/test_yoga_engine_rule_driven.py:17-37` | Yoga integration test | TEST_OR_FIXTURE | Loader/Yoga API | Direct | Yoga dict list | IDs/evidence/trace ID | Type only | Discards | Discards | Presence only | No | ACTIVE_TEST_PATH_ONLY | Self | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | Rule firing/evidence regression |
| `tests/enrichments/test_yoga_loader.py:5-26` | Loader tests | TEST_OR_FIXTURE | Yoga loader/registry | Indirect | Rule dicts | IDs/validation | N/A | Validation only | N/A | N/A | No | ACTIVE_TEST_PATH_ONLY | Self | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | Predicate-reference validation |
| `systems/Parasara/tests/test_rule_runtime.py:12-21` | Primitive test | TEST_OR_FIXTURE | Bool helpers | Direct | `bool` | Raw truthiness | None | None | None | None | No | ACTIVE_TEST_PATH_ONLY | Self | DIRECT_MIGRATION_REQUIRED | TEMPORARY_COMPATIBILITY | P1 | Legacy contract assertions |
| `test_rule_runtime.py:24-33` | Evaluator test | TEST_OR_FIXTURE | `evaluate_rule` | Direct | Match/evidence dict | Reads match only | Discards | Errors unavailable | None | None | No | ACTIVE_TEST_PATH_ONLY | Self | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | Dict contract assertion |
| `test_rule_runtime_merge.py:9-19` | Merge test | TEST_OR_FIXTURE | Score wrapper | Direct | Rule dict | Reads context/provenance | Discards | Discards | None | None | No | ACTIVE_TEST_PATH_ONLY | Self | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | Rule merge behavior |
| `test_career_interpreter.py:6-17` | Career structure test | TEST_OR_FIXTURE | Career | Direct | Domain dict | Checks fields/evidence shape | Partial | None | N/A | N/A | No | ACTIVE_TEST_PATH_ONLY | Self | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | Domain schema |
| `test_additional_snapshots.py:12-20` | Additional snapshot test | TEST_OR_FIXTURE | `generate` | Indirect | Output dict | Indicator IDs | Discards | Discards | N/A | N/A | Reads JSON | ACTIVE_TEST_PATH_ONLY | Self | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P2 | Rule-firing regression |
| `tests/determinism_test.py:7-15` | Determinism test | TEST_OR_FIXTURE | `generate` | Indirect | Output dict | Serialize/hash | Preserves serialized | Exceptions fail | N/A | N/A | JSON/hash | ACTIVE_TEST_PATH_ONLY | Self | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P2 | Timing/cache fields destabilize |
| `test_career_snapshot.py:6-21` | Career snapshot test | TEST_OR_FIXTURE | `generate` | Indirect | Domain dict | Indicator IDs | Discards | Discards | N/A | N/A | Reads JSON | ACTIVE_TEST_PATH_ONLY | Self | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P2 | Indicator regression |
| `test_vertical_slice_career.py:7-22` | Vertical-slice test | TEST_OR_FIXTURE | `generate` | Indirect | Full output dict | Exact equality | Preserves all | Exceptions fail | N/A | N/A | JSON | ACTIVE_TEST_PATH_ONLY | Self | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P0 | Any output drift fails |
| `testing_framework/snapshot_runner.py:8-35` | `compare_snapshots` | TEST_OR_FIXTURE | `generate` | Indirect | Output dict | Compare; errors -> unmatched | Preserves target | Treats generation error as false | N/A | N/A | JSON | ACTIVE_TEST_PATH_ONLY | Regression framework | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P2 | Errors look like mismatch |
| `regression_runner.py:6-11` | `run_regression` | TEST_OR_FIXTURE | Snapshot runner | Indirect | Comparison dict | Forwards | Indirect | Forwards | N/A | N/A | No | ACTIVE_TEST_PATH_ONLY | Framework smoke/report | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P3 | Broad fan-out |
| `tests/test_framework_integration.py:9-42` | Framework smoke test | TEST_OR_FIXTURE | Regression runner | Indirect | Comparison dicts | Truthiness matched | Indirect | Treats false as failure | N/A | N/A | HTML downstream | ACTIVE_TEST_PATH_ONLY | Self | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P3 | Writes report if run |
| `testing_framework/perf.py:9-17` | `measure_runs` | SCRIPT_OR_TOOL | `generate` | Indirect | Output ignored | Timing only | Discards | Exceptions fail | N/A | N/A | No | ACTIVE_TEST_PATH_ONLY | No direct test found | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P3 | Typed overhead baseline |
| `update_and_sign_snapshot.py:8-12` | `update_and_sign` | SCRIPT_OR_TOOL | `generate` | Indirect | Snapshot file | Signs output | Preserves file | Exceptions fail | N/A | N/A | JSON/signoff | ACTIVE_TEST_PATH_ONLY | CLI | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P2 | Must not auto-approve schema drift |
| `generate_full_report.py:20-30` | `main` | SCRIPT_OR_TOOL | Regression runner | Indirect | Comparison results | Builds report | Indirect | Indirect | N/A | N/A | HTML/JSON | ACTIVE_TEST_PATH_ONLY | CLI | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P3 | Report drift |
| `tools/surya_to_parasara.py:80-102` | `main` | SCRIPT_OR_TOOL | Optional `generate` | Indirect | Output file | End-to-end CLI | Preserves snapshot | Exceptions propagate | N/A | N/A | JSON | ACTIVE_TEST_PATH_ONLY | CLI | INDIRECT_MIGRATION_REQUIRED | IN_SCOPE | P3 | Generated snapshot compatibility |
| `generate_full_artifacts.py:51-79` | `run_rules_and_trace` | SCRIPT_OR_TOOL | Score wrapper | Direct | Rule dict | Stores traces; false fallback | Preserves current | Exception -> false | None | No predicate trace | JSON | ACTIVE_TEST_PATH_ONLY | CLI | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P2 | Artifact schema |
| `generate_full_artifacts.py:82-103` | `synthesize_domain_prediction` | SCRIPT_OR_TOOL | Rule dicts | Direct | `matched`/score/evidence | Raw truthiness/aggregation | Preserves evidence | Discards errors | None | None | JSON | ACTIVE_TEST_PATH_ONLY | CLI | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P2 | Score artifact drift |
| `testing_framework/rule_coverage.py:7-27` | `run_rule_coverage_scan` | SCRIPT_OR_TOOL | Score wrapper | Direct | Return ignored | Instrumentation only | Discards | Swallows | None | None | Optional JSON | ACTIVE_TEST_PATH_ONLY | Coverage tests/tools | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P2 | False coverage confidence |
| `testing_framework/instrumentation.py:21-25` | `record_predicate` | LEGACY_OR_COMPATIBILITY | Runtime bool callbacks | Indirect | Name + bool | Global count | Discards | Discards | Bool only | Discards | Report dict | ACTIVE_PRODUCTION_PATH | Coverage tools | DIRECT_MIGRATION_REQUIRED | IN_SCOPE | P1 | Production imports tests |

### Summary counts

| Measure | Count |
|---|---:|
| Total callers/consumer surfaces | 47 |
| Direct callers | 22 |
| Indirect or dynamic callers | 25 |
| Generic evaluator callers | 5 |
| Condition evaluator callers | 3 |
| Direct registered-handler callers | 1 |
| Direct registered-handler bypasses | 0 |
| Yoga callers/surfaces | 4 |
| Domain callers | 2 |
| Serialization consumers | 9 |
| Cache consumers | 7 |
| Test/tool-only callers | 27 |
| Active production callers | 18 |
| Dormant but referenced callers | 1 |
| Confirmed-unused callers | 1 |
| Callers discarding evidence | 12 |
| Callers discarding available typed errors | 3 |
| Callers treating errors/exceptions as unmatched | 5 |
| Tuple-unpacking callers | 2 |
| Raw-truthiness consumers | 5 |
| Tuple-unpacking plus raw-truthiness callers | 7 |
| Callers requiring direct migration | 23 |
| Callers with unknown migration status | 0 |
| P0 findings | 4 |
| P1 findings | 7 |
| P2 findings | 4 |
| P3 findings | 2 |

### Countable priority findings

1. **P0 — Yoga loses typed failure state before rule output.** `evaluate_yoga_rules` reads only match/evidence, so predicate errors, missing capabilities, invalid parameters, trace, and version cannot survive (`yoga_engine.py:154-177`).
2. **P0 — Career’s active legacy caller chain bypasses the predicate engine and controls score/confidence.** `career.py:45-64` consumes raw/dictionary runtime results and broadly falls back, making contract migration behavior-sensitive.
3. **P0 — Active YAML contains an unregistered condition and loaders do not validate it.** `HOUSE_LORDS_COMBINATION` (`yogas.yaml:41-44`) reaches the unknown-predicate false path rather than a configuration error.
4. **P0 — Output and golden consumers amplify internal changes into public/snapshot regressions.** `generate_snapshot.py:14-50`, runner/API, and exact snapshot tests freeze current score/evidence behavior.
5. **P1 — Central logical aggregation discards full child result identity and conflates ConditionResult with PredicateResult.** `engine.py:142-159` requires direct migration.
6. **P1 — Generic tuple compatibility remains reachable.** `engine.py:80-93` can hide unmigrated dynamic handlers and loses typed fields.
7. **P1 — Legacy runtime callers expect bool/dictionary contracts.** Runtime, Career, tests, and tooling cannot accept tuple/raw-bool removal without an explicit compatibility boundary.
8. **P1 — Rule loaders are not predicate-contract consumers today.** They cannot validate mandatory versions, schemas, capabilities, or unknown IDs before runtime.
9. **P1 — Cache consumers rely on current global clear/cache-hit behavior.** Version/digest-safe keys and telemetry separation will require evaluator, Yoga, and test updates.
10. **P1 — Typed tests encode the incomplete dataclass surface.** `asdict`, mutable lists/dicts, missing version/status, and current error dictionaries are assumed or untested.
11. **P1 — Production runtime depends on boolean-only test instrumentation.** This consumer cannot observe typed status/errors and introduces shared mutation.
12. **P2 — Confidence/explainability consumers discard predicate details.** Current scores may remain stable only if typed migration preserves rule-level match/contribution semantics.
13. **P2 — The dormant Yoga tuple caller duplicates the central evaluator.** It is confirmed unused but must be removed only after resolving the missing condition semantics.
14. **P2 — Artifact, coverage, and snapshot tools convert failures to false or schema drift.** These can hide errors or encourage broad snapshot updates.
15. **P2 — No caller test exercises API/frontend propagation of typed errors or missing capabilities.** Public behavior under new status semantics is unprotected.
16. **P3 — Re-export and optional CLI surfaces expand compatibility without adding contract coverage.** They should be verified after core migration.
17. **P3 — Performance/report harnesses ignore logical results or consume only downstream files.** They are nonblocking but require baseline/report review.

## 18. Unresolved Questions

1. Which legacy runtime callers will migrate in Prompt-01 versus remain behind a temporary adapter? The four primitives are temporary compatibility per Audit-2, but active `evaluate_rule`, Career, and tooling still need an approved boundary.
2. Should `HOUSE_LORDS_COMBINATION` become a registered predicate, a composed condition, or an invalid rule? Caller evidence cannot settle astrological ownership.
3. Is the frontend/API response schema expected to expose predicate status/errors/traces, or must those remain internal while public JSON stays unchanged?
4. Does any external consumer outside this repository dynamically register tuple-return handlers? No repository caller does, but external usage cannot be proven absent.

## 19. Audit-4 Conclusion

Audit-4 is complete. Forty-seven caller/consumer surfaces were classified with no unknown usage or migration status. The registered-handler path has one approved dynamic caller and zero direct bypasses. The highest migration risk lies in active Yoga information loss, unvalidated dynamic conditions, the legacy Career/runtime scoring chain, and broad output/snapshot fan-out.

Prompt-01 caller migration must preserve Yoga firing, Career score/confidence, evidence, public JSON, and golden behavior while introducing typed version/status/error/trace semantics. This audit created only this report and did not begin Audit-5.
