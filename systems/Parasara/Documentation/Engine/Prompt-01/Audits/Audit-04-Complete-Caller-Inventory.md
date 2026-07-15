# Prompt-01 — Audit-4: Complete Caller Inventory

You are auditing the Jyothishyam repository before implementing Prompt-01.

Audits 1–3 are complete. Read their reports first:

- systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-01-Predicate-Registry.md
- systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-02-Complete-Predicate-Inventory.md
- systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-03-Legacy-Return-Contracts.md

Also read these authoritative documents:

1. Jyothishyam Master Architecture Specification v1.0
2. Prompt-01

Locate the authoritative documents by filename if necessary.

## Objective

Perform only Audit-4: Complete Caller Inventory.

Identify every caller and consumer of predicates, predicate results, condition evaluators and legacy predicate-like helpers.

Determine what each caller expects and what could break when Prompt-01 introduces the universal immutable `PredicateResult` contract.

This is a repository-wide, read-only audit. Do not implement fixes.

## Repository-wide search

Search all source code, tests, fixtures, scripts and relevant configuration or documentation.

Find every use of:

- registered predicate handlers;
- predicate registry lookup;
- `evaluate_predicate(...)`;
- `evaluate_condition(...)`;
- `PredicateResult`;
- predicate-like helpers identified in Audits 2 and 3;
- Yoga-specific condition evaluators;
- direct calls to predicate handlers;
- dynamic predicate dispatch;
- tuple unpacking of predicate results;
- `.matched`, `.evidence`, `.errors`, `.trace_steps`, `.status`;
- truthiness checks on predicate or condition results;
- predicate-result serialization;
- predicate cache access;
- mocks, monkeypatches and test predicates.

Do not rely only on direct function calls. Check:

- imported aliases;
- re-exports;
- callbacks stored in registries;
- string-based dispatch;
- decorators;
- dynamically retrieved handlers;
- test parametrization;
- fixtures;
- wrappers and adapters.

## Caller categories

Classify each caller as one of:

- REGISTRY_LOOKUP
- GENERIC_PREDICATE_EVALUATOR
- CONDITION_EVALUATOR
- RULE_ENGINE
- RULE_LOADER_OR_COMPILER
- YOGA_ENGINE
- DOMAIN_RUNTIME
- INFERENCE_ENGINE
- OUTPUT_OR_SERIALIZATION
- CACHE_LAYER
- TEST_OR_FIXTURE
- SCRIPT_OR_TOOL
- LEGACY_OR_COMPATIBILITY
- OTHER

## Required findings

For every caller or consumer, report:

1. File path and symbol.
2. Line number or small line range when practical.
3. Called predicate API, handler or helper.
4. Direct, indirect or dynamically resolved call.
5. Current expected return contract.
6. Consumption pattern.
7. Whether it:
   - tuple-unpacks results;
   - checks raw truthiness;
   - reads `.matched`;
   - reads or discards evidence;
   - reads or discards errors;
   - reads or discards status;
   - reads or discards trace steps;
   - depends on predicate version;
   - serializes the result;
   - mutates the result or nested data.
8. Current error and missing-capability behavior.
9. Whether errors are treated as ordinary non-matches.
10. Whether the caller invokes registered predicates directly and bypasses the generic evaluator.
11. Whether the caller recomputes predicate facts.
12. Whether the caller depends on mutable result objects.
13. Whether the caller accesses raw Surya Siddhanta JSON.
14. Whether the caller is on an active production path.
15. Existing tests covering the interaction.
16. Prompt-01 migration requirement.
17. Compatibility and regression risk.

## Prompt-01 compatibility questions

Determine whether each caller will remain compatible when:

- `PredicateResult` becomes deeply immutable;
- `predicate_version` becomes mandatory;
- `status` becomes mandatory;
- errors become typed immutable objects;
- trace steps become typed immutable objects;
- evidence and inputs become immutable;
- missing capability differs from unmatched;
- invalid parameters differ from unmatched;
- tuple and raw-boolean compatibility paths are removed;
- logical condition nodes return `ConditionResult`;
- cache telemetry is separated from logical result identity;
- serialization changes from mutable dictionaries/lists to canonical typed structures.

Prompt-01 must preserve existing domain scoring behavior. Identify exact callers where the contract migration could unintentionally change:

- Yoga matches;
- Career or other domain scores;
- confidence;
- rule firing;
- evidence propagation;
- output JSON;
- snapshots;
- error handling.

