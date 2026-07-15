# Prompt-01 Audit-15: Yoga Engine

## 1. Executive Summary

Yoga has one active execution path. It loads raw YAML rule dictionaries, performs mutable enrichment preparation, clears the global predicate cache, evaluates each condition through the canonical generic evaluator and central registry, reduces the result to `.matched` plus `.evidence`, creates a custom mutable dictionary with a random UUID trace ID, stores the list in `astro.enrichments['yogas']`, and returns it.

The path is `GENERIC_PATH_WITH_INFORMATION_LOSS`, not generic-compliant. Status, typed errors, condition traces, child results, cache telemetry, predicate versions, and evaluation order are discarded. Missing capabilities, invalid parameters, unknown predicates, and predicate errors become ordinary Yoga non-matches. The active YAML contains unregistered `HOUSE_LORDS_COMBINATION`, so one current Yoga branch is already misclassified as factual false.

Five Yoga-local tuple-return helpers form a dormant parallel evaluator; all are `CONFIRMED_UNUSED`. Three factual helpers duplicate registered predicates with semantic/evidence differences. Active Yoga also has four enrichment-recomputation paths, three AstroState-mutation paths, four cache/staleness risks, and six nondeterministic mechanisms. Findings total **7 P0, 8 P1, 4 P2, and 2 P3**.

## 2. Audit Scope and Method

The audit read the Master Architecture, Prompt-01, Audits 1–14, all Yoga sources/loaders/rules/evaluators, registered predicates, enrichment implementations, callers, tests, snapshots, tools, and current/target documentation. Repository-wide symbol/reference searches proved active and unused paths and identified the stale test API.

No Yoga evaluation or enrichment was executed because the audit forbids mutation/cache clearing and the environment lacks project `yaml`, `pydantic`, and `pytest` dependencies. Static control/data-flow evidence is complete enough for the requested audit.

## 3. Reconciliation with Audits 1–14

Audit-1 establishes Yoga's explicit predicate-module import and central registry path. Audits 2–3 identify five Yoga tuple helpers and three factual duplicates. Audit-4 proves `evaluate_yoga_rules -> evaluate_condition` and no active tuple caller. Audits 5–8 establish missing typed status/error/capability models. Audits 9–10 identify Yoga mutation, CWD dependencies, repeated role computation, UUID/set nondeterminism, and unsafe purity boundaries. Audit-11 establishes global clear and unsafe leaf caching. Audit-12 proves eager/lossy AND/OR. Audit-13 identifies the active Yoga format. Audit-14 adds raw loading, duplicate rule IDs, no validation, and the stale imported `RULE_REGISTRY` risk.

All fourteen expected reports are present. Audit-15 confirms their Yoga findings and adds detailed evidence/trace/derived-field/test compatibility consequences.

## 4. Yoga Component Inventory

