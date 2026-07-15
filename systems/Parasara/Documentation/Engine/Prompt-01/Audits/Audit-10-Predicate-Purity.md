# Prompt-01 — Audit-10: Predicate Purity Audit

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

If an expected report is missing:

- record it as a limitation;
- continue if Audit-10 can still be completed reliably;
- do not recreate or modify the missing report;
- return `BLOCKED` only if the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-10: Predicate Purity Audit**.

Determine whether every registered predicate and predicate-like execution path is:

- factual;
- deterministic;
- free of side effects;
- independent of evaluation order;
- independent of mutable global state;
- isolated from scoring and interpretation;
- safe to cache where declared cacheable;
- safe to evaluate repeatedly.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Predicate purity contract

A pure predicate should behave conceptually as:

```text
PredicateResult = predicate(
    immutable AstroState,
    canonical parameters,
    explicit evaluation context
)
```

For identical logical inputs and versions, it should produce the same logical result.

Predicates may read:

- normalized facts from `AstroState`;
- prepared enrichments;
- canonical parameters;
- explicit evaluation context;
- immutable configuration or versioned rule tables.

Predicates must not:

- mutate `AstroState`;
- mutate enrichments;
- mutate parameters;
- mutate caller-owned objects;
- mutate global or module state;
- calculate domain scores;
- assign rule weights;
- calculate confidence;
- resolve rule conflicts;
- generate narratives;
- assemble public JSON;
- access raw Surya Siddhanta JSON;
- execute enrichment engines;
- call external services;
- perform network or filesystem I/O;
- read environment variables during evaluation;
- read system time implicitly;
- use randomness;
- depend on cache warmth for logical behavior;
- depend on which predicate executed first.

Use Prompt-01 as authoritative if its exact contract differs.

## 4. Repository-wide discovery

Search the complete repository, including:

- registered predicate handlers;
- unregistered predicate-like helpers from Audit-2;
- predicate registry and evaluator;
- condition evaluator;
- Yoga Engine;
- domain runtimes;
- enrichment engines called by predicates;
- cache code;
- tests and fixtures;
- scripts and utilities;
- configuration and table loaders.

Search for impurity indicators such as:

```python
astro.field = value
astro.enrichments["key"] = value
astro.enrichments.update(...)
params.pop(...)
params.setdefault(...)
params["key"] = value
global ...
nonlocal ...
list.append(...)
dict.update(...)
set.add(...)
random...
uuid...
datetime.now(...)
datetime.utcnow(...)
date.today(...)
time.time(...)
os.environ
os.getenv(...)
open(...)
Path(...).read_text(...)
Path(...).write_text(...)
requests...
httpx...
subprocess...
logging...
print(...)
```

Also search for:

- lazy initialization;
- module-level caches;
- singleton state;
- mutable class variables;
- counters;
- metrics;
- memoization;
- exception swallowing;
- enrichment computation;
- scoring and confidence calculations;
- narrative generation;
- direct output construction.

Treat search matches as candidates. Inspect context before classifying them.

## 5. Complete predicate purity inventory

Using Audit-2 as a starting point, verify every registered predicate directly against current code.

For each predicate, report:

1. Predicate ID.
2. File and handler symbol.
3. Inputs read.
4. `AstroState` fields read.
5. Enrichments read.
6. Evaluation-context values read.
7. Configuration or tables read.
8. Functions called.
9. Direct mutations.
10. Indirect mutation risk.
11. Global-state reads.
12. Global-state writes.
13. System-time reads.
14. Randomness.
15. I/O or external-service calls.
16. Enrichment computation.
17. Scoring or interpretation logic.
18. Exception behavior.
19. Evaluation-order dependency.
20. Cache-safety assessment.
21. Existing purity tests.
22. Compliance, scope and priority.

Do not mark a predicate pure solely because its own function body contains no assignment. Inspect called helpers.

## 6. Call-graph and transitive purity audit

For every registered predicate, inspect its direct helper calls.

Follow calls far enough to determine whether helpers:

- mutate inputs;
- mutate `AstroState`;
- mutate global state;
- read system time;
- use randomness;
- perform I/O;
- calculate enrichments;
- calculate scores;
- call external services;
- depend on non-versioned mutable tables.

Do not perform an unlimited whole-program call-graph analysis. Stop when the relevant purity behavior is established.

For each impurity found through a helper, record:

- predicate ID;
- predicate handler;
- called helper;
- helper file and symbol;
- impurity type;
- active-path evidence;
- whether the helper is shared;
- migration risk.

## 7. AstroState and enrichment mutation

Reconcile this section with Audits 8 and 9.

Find predicates or predicate-related evaluators that:

