# Prompt-01 Audit-20: Serialization and Public Output

## 1. Executive Summary

Audit-20 is **COMPLETE**. All nineteen prerequisite reports were present. Seventeen relevant serialization/exposure surfaces were identified: four internal runtime, three debug/test-diagnostic, two snapshot-contract families, two persisted-internal artifact families, and six public-contract surfaces.

Only one path directly serializes a complete `PredicateResult`: `dataclasses.asdict` followed by `json.dumps(default=str)` in `tests/rules/test_predicate_result.py:67-74`. It is test-only, includes all eight current fields, masks unsupported nested values with string conversion, and has no deserializer. No condition result is directly serialized. The active Yoga path converts a condition `PredicateResult` into one custom mutable dictionary shape; Career and the snapshot assembler provide two domain/output serializers, while no inference serializer exists.

Prompt-01 adds `predicate_version`, `status`, typed immutable errors/traces, deeply immutable mappings/tuples, and canonical semantics. Current serializers have four immutable-container incompatibilities, one enum-representation inconsistency, two tuple/list risks, five non-JSON-safe nested-value paths, and no canonical logical serializer. `cache_hit`, `evaluation_time_ms`, and random Yoga trace identity create three telemetry/diagnostic contamination paths. Cold versus warm direct result serialization differs in one field (`cache_hit`) while warm output reuses cold timing.

The public path is `interpret_career -> assemble_output -> json.dumps -> runner_api -> NextResponse.json -> frontend`. It does not expose raw `PredicateResult`, condition results, predicate errors, or predicate trace steps. It exposes selected legacy rule evidence, scores, confidence, components, indicators, and constant `career_001`. Prompt-01 must therefore remain internal by default, but changes to matching/evidence can indirectly affect five snapshot/artifact families and six public compatibility surfaces.

No dedicated `OutputAssembler` exists. `generate_snapshot.py` directly reasons about domain calls and assembles dictionaries. `parashara_output.schema.json` is a minimal Draft-07 validator, has no explicit output-schema version, omits most emitted fields/structures, and is not invoked by the generator. Five schema-version decisions are required across PredicateResult, ConditionResult, Yoga, domain output, and public output.

There is no PredicateResult/condition round trip, cache persistence, public response model, or typed frontend schema (`Snapshot = any`). Eight round-trip gaps, six nondeterministic serialization paths, ten at-risk downstream consumers, and twenty-eight missing test categories were found.

The 21 compliance findings total **P0=7, P1=8, P2=4, P3=2**. Safe Prompt-01 implementation requires an internal canonical logical representation and explicit debug/public projections; it must not automatically publish all internal fields or update snapshots without approved compatibility decisions.

## 2. Audit Scope and Method

The Master Architecture, Prompt-01, and Audits 1–19 were reconciled with source, tests, schemas, snapshots, fixtures, artifact tools, the Python runner, Next.js API route, and frontend consumer. Searches covered dataclass/Pydantic conversion, JSON encode/decode, model dumps, snapshots, schemas, artifacts, diagnostics, evidence, errors, traces, cache telemetry, and timing.

Counts group files that form one contract family when they serialize the same shape (for example, three Career golden fixtures), but keep separate architectural boundaries such as the generator, runner, HTTP route, and frontend download. Input fixture loading is not counted unless it deserializes a predicate-derived result.

No generator, snapshot check, artifact writer, formatter, or update command was executed because each writes repository files. Tests remain unavailable due missing Python dependencies. All work was static and read-only except creation of this report.

## 3. Reconciliation with Audits 1–19

All expected reports exist; no limitation applies.

- Audits 1–4 establish the complete caller graph and nine broad material serialization consumers. Audit-20 refines them into seventeen conversion/exposure surfaces and contract classifications.
- Audit-5 establishes one direct complete-result serializer, missing status/version, shallow mutability, `default=str`, and nine broad impacts. Audit-20 verifies no additional direct serializer/deserializer appeared.
- Audit-6 establishes no supporting models/serializers. Enum/error/trace behavior is therefore a required decision, not current behavior.
- Audits 7–10 show inputs/evidence may contain unvalidated, provider/config-dependent, or mutable values.
- Audit-11 proves one cold/warm serialized field difference and shared nested values.
- Audit-12 establishes no `ConditionResult`; logical nodes reuse PredicateResult and are not directly serialized.
- Audits 15–16 establish Yoga custom dictionaries and Career/public snapshot fan-out. Audit-20 preserves their information-loss classifications.
- Audit-17 supplies five raw exception exposures; only the complete stderr relay is a public serialization concern here, while predicate raw errors remain internal unless debug/asdict/artifact paths serialize them.
- Audit-18 supplies evidence mutability/non-JSON risks and six exposure impacts.
- Audit-19 supplies trace UUID/timing/set/cache nondeterminism and three snapshot impacts.

No prior count or active-path classification is contradicted.

## 4. Serialization-Surface Inventory

