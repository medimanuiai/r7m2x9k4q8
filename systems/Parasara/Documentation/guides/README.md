# Parāśara Engine Guides

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-17

## Purpose

Guides describe reproducible developer workflows. They do not define architecture contracts or prove that commands currently pass.

| Guide | Purpose |
|---|---|
| [Testing](testing.md) | Test layers, safe command boundaries, CI behavior, and mutating tools |
| [M1 Vertical Slice](vertical-slice.md) | Current fixture-to-Career snapshot compatibility path |
| [Predicate Authoring](predicate-authoring.md) | Registration, parameter/capability, result, safety, cache, and test requirements |
| [Conditions, Yoga, Loaders, and Career](conditions-yoga-career.md) | Active formats, deterministic loading, and typed compatibility boundaries |

## Command classifications

- `read-only inspection`: searches and file reads that do not execute project code or write artifacts.
- `test execution`: runs project code and may write temporary files, bytecode, coverage, or pytest cache.
- `mutating workflow`: intentionally writes fixtures, snapshots, reports, approvals, or repository files.
- `environment-changing workflow`: installs packages or modifies the configured development environment.

Every guide must label commands whose effects exceed read-only inspection.
