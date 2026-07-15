# WP00 — Dual-Python Decision Record and Reproducible Baseline

Copy the complete prompt below into GitHub Copilot.

---

You are implementing **WP00 — Decision Record and Reproducible Python Baseline Matrix** for Prompt-01 in the Parasara system.

## Objective

Prepare the repository for safe Prompt-01 implementation without changing production behavior.

Establish:

- **Python 3.14.x** as the primary development and forward-compatibility target;
- **Python 3.11.x** as the compatibility and current-CI baseline;
- separate reproducible virtual environments for both versions;
- one shared, repository-owned dependency source;
- trustworthy collection, test, rule-lint, and read-only snapshot baseline evidence for both lanes.

This package is environment, evidence, and documentation work. It must not implement Prompt-01 production architecture.

## Required references

Read before editing:

- `systems/Parasara/Documentation/Engine/Prompt-01/Prompt-01-Locked-Decisions-and-Execution-Plan.md`
- `systems/Parasara/Documentation/Engine/Prompt-01/Reports/Prompt-01-Final-Audit-Consolidation.md`
- all `Audit-01` through `Audit-25` reports under `systems/Parasara/Documentation/Engine/Prompt-01/Reports/`

Pay particular attention to Audits 21, 22, and 23. Locate documents by filename if paths differ and record actual paths.

## Runtime policy

Use the newest stable patch releases available in these minor lines:

- Python 3.14.x — primary target;
- Python 3.11.x — compatibility/current-CI baseline.

Do not hard-code a patch number in project policy unless tooling requires it. Record the exact installed patch versions in the completion report.

Create separate environments with unambiguous names, such as `.venv-py314` and `.venv-py311`, using the repository's established environment convention if one exists. Ensure both are ignored by Git. Never reuse packages across the environments.

If an interpreter is not installed, report the exact safe installation command appropriate to the developer's operating system and package manager. Do not silently choose system-wide locations or replace an existing default interpreter. After installation, verify executable path and version.

## Dependency policy

1. Discover the repository's authoritative runtime and development dependency declarations.
2. Install both environments from the same source declarations.
3. Include all existing runtime dependencies, pytest, PyYAML, Pydantic, required pytest plugins, snapshot tooling, rule-lint tooling, and any existing test requirements.
4. Prefer existing pinned/locked declarations.
5. Do not opportunistically upgrade, downgrade, or broadly re-resolve dependencies.
6. Do not add compatibility pins merely to make Python 3.14 appear green without investigating and documenting the constraint.
7. Record resolved package versions separately for both environments without committing machine-specific environment exports unless the repository already requires them.

If existing declarations cannot install on Python 3.14, classify each failure as:

- `PROJECT_INCOMPATIBILITY`;
- `DEPENDENCY_INCOMPATIBILITY`;
- `TOOLING_INCOMPATIBILITY`; or
- `ENVIRONMENT_ERROR`.

Identify the exact package, constraint, command, and error. Determine whether it affects core runtime architecture, tests only, or optional tooling. Do not fix production code in WP00.

## Permitted changes

You may modify only what is necessary for a reproducible baseline:

- Prompt-01 decision/baseline documentation;
- narrowly scoped environment bootstrap documentation or scripts, if the repository already uses them;
- dependency declarations or locks only when necessary to accurately express already-intended compatibility and only after proving the change is not an opportunistic upgrade;
- `.gitignore` entries for local environments/caches;
- the WP00 completion report.

Before changing any dependency or bootstrap file, explain why documentation alone is insufficient and show the minimal diff.

## Prohibited changes

Do not modify:

- production Python behavior;
- predicate handlers, registry, evaluator, cache, AstroState, Yoga, Career, or domain implementation;
- astrology rules, YAML/JSON rule data, weights, formulas, or tables;
- tests or assertions to make failures disappear;
- approved snapshots, golden files, or public schemas;
- CI workflow behavior in WP00, except documenting a proposed WP19 matrix;
- generated artifacts tracked by the repository.

Never run snapshot update, accept, record, rewrite, or auto-approval commands. Never use `|| true`, fallback commands, broad exclusions, or changed tolerances to hide failure.

## Phase 1 — Repository and safety inspection

Before installation or edits:

1. Record operating system, architecture, shell, Git branch, and working-tree state.
2. Preserve all unrelated user changes.
3. Inventory Python executables and launchers already available.
4. Inventory dependency files, locks, Python-version constraints, test configuration, CI workflows, lint commands, snapshot commands, and artifact-writing utilities.
5. Identify the exact current CI Python version and commands.
6. Identify commands that mutate snapshots, fixed repository paths, reports, or generated outputs and mark them unsafe.
7. Determine safe cache locations outside tracked source paths.

Do not assume command names. Derive them from repository files and record the evidence.

