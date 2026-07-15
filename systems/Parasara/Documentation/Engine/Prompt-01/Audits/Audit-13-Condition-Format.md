# Prompt-01 — Audit-13: Condition-Format Inventory

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

If an expected report is missing:

- record it as a limitation;
- continue if Audit-13 can still be completed reliably;
- do not recreate or modify it;
- return `BLOCKED` only when the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-13: Condition-Format Inventory**.

Find, classify and document every condition-tree representation currently used or accepted by the repository.

Inspect condition formats in:

- YAML rules;
- JSON rules;
- Python-created condition trees;
- tests and fixtures;
- Yoga rules;
- domain rules;
- loaders and validators;
- condition evaluators;
- conversion or compatibility adapters;
- documentation examples.

Determine:

1. The canonical current format, if one exists.
2. Every alternate or legacy format.
3. Which formats are active.
4. Which loaders or evaluators accept each format.
5. How aliases and casing are normalized.
6. How predicate parameters are nested.
7. What compatibility must be preserved during Prompt-01.
8. Which format issues belong to later DSL/compiler work.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Scope boundary

Audit condition syntax and representation only as needed for Prompt-01 compatibility.

Do not:

- design a new DSL;
- create a grammar;
- create an AST;
- implement a compiler;
- rewrite rule files;
- standardize all condition files;
- expand supported operators;
- implement macros or references;
- change astrology semantics.

Prompt-01 must preserve currently valid condition inputs while establishing the typed predicate-result boundary.

Clearly separate:

- current active formats;
- legacy compatibility formats;
- malformed or unsupported formats;
- future DSL/compiler concepts.

## 4. Repository-wide discovery

Search the complete repository, not only known rule directories.

Inspect:

- `*.yaml`;
- `*.yml`;
- `*.json`;
- Python source;
- tests and fixtures;
- scripts;
- examples;
- documentation.

Search for structures and keys such as:

```text
condition
conditions
predicate
predicate_id
params
parameters
type
op
operator
children
args
all
any
not
reference
macro
```

Search for predicate IDs identified by Audit-2.

Also search for code that:

- constructs condition dictionaries;
- converts one condition shape into another;
- renames keys;
- normalizes case;
- unwraps `condition` or `conditions`;
- accepts lists as implicit logical groups;
- injects default operators;
- converts Yoga conditions;
- serializes or deserializes condition trees.

Use search results as candidates. Inspect their actual use before classifying them.

## 5. Required condition shapes to verify

Search for and document variants such as:

```yaml
type: AND
children:
  - predicate: PLANET_IN_HOUSE
    params:
      planet: Mars
      house: 10
```

```yaml
predicate: PLANET_IN_HOUSE
params:
  planet: Mars
  house: 10
```

```yaml
condition:
  predicate: PLANET_IN_HOUSE
  params: {}
```

```yaml
conditions:
  - predicate: PLANET_IN_HOUSE
    params: {}
```

```yaml
op: AND
args:
  - predicate: PLANET_IN_HOUSE
    params: {}
```

These are examples to verify, not assumptions that every shape exists.

Also identify:

- top-level condition lists;
- implicit `AND` lists;
- lowercase operator names;
- uppercase operator names;
- predicate names stored under `type`;
- parameters stored directly on a condition node;
- Yoga-specific formats;
- domain-specific wrappers;
- condition references;
- macro invocations;
- count or existence expressions.

Do not expand support for formats that are not currently active.

## 6. Complete condition-source inventory

Identify every source containing or creating condition trees.

For each source, report:

1. File path.
2. File type.
3. Rule system or owner.
4. Top-level container.
5. Condition root shape.
6. Logical-node shape.
7. Predicate-leaf shape.
8. Parameter shape.
9. Operators used.
10. Predicate IDs used.
11. Loader or consumer.
12. Production, test, example or documentation status.
13. Current validation.
14. Active-path evidence.

Group identical files when appropriate, but retain file-specific evidence for variants.

## 7. Canonical-format determination

Determine whether the repository has an explicitly documented canonical condition format.

Evidence may come from:

- authoritative architecture documents;
- Prompt-01;
- schemas;
- loader models;
- validators;
- dominant production rule files;
- condition evaluator expectations;
- tests.

Classify the canonical status as:

- `EXPLICITLY_DOCUMENTED`
- `SCHEMA_ENFORCED`
- `IMPLICITLY_DOMINANT`
- `MULTIPLE_CANONICAL_FORMATS`
- `NO_CANONICAL_FORMAT`
- `UNKNOWN`

