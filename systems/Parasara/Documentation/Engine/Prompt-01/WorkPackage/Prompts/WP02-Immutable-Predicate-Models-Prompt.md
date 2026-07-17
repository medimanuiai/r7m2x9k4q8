You are implementing **WP02 — Immutable Status, Error, Trace, and PredicateResult Models** for Prompt-01 in the Parasara system.

## Objective

Introduce and thoroughly test the canonical immutable predicate-domain models:

- `PredicateStatus`;
- `PredicateError`;
- `PredicateTraceStep`;
- `PredicateResult`.

WP02 establishes model construction, invariants, defensive immutability, logical equality, and telemetry separation. It must not migrate predicate handlers, evaluator behavior, cache behavior, condition evaluation, Yoga, Career, public serialization, or callers.

Canonical logical/full JSON serialization and the reusable public freeze/canonicalization subsystem belong to WP03.

## Prerequisite gate

Before editing:

1. Locate and read the final WP00-R report and confirm `VERDICT: COMPLETE` and `WP01_READY: YES`.
2. Locate and read the WP01 completion report. Confirm WP01 is `COMPLETE`, all characterization tests pass in Python 3.14 and Python 3.11, approved snapshots are unchanged, and no unresolved blocker affects model design.
3. Run the final WP00-R/WP01 baseline commands in both Python lanes and confirm the recorded green baseline.
4. Record the Git branch and working-tree state and preserve unrelated changes.
5. Locate all current `PredicateResult` definitions, imports, constructors, `dataclasses.replace` calls, serializers, type checks, cache uses, and tests.

If WP01 is absent, incomplete, blocked, or its baseline is not reproducible, **STOP without editing** and report the exact blocker. Do not infer completion from WP00-R alone.

## Required references

Locate by exact filename and read:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- the final WP00-R completion report;
- the WP01 completion report;
- `Audit-05-PredicateResult-Model.md`;
- `Audit-06-Supporting-Models.md`;
- `Audit-17-Error-Handling.md`;
- `Audit-18-Evidence.md`;
- `Audit-19-Trace.md`;
- `Audit-20-Serialization-Public-Output.md`;
- `Audit-21-Determinism.md`;
- `Audit-22-Test-Inventory-Gap-Analysis.md`.

Record the actual paths used. Stop if duplicate authoritative-looking documents disagree.

## Package boundary

WP02 may add:

- one predicate-owned model module, preferably `systems/Parasara/engine/rules/models.py` or the repository-equivalent location;
- focused model tests, preferably `tests/rules/test_predicate_models.py`, `test_predicate_errors.py`, and `test_predicate_traces.py` or a smaller coherent equivalent;
- the WP02 completion report;
- the narrowest import/export needed to make the new model API importable without migrating runtime producers.

WP02 must not:

- migrate or rewrite any predicate handler;
- alter registered predicate outcomes, evidence, errors, or traces;
- change the evaluator, condition evaluator, registry behavior, parameter validation, capability handling, cache keys/policy, AstroState, Yoga, Career, rules, scoring, public output, or snapshots;
- expose new internal fields through an API or public JSON;
- implement WP03 canonical JSON, general serialization, round-trip schema, or reusable canonical hashing;
- introduce timeout execution, strict-mode exception conversion, or error-code behavior into the evaluator;
- modify dependencies or CI;
- weaken or update characterization tests or approved goldens.

## Runtime integration rule

Do not create an accidental flag day.

Inspect the current active `PredicateResult` constructor/caller inventory. Choose the least invasive approach that makes the canonical WP02 models importable and testable while leaving existing runtime behavior unchanged.

Preferred approach for WP02:

- define the canonical models in the new predicate-owned model module;
- leave legacy runtime construction behind an explicitly named temporary compatibility boundary until the appropriate handler/evaluator migration packages;
- do not silently relax canonical constructor invariants to accommodate legacy callers;
- document every temporary legacy definition/alias and its planned removal package.

If making the new canonical class active would require changing handlers or observable behavior, do not do so in WP02. Do not maintain two objects both described as canonical. The existing runtime object must be explicitly labeled legacy/compatibility in code or documentation, and the new model module is the sole target contract.

## Locked model decisions

### 1. `PredicateStatus`

Implement a string-valued enum with exactly these values:

- `matched`;
- `unmatched`;
- `missing_capability`;
- `invalid_parameters`;
- `error`;
- `timeout`;
- `skipped`.

Requirements:

- values are stable lowercase strings;
- no `evaluated`, `unknown`, `success`, or alias status;
- construction from each exact value is deterministic;
- invalid values fail explicitly;
- enum string values are suitable for later canonical JSON without using `default=str`.

