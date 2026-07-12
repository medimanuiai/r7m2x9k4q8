**Validation And Roadmap**

This document records the Phase plan and the validation changes requested for reaching "project complete". It separates astronomy accuracy from Jyotisha normalization, prescribes Phase 1 validation gates, and records acceptance criteria.

**Phase 1 — Critical validation & core engines**
- **Surya Siddhanta validation (Layered)**: separate astronomy vs Jyotisha normalization.
  - **Layer A — Astronomy (JPL/Skyfield vs NDAstro)**: validate planetary longitudes computed by `ndastro_engine`/SuryaSiddhanta against Skyfield/JPL.
    - Targets: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu.
    - Tolerance: preferred <= 0.01°; acceptable <= 0.1°.
    - Data: 500+ deterministic birth cases (`tests/surya/planet_position_test_cases.json`).
    - Acceptance: per-planet longitude within tolerance.

  - **Layer B — Jyotisha conversion (normalization)**: validate sidereal conversion and discrete classifications derived from longitude.
    - Flow: Tropical longitude -> Lahiri ayanamsa -> Sidereal longitude -> Rashi -> Nakshatra -> Pada.
    - Acceptance: Rashi match = 100%, Nakshatra match = 100%, Pada match = 100% (for validated cases).
    - Rationale: a correct longitude may still produce wrong nakshatra if ayanamsa is mishandled.

- **Vimshottari Dasha**
  - Coverage: canonical M1 algorithm with nakshatra-lord mapping, balance-at-birth, mahadasha, antardasha, pratyantardasha.
  - Tests: golden outputs + boundary tests:
    - Moon at nakshatra fractions: 0°00', 3°20', 6°40', 10°00', 13°20' ... (0, 1/4, 2/4, 3/4, 1 of nakshatra)
    - Exact nakshatra transition
    - Midnight births
    - Leap-year dates
    - Timezone conversions
  - Acceptance: sequence and start/end dates match canonical reference within 1 day.

- **Planet Strength Engine (Parāśara shadbala and components)**
  - Implement classical components and preserve raw source values (do not collapse classical measures into opaque scalar without retaining sources).
  - Required outputs (structure):
    {
      "dignity": { "own_sign": bool, "exalted": bool, "debilitated": bool },
      "shadbala": { "rupas": float, "dig_bala": float, "kala_bala": float, "cheshta_bala": float, "drik_bala": float, "naisargika": float },
      "derived_strength_score": float
    }
  - Acceptance: raw classical values produced and unit-tested against reference charts; derived score is only a convenience, not a replacement for raw measures.

- **Functional Role Engine**
  - Produce structured per-planet functional reasoning (not just labels). Example:
    {
      "Mars": {
        "natural": "malefic",
        "functional_role": "mixed",
        "roles": {"lagna_lord": true, "sixth_lord": true, "yogakaraka": false},
        "reason": ["Lagna lord", "Owns 6th house", "Net positive due to Scorpio lagna"]
      }
    }
  - Matrix tests: full `12 lagnas × 9 planets × multiple states` golden matrix.
  - Acceptance: structured reasoning present in outputs and unit/golden tests pass.

- **Parāśara Aspect Engine**
  - Implement only Parāśara Graha Drishti (whole-sign offsets) in Phase 1.
  - Offsets:
    - Mars: 4th, 7th, 8th
    - Jupiter: 5th, 7th, 9th
    - Saturn: 3rd, 7th, 10th
    - All planets: 7th
    - Rahu/Ketu: configurable (default 7th)
  - Do NOT introduce Western aspect terms (square, trine, sextile, opposition).
  - Postpone orbit/orb-strengths to Phase 2.

**Phase 2 — Rule library, Yoga, Interpretation, Transit & Dasha mapping**
- **Yoga Engine**: extend scaffolding into a data-driven library.
  - Minimum golden cases recommended:
    - Rajayoga: 100
    - Dhana Yoga: 100
    - Arishta: 100
    - Kuja Dosha: 50
    - Total yoga golden: >= 350
- **Rule library expansion**: author 200+ Parāśara rules separated by category:
  - `rules/dignity/`, `rules/yoga/`, `rules/house/`, `rules/aspects/`, `rules/dasha/`, `rules/transit/`, `rules/domain/`
  - Each rule must carry metadata: `id`, `description`, `examples`, `sme_approved` (boolean), `severity`.
  - Enforce linting with `tools/rules_lint.py` in CI.
- **Interpretation layer (Domain Interpreter)**: domain interpreters (Career, Marriage, etc.) should be thin wrappers mapping `RuleMatch[]` into domain scores via YAML-driven rules (no duplicated astrology logic inside interpreters).

**Phase 3 — Domain engines & Confidence**
- **Domain Interpreter**: implement rule-driven interpreters, not monolithic logic.
- **Confidence Engine**: compute `confidence` as combination of:
  - rule coverage, evidence quality, data completeness, agreement (natal, dasha, transit)
  - Provide explainable contributors (list of factors and weights).

**Phase 4 — Final validation and reproducibility**
- **Golden/SME validation**: collect 1000 golden charts across modules (Surya, Dasha, Yoga, Rules).
- **SME approval**: enforce `sme_approved=true` for production rule merges.
- **Reproducibility test**: repeat same input + same engine + same rule version + same machine 100× — expect identical JSON outputs (except metadata timestamps).

**Acceptance gating & CI**
- Add a `surya-validation` CI job that installs `skyfield`, `jplephem` and required ephemerides and runs `tests/surya/test_positions.py`. Failure on mismatch.
- Add `rules-lint` job that runs `tools/rules_lint.py` and rejects PRs that remove or fail `sme_approved` gating for production rules.
- Require golden tests to pass for merge to `main`.

**Immediate next steps (after documentation)**
1. Add CI `surya-validation` action (draft) OR run Skyfield locally to validate the 500 cases.
2. Implement Planet Strength full components and unit tests.
3. Expand Functional Role matrix and capture reasoning traces.

**Phase 1 constraint**: do not begin Phase 2/3 domain work until all Phase 1 validations are green and SME-approved where required.

---

Document author: Project team
Status: draft — awaiting execution approval
