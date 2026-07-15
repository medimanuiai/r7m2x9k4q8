# Prompt-01 — Audit-21: Determinism Audit

You are auditing the Jyothishyam repository before implementing Prompt-01.

## 1. Authoritative material

Read these authoritative documents first:

1. Jyothishyam Master Architecture Specification v1.0
2. Prompt-01

Locate them by filename if necessary.

Then read the completed reports from:

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
- `Audit-11-Predicate-Cache.md`
- `Audit-12-Condition-Evaluator.md`
- `Audit-13-Condition-Format-Inventory.md`
- `Audit-14-Rule-Loader-Compiler-Interaction.md`
- `Audit-15-Yoga-Engine.md`
- `Audit-16-Domain-Runtime.md`
- `Audit-17-Error-Handling.md`
- `Audit-18-Evidence.md`
- `Audit-19-Trace.md`
- `Audit-20-Serialization-Public-Output.md`

If an expected report is missing:

- record it as a limitation;
- continue if Audit-21 can still be completed reliably;
- do not recreate or modify it;
- return `BLOCKED` only when the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-21: Determinism Audit**.

Identify every source of nondeterminism that can affect predicates or predicate-derived output, including:

- logical result;
- status;
- evidence;
- errors;
- traces;
- cache identity;
- condition aggregation;
- Yoga matches;
- domain scores;
- serialization;
- snapshots;
- public output.

Determine whether identical logical inputs and versioned context produce identical logical results across:

- repeated evaluations;
- cold and warm cache runs;
- equivalent AstroState instances;
- different evaluation orders;
- separate processes where relevant;
- different test execution orders;
- serial and parallel evaluation where supported.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Determinism contract

Prompt-01 requires deterministic logical predicate behavior.

Conceptually:

```text
Same AstroState content and versions
+ same predicate ID and version
+ same canonical parameters
+ same explicit evaluation context
+ same relevant capability/enrichment versions
= same logical PredicateResult
```

Runtime telemetry may legitimately vary, but it must be separated from logical identity.

Logical fields generally include:

- predicate ID;
- predicate version;
- status;
- matched outcome;
- canonical inputs;
- factual evidence;
- typed error identity and stable details;
- deterministic logical trace content where required.

Variable telemetry may include:

- elapsed time;
- performance counters;
- cache-hit state;
- diagnostic timestamps, if explicitly classified.

Use Prompt-01 as authoritative if its exact boundary differs.

## 4. Repository-wide discovery

Search production code, tests, fixtures, predicates, registry, cache, condition evaluation, Yoga, domains, inference, serialization, snapshots and documentation.

Search for:

```text
datetime.now
datetime.utcnow
date.today
time.time
perf_counter
monotonic
uuid.uuid4
random
secrets
id(
hash(
set(
frozenset
os.environ
os.getenv
glob
rglob
iterdir
listdir
cache_hit
evaluation_time_ms
trace_id
```

Also inspect:

- dictionary and registry iteration;
- mutable module-level state;
- lazy initialization;
- global caches;
- test-time registration;
- filesystem traversal;
- parallel execution;
- exception message content;
- JSON serialization ordering;
- floating-point calculations;
- locale and timezone dependencies.

Treat matches as candidates. Inspect whether they affect predicate-related logical or telemetry output.

## 5. Nondeterminism-source inventory

For every candidate source, report:

1. File and symbol.
2. Line number or small line range.
3. Architectural layer.
4. Source of nondeterminism.
5. Trigger and inputs.
6. Fields or behavior affected.
7. Logical or telemetry classification.
8. Reproducibility scope.
9. Cache impact.
10. Snapshot/public-output impact.
11. Active-path evidence.
12. Existing controls or normalization.
13. Existing tests.
14. Scope and priority.

Classify each source as:

- `LOGICAL_NONDETERMINISM`
- `EVIDENCE_NONDETERMINISM`
- `ERROR_NONDETERMINISM`
- `TRACE_ONLY_NONDETERMINISM`
- `CACHE_NONDETERMINISM`
- `SERIALIZATION_NONDETERMINISM`
- `PERFORMANCE_ONLY_NONDETERMINISM`
- `UNRELATED`
- `UNKNOWN`

## 6. System-time dependency

Find every predicate-related use of current time or date.

For each, determine:

- whether time affects logical evaluation;
- whether it is supplied explicitly in evaluation context;
- whether a default reads the system clock;
- timezone source;
- cache-key inclusion;
- evidence or trace inclusion;
- snapshot impact;
- test injection or freezing.

