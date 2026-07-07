import sys
sys.path.insert(0, '.')
import json
from systems.Parasara.tools.generate_snapshot import generate

FIXTURE_MAP = {
    'systems/Parasara/fixtures/surya_generated_chart.json': 'systems/Parasara/tests/fixtures/surya_generated_chart_career_snapshot.json',
    'systems/Parasara/fixtures/golden_chart_01.json': 'systems/Parasara/tests/fixtures/golden_chart_01_career_snapshot.json',
}


def test_additional_snapshots_match():
    for inp, golden in FIXTURE_MAP.items():
        out = generate(inp, '-')
        career = out['domains']['career']
        with open(golden, 'r', encoding='utf-8') as fh:
            g = json.load(fh)
        got_ids = [i['rule_id'] for i in career.get('indicators', [])]
        gold_ids = [i['rule_id'] for i in g.get('indicators', [])]
        assert got_ids == gold_ids, f"Indicator ids differ for {inp}"