Do not select a canonical format based only on frequency.

If documents, loaders and runtime disagree, record the disagreement.

## 8. Logical-node format inventory

For every logical-node shape, document:

- operator key;
- operator value;
- case sensitivity;
- child-container key;
- child-container type;
- minimum and maximum child counts;
- empty-child behavior;
- nested-node behavior;
- unknown-key behavior;
- loader normalization;
- evaluator support;
- test coverage.

Audit at least:

- `AND`;
- `OR`;
- `NOT`.

Also identify existing usage of:

- `ALL`;
- `ANY`;
- `EXISTS`;
- `COUNT`;
- `REFERENCE`;
- `MACRO`.

Do not assume these additional operators should be supported. Classify them as active, planned, documentation-only or unsupported.

## 9. Predicate-leaf format inventory

For every predicate-leaf shape, document:

1. Predicate-ID key.
2. Parameter-container key.
3. Whether parameters may be omitted.
4. Whether parameters may appear directly on the node.
5. Version field, if any.
6. Alias handling.
7. Case normalization.
8. Unknown-field handling.
9. Loader validation.
10. Evaluator expectations.
11. Serialization behavior.
12. Production examples.
13. Test examples.

Determine whether these or equivalent variants exist:

```yaml
predicate: PLANET_IN_HOUSE
params: {}
```

```yaml
predicate_id: PLANET_IN_HOUSE
parameters: {}
```

```yaml
type: PLANET_IN_HOUSE
params: {}
```

```yaml
PLANET_IN_HOUSE:
  planet: Mars
  house: 10
```

Do not add support for unused variants.

## 10. Wrapper-format inventory

Audit wrappers such as:

```yaml
condition: {}
```

```yaml
conditions: []
```

and rule structures that nest condition trees under other keys.

For each wrapper, determine:

- owning rule type;
- singular or plural semantics;
- whether a list implies `AND`, `OR` or another behavior;
- whether the loader unwraps it;
- whether the evaluator receives the wrapper;
- whether Yoga uses a different wrapper;
- whether empty wrappers are allowed;
- whether wrappers preserve source location.

## 11. YAML and JSON behavior

Determine whether YAML and JSON rule inputs behave identically.

Audit:

- scalar typing;
- booleans;
- integers;
- floats;
- `null`;
- duplicate YAML keys;
- anchors and aliases, if used;
- mapping order;
- case sensitivity;
- enum-like strings;
- numeric predicate parameters;
- serialization round trips.

Identify formats that work in YAML but not JSON, or vice versa.

Do not redesign parsing.

## 12. Python-created condition trees

Find every condition tree constructed directly in Python.

For each construction path, report:

1. File and symbol.
2. Exact shape created.
3. Purpose.
4. Whether production or test-only.
5. Whether it passes through a loader.
6. Whether it bypasses validation.
7. Whether it differs from file-based formats.
8. Whether callers mutate it.
9. Whether aliases or defaults are injected.
10. Prompt-01 compatibility risk.

Pay attention to dictionaries created inline inside tests, Yoga code and domain engines.

## 13. Loader normalization

Find every loader or adapter that normalizes condition formats.

Document transformations such as:

- `op` → `type`;
- `args` → `children`;
- `parameters` → `params`;
- lowercase → uppercase;
- singular wrapper → root condition;
- list → implicit logical node;
- aliases → canonical predicate IDs;
- direct parameters → nested parameter mapping;
- default operator injection.

For every transformation, report:

1. File and symbol.
2. Input shape.
3. Output shape.
4. Determinism.
5. Error behavior.
6. Unknown-field behavior.
7. Source-location preservation.
8. Existing tests.
9. Whether normalization occurs before validation.
10. Whether normalization occurs before cache-key construction.

## 14. Evaluator format support

For every evaluator identified by Audit-12, map the formats it accepts.

Determine whether:

- the canonical evaluator accepts normalized nodes only;
- raw YAML dictionaries reach the evaluator;
- Yoga accepts additional shapes;
- legacy evaluators accept different keys;
- malformed nodes fall through as predicate leaves;
- unknown operators become predicate IDs;
- lists are treated implicitly;
- wrapper nodes are handled by callers instead of the evaluator.

Identify mismatches between loader output and evaluator expectations.

## 15. Alias and case-sensitivity audit

Audit aliases for:

- operator keys;
- operator values;
- predicate-ID keys;
- parameter-container keys;
- predicate IDs;
- parameter names;
- wrapper keys.

For each alias, report:

- canonical form;
- accepted alias;
- normalization location;
- conflict behavior;
- case sensitivity;
- production use;
- tests;
- whether it must be preserved temporarily.

Determine what happens when both canonical and alias keys appear.

Do not create new aliases.

## 16. Parameter nesting and validation

Determine how each condition format carries predicate parameters.

Audit whether parameters are:

- under `params`;
- under `parameters`;
- directly embedded;
- absent;
- inherited;
- dynamically injected;
- represented as `null`;
- represented as a non-mapping value.

Determine:

- whether unknown parameters survive normalization;
- whether defaults are applied;
- whether aliases normalize;
- whether validation occurs before evaluation;
- whether source location is preserved for errors.

Reconcile with Audit-7.

## 17. Operator arity and empty-node behavior

Document format-level requirements for:

- zero-child `AND`;
- zero-child `OR`;
- zero-child `NOT`;
- single-child `AND`;
- single-child `OR`;
- single-child `NOT`;
- multi-child `NOT`;
- missing `children`;
- `children: null`;
- non-list children.

Separate:

- what the format permits;
- what loaders validate;
- what evaluators accept;
- what current rule files contain;
- what Prompt-01 requires.

Do not invent arity rules where the authoritative material is silent.

## 18. Unknown and extra fields

Determine whether nodes reject, ignore or preserve unknown keys.

For each format and loader, classify unknown-field behavior as:

- `REJECTED`
- `IGNORED`
- `PRESERVED`
- `FORWARDED`
- `INTERPRETED_AS_PARAMETERS`
- `UNKNOWN`

Identify misspellings that may silently change behavior, such as:

```yaml
childen: []
param: {}
predciate: PLANET_IN_HOUSE
```

Determine whether these become:

- load errors;
- runtime errors;
- unmatched conditions;
- empty conditions;
- ignored data.

## 19. Condition identity and source location

Determine whether condition nodes have stable identifiers or source references.

Search for:

- node IDs;
- rule IDs;
- condition IDs;
- YAML paths;
- line and column information;
- AST references;
- parent-child paths;
- generated UUIDs.

Assess whether trace and error reporting can identify the source condition deterministically.

Do not implement node identity.

## 20. References, macros and extended constructs

Identify any existing format support or usage for:

- references;
- reusable condition blocks;
- macros;
- `ALL`;
- `ANY`;
- `EXISTS`;
- `COUNT`;
- named conditions;
- external rule fragments.

For each construct, classify it as:

- `ACTIVE_PRODUCTION`
- `ACTIVE_TEST_ONLY`
- `DOCUMENTED_BUT_NOT_IMPLEMENTED`
- `PLANNED_FUTURE_STAGE`
- `LEGACY`
- `UNKNOWN`

Do not expand DSL scope or propose implementation as part of Prompt-01 unless required for compatibility.

## 21. Migration compatibility assessment

For every active format, determine whether Prompt-01’s typed results can be introduced without changing condition syntax.

Classify each format as:

- `PRESERVE_AS_IS`
- `PRESERVE_THROUGH_EXISTING_NORMALIZATION`
- `TEMPORARY_COMPATIBILITY_REQUIRED`
- `MIGRATION_REQUIRED_FOR_PROMPT_01`
- `FUTURE_DSL_MIGRATION`
- `UNRELATED`
- `UNKNOWN`

Identify exact compatibility risks involving:

- predicate versions;
- parameter schemas;
- required capabilities;
- `ConditionResult`;
- `NOT`;
- short-circuit behavior;
- unknown predicate validation;
- unknown operator validation.

Do not rewrite rule files.

## 22. Test inventory and gap analysis

Locate tests covering:

### Canonical formats

- predicate leaf;
- nested `AND`;
- nested `OR`;
- `NOT`;
- mixed nested conditions;
- parameters;
- wrappers.

### Alternate and legacy formats

- aliases;
- casing;
- `op/args`;
- `condition`;
- `conditions`;
- Yoga-specific shapes;
- Python-created shapes.

### Invalid formats

- missing predicate ID;
- missing operator;
- missing children;
- wrong child type;
- wrong parameter-container type;
- unknown keys;
- unknown operator;
- conflicting aliases;
- malformed nesting.

### Loader/evaluator integration

- normalization output;
- validation before evaluation;
- YAML and JSON equivalence;
- source-location preservation;
- canonical serialization;
- condition evaluator acceptance.

For every missing test category:

- identify the gap;
- explain the risk;
- recommend the likely test file;
- do not create the test.