Pay special attention to:

- transit evaluation dates;
- Dasha reference dates;
- “today” defaults;
- timestamps used as identities;
- cache expiration;
- trace timestamps.

Classify time use as:

- `EXPLICIT_VERSIONED_CONTEXT`
- `IMPLICIT_LOGICAL_TIME`
- `TRACE_TELEMETRY_TIME`
- `PERFORMANCE_TIMING`
- `UNRELATED`

## 7. Randomness and UUIDs

Find all predicate-related random-number, token and UUID generation.

Determine whether random values affect:

- logical result;
- evidence;
- errors;
- trace IDs;
- rule or Yoga identities;
- cache keys;
- serialization;
- snapshots;
- logs only.

Identify whether deterministic IDs or normalization already exist.

Do not implement a new ID algorithm.

## 8. Process identity and unstable hashes

Find all predicate-related use of:

- `id(object)`;
- default object hash;
- Python runtime string hash;
- memory address representations;
- object `repr` containing addresses;
- process IDs;
- thread IDs.

Pay special attention to predicate cache keys using `id(astro)`.

Determine whether identity remains stable across:

- repeated calls in one process;
- mutation of the same object;
- equivalent objects;
- separate processes.

Reconcile with Audits 9 and 11.

## 9. Collection ordering

Audit output-affecting iteration over:

- sets and frozensets;
- dictionaries where construction order varies;
- predicate registries;
- error collections;
- evidence mappings;
- trace collections;
- rule files;
- Yoga matches;
- domain indicators;
- filesystem results.

Determine whether order is:

- semantically defined;
- insertion based and stable;
- explicitly sorted;
- derived from unstable input;
- nondeterministic;
- irrelevant because normalized before output.

Do not sort semantic evaluation sequences merely to obtain alphabetic output. Record the required semantic order.

## 10. Filesystem and import ordering

Find predicate-related behavior dependent on:

- `glob` or recursive glob order;
- `os.listdir`;
- directory iteration;
- module discovery;
- registry import order;
- rule-file load order;
- plugin discovery;
- duplicate registration order.

Determine whether different order changes:

- available predicates;
- duplicate winners;
- validation results;
- rule order;
- Yoga order;
- evidence/error order;
- serialization.

Reconcile with Audits 1, 13 and 14.

## 11. Mutable global state and test order

Inventory predicate-related mutable globals, including:

- registries;
- caches;
- counters;
- configuration tables;
- lazy-loaded state;
- singleton engines;
- trace collectors;
- test registrations.

Determine whether results depend on:

- which test ran first;
- whether a registry was previously modified;
- whether a cache was warmed;
- whether a global was reset;
- whether configuration was loaded earlier;
- whether Yoga or a domain ran first.

Identify isolation and reset mechanisms.

## 12. AstroState mutation and lifecycle

Determine whether predicate results depend on:

- AstroState mutation;
- enrichment added during evaluation;
- Yoga mutation;
- domain mutation;
- digest calculation before versus after mutation;
- reuse of a partially prepared state;
- evaluation order.

Reconcile with Audits 8–10.

## 13. Predicate-by-predicate determinism

For every registered predicate, assess:

1. Predicate ID and version.
2. Inputs and capabilities.
3. Global dependencies.
4. Time dependency.
5. Randomness.
6. I/O dependency.
7. Mutable state dependency.
8. Collection-order dependency.
9. Floating-point dependency.
10. Cache dependency.
11. Trace/telemetry variability.
12. Existing determinism tests.
13. Final classification.

Use:

- `DETERMINISTIC`
- `DETERMINISTIC_WITH_EXPLICIT_CONTEXT`
- `LOGICALLY_DETERMINISTIC_TELEMETRY_VARIES`
- `NONDETERMINISTIC`
- `UNKNOWN`

## 14. Parameter canonicalization

Determine whether logically equivalent parameters produce identical logical results and identities.

Audit:

- mapping insertion order;
- aliases;
- case normalization;
- explicit versus omitted defaults;
- list versus tuple;
- set ordering;
- numeric strings versus numbers;
- floats and decimal values;
- NaN and infinity;
- dates and datetimes;
- custom objects.

Reconcile with Audits 7 and 11.

## 15. Floating-point determinism

Identify predicate-related floating-point calculations and comparisons.

Determine whether behavior depends on:

- platform math;
- rounding mode;
- tolerance;
- order of summation;
- NaN;
- infinity;
- serialization precision;
- different calculation paths.

