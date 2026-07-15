# Prompt-01 Audit-16: Domain Runtime

## 1. Executive Summary

Audit-16 is **COMPLETE**. All fifteen prerequisite reports were present. Repository-wide inspection found one implemented domain, Career, and one active domain execution path. Wealth is a constant output placeholder, not an implemented runtime; Marriage, Children, Health, Safety/Longevity, Education, Spirituality, and other domain interpreters are absent.

The active Career path is not connected to `evaluate_predicate` or `evaluate_condition`. `interpret_career` builds flat mutable rule dictionaries and calls the legacy `evaluate_rule_with_score`, with a broad-exception fallback to `evaluate_rule` (`systems/Parasara/engine/interpreters/career.py:33-64`). That legacy runtime performs raw-boolean and inline factual evaluation, converts a `RuleMatch` model immediately to a dictionary, and collapses unavailable, invalid, unsupported, and failed evaluations into `matched=False` (`systems/Parasara/engine/rules/runtime.py:111-245`). Career then consumes only `matched`, a score field, selected matched evidence, and context. Predicate/condition status, version, typed errors, traces, child results, and unmatched evidence cannot reach domain scoring.

Career also performs three factual computations directly: kendra/10th-house occupancy selection, 10th-house/lord lookup, and 10th-house occupant-strength reconstruction. These overlap registered or predicate-like facts even though Career's scoring and narrative are legitimate domain concerns. Career owns the complete prototype inference policy: neutral/base score, positive contribution filtering, clipping, confidence, components, and summary. Prompt-01 must not change those valid-output results accidentally while correcting the factual contract.

No domain mutates AstroState or predicate/result objects and no domain reads raw Surya payloads. The snapshot path normalizes through `SuryaAdapter` before Career. Nevertheless, the legacy runtime mutates shared rule-loader state through best-effort auto/lazy loading, bypasses the predicate cache entirely, and has no cold/warm equivalence test. Seven serialization surfaces expose Career behavior, from its dictionary through snapshots, the Python runner, the Next.js API route, and the frontend summary/JSON download.

The 20 compliance findings total **P0=6, P1=7, P2=5, P3=2**. Career is the only domain requiring direct caller migration. The safe Prompt-01 boundary is an explicit compatibility path that preserves current valid matching, contributions, score, confidence, indicators, evidence shape, ordering, and public JSON while replacing legacy factual results with approved typed results. Shared inference, typed `DomainPrediction`, additional domains, and the dedicated `OutputAssembler` remain future stages.

## 2. Audit Scope and Method

This read-only audit covered all repository files matching domain, interpreter, score, confidence, explainability, runtime, output, API, fixture, rule, and test terminology. Static call graphs were verified with symbol searches rather than inferred from names. Production files inspected in depth were `engine/interpreters/career.py`, `engine/rules/runtime.py`, `engine/confidence.py`, `engine/explainability.py`, `tools/generate_snapshot.py`, `tools/runner_api.py`, and `frontend/app/(auth)/account/astro/page.tsx` plus the Next route.

The authoritative target-state, AstroState, inference, output, Prompt-01, current-state, implementation-status, roadmap, and testing documents were reconciled with Audits 1–15. Existing Career/runtime tests and all JSON snapshot/fixture consumers were inventoried. Safe searches were completed. Focused tests were attempted but could not start because the available Python environment has no `pytest` module; production code, rules, fixtures, tests, previous reports, and snapshots were not changed.

The audit classifies an implemented domain only when executable code performs domain-specific evaluation or interpretation. A fixed dictionary carrying a domain key is a placeholder, not an implemented runtime. Generic integration means actual use of the central registry-backed predicate/condition path; merely producing a dictionary named `RuleMatch` does not qualify.

## 3. Reconciliation with Audits 1–15

All expected reports exist under `systems/Parasara/Documentation/Engine/Prompt-01/Reports/`; there is no missing-report limitation.

- Audits 1–2 establish six registered IDs/five handlers plus raw-boolean and predicate-like alternatives. Audit-16 finds no domain direct handler import or registry lookup, but Career reaches the alternate M1 factual runtime.
- Audits 3–4 classify the Career/runtime chain as active legacy compatibility and identify zero registered-handler bypasses. Audit-16 preserves that result: one active domain path is `LEGACY_TUPLE_OR_BOOLEAN_PATH`, not `DIRECT_HANDLER_BYPASS`.
- Audits 5–6 show the incomplete shallow-frozen `PredicateResult`, dictionary `RuleMatch`, and absent typed status/supporting models. Career sees the serialized dictionary only and therefore cannot preserve the missing typed contract.
- Audit 7 finds no parameter schema. Career constructs flat, unvalidated parameters in Python; runtime unknown/invalid values become ordinary false outcomes.
- Audits 8–10 identify missing capability semantics, mutable AstroState, enrichment ambiguity, and factual purity issues. Career reads normalized AstroState and prepared enrichments without mutating them, but the legacy runtime cannot distinguish unavailable data from negative facts.
- Audit 11 finds an unsafe central cache. Career bypasses it; a future migration must prove that adopting the approved cache does not change logical scoring between cold and warm runs.
- Audits 12–13 identify four evaluator contracts and two active syntaxes. Career uses the flat F3 compatibility syntax and neither generic condition evaluation nor a typed `ConditionResult`.
- Audit 14 identifies the raw M1 loader/runtime path, best-effort global registry state, and score/public-output migration risk. Audit-16 traces that risk through every domain consumer.
- Audit 15 finds one active Yoga path but no domain consumer. Career independently evaluates `rajayoga_naive`; Yoga results remain hardcoded as `[]` in public snapshot diagnostics.

