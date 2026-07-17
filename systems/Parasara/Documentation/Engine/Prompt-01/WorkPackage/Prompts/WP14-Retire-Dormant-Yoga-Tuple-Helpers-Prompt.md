Implement **WP14 — retire the five confirmed-unused Yoga-local tuple helpers and enforce the canonical Yoga boundary** for Prompt-01.

Do not merely review this specification. Remove only the proven-dormant implementation family, add negative architecture tests, run all dual-lane gates, and create the WP14 completion report. **Do not proceed to WP15.**

## Objective

Remove these five dormant symbols from `systems/Parasara/engine/enrichments/yoga_engine.py`:

- `_eval_aspect_condition`;
- `_eval_functional_role_condition`;
- `_eval_house_lords_combination`;
- `_eval_house_occupant`;
- recursive dispatcher `_eval_condition`.

Then prove that:

- active Yoga continues exclusively through WP12 validation, WP07 prepared state, WP09 evaluator, WP10 conditions, and WP11 canonical predicates;
- no tuple/raw-Boolean Yoga predicate fallback remains;
- `HOUSE_LORDS_COMBINATION` remains an unregistered typed definition error with exactly the WP12/WP13 disposition;
- no rule, firing, row order, compatibility dictionary, trace reference, state attachment, Career output, or public snapshot changes;
- no active caller, import, re-export, test, documentation example, or dynamic lookup requires any removed symbol.

This package retires unreachable code. It does **not** activate, remove, approve, reject, or reinterpret the Yoga rule concept named `HOUSE_LORDS_COMBINATION`.

## Hard prerequisite gate

Before editing:

1. Locate final WP00-R and WP01–WP13 reports by exact filename.
2. Confirm WP13 records `VERDICT: COMPLETE` and `WP14_READY: YES`.
3. Reproduce WP13's static/dynamic proof that all five symbols occur only inside the dormant family and the active pipeline does not call them.
4. Confirm active Yoga returns the exact three compatibility rows, deterministic trace IDs, typed invalid Dhana disposition, and approved attachment behavior.
5. Reproduce the Python 3.14/3.11 baseline: identical collection IDs, two clean full suites, Yoga permutations, loader orders, five-file lint, and strict snapshots.
6. Record and preserve the inherited dirty worktree.

If any symbol has an active or external caller, or any prerequisite fails, stop before deletion and report `VERDICT: BLOCKED` and `WP15_READY: NO` with exact caller evidence.

## Required references

Read the current source plus:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP12 and WP13 reports;
- Audit 02, 03, 04, 12, 14, 15, 17, 19, 21, and 22 reports.

Resolve moved documents by filename. Treat the current repository and completion reports as implementation evidence.

## Strict scope

### Permitted

- Delete only the five dormant helper/dispatcher definitions.
- Remove imports/constants used exclusively by those deleted functions.
- Add focused static/dynamic negative architecture tests.
- Narrowly update internal comments/docs that falsely claim the dormant path still exists, if any.
- Add the WP14 report.

### Forbidden

- Do not edit `yogas.yaml` or any rule/table/fixture/snapshot.
- Do not register or implement `HOUSE_LORDS_COMBINATION`.
- Do not remove the `dhana_naive` rule or its typed WP12 issue/WP13 invalid record.
- Do not change canonical Aspect, functional-role, occupant, house-lords, condition, cache, preparation, Yoga projection, trace, attachment, or error semantics.
- Do not remove legacy loader/public surfaces owned by WP16.
- Do not migrate Career/F3 runtime; WP15 owns Career.
- Do not redesign universal RuleMatch, public schemas/output, dependencies, CI, or future DSL/compiler.

If deletion requires any forbidden change, stop and request direction.

## Pre-deletion caller proof

Perform repository-wide static searches for every symbol and for likely dynamic access:

