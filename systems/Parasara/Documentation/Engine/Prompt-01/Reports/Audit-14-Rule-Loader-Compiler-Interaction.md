# Prompt-01 Audit-14: Rule Loader and Compiler Interaction

## 1. Executive Summary

The repository has three loader functions, one narrow validator, no rule linter, and no AST/compiler component. Two active rule systems—Yoga and legacy M1/Career—carry mutable raw dictionaries to runtime. There are zero generic or specialized fully validated paths and three active raw-runtime paths.

Neither loader validates predicate IDs, predicate parameters, predicate versions, capabilities, logical operators, condition arity, or duplicates. Yoga validates only presence of ten top-level rule fields. Unknown predicates and operators reach runtime and become ordinary unmatched results; the active `HOUSE_LORDS_COMBINATION` Yoga leaf demonstrates this defect. The generic loader silently overwrites duplicates, and `rajayoga_naive` is actually duplicated between `yogas.yaml` and `m1_rules.yaml`.

Prompt-01 requires a shared validated predicate boundary and typed definition failures, but does not require the future grammar, canonical AST, macros/references, or optimized execution plans. Findings total **7 P0, 7 P1, 4 P2, and 2 P3**. No corrections were implemented.

## 2. Audit Scope and Method

The audit read the Master Architecture, Prompt-01, Audits 1–13, all rule sources, loaders, registries, evaluators, Yoga/Career callers, schemas, tests, tools, Makefiles, requirements, and GitHub workflows. Searches covered every requested parser/loader/validator/compiler/linter/identity/version/capability/operator term.

An isolated non-writing probe with a stubbed `yaml` module confirmed rule duplicate last-wins and `RULE_REGISTRY` object rebinding. Targeted pytest could not run because `pytest` is absent; ordinary YAML parser execution could not run because `yaml` is absent. Static code and source data provide sufficient audit evidence.

## 3. Reconciliation with Audits 1–13

Audit-1 found the import-side-effect predicate registry and loader disconnection. Audit-2 supplies six registered IDs and the unregistered active Yoga ID. Audit-4 proves the active Yoga and Career caller chains. Audit-7 establishes absent parameter schemas and invalid-to-unmatched behavior; Audit-8 establishes no static/runtime capability distinction. Audits 9–11 add state/cache/version identity risks. Audit-12 counts four unknown-predicate-to-unmatched and two unknown-operator-to-unmatched evaluator paths. Audit-13 establishes six formats, zero canonical formats, and zero loader condition transformations.

Audit-14 confirms all of these and adds actual cross-file duplicate-rule evidence, missing CI enforcement/dependency declaration, unsorted traversal, and a stale imported-registry reference hazard. All thirteen expected reports are present.

## 4. Loader, Validator and Compiler Inventory

| Component | File | Symbol | Category | Rule System | Input | Output | Predicate Validation | Parameter Validation | Version Validation | Capability Validation | Operator Validation | Duplicate Validation | Registry Dependency | Callers | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Generic directory loader | `systems/Parasara/engine/rules/loader.py:8-36` | `load_rules_from_dir` | PRODUCTION_LOADER | M1/all YAML | directory of YAML/YML | mutable `dict[id, rule dict]` | None | None | None | None | None | silent last wins | writes `RULE_REGISTRY`; no predicate registry | runtime, tests/tools | merge indirect |
| Rule registry sink | `engine/rules/loader.py:39-46` | `get_rule`, `register_rule` | RUNTIME_NORMALIZER | shared | rule dict/ID | stored/raw rule | None | None | None | None | None | silent last wins | mutable global | Yoga loader/runtime/tests | registration presence |
| Yoga YAML parser | `engine/rules/yoga_loader.py:10-18` | `_load_yaml` | YOGA_SPECIFIC_LOADER | Yoga | one YAML path | list of raw dicts or `[]` | None | None | None | None | None | None | None | Yoga loader | indirect |
| Yoga rule validator | `engine/rules/yoga_loader.py:21-24` | `validate_yoga_rule` | PRODUCTION_VALIDATOR | Yoga | raw rule dict | `None` or `ValueError` | None | None | presence only, not value | None | None | None | None | Yoga loader/test | missing top-level fields |
| Yoga orchestration loader | `engine/rules/yoga_loader.py:27-45` | `load_yoga_rules` | YOGA_SPECIFIC_LOADER | Yoga | default/CWD rule path | validated-top-level raw dict list; shared registry | None | None | top-level presence only | None | None | silent registry overwrite | shared rule registry; not predicate registry | Yoga runtime/tests | load/registration |

