# Predicate and PredicateResult Contract

Status: APPROVED  
Authority: Master Architecture Specification and Prompt-01  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-07-13

## Predicate responsibility

A predicate answers one factual question from AstroState, canonical parameters, and explicit evaluation context. It must not score, assign rule weight or confidence, resolve conflicts, narrate, mutate state, or construct public output.

Predicates must consume normalized AstroState facts only. They must not read raw Surya input, adapter internals, external services, system time, files, or mutable shared configuration during evaluation.

## PredicateResult

Every active registered predicate must return one typed, immutable result containing the approved logical identity, normalized inputs, structured evidence, ordered trace information, structured errors, cache information, evaluation status, and predicate version.

Missing capability is distinct from factual nonmatch. Invalid parameters and expected evaluation failures must be represented through approved structured status/error semantics.

The logical contract includes:

- non-null factual `matched` state;
- canonical `predicate_id` and explicit `predicate_version`;
- immutable canonical inputs;
- immutable structured evidence;
- ordered typed trace steps;
- ordered typed errors;
- explicit evaluation status;
- cache-hit and optional performance metadata that do not alter logical meaning.

PredicateResult must not contain rule weight, adjusted contribution, domain score, confidence, priority, or narrative.

## Status and errors

At minimum, the contract must distinguish matched, unmatched, invalid parameters, missing capability, evaluation error, skipped, and any explicitly supported timeout state. Status and `matched` must not contradict each other.

Expected factual/data errors use stable error codes, safe messages, predicate identity, immutable details, and recoverability metadata. Public results must not expose raw stack traces. Strict development modes must not hide unexpected programming defects behind universal exception conversion.

## Parameters and evidence

- Every registration supplies a parameter schema.
- Required, unknown, mistyped, and unsupported parameters are validated explicitly.
- Canonical normalization is deterministic and does not silently coerce materially invalid values.
- Evidence remains factual, machine-readable, JSON-safe, and sufficient to audit the result.
- Stable AstroState node or relationship identifiers are included where available.
- Empty evidence, traces, and errors serialize as empty collections rather than null.

## Registry

Registrations must validate predicate identity, version, description, parameter schema, required capabilities, cacheability, determinism, cost class, system scope, and deprecation/replacement metadata. Duplicate and alias behavior must be explicit and deterministic.

The registry must reject blank identity, missing/invalid version, invalid metadata, and non-callable handlers. Incompatible duplicate registration must fail rather than depend on import order. Alias identity, normalization, case sensitivity, enumeration order, initialization, test registration, and test cleanup must be explicit contracts.

## Cache

Cache identity must include the AstroState digest, predicate identity and version, canonical parameters, and relevant evaluation/configuration/enrichment versions. A cache hit must not mutate the stored logical result.

Only predicates declared deterministic and cacheable may be cached. Cold and warm results must have identical logical content after excluding approved performance/cache-observation fields. Cache storage must not expose mutable nested references or permit cross-version, cross-system, cross-context, or changed-state contamination.

## Serialization and determinism

One canonical serializer must provide stable field order, enum values, numeric representation, datetime formatting, nested normalization, and JSON-safe output. Repeated logical evaluation and serialization must be equivalent for the same state, predicate, parameters, and context.

## Migration constraint

Prompt-01 must preserve compliant existing behavior and astrological semantics. Stage-required audits determine alias compatibility, active predicate scope, legacy return contracts, callers, supporting models, parameter validation, and rule-directory ownership before migration decisions are implemented.

The present model and registry in `engine/rules/engine.py` are partial compatibility implementations: nested collections are mutable, required identity/status/error metadata is incomplete, tuple compatibility remains, registration validation is minimal, and cache identity uses process-local object identity.