### 2. `PredicateError`

Implement an immutable typed value with exactly these fields:

- `code: str`;
- `message: str`;
- `predicate_id: str`;
- `details: immutable mapping`;
- `recoverable: bool`.

Requirements:

- `code`, `message`, and `predicate_id` are non-empty strings after validation; do not silently coerce arbitrary objects;
- `recoverable` must be an actual Boolean;
- `details` is defensively copied/frozen so caller mutation cannot affect the model;
- details must not contain raw exception objects, traceback objects, callables, open resources, or mutable aliases;
- messages/details are safe model data and must not contain stack traces introduced by constructors;
- WP02 does not define the complete production error-code catalog or evaluator conversion policy;
- do not use raw exception text in model tests;
- ordered equality is deterministic.

Do not invent public error exposure. These models remain internal.

### 3. `PredicateTraceStep`

Implement an immutable typed value with these logical fields:

- `step_id` — non-empty stable path-derived identifier;
- `operation` — non-empty typed/stable operation name;
- `details` — immutable inputs/details mapping;
- `observation` — immutable factual result/observation value or mapping;
- `parent_step_id` — optional non-empty stable parent reference;
- `error_code` — optional non-empty safe error-code reference.

Use the exact field names already locked by the final plan/audits if they differ; document any reconciliation. Do not add timing, cache-hit, random UUID, wall-clock, process ID, memory identity, or run-specific telemetry to logical trace identity.

Requirements:

- reject empty identifiers and invalid optional strings;
- defensively freeze nested caller data sufficiently to prevent mutation of a constructed model;
- preserve semantic step order when steps are stored in `PredicateResult`;
- do not generate step IDs inside the model from randomness or time;
- do not introduce a speculative complete trace-operation enum if the approved documents do not define one. A validated stable string or narrowly justified extensible string type is preferable to inventing future operations.

### 4. `PredicateResult`

Implement an immutable typed value with exactly these ten fields, in this logical contract:

1. `matched`;
2. `predicate_id`;
3. `predicate_version`;
4. `inputs`;
5. `evidence`;
6. `trace_steps`;
7. `errors`;
8. `cache_hit`;
9. `evaluation_time_ms`;
10. `status`.

Required types/shape:

- `matched`: actual Boolean;
- `predicate_id`: non-empty string;
- `predicate_version`: non-empty string representing the producing predicate version; do not enforce full SemVer here unless the locked decision explicitly requires it at model level;
- `inputs`: immutable mapping;
- `evidence`: immutable mapping;
- `trace_steps`: tuple of `PredicateTraceStep`;
- `errors`: tuple of `PredicateError`;
- `cache_hit`: actual Boolean, default `False`;
- `evaluation_time_ms`: `None` or finite nonnegative numeric telemetry; reject Boolean, negative, NaN, and infinity;
- `status`: `PredicateStatus`.

Normalize omitted collections to independent empty immutable values. Reject `None` for required collections rather than treating it ambiguously unless the approved contract explicitly says otherwise.

## Required invariants

Enforce at construction:

- `status == PredicateStatus.MATCHED` requires `matched is True`;
- `matched is True` requires `status == PredicateStatus.MATCHED`;
- every other status requires `matched is False`;
- `status == PredicateStatus.ERROR` requires at least one `PredicateError`;
- `status` values representing ordinary factual outcomes (`matched`, `unmatched`) must not carry contradictory construction state;
- `trace_steps` contains only `PredicateTraceStep` objects;
- `errors` contains only `PredicateError` objects;
- no mutable caller-owned object remains reachable through the constructed model.

Do not add speculative invariants such as requiring an error for every missing capability or invalid parameter unless the locked documents explicitly require them now. Record such policy for later evaluator packages.

## Immutability boundary with WP03

WP02 must prove that constructed model state cannot be changed through:

- field reassignment;
- top-level mapping mutation;
- nested mapping/list/set mutation through original caller references;
- mutation of original error, evidence, input, trace-detail, or observation inputs;
- shared default collections across instances.

Implement only the minimum private/internal defensive-freeze support needed for model immutability. WP03 owns:

- the reusable project-level `FrozenMapping`/canonical-freeze API;
- complete supported-value policy;
- canonical key ordering;
- logical and full serialization;
- JSON byte stability;
- round trips;
- unsupported-value/cycle policy across all canonical serializers.

Do not expose a premature general serialization API in WP02. Clearly mark any private freeze helper for consolidation/replacement in WP03.

