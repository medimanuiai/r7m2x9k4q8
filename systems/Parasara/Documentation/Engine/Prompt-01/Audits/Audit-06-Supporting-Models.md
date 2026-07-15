# Prompt-01 — Audit-6: Supporting Model Audit

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

If an expected report is missing:

- record it as a limitation;
- continue when the missing report does not prevent a reliable audit;
- do not recreate or modify it;
- return `BLOCKED` only when the missing information makes Audit-6 unreliable.

## 2. Objective

Perform only **Audit-6: Supporting Model Audit**.

Audit all supporting types required by the Prompt-01 predicate-result contract, especially:

- `PredicateStatus`
- `PredicateError`
- `PredicateTraceStep`
- immutable nested-value representations
- canonicalization utilities
- equivalent status, error or trace models under different names

Determine:

1. What already exists.
2. What is currently used.
3. What can safely be reused.
4. What must remain separate.
5. What Prompt-01 still requires.
6. What architectural decisions remain unresolved.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Repository-wide discovery

Search the complete repository, including:

- production source code;
- tests and fixtures;
- predicate and condition engines;
- rule engine and rule loaders;
- Yoga Engine;
- domain interpreters;
- inference code;
- output assembly;
- cache and serialization utilities;
- scripts and diagnostics;
- YAML and JSON files where relevant;
- architecture documentation.

Search for:

- `PredicateStatus`
- `PredicateError`
- `PredicateTraceStep`
- predicate-related status enums
- error dataclasses
- trace dataclasses
- Pydantic error or trace models
- named tuples and typed dictionaries
- error-code enums and constants
- recoverability fields
- trace IDs
- parent and child trace identifiers
- immutable mapping utilities
- deep-freezing utilities
- canonicalization utilities
- deterministic serialization helpers
- dictionaries used as errors
- dictionaries used as trace steps
- test-only supporting models
- equivalent models with different names

Do not assume that similarly named models are compatible. Compare their fields, semantics, ownership and architectural layer.

## 4. PredicateStatus audit

Determine whether a suitable predicate-status model already exists.

Assess support for these Prompt-01 states:

- `matched`
- `unmatched`
- `missing_capability`
- `invalid_parameters`
- `error`
- `timeout`
- `skipped`

For every existing status model, report:

1. Repository-relative file path.
2. Symbol name.
3. Model type.
4. Member names.
5. Serialized values.
6. Case sensitivity.
7. Equality behavior.
8. Hashing behavior.
9. JSON serialization behavior.
10. Invalid or unknown-value handling.
11. Producers.
12. Consumers.
13. Whether it is predicate-specific or shared.
14. Whether it represents all required states.
15. Whether aliases or duplicate status models exist.
16. Whether it can be reused without affecting unrelated layers.

Determine whether `matched` and `status` can contradict each other.

Examples of potentially invalid combinations include:

```python
matched=True
status=PredicateStatus.UNMATCHED
```

```python
matched=False
status=PredicateStatus.MATCHED
```

Report whether:

- the current model prevents contradictions;
- factories enforce consistency;
- callers can construct inconsistent values;
- a single authoritative consistency rule exists.

Do not invent a rule if Prompt-01 is unclear. Record it as an unresolved architectural question.

## 5. PredicateError audit

Find every predicate-related error representation.

Include ad hoc dictionaries such as:

```python
{"error": str(exception)}
```

Compare existing models against Prompt-01 requirements, including:

- stable error code;
- safe message;
- predicate ID;
- structured details;
- recoverability;
- deep immutability;
- deterministic serialization;
- JSON safety.

For every existing or candidate error model, report:

1. File and symbol.
2. Model type.
3. Field names and types.
4. Required and optional fields.
5. Default values.
6. Error-code representation.
7. Message semantics.
8. Predicate identity support.
9. Structured-detail support.
10. Recoverability classification.
11. Exception-wrapping behavior.
12. Whether raw exception text is exposed.
13. Whether stack traces can enter result data.
14. Nested mutability.
15. Serialization behavior.
16. Producers and consumers.
17. Whether predicate, rule, domain and infrastructure errors are mixed.

Assess existing support for these candidate categories:

- `INVALID_PARAMETERS`
- `MISSING_CAPABILITY`
- `MISSING_PLANET`
- `MISSING_HOUSE`
- `MISSING_VARGA`
- `MISSING_ASPECT_GRAPH`
- `UNKNOWN_REFERENCE`
- `UNKNOWN_PREDICATE`
- `INVALID_RETURN_TYPE`
- `PREDICATE_EXCEPTION`
- `PREDICATE_TIMEOUT`

These are audit candidates, not implementation instructions.

Identify:

- which codes already exist;
- which are required explicitly by Prompt-01;
- which are implied but not defined;
- which require an architectural decision;
- which may belong to another layer.

Do not reproduce secrets, sensitive values or raw stack traces in the report.

## 6. PredicateTraceStep audit

