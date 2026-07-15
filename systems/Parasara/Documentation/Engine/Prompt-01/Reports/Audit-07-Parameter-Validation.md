# Prompt-01 Audit-07: Parameter Validation

## 1. Executive Summary

Audit-7 is **COMPLETE**. All six expected prerequisite reports were present and read. The current repository still has six registered predicate IDs backed by five handlers: `ASPECT`, `ASPECT_EXISTS`, `PLANET_IN_HOUSE`, `HOUSE_OCCUPANT`, `FUNCTIONAL_ROLE`, and `PLANET_EXALTED` (`systems/Parasara/engine/rules/predicates.py:12-99`). No new registration or parameter was found relative to Audit-2.

The six registrations expose **seven distinct parameter names**: `from_house`, `to_house`, `from_planet`, `to_planet`, `planet`, `house`, and `role_in`. Across the 14 predicate/parameter rows, five are de facto required, nine are optional, and nine have implicit handler defaults. The registry stores no `parameter_schema`, and no registered predicate performs complete parameter validation. Classification is **0 COMPLETE, 0 PARTIAL, and 6 ABSENT**.

All handlers receive unchecked runtime dictionaries. The evaluator builds the cache key before its no-op `_normalize_inputs`, and falsey inputs become `{}` (`systems/Parasara/engine/rules/engine.py:39-59`). Handler annotations are not enforced. Missing keys, invalid planet names, invalid house values, and unknown role values usually become ordinary `matched=False` results with empty evidence and errors. Unknown keys are preserved in `PredicateResult.inputs` and the cache key but ignored by every handler.

An isolated, non-writing behavior probe confirmed six coercion/normalization risks: Boolean houses match house `1`, integral floats match integer houses, arbitrary iterables can act as `role_in`, falsey non-mappings collapse to `{}`, truthy non-mappings cause predicate-specific partial/error behavior, and cache-key `default=str` masks unsupported values. It identified **20 registered-predicate invalid-input classes that can become ordinary unmatched results** and **9 validation/missing-capability boundary violations**.

Yoga YAML is parsed and checked only for top-level rule fields. Predicate IDs, parameters, types, unknown keys, defaults, aliases, and versions are not validated at load time (`systems/Parasara/engine/rules/yoga_loader.py:7-45`). Invalid condition data can therefore load, reach the cache, and fail or silently evaluate at runtime without rule/condition location.

The audit records **6 P0, 8 P1, 3 P2, and 1 P3 findings**. The main unresolved decisions are the approved canonical planet catalog/alias policy, exact strictness for integer-like house values, whether an empty ASPECT filter means “any aspect,” and the closed vocabulary for `role_in`.

## 2. Audit Scope and Method

Authority was reviewed in this order:

1. `Documentation/AI-Prompt/Jyothishyam Master Architecture Specification v1.0.docx`, including parameter-schema, canonical-parameter, invalid-parameter, missing-capability, and rule-validation requirements.
2. `Documentation/AI-Prompt/Prompt-01.docx`, especially parameter validation, canonical inputs, missing-capability behavior, registry metadata, caching, and error-result requirements.
3. Completed reports Audit-01 through Audit-06 in `systems/Parasara/Documentation/Engine/Prompt-01/Reports/`.
4. Current production source, YAML/JSON, tests, fixtures, tools, and documentation.

Repository-wide searches covered registrations, handler signatures and access patterns, `params.get`/indexing, schema libraries and typed models, rule loaders, condition trees, direct evaluator calls, aliases, defaults, coercions, domain catalogs, cache-key construction, error conversion, and parameter-focused tests. Current behavior was verified statically and with one isolated `python -B` probe using in-memory dependency stubs and a synthetic object graph; it wrote no files or repository state. The normal project imports could not run because `pydantic` and `yaml` are absent from the available interpreter. Targeted pytest also could not run because `pytest` is absent.

Counting policy:

- registered IDs are counted separately, so `ASPECT` and `ASPECT_EXISTS` are two audited predicates even though they share one handler;
- “distinct parameters” deduplicates parameter names across IDs;
- required/optional/default counts use the 14 predicate/parameter inventory rows, not deduplicated names;
- invalid-to-unmatched paths count distinct predicate ID plus invalid-input class; combined table rows for the two Aspect IDs count twice;
- boundary violations count distinct registered predicate/data-capability path, not each test value;
- a validation test category is credited only when assertions establish the parameter contract, not when valid input is merely used.

No production code, tests, rules, prior reports, schemas, snapshots, or generated artifacts were modified.

## 3. Reconciliation with Audits 1–6

Audit-1 found no registry `parameter_schema` field and no registration validation. Audit-7 confirms no schema representation, mandatory flag, version, alias/default metadata, unknown-key policy, or import-order-independent enforcement has appeared (`engine.py:21-32`). Invalid schemas cannot be rejected because schemas cannot be registered.

Audit-2 listed the same six IDs/five handlers and reported all six without parameter validation. Direct inspection confirms its accepted names and adds row-level default, coercion, unknown-key, cache, and invalid-outcome evidence. No newly discovered registered parameter changes Audit-2's inventory.

Audit-3's legacy tuple/boolean/dictionary paths remain separate compatibility flows. They also lack central schemas, but they are not counted among the six registered predicates. Their existence means direct Career/runtime behavior can remain inconsistent after central validation unless deliberately adapted.

Audit-4 identified 47 caller/consumer surfaces and the active path `yogas.yaml -> evaluate_yoga_rules -> evaluate_condition -> evaluate_predicate`. Audit-7 confirms the highest caller risk: Yoga parameters are accepted at load time, and downstream Yoga collapses predicate errors/status distinctions into match/evidence behavior (`yoga_engine.py:150-177`). Direct evaluator tests are the only direct registered-parameter callers.

