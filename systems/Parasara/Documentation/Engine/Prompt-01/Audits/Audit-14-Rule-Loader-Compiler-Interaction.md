# Prompt-01 — Audit-14: Rule Loader and Compiler Interaction Audit

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

If an expected report is missing:

- record it as a limitation;
- continue if Audit-14 can still be completed reliably;
- do not recreate or modify the missing report;
- return `BLOCKED` only when the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-14: Rule Loader and Compiler Interaction Audit**.

Determine how predicate definitions and condition trees move through:

```text
YAML, JSON or Python rule source
→ parsing
→ loading
→ normalization
→ validation
→ optional compilation
→ runtime condition evaluation
→ predicate registry
```

Audit whether rule-definition errors are detected before runtime and whether Prompt-01 can introduce typed predicate contracts without improperly expanding into later DSL/compiler work.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Key questions

Determine:

1. When predicate IDs are validated.
2. Whether unknown predicates are rejected before evaluation.
3. Whether predicate parameters are validated.
4. Whether predicate versions are validated.
5. Whether required capabilities are validated.
6. Whether logical operators are validated.
7. Whether condition shapes are normalized.
8. Whether duplicate rule IDs are rejected.
9. Whether duplicate condition IDs are rejected.
10. Whether rules are evaluated directly from raw YAML or JSON.
11. Whether an AST or compiled execution plan exists.
12. Whether Yoga uses a separate loader.
13. Whether domain systems use separate loaders.
14. Whether registry import order affects validation.
15. What Prompt-01 must change.
16. What belongs to a later DSL/compiler stage.

## 4. Scope boundary

Prompt-01 requires a reliable predicate contract and must not silently treat rule-definition errors as factual non-matches.

However, this audit must not:

- design a new DSL;
- implement a grammar;
- create a complete AST;
- create an execution-plan compiler;
- implement macros or references;
- rewrite rule files;
- broaden operator support;
- redesign rule governance;
- implement Prompt-02 `RuleMatch`.

Separate findings into:

- `PROMPT_01_REQUIRED`
- `TEMPORARY_COMPATIBILITY`
- `FUTURE_DSL_COMPILER_STAGE`
- `UNRELATED`

## 5. Repository-wide discovery

Search the complete repository for:

- rule loaders;
- YAML and JSON parsers;
- schemas;
- validators;
- linters;
- compilers;
- AST models;
- execution-plan models;
- rule registries;
- rule factories;
- Yoga rule loaders;
- domain rule loaders;
- condition normalization;
- predicate validation;
- duplicate-ID checks;
- version checks;
- capability checks;
- rule provenance checks;
- SME approval checks;
- direct raw-rule evaluation.

Search for terms and patterns such as:

```text
load_rule
load_rules
parse_rule
parse_rules
validate_rule
validate_rules
compile_rule
compile_rules
rule_lint
schema
predicate
predicate_id
condition
conditions
operator
version
required_capabilities
duplicate
sme_approved
yaml.safe_load
json.load
json.loads
```

Inspect Python, tests, scripts, workflows, YAML, JSON and documentation.

Do not rely only on known loader filenames.

## 6. Loader and validator inventory

Identify every rule loader, validator, linter or compiler-like component.

For each component, report:

1. File and symbol.
2. Component category.
3. Rule system or owner.
4. Input format.
5. Output format.
6. Supported condition formats.
7. Predicate validation.
8. Parameter validation.
9. Version validation.
10. Capability validation.
11. Operator validation.
12. Duplicate-ID validation.
13. Error contract.
14. Source-location preservation.
15. Registry dependency.
16. Import-order dependency.
17. Production, CI, test or tooling status.
18. Callers.
19. Existing tests.

Classify each as:

- `PRODUCTION_LOADER`
- `PRODUCTION_VALIDATOR`
- `CI_LINTER`
- `RUNTIME_NORMALIZER`
- `COMPILER_OR_COMPILER_SCAFFOLD`
- `YOGA_SPECIFIC_LOADER`
- `DOMAIN_SPECIFIC_LOADER`
- `TEST_ONLY_HELPER`
- `DOCUMENTATION_ONLY`
- `UNKNOWN`

## 7. Rule-source inventory

Identify every rule source that can reach runtime evaluation.

For each source, report:

- path;
- format;
- rule system;
- loader;
- validator;
- runtime consumer;
- condition format;
- predicate IDs;
- schema or version;
- active-path evidence;
- test coverage.

Distinguish:

- production rules;
- examples;
- test fixtures;
- generated rules;
- deprecated rules;
- documentation samples.

Reconcile with Audit-13.

## 8. End-to-end rule path

For each active rule system, trace:

```text
Source file or Python object
→ parser
→ loader
→ normalization
→ validation
→ compiled or runtime representation
→ condition evaluator
→ predicate evaluator
```

