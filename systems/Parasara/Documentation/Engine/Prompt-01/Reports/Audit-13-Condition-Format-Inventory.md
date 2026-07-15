# Prompt-01 Audit-13: Condition-Format Inventory

## 1. Executive Summary

The repository has **no canonical condition format** (`NO_CANONICAL_FORMAT`). The active Yoga path uses a plural `conditions` wrapper around nodes shaped as `type/children` and leaves shaped as `type/params`; the generic evaluator implicitly expects that node grammar, but no schema or loader enforces it. The active Career/runtime path uses a separate flat rule dictionary where `type` identifies hard-coded behavior and arguments are top-level fields.

Six distinct formats occur across 12 source files: one active tree format, one active legacy flat format, one test-only bare leaf form, and three documentation-only target/legacy forms. The loaders perform **zero condition-format transformations**: they neither translate `op/args`, normalize keys, unwrap wrappers, canonicalize parameters, nor preserve source positions. Raw YAML dictionaries reach evaluation.

The Master Architecture documents `condition -> op/args -> predicate/params` intent and a canonical AST with `node_type/op/children/predicate_id/params`; neither is accepted by current runtime. Prompt-01 can preserve the two active syntaxes while changing result contracts, but validation, unknown-definition handling, parameters, and the future compiler boundary remain prerequisites. Findings total **6 P0, 8 P1, 4 P2, and 2 P3**.

## 2. Audit Scope and Method

The audit read the Master Architecture Specification, Prompt-01, Audits 1–12, all rule YAML/YML/JSON files, relevant Python constructors/loaders/evaluators/callers/tests, and documentation examples. Repository-wide searches covered all requested keys, six registered predicate IDs, logical operators, wrappers, macros/references, direct dictionaries, serialization, and adapters.

Counts are by distinct representation or source file, not rule instance. Forwarding a loaded dictionary without constructing a new shape is not counted as a condition source. Safe parser/test commands were attempted; the available interpreter lacks both `yaml` and `pytest`, so YAML behavior is based on source-level loader inspection and current files rather than runtime parser confirmation.

## 3. Reconciliation with Audits 1–12

Audit-2's six registered IDs are the lookup vocabulary; active Yoga uses `ASPECT`, `FUNCTIONAL_ROLE`, and `HOUSE_OCCUPANT`, plus unregistered `HOUSE_LORDS_COMBINATION`. Audits 3–4 establish the separate flat runtime/Career compatibility flow. Audit-7 confirms no parameter schemas, aliases, defaults, type/range validation, or source-located errors. Audits 8–11 add capability, state, purity, and cache risks without introducing formats. Audit-12's four evaluators map exactly to the two executable syntaxes and confirms eager AND/OR, missing NOT, ignored fields, malformed-node behavior, and no `ConditionResult`.

All twelve expected reports are present. No previous report requires correction and no missing-report limitation applies.

## 4. Complete Condition-Source Inventory

