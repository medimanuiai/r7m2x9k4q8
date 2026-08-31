# Prompt-05 Provenance Architecture Decision

Status: APPROVED — R4 IMPLEMENTATION AUTHORIZED

Decision date: 2026-08-24

Scope: Prompt-05 provenance only

Branch and reviewed HEAD: `main` at
`c719a1bf686e1e37eb8542f9323fc279b670250e`

## 1. Decision summary

Prompt-05 will use an explicit in-process authority boundary rather than trying
to make ordinary Python values cryptographically authentic.

The authoritative Career execution product will be one private,
evaluator/interpreter-owned `CareerInferenceEvaluation` value. It will bind,
during the same execution:

- the complete evaluator-produced `RuleMatch` ledger;
- the approved `InferenceConfig` identity and canonical fingerprint;
- the Prompt-03 `InferenceResult` produced from that ledger and configuration;
- contribution-to-RuleMatch lineage;
- exactly one Career compatibility projection produced by `InferenceEngine`
  from that same result and configuration.

The projection is **stored once during authoritative inference execution**. It
is not derived later from a newly supplied configuration. No supported API may
accept a second configuration after aggregation.

Prompt-05 evaluated `DomainPrediction`, `DomainIndicator`, and `YogaDiagnostic`
objects will be created only inside their approved execution pipelines. Their
public constructors, `dataclasses.replace` reconstruction paths, and
authoritative logical deserializers will be unavailable. Public batches,
evaluation records, serialized dictionaries, digests, and caller-replaced
dataclasses are data values; none establishes authority.

`RuleMatch` remains the sole authority for Yoga rule truth, matched state,
status, rule evidence, and rule trace. Legacy Yoga display evidence may remain
as explicitly presentation-only metadata produced during the same evaluation,
but it can neither override `RuleMatch` nor be supplied later to construct an
authoritative diagnostic.

This decision requires no change to the approved Prompt-02, Prompt-03, or
Prompt-04 contracts and no public compatibility change.

## 2. Context and verified failure

R1 through R3 repeatedly added reconciliation fields, digests, tokens, and
retained wrappers. Final R3 showed that these mechanisms still permitted two
coordinated attacks through supported APIs:

1. A caller supplied another internally valid `InferenceConfig`, obtained a
   projection for an unchanged `InferenceResult`, and reconstructed a Career
   prediction with changed formula, baseline, contribution total, and
   precision. A replaced Yoga evaluation record similarly changed public Yoga
   compatibility evidence while retaining the original `RuleMatch`.
2. A caller replaced an unmatched candidate `RuleMatch`, its evidence, the
   `CareerEvaluationBatch`, and a contribution-free indicator. The domain
   validator accepted the replaced batch as the parent authority.

The common defect is not missing field comparison. It is that authority is
currently inferred from a value supplied by the same caller whose claims are
being checked.

The governing ownership remains:

- Prompt-02 `RuleEngine` owns construction of universal `RuleMatch` and
  `RuleMatch` owns rule truth, rule evidence, and rule trace.
- Prompt-03 `InferenceEngine` owns contributions, aggregation, normalization,
  confidence, agreement, conflicts, and the immutable `InferenceResult`.
- Prompt-04 `AstroStateSnapshot` owns facts and factual capability state.
- Prompt-05 maps already-authoritative values into typed domain presentation
  and one-way public compatibility output.

## 3. Threat model

### 3.1 In scope

The engine must reject invalid authoritative domain construction through:

- public constructors;
- public factories;
- supported deserialization or reconstruction APIs;
- `dataclasses.replace` on publicly exposed dataclasses;
- coordinated replacement of multiple related public fields;
- alternate, internally consistent configurations supplied through public
  APIs;
- caller-created batches or evaluation records supplied through public APIs;
- replacement of logical content together with its unkeyed digest;
- construction of mutually consistent presentation, source, and lineage
  wrappers by the same caller.

An operation is in scope when repository documentation, `__all__`, a public
method/function name, or a supported serializer/deserializer presents it as an
engine construction or reconstruction path.

### 3.2 Out of scope

Prompt-05 is not required to resist:

