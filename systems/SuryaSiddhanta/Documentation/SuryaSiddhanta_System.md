# SuryaSiddhanta — System Documentation

Purpose: developer-facing system doc for `ndastro_engine` implementation, integration points, data, and testing notes.

Overview
- Short description: `SuryaSiddhanta` provides the astrology calculation engine used to compute planetary positions, houses, ayanamsa, dashas and related utilities.
- Location: `systems/SuryaSiddhanta/ndastro_engine`

Code layout
- `ndastro_engine/core.py`: high-level orchestration (load ephemeris, calculate planets/houses).
- `ndastro_engine/utils.py`: helpers (angles, DMS conversions, elevation lookup — SRTM + JSON fallback).
- `ndastro_engine/enums.py`: domain enums (planets, rasi, nakshatra).
- `ndastro_engine/models.py`: data models for charts, planets, houses.
- `ndastro_engine/dasa.py`: dasha calculations.
- `ndastro_engine/config.py`: configuration helpers and env var defaults.

Setup & development
- Python: use repo venv `jyothishyam_env` (see repo root instructions).
- Install dev deps: `jyothishyam_env/Scripts/python -m pip install -r requirements-dev.txt`.
- Optional for integration accuracy: install `skyfield` and `srtm`, and place `de440t.bsp` under `ndastro_engine/data/ephemeris/`.

Runtime configuration (env vars)
- `NDASTRO_USE_SRTM` — `1` (default) to enable SRTM; set `0` to force JSON fallback for deterministic unit tests.
- `NDASTRO_ELEVATION_SOURCE` — path to JSON elevation cache used when SRTM is disabled.

Testing
- Unit tests live under `tests/SuryaSiddhanta/`.
- System-level integration tests that require `de440t.bsp` should be gated and skipped when ephemeris is not present.
- See `tests/SuryaSiddhanta/Documentation/SuryaSiddhanta_Testing.md` for commands, fixtures and recent runs.

Data & assets
- Elevation cache: `ndastro_engine/data/elevation/elevation_cache.json` (packaged fallback for unit tests).
- Ephemeris: `ndastro_engine/data/ephemeris/de440t.bsp` (optional, used for high-accuracy integration).

API / Public entrypoints
- `calculate_chart(birth_iso, lat, lon, ayanamsa='lahiri')` — returns full chart JSON.
- `get_planet_position(eph, ts, body, when)` — low-level planet lon/lat computation (used internally and by tests).

Developer notes
- Keep I/O out of unit tests: use JSON elevation cache and mocked Skyfield objects in unit tests.
- When adding integration tests, store expected outputs as small numeric fixtures under `tests/SuryaSiddhanta/fixtures/` and gate the tests by checking for `de440t.bsp` presence.

Open tasks
- Add a canonical `trusted_chart.json` fixture for an agreed test case (e.g., `1995-03-10T14:35:00+05:30`, Bangalore) and scaffold a gated integration test comparing numeric tolerances.
- Document the `calculate_chart()` JSON schema in `systems/SuryaSiddhanta/Documentation` (schema example + field definitions).
