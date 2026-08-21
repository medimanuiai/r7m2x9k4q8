# Prompt-04 — AstroState API

Status: APPROVED — IMPLEMENTATION AUTHORIZED
Authority: Jyothishyam Master Architecture Specification v1.0 and Prompt-Plan
Owner: Parāśara engine maintainers
Last reviewed: 2026-08-18
Official implementation unit: Prompt-04
Predecessor: Prompt-03 — InferenceEngine
Successor: Prompt-05 — Typed Domain Models
Supported implementation and validation platform: Windows, Python 3.11 and Python 3.14

## 1. Governing references and authority

Implement this specification under the following precedence:

1. `Documentation/AI-Prompt/Jyothishyam Master Architecture Specification v1.0.docx` — governing architecture and highest authority.
2. `Documentation/AI-Prompt/Prompt-Plan.docx` — official Prompt-00 through Prompt-10 sequence and titles.
3. `Documentation/AI-Prompt/Prompt-01.docx` — authoritative predecessor contract for immutable predicate evaluation.
4. The approved standalone Prompt-02 RuleMatch specification and merged Prompt-02 implementation.
5. The approved standalone Prompt-03 InferenceEngine specification and merged Prompt-03 implementation.
6. `systems/Parasara/Documentation/architecture/target-state.md` and the approved focused specifications.
7. `Documentation/AI-Prompt/Jyothishyam Architecture Consolidation.docx` — secondary historical drafting material only.

If source behavior or a lower-authority document conflicts with a higher-authority requirement, do not silently choose one. Preserve the higher-authority boundary, document the discrepancy, and stop for review if compliance would change astrology semantics, approved public behavior, a protected historical contract, or another Prompt's ownership.

This document specifies only the official Prompt-04 — AstroState API unit. Historical references to “Stage 4” describe the same architectural step and must not create a second project unit, numbering system, audit series, or work-package hierarchy.

## 2. Authorized starting state

Prompt-01, Prompt-02, and Prompt-03 are complete and merged.

The expected implementation starting point is:

```text
branch: main
local main: f3a2aeed3d45e41e0c89141b5704a5efe205c879
remote main: f3a2aeed3d45e41e0c89141b5704a5efe205c879
Prompt-02 merged main: 9509bd9faa1195e8faf06bef9e6a917ecd6ad07a
Prompt-03 merged main: f3a2aeed3d45e41e0c89141b5704a5efe205c879
```

Before implementation:

- verify the exact authorized commit against local and remote `main`;
- require a clean tracked worktree;
- resolve or explicitly exclude unrelated local documentation changes;
- preserve the four personal validation exports listed below;
- establish the current Python 3.11, Python 3.14, frontend, snapshot, deterministic-manifest, and protected-artifact baselines;
- stop rather than repairing synchronization or absorbing unrelated local files.

The four personal exports are protected and must never be modified, staged, committed, deleted, renamed, or cleaned:

```text
systems/Parasara/Documentation/Engine/MVP/Manohar-try1.json
systems/Parasara/Documentation/Engine/MVP/Manohar-try2.json
systems/Parasara/Documentation/Engine/MVP/Manohar-try3.json
systems/Parasara/Documentation/Engine/MVP/Manohar-try4.json
```

If documentation-only reconciliation advances `main` before Prompt-04 implementation is authorized, update the starting commit through explicit review. Do not silently reinterpret a different commit as this specification's baseline.

### Current manifest validation interpretation

- `tools/validate_prompt01.py` and its digest remain the preserved historical Prompt-01 gate; they are not required to pass against the later Prompt-02/03 aggregate state.
- Current Prompt-01 integrity is established through WP17, unchanged core contracts, current Prompt-02/03 validators, public outputs, snapshots, and protected artifacts.
- Prompt-04 validation composes WP17 plus the current Prompt-02, Prompt-03, and Prompt-04 gates; it never runs the raw Prompt-01 full validator against current HEAD.
- Do not modify the historical Prompt-01 validator, scenario manifest, either historical/current digest, or add a parallel Prompt-01 current-manifest framework.
- The historical WP06/WP07 capability-fingerprint documentation discrepancy remains recorded and deferred; Prompt-04 does not repair historical evidence.

## 3. Objective

Establish one stable, immutable, deterministic, read-only AstroState query and capability boundary for all downstream Parāśara evaluation consumers.

The required runtime boundary is:

```text
validated Chart
  -> mutable compatibility construction AstroState
  -> explicit normalization and enrichment producers
  -> validation and freeze boundary
  -> immutable AstroStateSnapshot
  -> factual query API
  -> predicate preparation / Yoga / Career / downstream factual consumers
```

AstroState remains factual infrastructure. It must not become a predicate engine, rule engine, inference engine, domain interpreter, or output assembler.

Prompt-04 must make facts reliably accessible without changing their astrological meaning.

## 4. Current repository state

The implementation begins from these verified facts:

### 4.1 Mutable construction model

`systems/Parasara/engine/astrostate.py` defines mutable Pydantic `AstroState` and `PlanetState` models. `AstroState` exposes mutable lists and dictionaries for planets, houses, diagnostics, enrichments, metadata, and derived state.

`systems/Parasara/engine/normalizer.py` constructs this model, mutates planet fields, attaches selected enrichments, and uses broad compatibility fallbacks. Some enrichment producers also mutate `astro.enrichments` directly.

The existing mutable object is a compatibility construction container. It is not the approved immutable downstream boundary.

### 4.2 Predicate-specific prepared state

Prompt-01 introduced immutable `PreparedAstroState` in `engine/rules/prepared_state.py`. It snapshots a bounded predicate-facing subset with seven versioned capabilities:

```text
aspects.basic_conjunction_list
aspects.whole_sign_graph
chart.lagna
dignity.exaltation_facts
planets.house_placement
planets.normalized
roles.functional
```

It provides explicit ready, empty, missing, malformed, version-mismatch, unsupported, present, absent-entity, and unavailable semantics. It has deterministic canonical serialization and digest behavior.

This contract is valuable predecessor infrastructure, but it is intentionally not the future general AstroState API. Its exact Prompt-01 logical bytes, hashes, capability meanings, and evaluator behavior are protected compatibility contracts.

### 4.3 Remaining direct consumers

Current active paths still include direct mutable traversal or consumer-time preparation:

- Career reads `astro.planets`, `astro.houses`, `astro.enrichments`, `astro.metadata`, and `astro.lagna_sign` while building its typed factual bridge.
- Yoga defensively copies mutable AstroState and may compute the aspect graph or functional roles during Yoga preparation before creating `PreparedAstroState`.
- Snapshot assembly reads mutable enrichment and diagnostic dictionaries directly.
- Some legacy helpers inspect mutable planets, houses, metadata, or enrichment dictionaries.
- The existing architecture scan prevents domain interpreters from importing `Chart`, but it does not enforce use of a stable AstroState query API.

### 4.4 Missing or partial capabilities

The repository does not currently provide all approved target facts as one validated immutable snapshot:

- Dasha is not integrated into the primary output boundary.
- Current transits are not integrated.
- Shadbala and other strengths have partial/proxy behavior and inconsistent integration.
- Varga facts exist in more than one compatibility shape.
- Whole-sign aspects and functional roles may be prepared on consumer-specific paths.
- Houses are represented as dictionaries rather than one immutable typed contract.

Prompt-04 must represent these limitations truthfully. File or function existence is not capability readiness.

## 5. Locked architectural decisions

The following decisions are binding for Prompt-04:

1. The current mutable Pydantic `AstroState` may remain temporarily as an internal construction and compatibility model.
2. A new immutable `AstroStateSnapshot` is the sole approved downstream factual evaluation view after normalization and selected enrichment production complete.
3. Snapshot construction and query execution are separate phases. Query methods never execute enrichment producers, read files, inspect the system clock, make network calls, mutate state, or repair missing data.
4. Existing enrichment producers may read and mutate the construction model while the explicit construction phase is open. Mutation ends before snapshot publication.
5. Every query returns an explicit typed outcome. `None`, an empty list, an empty mapping, and a raised exception must not ambiguously represent the same condition.
6. Invalid query input, absent entity, ready-empty capability, unavailable capability, malformed capability, version mismatch, and unsupported capability remain distinct.
7. Returned collections are immutable and deterministically ordered.
8. The snapshot owns defensive copies of all nested factual values. Mutating a source builder, source mapping, or query result cannot change the snapshot or its digest.
9. Raw Surya JSON, adapter models, and request payload dictionaries are unavailable through the snapshot and query API.
10. AstroState contains facts and capability metadata only. It contains no PredicateResult, RuleMatch, contribution, score, confidence, conflict, narrative, DomainPrediction, or public-output assembly state.
11. The existing seven Prompt-01 predicate capability definitions and versions retain their meaning. New general capabilities must not alter the legacy `PreparedAstroState` projection or its protected logical hashes.
12. `PreparedAstroState` remains a bounded predicate compatibility projection during Prompt-04. It must be derived from the new factual query boundary or an explicitly equivalent adapter, never from an independent alternate truth.
13. Prompt-04 does not require a CoreAstroState/EnrichedAstroState split. The required distinction is mutable construction versus immutable evaluation snapshot; internal class factoring may vary if that boundary is proven.
14. Public MVP-01 JSON, Career scores/confidence, Yoga results, rule matches, inference results, ordering, snapshots, and protected artifacts remain unchanged.
15. Missing Dasha, transit, full Shadbala, varga, strength, or classical-validation coverage is represented as unavailable or partial. Prompt-04 must not implement or claim those capabilities merely to make queries return values.
16. Every factual value has exactly one canonical stored owner in the snapshot. No core field, capability value, compatibility adapter, query result, or projection may carry an independently supplied competing copy of the same fact.
17. `core` owns only declared base facts and canonical entity identity. Capability records for core-owned facts may carry readiness/version metadata and deterministic projections that reference the canonical owner; they must not accept or store a second authoritative value.
18. Optional or derived facts—including house placement, dignity, strength, house lord, occupants, aspects, functional roles, and vargas—belong to their declared capabilities. They are not fields of a composite base planet or house value.
19. Every factual query result identifies exactly one primary capability ID and version. Consumers that need facts owned by several capabilities compose several query results.
20. AstroState exposes factual availability and capability inspection only. Domain completeness calculations and policies remain owned by their existing domain compatibility boundaries.

## 6. Scope

Prompt-04 includes only work required to establish and adopt the stable factual boundary:

- inventory every active AstroState producer, mutation, consumer, direct dictionary traversal, adapter seam, serializer, and relevant test;
- define immutable query-result and factual-view models;
- define the immutable `AstroStateSnapshot` contract;
- define or compose a versioned general AstroState capability catalog;
- add one pure validation/freeze boundary that does not execute producers;
- expose stable factual query methods;
- make capability/readiness inspection explicit without adding a domain completeness policy;
- preserve deterministic canonical serialization and logical digest behavior;
- adapt the existing `PreparedAstroState` projection without changing its protected contract;
- migrate active predicates and predicate preparation to the new factual source boundary while preserving PredicateResult behavior;
- migrate Yoga factual preparation away from hidden consumer-time enrichment;
- migrate Career factual preparation away from mutable nested traversal;
- migrate active snapshot/tool consumers where required to avoid bypassing the new boundary;
- preserve narrow compatibility wrappers for existing callers where necessary;
- add architecture enforcement, focused tests, deterministic evidence, and a Prompt-04 validator;
- update only the canonical AstroState/current-state/status documentation and Prompt-04 completion records required by this work.

## 7. Explicit non-goals

Do not implement, redesign, or broaden any of the following:

- new astrological calculations or corrections;
- new Dasha, transit, Shadbala, strength, aspect, varga, functional-role, dignity, or house-lord algorithms;
- scientific or SME validation of existing calculations;
- Prompt-05 typed DomainPrediction, new domains, narrative redesign, or OutputAssembler;
- Prompt-06 rule-set selection, governance, promotion, rollback, or replay infrastructure;
- Prompt-07 DSL operators or compiler expansion;
- Prompt-08 dependency graph;
- new rules, predicates, Yogas, domain weights, confidence formulas, or inference policies;
- Career or Yoga semantic changes;
- public JSON/schema redesign;
- broad error-policy redesign outside the AstroState construction/query boundary;
- persistent/distributed caching, concurrency architecture, database persistence, services, API endpoints, accounts, payments, geocoding, or frontend features;
- automatic snapshot approval;
- cleanup or absorption of unrelated local Prompt-02/03 documentation.

## 8. Required discovery report

Before modifying source, report:

- every constructor and adapter that creates `AstroState`;
- every function that mutates `AstroState`, `PlanetState`, houses, diagnostics, derived data, or enrichments;
- exact producer order on each active runtime path;
- every active direct read of AstroState fields or nested dictionaries;
- every consumer that computes or recomputes an enrichment;
- all capability shapes and competing representations for planets, houses, aspects, vargas, roles, strengths, Dasha, and transits;
- all raw Chart, adapter-model, and Surya-payload accesses after AstroState construction;
- all existing query helpers and whether they distinguish absence from unavailability;
- every serializer, cache, manifest, snapshot, digest, or trace that depends on current AstroState or `PreparedAstroState` structure;
- compatibility entry points that must keep accepting mutable `AstroState` during migration;
- source/test paths allowed to access the mutable construction model after migration;
- exact current public Career/Yoga/snapshot outputs and hashes.

Do not assume filenames from architecture documents. Use actual repository paths and present the inventory before implementation.

## 9. Required module ownership

Use these ownership boundaries unless repository discovery proves a smaller equivalent layout:

```text
systems/Parasara/engine/astrostate.py
  mutable construction compatibility models

systems/Parasara/engine/astrostate_api.py
  immutable snapshot, query outcomes, factual views, capability composition,
  canonical snapshot serialization, and read-only query methods

systems/Parasara/engine/normalizer.py and enrichment modules
  existing factual production during the open construction phase

systems/Parasara/engine/rules/prepared_state.py
  protected predicate-specific projection and compatibility adapters
```

Do not create a second package named `astrostate` alongside the existing `astrostate.py` module. Avoid circular imports. General AstroState models must not import predicates, rules, inference, interpreters, or output tooling.

## 10. Immutable snapshot contract

Create one immutable `AstroStateSnapshot` logical model. An equivalent frozen model is acceptable only if it satisfies the exact semantics below.

Required logical fields:

```text
schema_version
producer_version
normalization_version
system_scope
evaluation_context
core
capabilities
construction_issues
logical_digest
```

Requirements:

- versions use strict SemVer where the existing project does so;
- `system_scope` is explicit and remains `parasara` for this implementation;
- `evaluation_context` contains only explicit factual inputs such as an available evaluation instant and location/time context;
- `evaluation_context` is the sole owner of explicit evaluation instant and related factual evaluation context;
- `core` owns declared base chart facts, canonical entity identities, location, and source metadata required downstream; it does not duplicate `evaluation_context` or the top-level version fields;
- `capabilities` owns optional or derived factual values plus readiness/version metadata; capability metadata or deterministic projections for core-owned facts reference the one core owner and do not contain an independently supplied competing copy;
- every fact declares exactly one canonical owner; freeze rejects duplicate or contradictory legacy sources instead of selecting one by incidental order;
- query methods and `PreparedAstroState` projections read or project from that same canonical owner;
- construction issues are typed, safe, deterministic, factual, and free of machine paths, exception strings, stack traces, or sensitive raw payloads;
- `logical_digest` is derived from the canonical logical projection excluding `logical_digest` itself and is validated rather than caller-supplied arbitrary identity;
- the object contains no mutable Pydantic model, caller-owned mapping/list, raw adapter object, or lazy producer;
- object equality and digest identity ignore performance telemetry, cache hits, logs, and consumer results.

The implementation may calculate `logical_digest` through a property instead of storing it, provided repeated access is pure and byte-identical.

## 11. Immutable factual views

At minimum define immutable, JSON-safe views for facts that are currently available:

### PlanetFact

```text
planet_id
sign
degree
normalized_longitude
```

`planet_id` is the canonical identity. Do not add `canonical_id` unless repository discovery establishes a distinct, necessary, nonduplicative identity with an approved purpose. House placement, dignity, strength, roles, and varga positions are separately owned capability facts and are not embedded in `PlanetFact`.

Optional or unavailable base values must remain explicit. Do not fill missing values with invented defaults.

### HouseFact

```text
house_number
sign
```

House lord and occupants are separately owned capability facts and are not embedded in `HouseFact`. Occupant query results use canonical planet identity and deterministic catalog order unless an approved source contract requires a different preserved order.

### AspectFact

Represent the existing aspect source, target kind/identity, aspect kind, and factual configuration/version identity needed to distinguish the current basic-conjunction and whole-sign graph representations. Do not collapse those two representations or invent one as authoritative when only the other is present.

### VargaFact and VargaPositionFact

Represent only existing normalized varga facts. Preserve varga identity and deterministic planet order. Do not calculate a missing varga during query execution.

### FunctionalRoleFact and StrengthFact

Preserve source identity, version where available, exact factual value, and known partial/proxy status. A generic strength query must not make partial current values appear to be fully validated Shadbala.

Dasha and transit query methods may return unavailable outcomes throughout Prompt-04 if no integrated factual producer is present. Do not create empty typed timeline objects that imply readiness.

## 12. Query-result contract

Every factual query returns one typed immutable result, referred to here as `AstroQueryResult[T]`.

Required logical fields:

```text
capability_id
capability_version
state
entity_kind
entity_id
value_present
value
issues
```

Required states must align exactly with the existing capability semantics:

```text
present
absent_entity
capability_unavailable
malformed_capability
version_mismatch
unsupported_capability
```

Capability-level inspection separately retains:

```text
ready
ready_empty
missing
malformed
version_mismatch
unsupported
```

Reuse, relocate with compatibility re-exports, or losslessly adapt the existing `CapabilityReadiness`, `CapabilityFactState`, `CapabilityInspection`, and `CapabilityFactObservation` contracts. Do not create a competing taxonomy with different meanings.

Rules:

- `present` requires an immutable non-null value and `value_present=true`;
- `absent_entity` means the capability was ready but the requested canonical entity was absent;
- ready-empty collection queries return a present immutable empty tuple or an explicitly defined collection outcome; they must not become unavailable;
- unavailable, malformed, version-mismatch, and unsupported results carry no factual value;
- malformed query arguments are rejected at the query boundary with one documented safe typed input error or `ValueError`; they are not converted into absent entities;
- results do not contain raw exception messages or mutable source values;
- each result carries exactly one primary `capability_id` and `capability_version`; a result must not combine values owned by multiple capabilities;
- a higher-level consumer composes multiple results when it needs multiple facts rather than receiving a composite result falsely labeled as one capability.