| Source File | Type | Owner/System | Root Shape | Logical Shape | Predicate Shape | Parameter Shape | Operators | Loader/Consumer | Status | Validation | Active Evidence | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `systems/Parasara/rules/parashara/v1/yogas.yaml:4-82` | YAML | Yoga | list of rules; `conditions: mapping` | `type: AND/OR`, `children: list` | `type: ID` | nested `params` | AND, OR | `load_yoga_rules` -> Yoga -> generic evaluator | ACTIVE_ALTERNATE | top-level fields only | three production rules | Yoga loader/integration, weak format assertions |
| `systems/Parasara/rules/parashara/v1/primitives.yml:1-16` | YAML | legacy M1 | list of flat rules | none | `type: lowercase rule type` | direct top-level fields | none | generic loader -> runtime | LEGACY_COMPATIBILITY | truthy ID only | registry/runtime compatibility | runtime indirect |
| `systems/Parasara/rules/parashara/v1/m1_rules.yaml:4-42` | YAML | legacy M1/Career | list of flat rules | none | `type: rule type` | mostly metadata; runtime context supplies values | none | generic loader -> runtime/Career | LEGACY_COMPATIBILITY | truthy ID only | runtime auto/lazy load | merge/Career indirect |
| `systems/Parasara/rules/parashara/v1/derived_rules.yml:1-14` | YAML | legacy M1 | list of flat rules | none | `type: rule type` | direct top-level fields | none | generic loader -> runtime | LEGACY_COMPATIBILITY | truthy ID only | registry candidate | coverage/runtime indirect |
| `systems/Parasara/engine/interpreters/career.py:33-52` | Python | Career | list of candidate rule dicts | none | `type` plus `id` | direct top-level fields | none | runtime evaluators | LEGACY_COMPATIBILITY | none | active Career path | Career/snapshots indirect |
| `tests/rules/test_predicate_result.py:58-64` | Python test | generic engine | bare node | none | `type: PLANET_IN_HOUSE` | nested `params` | none | direct `evaluate_condition` | TEST_ONLY | none | test only | one matched leaf |
| `systems/Parasara/tests/test_rule_runtime.py:24-33` | Python test | legacy runtime | bare flat rule | none | lowercase `type` | direct top-level fields | none | `evaluate_rule` | LEGACY_COMPATIBILITY | none | test of active contract | matched/unmatched |
| `systems/Parasara/tests/test_rule_runtime_merge.py:9-19` | Python test | legacy runtime | bare flat rule | none | `type: rajayoga_naive` | omitted | none | scored runtime | LEGACY_COMPATIBILITY | none | active contract test | merge only |
| `tests/testing_framework/rule_coverage.py:15-23` | Python tool | coverage | bare flat rule | none | copied `type` | omitted | none | scored runtime | LEGACY_COMPATIBILITY | none | test/tool path | none |
| `Documentation/AI-Prompt/Jyothishyam Master Architecture Specification v1.0.docx` §§87–92 | DOCX | authoritative target | singular `condition` | `op/args`; separately canonical `node_type=logical`, `op/children` | `predicate`; separately `node_type=predicate`, `predicate_id` | nested `params` | AND, OR, NOT; extended | future compiler | DOCUMENTATION_ONLY | specified target, not implemented | no current consumer | none |
| `systems/Parasara/rules/parashara/v1/macros.yaml:1-6` | commented YAML | future rule pack | commented macro list | textual `ANY(count(... AND ...))` | function-like names | macro `params` declaration | ANY, count, AND | none | DOCUMENTATION_ONLY | none | comment only | none |
| `systems/Parasara/Documentation/archive/legacy-basic-specs.md:109-136` | Markdown | legacy design | rule `condition` AST concept | named AST operators | primitive function syntax | positional/function-like | COUNT, ANY, ALL, etc. | none | DOCUMENTATION_ONLY | aspirational | archived | none |

Condition-source file count: **12**. No JSON file contains an executable condition/predicate shape; `calibration.json` is unrelated calibration data.

## 5. Canonical-Format Assessment

Classification: **`NO_CANONICAL_FORMAT`**. The generic evaluator's `type/children/params` contract is implicitly dominant for active trees, but frequency and direct acceptance do not make it canonical. There is no condition schema, typed loader model, canonical serializer, compiler, or normalizer. The authoritative Master Architecture instead says raw YAML must be compiled to a canonical AST and illustrates different keys. Prompt-01 requires compatibility but does not declare the current raw dictionary shape canonical.