Loaders discovered: **3** (`load_rules_from_dir`, `_load_yaml`, `load_yoga_rules`); validators: **1**; CI rule linters: **0**; compiler/AST components: **0**. `register_rule` is inventoried as a registry boundary but not counted as a loader.

## 5. Rule-Source Inventory

Four production YAML/YML files can enter the generic registry: `yogas.yaml`, `m1_rules.yaml`, `primitives.yml`, and `derived_rules.yml`. Yoga's specialized loader reads only `yogas.yaml`. `macros.yaml` is comments only; `calibration.json` is not a rule source and JSON files are not scanned.

Yoga rules use `conditions -> type/children/type/params`, predicate IDs `ASPECT`, `FUNCTIONAL_ROLE`, `HOUSE_OCCUPANT`, and unregistered `HOUSE_LORDS_COMBINATION` (`yogas.yaml:11-74`). M1 files use flat hard-coded runtime types and optional top-level arguments (`m1_rules.yaml:4-42`; `primitives.yml:1-16`; `derived_rules.yml:1-14`). Career also constructs flat rules in Python (`career.py:33-52`). Tests and coverage/artifact tools load or construct the same raw forms.

No rule source has a condition schema, rule-set selection contract, predicate version, capability declaration, or compiler version. Yoga rule-level versions are present but unchecked; several flat rules omit versions. Test coverage asserts loading and selected runtime outputs, not source contracts.

## 6. End-to-End Rule Paths

| Rule System | Source | Parser | Loader | Normalizer | Validator | Compiler/Representation | Evaluator | Raw Dictionaries Reach Runtime | Validation Gaps | Active Evidence | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Yoga | `yogas.yaml` | `yaml.safe_load` | specialized Yoga loader/registry | none; caller unwraps `conditions` | top-level required fields only | mutable rule/condition dict | generic condition/predicate evaluators | Yes | predicates/params/versions/capabilities/operators/duplicates | `evaluate_yoga_rules:128-179` | P0 |
| Legacy M1 YAML | three YAML/YML files plus Yoga file via directory scan | `yaml.safe_load` | generic directory loader | `_source_file` only; runtime shallow merge | truthy ID only | mutable rule dict | hard-coded runtime | Yes | all predicate/condition contracts | runtime:124-269 | P0 |
| Career Python | inline candidate dicts | none | none | registry merge by runtime | none | mutable dict | scored runtime/fallback | Yes | every validation stage | career:33-64 | P0 |
| Direct condition API | inline test/client dict | none | none | runtime `type.upper`/falsey collapse | none | mutable dict | generic evaluator | Yes | every validation stage | predicate-result test:58-64 | P1 |

Active rule systems: **2**. Fully `GENERIC_VALIDATED_PATH`: **0**; fully `SPECIALIZED_VALIDATED_PATH`: **0**; active `RAW_RUNTIME_PATH`: **3**. Yoga is partly validated at rule metadata level but is raw/unvalidated at the condition boundary. The direct condition API is a `TEST_ONLY_PATH` in repository evidence and excluded from the active raw-path count.

At no boundary are raw dictionaries replaced by immutable validated models. Source line/column is lost immediately; generic loading adds only `_source_file`. Declared list/child order is retained incidentally, while directory file order is unsorted. Predicate registry initialization is required only at evaluation, too late for validation.

## 7. Unknown Predicate Validation

