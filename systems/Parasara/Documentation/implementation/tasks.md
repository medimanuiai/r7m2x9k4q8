# Parāśara Engine Active Tasks

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-17

## Task rules

- This file records actionable work, not architectural specifications.
- Status claims link to an acceptance result or remain open.
- Legacy `P#-Task#` identifiers are preserved in `../archive/legacy-tasks.md` and are not active unless deliberately reconciled here.
- Do not start a blocked task by broadening the scope of its prerequisite.

## Active documentation migration

| ID | Task | Status | Acceptance |
|---|---|---|---|
| DOC-001 | Establish documentation index and authority policy | COMPLETE | Index, current/target architecture, policy, and Prompt-01 index exist |
| DOC-002 | Establish canonical status, roadmap, tasks, and specifications | COMPLETE | Focused documents exist and index links resolve |
| DOC-003 | Correct and migrate guides, governance, and operations documents | COMPLETE | New locations contain corrected content and known references are updated |
| DOC-004 | Archive superseded mixed documents | COMPLETE | Valid content extracted, replacement notices present, history preserved |
| DOC-005 | Validate repository-wide documentation links and stale paths | COMPLETE | Structural migration validation is recorded in `../evidence/documentation-validation-2026-07-12.md`; live stage-workspace status is tracked separately |

## Active content review

| ID | Area | Status | Acceptance |
|---|---|---|---|
| DOC-C01 | Architecture | COMPLETE | Current and target documents match verified source boundaries and approved architecture |
| DOC-C02 | Specifications | COMPLETE | All focused contracts distinguish target requirements from current compatibility behavior |
| DOC-C03 | Implementation | COMPLETE | Status, roadmap, and tasks use evidence-based language and do not duplicate live audit status |
| DOC-C04 | Governance | COMPLETE | Policies and guardrails distinguish requirements, evidence, approval, implementation, and current CI enforcement |
| DOC-C05 | Guides | COMPLETE | Commands, paths, test side effects, mutation warnings, Makefile limits, and CI statements are verified |
| DOC-C06 | Operations | COMPLETE | Proposed controls, current repository evidence, privacy/reliability decisions, and license-audit limitations are distinguished |
| DOC-C07 | Root pointers and indexes | COMPLETE | Migration wording, pointer metadata, gaps document, and external TOC links are corrected |

## Prompt-01 implementation

| ID | Task | Status | Acceptance |
|---|---|---|---|
| P01-AUD | Complete and approve the stage prerequisite audits | COMPLETE | Audit reports and locked decisions preserved in the Prompt-01 workspace |
| P01-I01 | Implement approved PredicateResult contract | COMPLETE | WP02-WP03 and WP17 executable contracts |
| P01-I02 | Migrate predicate registry and cache | COMPLETE | WP04-WP09 and cache/registry determinism tests |
| P01-I03 | Migrate active predicates and condition evaluation | COMPLETE | WP08-WP12 and typed condition tests |
| P01-I04 | Migrate callers and verify compatibility | COMPLETE | WP13-WP16; Yoga/Career/tooling compatibility |
| P01-I05 | Complete validation and CI/docs sign-off | COMPLETE | WP17-WP19 and authoritative dual-lane gate |

## Deferred architecture work

| ID | Task | Status | Dependency |
|---|---|---|---|
| P02-001 | Universal RuleMatch | DEFERRED / READY FOR OWNER AUTHORIZATION | Prompt-01 complete |
| P03-001 | Shared InferenceEngine | DEFERRED | Universal RuleMatch complete |
| P04-001 | Stable AstroState query API | DEFERRED | Approved stage entry |
| P05-001 | Typed domain outputs and thin Career interpreter | DEFERRED | Shared inference complete |
| P05-002 | OutputAssembler | DEFERRED | Typed output contracts approved |
| P06-001 | Explicit engine and rule-set version selection | DEFERRED | Approved stage entry |
| P07-001 | DSL baseline extensions | DEFERRED | Stable predicate/rule contracts |
| P08-001 | Rule dependency graph | DEFERRED | Stable DSL compiler contract |
| REL-001 | Privacy/security/licensing/publication findings | SEPARATE OWNER WORK | Audit-25; before applicable public release |
