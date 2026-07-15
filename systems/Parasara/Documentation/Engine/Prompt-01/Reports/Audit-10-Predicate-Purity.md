# Prompt-01 Audit-10: Predicate Purity

## 1. Executive Summary

Audit-10 is **COMPLETE**. All nine prerequisite reports were available. Six registered predicate IDs were audited: **2 PURE, 0 PURE_WITH_EXPLICIT_CONTEXT, 3 MOSTLY_PURE_WITH_RISK, 1 IMPURE, and 0 UNKNOWN**.

`PLANET_IN_HOUSE` and `HOUSE_OCCUPANT` are locally factual/read-only deterministic functions for immutable validated inputs. `ASPECT`/`ASPECT_EXISTS` and `PLANET_EXALTED` are locally read-only but depend on mutable, ambiguously prepared capability shapes and broad fallbacks. `FUNCTIONAL_ROLE` is impure: it calls `compute_functional_roles` during evaluation, which reads CWD-dependent YAML files or applies an unversioned heuristic (`systems/Parasara/engine/rules/predicates.py:70-82`; `enrichments/functional_roles.py:16-146`).

Registered handlers have **0 direct state mutations, 0 transitive state mutations, and 0 parameter mutations**. Predicate-related Yoga callers mutate AstroState, but those are classified separately. Registered predicates have no logical system-time or randomness reads. Evaluator timing is performance-only; Yoga UUID4/set ordering are later-layer nondeterminism.

All six predicates are **NOT_CACHE_SAFE** under the current key because it omits content digest, versions, context, capability readiness, and configuration. Six evaluation-order dependencies carry forward from Audit-9. Findings total **6 P0, 7 P1, 4 P2, and 1 P3**.

## 2. Audit Scope and Method

The Master Architecture, Prompt-01, Audits 1–9, registered and legacy handlers, transitive helpers, enrichments, Yoga, runtime/Career, cache/registries, tests, tools, and configuration loaders were inspected. Searches covered writes, globals, I/O, environment/time/randomness, enrichment calls, scoring/output, exceptions, iteration order, and test coverage.

Purity counts apply to registered IDs; shared Aspect IDs count separately. Side effects in Yoga/legacy callers are inventoried but not misattributed to registered handlers. No mutating command or implementation change was run. Pytest remains unavailable.

## 3. Reconciliation with Audits 1–9

Audit-2's six-ID/five-handler inventory is unchanged. Audit-3's raw boolean/dictionary legacy paths include global instrumentation and mixed scoring, but are compatibility paths. Audit-4 shows Yoga and Career caller risks. Audits 5–6 establish result/telemetry mutability and nondeterminism. Audit-7 found no parameter mutation but noncanonical caller-owned inputs. Audit-8 found one predicate recomputation. Audit-9 found zero registered state writes, four caller preparation mutations, and six order dependencies. Audit-10 confirms all of these under the purity contract.

## 4. Predicate Purity Contract

Logical purity is assessed separately from evaluator telemetry and caller preparation. A handler may be locally read-only yet not cache-safe if its inputs are mutable, unversioned, hidden, or prepared inconsistently. Factual boundary means the handler answers a fact, not whether its implementation is pure.

## 5. Complete Predicate Purity Inventory

