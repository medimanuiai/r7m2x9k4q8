# Prompt-01 Audit-06: Supporting Models

## 1. Executive Summary

Audit-6 is **COMPLETE**. Repository-wide inspection found **zero predicate-status models, zero typed predicate-error models, and six trace-model or trace-shape candidates**. No existing type can be reused as `PredicateStatus`, `PredicateError`, or `PredicateTraceStep` without violating ownership, immutability, or semantics. Prompt-01 therefore requires three predicate-specific supporting models.

The current contract stores errors and trace steps as mutable dictionaries (`systems/Parasara/engine/rules/engine.py:15-16`). Three distinct dictionary-based predicate-error patterns occur in the central evaluator: invalid return type, raw exception text, and missing condition type (`engine.py:109,127,140`). The only populated `trace_steps` shape is a condition-child summary (`engine.py:153-159`); registered predicate handlers produce empty lists (`systems/Parasara/engine/rules/predicates.py:38-99`).

No predicate status exists, so all successful false results and most failures collapse into `matched=False`. Unknown predicates even return `errors=[]` (`engine.py:62-77`). There is no invariant that could prevent `matched` and a future `status` from contradicting each other.

The closest typed candidate, `RuleMatch` (`systems/Parasara/engine/models.py:45-58`), belongs to the later rule layer, is mutable under its current Pydantic configuration, and provides only an optional opaque `trace_id`. It must remain separate. Aspect, Shadbala, Yoga, and Career trace dictionaries are likewise layer-specific and unsuitable as predicate trace steps.

Four Prompt-01-relevant nondeterministic mechanisms were found: `time.perf_counter()` durations, Yoga UUID4 trace IDs, set-to-list ordering in Yoga evidence/output, and process-local `id(astro)` cache identity (`engine.py:39-44,61-159`; `yoga_engine.py:14-15,51,173-177`). No reusable deep-freeze or canonical serializer exists. `tools/ci_snapshot_check.normalize` is a useful comparison helper but rounds floats, accepts only JSON-like dict/list/float values, leaves unsupported values untouched, and does not freeze or defensively copy all inputs (`systems/Parasara/tools/ci_snapshot_check.py:20-35`).

The audit records **4 P0, 6 P1, 4 P2, and 2 P3 findings**. The primary unresolved decision is the exact `PredicateStatus` invariant: Prompt-01 lists `evaluated`, `matched`, and `unmatched`, while also requiring noncontradictory `matched/status` combinations.

## 2. Audit Scope and Method

The audit was read-only except for this report. It inspected:

- `Documentation/AI-Prompt/Jyothishyam Master Architecture Specification v1.0.docx` and `Documentation/AI-Prompt/Prompt-01.docx` by reading their document XML;
- completed reports Audit-01 through Audit-05 under `systems/Parasara/Documentation/Engine/Prompt-01/Reports/`;
- production Python under `systems/Parasara`, including central predicates/conditions, legacy runtime, Yoga, enrichments, domain output, schemas, tools, and serializers;
- repository tests, fixtures, artifacts, YAML/JSON, and test framework utilities;
- repository-wide definitions of enums, dataclasses, Pydantic models, typed dictionaries, named tuples, status/error/trace fields, clocks, UUIDs, process identity, set ordering, normalization, serialization, and hashing.

Counts use distinct repository-defined models or stable dictionary shapes, not every construction occurrence. A trace candidate is counted when it is a typed model with trace fields or a repeated, identifiable trace dictionary shape. Five of the six trace candidates are dictionary-based trace/trace-bearing shapes; only one is stored specifically in `PredicateResult.trace_steps`. Scalar error/evidence occurrences are recorded but are not counted as typed error models. “Reusable” means usable for Prompt-01 without extension; candidates requiring semantic or structural changes are not counted.

The targeted test command was safe and non-generating. It could not run because the current Python environment has no `pytest`. Snapshot generators were not run because they write files.

## 3. Reconciliation with Audits 1–5

Audits 1 and 2 found one central registry, six registered IDs/five handlers, and one shared `PredicateResult`. Audit-6 agrees: all registered handlers import the same dataclass and none imports a status/error/trace supporting type (`systems/Parasara/engine/rules/predicates.py:5,12-99`).

Audit-3 found legacy tuples, booleans, dictionaries, compatibility adapters, and information-loss boundaries. Audit-6 treats these as representations, not supporting-model definitions. The legacy rule error dictionary `{'error': 'evaluation_failed'}` is rule evidence (`systems/Parasara/engine/rules/runtime.py:237-240`), so it is retained as a separate error shape rather than counted as a predicate-error model.

Audit-4 is present, and Audit-5 has already been reconciled with it. Audit-4 confirms that condition aggregation reads child errors and builds summaries, Yoga keeps only match/evidence and creates random trace IDs, and downstream Career/output consumers do not preserve predicate status/error/trace data (`Audit-04-Complete-Caller-Inventory.md:39-45,55-80,158-169`). Audit-6 incorporates those caller findings.

Audit-5 found one eight-field shallow-frozen `PredicateResult`, missing `predicate_version` and `status`, with mutable dictionary/list fields and no canonical serializer. Audit-6 confirms its supporting-type conclusion and adds the cross-layer comparison: `RuleMatch`, Aspect traces, Shadbala traces, Yoga IDs, and Career IDs are not compatible substitutes. Audit-5's open `evaluated` versus `matched`/`unmatched` status question remains unresolved because neither authoritative document supplies a complete invariant.

