# Prompt-01 Audit-08: Capability Handling

## 1. Executive Summary

Audit-8 is **COMPLETE**. All seven prerequisite reports were present. Six registered predicate IDs were audited against six distinct implicit capabilities: normalized planets, planet-house placement, AspectGraph, Lagna, functional-role facts, and exaltation/dignity facts. The registry declares none of them; all six predicates have implicit dependencies.

Missing capability is never represented as `missing_capability`. Fourteen registered-predicate capability paths can become ordinary unmatched results, and fourteen capability-versus-entity distinctions are conflated. Ten access patterns collapse missing, `None`, empty, false-like, or malformed data.

The highest-risk conflict is `astro.enrichments['aspects']`. Normalization stores the list returned by `compute_basic_aspects` (`systems/Parasara/engine/normalizer.py:134-147`; `enrichments/aspects.py:165-196`), while `ASPECT`/`ASPECT_EXISTS` require a dictionary with an `edges` list (`rules/predicates.py:14-18`). A present list is treated as empty. Yoga later recomputes a different whole-sign AspectGraph and overwrites the same key (`yoga_engine.py:133-138`; `aspects.py:24-100`), so predicate results depend on preparation order.

`FUNCTIONAL_ROLE` recomputes its capability inside the predicate by reading working-directory-dependent YAML or applying a heuristic (`predicates.py:70-82`; `functional_roles.py:16-146`). It neither consumes a declared prepared enrichment nor records the producer/configuration version. Yoga redundantly computes functional roles before invoking the predicate but discards that result (`yoga_engine.py:141-145`).

The cache uses process-local AstroState identity and parameters only. It does not include capability readiness, enrichment content/version, context, or AstroState digest (`rules/engine.py:39-44`). A cached unmatched result can therefore remain after a capability is populated or replaced on the same object. Yoga mitigates only its own path by clearing the entire cache after on-demand preparation (`yoga_engine.py:147-148`).

Five relevant recomputation/mutation operations were found, none governed by capability metadata. No registered predicate or central evaluator directly mutates AstroState, but one predicate recomputes functional roles, and the Yoga caller performs capability recomputation and three state mutations. Findings total **7 P0, 7 P1, 3 P2, and 1 P3**. The principal unresolved question is which versioned Aspect representation is canonical.

## 2. Audit Scope and Method

The audit reviewed the Master Architecture, Prompt-01, Audits 1–7, current AstroState models, normalizer/enrichments, all registered handlers, evaluators/cache, Yoga, loaders, legacy runtime, YAML/JSON, tests, fixtures, tools, and architecture documentation. Searches covered capability metadata/names, enrichment reads and writes, empty defaults, exception fallbacks, on-demand computation, versions, context, cache identity, and capability tests.

Counts use registered IDs separately, so shared `ASPECT` and `ASPECT_EXISTS` behavior counts twice where caller-visible. A capability is counted only when a registered handler actually requires or conditionally relies on prepared factual data. Varga, strength, Dasha, transit, and Yoga facts are not counted because no registered handler consumes them today. Missing-to-unmatched counts use distinct predicate ID/capability paths. Mutation/recomputation counts use distinct operations, not every invocation.

The targeted pytest command was safe and non-generating but did not execute because the available interpreter has no `pytest`. No generator or enrichment function was executed because the audit forbids populating/mutating AstroState.

## 3. Reconciliation with Audits 1–7

Audit-1 found `required_capabilities` missing from callable-only registry metadata. Audit-8 confirms no field, type, name catalog, validation, optional-capability expression, version, loader/runtime consumer, or test-predicate declaration exists (`engine.py:21-32`).

Audit-2 identified the same registered predicates and noted AspectGraph, planet/house, functional-role, and exaltation dependencies. Audit-8 adds the incompatible dual `aspects` representation, exact missing/empty behavior, readiness order, and capability/cache counts. No Audit-2 predicate inventory changes.

