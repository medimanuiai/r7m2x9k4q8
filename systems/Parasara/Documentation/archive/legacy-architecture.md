# Historical Architecture Overview

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
	- Note: `AstroState` models Lagna explicitly via `lagna_sign` and `lagna_degree`. The normalizer will prefer `chart.lagna` and also capture any Ascendant node provided by upstream (but will not keep an `Ascendant` planet node in `planets`). House numbering is normalized to be lagna-relative for whole-sign systems.
	- DerivedState & validation: the engine produces a consolidated `derived` bundle validated by Pydantic models in `systems/Parasara/engine/derived/models.py`. The `derived` bundle contains typed `PlanetStrength` and `HouseSummary` entries which the rule runtime and interpreters consume to avoid repeated recalculation.
	- Functional-role tables: SME-tuned overrides are stored under `systems/Parasara/enrichment_tables/functional_roles/` and are consulted by the functional role enrichment step; this makes functional role mapping data-driven and lagna-specific.
- `DashaContext` / `TransitContext` — timing contexts used by inference.
- `RuleMatch` — structured evidence produced by rule evaluation.
- `DomainPrediction` — per-domain output structure including score, confidence, components.

## Files and locations

- Implementation & plan (index): `implementation.md` (keep as canonical index/status).
- Architecture details: this file `architecture.md`.
- Tasks and roadmap: `roadmap.md`, `tasks.md`.
- Guides: `guides/vertical-slice.md` and others.

Maintain stable model definitions here and reference them from code via file path links.
