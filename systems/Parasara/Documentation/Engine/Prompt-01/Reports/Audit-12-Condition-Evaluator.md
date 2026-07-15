# Prompt-01 Audit-12: Condition Evaluator

## 1. Executive Summary

The repository has four condition/rule evaluator contracts: the canonical generic `evaluate_condition`, a dormant Yoga-local recursive tuple evaluator, and two active legacy flat-rule evaluators. Three are active in production. The canonical evaluator delegates leaves correctly through `evaluate_predicate`, but logical `AND` and `OR` nodes are falsely returned as `PredicateResult(predicate_id="AND"|"OR")`; no `ConditionResult` exists.

Both recursive implementations evaluate every child before applying `all` or `any`, producing four non-short-circuit operator paths. `NOT` is not implemented: it falls through as an unknown predicate and becomes a cached false result. There is no typed condition status, child results are not retained, skipped branches are not represented, and nested traces are reduced or absent. Unknown predicates and operators become ordinary negative outcomes rather than definition/compilation errors.

The current implementation is NONCOMPLIANT with Prompt-01 and the Master Architecture. Findings total **7 P0, 8 P1, 3 P2, and 1 P3**. No correction was implemented.

## 2. Audit Scope and Method

The audit read the Master Architecture Specification, Prompt-01, all eleven prerequisite reports, condition/rule engine source, loaders, Yoga and Career callers, active YAML, tests, and current architecture documentation. Repository-wide searches covered evaluator names, recursion, logical aggregation, registry calls, tuples/booleans, child/evidence/error/trace handling, and caches. Counts distinguish evaluator/operator paths, not individual rule instances.

A non-mutating direct probe exercised empty nodes, eager evaluation, `NOT`, unknown types, and malformed inputs. Targeted pytest invocation could not collect because the available Python installation has no `pytest` module.

## 3. Reconciliation with Audits 1–11

Audit-1 established the central registry plus legacy runtime and Yoga bypasses; Audit-2 counted the same generic/Yoga/runtime helpers. Audit-3 classified Yoga tuples and runtime booleans/dictionaries. Audit-4 proved the active chains `Yoga -> evaluate_condition -> evaluate_predicate` and `Career -> evaluate_rule_with_score -> evaluate_rule`, plus the dormant status of Yoga `_eval_condition`. Audits 5–6 established the incomplete `PredicateResult` and absent `ConditionResult`/typed status-error-trace models. Audits 7–8 established missing load/runtime validation and capability status. Audits 9–10 establish mutable state, nondeterministic telemetry, and unsafe purity boundaries. Audit-11 found one predicate-leaf cache and no condition-result cache. Audit-12 found no contradiction.

All expected reports were present; no missing-report limitation applies.

## 4. Condition Evaluator Inventory

| Evaluator | File | Symbol | Category | Input Contract | Operators | Leaf Dispatch | Return Contract | Short-Circuit | Status | Evidence | Errors | Trace | Child Results | Callers | Active Status | Tests | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Generic recursive evaluator | `systems/Parasara/engine/rules/engine.py:135-162` | `evaluate_condition` | `CANONICAL_GENERIC_EVALUATOR` | raw dict: `type`, optional `children`, `params` | AND, OR | `evaluate_predicate(t, params, astro, context)` | `PREDICATE_RESULT_FOR_LOGICAL_NODE`; leaf `PredicateResult` | No; eager loop | Absent | Child evidence list | Flattened untyped list | Rebuilt one-level summaries | No | self, Yoga, direct test | `CANONICAL` | leaf-only test | P0 |
| Yoga recursive evaluator | `systems/Parasara/engine/enrichments/yoga_engine.py:102-125` | `_eval_condition` | `YOGA_SPECIFIC_EVALUATOR` | raw dict: exact uppercase `type`, `children`, `params` | AND, OR | four hard-coded local helpers | `LEGACY_TUPLE` | No; eager loop | Absent | Child evidence list | None | None | No | self-recursion only | `CONFIRMED_UNUSED` | None | P2 |
| Legacy flat rule evaluator | `systems/Parasara/engine/rules/runtime.py:76-108` | `evaluate_rule` | `LEGACY_GENERIC_EVALUATOR` | flat dict with lowercase `type` and top-level arguments | None | four raw-boolean helpers | dict `{'match','evidence'}` | N/A | Absent | Partial flat dict | Unsupported/missing become evidence reason | None | N/A | score wrapper, Career fallback, tests | `ACTIVE_ALTERNATE` | primitive matched/unmatched | P0 |
| Legacy scored rule evaluator | `systems/Parasara/engine/rules/runtime.py:111-269` | `evaluate_rule_with_score` | `DOMAIN_SPECIFIC_EVALUATOR` | flat rule dict/registry metadata | None | `evaluate_rule` plus inline duplicated facts | serialized `RuleMatch` dictionary | N/A | No predicate/condition status | Partial | exception becomes generic evidence | only optional rule `trace_id` | N/A | Career, test | `ACTIVE_ALTERNATE` | merge test | P0 |

