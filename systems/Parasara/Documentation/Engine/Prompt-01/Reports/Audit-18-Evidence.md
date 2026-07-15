# Prompt-01 Audit-18: Evidence

## 1. Executive Summary

Audit-18 is **COMPLETE**. All seventeen prerequisite reports were present. Six registered predicate IDs backed by five handlers were verified directly. None produces complete matched evidence under Prompt-01's expected/actual/capability/version standard, and none produces complete unmatched evidence. All six are `MATCHED_ONLY`: they can emit some evidence when true but normally return `{}` when false. No registered predicate is wholly without a matched-evidence path.

The central problem is not merely sparse output. Empty unmatched evidence collapses fact-false, missing planet/entity, unavailable capability, invalid parameters, malformed enrichment, and handler failure. Audit-8's **14 missing-capability-versus-entity conflations** remain current. All six IDs omit explicit expected and/or actual observations. Seven misleading evidence paths are counted: one for each registered ID's false/capability ambiguity plus a separate `PLANET_EXALTED` semantic path.

`PLANET_EXALTED` has one suspected semantic defect. It first accepts an explicit `flags.exalted` value, but otherwise marks a planet exalted whenever `metadata.exaltations` contains an entry for that planet. It does not compare the current sign or longitude with the configured exaltation placement. Its evidence can therefore present a configured exaltation degree as if it were an observed current exaltation (`systems/Parasara/engine/rules/predicates.py:85-99`).

`ASPECT`/`ASPECT_EXISTS` preserve matched edge dictionaries but cannot distinguish a missing/malformed AspectGraph, a present empty graph, and a valid graph with no requested match. `PLANET_IN_HOUSE` and `HOUSE_OCCUPANT` repeat requested values on matches and provide no observed house/occupant facts on failures. `FUNCTIONAL_ROLE` recomputes role facts during predicate evaluation but returns only matched planet display names, omitting the observed role, source table/version, ownership facts, and capability readiness.

All evidence is shallow mutable. ASPECT evidence embeds live edge dictionaries from mutable AstroState enrichment; condition aggregation retains anonymous child evidence; cache copies share nested evidence; Yoga and Career pass mutable references onward. Seven mutable-evidence mechanisms, one non-JSON-safe risk class, and four nondeterministic mechanisms were found. Cold and warm values are normally equal, but one reachable caller-mutation path can corrupt cached warm evidence.

Condition aggregation has three evidence-loss paths, Yoga has two, and Career/domain processing has two. Predicate identity and complete child results are removed before Yoga; Career is on a separate legacy path and retains only matched-positive rule evidence. Six evidence-related serialization surfaces can be affected by immutable/canonical normalization.

The 21 compliance findings total **P0=7, P1=8, P2=4, P3=2**. Prompt-01 must establish factual evidence shapes, explicit false/missing/error distinctions, stable identities, deep immutable JSON-safe normalization, child-linked aggregation, and cache equivalence without silently redesigning the factual astrology.

## 2. Audit Scope and Method

The Master Architecture and Prompt-01 DOCX sources were reconciled with Audits 1–17. Prompt-01 requires evidence to be factual, deterministic, deeply immutable, JSON-safe, capability-aware, and preserved with predicate identity. Domain scoring, confidence, interpretation, and public formatting remain outside predicate evidence.

Repository-wide discovery covered evidence producers, `PredicateResult`, registered handlers, AspectGraph and functional-role sources, condition aggregation, Yoga conversion, legacy rule/domain paths, cache storage, snapshots, artifact generation, runner/API/frontend output, tests, fixtures, and documentation. Counts use registered IDs when assessing predicate compliance, even where ASPECT and ASPECT_EXISTS share one handler.

A non-writing `python -B` behavior probe was attempted, but importing the production predicates failed before evaluation because the active interpreter lacks `pydantic`. Static source is sufficient because all handler return branches and literal evidence shapes are explicit. `pytest` is also unavailable. No code, tests, rules, fixtures, snapshots, prior reports, or Audit-19 artifacts were modified.

## 3. Reconciliation with Audits 1–17

All prerequisite reports exist; no limitation or blocker applies.

