Implement **WP17 — complete architecture, safety, serialization, and determinism enforcement** for Prompt-01.

Do not merely review this specification. Establish the executable P0/P1 Stage-01 gates, validate them in both locked Python lanes and fresh subprocesses, and create the WP17 completion report. **Do not proceed to WP18.**

## Objective

Turn the architecture and compatibility guarantees completed through WP16 into repository-enforced tests that fail when future code:

- reintroduces tuple/raw-Boolean/dictionary predicate boundaries;
- bypasses `PredicateEvaluator` or the typed condition/Yoga/Career paths;
- imports raw Surya/provider objects into predicate, Yoga, or Career factual evaluation;
- performs predicate-relevant I/O, environment/CWD discovery, wall-clock/random identity, global-state mutation, input mutation, or producer recomputation;
- allows mutable aliases into prepared state, cached results, typed results, or public projections;
- mixes telemetry into logical identity;
- emits nondeterministic logical serialization, evidence, errors, traces, ordering, cache output, Yoga output, Career output, or tooling artifacts;
- leaks raw exception text, tracebacks, absolute paths, object identities, secrets, or uncontrolled values through typed/public diagnostic surfaces.

WP17 is an enforcement package. It is not the full-regression/performance evidence package (WP18), CI/workflow/documentation package (WP19), shared inference architecture, public schema redesign, new rule compiler, new astrology semantics, or broad repository security audit.

## Hard preflight gate

Before editing:

1. Locate and read by exact filename:
   - the locked Prompt-01 decisions/execution plan;
   - `Prompt-01-Final-Audit-Consolidation.md`;
   - final WP00-R and WP01 reports;
   - WP02 through WP16 completion reports;
   - Audits 02–12 and 14–23, emphasizing purity, cache, errors, evidence, trace, serialization, determinism, tests, and CI validation.
2. Require every predecessor through WP16 to record `VERDICT: COMPLETE` and WP16 to record `WP17_READY: YES`.
3. Record and preserve the inherited dirty worktree. Do not restore, stage, delete, or overwrite unrelated work.
4. Reproduce the complete WP16 baseline in Python 3.14.6 and Python 3.11.9:
   - identical collection;
   - two full-suite passes per lane;
   - focused typed tooling/retirement suite;
   - Yoga order permutations;
   - both loader trigger orders;
   - five-file rule lint;
   - strict approved snapshot comparison.
5. Reproduce the WP16 Career, tooling artifact, and coverage hashes in two fresh processes per lane.

Expected inherited evidence is 759 identical nodes, node-ID SHA-256 `167bf427a6a5e1ba1ffb18593202df64584787c13086152b7b40a18028b67598`, 757 passed and 2 optional skips in each repeated full run, and approved snapshot SHA-256 `da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`. Reproduce these values before adding WP17 tests; do not force final counts after legitimate new tests are added.

If a prerequisite is not reproducible, stop without production edits and report:

```text
VERDICT: BLOCKED
WP18_READY: NO
```

## Change boundary

The expected WP17 change is tests plus a small deterministic validation helper if needed. Do not modify production code merely to make a broad stylistic rule pass.

If an executable gate discovers an actual Prompt-01 violation:

1. add a focused red test;
2. identify the smallest behavior-preserving fix;
3. prove it does not change logical/public output or approved hashes;
4. document the deviation and fix in the report.

Any required astrology-semantic, rule/YAML/table, Career scoring, Yoga behavior, public schema, approved snapshot, dependency, or CI change requires separate owner approval. Stop rather than make such a change.

## Phase 1 — executable architecture policy

Create a centralized, deterministic architecture test suite for the current executable Python source. Prefer AST/import-graph checks and explicit allowlists over fragile plain-text searches.

The suite must prove:

### Typed invocation boundaries

- Registered predicate handlers are invoked only inside the approved evaluator boundary and explicit handler unit tests.
- Production callers consume canonical typed `PredicateResult`, `ConditionResult`, typed Yoga records/batches, or typed Career facts/batches as applicable.
- No production/test/tool code imports or calls the retired legacy runtime, retired tuple handler engine, legacy instrumentation, raw helpers, or `RuleMatch`.
- No predicate-like production function exposed to engine callers returns raw `bool`, tuple, or ad hoc result dictionary.
- Compatibility projections are one-way output adapters and are never fed back into typed evaluators, caches, conditions, Yoga, or Career.
- Conditions preserve typed child results; Yoga and Career retain typed internal outcomes before public projection.

### Layer/import boundaries

- Predicate preparation/evaluation does not import interpreter, public output, frontend/API, snapshot, test instrumentation, or raw Surya/provider modules.
- Yoga factual evaluation does not import Career/domain/public-output layers.
- Career factual evaluation does not import Yoga public output, generic legacy registry warmth, raw Surya/provider objects, snapshot/frontend/API layers, or retired modules.
- Core typed models/serialization do not import handlers, loaders, domain interpreters, public assemblers, clocks, randomness, filesystem, network, or tests.
- Tests may import production; production must never import `tests` or testing helpers.

### Side-effect boundaries

