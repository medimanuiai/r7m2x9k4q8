
Implement **WP11 — migrate the remaining registered predicates to the canonical WP02–WP10 execution boundary** for Prompt-01.

Do not merely review this specification. Implement all permitted work, validate it in both locked Python lanes, and create the WP11 completion report. **Do not proceed to WP12.**

## Objective

Migrate these remaining canonical definitions:

- `HOUSE_OCCUPANT@1.0.0`;
- `ASPECT_EXISTS@1.0.0`, exposed as `ASPECT` and `ASPECT_EXISTS` through the existing alias definition;
- `FUNCTIONAL_ROLE@1.0.0`;
- `PLANET_EXALTED@1.0.0`.

Each canonical path must:

- consume WP07 `PreparedAstroState` and typed `PredicateEvaluationContext` only;
- validate through its existing WP05 schema;
- inspect/query only its exact WP06/WP07 prepared capabilities;
- return the immutable WP02 `PredicateResult` with truthful status, complete safe factual evidence, deterministic trace, and typed errors;
- serialize through WP03;
- execute through the WP09 evaluator/cache with explicit context relevance;
- work as a leaf in the WP10 canonical condition evaluator;
- perform no producer execution, I/O, raw-state fallback, mutation, implicit time, randomness, domain scoring, or astrology inference;
- preserve approved valid legacy truth values, alias identity, active rule/Yoga/Career behavior, public output, and snapshots.

After WP11, all six exposed registered IDs must resolve to five canonical predicate definitions/handlers. Active loaders and Yoga remain on their compatibility paths until WP12/WP13.

## Hard prerequisite gate

Before editing:

1. Locate final WP00-R and WP01–WP10 reports by exact filename.
2. Confirm WP10 records `VERDICT: COMPLETE` and `WP11_READY: YES`.
3. Confirm WP09 canonical evaluator/cache and WP10 condition evaluator contracts reproduce exactly.
4. Reproduce the Python 3.14 and 3.11 baseline: identical node IDs, two clean full-suite runs, Yoga permutations, both loader orders, five-file rule lint, and strict approved snapshots.
5. Record and preserve the inherited dirty worktree.

If any gate fails, stop without production edits and report `VERDICT: BLOCKED` and `WP12_READY: NO`.

## Required references

Read the current implementation plus:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP02–WP10 reports;
- Audit 01, 02, 04, 05, 07, 08, 09, 10, 11, 12, 15, 17, 18, 19, 20, 21, and 22 reports.

Resolve moved documents by filename. Treat completion reports as implementation evidence and audits as defect/test inventories.

## Strict scope

### Permitted

- Add canonical handler modules or a small shared pure handler-support module following the WP08 pattern.
- Extend WP09 routing, definition-specific context relevance, and cache eligibility for newly canonical predicates.
- Add focused per-predicate, alias, cache, condition-leaf, purity, and serialization tests.
- Narrowly adapt canonical evaluator helpers when the WP08 single-predicate assumption must become a five-definition dispatch table.
- Add the WP11 report.

### Forbidden

- Do not change WP05 parameter schemas/vocabularies or WP06 capability declarations unless a direct implementation contradiction proves the locked metadata impossible; stop for owner review instead.
- Do not decide new Aspect doctrine, convert list/graph representations, reorder/deduplicate edges, or reinterpret target-`None` behavior.
- Do not recompute functional roles, read role YAML/tables/CWD, select a new table/fallback, or change role vocabulary.
- Do not select a preferred exaltation source, introduce sign/degree/orb mathematics, or change legacy flag-versus-metadata meaning.
- Do not alias `HOUSE_OCCUPANT` to `PLANET_IN_HOUSE`, despite shared facts; preserve separate identity/version/schema/evidence/trace/cache identity.
- Do not register, activate, remove, or interpret `HOUSE_LORDS_COMBINATION`.
- Do not modify active Yoga, Career/runtime, loaders, rule files/tables, public schemas/output, dependencies, CI, fixtures, snapshots, or approved artifacts.
- Do not implement WP12 format validation or WP13 Yoga migration.

If a protected astrology/public change is required, stop and request approval rather than changing expected output.

## Shared canonical handler pattern

Follow WP08's established result vocabulary and execution order where applicable:

1. resolve canonical definition identity/version;
2. validate parameters through WP05;
3. inspect exact required capabilities in deterministic definition order;
4. query facts only through WP07 typed prepared-state APIs;
5. distinguish factual matched/unmatched from unavailable capability/entity/fact;
6. return exact actual-versus-expected evidence;
7. produce deterministic path-derived trace steps and typed safe errors;
8. catch unexpected defects only at the narrow canonical boundary;
9. serialize through WP03;
10. allow WP09 to cache only final matched/unmatched results.

Use shared helpers only for generic validation/capability/evidence/trace construction. Do not create a generic reflection-heavy handler framework or hide predicate-specific truth semantics.

For all handlers:

- invalid parameters return `invalid_parameters`, empty factual evidence, and do not inspect capabilities;
- unavailable/malformed/version-mismatched/unsupported required capabilities return `missing_capability`, never unmatched;
- missing required entity/fact returns `missing_capability` with a stable predicate-specific error code;
- ordinary unmatched is permitted only after sufficient present facts prove the requested relationship false;
- unexpected errors return `error`, never unmatched, and expose no raw exception text/type/traceback/path;
- logical inputs contain only WP05 normalized values;
- result predicate identity is the canonical registry identity and SemVer.

## `HOUSE_OCCUPANT@1.0.0`

### Parameters and capabilities

Use the exact existing schema order and requirements:

- parameters: required strict `house`, required canonical `planet`;
- `planets.house_placement@1.0.0`;
- `planets.normalized@1.0.0`.

### Truth contract

`HOUSE_OCCUPANT` tests whether the requested canonical planet occupies the requested house. Preserve its separate public vocabulary and identity.

| Observation | Status | Matched |
|---|---|---:|
| planet present and actual house equals expected | `matched` | true |
| planet present and actual valid house differs | `unmatched` | false |
| requested planet absent | `missing_capability` | false |
| planet present but strict house unavailable | `missing_capability` | false |

Do not broaden it into “return every occupant” and do not alias it to `PLANET_IN_HOUSE`. A shared internal pure comparison helper is allowed, but result ID, inputs, evidence vocabulary, trace IDs, definition fingerprint, and cache key must remain `HOUSE_OCCUPANT`-specific.

Evidence must include canonical requested occupant/planet, expected house, actual house when present, equality outcome, and ordered capability rows. Missing results include safe entity/fact state without inventing an occupant.

## `ASPECT` / `ASPECT_EXISTS@1.0.0`

### Identity

- Preserve six exposed registry IDs and five canonical definitions.
- `ASPECT` and `ASPECT_EXISTS` resolve to the same canonical `ASPECT_EXISTS` definition, schema, version, requirements, canonical handler, context relevance, and cache identity.
- Results from either exposed spelling use canonical `predicate_id=ASPECT_EXISTS`.
- Normalized aliases share one WP09 entry; do not duplicate cache entries or traces by requested alias.

### Parameters and capability

Use the exact WP05 optional filter schema:

- `from_house`;
- `to_house`;
- `from_planet`;
- `to_planet`.

An empty mapping is valid and means “any prepared graph edge.” Omitted filters remain absent; explicit `None` is invalid. Use only:

- `aspects.whole_sign_graph@1.0.0`.

Do not require or inspect the basic-conjunction list and do not convert between representations.

### Truth contract

- A ready nonempty graph is evaluated in preserved prepared edge sequence.
- A ready-empty graph is a valid factual `unmatched`, not missing capability.
- Match an edge only with the exact compatibility comparison already characterized for the four normalized optional filters.
- All supplied filters must match the same edge.
- Empty filters match when at least one valid prepared edge exists.
- Preserve source edge order and duplicates in examination and matched evidence.
- Do not sort, deduplicate, reverse, infer, normalize, or synthesize edges.
- Preserve current handling of absent optional edge fields and target-`None`; do not choose new semantics. Lock the characterized behavior explicitly in tests and report it.

Matched evidence must include:

- canonical normalized filters;
- graph capability/version/readiness/source identity;
- total prepared edge count;
- ordered immutable matched edge projections sufficient to show actual source/target/aspect/kind fields that were present;
- matched indexes in source sequence.

Unmatched evidence must include filters, graph availability, edge count, and zero matched indexes without copying raw provider/diagnostic trace. Ready-empty evidence explicitly records zero edges.

Do not include graph `by_planet`, diagnostic trace, raw envelope, or provider objects.

## `FUNCTIONAL_ROLE@1.0.0`