- `object.__new__` bypasses;
- `object.__setattr__` attacks on frozen objects;
- monkeypatching;
- importing and invoking explicitly private module internals;
- process-memory manipulation;
- replacing Python modules at runtime;
- cryptographic attackers executing arbitrary code inside the engine process.

“Authoritative” means created and bound at the approved
engine/evaluator/interpreter boundary and inaccessible through supported caller
construction. It does not mean cryptographically unforgeable against arbitrary
code executing inside the Python process.

### 3.3 Consequences of the threat model

- A leading underscore alone is sufficient only when the value is also absent
  from public exports, documentation, supported callbacks, and public return
  values used for later authoritative construction.
- A private constructor token is an implementation guard, not provenance, if a
  supported public helper will mint the guarded value from arbitrary caller
  inputs.
- An unkeyed SHA-256 digest proves deterministic logical equality or detects an
  accidental mismatch. It does not prove origin when a caller can replace both
  data and digest.
- Frozen dataclasses prevent ordinary mutation. They do not establish the
  origin of a newly constructed or replaced value.
- No HMAC, signature, process registry, random nonce, or nondeterministic
  identity token is required for this in-process boundary.

## 4. Career configuration and projection ownership

### 4.1 Chosen design

The Career interpreter owns selection of the one approved configuration. Its
canonical path accepts an `AstroStateSnapshot` and no caller-supplied
`InferenceConfig`, `CareerEvaluationBatch`, `InferenceResult`, or compatibility
projection.

The internal flow is:

```text
AstroStateSnapshot
  -> private Career preparation/evaluation
  -> private complete RuleMatch ledger
  -> interpreter selects approved InferenceConfig
  -> InferenceEngine.aggregate(..., approved_config) exactly once
  -> InferenceEngine creates one compatibility projection with that same config
  -> private CareerInferenceEvaluation
  -> private DomainPrediction factory
  -> immutable DomainPrediction
  -> OutputAssembler / one-way public compatibility projection
```

The private logical contract is:

```text
CareerInferenceEvaluation
  evaluation_schema_version
  evaluation_lineage_id
  rule_match_ledger
  rule_match_ledger_digest
  approved_config_id
  approved_config_fingerprint
  inference_result
  inference_result_digest
  compatibility_projection
```

The exact class name may retain a leading underscore. Its semantics may not be
split among multiple caller-supplied wrappers.

### 4.2 Configuration binding

The approved config binding contains:

- the config schema version;
- `inference_version`;
- the canonical config identifier;
- SHA-256 of the complete canonical `InferenceConfig` logical data;
- the compatibility formula/profile identity;
- normalization precision and rounding policy identity;
- baseline rule/category identity;
- the configuration identity already propagated into inference traces.

The private evaluation constructor receives the exact config object used by
`InferenceEngine.aggregate`, immediately records its canonical fingerprint,
and stores the engine-produced projection before returning. The projection
must reconcile to the stored result digest and config fingerprint.

Version equality alone never establishes configuration equality.

### 4.3 Stored projection decision

The compatibility projection is stored once during the authoritative
evaluation. Later derivation with any configuration is prohibited.

The current public operation:

```python
InferenceEngine.compatibility_projection(result, config)
```

must cease to be a supported public API. The engine may retain an explicitly
private helper used only while constructing `CareerInferenceEvaluation`.

There will be no supported equivalent of:

```python
result.compatibility_projection(attacker_config)
```

The stored projection remains the sole source for compatibility-only formula,
base score, total contribution, public trace identity, and precision.
`OutputAssembler` may round/format those stored values as required by the
locked public schema, but may not aggregate or select another config.

### 4.4 Prompt-03 compatibility

Prompt-03's public `InferenceEngine.aggregate(..., config) -> InferenceResult`
and `InferenceResult` logical contract remain unchanged. Generic callers may
still create and test alternate `InferenceConfig` values and obtain ordinary
Prompt-03 results.

Prompt-05 does not treat a bare caller-supplied or deserialized
`InferenceResult` as sufficient authority to construct an evaluated Career
domain result. Authority is the private Prompt-05 execution value that contains
the Prompt-03 result and the same-run config and ledger binding.

