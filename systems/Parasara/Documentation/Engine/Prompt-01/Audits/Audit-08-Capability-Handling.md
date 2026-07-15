# Prompt-01 — Audit-8: Capability Handling Audit

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

If an expected report is missing:

- record it as a limitation;
- continue if Audit-8 can still be completed reliably;
- do not recreate or modify it;
- return `BLOCKED` only if the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-8: Capability Handling Audit**.

Determine how registered predicates identify and handle required `AstroState` capabilities, enrichments and factual data.

Find every path where missing capability or missing data is incorrectly treated as:

- an ordinary unmatched result;
- invalid parameters;
- empty evidence;
- an exception;
- an ignored condition;
- a partially evaluated predicate;
- negative evidence.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Core architectural rule

Prompt-01 requires a strict distinction between:

```text
Fact is available and false
    → unmatched

Required capability is unavailable
    → missing_capability

Caller supplied invalid parameters
    → invalid_parameters

Unexpected evaluation failure
    → error
```

Missing capability must not be interpreted as negative astrological evidence.

Example:

```text
AspectGraph exists and no requested aspect is present
    → unmatched

AspectGraph does not exist
    → missing_capability
```

Use the authoritative documents for exact status names and semantics.

## 4. Definition of capability

For this audit, a capability is a required, prepared source of factual information that a predicate expects from `AstroState`, its enrichments or evaluation context.

Candidate capabilities may include:

- normalized planets;
- houses;
- signs;
- ascendant or Lagna;
- house lords;
- aspects or `AspectGraph`;
- functional roles;
- dignity or exaltation data;
- planetary strength;
- Shadbala;
- vargas or divisional charts;
- Dasha timelines;
- transit positions;
- Yoga-related prepared facts;
- evaluation instant;
- system or plugin-specific enrichments.

Do not assume every candidate is formally a capability. Verify actual repository usage and document ambiguity.

## 5. Repository-wide discovery

Search the complete repository, including:

- `AstroState` models;
- enrichment containers;
- enrichment engines;
- predicate registry metadata;
- registered predicate handlers;
- generic predicate evaluator;
- condition evaluator;
- Yoga Engine;
- rule loaders and validators;
- domain runtimes;
- cache code;
- tests and fixtures;
- YAML and JSON rules;
- relevant architecture documentation.

Search for access patterns such as:

```python
astro.enrichments
astro.enrichments.get(...)
getattr(astro, ...)
getattr(astro, "enrichments", {})
dict.get(...)
or {}
or []
if not graph
if graph is None
if value is None
try:
    ...
except KeyError:
except AttributeError:
except Exception:
```

Also search for:

- `required_capabilities`;
- `capability`;
- `capabilities`;
- `missing_capability`;
- `MISSING_CAPABILITY`;
- `MISSING_ASPECT_GRAPH`;
- missing planet, house or varga errors;
- enrichment availability checks;
- lazy enrichment computation;
- default empty collections;
- fallback calculations;
- predicates that call enrichment engines;
- predicates that mutate or populate enrichments;
- Yoga code that prepares capabilities during evaluation.

Use search results only as candidates. Inspect context before classifying them.

## 6. Capability inventory

Identify every capability currently required or implicitly assumed by a registered predicate.

For each capability, report:

1. Canonical capability name, if one exists.
2. Alternate names or keys.
3. Owning model or enrichment.
4. Producer or enrichment engine.
5. Storage location in `AstroState`.
6. Version information, if any.
7. Predicates requiring it.
8. Whether the requirement is declared in registry metadata.
9. How availability is checked.
10. How absence is represented.
11. Current missing-capability outcome.
12. Expected Prompt-01 outcome.
13. Whether empty and missing are distinguishable.
14. Whether malformed and missing are distinguishable.
15. Existing tests.
16. Migration risk.

Do not invent canonical names when none exist. Record the lack of a canonical name.

## 7. Complete predicate capability assessment

For every registered predicate, determine:

- required capabilities;
- optional capabilities;
- exact `AstroState` fields accessed;
- enrichment keys accessed;
- evaluation-context values accessed;
- whether requirements are declared centrally;
- whether requirements are checked before evaluation;
- whether the handler performs its own checks;
- whether missing values receive empty defaults;
- whether missing capability becomes unmatched;
- whether missing data becomes invalid parameters;
- whether an exception is raised or swallowed;
- whether the predicate recomputes the capability;
- whether the predicate mutates `AstroState`;
- whether fallback logic duplicates an enrichment engine;
- whether evidence explains missing capability;
- whether errors identify the missing capability.

Use Audit-2’s predicate inventory as a starting point, but verify every predicate against current code.

## 8. Required-capability metadata audit

Determine whether predicate registrations store:

```text
required_capabilities
```

Assess:

1. Whether the field exists.
2. Whether it is mandatory.
3. Its type and representation.
4. Whether values are validated.
5. Whether duplicate capability names are normalized.
6. Whether names are versioned.
7. Whether registration rejects unknown capabilities.
8. Whether rule loading uses the metadata.
9. Whether runtime evaluation uses it.
10. Whether direct handler calls bypass it.
11. Whether test predicates declare it.
12. Whether optional capabilities can be expressed.
13. Whether capability dependencies affect cache keys.
14. Whether system-specific capabilities are supported.
15. Whether import order affects capability validation.

Compare these findings with Audit-1.

## 9. Missing versus empty versus false

Audit every relevant data access for distinctions among:

```text
Missing
Present but empty
Present but false
Present but malformed
Present with a legitimate zero value
Present but unsupported
```

Examples:

```python
graph = enrichments.get("aspects", {}) or {}
```

This may collapse:

- missing AspectGraph;
- `None`;
- empty graph;
- malformed false-like values.

Other risky patterns include:

```python
value = mapping.get(key)
if not value:
    ...
```

This may collapse:

- missing key;
- `None`;
- `False`;
- zero;
- empty collection;
- valid empty result.

For each collapse, report:

- file and symbol;
- values being conflated;
- current predicate outcome;
- expected distinction;
- evidence loss;
- migration risk.

## 10. Missing capability versus missing entity

Determine whether the architecture distinguishes:

```text
Capability unavailable
```

from:

```text
Capability available, but requested entity absent
```

Examples:

- planet collection unavailable versus named planet absent;
- houses unavailable versus house 10 absent;
- varga engine unavailable versus requested D9 absent;
- AspectGraph unavailable versus planet has no matching aspect;
- functional-role enrichment unavailable versus planet has no requested role.

For each case, identify:

- current behavior;
- Prompt-01 requirement;
- existing error or status;
- evidence produced;
- unresolved semantics.

Do not create new status categories. Flag unclear cases for architectural decision.

## 11. Malformed or stale capability data

Audit behavior when a capability exists but is malformed, incomplete or stale.

Examples include:

- wrong enrichment type;
- missing required keys;
- unknown version;
- incompatible version;
- partial graph;
- empty object used as a placeholder;
- unsupported varga;
- stale evaluation instant;
- enrichment generated for a different AstroState digest.

Determine whether such cases become:

- unmatched;
- missing capability;
- error;
- ignored data;
- partial evaluation;
- exception;
- unknown.

Distinguish malformed capability from unavailable capability where the architecture supports that distinction.

## 12. Predicate fallback and recomputation audit

Find predicates that:

- call enrichment engines;
- compute functional roles;
- compute aspects;
- calculate vargas;
- derive houses;
- populate missing data;
- construct fallback graphs;
- mutate enrichment dictionaries;
- access raw Surya Siddhanta JSON;
- call external services.

For each occurrence, report:

1. File and symbol.
2. Predicate ID.
3. Capability being recomputed.
4. Called engine or helper.
5. Whether computation is deterministic.
6. Whether it mutates `AstroState`.
7. Whether it bypasses capability checks.
8. Whether it changes cache assumptions.
9. Whether it violates predicate purity.
10. Whether it belongs in Prompt-01 or another stage.

Pay particular attention to `FUNCTIONAL_ROLE`, Yoga evaluation and AspectGraph preparation.

Do not remove or relocate computation during this audit.

## 13. AstroState mutation during capability handling

Find capability-related writes such as:

```python
astro.enrichments["..."] = value
astro.enrichments.update(...)
setattr(astro, ...)
integrate_vargas_into_astro(astro)
compute_aspect_graph(astro)
```