- write to `AstroState`;
- write to `astro.enrichments`;
- integrate vargas;
- compute aspects and attach them;
- compute functional roles and attach them;
- populate Yoga matches;
- add cached or derived state;
- normalize or repair chart values in place.

Classify every mutation as:

- `DIRECT_PREDICATE_MUTATION`
- `TRANSITIVE_HELPER_MUTATION`
- `CONDITION_EVALUATOR_MUTATION`
- `YOGA_EVALUATION_MUTATION`
- `CALLER_PREPARATION_MUTATION`
- `TEST_ONLY_MUTATION`
- `FALSE_POSITIVE_OR_UNRELATED`

Preparation before predicate evaluation may be valid. Distinguish it from mutation during predicate evaluation.

## 8. Parameter and caller-owned data mutation

Determine whether predicates or helpers mutate:

- the parameter dictionary;
- nested parameter values;
- evidence templates;
- configuration dictionaries;
- caller-owned lists, sets or mappings;
- objects reused across evaluations.

Search for operations such as:

```python
params.pop(...)
params.update(...)
params.setdefault(...)
params["key"] = ...
values.append(...)
values.sort(...)
mapping.clear(...)
```

For every occurrence, determine:

- whether the input is defensively copied;
- whether later evaluations observe the mutation;
- whether cache-key construction happens before or after mutation;
- whether tests reuse the same parameter object;
- whether behavior becomes order dependent.

## 9. Mutable global and module state

Inventory predicate-related mutable globals, including:

- registries;
- caches;
- counters;
- configuration dictionaries;
- loaded rule tables;
- mutable constants;
- singleton services;
- lazy-initialized data;
- module-level error or trace collections.

For each, report:

1. File and symbol.
2. Type.
3. Writers.
4. Readers.
5. Initialization behavior.
6. Test reset behavior.
7. Thread-safety.
8. Whether logical output depends on current state.
9. Whether state is versioned.
10. Whether it affects determinism or cache safety.

Do not classify the predicate registry itself as impure merely because it is mutable during application startup. Assess whether it mutates during evaluation.

## 10. Time dependency

Find every predicate-related use of:

- `datetime.now`;
- `datetime.utcnow`;
- `date.today`;
- `time.time`;
- local timezone lookup;
- implicit “today” defaults;
- current transit date;
- current Dasha evaluation time;
- timestamp generation.

For each occurrence, determine:

- whether the time value affects logical output;
- whether it affects trace or telemetry only;
- whether it is supplied explicitly through evaluation context;
- whether it is included in cache identity;
- whether tests freeze or inject it;
- whether repeated evaluation can differ.

Classify each as:

- `EXPLICIT_CONTEXT_TIME`
- `IMPLICIT_LOGICAL_TIME`
- `TRACE_ONLY_TIME`
- `PERFORMANCE_ONLY_TIME`
- `UNRELATED_TIME_USE`

Prompt-01 predicates must not read system time implicitly.

## 11. Randomness and nondeterministic identity

Find uses of:

- `uuid.uuid4`;
- random-number generation;
- secrets or token generation;
- unordered set iteration;
- unstable object representation;
- process memory IDs;
- Python runtime hash values;
- random trace IDs.

Determine whether each affects:

- `matched`;
- status;
- evidence;
- errors;
- trace steps;
- cache keys;
- serialization;
- snapshots;
- logs only.

Classify as:

- `LOGICAL_NONDETERMINISM`
- `EVIDENCE_NONDETERMINISM`
- `TRACE_NONDETERMINISM`
- `CACHE_NONDETERMINISM`
- `TELEMETRY_ONLY`
- `UNRELATED`

## 12. I/O and external dependency audit

Find predicate-related:

- filesystem reads or writes;
- database access;
- network calls;
- HTTP clients;
- subprocess execution;
- environment-variable reads;
- dynamic configuration reloads;
- logging handlers with side effects.

For every occurrence, report:

1. Predicate or evaluator.
2. File and symbol.
3. I/O type.
4. Data read or written.
5. Whether it affects logical output.
6. Failure behavior.
7. Timeout behavior.
8. Determinism.
9. Cache impact.
10. Prompt-01 scope.

Reading an immutable table loaded before evaluation may be acceptable. Distinguish startup configuration from evaluation-time I/O.

## 13. Factual-boundary audit

For each registered predicate, determine whether it answers only a factual question.

Flag predicates or helpers that:

- assign weights;
- calculate scores;
- calculate confidence;
- combine domain indicators;
- resolve conflicts;
- rank outcomes;
- generate interpretations;
- produce narratives;
- recommend actions;
- assemble API or public JSON;
- create `RuleMatch`;
- perform inference.

Classify each boundary issue as:

- `FACTUAL_PREDICATE`
- `PREDICATE_WITH_MIXED_RESPONSIBILITIES`
- `SCORING_LOGIC_IN_PREDICATE`
- `INTERPRETATION_LOGIC_IN_PREDICATE`
- `OUTPUT_LOGIC_IN_PREDICATE`
- `NOT_ACTUALLY_A_PREDICATE`
- `UNKNOWN`

Do not change astrology behavior. Record only the architectural boundary.

## 14. Enrichment recomputation

Find predicates that calculate facts which should have been prepared by enrichment engines.

Examples may include:

- functional roles;
- aspect graphs;
- vargas;
- planetary strengths;
- house conditions;
- Dasha timelines;
- transit positions.

For every occurrence, report:

- predicate ID;
- enrichment being recomputed;
- called engine or helper;
- whether state is mutated;
- computational cost;
- deterministic inputs;
- version tracking;
- cache implications;
- whether the same fact is computed elsewhere;
- Prompt-01 scope.

Pay special attention to `FUNCTIONAL_ROLE`.

## 15. Exception and fallback behavior

Find predicate-related `try/except` blocks.

Determine whether exceptions:

- are converted to typed errors;
- become unmatched;
- return empty evidence;
- are swallowed;
- trigger fallback computation;
- mutate state;
- retry nondeterministically;
- expose raw exception messages;
- hide impurity.

For every relevant block, report:

```text
File and symbol
Exception scope
Expected or unexpected exception
Current fallback
Logical result produced
State changes before failure
Whether exception is swallowed
Whether strict mode exists
Prompt-01 risk
```

## 16. Repeatability and evaluation-order audit

Determine whether repeated evaluation with the same logical inputs produces the same logical result.

Audit dependencies on:

- prior predicate execution;
- prior Yoga execution;
- prior enrichment computation;
- cache warmth;
- registry mutation;
- caller mutation;
- global configuration changes;
- test ordering;
- dictionary or set iteration order;
- exception history;
- lazy initialization.

Identify sequences such as:

```text
Evaluate predicate A
→ state or global data changes
→ evaluate predicate B
→ result differs
```

For each dependency, report:

- initiating operation;
- mutated or initialized state;
- affected predicate;
- result fields affected;
- active-path evidence;
- test coverage;
- risk and priority.

## 17. Cache-safety assessment

For every predicate declared or assumed cacheable, determine whether it is actually safe to cache.

A cacheable predicate should depend only on:

- deterministic `AstroState` content;
- canonical parameters;
- explicit evaluation context;
- predicate version;
- relevant capability and enrichment versions;
- immutable versioned configuration.

Classify each predicate as:

- `CACHE_SAFE`
- `CACHE_SAFE_WITH_CONTEXT`
- `NOT_CACHE_SAFE`
- `CACHE_SAFETY_UNKNOWN`
- `NOT_APPLICABLE`

Report reasons such as:

- system-time dependency;
- mutable global state;
- missing version tracking;
- state mutation;
- evaluation-order dependency;
- I/O;
- randomness;
- incomplete cache key.

Do not redesign the cache. Audit-11 will examine cache implementation in detail.

## 18. Thread-safety and parallel evaluation

Assess whether predicate evaluation is safe when different predicates or charts are evaluated concurrently.

Inspect:

- shared mutable registries;
- global caches;
- counters;
- mutable configuration;
- lazy initialization;
- shared AstroState mutation;
- non-atomic cache operations;
- test-only global registrations.

Do not perform unsafe stress tests.

Classify findings as:

- `THREAD_SAFE`
- `PROBABLY_THREAD_SAFE`
- `NOT_THREAD_SAFE`
- `UNKNOWN`

Only include issues relevant to Prompt-01 purity and determinism.

## 19. Test inventory and gap analysis

Locate tests covering:

### Direct purity

- predicate does not mutate `AstroState`;
- predicate does not mutate enrichments;
- predicate does not mutate parameters;
- predicate does not mutate caller-owned nested values;
- predicate does not modify global state.

### Determinism

- repeated evaluation produces equivalent logical results;
- separate equivalent AstroState instances produce equivalent results;
- system time does not affect predicates without explicit context;
- random identity does not affect logical results;
- unordered input does not affect serialization.

### Evaluation order

- predicate order does not affect results;
- Yoga execution does not affect later predicates;
- cold and warm cache runs are logically equivalent;
- lazy initialization does not change logical output.

### Boundary enforcement

- predicates do not import domain interpreters;
- predicates do not calculate scores;
- predicates do not access raw Surya data;
- predicates do not call external services;
- predicates do not perform evaluation-time file I/O;
- predicates do not run enrichment engines.

### Cache safety

