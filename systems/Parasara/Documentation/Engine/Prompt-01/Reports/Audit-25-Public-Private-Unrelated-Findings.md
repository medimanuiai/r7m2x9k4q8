# Prompt-01 Audit-25: Public/Private and Unrelated Findings

## 1. Executive Summary

Audit-25 is complete as a repository-local, read-only exposure and scope-protection review. All 24 prerequisite reports exist. No probable or confirmed embedded live secret was found. Seven credential-shaped candidate groups were identified: four documentation/example placeholders, one tracked test-fixture credential group, and two code/config references that do not contain a stored credential value.

Urgent release-facing exposure does exist. Two tracked Parāśara datasets contain names together with exact birth metadata and lack the repository's anonymization marker. The public astrology generation route returns the complete raw generated chart without an allowlist and relays child-process error detail. Tracked/generated report artifacts also preserve raw charts, traces, derived states, and test output, and CI uploads the report tree. No secret or personal value is reproduced here.

Prompt-01 remains bounded. Eight consolidated contract/migration/acceptance groups from Audits 1–24 block Prompt-01. Fifteen unrelated or later-stage groups do not block it; thirteen map to later architecture or governance stages and two are independently urgent release/compliance work. Public/privacy and licensing concerns require owner action before publication or release, but do not justify expanding the typed predicate-result implementation.

## 2. Audit Scope, Safety Rules and Method

The audit covered tracked source, tests, fixtures, rules, configuration, workflows, scripts, documentation, snapshots, reports, ignore controls, and repository-local licensing evidence. It reconciled Reports 1–24 and inspected the active output/error/artifact paths identified by Audits 17–20.

Searches were metadata-only: candidate values were never printed, copied, authenticated, uploaded, or sent to an external scanner. Credential candidates were classified from file context and value-shape indicators only. Personal-data inspection counted field categories and anonymization markers without reproducing names, dates, coordinates, account identifiers, or credentials. Repository history was not inspected, so historical exposure is `UNKNOWN` and is not claimed.

No scanner was installed; no network call was made; no production code, test, fixture, rule, configuration, workflow, prior report, repository setting, credential, or history was changed. Only this report was created.

## 3. Reconciliation with Audits 1–24

| Audit | Reconciled contribution | Prompt-01 disposition |
|---|---|---|
| 01 Predicate Registry | split registration, divergent wrappers, and registry identity | contract blocker |
| 02 Predicate Inventory | six active typed-registry predicates plus legacy factual helpers | contract and migration blocker |
| 03 Legacy Return Contracts | Boolean, tuple, list, dictionary, and typed-result compatibility | migration blocker |
| 04 Caller Inventory | Yoga direct migration and Career indirect compatibility | migration blocker; inference redesign deferred |
| 05 PredicateResult Model | mutable/unvalidated result and unresolved normalization/serialization policy | contract blocker |
| 06 Supporting Models | trace/evidence/error model gaps | bounded contract blocker; run-level tracing deferred |
| 07 Parameter Validation | validation, normalization, and duplicate/unknown parameter policy | contract blocker |
| 08 Capability Handling | implicit enrichment preparation and missing capability contract | contract blocker; broader capabilities deferred |
| 09 AstroState Boundary | mutable state, weak identity, and unsafe cache dependencies | contract blocker; stable query API deferred |
| 10 Predicate Purity | mutation/nondeterminism boundary and Yoga UUID concern | contract blocker; Yoga/run identity redesign deferred |
| 11 Predicate Cache | identity-keyed mutable cache and invalidation gaps | contract blocker; distributed cache deferred |
| 12 Condition Evaluator | recursive aggregation loses typed semantics | contract blocker |
| 13 Condition Format | five active formats and future DSL constructs | compatibility blocker; compiler/AST deferred |
| 14 Loader/Compiler | loader normalization and runtime bridge requirements | compatibility blocker; compiler/optimizer/governance deferred |
| 15 Yoga Engine | active custom result/trace dictionaries and preparation mutation | direct migration blocker; universal RuleMatch deferred |
| 16 Domain Runtime | Career behavior must remain stable | compatibility blocker; shared inference/output models deferred |
| 17 Error Handling | raw exceptions and inconsistent failure policy | safe-contract blocker; public output policy partly later-stage |
| 18 Evidence | inconsistent evidence ownership and linkage | safe-contract blocker; universal evidence model deferred |
| 19 Trace | unbounded/mutable traces and UUID identity | safe-contract blocker; run correlation deferred |
| 20 Serialization/Public Output | no explicit predicate serializer; raw public envelope discovered | bounded serializer blocker plus urgent independent release risk |
| 21 Determinism | state/cache/order/time nondeterminism | contract blocker; Dasha evaluation clock deferred |
| 22 Test Inventory | required contract, compatibility, determinism, and regression tests missing | acceptance blocker |
| 23 CI Validation | active tests run, but contract/safety gates are incomplete | acceptance blocker; broader DevOps deferred |
| 24 Documentation | missing Prompt-01 completion row, decisions, and migration/current-state docs | completion blocker; five future guides deferred |