Condition evaluator count: **4**; active production: **3**; canonical: **1**; legacy/alternate: **3**; tuple/raw-boolean evaluator contracts: **1**. The four Yoga `_eval_*` leaf helpers and four runtime boolean primitives are dispatch dependencies, not additional tree evaluators.

## 5. Canonical Evaluator and Active Paths

`evaluate_condition` is canonical because current implementation status names it, Prompt-01 names it for migration, Yoga imports/calls it (`yoga_engine.py:6,150-156`), and it alone delegates through `PREDICATE_REGISTRY`. Its production path receives raw YAML dictionaries from `load_yoga_rules`; there is no compiler/canonical AST boundary.

The Yoga-local `_eval_condition` is not import-order selected and has no external caller; repository-wide evidence finds only self-recursion. The active Career runtime remains a duplicate factual/rule path and bypasses both the registry and canonical evaluator. Import order affects central predicate availability through decorator side effects, but does not swap evaluator implementations.

## 6. Condition Input Contract

The generic evaluator accepts `{type: <operator-or-predicate>, children?: list, params?: dict}`. `type` is required in practice and uppercased at runtime; leaf parameters remain nested under `params`. Logical `children` defaults to `[]`, and `None` is converted to `[]`. Unknown fields are ignored. Raw YAML dictionaries reach runtime because `validate_yoga_rule` checks only top-level required fields (`yoga_loader.py:21-44`).

Empty `AND` returns true and empty `OR` returns false by Python identities. `{}` returns a false `UNKNOWN` result with `missing_type`; `None`, list roots, non-list `children`, and non-dict children raise uncontrolled `AttributeError`. Cycles/excessive nesting have no guard. Lowercase logical/predicate types work only in the generic evaluator; the Yoga-local and runtime dispatchers use exact case. These behaviors are implementation accidents, not an approved validated contract.

## 7. Predicate-Leaf Delegation

| Evaluator | Leaf Shape | Called API | Registry Used | Received Contract | Conversion | Information Lost | Unknown Predicate Behavior | Active Callers | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| `evaluate_condition` | `{type: ID, params: {...}}` | `evaluate_predicate` | Yes | `PredicateResult` | None for leaves | None at leaf boundary | cached `matched=False`, reason only | Yoga | PARTIAL | P0 |
| `_eval_condition` | same, exact uppercase | local `_eval_*` | No | `(bool, dict)` | tuple passthrough | status/errors/trace/version | `(False, unknown_condition_type)` | none | NONCOMPLIANT | P2 |
| `evaluate_rule` | flat `{type: lowercase, ...}` | boolean helpers | No | raw bool | dict wrapping | typed identity/status/errors/trace | false `unsupported_rule_type` | wrapper/Career fallback | NONCOMPLIANT | P0 |
| `evaluate_rule_with_score` | flat rule/registered metadata | local branches/`evaluate_rule` | No | bool/dict/internal fields | serialized rule dictionary | predicate results/status/errors/trace | fallback false result | Career | NONCOMPLIANT | P0 |

The active YAML ID `HOUSE_LORDS_COMBINATION` has no central registration (`yogas.yaml:41-44`). It therefore becomes a cached false leaf even though the dormant Yoga evaluator has a local implementation (`yoga_engine.py:70-91,120-121`).

