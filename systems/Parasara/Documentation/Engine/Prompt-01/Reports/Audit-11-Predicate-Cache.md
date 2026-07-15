# Prompt-01 Audit-11: Predicate Cache

## 1. Executive Summary

Audit-11 is **COMPLETE**. All ten prerequisite reports were available. One active predicate-related cache exists: process-global `_CACHE` in `systems/Parasara/engine/rules/engine.py:24-25`. One key-construction path uses `(id(astro), pname.upper(), json.dumps(params or {}, sort_keys=True, default=str))` with a weaker `str` fallback (`engine.py:39-44`).

The cache is not content-addressed, version-safe, context-isolated, capability-aware, mutation-safe, bounded, or thread-safe. All six registered predicates are cached unconditionally and are `NOT_CACHE_SAFE` under the current key. Predicate-version isolation is missing for all six IDs; one known context component (`FUNCTIONAL_ROLE.context['planets']`) and all six predicates' capability/version dependencies are absent.

The evaluator returns a cold result with `cache_hit=False`, stores a shallow `dataclasses.replace(..., cache_hit=True)`, and returns that same stored object on warm calls (`engine.py:54-57,94-115`). The only direct cold/warm field difference is `cache_hit`, but generated dataclass equality/serialization treat it as logical. Four nested mutable fields—inputs, evidence, errors, and trace steps—remain shared/corruptible.

Unmatched, invalid-input-as-unmatched, missing-capability-as-unmatched, and exception results are all sticky risks because every branch is cached without recovery-aware invalidation. Findings total **7 P0, 7 P1, 3 P2, and 1 P3**.

## 2. Audit Scope and Method

The audit reviewed Prompt-01, the Master Architecture, Audits 1–10, all cache/memoization searches, evaluator/registry/Yoga paths, result construction, parameters/context/capabilities/versions, callers, serialization, concurrency, memory, and tests. Counts are distinct implementation/key/risk categories unless explicitly per predicate. No cache was warmed/cleared persistently and no implementation/test file was modified. Pytest is unavailable.

## 3. Reconciliation with Audits 1–10

Audit-1 supplies missing predicate version/cacheable/deterministic metadata and dynamic-registration risks. Audits 2–4 establish six cached IDs and Yoga/global-clear callers. Audits 5–6 prove shallow result mutability and telemetry equality. Audit-7 supplies parameter-canonicalization gaps; Audit-8 capability recovery risks; Audit-9 the absent digest/object identity; Audit-10 classifies all six NOT_CACHE_SAFE. Audit-11 confirms these in the one implementation without disagreement.

## 4. Cache Implementation Inventory

| Cache | File | Symbol | Owner | Scope | Storage | Key Type | Value Type | Lifetime | Eviction | Clear Path | Thread-Safe | Production Use | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Predicate cache | `rules/engine.py:24-57` | `_CACHE` | module evaluator | Process/module/global | mutable dict | tuple[int,str,str] | `PredicateResult` with `cache_hit=True` | Until explicit clear/process exit | None/unbounded | `clear_cache`; Yoga and tests | No locks | Yes | One same-object cold/warm test |

Predicate-related cache count: **1**; active production count: **1**; key-construction paths: **1**. No condition/rule/Yoga duplicate memoization cache was found.

## 5. Cache-Key Construction

| Cache | Key Component | Current Source | Included | Canonical | Deterministic | Versioned | Mutable | Collision/Staleness Risk | Required Change | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| `_CACHE` | AstroState identity | `id(astro)` | Yes | No | Process-local | No | State content mutable | Equivalent objects split; mutated object stale | Approved state digest | P0 |
| `_CACHE` | Predicate ID | `pname.upper()` | Yes | Partial | Yes for string | No | Registry handler mutable | aliases split; replacement stale | canonical ID/version/scope | P0 |
| `_CACHE` | Parameters | sorted JSON/default string | Yes | Partial | Unsupported repr unstable | No | Caller values mutable | coercion/cycles/default/alias gaps | validated canonical params | P0 |
| `_CACHE` | Predicate version | none | No | No | N/A | No | N/A | all versions collide | include version | P0 |
| `_CACHE` | Evaluation context | none | No | No | N/A | No | context mutable | role candidate collisions | context identity | P0 |
| `_CACHE` | Capability/enrichment versions | none | No | No | N/A | No | enrichments mutable | stale after preparation/change | relevant versions/digests | P0 |
| `_CACHE` | system/plugin/normalization scope | none | No | No | N/A | No | configuration changes | cross-version semantic collision | approved scope/versions | P1 |