All expected report filenames are present. No prerequisite report was missing and no previous report was modified.

## 4. Secret and Credential Findings

No `CONFIRMED_LIVE_SECRET`, `PROBABLE_SECRET`, private-key marker, or provider-token-shaped value was found by the safe local scan. Candidate context follows; values are deliberately omitted.

| Finding ID | File | Location | Category | Secret/Data Type | Classification | Tracked/Generated | Exposure Surface | Urgency | Recommended Owner Action | Prompt-01 Impact | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | `auth-scaffold/.env.example` | line 10 | SECRET_OR_CREDENTIAL | session-signing secret example | PLACEHOLDER_OR_EXAMPLE | tracked/example | public repository content | LOW_BACKLOG | retain only an unmistakable placeholder; verify deployment injects a real value | DOES_NOT_BLOCK_PROMPT_01 | P3 |
| S02 | `auth-scaffold/README.md` | lines 111–113 | SECRET_OR_CREDENTIAL | environment credential examples | PLACEHOLDER_OR_EXAMPLE | tracked/documentation | public documentation | LOW_BACKLOG | keep examples nonoperational and aligned with ignore guidance | DOES_NOT_BLOCK_PROMPT_01 | P3 |
| S03 | `Documentation/04_AI_ENGINE_SPEC.md` | lines 49–51 | SECRET_OR_CREDENTIAL | connection/API configuration examples | PLACEHOLDER_OR_EXAMPLE | tracked/documentation | public documentation | LOW_BACKLOG | retain placeholder-only examples | DOES_NOT_BLOCK_PROMPT_01 | P3 |
| S04 | `Documentation/07_AUTH_SPEC.md` | lines 28, 97, 311 | SECRET_OR_CREDENTIAL | auth/database configuration examples | PLACEHOLDER_OR_EXAMPLE | tracked/documentation | public documentation | LOW_BACKLOG | retain placeholder-only examples and document secret injection | DOES_NOT_BLOCK_PROMPT_01 | P3 |
| S05 | `auth-scaffold/server/data/accounts.json` | lines 1–260 | SECRET_OR_CREDENTIAL | 43 credential-shaped test records and email-shaped identifiers | TEST_FIXTURE_VALUE | tracked/test scaffold | repository and any packaged scaffold | HIGH_BEFORE_PUBLICATION_OR_RELEASE | confirm synthetic ownership; remove from release artifacts or replace with generated fixtures | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |
| S06 | `.github/workflows/ci.yaml` | line 36 | FALSE_POSITIVE | CI secret-context reference, no stored value | FALSE_POSITIVE | tracked/configuration | CI runtime only | INFORMATIONAL | no credential action; preserve secret-context use | DOES_NOT_BLOCK_PROMPT_01 | P3 |
| S07 | `tests/testing_framework/create_snapshot_pr_ci.py` | lines 2, 37–54 | FALSE_POSITIVE | runtime token reference and authenticated remote construction, no stored value | FALSE_POSITIVE | tracked/tool | CI process/log boundary | MEDIUM_PLANNED_REMEDIATION | prevent authenticated URLs or provider responses from reaching logs; use non-shell credential handling | DOES_NOT_BLOCK_PROMPT_01 | P2 |

Credential candidate counts: 7 total; confirmed/probable 0; placeholder/example 4; test-fixture value 1; false positive 2; unknown 0.

## 5. Sensitive Personal and Chart Data

