You are implementing **WP04 — Predicate Definition Metadata, Deterministic Registry, Bootstrap, and Isolation** for Prompt-01 in the Parasara system.

## Objective

Replace the handler-only, import-side-effect-dependent predicate registry with one validated deterministic registry of immutable predicate definitions while preserving:

- exactly six exposed production IDs;
- exactly five unique production handlers;
- current handler implementations and factual behavior;
- current Yoga, Career, rule, snapshot, and public-output contracts;
- the legacy eight-field runtime result boundary until later migration packages.

WP04 introduces metadata and registry lifecycle only. WP05 owns executable parameter validation, WP06 owns the versioned capability catalog/readiness behavior, and WP08+ own canonical-result/evaluator migration.

## Prerequisite gate

Before editing:

1. Locate the final WP00-R, WP01, WP02, and WP03 reports.
2. Confirm WP03 records `VERDICT: COMPLETE` and `WP04_READY: YES`.
3. Confirm `models.py` and `canonical.py` exist at the paths recorded by WP03.
4. Run WP02 model tests, WP03 canonical tests, WP01 characterization tests, and the complete suite in Python 3.14 and Python 3.11.
5. Confirm Yoga order/loader-trigger tests, repository rule lint, and strict approved snapshots are green.
6. Record Git branch/status and preserve unrelated changes.
7. Inventory every current registry definition, decorator, import side effect, lookup, mutation, direct dictionary access, test registration, cache dependency, and loader reference.

If any prerequisite is absent or failing, **STOP without editing**. Do not infer readiness from an abbreviated summary.

## Required references

Locate by exact filename and read:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP00-R, WP01, WP02, and WP03 completion reports;
- `Audit-01-Predicate-Registry.md`;
- `Audit-02-Complete-Predicate-Inventory.md`;
- `Audit-04-Complete-Caller-Inventory.md`;
- `Audit-07-Parameter-Validation.md`;
- `Audit-08-Capability-Handling.md`;
- `Audit-11-Predicate-Cache.md`;
- `Audit-14-Rule-Loader-Compiler-Interaction.md`;
- `Audit-21-Determinism.md`;
- `Audit-22-Test-Inventory-Gap-Analysis.md`.

Record actual paths. Stop if duplicate authoritative-looking documents conflict.

## Package boundary

WP04 may add or modify only:

- a predicate-owned registry/definition module, or a clearly justified registry section in the current rules engine;
- predicate registration declarations needed to supply metadata without changing handler bodies or outcomes;
- the narrow engine/bootstrap compatibility surface used by current callers;
- registry-focused tests and necessary test-isolation fixtures;
- package exports;
- the WP04 completion report.

WP04 must not:

- migrate handlers to canonical `PredicateResult`;
- alter handler logic, parameters, evidence, trace, errors, or factual outcomes;
- enforce parameter schemas at evaluation time;
- enforce capability readiness at evaluation time;
- change evaluator status/error behavior, cache identity/policy, conditions, rule loading/validation, Yoga, Career, AstroState, rules, scoring, or public output;
- activate `HOUSE_LORDS_COMBINATION` or any dormant Yoga/legacy helper;
- combine `PLANET_IN_HOUSE` and `HOUSE_OCCUPANT`;
- change approved astrology semantics;
- update snapshots/goldens, schemas, dependencies, or CI;
- begin WP05.

## Canonical definition model

Implement immutable `PredicateDefinition` with exactly these metadata fields plus the handler reference:

- `predicate_id`;
- `predicate_version`;
- `description`;
- `parameter_schema`;
- `required_capabilities`;
- `cacheable`;
- `deterministic`;
- `cost_class`;
- `system_scope`;
- `deprecated`;
- `replacement`;
- `aliases`;
- `handler`.

If the locked plan uses a materially different exact field name, reconcile it explicitly in the report. Do not add speculative ownership, scoring, confidence, domain, UI, or public-schema fields.

Use WP03 `FrozenMapping` and tuples for nested metadata. Do not create another immutable mapping implementation.

### Field validation

`predicate_id`:

- required canonical uppercase ASCII identifier matching `^[A-Z][A-Z0-9_]*$`;
- no leading/trailing whitespace;
- no lowercase stored form;
- canonical identity cannot be an operator such as `AND`, `OR`, or `NOT`.

`predicate_version`:

