# Historical Roadmap (Phases & Milestones)

This file provides a high-level roadmap and milestones derived from `implementation.md`. Use it to track phase-level progress and major deliverables.

## Phases (short)

- Phase 0 — Foundation (schemas, fixtures, CI, ops)
- Phase 1 — Adapter & Normalization (SuryaAdapter, AstroState)
- Phase 2 — AstroState Builder & Enrichments (dignity, shadbala, house state)
- Phase 3 — DSL & Rule Engine (parser, primitives, rule library)
- Phase 4 — Timing Systems (DashaEngine, TransitEngine)
- Phase 5 — Prediction Engines (domain interpreters)
- Phase 6 — Output & Explainability
- Phase 7 — Rule Governance
- Phase 8 — Testing & Calibration (snapshots, backtest)
- Phase 9 — Performance & Scaling
- Phase 10 — Production Operations

## Milestones (examples)

- M1 — Thin vertical slice (Adapter → Normalization → AstroState → Rule Engine → Inference → Career Interpreter → Output + Explainability)
 	- Notes: include explainability traces from Day 1 so interpretability is baked into every prediction.

- M2 — Snapshot harness + golden charts + CI regression
 	- Notes: golden charts are the permanent regression suite; CI must fail on snapshot drift without approved updates.

- M3 — Backtesting framework + calibration metrics
 	- Notes: support multiple datasets and emit calibration reports for rule tuning.

- M4 — Rule governance MVP (promotion, rollback, audit logging)
 	- Notes: provide safe promotion/rollback workflows and an immutable audit trail for SME reviews.

- M5 — Advanced Vargas (D10, D7, D2)
 	- Notes: deterministic mapping and consistency checks for additional vargas.

- M6 — Advanced Timing (transit strength, transit dignity, transit vargas)
 	- Notes: integrate transit-based scoring into timing fusion.

- M7 — Advanced Yogas (Lakshmi, Vipareeta, Neechabhanga variants, rare yogas)
 	- Notes: catalog detection rules and explanations for rare and compound yogas.

- M8 — Calibration (historical datasets, SME tuning, rule optimization)
 	- Notes: backtest pipelines, automated tuning, and SME feedback loops.

- M9 — Production Readiness (monitoring, distributed cache, profiling, privacy, API versioning)
 	- Notes: infra hardening, performance baseline, and privacy controls for deployment.

Update this file with estimated dates and owners when planning sprints or releases.
