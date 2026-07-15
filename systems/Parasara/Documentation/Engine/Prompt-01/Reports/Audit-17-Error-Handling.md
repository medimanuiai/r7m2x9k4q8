# Prompt-01 Audit-17: Error Handling

## 1. Executive Summary

Audit-17 is **COMPLETE**. All sixteen prerequisite reports were present. The repository has no canonical `PredicateError`, no predicate error-code enum, no status model, no recoverability field, no timeout mechanism, and no strict development mode. All **37 predicate-related error-handling paths** are untyped. Zero paths are typed-and-preserved and zero are typed-with-information-loss.

The generic evaluator is the least lossy current boundary, but it still turns unknown predicates, invalid return types, handler exceptions, missing condition type, invalid parameters, and unavailable capabilities into `matched=False` without a status. Handler exceptions expose raw `str(exception)` in a mutable error dictionary and are cached. AND/OR aggregate those dictionaries in child order but determine their own match from booleans only; therefore `OR(error, matched)` is matched-with-errors and `AND(unmatched, error)` is merely false-with-errors. NOT is unsupported and is misrouted as an unknown predicate. Malformed roots/children can escape uncontrolled to the caller.

Loader and Yoga paths lose errors earlier. Generic and Yoga loaders silently skip parse, I/O, record, and validation failures. Yoga swallows enrichment-preparation and storage failures, ignores `PredicateResult.errors` and trace steps, and emits ordinary matched/unmatched custom dictionaries. Career uses a separate legacy evaluator whose errors become false/zero-score evidence, then discards unmatched evidence through three domain conversion boundaries. These findings reconcile exactly with Audit-15's two Yoga error-loss paths and Audit-16's three domain error-loss paths.

Five raw-exception exposure paths exist. The most important is `evaluate_predicate` placing `str(exc)` in `PredicateResult.errors`; test artifact helpers and snapshot tooling repeat raw exception messages. The public Next.js route forwards the Python runner's complete stderr as an API `detail`, creating one stack-trace exposure risk if an uncaught child-process traceback reaches stderr. No current predicate result explicitly constructs or returns a traceback.

Four current sticky cache-error categories remain from Audit-11: unmatched, missing capability represented as unmatched, invalid parameters represented as unmatched/error, and handler exceptions. Error timing, raw exception messages, string fallback representations, cache warmth, global loader state, and Yoga UUID/set behavior create six nondeterministic error mechanisms.

The 21 compliance findings total **P0=7, P1=8, P2=4, P3=2**. Safe Prompt-01 implementation requires typed immutable errors/status, validated definitions and parameters, deterministic safe exception conversion, explicit condition error precedence, a recovery-aware cache policy, and strict-development behavior. It must preserve current valid factual results while refusing to preserve silent error-to-nonmatch behavior as factual semantics.

## 2. Audit Scope and Method

The authoritative Master Architecture and Prompt-01 DOCX files were read directly from their document XML without extraction to the workspace. Prompt-01 requires immutable `PredicateError(code, message, predicate_id, details, recoverable)`, explicit statuses, safe exception conversion, no public stack traces, internal secure logging, and explicit `fail_on_error` behavior. The Master Architecture additionally requires deterministic compilation errors, machine-readable runtime errors, and strict versus experimental behavior.

Repository-wide searches covered production code, tests, fixtures, tools, loaders, predicates, generic conditions, Yoga, Career, caches, artifact writers, runner/API output, logging, `try/except`, `raise`, error/reason dictionaries, timeout, strictness, traceback, and raw exception rendering. Every candidate was inspected in context. Counts represent distinct behavior paths; repeated instrumentation catches with identical semantics are grouped, while materially different producer/consumer boundaries are separate.

An in-memory `python -B` probe verified unknown-predicate, invalid-return, handler-exception, warm-cache, and OR aggregation behavior without writing repository files. Focused pytest remains unavailable because the active Python environment has no `pytest` module. No production code, tests, rules, fixtures, snapshots, prior reports, or Audit-18 artifacts were modified.

## 3. Reconciliation with Audits 1–16

All expected reports exist. No missing-report limitation applies.

- Audits 1–5 establish the handler-only registry, alternate legacy evaluators, incomplete `PredicateResult`, mutable nested error collections, and information-loss callers. Audit-17 retains those active/dormant classifications.
- Audit-6 found zero typed predicate-error/status models and three central error-dictionary shapes. Audit-17 verifies those shapes and adds loader, Yoga, legacy runtime, artifact, and API exposure paths.
- Audit-7 found invalid parameters become false or raw-string exceptions; Audit-8 found missing capabilities become false. Both are counted as converted-to-unmatched paths, not new error models.
- Audits 9–10 establish mutable state, hidden enrichment I/O, and recomputation failures. Audit-17 includes only those failures reachable from predicates/Yoga and does not count unrelated enrichment fallbacks.
- Audit-11 counted four sticky status/error categories. Audit-17 preserves that count and confirms cached raw exception text/timing on warm retrieval.
- Audit-12 found eager AND/OR, no NOT, flattened errors, malformed-node escapes, and unresolved precedence. Audit-17 expands the four required mixed-error scenarios without inventing semantics.
- Audits 13–14 establish missing format validation, four incorrect unknown-predicate paths, two unknown-operator paths, and best-effort loader suppression. Audit-17 preserves those counts.
- Audit-15 counted two Yoga error-loss paths: active generic-to-Yoga conversion and dormant tuple parallel handling. Audit-17 preserves **2**.
- Audit-16 counted three Career/domain conversions discarding errors. Audit-17 preserves **3** and traces the raw evaluator fallback before them.

