You are implementing **WP01 — P0 Characterization Fixtures and Tests** for Prompt-01 in the Parasara system.

## Objective

Create a reliable, passing characterization-test safety net for the current valid behavior of:

1. all six registered predicate IDs;
2. the active Yoga evaluation path; and
3. the active Career evaluation and public-output path.

This package records behavior before the predicate-contract migration begins. It must not redesign or fix production behavior.

## Required references

Read these files before making changes:

- `systems/Parasara/Documentation/Engine/Prompt-01/Prompt-01-Locked-Decisions-and-Execution-Plan.md`
- `systems/Parasara/Documentation/Engine/Prompt-01/Reports/Prompt-01-Final-Audit-Consolidation.md`
- all `Audit-01` through `Audit-25` reports in `systems/Parasara/Documentation/Engine/Prompt-01/Reports/`

Pay particular attention to Audits 02, 03, 04, 15, 16, 21, and 22.

If either required Prompt-01 decision/consolidation document has a slightly different repository location, locate it by filename and record the actual path in the completion report.

## Hard preflight gate

WP01 may begin only after WP00 has established separate reproducible Python 3.14 and Python 3.11 environments and recorded a trustworthy baseline matrix. Python 3.14 is the primary development target; Python 3.11 is the compatibility/current-CI baseline.

Before editing:

1. Locate the WP00 completion evidence.
2. Confirm both interpreters and their isolated environments: Python 3.14.x and Python 3.11.x.
3. Confirm required test dependencies import successfully in both environments.
4. Run the WP00 collection and baseline commands for both lanes exactly as recorded.
5. Confirm the working tree state and preserve all unrelated changes.

If WP00 evidence is missing, either interpreter/environment is unavailable, dependencies are unavailable, collection fails unexpectedly, or either lane has unexplained failures, **STOP**. Do not edit files. Report the blocker and the exact commands/results. A documented Python 3.14 dependency incompatibility may proceed only if WP00 explicitly proves it does not affect WP01 test design or any upcoming WP02 architectural choice.

## Absolute scope restrictions

This is a test-only package.

You may add or modify only:

- characterization tests;
- test-local fixtures and test data;
- a WP01 completion report.

Do **not** modify:

- production Python source;
- predicate handlers, registry, evaluator, cache, AstroState, Yoga, or Career implementation;
- astrology rules, YAML/JSON rule data, weights, scoring formulas, or tables;
- public schemas or output serializers;
- approved snapshots or golden files;
- CI workflows or dependency files;
- the existing assertions merely to force a pass.

Never run snapshot update, accept, record, rewrite, or auto-approval commands. Do not create fixed-path temporary artifacts inside the repository.

## Behaviors to characterize

### A. Registered predicate inventory

Confirm the production registry currently exposes exactly these six IDs:

- `ASPECT`
- `ASPECT_EXISTS`
- `PLANET_IN_HOUSE`
- `HOUSE_OCCUPANT`
- `FUNCTIONAL_ROLE`
- `PLANET_EXALTED`

Confirm that `ASPECT` and `ASPECT_EXISTS` currently resolve to the same handler identity. Characterize deterministic enumeration only if the current implementation already guarantees it; otherwise record the observed order without turning incidental import order into a required contract.

For each ID, invoke the existing production path with representative valid prepared input and capture the current return contract and observable outcome. Include at least one current matched and one current unmatched case where the existing implementation can reliably express both.

Do not invent future `PredicateStatus`, `PredicateError`, `PredicateTraceStep`, metadata, schema, capability, or immutable-result expectations in WP01. Those belong to later work packages.

### B. Predicate compatibility matrix

Build a clear test matrix covering, where applicable to current behavior:

- current return type and shape;
- matched/unmatched value;
- predicate ID and any existing identifier fields;
- current input normalization that callers depend on;
- current evidence shape and ordering;
- current empty/error behavior for safe, representative cases;
- repeated evaluation on equivalent prepared input;
- alias equivalence for `ASPECT` and `ASPECT_EXISTS`.

Use semantic assertions. Avoid weak checks such as only `isinstance`, non-empty IDs, `or True`, nonnegative counts, or serialization merely producing a string.

### C. Astrology preservation locks

Do not convert suspected defects into approved semantics.

- `PLANET_EXALTED`: preserve and characterize only enough current behavior to detect accidental migration changes. Clearly label the suspected semantic issue as deferred; do not broaden the test matrix into an authoritative exaltation specification.
- Aspects: preserve the behavior used by the current valid Yoga path. Do not select new graph/list, conjunction, `target=None`, or tradition semantics.
- Functional roles and `HOUSE_LORDS_COMBINATION`: preserve currently effective Career/Yoga results. Do not activate, remove, or reinterpret dormant behavior.

If an expected value cannot be justified as currently valid and stable, do not freeze it. Record it as an unresolved observation in the report.

### D. Active Yoga path