| Format ID | Representative Shape | Source Files | Logical Key | Children Key | Predicate Key | Parameters Key | Wrappers | Case Rules | Normalizer | Evaluators | Status | Compatibility | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 Yoga tree | `conditions: {type: AND, children: [{type: ASPECT, params:{...}}]}` | `yogas.yaml` | `type` | `children` | `type` | `params` | plural `conditions` | generic uppercases values; file uppercase | none | generic; dormant Yoga local | ACTIVE_ALTERNATE | PRESERVE_AS_IS | P0 |
| F2 bare typed leaf | `{type: PLANET_IN_HOUSE, params:{...}}` | predicate-result test | none | none | `type` | `params` | none | generic uppercases value | runtime value normalization only | generic | TEST_ONLY | PRESERVE_AS_IS | P1 |
| F3 flat runtime rule | `{type: in_house, planet:Mars, house:1}` | three rule files, Career, runtime tests/tool | none | none | `type` (rule type) | direct fields | none | exact lowercase/mixed branch strings | none | runtime pair | LEGACY_COMPATIBILITY | TEMPORARY_COMPATIBILITY_REQUIRED | P0 |
| F4 intent DSL | `condition: {op: AND, args:[{predicate: ID, params:{}}]}` | Master Architecture | `op` | `args` | `predicate` | `params` | singular `condition` | target normalization required | absent | none | DOCUMENTATION_ONLY | FUTURE_DSL_MIGRATION | P3 |
| F5 canonical AST | `{node_type:logical, op:AND, children:[{node_type:predicate,predicate_id:ID,params:{}}]}` | Master Architecture | `op` plus discriminator | `children` | `predicate_id` plus discriminator | `params` | none/inside rule condition | target canonical rules | absent | none | DOCUMENTATION_ONLY | FUTURE_DSL_MIGRATION | P3 |
| F6 textual macro/expression | `ANY(count(predicate(...) AND ...) >= 1)` | `macros.yaml`, legacy spec | expression tokens | expression | function-like | positional/named expression | macro definition | unspecified | absent | none | DOCUMENTATION_ONLY | FUTURE_DSL_MIGRATION | P3 |

Distinct formats: **6**; canonical: **0**; active alternate: **1**; legacy compatibility: **1**; test-only: **1**; documentation-only: **3**.

## 6. Logical-Node Formats

There are three logical-node variants: F1 `type/children`, F4 `op/args`, and F5 `node_type/op/children`. Only F1 executes. It accepts case-insensitive operator values in the generic evaluator by `str.upper()` (`engine.py:137-142`), but the dormant Yoga evaluator requires exact uppercase (`yoga_engine.py:103-105`). Neither loader normalizes casing.

Current files use only AND and OR with two children each. Runtime imposes no min/max, treats missing/null `children` as empty, permits nesting recursively, and ignores extra keys. NOT is documented/required but unsupported. ALL, ANY, EXISTS, COUNT, REFERENCE, MACRO, reusable/named blocks, and external fragments are documentation-only/future constructs, not aliases for current operators.

## 7. Predicate-Leaf Formats

Four leaf variants exist: active/test `type + params`; active legacy `type + direct fields`; target `predicate + params`; and target AST `node_type=predicate + predicate_id + params`. Only the first two execute, in separate evaluators.

For F1/F2, `params` may be omitted or falsey and becomes `{}`. Direct fields are ignored by the generic evaluator. There is no predicate version on a node, key alias handling, unknown-key rejection, parameter schema, or canonical serialization. The evaluator uppercases `type`; registry lookup also uppercases without trimming. `ASPECT` is an ungoverned alias registration whose handler returns `ASPECT_EXISTS` identity. F3 uses exact hard-coded runtime strings and top-level arguments.

The active Yoga examples are `ASPECT`, `FUNCTIONAL_ROLE`, `HOUSE_OCCUPANT`, and unregistered `HOUSE_LORDS_COMBINATION` (`yogas.yaml:14-74`). The only direct F2 test uses `PLANET_IN_HOUSE` (`test_predicate_result.py:61`). No `parameters`, mapping-key predicate form, or node-level predicate version is used.

## 8. Wrapper Formats

Two wrapper variants exist. Active Yoga uses plural `conditions` with **one mapping**, not a list and not implicit AND (`yoga_engine.py:150-154`). The authoritative/legacy documents use singular `condition` around an AST. Neither loader unwraps either form; Yoga itself selects `rule['conditions']`, while the evaluator accepts only the selected bare node. Empty/falsey Yoga conditions cause the rule to be skipped.

Generic M1 flat rules have no wrapper. There is no active top-level condition list, implicit AND list, wrapper source-location metadata, or support for both singular/plural keys. If both keys exist, Yoga reads only `conditions`; generic loader preserves both without interpretation.

## 9. YAML and JSON Differences

Both loaders call `yaml.safe_load` and only accept a list root (`loader.py:24-35`; `yoga_loader.py:10-18`). The generic loader scans only `.yaml`/`.yml`; JSON rule files are not loaded. Therefore YAML and JSON rules are not behaviorally equivalent, and no JSON condition source exists.

