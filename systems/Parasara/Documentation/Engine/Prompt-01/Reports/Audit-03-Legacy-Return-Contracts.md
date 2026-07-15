# Prompt-01 Audit-03: Legacy Return Contracts

## 1. Executive Summary

The central predicate module has already migrated its six registered IDs (five unique handlers) to return `PredicateResult`, but the repository still contains multiple legacy predicate and predicate-like contracts around that core. The audit found **5 legacy tuple producers**, **2 tuple consumers**, **4 raw-boolean producers**, **3 raw-boolean consumers**, **4 dictionary/ad hoc result contracts**, **3 compatibility adapters**, and **8 information-loss boundaries**.

The five tuple producers are a parallel Yoga evaluator and four Yoga leaf helpers. Repository-wide reference searches show that this local evaluator family is not called by the active Yoga path; it is classified `CONFIRMED_UNUSED`, not active production. The generic evaluator nevertheless retains a tuple compatibility branch that can accept any dynamically registered tuple-return handler.

The principal active risk is the separate rule runtime used by Career and test/report tooling. Four predicate-like primitives return raw booleans, `evaluate_rule` packages those values into `{'match', 'evidence'}` dictionaries, and `evaluate_rule_with_score` converts them into a serialized `RuleMatch` dictionary. This path bypasses `PREDICATE_REGISTRY`, `evaluate_predicate`, and the typed predicate contract. The active generic condition/Yoga path uses `PredicateResult` but discards child or top-level errors, trace, cache, status, and version information at aggregation and consumer boundaries.

There are **11 active production legacy paths**, **3 test-only legacy-preserving paths**, **5 confirmed-unused paths**, and **0 unknown-usage paths**. Countable findings total **3 P0, 6 P1, 3 P2, and 1 P3**. No fixes were implemented.

## 2. Audit Scope and Method

The audit searched all repository Python, tests, scripts, YAML/YML, JSON, and relevant documentation for tuple annotations/returns, tuple unpacking, raw booleans, `match`/`matched` dictionaries, `PredicateResult` construction and consumption, compatibility type checks, registry/evaluator calls, and caller references. Candidate matches were inspected in context; astronomy tuples, JSON comparison tuples, linter return pairs, and ordinary boolean helpers were excluded when they did not represent a predicate boundary.

Authoritative requirements came from `Documentation/AI-Prompt/Jyothishyam Master Architecture Specification v1.0.docx` sections 19-25 and `Documentation/AI-Prompt/Prompt-01.docx` sections 4-5, 10, 14, 19-21, 26-31, and 35-37. Prompt-01 requires factual predicates to return the typed result and requires evidence, errors, status, trace, and predicate version to survive the rule-evaluation path.

Safe, non-mutating `rg`, PowerShell file inspection, and caller/reference searches were executed. Tests were not run because this is a static contract audit and the default interpreter was already confirmed during Audit-1 to lack `pytest` and `pydantic`. No generated-artifact command was run because `tests/testing_framework/generate_full_artifacts.py:23-24,35-36` writes files on import/use.

Counting policy: a producer or consumer is counted once per symbol, even if it has multiple return or call sites. A symbol may belong to more than one category (for example, Yoga `_eval_condition` both produces and consumes tuples). “Active production” describes a callable path reached by a production entry point, including test instrumentation imported directly by production runtime code; it does not claim every branch is exercised by every chart.

## 3. Reconciliation with Audits 1 and 2

Audit-1 and Audit-2 are available at `systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-01-Predicate-Registry.md` and `systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-02-Complete-Predicate-Inventory.md`. This audit confirms their main contract findings:

- one central handler registry and two hard-coded equivalent dispatch mechanisms;
- all six central IDs resolve to five typed handlers in `systems/Parasara/engine/rules/predicates.py:12-99`;
- a generic tuple compatibility branch remains at `systems/Parasara/engine/rules/engine.py:80-93`;
- the active Career path uses the separate raw-boolean/dictionary runtime;
- Yoga retains a parallel tuple evaluator but actively calls the generic typed evaluator at `yoga_engine.py:150-156`.

Audit-2 counts 12 unregistered predicate-like/condition functions: four raw-boolean runtime primitives, two active legacy rule evaluators, four Yoga tuple leaf helpers, one Yoga tuple condition dispatcher, and the central condition evaluator (`Audit-02`, sections 1 and 6). Audit-3 finds the same function set and the same **five tuple producers** and **four raw-boolean producers**. Audit-3 expands the view to consumers/adapters, adding the tuple compatibility branch, boolean-only instrumentation, Career/explainability dictionary adapters, test harnesses, and typed-result information-loss boundaries.