## Equality and telemetry

Define model equality so logical content is compared deterministically. For `PredicateResult`, `cache_hit` and `evaluation_time_ms` are telemetry and must not affect logical equality or logical hashing.

Requirements:

- two otherwise identical cold/warm results compare logically equal;
- two otherwise identical results with different evaluation durations compare logically equal;
- differences in predicate identity/version, status, matched value, inputs, evidence, trace steps, or errors are logically unequal;
- do not rely on Python's randomized object identity;
- if Python `__hash__` is implemented, it must follow equality and exclude telemetry; otherwise deliberately make the object unhashable and document that canonical logical hashing belongs to WP03.

Do not add a full diagnostic equality/serializer unless explicitly named as a small internal test helper. WP03 owns the public distinction between logical and full projections.

## Tests-first requirements

Write focused failing tests before implementing models. Cover at minimum:

### Status tests

- all seven exact values;
- invalid value rejection;
- stable string values;
- no aliases/additional statuses.

### Result construction/invariant tests

- valid instance for every status;
- matched/status truth table;
- error status with and without errors;
- exact field inventory and defaults;
- strict Boolean checks;
- predicate ID/version validation;
- telemetry validation including `None`, zero, finite positive, negative, Boolean, NaN, and infinities;
- invalid trace/error element types;
- independent empty defaults.

### Error tests

- valid construction;
- empty/invalid string rejection;
- strict recoverable Boolean;
- immutable details;
- caller-mutation isolation;
- no raw exception/traceback objects accepted.

### Trace tests

- valid root and child construction;
- invalid/empty IDs and optional references;
- immutable details and observation;
- caller-mutation isolation;
- deterministic tuple ordering;
- absence of telemetry/random identity fields.

### Immutability tests

- frozen field assignment failure for every model;
- mutation attempts at every nested supported level;
- mutation of original input objects after construction;
- no shared mutable defaults;
- equality unaffected by caller mutation.

### Equality tests

- telemetry-independent logical equality;
- logical inequality for every non-telemetry field;
- equality symmetry/transitivity;
- hash consistency if hashability is implemented.

Avoid shallow type/presence-only assertions. Do not use `json.dumps(default=str)`.

## Compatibility validation

After model tests pass, prove that WP02 has not altered existing behavior:

1. run the WP01 characterization suite in Python 3.14 and 3.11;
2. run predicate, Yoga, Career, functional-role, rule-runtime, linter, writer-safety, and snapshot tests in both lanes;
3. run the full suite twice in fresh processes per lane;
4. run Yoga node-ID order permutations from WP00-R;
5. run rule lint and prove all supported rule files, including `yogas.yaml`, are inspected exactly once;
6. run strict approved snapshot comparison twice per lane without updating it;
7. verify the generated hash remains the approved WP00-R hash;
8. inspect Git status and artifact paths.

Use the exact safe commands and explicit `--basetemp` policy recorded by WP00-R/WP01. Do not exclude failures or modify approved output.

## Completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP02/WP02.md`

Include:

1. verdict: `COMPLETE`, `BLOCKED`, or `INCOMPLETE`;
2. prerequisite evidence and actual reference paths;
3. current legacy/canonical model inventory before and after;
4. final model field/type/invariant table;
5. immutability and equality decisions;
6. explicit WP02/WP03 boundary;
7. temporary compatibility boundary and planned removal package;
8. files changed;
9. model test symbols and requirement traceability;
10. exact commands and counts for Python 3.14 and 3.11;
11. Yoga order, linter, snapshot, hash, and artifact evidence;
12. unresolved issues, without silently expanding scope;
13. explicit `WP03_READY: YES` or `WP03_READY: NO`.

## Definition of done

WP02 is complete only when:

- WP01 is complete and its characterization baseline is reproducible;
- all four canonical models exist in the predicate-owned target module;
- `PredicateResult` has exactly the ten locked fields;
- all seven statuses and truth invariants are enforced;
- error and trace collections are typed immutable tuples;
- all model state is defensively immutable from caller mutation;
- telemetry does not affect logical equality/hash;
- focused model tests pass in both Python lanes;
- no handler/caller migration or observable output change occurred;
- the full dual-lane baseline, Yoga permutations, rule lint, and strict snapshots remain green;
- no approved snapshot, rule behavior, public schema, or fixed artifact changed;
- the completion report contains reproducible evidence and `WP03_READY: YES`.

At the end, provide a concise summary with the verdict, model location, tests/counts for both lanes, compatibility status, files changed, temporary legacy boundary, and WP03 readiness. Do not proceed to WP03.