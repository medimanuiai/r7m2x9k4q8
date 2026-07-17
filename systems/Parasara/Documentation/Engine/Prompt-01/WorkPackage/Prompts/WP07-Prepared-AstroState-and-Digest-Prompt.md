Implement **WP07 — Prepared Immutable AstroState Boundary, Typed Evaluation Context, and Canonical Content Digest** for Prompt-01.

Do not only review this prompt. Implement all permitted work, validate it, and create the required completion report. Do not proceed to WP08.

## Objective

Introduce a predicate-owned immutable prepared-state boundary that:

- snapshots predicate-relevant normalized facts without retaining mutable aliases;
- records the WP06 capability manifest, readiness, source kind, contract versions, and prepared content;
- provides canonical read-only factual queries;
- separates preparation from evaluation;
- provides deterministic state and context projections/UTF-8 bytes/SHA-256 digests;
- rejects or truthfully records malformed/missing inputs without converting them to factual false;
- prevents object identity, mutation order, telemetry, diagnostics, Yoga output, or unrelated data from entering predicate state identity.

WP07 must coexist with the mutable legacy `AstroState`; it must not redirect current handlers/evaluator/Yoga/Career to the prepared state. WP08 introduces the first canonical handler using this boundary. WP09 uses the state/context digests for evaluator/cache identity.

## Prerequisite gate

Before editing:

1. Locate final WP00-R and WP01–WP06 reports.
2. Confirm WP06 records `VERDICT: COMPLETE` and `WP07_READY: YES`.
3. Confirm WP03 canonical APIs, WP04 registry, WP05 schemas, and WP06 catalog/inspection APIs exist at their reported paths.
4. Run WP02–WP06 focused tests and WP01 characterization in Python 3.14 and Python 3.11.
5. Run the full suite, Yoga order/loader-trigger matrix, rule lint, catalog/registry fingerprints, and strict snapshots in both lanes.
6. Record Git branch/status and preserve unrelated changes.
7. Inventory the actual mutable AstroState model, nested models, producer/preparation paths, current capability locations, diagnostic/output fields, context uses, and all mutation points.

If any prerequisite is absent, inconsistent, or failing, **STOP without editing**.

## Required references

Locate by exact filename and read:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP00-R and WP01–WP06 completion reports;
- `Audit-02-Complete-Predicate-Inventory.md`;
- `Audit-07-Parameter-Validation.md`;
- `Audit-08-Capability-Handling.md`;
- `Audit-09-AstroState-Boundary.md`;
- `Audit-10-Predicate-Purity.md`;
- `Audit-11-Predicate-Cache.md`;
- `Audit-15-Yoga-Engine.md`;
- `Audit-18-Evidence.md`;
- `Audit-19-Trace.md`;
- `Audit-20-Serialization-Public-Output.md`;
- `Audit-21-Determinism.md`;
- `Audit-22-Test-Inventory-Gap-Analysis.md`.

Record actual paths. Stop if authoritative-looking duplicates conflict.

## Package boundary

WP07 may add or modify only:

- predicate-owned prepared-state, preparation, query, and typed-context modules;
- WP06 capability code only where necessary to project/rehydrate its immutable readiness models through the prepared boundary;
- deterministic prepared-state/context serialization and digest helpers using WP03 canonical APIs;
- focused prepared-state/digest/purity tests;
- narrow registry/catalog fingerprint tests if static versions are referenced;
- package exports;
- the WP07 completion report.

WP07 must not:

- modify the existing mutable `AstroState` model or normalizer behavior unless a compile/import-only annotation is unavoidable and separately justified;
- mutate an input AstroState or any nested value;
- invoke normalizers, enrichment producers, varga/aspect/role/exaltation computation, loaders, filesystem, network, environment, clock, randomness, cache, or public serializers;
- change handler bodies or signatures;
- redirect the legacy evaluator/cache/conditions/Yoga/Career to prepared state;
- migrate any predicate to canonical `PredicateResult`;
- change WP05 validation or WP06 readiness semantics;
- choose or convert Aspect representations;
- choose a preferred exaltation source or reinterpret degree/flag facts;
- compute functional roles or select table/heuristic modes;
- include Yoga results, scores, narratives, diagnostics, public output, or unrelated enrichments in state identity;
- update rules, tables, snapshots/goldens, schemas, dependencies, CI, or public output;
- begin WP08.

## Lifecycle decision

Use this explicit lifecycle:

```text
mutable compatibility AstroState / explicit prepared capability supplies
    -> read-only preparation and validation
    -> immutable PreparedAstroState
    -> canonical queries and digest
    -> later predicate evaluation
```

Preparation may truthfully produce a prepared state containing `missing`, `ready_empty`, `malformed`, `version_mismatch`, or `unsupported` capability entries. Missing capability is not itself a preparation exception. The prepared state is a faithful immutable snapshot of what was available.

Preparation fails without producing a state only for contract-level failures such as:

- invalid preparation input object;
- impossible duplicate canonical entity identity;
- unsafe/cyclic/unsupported canonical content;
- contradictory manifest/content invariants;
- unexpected programming defect.

Expected missing/malformed capability states remain represented inside a successfully constructed snapshot so later canonical predicates can produce truthful typed results.

## Core version boundaries

Define stable SemVer constants or immutable version fields:

- prepared-state schema version: `1.0.0`;
- preparation contract/producer version: `1.0.0`;
- normalization compatibility version: explicit nonempty SemVer. Use `1.0.0` for the current adapter contract unless repository evidence proves an approved normalization version;
- system scope: `parasara`.

These version the software data contract, not astrology doctrine.

Every prepared state and digest includes these versions plus every included WP06 capability contract version. Do not derive versions from file timestamps, Git working state, package installation paths, or runtime object identity.

## Prepared models

Implement immutable predicate-owned models using WP03 `FrozenMapping`, tuples, and canonical policies.

### `PreparedPlanet`

Required logical fields:

- `planet_id` — one of the nine WP05 canonical planet IDs;
- `house` — strict integer 1–12 or `None` when unavailable;
- `sign` — canonical repository sign or `None` when unavailable;
- `source_index` — do not include unless it is required solely for compatibility ordering; if included, it must not enter semantic identity unless output order depends on it.

Do not place exaltation, role, strength, score, narrative, raw provider, or mutable flags on the planet model. Those facts belong to versioned capability content.

Reject duplicate planet IDs. Store planets in canonical nine-planet catalog order, with absent catalog planets omitted. Do not require all nine planets.

### `PreparedCapability`

Required logical fields:

- `capability_id`;
- `capability_version`;
- `readiness` — WP06 `CapabilityReadiness`;
- `source_kind`;
- `content_empty`;
- `content` — canonical immutable value or `None` according to readiness;
- `issues` — immutable ordered safe issue codes.

Invariants:

- `ready` requires valid nonempty canonical content;
- `ready_empty` requires explicit valid empty canonical content and a catalog `ready_empty` policy;
- unavailable states carry no factual content;
- malformed/version-mismatch/missing/unsupported states preserve safe issues but no raw source;
- capability identity/version must match the finalized WP06 catalog except an explicitly represented unsupported request;
- source kind remains representation-specific;
- no producer callable, path, raw exception, telemetry, mutable object, or full AstroState is retained.

### `PreparedAstroState`

Required logical fields:

- `schema_version`;
- `producer_version`;
- `normalization_version`;
- `system_scope`;
- `lagna_sign` — canonical sign or `None`;
- `planets` — canonical ordered tuple of `PreparedPlanet`;
- `capabilities` — `FrozenMapping[str, PreparedCapability]` or an equivalently immutable deterministic mapping;
- `source_fingerprint` — omit unless a safe provider-independent factual identifier is already authoritative; never use object ID/path/raw payload hash;

Do not add cache hit, timing, run ID, UUID, generated timestamp, Yoga output, diagnostics, scores, confidence, public projection, or arbitrary metadata.

If `FrozenMapping` cannot directly hold model objects under WP03's strict canonical policy, store dedicated canonical projections or implement an explicit model-owned immutable mapping without weakening WP03. Do not teach the general canonical freezer to reflect arbitrary dataclasses.

## Capability content contracts

Prepared content must be explicit and representation-preserving.

### `planets.normalized`

Content is the canonical ordered tuple of prepared planet factual projections needed by current registered predicates. Include canonical planet identity and sign/house only when present. Do not include raw coordinates, strength, vargas, diagnostics, source models, or unrelated metadata.

### `planets.house_placement`

Content is a canonical mapping from present planet ID to strict house 1–12. A present planet with unavailable/invalid house must not be inserted as `None`; readiness/issues must reflect incomplete/malformed placement facts.

