Implement **WP16 — migrate all remaining callers and retire the active legacy rule-runtime adapters** for Prompt-01.

Do not merely review this specification. Perform the repository-first inventory, add characterization where necessary, implement the narrow migration/removal, validate both locked Python lanes, and create the WP16 completion report. **Do not proceed to WP17.**

## Objective

Complete the boundary cleanup established by WP02–WP15:

- remove every active caller of `evaluate_rule_with_score`, `evaluate_rule`, and the four raw-Boolean legacy factual helpers;
- migrate the remaining test and artifact/coverage tooling to the typed predicate, condition, Yoga, and Career contracts already implemented;
- retire the legacy runtime adapters and any compatibility-only bootstrap/instrumentation coupling when proven unused;
- remove compatibility-only `RuleMatch` construction/serialization if and only if no independently valid caller remains;
- retain generic/Yoga loader functionality only where a current typed path still requires it;
- preserve all production outputs, Career calculations, Yoga behavior, rule files, approved snapshots, artifact schemas, deterministic order, and public APIs exactly.

WP16 is **not** the shared `InferenceEngine`, universal rule compiler, `DomainPrediction`, `OutputAssembler`, public-schema redesign, rule-language redesign, or astrology-semantics package.

## Hard preflight gate

Before editing production code:

1. Locate and read by exact filename:
   - the locked Prompt-01 decisions/execution plan;
   - `Prompt-01-Final-Audit-Consolidation.md`;
   - final WP00-R and WP01 reports;
   - WP02 through WP15 completion reports;
   - Audits 02, 03, 04, 07, 08, 10, 12, 14, 16, 17, 18, 19, 21, 22, and 25.
2. Require every predecessor through WP15 to record `VERDICT: COMPLETE` and WP15 to record `WP16_READY: YES`.
3. Record the inherited dirty worktree without restoring, deleting, staging, or overwriting unrelated work.
4. Reproduce the current WP15 baseline in both locked environments:
   - Python 3.14.6;
   - Python 3.11.9.
5. Require identical collected node IDs between lanes, two clean full-suite runs per lane, Yoga order isolation, both loader orders, rule lint, and strict approved-snapshot comparison.
6. Capture exact current outputs/hashes for every test/tool surface that still calls a legacy symbol.

The expected inherited WP15 evidence is 757 identical collected tests, 755 passed and 2 optional skips in each repeated full run per lane, five linted rule files exactly once, unchanged approved snapshot SHA-256 `da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`, and byte-identical Career public output across lanes. Treat these as evidence to reproduce, not values to force if legitimate new tests increase collection.

If any prerequisite fails, stop without production edits and report:

```text
VERDICT: BLOCKED
WP17_READY: NO
```

## Owner-approval boundary

Do not change production astrology semantics, rule/YAML content, weights, Career scoring/confidence/narrative, public schemas, approved snapshots, dependencies, or CI configuration without separate explicit owner approval.

No such change is expected for WP16. If migration appears to require one, stop and report the exact blocker rather than approximating behavior or updating a golden.

## Phase 1 — authoritative live inventory

Build a symbol-level definition/import/call/reference inventory for:

- `in_sign`;
- `in_house`;
- `lord_of_house`;
- `is_exalted`;
- `evaluate_rule`;
- `evaluate_rule_with_score`;
- `RuleMatch`;
- `RULE_REGISTRY`, `load_rules_from_dir`, `get_rule`, runtime auto/lazy load, and Yoga registry/loader symbols;
- `record_predicate` and legacy test instrumentation;
- `tests/testing_framework/generate_full_artifacts.py`;
- `tests/testing_framework/rule_coverage.py`;
- `systems/Parasara/tests/test_rule_runtime.py`;
- `systems/Parasara/tests/test_rule_runtime_merge.py`.

Classify every occurrence as:

1. active production caller;
2. active test/tool caller;
3. definition or self-call;
4. compatibility export/import;
5. assertion/negative architecture test;
6. documentation/report/prompt/history only;
7. unrelated same-name symbol.

Do not count documentation text as an active caller. Do not remove a symbol based only on its filename or on WP15's earlier inventory; verify the current repository.

The starting expectation from WP15 is:

- Career production callers: zero;
- active definitions/self-calls: `engine/rules/runtime.py`;
- direct test callers: `test_rule_runtime.py` and `test_rule_runtime_merge.py`;
- direct tooling callers: `generate_full_artifacts.py` and `rule_coverage.py`;
- generic loader/Yoga compatibility may still have independent typed callers and must be decided separately.

Record deviations before implementation.

## Phase 2 — freeze remaining compatibility behavior

Before replacing a remaining caller, add focused tests that capture its externally observable contract:

- exact artifact filename/schema/key order where contractually relevant;
- record ordering and inclusion/omission rules;
- factual matched/unmatched/non-factual treatment;
- evidence and trace projection;
- coverage numerator/denominator and reported identifiers;
- duplicate-ID/source precedence if the surface observes it;
- deterministic bytes and SHA-256 where artifacts are stable;
- cold/warm and loader-order independence;
- safe error projection with no raw exception, path, traceback, or object leakage;
- no writes to tracked/fixed artifacts during tests.

Use unique temporary directories. Do not regenerate or approve fixed snapshots. Do not weaken or delete assertions merely because the legacy implementation is being removed.

## Phase 3 — migrate artifact generation

Refactor `tests/testing_framework/generate_full_artifacts.py` so its factual/rule trace generation uses the appropriate typed public contracts rather than the legacy runtime.

Requirements:

- Use the WP09 canonical evaluator for registered predicates, WP12 typed condition evaluation, WP13 typed Yoga execution, and WP15 typed Career batch only where each is the exact semantic owner.
- Do not introduce a new general-purpose rule evaluator, new inference engine, or new rule semantics.
- Preserve any currently approved artifact schema and deterministic ordering that downstream tests actually consume.
- If a legacy artifact represents obsolete `RuleMatch` internals and has no approved consumer, do not silently invent a replacement. Prove it is unused and either remove that artifact path with focused tests/documentation or retain a compatibility projection sourced from typed results.
- A compatibility projection must be one-way, fresh/detached, deterministic, safely lossy, and must never become a typed engine input.
- Never expose raw exception text/type/traceback/path.
- Remove imports/calls to legacy runtime and mutable generic registry warmth.

## Phase 4 — migrate coverage tooling

Refactor `tests/testing_framework/rule_coverage.py` and its tests away from runtime instrumentation and raw Boolean helpers.

Coverage must be based on explicit typed evaluation records, stable IDs/versions, and deterministic source order. It must not depend on:

- `record_predicate` side effects;
- global mutable “seen predicate” state;
- import order;
- CWD-sensitive discovery;
- test execution order;
- raw handler invocation;
- legacy runtime dictionaries.

Preserve the existing user-visible coverage contract where it is meaningful. If the old metric counted implementation calls rather than semantic evaluation, document the exact translation and keep the result compatible for fixed fixtures unless the prior value was demonstrably non-contractual. Do not claim coverage for rules/predicates that were not actually inspected.

## Phase 5 — replace legacy-runtime tests

The existing runtime tests must not remain as callers merely to keep dead APIs alive.

- Translate still-relevant behavioral assertions into tests of the canonical typed predicate/condition/Career boundary that now owns the behavior.
- Preserve explicit characterization of semantic differences rather than treating superficially similar predicates as interchangeable.
- In particular, do not reinterpret sign-based legacy exaltation as equivalent to the canonical `PLANET_EXALTED` contract without owner approval.
- Retain loader precedence/provenance tests only against a currently supported loader/compiler consumer.
- Remove tests whose sole purpose is exercising a retired adapter after equivalent behavior and migration safety are proved elsewhere.
- Add negative tests proving no production/test/tool execution imports or calls the retired runtime.

Do not reduce the net strength of the suite. Any deleted test must have a report mapping to its replacement assertion or a proof that it tested only an intentionally retired implementation detail.

## Phase 6 — retire adapters and compatibility-only code

After all active callers have migrated:

1. Remove `evaluate_rule_with_score`, `evaluate_rule`, and the raw factual helpers from the active codebase.
2. Remove runtime import-time/lazy loader bootstrap and its broad exception swallowing.
3. Remove compatibility-only instrumentation imports/side effects.
4. Delete `runtime.py` if it has no independently valid responsibility; otherwise reduce/rename it so none of the retired adapters or raw contracts remain.
5. Remove `RuleMatch` only if repository-wide inventory proves it has no valid nonlegacy consumer. If retained, document its exact owner and prohibit its use as a predicate/condition/domain result.
6. Remove dead exports/imports/tests created solely for these adapters.
7. Do not remove generic `loader.py`, `RULE_REGISTRY`, or Yoga loader/registry merely because the legacy runtime used them. Keep, narrow, or remove each only according to verified current typed callers.

No deprecation shim that still returns a raw Boolean/dictionary/tuple is acceptable as an “implementation.” There must be zero active callers and zero executable compatibility path.

## Required architecture invariants

Add or extend architecture tests proving:

- zero production/test/tool callers of all retired legacy symbols;
- zero raw-Boolean factual producer used as an engine boundary;
- zero tuple/dictionary predicate-result consumer;
- no direct registered-predicate handler calls outside approved evaluator internals/tests;
- no Career dependency on runtime, generic registry, loader warmth, or CWD;
- no artifact/coverage dependency on mutable global instrumentation;
- no broad exception-to-unmatched conversion at the removed boundary;
- no import-time generic rule loading for retired runtime behavior;
- typed results remain immutable and projections are detached;
- Yoga and Career public paths remain unchanged.

AST/import analysis should inspect executable Python, not reports or Markdown. Allow explicit symbol strings only in negative architecture tests and migration reports.

## Determinism and compatibility requirements

Prove in both Python lanes:

- identical collected node IDs and node-ID SHA-256;
- focused WP16 tests pass;
- WP02–WP16 contract tests pass;
- all rules tests pass;
- full suite passes twice in fresh temporary workspaces;
- Yoga normal/reverse/A/B/C permutations pass;
- generic-loader/Yoga and Yoga/generic-loader trigger orders pass if both loaders remain;
- lint scans every supported `.yml` and `.yaml` rule file exactly once;
- strict approved snapshot comparison passes twice without update mode;
- all fixed Career public bytes/hashes remain identical to WP15;
- affected artifact and coverage outputs are repeatable cold/warm, across fresh processes, and across Python versions;
- approved snapshot and tracked test artifacts remain byte-for-byte unchanged;
- `git diff --check` passes, aside from explicitly inherited warnings.

If a generic loader is retained, add deterministic duplicate/source-order tests and prove no stale-reference rebind behavior is reintroduced. If it is removed, prove no supported loader/Yoga/Career/tool path imports it.

## Forbidden changes

Do not:

- change astrology doctrine or predicate meaning;
- activate `HOUSE_LORDS_COMBINATION` or add new predicates;
- change Career candidate set/order/denominator/contributions/formulas/confidence/components/indicators/evidence/summary/scoring/trace ID;
- change Yoga match semantics, ordering, public projection, or hashes;
- change rule/YAML/table content or weights;
- change public API/frontend schemas;
- update approved snapshots or fixed tracked artifacts;
- add dependencies, random-order plugins, or CI changes;
- build the shared inference/domain/output architecture reserved for later work;
- start WP17.