- cacheable predicates have no implicit dependencies;
- evaluation context isolates time-dependent results;
- configuration or enrichment versions isolate results.

For every missing test category:

- identify the gap;
- explain its risk;
- recommend the likely test file;
- do not create the test.

## 20. Required classifications

Classify predicate purity as:

- `PURE`
- `PURE_WITH_EXPLICIT_CONTEXT`
- `MOSTLY_PURE_WITH_RISK`
- `IMPURE`
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

## 21. Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- symbol name;
- line number or small range when practical;
- predicate ID or caller;
- impurity type;
- direct or transitive behavior;
- affected logical or telemetry fields;
- active-path evidence;
- existing tests;
- cache or determinism impact;
- uncertainty where static analysis cannot prove runtime behavior.

Reconcile findings with Audits 1–9.

Explain:

- predicate inventory differences from Audit-2;
- legacy-path implications from Audit-3;
- caller implications from Audit-4;
- result-model determinism implications from Audits 5 and 6;
- parameter mutation findings related to Audit-7;
- capability recomputation findings from Audit-8;
- AstroState mutation and identity findings from Audit-9.

Do not modify earlier reports.

## 22. Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify rules;
- modify previous audit reports;
- refactor predicates;
- remove side effects;
- relocate enrichment logic;
- add context parameters;
- change cache behavior;
- change logging;
- change astrology semantics;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-11.

You may run safe, non-mutating searches and tests.

Do not execute commands that update files, snapshots or generated artifacts.

## 23. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-10-Predicate-Purity.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker instead of selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-10: Predicate Purity

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–9
## 4. Predicate Purity Contract
## 5. Complete Predicate Purity Inventory
## 6. Transitive Helper and Call-Graph Assessment
## 7. AstroState and Enrichment Mutation
## 8. Parameter and Caller-Owned Data Mutation
## 9. Mutable Global and Module State
## 10. Time and Randomness Dependencies
## 11. I/O and External Dependencies
## 12. Factual Predicate Boundary
## 13. Enrichment Recomputation
## 14. Exception and Fallback Behavior
## 15. Repeatability and Evaluation-Order Dependencies
## 16. Cache-Safety Assessment
## 17. Thread-Safety and Parallel Evaluation
## 18. Existing Tests and Coverage Gaps
## 19. Prompt-01 Compliance Matrix
## 20. Migration Risks and Priorities
## 21. Unresolved Architectural Questions
## 22. Audit-10 Conclusion
```

### Complete predicate purity inventory

Include these columns:

| Predicate ID | File | Handler | Inputs Read | Helpers Called | State Mutation | Parameter Mutation | Global State | Time | Randomness | I/O | Enrichment Computation | Scoring/Interpretation | Order Dependency | Purity | Cache Safety | Tests | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Transitive impurity inventory

Include these columns:

| Predicate ID | Handler | Called Helper | Helper File | Impurity Type | Direct/Transitive | State Affected | Logical Impact | Active Path | Shared Helper | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|

### Mutable global-state inventory

Include these columns:

| File | Symbol | Type | Readers | Writers | Mutates During Evaluation | Versioned | Thread-Safe | Logical Impact | Tests | Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|

### Nondeterminism inventory

Include these columns:

| File | Symbol | Predicate/Caller | Source | Classification | Fields Affected | Explicit Context | Cache Impact | Snapshot Impact | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Cache-safety matrix

Include these columns:

| Predicate ID | Declared Cacheable | Purity | Implicit Dependencies | Context Required | Version Coverage | Cache Classification | Evidence | Required Action | Priority |
|---|---|---|---|---|---|---|---|---|---|

### Compliance matrix

Include these columns:

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- registered predicates audited;
- pure predicates;
- predicates pure only with explicit context;
- mostly pure predicates with risks;
- impure predicates;
- predicates with unknown purity;
- direct mutation paths;
- transitive mutation paths;
- parameter-mutation paths;
- mutable global-state dependencies;
- implicit system-time dependencies;
- randomness dependencies;
- evaluation-time I/O paths;
- enrichment-recomputation paths;
- scoring or interpretation boundary violations;
- evaluation-order dependencies;
- predicates classified as not cache-safe;
- missing purity-test categories;
- P0, P1, P2 and P3 findings.

## 24. Final response

After creating the report, stop.

Respond with only:

1. Audit-10 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Registered predicates audited
6. Pure, context-dependent, mostly pure, impure and unknown counts
7. Direct and transitive mutation counts
8. Implicit time or randomness dependency count
9. Enrichment-recomputation count
10. Factual-boundary violation count
11. Evaluation-order dependency count
12. Not-cache-safe predicate count
13. Missing purity-test-category count
14. Number of P0, P1, P2 and P3 findings
15. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-11.