No disagreement changes a prior numeric inventory. Newly enumerated evidence consists of six cross-layer trace candidates, four nondeterministic mechanisms, and two non-predicate normalization/comparison helpers that earlier audits did not need to classify.

## 4. Existing Supporting-Model Inventory

| Model | File | Symbol | Layer | Model Type | Fields | Immutable | Deterministic | JSON-Safe | Producers | Consumers | Tests | Reuse Recommendation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Predicate error dictionaries | `systems/Parasara/engine/rules/engine.py:109,127,140` | `evaluate_predicate`; `evaluate_condition` | Predicate/condition | Ad hoc `dict` | `error`; optional `type` | No | Raw exception/type rendering not guaranteed stable | Not guaranteed | Central evaluator | Condition aggregation; predicate tests; otherwise discarded | Exception test checks only nonempty list | `PREDICATE_SPECIFIC_MODEL_REQUIRED` |
| Condition child trace summary | `systems/Parasara/engine/rules/engine.py:153-159` | `evaluate_condition` | Condition | `dict` in list | `predicate_id`, `matched`, `errors`, `evaluation_time_ms` | No | No; duration varies | Not guaranteed through nested errors | Condition evaluator | Parent condition result; Yoga discards it | No field assertions | `PREDICATE_SPECIFIC_MODEL_REQUIRED` for predicate steps; later `ConditionTraceStep` separate |
| `RuleMatch` | `systems/Parasara/engine/models.py:45-58` | `RuleMatch` | Rule | Pydantic `BaseModel` | Rule identity, match/scoring, mutable context/evidence/provenance, optional `trace_id`, timing | No frozen config | Optional caller-supplied ID; no policy | Pydantic-supported values only; `Any` dictionaries weaken guarantee | `evaluate_rule_with_score` | Career, snapshots, API | Rule runtime/Career/snapshot tests | `KEEP_SEPARATE` |
| Yoga match trace-bearing dictionary | `systems/Parasara/engine/enrichments/yoga_engine.py:169-178` | `evaluate_yoga_rules` | Yoga | Ad hoc `dict` | Yoga fields plus `evidence`, random `trace_id` | No | No; UUID4 and set ordering | Usually, not validated | Yoga engine | `AstroState.enrichments`, Yoga tests | Presence only | `KEEP_SEPARATE` |
| Aspect edge trace dictionary | `systems/Parasara/engine/enrichments/aspects.py:62-90` | `compute_aspect_graph` | Enrichment | Ad hoc `dict` | From/to longitude, delta, aspect angle, orb, match | No | Yes for stable ordered AstroState/config | Scalar JSON-like values | Aspect enrichment | Predicates, Shadbala, snapshots | Aspect/enrichment tests, no immutability | `KEEP_SEPARATE` |
| Shadbala calculation trace dictionary | `systems/Parasara/engine/enrichments/shadbala.py:30-170` | component calculators | Enrichment | Ad hoc `dict` | `component`, `value`, `formula_used`, `input_factors`, `evidence` | No | Generally yes for stable input/config order | Usually, not validated | Shadbala functions | Enrichments, tests/artifacts | Component/integration tests | `KEEP_SEPARATE` |
| Career domain trace-bearing dictionary | `systems/Parasara/engine/interpreters/career.py:108-116` | `interpret_career` | Domain | Ad hoc `dict` | Domain score/confidence/evidence plus constant `trace_id` | No | Yes, but constant ID is not unique identity | JSON-like values | Career interpreter | output/snapshots/API | Career and golden tests | `KEEP_SEPARATE` |
| JSON-schema validation errors | `systems/Parasara/engine/adapter/surya_adapter.py:22-25` | `jsonschema.ValidationError` instances | Input adapter | External exception objects | Library-defined message/path/schema context | No contract here | Ordering/message library-dependent | No direct JSON guarantee | JSON Schema validator | Adapter raises `ValueError` text | Adapter validation tests | `KEEP_SEPARATE` |

No `PredicateStatus`, `PredicateError`, `PredicateTraceStep`, error-code enum, immutable mapping wrapper, deep-freeze type, or predicate serializer was found. No test-only duplicate supporting type was found.

## 5. PredicateStatus Assessment

There is no status enum, literal type, constant catalog, Pydantic field, or status factory in Parasara. Repository-wide enum discovery found only the unrelated Surya Siddhanta `Nakshatras` enum (`systems/SuryaSiddhanta/ndastro_engine/nakshatra_enum.py:40`). The `lord_status` strings in `runtime.py:192` are a rule kind, not evaluation status.

| Required Status | Existing Representation | Serialized Value | Semantics Defined | Producers | Consumers | Compliance | Gap | Priority |
|---|---|---|---|---|---|---|---|---|
| `matched` | `matched=True` boolean only | `true` | Factual boolean only | Handlers/evaluators | Conditions, Yoga, tests | PARTIAL | No typed status or invariant | P0 |
| `unmatched` | `matched=False` boolean only | `false` | Indistinguishable from most failures | Handlers/evaluators | Conditions, Yoga, tests | NONCOMPLIANT | Failure and factual false collapse | P0 |
| `missing_capability` | Often ordinary false/empty evidence | None | Not defined | Some predicates implicitly | Consumers treat as unmatched | MISSING | No detection/status/serialization | P0 |
| `invalid_parameters` | False, exception, or handler-specific evidence | None | Not defined | Evaluator/handlers | Consumers treat as unmatched | MISSING | No validation/status | P0 |
| `error` | `matched=False` plus mutable error dict | None as status | Ad hoc branch behavior only | Evaluator | Test reads list; Yoga discards | NONCOMPLIANT | No typed error status | P0 |
| `timeout` | None | None | No timeout mechanism | None | None | MISSING | State and runtime policy absent | P1 |
| `skipped` | None at predicate layer | None | Master architecture discusses skipped rule/dependency paths, not predicate invariant | None | None | MISSING | Predicate meaning/producer policy absent | P1 |