Current YAML supplies integers, floats, booleans, null-capable mappings/lists, and quoted/unquoted strings directly as Python values; no scalar canonicalization follows parsing. Numeric house parameters remain integers in current Yoga data. No anchors, aliases, merge keys, or duplicate condition keys occur in current rule files. The loader does not configure duplicate-key rejection, retain YAML line/column data, or provide a round-trip serializer. Mapping order reaches Python but only declared child-list order is semantically used. PyYAML is imported but is not declared in `systems/Parasara/requirements.txt`, and the audit environment lacks `yaml`, preventing parser-version verification.

## 10. Python-Created Condition Trees

There are two distinct Python-created shapes. `test_evaluate_condition_returns_predicate_result` constructs a bare F2 leaf and bypasses all loading/validation. `interpret_career`, runtime tests, and `rule_coverage` create F3 flat dictionaries, also bypassing file validation. Callers inject no aliases/default operators and may merge registry dictionaries (`runtime.py:134-158`); Career builds new mutable dictionaries and runtime shallow-copies registered rules before merging.

Python-created shape count: **2**. Prompt-01 cannot rely solely on loader validation because direct evaluator/runtime calls remain reachable.

## 11. Loader Normalization

| Loader | File | Input Format | Transformation | Output Format | Validation Before/After | Unknown Fields | Deterministic | Source Location Preserved | Tests | Risk |
|---|---|---|---|---|---|---|---|---|---|---|
| generic directory loader | `engine/rules/loader.py:8-36` | YAML list of arbitrary rule dicts | no condition transformation; adds `_source_file` to rule | same nested/flat dict | truthy `id` only | PRESERVED/FORWARDED | file traversal/duplicate winner not guaranteed | file path only; no line/column | merge/registry indirect | High |
| Yoga loader | `engine/rules/yoga_loader.py:10-45` | `yogas.yaml` list | none; registers same rule object | unchanged F1 wrapper/tree | required top-level fields only | PRESERVED/FORWARDED | source list order, global registry effects | No | top-level required fields | Critical |
| Yoga caller unwrap | `engine/enrichments/yoga_engine.py:150-154` | rule with `conditions` | selects plural wrapper value | bare F1 node | none | wrapper siblings ignored by evaluator | deterministic registry iteration conditional on load | No | integration only | High |
| generic evaluator value normalization | `engine/rules/engine.py:135-162` | bare F1/F2 node | `type -> str.upper`; falsey params/children -> empty | runtime values, same keys | after no validation | IGNORED except params forwarded | input-order traversal | No | leaf only | Critical |

Condition-format loader transformation count: **0**. The wrapper selection and runtime value coercions are not loader transformations; they do not translate one accepted syntax to another. No normalization occurs before validation because condition validation is absent. Predicate cache keys are constructed after wrapper selection and operator dispatch but before parameter normalization (`engine.py:54-60,160-162`).

## 12. Evaluator Format Support

| Evaluator | Canonical Format | Alternate Formats | Wrappers Accepted | Operators | Raw/Normalized Input | Unsupported Behavior | Active Callers | Tests | Priority |
|---|---|---|---|---|---|---|---|---|---|
| `evaluate_condition` | none; implicitly F1/F2 | none | none | AND, OR | raw dict; value uppercase at runtime | op/args/predicate keys become missing type; unknown operator becomes predicate | Yoga/self/test | leaf only | P0 |
| Yoga `_eval_condition` | none; F1 structural subset | none | none | exact AND, OR | raw dict | unknown false tuple; lowercase unsupported | none | none | P2 |
| `evaluate_rule` | none; F3 | none | none | none | raw flat dict | unsupported type false | wrapper/Career/tests | basic | P0 |
| `evaluate_rule_with_score` | none; F3 plus registered metadata | none | none | none | raw/merged rule dict | unknown falls back false; exceptions collapse | Career/test | merge | P0 |

Raw YAML reaches the generic condition evaluator. Lists are not implicit groups, wrappers are handled only by callers, and malformed/target-format nodes do not normalize into F1.

## 13. Aliases and Case Sensitivity

