import json
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.dasha.vimshottari import compute_vimshottari


def test_vimshottari_matches_golden():
    chart = SuryaAdapter.load('systems/Parasara/fixtures/golden_chart_01.json')
    astro = chart_to_astrostate(chart)
    out = compute_vimshottari(astro, periods=2)
    with open('tests/dasha/golden_vimshottari_01.json', 'r', encoding='utf8') as f:
        golden = json.load(f)
    # compare structural equality
    assert len(out) == len(golden)
    for a, b in zip(out, golden):
        assert a['lord'] == b['lord']
        assert a['duration_days'] == b['duration_days']