| Path | Unknown Item | Validation Stage | Current Outcome | Runtime Reachable | Becomes Unmatched | Error Contract | Required Prompt-01 Behavior | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|
| Yoga YAML -> generic evaluator | predicate ID | NOT_VALIDATED | cached false reason | Yes | Yes | no typed error/status | reject definition before factual outcome | IN_SCOPE | P0 |
| Direct generic condition | predicate ID | RUNTIME lookup only | cached false reason | Yes | Yes | no typed error/status | typed definition error/shared validation | IN_SCOPE | P0 |
| Dormant Yoga local | condition type | NOT_VALIDATED | false tuple | dormant | Yes | evidence reason only | retire, never fallback | TEMPORARY_COMPATIBILITY | P2 |
| Legacy runtime | hard-coded rule type | RUNTIME branch | false unsupported-rule dict | Yes | Yes | evidence reason only | migrate/isolate factual boundary | IN_SCOPE | P0 |
| Generic/Yoga logical tree | unknown operator | RUNTIME fallthrough | treated as predicate then false | Yes | Yes | no typed definition error | reject supported-operator violation | IN_SCOPE | P0 |
| Yoga local logical tree | unknown operator | RUNTIME | false tuple | dormant | Yes | evidence reason only | retire | TEMPORARY_COMPATIBILITY | P2 |

Unknown-predicate-to-unmatched paths: **4**; unknown-operator-to-unmatched paths: **2**, consistent with Audit-12. Parsing/loading/linting/compilation reject none. There is no CI-only substitute.

## 8. Predicate Parameter-Schema Validation

No loader, validator, registry metadata, or runtime boundary supplies predicate-specific schemas. Required/optional keys, types, ranges, vocabularies, aliases, defaults, unknown fields, and cross-field constraints are unvalidated. Yoga forwards nested `params`; legacy runtime reads top-level fields; Career bypasses loading.

Four inventoried paths lack parameter validation: Yoga YAML, generic legacy YAML, Career Python, and the direct condition API. Invalid registered inputs can become false/error outcomes after caching as established by Audit-7. Validation is neither before nor after normalization; condition normalization itself is absent.

## 9. Predicate-Version Validation

Classification: **`UNSUPPORTED`**. Condition nodes cannot specify a predicate version; the registry stores no version; loaders never resolve or compare versions; compatibility ranges, deprecation, and replacement are absent. Rule-level `version` is merely stored when present and ignored when absent or malformed.

All four inventoried paths lack predicate-version validation. Cache identity consequently cannot distinguish handler versions (Audit-11).

## 10. Required-Capability Validation

The registry has no `required_capabilities` metadata, and loaders/validators cannot inspect it. No static system compatibility check exists. At runtime, missing chart enrichments usually become false or empty evidence rather than typed `missing_capability`, so static unsupported-system defects and chart-specific absence are conflated.

All four inventoried paths lack capability validation. Prompt-01 needs metadata and typed runtime distinction; complete compiled dependency planning belongs later.

## 11. Logical Operator Validation

Neither loader checks operator key/value, case, children type/count, empty AND/OR, NOT arity, unknown operators, depth, or cycles. Generic runtime uppercases values and supports eager AND/OR; Yoga local requires exact uppercase. Missing/null children become empty; malformed children can raise; NOT/unknown operators become predicate IDs or false tuples (Audits 12–13).

| Validation | Rule System | Parse | Load | Compile | CI | Runtime | Not Validated | Bypass Path | Current Failure | Required Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Predicate ID | Yoga/generic/direct | No | No | none | No | lookup only | Yes | every direct/raw path | unmatched | PROMPT_01_REQUIRED | P0 |
| Parameters | all | No | No | none | No | handler accidents | Yes | all four | unmatched/error | PROMPT_01_REQUIRED | P0 |
| Predicate version | all | No | No | none | No | No | Yes | all four | ignored/unsupported | PROMPT_01_REQUIRED | P0 |
| Capabilities | all | No | No | none | No | implicit reads | Yes | all four | unmatched | PROMPT_01_REQUIRED | P0 |
| Operators/arity | Yoga/direct | No | No | none | No | partial dispatch | Yes | raw nodes | unmatched/exception | PROMPT_01_REQUIRED | P0 |
| Rule metadata presence | Yoga | parser syntax only | partial | none | test only | no repeat | Partly | generic loader/Python | invalid Yoga skipped | PROMPT_01_REQUIRED | P1 |
| Rule duplicate ID | generic/Yoga | No | No | none | No | dict overwrite | Yes | register/direct load | last wins | PROMPT_01_REQUIRED | P1 |
| SME/lifecycle/provenance values | all | No | presence only for Yoga | none | No | ignored | Yes | all | unapproved rules execute | FUTURE_DSL_COMPILER_STAGE | P2 |