Five alias/case rules were found: generic operator value uppercase; generic predicate value uppercase; registry ID uppercase; exact-uppercase Yoga-local dispatch; and the `ASPECT`/`ASPECT_EXISTS` stacked-registration alias. Key aliases count is zero: `op`, `args`, `predicate`, `predicate_id`, `parameters`, and singular `condition` are not accepted aliases for active F1 keys.

Parameter names and planet/role strings are generally case-sensitive and unnormalized (Audit-7). Both canonical and alias keys can coexist because unknown keys are retained/ignored: active code reads only `type`, `children`, `params`, and `conditions`. No conflict error or test exists. These unaccepted target keys must not be accidentally advertised as current compatibility aliases.

## 14. Parameter Nesting and Validation

F1/F2 nest parameters under `params`; F3 embeds arguments directly. `parameters` is unsupported. Omitted, null, empty, or any falsey `params` becomes `{}`; truthy non-mappings reach cache/handlers and may become errors or false outcomes. Unknown parameters survive in result inputs/cache identity but handlers ignore them. No defaults or aliases are applied by a formal layer, and no validation/source location precedes evaluation.

This reconciles with Audit-7: six registered predicates have absent schema coverage, 20 invalid-input classes may become ordinary unmatched, and the cache key is built from unchecked parameters. Prompt-01 parameter schemas must serve both file and direct-Python paths without rewriting valid F1 syntax.

## 15. Operator Arity and Empty Nodes

No format-level schema declares arity. Current YAML uses two children for every AND/OR. Runtime accepts zero or one: empty/missing/null AND evaluates true; empty/missing/null OR evaluates false; a single child follows `all`/`any`. NOT is not recognized, so zero/one/multiple children are ignored when `NOT` falls through as an unknown predicate. Non-list children are iterated and usually cause attribute errors; non-dict children fail recursively.

Prompt-01/Master require exactly one NOT child and left-to-right AND/OR semantics, but do not settle whether empty AND/OR are valid identity nodes. That remains an architectural question, not an invented audit rule.

## 16. Unknown and Extra Fields

Yoga and generic loaders preserve/forward unknown fields; evaluators ignore keys they do not read. A misspelled `childen` on AND/OR behaves like missing children, while `param`, `parameters`, or direct parameters are ignored by F1. A misspelled/missing `type` produces a false `UNKNOWN` result; unknown operator values become predicate IDs and unknown predicates become false. Generic flat loader also accepts arbitrary rule fields and runtime ignores most.

Ten malformed categories are silently accepted into evaluation or ordinary outcomes: missing children, null children, empty AND, empty OR, unknown/misspelled node fields, unsupported parameter-container aliases, direct parameters on F1, unknown operators, unknown predicate IDs, and non-mapping/falsey parameters. Structurally crashing non-list children and non-dict roots are not counted as silent acceptance.

## 17. Condition Identity and Source Location

Condition nodes have no node ID, condition ID, parent path, YAML line/column, AST digest, or source reference. Generic loader adds only rule-level `_source_file` (`loader.py:31`); Yoga loader does not. Predicate results contain predicate IDs but not rule/node source. Logical traces use predicate summaries without stable child identity. Yoga public matches create random UUID4 IDs unrelated to source nodes (`yoga_engine.py:14-15,177`). Deterministic source-condition attribution is therefore impossible.

## 18. References, Macros and Extended Constructs

Eight future DSL-only constructs/groups were found: `ALL`, `ANY`, `EXISTS`, `COUNT`, `REFERENCE`, `MACRO`, reusable/named condition blocks, and external rule fragments. They are `DOCUMENTED_BUT_NOT_IMPLEMENTED` or `PLANNED_FUTURE_STAGE`. `macros.yaml` contains only a commented expression; no loader expands it. The generic loader may encounter the file but `safe_load` yields no rule list. No active/test construct uses these forms.

NOT is separately required by Prompt-01 and is not counted as future-only. No implementation, format adapter, reference resolver, macro expander, or cycle detector exists.

## 19. Migration Compatibility

