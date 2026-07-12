 # Vertical Slice Guide — Adapter → AstroState → Rule Engine → Inference → Career → Output

This guide describes the thin vertical slice to implement and verify during early iterations.

## Goal

Produce a working end-to-end path for a single golden fixture that outputs a `domains.career` prediction with traces.

## Steps

1. Ensure dependencies installed and project root on `PYTHONPATH`.

2. Generate a snapshot for the golden fixture (example):

```bash
PYTHONPATH=. jyothishyam_env/Scripts/python systems/Parasara/tools/generate_snapshot.py \
  systems/Parasara/fixtures/golden_chart_01.json \
  systems/Parasara/tests/snapshots/generated_vertical_slice_career.json
```

2b. Or generate a Surya-format chart directly from the local SuryaSiddhanta engine and run the Parasara pipeline end-to-end (SuryaSiddhanta must be importable in the virtualenv):

```bash
PYTHONPATH=. jyothishyam_env/Scripts/python systems/Parasara/tools/surya_to_parasara.py \
  --lat 12.9716 --lon 77.5946 --dt 1990-01-01T12:00:00 --out systems/Parasara/fixtures/surya_generated_chart.json --run-snapshot
```

3. Run the vertical slice integration test (to be added):

```bash
PYTHONPATH=. jyothishyam_env/Scripts/python -m pytest -q systems/Parasara/tests/test_vertical_slice_career.py
```

4. Inspect output and evidence traces in `systems/Parasara/tests/snapshots/generated_vertical_slice_career.json` and compare to the approved snapshot.

## Acceptance

- `domains.career` contains `summary`, `score`, `confidence`, `components`, and an `evidence` trace.
- The test passes locally and is suitable for CI snapshot check.
