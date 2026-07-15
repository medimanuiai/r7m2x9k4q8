# Prompt-01 — Audit-18: Evidence Audit

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

If an expected report is missing:

- record it as a limitation;
- continue if Audit-18 can still be completed reliably;
- do not recreate or modify it;
- return `BLOCKED` only when the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-18: Evidence Audit**.

For every registered predicate, inspect the quality, correctness, completeness, immutability, determinism and downstream preservation of its evidence.

Determine whether evidence:

- exists for matched results;
- exists for unmatched results;
- records expected and actual values;
- explains missing capabilities without presenting negative astrological evidence;
- uses stable AstroState identifiers or canonical factual values;
- remains factual rather than interpretive;
- contains only JSON-safe deterministic values;
- is deeply immutable;
- survives condition aggregation, Yoga processing, domain processing and serialization;
- is logically equivalent between cold and warm cache evaluations.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Evidence boundary

Predicate evidence must describe factual observations supporting the predicate outcome.

Evidence may include:

- requested entity;
- actual observed value;
- expected value or comparison target;
- factual relationship;
- stable AstroState identifiers;
- capability availability;
- relevant configured rule or table version;
- deterministic factual calculation details.

Predicate evidence must not:

- calculate domain scores;
- assign weights;
- calculate confidence;
- resolve conflicts;
- generate narratives;
- recommend actions;
- construct public output;
- expose raw Surya Siddhanta payloads;
- expose raw exception details or stack traces;
- contain mutable live engine objects;
- hide missing capability as negative evidence.

Use Prompt-01 as authoritative if its exact evidence contract differs.

## 4. Repository-wide discovery

Search production code, tests, fixtures, predicates, condition evaluation, Yoga, domains, inference, caches, serializers and documentation.

Search for:

```text
evidence
PredicateResult
matched
actual
expected
reason
details
observed
source
planet
house
aspect
role
exalted
```

Find:

- every evidence producer;
- every evidence conversion;
- every evidence aggregator;
- every evidence consumer;
- evidence serialization;
- evidence mutation;
- evidence discarded by callers;
- evidence stored in caches;
- evidence embedded in Yoga or domain results;
- evidence shown in snapshots or public output.

Treat search matches as candidates. Inspect context before classifying them as predicate evidence.

## 5. Complete predicate evidence inventory

Using Audit-2 as a starting point, verify every registered predicate directly against current code.

For each predicate, report:

1. Predicate ID.
2. File and handler symbol.
3. Input parameters.
4. Evidence produced when matched.
5. Evidence produced when unmatched.
6. Evidence produced for missing capability.
7. Evidence produced for invalid parameters.
8. Evidence produced for error or timeout.
9. Expected values recorded.
10. Actual values recorded.
11. Entity identity used.
12. Data source or capability represented.
13. Evidence type and nested types.
14. Deep immutability.
15. JSON safety.
16. Deterministic ordering.
17. Factual correctness concerns.
18. Downstream preservation.
19. Existing tests.
20. Compliance, scope and priority.

Do not trust earlier counts without verifying current code.

## 6. Matched evidence

For every predicate, determine whether matched evidence clearly demonstrates why the predicate matched.

Assess whether it records enough factual information to independently understand the match without rerunning the predicate.

Examples may include:

```json
{
  "planet": "Mars",
  "actual_house": 10,
  "expected_house": 10
}
```

Do not require this exact schema. Evaluate the actual predicate semantics.

Identify matched evidence that is:

- absent;
- ambiguous;
- narrative-only;
- based only on input repetition;
- inconsistent with the matched outcome;
- dependent on unstable objects.

## 7. Unmatched evidence

For every predicate, determine whether an unmatched result preserves useful factual evidence.

Example:

```json
{
  "planet": "Mars",
  "actual_house": 7,
  "expected_house": 10
}
```

Identify predicates that return an empty evidence mapping for unmatched results even though an actual observed value is available.

Distinguish:

- fact evaluated and false;
- entity absent;
- capability unavailable;
- invalid parameters;
- evaluation failure.

