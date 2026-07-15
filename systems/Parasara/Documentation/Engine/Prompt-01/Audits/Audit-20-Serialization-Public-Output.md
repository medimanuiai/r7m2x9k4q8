# Prompt-01 — Audit-20: Serialization and Public-Output Audit

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

If an expected report is missing:

- record it as a limitation;
- continue if Audit-20 can still be completed reliably;
- do not recreate or modify it;
- return `BLOCKED` only when the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-20: Serialization and Public-Output Audit**.

Find every place that serializes, converts, logs, snapshots, stores or publicly exposes:

- `PredicateResult`;
- predicate inputs;
- predicate evidence;
- predicate errors;
- predicate traces;
- `ConditionResult` or equivalent condition results;
- Yoga evidence and matches;
- domain results containing predicate-derived data;
- predicate cache telemetry;
- evaluation timing.

Determine precisely whether Prompt-01’s typed, deeply immutable models will affect:

- internal-only representations;
- debug output;
- logs;
- golden snapshots;
- persisted artifacts;
- API responses;
- public JSON schemas;
- output schema versions;
- downstream consumers.

This is a repository-wide, read-only audit.

Do not implement corrections or update snapshots.

## 3. Architectural serialization boundary

Prompt-01 primarily defines an internal predicate contract.

Do not assume every internal `PredicateResult` field must become part of public JSON.

Separate these surfaces:

```text
Internal runtime model
Internal canonical/logical representation
Debug or diagnostic representation
Golden snapshot representation
Persisted internal artifact
Public API or output schema
```

Changes to an internal model should not accidentally alter the public contract without an explicit schema decision.

Use the authoritative documents if they define a different boundary.

## 4. Repository-wide discovery

Search production code, tests, fixtures, scripts, output assembly, API layers, logging, caches, snapshots and documentation.

Search for:

```text
dataclasses.asdict
asdict
json.dumps
json.dump
json.loads
model_dump
model_dump_json
dict()
to_dict
to_json
serialize
deserialize
encoder
decoder
snapshot
golden
output
response
schema
PredicateResult
ConditionResult
evidence
errors
trace_steps
cache_hit
evaluation_time_ms
```

Also inspect:

- custom JSON encoders;
- enum encoders;
- dataclass converters;
- tuple/list conversion;
- immutable mapping conversion;
- API response models;
- output schemas;
- logs and report generators;
- test assertions against dictionaries or JSON.

Treat search matches as candidates. Inspect actual data flow before classifying them.

## 5. Serialization-surface inventory

Identify every relevant serialization or exposure surface.

For each, report:

1. File and symbol.
2. Architectural layer.
3. Data serialized.
4. Serializer or conversion method.
5. Input type.
6. Output type and format.
7. Internal or public classification.
8. Field selection or filtering.
9. Enum behavior.
10. Immutable mapping behavior.
11. Tuple behavior.
12. Ordering behavior.
13. Error behavior.
14. Consumer.
15. Schema or version.
16. Snapshot or persistence impact.
17. Existing tests.

Classify each surface as:

- `INTERNAL_RUNTIME`
- `INTERNAL_DEBUG`
- `LOGGING`
- `GOLDEN_SNAPSHOT`
- `PERSISTED_INTERNAL_ARTIFACT`
- `PUBLIC_API`
- `PUBLIC_OUTPUT_JSON`
- `TEST_ONLY`
- `DOCUMENTATION_EXAMPLE`
- `UNKNOWN`

## 6. PredicateResult serialization

Find every direct or indirect serialization of `PredicateResult`.

Determine whether the serialized representation includes:

- `predicate_id`;
- `predicate_version`;
- `status`;
- `matched`;
- `inputs`;
- `evidence`;
- `errors`;
- `trace_steps`;
- `cache_hit`;
- `evaluation_time_ms`.

For each path, report:

- current field names;
- missing required fields;
- extra fields;
- default omission behavior;
- `None` handling;
- enum representation;
- nested-model conversion;
- ordering;
- public/internal status;
- consumer compatibility.

## 7. Supporting-model serialization

Audit serialization of:

- `PredicateStatus`;
- `PredicateError`;
- `PredicateTraceStep`;
- immutable mapping types;
- tuples and frozen collections;
- equivalent existing models.

Determine whether they serialize as:

- enum name;
- enum value;
- arbitrary object representation;
- dictionary;
- list;
- tuple;
- unsupported object.

Reconcile with Audit-6.

## 8. Deep immutable-value serialization

Determine how serializers handle:

- mapping proxies;
- frozen dictionaries;
- tuples;
- frozensets;
- nested immutable dataclasses;
- enums;
- dates and datetimes;
- decimal values;
- floats, NaN and infinity;
- UUIDs;
- non-string keys;
- custom AstroState objects;
- cyclic values.

Identify whether adding deep immutability to Prompt-01 models will break current `json.dumps`, `asdict`, snapshot or API paths.

Do not choose a new immutable container implementation during this audit.

## 9. Canonical logical serialization

Determine whether a canonical representation exists for deterministic logical comparison or hashing.

Audit whether canonicalization:

- sorts mapping keys;
- preserves semantic list order;
- normalizes sets;
- normalizes enums;
- normalizes aliases;
- separates telemetry;
- handles optional and empty fields consistently;
- rejects unsupported values;
- produces identical bytes or structures for equivalent results.

Distinguish canonical logical serialization from user-facing JSON formatting.

## 10. Telemetry separation

Determine whether these fields are included in logical serialization, snapshots or public output:

- `cache_hit`;
- `evaluation_time_ms`;
- timestamps;
- durations;
- random trace IDs;
- process-local IDs.

Classify each use as:

- `LOGICAL_OUTPUT`
- `DEBUG_TELEMETRY`
- `PERFORMANCE_TELEMETRY`
- `PUBLIC_DIAGNOSTIC`
- `SNAPSHOT_NOISE`
- `UNKNOWN`

Determine whether cold and warm evaluation serialize differently for logical fields or only telemetry.

Reconcile with Audits 11 and 19.

## 11. Condition-result serialization

Find every serialization of logical condition results.

Determine whether logical nodes currently serialize as `PredicateResult` with IDs such as `AND` or `OR`.

Assess the impact of introducing `ConditionResult` on:

- field names;
- nested child results;
- operator identity;
- status;
- evidence;
- errors;
- traces;
- skipped branches;
- recursion;
- snapshots;
- downstream consumers.

Do not implement `ConditionResult`.

## 12. Evidence serialization

Reconcile with Audit-18.

Determine whether predicate evidence contains:

- mutable containers;
- custom objects;
- AstroState objects;
- enums;
- sets;
- raw provider input;
- exception objects;
- non-string keys;
- nondeterministic ordering.

Find every point where evidence is flattened, renamed, filtered or dropped during serialization.

## 13. Error serialization and safety

Reconcile with Audit-17.

Determine whether serialized errors expose:

- raw exception messages;
- stack traces;
- filesystem paths;
- environment values;
- raw parameters;
- raw Surya payloads;
- internal class representations.

Assess whether typed errors will change existing field names, list structure or public filtering.

Do not reproduce sensitive values in the report.

## 14. Trace serialization

Reconcile with Audit-19.

Determine whether serialized traces include:

- deterministic step identity;
- random UUIDs;
- timestamps;
- duration fields;
- parent-child relationships;
- skipped branches;
- cache-hit details;
- raw exceptions;
- internal-only details.

Identify snapshot and public-schema nondeterminism.

## 15. Yoga serialization

Determine how Yoga serializes or stores:

- match identity;
- supporting predicate or condition results;
- evidence;
- errors;
- traces;
- scores or classifications;
- AstroState enrichment data.

Identify Prompt-01 changes that could affect Yoga snapshots or consumers without changing Yoga matching.

Reconcile with Audit-15.

## 16. Domain and inference serialization

Inspect Career and all other implemented domains.

Determine whether domain or inference output:

- includes raw `PredicateResult`;
- includes selected predicate fields;
- copies evidence;
- filters errors;
- exposes traces;
- depends on dictionary/list mutability;
- depends on current field ordering;
- includes cache or timing telemetry.

Reconcile with Audit-16.

## 17. OutputAssembler and public schema

Identify every output-assembly component and public response model.

For each, report:

- file and symbol;
- input models;
- output model or schema;
- predicate-derived fields;
- filtering and transformation;
- schema version;
- consumers;
- compatibility tests.

Determine whether Prompt-01 is intended to change public output or remain internal.

