You are implementing **WP03 — Canonical Freeze and Logical/Full Serialization** for Prompt-01 in the Parasara system.

## Objective

Implement one strict, reusable predicate-owned canonical value system that provides:

- public `FrozenMapping`;
- recursive defensive freezing;
- explicit supported/unsupported value policy;
- deterministic logical and full projections for the WP02 canonical models;
- strict canonical JSON bytes;
- typed round trips;
- stable SHA-256 logical hashing;
- telemetry exclusion from logical identity.

WP03 must consolidate and replace WP02's private `_ImmutableMapping` and `_freeze_value`; it must not create a second competing freeze implementation.

WP03 does not migrate handlers, evaluator, registry, cache, conditions, Yoga, Career, or callers and does not expose canonical predicate models through public output.

## Prerequisite gate

Before editing:

1. Locate the final WP00-R, WP01, and WP02 completion reports.
2. Confirm WP02 records `VERDICT: COMPLETE` and `WP03_READY: YES`.
3. Confirm the canonical model module exists at `systems/Parasara/engine/rules/models.py` or its recorded equivalent.
4. Re-run the WP02 focused model tests and the complete dual-Python baseline under Python 3.14 and Python 3.11.
5. Confirm rule lint, Yoga order permutations, and strict approved snapshots remain green.
6. Record Git branch/status and preserve unrelated changes.
7. Inspect the actual WP02 private `_ImmutableMapping`, `_freeze_value`, model equality, field definitions, and all tests before designing the replacement.

If any prerequisite is absent, inconsistent, or failing, **STOP without editing**. Do not infer readiness from a summary alone.

## Required references

Locate by exact filename and read:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP00-R report;
- WP01 completion report;
- WP02 completion report;
- `Audit-05-PredicateResult-Model.md`;
- `Audit-06-Supporting-Models.md`;
- `Audit-18-Evidence.md`;
- `Audit-19-Trace.md`;
- `Audit-20-Serialization-Public-Output.md`;
- `Audit-21-Determinism.md`;
- `Audit-22-Test-Inventory-Gap-Analysis.md`.

Record actual paths and stop if duplicate authoritative-looking documents conflict.

## Permitted files and package boundary

WP03 may add or modify only:

- a predicate-owned canonicalization/serialization module, preferably `systems/Parasara/engine/rules/canonical.py`;
- the WP02 canonical model module solely to replace its private immutable helper with the shared WP03 API and to add explicit model serialization entry points if justified;
- focused canonicalization/serialization tests under `tests/rules/`;
- narrow package exports for the canonical API;
- the WP03 completion report.

WP03 must not:

- alter the legacy eight-field runtime `engine.PredicateResult` or its callers;
- migrate registered predicates or change any result/evidence/error/trace behavior;
- change registry definitions, parameter validation, capabilities, AstroState, evaluator, cache, conditions, Yoga, Career, rules, scoring, or public projections;
- serialize arbitrary dataclasses/Pydantic objects by reflection;
- use `dataclasses.asdict`, `json.dumps(default=str)`, `repr`, pickle, or object identity as a canonical boundary;
- update snapshots/goldens, public schemas, dependencies, or CI;
- implement WP04+ behavior;
- weaken WP01/WP02 characterization or model tests.

## Locked canonical value policy

Canonical values support exactly:

- `None`;
- actual `bool`;
- `int` excluding Boolean-as-integer coercion;
- finite `float`, with negative zero normalized to positive `0.0`;
- `str`, preserved exactly without implicit case or Unicode normalization;
- string-valued enums only, serialized using their declared string value;
- mappings whose keys are actual strings and whose values are supported canonical values;
- lists and tuples, both defensively frozen to tuples and serialized as JSON arrays;
- the explicit WP02 canonical models through dedicated serializers, not generic dataclass reflection.

Reject explicitly:

- non-string mapping keys;
- NaN and positive/negative infinity;
- sets and frozensets, because unordered producer values must be normalized at the owning semantic boundary rather than silently assigned canonical order;
- bytes/bytearray/memoryview;
- `Decimal`, complex numbers, dates, datetimes, timedeltas, UUIDs, paths, regex objects, modules, classes, callables, generators, iterators, exceptions, tracebacks, open resources, locks, sockets, and arbitrary custom objects;
- arbitrary dataclasses and Pydantic models;
- cyclic structures;
- enum values that are not strings;
- any value that would require `str()`, `repr()`, or lossy coercion.

Error messages must identify the failing logical path and value category without embedding secrets, entire values, memory addresses, or unstable representations.

WP02 currently freezes sets privately. WP03 intentionally tightens the canonical contract: update focused canonical-model tests so sets/frozensets are rejected with deterministic path-aware errors. This affects only the not-yet-runtime canonical target models and must not change existing public behavior.

## `FrozenMapping` contract

Implement a project-owned immutable generic mapping with:

- defensive construction through the canonical freezer;
- string keys only;
- deterministic lexicographic iteration by exact key value;
- normal mapping lookup, length, iteration, membership, and safe representation;
- no mutation methods;
- equality based on logical key/value content rather than insertion order;
- hashability only when every contained canonical value is hashable under the same canonical policy;
- a hash consistent with equality and independent of caller insertion order;
- no exposure of a mutable backing dictionary;
- no shared caller-owned mutable values;
- stable empty singleton/default behavior only if it does not create mutable aliasing or identity semantics.

Do not make Python's process-randomized `hash()` the persisted or cross-process identity. Persisted identity uses canonical JSON SHA-256.

## Recursive freeze contract

Provide one public function with a clear name such as `freeze_canonical(value, *, path="$" )`.

Requirements:

- recursively produce `FrozenMapping`, tuple, or approved immutable scalar/enum representation;
- defend against later caller mutation at every nesting level;
- detect cycles by active recursion ancestry, not by rejecting harmless repeated references;
- allow the same acyclic object to appear in multiple branches and freeze each occurrence deterministically;
- preserve list/tuple semantic order;
- normalize mapping order through `FrozenMapping`;
- normalize `-0.0` to `0.0`;
- reject unsupported values with stable path-aware exceptions;
- produce equivalent frozen values for logically equivalent inputs regardless of mapping insertion order;
- avoid global caches and memory-identity-dependent output.

Replace WP02's private helper rather than wrapping or retaining two independent policies. Remove dead private code after all WP02 tests are migrated.

## Model projection contract

Provide dedicated strict projections for:

- `PredicateError`;
- `PredicateTraceStep`;
- `PredicateResult`.

Use stable lowercase status/enum values, JSON objects for mappings, and JSON arrays for tuples.

### PredicateError projection

Include exactly:

- `code`;
- `message`;
- `predicate_id`;
- `details`;
- `recoverable`.

### PredicateTraceStep projection

Include exactly the WP02 fields:

- `step_id`;
- `operation`;
- `details`;
- `observation`;
- `parent_step_id`;
- `error_code`.

Retain explicit `null` for optional trace fields; do not omit them opportunistically.

### PredicateResult logical projection

Include exactly these eight logical fields:

- `matched`;
- `predicate_id`;
- `predicate_version`;
- `inputs`;
- `evidence`;
- `trace_steps`;
- `errors`;
- `status`.

Exclude:

- `cache_hit`;
- `evaluation_time_ms`.

### PredicateResult full diagnostic projection

Include all ten fields in the locked contract, including:

- `cache_hit`;
- `evaluation_time_ms`.

The full projection is diagnostic and is not logical identity.

Do not add timestamps, schema wrappers, class names, Python module names, or hidden metadata. If a format-version envelope is considered necessary, stop and document the proposal rather than inventing it in WP03.

## Canonical JSON contract

Provide explicit functions for logical and full JSON data/text/bytes. Use one strict JSON encoder configuration:

- UTF-8;
- `ensure_ascii=False`;
- `allow_nan=False`;
- lexicographically sorted object keys at every level;
- compact separators `(',', ':')`;
- no indentation or trailing whitespace;
- no `default` fallback;
- stable lowercase JSON literals;
- a final byte representation with no BOM and no implicit platform newline.

The canonical bytes for equal logical results must be identical across:

- repeated calls;
- mapping insertion orders;
- cold/warm telemetry differences;
- Python 3.14 and Python 3.11;
- fresh processes.

Full bytes may differ when telemetry differs, but must otherwise be deterministic.

## Round-trip contract

Implement strict dedicated deserializers for the three WP02 model types.

Requirements:

- logical result round-trip reconstructs a logically equal `PredicateResult` with telemetry defaults (`cache_hit=False`, `evaluation_time_ms=None`);
- full result round-trip preserves telemetry exactly;
- error and trace round trips preserve all fields;
- reject missing required keys;
- reject unknown keys;
- reject wrong JSON container/value types;
- reject duplicate JSON object keys during parsing rather than silently taking the last value;
- reapply all WP02 invariants and canonical value validation;
- reject noncanonical enum/status values;
- accept JSON text/bytes only through explicit strict entry points;
- do not instantiate arbitrary types from input tags.

Round-trip equality means typed logical equality, not preservation of original list-versus-tuple or mapping insertion order, which canonicalization intentionally normalizes.

## Stable logical hashing

Provide a named function such as `predicate_result_logical_sha256(result) -> str` that:

- hashes the exact canonical logical UTF-8 bytes;
- returns a lowercase 64-character hexadecimal SHA-256 digest;
- excludes telemetry;
- is stable across processes and both Python lanes;
- changes when any logical field changes.

Do not make canonical models Python-hashable merely because this digest exists. Retain deliberate model unhashability unless a separately documented need proves otherwise.

