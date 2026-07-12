from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.enrichments.planet_strengths import compute_planet_strengths


def test_planet_strengths_structure():
    chart = SuryaAdapter.load('systems/Parasara/fixtures/golden_chart_01.json')
    astro = chart_to_astrostate(chart)
    strengths = compute_planet_strengths(astro)
    assert isinstance(strengths, dict)
    for pname, pdata in strengths.items():
        assert 'shadbala' in pdata
        s = pdata['shadbala']
        assert 'rupas' in s and 'dig_bala' in s and 'cheshta_bala' in s
