Implement **WP06 — Versioned Capability Catalog, Readiness, and Missing-Data Semantics** for Prompt-01 in the Parasara system.

Do not only review this prompt. Implement all permitted work, validate it, and create the required completion report. Do not proceed to WP07.

## Objective

Create one immutable, versioned predicate-capability system that can distinguish:

- supported versus unsupported capability identity;
- missing capability;
- authoritative empty capability;
- malformed capability;
- capability version mismatch;
- present versus absent requested entity;
- present factual value `False` versus missing/absent data.

WP06 introduces capability definitions, typed registry requirements, read-only inspection adapters, readiness/query outcomes, safe diagnostics, and deterministic catalog fingerprints.

WP06 must not prepare, recompute, mutate, or freeze AstroState; WP07 owns the prepared immutable AstroState boundary and digest. WP08/WP11 apply capability outcomes during canonical handler migration. WP09 incorporates capability versions/readiness into evaluator/cache identity. WP12 uses static capability compatibility during rule validation.

## Prerequisite gate

Before editing:

1. Locate final WP00-R and WP01–WP05 reports.
2. Confirm WP05 records `VERDICT: COMPLETE` and `WP06_READY: YES`.
3. Confirm the production registry has five canonical definitions/six exposed IDs and executable WP05 schemas.
4. Run WP02 model, WP03 canonical, WP04 registry, WP05 parameter, and WP01 characterization suites under Python 3.14 and Python 3.11.
5. Run the full suite, Yoga order/loader-trigger matrix, rule lint, registry/schema fingerprint, and strict snapshots in both lanes.
6. Record Git branch/status and preserve unrelated changes.
7. Inventory every current capability source, shape, producer, version-like field, fallback, mutation, and consumer.

If any prerequisite is absent, inconsistent, or failing, **STOP without editing**.

## Required references

Locate by exact filename and read:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP00-R and WP01–WP05 completion reports;
- `Audit-01-Predicate-Registry.md`;
- `Audit-02-Complete-Predicate-Inventory.md`;
- `Audit-07-Parameter-Validation.md`;
- `Audit-08-Capability-Handling.md`;
- `Audit-09-AstroState-Boundary.md`;
- `Audit-10-Predicate-Purity.md`;
- `Audit-11-Predicate-Cache.md`;
- `Audit-14-Rule-Loader-Compiler-Interaction.md`;
- `Audit-15-Yoga-Engine.md`;
- `Audit-18-Evidence.md`;
- `Audit-21-Determinism.md`;
- `Audit-22-Test-Inventory-Gap-Analysis.md`.

Record actual paths. Stop if authoritative-looking duplicates conflict.

## Package boundary

WP06 may add or modify only:

- predicate-owned capability catalog/models/inspection modules;
- `PredicateDefinition.required_capabilities` and deterministic registry metadata/fingerprint;
- read-only adapters over the current AstroState/source shapes;
- safe capability diagnostic adapters using WP02 canonical errors;
- focused capability tests and narrowly adapted registry tests;
- package exports;
- the WP06 completion report.

WP06 must not:

- change handler bodies or invoke capability checks from the legacy evaluator;
- migrate any handler/caller to canonical `PredicateResult`;
- change WP05 parameter behavior;
- mutate, prepare, enrich, normalize, freeze, or digest AstroState;
- execute aspect, functional-role, exaltation, or other producers;
- overwrite `astro.enrichments['aspects']` or introduce automatic preparation;
- change Yoga preparation/evaluation, Career, rules, scoring, cache, conditions, loader behavior, or public output;
- select new conjunction/whole-sign, exaltation, dignity, functional-role, house-lord, or entity-absence astrology semantics;
- activate `HOUSE_LORDS_COMBINATION` or dormant helpers;
- update snapshots/goldens, schemas, dependencies, or CI;
- begin WP07.

## Representation-preservation decision

The repository currently uses incompatible Aspect representations under the same legacy enrichment key. Do not choose one and do not translate between them in WP06.

Represent them as distinct catalog identities:

- `aspects.basic_conjunction_list` — the normalized list-shaped basic/conjunction representation;
- `aspects.whole_sign_graph` — the dictionary/envelope representation with an `edges` collection used by the registered Aspect handler/Yoga path.

The production predicate definition `ASPECT_EXISTS`/alias `ASPECT` requires `aspects.whole_sign_graph` because that is the shape its current handler consumes. The basic list remains catalogued as a supported repository capability but is not treated as satisfying the graph requirement.