No prior finding is contradicted. Audit-17 newly identifies the public stderr relay and test-artifact raw-message surfaces because their security/serialization significance is specific to this audit.

## 4. Error-Handling Path Inventory

| File | Symbol | Layer | Predicate/Caller | Exception Scope | Classification | Current Fallback | Result Status | Swallowed | Raw Text Exposed | Stack Trace | Evidence Preserved | Recoverable | Strict Mode | Active Path | Tests | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `engine/rules/engine.py:39-44` | `_cache_key` | cache | all predicates | parameter JSON serialization | `CONTRACT_VIOLATION` | `str(params)` key | none | Yes | representation may enter key only | No | N/A | No | No | Yes | no failure test | P0 |
| `engine/rules/engine.py:62-77` | `evaluate_predicate` | predicate | unknown ID | registry miss | `RULE_DEFINITION_ERROR` | false result, reason only, cached | no status; unmatched | cause converted | No | No | reason retained | No | No | Yes | no direct assertion | P0 |
| `engine/rules/engine.py:80-93,119-132` | `evaluate_predicate` | predicate | legacy tuple | tuple arity/unpack/coercion | `CONTRACT_VIOLATION` | caught as predicate exception | no status; unmatched | original contract defect hidden | Yes | No | generic reason | No | No | reachable/test registration | no tuple-failure test | P0 |
| `engine/rules/engine.py:101-112` | `evaluate_predicate` | predicate | invalid handler return | non-result/non-tuple | `CONTRACT_VIOLATION` | false result with dict error | no status; unmatched | converted | type string only | No | reason retained | No | No | Yes | none | P0 |
| `engine/rules/engine.py:113-117` | `evaluate_predicate` | cache | all results | `replace` failure | `CONTRACT_VIOLATION` | cache original object | inherited | Yes | No | No | inherited | No | No | Yes | none | P1 |
| `engine/rules/engine.py:119-132` | `evaluate_predicate` | predicate | handler | any handler/cache-store exception in try | `UNEXPECTED_PROGRAMMING_ERROR` or input/capability accident | false result, raw-message dict, cached | no status; unmatched | exception class/trace hidden | Yes | No | generic reason | No | No | Yes | exception only checks nonempty | P0 |
| `engine/rules/engine.py:135-140` | `evaluate_condition` | condition | missing node type | malformed definition | `RULE_DEFINITION_ERROR` | false `UNKNOWN`, dict error | no status; unmatched | converted | No | No | missing-type reason | No | No | Yes | none | P0 |
| `engine/rules/engine.py:135-162` | `evaluate_condition` | condition | malformed root/child | `.get`, iteration, recursion | `RULE_DEFINITION_ERROR`/`CONTRACT_VIOLATION` | uncontrolled raise | none | No | caller-dependent | possible caller traceback | No | No | No | reachable | none | P0 |
| `engine/rules/engine.py:142-159` | `evaluate_condition` | condition | AND child error | child result aggregation | `CONTRACT_VIOLATION` | boolean `all`, flatten errors | no status | No | inherited raw text | No direct traceback | child evidence/error summary partial | No | No | active Yoga | none | P0 |
| `engine/rules/engine.py:142-159` | `evaluate_condition` | condition | OR child error | child result aggregation | `CONTRACT_VIOLATION` | boolean `any`, flatten errors | no status | No | inherited raw text | No direct traceback | child evidence/error summary partial | No | No | active Yoga | probe only | P0 |
| `engine/rules/engine.py:141,160-162` | `evaluate_condition` | condition | unknown operator/NOT | fallthrough as predicate | `RULE_DEFINITION_ERROR` | unknown predicate false | no status; unmatched | semantic defect hidden | No | No | wrong unknown-predicate reason | No | No | reachable | none | P0 |
| `engine/rules/predicates.py:20-37` | `aspect_exists` | predicate | ASPECT edge | any per-edge access error | `EXPECTED_MISSING_DATA` or programming error | skip edge | ordinary result | Yes | No | No | failed edge absent | No | No | active | no malformed-edge test | P1 |
| `engine/rules/predicates.py:69-82` | `functional_role` | predicate/enrichment | role computation | table/I/O/value failure | `EXPECTED_MISSING_CAPABILITY`/`INFRASTRUCTURE_ERROR` | bubbles to generic catch | no status; unmatched | converted by caller | generic catch raw text | No | generic reason | No | No | active | no failure test | P0 |
| `engine/rules/predicates.py:50-67` | house predicates | predicate | missing/invalid planet/house | input or state absence | `EXPECTED_INPUT_ERROR`/`EXPECTED_MISSING_DATA` | false, empty evidence/errors | no status; unmatched | distinction swallowed | No | No | No | No | No | active | factual match tests only | P0 |
| `engine/rules/predicates.py:85-99` | `planet_exalted` | predicate | missing planet/exaltation capability | state/capability absence | `EXPECTED_MISSING_CAPABILITY` | false, empty evidence/errors | no status; unmatched | distinction swallowed | No | No | partial only if degree exists | No | No | active | false test only | P0 |
| `engine/rules/loader.py:13-36` | `load_rules_from_dir` | loader | generic rules | I/O, YAML, record shape | `RULE_DEFINITION_ERROR`/`INFRASTRUCTURE_ERROR` | continue file | no result | Yes | No | No | No | No | No | active M1 | no malformed-source test | P0 |
| `engine/rules/yoga_loader.py:10-18` | `_load_yaml` | loader | Yoga rules | path/I/O/YAML | `RULE_DEFINITION_ERROR`/`INFRASTRUCTURE_ERROR` | empty list | no result | Yes | No | No | No | No | No | active | happy path only | P0 |
| `engine/rules/yoga_loader.py:21-24` | `validate_yoga_rule` | loader | Yoga rule | missing top-level fields | `RULE_DEFINITION_ERROR` | raises `ValueError` | raised | No | rule ID/field names in message | caller could expose | partial message | No | No | active validation | one raise test | P1 |
| `engine/rules/yoga_loader.py:28-44` | `load_yoga_rules` | loader | Yoga rule | validator/registration | `RULE_DEFINITION_ERROR` | skip invalid rule | no result | Yes | No | No | No | No | No | active | skip not asserted | P0 |
| `engine/enrichments/yoga_engine.py:22-52` | `_eval_aspect_condition` | dormant Yoga | local aspect fact | per-edge access error | `EXPECTED_MISSING_DATA`/programming error | continue edge | tuple false/partial | Yes | No | No | failed edge absent | No | No | confirmed unused | none | P2 |
| `engine/enrichments/yoga_engine.py:102-125` | `_eval_condition` | dormant Yoga | unknown type/operator | local dispatch miss | `RULE_DEFINITION_ERROR` | false tuple with reason | no status; unmatched | converted | No | No | reason retained | No | No | confirmed unused | none | P2 |
| `engine/enrichments/yoga_engine.py:134-139` | `evaluate_yoga_rules` | Yoga/enrichment | varga/aspect prep | any preparation failure | `EXPECTED_MISSING_CAPABILITY`/programming error | continue with partial state | none | Yes | No | No | No | No | No | active | no failure test | P0 |
| `engine/enrichments/yoga_engine.py:141-145` | `evaluate_yoga_rules` | Yoga/enrichment | role prep | any role failure | `EXPECTED_MISSING_CAPABILITY`/`INFRASTRUCTURE_ERROR` | continue | none | Yes | No | No | No | No | No | active | no failure test | P0 |
| `engine/enrichments/yoga_engine.py:150-179` | `evaluate_yoga_rules` | Yoga | predicate/condition errors | result conversion | `CONTRACT_VIOLATION` | read only matched/evidence | custom boolean; no status | errors/trace swallowed | inherited evidence only | No | evidence partial | No | No | active | shape only | P0 |
| `engine/enrichments/yoga_engine.py:181-186` | `evaluate_yoga_rules` | Yoga/state | Yoga storage | assignment/model failure | `CONTRACT_VIOLATION` | return matches anyway | none | Yes | No | No | returned matches retained | No | No | active | none | P1 |
| `engine/rules/runtime.py:9-71` | raw helpers/instrumentation | legacy predicate | coverage hooks and sign fallback | instrumentation/degree errors | `INFRASTRUCTURE_ERROR`/input error | pass/false | raw bool | Yes | No | No | No | No | No | active legacy | runtime happy paths | P2 |
| `engine/rules/runtime.py:81-89` | `evaluate_rule` | legacy rule | missing planet | state/input absence | `EXPECTED_MISSING_DATA` | false reason dictionary | unmatched | converted | No | No | reason retained | No | No | active/fallback | runtime missing path partial | P0 |
| `engine/rules/runtime.py:108` | `evaluate_rule` | legacy rule | unsupported type | definition defect | `RULE_DEFINITION_ERROR` | false reason dictionary | unmatched | converted | No | No | reason retained | No | No | active fallback | none | P0 |
| `engine/rules/runtime.py:125-158` | `evaluate_rule_with_score` | legacy loader/rule | load/get/registry iteration | I/O/global state/programming errors | `INFRASTRUCTURE_ERROR`/programming error | pass/None/no merge | continues | Yes | No | No | No | No | No | active Career | merge happy path only | P1 |
| `engine/rules/runtime.py:165-205` | `evaluate_rule_with_score` | legacy rule | factual/scoring branch | any evaluation error | `UNEXPECTED_PROGRAMMING_ERROR` or input/capability accident | false, score zero, fixed error evidence | unmatched | cause/class swallowed | fixed text only | No | generic error evidence | No | No | active Career | none | P0 |
| `engine/rules/runtime.py:231-245` | `evaluate_rule_with_score` | legacy serialization | Pydantic V2 export | API/version mismatch | `CONTRACT_VIOLATION` | fall back to `.dict()` | inherited | first exception swallowed | No | No | inherited | No | No | active | indirect | P2 |
| `engine/rules/runtime.py:270-278` | module bootstrap | legacy loader | auto-load | path/YAML/registry error | `INFRASTRUCTURE_ERROR` | pass | none | Yes | No | No | No | No | No | active import | none | P1 |
| `engine/interpreters/career.py:45-52` | `interpret_career` | domain | scored evaluator | any exception | mixed/unknown | call legacy simple evaluator | legacy matched/zero | scored error swallowed | No | No | fallback evidence only | implicit retry only | No | active | snapshots only | P0 |
| `engine/interpreters/career.py:55-64` | `interpret_career` | domain | false/error result | result consumption | `CONTRACT_VIOLATION` | omit nonmatched/nonpositive row | ordinary zero contribution | error evidence lost | No | No | only matched-positive | No | No | active | no error test | P0 |
| `tests/testing_framework/generate_full_artifacts.py:56-78` | `save_rule_traces` | test artifact | legacy rules | evaluator exception | `UNKNOWN` | false trace with `str(e)` | untyped unmatched | converted | Yes, artifact JSON | No explicit traceback | raw message as evidence | No | No | test/tool | none | P2 |
| `tests/testing_framework/snapshot_runner.py:13-17` | `run_and_compare` | test tool | full generation | any generator exception | `UNKNOWN` | false dict with formatted exception | untyped unmatched | converted | Yes, returned tool result | No explicit traceback | raw message field | No | No | test/tool | none | P2 |
| `tools/runner_api.py:25-105`; `frontend/app/api/astro/generate/route.ts:46-67` | runner `main`; API `POST` | public output | snapshot generation | input/import/provider/generation/server errors | mixed input/infrastructure/programming | stderr then nonzero; API relays stderr/detail | HTTP 500 error dict | cause not typed | Yes, public detail/log | Possible if child stderr contains one | no predicate identity | No | No | active public | none | P0 |

