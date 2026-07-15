# Prompt-01 Audit-01: Predicate Registry

## 1. Executive Summary

The repository contains **one actual predicate registry**, `PREDICATE_REGISTRY`, and **two hard-coded predicate-like dispatch mechanisms** that bypass it. The central registry contains six IDs backed by five unique handlers when `systems.Parasara.engine.rules.predicates` has been imported: `ASPECT`, `ASPECT_EXISTS`, `FUNCTIONAL_ROLE`, `HOUSE_OCCUPANT`, `PLANET_EXALTED`, and `PLANET_IN_HOUSE`. `ASPECT` and `ASPECT_EXISTS` are implicit aliases for the same function.

The registry is a process-global mutable `dict[str, callable]`. Registration uppercases IDs, preserves surrounding whitespace, stores no metadata other than the normalized dictionary key, silently overwrites duplicates, and accepts blank IDs and non-callable values. It has no version model, parameter schemas, capability declarations, deprecation data, system scope, deterministic enumeration API, or isolation facility. Availability depends on importing the predicate-definition module for decorator side effects.

The active Yoga path imports the definition module explicitly and resolves condition leaves through the central evaluator. The legacy rule runtime used by the Career interpreter instead dispatches predicate-like rule types through `if`/`elif` branches. A second, currently uncalled Yoga-local tuple evaluator remains in the source. Rule loaders do not validate condition types against `PREDICATE_REGISTRY`; consequently, `HOUSE_LORDS_COMBINATION` in the active Yoga YAML resolves as an unknown predicate even though a dormant Yoga-local implementation exists.

The current design does not comply with Prompt-01 section 15. The numbered findings comprise **6 P0, 4 P1, 2 P2, and 0 P3** items. This audit made no production, test, rule-data, or snapshot changes.

## 2. Audit Scope and Method

Authoritative inputs reviewed:

- `Documentation/AI-Prompt/Jyothishyam Master Architecture Specification v1.0.docx`, especially sections 19-25 (predicate philosophy, contract, central registration, naming, composition, and caching) and section 34 (rule validation).
- `Documentation/AI-Prompt/Prompt-01.docx`, especially sections 3, 10-19, 26-31, 35-37, and 40. Section 15 supplies the required registry metadata and rejection behavior; sections 27-29 prohibit active bypass and tuple paths.

Repository-wide searches covered Python, tests, YAML/YML, JSON, scripts, and Markdown. Searches included registry/decorator names, callable dictionaries, predicate evaluators, predicate imports, condition types, runtime dispatch, dynamic test registration, and registry-related test assertions. Caller searches confirmed the active and dormant paths rather than assuming functions were unused.

Safe empirical checks were run in isolated Python processes for uppercase/whitespace normalization, duplicate replacement, blank IDs, and non-callable handlers. Imported-registry inspection and targeted pytest execution could not run in the default interpreter because project dependencies are unavailable (`pydantic` and `pytest`, respectively); static import/decorator evidence is therefore used where noted. No virtual-environment Python executable exists under the repository's `jyothishyam_env/Scripts` directory.

## 3. Registry Mechanisms Discovered

### Registry inventory

