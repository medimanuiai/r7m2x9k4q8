# Prompt-01 Audit-02: Complete Predicate Inventory

## 1. Executive Summary

The repository contains **6 production registered predicate IDs**, implemented by **5 unique production handlers**. This exactly reconciles with Audit-1: `ASPECT`, `ASPECT_EXISTS`, `FUNCTIONAL_ROLE`, `HOUSE_OCCUPANT`, `PLANET_EXALTED`, and `PLANET_IN_HOUSE`. `ASPECT` and `ASPECT_EXISTS` are two registry keys for the same handler, not two implementations. One additional predicate, `RAISE_TEST`, is registered dynamically inside a test and is not a persistent production predicate.

The broader inventory found **12 unregistered predicate-like or condition-evaluation helpers**: four active raw-boolean factual primitives, two active legacy rule evaluators, four dormant Yoga-local tuple-return factual helpers, one dormant Yoga-local tuple condition dispatcher, and the active central condition evaluator. Five helpers return predicate-like tuples and four return raw booleans. The remaining three return dictionaries or `PredicateResult` while dispatching factual or logical conditions.

The registered predicates already return the initial frozen `PredicateResult`, but none satisfies the complete Prompt-01 contract. All six lack versions, parameter schemas/validation, typed status, typed errors, predicate trace steps, capability declarations, and safe versioned cache identity. `ASPECT` is noncompliant because the result identifies itself as `ASPECT_EXISTS`. `FUNCTIONAL_ROLE` is noncompliant with the AstroState-only boundary because it reads YAML selected from the process working directory through `compute_functional_roles`.

The most important compatibility boundary is the active Career path: `career.interpret_career` calls `runtime.evaluate_rule_with_score`, which performs factual checks and scoring outside the central predicate registry. Per the approved scope direction, this audit does **not** prescribe automatic migration or deletion of those raw-boolean functions. It records them as active temporary compatibility behavior requiring an explicit Prompt-01 migration-boundary decision.

Countable findings are **5 P0, 10 P1, 6 P2, and 0 P3**. No fixes were implemented.

## 2. Audit Scope and Method

Authoritative inputs were applied in the approved order:

1. `Documentation/AI-Prompt/Jyothishyam Master Architecture Specification v1.0.docx`, especially predicate philosophy, requirements, result contract, central registration, naming, composition, caching, rule validation, predicate resolution/metadata/versioning, and global invariants.
2. `Documentation/AI-Prompt/Prompt-01.docx`, especially sections 1-3, 10-29, 30-31, and 35-37.
3. `systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-01-Predicate-Registry.md` as the completed preceding audit.
4. Source, tests, rule data, fixtures, scripts, and utilities as evidence of current behavior.

Repository-wide searches covered Python, YAML/YML, JSON, Markdown references, registration decorators, registry mutation, `PredicateResult`, tuple/boolean returns, direct type dispatch, callers, imports, rule IDs, and test-only registration. Generated/dependency/cache/Git locations were excluded. Caller searches included direct invocation, imports, string-based rule dispatch, YAML condition types, test harnesses, and integration tests.

Static analysis was used for counts and active-path classification. The targeted command

```text
python -B -m pytest -p no:cacheprovider tests/rules/test_predicate_result.py systems/Parasara/tests/test_rule_runtime.py systems/Parasara/tests/test_rule_runtime_merge.py tests/enrichments/test_yoga_engine_rule_driven.py -q
```

did not execute because the available interpreter reports `No module named pytest`. This is an environment limitation, not a failing test result. No full suite, formatter, generator, or mutating tool was run.

The inventory applies this boundary: a factual astrological question is predicate-like even when implemented inside legacy rule dispatch. Scoring, confidence, narrative, output assembly, and logical composition are not factual predicates; mixed evaluators are recorded because they contain or dispatch factual checks, but are not promoted to registered-predicate status.

## 3. Inventory Reconciliation with Audit-1

Audit-1 reported six production registry keys and five unique production handlers. Audit-2 found the same decorator set and no additional production registration or direct registry assignment:

- `systems/Parasara/engine/rules/predicates.py:12-14` registers `ASPECT` and `ASPECT_EXISTS` on `aspect_exists`.
- `systems/Parasara/engine/rules/predicates.py:50-57` registers `PLANET_IN_HOUSE`.
- `systems/Parasara/engine/rules/predicates.py:60-67` registers `HOUSE_OCCUPANT`.
- `systems/Parasara/engine/rules/predicates.py:70-82` registers `FUNCTIONAL_ROLE`.
- `systems/Parasara/engine/rules/predicates.py:85-99` registers `PLANET_EXALTED`.

The only additional decorator use is test-local `RAISE_TEST` at `tests/rules/test_predicate_result.py:39-55`. It exists only while that test module executes and is manually removed, so it is counted as one test-only predicate and not as a seventh production predicate.

The Audit-2 helper count is intentionally broader than Audit-1's registry-mechanism count. Audit-1 described two bypass mechanisms as units; Audit-2 inventories their individual factual helpers and condition/rule evaluators. This difference does not change the registered-predicate count.

## 4. Complete Registered Predicate Inventory

All production handlers share the signature `(params: Dict[str, Any], astro: AstroState, context: Dict[str, Any]) -> PredicateResult`. None declares a predicate version, status model, parameter schema, required capability, or cache policy. `evaluate_predicate` caches all results unconditionally using `(id(astro), uppercased_name, serialized_params)` and omits predicate version, AstroState digest, context, and capability/enrichment versions (`systems/Parasara/engine/rules/engine.py:24-25,39-57,113-131`).

