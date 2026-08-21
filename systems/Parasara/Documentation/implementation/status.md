# Parāśara Engine Implementation Status

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-08-21

## Status rules

- `IMPLEMENTED`: active source satisfies the stated current contract; scientific or production validation may still be a separate gate.
- `PARTIAL`: usable implementation exists but does not satisfy the approved contract or validation gate.
- `MISSING`: no active implementation of the approved component was found.
- `UNVERIFIED`: implementation exists, but correctness or acceptance evidence was not established during documentation review.

Prompt-01 validation was reproduced on Windows on 2026-07-17 in Python 3.11.9
and 3.14.6. Windows is the supported Stage-01 backend/runtime, validation, CI,
and deployment platform. Linux is not currently supported or validated. This
does not certify scientific, release, privacy, security, licensing, or
operational readiness.

## Component matrix

| Component | Status | Current evidence | Principal gap |
|---|---|---|---|
| Surya input adapter | PARTIAL | `systems/Parasara/engine/adapter/surya_adapter.py`, `systems/Parasara/schemas/surya_input.schema.json`, adapter tests | `load` validates input, but `load_many` does not consistently apply the same schema-validation boundary |
| Chart models | PARTIAL | `systems/Parasara/engine/models.py` | Mutable defaults and incomplete target contracts remain |
| Normalization | PARTIAL | `systems/Parasara/engine/normalizer.py` | Broad exception fallbacks, mutation, and no formal dependency-ordered pipeline contract |
| AstroState API | IMPLEMENTED | `engine/astrostate_api.py`, `rules/snapshot_adapter.py`, `tests/astrostate`, `tools/validate_prompt04.py` | Mutable construction compatibility remains before freeze; scientific/release validation is separate |
| AstroState construction | PARTIAL | mutable `engine/astrostate.py`, normalizer, and existing producers | Broad fallbacks and mutable compatibility models remain construction-only |
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
| RuleMatch | IMPLEMENTED | `engine/rules/rule_match.py`, `rule_engine.py`, Prompt-02 contract/integration tests | Scientific/public/release validation remains separate |
| Yoga evaluation | IMPLEMENTED | Snapshot-based producer orchestration, RuleMatch-backed typed batch, compatibility projection, Prompt-04/Prompt-02/WP17 tests | Public compatibility projection/state attachment remain until later typed-output work |
| Career interpreter | PARTIAL | Snapshot-query factual bridge, one shared inference call, and compatibility projection in `career.py`/`career_models.py` | Public compatibility dictionary remains until Prompt-05 typed domains |
| Other domain interpreters | MISSING | Placeholder Wealth output in `systems/Parasara/tools/generate_snapshot.py` | Typed Wealth, Marriage, Children, Health, and Safety interpreters absent |
| Shared InferenceEngine | IMPLEMENTED | `engine/inference/`, versioned config, Prompt-03 contract/integration/architecture tests | Career is the first migrated domain; calibration and later domain policies remain separate |
| Typed domain output | MISSING | Current interpreters return dictionaries | Approved DomainPrediction boundary absent |
| OutputAssembler | MISSING | `systems/Parasara/tools/generate_snapshot.py` assembles dictionaries directly | Dedicated schema-validating serialization-only layer absent |
| Rule-set selection | PARTIAL | Hardcoded `v1` paths in runtime/loaders and output metadata | No explicit EngineConfig, strict selection, or cache-safe version propagation |
| Rule governance | MISSING | Metadata fragments and proposed policy only | No promotion, rollback, approval enforcement, or audit service |
| Prompt-01 validation/CI | IMPLEMENTED | `tools/validate_prompt01.py`, `tests/wp19`, Windows dual-Python CI workflow, WP19 | Linux portability, external required-check setting, and release/compliance gates are separate |
| Prompt-04 validation/CI | IMPLEMENTED | `tools/validate_prompt04.py`, deterministic snapshot/query manifest, dual-Python Windows workflow | External required-check setting and release/compliance gates remain separate |
| Snapshot/testing harness | PARTIAL | Prompt-01 gate, snapshots, testing framework | Prompt-01 compatibility validated; scientific/production acceptance remains |
| Public engine API | MISSING | Tool-level entry points only | Versioned service/facade contract absent |
| Production operations | MISSING | Documentation checklist only | Monitoring, deployment, retention automation, and operational evidence absent |

## Active architectural blockers

1. Domain thinning/public output stabilization depend on
   typed outputs.
2. Release/privacy/security/licensing/publication work remains separate owner
   work.

## Validation status

Prompt-04 focused and full dual-lane validation passed on Windows on 2026-08-21 with
912 collected nodes, 910 passed and 2 skipped per full lane, 62 Prompt-04
tests, 38 remediation tests, fatal rejection of unsafe supplied aspect facts,
strict canonical Career exception visibility, and
identical snapshot/query manifest `440a459cc60e9575874341e7c6673e714585ae79123957c9c19ccd175cb7930b`,
current WP17/Prompt-02/Prompt-03 manifests, protected artifacts and exports,
public Career/Yoga behavior, and the approved snapshot. Linux
is not a supported or validated Prompt-01 platform. Scientific
correctness, SME approval, public schema approval, privacy/security/licensing,
and production operations remain separate gates.

Remaining non-Prompt risks include Dasha wall-clock fallback, mutable
construction compatibility state, some legacy discovery/fallback paths, and
incomplete public/output and release architecture.

All Prompt-04 remediation findings R1-R10 are verified. Invalid supplied aspect
facts fail before snapshot publication; nonfatal malformed capability
availability remains a separate typed state.

## Superseded status source

The former status document is preserved at `../archive/legacy-implementation-status.md`. Its completion labels are not canonical when they conflict with this evidence-based matrix.