Find every predicate, condition, rule, Yoga, inference and run-level trace model.

Determine whether an existing model can safely serve as `PredicateTraceStep` without coupling predicates to later layers.

For every candidate trace model, report:

1. File and symbol.
2. Architectural layer.
3. Owning component.
4. Model type.
5. Field names and types.
6. Step or operation identity.
7. Sequence or ordering support.
8. Parent-child relationships.
9. Input or observation details.
10. Outcome representation.
11. Error references.
12. AST-node references.
13. Rule-node references.
14. Duration fields.
15. Timestamp fields.
16. UUID or random-ID usage.
17. Deep immutability.
18. Serialization behavior.
19. Producers and consumers.
20. Snapshot exposure.
21. Public-output exposure.

Assess whether trace steps can represent deterministic operations such as:

- locating a planet;
- checking a required capability;
- reading an actual house;
- comparing actual and expected values;
- producing a predicate result.

Do not require excessively verbose traces. Determine only what Prompt-01 requires.

## 7. Trace identity and determinism

Identify supporting trace mechanisms that use:

- random UUIDs;
- `datetime.now`;
- `datetime.utcnow`;
- `time.time`;
- system-clock reads;
- process-specific identifiers;
- memory addresses;
- unordered sets;
- unordered iteration;
- performance duration values.

Classify each occurrence as:

- `LOGICAL_NONDETERMINISM`
- `TRACE_ONLY_NONDETERMINISM`
- `PERFORMANCE_ONLY_NONDETERMINISM`
- `UNRELATED_TO_PROMPT_01`

Determine whether trace identity is currently:

- deterministic;
- random;
- optional;
- absent;
- included in logical equality;
- included in logical hashing;
- included in snapshots;
- included in public output.

Do not implement a trace-ID algorithm.

## 8. Immutable and canonical nested-data audit

Find existing utilities that:

- freeze mappings;
- create defensive copies;
- convert lists to tuples;
- normalize sets;
- sort mapping keys;
- canonicalize nested values;
- convert values to JSON-safe forms;
- calculate deterministic digests.

For every candidate utility, report:

1. File and symbol.
2. Current consumers.
3. Supported input types.
4. Deep-freezing behavior.
5. Defensive-copy behavior.
6. Whether caller-owned values remain shared.
7. Determinism.
8. JSON compatibility.
9. Dictionary-key ordering.
10. Set ordering.
11. Enum handling.
12. Dataclass handling.
13. Date and datetime handling.
14. Floating-point handling.
15. Custom-object handling.
16. Cycle handling.
17. Unsupported-value behavior.
18. Whether inputs are mutated.
19. Suitability for:
    - predicate inputs;
    - predicate evidence;
    - error details;
    - trace details.

Do not redesign repository-wide serialization.

## 9. Duplicate-model and reuse analysis

Identify overlapping supporting models across:

- predicates;
- condition evaluation;
- rule matching;
- Yoga;
- domain interpretation;
- inference;
- output assembly;
- diagnostics;
- general infrastructure.

For every overlapping or candidate model, recommend exactly one classification:

- `REUSE_AS_IS`
- `REUSE_WITH_PROMPT_01_EXTENSION`
- `PREDICATE_SPECIFIC_MODEL_REQUIRED`
- `KEEP_SEPARATE`
- `DEPRECATE_LATER`
- `UNKNOWN`

Base the recommendation on:

- field compatibility;
- semantic compatibility;
- ownership;
- layer boundaries;
- immutability;
- serialization;
- determinism;
- existing consumers;
- regression risk.

Do not merge, rename or modify models during this audit.

## 10. Construction and consumption paths

Find every location where supporting models or equivalent dictionaries are:

- constructed;
- appended;
- copied;
- replaced;
- converted;
- serialized;
- cached;
- logged;
- ignored;
- exposed publicly;
- mutated after construction.

For each relevant path, report:

1. File and symbol.
2. Supporting model involved.
3. Construction or consumption behavior.
4. Whether typed models are used.
5. Whether information is lost.
6. Whether raw exceptions are exposed.
7. Whether nested data remains mutable.
8. Whether deterministic ordering is preserved.
9. Whether conversion crosses architectural layers.
10. Whether migration is required for Prompt-01.

## 11. Serialization and schema impact

Inspect how supporting models or equivalent dictionaries reach:

- `dataclasses.asdict`;
- `json.dumps`;
- Pydantic serialization;
- custom serializers;
- logs;
- snapshots;
- output assembly;
- API responses;
- public JSON.

Determine whether typed enums, immutable mappings, tuples and nested models would affect:

- JSON compatibility;
- serialized enum values;
- field names;
- field ordering;
- golden snapshots;
- debug output;
- public schemas;
- backward compatibility.

Do not modify serializers, schemas or snapshots.

## 12. Test inventory and gap analysis

Locate existing tests for the following categories.

### PredicateStatus tests

- complete enum membership;
- stable serialized values;
- invalid status rejection;
- matched/status consistency;
- JSON serialization.

