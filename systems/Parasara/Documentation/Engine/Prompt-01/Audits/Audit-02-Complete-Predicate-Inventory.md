# Prompt-01 — Audit-2: Complete Predicate Inventory

You are auditing the Jyothishyam repository before implementing Prompt-01.

Audit-1 (Predicate Registry Audit) is complete. Read its report first:

systems\Parasara\Documentation\Engine\Prompt-01\Reports\Audit-01-Predicate-Registry.md

Also read these authoritative documents:

1. Jyothishyam Master Architecture Specification v1.0
2. Prompt-01

Locate them by filename if necessary.

## Objective

Perform only Audit-2: Complete Predicate Inventory.

Build an evidence-based inventory of every registered predicate and every predicate-like function in the repository.

This is a read-only audit. Do not implement fixes.

## Repository-wide search

Search the complete repository, including:

- Python source files;
- tests and fixtures;
- YAML and JSON rule files;
- scripts and utilities;
- domain engines;
- Yoga code;
- rule loaders and evaluators;
- documentation where relevant.

Do not rely only on registry contents or known filenames.

Search for:

- registered predicate handlers;
- registration decorators and function calls;
- functions returning `PredicateResult`;
- functions returning predicate-like tuples or booleans;
- condition-evaluation helpers;
- Yoga-specific predicate helpers;
- domain-specific factual checks;
- direct predicate-ID comparisons;
- dynamically constructed predicate IDs;
- test-only predicates;
- aliases and duplicate implementations;
- unreachable or apparently unused predicate code.

## Required findings

For every registered predicate, report:

1. Canonical predicate ID.
2. Aliases and case variants.
3. Registration location.
4. Handler file and symbol.
5. Handler signature.
6. Current return contract.
7. Predicate version, if any.
8. Parameter names, types, defaults and validation.
9. Required AstroState capabilities or enrichments.
10. Evidence produced for matched results.
11. Evidence produced for unmatched results.
12. Error behavior.
13. Trace support.
14. Purity and determinism.
15. Cache eligibility and current cache use.
16. Known callers.
17. Existing tests.
18. Prompt-01 compliance status.
19. Migration priority.

Also identify every predicate-like helper that is not registered, including:

- tuple-return factual checks;
- boolean-return factual checks;
- duplicate predicate implementations;
- Yoga-specific evaluators;
- domain-specific factual helpers;
- legacy or compatibility functions;
- test-only predicate handlers.

For each predicate-like helper, determine:

- whether it duplicates a registered predicate;
- whether it is on an active execution path;
- confirmed callers;
- whether it should be migrated, preserved temporarily or treated as outside Prompt-01;
- whether its apparent lack of callers was verified.

## Predicate boundary

Use this architectural rule:

A predicate answers a factual astrological question.

Predicates must not:

- calculate domain scores;
- assign rule weights;
- calculate confidence;
- resolve conflicts;
- generate narratives;
- construct public JSON;
- mutate AstroState;
- access raw Surya Siddhanta JSON;
- call external services;
- read system time.

Flag violations, but do not fix them.

Do not classify logical operators such as `AND`, `OR` and `NOT` as registered factual predicates. Record them separately if the current implementation treats them as predicates.

## Compliance classification

For each predicate, use one status:

- IMPLEMENTED
- PARTIAL
- MISSING
- NONCOMPLIANT
- UNKNOWN

Use these priorities:

- P0 — Blocks safe Prompt-01 implementation
- P1 — Required for Prompt-01 completion
- P2 — Important compatibility or quality concern
- P3 — Later-stage or nonblocking concern

Use these scope classifications:

- IN_SCOPE
- TEMPORARY_COMPATIBILITY
- OUT_OF_SCOPE_FUTURE_STAGE
- UNRELATED

## Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- symbol name;
- line number or small line range when practical;
- confirmed registration or caller evidence;
- concise explanation;
- uncertainty where static analysis cannot confirm behavior.

Do not claim that code is unused without searching for:

- direct callers;
- imports;
- registry references;
- string-based dispatch;
- dynamic lookup;
- tests and fixtures.

Do not change astrology semantics. Flag suspected semantic errors for later review.

## Scope restrictions

Do not:

- modify production code;
- modify tests;
- modify rule files;
- register or migrate predicates;
- remove legacy helpers;
- refactor implementations;
- update snapshots;
- run formatters;
- commit or push;
- begin Audit-3.

You may run safe, non-mutating searches and tests. Do not execute commands that update files or generated artifacts.

## Deliverable

Create exactly one file:

systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-02-Complete-Predicate-Inventory.md

If `systems/Parasara/Documentation/Engine/Prompt-01/Reports` does not exist, stop and report the blocker.

Do not modify Audit-1 or any other file.

Use this structure:

# Prompt-01 Audit-02: Complete Predicate Inventory

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Inventory Reconciliation with Audit-1
## 4. Complete Registered Predicate Inventory
## 5. Predicate Aliases and ID Variants
## 6. Unregistered Predicate-Like Helpers
## 7. Duplicate Predicate Implementations
## 8. Test-Only and Dynamically Registered Predicates
## 9. Predicate Boundary Violations
## 10. Caller and Active-Path Summary
## 11. Prompt-01 Compliance Assessment
## 12. Migration Priorities and Risks
## 13. Unresolved Questions
## 14. Audit-2 Conclusion

### Registered predicate inventory

Include these columns:

Predicate ID | Aliases | File | Handler | Signature | Return Contract | Version | Status Support | Parameters | Required Capabilities | Evidence Quality | Trace Support | Purity | Cacheable | Callers | Tests | Compliance | Scope | Priority

### Predicate-like helper inventory

Include these columns:

File | Symbol | Function Type | Return Contract | Duplicates Predicate | Confirmed Callers | Active Path | Registration Status | Migration Required | Scope | Risk | Priority

### Inventory summary

Include counts for:

- registered predicates;
- aliases;
- test-only predicates;
- unregistered predicate-like helpers;
- tuple-return helpers;
- boolean-return helpers;
- duplicate implementations;
- predicates without tests;
- predicates without versions;
- predicates without parameter validation;
- predicates lacking unmatched evidence;
- predicates lacking trace support;
- predicates with suspected purity violations;
- predicates whose active-path status remains unknown.

Reconcile the registered-predicate count with Audit-1. Explain every difference.

## Final response

After creating the report, stop.

Respond with only:

1. Audit-2 status: COMPLETE or BLOCKED
2. Report file path
3. Files modified
4. Tests or commands executed
5. Registered predicate count
6. Predicate-like helper count
7. Duplicate implementation count
8. Number of P0, P1, P2 and P3 findings
9. Any blocker or unresolved architectural question

Do not implement corrections and do not proceed to Audit-3.