This avoids changing the protected Prompt-03 model or manifest while meeting
Prompt-03's requirement that configuration identity propagate through the
authoritative execution.

## 5. Evaluation lineage ownership

### 5.1 Ledger owner and contents

The Career evaluator owns one private `CareerEvaluationLedger`. It is created
inside the canonical snapshot-to-Career execution and is never accepted as an
argument from a public caller.

The ledger includes every relevant `RuleMatch` produced by the generic
`RuleEngine` during that evaluation:

- matched contributing rules;
- matched non-contributing rules, if such diagnostics are approved;
- unmatched diagnostic candidates;
- skipped, excluded, missing-capability, invalid, or error outcomes that are
  permitted to produce typed diagnostics;
- the explicit Career compatibility baseline match supplied to Prompt-03.

Ledger ordering is canonical and preserves the approved source-order metadata
where public compatibility requires it.

### 5.2 Membership

Each ledger member has a canonical membership record containing at least:

- rule ID and rule version;
- rule status and matched value;
- rule trace ID;
- canonical `RuleMatch` logical digest;
- evaluator source position;
- evaluation lineage ID.

The ledger stores the exact immutable `RuleMatch` values produced during the
run. A `DomainIndicator` is created only after resolving its membership record
from this ledger. Copying the same fields into another `RuleMatch` does not add
that object to the ledger.

For score-bearing indicators:

- the referenced RuleMatch must be a ledger member;
- the referenced contribution must belong to the bound `InferenceResult`;
- contribution rule ID/version/trace and evidence references must reconcile to
  that ledger member.

For contribution-free indicators:

- the referenced RuleMatch must still be a ledger member;
- the match's evidence and trace remain Prompt-02-owned;
- no `CareerEvaluationBatch`, indicator, or embedded RuleMatch supplied by a
  caller can establish membership.

### 5.3 Construction and replacement policy

`CareerEvaluationLedger` and `CareerInferenceEvaluation` are private
implementation types with non-public construction. They are not exported,
serialized as authoritative objects, returned to callers, or accepted by a
public factory. `dataclasses.replace` is therefore not a supported provenance
path. If implemented as dataclasses, authoritative construction must use
`init=False` or another private constructor boundary so ordinary
`dataclasses.replace` cannot mint a valid authority value.

`DomainPrediction` and `DomainIndicator` must likewise reject ordinary direct
construction and `dataclasses.replace`. Their evaluated forms are emitted only
by the internal factory receiving the private evaluation value. Standalone
replaced presentation values may exist as ordinary Python data, but no
supported assembler or factory accepts them as authoritative input.

### 5.4 Disposition of `CareerEvaluationBatch`

`CareerEvaluationBatch` remains an immutable, deterministic diagnostic and
compatibility data contract because Prompt-04 protects its logical behavior.
It becomes explicitly **untrusted for Prompt-05 authority**.

- Its canonical serializers and hashes may remain.
- Callers may deserialize, inspect, copy, or replace it as ordinary data.
- No evaluated `DomainPrediction` factory may accept it.
- Public `build_career_prediction(batch, result)` and
  `project_career_compatibility(batch, inference_result)` authority paths must
  be removed or made private.
- The canonical public Career entrypoints accept only `AstroState` or
  `AstroStateSnapshot` and run the evaluator-owned pipeline internally.

Tests construct legitimate evaluated predictions through the canonical
snapshot interpreter. Tests that need a batch for Prompt-04 compatibility may
continue to create one, but cannot use it to confer Prompt-05 authority.

## 6. Yoga authority

### 6.1 Locked rule

`RuleMatch` is the sole authority for Yoga rule truth, matched state, status,
evidence, and rule trace.

Consequently:

- `YogaDiagnostic.matched` is exactly `RuleMatch.matched`;
- `YogaDiagnostic.status` is exactly `RuleMatch.status`;
- Yoga rule evidence is exactly `RuleMatch.evidence`;
- Yoga rule trace and identity are exactly the RuleMatch trace and identity;
- a disagreeing `condition_result.matched` causes rejection of authoritative
  diagnostic construction;
- no invalid-definition compatibility branch may promote condition truth over
  RuleMatch truth.