No prior count or active/dormant classification is contradicted.

## 4. Domain Component Inventory

| Domain | Component | File | Symbol | Category | Responsibility | Inputs | Outputs | Evaluator | Predicate Integration | Scoring | Mutation | Consumers | Status | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Career | domain interpreter | `systems/Parasara/engine/interpreters/career.py:8-116` | `interpret_career` | `DOMAIN_ENTRY_POINT`, `DOMAIN_INTERPRETER`, `DOMAIN_CONDITION_CALLER`, `DOMAIN_SCORER` | build candidate rules, consume matches, score, confidence, components, evidence, narrative | mutable `AstroState` | untyped Career dictionary | legacy runtime pair | `LEGACY_TUPLE_OR_BOOLEAN_PATH` plus inline facts | base average + positive contributions, clipping, heuristic confidence | reads only; builds mutable local dict/list output | snapshot assembler; tests | active production, partial | interpreter, snapshots, vertical slice |
| Career | scored rule runtime | `systems/Parasara/engine/rules/runtime.py:111-245` | `evaluate_rule_with_score` | `LEGACY_DOMAIN_EVALUATOR`, `DOMAIN_FACT_HELPER` | load/merge flat rules, evaluate facts, attach prototype score | AstroState + flat rule dict | serialized `RuleMatch` dict | local branch dispatch and `evaluate_rule` | `LEGACY_TUPLE_OR_BOOLEAN_PATH`; no central predicate/condition API | hard-coded per-type score | lazy/global rule registry and instrumentation state; no AstroState mutation | Career; runtime tests | active legacy production | runtime and merge tests |
| Career | primitive evaluator | `systems/Parasara/engine/rules/runtime.py:61-108` | `evaluate_rule` | `LEGACY_DOMAIN_EVALUATOR`, `DOMAIN_FACT_HELPER` | dispatch four raw-boolean fact helpers | AstroState + flat rule dict | `{match,evidence}` dict | local exact-string dispatch | `LEGACY_TUPLE_OR_BOOLEAN_PATH` | none; caller adds 0.05 fallback | instrumentation state only | scored runtime; Career exception fallback; tests/tooling | active alternate/fallback | runtime tests |
| Career | confidence helpers | `systems/Parasara/engine/confidence.py:4-67` | `compute_*` | `DOMAIN_SCORER` | data completeness, match coverage, evidence-strength proxy, confidence | AstroState + synthetic match dicts | float | none | receives lossy synthetic dictionaries | `0.4 coverage + 0.3 score proxy + 0.3 completeness` | none | Career | active production | snapshot coverage only |
| Career | explainability helpers | `systems/Parasara/engine/explainability.py:4-22` | `evidence_for_rule`, `scoring_breakdown` | `DOMAIN_SCORER`, `DOMAIN_OUTPUT_ADAPTER` | wrap matched evidence and calculate clipped score breakdown | rule/eval dicts, base, contributions | dictionaries | none | downstream of legacy conversion | `min(1, base + sum)` | none | Career/public output | active production | indirect snapshots |
| Career | snapshot assembler | `systems/Parasara/tools/generate_snapshot.py:14-49` | `assemble_output`, `generate` | `DOMAIN_OUTPUT_ADAPTER`, `DOMAIN_ENTRY_POINT` | call Career and directly assemble public dictionaries | normalized/enriched AstroState | snapshot dict/JSON | Career | indirect legacy dependency | none itself; publishes scores | output file write in `generate`; no AstroState mutation | tests, runner/API, frontend | active production/tool | four snapshot/interpreter suites |
| Wealth | fixed placeholder | `systems/Parasara/tools/generate_snapshot.py:35` | `assemble_output` wealth literal | `DOMAIN_OUTPUT_ADAPTER` | expose empty/default Wealth-shaped dictionary | none | constant dictionary | none | none | constant score/confidence 0.5 | none | snapshot/API/frontend JSON | placeholder, not implemented | full snapshot incidentally |
| Career | Python API runner | `systems/Parasara/tools/runner_api.py:62-107` | `main` | `DOMAIN_OUTPUT_ADAPTER`, `DOMAIN_ENTRY_POINT` | generate normalized snapshot and wrap with raw chart for client inspection | birth request/Surya chart | `{snapshot,surya_chart}` JSON | snapshot generator | indirect legacy dependency | none | temporary files only | Next API route | active public tool | no focused contract test found |
| Career | Next API bridge | `frontend/app/api/astro/generate/route.ts:22-67` | `POST` | `DOMAIN_OUTPUT_ADAPTER` | spawn runner and relay JSON | HTTP request | HTTP JSON | Python runner | indirect | none | none | frontend | active public path | no focused domain contract test found |
| Career | frontend consumer | `frontend/app/(auth)/account/astro/page.tsx:172-200` | `ResultViewer` | `DOMAIN_OUTPUT_ADAPTER` | read Career summary, display/download full snapshot | public snapshot JSON | UI/download JSON | none | indirect | no recomputation | local UI state only | user | active public path | no focused test found |
| Career | regression artifacts | `systems/Parasara/tests/test_career_*.py`; `test_vertical_slice_career.py`; `test_additional_snapshots.py`; fixtures/snapshots | test functions and JSON artifacts | `TEST_OR_FIXTURE` | assert structure, indicator IDs, or complete snapshot equality | fixtures | assertions/goldens | production path | indirect legacy dependency | freezes selected/current values | test output files only via temp path | CI/developers | active tests/artifacts | self |
| Other named domains | absent runtimes | repository-wide | none | `UNKNOWN` | no executable interpreter discovered | N/A | N/A | N/A | N/A | N/A | N/A | N/A | missing | none |

