# Prompt-01 — Audit-12: Condition Evaluator Audit

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
- `Audit-11-Predicate-Cache.md`

If an expected report is missing:

- record it as a limitation;
- continue if Audit-12 can still be completed reliably;
- do not recreate or modify the missing report;
- return `BLOCKED` only if the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-12: Condition Evaluator Audit**.

Determine how the repository evaluates condition trees containing predicate leaves and logical operators.

Audit:

- the generic condition evaluator;
- every alternate or legacy condition evaluator;
- predicate-leaf delegation;
- result types;
- `AND`, `OR` and `NOT` semantics;
- status, evidence, error and trace preservation;
- short-circuit behavior;
- skipped-branch representation;
- evaluation order;
- unknown operator handling;
- unknown predicate handling;
- condition-result caching;
- compatibility with Prompt-01 and future `RuleMatch`.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Architectural boundary

Use this boundary:

```text
Predicate leaf
    → Generic Predicate Evaluator
    → PredicateResult

Logical condition tree
    → Generic Condition Evaluator
    → ConditionResult or equivalent internal result
```

Logical operators such as `AND`, `OR` and `NOT` are not factual predicates.

The condition evaluator must not falsely represent logical nodes as registered predicates merely to reuse `PredicateResult`.

Prompt-01 permits or requires an internal typed bridge such as `ConditionResult` where necessary to preserve:

- child predicate results;
- child condition results;
- status;
- matched outcome;
- evidence;
- errors;
- trace steps;
- evaluation order;
- short-circuit behavior;
- skipped branches.

Use Prompt-01 as authoritative if its terminology differs.

Do not implement Prompt-02 `RuleMatch` during this audit.

## 4. Repository-wide discovery

Search the complete repository for:

- `evaluate_condition`;
- `_eval_condition`;
- `eval_condition`;
- condition evaluator classes;
- recursive condition processing;
- `AND`, `OR` and `NOT`;
- operator dispatch;
- predicate-leaf detection;
- Yoga-specific evaluators;
- domain-specific condition evaluators;
- tuple-return condition helpers;
- raw-boolean aggregation;
- `all(...)`;
- `any(...)`;
- short-circuit loops;
- child result lists;
- skipped results;
- condition traces;
- condition-result models;
- unknown-operator fallbacks;
- direct predicate registry calls.

Search production code, tests, fixtures, YAML, JSON, scripts and documentation.

Treat matches as candidates. Inspect context before classifying them.

## 5. Condition evaluator inventory

Identify every function, method or class that evaluates condition nodes or condition trees.

For each evaluator, report:

1. File and symbol.
2. Input contract.
3. Supported condition shapes.
4. Supported operators.
5. Predicate-leaf representation.
6. Predicate dispatch mechanism.
7. Return contract.
8. Recursive behavior.
9. Short-circuit behavior.
10. Evidence handling.
11. Error handling.
12. Status handling.
13. Trace handling.
14. Child-result preservation.
15. Cache behavior.
16. Callers.
17. Active-path status.
18. Existing tests.
19. Relationship to other evaluators.

Classify each evaluator as:

- `CANONICAL_GENERIC_EVALUATOR`
- `LEGACY_GENERIC_EVALUATOR`
- `YOGA_SPECIFIC_EVALUATOR`
- `DOMAIN_SPECIFIC_EVALUATOR`
- `TEST_ONLY_EVALUATOR`
- `UTILITY_OR_WRAPPER`
- `UNKNOWN`

## 6. Canonical evaluator determination

Determine which evaluator is intended to be canonical.

Report:

- evidence that it is canonical;
- production callers;
- registry integration;
- rule-loader integration;
- Yoga integration;
- domain integration;
- whether alternate evaluators bypass it;
- whether duplicate implementations remain active;
- whether import order affects which evaluator is used.

Do not claim an evaluator is unused without repository-wide caller evidence.

## 7. Condition input contract

For every active evaluator, document accepted condition-node structures.