| Component | File | Symbol | Category | Responsibility | Inputs | Outputs | Loader | Evaluator | Predicate Integration | Mutation | Cache Interaction | Callers | Status | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Yoga rule source | `systems/Parasara/rules/parashara/v1/yogas.yaml:4-82` | three rules | YOGA_RULE_SOURCE | declarative Yoga definitions | YAML | raw rule list | Yoga/generic loaders | generic path | four IDs, one unregistered | none | leaf params affect keys | loader/runtime | active production | loader/integration |
| Yoga loader | `engine/rules/yoga_loader.py:7-45` | `_load_yaml`, `validate_yoga_rule`, `load_yoga_rules` | YOGA_LOADER | parse/top-level checks/register | path/YAML | mutable raw dicts | self | none | no predicate validation | global registry | none | Yoga/tests | active production | top-level only |
| Active Yoga evaluator | `engine/enrichments/yoga_engine.py:128-188` | `evaluate_yoga_rules` | YOGA_EVALUATOR; YOGA_EVIDENCE_ASSEMBLER | prepare/evaluate/build/store | mutable AstroState/global rules | list of custom dicts | Yoga loader | `evaluate_condition` | indirect central registry | yes | global clear/leaves cached | public re-export/test | active production | one rule-driven test |
| Public Yoga API | `engine/enrichments/yoga.py:1-3` | `evaluate_yoga_rules` re-export | CALLER_OR_CONSUMER | import surface | function | function | N/A | same | same | same | same | test/external | active production surface | one test |
| Generic bridge | `engine/rules/engine.py:54-162` | `evaluate_condition`, `evaluate_predicate` | ENRICHMENT_OR_PREPARATION | logical/leaf execution | raw node/state/context | `PredicateResult` | none | canonical | dynamic registry | cache mutation | reads/writes cache | Yoga | active production | leaf only |
| Legacy logical helper | `yoga_engine.py:102-125` | `_eval_condition` | LEGACY_CONDITION_HELPER | recursive AND/OR/local dispatch | node/state/context | `(bool, dict)` | none | self | bypass/local helpers | none directly | none | self only | confirmed unused | none |
| Legacy aspect helper | `yoga_engine.py:22-52` | `_eval_aspect_condition` | LEGACY_CONDITION_HELPER | aspect fact | params/state/context | tuple | none | local | duplicates ASPECT | none | none | legacy dispatcher | confirmed unused | none |
| Legacy role helper | `yoga_engine.py:55-67` | `_eval_functional_role_condition` | LEGACY_CONDITION_HELPER | role fact/recompute | params/state/context | tuple | none | local | duplicates FUNCTIONAL_ROLE | no state write | none | legacy dispatcher | confirmed unused | none |
| Legacy lord helper | `yoga_engine.py:70-91` | `_eval_house_lords_combination` | LEGACY_CONDITION_HELPER | mutual lord fact | params/state/context | tuple | none | local | no registered equivalent | none | none | legacy dispatcher | confirmed unused | none |
| Legacy occupant helper | `yoga_engine.py:94-99` | `_eval_house_occupant` | LEGACY_CONDITION_HELPER | occupant fact | params/state/context | tuple | none | local | duplicates HOUSE_OCCUPANT | none | none | legacy dispatcher | confirmed unused | none |
| Varga preparation | `engine/enrichments/varga.py:188-222` | `integrate_vargas_into_astro` | ENRICHMENT_OR_PREPARATION | compute/attach vargas | AstroState | same state | N/A | N/A | later facts | enrichments/planets | invalidates identity assumptions | Yoga/tests | active | varga tests, indirect Yoga |
| Aspect preparation | `engine/enrichments/aspects.py:24-104` | `compute_aspect_graph` | ENRICHMENT_OR_PREPARATION | compute/attach graph | AstroState/CWD table | graph | N/A | N/A | ASPECT reads it | enrichments | invalidates prior aspect cache | Yoga/tests | active | aspects/Yoga |
| Role preparation | `engine/enrichments/functional_roles.py:16-162` | `compute_functional_roles` | ENRICHMENT_OR_PREPARATION | compute table/heuristic roles | state/CWD YAML | dict | N/A | N/A | FUNCTIONAL_ROLE recomputes it | no attach | config absent from key | Yoga/predicate/local helper | active | role tests |
| Rule-driven Yoga test | `tests/enrichments/test_yoga_engine_rule_driven.py:17-37` | test function | TEST_OR_FIXTURE | smoke integration | fixture | assertions | Yoga loader | public API | indirect | prepares/mutates | indirectly clears | pytest | active test | self |
| Yoga loader test | `tests/enrichments/test_yoga_loader.py:5-26` | three tests | TEST_OR_FIXTURE | load/top-level check | YAML/dict | assertions | Yoga loader | none | none | global rule registry | none | pytest | active test | self |
| Stale Yoga consumer test | `tests/enrichments/test_integration_aspects_consumers.py:16-54` | test function | TEST_OR_FIXTURE | aspect/Yoga integration | fixture | assertions | none | nonexistent API | none | preparation | none | pytest | stale/broken reference | self |
| Coverage/output consumers | `tests/testing_framework/coverage_engine.py:23-76`; `tools/generate_snapshot.py:14-40` | ingestion/assembler | CALLER_OR_CONSUMER | consume or reserve Yoga output | dict/AstroState | coverage/public dict | none | none | none | reads; assembler hardcodes empty | none | reports/snapshots | partial/non-integrated | indirect |
| Yoga architecture/docs | `Documentation/architecture/current-state.md:68-77,126-135`; `specifications/rules.md:27-31` | current/target contracts | DOCUMENTATION | describe boundary | source evidence | Markdown | N/A | N/A | target central path | N/A | N/A | maintainers | documentation | N/A |