### Parameters, capabilities, and context

Use:

- required nonempty normalized `role_in` tuple with the exact WP05 six-value vocabulary;
- `chart.lagna@1.0.0`;
- `planets.normalized@1.0.0`;
- `roles.functional@1.0.0`.

Never call `compute_functional_roles`, load a table, read CWD/filesystem/environment, or apply a heuristic. Only prepared `roles.functional` facts are authoritative.

The behavior-relevant WP09 context projection is exactly `selected_planets`:

- `None`: evaluate all present prepared planets in canonical nine-planet order;
- empty tuple: explicitly evaluate none and return valid `unmatched` with empty candidate observations;
- nonempty tuple: evaluate those canonical candidates in WP07 canonical order.

`evaluation_instant` is irrelevant and must not fragment the cache. `system_scope` compatibility remains enforced. `evaluation_mode` is currently fixed/default and adds no independent behavior unless the locked context definition permits another mode.

### Truth and availability contract

For each selected candidate, obtain its prepared entity and exact role fact without recomputation.

- If any present candidate has an exact observed role in `role_in`, result is `matched`.
- Preserve all evaluated candidates in canonical order; do not stop at the first role match unless existing approved behavior explicitly did so. Legacy evidence returns all matching planets.
- If no candidate matches and every requested fact is present, result is `unmatched`.
- A selected canonical planet absent from normalized planets is unavailable, not ordinary nonmatch.
- A present selected planet with no role fact is unavailable, not ordinary nonmatch.
- If at least one role matches, matched is decisive while unavailable candidate observations remain recorded safely.
- If no role matches and any selected candidate/entity/role fact is unavailable, return `missing_capability` using deterministic first/highest unavailable observation.
- A ready-empty role mapping with `selected_planets=None` and present planets means required role facts are unavailable, not a factual unmatched role classification.
- An explicitly empty selection is the only zero-candidate case that yields valid unmatched without requiring per-planet role facts.

Evidence must include expected normalized roles, selection policy, ordered candidates, per-candidate entity/fact state, exact observed role when present, membership result, ordered matched planet IDs, and all three capability rows. Never expose table paths/content or role-production diagnostics.

## `PLANET_EXALTED@1.0.0`

### Parameters and capabilities

Use:

- required canonical `planet`;
- `dignity.exaltation_facts@1.0.0`;
- `planets.normalized@1.0.0`.

Use WP07 source-discriminated prepared exaltation records only. Never read mutable flags/metadata directly.

### Preservation-locked truth contract

Do not introduce astrology doctrine. Preserve characterized legacy factual meaning by source:

- explicit Boolean flag record with value `True`: matched;
- explicit Boolean flag record with value `False`: unmatched;
- legacy metadata exaltation entry with a finite numeric value, including zero: matched by configured-entry presence, while preserving the numeric value as evidence;
- absence of the requested normalized planet: `missing_capability`;
- present planet but no prepared exaltation fact: `missing_capability`, not factual false;
- malformed/conflicting sources: `missing_capability` with the existing malformed-capability error;
- do not compare sign, longitude, degree, orb, dignity, or placement;
- do not prefer a flag over metadata or combine conflicting sources. WP07 already marks overlapping conflicts malformed.

If WP07 admits another safe source/value combination, do not guess its truth meaning. Return a typed non-factual unsupported/malformed result and document it unless the locked characterization explicitly resolves it.

Evidence must include canonical planet, ordered source-discriminated records, exact source kind, exact preserved Boolean/numeric value, interpretation rule (`explicit_flag_boolean` or `configured_metadata_entry`), resulting factual state, and capability rows. A numeric degree is configuration evidence, not a computed current longitude comparison.

## Evidence, trace, and error vocabulary

Use deterministic predicate-specific root prefixes:

- `house_occupant.*`;
- `aspect_exists.*` for both exposed Aspect IDs;
- `functional_role.*`;
- `planet_exalted.*`.

At minimum represent parameter validation, capability inspection, entity/fact retrieval, predicate-specific comparison, and final disposition. Use stable parent relationships and decisive error codes. Do not fabricate unexecuted steps.

Create a shared safe capability-row vocabulary consistent with WP08. Predicate-specific evidence must contain actual-versus-expected facts, not only echoed inputs. Exact fields must be documented and locked with strict projection/byte assertions.

