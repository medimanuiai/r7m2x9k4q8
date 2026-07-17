Implement **WP10 — add the immutable canonical `ConditionResult` model and deterministic `AND`/`OR`/`NOT` condition evaluator** for Prompt-01.

Do not merely review this specification. Implement the permitted work, run all validation gates in both locked Python lanes, and create the WP10 completion report. **Do not proceed to WP11.**

## Objective

Build a canonical condition boundary over the WP09 `PredicateEvaluator` that:

- represents every logical node with a deeply immutable typed `ConditionResult`, never a predicate result mislabeled `AND` or `OR`;
- preserves complete evaluated child results recursively;
- represents unevaluated short-circuited children explicitly and deterministically;
- evaluates children left-to-right;
- implements deterministic short-circuiting for `AND` and `OR`;
- implements `NOT` with exactly one child;
- rejects empty `AND`/`OR`, invalid `NOT` arity, malformed nodes, unknown operators, and unknown definitions as typed failures rather than factual false;
- applies a locked mixed-status precedence policy without flattening errors, evidence, or traces;
- keeps telemetry outside logical equality/serialization;
- preserves current valid legacy/Yoga truth values and public outputs while leaving active Yoga on its compatibility path until WP13.

WP10 owns canonical condition models and canonical logical evaluation. WP11 migrates the remaining predicate handlers. WP12 validates active formats/loaders. WP13 migrates Yoga. Do not pull those packages forward.

## Hard prerequisite gate

Before editing:

1. Locate final WP00-R and WP01–WP09 reports by exact filename.
2. Confirm WP09 records `VERDICT: COMPLETE` and `WP10_READY: YES`.
3. Confirm the WP09 canonical evaluator is instance-owned, bounded to 256 by default, caches only matched/unmatched results, and has no canonical process-global cache.
4. Reproduce the current Python 3.14 and 3.11 baseline: identical collection IDs, clean full suites, all Yoga permutations and loader orders, five-file lint, and strict approved snapshot comparison.
5. Record and preserve the inherited dirty worktree.

If any gate fails, stop without production edits and report `VERDICT: BLOCKED` and `WP11_READY: NO`.

## Required references

Read the current implementation plus:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP02–WP09 reports;
- Audit 05, 06, 12, 13, 14, 17, 18, 19, 20, 21, and 22 reports.

Resolve moved documents by filename. Treat completion reports as implementation evidence and audits as defect/test inventories.

## Strict scope

### Permitted

- Add canonical immutable condition models/enums in a dedicated module or the existing canonical model module.
- Add a canonical condition evaluator that consumes the WP09 `PredicateEvaluator` instance.
- Support the current bare-node compatibility grammar used by direct evaluation and active Yoga trees: logical `{type, children}` and leaf `{type, params}`.
- Add runtime structural validation sufficient to make canonical evaluation safe and deterministic.
- Add focused model/operator/serialization/purity tests.
- Keep a temporary explicit legacy `evaluate_condition` adapter unchanged or isolated until later migration.
- Add the WP10 report.

### Forbidden

- Do not migrate `HOUSE_OCCUPANT`, `ASPECT`, `ASPECT_EXISTS`, `FUNCTIONAL_ROLE`, or `PLANET_EXALTED`.
- Do not activate, register, remove, or reinterpret `HOUSE_LORDS_COMBINATION`.
- Do not modify Yoga execution, Yoga loaders/rules, Career/runtime, rule files, public schemas/output, dependencies, CI, snapshots, or approved artifacts.
- Do not implement the future `op/args`, canonical AST/compiler, macros, references, `ALL`, `ANY`, `EXISTS`, `COUNT`, reusable blocks, or external fragments.
- Do not cache complete `ConditionResult` trees in WP10.
- Do not change astrology semantics or infer missing facts.

If a protected behavior or astrology decision is required, stop and request owner approval.

## Canonical input boundary

The canonical evaluator must accept:

- a raw current-format bare node;
- `PreparedAstroState`;
- `PredicateEvaluationContext`;
- an explicit WP09 `PredicateEvaluator` instance;
- an optional caller-supplied stable root node ID/path, with a deterministic default that does not depend on object identity.

Supported current-format nodes only:

```text
logical: {"type": "AND"|"OR"|"NOT", "children": [...]}
leaf:    {"type": <registered predicate ID>, "params": {...}}
```

Operator/predicate type values may follow the existing case/trim normalization only. Do not accept alternate field names or future DSL forms.

Structural validation must reject safely:

- non-mapping/null root or child;
- missing, blank, non-string, or unknown `type`;
- unknown logical operator;
- logical node with missing/null/non-sequence/non-list `children`;
- empty `AND` or `OR`;
- `NOT` with zero or more than one child;
- leaf with `children`;
- logical node with `params`;
- leaf with missing/null/non-mapping `params` where the existing schema does not allow it;
- unknown/misspelled fields rather than ignoring them;
- cycles and excessive nesting.

Use a documented finite maximum depth and maximum total node count. Preferred conservative bounds: **64 levels** and **4096 nodes**. These are safety limits, not astrology semantics. If an approved existing limit exists, use it and report the resolution.

WP12 will validate loader/file formats. WP10 validation applies only at the canonical runtime boundary.

## Required condition models

Use the existing WP02 `PredicateStatus`, `PredicateError`, `PredicateTraceStep`, and `PredicateResult`; do not duplicate them.

Add a minimal exact immutable condition contract with equivalent repository naming. It must represent:

### `ConditionOperator`

Exactly `AND`, `OR`, and `NOT` as stable string values.

### `ConditionNodeDisposition`

Exactly:

- `evaluated`;
- `skipped`.

### `ConditionChildResult`

Required fields:

- stable `node_id`;
- zero-based `child_index`;
- `disposition`;
- exactly one evaluated result (`PredicateResult` or nested `ConditionResult`) when evaluated;
- no result plus a stable `skip_reason` when skipped.

Invariants must reject contradictory evaluated/skipped combinations. Preserve declared child order.

### `ConditionResult`

Required logical fields:

- stable `node_id`;
- `operator`;
- `matched` strict Boolean;
- `status` using the existing `PredicateStatus` truth vocabulary;
- immutable canonical node inputs/details sufficient to identify the operator and arity without retaining the raw node;
- ordered tuple of all `ConditionChildResult` values, including skipped children;
- ordered typed errors owned by the logical node only;
- ordered typed trace steps owned by the logical node;
- optional finite nonnegative `evaluation_time_ms` telemetry.

Do not add `cache_hit` to `ConditionResult`; leaf cache telemetry remains inside preserved predicate children and must be excluded from the condition logical projection.

The model must be deeply immutable, reject cycles/unsafe values, isolate caller-owned data, enforce `matched=True` iff `status=matched`, and use logical equality that excludes only condition telemetry and descendant predicate telemetry.

If the existing canonical model conventions require slightly different field names, preserve the semantics above and document the exact final inventory. Do not add unrelated AST/source/public fields.

## Leaf representation

A leaf evaluation returns the canonical WP02 `PredicateResult` inside its parent's `ConditionChildResult`; do not flatten or copy only selected fields.

When the root itself is a leaf, expose one documented canonical outcome type:

- preferred: return the canonical `PredicateResult` directly; or
- if a uniform root `ConditionResult` wrapper is required by existing architecture, use an explicit `LEAF` node kind without pretending it is an operator.

Do not invent `AND` with one child as a leaf wrapper. Document and test the selected policy.

WP10 canonical tests may use `PLANET_IN_HOUSE` leaves because it is the only migrated predicate. A known but unmigrated predicate must retain WP09's typed `predicate_not_migrated` result and must not fall back to the legacy evaluator.

## Locked operator semantics

Evaluate declared children left-to-right.

### `AND`

