You are implementing **WP05 — Executable Parameter Schemas and Canonical Normalization** for Prompt-01 in the Parasara system.

## Objective

Replace WP04's descriptive parameter metadata with strict executable schemas and one shared validation/normalization API for all five canonical predicate definitions and six exposed IDs.

WP05 establishes:

- exact accepted parameter names;
- required/optional/default policy;
- strict types and value ranges;
- canonical planet normalization;
- closed functional-role vocabulary;
- unknown-key and alias policy;
- deterministic immutable normalized inputs;
- stable safe invalid-parameter diagnostics.

WP05 must not migrate handlers or the evaluator to canonical `PredicateResult`. The schemas become authoritative and testable now; WP08/WP11 apply them to canonical predicate execution, WP09 applies them before cache identity, and WP12 applies them to active rule/condition loading.

## Prerequisite gate

Before editing:

1. Locate the final WP00-R and WP01–WP04 reports.
2. Confirm WP04 records `VERDICT: COMPLETE` and `WP05_READY: YES`.
3. Confirm the authoritative registry contains five canonical definitions and six exposed IDs with `ASPECT` aliasing `ASPECT_EXISTS`.
4. Run WP02 model, WP03 canonical, WP04 registry, and WP01 characterization tests in Python 3.14 and Python 3.11.
5. Run the complete suite, Yoga order/loader-trigger matrix, rule lint, registry fingerprint, and strict snapshot comparison in both lanes.
6. Record Git branch/status and preserve unrelated changes.
7. Inventory actual handler parameter reads, active Yoga parameters, direct evaluator callers, test fixtures, registry metadata, and every observed role value in versioned repository tables/rules.

If any prerequisite is absent, inconsistent, or failing, **STOP without editing**.

## Required references

Locate by exact filename and read:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP00-R and WP01–WP04 completion reports;
- `Audit-01-Predicate-Registry.md`;
- `Audit-02-Complete-Predicate-Inventory.md`;
- `Audit-04-Complete-Caller-Inventory.md`;
- `Audit-07-Parameter-Validation.md`;
- `Audit-08-Capability-Handling.md`;
- `Audit-11-Predicate-Cache.md`;
- `Audit-13-Condition-Format-Inventory.md`;
- `Audit-14-Rule-Loader-Compiler-Interaction.md`;
- `Audit-21-Determinism.md`;
- `Audit-22-Test-Inventory-Gap-Analysis.md`.

Record actual paths and stop if authoritative-looking duplicates conflict.

## Package boundary

WP05 may add or modify only:

- predicate parameter-schema/validation modules;
- the `PredicateDefinition.parameter_schema` representation and five built-in definition declarations;
- registry validation/fingerprinting necessary to validate and expose executable schemas;
- focused parameter-schema/normalization tests;
- narrowly adapted registry tests/fingerprints;
- package exports;
- the WP05 completion report.

WP05 must not:

- change handler bodies, results, evidence, trace, errors, or factual outcomes;
- call the new validator automatically from the legacy evaluator or cache;
- migrate any handler/caller to canonical `PredicateResult`;
- add capability readiness checks or classify missing chart data;
- modify AstroState, cache identity/policy, condition evaluation, Yoga execution, Career, rule execution, or public output;
- recursively validate rule/condition YAML yet;
- activate `HOUSE_LORDS_COMBINATION` or dormant helpers;
- change astrology rules/tables/weights/scoring;
- update snapshots/goldens, public schemas, dependencies, or CI;
- begin WP06.

## Authoritative production schema inventory

Provide executable schemas for these five canonical definitions:

### `ASPECT_EXISTS` and alias `ASPECT`

Accepted keys, all optional:

- `from_house` — house;
- `to_house` — house;
- `from_planet` — planet;
- `to_planet` — planet.

Rules:

- zero filters is valid and retains the characterized compatibility meaning “any available aspect edge”;
- omission means no filter and remains omitted from normalized inputs;
- explicit `None` is invalid, not equivalent to omission;
- at least one filter is not required;
- alias `ASPECT` uses the exact same schema object/version/normalization as canonical `ASPECT_EXISTS`;
- no misspelled or extra filters are accepted.

### `PLANET_IN_HOUSE`

Required keys:

- `planet` — planet;
- `house` — house.

No optional keys and no defaults.

### `HOUSE_OCCUPANT`

Required keys:

- `house` — house;
- `planet` — planet.

No optional keys and no defaults. Preserve this as separate vocabulary from `PLANET_IN_HOUSE`.

### `FUNCTIONAL_ROLE`

Required key:

- `role_in` — nonempty role collection.

Rules:

- omission, `None`, empty collection, string, mapping, set/frozenset, generator, and arbitrary iterable are invalid;
- accept only list or tuple input;
- every item must be an exact valid role string;
- duplicate roles are invalid rather than silently deduplicated;
- normalized roles are sorted lexicographically into an immutable tuple because membership semantics are order-independent;
- no implicit empty default remains in the executable schema;
- `context.planets` is evaluation context, not a predicate parameter, and must not appear in this schema.

Build the closed role vocabulary by scanning the active/versioned functional-role tables, compatibility tables, producer code, and active Yoga rule values. Include only exact values demonstrably present in those authoritative repository sources.

At minimum reconcile these observed categories:

- `functional_benefic`;
- `functional_malefic`;
- `functional_neutral`;
- `yogakaraka`;
- active Yoga literals `benefic` and `malefic` if they remain present.

Treat `benefic`/`malefic` as distinct literal vocabulary when retained; do **not** normalize them to `functional_benefic`/`functional_malefic`, because that could change Yoga firing. Record every admitted value and its source path in the WP05 report. If additional table values exist, include them only with exact source evidence. Do not invent astrology aliases.

### `PLANET_EXALTED`

Required key:

- `planet` — planet.

No optional keys and no defaults. Parameter validation must not resolve the deferred exaltation-semantic question.

## Canonical planet policy

Use exactly this Stage-01 canonical planet catalog:

- `Sun`;
- `Moon`;
- `Mars`;
- `Mercury`;
- `Jupiter`;
- `Venus`;
- `Saturn`;
- `Rahu`;
- `Ketu`.

Normalization:

- input must be an actual string;
- trim leading/trailing whitespace;
- match catalog values case-insensitively using ASCII spelling;
- output the exact canonical catalog spelling;
- reject empty/whitespace-only values;
- reject unknown names, numeric values, Boolean values, abbreviations, transliterations, `Ascendant`, `Lagna`, outer planets, and arbitrary aliases;
- no fuzzy matching or Unicode transliteration;
- a canonical valid planet absent from a particular AstroState is not a parameter error; WP06 owns missing capability/entity semantics.

There are no production planet aliases in WP05 beyond case/outer-whitespace normalization. Case variants are normalization, not registered aliases.

## House policy

House input must be:

- an actual `int`;
- not a Boolean;
- in the inclusive range 1–12.

Reject:

- zero, negatives, and values above 12;
- Boolean values;
- floats, including integral floats such as `7.0`;
- numeric strings such as `"7"`;
- `Decimal`, enums, custom numeric types, `None`, and arbitrary objects.

Do not coerce or clamp.

## Parameter-key, container, and alias policy

The top-level parameter input must be a mapping. Reject `None`, list, tuple, string, number, generator, Pydantic object, dataclass, and arbitrary custom object as the parameter container.

Keys:

- must be actual strings;
- must exactly match the lowercase schema key;
- are not trimmed or case-normalized;
- unknown keys are invalid;
- duplicate keys at Python-mapping level are not representable; duplicate YAML/JSON-key diagnostics remain loader/compiler work;
- input mappings are never mutated.

Production parameter aliases:

- none are declared in WP05;
- do not infer aliases from similar names or legacy rule vocabulary;
- the schema framework may support explicitly registered aliases for isolated tests/future use;
- if a canonical key and its registered alias are both supplied in a synthetic schema, return deterministic `conflicting_alias` rather than choosing one;
- alias normalization must occur before unknown-key reporting and canonical freezing.

## Schema model

Replace WP04's descriptive `FrozenMapping` schema with a typed immutable executable schema model. Use the WP03 canonical types and avoid arbitrary callables embedded in metadata fingerprints.

Prefer a small predicate-owned design such as:

- `ParameterKind` string enum;
- immutable `ParameterSpec`;
- immutable `ParameterSchema`;
- immutable `ParameterValidationIssue` or an equivalent safe structure;
- immutable `ParameterValidationOutcome` or an equivalent nonexceptional expected-failure result.

Exact names may follow repository conventions, but the contract must be explicit and tested.

Each schema must expose deterministic metadata suitable for the registry fingerprint without serializing functions, object IDs, or `repr`.

Required schema behavior:

- exact ordered specifications;
- required/optional distinction;
- explicit defaults/omission policy;
- aliases tuple;
- kind/value constraints;
- schema version or deterministic link to predicate version;
- canonical normalized output as WP03 `FrozenMapping`;
- no mutation/backing escape;
- deterministic equality/fingerprint across construction/import order/process/Python version.

