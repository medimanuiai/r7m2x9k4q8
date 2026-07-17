# Predicate Authoring Guide

Status: CURRENT-STATE
Owner: Parāśara engine maintainers
Last verified: 2026-07-17

## Registration

Define factual handlers in `systems/Parasara/engine/rules/` and register a
`PredicateDefinition` through the isolated registry/bootstrap path. Each
definition declares a canonical uppercase ID, SemVer version, description,
parameter schema, required capabilities, cacheability, determinism, cost
class, system scope, deprecation metadata, and explicit aliases. `ASPECT` is
the current compatibility alias for `ASPECT_EXISTS`; do not create aliases by
duplicating handlers.

Bootstrap is deterministic and the production registry is frozen after
construction. Tests that need custom definitions must construct an isolated
registry; they must not mutate or rebind the production registry.

## Parameters and capabilities

Use the schemas in `parameters.py`; do not normalize inside a handler. Unknown
keys, material coercion, Boolean-as-integer values, unknown planet names, and
out-of-range houses are rejected. The evaluator supplies canonical parameters
to handlers, result inputs, and cache identity.

Declare every factual dependency through the capability catalog. Read only the
prepared `PreparedAstroState` passed to the handler. A handler must not read raw
Surya input, the caller's mutable `AstroState`, files, environment variables,
the current directory, wall-clock time, network services, or enrichment
engines.

## Handler result rules

Handlers are pure and return immutable `PredicateResult` values:

- factual true uses `matched=True` and status `matched`;
- factual false uses `matched=False` and status `unmatched`;
- missing, unsupported, malformed, or absent facts retain their typed
  non-factual status and must not be reported as `unmatched`;
- invalid parameters are normally rejected before the handler;
- expected failures use bounded `PredicateError` values and safe trace steps;
- raw exceptions, stack traces, chart payloads, and provider diagnostics do
  not belong in evidence, errors, or traces.

Evidence records canonical factual identity, expected value, actual value, and
the comparison or relationship. Trace IDs and ordering are semantic and
deterministic. Use the exact telemetry field `evaluation_time_ms`; it and
`cache_hit` are excluded from logical identity.

Declare `cacheable=True` only when the result is deterministic from prepared
state, canonical parameters, declared capabilities/versions, and explicit
evaluation context. Do not add hidden inputs.

## Required tests

Add focused cases for matched, unmatched, invalid parameters, every relevant
capability/readiness state, evidence/error/trace safety, logical/full
serialization, cold/warm equality, registry isolation, and deterministic
repetition. Then run:

```text
python tools/validate_prompt01.py focused
python tools/validate_prompt01.py full
```

The full command is the authoritative Stage-01 gate. It never approves or
updates a snapshot.
