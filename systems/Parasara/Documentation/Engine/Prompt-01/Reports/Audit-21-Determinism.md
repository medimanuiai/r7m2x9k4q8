# Prompt-01 Audit-21: Determinism

## 1. Executive Summary

Audit-21 is **COMPLETE**. The authoritative Master Architecture and Prompt-01 DOCX files were read directly, and all twenty prerequisite reports were present. The current repository does not satisfy the Prompt-01 determinism contract.

Twenty distinct nondeterminism sources were found: five logical, three evidence, two error, one trace-only, three cache, four serialization/snapshot, and two performance-only sources. One implicit logical system-clock dependency exists in the predicate-derived Dasha layer; Yoga has one UUID4 dependency; and the predicate cache has one process-identity dependency. Six collection-order paths, three filesystem/import-order dependencies, four mutable-global/test-order dependencies, and four AstroState lifecycle dependencies are material.

All six registered predicate IDs are locally deterministic for fixed, fully prepared inputs, but all six use the central cache keyed by `id(astro)` without an AstroState digest or predicate/capability versions. The current end-to-end classification is therefore `NONDETERMINISTIC` for all six: same-object mutation can return stale matched/evidence content, equivalent AstroState objects cannot share identity, and global cache state affects behavior. Two cold/warm logical-difference mechanisms are reachable: stale same-object results and mutation of shallow-shared cached evidence. Cache-hit and elapsed-time changes are telemetry and are counted separately.

Yoga/domain processing has eight determinism risks, concurrent use has five race/order risks, six serialization/snapshot paths can vary, and twenty-six required determinism test categories are missing. The compliance matrix records 7 P0, 8 P1, 4 P2, and 2 P3 findings. No implementation, test, rule, fixture, snapshot, schema, or prior report was modified.

## 2. Audit Scope and Method

This read-only audit covered registered predicates, the central evaluator and cache, condition aggregation, rule/Yoga loaders, Yoga and Career processing, AstroState construction and mutation, Dasha time fallback, serialization, public output, snapshots, diagnostics, and determinism tests. Searches covered clocks, timers, UUID/randomness, process identity, hashing, sets, environment/CWD access, filesystem enumeration, global state, exception conversion, JSON ordering, floating-point operations, and concurrency mechanisms.

Static analysis traced each candidate to an active or reachable predicate-derived path. Existing reports were reconciled rather than modified. No generator, formatter, snapshot updater, concurrency stress test, or test command that could create repository artifacts was run.

Scope boundaries:

- Surya test-data randomness is seeded and outside the Parasara predicate runtime.
- Snapshot-approval timestamps and CI branch timestamps are tooling metadata, not logical predicate output.
- Performance timers are reported but not classified as logical time.
- Dasha is not used by the six current registered predicates, but is included because it is a predicate-derived domain capability and its clock fallback violates the architecture-wide explicit-time rule.
- Python ordered dictionaries are treated as stable only when their construction source is stable; insertion order is not a substitute for a semantic-order contract.

## 3. Reconciliation with Audits 1–20

All expected reports exist. Audits 1–4 establish six registered IDs over five handlers, mutable registries, import-side-effect registration, and the active Yoga and Career call chains. Audits 5–8 establish mutable nested result data, absent typed status/error/trace models, noncanonical parameters, and caller-dependent capability preparation. Audits 9–10 establish no direct registered-handler mutation but four caller preparation mutations, an absent AstroState digest, a CWD/file-dependent `FUNCTIONAL_ROLE`, and caller-layer UUID/set risks.

Audit-11 classifies all six current predicate IDs as not cache-safe because the key uses object identity, excludes versions/context, and stores shallow mutable results. Audit-12 establishes eager source-order condition evaluation and timing-bearing child summaries. Audits 13–14 establish missing source identity, nondeterministic loader/duplicate behavior, global registry rebinding, and no compilation boundary. Audit-15 supplies six Yoga nondeterminism mechanisms and active AstroState mutation. Audit-16 supplies deterministic current Career ordering only under stable state/rule iteration, with no cold/warm test. Audits 17–19 supply six error mechanisms, four evidence mechanisms, one UUID, three trace ordering paths, and telemetry leakage. Audit-20 supplies six serialization paths. Audit-21 deduplicates overlaps into the twenty-source inventory below while retaining the earlier per-layer counts where explicitly referenced.

No prerequisite-report limitation applies.

## 4. Determinism Contract

The governing logical contract is:

```text
same canonical AstroState content and digest
+ same predicate ID and predicate version
+ same canonical parameters
+ same explicit evaluation context
+ same capability/enrichment/rule-set versions
= same logical PredicateResult
```

Logical identity includes canonical predicate identity/version, status, match, canonical inputs, factual evidence, stable typed error identity/details, and required deterministic trace content. `cache_hit`, elapsed time, performance counters, and explicitly diagnostic timestamps may vary only in a separate telemetry projection. Equivalent states must behave identically across objects and processes; mutation or enrichment changes must change the state identity; evaluation order and cache warmth must not change logical content.

The current model lacks predicate version/status, canonical state identity, canonical parameter/value normalization, typed errors/traces, deep immutability, and a logical serializer. Its equality/debug serialization includes telemetry. The cache and downstream adapters therefore cannot enforce this contract.

## 5. Complete Nondeterminism-Source Inventory

