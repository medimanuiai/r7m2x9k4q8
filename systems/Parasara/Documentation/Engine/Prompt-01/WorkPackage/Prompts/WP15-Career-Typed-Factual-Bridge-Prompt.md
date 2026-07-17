Implement **WP15 — migrate the Career factual compatibility path to immutable typed results while preserving every current Career calculation and public field** for Prompt-01.

Do not merely review this specification. Implement the narrow typed bridge, validate both Python lanes, and create the WP15 completion report. **Do not proceed to WP16.**

## Objective

Remove Career's active dependency on:

- `runtime.evaluate_rule_with_score`;
- fallback `runtime.evaluate_rule`;
- raw-Boolean/dictionary factual dispatch;
- mutable/global rule-registry warmth and implicit M1 loading;
- broad exception-to-false conversion.

Replace it with a deterministic, immutable Career-specific factual bridge that:

- prepares the exact Career-relevant facts once from the normalized AstroState without retaining mutable aliases;
- uses WP09/WP11 canonical predicates wherever an exact registered predicate contract exists;
- represents remaining Career-specific facts with a minimal typed temporary result contract using WP02 statuses/errors/traces and WP03 serialization;
- retains every candidate outcome, including unmatched and non-factual statuses, internally;
- preserves the exact existing candidate set/order and confidence denominator;
- preserves every contribution, base score, final score, confidence, component, indicator, evidence row, summary, scoring field, trace ID, key order, type, and public JSON value;
- performs no raw Surya access, producer recomputation, mutable global loading, predicate/result mutation, or new astrology inference.

This is a compatibility migration, not the future shared `InferenceEngine`, universal `RuleMatch`, typed `DomainPrediction`, or `OutputAssembler` redesign.

## Hard prerequisite gate

Before editing:

1. Locate final WP00-R and WP01–WP14 reports by exact filename.
2. Confirm WP14 records `VERDICT: COMPLETE` and `WP15_READY: YES`.
3. Reproduce WP11 canonical predicate, WP13/WP14 Yoga, and WP09 cache contracts.
4. Capture exact current Career output for every existing Career/vertical-slice/additional-snapshot fixture, including candidate construction order, rule merge/source, rule outcomes, base inputs, contributions, denominator, confidence terms, components, indicators, evidence, summary, scoring, trace, dictionary/list insertion order, numeric types, and serialized JSON.
5. Reproduce the Python 3.14/3.11 baseline: identical collection IDs, two full-suite passes, Yoga permutations, loader orders, five-file lint, and strict snapshots.
6. Record and preserve the inherited dirty worktree.

If any prerequisite fails, stop without production edits and report `VERDICT: BLOCKED` and `WP16_READY: NO`.

## Required references

Read the current implementation plus:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP01 characterization and WP07–WP14 reports;
- Audit 02, 03, 04, 07, 08, 09, 10, 11, 12, 14, 16, 17, 18, 19, 20, 21, and 22 reports.

Resolve moved documents by filename. Treat current code and completion reports as implementation evidence.

## Strict scope

### Permitted

- Add minimal immutable Career fact/candidate/evaluation-batch models and WP03 projections.
- Add an explicit Career fact-preparation adapter and rule/candidate catalog boundary.
- Modify `interpret_career` to consume the typed bridge and then produce the existing public dictionary.
- Use WP09/WP11 canonical predicates for exact existing planet/house facts.
- Retain domain-specific strength/lord/dignity/rajayoga facts in a narrow typed Career bridge when no exact registered predicate exists.
- Add focused status, evidence, cache, determinism, architecture, and deep-compatibility tests.
- Add the WP15 report.

### Forbidden

- Do not change candidate rule IDs/order/count, rule types, parameters, hard-coded/base scores, weights, thresholds, clipping, rounding, confidence formula/denominator, component logic, indicator/evidence inclusion, summary text, or public trace ID.
- Do not register new predicates for Career-only rule types.
- Do not reinterpret `PLANET_EXALTED`, functional roles, Aspects, lords, dignity, house summaries, strength thresholds, or rajayoga semantics.
- Do not change M1/Yoga rule files, tables, fixtures, schemas, dependencies, CI, public output schema, Wealth placeholder, frontend/API, or snapshots.
- Do not delete legacy runtime/loader APIs; WP16 owns final caller migration/removal.
- Do not expose new typed diagnostics in the public Career dictionary.
- Do not implement shared inference/domain/output architecture.