Yoga component count: **18**.

## 5. End-to-End Yoga Execution Paths

| Entry Point | Rule Source | Loader | Condition Format | Evaluator | Predicate Dispatch | Intermediate Contract | Final Contract | Evidence | Errors | Trace | Mutation | Cache | Consumers | Classification | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `yoga.evaluate_yoga_rules` | `yogas.yaml`/shared registry | specialized Yoga loader when imported registry empty | `conditions -> type/children/type/params` | generic `evaluate_condition` | `evaluate_predicate`/central registry | leaf/logical `PredicateResult` | `list[dict]` plus state storage | immediate evidence retained; derived fields lossy | discarded | discarded/replaced by UUID | preparation + final store | global clear then shared leaf cache | test/public caller | GENERIC_PATH_WITH_INFORMATION_LOSS | P0 |
| dormant `_eval_condition` | caller-supplied raw node | none | exact-uppercase F1 subset | local recursion | four local tuple helpers | `(bool, dict)` | tuple | dict only | no channel | none | role computation only | none | no external caller | LEGACY_PARALLEL_PATH | P2 |
| stale test `detect_yogas_from_aspect_graph` | none | none | N/A | nonexistent symbol | none | none | exception | none | AttributeError expected | none | prior prep | none | test only | TEST_ONLY_PATH | P2 |

Active Yoga execution-path count: **1**. Generic-compliant paths: **0**; generic paths with information loss: **1**; legacy parallel paths: **1**; active direct predicate bypasses: **0**.

The active flow is: public function -> conditional raw Yoga load -> varga/aspect/role preparation -> global cache clear -> ordered registry loop -> generic condition/predicate evaluation -> custom Yoga dictionary -> `astro.enrichments['yogas']` -> return. No domain/public output pipeline currently invokes this function automatically.

## 6. Generic Condition-Evaluator Integration

`evaluate_yoga_rules` passes `rule['conditions']`, the AstroState, and `{}` context to `evaluate_condition` (`yoga_engine.py:150-156`). It expects a `PredicateResult`, reads `.matched` and `.evidence`, and never tuple-unpacks. This is the correct generic call site but an incomplete consumer.

It discards `.errors`, `.trace_steps`, `.cache_hit`, `.evaluation_time_ms`, inputs, and logical child identity; current models have no status/version. Consequently unmatched, missing capability, invalid parameter, unknown definition, and error are indistinguishable. The condition evaluator has already converted logical nodes into predicate-shaped results and stripped full children (Audit-12).

## 7. Predicate Registry Integration

Active leaves delegate through `evaluate_predicate` and `PREDICATE_REGISTRY`; Yoga imports `rules.predicates` for decorator side effects (`yoga_engine.py:6-7`). No active Yoga code calls a registered handler directly. Versions, schemas, required capabilities, and aliases are not validated.

`ASPECT` resolves through the ASPECT/ASPECT_EXISTS alias but returns result identity `ASPECT_EXISTS`. `FUNCTIONAL_ROLE` and `HOUSE_OCCUPANT` resolve centrally. `HOUSE_LORDS_COMBINATION` is not registered, so the active Dhana rule's first OR child becomes cached unmatched rather than invoking the similarly named dormant helper (`yogas.yaml:38-48`).

## 8. Legacy Yoga Evaluators