- Continue through `matched` children.
- Stop at the first `unmatched` child because factual false is decisive.
- Mark every remaining child as skipped with reason `and_short_circuit_unmatched`.
- A non-factual child (`error`, `timeout`, `invalid_parameters`, `missing_capability`, or `skipped`) is not factual false. Continue evaluation to preserve the possibility of discovering a decisive factual unmatched child, subject to the precedence rule below.
- If all children match, parent is `matched`.
- If an unmatched child occurs with no previously evaluated non-factual child, parent is `unmatched`.
- If a non-factual child occurred before the decisive unmatched child, parent uses the highest non-factual precedence rather than claiming an ordinary factual unmatched result.
- If no unmatched occurs and at least one non-factual child exists, use the highest non-factual precedence.

### `OR`

- Continue through `unmatched` and non-factual children.
- Stop at the first `matched` child because factual true is decisive.
- Mark every remaining child as skipped with reason `or_short_circuit_matched`.
- A decisive matched child produces parent `matched` even if an earlier child was non-factual; the preserved children reveal that earlier issue.
- If no child matches and all evaluated children are unmatched, parent is `unmatched`.
- If no child matches and any child is non-factual, use the highest non-factual precedence rather than claiming ordinary factual unmatched.

### `NOT`

- Require exactly one child.
- Child `matched` becomes parent `unmatched`.
- Child `unmatched` becomes parent `matched`.
- Any non-factual child status propagates unchanged.
- Preserve the complete child result and do not invert or discard its evidence/errors/trace.

### Mixed non-factual precedence

Use this stable precedence, highest first:

1. `error`;
2. `timeout`;
3. `invalid_parameters`;
4. `missing_capability`;
5. `skipped`.

If the approved locked decision record contains a different explicit ordering, use it, document the exact conflict, and lock that approved order in tests. Never collapse these statuses into unmatched.

Parent errors must reference child node IDs/error codes safely rather than flattening or duplicating raw child details. A parent may carry one stable summary error for the decisive/highest status while the complete typed child errors remain preserved in the child tree.

## Skipped-child contract

Every declared child must appear exactly once in the parent `children` tuple.

For skipped children:

- assign the deterministic path-derived node ID that the child would have used;
- store its index and `disposition=skipped`;
- store no evaluated result;
- use only the locked operator-specific skip reason;
- never inspect, validate deeply, execute, cache, or derive factual evidence from its subtree after short-circuit;
- add a deterministic parent-owned trace step describing the skip without copying raw subtree values.

Root structural validation may validate the overall node shape and cycle/depth/node limits before execution, but it must not execute or semantically validate skipped leaf parameters.

## Node IDs and trace lineage

Use stable path-derived IDs such as `condition.root`, `condition.root.children.0`, and nested extensions. IDs must depend only on declared tree position and optional caller root ID, never UUID, time, object identity, hash iteration, or memory representation.

Each logical result must have deterministic typed trace steps for:

1. operator validation/start;
2. each child evaluation result or skip decision in declared order;
3. short-circuit decision when applicable;
4. status-precedence selection when applicable;
5. final disposition.

Preserve child trace trees inside child results; do not flatten them into the parent trace. Parent steps reference child node IDs. Exclude timing/cache telemetry, raw nodes, exception strings, paths, and provider values from logical trace content.

## Evidence and error boundary

Do not synthesize flattened aggregate factual evidence. The recursive child tree is the authoritative evidence container.

Logical-node details may include only stable facts such as operator, declared/evaluated/skipped counts, decisive child ID/index, and final precedence source. Do not duplicate arbitrary child evidence.

Malformed structure, unknown operator/definition, depth/node-limit, cycle, or unexpected evaluator defect must return a typed canonical failure; never raise uncontrolled exceptions to callers and never return ordinary false. Use stable safe error codes/details and no raw values, repr, exception text, traceback, filesystem path, or object identity.

## Canonical serialization

Extend WP03 using model-owned projections; do not create an unrelated serializer.

Provide and test:

- logical data/UTF-8 bytes/lowercase SHA-256 for `ConditionResult` trees;
- full/telemetry projection if consistent with WP03 conventions;
- recursive serialization of evaluated `PredicateResult` and nested `ConditionResult` children;
- explicit skipped-child representation;
- deterministic enum/string and mapping ordering;
- round trip if WP03 currently requires it for canonical models;
- rejection of unsupported/unsafe values;
- exclusion of condition durations and descendant predicate `cache_hit`/durations from logical bytes;
- preservation of child order, trace order, status, errors, and skip reasons.

Equivalent cold/warm leaf trees must yield identical condition logical equality/bytes/hash. Full projection may differ only in already-approved telemetry fields.

Do not use `asdict`, `default=str`, repr, pickle, arbitrary model dumping, or Python `hash()`.

## Evaluator/cache interaction

The condition evaluator must receive and reuse one explicit WP09 evaluator instance for all evaluated leaves.

- Skipped leaves must not call the evaluator and must not warm/promote cache entries.
- Evaluated repeated equivalent leaves may use WP09 caching normally.
- Condition trees themselves are not cached.
- Cache-hit differences in child predicate telemetry must not alter condition logical equality/bytes/hash/status.
- Do not clear/freeze the caller's evaluator cache implicitly.

## Compatibility boundary

Do not redirect active Yoga, Career, loader, or legacy runtime paths in WP10. Keep existing legacy condition entry points as explicit temporary compatibility paths.

Prove:

- current valid Yoga firing, order, evidence/public projection, and snapshots remain unchanged;
- existing direct legacy `evaluate_condition` behavior required by characterization remains compatible unless a test asserted an intentionally replaced canonical-only contract;
- WP10 canonical evaluator never falls back to Yoga-local or flat runtime helpers;
- no `HOUSE_LORDS_COMBINATION` behavior changes;
- registry inventory and all handler identities remain unchanged.

WP13 will migrate Yoga after WP11/WP12 make all active leaves and formats safe.

## Tests first

Create focused model and evaluator tests before production edits. Cover at least:

### Models/invariants

- exact enum values and exact field inventories;
- every valid status/matched invariant;
- evaluated/skipped child invariants;
- mixed predicate/nested-condition children;
- deep immutability, caller mutation isolation, unsafe values, cycles;
- logical equality excluding all recursive telemetry;
- exact logical/full serialization and round trip where applicable.

### Input validation

- valid leaf and nested `AND`/`OR`/`NOT` current-format nodes;
- case/trim normalization;
- non-mapping/null roots/children;
- missing/blank/non-string/unknown types;
- unknown fields and future DSL aliases rejected;
- children missing/null/empty/non-list;
- empty `AND` and `OR` rejected;
- `NOT` zero/one/multiple arity;
- leaf-with-children, logical-with-params, malformed params;
- unknown predicate and known-unmigrated predicate typed failures;
- cycle, depth 64/65 boundary, and node-count 4096/4097 boundary without recursion crash.

### `AND`

- all matched;
- early and later unmatched;
- unmatched first skips later invalid/error leaf without executing it;
- error/invalid/missing/timeout followed by unmatched applies precedence;
- mixed non-factual statuses use exact precedence;
- no unmatched plus non-factual status;
- exact child order, evaluated/skipped dispositions, decisive ID, trace, and evaluator-call count.

### `OR`

- early and later matched;
- all unmatched;
- matched first skips later invalid/error leaf without executing it;
- error/invalid/missing/timeout then matched produces matched while preserving prior child;
- no match plus non-factual statuses uses exact precedence;
- exact child order, dispositions, decisive ID, trace, and call count.

### `NOT`

- matched to unmatched;
- unmatched to matched;
- exact propagation of error, timeout, invalid, missing, and skipped;
- full child evidence/error/trace preservation;
- arity failures never execute children.

### Recursion/trace/serialization

- nested mixed operators;
- stable path IDs and parent/child trace references;
- skipped nested subtree not evaluated or cached;
- no flattened child information loss;
- cold/warm leaf trees logically and byte/hash identical;
- mapping insertion order and equivalent independently created trees serialize identically;
- meaningful child/order/status/skip changes alter logical bytes/hash;
- fresh-process and Python 3.14/3.11 bytes/hashes identical.