If exact output requires a semantic/formula/public change, stop and request owner approval.

## Exact pre-migration inventory

Before implementation, document and lock with tests:

- all candidate dictionaries created by `interpret_career`, in exact order;
- explicit versus merged rule fields and their winning sources;
- every `evaluate_rule_with_score` branch reached by Career fixtures;
- all direct Career factual reads;
- all contribution values and selection rules;
- base-score planet selection/order/strength values;
- 10th house summary, lord, occupants, and strength component inputs;
- confidence numerator/denominator, evidence-strength values, and completeness fields;
- exact output field/list/mapping order and JSON bytes for each fixed fixture.

Do not rely only on indicator IDs. Create deep before/after fixtures/assertions from current production output without modifying approved goldens.

## Required architecture

Use three explicit layers:

```text
normalized mutable AstroState
    -> immutable CareerPreparedFacts snapshot
    -> immutable typed Career candidate/fact evaluation batch
    -> unchanged Career scoring/confidence logic
    -> one-way existing public Career dictionary projection
```

Typed internal models must not retain the public dictionary, mutable AstroState, global rule registry, loader object, raw YAML mapping, provider object, or callable.

## Minimal typed Career contracts

Use WP02 `PredicateStatus`, `PredicateError`, and `PredicateTraceStep`, WP03 freezing/serialization, and canonical `PredicateResult`/`ConditionResult` where used. Add only the minimum temporary Career models.

### `CareerFactKind`

An exact enum covering only the currently executed Career factual groups discovered from the pre-migration inventory. Do not add future facts. Expected groups may include:

- canonical planet/house occupancy;
- strong-in-house;
- house-lord lookup/status;
- current rajayoga compatibility fact;
- base kendra strength selection;
- 10th-house occupant-strength component.

Use actual current branches and names; do not invent unused members.

### `CareerFactResult`

Required fields:

- stable fact ID/version;
- fact kind;
- `matched` strict Boolean;
- WP02 `PredicateStatus`;
- immutable normalized inputs;
- complete safe actual/expected evidence;
- ordered typed errors;
- ordered typed trace steps;
- optional canonical `PredicateResult` or `ConditionResult` backing result when an exact central evaluation was used;
- optional duration telemetry.

Invariants mirror WP02: matched iff status matched; factual matched/unmatched have no errors; non-factual outcomes never masquerade as unmatched; recursive telemetry excluded from logical equality.

### `CareerCandidateDefinition`

Immutable exact representation of each current candidate:

- candidate/rule ID;
- current rule type/version/source identity;
- immutable normalized legacy-compatible parameters/context;
- exact current base/adjustment score metadata;
- declared source order/index.

No raw rule mapping or global loader reference.

### `CareerCandidateEvaluation`

Required fields:

- candidate definition;
- complete typed fact result;
- matched/status;
- exact computed contribution using the unchanged current rule score policy;
- immutable compatibility evidence/context used by the existing public adapter;
- stable internal trace lineage;
- optional telemetry.

### `CareerEvaluationBatch`

Required fields:

- schema/evaluator version;
- prepared-facts digest;
- exact source-ordered tuple of **all** candidates, not only matches;
- immutable typed base/component fact records;
- optional telemetry.

Do not create a general `RuleMatch` or `DomainPrediction`.

If repository conventions require different names, preserve these semantics and report exact inventories.

## WP03 identity and serialization

Provide logical/full data, strict compact UTF-8 bytes, lowercase SHA-256, and strict round trip where current model conventions require it.

Logical identity includes:

- Career schema/evaluator/fact versions;
- prepared Career fact digest;
- exact candidate definitions/order;
- complete typed fact status/inputs/evidence/errors/traces/backing logical result;
- exact contributions;
- base/component fact observations.

Exclude:

- all durations/cache-hit telemetry;
- object/process identity, CWD/environment, mutable registry state;
- raw AstroState/YAML/provider/rule dictionaries;
- final public Career dictionary and narrative/scoring output as input to factual identity;
- random/current time.

Cold/warm central predicate evaluation must produce identical Career logical bytes/hash and public output.

## Career fact preparation

Create a read-only snapshot of every fact currently read by Career/runtime:

- canonical planet identities, houses, signs where actually used;
- exact strength values and missing states;
- exact house-summary representation used by current Career logic, including house 10 lord and occupants;
- dignity/status fields actually used;
- exact Aspect/rajayoga inputs actually used;
- other current branch inputs proven by inventory.

