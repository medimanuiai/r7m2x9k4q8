# Prompt-01 — Audit-16: Domain Runtime Audit

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

If an expected report is missing:

- record it as a limitation;
- continue if Audit-16 can still be completed reliably;
- do not recreate or modify it;
- return `BLOCKED` only when the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-16: Domain Runtime Audit**.

Inspect Career and every other implemented domain runtime. Determine whether domain code correctly consumes generic predicate and condition results without bypassing, duplicating or weakening the Prompt-01 contract.

Identify whether domain code:

- calls predicates directly;
- calls the generic predicate evaluator;
- calls the condition evaluator;
- tuple-unpacks results;
- consumes raw booleans;
- reads only `matched` and ignores status;
- discards evidence, errors, traces or predicate versions;
- treats predicate failures as ordinary non-matches;
- recomputes factual predicate logic;
- mutates `AstroState`;
- accesses raw Surya Siddhanta data;
- relies on mutable result objects;
- serializes predicate results publicly;
- changes scoring behavior between cold and warm cache runs.

Prompt-01 must preserve existing domain scoring behavior while correcting the predicate contract.

This is a repository-wide, read-only audit. Do not implement corrections.

## 3. Architectural boundary

Use this boundary:

```text
AstroState and enrichments
    → Generic Predicate Engine
    → PredicateResult
    → Generic Condition/Rule Engine
    → typed condition or rule result
    → Domain Interpreter
    → domain scoring and interpretation
```

Predicates answer factual questions. Domain interpreters may perform domain-specific scoring and interpretation after consuming typed factual results.

Domain runtimes must not create parallel factual predicate engines or silently reinterpret unavailable facts as negative evidence.

Do not move scoring into predicates or factual evaluation into domain code during this audit.

## 4. Repository-wide discovery

Search the complete repository for all implemented domains, including but not limited to:

- Career;
- wealth and finance;
- marriage and relationships;
- children;
- health;
- safety or longevity;
- education;
- spirituality;
- any additional system-specific domains.

Search production code, tests, fixtures, rules, scripts, examples and documentation.

Search for:

```text
evaluate_predicate
evaluate_condition
PredicateResult
ConditionResult
matched
evidence
errors
trace_steps
status
tuple unpacking
predicate registry lookup
direct predicate handler imports
raw AstroState access
raw Surya input access
score
confidence
weight
indicator
interpret
```

Do not assume a directory or class is a domain runtime based only on its name. Verify its role and active callers.

## 5. Domain component inventory

Identify every domain-related component.

For each component, report:

1. File and symbol.
2. Domain.
3. Responsibility.
4. Inputs and outputs.
5. Rule source.
6. Loader and evaluator used.
7. Predicate integration.
8. Scoring and confidence behavior.
9. Evidence, error and trace behavior.
10. AstroState access and mutation.
11. Downstream consumers.
12. Production, test-only, legacy or documentation status.
13. Existing tests.

Classify each component as:

- `DOMAIN_ENTRY_POINT`
- `DOMAIN_RULE_LOADER`
- `DOMAIN_CONDITION_CALLER`
- `DOMAIN_SCORER`
- `DOMAIN_INTERPRETER`
- `DOMAIN_OUTPUT_ADAPTER`
- `DOMAIN_FACT_HELPER`
- `LEGACY_DOMAIN_EVALUATOR`
- `TEST_OR_FIXTURE`
- `DOCUMENTATION`
- `UNKNOWN`

## 6. End-to-end domain execution paths

Trace every active domain path:

```text
Entry point
→ rule or indicator loading
→ factual or condition evaluation
→ result consumption
→ scoring
→ confidence
→ interpretation
→ output or inference consumer
```

For every path, document:

- entry point;
- domain;
- rule or indicator source;
- evaluator called;
- intermediate contracts;
- scoring inputs;
- evidence propagation;
- error propagation;
- trace propagation;
- cache interaction;
- final output;
- active-path evidence.

## 7. Generic predicate and condition integration

For every domain caller, determine whether it:

- calls `evaluate_predicate(...)`;
- calls `evaluate_condition(...)`;
- receives a typed result;
- calls a registered handler directly;
- resolves the registry directly;
- calls a legacy tuple-return helper;
- implements factual checks inline;
- expects logical operators to return `PredicateResult`.

Report every bypass of the generic evaluation path.

## 8. Result-consumption audit

For each domain caller, determine whether it:

- tuple-unpacks a result;
- checks raw truthiness;
- reads `.matched`;
- reads `.status`;
- reads `.predicate_version`;
- preserves inputs;
- preserves matched evidence;
- preserves unmatched evidence;
- preserves typed errors;
- preserves traces;
- preserves nested child results;
- mutates the result or nested structures;
- serializes the result.

Identify every conversion boundary and the information lost.

## 9. Status semantics

Audit domain behavior for:

- `matched`;
- `unmatched`;
- `missing_capability`;
- `invalid_parameters`;
- `error`;
- `timeout`;
- `skipped`.