| Predicate ID | Aliases | File | Handler | Signature | Return Contract | Version | Status Support | Parameters | Required Capabilities | Evidence Quality | Trace Support | Purity | Cacheable | Callers | Tests | Compliance | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ASPECT` | Implicit alias of `ASPECT_EXISTS`; lookup accepts case variants | `systems/Parasara/engine/rules/predicates.py:12-47` | `aspect_exists` | Common signature | Initial `PredicateResult`, but result ID is always `ASPECT_EXISTS` | None | None | Optional `from_house`, `to_house`, `from_planet`, `to_planet`; no types/default schema/unknown-key checks | `astro.planets`; `astro.enrichments.aspects.edges` | Matched: full edge objects. Unmatched/missing graph: `{}`; malformed edges silently skipped | Empty handler trace | Read-only, but catches edge errors and returns mutable edge references | Currently always cached; logically eligible only with stable AstroState/enrichment/version identity | Yoga YAML uses `ASPECT` at `yogas.yaml:14,45`; active through `yoga_engine.py:150-156` | Indirect Yoga integration only; no alias-identity assertion | **NONCOMPLIANT**: canonical ID mismatch and missing contract fields | IN_SCOPE | P0 |
| `ASPECT_EXISTS` | Same handler as `ASPECT`; lookup accepts case variants | `predicates.py:12-47` | `aspect_exists` | Common signature | Initial `PredicateResult` | None | None | Same four optional keys; unvalidated | Same as `ASPECT` | Same as `ASPECT` | Empty | Same as `ASPECT` | Currently cached under a separate key from `ASPECT` | No repository rule/caller invokes this ID directly; registry/test imports expose it | No direct invocation test | **PARTIAL** | IN_SCOPE | P1 |
| `PLANET_IN_HOUSE` | Case variants via lookup; no declared alias | `predicates.py:50-57` | `planet_in_house` | Common signature | Initial `PredicateResult` | None | None | De facto required `planet`, `house`; no validation; missing/wrong values become false | `astro.planets[].name/house` | Matched: requested planet and house. Unmatched/missing planet: `{}` | Empty | Read-only and deterministic for a stable AstroState | Currently always cached; cache identity is insufficient if AstroState mutates | Direct test/evaluator use at `tests/rules/test_predicate_result.py:14-27,58-64,67-74` | Direct matched, warm-cache, condition bridge, serialization tests; no invalid/missing/unmatched evidence test | **PARTIAL** | IN_SCOPE | P1 |
| `HOUSE_OCCUPANT` | Case variants; no declared relationship to `PLANET_IN_HOUSE` | `predicates.py:60-67` | `house_occupant` | Common signature | Initial `PredicateResult` | None | None | De facto required `house`, `planet`; no validation | `astro.planets[].name/house` | Matched: planet and house. Unmatched/missing planet: `{}` | Empty | Read-only and deterministic for stable input | Currently always cached; same deficiencies | Yoga YAML at `yogas.yaml:68-71`; active through central evaluator | Indirect Yoga integration; no dedicated behavior test | **PARTIAL**; duplicates `PLANET_IN_HOUSE` behavior without alias metadata | IN_SCOPE | P1 |
| `FUNCTIONAL_ROLE` | Case variants; no declared alias | `predicates.py:70-82` | `functional_role` | Common signature | Initial `PredicateResult` | None | None | `role_in` defaults to `[]`; `context.planets` optional; no validation | Lagna, planets, functional-role tables/computation | Matched: planet names. Unmatched: `{}`; no source/table evidence | Empty | **Not AstroState-only**: calls file-backed `compute_functional_roles` | Currently cached although context is omitted from key and table/CWD state can change | Yoga YAML at `yogas.yaml:18-20,72-74`; active through central evaluator | Indirect Yoga integration; enrichment tests do not test predicate contract | **NONCOMPLIANT**: filesystem/CWD dependency and unsafe cache identity | IN_SCOPE | P0 |
| `PLANET_EXALTED` | Case variants; conceptually overlaps legacy `is_exalted` | `predicates.py:85-99` | `planet_exalted` | Common signature | Initial `PredicateResult` | None | None | De facto required `planet`; no validation | Planet lookup; attempts `PlanetState.__dict__.flags`; falls back to `astro.metadata.exaltations` | Matched: flag or metadata degree. Unmatched/missing planet: `{}` | Empty | Read-only and deterministic for stable input, but data-source contract is unclear | Currently always cached; cache identity insufficient | Direct evaluator use only in test | One unmatched test at `test_predicate_result.py:30-36` | **PARTIAL**; source semantics and missing-data behavior unresolved | IN_SCOPE | P1 |

Additional verified details:

- `PlanetState` has no declared `flags` field (`systems/Parasara/engine/astrostate.py:12-21`), while the upstream `Planet` model does (`systems/Parasara/engine/models.py:11-18`). `PLANET_EXALTED` therefore depends on extra/unmodeled state or metadata after normalization. This is a compatibility/semantic concern, not a recommendation to change exaltation mathematics in Prompt-01.
- `FUNCTIONAL_ROLE` resolves tables from `os.getcwd()/rules/parashara/functional_roles` and then a systems fallback (`functional_roles.py:16-47`). Its output can vary with working directory and file contents even when AstroState, params, and context are unchanged.
- Every handler receives and stores `params` without a defensive copy; evidence and trace/error collections are mutable despite the frozen outer dataclass (`engine.py:9-18`).

## 5. Predicate Aliases and ID Variants

There is exactly **one explicit alias relationship inferred from implementation**: `ASPECT` and `ASPECT_EXISTS` are stacked decorators on one function (`predicates.py:12-14`). The registry has no alias metadata, canonical-ID field, deprecation status, or replacement reference. `ASPECT` is used by current Yoga YAML; `ASPECT_EXISTS` is not directly invoked by repository rules or tests. This evidence is insufficient to decide whether the IDs must remain aliases, whether one is deprecated, or whether their semantics should diverge. That decision remains intentionally open.

Registration and lookup apply `str.upper()` (`engine.py:28-30,54-60`), so ordinary case variants such as `aspect`, `Aspect`, and `ASPECT` resolve to the same key. These are normalization variants, not counted as aliases. Whitespace is not trimmed. The legacy runtime instead compares exact lowercase rule types (`runtime.py:90-108,162-236`), creating a separate ID policy.

Logical `AND` and `OR` are not registered factual predicates. The current central condition evaluator nevertheless emits a `PredicateResult` whose `predicate_id` is `AND` or `OR` (`engine.py:142-159`). `NOT` is absent. These logical IDs are recorded as a condition-boundary issue, not included in the six registered predicates.

## 6. Unregistered Predicate-Like Helpers

The following count is function-based. Inline factual branches within `evaluate_rule_with_score` are described in that function's row rather than inflated into separate function counts.

| File | Symbol | Function Type | Return Contract | Duplicates Predicate | Confirmed Callers | Active Path | Registration Status | Migration Required | Scope | Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `systems/Parasara/engine/rules/runtime.py:10-34` | `in_sign` | Factual primitive | `bool` | No registered equivalent | `is_exalted`; `evaluate_rule`; direct test; YAML type `in_sign` | Yes, through legacy runtime and tests | Unregistered | Boundary decision required; do not automatically delete or redesign | TEMPORARY_COMPATIBILITY | Raw boolean, no evidence/errors; mutates test instrumentation | P1 |
| `runtime.py:37-44` | `in_house` | Factual primitive | `bool` | Yes: `PLANET_IN_HOUSE` and `HOUSE_OCCUPANT` | `evaluate_rule`; direct test; YAML `in_house` | Yes | Unregistered | Reconcile without changing behavior unless approved in Prompt-01 scope | TEMPORARY_COMPATIBILITY | Three implementations of the same basic fact | P1 |
| `runtime.py:47-61` | `lord_of_house` | Factual primitive | `bool` | No registered production equivalent; Master Architecture lists `HOUSE_LORD` as target example | `evaluate_rule`; direct test | Yes | Unregistered | Preserve pending scope decision | TEMPORARY_COMPATIBILITY | Raw bool; no missing-house distinction | P1 |
| `runtime.py:64-73` | `is_exalted` | Factual primitive | `bool` | Conceptually duplicates `PLANET_EXALTED`, but takes expected sign and uses different semantics | `evaluate_rule`; calls `in_sign` | Yes | Unregistered | Preserve semantics; reconcile identity/contract only if placed in scope | TEMPORARY_COMPATIBILITY | Double instrumentation side effect; semantic mismatch | P1 |
| `runtime.py:76-108` | `evaluate_rule` | Legacy factual dispatcher | `dict` with `match` and `evidence` | Dispatches the four primitives above | `evaluate_rule_with_score`; Career fallback; direct tests | Yes | Not a predicate registration | Caller/adapter boundary must be handled; function itself is a rule evaluator | TEMPORARY_COMPATIBILITY | Collapses missing/unsupported states into false dictionaries | P0 |
| `runtime.py:111-269` | `evaluate_rule_with_score` | Mixed rule evaluator with inline factual checks and scoring | Serialized `RuleMatch` dictionary | Inline house/strength, lord dignity, Yoga, and aspect checks overlap registered/legacy facts | Career interpreter `career.py:45-64`; rule coverage and artifact scripts; merge test | Yes | Not registered | Keep scoring behavior unchanged; isolate factual-result migration boundary explicitly | TEMPORARY_COMPATIBILITY | Predicate boundary violation if treated as predicate; active bypass of central registry | P0 |
| `systems/Parasara/engine/enrichments/yoga_engine.py:22-52` | `_eval_aspect_condition` | Yoga factual helper | `(bool, dict)` | Yes: `ASPECT`/`ASPECT_EXISTS` | Only `_eval_condition` at line 117; `_eval_condition` has no external caller | No confirmed active path | Unregistered | Do not activate; classify for later retirement/migration decision | TEMPORARY_COMPATIBILITY | Duplicate semantics and unordered `set` evidence | P2 |
| `yoga_engine.py:55-67` | `_eval_functional_role_condition` | Yoga factual helper | `(bool, dict)` | Yes: `FUNCTIONAL_ROLE` | Only dormant `_eval_condition` | No | Unregistered | Do not activate; preserve until approved disposition | TEMPORARY_COMPATIBILITY | Same file/CWD dependency; tuple contract | P2 |
| `yoga_engine.py:70-91` | `_eval_house_lords_combination` | Yoga factual helper | `(bool, dict)` | No registered equivalent | Only dormant `_eval_condition`; YAML references ID through active central path | Helper inactive; referenced concept active but unresolved | Unregistered | P0 migration/registration/validation boundary decision required; no semantic redesign here | IN_SCOPE | Active YAML becomes unknown-predicate false | P0 |
| `yoga_engine.py:94-99` | `_eval_house_occupant` | Yoga factual helper | `(bool, dict)` | Yes: `HOUSE_OCCUPANT` and `PLANET_IN_HOUSE` | Only dormant `_eval_condition` | No | Unregistered | Do not activate; preserve pending disposition | TEMPORARY_COMPATIBILITY | Duplicate and different unmatched evidence | P2 |
| `yoga_engine.py:102-125` | `_eval_condition` | Yoga logical/factual dispatcher | `(bool, dict)` | Duplicates central condition evaluation and four factual handlers | Self-recursion and helpers only; active Yoga uses central evaluator at lines 150-156 | No confirmed active path | Unregistered; `AND`/`OR` are not predicates | Must not remain an active tuple bypass after Prompt-01; currently dormant | TEMPORARY_COMPATIBILITY | Legacy bypass could be reactivated accidentally | P2 |
| `systems/Parasara/engine/rules/engine.py:135-162` | `evaluate_condition` | Central logical-condition evaluator | `PredicateResult` for logical nodes and leaves | Duplicates condition-dispatch role, not a factual predicate | Yoga engine; direct condition test; self-recursion | Yes | Not registered; correctly infrastructure rather than factual predicate | Prompt-01 explicitly includes its typed-result boundary | IN_SCOPE | Uses predicate result identity for logical operators; no short circuit; child results reduced to evidence/trace summaries | P1 |

Unrelated boolean/tuple utilities were searched but excluded from the predicate count after boundary review. Examples include `tools/rules_lint.py:14-26`, `systems/Parasara/tools/ci_snapshot_check.py:34-35`, and `tests/testing_framework/json_compare.py:30-82`; they answer tooling/comparison questions, not astrological facts. Surya Siddhanta combustion/retrograde callables are astronomy-system calculations, and the Master Architecture explicitly prohibits treating Surya Siddhanta as a predicate (`Master Architecture`, global invariants).

## 7. Duplicate Predicate Implementations

This audit counts **7 duplicate or conceptually overlapping implementations**, excluding `ASPECT`/`ASPECT_EXISTS` because those are two IDs pointing to one implementation:

1. Registered `house_occupant` duplicates registered `planet_in_house` (`predicates.py:50-67`).
2. Legacy `runtime.in_house` duplicates both registered house-occupancy handlers (`runtime.py:37-44`).
3. Legacy `runtime.is_exalted` overlaps `PLANET_EXALTED` but implements a different sign-based contract (`runtime.py:64-73`; `predicates.py:85-99`).
4. Yoga `_eval_aspect_condition` duplicates the registered aspect handler with a narrower parameter set (`yoga_engine.py:22-52`).
5. Yoga `_eval_functional_role_condition` duplicates `FUNCTIONAL_ROLE` (`yoga_engine.py:55-67`).
6. Yoga `_eval_house_occupant` duplicates both registered house-occupancy handlers (`yoga_engine.py:94-99`).
7. Inline `aspect_on_house`/`afflict_house` logic in `evaluate_rule_with_score` overlaps the aspect predicate concept (`runtime.py:221-229`).

These are compatibility findings, not instructions to merge them. Differences in parameter shape, evidence, missing-data behavior, instrumentation, aspect data shape, and exaltation semantics must be preserved until approved migration decisions and tests establish equivalence.

## 8. Test-Only and Dynamically Registered Predicates

`RAISE_TEST` is the only test-only/dynamic predicate found (`tests/rules/test_predicate_result.py:39-55`). Its local handler `_raise(params, astro, context)` raises `RuntimeError('boom')`; it has no return contract on the successful path, version, schema, capabilities, or metadata. The test verifies that `evaluate_predicate` converts the exception into a `PredicateResult` with at least one error.

The decorator mutates the production global registry and cleanup uses `PREDICATE_REGISTRY.pop` after assertions. A failure before cleanup can leak the handler, and registration does not invalidate same-ID cache entries. It is test-only, scope `IN_SCOPE` for registry/error-contract test migration, risk P2. No fixture/YAML/JSON-defined handler registration, dynamic ID construction for predicate registration, plugin registry, or second production registry was found.

Existing test coverage by registered ID:

- `PLANET_IN_HOUSE`: direct matched, cache, condition, and serialization coverage (`test_predicate_result.py:14-27,58-74`).
- `PLANET_EXALTED`: direct unmatched coverage only (`test_predicate_result.py:30-36`).
- `ASPECT`, `HOUSE_OCCUPANT`, and `FUNCTIONAL_ROLE`: exercised indirectly by the Yoga integration path because the evaluator processes all children (`tests/enrichments/test_yoga_engine_rule_driven.py:17-37`), but individual results, evidence, error behavior, and aliases are not asserted.
- `ASPECT_EXISTS`: no direct invocation or ID-specific test.

Thus one registered ID has no observed test execution, while four IDs lack dedicated predicate behavior tests.

## 9. Predicate Boundary Violations

1. `FUNCTIONAL_ROLE` does not query only normalized AstroState. It invokes `compute_functional_roles`, which reads YAML from CWD-dependent paths (`predicates.py:70-82`; `functional_roles.py:16-47,50-162`). This also makes cache correctness depend on state absent from the key.
2. The four legacy boolean primitives update process-global test instrumentation through `record_predicate` (`runtime.py:10-73`; `tests/testing_framework/instrumentation.py:4-25`). They are therefore not pure even though the astrological return value is deterministic for stable inputs.
3. `evaluate_rule_with_score` combines factual evaluation with rule score assignment (`runtime.py:159-240`). It is a rule evaluator, not a predicate, but it is an active bypass that prevents a truthful claim that all factual evaluation flows through the central predicate engine.
4. `evaluate_condition` represents `AND` and `OR` as `PredicateResult` identities (`engine.py:142-159`). Logical operators are not registered factual predicates; a typed condition boundary is required by Prompt-01 if needed.
5. `evaluate_yoga_rules` mutates `astro.enrichments['yogas']` and creates random UUID trace IDs (`yoga_engine.py:14-15,169-185`). This is Yoga-engine behavior, not registered predicate behavior, but it must not be moved into predicates during migration.
6. The dormant Yoga-local `_eval_condition` is a tuple-return bypass around the registry (`yoga_engine.py:102-125`). It is not active today, but would violate Prompt-01 if reactivated.

No registered predicate was found accessing raw Surya JSON, network services, system time, domain scores, confidence, narratives, or public-output assembly directly.

## 10. Caller and Active-Path Summary

The active central path is:

```text
yogas.yaml condition
  -> yoga_engine.evaluate_yoga_rules
  -> engine.evaluate_condition
  -> engine.evaluate_predicate
  -> PREDICATE_REGISTRY handler