A present basic list where a whole-sign graph is required is a representation mismatch/required capability absence—not an empty graph and not factual unmatched. Do not overwrite, merge, infer conjunction semantics, or change Yoga rules.

## Capability catalog

Implement immutable `CapabilityDefinition` and `CapabilityCatalog` (or repository-equivalent exact names) using WP03 canonical types.

The catalog must include at least these versioned definitions:

1. `planets.normalized`;
2. `planets.house_placement`;
3. `aspects.basic_conjunction_list`;
4. `aspects.whole_sign_graph`;
5. `chart.lagna`;
6. `roles.functional`;
7. `dignity.exaltation_facts`.

Use capability contract version `1.0.0` for the Stage-01 compatibility shapes unless repository evidence proves an approved capability version. This versions the software data contract, not astrology doctrine.

### Capability ID rules

- required lowercase ASCII dotted identifier;
- match `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$`;
- no whitespace, uppercase, aliases, empty segments, operators, paths, or arbitrary punctuation;
- external lookup requires a string, trims outer whitespace, and lowercases ASCII spelling;
- stored identity is exact canonical form.

### `CapabilityDefinition` fields

Use exactly these logical fields unless the locked plan requires an equivalent name:

- `capability_id`;
- `capability_version`;
- `description`;
- `system_scope`;
- `content_kind`;
- `empty_policy`;
- `recoverable_when_missing`.

Recommended typed vocabularies:

- `content_kind`: `collection`, `mapping`, `scalar`, `graph`, `entity_fields`;
- `empty_policy`: `ready_empty` or `empty_not_ready`.

Validation:

- SemVer `MAJOR.MINOR.PATCH`, same strictness as WP04/WP05;
- nonempty trimmed factual description;
- `system_scope='parasara'` for current capabilities;
- actual Boolean recoverability;
- no handlers/producers/callables embedded in definitions;
- definitions are frozen and canonically fingerprintable;
- duplicates rejected atomically;
- catalog finalizes/readies once and becomes immutable;
- deterministic lexicographic enumeration;
- unsupported well-formed ID returns a typed catalog miss, never a factual result.

### Empty policies

Use:

- `aspects.basic_conjunction_list`: `ready_empty`;
- `aspects.whole_sign_graph`: `ready_empty` when the graph envelope is valid and its explicit `edges` collection is empty;
- `roles.functional`: `ready_empty` only when an explicit valid prepared role mapping exists and is empty;
- `dignity.exaltation_facts`: `ready_empty` only when an explicit valid prepared facts mapping exists and is empty;
- `planets.normalized`: `empty_not_ready`;
- `planets.house_placement`: `empty_not_ready` when no authoritative placements exist;
- `chart.lagna`: `empty_not_ready`.

An empty container is never treated as ready merely because a missing value was defaulted to `{}` or `[]`. Ready-empty requires an explicit present container of the correct shape and, where available, matching version/provenance metadata.

## Typed capability requirements in predicate definitions

Replace WP04's tuple of strings with immutable `CapabilityRequirement` values.

Fields:

- `capability_id`;
- `capability_version`;
- `required` — actual Boolean;
- `when_parameters_present` — immutable tuple of WP05 canonical parameter names, empty for unconditional requirements.

Rules:

- catalog ID/version must exist/match when the predicate registry finalizes;
- requirement order deterministic by capability ID then condition tuple;
- no duplicates/conflicting versions;
- conditional parameter names must exist in the predicate's WP05 schema;
- aliases share canonical requirements;
- no dynamic callable predicates in requirement metadata;
- no runtime readiness behavior is triggered in WP06.

Declare requirements from actual handler data access and audited provider dependencies. At minimum:

- `ASPECT_EXISTS`: unconditional `aspects.whole_sign_graph@1.0.0`; add only genuinely accessed conditional planet/house requirements, with evidence;
- `PLANET_IN_HOUSE`: unconditional `planets.normalized@1.0.0` and `planets.house_placement@1.0.0`;
- `HOUSE_OCCUPANT`: the same two capabilities, while remaining a separate predicate;
- `FUNCTIONAL_ROLE`: unconditional `planets.normalized@1.0.0`, `chart.lagna@1.0.0`, and `roles.functional@1.0.0` as the target prepared-fact contract;
- `PLANET_EXALTED`: unconditional `planets.normalized@1.0.0` and `dignity.exaltation_facts@1.0.0`.

If the current Aspect handler does not actually read normalized planets/placements, do not retain misleading WP04 declarations merely because they were descriptive. Record the correction in the report. Provider prerequisites belong to preparation dependency metadata later, not predicate direct requirements, unless explicitly modeled and justified.

## Readiness states