Audit-2 classifies the four raw-boolean primitives as `TEMPORARY_COMPATIBILITY`/P1 pending an explicit migration-boundary decision. Audit-3 preserves that scope and priority for the individual primitive functions; it does not prescribe automatic deletion or semantic redesign. The active `evaluate_rule`/Career boundary remains P0 because those consumers must be explicitly isolated or migrated for Prompt-01 to complete safely. There is no disagreement in registered IDs, active status, tuple counts, or helper counts.

## 4. Legacy Tuple Producers

Five symbols in `systems/Parasara/engine/enrichments/yoga_engine.py` advertise and return `Tuple[bool, Dict[str, Any]]`:

1. `_eval_aspect_condition` (`22-52`) returns match plus aspect evidence.
2. `_eval_functional_role_condition` (`55-67`) returns match plus matched planets.
3. `_eval_house_lords_combination` (`70-91`) returns match plus combination/reason evidence.
4. `_eval_house_occupant` (`94-99`) returns match plus planet/house evidence.
5. `_eval_condition` (`102-125`) returns logical or leaf match plus evidence.

The only references to the four leaf helpers are dispatch branches inside `_eval_condition` (`116-123`). The only `_eval_condition` call is its own recursion at line 109. The exported/active `evaluate_yoga_rules` instead calls imported `evaluate_condition` from the central engine (`6,150-156`). Repository-wide caller evidence therefore supports `CONFIRMED_UNUSED` for all five, while recognizing they remain source-level duplicates and may confuse future maintenance.

None can preserve typed errors, trace steps, predicate status, cache state, or predicate version. Their evidence dictionaries are preserved only within their isolated tuple tree. They bypass the central registry and duplicate central `ASPECT`, `FUNCTIONAL_ROLE`, and `HOUSE_OCCUPANT` behavior; `_eval_house_lords_combination` has no registered central equivalent.

## 5. Legacy Tuple Consumers

Two symbols tuple-unpack predicate-related output:

- `evaluate_predicate` in `systems/Parasara/engine/rules/engine.py:54-132` checks `isinstance(out, tuple)` and unpacks `ok, evidence` at lines 80-93. It wraps those two values in `PredicateResult`, preserving only matched/evidence and synthesized ID/inputs/timing. It cannot preserve source status, errors, trace, version, cache semantics, or tuple arity/type guarantees. No production registered handler currently returns a tuple, so the branch is `DORMANT_BUT_REFERENCED` and `TEMPORARY_COMPATIBILITY` in migration scope.
- Yoga `_eval_condition` at `yoga_engine.py:102-125` recursively unpacks `ok, ev` at lines 108-111. It is part of the confirmed-unused parallel evaluator and loses all typed-result fields by design.

No active central caller tuple-unpacks the output of `evaluate_predicate` or the imported central `evaluate_condition`. Tests at `tests/rules/test_predicate_result.py:14-74` use `PredicateResult` attributes rather than tuple positions.

## 6. Raw Boolean Predicate Contracts

Four active predicate-like primitives in `systems/Parasara/engine/rules/runtime.py` return `bool`:

- `in_sign` (`10-34`);
- `in_house` (`37-44`);
- `lord_of_house` (`47-61`);
- `is_exalted` (`64-73`).

These functions answer factual astrological questions and are therefore raw-boolean predicate contracts, not unrelated helpers. They do not register centrally, accept the common `(astro, params, context)` signature, or return evidence/errors/status/trace/version. `in_sign` also has a fallback calculation and exception swallowing at lines 19-34. `is_exalted` consumes the raw boolean returned by `in_sign`.

Two additional raw-boolean consumers are:

- `evaluate_rule` (`runtime.py:76-108`), which calls the four primitives and packages each boolean with evidence;
- `record_predicate` (`tests/testing_framework/instrumentation.py:21-25`), which accepts only a boolean and records true/false counts. Production `runtime.py:7,15,28,41,58,70` imports and calls this test-framework API, making the boolean-only observer an active production dependency despite its test path.

The raw-boolean totals are four producers plus three consumer symbols, or seven raw-boolean contract symbols. Direct primitive assertions in `systems/Parasara/tests/test_rule_runtime.py:12-21` preserve the legacy behavior in tests.

## 7. Dictionary and Ad Hoc Result Contracts

Four material dictionary contracts participate in the predicate/rule path:

1. `runtime.evaluate_rule` returns `{'match': bool, 'evidence': dict}` for primitive success, missing planets, and unsupported types (`runtime.py:76-108`). This is a predicate-like result dictionary with no errors/status/trace/version.
2. `runtime.evaluate_rule_with_score` consumes that dictionary for primitive/fallback types (`runtime.py:167-173,231-236`) and returns `RuleMatch.model_dump()`/`.dict()` at lines 242-269. Although the output is rule-shaped rather than a factual predicate result, its factual inputs come from the bypass path.
3. `interpret_career` consumes the `RuleMatch` dictionary and, on exception, creates another RuleMatch-like dictionary from `evaluate_rule` (`career.py:45-64`). It supports both `adjusted_score` and legacy `score` fields (`55-56`).
4. `evidence_for_rule` expects an ad hoc `eval_result` dictionary with `match` and `evidence` (`explainability.py:4-11`). Career constructs that adapter dictionary at `career.py:62-64`.

Yoga match dictionaries returned by `evaluate_yoga_rules` and public domain outputs were inspected but not counted as predicate dictionary contracts: they are separate Yoga/domain-stage models. Their conversion boundaries are still noted where they discard predicate information.

## 8. Compatibility Adapters

Three adapters preserve legacy behavior:

- **Generic tuple adapter:** `engine.evaluate_predicate` converts `(bool, evidence)` to `PredicateResult` (`engine.py:80-93`). It is not marked deprecated and has no removal tracking.
- **Legacy runtime-to-rule adapter:** `runtime.evaluate_rule_with_score` converts raw booleans or `{'match','evidence'}` into a `RuleMatch` model and immediately serializes it back to a dictionary (`runtime.py:167-173,231-269`). It bypasses the central predicate engine.
- **Career exception fallback:** `career.interpret_career` converts the legacy `evaluate_rule` dictionary into a partial RuleMatch-like dictionary (`career.py:47-56`). It silently changes behavior when the primary runtime throws and supplies a fixed score of `0.05` for a match.

The generic evaluator does not accept raw booleans as successful predicate results. A boolean reaches the `invalid_predicate_return` typed failure branch at `engine.py:101-112`, which is preferable to silently treating it as a match but still lacks Prompt-01 typed error/status/version models.

## 9. Information-Loss Boundaries

Eight distinct boundaries lose contract information:

1. Generic tuple-to-`PredicateResult` conversion loses producer errors, trace, status, and version (`engine.py:80-93`).
2. Yoga tuple `_eval_condition` reduces child results to booleans and evidence only (`yoga_engine.py:102-125`).
3. `runtime.evaluate_rule` reduces factual outcomes to `match` and ad hoc evidence (`runtime.py:76-108`).
4. `runtime.evaluate_rule_with_score` converts legacy factual results into rule data with no predicate identity/version/status/trace (`runtime.py:167-173,231-269`).
5. Central `evaluate_condition` retains child evidence and a summary trace but does not retain child `PredicateResult` objects or child trace steps/cache state (`engine.py:142-159`). It flattens child errors and does not short-circuit.
6. Active Yoga `evaluate_yoga_rules` reads only `pr.matched` and `pr.evidence` (`yoga_engine.py:154-177`), dropping errors, trace steps, cache state, timing, status, and version before constructing Yoga dictionaries.
7. Career normalizes a RuleMatch/legacy dictionary through `bool(match.get('matched'))` and a score fallback (`career.py:48-64`); errors and predicate-level trace/status/version are unavailable or discarded.
8. Career’s `eval_result` adapter and `explainability.evidence_for_rule` retain only match/evidence plus contribution (`career.py:62-64`; `explainability.py:4-11`).

`record_predicate` intentionally observes only boolean coverage and is not counted as a main result-conversion boundary, but its API prevents richer execution-state instrumentation.

## 10. Yoga Legacy Contracts

Yoga contains both legacy and typed paths in the same file:

- The legacy family at `yoga_engine.py:22-125` returns tuples and directly implements four condition types. It is confirmed unused by repository-wide reference search.
- The active family imports `evaluate_condition` and predicate definitions at lines 6-7, then calls the typed evaluator at lines 150-156.

This is not an active tuple-unpacking Yoga path, but it remains a parallel contract and duplicates factual logic. Its `HOUSE_LORDS_COMBINATION` branch (`70-91,120-121`) is especially risky because active YAML uses that condition while the central registry does not provide it; the active typed evaluator treats it as unknown. Removing or migrating the dormant code without first resolving that semantic gap could hide intended behavior.

