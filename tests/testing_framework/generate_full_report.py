#!/usr/bin/env python3
"""Run regression over example testcases, generate coverage and HTML report."""
import json
from pathlib import Path
from tests.testing_framework.data_models import TestCase
from tests.testing_framework.regression_runner import run_regression
from tests.testing_framework.generate_coverage_report import generate_report
from tests.testing_framework.report_generator import generate_html_report


def load_examples():
    # load the JSON examples file
    p = Path('tests/testing_framework/examples/testcases.json')
    arr = json.loads(p.read_text())
    # Pydantic V2: use model_validate
    tcs = [TestCase.model_validate(x) for x in arr]
    return tcs


def main():
    outdir = Path('tests/reports')
    outdir.mkdir(parents=True, exist_ok=True)
    tcs = load_examples()
    results = run_regression(tcs)
    cov_path = generate_report('systems/Parasara/fixtures/golden_chart_01.json', str(outdir))
    cov = json.loads(Path(cov_path).read_text())
    # coverage counts
    coverage_counts = {k: len(v) for k, v in cov.items()}
    html = generate_html_report(results, coverage_counts, str(outdir / 'report.html'))
    print('Report generated:', html)


if __name__ == '__main__':
    main()