Process-identity dependencies: **1**. Missing predicate-version components: **6 predicate IDs**. Missing known context components: **1**. Missing capability/enrichment-version coverage: **6 predicate IDs**.

## 6. AstroState Identity and Digest

There is no AstroState digest (Audit-9). Separate equivalent objects never share entries; changed content in the same object retains entries; enrichment after cached false does not invalidate; cross-process reconstruction cannot address the same logical entry; version changes are invisible. Every scenario is NONCOMPLIANT/P0.

## 7. Predicate Identity and Version Isolation

Uppercasing provides only partial ID normalization. `ASPECT` and `ASPECT_EXISTS` generate separate keys despite sharing a handler, while the handler returns `ASPECT_EXISTS`. No predicate/handler version or system scope exists. Re-registering/replacing a handler does not clear entries; test registration can reuse stale same-ID keys; import order can change the callable without key change.

## 8. Parameter Canonicalization

Dictionary insertion order is stabilized by `sort_keys=True`. Eight remaining gaps are: schema/default materialization, aliases, unknown ignored keys, type/Boolean/float semantics, list-versus-tuple/set policy, enum/dataclass/Pydantic/date policy, custom-object `default=str`, and cycles/fallback/mutable caller values. Validation and normalization occur after key construction—or not at all (`engine.py:39-59`). Parameter-canonicalization gap count: **8**.

## 9. Evaluation-Context Isolation

No context enters the key. `FUNCTIONAL_ROLE` reads `context['planets']`, so different explicit candidate selections collide. No current registered predicate reads time, but future time/version/context values also have no representation. Omission versus explicit empty context semantics are unvalidated and untested.

## 10. Capability and Enrichment Isolation

Capability absent/None/empty/malformed/present and enrichment versions share the same state identity. A false Aspect result can persist after Yoga attaches a graph; functional-role table/config changes are invisible; partial versus complete facts collide. Current missing-capability results are ordinary unmatched and cached, so caching is unsafe within mutable lifecycle.

## 11. Predicate Cacheability and Purity

| Predicate ID | Declared Cacheable | Actually Cached | Purity | Context Dependency | Capability Dependency | Version Coverage | Current Key Safe | Classification | Required Action | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| `ASPECT` | Missing | Yes | MOSTLY_PURE_WITH_RISK | No | graph/planets/houses | None | No | NOT_CACHE_SAFE | digest/readiness/version | P0 |
| `ASPECT_EXISTS` | Missing | Yes | MOSTLY_PURE_WITH_RISK | No | same | None | No | NOT_CACHE_SAFE | same | P0 |
| `PLANET_IN_HOUSE` | Missing | Yes | PURE locally | No | planets/houses | None | No | NOT_CACHE_SAFE | content identity | P0 |
| `HOUSE_OCCUPANT` | Missing | Yes | PURE locally | No | planets/houses | None | No | NOT_CACHE_SAFE | content identity | P0 |
| `FUNCTIONAL_ROLE` | Missing | Yes | IMPURE | Yes | roles/Lagna/config | None | No | NOT_CACHE_SAFE | prepared versioned facts/context | P0 |
| `PLANET_EXALTED` | Missing | Yes | MOSTLY_PURE_WITH_RISK | No | planets/exaltation | None | No | NOT_CACHE_SAFE | canonical capability identity | P0 |

Unsafe cacheable predicate count: **6**.

## 12. Cached-Value Immutability

The cache stores a shallow replaced dataclass, not serialized/logical data. Four mutability risks exist: `inputs`, `evidence`, `errors`, and `trace_steps`, including nested values. Caller-owned references can remain shared; cold-result mutation can corrupt the stored warm result. Retrieval returns the stored object without defensive copying.

## 13. Cache-Hit and Telemetry Behavior

Cold evaluation measures timing and returns `cache_hit=False`; storage changes only `cache_hit=True`; warm retrieval returns the stored timing and true flag without recalculation. Cache telemetry is permanently embedded in the cached value. No hit/miss statistics or separate observation envelope exists.

## 14. Cold/Warm Logical Equivalence