| Registry | File | Symbol | Registration API | Storage Type | Stored Value | Import/Initialization | Duplicate Behavior | Alias Support | Deterministic | Tests |
|---|---|---|---|---|---|---|---|---|---|---|
| Central predicate registry | `systems/Parasara/engine/rules/engine.py:21-32` | `PREDICATE_REGISTRY`; `register_predicate` | `@register_predicate(name)` | Process-global mutable `dict[str, Callable]` | Handler function only | Empty when `engine.py` loads; decorators execute only when `rules/predicates.py` is imported | Silent last-registration-wins replacement at normalized key | No alias model; stacked decorators register two keys for one handler | Fixed-module registration is repeatable, but no canonical enumeration contract; availability/winner depends on imports | `tests/rules/test_predicate_result.py:39-55` tests one dynamic registration and manual cleanup; no registry-contract tests |
| Legacy runtime dispatch (equivalent, not a registry) | `systems/Parasara/engine/rules/runtime.py:10-108,159-236` | `in_sign`, `in_house`, `lord_of_house`, `is_exalted`, `evaluate_rule`, `evaluate_rule_with_score` | None; edit `if`/`elif` code | Hard-coded branches | Direct function/branch logic returning `bool` or dictionaries | Imported by callers; rule registry is lazily loaded separately | Not applicable; overlapping branch semantics can coexist | Exact lowercase string alternatives in branch conditions only | Branch order is fixed, but behavior is outside the central versioned predicate contract | `systems/Parasara/tests/test_rule_runtime.py:12-33`; merge behavior at `test_rule_runtime_merge.py:9-19` |
| Yoga-local tuple dispatch (equivalent, presently dormant) | `systems/Parasara/engine/enrichments/yoga_engine.py:22-125` | `_eval_condition` and four `_eval_*` helpers | None; edit `if`/`elif` code | Hard-coded branches | Local functions returning `(bool, dict)` | Defined when Yoga engine imports; repository caller search finds only self-recursion/helper calls, while active evaluation uses central `evaluate_condition` at lines 150-156 | Not applicable | `ASPECT` only; no `ASPECT_EXISTS` alternate | Branch order fixed, but unordered `set` conversion affects some evidence ordering | No direct tests of these helpers |

Only the first row is a registry. No separate Jaimini, Tajaka, KP, plugin, fixture-only, or other system-specific predicate registry was found. `RULE_REGISTRY` in `systems/Parasara/engine/rules/loader.py:5` stores rule dictionaries, not predicate handlers, and is not counted as a predicate registry.

### Central registrations

All production decorator uses are in `systems/Parasara/engine/rules/predicates.py`:

| Registered ID | Handler | Evidence |
|---|---|---|
| `ASPECT_EXISTS` | `aspect_exists` | `predicates.py:12-14` |
| `ASPECT` | `aspect_exists` | `predicates.py:12-14`; stacked alias |
| `PLANET_IN_HOUSE` | `planet_in_house` | `predicates.py:50-57` |
| `HOUSE_OCCUPANT` | `house_occupant` | `predicates.py:60-67` |
| `FUNCTIONAL_ROLE` | `functional_role` | `predicates.py:70-82` |
| `PLANET_EXALTED` | `planet_exalted` | `predicates.py:85-99` |

`tests/rules/test_predicate_result.py:43-55` dynamically adds `RAISE_TEST` to the same production registry and removes it manually. It is not a persistent production registration.

## 4. Registry Initialization and Import Order

`PREDICATE_REGISTRY` is initialized empty at module import (`engine.py:21-22`). `register_predicate` mutates it during decorator execution (`engine.py:28-32`). Neither `systems/Parasara/engine/__init__.py` nor a rules-package initializer imports the definitions; in fact, no `systems/Parasara/engine/rules/__init__.py` exists.

Confirmed initialization paths are:

- `systems/Parasara/engine/enrichments/yoga_engine.py:6-7` imports `evaluate_condition` and then imports `systems.Parasara.engine.rules.predicates` specifically for registration side effects. The active Yoga evaluator subsequently calls the central evaluator at lines 150-156.
- `tests/rules/test_predicate_result.py:5-6` follows the same explicit pattern.
- Direct consumers of `engine.evaluate_predicate` that do not first import `predicates.py` see an empty registry and receive an unknown-predicate result.

Python module caching makes repeated imports of `predicates.py` in the same process no-ops unless reloaded. Registration order in the current definition module is source/decorator order and thus repeatable. However, the winner for duplicate normalized IDs is whichever decorator executes last, so duplicate behavior is import-order dependent. Registry availability is also import-path dependent. There is no explicit bootstrap, freeze/finalize phase, or registry readiness check.

The legacy runtime is independently initialized. `runtime.py:124-150` lazily loads `RULE_REGISTRY`; `runtime.py:272-279` also attempts best-effort import-time loading. Neither path imports or validates the predicate registry.

## 5. Registration and Storage Behavior

