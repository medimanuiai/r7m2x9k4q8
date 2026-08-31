# DomainPrediction and typed output contract

Status: R4 IMPLEMENTATION-VALIDATED — INDEPENDENT FINAL R4 REVIEW PENDING  
Internal schema version: `1.0.0`  
Public profile: unchanged `parasara_snapshot_v1` compatibility  
Owner: Parāśara engine maintainers  
Last verified: 2026-08-29

## Purpose

`engine/domain/models.py` is the immutable typed boundary between generic
inference and serialization. It is not a second inference model and contains
no astrology.

```text
InferenceResult + source RuleMatch/fact presentation identity
  -> DomainPrediction
  -> OutputAssemblyInput
  -> OutputAssembler
```

## Universal domain result

`DomainPrediction` supports Career, Wealth, Marriage, Children, Health, and
Safety through a closed `DomainId`; only Career has an interpreter in this
build. Evaluated Career results are produced from one private same-run value
binding the complete evaluator RuleMatch ledger, approved config and
fingerprint, `InferenceResult`, contribution lineage, and one stored
compatibility projection. Public `CareerEvaluationBatch` values remain
diagnostic-only. Evaluated domain/Yoga dictionaries are one-way DTOs and cannot
reconstruct authority. Projected values must exactly match:

- normalized score, confidence, and agreement;
- `ConflictRecord` order and values;
- `DataCompleteness` and missing capability references;
- source inference trace, system, rule-set version, and inference version;
- component, contribution, rule, evidence, and trace identities.

`DomainComponent` can preserve an existing Career compatibility row, but its
`score` is always the referenced authoritative `InferenceComponent` normalized
value. Its compatibility `weight` remains presentation data and never changes
domain inference. `DomainIndicator.contribution` is exactly the referenced
`Contribution.final_contribution`. Every Career indicator also resolves its
unchanged `RuleMatch` against the private evaluator ledger. A
score-bearing indicator cannot clear its contribution identity and a
contribution-free indicator cannot substitute a caller-owned match.

Narrative is deterministic post-inference presentation. Every section retains
rule, indicator, issue, or trace references and a template identity/version.
The current Career headline preserves the existing score/confidence summary;
no new astrology narrative policy was introduced.

## Status and failure

`evaluated`, `partial`, and `insufficient_evidence` correspond exactly to the
Prompt-03 result. `unavailable`, `not_supported`, `not_requested`, and `failed`
do not carry fabricated inference values. `DomainBuildRejected` is reserved for
invalid source identity, reconciliation, or construction; expected bounded
domain/capability states remain valid `DomainPrediction` statuses.

Typed `DomainIssue` values have stable identities/codes, bounded safe messages,
severity, phase, recovery status, optional capability/rule/trace references,
and recursively frozen JSON-safe detail. They do not expose stack traces,
exception objects, raw payloads, or Windows filesystem paths.

## Yoga diagnostic

`YogaDiagnostic` retains the exact authoritative `RuleMatch` and same-run
presentation record. It validates ID, category, domains, trace, rule
version, rule-set version, compatibility evidence, houses, and source order
against those sources. Canonical Yoga evaluation builds diagnostics internally;
public Yoga batches cannot construct authority. The record's frozen
compatibility evidence remains the approved presentation source for the
unchanged eight-key public row.

Prompt-02/WP17 Yoga baseline contradiction reconciled; Prompt-05 R4 validation
completed; independent Final R4 Review pending. A diagnostic condition Boolean
cannot override an invalid or unmatched RuleMatch, and disagreement is rejected
at authoritative YogaDiagnostic construction.

## Timing outputs

`DashaTimeline` and `TransitSummary` distinguish available, partial,
unavailable, not-requested, and failed. Available values require supplied
reference instants and calculation versions. Dasha validates chronology,
duration, nested parent containment, and active period references. Transit
validates finite normalized longitude, body/fact relationships, order, and
source resolution. No designated transit producer is integrated in this build,
so transit is truthfully `unavailable`; public factory calls and logical
reconstruction cannot mint available or ready-empty provenance.

Prompt-05 factories accept already-produced values only. The current primary
pipeline creates unavailable models and does not import/call the Vimshottari
calculator, a transit calculator, or a clock.

## Immutability and canonical serialization

Frozen slotted dataclasses use validated producer boundaries for top-level
Career and Yoga values, so direct construction and `dataclasses.replace`
cannot substitute coordinated public/private sources. Caller mappings/lists become recursively immutable
`FrozenMapping`/tuple values with sorted mapping keys and normalized negative
zero. Nonfinite values, cycles, unsupported runtime objects, duplicate IDs,
bad order, unresolved references, and incompatible versions fail.

Each top-level domain, Yoga, Dasha, and transit value carries lowercase SHA-256
over compact canonical JSON with `logical_digest` and nonlogical source object
references excluded. A supplied stale or incorrect digest fails construction.
Evaluated DomainPrediction/Yoga JSON is presentation-only and is rejected as an
authority input. Strict status/timing readers continue rejecting malformed
UTF-8, duplicate keys, nonfinite constants, unknown/missing fields, and
invariant violations.

## Output assembly and public compatibility

`engine/output_assembler.py` owns typed engine metadata, diagnostics,
explainability, `OutputAssemblyInput`, and the only `OutputAssembler`. The
assembler validates cross-object system/engine/rule-set/domain/Yoga order and
profile identities before producing a fresh public structure. It performs no
aggregation: Career base score and total contribution are selected from the
sealed inference-owned compatibility projection.

The current outward profile intentionally has no exposed schema-version field.
It preserves the existing top-level keys, `generated_at: null`, empty timing
arrays, skeletal explainability objects, exact Career fields/order/rounding,
and the compatibility-only Wealth placeholder. This profile is not evidence of
a Wealth interpreter. Rich internal typed fields remain unexposed until a
separately approved public schema migration.

## Versions

- domain/Yoga/Dasha/transit internal schemas: `1.0.0`;
- Career interpreter/narrative mapping: existing `1.0.0`;
- inference version: propagated from `InferenceResult`;
- rule/rule-set versions: propagated from `RuleMatch`/`InferenceResult`;
- engine version: current `0.1.0`;
- output internal schema: `1.0.0`;
- public compatibility profile: `parasara_snapshot_v1`.

General version selection, promotion, rollback, approval, and replay governance
remain Prompt-06.