Examples may include:

```yaml
type: AND
children: []
```

```yaml
predicate: PLANET_IN_HOUSE
params:
  planet: Mars
  house: 10
```

Other possible forms include:

```yaml
condition: {}
```

```yaml
conditions: []
```

```yaml
op: AND
args: []
```

Determine:

- required keys;
- optional keys;
- aliases;
- case sensitivity;
- parameter nesting;
- child nesting;
- empty-node behavior;
- malformed-node behavior;
- unknown-field behavior;
- loader normalization;
- runtime normalization;
- whether raw YAML dictionaries reach the evaluator.

Do not perform the complete condition-format inventory assigned to Audit-13. Record only formats necessary to understand evaluator behavior.

## 8. Predicate-leaf delegation

Determine how each evaluator recognizes and evaluates a predicate leaf.

Audit whether it:

- calls `evaluate_predicate(...)`;
- directly resolves the registry;
- calls a registered handler directly;
- calls a legacy tuple-return helper;
- contains duplicate predicate logic;
- treats unknown predicates as unmatched;
- preserves `PredicateResult`;
- converts it to a tuple or raw boolean;
- discards evidence, errors, status or traces.

For every dispatch path, report:

1. Evaluator.
2. Predicate-leaf shape.
3. Called API or handler.
4. Return contract received.
5. Conversion performed.
6. Information lost.
7. Unknown-predicate behavior.
8. Active callers.
9. Prompt-01 compliance.

## 9. Return-contract audit

Determine the return type used for:

- predicate leaves;
- `AND`;
- `OR`;
- `NOT`;
- malformed conditions;
- unknown operators;
- empty condition trees;
- short-circuited branches.

Identify whether active evaluators return:

- `PredicateResult`;
- `ConditionResult`;
- tuple;
- raw boolean;
- dictionary;
- `None`;
- mixed types.

Pay special attention to logical nodes constructed as:

```python
PredicateResult(predicate_id="AND", ...)
```

or:

```python
PredicateResult(predicate_id="OR", ...)
```

Determine whether this incorrectly treats logical operators as predicates.

Assess whether an existing `ConditionResult` or equivalent model exists and whether it can preserve nested results.

Do not implement the model.

## 10. AND semantics

For every `AND` implementation, determine:

- child evaluation order;
- empty-child behavior;
- short-circuit behavior;
- result when all children match;
- result when one child is unmatched;
- result when one child has invalid parameters;
- result when one child has missing capability;
- result when one child has an error;
- result when one child times out;
- result when one child is skipped;
- whether remaining children are evaluated;
- whether skipped branches are represented;
- evidence aggregation;
- error aggregation;
- trace aggregation;
- child-result preservation.

Prompt-01 requires deterministic short-circuit behavior. Verify the exact authoritative semantics.

Do not invent status-precedence rules when the documents are unclear. Record them as unresolved decisions.

## 11. OR semantics

For every `OR` implementation, determine:

- child evaluation order;
- empty-child behavior;
- short-circuit behavior;
- result when the first child matches;
- result when all children are unmatched;
- result when one child has missing capability;
- result when one child has invalid parameters;
- result when one child errors;
- whether a later matched child overrides an earlier error;
- whether remaining children are skipped;
- skipped-branch representation;
- evidence aggregation;
- error aggregation;
- trace aggregation;
- child-result preservation.

Record ambiguous status-precedence behavior as an architectural question.

## 12. NOT semantics

Determine whether `NOT` is currently implemented.

If implemented, report:

- accepted node shape;
- required child count;
- behavior with zero children;
- behavior with multiple children;
- match inversion;
- status transformation;
- missing-capability behavior;
- invalid-parameter behavior;
- error behavior;
- timeout behavior;
- skipped behavior;
- evidence preservation;
- error preservation;
- trace preservation;
- child-result preservation.

A non-match may be logically inverted, but missing capability or error must not automatically become positive evidence.