Do not build a general JSON Schema engine, Pydantic model factory, DSL compiler, or plugin schema system.

## Validation API and safe failures

Provide one shared API that validates by canonical predicate definition/ID and returns an expected, typed outcome rather than raising for ordinary invalid caller input.

The outcome must distinguish:

- success with canonical immutable inputs and no issues;
- invalid input with no canonical inputs and one or more ordered safe issues.

Issue ordering:

1. schema-declared parameters in schema order;
2. alias conflicts associated with their canonical parameter;
3. unknown keys in lexicographic order;
4. container-level issue first when the top-level value is not a mapping.

Use stable reason codes such as:

- `invalid_container`;
- `missing_required`;
- `unknown_parameter`;
- `invalid_type`;
- `invalid_value`;
- `conflicting_alias`;
- `duplicate_value`.

Safe issue data may include only:

- canonical predicate ID;
- canonical parameter name when known;
- stable reason code;
- expected kind/range/catalog identifier;
- safe logical path.

Do not include the supplied raw value, raw exception text, object type `repr`, memory address, full parameter mapping, secrets, or source file content.

Provide a narrow adapter that can create the WP02 canonical `PredicateError` with:

- `code="invalid_parameters"`;
- safe fixed message;
- canonical predicate ID;
- immutable safe issue details;
- `recoverable=True`.

Do not create a `PredicateResult` or invoke handlers in WP05.

## Canonical normalized inputs

Successful output must be WP03 `FrozenMapping` and follow:

- keys in deterministic canonical mapping order;
- required parameters present;
- optional omitted parameters remain omitted unless the schema declares a meaningful explicit default;
- no `None` placeholders for omitted Aspect filters;
- planets use exact canonical catalog spelling;
- houses remain strict integers;
- `role_in` becomes a lexicographically sorted tuple;
- input order, mapping implementation, and mutable caller references do not affect output;
- caller mutation after validation cannot alter normalized inputs;
- logically equivalent case/outer-whitespace planet inputs normalize identically;
- no other material coercion occurs.

WP05 must prove canonical normalization before later cache identity, but it must not change the legacy cache yet.

## Registry integration

Every canonical `PredicateDefinition.parameter_schema` must contain the typed executable schema. Registry construction/finalization must reject:

- missing/wrong schema type;
- schema whose predicate identity disagrees with the definition;
- duplicate spec names or aliases;
- invalid spec ordering/defaults;
- unsupported kind/constraint combinations;
- alias/canonical collisions;
- schema metadata that cannot be fingerprinted canonically.

`ASPECT` resolves the exact `ASPECT_EXISTS` definition/schema object. Registry enumeration and handler identity remain unchanged.

Update the registry fingerprint to include deterministic executable schema metadata. The fingerprint must remain identical across fresh processes, import orders, and both Python lanes. A schema change must change the fingerprint.

Do not make validation affect production lookup/evaluation in WP05.

## Tests-first requirements

Write failing tests before implementation. Cover at minimum:

### General schema behavior

- exact five schemas/six exposed IDs;
- required, optional, omitted, and explicit `None` cases;
- invalid top-level containers, including falsey non-mappings;
- unknown and non-string keys;
- wrong case/whitespace parameter keys;
- multiple deterministic issues and ordering;
- caller mutation isolation;
- mapping insertion-order independence;
- exact normalized `FrozenMapping` output;
- schema immutability and deterministic metadata;
- safe issue/error details without raw values.

### House cases

- houses 1 and 12 accepted;
- representative middle house accepted;
- zero, negative, 13+, Boolean, float, numeric string, nonnumeric string, `None`, Decimal/custom numeric rejected;
- no coercion.

### Planet cases

- all nine canonical values;
- lowercase/uppercase/mixed-case and outer-whitespace normalization;
- Rahu/Ketu;
- empty, whitespace, unknown, unsupported, abbreviation, number, Boolean, `None`, custom object rejected;
- valid catalog planet remains valid regardless of AstroState membership.

### Aspect cases

- empty mapping valid;
- each filter independently;
- all filters together;
- alias and canonical ID produce identical normalized inputs/schema identity;
- omission versus explicit `None`;
- unknown/misspelled filter rejection;
- invalid planet/house cases;
- input does not invoke handler or require aspect capability.

### Functional-role cases

- every source-backed allowed value;
- valid list and tuple normalization;
- deterministic sorted role tuple;
- missing, `None`, empty, duplicate, unknown, wrong-case/whitespace value;
- string, mapping, set/frozenset, generator, arbitrary iterable, and noniterable rejection;
- prove `benefic`/`malefic` are not rewritten to functional-role strings;
- prove validation does not compute functional roles or read chart state.