- required SemVer string in `MAJOR.MINOR.PATCH` form;
- nonnegative decimal components with no leading zeros except zero itself;
- no `v` prefix, blank value, implicit integer, or arbitrary label;
- pre-release/build suffixes are out of scope for Stage-01 unless the repository already has an approved parser requiring them;
- aliases retain the canonical definition's exact version.

For the five existing compatible handler implementations, use explicit initial version `1.0.0` unless repository evidence proves an already approved predicate-contract version. This version labels the compatibility implementation contract; it does not claim astrology-rule maturity.

`description`:

- required non-empty trimmed human-readable string;
- factual and implementation-neutral;
- no astrology claims beyond existing handler behavior.

`parameter_schema`:

- required `FrozenMapping` metadata;
- in WP04 it describes the currently observed parameter names, required/optional status, and current defaults only;
- it is not executable and must not reject or normalize runtime input yet;
- it must not silently legitimize questionable semantics;
- WP05 replaces/extends this with the approved executable strict schemas.

`required_capabilities`:

- required tuple of unique stable non-empty strings in deterministic order;
- describe observed data dependencies only;
- do not perform readiness checks in WP04;
- WP06 owns the versioned catalog and runtime semantics.

`cacheable` and `deterministic`:

- actual Booleans;
- reject `cacheable=True` with `deterministic=False`;
- declarations do not alter the current cache in WP04;
- all current classifications require evidence in the report.

`cost_class`:

- string-valued enum with exactly `low`, `medium`, and `high`;
- classify current handlers from observed bounded work, not timing telemetry;
- no scheduler behavior is implemented in WP04.

`system_scope`:

- required stable lowercase scope identifier;
- use `parasara` for all five current canonical definitions;
- no plugin-loading architecture is introduced.

`deprecated`:

- actual Boolean;
- default `False`.

`replacement`:

- `None` or a canonical predicate ID;
- cannot reference self or an alias spelling;
- if present, must resolve to another canonical definition at registry freeze/finalization;
- detect replacement cycles;
- no current canonical definition requires a replacement.

`aliases`:

- immutable tuple of unique canonical-format IDs;
- cannot include the canonical ID;
- cannot collide with another canonical ID or alias;
- cannot contain logical operators;
- aliases are lookup vocabulary, not duplicate definitions.

`handler`:

- required callable;
- preserve handler identity;
- do not wrap handlers in a way that changes signature, name, module, exceptions, or return behavior.

## Locked production inventory and alias policy

The registry must expose exactly these six IDs:

- `ASPECT`;
- `ASPECT_EXISTS`;
- `FUNCTIONAL_ROLE`;
- `HOUSE_OCCUPANT`;
- `PLANET_EXALTED`;
- `PLANET_IN_HOUSE`.

Canonical definitions/handlers are exactly five:

- canonical `ASPECT_EXISTS`, with explicit alias `ASPECT`;
- `FUNCTIONAL_ROLE`;
- `HOUSE_OCCUPANT`;
- `PLANET_EXALTED`;
- `PLANET_IN_HOUSE`.

`ASPECT` lookup must resolve to the same immutable definition and handler identity as `ASPECT_EXISTS`. The canonical ID/version remain `ASPECT_EXISTS`/its canonical version. Preserve current Yoga rules that use `ASPECT`; do not rewrite rule files.

Do not mark `ASPECT` as a separate canonical definition. Do not deprecate it in WP04. Do not treat case variants as declared aliases.

`PLANET_IN_HOUSE` and `HOUSE_OCCUPANT` remain separate canonical vocabulary despite overlapping behavior. WP04 must not alias or merge them.

## Registry lifecycle and API

Implement a dedicated `PredicateRegistry` with clear build and frozen/read-only phases.

Required behavior:

- register validated `PredicateDefinition` objects during build only;
- reject every duplicate canonical ID, even if metadata/handler is identical;
- reject canonical/alias collisions and alias/alias collisions;
- reject invalid definitions before mutating registry state;
- finalization validates alias targets, replacements, cycles, and complete metadata;
- after finalization, registration/removal/replacement/reset fails explicitly;
- lookup normalizes external ID input by requiring a string, trimming surrounding whitespace, and uppercasing ASCII spelling;
- blank, malformed, and non-string lookup values fail explicitly at the registry API rather than silently becoming unknown;
- unknown well-formed IDs return a clear registry miss (`None` or a dedicated internal lookup exception, selected and tested consistently) without creating a factual result;
- enumeration is deterministic lexicographic order, independent of registration/import order;
- canonical-definition enumeration returns five definitions exactly once;
- exposed-ID enumeration returns six IDs exactly once;
- metadata snapshots are immutable/read-only;
- handler lookup preserves the existing callable identity;
- registry readiness/frozen state is queryable;
- no public mutable dictionary or backing store escapes.

