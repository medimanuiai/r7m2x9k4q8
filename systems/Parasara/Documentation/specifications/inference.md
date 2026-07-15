# Inference Contract

Status: APPROVED  
Authority: Master Architecture Specification  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-07-13

## Responsibility

Exactly one shared InferenceEngine combines universal RuleMatch objects into a typed InferenceResult.

It owns:

- contribution calculation;
- context and priority multipliers;
- positive, negative, neutral, and mixed aggregation;
- deterministic conflict resolution;
- score normalization;
- confidence calculation separate from score;
- contribution and conflict explainability.

It consumes universal RuleMatch objects, explicit timing context, data-completeness information, and versioned inference configuration. It does not call predicates or reinterpret rule condition trees.

## Boundaries

The InferenceEngine must not inspect raw Surya JSON, recompute enrichments, evaluate YAML conditions, generate final narrative, or mutate AstroState.

Predicates supply facts. Rules supply semantic meaning and base weights. The shared InferenceEngine supplies combination policy. Domain interpreters present domain-specific results.

Confidence must be calculated separately from score. At minimum it reflects evidence strength, rule quality, data completeness, cross-context agreement, and the number or independence of contributing rules. Lack of evidence must not silently appear as neutral high confidence.

Conflicting supportive and adverse contributions remain visible. Tie-breaking and collapse behavior must be deterministic, configurable, versioned, and included in explanation factors.

## Configuration

Formulas, coefficients, multipliers, normalization, confidence policy, and tie-breakers must be versioned, deterministic, testable, and traceable. They must not be silently embedded in domain interpreters.

The public normalized score and confidence ranges are `0.0` through `1.0`. The baseline meaning of a neutral score, no-match behavior, insufficient-data behavior, clipping, and normalization strategy must be explicit. Silent clipping is prohibited.

## InferenceResult

One immutable typed result must include domain, evaluation status, raw and normalized scores, confidence, positive/negative/neutral contributions, components, conflicts, agreement, data completeness, explanation factors, deterministic trace identity, and inference/configuration version.

Every contribution preserves its originating rule ID/version, sign, context, base weight, quality, evidence strength, applied multipliers, final contribution, evidence, and trace link.

## Determinism and errors

Input RuleMatches are processed in canonical order. No random identity, system time, mutable global state, or unordered traversal may affect logical output. Invalid configuration and incompatible matches fail explicitly; missing data follows the typed result policy rather than being silently fabricated.

## Current state

No shared InferenceEngine exists. Career-local scoring and confidence are prototype compatibility behavior, not this contract's implementation.
