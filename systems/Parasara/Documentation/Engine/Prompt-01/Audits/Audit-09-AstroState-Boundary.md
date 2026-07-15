# Prompt-01 — Audit-9: AstroState Boundary Audit

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

If an expected report is missing:

- record it as a limitation;
- continue if Audit-9 can still be completed reliably;
- do not recreate or modify it;
- return `BLOCKED` only if the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-9: AstroState Boundary Audit**.

Determine whether predicates and predicate-related evaluation paths obey the required `AstroState` architectural boundary.

Audit:

- the canonical `AstroState` model;
- how it is constructed;
- how predicates access it;
- whether predicates access raw Surya Siddhanta input;
- whether predicates mutate it;
- whether predicate behavior depends on object identity or mutable state;
- whether a deterministic content digest exists;
- whether the digest covers all predicate-relevant facts and versions;
- whether predicate cache keys can safely rely on it.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Required architectural boundary

Prompt-01 concerns this flow:

```text
Raw Surya Siddhanta JSON
    ↓
Adapter and normalization
    ↓
AstroState
    ↓
Enrichment engines
    ↓
Prepared or immutable AstroState
    ↓
Generic Predicate Engine
    ↓
PredicateResult
```

Predicates should query factual information through `AstroState` or stable query APIs.

Predicates must not:

- access raw Surya Siddhanta JSON;
- parse provider-specific structures;
- normalize raw chart data;
- calculate domain scores;
- generate narratives;
- call external services;
- read system time;
- mutate `AstroState`;
- run enrichment engines during evaluation;
- depend on process memory identity;
- depend on evaluation order.

Do not redesign `AstroState`. Identify only Prompt-01-relevant boundary problems.

## 4. Repository-wide discovery

Search the complete repository for:

- every `AstroState` definition;
- builders, factories and adapters;
- normalization engines;
- enrichment storage;
- query methods;
- mutation helpers;
- copy or freeze functions;
- serialization methods;
- digest, hash or fingerprint functions;
- version fields;
- raw-input retention;
- Surya Siddhanta imports and access;
- predicate access to chart data;
- predicate cache keys using `id(astro)`;
- direct dictionary access;
- Yoga and domain mutations;
- test-only AstroState variants;
- mocks and fixtures;
- alternate or legacy state models.

Search for patterns such as:

```python
class AstroState
@dataclass
astro.
astro[...]
astro.get(...)
getattr(astro, ...)
astro.enrichments
astro.enrichments[...]
astro.enrichments.get(...)
astro.enrichments.update(...)
setattr(astro, ...)
id(astro)
hash(astro)
digest
fingerprint
checksum
raw
source
surya
json
payload
```

Inspect context before classifying a match as relevant.

## 5. AstroState definition inventory

Identify every current or legacy `AstroState` representation.

For each definition, report:

1. File and symbol.
2. Model type.
3. Fields.
4. Nested field types.
5. Required and optional fields.
6. Defaults.
7. Construction paths.
8. Producers.
9. Consumers.
10. Frozen or mutable status.
11. Deep immutability.
12. Validation behavior.
13. Serialization behavior.
14. Digest or hashing support.
15. Version support.
16. Raw-input retention.
17. Production, test-only or dormant status.
18. Existing tests.

Determine which definition is canonical.

If multiple definitions are active, explain their boundaries and compatibility risks.

## 6. Construction and preparation pipeline

Trace the complete path from raw input to predicate-ready state:

```text
Raw chart
→ adapter
→ normalization
→ AstroState construction
→ enrichment
→ finalization or freezing
→ predicate evaluation
```

For every stage, identify:

- file and symbol;
- input type;
- output type;
- mutation behavior;
- validation performed;
- version information added;
- enrichment information added;
- whether deterministic ordering is preserved;
- whether system time is read;
- whether external services are called;
- whether the resulting state is safe for predicate evaluation.

Determine whether a clear predicate-readiness boundary exists.

Classify readiness as:

- `EXPLICITLY_ENFORCED`
- `EXPLICIT_BUT_NOT_ENFORCED`
- `IMPLICIT`
- `CALLER_DEPENDENT`
- `ABSENT`
- `UNKNOWN`

## 7. Predicate data-access inventory

For every registered predicate, document:

1. Predicate ID.
2. Handler file and symbol.
3. `AstroState` fields accessed.
4. Enrichment keys accessed.
5. Query methods used.
6. Direct mapping access.
7. `getattr` or fallback access.
8. Raw-input access.
9. Provider-specific assumptions.
10. Required capability.
11. Mutation behavior.
12. Recomputation behavior.
13. Evaluation-context access.
14. Existing tests.

Classify each access as:

- `CANONICAL_QUERY_API`
- `CANONICAL_FIELD_ACCESS`
- `DIRECT_ENRICHMENT_ACCESS`
- `DYNAMIC_GETATTR_ACCESS`
- `RAW_SOURCE_ACCESS`
- `LEGACY_STATE_ACCESS`
- `UNKNOWN`

Do not automatically classify direct field access as incorrect. Compare it with the documented architecture.

## 8. Raw Surya Siddhanta boundary audit

Find every predicate, condition evaluator, Yoga helper or predicate-related caller that accesses:

- raw Surya Siddhanta JSON;
- raw provider payloads;
- provider-specific keys;
- unnormalized planet names;
- raw longitude fields;
- raw house fields;
- provider-specific metadata;
- source file paths;
- provider adapters.

For every occurrence, report:

1. File and symbol.
2. Predicate or caller.
3. Raw data accessed.
4. Reason for access.
5. Whether normalized equivalent data exists.
6. Whether it bypasses `AstroState`.
7. Whether it creates provider coupling.
8. Whether it is on an active path.
9. Prompt-01 migration scope.
10. Risk and priority.

Distinguish:

- legitimate adapter-layer access;
- legitimate normalization-layer access;
- prohibited predicate-layer access;
- test-fixture setup;
- unrelated tooling.

## 9. AstroState mutation audit

Find every predicate-related write to `AstroState` or its nested objects.

Search for:

```python
astro.field = value
astro.enrichments["key"] = value
astro.enrichments.update(...)
astro.planets.append(...)
astro.houses[...] = value
setattr(astro, ...)
del astro...
```

Also inspect functions that receive `AstroState` and may mutate it indirectly.

For every mutation candidate, report:

1. File and symbol.
2. Caller or predicate.
3. Mutated field or structure.
4. Direct or indirect mutation.
5. Timing relative to predicate evaluation.
6. Whether mutation performs enrichment.
7. Whether it affects later predicate results.
8. Whether it affects caching.
9. Whether it creates evaluation-order dependence.
10. Existing tests relying on it.
11. Execution status.
12. Scope and priority.

Classify mutations as:

- `PREPARATION_STAGE_MUTATION`
- `PREDICATE_EVALUATION_MUTATION`
- `CONDITION_EVALUATION_MUTATION`
- `YOGA_EVALUATION_MUTATION`
- `DOMAIN_EVALUATION_MUTATION`
- `TEST_ONLY_MUTATION`
- `UNRELATED`

Preparation-stage mutation may be valid before finalization. Do not classify it as a violation without considering lifecycle.

## 10. Deep immutability assessment

Determine whether the predicate-ready `AstroState` is deeply immutable.

Audit whether callers can mutate:

- planets;
- houses;
- signs;
- ascendant data;
- enrichments;
- aspects;
- vargas;
- functional roles;
- strength data;
- Dasha or transit data;
- metadata;
- version maps;
- nested lists, dictionaries and sets.

Check whether:

- the outer model is frozen;
- nested dictionaries remain mutable;
- nested lists remain mutable;
- caller-owned constructor values remain shared;
- defensive copies are made;
- cached predicate results can become stale after mutation;
- digest values can disagree with mutated content;
- copy helpers preserve immutability.

Do not change the model.

## 11. Query API assessment

Identify every `AstroState` query method intended for predicate use.

Examples may include methods for:

- finding a planet;
- reading a planet’s house;
- retrieving a house;
- finding a house lord;
- reading an enrichment;
- checking capability availability;
- retrieving aspects;
- retrieving vargas;
- retrieving functional roles.

For each query API, report:

1. File and symbol.
2. Input contract.
3. Return contract.
4. Missing-data behavior.
5. Exception behavior.
6. Determinism.
7. Mutation behavior.
8. Provider independence.
9. Existing predicate callers.
10. Tests.
11. Prompt-01 suitability.

Identify duplicate lookup logic implemented independently inside predicates.

Do not design new query APIs during this audit.

## 12. AstroState digest inventory

Search for every existing:

- digest;
- fingerprint;
- checksum;
- stable hash;
- chart ID;
- state ID;
- content hash;
- serialization hash.

For each candidate, report:

1. File and symbol.
2. Algorithm.
3. Input fields.
4. Excluded fields.
5. Ordering guarantees.
6. Version fields included.
7. Enrichment data included.
8. Evaluation context included.
9. Raw input included.
10. Telemetry included.
11. Mutability risks.
12. Determinism across processes.
13. Determinism across Python versions, if relevant.
14. Current consumers.
15. Tests.
16. Suitability for predicate caching.

Do not assume a chart ID is a content digest. Verify how it is produced.

## 13. Required digest coverage

Compare the current digest against Prompt-01 cache and determinism requirements.

Determine whether it covers predicate-relevant state such as:

- normalized core chart facts;
- planets;
- houses;
- ascendant;
- signs;
- house lords;
- normalization version;
- source-system version where relevant;
- enrichment versions;
- aspect data or version;
- varga data or version;
- functional-role data or version;
- strength data or version;
- rule-system or plugin scope where relevant.

Classify each field or version as:

- `INCLUDED`
- `EXCLUDED_INTENTIONALLY`
- `EXCLUDED_UNSAFELY`
- `NOT_APPLICABLE`
- `UNKNOWN`

Do not require all enrichment contents to be included if versioned capability digests are architecturally intended. Report the actual design and unresolved choices.

## 14. Digest canonicalization

Audit whether digest generation handles:

- dictionary key order;
- list order;
- sets;
- enums;
- dataclasses;
- floats;
- NaN and infinity;
- dates and datetimes;
- UUIDs;
- custom objects;
- optional and missing fields;
- empty versus absent values;
- aliases;
- nested mutable structures.

Determine whether logically equivalent `AstroState` instances produce the same digest across:

- repeated construction;
- different dictionary insertion orders;
- separate processes;
- cold and warm runs;
- serialized and deserialized forms.

Do not create a new digest algorithm.

## 15. Object identity and cache-key audit

Find every use of:

```python
id(astro)
id(ast_state)
hash(astro)
object.__hash__(...)
```

in predicate caching, evaluation, tracing or memoization.

For each occurrence, determine:

- purpose;
- process stability;
- content sensitivity;
- mutation sensitivity;
- collision or reuse risk;
- current tests;
- Prompt-01 compliance;
- required migration dependency.

Pay particular attention to cache keys shaped like:

```python
(id(astro), predicate_name, params_json)
```

Determine whether identical charts in different objects share cache entries and whether mutated charts retain stale entries.

Do not modify the cache during this audit.

## 16. Version-boundary assessment

Identify all versions relevant to `AstroState` and predicate behavior:

- schema version;
- adapter version;
- normalization version;
- source-system version;
- enrichment versions;
- aspect-engine version;
- varga-engine version;
- functional-role version;
- strength-engine version;
- system or plugin version.

For each version, report:

1. Where it is defined.
2. Where it is stored.
3. Whether it is included in the digest.
4. Whether it is included in predicate cache keys.
5. Whether it is serialized.
6. Whether it is deterministic.
7. Whether changing it invalidates cached predicate results.
8. Whether tests cover version isolation.

Do not invent versions that do not exist. Identify missing version boundaries required by Prompt-01.

## 17. Equality, copying and lifecycle

Determine:

- whether two content-equivalent states compare equal;
- whether equality includes enrichments;
- whether equality includes telemetry;
- whether `AstroState` is hashable;
- whether copies share nested mutable values;
- whether enrichment creates a new state or mutates the existing state;
- whether a finalized state can be reopened;
- whether digest calculation occurs before or after enrichment;
- whether cached digest values can become stale;
- whether predicate evaluation assumes a particular lifecycle stage.

Distinguish object equality from deterministic content identity.

## 18. Evaluation-order dependency

Identify cases where predicate results depend on:

- whether another predicate ran first;
- whether Yoga ran first;
- whether an enrichment was computed lazily;
- whether a caller mutated `AstroState`;
- whether the predicate cache was populated;
- whether tests reuse the same state;
- registry or dictionary iteration order.

For each dependency, report:

- initiating operation;
- affected predicate;
- changed state;
- observed or inferred result difference;
- supporting evidence;
- test coverage;
- risk and priority.

Do not execute destructive mutation experiments.

## 19. Serialization and public exposure

Find every place `AstroState` or its digest is:

- serialized;
- logged;
- placed in evidence;
- included in traces;
- included in snapshots;
- exposed through APIs;
- stored in cache metadata.

Determine whether Prompt-01 changes to digest or immutability could affect:

- internal debug output;
- golden snapshots;
- public JSON;
- trace IDs;
- cache persistence;
- backward compatibility.

Do not change public schemas or snapshots.

## 20. Test inventory and gap analysis

Locate tests covering:

### Construction and boundary

- raw input becomes normalized `AstroState`;
- predicates do not access raw input;
- predicates use normalized values;
- provider-specific data does not leak into predicates;
- invalid construction is rejected.

### Immutability

- outer mutation rejection;
- nested mapping mutation rejection;
- nested-list mutation rejection;
- caller-owned input mutation isolation;
- enrichment lifecycle;
- copy isolation.

### Digest

- same content produces the same digest;
- different content produces different digests;
- dictionary insertion order does not affect digest;
- version changes affect digest;
- enrichment changes affect digest or capability version;
- digest is stable across repeated construction;
- digest does not contain process memory identity;
- digest does not contain runtime telemetry.

### Cache integration

- equivalent states share logical cache identity;
- different states are isolated;
- mutation cannot produce stale cache results;
- enrichment-version changes invalidate relevant entries;
- object identity is not used as chart identity.

