Implement **WP08 — migrate `PLANET_IN_HOUSE` as the canonical reference predicate end-to-end** for Prompt-01.

Do not merely review this specification. Implement the permitted changes, run the complete validation gates, and create the WP08 completion report. **Do not proceed to WP09.**

## Objective

Migrate only the canonical `PLANET_IN_HOUSE@1.0.0` execution path so that it:

- accepts the WP07 immutable `PreparedAstroState` and typed `PredicateEvaluationContext` boundary;
- applies the WP05 schema before factual evaluation;
- checks the exact WP06 capability requirements and readiness states;
- returns the WP02 immutable canonical `PredicateResult` with typed status, evidence, trace, and errors;
- uses WP03 canonical logical/full serialization without `default=str` or ad hoc conversion;
- distinguishes matched, valid unmatched, missing entity/data/capability, malformed/version-incompatible capability, invalid parameters, and unexpected error;
- performs no mutation, I/O, producer execution, implicit time lookup, randomness, cache access, or astrology inference;
- preserves valid legacy factual truth values and all current Yoga, Career, rule, snapshot, and public behavior.

This package establishes a reviewed reference pattern for WP11. It does **not** migrate `HOUSE_OCCUPANT` or any other predicate, replace the evaluator/cache contract, introduce logical operators, change Yoga/Career integration, or remove legacy compatibility paths.

## Hard prerequisite gate

Before editing:

1. Locate and read the final WP00-R and WP01–WP07 completion reports by filename rather than assuming stale paths.
2. Confirm WP07 records `VERDICT: COMPLETE` and `WP08_READY: YES`.
3. Reproduce the current dual-Python baseline using the locked Python 3.14 and 3.11 environments.
4. Confirm identical collection node IDs in both lanes, both full suites pass, rule lint inspects all five supported rule files exactly once, and strict approved-snapshot comparison passes without updating the golden.
5. Record the inherited dirty worktree before editing and preserve unrelated changes.

If any gate fails, stop without production edits and report `VERDICT: BLOCKED` and `WP09_READY: NO` with exact evidence.

## Required references

Read the actual current implementation plus:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP02 through WP07 reports;
- Audit 02, 04, 05, 07, 08, 09, 10, 11, 18, 19, 20, 21, and 22 reports.

Resolve moved documents by exact filename. Treat completion reports as implementation evidence and audits as problem inventories.

## Locked scope

### Permitted

- Add focused WP08 tests before production edits.
- Add a canonical `PLANET_IN_HOUSE` handler or a narrowly scoped canonical execution seam using existing WP02–WP07 APIs.
- Minimally adjust registry metadata/bootstrap wiring only if required to identify the canonical handler while preserving the six registered IDs and five legacy handler identities outside the new seam.
- Add a narrowly scoped adapter at the evaluator boundary if unavoidable for compatibility tests.
- Add safe stable error codes or helper factories only where the existing canonical model lacks the construction convenience needed by this predicate.
- Add the WP08 completion report.

### Forbidden

- Do not implement WP09's content-addressed bounded cache, key composition, eviction, concurrency, or global-cache replacement.
- Do not migrate or change `HOUSE_OCCUPANT`, `ASPECT`, `ASPECT_EXISTS`, `FUNCTIONAL_ROLE`, or `PLANET_EXALTED`.
- Do not change condition `AND`/`OR`/`NOT`, Yoga, Career, loaders, rule files, astrology tables, public schemas, dependencies, CI, snapshots, or approved artifacts.
- Do not infer house placement, compute planets, call normalizers/enrichment producers, read raw Surya/provider objects, or fall back from unavailable prepared facts to mutable legacy data.
- Do not decide whether `HOUSE_OCCUPANT` is an alias; that remains deferred.
- Do not introduce new astrology semantics.

If completion requires any forbidden or semantic change, stop and request owner approval. Do not alter expected tests or snapshots to accommodate it.

## Required execution boundary

Use the current repository APIs and names discovered from WP02–WP07; do not create duplicate models, schemas, capability catalogs, canonicalizers, or prepared-state types.