Do not implement any behavioral change.

## Execution-status classification

Classify every caller as:

- ACTIVE_PRODUCTION_PATH
- ACTIVE_TEST_PATH_ONLY
- DORMANT_BUT_REFERENCED
- CONFIRMED_UNUSED
- UNKNOWN

Do not classify a caller as `CONFIRMED_UNUSED` without repository-wide evidence.

## Migration classification

Use:

- NO_CHANGE_EXPECTED
- DIRECT_MIGRATION_REQUIRED
- INDIRECT_MIGRATION_REQUIRED
- TEMPORARY_ADAPTER_REQUIRED
- REMOVE_AFTER_CALLER_VERIFICATION
- FUTURE_STAGE
- UNKNOWN

Use scope classifications:

- IN_SCOPE
- TEMPORARY_COMPATIBILITY
- OUT_OF_SCOPE_FUTURE_STAGE
- UNRELATED

Use priorities:

- P0 — Blocks safe Prompt-01 implementation
- P1 — Required for Prompt-01 completion
- P2 — Important compatibility or quality concern
- P3 — Later-stage or nonblocking concern

## Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- caller symbol;
- line number or small range when practical;
- called API or handler;
- observed consumption behavior;
- caller/reference evidence;
- reason for execution-status classification;
- uncertainty where static analysis cannot prove runtime behavior.

Reconcile the caller counts with Audits 1–3. Explain new callers, missing callers or disagreements.

## Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify rules;
- migrate callers;
- add adapters;
- remove legacy paths;
- change serialization;
- update snapshots;
- run formatters;
- commit or push;
- begin Audit-5.

You may run safe, non-mutating searches and tests. Do not execute commands that update files or generated artifacts.

## Deliverable

Create exactly one file:

systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-04-Complete-Caller-Inventory.md

If `systems/Parasara/Documentation/Engine/Prompt-01/Reports` does not exist, stop and report the blocker.

Do not modify previous audit reports or any other file.

Use this structure:

# Prompt-01 Audit-04: Complete Caller Inventory

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–3
## 4. Predicate Registry and Evaluator Callers
## 5. Condition Evaluator Callers
## 6. Direct Predicate-Handler Callers
## 7. Yoga Engine Callers
## 8. Domain Runtime Callers
## 9. Rule Loader, Compiler and Rule-Engine Callers
## 10. Inference and Output Consumers
## 11. Cache Consumers
## 12. Serialization Consumers
## 13. Test, Fixture and Tooling Callers
## 14. Legacy and Compatibility Callers
## 15. Information-Loss and Error-Handling Boundaries
## 16. Prompt-01 Compatibility Assessment
## 17. Caller Migration Risks and Priorities
## 18. Unresolved Questions
## 19. Audit-4 Conclusion

### Complete caller inventory

Include these columns:

File | Symbol | Category | Called API | Resolution Type | Current Expectation | Consumption Pattern | Evidence Handling | Error Handling | Status Handling | Trace Handling | Serialization | Active Path | Tests | Migration Needed | Scope | Priority | Risk

### Contract-impact matrix

Include these columns:

Caller | Deep Immutability | Mandatory Version | Typed Status | Typed Errors | Typed Traces | ConditionResult | Tuple Removal | Serialization Change | Regression Risk | Required Action

### Summary counts

Include counts for:

- total callers;
- direct callers;
- indirect or dynamic callers;
- generic evaluator callers;
- condition evaluator callers;
- direct handler callers;
- Yoga callers;
- domain callers;
- serialization consumers;
- cache consumers;
- test-only callers;
- active production callers;
- callers discarding evidence;
- callers discarding errors;
- callers treating errors as unmatched;
- tuple-unpacking callers;
- raw-truthiness consumers;
- callers requiring direct migration;
- callers with unknown migration status;
- P0, P1, P2 and P3 findings.

## Final response

After creating the report, stop.

Respond with only:

1. Audit-4 status: COMPLETE or BLOCKED
2. Report file path
3. Files modified
4. Tests or commands executed
5. Total caller count
6. Active production caller count
7. Direct handler-bypass count
8. Tuple-unpacking and raw-truthiness caller count
9. Callers requiring direct migration
10. Number of P0, P1, P2 and P3 findings
11. Any blocker or unresolved architectural question

Do not implement corrections and do not proceed to Audit-5.
