# Parāśara Engine Guardrails

Status: APPROVED  
Authority: Master Architecture Specification and approved stage prompts  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-07-17

## Architectural invariants

- Astronomy and astrological interpretation remain separate systems.
- AstroState is the sole downstream chart contract after normalization.
- Identical inputs, versions, configuration, and evaluation instant produce identical logical output.
- Predicates answer facts and never score, narrate, assign confidence, or mutate state.
- Rules express versioned astrological meaning and retain evidence and provenance.
- One shared InferenceEngine owns generic scoring, normalization, conflict handling, and confidence.
- Domain interpreters remain thin and evidence-backed.
- The OutputAssembler alone serializes public output.
- Every production rule and conclusion is versioned, explainable, auditable, and governed.
- Missing capability, invalid input, factual nonmatch, evaluation error, and insufficient data remain distinguishable.
- Shared infrastructure remains free of interpretation-system-specific astrological meaning.

## Change guardrails

- Do not redesign unrelated architecture inside a stage-specific prompt.
- Preserve current astrological mathematics during contract migrations unless correctness of that contract requires a change.
- Do not convert unavailable data into negative factual evidence.
- Do not hide defects through broad best-effort exception handling.
- Do not update or approve snapshots merely because an internal contract changed.
- Do not describe scaffolds or file existence as completed acceptance.
- Do not make active engine behavior depend on test packages, process working directory, random identity, or implicit wall-clock time.
- Do not silently replace duplicate registry/rule identities or fall back to an unrequested version.

## Validation gates

Astronomy and sidereal/Jyotisha normalization require separate validation. Strengths, aspects, functional roles, vargas, Yoga, and Dasha require deterministic evidence plus appropriate classical or SME review. Rule metadata, identity, schema, versions, provenance, lifecycle, dependencies, and applicable approval must be enforced before production.

Required validation dimensions are independent:

- contract and schema validation;
- unit and integration behavior;
- deterministic replay and version isolation;
- scientific/classical correctness;
- SME and governance approval;
- operational readiness.

Evidence for one dimension must not be presented as completion of another.

## Stage gates

Every implementation stage must complete its approved prerequisite audit and decision sequence before code migration begins. The stage workspace owns live audit filenames and progress; this guardrail records only the stable requirement.

Compatibility behavior is preserved unless approved evidence shows that it violates the active stage contract. A contract migration must not silently redesign astrological mathematics or later architectural layers.

## Current automated enforcement

`tools/validate_prompt01.py full` enforces typed contracts,
architecture/purity/safety, complete regression, deterministic manifest and
serialization, Yoga/loader order, Career/tooling compatibility, exact
supported-file rule lint, strict no-update snapshot bytes, and protected
artifact/worktree preservation.

`.github/workflows/ci.yaml` installs the WP00 lock and runs that command as a
blocking Python 3.11/3.14 matrix. It has no weak retry, failure suppression,
credentialed mutation, snapshot approval, or report-tree upload. The
supplemental snapshot workflow uses the same lock and an explicit temporary
output.

These gates do not prove scientific validation, SME approval,
branch-protection configuration, privacy/security/license readiness, or
production readiness.

## Additional enforcement required before production

- Rule/schema linting and duplicate/version validation in CI.
- Determinism and version-isolation checks.
- Deliberate golden/snapshot approval without automatic acceptance of drift.
- Scientific and classical validation gates appropriate to each component.
- Production rule lifecycle and SME policy enforcement.
- Dependency/license, security, privacy, and operational control evidence.

## Production gate

The engine is not production-ready until architecture contracts, scientific validation, deterministic replay, governance, security/privacy controls, monitoring, and operational recovery have acceptance evidence.