| Result Field | Cold Value Source | Stored Value | Warm Value Source | Expected Difference | Actual Difference | Logical Impact | Snapshot Impact | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|
| matched/ID/inputs/evidence/errors/trace | handler/evaluator | shallow same values | stored object | None | None unless mutation | Nested alias corruption possible | Possible | PARTIAL | P0 |
| `cache_hit` | false | true | stored true | Telemetry only | false vs true | Dataclass equality differs | Direct serialization differs | NONCOMPLIANT | P1 |
| timing | cold measurement | same measurement | stored value | Telemetry policy | warm reuses cold time | Equality includes it across separate cold runs | Nondeterministic | NONCOMPLIANT | P2 |
| version/status/logical hash | absent | absent | absent | Must exist/normalize | Missing | Equivalence unprovable | N/A | MISSING | P1 |

Cold/warm direct difference count: **1 field** (`cache_hit`), but logical equivalence is noncompliant because equality/serialization include it and no logical projection exists.

## 15. Error and Status Caching

| Status | Currently Cached | Key Covers Recovery Dependencies | Sticky-Result Risk | Current Invalidation | Required Decision | Priority |
|---|---|---|---|---|---|---|
| unmatched | Yes | No | High after state/capability change | Global manual clear | lifecycle policy | P0 |
| missing capability | Represented/cached as unmatched | No | Critical after preparation | Yoga-only global clear | typed status/cache policy | P0 |
| invalid parameters | Represented/cached as unmatched/error | No canonical params | High | manual clear | validation/result policy | P0 |
| error/exception | Yes | No config/transient identity | Sticky transient failure | manual clear | error cache policy | P0 |
| timeout | Not representable | No | Future | None | explicit policy | P1 |
| skipped | Not representable | No | Future | None | explicit policy | P1 |

Sticky-result risk categories: **4** current (`unmatched`, missing capability, invalid parameters, errors).

## 16. Invalidation and Lifecycle

Only global `clear_cache()` exists. Yoga clears after capability preparation; tests clear before cases. No automatic invalidation exists for state content, enrichment/version, handler/version, configuration, context, system scope, dynamic registration, or new run outside Yoga. Invalidation-gap count: **8**. Clearing is global/caller-dependent, not per-state/run/request.

## 17. Concurrency and Isolation

Classification: NOT_THREAD_SAFE. Five risks: unlocked global reads/writes, global clear racing evaluations, duplicate computation/check-then-write, dynamic registry/cache mismatch, and cross-request/test retention. Python's GIL does not provide lifecycle/logical isolation. Concurrency-risk count: **5**.

## 18. Memory and Eviction

The cache is unbounded with no eviction, TTL, size control, metrics, or automatic lifecycle. Keys contain dead object IDs without retaining AstroState itself; values can retain large evidence graphs. Entries grow across requests/tests until global clear/process exit, and reused object IDs create theoretical collision risk. This is MEMORY_OR_EVICTION/P2.

## 19. Serialization and Snapshot Impact

The direct predicate serialization test includes `cache_hit` and timing through `asdict`; no canonical projection exists. Production public output does not currently serialize full PredicateResult, but condition/Yoga/artifact migrations can expose differences. Timing and Yoga random trace IDs add separate nondeterminism. No cache entry ID is serialized.

## 20. Existing Tests and Coverage Gaps

One test covers cold result, warm result, and `cache_hit` on the same object (`tests/rules/test_predicate_result.py:14-27`). It does not assert logical equality or isolation.

| Area | Missing Categories | Count | Recommended Location |
|---|---|---:|---|
| Key construction | digest, ID, version, parameter order, alias, defaults, context, enrichment, scope | 9 | `tests/rules/test_predicate_cache_keys.py` |
| Cold/warm | logical/evidence/error/trace/status/hash equivalence | 6 | `tests/rules/test_predicate_cache_equivalence.py` |
| Mutation | evidence/inputs/errors/trace/caller input/state mutation | 6 | `tests/rules/test_predicate_cache_mutation.py` |
| Error/capability | missing, invalid, exception, timeout, transient, post-enrichment | 6 | `tests/rules/test_predicate_cache_failures.py` |
| Lifecycle/concurrency | clear contract, isolation, registration, bounds, parallel, cross-chart | 6 | `tests/rules/test_predicate_cache_lifecycle.py` |

Missing cache-test-category count: **33**.