## Phase 2 — Create isolated environments

For Python 3.14 and Python 3.11 independently:

1. Verify interpreter path and exact version.
2. Create the isolated environment.
3. Upgrade only environment bootstrap packaging tools if required by the documented repository process; record any such change.
4. Install from the authoritative repository dependency source.
5. Verify imports for core runtime and test dependencies.
6. Record resolved versions of Python, pip/build tooling, pytest, PyYAML, Pydantic, plugins, and other relevant packages.
7. Prove the environment does not import packages from the other environment or an unintended user/global site.

Use platform-appropriate commands. Do not activate one environment and accidentally execute the other interpreter; prefer explicit environment executable paths in recorded commands.

## Phase 3 — Safe baseline matrix

Run the same logical validation in both environments, with Python 3.14 first and Python 3.11 second:

1. dependency/import smoke test;
2. pytest collection only;
3. targeted existing predicate-contract tests;
4. targeted existing Yoga tests;
5. targeted existing Career tests;
6. full safe baseline suite using the repository's discovery rules;
7. rule lint/validation;
8. approved snapshot/golden comparison in strict no-update mode with output redirected to `tmp_path` or an OS temporary directory;
9. a second fresh-process run of deterministic/sensitive baseline tests where safe;
10. repository status check after every command capable of writing files.

Prevent bytecode, pytest cache, reports, and temporary output from polluting tracked paths where practical. Do not delete pre-existing user artifacts.

For every command record:

- environment/version;
- exact command;
- exit code;
- collected/passed/failed/skipped/xfail counts where applicable;
- duration if available;
- files created or changed;
- whether the result is trustworthy.

## Failure policy

### Python 3.11

Any unexplained install, collection, baseline, lint, or golden comparison failure is a WP00 blocker because 3.11 is the current CI compatibility contract.

### Python 3.14

Investigate and classify every failure. A 3.14 failure is a blocker before WP02 if it affects:

- a core runtime dependency;
- language behavior relevant to immutable models, serialization, hashing, enums, typing, dataclasses, concurrency, or caching;
- production importability;
- the design of any WP02+ component.

A failure limited to optional tooling may be documented as a temporary compatibility gap only when the 3.11 lane passes, the limitation does not weaken WP01 characterization, and there is a named remediation owner/work package. Do not call the 3.14 lane passing when such a gap exists.

For all failures:

1. reproduce in a fresh process;
2. capture a concise error without exposing secrets or personal data;
3. identify whether it existed before any WP00 edit;
4. do not alter production behavior or approved output;
5. stop if continuing would make the baseline misleading.

## Decision record

Ensure the repository records these decisions:

- Python 3.14 is the primary target for new Prompt-01 code.
- Python 3.11 remains supported and is the current CI baseline.
- all new code must run on both versions and must not introduce version-specific logical differences;
- dependency declarations are shared; environments and resolved evidence are separate;
- WP01 validation runs in both lanes;
- WP02 cannot begin with unresolved architecture-relevant Python 3.14 incompatibilities;
- WP19 must add/enforce the final CI version matrix after the complete suite is proven.

Do not change the CI workflow in this package unless separately authorized.

## Completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/WP00-Dual-Python-Decision-and-Baseline.md`

Include:

1. executive verdict: `COMPLETE`, `BLOCKED`, or `INCOMPLETE`;
2. repository/OS inspection summary;
3. authoritative dependency sources;
4. exact interpreter paths and versions;
5. environment creation/install commands;
6. relevant resolved dependency versions for both lanes;
7. import-smoke matrix;
8. collection/test/lint/golden matrix with exact commands and counts;
9. failure classifications and minimal reproductions;
10. architecture impact assessment for every Python 3.14 gap;
11. files added/modified and justification;
12. proof that production/rules/tests/snapshots/public schemas were unchanged;
13. working-tree status before and after;
14. safe commands WP01 must reuse;
15. explicit readiness verdict for WP01 and WP02.

## Definition of done

WP00 is complete only when:

- both interpreters and isolated environments exist and are verified;
- dependency installation is reproducible from shared repository declarations;
- Python 3.11 collection, baseline, lint, and no-update golden validation pass or any pre-existing failure is fully characterized and formally blocks continuation;
- Python 3.14 results are complete and every incompatibility is classified;
- no unresolved Python 3.14 issue can influence WP02 architecture;
- no production behavior, rule, test assertion, approved snapshot, golden file, or public schema changed;
- commands are safe, reproducible, and recorded for WP01;
- the completion report contains evidence sufficient for another developer to reproduce both lanes.

At the end, return a concise summary with the verdict, exact Python versions, environment names, test results for both lanes, files changed, compatibility gaps, and whether WP01 may begin. Do not proceed to WP01.
