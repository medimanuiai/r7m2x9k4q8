# Prompt-01 — Audit-3: Legacy Return-Contract Search

You are auditing the Jyothishyam repository before implementing Prompt-01.

Audits 1 and 2 are complete. Read their reports first:

- systems\Parasara\Documentation\Engine\Prompt-01\Reports\Audit-01-Predicate-Registry.md
- systems\Parasara\Documentation\Engine\Prompt-01\Reports\Audit-02-Complete-Predicate-Inventory.md

Also read these authoritative documents:

1. Jyothishyam Master Architecture Specification v1.0
2. Prompt-01

Locate the authoritative documents by filename if necessary.

## Objective

Perform only Audit-3: Legacy Return-Contract Search.

Find every predicate or predicate-like execution path that still returns, accepts, converts, forwards or tuple-unpacks legacy values instead of using the required typed result contract.

This is a repository-wide, read-only audit. Do not implement fixes.

## Canonical boundary

Prompt-01 requires factual predicate handlers to return `PredicateResult`.

Search for legacy contracts such as:

- `Tuple[bool, Dict]`;
- `tuple[bool, dict]`;
- `(matched, evidence)`;
- `(bool, evidence)`;
- raw `bool`;
- raw evidence dictionaries;
- `None` used as a predicate result;
- dictionaries shaped like predicate results;
- arbitrary objects converted into `PredicateResult`;
- compatibility branches accepting tuples or booleans;
- callers that tuple-unpack predicate output;
- callers that use only truthiness or `.matched`;
- adapters that discard errors, evidence, status, versions or traces.

Logical condition nodes may require a separate `ConditionResult`. Do not automatically classify logical operators as factual predicates.

## Repository-wide search

Search the complete repository, including:

- predicate modules;
- predicate registry and evaluator;
- condition evaluator;
- rule engine and loaders;
- Yoga Engine;
- Career and other domains;
- inference and output layers;
- tests and fixtures;
- scripts and utilities;
- YAML/JSON-related runtime adapters;
- type annotations and documentation examples.

Do not rely only on the symbols found by Audits 1 and 2.

Search for patterns including, but not limited to:

- `Tuple[bool`;
- `tuple[bool`;
- `return True`;
- `return False`;
- `return ok,`;
- `return matched,`;
- `ok, evidence =`;
- `matched, evidence =`;
- `isinstance(..., tuple)`;
- `isinstance(..., bool)`;
- `bool(result)`;
- `if result:`;
- `result[0]` and `result[1]`;
- `.matched`;
- dictionaries containing keys such as `matched`, `evidence` or `errors`;
- compatibility adapters around `evaluate_predicate` or `evaluate_condition`.

Use search results as candidates. Inspect context before classifying anything as predicate-related.

## Required findings

For every legacy contract occurrence, report:

1. File path and symbol.
2. Relevant line number or small line range.
3. Whether it is a producer, consumer, adapter or test.
4. Actual return or expected input type.
5. Whether it represents a factual predicate, logical condition or unrelated boolean logic.
6. Confirmed callers or downstream consumers.
7. Whether it is on an active production path.
8. Evidence handling.
9. Error handling.
10. Trace handling.
11. Status and predicate-version preservation.
12. Whether information is lost during conversion.
13. Whether the path bypasses the central predicate registry.
14. Whether it duplicates another evaluator.
15. Migration requirement and risk.

Pay special attention to:

- the generic evaluator’s tuple compatibility branch;
- Yoga-specific tuple-return helpers;
- condition aggregation;
- domain code that expects booleans;
- tests that preserve legacy behavior;
- annotations that still advertise tuple contracts;
- compatibility wrappers that appear unused.

## Classification

Classify every candidate by pattern:

- LEGACY_TUPLE_PRODUCER
- LEGACY_TUPLE_CONSUMER
- RAW_BOOLEAN_PRODUCER
- RAW_BOOLEAN_CONSUMER
- DICTIONARY_RESULT_CONTRACT
- COMPATIBILITY_ADAPTER
- TYPED_RESULT_WITH_INFORMATION_LOSS
- LOGICAL_CONDITION_CONTRACT
- TEST_ONLY_LEGACY_CONTRACT
- FALSE_POSITIVE_OR_UNRELATED

Classify its execution status as:

- ACTIVE_PRODUCTION_PATH
- ACTIVE_TEST_PATH_ONLY
- DORMANT_BUT_REFERENCED
- CONFIRMED_UNUSED
- UNKNOWN

Do not use `CONFIRMED_UNUSED` without repository-wide caller and reference evidence.

Classify migration scope as:

- IN_SCOPE
- TEMPORARY_COMPATIBILITY
- OUT_OF_SCOPE_FUTURE_STAGE
- UNRELATED

Use priorities:

- P0 — Blocks safe Prompt-01 implementation
- P1 — Required for Prompt-01 completion
- P2 — Important compatibility or quality concern
- P3 — Later-stage or nonblocking concern

## Architectural requirements

Assess the repository against these Prompt-01 requirements:

- all factual predicates return `PredicateResult`;
- active tuple-return predicate paths are eliminated;
- active callers do not tuple-unpack predicate results;
- raw booleans are not used as predicate contracts;
- unexpected handler return types are handled as typed errors or rejected in strict mode;
- compatibility adapters are isolated and explicitly deprecated;
- compatibility conversion preserves evidence and errors where possible;
- Yoga does not retain a parallel predicate contract;
- logical operators are separated from predicate-leaf results;
- status, errors, evidence, trace and predicate version are preserved end-to-end.

## Evidence requirements

Every substantive finding must provide:

- repository-relative file path;
- symbol name;
- line number or small range when practical;
- observed contract;
- caller/reference evidence;
- reason for classification;
- uncertainty where static analysis cannot prove runtime usage.

Reconcile findings with Audits 1 and 2. Explain new discoveries or disagreements.

## Scope restrictions

Do not:

- modify production code;
- modify tests;
- modify rule files;
- change annotations;
- remove adapters;
- migrate callers;
- update snapshots;
- run formatters;
- commit or push;
- begin Audit-4.

You may run safe, non-mutating searches and tests. Do not run commands that update files or generated artifacts.

## Deliverable

Create exactly one file:

systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-03-Legacy-Return-Contracts.md

If `systems/Parasara/Documentation/Engine/Prompt-01/Reports` does not exist, stop and report the blocker.

Do not modify either previous audit report or any other file.

Use this structure:

# Prompt-01 Audit-03: Legacy Return Contracts

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1 and 2
## 4. Legacy Tuple Producers
## 5. Legacy Tuple Consumers
## 6. Raw Boolean Predicate Contracts
## 7. Dictionary and Ad Hoc Result Contracts
## 8. Compatibility Adapters
## 9. Information-Loss Boundaries
## 10. Yoga Legacy Contracts
## 11. Condition Evaluator Contracts
## 12. Domain and Rule-Engine Consumers
## 13. Test-Only and Dormant Legacy Paths
## 14. False Positives and Excluded Findings
## 15. Prompt-01 Compliance Assessment
## 16. Migration Risks and Priorities
## 17. Unresolved Questions
## 18. Audit-3 Conclusion

### Legacy contract inventory

Include these columns:

File | Symbol | Role | Pattern | Actual Contract | Expected Contract | Callers | Execution Status | Evidence Preserved | Errors Preserved | Trace Preserved | Version Preserved | Registry Bypass | Migration Required | Scope | Priority | Risk

### Caller migration inventory

Include these columns:

File | Symbol | Called API | Current Expectation | Consumption Pattern | Information Lost | Active Path | Required Migration | Priority

### Summary counts

Include counts for:

- tuple producers;
- tuple consumers;
- raw-boolean producers;
- raw-boolean consumers;
- dictionary/ad hoc result contracts;
- compatibility adapters;
- information-loss boundaries;
- active production legacy paths;
- test-only paths;
- confirmed-unused paths;
- unknown-usage paths;
- P0, P1, P2 and P3 findings.

## Final response

After creating the report, stop.

Respond with only:

1. Audit-3 status: COMPLETE or BLOCKED
2. Report file path
3. Files modified
4. Tests or commands executed
5. Legacy tuple producer count
6. Legacy tuple consumer count
7. Raw-boolean contract count
8. Compatibility adapter count
9. Active production legacy-path count
10. Number of P0, P1, P2 and P3 findings
11. Any blocker or unresolved architectural question

Do not implement corrections and do not proceed to Audit-4.