## 12. Duplicate Identity Handling

Generic rule IDs silently last-win at `loader.py:29-32`; Yoga IDs silently last-win through `register_rule` (`loader.py:43-46`). Predicate IDs silently last-win through decorators (`engine.py:28-31`), and aliases have no collision policy. These are **4 duplicate identity classes not rejected**. Condition IDs, references, and macro identities are not representable and are not counted.

`rajayoga_naive` occurs in both `yogas.yaml:4` and `m1_rules.yaml:20`. Which rule survives a generic directory scan depends on unsorted filesystem traversal. The isolated probe confirmed `register_rule` retains the second value. No duplicate test exists.

## 13. Registry Initialization and Import Order

Five risks are counted:

1. `PREDICATE_REGISTRY` begins empty and depends on importing `predicates.py` decorators (`engine.py:21-32`).
2. Duplicate predicate winner depends on decorator/import order.
3. Dynamic test registration mutates the production registry and can leak/overwrite.
4. `yoga_engine.py:4` imports the `RULE_REGISTRY` object directly, while `load_rules_from_dir` rebinds the module global at `loader.py:15`; Yoga can retain a stale dictionary reference. The isolated probe confirmed old and new objects diverge.
5. Runtime performs best-effort import-time and lazy rule loading (`runtime.py:124-150,272-279`) with path/order-dependent contents.

There is no explicit bootstrap, readiness/freeze phase, plugin discovery contract, or registry snapshot. Adding loader-time predicate validation without fixing initialization would make valid rules appear unknown depending on import path.

## 14. Raw Rule Evaluation Paths

Yoga evaluates `rule['conditions']` directly after top-level validation. Generic M1 YAML is stored and shallow-merged into runtime dispatch. Career constructs dictionaries and calls runtime directly. Direct `evaluate_condition` callers bypass loading. These paths skip condition normalization, predicate/parameter/version/capability/operator validation, immutable representation, and source-located errors.

Prompt-01 does not need a complete compiler to close this gap: a shared validated internal boundary can satisfy current requirements while preserving active syntax. The legacy Career path remains temporary compatibility.

## 15. AST and Compiler Status

No active grammar, AST node model, condition model, compiled rule, execution plan, bytecode, macro expansion, reference resolution, or rule linter exists. `RuleMatch` is an output model, not an AST. The Master Architecture canonical AST and archived DSL material are `DOCUMENTATION_ONLY`; `macros.yaml` is a commented placeholder.

Compiler/AST component count: **0**. Prompt-01 depends only on truthful predicate/condition validation and typed results, not implementation of future grammar, macro/reference expansion, optimizer, or full execution plan.

## 16. Yoga Loader Interaction

Yoga uses `_load_yaml`/`load_yoga_rules`, then the shared `RULE_REGISTRY`, and evaluates the raw plural-`conditions` mapping through the generic evaluator. The loader checks presence of `id`, `name`, `version`, `category`, `conditions`, `weights`, `evidence_required`, `provenance`, `sme_approved`, and `tests`, but not their types/values. Any validation error is caught and the rule is silently skipped; parse/path errors become an empty list.

Yoga differs from the generic loader by top-level presence checks and single-file selection, but shares silent duplicate registration and raw dictionaries. It explicitly imports predicates before evaluation, while the loader itself does not. The dormant local tuple evaluator is not an active fallback. Audit-15 remains responsible for broader Yoga behavior.

## 17. Domain Loader Interaction

Career has no domain-specific loader. It creates flat candidate rules in Python and calls `evaluate_rule_with_score`, which may lazily load/merge generic registry metadata; on exception it falls back to `evaluate_rule` (`career.py:33-64`). It bypasses the predicate registry, condition formats, parameter schemas, and typed results, and embeds scoring metadata beside factual arguments.

No other implemented domain rule loader was found. Tools iterate the generic registry and invoke the same runtime. Prompt-01 must isolate/migrate factual contracts without redesigning domain scoring; Audit-16 covers the latter.

## 18. Error Reporting and Source Location

Generic loading catches all file/parse/record exceptions and continues silently (`loader.py:24-35`). Yoga parsing returns `[]` on any exception; Yoga loading catches validator errors and skips the rule (`yoga_loader.py:10-18,36-44`). `validate_yoga_rule` includes only rule ID and missing top-level field names in an untyped `ValueError`.

