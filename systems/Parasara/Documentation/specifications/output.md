# Domain and Output Contract

Status: APPROVED  
Authority: Master Architecture Specification  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-07-17

## Domain interpreters

Each domain interpreter selects a versioned rule pack, requests generic rule evaluation, passes universal RuleMatches to the shared InferenceEngine, and adds evidence-backed domain labels or narrative.

Interpreters must not calculate generic scores or confidence, resolve conflicts, recompute enrichments, read raw Surya data, or assemble public JSON.

All domains return the same typed DomainPrediction family with explicit evaluated, unavailable, insufficient-data, and error behavior.

Domain-specific logic is limited to rule-pack selection, domain labels/components, and evidence-backed narrative policy. A domain must not introduce facts or claims absent from evaluated evidence.

The typed output family must cover domain indicators/components, conflicts, narrative sections, Yoga diagnostics, Dasha timelines, transit summaries, and other approved domain-neutral structures without reverting to arbitrary dictionaries.

## OutputAssembler

The OutputAssembler is the sole public serializer. It performs no astrology, scoring, confidence calculation, or narrative inference. Output includes engine, rule-set, predicate/configuration, schema, and evaluation-context versions required for replay.

Serialization must be deterministic and JSON-safe, with stable enum/datetime/numeric representation and explicit empty-collection policy. Performance-only metadata and timestamps must be excluded or normalized in deterministic snapshots according to the schema contract.

The assembler validates the public schema and preserves typed status/error distinctions. It must not repair invalid internal results by inventing values or silently dropping required evidence.

## Explainability

Every public conclusion must retain traceable rule contributions and factual evidence. Narrative may summarize evidence but must not introduce unsupported assertions.

Public output must make it possible to trace a domain conclusion through inference contributions and RuleMatches to PredicateResults and the relevant AstroState facts and versions. Sensitive raw input and internal exception details must not leak merely for explainability.

## Compatibility and versioning

Public schema versioning is separate from internal model versioning. Backward compatibility, intentional breaking changes, serializer adapters, snapshot changes, and deprecation periods must be explicit. Internal contract migrations must not broadly rewrite public snapshots when the public schema is intended to remain stable.

## Current state

Career now retains a typed internal prepared-facts/evaluation batch for its
factual bridge, then deliberately projects to the unchanged public dictionary.
It still owns local candidate selection, scoring/confidence, narrative, and
component assembly. That bridge is temporary and must not be described as the
future universal inference/output architecture.

The snapshot tool still assembles public dictionaries directly. Wealth is a
placeholder; Dasha, transits, and top-level explainability sections are empty
or skeletal. Universal RuleMatch, shared InferenceEngine, typed universal
DomainPrediction, public schema redesign, and a schema-validating
OutputAssembler are not implemented.
