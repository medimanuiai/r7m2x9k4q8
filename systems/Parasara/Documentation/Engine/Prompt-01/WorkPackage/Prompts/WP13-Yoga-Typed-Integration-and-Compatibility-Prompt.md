Implement **WP13 — migrate active Yoga evaluation to the WP07–WP12 canonical boundary with typed internal results and a deterministic compatibility adapter** for Prompt-01.

Do not merely review this specification. Implement the permitted changes, run all dual-lane validation gates, and create the WP13 completion report. **Do not proceed to WP14.**

## Objective

Replace Yoga's active lossy execution internals so that:

- rule definitions are loaded/validated through WP12 rather than mutable global registry accidents;
- compatible predicate facts are prepared once into WP07 `PreparedAstroState` before evaluation;
- each rule uses one explicit WP09 `PredicateEvaluator` and WP10 `ConditionEvaluator`;
- every rule retains its complete `PredicateResult` or recursive `ConditionResult`, status, evidence, errors, trace, skipped children, identity, and version internally;
- the known `HOUSE_LORDS_COMBINATION` defect remains a typed definition error and is never activated or converted to factual false internally;
- all current source rows remain represented in source order;
- the existing public `evaluate_yoga_rules` surface continues returning the current list-of-dictionaries compatibility shape and continues the currently required state attachment;
- public trace references become deterministic and nonrandom;
- no global predicate-cache clear, stale shared rule-registry reference, CWD-dependent rule selection, or Yoga-local tuple fallback remains active;
- valid current Yoga firing/order and approved public/snapshot behavior remain unchanged.

WP13 owns active Yoga integration and the one-way compatibility adapter. WP14 owns removal of the five dormant tuple helpers. WP15 owns Career migration. Do not pull those packages forward.

## Hard prerequisite gate

Before editing:

1. Locate final WP00-R and WP01–WP12 reports by exact filename.
2. Confirm WP12 records `VERDICT: COMPLETE` and `WP13_READY: YES`.
3. Confirm strict validation of `yogas.yaml` produces exactly one issue: `unknown_predicate` for rule `dhana_naive`, index 1, node `condition.root.children.0`, requested ID `HOUSE_LORDS_COMBINATION`.
4. Reproduce the Python 3.14 and 3.11 baseline: identical collection IDs, two clean full suites, all Yoga permutations, both loader orders, five-file lint, and strict approved snapshots.
5. Capture exact before-change Yoga output for every current characterization fixture, including row count/order, key insertion order, values, nested evidence, state attachment, and trace-field format. Treat random trace values as telemetry while recording their type/shape.
6. Record and preserve the inherited dirty worktree.

If any gate fails, stop without production edits and report `VERDICT: BLOCKED` and `WP14_READY: NO`.

## Required references

Read the current implementation plus:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP02–WP12 reports;
- Audit 03, 04, 09, 10, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, and 24 reports.

Resolve moved documents by filename. Treat completion reports as implementation evidence and audits as defect/test inventories.

## Strict scope

### Permitted

- Add minimal immutable internal Yoga evaluation models and WP03 projections.
- Add a canonical Yoga evaluator over validated/current rules and prepared state.
- Add a bounded mutable-AstroState compatibility preparation adapter outside predicates.
- Modify active Yoga loader/evaluator/public re-export to use the typed pipeline and one-way compatibility projection.
- Preserve temporary state attachment if required by the locked DR28 compatibility decision.
- Add focused Yoga integration, projection, determinism, mutation, and compatibility tests.
- Add the WP13 report.

### Forbidden

- Do not implement/register/activate/remove/reinterpret `HOUSE_LORDS_COMBINATION` or call its dormant helper.
- Do not remove the five dormant Yoga tuple helpers in WP13; WP14 owns removal after migration proof.
- Do not change Yoga rule files, rule IDs, versions, weights, category, provenance, SME flags, tests metadata, row order, or astrology semantics.
- Do not change Aspect, functional-role, house, exaltation, or condition semantics.
- Do not redesign a universal `RuleMatch`, domain/inference model, public schema, output assembler, frontend contract, or future DSL/compiler.
- Do not migrate Career/F3 runtime, modify dependencies/CI, or update snapshots/goldens.
- Do not silently discard invalid rules or reduce typed results to booleans internally.