| Finding ID | File | Location | Category | Secret/Data Type | Classification | Tracked/Generated | Exposure Surface | Urgency | Recommended Owner Action | Prompt-01 Impact | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D01 | `systems/Parasara/fixtures/historical_pilot_candidates.json` | lines 1–193 | PERSONAL_OR_CHART_DATA | 12 named records with exact birth time and coordinates; public-source/consent status unverified | UNKNOWN | tracked/fixture | public repository and test use | HIGH_BEFORE_PUBLICATION_OR_RELEASE | owner must establish lawful/public provenance or publish only reviewed anonymized data | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |
| D02 | `systems/Parasara/fixtures/sme_review_package_20.json` | lines 1–313 | PERSONAL_OR_CHART_DATA | 20 named records with exact birth time and coordinates; public-source/consent status unverified | UNKNOWN | tracked/review fixture | public repository and SME package | HIGH_BEFORE_PUBLICATION_OR_RELEASE | owner must establish provenance/consent or replace with reviewed anonymized package | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |
| D03 | `systems/Parasara/fixtures/golden_chart_01.json`; `surya_generated_chart.json`; `surya_test_chart.json` | birth metadata fields | PERSONAL_OR_CHART_DATA | exact chart time/location fixtures without personal identity | TEST_FIXTURE_VALUE | tracked/fixtures | repository/tests | MEDIUM_PLANNED_REMEDIATION | mark provenance and synthetic/public status explicitly | DOES_NOT_BLOCK_PROMPT_01 | P2 |
| D04 | `systems/Parasara/tests/fixtures/`; `systems/Parasara/tests/snapshots/`; `tests/dasha/`; `tests/enrichments/` | JSON fixtures/snapshots | PERSONAL_OR_CHART_DATA | derived chart and prediction data | TEST_FIXTURE_VALUE | tracked/test | repository/tests | MEDIUM_PLANNED_REMEDIATION | document fixture provenance and prohibit identifiable production inputs | DOES_NOT_BLOCK_PROMPT_01 | P2 |
| D05 | `tests/reports/artifacts/raw_surya.json`; `astrostate.json`; trace/domain files | tracked artifact tree | RAW_INPUT_EXPOSURE | raw chart, derived state, evidence, traces, and predictions | TEST_FIXTURE_VALUE | tracked/generated artifact | repository and CI artifact | HIGH_BEFORE_PUBLICATION_OR_RELEASE | generate only from approved synthetic inputs; define retention/redaction and stop tracking runtime reports | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |
| D06 | `tests/reports/artifacts/test_summary*.txt`; API diagnostics | generated diagnostics | INTERNAL_PATH_OR_METADATA | command output, environment-dependent paths, and exception metadata | UNKNOWN | tracked/generated | repository, logs, CI artifact | MEDIUM_PLANNED_REMEDIATION | sanitize and retain only bounded summaries | DOES_NOT_BLOCK_PROMPT_01 | P2 |
| D10 | Reports 1–24 | all sections | FALSE_POSITIVE | audit metadata only; no detected secret, personal value, raw payload, stack trace, or private home path | FALSE_POSITIVE | tracked/reports | documentation | INFORMATIONAL | continue metadata-only reporting | DOES_NOT_BLOCK_PROMPT_01 | P3 |

The repository includes `systems/Parasara/tools/anonymize_pilot.py`, but both named datasets are tracked without its `anonymized` marker and retain exact birth metadata. The script's existence is not evidence that the published inputs are approved or anonymized.

## 6. Raw Input, Error and Trace Exposure

| Finding ID | File | Location | Category | Secret/Data Type | Classification | Tracked/Generated | Exposure Surface | Urgency | Recommended Owner Action | Prompt-01 Impact | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D07 | `systems/Parasara/tools/runner_api.py` | `main`, lines 90–104 | RAW_INPUT_EXPOSURE | complete generated Surya chart added to response | UNKNOWN | tracked/runtime | PUBLIC_OUTPUT | HIGH_BEFORE_PUBLICATION_OR_RELEASE | owner must define an allowlisted response and raw-chart authorization policy | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |
| D08 | `frontend/app/api/astro/generate/route.ts` | `POST`, lines 46–67 | ERROR_OR_STACK_TRACE_EXPOSURE | raw child stderr and stringified server errors | UNKNOWN | tracked/runtime | PUBLIC_OUTPUT and server log | HIGH_BEFORE_PUBLICATION_OR_RELEASE | return stable error codes; keep sanitized diagnostics internal | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |
| D09 | `systems/Parasara/engine/rules/engine.py`; `tests/testing_framework/generate_full_artifacts.py` | exception paths; artifact generator lines 51–78, 162–173 | ERROR_OR_STACK_TRACE_EXPOSURE | raw exception strings embedded in typed errors, traces, or test output | UNKNOWN | tracked/runtime/generated | INTERNAL_ONLY and SNAPSHOT_OR_TEST_ARTIFACT; can flow outward through unfiltered callers | HIGH_BEFORE_PUBLICATION_OR_RELEASE | Prompt-01 should use bounded typed error metadata; release layer must filter details | BLOCKS_PROMPT_01 for typed error boundary only | P1 |

Raw-input exposure count is 4 paths: runner response, API pass-through, tracked raw-report generation, and CI/report publication. Error/stack-trace exposure count is 5 paths: predicate error capture, artifact trace capture, captured test stderr, public runner stderr detail, and public stringified server error detail. Internal-path/metadata exposure count is 3 paths: runner-path logging, environment-dependent test summaries, and unsanitized exception diagnostics.

### Public-output exposure inventory

