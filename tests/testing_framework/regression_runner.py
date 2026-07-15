from typing import List, Dict
from pathlib import Path
from .data_models import TestCase
from .snapshot_runner import compare_snapshots


def run_regression(testcases: List[TestCase], output_dir: str = None) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for index, tc in enumerate(testcases):
        fs = tc.expected.full_snapshot
        output_path = str(Path(output_dir) / f'{index}-{tc.id}.json') if output_dir else None
        res = compare_snapshots(tc.input_chart_path, fs, output_path=output_path)
        results.append({'id': tc.id, 'result': res})
    return results
