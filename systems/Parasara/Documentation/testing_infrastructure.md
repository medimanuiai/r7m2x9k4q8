Parāśara Testing Infrastructure

Overview
- Purpose: describe the deterministic, explainable testing infrastructure and how to run it locally and in CI.
- Scope: vertical-slice tests, snapshot/golden workflow, rule & predicate coverage, property tests, determinism harness, and performance checks.

Phases implemented
1. Phase A — Deterministic snapshots
   - Full-JSON comparator with float tolerance and ignore-list
   - Snapshot generation: `systems/Parasara/tools/generate_snapshot.py`
2. Phase B — Instrumentation & Coverage
   - `tests/testing_framework/instrumentation.py` records rule and predicate hits
   - Harness: `tests/testing_framework/rule_coverage.py` and `tests/test_rule_coverage.py`
3. Phase C — Property & Determinism
   - Property tests with Hypothesis: `tests/property_tests.py`
   - Determinism harness: `tests/determinism_test.py`
4. Phase D — Performance
   - Perf measurement harness: `tests/testing_framework/perf.py`
5. Phase E — Golden Approval
   - Snapshot signoff helper: `tests/testing_framework/approve_snapshot.py`

How to run locally
- Run only Parāśara subsystem tests (recommended):

```bash
PYTHONPATH=. jyothishyam_env/Scripts/python -m pytest systems/Parasara
```

- Run only the coverage harness (generates rule & predicate summary):

```bash
PYTHONPATH=. jyothishyam_env/Scripts/python - <<PY
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from tests.testing_framework.rule_coverage import run_rule_coverage_scan
chart = SuryaAdapter.load('systems/Parasara/fixtures/golden_chart_01.json')
astro = chart_to_astrostate(chart)
print(run_rule_coverage_scan(astro))
PY
```

- Run property and determinism tests:

```bash
jyothishyam_env/Scripts/python -m pytest tests/property_tests.py
jyothishyam_env/Scripts/python -m pytest tests/determinism_test.py
```

Determinism and golden workflow
- Snapshots are deterministic: `generate_snapshot.generate()` sets `meta.generated_at` to null for comparability.
- To update a golden snapshot (SME-approved): regenerate and then call the signoff helper:

```bash
PYTHONPATH=. jyothishyam_env/Scripts/python - <<PY
from systems.Parasara.tools.generate_snapshot import generate
generate('systems/Parasara/fixtures/golden_chart_01.json', 'systems/Parasara/tests/snapshots/output_golden_chart_01.json')
PY

jyothishyam_env/Scripts/python tests/testing_framework/approve_snapshot.py systems/Parasara/tests/snapshots/output_golden_chart_01.json "SME Name" "note"
```

CI integration suggestions
- Add a job to run `pytest systems/Parasara` and publish these artifacts:
  - `tests/reports/rule_coverage.json` (output of `run_rule_coverage_scan`)
  - `tests/reports/perf.json` (output of perf harness)
  - Snapshot diff artifact when snapshots change
- Fail the build when rule coverage falls below a policy threshold.

Notes
- The full repo test run may require system-level dependencies (e.g., `ndastro_engine`, Skyfield). If CI runs the full suite, ensure the environment installs all required dev dependencies from `requirements-dev.txt`.
- Files of interest:
  - `tests/testing_framework/instrumentation.py`
  - `tests/testing_framework/rule_coverage.py`
  - `systems/Parasara/rules/parashara/v1` (YAML rule set)
  - `systems/Parasara/tests/snapshots/output_golden_chart_01.json`

Contact
- Ask me to wire CI steps, publish coverage reports, or create a PR with snapshot updates if you'd like me to proceed.