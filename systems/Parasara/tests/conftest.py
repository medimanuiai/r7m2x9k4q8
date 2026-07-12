import json
from pathlib import Path
import pytest

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

@pytest.fixture
def golden_chart_path():
    return FIXTURES / "golden_chart_01.json"

@pytest.fixture
def load_golden_chart(golden_chart_path):
    with open(golden_chart_path, 'r', encoding='utf-8') as f:
        return json.load(f)