For every candidate mutation, determine:

- whether mutation occurs before predicate evaluation;
- whether it occurs inside a predicate;
- whether it occurs inside condition evaluation;
- whether Yoga triggers it;
- whether it occurs in a caller;
- whether it affects later predicate results;
- whether it invalidates the cache;
- whether behavior depends on evaluation order;
- whether tests rely on it.

Do not modify mutation behavior. Record Prompt-01 risks.

## 14. Capability readiness and evaluation order

Determine whether the engine has a defined preparation sequence such as:

```text
Normalize AstroState
→ execute enrichment engines
→ freeze AstroState
→ evaluate predicates
```

Report:

- where this sequence is implemented;
- whether it is enforced;
- whether callers can skip it;
- whether predicates assume enrichments without checking;
- whether Yoga performs preparation on demand;
- whether domains invoke predicates before readiness;
- whether test fixtures construct partially prepared states;
- whether capability readiness is explicit or inferred.

Identify evaluation-order dependencies.

## 15. Rule-loader and compiler interaction

Determine whether rules can be validated against predicate capability requirements before runtime.

Audit whether:

- predicate capability requirements are known at load time;
- rule loaders inspect them;
- incompatible rules are rejected;
- system-specific rules are checked against supported capabilities;
- missing capabilities cause compilation failure;
- missing capabilities are allowed as runtime states;
- Yoga has separate behavior;
- predicate versions affect capability validation.

Clearly distinguish:

- static rule-definition errors;
- runtime chart-specific missing capability;
- system-configuration incompatibility;
- future DSL/compiler responsibilities.

Do not expand compiler scope.

## 16. Evaluation-context capabilities

Identify predicates that require context outside core `AstroState`, such as:

- evaluation instant;
- timezone;
- Ayanamsa;
- transit date;
- Dasha reference time;
- system version;
- plugin version;
- normalization version;
- enrichment versions.

Determine:

- where the context is supplied;
- whether it is required or optional;
- whether it defaults to system time;
- how absence is handled;
- whether it is represented as a capability;
- whether it affects deterministic output;
- whether it affects cache keys;
- whether it is captured in inputs, evidence or traces.

Do not redesign evaluation context.

## 17. Cache interaction

Determine whether capability state and versions are reflected in predicate cache keys.

Audit whether the cache distinguishes:

- capability present versus absent;
- enrichment version changes;
- AstroState digest changes;
- partial versus complete enrichments;
- evaluation-context changes;
- dynamically computed capabilities;
- system/plugin versions;
- pre-mutation versus post-mutation AstroState.

Identify whether a cached unmatched result can remain after a capability becomes available.

Also determine whether missing-capability results are cached and whether that behavior is safe.

Do not redesign the cache during this audit.

## 18. Evidence and error quality

For every missing-capability path, determine whether the result records:

- predicate ID;
- capability name;
- stable error code;
- safe message;
- recoverability;
- requested entity;
- capability version;
- available alternatives;
- evidence explaining why evaluation could not proceed.

Identify cases where missing capability produces:

- empty evidence;
- misleading negative evidence;
- an ordinary unmatched reason;
- raw exceptions;
- no error.

Do not prescribe narrative explanations. Keep evidence factual.

## 19. Test inventory and gap analysis

Locate tests covering:

### General capability behavior

- capability present and fact true;
- capability present and fact false;
- capability missing;
- capability set to `None`;
- capability present but empty;
- capability malformed;
- capability version mismatch;
- optional capability absent.

### Status and error behavior

- `missing_capability` status;
- distinction from unmatched;
- distinction from invalid parameters;
- stable error code;
- capability name in error details;
- recoverability;
- safe exception handling.

### Predicate-specific behavior

- missing AspectGraph;
- empty AspectGraph;
- missing functional-role enrichment;
- missing houses;
- missing planet collection;
- missing varga;
- missing strength data;
- missing evaluation context.

### Purity and readiness

- predicate does not compute enrichment;
- predicate does not mutate `AstroState`;
- evaluation order does not affect logical result;
- partially prepared AstroState produces a typed result;
- capability preparation occurs before evaluation.

### Cache behavior