Stop and request approval if protected rule firing/public values cannot be preserved without a semantic change.

## Required architecture

Implement two explicit layers:

```text
explicit Yoga source / WP12 validation outcomes
        + PreparedAstroState + PredicateEvaluationContext
        + one PredicateEvaluator instance
    -> typed canonical Yoga evaluation records
    -> one-way compatibility projection
    -> existing list[dict] return and temporary state attachment
```

The typed layer must never depend on the compatibility dictionaries or attached Yoga output. The prepared-state digest/cache identity must exclude Yoga results and compatibility telemetry, as WP07 already requires.

## Minimal internal Yoga models

Use WP02/WP03 conventions and existing result types. Add the smallest exact immutable contracts, with equivalent repository naming:

### `YogaDefinitionDisposition`

Exactly:

- `valid`;
- `invalid`.

### `YogaEvaluationRecord`

Required logical fields:

- canonical `yoga_id`;
- rule `name`;
- rule `version` as the existing validated source value;
- stable source identity/rule index;
- definition disposition;
- ordered WP12 definition issues for that rule;
- complete evaluated `PredicateResult` or `ConditionResult` when execution occurred;
- explicit Yoga-level `matched` and typed status consistent with the condition result;
- stable deterministic `trace_reference`;
- immutable safe rule metadata needed by the compatibility projection only if already exposed/used;
- optional evaluation duration as telemetry only.

Invariants:

- a valid disposition has no definition issues and exactly one canonical condition result;
- an invalid disposition has one or more definition issues; it may have a safe runtime condition result only under the explicit invalid-tree compatibility policy below;
- matched is true iff typed status is matched;
- the condition result's logical identity is retained intact;
- no raw rule mapping, mutable AstroState, provider object, callable, cache object, path, or compatibility dictionary is retained;
- deeply immutable and telemetry-neutral logical equality.

### `YogaEvaluationBatch`

Required fields:

- schema/evaluator version;
- prepared-state digest used;
- ordered tuple of every source Yoga row's `YogaEvaluationRecord`;
- ordered batch/source validation issues not owned by a single rule;
- optional total duration telemetry.

Preserve source row order exactly. Do not omit invalid or unmatched rows.

If existing canonical conventions require slightly different field names, preserve these semantics and document the exact inventory.

## WP03 serialization and identity

Add model-owned logical/full projections, strict bytes, and lowercase SHA-256.

Logical Yoga identity includes:

- Yoga model/evaluator version;
- prepared-state digest;
- rule ID/name/version and stable logical source index;
- definition disposition/issues;
- complete condition logical projection;
- Yoga matched/status;
- deterministic trace reference;
- compatibility-relevant rule metadata only when approved.

Exclude:

- condition/predicate/Yoga durations;
- leaf cache-hit telemetry;
- mutable AstroState identity/content outside prepared digest;
- compatibility dictionary key order as an internal identity mechanism;
- attached Yoga output, UUID4/randomness, CWD/absolute path/environment;
- raw rules/source text/parser objects.

Cold/warm leaf differences must not change Yoga logical equality/bytes/hash. Full projection may differ only in approved telemetry.

## Yoga rule loading and source order

The canonical typed path must use WP12's explicit strict file/record APIs and must not depend on `RULE_REGISTRY`, stale imported dictionary references, last-wins behavior, or implicit CWD paths.

- Resolve the default production Yoga source from a stable repository/module-relative path, not CWD.
- Preserve file record order.
- Aggregate WP12 issues exactly.
- Represent every source row, including invalid `dhana_naive`.
- Do not mutate/register rules globally as part of canonical evaluation.
- Keep legacy loader functions only as named compatibility surfaces if current external/tests require them; document their WP14/WP16 disposition.

No broad directory scan or generic F3 duplicate policy belongs here.

## Preparation boundary

Predicates and the condition evaluator must receive a fully prepared immutable WP07 state. Yoga must no longer recompute/mutate facts during rule iteration.

Create an explicit preparation API that either:

1. accepts an already prepared `PreparedAstroState`; or
2. for the legacy mutable-AstroState public adapter, builds required facts once before canonical evaluation.

For the legacy adapter:

- never let predicate handlers access mutable AstroState;
- avoid mutating the caller during factual preparation; use a defensive deep copy or isolated compatibility preparation object when current producers require mutation;
- prepare the whole-sign Aspect graph once using the currently locked producer/behavior only when needed to reproduce the public API contract;
- obtain functional-role facts once outside evaluation and pass them through WP07's explicit typed capability-supply mechanism;
- do not recompute roles per predicate/rule;
- do not run varga preparation unless a current registered Yoga predicate capability actually requires it; prove removing redundant varga work does not change Yoga results;
- do not clear any global cache; create one explicit WP09 evaluator per Yoga batch;
- do not read CWD for rule selection; any unavoidable legacy producer configuration access must be explicit, stable, and documented;
- capture preparation failures as typed safe batch/rule issues, never raw exceptions or factual unmatched.

Do not change the underlying astrology producer/table in WP13. If exact compatible preparation cannot be achieved without changing doctrine/configuration, stop for approval.

## Valid-rule evaluation

For a WP12-valid Yoga rule:

- evaluate its normalized immutable condition through one WP10 `ConditionEvaluator` sharing the batch's WP09 evaluator;
- retain the complete result tree;
- derive Yoga matched/status directly and truthfully;
- preserve definition/source identity and trace lineage;
- never flatten evidence/errors/traces internally;
- preserve WP10 left-to-right order, short-circuiting, skipped children, and status precedence;
- do not call legacy `engine.evaluate_condition` or Yoga-local helpers.

## Invalid `HOUSE_LORDS_COMBINATION` compatibility policy

The `dhana_naive` rule contains one invalid unknown leaf under an OR. Do not activate or treat it as factual false.

Use this locked policy:

1. Preserve the WP12 definition issue in the Yoga record.
2. For compatibility evaluation only, pass the original safe current-format condition through WP10's canonical runtime boundary, which already represents the unknown leaf as a typed error rather than unmatched.
3. Continue evaluating other OR children under WP10 semantics. A later matched canonical child may decisively produce a matched OR; otherwise the condition/Yoga status remains non-factual error according to WP10 precedence.
4. Retain the complete typed error child/result tree internally.
5. The public compatibility projection may emit `matched=False` for a nonmatched/nonfactual Yoga row because the legacy dictionary has only a Boolean field, but it must not rewrite the internal status or evidence into factual unmatched.
6. Never call `_eval_house_lords_combination` or any legacy tuple helper.

If WP10 cannot safely evaluate the raw invalid tree exactly this way, add a narrow typed definition-error leaf adapter at the condition boundary; do not create predicate semantics or a legacy fallback.

## Deterministic trace reference

Replace UUID4 with a deterministic, nonrandom public-compatible string derived from canonical logical identity.

Preferred representation: UUIDv5 string using one fixed documented namespace and a name composed only from Yoga evaluator version, canonical Yoga ID/version, logical source index, prepared-state digest, and condition logical SHA-256.

Requirements:

- same logical evaluation produces the same reference across runs/processes/Python versions;
- a relevant fact/rule/condition-result change changes it;
- cache warmth/duration/object identity/CWD does not;
- retain the current compatibility field name and string/UUID-shaped value if consumers expect it;
- do not include secrets, absolute paths, random seed, current time, or raw rule text.

## One-way compatibility projection

Inventory the exact current dictionary fields and insertion order from the source and WP01 characterization before editing. Lock them in tests.

The compatibility adapter must:

- emit every current source row, including unmatched/invalid rows, in current source order;
- preserve exact current key names, key insertion order, value types, and compatibility meanings except the approved random-to-deterministic trace change;
- preserve valid current matched Booleans for the locked fixtures;
- preserve current names/IDs and existing planets/houses/aspects/evidence fields;
- derive values from the typed record/tree without mutating or discarding it;
- use deterministic first-seen traversal for any de-duplication instead of set-to-list ordering;
- produce fresh detached mutable dictionaries/lists only at this outer compatibility boundary;
- never expose internal cache telemetry, raw errors/exceptions, source paths, unsupported objects, or new public keys;
- never feed projected dictionaries back into canonical evaluation or digest identity.

Where the richer canonical evidence cannot exactly equal the old lossy evidence, implement an explicit compatibility-evidence projection that reproduces the existing contractual shape for the characterized fixtures while the typed record retains complete evidence internally. Document every lossy compatibility mapping.

