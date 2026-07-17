# Predicate and PredicateResult Contract

Status: APPROVED  
Authority: Master Architecture Specification and Prompt-01  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-07-17

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

## Implemented Stage-01 boundary

Prompt-01 now implements the contract in `engine/rules/models.py`,
`canonical.py`, `registry.py`, `parameters.py`, `capabilities.py`,
`prepared_state.py`, `evaluator.py`, and `conditions.py`. All ten
`PredicateResult` fields are present: `matched`, `predicate_id`,
`predicate_version`, `inputs`, `evidence`, `trace_steps`, `errors`,
`cache_hit`, `evaluation_time_ms`, and `status`.

Logical and full serialization are distinct; telemetry is excluded from
logical identity. Registry bootstrap/freeze/isolation, strict normalization,
prepared-state readiness/digest, engine-owned bounded cache policy, typed
conditions, and deterministic serialization are executable contracts.
`ASPECT` remains the explicit compatibility alias for `ASPECT_EXISTS`.

See [Predicate Authoring](../guides/predicate-authoring.md) for the active
registration, safety, evidence, cache, and test workflow.

Universal RuleMatch, shared inference, public schema redesign, persistent or
distributed caching, broad concurrency, and a full DSL/compiler remain outside
this implemented boundary.