- Predicate handlers/evaluator, condition evaluator, Yoga typed evaluation, and Career typed evaluation perform no filesystem/network/subprocess I/O.
- They perform no CWD/environment discovery and no import-time data loading.
- They do not use uncontrolled wall-clock time, UUID/random identity, process/hash randomization, object identity, or memory addresses in logical data.
- They do not mutate AstroState, prepared state, parameters, registry definitions, result objects, cached values, rule definitions, or caller-owned collections.
- Producer/enrichment computation is not invoked from the factual evaluation boundary.

Scope AST checks to executable `.py` files and document explicit exceptions. Reports, prompts, archived documents, strings in negative tests, generated environments, and unrelated subsystems must not create false failures.

## Phase 2 — mutation and purity enforcement

Add runtime tests using guarded/frozen/sentinel inputs that fail on:

- attribute assignment;
- mapping/list/set mutation;
- alias retention followed by caller mutation;
- registry mutation or rebinding during evaluation;
- filesystem access (`open`, `Path` reads/writes, glob/walk);
- network/subprocess access;
- environment/CWD access;
- raw provider/Surya access;
- producer/enrichment invocation;
- clock/UUID/random access for logical fields.

Cover at minimum:

- all canonical registered predicate IDs and aliases;
- prepared predicate state and digest generation;
- cold/warm evaluator and cache paths;
- leaf and nested AND/OR/NOT conditions, including short-circuit/skipped children;
- typed Yoga batch and its public compatibility projection;
- typed Career preparation/batch and its public projection;
- typed tooling trace/coverage projections introduced in WP16.

Tests must distinguish logical behavior from permitted optional telemetry. Do not ban an injected monotonic clock used solely for excluded duration telemetry, but prove that changing it cannot alter logical bytes or public output.

## Phase 3 — safe error, evidence, and trace enforcement

Build a cross-layer matrix covering matched, unmatched, missing capability, invalid input/definition, controlled error, timeout, and skipped outcomes where supported.

Enforce:

- stable bounded error codes and fixed safe messages;
- deterministic, recursively frozen details containing only approved scalar/collection types;
- no `str(exc)`, `repr(exc)`, traceback, exception class/module, absolute path, object address, secret/token, raw payload, or uncontrolled caller value in logical/public errors;
- factual evidence describes actual observations and does not fabricate unavailable data;
- unmatched is never used for missing/invalid/error/timeout/skipped;
- trace step IDs, parent-child relationships, ordering, and lineage are deterministic;
- short-circuited condition children are represented truthfully as skipped where the contract requires them;
- Yoga and Career retain internal typed non-factual outcomes even when the unchanged public compatibility projection omits them;
- telemetry remains excluded from logical serialization.

Use adversarial sentinel exceptions and values containing temporary absolute paths, memory-address-like text, newlines, credential-shaped strings, and unstable representations. Assert absence from logical bytes, public JSON, trace/evidence output, and tooling artifacts. Do not include real credentials or personal data in fixtures.

## Phase 4 — serialization enforcement

Create a single cross-model serialization contract matrix for:

- predicate models/results;
- condition results and child trees;
- prepared state/digest projections;
- Yoga typed records/batches;
- Career prepared facts, facts, evaluations, and batches;
- WP16 typed tooling projections.

For every supported logical/full serializer, prove:

- strict JSON; compact UTF-8; finite numbers only;
- deterministic key/value/list ordering under the defined contract;
- duplicate-key rejection on parsing;
- rejection of unsupported objects and non-finite numbers;
- round-trip preservation of identity-bearing fields;
- deep immutability after parsing;
- lowercase SHA-256 of exact bytes;
- logical projection excludes duration, cache-hit, timestamps, and all other approved telemetry;
- full projection may include approved telemetry but never unsafe/unserializable data;
- public compatibility mappings preserve their independently locked key/list order and exact bytes;
- repeated serialization returns fresh bytes/data without mutating the source.

Do not impose sorted-key public JSON where the established public contract preserves insertion order. Logical canonical identity and public compatibility ordering are separate contracts.

## Phase 5 — deterministic scenario harness

Add a bounded subprocess determinism harness that runs an explicit scenario manifest rather than relying on pytest discovery randomness.

The manifest must cover:

1. all registered predicate IDs/aliases on fixed matched, unmatched, and relevant non-factual fixtures;
2. equivalent independently constructed prepared states;
3. cold and warm cache evaluation;
4. cache eviction/bounds and re-evaluation;
5. nested condition evaluation and short-circuit cases;
6. Yoga normal/reverse/A/B/C explicit rule permutations;
7. generic-loader then Yoga-loader and Yoga-loader then generic-loader order;
8. Career fixed fixtures and repeated projection;
9. WP16 tooling artifact and coverage generation to unique temporary paths;
10. repeated serialization/parse/round trip.

Run each scenario:

- twice in one process;
- in at least two fresh processes per Python lane;
- under at least two explicit `PYTHONHASHSEED` values per lane;
- with two explicit safe working directories where the contract is CWD-independent;
- cold and warm where cache/loader state applies.