## 21. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Content-addressed state identity | NONCOMPLIANT | `id(astro)` | engine/state | approved digest | IN_SCOPE | P0 | Yes |
| Predicate version/scope isolation | MISSING | absent | registry/cache | include canonical version/scope | IN_SCOPE | P0 | Yes |
| Canonical validated parameters | NONCOMPLIANT | eight gaps | engine/handlers | pre-key canonicalization | IN_SCOPE | P0 | Yes |
| Evaluation-context isolation | NONCOMPLIANT | role context omitted | engine/role | context identity | IN_SCOPE | P0 | Yes |
| Capability/version isolation | NONCOMPLIANT | all six omitted | engine/enrichments | relevant version identity | IN_SCOPE | P0 | Yes |
| Mutation-safe cached values | NONCOMPLIANT | four mutable fields | result/cache | immutable logical value/copy | IN_SCOPE | P0 | Yes |
| Safe caching by predicate | NONCOMPLIANT | six unsafe | all | metadata/purity/key coverage | IN_SCOPE | P0 | Yes |
| Cold/warm logical equivalence | NONCOMPLIANT | telemetry equality | result/tests | logical projection | IN_SCOPE | P1 | Yes |
| Error/status cache policy | MISSING | every branch cached | engine | explicit status policies | IN_SCOPE | P1 | Yes |
| Automatic lifecycle invalidation | MISSING | global clear only | engine/Yoga | approved scoped lifecycle | IN_SCOPE | P1 | Yes |
| Canonical alias/ID behavior | NONCOMPLIANT | Aspect keys/result mismatch | registry/predicates | canonical alias policy | IN_SCOPE | P1 | Yes |
| Bounded cache/eviction | MISSING | unbounded dict | engine | approved bounds later | IN_SCOPE | P1 | No |
| Concurrency/request isolation | NONCOMPLIANT | unlocked global | engine | isolation/thread policy | IN_SCOPE | P1 | Yes |
| Cache contract tests | MISSING | 33 gaps | tests | focused suites | IN_SCOPE | P1 | Yes |
| Telemetry separated from logic | NONCOMPLIANT | hit/timing in equality | result/cache | observation envelope/policy | IN_SCOPE | P2 | No |
| Legacy/Yoga compatibility | PARTIAL | global clear/caller dependence | Yoga/callers | explicit adapters | TEMPORARY_COMPATIBILITY | P2 | No |
| Memory observability | MISSING | no metrics | engine | later operational policy | OUT_OF_SCOPE_FUTURE_STAGE | P2 | No |
| Persistent/distributed cache policy | UNKNOWN | none exists | future | decide only if introduced | OUT_OF_SCOPE_FUTURE_STAGE | P3 | No |

## 22. Migration Risks and Priorities

The 18 findings total **P0=7, P1=7, P2=3, P3=1**. Key/value/lifecycle changes touch every predicate and the Yoga caller. Migration must preserve valid cold/warm factual results while excluding telemetry from logical identity and must not cache recovery-dependent false/error states under incomplete keys.

## 23. Unresolved Architectural Questions

1. What approved AstroState/core-capability digest composition identifies facts?
2. Which evaluation-context fields enter identity?
3. Which statuses/errors are cacheable and for how long?
4. Is the cache per evaluation run, engine instance, request, or shared process?
5. How are alias IDs and handler upgrades invalidated?
6. What bounded eviction/concurrency policy is required?
7. Is telemetry returned via a separate envelope or excluded from equality/serialization?

Questions 1–5 block safe implementation.

## 24. Audit-11 Conclusion

Audit-11 is complete. All prerequisites were present; no correction was implemented and Audit-12 was not started.

### Summary counts

| Metric | Count |
|---|---:|
| Predicate-related caches | 1 |
| Active production caches | 1 |
| Cache-key construction paths | 1 |
| Process-identity key dependencies | 1 |
| Missing predicate-version key components | 6 |
| Missing context key components | 1 |
| Missing capability/enrichment-version components | 6 |
| Parameter-canonicalization gaps | 8 |
| Cached-value mutability risks | 4 |
| Cold/warm logical differences | 1 |
| Sticky error/missing-capability risks | 4 |
| Unsafe cacheable predicates | 6 |
| Invalidation gaps | 8 |
| Concurrency risks | 5 |
| Cache test gaps | 33 |
| P0 findings | 7 |
| P1 findings | 7 |
| P2 findings | 3 |
| P3 findings | 1 |

The only modified file is this report.