If `NOT` is absent, document all callers or rules that require it.

## 13. Short-circuit and skipped-branch audit

Determine whether active evaluators implement:

```text
AND → stop on the first result that determines failure
OR  → stop on the first result that determines success
```

For every implementation, report:

- whether short-circuiting occurs;
- exact stopping condition;
- whether status affects stopping;
- evaluation order;
- whether unevaluated children are omitted or represented;
- whether skipped branches receive a typed skipped status;
- whether skipped branches appear in traces;
- whether skipped branches produce evidence or errors;
- whether tests verify non-execution.

Identify current loops that evaluate every child before aggregation.

## 14. Status propagation and precedence

Determine how condition evaluation combines child statuses:

- `matched`;
- `unmatched`;
- `missing_capability`;
- `invalid_parameters`;
- `error`;
- `timeout`;
- `skipped`.

Report whether the evaluator:

- preserves statuses;
- converts all non-matches to `False`;
- converts errors to unmatched;
- ignores missing capabilities;
- discards invalid-parameter results;
- uses explicit precedence;
- behaves differently for `AND`, `OR` and `NOT`.

If no authoritative precedence exists, provide concrete unresolved scenarios rather than inventing rules.

Examples:

```text
AND(unmatched, missing_capability)
OR(unmatched, missing_capability)
OR(error, matched)
NOT(missing_capability)
```

## 15. Evidence preservation

Audit whether condition aggregation preserves:

- evidence from matched children;
- evidence from unmatched children;
- expected and actual values;
- missing-capability details;
- error-related factual context;
- child-to-parent relationships;
- deterministic child order.

Identify whether evidence is:

- discarded;
- flattened;
- overwritten;
- merged with key collisions;
- converted to narrative text;
- stored as mutable dictionaries;
- stored without child identity.

Do not design the final evidence schema.

## 16. Error preservation

Determine whether condition evaluation preserves:

- typed predicate errors;
- stable error codes;
- predicate IDs;
- child-node identity;
- recoverability;
- deterministic order.

Find paths where errors are:

- swallowed;
- ignored;
- converted to unmatched;
- replaced with raw exception strings;
- merged incorrectly;
- lost during tuple conversion;
- omitted after short-circuiting.

Reconcile with Audits 3, 4 and 6.

## 17. Trace and child-result preservation

Determine whether the evaluator preserves:

- predicate trace steps;
- nested condition trace steps;
- parent-child relationships;
- evaluation sequence;
- short-circuit decision;
- skipped branches;
- cache-hit information;
- duration fields;
- AST or condition-node references.

Determine whether logical nodes generate:

- deterministic trace identity;
- random UUIDs;
- system-time timestamps;
- nondeterministic duration values.

Assess whether complete child results are preserved or reduced to booleans.

## 18. Unknown operator behavior

Find every path handling an unknown logical operator.

Determine whether it:

- raises a validation error;
- fails during rule loading;
- returns `False`;
- returns unmatched;
- returns a typed error;
- silently treats it as a predicate;
- ignores the node;
- falls through to an unrelated branch.

Unknown operators must not silently become ordinary negative evidence.

Separate:

- load/compile-time behavior;
- direct runtime invocation;
- malformed internal nodes.

## 19. Unknown predicate behavior

Determine how predicate leaves with unknown IDs are handled by:

- rule loaders;
- condition evaluators;
- generic predicate evaluator;
- Yoga evaluator;
- test helpers.

Assess whether unknown predicates:

- fail validation;
- raise;
- return unmatched;
- return invalid parameters;
- return typed errors;
- are ignored.

Unknown predicate IDs are rule-definition or compilation errors, not ordinary factual non-matches.

Reconcile with Audits 1, 3, 4 and 7.

## 20. Empty and malformed condition behavior

Audit behavior for:

- `None`;
- empty dictionary;
- empty list;
- missing operator;
- missing predicate ID;
- missing children;
- empty `AND`;
- empty `OR`;
- `NOT` without a child;
- `NOT` with multiple children;
- non-list children;
- non-dictionary child;
- unknown fields;
- cyclic in-memory condition trees;
- excessive nesting where relevant.

Report current behavior, expected documented behavior and unresolved cases.

Do not expand into a general DSL redesign.

## 21. Alternate and legacy evaluator audit

Identify every alternate evaluator, especially Yoga-specific helpers such as:

```text
_eval_aspect_condition
_eval_functional_role_condition
_eval_house_lords_combination
_eval_house_occupant
_eval_condition
```

For each, determine:

- current return contract;
- supported operators;
- duplicate predicate logic;
- callers;
- active-path status;
- fallback usage;
- information loss;
- whether it bypasses the registry;
- whether removal is required by Prompt-01;
- whether temporary compatibility is necessary.

Do not remove the evaluator.

Audit-15 will examine Yoga comprehensively. Keep this section focused on condition-evaluation contracts.

## 22. Condition caching

Determine whether:

- complete condition results are cached;
- only predicate leaves are cached;
- logical nodes are recomputed;
- child cache hits affect parent output;
- cache telemetry changes condition serialization;
- skipped branches interact with cache;
- evaluation order changes cache population;
- errors or missing-capability results are cached.

Do not redesign caching. Reconcile relevant findings with Audit-11.

## 23. Caller compatibility

Identify active callers that depend on current condition-result behavior.

For each caller, determine whether it expects:

- `PredicateResult`;
- tuple;
- raw boolean;
- `.matched`;
- evidence dictionary;
- complete child results;
- error-free output;
- all children to be evaluated;
- Yoga-specific evidence;
- mutable results.

Pay attention to:

- Yoga matching;
- Career and other domains;
- rule processing;
- inference;
- tests and snapshots.

Prompt-01 must preserve domain scoring and rule-firing behavior unless current behavior is explicitly noncompliant.

Do not migrate callers.

## 24. Test inventory and gap analysis

Locate tests covering:

### Predicate-leaf behavior

- generic evaluator delegation;
- typed `PredicateResult`;
- evidence preservation;
- error preservation;
- trace preservation;
- unknown predicate.

### AND behavior

- all matched;
- first unmatched;
- later unmatched;
- missing capability;
- invalid parameters;
- error;
- short-circuit;
- skipped branches;
- empty children.

### OR behavior

- first matched;
- later matched;
- all unmatched;
- missing capability;
- invalid parameters;
- error followed by match;
- short-circuit;
- skipped branches;
- empty children.

### NOT behavior

- matched child;
- unmatched child;
- missing capability;
- invalid parameters;
- error;
- zero children;
- multiple children.

### Invalid conditions

- unknown operator;
- missing operator;
- malformed children;
- invalid leaf;
- excessive nesting if bounded.

### Integration

- Yoga condition evaluation;
- rule-loader validation;
- domain compatibility;
- cold and warm predicate-cache behavior;
- deterministic repeated evaluation;
- child-result preservation.

For every missing test category:

- identify the gap;
- explain the risk;
- recommend the likely test file;
- do not create the test.

## 25. Required classifications

Classify evaluator contracts as:

- `TYPED_CONDITION_RESULT`
- `PREDICATE_RESULT_FOR_LOGICAL_NODE`
- `LEGACY_TUPLE`
- `RAW_BOOLEAN`
- `MIXED`
- `UNKNOWN`

Classify evaluator status as:

- `CANONICAL`
- `ACTIVE_ALTERNATE`
- `TEMPORARY_COMPATIBILITY`
- `DORMANT_BUT_REFERENCED`
- `CONFIRMED_UNUSED`
- `TEST_ONLY`
- `UNKNOWN`

Do not use `CONFIRMED_UNUSED` without repository-wide caller evidence.

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

## 26. Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- symbol name;
- line number or small range when practical;
- evaluator or operator;
- current input and return contract;
- observed status, evidence, error and trace behavior;
- caller or active-path evidence;
- existing tests;
- uncertainty where static analysis cannot prove runtime behavior.