Keep this focused on Prompt-01 predicates and predicate-derived output. Do not broaden into a complete astrology calculation audit.

## 16. Error determinism

Determine whether identical failures produce stable:

- status;
- error code;
- safe message;
- structured details;
- error ordering.

Identify variability caused by:

- raw exception messages;
- filesystem paths;
- memory addresses;
- library/version-specific text;
- timestamps;
- stack traces;
- parallel aggregation.

Reconcile with Audit-17.

## 17. Evidence determinism

Determine whether equivalent evaluations produce equivalent factual evidence.

Audit:

- mapping order;
- collection order;
- object representations;
- mutable values;
- raw provider fields;
- floating-point precision;
- cache warmth;
- evaluation order.

Reconcile with Audit-18.

## 18. Trace determinism

Determine whether trace identity, content and ordering remain stable where required.

Audit:

- UUIDs;
- timestamps;
- durations;
- step ordering;
- parent-child identity;
- cache-hit differences;
- skipped branches;
- parallel execution.

Separate logical trace content from telemetry.

Reconcile with Audit-19.

## 19. Cache-state determinism

Compare cold and warm evaluation for:

- matched outcome;
- status;
- canonical inputs;
- evidence;
- errors;
- logical trace;
- serialization;
- Yoga and domain consumers.

Determine whether cache state changes any logical field.

Also assess:

- cache clearing;
- stale cache after enrichment;
- global cache leakage;
- concurrency;
- cached transient failures.

Reconcile with Audit-11.

## 20. Condition-evaluation determinism

Determine whether logical condition results depend on:

- child order;
- short-circuit behavior;
- all-child evaluation;
- error aggregation order;
- skipped-branch representation;
- cache state;
- alternate evaluator selection.

The source condition order may be semantically meaningful. Preserve it in the assessment.

Reconcile with Audit-12.

## 21. Yoga and domain determinism

Determine whether identical inputs produce identical:

- Yoga match sets and ordering;
- Yoga evidence and traces;
- domain indicator order;
- domain scores and confidence;
- domain evidence;
- output order.

Audit dependencies on:

- rule-file order;
- dictionaries or sets;
- UUIDs;
- AstroState mutation;
- cache warmth;
- system time;
- partial failures.

Reconcile with Audits 15 and 16.

## 22. Serialization and snapshot determinism

Determine whether identical logical results produce identical serialized structures and snapshot content.

Audit:

- key ordering;
- list ordering;
- enum serialization;
- tuple/list normalization;
- random IDs;
- timestamps;
- timing fields;
- cache-hit telemetry;
- object `repr`;
- non-JSON-safe fallbacks.

Reconcile with Audit-20.

## 23. Parallel and concurrent execution

Assess whether predicate-related output can vary under concurrent execution due to:

- shared mutable registry;
- shared cache;
- non-atomic writes;
- global counters;
- shared AstroState mutation;
- unordered completion;
- error and trace aggregation order.

Do not run unsafe concurrency or stress tests.

Classify concurrency behavior as:

- `DETERMINISTIC_AND_SAFE`
- `LIKELY_SAFE_NOT_PROVEN`
- `ORDER_DEPENDENT`
- `RACE_RISK`
- `UNSUPPORTED`
- `UNKNOWN`

## 24. Repeatability test strategy audit

Locate current tests or utilities that repeat evaluations and compare outputs.

Determine whether they normalize only permitted telemetry or accidentally hide logical differences.

Identify support for:

- same object, repeated evaluation;
- equivalent separate objects;
- cold and warm cache;
- different parameter insertion order;
- different registry/rule load order;
- subprocess repeatability;
- different test order;
- parallel evaluation;
- snapshot comparison.

Do not create tests.

## 25. Test inventory and gap analysis

Locate tests covering:

### Predicate repeatability

- repeated identical evaluation;
- equivalent AstroState instances;
- explicit context time;
- no implicit system time;
- no randomness;
- stable error and evidence.

### Ordering

- parameter mappings;
- registries;
- rule files;
- errors;
- traces;
- Yoga matches;
- domain indicators.

### Cache

- cold/warm logical equivalence;
- stale cache prevention;
- transient error behavior;
- enrichment-version isolation.

### Serialization

- repeated canonical serialization;
- telemetry separation;
- snapshot stability;
- cross-process stability where required.

### Lifecycle and concurrency

- test-order independence;
- registry reset;
- cache reset;
- no AstroState mutation dependence;
- serial versus parallel equivalence where supported.