### Compatibility/purity

- WP09 cache ownership/bounds/status policies remain intact;
- canonical condition module imports no mutable AstroState/raw provider, Yoga, Career, loader, producer, filesystem/network/environment/random/UUID;
- time source, if used, affects only condition telemetry;
- no input/state/context/registry/cache/global mutation except normal explicit leaf cache operations;
- Yoga/Career/legacy/rules/public snapshot remain unchanged.

Do not weaken or delete existing tests and never update the approved snapshot.

## Validation gates

Run in both locked Python 3.14 and 3.11 lanes with bytecode/cache isolation and unique ignored temporary paths:

1. WP10 condition model/operator/serialization focused tests.
2. WP02–WP09 focused modules.
3. All `tests/rules`.
4. WP01 predicate/Yoga/Career characterization.
5. Targeted evaluator/cache/legacy-condition, Yoga, Career, runtime, role, Aspect, writer, linter, determinism, and snapshot regression tests.
6. Exact full collection comparison and node-ID SHA-256.
7. Complete suite twice from fresh processes per lane.
8. Yoga normal/reverse/A/B/C permutations.
9. Both loader-trigger orders.
10. Rule lint proving all five supported files, including `yogas.yaml`, are inspected exactly once.
11. Strict approved-snapshot comparison twice per lane using temporary output and no update mode.
12. Fresh-process/cross-version representative nested-condition logical/full bytes and hashes, including cold/warm leaf variants.
13. `git diff --check` and scoped tracked-artifact checks.

Record exact commands, versions, counts, node-ID hash, condition byte lengths/hashes, evaluator call sequences, skipped/cache behavior, and compatibility evidence. Treat protected factual/public differences as blockers.

## Required completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP10/WP10.md`

The report must include:

1. `VERDICT: COMPLETE` or `VERDICT: BLOCKED`;
2. `WP11_READY: YES` or `WP11_READY: NO`;
3. actual model/reasoning used;
4. prerequisite/baseline evidence;
5. exact files changed and APIs;
6. exact model/enumeration field inventories and invariants;
7. accepted/rejected runtime node grammar and safety limits;
8. root-leaf representation policy;
9. exact `AND`/`OR`/`NOT` truth, short-circuit, and mixed-status precedence tables;
10. skipped-child representation and reasons;
11. node-ID/trace/error/evidence lineage policy;
12. logical/full serialization inclusion/exclusion tables;
13. WP09 evaluator/cache interaction evidence;
14. test-to-requirement traceability;
15. exact dual-lane commands/counts and collection hash;
16. fresh-process/cross-version nested-tree bytes/hashes;
17. Yoga/loader/lint/snapshot/artifact compatibility evidence;
18. deferred WP11–WP13 work and any owner decision required;
19. explicit proof WP11 was not started.

## Definition of done

WP10 is complete only when:

- WP09 remains complete and reproducible;
- one deeply immutable typed condition-result tree preserves every declared evaluated or skipped child;
- every evaluated leaf retains its complete canonical `PredicateResult`;
- `AND`, `OR`, and `NOT` follow the locked left-to-right, short-circuit, arity, and mixed-status policies;
- empty/malformed/unknown/unsafe nodes never become factual false or uncontrolled exceptions;
- skipped subtrees do not execute or affect cache state;
- errors/evidence/traces retain deterministic recursive lineage without flattening or raw details;
- condition logical equality/bytes/hash exclude all condition and leaf telemetry;
- no condition-result cache, remaining-handler migration, loader/DSL, Yoga, Career, rule, public-output, CI, dependency, or snapshot change occurred;
- all dual-lane, determinism, compatibility, lint, snapshot, and artifact gates pass;
- the report records `VERDICT: COMPLETE` and `WP11_READY: YES`.

At the end, return a concise summary with the verdict, model/reasoning used, model/evaluator locations, exact operator/precedence/skip policies, serialization hashes, dual-lane counts, cache and compatibility status, files changed, deferred issues, and WP11 readiness. **Do not proceed to WP11.**