### Evaluation order

- predicate order does not change logical results;
- Yoga execution does not alter later predicate results;
- lazy enrichment does not produce hidden state changes;
- cold and warm evaluations are logically equivalent.

For every missing test category:

- identify the gap;
- explain its risk;
- recommend the likely test file;
- do not create the test.

## 21. Required classifications

Classify boundary access as:

- `COMPLIANT_ASTROSTATE_ACCESS`
- `ACCEPTABLE_PREPARATION_ACCESS`
- `DIRECT_ENRICHMENT_ACCESS_REQUIRING_REVIEW`
- `RAW_SOURCE_BOUNDARY_VIOLATION`
- `MUTATION_BOUNDARY_VIOLATION`
- `OBJECT_IDENTITY_DEPENDENCY`
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

## 22. Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- symbol name;
- line number or small range when practical;
- predicate or caller;
- accessed or mutated `AstroState` field;
- observed behavior;
- active-path evidence;
- relevant tests;
- expected Prompt-01 boundary;
- uncertainty where static analysis cannot prove runtime behavior.

Reconcile findings with Audits 1–8.

Explain:

- predicate access differences from Audit-2;
- caller implications from Audit-4;
- cache and model implications from Audit-5;
- canonicalization dependencies from Audit-6;
- parameter-versus-state distinctions from Audit-7;
- capability and mutation findings from Audit-8.

Do not modify previous reports.

## 23. Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify rules;
- modify previous audit reports;
- change `AstroState`;
- create a digest;
- change digest fields;
- add version metadata;
- freeze models;
- move enrichment logic;
- change predicate data access;
- change cache behavior;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-10.

You may run safe, non-mutating searches and tests.

Do not execute commands that update files, snapshots or generated artifacts.

## 24. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-09-AstroState-Boundary.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker instead of selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-09: AstroState Boundary

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–8
## 4. AstroState Definition Inventory
## 5. Construction and Preparation Pipeline
## 6. Predicate Data-Access Inventory
## 7. Raw Surya Siddhanta Boundary
## 8. AstroState Mutation Assessment
## 9. Deep Immutability Assessment
## 10. AstroState Query APIs
## 11. Digest and Content-Identity Inventory
## 12. Required Digest Coverage
## 13. Digest Canonicalization and Determinism
## 14. Object Identity and Cache Keys
## 15. Version Boundaries
## 16. Equality, Copying and Lifecycle
## 17. Evaluation-Order Dependencies
## 18. Serialization and Public Exposure
## 19. Existing Tests and Coverage Gaps
## 20. Prompt-01 Compliance Matrix
## 21. Migration Risks and Priorities
## 22. Unresolved Architectural Questions
## 23. Audit-9 Conclusion
```

### AstroState definition inventory

Include these columns:

| Definition | File | Symbol | Model Type | Active Status | Fields | Frozen | Deeply Immutable | Digest | Versioned | Raw Input Retained | Producers | Consumers | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Predicate data-access inventory

Include these columns:

| Predicate ID | File | Handler | AstroState Fields | Enrichments | Query APIs | Access Type | Raw Access | Mutation | Recomputation | Required Capability | Tests | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Mutation inventory

Include these columns:

| File | Symbol | Caller/Predicate | Mutated Field | Mutation Type | Lifecycle Stage | Active Path | Order Dependent | Cache Impact | Tests | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|

### Digest coverage matrix

Include these columns:

| Field or Version | Predicate Relevant | Current Digest Coverage | Evidence | Ordering Stable | Mutation Risk | Required Action | Scope | Priority |
|---|---|---|---|---|---|---|---|---|

### Version inventory

Include these columns:

| Version | Defined At | Stored In | Digest Included | Cache-Key Included | Serialized | Invalidation Behavior | Tests | Gap | Priority |
|---|---|---|---|---|---|---|---|---|---|

### Compliance matrix

Include these columns:

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- `AstroState` definitions;
- active `AstroState` definitions;
- registered predicates audited;
- canonical query APIs;
- direct enrichment-access paths;
- raw-source boundary violations;
- predicate-related mutation paths;
- evaluation-order dependencies;
- digest implementations;
- unsafe digest exclusions;
- object-identity cache dependencies;
- missing version boundaries;
- AstroState and digest test gaps;
- P0, P1, P2 and P3 findings.

## 25. Final response

After creating the report, stop.

Respond with only:

1. Audit-9 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Active AstroState definition count
6. Registered predicates audited
7. Raw-source boundary-violation count
8. Predicate-related mutation count
9. Object-identity dependency count
10. Digest coverage-gap count
11. Evaluation-order dependency count
12. Missing test-category count
13. Number of P0, P1, P2 and P3 findings
14. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-10.
