import sys
sys.path.insert(0, '.')
import json
from pathlib import Path
from systems.Parasara.tools.generate_snapshot import generate

def test_career_snapshot_matches_golden(tmp_path):
    repository_dash = Path(__file__).resolve().parents[3] / '-'
    dash_before = repository_dash.read_bytes() if repository_dash.exists() else None
    out = generate('systems/Parasara/fixtures/surya_test_chart.json', str(tmp_path / 'career-snapshot.json'))
    career = out['domains']['career']
    with open('systems/Parasara/tests/fixtures/golden_career_snapshot.json','r',encoding='utf-8') as fh:
        golden = json.load(fh)
    # Basic structural checks: indicators equality by id and contribution keys
    assert isinstance(career, dict)
    assert 'indicators' in career
    assert isinstance(career['indicators'], list)
    # ensure each indicator has rule_id and contribution
    for ind in career['indicators']:
        assert 'rule_id' in ind and 'contribution' in ind
    # compare rule ids with golden
    got_ids = [i['rule_id'] for i in career['indicators']]
    gold_ids = [i['rule_id'] for i in golden.get('indicators', [])]
    assert got_ids == gold_ids
    dash_after = repository_dash.read_bytes() if repository_dash.exists() else None
    assert dash_after == dash_before, "snapshot generation modified the repository-root '-' artifact"