The active path still violates end-to-end preservation: it consumes only `.matched` and `.evidence`. It does not expose predicate errors or central condition trace in the Yoga result (`154-177`).

## 11. Condition Evaluator Contracts

Central `evaluate_condition` returns `PredicateResult` for both logical operators and factual leaves (`engine.py:135-162`). This eliminates tuple output on the active path, but it conflates logical `AND`/`OR` aggregation with a factual predicate result identified as `AND` or `OR`. Prompt-01 permits a separate `ConditionResult` boundary.

For `AND`/`OR`, every child is evaluated (`145-151`), child `.matched` values become a boolean list, evidence becomes a list of child evidence dictionaries, errors are flattened, and trace steps are reconstructed with only ID/match/errors/timing (`152-159`). Full child results, nested trace, cache state, status, and version are not preserved. There is no `NOT` branch. Leaves delegate correctly to `evaluate_predicate` at lines 160-162.

The legacy Yoga `_eval_condition` has the same eager logical evaluation pattern but returns tuples and loses even more information (`yoga_engine.py:102-125`). It is not the active evaluator.

## 12. Domain and Rule-Engine Consumers

Career is the confirmed production domain consumer. `systems/Parasara/tools/generate_snapshot.py:11,34` imports and invokes `interpret_career`, while `systems/Parasara/tests/test_career_interpreter.py:6-17` validates its public dictionary structure.

Career never calls `evaluate_predicate` or `evaluate_condition`. It constructs candidate rule dictionaries, calls the hard-coded runtime, consumes dictionary fields with truthiness conversion, and falls back to the older dictionary evaluator on any exception (`career.py:35-64`). Consequently, predicate evidence cannot carry typed errors/status/version/trace into Career.

`runtime.evaluate_rule_with_score` is both a consumer and adapter. Its hard-coded branches at `runtime.py:167-240` implement factual and higher-level rule logic, catch all exceptions, and emit `{'error': 'evaluation_failed'}` with `matched=False`. That collapses configuration, missing capability, invalid input, and programming failures into a non-match-like rule result.

`confidence.py:35-57` consumes `matched` and score fields from rule dictionaries. This is a rule/inference-stage consumer and is not independently counted as a predicate legacy contract, but it demonstrates that information already discarded upstream cannot be recovered downstream.

## 13. Test-Only and Dormant Legacy Paths

Test-only legacy-preserving paths are grouped into three:

1. `systems/Parasara/tests/test_rule_runtime.py:12-33` directly asserts raw booleans and `{'match': ...}` dictionary behavior.
2. `systems/Parasara/tests/test_rule_runtime_merge.py:9-19` asserts dictionary output from `evaluate_rule_with_score`.
3. Test/report harnesses call or consume the legacy runtime: `tests/testing_framework/generate_full_artifacts.py:51-103` and `tests/testing_framework/rule_coverage.py:7-27`. The latter discards the returned result entirely and relies on boolean instrumentation.

The five Yoga tuple producers form the confirmed-unused set. They are source-referenced within their own isolated family but have no entry caller. The generic tuple adapter is not “unused”: it is a reachable branch of the active evaluator API and can be triggered by dynamic registration, so it is classified `DORMANT_BUT_REFERENCED`.

Typed-result tests at `tests/rules/test_predicate_result.py:14-74` do not preserve tuple output. They verify `.matched`, caching, exception conversion, condition return type, and basic serialization. They do not test rejection/deprecation of tuple or boolean handler returns or end-to-end field preservation.

## 14. False Positives and Excluded Findings

The following search matches are unrelated to the predicate contract and were excluded from counts:

- `tests/testing_framework/json_compare.py:30-85` and its callers return/unpack `(matched, diffs)` for JSON comparison, not astrology evaluation.
- `tools/rules_lint.py:13-26` returns `(bool, message)` for CLI lint status.
- `systems/SuryaSiddhanta/ndastro_engine/combustion.py:137-175` and `retrograde.py:144-180` return astronomy event tuples; they are above the AstroState/predicate boundary.
- `tests/testing_framework/create_snapshot_pr_ci.py:22-25`, `systems/Parasara/tools/ci_snapshot_check.py:34-59`, and test assertion helpers return ordinary operational booleans.
- Shadbala/enrichment dictionaries contain evidence but represent enrichment calculations, not predicate results (`systems/Parasara/engine/enrichments/shadbala.py:29-174`).
- `PredicateResult.matched` assertions in `tests/rules/test_predicate_result.py` are valid typed consumers, not raw-boolean predicate contracts.

