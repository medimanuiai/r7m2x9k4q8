# Prompt-01: PredicateResult Consolidation

Status: CURRENT-STATE  
Authority: Jyothishyam Master Architecture Specification and approved Prompt-01  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-12

## Objective

Prompt-01 establishes one typed, immutable, deterministic `PredicateResult` contract for every active registered predicate and migrates the affected evaluation, caching, tracing, error-handling, and caller boundaries.

It is a contract-consolidation stage. It must not silently redesign astrological calculations, universal RuleMatch, shared inference, domain scoring, or unrelated DSL behavior.

## Authority

Apply this order within Prompt-01 work:

1. Jyothishyam Master Architecture Specification.
2. Approved Prompt-01 requirements.
3. Approved Prompt-01 audit decisions.
4. Source code and tests as evidence of current behavior.
5. Implementation and status documents.

The currently approved Prompt-01 source is `Documentation/AI-Prompt/Prompt-01.docx`. A reviewed Markdown copy may be added here in a later documentation batch; until then, this index does not replace that source.

## Current implementation baseline

An initial `PredicateResult` implementation exists in `systems/Parasara/engine/rules/engine.py`. It must be preserved where it agrees with the approved architecture and completed or replaced only where evidence shows noncompliance.

Known baseline characteristics requiring Audit-1 verification include:

- a global predicate registry storing handlers;
- import-triggered predicate registration;
- an initial frozen result dataclass with mutable nested collections;
- tuple-return compatibility in predicate evaluation;
- an in-memory cache keyed partly by AstroState object identity;
- generic predicate-leaf and `AND`/`OR` evaluation;
- Yoga integration through the generic condition evaluator;
- separate raw-boolean helpers and M1 rule evaluation in `rules/runtime.py`.

These statements are orientation, not final audit conclusions.

## Approved decisions

- Preserve existing PredicateResult behavior where it agrees with the Master Architecture.
- Do not discard working compatibility behavior without evidence.
- Audit raw-boolean functions in `runtime.py`; do not automatically migrate or delete them unless Prompt-01 scope requires it.
- Do not decide whether `ASPECT` and `ASPECT_EXISTS` are aliases or separate identities until callers, rules, tests, and compatibility requirements are audited.
- Do not guess ownership of the two rule-directory trees; determine it from loaders, imports, runtime paths, CI, tests, and documentation.
- Preserve simplified astrological calculations unless PredicateResult correctness requires a change.
- Complete Audit-1 before Prompt-01 implementation.

## Audit workspace status

The active audit workspace is indexed at `../../Engine/Prompt-01/Audits/README.md`. Its Audit 1–4 files are instruction templates with unpopulated report sections; `Audit-5.md` is empty. No completed audit deliverable currently exists at the report paths specified by those templates.

Claims inside later templates that earlier audits are complete describe expected workflow state and are not completion evidence.

## Audit sequence

### Audit-1: Predicate registry

Audit registration, storage, discovery, initialization, metadata, duplicates, aliases, lookup behavior, deterministic enumeration, test isolation, loader interaction, and Prompt-01 compliance.

The existing audit instruction is currently located at:

`systems/Parasara/Documentation/Engine/Prompt-01/Audits/Audit-01-Predicate-Registry.md`

The instruction template remains separate from any completed report. Its embedded report headings are currently unpopulated.

### Later impact analysis

Subsequent approved audits or migration inventories should establish:

- all registered predicates and return formats;
- tuple-unpacking and raw-boolean callers;
- cache consumers and version inputs;
- condition-evaluator boundaries;
- Yoga and domain compatibility;
- serialization and snapshot exposure;
- rule-directory ownership relevant to predicate validation.

## Implementation gate

Prompt-01 implementation must not begin until Audit-1 establishes the current registry contract, impact surface, conflicts, backward-compatibility requirements, and migration boundaries.

Prompt-01 must not be marked complete while active registered predicates or active callers remain on an unapproved legacy contract.

## Out of scope for this documentation batch

- Running or completing Audit-1.
- Changing PredicateResult code.
- Moving or renaming existing Prompt-01 audit templates.
- Deciding `ASPECT` versus `ASPECT_EXISTS` semantics.
- Choosing rule-directory ownership.
- Changing rule, Yoga, Career, scoring, or astrological behavior.
