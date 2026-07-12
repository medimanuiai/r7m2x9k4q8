import sys
sys.path.insert(0, '.')
import json
from systems.Parasara.tools.generate_snapshot import generate

def test_career_snapshot_matches_golden():
    out = generate('systems/Parasara/fixtures/surya_test_chart.json','-')
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