The existing `compatibility_match` override in the Yoga diagnostic factory and
model must be removed.

### 6.2 Presentation-only metadata

The locked public Yoga row also contains a name, source order, houses, planets,
and legacy evidence formatting. Values that are not RuleMatch-owned may be
retained in a typed `YogaPresentationMetadata` value only when:

- they are created during the same private Yoga evaluation run;
- their names make clear that they are presentation metadata, not rule
  evidence or truth;
- they cannot alter Yoga ID, matched, status, rule evidence, or rule trace;
- source order reconciles to evaluator-owned rule-source order;
- their public compatibility projection remains exactly the approved row.

Derivation is preferred. Where exact public compatibility requires stored
legacy formatting, it is stored once in the private evaluation run and copied
into the internally constructed diagnostic. It is never accepted later from a
public evaluation record.

### 6.3 Records and batches

Public `YogaEvaluationRecord` and `YogaEvaluationBatch` serializers may remain
for the protected typed-batch contract, but those objects are untrusted for
Prompt-05 authority after being returned to a caller.

- `build_yoga_diagnostics(batch)` must cease to be a supported authoritative
  construction API.
- The canonical snapshot pipeline builds diagnostics before its private Yoga
  run leaves the evaluator boundary.
- Batch deserialization may recreate diagnostic data, but not an authoritative
  `YogaDiagnostic` or public-output assembly input.
- `YogaDiagnostic` direct construction and `dataclasses.replace` are rejected.
- `yoga_diagnostic_from_logical_data/json` must be removed from the supported
  authoritative API.

The legacy public `evaluate_yoga_rules(AstroState)` wrapper may remain only as
an end-to-end wrapper that runs the canonical evaluator. It must not accept a
caller batch or record.

## 7. Serialization and reconstruction

### 7.1 Public-output serialization

`OutputAssembler` and the named Career/Yoga compatibility projections produce
fresh public presentation DTOs. These dictionaries and JSON bytes are one-way
outputs.

They:

- preserve the exact approved public schema and bytes;
- carry no authority for later domain construction;
- cannot be supplied to a supported API to recreate an evaluated
  `DomainPrediction`, `DomainIndicator`, or `YogaDiagnostic`;
- do not become inference, rule, or factual inputs.

### 7.2 Internal trusted-domain reconstruction

Prompt-05 has no current persistence or cross-process replay requirement for
authoritative domain objects. R4 therefore will not support dictionary/JSON
reconstruction of evaluated authoritative objects.

Within one process, the canonical pipeline passes private typed run values
directly from evaluator to inference to domain factory. It does not serialize
and deserialize authority between those steps.

### 7.3 Untrusted external deserialization

Existing logical deserializers may remain only for non-authoritative DTOs whose
documentation and type names cannot be confused with engine-produced domain
authority. In particular:

- Prompt-02 `RuleMatch` and Prompt-03 `InferenceResult` deserialization may
  recreate valid contract values under their predecessor contracts, but the
  values do not gain membership in a Prompt-05 private execution ledger.
- Career/Yoga batch deserialization recreates diagnostic data only.
- `domain_prediction_from_logical_data/json` and
  `yoga_diagnostic_from_logical_data/json` must not reconstruct authoritative
  evaluated values and should be removed from Prompt-05 public exports.
- If a future requirement needs authoritative persistence, it requires a
  separate approved design that re-executes or validates config identity,
  evaluator lineage, and all canonical inputs. R4 must not anticipate it.

Logical SHA-256 digests remain required for deterministic content identity and
mutation detection. They are never evidence of provenance by themselves.

### 7.4 Required logical attack tests

R4 acceptance must prove that supported APIs reject or make impossible:

- a public Career dictionary reintroduced as a `DomainPrediction`;
- an unchanged `InferenceResult` combined with a different valid config or
  config fingerprint;
- a replaced `CareerEvaluationBatch` used as parent authority;
- a serialized contribution-free indicator plus a forged parent match;
- a replaced Yoga record used to create a diagnostic;
- coordinated replacement of logical fields and logical digest;
- a deserialized RuleMatch/InferenceResult used without private ledger/config
  membership;
