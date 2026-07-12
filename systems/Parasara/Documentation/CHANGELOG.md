# Documentation changelog

All notable changes to documentation are recorded here.

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