## 8. Return-Contract Assessment

Leaves on the canonical path return `PredicateResult`. `AND` and `OR` also return `PredicateResult`, incorrectly using logical operator strings as factual predicate IDs (`engine.py:159`). `NOT`, any other operator, and any unknown predicate fall through to `evaluate_predicate`, returning a false leaf-shaped result. Missing type returns `PredicateResult('UNKNOWN')`; structurally malformed roots raise. No `ConditionResult` or equivalent nested model exists.

The Yoga alternate returns `LEGACY_TUPLE`; the two legacy runtime evaluators return dictionaries and consume raw booleans internally. Evaluators returning `PredicateResult` for logical nodes: **1**.

## 9. AND Semantics

Children are evaluated left-to-right but all are evaluated. `all([])` makes empty AND true. All matched produces true; any false/error/missing-capability/invalid-parameter child produces false because those states have already collapsed to `.matched=False`. Errors are flattened; evidence is a positional list; nested trace and full child objects are lost. No remaining child is skipped or marked skipped.

| Operator | Scenario | Children Evaluated | Current Matched Outcome | Current Status | Evidence Preserved | Errors Preserved | Trace Preserved | Skipped Represented | Required Decision | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AND | first child false, later true | all | false | none | evidence dicts only | flattened | one-level summaries | No | short-circuit/typed precedence | NONCOMPLIANT | P0 |
| AND | error/missing capability plus other child | all | false | none | partial | untyped/identity lost | nested trace lost | No | status precedence | NONCOMPLIANT | P0 |
| AND | empty children | none | true | none | empty list | empty | empty | N/A | approve identity or reject | UNKNOWN | P1 |

## 10. OR Semantics

Children are evaluated left-to-right but all are evaluated. `any([])` makes empty OR false. A later match makes the parent true even after an earlier error, while the flattened error remains attached to a matched result; no status defines that mixed outcome. Remaining branches after a match execute and can populate caches or cause side effects/errors.

| Operator | Scenario | Children Evaluated | Current Matched Outcome | Current Status | Evidence Preserved | Errors Preserved | Trace Preserved | Skipped Represented | Required Decision | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OR | first child true, later false | all | true | none | evidence dicts only | flattened | one-level summaries | No | short-circuit | NONCOMPLIANT | P0 |
| OR | error then matched | all | true with errors | none | partial | untyped/identity lost | nested trace lost | No | explicit precedence | NONCOMPLIANT | P0 |
| OR | empty children | none | false | none | empty list | empty | empty | N/A | approve identity or reject | UNKNOWN | P1 |

## 11. NOT Semantics

`NOT` is absent from both recursive evaluators. On the canonical path it is treated as predicate ID `NOT`, so its child is never evaluated and the result is cached false/unknown predicate. On the Yoga path it returns false/unknown condition type. No repository rule currently uses `NOT`, but the Master Architecture baseline and Prompt-01 require it. Zero/multiple-child arity, status inversion, evidence preservation, and trace inversion are wholly missing.

## 12. Short-Circuit and Skipped Branches

The generic and Yoga evaluators each contain eager `AND` and eager `OR`, for **4 non-short-circuit paths**. The direct probe confirmed calls `['F','T']` for AND and `['T','F']` for OR. Stopping conditions do not exist; status cannot influence them. Unevaluated/skipped results and trace entries do not exist, and tests do not verify non-execution.

## 13. Status Propagation and Precedence

There is no condition status model and the current `PredicateResult` itself lacks typed status. Six counted paths lack propagation: generic AND/OR, Yoga AND/OR, `evaluate_rule`, and `evaluate_rule_with_score`. Missing capability, invalid parameters, unknown definitions, exceptions, and ordinary factual nonmatches all reduce to false at one or more boundaries.

Authoritative precedence is unresolved for `AND(unmatched, missing_capability)`, `OR(unmatched, missing_capability)`, `OR(error, matched)`, and `NOT(missing_capability)`. The report does not invent precedence.