| File | Symbol | Signature | Return Contract | Responsibility | Duplicate Predicate | Confirmed Callers | Execution Status | Evidence | Errors | Trace | Migration Required | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `yoga_engine.py:102-125` | `_eval_condition` | `(node, astro, context)` | `LEGACY_TUPLE` | eager AND/OR/local dispatch | generic logical evaluator | self-recursion only | CONFIRMED_UNUSED | anonymous children | none | none | remove/retire after semantic resolution | P2 |
| `yoga_engine.py:22-52` | `_eval_aspect_condition` | `(params, astro, context)` | `LEGACY_TUPLE` | aspect fact | ASPECT/ASPECT_EXISTS | local dispatcher only | CONFIRMED_UNUSED | matched edges/planets | swallowed edge errors | none | retire; do not activate | P1 |
| `yoga_engine.py:55-67` | `_eval_functional_role_condition` | same | `LEGACY_TUPLE` | role fact | FUNCTIONAL_ROLE | local dispatcher only | CONFIRMED_UNUSED | matched planets, including empty list | none | none | retire | P1 |
| `yoga_engine.py:70-91` | `_eval_house_lords_combination` | same | `LEGACY_TUPLE` | mutual-lord fact | none registered | local dispatcher only | CONFIRMED_UNUSED | lord/reason dicts | none; unsafe `getattr(None)` possible | none | decide registered semantics separately | P0 |
| `yoga_engine.py:94-99` | `_eval_house_occupant` | same | `LEGACY_TUPLE` | occupant fact | HOUSE_OCCUPANT/PLANET_IN_HOUSE | local dispatcher only | CONFIRMED_UNUSED | requested fact even false | none | none | retire | P1 |

Legacy tuple-return helpers: **5**; confirmed unused: **5**; unknown usage: **0**. Repository-wide calls find only the local dispatcher/self-recursion. There is no active or test fallback to them.

## 9. Duplicate Predicate Logic

Three Yoga factual implementations duplicate registered predicates:

- Aspect: local helper rejects edges missing source/target, supports only house filters, returns matched planets, and always exposes empty-list evidence; registered ASPECT supports planet filters, may accept target-`None` edges when filters permit, returns ID `ASPECT_EXISTS`, and returns `{}` when unmatched (`yoga_engine.py:22-52`; `predicates.py:12-47`).
- Functional role: both recompute roles and honor candidate context, but local unmatched evidence is `{'matched_planets': []}` while registered unmatched evidence is `{}` (`yoga_engine.py:55-67`; `predicates.py:70-82`).
- House occupant: factual comparison is equivalent, but local always emits requested planet/house while registered emits evidence only on match (`yoga_engine.py:94-99`; `predicates.py:60-67`).

`_eval_house_lords_combination` is unique missing central functionality, not counted as a duplicate. Duplicate predicate implementation count: **3**. Activating the local path would change matching/evidence and reintroduce tuple contracts.

## 10. Return Contracts and Information Loss

Active contracts are raw rule dict -> predicate/logical `PredicateResult` -> Yoga custom dict. No `ConditionResult` or Yoga model exists. The final dictionary preserves `yoga_id`, name, boolean match, selected planet/house/aspect fields, raw condition evidence, and random trace ID. It omits rule version/category/weights/provenance/approval, predicate identity/version/status/errors/traces/children/cache/timing.

Counted loss paths include the active generic aggregation/Yoga conversion and dormant tuple parallel path: status-loss **2**, evidence-loss **2**, error-loss **2**, trace-loss **3**. Trace has one extra active loss because condition traces are first reduced by generic aggregation and then wholly discarded by Yoga before UUID replacement.

## 11. Status and Error Semantics

Yoga treats every `matched=False` identically. It has no place for missing capability, invalid parameters, timeout, skipped, or recoverability. Predicate errors may remain in `pr.errors`, but Yoga never reads/stores them. Preparation errors for varga/aspect and role computation are broadly swallowed; rule-load errors are silently skipped; final state-storage errors are swallowed.