Do not silently discard malformed placements and claim ready. If some present planets have valid placements and others are unavailable, classify using a documented deterministic completeness policy. Prefer `malformed`/incomplete for the capability rather than a misleading partial-ready state, while retaining no unsafe partial content.

### `aspects.basic_conjunction_list`

Content is the WP03-frozen exact validated compatibility list representation. Preserve semantic/source order. Do not convert to graph, infer aspects, sort edges, or reinterpret fields.

### `aspects.whole_sign_graph`

Content is a validated frozen graph projection with explicit `edges` sequence and safe producer/config metadata already present.

- preserve edge order and duplicates because current evidence/output may depend on them;
- include only fields currently consumed by registered Aspect behavior or required to establish graph contract/version;
- do not sort edges into a semantic set;
- do not convert basic list content;
- do not infer conjunction, target-none, or tradition profile;
- an empty valid edge sequence remains ready-empty.

### `chart.lagna`

Content is the exact canonical repository sign string. Missing/invalid remains unavailable readiness; do not infer from houses or raw provider input.

### `roles.functional`

Content is a canonical mapping from canonical planet ID to an exact WP05 source-backed role value. Preparation consumes only explicitly available prepared facts or an explicitly supplied already-computed mapping. It must never call role producers or read tables.

Preserve exact `benefic`/`malefic` versus `functional_*` values; do not alias them. Empty valid explicitly supplied mapping can be ready-empty.

### `dignity.exaltation_facts`

Content must preserve source interpretation without choosing astrology semantics. Use an explicit source-discriminated canonical projection, for example per-planet records containing:

- canonical planet ID;
- source kind (`legacy_planet_flags` or `legacy_metadata_exaltations`);
- factual value exactly as validated (`True`, `False`, zero/finite degree, or other already-approved scalar form);
- no interpretation such as “degree means matched.”

Conflicting overlapping source values remain malformed `conflicting_sources`; do not choose one. Empty explicit valid source can be ready-empty.

## Preparation input and explicit supplies

Provide one API such as:

`prepare_predicate_state(astro, *, capability_supplies=None, versions=None) -> PreparationOutcome`

The exact name may follow repository conventions.

Rules:

- inspect the compatibility AstroState through WP06 read-only adapters;
- accept optional explicit already-computed capability supplies for facts not stored on AstroState, especially functional roles;
- supplies must declare capability ID/version/source kind/content and pass the same strict capability validation;
- supplied data overrides a missing compatibility location only when explicitly provided;
- do not allow a supply silently to override conflicting present compatibility facts; report a deterministic conflict;
- no arbitrary producer callback or lazy callable;
- no filesystem/path-based supply;
- input/supply mappings are defensively copied and never mutated;
- unknown capability supply rejected safely;
- output ordering independent of supply mapping insertion order.

Implement immutable `PreparationIssue` and `PreparationOutcome` or an equivalent typed expected-result contract. Ordinary capability unavailability is inside the prepared state, not duplicated as a fatal issue. Fatal issues contain safe paths/codes only and no raw values.

## Canonical query API

Provide read-only provider-independent queries over `PreparedAstroState`, returning WP06 `CapabilityInspection`/`CapabilityFactObservation` or equally compatible typed results.

At minimum:

- inspect capability by typed requirement;
- find canonical planet;
- observe planet house;
- observe Lagna;
- retrieve exact Aspect capability representation;
- observe prepared functional role;
- observe prepared exaltation fact without interpreting it.

Queries:

- never raise for expected missing entity/capability;
- distinguish absent entity from capability unavailable/malformed/version mismatch;
- preserve present `False` and numeric zero;
- never return mutable backing data;
- do not invoke producers, I/O, clock, randomness, cache, or global state;
- do not create `PredicateResult`;
- have deterministic results and issue ordering.

## Typed evaluation context

Implement minimal immutable `PredicateEvaluationContext` with exactly the behavior-changing Stage-01 fields needed now:

- `system_scope` — `parasara`;
- `evaluation_mode` — stable string enum/value, initially `default`;
- `selected_planets` — `None` means all eligible planets; immutable canonical tuple means explicit selection; empty tuple means explicitly none;
- `evaluation_instant` — optional explicit canonical UTC instant field reserved for predicates that declare it relevant; current five predicates must not read/default it from system time.

Do not add user identity, locale, narrative mode, UI state, trace ID, request ID, timezone guessing, system clock fallback, scores, or arbitrary context mappings.

Validation:

- selected planets use WP05 canonical normalization;
- duplicates rejected;
- stored in canonical catalog order;
- `None`, empty tuple, and nonempty tuple remain distinct;
- instant, when supplied, must be timezone-aware UTC and serialized in one exact canonical format; no current predicate requirement depends on it;
- no implicit current time.

Provide deterministic context projection/bytes/SHA-256 separate from state digest. WP09 combines relevant context identity with state/predicate/parameter/capability versions.

## Digest policy

Provide dedicated canonical projections, UTF-8 bytes, and SHA-256 functions for prepared state and evaluation context.

State digest includes exactly:

- prepared-state schema, producer, normalization versions;
- system scope;
- canonical Lagna fact;
- canonical ordered prepared planets;
- every included capability ID, contract version, readiness, source kind, content-empty flag, safe issues, and prepared content;
- explicit representation identity for basic Aspect list versus whole-sign graph;
- exact source-discriminated exaltation facts;
- prepared functional-role facts/version.

State digest excludes:

- Python object ID/hash/repr;
- mutable source object identity;
- raw Surya/provider payload and file paths;
- arbitrary metadata/diagnostics;
- location unless a current registered predicate factually consumes it (currently none);
- Yoga results or other downstream outputs;
- Career/domain results, scores, confidence, narrative;
- cache hit, timing, trace/run IDs, UUID, generated timestamp;
- system clock/environment;
- unrelated varga, strength, Dasha, transit, or public-output data;
- evaluation context, which has its own digest;
- registry/predicate/schema fingerprint, which WP09 includes separately.

Use WP03 canonical JSON configuration and lowercase SHA-256. Do not use Pydantic `.dict()`/`.model_dump()` or generic dataclass reflection as the canonical state serializer.

## Equality and semantic ordering

- Prepared models are deeply immutable.
- Logical equality follows the exact canonical projection.
- Mapping insertion order does not matter.
- Planet tuple order is canonical catalog order.
- Role mapping order does not matter.
- Aspect edge/list sequence order **does** matter in WP07 because current handler evidence/order may depend on it; reordered edges therefore produce a different digest until later semantics explicitly canonicalize output.
- Duplicate Aspect edges remain significant and produce a different digest.
- Diagnostic/source container order outside the prepared projection does not matter.
- Equivalent independently created source objects produce the same state digest.
- Mutating the original source after preparation cannot alter prepared state/digest.
- Any predicate-relevant prepared fact/readiness/version change changes the digest.
- Any excluded diagnostic/Yoga/public/telemetry-only change leaves the digest unchanged.

## Purity and boundary enforcement

Add executable tests/static checks proving preparation and queries:

- import no raw `Chart`, Surya adapter, provider-specific JSON reader, domain interpreter, scoring layer, or public assembler;
- do not call enrichments/producers;
- do not access filesystem/network/subprocess/environment/system clock/random UUID;
- do not mutate AstroState, supplies, registries, caches, rule registries, or globals;
- do not retain mutable caller aliases;
- do not attach a digest/manifest to mutable AstroState;
- do not use `id()`, `hash()` persistence, `repr`, pickle, or `default=str`;
- do not depend on CWD or test order.

Do not modify existing Yoga mutation/preparation in WP07. Characterize it as legacy caller behavior and keep prepared-state construction separate.

## Tests-first requirements

Write failing tests before implementation. Cover at minimum:

### Model/lifecycle tests

- exact fields, strict versions/enums/Booleans, invariants, immutability;
- preparation success with ready and unavailable capabilities;
- fatal preparation outcome with no state;
- missing/malformed capability remains representable in a successful state;
- duplicate planets/capabilities/supplies/conflicts;
- no mutable backing escape/caller alias;
- unknown/unsupported canonical content rejection.

### Capability preparation matrix

- all seven capability identities;
- ready, ready-empty, missing, malformed, version mismatch, unsupported where applicable;
- list/graph Aspect separation and exact sequence preservation;
- empty Aspect representation;
- normalized planets and placement completeness;
- valid/empty/malformed supplied roles;
- each exaltation source, false/zero/true, empty, missing, malformed, conflict;
- no source preference/conversion.

### Query tests

- planet present/absent/capability unavailable;
- house present/different/missing/malformed;
- Lagna;
- Aspect representation retrieval;
- functional role present/absent/missing;
- exaltation factual value without interpretation;
- present false/zero preserved;
- immutable returned values and deterministic issues.

### Context tests