## Tests-first requirements

Write focused failing tests before implementation. Cover at minimum:

### FrozenMapping and freeze

- empty and nested construction;
- deterministic iteration and representation;
- insertion-order-independent equality/hash;
- mapping/list/tuple recursion;
- caller mutation isolation;
- repeated noncyclic aliases accepted;
- direct and indirect cycles rejected;
- string-enum normalization;
- negative-zero normalization;
- finite float handling;
- every unsupported category listed above;
- non-string keys at root and nested paths;
- deterministic safe path-aware errors;
- sets/frozensets explicitly rejected;
- no mutable backing escape.

### Model projections

- exact key sets for error, trace, logical result, and full result;
- exact enum values;
- tuples become arrays and mappings become objects;
- optional trace values remain explicit `null`;
- empty collections remain explicit empty objects/arrays;
- logical projection excludes exactly the two telemetry fields;
- full projection contains exactly all ten fields;
- no public/Yoga/Career projection changes.

### JSON determinism

- exact expected byte literals for representative nested models;
- repeated-call byte equality;
- different mapping insertion orders produce identical bytes;
- telemetry changes leave logical bytes unchanged;
- telemetry changes affect full bytes as expected;
- Unicode is preserved under the approved UTF-8 policy;
- NaN/infinity and unsupported values fail;
- no permissive string fallback;
- cross-process comparison;
- Python 3.14/3.11 byte/hash comparison.

### Round trips

- error, root/child trace, logical result, and full result;
- every status;
- matched/unmatched/error examples;
- empty and deeply nested values;
- missing/unknown/duplicate keys;
- wrong types and invalid invariants;
- malformed UTF-8/JSON;
- logical telemetry defaults and full telemetry preservation.

### Hashing

- exact SHA-256 format;
- stability across calls/processes/Python lanes;
- telemetry independence;
- sensitivity to every logical field;
- no dependence on Python `hash()` or object identity.

Retain and adapt all 115 WP02 model tests. Add targeted regression tests proving WP02 caller-mutation guarantees remain true after replacing the private helper.

## Validation matrix

Run in Python 3.14 first and Python 3.11 second:

1. WP02 model tests;
2. new WP03 canonicalization/serialization tests;
3. WP01 characterization group;
4. targeted predicate/Yoga/Career/functional-role/rule-runtime/linter/writer/snapshot compatibility set;
5. all WP00-R Yoga node-ID orders and loader trigger orders;
6. full collection with exact node-ID comparison;
7. complete suite twice in fresh processes;
8. cross-process canonical byte/hash probe in each lane;
9. direct cross-lane comparison of recorded canonical byte fixtures and hashes;
10. repository rule lint proving five supported rule files, including `yogas.yaml`, inspected once;
11. strict approved snapshot comparison twice per lane;
12. repository status, artifact scan, and `git diff --check`.

Use the exact safe environment variables, explicit interpreter paths, and ignored unique `--basetemp` policy from WP00-R/WP02. Never update a snapshot or hide a failure.

## Completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP03/WP03.md`

Include:

1. verdict: `COMPLETE`, `BLOCKED`, or `INCOMPLETE`;
2. prerequisite evidence and actual reference paths;
3. before/after freeze-helper inventory proving consolidation;
4. supported/rejected canonical type table;
5. `FrozenMapping` and cycle policy;
6. exact logical/full projection schemas;
7. exact JSON encoder policy;
8. round-trip validation policy;
9. logical hash policy;
10. files changed;
11. test-to-requirement traceability;
12. exact dual-lane commands/counts;
13. cross-process/cross-version byte and hash evidence;
14. WP01/WP02 compatibility, Yoga, lint, snapshot, and artifact evidence;
15. unresolved issues assigned to later packages;
16. explicit `WP04_READY: YES` or `WP04_READY: NO`.

## Definition of done

WP03 is complete only when:

- WP02 is complete and reproducible;
- one shared public `FrozenMapping`/freeze policy replaces WP02's private implementation;
- supported and unsupported values follow the locked policy without coercive fallback;
- cycles and non-string keys fail deterministically with safe logical paths;
- logical and full projections have exact tested schemas;
- canonical logical bytes exclude telemetry and are stable across processes and both Python versions;
- strict typed logical/full round trips pass;
- SHA-256 logical hashing is stable and telemetry-independent;
- all WP02 immutability/equality guarantees remain green;
- no runtime handler/caller migration or public-output change occurs;
- the complete dual-lane suite, Yoga orders, rule lint, and unchanged approved snapshots pass;
- no fixed/tracked artifact is written;
- the report records `WP04_READY: YES`.

At the end, provide a concise summary with the verdict, API/module location, supported-value policy, test counts for both lanes, cross-version byte/hash evidence, compatibility/snapshot status, files changed, and WP04 readiness. Do not proceed to WP04.