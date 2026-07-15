# Prompt-01 — Audit-11: Predicate Cache Audit

You are auditing the Jyothishyam repository before implementing Prompt-01.

## 1. Authoritative material

Read these authoritative documents first:

1. Jyothishyam Master Architecture Specification v1.0
2. Prompt-01

Locate them by filename if necessary.

Then read the completed audit reports from:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/`

Expected reports:

- `Audit-01-Predicate-Registry.md`
- `Audit-02-Complete-Predicate-Inventory.md`
- `Audit-03-Legacy-Return-Contracts.md`
- `Audit-04-Complete-Caller-Inventory.md`
- `Audit-05-PredicateResult-Model.md`
- `Audit-06-Supporting-Models.md`
- `Audit-07-Parameter-Validation.md`
- `Audit-08-Capability-Handling.md`
- `Audit-09-AstroState-Boundary.md`
- `Audit-10-Predicate-Purity.md`

If an expected report is missing:

- record it as a limitation;
- continue if Audit-11 can still be completed reliably;
- do not recreate or modify it;
- return `BLOCKED` only if the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-11: Predicate Cache Audit**.

Determine whether the predicate cache is:

- deterministic;
- version-safe;
- content-addressed;
- isolated by canonical parameters;
- isolated by evaluation context;
- isolated by relevant capabilities and enrichment versions;
- protected from caller mutation;
- logically equivalent between cold and warm evaluation;
- safe for concurrent and repeated use.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Required cache contract

Prompt-01 requires a cache identity conceptually based on:

```text
AstroState content digest
+ predicate ID
+ predicate version
+ canonical parameters
+ relevant evaluation-context identity
+ relevant capability/enrichment versions
+ system or plugin scope where applicable
```

A cache key must not depend on:

- process memory address;
- `id(astro)`;
- unstable Python hashes;
- random UUIDs;
- dictionary insertion order;
- mutable caller-owned values;
- implicit system time;
- cache warmth;
- performance telemetry.

Cold and warm evaluation must produce logically equivalent results.

Retrieval telemetry such as `cache_hit=True` must not change the underlying logical result identity.

Use Prompt-01 as authoritative if its exact requirements differ.

## 4. Repository-wide discovery

Search the complete repository for:

- predicate caches;
- condition caches;
- rule caches;
- Yoga caches;
- memoization decorators;
- LRU caches;
- module-level cache dictionaries;
- cache-key classes;
- digest functions;
- canonical parameter serialization;
- cache clearing;
- cache statistics;
- cache-hit fields;
- cache invalidation;
- test fixtures that reset caches;
- direct cache access by callers.

Search for patterns such as:

```python
cache
_cache
CACHE
lru_cache
functools.cache
memoize
id(astro)
hash(astro)
json.dumps(params)
cache_hit
clear_cache
cache.clear()
dict.setdefault(...)
```

Inspect context before classifying a cache as predicate-related.

## 5. Cache implementation inventory

Identify every cache that can affect predicate or condition evaluation.

For each cache, report:

1. File and symbol.
2. Cache owner.
3. Storage type.
4. Scope:
   - process;
   - module;
   - engine instance;
   - evaluation run;
   - thread;
   - request;
   - test.
5. Key type and exact components.
6. Value type.
7. Read path.
8. Write path.
9. Clear or invalidation path.
10. Size limit.
11. Eviction policy.
12. Lifetime.
13. Thread-safety.
14. Mutation protection.
15. Telemetry.
16. Production or test-only status.
17. Existing tests.

Identify the canonical predicate cache and any parallel or duplicate caches.

## 6. Cache-key construction audit

Inspect every predicate cache-key construction path.

For each key component, determine:

- where it comes from;
- whether it is deterministic;
- whether it is canonical;
- whether it is immutable;
- whether it is versioned;
- whether logically equivalent inputs produce the same value;
- whether logically different inputs can collide.

Pay particular attention to keys shaped like:

```python
(id(astro), predicate_name, params_json)
```

Assess whether the key includes:

- AstroState digest;
- predicate ID;
- predicate version;
- canonical parameters;
- evaluation-context digest;
- evaluation instant for time-dependent predicates;
- normalization version;
- enrichment versions;
- capability versions;
- system or plugin scope.

Do not design or implement a replacement key.

## 7. AstroState identity audit

Determine whether the cache uses:

- `id(astro)`;
- object identity;
- object hash;
- chart ID;
- serialized AstroState;
- stable content digest;
- partial content digest.

Assess these scenarios:

1. Same AstroState content in two different objects.
2. Different AstroState content in the same mutable object.
3. AstroState mutated after a cache entry is written.
4. Enrichment added after an unmatched result is cached.
5. Equivalent state reconstructed in another process.
6. Same core chart with different enrichment versions.

For each scenario, report current behavior, expected behavior and risk.

Reconcile with Audit-9.

## 8. Predicate identity and version isolation

Determine whether cache keys include:

- canonical predicate ID;
- aliases after normalization;
- predicate version;
- handler version;
- system/plugin scope;
- deprecation or replacement identity where relevant.

Assess whether:

- two versions of the same predicate can collide;
- aliases create duplicate cache entries;
- handler replacement leaves stale results;
- test-time dynamic registration reuses existing entries;
- duplicate registrations affect cache correctness;
- import order changes the resolved handler without invalidating cache entries.

Reconcile with Audit-1.

## 9. Parameter canonicalization

Determine how parameters are represented in cache keys.

Audit handling of:

- dictionary insertion order;
- lists and tuples;
- sets and frozensets;
- enums;
- dataclasses;
- Pydantic models;
- integers and floats;
- numeric strings;
- booleans;
- `None`;
- dates and datetimes;
- UUIDs;
- custom objects;
- non-string dictionary keys;
- unsupported or cyclic structures.

Assess logically equivalent examples such as:

```json
{"planet": "Mars", "house": 7}
```

and:

```json
{"house": 7, "planet": "Mars"}
```

Also assess:

```json
{"house": 7}
```

versus:

```json
{"house": "7"}
```

and:

- omitted default versus explicit default;
- alias versus canonical parameter name;
- unknown but unused parameter versus omitted parameter.

Determine whether validation and normalization occur before key construction.

Reconcile with Audit-7.

## 10. Evaluation-context isolation

Identify every evaluation-context value that can affect predicate output, including:

- evaluation instant;
- timezone;
- Ayanamsa;
- transit date;
- Dasha reference date;
- locale, if logically relevant;
- normalization version;
- system version;
- plugin version;
- feature configuration.

For each value, report:

1. Source.
2. Predicates affected.
3. Whether it is explicit or implicit.
4. Whether it appears in the key.
5. Whether it defaults to system time.
6. Whether omission and explicit default are equivalent.
7. Collision or stale-result risk.
8. Existing tests.

A time-dependent predicate must not reuse an entry created for a different evaluation instant.

## 11. Capability and enrichment isolation

Determine whether the cache accounts for predicate-required capabilities and enrichment versions.

Assess:

- capability present versus absent;
- capability `None` versus empty;
- missing AspectGraph versus empty AspectGraph;
- enrichment added after initial evaluation;
- enrichment version changes;
- partial versus complete enrichment;
- functional-role recalculation;
- varga recalculation;
- strength data changes;
- system-specific capability differences.

Determine whether a cached unmatched result can remain after the required capability becomes available.

Determine whether missing-capability results are cached and whether that is safe within the current lifecycle.

Reconcile with Audit-8.

## 12. Cacheability metadata and purity

Compare the registry’s `cacheable` and `deterministic` metadata with actual behavior.

For every registered predicate, report:

- declared cacheability;
- actual cache usage;
- purity classification from Audit-10;
- implicit dependencies;
- context requirements;
- relevant versions;
- whether current cache key covers those dependencies;
- final cache-safety classification.

Use:

- `CACHE_SAFE`
- `CACHE_SAFE_WITH_CONTEXT`
- `NOT_CACHE_SAFE`
- `CACHE_SAFETY_UNKNOWN`
- `NOT_CACHED`

Identify predicates that are cached despite being impure or context-dependent.

## 13. Cache value and immutability audit

Determine what the cache stores:

- the original `PredicateResult`;
- a modified copy;
- a tuple;
- a dictionary;
- serialized data;
- logical result without telemetry;
- result with `cache_hit=True`.

Assess whether:

- cached values are deeply immutable;
- caller mutation can corrupt future hits;
- caller-owned evidence remains shared;
- errors or trace steps remain mutable;
- cached results are defensively copied;
- retrieval changes the cached object;
- cache telemetry is embedded permanently;
- nested mutable values survive copying.

Reconcile with Audits 5 and 6.

## 14. Cache-hit behavior

Inspect cold and warm evaluation behavior.

Determine:

1. What the cold call returns.
2. What is stored.
3. What the warm call returns.
4. How `cache_hit` is set.
5. Whether timing is recalculated.
6. Whether evidence differs.
7. Whether errors differ.
8. Whether trace steps differ.
9. Whether status differs.
10. Whether equality differs.
11. Whether serialization differs.
12. Whether logical hashes differ.

Pay particular attention to behavior where the initially stored copy permanently contains:

```python
cache_hit=True
```

Determine whether cache telemetry contaminates logical identity, snapshots or downstream behavior.

## 15. Logical equivalence audit

Cold and warm results may differ in retrieval telemetry but must remain logically equivalent.

Assess equivalence of:

- `predicate_id`;
- `predicate_version`;
- `status`;
- `matched`;
- canonical inputs;
- evidence;
- errors;
- logical trace content;
- logical hash or normalized representation.

Determine whether downstream callers treat `cache_hit` or timing as logical evidence.

Identify any caller whose behavior changes between cold and warm evaluation.

## 16. Error and status caching

Determine whether the cache stores results with:

- `unmatched`;
- `missing_capability`;
- `invalid_parameters`;
- `error`;
- `timeout`;
- `skipped`.

For each status, determine:

- whether caching occurs;
- whether it is intentional;
- whether the key includes all recovery dependencies;
- whether a transient failure becomes sticky;
- whether a timeout result becomes sticky;
- whether invalid parameters can poison later valid calls;
- whether missing capability remains cached after preparation;
- whether exceptions leave partial cache entries.

Do not decide a final caching policy unless Prompt-01 specifies it. Record unresolved policies.

## 17. Invalidation and lifecycle

Identify all cache invalidation mechanisms.

Report whether invalidation occurs when:

- AstroState content changes;
- enrichments change;
- predicate version changes;
- registry handlers change;
- configuration changes;
- evaluation context changes;
- system/plugin version changes;
- tests register predicates;
- Yoga mutates AstroState;
- a new evaluation run starts.

Determine whether cache clearing is:

- explicit;
- automatic;
- caller-dependent;
- global;
- per-state;
- per-run;
- absent.

Pay particular attention to Yoga or other callers clearing a global predicate cache.

## 18. Concurrency and isolation

Assess:

- thread-safety;
- parallel chart evaluation;
- parallel predicate evaluation;
- global cache sharing;
- race conditions;
- partial writes;
- duplicate computation;
- cross-test leakage;
- cross-chart contamination;
- user/request isolation.

Do not run unsafe stress tests.

Classify each cache as:

- `THREAD_SAFE`
- `PROBABLY_THREAD_SAFE`
- `NOT_THREAD_SAFE`
- `UNKNOWN`

## 19. Memory and eviction behavior

Report, without performance redesign:

- whether cache size is bounded;
- eviction policy;
- whether entries retain large AstroState-derived evidence;
- whether object identity keys retain stale entries;
- whether cache grows across requests or test runs;
- whether clear operations exist;
- whether cache metrics exist.

Classify memory risks separately from logical-correctness risks.

## 20. Serialization and snapshot impact

Determine whether cache-related fields appear in:

- predicate serialization;
- evidence;
- trace output;
- logs;
- debug output;
- golden snapshots;
- public JSON.

Assess whether these fields create nondeterministic differences:

- `cache_hit`;
- `evaluation_time_ms`;
- cache entry IDs;
- timestamps;
- random trace IDs.

Do not update snapshots.

## 21. Test inventory and gap analysis

Locate tests covering:

### Key construction

- AstroState digest isolation;
- predicate-ID isolation;
- predicate-version isolation;
- parameter-order normalization;
- alias normalization;
- default normalization;
- evaluation-context isolation;
- enrichment-version isolation;
- system/plugin-scope isolation.

### Cold and warm behavior

- cold result;
- warm result;
- `cache_hit`;
- logical equivalence;
- evidence equivalence;
- error equivalence;
- trace equivalence;
- status equivalence;
- logical-hash equivalence.

### Mutation protection

- caller cannot mutate cached evidence;
- caller cannot mutate cached inputs;
- caller cannot mutate cached errors;
- caller cannot mutate cached trace steps;
- caller-owned input mutation does not corrupt keys;
- AstroState mutation cannot create stale hits.

### Error and capability results

- missing capability;
- invalid parameters;
- predicate exception;
- timeout;
- no sticky transient failure;
- enrichment added after initial evaluation.

### Lifecycle and concurrency

- cache clear;
- test isolation;
- dynamic registration isolation;
- bounded-size behavior;
- parallel access;
- no cross-chart contamination.

For each missing test category:

- identify the gap;
- explain the risk;
- recommend the likely test file;
- do not create the test.

## 22. Required classifications

Classify cache-key components as:

- `DETERMINISTIC_AND_CANONICAL`
- `DETERMINISTIC_BUT_NONCANONICAL`
- `PROCESS_LOCAL`
- `MUTABLE`
- `INCOMPLETE`
- `NONDETERMINISTIC`
- `UNKNOWN`

Classify cache findings as:

- `LOGICAL_CORRECTNESS`
- `VERSION_ISOLATION`
- `CONTEXT_ISOLATION`
- `MUTATION_SAFETY`
- `CONCURRENCY`
- `MEMORY_OR_EVICTION`
- `TELEMETRY_ONLY`
- `UNKNOWN`

Classify each Prompt-01 requirement as:

- `IMPLEMENTED`
- `PARTIAL`
- `MISSING`
- `NONCOMPLIANT`
- `UNKNOWN`

Use priorities:

- `P0` — Blocks safe Prompt-01 implementation
- `P1` — Required for Prompt-01 completion
- `P2` — Important compatibility or quality concern
- `P3` — Later-stage or nonblocking concern

Use scope classifications:

- `IN_SCOPE`
- `TEMPORARY_COMPATIBILITY`
- `OUT_OF_SCOPE_FUTURE_STAGE`
- `UNRELATED`

## 23. Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- symbol name;
- line number or small range when practical;
- cache name;
- exact key or value behavior;
- affected predicates or callers;
- active-path evidence;
- existing tests;
- logical or telemetry impact;
- uncertainty where static analysis cannot prove runtime behavior.

Reconcile findings with Audits 1–10.

Explain:

- registry metadata dependencies from Audit-1;
- predicate and caller dependencies from Audits 2–4;
- result immutability and telemetry concerns from Audits 5–6;
- canonical parameter dependencies from Audit-7;
- capability/version dependencies from Audit-8;
- AstroState digest and identity findings from Audit-9;
- purity and cache-safety findings from Audit-10.

Do not modify previous reports.

## 24. Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify rules;
- modify previous audit reports;
- replace cache keys;
- add a digest;
- change cache values;
- change invalidation;
- clear or warm caches as a persistent action;
- add locks;
- change predicate metadata;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-12.

You may run safe, non-mutating searches and isolated tests.

Do not execute commands that update files, snapshots or generated artifacts.

## 25. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-11-Predicate-Cache.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker instead of selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-11: Predicate Cache

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–10
## 4. Cache Implementation Inventory
## 5. Cache-Key Construction
## 6. AstroState Identity and Digest
## 7. Predicate Identity and Version Isolation
## 8. Parameter Canonicalization
## 9. Evaluation-Context Isolation
## 10. Capability and Enrichment Isolation
## 11. Predicate Cacheability and Purity
## 12. Cached-Value Immutability
## 13. Cache-Hit and Telemetry Behavior
## 14. Cold/Warm Logical Equivalence
## 15. Error and Status Caching
## 16. Invalidation and Lifecycle
## 17. Concurrency and Isolation
## 18. Memory and Eviction
## 19. Serialization and Snapshot Impact
## 20. Existing Tests and Coverage Gaps
## 21. Prompt-01 Compliance Matrix
## 22. Migration Risks and Priorities
## 23. Unresolved Architectural Questions
## 24. Audit-11 Conclusion
```

