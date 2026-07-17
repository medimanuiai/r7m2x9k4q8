# Jyothishyam Testing Framework

This directory contains compatibility and diagnostic helpers used by tests.
Determinism is a property of specific WP17/WP19 scenarios, not a blanket claim
about every helper or engine path.

Current capabilities include constraint-based fixture generation, golden
snapshot regression, JSON comparison with caller-provided ignore
fields/tolerances, rule/data coverage projections, report generation, and
typed Prompt-01 tooling projections.

Historical phase labels in earlier documentation were plans, not completion
claims. Coverage from these helpers means observed rule/data paths, not Python
statement/branch coverage, scientific correctness, or production acceptance.
Performance helpers do not provide an approved no-regression baseline.

## How to run

```text
python tools/validate_prompt01.py focused
python tools/validate_prompt01.py full
```

The full command is the authoritative Stage-01 gate. It redirects pytest,
snapshot, and scenario artifacts to unique OS-temporary directories and checks
that tracked/protected artifacts remain unchanged.

## JSON and snapshot comparison

`json_compare.compare_json()` supports explicit caller-provided ignore fields
and float tolerance. Do not infer that fields are ignored by default without
checking the call. The Prompt-01 gate uses no ignore fields for its final exact
byte comparison and never updates the approved snapshot.

Report/full-artifact helpers write to their configured destination. Never point
ordinary validation at tracked `tests/reports`; use a unique temporary
directory. These outputs may contain raw chart/provider/trace diagnostics and
must not be uploaded wholesale.

## Extending the framework

- Add approved fixtures only through the applicable owner/governance workflow.
- Add TestCase JSON entries consumed by the regression runner.
- Add property strategies only with explicit acceptance criteria.
- Keep generated artifacts detached from typed internal objects and tracked
  paths.

Snapshot equality and tooling determinism are regression evidence only. They do
not grant scientific, privacy, security, licensing, release, or publication
approval.