There are no stable codes, condition paths, YAML lines/columns, predicate IDs, parameter names, suggestions, or multi-error aggregation. Generic rules gain `_source_file`; Yoga rules do not. Runtime definition defects become unmatched, while broad Career/runtime exceptions become generic false/error evidence. Raw stack traces are generally swallowed rather than exposed.

## 19. Determinism

`os.walk` directories/files are not sorted, so duplicate resolution and registry insertion order depend on filesystem enumeration (`loader.py:19-32`). Python mapping iteration then preserves that incidental order. Global registries are mutable; loader rebinding creates stale-reference risk; decorator and test import order affect predicates. Relative CWD paths affect Yoga and lazy runtime loading, while the runtime import-time path calculation is best-effort and may not identify the repository root correctly.

No parser version is pinned because PyYAML is not declared. Identical source trees are therefore not guaranteed identical registry winners/error order. Yoga UUID trace generation is downstream, but further prevents deterministic output attribution.

## 20. CI versus Runtime Enforcement

No rules-lint script, pre-commit rule check, build rule check, duplicate/version gate, predicate-reference validation, or SME approval gate exists. `.github/workflows/ci.yaml` runs pytest and coverage tooling; the snapshot workflow runs output comparison. `systems/Parasara/Makefile` validates only Surya input schema. Documentation mentions a future `tools/rules_lint.py`, but no such file/job exists.

CI-only rule validations: **0**. Runtime does not enforce any stronger policy. Moreover, PyYAML is imported by rule loaders but absent from `requirements-dev.txt`, `systems/Parasara/requirements.txt`, and `setup.py`; both CI dependency paths may lack the loader dependency unless supplied transitively.

## 21. Prompt-01 versus Future-Stage Classification

| Finding | Current Behavior | Required Outcome | Classification | Dependency | Blocking Prompt-01 | Priority | Rationale |
|---|---|---|---|---|---|---|---|
| Unknown predicates | false/unmatched | definition error, never factual false | PROMPT_01_REQUIRED | registry metadata | Yes | P0 | truthful contract |
| Parameters | unchecked | shared schema validation/typed invalid | PROMPT_01_REQUIRED | Audit-7 decisions | Yes | P0 | result correctness |
| Predicate versions | unsupported | metadata/selection sufficient for active path | PROMPT_01_REQUIRED | registry migration | Yes | P0 | cache/result identity |
| Capability distinction | conflated | static incompatibility vs runtime missing | PROMPT_01_REQUIRED | capability metadata/status | Yes | P0 | missing is not false |
| Operators/arity | unchecked | validate current supported syntax | PROMPT_01_REQUIRED | condition boundary | Yes | P0 | definition safety |
| Registry bootstrap | import side effects | deterministic ready registry | PROMPT_01_REQUIRED | registry lifecycle | Yes | P0 | validation reliability |
| Typed child results | raw/lossy | preserve PredicateResults | PROMPT_01_REQUIRED | ConditionResult | Yes | P0 | Prompt-01 acceptance |
| Active generic boundary | Career bypass | migrate/isolate facts | PROMPT_01_REQUIRED | caller adapters | Yes | P1 | one predicate contract |
| Duplicate predicate identity | silent replacement | deterministic rejection/policy | PROMPT_01_REQUIRED | registry metadata | Yes | P1 | import safety |
| Minimal condition shape validation | raw malformed nodes | shared validated model/boundary | PROMPT_01_REQUIRED | active F1/F2 | Yes | P1 | no full compiler required |
| Typed/source-attributed errors | swallowed/unmatched | stable actionable errors | PROMPT_01_REQUIRED | validation boundary | Yes | P1 | diagnosis/audit |
| Preserve F1 Yoga syntax | raw tree active | accept valid current files | TEMPORARY_COMPATIBILITY | Yoga tests | Yes | P1 | avoid rule rewrite |
| Preserve F3 Career behavior | flat runtime active | bounded adapter/migration | TEMPORARY_COMPATIBILITY | scoring snapshots | Yes | P1 | output stability |
| Yoga specialized loader | partial separate path | temporarily route through shared checks | TEMPORARY_COMPATIBILITY | loader integration | Yes | P1 | active path |
| Existing rule-file stability | mutable YAML | no broad source rewrite | TEMPORARY_COMPATIBILITY | compatibility tests | No | P2 | scope control |
| Formal grammar/canonical AST | absent | later compiler | FUTURE_DSL_COMPILER_STAGE | DSL stage | No | P2 | beyond Prompt-01 |
| Macro/reference expansion | absent | later compiler | FUTURE_DSL_COMPILER_STAGE | AST/compiler | No | P2 | no active use |
| Optimized execution plan | absent | later optimizer | FUTURE_DSL_COMPILER_STAGE | compiler | No | P2 | performance stage |
| Full governance/SME lifecycle | presence ignored | later governance enforcement | FUTURE_DSL_COMPILER_STAGE | rule governance | No | P3 | broader than predicate contract |
| JSON parity/advanced diagnostics | unsupported | later source/compiler policy | FUTURE_DSL_COMPILER_STAGE | parser/compiler | No | P3 | no active JSON rules |