| Surface | Producer | Consumer | Current shape | Classification | Risk |
|---|---|---|---|---|---|
| Predicate cache key | `rules/engine.py::_cache_key` | predicate cache | JSON/repr string | Internal runtime | lossy fallback and weak canonicalization |
| PredicateResult debug serialization | `test_predicate_result.py` | test only | `asdict` plus `default=str` | Debug/logging | lossy and unversioned |
| Condition result construction | `rules/engine.py::evaluate_condition` | Yoga evaluator | in-memory PredicateResult/dicts | Internal runtime | no condition-specific boundary |
| RuleMatch conversion | `rules/runtime.py` | Career/artifact code | mutable dict | Internal runtime | Pydantic-version-dependent |
| Yoga conversion | `yoga_engine.py` | AstroState/Yoga consumers | manual dict | Internal runtime | lossy projection |
| Career domain dictionary | `career.py` | assembler/public output | mutable nested dict | Public contract | legacy evidence contract |
| Snapshot assembly | `generate_snapshot.py::assemble_output` | snapshot generator | manual output dict | Public contract | incomplete schema/versioning |
| Snapshot JSON writer | `generate_snapshot.py::generate` | tests/users | sorted JSON file | Public contract | list ordering remains semantic |
| Full golden snapshots | snapshot generator | regression tests/CI | persisted JSON | Snapshot contract | exact-change sensitivity |
| Career golden fixtures | Career generator/manual approval | Career tests | persisted JSON | Snapshot contract | ordered IDs/evidence |
| CI/determinism diagnostics | CI/determinism tools | developers/CI | normalized JSON/hash | Debug/logging | divergent normalization |
| Snapshot comparison output | snapshot runner | developers/tests | diff/temp JSON | Debug/logging | ignore rules mask changes |
| Rule-trace artifacts | artifact generator | reports/SME tools | persisted JSON | Persisted internal | raw errors and legacy dicts |
| Domain/explainability artifacts | artifact generator | reports/SME tools | persisted JSON | Persisted internal | heuristic selection/order |
| Python runner response | `runner_api.py` | Next.js route | JSON stdout envelope | Public contract | raw chart/error exposure |
| Next.js HTTP response | API route | web clients | untyped HTTP JSON | Public contract | no filtering/version |
| Frontend display/download | account astro page | end user | `any` plus JSON blob | Public contract | implicit field dependency |

| Surface | File | Symbol | Layer | Data | Method | Input Type | Output Type | Classification | Field Filtering | Ordering | Schema Version | Consumer | Tests | Prompt-01 Impact | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| predicate cache key | `systems/Parasara/engine/rules/engine.py:39-44` | `_cache_key` | predicate/cache | params | `json.dumps(sort_keys=True,default=str)`; fallback `str` | arbitrary dict-like | process key string | `INTERNAL_RUNTIME` | none | mapping keys sorted only | none | `_CACHE` | indirect cache test | canonicalization replacement required | P0 |
| complete PredicateResult debug | `tests/rules/test_predicate_result.py:67-74` | serialization test | test/debug | all current result fields | `asdict`; `json.dumps(default=str)` | dataclass | dict/string | `INTERNAL_DEBUG` | none | dataclass field order | none | test only | presence/string only | internal representation change | P1 |
| condition result construction | `systems/Parasara/engine/rules/engine.py:135-159` | `evaluate_condition` | condition | logical result/children summaries | PredicateResult constructor/dicts | child results | in-memory PredicateResult | `INTERNAL_RUNTIME` | full children reduced | child source order | none | Yoga | type only | future ConditionResult change | P0 |
| RuleMatch conversion | `systems/Parasara/engine/rules/runtime.py:242-269` | `evaluate_rule_with_score` | legacy rule | RuleMatch | `model_dump`, fallback `.dict()` | Pydantic model | mutable dict | `INTERNAL_RUNTIME` | no configured exclusion | model field order | rule fields only | Career/artifacts | runtime tests indirect | typed/dict adapter compatibility | P0 |
| Yoga result conversion/storage | `systems/Parasara/engine/enrichments/yoga_engine.py:150-186` | `evaluate_yoga_rules` | Yoga | selected condition match/evidence | manual dict + AstroState assignment | PredicateResult/rule dict | list of custom dicts | `INTERNAL_RUNTIME` | errors/traces/status/version dropped | registry order; set planets | Yoga rule version not output contract | re-export/tests/state | shape/ID presence | internal + possible snapshot change | P0 |
| Career domain dictionary | `systems/Parasara/engine/interpreters/career.py:45-116` | `interpret_career` | domain | selected legacy rule evidence/score | manual dict/list conversion | RuleMatch-like dicts | domain dict | `PUBLIC_OUTPUT_JSON` | matched-positive only; errors/traces dropped | candidate order | none | assembler/public | interpreter/snapshots | public compatibility risk | P0 |
| snapshot assembly | `systems/Parasara/tools/generate_snapshot.py:14-40` | `assemble_output` | output tool | diagnostics and domains | manual nested dictionaries | AstroState/domain dict | output dict | `PUBLIC_OUTPUT_JSON` | hardcoded Yoga empty; selected state fields | literal/list order | engine/rule versions only | generator | vertical snapshot | schema decision required | P0 |
| snapshot JSON writer | `systems/Parasara/tools/generate_snapshot.py:43-49` | `generate` | output tool | complete assembled output | `json.dumps(indent=2,sort_keys=True)` | dict | JSON file + returned dict | `PUBLIC_OUTPUT_JSON` | none after assembly | keys sorted in file; lists preserved | no output-schema version | tests/runner/users | immutable/enum adapters needed | P0 |
| full golden snapshot family | `systems/Parasara/tests/snapshots/*.json` | approved/generated snapshots | regression | complete output | JSON artifacts/equality | output dict | persisted JSON | `GOLDEN_SNAPSHOT` | none; generated_at null | file sorted; comparison normalizers vary | embedded engine/rule only | tests/CI | full snapshot can change indirectly | P1 |
| Career golden family | `systems/Parasara/tests/fixtures/*career_snapshot.json` | Career fixtures | regression | Career indicators/evidence/score subsets | JSON load/list comparisons | domain dict | persisted JSON | `GOLDEN_SNAPSHOT` | tests often compare IDs only | list order significant | none | Career tests/framework | rule/evidence changes | P1 |
| CI/determinism diagnostics | `systems/Parasara/tools/ci_snapshot_check.py:18-67`; `tests/determinism_test.py:5-16` | normalize/compare/hash | debug/test | generated output | recursive normalize + `json.dumps` | dict | console JSON/hash | `INTERNAL_DEBUG` | ignores none in CI; rounds floats | sorted dict keys; lists preserved | none | CI/developer | tests not runnable here | telemetry/UUID impacts | P1 |
| snapshot comparison tool | `tests/testing_framework/snapshot_runner.py:8-35` | `compare_snapshots` | test/debug | full/Career output and errors | JSON load/custom compare | dict/JSON | diff dict/temp JSON | `INTERNAL_DEBUG` | default ignores meta/engine/run ID | comparator-specific | none | regression reports | framework integration | can mask version/telemetry changes | P2 |
| rule-trace artifacts | `tests/testing_framework/generate_full_artifacts.py:51-79` | `run_rules_and_trace` | test artifact | full RuleMatch dicts/raw errors | `json.dumps(indent=2)` | list of dicts | JSON files | `PERSISTED_INTERNAL_ARTIFACT` | none | registry iteration | none | validation/report tools | none | typed values/raw errors can break/change | P1 |
| domain/explainability artifacts | `tests/testing_framework/generate_full_artifacts.py:82-158` | synthesis/save helpers | test artifact | selected evidence/scores/explanation | manual dict + `json.dumps` | rule dicts | JSON files | `PERSISTED_INTERNAL_ARTIFACT` | heuristic field selection | registry-derived contributor order | none | SME/report tools | none | internal artifact compatibility | P2 |
| Python runner response | `systems/Parasara/tools/runner_api.py:90-105` | `main` | public API bridge | snapshot + raw Surya chart | `json.dumps` to stdout | dicts | JSON response payload | `PUBLIC_API` | adds raw chart; no predicate field filtering | insertion order | none | Next route | none | public schema/privacy risk | P0 |
| Next.js HTTP response | `frontend/app/api/astro/generate/route.ts:46-67` | `POST` | public API | runner JSON/errors | `JSON.parse`; `NextResponse.json` | untyped JSON | HTTP JSON | `PUBLIC_API` | none; stderr returned on failure | JS serializer | none | frontend/client | none | public compatibility/error filtering | P0 |
| frontend display/download | `frontend/app/(auth)/account/astro/page.tsx:172-201` | `ResultViewer` | public consumer | snapshot/Career summary/full JSON | optional chaining; `JSON.stringify` | `any` | UI/blob download | `PUBLIC_API` consumer | summary selection only; full download | JS property order | none | end user | none | field/type/schema risk | P1 |