- any public factory that mints a newly named authoritative wrapper from
  caller-provided matches, batches, records, or config values.

## 8. Construction API policy

“Public constructor” below means a supported operation that can create an
authoritative value, not merely Python's ability to import a class.

| Type | Owner | Public constructor? | Public replacement supported? | Authoritative inputs | Deserialization policy |
| --- | --- | ---: | ---: | --- | --- |
| `RuleMatch` | Prompt-02 generic `RuleEngine` | No; RuleEngine factory only | Replacement yields an untrusted value | Resolved rule plus typed condition result | Predecessor logical deserialization remains data-only for Prompt-05 ledger membership |
| `CareerEvaluationLedger` / `CareerInferenceEvaluation` | Private Career evaluator/interpreter boundary | No | No | Same-run RuleMatches, approved config, Prompt-03 result, stored projection | None |
| `CareerEvaluationBatch` | Career evaluator diagnostic contract | Yes, as non-authoritative data | Yes, as non-authoritative data | Evaluated facts and RuleMatches for diagnostics | Allowed as diagnostic data; never establishes authority |
| `InferenceConfig` | Prompt-03 config loader; Career interpreter selects approved instance | Yes, as generic policy input | Yes, but replacement is not Career approval | Versioned canonical config source | Allowed under Prompt-03; caller config cannot enter authoritative Career path |
| `InferenceResult` | Prompt-03 `InferenceEngine.aggregate` | No supported direct authoritative constructor | Replacement is untrusted for Prompt-05 | Ledger RuleMatches, completeness, timing, exact approved config | Prompt-03 deserialization remains data-only for Prompt-05 authority |
| Compatibility projection | Prompt-03 engine during private Career execution | No | No | Bound result and exact same-run config | None; public representation is one-way DTO only |
| `DomainIndicator` | Private Prompt-05 domain factory | No | No | Resolved private-ledger member and optional bound contribution | No authoritative deserialization |
| Evaluated `DomainPrediction` | Private Prompt-05 domain factory | No | No | Private Career execution value | No authoritative deserialization |
| Non-evaluated `DomainPrediction` rejection/status outcome | Prompt-05 status factory | Restricted public factory may remain | Replacement must reject invalid combinations | Typed issue/status only; no inferred values | Strict status DTO parsing may remain if it cannot create evaluated authority |
| `YogaEvaluationRecord` / batch | Yoga evaluator diagnostic contract | Yes, as non-authoritative data | Yes, as non-authoritative data | RuleMatch and evaluation diagnostics | Allowed as diagnostic data; cannot construct Yoga authority |
| `YogaDiagnostic` | Private Yoga evaluator/domain boundary | No | No | Same-run RuleMatch plus bounded presentation metadata | No authoritative deserialization |
| Unavailable `TransitSummary` | Prompt-05 transit status factory | Yes, through canonical unavailable factory | Replacement revalidates and cannot become active | Typed unavailable issue only | Strict unavailable reconstruction may remain |
| Available/partial `TransitSummary` | Future real transit producer boundary | No current constructor | No | Actual future producer output | Unsupported while no producer exists |

### 8.1 Meaning of sealed

This decision does not use “sealed” as a synonym for a token check. A sealed
authoritative type must satisfy all of these:

- no public constructor creates an authoritative instance;
- no public factory accepts caller-controlled authoritative fields;
- `dataclasses.replace` cannot create another authoritative instance;
- no public deserializer recreates it from a dictionary or JSON;
- it is produced only inside the named owner boundary;
- consumers that require authority accept only values flowing directly from
  that boundary, not look-alike wrappers.

## 9. Preserved R3 and predecessor decisions

R4 must preserve without redesign:

- transit remains honestly unavailable until a real integrated producer exists;
- `InferenceEngine` remains the sole aggregation owner;
- `OutputAssembler` remains serialization-only;
- Yoga source ordering remains evaluator-owned and exact;
- Prompt-03 neutral insufficient-evidence semantics remain exact;
- the executable `MISSING_INFERENCE_RESULT` path remains distinct;
- public Career output remains exact;
- public Yoga output remains exact;
- the approved 4,041-byte snapshot remains exact;
- Prompt-01 through Prompt-04 models, behavior, validators, and manifests remain
  exact;