Unmatched evidence must not falsely imply evaluation succeeded when required data was unavailable.

## 8. Expected-versus-actual values

For every comparison predicate, determine whether evidence includes:

- expected value;
- actual value;
- comparison operation;
- units where applicable;
- normalization applied;
- tolerance or orb where applicable;
- configured rule/table version where relevant.

Identify evidence that merely repeats input parameters without recording the observed fact.

## 9. Missing-capability and missing-entity evidence

Audit evidence for:

- missing AspectGraph;
- missing house data;
- missing planet data;
- missing varga;
- missing functional-role enrichment;
- missing strength data;
- missing evaluation context;
- other capabilities identified in Audit-8.

Determine whether evidence distinguishes:

```text
Capability unavailable
```

from:

```text
Capability available, requested fact absent or false
```

Missing capability must not produce misleading negative evidence.

## 10. Invalid-parameter and error evidence

Determine whether invalid parameters and errors are incorrectly stored as ordinary factual evidence.

Audit whether evidence contains:

- raw exception messages;
- stack traces;
- unvalidated caller input;
- internal object representations;
- sensitive raw payloads;
- provider-specific data.

Typed diagnostic information should reside in typed errors where required, while factual evidence remains factual.

Reconcile with Audits 7 and 17.

## 11. Entity identity and references

Determine how evidence identifies:

- planets;
- houses;
- signs;
- aspects;
- vargas;
- functional roles;
- rules or condition nodes;
- capabilities.

Classify identity as:

- `CANONICAL_STABLE_ID`
- `CANONICAL_NAME`
- `DISPLAY_NAME_ONLY`
- `OBJECT_REFERENCE`
- `MEMORY_IDENTITY`
- `RAW_PROVIDER_ID`
- `UNKNOWN`

Identify inconsistencies and alias risks, especially planet casing and Rahu/Ketu naming.

## 12. Deep immutability and defensive copying

Determine whether callers can mutate:

- the evidence mapping;
- nested mappings;
- lists;
- sets;
- dataclasses;
- custom domain objects;
- evidence returned from cache;
- caller-owned objects reused inside evidence.

Assess whether:

- defensive copies are made;
- lists become tuples;
- mappings become immutable;
- nested objects remain shared;
- one caller can corrupt later cache hits;
- construction helpers normalize evidence deeply.

Reconcile with Audits 5, 6 and 11.

## 13. JSON safety and canonicalization

Audit evidence handling for:

- dictionaries and key order;
- lists and tuples;
- sets and frozensets;
- enums;
- dataclasses;
- Pydantic models;
- dates and datetimes;
- decimal values;
- floats, NaN and infinity;
- UUIDs;
- custom objects;
- non-string keys;
- cycles.

Determine whether identical logical evidence serializes identically across repeated runs.

Do not design a repository-wide serialization framework.

## 14. Factual-boundary violations

Identify evidence containing:

- domain score;
- confidence;
- rule weight;
- interpretation;
- conflict resolution;
- narrative text as the only evidence;
- recommendation;
- public-output formatting.

Classify each as:

- `FACTUAL_EVIDENCE`
- `FACTUAL_WITH_EXTRA_INTERPRETATION`
- `DOMAIN_DATA_IN_PREDICATE_EVIDENCE`
- `NARRATIVE_ONLY`
- `OUTPUT_COUPLING`
- `UNKNOWN`

Do not remove or rewrite evidence.

## 15. Predicate-specific semantic review

Pay special attention to these predicates:

### PLANET_EXALTED

Verify whether the predicate checks the planet’s actual sign and/or longitude against the configured exaltation rule.

Determine whether evidence merely finds that an exaltation-degree mapping exists for the planet and incorrectly treats that as proof of current exaltation.

Record the actual data model, algorithm, evidence and suspected semantic issue.

Do not change the astrology semantics during the audit.

### ASPECT_EXISTS

Determine whether evidence distinguishes:

- AspectGraph missing;
- graph present but empty;
- graph present with no requested aspect;
- requested aspect found;
- malformed graph.

### PLANET_IN_HOUSE

Determine whether unmatched evidence records the actual house and expected house.

### FUNCTIONAL_ROLE

Determine whether evidence records prepared functional-role facts or results recomputed during predicate evaluation.

### HOUSE_OCCUPANT

Determine whether evidence identifies the requested house, requested occupant and actual occupants for matched and unmatched results.

## 16. Condition aggregation

Determine how the condition evaluator handles child evidence for:

- `AND`;
- `OR`;
- `NOT`;
- short-circuiting;
- skipped branches;
- nested conditions.

Identify whether child evidence is:

- preserved with identity;
- flattened;
- overwritten;
- discarded;
- merged with collisions;
- reordered nondeterministically;
- incorrectly negated by `NOT`.

Reconcile with Audit-12.

## 17. Yoga evidence preservation

Determine whether Yoga:

- preserves predicate evidence;
- preserves unmatched evidence where relevant;
- retains predicate and condition identity;
- converts evidence into legacy dictionaries;
- discards errors while retaining misleading evidence;
- duplicates evidence generation;
- mutates evidence;
- stores Yoga scores inside factual evidence.

Reconcile with Audit-15.

## 18. Domain evidence preservation

Determine whether domain runtimes:

- preserve factual evidence;
- associate evidence with indicators and rules;
- discard unmatched evidence;
- treat missing capability as negative evidence;
- add scores or confidence into predicate evidence;
- flatten evidence irreversibly;
- expose raw predicate evidence publicly.

Reconcile with Audit-16.

## 19. Cache equivalence

Compare evidence produced during:

- cold evaluation;
- stored cache value;
- warm retrieval.

Determine whether:

- evidence is logically equivalent;
- cached evidence is immutable;
- telemetry enters evidence;
- ordering changes;
- caller mutation corrupts later results;
- capability or version changes leave stale evidence.

## 20. Serialization and public exposure

Find every place evidence is serialized into:

- debug output;
- logs;
- snapshots;
- Yoga output;
- domain output;
- inference output;
- API or public JSON.

Determine whether Prompt-01 evidence normalization could affect:

- field names;
- list versus tuple representation;
- enum values;
- mapping order;
- schema versions;
- backward compatibility.

Do not modify serializers or snapshots.

## 21. Test inventory and gap analysis

Locate tests covering:

### Per-predicate evidence

- matched evidence;
- unmatched evidence;
- expected and actual values;
- missing capability;
- invalid parameters;
- errors;
- semantic correctness.

### Model safety

- deep immutability;
- defensive copying;
- JSON safety;
- canonical ordering;
- deterministic serialization;
- unsupported values.

### Aggregation and propagation

- condition aggregation;
- short-circuit evidence;
- Yoga preservation;
- domain preservation;
- output serialization;
- cold/warm cache equivalence.

### Priority predicates

- `PLANET_EXALTED` actual placement;
- `ASPECT_EXISTS` missing versus empty graph;
- `PLANET_IN_HOUSE` unmatched actual value;
- `FUNCTIONAL_ROLE` prepared enrichment evidence;
- `HOUSE_OCCUPANT` actual occupants.

For every missing test category:

- identify the gap;
- explain its risk;
- recommend the likely test file;
- do not create the test.

## 22. Required classifications

Classify evidence quality as:

- `COMPLETE_AND_FACTUAL`
- `ADEQUATE`
- `MATCHED_ONLY`
- `INCOMPLETE`
- `MISLEADING`
- `NONDETERMINISTIC`
- `NON_JSON_SAFE`
- `MISSING`
- `UNKNOWN`

Classify preservation as:

- `PRESERVED_END_TO_END`
- `PARTIALLY_PRESERVED`
- `FLATTENED_WITH_INFORMATION_LOSS`
- `DISCARDED`
- `OVERWRITTEN`
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

## 23. Evidence requirements for this audit

Every substantive finding must include:

- repository-relative file path;
- symbol name;
- line number or small range when practical;
- predicate ID or consumer;
- outcome/status being assessed;
- actual evidence shape;
- expected factual content;
- semantic or preservation risk;
- active-path evidence;
- existing tests;
- uncertainty where static analysis cannot prove behavior.

Include small redacted examples where useful. Do not reproduce sensitive raw inputs.

Reconcile findings with Audits 1–17 without modifying earlier reports.

## 24. Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify rules;
- modify previous audit reports;
- change astrology semantics;
- change evidence schemas;
- rewrite evidence;
- change condition aggregation;
- migrate Yoga or domain callers;
- change serialization;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-19.

You may run safe, non-mutating searches and tests.

Do not execute commands that update files, snapshots or generated artifacts.

## 25. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-18-Evidence.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker rather than selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-18: Evidence

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–17
## 4. Complete Predicate Evidence Inventory
## 5. Matched Evidence
## 6. Unmatched Evidence
## 7. Expected-versus-Actual Values
## 8. Missing-Capability and Missing-Entity Evidence
## 9. Invalid-Parameter and Error Evidence
## 10. Entity Identity and References
## 11. Deep Immutability and Canonicalization
## 12. Factual-Boundary Violations
## 13. Priority Predicate Semantic Review
## 14. Condition Evidence Aggregation
## 15. Yoga Evidence Preservation
## 16. Domain Evidence Preservation
## 17. Cache Equivalence
## 18. Serialization and Public Exposure
## 19. Existing Tests and Coverage Gaps
## 20. Prompt-01 Compliance Matrix
## 21. Migration Risks and Priorities
## 22. Unresolved Architectural Questions
## 23. Audit-18 Conclusion
```

### Predicate evidence inventory

| Predicate ID | File | Handler | Matched Evidence | Unmatched Evidence | Missing-Capability Evidence | Expected/Actual | Identity Type | Immutable | JSON-Safe | Deterministic | Semantic Concerns | Downstream Preservation | Tests | Quality | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Evidence propagation matrix

| Evidence Source | Predicate Result | Condition | Yoga | Domain | Output | Identity Preserved | Ordering Preserved | Information Lost | Preservation Classification | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Priority predicate matrix

| Predicate | Actual Algorithm | Matched Evidence | Unmatched Evidence | Missing-Data Behavior | Suspected Semantic Issue | Evidence Correct | Tests | Required Review | Priority |
|---|---|---|---|---|---|---|---|---|---|

### Evidence safety inventory

| File | Symbol | Predicate/Consumer | Mutable Value | Non-JSON Value | Raw Object/Input | Nondeterminism | Public Exposure | Current Protection | Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|

### Compliance matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- registered predicates audited;
- predicates with complete matched evidence;
- predicates with complete unmatched evidence;
- matched-only evidence predicates;
- predicates without evidence;
- predicates missing expected or actual values;
- misleading evidence paths;
- suspected semantic errors;
- missing-capability evidence conflations;
- invalid-parameter or exception data stored as evidence;
- unstable identity uses;
- mutable evidence risks;
- non-JSON-safe evidence risks;
- nondeterministic evidence mechanisms;
- condition evidence-loss paths;
- Yoga evidence-loss paths;
- domain evidence-loss paths;
- cold/warm evidence differences;
- public serialization impacts;
- missing evidence test categories;
- P0, P1, P2 and P3 findings.

## 26. Final response

After creating the report, stop.

Respond with only:

1. Audit-18 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Registered predicates audited
6. Complete matched, complete unmatched, matched-only and missing-evidence counts
7. Missing expected/actual and misleading-evidence counts
8. Suspected semantic-error count
9. Missing-capability evidence-conflation count
10. Mutable, non-JSON-safe and nondeterministic evidence counts
11. Condition, Yoga and domain evidence-loss counts
12. Cold/warm evidence-difference and public-serialization-impact counts
13. Missing test-category count
14. Number of P0, P1, P2 and P3 findings
15. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-19.