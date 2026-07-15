# Parāśara Engine Implementation Status

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-13

## Status rules

- `IMPLEMENTED`: active source satisfies the stated current contract; scientific or production validation may still be a separate gate.
- `PARTIAL`: usable implementation exists but does not satisfy the approved contract or validation gate.
- `MISSING`: no active implementation of the approved component was found.
- `UNVERIFIED`: implementation exists, but correctness or acceptance evidence was not established during documentation review.

This document records repository evidence. It does not certify test results; no test suite was run for this documentation migration.

## Component matrix

| Component | Status | Current evidence | Principal gap |
|---|---|---|---|
| Surya input adapter | PARTIAL | `systems/Parasara/engine/adapter/surya_adapter.py`, `systems/Parasara/schemas/surya_input.schema.json`, adapter tests | `load` validates input, but `load_many` does not consistently apply the same schema-validation boundary |
| Chart models | PARTIAL | `systems/Parasara/engine/models.py` | Mutable defaults and incomplete target contracts remain |
| Normalization | PARTIAL | `systems/Parasara/engine/normalizer.py` | Broad exception fallbacks, mutation, and no formal dependency-ordered pipeline contract |
| AstroState | PARTIAL | `systems/Parasara/engine/astrostate.py` | Mutable, dictionary-heavy, and lacks capabilities, logical digest, evaluation context, and approved query API |
| Derived state | PARTIAL | `systems/Parasara/engine/derived/` | Builder can return an unvalidated dictionary and is not the sole downstream access boundary |
| Vargas | PARTIAL | `systems/Parasara/engine/enrichments/varga.py` and related tests | Classical coverage and validation vary by varga |
| Aspect enrichment | PARTIAL | `systems/Parasara/engine/enrichments/aspects.py` and related tests | Capability/version contract and full graph policy are incomplete |
| Functional roles | PARTIAL | `systems/Parasara/engine/enrichments/functional_roles.py`, YAML tables, and tests | Working-directory-dependent discovery, SME authority, and complete validation are unresolved |
| Planet strengths | PARTIAL | `systems/Parasara/engine/enrichments/planet_strengths.py`, `shadbala.py`, and tests | Contains approximations/proxies and working-directory-dependent tables; classical validation incomplete |
| Vimshottari Dasha | PARTIAL | `systems/Parasara/engine/dasha/vimshottari.py`, unit tests, and golden tests | Not integrated into primary output; wall-clock fallback and Moon-longitude input require correction/verification |
| PredicateResult | PARTIAL | `systems/Parasara/engine/rules/engine.py`, `tests/rules/test_predicate_result.py` | Approved Prompt-01 metadata, deep immutability, errors/status, serialization, validation, and cache isolation incomplete |
| Predicate registry | PARTIAL | `PREDICATE_REGISTRY` and `register_predicate` in `systems/Parasara/engine/rules/engine.py` | Handler-only storage, silent replacement, import initialization, incomplete validation |
| Generic condition evaluator | PARTIAL | `evaluate_condition` in `systems/Parasara/engine/rules/engine.py` | Only leaves plus AND/OR; no typed ConditionResult or approved trace semantics |
| Rule loader | PARTIAL | `systems/Parasara/engine/rules/loader.py`, `yoga_loader.py` | Best-effort error suppression, silent duplicates, working-directory paths, and incomplete version/governance enforcement |
| M1 rule runtime | PARTIAL | `systems/Parasara/engine/rules/runtime.py` | Prototype hardcoded dispatch/scoring, dictionary output, working-directory loading, and production dependency on test instrumentation |
| RuleMatch | PARTIAL | `systems/Parasara/engine/models.py`, M1 runtime | Runtime serializes the model to dictionaries; universal contract and PredicateResult preservation missing |
| Yoga evaluation | PARTIAL | `systems/Parasara/engine/enrichments/yoga_engine.py`, YAML rules, tests | Custom dictionaries, random trace IDs, mutation, swallowed errors, and legacy tuple helpers remain |
| Career interpreter | PARTIAL | `systems/Parasara/engine/interpreters/career.py` and snapshot tests | Owns candidate construction, generic scoring/confidence, narrative, and dictionary output responsibilities |
| Other domain interpreters | MISSING | Placeholder Wealth output in `systems/Parasara/tools/generate_snapshot.py` | Typed Wealth, Marriage, Children, Health, and Safety interpreters absent |
| Shared InferenceEngine | MISSING | No active module found | Required aggregation, normalization, conflicts, and confidence service absent |
| Typed domain output | MISSING | Current interpreters return dictionaries | Approved DomainPrediction boundary absent |
| OutputAssembler | MISSING | `systems/Parasara/tools/generate_snapshot.py` assembles dictionaries directly | Dedicated schema-validating serialization-only layer absent |
| Rule-set selection | PARTIAL | Hardcoded `v1` paths in runtime/loaders and output metadata | No explicit EngineConfig, strict selection, or cache-safe version propagation |
| Rule governance | MISSING | Metadata fragments and proposed policy only | No promotion, rollback, approval enforcement, or audit service |
| Snapshot/testing harness | PARTIAL | `systems/Parasara/tests/`, `tests/`, snapshots, and `tests/testing_framework/` | Full current pass state and scientific acceptance were not verified |
| Public engine API | MISSING | Tool-level entry points only | Versioned service/facade contract absent |
| Production operations | MISSING | Documentation checklist only | Monitoring, deployment, retention automation, and operational evidence absent |

## Active architectural blockers

1. The complete approved Prompt-01 prerequisite audit sequence must finish before PredicateResult implementation.
2. Predicate identity, registry metadata, supporting models, parameter validation, capability handling, cache identity, callers, and compatibility boundaries require approved audit decisions.
3. Universal RuleMatch depends on completed PredicateResult consolidation.
4. Shared inference depends on universal RuleMatch.
5. Domain thinning and public output stabilization depend on shared inference and typed outputs.

## Validation status

The repository contains targeted tests and golden artifacts, but this status document does not assert that they currently pass. Scientific correctness, SME approval, full-suite regression, deterministic replay, and production readiness remain separate acceptance gates.

Known current determinism and deployment risks include wall-clock and random trace generation, object-identity caching, mutable global registries/caches, broad exception fallbacks, working-directory-dependent discovery, and a production runtime import from `tests.testing_framework`.

## Superseded status source

The former status document is preserved at `../archive/legacy-implementation-status.md`. Its completion labels are not canonical when they conflict with this evidence-based matrix.