- all 24 protected files and four personal exports remain unchanged;
- Windows Python 3.11 and 3.14 remain the supported validation lanes.

If protected public Yoga fixtures require `condition_result.matched` to
override a disagreeing RuleMatch, R4 must stop and report a direct conflict
rather than retain the override. Current reviewed fixtures and exact public
validation do not establish such a required disagreement.

## 10. Bounded R4 implementation plan

R4 is not authorized by this document. After explicit user approval, one R4
session may implement only the following plan.

### 10.1 Production files expected to change

Required or likely:

- `systems/Parasara/engine/inference/engine.py`
  - make compatibility projection a private same-run operation;
  - keep aggregation and all total/base selection in the engine.
- `systems/Parasara/engine/inference/models.py`
  - restrict/remove the publicly constructible compatibility projection path;
  - do not change protected Prompt-03 `InferenceResult` logical fields.
- `systems/Parasara/engine/inference/__init__.py`
  - remove Prompt-05 projection construction exports, if any.
- `systems/Parasara/engine/interpreters/career.py`
  - add the private canonical Career execution coordinator;
  - select the approved config internally;
  - bind ledger, config fingerprint, inference result, and stored projection;
  - remove public batch/result/config injection into domain construction.
- `systems/Parasara/engine/interpreters/career_models.py`
  - retain `CareerEvaluationBatch` as diagnostic data;
  - add private run/ledger implementation only if not kept in `career.py`.
- `systems/Parasara/engine/domain/models.py`
  - make evaluated authoritative construction/replacement unavailable;
  - remove authoritative domain/Yoga logical reconstruction;
  - retain deterministic logical projection for output and manifests.
- `systems/Parasara/engine/domain/factories.py`
  - accept private same-run authority only;
  - remove public Career inference and Yoga record authority paths;
  - remove Yoga truth override.
- `systems/Parasara/engine/domain/__init__.py`
  - remove unsupported constructors/deserializers from public exports.
- `systems/Parasara/engine/enrichments/yoga_engine.py`
  - construct diagnostics inside the private evaluator pipeline;
  - keep public batches diagnostic-only;
  - prevent record/batch injection into authoritative construction.
- `systems/Parasara/engine/output_assembler.py`
  - adapt only to the final immutable typed values;
  - perform no aggregation or authority reconstruction.
- `systems/Parasara/tools/generate_snapshot.py`
  - route through the new canonical end-to-end Career/Yoga entrypoints if
    required; retain `OutputAssembler` as sole serializer.

No predecessor factual, predicate, RuleMatch, or `InferenceResult` logical
model file is otherwise in scope.

### 10.2 Public APIs to remove or restrict

- Remove `InferenceEngine.compatibility_projection(result, config)` as a
  supported public operation.
- Remove or privatize public authority use of:
  - `build_career_prediction(batch, result)`;
  - `infer_career(batch, config=..., engine=...)` for the canonical domain path;
  - `project_career_compatibility(batch, inference_result)`;
  - `DomainPredictionFactory.from_inference(...)` for evaluated Career;
  - `build_yoga_diagnostics(batch)` as caller-supplied authority;
  - `YogaDiagnosticFactory.from_evaluation_record(record)` as a public path;
  - `domain_prediction_from_logical_data/json` for evaluated authority;
  - `yoga_diagnostic_from_logical_data/json`.
- Preserve end-to-end compatibility entrypoints accepting `AstroState` or
  `AstroStateSnapshot`.
- Preserve Prompt-02/03 serializers as predecessor data contracts without
  granting Prompt-05 authority.

### 10.3 Tests expected to change or be added

Add:

- `tests/domain/test_remediation_r4.py` containing the exact successful Final
  R3 attacks and their required failures.

Update as narrowly required:

- `tests/domain/test_architecture.py`;
- `tests/domain/test_career_yoga.py`;
- `tests/domain/test_models.py`;
- `tests/domain/test_output_assembler.py`;
- `tests/domain/test_remediation_adversarial.py`;
- `tests/domain/test_remediation_r2.py`;
- `tests/domain/test_remediation_r3.py`;
- `tests/domain/conftest.py`;
- `tests/domain/scenario_manifest.py`;
- affected existing Yoga typed-integration tests if they currently use a batch
  as a diagnostic authority;