There is no case-sensitivity, equality, hashing, invalid-value, alias, JSON-enum, producer, or consumer behavior to assess for an existing status model. A future plain enum would normally provide member equality/hash but still needs explicit value serialization and rejection rules.

Prompt-01 lists `evaluated`, `matched`, `unmatched`, `missing_capability`, `invalid_parameters`, `error`, `timeout`, and `skipped` and recommends a default `PredicateStatus.EVALUATED`. It also gives `matched=True/status=matched` and `matched=False/status=unmatched` examples. No authoritative consistency rule says whether `evaluated` is a transient/internal state, an allowed final success status, or an umbrella status. The current constructor cannot create contradictions only because status is absent; adding an unconstrained field would permit them immediately. No factory or post-init validation exists.

## 6. PredicateError Assessment

| Required Field or Behavior | Existing Support | Evidence | Safety Concern | Required Change | Compliance | Priority |
|---|---|---|---|---|---|---|
| Stable code | Lower-case strings sometimes placed in `error` | `engine.py:109,140` | Key/value vocabulary is inconsistent and incomplete | Typed stable code catalog/value policy | PARTIAL | P1 |
| Safe message | Exception text copied verbatim | `engine.py:117-129` | May expose paths, values, implementation details, or secrets | Safe public message plus secure internal logging boundary | NONCOMPLIANT | P0 |
| Predicate ID | Not inside error object | Parent result has ID except missing-type path uses `UNKNOWN` | Flattened/forwarded errors lose unambiguous origin | Mandatory canonical predicate ID | MISSING | P1 |
| Structured details | Only invalid-return `type` | `engine.py:109` | Arbitrary unvalidated dictionaries; no schema | Immutable canonical details mapping | PARTIAL | P1 |
| Recoverability | None | All error branches | Callers cannot decide fail/continue/retry | Explicit recoverable field and semantics | MISSING | P1 |
| Deep immutability | None | List/dict annotations at `engine.py:16` | Caller/cache mutation and aliasing | Frozen model plus recursive normalization | NONCOMPLIANT | P0 |
| Deterministic serialization | None | `asdict` + `json.dumps(default=str)` only in test | Raw/custom repr and mutable ordering can vary | Canonical serializer shared with result | NONCOMPLIANT | P1 |
| JSON safety | Not enforced | `Dict[str, Any]`; raw strings happen to serialize | Future details may contain arbitrary objects/cycles | Reject or canonically normalize supported values | PARTIAL | P1 |
| Exception wrapping | Broad `except Exception` creates dictionary | `engine.py:117-129` | Exception class/code lost; raw message exposed | Stable `PREDICATE_EXCEPTION`, safe message/details, strict-mode policy | NONCOMPLIANT | P0 |
| Stack-trace exclusion | No traceback is explicitly added | `engine.py:127` | Raw exception text can still leak sensitive context; no public/internal boundary | Explicit exclusion test and logging policy | PARTIAL | P1 |
| Layer separation | Predicate, condition, rule, and adapter shapes differ | `engine.py`; `runtime.py:237-240`; `surya_adapter.py:22-25` | Merging them would couple unrelated lifecycle and recovery semantics | Predicate-specific type; translate only at boundaries | PARTIAL | P2 |

No stack trace is currently inserted into `PredicateResult`, but static analysis cannot guarantee that `str(e)` itself contains no sensitive multi-line details. The report intentionally does not reproduce exception contents.

The concrete dictionary variants are:

- `evaluate_predicate` invalid-return handling (`engine.py:102-112`) creates required-at-that-site keys `error` and `type`, both strings, with no defaults, predicate ID, details container, or recoverability. The parent `PredicateResult` supplies the requested predicate name. Condition aggregation and the predicate-result serializer test are potential consumers; Yoga discards the list.
- `evaluate_predicate` exception handling (`engine.py:117-129`) creates only `error`, whose value is raw `str(e)`. It has no stable code or safe-message separation. The parent carries the predicate name; the direct exception test checks only that the list is nonempty (`tests/rules/test_predicate_result.py:39-55`).
- `evaluate_condition` missing-type handling (`engine.py:135-140`) creates only `error='missing_type'` and places it under a parent result whose predicate ID is `UNKNOWN`. No originating AST/condition node identity or recoverability is retained.
- The legacy rule path's `{'error':'evaluation_failed'}` (`runtime.py:237-240`) is evidence inside a rule result, not a `PredicateResult.errors` entry. It is a separate fixed-message compatibility shape and must not be treated as a reusable predicate-error model.

All variants are mutable, have no declared required/optional schema or defaults beyond their construction sites, and are serialized only by ordinary dict/Pydantic/downstream JSON behavior.

## 7. PredicateTraceStep Assessment

