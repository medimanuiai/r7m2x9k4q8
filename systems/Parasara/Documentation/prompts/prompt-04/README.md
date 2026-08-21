# Prompt-04 — AstroState API

Status: IMPLEMENTED — REMEDIATED, PENDING FINAL APPROVAL CHECK
Last verified: 2026-08-21

Prompt-04 implements one immutable `AstroStateSnapshot` after mutable chart
construction and existing factual producers. The snapshot exposes explicit,
deterministic typed queries and capability readiness without owning predicates,
rules, inference, domain scoring, narratives, or public serialization.

The seven Prompt-01 prepared capabilities remain byte-identical. Yoga, Career,
and snapshot generation now evaluate/query the immutable boundary through
narrow compatibility wrappers, with existing Career/Yoga public outputs and
the approved MVP snapshot unchanged. Dasha/transit availability remains
truthfully unavailable; existing Shadbala values are marked partial/proxy.
All public immutable models defensively freeze nested caller values, including
construction through `dataclasses.replace`. Capability records enforce their
catalog version, core path, readiness/content/empty-state contract, and factual
presence flags; snapshots reconcile core-backed readiness with `AstroCore`.
Core-backed supplies cannot introduce a competing fact owner. Aspect endpoints
must belong to the snapshot entity set, whole-sign planet targets must agree
with their canonical sign, and sign targets resolve to canonical snapshot
houses. Invalid supplied aspect content fails fatally before publication and
produces no snapshot; nonfatal malformed capability availability remains a
distinct typed state. Canonical Career evaluation exposes unexpected
programming defects while expected factual unavailability remains typed.

Validation is composed by `tools/validate_prompt04.py` through WP17 and the
current Prompt-02/03/04 gates. The historical raw Prompt-01 validator and digest
remain preserved and are not reinterpreted as a current aggregate gate.
Dual-lane full validation collects 912 nodes and completes with 910 passed and
2 existing skips; all 62 Prompt-04 tests and 38 remediation tests pass, all
remediation findings R1-R10 are verified, and
the remediated Prompt-04 manifest is
`440a459cc60e9575874341e7c6673e714585ae79123957c9c19ccd175cb7930b`.
Personal exports are protected when present but are not required in clean CI.

Prompt-04 does not implement Prompt-05 typed domain models or OutputAssembler.
Structural validation does not imply scientific/SME or production approval.