## 14. Evidence and Error Preservation

Generic logical aggregation retains each immediate child's evidence dictionary in order, but strips child result identity and can expose mutable nested dictionaries. Nested logical evidence becomes anonymous `children` lists. The Yoga alternate does likewise with tuples. Runtime paths construct separate limited evidence and never retain PredicateResults.

Counted evidence-loss paths: **4** (generic AND/OR and Yoga AND/OR lose full child/evidence identity). Counted error-loss paths: **6** (generic AND/OR flatten untyped errors and lose child identity; Yoga AND/OR have no error channel; each runtime evaluator collapses or omits typed errors). Predicate exceptions use raw strings centrally; Yoga aspect helper silently continues after exceptions; scored runtime exceptions become `{'error':'evaluation_failed'}`.

## 15. Trace and Child-Result Preservation

Generic AND/OR create one-level summaries containing predicate ID, matched, errors, and timing, but discard child `trace_steps`, inputs, evidence links, cache hits, and nested parent-child structure. No stable node IDs, AST references, short-circuit decisions, or skipped nodes exist. Durations use `perf_counter` and differ between runs. Yoga's public results add random UUID4 trace IDs (`yoga_engine.py:14-15,177`).

Trace-loss paths: **6** (generic AND/OR, Yoga AND/OR, and both legacy runtime evaluators). Complete child-result preservation count is zero for all logical paths.

## 16. Unknown Operator and Predicate Handling

No loader validates operators or predicate IDs. Direct runtime invocation treats an unknown logical operator as a leaf. Central unknown leaves return cached unmatched evidence with no error/status (`engine.py:62-77`); Yoga unknown types return false tuples; legacy rule dispatchers return false dictionaries. Unknown-predicate-to-unmatched paths: **4**. Unknown-operator-to-unmatched paths: **2** (generic and Yoga recursive evaluators).

These are rule-definition/compilation faults, not factual negative evidence. The direct probe confirmed both `NOT` and `BOGUS` return unmatched without errors.

## 17. Empty and Malformed Conditions

| Input | Generic Current Behavior | Yoga Current Behavior | Required Status | Priority |
|---|---|---|---|---|
| `None` / list root | uncontrolled attribute error | same | validated definition error | P0 |
| `{}` / missing type | false `UNKNOWN` with error | false unknown tuple | load/compile error | P0 |
| empty AND / missing children / null children | true | true | unresolved identity-vs-invalid decision | P1 |
| empty OR | false | false | unresolved identity-vs-invalid decision | P1 |
| NOT zero/multiple child | treated unknown; child ignored | treated unknown | exact-one validation | P0 |
| non-list children/non-dict child | uncontrolled attribute error | same | validated definition error | P0 |
| unknown fields | ignored | ignored | compiler/schema decision | P1 |
| cycle/excessive nesting | unbounded recursion/no limit | same | cycle/depth validation | P1 |

## 18. Alternate and Legacy Evaluators

Yoga `_eval_condition` duplicates AND/OR and four facts, bypasses the registry, returns tuples, and is confirmed unused by repository-wide caller evidence. Its local `HOUSE_LORDS_COMBINATION` highlights semantic drift from the active central registry. It should not become a fallback; Prompt-01 requires no Yoga custom bypass after migration.

The active runtime/Career chain evaluates flat rule dictionaries, duplicates factual logic, uses booleans/dictionaries, and mixes scoring with rule evaluation. It is temporary compatibility whose current scoring and public-output behavior must be protected while its factual boundary is migrated. Audit-15 will cover Yoga beyond these contracts.

## 19. Condition Caching

No complete logical/condition result is cached. Only predicate leaves use `_CACHE`; logical nodes recompute on every call. Eager evaluation warms every leaf even when AND/OR should have skipped later branches, so fixing short-circuiting will change cache population. Cached error, missing-capability, invalid-input, and unknown-predicate false results can make parent outcomes sticky. Child `cache_hit` is omitted from parent trace summaries, while timing is retained; see Audit-11.

## 20. Caller Compatibility