## 23. Required classifications

Classify format status as:

- `CANONICAL`
- `ACTIVE_ALTERNATE`
- `LEGACY_COMPATIBILITY`
- `TEST_ONLY`
- `DOCUMENTATION_ONLY`
- `PLANNED_FUTURE`
- `MALFORMED_OR_UNSUPPORTED`
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

## 24. Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- line number or small range when practical;
- condition shape;
- loader or evaluator;
- production/test/documentation status;
- normalization behavior;
- validation behavior;
- active-path evidence;
- existing tests;
- uncertainty where static analysis cannot prove runtime use.

Include small representative examples, but do not copy entire rule files.

Reconcile findings with Audits 1–12, especially:

- predicate IDs from Audit-2;
- parameter shapes from Audit-7;
- condition evaluator behavior from Audit-12;
- caller and Yoga paths from Audits 4 and 12.

Do not modify earlier reports.

## 25. Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify YAML or JSON rules;
- modify previous audit reports;
- define a new canonical format;
- create schemas;
- change aliases;
- change casing behavior;
- add operators;
- implement macros or references;
- implement a DSL or compiler;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-14.

You may run safe, non-mutating searches, parsers and tests.

Do not run commands that rewrite files, update snapshots or generate persistent artifacts.

## 26. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-13-Condition-Format-Inventory.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker rather than selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-13: Condition-Format Inventory

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–12
## 4. Complete Condition-Source Inventory
## 5. Canonical-Format Assessment
## 6. Logical-Node Formats
## 7. Predicate-Leaf Formats
## 8. Wrapper Formats
## 9. YAML and JSON Differences
## 10. Python-Created Condition Trees
## 11. Loader Normalization
## 12. Evaluator Format Support
## 13. Aliases and Case Sensitivity
## 14. Parameter Nesting and Validation
## 15. Operator Arity and Empty Nodes
## 16. Unknown and Extra Fields
## 17. Condition Identity and Source Location
## 18. References, Macros and Extended Constructs
## 19. Migration Compatibility
## 20. Existing Tests and Coverage Gaps
## 21. Prompt-01 Compliance Matrix
## 22. Risks and Priorities
## 23. Unresolved Architectural Questions
## 24. Audit-13 Conclusion
```

### Condition-source inventory

Include these columns:

| Source File | Type | Owner/System | Root Shape | Logical Shape | Predicate Shape | Parameter Shape | Operators | Loader/Consumer | Status | Validation | Active Evidence | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Format inventory

Include these columns:

| Format ID | Representative Shape | Source Files | Logical Key | Children Key | Predicate Key | Parameters Key | Wrappers | Case Rules | Normalizer | Evaluators | Status | Compatibility | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Loader-normalization matrix

Include these columns:

| Loader | File | Input Format | Transformation | Output Format | Validation Before/After | Unknown Fields | Deterministic | Source Location Preserved | Tests | Risk |
|---|---|---|---|---|---|---|---|---|---|---|

### Evaluator support matrix

Include these columns:

| Evaluator | Canonical Format | Alternate Formats | Wrappers Accepted | Operators | Raw/Normalized Input | Unsupported Behavior | Active Callers | Tests | Priority |
|---|---|---|---|---|---|---|---|---|---|

### Compatibility matrix

Include these columns:

| Format | Active Use | Must Preserve | Existing Normalization | Prompt-01 Impact | Later DSL Impact | Required Classification | Risk | Priority |
|---|---|---|---|---|---|---|---|---|

### Compliance matrix

Include these columns:

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- condition-source files;
- distinct condition formats;
- canonical formats;
- active alternate formats;
- legacy compatibility formats;
- test-only formats;
- documentation-only formats;
- logical-node variants;
- predicate-leaf variants;
- wrapper variants;
- aliases and case-normalization rules;
- loader transformations;
- Python-created condition shapes;
- malformed formats silently accepted;
- active formats requiring Prompt-01 compatibility;
- future DSL-only constructs;
- missing condition-format test categories;
- P0, P1, P2 and P3 findings.

## 27. Final response

After creating the report, stop.

Respond with only:

1. Audit-13 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Condition-source file count
6. Distinct condition-format count
7. Canonical, active-alternate, legacy and test-only format counts
8. Logical-node, predicate-leaf and wrapper variant counts
9. Loader-normalization count
10. Silently accepted malformed-format count
11. Active compatibility-format count
12. Future DSL-only construct count
13. Missing test-category count
14. Number of P0, P1, P2 and P3 findings
15. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-14.