| Model | Layer | Identity | Step Ordering | Parent/Child Support | Timing Fields | Randomness | Immutable | Serialization | Predicate Suitability | Recommendation | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Condition child summary dict | Condition | Predicate ID only; no step ID | Child list order | Nesting implied, no IDs | `evaluation_time_ms` | Varying duration | No | `asdict` path only | Missing operation/inputs/result/evidence/parent ID and mixes condition ownership | `PREDICATE_SPECIFIC_MODEL_REQUIRED` | P1 |
| `RuleMatch` | Rule | Optional opaque `trace_id` | None | None | Optional integer ms | Caller-controlled | No | Pydantic dump | Scoring/rule semantics and no step fields | `KEEP_SEPARATE` | P2 |
| Yoga match dict | Yoga | UUID4 | Rule-registry insertion order; nested set order unstable | None | None | UUID4 | No | AstroState enrichment/test serialization; current central snapshot emits `yogas: []` | Random later-layer aggregate, not a step | `KEEP_SEPARATE` | P1 |
| Aspect trace dict | Enrichment | None | Planet nested-loop/list order | None | None | None | No | Embedded dictionary | Useful evidence shape but enrichment-owned and lacks step identity/parent/outcome contract | `KEEP_SEPARATE` | P2 |
| Shadbala trace dict | Enrichment | Component name only | Explicit append/extend order | Nested evidence only | None | None | No | Embedded dictionary | Calculation-specific fields; no predicate identity/parent | `KEEP_SEPARATE` | P2 |
| Career result trace ID | Domain | Constant `career_001` | None | None | None | None | No | Public/snapshot dictionary | Not unique and domain-owned | `KEEP_SEPARATE` | P3 |

No candidate supports the recommended complete predicate-step shape: deterministic `step_id`, `operation`, description, immutable inputs, result, immutable evidence, and optional parent step ID, duration, cache hit, and AST node ID. None can directly express all five example operations (capability check, planet lookup, actual-house read, comparison, result production) without inventing ad hoc keys.

The existing condition summary can describe a child outcome but not the operation that produced it. It also embeds mutable child error lists by reference and records nondeterministic performance time. Predicate handlers currently emit no trace operations at all.

Candidate ownership and exposure details are:

- The condition evaluator owns the child-summary dictionary (`engine.py:135-162`). Its fields are `predicate_id: str`, `matched: bool`, `errors: list[dict]`, and `evaluation_time_ms: float|None`. List position supplies ordering; it has no step/parent/run/AST/rule ID, inputs, observation details, timestamps, or explicit outcome beyond `matched`. It is consumed by the parent result and then discarded by Yoga. No test inspects its fields, and no complete predicate result currently reaches public output.
- `RuleMatch` is owned by the legacy rule runtime (`models.py:45-58`; `runtime.py:242-269`). `rule_id` is a rule reference, while `trace_id` is optional and unconstrained. It has no step ordering, parent, AST node, timestamp, or error reference. Runtime serializes it to a dict; artifact generation writes those dictionaries to `rule_traces.json` (`tests/testing_framework/generate_full_artifacts.py:51-79`). Career consumes selected fields but does not propagate this trace ID to its domain result.
- Yoga owns the match dictionary (`yoga_engine.py:128-188`), with Yoga/rule identity, match, planets/houses/aspects/evidence, and a UUID4 `trace_id`. It has no parent, step sequence, AST node, timestamp, duration, or error reference. Tests assert ID presence (`tests/enrichments/test_yoga_engine_rule_driven.py:34-37`), but the current central snapshot explicitly emits an empty Yoga list (`tools/generate_snapshot.py:25-32`), so static evidence does not show this random ID in that public output path.
- Aspect enrichment owns the trace dictionary (`aspects.py:22-100`), whose scalar/list fields capture source planet/sign/degree, configured offset, target sign, matched planets, and explanation. Edge-list order is the sequence; there are no IDs, parents, errors, AST/rule references, timestamps, or durations. It is embedded in aspect edges, asserted by aspect tests (`tests/enrichments/test_aspects.py:28-46`), consumed by predicates/Shadbala, and included in snapshot diagnostics (`tools/generate_snapshot.py:25-31`).
- Shadbala owns component trace dictionaries (`shadbala.py:30-170`) with `component`, `value`, `formula_used`, `input_factors`, and nested `evidence`. Append/extend order supplies sequence; there are no IDs, parents, error references, AST/rule references, timestamps, or durations. Component/integration tests inspect the calculation trace (`tests/enrichments/test_shadbala_golden.py:18`), and planet-strength diagnostics can reach snapshots.
- Career owns the domain result dictionary (`career.py:108-116`). It has a constant `trace_id='career_001'` but no trace steps, parent, error/AST/rule link collection, timestamp, or duration. It is covered by Career/golden tests and reaches the public snapshot/API chain. The constant is deterministic but cannot uniquely identify different evaluations.

No inference-result, inference-trace, run-trace, condition-trace class, parent/child trace-ID model, or trace-store model exists in production. Documentation specifies future trace hierarchy, but documentation requirements are not counted as existing models.

## 8. Error Codes and Exception Safety