Audit-3's legacy runtime remains capability-implicit and sometimes reads `planet_strengths` or `aspects`, but it is a compatibility bypass rather than a registered-predicate capability count. Audit-4 confirms Yoga is the active registered-predicate caller and discards errors/status/trace, so capability failures become downstream nonmatches.

Audit-5 confirms the result cannot express capability version/status and stores mutable evidence/inputs. Audit-6 confirms no `PredicateStatus.MISSING_CAPABILITY`, `PredicateError`, or stable capability error code exists. Audit-7 counts nine parameter/capability boundary violations; Audit-8 expands this into capability-specific paths and distinguishes invalid caller input from absent prepared facts.

No prior conclusion is contradicted. Newly explicit evidence is the normalizer/Yoga AspectGraph shape collision and redundant functional-role computation.

## 4. Capability Definition and Repository Model

`AstroState` has typed top-level `planets`, `houses`, `lagna_sign`, metadata, and an untyped mutable `enrichments: Dict[str, Any]` (`systems/Parasara/engine/astrostate.py:5-35`). It has no capability manifest, readiness state, digest, enrichment provenance/version envelope, completeness map, or freeze boundary.

For this audit:

- normalized planets and their house placements are core factual capabilities;
- AspectGraph is a prepared enrichment, but the repository uses two incompatible values at the same key;
- functional-role facts are logically a prepared capability even though the registered predicate recomputes them;
- Lagna is a source capability needed for meaningful functional-role derivation;
- exaltation/dignity facts are a capability with two undocumented fallback locations;
- optional `context['planets']` is an evaluation-selection input, not a factual capability.

No canonical capability names exist in code. Uppercase names below are audit labels, not proposed implementation constants.

## 5. Complete Capability Inventory

| Capability | Alternate Names | Owner/Producer | AstroState Location | Versioned | Required By | Registry Declared | Availability Check | Missing Representation | Empty Distinguishable | Tests | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `NORMALIZED_PLANETS` | planets, canonical planet IDs | Normalizer / `AstroState` | `astro.planets`; IDs also in enrichments | No | All six IDs | No | `getattr(..., []) or []`; exact lookup | Missing/None/empty all act empty | No | Valid Mars test only | NONCOMPLIANT | P0 |
| `PLANET_HOUSE_PLACEMENT` | `PlanetState.house` | Normalizer/adapter | `astro.planets[].house` | No | Aspect IDs conditionally; `PLANET_IN_HOUSE`; `HOUSE_OCCUPANT` | No | `getattr(p,'house',None)` | Missing entity/house/None collapse | No | Valid house only | NONCOMPLIANT | P0 |
| `ASPECT_GRAPH` | `aspects`, basic-aspect list | `compute_aspect_graph`; conflicting `compute_basic_aspects` | `astro.enrichments['aspects']` | Graph has optional `config_version`; not enforced | `ASPECT`, `ASPECT_EXISTS` | No | Dict check then `.get('edges',[])` | Missing/None/list/malformed/empty become no edges | No | Producer tests, not missing predicate paths | NONCOMPLIANT | P0 |
| `LAGNA` | ascendant, `lagna_sign` | Normalizer | `astro.lagna_sign` | No | `FUNCTIONAL_ROLE` derivation | No | Empty string fallback in producer | Missing/empty/invalid all degrade heuristic | No | Enrichment matrix only | PARTIAL | P1 |
| `FUNCTIONAL_ROLES` | functional role map/table | `compute_functional_roles` and YAML tables | Not stored by handler; recomputed return value | Table/version not captured | `FUNCTIONAL_ROLE` | No | Recompute; missing table -> heuristic | Missing table indistinguishable from intended heuristic mode | No | Producer tests only | NONCOMPLIANT | P0 |
| `EXALTATION_FACTS` | flags.exalted, metadata.exaltations, dignity | Upstream/metadata; no single owner | undeclared `planet.__dict__['flags']` or `astro.metadata['exaltations']` | No | `PLANET_EXALTED` | No | Dict/type/get fallbacks | Missing/None/empty/key absent collapse | No | One ambiguous unmatched test | NONCOMPLIANT | P0 |

