# Parāśara Engine Current State

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-12

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

`systems/Parasara/engine/rules/engine.py` contains:

- a global predicate registry;
- a registration decorator;
- an initial frozen `PredicateResult` dataclass;
- an in-memory predicate cache;
- predicate-leaf and `AND`/`OR` condition evaluation.

Registered predicate handlers live in `systems/Parasara/engine/rules/predicates.py`. Registration currently depends on importing that module. The registry stores handlers without the complete Prompt-01 metadata contract.

The existing `PredicateResult` is only shallowly immutable because its collections remain mutable. It lacks several approved Prompt-01 fields and retains tuple-return compatibility.

Predicate registration uppercases lookup IDs, stores handlers in a global mutable dictionary, and silently replaces an existing entry with the same normalized ID. Registration does not currently validate blank IDs, callable handlers, versions, schemas, capabilities, or alias metadata. Test-time registration uses the same global registry and relies on manual cleanup.

The predicate cache is also global. Its key uses `id(astro)`, normalized predicate name, and serialized parameters; it does not include an AstroState digest, predicate version, enrichment/configuration versions, or evaluation context. Mutating an AstroState after caching can therefore leave a cached result associated with changed state.

### Rules and yoga evaluation

Two related runtime paths exist:

1. The generic predicate/condition evaluator used by the rule-driven Yoga engine.
2. The M1 runtime in `systems/Parasara/engine/rules/runtime.py`, which evaluates hardcoded rule types and applies prototype scores.

The YAML loaders use a global rule registry and best-effort loading. Yoga evaluation returns custom dictionaries and generates random UUID trace identifiers.

The predicate registry and rule registry are separate global mechanisms. The rule loader silently replaces duplicate rule IDs and skips parse/validation failures through best-effort exception handling. Registry iteration is not governed by an explicit canonical ordering contract.

The M1 rule runtime imports rule and predicate instrumentation from `tests.testing_framework`. Active engine code therefore depends on a test package for coverage instrumentation.

### Domain interpretation

Career is the only substantive domain interpreter. It currently selects candidate rule dictionaries, evaluates M1 rules, aggregates contributions, computes confidence, creates narrative text, and returns an untyped dictionary.

Other domain outputs are absent or placeholders in the snapshot assembler.

### Timing and output

A Vimshottari implementation exists but is not integrated into the primary snapshot output. Snapshot generation is performed by `systems/Parasara/tools/generate_snapshot.py`, which directly assembles public dictionaries.

There is no dedicated shared `InferenceEngine` or serialization-only `OutputAssembler` in the active runtime.

The snapshot assembler currently emits a substantive Career dictionary, a placeholder Wealth dictionary, empty Dasha and transit collections, and skeletal explainability policy sections.

### Error and fallback behavior

Broad `except Exception` handling appears in normalization, derived-state construction, enrichments, rule loading, runtime evaluation, Yoga evaluation, and Career interpretation. Depending on the path, failures may be skipped, converted to fallback dictionaries, or replaced with partial enrichment state. This preserves prototype execution but can obscure invalid configuration, missing capabilities, and programming defects.

### Determinism risks

Known current risks include:

- Yoga trace IDs generated with `uuid.uuid4()`;
- Vimshottari fallback to `datetime.utcnow()` when birth time is absent or invalid;
- predicate cache identity based on the in-process AstroState object ID;
- mutable global predicate, rule, and cache dictionaries;
- no explicit canonical registry-enumeration order;
- working-directory-dependent table and rule discovery;
- mutation of AstroState after construction and during enrichment.

## Current data flows

Primary snapshot flow:

```text
Surya JSON
  -> SuryaAdapter
  -> Chart
  -> chart_to_astrostate
  -> mutable enriched AstroState
  -> Career interpreter
  -> M1 rule runtime and local scoring/confidence
  -> snapshot dictionary/JSON
```

Yoga flow:

```text
AstroState
  -> enrichment updates
  -> YAML yoga loader
  -> generic condition evaluator
  -> PredicateResult
  -> custom yoga-match dictionaries
```

## Verified architectural gaps

- No shared Inference Engine.
- No universal active-runtime `RuleMatch` boundary.
- No typed domain-output boundary.
- No dedicated Output Assembler.
- No stable read-only AstroState query API.
- No complete predicate metadata registry.
- No digest- and version-safe predicate cache.
- No fully wired engine/rule-set version selection.
- No complete DSL compiler or dependency graph.
- No production rule-governance workflow.
- No explicit separation between production engine dependencies and test instrumentation.
- No deterministic error/fallback policy shared across layers.

## Interpretation rule

Simplified astrological calculations are current behavior. Documentation cleanup and Prompt-01 contract work must not silently redesign those calculations.