Reuse existing safe error codes where meanings match. Add only stable predicate-specific codes needed for missing planet/house/role/exaltation fact or unsupported preserved source. Every error has fixed message, canonical predicate ID, bounded safe details, and accurate recoverability.

No evidence/trace/error may include raw source mappings, graph diagnostic traces, YAML/table paths, exception messages/classes, traceback, object identity, CWD, time, cache telemetry, Yoga/Career scores, or public narrative.

## WP09 evaluator/cache integration

Replace the single-handler conditional route with a deterministic canonical dispatch table covering all five canonical definitions. Do not use reflection, import scanning, mutable runtime registration, or legacy fallback.

Context relevance:

| Canonical predicate | Relevant context |
|---|---|
| `PLANET_IN_HOUSE` | none, unchanged |
| `HOUSE_OCCUPANT` | none |
| `ASPECT_EXISTS` | none |
| `FUNCTIONAL_ROLE` | canonical `selected_planets` only |
| `PLANET_EXALTED` | none |

Prove:

- aliases resolve before dispatch/key construction;
- `ASPECT` and `ASPECT_EXISTS` share key/value;
- separate predicate identities with equivalent underlying facts do not collide;
- relevant role selection changes isolate cache entries;
- neutral instant/context differences do not;
- every included state fact/readiness/version/source/content difference isolates through WP07 digest;
- only matched/unmatched results cache; missing/invalid/error continue to re-evaluate;
- cache bound/LRU/freeze/clear/concurrency contracts remain unchanged.

## WP10 condition integration

Canonical WP10 leaf evaluation must now accept all six exposed registered IDs without `predicate_not_migrated`:

- `ASPECT` and `ASPECT_EXISTS` produce canonical `ASPECT_EXISTS` leaf results;
- all other IDs preserve their own canonical identity;
- logical parent status/short-circuit/skipped behavior remains unchanged;
- leaf evidence/errors/traces remain complete and recursively serialized;
- no active Yoga redirection occurs yet.

Unknown IDs and `HOUSE_LORDS_COMBINATION` remain typed definition errors, never ordinary false.

## Tests first

Create focused handler modules/tests before production edits. Cover at least:

### Shared contract

- exact definition/schema/version/capability requirements;
- valid normalization and complete invalid matrices from WP05;
- all WP06 readiness states independently and in deterministic combinations;
- exact matched/unmatched/missing/invalid/error result contracts;
- deep immutability/source mutation isolation;
- deterministic trace/error/evidence fields;
- WP03 logical/full projections, exact bytes/hashes, telemetry neutrality;
- fresh-process and cross-Python equality;
- purity/static forbidden imports/calls.

### `HOUSE_OCCUPANT`

- matched, different-house unmatched, absent planet, unavailable house;
- exact actual/expected evidence;
- separate identity/cache entry from equivalent `PLANET_IN_HOUSE`;
- no all-occupants expansion or alias metadata change.

### Aspect alias/handler

- each exposed ID and case normalization;
- canonical result identity and one shared cache entry;
- empty filters, each single filter, all filters;
- ready-empty graph;
- matched and unmatched nonempty graph;
- multiple ordered matches and duplicates preserved;
- list/graph mismatch unavailable;
- absent optional edge fields and target-`None` characterized behavior;
- no edge conversion, inference, sorting, deduplication, diagnostic trace leakage, or input mutation.

### Functional role

- every admitted role vocabulary value remains distinct;
- role tuple normalization/order;
- selection `None`, empty, single, multiple, and normalization;
- all matching planets preserved in canonical order;
- no match with complete facts;
- matched plus unavailable candidate;
- absent selected entity, missing role fact, ready-empty role map;
- relevant selection cache isolation and neutral-instant sharing;
- monkeypatch guards proving no producer/table/filesystem/CWD access.

### Exaltation

- explicit true and false flags;
- metadata positive numeric and zero;
- absent planet and absent fact;
- conflicting/malformed sources;
- version/source isolation;
- unsupported source/value fails non-factually;
- no sign/longitude/degree/orb comparison or source preference.

### Evaluator/condition/cache

- five-definition dispatch inventory and no reflection/legacy fallback;
- every exposed ID evaluates canonically;
- aliases share cache identity; other definitions do not collide;
- matched/unmatched cached, all non-factual statuses not cached;
- WP10 nested conditions using each exposed ID preserve children/status/trace;
- unknown and `HOUSE_LORDS_COMBINATION` remain typed errors;
- LRU/bounds/freeze/clear/isolation/concurrency unchanged.