Yoga therefore emits invalid/unavailable/error rules as ordinary unmatched Yoga dictionaries. Status precedence for mixed AND/OR and Yoga exposure remains unresolved and must follow the typed condition decisions from Audit-12.

## 12. Evidence Quality and Preservation

Yoga retains `pr.evidence` in the final dictionary, including unmatched evidence where predicates provide it. However, logical evidence is anonymous ordered `children` dictionaries without predicate IDs or stable nodes. Existing registered predicates often return `{}` on false, so expected/actual and missing-capability facts are unavailable.

Derived fields are lossy or misleading for current logical roots: `planets` flattens only one child level; `aspects_used` reads only root `matched_edges`, so nested Aspect evidence is missed; `houses` reads `conditions.params.houses`, but current roots are logical nodes with no params. Full raw evidence remains present, but these convenience fields can be empty despite relevant child evidence. `list(set(...))` makes planet ordering nondeterministic. Evidence and nested edge objects are mutable and lack stable AstroState IDs.

## 13. Trace and Determinism

Yoga discards predicate/condition trace steps and creates one UUID4 per emitted rule, including nonmatches (`yoga_engine.py:14-15,169-179`). There is no parent-child lineage, rule version, node path, skipped-branch record, cache hit, or evaluation-order trace. Predicate/condition timing uses `perf_counter` but is discarded.

Six nondeterministic mechanisms are counted:

1. UUID4 trace IDs (`TRACE_ONLY_NONDETERMINISM`).
2. set-to-list planet aggregation (`EVIDENCE_NONDETERMINISM`).
3. mutable/unsorted rule-registry load and iteration (`LOGICAL_NONDETERMINISM`).
4. performance timings in discarded intermediate results (`PERFORMANCE_ONLY_NONDETERMINISM`).
5. CWD/file-dependent aspect and functional-role configuration (`LOGICAL_NONDETERMINISM`).
6. global registry/cache/state lifecycle and import order (`LOGICAL_NONDETERMINISM`).

Identical inputs do not guarantee identical serialized Yoga output, even when matched booleans happen to remain equal.

## 14. Enrichment Preparation and Recomputation

| File | Symbol | Operation | Enrichment/Field | Lifecycle Stage | Direct/Indirect | Mutates AstroState | Order Dependent | Cache Risk | Tests | Classification | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `yoga_engine.py:134-139`; `varga.py:188-222` | `evaluate_yoga_rules` -> `integrate_vargas_into_astro` | recompute/attach D3/D7/D9/D30 and planet vargas | `enrichments.vargas`, `PlanetState.vargas` | Yoga entry before conditions | indirect | Yes | Yes | invalidates earlier state-based entries | tests also precompute | MUST_FIX_IN_PROMPT_01 | P0 |
| `yoga_engine.py:134-139`; `aspects.py:24-104` | Yoga -> `compute_aspect_graph` | recompute/replace graph | `enrichments.aspects` | before conditions | indirect | Yes | Yes; replaces normalizer basic list | invalidates earlier ASPECT results | tests precompute then Yoga recomputes | MUST_FIX_IN_PROMPT_01 | P0 |
| `yoga_engine.py:141-145` | `compute_functional_roles` | compute then discard result | none attached | before conditions | direct | No | CWD/config dependent | config not keyed | no Yoga assertion | MUST_FIX_IN_PROMPT_01 | P0 |
| `predicates.py:70-82` | `functional_role` | recompute per uncached parameter set | returned evidence | during condition evaluation | indirect through registry | No | rule/cache order dependent | unsafe context/config cache | indirect only | MUST_FIX_IN_PROMPT_01 | P0 |
| `yoga_engine.py:181-186` | final storage | attach Yoga results | `enrichments.yogas` | after all conditions | direct | Yes | downstream-state dependent | state digest absent | rule-driven test not asserting store | FUTURE_ARCHITECTURE_STAGE | P2 |

Active enrichment-recomputation paths: **4**. `compute_planet_strengths` is imported by Yoga but never called. Tests precompute vargas/aspects before Yoga, proving redundant recomputation in that path.