Classification totals: internal runtime **4**, debug/logging **3**, snapshot contracts **2**, persisted internal contracts **2**, public contracts **6**; total **17**.

## 5. PredicateResult Serialization

| Field | Type | JSON-safe? | Stable? | Public? | Notes |
|---|---|---|---|---|---|
| `predicate_id` | string | Yes | Partly | No direct exposure | alias/canonical-ID policy missing |
| `predicate_version` | missing | N/A | No | No | required by Prompt-01 |
| `status` | missing enum | N/A | No | No | wire values not decided |
| `matched` | bool | Yes | Yes | Indirectly | semantics must remain compatible |
| `inputs` | arbitrary mapping | Not guaranteed | No | No | nested values unrestricted |
| `evidence` | arbitrary mapping | Not guaranteed | No | Indirectly | downstream projections are lossy |
| `errors` | list of dicts | Not guaranteed | No | No intended | typed/safe filtering absent |
| `trace_steps` | list of dicts | Not guaranteed | No | No intended | immutable representation unresolved |
| `cache_hit` | bool | Yes | No | No | cold/warm telemetry contamination |
| `evaluation_time_ms` | float/null | Usually | No | No | logical/diagnostic split required |

| Field | Internal Model | Canonical Serialization | Debug Output | Snapshot | Persisted Artifact | Public Output | Representation | Consumer Dependency | Impact | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| predicate_id | present | absent | included by asdict | absent directly | absent directly | absent directly | string | condition/cache/test | alias/canonical decision | P0 |
| predicate_version | missing | absent | missing | absent | absent | absent | N/A | future cache/rule | required internal field | P0 |
| status | missing | absent | missing | absent | absent | absent | N/A | all callers | enum/value decision | P0 |
| matched | present | absent | bool included | indirect Yoga/domain booleans | RuleMatch matched, not predicate | indirect only | bool | evaluator/Yoga | preserve semantics | P0 |
| inputs | mutable dict | cache-key string only, not result canonicalization | included | omitted downstream | RuleMatch context differs | omitted | arbitrary dict | cache/debug | deep immutable serialization | P0 |
| evidence | mutable dict | absent | included | selected Yoga/Career-derived forms | rule artifacts use legacy evidence | selected legacy evidence | dict/list nested | Yoga/Career/tests | canonical/safety compatibility | P0 |
| errors | mutable list[dict] | absent | included/raw | dropped | artifact fallback may use raw legacy errors | API runner errors separate | list of dicts | condition/debug | typed safe filtering | P0 |
| trace_steps | mutable list[dict] | absent | included | dropped | no predicate steps | dropped | list of dicts | condition/debug | typed list/tuple conversion | P1 |
| cache_hit | present | contaminates model equality, no canonical projection | included | not directly | absent | absent | bool | cache test | cold/warm difference | P1 |
| evaluation_time_ms | present | contaminates equality, no canonical projection | included | not directly | RuleMatch timing usually null | absent | float/None | cache/condition/debug | telemetry separation | P1 |