Rule source for Career is split: candidate rule instances are constructed in `interpret_career`; `evaluate_rule_with_score` optionally merges matching/type-compatible records loaded from `systems/Parasara/rules/parashara/v1/m1_rules.yaml` through the generic loader. There is no domain-specific loader or compiler.

## 5. End-to-End Domain Execution Paths

| Domain | Entry Point | Rule/Indicator Source | Loader | Evaluator | Intermediate Contract | Consumption Pattern | Scoring Path | Evidence | Errors | Trace | Cache | Output | Active Evidence | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Career | `generate` -> `assemble_output` -> `interpret_career` | Python candidate dictionaries; optional M1 YAML metadata merge | generic loader with global registry, best effort | `evaluate_rule_with_score`; broad fallback to `evaluate_rule` | serialized `RuleMatch` dict or `{match,evidence}` fallback dict | `bool(matched)` plus `adjusted_score/score`; accept only matched positive contribution | kendra-strength mean -> sum positive contributions -> clip 1.0 -> confidence from matched count/score proxy/completeness | matched-positive only, wrapped by rule ID; unmatched evidence dropped | runtime collapses; Career catches any escaped exception and falls back | runtime trace field usually `None`; Career replaces lineage with constant `career_001` | central predicate cache bypassed; mutable rule registry/load state | Career dict -> snapshot -> runner/API/frontend | direct imports/calls at `career.py:45-113`, `generate_snapshot.py:34`, route/runner chain | P0 |
| Wealth | `assemble_output` | constant literal | none | none | fixed dict | no factual consumption | fixed 0.5 score/confidence | none | none | none | none | placeholder Wealth JSON | literal at `generate_snapshot.py:35` | P3 |

Implemented-domain active execution paths: **1**. The Wealth row is a serialization placeholder and is excluded from that count. Yoga is an enrichment/rule diagnostic path, not a domain runtime, and no active domain consumes it.

## 6. Generic Predicate and Condition Integration

| Domain | File | Symbol | Called API | Integration Type | Expected Contract | Status Use | Evidence Use | Error Use | Trace Use | Mutation | Serialization | Migration Required | Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Career | `engine/interpreters/career.py:45-64` | `interpret_career` | `runtime.evaluate_rule_with_score`; fallback `evaluate_rule` | `LEGACY_TUPLE_OR_BOOLEAN_PATH` | RuleMatch-like dict / legacy match dict | reads boolean only; no status | preserves matched-positive evidence; drops all other evidence | none; broad exception erases cause | none; emits unrelated constant domain trace | no result mutation | converts to indicators/evidence/domain dict | Yes | Critical | P0 |
| Career | `engine/interpreters/career.py:58-64` | `interpret_career` | `explainability.evidence_for_rule` | `GENERIC_PATH_WITH_INFORMATION_LOSS` downstream adapter, not generic predicate execution | reduced `{match,evidence}` | unavailable | preserves supplied evidence only | unavailable | unavailable | none | evidence dictionary | Yes, after typed rule boundary | High | P1 |
| Career | `engine/interpreters/career.py:94-104` | `interpret_career` | `confidence.compute_confidence` | `GENERIC_PATH_WITH_INFORMATION_LOSS` downstream adapter | synthetic match/score dictionaries | boolean matched only | original evidence omitted | omitted | omitted | none | float confidence | Yes, future inference stage | High | P2 |
| Career | `tools/generate_snapshot.py:14-40` | `assemble_output` | `interpret_career` | indirect legacy consumer | untyped Career dict | none | serializes existing evidence | serializes no typed errors | serializes constant Career trace only | none | full public dict | Compatibility adapter required | Critical | P1 |