`register_predicate(name)` returns a decorator and assigns `PREDICATE_REGISTRY[name.upper()] = fn` (`engine.py:28-32`). Observed and implied behavior:

- **Storage:** only the uppercase key and handler object are stored. The declared spelling and all metadata are discarded.
- **Callability:** the decorator annotation suggests a callable but performs no runtime check. An isolated check successfully registered integer `42`.
- **Missing/blank ID:** no argument default exists, so omitting the positional argument raises Python `TypeError`; however, `''` is accepted and becomes the empty key. `None` fails incidentally at `.upper()` with `AttributeError`, not a deliberate validation error.
- **Whitespace:** no trimming occurs. An isolated registration of `' mixedCase '` produced key `' MIXEDCASE '`, distinct from `MIXEDCASE`.
- **Versions:** the API accepts no version and validates none. Missing and invalid versions are therefore indistinguishable because versions are not represented.
- **Metadata:** no description, schema, capabilities, cache policy, determinism flag, cost, scope, deprecation, or replacement is retained.
- **Dynamic registration:** any runtime or test code can add, replace, or remove entries by decorator or direct dictionary mutation.

The evaluator uppercases lookup names at `engine.py:54-60` but likewise does not strip whitespace. It computes the cache key before lookup at lines 54-59. A non-callable stored value is truthy and will be invoked at line 79; the resulting `TypeError` is caught and converted into a predicate error at lines 119-132 rather than rejected during registration.

## 6. Duplicate IDs, Aliases, and Lookup Behavior

### Duplicates

Dictionary assignment at `engine.py:30` silently replaces an existing handler. Isolated checks confirmed last-registration-wins behavior. Compatibility is never compared, no warning/error is emitted, and the overwritten registration is not retained for audit. Replacing an existing dictionary value does not move its insertion position, so enumeration order does not reveal which registration won.

### Aliases and case sensitivity

There is no typed alias or canonical-ID concept. `ASPECT` and `ASPECT_EXISTS` are produced by stacking two decorators on `aspect_exists` (`predicates.py:12-14`). Both keys point to the same callable, but the function always constructs `PredicateResult(predicate_id='ASPECT_EXISTS')` (`predicates.py:38-46`). Therefore, evaluating the registered ID `ASPECT` returns a result identifying a different predicate ID. Alias provenance, deprecation, and replacement cannot be enumerated.

Registration and lookup are case-insensitive only through `str.upper()` (`engine.py:30,44,58`). Whitespace and other Unicode normalization are not performed. Runtime legacy rule types are instead exact lowercase comparisons (`runtime.py:90-108,168-236`), while Yoga condition types are uppercased by the central evaluator (`engine.py:137-162`). These differing normalization policies are a compatibility risk.

### Unknown lookup

Missing keys produce `PredicateResult(matched=False)` with evidence `{'reason': 'unknown_predicate', 'predicate': pname}`, an empty error list, and no explicit status (`engine.py:62-77`). The result is cached. Unknown registration is therefore represented as a factual non-match rather than a typed configuration/validation error.

## 7. Current Metadata Assessment

The registry value type is a handler only (`engine.py:21-22`). The dictionary key partially represents `predicate_id`; no other Prompt-01 registration metadata is stored. Function names, annotations, comments, implementation behavior, file location, and the `PredicateResult.predicate_id` field are not registry metadata and were not credited as such.

The current `PredicateResult` at `engine.py:8-18` has `predicate_id` but no `predicate_version`. Individual handlers supply a result ID (`predicates.py:38-99`), but the evaluator does not reconcile it with the lookup key. Prompt-01 registration metadata is not consumed by caching, evaluation, rule loading, or validation because it does not exist.

## 8. Prompt-01 Metadata Compliance Matrix