- `tools/validate_prompt05.py` only for the legitimately changed Prompt-05
  manifest and R4 test composition.

Do not weaken or delete valid prior attack coverage. Re-express tests through
the supported construction boundary.

### 10.4 Exact attacks that must fail

R4 tests must independently prove failure of:

1. Original inference plus alternate valid config changing formula.
2. Original inference plus alternate baseline category/rule changing base or
   contribution total.
3. Original inference plus alternate precision changing public score rounding.
4. Alternate config plus coordinated compatibility fields and digest.
5. Direct or replaced compatibility projection construction.
6. Replaced Career batch plus forged unmatched RuleMatch and evidence.
7. Contribution-free indicator plus coordinated parent-batch replacement.
8. Score-bearing indicator detached from either ledger or contribution.
9. Replaced Yoga record plus fabricated compatibility evidence.
10. Coordinated Yoga logical reconstruction with that record.
11. `condition_result.matched` disagreeing with RuleMatch.
12. Direct construction or `dataclasses.replace` of evaluated
    `DomainPrediction`, `DomainIndicator`, or `YogaDiagnostic`.
13. Public-output or logical dictionaries reintroduced as authoritative
    objects.
14. A public helper minting an authority wrapper from caller matches/config.

The tests must use supported public operations. Attacks through explicitly
private internals are outside the threat model and must not be used to create
an endless sealing requirement.

### 10.5 Valid paths that must continue

- `AstroStateSnapshot -> canonical Career interpreter -> DomainPrediction`.
- Mutable `AstroState` compatibility wrapper through the same snapshot path.
- Prompt-03 generic aggregation with explicitly supplied configs for generic
  Prompt-03 tests, without granting Prompt-05 authority.
- Career batch creation and serialization as diagnostic data.
- Yoga snapshot evaluation and protected batch serialization.
- Canonical Yoga evaluation to internally created diagnostics.
- Canonical unavailable transit and Dasha results.
- Neutral insufficient inference and missing-inference rejection.
- Output assembly from internally produced typed values.

### 10.6 Compatibility requirements

The following remain byte/value exact:

- public Career dictionaries for all protected fixtures;
- public Yoga rows and source order;
- approved 4,041-byte snapshot with SHA-256
  `da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`;
- Prompt-01/WP17 and Prompt-02 manifest
  `75b65d2cd1420c6261aadbb8159d10fb8c641137ce08d29f2a651952e5cdfaf7`;
- Prompt-03 manifest
  `f57bc28504988ecf5ccfbf82de4bc495d2e69a91dfd476997cda5c89a563786e`;
- Prompt-04 manifest
  `440a459cc60e9575874341e7c6673e714585ae79123957c9c19ccd175cb7930b`.

The Prompt-05 manifest may change only for the bounded authority model and new
tests and must match across Python 3.11 and 3.14.

### 10.7 Documentation status corrections

R4 must preserve R1, R2, R3, and Final Review records as historical evidence.
It may:

- create one truthful `Prompt-05-Remediation-R4.md` report;
- update the Prompt-05 requirements status line;
- update `systems/Parasara/Documentation/Engine/Prompt-05/README.md`;
- update `systems/Parasara/Documentation/prompts/prompt-05/README.md`;
- append, without rewriting historical text, a current R4 addendum to the
  Prompt-05 stopping report;
- update current architecture and implementation-status text;
- update the Prompt-05 report index.

All status text must say R4 is implementation-validated but not accepted until
an independent Final R4 Review passes. It must not claim commit, merge, or
Prompt-06 readiness.

### 10.8 Validation commands

Use the repository's Windows environments and temporary outputs:

```powershell
$env:PYTEST_ADDOPTS='--ignore=jyothishyam_env'
.\jyothishyam_env\prompt01-py311\Scripts\python.exe -m pytest -q tests\domain
.\jyothishyam_env\prompt01-py314\Scripts\python.exe -m pytest -q tests\domain

.\jyothishyam_env\prompt01-py311\Scripts\python.exe -m pytest -q tests\domain\test_remediation_r4.py
.\jyothishyam_env\prompt01-py314\Scripts\python.exe -m pytest -q tests\domain\test_remediation_r4.py

.\jyothishyam_env\prompt01-py311\Scripts\python.exe tools\validate_prompt05.py full
.\jyothishyam_env\prompt01-py314\Scripts\python.exe tools\validate_prompt05.py full

Set-Location frontend
npm run lint
npm run type-check
```

Run `npm run build` in a temporary frontend mirror, then verify the governed
route count. Finish with `git diff --check`, protected-file comparison, all
four personal-export size/hash comparisons, staged-file inspection, Prompt-06
exclusion, and repository TypeScript build-info checks.

Do not run redundant full suites outside the composed validator.

### 10.9 Explicit R4 exclusions

R4 must not:

- change Prompt-01 through Prompt-04 logical contracts or manifests;
- change astrology, rule conditions, weights, inference arithmetic, confidence,
  completeness, or conflict semantics;
- redesign transit, Dasha, Yoga order, insufficient evidence, missing
  inference, OutputAssembler ownership, or frontend behavior;
- add cryptography, HMAC, signatures, process registries, persistence, caching,
  governance, DSL, or external replay infrastructure;
- add Wealth, Marriage, Children, Health, or Safety interpreters;
- modify public JSON or approved snapshots;
- perform unrelated cleanup;
- stage, commit, push, create a PR, merge, or begin Prompt-06.

## 11. R4 acceptance gate

R4 is ready for an independent final review only if:

- authority originates at the named evaluator/interpreter boundary;
- the same-run approved config fingerprint and stored projection are bound to
  the Prompt-03 result;
- no supported later API accepts another compatibility config;
- every indicator resolves to the private evaluator ledger;
- contribution-free indicators cannot use a caller batch as authority;
- Yoga truth/evidence/trace come only from RuleMatch;
- public constructors, replacement, and logical reconstruction cannot mint
  evaluated authority;
- all fourteen attack classes in Section 10.4 fail behaviorally;
- transit and sole aggregation ownership remain intact;
- exact compatibility, dual-Python validation, frontend gates, protected files,
  exports, and worktree integrity pass;
- documentation truthfully records R4 pending independent review.

## 12. Decision consequences

### Benefits

- Authority has one named origin rather than a chain of mutually validating
  caller values.
- Prompt-02 and Prompt-03 ownership remains intact.
- Public compatibility stays one-way and byte exact.
- The threat model has a finite, testable boundary appropriate for Python.
- Future reviews can distinguish supported construction attacks from arbitrary
  in-process code execution.

### Costs

- Some currently exported low-level Career/Yoga construction helpers become
  private or diagnostic-only.
- Tests must use end-to-end authoritative entrypoints for evaluated objects.
- Authoritative Prompt-05 object round-trip from arbitrary JSON is deliberately
  unsupported until an actual persistence requirement exists.

### Rejected alternatives

- **More reconciliation fields or digests:** rejected because coordinated
  caller replacement remains possible.
- **Another public trusted-wrapper factory:** rejected because it merely moves
  caller-controlled authority.
- **Store config only by version:** rejected because the Final R3 alternate
  config used the same version.
- **Late projection with a supplied config:** rejected because it recreates the
  verified attack.
- **HMAC/signatures/random process tokens:** rejected because there is no
  external persistence or hostile-process requirement.
- **Change Prompt-03 `InferenceResult`:** rejected because the private
  Prompt-05 execution binding solves the problem without changing the
  protected predecessor contract.

## 13. Approval and implementation state

This document records the user-approved governing R4 architecture.

- User architectural approval: approved on 2026-08-24.
- R4 implementation: attempted; blocked by the exact inherited Prompt-02/WP17
  Yoga compatibility contract recorded in the R4 remediation report.
- Commit, push, PR, merge: not authorized.
- Prompt-06: not started and not authorized.

Recommended next action:

**STOP AND REPORT THE EXACT PROMPT-02 CONTRACT CONFLICT**