No domain calls `evaluate_predicate`, `evaluate_condition`, a registered handler, or registry lookup. No domain tuple-unpacks a central result. The zero direct-handler-bypass count is retained from Audits 3–4; the legacy runtime is instead a parallel evaluator containing four raw-boolean primitives and hard-coded higher-level facts.

The two rows labelled information loss are downstream reductions of the legacy domain result. They do not count as active **generic predicate paths** in the summary, because no central typed predicate/condition result enters them. Summary integration counts are therefore generic typed **0**, generic-with-information-loss **0**, direct registered-handler bypass **0**, legacy tuple/raw-boolean path **1**.

## 7. Result-Consumption Contracts

`evaluate_rule_with_score` constructs `RuleMatch` then immediately calls `model_dump()`/`dict()` (`runtime.py:211-245`). This loses the type boundary while retaining current fields as mutable nested dictionaries. It never carries `PredicateResult`, predicate identity/version/status/errors/trace steps/child results/cache telemetry. Career accepts both `adjusted_score` and legacy `score`, making two unvalidated dictionary shapes part of active compatibility.

Three domain conversion boundaries discard result information:

1. `interpret_career` reduces each rule dictionary to boolean match and contribution. It discards status, typed errors, predicate/rule trace lineage, predicate version, provenance in output indicators, and all unmatched or non-positive evidence (`career.py:55-64`).
2. The explainability adapter receives a newly constructed `{match,evidence}` object rather than the original result. It preserves those two values and rule/context, but status, error, trace, version, provenance, confidence, and timing were already removed (`career.py:62-64`; `explainability.py:4-11`).
3. Confidence receives synthetic `{matched,adjusted_score}` dictionaries created from already-filtered evidence. It receives no original evidence, status, errors, traces, versions, provenance, or unmatched rows (`career.py:94-104`).

Counted caller/conversion losses are: status **3**, evidence **2**, errors **3**, traces **3**. No caller mutates a result or nested result collection. The output dictionaries themselves remain mutable, and the full Career dictionary is publicly serialized.

## 8. Status Semantics

The legacy contracts have no status enum. Career treats every false-like outcome identically and contributes zero. The following current states collapse to negative/no-contribution behavior:

- factual unmatched;
- missing planet or missing lord/fact input;
- missing enrichment values that fall back to `0.0` or `None`;
- unsupported/unknown rule type;
- invalid or misspelled parameters/types;
- evaluation exception caught inside runtime;
- any exception escaping the scored evaluator and yielding a false legacy fallback.

There is no representation of `missing_capability`, `invalid_parameters`, `error`, `timeout`, or `skipped`; confidence is not deliberately lowered for unavailable facts. Missing metadata can lower apparent coverage because the denominator includes all candidate rules while only matched-positive evidence is supplied to confidence. Public output exposes no stable diagnostic code or recoverability.

Two active missing-capability-to-negative-evidence paths are counted: the scored runtime's internal collapse and Career's broad fallback through the primitive evaluator. Prompt-01 must define how typed non-match statuses affect eligibility without inventing new Career weights or changing valid factual matches. Timeout and skipped semantics have no current implementation and remain unresolved.

## 9. Evidence, Error and Trace Handling

Matched-positive rules preserve rule ID, contribution, runtime evidence, and context in `indicators`; a second evidence wrapper repeats rule ID, context, match, evidence, and contribution. Factual expected/actual values survive only when the selected legacy branch supplies them. Unmatched, errored, unsupported, missing-input, and zero/negative-contribution evidence is discarded before domain output.

Nested predicate/condition evidence never enters Career. Runtime evidence is ad hoc, mutable, and branch-specific. `rajayoga_naive` exposes occupants; `strong_in_10` exposes planet/house/strength; `lord_status` exposes lord/dignity. No predicate version, stable AstroState fact ID, rule provenance, child relation, error code, or recoverability is associated with the public indicator.

The runtime catches all evaluation exceptions and emits `{'error':'evaluation_failed'}` while marking false (`runtime.py:202-205`), but Career drops that evidence because it is unmatched. Career then catches any remaining exception without recording text or type. Raw exception text is therefore not public, but only because all diagnostics are erased.

The current `RuleMatch.trace_id` is normally `None`; predicate trace steps do not exist on this path. Career emits constant `'career_001'`, which is deterministic but not linked to rule or predicate execution. Cache-hit/timing telemetry does not reach score or JSON. Trace ordering and lineage cannot be audited from the output.

## 10. Direct Factual Logic and Duplication

Three Career-local factual computations overlap central or legacy factual helpers:

| Domain File and Symbol | Factual Calculation | Registered/Predicate-Like Equivalent | Semantic/Parameter Difference | Evidence Difference | Active Caller | Migration Risk |
|---|---|---|---|---|---|---|
| `career.py:14-21`, `interpret_career` | select planets in kendra houses and read strength | `PLANET_IN_HOUSE`, `HOUSE_OCCUPANT`, runtime `in_house` | set membership across 1/4/7/10 plus direct strength; predicates test one requested fact | no factual evidence retained for base score | `assemble_output` | Critical: base score changes if selection/absence semantics change |
| `career.py:27-31`, `interpret_career` | find house 10 and retrieve its lord | runtime `lord_of_house`; AstroState house query intent | retrieval from `enrichments.house_summaries`, not boolean lord assertion over `astro.houses` | missing summary/lord silently omits candidate; no status/evidence | `assemble_output` | High: state-shape/capability migration changes rule set and confidence denominator |
| `career.py:71-82`, `interpret_career` | resolve 10th occupants to planets and average strengths | `HOUSE_OCCUPANT`/`PLANET_IN_HOUSE`; runtime `strong_in_10` | trusts summary occupants, filters missing strengths, derives house component independent of rule match | only component occupants/weight; no source/version or missing-name evidence | `assemble_output` | High: duplicated representations can disagree |

These three are counted as inline factual-logic duplicates. The rule runtime adds seven predicate-like factual groups (`in_sign`, `in_house`, `lord_of_house`, `is_exalted`, strong-in-house, lord-status, rajayoga/aspect branches), but those belong to the single legacy evaluator path already inventoried by Audits 2–4; they are not added again to the domain-local duplicate count. Career scoring, clipping, confidence, contribution selection, and narrative are not classified as factual duplicates.

## 11. Scoring and Confidence Compatibility

| Domain | Current Scoring Input | Unmatched Behavior | Missing-Capability Behavior | Invalid-Parameter Behavior | Error Behavior | ConditionResult Impact | Tuple-Removal Impact | Regression Risk | Required Decision | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| Career | mean kendra planet strength; matched positive `adjusted_score/score`; candidate count; matched contribution proxy; AstroState completeness | zero contribution; unmatched evidence absent | currently indistinguishable from unmatched and can lower coverage | currently false/zero | false/zero or fallback; cause erased | typed logical results could change match/status/evidence and candidate eligibility; Career currently has no logical result consumer | removing legacy dict/raw-bool path breaks field access and fallback unless adapted | Critical across score, confidence, indicators, components, summary, snapshots | preserve valid factual outcomes and current scoring formula behind explicit typed-to-compatibility boundary; separately decide status eligibility | P0 |
| Wealth placeholder | no factual inputs | N/A | N/A | N/A | N/A | none | none | Low, unless placeholder removal changes schema | defer real Wealth domain to typed-domain stage | P3 |

Current Career scoring is:

- base score: average strength of planets in houses 1, 4, 7, and 10, or `0.5` if none;
- contributions: only rules where `matched` and `contrib > 0`;
- final score: `min(1.0, base + sum(contributions))`, without a lower clamp;
- confidence: `0.4 * matched/total + 0.3 * average(adjusted_score) + 0.3 * four-field data completeness`; when no evidence, the rule list supplied is empty;
- conflicts/negative contributions: none; negative or zero contributions are excluded;
- thresholds: `strong_in_house >= 0.75`; dignity in `own_sign|exalted`; rule-specific hard-coded scores reside in runtime.

Six scoring-regression risks are counted: base-fact selection, rule match eligibility, contribution magnitude/source, candidate denominator, evidence-filtered confidence, and cache/loader lifecycle equivalence. `or`-based score selection in `compute_evidence_strength` also treats a legitimate zero as absent. Immutable evidence should not itself affect scoring because Career reads only values, but mutable-dict assumptions in adapters and tests must be removed deliberately. `ConditionResult` replacement is an indirect future risk because the active path currently bypasses conditions.

## 12. AstroState and Raw-Source Boundary

Career accepts typed `AstroState` and reads `planets`, houses through `enrichments.house_summaries`, `enrichments.planet_strengths` indirectly in runtime, and metadata/houses in confidence. These are legitimate prepared-fact inputs in principle, although direct dictionary reads and cross-representation reconstruction bypass a stable query/capability boundary.

Career does not import the adapter, load raw Surya JSON, repair provider fields, compute an enrichment module, or mutate AstroState. The production snapshot path is `SuryaAdapter.load -> chart_to_astrostate -> interpret_career` (`generate_snapshot.py:43-46`). `runner_api` exposes the raw Surya chart beside the snapshot for frontend inspection, but it does not pass that raw object into Career. Raw Surya domain-boundary violations: **0**.

The main ambiguity is `astro.enrichments['house_summaries']` versus `astro.houses`: Career uses the former for the 10th lord/component while runtime `lord_of_house` uses the latter. Audit-9's mutable/multiple-representation risk therefore affects factual consistency even without direct domain mutation.