Inventory count: **37**. Handling classifications overlap by design: every path is untyped; **14** paths convert an error/definition/capability defect to ordinary unmatched/false behavior, and **15** discard the originating exception or distinction (`SWALLOWED`). No path is `TYPED_AND_PRESERVED` or `TYPED_WITH_INFORMATION_LOSS`.

## 5. Typed Error-Model Assessment

No canonical `PredicateError` or equivalent exists. `PredicateResult.errors` is `List[Dict[str, Any]]` inside a frozen dataclass (`engine.py:9-18`), so the list, dictionaries, and nested details are mutable. Error producers use three central shapes:

- `{'error':'invalid_return_type','type':str(type(out))}`;
- `{'error':str(exc)}`;
- `{'error':'missing_type'}`.

Legacy rule/Yoga/tool paths add reason/evidence/error strings rather than predicate error objects. None guarantees stable `code`, safe public `message`, embedded `predicate_id`, immutable JSON-safe `details`, or `recoverable`. Parent results sometimes retain predicate identity, but condition flattening and downstream adapters make origin ambiguous. There is no canonical serializer or constructor validation.

Prompt-01 therefore requires a predicate-owned immutable model. Existing Pydantic `RuleMatch`, Yoga dictionaries, validation exceptions, and evidence dictionaries cannot be reused because their ownership and semantics differ. Audit-6's zero-model conclusion remains current.

