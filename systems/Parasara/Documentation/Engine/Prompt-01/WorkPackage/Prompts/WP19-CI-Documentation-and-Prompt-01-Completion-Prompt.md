Implement **WP19 — strengthen the bounded Prompt-01 CI gate, update Stage-01 documentation/completion records, and produce final Prompt-01 sign-off**.

Do not merely review this specification. Implement the CI and documentation changes, validate the CI-equivalent commands locally in both locked Python lanes, and create the WP19 completion report. WP19 is the final planned work package; **do not invent WP20 or begin future-stage work**.

## Objective

Complete Prompt-01 by ensuring that future changes cannot merge with a green Stage-01 status while violating the contracts proven through WP18.

WP19 must:

- provide one discoverable, non-mutating, deterministic Prompt-01 validation entry point;
- wire the bounded Stage-01 gates into CI with failure propagation and no fallback that hides failures;
- validate the supported Python 3.11 lane and forward Python 3.14 lane according to the locked dual-Python decision;
- enforce typed contracts, architecture, safety, determinism, rule lint, Yoga/Career compatibility, and strict no-update snapshot comparison;
- use reproducible dependencies from the WP00 decision/lock rather than ad hoc divergent installs;
- avoid publishing raw report trees, credentials, personal/chart data, or provider diagnostics as part of the Prompt-01 gate;
- update the implemented predicate/condition/Yoga/Career architecture and authoring/testing references;
- update status, roadmap, active tasks, changelog, indexes, and `tests/COMPLETION_MATRIX.md` with evidence-backed claims only;
- preserve authoritative specifications and completed audit/WP reports as historical evidence rather than rewriting them;
- record Prompt-01 as complete only if all WP19 local/CI-equivalent gates pass;
- state explicitly that Prompt-01 completion is **not** release, privacy, security, licensing, or publication approval.

## Hard preflight gate

Before editing:

1. Locate and read by exact filename:
   - the locked Prompt-01 decisions/execution plan;
   - `Prompt-01-Final-Audit-Consolidation.md`;
   - final WP00-R and WP01 reports;
   - WP02 through WP18 completion reports;
   - Audits 22, 23, 24, and 25;
   - the current CI workflows, dependency sources, documentation policy, guardrails, documentation indexes, implementation status/roadmap/tasks/gaps, specifications, testing/rule guides, changelog, and completion matrix.
2. Require every predecessor through WP18 to record `VERDICT: COMPLETE` and WP18 to record `WP19_READY: YES`.
3. Record and preserve the inherited dirty worktree. Do not restore, stage, clean, commit, push, or overwrite unrelated changes.
4. Reproduce the essential WP18 acceptance gate in both locked Python environments before making CI/documentation changes:
   - 781 identical ordered nodes;
   - node-ID SHA-256 `0b3ae6acb231a374a50fdc21b4c78c270340657f6365a3823136b2b7f53b0f7a`;
   - 779 passed and 2 optional skips;
   - WP17 focused enforcement;
   - deterministic manifest SHA-256 `01b53b093e62e328de7758ed543a2c8f3b06c3a97e0502d7e879730e8c10d256`;
   - five-file rule lint;
   - strict approved snapshot match with SHA-256 `da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`.
5. Hash the WP18 protected-artifact manifest before edits.

Treat the counts/hashes as the inherited baseline. Final collection may increase only if WP19 adds legitimate command/config validation tests; it must remain identical between Python lanes.

If a prerequisite fails, stop without CI/documentation edits and report:

```text
VERDICT: BLOCKED
PROMPT_01_COMPLETE: NO
```

## Scope and authority boundary

WP19 may change only:

- the minimum relevant CI workflow(s);
- a small local Prompt-01 validation script/configuration if needed;
- focused tests for that script/workflow contract;
- Stage-01 documentation, navigation, status, changelog, and completion records;
- the WP19 completion report.

Do not change production behavior, astrology semantics, predicates, conditions, Yoga, Career, rules/YAML/tables, public schemas, snapshots/goldens, fixtures, dependency versions, or approved artifacts.