If the authoritative documents do not decide this, record it as an architectural question.

## 18. Golden snapshots and fixtures

Find every snapshot, golden file, fixture or expected JSON containing predicate-derived data.

For each snapshot family, report:

- location;
- generator;
- data included;
- deterministic normalization;
- telemetry included;
- update command;
- tests consuming it;
- Prompt-01 impact.

Do not update or regenerate snapshots.

Clearly distinguish:

- snapshots expected to change after approved implementation;
- snapshots that must remain stable;
- debug-only artifacts;
- public-schema contract fixtures.

## 19. Logs and diagnostic output

Find logs, console output, HTML reports and debug dumps containing predicate-derived models.

Determine whether they:

- invoke serializers directly;
- expose raw internal details;
- depend on mutable dictionaries;
- contain nondeterministic timings or IDs;
- are confused with public output;
- are covered by tests.

Do not change logging or reports.

## 20. Deserialization and round trips

Identify whether predicate or condition results are deserialized from:

- JSON;
- cache persistence;
- snapshots;
- API requests;
- stored reports.

Determine whether round trips preserve:

- enum values;
- immutable nested types;
- tuple/list semantics;
- errors;
- traces;
- child results;
- predicate version;
- status/matched consistency.

Do not assume serialization is one-way.

## 21. Schema versioning and compatibility

Identify schema versions relevant to:

- predicate-result serialization;
- condition results;
- Yoga output;
- domain output;
- public API output;
- snapshots or persisted artifacts.

Determine whether adding fields is:

- internal-only;
- backward compatible;
- breaking;
- ignored by consumers;
- undocumented;
- unknown.

Do not increment schema versions during the audit.

## 22. Downstream consumer inventory

Identify consumers that parse or depend on predicate-derived serialized data.

Include:

- Python code;
- tests;
- scripts;
- API clients inside the repository;
- report generators;
- frontend or mobile-facing schema definitions, if present;
- documentation examples.

For each consumer, determine whether it depends on:

- exact field names;
- missing versus present fields;
- dictionary/list representation;
- enum string values;
- ordering;
- telemetry fields;
- unknown-field rejection.

## 23. Determinism and ordering

Identify serialization nondeterminism caused by:

- random UUIDs;
- current time;
- performance timing;
- unordered sets;
- unsorted mappings;
- filesystem traversal order;
- registry iteration;
- cache warmth;
- object representation;
- process memory identity.

Classify each occurrence as:

- `LOGICAL_SERIALIZATION_NONDETERMINISM`
- `SNAPSHOT_NONDETERMINISM`
- `PUBLIC_OUTPUT_NONDETERMINISM`
- `DEBUG_OR_TELEMETRY_ONLY`
- `UNRELATED`

## 24. Test inventory and gap analysis

Locate tests covering:

### Model serialization

- `PredicateResult` JSON serialization;
- status enum serialization;
- typed errors;
- typed trace steps;
- immutable mappings;
- tuples and frozen collections;
- nested canonicalization.

### Round trips

- serialize and deserialize;
- field preservation;
- enum preservation;
- error and trace preservation;
- status/matched consistency;
- deterministic repeated serialization.

### Internal/public separation

- internal fields are not exposed publicly;
- raw exception details are filtered;
- cache and timing telemetry are filtered or explicitly classified;
- public schema remains versioned.

### Integration

- condition-result serialization;
- Yoga output;
- domain output;
- OutputAssembler;
- snapshots;
- cold/warm logical equivalence.

### Failure behavior

- unsupported evidence values;
- non-string keys;
- cycles;
- NaN and infinity;
- unknown enum values;
- malformed deserialization input.

For every missing test category:

- identify the gap;
- explain its risk;
- recommend the likely test file;
- do not create the test.

## 25. Required classifications

Classify serialization surfaces as:

- `INTERNAL_ONLY`
- `DEBUG_OR_TELEMETRY`
- `SNAPSHOT_CONTRACT`
- `PERSISTED_INTERNAL_CONTRACT`
- `PUBLIC_CONTRACT`
- `UNKNOWN`

Classify Prompt-01 impact as:

- `NO_IMPACT`
- `INTERNAL_REPRESENTATION_CHANGE`
- `EXPECTED_SNAPSHOT_CHANGE`
- `PUBLIC_COMPATIBILITY_RISK`
- `SCHEMA_VERSION_DECISION_REQUIRED`
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

