Implement **WP09 — replace the predicate evaluator and cache contract with an engine-owned, content-addressed, immutable, bounded cache** for Prompt-01.

Do not merely review this specification. Implement the permitted work, validate it in both locked Python lanes, and create the WP09 completion report. **Do not proceed to WP10.**

## Objective

Integrate the WP08 canonical `PLANET_IN_HOUSE@1.0.0` seam into a canonical evaluator and replace the unsafe object-identity/process-global cache contract with a deterministic engine-owned cache that:

- keys only on canonical predicate behavior inputs and versioned prepared facts;
- stores immutable telemetry-free logical results;
- returns cold and warm results that are logically identical;
- keeps cache telemetry outside logical equality/bytes;
- caches only completed `matched` and `unmatched` outcomes;
- never caches invalid, missing, error, timeout, or skipped outcomes;
- is explicitly bounded, deterministic, clearable, freezable, and isolated per evaluator instance;
- performs no implicit preparation, provider access, astrology inference, output mutation, or cross-request global sharing;
- preserves valid legacy factual, Yoga, Career, rule, snapshot, and public behavior.

WP09 owns evaluator/cache infrastructure and the canonical routing of `PLANET_IN_HOUSE` only. WP10 owns typed conditions/operators. WP11 owns migration of the remaining predicates.

## Hard prerequisite gate

Before editing:

1. Locate final WP00-R and WP01–WP08 reports by exact filename.
2. Confirm WP08 records `VERDICT: COMPLETE` and `WP09_READY: YES`.
3. Reproduce the current baseline in the locked Python 3.14 and 3.11 environments.
4. Confirm identical collection node IDs, clean full suites, all Yoga permutations and loader orders, rule lint over all five supported files exactly once, and strict approved-snapshot matches.
5. Record and preserve the inherited dirty worktree.

If any prerequisite fails, stop without production changes and report `VERDICT: BLOCKED` and `WP10_READY: NO`.

## Required references

Read the current implementation plus:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP02–WP08 reports;
- Audit 04, 05, 07, 08, 09, 10, 11, 12, 18, 19, 20, 21, and 22 reports.

Resolve moved files by filename. Use completion reports as implementation evidence and audits as defect/test inventories.

## Locked architectural decisions

Implement these decisions unless the existing locked decision record specifies an already-approved stricter compatible value:

| Concern | WP09 decision |
|---|---|
| ownership | cache belongs to a `PredicateEvaluator` instance; no canonical process-global cache |
| default bound | maximum **256 entries**, constructor-configurable to a strict positive non-Boolean integer |
| eviction | deterministic least-recently-used eviction; a hit updates recency |
| values | immutable canonical `PredicateResult` logical content with `cache_hit=False` and `evaluation_time_ms=None` while stored |
| cacheable statuses | only `matched` and `unmatched` |
| non-cacheable statuses | `missing_capability`, `invalid_parameters`, `error`, `timeout`, and `skipped` |
| key | canonical typed components/bytes; never Python object identity, raw values, repr, pickle, or fallback strings |
| concurrency | each instance owns its state; cache get/put/clear/freeze operations are protected from concurrent mutation; no distributed/parallel design |
| clear | explicit instance method empties entries deterministically |
| freeze | explicit instance method disables future cache mutation; hits remain readable and misses evaluate without insertion |
| telemetry | produced per evaluation response; excluded from the stored value, key, logical equality, and logical serialization |
| preparation | caller supplies `PreparedAstroState` and typed context; evaluator never prepares mutable state implicitly |

If the current approved locked plan contains a different explicit cache bound, use that value and document the conflict/resolution. Do not silently invent another policy.

## Strict scope

### Permitted

- Add a canonical `PredicateEvaluator` and a small dedicated cache/key module if separation improves boundary enforcement.
- Modify `rules/engine.py` narrowly to expose canonical evaluation and retire the unsafe `_CACHE`/`id(astro)` key from the canonical path.
- Route canonical `PLANET_IN_HOUSE` calls through the WP08 handler.
- Retain a clearly named temporary legacy adapter for unmigrated predicates, but it must not share or contaminate the canonical cache.
- Update tests whose only assertion is the intentionally replaced legacy cache telemetry/ownership contract.
- Add WP09 focused tests and the completion report.

### Forbidden

- Do not migrate `HOUSE_OCCUPANT`, `ASPECT`, `ASPECT_EXISTS`, `FUNCTIONAL_ROLE`, or `PLANET_EXALTED`.
- Do not implement `ConditionResult`, `AND`, `OR`, `NOT`, loader validation, Yoga/Career migration, or caller cleanup.
- Do not add persistent, disk, distributed, cross-process, TTL, weak-reference, background-cleaner, or performance-metrics infrastructure.
- Do not change astrology semantics, rule files/tables, schemas, public output, dependencies, CI, approved snapshots, or golden artifacts.
- Do not auto-prepare mutable `AstroState`, call producers, inspect raw Surya/provider objects, or fall back from prepared facts.
- Do not cache recovery-dependent failures.

