from typing import List, Dict
from .data_models import TestCase
from .snapshot_runner import compare_snapshots


def run_regression(testcases: List[TestCase]) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for tc in testcases:
        fs = tc.expected.full_snapshot
        res = compare_snapshots(tc.input_chart_path, fs)
        results.append({'id': tc.id, 'result': res})
    return results
