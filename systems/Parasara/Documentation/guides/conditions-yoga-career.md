# Conditions, Yoga, Loaders, and Career Guide

Status: CURRENT-STATE
Owner: Parāśara engine maintainers
Last verified: 2026-08-14

## Active condition format

The active format is a mapping with `type`. A leaf uses a registered predicate
type plus `params`. Logical nodes use `AND`, `OR`, or `NOT` plus `children`.
`AND` and `OR` require at least one child; `NOT` requires exactly one. Unknown
operators, unknown predicates, malformed parameters, and invalid arity are
definition errors.

`ConditionEvaluator` evaluates left to right. `AND` stops at the first
decisive nonmatch and `OR` at the first match; `NOT` reverses its one child's
factual result. Evaluated children retain typed results, evidence, errors, and
traces. Unevaluated children are explicit skipped child records. Non-factual
statuses are not collapsed into false.

The loader validates the formats actually used by active Yoga files.
Deterministic source precedence is explicit, supported `.yml` and `.yaml`
files are enumerated canonically, and loader order must preserve the global
rule-registry object identity. A general compiler, macro expander, dependency
graph, and full DSL are future architecture and are not implemented.

## Yoga compatibility

Yoga preparation freezes one prepared factual state. One evaluator produces a
typed `YogaEvaluationBatch` whose records each contain one universal
`RuleMatch`; `project_yoga_compatibility` is the named one-way
adapter to the unchanged externally consumed list/dictionary shape. Rule
firing, row ordering, weights, public keys, and compatibility state attachment
remain preserved. Do not reintroduce the retired raw-Boolean or tuple helpers.

The WP17 manifest executes the five required rule permutations and both
generic/Yoga loader trigger orders. The authoritative validation command runs
that manifest explicitly.

## Career compatibility

Career uses a Career-specific factual bridge around the universal RuleMatch:
`prepare_career_facts`, `evaluate_career_batch`, then the existing public
projection. It reuses canonical occupancy facts and preserves candidate order,
the fixed denominator/contribution policy, scores, confidence, components,
indicators, evidence meaning, rounding, narrative, and public dictionary
shape.

Each candidate wrapper contains one universal `RuleMatch`. Existing adjusted
score/contribution fields remain only in the compatibility wrapper and public
projection; they are not RuleMatch fields. Shared `InferenceEngine`, typed
universal `DomainPrediction`, and any authorization to copy Career scoring
into another domain remain separately staged work.

Both typed batches expose canonical RuleMatch collection order. Their public
adapters deliberately preserve the prior source/catalog order and schemas.

## Validation

Use `python tools/validate_prompt02.py focused` while editing Prompt-02. Before
review, run `python tools/validate_prompt02.py full` under both supported Python
lanes. The historical Prompt-01 validator remains frozen to its completed
baseline.
Generated artifacts and snapshot output must remain in unique OS-temporary
directories; snapshot update/approval commands are outside this workflow.