Requirements:

- defensive copy/freeze; no mutable alias retained;
- distinguish absent entity/fact/capability from present false/zero;
- preserve zero and false values exactly;
- no normalization/enrichment producer, file/network/CWD access, clock, random, cache, or mutation;
- no raw Surya/provider import;
- deterministic catalog/source ordering matching current Career outcomes;
- digest every behavior-changing fact/source/version needed by the current bridge;
- exclude unrelated domains, Yoga output, public output, diagnostics, telemetry.

Do not “correct” `house_summaries` versus `astro.houses`; preserve the exact representation each current Career branch uses and document it.

## Explicit Career candidate catalog

Remove active Career dependence on generic `RULE_REGISTRY` warmth and best-effort/lazy loading.

Build candidates deterministically from the same current Python definitions and exact approved M1 metadata needed by Career:

- use an explicit stable module/repository-relative M1 source if current score metadata must be read;
- select only exact current rule IDs/compatible records using a documented deterministic policy;
- reproduce the current winning fields/scores exactly;
- reject/record malformed or duplicate relevant definitions safely rather than last-wins;
- do not scan Yoga files or broad directories;
- do not select a new winner for the unrelated cross-file `rajayoga_naive` duplicate;
- do not mutate/rebind the generic rule registry.

Prefer freezing the tiny current Career candidate metadata in an explicit typed catalog if that exactly reflects current authoritative code/source and avoids runtime YAML loading. Do not duplicate astrology facts—only rule identity/score metadata.

## Canonical predicate use

Where Career asks the exact registered question “does planet P occupy house H?”, use WP09/WP11 `PLANET_IN_HOUSE` or `HOUSE_OCCUPANT` over one prepared predicate state and one explicit evaluator instance.

- Preserve separate predicate identity according to the current candidate meaning.
- Retain the full canonical PredicateResult in the Career fact record.
- Use no direct handler import/call.
- Cache warmth must not change Career logic.

Do not force non-equivalent Career facts into an existing predicate:

- strength thresholds;
- house-lord lookup;
- dignity/lord-status branches;
- rajayoga compatibility logic not exactly equal to an existing canonical Yoga/predicate contract;
- component aggregation.

Those remain explicitly versioned Career facts with typed outcomes and exact preserved legacy meaning. Do not register new predicates in WP15.

## Preservation-locked factual policies

For each legacy/current Career fact branch, transcribe its existing behavior exactly into typed form:

- `strong_in_house` threshold remains exactly `>= 0.75` where currently used;
- dignity matching remains exactly current `own_sign|exalted` behavior and current source fields;
- rajayoga/aspect compatibility keeps the exact current branch and evidence—not WP13 Yoga output unless it was already the source;
- house lord/occupant lookups preserve current `house_summaries` versus other-field behavior;
- missing facts produce typed non-factual statuses internally but contribute exactly what the legacy public/scoring adapter contributed previously;
- present zero/false remains factual and is never treated as absent by the bridge.

Document an exact before/after truth table for every executed rule type. Do not expand supported rule types.

## Status eligibility and confidence denominator

Use the locked DR29 policy:

- the candidate set and order are fixed before evaluation;
- **every candidate remains in the same confidence denominator regardless of typed status**;
- matched candidates are eligible for contribution exactly as before;
- unmatched candidates contribute zero exactly as before;
- missing capability/entity/fact, invalid parameters, error, timeout, or skipped remain distinct internally and contribute the same zero/no-public-indicator behavior the legacy path produced;
- non-factual statuses are never relabeled unmatched in typed records;
- no non-factual candidate is silently dropped from the internal batch or denominator;
- public output remains unchanged and does not gain status/error fields.

If current confidence code receives a filtered list, reproduce its exact current input list/denominator mechanics rather than “improving” them. Lock both the conceptual candidate denominator and the actual function inputs in tests.

## Scoring, confidence, components, and narrative freeze

Do not rewrite formulas. Reuse or minimally adapt existing functions.

Preserve exactly:

- base score: mean strength of current kendra-selected planets or `0.5` when none;
- contribution inclusion: matched and positive only;
- rule-specific adjusted/base score selection, including current zero-handling behavior;
- final score: `min(1.0, base + sum(contributions))`, with no new lower clamp;
- confidence formula and all inputs/rounding;
- current completeness fields;
- components, including 10th-house occupants/weight/strength reconstruction;
- indicator/evidence membership and source order;
- summary wording/thresholds;
- public `trace_id="career_001"` exactly.