## 13. Mutation, Statefulness and Cache Interaction

AstroState or predicate/result mutation paths in domain code: **0**. Career creates and mutates only local candidate/result/output containers. It does not write enrichments, cache fields, result evidence, or shared score state.

Statefulness remains relevant in the invoked legacy runtime. `evaluate_rule_with_score` best-effort loads rules when the global registry is empty, consults that mutable registry, and merges metadata based on exact ID or first matching type (`runtime.py:125-164`). Import-time auto-loading and production imports from test instrumentation add process/order state. These are loader/runtime state paths, not counted as AstroState/result mutation.

Career neither reads nor clears the central predicate cache, and the legacy evaluator bypasses it. Three domain cache risks are counted:

1. migrating Career onto the central evaluator introduces Audit-11 key/value/lifecycle behavior into a path previously uncached;
2. current global rule-registry warmth/import/CWD state can alter which metadata and base score are merged before Career scoring;
3. no test proves cold/warm logical equality, telemetry exclusion, or repeated deterministic domain output under the future cache.

No `cache_hit` or evaluation timing is used in score, evidence, trace, snapshot, or API output. Current repeated Career execution should be logically stable for a fixed already-normalized AstroState and stable registry, but static analysis cannot prove stability across import/CWD/global-registry states.

## 14. Serialization and Public-Output Dependencies

Seven public or regression serialization impacts are counted:

1. `interpret_career`'s dictionary fields: `summary`, `score`, `confidence`, `components`, `indicators`, `evidence`, `scoring`, `trace_id`.
2. `assemble_output` embeds that dictionary at `domains.career` and a Wealth placeholder.
3. Career-specific golden fixtures freeze indicator IDs and selected shapes.
4. the full vertical-slice snapshot freezes complete values, ordering, empty collections, and schema.
5. `runner_api` wraps snapshot output with `surya_chart` and serializes it.
6. the Next.js API route relays parsed runner JSON without schema validation.
7. `ResultViewer` reads `domains.career.summary` and displays/downloads the entire snapshot.

PredicateResult and ConditionResult are not serialized directly because Career never receives them. Runtime `RuleMatch` is serialized to a dict before Career, then only selected fields survive. Prompt-01 changes can therefore affect field types (enums/mappings/tuples), evidence JSON safety, deterministic ordering, indicator firing, scores/confidence, and golden/API output even if the public schema is intended to stay stable.

The existing `test_vertical_slice_matches_snapshot` provides the strongest compatibility guard. Career-specific snapshot tests compare only indicator IDs and structure, not complete status/evidence/error/trace semantics. The fixed `career_001` and normalized `generated_at=None` are deterministic; no timing/cache telemetry is public.

## 15. Domain-by-Domain Compatibility Assessment

| Domain | Active | Generic Typed Path | Direct Bypass | Legacy Contract | Inline Facts | Evidence Preserved | Errors Preserved | Traces Preserved | Compatibility Classification | Required Action | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Career | Yes | No | no registered-handler direct call; yes parallel legacy evaluator | Yes | 3 | matched-positive subset only | No | No; constant unrelated ID only | `DIRECT_CALLER_MIGRATION_REQUIRED`, `SCORING_REGRESSION_RISK` | typed factual/rule compatibility boundary preserving current valid outputs; then later shared inference/domain model | P0 |
| Wealth | No; constant output only | No | No | No | 0 | N/A | N/A | N/A | `INACTIVE_OR_TEST_ONLY` | retain explicit placeholder compatibility or version its later removal | P3 |
| Marriage/relationships | No implementation found | N/A | N/A | N/A | N/A | N/A | N/A | N/A | `INACTIVE_OR_TEST_ONLY` | future typed-domain stage | P3 |
| Children | No implementation found | N/A | N/A | N/A | N/A | N/A | N/A | N/A | `INACTIVE_OR_TEST_ONLY` | future typed-domain stage | P3 |
| Health | No implementation found | N/A | N/A | N/A | N/A | N/A | N/A | N/A | `INACTIVE_OR_TEST_ONLY` | future typed-domain stage | P3 |
| Safety/longevity | No implementation found | N/A | N/A | N/A | N/A | N/A | N/A | N/A | `INACTIVE_OR_TEST_ONLY` | future typed-domain stage | P3 |
| Education | No implementation found | N/A | N/A | N/A | N/A | N/A | N/A | N/A | `INACTIVE_OR_TEST_ONLY` | future typed-domain stage | P3 |
| Spirituality | No implementation found | N/A | N/A | N/A | N/A | N/A | N/A | N/A | `INACTIVE_OR_TEST_ONLY` | future typed-domain stage | P3 |

Only priority findings in the compliance/migration inventory are included in P0–P3 summary totals; absent future domains do not each create separate Prompt-01 findings.

## 16. Existing Tests and Coverage Gaps