### Compatibility

- six exposed IDs/five definitions and five legacy handler identities remain stable;
- current valid legacy matched/unmatched outcomes characterized before/after;
- active Yoga firing/order/evidence/public projection unchanged;
- Career/runtime, rules, lint, loaders, output and approved snapshot unchanged;
- dormant Yoga helpers are neither activated nor removed.

Do not weaken/delete existing tests and never update the approved snapshot.

## Validation gates

Run in both locked Python 3.14 and 3.11 lanes with bytecode/cache isolation and unique ignored temporary paths:

1. WP11 handler/alias/evaluator/cache/condition/purity focused tests.
2. WP02–WP10 focused modules.
3. All `tests/rules`.
4. WP01 predicate/Yoga/Career characterization.
5. Targeted legacy predicate/evaluator/condition, Yoga, Career, runtime, role, Aspect, exaltation, writer, linter, determinism, and snapshot regressions.
6. Exact full collection comparison and node-ID SHA-256.
7. Complete suite twice from fresh processes per lane.
8. Yoga normal/reverse/A/B/C permutations.
9. Both loader-trigger orders.
10. Rule lint proving all five supported files, including `yogas.yaml`, are inspected exactly once.
11. Strict approved-snapshot comparison twice per lane using temporary output and no update mode.
12. Fresh-process/cross-version representative result bytes/hashes for each canonical definition, Aspect alias equality, role context isolation, and a mixed WP10 tree containing the newly migrated leaves.
13. `git diff --check` and scoped artifact/status checks.

Record exact commands, versions, counts, node-ID hash, bytes/hashes, cache keys/entry counts, source/context distinctions, and protected compatibility evidence. Any astrology/public/snapshot difference is a blocker.

## Required completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP11/WP11.md`

The report must include:

1. `VERDICT: COMPLETE` or `VERDICT: BLOCKED`;
2. `WP12_READY: YES` or `WP12_READY: NO`;
3. actual model/reasoning used;
4. prerequisites/baseline evidence;
5. exact files changed and handler/evaluator APIs;
6. six-ID/five-definition identity and alias table;
7. exact parameter/capability/context requirement table;
8. per-predicate truth/availability matrices;
9. exact evidence schemas;
10. exact trace step/error vocabularies;
11. Aspect edge/filter/ordering/target-`None` preservation decisions;
12. functional-role candidate/context/missing-fact policy and no-producer proof;
13. exaltation source/value preservation policy and no-doctrine proof;
14. WP09 key/context/cache integration evidence;
15. WP10 leaf/recursive condition integration evidence;
16. test-to-requirement traceability;
17. exact dual-lane commands/counts and collection hash;
18. fresh-process/cross-version result/tree bytes/hashes;
19. Yoga/loader/lint/Career/snapshot/artifact compatibility evidence;
20. deferred WP12/WP13/WP16 work and any owner decision required;
21. explicit proof WP12 was not started.

## Definition of done

WP11 is complete only when:

- WP10 remains complete and reproducible;
- all six exposed registered IDs execute through five canonical prepared-state handlers;
- every handler applies WP05 validation and WP06/WP07 truthful availability semantics;
- matched/unmatched evidence contains complete actual-versus-expected facts;
- no invalid/missing/malformed/version/unsupported/entity/fact state becomes ordinary false;
- Aspect aliases share canonical result/cache identity while graph representation/order/duplicates and ambiguous edge behavior are preserved;
- `HOUSE_OCCUPANT` remains separately identified;
- functional roles use prepared facts only with exact selected-planet context identity;
- exaltation preserves explicit source/value meaning without new astrology inference;
- WP09 cache and WP10 condition contracts work for every exposed ID;
- no active Yoga/Career/loader/rule/public-output/CI/dependency/snapshot migration occurred;
- all dual-lane, determinism, compatibility, lint, snapshot, and artifact gates pass;
- the report records `VERDICT: COMPLETE` and `WP12_READY: YES`.

At the end, return a concise summary with verdict, model/reasoning used, files and canonical handlers, identity/alias/context policies, per-predicate truth/evidence/trace contracts, cache/condition integration, dual-lane counts, cross-version hashes, compatibility/snapshot status, deferred issues, and WP12 readiness. **Do not proceed to WP12.**