Do not populate currently empty broader public diagnostics/output fields merely because typed Yoga data now exists.

## State attachment policy

Preserve the current compatibility behavior required by DR28:

- `evaluate_yoga_rules(legacy_astro, ...)` returns the compatibility list;
- it attaches a detached copy of that same compatibility list at the existing `astro.enrichments['yogas']` location if the current API does so;
- attachment occurs only after the typed batch and projection complete;
- attachment failure is handled by the existing approved compatibility policy and never changes the typed batch;
- attached Yoga output is never included in prepared-state/cache identity;
- canonical typed evaluation over `PreparedAstroState` performs no mutation/attachment.

Prove attached and returned values cannot mutate the internal typed batch, and mutation of one compatibility copy cannot corrupt the other if the locked behavior requires independent copies.

## Typed API and legacy public API

Expose clear separate APIs, following repository naming conventions:

- canonical typed Yoga evaluation accepting prepared state, typed context, validated/source rule outcomes, and optional explicit evaluator;
- compatibility projection from `YogaEvaluationBatch` to current dictionaries;
- existing public `evaluate_yoga_rules` wrapper for mutable AstroState callers.

Do not overload one function with ambiguous raw/prepared return types without explicit names and tests.

## Errors, evidence, and trace preservation

The typed batch/record must retain:

- WP12 definition issues;
- full WP02 leaf errors/evidence/traces;
- complete WP10 nested child results, skips, status precedence, and trace lineage;
- preparation issues with stable safe codes;
- stable rule-to-condition linkage.

Do not flatten errors, duplicate arbitrary child evidence, expose exception text, or synthesize factual evidence for unavailable definitions/capabilities. Compatibility loss is allowed only in the documented one-way adapter.

## Tests first

Add focused tests before production changes. Cover at least:

### Models/serialization

- exact fields/enums/invariants;
- valid/invalid definition records;
- recursive result retention and deep immutability;
- logical equality excluding all recursive telemetry;
- strict logical/full projections and round trips where applicable;
- exact bytes/hashes and source mutation isolation.

### Loading/validation/order

- stable explicit production source path independent of CWD;
- exact three source rows and order;
- exact WP12 `HOUSE_LORDS_COMBINATION` issue retained;
- no global rule registry mutation/rebinding/stale reference;
- duplicate/malformed synthetic sources become typed issues, not silent skips;
- no generic F3 scan.

### Preparation

- already-prepared input performs no producer call/mutation;
- legacy adapter prepares Aspect graph at most once and roles at most once per batch;
- no per-rule/per-leaf recomputation;
- no redundant varga call;
- caller mutable state factual content unchanged during preparation except final approved Yoga attachment;
- no global cache clear;
- preparation failure becomes safe typed issue;
- equivalent inputs produce identical prepared digest.

### Evaluation

- all valid rules use WP10/WP11 canonical leaves only;
- one shared WP09 evaluator per batch;
- complete child/evidence/error/trace/status preservation;
- short-circuit/skipped behavior preserved;
- invalid Dhana unknown leaf is typed error, dormant helper never called, later OR child behavior follows WP10;
- no legacy `evaluate_condition` or tuple helper fallback;
- matched/unmatched/missing/error cases remain distinct internally.

### Compatibility projection

- exact current row count/order;
- exact key names/insertion order/value types for every row;
- exact characterized valid matched values and lossy evidence/derived fields;
- deterministic first-seen planet/house/aspect ordering;
- deterministic UUID-shaped trace references;
- all rows emitted, including invalid/nonfactual;
- no new public keys or broader diagnostics;
- fresh detached dictionaries and no typed-batch mutation.

### Attachment/public API

- public import path/signature remains compatible;
- returned and attached compatibility values follow exact locked copy/identity behavior;
- canonical typed API does not mutate;
- attachment does not alter prepared digest/cache keys;
- repeated calls are logically deterministic and do not accumulate/corrupt state.

### Determinism/compatibility

- same fixture repeated, fresh process, alternate CWD, loader order, and Python 3.14/3.11 produce identical typed logical bytes and compatibility output after excluding no fields—the trace is now deterministic;
- cold/warm leaf cache changes only full telemetry, not Yoga logical/compatibility output;
- existing Yoga firing/order, Career, rules, public snapshot, and fixed artifacts remain unchanged;
- no rule/YAML/schema/weight/table edit.

