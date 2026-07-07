Jyothishyam Testing Framework
=============================

Overview
--------
This framework provides deterministic, reproducible testing for both Surya Siddhanta parsing and Par01ara interpretation engines. It supports:

- Constraint-based chart generation
- Golden snapshot regression tests
- Full JSON snapshot comparison with configurable ignore-list and float tolerances
- Coverage collection and HTML reporting

Phases
------
Phase A: Full JSON snapshot comparison (implemented)
Phase B: Rule coverage instrumentation
Phase C: Predicate branch coverage
Phase D: Property-based tests (Hypothesis)
Phase E: Determinism harness
Phase F: Performance regression checks
Phase G: Golden approval workflow

How to run
----------
Run the smoke integration test with pytest:

```bash
jyothishyam_env/Scripts/python -m pytest tests/test_framework_integration.py -q
```

Full JSON comparison
--------------------
The snapshot runner uses `json_compare.compare_json()` to compare entire engine outputs against golden snapshots. Non-deterministic keys (timestamps, generated IDs) are ignored by default; adjust via `ignore_keys` in the snapshot runner call.

Extending the framework
-----------------------
- Add SME-approved golden snapshots under `systems/Parasara/tests/fixtures/`.
- Add new TestCase JSON entries consumed by the regression runner.
- Implement Hypothesis strategies under `tests/testing_framework/` for property tests.

Contact
-------
If you need a new feature or a different comparison strategy, open an issue describing the requirements.