Direct complete PredicateResult serializers: **1**. It includes eight current fields, never omits `None`, has no enum handling, and uses `default=str`. No current consumer deserializes it. Required version/status/supporting models have no current representation.

## 6. Supporting-Model Serialization

`PredicateStatus`, `PredicateError`, and `PredicateTraceStep` do not exist, so there is no current enum-name/value, nested-model, or omission policy. Existing error and trace dictionaries serialize only through asdict/debug or are dropped downstream.

The Pydantic RuleMatch dump is not a reusable supporting-model serializer. Yoga/Career dictionaries are layer-owned. One enum inconsistency risk is counted: no policy decides enum name versus value across dataclass, Pydantic, JSON, cache canonicalization, or frontend output.

## 7. Immutable-Value Serialization

| Value type | Current wire shape | Round-trip risk | Recommended encoding |
|---|---|---|---|
| Frozen/mapping-proxy mapping | unsupported/object-dependent | High | sorted ordinary JSON object |
| Tuple | JSON array | tuple identity lost | array with schema-owned reconstruction |
| Frozenset | unsupported or string fallback | High and nondeterministic | sorted canonical array or reject |
| Frozen/nested dataclass | recursive dict/list via `asdict` | concrete type lost | explicit tagged/versioned projection if reconstruction is required |
| Enum | unsupported unless projected | High | stable string value |
| datetime/date/Decimal/UUID | string only through fallback | format/type lost | allowlisted canonical strings |
| NaN/Infinity | non-standard JSON tokens | strict-parser failure | reject or normalize by explicit policy |
| Non-string mapping keys | coerced or rejected | collision/type loss | validate string keys |
| AstroState/Pydantic/custom objects | dict or repr | High | explicit stable-ID/field projection |
| Cyclic values | serialization failure | Cannot round-trip | reject during validation |

| Value Type | Current Use | Serializer | Supported | Current Representation | Deterministic | Round-Trip Safe | Affected Surfaces | Required Decision | Priority |
|---|---|---|---|---|---|---|---|---|---|
| mapping proxy/frozen mapping | not current; Prompt-01 candidate | json/asdict/model_dump | generally No/unknown | unsupported or object-dependent | unknown | No | all internal/debug adapters | approved immutable mapping projection | P0 |
| tuple | Prompt-01 errors/traces candidate | stdlib JSON | Yes as array | list in JSON | order yes | No tuple identity | debug/snapshot/public if exposed | logical tuple versus JSON array policy | P1 |
| frozenset | possible immutable set | stdlib JSON | No | TypeError/default string | No canonical order | No | nested details/evidence | reject or canonical sequence policy | P1 |
| frozen/nested dataclass | Prompt-01 model candidate | asdict | only dataclass-aware | recursive dict/list | field order | type lost | debug/internal serializer | typed reconstruction policy | P1 |
| Enum | future status | stdlib JSON | not generic | unsupported unless str/value projected | policy-dependent | No without schema | all | enum value contract | P0 |
| datetime/date/Decimal/UUID | possible details/trace/config | stdlib JSON | No generic | default string in test only | formatting-dependent | No | debug/errors/traces | allowlist/canonical formatting | P1 |
| float NaN/Infinity | unrestricted current model | stdlib JSON | emitted nonstandard by default | NaN/Infinity token | not strict JSON | No | all | reject/normalize | P0 |
| non-string keys | unrestricted mappings | stdlib JSON | partial/coercive | strings or error | collision risk | No | inputs/evidence/details | string-key validation | P0 |
| custom AstroState/Pydantic object | unrestricted nested Any | mixed | only model_dump/default string | dict or repr | repr can vary | No | debug/artifacts | prohibit/project stable IDs | P0 |
| cycles | unrestricted nested Any | all current | No | recursion/circular-reference error | No | No | internal/debug | validation/rejection | P0 |

Four immutable-container incompatibilities are counted: mapping proxy/frozen mapping, frozenset, nested frozen/custom mapping, and deep immutable details requiring projection. Tuple/list representation risks: **2** (tuple type loss and set/frozen-set ordering/conversion). Non-JSON-safe value paths: **5** across inputs, evidence, errors/details, traces, and RuleMatch/AstroState nested dictionaries.

## 8. Canonical Logical Serialization

No canonical PredicateResult or ConditionResult serialization exists. `_cache_key` sorts parameter mapping keys but uses `default=str`, ignores schema/defaults/aliases/types/context/versions, and falls back to raw `str`. This is cache key construction, not a logical result serializer.

The snapshot writer sorts dictionary keys for formatted files. CI normalization recursively sorts mapping keys and rounds finite floats; the test framework comparator applies different ignored-key/tolerance policies. None preserves types, rejects unsupported values, separates telemetry, normalizes enum/aliases/sets, or guarantees equivalent logical bytes.

Empty handler evidence/errors/traces conventionally use `{}`/`[]`, while absent optional RuleMatch fields serialize as `null`. No omission policy is approved. Semantic list order must be preserved; global alphabetical sorting would not solve registry/condition order.

## 9. Telemetry Separation

Three logical/diagnostic contamination paths are counted:

1. `cache_hit` is included in dataclass equality/asdict and changes cold versus warm serialization.
2. `evaluation_time_ms` is included in equality/asdict/condition trace summaries and varies across independent cold runs; warm cache reuses cold timing.
3. Yoga's UUID4 trace ID is embedded in its serializable custom result rather than separated as nondeterministic diagnostic identity.