Add characterization coverage for the production path:

`Yoga YAML -> load_yoga_rules -> evaluate_yoga_rules -> evaluate_condition -> evaluate_predicate -> registry handler -> Yoga output`

Using stable existing fixtures, assert:

- the valid rule set used by the fixture;
- which rules fire and do not fire;
- output row membership and order;
- externally consumed keys and value shapes;
- evidence meanings and ordering that current consumers depend on;
- repeatability of logical output after excluding known volatile telemetry or random trace identity;
- registry/global-state isolation between tests.

Do not bless random UUID values as logical identity. Normalize only demonstrably volatile diagnostic identity in a test-local comparison helper, while separately asserting that required fields remain present and well formed.

Do not mutate approved Yoga snapshots or rule files.

### E. Career compatibility path

Using the strongest existing stable fixture and the current full-output golden contract, characterize:

- candidate membership and order;
- exact score and confidence values;
- component membership, values, and order;
- indicator membership, identifiers, values, and order;
- evidence meanings and ordering;
- rounding behavior;
- public dictionary keys, nesting, and value types;
- repeated logical output for the same prepared input.

Reuse approved golden data read-only. Do not regenerate or update it. If the existing full snapshot differs, stop and report the difference rather than accepting it.

### F. Isolation and determinism

All new tests must be hermetic:

- restore predicate and rule registries with `yield`/`finally` fixtures;
- isolate caches and mutable globals between tests;
- do not depend on current working directory;
- use `tmp_path` for any temporary file;
- avoid wall-clock time, random logical identities, filesystem enumeration order, network access, and shared output paths;
- snapshot mutable input/state before and after evaluation where feasible and assert the characterized call does not introduce unexpected cross-test leakage;
- run the new suite at least twice in fresh test processes and compare results.

Do not change production code to achieve isolation. If the existing design makes safe isolation impossible, add the narrowest test-local cleanup possible and record the limitation.

## Suggested test organization

Prefer extending existing relevant tests only when that keeps ownership clear. Otherwise use narrowly named files such as:

- `tests/rules/test_registered_predicates_characterization.py`
- `tests/enrichments/test_yoga_characterization.py`
- `systems/Parasara/tests/test_career_characterization.py`

Avoid creating future-contract test files whose names imply WP02+ functionality.

## Required validation

Run the following first in the Python 3.14 environment and then in the Python 3.11 environment:

1. collection for every new/modified test file;
2. the targeted predicate characterization tests;
3. the targeted Yoga characterization tests;
4. the targeted Career compatibility tests;
5. the complete WP01 characterization group twice in separate fresh processes;
6. the full safe baseline suite recorded by WP00;
7. the approved read-only golden/snapshot comparison command from WP00;
8. a repository status/diff check proving no prohibited file changed.

Use the repository's exact commands discovered during inspection. Disable pytest cache/bytecode or redirect caches outside the repository if WP00 requires this. Do not hide failures using `|| true`, fallback serial execution, broad exclusions, changed tolerances, or weakened assertions.

## Failure policy

If a new characterization test exposes an existing defect or nondeterminism:

1. confirm it in a fresh process;
2. minimize the reproduction;
3. do not fix production code in WP01;
4. do not encode unstable or invalid behavior as a permanent assertion;
5. record the finding and mark WP01 blocked if it prevents a trustworthy baseline.

Any change in Yoga firing/order, Career score/confidence/components/indicators, or approved public output is a hard stop.

## Completion report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/Reports/WP01-P0-Characterization-Fixtures-and-Tests.md`

The report must include:

1. preflight evidence and WP00 reference;
2. files added/modified;
3. predicate matrix with all six IDs and cases covered;
4. Yoga cases and compatibility fields protected;
5. Career cases and compatibility fields protected;
6. isolation/normalization decisions and their justification;
7. exact commands and pass/fail/count results;
8. full baseline and golden comparison results;
9. unresolved observations and deferred semantic issues;
10. prohibited-file diff verification;
11. a requirement-to-test-symbol traceability table;
12. final verdict: `COMPLETE`, `BLOCKED`, or `INCOMPLETE`.

## Definition of done

WP01 is complete only when:

- WP00 preflight and baseline matrix pass under Python 3.14 and Python 3.11, or any permitted 3.14 dependency limitation is explicitly documented and proven non-architectural;
- all six registered IDs have meaningful current-behavior coverage;
- active Yoga firing, ordering, keys, and logical repeatability are protected;
- Career membership, ordering, scoring, confidence, evidence, rounding, and public shape are protected;
- tests are isolated and repeatable in fresh processes;
- the existing safe full baseline still passes;
- approved golden output is unchanged;
- no production, rule, schema, snapshot, CI, or dependency file changed;
- the completion report contains reproducible evidence.

At the end, provide a concise summary containing the verdict, files changed, tests executed with counts, baseline/golden status, and any blockers. Do not proceed to WP02.