## 15. Prompt-01 Compliance Assessment

| Requirement | Status | Evidence and gap |
|---|---|---|
| All registered factual predicates return `PredicateResult` | PARTIAL/PASS FOR CURRENT REGISTRY | All five unique handlers do so (`predicates.py:12-99`), but factual runtime primitives bypass registration and return bool. |
| No active tuple-return predicate paths | PASS WITH DORMANT DEBT | Five tuple producers exist but caller search confirms the family is unused. |
| No active tuple-unpacking predicate callers | PASS WITH COMPATIBILITY DEBT | Only unused Yoga recursion and the reachable generic compatibility adapter unpack tuples. |
| No raw booleans as predicate contracts | FAIL | Four active runtime primitives return bool (`runtime.py:10-73`). |
| Unexpected handler returns become typed errors or strict rejection | PARTIAL | Arbitrary returns become a failure result (`engine.py:101-112`); tuple returns are silently accepted and registration does not reject contract mismatch. |
| Compatibility adapters isolated and deprecated | FAIL | Tuple, runtime, and Career adapters are not explicitly deprecated or removal-tracked. |
| Compatibility conversion preserves information | FAIL | Eight information-loss boundaries omit required fields. |
| Yoga has no parallel predicate contract | FAIL | Unused but complete tuple evaluator remains (`yoga_engine.py:22-125`). |
| Logical operators separated from predicate leaves | FAIL | Central evaluator represents `AND`/`OR` as `PredicateResult` (`engine.py:135-159`). |
| Status/errors/evidence/trace/version preserved end-to-end | FAIL | Active central and legacy paths drop these fields; predicate version/status do not yet exist in the current model. |

Prompt-01 completion criteria are not met even though current registered handlers themselves return the typed class.

## 16. Migration Risks and Priorities

### Legacy contract inventory