| File | Symbol/Section | Data Exposed | Surface | Internal/Public | Current Filtering | Risk | Scope | Urgency | Priority |
|---|---|---|---|---|---|---|---|---|---|
| `systems/Parasara/tools/runner_api.py` | `main`, lines 96–101 | complete raw generated chart plus snapshot | HTTP response via caller | PUBLIC_OUTPUT | none; explicit full-object inclusion | raw chart and future private input can cross the public boundary | UNRELATED_BUT_URGENT | HIGH_BEFORE_PUBLICATION_OR_RELEASE | P1 |
| `frontend/app/api/astro/generate/route.ts` | `POST`, lines 58–60 | parsed runner JSON | HTTP response | PUBLIC_OUTPUT | no schema or allowlist | all present and future runner fields are exposed | UNRELATED_BUT_URGENT | HIGH_BEFORE_PUBLICATION_OR_RELEASE | P1 |
| `frontend/app/api/astro/generate/route.ts` | `POST`, lines 51–55 | raw child stderr | HTTP error response | PUBLIC_OUTPUT | none | internal paths, exception text, and process detail can leak | UNRELATED_BUT_URGENT | HIGH_BEFORE_PUBLICATION_OR_RELEASE | P1 |
| `frontend/app/api/astro/generate/route.ts` | `POST`, lines 66–67 | stringified server exception | HTTP error response | PUBLIC_OUTPUT | none | internal error metadata can leak | UNRELATED_BUT_URGENT | HIGH_BEFORE_PUBLICATION_OR_RELEASE | P1 |
| `tests/reports/artifacts/` | generated JSON/text/SVG | raw chart, state, traces, predictions, test output | repository/CI artifact | SNAPSHOT_OR_TEST_ARTIFACT | no content redaction | test data and diagnostics become durable/shared | UNRELATED_BUT_URGENT | HIGH_BEFORE_PUBLICATION_OR_RELEASE | P1 |
| `systems/Parasara/engine/rules/engine.py` | `PredicateResult.errors` construction | caller parameters and raw exception strings | internal typed result | INTERNAL_ONLY today | no bounded error schema | future serializers could accidentally publish internals | IN_SCOPE_PROMPT_01 | HIGH_BEFORE_PUBLICATION_OR_RELEASE | P1 |
| `systems/Parasara/schemas/parashara_output.schema.json` | output schema | broad generated output | schema/documented surface | UNKNOWN | schema is not enforced at API boundary | schema existence does not constrain actual pass-through output | OUT_OF_SCOPE_FUTURE_STAGE | MEDIUM_PLANNED_REMEDIATION | P2 |

There are 4 consolidated public-schema risks: full raw-chart inclusion, untyped API pass-through, public raw error detail, and absence of an enforced allowlisted response schema.

## 7. Logs, Snapshots and Generated Artifacts

| Finding ID | File | Location | Category | Secret/Data Type | Classification | Tracked/Generated | Exposure Surface | Urgency | Recommended Owner Action | Prompt-01 Impact | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G01 | `tests/reports/artifacts/`; `tests/reports/report.html`; `coverage_report.json` | complete trees | GENERATED_ARTIFACT_EXPOSURE | raw/derived chart data, traces, predictions, test output, coverage | TEST_FIXTURE_VALUE | tracked/generated | repository | HIGH_BEFORE_PUBLICATION_OR_RELEASE | define approved generated-output policy and stop tracking transient reports | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |
| G02 | `.github/workflows/ci.yaml` | lines 26–33 | GENERATED_ARTIFACT_EXPOSURE | complete `tests/reports` tree | UNKNOWN | generated/uploaded | CI artifact | HIGH_BEFORE_PUBLICATION_OR_RELEASE | upload only an allowlisted sanitized report set with retention/access policy | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |
| G03 | `.github/workflows/ci.yaml`; `tests/testing_framework/create_snapshot_pr_ci.py` | CI lines 34–40; tool lines 22–72 | GENERATED_ARTIFACT_EXPOSURE | changed reports/snapshots and provider response | UNKNOWN | generated/PR automation | branch, PR, and CI log | HIGH_BEFORE_PUBLICATION_OR_RELEASE | restrict staged paths, sanitize logs, and require reviewed synthetic inputs | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |
| G04 | `.gitignore` | lines 1–81 | GENERATED_ARTIFACT_EXPOSURE | report/artifact trees and general snapshots | UNKNOWN | tracked/configuration gap | repository | HIGH_BEFORE_PUBLICATION_OR_RELEASE | owner should define exclusions after deciding which golden artifacts are authoritative | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |
| G05 | `tests/tmp_snapshot.json`; `tmp_generated_snapshot.json` | complete files | GENERATED_ARTIFACT_EXPOSURE | temporary/generated snapshot data | TEST_FIXTURE_VALUE | tracked despite temporary naming | repository | MEDIUM_PLANNED_REMEDIATION | classify as golden or remove through a separately approved cleanup | DOES_NOT_BLOCK_PROMPT_01 | P2 |