## 13. Required query API

The immutable snapshot must expose the following factual methods or exact protocol equivalents:

```text
get_planet(planet_id)
get_planets()
get_house(house_number)
get_houses()
get_lagna()
get_planet_house(planet_id)
get_planet_dignity(planet_id)
get_house_lord(house_number)
get_occupants(house_number)
get_aspects_from(planet_id, representation)
get_aspects_to_planet(planet_id, representation)
get_aspects_to_house(house_number, representation)
get_varga(varga_id)
get_planet_in_varga(planet_id, varga_id)
get_functional_role(planet_id)
get_exaltation_facts(planet_id)
get_planet_strength(planet_id)
get_shadbala(planet_id)
get_current_dasha()
get_current_transits()
inspect_capability(capability_id, expected_version=None)
inspect_capabilities(required_capability_ids)
list_capabilities()
```

Each method maps to exactly one primary capability:

| Query | Primary capability |
|---|---|
| `get_planet`, `get_planets` | `planets.normalized` `1.0.0` |
| `get_house`, `get_houses` | `houses.normalized` and its declared version |
| `get_lagna` | `chart.lagna` `1.0.0` |
| `get_planet_house` | `planets.house_placement` `1.0.0` |
| `get_planet_dignity` | `dignity.planet` and its declared version |
| `get_house_lord` | `houses.lords` and its declared version |
| `get_occupants` | `houses.occupants` and its declared version |
| aspect queries with `basic_conjunction_list` | `aspects.basic_conjunction_list` `1.0.0` |
| aspect queries with `whole_sign_graph` | `aspects.whole_sign_graph` `1.0.0` |
| `get_varga`, `get_planet_in_varga` | `vargas.positions` and its declared version |
| `get_functional_role` | `roles.functional` `1.0.0` |
| `get_exaltation_facts` | `dignity.exaltation_facts` `1.0.0` |
| `get_planet_strength` | `strengths.planet` and its declared version |
| `get_shadbala` | `strengths.shadbala` and its declared version |
| `get_current_dasha` | `dasha.current` and its declared version |
| `get_current_transits` | `transits.current` and its declared version |
| `inspect_capability` | the explicitly requested capability ID/version; metadata only |
| `inspect_capabilities` | the explicitly requested capability IDs/versions; readiness observations only |
| `list_capabilities` | the catalog metadata capability/view; no factual values |

`representation` is required for every canonical aspect query and is a closed value selecting exactly `aspects.basic_conjunction_list` or `aspects.whole_sign_graph`. There is no implicit canonical default and no automatic fallback from one representation to the other. A legacy compatibility wrapper may retain a protected existing default only when discovery proves it is required, and that default must not be available to new canonical callers.

Requirements:

- all names and identifiers normalize through one documented canonical policy;
- house numbers are strict integers 1 through 12; Boolean, float, string, zero, and out-of-range values are invalid;
- planet results use the existing canonical planet catalog and aliases only where approved normalization already exists;
- collection ordering is explicitly defined and tested;
- `get_planets()` uses canonical planet catalog order;
- `get_houses()` uses numeric house order;
- occupants use deterministic canonical planet order;
- canonical aspect callers always select a representation explicitly; aspect ordering is derived from a stable representation-specific factual key that includes source/target/kind and preserves required source semantics;
- vargas use stable varga identity and canonical planet order;
- capability listing is sorted by capability ID;
- `inspect_capabilities` returns only deterministically ordered readiness observations and never a score, Boolean completeness judgment, confidence value, adverse weight, or domain policy result;
- no query returns a mutable reference;
- no query has side effects or caches values in caller-visible mutable state;
- query behavior is independent of call order and repetition.

Do not expose a generic `get_enrichment(name)` or raw dictionary escape hatch. Such an API would preserve the current unstable storage contract rather than solve it.

## 14. Capability catalog and factual availability

Create one general AstroState capability view by composing the existing predicate capability definitions with new definitions required by the stable API.

At minimum account for these logical capability areas:

```text
chart.metadata
chart.location
chart.lagna
planets.normalized
planets.house_placement
houses.normalized
houses.lords
houses.occupants
aspects.basic_conjunction_list
aspects.whole_sign_graph
dignity.exaltation_facts
dignity.planet
vargas.positions
roles.functional
strengths.planet
strengths.shadbala
dasha.current
transits.current
```

Exact IDs may be refined during the required discovery pass only to follow an already-established repository naming convention. Any refinement must be listed in the discovery report before source code is written.

Requirements:

- all seven existing Prompt-01 capability IDs—`planets.normalized`, `planets.house_placement`, `aspects.basic_conjunction_list`, `aspects.whole_sign_graph`, `chart.lagna`, `roles.functional`, and `dignity.exaltation_facts`—are present in or composed into the general catalog;
- those seven protected definitions retain version `1.0.0`, their current semantics, legacy manifest membership, serialization, fingerprint behavior, and hashes unless separately approved;
- the legacy predicate catalog/fingerprint and `PreparedAstroState` manifest remain protected views of the same definitions;
- adding general capabilities must not automatically add them to legacy predicate serialization;
- each definition records ID, version, content kind, empty policy, system scope, source kind, and recoverability when unavailable;
- readiness reflects the actual frozen content, not the existence of a producer function;
- partial/proxy facts carry truthful factual scope metadata;
- AstroState exposes individual or grouped capability readiness observations only; it does not derive a generic completeness score or optimistic completeness Boolean;
- AstroState does not own Career-specific completeness, domain confidence, domain scoring, adverse weighting, or domain sufficiency judgments;
- querying unavailable Dasha, transits, or Shadbala returns a typed unavailable result and does not lower or alter domain scores inside AstroState.

## 15. Construction and freeze boundary

Provide one explicit pure freeze operation, referred to here as:

```text
freeze_astrostate(
    construction_state,
    *,
    capability_supplies=None,
    versions=None,
    evaluation_context=None,
) -> AstroStateBuildOutcome
```

`AstroStateBuildOutcome` is a closed immutable success/failure union or an exact equivalent:

```text
AstroStateBuildSuccess
  snapshot
  issues

AstroStateBuildFailure
  issues
```

The variants obey these invariants:

- success contains exactly one immutable snapshot and may contain deterministically ordered nonfatal issues;
- failure contains no snapshot and at least one deterministically ordered fatal construction issue;
- no caller can construct an ambiguous outcome containing both a fatal result and a published snapshot;
- issue serialization is canonical and deterministic;
- outcomes contain no raw exception strings, mutable source values, machine paths, or raw payloads;
- the outcome wrapper does not affect snapshot identity; only factual readiness and construction issues explicitly included in the snapshot's logical projection affect its digest.

Equivalent naming is acceptable, but the behavior is locked:

- it reads and defensively copies facts already produced;
- it validates core invariants and capability shapes;
- it does not execute normalization or enrichment producers;
- it does not mutate the construction state;
- it returns `AstroStateBuildSuccess` with one snapshot or `AstroStateBuildFailure` with no snapshot;
- duplicate canonical entity identity, unsafe canonical content, invalid required core shape, or contradictory sources fail safely and deterministically;
- contradictory legacy sources for a canonically owned fact are rejected; freeze does not choose one source by insertion order, precedence guess, or compatibility convenience;
- missing optional capabilities do not make the whole snapshot fatal;
- producer exceptions are handled by the explicit producer/orchestration layer, not hidden inside query methods;
- repeated freezing of equivalent facts produces byte-identical logical output and digest.

If active runtime paths need explicit producer orchestration before freezing, introduce the smallest named orchestration function. It must declare order, call only existing producers, preserve current outputs, and remain separate from `freeze_astrostate`.

## 16. Mutation lifecycle

Enforce this lifecycle:

```text
CONSTRUCTION_OPEN
  normalization and selected factual producers may mutate the internal builder

FREEZE
  validate, copy, canonicalize, and publish AstroStateSnapshot

EVALUATION_READ_ONLY
  predicates, rules, Yoga evaluation, Career, inference adapters, and tools query only
```

No consumer may retain a reference that allows mutation of the snapshot. No producer may run after publication for the same evaluation snapshot. A separate construction run is required to produce different facts.

The implementation does not need to expose these lifecycle names as a public enum if the boundary is structurally enforced and tested.

## 17. Canonical serialization and digest

Provide one canonical logical projection and SHA-256 digest for `AstroStateSnapshot`.

The digest includes every factual input or version capable of changing query results, including where applicable:

- snapshot schema and producer version;
- normalization version;
- system scope;
- canonical core facts;
- capability ID/version/readiness/content/source identity;
- relevant enrichment/configuration versions;
- explicit evaluation instant and factual location/time context;
- deterministic construction issues that affect factual availability.

The digest excludes:

- `logical_digest` itself;
- Python object identity;
- process-local paths or addresses;
- performance duration;
- cache-hit telemetry;
- logs and diagnostics unrelated to factual availability;
- PredicateResult, RuleMatch, InferenceResult, Yoga/domain output, score, confidence, narrative, or public JSON;
- random IDs;
- incidental mapping insertion order.

Canonical bytes are produced from the remaining logical projection without a `logical_digest` field. SHA-256 is calculated over those bytes, and the resulting digest is then exposed as a derived property or validated stored value. Digest calculation must never hash a projection containing the digest being calculated.

Changing a factual value, readiness state, relevant version, or evaluation context must change the digest. Reordering semantically unordered mappings must not. Ordering that is itself part of a factual contract must remain identity-affecting and documented.

## 18. PreparedAstroState compatibility

Prompt-01's `PreparedAstroState` remains protected.

Requirements:

- derive it from `AstroStateSnapshot` queries or from one proven equivalent compatibility adapter;
- do not broaden its seven-capability manifest merely because the general snapshot has more capabilities;
- preserve exact existing schema/producer/normalization versions unless a separately versioned migration is unavoidable;
- preserve existing canonical bytes and hashes for equivalent Prompt-01 scenarios;
- preserve current predicate query helpers and `CapabilityFactObservation` behavior;
- preserve evaluator cache identity and cold/warm logical equivalence;
- prevent independent extraction logic from making the general snapshot and predicate projection disagree;
- read every prepared fact from the same canonical owner used by the corresponding general query; legacy serialization adapters may project that fact into the protected shape but must not require duplicated authoritative storage;
- add equivalence tests for every existing prepared capability.

If exact preservation is impossible, stop and report the specific protected contract conflict. Do not update historical manifests or expected hashes automatically.

## 19. Predicate migration

Predicates remain factual and continue returning only `PredicateResult`.

Prompt-04 migration requirements:

- predicate preparation obtains its source facts from the immutable snapshot boundary;
- active predicate handlers use stable prepared/general query helpers rather than mutable nested dictionaries;
- no predicate accesses mutable `AstroState`, Chart, raw Surya JSON, adapter models, domain interpreters, or enrichment producers;
- unavailable and absent facts retain current typed PredicateResult distinctions;
- parameter validation remains unchanged unless required to route through canonical AstroState identifiers;
- predicate cache keys remain isolated by the protected prepared-state digest and relevant context/version values;
- predicate results, traces, errors, ordering, logical serialization, and public compatibility remain exact.

Do not add new predicates in this Prompt.

## 20. Yoga migration

Yoga must evaluate facts from the immutable snapshot/prepared projection.

Requirements:

- remove active Yoga dependence on deep-copying the caller's mutable AstroState merely to isolate evaluation;
- do not compute aspect graphs, functional roles, or another enrichment inside Yoga query/evaluation code;
- if current Yoga requires those producers, execute them explicitly before freeze through the construction orchestration boundary;
- preserve the exact current Yoga rule source, validation, source order, RuleMatch collection order, typed batch, logical hashes, compatibility projection, and public rows;
- preserve missing-capability behavior without converting producer failure into factual nonmatch;
- retain a narrow `evaluate_yoga_rules(AstroState)` compatibility wrapper only if current callers require it; new internal code must use the immutable snapshot path;
- prevent the compatibility wrapper from becoming a second source of factual truth.

No Yoga rule or astrological condition may change.

## 21. Career migration

Career must build its typed factual bridge through stable snapshot queries.

Requirements:

- replace direct traversal of `astro.planets`, `astro.houses`, `astro.enrichments`, `astro.metadata`, and `astro.lagna_sign` in canonical preparation code;
- obtain planet placement, house 10, house lord, occupants, strength, dignity, and Lagna through separately owned explicit query results;
- derive Career's existing compatibility completeness result from explicit capability inspections/query results using the currently protected Career policy; preserve the exact result without moving that policy, score, or judgment into AstroState;
- preserve source order where current public compatibility requires it, while keeping canonical query order separately defined;
- preserve the existing typed Career batch, universal RuleMatches, shared InferenceEngine call, InferenceResult, score, confidence, components, evidence, trace IDs, narratives, and public dictionary exactly;
- keep missing data neutral/unavailable under the Prompt-03 policy; do not turn missing capability into adverse evidence;
- retain a narrow `interpret_career(AstroState)` wrapper if required by current callers, but route canonical evaluation through one frozen snapshot;
- do not introduce typed DomainPrediction or OutputAssembler.

## 22. Other consumer migration

Inspect and migrate active downstream consumers, including snapshot generation and any active confidence/diagnostic helper, when they bypass the query boundary.

Rules:

- enrichment producers may continue to access construction internals during `CONSTRUCTION_OPEN`;
- serializers/tools operating after freeze must query the snapshot or consume approved typed results;
- legacy inactive helpers may remain only when clearly identified, unreferenced by active runtime paths, and covered by architecture enforcement preventing new use;
- no active consumer after freeze uses raw `enrichments`, `derived`, mutable house dictionaries, or mutable planet collections as an alternate API;
- current `generate_snapshot.py` remains a compatibility assembler until Prompt-05; Prompt-04 changes its factual source, not its public schema or ownership.

## 23. Raw-input prohibition

After snapshot construction:

- no interpreter, predicate, rule engine, inference engine, Yoga evaluator, or output tool reads `Chart`, `Planet`, adapter internals, raw Surya JSON, frontend request dictionaries, or normalization-source dictionaries;
- the snapshot must not retain a raw payload field or arbitrary source-object escape hatch;
- source provenance uses bounded canonical metadata and digests, not embedded private birth records unless explicitly required by an approved factual contract;
- static architecture tests scan imports, annotations, attribute traversal, dictionary-key access, and known raw-payload identifiers;
- allowlists are narrow, path-specific, reviewed, and limited to adapter/normalization/construction modules.

## 24. Error and issue policy

AstroState query behavior must distinguish:

```text
invalid query input
absent entity
ready empty capability
missing capability
malformed capability
capability version mismatch
unsupported capability
fatal snapshot construction failure
unexpected programming defect
```

Expected factual availability outcomes return typed results. Invalid caller inputs use the documented input-error boundary. Unexpected programming defects remain visible in strict development and tests; do not hide them through broad exception swallowing.

Construction issues contain safe codes, rooted logical paths, optional capability/entity identity, and recoverability. They do not expose source values, stack traces, operating-system paths, or arbitrary exception text.

## 25. Compatibility requirements

Prompt-04 is an internal architecture migration. Preserve:

- Prompt-01 predicate models, prepared-state logical outputs, validator, and protected manifests;
- Prompt-02 RuleMatch model, scenario manifest, Yoga/Career compatibility, and validator;
- Prompt-03 inference models, versioned configuration, Career inference behavior, manifest, and validator;
- all existing rule files, rule metadata, weights, priorities, and order;
- MVP-01 Career JSON values, key order where protected, download behavior, and approved snapshot bytes;
- existing Yoga public projection and rule firing;
- deterministic trace identities and collection ordering;
- frontend-visible behavior;
- protected artifacts and personal export hashes.

Compatibility wrappers:

- must be named and documented;
- must convert in one direction toward the immutable boundary;
- must not allow new canonical code to depend on mutable AstroState;
- must not duplicate query or producer logic;
- must be covered by deprecation/architecture tests where appropriate;
- must list an owner and later removal stage if they remain after Prompt-04.

## 26. Required tests

### Snapshot model tests

- unambiguous `AstroStateBuildSuccess` with exactly one snapshot and optional nonfatal issues;
- unambiguous `AstroStateBuildFailure` with no snapshot and at least one fatal issue;
- deterministic build-issue ordering/serialization and rejection of ambiguous success/failure construction;
- exact field/model inventory;
- deep immutability;
- defensive copying of source objects and nested values;
- finite numeric and safe canonical-value validation;
- duplicate entity rejection;
- exactly one canonical stored owner per fact;
- deterministic rejection of contradictory duplicate/legacy sources;
- canonical serialization round trip;
- deterministic digest;
- digest version/context/fact/readiness isolation;
- digest self-exclusion from canonical bytes;
- exclusion of telemetry, domain output, and object identity.

### Query-result tests

- present fact;
- absent entity;
- ready-empty collection;
- missing capability;
- malformed capability;
- version mismatch;
- unsupported capability;
- invalid planet, house, and varga identifiers;
- immutable returned values;
- safe deterministic issues;
- exactly one primary capability ID/version per result;
- consumer composition of multiple query results without composite capability mislabeling;
- repeated and reordered query-call equivalence.

### Query-method tests

- planet lookup and canonical ordering;
- all-planets query;
- house lookup and numeric ordering;
- planet-house and planet-dignity lookup through separate capabilities;
- house-lord lookup;
- occupant lookup and ordering;
- aspects from a planet with explicit representation selection;
- aspects to a planet with explicit representation selection;
- aspects to a house with explicit representation selection;
- rejection of omitted/invalid aspect representation and no implicit cross-representation fallback;
- basic-conjunction versus whole-sign capability/representation separation;
- varga lookup and planet-in-varga lookup;
- functional-role lookup;
- current planet-strength lookup;
- honest partial/unavailable Shadbala behavior;
- unavailable Dasha behavior when no integrated producer exists;
- unavailable transit behavior when no integrated producer exists;
- capability inspection and sorted listing;
- domain-neutral grouped capability inspection with readiness observations only and no score/Boolean judgment.

### Purity and lifecycle tests

- freeze does not mutate the source construction model;
- query methods do not call enrichment producers;
- query methods perform no file, network, environment, clock, random, registry, or logging mutation;
- producer functions cannot mutate a published snapshot;
- source mutation after freeze cannot change snapshot values or digest;
- query-result mutation is impossible;
- consumer evaluation does not mutate snapshot state.

### Prepared-state compatibility tests

- exact seven-capability legacy manifest including `dignity.exaltation_facts`;
- all seven protected definitions appear in or compose into the general catalog with unchanged IDs, versions, semantics, serialization, and hashes;
- existing canonical bytes and representative hashes unchanged;
- every legacy observation agrees with the corresponding general query;
- each legacy projection and corresponding general query read the same canonical owner;
- capability versions unchanged;
- predicate cache cold/warm logical hashes unchanged;
- existing parameter, capability, predicate, condition, and WP17 tests unchanged.