## 6. Error-Code Inventory

| Code/Reason | Defined At | Representation | Producers | Consumers | Stable | Recoverable | Serialized | Duplicate/Alias | Prompt-01 Status | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| `INVALID_PARAMETERS` | Prompt-01 only | absent | none | none | No | No | No | invalid values currently false/raw exception | `MISSING` | P0 |
| `MISSING_CAPABILITY` | Prompt-01 only | absent | none | none | No | No | No | missing facts currently false | `MISSING` | P0 |
| `MISSING_PLANET` | Prompt-01 candidate; runtime has `planet_not_found` | ad hoc evidence reason | legacy runtime only | Career drops when false | No canonical code | No | internal dict only | `planet_not_found`, empty registered evidence | `MISSING` | P1 |
| `MISSING_HOUSE` | Prompt-01 only | absent | none | none | No | No | No | false/empty evidence | `MISSING` | P1 |
| `MISSING_VARGA` | Prompt-01 only | absent | none | none | No | No | No | Yoga prep swallow | `MISSING` | P1 |
| `MISSING_ASPECT_GRAPH` | Prompt-01 example | absent | none | none | No | No | No | empty graph/nonmatch/prep swallow | `MISSING` | P0 |
| `UNKNOWN_REFERENCE` | Prompt-01 only | absent | none | none | No | No | No | no reference system | `MISSING` | P1 |
| `UNKNOWN_PREDICATE` | Master target; current `unknown_predicate` reason | evidence string, `errors=[]` | generic evaluator | condition/Yoga matched logic | lower-case reason stable only locally | No | possible `asdict`; Yoga drops ID/error | unknown operator shares path | `NONCOMPLIANT` | P0 |
| `UNKNOWN_OPERATOR` | audit candidate | absent | none | none | No | No | No | mis-aliased to unknown predicate; dormant `unknown_condition_type` | `MISSING` | P0 |
| `INVALID_RETURN_TYPE` | current `invalid_return_type` | mutable error dict | generic evaluator | condition aggregation/test serialization | local string only | No | possible | evidence uses `invalid_predicate_return` alias | `NONCOMPLIANT` | P0 |
| `PREDICATE_EXCEPTION` | Prompt-01; current `predicate_error` reason | evidence reason + raw-message error dict | generic evaluator | cache/condition; Yoga drops | reason stable, message not | No | possible | legacy `evaluation_failed` | `NONCOMPLIANT` | P0 |
| `PREDICATE_TIMEOUT` | Prompt/Master | absent | none | none | No | No | No | none | `MISSING` | P1 |

Missing canonical stable error codes: **12** candidate categories. Ad hoc aliases are not counted as implementations because they lack a typed code field and consistent semantics.

Four invalid-return-type gaps are counted: no typed code/status/model; no tuple-shape/evidence validation; no strict-mode raise for programming defects; and unconditional caching of the false error result.

## 7. Exception Classification

Expected input errors include missing/invalid parameters and malformed direct condition input; they currently become false or handler exceptions. Expected missing data/capability includes unavailable aspect graph, roles, vargas, planet/house facts, and enrichments; it currently becomes false, empty facts, or swallowed preparation.

Rule-definition errors include unknown predicates/operators, malformed YAML/rules/nodes, duplicate IDs, invalid top-level Yoga definitions, and unsupported legacy rule types. Most are skipped or deferred to false runtime outcomes. Contract violations include invalid handler returns, malformed legacy tuples, mutable/contradictory result construction, and failed serializer/cache replacement. Unexpected programming errors are broadly captured by generic handler, Yoga preparation, legacy runtime, and Career catches, so tests cannot reliably surface defects.