Generated-artifact exposure count is 5. The files are not assumed private merely because they are test or CI outputs.

## 8. Repository Ignore and Protection Controls

`.gitignore` excludes common Python/Node build products, local virtual environments, databases, logs, `.env`, `.env.local`, and `systems/Parasara/tests/snapshots/generated_*.json`. It does not cover `.env.*` generally, private-key/certificate files, credential-named files, `tests/reports/`, root temporary snapshots, pilot/review datasets, or Audit report safety. There is no tracked `.dockerignore`, pre-commit configuration, or repository-native secret-scanner configuration.

The report directory is intentionally tracked and is not itself unsafe, but it has no automated rule preventing copied secrets, personal values, private paths, or raw provider payloads. Existing ignore rules also cannot protect files already tracked.

## 9. Public/Private Documentation Boundary

The Prompt-01 audit reports are suitable as internal engineering evidence only after owner confirmation that detailed architecture, file paths, rule-table references, and unresolved security findings may be public. The scan found no embedded credential value, personal record, raw provider payload, raw stack trace, email value, or absolute home-directory path in Reports 1–24.

Documentation contains configuration examples and licensing/provenance notes, but the matched configuration entries are placeholders/examples. Proprietary status for Parāśara rule tables, SME packages, and external reference material is not documented. Audit-25 cannot decide confidentiality or publication policy; owners must explicitly classify those materials before making the repository or generated reports public.

## 10. Licensing and Provenance Observations

| Finding ID | File | Location | Category | Secret/Data Type | Classification | Tracked/Generated | Exposure Surface | Urgency | Recommended Owner Action | Prompt-01 Impact | Priority |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L01 | `systems/Parasara/Documentation/operations/licensing-audit.md`; `evidence/licenses.json` | scope/limitations | LICENSING_OR_PROVENANCE | point-in-time partial dependency inventory | PROVENANCE_UNCLEAR | tracked/evidence | release compliance | HIGH_BEFORE_PUBLICATION_OR_RELEASE | run an approved complete release inventory and designated compliance review | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |
| L02 | `requirements-dev.txt`; `systems/Parasara/requirements.txt`; `setup.py` | dependency declarations | LICENSING_OR_PROVENANCE | unpinned/incomplete dependency source and environment mismatch | PROVENANCE_UNCLEAR | tracked/configuration | build/release | MEDIUM_PLANNED_REMEDIATION | establish locked dependency sources and reproducible license evidence | DOES_NOT_BLOCK_PROMPT_01 | P2 |
| L03 | `systems/Parasara/rules/parashara/v1/yogas.yaml` and rule/reference tables | metadata fields | LICENSING_OR_PROVENANCE | classical-source attribution and SME approval status | CLASSICAL_SOURCE_REVIEW_NEEDED | tracked/rules | repository/release | HIGH_BEFORE_PUBLICATION_OR_RELEASE | record source, edition/translation, derivation, ownership, and review decision | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |
| L04 | `external_refs/`; ephemeris/data, generated assets, fixtures, documentation/media | repository-local materials | LICENSING_OR_PROVENANCE | asset/code/data provenance outside current inventory | PROVENANCE_UNCLEAR | tracked/mixed | repository/distribution | HIGH_BEFORE_PUBLICATION_OR_RELEASE | designated owner must inventory licenses, notices, attribution, and redistribution obligations | DOES_NOT_BLOCK_PROMPT_01_BUT_URGENT | P1 |

No obvious AGPL marker or copied third-party predicate header was found in the reviewed Prompt-01 path. That is not a legal conclusion. Licensing/provenance concern count is 4.

## 11. Prior Audit-Report Exposure Assessment

All 24 prior reports were checked for absolute Windows user paths, POSIX home paths, private-key markers, provider-token shapes, raw stack traces, raw embedded `surya_chart` objects, and email-shaped values. No report matched those exposure categories. Reports discuss symbols and risk locations but do not reproduce the underlying sensitive values.

Prior audit reports with exposure concerns: 0. Repository-relative implementation detail may still be confidential under an owner policy that has not yet been defined; this is an owner classification question, not evidence of an unsafe report.

## 12. Consolidated Unrelated Findings

