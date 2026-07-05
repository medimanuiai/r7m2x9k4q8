# Parāśara Engine — Implementation & Status

This single living document combines the implementation plan, current status, implemented artifacts, and open implementation issues. Use this as the canonical source for what we will implement and what is implemented.

Date: 2026-07-04

---

## Prerequisites (must be completed before Phase work)

- Developer environment: ensure Python 3.11+ and `pip` available; CI matrix documents Python versions tested.  
  
  Purpose: ensure developers and CI run the same Python runtime and tooling so builds and tests are reproducible.

  Acceptance: `python -m pip --version` and `python --version` succeed in CI.

- Dependencies: add core dev dependencies in `systems/Parasara/requirements.txt`: include `jsonschema`, `pydantic`, `pytest`, `hypothesis`.  
  
  Purpose: provide validation, typing and testing toolchain required for schema checks and unit/property tests.
  
  Acceptance: `python -m pip install -r systems/Parasara/requirements.txt` completes in dev environment.

- Schema validation: validate `fixtures/golden_chart_01.json` against `schemas/surya_input.schema.json` and fix schema gaps.  
  
  Purpose: catch structural mismatches early so engine code consumes well-formed inputs.
  
  Acceptance: sample fixture validates with `jsonschema`.

- Licensing audit: run dependency license scanner and record results in `systems/Parasara/Documentation/licensing-audit.md`.  
  
  Purpose: detect incompatible licenses (AGPL/GPL) and capture mitigations before production use.
  
  Acceptance: no AGPL dependencies flagged; if flagged, document mitigation.

- CI and snapshot harness basics: add `Makefile` targets `lint`, `test`, `validate-schemas`, `snapshot`; configure CI to run `make test`.  
  
  Purpose: provide reproducible developer commands and enforce automated checks for PRs.
  
  Acceptance: CI pipeline runs `make test` and `make validate-schemas` on PRs.

- Golden fixtures & snapshots: author `fixtures/golden_chart_01.json` and expected output snapshot.  
  
  Purpose: provide a known-good input/output pair used to detect regressions during development.
  
  Acceptance: snapshot present in `systems/Parasara/tests/snapshots/` and CI compares it.

- Rule-set seed: ensure `rules/parashara/v1` contains starter `macros.yaml`, `yogas.yaml`, and `calibration.json`.  
  
  Purpose: provide an initial, versioned rule folder so rule loader and governance plumbing can be exercised early.
  
  Acceptance: rule loader accepts v1 directory (even if empty rules) and logs `v1` available.

- Data retention & secrets policy: document storage encryption and secret handling in `systems/Parasara/Documentation/ops.md`.  
  
  Purpose: ensure compliance for sensitive birth data and enforce secure secret handling before production deployments.
  
  Acceptance: ops checklist present and referenced in onboarding docs.

- Historical dataset collection: acquire a labeled, consented dataset suitable for backtesting and calibration.
  
  Purpose: provide ground-truth cases for backtesting, calibration of scoring formulas, regression tests, and supervised model training.
  
  Acceptance: dataset schema and labeling spec approved by SME; pilot dataset (50–200 anonymized charts) ingested and validated; Legal/Privacy sign-off obtained before collecting larger datasets.


---

## Status Legend

- 🟩 Completed
- 🟧 In Progress / Partial
- 🟥 Not Started / Not Completed


### Prerequisite task status

| Task | Status |
|---|---:|
| Phase 0 — Foundation | 🟩 Completed |
| Rule-set seed (`rules/parashara/v1`) | 🟩 Completed |
| Developer environment verification | 🟩 Completed (local virtual environment `jyothishyam_env` activated) |
| Dependencies in `systems/Parasara/requirements.txt` | 🟩 Completed (installed into `jyothishyam_env`) |
| Schema validation (`fixtures/golden_chart_01.json` vs `schemas/surya_input.schema.json`) | 🟩 Completed (validation OK) |
| Licensing audit (`pip-licenses`) | 🟩 Completed (`systems/Parasara/Documentation/licenses.json` created) |
| CI wiring / `Makefile` targets (`validate-schemas`, `test`) | 🟩 Completed (Makefile + CI workflow added) |
| Golden fixtures (`fixtures/golden_chart_01.json`, expected output) | 🟩 Completed (fixture + approved expected output present) |
| Snapshot harness (`systems/Parasara/tests/snapshots/`) | 🟩 Completed (seeded snapshot added) |
| Data retention & secrets policy (`systems/Parasara/Documentation/ops.md`) | 🟩 Completed (ops checklist created) |
| Historical dataset collection (backtesting) | 🟥 Not Completed |

---

## Actionable subtasks (TODOs)

The following concrete subtasks convert the `Partial` and `Not Completed` prerequisites into runnable actions. Tasks completed by the assistant are checked; I'll update this file after completing future tasks.