Infrastructure errors include file access, configuration-table access, import/bootstrap, and subprocess/provider failures. They are usually swallowed or flattened into raw text. No `TIMEOUT_OR_CANCELLATION` path exists. Several broad catches protect mixed classifications; because no code/status/strict policy exists, callers cannot tell which class occurred.

## 8. Predicate Evaluator Error Handling

The generic evaluator builds its cache key before validation. JSON serialization uses `default=str`, then catches any remaining exception and uses `str(params)`, which can be unstable and collision-prone. Unknown IDs return cached false with `errors=[]`. Parameters are never validated; missing capability is not declared; both commonly become normal unmatched handler results.

Legacy tuples are accepted without checking length, evidence type, predicate identity, or error semantics. Unpacking/coercion failures enter the same handler-exception catch. A non-tuple/non-`PredicateResult` return becomes a false error-like result, but no status or strict failure exists. A handler exception becomes false with safe generic evidence and raw exception text in `errors`; class, stable code, recoverability, internal trace, and source location are lost.

Every result branch is cached, including unknown ID, invalid return, invalid-parameter exception, missing-capability-as-false, and unexpected exception. Cache write failure is swallowed. No serialization validation or timeout applies. There is no `fail_on_error` evaluation/rule metadata and no development/production behavioral distinction.

The in-memory probe confirmed that the warm exception result retains the same raw message and cold timing while only `cache_hit` changes. This proves both sticky failure and telemetry/logical inequality without relying on static inference.

## 9. Condition Evaluator Error Handling

AND/OR evaluate every child left-to-right, flatten all child error dictionaries, and create trace summaries containing child ID, match, errors, and timing. Full child results/status/recoverability do not exist. Current outcomes are:

| Scenario | Current Match | Current Error Handling | Required Decision |
|---|---|---|---|
| `AND(unmatched,error)` | false | error flattened; parent otherwise indistinguishable from unmatched | precedence/status and whether later child runs |
| `OR(error,matched)` | true | raw child error remains on matched parent | matched-with-warning versus error policy |
| `OR(error,unmatched)` | false | error flattened; looks like false-with-errors | error versus unmatched precedence |
| `NOT(error)` | false unknown-predicate path | NOT is treated as unknown predicate; original child never runs | implement/validate NOT and propagate child error |

There is no short circuit, skipped branch, timeout, node identity, or nested typed child preservation. Error order follows raw child list order, but raw error messages/timing remain nondeterministic. Malformed roots, non-list children, non-dict children, excessive depth, and cycles can raise uncontrolled exceptions. No condition boundary catches them or attaches rule/source location.

| Error Source | Predicate Result | Condition Handling | Yoga Handling | Domain Handling | Output Handling | Status Preserved | Error Preserved | Evidence Preserved | Trace Preserved | Information Lost | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| handler exception | false result with raw-message dict | error flattened; boolean decides parent | errors discarded; ordinary Yoga boolean | not on generic Career path | direct serialization possible only through debug/asdict | No | condition only | generic reason only | timing summary only | class, safe code, recoverability, lineage | P0 |
| invalid parameters | false, broad match, or caught exception | treated as ordinary leaf outcome | ordinary Yoga match/nonmatch | legacy runtime false/zero | usually omitted | No | usually No | partial/empty | No | parameter location, expected/actual, status | P0 |
| missing capability | ordinary false/empty result | treated as false child | ordinary Yoga nonmatch after prep swallow | zero/no indicator | omitted | No | No | usually No | No | capability identity and recovery dependency | P0 |
| unknown predicate/operator | cached false; unknown operator aliases to predicate | boolean aggregate | emitted as Yoga nonmatch | legacy unsupported false | omitted | No | No | wrong/ad hoc reason | No | definition location and correct category | P0 |
| loader/validation failure | no predicate result | no condition evaluated for skipped rule | rule absent silently | registry metadata may be absent | no diagnostic | No | No | No | No | source, code, rule identity, all failures | P0 |
| Yoga preparation failure | later predicates see partial state | results depend on remaining facts | swallowed; partial Yoga rows | no Yoga consumer | Yoga errors absent from current snapshot | No | No | partial factual evidence | random replacement ID | failed capability/stage and mutation history | P0 |
| legacy rule evaluation exception | no PredicateResult; false scored dict | generic condition bypassed | N/A | Career drops false evidence or retries simpler evaluator | Career JSON contains no error | No | No | fixed evidence then lost | No | exception class, rule failure, retry lineage | P0 |

## 10. Rule Loader and Compiler Errors

The generic loader catches all file/open/YAML/record exceptions and continues. The Yoga parser returns `[]` for any path, I/O, or parse exception. Yoga validation raises a message-bearing `ValueError`, but the public loader catches all exceptions and skips the rule. Duplicate IDs overwrite silently. Neither loader validates predicate IDs, parameters, versions, capabilities, operators, arity, cycles, or registry readiness.

Consequently four unknown-predicate paths are incorrect: Yoga YAML, direct generic condition, generic/legacy rule definition, and Python-created runtime rule use. Two unknown-operator paths are incorrect: generic condition fallthrough and dormant Yoga local dispatch. Definition defects can be skipped, overwritten, or executed as factual nonmatch. There is no compiler, source-location model, error aggregation, quarantine report, or strict production startup failure.

## 11. Yoga Error Handling

Yoga has two counted error-loss paths, consistent with Audit-15:

1. The active generic path receives untyped predicate/condition errors but `evaluate_yoga_rules` reads only `.matched` and `.evidence`; it discards errors, trace steps, inputs, cache/timing, and any future status. Invalid/unavailable/errored rules become ordinary Yoga nonmatches.
2. The dormant tuple evaluator returns false/reason or skips edge failures and has no error channel. Although confirmed unused, activating it would restore silent parallel error semantics.