The harness must emit a compact manifest of scenario name, logical byte length, SHA-256, and public/artifact SHA-256 where applicable. It must compare exact bytes, not only parsed equality. Sort the manifest by an explicit stable scenario order, not filesystem or set iteration.

Do not add a random-order pytest plugin or use nondeterministic shuffling. Use explicit recorded permutations only.

## Phase 6 — cache and registry isolation gates

Enforce:

- cache key includes canonical predicate ID/version, normalized parameters, prepared-state digest/version, and behavior-changing context;
- aliases share canonical identity only where explicitly defined;
- logical cold/warm results are byte-identical;
- cached values cannot be mutated by callers;
- telemetry cannot contaminate logical identity;
- capacity is bounded and eviction deterministic;
- failures/non-factual outcomes follow the approved caching policy;
- isolated registries do not contaminate the canonical registry;
- duplicate/alias/version/schema/capability validation remains deterministic;
- registry object identity is preserved where the supported loader contract requires it;
- loader source discovery and duplicate precedence are stable across order and CWD scenarios.

Do not add persistent/distributed caching or change the approved cache policy.

## Required validation

Run in both Python 3.14.6 and Python 3.11.9 with bytecode/cache writes disabled and unique temporary workspaces:

- focused WP17 architecture tests;
- focused WP17 purity/safety tests;
- focused WP17 serialization tests;
- focused WP17 determinism/subprocess tests;
- WP02–WP17 contract suites;
- all `tests/rules`;
- Yoga and Career integration/characterization suites;
- WP16 tooling tests;
- collection comparison;
- full suite twice per lane;
- explicit Yoga permutations and loader trigger orders;
- rule lint proving all supported `.yml`/`.yaml` files inspected exactly once;
- strict approved-snapshot comparison twice per lane without update mode;
- `git diff --check`.

Record exact commands, versions, counts, skips, node-ID hash, scenario-manifest bytes/hash, per-scenario hashes, Career public hashes, Yoga hashes, tooling hashes, snapshot hashes, and cross-version comparison.

WP17 tests must be safe for normal pytest collection: no fixed-path writes, network, external services, current-time dependence, random ordering, or environment mutation leakage.

## Forbidden changes

Do not:

- change predicate/Yoga/Career astrology semantics;
- add or activate predicates/rules;
- change rule files, weights, tables, candidate sets, formulas, confidence, narrative, evidence policy, or public schemas;
- update snapshots/goldens/fixed artifacts;
- add dependencies, type-checkers, formatters, CI steps, workflow edits, or broad repository tooling;
- add persistent/distributed cache or concurrency redesign;
- implement future `InferenceEngine`, universal `RuleMatch`, `DomainPrediction`, or `OutputAssembler`;
- weaken/delete prior assertions or broaden allowlists merely to obtain green results;
- start WP18.

## Required WP17 report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP17/WP17.md`

The report must include:

1. `VERDICT: COMPLETE` or `VERDICT: BLOCKED`;
2. `WP18_READY: YES` or `WP18_READY: NO`;
3. model and reasoning level used;
4. prerequisite and inherited-worktree evidence;
5. reproduced WP16 baseline;
6. exact architecture rules, scopes, and narrowly justified allowlists;
7. runtime purity/mutation/I/O/time/random/provider/producer enforcement matrix;
8. error/evidence/trace adversarial safety matrix;
9. cross-model logical/full/public serialization matrix;
10. deterministic scenario manifest and execution dimensions;
11. cache and registry isolation/identity/bounds evidence;
12. every discovered violation and minimal fix, or explicit statement that production was unchanged;
13. test-to-P0/P1 Stage-01 requirement traceability;
14. exact dual-lane commands, counts, skips, node-ID hash, and repeated-run results;
15. fresh-process/hash-seed/CWD/cold-warm/cross-version bytes and hashes;
16. Yoga, Career, tooling, lint, loader-order, snapshot, public API, and artifact compatibility evidence;
17. changed-file inventory separated from inherited changes;
18. deferred WP18/WP19 and future-stage work;
19. explicit proof WP18 was not started.

## Definition of done

WP17 is complete only when:

- WP16 remains complete and reproducible;
- all required architecture boundaries are executable and green;
- purity and mutation sentinels cover every typed factual layer;
- safe errors/evidence/traces are enforced against adversarial unstable values;
- every supported model has canonical logical/full serialization enforcement;
- logical identity excludes all telemetry;
- deterministic scenario bytes match across repeats, processes, hash seeds, safe CWDs, cold/warm state, and Python lanes;
- cache bounds/identity/isolation and registry/loader determinism are enforced;
- no legacy/raw boundary or forbidden dependency is reintroduced;
- Career, Yoga, tooling, rule content, public output, and approved snapshots remain unchanged;
- the complete dual-lane suite is green twice;
- the report records `VERDICT: COMPLETE` and `WP18_READY: YES`.

At the end, return a concise summary with verdict, model/reasoning, gates added, violations/fixes, deterministic manifest/hash results, dual-lane counts, Career/Yoga/tooling/snapshot compatibility, changed files, deferred work, and WP18 readiness. **Do not proceed to WP18.**