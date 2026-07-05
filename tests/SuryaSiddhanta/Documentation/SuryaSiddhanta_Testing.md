# Testing Guide — ndastro_engine (SuryaSiddhanta)

This document describes how to test the `ndastro_engine` package, including the local elevation model, recommended test layout, virtual environment setup, fixtures, CI guidance, and a concise record of recent test runs.

This file is a living document — it is updated as tests are added and integration requirements evolve.

## Purpose

- Make tests deterministic and fast.
- Remove external HTTP dependency for elevation lookups (use local JSON cache for unit tests; SRTM supported for integration accuracy checks).
- Provide clear commands, inputs and expected outputs to reproduce verification runs.

## Recent Test Runs

- Date: 2026-07-03
- Environment: `jyothishyam_env` (virtualenv created in repo root)
- Key env vars used for deterministic runs:
  - `NDASTRO_USE_SRTM=0` (disable SRTM for unit tests)
  - `NDASTRO_ELEVATION_SOURCE=$(pwd)/tests/SuryaSiddhanta/fixtures/elevation_cache.json`
  - `PYTHONPATH=$(pwd)/systems/SuryaSiddhanta` (so `ndastro_engine` imports from the workspace)

- Canonical test input used in fixtures and tests:
  - Birth datetime (ISO, tz-aware): `1995-03-10T14:35:00+05:30` (used as canonical example in discussion)
  - Location: Bangalore — `lat=12.9716`, `lon=77.5946`

- Commands executed (examples):
  - Install dev deps (once):
    - `jyothishyam_env/Scripts/python -m pip install -r requirements-dev.txt`
    - optional: `jyothishyam_env/Scripts/python -m pip install skyfield python-dotenv srtm`
  - Run targeted unit tests (JSON elevation fallback):
    - `PYTHONPATH="$(pwd)/systems/SuryaSiddhanta" NDASTRO_USE_SRTM=0 NDASTRO_ELEVATION_SOURCE="$(pwd)/tests/SuryaSiddhanta/fixtures/elevation_cache.json" jyothishyam_env/Scripts/python -m pytest tests/SuryaSiddhanta/test_utils.py -q`
  - Run full unit suite (JSON fallback):
    - `PYTHONPATH="$(pwd)/systems/SuryaSiddhanta" NDASTRO_USE_SRTM=0 NDASTRO_ELEVATION_SOURCE="$(pwd)/tests/SuryaSiddhanta/fixtures/elevation_cache.json" jyothishyam_env/Scripts/python -m pytest -q`

- Tests added / executed:
  - `tests/SuryaSiddhanta/test_utils.py` — unit tests for:
    - `normalize_degree()` (angle normalization)
    - `dms2dd()` / `dd2dms()` round-trip
    - `get_elevation_by_latlon()` JSON fallback (exact match and nearby rounding)
  - `tests/SuryaSiddhanta/test_core_mocked.py` — mocked Skyfield integration:
    - `get_planet_position()` exercised with a Skyfield-like fake `eph` and `ts` (no ephemeris download)

- Results:
  - `tests/SuryaSiddhanta/test_utils.py`: 3 passed
  - `tests/SuryaSiddhanta/test_core_mocked.py`: 1 passed
  - Full run: `4 passed` (all unit tests passed)

## Ephemeris (de440t.bsp)

- Decision: download `de440t.bsp` once and use it only for optional accuracy integration tests.
- Location downloaded to (project): `systems/SuryaSiddhanta/ndastro_engine/data/ephemeris/de440t.bsp` (downloaded on 2026-07-03).
- Note: unit tests and mocked tests do not require this file; it is used only for accuracy/integration checks.

## Inputs / Outputs recorded for verification

- Input form used in tests and fixtures:
  - `birth_iso` (string, ISO 8601 with timezone)
  - `lat` / `lon` (floats)
  - `ayanamsa_system` (string, e.g., `lahiri`)

- Representative output fields produced by the engine (schema enforced in tests/fixtures):
  - `ayanamsa_deg` (float)
  - `lagna_deg` (float)
  - `planets`: mapping from planet name → `{ lon_deg: float, nakshatra: string, pada: int }`
  - `houses`: list of house cusps (floats)

## Types of testing (what we cover now)

- Unit tests: pure functions and small helpers (deterministic, fast). Example: `normalize_degree`, `dms2dd`, JSON elevation fallback.
- Mocked Skyfield tests: exercises integration with Skyfield-like objects while avoiding network/ephemeris I/O. Example: `get_planet_position()` with fake `eph`/`ts`.
- Integration / Accuracy tests (optional, slow): run with `de440t.bsp` + SRTM to compare outputs against a trusted reference (Swiss Ephemeris / DrikPanchang). These run in a separate job to keep CI fast.

## Next steps / notes

- I will scaffold a single accuracy test on request that uses `de440t.bsp` to compute the canonical birth chart and compare against a trusted fixture with numeric tolerances. This test will be gated so it runs only when ephemeris is available (or when a CI job opts in).
- If you prefer, I will insert a brief entry in this document each time we add tests or run the integration, including the exact input JSON and output snapshot. Tell me whether you want automatic snapshot files committed to `tests/SuryaSiddhanta/fixtures/`.
