Implement **WP12 — validate active Yoga/current condition formats against the canonical predicate, parameter, capability, and operator contracts** for Prompt-01.

Do not merely review this specification. Implement the permitted validation boundary, run all dual-lane gates, and create the WP12 completion report. **Do not proceed to WP13.**

## Objective

Create one deterministic, immutable, source-attributed definition-validation boundary for:

- current F1 Yoga condition trees: logical `{type, children}` and leaf `{type, params}` under the existing plural `conditions` wrapper;
- current F2 direct bare nodes using the same tree/leaf shapes.

The boundary must:

- validate structure and operator arity using WP10's exact current-format grammar and safety limits;
- resolve predicate IDs/aliases through the finalized WP04 registry;
- validate leaf parameters through WP05 schemas;
- bind every leaf to its canonical predicate ID and SemVer;
- verify required capability declarations against the finalized WP06 catalog without inspecting a chart;
- preserve source child order and current valid syntax;
- produce immutable normalized definitions plus stable, safe, source-attributed issues;
- reject unknown predicates/operators, malformed nodes, invalid parameters, duplicates, unsafe depth/count/cycles, and unsupported alternate formats as definition errors—never factual unmatched;
- provide a strict validated Yoga-loading API for WP13 while leaving the currently active Yoga execution path behavior unchanged in WP12;
- preserve F3 flat M1/Career runtime as an explicit temporary compatibility path.

WP12 is a minimal validated boundary, not the future grammar, canonical AST, macro/reference compiler, optimizer, or governance system.

## Hard prerequisite gate

Before editing:

1. Locate final WP00-R and WP01–WP11 reports by exact filename.
2. Confirm WP11 records `VERDICT: COMPLETE` and `WP12_READY: YES`.
3. Confirm all six exposed IDs resolve to five canonical handlers and all WP09/WP10 contracts reproduce.
4. Reproduce the locked Python 3.14 and 3.11 baseline: identical collection IDs, two clean full-suite runs, all Yoga permutations, both loader orders, five-file lint, and strict approved snapshots.
5. Record and preserve the inherited dirty worktree.

If any gate fails, stop without production edits and report `VERDICT: BLOCKED` and `WP13_READY: NO`.

## Required references

Read the current implementation plus:

- `Prompt-01-Locked-Decisions-and-Execution-Plan.md`;
- `Prompt-01-Final-Audit-Consolidation.md`;
- final WP02–WP11 reports;
- Audit 01, 04, 07, 08, 12, 13, 14, 15, 17, 19, 21, 22, 23, and 24 reports.

Resolve moved documents by filename. Treat completion reports as implementation evidence and audits as defect/test inventories.

## Strict scope

### Permitted

- Add immutable validation outcome/issue/source/normalized-definition models.
- Add a shared F1/F2 condition-definition validator using current WP04–WP06 and WP10 contracts.
- Add a strict, side-effect-free Yoga rule-set validation/loading API for later WP13 adoption.
- Narrowly improve deterministic Yoga parsing/validation helpers without redirecting active Yoga evaluation.
- Add tests for current valid sources and synthetic invalid definitions.
- Add the WP12 report.

### Forbidden

- Do not implement or accept F4 `op/args`, F5 canonical AST fields, F6 macros/expressions, `ALL`, `ANY`, `EXISTS`, `COUNT`, references, reusable blocks, external fragments, compilation, optimization, or execution plans.
- Do not rewrite any YAML/rule file.
- Do not activate, register, remove, reinterpret, or add semantics for `HOUSE_LORDS_COMBINATION`.
- Do not migrate or redirect active Yoga evaluation; WP13 owns that change.
- Do not migrate F3 flat runtime/Career rules, alter scoring, or change Career output.
- Do not change predicate schemas, capability declarations, handler semantics, registry aliases, public schemas/output, dependencies, CI, snapshots, fixtures, or approved artifacts.
- Do not use validation to silently skip invalid active rules in the current production Yoga path during WP12.

If strict validation reveals an unresolved active-source defect, report it truthfully and preserve current runtime compatibility. Do not make the definition appear valid and do not change its astrology meaning.