Do not add a formatter, type checker, coverage threshold, concurrency redesign, secret scanner, license scanner, benchmark framework, new dependency, or broad DevOps modernization merely because Audit-23/Audit-25 identified future gaps. Only the minimum Prompt-01 acceptance gate is in scope.

Any discovered production/test regression blocks WP19 and requires a separately authorized remediation package.

## Phase 1 — current CI and documentation inventory

Build a live, evidence-backed before-state inventory.

### CI inventory

For each workflow/job/step relevant to Parasara or Prompt-01, record:

- triggers and path filters;
- Python versions;
- dependency install source;
- working directory and environment variables;
- exact test/lint/snapshot/report commands;
- whether failure is propagated, suppressed, retried, or hidden by fallback;
- mutation, fixed-path write, branch/PR creation, artifact upload, credential, and data-exposure risk;
- whether it is a blocking validation gate, advisory automation, or unrelated workflow.

Pay particular attention to:

- `pytest -n auto || pytest` style fallback;
- `|| true`, `continue-on-error`, and shell error-handling gaps;
- full `tests/reports` uploads;
- automatic snapshot/report PR creation;
- divergent dependency install commands;
- snapshot output paths;
- workflow path filters that omit rule, validation-tool, dependency, or documentation changes.

### Documentation inventory

Verify the live status of every Audit-24 record, including:

- `systems/Parasara/Documentation/architecture/current-state.md`;
- `systems/Parasara/Documentation/architecture/target-state.md`;
- `systems/Parasara/Documentation/specifications/predicates.md`;
- `systems/Parasara/Documentation/specifications/rules.md`;
- `systems/Parasara/Documentation/specifications/astrostate.md`;
- `systems/Parasara/Documentation/specifications/output.md`;
- `systems/Parasara/Documentation/specifications/timing.md`;
- `systems/Parasara/Documentation/prompts/prompt-01/README.md`;
- `systems/Parasara/Documentation/README.md`;
- `systems/Parasara/Documentation/guides/testing.md`;
- `systems/Parasara/Documentation/guides/vertical-slice.md`;
- `systems/Parasara/Documentation/governance/guardrails.md`;
- `systems/Parasara/Documentation/governance/documentation-policy.md`;
- `systems/Parasara/Documentation/implementation/status.md`;
- `systems/Parasara/Documentation/implementation/roadmap.md`;
- `systems/Parasara/Documentation/implementation/tasks.md`;
- `systems/Parasara/Documentation/implementation/gaps.md`;
- `tests/COMPLETION_MATRIX.md`;
- `systems/Parasara/Documentation/CHANGELOG.md`;
- `systems/Parasara/rules/parashara/v1/README.md`;
- `tests/testing_framework/README.md`;
- applicable documentation indexes/TOCs and dated validation evidence.

Do not edit every listed document automatically. Classify each as `UPDATE_REQUIRED`, `LINK_ONLY`, `ACCURATE_NO_CHANGE`, `HISTORICAL_PRESERVE`, or `FUTURE_STAGE_PRESERVE`, and update only what the implemented Stage-01 truth requires.

## Phase 2 — one local Prompt-01 validation entry point

Create or designate one repository-local, non-mutating command that CI and developers can invoke consistently. Prefer a small Python orchestration script using only the standard library and existing repository dependencies.

The entry point must:

- run from repository root without relying on the caller's CWD after startup;
- locate repository paths deterministically;
- use the current interpreter (`sys.executable`) for all Python subprocesses;
- set `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=.`, and `NDASTRO_USE_SRTM=0` where applicable;
- use unique OS-temporary pytest/snapshot/artifact directories;
- disable pytest cache and repository-configured parallel addopts where necessary for deterministic acceptance;
- propagate the first nonzero failure without retrying in a weaker mode;
- never update snapshots or write tracked/fixed artifacts;
- print bounded, sanitized command/result summaries without absolute user paths, environment dumps, raw chart data, tokens, or exception payloads;
- provide stable named modes if useful, such as `focused` and `full`, while keeping one documented full Stage-01 command authoritative;
- exit nonzero on any failed contract, architecture, determinism, lint, or snapshot gate.

The authoritative full mode must include:

1. import/version smoke;
2. ordered collect-only capture and optional expected-count/hash reporting without hard-coding a stale count as the only correctness rule;
3. WP17 architecture/safety/serialization/determinism tests;
4. complete repository pytest suite;
5. explicit WP17 scenario manifest comparison/repeat;
6. explicit Yoga permutations and loader trigger orders, unless already unequivocally covered by the invoked deterministic gate and documented as such;
7. rule lint with proof that every supported `.yml`/`.yaml` file is inspected exactly once;
8. strict approved-snapshot comparison using a unique temporary `--out` and no update mode;
9. protected-artifact or worktree mutation check scoped so inherited dirty changes are not mistaken for changes caused by validation.

Do not embed WP18's performance benchmark into blocking CI. Performance remains dated descriptive evidence, not a stable threshold.

Add focused tests proving command construction, failure propagation, path safety, no-update behavior, supported modes, and sanitized output. Tests must not recursively execute the entire suite.

## Phase 3 — bounded CI wiring

Update the minimum relevant workflow(s) so Prompt-01 validation is a clear blocking job.

### Python matrix

Use the locked support policy:

- Python 3.11 is the Stage-01 compatibility/baseline lane;
- Python 3.14 is the forward/current lane.

Both lanes must run the authoritative Prompt-01 validation entry point. If hosted CI cannot yet provide the exact patch versions used locally, pin supported minor lanes (`3.11`, `3.14`) and print exact resolved versions. Do not falsely claim patch-identical CI.

### Dependencies

- Use the approved WP00 reproducible Stage-01 dependency source/lock.
- Do not silently fall back to divergent root/Parasara requirement files.
- Do not alter dependency versions in WP19.
- Verify installation commands on the workflow's OS and document any platform-specific handling.

### Failure semantics

- No `|| true`, `continue-on-error`, or parallel-to-serial fallback may suppress a Prompt-01 validation failure.
- A separate optional diagnostic step may run with `if: failure()` only if it cannot change the job result or expose unsafe data.
- Do not auto-update snapshots, create branches/commits/PRs, or stage files in the validation job.
- Do not upload the entire `tests/reports` tree.
- The bounded Prompt-01 job should upload nothing by default. If a small failure artifact is essential, it must be an explicit sanitized allowlist with short documented retention and no raw chart/provider/trace/error payload; otherwise omit uploads.

### Triggers and paths

Ensure the blocking gate runs for relevant pull requests and protected-branch pushes when changes affect:

- Parasara production/tests/rules/fixtures/snapshots;
- Prompt-01 validation tools and dependency lock;
- relevant workflows;
- Stage-01 documentation/completion records.

Avoid a path filter that silently skips an architecture or validation-tool change. Do not redesign unrelated repository triggers.

### Existing automation

Separate advisory report/snapshot-PR automation from the blocking validation path. Do not expand Audit-25's privacy/security scope, but ensure WP19's new/updated validation job does not publish raw report trees or invoke credentialed mutation automation.

Preserve unrelated workflows unless a direct conflict prevents truthful Prompt-01 enforcement. Document retained risks and future owners.

## Phase 4 — implemented architecture documentation

Update the Stage-01 documentation to describe what is actually implemented, not the pre-audit baseline or future universal architecture.

The implemented reference must accurately cover:

- immutable typed predicate status/error/trace/result contracts and exact timing field name;
- logical versus full serialization and telemetry exclusion;
- registry metadata, aliases, versions, schemas, capabilities, bootstrap/freeze/isolation;
- strict parameter normalization and rejection behavior;
- prepared AstroState factual boundary, readiness, defensive freeze, digest composition, and exclusions;
- `PredicateEvaluator`, engine-owned bounded cache, cache key/policy/lifecycle;
- typed leaf/AND/OR/NOT conditions, ordering, short-circuit, skipped children, and active format validation;
- typed Yoga internal batch and unchanged compatibility projection;
- typed Career factual bridge, fixed candidate/denominator/scoring policy, and unchanged public projection;
- retired legacy runtime/raw Boolean/tuple/dictionary adapters;
- deterministic tooling projections and WP17 executable architecture gates;
- safe local/CI validation commands;
- known compatibility adapters and deliberately deferred architecture.