- [x] Developer environment verification
  - Goal: Confirm dev machines and CI run Python 3.11+ and have `pip` available.
  - How to run: `python --version` and `python -m pip --version` on each developer machine and in CI.

- [x] Install dependencies for `systems/Parasara`
  - Goal: Install validation and test toolchain into CI and dev environments.
  - Command: `python -m pip install -r systems/Parasara/requirements.txt`
  - Acceptance: command exits 0 and `jsonschema` is importable.

- [x] Run schema validation (fixtures)
  - Goal: Validate `systems/Parasara/fixtures/golden_chart_01.json` against `systems/Parasara/schemas/surya_input.schema.json`.
  - Command: `make -C systems/Parasara validate-schemas` or run the inline validator script in this doc.
  - Acceptance: validation succeeds or schema adjusted and re-run until success.

- [x] Licensing audit
  - Goal: Produce `systems/Parasara/Documentation/licenses.json` and review for AGPL/GPL risks.
  - Command: `pip-licenses --format=json > systems/Parasara/Documentation/licenses.json`
  - Note: `systems/Parasara/Documentation/licenses.json` has been created.

- [x] CI wiring: add GitHub Actions
  - Goal: Run `make validate-schemas` and `make test` on PRs to block regressions.
  - Acceptance: workflow passes on example PR.
  - Note: workflow added at `.github/workflows/parasara-ci.yml`.

- [x] Snapshot harness
  - Goal: Add `systems/Parasara/tests/snapshots/` and commit approved snapshot for `golden_chart_01`.
  - Acceptance: CI compares snapshot on changes.
  - Note: seeded snapshot `systems/Parasara/tests/snapshots/output_golden_chart_01.json` committed.

- [x] Ops checklist (data retention & secrets)
  - Goal: Create `systems/Parasara/Documentation/ops.md` with encryption and secret-handling guidance.
  - Acceptance: `systems/Parasara/Documentation/ops.md` created and committed.

- [ ] Historical dataset collection
  - Goal: Acquire initial labeled dataset (target ≥ 500 charts) or agreement to use smaller pilot dataset.

- [x] Historical dataset schema
  - Note: `systems/Parasara/schemas/historical_dataset.schema.json` added.

- [x] Pilot candidate file (curated)
  - Note: `systems/Parasara/fixtures/historical_pilot_candidates.json` added (12 records; provenance & time_confidence fields included).

- [x] Historical validator script
  - Note: `systems/Parasara/tools/validate_historical.py` added and run (VALIDATION_OK).

- [x] Phase‑1 skeleton: models & adapter
  - Note: `systems/Parasara/engine/models.py` and `systems/Parasara/engine/adapter/surya_adapter.py` added; `SuryaAdapter` successfully loads `golden_chart_01.json` and historical pilot candidates.

- [x] Unit tests for validator and adapters
  - Goal: Add `pytest` tests asserting schema validation and parsing; run in CI.
  - Note: tests added at `systems/Parasara/tests/test_validator_and_adapter.py` and pass locally; `Makefile` test target scoped to `systems/Parasara/tests`.

- [ ] SME verification package
  - Goal: prepare a 20-record SME review package with provenance and checklist.

- [ ] Generate synthetic pilot (50–200)
  - Goal: produce anonymized synthetic dataset for development/backtesting.
  - Note: pilot candidate file created at `systems/Parasara/fixtures/historical_pilot_candidates.json` (curated celebrity rows with provenance and time confidence). Pending SME/legal verification and anonymized pilot ingestion.

---

## Plan (phases)

- Phase 0 — Foundation: project skeleton, schemas, fixtures.
- Phase 1 — Adapter & Normalization: `SuryaAdapter`, `NormalizationEngine`, canonical IDs.
- Phase 2 — AstroState Builder & Enrichment: typed graph, dignity/shadbala, house state.
- Phase 3 — DSL Parser & Rule Engine: parser, macro expander, compiler, evaluator.
- Phase 4 — Timing Engine: DashaEngine, TransitEngine, Evaluation clock.
- Phase 5 — Yoga Detector & Domain Interpreters: yoga detection, per-domain interpreters.
- Phase 6 — Aggregator & Output Assembler: final JSON, explainability, traces.
- Phase 7 — Governance & Rule Lifecycle: rule registry, promoter, audit logs, snapshots.
- Phase 8 — Testing & Snapshot Harness: golden snapshots, backtest harness.
- Phase 9 — Performance & Caching: caches, profiling, parallel interpreters.
- Phase 10 — Operational Infrastructure: Redis, trace-store, dashboards, deployment.

---

## Feature Table — Components & Status

The following table maps high-level feature categories to included components, priority, and current status.