- Audits 1–2 establish six registered IDs/five handlers. Audit-18 reverified the current decorators and every return branch; the count is unchanged.
- Audits 3–4 identify generic Yoga and legacy Career flows. Evidence propagation below preserves their active/dormant classifications.
- Audits 5–6 prove shallow result immutability, arbitrary nested values, no evidence model, and no canonical serializer. Audit-18 narrows those model risks to concrete evidence producers/consumers.
- Audit 7 finds invalid inputs become false/empty evidence or raw exception dictionaries. Four evaluator/condition reason shapes are counted as invalid/error data improperly occupying evidence rather than factual observations.
- Audit 8 counts 14 capability/entity conflations. Audit-18 retains that expanded dependency-level count rather than reducing it to six IDs.
- Audits 9–10 establish mutable AstroState, Aspect shape collision, CWD-dependent role calculation, and predicate-time recomputation. These directly affect evidence source authority and determinism.
- Audit 11 proves cached nested aliasing. Audit-18 counts one reachable cold/warm evidence-corruption path, while noting unmutated logical evidence remains equal.
- Audit 12 establishes anonymous child evidence, eager AND/OR, no NOT/skipped representation, and loss of complete child results. Audit-18 counts three evidence-specific loss paths.
- Audit 14 confirms no validation/compiler/source location. Evidence has no rule source, condition path, or definition version.
- Audit 15 counts two Yoga evidence-loss paths; Audit-18 preserves **2**.
- Audit 16 counts two domain evidence-discard paths and three error/status conversions. Audit-18 uses the evidence-specific count **2**.
- Audit 17 establishes error dictionaries and raw messages. Those diagnostics are not factual evidence and must move to typed errors rather than be normalized as observations.

No earlier report is contradicted.

## 4. Complete Predicate Evidence Inventory