## 26. Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- symbol name;
- line number or small range when practical;
- serialized model or field;
- serialization method;
- consumer and surface classification;
- observed representation;
- Prompt-01 impact;
- existing tests;
- uncertainty where static analysis cannot prove runtime behavior.

Include small redacted examples where useful. Do not reproduce sensitive data.

Reconcile findings with Audits 1–19 without modifying earlier reports.

## 27. Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify rules;
- modify previous audit reports;
- change serializers;
- change schemas or schema versions;
- regenerate or update snapshots;
- modify API output;
- migrate consumers;
- run formatters;
- create commits;
- push changes;
- begin Audit-21.

You may run safe, non-mutating searches and tests.

Do not execute commands that update files, snapshots or generated artifacts.

## 28. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-20-Serialization-Public-Output.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker rather than selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-20: Serialization and Public Output

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–19
## 4. Serialization-Surface Inventory
## 5. PredicateResult Serialization
## 6. Supporting-Model Serialization
## 7. Immutable-Value Serialization
## 8. Canonical Logical Serialization
## 9. Telemetry Separation
## 10. Condition-Result Serialization
## 11. Evidence, Error and Trace Serialization
## 12. Yoga Serialization
## 13. Domain and Inference Serialization
## 14. OutputAssembler and Public Schemas
## 15. Golden Snapshots and Fixtures
## 16. Logs and Diagnostic Output
## 17. Deserialization and Round Trips
## 18. Schema Versioning and Compatibility
## 19. Downstream Consumer Inventory
## 20. Determinism and Ordering
## 21. Existing Tests and Coverage Gaps
## 22. Prompt-01 Compliance Matrix
## 23. Migration Risks and Priorities
## 24. Unresolved Architectural Questions
## 25. Audit-20 Conclusion
```

### Serialization-surface inventory

| Surface | File | Symbol | Layer | Data | Method | Input Type | Output Type | Classification | Field Filtering | Ordering | Schema Version | Consumer | Tests | Prompt-01 Impact | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### PredicateResult field matrix

| Field | Internal Model | Canonical Serialization | Debug Output | Snapshot | Persisted Artifact | Public Output | Representation | Consumer Dependency | Impact | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Immutable-value compatibility matrix

| Value Type | Current Use | Serializer | Supported | Current Representation | Deterministic | Round-Trip Safe | Affected Surfaces | Required Decision | Priority |
|---|---|---|---|---|---|---|---|---|---|

### Snapshot and public-output impact matrix

| Artifact/Schema | Location | Generator | Predicate-Derived Data | Telemetry | Deterministic | Consumer | Prompt-01 Change | Compatibility Risk | Update Allowed Now | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Downstream consumer inventory

| Consumer | File | Symbol | Surface | Fields Used | Exact-Type Dependency | Ordering Dependency | Unknown-Field Behavior | Schema Version | Migration Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Compliance matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- serialization surfaces;
- internal runtime surfaces;
- debug/logging surfaces;
- snapshot contracts;
- persisted internal contracts;
- public contracts;
- direct `PredicateResult` serializers;
- condition-result serializers;
- Yoga/domain/inference serializers;
- immutable-value incompatibilities;
- enum serialization inconsistencies;
- tuple/list representation risks;
- non-JSON-safe value paths;
- logical telemetry contamination paths;
- cold/warm serialization differences;
- snapshot impacts;
- public compatibility risks;
- schema-version decisions required;
- downstream consumers at risk;
- round-trip gaps;
- nondeterministic serialization paths;
- missing serialization test categories;
- P0, P1, P2 and P3 findings.

## 29. Final response

After creating the report, stop.

Respond with only:

1. Audit-20 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Serialization-surface counts by classification
6. Direct PredicateResult, condition, Yoga and domain/inference serializer counts
7. Immutable-value, enum and tuple/list compatibility-risk counts
8. Non-JSON-safe and logical-telemetry-contamination counts
9. Cold/warm serialization-difference count
10. Snapshot-impact and public-compatibility-risk counts
11. Schema-version-decision count
12. At-risk downstream-consumer count
13. Nondeterministic serialization-path count
14. Missing test-category count
15. Number of P0, P1, P2 and P3 findings
16. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-21.