from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.dasha.vimshottari import compute_vimshottari


def test_vimshottari_structure():
    chart = SuryaAdapter.load('systems/Parasara/fixtures/golden_chart_01.json')
    astro = chart_to_astrostate(chart)
    d = compute_vimshottari(astro)
    assert isinstance(d, list)
    if d:
        first = d[0]
        assert 'lord' in first and 'start' in first and 'end' in first