## Accepted compatibility formats

Accept only:

### F1 Yoga wrapper and tree

```text
rule["conditions"] = {"type": "AND"|"OR"|"NOT", "children": [...]}
leaf = {"type": <registered predicate ID>, "params": {...}}
```

The wrapper is plural `conditions` containing exactly one mapping. Do not accept a list wrapper, implicit AND, singular `condition`, or simultaneous wrapper aliases.

### F2 direct bare node

```text
{"type": <operator-or-predicate>, "children": [...]}
{"type": <registered predicate ID>, "params": {...}}
```

F2 is a supported internal canonical-entry compatibility format for direct validation/evaluation; it is not declared a public DSL.

### Explicitly unsupported in WP12

- F3 flat rules are preserved outside this validator as legacy compatibility;
- F4/F5/F6 and JSON rule-source parity are rejected/not routed here;
- unknown top-level/condition/leaf fields are errors, not ignored metadata.

## Registry bootstrap and validation ordering

Validation must never depend on incidental decorator/import order.

Use the existing WP04 production bootstrap/readiness API and prove:

1. registry and capability catalog are fully bootstrapped, finalized, and frozen before rule validation;
2. six exposed IDs/five definitions are identical across import orders;
3. aliases resolve deterministically;
4. validation never mutates the registry/catalog;
5. a deliberately unready/incomplete synthetic registry produces a stable boundary error rather than classifying valid IDs as unknown;
6. no dynamic test registration leaks into production validation.

Do not add import scanning/plugin discovery or restore decorator-owned mutable registration.

## Minimal immutable validation models

Use current WP02/WP03 immutability/canonicalization conventions. Add the smallest exact models needed, with equivalent repository naming:

### `RuleSourceIdentity`

Fields:

- stable logical `source_name` using a repository-relative rule identity or caller-provided safe name, never absolute path/CWD;
- optional canonical `rule_id`;
- optional nonnegative `rule_index`.

No filesystem path, line/column claim, URI, object identity, or parser exception text.

### `DefinitionIssue`

Fields:

- stable `code`;
- fixed safe `message`;
- logical condition `node_path`;
- source identity;
- optional canonical/requested predicate ID;
- optional canonical parameter name;
- immutable bounded safe details;
- strict severity (`error` only in WP12 unless an approved warning contract already exists).

Issues never contain raw supplied values, mappings, YAML fragments, exception text/type/traceback, absolute paths, secrets, repr, or memory addresses.

### `ValidatedNodeBinding`

This is validation metadata, **not a future AST**. It records for each node in declared preorder:

- stable path-derived `node_id`/`node_path`;
- node kind (`logical` or `predicate`);
- requested normalized type;
- canonical operator or canonical predicate ID;
- resolved predicate SemVer for leaves;
- canonical normalized parameters for leaves;
- exact ordered required capability IDs/versions for leaves;
- declared child count for logical nodes.

Do not add macro/reference/source-span/execution-plan/domain/output fields.

### `ValidatedConditionDefinition`

Fields:

- source identity;
- deeply immutable normalized current-format condition mapping suitable for WP10 canonical evaluation;
- ordered tuple of node bindings;
- canonical definition fingerprint/bytes identity through WP03.

### `DefinitionValidationOutcome`

Fields:

- strict `valid` Boolean;
- validated definition only on success;
- ordered nonempty issues only on failure.

Enforce contradictory-state invariants and deep immutability.

If existing canonical models make different field names more consistent, preserve these semantics and document the exact final inventory.

## Structural validation contract

Match WP10 exactly:

- `AND`, `OR`, `NOT` only;
- left-to-right declared child order;
- nonempty AND/OR;
- exactly one NOT child;
- list children only;
- mapping nodes only;
- exact `type` plus `children` for logical nodes;
- exact `type` plus `params` for leaves;
- no missing/null/wrong-type containers;
- no unknown/misspelled/alternate fields;
- maximum depth 64 with root level 1;
- maximum total nodes 4096 including root;
- cycle rejection;
- stable path IDs identical to WP10 defaults when evaluated.