| File | Symbol | Role | Pattern | Actual Contract | Expected Contract | Callers | Execution Status | Evidence Preserved | Errors Preserved | Trace Preserved | Version Preserved | Registry Bypass | Migration Required | Scope | Priority | Risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `systems/Parasara/engine/enrichments/yoga_engine.py:22-52` | `_eval_aspect_condition` | Producer | LEGACY_TUPLE_PRODUCER | `(bool, dict)` | `PredicateResult` | Unused `_eval_condition` | CONFIRMED_UNUSED | Yes | No | No | No | Yes | Remove/migrate with semantic check | IN_SCOPE | P2 | Duplicate can diverge |
| `yoga_engine.py:55-67` | `_eval_functional_role_condition` | Producer | LEGACY_TUPLE_PRODUCER | `(bool, dict)` | `PredicateResult` | Unused `_eval_condition` | CONFIRMED_UNUSED | Yes | No | No | No | Yes | Remove/migrate | IN_SCOPE | P2 | Duplicate can diverge |
| `yoga_engine.py:70-91` | `_eval_house_lords_combination` | Producer | LEGACY_TUPLE_PRODUCER | `(bool, dict)` | Registered typed predicate or explicit condition contract | Unused `_eval_condition` | CONFIRMED_UNUSED | Yes | No | No | No | Yes | Resolve active YAML semantic gap first | IN_SCOPE | P0 | Intended condition currently unknown centrally |
| `yoga_engine.py:94-99` | `_eval_house_occupant` | Producer | LEGACY_TUPLE_PRODUCER | `(bool, dict)` | `PredicateResult` | Unused `_eval_condition` | CONFIRMED_UNUSED | Yes | No | No | No | Yes | Remove/migrate | IN_SCOPE | P2 | Duplicate can diverge |
| `yoga_engine.py:102-125` | `_eval_condition` | Producer/consumer | LEGACY_TUPLE_PRODUCER; LEGACY_TUPLE_CONSUMER; LOGICAL_CONDITION_CONTRACT | `(bool, dict)` | `ConditionResult` | Self-recursion only | CONFIRMED_UNUSED | Partial | No | No | No | Yes | Remove after semantic reconciliation | IN_SCOPE | P2 | Parallel evaluator |
| `systems/Parasara/engine/rules/engine.py:80-93` | `evaluate_predicate` tuple branch | Consumer/adapter | LEGACY_TUPLE_CONSUMER; COMPATIBILITY_ADAPTER | Accepts `(bool, evidence)` | Reject incompatible return or isolated deprecated adapter | Any dynamically registered tuple handler; none production | DORMANT_BUT_REFERENCED | Evidence only | No | No | No | No | Deprecate and remove after migration proof | TEMPORARY_COMPATIBILITY | P1 | Hides incomplete migrations |
| `systems/Parasara/engine/rules/runtime.py:10-34` | `in_sign` | Producer | RAW_BOOLEAN_PRODUCER | `bool` | `PredicateResult` or explicitly private compatibility helper | `evaluate_rule`, `is_exalted`, tests | ACTIVE_PRODUCTION_PATH | No | No | No | No | Yes | Boundary decision; preserve semantics | TEMPORARY_COMPATIBILITY | P1 | Factual result loses all context |
| `runtime.py:37-44` | `in_house` | Producer | RAW_BOOLEAN_PRODUCER | `bool` | `PredicateResult` or explicitly private compatibility helper | `evaluate_rule`, tests | ACTIVE_PRODUCTION_PATH | No | No | No | No | Yes | Boundary decision; preserve semantics | TEMPORARY_COMPATIBILITY | P1 | Factual result loses all context |
| `runtime.py:47-61` | `lord_of_house` | Producer | RAW_BOOLEAN_PRODUCER | `bool` | `PredicateResult` or explicitly private compatibility helper | `evaluate_rule`, tests | ACTIVE_PRODUCTION_PATH | No | No | No | No | Yes | Boundary decision; preserve semantics | TEMPORARY_COMPATIBILITY | P1 | Factual result loses all context |
| `runtime.py:64-73` | `is_exalted` | Producer/consumer | RAW_BOOLEAN_PRODUCER; RAW_BOOLEAN_CONSUMER | `bool` | `PredicateResult` or explicitly private compatibility helper | `evaluate_rule`; consumes `in_sign` | ACTIVE_PRODUCTION_PATH | No | No | No | No | Yes | Boundary decision; preserve semantics | TEMPORARY_COMPATIBILITY | P1 | Composed predicate loses provenance |
| `runtime.py:76-108` | `evaluate_rule` | Consumer/producer | RAW_BOOLEAN_CONSUMER; DICTIONARY_RESULT_CONTRACT | `{'match','evidence'}` | Typed predicate/condition result | Career fallback, score wrapper, tests | ACTIVE_PRODUCTION_PATH | Partial | No | No | No | Yes | Retire or route through central engine | IN_SCOPE | P0 | Unknown/errors become non-match dictionaries |
| `runtime.py:111-269` | `evaluate_rule_with_score` | Consumer/adapter | DICTIONARY_RESULT_CONTRACT; COMPATIBILITY_ADAPTER | Raw/dict facts to serialized `RuleMatch` dict | Typed predicate then typed rule boundary | Career, tools, tests | ACTIVE_PRODUCTION_PATH | Partial | Partial ad hoc | No predicate trace | No predicate version | Yes | Migrate factual dispatch; preserve rule behavior | IN_SCOPE | P1 | Mixed predicate/rule/scoring responsibilities |
| `engine.py:135-159` | `evaluate_condition` logical branches | Typed consumer | TYPED_RESULT_WITH_INFORMATION_LOSS; LOGICAL_CONDITION_CONTRACT | `PredicateResult` representing `AND`/`OR` | `ConditionResult` retaining children | Yoga active path | ACTIVE_PRODUCTION_PATH | Partial | Flattened | Summary only | No | No | Introduce/retain typed condition boundary | IN_SCOPE | P1 | Child provenance lost |
| `yoga_engine.py:128-188` | `evaluate_yoga_rules` | Typed consumer | TYPED_RESULT_WITH_INFORMATION_LOSS | Reads `.matched`/`.evidence` only | Preserve typed condition/predicate results | Yoga API/tests | ACTIVE_PRODUCTION_PATH | Yes | No | No | No | No | Carry typed result information forward | IN_SCOPE | P0 | Errors can become ordinary nonmatches |
| `systems/Parasara/engine/interpreters/career.py:45-64` | `interpret_career` | Consumer/adapter | DICTIONARY_RESULT_CONTRACT; COMPATIBILITY_ADAPTER | Rule dict plus legacy fallback dict | Typed rule result consuming typed predicates | Snapshot generation/tests | ACTIVE_PRODUCTION_PATH | Partial | No | No | No | Indirect yes | Migrate caller/fallback | IN_SCOPE | P0 | Broad fallback changes semantics silently |
| `systems/Parasara/engine/explainability.py:4-11` | `evidence_for_rule` | Consumer | DICTIONARY_RESULT_CONTRACT; TYPED_RESULT_WITH_INFORMATION_LOSS | Ad hoc `{'match','evidence'}` input | Typed rule/condition evidence | Career | ACTIVE_PRODUCTION_PATH | Yes | No | No | No | Indirect | Accept typed upstream evidence | IN_SCOPE | P2 | Audit detail unrecoverable |
| `tests/testing_framework/instrumentation.py:21-25` | `record_predicate` | Consumer | RAW_BOOLEAN_CONSUMER | Predicate name + bool | Typed observation or non-production hook | Production `runtime.py` | ACTIVE_PRODUCTION_PATH | No | No | No | No | Yes | Decouple and enrich/retire | IN_SCOPE | P1 | Production depends on tests and bool-only state |
| `tests/testing_framework/generate_full_artifacts.py:51-103` | `run_rules_and_trace`; `synthesize_domain_prediction` | Test consumer | DICTIONARY_RESULT_CONTRACT | Rule dictionaries | Typed serialized rule results | Script main | ACTIVE_TEST_PATH_ONLY | Partial | Ad hoc only | No | No | Indirect | Update with runtime migration | IN_SCOPE | P3 | Generated artifacts can entrench schema |
| `tests/testing_framework/rule_coverage.py:7-27` | `run_rule_coverage_scan` | Test consumer | RAW_BOOLEAN_CONSUMER / result discarded | Ignores returned rule dictionary | Typed execution observation | Coverage harness | ACTIVE_TEST_PATH_ONLY | No | No | No | No | Indirect | Update instrumentation | IN_SCOPE | P3 | Coverage hides contract loss |
| `systems/Parasara/tests/test_rule_runtime.py:12-33`; `test_rule_runtime_merge.py:9-19` | Runtime tests | Test | TEST_ONLY_LEGACY_CONTRACT | Assert bool/dict contracts | Assert migrated typed contracts | pytest | ACTIVE_TEST_PATH_ONLY | As asserted only | No | No | No | Yes | Rewrite with migration | IN_SCOPE | P3 | Tests resist removal of legacy API |

