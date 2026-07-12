# SuryaSiddhanta (Astronomy Engine) Documentation Index

Key locations for SuryaSiddhanta documentation and code:

- Engine code: systems/SuryaSiddhanta/
  - Core module: systems/SuryaSiddhanta/ndastro_engine/core.py
  - Ayanamsa functions: systems/SuryaSiddhanta/ndastro_engine/ayanamsa.py
  - Dasa/Vimshottari helpers: systems/SuryaSiddhanta/ndastro_engine/dasa.py
  - Nakshatra enum: systems/SuryaSiddhanta/ndastro_engine/nakshatra_enum.py

- System README and docs: systems/SuryaSiddhanta/README.md
- Tests and fixtures: tests/SuryaSiddhanta/ and systems/Parasara/fixtures/surya_generated_chart.json
- Surya -> Parasara conversion tool: systems/Parasara/tools/surya_to_parasara.py

Validation & testing files:

- Surya validation test cases: tests/surya/planet_position_test_cases.json
- Skyfield-based validation test: tests/surya/test_positions.py
- Surya testcase generator: tests/surya/generate_surya_test_cases.py
- Surya expected filler: tests/surya/fill_surya_expected.py

Notes:
- For astronomy accuracy (ayanamsa and sidereal conversion) see `systems/SuryaSiddhanta/ndastro_engine/ayanamsa.py` and `systems/SuryaSiddhanta/ndastro_engine/core.py`.
- To regenerate a Surya-format chart use `systems/Parasara/tools/surya_to_parasara.py`.