| Metadata Field | Status | Current Evidence | Gap | Affected Files | Required Prompt-01 Change | Priority |
|---|---|---|---|---|---|---|
| `predicate_id` | PARTIAL | Dictionary key from `name.upper()` at `engine.py:28-30`; result field at `engine.py:10-13` | No metadata object, blank/whitespace accepted, aliases not canonicalized, handler result ID can disagree | `engine.py`; `predicates.py` | Define validated canonical ID on each registration and enforce result identity/alias policy | P0 |
| `predicate_version` | MISSING | No registry field or decorator argument; `PredicateResult` fields at `engine.py:10-18` omit it | Cannot validate registration or isolate cache by implementation version | `engine.py`; `predicates.py` | Require a valid explicit version and include it in result/cache identity | P0 |
| `description` | MISSING | Registry stores only callable at `engine.py:22,30` | No discoverable predicate description | `engine.py`; `predicates.py` | Add validated description metadata | P1 |
| `parameter_schema` | MISSING | Handlers read unvalidated dictionaries, e.g. `predicates.py:50-99` | Load/evaluation cannot reject missing, unknown, or invalid parameters from registry data | `engine.py`; `predicates.py` | Require and expose a schema for every predicate | P0 |
| `required_capabilities` | MISSING | `ASPECT_EXISTS` directly reads enrichments at `predicates.py:16-17`; no registry declaration | Missing capability cannot be prechecked or distinguished from false | `engine.py`; `predicates.py` | Declare and validate capability requirements | P0 |
| `cacheable` | MISSING | Evaluator caches all outcomes unconditionally at `engine.py:54-57,75-76,113-131` | No per-predicate opt-out or policy validation | `engine.py`; `predicates.py` | Add a required boolean and honor it in evaluator/cache | P1 |
| `deterministic` | MISSING | No registration field; unconditional cache assumes suitability | Determinism is neither declared nor enforced | `engine.py`; `predicates.py` | Add required declaration and reject unsafe caching | P1 |
| `cost_class` | MISSING | No field; timing is measured at `engine.py:61-130` but not classified | No scheduling/timeout cost metadata | `engine.py`; `predicates.py` | Add validated cost class | P1 |
| `system_scope` | MISSING | Implementations reside under Parasara, but scope is not stored | Cannot safely support shared versus plugin-specific predicate identities | `engine.py`; `predicates.py` | Add explicit validated system/plugin scope | P1 |
| `deprecated` | MISSING | No field or alias lifecycle model | Consumers cannot discover deprecated IDs | `engine.py`; `predicates.py` | Add a required/defaulted deprecation flag | P1 |
| `replacement_predicate` | MISSING | No field; stacked `ASPECT` alias has no relationship metadata | No validated migration target for deprecated/alias IDs | `engine.py`; `predicates.py` | Add optional validated replacement reference and cycle/existence checks | P1 |

Status totals: 1 PARTIAL, 10 MISSING, 0 IMPLEMENTED, 0 NONCOMPLIANT, and 0 UNKNOWN. “MISSING” means no exact registration field exists; behavior elsewhere was not treated as equivalent metadata.

## 9. Determinism and Test-Isolation Assessment

Registration from the single production module is deterministic under a fresh interpreter because decorator execution and Python dictionary insertion are ordered. That is an implementation consequence, not a registry contract: there is no sorted/canonical enumeration API, immutable snapshot, explicit initialization sequence, or duplicate rejection. Dynamic imports and registrations change both membership and potentially handlers. `dict` enumeration follows insertion order, while duplicate replacement preserves the old key position.

The registry and `_CACHE` are process-global mutable dictionaries (`engine.py:22-25`). `clear_cache` clears only `_CACHE` (`engine.py:35-36`); there is no registry reset/snapshot/context manager. The dynamic `RAISE_TEST` test mutates the production registry and manually pops the key after assertions (`tests/rules/test_predicate_result.py:39-55`). If setup, evaluation, or an assertion fails before line 55, the registration leaks to later tests in the same process. A colliding test ID can silently replace a production handler with no restoration. Cache entries for a dynamically replaced predicate are not invalidated by registration, and the cache key lacks handler or predicate version (`engine.py:39-44`).

No test checks deterministic registration/enumeration, duplicate behavior, alias identity, normalization, blank/missing IDs, invalid handlers, metadata validation, registry reset, import bootstrapping, cross-test leakage, or cache invalidation after re-registration.