## 15. AstroState Mutation

Three active mutation paths exist: varga integration (both enrichment and planet subobjects), aspect-graph attachment/replacement, and final Yoga-result attachment. Preparation happens before cache clearing and predicate evaluation; final Yoga storage happens afterward. Functional roles are computed but not stored.

The evaluator both returns matches and mutates the input state. Evaluation order matters because normalizer/test aspect data may be replaced, earlier non-Yoga predicate cache entries become stale until Yoga's global clear, and other concurrent consumers can observe partial/prepared/final state. No test proves isolation, idempotence, or absence of stale observations.

## 16. Predicate Cache Interaction

Yoga calls `clear_cache()` exactly once after enrichment/role preparation and before iterating rules (`yoga_engine.py:147-154`). Leaves then share the global cache across Yoga rules; logical nodes are recomputed. Four cache risks are counted:

1. global clear races and destroys unrelated request/test entries;
2. invalidation is caller-specific and depends on preparation order;
3. keys omit state digest, predicate/version, capability/config, and context identity;
4. unmatched/error/missing-capability results are cached and can remain sticky across Yoga rules.

Yoga discards `cache_hit`, so cold/warm observation is unavailable. Final `yogas` mutation is not represented in the key, and no scoped run cache exists.

## 17. Yoga Rule Loading and Validation

Yoga uses its specialized YAML loader, not the generic directory loader when its imported registry appears empty. It checks only top-level field presence and registers raw dicts into the shared global rule registry. Duplicate Yoga IDs last-win; IDs/types/values/versions/provenance/approval are not validated; predicate IDs, parameters, capabilities, operators, and arity are wholly unchecked.

The direct imported `RULE_REGISTRY` can become stale when the generic loader rebinds its module global (Audit-14). Parse/validation failures silently remove rules. No JSON/Python Yoga rule path is active. F1 syntax must be preserved during Prompt-01, but raw validation failures must not remain factual nonmatches.

## 18. Downstream Compatibility

| Consumer | File | Yoga API/Field Used | Expected Contract | Evidence Use | Error Use | Ordering Dependency | Mutation Dependency | Serialization Impact | Regression Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Public re-export callers | `engine/enrichments/yoga.py:1-3` | function/list dictionaries | current callable/dict list | unknown external | none available | possible list order | function mutates | custom dict schema | High | P1 |
| Rule-driven Yoga test | `tests/enrichments/test_yoga_engine_rule_driven.py:17-37` | IDs/evidence type/trace presence | three emitted rows | dict type only | none | set of IDs removes order | preparation mutation | random trace only presence | Critical | P0 |
| Aspect consumer test | `tests/enrichments/test_integration_aspects_consumers.py:16-37` | nonexistent `detect_yogas_from_aspect_graph` | list with trace/aspects | aspects only | none | first element if any | requires attached graph | stale API cannot run | High | P2 |
| Coverage engine | `tests/testing_framework/coverage_engine.py:23-76` | diagnostics/enrichments yogas; ID/name/yoga_id | list of dicts | ID only | none | set aggregation | reads stored/output | field-name tolerant | Medium | P2 |
| Snapshot/output contract | `tools/generate_snapshot.py:14-40`; snapshots | diagnostics.yogas | currently hardcoded `[]` | none | none | future | ignores state Yoga | populating changes JSON | High | P2 |

Downstream consumers/surfaces at regression risk: **5**. No active domain interpreter or inference service consumes Yoga results. Career separately hard-codes `rajayoga_naive`, a semantic overlap rather than a Yoga-result consumer.

## 19. Existing Tests and Coverage Gaps

Existing Yoga tests prove three files/rules load, top-level missing fields raise, the public evaluator emits the three IDs, evidence is a dict, and random trace IDs are nonempty. They do not assert actual matched outcomes, typed contracts, or deterministic content. One integration test calls a nonexistent Yoga API.

