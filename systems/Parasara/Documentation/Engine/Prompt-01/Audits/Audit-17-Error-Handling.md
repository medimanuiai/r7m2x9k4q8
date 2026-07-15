# Prompt-01 — Audit-17: Error-Handling Audit

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

If an expected report is missing:

- record it as a limitation;
- continue if Audit-17 can still be completed reliably;
- do not recreate or modify it;
- return `BLOCKED` only when the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-17: Error-Handling Audit**.

Find every predicate-related error-handling path across the repository and determine whether errors are:

- represented by typed, stable models;
- classified consistently;
- distinguished from unmatched results and missing capabilities;
- preserved across predicate, condition, Yoga and domain boundaries;
- converted safely from exceptions;
- free of raw stack traces and uncontrolled exception details;
- deterministic and JSON-safe;
- compatible with strict development behavior and safe production behavior.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Architectural error boundary

Prompt-01 requires factual outcomes to remain distinct:

```text
Valid fact is true                 → matched
Valid fact is false                → unmatched
Parameters are invalid             → invalid_parameters
Required capability is unavailable → missing_capability
Unexpected predicate failure       → error
Evaluation exceeds allowed time    → timeout
Branch is not evaluated            → skipped
```

An exception, invalid parameter, unknown predicate or missing capability must not silently become an ordinary non-match.

Use Prompt-01 as authoritative if its exact statuses or fields differ.

## 4. Repository-wide discovery

Search production code, tests, fixtures, scripts, rule loaders, Yoga, domains, inference, output and documentation.

Find every predicate-related:

- `try/except`;
- `raise`;
- assertion;
- error dictionary;
- typed error construction;
- error-code enum or constant;
- exception-to-result conversion;
- error aggregation;
- swallowed exception;
- logging call;
- traceback handling;
- unknown predicate path;
- unknown operator path;
- invalid return-type path;
- timeout path;
- strict-mode path.

Search especially for patterns such as:

```python
except Exception:
    pass
```

```python
except Exception:
    continue
```

```python
except Exception as exc:
    return False
```

```python
except Exception as exc:
    return PredicateResult(matched=False, ...)
```

```python
errors=[{"error": str(exc)}]
```

Treat search matches as candidates. Inspect context before classifying them as predicate-related.

## 5. Error-handling path inventory

For every relevant error path, report:

1. File and symbol.
2. Line number or small line range.
3. Architectural layer.
4. Predicate, condition, Yoga, domain or caller involved.
5. Exception scope.
6. Expected or unexpected failure.
7. Current fallback.
8. Current result status.
9. Whether the exception is swallowed.
10. Whether raw exception text is exposed.
11. Whether a stack trace is logged or returned.
12. Whether evidence is preserved.
13. Whether predicate identity is preserved.
14. Whether recoverability is represented.
15. Whether strict mode exists.
16. Whether the outcome becomes unmatched.
17. Active-path status.
18. Existing tests.
19. Required Prompt-01 migration.

## 6. Typed error-model assessment

Reconcile with Audit-6 and verify current code.

Determine whether a canonical `PredicateError` or equivalent exists and whether it supports:

- stable `code`;
- safe `message`;
- `predicate_id`;
- immutable structured `details`;
- `recoverable` classification;
- deterministic serialization;
- JSON-safe values.

Identify every remaining dictionary, string, tuple or exception object used as a predicate error.

Do not implement the model.

## 7. Error-code inventory

Inventory all existing predicate-related error codes, aliases and ad hoc reason strings.

Assess support for these candidate categories:

- `INVALID_PARAMETERS`
- `MISSING_CAPABILITY`
- `MISSING_PLANET`
- `MISSING_HOUSE`
- `MISSING_VARGA`
- `MISSING_ASPECT_GRAPH`
- `UNKNOWN_REFERENCE`
- `UNKNOWN_PREDICATE`
- `UNKNOWN_OPERATOR`
- `INVALID_RETURN_TYPE`
- `PREDICATE_EXCEPTION`
- `PREDICATE_TIMEOUT`

These are audit candidates, not instructions to implement all codes.

For each code or reason, document:

- definition location;
- producers;
- consumers;
- serialized value;
- stability;
- duplicates or aliases;
- recoverability;
- Prompt-01 requirement or unresolved status.

## 8. Exception classification

Classify each caught or raised exception as:

- `EXPECTED_INPUT_ERROR`
- `EXPECTED_MISSING_DATA`
- `EXPECTED_MISSING_CAPABILITY`
- `RULE_DEFINITION_ERROR`
- `CONTRACT_VIOLATION`
- `UNEXPECTED_PROGRAMMING_ERROR`
- `TIMEOUT_OR_CANCELLATION`
- `INFRASTRUCTURE_ERROR`
- `UNKNOWN`

Determine whether current handling matches the classification.

Do not use a broad exception classification without inspecting the protected code and caller behavior.

## 9. Predicate evaluator error handling