Process-local `id(astro)` is part of cache identity but is not serialized as a result field. Snapshot `generated_at` is deliberately normalized to `None`. Current public Career output contains constant trace ID but no cache/timing telemetry.

Cold/warm direct serialization differences: **1** (`cache_hit`); nested values can additionally diverge after mutation, but that is counted as safety rather than a normal cold/warm field difference.

## 10. Condition-Result Serialization

No `ConditionResult` exists and no condition result is directly serialized. AND/OR return PredicateResult with `predicate_id='AND'/'OR'`, anonymous child evidence, flattened errors, trace summaries, timing, and no nested full children/status/skips.

Introducing ConditionResult affects field names/types, operator identity, child recursion, error/trace linkage, skipped branches, and canonical serialization. Yoga currently expects only `.matched` and `.evidence`, so an adapter is required even if no public JSON changes. Direct condition serializers: **0**.

## 11. Evidence, Error and Trace Serialization

Evidence reaches three forms: direct PredicateResult debug serialization, raw condition evidence copied into Yoga dictionaries, and selected legacy rule evidence copied into Career indicators/public JSON. Identity, versions, unmatched facts, errors, and traces are lost before public output. ASPECT edges and nested mutable values are not validated.

Predicate errors serialize only in the direct asdict test or inside condition trace summaries if a caller serializes the complete result. They may contain raw exception text. Yoga/Career drop them. Separately, the API returns raw runner stderr in public error `detail`; typed predicate errors must not inherit this filtering failure.

Predicate trace steps are empty; condition summaries contain timing/raw errors; Yoga discards them and inserts UUID4; Career inserts `career_001`. Serialization does not preserve parent-child or skipped branches.

## 12. Yoga Serialization

Yoga manually emits `yoga_id`, name, matched, planets, houses, aspects_used, evidence, and UUID trace ID. It omits rule/predicate versions, condition identity, status, errors, traces, cache, timing, provenance, approval, and full child results. It stores the mutable list on AstroState.

The primary snapshot explicitly hardcodes `diagnostics.yogas=[]`, so current golden snapshots do not serialize active Yoga results. Public re-export callers and Yoga tests can receive the custom list. Prompt-01 changes may affect the internal Yoga adapter and any future diagnostics population without requiring a public change now. Yoga serializers/conversion surfaces: **1**.

## 13. Domain and Inference Serialization

Career returns an untyped dictionary with summary, score, confidence, components, indicators, evidence, scoring, and trace ID. It exposes matched-positive legacy evidence/context and omits all generic predicate/result fields, unmatched/errors/traces/cache/timing/version. The assembler embeds this dictionary without validation.

There is no inference engine or serializer. Wealth is a constant dictionary. Domain/inference serializer surfaces: **2** (Career conversion and output assembly; inference zero). Deep immutability may break local mutation assumptions only where adapters build lists/dicts; public JSON should remain projected dictionaries/lists by explicit serializer.

## 14. OutputAssembler and Public Schemas

No dedicated OutputAssembler exists. `assemble_output` invokes Career, reads AstroState/enrichments, chooses diagnostics, supplies placeholders, and constructs public dictionaries. This violates the target serialization-only boundary.

`systems/Parasara/schemas/parashara_output.schema.json` requires engine, diagnostics, domains and summary/score/confidence for each domain. It does not require/describe meta, versions beyond engine/rule set, components, indicators, evidence, scoring, trace, errors, Yoga shape, deterministic ordering, or output schema version. The generator does not validate against it.

Prompt-01 is intended primarily as an internal contract. Publishing status/errors/traces/evidence requires an explicit public schema decision; absence of an authoritative field-level compatibility policy is recorded below.

## 15. Golden Snapshots and Fixtures

| Artifact | Current contract | Change sensitivity | Consumer impact |
|---|---|---|---|
| Approved full snapshot | exact persisted output JSON | High | vertical-slice and CI regressions |
| Generated snapshot variants | informally retained output JSON | Medium | manual review and stale-contract confusion |
| Career fixture family | ordered indicators/evidence/scores | High | Career regression failures |
| Rule-trace artifacts | persisted internal legacy dicts | Medium | report/SME tooling changes |
| Domain/explainability artifacts | heuristic contribution JSON | Medium | report interpretation changes |
| Public JSON schema | skeletal Draft-07 contract | Critical | validators and external consumers remain under-specified |

| Artifact/Schema | Location | Generator | Predicate-Derived Data | Telemetry | Deterministic | Consumer | Prompt-01 Change | Compatibility Risk | Update Allowed Now | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| approved full snapshot | `systems/Parasara/tests/snapshots/output_golden_chart_01.json` | `generate` | Career legacy evidence/scores; diagnostics | generated_at null; Career constant trace | current path mostly | vertical-slice/CI | indirect match/evidence changes | High | No | P0 |
| generated snapshot variants | `systems/Parasara/tests/snapshots/generated_*.json` | tools/manual | same shape, sometimes stale | varies by artifact | not uniformly governed | manual/tests | expected only after approval | Medium | No | P1 |
| Career fixture family | `systems/Parasara/tests/fixtures/*career_snapshot.json` | generator/manual | indicator IDs/contributions/evidence | none | list-order dependent | Career/framework tests | valid firing/evidence must be protected | High | No | P0 |
| rule trace artifacts | `tests/reports/artifacts/rule*_traces.json` when generated | artifact generator | legacy RuleMatch/evidence/raw failures | rule timing nullable | registry order dependent | reports/SME | internal expected change | Medium | No | P2 |
| domain/explainability artifacts | `tests/reports/artifacts/domain_prediction.json`, `explainability.json` | artifact generator | heuristic contributions/evidence | none | registry order dependent | reports | internal expected change | Medium | No | P2 |
| public JSON schema | `systems/Parasara/schemas/parashara_output.schema.json` | manual | only coarse domain requirements | none | N/A | validators/docs | explicit schema decision | Critical | No | P0 |