The canonical handler must consume, directly or through a minimal typed request object:

- canonical predicate identity `PLANET_IN_HOUSE`;
- predicate version `1.0.0` from the registry definition;
- raw caller parameters to be normalized by the WP05 schema;
- `PreparedAstroState` from WP07;
- `PredicateEvaluationContext` from WP07.

It must not accept mutable `AstroState` as its canonical factual input. If the current legacy evaluator must remain operational until WP09, keep an explicit, isolated compatibility path and prove it does not silently bypass the prepared boundary for canonical WP08 tests.

Do not redesign the complete evaluator. The minimal WP08 seam must be removable or directly reusable by WP09.

## Parameter contract

Apply the existing WP05 `PLANET_IN_HOUSE@1.0.0` schema exactly:

- required `planet` normalized to one of the nine canonical planet IDs;
- required `house` must be an actual non-Boolean integer from 1 through 12;
- reject missing keys, explicit `None`, unknown keys, invalid strings/types, Boolean values, floats, and out-of-range houses;
- use only the schema's existing trim/case normalization; add no semantic coercion;
- place only canonical normalized parameters in `PredicateResult.inputs` and canonical trace details.

All invalid forms return `status=invalid_parameters`, `matched=False`, no factual evidence, and deterministic typed errors. They must not query prepared capability content.

Use stable safe error codes and paths from existing WP05/WP02 APIs where available. Do not include raw input representations, exceptions, tracebacks, memory addresses, or provider data.

## Capability contract

Use the exact WP06 requirements already registered for `PLANET_IN_HOUSE`:

- `planets.normalized@1.0.0`;
- `planets.house_placement@1.0.0`.

Inspect both through WP07 canonical query/inspection APIs. Do not read prepared internals ad hoc when a typed API exists.

Handle readiness truthfully:

- required capability ready with valid content: continue;
- missing, ready-empty where prohibited, malformed, version mismatch, or unsupported: return `missing_capability` with deterministic typed error(s) and capability evidence/trace that contains only safe IDs, required/observed versions, readiness, source kind when safe, and issue codes;
- never convert unavailable or malformed capability data into ordinary `unmatched`;
- never use partial house content after the house-placement capability is malformed.

Preserve the distinction between an unavailable capability, an absent canonical planet entity, and a present planet whose house fact is unavailable.

## Locked factual truth table

After parameters and capabilities are valid:

| Observation | Status | Matched | Required meaning |
|---|---|---:|---|
| requested planet present; actual house equals expected | `matched` | true | factual equality established |
| requested planet present; actual valid house differs | `unmatched` | false | factual inequality established |
| requested canonical planet absent | `missing_capability` | false | required entity/fact unavailable; never ordinary false |
| planet present but strict house fact unavailable | `missing_capability` | false | required fact unavailable |

Do not require all nine planets globally and do not infer an absent planet. Use WP07's typed entity/house observations.

## Evidence contract

Evidence must be deterministic, immutable, JSON-safe, and sufficient to explain the result without repeating only caller input.

For matched and valid unmatched results, include a stable factual structure containing at minimum:

- canonical planet ID;
- expected house;
- observed actual house;
- equality outcome;
- the two required capability IDs and their contract versions/readiness in a canonical order.

For missing entity/fact/capability results, include only safe availability observations:

- requested canonical planet and expected house;
- entity presence state where known;
- required capability identity, version expectation, readiness, safe source kind, and issue codes where applicable;
- no invented actual house and no raw source payload.

Invalid parameters have no factual evidence. Unexpected errors have no raw exception evidence.

Choose exact field names once, document them in the report, and lock them with exact projection/byte assertions so WP11 can follow the same vocabulary. Do not expose telemetry in logical evidence.

## Trace contract

Return deterministic typed `PredicateTraceStep` values with stable caller-independent step IDs. At minimum represent the applicable sequence:

1. parameter validation;
2. required capability inspection;
3. canonical planet lookup;
4. house observation/comparison;
5. final disposition.

Requirements:

- preserve semantic left-to-right order;
- use stable `parent_step_id` relationships if child steps are used;
- record only canonical safe details and observations;
- attach stable `error_code` on the decisive failed step;
- do not include clock values, durations, cache state, UUIDs, object IDs, paths, raw exceptions, or provider representations;
- do not fabricate steps that did not execute: invalid parameters must show that factual/capability evaluation was skipped or absent using one documented deterministic policy.

The exact trace vocabulary and step IDs become the reference pattern for WP11 and must be documented.

## Error and unexpected-failure policy

Use typed `PredicateError` values with stable codes, canonical predicate ID, safe immutable details, and accurate `recoverable` flags.

- parameter failures: `invalid_parameters`;
- capability/entity/fact unavailability: `missing_capability`;
- unexpected internal construction/query defect: `error`.

Catch exceptions only at the narrow canonical execution boundary. Never use a broad fallback that turns defects into `unmatched`. Never expose `str(exception)`, exception class representations, stack traces, source paths, or arbitrary runtime values in result/evidence/trace.

Tests may inject a controlled failure to prove safe conversion, but production code must not add a test-only predicate or global mutation.

## Serialization and identity

Use WP03 canonical result projection APIs. Prove:

- exact logical projection and exact canonical UTF-8 bytes for representative matched, unmatched, missing, invalid, and error results;
- deterministic lowercase SHA-256 where the existing API exposes it;
- logical equality and logical bytes do not change with `cache_hit` or `evaluation_time_ms`;
- full/telemetry projection changes only as already defined by WP03;
- mappings are order-independent where canonicalized; trace sequence remains significant;
- no `dataclasses.asdict`, pickle, `repr`, `default=str`, or arbitrary-object serialization is introduced.

WP08 must not define the WP09 cache key.

## Purity and architecture enforcement

Add focused static and behavioral tests proving the canonical handler/module:

- imports no mutable AstroState/raw Chart/Surya model, normalizer, enrichment producer, Yoga, Career, loader, output assembler, filesystem/network/subprocess/environment/time/random/UUID/cache service;
- performs no mutation of prepared state, context, parameters, registry, capability content, globals, or returned results;
- performs no I/O and calls no producer;
- reads facts through the WP07 prepared query boundary;
- does not persist object identity, hashes, representations, or raw values;
- returns a canonical WP02 `PredicateResult` on every canonical path;
- leaves the other registered predicate handlers and active callers on their existing compatibility behavior until their owning packages.

## Tests first

Create a focused WP08 test module before production changes. Cover at least:

### Parameters

- canonical valid input;
- case/whitespace normalization;
- parameter mapping insertion-order equivalence;
- missing `planet`; missing `house`; explicit `None` for each;
- unknown key;
- unknown/non-string planet;
- house 0, 13, negative, Boolean, float, numeric string, list, and mapping;
- unsafe/cyclic/raw runtime values rejected without unsafe serialization.

### Factual outcomes

- matched canonical planet/house;
- valid unmatched with actual and expected houses preserved;
- absent requested planet;
- present planet with unavailable house;
- equivalent independently prepared states produce identical logical results;
- source mutation after preparation cannot alter the result;
- selection context `None`, empty, and nonempty does not silently change factual semantics unless an existing locked context rule explicitly requires it; document the decision and do not invent one.

### Capabilities

- both requirements ready;
- each requirement missing independently;
- malformed normalized planets;
- malformed house placement;
- version mismatch for each;
- unsupported requirement;
- prohibited ready-empty state;
- safe deterministic ordering when more than one requirement fails;
- no partial fact use and no fallback to mutable data.

### Result contract

- exact predicate ID/version/status/matched/input/evidence/trace/error contract for matched, unmatched, missing, invalid, and injected error;
- deep immutability and caller/source mutation isolation;
- deterministic error codes and recoverability;
- exact trace step order, IDs, parent links, decisive error link, and absence of telemetry/raw values;
- canonical logical/full projections, bytes, and repeated hashes;
- telemetry-independent logical equality/bytes;
- fresh-process and cross-Python equality for representative results.

### Compatibility