Determine whether domain code:

- treats every `matched=False` result identically;
- converts errors into zero scores;
- treats missing capability as negative evidence;
- ignores invalid parameters;
- continues after timeout;
- records skipped facts as evaluated facts;
- lowers confidence for unavailable data;
- exposes diagnostic errors to public output.

Do not invent final scoring semantics for non-match statuses. Record unresolved decisions with exact affected callers.

## 10. Evidence handling

Determine whether domain code:

- preserves factual evidence;
- uses expected and actual values;
- keeps predicate identity;
- associates evidence with rule or indicator identity;
- overwrites evidence keys;
- flattens nested evidence;
- discards unmatched evidence;
- converts evidence into narrative-only text;
- stores mutable or non-JSON-safe objects;
- inserts domain scores into predicate evidence.

Identify evidence needed for explainability that is lost before inference or output assembly.

## 11. Error and trace handling

Find where domain runtimes consume, ignore or transform predicate and condition errors and traces.

Report whether:

- typed errors are retained;
- stable error codes are preserved;
- raw exception text is exposed;
- recoverability is preserved;
- trace order is deterministic;
- predicate trace steps reach downstream processing;
- cache hits alter trace content;
- random IDs or timing fields affect domain output.

## 12. Direct factual logic and duplication

Identify factual astrological checks implemented inside domain code that duplicate registered predicates or predicate-like helpers.

For every duplicate, report:

- domain file and symbol;
- factual calculation;
- registered predicate equivalent;
- semantic differences;
- parameter differences;
- evidence differences;
- active callers;
- migration risk.

Do not classify domain scoring, weighting or interpretation as duplicate predicate logic unless it actually answers a factual question.

## 13. Scoring and confidence compatibility

Document how each domain calculates:

- indicator values;
- weights;
- positive and negative contributions;
- scores;
- confidence;
- conflict resolution;
- thresholds;
- missing-data adjustments.

Do not judge or redesign the domain algorithms. Identify only how Prompt-01 contract changes could alter them.

Assess compatibility when:

- missing capability no longer appears as unmatched;
- invalid parameters no longer appear as unmatched;
- predicate errors become typed;
- tuple paths are removed;
- `ConditionResult` replaces logical-node `PredicateResult`;
- evidence becomes immutable;
- cold and warm cache results differ only in telemetry.

## 14. AstroState and raw-source boundary

Determine whether domain runtime code:

- reads normalized `AstroState` facts;
- reads enrichments directly;
- mutates `AstroState`;
- computes enrichments;
- accesses raw Surya Siddhanta JSON;
- repairs or normalizes raw chart data;
- depends on provider-specific keys.

Distinguish legitimate domain consumption of prepared facts from duplicated predicate or enrichment logic.

## 15. Mutation and statefulness

Find domain-related mutation of:

- `AstroState`;
- enrichments;
- predicate or condition results;
- evidence;
- parameters;
- global registries;
- global caches;
- shared scoring state.

Determine whether repeated domain evaluation or domain evaluation order can change results.

## 16. Cache interaction

Determine whether domains:

- directly access or clear predicate caches;
- depend on cache warmth;
- mutate state after caching;
- include `cache_hit` in scoring or evidence;
- include timing in snapshots;
- receive logically different cold and warm results.

Reconcile with Audit-11.

## 17. Serialization and public-output dependency

Find every domain path that serializes or publicly exposes:

- predicate results;
- condition results;
- predicate evidence;
- predicate errors;
- predicate traces;
- domain scores based on predicate outcomes.

Assess whether Prompt-01 changes could affect:

- field names;
- enum serialization;
- lists versus tuples;
- immutable mappings;
- snapshots;
- API responses;
- public JSON schema;
- deterministic ordering.

Do not modify schemas or snapshots.

## 18. Domain-by-domain compatibility assessment

For every implemented domain, classify Prompt-01 compatibility as:

- `COMPATIBLE_NO_CALLER_CHANGE`
- `COMPATIBLE_WITH_INDIRECT_DEPENDENCY`
- `DIRECT_CALLER_MIGRATION_REQUIRED`
- `SCORING_REGRESSION_RISK`
- `INACTIVE_OR_TEST_ONLY`
- `UNKNOWN`

Provide evidence for the classification.

## 19. Test inventory and gap analysis

Locate tests covering:

### Integration

- domain uses generic predicate evaluation;
- domain uses generic condition evaluation;
- no direct registered-handler bypass;
- no tuple or raw-boolean predicate contract;
- typed results reach domain scoring.

### Status behavior

- matched;
- unmatched;
- missing capability;
- invalid parameters;
- predicate error;
- timeout;
- skipped branch.

### Evidence and diagnostics

- matched evidence reaches the domain;
- unmatched evidence is preserved where required;
- errors are preserved;
- traces are preserved;
- raw exception text is not public.

### Regression behavior