Classification counts: **11 PROMPT_01_REQUIRED**, **4 TEMPORARY_COMPATIBILITY**, **5 FUTURE_DSL_COMPILER_STAGE**.

## 22. Existing Tests and Coverage Gaps

Existing tests cover valid Yoga YAML loading, registry presence, missing top-level Yoga fields, basic generic directory merge, flat runtime outcomes, and Yoga integration. They do not validate condition definitions against predicate contracts.

| Area | Missing Categories | Count | Recommended Test File |
|---|---|---:|---|
| Loading/parsing | JSON policy, malformed source, deterministic order, multiple-file contract, empty set | 5 | `tests/rules/test_rule_loading.py` |
| Predicate validation | known/unknown, registry uninitialized, alias, duplicate registration, deprecated, version mismatch | 7 | `tests/rules/test_rule_predicate_validation.py` |
| Parameter validation | missing, type, value, unknown, alias, default | 6 | `tests/rules/test_rule_parameter_validation.py` |
| Operator validation | AND, OR, NOT, unknown, arity, malformed children, depth | 7 | `tests/rules/test_rule_operator_validation.py` |
| Duplicate identity | generic rule, Yoga rule, condition, deterministic error | 4 | `tests/rules/test_rule_duplicates.py` |
| Integration | loader-to-predicate registry, CI/runtime parity, source-location errors | 3 | `tests/rules/test_rule_loader_integration.py` |

Missing loader/compiler test categories: **32**.

## 23. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Reject unknown predicates | NONCOMPLIANT | four unmatched paths | loaders/engine/runtime | shared typed definition validation | IN_SCOPE | P0 | Yes |
| Validate predicate parameters | MISSING | four unchecked paths | registry/loaders | schema validation | IN_SCOPE | P0 | Yes |
| Validate predicate version identity | MISSING | unsupported | registry/nodes/cache | active-path version metadata | IN_SCOPE | P0 | Yes |
| Distinguish capability incompatibility/absence | MISSING | no metadata/status | registry/loaders/handlers | static/runtime distinction | IN_SCOPE | P0 | Yes |
| Validate active operators/arity | MISSING | two unknown-op paths | loaders/evaluator | current-format validation | IN_SCOPE | P0 | Yes |
| Deterministic registry initialization | NONCOMPLIANT | import/rebind risks | registries/loaders | bootstrap/readiness lifecycle | IN_SCOPE | P0 | Yes |
| Preserve typed child results | NONCOMPLIANT | raw/lossy condition path | engine | typed condition boundary | IN_SCOPE | P0 | Yes |
| Central predicate boundary | NONCOMPLIANT | Career/runtime bypass | runtime/Career | migrate/isolate adapter | IN_SCOPE | P1 | Yes |
| Duplicate predicate policy | NONCOMPLIANT | last registration wins | registry | reject/explicit alias policy | IN_SCOPE | P1 | Yes |
| Minimal validated condition model | MISSING | raw dicts | loaders/evaluator | shared validated representation | IN_SCOPE | P1 | Yes |
| Typed source-attributed errors | MISSING | swallowed/unlocated | loaders/runtime | error contract/source path | IN_SCOPE | P1 | Yes |
| Preserve Yoga F1 syntax | PARTIAL | active raw files | Yoga/engine | compatibility coverage | TEMPORARY_COMPATIBILITY | P1 | Yes |
| Preserve Career F3 behavior | PARTIAL | score/output dependency | runtime/Career | bounded adapter | TEMPORARY_COMPATIBILITY | P1 | Yes |
| Route specialized Yoga loader through shared checks | MISSING | top-level only | Yoga loader | shared validation | TEMPORARY_COMPATIBILITY | P1 | Yes |
| Avoid broad rule rewrites | IMPLEMENTED | audit scope/current files untouched | rule files | preserve during migration | TEMPORARY_COMPATIBILITY | P2 | No |
| Formal grammar/AST | MISSING | documentation only | future DSL | later compiler | OUT_OF_SCOPE_FUTURE_STAGE | P2 | No |
| Macro/reference expansion | MISSING | placeholder only | future DSL | later compiler | OUT_OF_SCOPE_FUTURE_STAGE | P2 | No |
| Optimized execution plan | MISSING | absent | future compiler | later optimizer | OUT_OF_SCOPE_FUTURE_STAGE | P2 | No |
| Full governance/SME enforcement | MISSING | values ignored | loaders/governance | later governance | OUT_OF_SCOPE_FUTURE_STAGE | P3 | No |
| JSON source parity/advanced diagnostics | MISSING | YAML-only/no locations | future parser | later source policy | OUT_OF_SCOPE_FUTURE_STAGE | P3 | No |