Do not weaken/delete existing tests and never update the approved snapshot.

## Validation gates

Run in both locked Python 3.14 and 3.11 lanes with bytecode/cache isolation and unique ignored temporary paths:

1. WP13 Yoga model/preparation/evaluation/projection/attachment focused tests.
2. WP02–WP12 focused modules.
3. All `tests/rules` and Yoga tests.
4. WP01 predicate/Yoga/Career characterization, updating only the explicitly approved random-trace assertion to deterministic identity if needed while preserving all logical/public fields.
5. Targeted loader/evaluator/cache/condition/predicate/Yoga/Career/runtime/writer/linter/determinism/snapshot regressions.
6. Exact full collection comparison and node-ID SHA-256.
7. Complete suite twice from fresh processes per lane.
8. Yoga normal/reverse/A/B/C permutations under the migrated active path.
9. Both loader-trigger orders.
10. Rule lint proving all five supported files, including `yogas.yaml`, are inspected exactly once.
11. Strict approved-snapshot comparison twice per lane with temporary output and no update mode.
12. Fresh-process/cross-version exact typed-batch logical/full bytes/hashes and complete compatibility JSON bytes/hash, including deterministic trace references.
13. `git diff --check` and scoped artifact/status checks.

Record exact commands, versions, counts, node-ID hash, rule outputs, typed/compatibility hashes, producer call counts, mutation/attachment behavior, and protected compatibility evidence. Any unexplained Yoga firing, rule order, public field, Career, or snapshot change is a blocker.

## Required completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP13/WP13.md`

The report must include:

1. `VERDICT: COMPLETE` or `VERDICT: BLOCKED`;
2. `WP14_READY: YES` or `WP14_READY: NO`;
3. actual model/reasoning used;
4. prerequisite/baseline and exact pre-migration Yoga projection;
5. exact files changed and typed/public APIs;
6. internal Yoga model fields/invariants;
7. logical/full serialization inclusion/exclusion and hashes;
8. loading/source-order/global-registry disposition;
9. preparation lifecycle, producer call counts, purity, mutation, and failure policy;
10. valid-rule WP09/WP10/WP11 evaluation flow;
11. exact invalid `HOUSE_LORDS_COMBINATION` typed compatibility behavior;
12. deterministic trace-reference algorithm/namespace/inputs;
13. exact compatibility dictionary key/order/value and lossy mapping table;
14. state attachment/copy/isolation policy;
15. complete errors/evidence/trace preservation evidence;
16. test-to-requirement traceability;
17. exact dual-lane commands/counts and collection hash;
18. fresh-process/cross-version typed and compatibility bytes/hashes;
19. Yoga permutations/loader/lint/Career/snapshot/artifact evidence;
20. static caller proof that dormant helpers remain unused and no fallback exists;
21. deferred WP14/WP15/WP16 work and any owner/SME decision required;
22. explicit proof WP14 was not started.

## Definition of done

WP13 is complete only when:

- WP12 remains complete and reproducible;
- active Yoga uses validated definitions, prepared immutable state, one explicit WP09 evaluator, and WP10/WP11 canonical execution;
- every source row has a typed immutable record retaining complete condition results/issues/status/evidence/errors/traces;
- `HOUSE_LORDS_COMBINATION` remains an unactivated typed definition error with no factual false conversion internally;
- no global cache clear, mutable-rule registry dependency, CWD rule selection, per-rule producer recomputation, or active tuple-helper fallback remains;
- the compatibility adapter preserves current rows/order/keys/types/valid firing and approved state attachment, with only the approved deterministic trace change;
- typed/full and public compatibility outputs are deterministic across runs/processes/CWD/Python lanes;
- no rule/YAML/astrology/Career/public-schema/CI/dependency/snapshot change occurred;
- all dual-lane, regression, Yoga permutation, loader, lint, snapshot, and artifact gates pass;
- the report records `VERDICT: COMPLETE` and a justified WP14 readiness decision.

At the end, return a concise summary with verdict, model/reasoning used, typed/public APIs, preparation and invalid-rule policies, trace/compatibility/attachment contracts, dual-lane counts, cross-version hashes, Yoga firing/snapshot status, files changed, deferred issues, and WP14 readiness. **Do not proceed to WP14.**