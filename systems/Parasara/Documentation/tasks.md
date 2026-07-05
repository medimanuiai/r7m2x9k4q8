# Tasks and P#-Task# Registry

This document is the canonical registry for `P#-Task#` entries. It should be kept in sync with `implementation.md` (the index) and used to assign owners, estimates, and acceptance criteria.

Usage:
- Add one line per `P#-Task#` with owner, estimate, and acceptance criteria.
- Link to related code, tests, and docs.

Example entry:

- P1-Task#001 — `Chart`/`Planet`/`Metadata` models — owner: @owner — estimate: 1d — acceptance: typed Pydantic models present and adapter uses them. — [code link]

Current TODO: populate this file from `implementation.md`. Use this file to record owners and exact acceptance criteria for each Phase task.

- P0-Task#009 — Finalize historical dataset schema, validator, anonymizer — owner: @data — estimate: 2d — acceptance: `schemas/historical_dataset.schema.json` validated against pilot; `tools/validate_historical.py` exits 0; anonymizer script available.

- P8-Task#001 — Add pytest tests for schema, SuryaAdapter, and snapshot equality — owner: @qa — estimate: 1d — acceptance: tests in `systems/Parasara/tests` run and pass in CI.

- P1-Task#002 — Implement `SuryaAdapter` and core adapter models — owner: @adapter — estimate: 2d — acceptance: `SuryaAdapter.load` returns typed `Chart` objects and covered by unit tests.

- P0-Task#013 — Prepare 20-record SME review package — owner: @sme — estimate: 3d — acceptance: 20 anonymized charts with provenance and SME checklist uploaded to `systems/Parasara/fixtures/sme_review/`.

- P8-Task#004 — Backtest runner (stubbed interpreters) — owner: @backtest — estimate: 2d — acceptance: runner executes interpreters over pilot and emits metrics summary CSV.

- P3-Task#002 — DSL grammar & parser (Lark/PEG) — owner: @dsl — estimate: 3d — acceptance: parser produces AST for sample rules in `rules/parashara/v1`.

- P4-Task#001 — Prototype DashaEngine producing timelines — owner: @timing — estimate: 5d — acceptance: deterministic timelines produced for golden fixtures and covered by unit tests.

- P7-Task#001 — SnapshotStore API and rule registry/promoter — owner: @infra — estimate: 3d — acceptance: snapshot store can save and load snapshots; rule registry lists available rule sets.

- P9-Task#001 — Caching & profiling harness (Redis) — owner: @perf — estimate: 5d — acceptance: baseline profiling and Redis-backed cache storing rule evaluation results.

- P1-Task#008 — Define core data models (`Chart`, `AstroState`, `DashaContext`, `TransitContext`, `RuleMatch`, `DomainPrediction`) — owner: @models — estimate: 2d — acceptance: models implemented in `systems/Parasara/engine/models.py` and used by adapter/normalizer.

## M1 — Thin vertical slice (concrete subtasks)

The following subtasks implement the M1 vertical slice: Adapter → Normalization → AstroState → Rule Engine → Inference → Career Interpreter → Output + Explainability.

- M1-Task#001 — Adapter: SuryaAdapter fixture load — owner: @adapter — estimate: 1d — acceptance: `SuryaAdapter.load(golden_chart_01.json)` returns typed `Chart` with no schema errors. — Code: `systems/Parasara/engine/adapter/surya_adapter.py`

- M1-Task#002 — Normalization: canonical ids & precision — owner: @normalizer — estimate: 1d — acceptance: `chart_to_astrostate()` sets `planet.canonical_id`, `planet.degree_norm`, and attaches `vargas` (D1,D9) for each planet. — Code: `systems/Parasara/engine/normalizer.py`

- M1-Task#003 — Enrichments: basic planet_strengths & house_summaries — owner: @enrich — estimate: 2d — acceptance: `astro.enrichments` contains `planet_strengths` and `house_summaries` entries matching the golden fixture; simple numeric strengths present. — Code: `systems/Parasara/engine/enrichments/varga.py`, `systems/Parasara/engine/enrichments/planet_strengths.py`

- M1-Task#004 — Minimal Rule Runtime: core predicates & evaluator — owner: @ruleengine — estimate: 3d — acceptance: evaluator supports `in_sign`, `in_house`, `lord_of_house`, `is_exalted`, returns `RuleMatch` with evidence traces for sample rules. — Code: `systems/Parasara/engine/rule_engine/*.py`

- M1-Task#005 — Career Interpreter: mapping evidence → domain output — owner: @career — estimate: 2d — acceptance: `domains.career` contains `summary`, `score`, `confidence`, `components`, and `evidence` trace for golden fixture; output schema validated. — Code: `systems/Parasara/engine/interpreters/career.py`

- M1-Task#006 — Explainability: per-rule scoring breakdown & traces — owner: @explainability — estimate: 1d — acceptance: `domains.career.evidence` includes rule id, matched predicates, contribution, and final scoring formula breakdown. — Code: `systems/Parasara/engine/explainability.py`

- M1-Task#007 — Vertical-slice integration test & snapshot — owner: @qa — estimate: 1d — acceptance: `systems/Parasara/tests/test_vertical_slice_career.py` passes locally and snapshot `systems/Parasara/tests/snapshots/generated_vertical_slice_career.json` is added/approved. — Code/tests: `systems/Parasara/tests/` + snapshot path

- M1-Task#008 — CI snapshot check (integration) — owner: @ci — estimate: 0.5d — acceptance: CI job runs snapshot compare and fails on unapproved snapshot drift; pipeline step documented. — CI config: `.github/workflows/parasara-ci.yml`

Notes:
- Link code targets are suggested files/locations. If a target file does not yet exist, create a minimal module with the documented API and add tests.
- Keep explainability traces lightweight but complete enough to reconstruct scoring decisions.