| Category | Basic Components Included | Priority | Status |
|---|---|---:|---|
| Core Data Models | `Chart`, `AstroState`, `DashaContext`, `TransitContext`, `RuleMatch`, `DomainPrediction` | Basic | 🟧 In Progress |
| Core Architecture | Adapter, NormalizationEngine, AstroState graph | Basic | 🟧 In Progress |
| Adapter | `SuryaAdapter`, schema validation, load/load_many helpers | Basic | 🟩 Completed |
| NormalizationEngine | degree/precision utilities, canonical IDs, enrichment hooks | Basic | 🟧 In Progress |
| Planet Enrichment | dignity, combustion, retrograde, friendships, shadbala, avasthas | Basic | 🟥 Not Started |
| House Enrichment | occupancy, house lord, benefic/malefic pressure, house summaries | Basic | 🟥 Not Started |
| Relationship Graph | aspects, conjunctions, exchanges, dispositors, reception map | Basic | 🟥 Not Started |
| Mandatory Vargas | D1 (natal), D9 (navamsa) — treated as canonical charts | Basic | 🟧 Partial (D9 implemented) |
| Advanced Vargas | D2, D3, D7, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60 | Advanced | 🟥 Not Started |
| DSL + Rule Engine | grammar, AST, compiler, execution plan, primitive predicates | Basic | 🟥 Not Started |
| Rule Library | house rules, planet rules, yogas, domain rules (data files) | Basic | 🟥 Not Started |
| Validation | schema validation, rule validation, chart consistency checks | Basic | 🟩 Completed (schema checks) |
| Reference Knowledge | signs, nakshatras, planetary constants, friendship tables, exaltation tables, vimshottari table | Basic | 🟩 Completed (seeded) |
| Inference Engine | Timing fusion, conflict resolver, confidence model, score aggregator | Basic | 🟥 Not Started |
| Prediction Engine (Domains) | Career, Wealth, Marriage, Children, Health, Safety (interpreters) | Basic | 🟥 Not Started |
| Output Layer | Output assembler, explainability, JSON schema, version metadata | Basic | 🟥 Not Started |
| Testing & Snapshot Harness | Golden charts, snapshot tests, rule tests | Basic | 🟩 Completed (seeded) |
| Rule Governance | Rule lifecycle, versioning, SME approvals, promotion workflows | Advanced | 🟥 Not Started |
| Calibration Systems | Backtest pipeline, accuracy computation, calibration engine | Advanced | 🟧 In Progress (backtest runner) |
| Performance & Scaling | Deterministic comparator, caching, predicate indexing, parallel interpreters | Advanced | 🟥 Not Started |
| Production Operations | Monitoring, logging, trace retention, privacy compliance, deployment | Advanced | 🟥 Not Started |
| Public API | Engine facade, request/response contracts, version negotiation | Basic | 🟥 Not Started |


## Next Implementation Sequence & Priorities (Table)

| Task# | Priority | Short Description | Acceptance | Status |
|---|---:|---|---|---|
| P0-Task#009 | High | Finalize `historical_dataset.schema.json`, add `validate_historical.py`, and anonymizer. | Validator passes on pilot; anonymizer present; `ops.md` references privacy checklist. | 🟩 Completed |
| P8-Task#001 | High | Add pytest tests for schema, `SuryaAdapter`, and snapshot equality. | Tests run locally and in CI passing. | 🟩 Completed |
| P1-Task#002 | High | Implement `engine/adapter` SuryaAdapter and models. | `SuryaAdapter.load` returns typed objects for fixtures and pilot; covered by tests. | 🟩 Completed |
| P0-Task#013 | High → Medium | Prepare 20-record SME review package with provenance and checklist. | SME annotations recorded; issues tracked. | 🟥 Not Started |
| P8-Task#004 | Medium | Small runner to execute interpreters (stubbed) over pilot and compute metrics. | Backtest runs and emits metrics summary. | 🟧 In Progress |
| P3-Task#002 | Medium | Implement grammar and parser (Lark/PEG) for the DSL. | Parser produces AST consistent with DSL spec. | 🟥 Not Started |
| P4-Task#001 | Medium | Prototype DashaEngine producing timelines. | Engines return deterministic timelines for fixtures. | 🟥 Not Started |
| P7-Task#001 | Medium → Low | SnapshotStore API and rule registry/promoter. | Snapshot workflow documented and tested. | 🟥 Not Started |
| P9-Task#001 | Low | Add caching and profiling harness; Redis integration. | Baseline performance tests and caching validated. | 🟥 Not Started |

---

| P1-Task#008 | High | Define `Core Data Models` (`Chart`, `AstroState`, `DashaContext`, `TransitContext`, `RuleMatch`, `DomainPrediction`). | Models available and used across adapter/normalizer/rule engine; stable model schema. | 🟧 In Progress |