Implement string enum `CapabilityReadiness` with exactly:

- `ready`;
- `ready_empty`;
- `missing`;
- `malformed`;
- `version_mismatch`;
- `unsupported`.

Do not use one ambiguous `empty` status.

Implement immutable `CapabilityInspection` with logical fields:

- `capability_id`;
- `expected_version`;
- `observed_version` — optional;
- `readiness`;
- `source_kind` — safe stable identifier, optional only when absent/unsupported;
- `content_empty` — actual Boolean;
- `issues` — immutable tuple of safe issue codes/records.

Invariants:

- `ready` requires present, valid, nonempty content;
- `ready_empty` requires present, valid, explicitly empty content and `ready_empty` policy;
- `missing` has no observed version/content;
- `version_mismatch` requires safe expected/observed versions;
- `unsupported` means the catalog/system does not define/support the requested capability;
- malformed content never becomes ready-empty;
- no raw content, mutable AstroState object, exception, file path, or producer object is stored in the inspection;
- inspection equality/fingerprint excludes no fields because it contains no telemetry.

## Entity and factual-value distinction

Implement a separate immutable query observation model, such as `CapabilityFactObservation`, with exact typed state vocabulary:

- `present`;
- `absent_entity`;
- `capability_unavailable`;
- `malformed_capability`;
- `version_mismatch`;
- `unsupported_capability`.

Fields should include:

- capability identity/version;
- state;
- canonical entity kind/ID when requested;
- `value_present` Boolean;
- canonical value only when present;
- safe issue codes.

Critical rule: a present factual value `False`, numeric zero, empty string where valid, or empty canonical collection is still **present** when the capability contract says it is a legitimate value. Never infer absence from Python truthiness.

For a complete valid planet collection, a requested canonical planet not present is `absent_entity`, not `missing` capability and not invalid parameters. WP08/WP11 decide how that observation maps into final predicate status/evidence; WP06 does not create a `PredicateResult`.

## Read-only AstroState inspection adapters

Provide one read-only inspection boundary over current compatibility AstroState shapes.

Requirements:

- accepts an AstroState-like object and a catalog requirement;
- never mutates input or nested values;
- never invokes normalizers/enrichments/producers;
- performs no filesystem/network/time/random access;
- does not cache;
- does not attach manifests or enrichments;
- uses exact type/shape checks rather than truthiness;
- catches only expected access/shape failures and converts them to safe issue codes;
- unexpected programming defects remain visible in tests rather than becoming `missing`;
- returns inspection/observation models, not `PredicateResult`.

### Normalized planets

Distinguish:

- missing `planets` attribute/value;
- explicit `None`;
- wrong container type;
- empty correctly typed collection;
- malformed element;
- valid nonempty normalized planet collection;
- duplicate canonical planet IDs;
- valid collection with requested planet absent;
- present entity with factual fields.

Do not require every one of the nine catalog planets to be present unless the existing normalization contract explicitly guarantees that completeness.

### Planet-house placement

Distinguish:

- normalized planets unavailable;
- entity absent;
- present planet but house field unavailable/`None`/invalid;
- valid house 1–12;
- factual nonmatch later (valid observed house differs from requested house).

Do not treat house `1`/`12` or any valid integer as false-like missing.

### Aspect representations

Inspect the legacy `astro.enrichments['aspects']` value without changing it:

- valid list -> `aspects.basic_conjunction_list` readiness according to its shape;
- valid graph mapping/envelope with `edges` list/tuple -> `aspects.whole_sign_graph`;
- explicit valid empty list/empty edges -> corresponding `ready_empty`;
- missing key/container, `None`, wrong representation, malformed edges, missing required graph keys, or incompatible version -> distinct readiness;
- a list must never satisfy graph requirements;
- a graph must never satisfy basic-list requirements;
- do not infer/convert conjunction, whole-sign, target-none, or tradition semantics;
- inspect `config_version` only as safe observed producer metadata; map it to the capability contract version only through an explicit tested compatibility rule, never string coincidence.

If current graph data lacks a formal capability version, report `source_kind='legacy_whole_sign_graph'` with contract adapter version `1.0.0`; do not mutate the graph to add fields.

### Lagna

Distinguish missing, `None`, empty, malformed/unknown sign, and valid canonical sign. Use the repository's existing canonical sign catalog without introducing transliteration or astrology changes.

### Functional roles

WP06 defines the target prepared capability but does not compute it.

Inspect only explicitly stored/prepared role facts if such a location currently exists. If the current registered handler recomputes roles and no prepared facts are stored, report `missing` for `roles.functional`; do not call `compute_functional_roles` and do not read tables.

