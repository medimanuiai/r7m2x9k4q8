# Parāśara Engine Documentation

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-13

## Purpose

This directory contains documentation for the Jyothishyam Parāśara interpretation engine. It covers the implemented runtime, approved target architecture, implementation planning, operational guidance, prompts, and audit evidence.

The structural migration is complete. Canonical content is being reviewed folder by folder under the organization and authority rules below. Former stable root paths are retained as compatibility pointers.

## Authority

When documents or code disagree, use this order:

1. Jyothishyam Master Architecture Specification.
2. Approved implementation prompts, including Prompt-01.
3. Approved audit decisions.
4. Source code and tests as evidence of current behavior.
5. Implementation, status, roadmap, and task documents.

The Master Architecture and approved prompts define what the system should become. Source code and tests establish what it currently does. Status documents do not override either.

## Start here

| Topic | Document | Purpose |
|---|---|---|
| Current implementation | [Current State](architecture/current-state.md) | Verified description of the present runtime and known gaps |
| Approved destination | [Target State](architecture/target-state.md) | Architectural requirements inherited from the Master Architecture |
| Documentation rules | [Documentation Policy](governance/documentation-policy.md) | Status labels, evidence rules, ownership, and migration policy |
| Stage prompts | [Prompt-01 Summary](prompts/prompt-01/README.md) | Stable authority, scope, and implementation gate; live workspace status is separate |
| Implementation status | [Canonical Status](implementation/status.md) | Evidence-based component status and known limitations |
| Delivery roadmap | [Canonical Roadmap](implementation/roadmap.md) | Ordered architecture stages and validation gates |
| Active work | [Canonical Tasks](implementation/tasks.md) | Actionable task registry without duplicated architecture claims |
| Specifications | [Specification Index](specifications/README.md) | Focused contracts extracted from legacy mixed specifications |
| Developer guides | [Guide Index](guides/README.md) | Testing and M1 vertical-slice workflows with side-effect classifications |
| Vertical slice | [Vertical Slice](guides/vertical-slice.md) | Current M1 snapshot path and target-boundary warning |
| Engineering guardrails | [Guardrails](governance/guardrails.md) | Approved invariant and validation gates |
| Operations | [Operations Index](operations/README.md) | Proposed controls and bounded operational evidence |
| Licensing | [Licensing Audit](operations/licensing-audit.md) | Scope and limitations of current license evidence |
| Migration validation | [Validation Evidence](evidence/documentation-validation-2026-07-12.md) | Point-in-time structural migration checks; not live stage status |
| Known gaps | [Implementation Gaps](implementation/gaps.md) | Verified missing capabilities and separately labeled proposals |
| Historical material | [Archive](archive/README.md) | Superseded mixed documents retained for provenance |

## Document statuses

- `AUTHORITATIVE`: controlling specification approved outside this directory.
- `APPROVED`: reviewed local decision or contract.
- `CURRENT-STATE`: evidence-based description of current behavior.
- `PROPOSED`: recommendation awaiting approval.
- `DRAFT`: incomplete working material.
- `HISTORICAL`: superseded material retained for provenance.
- `EVIDENCE`: point-in-time generated or audit evidence.

## Current organization

The documentation uses these controlled areas:

- `architecture/`: verified current architecture and approved target architecture.
- `specifications/`: focused approved contracts and explicit future requirements.
- `implementation/`: evidence-based status, roadmap, and actionable tasks.
- `governance/`: documentation and engineering governance.
- `guides/`: developer workflows that distinguish read-only checks from mutating commands.
- `operations/`: proposed operational controls and point-in-time compliance reviews.
- `evidence/`: dated generated evidence that must not be treated as a timeless specification.
- `prompts/`: stable implementation-stage summaries and gates; live stage workspaces are managed separately.

Former stable root paths contain historical compatibility pointers linking to canonical and archived documents. They are not independent sources of truth.

## Change discipline

- Do not combine documentation restructuring with engine behavior changes.
- Do not describe proposed components as implemented.
- Link completion claims to source, tests, schemas, CI, or approved audit evidence.
- Preserve historical prompts and audits; do not silently rewrite their conclusions.
- Update inbound links in the same change that moves a document.