Do not claim implementation of:

- universal `RuleMatch`;
- shared `InferenceEngine`;
- typed universal `DomainPrediction`;
- `OutputAssembler`;
- full DSL/compiler/macros/dependency graph;
- public schema redesign;
- persistent/distributed cache;
- broad concurrency/performance architecture;
- Dasha clock redesign;
- additional domains or astrology-semantic changes.

## Phase 5 — authoring and testing guidance

Update or create the minimum discoverable guidance for maintainers:

### Predicate authoring

Document:

- how to define/register an ID/version/alias;
- parameter schema and capability declarations;
- pure handler inputs/outputs;
- matched/unmatched/non-factual status requirements;
- safe error/evidence/trace conventions;
- prepared-state fact access restrictions;
- cacheability/determinism rules;
- required focused tests and validation command.

### Condition/Yoga/loader guidance

Document active supported condition formats/operators, validation behavior, deterministic source precedence, typed internal retention, and public compatibility boundary. Clearly label future compiler/DSL concepts as not implemented.

### Career guidance

Document the temporary Career-specific factual bridge, canonical occupancy reuse, preserved scoring/confidence/public contract, and prohibition on treating it as the future universal inference layer.

### Testing guide

Replace stale/unsafe commands with the authoritative validation command, focused developer commands, unique-temporary-output rules, no-update snapshot policy, dual-Python expectations, and interpretation of optional skips/telemetry/performance evidence.

Correct the rule-set README's live file inventory and the testing-framework README's claims about determinism, artifact writing, ignore fields, coverage semantics, and current typed projections.

## Phase 6 — status, decisions, completion matrix, and sign-off

Update Stage-01 tracking truthfully:

- Prompt-01 local README: completed audits/WPs, canonical links, final status, and validation entry point;
- implementation status: Prompt-01 implemented/validated with evidence date and remaining non-Prompt blockers;
- roadmap/tasks/gaps: close only completed Prompt-01 items; retain future-stage and release/compliance work with owners/status;
- guardrails: list the new executable/CI enforcement;
- changelog: summarize typed migration, compatibility preservation, legacy retirement, deterministic gates, and CI/docs completion;
- `tests/COMPLETION_MATRIX.md`: add a Prompt-01/typed predicate architecture row with implementation, unit/integration/golden/CI evidence and exact report links; correct unsupported “passing” claims elsewhere only where current WP18 evidence legitimately supports them;
- documentation indexes/TOCs: add/fix canonical links without rewriting historical evidence;
- decision record or locked-decision summary: record the actual implemented decisions from WP00–WP17, with authority and deferred items. Do not fabricate approvals.

Create a concise final Stage-01 completion/sign-off document if no existing canonical document serves this purpose. It must distinguish:

```text
PROMPT_01_IMPLEMENTATION: COMPLETE
PROMPT_01_VALIDATION: COMPLETE
PROMPT_01_CI_GATE: COMPLETE
PROMPT_01_DOCUMENTATION: COMPLETE
RELEASE_READINESS: NOT ASSESSED / BLOCKED BY SEPARATE OWNER WORK
PUBLICATION_APPROVAL: NOT GRANTED
```

Use the disposition supported by current evidence. Audit-25's urgent privacy, raw-output/artifact exposure, licensing/provenance, and public-release findings remain separate owner work. Link/classify them without reproducing sensitive values and without marking Prompt-01 incomplete solely because release readiness is separate.

## Phase 7 — documentation and workflow validation

Add or run bounded checks for:

- workflow YAML syntax and structural assertions for matrix versions, authoritative command, failure propagation, no snapshot update, no report-tree upload, and no credentialed mutation in the blocking job;
- local Markdown links for every changed Stage-01 document;
- referenced commands/files/test paths actually exist;
- no stale links to deleted legacy runtime/engine/predicate modules except explicitly labeled historical records;
- no contradiction between current-state, status, roadmap, tasks, completion matrix, changelog, and final sign-off;
- no claim that WP18 performance is a historical no-regression proof;
- no claim of release/publication/privacy/license approval;
- no raw secret, personal/chart value, absolute home path, or provider payload introduced into changed documentation/CI output.

