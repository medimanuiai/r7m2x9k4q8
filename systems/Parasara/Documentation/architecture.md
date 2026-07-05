# Architecture Overview

This document contains a concise architecture summary for the Parāśara engine. It is intended for engineers and SMEs who need a system-level view and stable references for core data models and reference knowledge.

## System components ( high level )

- Adapter — Surya JSON validation and parsing (`SuryaAdapter`).
- NormalizationEngine — canonicalization, degree normalization, enrichment hooks.
- AstroState — typed graph: `Chart`, `AstroState`, `PlanetNode`, `HouseNode`, `VargaNode`.
- Rule Engine — DSL parser / primitive predicate evaluator / execution plan.
- Rule Library — data files containing rules (house rules, yogas, domain rules).
- Inference Engine — timing fusion, conflict resolver, confidence model, score aggregator.
- Prediction Interpreters — per-domain interpreters (career, wealth, marriage, ...).
- Output Layer — assembler, explainability traces, output JSON schema.
- Reference Knowledge — signs, nakshatras, friendship and exaltation tables, vimshottari table.

## Core Data Models

- `Chart` — input canonical model (metadata, planets, houses, lagna).
- `AstroState` — normalized, enriched graph used by rule evaluation.
- `DashaContext` / `TransitContext` — timing contexts used by inference.
- `RuleMatch` — structured evidence produced by rule evaluation.
- `DomainPrediction` — per-domain output structure including score, confidence, components.

## Files and locations

- Implementation & plan (index): `implementation.md` (keep as canonical index/status).
- Architecture details: this file `architecture.md`.
- Tasks and roadmap: `roadmap.md`, `tasks.md`.
- Guides: `guides/vertical-slice.md` and others.

Maintain stable model definitions here and reference them from code via file path links.