- direct calls and imports;
- `getattr`, `globals`, string-based dispatch, monkeypatch targets, re-exports, `__all__`, docs/examples, and tests;
- tuple unpacking of Yoga condition/helper results;
- local dispatch dictionaries or name strings;
- stale API consumers.

Classify every occurrence before editing. Expected result: definitions and self-family calls only, plus audit/report text. Production/test runtime references outside the family must be zero.

Do not count historical reports/prompts as active callers and do not rewrite them.

## Deletion contract

Delete the family atomically:

1. leaf helper definitions;
2. recursive dispatcher;
3. imports/constants exclusively used by them;
4. dead comments describing their runtime behavior.

Preserve all WP13 typed models, preparation, strict loading, evaluation, compatibility projection, public wrapper, and exports byte-for-byte except unavoidable import cleanup.

Do not leave aliases, deprecated wrappers, raising stubs, feature flags, dead dispatch entries, or fallback code for the removed functions. The architecture gate should fail if any symbol is reintroduced.

## `HOUSE_LORDS_COMBINATION` semantic boundary

Removing `_eval_house_lords_combination` removes only an unreachable private implementation. It does not decide the meaning or lifecycle of the source rule.

After deletion, prove exactly:

- production registry lookup for `HOUSE_LORDS_COMBINATION` remains absent;
- WP12 strict validation still returns one `unknown_predicate` issue for `dhana_naive` at index 1 and `condition.root.children.0`;
- WP13 retains disposition `invalid` and the complete typed error child/result;
- the dormant implementation is never used as validation/evaluation fallback because it no longer exists;
- public compatibility still emits the same Dhana row and deterministic trace reference for the locked fixture;
- any future activation still requires a new registered/versioned predicate plus SME approval.

Do not describe code deletion as removal of the Yoga rule or approval of its nonexistence.

## Negative architecture enforcement

Add focused tests that fail if:

- any of the five symbol definitions reappear;
- Yoga production code contains tuple-return factual helpers or a local recursive predicate/operator dispatcher;
- active Yoga imports/calls legacy `engine.evaluate_condition`, legacy `evaluate_predicate`, `clear_cache`, generic `RULE_REGISTRY`, `load_yoga_rules`, UUID4, or local fallback names;
- active Yoga directly computes predicate facts or calls canonical handler functions rather than WP10/WP11 through the evaluator;
- `HOUSE_LORDS_COMBINATION` becomes registered or its typed issue disappears;
- dormant helper names appear in Yoga `__all__`/re-exports.

Use AST/symbol/caller checks, not fragile broad text assertions that fail on the WP14 report or historical audit files.

## Dynamic behavior proof

Run the migrated active Yoga path with sentinels/monkeypatches where useful and prove:

- only WP12/WP07/WP09/WP10/WP11 routes execute;
- no local tuple/raw-Boolean factual result is accepted;
- exact typed batch logical bytes/hash remain the WP13 value for the locked fixture;
- exact complete compatibility JSON, row order, nested key order, UUIDv5 trace references, and attachment/copy isolation remain unchanged;
- repeated/CWD/import-order/cache-warmth behavior remains deterministic;
- Dhana invalid-tree/later-OR-child behavior remains exactly WP13's policy.

If import cleanup changes any behavior/hash other than source-code inventory, treat it as a regression.

## Tests first

Before deleting production code, add/update tests that initially fail because the forbidden symbols still exist, while separately proving the active path already ignores them.

Cover at least:

### Caller inventory

- exact five-symbol definition/reference inventory;
- zero external production/test callers;
- no re-export/dynamic lookup/dispatch/tuple consumer;
- historical docs/reports excluded from active count.

### Post-removal architecture

- symbols absent from module and source AST;
- exclusive imports removed;
- no local Yoga factual/recursive fallback pattern;
- canonical route-only static and dynamic proof;
- no reintroduction via alias/stub/string dispatch.

### House-lords disposition

