# Parāśara Engine Guardrails

This document captures the project-level guardrails for completing the Jyothishyam Parāśara engine. Follow these rules for design, implementation, testing, and CI enforcement. Keep it versioned and require SME signoff for rule changes.

## Acceptance
- I accept these guardrails and will follow them. I have two operational concerns (listed below) that need SME or operational decisions before full automation.

## High-level Principles
- Deterministic: identical input -> identical output. Tests must prove determinism. Use fixed seeds for synthetic generation.
- Explainable: every prediction must include evidence, provenance, and a trace linking back to rules and inputs.
- Auditable: every rule and derived artifact must include source file, author, version, and SME approval metadata.
- Versioned: all rules and canonical datasets are YAML/JSON under `systems/Parasara/rules/` and `golden_charts/`.
- Test-driven: every feature must have golden tests, unit tests, and property tests (Hypothesis where applicable).
- License-safe: Do not include AGPL code.

## 1. Surya Siddhanta validation (astronomy)
Status policy: "Implemented but awaiting astronomical validation" until 500 validation cases pass.

Required outputs (must be present and tested):
- Planet longitudes (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
- Sidereal correction + Lahiri ayanamsa (configurable)
- Ascendant (Lagna) calculation
- House cusps (whole-sign and pluggable systems)
- Nakshatra and pada
- Retrograde flag and planetary speed
- Sunrise/sunset if used by features
- Timezone conversion and lat/lon handling

Validation requirements:
- Create `tests/surya/planet_position_test_cases.json` with 500 deterministic cases (different centuries, lat/lon, times). Each case includes `tolerance_preferred = 0.01°` and `tolerance_regression = 0.1°`.
- CI must run a Surya validation job and mark engine as "astronomy-validated" only after all 500 cases pass with preferred tolerance; regression tolerance may be used for non-blocking runs but not for final acceptance.

## 2. FunctionalRoleEngine testing
- Must produce deterministic functional role mapping for every planet for all 12 lagnas.
- Test matrix: `12 lagnas × 9 planets × 3 states (benefic / malefic / neutral)` with golden expectations.
- Store expected outputs under `golden_charts/functional_roles/` with a canonical naming convention.

## 3. Aspect Engine (Parāśara Drishti)
- Implement a dedicated `ParasaraDrishtiEngine` (separate from any WesternAspectEngine) and make Western aspects opt-in and clearly named.
- Parāśara aspects to support at minimum:
  - Sun: 7th
  - Moon: 7th
  - Mars: 4th, 7th, 8th
  - Mercury: 7th
  - Jupiter: 5th, 7th, 9th
  - Venus: 7th
  - Saturn: 3rd, 7th, 10th
- Rahu/Ketu aspect behavior configurable in `systems/Parasara/config/aspects.yaml`.
- Each aspect edge must include `source`, `target`, `aspect_type`, `strength`, `orb`, and `evidence`.

## 4. Dasha Engine (Vimshottari)
- Implement `systems/Parasara/engine/dasha/vimshottari.py` with:
  - Moon nakshatra & pada calculation
  - balance at birth
  - Mahadasha, Antardasha, Pratyantardasha
- Tests: boundary tests for nakshatra/pada transitions, dasha boundaries, leap-year/date-edge cases.
- Output schema required:
  ```json
  {"period":"Mahadasha","lord":"Venus","start":"...","end":"...","duration_seconds":...}
  ```

## 5. Yoga Engine (data-driven, SME-approved rules)
- All yogas MUST be data-driven YAML under `systems/Parasara/rules/parashara/yogas/`.
- Required rule metadata fields (CI-enforced):
  - `id`, `name`, `source`, `classical_reference`, `conditions`, `exceptions`, `cancellation_rules`, `confidence`, `sme_status`, `author`, `version`
- New/modified yoga YAMLs must have `sme_status: pending` by default and a corresponding `tests/` entry demonstrating expected detection. CI will block merges to protected branches unless `sme_status: approved` and the golden tests pass.

## 6. Golden chart library and generation
- Organization: store charts under `golden_charts/<category>/<lagna>/<id>.json`.
- Categories must include (minimum): `normal`, `exaltation`, `debilitation`, `rajayoga`, `dhana`, `dasha_boundary`, `transit_cases`, `varga_cases`.
- Target initial count: 500 deterministic charts; expand to 1000+ in subsequent phases.
- Charts are synthetic but constraint-driven (SME templates) — each chart must include the input Surya JSON plus expected `AstroState`, expected yogas, dashas (where applicable), and domain indicators.

## 7. Interpretation Layer
- Add an interpretation generator module `systems/Parasara/interpretation/` which maps domain scores + contributors -> human-readable explanations.
- Interpretations must reference rule ids and evidence — no free-text assertions without rule linkage.

## 8. Completion criteria (blocker checklist)
Do not declare the engine "complete" until all items below are satisfied and CI shows green for the release branch:
- Surya: 500 astronomical validation cases pass (preferred tolerance) and regression tolerance documented.
- AstroState: full node/edge presence and schema validated.
- Enrichments: dignity, friendships, functional roles, aspects, shadbala, avasthas implemented and tested.
- Timing: Vimshottari implemented and boundary tests pass.
- Rules: all production rules are YAML, versioned, have provenance, and have SME approval metadata.
- Testing: golden charts present (500+), property tests (Hypothesis), deterministic snapshots, regression harness.
- Output: score ∈ [0,1], confidence ∈ [0,1], evidence present, trace present, interpretation present.

## CI enforcement and tooling
- Add CI checks:
  - `surya-validation` job (runs `tests/surya/`) — status gated for final release.
  - `rules-lint` job (ensures required YAML metadata, no missing fields).
  - `golden-approval` job (generates snapshot PR when golden artifacts change; PR blocked until `sme_status: approved`).
  - `determinism-check` job (re-run artifact generator twice and assert identical JSON hashes).

## Rule QA workflow
- New rule YAMLs must include `sme_status: pending` and a pointer to a test case.
- SME signs off by updating `sme_status: approved` and adding a short `sme_review` entry in YAML.
- CI enforces that merges to `pilot`/`main` only contain `sme_status: approved` for rule files.

## Concerns & required decisions
1. SME availability: many yoga rules and edge cases require classical SME validation. We need explicit SME time for rule signoff. Without SME, the engine can be built but must not be declared complete.
2. Astronomy reference: we'll use Skyfield/JPL for validation only (you approved). We must ensure the Surya adapter remains authoritative for production unless we decide to swap.

## Tracking and ownership
- Track progress via `Documentation/roadmap.md` and CI badges. Each phase must produce a short report under `tests/reports/phase_<n>_report.json`.
- Ownership: add `OWNER` metadata in rule directories for SME and eng lead.

## Next actions (immediate)
1. Create `tests/surya/planet_position_test_cases.json` scaffold and one Skyfield-based validator harness under `tests/surya/test_positions.py`.
2. Implement synthetic generator to start producing 500 golden charts (incremental categories first: one lagna per category).
3. Implement dasha engine scaffolding and representative boundary tests.

If you approve this document, I'll commit it to the repo (this file) and proceed with the immediate next actions above. If you have edits to the guardrails I'll update before implementing.