- current domain scores remain stable for valid inputs;
- rule firing remains stable;
- confidence remains stable;
- cold and warm evaluation are logically equivalent;
- repeated evaluation is deterministic;
- serialization remains compatible where required.

### Architecture enforcement

- no tuple-unpacking domain caller;
- no raw-boolean predicate caller;
- no domain import from raw Surya adapters;
- no predicate import of domain interpreters;
- no domain mutation of predicate results.

For every missing test category:

- identify the gap;
- explain its risk;
- recommend the likely test file;
- do not create the test.

## 20. Required classifications

Classify caller integration as:

- `GENERIC_TYPED_PATH`
- `GENERIC_PATH_WITH_INFORMATION_LOSS`
- `DIRECT_HANDLER_BYPASS`
- `LEGACY_TUPLE_OR_BOOLEAN_PATH`
- `INLINE_FACTUAL_LOGIC`
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
- domain and execution path;
- current input and result contract;
- observed status, evidence, error and trace behavior;
- scoring or compatibility impact;
- active-path evidence;
- existing tests;
- uncertainty where static analysis cannot prove runtime behavior.

Reconcile findings with Audits 1–15, especially:

- predicate and caller inventories from Audits 2–4;
- result and supporting models from Audits 5–6;
- capability and state boundaries from Audits 8–10;
- cache behavior from Audit-11;
- condition behavior from Audit-12;
- rule-loading behavior from Audit-14;
- Yoga integration from Audit-15.

Do not modify earlier reports.

## 22. Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify rules;
- modify previous audit reports;
- migrate domain callers;
- change scores, weights or confidence;
- change astrology semantics;
- add adapters;
- change serialization;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-17.

You may run safe, non-mutating searches and tests.

Do not execute commands that update files, snapshots or generated artifacts.

## 23. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-16-Domain-Runtime.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker rather than selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-16: Domain Runtime

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–15
## 4. Domain Component Inventory
## 5. End-to-End Domain Execution Paths
## 6. Generic Predicate and Condition Integration
## 7. Result-Consumption Contracts
## 8. Status Semantics
## 9. Evidence, Error and Trace Handling
## 10. Direct Factual Logic and Duplication
## 11. Scoring and Confidence Compatibility
## 12. AstroState and Raw-Source Boundary
## 13. Mutation, Statefulness and Cache Interaction
## 14. Serialization and Public-Output Dependencies
## 15. Domain-by-Domain Compatibility Assessment
## 16. Existing Tests and Coverage Gaps
## 17. Prompt-01 Compliance Matrix
## 18. Migration Risks and Priorities
## 19. Unresolved Architectural Questions
## 20. Audit-16 Conclusion
```

### Domain component inventory

| Domain | Component | File | Symbol | Category | Responsibility | Inputs | Outputs | Evaluator | Predicate Integration | Scoring | Mutation | Consumers | Status | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Domain execution-path inventory

| Domain | Entry Point | Rule/Indicator Source | Loader | Evaluator | Intermediate Contract | Consumption Pattern | Scoring Path | Evidence | Errors | Trace | Cache | Output | Active Evidence | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Domain caller inventory

| Domain | File | Symbol | Called API | Integration Type | Expected Contract | Status Use | Evidence Use | Error Use | Trace Use | Mutation | Serialization | Migration Required | Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Scoring compatibility matrix

| Domain | Current Scoring Input | Unmatched Behavior | Missing-Capability Behavior | Invalid-Parameter Behavior | Error Behavior | ConditionResult Impact | Tuple-Removal Impact | Regression Risk | Required Decision | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Domain compatibility matrix

| Domain | Active | Generic Typed Path | Direct Bypass | Legacy Contract | Inline Facts | Evidence Preserved | Errors Preserved | Traces Preserved | Compatibility Classification | Required Action | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|

### Compliance matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- implemented domains;
- active domain execution paths;
- generic typed paths;
- generic paths with information loss;
- direct predicate-handler bypasses;
- legacy tuple or raw-boolean paths;
- inline factual-logic duplicates;
- callers discarding status;
- callers discarding evidence;
- callers discarding errors;
- callers discarding traces;
- missing-capability-to-negative-evidence paths;
- scoring regression risks;
- AstroState or result mutation paths;
- raw Surya boundary violations;
- cache-related domain risks;
- public serialization impacts;
- domains requiring direct caller migration;
- missing domain test categories;
- P0, P1, P2 and P3 findings.

## 24. Final response

After creating the report, stop.

Respond with only:

1. Audit-16 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Implemented-domain and active-path counts
6. Generic typed, information-loss, bypass and legacy-path counts
7. Inline factual-logic duplicate count
8. Status, evidence, error and trace-discard counts
9. Missing-capability-to-negative-evidence count
10. Scoring-regression-risk count
11. Mutation, raw-source and cache-risk counts
12. Domains requiring direct migration
13. Missing test-category count
14. Number of P0, P1, P2 and P3 findings
15. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-17.