| Area | Missing Categories | Count | Recommended Test File |
|---|---|---:|---|
| Generic integration | generic call, registry use, typed result flow, no handler bypass, no tuple unpack | 5 | `tests/enrichments/test_yoga_generic_contract.py` |
| Match behavior | matched, unmatched, nested semantics, deterministic order, repeated evaluation | 5 | `tests/enrichments/test_yoga_matches.py` |
| Status behavior | missing capability, invalid params, error, timeout, skipped, unmatched distinction | 6 | `tests/enrichments/test_yoga_status.py` |
| Evidence/trace | factual evidence, errors, child results, deterministic trace, no random logical ID | 5 | `tests/enrichments/test_yoga_evidence_trace.py` |
| State/cache | no evaluation mutation, preparation ordering, scoped invalidation, post-enrichment freshness, cold/warm equivalence | 5 | `tests/enrichments/test_yoga_state_cache.py` |
| Legacy enforcement | no active tuples, no duplicate facts, no fallback, no raw booleans | 4 | `tests/enrichments/test_yoga_architecture.py` |

Missing Yoga test categories: **30**.

## 20. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Classification | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Preserve typed condition/predicate contract | NONCOMPLIANT | `.matched`/evidence only | Yoga/engine | consume typed ConditionResult/children | MUST_FIX_IN_PROMPT_01 | P0 | Yes |
| Distinguish statuses/errors | NONCOMPLIANT | every false identical | Yoga/engine | typed status/error handling | MUST_FIX_IN_PROMPT_01 | P0 | Yes |
| Reject unknown Yoga predicate definitions | NONCOMPLIANT | HOUSE_LORDS false | loader/registry | validate/resolve definition | MUST_FIX_IN_PROMPT_01 | P0 | Yes |
| Cache-safe Yoga evaluation | NONCOMPLIANT | global clear/unsafe keys | Yoga/cache | scoped approved cache contract | MUST_FIX_IN_PROMPT_01 | P0 | Yes |
| Freeze preparation before evaluation | NONCOMPLIANT | Yoga mutates state | Yoga/enrichments | explicit preparation lifecycle | MUST_FIX_IN_PROMPT_01 | P0 | Yes |
| No predicate-time enrichment recomputation | NONCOMPLIANT | role recomputed | role predicate/Yoga | prepared capability consumption | MUST_FIX_IN_PROMPT_01 | P0 | Yes |
| Deterministic registry/rule lifecycle | NONCOMPLIANT | stale/global/order risks | loaders/Yoga | bootstrap/snapshot rules | MUST_FIX_IN_PROMPT_01 | P0 | Yes |
| Preserve complete evidence/children | NONCOMPLIANT | anonymous/lossy derived fields | Yoga/condition | retain typed child linkage | MUST_FIX_IN_PROMPT_01 | P1 | Yes |
| Preserve typed errors | MISSING | errors discarded | Yoga | propagate diagnostics/policy | MUST_FIX_IN_PROMPT_01 | P1 | Yes |
| Preserve deterministic traces | NONCOMPLIANT | traces discarded/UUID | Yoga/engine | stable trace lineage | MUST_FIX_IN_PROMPT_01 | P1 | Yes |
| Deterministic short circuit/skips | NONCOMPLIANT | eager/no skips | condition/Yoga | Audit-12 semantics | MUST_FIX_IN_PROMPT_01 | P1 | Yes |
| Validate active Yoga rule contract | MISSING | top-level only | Yoga loader | shared validation | MUST_FIX_IN_PROMPT_01 | P1 | Yes |
| Retire active possibility of local tuple engine | PARTIAL | unused but present | Yoga helpers | remove after migration proof | MUST_FIX_IN_PROMPT_01 | P1 | Yes |
| Validate aliases/versions/capabilities | MISSING | none | registry/loader | metadata-backed checks | MUST_FIX_IN_PROMPT_01 | P1 | Yes |
| Yoga contract tests | MISSING | 30 gaps | tests | focused coverage | MUST_FIX_IN_PROMPT_01 | P1 | Yes |
| Preserve current Yoga dictionary temporarily | PARTIAL | public/test compatibility | Yoga consumers | explicit adapter | TEMPORARY_COMPATIBILITY | P2 | No |
| Separate preparation service | PARTIAL | Yoga owns recomputation | pipeline/Yoga | staged architecture migration | FUTURE_ARCHITECTURE_STAGE | P2 | No |
| Integrate primary output deliberately | MISSING | diagnostics yogas hardcoded empty | assembler | later typed output integration | FUTURE_ARCHITECTURE_STAGE | P2 | No |
| Resolve stale test API | NONCOMPLIANT | nonexistent function | integration test/Yoga API | align after contract decision | TEMPORARY_COMPATIBILITY | P2 | No |
| Universal Yoga/RuleMatch model | MISSING | custom dictionaries | Prompt-02 models | later universal RuleMatch | FUTURE_ARCHITECTURE_STAGE | P3 | No |
| Complete classical/SME Yoga library | MISSING | three naive unapproved rules | rule governance | later scientific stage | FUTURE_ARCHITECTURE_STAGE | P3 | No |