Stop and request owner approval if a protected factual/public/astrology change is required.

## Canonical evaluator API

Create one explicit instance-owned evaluator API using current repository naming conventions. It must accept at minimum:

- requested predicate ID;
- raw parameters;
- `PreparedAstroState`;
- `PredicateEvaluationContext`;
- an optional explicit cache-use flag only if genuinely needed by tests/callers.

The canonical path must:

1. resolve the WP04 registry definition deterministically;
2. reject unknown/unmigrated canonical execution requests safely rather than treating them as false;
3. normalize/validate parameters through the definition's WP05 schema before key construction;
4. determine the canonical predicate ID/version and exact capability requirements;
5. construct the cache key from safe canonical components;
6. return a fresh telemetry-decorated result on a hit;
7. invoke the WP08 canonical handler on a miss;
8. cache only eligible logical results;
9. return a fresh cold response without exposing the stored cache object.

Do not duplicate WP08 parameter or factual logic inside the evaluator. If WP08 currently validates internally, add a narrowly reusable validation/request-preparation helper or make key construction consume the canonical result inputs only after safe evaluation on a miss. A hit must never be based on unvalidated raw parameters.

## Cache-key contract

Define a frozen typed key or canonical key projection. For `PLANET_IN_HOUSE`, identity must include:

1. system scope;
2. canonical predicate ID;
3. predicate SemVer;
4. a definition-specific fingerprint covering its parameter schema and ordered capability requirements/versions;
5. canonical normalized parameter bytes or SHA-256;
6. WP07 prepared-state schema/producer/normalization identity through the prepared-state canonical digest;
7. all predicate-relevant capability readiness, versions, source identity, and content through that state digest;
8. only behavior-relevant evaluation-context identity.

WP08 established that all current context fields are factually neutral for `PLANET_IN_HOUSE`. Therefore the WP09 key must use an explicit **no-relevant-context** projection for this predicate; `selected_planets`, `evaluation_instant`, and other neutral context differences must share the same logical entry. Do not accidentally key on the whole context merely because WP07 exposes a context digest. Preserve validation that state/context system scope is compatible.

Future migrated predicates may declare relevant context components in WP11; design the key builder so relevance can be supplied explicitly without changing the WP09 key format.

Requirements:

- equivalent independently constructed prepared states share the same key;
- any included factual/readiness/content/version change isolates the key;
- normalized equivalent parameters share the key;
- different valid canonical parameters do not;
- unrelated mapping insertion order, mutable source identity, process, CWD, and Python version do not matter;
- alias resolution must use canonical registry identity; do not create alias-specific duplicate entries unless an alias is explicitly versioned as behaviorally distinct;
- never include telemetry, evaluator/cache instance ID, object IDs, raw values, diagnostics, Yoga/Career/output, environment, or current time.

Use WP03 canonical projection/bytes/hash APIs. Do not use `json.dumps(default=str)`, `str` fallbacks, `repr`, `hash()`, pickle, or dataclass/Pydantic arbitrary serialization.

## Cache value and response policy

The stored value must be a canonical immutable WP02 `PredicateResult` representing logical content only:

- same predicate ID/version, inputs, evidence, trace, errors, status, and matched value as the handler result;
- `cache_hit=False`;
- `evaluation_time_ms=None`.

Never store a caller-facing response object carrying evaluation telemetry. Never return the actual stored object if response telemetry must differ.

On a cold eligible result:

- return logical content with `cache_hit=False`;
- attach finite nonnegative evaluation duration only in the existing telemetry field;
- store the telemetry-free logical value.

On a warm hit:

- return the same logical content with `cache_hit=True`;
- attach a fresh finite nonnegative lookup/evaluation duration, or `None` only if the locked telemetry contract explicitly requires it;
- do not reuse the cold duration.

Cold and warm results must compare equal and have identical WP03 logical data/bytes/SHA-256. Only the existing full/telemetry projection may differ.

Because values are deeply immutable, no defensive mutable-copy scheme is needed, but response construction must ensure telemetry decoration cannot mutate or replace the stored value.

## Status and recovery policy

Cache only results whose final canonical status is:

- `matched`;
- `unmatched`.

Do not cache:

- `missing_capability` (state may be re-prepared or capability versions may recover);
- `invalid_parameters`;
- `error`;
- `timeout`;
- `skipped`.