### Caller migration inventory

| File | Symbol | Called API | Current Expectation | Consumption Pattern | Information Lost | Active Path | Required Migration | Priority |
|---|---|---|---|---|---|---|---|---|
| `engine.py:54-118` | `evaluate_predicate` | Registered handler | `PredicateResult` or tuple | Type branch and tuple unpack | Tuple source errors/status/trace/version | Reachable; no current prod tuple handler | Reject or isolate deprecated adapter | P1 |
| `yoga_engine.py:102-125` | Legacy `_eval_condition` | Local tuple helpers | `(bool, dict)` | Tuple unpack/recursive aggregation | All typed fields | No, confirmed unused | Remove after reconciling semantics | P2 |
| `runtime.py:64-73` | `is_exalted` | `in_sign` | `bool` | Direct assignment | Evidence and child identity | Yes | Boundary decision: typed composition or private compatibility helper | P1 |
| `runtime.py:76-108` | `evaluate_rule` | Four runtime primitives | `bool` | Direct match assignment then dict return | Errors/status/trace/version | Yes | Route through predicate/condition engine | P0 |
| `runtime.py:111-269` | `evaluate_rule_with_score` | `evaluate_rule` and hard-coded branches | `{'match','evidence'}` or raw branch state | `.get`, `bool`, model dump | Predicate identity/status/trace/version | Yes | Separate factual evaluation from RuleMatch construction | P1 |
| `yoga_engine.py:128-188` | `evaluate_yoga_rules` | Central `evaluate_condition` | `PredicateResult` | Reads `.matched`, `.evidence` | Errors/trace/cache/status/version | Yes | Preserve typed condition results/evidence | P0 |
| `career.py:8-116` | `interpret_career` | `evaluate_rule_with_score`; fallback `evaluate_rule` | Rule dictionaries | `.get`, `bool`, score fallback | Errors/predicate trace/status/version | Yes | Consume typed RuleMatch; remove broad legacy fallback | P0 |
| `explainability.py:4-11` | `evidence_for_rule` | Career adapter dict | `{'match','evidence'}` | `.get` | Errors/status/trace/version | Yes | Accept typed evidence/trace source | P2 |
| `instrumentation.py:21-25` | `record_predicate` | Runtime boolean | `bool` | Boolean-key counter | All non-boolean result data | Yes via production import | Observe typed status without test dependency | P1 |
| `generate_full_artifacts.py:51-103` | Artifact generator | `evaluate_rule_with_score` | Rule dictionaries | `.get`, `bool`, JSON writes | Typed identity and errors | Test/script only | Update after typed runtime migration | P3 |