Do not connect unknown registry lookup to new typed evaluator outcomes in WP04. Existing evaluator compatibility behavior must remain unchanged until its approved migration package.

## Deterministic bootstrap

Eliminate production availability dependence on consumers importing `predicates.py` for decorator side effects.

Implement one explicit, idempotent production bootstrap that:

- constructs a fresh registry;
- registers the five built-in definitions in one explicit deterministic place;
- finalizes/freezes the registry;
- publishes one read-only production instance/view;
- is safe when called repeatedly;
- does not depend on filesystem enumeration, arbitrary module discovery, plugin scanning, test order, or prior Yoga imports;
- detects a partially initialized or failed bootstrap rather than publishing incomplete state;
- yields the same definition metadata, ID order, handler identities, and canonical digest/serialization evidence in fresh processes and both Python lanes.

Avoid circular imports. Prefer explicit local imports or a dedicated built-in-definition factory over global decorator mutation. If decorators remain as declaration syntax, they must target an explicit builder during bootstrap and must not mutate a process-global registry merely by module import.

## Legacy compatibility surface

Current evaluator/tests may expect `PREDICATE_REGISTRY.get(id)` to return a handler. Preserve this only through a named read-only compatibility mapping/view backed by the authoritative registry.

Requirements:

- it contains the same six exposed IDs;
- `.get`/lookup returns the existing handler callable;
- it cannot be mutated, cleared, or overwritten;
- it is never a second source of truth;
- it is documented for removal during evaluator/caller migration;
- current handler/evaluator behavior remains characterized and unchanged.

Update any legacy test that dynamically registers `RAISE_TEST` into the production global. Such tests must use an isolated unfrozen test registry or a scoped registry dependency with `yield/finally` restoration. A test must never mutate/freeze/reset the production registry.

Do not add a production global reset hook merely for tests.

## Parameter/capability metadata boundary

Build a truthful inventory for each canonical definition from current handler reads and audits.

At minimum record:

- `ASPECT_EXISTS`: current optional `from_house`, `to_house`, `from_planet`, `to_planet`; observed planet/aspect data dependency;
- `PLANET_IN_HOUSE`: current required `planet`, `house`; planet/house data dependency;
- `HOUSE_OCCUPANT`: current required `house`, `planet`; planet/house data dependency;
- `FUNCTIONAL_ROLE`: current `role_in` default and contextual planet behavior; functional-role/planet data dependency;
- `PLANET_EXALTED`: current required `planet`; planet/exaltation-fact dependency.

This metadata must not change what current handlers accept or return. Clearly label observed compatibility defaults separately from WP05 approved normalization rules.

## Tests-first requirements

Write failing registry tests before production changes. Cover at minimum:

### Definition validation

- every required field;
- exact field inventory;
- valid/invalid canonical IDs;
- all SemVer acceptance/rejection cases;
- descriptions;
- strict Booleans;
- exact cost classes and system scope;
- immutable parameter/capability/alias metadata;
- callable validation;
- cacheable/deterministic consistency;
- replacement self-reference/cycles/missing target;
- alias self/collision/operator cases.

### Registration/lifecycle

- successful five-definition build;
- invalid registration leaves builder unchanged;
- duplicate canonical ID rejected;
- duplicate handler under distinct canonical IDs is allowed only for the explicit alias policy—not by registering a second `ASPECT` definition;
- finalize/freeze behavior;
- all mutation after freeze rejected;
- readiness state;
- no backing-store escape.

### Alias and lookup

- exact six exposed IDs/five canonical definitions/five handlers;
- `ASPECT` and `ASPECT_EXISTS` resolve to the same definition and handler identity;
- alias retains canonical ID/version;
- case/outer-whitespace lookup normalization;
- malformed/non-string/blank lookup rejection;
- unknown well-formed lookup behavior;
- `PLANET_IN_HOUSE` and `HOUSE_OCCUPANT` remain distinct.