### PredicateError tests

- stable error codes;
- safe exception conversion;
- recoverability;
- immutable details;
- JSON-safe details;
- exclusion of raw stack traces;
- deterministic serialization.

### PredicateTraceStep tests

- construction;
- deep immutability;
- deterministic ordering;
- deterministic identity;
- JSON serialization;
- cache-hit behavior;
- absence of system-clock dependency;
- parent-child relationships where required.

### Canonicalization tests

- nested dictionaries;
- lists and tuples;
- sets;
- enums;
- dataclasses;
- mutation of caller-owned input after construction;
- unsupported values;
- deterministic repeated output;
- cycle handling where applicable.

For every missing test category:

- identify the gap;
- explain its risk;
- recommend the likely test-file location;
- do not create the test.

## 13. Compliance classifications

For every Prompt-01 requirement, use one status:

- `IMPLEMENTED`
- `PARTIAL`
- `MISSING`
- `NONCOMPLIANT`
- `UNKNOWN`

Use these priorities:

- `P0` — Blocks safe Prompt-01 implementation
- `P1` — Required for Prompt-01 completion
- `P2` — Important compatibility or quality concern
- `P3` — Later-stage or nonblocking concern

Use these scope classifications:

- `IN_SCOPE`
- `TEMPORARY_COMPATIBILITY`
- `OUT_OF_SCOPE_FUTURE_STAGE`
- `UNRELATED`

## 14. Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- symbol name;
- line number or small range when practical;
- observed fields or behavior;
- producers and consumers where applicable;
- existing test evidence;
- reason the model can or cannot be reused;
- uncertainty where static analysis cannot prove behavior.

Reconcile findings with Audits 1–5.

Explain:

- disagreements;
- count differences;
- newly discovered models;
- missing earlier evidence;
- findings that supersede an earlier audit conclusion.

Do not silently overwrite or modify earlier conclusions.

## 15. Scope restrictions

Do not:

- modify production code;
- modify tests;
- modify rules;
- modify previous audit reports;
- create supporting models;
- add enum members;
- add error codes;
- change exception handling;
- change trace generation;
- refactor canonicalization utilities;
- change serialization;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-7.

You may run safe, non-mutating searches and tests.

Do not run commands that update files, snapshots or generated artifacts.

## 16. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-06-Supporting-Models.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker rather than selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-06: Supporting Models

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–5
## 4. Existing Supporting-Model Inventory
## 5. PredicateStatus Assessment
## 6. PredicateError Assessment
## 7. PredicateTraceStep Assessment
## 8. Error Codes and Exception Safety
## 9. Trace Identity and Determinism
## 10. Immutable and Canonical Data Utilities
## 11. Duplicate Models and Reuse Opportunities
## 12. Construction and Consumption Paths
## 13. Serialization and Public-Schema Impact
## 14. Existing Tests and Coverage Gaps
## 15. Prompt-01 Compliance Matrix
## 16. Migration Risks and Priorities
## 17. Unresolved Architectural Questions
## 18. Audit-6 Conclusion
```

### Supporting-model inventory

Include these columns:

| Model | File | Symbol | Layer | Model Type | Fields | Immutable | Deterministic | JSON-Safe | Producers | Consumers | Tests | Reuse Recommendation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

### PredicateStatus comparison

Include these columns:

| Required Status | Existing Representation | Serialized Value | Semantics Defined | Producers | Consumers | Compliance | Gap | Priority |
|---|---|---|---|---|---|---|---|---|

### PredicateError comparison

Include these columns:

| Required Field or Behavior | Existing Support | Evidence | Safety Concern | Required Change | Compliance | Priority |
|---|---|---|---|---|---|---|

### Trace-model comparison

Include these columns:

| Model | Layer | Identity | Step Ordering | Parent/Child Support | Timing Fields | Randomness | Immutable | Serialization | Predicate Suitability | Recommendation | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|

### Canonicalization-utility inventory

Include these columns:

| Utility | File | Supported Types | Deep Freeze | Defensive Copy | Deterministic | JSON-Safe | Current Consumers | Predicate Suitability | Risk |
|---|---|---|---|---|---|---|---|---|---|

### Compliance matrix

Include these columns:

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- existing status models;
- existing error models;
- existing trace models;
- dictionary-based predicate-error patterns;
- dictionary-based trace-step patterns;
- reusable supporting models;
- models requiring extension;
- predicate-specific models required;
- deterministic trace models;
- nondeterministic trace mechanisms;
- reusable canonicalization utilities;
- missing supporting-model test categories;
- P0, P1, P2 and P3 findings.

## 17. Final response

After creating the report, stop.

Respond with only:

1. Audit-6 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Status-model count
6. Error-model count
7. Trace-model count
8. Reusable supporting-model count
9. Nondeterministic trace-mechanism count
10. Missing supporting-model test-category count
11. Number of P0, P1, P2 and P3 findings
12. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-7.