- registry absence;
- exact WP12 issue projection/hash unchanged;
- exact WP13 invalid record/status/error tree unchanged;
- compatibility Dhana row/trace unchanged;
- synthetic later matched OR child remains decisive without house-lords execution.

### Compatibility/determinism

- exact typed Yoga logical/full projections as applicable;
- exact three-row compatibility JSON bytes/hash;
- key/value/nested order and attachment isolation;
- normal/reverse/A/B/C and loader-order behavior;
- fresh-process/CWD/Python-lane equality;
- Career/public snapshot/fixed artifacts unchanged.

Do not weaken/delete characterization assertions and never update the approved snapshot.

## Validation gates

Run in both locked Python 3.14 and 3.11 lanes with bytecode/cache isolation and unique ignored temporary paths:

1. WP14 caller/architecture/removal focused tests.
2. WP13 typed Yoga focused tests.
3. WP02–WP12 focused modules.
4. All `tests/rules` and Yoga tests.
5. WP01 predicate/Yoga/Career characterization.
6. Targeted loader/evaluator/cache/condition/predicate/Yoga/Career/runtime/writer/linter/determinism/snapshot regressions.
7. Exact full collection comparison and node-ID SHA-256.
8. Complete suite twice from fresh processes per lane.
9. Yoga normal/reverse/A/B/C permutations.
10. Both loader-trigger orders.
11. Rule lint proving all five supported files, including `yogas.yaml`, are inspected exactly once.
12. Strict approved-snapshot comparison twice per lane using temporary output and no update mode.
13. Fresh-process/cross-version exact WP12 issue, WP13 typed Yoga, and complete compatibility bytes/hashes.
14. Final repository-wide active caller/definition scan.
15. `git diff --check` and scoped artifact/status checks.

Record exact commands, counts, hashes, symbol inventories before/after, imports removed, and compatibility evidence. Any behavior/public/snapshot change is a blocker.

## Required completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP14/WP14.md`

The report must include:

1. `VERDICT: COMPLETE` or `VERDICT: BLOCKED`;
2. `WP15_READY: YES` or `WP15_READY: NO`;
3. actual model/reasoning used;
4. prerequisite/baseline evidence;
5. exact pre-deletion caller/reference inventory;
6. exact files/symbols/imports removed or changed;
7. post-deletion negative architecture evidence;
8. canonical Yoga route proof;
9. exact `HOUSE_LORDS_COMBINATION` registry/WP12/WP13/public disposition;
10. before/after typed and compatibility hashes;
11. test-to-requirement traceability;
12. exact dual-lane commands/counts and collection hash;
13. Yoga permutations/loader/lint/Career/snapshot/artifact evidence;
14. final zero-caller/zero-definition scan;
15. deferred WP15/WP16 work and any owner/SME decision required;
16. explicit proof WP15 was not started.

## Definition of done

WP14 is complete only when:

- WP13 remains complete and reproducible;
- all five dormant private tuple/dispatcher symbols and exclusive imports are removed with zero active callers;
- no alias/stub/fallback/local predicate dispatcher remains;
- active Yoga uses only the canonical typed route;
- `HOUSE_LORDS_COMBINATION` remains unregistered and typed-invalid without changing its source rule or public compatibility;
- WP12 issue, WP13 typed logical/full identity, complete compatibility dictionaries/traces, attachment, Yoga firing/order, and snapshots remain unchanged;
- no Career/loader-public/rule/table/schema/dependency/CI/snapshot migration occurred;
- every dual-lane, determinism, compatibility, lint, snapshot, artifact, and negative architecture gate passes;
- the report records `VERDICT: COMPLETE` and `WP15_READY: YES`.

At the end, return a concise summary with verdict, model/reasoning used, removed symbols/imports, canonical-route and house-lords disposition proof, dual-lane counts, before/after hashes, Yoga/Career/snapshot status, files changed, deferred issues, and WP15 readiness. **Do not proceed to WP15.**