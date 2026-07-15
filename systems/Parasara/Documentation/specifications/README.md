# Parāśara Engine Specifications

Status: APPROVED  
Authority: Jyothishyam Master Architecture Specification and approved stage prompts  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-07-13

## Purpose

These documents separate focused contracts from the mixed archived specification at `../archive/legacy-basic-specs.md`. They summarize approved requirements and explicitly identify current compatibility boundaries. The Master Architecture and approved stage prompts remain controlling.

Specifications define required target contracts. They do not assert that the current implementation satisfies those contracts. Each specification must keep approved requirements separate from its current compatibility boundary.

| Contract | Document |
|---|---|
| AstroState | [AstroState](astrostate.md) |
| Predicates and PredicateResult | [Predicates](predicates.md) |
| Rules and RuleMatch | [Rules](rules.md) |
| Inference | [Inference](inference.md) |
| Timing | [Timing](timing.md) |
| Domain and public output | [Output](output.md) |

Specifications describe required contracts. Implementation maturity is recorded in `../implementation/status.md`.

## Dependency order

The contracts should be read in runtime dependency order:

1. AstroState establishes the factual evaluation snapshot.
2. Predicates query that snapshot and produce PredicateResult.
3. Rules preserve PredicateResults and produce universal RuleMatch.
4. Timing supplies explicit factual evaluation contexts.
5. Inference combines RuleMatches through one shared policy.
6. Domain interpreters and the OutputAssembler produce typed domain and public output.

Stage-specific prompts may refine one contract without authorizing redesign of later layers.

## Contract conventions

- Required behavior uses normative language such as `must` and `must not`.
- Current implementation behavior is labeled explicitly and is not approval of a deviation.
- Missing data, missing capability, factual nonmatch, validation failure, and programming error remain distinguishable.
- Every output-affecting version and evaluation input must be available for deterministic replay.
- Public and internal collection ordering must be deterministic where order affects serialization, tracing, caching, or evaluation.