Do not regenerate a repository-wide TOC with an unsafe or unreviewed generator. If a generated index has one stale relevant link, fix its maintained source or make the smallest reviewed correction and document the method.

## Phase 8 — final CI-equivalent acceptance

After edits, run in both locked local lanes:

1. focused WP19 validation-script/workflow/documentation tests;
2. the authoritative Prompt-01 full validation entry point;
3. ordered collection comparison;
4. full repository suite at least twice per lane using unique temporary directories;
5. WP17 scenario manifest across required seeds/CWDs;
6. rule lint;
7. strict no-update snapshot comparison twice per lane;
8. changed-document link/consistency validation;
9. workflow structural validation;
10. protected-artifact pre/post hash comparison;
11. `git diff --check`.

Record exact commands, exit codes, counts, skips, versions, node-ID hash, manifest hash, snapshot hash, inspected rule files, link counts/results, workflow assertions, and protected-artifact equality.

Do not trigger remote CI, push, commit, open a PR, upload artifacts, or modify branch protection. External required-check configuration is an owner/repository-setting action; document the exact check name that must be marked required, but do not claim it is required unless verifiable repository evidence exists.

## Required WP19 report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP19/WP19.md`

The report must include:

1. `VERDICT: COMPLETE` or `VERDICT: BLOCKED`;
2. `PROMPT_01_COMPLETE: YES` or `PROMPT_01_COMPLETE: NO`;
3. model and reasoning level used;
4. prerequisite and inherited-worktree evidence;
5. reproduced WP18 baseline;
6. before/after CI inventory;
7. authoritative local validation command and exact included gates;
8. workflow matrix/dependency/triggers/failure/mutation/artifact policy;
9. exact check name recommended for branch protection and whether external enforcement was verifiable;
10. changed documentation inventory with reason/classification;
11. implemented architecture/authoring/testing reference summary;
12. decision/deferred-item reconciliation;
13. completion-matrix/status/roadmap/tasks/changelog changes;
14. documentation link/command/consistency validation results;
15. workflow structural validation results;
16. final dual-lane commands, versions, counts, skips, node-ID hash, and repeated-run evidence;
17. determinism, lint, snapshot, Career/Yoga/tooling, and protected-artifact hashes;
18. changed-file inventory separated from inherited changes;
19. explicit production/rule/schema/snapshot/dependency non-change proof;
20. Prompt-01 completion statement;
21. release/publication/privacy/security/licensing non-approval statement and separately owned blockers;
22. future-stage backlog boundaries;
23. explicit proof no WP20/future-stage implementation was started.

## Definition of done

WP19 and Prompt-01 are complete only when:

- WP18 remains complete and reproducible;
- one safe authoritative Prompt-01 validation command exists and is documented;
- CI runs it as a blocking dual-Python matrix with correct dependency source and failure propagation;
- the blocking job cannot update snapshots, mutate git, create PRs, upload raw report trees, or hide failures through fallback;
- workflow triggers cover relevant Prompt-01 code/test/rule/tool/dependency/workflow/documentation changes;
- current architecture, predicate authoring, conditions/Yoga/Career compatibility, and testing commands are accurately documented;
- status, roadmap, tasks, gaps, guardrails, changelog, indexes, and completion matrix are mutually consistent and evidence-backed;
- authoritative/historical reports remain preserved;
- future-stage architecture and urgent release/compliance work remain clearly deferred to their proper owners;
- no release or publication approval is falsely claimed;
- changed documentation links and workflow structural checks pass;
- both local Python lanes pass the authoritative gate and repeated full regression;
- all deterministic, lint, snapshot, public compatibility, and protected-artifact hashes remain exact;
- no production/rule/schema/snapshot/fixture/dependency behavior changed;
- the report records `VERDICT: COMPLETE` and `PROMPT_01_COMPLETE: YES`.

At the end, return a concise summary with verdict, model/reasoning, authoritative command, CI matrix/check name, dual-lane counts/hashes, workflow safety, documentation/completion updates, Prompt-01 completion status, separately deferred release/compliance work, and changed files. **Do not invent WP20 or begin future-stage implementation.**