# AstroState Contract

Status: APPROVED  
Authority: Master Architecture Specification  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-08-21

## Contract

After adapter validation and normalization, AstroState is the sole downstream representation of chart facts. Downstream engines must not read raw Surya JSON or adapter internals.

AstroState must provide normalized planets, houses, Lagna, vargas, relationships, enrichments, metadata, evaluation context, versions, and completeness/capability information needed by factual consumers.

The approved boundary may be implemented as separate core and enriched types or as one controlled builder that freezes the completed evaluation snapshot. In either design, construction and enrichment mutation must finish before predicate or rule evaluation begins.

## Required logical sections

AstroState must expose, directly or through stable typed sections:

- source and normalization metadata;
- Lagna and normalized planet facts;
- houses and occupants;
- varga positions;
- factual relationships such as aspects;
- reusable enrichment outputs such as functional roles and strengths;
- Dasha and transit capabilities when available;
- engine, normalization, enrichment, and configuration versions relevant to facts;
- evaluation instant and applicable location/time context;
- completeness and capability metadata;
- a deterministic logical digest suitable for cache and replay identity.

Raw Surya payloads and adapter-specific structures must not be retained as alternate downstream truth.

## Required properties

- Immutable during predicate, rule, inference, and interpretation evaluation.
- Deterministic ordering and serialization.
- Stable factual query API.
- Explicit missing-data and missing-capability behavior.
- No domain scoring, prediction, or narrative logic.
- No hidden enrichment recomputation from query methods.
- No domain weights, prediction scores, confidence, narratives, or rule matches.
- Defensive ownership of nested collections so callers cannot mutate stored facts indirectly.
- JSON-safe canonical values for hashing, traces, snapshots, and replay.

## Query API

The stable factual API must cover, as capabilities become available:

- planet and house lookup;
- house-lord and occupant lookup;
- aspects from and to planets or houses;
- varga and varga-position lookup;
- functional-role and strength lookup;
- current Dasha and transit context;
- capability and completeness inspection.

Queries must return deterministically ordered collections. They must not silently calculate missing enrichments. Missing identifiers and unavailable capabilities must use explicit typed behavior rather than ambiguous empty values where the distinction matters.

## Identity and versions

The AstroState logical digest must be derived from canonical factual content and every version or evaluation input that can change those facts. It must not use Python object identity, process-local addresses, random values, or incidental serialization order.

Changing normalization, relevant enrichment configuration, evaluation instant, system scope, or another factual input must produce an isolated state/cache identity.

## Construction and validation

- Adapter validation precedes AstroState construction.
- Normalization and enrichment dependencies execute in a declared order.
- Required factual invariants are validated before the state is frozen.
- Partial states identify missing capabilities and completeness explicitly.
- Broad exception fallbacks must not make failed enrichment indistinguishable from an evaluated empty result.
- Construction diagnostics remain factual and must not become domain interpretation.

## Implemented Prompt-04 boundary

`engine/astrostate.py` remains the bounded mutable construction and legacy
entry model. `engine/astrostate_api.py` implements the post-enrichment factual
boundary:

```text
mutable AstroState construction
  -> explicit existing producers
  -> freeze_astrostate
  -> immutable AstroStateSnapshot
  -> typed factual queries
```

The snapshot contains versioned core facts, a composed capability catalog,
safe deterministic construction issues, explicit evaluation context, and a
SHA-256 logical digest. Canonical digest bytes exclude `logical_digest`
itself, telemetry, cache state, rule/domain results, public output, random
identity, and process-local data. Duplicate entities, unsafe core content, and
contradictory legacy owners fail construction; optional missing capabilities
remain queryable as typed unavailable states.

Every public immutable model validates its invariants in direct construction
and defensively freezes nested mappings and collections. Caller mutation and
`dataclasses.replace` therefore cannot bypass catalog versions, core paths,
readiness/content/empty-state rules, factual presence flags, core-backed
readiness reconciliation, published equality, or digest identity. Core-backed
capability supplies are rejected rather than stored as a second fact owner.
Evaluation context is bounded to the implemented factual `instant`; telemetry,
cache, logs, scores, confidence, domain results, raw requests, unknown keys,
and mutable nested values are rejected.

Query results reuse the established capability readiness/fact-state taxonomy.
Planet and house collections use canonical ordering. Every aspect query
requires an explicit `basic_conjunction_list` or `whole_sign_graph`
representation. No query executes a producer or exposes a generic enrichment
dictionary. Whole-sign facts preserve their target sign and house queries map
that sign only through the canonical houses owned by the snapshot. Every
published aspect source and planet target belongs to the snapshot's canonical
planet set, and a whole-sign planet target must agree with its canonical sign.
Missing entities remain distinct from present-empty aspect collections.
Unsafe supplied aspect facts fail construction with a deterministic fatal issue
before a snapshot is published; they are never discarded or converted into a
malformed or ready-empty capability. A typed nonfatal `malformed` capability is
reserved for bounded availability or producer outcomes that contain no invalid
supplied factual content.

The general catalog composes the protected seven Prompt-01 definitions without
changing their versions or legacy manifest. `rules/snapshot_adapter.py`
projects the same canonical owners into byte-identical `PreparedAstroState`
values. Yoga, Career, confidence, and snapshot generation evaluate/query the
immutable boundary; narrow mutable entry wrappers remain for compatibility and
are owned for removal or further thinning in later approved stages.
Canonical Career batch evaluation catches no arbitrary programming exception:
unexpected defects propagate, while expected factual absence continues through
the existing typed status/error contracts.

Current Dasha and transit capabilities are unavailable because no integrated
producer supplies them. Existing Shadbala payloads are exposed only with the
truthful `legacy_partial_proxy` scope. Structural and deterministic validation
does not imply scientific/SME, release, privacy, security, licensing, or
operations approval.