- current valid legacy matched and unmatched truth values preserved;
- existing `PLANET_IN_HOUSE` evaluator/condition characterization still passes through the approved compatibility boundary;
- registry remains six IDs/five legacy handler identities unless the current WP04 design explicitly represents a separate canonical callable without changing that invariant;
- `HOUSE_OCCUPANT` and all other handlers are byte/behavior unchanged;
- WP01 characterization, Yoga orders, loader-trigger orders, Career, lint, and approved snapshot remain unchanged.

Do not weaken or delete existing tests. Do not update the approved snapshot.

## Validation gates

Run all applicable commands in both locked Python 3.14 and Python 3.11 lanes with bytecode/cache isolation and unique ignored temporary paths:

1. WP08 focused tests.
2. WP02 model, WP03 canonical serialization, WP04 registry, WP05 parameters, WP06 capabilities, and WP07 prepared-state tests.
3. All `tests/rules`.
4. WP01 predicate/Yoga/Career characterization.
5. Targeted predicate/evaluator/condition, Yoga, Career, runtime, role, Aspect, writer, linter, and snapshot-related regression set.
6. Complete collection; compare exact node-ID lists and SHA-256 between lanes.
7. Complete suite twice from fresh processes per lane.
8. Yoga normal, reverse, and the WP00-R explicit A/B/C node permutations per lane.
9. Both loader-trigger orders per lane.
10. Rule lint; prove all five supported `.yml`/`.yaml` files, including `yogas.yaml`, were inspected exactly once.
11. Strict approved snapshot comparison twice per lane using temporary output; never approval/update mode.
12. Fresh-process and cross-version canonical result byte/hash comparison.
13. `git diff --check` and scoped artifact/status checks proving no fixed/tracked test artifact or approved golden changed.

If valid legacy factual truth, Yoga/Career/public output, collection parity, determinism, lint, or snapshot gates fail, stop. Do not normalize the failure by changing expected output.

## Required completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP08/WP08.md`

The report must include:

1. `VERDICT: COMPLETE` or `VERDICT: BLOCKED`;
2. `WP09_READY: YES` or `WP09_READY: NO`;
3. actual model/reasoning used;
4. prerequisite and baseline evidence;
5. before/after execution and compatibility boundaries;
6. exact files changed;
7. canonical handler/API locations and signatures;
8. exact parameter normalization/validation matrix;
9. capability requirement/readiness matrix;
10. factual truth table;
11. exact evidence schema for every status;
12. exact trace step vocabulary/order/parent/error-link policy;
13. typed error codes and recoverability policy;
14. canonical logical/full serialization and digest evidence;
15. purity/static-boundary evidence;
16. test-to-requirement traceability;
17. exact dual-lane commands, collection counts/node-ID hash, test counts, Yoga/loader/lint/snapshot results;
18. fresh-process/cross-version bytes and hashes;
19. confirmation that WP09 cache work and all other predicate migrations were not started;
20. deferred semantic issues and any blocker requiring owner approval.

## Definition of done

WP08 is complete only when:

- WP07 remains complete and reproducible;
- `PLANET_IN_HOUSE@1.0.0` alone uses the WP05–WP07 canonical boundary;
- every canonical path returns the immutable WP02 result and WP03 serialization works exactly;
- invalid input never becomes factual false;
- missing/malformed/version-incompatible capability or missing fact/entity never becomes ordinary unmatched;
- matched and valid unmatched results contain actual-versus-expected factual evidence;
- trace and errors are stable, safe, typed, immutable, and deterministic;
- valid legacy factual outputs remain unchanged;
- no producer, I/O, mutation, implicit time, randomness, raw-state fallback, or cache implementation enters the canonical handler;
- other predicates, Yoga, Career, rules, public output, CI, dependencies, and approved snapshots are unchanged;
- all required dual-lane and determinism gates pass;
- the report records `VERDICT: COMPLETE` and `WP09_READY: YES`.

At the end, return a concise implementation summary with the verdict, model/reasoning used, files changed, canonical handler/seam, result/evidence/trace/error contracts, dual-lane test counts, cross-version bytes/hashes, compatibility/snapshot status, deferred issues, and WP09 readiness. **Do not proceed to WP09.**