```

Evidence: `yoga_engine.py:6-7,128-156`; `engine.py:135-162`; `yogas.yaml:11-20,38-48,65-74`.

The active legacy/domain path is:

```text
career.interpret_career
  -> runtime.evaluate_rule_with_score
  -> runtime.evaluate_rule and/or inline factual branches
  -> raw bool/dict results
  -> scoring and serialized RuleMatch dictionary
```

Evidence: `systems/Parasara/engine/interpreters/career.py:33-64`; `runtime.py:76-108,111-269`. Test/artifact callers also execute this path at `systems/Parasara/tests/test_rule_runtime_merge.py:9-22`, `tests/testing_framework/rule_coverage.py:7-27`, and `tests/testing_framework/generate_full_artifacts.py:51-79`.

The Yoga-local tuple path is dormant. Repository searches found `_eval_condition` only in its definition, self-recursion, and calls to its four local helpers (`yoga_engine.py:102-125`). Active Yoga evaluation calls imported central `evaluate_condition`, not the local underscore function (`yoga_engine.py:154`). Its apparent lack of callers was therefore verified by direct symbol search, import search, and active call-site inspection.

Rule-data reconciliation:

- Central Yoga condition IDs: `ASPECT`, `FUNCTIONAL_ROLE`, `HOUSE_LORDS_COMBINATION`, `HOUSE_OCCUPANT` (`yogas.yaml:14-18,41-45,68-72`). Three resolve; `HOUSE_LORDS_COMBINATION` does not.
- Legacy rule types: `in_house`, `in_sign`, `strong_in_10`, `lord_status`, `rajayoga_naive`, `aspect_on_house`, and `afflict_house` occur in `systems/Parasara/rules/parashara/v1/*.yml|yaml` and resolve through runtime string branches rather than the predicate registry.
- `strong_in_house` and `is_exalted` are supported in code but were not found in current rule data. `lord_of_house` is directly tested and supported by `evaluate_rule`, but not found in current rule YAML.

## 11. Prompt-01 Compliance Assessment

Inventory summary:

| Measure | Count | Basis |
|---|---:|---|
| Production registered predicate IDs | 6 | Registry keys after importing `predicates.py` |
| Unique production registered handlers | 5 | `ASPECT` and `ASPECT_EXISTS` share one handler |
| Explicit inferred aliases | 1 | `ASPECT` -> shared `ASPECT_EXISTS` handler; case variants excluded |
| Test-only predicates | 1 | `RAISE_TEST` |
| Unregistered predicate-like/condition helpers | 12 | Function-based inventory in section 6 |
| Tuple-return helpers | 5 | Four Yoga factual helpers plus Yoga `_eval_condition` |
| Boolean-return factual helpers | 4 | Legacy runtime primitives |
| Duplicate/overlapping implementations | 7 | Section 7 definition |
| Registered predicates without any observed test execution | 1 | `ASPECT_EXISTS`; four IDs additionally lack dedicated behavior tests |
| Registered predicates without versions | 6 | No version field/registration metadata |
| Registered predicates without parameter validation | 6 | Dictionary `.get` only |
| Registered predicates lacking factual unmatched evidence | 6 | All return `{}` for ordinary non-match/missing fact |
| Registered predicates lacking predicate trace steps | 6 | Every handler returns `trace_steps=[]` |
| Registered predicates with suspected purity/boundary violations | 1 | `FUNCTIONAL_ROLE` file/CWD dependency |
| Predicates/helpers whose repository active-path status remains unknown | 0 | Active, test-only, or dormant status established statically |

Compliance classification totals for production registered IDs: **4 PARTIAL, 2 NONCOMPLIANT, 0 IMPLEMENTED, 0 MISSING, 0 UNKNOWN**. `MISSING` is not used for an existing registered ID merely because fields are absent; those existing handlers are partial/noncompliant implementations. `HOUSE_LORDS_COMBINATION` is a missing registration/helper migration issue, not a registered predicate row.

Cross-cutting noncompliance applies to every registered ID:

- no predicate version or registration metadata (`engine.py:21-32`);
- no parameter schema or validation (`predicates.py:14-99`);
- no typed status or typed error model (`engine.py:9-18`);
- no trace steps from handlers;
- missing capabilities become ordinary unmatched results;
- exceptions are universally swallowed into untyped errors (`engine.py:119-132`);
- cache keys omit required digest/version/context inputs (`engine.py:39-44`);
- deep immutability and canonical serialization are absent.

## 12. Migration Priorities and Risks

The following numbered findings define the reported priority totals.

| # | Priority | Finding | Evidence |
|---:|---|---|---|
| 1 | P0 | `ASPECT` returns canonical ID `ASPECT_EXISTS`; alias/deprecation semantics are ungoverned | `predicates.py:12-14,38-46`; `yogas.yaml:14,45` |
| 2 | P0 | `FUNCTIONAL_ROLE` violates the AstroState-only boundary and cannot be safely cached with the current key | `predicates.py:70-82`; `functional_roles.py:16-47`; `engine.py:39-44` |
| 3 | P0 | Active YAML references unregistered `HOUSE_LORDS_COMBINATION`, which becomes cached false/unknown while its only implementation is dormant | `yogas.yaml:41-44`; `yoga_engine.py:70-91,120-121`; `engine.py:62-77` |
| 4 | P0 | Active Career factual evaluation bypasses the registry through mixed legacy rule/scoring dispatch | `career.py:45-64`; `runtime.py:159-240` |
| 5 | P0 | `evaluate_rule` remains an active raw-dictionary factual boundary and Career fallback | `runtime.py:76-108`; `career.py:48-52` |
| 6 | P1 | All six registrations lack version and required registry metadata | `engine.py:21-32`; all decorators in `predicates.py` |
| 7 | P1 | All six handlers lack parameter schemas and validation | `predicates.py:14-99` |
| 8 | P1 | All six lack typed status, typed errors, and predicate trace steps | `engine.py:9-18`; `predicates.py:38-99` |
| 9 | P1 | Missing capabilities/data are conflated with factual false | `predicates.py:16-17,54-57,64-67,89-99` |
| 10 | P1 | All six lack useful factual unmatched evidence | `predicates.py:42,56,66,81,90,98-99` |
| 11 | P1 | Four active raw-boolean primitives sit outside the central predicate contract | `runtime.py:10-73,90-106` |
| 12 | P1 | `PLANET_EXALTED` reads a flag absent from declared `PlanetState` and uses a metadata fallback with unresolved compatibility semantics | `astrostate.py:12-21`; `predicates.py:85-99` |
| 13 | P1 | `PLANET_IN_HOUSE` and `HOUSE_OCCUPANT` duplicate one fact without alias/identity policy | `predicates.py:50-67` |
| 14 | P1 | Central condition evaluation uses predicate identity for logical operators and lacks `NOT`/short-circuit semantics required by Prompt-01 preservation rules | `engine.py:135-162` |
| 15 | P1 | Existing tests do not establish the complete registered-predicate contract | `test_predicate_result.py:14-74`; Yoga integration lines 17-37 |
| 16 | P2 | Test registration can leak/overwrite global registry state and leave cache entries | `test_predicate_result.py:39-55`; `engine.py:22-25,28-36` |
| 17 | P2 | Legacy factual primitives mutate global instrumentation, violating purity | `runtime.py:10-73`; `instrumentation.py:4-25` |
| 18 | P2 | Dormant Yoga tuple evaluator and four tuple helpers duplicate the active engine and could be reactivated | `yoga_engine.py:22-125,150-156` |
| 19 | P2 | Yoga aspect evidence uses `list(set(...))`, making ordering noncanonical | `yoga_engine.py:29-52` |
| 20 | P2 | Central and legacy predicate/type normalization differ (uppercase vs exact lowercase) | `engine.py:28-30,54-60`; `runtime.py:90-108,162-236` |
| 21 | P2 | Functional-role table ownership and CWD selection can change factual results across runtime environments | `functional_roles.py:16-47` and both `rules/parashara/functional_roles` and `systems/Parasara/enrichment_tables/functional_roles` |

Primary migration risks are breaking active Yoga rules when validating unknown IDs, changing Career scoring while migrating factual contracts, collapsing distinct alias/duplicate identities prematurely, changing simplified exaltation/aspect semantics, caching across context/version/table changes, and accidentally reactivating the dormant tuple path. Prompt-01 should standardize result contracts without silently redesigning those astrological calculations.

## 13. Unresolved Questions

1. Should `ASPECT` remain a compatibility alias of `ASPECT_EXISTS`, become a deprecated ID with an explicit replacement, or represent different semantics? Caller/rule evidence establishes that `ASPECT` is the active YAML ID; it does not settle the architecture decision.
2. Which legacy runtime facts (`in_sign`, `in_house`, `lord_of_house`, `is_exalted`, and inline higher-level checks) are explicitly inside Prompt-01 migration scope versus temporary compatibility adapters? The approved direction prohibits automatic migration/deletion.
3. Should `HOUSE_LORDS_COMBINATION` become a registered predicate, should the YAML migrate to a different approved composition, or is the rule invalid? This requires SME/architecture approval because activating the dormant implementation could change Yoga results.
4. Is functional-role computation required to be precomputed into AstroState before predicate evaluation, or is an approved query/capability service planned? Direct filesystem lookup violates the target boundary.
5. Are `PLANET_IN_HOUSE` and `HOUSE_OCCUPANT` intentionally distinct public vocabulary, aliases, or an accidental duplicate?
6. Which normalized source is authoritative for exaltation after adapter/normalizer processing: a PlanetState field, derived/enrichment data, or metadata? This audit does not change the current simplified behavior.

None of these questions blocks completion of the inventory. They block safe implementation decisions that would otherwise change identity, execution paths, or astrology semantics.

## 14. Audit-2 Conclusion

Audit-2 is complete. The production registry count remains six IDs/five handlers, with one test-only dynamic predicate. Twelve unregistered predicate-like or condition-evaluation functions were classified by return contract and active path. Seven duplicate/overlapping implementations were identified without assuming semantic equivalence.

No production code, tests, rule files, snapshots, or other audit documents were modified. Prompt-01 implementation must not begin from the registry list alone: the active legacy Career/runtime path, unresolved Yoga predicate, alias identity, filesystem-backed functional role behavior, and dormant tuple dispatcher define the migration boundary that later approved audits must reconcile.
