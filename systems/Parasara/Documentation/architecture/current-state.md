# Parāśara Engine Current State

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-08-21

## Scope

This document describes verified implementation behavior. It is not the target architecture and does not grant architectural approval to prototype behavior.

## Runtime components

### Adapter and input models

`systems/Parasara/engine/adapter/surya_adapter.py` validates Surya-format JSON and constructs the Pydantic models defined in `systems/Parasara/engine/models.py`.

The active model surface is split across:

- `systems/Parasara/engine/models.py` for adapter-facing `Chart` models;
- `systems/Parasara/engine/astrostate.py` for `AstroState` and `PlanetState`;
- `systems/Parasara/engine/astrostate_api.py` for the immutable
  `AstroStateSnapshot`, capability catalog, freeze boundary, and factual queries;
- `systems/Parasara/engine/derived/models.py` for typed derived summaries;
- `systems/Parasara/engine/rules/rule_match.py` for the immutable universal
  `RuleMatch` evaluation result;
- `systems/Parasara/engine/domain/models.py` for immutable domain, Yoga
  diagnostic, Dasha, and transit output contracts;
- `systems/Parasara/engine/output_assembler.py` for typed public serialization.

Adapter and construction models remain mutable. Evaluation publishes one
deeply immutable snapshot; PreparedAstroState, RuleMatch, InferenceResult,
DomainPrediction, YogaDiagnostic, and their nested logical values are
immutable. Yoga and Career retain only explicit one-way compatibility
projections for existing public output.
Direct construction and `dataclasses.replace` cannot bypass snapshot-model
validation or retain caller-owned mutable nested values. Capability records
are catalog/version/core-path checked, and snapshot publication reconciles
core-backed readiness with the referenced `AstroCore` fact.

### Normalization and AstroState construction

`systems/Parasara/engine/normalizer.py` converts a `Chart` into `AstroState`. It currently:

- normalizes common planet naming and longitude values;
- separates Lagna/Ascendant from planet nodes;
- constructs lagna-relative whole-sign houses when houses are absent;
- attaches canonical IDs and varga summaries;
- invokes selected strength, house, aspect, and derived-state builders.

The current `AstroState` is a mutable Pydantic construction container.
Enrichment code may update it only before `freeze_astrostate` publishes an
immutable `AstroStateSnapshot`; evaluation consumers query that snapshot.

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

`rules/snapshot_adapter.py` projects canonical snapshot owners into the exact
seven-capability `PreparedAstroState` view. The legacy
`prepare_predicate_state` entry remains for compatibility. Its digest
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

Yoga explicitly runs its existing required whole-sign-aspect and
functional-role producers in a separate construction run, freezes once, and
evaluates from that snapshot. It retains a typed internal batch from one
prepared state and one evaluator,
with one universal RuleMatch per record. Prompt-05 maps each record to a
`YogaDiagnostic` that retains the authoritative RuleMatch, source order, and
compatibility evidence, then uses a named one-way compatibility projection to
preserve existing public keys, firing, and row order. Dormant tuple helpers were retired. The generic
rule loader remains a compatibility registry for current rule records; WP17
enforces deterministic Yoga permutations and both loader trigger orders.

### Domain interpretation

Career is the only substantive domain interpreter. Its factual preparation
composes typed snapshot queries for placement, dignity, strength, Lagna,
house lord, and occupants. Evaluation uses a typed Career-specific batch,
and universal RuleMatch values. Career supplies explicit completeness and a
RuleMatch-backed compatibility baseline to the one shared InferenceEngine.
Prompt-05 maps that one InferenceResult to a closed typed build outcome and
one immutable `DomainPrediction`. Components, indicators, narrative, issues,
versions, and traces validate against the retained inference and parent Career
evaluation batch. The sealed inference-owned compatibility projection supplies
base score and total contribution; `OutputAssembler` only selects and
serializes those values. The compatibility projection preserves candidate
order, components, indicators, narrative, and the public dictionary, while
final score, confidence, agreement, completeness, contributions, and conflicts
come only from InferenceResult. Canonical Career evaluation keeps
expected factual unavailability typed and allows unexpected programming
defects to propagate to strict callers and tests.

Wealth, Marriage, Children, Health, and Safety have shared `DomainId` and model
readiness but no interpreter. The old Wealth row exists only in the outward
compatibility profile and is not a typed evaluated domain.