| Format | Active Use | Must Preserve | Existing Normalization | Prompt-01 Impact | Later DSL Impact | Required Classification | Risk | Priority |
|---|---|---|---|---|---|---|---|---|
| F1 Yoga tree/wrapper | Yes | syntax and valid rule firing | only runtime value uppercase/falsey collapse | typed leaves/ConditionResult, validation, NOT/short circuit | compile to future AST later | PRESERVE_AS_IS | Critical | P0 |
| F2 bare leaf | test/direct API | direct-call compatibility or explicit API boundary | same as F1 | typed result/schema validation | future direct AST API decision | PRESERVE_AS_IS | Medium | P1 |
| F3 flat runtime | Yes, Career | score/evidence/public behavior temporarily | none | isolate/migrate factual bypass | replace via rule compiler later | TEMPORARY_COMPATIBILITY_REQUIRED | Critical | P0 |
| F4 intent DSL | No | No current runtime contract | none | none unless explicitly staged | target compiler input | FUTURE_DSL_MIGRATION | Low now | P3 |
| F5 canonical AST | No | No current runtime contract | none | typed results must be compatible later | target executable representation | FUTURE_DSL_MIGRATION | Low now | P3 |
| F6 macro expression | No | No | none | none | grammar/macro stage | FUTURE_DSL_MIGRATION | Low now | P3 |

Active formats requiring Prompt-01 compatibility: **2** (F1 and F3). Prompt-01 does not require rewriting either rule source during result consolidation.

## 20. Existing Tests and Coverage Gaps

Current tests cover one F2 predicate leaf with nested params, basic F3 dictionaries, Yoga loading/evaluation of F1, and top-level missing-rule fields. They do not assert normalized syntax, logical format semantics, invalid node rejection, source identity, or serialization.

| Area | Missing Categories | Count | Recommended Test File |
|---|---|---:|---|
| Canonical/current tree | nested AND, nested OR, NOT, mixed nesting, wrapper contract | 5 | `tests/rules/test_condition_format_current.py` |
| Alternate/documented forms | aliases, casing, op/args rejection-or-normalization, singular condition policy | 4 | `tests/rules/test_condition_format_compat.py` |
| Invalid formats | missing predicate/operator/children, wrong child/params types, unknown keys/operator, conflicts, malformed nesting | 9 | `tests/rules/test_condition_format_invalid.py` |
| Loader/evaluator integration | normalization output, validation ordering, YAML/JSON policy, source location, canonical serialization | 5 | `tests/rules/test_condition_format_integration.py` |

Missing condition-format test categories: **23**.

## 21. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Shared validated condition boundary | MISSING | raw dicts/no schema | loaders/evaluator | validated shared entry boundary | IN_SCOPE | P0 | Yes |
| Unknown definitions rejected distinctly | NONCOMPLIANT | operator/predicate -> false | loaders/engine | typed load/runtime definition errors | IN_SCOPE | P0 | Yes |
| Predicate parameter schemas | MISSING | Audit-7; raw params | registry/loaders | schema validation without syntax rewrite | IN_SCOPE | P0 | Yes |
| Active Yoga ID compatibility | NONCOMPLIANT | unregistered HOUSE_LORDS_COMBINATION | YAML/registry | resolve semantic registration/validation decision | IN_SCOPE | P0 | Yes |
| Typed logical-result compatibility | MISSING | F1 logical nodes use PredicateResult | engine/models | ConditionResult boundary preserving F1 | IN_SCOPE | P0 | Yes |
| Central factual execution | NONCOMPLIANT | active F3 runtime bypass | runtime/Career | migrate or isolate explicit adapter | IN_SCOPE | P0 | Yes |
| Preserve valid F1 syntax | PARTIAL | active Yoga dependency | Yoga/engine | compatibility tests | IN_SCOPE | P1 | Yes |
| Preserve F3 behavior temporarily | PARTIAL | Career scoring/output | runtime/Career | bounded adapter/migration plan | TEMPORARY_COMPATIBILITY | P1 | Yes |
| Operator arity validation | MISSING | no min/max; NOT absent | loader/evaluator | validate supported nodes | IN_SCOPE | P1 | Yes |
| Unknown-field/conflict policy | MISSING | retained/ignored | loaders/evaluator | explicit rejection/policy | IN_SCOPE | P1 | Yes |
| Alias/casing policy | PARTIAL | five inconsistent rules | engine/registry/runtime | declare tested current compatibility | IN_SCOPE | P1 | Yes |
| Stable condition source identity | MISSING | no node/source location | loader/trace | deterministic source attribution | IN_SCOPE | P1 | Yes |
| Direct-Python validation parity | MISSING | F2/F3 bypass loaders | evaluator/runtime | shared validation | IN_SCOPE | P1 | Yes |
| Condition-format tests | MISSING | 23 gaps | tests | focused suites | IN_SCOPE | P1 | Yes |
| YAML parser/dependency contract | UNKNOWN | undeclared PyYAML/environment absent | requirements/loaders | pin/verify parsing policy later | IN_SCOPE | P2 | No |
| Dormant Yoga exact-case path | NONCOMPLIANT | duplicate F1 subset | Yoga | retire after migration | TEMPORARY_COMPATIBILITY | P2 | No |
| Documentation/runtime format alignment | NONCOMPLIANT | F1 differs from F4/F5 | docs/runtime | clearly stage compatibility/compiler | OUT_OF_SCOPE_FUTURE_STAGE | P2 | No |
| Test-only bare-node API policy | UNKNOWN | direct test only | tests/engine | decide supported direct API | IN_SCOPE | P2 | No |
| Extended DSL constructs | MISSING | eight future-only groups | architecture/macros | later compiler stage | OUT_OF_SCOPE_FUTURE_STAGE | P3 | No |
| Canonical AST/serialization | MISSING | target only | future compiler | later AST/compiler work | OUT_OF_SCOPE_FUTURE_STAGE | P3 | No |

