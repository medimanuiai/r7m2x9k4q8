# Documentation changelog

All notable changes to documentation are recorded here.

## 2026-07-13

- Completed evidence-based reviews of architecture, specifications, implementation, governance, guides, and operations.
- Expanded current-state and target-state boundaries without changing engine behavior.
- Corrected implementation status, task, testing, vertical-slice, governance, and operational claims against repository evidence.
- Archived the mixed gap proposal list and added a canonical evidence-based gap register.
- Normalized compatibility-pointer metadata and corrected root and repository documentation indexes.

## 2026-07-12

- Established a local documentation index, authority policy, and separate current/target architecture records.
- Added canonical implementation status, roadmap, active tasks, and focused architecture specifications.
- Migrated and corrected testing and vertical-slice guides under `guides/`.
- Migrated engineering guardrails under `governance/`.
- Migrated operational and licensing documentation under `operations/`.
- Moved the point-in-time license inventory to `evidence/licenses.json`.
- Updated known repository references to the migrated paths.
- Archived the superseded mixed architecture, specification, implementation-status, roadmap, and task documents.
- Added replacement notices at former stable paths and redirected repository indexes to canonical documents.
- Completed the final structural validation pass and recorded evidence under `evidence/`.
- Recorded a point-in-time structural index while keeping live stage-workspace status separate from canonical documentation.

## 2026-07-05

- Split large `implementation.md` content into modular docs and added scaffolding:
  - `architecture.md`
  - `roadmap.md`
  - `tasks.md`
  - `guides/vertical-slice.md`

## 2026-07-06

- Added `DerivedState` Pydantic models and validation in the DerivedState builder (`systems/Parasara/engine/derived/models.py`, `systems/Parasara/engine/derived/builder.py`).
- Seeded per-lagna functional-role YAML tables for all 12 signs under `systems/Parasara/enrichment_tables/functional_roles/` and integrated them into the functional-role engine.
- Enhanced `planet_strengths` to include `strength_components` for explainability and diagnostics.
- Added focused unit tests and golden snapshot tests for the career domain; CI workflow to run `pytest` on push/PR added at `.github/workflows/ci.yaml`.
- Documentation updates: `basic-specs.md` and `architecture.md` updated to reflect DerivedState, tables, strength components, and CI.