Additionally, active Yoga swallows varga/aspect preparation, functional-role preparation, load/validation, and final AstroState storage failures. Preparation mutates state before later failures, so partial state can be evaluated. It returns partial/all rule dictionaries rather than a typed partial-error result. UUID4 trace IDs and set-to-list planet ordering replace rather than preserve predicate traces.

## 12. Domain Runtime Error Handling

Career has three counted error-loss conversion boundaries from Audit-16: rule dict to matched/contribution, reduced explainability input, and synthetic confidence input. The legacy runtime catches factual/scoring errors and emits false/zero with fixed evidence; Career's broad catch retries using the simpler evaluator. The fallback has no classification, retry marker, or protection if it also raises.

Unmatched/error evidence is omitted because only matched positive contributions become indicators. Missing capabilities and invalid inputs can reduce apparent rule coverage/confidence as if the fact were negative. Public Career output exposes no internal raw exception text, but only because errors are discarded. The constant `career_001` is not linked to error lineage. Wealth remains a constant placeholder and has no error behavior.

## 13. Cache-Related Errors

Four sticky cache-error categories are retained from Audit-11:

1. ordinary unmatched after mutable state changes;
2. missing capability represented as unmatched before enrichment recovery;
3. invalid parameters represented as unmatched or caught error;
4. handler exception/error after transient dependency recovery.

Unknown-predicate and invalid-return results are also cached manifestations of the definition/contract categories. Keys omit state digest, predicate version, capability/configuration versions, context, and recovery dependencies. Error objects are shallowly shared and mutable; corrupted entries are neither detected nor evicted. Retrieval has no catch or validation. There is no partial-write transaction, TTL, targeted invalidation, timeout policy, or recovery retry. Yoga's global clear is caller-specific and race-prone.

## 14. Raw Exception and Sensitive-Data Exposure

| File | Symbol | Exposed Value Type | Destination | Internal/Public | Sensitive Risk | Stack Trace Risk | Current Protection | Required Action | Priority |
|---|---|---|---|---|---|---|---|---|---|
| `engine/rules/engine.py:119-132` | `evaluate_predicate` | `str(exc)` | `PredicateResult.errors` -> cache/condition/asdict-capable result | internal currently, contract may serialize | parameter/path/provider content possible | Low; message only | generic evidence hides details but error does not | stable safe code/message; secure internal exception log | P0 |
| `tests/testing_framework/generate_full_artifacts.py:56-78` | `save_rule_traces` | `str(exc)` | `rule_traces.json`/Career trace artifact | test artifact | paths/values possible | Low | none | sanitize or typed artifact projection | P2 |
| `tests/testing_framework/snapshot_runner.py:13-17` | `run_and_compare` | formatted exception | returned comparison dict | test/tool | paths/input values possible | Low | fixed prefix only | safe diagnostic separation | P2 |
| `tools/runner_api.py:25-105` | `main` | raw exception message on stderr | child stderr | internal process boundary | input/provider/path/import detail possible | Medium if uncaught code writes traceback | labels only | stable internal logging and safe outward code | P1 |
| `frontend/app/api/astro/generate/route.ts:46-67` | `POST` | complete stderr or `String(err)` | HTTP 500 `detail`; server console | public and internal | birth/provider/path/environment detail possible | High: entire child stderr relayed | none | never relay stderr; public stable code/correlation only | P0 |

Raw exception exposure paths: **5**. Stack-trace exposure risks: **1**. No secret was found during the audit. Raw request payloads are not inserted into predicate errors, but runner/provider exception messages and stderr may incorporate sensitive values; the report intentionally does not reproduce any real value.

## 15. Logging and Observability

Predicate, condition, loader, Yoga, and Career code has no production logger and emits no stable error code, predicate ID, rule ID, trace/run ID, or secure stack trace. Broad catches substitute for observability. The M1 runtime imports test instrumentation, but those hooks record coverage, not errors, and their failures are swallowed.

The Python runner prints labeled exception messages to stderr. The Next route logs complete stderr, runner paths, invalid stdout, and server errors with `console.error`; it also relays stderr publicly. Logging has no redaction, structured code, correlation ID, environment policy, or duplication rule. Internal exception detail is not securely separated from returned errors.

Because logging does not affect successful JSON but API error `detail` incorporates runtime text, error output is environment-dependent. Prompt-01 should define internal logging without making logging itself part of deterministic predicate results.

## 16. Strict Development Mode

No strict mode, `fail_on_error`, evaluation mode, rule metadata switch, environment-variable activation, or test fixture exists for predicate failures. Production and tests use the same broad-conversion behavior. Six strict-mode gaps are counted:

1. invalid handler return type does not fail;
2. malformed tuple return does not fail clearly;
3. duplicate registration/metadata defects silently replace or proceed;
4. impossible future status/matched/error combinations are not validated;
5. malformed condition nodes/operators can become false or uncontrolled generic exceptions;
6. unexpected predicate/programming exceptions cannot be surfaced by configured strict runs.

Default, activation, production behavior, logging, and deterministic strict-mode tests are all absent.

## 17. Recoverability and Retry Semantics

No error carries `recoverable`. Callers cannot distinguish permanent rule-definition defects from missing prepared capabilities, transient I/O, or programming errors. There is no formal retry policy.

