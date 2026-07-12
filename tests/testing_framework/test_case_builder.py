import json
from typing import Dict
from tests.testing_framework.data_models import TestCase, ExpectedOutputs


def build_testcase_from_chart(chart_path: str, expected_snapshot_path: str, id: str, desc: str = None) -> TestCase:
    exp = ExpectedOutputs(full_snapshot=expected_snapshot_path)
    tc = TestCase(id=id, description=desc, input_chart_path=chart_path, expected=exp)
    return tc


def load_testcases_from_json(path: str) -> list:
    with open(path, 'r', encoding='utf-8') as fh:
        arr = json.load(fh)
    out = []
    for o in arr:
        tc = TestCase.model_validate(o)
        out.append(tc)
    return out