Internal trace lineage may become deterministic and rich, but the public trace ID must not change in WP15.

## One-way public compatibility projection

Keep `interpret_career(astro)` returning the exact existing dictionary with fields in current order:

`summary`, `score`, `confidence`, `components`, `indicators`, `evidence`, `scoring`, `trace_id`.

The adapter must:

- preserve nested keys/order, lists/order, scalar types, floats, rounding, strings, and `None` behavior;
- include exactly the same indicators/evidence rows and legacy-shaped evidence/context;
- expose no new status/error/trace/version/provenance fields;
- return fresh detached mutable containers;
- never feed the public dictionary back into typed evaluation or identity;
- preserve runner/API/frontend and snapshot bytes.

Typed unmatched/non-factual evidence remains available only through an internal typed API in WP15; do not broaden the public schema.

## Typed and public APIs

Expose separate clear APIs following repository conventions:

- `prepare_career_facts(astro) -> CareerPreparedFacts`;
- `evaluate_career_batch(prepared_facts, ..., predicate_state/evaluator as needed) -> CareerEvaluationBatch`;
- `project_career_compatibility(batch, astro-or-required-score-context) -> dict`;
- existing `interpret_career(astro) -> dict` wrapper.

If scoring must occur in the batch rather than projection, keep factual evaluation and public projection one-way and explicitly separated. Avoid an ambiguous function returning typed or dictionary shapes based on input type.

## Error and recovery policy

- Unexpected preparation/evaluation defects become typed safe errors with fixed codes and no raw exception text/type/traceback/path.
- Do not fall back to legacy runtime.
- Non-factual candidates remain in the typed batch and denominator policy.
- The public adapter preserves current zero-contribution/no-indicator behavior without claiming the typed result was factual unmatched.
- A catastrophic batch failure must follow a documented deterministic compatibility policy that preserves public schema and cannot expose internals; test it without changing normal fixture output.

## Architecture enforcement

Add static/dynamic tests proving Career production code:

- does not import/call `evaluate_rule_with_score`, `evaluate_rule`, raw Boolean primitives, generic `RULE_REGISTRY`, lazy loader, test instrumentation, or direct canonical handlers;
- does not tuple-unpack factual results;
- does not import raw Surya/provider or Yoga output as Career facts;
- does not mutate AstroState, prepared facts, predicate results, registry, cache, globals, or public output inputs;
- uses explicit typed bridge and WP09 evaluator where appropriate;
- performs no CWD/filesystem rule discovery, producer execution, time/random identity, or broad exception-to-false fallback;
- leaves legacy runtime present only for remaining WP16 callers/tests.

## Tests first

Add focused tests before production changes. Cover at least:

### Pre-migration locks

- exact candidates/rules/order/merged score metadata;
- exact direct fact inputs and branch outputs;
- deep complete Career dictionary for every fixed fixture;
- exact JSON bytes/hash and public key/nested order;
- exact score/confidence terms and denominators.

### Models/preparation

- exact fields/enums/invariants;
- deep immutability and source mutation isolation;
- present false/zero versus absent fact;
- `house_summaries`/strength/dignity/Aspect facts preserved exactly;
- logical/full serialization/round trip/hashes;
- no producer/raw provider/I/O/CWD/time/random/mutation.

### Candidate facts/statuses

- every currently executed rule type matched/unmatched;
- missing capability/entity/fact, invalid, injected error, timeout, skipped represented distinctly;
- all candidates retained in source order and denominator;
- contributions and public indicator eligibility unchanged;
- full evidence/errors/traces retained internally;
- no raw exception leakage.

### Canonical integration/cache

- exact occupancy questions use WP09/WP11 and retain backing PredicateResult;
- no direct handler or legacy runtime call;
- cold/warm/repeated/equivalent state produce identical Career logical/public output;
- relevant fact/version change isolates identity;
- cache bounds/lifecycle remain unchanged.

### Score/public compatibility

- base score planet selection and fallback;
- every positive/zero/negative contribution path;
- clipping/no lower clamp;
- exact confidence coverage/evidence/completeness calculations;
- exact components/occupants/weights;
- exact indicator/evidence membership/order/content;
- exact summary and `career_001`;
- full snapshot/runner-facing dictionary equality.