### Cache implementation inventory

Include these columns:

| Cache | File | Symbol | Owner | Scope | Storage | Key Type | Value Type | Lifetime | Eviction | Clear Path | Thread-Safe | Production Use | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Cache-key component matrix

Include these columns:

| Cache | Key Component | Current Source | Included | Canonical | Deterministic | Versioned | Mutable | Collision/Staleness Risk | Required Change | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Predicate cache-safety matrix

Include these columns:

| Predicate ID | Declared Cacheable | Actually Cached | Purity | Context Dependency | Capability Dependency | Version Coverage | Current Key Safe | Classification | Required Action | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Cold/warm equivalence matrix

Include these columns:

| Result Field | Cold Value Source | Stored Value | Warm Value Source | Expected Difference | Actual Difference | Logical Impact | Snapshot Impact | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|

### Error and status caching matrix

Include these columns:

| Status | Currently Cached | Key Covers Recovery Dependencies | Sticky-Result Risk | Current Invalidation | Required Decision | Priority |
|---|---|---|---|---|---|---|

### Compliance matrix

Include these columns:

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- predicate-related caches;
- active production caches;
- cache-key construction paths;
- process-identity key dependencies;
- missing predicate-version key components;
- missing context key components;
- missing capability/enrichment-version components;
- parameter-canonicalization gaps;
- cached-value mutability risks;
- cold/warm logical differences;
- sticky error or missing-capability risks;
- unsafe cacheable predicates;
- invalidation gaps;
- concurrency risks;
- cache test gaps;
- P0, P1, P2 and P3 findings.

## 26. Final response

After creating the report, stop.

Respond with only:

1. Audit-11 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Predicate-related cache count
6. Process-identity key-dependency count
7. Missing version/context/capability key-component counts
8. Parameter-canonicalization gap count
9. Cached-value mutability-risk count
10. Cold/warm logical-difference count
11. Sticky-result risk count
12. Unsafe-cacheable-predicate count
13. Invalidation and concurrency risk counts
14. Missing cache-test-category count
15. Number of P0, P1, P2 and P3 findings
16. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-12.
