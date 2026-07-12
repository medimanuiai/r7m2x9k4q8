# SuryaSiddhanta Validation Simulation

Purpose: lightweight, isolated scripts to validate `systems/SuryaSiddhanta` (ndastro_engine)
by comparing selected outputs against reference engines cloned under `external_refs/`.

Design goals
- All work stays inside `external_refs/Simulation/SuryaSiddhanta`.
- Non-invasive: scripts only import from the cloned repos or call them; they do not modify other code.
- Robust: imports are attempted and skipped gracefully if dependencies are missing.

Quick start
1. Activate your project venv (optional):

```bash
source jyothishyam_env/Scripts/activate
```

2. Run the comparison script (from the repo root):

```bash
python external_refs/Simulation/SuryaSiddhanta/scripts/compare_engines.py
```

What it does
- Loads fixtures in `fixtures/fixtures.json` (3 example edge cases).
- Runs `systems/SuryaSiddhanta/ndastro_engine` calculations for each fixture.
- Attempts to import `VedicAstroEngineLite` and `VedAstro.Python` from `external_refs/` and run comparable calculations.
- Prints a JSON report summarizing numeric outputs for quick inspection.

Notes
- You may need to install dependencies for the external engines (see their READMEs). The script will still run SuryaSiddhanta outputs even if references are unavailable.
- This is a validation harness — tweak fixtures and tolerances as needed.