| Predicate ID | File | Handler | Matched Evidence | Unmatched Evidence | Missing-Capability Evidence | Expected/Actual | Identity Type | Immutable | JSON-Safe | Deterministic | Semantic Concerns | Downstream Preservation | Tests | Quality | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ASPECT` | `systems/Parasara/engine/rules/predicates.py:12-47` | `aspect_exists` | `{'matched_edges':[edge,...]}` using original graph edge dicts | `{}` | `{}`; missing/malformed/list graph treated empty | requested filters remain only in inputs; actual matched edges present; no graph capability/version | `DISPLAY_NAME_ONLY` for source/target | No; mapping/list/edge refs mutable | current generated graph yes; arbitrary injected edge not validated | edge/input order dependent | target-`None` edges can match unconstrained requests; alias result ID is ASPECT_EXISTS | condition keeps evidence anonymously; Yoga keeps raw evidence but loses predicate ID | no direct predicate evidence test | `MATCHED_ONLY` | P0 |
| `ASPECT_EXISTS` | `systems/Parasara/engine/rules/predicates.py:12-47` | `aspect_exists` | same matched edge list | `{}` | same missing/empty/malformed conflation | same | `DISPLAY_NAME_ONLY` | No | conditionally | conditionally | alias/cache/result identity divergence; capability ambiguity | same | no direct evidence test | `MATCHED_ONLY` | P0 |
| `PLANET_IN_HOUSE` | `systems/Parasara/engine/rules/predicates.py:50-57` | `planet_in_house` | `{'planet':name,'house':requested}` | `{}` | `{}` when planets/state unavailable | no `actual_house`/`expected_house`; matched evidence repeats input | `DISPLAY_NAME_ONLY` | No | current scalar shape yes | yes for stable inputs | absent planet, invalid house, and false occupation identical | condition/Yoga only; Career uses legacy duplicate | match/cache test does not inspect evidence | `MATCHED_ONLY` | P0 |
| `HOUSE_OCCUPANT` | `systems/Parasara/engine/rules/predicates.py:60-67` | `house_occupant` | `{'planet':requested,'house':requested}` | `{}` | `{}` when houses/planets unavailable | no actual occupants or observed planet house | `DISPLAY_NAME_ONLY` | No | current scalar shape yes | yes for stable inputs | repeats request rather than observation; cannot distinguish entity absence | condition/Yoga raw evidence, identity lost | no direct predicate test | `MATCHED_ONLY` | P0 |
| `FUNCTIONAL_ROLE` | `systems/Parasara/engine/rules/predicates.py:70-82` | `functional_role` | `{'matched_planets':[names...]}` | `{}` | `{}` or generic predicate-error reason after recomputation failure | expected roles only in inputs; observed roles/table/version/ownership absent | `DISPLAY_NAME_ONLY` | No; list mutable | current list/strings yes | CWD/table/context/cache dependent | recomputes facts; empty context means all; no source/version | condition/Yoga evidence only; errors/status lost | no direct predicate evidence test | `MATCHED_ONLY`, `INCOMPLETE` | P0 |
| `PLANET_EXALTED` | `systems/Parasara/engine/rules/predicates.py:85-99` | `planet_exalted` | flag path: planet + true flag; metadata path: planet + configured degree | `{}` | `{}` for missing planet/exaltation facts | no current sign/longitude, expected sign/degree, comparison/orb/version | `DISPLAY_NAME_ONLY` | No | current scalars yes | stable only for fixed mutable metadata | metadata-entry existence is treated as current exaltation proof | condition/Yoga evidence only; Career uses separate dignity rule | false-only test; evidence/placement untested | `MISLEADING` | P0 |

Registered predicates audited: **6**. Complete matched evidence: **0**. Complete unmatched evidence: **0**. Matched-only evidence predicates: **6**. Predicates without any evidence-producing branch: **0**.

## 5. Matched Evidence

ASPECT evidence is the richest because each edge may contain source, target, aspect/kind, and an enrichment trace. However, it embeds the original mutable edge and does not state which requested filters were applied, graph capability/version, normalization, or stable entity IDs. It is `ADEQUATE` for some current matches but not complete.

The two house predicates provide only the requested planet/house on success. Because the result is matched, a reader can infer equality, but the evidence does not independently record actual versus expected values or observation source. HOUSE_OCCUPANT does not list actual occupants. FUNCTIONAL_ROLE lists matched planets but not their actual roles, table/heuristic source, ownership facts, or version.

PLANET_EXALTED's explicit flag branch is partially factual; its mapping branch is misleading. None includes all actual/expected/comparison/version content required for independent explanation, hence complete matched count zero.

No predicate evidence contains domain scores, weights, confidence, recommendations, or narratives. The registered handlers remain factual in intent.

## 6. Unmatched Evidence

All six registered IDs return `{}` for normal unmatched outcomes. Available observations are discarded:

- ASPECT IDs do not record graph availability, edge count, requested filters, examined source/target entities, or why no edge qualified.
- PLANET_IN_HOUSE does not record the actual planet house.
- HOUSE_OCCUPANT does not record actual occupants or the requested planet's actual house.
- FUNCTIONAL_ROLE does not record evaluated candidates and their observed roles.
- PLANET_EXALTED does not record the actual sign/longitude, explicit flag state, or missing configuration.

This is useful only as an empty-schema convention, not factual explainability. Fact-false cannot be separated from entity absence, invalid inputs, or unavailable capability. Complete unmatched evidence count is zero.

## 7. Expected-versus-Actual Values

All **6 predicate IDs** are missing explicit expected and/or actual values.

| Predicate IDs | Missing Expected Content | Missing Actual Content | Comparison Metadata |
|---|---|---|---|
| ASPECT, ASPECT_EXISTS | normalized requested filters and expected relation | graph availability/version and examined/no-match facts | operation, graph version, normalization |
| PLANET_IN_HOUSE | explicit expected house | actual house or entity-absence fact | equality/normalization |
| HOUSE_OCCUPANT | expected occupant/house | actual occupants and requested planet house | membership/equality |
| FUNCTIONAL_ROLE | normalized accepted role set | per-candidate observed roles and source | membership, table/heuristic version |
| PLANET_EXALTED | configured expected sign/degree/rule | current sign/longitude/flag | rule, orb/tolerance, normalization/version |

Units and tolerance are most relevant to exaltation longitude but absent. ASPECT enrichment traces may contain degrees and configured offsets, but the predicate does not summarize which comparison/filter produced the match.

## 8. Missing-Capability and Missing-Entity Evidence

Audit-8's **14 dependency-level conflations** remain verified: both Aspect IDs depend on normalized planets and AspectGraph; house predicates depend on normalized planet/house facts; FUNCTIONAL_ROLE depends on planets, lagna, table/config/context; PLANET_EXALTED depends on planet placement and exaltation facts. Missing, `None`, empty, malformed, and legitimate no-match generally converge on `{}`.

The six registered-ID misleading false paths are:

1. ASPECT missing/malformed graph versus valid no match;
2. ASPECT_EXISTS same shared-handler ambiguity;
3. PLANET_IN_HOUSE missing planet/state versus valid different house;
4. HOUSE_OCCUPANT missing planet/house capability versus valid nonoccupancy;
5. FUNCTIONAL_ROLE unavailable/recomputed-empty role facts versus no qualifying role;
6. PLANET_EXALTED unavailable placement/config versus not exalted.

No evidence declares capability identity, availability, version, completeness, or recoverability. Condition/Yoga can therefore consume missing capability as negative factual evidence.

## 9. Invalid-Parameter and Error Evidence

Registered handlers normally return empty factual evidence for invalid parameters. The evaluator then introduces four nonfactual evidence shapes:

1. unknown predicate: `reason=unknown_predicate`;
2. invalid return: `reason=invalid_predicate_return` plus rendered Python type;
3. handler exception: `reason=predicate_error` while raw exception text sits in `errors`;
4. missing condition type: `reason=missing_type`.

These are diagnostics, not factual observations. They lack typed status/code/source location and are cached/aggregated like facts. Unvalidated caller inputs are retained in `PredicateResult.inputs`, not normally duplicated into evidence, but legacy runtime and Yoga reason dictionaries do repeat unchecked values.

Invalid-parameter or exception data stored as evidence paths: **4**. No registered evidence deliberately contains raw Surya payloads or stack traces. ASPECT can expose arbitrary nested graph-edge values because there is no shape validation.

## 10. Entity Identity and References

All six registered IDs use `DISPLAY_NAME_ONLY` identity. Planet evidence uses exact runtime names; aspect edges use source/target strings. None uses `PlanetState.canonical_id`, a stable house ID, aspect ID, capability ID, rule/version ID, or condition-node ID.

Case normalization and Rahu/Ketu aliases are absent. `_planet_by_name` is exact and case-sensitive. ASPECT decorator aliases return `predicate_id='ASPECT_EXISTS'` even for an ASPECT lookup, further weakening identity. No object reference or `id(...)` is placed directly into current handler evidence, but ASPECT evidence shares mutable dictionaries owned by AstroState.

Unstable/noncanonical identity uses: **6 registered IDs**.

## 11. Deep Immutability and Canonicalization

Seven mutable-evidence mechanisms are counted:

1. `PredicateResult.evidence` is a mutable dictionary despite the frozen outer dataclass.
2. ASPECT evidence stores a mutable list of original mutable edge dictionaries and nested traces.
3. FUNCTIONAL_ROLE evidence stores a mutable matched-planets list.
4. condition aggregation builds mutable child lists/dictionaries and retains child evidence values without deep freezing.
5. Yoga reuses `pr.evidence` and produces mutable lists/dictionaries.
6. Career legacy indicators and explainability wrappers reuse nested evidence references.
7. cache `replace` is shallow, so cold-result mutation corrupts stored/warm evidence.

No defensive copying, tuple conversion, immutable mapping, cycle detection, canonical numeric policy, or deep validator exists. One non-JSON-safe evidence risk class is counted: the unrestricted nested `Any` contract can accept custom objects, cycles, non-string keys, sets, dataclasses, enums, NaN/Infinity, or injected ASPECT edge content. Current built-in registered success shapes are JSON-safe for normal generated AstroState, but the model does not guarantee it and the direct serializer uses `default=str`.

Four nondeterministic evidence mechanisms are counted:

1. mutable/shared evidence can be changed by caller order;
2. ASPECT evidence order/content follows mutable graph construction/config source;
3. FUNCTIONAL_ROLE evidence depends on CWD-selected tables and unkeyed context;
4. object-identity caching and post-cache capability/state mutation can preserve stale evidence.

Yoga UUID and set ordering affect downstream wrappers rather than the predicate evidence mapping itself; they are discussed as propagation risks but not double-counted here.

## 12. Factual-Boundary Violations

Registered handler evidence is classified `FACTUAL_EVIDENCE` in intent. No domain score, confidence, rule weight, conflict resolution, recommendation, or public formatting is inserted by registered predicates.

`PLANET_EXALTED` is `MISLEADING`, not interpretive: the problem is a factual algorithm/evidence mismatch. Evaluator diagnostic reasons are nonfactual and belong in typed errors/status. ASPECT enrichment traces contain explanatory text such as configured-offset narratives; these are factual calculation explanations rather than domain narratives, but they should be structured/versioned rather than treated as the sole proof.

Legacy Career evidence adds contributions outside predicate evidence, and Yoga adds rule/domain fields outside `pr.evidence`; those are downstream contracts, not registered-predicate factual-boundary violations.

## 13. Priority Predicate Semantic Review

| Predicate | Actual Algorithm | Matched Evidence | Unmatched Evidence | Missing-Data Behavior | Suspected Semantic Issue | Evidence Correct | Tests | Required Review | Priority |
|---|---|---|---|---|---|---|---|---|---|
| `PLANET_EXALTED` | find exact-name planet; accept raw `flags.exalted`; otherwise match if metadata exaltation mapping has any degree entry | planet+flag or planet+configured degree | `{}` | missing planet/config becomes false | mapping existence does not prove current sign/longitude is exalted | No on metadata path | only false/no-error | SME/config model review of sign/degree/orb semantics | P0 |
| `ASPECT_EXISTS`/`ASPECT` | read `enrichments.aspects` only if dict; filter edges by optional houses/planets | original matching edges | `{}` | missing/list/malformed/empty/no-match collapse | unconstrained/misspelled filters can broaden match; target-None edges may qualify | Partial | no direct predicate evidence tests | approve graph capability/version and filters | P0 |
| `PLANET_IN_HOUSE` | exact-name planet lookup, direct house equality | requested planet/house | `{}` | missing entity indistinguishable | no actual-house observation | Only inferentially | match/cache only | expected/actual/entity absence contract | P0 |
| `FUNCTIONAL_ROLE` | recompute roles from CWD table/heuristic; filter context candidates by requested roles | matched planet names | `{}` | failure generic; empty facts false | evidence hides observed role/source and recomputation | Incomplete | none | prepared capability/version/source policy | P0 |
| `HOUSE_OCCUPANT` | exact-name planet lookup, direct house equality | requested planet/house | `{}` | missing entity/house indistinguishable | no actual occupant collection or actual planet house | Only inferentially | none | occupant evidence/query boundary | P0 |

Suspected semantic errors: **1** (`PLANET_EXALTED` metadata path). The other rows are evidence/contract concerns; this audit does not adjudicate or change astrological mathematics.

## 14. Condition Evidence Aggregation

Three condition evidence-loss paths are counted:

1. Generic AND/OR replace complete child results with `{'children':[child.evidence,...]}`. Predicate IDs, inputs, status/version, cache, errors as typed objects, and nested result identity are absent from evidence.
2. Dormant Yoga-local AND/OR do the same with tuple evidence and no identity/error channel.
3. NOT is unsupported; it falls through as an unknown predicate and never evaluates/preserves child evidence. Skipped branches cannot be represented.

Generic child order is raw list order and all children evaluate; no merge collision occurs because evidence remains in a positional list. Nested conditions create anonymous nested `children`. Error summaries live in `trace_steps`, separate from factual evidence, but Yoga discards them. Empty AND/OR evidence is an empty children list and does not explain vacuous truth/falsehood.

## 15. Yoga Evidence Preservation

Yoga's active path copies `pr.evidence` into each custom dictionary, so the raw root evidence is partially preserved. It then derives `planets`, `houses`, and `aspects_used` using shallow/root-level assumptions. Nested evidence is flattened only one level for matched planets; aspect edges nested under logical children are missed; houses are read from root params that current logical nodes do not have. Predicate and condition identity, full children, inputs, errors, status/version, trace, cache, and timing are discarded.

Yoga therefore retains potentially misleading false evidence while discarding the diagnostics that would distinguish missing capability/error. It does not add scores to predicate evidence. It mutates AstroState to store Yoga results and shares mutable evidence references. The dormant tuple path separately generates duplicate evidence with different false shapes. Yoga evidence-loss paths: **2**.

## 16. Domain Evidence Preservation

Career does not consume the generic predicate/condition path. Its legacy runtime produces ad hoc evidence; `interpret_career` preserves it only for matched rules with positive contribution and associates it with rule ID/context. It drops all unmatched, unavailable, invalid, errored, zero, and negative evidence. The explainability wrapper nests the same evidence with a contribution, and confidence receives synthetic matches with no factual evidence.

Two domain evidence-loss paths are counted, consistent with Audit-16: the primary rule-to-indicator filter and the confidence synthesis boundary. Contribution/score fields are adjacent domain data, not inserted into the nested predicate evidence. Career evidence reaches public snapshot/API JSON; no generic PredicateResult evidence does. Wealth has no factual evidence.

## 17. Cache Equivalence

Cold evaluation returns one result; the cache stores `replace(res, cache_hit=True)` and warm retrieval returns the stored object. Without mutation, evidence is logically equal because the same nested values are shallowly shared. Telemetry does not enter evidence.

There is **1 reachable cold/warm evidence-difference path**: mutate the cold result's evidence/nested edge/list after evaluation, thereby mutating the stored warm result. State/capability changes can also make unchanged cached evidence stale because keys use `id(astro)` and omit state digest, predicate version, context, capability/configuration versions, and enrichment readiness. Yoga clears globally before its run, but direct callers do not.

No test asserts cold/warm evidence equality, defensive copying, stale capability recovery, or caller-mutation isolation.

## 18. Serialization and Public Exposure

| Evidence Source | Predicate Result | Condition | Yoga | Domain | Output | Identity Preserved | Ordering Preserved | Information Lost | Preservation Classification | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| registered leaf evidence | mutable mapping | direct leaf unchanged | root raw mapping retained | no generic consumer | debug/asdict only | result ID only until Yoga | current list/dict order | version/status/capability | `PARTIALLY_PRESERVED` | P0 |
| AND/OR children | anonymous children list | root aggregate | raw nested list retained | none | Yoga diagnostics only if later wired | No | raw child order | complete children and IDs | `FLATTENED_WITH_INFORMATION_LOSS` | P0 |
| missing/error evidence | empty or diagnostic reason | aggregated as if fact | retained without status/errors | legacy separate false evidence dropped | generally absent | No | N/A | outcome class/recoverability | `FLATTENED_WITH_INFORMATION_LOSS` | P0 |
| Yoga derived evidence | N/A | source already reduced | raw evidence plus lossy derived fields | no active consumer | current primary snapshot hardcodes yogas `[]` | Yoga ID only | planet set order not guaranteed | predicate identity/traces | `PARTIALLY_PRESERVED` | P1 |
| Career legacy evidence | no PredicateResult | bypassed | N/A | matched-positive only, wrapped twice | snapshot/runner/API/frontend | rule ID retained | candidate/indicator order | all nonmatched/error evidence | `PARTIALLY_PRESERVED` | P1 |
| cache evidence | shallow same object | warm child reuse | shared across Yoga rules | generic path absent | debug if serialized | same ID | mutation-dependent | isolation/freshness | `PARTIALLY_PRESERVED` | P0 |

| File | Symbol | Predicate/Consumer | Mutable Value | Non-JSON Value | Raw Object/Input | Nondeterminism | Public Exposure | Current Protection | Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| `systems/Parasara/engine/rules/engine.py:9-18` | `PredicateResult` | all | evidence dict/nested values | unrestricted `Any` | possible | caller mutation | debug/asdict | frozen outer only | Critical | P0 |
| `systems/Parasara/engine/rules/predicates.py:12-47` | `aspect_exists` | ASPECT IDs | list + original edges/traces | injected graph values possible | AstroState-owned edge dicts | graph/config/order | Yoga; future diagnostics | none | Critical | P0 |
| `systems/Parasara/engine/rules/predicates.py:70-82` | `functional_role` | FUNCTIONAL_ROLE | matched list | current values safe | recomputed facts summarized | CWD/context/cache | Yoga | none | High | P0 |
| `systems/Parasara/engine/rules/engine.py:142-159` | `evaluate_condition` | logical caller | child evidence lists/dicts | inherited | child references | tree/input order | Yoga | positional wrapper only | High | P0 |
| `systems/Parasara/engine/enrichments/yoga_engine.py:150-186` | `evaluate_yoga_rules` | Yoga | evidence/custom dicts | inherited | shared predicate evidence | UUID/set/registry | custom Yoga result; snapshot currently empty | none | High | P1 |
| `systems/Parasara/engine/interpreters/career.py:55-64` | `interpret_career` | Career | nested legacy evidence | inherited | shared runtime context/evidence | loader/candidate state | public domain JSON | matched-positive filter | High | P1 |
| `tests/rules/test_predicate_result.py:67-74` | serialization test | complete result | `asdict` copy | masked by `default=str` | arbitrary becomes string | repr/order | test only | none | Medium | P2 |

Six public/serialization impacts are counted: complete-result debug/asdict; condition aggregate shape; Yoga custom output; Career indicators/evidence; snapshots/artifacts; runner/API/frontend JSON. Immutable mappings/tuples and stable IDs may change list/mapping forms and ordering, so an explicit compatibility serializer is required.

## 19. Existing Tests and Coverage Gaps

Existing direct tests prove PLANET_IN_HOUSE can match and cache, PLANET_EXALTED can return false, handler exceptions create an error list, and PredicateResult can be serialized using `default=str`. They do not inspect factual evidence. Yoga tests assert only that evidence is a dictionary. Career tests inspect rule ID/contribution presence, not factual completeness.

| Area | Missing Categories | Count | Risk | Recommended Test File |
|---|---|---:|---|---|
| Per-predicate evidence | matched; unmatched; expected/actual; missing capability; invalid parameters; errors; semantic correctness | 7 | false/missing/error facts remain indistinguishable | `tests/rules/test_predicate_evidence.py` |
| Model safety | deep immutability; defensive copy; JSON safety; canonical order; deterministic serialization; unsupported values | 6 | cache/public evidence can mutate or stringify unpredictably | `tests/rules/test_evidence_model_safety.py` |
| Aggregation/propagation | condition aggregation; short-circuit/skipped; Yoga preservation; domain preservation; output serialization; cold/warm equivalence | 6 | evidence disappears between layers | `tests/rules/test_evidence_propagation.py` |
| Priority predicates | exaltation placement; Aspect missing-vs-empty; house unmatched actual; prepared role evidence; actual occupants | 5 | high-value semantic/evidence defects remain unguarded | `tests/rules/test_priority_predicate_evidence.py` |

Missing evidence test categories: **24**. No prescribed category has adequate current coverage.

## 20. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Complete factual matched evidence | `NONCOMPLIANT` | 0/6 complete | predicates | per-predicate approved shapes | `IN_SCOPE` | P0 | Yes |
| Useful unmatched evidence | `MISSING` | all six return `{}` | predicates | actual/expected/entity observations | `IN_SCOPE` | P0 | Yes |
| Missing capability distinct from false | `NONCOMPLIANT` | 14 conflations | predicates/engine/Yoga | typed status/error plus capability evidence | `IN_SCOPE` | P0 | Yes |
| Correct PLANET_EXALTED fact/evidence | `UNKNOWN` | mapping existence implies match | exaltation predicate/config | SME-approved semantic review and evidence | `IN_SCOPE` | P0 | Yes |
| Deep immutable evidence | `NONCOMPLIANT` | seven mutable mechanisms | result/cache/callers | deep freeze/defensive normalize | `IN_SCOPE` | P0 | Yes |
| Stable canonical entity identity | `MISSING` | display names only | predicates/AstroState | canonical IDs and alias policy | `IN_SCOPE` | P0 | Yes |
| Preserve child evidence with identity | `NONCOMPLIANT` | anonymous evidence lists | condition | typed child-linked result | `IN_SCOPE` | P0 | Yes |
| Explicit expected/actual/comparison values | `MISSING` | six IDs incomplete | predicates | approved evidence schemas | `IN_SCOPE` | P1 | Yes |
| JSON-safe canonical evidence | `PARTIAL` | normal shapes safe; contract unrestricted | model/predicates/serializer | validate/canonicalize supported values | `IN_SCOPE` | P1 | Yes |
| Deterministic evidence ordering | `PARTIAL` | graph/role/cache mechanisms | predicates/enrichments/cache | canonical source/order/version | `IN_SCOPE` | P1 | Yes |
| Invalid/error diagnostics outside evidence | `NONCOMPLIANT` | four reason shapes | evaluator/condition | typed error/status separation | `IN_SCOPE` | P1 | Yes |
| Preserve evidence through Yoga | `NONCOMPLIANT` | two loss paths | Yoga/condition | typed identity-preserving adapter | `IN_SCOPE` | P1 | Yes |
| Preserve domain-relevant factual evidence | `NONCOMPLIANT` | two Career loss paths | runtime/Career | compatibility path preserving valid output | `IN_SCOPE` | P1 | Yes |
| Cold/warm evidence equivalence/isolation | `NONCOMPLIANT` | shallow shared cache value | engine/cache | immutable value and safe identity | `IN_SCOPE` | P1 | Yes |
| Evidence-focused acceptance tests | `MISSING` | 24 categories | tests | focused suites | `IN_SCOPE` | P1 | Yes |
| Preserve current public compatibility deliberately | `PARTIAL` | snapshot/API fan-out | serializers/output | explicit adapter/schema decision | `TEMPORARY_COMPATIBILITY` | P2 | No |
| Resolve canonical AspectGraph evidence source | `UNKNOWN` | list/dict shape collision | normalizer/aspects/predicates | approved capability/source contract | `IN_SCOPE` | P2 | No |
| Eliminate predicate-time role recomputation | `NONCOMPLIANT` | FUNCTIONAL_ROLE computes roles | predicate/enrichment pipeline | prepared capability consumption | `IN_SCOPE` | P2 | No |
| Source/rule/version provenance in evidence | `MISSING` | no versions/config IDs | loader/registry/predicates | metadata propagation | `IN_SCOPE` | P2 | No |
| Universal RuleMatch evidence linkage | `MISSING` | legacy/custom rule dicts | future rule engine | Prompt-02 | `OUT_OF_SCOPE_FUTURE_STAGE` | P3 | No |
| Typed public explainability/output schema | `MISSING` | direct dictionaries | future inference/output | later architecture stages | `OUT_OF_SCOPE_FUTURE_STAGE` | P3 | No |

## 21. Migration Risks and Priorities

The 21 findings total **P0=7, P1=8, P2=4, P3=2**.

P0 blocks truthful implementation: matched/unmatched/capability evidence, exaltation correctness review, deep immutability, stable identity, and child-linked preservation. P1 completes expected/actual values, canonical JSON safety/order, diagnostic separation, Yoga/domain/cache propagation, and tests. P2 protects public compatibility and resolves source/provenance concerns. P3 is reserved for later RuleMatch and output architecture.

Changing evidence can expose current semantic differences and alter cache equality, Yoga derived fields, Career snapshots, and API JSON. Valid factual outcomes must be preserved unless the approved semantic review confirms a defect. Empty false evidence is current behavior but must not be mistaken for an architectural compatibility requirement to hide unavailable facts.

## 22. Unresolved Architectural Questions

1. What per-predicate minimum evidence schema is approved for matched, unmatched, missing entity, and missing capability?
2. What are the authoritative PLANET_EXALTED sign/longitude/degree/orb rules and configuration source?
3. Which Aspect representation/version is canonical, and may target-`None` trace edges satisfy ASPECT_EXISTS?
4. Are canonical planet IDs mandatory in evidence while display names remain optional labels?
5. Where are functional roles prepared, versioned, and exposed without recomputation?
6. Does HOUSE_OCCUPANT evidence use the requested planet's actual house, the full occupant set, or both?
7. How are logical child identity/path and skipped evidence represented without conflating it with predicate evidence?
8. Which temporary Yoga/Career/public fields must remain byte/shape compatible during deep-freeze migration?
9. Which evidence values are part of logical equality versus diagnostic/telemetry projection?
10. How are entity absence and incomplete-but-present capabilities distinguished from missing capability?

These questions affect implementation but do not block completion of Audit-18.

## 23. Audit-18 Conclusion

Audit-18 is COMPLETE. Six registered IDs were audited: zero have complete matched evidence, zero have complete unmatched evidence, all six are matched-only, and none lacks every evidence-producing path. Six miss explicit expected/actual observations; seven misleading paths and one suspected semantic error were identified. Fourteen capability/entity conflations remain. Evidence has seven mutability mechanisms, one non-JSON-safe risk class, four nondeterministic mechanisms, three condition loss paths, two Yoga loss paths, two domain loss paths, one reachable cold/warm difference, six serialization impacts, and twenty-four missing test categories. Exactly this report was created; no code, tests, rules, fixtures, snapshots, previous reports, or Audit-19 artifacts were modified.

### Summary counts

| Metric | Count |
|---|---:|
| Registered predicates audited | 6 |
| Predicates with complete matched evidence | 0 |
| Predicates with complete unmatched evidence | 0 |
| Matched-only evidence predicates | 6 |
| Predicates without evidence | 0 |
| Predicates missing expected or actual values | 6 |
| Misleading evidence paths | 7 |
| Suspected semantic errors | 1 |
| Missing-capability evidence conflations | 14 |
| Invalid-parameter/exception data stored as evidence | 4 |
| Unstable identity uses | 6 |
| Mutable evidence risks | 7 |
| Non-JSON-safe evidence risks | 1 |
| Nondeterministic evidence mechanisms | 4 |
| Condition evidence-loss paths | 3 |
| Yoga evidence-loss paths | 2 |
| Domain evidence-loss paths | 2 |
| Cold/warm evidence differences | 1 |
| Public serialization impacts | 6 |
| Missing evidence test categories | 24 |
| P0 findings | 7 |
| P1 findings | 8 |
| P2 findings | 4 |
| P3 findings | 2 |
