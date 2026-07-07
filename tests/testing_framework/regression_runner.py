from typing import List
from .data_models import TestCase
from .snapshot_runner import compare_snapshots


def run_regression(testcases: List[TestCase]) -> List[dict]:
    results = []
    for tc in testcases:
        res = compare_snapshots(tc.input_chart_path, tc.expected.full_snapshot)
        results.append({'id': tc.id, 'result': res})
    return results