### Timing and output

A Vimshottari implementation exists but is not integrated into the primary
snapshot output, so `dasha.current` remains unavailable. Snapshot generation
is orchestrated by `systems/Parasara/tools/generate_snapshot.py`. Prompt-05
publishes immutable availability-bearing Dasha/transit output contracts but
does not call or repair a calculator; the primary path constructs truthful
unavailable values.

There is one dedicated shared `InferenceEngine` and one serialization-only
`OutputAssembler`. The assembler accepts only typed metadata, diagnostics,
Yoga diagnostics, domain predictions, timing contracts, explainability, and
typed issues. It has no adapter, AstroState, predicate, rule-engine, inference,
interpreter, or calculator dependency.

Prompt-02/WP17 Yoga baseline contradiction reconciled; Prompt-05 R4 validation
completed; independent Final R4 Review pending. RuleMatch remains the sole
Yoga rule-truth, status, evidence, and trace authority. The corrected current
Prompt-02/WP17 manifest is `06330b43...b3017`; the superseded `75b65d2c...dfaf7`
hash remains historical evidence. The exact lineage is recorded in
`Engine/Prompt-02/Reports/Prompt-02-WP17-Yoga-Contract-Reconciliation.md` and
`Engine/Prompt-05/Reports/Prompt-05-Remediation-R4.md`. Prompt-05 remains
unaccepted and commit authorization remains separate.

The `parasara_snapshot_v1` compatibility profile emits the unchanged
substantive Career dictionary, compatibility-only Wealth dictionary, empty
Dasha/transit arrays, and skeletal explainability sections. The approved
snapshot remains 4,041 bytes with SHA-256
`da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`.

### Error and fallback behavior

Predicate and condition boundaries convert expected failures to bounded typed
errors/statuses and re-raise programming defects in strict mode. Broad
compatibility fallbacks remain elsewhere in normalization, non-Prompt rule
loading, timing, and other legacy enrichments.

### Determinism risks

Prompt-01 logical predicate/condition, Prompt-02 RuleMatch, Prompt-03
InferenceResult, Prompt-04 snapshot/query, and Prompt-05 domain/Yoga/timing/
assembly, Career, tooling, serialization,
loader-order, registry, and cache scenarios are deterministic across the
supported Python lanes, hash seeds, safe working directories, and repetitions.
Remaining non-Prompt risks include Vimshottari wall-clock fallback, mutable
construction/enrichment stages, some working-directory-dependent legacy table
discovery, and mutable compatibility rule registries.

## Current data flows

Primary snapshot flow:

```text
Surya JSON
  -> SuryaAdapter
  -> Chart
  -> chart_to_astrostate
  -> mutable enriched AstroState
  -> freeze_astrostate
  -> immutable AstroStateSnapshot and typed factual queries
  -> prepared Career factual boundary
  -> typed Career evaluation batch
  -> universal RuleMatch collection
  -> shared InferenceEngine and immutable InferenceResult
  -> closed Career build outcome and immutable DomainPrediction
  -> typed OutputAssemblyInput with unavailable Dasha/transit contracts
  -> OutputAssembler / parasara_snapshot_v1
  -> unchanged snapshot dictionary/JSON
```

Yoga flow:

```text
AstroState compatibility input
  -> explicit Yoga producer construction
  -> immutable AstroStateSnapshot
  -> immutable PreparedAstroState
  -> PredicateEvaluator and typed ConditionResult
  -> typed Yoga batch
  -> universal RuleMatch collection
  -> RuleMatch-backed YogaDiagnostic collection
  -> one-way compatibility projection
```

## Verified architectural gaps

- Mutable construction compatibility and broad legacy producer fallbacks remain
  before the freeze boundary.
- No fully wired engine/rule-set version selection.
- No complete DSL compiler or dependency graph.
- No production rule-governance workflow.
- No persistent/distributed cache or broad concurrency architecture.
- No deterministic error/fallback policy shared across non-Prompt layers.
- No typed Wealth, Marriage, Children, Health, or Safety interpreter.
- No integrated Dasha or transit producer in the primary pipeline.

## Interpretation rule

Simplified astrological calculations are current behavior. Documentation cleanup and Prompt-01 contract work must not silently redesign those calculations.