Repeated non-cacheable evaluations must execute again and return `cache_hit=False`. Prove controlled recovery: a first missing/error result must not prevent a later valid evaluation under the same normalized request from succeeding.

Do not reinterpret status, evidence, trace, or error content in the cache layer.

## Bounded deterministic LRU contract

Implement exact behavior tests for the default/configured bound:

- capacity must be a positive non-Boolean integer;
- insertion up to capacity does not evict;
- the next distinct eligible insertion evicts exactly the least recently used entry;
- a hit promotes the entry to most recently used;
- replacing an existing key does not grow size;
- non-cacheable results never consume capacity or alter unrelated recency;
- `clear()` empties the instance and is idempotent;
- `freeze()` is idempotent, preserves existing readable hits, prevents insertion/eviction/clear unless the locked contract deliberately permits clear, and misses still evaluate uncached;
- two evaluator/cache instances never share entries, recency, clear, or freeze state.

Choose and document whether `clear()` after freeze is rejected or allowed as a one-way safety operation. Preferred decision: **allow clear after freeze**, because it reduces retained data without adding entries; frozen state remains frozen.

Do not expose mutable internal mappings/order structures.

## Concurrency boundary

Use a minimal standard-library synchronization mechanism around cache structural operations. Prove:

- concurrent gets/inserts/clear/freeze cannot corrupt size, order, or values;
- capacity is never exceeded after an operation completes;
- instances remain isolated;
- duplicate computation on simultaneous misses is acceptable only if both responses are logically identical and at most one canonical entry remains;
- the handler is never executed while holding a cache lock if that could cause deadlock or excessive critical sections.

This is not authorization for parallel predicate execution, async redesign, distributed locking, or performance architecture.

## Legacy compatibility boundary

The unsafe canonical `_CACHE` key using `id(astro)` must be removed from the new path. Prefer removing that global cache entirely.

Until WP11/WP16 migrate remaining predicates/callers:

- keep any necessary legacy entry point explicitly named/documented as compatibility-only;
- do not cache legacy mutable-state results in the new canonical cache;
- do not silently convert mutable AstroState to PreparedAstroState;
- preserve valid legacy matched/unmatched truth and downstream Yoga/Career/public output;
- a historical test that asserted process-global warm-cache behavior must be migrated to the explicit evaluator-instance contract rather than forcing the unsafe global cache to remain;
- retain `clear_cache` only as a temporary compatibility adapter if an active caller still requires the symbol; it must not conceal a canonical process-global cache. Document exact behavior and planned WP16 removal.

Do not claim all predicates are canonical or cache-safe; only WP08's migrated predicate is eligible in WP09.

## Tests first

Add focused test modules before production changes. Cover at least:

### Key identity

- exact key fields/projection and canonical bytes/hash;
- equivalent state objects share a key and warm entry;
- changed prepared fact, readiness, capability version/content/source, prepared schema/producer/normalization version, predicate version, definition requirements/schema fingerprint, system scope, or valid canonical parameter isolates;
- normalized case/whitespace and parameter mapping order share;
- irrelevant context differences share for `PLANET_IN_HOUSE`;
- object identity, source mutation after preparation, CWD, process, and Python version do not affect the key;
- unsafe/cyclic/unvalidated parameters never reach key construction;
- no alias duplication where canonical identity is shared.

### Cold/warm behavior

- first eligible evaluation cold; second warm;
- exact logical equality, evidence, trace, errors, status, inputs, predicate identity/version, logical bytes, and logical hash;
- only allowed telemetry differs in full projection;
- cold duration is not reused as warm duration;
- caller cannot mutate either response or cached value;
- injected mutation attempts and source changes cannot corrupt later hits;
- cache bypass, if exposed, evaluates cold and does not mutate recency/storage.

### Status policy and recovery

- matched and unmatched cached;
- missing capability, absent entity/fact, invalid parameters, injected error, timeout, and skipped not cached (construct controlled canonical results/helpers where a status is not currently produced by WP08);
- repeated non-cacheable request executes again and remains cold;
- missing/error then repaired/valid request succeeds without manual clearing;
- no error/evidence/trace rewriting by cache.

### Bounds/lifecycle/isolation

- default 256 and small configured capacities;
- exact LRU eviction and hit promotion;
- replacement/duplicate key size behavior;
- non-cacheable capacity/recency neutrality;
- clear/idempotence;
- freeze/read-hit/miss-no-insert/clear-after-freeze behavior;
- per-instance isolation;
- no mutable cache internals exposed;
- minimal concurrency stress with deterministic invariants, no ordering assertion based on scheduler timing.

### Evaluator and compatibility