### Architecture/regression

- forbidden imports/calls and no tuple/raw-Boolean factual consumers;
- no global registry/loader state sensitivity;
- alternate CWD/import order/process/Python version determinism;
- Yoga and all unrelated systems unchanged;
- no approved artifact modification.

Do not weaken/delete characterization tests and never update approved snapshots.

## Validation gates

Run in both locked Python 3.14 and 3.11 lanes with bytecode/cache isolation and unique ignored temporary paths:

1. WP15 Career models/facts/status/cache/compatibility/architecture focused tests.
2. All existing Career interpreter, characterization, snapshot, vertical-slice, runtime, and additional-snapshot tests.
3. WP02–WP14 focused modules.
4. All `tests/rules`, Yoga tests, and domain tests.
5. WP01 predicate/Yoga/Career characterization.
6. Targeted loader/evaluator/cache/condition/predicate/Yoga/Career/runtime/writer/linter/determinism/snapshot regressions.
7. Exact full collection comparison and node-ID SHA-256.
8. Complete suite twice from fresh processes per lane.
9. Yoga normal/reverse/A/B/C permutations and both loader orders.
10. Rule lint proving all five supported files are inspected exactly once.
11. Strict approved-snapshot comparison twice per lane using temporary output and no update mode.
12. Fresh-process/cross-version exact Career prepared-fact/batch logical/full bytes/hashes and complete public Career JSON bytes/hash for every fixed fixture, cold and warm.
13. Final static caller scan proving Career no longer calls legacy runtime/raw Boolean facts.
14. `git diff --check` and scoped artifact/status checks.

Record exact commands, versions, counts, node-ID hash, candidate/denominator inventories, score/confidence terms, bytes/hashes, and public compatibility evidence. Any unexplained output difference is a blocker.

## Required completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP15/WP15.md`

The report must include:

1. `VERDICT: COMPLETE` or `VERDICT: BLOCKED`;
2. `WP16_READY: YES` or `WP16_READY: NO`;
3. actual model/reasoning used;
4. prerequisite/baseline and exact pre-migration Career captures;
5. exact files changed and typed/public APIs;
6. model fields/invariants and serialization policy;
7. prepared Career fact inventory/digest policy;
8. exact candidate catalog/order/source/score metadata;
9. per-rule/fact before-after truth/status/evidence mapping;
10. canonical predicate versus Career-specific fact routing;
11. non-factual status/denominator/contribution policy;
12. exact scoring/confidence/component/narrative freeze evidence;
13. public dictionary and lossy typed-to-public mapping table;
14. error/recovery and internal trace policy;
15. legacy runtime/global-loader removal from Career call graph;
16. test-to-requirement traceability;
17. exact dual-lane commands/counts and collection hash;
18. fresh-process/cross-version typed/public bytes/hashes;
19. Yoga/loader/lint/snapshot/API/artifact compatibility evidence;
20. final active caller inventory for legacy runtime and remaining WP16 work;
21. deferred shared-inference/domain/output work;
22. explicit proof WP16 was not started.

## Definition of done

WP15 is complete only when:

- WP14 remains complete and reproducible;
- Career no longer calls legacy raw-Boolean/dictionary evaluators or depends on mutable global rule loading;
- every candidate/base/component fact has an immutable typed outcome with truthful status/evidence/errors/trace;
- exact existing candidates/order/denominator/contributions/formulas/confidence/components/indicators/evidence/summary/scoring/trace/public JSON remain unchanged;
- canonical predicates are used only for exact equivalent facts and Career-specific semantics are preserved in a narrow versioned bridge;
- non-factual statuses remain distinct internally and never masquerade as unmatched, while public zero-contribution compatibility remains exact;
- no raw Surya, producer, mutation, CWD discovery, direct handler, tuple/raw-Boolean result, or broad fallback remains in Career;
- no Yoga/rule/table/schema/public-output/CI/dependency/snapshot change occurred;
- all dual-lane, determinism, Career, Yoga, lint, snapshot, API, artifact, and architecture gates pass;
- the report records `VERDICT: COMPLETE` and `WP16_READY: YES`.

At the end, return a concise summary with verdict, model/reasoning used, typed/public APIs, candidate/status/denominator and scoring policies, legacy-call removal, dual-lane counts, cross-version hashes, exact Career/Yoga/snapshot status, files changed, deferred work, and WP16 readiness. **Do not proceed to WP16.**