### Bootstrap/determinism

- explicit bootstrap works without prior predicate/Yoga import side effects;
- repeated bootstrap is idempotent;
- import order does not change inventory;
- deterministic canonical/exposed enumeration;
- fresh-process metadata/handler-name fingerprint equality;
- Python 3.14/3.11 fingerprint equality;
- failed bootstrap does not publish a partial registry.

### Test isolation

- isolated registry registration cannot affect production registry;
- failed tests/fixtures restore scoped state;
- no `RAISE_TEST` leakage;
- production registry remains frozen and unchanged across test orders;
- no cache interaction or invalidation is introduced in WP04.

### Metadata inventory

- all five canonical definitions have complete fields;
- all six exposed IDs resolve;
- versions are valid and aliases share canonical version;
- parameter schema and capabilities are present and immutable;
- cost/cache/determinism/scope declarations are explicit;
- no logical operator or `HOUSE_LORDS_COMBINATION` appears as a registered predicate.

Do not write tests that enforce WP05 parameter values or WP06 capability readiness outcomes.

## Compatibility validation

Run in Python 3.14 first and Python 3.11 second:

1. WP02 model tests;
2. WP03 canonical tests;
3. new WP04 registry tests;
4. WP01 characterization tests;
5. legacy evaluator/registry tests adapted only for isolation;
6. targeted predicate/Yoga/Career/functional-role/rule-runtime/linter/writer/snapshot set;
7. all WP00-R Yoga node-ID orders and both loader-trigger orders;
8. explicit fresh-process evaluation of all six exposed IDs without a prior side-effect import;
9. full collection and identical node-ID comparison;
10. complete suite twice in fresh processes;
11. cross-process/cross-version registry fingerprint comparison;
12. repository rule lint proving five supported rule files inspected once;
13. strict approved snapshot comparison twice per lane;
14. artifact scan, scoped Git status, and `git diff --check`.

The fingerprint must include deterministic exposed IDs, canonical IDs, versions, aliases, handler module/qualified name, non-handler metadata, and registry frozen/readiness state. Do not serialize callable `repr` or memory addresses.

Use the safe dual-environment and unique ignored `--basetemp` policy from WP00-R/WP03. Never update snapshots or hide failures.

## Completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP04/WP04.md`

Include:

1. verdict: `COMPLETE`, `BLOCKED`, or `INCOMPLETE`;
2. prerequisite evidence and actual reference paths;
3. before/after registry/import/mutation inventory;
4. exact `PredicateDefinition` field/type/validation table;
5. five canonical definitions and six exposed IDs table;
6. alias resolution and identity evidence;
7. observed parameter/capability metadata with WP05/WP06 boundary;
8. bootstrap/freeze/read-only architecture;
9. temporary legacy compatibility view and removal package;
10. files changed;
11. test-to-requirement traceability;
12. exact dual-lane commands/counts;
13. fresh-process/cross-version fingerprint evidence;
14. WP01–WP03 compatibility, Yoga, lint, snapshot, and artifact evidence;
15. deferred issues assigned to later packages;
16. explicit `WP05_READY: YES` or `WP05_READY: NO`.

## Definition of done

WP04 is complete only when:

- WP03 is complete and reproducible;
- one authoritative immutable definition registry exists;
- the definition model contains all locked metadata and valid SemVer;
- exactly five canonical definitions expose exactly six production IDs;
- `ASPECT` is an explicit alias resolving to canonical `ASPECT_EXISTS` with identical handler/version;
- deterministic explicit bootstrap removes consumer import-side-effect dependence;
- duplicates, invalid definitions, collisions, bad replacements, and post-freeze mutations are rejected;
- canonical and exposed enumeration is deterministic across order/process/Python version;
- isolated tests cannot mutate production registry;
- current evaluator behavior remains available through one read-only compatibility view;
- no runtime parameter/capability enforcement, handler migration, or public-output change occurs;
- the complete dual-lane suite, Yoga orders, rule lint, and unchanged approved snapshots pass;
- no fixed/tracked artifact is written;
- the report records `WP05_READY: YES`.

At the end, provide a concise summary with the verdict, registry/definition locations, five/six inventory, alias policy, bootstrap behavior, test counts for both lanes, fingerprint evidence, compatibility/snapshot status, files changed, and WP05 readiness. Do not proceed to WP05.