### Yoga integration tests

- Yoga canonical path accepts the immutable snapshot;
- no Yoga-time enrichment production;
- no defensive copy required for canonical evaluation;
- exact RuleMatches, trace IDs, batch hashes, public projection, and order unchanged;
- compatibility wrapper behavior unchanged;
- unavailable producer facts remain typed unavailable outcomes.

### Career integration tests

- Career canonical preparation accepts the immutable snapshot;
- no direct mutable AstroState traversal in canonical preparation;
- protected Career completeness remains exact while being derived from explicit readiness/query observations outside AstroState;
- AstroState exposes no Career-specific or generic scored completeness policy;
- exact factual batch, RuleMatches, InferenceResult, score, confidence, components, evidence, narrative, and public JSON unchanged;
- representative fixtures and no-match/missing-data cases unchanged;
- shared InferenceEngine is still called exactly once.

### Architecture tests

- downstream consumers do not import or reference Chart/raw adapter models;
- predicates, Yoga, Career, and post-freeze tools do not traverse mutable AstroState fields directly;
- only allowlisted construction/enrichment modules mutate AstroState;
- AstroState API does not import predicates, RuleMatch, inference, interpreters, or output tooling;
- no generic raw-enrichment escape hatch exists;
- no query method calls a producer;
- no new scoring, confidence, narrative, rule, DSL, governance, or domain-output implementation appears;
- no Prompt-05 through Prompt-10 scope is introduced.

### Determinism and regression tests

- repeated same-process snapshot/query equivalence;
- fresh-process equivalence;
- Python 3.11/3.14 canonical hash equality;
- mapping insertion-order equivalence;
- supported hash-seed and safe working-directory equivalence;
- full backend regression in both Python lanes;
- frontend production build;
- approved snapshot exact comparison without update mode;
- protected-artifact and personal-export identity checks;
- preserved Prompt-01/02/03 validators and manifests.

Never delete or weaken valid tests, loosen tolerances without approved evidence, hide incomplete behavior behind skips, or approve changed golden outputs automatically.

## 27. Performance requirements

Measure without changing semantics:

- construction/freeze time;
- snapshot canonical serialization time;
- representative single and collection query time;
- Career and Yoga end-to-end compatibility paths;
- snapshot memory size where reasonably measurable.

Report the environment and before/after values. Avoid premature caches. If any internal cache is necessary, it must be immutable, deterministic, snapshot-owned, invisible to logical output, and unable to call producers.

No performance target authorizes retaining mutable alternate truth or weakening typed availability behavior.

## 28. Implementation sequence

Use this order:

1. Verify synchronized authorized `main`, worktree boundaries, and protected exports.
2. Establish dual-Python, frontend, snapshot, manifest, and artifact baselines.
3. Produce the Section 8 repository discovery report.
4. Lock canonical entity names, capability definitions, ordering, and compatibility seams from repository evidence.
5. Add immutable factual views, query outcomes, construction issues, and snapshot model.
6. Add the composed general capability catalog while preserving the seven-capability predicate view.
7. Add the pure freeze/validation boundary and canonical digest.
8. Add query methods with complete typed missing/unavailable behavior.
9. Prove `PreparedAstroState` projection equivalence before migrating consumers.
10. Move Yoga's required existing producer calls to explicit pre-freeze orchestration and migrate canonical Yoga evaluation.
11. Migrate Career factual preparation and preserve Prompt-03 inference/public compatibility.
12. Migrate other active post-freeze consumers and add narrow compatibility wrappers.
13. Add architecture scans and focused Prompt-04 tests.
14. Add `tools/validate_prompt04.py` by composing preserved earlier gates rather than rewriting historical validators.
15. Wire the active CI gate only after both local Python lanes pass.
16. Update only required current-state, AstroState contract, status, Prompt-04, and validation documentation.
17. Run complete validation and produce the stopping report.

Do not commit, push, open a pull request, merge, publish, begin Prompt-05, or absorb unrelated documentation unless separately authorized.

## 29. Required validation

Run and report exact Windows commands and results for:

- pre-change Python 3.11 baseline;
- pre-change Python 3.14 baseline;
- focused Prompt-04 snapshot/query tests;
- Prompt-04 architecture enforcement;
- preserved Prompt-01 validation integrity;
- preserved Prompt-02 validation integrity;
- preserved Prompt-03 validation integrity;
- `tools/validate_prompt04.py focused` in the supported lane(s);
- `tools/validate_prompt04.py full` under Python 3.11;
- `tools/validate_prompt04.py full` under Python 3.14;
- full backend regression under both lanes;
- frontend production build and relevant MVP-01 integration;
- deterministic cross-lane snapshot/query hash comparison;
- approved snapshot comparison without update mode;
- protected-artifact comparison;
- all four personal-export hash comparisons;
- worktree mutation check.

The Prompt-04 validator must use unique OS-temporary outputs, strict failure propagation, no snapshot-update mode, and the existing protection mechanisms. It must not mutate tracked files or personal exports.

Do not substitute Linux validation. Windows remains the supported backend/runtime and validation platform for this sequence.

## 30. Documentation requirements

Update only documentation required to truthfully describe the implemented Prompt-04 boundary:

- `systems/Parasara/Documentation/specifications/astrostate.md` — stable approved contract and implemented Prompt-04 boundary;
- `systems/Parasara/Documentation/architecture/current-state.md` — verified post-implementation runtime flow and remaining mutable construction compatibility;
- `systems/Parasara/Documentation/implementation/status.md` — evidence-based component status;
- `systems/Parasara/Documentation/implementation/roadmap.md` and `tasks.md` only if their live Prompt status is being corrected in the same separately approved documentation scope;
- `systems/Parasara/Documentation/Engine/Prompt-04/README.md` — detailed completion report or workspace index after implementation;
- `systems/Parasara/Documentation/prompts/prompt-04/README.md` — concise stable completion summary only after implementation and validation are complete;
- developer guidance only where query usage or compatibility ownership requires it.

Do not copy this full requirement into the stable completion summary. Do not rewrite governing DOCX files, archived documents, Prompt-01/02/03 historical requirements, or point-in-time evidence.

Documentation must distinguish:

- immutable evaluation snapshot implemented;
- mutable construction compatibility remaining;
- query capabilities ready, ready-empty, partial, missing, or unsupported;
- structural/deterministic validation completed;
- scientific/SME validation not implied;
- release/privacy/security/licensing/operations approval not implied.

## 31. Acceptance criteria

Prompt-04 is acceptable only when:

- one immutable `AstroStateSnapshot` factual boundary exists;
- every factual value has exactly one canonical stored owner, and core/capability projections cannot become competing sources of truth;
- contradictory duplicate legacy sources are rejected deterministically;
- normalization/enrichment mutation ends before snapshot publication;
- one stable typed query API covers the required factual surface;
- every factual query result maps to exactly one primary capability ID/version, and consumers compose separate results for separately owned facts;
- canonical aspect queries require explicit selection of the basic-conjunction or whole-sign-graph representation and never fall back implicitly;
- missing, empty, absent, malformed, mismatched, and unsupported states remain distinct;
- build outcomes are a closed, unambiguous immutable success/failure union with deterministic safe issues;
- query methods never compute enrichments or mutate state;
- returned facts and collections are deeply immutable and deterministically ordered;
- one canonical logical serialization and digest include all fact-affecting versions/context while excluding `logical_digest` itself from the hashed projection;
- raw Surya/Chart/adapter data is unavailable downstream;
- the general capability view truthfully represents current partial and missing capabilities;
- capability inspection is domain-neutral and exposes no completeness score, confidence, adverse weight, or Career-specific policy;
- all seven protected Prompt-01 capability definitions—including `dignity.exaltation_facts`—are composed into the general catalog without changing versions, semantics, legacy manifest, serialization, hashes, or predicate cache identity;
- existing seven-capability `PreparedAstroState` behavior and bytes remain exact and read from the same canonical fact owners as general queries;
- predicates use the protected query/projection boundary;
- Yoga no longer computes enrichment inside canonical evaluation;
- Career canonical preparation no longer traverses mutable nested AstroState structures;
- Career's protected completeness result remains unchanged and is derived outside AstroState from explicit readiness/query observations;
- active post-freeze consumers do not bypass the query API;
- public Career and Yoga output remains exact;
- RuleMatch and InferenceResult contracts remain unchanged;
- Prompt-01/02/03 validators/manifests remain intact;
- dual-Python, determinism, frontend, snapshot, protected-artifact, personal-export, and worktree gates pass;
- documentation truthfully records implemented versus unavailable capabilities;
- Prompt-05 has not started;
- no commit or publication action occurred unless separately authorized.

## 32. Required stopping report

After implementation and validation, provide:

```text
Prompt
------
Prompt-04 — AstroState API

Starting State
--------------
Branch:
Starting main commit:
Local/remote synchronized:
Tracked worktree:
Protected personal exports:

Baseline
--------
Python 3.11:
Python 3.14:
Frontend:
Approved snapshot:
Prompt-01/02/03 manifests:
Protected artifacts:

Repository Discovery
--------------------
Construction models:
Producer/mutation inventory:
Producer order:
Direct consumers before:
Raw-input accesses after construction:
Capability representations:
Compatibility entry points:

Implementation Status
---------------------
Implemented / Blocked

Shared Contracts
----------------
AstroStateSnapshot:
AstroQueryResult:
Factual view models:
Capability catalog/version:
Canonical digest:

Capability Results
------------------
Ready:
Ready empty:
Partial/proxy:
Missing:
Unsupported:

Migration Results
-----------------
PreparedAstroState preservation:
Predicate source boundary:
Yoga hidden producers before/after:
Career direct mutable accesses before/after:
Other consumer bypasses before/after:
Compatibility wrappers remaining:

Architecture Boundaries
-----------------------
Raw Surya access downstream:
Query-time producer calls:
AstroState mutation after freeze:
Predicate changes:
RuleMatch changes:
Inference changes:
Public output changes:
Prompt-05 started:

Files Added
-----------

Files Modified
--------------

Tests Added
-----------

Validation Evidence
-------------------
Focused tests:
Architecture enforcement:
Python 3.11 full result:
Python 3.14 full result:
Frontend result:
Snapshot/query deterministic hashes:
Approved snapshot:
Protected artifacts:
Personal exports:
Earlier validator integrity:
Worktree mutation check:

Public Behavior
---------------
MVP-01 Career JSON unchanged:
Career score/confidence unchanged:
Yoga output unchanged:
Approved snapshot unchanged:

Performance
-----------
Freeze:
Queries:
Career/Yoga:
Memory:

Documentation Updated
---------------------

Known Limitations
-----------------

Remaining TODO
--------------

Risks or Blockers
-----------------

Acceptance Criteria
-------------------
PASS / FAIL with failed items listed

Ready for Commit Review
-----------------------
YES / NO

Ready for Prompt-05
-------------------
YES / NO — architectural handoff only; Prompt-05 not started

Recommended Next Action
-----------------------
Review Prompt-04 implementation and validation before authorizing commit/push/PR.
```

Stop after the report. Do not commit merely because validation passes.

## 33. Explicit handoff boundary to Prompt-05

Prompt-04 ends with:

```text
immutable AstroStateSnapshot
  -> stable factual queries and typed capability outcomes
  -> preserved PredicateResult / universal RuleMatch[]
  -> preserved shared InferenceEngine / InferenceResult
  -> unchanged Career compatibility projection
```

Prompt-05 may later introduce typed DomainPrediction models, thin domain interpreters, and the serialization-only OutputAssembler.

Prompt-04 must not anticipate Prompt-05 by adding domain scores, narratives, output schemas, generic domain base classes, empty domain implementations, or public serialization logic to AstroState.

## Final instruction to the implementation agent

Implement only Prompt-04 — AstroState API.

Begin from explicitly synchronized and approved `main`. Inspect the real construction lifecycle and every active consumer before choosing files. Preserve the existing mutable model only as a bounded construction/compatibility seam, publish one immutable post-enrichment factual snapshot, expose explicit deterministic queries, and migrate active consumers without changing astrology or public behavior.

Preserve Prompt-01 `PreparedAstroState`, Prompt-02 RuleMatch, Prompt-03 InferenceEngine, validators, manifests, snapshots, protected artifacts, and the four personal exports. Represent missing capabilities honestly. Produce the required report and stop before commit, push, PR, merge, Prompt-05, or unrelated cleanup.
