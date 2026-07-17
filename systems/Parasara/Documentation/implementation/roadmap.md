# Parāśara Engine Roadmap

Status: APPROVED  
Authority: Master Architecture Specification and approved stage prompts  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-07-17

## Planning rule

Stages follow architectural dependencies. A later stage must not be used to conceal incomplete acceptance criteria in an earlier contract.

## Stage 0 — Documentation and evidence control

Status: STRUCTURE COMPLETE; CONTENT REVIEW IN PROGRESS

- Separate current and target architecture.
- Establish canonical status, roadmap, task, and specification documents.
- Validate canonical content folder by folder and correct stale external indexes.

Gate: authoritative documents, current behavior, proposals, and historical material are clearly distinguishable.

## Stage 1 — PredicateResult consolidation

Status: COMPLETE (2026-07-17)

1. Completed prerequisite audits and locked decisions.
2. Implemented immutable typed predicate/condition contracts.
3. Migrated registry, parameters, capabilities, prepared state,
   evaluator/cache, active predicates, Yoga, Career facts, and tooling callers.
4. Retired active legacy adapters while preserving public behavior.
5. Added executable architecture/determinism and dual-Python CI gates.
6. Recorded WP18 regression/performance and WP19 completion evidence.

Gate: Prompt-01 acceptance criteria pass and active production paths contain no unapproved legacy predicate contract.

Completion is Prompt-01 contract completion only, not production or release
approval.

## Stage 2 — Universal RuleMatch

Status: READY FOR SEPARATE AUTHORIZATION

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
