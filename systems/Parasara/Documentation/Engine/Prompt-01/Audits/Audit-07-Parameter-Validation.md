# Prompt-01 — Audit-7: Parameter Validation Audit

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

If an expected report is missing:

- record it as a limitation;
- continue if a reliable Audit-7 can still be completed;
- do not recreate or modify the missing report;
- return `BLOCKED` only if the missing information prevents a reliable audit.

## 2. Objective

Perform only **Audit-7: Parameter Validation Audit**.

Determine how every registered predicate currently declares, receives, normalizes and validates its parameters.

Identify where invalid parameters incorrectly become:

- ordinary unmatched results;
- missing-data results;
- runtime exceptions;
- silently ignored values;
- partially evaluated predicates;
- unsafe or nondeterministic inputs.

This is a repository-wide, read-only audit.

Do not implement corrections.

## 3. Architectural boundary

Predicate parameters must be validated before factual evaluation.

Prompt-01 requires the engine to distinguish at least:

```text
Valid parameters + fact true      → matched
Valid parameters + fact false     → unmatched
Invalid or missing parameters     → invalid_parameters
Missing required AstroState data  → missing_capability or another typed missing-data result
Unexpected execution failure      → error
```

Do not treat these outcomes as equivalent.

Parameter validation must not:

- calculate domain scores;
- assign rule weights;
- alter astrology semantics;
- mutate `AstroState`;
- read raw Surya Siddhanta input;
- depend on system time;
- silently coerce ambiguous values unless explicitly authorized;
- silently ignore unknown parameters unless Prompt-01 permits it.

## 4. Repository-wide discovery

Search the complete repository, including:

- predicate registry and definitions;
- predicate handlers;
- generic predicate evaluator;
- condition evaluator;
- rule loaders and validators;
- Yoga Engine;
- domain runtimes;
- tests and fixtures;
- YAML and JSON rule files;
- scripts and utilities;
- documentation and examples.

Search for parameter access and validation patterns such as:

```python
params.get(...)
params[...]
kwargs.get(...)
kwargs[...]
setdefault(...)
pop(...)
int(...)
float(...)
str(...)
bool(...)
isinstance(...)
assert ...
if not ...
if ... is None
try:
    ...
except ...
```

Also search for:

- Pydantic models;
- dataclasses used as parameter schemas;
- `TypedDict`;
- JSON Schema;
- Marshmallow or similar validators;
- custom validation functions;
- allowed-value tables;
- enum conversion;
- planet-name normalization;
- house-number validation;
- sign validation;
- role validation;
- varga validation;
- aspect-type validation;
- operator validation;
- unknown-key rejection;
- default-value injection;
- predicate-specific aliases;
- registry metadata describing parameter schemas.

Use search results as candidates. Inspect context before classifying code as predicate-parameter validation.

## 5. Complete predicate parameter inventory

Using Audit-2 as a starting point, verify every registered predicate directly against the current repository.

For each registered predicate, document:

1. Predicate ID.
2. File and handler symbol.
3. Handler signature.
4. Accepted parameter names.
5. Required parameters.
6. Optional parameters.
7. Default values.
8. Expected types.
9. Allowed values or ranges.
10. Aliases.
11. Case sensitivity.
12. Normalization behavior.
13. Coercion behavior.
14. Unknown-parameter behavior.
15. Missing-parameter behavior.
16. Invalid-type behavior.
17. Invalid-value behavior.
18. Cross-field validation.
19. Validation location.
20. Current failure result.
21. Expected Prompt-01 failure result.
22. Existing tests.
23. Migration risk.

Do not infer a parameter contract solely from rule examples. Confirm it using handler behavior, loaders, tests or authoritative documentation.

## 6. Parameter source and flow audit

Trace predicate parameters from their original source through evaluation.

Potential sources include:

- YAML rule files;
- JSON rule files;
- code-created condition trees;
- tests and fixtures;
- direct API calls;
- Yoga rules;
- domain code;
- macros or references;
- default parameters;
- dynamically constructed dictionaries.

For every distinct flow, identify:

```text
Parameter source
→ loader or parser
→ normalization
→ schema validation
→ condition evaluator
→ predicate evaluator
→ predicate handler
```

Determine at which stage:

- required keys are checked;
- unknown keys are rejected;
- types are validated;
- values are normalized;
- aliases are resolved;
- defaults are applied;
- versions are checked;
- errors are converted into typed results.

Report paths where validation is duplicated, delayed or absent.

## 7. Registry schema audit

Audit whether the predicate registry currently stores or enforces a parameter schema.

Determine:

1. Whether `parameter_schema` metadata exists.
2. Its representation.
3. Whether it is mandatory.
4. Whether registration validates it.
5. Whether rule loading uses it.
6. Whether runtime evaluation uses it.
7. Whether direct predicate calls bypass it.
8. Whether schemas are versioned.
9. Whether schemas are deterministic.
10. Whether aliases are part of the schema.
11. Whether defaults are declared centrally or inside handlers.
12. Whether unknown parameters are rejected.
13. Whether test-only predicates require schemas.
14. Whether invalid schemas can be registered.
15. Whether schema behavior depends on import order.

Compare the findings with Audit-1 and explain any differences.

## 8. Required and missing parameters

Find every predicate that accesses parameters using patterns such as:

```python
planet = params.get("planet")
house = params.get("house")
```

Determine whether a missing key:

- produces `None`;
- receives a default;
- causes an exception;
- produces `matched=False`;
- produces empty evidence;
- produces a typed invalid-parameter result;
- becomes indistinguishable from missing AstroState data.

Identify ambiguous cases such as:

```python
params.get("house")
```

where `None` could mean:

- the caller omitted the parameter;
- the caller explicitly supplied `None`;
- the loader removed an invalid value;
- the predicate could not find the house.

Report these distinctions precisely.

## 9. Type validation and coercion

Audit validation for:

- strings;
- integers;
- floats;
- booleans;
- lists;
- tuples;
- mappings;
- enums;
- `None`;
- numeric strings;
- arbitrary objects.

Pay particular attention to unsafe or ambiguous Python behavior:

```python
bool("false") is True
int(True) == 1
isinstance(True, int) is True
```

Determine whether inputs such as these are accepted:

```json
{"house": "7"}
{"house": "seven"}
{"house": 7.0}
{"house": true}
{"planet": 7}
{"planet": null}
{"enabled": "false"}
```

Do not decide whether coercion should be allowed unless the authoritative documents specify it.

Classify existing coercion as:

- `EXPLICIT_AND_DOCUMENTED`
- `EXPLICIT_BUT_UNDOCUMENTED`
- `IMPLICIT_LANGUAGE_COERCION`
- `AMBIGUOUS`
- `NO_COERCION`
- `UNKNOWN`

## 10. Domain-value validation

Audit validation and normalization for domain-specific values.

### Planet values

Check:

- accepted planet names;
- capitalization;
- aliases;
- spelling variants;
- Rahu and Ketu;
- unsupported planets;
- empty strings;
- whitespace;
- enum versus string use.

### House values

Check:

- integer requirement;
- valid range 1–12;
- zero;
- negative values;
- values greater than 12;
- numeric strings;
- booleans;
- missing values.

### Sign values

Check:

- accepted names;
- numbers or indices;
- capitalization;
- abbreviations;
- aliases;
- range;
- zero-based versus one-based numbering.

### Functional-role values

Check:

- accepted roles;
- singular and plural variants;
- capitalization;
- aliases;
- unknown roles;
- multiple-role parameters.

### Aspect values

Check:

- aspect type;
- source planet;
- target planet;
- orb or tolerance values;
- directed versus undirected semantics;
- required AspectGraph capability.

### Varga values

Check:

- divisional-chart identifiers;
- supported versus unsupported vargas;
- naming aliases;
- missing varga capability;
- case sensitivity.

### Comparison and threshold values

Check:

- numeric types;
- bounds;
- inclusive versus exclusive comparison;
- NaN and infinity;
- missing thresholds;
- unit assumptions.

Do not change or reinterpret astrology semantics. Flag suspected semantic ambiguities for architectural review.

## 11. Unknown-parameter audit

Determine what happens when callers provide additional keys.

For example:

```json
{
  "planet": "Mars",
  "house": 10,
  "unexpected": "value"
}
```

For every predicate or schema, classify unknown-key behavior as:

- `REJECTED`
- `IGNORED`
- `PRESERVED_BUT_UNUSED`
- `FORWARDED`
- `ERROR`
- `UNKNOWN`

Assess risks including:

- misspelled parameters becoming silent non-matches;
- stale rule syntax remaining undetected;
- hidden behavior differences between predicates;
- unused values entering cache keys;
- unused values entering evidence;
- public callers relying on ignored fields.

## 12. Alias and normalization audit

Find all parameter aliases and normalizers.

Examples may include:

```text
planet / graha
house / bhava
role / functional_role
source / from_planet
target / to_planet
```

For each alias or normalization rule, report:

1. Canonical parameter name.
2. Alias.
3. File and symbol implementing it.
4. Whether it is documented.
5. Whether it is applied by the loader, evaluator or handler.
6. Conflict behavior when canonical and alias keys are both present.
7. Whether normalization is deterministic.
8. Whether normalization happens before cache-key generation.
9. Whether tests cover it.

Do not propose new aliases during this audit.

## 13. Default-value audit

For every default parameter value, determine:

- where it is declared;
- whether it is documented;
- whether the loader and handler agree;
- whether it changes astrology semantics;
- whether it depends on mutable state;
- whether it depends on system time;
- whether it affects cache keys;
- whether omission and explicit default values are treated identically;
- whether different callers apply different defaults.

Classify each default as:

- `CENTRAL_SCHEMA_DEFAULT`
- `HANDLER_DEFAULT`
- `LOADER_DEFAULT`
- `CALLER_DEFAULT`
- `IMPLICIT_PYTHON_DEFAULT`
- `DUPLICATED_DEFAULT`
- `UNKNOWN`

## 14. Invalid-parameter outcome audit

For every invalid-parameter path, determine whether the current outcome is:

- ordinary unmatched;
- missing capability;
- exception;
- swallowed exception;
- empty evidence;
- error dictionary;
- typed error;
- skipped evaluation;
- partial evaluation;
- unknown.

Compare it with the expected Prompt-01 outcome:

```text
status = invalid_parameters
matched = false
typed PredicateError with a stable code
```

Use Prompt-01 as authoritative if its exact semantics differ.

Determine whether raw exception text, stack traces or sensitive input values can enter:

- `PredicateResult.errors`;
- evidence;
- logs;
- snapshots;
- public output.

## 15. Validation versus missing-capability boundary

Distinguish invalid parameters from unavailable AstroState capabilities.

Examples:

```text
Missing "planet" parameter
    → invalid_parameters

Unknown planet name
    → invalid_parameters

Valid planet parameter but planet absent from AstroState
    → typed missing-data result, according to Prompt-01

Valid aspect parameters but AspectGraph absent
    → missing_capability

Valid house parameter but house data unavailable
    → typed missing-data or missing-capability result
```

Audit whether the current code preserves these distinctions.

Report every path where:

- invalid input becomes unmatched;
- missing capability becomes unmatched;
- absent AstroState data becomes invalid input;
- exceptions erase the distinction;
- evidence does not explain the outcome.

Do not invent new status categories. Identify unresolved cases.

## 16. Condition-tree and rule-loader validation

Inspect validation of predicate parameters in:

- YAML rules;
- JSON rules;
- code-created condition trees;
- Yoga condition definitions;
- test fixtures;
- rule loaders;
- rule linters;
- compilers or validators.

Determine:

1. Whether unknown predicate IDs are rejected.
2. Whether predicate parameters are validated at load time.
3. Whether validation is postponed until runtime.
4. Whether invalid rule files can load successfully.
5. Whether parameter errors include rule or condition location.
6. Whether predicate versions affect validation.
7. Whether registry import order affects validation.
8. Whether aliases are normalized before validation.
9. Whether duplicate parameters can occur.
10. Whether loader normalization hides invalid input.
11. Whether validation behavior differs between Yoga and other rules.

Clearly separate:

- Prompt-01 requirements;
- later DSL/compiler responsibilities;
- temporary compatibility needs.

Do not expand the DSL scope.

## 17. Cache interaction

Determine whether parameter validation and normalization happen before or after cache-key construction.

Report whether cache keys can differ for logically equivalent parameters such as:

```json
{"planet": "Mars", "house": 7}
```

and:

```json
{"house": 7, "planet": "Mars"}
```

Also assess:

```json
{"house": 7}
```

versus:

```json
{"house": "7"}
```

and omission versus explicit default values.

Identify whether:

- invalid parameters can be cached;
- unknown parameters affect cache keys;
- aliases normalize before caching;
- mutable parameters can corrupt cache behavior;
- non-JSON-safe parameters break key generation;
- handler-level normalization causes cache fragmentation;
- canonical parameters are preserved in `PredicateResult.inputs`.

Do not redesign the cache. Record only Prompt-01-relevant dependencies.

## 18. Test inventory and gap analysis

Locate tests covering:

### General parameter validation

- missing required parameters;
- unknown parameters;
- invalid types;
- invalid values;
- explicit `None`;
- empty strings;
- additional keys;
- default values;
- aliases;
- conflicting aliases;
- deterministic normalization.

### Planet parameters

- valid planet;
- invalid planet;
- capitalization;
- Rahu and Ketu;
- unsupported name;
- non-string value.

### House parameters

- houses 1 and 12;
- zero;
- negative value;
- value above 12;
- numeric string;
- nonnumeric string;
- boolean;
- float;
- `None`.

### Error-result behavior

- `invalid_parameters` status;
- stable error code;
- predicate ID in the error;
- safe details;
- no raw exception leakage;
- distinction from unmatched;
- distinction from missing capability.

### Integration behavior

- invalid YAML/JSON rule rejection;
- direct runtime invocation;
- Yoga validation;
- condition-tree validation;
- cache behavior after normalization;
- evidence and errors reaching downstream callers.