| Candidate Code | Existing Representation | Assessment | Ownership Decision |
|---|---|---|---|
| `INVALID_PARAMETERS` | No stable code | Explicit Prompt-01 recommended code; behavior absent | Predicate-specific |
| `MISSING_CAPABILITY` | No stable code | Explicit Prompt-01 recommended code and master typed-runtime requirement | Predicate-specific, capability policy still needed |
| `MISSING_PLANET` | Legacy `planet_not_found` evidence in `runtime.py:86-89`; registered handlers often return false | Recommended candidate, not implemented as error | Predicate-specific only when absence is invalid/missing capability rather than factual nonmatch |
| `MISSING_HOUSE` | None | Recommended candidate | Architectural semantics required |
| `MISSING_VARGA` | None | Recommended candidate | Capability/error boundary required |
| `MISSING_ASPECT_GRAPH` | ASPECT handler returns ordinary unmatched/empty evidence | Recommended candidate | Predicate capability error |
| `UNKNOWN_REFERENCE` | Unknown condition type/predicate appear as evidence reasons | No stable error code | Compilation/condition ownership may be more appropriate |
| `UNKNOWN_PREDICATE` | `reason='unknown_predicate'`, `errors=[]` at `engine.py:62-77` | Prompt-01 implies deterministic error; master says unknown predicates are rule-definition errors | Prefer loader/compiler error; evaluator still needs safe defensive result policy |
| `INVALID_RETURN_TYPE` | `{'error':'invalid_return_type','type':str(type(out))}` | Concept exists with wrong key/type/safety contract | Temporary evaluator compatibility error |
| `PREDICATE_EXCEPTION` | `{'error':str(e)}` plus `reason='predicate_error'` | Recommended code missing; unsafe message | Predicate-specific wrapper plus internal logging |
| `PREDICATE_TIMEOUT` | None | Explicit recommended/master typed-runtime code; no timeout mechanism | Predicate/evaluation context policy required |

Only `invalid_return_type`, `missing_type`, and `evaluation_failed` resemble codes, and none implements the Prompt-01 typed contract. `unknown_predicate`, `unknown_condition_type`, `predicate_error`, and `planet_not_found` are evidence reasons rather than error codes. Code spelling/case is not centralized.

Raw exceptions are caught at `engine.py:117-129` and copied with `str(e)`. The legacy runtime catches broadly and emits the fixed `evaluation_failed` string (`runtime.py:237-240`), which is safer publicly but loses classification, origin, and debugging correlation. Adapter schema errors are joined into a `ValueError` message (`surya_adapter.py:22-25`) and must remain an input-layer concern.

## 9. Trace Identity and Determinism

| Mechanism | Evidence | Classification | Effect |
|---|---|---|---|
| `time.perf_counter()` durations | `engine.py:61-64,83,96,102,120,136-159` | `PERFORMANCE_ONLY_NONDETERMINISM` until included in equality/serialization; currently generated dataclass equality makes it observable | Repeated logical results and condition trace summaries differ |
| `uuid.uuid4()` Yoga IDs | `yoga_engine.py:14-15,177` | `TRACE_ONLY_NONDETERMINISM`, but embedded output can make snapshots/logical JSON differ | Same Yoga evaluation receives a different trace identity |
| `list(set(...))` in Yoga evidence/output | `yoga_engine.py:51,173` | `LOGICAL_NONDETERMINISM` | Matched-planet/evidence order can vary and feeds trace-bearing output |
| Process-local `id(astro)` cache key | `engine.py:39-44` | `LOGICAL_NONDETERMINISM` for cache/telemetry identity, not factual match | Cache-hit behavior is process/object-instance dependent and can affect serialized result/trace telemetry |

The count of Prompt-01-relevant nondeterministic mechanisms is **4**. `datetime.utcnow()` in Dasha (`systems/Parasara/engine/dasha/vimshottari.py:64-66`), snapshot-approval time, test PR branch time, and performance-test clocks are `UNRELATED_TO_PROMPT_01` for this supporting-model audit.

Three candidate trace shapes are deterministic for stable inputs: Aspect trace dictionaries, Shadbala component trace dictionaries, and the Career constant trace field. The Career value is deterministic but not a valid identity because every result reuses `career_001`. `RuleMatch.trace_id` is optional and unconstrained, so determinism is unknown. Condition summaries are performance-variable and Yoga IDs are random.

Predicate trace identity is absent. There is no step ID, run ID, parent ID, logical hash, or AST-node linkage. Trace steps participate in generated `PredicateResult` equality and attempted hashing, while Yoga/Career trace IDs enter embedded JSON and snapshots. No trace-ID algorithm is proposed here.

## 10. Immutable and Canonical Data Utilities

| Utility | File | Supported Types | Deep Freeze | Defensive Copy | Deterministic | JSON-Safe | Current Consumers | Predicate Suitability | Risk |
|---|---|---|---|---|---|---|---|---|---|
| `_normalize_inputs` | `systems/Parasara/engine/rules/engine.py:47-51` | Any supplied params dict | No | No; returns same object | No guarantee | No guarantee | `evaluate_predicate` | Not suitable | Aliasing and arbitrary values persist |
| `_cache_key` JSON formatting | `systems/Parasara/engine/rules/engine.py:39-44` | Dicts accepted by JSON/default string fallback | No | Serialization creates text only | Partial; sorted keys but `default=str` and fallback repr | Produces a string, masks unsupported objects | Predicate cache | Not suitable | Memory addresses/custom repr, process ID, semantic coercion |
| `normalize` | `systems/Parasara/tools/ci_snapshot_check.py:20-30` | Dict, list, float, pass-through scalars/others | No | Recursively rebuilds dict/list; other objects shared | Partial; sorted dict keys and rounded finite floats | Only for already JSON-like inputs | `compare_json`, diagnostic printing | Not suitable as-is | Float rounding changes meaning; no tuple/set/enum/dataclass/datetime/custom/cycle policy |
| `_clean` | `tests/testing_framework/json_compare.py:12-25` | Dict, list, pass-through values | No | Rebuilds dict/list | Preserves insertion/list order; removes keys | Only for JSON-like inputs | `compare_json` | Not suitable | Test-only ignore semantics intentionally discard data |
| Sorted JSON snapshot output | `systems/Parasara/tools/generate_snapshot.py:43-50` | Existing output dictionary | No | Serialization only | Key order stable, values not canonicalized | Only if input already safe | Snapshot/public output | Not a nested-value utility | Does not validate enums, sets, datetimes, NaN, custom values, cycles |
| Determinism-test hash | `tests/determinism_test.py:7-15` | Generated snapshot | No | Serialization only | Sorted keys; default numeric/Python JSON behavior | Only if input already safe | One test | Test oracle only | Generator writes output; no predicate isolation or unsupported-value policy |