| File | Symbol | Layer | Source | Trigger | Fields Affected | Impact Classification | Repeatability Scope | Cache Impact | Snapshot/Public Impact | Existing Control | Active Path | Tests | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `systems/Parasara/engine/dasha/vimshottari.py:54-66` | `compute_vimshottari` start fallback | Dasha/domain | `datetime.utcnow()` when birth time is missing/invalid | incomplete metadata | Dasha period dates and derived activations | `LOGICAL_NONDETERMINISM` | wall clock/process run | context absent from any future key | domain/public output if used | explicit metadata is preferred | reachable Dasha API; not current six predicates | none for clock injection | `OUT_OF_SCOPE_FUTURE_STAGE` | P2 |
| `systems/Parasara/engine/enrichments/functional_roles.py:16-45`; `rules/predicates.py:70-82` | `_load_table_for_lagna`; `functional_role` | predicate/capability | CWD-dependent YAML lookup and unversioned fallback | `FUNCTIONAL_ROLE` evaluation | matched planets/evidence | `LOGICAL_NONDETERMINISM` | CWD/file deployment | config version absent | Yoga/domain results | fixed fallback algorithm and rounded score | active registered handler | functional-role behavior tests, no CWD/version test | `IN_SCOPE` | P0 |
| `systems/Parasara/engine/rules/loader.py:14-34,44-47` | `load_rules_from_dir`; `register_rule` | loader/registry | unsorted `os.walk`, silent duplicate overwrite | load tree with duplicates/order variation | available rule/winner/order | `LOGICAL_NONDETERMINISM` | filesystem/process/import | selected rule not versioned in predicate key | Yoga/domain/artifacts | dict insertion order after load | active rule/artifact path | basic load/merge only | `IN_SCOPE` | P0 |
| `systems/Parasara/engine/enrichments/yoga_engine.py:1-8,142-151`; `rules/loader.py:14-16` | imported `RULE_REGISTRY`; lazy load | Yoga/registry | stale imported dict after loader rebind plus prior global state | prior loader call/import/test order | Yoga membership/order/matches | `LOGICAL_NONDETERMINISM` | test/process order | Yoga clears only predicate cache | Yoga output/state | lazy nonempty check | active Yoga path | load/count tests only | `IN_SCOPE` | P0 |
| `systems/Parasara/engine/enrichments/yoga_engine.py:142-189`; `normalizer.py:133-155` | `evaluate_yoga_rules`; `chart_to_astrostate` | state lifecycle | enrichment preparation and mutation order | partially prepared/reused AstroState | facts read, matches, state output | `LOGICAL_NONDETERMINISM` | evaluation order/same object | `id(astro)` key remains unchanged | Yoga/domain/snapshot state | Yoga clears cache at run start | active Yoga/normalizer paths | integration tests, no order permutation | `IN_SCOPE` | P0 |
| `systems/Parasara/engine/rules/predicates.py:12-47` | `aspect_exists` | predicate/evidence | source edge list order and live mutable edge dictionaries | equivalent graphs with different order/caller mutation | `matched_edges` evidence | `EVIDENCE_NONDETERMINISM` | object/evaluation order | cached shallow references | Yoga/artifact evidence | list traversal preserves supplied order | active `ASPECT`/`ASPECT_EXISTS` | indirect aspect tests | `IN_SCOPE` | P1 |
| `systems/Parasara/engine/rules/predicates.py:70-82` | `functional_role` | predicate/evidence | candidate/planet input order | context list or equivalent state ordering differs | `matched_planets` order | `EVIDENCE_NONDETERMINISM` | caller/state construction | cached evidence preserves first order | Yoga/domain evidence | source-order append | active handler | no permutation test | `IN_SCOPE` | P1 |
| `systems/Parasara/engine/enrichments/yoga_engine.py:43-52,164-178` | aspect helper and Yoga projection | Yoga/evidence | `list(set(...))` | duplicate/varied matched planets | planets/evidence order | `EVIDENCE_NONDETERMINISM` | process hash seed | indirect cached child evidence | Yoga serialized row | none | active projection at line 173; helper path dormant | only nonempty/type assertions | `IN_SCOPE` | P0 |
| `systems/Parasara/engine/rules/engine.py:117-131` | `evaluate_predicate` exception adapter | predicate/error | raw `str(e)` | identical failure under differing paths/library versions | error message/details | `ERROR_NONDETERMINISM` | environment/version | transient failure is cached | debug/Yoga loss; possible future public output | broad catch prevents crash | active evaluator | exception shape not tested | `IN_SCOPE` | P1 |
| `systems/Parasara/engine/rules/loader.py:19-34`; `yoga_loader.py:10-18,33-43` | loader exception handling | load/error | filesystem-order-dependent failures are swallowed | malformed/unreadable sources | registry and missing diagnostics | `ERROR_NONDETERMINISM` | filesystem/process | changes callable/rule availability | Yoga/domain/artifacts | best-effort continuation | active loaders | missing-field tests only | `IN_SCOPE` | P1 |
| `systems/Parasara/engine/enrichments/yoga_engine.py:14-15,177` | `_make_trace_id` | Yoga/trace | `uuid.uuid4()` | every emitted Yoga row | `trace_id` | `TRACE_ONLY_NONDETERMINISM` | every call/process | no direct key effect | Yoga serialization/public if exposed | none | active Yoga path | asserts only nonempty ID | `IN_SCOPE` | P0 |
| `systems/Parasara/engine/rules/engine.py:37-44` | `_cache_key` | cache | `id(astro)` process/memory identity | all predicate calls | selected logical result and `cache_hit` | `CACHE_NONDETERMINISM` | object/process lifecycle | core defect; no digest/version | stale logical downstream content | name uppercase and JSON key sort | active for all six IDs | same-object warm hit only | `IN_SCOPE` | P0 |
| `systems/Parasara/engine/rules/engine.py:37-47` | `_cache_key`; `_normalize_inputs` | cache/parameters | `default=str` or raw `str(dict)` for custom/non-JSON values | noncanonical parameters | cache identity/inputs | `CACHE_NONDETERMINISM` | repr/process/type | collisions/fragmentation | indirect stale/wrong result | mapping keys sorted only in happy path | active for all calls | no equivalent-value tests | `IN_SCOPE` | P0 |
| `systems/Parasara/engine/rules/engine.py:24-25,50-131` | `_CACHE`; `clear_cache`; stores | cache/global state | mutable process-global non-atomic cache, sticky failures, shallow values | test/order/concurrent calls/mutation | match/evidence/errors/telemetry | `CACHE_NONDETERMINISM` | test/thread/process order | direct | indirect Yoga/domain/public | explicit whole-cache clear | active evaluator; Yoga globally clears | basic cold/warm flag test | `IN_SCOPE` | P0 |
| `tests/rules/test_predicate_result.py:67-74`; `engine/rules/engine.py:37-43` | debug `asdict`; string fallback | debug/serialization | arbitrary object string/repr and telemetry inclusion | debug/canonicalization attempt | full result/key text | `SERIALIZATION_NONDETERMINISM` | process/type/version | fallback changes identity | debug/future serializers | `sort_keys` only for key path | test/debug and active key fallback | JSON string only | `IN_SCOPE` | P1 |
| `systems/Parasara/engine/enrichments/yoga_engine.py:150-180` | Yoga rule loop/output | Yoga/serialization | global registry insertion order | loader/import order differs | Yoga row order and UUID-bearing rows | `SERIALIZATION_NONDETERMINISM` | process/test/load order | cache cleared but registry persists | Yoga state/public | dict insertion order only | active | no repeated-output equality test | `IN_SCOPE` | P1 |
| `tests/testing_framework/generate_full_artifacts.py:51-79` | `run_rules_and_trace` | artifact serialization | registry iteration/list order | artifact generation after varied load | rule trace row order | `SERIALIZATION_NONDETERMINISM` | filesystem/process | no direct key effect | persisted internal artifacts | JSON indentation only | active tooling when invoked | none | `TEMPORARY_COMPATIBILITY` | P2 |
| `systems/Parasara/tools/generate_snapshot.py:43-49`; `ci_snapshot_check.py:21-28`; `tests/determinism_test.py:7-15` | writer/normalizers/hash | output/snapshot | keys sorted but lists preserved; normalization policies differ | unstable Yoga/rule/evidence order | serialized/snapshot tree | `SERIALIZATION_NONDETERMINISM` | runner/tool policy | selected stale content can enter output | full snapshot/public | `generated_at=None`, sorted keys, CI float rounding | active snapshot/test paths | one repeated whole-output hash test | `TEMPORARY_COMPATIBILITY` | P1 |
| `systems/Parasara/engine/rules/engine.py:61-131` | `evaluate_predicate` | predicate telemetry | `time.perf_counter()` | every cold/error evaluation | `evaluation_time_ms` | `PERFORMANCE_ONLY_NONDETERMINISM` | every call/machine | cold value reused on warm result | debug/future serializer | intended telemetry field | active for all six IDs | asserts non-null only | `IN_SCOPE` | P1 |
| `systems/Parasara/engine/rules/engine.py:135-159` | `evaluate_condition` | condition telemetry | elapsed timing copied into child summaries | every logical condition | result time and trace-step times | `PERFORMANCE_ONLY_NONDETERMINISM` | every call/machine/order | leaf warmth changes child telemetry | Yoga intermediates/debug | source child order retained | active Yoga condition path | condition match only | `IN_SCOPE` | P1 |