## 24. Migration Risks and Priorities

The 20 findings total **P0=7, P1=7, P2=4, P3=2**. Highest risks are loader-time validation against an uninitialized registry, stale Yoga registry references after generic reload, changing the winner for the real `rajayoga_naive` duplicate, turning previously silent Yoga false outcomes into definition errors, and changing Career scores/public snapshots while removing raw runtime behavior.

A Prompt-01 solution should validate the currently active formats at one shared boundary and preserve rule syntax. Expanding immediately to the target DSL/compiler would add unrelated migration risk.

## 25. Unresolved Architectural Questions

1. What explicit bootstrap/freeze lifecycle guarantees a complete registry before rule validation?
2. Which `rajayoga_naive` definition is authoritative when both rule files are loaded?
3. What minimal immutable validated condition representation is sufficient for Prompt-01 without becoming the future AST?
4. Where are direct Python F2/F3 objects validated?
5. Which definition defects fail load versus produce a typed runtime error when validation is bypassed?
6. How is static system capability compatibility represented separately from chart-specific absence?
7. What temporary boundary preserves Career scoring while centralizing factual predicates?
8. What source identity can be retained before a full compiler supplies stable AST node IDs?

Questions 1–8 affect safe implementation; none prevents completion of this audit.

## 26. Audit-14 Conclusion

Audit-14 is COMPLETE. Three loaders and one partial validator feed two active rule systems through three raw-runtime paths; no rule linter, compiler, AST, or fully validated path exists. Unknown definitions become unmatched, every path lacks parameter/version/capability validation, four duplicate identity classes are unprotected, and five registry/import-order risks remain. Exactly this report was created; no code, tests, rules, CI, prior reports, or Audit-15 artifacts were modified.

### Summary counts

| Metric | Count |
|---|---:|
| Loaders discovered | 3 |
| Validators discovered | 1 |
| CI linters discovered | 0 |
| Compiler or AST components | 0 |
| Active rule systems | 2 |
| Generic validated paths | 0 |
| Specialized validated paths | 0 |
| Raw runtime paths | 3 |
| Unknown-predicate-to-unmatched paths | 4 |
| Unknown-operator-to-unmatched paths | 2 |
| Paths without parameter validation | 4 |
| Paths without version validation | 4 |
| Paths without capability validation | 4 |
| Duplicate identities not rejected | 4 |
| Registry import-order risks | 5 |
| CI-only validations | 0 |
| Prompt-01 findings | 11 |
| Temporary compatibility findings | 4 |
| Future DSL/compiler findings | 5 |
| Missing loader/compiler test categories | 32 |
| P0 findings | 7 |
| P1 findings | 7 |
| P2 findings | 4 |
| P3 findings | 2 |