## 22. Risks and Priorities

The 20 findings total **P0=6, P1=8, P2=4, P3=2**. The largest compatibility risk is treating the documented F4/F5 shapes as already accepted and silently breaking F1. Other critical risks are changing Yoga firing when `HOUSE_LORDS_COMBINATION` becomes a definition error, validating only file inputs while F2/F3 bypass loaders, and changing Career scoring while removing F3. Future DSL work must not be folded into Prompt-01 merely because authoritative target examples use different keys.

## 23. Unresolved Architectural Questions

1. Which boundary validates both loaded F1 trees and direct Python F2 calls?
2. Is F2 a supported public/internal input contract or only a test convenience?
3. What is the temporary lifetime and adapter contract for active F3 Career rules?
4. Are empty AND/OR valid formats or invalid definitions?
5. What current case/alias behavior must be preserved versus rejected at validation?
6. Should JSON rule input remain unsupported until the later compiler, or require explicit parity?
7. What stable rule/node source identity is required during Prompt-01 before a canonical AST exists?

Questions 1, 3, 4, 5, and 7 affect safe Prompt-01 implementation; none blocks completion of this inventory.

## 24. Audit-13 Conclusion

Audit-13 is COMPLETE. Twelve source files express six formats, but none is canonical or schema-enforced. Two formats are active compatibility obligations; three documented target/legacy formats are non-executable, and one bare-leaf form is test-only. Loader condition transformations are absent, ten malformed categories can become ordinary outcomes, and 23 test categories are missing. Exactly this report was created; no code, tests, rules, fixtures, previous reports, or Audit-14 artifacts were modified.

### Summary counts

| Metric | Count |
|---|---:|
| Condition-source files | 12 |
| Distinct condition formats | 6 |
| Canonical formats | 0 |
| Active alternate formats | 1 |
| Legacy compatibility formats | 1 |
| Test-only formats | 1 |
| Documentation-only formats | 3 |
| Logical-node variants | 3 |
| Predicate-leaf variants | 4 |
| Wrapper variants | 2 |
| Aliases and case-normalization rules | 5 |
| Loader transformations | 0 |
| Python-created condition shapes | 2 |
| Malformed formats silently accepted | 10 |
| Active formats requiring Prompt-01 compatibility | 2 |
| Future DSL-only constructs | 8 |
| Missing condition-format test categories | 23 |
| P0 findings | 6 |
| P1 findings | 8 |
| P2 findings | 4 |
| P3 findings | 2 |