| Predicate ID | File | Handler | Inputs Read | Helpers Called | State Mutation | Parameter Mutation | Global State | Time | Randomness | I/O | Enrichment Computation | Scoring/Interpretation | Order Dependency | Purity | Cache Safety | Tests | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ASPECT` | `predicates.py:12-47` | `aspect_exists` | params, planets, aspects | `_planet_by_name` | No | No | Mutable state only | No | No | No | No | None | Yes: aspect preparation | MOSTLY_PURE_WITH_RISK | NOT_CACHE_SAFE | Indirect Yoga | IN_SCOPE | P0 |
| `ASPECT_EXISTS` | same | same | same | same | No | No | Same | No | No | No | No | None | Yes | MOSTLY_PURE_WITH_RISK | NOT_CACHE_SAFE | None direct | IN_SCOPE | P0 |
| `PLANET_IN_HOUSE` | `predicates.py:50-57` | `planet_in_house` | params, planets/house | `_planet_by_name` | No | No | None in handler | No | No | No | No | None | Caller mutation/cache only | PURE | NOT_CACHE_SAFE | Direct valid/cache | IN_SCOPE | P1 |
| `HOUSE_OCCUPANT` | `predicates.py:60-67` | `house_occupant` | params, planets/house | `_planet_by_name` | No | No | None | No | No | No | No | None | Caller mutation/cache only | PURE | NOT_CACHE_SAFE | Indirect Yoga | IN_SCOPE | P1 |
| `FUNCTIONAL_ROLE` | `predicates.py:70-82` | `functional_role` | params, context, planets/Lagna/config | `compute_functional_roles` | No | No | Mutable constants/config | No | No | Filesystem | Yes | Factual only | CWD/config/context | IMPURE | NOT_CACHE_SAFE | Indirect Yoga | IN_SCOPE | P0 |
| `PLANET_EXALTED` | `predicates.py:85-99` | `planet_exalted` | params, planets, flags, metadata | `_planet_by_name` | No | No | Mutable state | No | No | No | No | None | Capability preparation | MOSTLY_PURE_WITH_RISK | NOT_CACHE_SAFE | Ambiguous false | IN_SCOPE | P0 |

## 6. Transitive Helper and Call-Graph Assessment

| Predicate ID | Handler | Called Helper | Helper File | Impurity Type | Direct/Transitive | State Affected | Logical Impact | Active Path | Shared Helper | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Aspect/house/exalted IDs | respective | `_planet_by_name` | `predicates.py:8-9` | Mutable-state read; no mutation | Transitive | planets | Exact lookup depends on current list | Yes | Yes | IN_SCOPE | P1 |
| `FUNCTIONAL_ROLE` | `functional_role` | `compute_functional_roles` | `functional_roles.py:50-146` | Enrichment computation, CWD filesystem I/O, unversioned mutable tables | Transitive | none written; reads state/files | Changes matched/evidence | Yes | Shared by enrichments | IN_SCOPE | P0 |
| `FUNCTIONAL_ROLE` | helper | `_load_table_for_lagna` | `functional_roles.py:16-47` | Evaluation-time file existence/open/YAML; swallowed failures | Transitive | external config | Table versus heuristic result | Yes | Yes | IN_SCOPE | P0 |

## 7. AstroState and Enrichment Mutation

Registered handlers and condition evaluator perform no writes. Audit-9's active caller/preparation mutations remain: `chart_to_astrostate`, `integrate_vargas_into_astro`, `compute_aspect_graph`, and `evaluate_yoga_rules` (`normalizer.py:30-158`; `varga.py:188-225`; `aspects.py:24-100`; `yoga_engine.py:128-186`). They are preparation/Yoga mutations, not predicate mutations, but affect later results and cache validity.

## 8. Parameter and Caller-Owned Data Mutation

No handler calls `pop`, `update`, `setdefault`, assignment, sort, clear, or append on parameters. Parameter-mutation paths: **0**. Inputs are not defensively copied, so callers can mutate them/result inputs after key construction; this is aliasing risk rather than handler mutation.

## 9. Mutable Global and Module State

| File | Symbol | Type | Readers | Writers | Mutates During Evaluation | Versioned | Thread-Safe | Logical Impact | Tests | Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `rules/engine.py:21-25` | `PREDICATE_REGISTRY` | dict | evaluator | decorators/tests | Test/runtime registration possible | No | No locks | Handler resolution | Dynamic test only | High | P1 |
| `rules/engine.py:24-36` | `_CACHE` | dict | evaluator | evaluator/clear | Yes | No | No locks | Warm result selection | One warm test | Critical | P0 |
| `rules/loader.py:5-46` | `RULE_REGISTRY` | dict | Yoga/runtime | loaders | Lazy/loading/evaluation setup | No | No locks | Rules executed/order | Loader tests | High | P2 |
| `tests/testing_framework/instrumentation.py:4-25` | counters | dict/global | legacy tools | legacy predicates | Yes on legacy execution | No | No | Coverage side effect, not factual output | Runtime tests | Medium | P2 |

Mutable global-state dependency count is **4**. Functional-role constants are mutable Python dicts/sets but have no observed runtime writer; filesystem tables are the material logical dependency.

## 10. Time and Randomness Dependencies

| File | Symbol | Predicate/Caller | Source | Classification | Fields Affected | Explicit Context | Cache Impact | Snapshot Impact | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| `engine.py:61-159` | evaluators | all | `time.perf_counter` | TELEMETRY_ONLY | evaluation time/equality/trace summary | No | Cached telemetry differs | Direct serialization risk | IN_SCOPE | P2 |
| `yoga_engine.py:14-15,177` | Yoga | caller | UUID4 | TRACE_NONDETERMINISM | Yoga trace ID | No | Not predicate key | Yoga output if exposed | OUT_OF_SCOPE_FUTURE_STAGE | P2 |
| `yoga_engine.py:51,173` | Yoga | caller | set-to-list | EVIDENCE_NONDETERMINISM | planet ordering | No | Indirect state/output | Yes | IN_SCOPE caller | P1 |
| `engine.py:39-44` | cache key | all | `id(astro)`, `default=str` | CACHE_NONDETERMINISM | cache hit/telemetry | No | Direct | Indirect | IN_SCOPE | P0 |

Registered logical implicit-time dependencies: **0**. Registered randomness dependencies: **0**; predicate-related caller randomness dependencies: **1**.

## 11. I/O and External Dependencies

`FUNCTIONAL_ROLE` has one evaluation-time I/O path: `_load_table_for_lagna` checks/opens YAML under CWD-dependent primary/legacy paths and swallows read/parse errors (`functional_roles.py:16-47`). It has no timeout, version, immutable preload, or cache identity. No registered predicate uses network, database, subprocess, environment variables, logging, writes, or external services.

## 12. Factual Predicate Boundary

All six registered handlers answer factual questions and perform no score, weight, confidence, conflict, narrative, inference, RuleMatch, or public-output construction. Registered factual-boundary violation count is **0**.

Legacy `evaluate_rule_with_score` and Career combine facts with scoring/interpretation (`runtime.py:111-269`; `career.py:8-116`), producing **2 predicate-related compatibility boundary violations**, but neither is a registered predicate.

## 13. Enrichment Recomputation

Only `FUNCTIONAL_ROLE` recomputes an enrichment during registered predicate evaluation. Recomputation count: **1**. It is deterministic only for identical AstroState, CWD, file contents, YAML behavior, and code; none of the table/config versions enter result or cache identity. Yoga redundantly computes roles before conditions and discards them.

## 14. Exception and Fallback Behavior

Aspect swallows per-edge exceptions and continues, producing partial/false results (`predicates.py:19-36`). Functional-role table loading swallows file/YAML errors and silently falls back to heuristic (`functional_roles.py:21-47`). Normalizer/Yoga swallow broad preparation errors. The central evaluator catches every handler exception, returns false with raw `str(e)`, and caches it (`engine.py:117-130`). No typed error or strict mode exists.

These fallbacks can hide impurity/configuration changes and turn unavailable/malformed facts into nonmatches.

## 15. Repeatability and Evaluation-Order Dependencies

Six dependencies are inherited from Audit-9: aspect representation before/after Yoga, stale cache after preparation, Yoga-only cache clear, CWD/table changes, hidden context selection, and partial best-effort preparation. Registry mutation/test order and caller mutation are additional concurrency/repeatability risks but not separately counted.

Cold and warm results differ in `cache_hit` and timing/equality. Logical matched/evidence may also differ when state/config/context changes without key changes. Evaluation-order dependency count: **6**.

## 16. Cache-Safety Assessment

| Predicate ID | Declared Cacheable | Purity | Implicit Dependencies | Context Required | Version Coverage | Cache Classification | Evidence | Required Action | Priority |
|---|---|---|---|---|---|---|---|---|---|
| `ASPECT` | No declaration; always cached | MOSTLY_PURE_WITH_RISK | mutable graph/planets/houses | No | None | NOT_CACHE_SAFE | incompatible capability/order | readiness/digest/version | P0 |
| `ASPECT_EXISTS` | Same | MOSTLY_PURE_WITH_RISK | same | No | None | NOT_CACHE_SAFE | same | same | P0 |
| `PLANET_IN_HOUSE` | Always cached | PURE | mutable planets/houses | No | None | NOT_CACHE_SAFE | object-ID key | content identity | P0 |
| `HOUSE_OCCUPANT` | Always cached | PURE | mutable planets/houses | No | None | NOT_CACHE_SAFE | object-ID key | content identity | P0 |
| `FUNCTIONAL_ROLE` | Always cached | IMPURE | context, CWD/table, state | Yes | None | NOT_CACHE_SAFE | key omits context/config | prepared facts/version/context | P0 |
| `PLANET_EXALTED` | Always cached | MOSTLY_PURE_WITH_RISK | mutable flags/metadata | No | None | NOT_CACHE_SAFE | capability/version absent | canonical facts/identity | P0 |

Not-cache-safe predicate count: **6**.

## 17. Thread-Safety and Parallel Evaluation

Classification: **NOT_THREAD_SAFE**. Global registry/cache/rule registry/counters have no locks or lifecycle isolation; Yoga mutates shared AstroState and clears global cache; dynamic test registration can overwrite handlers; functional-role files may change during evaluation. Separate immutable states with direct local pure handlers would be safer, but the actual evaluator/caller system is shared and mutable.

## 18. Existing Tests and Coverage Gaps

No test directly asserts the requested purity contract. Existing cache/determinism tests do not isolate handler purity or all logical fields.

| Area | Missing Categories | Count | Recommended Location |
|---|---|---:|---|
| Direct purity | no state/enrichment/parameter/nested/global mutation | 5 | `tests/rules/test_predicate_purity.py` |
| Determinism | repeated/equivalent states/no time/no random/no unordered serialization | 5 | `tests/rules/test_predicate_determinism.py` |
| Evaluation order | predicate order/Yoga/cold-warm/lazy initialization | 4 | `tests/rules/test_predicate_order.py` |
| Boundary enforcement | no domain scoring/raw source/external service/file I/O/enrichment engine | 6 | `tests/rules/test_predicate_boundaries.py` |
| Cache safety | no implicit dependencies/context isolation/version isolation | 3 | `tests/rules/test_predicate_cache_safety.py` |

Missing purity-test-category count: **23**. Pytest is unavailable in the current interpreter.

## 19. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| All registered predicates pure | NONCOMPLIANT | role I/O/recomputation; three risky | predicates/helpers | Prepared immutable facts | IN_SCOPE | P0 | Yes |
| No evaluation-time I/O | NONCOMPLIANT | role YAML reads | functional roles | Versioned preload/preparation | IN_SCOPE | P0 | Yes |
| No enrichment computation | NONCOMPLIANT | role helper call | role predicate | Consume prepared capability | IN_SCOPE | P0 | Yes |
| Deterministic logical inputs | NONCOMPLIANT | state/context/config hidden | engine/predicates | Explicit immutable identity | IN_SCOPE | P0 | Yes |
| Cache safety | NONCOMPLIANT | all six unsafe | engine/all handlers | Audit-11 with purity prerequisites | IN_SCOPE | P0 | Yes |
| Evaluation-order independence | NONCOMPLIANT | six paths | Yoga/state/cache | Enforced readiness/isolation | IN_SCOPE | P0 | Yes |
| No state mutation in handlers | IMPLEMENTED | zero paths | predicates | Preserve/test | IN_SCOPE | P1 | No |
| No parameter mutation | IMPLEMENTED | zero paths | predicates | Preserve/test | IN_SCOPE | P1 | No |
| Factual-only registered predicates | IMPLEMENTED | no score/output | predicates | Preserve/test | IN_SCOPE | P1 | No |
| No raw/external service access | IMPLEMENTED | zero raw/network | predicates | Preserve/test | IN_SCOPE | P1 | No |
| Explicit context identity | MISSING | role context omitted | engine/role predicate | Declare/validate/key context | IN_SCOPE | P1 | Yes |
| Safe typed exception behavior | NONCOMPLIANT | swallow/raw strings | engine/helpers | Typed errors/strict policy | IN_SCOPE | P1 | Yes |
| Deterministic evidence/telemetry separation | NONCOMPLIANT | timing/set/UUID caller paths | engine/Yoga | Separate logical/telemetry | IN_SCOPE | P1 | Yes |
| Purity contract tests | MISSING | 23 gaps | tests | Focused suites | IN_SCOPE | P1 | Yes |
| Thread-safe evaluator globals | NONCOMPLIANT | unlocked globals | engine/loaders | Isolated lifecycle/thread policy | IN_SCOPE | P2 | No |
| Legacy boundary purity | NONCOMPLIANT | instrumentation/scoring | runtime/Career | Temporary adapters | TEMPORARY_COMPATIBILITY | P2 | No |
| Caller preparation purity | PARTIAL | Yoga mutates/recomputes | Yoga/enrichments | Explicit preparation stage | OUT_OF_SCOPE_FUTURE_STAGE | P2 | No |
| Parallel execution policy | MISSING | no contract/tests | engine architecture | Define later | OUT_OF_SCOPE_FUTURE_STAGE | P3 | No |

## 20. Migration Risks and Priorities

The 18 findings total **P0=6, P1=7, P2=4, P3=1**. Valid factual semantics must be preserved while removing hidden I/O/recomputation. Locally pure handlers still require immutable state, canonical parameters, versions, and context-safe cache identity. Compatibility work must not pull legacy scoring into predicates.

## 21. Unresolved Architectural Questions

1. Where and when are functional roles prepared, frozen, and versioned?
2. Which Aspect representation/readiness contract governs repeated evaluation?
3. What counts as logical equality excluding cache/timing telemetry?
4. How is explicit evaluation context represented in identity?
5. Are table fallbacks approved modes or failures?
6. What thread/registry/cache isolation model is required?

Questions 1–4 block safe purity/cache implementation.

## 22. Audit-10 Conclusion

Audit-10 is complete. All prerequisites were available; no implementation correction was made and Audit-11 was not started.

### Summary counts

| Metric | Count |
|---|---:|
| Registered predicates audited | 6 |
| PURE predicates | 2 |
| PURE_WITH_EXPLICIT_CONTEXT predicates | 0 |
| MOSTLY_PURE_WITH_RISK predicates | 3 |
| IMPURE predicates | 1 |
| UNKNOWN purity | 0 |
| Direct mutation paths | 0 |
| Transitive mutation paths | 0 |
| Parameter-mutation paths | 0 |
| Mutable global-state dependencies | 4 |
| Implicit system-time dependencies | 0 |
| Predicate-related randomness dependencies | 1 |
| Evaluation-time I/O paths | 1 |
| Enrichment-recomputation paths | 1 |
| Registered scoring/interpretation violations | 0 |
| Legacy compatibility boundary violations | 2 |
| Evaluation-order dependencies | 6 |
| Predicates NOT_CACHE_SAFE | 6 |
| Missing purity-test categories | 23 |
| P0 findings | 6 |
| P1 findings | 7 |
| P2 findings | 4 |
| P3 findings | 1 |

The only modified file is this report.