Snapshot impacts: **5** contract/artifact families (full, generated variants, Career fixtures, rule artifacts, domain/explainability artifacts). Schema is counted separately as a public decision. Update tools exist, but Audit-20 authorizes no regeneration.

## 16. Logs and Diagnostic Output

`ci_snapshot_check` prints normalized full generated/approved JSON on mismatch. Artifact/report tools dump RuleMatch evidence and raw exception messages. The runner prints exception details and resolved paths to stderr; the Next route logs and returns stderr. These are untyped, unredacted, and not governed by a diagnostic schema.

No predicate logger or secure internal/public filtering layer exists. Debug output can be mistaken for contract output because both use ordinary JSON dictionaries. Timing, UUIDs, raw errors, and mutable data are not consistently normalized.

## 17. Deserialization and Round Trips

No PredicateResult, error, trace, or condition result is deserialized. Cache is memory-only and stores live objects. Snapshots are loaded only for comparison; API JSON is parsed as untyped data and not reconstructed into models. Frontend type is `any`.

Eight round-trip gaps are counted: predicate version, status enum, immutable mappings, tuple errors, tuple traces, nested child results, safe typed errors/traces, and status/matched invariant. There is no malformed/unknown-field/version policy or migration reader.

## 18. Schema Versioning and Compatibility

Five schema-version decisions are required:

1. internal canonical PredicateResult representation/version;
2. ConditionResult representation/version;
3. temporary Yoga custom output/version;
4. Career/domain compatibility shape/version;
5. public Parashara output schema version and change policy.

Engine and rule-set versions exist in output, but predicate library, DSL, inference, normalization, enrichment, and output-schema versions are absent. Adding internal fields is not automatically a public breaking change. Changing Career firing/evidence/field shape or API wrapper is a public compatibility risk even if PredicateResult remains internal.

## 19. Downstream Consumer Inventory

| Consumer | Input artifact | Assumptions | Breakage risk |
|---|---|---|---|
| PredicateResult tests | direct dataclass/debug dict | dataclass type and current fields | High |
| Yoga evaluator | condition PredicateResult | `.matched` and `.evidence` attributes | Critical |
| Career interpreter | legacy RuleMatch dict | current keys, scores, evidence, order | Critical |
| Vertical snapshot test | full golden JSON | exact structural equality | Critical |
| Career snapshot tests | Career fixtures | ordered rule IDs and selected fields | High |
| CI/determinism tools | generated output | stable normalized tree and list order | High |
| Artifact/report tools | RuleMatch/domain artifact JSON | mutable dictionaries and registry order | High |
| Python runner | assembled snapshot/raw chart | JSON-serializable untyped dictionaries | Critical |
| Next.js API route | runner stdout JSON | pass-through arbitrary payload | Critical |
| Frontend viewer/download | HTTP response | `domains.career.summary`, metadata, full JSON | High |

| Consumer | File | Symbol | Surface | Fields Used | Exact-Type Dependency | Ordering Dependency | Unknown-Field Behavior | Schema Version | Migration Risk | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| predicate tests | `tests/rules/test_predicate_result.py` | tests | direct result/debug | type, matched, ID, cache, timing, errors | dataclass/isinstance | dataclass fields indirectly | asdict accepts all | none | High | P0 |
| Yoga evaluator | `engine/enrichments/yoga_engine.py:150-179` | `evaluate_yoga_rules` | internal condition | `.matched`, `.evidence` | attribute contract | registry/child evidence | ignores extra fields | none | Critical | P0 |
| Career interpreter | `engine/interpreters/career.py:45-104` | `interpret_career` | legacy rule dict | matched, scores, evidence, context, rule ID | dict keys | candidate order | ignores extra | none | Critical | P0 |
| vertical snapshot test | `systems/Parasara/tests/test_vertical_slice_career.py` | test | full golden | complete dict equality | JSON dict/list | Yes | any difference fails | embedded only | Critical | P0 |
| Career snapshot tests | `systems/Parasara/tests/test_*snapshot.py` | tests | Career fixtures | indicators/rule IDs; one full output | dict/list | Yes for IDs | extra often ignored | none | High | P1 |
| CI/determinism tools | `tools/ci_snapshot_check.py`; `tests/determinism_test.py` | compare/hash | generated snapshot | complete normalized output | JSON-like | list order yes | extra changes hash/compare | none | High | P1 |
| artifact/report tools | `tests/testing_framework/generate_full_artifacts.py` | generators | persisted internal | RuleMatch keys/evidence/scores | mutable dict | registry order | heuristic/ignored | none | High | P1 |
| Python runner | `systems/Parasara/tools/runner_api.py` | `main` | public wrapper | snapshot + raw chart | JSON serializable dict | insertion/list | passes all | none | Critical | P0 |
| Next API route | `frontend/app/api/astro/generate/route.ts` | `POST` | public API | arbitrary parsed runner JSON | untyped JSON | no explicit | passes all | none | Critical | P0 |
| frontend viewer | `frontend/app/(auth)/account/astro/page.tsx` | `ResultViewer` | public client | domains.career.summary, meta, full JSON | `any` | JSON download order incidental | tolerates unknown | none | High | P1 |