Existing evidence includes structural Career output checks, indicator-ID snapshots over three fixtures, one complete vertical-slice snapshot, legacy runtime primitive/scored behavior, and rule-registry merge behavior. These protect current valid output partially but do not prove architectural compliance.

| Area | Missing Categories | Count | Risk | Recommended Test File |
|---|---|---:|---|---|
| Generic integration | domain calls generic predicate; domain calls generic condition/rule boundary; no direct registered-handler bypass; no tuple/raw-boolean contract; typed results reach scoring | 5 | migration can retain a parallel factual engine or silently flatten results | `systems/Parasara/tests/test_career_generic_contract.py` |
| Status behavior | matched; unmatched; missing capability; invalid parameters; predicate error; timeout; skipped branch | 7 | all current false/error states score identically | `systems/Parasara/tests/test_career_status_semantics.py` |
| Evidence/diagnostics | unmatched evidence; typed errors; predicate/condition traces; raw exception text excluded | 4 | explanation and failure diagnosis disappear before output | `systems/Parasara/tests/test_career_diagnostics.py` |
| Regression | cold/warm logical equivalence; repeated deterministic evaluation | 2 | cache or global lifecycle could change score/output | `systems/Parasara/tests/test_career_determinism.py` |
| Architecture enforcement | no tuple-unpacking domain caller; no raw-boolean predicate caller; no raw Surya import; no predicate-to-domain import; no predicate/result mutation | 5 | future edits can reintroduce forbidden coupling | `systems/Parasara/tests/test_domain_architecture.py` |

Missing prescribed test categories: **23**. Matched evidence reaching the domain is partially covered by `test_career_interpreter_outputs_structure` and snapshots. Current score, rule firing, confidence, and serialization stability are covered most strongly by the complete vertical-slice snapshot; the narrower Career snapshot tests compare only indicator IDs. There is no active test for a non-Career domain because none is implemented.

## 17. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Domain factual path uses approved typed engine | `NONCOMPLIANT` | Career calls legacy runtime only | Career/runtime | migrate/isolate through approved typed boundary | `IN_SCOPE` | P0 | Yes |
| Distinct status semantics reach domain | `MISSING` | boolean-only consumption | Career/runtime | preserve typed status and approved eligibility policy | `IN_SCOPE` | P0 | Yes |
| Preserve valid Career scoring behavior | `PARTIAL` | snapshot coverage exists; migration boundary absent | Career/explainability/confidence/tests | characterize and enforce compatibility | `TEMPORARY_COMPATIBILITY` | P0 | Yes |
| Preserve complete errors and traces | `NONCOMPLIANT` | broad catches/drop; constant trace | Career/runtime | carry typed diagnostics/lineage without raw exception leak | `IN_SCOPE` | P0 | Yes |
| Validate parameters/capabilities before scoring | `NONCOMPLIANT` | flat unchecked rules and false collapse | Career/runtime/loader | consume Audit-7/8 typed outcomes | `IN_SCOPE` | P0 | Yes |
| Cache-safe cold/warm domain equivalence | `MISSING` | legacy bypass, no test | engine/cache/Career tests | approved cache plus domain equivalence tests | `IN_SCOPE` | P0 | Yes |
| Preserve unmatched evidence where policy requires | `NONCOMPLIANT` | matched-positive filter | Career | typed rule/domain adapter must retain diagnostics | `IN_SCOPE` | P1 | Yes |
| Preserve predicate/rule versions and provenance | `NONCOMPLIANT` | omitted from indicators/evidence | runtime/Career | retain typed linkage through adapter | `IN_SCOPE` | P1 | Yes |
| Eliminate duplicated domain factual checks | `PARTIAL` | three local facts | Career/AstroState query boundary | migrate facts without moving domain scoring | `IN_SCOPE` | P1 | Yes |
| Deterministic rule/registry lifecycle | `NONCOMPLIANT` | lazy/import/CWD global state | runtime/loader | explicit versioned selection/snapshot | `IN_SCOPE` | P1 | Yes |
| No domain result mutation | `IMPLEMENTED` | local reads only | Career | enforce with test | `IN_SCOPE` | P1 | Yes |
| No raw Surya domain access | `IMPLEMENTED` | adapter/normalizer precede Career | generator/Career | enforce import/runtime boundary test | `IN_SCOPE` | P1 | Yes |
| Domain architecture/status test suite | `MISSING` | 23 categories missing | tests | add focused tests during implementation | `IN_SCOPE` | P1 | Yes |
| Preserve current public Career JSON | `PARTIAL` | snapshot exists; indirect consumers untyped | generator/runner/API/frontend | explicit compatibility/schema decision | `TEMPORARY_COMPATIBILITY` | P2 | No |
| Remove production dependency on test instrumentation | `NONCOMPLIANT` | runtime imports `tests.testing_framework` | runtime | replace with production observability boundary | `IN_SCOPE` | P2 | No |
| Replace mutable dictionary adapters | `PARTIAL` | RuleMatch/domain/evidence dictionaries | runtime/Career/helpers | typed internal adapter while retaining public compatibility | `TEMPORARY_COMPATIBILITY` | P2 | No |
| Resolve multiple AstroState fact representations | `PARTIAL` | house summaries versus houses | Career/runtime/AstroState | stable query/capability policy | `OUT_OF_SCOPE_FUTURE_STAGE` | P2 | No |
| Separate placeholder/public domain availability | `PARTIAL` | Wealth looks scored but is unevaluated | generator/output schema | explicit unavailable status in typed output stage | `OUT_OF_SCOPE_FUTURE_STAGE` | P2 | No |
| Shared InferenceEngine | `MISSING` | Career owns scoring/confidence | Career/confidence/explainability | Prompt-03 shared inference | `OUT_OF_SCOPE_FUTURE_STAGE` | P3 | No |
| Typed DomainPrediction and OutputAssembler | `MISSING` | Career/generator dictionaries | Career/generator/public consumers | Prompt-05 typed/output stages | `OUT_OF_SCOPE_FUTURE_STAGE` | P3 | No |

