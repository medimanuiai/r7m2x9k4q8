# Parāśara Engine Implementation Status

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-08-29

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
| Yoga evaluation | IMPLEMENTED | Snapshot-based producer orchestration, RuleMatch-backed typed batch, Prompt-05 YogaDiagnostic mapping, exact compatibility projection | Public compatibility projection/state attachment remains until consumers migrate to an approved typed/public schema |
| Career interpreter | IMPLEMENTED | Snapshot-query factual bridge, one shared inference call, closed typed build outcome, DomainPrediction, exact compatibility projection | Public compatibility dictionary remains until consumers migrate through an approved schema change |
| Other domain interpreters | MISSING | Shared DomainId/model readiness only; compatibility-only Wealth row in OutputAssembler | Typed Wealth, Marriage, Children, Health, and Safety interpreters absent by Prompt-05 design |
| Shared InferenceEngine | IMPLEMENTED | `engine/inference/`, versioned config, Prompt-03 contract/integration/architecture tests | Career is the first migrated domain; calibration and later domain policies remain separate |
| Typed domain output | IMPLEMENTED | `engine/domain/`, Prompt-05 model/factory/adversarial/determinism tests | Only Career is substantively implemented; public typed schema migration remains separate |
| OutputAssembler | IMPLEMENTED | `engine/output_assembler.py`, typed assembly input, purity/architecture/exact snapshot tests | Current outward profile intentionally preserves the unversioned legacy public shape |
| Rule-set selection | PARTIAL | Hardcoded `v1` paths in runtime/loaders and output metadata | No explicit EngineConfig, strict selection, or cache-safe version propagation |
| Rule governance | MISSING | Metadata fragments and proposed policy only | No promotion, rollback, approval enforcement, or audit service |
| Prompt-01 validation/CI | IMPLEMENTED | `tools/validate_prompt01.py`, `tests/wp19`, Windows dual-Python CI workflow, WP19 | Linux portability, external required-check setting, and release/compliance gates are separate |
| Prompt-04 validation/CI | IMPLEMENTED | `tools/validate_prompt04.py`, deterministic snapshot/query manifest, dual-Python Windows workflow | External required-check setting and release/compliance gates remain separate |
| Prompt-05 validation/CI | IMPLEMENTED | `tools/validate_prompt05.py`, typed-domain manifest, composed predecessor gates, dual-Python Windows workflow | External required-check setting and release/compliance gates remain separate |
| Snapshot/testing harness | PARTIAL | Prompt-01 gate, snapshots, testing framework | Prompt-01 compatibility validated; scientific/production acceptance remains |
| Public engine API | MISSING | Tool-level entry points only | Versioned service/facade contract absent |
| Production operations | MISSING | Documentation checklist only | Monitoring, deployment, retention automation, and operational evidence absent |

## Active architectural blockers

1. Additional domain implementations and a richer public schema require
   separately approved domain/public migration work.
2. Rule-set selection/governance remains Prompt-06.
3. Release/privacy/security/licensing/publication work remains separate owner
   work.

## Validation status

Prompt-02/WP17 Yoga baseline contradiction reconciled; Prompt-05 R4 validation
completed; independent Final R4 Review pending. The reconciled current
Prompt-02/WP17 manifest is
`06330b43cac062239e0670d1e48ab00c328ee270af64023b2017b819dc7b3017`;
the old `75b65d2cd1420c6261aadbb8159d10fb8c641137ce08d29f2a651952e5cdfaf7`
remains historical baseline evidence. RuleMatch remains the sole Yoga
truth/status/evidence/trace authority and all 14 R4 attack classes pass.

R4 validation passed under Windows Python 3.11.9 and 3.14.6. Each full
Prompt-05 lane collected 1,005 nodes, with 1,003 passed, 2 optional-dependency
skips, and 0 failed; 93 focused Prompt-05 tests passed. Prompt-03, Prompt-04,
and Prompt-05 manifests remain exact at `f57bc285...a563786e`,
`440a459c...b7930b`, and `f6d90db7...3c393ba92`. Public Career and unaffected
Yoga behavior, Yoga order, 24 protected artifacts, four personal exports, and
the 4,041-byte approved snapshot remain exact. Frontend lint, nonincremental
type-check, 12-route production build, and 14 static generation units passed.
Prompt-05 remains unaccepted until independent Final R4 Review; commit
authorization and Prompt-06 remain blocked.

Prompt-05 remediation R3 focused and full dual-lane validation passed on
Windows on 2026-08-23 with 985 collected nodes, 983 passed and 2 skipped per
full lane, 73 focused Prompt-05 tests (including 13 R3 adversarial tests), all
Prompt-02/03/04 and WP17 gates, and identical Prompt-05 manifest
`f6d90db74309127e99d55e17c542214b05bb385b8ec62447c1baef53c393ba92`.
The Prompt-02/WP17, Prompt-03, and Prompt-04 manifests remain
`75b65d2cd1420c6261aadbb8159d10fb8c641137ce08d29f2a651952e5cdfaf7`,
`f57bc28504988ecf5ccfbf82de4bc495d2e69a91dfd476997cda5c89a563786e`,
and `440a459cc60e9575874341e7c6673e714585ae79123957c9c19ccd175cb7930b`.
Public Career/Yoga hashes, 24 protected artifacts, four present personal
exports, and the 4,041-byte approved snapshot remain exact. Frontend lint,
non-incremental type-check, and production build passed; the build listed 12
routes and completed 14 static page-generation units without leaving a
TypeScript build-info cache. Final R2 failed; R3 is implementation-validated
but is not accepted until an independent Final R3 Review passes.
Linux
is not a supported or validated Prompt-01 platform. Scientific
correctness, SME approval, public schema approval, privacy/security/licensing,
and production operations remain separate gates.

Remaining non-Prompt risks include Dasha wall-clock fallback, unavailable
integrated transit/Dasha output, mutable construction compatibility state,
some legacy discovery/fallback paths, additional missing domains, unexposed
public schema version, rule governance, and release architecture.

All Prompt-04 remediation findings R1-R10 are verified. Invalid supplied aspect
facts fail before snapshot publication; nonfatal malformed capability
availability remains a separate typed state.

## Superseded status source

The former status document is preserved at `../archive/legacy-implementation-status.md`. Its completion labels are not canonical when they conflict with this evidence-based matrix.