For explicit prepared facts distinguish missing, empty valid mapping, malformed mapping, absent planet, and present exact role value. Validate role values against the WP05 source-backed role catalog only where the capability shape claims that vocabulary.

### Exaltation facts

Do not select a new authoritative astrology source. Implement explicit read-only compatibility adapters for the currently observed source variants:

- legacy planet flag/dignity-like source;
- legacy metadata `exaltations` mapping.

Record `source_kind` so variants never become indistinguishable. Distinguish missing source, malformed source, absent planet/key, explicit `False`, explicit zero/degree, and present true fact without changing how later predicates interpret degrees versus flags. If both sources conflict, report a safe `conflicting_sources` malformed issue and stop short of choosing one.

WP07 may consolidate prepared facts only under the preservation policy; WP11 handles predicate semantics.

## Static compatibility API

Provide deterministic functions that:

- validate every predicate requirement against the finalized catalog;
- report unknown capability IDs, invalid versions, duplicate/conflicting requirements, and invalid conditional parameters;
- return immutable compatibility results;
- do not inspect a chart for static compatibility;
- do not modify rule loaders in WP06.

Registry finalization must reject statically invalid requirements/catalog mismatches atomically. The production catalog and registry must finalize together without circular import or partial publication.

## Safe capability diagnostics

Provide narrow adapters from unavailable inspections to WP02 `PredicateError` only; do not create `PredicateResult`.

Use stable codes:

- `missing_capability` for `missing`;
- `malformed_capability` for `malformed`;
- `capability_version_mismatch` for `version_mismatch`;
- `unsupported_capability` for `unsupported`.

Use safe fixed messages. Details may contain only:

- canonical predicate ID;
- capability ID;
- expected/observed safe versions;
- readiness/state code;
- safe source kind;
- canonical requested entity kind/ID when applicable;
- ordered safe issue codes.

No raw capability content, exception text, traceback, file path, AstroState serialization, object type `repr`, memory address, or secret data.

Recoverability:

- missing prepared capability: `True`;
- version mismatch: `True` only if re-preparation/configuration can satisfy it; default `True` at this pre-evaluation boundary;
- malformed capability: `False` by default;
- unsupported capability: `False`.

Document that final evaluator cacheability/retry policy belongs to WP09.

## Deterministic catalog/registry fingerprint

Extend the WP05 registry fingerprint with:

- full capability catalog metadata;
- exact typed predicate requirements;
- conditional parameter names;
- versions, empty policies, content kinds, and recoverability;
- finalized/readiness state.

Do not include adapter callables, object IDs, `repr`, source content, or runtime chart readiness.

The fingerprint must be stable across:

- registration order;
- registry-first/predicate-first/Yoga-first imports;
- fresh processes;
- Python 3.14/3.11.

Any capability definition/requirement/version change must change the fingerprint.

## Tests-first requirements

Write failing tests before implementation. Cover at minimum:

### Catalog/definition tests

- exact seven capability definitions;
- IDs, versions, fields, enums, strict Booleans, immutability;
- duplicate/invalid registration atomicity;
- finalization/readiness/post-freeze mutation;
- deterministic enumeration and no backing escape;
- empty policies and content kinds;
- unsupported lookup.

### Predicate requirement tests

- exact five canonical/six exposed predicate requirement inventory;
- Aspect alias shares exact requirements;
- catalog/version/conditional-parameter validation;
- duplicate/conflicting requirements;
- wrong/missing requirement type;
- static compatibility results;
- schema/capability circular-import-free finalization;
- misleading WP04 descriptive requirements corrected from actual handler reads.

### Readiness matrix

For every catalog capability test:

- ready nonempty;
- valid explicit ready-empty where policy allows;
- empty-not-ready where policy forbids;
- missing attribute/key;
- explicit `None`;
- wrong container/type;
- malformed nested content;
- version mismatch;
- unsupported ID;
- repeated deterministic inspection;
- caller-state mutation comparison proving inspection itself does not mutate.

### Entity/factual distinction

- complete capability plus present entity;
- complete capability plus absent entity;
- capability unavailable;
- malformed/version mismatch/unsupported;
- present `False` and numeric zero remain present;
- valid observed house differing from requested is present factual data, not absence;
- invalid parameters remain WP05 errors, not capability outcomes.

### Aspect tests

- list and graph classified as different capabilities;
- empty list and empty graph correctly ready-empty;
- list never satisfies graph and graph never satisfies list;
- missing/None/malformed graph/edges/version;
- legacy graph adapter source/version;
- no conversion, producer invocation, or state overwrite;
- no Aspect semantic assumptions.