## 18. Migration Risks and Priorities

The 20 findings total **P0=6, P1=7, P2=5, P3=2**.

P0 work must establish the typed factual/rule compatibility boundary, status/error behavior, score compatibility, validated parameters/capabilities, and cold/warm equivalence before the legacy path is removed. The most likely user-visible regressions are changed candidate firing, adjusted scores, base-score membership, confidence denominator, indicator order/content, summary rounding, and snapshot/API JSON.

P1 work must preserve unmatched diagnostics, versions/provenance, remove local factual duplication, stabilize loader state, enforce no-mutation/raw-source boundaries, and cover the missing architecture/status tests. P2 items are compatibility and quality concerns that should not cause Prompt-01 to redesign public output or later AstroState/domain architecture. P3 items—shared inference and typed domain/output models—are explicitly later stages.

A safe sequence is: freeze current valid Career fixtures and score mechanics; introduce typed factual/rule results with an explicit legacy-shape adapter; decide non-match status eligibility; prove cold/warm and repeated equality; migrate Career consumption; then retire the raw-boolean evaluator only when no active caller remains. This is a migration boundary, not an instruction to implement during Audit-16.

## 19. Unresolved Architectural Questions

1. Which typed result reaches Career during Prompt-01: PredicateResult-derived compatibility data, a temporary typed rule result, or the later universal RuleMatch?
2. For each non-match status, should a Career candidate remain in the confidence denominator, be unavailable, or invalidate the domain evaluation?
3. Must unmatched and errored candidate evidence appear in the temporary Career public dictionary, or only remain internally traceable until the output stage?
4. Which current Career fields/order are guaranteed compatibility versus incidental snapshot behavior?
5. How are the three Career-local facts moved behind stable AstroState/predicate queries without changing base and component calculations?
6. What stable trace lineage replaces `career_001` while avoiding a premature public-schema redesign?
7. How is explicit M1 rule-set selection introduced without changing the current merge winner or hard-coded scores?
8. Should the fixed Wealth object remain a placeholder or expose typed unavailable status only in the later domain/output stage?

These questions affect safe implementation but do not block completion of this audit.

## 20. Audit-16 Conclusion

Audit-16 is COMPLETE. Career is the sole implemented domain and has one active legacy raw-boolean/dictionary path. It has no generic typed predicate/condition integration, no registered-handler direct bypass, three inline factual duplicates, two missing-capability-negative paths, three status/error/trace-loss conversion boundaries, two evidence-loss boundaries, six scoring risks, zero AstroState/result mutations, zero raw Surya violations, three cache-related risks, and seven public serialization impacts. Career alone requires direct caller migration. Exactly this report was created; no production code, tests, fixtures, rules, snapshots, previous reports, or Audit-17 artifacts were modified.

### Summary counts

| Metric | Count |
|---|---:|
| Implemented domains | 1 |
| Active domain execution paths | 1 |
| Generic typed paths | 0 |
| Generic paths with information loss | 0 |
| Direct predicate-handler bypasses | 0 |
| Legacy tuple or raw-boolean paths | 1 |
| Inline factual-logic duplicates | 3 |
| Callers/conversions discarding status | 3 |
| Callers/conversions discarding evidence | 2 |
| Callers/conversions discarding errors | 3 |
| Callers/conversions discarding traces | 3 |
| Missing-capability-to-negative-evidence paths | 2 |
| Scoring regression risks | 6 |
| AstroState or result mutation paths | 0 |
| Raw Surya boundary violations | 0 |
| Cache-related domain risks | 3 |
| Public serialization impacts | 7 |
| Domains requiring direct caller migration | 1 |
| Missing domain test categories | 23 |
| P0 findings | 6 |
| P1 findings | 7 |
| P2 findings | 5 |
| P3 findings | 2 |