Career performs one implicit fallback retry: any exception from `evaluate_rule_with_score` invokes `evaluate_rule`, potentially changing evaluation coverage and score. Yoga performs preparation before evaluation but swallows failure rather than recording a retry or invalidating recovery-dependent cache entries. Loader/bootstrap code may retry implicitly on later calls when registries remain empty. There is no timeout retry, backoff, cache eviction after recovery, or permanent-error quarantine.

These fallbacks may change logical behavior depending on which attempt fails. Prompt-01 must make failure policy explicit without turning all failures into retryable events.

## 18. Determinism and Error Ordering

Six nondeterministic error mechanisms are counted:

1. raw `str(exception)` messages can contain library/version/path/value-specific text;
2. `_cache_key` fallback `str(params)` can include unstable object representations;
3. `evaluation_time_ms` appears in error results and condition child traces;
4. cache warmth retains cold timing/raw error and changes `cache_hit`;
5. CWD/import/global registry/file iteration changes which loader errors occur or are suppressed;
6. Yoga replaces lost error traces with UUID4 IDs and set-derived ordering.

Within one valid raw condition tree, child error flattening is list-ordered. Across file/registry inputs, no canonical ordering or multi-error collection exists. Silent loader skipping means error absence itself varies with environment. Logical error identity is not separated from telemetry.

## 19. Serialization and Public-Schema Impact

Six serialization impacts are counted:

1. `dataclasses.asdict(PredicateResult)` recursively exposes mutable raw error dictionaries; the only test uses `json.dumps(..., default=str)`.
2. condition results embed errors both in the root list and trace summaries, duplicating mutable/raw content.
3. Yoga discards those fields and serializes ordinary custom dictionaries, so adding typed errors can change Yoga shape and snapshots if later wired.
4. Career/runtime drops or converts errors before the public snapshot, so preserving errors can change indicators, confidence, and domain JSON.
5. test artifact and snapshot helpers serialize raw exception messages into result/artifact dictionaries.
6. runner/API error output relays stderr/raw detail to public JSON and frontend consumers.

Typed immutable mappings, tuples, enums, and error objects will require an explicit serializer; current `json.dumps(default=str)` must not become the public schema policy. Stable field ordering, enum values, empty error collections, safe details, and schema-version decisions are missing. No snapshot should be updated merely to bless raw exception content.

## 20. Existing Tests and Coverage Gaps

The direct predicate suite covers one handler exception only by asserting a nonempty error list. It does not assert safe message, code, identity, status, cache policy, or propagation. Yoga loader tests cover one direct `ValueError` but not the public loader's silent skip. Existing Yoga/Career/snapshot tests assert output shape or valid-path behavior, not errors.

| Area | Missing Categories | Count | Risk | Recommended Test File |
|---|---|---:|---|---|
| Predicate errors | invalid parameters; missing capability; unknown predicate; invalid return; timeout; safe message; stable code; predicate identity; immutable details; recoverability | 10 | failures remain indistinguishable/unsafe | `tests/rules/test_predicate_errors.py` |
| Propagation | predicate-to-condition; condition-to-Yoga; condition-to-domain; aggregation; short circuit; child identity; evidence/trace preservation | 7 | errors disappear or alter matches | `tests/rules/test_error_propagation.py` |
| Safety | no raw stack trace; no secret/raw-payload exposure; JSON-safe details; deterministic serialization; public filtering | 5 | sensitive or unstable diagnostics become public | `tests/rules/test_error_safety.py` |
| Cache/strict | nonsticky recovery; strict invalid return; safe production conversion; cold/warm logical identity | 4 | transient/programming errors become permanent false facts | `tests/rules/test_error_cache_strict.py` |

Missing error-handling test categories: **26** of the 27 prescribed categories. Only basic handler-exception conversion is partially covered, and even that test is insufficient for Prompt-01 acceptance.

## 21. Prompt-01 Compliance Matrix