| Finding ID | Originating Audit | Description | Affected Area | Why Outside Prompt-01 | Future Owner/Stage | Urgency | Prompt-01 Dependency | Scope Classification | Priority |
|---|---|---|---|---|---|---|---|---|---|
| U01 | 15, 17–19, 24 | universal immutable `RuleMatch` and cross-rule evidence/trace hierarchy | rule runtime/Yoga | PredicateResult does not own universal rule results | Prompt-02 RuleMatch | LOW_BACKLOG | No | OUT_OF_SCOPE_FUTURE_STAGE | P3 |
| U02 | 04, 16, 18–21, 24 | shared inference/scoring/confidence engine | domain inference | Prompt-01 must preserve Career behavior, not centralize inference | shared inference stage | LOW_BACKLOG | No | OUT_OF_SCOPE_FUTURE_STAGE | P3 |
| U03 | 05, 16–20, 24 | typed DomainPrediction and dedicated OutputAssembler | domain/public output | full public model redesign exceeds predicate-result contract | output/API schema stage | LOW_BACKLOG | No | OUT_OF_SCOPE_FUTURE_STAGE | P3 |
| U04 | 08–10, 16, 24 | stable versioned AstroState query/capability API | state/enrichments | only the minimum compatible predicate boundary is required now | enrichment architecture | MEDIUM_PLANNED_REMEDIATION | No | OUT_OF_SCOPE_FUTURE_STAGE | P2 |
| U05 | 07, 12–14, 24 | formal DSL grammar, AST, macros, dependency graph, optimizer | rules/compiler | Prompt-01 only bridges active condition forms | DSL/compiler stage | LOW_BACKLOG | No | OUT_OF_SCOPE_FUTURE_STAGE | P3 |
| U06 | 08–10, 15 | broad Yoga preparation/enrichment and run-identity redesign | Yoga/enrichments | only compatibility migration is required | Yoga architecture | MEDIUM_PLANNED_REMEDIATION | No | OUT_OF_SCOPE_FUTURE_STAGE | P2 |
| U07 | 21, 22, 24 | explicit evaluation clock for Dasha/time consumers | timing/Dasha | current six predicates do not use the wall-clock fallback | timing context stage | MEDIUM_PLANNED_REMEDIATION | No | OUT_OF_SCOPE_FUTURE_STAGE | P2 |
| U08 | 22, 23 | broader lint, type, coverage, matrix, and release enforcement | CI/DevOps | beyond the minimum Prompt-01 acceptance gate | CI/DevOps | MEDIUM_PLANNED_REMEDIATION | No | OUT_OF_SCOPE_FUTURE_STAGE | P2 |
| U09 | 10, 11, 21, 23 | concurrency, memory observability, timeout, and scalability policy | performance/cache | no distributed/production performance contract is required now | performance/scalability | LOW_BACKLOG | No | OUT_OF_SCOPE_FUTURE_STAGE | P3 |
| U10 | 20, 23, 25 | public raw-input/error filtering, personal-data publication, artifact retention | security/privacy | separate release boundary from PredicateResult implementation | security/privacy hardening | HIGH_BEFORE_PUBLICATION_OR_RELEASE | No | UNRELATED_BUT_URGENT | P1 |
| U11 | 20 | generated frontend response types | frontend/API | frontend client generation is a later schema consumer | output/API schema | MEDIUM_PLANNED_REMEDIATION | No | OUT_OF_SCOPE_FUTURE_STAGE | P2 |
| U12 | 14, 24, 25 | full rule governance, provenance, SME promotion, and release licensing | rules/compliance | contract can preserve metadata without deciding publication rights | licensing/provenance review | HIGH_BEFORE_PUBLICATION_OR_RELEASE | No | UNRELATED_BUT_URGENT | P1 |
| U13 | 13, 23, 24 | repository-wide stale links/status/command-evidence governance | documentation | only Prompt-01 completion docs are required now | documentation governance | MEDIUM_PLANNED_REMEDIATION | No | OUT_OF_SCOPE_FUTURE_STAGE | P2 |
| U14 | 16, 22 | additional domains and universal integration suites | domains | Career is the only direct compatibility surface | later domain stages | LOW_BACKLOG | No | OUT_OF_SCOPE_FUTURE_STAGE | P3 |
| U15 | 11, 21 | persistent/distributed cache and cross-process equality | cache/platform | current cache is process-local and must merely be made safe/bounded | performance/cache stage | LOW_BACKLOG | No | OUT_OF_SCOPE_FUTURE_STAGE | P3 |

Consolidated unrelated findings: 15. Future-stage findings: 13. The two urgent groups remain independent release/compliance gates and must not become typed-contract implementation requirements.

## 13. Prompt-01 Scope Protection