### Countable priority findings

1. **P0 — Active legacy `evaluate_rule` uses a dictionary predicate contract.** `runtime.py:76-108` collapses unknown, missing, and factual outcomes to `match/evidence`.
2. **P0 — Career actively consumes and reconstructs ad hoc legacy results.** `career.py:45-64` uses dictionary truthiness and a broad exception fallback that can silently change scores.
3. **P0 — Active Yoga discards typed error/trace/status/version information.** `yoga_engine.py:154-177` reduces the central result to match/evidence; unregistered conditions can appear as ordinary false results.
4. **P1 — Active runtime factual primitives return raw booleans and bypass the central registry.** Four symbols at `runtime.py:10-73` cannot preserve required predicate information; consistent with Audit-2, their individual migration scope remains a compatibility-boundary decision.
5. **P1 — Generic tuple compatibility remains reachable and undeclared.** `engine.py:80-93` accepts tuple handlers without deprecation or removal controls.
6. **P1 — Central logical aggregation does not preserve child typed results.** `engine.py:142-159` conflates conditions with predicates and rebuilds partial traces.
7. **P1 — `evaluate_rule_with_score` mixes legacy factual dispatch, rule construction, scoring, and dictionary serialization.** `runtime.py:111-269` blocks a clean typed boundary.
8. **P1 — Production runtime imports boolean-only test instrumentation.** `runtime.py:7` and `instrumentation.py:21-25` couple production behavior to a test module and discard result richness.
9. **P1 — Tests do not enforce removal/rejection of legacy handler contracts or end-to-end field preservation.** Current typed tests never register tuple/bool returns to assert migration policy.
10. **P2 — Five confirmed-unused Yoga tuple producers duplicate the active engine.** `yoga_engine.py:22-125` can drift and obscures the missing central `HOUSE_LORDS_COMBINATION` behavior.
11. **P2 — Broad exception handling collapses defects into nonmatches.** `runtime.py:237-240` and Career fallback at `career.py:47-52` erase failure classification.
12. **P2 — Explainability adapters preserve only match/evidence/contribution.** `career.py:62-64` and `explainability.py:4-11` cannot carry predicate errors/status/version/trace.
13. **P3 — Test/report tooling encodes legacy bool/dictionary contracts.** Runtime tests and artifact/coverage scripts must change during migration but do not independently block architecture work.

### Summary counts

| Measure | Count |
|---|---:|
| Tuple producers | 5 |
| Tuple consumers | 2 |
| Raw-boolean producers | 4 |
| Raw-boolean consumers | 3 |
| Raw-boolean contract symbols (producer + consumer) | 7 |
| Dictionary/ad hoc result contracts | 4 |
| Compatibility adapters | 3 |
| Information-loss boundaries | 8 |
| Active production legacy paths | 11 |
| Test-only paths | 3 |
| Confirmed-unused paths | 5 |
| Unknown-usage paths | 0 |
| P0 findings | 3 |
| P1 findings | 6 |
| P2 findings | 3 |
| P3 findings | 1 |

## 17. Unresolved Questions

1. Architecture ownership must decide whether `runtime.py` primitives are migrated into central predicates, retained as private helpers underneath typed predicates, or retired with the legacy rule runtime. They cannot remain public factual bool contracts for Prompt-01 completion.
2. `HOUSE_LORDS_COMBINATION` exists only in the dormant Yoga evaluator while active Yoga YAML references it. Its intended central typed implementation/condition ownership must be resolved before deleting the dormant family.
3. The generic tuple adapter has no documented external callers. Repository evidence supports no current production tuple handler, but external consumers outside the repository cannot be ruled out without a public API compatibility decision.

## 18. Audit-3 Conclusion

Audit-3 is complete and reconciled with both prior reports. Repository-wide evidence agrees with Audit-2’s six registered IDs/five handlers, 12 unregistered predicate-like/condition helpers, five tuple producers, four raw-boolean producers, and active-versus-dormant path classifications. No active Yoga caller tuple-unpacks the central evaluator. Nevertheless, Prompt-01 remains blocked by an active parallel raw-boolean/dictionary runtime, undeclared tuple compatibility, typed-result information loss in condition/Yoga/domain boundaries, and tests/tooling that preserve legacy contracts.

This audit created only this report. It did not modify production code, tests, rules, prior reports, snapshots, or generated artifacts, and it did not begin Audit-4.