Audit the generic predicate evaluator for:

- unknown predicate IDs;
- invalid parameters;
- handler exceptions;
- unexpected return types;
- legacy tuple conversion failures;
- capability failures;
- cache-key construction failures;
- serialization failures;
- timeouts;
- strict versus production behavior.

Determine whether every path returns or raises the correct typed contract and whether errors are mistakenly converted into `matched=False` without an error status.

## 10. Condition evaluator error handling

Audit how `AND`, `OR`, `NOT` and predicate leaves handle child errors.

Determine whether errors are:

- preserved;
- aggregated deterministically;
- swallowed;
- converted to unmatched;
- overridden by another child;
- lost during short-circuiting;
- associated with the correct child node;
- represented for skipped branches.

Record unresolved precedence scenarios rather than inventing rules.

Examples include:

```text
AND(unmatched, error)
OR(error, matched)
OR(error, unmatched)
NOT(error)
```

## 11. Rule loader and compiler errors

Audit error handling for:

- malformed YAML or JSON;
- invalid condition shape;
- unknown predicate;
- unknown operator;
- duplicate IDs;
- invalid predicate version;
- invalid parameters;
- missing registry initialization;
- unsupported capabilities.

Determine whether errors are rejected at load/compile time or deferred until runtime and converted into non-matches.

Reconcile with Audit-14.

## 12. Yoga error handling

Audit every Yoga path for:

- swallowed predicate errors;
- tuple helpers returning false after exceptions;
- ignored error lists;
- missing capability treated as Yoga non-match;
- raw exception exposure;
- enrichment failures;
- mutation occurring before failure;
- partial Yoga results after error.

Reconcile with Audit-15.

## 13. Domain runtime error handling

Audit Career and every other implemented domain for:

- errors treated as zero score;
- errors treated as unmatched indicators;
- missing capability treated as negative evidence;
- ignored error details;
- public exposure of internal errors;
- partial scoring after failures;
- confidence changes caused by unavailable data;
- domain-specific fallback evaluators.

Reconcile with Audit-16.

## 14. Cache-related errors

Determine how the predicate cache handles:

- key-construction errors;
- unserializable parameters;
- cached error results;
- cached timeout results;
- cached missing-capability results;
- partial writes;
- corrupted entries;
- retrieval exceptions;
- stale failures after dependencies recover.

Identify sticky-error risks without redesigning cache policy.

## 15. Raw exception and sensitive-data exposure

Find every use of:

- `str(exception)`;
- `repr(exception)`;
- traceback strings;
- raw parameters in errors;
- raw input payloads;
- filesystem paths;
- environment values;
- provider responses.

Determine whether these enter:

- `PredicateResult`;
- evidence;
- traces;
- logs;
- snapshots;
- API responses;
- public JSON.

Do not reproduce secrets or sensitive values in the audit report. If a secret is discovered, identify only the file and secret type and mark it urgent.

## 16. Logging and observability

Inventory predicate-related logging of errors and exceptions.

Determine whether logging:

- uses stable error codes;
- includes predicate identity;
- includes trace or run identity;
- logs stack traces only in appropriate internal contexts;
- duplicates errors returned in results;
- changes deterministic output;
- leaks sensitive values;
- silently replaces typed error propagation.

Do not change logging.

## 17. Strict development mode

Determine whether a strict mode exists that can surface programming errors such as:

- invalid handler return type;
- duplicate registration;
- missing metadata;
- impossible status/matched combinations;
- invalid internal condition nodes;
- unexpected exceptions.

Document:

- activation mechanism;
- default behavior;
- production behavior;
- test coverage;
- whether strictness depends on environment variables;
- whether behavior is deterministic.

Do not implement strict mode.

## 18. Recoverability and retry semantics

Determine whether errors are classified as recoverable and whether callers act on that classification.

Audit:

- retries;
- fallback evaluation;
- enrichment preparation followed by retry;
- timeout retry;
- cache invalidation after recovery;
- permanent rule-definition errors;
- transient infrastructure errors.

Identify implicit retries or fallbacks that may change logical behavior.

## 19. Determinism and ordering

Determine whether error behavior is deterministic across repeated runs.

Inspect:

- error ordering;
- set or dictionary iteration;
- exception message variability;
- filesystem paths;
- process IDs;
- timestamps;
- UUIDs;
- timing values;
- cache warmth;
- parallel evaluation.

Separate logical error identity from runtime diagnostic telemetry.

## 20. Serialization and public-schema impact

Find every serializer or output path for predicate errors.

Assess whether typed immutable errors could affect:

- `dataclasses.asdict`;
- `json.dumps`;
- Pydantic serialization;
- snapshots;
- debug output;
- API responses;
- public schema versions;
- field ordering.

Do not update serializers or snapshots.

## 21. Test inventory and gap analysis

Locate tests covering:

### Predicate errors

