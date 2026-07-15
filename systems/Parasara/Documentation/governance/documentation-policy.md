# Parāśara Documentation Policy

Status: APPROVED  
Authority: Project documentation governance under the Master Architecture  
Approval basis: Approved documentation restructuring and staged review sequence  
Owner: Parāśara engine maintainers  
Effective: 2026-07-12
Last reviewed: 2026-07-13

## Purpose

This policy keeps Parāśara documentation distinguishable by authority, lifecycle, and evidence. It applies to documents under `systems/Parasara/Documentation`.

## Authority hierarchy

1. Jyothishyam Master Architecture Specification.
2. Approved stage prompts.
3. Approved audit decisions.
4. Source code and tests as current-behavior evidence.
5. Implementation, status, roadmap, and task documents.

Lower-authority documents must identify conflicts rather than reinterpret higher-authority requirements.

## Required metadata

New or materially rewritten Markdown documents must declare:

- `Status`
- `Owner`
- `Last verified`, `Last reviewed`, or `Effective` date
- `Authority` when the document summarizes an external controlling specification
- `Approval basis` when `Status: APPROVED` is used

Approval metadata identifies why a document is approved; it does not imply that every component it describes is implemented.

## Status meanings

### AUTHORITATIVE

A controlling specification. This label must not be applied locally unless the document is formally designated as authoritative.

### APPROVED

A reviewed decision, policy, or local contract. Approval must be explicit.

The approval basis and approving authority or decision context must be recorded. An approved target contract may still have a partial or missing implementation.

### CURRENT-STATE

An evidence-based description of existing behavior. Claims should link to source, tests, schemas, workflows, or audit evidence.

### PROPOSED

A recommendation awaiting approval. It must not be presented as required or implemented behavior.

### DRAFT

Incomplete working material unsuitable as an implementation contract.

### HISTORICAL

Superseded material retained for provenance. It must link to its replacement when one exists.

### EVIDENCE

A point-in-time audit or generated artifact. Evidence must record how and when it was produced and must not be silently regenerated.

Evidence must also record its scope, method or command where applicable, limitations, and the repository/environment state needed to interpret it. Live status should not be inferred from old evidence.

## Document roles

- Architecture documents define verified current boundaries or approved target boundaries.
- Specifications define focused normative contracts.
- Implementation documents report evidence-based status, dependency order, and actionable work.
- Governance documents define policy and gates.
- Guides describe reproducible workflows and distinguish read-only from mutating commands.
- Operations documents distinguish proposed controls from implemented evidence.
- Compatibility pointers preserve stable paths without duplicating canonical content.
- Archived documents retain provenance and are not maintained as current truth.

## Current and target architecture

Current-state documents answer what the repository does now. Target-state documents answer what approved architecture requires. A document must not blend these without explicit labels.

Source code may contradict status documentation. In that case, current-state documentation follows verified code behavior and records the discrepancy. Source behavior does not override an approved target requirement.

## Completion claims

A component may be marked complete only when its stated acceptance criteria have evidence. Depending on the claim, evidence may include:

- active source paths;
- targeted passing tests;
- schema validation;
- CI workflow enforcement;
- deterministic or golden evidence;
- required SME or governance approval.

File existence alone is not completion evidence. Local dependency installation is not project-completion evidence.

Where relevant, completion must distinguish:

- contract implementation;
- unit/integration validation;
- deterministic replay;
- scientific or classical validation;
- SME/governance approval;
- production operational readiness.

Passing one gate does not imply the others.

## Prompts and audits

- Preserve the approved wording of prompts.
- Store instructions separately from completed audit reports.
- Treat audit reports as point-in-time evidence.
- Record approved audit decisions without rewriting the original findings.
- Do not begin implementation when an approved prompt requires an incomplete prerequisite audit.
- Keep live audit sequencing and status in the stage workspace; canonical architecture and implementation documents should record only stable gates and approved decisions.

## Moves and archives

- Do not delete a document until valid content and inbound references have been reviewed.
- Update repository references in the same change that moves a document.
- Preserve superseded documents under `archive/` when they contain historical decisions or provenance.
- Add a replacement notice when a formerly stable path must remain discoverable.
- Record structural migrations in `CHANGELOG.md`.

Compatibility pointers must use `Status: HISTORICAL` plus an explicit document type. New documents must use repository-relative links that resolve from the containing Markdown file.

## Change boundaries

- Documentation reorganization must not change engine behavior.
- Prompt-stage implementation must not be hidden inside documentation cleanup.
- Status correction must not broaden the scope of an approved implementation stage.
- Simplified calculations remain documented current behavior unless a separately approved task changes them.

## Evidence and enforcement language

Documents must distinguish:

- `required`: mandated by an approved contract or policy;
- `implemented`: present in active source;
- `enforced`: automatically checked by active tooling or CI;
- `validated`: checked by recorded evidence;
- `approved`: accepted by the required authority.

Do not describe a rule as CI-enforced merely because a linter or script exists. Cite the active workflow step that enforces it. Do not describe a policy as operationally implemented without infrastructure or runbook evidence.

## Content freshness

- Update `Last verified` only after checking current source/evidence.
- Update `Last reviewed` when normative content is reviewed without asserting implementation verification.
- Point-in-time evidence keeps its original evidence date.
- Changing stage-workspace files must not require canonical documents to enumerate live filenames or transient completion states.
- Known stale or unresolved claims must be labeled, corrected, or moved to the archive.

## Review checklist

Before merging a documentation change, verify:

- authority and status are explicit;
- current and target behavior are not conflated;
- local paths exist or are clearly marked proposed;
- completion claims have evidence;
- moved paths have no unresolved inbound references;
- prompts, audits, and decisions retain provenance;
- no unrelated source behavior changed.
- approval basis is present for approved documents;
- claims of enforcement cite an active enforcement mechanism;
- repository-relative links resolve from the document location;
- live stage-workspace details are not duplicated unnecessarily.
