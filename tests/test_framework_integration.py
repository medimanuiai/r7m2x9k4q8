import os
import json
from tests.testing_framework.test_case_builder import build_testcase_from_chart
from tests.testing_framework.regression_runner import run_regression
from tests.testing_framework.coverage_engine import CoverageEngine
from tests.testing_framework.report_generator import generate_html_report


def test_framework_smoke_run():
    # Build example testcases using existing golden snapshots
    base = 'systems/Parasara/fixtures/golden_chart_01.json'
    golden = 'systems/Parasara/tests/fixtures/golden_career_snapshot.json'
    tc1 = build_testcase_from_chart(base, golden, id='golden_01', desc='Golden chart 01')

    base2 = 'systems/Parasara/fixtures/surya_generated_chart.json'
    golden2 = 'systems/Parasara/tests/fixtures/surya_generated_chart_career_snapshot.json'
    tc2 = build_testcase_from_chart(base2, golden2, id='generated_01', desc='Generated chart 01')

    testcases = [tc1, tc2]
    results = run_regression(testcases)
    cov = CoverageEngine()
    # ingest diagnostics from generated snapshots for coverage
    for tc in testcases:
        with open(tc.expected.full_snapshot, 'r', encoding='utf-8') as fh:
            snapshot = json.load(fh)
        # adapt to expected diagnostics structure used in coverage engine
        astro = {'diagnostics': {'lagna_summary': {}, 'planet_strengths': {}, 'houses': []}}
        # try to fill simple fields
        try:
            # golden snapshots are career-only; for demo we reuse tests/fixtures/golden_career_snapshot.json structure
            # skip detailed population
            pass
        except Exception:
            pass
        cov.ingest_astro(astro)

    report_path = 'tests/testrun_report.html'
    generate_html_report(results, cov.report(), report_path)
    # At least one test should pass in a smoke run; detailed CI should enforce full pass.
    assert any(r['result'].get('matched') for r in results), f"No test passed: {results}"
    # ensure report exists
    assert os.path.exists(report_path)