- invalid parameters;
- missing capability;
- unknown predicate;
- handler exception;
- invalid return type;
- timeout;
- safe message;
- stable code;
- predicate identity;
- immutable details;
- recoverability.

### Propagation

- predicate to condition;
- condition to Yoga;
- condition to domain;
- error aggregation;
- short-circuit behavior;
- child identity;
- evidence and trace preservation.

### Safety

- no raw stack traces in results;
- no secret or raw-payload exposure;
- JSON-safe details;
- deterministic serialization;
- public-output filtering.

### Cache and strict mode

- errors are not incorrectly sticky;
- invalid return type fails in strict mode;
- production conversion is typed and safe;
- cache warmth does not change logical error identity.

For every missing test category:

- identify the gap;
- explain its risk;
- recommend the likely test file;
- do not create the test.

## 22. Required classifications

Classify handling behavior as:

- `TYPED_AND_PRESERVED`
- `TYPED_WITH_INFORMATION_LOSS`
- `UNTYPED_BUT_PRESERVED`
- `CONVERTED_TO_UNMATCHED`
- `SWALLOWED`
- `RAW_EXCEPTION_EXPOSED`
- `RAISED_TO_CALLER`
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

## 23. Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- symbol name;
- line number or small range when practical;
- architectural layer;
- exception or error category;
- current fallback and result;
- whether the error becomes unmatched;
- evidence, status and trace impact;
- active-path evidence;
- existing tests;
- uncertainty where static analysis cannot prove runtime behavior.

Reconcile findings with Audits 1–16. Explain discrepancies and newly discovered paths without modifying earlier reports.

## 24. Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify rules;
- modify previous audit reports;
- create error models or codes;
- change exception handling;
- change logging;
- implement strict mode;
- change retry or cache policies;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-18.

You may run safe, non-mutating searches and tests.

Do not execute commands that update files, snapshots or generated artifacts.

## 25. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-17-Error-Handling.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker rather than selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-17: Error Handling

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–16
## 4. Error-Handling Path Inventory
## 5. Typed Error-Model Assessment
## 6. Error-Code Inventory
## 7. Exception Classification
## 8. Predicate Evaluator Error Handling
## 9. Condition Evaluator Error Handling
## 10. Rule Loader and Compiler Errors
## 11. Yoga Error Handling
## 12. Domain Runtime Error Handling
## 13. Cache-Related Errors
## 14. Raw Exception and Sensitive-Data Exposure
## 15. Logging and Observability
## 16. Strict Development Mode
## 17. Recoverability and Retry Semantics
## 18. Determinism and Error Ordering
## 19. Serialization and Public-Schema Impact
## 20. Existing Tests and Coverage Gaps
## 21. Prompt-01 Compliance Matrix
## 22. Migration Risks and Priorities
## 23. Unresolved Architectural Questions
## 24. Audit-17 Conclusion
```

### Error-handling inventory

| File | Symbol | Layer | Predicate/Caller | Exception Scope | Classification | Current Fallback | Result Status | Swallowed | Raw Text Exposed | Stack Trace | Evidence Preserved | Recoverable | Strict Mode | Active Path | Tests | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Error-code inventory

| Code/Reason | Defined At | Representation | Producers | Consumers | Stable | Recoverable | Serialized | Duplicate/Alias | Prompt-01 Status | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Propagation matrix

| Error Source | Predicate Result | Condition Handling | Yoga Handling | Domain Handling | Output Handling | Status Preserved | Error Preserved | Evidence Preserved | Trace Preserved | Information Lost | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|

### Raw-exposure inventory

| File | Symbol | Exposed Value Type | Destination | Internal/Public | Sensitive Risk | Stack Trace Risk | Current Protection | Required Action | Priority |
|---|---|---|---|---|---|---|---|---|---|

### Compliance matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- predicate-related error paths;
- typed and preserved paths;
- typed paths with information loss;
- untyped error paths;
- errors converted to unmatched;
- swallowed exceptions;
- raw exception exposures;
- stack-trace exposure risks;
- missing stable error codes;
- unknown-predicate incorrect paths;
- unknown-operator incorrect paths;
- invalid-return-type gaps;
- missing timeout handling paths;
- sticky cache-error risks;
- Yoga error-loss paths;
- domain error-loss paths;
- strict-mode gaps;
- nondeterministic error mechanisms;
- public serialization impacts;
- missing error-handling test categories;
- P0, P1, P2 and P3 findings.

## 26. Final response

After creating the report, stop.

Respond with only:

1. Audit-17 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Predicate-related error-path count
6. Typed, untyped, converted-to-unmatched and swallowed counts
7. Raw-exception and stack-trace exposure-risk counts
8. Missing stable-code and invalid-return-type gap counts
9. Yoga and domain error-loss counts
10. Sticky-cache-error and strict-mode gap counts
11. Nondeterministic error-mechanism count
12. Public serialization-impact count
13. Missing test-category count
14. Number of P0, P1, P2 and P3 findings
15. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-18.