No utility freezes mappings, converts lists to immutable tuples as a contract, normalizes sets, handles enums/dataclasses/datetimes/Decimals explicitly, rejects cycles with a typed error, or provides a stable predicate digest. No reusable canonicalization utility is counted. `ci_snapshot_check.normalize` is a useful design reference only; adapting it would require semantic changes and moving it out of a CI tool.

## 11. Duplicate Models and Reuse Opportunities

| Candidate | Overlap | Classification | Reason |
|---|---|---|---|
| `RuleMatch` | Matched flag, evidence, trace ID, timing | `KEEP_SEPARATE` | Later rule/scoring layer; mutable nested fields; lacks status/error/step semantics |
| Condition child summary | Predicate ID, match, errors, timing | `PREDICATE_SPECIFIC_MODEL_REQUIRED` | It is a lossy condition projection; predicate steps and future `ConditionTraceStep` have different owners |
| Yoga match dictionary | Match, evidence, trace ID | `KEEP_SEPARATE` | Yoga aggregate with random identity and public enrichment exposure |
| Aspect trace dictionary | Operation observations and result | `KEEP_SEPARATE` | Enrichment calculation evidence, not predicate evaluation lifecycle |
| Shadbala trace dictionary | Operation, inputs, result/evidence | `KEEP_SEPARATE` | Strength-calculation schema and mutable nested evidence |
| Career trace field | Stable-looking trace ID | `KEEP_SEPARATE` | Domain aggregate and nonunique constant identity |
| Adapter validation errors | Code/message/details-like information | `KEEP_SEPARATE` | External input-validation exception semantics and unsafe library-shaped context |
| `ci_snapshot_check.normalize` | Recursive dict/list normalization | `REUSE_WITH_PROMPT_01_EXTENSION` only as design logic, not as-is API | Requires new ownership and policies for immutable values, unsupported types, cycles, numerics, enums, dates |
| Predicate status/error/trace types | No compatible existing type | `PREDICATE_SPECIFIC_MODEL_REQUIRED` | Prompt-01 lifecycle and layer boundary are unique |

Reusable supporting-model count is **0**. Models requiring Prompt-01 extension count is **0** because extending `RuleMatch` or enrichment traces would violate boundaries; the one extension candidate is a utility, not a model. Predicate-specific models required count is **3**.

## 12. Construction and Consumption Paths

| Path | Construction/Consumption | Information/Safety/Ordering | Migration Need |
|---|---|---|---|
| `predicates.py:12-99` registered handlers | Construct `PredicateResult` with empty mutable trace/error lists and caller params/evidence dicts | No supporting types, defensive copy, or trace operations | Construct typed status/errors/traces and canonical values |
| `engine.py:52-130` `evaluate_predicate` | Constructs unknown/tuple/invalid-return/exception results; copies cached result with `replace` | Raw exception exposure; shallow replacement; variable timing; cache identity process-local | Central factory/validation/error translation/serializer boundary |
| `engine.py:135-162` `evaluate_condition` | Recurses, flattens child errors, rebuilds child summary dicts | Loses full child traces/cache/version/status; duration varies; nested references mutable | Separate typed `ConditionResult`/trace and preserve predicate result semantics |
| `yoga_engine.py:128-188` | Reads only `.matched/.evidence`, discards errors/traces, makes UUID trace ID | Failure becomes nonmatch; random/set order enters enrichment | Explicit status/error policy and separate deterministic Yoga trace |
| `runtime.py:111-269` | Builds mutable `RuleMatch`, converts broad exception to fixed evidence, Pydantic-dumps to dict | Predicate information unavailable; errors mixed into evidence | Keep rule model separate; translate typed predicate inputs intentionally |
| `career.py:8-116` | Consumes rule dictionaries, preserves only matched contributions, emits constant trace ID | Predicate errors/status/traces unavailable; public domain trace is nonunique | Preserve scoring while adding deliberate upstream error policy |
| `test_predicate_result.py:39-74` | Reads error-list length and serializes with `asdict`/`default=str` | Test tolerates unsafe shape and masks unsupported values | Replace with supporting-model and canonical-serialization assertions |
| Snapshot/API chain | Pydantic/dict output reaches sorted `json.dumps`, runner stdout, frontend response | Typed enums/tuples/mappings may alter JSON shape; predicate result not directly public today | Add explicit boundary serializer; avoid accidental golden/public drift |

No observed caller mutates current result fields after construction, agreeing with Audit-4. Mutation remains possible and Audit-5 demonstrated alias/cache corruption in isolation. Error dictionaries are appended only by constructing lists and condition flattening; no code enriches them safely after creation.

## 13. Serialization and Public-Schema Impact