At every boundary, report:

1. Input type.
2. Output type.
3. Validation performed.
4. Information added.
5. Information discarded.
6. Error behavior.
7. Whether raw dictionaries remain.
8. Whether source location is preserved.
9. Whether deterministic ordering is preserved.
10. Whether the predicate registry must already be initialized.

Identify paths that skip loading or validation.

## 9. Unknown predicate validation

Determine what happens when a rule contains an unknown predicate ID.

Audit behavior at:

- parsing;
- loading;
- linting;
- validation;
- compilation;
- direct runtime evaluation;
- Yoga evaluation;
- domain evaluation.

Classify each path as:

- `REJECTED_AT_LOAD`
- `REJECTED_AT_COMPILE`
- `REJECTED_BY_CI_ONLY`
- `RUNTIME_TYPED_ERROR`
- `RUNTIME_EXCEPTION`
- `RUNTIME_UNMATCHED`
- `SILENTLY_IGNORED`
- `UNKNOWN`

Unknown predicates should not silently become ordinary unmatched facts.

Identify whether CI-only validation can be bypassed during runtime.

## 10. Predicate parameter-schema validation

Determine whether rule parameters are validated against predicate-specific schemas.

Audit:

- required parameters;
- optional parameters;
- types;
- ranges;
- allowed values;
- aliases;
- defaults;
- unknown fields;
- cross-field validation.

For every loader or validator, determine:

- whether registry metadata supplies the schema;
- whether validation occurs before normalization;
- whether validation occurs after normalization;
- whether runtime revalidates;
- whether direct Python-created conditions bypass validation;
- whether Yoga follows the same path;
- whether invalid parameters become unmatched.

Reconcile with Audit-7.

## 11. Predicate-version validation

Determine whether rule condition nodes can specify a predicate version.

Audit:

- version field name;
- required or optional status;
- default resolution;
- registry comparison;
- compatibility ranges;
- unknown versions;
- deprecated versions;
- replacement predicates;
- cache implications;
- error reporting.

Classify current version behavior as:

- `EXACT_VERSION_VALIDATED`
- `VERSION_RANGE_VALIDATED`
- `IMPLICIT_CURRENT_VERSION`
- `IGNORED`
- `UNSUPPORTED`
- `UNKNOWN`

Do not design version-range semantics.

## 12. Required-capability validation

Determine whether loaders or compilers inspect predicate `required_capabilities`.

Separate:

```text
Static system capability incompatibility
```

from:

```text
Runtime chart-specific capability absence
```

For example:

- a rule requiring a predicate unsupported by the current system may be a load or compile error;
- a supported predicate whose required enrichment is missing for a particular evaluation may produce `missing_capability`.

Report whether the current architecture distinguishes these cases.

Reconcile with Audit-8.

## 13. Logical operator validation

Determine whether loaders validate:

- supported operators;
- operator case;
- child count;
- child type;
- empty `AND`;
- empty `OR`;
- `NOT` arity;
- unknown operators;
- excessive nesting;
- malformed logical nodes.

Determine whether invalid operators reach runtime and become:

- unmatched;
- predicate IDs;
- exceptions;
- typed errors;
- ignored nodes.

Reconcile with Audits 12 and 13.

## 14. Duplicate identity audit

Audit duplicate handling for:

- rule IDs;
- condition IDs;
- predicate IDs;
- aliases;
- Yoga IDs;
- domain rule IDs;
- references;
- macro names, if any.

For each identity type, determine:

- where duplicates are detected;
- whether the first or last definition wins;
- whether import or file order affects the winner;
- whether duplicates are rejected;
- whether CI and runtime behavior differ;
- whether tests cover duplicates.

Do not redesign identity management.

## 15. Registry initialization and import order

Determine whether rule validation depends on predicate modules having already been imported.

Audit:

- explicit registry bootstrap;
- implicit decorator side effects;
- package import order;
- dynamic plugin loading;
- test registrations;
- loader imports;
- circular-import workarounds.

Assess scenarios where:

- a valid predicate appears unknown because its module was not imported;
- validation results depend on test order;
- duplicate registration depends on import order;
- system-specific registries are incomplete at validation time.

Reconcile with Audit-1.

## 16. Raw rule evaluation

Determine whether any path evaluates raw YAML/JSON dictionaries without producing a validated intermediate representation.

For every such path, report:

1. Source.
2. Loader or missing loader.
3. Runtime consumer.
4. Validation skipped.
5. Normalization skipped.
6. Unknown-predicate risk.
7. Invalid-parameter risk.
8. Unknown-operator risk.
9. Active-path evidence.
10. Migration classification.

Do not require a complete compiler if a validated immutable internal model would satisfy Prompt-01.

## 17. AST and compiler status

Identify any existing:

- grammar;
- parser;
- AST nodes;
- condition models;
- compiled-rule models;
- execution plans;
- bytecode or instruction representation;
- macro expansion;
- reference resolution.

For each, classify it as:

- `ACTIVE_PRODUCTION`
- `PARTIAL_SCAFFOLD`
- `TEST_ONLY`
- `DOCUMENTATION_ONLY`
- `PLANNED`
- `LEGACY`
- `UNKNOWN`

Determine whether Prompt-01 depends on it or whether it belongs to a later stage.

Do not implement or complete compiler scaffolding.

## 18. Yoga loader interaction

Determine whether Yoga uses:

- the generic rule loader;
- a Yoga-specific loader;
- raw YAML/JSON;
- Python-created rules;
- separate validation;
- separate predicate lookup;
- separate condition formats;
- custom fallback evaluation.

Report differences in:

- predicate validation;
- parameter validation;
- operator validation;
- duplicate IDs;
- versions;
- capabilities;
- error behavior.

Audit-15 will perform the complete Yoga audit. Keep this section focused on loader/compiler interaction.

## 19. Domain loader interaction

Inspect Career and every other implemented domain.

Determine whether domain rules:

- use the generic loader;
- use a domain-specific loader;
- construct conditions in Python;
- bypass predicate validation;
- bypass condition normalization;
- rely on raw booleans;
- embed scoring metadata alongside predicate parameters.

Identify Prompt-01 compatibility risks without auditing domain scoring comprehensively. Audit-16 will cover domain runtime behavior.

## 20. Error reporting and source location

Determine whether loader and validation errors include:

- file path;
- rule ID;
- condition path;
- line and column;
- predicate ID;
- parameter name;
- stable error code;
- safe message;
- suggested correction;
- multiple-error aggregation.

Identify paths that:

- expose raw stack traces;
- swallow validation errors;
- continue loading partial rules;
- convert errors into runtime unmatched results;
- lose source location during normalization.

## 21. Determinism

Audit whether rule loading and validation are deterministic.

Check:

- filesystem traversal order;
- mapping iteration;
- set iteration;
- duplicate resolution order;
- registry iteration order;
- import order;
- generated UUIDs;
- timestamps;
- environment-dependent paths;
- mutable global registries;
- different YAML loader behavior.

Determine whether identical rule sources produce identical validated representations and error ordering.

## 22. CI versus runtime enforcement

Inspect:

- GitHub Actions;
- pytest configuration;
- rule-lint scripts;
- SME approval gates;
- local validation commands;
- pre-commit hooks;
- build scripts.

Determine:

- which validations run only in CI;
- which validations run at application startup;
- which run at rule load;
- which run only in tests;
- whether runtime can load rules that CI would reject;
- whether developers can bypass validation accidentally.

Do not change CI.

## 23. Prompt-01 versus future-stage classification

For each identified gap, classify whether it belongs to:

### Prompt-01

Examples may include:

- unknown predicate must not silently become unmatched;
- registry must expose metadata needed for validation;
- invalid parameters must produce the correct typed outcome;
- active rule paths must use the generic predicate boundary;
- condition results must preserve typed predicate results.

### Temporary compatibility

Examples may include:

- accepting an active legacy condition shape through a documented normalizer;
- preserving current rule files during contract migration.

### Future DSL/compiler stage

Examples may include:

- formal grammar;
- complete AST;
- macro expansion;
- reference resolution;
- optimized execution plan;
- static type inference;
- advanced compiler diagnostics.

Do not automatically assign all loader gaps to Prompt-01.

## 24. Test inventory and gap analysis

Locate tests covering:

### Loading and parsing

- valid YAML;
- valid JSON;
- malformed source;
- deterministic loading;
- multiple files;
- empty rule sets.

### Predicate validation

- known predicate;
- unknown predicate;
- registry not initialized;
- alias;
- duplicate registration;
- deprecated predicate;
- predicate version mismatch.

### Parameter validation

- missing required parameter;
- invalid type;
- invalid value;
- unknown parameter;
- alias normalization;
- default application.

### Operator validation

- valid `AND`;
- valid `OR`;
- valid `NOT`;
- unknown operator;
- wrong arity;
- malformed children;
- excessive nesting if bounded.

### Duplicate identities

- duplicate rule ID;
- duplicate Yoga ID;
- duplicate condition ID;
- deterministic duplicate error.

### Integration

- loader to condition evaluator;
- loader to predicate registry;
- Yoga loader path;
- domain loader path;
- CI linter versus runtime validation;
- error source location.

For every missing test category:

- identify the gap;
- explain the risk;
- recommend the likely test file;
- do not create the test.

## 25. Required classifications

Classify validation timing as:

- `PARSE_TIME`
- `LOAD_TIME`
- `COMPILE_TIME`
- `CI_ONLY`
- `RUNTIME`
- `NOT_VALIDATED`
- `UNKNOWN`

Classify loader paths as:

- `GENERIC_VALIDATED_PATH`
- `SPECIALIZED_VALIDATED_PATH`
- `RAW_RUNTIME_PATH`
- `PARTIALLY_VALIDATED_PATH`
- `TEST_ONLY_PATH`
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
- loader, validator or compiler component;
- input and output contract;
- observed validation timing;
- active-path evidence;
- existing tests;
- Prompt-01 versus future-stage classification;
- uncertainty where static analysis cannot prove runtime behavior.

Reconcile findings with Audits 1–13, especially:

- registry behavior from Audit-1;
- predicate inventory from Audit-2;
- caller paths from Audit-4;
- parameter validation from Audit-7;
- capability validation from Audit-8;
- condition evaluation from Audit-12;
- condition formats from Audit-13.

Do not modify earlier reports.

## 27. Scope restrictions

Do not:

- modify production code;
- modify tests or fixtures;
- modify YAML or JSON rules;
- modify previous audit reports;
- add schemas;
- create an AST;
- implement a compiler;
- add macros or references;
- change loader behavior;
- change validation behavior;
- update CI;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-15.

You may run safe, non-mutating searches, parsers and tests.

Do not execute commands that rewrite files, update snapshots or generate persistent artifacts.

## 28. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-14-Rule-Loader-Compiler-Interaction.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker rather than selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-14: Rule Loader and Compiler Interaction

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–13
## 4. Loader, Validator and Compiler Inventory
## 5. Rule-Source Inventory
## 6. End-to-End Rule Paths
## 7. Unknown Predicate Validation
## 8. Predicate Parameter-Schema Validation
## 9. Predicate-Version Validation
## 10. Required-Capability Validation
## 11. Logical Operator Validation
## 12. Duplicate Identity Handling
## 13. Registry Initialization and Import Order
## 14. Raw Rule Evaluation Paths
## 15. AST and Compiler Status
## 16. Yoga Loader Interaction
## 17. Domain Loader Interaction
## 18. Error Reporting and Source Location
## 19. Determinism
## 20. CI versus Runtime Enforcement
## 21. Prompt-01 versus Future-Stage Classification
## 22. Existing Tests and Coverage Gaps
## 23. Prompt-01 Compliance Matrix
## 24. Migration Risks and Priorities
## 25. Unresolved Architectural Questions
## 26. Audit-14 Conclusion
```

### Loader and validator inventory

Include these columns:

| Component | File | Symbol | Category | Rule System | Input | Output | Predicate Validation | Parameter Validation | Version Validation | Capability Validation | Operator Validation | Duplicate Validation | Registry Dependency | Callers | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### End-to-end rule-path inventory

Include these columns:

| Rule System | Source | Parser | Loader | Normalizer | Validator | Compiler/Representation | Evaluator | Raw Dictionaries Reach Runtime | Validation Gaps | Active Evidence | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|

### Validation-timing matrix

Include these columns:

| Validation | Rule System | Parse | Load | Compile | CI | Runtime | Not Validated | Bypass Path | Current Failure | Required Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|

### Unknown predicate and operator matrix

Include these columns:

| Path | Unknown Item | Validation Stage | Current Outcome | Runtime Reachable | Becomes Unmatched | Error Contract | Required Prompt-01 Behavior | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|

### Prompt-01 versus future-stage matrix

Include these columns:

| Finding | Current Behavior | Required Outcome | Classification | Dependency | Blocking Prompt-01 | Priority | Rationale |
|---|---|---|---|---|---|---|---|

### Compliance matrix

Include these columns:

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- loaders discovered;
- validators discovered;
- CI linters discovered;
- compiler or AST components;
- active rule systems;
- generic validated paths;
- specialized validated paths;
- raw runtime paths;
- unknown-predicate-to-unmatched paths;
- unknown-operator-to-unmatched paths;
- paths without parameter validation;
- paths without version validation;
- paths without capability validation;
- duplicate identities not rejected;
- registry import-order risks;
- CI-only validations;
- Prompt-01 findings;
- temporary compatibility findings;
- future DSL/compiler findings;
- missing loader/compiler test categories;
- P0, P1, P2 and P3 findings.

## 29. Final response

After creating the report, stop.

Respond with only:

1. Audit-14 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Loader, validator, linter and compiler-component counts
6. Active rule-system count
7. Generic, specialized and raw runtime path counts
8. Unknown-predicate/operator incorrect-outcome counts
9. Parameter, version and capability validation-gap counts
10. Duplicate-identity and import-order risk counts
11. Prompt-01, compatibility and future-stage finding counts
12. Missing test-category count
13. Number of P0, P1, P2 and P3 findings
14. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-15.