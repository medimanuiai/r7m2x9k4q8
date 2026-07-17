# Parāśara Engine Implementation Status

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-17

## Status rules

- `IMPLEMENTED`: active source satisfies the stated current contract; scientific or production validation may still be a separate gate.
- `PARTIAL`: usable implementation exists but does not satisfy the approved contract or validation gate.
- `MISSING`: no active implementation of the approved component was found.
- `UNVERIFIED`: implementation exists, but correctness or acceptance evidence was not established during documentation review.

Prompt-01 validation was reproduced on 2026-07-17 in Python 3.11.9 and 3.14.6.
This does not certify scientific, release, privacy, security, licensing, or
operational readiness.

## Component matrix

| Component | Status | Current evidence | Principal gap |
|---|---|---|---|
| Surya input adapter | PARTIAL | `systems/Parasara/engine/adapter/surya_adapter.py`, `systems/Parasara/schemas/surya_input.schema.json`, adapter tests | `load` validates input, but `load_many` does not consistently apply the same schema-validation boundary |
| Chart models | PARTIAL | `systems/Parasara/engine/models.py` | Mutable defaults and incomplete target contracts remain |
| Normalization | PARTIAL | `systems/Parasara/engine/normalizer.py` | Broad exception fallbacks, mutation, and no formal dependency-ordered pipeline contract |
| AstroState | PARTIAL | mutable compatibility state plus `engine/rules/prepared_state.py` | Prompt-01 has immutable prepared facts/digest; universal query API and construction redesign remain |
| Derived state | PARTIAL | `systems/Parasara/engine/derived/` | Builder can return an unvalidated dictionary and is not the sole downstream access boundary |
| Vargas | PARTIAL | `systems/Parasara/engine/enrichments/varga.py` and related tests | Classical coverage and validation vary by varga |
| Aspect enrichment | PARTIAL | `systems/Parasara/engine/enrichments/aspects.py` and related tests | Capability/version contract and full graph policy are incomplete |
| Functional roles | PARTIAL | `systems/Parasara/engine/enrichments/functional_roles.py`, YAML tables, and tests | Working-directory-dependent discovery, SME authority, and complete validation are unresolved |
| Planet strengths | PARTIAL | `systems/Parasara/engine/enrichments/planet_strengths.py`, `shadbala.py`, and tests | Contains approximations/proxies and working-directory-dependent tables; classical validation incomplete |
| Vimshottari Dasha | PARTIAL | `systems/Parasara/engine/dasha/vimshottari.py`, unit tests, and golden tests | Not integrated into primary output; wall-clock fallback and Moon-longitude input require correction/verification |
| PredicateResult | IMPLEMENTED | `engine/rules/models.py`, `canonical.py`, WP02/WP03/WP17 tests | Scientific/public/release validation remains separate |
| Predicate registry | IMPLEMENTED | `engine/rules/registry.py`, `canonical_predicates.py`, isolation tests | Future multi-library/version selection remains |
| Predicate parameters/capabilities | IMPLEMENTED | `parameters.py`, `capabilities.py`, focused/WP17 tests | Broader non-predicate query architecture remains |
| Predicate evaluator/cache | IMPLEMENTED | `evaluator.py`, `prepared_state.py`, cache/determinism tests | Persistent/distributed and concurrent caching are deferred |
| Generic condition evaluator | IMPLEMENTED | `conditions.py`, typed condition/definition/WP17 tests | Full compiler/DSL/dependency graph is deferred |
| Rule loader | PARTIAL | `loader.py`, `yoga_loader.py`, active definition validation | Active formats/order validated; universal compiler/governance/version selection absent |
| RuleMatch | PARTIAL | `systems/Parasara/engine/models.py`, M1 runtime | Runtime serializes the model to dictionaries; universal contract and PredicateResult preservation missing |
| Yoga evaluation | IMPLEMENTED | typed batch plus `project_yoga_compatibility`, Yoga/WP17 tests | Compatibility projection/state attachment remain until universal RuleMatch |
| Career interpreter | PARTIAL | typed factual bridge and compatibility projection in `career.py`/`career_models.py` | Preserved local scoring/confidence/public dictionary await shared inference/typed domains |
| Other domain interpreters | MISSING | Placeholder Wealth output in `systems/Parasara/tools/generate_snapshot.py` | Typed Wealth, Marriage, Children, Health, and Safety interpreters absent |
| Shared InferenceEngine | MISSING | No active module found | Required aggregation, normalization, conflicts, and confidence service absent |
| Typed domain output | MISSING | Current interpreters return dictionaries | Approved DomainPrediction boundary absent |
| OutputAssembler | MISSING | `systems/Parasara/tools/generate_snapshot.py` assembles dictionaries directly | Dedicated schema-validating serialization-only layer absent |
| Rule-set selection | PARTIAL | Hardcoded `v1` paths in runtime/loaders and output metadata | No explicit EngineConfig, strict selection, or cache-safe version propagation |
| Rule governance | MISSING | Metadata fragments and proposed policy only | No promotion, rollback, approval enforcement, or audit service |
| Prompt-01 validation/CI | IMPLEMENTED | `tools/validate_prompt01.py`, `tests/wp19`, CI workflow, WP19 | External required-check setting and release/compliance gates are separate |
| Snapshot/testing harness | PARTIAL | Prompt-01 gate, snapshots, testing framework | Prompt-01 compatibility validated; scientific/production acceptance remains |
| Public engine API | MISSING | Tool-level entry points only | Versioned service/facade contract absent |
| Production operations | MISSING | Documentation checklist only | Monitoring, deployment, retention automation, and operational evidence absent |

## Active architectural blockers

1. Universal RuleMatch is the next separately authorized architecture stage.
2. Shared inference depends on universal RuleMatch.
3. Domain thinning/public output stabilization depend on shared inference and
   typed outputs.
4. Release/privacy/security/licensing/publication work remains separate owner
   work.

## Validation status

The WP19 dual-lane gate passed 2026-07-17 with identical ordered collection,
determinism manifest, lint inventory, and approved snapshot. Scientific
correctness, SME approval, public schema approval, privacy/security/licensing,
and production operations remain separate gates.

Remaining non-Prompt risks include Dasha wall-clock fallback, mutable
pre-evaluation compatibility state, some legacy discovery/fallback paths, and
incomplete public/output and release architecture.

## Superseded status source

The former status document is preserved at `../archive/legacy-implementation-status.md`. Its completion labels are not canonical when they conflict with this evidence-based matrix.