The only direct full-`PredicateResult` serialization is test code using `dataclasses.asdict` and `json.dumps(default=str)` (`tests/rules/test_predicate_result.py:67-74`). This is neither canonical nor strict. The production rule layer uses `RuleMatch.model_dump()`/`.dict()` (`runtime.py:263-269`), and output tools use sorted JSON (`generate_snapshot.py:43-50`). No public schema under `systems/Parasara/schemas` defines predicate status, error, or trace-step fields.

Introducing string-valued enums, tuples, immutable mappings, and nested dataclasses is compatible only through an explicit serializer:

- enum member names must not leak; approved lower-case serialized values need stability;
- tuples must serialize as JSON arrays and immutable mappings as JSON objects;
- nested field order, map-key order, numeric representation, datetime format, empty lists, and unsupported values need one policy;
- performance timing must be excluded or normalized for logical snapshots;
- `asdict` consumers may break if nested models/mappings are not ordinary dataclasses/dicts;
- Pydantic `RuleMatch` must not become the accidental predicate serializer;
- Yoga, Career, snapshot, runner/API, and frontend contracts can change only if a deliberate mapping exposes predicate details.

Current public output does not directly embed a complete `PredicateResult`, so typed supporting models can remain internal initially. However, condition/Yoga information-loss fixes could change evidence and rule firing, and Yoga UUID IDs already make enrichment JSON nondeterministic. Golden changes must be reviewed rather than mechanically regenerated.

## 14. Existing Tests and Coverage Gaps

Existing evidence is limited:

- `tests/rules/test_predicate_result.py:39-55` proves an exception becomes a nonempty error list but does not assert code, safe message, recoverability, immutability, or serialization;
- `test_predicate_result.py:67-74` proves current content can be string-coerced to JSON, not canonical JSON safety;
- `tests/enrichments/test_yoga_engine_rule_driven.py:34-37` and `test_integration_aspects_consumers.py:34-36` assert only that random Yoga trace IDs exist;
- `tests/determinism_test.py:7-15` hashes full generated output, not predicate supporting models, and invokes a file-writing generator;
- no tests target `ci_snapshot_check.normalize` or immutable/canonical predicate values.

All **29 requested supporting-model test categories are missing as adequate contract tests**:

| Area | Missing Categories | Count | Risk | Recommended Location |
|---|---|---:|---|---|
| PredicateStatus | Complete membership; stable serialized values; invalid rejection; matched/status consistency; JSON serialization | 5 | Contradictory or unstable outcome semantics | `tests/rules/test_predicate_status.py` |
| PredicateError | Stable codes; safe exception conversion; recoverability; immutable details; JSON-safe details; raw-stack exclusion; deterministic serialization | 7 | Leakage, mutation, unrouteable failures, nondeterministic output | `tests/rules/test_predicate_error.py` |
| PredicateTraceStep | Construction; deep immutability; deterministic ordering; deterministic identity; JSON serialization; cache-hit behavior; no system-clock dependency; parent/child behavior | 8 | Unreplayable traces, cache drift, hidden ordering changes | `tests/rules/test_predicate_trace.py` |
| Canonicalization | Nested dicts; lists/tuples; sets; enums; dataclasses; caller mutation; unsupported values; repeated output; cycles | 9 | Aliasing, silent coercion, unstable hashes/JSON, recursion failure | `tests/rules/test_predicate_canonicalization.py` |

The existing exception and serialization tests should be migrated, not counted as satisfying these categories, because their assertions permit the exact unsafe behavior Prompt-01 prohibits.

## 15. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Typed status plus matched/status invariant | MISSING | No status symbol/field; Prompt-01 semantics unresolved | `engine.py`; `predicates.py` | Approve invariant and add validated predicate status | IN_SCOPE | P0 | Yes |
| Typed safe predicate errors | NONCOMPLIANT | Mutable dicts and `str(e)` at `engine.py:109,127,140` | `engine.py`; handlers | Frozen error model and safe exception boundary | IN_SCOPE | P0 | Yes |
| Deep immutable canonical nested values | NONCOMPLIANT | `Dict`/`List` fields and no-op normalization | `engine.py:9-18,47-51`; `predicates.py` | Defensive recursive normalization/freeze | IN_SCOPE | P0 | Yes |
| Failure state survives condition/Yoga consumption | NONCOMPLIANT | Condition flattens; Yoga discards errors/trace/status | `engine.py:153-159`; `yoga_engine.py:154-177` | Typed boundary policies preserving failure classes | IN_SCOPE | P0 | Yes |
| Typed ordered `PredicateTraceStep` | MISSING | Only mutable condition summary dict; handler traces empty | `engine.py`; `predicates.py` | Predicate-specific frozen step model | IN_SCOPE | P1 | Yes |
| Stable error-code catalog | MISSING | Lower-case ad hoc strings/reasons | `engine.py`; `runtime.py` | Approve ownership and stable serialized codes | IN_SCOPE | P1 | Yes |
| Deterministic trace identity/order | NONCOMPLIANT | UUID4, set ordering, duration fields | `yoga_engine.py`; `engine.py` | Separate deterministic logical identity from telemetry | IN_SCOPE | P1 | Yes |
| One canonical serializer | MISSING | Test-only `asdict/default=str`; sorted JSON downstream | `engine.py`; tests; output tools | Strict recursive serializer with stable policies | IN_SCOPE | P1 | Yes |
| Supporting-model construction validation | MISSING | Dataclass annotations unchecked; no factories | `engine.py`; handlers | Validate fields/invariants/unsupported values at construction | IN_SCOPE | P1 | Yes |
| Supporting-model contract tests | MISSING | 29 categories lack adequate tests | `tests/rules` | Add focused suites after model decisions | IN_SCOPE | P1 | Yes |
| Performance telemetry excluded from logical equivalence | NONCOMPLIANT | `perf_counter` timing participates in dataclass equality/trace | `engine.py` | Define logical projection and snapshot policy | IN_SCOPE | P2 | No |
| Backward-compatible serialization migration | PARTIAL | Predicate result internal; downstream evidence/snapshots sensitive | tests, Yoga, output/API | Explicit adapters and reviewed schema/golden policy | TEMPORARY_COMPATIBILITY | P2 | No |
| Rule/predicate model separation | PARTIAL | `RuleMatch` overlaps but is later-layer and mutable | `models.py`; `runtime.py` | Keep separate; define translation boundary | IN_SCOPE | P2 | No |
| Complete canonical type policy | MISSING | No set/enum/date/Decimal/custom/cycle rules | serializer/canonicalization module not present | Approve supported values and rejection behavior | IN_SCOPE | P2 | No |
| Enrichment trace standardization | PARTIAL | Aspect/Shadbala have unrelated mutable shapes | enrichment modules | Keep separate; standardize in their owning stages if needed | OUT_OF_SCOPE_FUTURE_STAGE | P3 | No |
| Run-level trace hierarchy/retention | MISSING | No parent/run IDs or retention/detail policy in code | future evaluation/output layers | Implement under later trace architecture | OUT_OF_SCOPE_FUTURE_STAGE | P3 | No |