| Finding | Required for Typed Predicate Contract | Compatibility Dependency | Security/Privacy/License Urgency | Correct Scope | Blocks Prompt-01 | Rationale | Priority |
|---|---|---|---|---|---|---|---|
| C01 result model, registry, and legacy return bridge | Yes | Yes | No | IN_SCOPE_PROMPT_01 | Yes | establishes one typed immutable result without breaking callers | P0 |
| C02 parameter validation and capability policy | Yes | Yes | No | IN_SCOPE_PROMPT_01 | Yes | deterministic evaluation requires normalized validated inputs and explicit prerequisites | P0 |
| C03 purity, immutable state boundary, and safe cache key/invalidation | Yes | Yes | No | IN_SCOPE_PROMPT_01 | Yes | current mutable state and identity cache can return stale results | P0 |
| C04 condition evaluator and active-format bridge | Yes | Yes | No | IN_SCOPE_PROMPT_01 | Yes | recursive conditions must preserve typed semantics across live formats | P0 |
| C05 Yoga caller migration | Yes | Yes | No | TEMPORARY_COMPATIBILITY | Yes | Yoga directly consumes legacy helpers and custom trace dictionaries | P0 |
| C06 Career/domain behavior preservation | No | Yes | No | TEMPORARY_COMPATIBILITY | Yes | direct redesign is excluded, but matching/score/confidence/snapshot behavior must not regress | P0 |
| C07 bounded errors, evidence, traces, and serialization | Yes | Yes | Yes for raw-error boundary | IN_SCOPE_PROMPT_01 | Yes | typed fields need safe deterministic ownership; public OutputAssembler remains later | P0 |
| C08 determinism tests, CI gate, decisions, and completion docs | Yes | Yes | No | IN_SCOPE_PROMPT_01 | Yes | the contract is not complete without executable acceptance evidence and locked decisions | P0 |
| Public raw chart/error and tracked personal data | No | No | Yes | UNRELATED_BUT_URGENT | No | release/privacy owners must fix independently before publication | P1 |
| Licensing/provenance completion | No | No | Yes | UNRELATED_BUT_URGENT | No | compliance approval is a release gate, not PredicateResult design | P1 |
| RuleMatch, inference, output assembler, full DSL, broad AstroState redesign | No | No | No | OUT_OF_SCOPE_FUTURE_STAGE | No | belongs to explicitly later architecture stages | P3 |
| CI/performance/documentation governance beyond Prompt-01 acceptance | No | No | No | UNRELATED_NONBLOCKING | No | quality work should retain its owning stage | P2 |

Prompt-01 blocker count: 8 consolidated groups. Nonblocking finding count: 41 exposure/unrelated report findings. Twelve nonblocking exposure/provenance findings remain `UNRELATED_BUT_URGENT` after duplicate public/artifact/provenance surfaces are consolidated; urgency does not convert them into Prompt-01 blockers.

## 14. Future-Stage Mapping

| Future stage | Consolidated findings | Required Prompt-01 boundary |
|---|---|---|
| Prompt-02 RuleMatch | U01 | preserve a bridge; do not implement universal RuleMatch |
| Shared inference/domain stages | U02, U14 | preserve Career behavior only |
| Output/API schema | U03, U11 | define only the minimum temporary PredicateResult filtering boundary |
| Enrichment/Yoga architecture | U04, U06 | require explicit capabilities without broad state redesign |
| DSL/compiler | U05 | support active formats; defer grammar/AST/macros/optimizer |
| Timing context | U07 | do not pull Dasha clock redesign into the six predicates |
| CI/DevOps | U08 | add only the Prompt-01 acceptance gate during implementation |
| Performance/scalability | U09, U15 | make current cache safe; defer distributed policy |
| Security/privacy hardening | U10 | independent before-publication gate |
| Licensing/provenance review | U12 | independent release/compliance gate |
| Documentation governance | U13 | update Prompt-01 docs; defer repository-wide governance |

## 15. Urgency and Blocking Assessment

There are no `CRITICAL_IMMEDIATE` or P0 credential/public-exposure findings. High-before-publication work includes named exact-birth datasets, credential-shaped scaffold data, raw public chart/error responses, tracked/uploaded report artifacts, and incomplete licensing/provenance evidence. Owners should treat public release as gated until those items are reviewed and remediated.

Prompt-01 implementation remains blocked by the eight C01–C08 groups from prior audits, not by U01–U15 or the independent release/compliance work. Historical secret exposure, data-subject consent/public-source status, repository confidentiality policy, and production publication status remain unknown because they require owner evidence or separately authorized history/operations review.

## 16. Existing CI and Safety Enforcement