Inventory counts are exclusive at the primary-impact level: logical 5, evidence 3, error 2, trace-only 1, cache 3, serialization/snapshot 4, and performance-only 2; total 20. Some paths have secondary impacts, especially cache-selected content entering serialization.

## 6. System-Time Dependencies

One predicate-derived implicit logical time dependency exists: `compute_vimshottari` uses `datetime.utcnow()` when `astro.metadata.birth_datetime_utc` is absent or invalid (`vimshottari.py:54-66`). It is `IMPLICIT_LOGICAL_TIME`: it changes period boundaries, has no injected evaluation clock, uses naive UTC, is absent from cache identity, and has no freeze/injection test. Supplying valid birth metadata is an existing partial control. This path is not invoked by the current six registered predicates.

Predicate and condition `perf_counter()` calls are `PERFORMANCE_TIMING`, not system-time logic. Snapshot `generated_at` is intentionally `None`. Snapshot-approval `datetime.utcnow()` and CI `time.time()` affect tooling metadata/branch naming and are `UNRELATED` to logical evaluation. No predicate-related `datetime.now`, `date.today`, `time.time`, or trace timestamp is active.

## 7. Randomness and UUIDs

There is one active predicate-derived random/UUID dependency: Yoga `_make_trace_id()` calls UUID4 for every output row (`yoga_engine.py:14-15,177`). It does not alter match logic but changes trace identity and serializable Yoga output on every call. There is no normalization or stable mapping; tests require only a nonempty ID and therefore endorse variability accidentally.

