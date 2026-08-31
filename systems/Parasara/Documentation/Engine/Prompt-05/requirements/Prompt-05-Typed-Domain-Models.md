# Prompt-05 — Typed Domain Models

Status: IMPLEMENTED — REMEDIATION R1 COMPLETE; PENDING INDEPENDENT FINAL R1 REVIEW  
Owner: Parāśara engine maintainers  
Starting commit: `c719a1bf686e1e37eb8542f9323fc279b670250e`  
Implementation date: 2026-08-21

## Authority and boundary

This is the canonical repository requirements summary for Prompt-05. The
Jyothishyam Master Architecture Specification, Prompt Plan, and approved
Prompt-01 through Prompt-04 contracts remain higher authority. The complete
approved implementation brief supplied for this work remains the controlling
Prompt-05 source where this summary is silent.

Prompt-05 establishes this boundary:

```text
AstroStateSnapshot
  -> PredicateResult / RuleMatch[]
  -> shared InferenceEngine / InferenceResult
  -> thin evidence-backed presentation mapping
  -> immutable DomainPrediction
  -> serialization-only OutputAssembler
  -> unchanged approved public compatibility output
```

It does not authorize astrology changes, inference arithmetic changes, public
schema changes, additional domain interpreters, Dasha/transit calculation,
rule-set governance, DSL work, staging, commit, push, PR, merge, or Prompt-06.

## Locked ownership

- `AstroStateSnapshot` owns facts and factual capability availability.
- `PredicateResult` owns predicate outcomes.
- `RuleMatch` owns universal rule meaning, rule metadata, provenance, rule
  evidence, and rule trace.
- Prompt-03 `InferenceResult`, `Contribution`, `InferenceComponent`,
  `ConflictRecord`, `DataCompleteness`, and `EvidenceReference` remain the sole
  owners of inference values.
- Prompt-05 presentation objects reference those owners; they do not create or
  adjust scores, confidence, agreement, completeness, contributions, conflicts,
  facts, or evidence.
- `OutputAssembler` serializes validated typed inputs under an explicit profile
  and owns no calculation.

## Required contracts

The implementation must provide closed `DomainId`, `DomainStatus`, narrative,
issue-severity, and timing-status enums plus deeply immutable contracts for:

- `DomainIssue`;
- `DomainComponent` and `DomainIndicator` with mandatory source identities;
- `NarrativeSection` and `DomainTimingReference`;
- one universal `DomainPrediction`;
- `YogaDiagnostic` containing the authoritative `RuleMatch`;
- `DashaPeriod` / `DashaTimeline`;
- `TransitPosition` / `TransitRelationship` / `TransitSummary`;
- `DomainBuildProduced | DomainBuildRejected`;
- typed output-assembly metadata, diagnostics, explainability, and input.

Every public constructor and `dataclasses.replace` path must revalidate
invariants and defensively freeze nested input. Top-level Prompt-05 models must
carry a lowercase SHA-256 digest of canonical logical content with the digest
field excluded. NaN, infinity, negative-zero drift, duplicate identities,
unresolved references, mutable nested values, invalid versions, and invalid
status/field combinations must fail deterministically.

## Domain status matrix

- `evaluated`, `partial`, and `insufficient_evidence` require one immutable
  `InferenceResult`. Score, confidence, agreement, completeness, conflicts,
  versions, and inference trace must reconcile exactly.
- `partial` requires typed incompleteness/issues.
- `insufficient_evidence` retains the exact Prompt-03 neutral/confidence result;
  Prompt-05 must not manufacture it.
- `unavailable`, `not_supported`, `not_requested`, and `failed` cannot carry a
  fabricated score, confidence, agreement, component, indicator, conflict, or
  completeness claim.
- Missing capability, factual nonmatch, insufficient evidence, unsupported,
  unrequested, ready-empty, and execution failure remain distinct.

## Career

Career is the only substantive Prompt-05 interpreter migration. It must:

- prepare facts from one immutable snapshot using the preserved typed Career
  batch;
- evaluate the preserved universal `RuleMatch` path;
- call the one shared `InferenceEngine` once;
- map the result to a closed typed build outcome;
- preserve component and candidate source order and lineage;
- obtain final score/confidence only from `InferenceResult`;
- publish the exact existing Career dictionary only through a named one-way
  compatibility projection.

Wealth, Marriage, Children, Health, and Safety receive shared model readiness
only. No interpreter or synthetic evaluated result is authorized.

## Yoga

Each existing Yoga record must map to one `YogaDiagnostic` without re-running
Yoga detection. The diagnostic must validate yoga ID, match Boolean, status,
domains, rule version, rule-set version, and trace against its authoritative
`RuleMatch`. Existing firing, source order, public row shape, evidence, and
trace must remain exact.

## Timing

Prompt-05 timing types validate already-supplied output and availability only.
They must not import/call calculators or the clock. The current primary Dasha
and transit paths remain explicitly unavailable; public compatibility continues
to emit the approved empty arrays. Available Dasha periods require supplied
chronology, parent resolution, active-period resolution, reference instant, and
calculation version. Available transit relationships require supplied position
and fact references.

## OutputAssembler

There must be exactly one active `OutputAssembler`. It must:

- accept only the validated immutable `OutputAssemblyInput`;
- reject incompatible engine, system, rule-set, domain, Yoga order, schema, and
  compatibility-profile identities;
- serialize enums, tuples, immutable mappings, optionals, and ordered objects
  deterministically;
- return fresh JSON-safe structures, canonical bytes, and a logical digest;
- preserve the exact existing public schema, omission/null behavior, numeric
  rounding, ordering, Career/Yoga rows, placeholder Wealth row, timing arrays,
  and snapshot bytes.

It must not import or call adapters, AstroState, predicates, rule evaluation,
`InferenceEngine`, interpreters, Dasha/transit calculators, or frontend code.

## Compatibility wrappers

- Career dictionary wrapper: remove only after all supported public consumers
  move to an approved versioned typed/public schema and snapshots are approved.
- Yoga row wrapper: remove only after all consumers accept `YogaDiagnostic` or
  an approved serialized schema.
- Snapshot compatibility profile: remove only through an approved public
  schema migration.
- Wealth placeholder: replace/remove only in separately approved Wealth/public
  schema work; it is not a typed domain implementation.

## Validation and acceptance

Acceptance requires focused/adversarial/model/integration/architecture/purity/
serialization/determinism tests; composed Prompt-01–04 gates; full Windows
Python 3.11 and 3.14 lanes with identical Prompt-05 manifest; exact approved
snapshot; protected artifact and personal-export integrity; frontend validation;
and a clean scope/stopping report.

Structural and deterministic acceptance does not establish scientific/SME,
privacy, security, licensing, operational, public-release, or production
approval.

The implementation must stop before staging, commit, push, PR, merge, or
Prompt-06.