At-risk downstream consumers: **10**.

## 20. Determinism and Ordering

Six nondeterministic serialization paths are counted:

1. predicate/condition `evaluation_time_ms`;
2. cold/warm `cache_hit` and reused cold timing;
3. Yoga UUID4 trace IDs;
4. Yoga set-to-list planet ordering;
5. unsorted filesystem/global rule-registry iteration in Yoga/artifacts;
6. `default=str`/fallback object representations in cache/debug serialization.

The snapshot writer sorts mapping keys and normalizes generated_at, but list order and logical content remain unnormalized. CI rounds floats; other tests/hash paths use different rules. Process memory identity is not output but can select stale cached content.

## 21. Existing Tests and Coverage Gaps

The one direct serializer test proves only that `json.dumps(default=str)` returns a string. Full snapshot tests protect current public shape, but not internal/public separation or typed model compatibility.

| Area | Missing Categories | Count | Recommended Test File |
|---|---|---:|---|
| Model serialization | status enum; typed errors; typed traces; immutable mappings; tuples/frozen values; nested canonicalization | 6 | `tests/rules/test_predicate_serialization.py` |
| Round trips | serialize/deserialize; fields; enums; errors/traces; status invariant; deterministic repeat | 6 | `tests/rules/test_predicate_roundtrip.py` |
| Internal/public separation | internal exclusion; raw-error filtering; telemetry filtering/classification; versioned public schema | 4 | `tests/output/test_predicate_public_boundary.py` |
| Integration | condition; Yoga; domain; OutputAssembler; snapshots; cold/warm equivalence | 6 | `tests/output/test_serialization_integration.py` |
| Failure behavior | unsupported values; non-string keys; cycles; NaN/Infinity; unknown enums; malformed input | 6 | `tests/rules/test_serialization_failures.py` |

Missing serialization test categories: **28**. The existing basic PredicateResult JSON test is the one partially covered category excluded from the prescribed total of 29.

## 22. Prompt-01 Compliance Matrix

| Requirement | Evidence | Status | Priority |
|---|---|---|---|
| Canonical logical PredicateResult serializer | only test `asdict/default=str` exists | Missing | P0 |
| Deep immutable value support | four identified incompatibilities | Noncompliant | P0 |
| Status/version serialization | fields do not exist | Missing | P0 |
| Typed safe errors/traces serialization | mutable dicts and raw text | Missing | P0 |
| Logical/telemetry separation | cache/timing included in debug/equality model | Noncompliant | P0 |
| ConditionResult serialization boundary | PredicateResult is reused | Missing | P0 |
| Explicit internal/public field filtering | ordinary dictionaries fan out | Noncompliant | P0 |
| JSON-safe nested values | five unrestricted paths | Noncompliant | P1 |
| Deterministic ordering/canonicalization | six unstable paths | Noncompliant | P1 |
| Cold/warm logical equivalence | `cache_hit` differs | Noncompliant | P1 |
| Yoga compatibility adapter | manual lossy dictionary | Missing | P1 |
| Career/public score compatibility | current full snapshots exist | Partial | P1 |
| Error/public filtering | runner stderr can be relayed | Noncompliant | P1 |
| Serialization and round-trip tests | 28 missing categories | Missing | P1 |
| Predicate/cache/schema versions in identity | output lacks required versions | Missing | P1 |
| Public output schema completeness | skeletal and not validated by generator | Noncompliant | P2 |
| Persisted-artifact contract classification | artifacts are ad hoc | Missing | P2 |
| Frontend typed response contract | response type is `any` | Missing | P2 |
| Snapshot governance consistency | comparator policies differ | Partial | P2 |
| Dedicated OutputAssembler | generator mixes responsibilities | Missing/future stage | P3 |
| Universal RuleMatch/inference serializers | legacy dict/no inference serializer | Missing/future stage | P3 |

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Canonical logical PredicateResult serializer | `MISSING` | asdict/default-str only | engine/models | deterministic internal projection | `IN_SCOPE` | P0 | Yes |
| Deep immutable value support | `NONCOMPLIANT` | four incompatibilities | model/serializer/cache | approved projection/validation | `IN_SCOPE` | P0 | Yes |
| Status/version serialization | `MISSING` | fields absent | result/cache/debug | enum/value/version contract | `IN_SCOPE` | P0 | Yes |
| Typed safe errors/traces serialization | `MISSING` | dicts/raw text/empty traces | engine/condition | safe nested serializer | `IN_SCOPE` | P0 | Yes |
| Logical/telemetry separation | `NONCOMPLIANT` | cache/timing equality/asdict | engine/cache | logical vs diagnostic projections | `IN_SCOPE` | P0 | Yes |
| ConditionResult serialization boundary | `MISSING` | PredicateResult reused | condition/Yoga | typed internal adapter | `IN_SCOPE` | P0 | Yes |
| Explicit internal/public field filtering | `NONCOMPLIANT` | ordinary dict fan-out | generator/API | serializer allowlists | `IN_SCOPE` | P0 | Yes |
| JSON-safe nested values | `NONCOMPLIANT` | five unrestricted paths | models/handlers/runtime | validate/reject/canonicalize | `IN_SCOPE` | P1 | Yes |
| Deterministic ordering/canonicalization | `NONCOMPLIANT` | six nondeterministic paths | cache/Yoga/artifacts | semantic order and normalization | `IN_SCOPE` | P1 | Yes |
| Cold/warm logical serialization equality | `NONCOMPLIANT` | cache_hit differs | cache/tests | exclude/classify telemetry | `IN_SCOPE` | P1 | Yes |
| Yoga compatibility adapter | `MISSING` | manual lossy dict | Yoga | typed-to-current projection | `IN_SCOPE` | P1 | Yes |
| Career/public score compatibility | `PARTIAL` | full snapshot exists | Career/generator/tests | explicit regression contract | `TEMPORARY_COMPATIBILITY` | P1 | Yes |
| Error/public filtering | `NONCOMPLIANT` | stderr relayed | runner/API | safe public error schema | `IN_SCOPE` | P1 | Yes |
| Serialization/round-trip tests | `MISSING` | 28 gaps | tests | focused suites | `IN_SCOPE` | P1 | Yes |
| Predicate/cache/schema versions in identity | `MISSING` | output lacks versions | config/output/cache | approved metadata propagation | `IN_SCOPE` | P1 | Yes |
| Public output schema completeness | `NONCOMPLIANT` | skeletal unvalidated schema | schema/generator | explicit schema/version validation | `TEMPORARY_COMPATIBILITY` | P2 | No |
| Persisted artifact contract classification | `MISSING` | ad hoc files | test framework/docs | mark/version/internalize artifacts | `TEMPORARY_COMPATIBILITY` | P2 | No |
| Frontend typed response contract | `MISSING` | `Snapshot=any` | frontend/API | later generated/typed client schema | `OUT_OF_SCOPE_FUTURE_STAGE` | P2 | No |
| Snapshot governance consistency | `PARTIAL` | multiple comparator/ignore policies | tools/tests | one approved policy | `TEMPORARY_COMPATIBILITY` | P2 | No |
| Dedicated OutputAssembler | `MISSING` | generator mixes responsibilities | future output layer | later architecture stage | `OUT_OF_SCOPE_FUTURE_STAGE` | P3 | No |
| Universal RuleMatch/inference serializers | `MISSING` | legacy dict/no inference | future stages | Prompt-02+ | `OUT_OF_SCOPE_FUTURE_STAGE` | P3 | No |