| Caller | File | Called Evaluator | Expected Contract | Boolean/Matched Use | Evidence Use | Error Use | Child-Result Use | All-Children Assumption | Migration Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| generic recursion | `rules/engine.py:145-159` | `evaluate_condition` | `PredicateResult` | `.matched` | `.evidence` | flatten `.errors` | No | Yes | Critical | P0 |
| Yoga rule evaluation | `enrichments/yoga_engine.py:150-177` | `evaluate_condition` | `PredicateResult` | `.matched` | `.evidence`; shallow planet flatten | None | No | current eager cache/effects possible | Critical | P0 |
| scored runtime | `rules/runtime.py:168-236` | `evaluate_rule` | match/evidence dict | bool of match | evidence | collapse | No | N/A | High | P0 |
| Career interpreter | `interpreters/career.py:45-64` | both runtime evaluators | RuleMatch-like/legacy dict | `bool(.matched/.match)` | matched paths | broad fallback | No | N/A | Critical scoring/output | P0 |
| condition unit test | `tests/rules/test_predicate_result.py:58-64` | `evaluate_condition` | `PredicateResult` | `.matched` | None | None | No | N/A | Medium | P1 |
| Yoga integration test | `tests/enrichments/test_yoga_engine_rule_driven.py:17-37` | Yoga API | Yoga dictionaries | implicit | type only | None | No | does not assert | High | P1 |

Active code caller symbols requiring migration: **4**. Loader/YAML validation and downstream snapshots are additional indirect compatibility surfaces, but are not included in this direct caller count.

## 21. Existing Tests and Coverage Gaps

Existing coverage proves one matched predicate leaf returns `PredicateResult`, basic Yoga output exists, flat runtime matched/unmatched behavior, and runtime rule-registry merge behavior. It does not directly test any logical operator.

| Area | Missing Categories | Count | Recommended Test File |
|---|---|---:|---|
| Predicate leaf | evidence, error, trace, unknown predicate | 4 | `tests/rules/test_condition_leaf.py` |
| AND | all matched, early/later unmatched, missing, invalid, error, short-circuit, skipped, empty | 9 | `tests/rules/test_condition_and.py` |
| OR | early/later match, all false, missing, invalid, error-then-match, short-circuit, skipped, empty | 9 | `tests/rules/test_condition_or.py` |
| NOT | matched, unmatched, missing, invalid, error, zero, multiple | 7 | `tests/rules/test_condition_not.py` |
| Invalid | unknown operator, missing operator, malformed children, invalid leaf, nesting bound | 5 | `tests/rules/test_condition_validation.py` |
| Integration | loader validation, domain compatibility, cold/warm, repeat determinism, child preservation | 5 | `tests/rules/test_condition_integration.py` |

Missing condition-evaluator test categories: **39**.

