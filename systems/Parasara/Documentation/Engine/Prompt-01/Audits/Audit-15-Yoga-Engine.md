# Prompt-01 — Audit-15: Yoga Engine Audit

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

If an expected report is missing:

- record it as a limitation;
- continue if Audit-15 can still be completed reliably;
- do not recreate or modify the missing report;
- return `BLOCKED` only when the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-15: Yoga Engine Audit**.

Inspect every Yoga evaluation path and determine whether the Yoga Engine:

- uses the generic condition evaluator;
- uses the central predicate registry;
- receives typed `PredicateResult` values;
- preserves status, evidence, errors and traces;
- contains legacy tuple-return evaluation paths;
- duplicates registered predicate logic;
- recomputes enrichments;
- mutates `AstroState`;
- clears or modifies predicate caches;
- generates deterministic output;
- preserves current Yoga matching behavior during Prompt-01 migration.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Architectural boundary

The intended boundary is:

```text
Yoga rule
    ↓
Generic rule/condition evaluator
    ↓
Predicate registry
    ↓
Registered factual predicate
    ↓
PredicateResult
    ↓
Yoga match processing
```

Yoga must not maintain an active parallel predicate engine.

Yoga-specific code may:

- load Yoga rules;
- submit condition trees to the generic evaluator;
- consume typed condition results;
- construct Yoga-domain match information after factual evaluation.

Yoga-specific code must not:

- duplicate registered predicate logic;
- maintain an active tuple-return predicate contract;
- silently convert predicate errors to non-matches;
- treat missing capability as negative evidence;
- mutate `AstroState` during predicate evaluation;
- recompute enrichments inside predicates;
- depend on random identity for deterministic logical output.

Use the authoritative documents when exact boundaries differ.

## 4. Repository-wide discovery

Search the complete repository for:

- Yoga Engine modules;
- Yoga rule loaders;
- Yoga rule files;
- Yoga evaluators;
- Yoga match models;
- Yoga evidence assembly;
- generic condition-evaluator calls;
- direct predicate-handler calls;
- predicate-registry calls;
- Yoga-specific condition helpers;
- tuple-return functions;
- raw-boolean functions;
- enrichment computation;
- AstroState mutation;
- cache clearing;
- UUID generation;
- trace generation;
- Yoga tests and fixtures;
- domain code consuming Yoga results.

Search for terms such as:

```text
yoga
evaluate_yoga
evaluate_yoga_rules
_eval_condition
_eval_aspect_condition
_eval_functional_role_condition
_eval_house_lords_combination
_eval_house_occupant
evaluate_condition
evaluate_predicate
PredicateResult
Tuple[bool
cache.clear
clear_cache
uuid
trace
evidence
enrichments["yogas"]
```

Do not rely only on the known `yoga_engine.py` filename.

## 5. Yoga component inventory

Identify every Yoga-related production, test and documentation component.

For each component, report:

1. File and symbol.
2. Category.
3. Responsibility.
4. Inputs.
5. Outputs.
6. Rule source.
7. Loader or parser.
8. Evaluator used.
9. Predicate integration.
10. State mutation.
11. Cache interaction.
12. Trace behavior.
13. Production, test-only, legacy or documentation status.
14. Callers.
15. Tests.

Classify components as:

- `YOGA_RULE_SOURCE`
- `YOGA_LOADER`
- `YOGA_EVALUATOR`
- `YOGA_MATCH_MODEL`
- `YOGA_EVIDENCE_ASSEMBLER`
- `LEGACY_CONDITION_HELPER`
- `ENRICHMENT_OR_PREPARATION`
- `CALLER_OR_CONSUMER`
- `TEST_OR_FIXTURE`
- `DOCUMENTATION`
- `UNKNOWN`

## 6. End-to-end Yoga execution paths

Trace every active Yoga execution path:

```text
Entry point
→ rule loading
→ rule normalization
→ condition evaluation
→ predicate evaluation
→ result aggregation
→ Yoga match creation
→ storage or return
→ downstream consumer
```

For every path, document:

- entry point;
- rule source;
- loader;
- condition format;
- evaluator;
- predicate dispatch;
- intermediate result types;
- final return type;
- evidence handling;
- error handling;
- trace handling;
- cache behavior;
- AstroState mutation;
- deterministic identity;
- downstream consumers.

Identify all alternate, fallback and test-only paths.

## 7. Generic evaluator integration

Determine whether active Yoga evaluation calls the canonical:

```python
evaluate_condition(...)
```

For each call site, report:

1. File and symbol.
2. Condition supplied.
3. Context supplied.
4. Return contract expected.
5. Whether `.matched` is read.
6. Whether a tuple is expected.
7. Whether evidence is preserved.
8. Whether errors are preserved.
9. Whether status is preserved.
10. Whether trace steps are preserved.
11. Whether child results are preserved.
12. Whether non-match, missing capability and error are distinguished.

Reconcile with Audits 4 and 12.

## 8. Predicate registry integration

Determine whether Yoga predicate leaves:

- use `evaluate_predicate`;
- resolve the central registry;
- call handlers directly;
- call Yoga-specific helpers;
- duplicate registered predicate logic;
- use predicate aliases;
- validate predicate versions;
- validate parameters;
- check required capabilities.

Identify every Yoga path that bypasses the generic predicate engine.

## 9. Legacy Yoga evaluator inventory

Inspect legacy functions such as:

```text
_eval_aspect_condition
_eval_functional_role_condition
_eval_house_lords_combination
_eval_house_occupant
_eval_condition
```

Also find equivalent functions under other names.

For each legacy helper, report:

1. File and symbol.
2. Signature.
3. Return contract.
4. Factual or logical responsibility.
5. Predicate logic duplicated.
6. Registered equivalent.
7. Direct callers.
8. Indirect or dynamic callers.
9. Active-path status.
10. Tests.
11. Evidence behavior.
12. Error behavior.
13. Trace behavior.
14. Prompt-01 migration requirement.

Classify execution status as:

- `ACTIVE_PRODUCTION_PATH`
- `ACTIVE_FALLBACK_PATH`
- `ACTIVE_TEST_PATH_ONLY`
- `DORMANT_BUT_REFERENCED`
- `CONFIRMED_UNUSED`
- `UNKNOWN`

Do not use `CONFIRMED_UNUSED` without repository-wide caller evidence.

Do not remove any helper during the audit.

## 10. Duplicate predicate logic

Compare Yoga-specific factual checks with the registered predicate inventory.

Identify duplication involving:

- aspects;
- functional roles;
- house lords;
- house occupants;
- planetary placement;
- exaltation or dignity;
- conjunctions;
- other factual checks.

For each duplicate, report:

- Yoga symbol;
- registered predicate ID;
- semantic differences;
- parameter differences;
- evidence differences;
- error differences;
- active callers;
- astrology-semantic risk;
- migration priority.

Do not assume similarly named functions are semantically identical. Compare their actual behavior.

## 11. Return-contract and information-loss audit

Determine every result contract used inside Yoga:

- `PredicateResult`;
- `ConditionResult`;
- tuple;
- raw boolean;
- dictionary;
- Yoga-specific result model;
- `None`.

For each conversion boundary, determine whether Yoga loses:

- predicate ID;
- predicate version;
- status;
- evidence;
- typed errors;
- traces;
- child results;
- cache telemetry;
- evaluation order.

Pay particular attention to:

```python
matched, evidence = ...
```

```python
if result:
```

```python
if result.matched:
```

and dictionary-only evidence extraction.

## 12. Status and error semantics

Determine how Yoga handles:

- matched;
- unmatched;
- missing capability;
- invalid parameters;
- error;
- timeout;
- skipped.

Report whether Yoga:

- treats every `matched=False` result identically;
- silently ignores predicate errors;
- treats missing capability as a Yoga non-match;
- continues after invalid rule parameters;
- stores errors for diagnostics;
- exposes raw exception text;
- preserves recoverability.

Do not invent Yoga-domain behavior for unresolved statuses. Record the decision required.

## 13. Evidence preservation and correctness

For each Yoga evaluation path, determine whether evidence:

- is preserved for matched predicates;
- is preserved for unmatched predicates;
- contains actual and expected facts;
- identifies predicate IDs;
- identifies Yoga rule IDs;
- retains child-condition structure;
- uses stable AstroState identifiers;
- remains JSON-safe;
- remains immutable;
- is overwritten during aggregation;
- is converted into narrative-only text.

Identify evidence that may be factually misleading, but do not change astrology semantics.

## 14. Trace behavior

Identify Yoga-related:

- predicate trace steps;
- condition traces;
- Yoga trace IDs;
- rule IDs;
- parent-child relationships;
- evaluation-order records;
- skipped-branch traces;
- cache-hit traces;
- timestamps;
- duration fields;
- UUID generation.

Determine whether Yoga trace identity or ordering is deterministic.

Classify nondeterminism as:

- `LOGICAL_NONDETERMINISM`
- `EVIDENCE_NONDETERMINISM`
- `TRACE_ONLY_NONDETERMINISM`
- `PERFORMANCE_ONLY_NONDETERMINISM`
- `UNRELATED`

## 15. Enrichment preparation and recomputation

Determine whether Yoga invokes:

- varga integration;
- aspect-graph computation;
- functional-role computation;
- house-condition computation;
- strength computation;
- other enrichment engines.

For every occurrence, report:

1. File and symbol.
2. Enrichment.
3. When it runs.
4. Whether it mutates `AstroState`.
5. Whether it is required preparation or evaluation-time recomputation.
6. Whether it is idempotent.
7. Whether it is deterministic.
8. Whether it is versioned.
9. Whether it changes predicate cache assumptions.
10. Whether callers already prepared the enrichment.
11. Prompt-01 classification.

Distinguish legitimate pre-evaluation preparation from mutation during condition evaluation.

## 16. AstroState mutation

Find every Yoga-related write such as:

```python
astro.enrichments["yogas"] = matches
astro.enrichments.update(...)
integrate_vargas_into_astro(astro)
compute_aspect_graph(astro)
setattr(astro, ...)
```

For each mutation, determine:

- lifecycle stage;
- direct or indirect mutation;
- whether predicate evaluation has already begun;
- whether subsequent predicates observe changed state;
- whether evaluation order matters;
- whether cached results become stale;
- whether tests depend on mutation;
- whether Yoga results are returned separately or stored in state.

Reconcile with Audits 8–10.

## 17. Predicate cache interaction

Determine whether Yoga:

- reads predicate cache entries;
- writes predicate cache entries;
- clears the global cache;
- clears cache before or after enrichment;
- depends on cache warmth;
- triggers stale entries through mutation;
- changes `cache_hit` behavior;
- shares cache state across Yoga rules;
- leaks cache state across charts or tests.

Report every cache-clear operation and its callers.

Do not change cache behavior.

## 18. Yoga rule loading and validation

Determine whether Yoga uses:

- the generic rule loader;
- a Yoga-specific loader;
- raw YAML or JSON dictionaries;
- Python-created rules.

Audit whether Yoga validates:

- Yoga rule IDs;
- duplicate IDs;
- predicate IDs;
- predicate versions;
- parameters;
- logical operators;
- condition arity;
- required capabilities;
- rule provenance;
- SME approval.

Reconcile with Audits 13 and 14.

## 19. Determinism

Identify Yoga nondeterminism involving:

- random UUIDs;
- current time;
- unordered mappings or sets;
- filesystem traversal order;
- rule iteration order;
- registry iteration order;
- mutable global state;
- cache state;
- AstroState mutation;
- performance timings;
- enrichment timing.

Determine whether identical inputs and versions produce identical:

- Yoga match sets;
- match ordering;
- evidence;
- errors;
- logical trace content;
- serialized output.

## 20. Downstream compatibility

Identify all consumers of Yoga results.

Determine whether they depend on:

- current match ordering;
- Yoga IDs;
- evidence dictionaries;
- mutable AstroState enrichment storage;
- tuple results;
- raw booleans;
- omitted errors;
- random trace IDs;
- current public serialization.

Pay attention to:

- domain interpreters;
- inference;
- output assembly;
- tests;
- snapshots;
- reports.

Prompt-01 must not unintentionally change Yoga matching or downstream scoring behavior.

## 21. Test inventory and gap analysis

Locate tests covering:

### Generic integration

- Yoga uses the generic condition evaluator;
- Yoga uses the predicate registry;
- typed predicate results reach Yoga;
- no direct-handler bypass;
- no tuple unpacking.

### Match behavior

- Yoga match;
- Yoga non-match;
- multiple rules;
- nested conditions;
- deterministic ordering;
- repeated evaluation.

### Status behavior

- missing capability;
- invalid parameters;
- predicate error;
- timeout;
- skipped branch;
- distinction from unmatched.

### Evidence and trace

- evidence preservation;
- error preservation;
- child-result preservation;
- deterministic trace;
- no random logical identity.

### State and cache

- Yoga does not mutate AstroState during evaluation;
- enrichment preparation occurs before evaluation;
- cache is not incorrectly cleared;
- no stale results after enrichment;
- cold and warm logical equivalence.

### Legacy enforcement

- no active Yoga tuple-return evaluator;
- no duplicate Yoga predicate logic;
- no custom fallback evaluator;
- no raw-boolean predicate contract.

For every missing test category:

- identify the gap;
- explain its risk;
- recommend the likely test file;
- do not create the test.

## 22. Required issue classifications

Classify every Yoga issue as:

- `MUST_FIX_IN_PROMPT_01`
- `TEMPORARY_COMPATIBILITY`
- `FUTURE_ARCHITECTURE_STAGE`
- `UNRELATED`

Classify integration paths as:

- `GENERIC_COMPLIANT_PATH`
- `GENERIC_PATH_WITH_INFORMATION_LOSS`
- `LEGACY_PARALLEL_PATH`
- `DIRECT_PREDICATE_BYPASS`
- `TEST_ONLY_PATH`
- `UNKNOWN`

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

## 23. Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- symbol name;
- line number or small range when practical;
- Yoga rule, evaluator or caller;
- current contract;
- active-path evidence;
- evidence, error and trace behavior;
- mutation or cache impact;
- existing tests;
- Prompt-01 classification;
- uncertainty where static analysis cannot prove runtime behavior.

Reconcile findings with Audits 1–14, especially:

- registry integration from Audit-1;
- predicate duplication from Audit-2;
- legacy contracts from Audit-3;
- caller expectations from Audit-4;
- capability and state findings from Audits 8–10;
- cache findings from Audit-11;
- condition evaluation from Audit-12;
- formats and loaders from Audits 13–14.

Do not modify earlier reports.

## 24. Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify Yoga rules;
- modify previous audit reports;
- remove legacy Yoga helpers;
- migrate Yoga callers;
- change Yoga matching;
- change astrology semantics;
- compute enrichments;
- mutate AstroState;
- clear caches as a persistent action;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-16.

You may run safe, non-mutating searches and tests.

Do not execute commands that update files, snapshots or generated artifacts.

## 25. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-15-Yoga-Engine.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker rather than selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-15: Yoga Engine

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–14
## 4. Yoga Component Inventory
## 5. End-to-End Yoga Execution Paths
## 6. Generic Condition-Evaluator Integration
## 7. Predicate Registry Integration
## 8. Legacy Yoga Evaluators
## 9. Duplicate Predicate Logic
## 10. Return Contracts and Information Loss
## 11. Status and Error Semantics
## 12. Evidence Quality and Preservation
## 13. Trace and Determinism
## 14. Enrichment Preparation and Recomputation
## 15. AstroState Mutation
## 16. Predicate Cache Interaction
## 17. Yoga Rule Loading and Validation
## 18. Downstream Compatibility
## 19. Existing Tests and Coverage Gaps
## 20. Prompt-01 Compliance Matrix
## 21. Migration Risks and Priorities
## 22. Unresolved Architectural Questions
## 23. Audit-15 Conclusion
```

### Yoga component inventory

Include these columns:

| Component | File | Symbol | Category | Responsibility | Inputs | Outputs | Loader | Evaluator | Predicate Integration | Mutation | Cache Interaction | Callers | Status | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Yoga execution-path inventory

Include these columns:

| Entry Point | Rule Source | Loader | Condition Format | Evaluator | Predicate Dispatch | Intermediate Contract | Final Contract | Evidence | Errors | Trace | Mutation | Cache | Consumers | Classification | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Legacy Yoga helper inventory

Include these columns:

| File | Symbol | Signature | Return Contract | Responsibility | Duplicate Predicate | Confirmed Callers | Execution Status | Evidence | Errors | Trace | Migration Required | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Mutation and enrichment inventory

Include these columns:

| File | Symbol | Operation | Enrichment/Field | Lifecycle Stage | Direct/Indirect | Mutates AstroState | Order Dependent | Cache Risk | Tests | Classification | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|

### Downstream compatibility matrix

Include these columns:

| Consumer | File | Yoga API/Field Used | Expected Contract | Evidence Use | Error Use | Ordering Dependency | Mutation Dependency | Serialization Impact | Regression Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Compliance matrix

Include these columns:

| Requirement | Status | Evidence | Affected Files | Required Change | Classification | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- Yoga components;
- active Yoga execution paths;
- generic-compliant paths;
- generic paths with information loss;
- legacy parallel paths;
- direct predicate bypasses;
- legacy tuple-return helpers;
- duplicate predicate implementations;
- confirmed-unused legacy helpers;
- helpers with unknown usage;
- status-loss paths;
- evidence-loss paths;
- error-loss paths;
- trace-loss paths;
- enrichment-recomputation paths;
- AstroState mutation paths;
- cache-clear or stale-cache risks;
- nondeterministic Yoga mechanisms;
- downstream consumers at regression risk;
- missing Yoga test categories;
- P0, P1, P2 and P3 findings.

## 26. Final response

After creating the report, stop.

Respond with only:

1. Audit-15 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Yoga component and active execution-path counts
6. Generic-compliant, information-loss, legacy and bypass path counts
7. Legacy tuple-helper and duplicate-predicate counts
8. Status, evidence, error and trace-loss counts
9. Enrichment-recomputation and AstroState-mutation counts
10. Cache-risk and nondeterminism counts
11. Downstream regression-risk count
12. Missing test-category count
13. Number of P0, P1, P2 and P3 findings
14. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-16.