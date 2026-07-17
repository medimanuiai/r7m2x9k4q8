# Parāśara Engine Current State

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-17

## Scope

This document describes verified implementation behavior. It is not the target architecture and does not grant architectural approval to prototype behavior.

## Runtime components

### Adapter and input models

`systems/Parasara/engine/adapter/surya_adapter.py` validates Surya-format JSON and constructs the Pydantic models defined in `systems/Parasara/engine/models.py`.

The active model surface is split across:

- `systems/Parasara/engine/models.py` for adapter-facing `Chart` models and the current Pydantic `RuleMatch`;
- `systems/Parasara/engine/astrostate.py` for `AstroState` and `PlanetState`;
- `systems/Parasara/engine/derived/models.py` for typed derived summaries.

These are not one immutable end-to-end model boundary. Several models expose mutable dictionaries/lists or use mutable collection defaults. The existing `RuleMatch` is converted back to a dictionary by the M1 runtime, while Yoga and Career retain separate dictionary-shaped match/output contracts.

### Normalization and AstroState construction

`systems/Parasara/engine/normalizer.py` converts a `Chart` into `AstroState`. It currently:

- normalizes common planet naming and longitude values;
- separates Lagna/Ascendant from planet nodes;
- constructs lagna-relative whole-sign houses when houses are absent;
- attaches canonical IDs and varga summaries;
- invokes selected strength, house, aspect, and derived-state builders.

The current `AstroState` is a mutable Pydantic container with nested mutable dictionaries and lists. Enrichment code may update it after construction.

### Enrichments

The engine contains modules for aspects, functional roles, planet strengths, shadbala, vargas, yogas, precision, canonical IDs, and derived summaries. Their maturity and validation levels differ. Some calculations remain M1 approximations or proxies.

Some table and rule discovery depends on the process working directory. In particular, functional-role tables, shadbala tables, and M1 rules use `os.getcwd()`-relative paths in active code. Running from a different directory can therefore change which data is discovered.

Two rule/reference roots are present:

- `rules/parashara/`;
- `systems/Parasara/rules/parashara/`.

Their responsibilities differ in practice, but ownership is not yet expressed through a single validated loading contract.

### Predicate evaluation

Prompt-01 is implemented in `systems/Parasara/engine/rules/`. The immutable
contracts are `PredicateStatus`, `PredicateError`, `PredicateTraceStep`,
`PredicateResult`, typed condition children, and `ConditionResult`. The exact
duration field is `evaluation_time_ms`. Logical serialization excludes
`cache_hit` and duration telemetry; full serialization includes them.

`PredicateDefinition` carries validated ID, SemVer version, description,
parameter schema, capabilities, cache/determinism/cost/system metadata,
deprecation data, and explicit aliases. Canonical bootstrap is deterministic,
the production registry freezes after bootstrap, enumeration is ordered, and
tests use isolated registries. `ASPECT` is an explicit alias for
`ASPECT_EXISTS`.

Parameters are normalized by strict declared schemas. Unknown keys, material
coercion, Boolean houses, out-of-range houses, and unknown planet identifiers
are rejected. The capability catalog distinguishes unsupported, missing,
empty, malformed, and absent-entity facts from factual false.

`prepare_predicate_state` creates a defensively frozen
`PreparedAstroState` from the mutable compatibility AstroState. Its digest
covers canonical predicate facts, readiness/content, producer/schema versions,
and relevant explicit context; Yoga/domain output, telemetry, performance
timing, random identity, and caller-owned mutable references are excluded.

`PredicateEvaluator` owns a bounded per-instance cache. Keys include prepared
state digest, canonical predicate ID/version, canonical parameters, relevant
context, and capability versions. Only allowed factual results are cached;
retrieval derives `cache_hit=True` without changing logical bytes.

### Rules and yoga evaluation

The active Prompt-01 runtime uses the generic predicate/condition evaluator.
The former M1 runtime and raw predicate adapter modules were retired in WP16.

Active condition evaluation supports typed leaves and `AND`, `OR`, and `NOT`.
It validates the active format, evaluates left to right, short-circuits
deterministically, preserves evaluated typed children, and represents
unevaluated children explicitly as skipped.

Yoga retains a typed internal batch from one prepared state and one evaluator,
then uses a named one-way compatibility projection to preserve existing public
keys, firing, and row order. Dormant tuple helpers were retired. The generic
rule loader remains a compatibility registry for current rule records; WP17
enforces deterministic Yoga permutations and both loader trigger orders.

### Domain interpretation

Career is the only substantive domain interpreter. Its factual checks now use
a typed Career-specific prepared/evaluation batch and canonical occupancy
facts. A compatibility projection preserves the prior candidate order,
denominator, scoring, confidence, components, indicators, narrative, and
public dictionary. Career still owns domain inference and is not the future
universal inference layer.

Other domain outputs are absent or placeholders in the snapshot assembler.

### Timing and output

A Vimshottari implementation exists but is not integrated into the primary snapshot output. Snapshot generation is performed by `systems/Parasara/tools/generate_snapshot.py`, which directly assembles public dictionaries.

There is no dedicated shared `InferenceEngine` or serialization-only `OutputAssembler` in the active runtime.

The snapshot assembler currently emits a substantive Career dictionary, a placeholder Wealth dictionary, empty Dasha and transit collections, and skeletal explainability policy sections.

### Error and fallback behavior

Predicate and condition boundaries convert expected failures to bounded typed
errors/statuses and re-raise programming defects in strict mode. Broad
compatibility fallbacks remain elsewhere in normalization, non-Prompt rule
loading, timing, and other legacy enrichments.

### Determinism risks

Prompt-01 logical predicate, condition, Yoga, Career, tooling, serialization,
loader-order, registry, and cache scenarios are deterministic across the
supported Python lanes, hash seeds, safe working directories, and repetitions.
Remaining non-Prompt risks include Vimshottari wall-clock fallback, mutable
preparation/enrichment stages, some working-directory-dependent legacy table
discovery, and mutable compatibility rule registries.

## Current data flows

Primary snapshot flow:

```text
Surya JSON
  -> SuryaAdapter
  -> Chart
  -> chart_to_astrostate
  -> mutable enriched AstroState
  -> prepared Career factual boundary
  -> typed Career evaluation batch
  -> preserved Career scoring/confidence and public projection
  -> snapshot dictionary/JSON
```

Yoga flow:

```text
AstroState
  -> explicit Yoga preparation
  -> immutable PreparedAstroState
  -> PredicateEvaluator and typed ConditionResult
  -> typed Yoga batch
  -> one-way compatibility projection
```

## Verified architectural gaps

- No stable read-only AstroState query API.
- No universal RuleMatch boundary.
- No shared InferenceEngine.
- No typed universal DomainPrediction boundary.
- No OutputAssembler.
- No fully wired engine/rule-set version selection.
- No complete DSL compiler or dependency graph.
- No production rule-governance workflow.
- No persistent/distributed cache or broad concurrency architecture.
- No deterministic error/fallback policy shared across non-Prompt layers.

## Interpretation rule

Simplified astrological calculations are current behavior. Documentation cleanup and Prompt-01 contract work must not silently redesign those calculations.