The validator may share a pure structural helper with WP10 to prevent drift. Do not make validation execute predicates or touch the evaluator/cache.

Issue order is deterministic preorder: structural issue at a node before descendants; siblings in declared order; within a leaf, WP05's existing parameter issue order. Fatal cycle/depth/node-bound failures use one documented deterministic issue policy without recursion crash.

## Predicate, version, parameter, and capability binding

For each leaf:

1. resolve the requested type through the finalized WP04 registry;
2. normalize case/trim only according to existing registry policy;
3. preserve requested exposed ID in binding metadata where useful, but store canonical predicate ID in executable normalized definition;
4. bind exact registry SemVer—current F1/F2 nodes do not declare versions;
5. validate raw `params` through the exact WP05 schema;
6. store only canonical normalized inputs;
7. bind exact ordered WP06 capability requirements;
8. verify every requirement/version exists in the finalized catalog;
9. never inspect chart readiness/content at definition validation time.

`ASPECT` binds canonically to `ASPECT_EXISTS@1.0.0`; all other exposed IDs bind to themselves. A node-level `version`, `predicate_version`, capability list, or alternate parameter container is an unknown-field error, not an override.

Unknown predicate IDs are definition errors. Known aliases are valid. `HOUSE_LORDS_COMBINATION` remains unknown and invalid; do not route it to a dormant helper and do not turn it into factual unmatched.

## Normalized definition and fingerprint policy

The normalized current-format mapping must:

- retain only `type`/`children` or `type`/`params`;
- use canonical operator/predicate type values;
- use WP05 normalized immutable parameters;
- preserve declared child order;
- contain no source metadata, raw values, parser objects, rule metadata, telemetry, registry object, callable, or capability content.

Definition identity includes:

- validation schema/version;
- normalized condition mapping;
- each canonical predicate ID/version;
- normalized parameters;
- exact capability requirement IDs/versions;
- stable logical source/rule identity only if the approved identity contract requires source-specific definitions.

Prefer separate semantic and source fingerprints if source identity would prevent equivalent definitions from sharing semantic bytes. Document inclusion/exclusion precisely. Equivalent F1/F2 trees from different objects and mapping insertion orders must have identical semantic bytes/hash.

## Yoga rule-set validation API

Add a side-effect-free strict API that accepts parsed Yoga rule records or an explicit file path/source and returns immutable validation results. It must not mutate/rebind `RULE_REGISTRY`, import a stale registry reference, or silently overwrite duplicate IDs.

For every rule:

- retain existing top-level required-field presence validation;
- additionally validate safe field container/types only to the degree required for deterministic rule identity and condition extraction;
- require a nonempty stable rule ID;
- reject duplicate rule IDs within the supplied Yoga set deterministically;
- validate exactly the plural `conditions` mapping through the shared condition validator;
- retain source file logical name and zero-based rule index;
- aggregate issues in source order instead of swallowing exceptions or silently skipping;
- return valid rules in original source order;
- do not register/evaluate them in WP12.

Parsing must use explicit supplied paths for tests/API; no CWD lookup. Convert missing file, unreadable file, invalid YAML, wrong document root, nonmapping record, and unsafe content to stable issues without raw parser/path detail. Do not add JSON support.

### Active `HOUSE_LORDS_COMBINATION` disposition

The current `yogas.yaml` contains an unregistered `HOUSE_LORDS_COMBINATION` leaf. WP12 must:

- report it as a deterministic unknown-predicate definition issue at the exact logical rule/node path;
- not register/implement/remove/rewrite it;
- not silently skip or mark its containing rule valid in the strict validation outcome;
- not redirect the active production Yoga loader/evaluator yet, so current Yoga firing/public compatibility remains unchanged;
- record this known strict-validation finding prominently in WP12.md as input for WP13's compatibility decision.

This known issue does not by itself make WP12 implementation incomplete. `WP13_READY: YES` is allowed only if the strict validator behaves exactly as specified and WP13 can consume the finding without new astrology semantics. If WP13 would require activating/removing/reinterpreting the predicate, report `WP13_READY: NO` and request SME direction.

