# AstroState Contract

Status: APPROVED  
Authority: Master Architecture Specification  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-07-17

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

## Implemented Prompt-01 factual boundary

The adapter/normalizer-facing `AstroState` remains the mutable compatibility
construction model. Prompt-01 adds an explicit `prepare_predicate_state`
boundary that copies supported facts into an immutable `PreparedAstroState`
with capability readiness, producer/schema versions, defensive freezing, and
a deterministic digest.

The digest includes canonical predicate-relevant facts, readiness/content,
relevant versions, and explicit factual context. It excludes Yoga/domain
outputs, cache telemetry, performance timing, random IDs, and caller-owned
mutable identity. Predicate handlers receive only this prepared snapshot.

This is not the future general AstroState query API. Other enrichments and
domains may still use the mutable compatibility AstroState, and the broader
construction/query redesign remains deferred.