- default/all, explicit empty, and selected planets distinct;
- normalization/catalog order/duplicate rejection;
- no system-time fallback;
- valid explicit UTC instant and invalid naive/non-UTC values;
- exact projection/bytes/hash;
- current predicate requirement metadata does not claim instant dependency.

### Digest tests

- exact representative canonical bytes and SHA-256;
- independently equivalent sources/states produce identical digest;
- mapping insertion order independence;
- source mutation after preparation has no effect;
- every included fact/readiness/version/source/content change affects digest;
- Aspect edge reorder/duplicate affects digest;
- list versus graph affects digest;
- excluded diagnostics/metadata/Yoga/output/telemetry changes do not affect digest;
- no object identity/CWD/time/random dependence;
- fresh-process and cross-Python equality;
- strict round-trip if a dedicated prepared-state deserializer is implemented; do not require one unless needed by architecture.

### Purity/static tests

- monkeypatch every producer/I/O/time/random/cache path to fail if called;
- before/after deep snapshots of AstroState and supplies;
- import/AST enforcement for raw provider/domain boundaries;
- no digest attachment/mutation;
- test order and repeated preparation independence.

## Compatibility validation

Use **GPT-5.6 Sol Medium** and validate first in Python 3.14, then Python 3.11:

1. WP02 model tests;
2. WP03 canonical tests;
3. WP04 registry tests;
4. WP05 parameter tests;
5. WP06 capability tests;
6. new WP07 prepared-state/digest/context/purity tests;
7. WP01 characterization group;
8. targeted predicate/Yoga/Career/functional-role/aspect/rule-runtime/linter/writer/snapshot set;
9. all WP00-R Yoga orders and both loader-trigger orders;
10. registry/catalog/schema fingerprints;
11. full collection and identical node-ID comparison;
12. complete suite twice in fresh processes;
13. cross-process/cross-version prepared-state/context byte/hash probe;
14. rule lint proving five supported rule files inspected once;
15. strict approved snapshot comparison twice per lane;
16. artifact scan, scoped Git status, and `git diff --check`.

Because WP07 remains parallel to legacy execution, all WP01 runtime behavior must remain unchanged. Do not modify characterization expectations.

If implementation needs to change Aspect/Yoga/exaltation/functional-role/public behavior, **STOP**, report the conflict, and escalate review to High reasoning.

## Completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP07/WP07.md`

Include:

1. verdict: `COMPLETE`, `BLOCKED`, or `INCOMPLETE`;
2. model/reasoning used;
3. prerequisite evidence and actual reference paths;
4. before/after AstroState/preparation/query/digest inventory;
5. exact prepared planet/capability/state/outcome/context contracts;
6. software version boundaries;
7. capability content tables and representation preservation;
8. preparation lifecycle and explicit-supply policy;
9. canonical query matrix;
10. exact state/context projection and digest inclusion/exclusion tables;
11. semantic ordering/equality decisions;
12. purity/static-boundary evidence;
13. explicit WP07/WP08/WP09 boundaries;
14. files changed;
15. test-to-requirement traceability;
16. exact dual-lane commands/counts;
17. cross-process/cross-version bytes/hashes;
18. WP01–WP06 compatibility, Yoga, lint, snapshot, and artifact evidence;
19. deferred semantic questions without resolving them;
20. explicit `WP08_READY: YES` or `WP08_READY: NO`.

## Definition of done

WP07 is complete only when:

- WP06 is complete and reproducible;
- one immutable predicate-ready state and typed context boundary exists;
- preparation snapshots facts/capabilities without mutation, producer execution, I/O, time, randomness, or caching;
- all WP06 readiness/entity/representation distinctions survive preparation and queries;
- state/context canonical bytes and SHA-256 are stable across source identity/process/Python version;
- digest includes every current predicate-relevant fact/readiness/version and excludes all locked unrelated/telemetry/output data;
- source mutation cannot affect prepared state/digest;
- list/graph Aspect and exaltation source identities remain distinct;
- no handler/evaluator/cache/Yoga/Career/public behavior changes;
- complete dual-lane tests, Yoga orders, rule lint, and unchanged approved snapshots pass;
- no fixed/tracked artifact is written;
- the report records `WP08_READY: YES`.

At the end, return a concise summary containing the verdict, model/reasoning used, prepared-state/context/API locations, version and digest policies, tests/counts in both lanes, cross-version hash evidence, purity/compatibility/snapshot status, files changed, deferred semantic issues, and WP08 readiness. Do not proceed to WP08.