## Duplicate and deterministic loading policy

WP12 strict Yoga validation rejects duplicate IDs; first occurrence remains the identity anchor and every later occurrence receives a deterministic duplicate issue. No last-wins behavior.

Do not change the generic F3 loader's real cross-file `rajayoga_naive` duplicate in WP12. Record it as deferred legacy-loader evidence. Do not select an authoritative winner, sort/rewrite rule sources, or change Career/runtime registry behavior.

Any directory enumeration added for validation must sort directories/files lexicographically and support `.yml` and `.yaml` exactly once, but the preferred WP12 Yoga API validates an explicit source rather than broad scanning.

## Direct F2 parity

Expose the same validator for in-memory F2 nodes. Prove file-loaded and direct equivalent nodes produce:

- identical semantic normalized definitions;
- identical predicate/version/schema/capability binding;
- identical issue codes/order for equivalent defects;
- source attribution differences only in the separate source view/fingerprint;
- WP10 evaluation of a validated definition yields the same canonical result/tree as evaluation of the equivalent valid raw node.

Validation itself must not evaluate, prepare state, touch cache, call producers, or perform astrology logic.

## Error and bypass behavior

- Strict API callers receive the full typed validation outcome.
- A bypassed invalid raw node passed directly to WP10 remains protected by WP10's typed runtime boundary; it never becomes ordinary false.
- Unknown definitions must never be adapted to a legacy helper.
- Do not log/print raw exceptions or silently return an empty rule set.
- Do not alter legacy F3 behavior in WP12; document it as an explicit isolated bypass for later WP15/WP16 work.

## Tests first

Add focused tests before production changes. Cover at least:

### Models/serialization

- exact field inventories/enums/invariants;
- deep immutability and caller mutation isolation;
- safe issue detail restrictions;
- exact logical/source projections, bytes, hashes, and round trips where applicable;
- mapping insertion-order and independent-object equivalence;
- source identity inclusion/exclusion policy.

### Registry/binding

- ready finalized registry prerequisite;
- unready/incomplete synthetic registry error;
- six exposed IDs/five canonical bindings;
- Aspect alias canonicalization;
- predicate version and ordered capability requirement binding;
- unknown ID and `HOUSE_LORDS_COMBINATION` typed definition errors;
- no registry/catalog mutation/import-order leakage.

### Structure/operators

- valid nested AND/OR/NOT and bare leaf;
- case/trim behavior;
- empty AND/OR, NOT arity, missing/null/non-list children;
- leaf/logical conflicting fields, unknown fields, alternate formats;
- nonmapping/null nodes, cycles, depth 64/65, nodes 4096/4097;
- deterministic preorder issue ordering and stable paths.

### Parameters/capabilities

- valid normalized parameters for every canonical definition;
- complete representative invalid categories per WP05;
- multiple leaf issues retain deterministic order;
- no node-declared version/capability override;
- static catalog compatibility versus no chart inspection;
- normalized definition contains canonical values only.

### Yoga strict loading

- current valid Yoga records preserve source order and F1 wrapper syntax;
- current file produces the exact known `HOUSE_LORDS_COMBINATION` issue and no unexpected issues;
- duplicate Yoga rule IDs rejected with no registry mutation;
- missing required top-level fields, bad ID/conditions/root/record types;
- missing/unreadable/malformed YAML safe issues;
- explicit path independent of CWD;
- no silent skip/last-wins/stale registry reference;
- active legacy Yoga path remains unchanged.

### F2/evaluator parity

- direct and file-equivalent semantic bytes/hash;
- valid normalized definition evaluates through WP10/WP11 identically to equivalent raw node;
- invalid bypass remains typed failure;
- validation does not execute predicates, mutate cache, prepare state, call producers, or access time/random/network/environment.

### Compatibility

- no rule/YAML modifications;
- active Yoga firing/order/evidence/public projection unchanged;
- Career/F3/runtime behavior unchanged;
- registry inventory, canonical handlers, WP09 cache, WP10 conditions unchanged;
- rule lint and approved snapshots unchanged.

