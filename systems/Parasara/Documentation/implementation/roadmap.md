# Parāśara Engine Roadmap

Status: APPROVED  
Authority: Master Architecture Specification and approved stage prompts  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-07-13

## Planning rule

Stages follow architectural dependencies. A later stage must not be used to conceal incomplete acceptance criteria in an earlier contract.

## Stage 0 — Documentation and evidence control

Status: STRUCTURE COMPLETE; CONTENT REVIEW IN PROGRESS

- Separate current and target architecture.
- Establish canonical status, roadmap, task, and specification documents.
- Validate canonical content folder by folder and correct stale external indexes.

Gate: authoritative documents, current behavior, proposals, and historical material are clearly distinguishable.

## Stage 1 — PredicateResult consolidation

Status: AUDIT REQUIRED

1. Complete the full approved prerequisite audit sequence maintained by the Prompt-01 stage workspace.
2. Approve the resulting migration boundaries and impact inventory.
3. Preserve compliant existing behavior.
4. Implement the universal immutable PredicateResult contract.
5. Migrate registry metadata, cache behavior, condition evaluation, active predicates, and affected callers.
6. Verify Yoga and domain compatibility, determinism, and serialization.

Gate: Prompt-01 acceptance criteria pass and active production paths contain no unapproved legacy predicate contract.

The roadmap does not duplicate live audit filenames or completion status. The stage workspace owns that changing audit sequence; this document records only the architectural gate.

## Stage 2 — Universal RuleMatch

Status: BLOCKED BY STAGE 1

- Establish one immutable RuleMatch model constructed by the generic Rule Engine.
- Preserve PredicateResults, evidence, provenance, versions, context, and deterministic trace identity.
- Migrate Yoga and Career away from custom match dictionaries.

## Stage 3 — Shared inference

Status: BLOCKED BY STAGE 2

- Implement one generic InferenceEngine.
- Centralize aggregation, normalization, conflict resolution, confidence, and contribution decomposition.
- Remove generic inference policies from Career and future interpreters.

## Stage 4 — Stable AstroState access

Status: PLANNED

- Add factual read-only query methods.
- Add capability and completeness metadata.
- Define explicit missing-data behavior and deterministic ordering.
- Prevent downstream raw Surya access.

Implementation may be coordinated with earlier stages only where their approved scope requires compatibility access.

## Stage 5 — Typed domains and output

Status: BLOCKED BY STAGE 3

- Introduce typed domain models.
- Make Career a thin interpreter, then add other domains through the same contract.
- Create the serialization-only OutputAssembler.

## Stage 6 — Version selection and governance

Status: PLANNED

- Introduce explicit EngineConfig and rule-set selection.
- Propagate versions through caches, matches, traces, snapshots, and output.
- Enforce strict and experimental rule policies.
- Add promotion, rollback, approval, and audit mechanisms.

## Stage 7 — DSL and dependency baseline

Status: PLANNED

- Add the approved bounded DSL operators.
- Add canonical AST validation and deterministic traversal.
- Implement an explicit rule dependency graph with cycle detection.

## Stage 8 — Validation and calibration

Status: PARTIAL INFRASTRUCTURE

- Validate astronomy separately from Jyotisha normalization.
- Expand golden and boundary coverage.
- Obtain SME-reviewed rule and classical-calculation evidence.
- Add deterministic replay and version-isolation evidence.
- Build historical calibration only from consented, governed data.

Validation work may run alongside architecture stages when it does not change their contracts, but it cannot be used to declare an incomplete contract production-ready.

## Stage 9 — Production readiness

Status: NOT STARTED

- Public engine facade and version negotiation.
- Performance baselines and cache safety.
- Monitoring, privacy, retention automation, recovery, and deployment controls.

## Milestone policy

Milestone completion requires acceptance evidence, not the presence of a scaffold, file, or local command result. Status is maintained in `status.md`; actionable work is maintained in `tasks.md`.