### Functional-role/exaltation tests

- no role producer/table I/O invoked;
- absent prepared roles -> missing;
- valid empty prepared roles -> ready-empty;
- malformed/absent entity/present role distinctions;
- each legacy exaltation source variant;
- explicit false/zero/true presence;
- missing/malformed/conflicting sources;
- no semantic source preference.

### Safe diagnostics

- exact code/message/recoverability mapping;
- immutable deterministic details;
- no raw values/exceptions/paths/addresses;
- aliases use canonical predicate ID;
- no `PredicateResult` or handler invocation.

### Purity/determinism/fingerprint

- snapshot AstroState/nested containers before and after every adapter;
- monkeypatch producers, filesystem, clock, randomness, and cache to fail if called;
- repeated/import-order/fresh-process/cross-version fingerprints;
- fingerprint sensitivity to capability metadata/requirements;
- no runtime public-output change.

## Compatibility validation

Run with **GPT-5.6 Sol Medium** implementation discipline and validate first in Python 3.14, then Python 3.11:

1. WP02 model tests;
2. WP03 canonical tests;
3. WP04 registry tests;
4. WP05 parameter tests;
5. new WP06 capability tests;
6. WP01 characterization group;
7. targeted predicate/Yoga/Career/functional-role/aspect/rule-runtime/linter/writer/snapshot set;
8. all WP00-R Yoga orders and both loader-trigger orders;
9. explicit purity tests showing no producer/mutation/I/O/cache use;
10. registry/catalog fingerprint under all import orders;
11. full collection and identical node-ID comparison;
12. complete suite twice in fresh processes;
13. cross-process/cross-version readiness/diagnostic byte-hash probe;
14. rule lint proving five rule files inspected exactly once;
15. strict approved snapshot comparison twice per lane;
16. artifact scan, scoped Git status, and `git diff --check`.

Because WP06 is not wired into legacy execution, all WP01 runtime observations must remain unchanged. Do not alter characterization expectations.

If any test or design requires changing Aspect/Yoga/exaltation/role factual behavior, **STOP**, report the conflict, and recommend switching the review to High reasoning. Do not decide silently.

## Completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP06/WP06.md`

Include:

1. verdict: `COMPLETE`, `BLOCKED`, or `INCOMPLETE`;
2. prerequisite evidence and actual reference paths;
3. before/after capability inventory;
4. exact catalog/definition/requirement/readiness/inspection/observation contracts;
5. seven capability definition table with versions/empty policies;
6. five canonical/six exposed predicate requirement matrix;
7. Aspect representation-preservation evidence;
8. entity/false/empty/missing/malformed/version distinctions;
9. functional-role and exaltation compatibility-adapter policy;
10. safe diagnostic contract;
11. static compatibility and registry finalization behavior;
12. fingerprint schema, bytes, and hashes;
13. explicit WP06/WP07/WP08/WP09/WP11/WP12 boundaries;
14. files changed;
15. test-to-requirement traceability;
16. exact dual-lane commands/counts;
17. cross-process/cross-version inspection/diagnostic/fingerprint evidence;
18. WP01–WP05 compatibility, Yoga, lint, snapshot, purity, and artifact evidence;
19. deferred semantic questions without resolving them;
20. explicit `WP07_READY: YES` or `WP07_READY: NO`.

## Definition of done

WP06 is complete only when:

- WP05 is complete and reproducible;
- one immutable finalized catalog defines the seven locked capabilities;
- every predicate definition has typed catalog-validated versioned requirements;
- list and graph Aspect representations remain distinct;
- readiness distinguishes ready, ready-empty, missing, malformed, version mismatch, and unsupported;
- observations distinguish absent entity and present false/zero from unavailable capability;
- read-only adapters perform no mutation, producer execution, I/O, time, randomness, or caching;
- safe diagnostics contain no raw capability content or exception details;
- catalog/registry fingerprints are stable across order/process/Python version and sensitive to changes;
- no handler/evaluator/cache/loader/Yoga/Career/public behavior changes;
- complete dual-lane tests, Yoga orders, rule lint, and unchanged approved snapshots pass;
- no fixed/tracked artifact is written;
- the report records `WP07_READY: YES`.

At the end, return a concise summary containing the verdict, model/reasoning used, catalog/API locations, seven-capability and five/six requirement inventories, tests/counts in both lanes, fingerprint/diagnostic evidence, compatibility/snapshot status, files changed, deferred semantic issues, and WP07 readiness. Do not proceed to WP07.