| Requirement | Status | Evidence | Affected Files | Required Change | Scope | Priority | Blocking Completion |
|---|---|---|---|---|---|---|---|
| Immutable typed PredicateError | `MISSING` | dict lists only | engine/supporting models | approved frozen model/serializer | `IN_SCOPE` | P0 | Yes |
| Explicit status/error invariants | `MISSING` | matched boolean only | engine/callers | typed status and validated constructors | `IN_SCOPE` | P0 | Yes |
| Invalid parameters distinct | `NONCOMPLIANT` | false/raw exception | validation/handlers | pre-invocation validation and code | `IN_SCOPE` | P0 | Yes |
| Missing capability distinct | `NONCOMPLIANT` | false/prep swallow | predicates/Yoga | capability checks and typed recoverable errors | `IN_SCOPE` | P0 | Yes |
| Unknown definitions rejected | `NONCOMPLIANT` | four predicate/two operator paths | loaders/condition/runtime | deterministic load/compile validation | `IN_SCOPE` | P0 | Yes |
| Safe handler exception conversion | `NONCOMPLIANT` | raw `str(exc)` and cached | engine | safe public message/code; internal detail policy | `IN_SCOPE` | P0 | Yes |
| Condition error precedence/preservation | `MISSING` | boolean aggregate/flat dicts | condition/Yoga | approved typed child/status semantics | `IN_SCOPE` | P0 | Yes |
| Invalid return contract enforcement | `PARTIAL` | false dict exists | engine/registry | typed production conversion plus strict failure | `IN_SCOPE` | P1 | Yes |
| Timeout/cancellation handling | `MISSING` | no mechanism | evaluator/condition/cache | typed timeout and policy | `IN_SCOPE` | P1 | Yes |
| Recovery-aware error cache | `NONCOMPLIANT` | four sticky categories | engine/cache/Yoga | explicit cacheability/invalidation | `IN_SCOPE` | P1 | Yes |
| Strict development behavior | `MISSING` | broad catches only | registry/evaluator/loaders/tests | explicit deterministic mode | `IN_SCOPE` | P1 | Yes |
| Deterministic error ordering/identity | `NONCOMPLIANT` | raw text/timing/global order | engine/loaders/Yoga | canonical code/details/order; telemetry separation | `IN_SCOPE` | P1 | Yes |
| Preserve errors through Yoga | `NONCOMPLIANT` | `.errors` ignored | Yoga | typed result propagation/compat adapter | `IN_SCOPE` | P1 | Yes |
| Preserve errors through Career/domain | `NONCOMPLIANT` | three loss boundaries | runtime/Career | typed compatibility path | `IN_SCOPE` | P1 | Yes |
| Error-focused acceptance tests | `MISSING` | 26 categories | tests | focused suites | `IN_SCOPE` | P1 | Yes |
| Secure internal logging | `MISSING` | no predicate logger; stderr raw | engine/runner/API | structured internal logs/redaction | `IN_SCOPE` | P2 | No |
| Public error filtering/schema | `NONCOMPLIANT` | API relays stderr | runner/API/output | safe public codes/schema version | `TEMPORARY_COMPATIBILITY` | P2 | No |
| Source-attributed loader diagnostics | `MISSING` | skips/no locations | loaders | deterministic diagnostic collection | `IN_SCOPE` | P2 | No |
| Legacy runtime fallback isolation | `PARTIAL` | Career broad fallback | runtime/Career | bounded adapter preserving valid scores | `TEMPORARY_COMPATIBILITY` | P2 | No |
| Universal RuleMatch failure policy | `MISSING` | legacy dict only | future rule engine | Prompt-02 contract | `OUT_OF_SCOPE_FUTURE_STAGE` | P3 | No |
| Public warnings/errors OutputAssembler | `MISSING` | assembler absent | future output layer | typed output stage | `OUT_OF_SCOPE_FUTURE_STAGE` | P3 | No |

## 22. Migration Risks and Priorities

The 21 findings total **P0=7, P1=8, P2=4, P3=2**.

P0 work must prevent false facts: create typed immutable status/errors, validate parameters/capabilities/definitions, remove raw exception content from logical results, and define condition precedence. P1 completes invalid-return, timeout, cache, strictness, determinism, Yoga/domain propagation, and test coverage. P2 addresses secure logging, public filtering, source diagnostics, and bounded Career compatibility. P3 belongs to later universal RuleMatch/output stages.

Major compatibility risks are changing current Yoga emission when `HOUSE_LORDS_COMBINATION` becomes a definition error, changing Career scores/confidence when failure candidates stop appearing as unmatched, changing cache warmth behavior, and exposing new error fields through snapshots/API. Valid factual matches must remain stable, but silent loader skips, raw exception strings, and missing-capability-as-negative behavior are defects rather than compatibility guarantees.

## 23. Unresolved Architectural Questions

1. What exact invariant relates `matched`, `status`, and a nonempty error tuple?
2. Which expected predicate exceptions are converted in production, and which unexpected exceptions re-raise in strict development?
3. What safe-message catalog and detail allowlist applies to each stable code?
4. Which error/status categories are cacheable, for how long, and against which recovery dependencies?
5. What deterministic precedence applies to the four mixed AND/OR/NOT error scenarios?
6. Which load/compile defects prevent production startup versus quarantine experimental rules?
7. How do Yoga and temporary Career dictionaries expose or retain errors without prematurely redesigning public schemas?
8. What run/trace correlation may be public while internal exception detail stays private?
9. Where is timeout enforced and how is cancellation distinguished from a predicate exception?
10. Should runner/API error filtering be fixed within Prompt-01 or coordinated with the future OutputAssembler while immediately preventing raw stderr exposure?

These decisions affect implementation but do not block completion of this audit.

## 24. Audit-17 Conclusion

Audit-17 is COMPLETE. Thirty-seven predicate-related error paths are all untyped; fourteen convert defects/failures to unmatched and fifteen swallow their origin or semantic distinction. There are five raw-exception exposures, one stack-trace exposure risk, twelve missing canonical code categories, four invalid-return gaps, four incorrect unknown-predicate paths, two incorrect unknown-operator paths, five missing timeout-layer paths, four sticky cache-error risks, two Yoga error-loss paths, three domain error-loss paths, six strict-mode gaps, six nondeterministic error mechanisms, six serialization impacts, and twenty-six missing test categories. Exactly this report was created; no code, tests, rules, fixtures, snapshots, previous reports, or Audit-18 artifacts were modified.

### Summary counts

| Metric | Count |
|---|---:|
| Predicate-related error paths | 37 |
| Typed and preserved paths | 0 |
| Typed paths with information loss | 0 |
| Untyped error paths | 37 |
| Errors converted to unmatched | 14 |
| Swallowed exceptions/distinctions | 15 |
| Raw exception exposures | 5 |
| Stack-trace exposure risks | 1 |
| Missing stable error-code categories | 12 |
| Unknown-predicate incorrect paths | 4 |
| Unknown-operator incorrect paths | 2 |
| Invalid-return-type gaps | 4 |
| Missing timeout handling layers | 5 |
| Sticky cache-error risks | 4 |
| Yoga error-loss paths | 2 |
| Domain error-loss paths | 3 |
| Strict-mode gaps | 6 |
| Nondeterministic error mechanisms | 6 |
| Public serialization impacts | 6 |
| Missing error-handling test categories | 26 |
| P0 findings | 7 |
| P1 findings | 8 |
| P2 findings | 4 |
| P3 findings | 2 |