No registered predicate, central condition evaluator, Career interpreter, cache key, or snapshot assembler uses random numbers. The seeded Surya testcase generator is unrelated test-data tooling. No `secrets` dependency was found.

## 8. Process Identity and Unstable Hashes

One active process-identity dependency exists: `_cache_key` uses `id(astro)` (`engine.py:37-44`). It is stable only for the lifetime of the same object in one process. It changes for equivalent objects and separate processes, survives mutation of the same object, can theoretically be reused after object destruction while a global cache entry remains, and prevents cross-process identity. This is a cache-selection risk rather than a serialized ID.

The repeated-output test hashes a JSON string with SHA-256 and is stable for that string. No active predicate path uses Python's default `hash()`, PID, thread ID, or explicit memory-address representation. However, `default=str` accepts custom object representations that may contain memory addresses; that is classified under cache/serialization fallback rather than a second direct identity source.

## 9. Collection, Filesystem and Import Ordering

| File | Symbol | Collection/Source | Semantic Order | Current Order | Stable | Normalized | Fields Affected | Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|
| `rules/predicates.py:18-43` | `aspect_exists` | aspect edge list | canonical graph/provider order required | supplied list order | No across equivalent constructions | No | matched edge evidence | evidence changes/order | P1 |
| `rules/predicates.py:74-81` | `functional_role` | context planets/`astro.planets` | canonical state/caller order required | supplied order | No across equivalent inputs | No | matched planets | evidence order | P1 |
| `enrichments/yoga_engine.py:43-52` | dormant aspect helper | set of planet names | first factual occurrence or canonical planet order | hash-set order | No | No | evidence planets | nondeterministic evidence | P2 |
| `enrichments/yoga_engine.py:164-178` | Yoga projection | set of flattened planets | condition/source occurrence order | hash-set order | No | No | Yoga planets | output changes by hash seed | P0 |
| `rules/loader.py:19-34` | loader | `os.walk` dirs/files | declared rule source order or order-independent duplicate rejection | filesystem enumeration | No | No | winner and registry order | logical membership/winner | P0 |
| `enrichments/yoga_engine.py:150` | Yoga loop | global rule registry | approved rule-set semantic order | insertion order from prior load | No | No | Yoga match rows | logical/output order | P0 |
| `testing_framework/generate_full_artifacts.py:57` | artifact loop | global rule registry | same approved rule order | insertion order | No | No | artifact rows | persisted order | P2 |
| `rules/engine.py:143-156` | condition loop | condition children | source order is semantic | explicit list order | Yes for fixed tree | Not required | evidence/errors/trace | missing node identity, not random order | P1 |
| `interpreters/career.py:37-105` | candidate/indicator loops | Astro planets/rule list | source/domain priority order | constructed list order | Yes for fixed prepared state | No | indicator order/score accumulation | upstream order dependency | P1 |
| `tools/generate_snapshot.py:49` | JSON writer | mapping keys and lists | schema field order plus semantic list order | keys sorted, lists retained | Partly | keys only | snapshot/public JSON | unstable lists survive | P1 |

Six unstable collection-order paths are counted: aspect edges, functional-role candidates, the two Yoga set conversions, Yoga rule iteration, and artifact registry iteration. Condition children are deliberately left-to-right and must not be alphabetically sorted. Career contributions likewise require an approved semantic order, not cosmetic sorting.

Three filesystem/import-order dependencies are material: unsorted rule discovery/duplicate overwrite, CWD-based functional-role configuration, and Yoga's stale imported registry/lazy initialization. YAML list order within the single `yogas.yaml` file is stable when that exact file is loaded into the same live dictionary, but the surrounding global lifecycle is not.

## 10. Mutable Global State and Test Order

Four mutable-global/test-order mechanisms exist:

1. `PREDICATE_REGISTRY` is mutated by import-time decorators and tests; there is no freeze, snapshot, reset, duplicate rejection, or cache invalidation after replacement (`engine.py:22,28-32`).
2. `_CACHE` is process-global, shallow, unbounded, and cleared wholesale; test/order and concurrent evaluation affect warmth and stale content (`engine.py:24-25,34-35`).
3. `loader.RULE_REGISTRY` is rebound and mutated; earlier imports may retain the old dictionary (`loader.py:5,14-16,44-47`).
4. Yoga uses its imported `RULE_REGISTRY`, lazily loads on emptiness, and globally clears the predicate cache, so prior loaders/tests change both rule visibility and other callers' cache state (`yoga_engine.py:4-8,142-150`).

Instrumentation globals in `tests/testing_framework/instrumentation.py` are locked but affect coverage diagnostics, not current predicate logical output. No production reset fixture or isolated registry/cache context exists. Existing tests call `clear_cache()` manually only for selected direct predicate cases.

## 11. AstroState Lifecycle and Mutation

Four lifecycle dependencies affect predicate-derived behavior:

1. normalization assigns the entire `astro.enrichments` dictionary and then computes strengths, houses, and aspects (`normalizer.py:133-155`);
2. Yoga integrates vargas into the supplied state (`yoga_engine.py:146-147`);
3. Yoga computes/replaces aspect data and invokes role computation before predicates (`yoga_engine.py:147-155`);
4. Yoga writes `astro.enrichments['yogas']` after evaluation (`yoga_engine.py:181-187`).