Audit-5 established that `PredicateResult.inputs` is mutable, not canonical, and may contain arbitrary values. Audit-7 confirms that handlers return the original normalized-by-truthiness mapping, including unknown keys, while the cache key may stringify a different semantic representation.

Audit-6 found no `PredicateStatus` or typed `PredicateError`. Consequently, Audit-7 cannot produce the required `invalid_parameters` state today: invalid values become false results or raw-string error dictionaries. Audit-6's canonicalization and status-invariant questions are direct prerequisites for the fixes implied here.

No disagreement with Audits 1–6 was found. Audit-7 provides finer-grained counts rather than revising earlier conclusions.

## 4. Parameter Sources and Data Flow

| Source | Loader | Normalizer | Validator | Evaluator | Handler | Validation Stage | Bypass Risk | Evidence |
|---|---|---|---|---|---|---|---|---|
| Yoga YAML condition params | `_load_yaml` / `load_yoga_rules` | None | Top-level rule fields only | `evaluate_condition` then `evaluate_predicate` | Dynamic registry handler | Absent | High: invalid IDs/params load and cache | `yogas.yaml:11-74`; `yoga_loader.py:7-45`; `yoga_engine.py:128-177` |
| Code-created condition dict | None | `type` is stringified/uppercased; falsey `params` -> `{}` | None | `evaluate_condition` | Dynamic registry handler | Absent | High: truthy non-mapping forwarded | `engine.py:135-162`; test at `test_predicate_result.py:58-64` |
| Direct evaluator call | None | `_normalize_inputs` returns mapping unchanged; falsey -> `{}` | None | `evaluate_predicate` | Dynamic registry handler | Absent | High: bypasses any future loader-only validation | `engine.py:47-59`; tests at `test_predicate_result.py:14-74` |
| Direct handler call | None | None | None | Bypassed | Named handler | Absent | High API misuse risk; no production caller found | `predicates.py:12-99`; Audit-4 confirms zero active direct handler bypasses |
| Generic rule YAML | `load_rules_from_dir` | Adds `_source_file` only | Truthy rule ID only | Legacy `evaluate_rule_with_score` | Hard-coded runtime branch | Absent from central predicate system | Active Career compatibility bypass | `loader.py:8-46`; `runtime.py:111-269`; `career.py:33-64` |
| Test-only `RAISE_TEST` | Code decorator | Empty mapping | None/schema impossible | `evaluate_predicate` | `_raise` | Absent | Dynamic registration can bypass future fixed production declarations | `test_predicate_result.py:39-55` |

There is no JSON rule source that directly supplies a registered predicate in current execution. No macro/reference/compiler expands predicate parameters. Validation is neither duplicated nor delayed—it is absent—while handler comparisons and `try/except` blocks accidentally act as late outcome filters.

The actual Yoga flow is:

```text
yogas.yaml params
  -> yaml.safe_load
  -> validate_yoga_rule (top-level fields only)
  -> RULE_REGISTRY
  -> evaluate_yoga_rules
  -> evaluate_condition: node.get('params', {}) or {}
  -> evaluate_predicate: cache key first
  -> _normalize_inputs: no-op/truthiness collapse
  -> registered handler comparisons
```

No stage rejects missing/unknown keys, checks types/ranges, resolves parameter aliases, applies a versioned schema, or converts errors to typed `invalid_parameters`.

## 5. Registry Parameter-Schema Assessment

`PREDICATE_REGISTRY` is `Dict[str, Callable]` and stores only an uppercased ID and function (`engine.py:21-32`). `parameter_schema` is **MISSING**.

| Question | Finding | Evidence | Coverage |
|---|---|---|---|
| Schema representation/mandatory | None; decorator accepts only name | `engine.py:28-32` | ABSENT |
| Registration validation | No ID/schema/handler metadata validation | `engine.py:28-32` | ABSENT |
| Loader usage | Loaders never query predicate registry/schema | `loader.py:8-46`; `yoga_loader.py:7-45` | ABSENT |
| Runtime usage | Evaluator invokes handler with unchecked input | `engine.py:54-130` | ABSENT |
| Direct-call bypass | Direct evaluator/handler APIs accept unchecked values | `engine.py:54`; `predicates.py:12-99` | ABSENT |
| Schema version/determinism | Not representable | Registry value is callable only | ABSENT |
| Aliases/defaults | No parameter metadata; only handler behavior | `predicates.py:14-99` | ABSENT |
| Unknown keys | Never rejected; handlers ignore but inputs/cache retain | All handler access sites | ABSENT |
| Test predicates | `RAISE_TEST` registers without schema | `test_predicate_result.py:43-55` | ABSENT |
| Invalid schema/import order | Invalid schema impossible to express; duplicate functions still import-order dependent | `engine.py:28-32` | ABSENT |

Audit-1's registry assessment remains exact. Future schemas enforced only by loaders would still be bypassed by direct `evaluate_predicate`, test registration, and condition dictionaries; the authoritative validation boundary must be shared.

## 6. Complete Predicate Parameter Inventory