- unknown predicate produces typed canonical error and is not cached;
- unmigrated predicate is rejected by canonical evaluation or routed only through an explicit legacy adapter, never cached canonically;
- `PLANET_IN_HOUSE` calls WP08 rather than duplicating factual logic;
- no mutable AstroState accepted by the canonical evaluator;
- legacy valid truth values remain unchanged;
- six-ID/five-handler registry inventory remains unchanged;
- Yoga/Career and other handlers remain compatible;
- no process-global canonical cache or `id(astro)` key remains.

### Static/determinism

- no `id`, `hash`, `repr`, pickle, `default=str`, raw-provider/preparation/producer/output imports in canonical evaluator/cache modules;
- no filesystem/network/environment/random/UUID identity;
- clock use, if any, is limited to response telemetry and excluded from logical key/value/projection;
- fresh-process and Python 3.14/3.11 key bytes, logical results, and hashes match exactly.

Do not weaken/delete characterization tests or update snapshots.

## Validation gates

Run in both locked Python 3.14 and 3.11 lanes with bytecode/cache isolation and unique ignored temporary paths:

1. WP09 cache/key/evaluator focused tests.
2. WP02–WP08 focused modules.
3. All `tests/rules`.
4. WP01 predicate/Yoga/Career characterization.
5. Targeted evaluator/condition, Yoga, Career, runtime, role, Aspect, writer, linter, determinism, and snapshot regression tests.
6. Exact full collection comparison and node-ID SHA-256.
7. Complete suite twice from fresh processes per lane.
8. Yoga normal/reverse/A/B/C permutations.
9. Both loader-trigger orders.
10. Rule lint proving all five `.yml`/`.yaml` files, including `yogas.yaml`, are inspected exactly once.
11. Strict approved snapshot comparison twice per lane using temporary output and no update mode.
12. Fresh-process/cross-version cache-key bytes, cold/warm logical bytes, and hashes.
13. `git diff --check` and scoped artifact/status checks.

Record exact commands, counts, versions, byte lengths, hashes, cache bound/eviction observations, and any compatibility adapter behavior. A snapshot mismatch or protected factual difference is a blocker, not permission to update expected output.

## Required completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP09/WP09.md`

It must include:

1. `VERDICT: COMPLETE` or `VERDICT: BLOCKED`;
2. `WP10_READY: YES` or `WP10_READY: NO`;
3. actual model/reasoning used;
4. prerequisites and pre-edit baseline;
5. before/after evaluator/cache architecture;
6. exact files changed and APIs/signatures;
7. cache ownership, default/configurable bound, LRU, clear, freeze, isolation, and concurrency policies;
8. exact cache-key component/inclusion/exclusion/relevance table;
9. definition/schema/capability/context fingerprint policy;
10. stored-value versus cold/warm response telemetry policy;
11. cacheable/non-cacheable status and recovery matrix;
12. legacy adapter/global-cache disposition and planned removal boundary;
13. test-to-requirement traceability;
14. exact dual-lane commands/counts and collection node-ID hash;
15. exact key/result bytes and hashes across processes/Python versions;
16. LRU/bounds/concurrency evidence;
17. Yoga/loader/lint/snapshot/artifact compatibility evidence;
18. deferred WP10/WP11/WP16 work and any owner decision required;
19. explicit proof WP10 was not started.

## Definition of done

WP09 is complete only when:

- WP08 remains complete and reproducible;
- canonical `PLANET_IN_HOUSE` is evaluated through an explicit evaluator instance;
- cache keys are content/version addressed and contain no object/process identity or unsafe fallback;
- context relevance is explicit and neutral WP08 context does not fragment entries;
- cache is bounded to 256 by default, configurable, deterministic LRU, clearable, freezable, structurally synchronized, and instance-isolated;
- stored values are immutable and telemetry-free;
- cold/warm responses are logically/byte/hash identical except full telemetry;
- only matched/unmatched outcomes are cached and all recovery-dependent statuses re-evaluate;
- no canonical process-global cache contamination remains;
- legacy compatibility remains explicit and does not enter the canonical cache;
- no other predicate, condition, Yoga, Career, rule, public output, dependency, CI, or snapshot migration occurred;
- all dual-lane, determinism, regression, lint, snapshot, and artifact gates pass;
- the report records `VERDICT: COMPLETE` and `WP10_READY: YES`.

workingmedise
At the end, return a concise summary with the verdict, model/reasoning used, evaluator/cache locations, key and status policies, bound/LRU/lifecycle behavior, cold/warm and cross-version hashes, dual-lane counts, compatibility/snapshot status, files changed, deferred issues, and WP10 readiness. **Do not proceed to WP10.**