## 10. Rule Loader and Validator Interaction

The generic rule loader creates a separate `RULE_REGISTRY` and loads list-shaped YAML documents (`systems/Parasara/engine/rules/loader.py:5-36`). It checks only for truthy rule IDs, silently overwrites duplicate IDs, and swallows load/parse exceptions. `register_rule` likewise stores truthy IDs without condition validation (`loader.py:39-46`). It never imports, enumerates, or queries `PREDICATE_REGISTRY`.

The Yoga loader validates only the presence of its rule-level `REQUIRED_FIELDS` (`systems/Parasara/engine/rules/yoga_loader.py:7,21-24`). `load_yoga_rules` registers valid rule dictionaries but catches and skips exceptions (`yoga_loader.py:27-45`). It does not recursively validate logical operators, predicate IDs, parameters, aliases, versions, or required capabilities against the predicate registry.

Concrete consequence: `systems/Parasara/rules/parashara/v1/yogas.yaml:41-44` uses `HOUSE_LORDS_COMBINATION`. No central decorator registers that ID. The active Yoga runtime calls central `evaluate_condition` (`yoga_engine.py:150-156`), so this leaf becomes the unknown-predicate false result described at `engine.py:62-77`. A matching implementation exists only in the uncalled Yoga-local helper at `yoga_engine.py:70-91,120-121`. Existing Yoga tests assert loaded/matched result IDs and basic evidence/trace presence, not that this condition resolves correctly (`tests/enrichments/test_yoga_engine_rule_driven.py:17-37`).

The Career interpreter uses the separate runtime dispatcher through `runtime.evaluate_rule_with_score` and fallback `runtime.evaluate_rule` (`systems/Parasara/engine/interpreters/career.py:48-52`). Thus rule-loader metadata and domain execution can bypass the central predicate registry entirely.

## 11. Existing Tests and Coverage Gaps

Existing central-evaluator coverage is concentrated in `tests/rules/test_predicate_result.py`:

- lines 14-27: registered `PLANET_IN_HOUSE` and cold/warm cache behavior;
- lines 30-36: unmatched `PLANET_EXALTED`;
- lines 39-55: dynamic exception handler registration, structured failure, and manual cleanup;
- lines 58-64: leaf condition returns `PredicateResult`;
- lines 67-74: basic dataclass/JSON serializability.

Integration coverage includes rule loading (`tests/enrichments/test_yoga_loader.py:5-26`), Yoga result presence (`test_yoga_engine_rule_driven.py:17-37`), legacy primitives (`systems/Parasara/tests/test_rule_runtime.py:12-33`), and rule-registry merge behavior (`test_rule_runtime_merge.py:9-19`). These tests do not establish Prompt-01 registry compliance.

Coverage gaps:

- no direct inventory assertion for all six production IDs or five handlers;
- no bootstrap/import-order test;
- no duplicate-compatible/incompatible registration tests;
- no alias canonical-ID or deprecation tests;
- no case/whitespace/Unicode normalization tests;
- no missing, blank, or malformed ID tests;
- no non-callable handler test;
- no version or metadata validation tests;
- no registry enumeration/freeze/reset/isolation tests;
- no test that rule loading rejects unknown predicates or bad parameters;
- no test for `HOUSE_LORDS_COMBINATION` through the active central path;
- no test preventing legacy runtime/Yoga-local bypasses;
- no cache invalidation test after handler replacement;
- no plugin/system-scope collision test.

Targeted tests were attempted but not executed: `python -m pytest tests/rules/test_predicate_result.py tests/enrichments/test_yoga_loader.py tests/enrichments/test_yoga_engine_rule_driven.py -q` failed before collection because the default Python installation has no `pytest`. Importing the full predicate module separately failed because it has no `pydantic`. These are environment blockers to runtime confirmation, not evidence of test failures.

## 12. Findings and Migration Risks

The following countable findings define the priority totals reported in the executive summary.