Do not weaken or delete existing tests and never update the approved snapshot.

## Validation gates

Run in both locked Python 3.14 and 3.11 lanes with bytecode/cache isolation and unique ignored temporary paths:

1. WP12 validation/model/Yoga-loader focused tests.
2. WP02–WP11 focused modules.
3. All `tests/rules` plus relevant Yoga loader tests.
4. WP01 predicate/Yoga/Career characterization.
5. Targeted loader/evaluator/cache/condition/predicate/Yoga/Career/runtime/writer/linter/determinism/snapshot regressions.
6. Exact full collection comparison and node-ID SHA-256.
7. Complete suite twice from fresh processes per lane.
8. Yoga normal/reverse/A/B/C permutations.
9. Both existing loader-trigger orders.
10. Rule lint proving all five supported `.yml`/`.yaml` files, including `yogas.yaml`, are inspected exactly once.
11. Strict approved-snapshot comparison twice per lane using temporary output and no update mode.
12. Fresh-process/cross-version semantic/source definition bytes/hashes, exact current Yoga validation issue projection, and F2 parity probe.
13. `git diff --check` and scoped artifact/status checks.

Record exact commands, versions, counts, node-ID hash, definition bytes/hashes, issue codes/paths/order, current Yoga strict-validation disposition, and compatibility evidence. Protected behavior differences are blockers.

## Required completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP12/WP12.md`

The report must include:

1. `VERDICT: COMPLETE` or `VERDICT: BLOCKED`;
2. `WP13_READY: YES` or `WP13_READY: NO`;
3. actual model/reasoning used;
4. prerequisite/baseline evidence;
5. exact files changed and APIs;
6. accepted/rejected F1/F2/F3/F4–F6 format table;
7. exact model field inventories/invariants;
8. registry bootstrap/readiness policy;
9. structural/operator/depth/node/cycle validation policy;
10. predicate/alias/version/parameter/capability binding policy;
11. normalized-definition and semantic/source fingerprint inclusion/exclusion tables;
12. exact issue code/message/path/order/source-attribution contract;
13. Yoga strict loader duplicate/parse/aggregation/no-mutation behavior;
14. exact `HOUSE_LORDS_COMBINATION` finding and WP13 implication;
15. direct F2/file parity and WP10 evaluation evidence;
16. explicit F3/Career and future-DSL deferrals;
17. test-to-requirement traceability;
18. exact dual-lane commands/counts and collection hash;
19. fresh-process/cross-version definition/issue bytes/hashes;
20. Yoga/loader/lint/Career/snapshot/artifact compatibility evidence;
21. explicit proof WP13 was not started.

## Definition of done

WP12 is complete only when:

- WP11 remains complete and reproducible;
- F1 Yoga and F2 direct nodes share one deterministic immutable definition validator;
- every valid leaf is bound to canonical registry identity/version, WP05 normalized parameters, and WP06 capability requirements;
- malformed/unknown/unsafe definitions produce typed stable issues and never factual false;
- current valid syntax/order is preserved without introducing future DSL/AST/compiler behavior;
- strict Yoga validation aggregates safe source-attributed issues, rejects duplicates, and never mutates registries;
- `HOUSE_LORDS_COMBINATION` is reported truthfully without activation/removal/rewrite or current runtime redirection;
- F3 Career/runtime remains explicit temporary compatibility;
- active Yoga/Career/rules/public output/CI/dependencies/snapshots remain unchanged;
- all dual-lane, determinism, compatibility, lint, snapshot, and artifact gates pass;
- the report records `VERDICT: COMPLETE` and a justified WP13 readiness decision.

At the end, return a concise summary with verdict, model/reasoning used, validator/model/loader APIs, accepted formats, binding/fingerprint/error policies, current Yoga strict-validation result, dual-lane counts, cross-version hashes, compatibility/snapshot status, files changed, deferred issues, and WP13 readiness. **Do not proceed to WP13.**