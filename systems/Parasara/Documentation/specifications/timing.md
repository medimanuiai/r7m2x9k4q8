# Timing Contract

Status: APPROVED  
Authority: Master Architecture Specification  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-07-13

## Scope

Timing enrichments provide deterministic factual contexts for Dasha, transit, and later timing fusion. They do not produce final domain predictions.

Timing facts are enrichment outputs consumed through AstroState and typed evaluation context. Predicates and rules may query those facts; the shared InferenceEngine determines how already-evaluated timing contributions combine with natal and other contexts.

## Requirements

- Evaluation instant and timezone inputs are explicit.
- Missing time inputs never fall back silently to system time in deterministic evaluation.
- Period boundaries and nesting serialize deterministically.
- Timing calculations expose versions, source facts, and trace evidence.
- Dasha and transit contexts enter rules/inference through typed contracts.
- Boundary, leap-year, timezone, golden, and replay tests establish acceptance.
- Period identity, hierarchy, lord, start/end instants, duration, source facts, and calculation version are explicit.
- UTC or another approved canonical timezone is used internally, with conversion policy documented.
- Nested periods remain contained within their parent after rounding and serialization.
- Transit inputs identify ephemeris/source version, observation instant, and applicable normalization.
- Timing caches include the evaluation instant and every factual version that can affect the result.

## Missing and invalid time behavior

Missing birth time, Moon position, evaluation instant, timezone, ephemeris capability, or another required fact must produce an explicit unavailable/invalid result or a documented caller error. It must not silently substitute wall-clock time or convert missing data into an empty factual timeline.

## Determinism and validation

The same canonical state, timing configuration, versions, and evaluation instant must produce the same periods and logical serialization. Acceptance requires transition-boundary cases, parent/child containment, duration reconciliation, timezone conversion, leap-year behavior, deterministic repetition, and trusted golden references.

## Current state

Vimshottari generation exists with nested periods, but it is not fully integrated and can fall back to `datetime.utcnow()`. It reads the current Moon `degree` field as its longitude input, so the intended absolute-longitude contract requires verification. Integer rounding is applied independently to nested durations, and containment/reconciliation behavior requires validation. Transit integration and the approved timing-context boundary are missing.