### Required predicate cases

- missing each required key independently and together;
- valid canonical inputs for `PLANET_IN_HOUSE`, `HOUSE_OCCUPANT`, and `PLANET_EXALTED`;
- their unknown keys and wrong values;
- `PLANET_IN_HOUSE`/`HOUSE_OCCUPANT` remain separate schemas even if specs overlap.

### Synthetic alias/schema validation

- registered alias success;
- canonical-plus-alias conflict;
- alias/alias and alias/canonical collisions;
- production has zero parameter aliases;
- invalid schemas rejected atomically by registry;
- fingerprint sensitivity/stability.

### Safe invalid-parameter adapter

- exact code/message/predicate ID/recoverability;
- immutable ordered issue details;
- no raw supplied values, exception strings, tracebacks, memory addresses, or arbitrary representations;
- no `PredicateResult` construction or handler invocation.

Do not add missing-capability tests here except to prove valid parameters are not rejected because chart data is absent. WP06 owns that distinction.

## Compatibility validation

Run in Python 3.14 first and Python 3.11 second:

1. WP02 model tests;
2. WP03 canonical tests;
3. WP04 registry tests;
4. new WP05 parameter tests;
5. WP01 characterization tests;
6. explicit valid-parameter validation for all six exposed IDs;
7. targeted predicate/Yoga/Career/functional-role/rule-runtime/linter/writer/snapshot set;
8. all WP00-R Yoga orders and both loader-trigger orders;
9. fresh-process registry/schema fingerprint tests under registry-first, predicate-first, and Yoga-first import orders;
10. full collection with identical node-ID comparison;
11. complete suite twice in fresh processes;
12. cross-process/cross-version normalized-input and safe-error byte/hash probe;
13. repository rule lint proving five rule files inspected once;
14. strict approved snapshot comparison twice per lane;
15. artifact scan, scoped Git status, and `git diff --check`.

Because the legacy evaluator does not enforce WP05 yet, all WP01 characterized runtime behavior must remain unchanged, including documented invalid/empty compatibility observations. Do not update those characterization expectations in WP05.

Use the exact safe dual-environment and unique ignored `--basetemp` policy from prior packages. Never update a snapshot or hide a failure.

## Completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP05/WP05.md`

Include:

1. verdict: `COMPLETE`, `BLOCKED`, or `INCOMPLETE`;
2. prerequisite evidence and actual reference paths;
3. before/after schema inventory;
4. exact schema/spec/outcome/issue contracts;
5. five canonical schema tables and six-ID resolution;
6. planet, house, Aspect, role, key, alias, and default policies;
7. complete source-backed role vocabulary with paths;
8. safe failure/error-detail contract;
9. normalized-input examples and deterministic hashes;
10. registry/fingerprint integration;
11. explicit WP05/WP06/WP08/WP09/WP12 boundaries;
12. files changed;
13. test-to-requirement traceability;
14. exact dual-lane commands/counts;
15. cross-process/cross-version schema/input/error fingerprint evidence;
16. WP01–WP04 compatibility, Yoga, lint, snapshot, and artifact evidence;
17. deferred issues assigned to later packages;
18. explicit `WP06_READY: YES` or `WP06_READY: NO`.

## Definition of done

WP05 is complete only when:

- WP04 is complete and reproducible;
- all five canonical definitions contain typed executable immutable schemas;
- all six exposed IDs resolve to the correct schema, with `ASPECT` sharing canonical schema identity;
- strict house, planet, role, key, alias, required/optional, and unknown-key policies are enforced by the validation API;
- successful inputs produce deterministic WP03 `FrozenMapping` values;
- invalid input produces ordered safe typed issues and the canonical invalid-parameter error adapter;
- no raw values/coercive fallback/mutable aliases enter normalized inputs or diagnostics;
- registry/schema fingerprints are stable across process/import order/Python version and sensitive to schema changes;
- handlers, legacy evaluator/cache, loaders, Yoga, Career, and public output remain unchanged;
- the complete dual-lane suite, Yoga orders, rule lint, and unchanged approved snapshots pass;
- no fixed/tracked artifact is written;
- the report records `WP06_READY: YES`.

At the end, provide a concise summary with the verdict, schema/API locations, five/six inventory, planet/house/role/Aspect policies, tests/counts in both lanes, fingerprint evidence, compatibility/snapshot status, files changed, and WP06 readiness. Do not proceed to WP06.