## 23. Migration Risks and Priorities

The 21 findings total **P0=7, P1=8, P2=4, P3=2**.

P0 work establishes internal canonical serialization, immutable support, version/status/error/trace handling, telemetry separation, ConditionResult boundary, and public filtering. P1 completes JSON safety, determinism, cache equality, Yoga/Career adapters, error filtering, versions, and tests. P2 covers public schema/artifact/frontend/snapshot governance. P3 remains with OutputAssembler and later rule/inference serializers.

The main regression trap is treating current asdict or public dictionaries as the new canonical contract. Another is updating snapshots to absorb unreviewed changes. Internal typed models should project to compatibility dictionaries deliberately; public status/error/trace exposure requires separate schema approval.

## 24. Unresolved Architectural Questions

1. What exact canonical logical serialization excludes telemetry while retaining all semantic fields?
2. Which immutable mapping implementation and JSON projection are approved?
3. Are status enums serialized by value, and are internal values ever public?
4. What temporary Yoga and Career dictionary fields/order are guaranteed?
5. Which PredicateResult/ConditionResult fields, if any, belong in public output during Prompt-01?
6. What output-schema version field and compatibility policy govern the current public JSON?
7. Which snapshot families are contracts versus debug artifacts, and which comparator policy is authoritative?
8. Are rule-trace/domain artifacts persisted contracts or disposable diagnostics?
9. How is runner stderr removed from public error responses while retaining secure diagnostics?
10. What deserializer/round-trip support is required now versus later replay architecture?

These questions affect implementation but do not block Audit-20 completion.

## 25. Audit-20 Conclusion

Audit-20 is COMPLETE. Seventeen surfaces comprise four internal runtime, three debug/logging, two snapshot, two persisted-internal, and six public contracts. One direct PredicateResult serializer, zero condition serializers, one Yoga conversion serializer, two domain/output serializers, and no inference serializer exist. Four immutable-value incompatibilities, one enum inconsistency, two tuple/list risks, five non-JSON paths, three telemetry contaminations, one cold/warm difference, five snapshot impacts, six public risks, five schema decisions, ten at-risk consumers, eight round-trip gaps, six nondeterministic paths, and twenty-eight missing test categories were recorded. Exactly this report was created; no code, tests, schemas, fixtures, snapshots, prior reports, or Audit-21 artifacts were modified.

### Summary counts

| Metric | Count |
|---|---:|
| Serialization surfaces | 17 |
| Internal runtime surfaces | 4 |
| Debug/logging surfaces | 3 |
| Snapshot contracts | 2 |
| Persisted internal contracts | 2 |
| Public contracts | 6 |
| Direct PredicateResult serializers | 1 |
| Condition-result serializers | 0 |
| Yoga serializers/converters | 1 |
| Domain/output serializers | 2 |
| Inference serializers | 0 |
| Immutable-value incompatibilities | 4 |
| Enum serialization inconsistencies | 1 |
| Tuple/list representation risks | 2 |
| Non-JSON-safe value paths | 5 |
| Logical telemetry contamination paths | 3 |
| Cold/warm serialization differences | 1 |
| Snapshot impacts | 5 |
| Public compatibility risks | 6 |
| Schema-version decisions required | 5 |
| Downstream consumers at risk | 10 |
| Round-trip gaps | 8 |
| Nondeterministic serialization paths | 6 |
| Missing serialization test categories | 28 |
| P0 findings | 7 |
| P1 findings | 8 |
| P2 findings | 4 |
| P3 findings | 2 |