- missing-capability result isolation;
- capability-version isolation;
- enrichment change isolation;
- no stale unmatched result after capability preparation.

For every missing test category:

- identify the gap;
- explain its risk;
- recommend the likely test file;
- do not create the test.

## 20. Required classifications

Classify capability handling as:

- `EXPLICIT`
- `IMPLICIT`
- `FALLBACK_BASED`
- `RECOMPUTED`
- `MISSING_AS_UNMATCHED`
- `MISSING_AS_ERROR`
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
- predicate ID;
- required capability;
- observed availability check;
- current missing-capability outcome;
- expected Prompt-01 outcome;
- evidence and error behavior;
- caller or test evidence where applicable;
- uncertainty where static analysis cannot prove runtime behavior.

Reconcile findings with Audits 1–7.

Explain:

- capability requirements missing from Audit-1 metadata;
- differences from Audit-2’s predicate inventory;
- legacy behavior identified by Audit-3;
- caller risks identified by Audit-4;
- status and error dependencies from Audits 5 and 6;
- parameter-versus-capability boundary issues from Audit-7.

Do not modify earlier reports.

## 22. Scope restrictions

Do not:

- modify production code;
- modify tests;
- modify rules or fixtures;
- modify previous audit reports;
- add capability metadata;
- add status or error models;
- compute or populate enrichments;
- mutate `AstroState`;
- change cache behavior;
- change astrology semantics;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-9.

You may run safe, non-mutating searches and tests.

Do not execute commands that update files, snapshots or generated artifacts.

## 23. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-08-Capability-Handling.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker rather than selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-08: Capability Handling

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–7
## 4. Capability Definition and Repository Model
## 5. Complete Capability Inventory
## 6. Predicate-to-Capability Matrix
## 7. Required-Capability Registry Metadata
## 8. Missing, Empty, False and Malformed Data
## 9. Missing Capability versus Missing Entity
## 10. Predicate Fallback and Recomputation
## 11. AstroState Mutation and Evaluation Order
## 12. Capability Readiness and Preparation Sequence
## 13. Rule Loader and Compiler Interaction
## 14. Evaluation-Context Capabilities
## 15. Cache and Capability-Version Interaction
## 16. Evidence and Error Quality
## 17. Existing Tests and Coverage Gaps
## 18. Prompt-01 Compliance Matrix
## 19. Migration Risks and Priorities
## 20. Unresolved Architectural Questions
## 21. Audit-8 Conclusion
```

### Capability inventory

Include these columns:

| Capability | Alternate Names | Owner/Producer | AstroState Location | Versioned | Required By | Registry Declared | Availability Check | Missing Representation | Empty Distinguishable | Tests | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Predicate-to-capability matrix

Include these columns:

| Predicate ID | Required Capability | Optional Capability | Data Access | Declared in Registry | Prechecked | Missing Outcome | Empty Outcome | Recomputed | Mutates State | Error/Evidence | Tests | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Missing-data distinction matrix

Include these columns:

| Predicate | Scenario | Current Behavior | Current Status | Expected Behavior | Evidence Produced | Error Produced | Distinction Preserved | Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|

### Recomputation and mutation inventory

Include these columns:

| File | Symbol | Predicate/Caller | Capability | Operation | Recomputes | Mutates AstroState | Order Dependent | Cache Risk | Prompt-01 Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Compliance matrix

Include these columns:

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- registered predicates audited;
- distinct required capabilities;
- predicates declaring capabilities in registry metadata;
- predicates with implicit capability dependencies;
- missing-capability-to-unmatched paths;
- missing-versus-empty conflations;
- missing-capability-versus-missing-entity conflations;
- predicates recomputing capabilities;
- predicate or evaluator AstroState mutations;
- capability-related cache risks;
- capability handling test gaps;
- P0, P1, P2 and P3 findings.

## 24. Final response

After creating the report, stop.

Respond with only:

1. Audit-8 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Registered predicates audited
6. Distinct capability count
7. Implicit capability-dependency count
8. Missing-capability-to-unmatched path count
9. Missing-versus-empty conflation count
10. Capability recomputation or AstroState mutation count
11. Capability-related test-gap count
12. Number of P0, P1, P2 and P3 findings
13. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-9.