## 21. Migration Risks and Priorities

The 21 findings total **P0=7, P1=8, P2=4, P3=2**. Highest regression risks are changing all-three-row emission or match booleans, activating the dormant house-lords helper to “fix” an unknown predicate, moving enrichment preparation without preserving fact availability, changing global cache warmth/order, replacing random trace/schema fields exposed to callers, and populating currently empty public diagnostics broadly.

Prompt-01 should preserve valid F1 rules and factual outcomes while introducing typed result consumption and an explicit compatibility adapter for Yoga dictionaries. It must not redesign universal RuleMatch or Yoga astrology.

## 22. Unresolved Architectural Questions

1. What registered/versioned semantics replace the dormant `HOUSE_LORDS_COMBINATION` implementation?
2. Which Yoga result statuses are emitted, suppressed, or diagnostic after typed condition evaluation?
3. Where does enrichment preparation occur, and who guarantees a frozen evaluation snapshot?
4. Does Yoga continue returning all evaluated rules or only matches under the future boundary?
5. What temporary Yoga dictionary fields/order must remain stable?
6. What stable trace identity replaces UUID4 before universal RuleMatch?
7. Should Yoga results remain stored on AstroState as well as returned during Prompt-01?
8. How is the stale shared `RULE_REGISTRY` reference eliminated without changing rule selection?

Questions 1–8 affect safe implementation; none blocks completion of this audit.

## 23. Audit-15 Conclusion

Audit-15 is COMPLETE. One active Yoga path uses the correct generic evaluator/registry but loses typed information, mutates state, recomputes enrichments, globally clears an unsafe cache, and emits nondeterministic custom dictionaries. Five tuple helpers are confirmed unused and three duplicate registered facts. Exactly this report was created; no Yoga code, rules, tests, state, cache, previous reports, or Audit-16 artifacts were modified.

### Summary counts

| Metric | Count |
|---|---:|
| Yoga components | 18 |
| Active Yoga execution paths | 1 |
| Generic-compliant paths | 0 |
| Generic paths with information loss | 1 |
| Legacy parallel paths | 1 |
| Direct predicate bypasses | 0 |
| Legacy tuple-return helpers | 5 |
| Duplicate predicate implementations | 3 |
| Confirmed-unused legacy helpers | 5 |
| Helpers with unknown usage | 0 |
| Status-loss paths | 2 |
| Evidence-loss paths | 2 |
| Error-loss paths | 2 |
| Trace-loss paths | 3 |
| Enrichment-recomputation paths | 4 |
| AstroState mutation paths | 3 |
| Cache-clear or stale-cache risks | 4 |
| Nondeterministic Yoga mechanisms | 6 |
| Downstream consumers at regression risk | 5 |
| Missing Yoga test categories | 30 |
| P0 findings | 7 |
| P1 findings | 8 |
| P2 findings | 4 |
| P3 findings | 2 |