## 16. Migration Risks and Priorities

Counted findings are the 16 compliance-matrix rows: **P0=4, P1=6, P2=4, P3=2**.

P0 risks:

1. Status absence and unresolved invariants block truthful outcome classification.
2. Raw mutable errors block safe exception handling.
3. Missing deep immutability/canonicalization permits alias and cache corruption.
4. Condition/Yoga collapse typed failures into ordinary nonmatches.

P1 completion work:

1. Add a predicate-owned trace-step type.
2. Approve a stable error-code catalog and ownership.
3. Remove random/unordered/logically variable trace behavior from logical identity.
4. Provide one strict canonical serializer.
5. Enforce model validation/factory invariants.
6. Cover all 29 missing supporting-model test categories.

P2 compatibility/quality risks are telemetry equality, serializer/public/golden migration, strict separation from `RuleMatch`, and the complete supported-value policy. P3 items are later enrichment-trace standardization and run-level trace hierarchy/retention.

Migration should introduce predicate-specific models at the central engine boundary before converting handlers and consumers. `RuleMatch`, Yoga, enrichment, and domain trace shapes should not be broadened into a shared base merely because field names overlap. Temporary adapters must translate explicitly and preserve current factual/scoring behavior; they must not use `default=str` or silently discard failure status.

## 17. Unresolved Architectural Questions

1. What are the final allowed `PredicateStatus` members, and is `evaluated` a final serialized state or only an umbrella/transient concept? What exact invariant maps every status to `matched`?
2. Are missing planet/house/varga/aspect facts always errors, capability failures, invalid parameters, or sometimes legitimate unmatched observations? The answer is predicate-schema and capability-policy dependent.
3. Should unknown predicates/references be rejected exclusively by rule loading/compilation, and what defensive evaluator result is required if one reaches runtime?
4. Which error codes are strings versus an enum, and are `INVALID_RETURN_TYPE` and `UNKNOWN_PREDICATE` temporary compatibility codes or permanent public contract members?
5. What content is permitted in safe public error messages/details, and where may secure internal exception diagnostics be logged?
6. Which nested value types are supported canonically: tuple/list distinction, sets, enums, dataclasses/Pydantic models, Decimal, datetime, AstroState identities, and custom objects? Must unsupported values reject construction?
7. Are duration and cache-hit fields excluded from equality, logical hashing, and deterministic snapshots while retained as performance metadata?
8. How are deterministic predicate step IDs derived, and which parent/run/AST identifiers belong in Prompt-01 versus the later condition/trace stages?
9. Must public API/Yoga output expose predicate statuses/errors/traces, or should explicit rule/domain adapters retain the current public schema?

The first question blocks a correct status model; questions 2–7 block a complete error/canonical serialization contract. This audit does not invent answers.

## 18. Audit-6 Conclusion

Audit-6 is complete and reliable with all five prerequisite reports available.

### Summary counts

| Metric | Count |
|---|---:|
| Existing status models | 0 |
| Existing typed error models | 0 |
| Existing trace-model/trace-shape candidates | 6 |
| Dictionary-based predicate-error patterns | 3 |
| Dictionary-based trace/trace-bearing patterns | 5 |
| Central predicate/condition `trace_steps` dictionary patterns | 1 |
| Reusable supporting models | 0 |
| Models requiring Prompt-01 extension | 0 |
| Predicate-specific models required | 3 |
| Deterministic trace candidates | 3 |
| Nondeterministic trace mechanisms | 4 |
| Reusable canonicalization utilities | 0 |
| Missing supporting-model test categories | 29 |
| P0 findings | 4 |
| P1 findings | 6 |
| P2 findings | 4 |
| P3 findings | 2 |

Prompt-01 cannot safely proceed to implementation until the status invariant, error ownership/safety, nested canonical value policy, and logical-versus-performance identity rules are approved. Cross-layer `RuleMatch`, Yoga, Aspect, Shadbala, and Career trace representations must remain separate. This audit modified only this report and did not begin Audit-7.