Reconcile findings with Audits 1–11.

Explain:

- registry dispatch implications from Audit-1;
- predicate inventory implications from Audit-2;
- legacy contract findings from Audit-3;
- caller expectations from Audit-4;
- model dependencies from Audits 5 and 6;
- validation boundaries from Audits 7 and 8;
- AstroState and purity findings from Audits 9 and 10;
- cache interactions from Audit-11.

Do not modify previous reports.

## 27. Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify rule files;
- modify previous audit reports;
- create `ConditionResult`;
- implement `NOT`;
- change short-circuit behavior;
- change status precedence;
- remove legacy evaluators;
- migrate callers;
- change caching;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-13.

You may run safe, non-mutating searches and tests.

Do not execute commands that update files, snapshots or generated artifacts.

## 28. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-12-Condition-Evaluator.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker instead of selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-12: Condition Evaluator

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–11
## 4. Condition Evaluator Inventory
## 5. Canonical Evaluator and Active Paths
## 6. Condition Input Contract
## 7. Predicate-Leaf Delegation
## 8. Return-Contract Assessment
## 9. AND Semantics
## 10. OR Semantics
## 11. NOT Semantics
## 12. Short-Circuit and Skipped Branches
## 13. Status Propagation and Precedence
## 14. Evidence and Error Preservation
## 15. Trace and Child-Result Preservation
## 16. Unknown Operator and Predicate Handling
## 17. Empty and Malformed Conditions
## 18. Alternate and Legacy Evaluators
## 19. Condition Caching
## 20. Caller Compatibility
## 21. Existing Tests and Coverage Gaps
## 22. Prompt-01 Compliance Matrix
## 23. Migration Risks and Priorities
## 24. Unresolved Architectural Questions
## 25. Audit-12 Conclusion
```

### Condition evaluator inventory

Include these columns:

| Evaluator | File | Symbol | Category | Input Contract | Operators | Leaf Dispatch | Return Contract | Short-Circuit | Status | Evidence | Errors | Trace | Child Results | Callers | Active Status | Tests | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Logical-operator behavior matrix

Include these columns:

| Operator | Scenario | Children Evaluated | Current Matched Outcome | Current Status | Evidence Preserved | Errors Preserved | Trace Preserved | Skipped Represented | Required Decision | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|

### Predicate-leaf dispatch inventory

Include these columns:

| Evaluator | Leaf Shape | Called API | Registry Used | Received Contract | Conversion | Information Lost | Unknown Predicate Behavior | Active Callers | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Caller compatibility matrix

Include these columns:

| Caller | File | Called Evaluator | Expected Contract | Boolean/Matched Use | Evidence Use | Error Use | Child-Result Use | All-Children Assumption | Migration Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Compliance matrix

Include these columns:

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- condition evaluators discovered;
- active production evaluators;
- canonical evaluators;
- legacy or alternate evaluators;
- evaluators returning `PredicateResult` for logical nodes;
- tuple or raw-boolean evaluators;
- operators supported;
- missing required operators;
- non-short-circuit paths;
- status-propagation gaps;
- evidence-loss paths;
- error-loss paths;
- trace-loss paths;
- unknown predicates becoming unmatched;
- unknown operators becoming unmatched;
- active callers requiring migration;
- missing condition-evaluator test categories;
- P0, P1, P2 and P3 findings.

## 29. Final response

After creating the report, stop.

Respond with only:

1. Audit-12 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Condition evaluator count
6. Active production evaluator count
7. Supported and missing logical operators
8. Non-short-circuit path count
9. Status, evidence, error and trace-loss counts
10. Logical nodes returning `PredicateResult` count
11. Unknown predicate/operator incorrect-outcome counts
12. Active callers requiring migration
13. Missing test-category count
14. Number of P0, P1, P2 and P3 findings
15. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-13.