Registered handlers perform no direct state write, but `FUNCTIONAL_ROLE` recomputes configuration-derived facts during evaluation. The same object can therefore change content while retaining the same `id(astro)` cache identity. A digest computed before versus after enrichment would differ conceptually, but no digest exists. Reusing partially prepared states or running Yoga/domain operations in different orders can change facts, evidence, stale-cache selection, and output. Equivalent separately constructed AstroState instances have no canonical equivalence test.

## 12. Predicate-by-Predicate Determinism

| Predicate ID | Version | Time | Randomness | I/O | Mutable State | Collection Order | Float Risk | Cache Dependency | Trace Variability | Classification | Evidence | Tests | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ASPECT` | missing | none | none | indirect prepared graph | live enrichment edges | edge order | none direct | unsafe `id(astro)` cache | timing; empty predicate steps | `NONDETERMINISTIC` | local alias handler stable only for fixed edge list; stale cache/order can alter evidence | indirect Yoga/aspect tests | P0 |
| `ASPECT_EXISTS` | missing | none | none | indirect prepared graph | live enrichment edges | edge order | none direct | unsafe `id(astro)` cache | timing; empty predicate steps | `NONDETERMINISTIC` | same handler as `ASPECT`; alias/version identity absent | no observed direct execution | P0 |
| `PLANET_IN_HOUSE` | missing | none | none | none | reads mutable planet list | first matching planet/list order | none | unsafe `id(astro)` cache | timing; empty predicate steps | `NONDETERMINISTIC` | handler locally factual; same-object mutation can return stale result | direct cold/warm flag test | P0 |
| `HOUSE_OCCUPANT` | missing | none | none | none | reads mutable planet list | first matching planet/list order | none | unsafe `id(astro)` cache | timing; empty predicate steps | `NONDETERMINISTIC` | handler locally duplicates house fact; active Yoga caller | indirect integration | P0 |
| `FUNCTIONAL_ROLE` | missing | none | none | CWD/YAML | recomputed roles/state list | candidate order | rounded role scores affect class thresholds | unsafe `id(astro)` cache | timing; empty predicate steps | `NONDETERMINISTIC` | external table/fallback version and CWD are hidden logical inputs | behavior/matrix tests only | P0 |
| `PLANET_EXALTED` | missing | none | none | none | reads flags/metadata fallback | first matching planet | metadata numeric representation | unsafe `id(astro)` cache | timing; empty predicate steps | `NONDETERMINISTIC` | ambiguous mutable capability sources plus stale cache | one unmatched test | P0 |

Final end-to-end counts are deterministic 0, deterministic with explicit context 0, logically deterministic with telemetry variation 0, nondeterministic 6, and unknown 0. This does not claim the five handler functions contain random logic: it records the active `evaluate_predicate` contract, including cache and mutable-state lifecycle. If evaluated directly with frozen prepared data, the simple handlers would be logically stable; that is not the public runtime path.

## 13. Parameter Canonicalization

Only JSON mapping keys are sorted in the cache-key happy path. `_normalize_inputs` returns the caller's dictionary unchanged. Equivalent forms are not normalized: aliases and case variants, omitted versus explicit defaults, numeric strings versus numbers, list versus tuple, set/frozenset order, date/datetime encodings, floats/Decimal, NaN/Infinity, and custom values can fragment or collide. `default=str` may erase type distinctions; fallback `str(dict)` restores insertion-order and representation dependence. The mutable caller-owned `inputs` object is stored in results.

Consequently, equivalent parameters are not guaranteed identical logical identity or serialized inputs. No test permutes mapping insertion order beyond JSON's simple string-key sorting, compares aliases/default forms, checks custom objects, or rejects non-finite numbers.

## 14. Floating-Point Determinism

Registered factual predicates perform no material floating summation. `FUNCTIONAL_ROLE` computes floating scores with fixed Python operations and rounds to three decimals, but table values, ownership order, NaN/Infinity, and threshold-edge behavior are unvalidated (`functional_roles.py:105-157`). Career averages strengths, accumulates contributions in candidate order, clamps/rounds via explainability, and emits three-decimal score/confidence (`career.py:16-21,86-115`). Stable finite inputs and stable order normally give stable CPython output; different contribution order can change boundary rounding.

CI normalization rounds floats while the snapshot writer and repeated-hash test use different policies. No tolerance/rounding contract, non-finite rejection, cross-platform test, or order-of-summation test exists. Platform math functions are not material in the six handlers.

## 15. Error, Evidence and Trace Determinism

Errors are mutable dictionaries. Handler exceptions become raw `str(e)`, while loaders swallow errors. Identical logical defects can therefore differ by filesystem path, library/version text, and discovery order; there is no stable code/details schema or deterministic mixed-child precedence. Condition errors are flattened in source child order, which is stable for a fixed tree but lacks node identity.

Evidence is shallow and caller-owned. Aspect edge dictionaries remain live, functional-role evidence follows candidate order, cache copies share nested values, and Yoga projects through set-derived lists. Equivalent evaluations are therefore not guaranteed equivalent evidence after caller/state mutation or reordered construction.

All registered handlers emit empty predicate trace lists. Condition summaries embed variable elapsed time. Yoga discards typed predicate trace potential and emits UUID4. The Career constant `career_001` is deterministic but nonunique. No timestamp affects trace identity. Logical operation ordering, skipped branches, parent/child IDs, and cache-hit-equivalent logical trace are undefined.

## 16. Cache-State Determinism

| Evaluation Scenario | Matched | Status | Inputs | Evidence | Errors | Logical Trace | Serialization | Expected Difference | Actual Difference | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| same object, immediate cold then warm | same normally | no status model | same reference | same shared values | same shared values | empty/same logical content | `cache_hit` and timing-bearing debug differ | telemetry only | cache flag changes; cold timing reused | Partial | P1 |
| same object mutated between calls | may be stale | absent | old/caller-owned | may be stale | sticky | stale/empty | stale result selected | recompute under new digest | logical matched/evidence can differ from fresh evaluation | Noncompliant | P0 |
| cached evidence mutated by caller | usually same match | absent | shared | warm value corrupted | shared | shared | mutated serialization | immutable equivalent value | one reachable logical evidence difference | Noncompliant | P0 |
| equivalent separate AstroState objects | handler result should match | absent | same logically | should match | should match | should match | telemetry differs | logical equality, independent telemetry | separate cold evaluations because IDs differ | Partial | P1 |
| same logical params, different insertion order | normally same simple JSON key | absent | retains caller order | normally same | same | same | result inputs/debug order differs | canonical identity/value | only cache happy path sorts keys | Noncompliant | P1 |
| transient handler failure then warm call | cached failure persists | absent | same | failure evidence | raw cached error | empty | warm returns sticky failure | policy-defined retry/recovery identity | failure is cached unconditionally | Noncompliant | P0 |
| Yoga run while other caller uses cache | predicate cache cleared globally | absent | caller-specific | caller-dependent | caller-dependent | timing changes | downstream timing/cache changes | isolated run cache | cross-caller lifecycle interference | Noncompliant | P0 |

Two cold/warm logical-difference mechanisms are counted: stale same-object state and mutable shared cached evidence. `cache_hit` and elapsed time are expected telemetry differences but are currently inseparable from dataclass equality/debug serialization. Predicate version, state digest, context, capability versions, rule-set versions, and deterministic/cacheable metadata are absent from the key. Clearing is global; writes/checks are not atomic; transient failures are cached.

## 17. Condition-Evaluation Determinism

AND/OR evaluate every child sequentially in source list order. For a fixed tree, match aggregation and flattened error/evidence ordering are repeatable, but evaluation is eager rather than an approved short-circuit contract. Cache population, timing, side effects of future handlers, and error aggregation therefore depend on child order. No NOT evaluator exists. Skipped-branch semantics, node IDs, status precedence, malformed/cyclic-tree handling, and alternate evaluator reconciliation are undefined.

Source order is semantic and must be preserved. Determinism requires a documented left-to-right evaluation/short-circuit policy, deterministic skipped representation, and child-path identity—not alphabetic sorting. Current Yoga's dormant private evaluator has separate tuple semantics and must not become an alternate runtime.

## 18. Yoga and Domain Determinism

Eight Yoga/domain risks are counted:

1. UUID4 Yoga trace IDs;
2. set-derived Yoga planet ordering;
3. rule-registry load/iteration and duplicate-winner ordering;
4. stale imported registry/lazy global lifecycle;
5. AstroState enrichment mutation/preparation order;
6. global predicate-cache clearing and stale leaf-cache behavior;
7. CWD/file-version-dependent functional roles;
8. Career candidate/contribution ordering and floating accumulation under upstream order changes.

For fixed current data and registry state, Career uses constructed candidate order, rounds scores/confidence, emits constant `career_001`, and is repeatable. It does not consume PredicateResult directly. That stability is conditional on upstream planet/rule/enrichment order and does not have a repeated/cold-warm domain test. Yoga is observably nonrepeatable even with identical state because every row gets a new UUID and planet lists can vary by hash seed. Yoga also writes results back into AstroState.

## 19. Serialization and Snapshot Determinism

Six serialization/snapshot nondeterminism paths are retained from Audit-20:

1. predicate/condition elapsed timing;
2. cold/warm `cache_hit` plus reused cold timing;
3. Yoga UUID4 trace IDs;
4. Yoga set-to-list planet order;
5. filesystem/global rule-registry iteration in Yoga/artifacts;
6. `default=str`/fallback object representations.

The snapshot writer fixes `generated_at=None` and sorts mapping keys. CI additionally rounds floats; the repeated hash test uses the writer's structure and sorted keys; the comparison framework has separate ignore/tolerance rules. Lists are never canonicalized because their semantic order must be defined upstream. The current main snapshot hardcodes Yoga to `[]`, so Yoga variability is not yet present there. Career's fixed trace ID is stable. Public runner/API/frontend layers pass through untyped JSON and provide no versioned logical/telemetry projection.

## 20. Parallel and Concurrent Execution

No supported parallel predicate/Yoga/domain evaluator or serial-versus-parallel equivalence test was found. Five concurrency risks exist:

| Component | Current concurrency classification | Reason |
|---|---|---|
| Predicate registry | `RACE_RISK` | unsynchronized registration/replacement during lookup |
| Predicate cache | `RACE_RISK` | check/store/clear are shared and non-atomic as a logical operation |
| Rule registry/loaders | `RACE_RISK` | global rebind and mutation while readers retain old/new dictionaries |
| Shared AstroState/Yoga | `RACE_RISK` | enrichments and Yoga results are mutated without isolation |
| Parallel result aggregation | `UNSUPPORTED` | no contract for completion/error/trace ordering |

The GIL does not make the multi-step lifecycle deterministic. Concurrent duplicate evaluation may both execute, a Yoga clear can affect unrelated evaluations, and shared state writes can interleave. Static analysis cannot prove actual production concurrency because no scheduler/executor integration was found; the risks remain reachable to callers using threads.

## 21. Repeatability Testing Assessment

`tests/determinism_test.py` generates the same snapshot repeatedly, JSON-serializes with sorted keys, and compares SHA-256 hashes. It exercises current Career output but not PredicateResult, Yoga (hardcoded empty in the snapshot), cache state, equivalent states, subprocesses, test order, load order, or concurrency. It also treats all output fields alike rather than explicitly excluding permitted telemetry.

`tests/rules/test_predicate_result.py` verifies one cold `cache_hit=False` and warm `cache_hit=True` result, but does not compare a logical projection or mutate state/evidence. Snapshot tests protect current artifacts, and CI normalizes keys/floats, but divergent normalization policies can hide or create differences. No utility systematically repeats predicate/condition/Yoga/domain evaluation across the required scenario matrix.

## 22. Existing Tests and Coverage Gaps

Twenty-six missing determinism test categories were identified:

| Area | Missing Categories | Count | Recommended Test File |
|---|---|---:|---|
| Predicate repeatability | same object repeat; equivalent states; explicit context time; no implicit time; no randomness; stable error/evidence | 6 | `tests/rules/test_predicate_determinism.py` |
| Ordering | parameter mappings; predicate registry; rule files/duplicates; errors; traces; Yoga matches; domain indicators | 7 | `tests/rules/test_deterministic_ordering.py` |
| Cache | cold/warm logical equality; stale-state prevention; transient-error policy; enrichment/version isolation | 4 | `tests/rules/test_cache_determinism.py` |
| Serialization | repeated canonical serialization; telemetry separation; snapshot stability; subprocess/cross-process stability | 4 | `tests/rules/test_deterministic_serialization.py` |
| Lifecycle/concurrency | test-order independence; registry reset; cache reset; no state-mutation dependence; serial/parallel equivalence | 5 | `tests/rules/test_runtime_isolation.py` |

Existing coverage is partial: basic cache flags, predicate results, Yoga load/output structure, Career/full snapshots, and repeated assembled-output hashes. It does not establish the Prompt-01 logical contract.

## 23. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Canonical AstroState digest in identity | `MISSING` | cache uses `id(astro)` | `engine.py`; AstroState | approved canonical digest/version | `IN_SCOPE` | P0 | Yes |
| Predicate and capability versions in identity | `MISSING` | no predicate metadata/key versions | registry/cache/loaders | versioned metadata and key | `IN_SCOPE` | P0 | Yes |
| Canonical parameter identity | `NONCOMPLIANT` | mutable input plus `default=str` | `engine.py`; handlers | validation and canonical value encoding | `IN_SCOPE` | P0 | Yes |
| Deterministic registry/rule lifecycle | `NONCOMPLIANT` | mutable globals, rebind, silent overwrite | engine/loaders/Yoga | bootstrap/freeze/duplicate policy | `IN_SCOPE` | P0 | Yes |
| State lifecycle isolation | `NONCOMPLIANT` | Yoga mutates prepared state | normalizer/Yoga/cache | explicit immutable prepared-state boundary | `IN_SCOPE` | P0 | Yes |
| Deep immutable logical results | `NONCOMPLIANT` | frozen shell, mutable nested values | models/cache/evidence | deep immutable typed values | `IN_SCOPE` | P0 | Yes |
| Deterministic logical/error status | `MISSING` | no status and raw/sticky failures | evaluator/condition | typed status/error precedence | `IN_SCOPE` | P0 | Yes |
| Logical/telemetry separation | `NONCOMPLIANT` | timing/cache flag in result equality/debug | evaluator/serializer | separate projections | `IN_SCOPE` | P1 | Yes |
| Deterministic evidence content/order | `NONCOMPLIANT` | live edges, caller order, sets | predicates/Yoga | factual immutable semantic ordering | `IN_SCOPE` | P1 | Yes |
| Deterministic trace identity/order | `NONCOMPLIANT` | empty steps, timing, UUID4 | evaluator/Yoga | stable typed trace contract | `IN_SCOPE` | P1 | Yes |
| Deterministic condition semantics | `PARTIAL` | fixed source order but eager/no status/skips | `engine.py` | approved left-to-right semantics | `IN_SCOPE` | P1 | Yes |
| Cold/warm logical equivalence | `NONCOMPLIANT` | two reachable logical differences | cache/evidence/state | immutable digest-keyed cache policy | `IN_SCOPE` | P1 | Yes |
| Deterministic safe error conversion | `NONCOMPLIANT` | raw exception text/silent loaders | evaluator/loaders | stable codes/details/order | `IN_SCOPE` | P1 | Yes |
| Deterministic Yoga integration | `NONCOMPLIANT` | eight Yoga/domain risks | Yoga/loaders/cache/state | compatibility adapter plus isolation | `IN_SCOPE` | P1 | Yes |
| Determinism test suite | `MISSING` | 26 categories absent | tests | scenario-based logical comparisons | `IN_SCOPE` | P1 | Yes |
| Canonical logical serialization | `MISSING` | only debug/default-str path | serializer/output | one deterministic serializer | `IN_SCOPE` | P2 | No |
| Explicit evaluation clock for Dasha/time consumers | `NONCOMPLIANT` | UTC-now fallback | Dasha/context | explicit versioned time context | `OUT_OF_SCOPE_FUTURE_STAGE` | P2 | No |
| Public schema/version and snapshot policy | `PARTIAL` | sorted keys but skeletal schema/divergent normalizers | output/schema/tests | approved versioned contract | `TEMPORARY_COMPATIBILITY` | P2 | No |
| Concurrency safety contract | `MISSING` | four races plus unsupported aggregation | registries/cache/Yoga | ownership/locking/isolation decision | `IN_SCOPE` | P2 | No |
| Cross-process cache persistence/equality | `MISSING` | process-only identity/cache | future cache layer | later persistence contract if required | `OUT_OF_SCOPE_FUTURE_STAGE` | P3 | No |
| Universal domain/inference deterministic traces | `MISSING` | Career constant/no inference serializer | future domain/inference stages | later shared trace architecture | `OUT_OF_SCOPE_FUTURE_STAGE` | P3 | No |

Priority totals are P0=7, P1=8, P2=4, and P3=2.

## 24. Migration Risks and Priorities

P0 work must establish canonical state/parameter/version identity, deterministic registry lifecycle, immutable logical results, explicit state preparation, and typed status/error semantics before caching migrated results. Otherwise a typed model would preserve nondeterministic selection rather than fix it.

P1 work must separate telemetry, define condition semantics, preserve deterministic evidence/trace order, isolate Yoga, make cold/warm results logically equal, and add focused repeatability tests. Care is required not to sort semantic child, rule, indicator, or contribution sequences alphabetically. Existing valid match results and Career snapshots need explicit compatibility assertions.

P2 covers canonical/public serialization, Dasha's later explicit clock, snapshot/schema governance, and concurrency ownership. P3 covers future cross-process persistence and universal domain/inference trace architecture. Random Yoga IDs, stale cache behavior, silent duplicate winners, and CWD configuration are the highest migration surprises.

## 25. Unresolved Architectural Questions

1. What exact AstroState fields, normalization version, and capability versions form the canonical digest?
2. Is the logical trace part of cache identity/equality, and which cache provenance belongs only to telemetry?
3. What approved semantic ordering applies to predicates, rules, Yoga rows, evidence collections, domain indicators, and errors?
4. What deterministic AND/OR/NOT short-circuit, skipped-node, and mixed-status precedence is required?
5. Should transient/recoverable failures ever be cached, and how is recovery/version change represented?
6. Must evaluation accept only an already immutable prepared AstroState, or may an explicit preparation stage return a new enriched state?
7. What stable Yoga/run/parent-child trace-ID scheme replaces UUID4 without conflating domain and predicate trace models?
8. Is concurrent evaluation supported in Prompt-01, serialized by ownership, or explicitly rejected?
9. Is Dasha's evaluation/reference time part of a shared versioned evaluation context in this stage or a later stage?
10. Which snapshot/public fields are logical contracts and which are explicitly excluded telemetry?

## 26. Audit-21 Conclusion

Audit-21 is COMPLETE. All twenty prerequisites were available. Twenty nondeterminism sources were classified: five logical, three evidence, two error, one trace-only, three cache, four serialization/snapshot, and two performance-only. There is one implicit-time, one UUID, one process-identity, six unstable collection-order, three filesystem/import-order, four mutable-global/test-order, and four AstroState lifecycle dependency counts.

All six registered IDs are end-to-end `NONDETERMINISTIC` under the current evaluator/cache contract, despite locally stable handler logic under fixed prepared input. Two cold/warm logical differences, eight Yoga/domain risks, five concurrency risks, six serialization/snapshot paths, and twenty-six missing test categories were recorded. Findings total 7 P0, 8 P1, 4 P2, and 2 P3. Exactly this report was created; Audit-22 was not started.

| Metric | Count |
|---|---:|
| Nondeterminism sources | 20 |
| Logical nondeterminism paths | 5 |
| Evidence nondeterminism paths | 3 |
| Error nondeterminism paths | 2 |
| Trace-only nondeterminism paths | 1 |
| Cache nondeterminism paths | 3 |
| Serialization/snapshot primary sources | 4 |
| Performance-only variability paths | 2 |
| Implicit system-time dependencies | 1 |
| Random or UUID dependencies | 1 |
| Process-identity dependencies | 1 |
| Unstable collection-order paths | 6 |
| Filesystem/import-order dependencies | 3 |
| Mutable-global/test-order dependencies | 4 |
| AstroState lifecycle dependencies | 4 |
| Deterministic predicates | 0 |
| Explicit-context deterministic predicates | 0 |
| Telemetry-only variable predicates | 0 |
| Nondeterministic predicates | 6 |
| Predicates with unknown determinism | 0 |
| Cold/warm logical differences | 2 |
| Yoga/domain determinism risks | 8 |
| Concurrency race or ordering risks | 5 |
| Serialization/snapshot nondeterminism paths including secondary impacts | 6 |
| Missing determinism test categories | 26 |
| P0 findings | 7 |
| P1 findings | 8 |
| P2 findings | 4 |
| P3 findings | 2 |