| Predicate ID | File | Handler | Parameter | Required | Expected Type | Allowed Values | Default | Aliases | Normalization | Unknown-Key Policy | Current Invalid Outcome | Required Outcome | Tests | Compliance | Scope | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ASPECT` | `predicates.py:12-47` | `aspect_exists` | `from_house` | No | Integer house | Architecturally 1–12; unenforced | Omitted = no source-house filter | None | None | PRESERVED_BUT_UNUSED | False, implicit match for `True`/`1.0`, or broad match if absent | `invalid_parameters` for invalid value | Yoga valid 1/5 only | NONCOMPLIANT | IN_SCOPE | P0 |
| `ASPECT` | `predicates.py:12-47` | `aspect_exists` | `to_house` | No | Integer house | Architecturally 1–12; unenforced | Omitted = no target-house filter | None | None | PRESERVED_BUT_UNUSED | Same as `from_house` | `invalid_parameters` | Yoga valid 10/11 only | NONCOMPLIANT | IN_SCOPE | P0 |
| `ASPECT` | `predicates.py:12-47` | `aspect_exists` | `from_planet` | No | Canonical planet string | Exact edge/AstroState name; catalog unresolved | Omitted = no source-planet filter | None | None/case-sensitive | PRESERVED_BUT_UNUSED | Ordinary false for invalid/nonmatching value | `invalid_parameters` | None | NONCOMPLIANT | IN_SCOPE | P1 |
| `ASPECT` | `predicates.py:12-47` | `aspect_exists` | `to_planet` | No | Canonical planet string | Exact edge/AstroState name; catalog unresolved | Omitted = no target-planet filter | None | None/case-sensitive | PRESERVED_BUT_UNUSED | Ordinary false for invalid/nonmatching value | `invalid_parameters` | None | NONCOMPLIANT | IN_SCOPE | P1 |
| `ASPECT_EXISTS` | `predicates.py:12-47` | `aspect_exists` | `from_house` | No | Integer house | 1–12; unenforced | Omitted = no filter | None | None | PRESERVED_BUT_UNUSED | False/coerced/broad match | `invalid_parameters` | No direct test | NONCOMPLIANT | IN_SCOPE | P0 |
| `ASPECT_EXISTS` | `predicates.py:12-47` | `aspect_exists` | `to_house` | No | Integer house | 1–12; unenforced | Omitted = no filter | None | None | PRESERVED_BUT_UNUSED | False/coerced/broad match | `invalid_parameters` | No direct test | NONCOMPLIANT | IN_SCOPE | P0 |
| `ASPECT_EXISTS` | `predicates.py:12-47` | `aspect_exists` | `from_planet` | No | Canonical planet string | Exact names; catalog unresolved | Omitted = no filter | None | None | PRESERVED_BUT_UNUSED | Ordinary false | `invalid_parameters` | None | NONCOMPLIANT | IN_SCOPE | P1 |
| `ASPECT_EXISTS` | `predicates.py:12-47` | `aspect_exists` | `to_planet` | No | Canonical planet string | Exact names; catalog unresolved | Omitted = no filter | None | None | PRESERVED_BUT_UNUSED | Ordinary false | `invalid_parameters` | None | NONCOMPLIANT | IN_SCOPE | P1 |
| `PLANET_IN_HOUSE` | `predicates.py:50-57` | `planet_in_house` | `planet` | Yes, de facto | Canonical planet string | Exact AstroState name; catalog unresolved | None; missing reads `None` | None | None/case-sensitive | PRESERVED_BUT_UNUSED | Ordinary false/empty evidence | `invalid_parameters` | Valid Mars only | NONCOMPLIANT | IN_SCOPE | P0 |
| `PLANET_IN_HOUSE` | `predicates.py:50-57` | `planet_in_house` | `house` | Yes, de facto | Integer | 1–12; unenforced | None; missing reads `None` | None | None; Python equality | PRESERVED_BUT_UNUSED | Ordinary false, or true for equal bool/float | `invalid_parameters` | Valid house 7 only | NONCOMPLIANT | IN_SCOPE | P0 |
| `HOUSE_OCCUPANT` | `predicates.py:60-67` | `house_occupant` | `house` | Yes, de facto | Integer | 1–12; unenforced | None; missing reads `None` | None | None; Python equality | PRESERVED_BUT_UNUSED | Ordinary false, or true for equal bool/float | `invalid_parameters` | Indirect valid YAML only | NONCOMPLIANT | IN_SCOPE | P0 |
| `HOUSE_OCCUPANT` | `predicates.py:60-67` | `house_occupant` | `planet` | Yes, de facto | Canonical planet string | Exact AstroState name; catalog unresolved | None; missing reads `None` | None | None/case-sensitive | PRESERVED_BUT_UNUSED | Ordinary false/empty evidence | `invalid_parameters` | Indirect Saturn only | NONCOMPLIANT | IN_SCOPE | P0 |
| `FUNCTIONAL_ROLE` | `predicates.py:70-82` | `functional_role` | `role_in` | No in code; semantically needed to match | Collection of role strings | Dynamic table/heuristic labels; no closed catalog | `[]` via `get(..., []) or []` | None | None; arbitrary membership semantics | PRESERVED_BUT_UNUSED | False, partial membership, or caught exception | `invalid_parameters` | Indirect YAML lists only | NONCOMPLIANT | IN_SCOPE | P0 |
| `PLANET_EXALTED` | `predicates.py:85-99` | `planet_exalted` | `planet` | Yes, de facto | Canonical planet string | Exact AstroState/metadata key; catalog unresolved | None; missing reads `None` | None | None/case-sensitive | PRESERVED_BUT_UNUSED | Ordinary false/empty evidence | `invalid_parameters` | Valid-form Mars unmatched only | NONCOMPLIANT | IN_SCOPE | P0 |

Distinct parameters: **7**. Required inventory rows: **5**. Optional rows: **9**. Rows with defaults: **9** (eight Aspect filter omissions plus `role_in=[]`). Parameter aliases: **0**.

The Aspect comment explicitly calls house filters optional and lists planet filters without a required marker (`predicates.py:14-15`). Whether zero filters is a valid “any edge” query is not documented. Required classifications for the remaining handlers are de facto: omission always prevents a meaningful positive factual check, but no schema declares them.

## 7. Required and Missing Parameters

`PLANET_IN_HOUSE`, `HOUSE_OCCUPANT`, and `PLANET_EXALTED` use `.get`, so omission and explicit `None` are indistinguishable (`predicates.py:52-53,62-63,87`). They all return ordinary false with `{}` evidence and `errors=[]`. The result does not reveal whether the caller omitted a required key, supplied `None`, supplied an unknown planet, or requested a valid planet absent from AstroState.

`FUNCTIONAL_ROLE` treats omission, `None`, an empty list, and other falsey values as the same empty collection (`predicates.py:72`). All normally produce unmatched with empty evidence. Omission versus explicit default is still distinct in `PredicateResult.inputs` and the cache key.

All Aspect filters are applied only when their key is present (`predicates.py:26-33`). Omission removes that constraint; explicit `None` adds a constraint comparing against `None`. Therefore omission and explicit `None` can differ. With no recognized filters, every well-formed edge matches; a typo such as `from_huose` silently broadens the predicate rather than producing a false result.

No predicate distinguishes a missing required parameter from missing AstroState facts, and no result uses `status=invalid_parameters` because status does not exist.

## 8. Type Validation and Coercion

| Input Pattern | Current Classification | Evidence | Effect |
|---|---|---|---|
| Correct string planet | NO_COERCION | Exact `p.name == name` in `_planet_by_name`, `predicates.py:8-9` | Works only with exact spelling/case |
| Numeric/non-string planet | NO_COERCION, but unvalidated | Same equality | Usually ordinary false |
| House numeric string (`"7"`) | NO_COERCION | Direct equality at `predicates.py:27,29,54,64` | Ordinary false |
| Integral float (`7.0`) | IMPLICIT_LANGUAGE_COERCION | Python numeric equality | Can match integer house 7 |
| Boolean (`True`) | IMPLICIT_LANGUAGE_COERCION | `bool` subclasses/equates with integer 1 | Can match house 1 |
| `role_in` string/mapping/set | IMPLICIT_LANGUAGE_COERCION | `functional_role in role_in`, `predicates.py:77` | Arbitrary substring/key/set membership; may partially evaluate |
| `role_in` noniterable integer | NO_COERCION then runtime exception | Membership operation | Evaluator returns raw-string error result |
| Falsey non-mapping params (`None`, `[]`, `''`, `0`) | EXPLICIT_BUT_UNDOCUMENTED | `params or {}` at `engine.py:55,58,79` | Collapses to empty mapping |
| Truthy non-mapping params | AMBIGUOUS | No mapping check | Handler-dependent broad match, false, or caught exception |
| Unknown/custom nested values | EXPLICIT_BUT_UNDOCUMENTED cache coercion | `json.dumps(..., default=str)`, `engine.py:39-44` | String representation enters cache identity; handler sees original object |

No registered parameter is explicitly and documentably coerced. Strings, integers, floats, booleans, lists, mappings, `None`, and arbitrary objects are not type-checked. NaN/infinity are accepted by Python/JSON defaults and normally compare false for houses, but no rejection exists. Tuples/sets can act as role collections; sets are stringified into a potentially order-dependent cache key.

Coercion-risk count is **6**: Boolean/integer equality, float/integer equality, arbitrary role iterables, falsey-container collapse, truthy non-mapping inconsistency, and `default=str` cache coercion.

## 9. Domain-Value Validation

| Value Type | Canonical Form | Accepted Alternatives | Invalid Examples | Validation Location | Normalization | Current Failure | Gap | Priority |
|---|---|---|---|---|---|---|---|---|
| Planet | Nonempty canonical AstroState planet identifier | Exact strings present in AstroState; exact `Rahu`/`Ketu` work if present | `mars`, whitespace, `7`, `None`, unsupported name | None; exact lookup in `_planet_by_name` | None | Ordinary false | Catalog, aliases, whitespace/case and absent-data distinction unresolved | P0 |
| House | Integer 1–12 | Floats/bools equal to stored integer are implicitly accepted | `0`, `-1`, `13`, `"7"`, `"seven"`, `True`, `7.0`, `None` | None; direct equality | None | False or implicit match | Strict integer/bool policy and range missing | P0 |
| Functional role | Collection of approved role codes | Any iterable/mapping accepted by `in` | Unknown labels, scalar string, integer, `None` | None | `or []` only | False, partial evaluation, or error | No versioned closed vocabulary/type/cross-value validation | P0 |
| Aspect source/target | Optional canonical planet and/or house filters | Exact strings; bool/float house equality | Invalid planet, invalid house, no filters, contradictory/unusable filters | None; per-edge comparisons | None | False or broad/partial match | No schema, at-least-one-filter rule, or cross-field checks | P0 |
| Sign | No registered predicate parameter | None | Names/indices/aliases not applicable | N/A | N/A | N/A | Legacy `in_sign` belongs to compatibility audit | P3 |
| Varga | No registered predicate parameter | None | Identifiers not applicable | N/A | N/A | N/A | Future predicate/schema decision | P3 |
| Comparison/threshold | No registered predicate parameter | None | NaN/infinity/units not applicable to current IDs | N/A | N/A | N/A | Future predicate/schema decision | P3 |

Planet names are case-sensitive and whitespace-sensitive. There is no `graha`, `bhava`, source/target, or spelling alias. `Rahu` and `Ketu` appear in functional-role calculation sets, but no predicate-schema test proves their acceptance. The exact approved planet catalog is not specified in current registry metadata.

The heuristic functional-role producer emits `functional_benefic`, `functional_malefic`, `functional_neutral`, or `yogakaraka` (`functional_roles.py:94-146`). Yoga YAML additionally supplies `benefic` and `malefic` (`yogas.yaml:20,74`), which are not heuristic `functional_role` values. External table files can supply other values. The handler validates none of them, so the authoritative vocabulary remains unresolved.

## 10. Unknown-Parameter Behavior

All six IDs classify as `PRESERVED_BUT_UNUSED`:

- handlers read only recognized keys and never reject/remove extras (`predicates.py:14-99`);
- the full input mapping is stored in `PredicateResult.inputs`;
- `_cache_key` serializes the full mapping, so an ignored key fragments cache identity (`engine.py:39-44`);
- evidence contains only selected recognized/matched fields, so unknown keys disappear from evidence;
- Yoga loaders preserve condition dictionaries without checking their keys.

For Aspect, an unknown key is more dangerous than a harmless extra: if no recognized filters remain, all graph edges match. Misspelled filters can therefore turn an intended constraint into a broad positive result. For the other handlers, misspellings generally become false because required data reads as `None`, but no error explains the typo.

Unknown-key behavior count: **6 predicates ignoring while preserving unknown parameters**. No current public caller reliance on extra keys was found, but YAML and direct dictionaries are unconstrained.

## 11. Aliases and Normalization

Parameter alias count is **0**. Repository searches found no handler/loader support for `graha`, `bhava`, `functional_role`, `source`, or `target` as aliases of the seven canonical names. `ASPECT` is a predicate-ID alias, not a parameter alias.

Planet values are not trimmed, case-folded, or mapped. House values are not converted or range-normalized. Role collections and values are not normalized. The evaluator's `_normalize_inputs` returns the same truthy object and only collapses falsey values to `{}` (`engine.py:47-51`).

Because `_cache_key` runs before `_normalize_inputs`, any future handler-level normalization would occur after cache identity. Today key ordering is normalized by `sort_keys=True`, so reordered dictionaries share a parameter JSON component. Semantically equivalent omission/explicit defaults, case variants if later authorized, and alternate types do not share keys.

There is no canonical/alias conflict behavior and no alias test. Whether aliases should exist is an architectural question, not a change proposed by this audit.

## 12. Default-Value Behavior

| Predicate/Parameter | Default | Classification | Location | Omission vs Explicit Default | Cache Impact |
|---|---|---|---|---|---|
| Aspect four filters, both IDs | Key absence means no constraint | HANDLER_DEFAULT | `predicates.py:26-33` | Omission differs from explicit `None`; explicit value filters | Different keys and potentially different outcome |
| `FUNCTIONAL_ROLE.role_in` | `[]` | HANDLER_DEFAULT | `predicates.py:72` | Omitted, `None`, and `[]` evaluate alike; stored inputs differ | Three cache keys for equivalent false behavior |
| Leaf condition `params` | `{}` when absent/falsey | CALLER_DEFAULT/evaluator fallback | `engine.py:161-162` | Missing, `None`, empty list/string/zero collapse alike | Same `{}` key after `or {}` |
| Required `planet`/`house` | Incidental `None` from `.get` | IMPLICIT_PYTHON_DEFAULT, not a valid contract default | `predicates.py:52-53,62-63,87` | Missing and explicit `None` evaluate false but inputs differ | Fragmented keys |

No `CENTRAL_SCHEMA_DEFAULT`, `LOADER_DEFAULT`, or documented versioned default exists. None depends on system time. Aspect omission changes factual scope, so its semantics require explicit approval. Defaults are applied after or independently of cache-key construction and are not materialized into canonical `PredicateResult.inputs`.

## 13. Invalid-Parameter Outcomes

| Predicate | Invalid Input | Current Behavior | Current Status | Error Produced | Evidence Produced | Expected Prompt-01 Behavior | Regression Risk | Priority |
|---|---|---|---|---|---|---|---|---|
| `ASPECT`, `ASPECT_EXISTS` | House string/out of range | Per-edge comparison usually false | No status; ordinary unmatched | None | `{}` | `invalid_parameters`, stable typed error | High; current rule firing may change | P0 |
| `ASPECT`, `ASPECT_EXISTS` | Planet non-string/unknown | Per-edge comparison false | Ordinary unmatched | None | `{}` | `invalid_parameters` | Medium | P1 |
| `ASPECT`, `ASPECT_EXISTS` | Boolean/integral-float house | Can match house 1/integer | Ordinary matched/unmatched | None | Matched edge or `{}` | Reject or approved documented coercion | High | P0 |
| `ASPECT`, `ASPECT_EXISTS` | Falsey non-mapping params | Collapses to `{}` and matches any edge | Ordinary matched if graph has edges | None | All matched edges | `invalid_parameters` for invalid container | Critical | P0 |
| `ASPECT`, `ASPECT_EXISTS` | Unknown/misspelled filter | Ignored; may match every edge | Ordinary matched/unmatched | None | Broad edges or `{}` | `invalid_parameters` | Critical | P0 |
| `PLANET_IN_HOUSE` | Missing `planet` | `None` lookup, false | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| `PLANET_IN_HOUSE` | Missing `house` | Compares to `None`, false | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| `PLANET_IN_HOUSE` | Invalid planet type/name | Lookup fails | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| `PLANET_IN_HOUSE` | Invalid house type/range/None | Usually false; bool/float may match | Ordinary unmatched/matched | None | `{}` or match evidence | `invalid_parameters` | Critical | P0 |
| `PLANET_IN_HOUSE` | Falsey non-mapping params | Becomes `{}`, both keys missing | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| `HOUSE_OCCUPANT` | Missing `planet` | `None` lookup, false | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| `HOUSE_OCCUPANT` | Missing `house` | Comparison false | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| `HOUSE_OCCUPANT` | Invalid planet type/name | Lookup fails | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| `HOUSE_OCCUPANT` | Invalid house type/range/None | Usually false; bool/float may match | Ordinary unmatched/matched | None | `{}` or match evidence | `invalid_parameters` | Critical | P0 |
| `HOUSE_OCCUPANT` | Falsey non-mapping params | Becomes `{}` | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| `FUNCTIONAL_ROLE` | Missing/None/empty `role_in` | Becomes `[]`; no matches | Ordinary unmatched | None | `{}` | `invalid_parameters` if role selection is required | High; requiredness unresolved | P0 |
| `FUNCTIONAL_ROLE` | Unknown role values | Membership never matches | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| `FUNCTIONAL_ROLE` | Wrong iterable such as string/mapping | Uses substring/key membership; partial evaluation | Ordinary matched/unmatched | None | Matched planets or `{}` | `invalid_parameters` | Critical | P0 |
| `FUNCTIONAL_ROLE` | Noniterable value | Raises inside handler; evaluator catches | Error-like false, no typed status | Raw exception string dictionary | Predicate-error reason | `invalid_parameters`, safe typed error | High | P0 |
| `FUNCTIONAL_ROLE` | Falsey non-mapping params | Becomes `{}`/empty role list | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| `PLANET_EXALTED` | Missing `planet` | Lookup fails | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| `PLANET_EXALTED` | Invalid planet type/name | Lookup fails | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| `PLANET_EXALTED` | Falsey non-mapping params | Becomes `{}` | Ordinary unmatched | None | `{}` | `invalid_parameters` | High | P0 |
| All handlers | Truthy non-mapping params | Handler-specific false/broad match or exception | Unmatched/matched/error-like | Sometimes raw exception string | Usually empty or predicate-error reason | `invalid_parameters` before invocation | Critical | P0 |

The reported invalid-input-to-unmatched count is **20** under the section-2 policy: four combined Aspect invalid-house/planet paths expand to four registered-ID paths; `PLANET_IN_HOUSE` and `HOUSE_OCCUPANT` contribute five each; `FUNCTIONAL_ROLE` contributes three; and `PLANET_EXALTED` contributes three. Broad-match, partial-evaluation, and exception rows are additional violations but are not included in that count.

No invalid input produces a typed error or `invalid_parameters` status. Through `evaluate_predicate`, uncaught invalid-parameter exception count is **0** because broad `except Exception` converts failures. Six registered IDs have a reachable handler-exception conversion class for suitable truthy non-mapping or nested values; those results expose `str(e)` in `errors` (`engine.py:117-129`). Direct handler calls can raise uncaught exceptions.

## 14. Validation versus Missing-Capability Boundary

| Predicate Path | Valid Parameter / Missing Data | Current Outcome | Required Distinction | Violation Count |
|---|---|---|---|---:|
| `ASPECT` | Valid filters, AspectGraph absent/malformed | Ordinary unmatched/empty evidence | `missing_capability` or typed missing data | 1 |
| `ASPECT_EXISTS` | Same shared handler path | Ordinary unmatched/empty evidence | Same | 1 |
| `PLANET_IN_HOUSE` | Valid canonical planet absent | Ordinary unmatched, indistinguishable from invalid name | Typed missing-data result | 1 |
| `PLANET_IN_HOUSE` | Planet present but house unavailable (`None`) | Ordinary unmatched | Missing house capability/data | 1 |
| `HOUSE_OCCUPANT` | Valid canonical planet absent | Ordinary unmatched | Typed missing-data result | 1 |
| `HOUSE_OCCUPANT` | Planet present but house unavailable | Ordinary unmatched | Missing house capability/data | 1 |
| `FUNCTIONAL_ROLE` | Planet/lagna/role capability unavailable or computation yields no usable role facts | Ordinary unmatched or caught error | Typed capability/data or execution result | 1 |
| `PLANET_EXALTED` | Valid canonical planet absent | Ordinary unmatched | Typed missing-data result | 1 |
| `PLANET_EXALTED` | Planet exists but flags/exaltation mapping capability absent | Ordinary unmatched | Typed capability/data result, unless approved factual semantics say false | 1 |

Boundary-violation count is **9**. Invalid parameter and missing capability both frequently yield `matched=False`, `{}` evidence, and `errors=[]`; exceptions sometimes replace both with a generic predicate error. This erases all four authoritative distinctions among invalid input, factual false, missing data/capability, and unexpected execution failure.

The exact missing-data status for absent planet/house/exaltation facts remains an architectural question; the current conflation is noncompliant regardless of which approved typed category is selected.

## 15. Condition-Tree and Rule-Loader Validation

The Yoga loader requires only rule-level fields (`yoga_loader.py:7,21-24`). It does not recurse into `conditions`. The generic loader checks only truthy rule IDs and silently skips file/parse exceptions (`loader.py:8-36`). Neither imports or queries predicate schemas.

Current behavior:

1. Unknown predicate IDs are not rejected. `HOUSE_LORDS_COMBINATION` loads and becomes an unknown-predicate false result.
2. Predicate parameters are not validated at load time or before runtime invocation.
3. Invalid rule files can load if their top-level Yoga fields exist.
4. Parameter errors carry no source file, rule ID, condition path, or AST node location.
5. Rule/predicate versions do not affect validation.
6. Registry import order affects whether a predicate ID resolves, but never parameter validation.
7. No parameter alias normalization occurs.
8. Duplicate YAML keys are not detected by repository code; behavior is delegated to the YAML library.
9. Loader normalization does not hide values, but exception swallowing hides malformed files/rules.
10. Yoga goes through the central unchecked evaluator; Career rules use a separate unchecked hard-coded runtime.

Prompt-01 requires schemas and invalid-parameter distinction now. Full AST location, macro expansion, duplicate-key diagnostics, and compiler-grade validation belong to the later DSL/compiler stage, but temporary loaders must not silently turn malformed predicate calls into factual false.

## 16. Cache and Canonical-Input Interaction

`evaluate_predicate` constructs `_cache_key(astro, name, params or {})` before lookup or `_normalize_inputs` (`engine.py:39-60`). Therefore validation and canonical normalization happen **after the key**, except neither actually occurs.

- Dictionary key order is normalized by `json.dumps(sort_keys=True)`, so `{'planet':'Mars','house':7}` and the reversed insertion order share the parameter-string component.
- `{'house':7}` and `{'house':'7'}` have different keys and different current outcomes; no type policy decides equivalence.
- Omitted Aspect filters and explicit defaults/`None` differ in key and may differ in outcome.
- Omitted, `None`, and `[]` `role_in` behave equivalently but fragment the cache.
- Unknown/unused parameters affect keys while not affecting handler logic.
- Invalid parameters, unknown predicate results, and caught exceptions are cached.
- There is no alias normalization before caching.
- `default=str` permits non-JSON-safe objects and may use process/order-dependent representations; the fallback `str(params)` is weaker still.
- Mutable parameters are stored by reference in `PredicateResult.inputs`; mutation after key construction can make recorded inputs disagree with the key and cached facts.
- Handler-level exact-case behavior means case variants fragment keys and results.

Canonical parameters are not preserved: `inputs` is the original truthy object or `{}`, not a validated/default-materialized immutable representation. Audit-11 must design the cache, but validation/canonicalization must precede whatever key it approves.

## 17. Existing Tests and Coverage Gaps

Existing tests establish only:

- valid `PLANET_IN_HOUSE` with Mars/house 7 and cache behavior (`tests/rules/test_predicate_result.py:14-27`);
- valid-form `PLANET_EXALTED` input producing unmatched (`lines 30-36`);
- a programming exception becoming a nonempty error list, without parameter semantics (`lines 39-55`);
- one valid code-created condition tree (`lines 58-64`);
- Yoga loader top-level required fields (`tests/enrichments/test_yoga_loader.py:5-26`);
- valid example parameter dictionaries are exercised indirectly through Yoga, without individual assertions (`test_yoga_engine_rule_driven.py:17-37`).

| Area | Missing Categories | Missing Count | Risk | Recommended Location |
|---|---|---:|---|---|
| General validation | Missing required; unknown; invalid types; invalid values; explicit None; empty strings; additional keys; defaults; aliases; conflicting aliases; deterministic normalization | 11 | Silent false/broad match and cache fragmentation | `tests/rules/test_predicate_parameters.py` |
| Planet parameters | Invalid planet; capitalization; Rahu/Ketu; unsupported name; non-string | 5 | Invalid input indistinguishable from absent planet; catalog drift | `tests/rules/test_predicate_planet_parameters.py` |
| House parameters | Houses 1/12; zero; negative; above 12; numeric string; nonnumeric string; boolean; float; None | 9 | Python equality admits unintended values; ranges unprotected | `tests/rules/test_predicate_house_parameters.py` |
| Error-result behavior | `invalid_parameters`; stable code; predicate ID; safe details; no raw exception; distinct from unmatched; distinct from missing capability | 7 | Consumers cannot act safely on failures | `tests/rules/test_predicate_parameter_errors.py` |
| Integration | Invalid YAML/JSON rejection; invalid direct invocation; Yoga validation; condition validation; normalized-cache behavior; downstream evidence/errors | 6 | Loader/runtime/public paths can diverge | `tests/rules/test_predicate_parameter_integration.py` |

Missing test-category count is **38**. The valid-planet category is credited by the direct Mars tests; no other requested category has assertions sufficient to define the contract. Alias categories remain gaps because tests should establish the approved no-alias or alias policy, even if the approved count stays zero.

The targeted pytest command was:

```text
python -B -m pytest -p no:cacheprovider tests/rules/test_predicate_result.py tests/enrichments/test_yoga_loader.py tests/enrichments/test_yoga_engine_rule_driven.py
```

It did not execute because the interpreter reported `No module named pytest`. This is an environment limitation, not a failing test result.

## 18. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Registry parameter schema for every predicate | MISSING | Callable-only registry | `engine.py:21-32`; `predicates.py` | Add approved versioned schemas/metadata | IN_SCOPE | P0 | Yes |
| Validate before factual evaluation | NONCOMPLIANT | Cache/invocation precedes any validation | `engine.py:39-130` | Shared pre-invocation validation boundary | IN_SCOPE | P0 | Yes |
| Invalid input distinct from unmatched | NONCOMPLIANT | 20 invalid-to-false paths | All registered handlers | Typed `invalid_parameters` outcome | IN_SCOPE | P0 | Yes |
| Missing capability distinct from invalid/false | NONCOMPLIANT | Nine conflated paths | handlers; AstroState consumers | Capability/data checks and typed outcomes | IN_SCOPE | P0 | Yes |
| Rule/condition parameter validation | MISSING | Top-level-only Yoga validator | `yoga_loader.py`; `loader.py`; `engine.py` | Validate IDs/params before executable registration/evaluation | IN_SCOPE | P0 | Yes |
| Canonical validated inputs before cache key | NONCOMPLIANT | `_cache_key` precedes no-op normalization | `engine.py:39-59` | Validate/default/canonicalize before cache identity | IN_SCOPE | P0 | Yes |
| Planet parameter type/value policy | MISSING | Exact unchecked lookup | `predicates.py:8-9,31,33,52,63,87` | Approve catalog/case/alias rules and validate | IN_SCOPE | P1 | Yes |
| House integer/range policy | MISSING | Direct equality accepts bool/float | `predicates.py:27,29,53,62` | Reject invalid type/range or document approved coercion | IN_SCOPE | P1 | Yes |
| Functional-role collection/value policy | MISSING | Arbitrary membership; dynamic values | `predicates.py:72-78`; `functional_roles.py` | Approve list/tuple and closed/versioned values | IN_SCOPE | P1 | Yes |
| Aspect cross-field/filter policy | MISSING | Zero filters match all; no schema | `predicates.py:14-34` | Define optionality/at-least-one and validate filters | IN_SCOPE | P1 | Yes |
| Unknown-parameter rejection | NONCOMPLIANT | Six preserve/cache but ignore extras | handlers; `engine.py:39-44` | Reject unknown keys with location/error | IN_SCOPE | P1 | Yes |
| Canonical defaults/omission equivalence | MISSING | Handler/implicit defaults fragment cache | `predicates.py`; `engine.py` | Declare/materialize approved schema defaults | IN_SCOPE | P1 | Yes |
| Typed safe invalid-parameter error | MISSING | No status/error model; raw `str(e)` | `engine.py:117-129` | Use approved Audit-6 supporting models | IN_SCOPE | P1 | Yes |
| Parameter validation tests | MISSING | 38 categories missing | `tests/rules`; Yoga tests | Add focused unit/integration coverage | IN_SCOPE | P1 | Yes |
| Safe exception/input-detail handling | NONCOMPLIANT | Invalid nested/container values can reach raw error text | `engine.py:117-129` | Safe details and internal logging boundary | IN_SCOPE | P2 | No |
| Compatibility bypass consistency | NONCOMPLIANT | Career/runtime loaders use separate unchecked contracts | `runtime.py`; `career.py`; loaders | Explicit adapters without semantic/scoring drift | TEMPORARY_COMPATIBILITY | P2 | No |
| Immutable/JSON-safe parameter values | NONCOMPLIANT | Shared mutable inputs and `default=str` | `engine.py:39-51`; `PredicateResult` | Audit-6 canonical immutable value policy | IN_SCOPE | P2 | No |
| Compiler-grade source/duplicate diagnostics | MISSING | No AST path/duplicate-key diagnostics | loaders/future compiler | Implement with later DSL/compiler architecture | OUT_OF_SCOPE_FUTURE_STAGE | P3 | No |

## 19. Migration Risks and Priorities

The 18 compliance rows define the finding counts: **P0=6, P1=8, P2=3, P3=1**.

P0 risks are the absence of registry schemas, lack of pre-evaluation validation, invalid-to-false collapse, missing-capability collapse, unchecked rule conditions, and cache identity built from unvalidated inputs.

P1 completion work covers planet, house, role, and Aspect policies; unknown-key rejection; canonical defaults; typed safe errors; and 38 missing test categories. These changes can alter Yoga firing—especially misspelled/empty Aspect filters—and must be protected by rule-location diagnostics and regression tests.

P2 compatibility risks are raw exception leakage, divergent Career/runtime validation, and mutable/non-JSON-safe parameter values. P3 compiler diagnostics should not expand Prompt-01 into a full DSL redesign.

Migration must preserve the factual/astrological behavior of valid approved parameters while making invalid calls explicit. It must not infer new aliases, silently coerce numeric/string variants, or treat missing AstroState data as invalid input. Loader validation and direct runtime validation must share the same schema semantics so no caller bypasses them.

## 20. Unresolved Architectural Questions

1. What is the approved canonical planet identifier catalog, including case, whitespace, Rahu/Ketu spelling, and any aliases?
2. Must house values be strict non-Boolean integers 1–12, or are integral floats/numeric strings ever explicitly allowed?
3. Is an Aspect call with zero filters a valid “any aspect exists” query, or must at least one source/target constraint be supplied?
4. What is the closed, versioned `role_in` vocabulary? Are YAML values `benefic`/`malefic` valid aliases, stale values, or table-defined extensions?
5. Is `role_in` required and nonempty, and are tuples/sets permitted or only canonical lists?
6. Which missing planet/house/exaltation facts are `missing_capability` versus another approved typed missing-data outcome?
7. Should explicit schema defaults be materialized in `PredicateResult.inputs` so omission and explicit default serialize/cache identically?
8. Are parameter aliases prohibited unless registered, and what conflict rule applies if canonical and alias keys coexist?
9. How should test-only dynamic predicates supply schemas without weakening production registration requirements?
10. At what temporary boundary should Yoga rules be rejected with source/condition location before the full compiler exists?

These questions do not block completion of Audit-7, but questions 1–8 block safe parameter-schema implementation.

## 21. Audit-7 Conclusion

Audit-7 is complete and reliable. All six prerequisite reports were available. The current six registered predicate IDs expose seven distinct parameter names but no schema, type/range/value validation, alias normalization, unknown-key rejection, typed invalid-parameter result, or canonical pre-cache input representation.

### Summary counts

| Metric | Count |
|---|---:|
| Registered predicates audited | 6 |
| Distinct parameters | 7 |
| Required predicate/parameter rows | 5 |
| Optional predicate/parameter rows | 9 |
| Parameter rows with defaults | 9 |
| Parameter aliases | 0 |
| Predicates with COMPLETE validation | 0 |
| Predicates with PARTIAL validation | 0 |
| Predicates with ABSENT validation | 6 |
| Predicates ignoring/preserving unknown parameters | 6 |
| Invalid-input-to-unmatched paths | 20 |
| Invalid inputs raising uncaught exceptions through evaluator | 0 |
| Registered IDs with reachable caught handler-exception conversion | 6 |
| Coercion risks | 6 |
| Validation/missing-capability boundary violations | 9 |
| Missing parameter-validation test categories | 38 |
| P0 findings | 6 |
| P1 findings | 8 |
| P2 findings | 3 |
| P3 findings | 1 |

No implementation corrections were made. The only modified file is this report. Audit-8 was not started.