1. **P0 — Registration accepts invalid identities and handlers.** `register_predicate` performs only `.upper()` and dictionary assignment (`engine.py:28-32`). Blank and whitespace-surrounded IDs and non-callable values are accepted; missing/invalid versions and metadata cannot be validated because the API has no such fields.
2. **P0 — Duplicate incompatible registrations silently replace prior handlers.** Last-registration-wins behavior at `engine.py:30` loses provenance and makes semantics import-order dependent, directly violating Prompt-01 section 15.
3. **P0 — Predicate availability depends on import side effects.** The registry begins empty (`engine.py:22`) and only Yoga/tests explicitly import definitions (`yoga_engine.py:6-7`; `test_predicate_result.py:5-6`). There is no authoritative bootstrap or readiness check.
4. **P0 — Rule loaders do not validate against the registry.** Neither `loader.py:8-46` nor `yoga_loader.py:21-45` checks condition references. Active YAML contains unregistered `HOUSE_LORDS_COMBINATION` (`yogas.yaml:41-44`), which is silently evaluated as false/unknown.
5. **P0 — Alias identity is inconsistent and ungoverned.** Stacked decorators map `ASPECT` and `ASPECT_EXISTS` to one handler (`predicates.py:12-14`), but it always returns ID `ASPECT_EXISTS` (`predicates.py:38-46`). No canonical alias, deprecation, or replacement metadata exists.
6. **P0 — Active predicate-like behavior is fragmented outside the registry.** Career executes the hard-coded legacy runtime (`career.py:48-52`; `runtime.py:76-108,159-236`), while obsolete Yoga tuple dispatch remains at `yoga_engine.py:22-125`. Prompt-01 cannot safely claim every predicate/caller migrated while these equivalent paths are unclassified.
7. **P1 — Prompt-01 registration metadata is absent.** Aside from the partial ID key, all required fields are missing from the handler-only storage (`engine.py:21-30`), preventing discovery, validation, versioning, capability checks, cache policy, and lifecycle governance.
8. **P1 — Unknown predicates are converted to cached factual non-matches.** `engine.py:62-77` emits no typed error/status, allowing configuration defects to be mistaken for astrological false results.
9. **P1 — Identifier normalization is incomplete and inconsistent.** Central registration/lookup uppercases without trimming (`engine.py:30,44,58`); legacy runtime uses exact lowercase branch strings (`runtime.py:90-108,168-236`). IDs that look equivalent to users can resolve differently.
10. **P1 — Tests do not protect the required registry contract.** Current tests omit duplicate, invalid handler/ID, metadata, alias, loader-validation, bootstrap, enumeration, and isolation requirements; see section 11.
11. **P2 — Test-time registrations can leak and overwrite production handlers.** The global registry has no isolation API, and the only dynamic test relies on cleanup after assertions (`test_predicate_result.py:39-55`). Cache state is independent and can retain results across handler replacement.
12. **P2 — Enumeration is only incidentally deterministic.** Dictionary/source order is stable in the current module, but no canonical enumeration API, sort policy, freeze phase, metadata snapshot, or cross-plugin ordering contract exists (`engine.py:22,28-32`).

Key migration risks are semantic collisions when aliases become first-class, cached results surviving handler/version changes, loaders beginning to reject currently accepted YAML, import-bootstrap changes exposing hidden call paths, and accidental conflation of legacy rule types with centrally registered factual predicates. Prompt-01 implementation should inventory and explicitly map these paths before changing public behavior; this audit does not prescribe or implement the migration.

## 13. Audit-1 Conclusion

Audit-1 is complete. One true predicate registry and two equivalent hard-coded dispatch mechanisms were discovered. The central registry is handler-only, mutable, import-side-effect initialized, silently overwriting, minimally normalized, and disconnected from rule validation. It provides none of the Prompt-01 metadata contract beyond a partial dictionary-key representation of `predicate_id`.

No unresolved question blocks the audit report. Before Prompt-01 implementation, architecture ownership must decide whether the legacy runtime rule types and dormant Yoga-local evaluators are to be migrated into the central predicate model or explicitly retired; that is a migration decision, not an Audit-1 blocker.