## 22. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Typed condition result | MISSING | logical nodes use PredicateResult | engine/models | approved internal bridge | IN_SCOPE | P0 | Yes |
| Preserve complete child results | NONCOMPLIANT | fields reduced to evidence/summary | engine | retain typed children | IN_SCOPE | P0 | Yes |
| Typed status propagation | MISSING | six gap paths | engine/Yoga/runtime | approved statuses/precedence | IN_SCOPE | P0 | Yes |
| Deterministic short-circuit | NONCOMPLIANT | four eager paths | engine/Yoga | left-to-right stop policy | IN_SCOPE | P0 | Yes |
| Definition errors not factual false | NONCOMPLIANT | unknown IDs/operators false | loaders/evaluators | compile/runtime typed failure | IN_SCOPE | P0 | Yes |
| Condition schema/arity validation | MISSING | malformed raises/ignored | loaders/evaluator | canonical validation boundary | IN_SCOPE | P0 | Yes |
| Canonical registry-only factual path | NONCOMPLIANT | runtime/Yoga duplicates | runtime/Yoga | migrate/isolate adapters | IN_SCOPE | P0 | Yes |
| NOT semantics | MISSING | treated unknown predicate | engine | exact-one typed inversion | IN_SCOPE | P1 | Yes |
| Skipped-branch representation | MISSING | none | engine/models | typed skip trace | IN_SCOPE | P1 | Yes |
| Evidence identity preservation | NONCOMPLIANT | anonymous evidence lists | engine/Yoga | retain structured linkage | IN_SCOPE | P1 | Yes |
| Typed error preservation | NONCOMPLIANT | flatten/swallow/generic strings | all evaluators | typed ordered errors | IN_SCOPE | P1 | Yes |
| Nested deterministic traces | NONCOMPLIANT | summaries/UUID/timing | engine/Yoga/runtime | stable node trace lineage | IN_SCOPE | P1 | Yes |
| Malformed/cycle/depth safety | MISSING | uncontrolled recursion/errors | loader/evaluator | validation/bounds | IN_SCOPE | P1 | Yes |
| Cache/short-circuit equivalence | NONCOMPLIANT | eager cache population/sticky false | engine | align after Audit-11 decisions | IN_SCOPE | P1 | Yes |
| Condition contract tests | MISSING | 39 categories | tests | focused suites | IN_SCOPE | P1 | Yes |
| Legacy runtime scoring compatibility | PARTIAL | Career depends on dict/score | runtime/Career | explicit compatibility adapter | TEMPORARY_COMPATIBILITY | P2 | No |
| Dormant Yoga evaluator retirement | PARTIAL | confirmed unused duplicate | Yoga | remove after semantic migration | TEMPORARY_COMPATIBILITY | P2 | No |
| Empty AND/OR policy | UNKNOWN | Python identities only | DSL/compiler | architectural decision | IN_SCOPE | P2 | No |
| Broader baseline DSL operators | MISSING | EXISTS/ANY/ALL/etc absent | future DSL | Audit-13/later staged work | OUT_OF_SCOPE_FUTURE_STAGE | P3 | No |

## 23. Migration Risks and Priorities

The 19 findings total **P0=7, P1=8, P2=3, P3=1**. Highest risks are changing Yoga rule firing when unknown IDs become errors, altering predicate cache population when short-circuiting is introduced, changing Career score/public snapshots while retiring runtime dictionaries, and inventing status precedence without approval. Migration must keep child order deterministic and preserve factual evidence while separating logical nodes from predicate identity.

## 24. Unresolved Architectural Questions

1. What exact status precedence applies to AND/OR/NOT mixed outcomes?
2. Are empty AND and OR valid identity nodes or invalid definitions?
3. What immutable `ConditionResult` shape preserves nested children and leaf PredicateResults?
4. How are skipped branches represented without fabricating predicate evaluation?
5. Must runtime direct invocation return typed definition errors after compiler validation fails or is bypassed?
6. Which legacy runtime/Career behavior remains behind a temporary adapter?
7. Is condition-result caching intentionally absent, and what telemetry belongs in condition serialization?

Questions 1–4 block safe condition-model/operator implementation; none blocks completion of this audit.

## 25. Audit-12 Conclusion

Audit-12 is COMPLETE. Four evaluator contracts were discovered, three are active, and only one is canonical. AND/OR are eager and lossy; NOT, typed condition results/status, skipped branches, full child preservation, validation, and correct unknown-definition behavior are missing. Exactly this report was created; no production code, tests, fixtures, rules, previous reports, or Audit-13 artifacts were modified.

### Summary counts

| Metric | Count |
|---|---:|
| Condition evaluators discovered | 4 |
| Active production evaluators | 3 |
| Canonical evaluators | 1 |
| Legacy or alternate evaluators | 3 |
| Evaluators returning PredicateResult for logical nodes | 1 |
| Tuple or raw-boolean evaluator contracts | 1 |
| Logical operators supported | 2 |
| Required logical operators missing | 1 |
| Non-short-circuit paths | 4 |
| Status-propagation gaps | 6 |
| Evidence-loss paths | 4 |
| Error-loss paths | 6 |
| Trace-loss paths | 6 |
| Unknown predicates becoming unmatched | 4 |
| Unknown operators becoming unmatched | 2 |
| Active callers requiring migration | 4 |
| Missing condition-evaluator test categories | 39 |
| P0 findings | 7 |
| P1 findings | 8 |
| P2 findings | 3 |
| P3 findings | 1 |