For every missing test category:

- identify the gap;
- explain its risk;
- recommend the likely test file;
- do not create the test.

## 26. Required classifications

Classify nondeterminism impact as:

- `LOGICAL`
- `EVIDENCE`
- `ERROR`
- `TRACE_ONLY`
- `CACHE_ONLY`
- `SERIALIZATION_OR_SNAPSHOT`
- `PERFORMANCE_ONLY`
- `UNRELATED`

Classify every Prompt-01 requirement as:

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

## 27. Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- symbol name;
- line number or small range when practical;
- nondeterminism source;
- affected fields and layers;
- logical versus telemetry classification;
- active-path evidence;
- existing normalization or controls;
- existing tests;
- uncertainty where static analysis cannot prove runtime behavior.

Reconcile findings with Audits 1–20 without modifying earlier reports.

## 28. Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify rules;
- modify previous audit reports;
- replace IDs;
- inject clocks;
- change cache keys;
- sort evaluation order;
- freeze global state;
- change serialization;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-22.

You may run safe, non-mutating searches and isolated tests.

Do not execute commands that update files, snapshots or generated artifacts.

## 29. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-21-Determinism.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker rather than selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-21: Determinism

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–20
## 4. Determinism Contract
## 5. Complete Nondeterminism-Source Inventory
## 6. System-Time Dependencies
## 7. Randomness and UUIDs
## 8. Process Identity and Unstable Hashes
## 9. Collection, Filesystem and Import Ordering
## 10. Mutable Global State and Test Order
## 11. AstroState Lifecycle and Mutation
## 12. Predicate-by-Predicate Determinism
## 13. Parameter Canonicalization
## 14. Floating-Point Determinism
## 15. Error, Evidence and Trace Determinism
## 16. Cache-State Determinism
## 17. Condition-Evaluation Determinism
## 18. Yoga and Domain Determinism
## 19. Serialization and Snapshot Determinism
## 20. Parallel and Concurrent Execution
## 21. Repeatability Testing Assessment
## 22. Existing Tests and Coverage Gaps
## 23. Prompt-01 Compliance Matrix
## 24. Migration Risks and Priorities
## 25. Unresolved Architectural Questions
## 26. Audit-21 Conclusion
```

### Nondeterminism-source inventory

| File | Symbol | Layer | Source | Trigger | Fields Affected | Impact Classification | Repeatability Scope | Cache Impact | Snapshot/Public Impact | Existing Control | Active Path | Tests | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Predicate determinism matrix

| Predicate ID | Version | Time | Randomness | I/O | Mutable State | Collection Order | Float Risk | Cache Dependency | Trace Variability | Classification | Evidence | Tests | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Ordering inventory

| File | Symbol | Collection/Source | Semantic Order | Current Order | Stable | Normalized | Fields Affected | Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|

### Cold/warm and repeated-run matrix

| Evaluation Scenario | Matched | Status | Inputs | Evidence | Errors | Logical Trace | Serialization | Expected Difference | Actual Difference | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|

### Compliance matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- nondeterminism sources;
- logical nondeterminism paths;
- evidence nondeterminism paths;
- error nondeterminism paths;
- trace-only nondeterminism paths;
- cache nondeterminism paths;
- serialization/snapshot nondeterminism paths;
- performance-only variability paths;
- implicit system-time dependencies;
- random or UUID dependencies;
- process-identity dependencies;
- unstable collection-order paths;
- filesystem/import-order dependencies;
- mutable-global/test-order dependencies;
- AstroState lifecycle dependencies;
- deterministic predicates;
- explicit-context deterministic predicates;
- telemetry-only variable predicates;
- nondeterministic predicates;
- predicates with unknown determinism;
- cold/warm logical differences;
- Yoga/domain determinism risks;
- concurrency race or ordering risks;
- missing determinism test categories;
- P0, P1, P2 and P3 findings.

## 30. Final response

After creating the report, stop.

Respond with only:

1. Audit-21 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Nondeterminism-source counts by impact classification
6. Implicit-time, randomness/UUID and process-identity counts
7. Collection-order, filesystem/import-order and mutable-global counts
8. Deterministic, context-deterministic, telemetry-variable, nondeterministic and unknown predicate counts
9. Cold/warm logical-difference count
10. Yoga/domain determinism-risk count
11. Concurrency risk count
12. Serialization/snapshot nondeterminism count
13. Missing test-category count
14. Number of P0, P1, P2 and P3 findings
15. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-22.