For every missing test category:

- identify the gap;
- explain its risk;
- recommend the likely test file;
- do not create the test.

## 19. Required classifications

Classify validation coverage as:

- `COMPLETE`
- `PARTIAL`
- `ABSENT`
- `INCONSISTENT`
- `UNKNOWN`

Classify each finding with:

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

## 20. Evidence requirements

Every substantive finding must include:

- repository-relative file path;
- symbol name;
- line number or small range when practical;
- predicate ID;
- relevant parameter;
- observed validation behavior;
- actual failure outcome;
- expected Prompt-01 outcome;
- caller or rule evidence where applicable;
- existing test evidence;
- uncertainty where static analysis cannot prove runtime behavior.

Reconcile findings with Audits 1–6.

Explain:

- newly discovered parameters;
- disagreements with Audit-2’s inventory;
- registry-schema differences from Audit-1;
- caller risks related to Audit-4;
- status and error dependencies related to Audits 5 and 6.

Do not modify earlier reports.

## 21. Scope restrictions

Do not:

- modify production code;
- modify tests;
- modify rule files;
- modify previous audit reports;
- add schemas;
- add validators;
- normalize existing data;
- change aliases;
- change default values;
- change astrology semantics;
- update snapshots;
- run formatters;
- create commits;
- push changes;
- begin Audit-8.

You may run safe, non-mutating searches and tests.

Do not execute commands that update files, snapshots or generated artifacts.

## 22. Deliverable

Create exactly one file:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-07-Parameter-Validation.md`

Do not modify any other file.

If the destination directory does not exist, stop and report the blocker instead of selecting another location.

Use exactly this report structure:

```markdown
# Prompt-01 Audit-07: Parameter Validation

## 1. Executive Summary
## 2. Audit Scope and Method
## 3. Reconciliation with Audits 1–6
## 4. Parameter Sources and Data Flow
## 5. Registry Parameter-Schema Assessment
## 6. Complete Predicate Parameter Inventory
## 7. Required and Missing Parameters
## 8. Type Validation and Coercion
## 9. Domain-Value Validation
## 10. Unknown-Parameter Behavior
## 11. Aliases and Normalization
## 12. Default-Value Behavior
## 13. Invalid-Parameter Outcomes
## 14. Validation versus Missing-Capability Boundary
## 15. Condition-Tree and Rule-Loader Validation
## 16. Cache and Canonical-Input Interaction
## 17. Existing Tests and Coverage Gaps
## 18. Prompt-01 Compliance Matrix
## 19. Migration Risks and Priorities
## 20. Unresolved Architectural Questions
## 21. Audit-7 Conclusion
```

### Complete predicate parameter inventory

Include these columns:

| Predicate ID | File | Handler | Parameter | Required | Expected Type | Allowed Values | Default | Aliases | Normalization | Unknown-Key Policy | Current Invalid Outcome | Required Outcome | Tests | Compliance | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Parameter-flow inventory

Include these columns:

| Source | Loader | Normalizer | Validator | Evaluator | Handler | Validation Stage | Bypass Risk | Evidence |
|---|---|---|---|---|---|---|---|---|

### Invalid-input behavior matrix

Include these columns:

| Predicate | Invalid Input | Current Behavior | Current Status | Error Produced | Evidence Produced | Expected Prompt-01 Behavior | Regression Risk | Priority |
|---|---|---|---|---|---|---|---|---|

### Domain-value validation matrix

Include these columns:

| Value Type | Canonical Form | Accepted Alternatives | Invalid Examples | Validation Location | Normalization | Current Failure | Gap | Priority |
|---|---|---|---|---|---|---|---|---|

### Compliance matrix

Include these columns:

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|

### Summary counts

Include counts for:

- registered predicates audited;
- distinct parameters;
- required parameters;
- optional parameters;
- parameters with defaults;
- parameter aliases;
- predicates with complete validation;
- predicates with partial validation;
- predicates with no validation;
- predicates ignoring unknown parameters;
- invalid inputs currently becoming unmatched;
- invalid inputs currently raising exceptions;
- coercion risks;
- validation and missing-capability boundary violations;
- missing parameter-validation test categories;
- P0, P1, P2 and P3 findings.

## 23. Final response

After creating the report, stop.

Respond with only:

1. Audit-7 status: `COMPLETE` or `BLOCKED`
2. Report file path
3. Files modified
4. Tests or commands executed
5. Registered predicates audited
6. Distinct parameter count
7. Predicates with complete, partial and absent validation
8. Invalid-input-to-unmatched path count
9. Validation/missing-capability boundary-violation count
10. Missing test-category count
11. Number of P0, P1, P2 and P3 findings
12. Any blocker or unresolved architectural question

Do not implement corrections.

Do not proceed to Audit-8.
