import sys
sys.path.insert(0, '.')
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.enrichments.planet_strengths import compute_planet_strengths


def test_strength_components_present():
    chart = SuryaAdapter.load('systems/Parasara/fixtures/surya_test_chart.json')
    astro = chart_to_astrostate(chart)
    ps = compute_planet_strengths(astro)
    assert isinstance(ps, dict)
    # check a few known planets
    for name in ('Sun','Moon','Mercury'):
        p = ps.get(name)
        assert p is not None
        assert 'strength_components' in p and isinstance(p['strength_components'], dict)