| Check | Tool/Workflow | File | Enforcement | Scope | Blocking | Coverage Gap | Priority |
|---|---|---|---|---|---|---|---|
| common local secret/output exclusion | Git ignore | `.gitignore` | automatic for untracked matches | `.env`, `.env.local`, logs, generated Parāśara snapshots | No | no broad `.env.*`, key/cert, reports, temporary snapshots, or already-tracked protection | P1 |
| snapshot drift validation | snapshot compare workflow/tool | `.github/workflows/parasara-snapshot-compare.yml`; `ci_snapshot_check.py` | automated CI | selected golden snapshot integrity | Yes for that workflow | validates drift, not personal data, redaction, or public-schema safety | P2 |
| secret scanning | none found | repository/CI | missing | tracked content/history | No | no blocking scanner or baseline | P1 |
| dependency/license scanning | point-in-time manual evidence | `Documentation/operations/licensing-audit.md`; `evidence/licenses.json` | manual/advisory | one development environment | No | incomplete dependency/assets coverage; not reproducible CI | P1 |
| personal/chart-data detection | anonymizer exists but is manual | `systems/Parasara/tools/anonymize_pilot.py` | manual/nonblocking | one pilot dataset shape | No | inputs remain tracked; no consent/provenance or PII gate | P1 |
| generated-artifact exclusion | partial ignore plus CI upload | `.gitignore`; `.github/workflows/ci.yaml` | partial and contradictory | selected snapshots vs complete report upload | No | no allowlist, redaction, retention, or tracked-artifact gate | P1 |
| public-schema filtering | none at API boundary | runner and Next route | missing | HTTP success/error payloads | No | pass-through raw chart and error detail | P1 |
| audit-report safety check | none found | `Reports/` | missing | generated audit documentation | No | no secret/PII/path/payload guard | P2 |

Existing automated safety checks: 2 (partial ignore protection and snapshot-integrity validation). Missing safety checks: 6 (secret scan, complete license scan, personal-data gate, complete artifact protection, public-schema filtering, and audit-report safety).

## 17. Risks and Priorities

Priority accounting uses unique consolidated findings: C01–C08, S01–S07, D01–D10, G01–G05, L01–L04, and U01–U15. Public-output and enforcement tables are cross-references and are not double-counted.

| Priority | Count | Meaning in this audit |
|---|---:|---|
| P0 | 8 | Prompt-01 contract/migration/acceptance blocker groups |
| P1 | 16 | high-before-publication exposure/provenance findings and urgent unrelated groups |
| P2 | 12 | planned hardening, compatibility, and future-stage quality findings |
| P3 | 13 | placeholders, false positives, and later architecture/informational findings |

Summary counts:

| Measure | Count |
|---|---:|
| Secret/credential candidates | 7 |
| Probable or confirmed secret findings | 0 |
| Placeholder/example findings | 4 |
| Test-fixture credential findings | 1 |
| False-positive credential findings | 2 |
| Personal/chart-data findings | 6 |
| Raw-input exposure paths | 4 |
| Error/stack-trace exposure paths | 5 |
| Internal-path/metadata exposures | 3 |
| Public-schema exposure risks | 4 |
| Generated-artifact exposure risks | 5 |
| Licensing/provenance concerns | 4 |
| Prior audit reports with exposure concerns | 0 |
| Consolidated unrelated findings | 15 |
| Future-stage findings | 13 |
| Unrelated-but-urgent findings | 12 |
| Prompt-01 blockers | 8 |
| Nonblocking findings | 41 |
| Existing automated safety checks | 2 |
| Missing safety checks | 6 |
| P0 findings | 8 |
| P1 findings | 16 |
| P2 findings | 12 |
| P3 findings | 13 |

## 18. Unresolved Owner Decisions

1. Are the 12 historical-pilot and 20 SME-review named records approved for public distribution, with documented source, consent/public-figure basis, retention, and allowed uses?
2. Are scaffold account records guaranteed synthetic, and may credential-shaped/email-shaped test records be distributed or packaged?
3. Is the raw generated chart an intentional authenticated public product field, or must the API use an allowlist that excludes it?
4. What public error code, internal diagnostic, artifact redaction, access, and retention policies apply to runner/API/test output?
5. Which fixtures, golden snapshots, audit reports, rule tables, SME packages, and external references are public, private, or release-excluded?
6. Who owns the complete dependency/code/data/asset provenance review and formal release approval?
7. Should a separately authorized history scan verify whether any secret or private data was previously committed? This audit did not inspect history.

## 19. Audit-25 Conclusion

Audit-25 completed the required safe inventory and final scope reconciliation. No probable or confirmed live secret was identified, but public/privacy, artifact, and provenance release risks require owner action. The eight Prompt-01 blockers remain the typed contract and its compatibility/acceptance boundary; the 15 unrelated groups remain nonblocking and mapped to their proper owners or later stages.

Urgent public exposure found: YES

Prompt-01 scope remains bounded: YES

Unrelated findings incorrectly blocking Prompt-01: NO

Files modified during Audit-25:

- `systems/Parasara/Documentation/Engine/Prompt-01/Reports/Audit-25-Public-Private-Unrelated-Findings.md`
