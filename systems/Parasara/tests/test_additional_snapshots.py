import sys
sys.path.insert(0, '.')
import json
from pathlib import Path
from systems.Parasara.tools.generate_snapshot import generate

FIXTURE_MAP = {
    'systems/Parasara/fixtures/surya_generated_chart.json': 'systems/Parasara/tests/fixtures/surya_generated_chart_career_snapshot.json',
    'systems/Parasara/fixtures/golden_chart_01.json': 'systems/Parasara/tests/fixtures/golden_chart_01_career_snapshot.json',
}


def test_additional_snapshots_match(tmp_path):
    repository_dash = Path(__file__).resolve().parents[3] / '-'
    dash_before = repository_dash.read_bytes() if repository_dash.exists() else None
    for index, (inp, golden) in enumerate(FIXTURE_MAP.items()):
        out = generate(inp, str(tmp_path / f'additional-snapshot-{index}.json'))
        career = out['domains']['career']
        with open(golden, 'r', encoding='utf-8') as fh:
            g = json.load(fh)
        got_ids = [i['rule_id'] for i in career.get('indicators', [])]
        gold_ids = [i['rule_id'] for i in g.get('indicators', [])]
        assert got_ids == gold_ids, f"Indicator ids differ for {inp}"
    dash_after = repository_dash.read_bytes() if repository_dash.exists() else None
    assert dash_after == dash_before, "snapshot generation modified the repository-root '-' artifact"
