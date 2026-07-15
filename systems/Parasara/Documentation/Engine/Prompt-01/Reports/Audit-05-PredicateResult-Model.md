# Prompt-01 Audit-05: PredicateResult Model

## 1. Executive Summary

The repository contains **one actual `PredicateResult` class definition**: the production `@dataclass(frozen=True)` at `systems/Parasara/engine/rules/engine.py:9-18`. It is the canonical and only active typed predicate-result model. No alternate Pydantic, `NamedTuple`, `TypedDict`, protocol, subclass, wrapper, test-only result class, factory model, deserializer, or public JSON schema for `PredicateResult` was found.

The current class has eight required fields: `matched`, `predicate_id`, `inputs`, `evidence`, `trace_steps`, `errors`, `cache_hit`, and `evaluation_time_ms`. Prompt-01 requires ten: the current eight plus mandatory `predicate_version` and `status`, with stronger immutable/typed/canonical semantics for the collection fields. The outer object rejects attribute reassignment, but it is not deeply immutable. All four collection fields are mutable; nested values are unrestricted; constructor-owned and caller-owned references are shared; and `dataclasses.replace` creates shallow cache/telemetry copies. An isolated check confirmed that mutating a cold result's evidence also mutates the cached warm result.

The dataclass performs no runtime validation. It accepts non-boolean `matched` and `cache_hit`, blank IDs, negative evaluation times, arbitrary mutable/non-JSON-safe nested values, and any objects despite annotations. It has no status/matched invariant because status does not exist. Unknown predicates, missing data/invalid parameters, invalid handler returns, and exceptions all become `matched=False` variants with ad hoc evidence/errors; missing capability, timeout, and skipped states are not representable.

Generated dataclass equality includes all fields, including `cache_hit` and `evaluation_time_ms`, so telemetry changes make logically equivalent results unequal. A generated hash method exists because the dataclass is frozen, but normal instances are not practically hashable because dictionaries and lists are fields; an isolated `hash(result)` raised `TypeError`. No normalized logical hash or telemetry-excluding identity exists.

The only serializer that directly receives a complete `PredicateResult` is `dataclasses.asdict` followed by `json.dumps(default=str)` in `tests/rules/test_predicate_result.py:67-74`. There is no canonical serializer. `default=str` masks unsupported values and may emit process- or ordering-dependent representations. Audit-04 identifies **9 material serialization consumers** when the direct model test and downstream RuleMatch, snapshot, API/frontend, CI, determinism, and artifact surfaces are counted. No current public schema directly exposes the complete model, but migration effects can propagate into those downstream JSON surfaces if predicate information or rule behavior changes.

All four expected prerequisite reports are now available. Audit-04 classifies 47 caller/consumer surfaces, 23 requiring direct migration, 9 material serialization consumers, and no unknown migration status. Audit-05 is reconciled with that inventory. Corrected countable findings are **5 P0, 10 P1, 4 P2, and 0 P3**. No production corrections were implemented.

## 2. Audit Scope and Method

Authority was applied in the approved order:

1. `Documentation/AI-Prompt/Jyothishyam Master Architecture Specification v1.0.docx`, especially predicate requirements/result contract/caching and global invariants.
2. `Documentation/AI-Prompt/Prompt-01.docx`, especially sections 4-9, 10-19, 22-25, 29-32, and 35-37.
3. Completed reports `Audit-01-Predicate-Registry.md`, `Audit-02-Complete-Predicate-Inventory.md`, `Audit-03-Legacy-Return-Contracts.md`, and `Audit-04-Complete-Caller-Inventory.md`.
4. Current source, tests, schemas, snapshots, scripts, and documentation as evidence of current behavior.

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-04-Complete-Caller-Inventory.md` is present and was read before this reconciliation update.

Repository searches covered definitions, constructors, imports, annotations, `PredicateResult`-shaped dictionaries/tuples, dataclasses/Pydantic/typed representations, factories/adapters, cache copies, serializers, schemas, snapshots, logs, tests, field consumers, and supporting-model names. Direct source inspection covered `engine.py`, registered predicates, Yoga/condition consumers, legacy runtime adapters, and predicate tests.

One safe in-memory Python snippet used `python -B` with `PYTHONDONTWRITEBYTECODE=1` to assess frozen assignment, nested aliasing, hash/equality, strict JSON behavior, invalid constructor values, and cold/warm cache aliasing. It created no repository artifact and cleaned its temporary in-process registration/cache. Targeted pytest was not retried: Audit-02 already established that the available interpreter has no `pytest`.

Counting policy:

- a model definition is counted only when a class/typed model defines the result shape;
- legacy tuple/dictionary equivalents are inventoried but not counted as `PredicateResult` definitions;
- construction paths are counted by distinct reachable producer/conversion/copy mechanism, not every syntactic return statement;
- deep-mutability issues are counted as ten distinct mutation/aliasing surfaces;
- serialization-impact count follows Audit-04's material serialization surfaces, while distinguishing the one direct complete-result serializer from eight downstream consumers.

## 3. Reconciliation with Audits 1–4

Audits 1 and 2 identify the same single class in `engine.py` and six registered IDs/five handlers returning it. Audit-05 confirms that no second typed definition exists and that all registered handlers import the canonical class from `systems.Parasara.engine.rules.engine` (`predicates.py:5,14-99`).

Audit-2 classifies the current implementation as initial/partial because version, status, validation, trace/error types, capability behavior, cache identity, and deep immutability are absent. Audit-05 confirms those gaps at the model level and adds empirical evidence that cached results share corruptible nested state.

Audit-3 reports five dormant tuple producers, four raw-boolean producers, four ad hoc dictionary contracts, three compatibility adapters, and eight information-loss boundaries. Those are alternate result representations, not additional `PredicateResult` class definitions. Audit-05 preserves Audit-3's active/dormant classification and focuses on how tuple/dictionary/evaluator conversion creates the canonical dataclass without validation or complete fields.

Audit-04 confirms 47 caller/consumer symbols or configuration surfaces: 22 direct, 25 indirect/dynamic, 18 active production, 27 test/tool-only, one dormant but referenced, and one confirmed unused. It confirms zero registered-handler bypasses, no result-field mutation callers, 23 direct migrations, and zero unknown migration statuses. Its nine serialization consumers expand Audit-05's impact assessment beyond the one direct complete-result serializer to downstream RuleMatch, snapshot, API/frontend, CI, determinism, and artifact paths.

No disagreement with Audits 1-4 was found.

## 4. PredicateResult Definitions and Canonical Model

### Model-definition inventory

| Definition | File | Symbol | Model Type | Active Status | Fields | Frozen | Deeply Immutable | Validation | Serialization | Producers | Consumers | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Canonical typed result | `systems/Parasara/engine/rules/engine.py:9-18` | `PredicateResult` | Standard-library dataclass | Canonical, active production and tests | 8 required fields | Yes, outer assignment only | No | None beyond Python constructor arity | No model API; test uses `asdict` + `json.dumps(default=str)` | Five registered handlers; evaluator branches; condition evaluator; cache `replace` | Evaluator/cache, condition/Yoga, tests | `tests/rules/test_predicate_result.py:14-74` |
| Legacy tuple equivalent | `systems/Parasara/engine/enrichments/yoga_engine.py:22-125` | Four `_eval_*` helpers and `_eval_condition` | `(bool, dict)` representation, not a class | Confirmed unused family | Match + evidence only | No | No | None | Ordinary tuple/dict | Dormant Yoga-local helpers | Dormant `_eval_condition` | No direct tests |
| Legacy dictionary equivalent | `systems/Parasara/engine/rules/runtime.py:76-108` | `evaluate_rule` output | Ad hoc dictionary, not a class | Active compatibility path | `match`, `evidence` | No | No | None | Ordinary dict/JSON-compatible only by convention | Legacy runtime | score wrapper, Career fallback, tests | `systems/Parasara/tests/test_rule_runtime.py:24-33` |

The actual `PredicateResult` definition count is **1**, and the active typed-definition count is **1**. `RuleMatch` in `systems/Parasara/engine/models.py` is a later-layer Pydantic rule model and is not an alternate predicate-result definition. Likewise, Yoga result dictionaries and public domain outputs are later-layer representations.

All eight dataclass fields have annotations but no defaults or default factories. `field` is imported at `engine.py:3` but unused. Construction therefore requires all eight positional/keyword arguments, while runtime types and semantic constraints remain unchecked.

## 5. Current Field and Type Assessment

### Field assessment

| Field | Current Type | Required Type/Semantics | Required | Default | Immutable | Canonically Normalized | JSON-Safe | Current Problems | Compliance | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| `predicate_id` | `str` annotation | Canonical registered ID | Yes | None | String itself immutable | No validation/normalization in model | Only if actually string | Blank/non-string accepted; alias result can disagree with lookup | PARTIAL | P1 |
| `predicate_version` | Absent | Explicit valid predicate implementation/library version | Yes | Absent | N/A | N/A | N/A | Mandatory identity/cache component missing | MISSING | P0 |
| `status` | Absent | Typed status consistent with `matched` and failure class | Yes | Absent | N/A | N/A | N/A | Cannot represent matched/unmatched/missing capability/invalid/error/timeout/skipped distinctly | MISSING | P0 |
| `matched` | `bool` annotation | Non-null factual boolean consistent with status | Yes | None | Scalar normally immutable | No validation | Only if actually boolean | Any object, including string/`None`, is accepted | PARTIAL | P1 |
| `inputs` | `Dict[str, Any]` | Canonical deeply immutable mapping with normalized values | Yes | None | No | No; `_normalize_inputs` returns original object | Not guaranteed | Top-level/nested mutation, aliasing, arbitrary keys/objects/cycles | NONCOMPLIANT | P0 |
| `evidence` | `Dict[str, Any]` | Structured deeply immutable factual JSON-safe mapping | Yes | None | No | No | Not guaranteed | Mutable/shared; handlers can embed AstroState edge dicts and arbitrary values | NONCOMPLIANT | P0 |
| `trace_steps` | `List[Dict[str, Any]]` | Ordered tuple of typed immutable `PredicateTraceStep` | Yes | None | No | No | Not guaranteed | Mutable list and dicts; no type/shape validation | NONCOMPLIANT | P1 |
| `errors` | `List[Dict[str, Any]]` | Ordered tuple of typed immutable `PredicateError` | Yes | None | No | No | Not guaranteed | Mutable untyped dicts; exception text exposed directly | NONCOMPLIANT | P1 |
| `cache_hit` | `bool` | Boolean observation, default false; must not change logical meaning | Yes | None | Scalar normally immutable | No validation | Only if actually boolean | Any value accepted; participates in equality | PARTIAL | P1 |
| `evaluation_time_ms` | `Optional[float]` | Optional nonnegative performance metadata, excluded/ignored for deterministic identity | Yes | None | Scalar normally immutable | No validation/normalization | Float normally JSON-safe except NaN/Infinity | Negative, string, NaN/Infinity accepted; participates in equality | PARTIAL | P2 |

Current fields present: **8**. Mandatory top-level Prompt-01 fields missing: **2** (`predicate_version`, `status`). Supporting types `PredicateStatus`, `PredicateError`, and `PredicateTraceStep` do not exist in production and are not referenced by the current class. Their detailed design belongs to Audit-06; at this boundary, `PredicateResult` fails to use them.

## 6. Required Prompt-01 Contract Comparison

Prompt-01's required-field section says every result must contain `matched`, `predicate_id`, `predicate_version`, `inputs`, `evidence`, `trace_steps`, `errors`, `cache_hit`, `evaluation_time_ms`, and `status`. The recommended shape gives `cache_hit=False`, `evaluation_time_ms=None`, and an illustrative status default, but exact status invariants must be defined. The current class contains eight names but only partially meets their semantics.

Implemented portions that should be preserved where compliant:

- one shared typed class is used by current registered handlers;
- `matched` and `predicate_id` are explicit fields;
- evidence, trace, errors, cache observation, and timing have explicit slots;
- outer field reassignment is blocked;
- empty handler evidence/traces/errors are normally represented as `{}`/`[]` rather than `None`;
- the evaluator uses `dataclasses.replace` rather than assigning `cache_hit` on the same outer instance.

Required gaps:

- explicit version and typed status;
- deep immutability and defensive normalization;
- typed immutable supporting models;
- validation of every field and cross-field invariant;
- canonical serializer/JSON-safe recursive normalization;
- telemetry-independent logical equivalence/hash;
- cache copies that do not share corruptible nested state;
- stable status/error behavior for missing capability, invalid input, exception, timeout, and skip.

Prompt-01 does not require the Python object itself to be hashable. It requires deterministic logical serialization/equivalence. Object hashability and logical hashing are therefore distinguished below.

## 7. Status and Matched Semantics

`matched` is constructor-mandatory because it has no default (`engine.py:10-18`), but runtime type/non-null validation is absent. The isolated constructor accepted `matched='yes'`.

`status` does not exist. Current evaluator behavior is:

- unknown predicate: `matched=False`, evidence reason, `errors=[]` (`engine.py:62-77`);
- legacy tuple false: `matched=bool(ok)`, no status/error (`80-93`);
- invalid handler return: `matched=False`, ad hoc error (`101-112`);
- handler exception: `matched=False`, raw exception string in error (`119-132`);
- missing condition type: `matched=False`, ID `UNKNOWN`, ad hoc error (`135-140`);
- logical condition: `matched=all/any`, flattened child errors (`142-159`);
- registered handlers: missing planet/data/capability generally becomes ordinary false with empty errors (`predicates.py:14-99`).

Four contradictory/ambiguous state-risk classes are counted:

1. unknown predicate is indistinguishable from a factual nonmatch through `matched` alone;
2. missing capability/data and invalid parameters are generally indistinguishable from unmatched;
3. invalid returns/exceptions are also `matched=False`, and consumers may ignore errors;
4. adding status without constructor invariants would permit `matched=True/status=unmatched` and equivalent contradictions.

Timeout and skipped states are unrepresentable. There is no timeout mechanism in the current evaluator. Callers rely primarily or exclusively on `.matched`: tests assert it (`test_predicate_result.py:19,35,50,64`), and Yoga reads `pr.matched` plus evidence but discards errors/trace (`yoga_engine.py:154-177`). Audit-04 confirms five paths treating errors or exceptions as unmatched and three typed-result callers discarding available errors. Introducing status can preserve factual booleans but must migrate those documented boundaries deliberately.

## 8. Deep Immutability Assessment

The outer dataclass is frozen. An isolated assignment to `result.matched` raised `FrozenInstanceError`. That guarantee stops at the field reference.

Ten distinct deep-mutability issues are verified or statically established:

1. `inputs` top-level dictionary can be edited through the result.
2. Nested lists/dicts/sets/custom objects inside `inputs` can be edited.
3. `evidence` top-level dictionary can be edited.
4. Nested evidence can be edited; aspect evidence contains original edge dictionaries (`predicates.py:18-42`).
5. `trace_steps` list can be appended/reordered/cleared.
6. Dictionaries and nested values inside trace steps can be edited.
7. `errors` list can be appended/reordered/cleared.
8. Dictionaries/details inside errors can be edited.
9. Arbitrary mutable domain/custom objects are accepted anywhere because annotations are not enforced or normalized.
10. `dataclasses.replace` makes shallow timing/cache copies that share all nested containers, so mutation of a cold result can corrupt the cached warm result (`engine.py:75-76,98-100,113-117,131`).

`_normalize_inputs` returns `params` unchanged (`engine.py:47-51`), so no defensive copy occurs. Registered handlers also store `params or {}` directly (`predicates.py:38-99`). The isolated check mutated a caller-owned nested list after construction and observed the change in `result.inputs`. It then mutated evidence, trace, and nested errors successfully.

The cache check registered an in-memory handler, evaluated it cold, mutated `cold.evidence['nested']`, then evaluated warm. The warm result contained the mutation. This proves caller-visible cache corruption, not merely a theoretical shallow-copy concern.

`dataclasses.asdict` recursively copies dataclass/container content for conversion, but that happens after the result has already been mutable and does not make the stored object immutable. `copy.copy`/`replace` remain shallow by default; no custom copy or normalization API exists.

## 9. Canonical Input and Evidence Normalization

There is no result-level canonical normalization. The only related code is `_normalize_inputs`, which returns the same dictionary, and `_cache_key`, which attempts `json.dumps(params, sort_keys=True, default=str)` then falls back to `str(params)` (`engine.py:39-51`). Cache-key formatting does not normalize the `PredicateResult.inputs` value.

Ten non-JSON-safe or nondeterministic value-risk classes are accepted without rejection/normalization:

1. sets and frozensets;
2. arbitrary enums;
3. dataclass instances;
4. Pydantic/AstroState or arbitrary custom objects;
5. dates and datetimes;
6. `Decimal` values;
7. UUID objects;
8. non-string or heterogeneous dictionary keys;
9. cycles/excessive recursion;
10. non-finite floats and custom string representations.

Lists/tuples/dictionaries are not defensively normalized; tuple versus list can therefore affect equality and output. Set ordering is not stabilized. Enum value/name policy is absent. Datetime format/timezone policy is absent. Decimal/float representation policy is absent. Stable AstroState node identities are not enforced. Cycles can make `asdict` or JSON conversion fail.

Logically equivalent dictionaries compare equal regardless insertion order, but `json.dumps(asdict(result), default=str)` in the existing test does not request sorted keys. Therefore byte output can differ for equal mappings constructed in different orders. `default=str` can include memory addresses or unordered set representations. `_cache_key` falls back to `str(dict)` if sorted JSON fails, which can also preserve insertion order or object-specific text.

The isolated strict `json.dumps(asdict(result))` failed with `TypeError` when evidence contained a set. The model itself accepted that evidence.

## 10. Equality, Hashing and Logical Identity

Standard dataclass equality compares every field recursively in declaration order. Thus logically identical results with different `cache_hit` or `evaluation_time_ms` compare unequal. The isolated comparison between otherwise identical objects differing only in `cache_hit` returned `False`.

`@dataclass(frozen=True)` generates `__hash__`, but normal results contain unhashable dictionaries/lists. The isolated `hash(result)` raised `TypeError`. The class is therefore nominally supplied with a generated hash method but practically unhashable for its declared field types.

No logical-identity projection, normalized dictionary, logical hash, cold/warm comparison helper, or telemetry exclusion exists. Cache keys are not result hashes and use process-local `id(astro)` plus name and params (`engine.py:39-44`).

Prompt-01 does not mandate Python object hashing. Safe completion requires deterministic logical equivalence/serialization excluding approved observation/performance fields; it does not necessarily require `hash(result)`.

## 11. Telemetry and Cache-Hit Semantics

`cache_hit` and `evaluation_time_ms` are required constructor arguments even though the recommended Prompt-01 shape provides defaults. Handlers construct `cache_hit=False` and `evaluation_time_ms=None`; the evaluator fills missing timing with `replace` and stores a `cache_hit=True` shallow copy (`predicates.py:38-99`; `engine.py:94-117`). Unknown/error results follow similar copy paths.

Warm cache retrieval returns the stored `cache_hit=True` object directly (`engine.py:55-57`). Cold and warm results therefore differ in equality. Timing is measured with `time.perf_counter`; repeated cold evaluations produce different values, and equality/snapshots include them unless a consumer manually excludes them.

Validation is absent. The isolated constructor accepted `cache_hit='no'` and `evaluation_time_ms=-2`. NaN, infinity, strings, and booleans-as-numbers are likewise not rejected by dataclass construction.

The cache observes neither result immutability nor logical equivalence. It also omits versions/context from the key, but the full cache audit belongs to Audit-11. Audit-05 records only the model/copy consequences: cached results can be corrupted, telemetry alters equality, and no logical view separates factual content from runtime observation.

## 12. Construction and Validation Paths

### Construction-path inventory

| File | Symbol | Construction Type | Fields Supplied | Validation | Mutable Data Risk | Status Consistency | Serialization Risk | Active Path | Migration Required | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| `systems/Parasara/engine/rules/predicates.py:14-47` | `aspect_exists` | Direct handler constructor | All current 8 | None | Params and matched edge objects shared | Status absent | Edge/custom values unrestricted | Active via `ASPECT` Yoga rule | Yes | P0 |
| `predicates.py:50-57` | `planet_in_house` | Direct handler constructor | All current 8 | None | Params shared; evidence mutable | Status absent | Arbitrary params accepted | Test/central API reachable | Yes | P1 |
| `predicates.py:60-67` | `house_occupant` | Direct handler constructor | All current 8 | None | Params/evidence mutable | Status absent | Arbitrary params accepted | Active Yoga | Yes | P1 |
| `predicates.py:70-82` | `functional_role` | Direct handler constructor | All current 8 | None | Params/evidence mutable | Status absent | Context-derived strings usually safe but unchecked | Active Yoga | Yes | P1 |
| `predicates.py:85-99` | `planet_exalted` | Three direct return branches, counted as one producer path | All current 8 | None | Params/evidence mutable | Missing planet and ordinary nonmatch identical | Metadata values unrestricted | Central API/test reachable | Yes | P1 |
| `systems/Parasara/engine/rules/engine.py:62-77` | `evaluate_predicate` unknown branch | Evaluator-created result | All current 8 | None | Inputs shared | Unknown represented as false without error/status | Inputs unrestricted | Active/reachable | Yes | P0 |
| `engine.py:80-93` | Tuple compatibility branch | Legacy conversion | Synthesizes all current 8 | Tuple arity only by unpack side effect | Tuple evidence reused | False/error distinctions unavailable | Evidence unrestricted | Reachable; no current production tuple handler | Yes/temporary compatibility | P1 |
| `engine.py:101-112` | Invalid-return branch | Evaluator-created failure | All current 8 | Tests result type only | Inputs shared; errors mutable | Invalid return represented as false | `str(type(out))` safe but ad hoc | Reachable | Yes | P1 |
| `engine.py:119-132` | Exception branch | Evaluator-created failure | All current 8 | None | Inputs/errors mutable | Exception represented as false | Raw exception message may be unsafe/sensitive | Active/reachable; tested | Yes | P0 |
| `engine.py:135-140` | Missing condition type | Positional direct constructor | All current 8 | None | Node params shared | Missing type represented as false | Params unrestricted | Reachable | Yes | P1 |
| `engine.py:142-159` | Logical `AND`/`OR` result | Aggregate direct constructor | All current 8 | None | Node params and rebuilt nested dict/list data mutable | Logical condition encoded as predicate; status absent | Child evidence/errors unrestricted | Active Yoga | Typed condition boundary required | P0 |
| `engine.py:75-76,98-100,113-117,131` | Cache/timing `replace` | Shallow derived copy | Existing fields with one telemetry replacement | None | Shares every nested object | No status invariant | Carries existing risk unchanged | Active | Deep-safe copy/logical view required | P0 |

Active/reachable construction mechanisms counted: **12**. No factory/builder, subclass, parser/deserializer, `from_dict`, `to_dict`, `to_json`, Pydantic validation, schema validation, or test fixture directly constructing an alternate typed model was found.

Every path can carry mutable/non-JSON-safe values. Every direct constructor can accept blank/non-string IDs, non-boolean match/cache flags, negative/invalid timing, and arbitrary nested objects. No path can supply predicate version/status because the fields do not exist. Error and trace content is always untyped.

## 13. Serialization and Public-Schema Impact

The only verified complete-result serializer is the test at `tests/rules/test_predicate_result.py:67-74`:

```text
d = asdict(res)
s = json.dumps(d, default=str)
```

It checks only that a dictionary contains `predicate_id` and that JSON returns a string. It does not assert stable bytes, normalized empty values, enum policy, round trip, strict JSON safety, or preservation of types. `default=str` hides unsupported objects rather than validating/normalizing them.

No production output assembler, log, snapshot, or schema was found serializing the complete `PredicateResult`. Searches of `systems/Parasara/schemas` and repository documentation schemas found no `PredicateResult`, `predicate_id`, `trace_steps`, or cache/timing fields in a public schema. Public output currently receives reduced rule/Yoga/domain dictionaries after upstream information loss, not the complete model.

Material serialization consumers affected: **9**, reconciled to Audit-04 section 12. One directly serializes the complete model (`test_predicate_result.py:67-74`). Eight serialize RuleMatch or downstream output/artifacts: `runtime.evaluate_rule_with_score`, `generate_snapshot.generate`, `runner_api.main`, the frontend POST route, `ci_snapshot_check.main`, `tests/determinism_test.py`, and two `generate_full_artifacts` stages. The downstream consumers do not currently receive the full `PredicateResult`, but model/condition migration can affect their evidence, status propagation, scores, or JSON shape.

Compatibility risks when the model becomes deeply immutable/typed:

- `dataclasses.asdict` behavior may differ or cease to be the canonical path;
- mapping/tuple/enums need a dedicated JSON-safe serializer;
- consumers currently expecting concrete `dict`/`list` may require serialized views;
- adding `predicate_version` and `status` changes complete internal dictionaries;
- telemetry must be excluded or normalized for deterministic snapshots;
- if predicate traces become public later, explicit schema versioning/approval is required.

No snapshot or public schema should be changed during this audit.

## 14. Producer and Consumer Compatibility

Producers:

- all five unique registered handlers directly construct the class (`predicates.py:14-99`);
- `evaluate_predicate` constructs unknown, tuple-adapted, invalid-return, and exception results (`engine.py:54-132`);
- `evaluate_condition` constructs missing-type and logical aggregate results (`engine.py:135-162`);
- cache/timing paths derive copies with `replace`.

Consumers:

- `evaluate_predicate` type-checks handlers and reads timing (`engine.py:78-118`);
- `_CACHE` stores/returns complete objects (`engine.py:24-25,55-57,75-76,113-131`);
- `evaluate_condition` reads child `.matched`, `.evidence`, `.errors`, `.predicate_id`, and timing, then discards complete children (`engine.py:142-159`);
- `evaluate_yoga_rules` reads only `.matched` and `.evidence` (`yoga_engine.py:154-177`);
- predicate tests read `.matched`, ID, cache flag, timing, and errors, then serialize via `asdict` (`test_predicate_result.py:14-74`).

Deep immutability may break code that assumes concrete dictionaries/lists even when current callers do not visibly mutate them. Typed status/errors/trace can be added compatibly only if callers stop interpreting all false states identically. Adding fields also makes every existing positional construction fragile, especially `engine.py:140`; keyword constructors dominate elsewhere but still must supply new mandatory fields or use validated factories/defaults.

Audit-04 closes the repository caller inventory at 47 surfaces and confirms that no caller mutates `.inputs`, `.evidence`, `.errors`, or `.trace_steps`. This lowers direct API-break risk from deep immutability, but it does not mitigate caller-visible cache corruption through returned nested containers. Audit-04 also confirms concrete dict/list and `asdict` compatibility concerns.

## 15. Existing Tests and Coverage Gaps

Existing coverage in `tests/rules/test_predicate_result.py` verifies:

- a matched registered predicate returns the class;
- cold/warm `cache_hit` values;
- one unmatched predicate;
- exception conversion produces a result with an error;
- a leaf condition returns the class;
- `asdict` plus `json.dumps(default=str)` produces a string.

It does not test direct constructor validation or model invariants. Of 16 model-test categories named by Audit-05, only successful construction (indirectly) and basic one-way JSON conversion have adequate minimal coverage. **14 model-test categories are missing or materially incomplete**:

1. default empty values;
2. frozen behavior;
3. deep immutability;
4. nested mutation/caller aliasing;
5. equality semantics;
6. practical hashing/logical hashing;
7. enum/status serialization;
8. serialization round trip;
9. canonical nested normalization;
10. invalid field rejection;
11. contradictory status/matched rejection;
12. cold/warm logical equivalence;
13. telemetry normalization/exclusion;
14. deterministic repeated byte-equivalent serialization.

Additional gaps include cache-corruption protection, cycles, non-JSON-safe values, non-finite floats, arbitrary objects, key ordering, immutable-copy behavior, version population, missing-capability representation, negative timing, and safe error messages. Likely focused location remains `tests/rules/test_predicate_result.py`, with cache/determinism integration placed according to later Audit-11 decisions. No tests were added.

## 16. Prompt-01 Compliance Matrix

### Compliance matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Single canonical typed definition | IMPLEMENTED | One class at `engine.py:9-18`; all handlers import it | `engine.py`, `predicates.py` | Preserve single authority | IN_SCOPE | P1 | No |
| `matched` field | PARTIAL | Present but unvalidated/non-null not enforced | `engine.py:11` | Validate boolean and status invariant | IN_SCOPE | P1 | Yes |
| Canonical `predicate_id` | PARTIAL | Present; blank/wrong types accepted; alias can disagree | `engine.py:12`; `predicates.py:12-46` | Validate canonical identity | IN_SCOPE | P1 | Yes |
| Explicit `predicate_version` | MISSING | No field or producer value | All predicate/evaluator/cache files | Add validated mandatory version | IN_SCOPE | P0 | Yes |
| Explicit typed `status` | MISSING | No field/model | All result constructors/consumers | Add status with matched invariant | IN_SCOPE | P0 | Yes |
| Canonical immutable inputs | NONCOMPLIANT | `Dict`; `_normalize_inputs` returns same object | `engine.py:13,47-51`; handlers | Defensive recursive canonicalization | IN_SCOPE | P0 | Yes |
| Canonical immutable evidence | NONCOMPLIANT | Mutable dict/nested edge references | `engine.py:14`; `predicates.py:18-42` | Typed/immutable normalized evidence | IN_SCOPE | P0 | Yes |
| Typed immutable trace steps | MISSING | `List[Dict]`; no supporting model | `engine.py:15`; constructors | Use approved Audit-06 model/tuple | IN_SCOPE | P1 | Yes |
| Typed immutable errors | MISSING | `List[Dict]`; raw exception strings | `engine.py:16,101-132` | Use approved error model and safe codes/details | IN_SCOPE | P1 | Yes |
| Cache observation without logical mutation | NONCOMPLIANT | Shallow `replace`; nested cache corruption proven | `engine.py:55-57,75-76,113-131` | Store/return deep-safe immutable logical content | IN_SCOPE | P0 | Yes |
| Optional performance metadata semantics | PARTIAL | Field exists; no validation; equality includes it | `engine.py:18`; tests | Validate and exclude/ignore in logical identity | IN_SCOPE | P1 | Yes |
| Deep immutability | NONCOMPLIANT | Frozen outer class with mutable shared containers | `engine.py:9-18`; all constructors | Recursively immutable values/defensive copies | IN_SCOPE | P0 | Yes |
| Constructor validation | MISSING | Dataclass annotations only | `engine.py:9-18` | Reject invalid fields/combinations | IN_SCOPE | P1 | Yes |
| Canonical serializer | MISSING | Only test `asdict` + `default=str` | `test_predicate_result.py:67-74` | One stable strict JSON-safe serializer | IN_SCOPE | P0 | Yes |
| Telemetry-independent equality/logical hash | MISSING | Dataclass equality includes telemetry; hash fails | `engine.py:9-18` | Define normalized logical comparison/hash as required | IN_SCOPE | P1 | Yes |
| Stable empty collections | PARTIAL | Handlers supply `{}`/`[]`; constructor has no defaults/validation | handlers; evaluator branches | Normalize empty collections consistently | IN_SCOPE | P2 | Yes |
| Public-schema exposure/versioning | IMPLEMENTED FOR CURRENT NON-EXPOSURE | No complete-result schema/output consumer found | schemas/output pipeline | Preserve non-exposure unless deliberately versioned | OUT_OF_SCOPE_FUTURE_STAGE | P2 | No |
| Complete caller reconciliation | IMPLEMENTED | Audit-04 classifies 47 surfaces, 23 direct migrations, and zero unknown migration statuses | Reports and consumers | Use the completed inventory during implementation planning | IN_SCOPE | P1 | No |

Summary counts:

| Measure | Count |
|---|---:|
| `PredicateResult` definitions | 1 |
| Active definitions | 1 |
| Active/reachable construction paths | 12 |
| Fields currently present | 8 |
| Mandatory top-level fields missing | 2 |
| Deep-mutability issues | 10 |
| Contradictory/ambiguous state risks | 4 |
| Non-JSON-safe/nondeterministic value-risk classes | 10 |
| Material serialization consumers affected | 9 |
| Missing/incomplete model-test categories | 14 |
| P0 findings | 5 |
| P1 findings | 10 |
| P2 findings | 4 |
| P3 findings | 0 |

## 17. Migration Risks and Priorities

The following numbered findings define the priority totals above.

1. **P0 — Cached results expose shared mutable nested state.** Shallow `replace` copies allow caller mutation to corrupt warm cache results (`engine.py:75-76,98-100,113-117,131`; isolated check).
2. **P0 — Mandatory `predicate_version` is absent.** Logical identity, registry compatibility, and cache isolation cannot satisfy Prompt-01 (`engine.py:9-18`).
3. **P0 — Mandatory status/failure semantics are absent.** Unknown, missing, invalid, and exception states collapse to false variants (`engine.py:62-77,101-140`; handlers).
4. **P0 — No canonical recursive serializer/normalizer exists.** Arbitrary accepted values can fail or serialize nondeterministically (`engine.py:39-51`; `test_predicate_result.py:67-74`).
5. **P0 — Nine serialization consumers amplify internal migration into snapshot, CI, API, determinism, and artifact regressions.** Audit-04 sections 10-13 trace this fan-out from `generate_snapshot.py:14-50` through runner/frontend and test/tool surfaces.
6. **P1 — `matched`, IDs, cache flags, and timing are unvalidated.** Invalid values were accepted by isolated construction (`engine.py:9-18`).
7. **P1 — Inputs are caller-owned mutable aliases.** `_normalize_inputs` is a no-op and handlers reuse params (`engine.py:47-51`; `predicates.py:38-99`).
8. **P1 — Evidence is mutable and may retain AstroState edge objects.** Aspect results share edge dictionaries (`predicates.py:18-42`).
9. **P1 — Trace steps are untyped mutable dictionaries/lists.** No supporting model or validation exists (`engine.py:15`; constructors).
10. **P1 — Errors are untyped mutable dictionaries and may expose raw exception messages.** (`engine.py:16,101-132`).
11. **P1 — Equality includes telemetry and no logical identity exists.** Cold/warm or repeated timing results compare unequal (`engine.py:9-18`; isolated check).
12. **P1 — Practical object hashing fails.** Generated hash encounters dict/list fields; no normalized logical hash exists (`engine.py:9-18`; isolated check).
13. **P1 — Twelve construction paths duplicate incomplete initialization rules.** Positional and direct constructors can diverge as fields are added (`engine.py:62-159`; `predicates.py:14-99`).
14. **P1 — Existing tests omit 14 required model categories.** (`tests/rules/test_predicate_result.py:14-74`).
15. **P1 — Condition aggregation constructs the same model for logical operators and drops complete child identity.** (`engine.py:135-159`).
16. **P2 — `cache_hit` and timing lack recommended defaults and validation.** Every producer must supply telemetry explicitly (`engine.py:17-18`; handlers).
17. **P2 — `asdict` plus `default=str` masks incompatibility instead of proving canonical JSON.** (`test_predicate_result.py:67-74`).
18. **P2 — Adding immutable mappings/tuples/enums may break concrete dict/list expectations.** Audit-04 confirms no mutation callers, but condition/Yoga consumers rebuild or inspect concrete collections (`engine.py:142-159`; `yoga_engine.py:154-177`).
19. **P2 — No caller test protects API/frontend behavior for typed errors, missing capabilities, or status propagation.** Audit-04 finds the public JSON fan-out but no API/frontend contract test for these states.

Migration must preserve the current working compatibility fields/behavior where they agree with authority. It must not redesign astrology semantics, decide `ASPECT` alias policy prematurely, or silently migrate/delete the legacy runtime. The highest risks are mutable cache contamination, changing false/error behavior when status is introduced, serializer incompatibility, and constructor proliferation.

## 18. Unresolved Architectural Questions

1. What exact `PredicateStatus` invariant is approved for successful evaluation: must status always be `matched`/`unmatched`, or is an `evaluated` status allowed? Prompt-01's recommended shape mentions `EVALUATED`, while its required semantic examples prefer matched/unmatched. Audit-06 must resolve this without permitting contradiction.
2. Should telemetry fields remain on `PredicateResult` but be excluded by a canonical logical projection, or should comparison be explicitly split into logical versus full diagnostic equality? Prompt-01 requires logical equivalence but does not require Python object hashing.
3. Which immutable mapping/sequence representation is approved, and what compatibility view should existing dict/list consumers receive? This belongs to implementation design after Audit-06/caller decisions.
4. How should arbitrary evidence values be handled: strict rejection, approved recursive normalization, or a bounded typed value model? Prompt-01 requires JSON-safe canonical output but does not prescribe the exact library.
5. Must `evaluation_time_ms` reject all non-finite/negative values, and is it serialized by default or omitted from deterministic snapshots?
6. Should predicate status/errors/traces remain internal or appear in frontend/API JSON? Audit-04 confirms the downstream surface but leaves this public-schema decision unresolved.

These questions do not block the current-model audit. They block safe implementation choices.

## 19. Audit-5 Conclusion

Audit-05 is complete and reconciled with all four prerequisite reports. The repository has one canonical active `PredicateResult` definition, eight current fields, two missing mandatory fields, and twelve reachable construction/copy paths. Its frozen dataclass is only shallowly immutable, performs no validation or canonical normalization, permits ten classes of non-JSON-safe/nondeterministic values, includes telemetry in equality, is practically unhashable, and exposes cache contents to nested mutation. Audit-04 confirms 47 caller/consumer surfaces and nine material serialization consumers that must be considered during migration.

No production code, tests, rules, schemas, snapshots, prior reports, or other audit files were modified. No Audit-06 work was started.