Distinct required capability count: **6**. No capability has a complete availability contract. The AspectGraph's `config_version` is the only local version-like field, but the predicate does not inspect or report it.

## 6. Predicate-to-Capability Matrix

| Predicate ID | Required Capability | Optional Capability | Data Access | Declared in Registry | Prechecked | Missing Outcome | Empty Outcome | Recomputed | Mutates State | Error/Evidence | Tests | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ASPECT` | AspectGraph | planets/house placement when house filters used | enrichments `aspects.edges`; planet lookup | No | No | Ordinary unmatched | Ordinary unmatched | No in handler | No | `{}`, no error | Indirect Yoga only | IN_SCOPE | P0 |
| `ASPECT_EXISTS` | AspectGraph | same conditional planet/house facts | same shared handler | No | No | Ordinary unmatched | Ordinary unmatched | No | No | `{}`, no error | No direct test | IN_SCOPE | P0 |
| `PLANET_IN_HOUSE` | planets; house placement | None | `astro.planets`, `PlanetState.house` | No | No | Ordinary unmatched | Ordinary unmatched | No | No | `{}`, no error | Valid true/cache only | IN_SCOPE | P0 |
| `HOUSE_OCCUPANT` | planets; house placement | None | same | No | No | Ordinary unmatched | Ordinary unmatched | No | No | `{}`, no error | Indirect Yoga only | IN_SCOPE | P0 |
| `FUNCTIONAL_ROLE` | planets; Lagna; functional-role facts/config | optional context planet selection | context, planets, filesystem-backed computation | No | No | False, degraded fallback, or caught error | False/degraded fallback | Yes | No direct mutation | `{}` or raw error | Indirect Yoga only | IN_SCOPE | P0 |
| `PLANET_EXALTED` | planets; exaltation facts | flags then metadata fallback | planet `__dict__`; metadata map | No | No | Ordinary unmatched | Ordinary unmatched | No | No | `{}`, no error | Ambiguous Mars false | IN_SCOPE | P0 |

Implicit capability-dependency count is **6 predicates**; declarations count is **0**. No handler records capability name, version, requested missing entity, recoverability, or available alternatives.

## 7. Required-Capability Registry Metadata

`required_capabilities` is wholly absent. The registry cannot express mandatory versus optional dependencies, normalize duplicate names, version capabilities, reject unknown/system-specific names, or validate dependency availability. Registration, rule loaders, runtime evaluator, direct handlers, and the test-only `RAISE_TEST` never handle capability metadata. Import order controls handler availability but cannot validate capabilities.

Capability dependencies do not enter cache keys. Rule loaders cannot statically identify incompatible system/rule combinations. This exactly confirms Audit-1's `required_capabilities` metadata finding.

## 8. Missing, Empty, False and Malformed Data

Ten distinct collapse patterns were found:

1. `getattr(astro,'enrichments',{})` and `.get('aspects',{}) or {}` collapse absent container, `None`, empty, and false-like graph (`predicates.py:16`).
2. A present non-dict Aspect value—including the normalizer's valid list representation—becomes `edges=[]` (`predicates.py:17`).
3. Missing, `None`, and empty `edges` all become `[]`; wrong truthy edge types can be iterated and partially swallowed (`predicates.py:17-36`).
4. `getattr(astro,'planets',[]) or []` collapses missing, `None`, and empty collection (`predicates.py:8-9,73`).
5. `context.get('planets') or all-planets` collapses absent, `None`, and an intentionally empty selection (`predicates.py:74`).
6. Missing/empty/malformed functional-role table falls back to heuristic `{}` mode (`functional_roles.py:16-47,50-146`).
7. Missing, empty, or invalid Lagna all prevent authoritative relative-house derivation but do not stop evaluation (`functional_roles.py:52-94`).
8. Missing/None/empty/malformed planet `flags` all mean no exalted flag (`predicates.py:91-94`).
9. Missing/None/empty/malformed metadata `exaltations` all become `{}` or an exception converted by evaluator (`predicates.py:96-99`).
10. Missing exaltation key and explicit `None` value both mean ordinary unmatched (`predicates.py:97-99`).

Missing-versus-empty conflation count is **10**. Legitimate false and zero receive no explicit policy: `flags['exalted']=False` is indistinguishable from absent flag, while an exaltation degree of `0` is treated as present because the code checks `is not None`.

Malformed Aspect edges are skipped individually by broad `except Exception`, enabling partial evaluation and misleading negative results (`predicates.py:19-36`). No version mismatch is detected. Stale capability data cannot be recognized because no AstroState digest/provenance binds enrichments to state.

## 9. Missing Capability versus Missing Entity

| Predicate | Scenario | Current Behavior | Current Status | Expected Behavior | Evidence Produced | Error Produced | Distinction Preserved | Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|
| Aspect IDs | Graph missing vs graph present/no matching edge | Both no matches | None/unmatched | missing capability vs unmatched | `{}` | None | No | Critical | P0 |
| All six IDs | Planet collection unavailable vs requested/no qualifying planet absent | False or degraded computation | None/unmatched | missing capability vs missing entity/factual false | Usually `{}` | None | No | Critical | P0 |
| Aspect/house IDs | House placement unavailable vs planet not in requested house | Comparison false | None/unmatched | missing data vs unmatched | `{}` | None | No | High | P0 |
| `FUNCTIONAL_ROLE` | Role facts unavailable vs no planet has requested role | False/degraded fallback | None/unmatched | missing capability vs unmatched | `{}` | Sometimes raw error | No | Critical | P0 |
| `PLANET_EXALTED` | Exaltation facts unavailable vs planet not exalted | Both false | None/unmatched | missing capability/data vs unmatched | `{}` | None | No | Critical | P0 |

Expanded by registered ID and dependency, missing-capability-versus-missing-entity conflation count is **14**. The repository has no formal entity-absence semantics; the expected non-capability category for a valid requested planet absent from a complete collection remains unresolved.

## 10. Predicate Fallback and Recomputation

| File | Symbol | Predicate/Caller | Capability | Operation | Recomputes | Mutates AstroState | Order Dependent | Cache Risk | Prompt-01 Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| `rules/predicates.py:70-82` | `functional_role` | `FUNCTIONAL_ROLE` | functional roles | Calls filesystem/heuristic producer inside predicate | Yes | No | Yes, CWD/table/state | Table/version absent from key | IN_SCOPE | P0 |
| `enrichments/yoga_engine.py:133-138` | `evaluate_yoga_rules` | Yoga caller | vargas | Integrates D3/D7/D9/D30 before conditions | Yes | Yes | Yes | Same object identity after mutation | OUT_OF_SCOPE_FUTURE_STAGE | P2 |
| `yoga_engine.py:133-138` | `evaluate_yoga_rules` | Yoga caller | AspectGraph | Computes and overwrites `aspects` | Yes | Yes | Yes | Changes prior cached meaning | IN_SCOPE caller boundary | P0 |
| `yoga_engine.py:141-145` | `evaluate_yoga_rules` | Yoga caller | functional roles | Computes then discards result | Yes | No | CWD/table dependent | Redundant and unversioned | IN_SCOPE caller boundary | P1 |
| `yoga_engine.py:180-186` | `evaluate_yoga_rules` | Yoga caller | Yoga results | Writes result enrichment | No | Yes | Later consumers observe it | Same object/cache identity | OUT_OF_SCOPE_FUTURE_STAGE | P2 |

Relevant recomputation/mutation operation count is **5**. Registered predicates recomputing capabilities: **1**. Registered predicate or central evaluator AstroState mutations: **0**. Yoga caller mutations: **3**. `FUNCTIONAL_ROLE` violates the target prepared-AstroState predicate boundary and makes logical/cache behavior depend on external mutable configuration.

## 11. AstroState Mutation and Evaluation Order

`AstroState` and nested enrichments are mutable Pydantic/dict/list objects. The normalizer populates basic strengths, houses, and list-shaped aspects (`normalizer.py:134-156`). Yoga then integrates vargas, overwrites aspects with a graph, clears the predicate cache, evaluates, and finally writes Yoga results (`yoga_engine.py:133-186`).

Thus mutation occurs in a caller immediately before predicate evaluation, not inside the central evaluator. Results differ depending on whether callers invoke a registered Aspect predicate directly after normalization or through Yoga. Tests manually prepare vargas/aspects before calling Yoga even though Yoga repeats preparation (`tests/enrichments/test_yoga_engine_rule_driven.py:22-27`; `test_integration_aspects_consumers.py:19-29`).

No mutation invalidation hook exists. Yoga's explicit `clear_cache()` protects only this path and globally discards unrelated entries. Other callers can cache a false result, mutate enrichments, and retrieve it as a hit.

## 12. Capability Readiness and Preparation Sequence

There is no enforced sequence equivalent to normalize -> enrich -> freeze -> evaluate. `chart_to_astrostate` performs best-effort enrichment inside broad exception handling and returns mutable partial state (`normalizer.py:134-158`). Direct tests construct partially prepared AstroState and call predicates. Yoga performs on-demand preparation with swallowed exceptions. Domain Career uses separate legacy paths.

Readiness is inferred from container shapes, not explicit. Callers can skip producers, supply incompatible shapes, or mutate after evaluation. No completeness/capability manifest tells a handler whether an empty collection is authoritative or merely unprepared.

## 13. Rule Loader and Compiler Interaction

Capability requirements are unavailable at load time, so generic and Yoga loaders cannot validate them (`loader.py:8-46`; `yoga_loader.py:7-45`). They do not reject rules incompatible with system/plugin capabilities, distinguish static unknown predicate errors from chart-specific runtime absence, or use predicate/capability versions.

Static predicate identity/schema validation belongs to Prompt-01. Chart-specific availability remains a runtime typed result. Full system compatibility planning and AST diagnostics belong to the later compiler, but current loaders must not silently allow every missing dependency to become false.

## 14. Evaluation-Context Capabilities

Only `FUNCTIONAL_ROLE` reads evaluation context: `context.get('planets')` optionally restricts candidates (`predicates.py:73-75`). Absence means all AstroState planets; an explicit empty list also means all planets, so “evaluate none” cannot be expressed. The context value is not declared, validated, included in `PredicateResult.inputs/evidence`, or included in the cache key. Two evaluations with identical state/params but different context can share the same cached result.

No registered predicate reads evaluation instant, timezone, Ayanamsa, transits, Dasha reference time, system/plugin version, normalization version, or enrichment version. No registered predicate defaults to system time.

## 15. Cache and Capability-Version Interaction

Eight capability-related cache risks exist:

1. `id(astro)` replaces a factual AstroState digest.
2. Capability present/absent states are not represented.
3. Enrichment/configuration versions are absent.
4. Mutating/populating a capability retains object identity.
5. Partial/malformed versus complete enrichment is not isolated.
6. `FUNCTIONAL_ROLE` context selection is absent.
7. Functional-role external table/configuration state is absent.
8. Predicate/system/plugin versions are absent.

Missing-capability outcomes are currently cached as unmatched or generic errors. A cached false Aspect result can survive later graph preparation outside Yoga. Cache safety cannot be achieved until capability readiness/version/digest semantics are defined; Audit-11 owns redesign.

## 16. Evidence and Error Quality

Every missing-capability path fails the requested evidence contract:

- predicate ID exists only on the parent result;
- capability name, version, requested missing entity, recoverability, and alternatives are absent;
- stable `MISSING_CAPABILITY`/specific error codes do not exist;
- normal missing paths generally produce `{}` evidence and no error;
- broad producer/handler exceptions are swallowed or converted to raw exception text;
- condition/Yoga aggregation can treat the resulting false as negative rule evidence.

Empty evidence is especially misleading for Aspect and exaltation because it cannot distinguish unprepared facts from evaluated false. No raw stack trace is inserted, but raw exception strings may expose implementation/input details (`engine.py:117-129`).

## 17. Existing Tests and Coverage Gaps

Existing tests cover one prepared true predicate result, AspectGraph production/attachment, functional-role producer outputs, and Yoga's happy-path preparation. They do not assert capability states or typed outcomes. The `PLANET_EXALTED` false test actually lacks a declared exaltation capability, so it entrenches the conflation rather than proving authoritative factual false.

| Area | Missing Categories | Count | Risk | Recommended Location |
|---|---|---:|---|---|
| General capability behavior | present/false; missing; None; empty; malformed; version mismatch; optional absent | 7 | False facts and bad capability data collapse | `tests/rules/test_predicate_capabilities.py` |
| Status/error behavior | missing status; distinct from unmatched; distinct from invalid params; stable code; capability name; recoverability; safe exception | 7 | Consumers cannot route failures safely | `tests/rules/test_predicate_capability_errors.py` |
| Predicate-specific | missing graph; empty graph; missing role facts; missing houses; missing planets; missing varga; missing strength; missing context | 8 | Major capability families unprotected | `tests/rules/test_predicate_capability_matrix.py` |
| Purity/readiness | no predicate recomputation; no mutation; order independence; partial state typed result; preparation before evaluation | 5 | Results depend on caller/order/CWD | `tests/rules/test_predicate_capability_readiness.py` |
| Cache | missing-result isolation; capability-version isolation; enrichment-change isolation; no stale false after preparation | 4 | Stale cached nonmatches | `tests/rules/test_predicate_capability_cache.py` |

Of 32 requested categories, only “capability present and fact true” is adequately exercised by the direct `PLANET_IN_HOUSE` test. Capability-related test-gap count is **31**.

Targeted pytest could not run: `python -B -m pytest ...` reported `No module named pytest`.

## 18. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Required-capability registry metadata | MISSING | Callable-only registry | `engine.py`; `predicates.py` | Declare/validate capabilities | IN_SCOPE | P0 | Yes |
| Typed missing-capability outcome | MISSING | All paths false/error; no status type | handlers; `PredicateResult` | Approved status/error production | IN_SCOPE | P0 | Yes |
| Capability/entity/factual-false distinction | NONCOMPLIANT | 14 conflations | all handlers | Explicit readiness/entity checks | IN_SCOPE | P0 | Yes |
| One canonical AspectGraph contract | NONCOMPLIANT | list vs graph at same key | normalizer; aspects; predicates; Yoga | Approve representation/producer boundary | IN_SCOPE | P0 | Yes |
| Predicate consumes prepared facts only | NONCOMPLIANT | role computation inside handler | `predicates.py`; `functional_roles.py` | Move to approved prepared boundary later | IN_SCOPE | P0 | Yes |
| Readiness before evaluation | MISSING | Caller-dependent on-demand preparation | normalizer; Yoga; evaluator | Explicit enforced preparation contract | IN_SCOPE | P0 | Yes |
| Capability-safe cache identity | NONCOMPLIANT | eight omitted capability inputs | `engine.py`; Yoga | Include approved digest/version/readiness after Audit-11 | IN_SCOPE | P0 | Yes |
| Missing/empty/malformed distinction | NONCOMPLIANT | ten collapse patterns | handlers/producers | Typed availability validation | IN_SCOPE | P1 | Yes |
| Capability/version validation | MISSING | graph version ignored; others absent | enrichments; registry | Versioned capability contract | IN_SCOPE | P1 | Yes |
| Factual capability evidence/errors | MISSING | empty evidence/no errors | handlers; engine | Stable code/details/version/entity | IN_SCOPE | P1 | Yes |
| Rule capability validation | MISSING | loaders cannot inspect dependencies | loaders/registry | Static compatibility checks where knowable | IN_SCOPE | P1 | Yes |
| Evaluation-context declaration/cache | NONCOMPLIANT | context planets hidden from key/result | `predicates.py`; `engine.py` | Declare/validate/identity policy | IN_SCOPE | P1 | Yes |
| Deterministic preparation order | NONCOMPLIANT | normalizer/Yoga overwrite same key | normalizer; Yoga; enrichments | Approved dependency sequence | IN_SCOPE | P1 | Yes |
| Capability behavior tests | MISSING | 31 categories absent | tests | Focused unit/integration/cache tests | IN_SCOPE | P1 | Yes |
| Legacy capability consistency | NONCOMPLIANT | Career runtime uses separate defaults | runtime; Career | Explicit compatibility adapters | TEMPORARY_COMPATIBILITY | P2 | No |
| Safe producer/handler failure handling | NONCOMPLIANT | swallowed exceptions/raw strings | normalizer; Yoga; engine | Typed safe failures/logging boundary | IN_SCOPE | P2 | No |
| Immutable capability snapshot | NONCOMPLIANT | mutable AstroState/enrichments | AstroState; enrichments | Later approved freeze/digest boundary | IN_SCOPE | P2 | No |
| Future system/plugin/time capabilities | MISSING | no representation; unused today | future context/compiler | Define when predicates require them | OUT_OF_SCOPE_FUTURE_STAGE | P3 | No |

## 19. Migration Risks and Priorities

The 18 compliance findings total **P0=7, P1=7, P2=3, P3=1**.

P0 changes can alter Yoga firing and direct Aspect behavior because current callers see different aspect shapes. Capability validation must not arbitrarily choose between conjunction and whole-sign semantics; architecture/SME approval is required. Functional-role migration must preserve the current table/heuristic result while removing CWD and in-predicate computation dependencies.

P1 work establishes availability/malformed/version checks, evidence/errors, loader/context handling, deterministic readiness, and 31 missing test categories. P2 work covers legacy compatibility, safe failures, and snapshot immutability. Future capabilities remain P3.

## 20. Unresolved Architectural Questions

1. Which Aspect representation is canonical: normalizer conjunction list, whole-sign `AspectGraph`, or distinct versioned capabilities/keys?
2. Is an empty authoritative AspectGraph a valid evaluated capability, and how is it distinguished from an unprepared placeholder?
3. What completeness manifest/digest proves normalized planet and house data are authoritative?
4. For a complete planet collection, is an absent requested planet a missing-data result or another approved category?
5. What is the canonical owner/storage/version for functional-role facts, and is heuristic fallback an explicit mode?
6. What is the canonical exaltation/dignity source: typed PlanetState dignity, flags, metadata mapping, or an enrichment?
7. Should an explicit empty `context['planets']` mean “none,” or continue to mean “all”?
8. Which capability/version/readiness fields participate in logical identity and cache keys?
9. Which runtime missing capabilities are recoverable versus system-configuration/compiler errors?

Questions 1, 5, 6, and 8 block safe implementation; this audit does not select astrological semantics.

## 21. Audit-8 Conclusion

Audit-8 is complete and reliable. All seven prerequisite reports were available. No corrections were implemented and Audit-9 was not started.

### Summary counts

| Metric | Count |
|---|---:|
| Registered predicates audited | 6 |
| Distinct required capabilities | 6 |
| Predicates declaring capabilities in registry metadata | 0 |
| Predicates with implicit capability dependencies | 6 |
| Missing-capability-to-unmatched paths | 14 |
| Missing-versus-empty conflations | 10 |
| Missing-capability-versus-missing-entity conflations | 14 |
| Predicates recomputing capabilities | 1 |
| Predicate or evaluator AstroState mutations | 0 |
| Yoga caller capability mutations | 3 |
| Recomputation/mutation operations | 5 |
| Capability-related cache risks | 8 |
| Capability handling test gaps | 31 |
| P0 findings | 7 |
| P1 findings | 7 |
| P2 findings | 3 |
| P3 findings | 1 |

The only modified file is this report.
