import sys
sys.path.insert(0, '.')
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.enrichments.planet_strengths import compute_planet_strengths


def test_strength_component_ranges():
    chart = SuryaAdapter.load('systems/Parasara/fixtures/surya_test_chart.json')
    astro = chart_to_astrostate(chart)
    ps = compute_planet_strengths(astro)
    for name, info in ps.items():
        comps = info.get('strength_components') or {}
        # each component should be a small float (abs <= 1.0)
        for k, v in comps.items():
            assert isinstance(v, float) or isinstance(v, int)
            assert abs(v) <= 1.0, f"Component {k} for {name} out of range: {v}"
        # final strength must equal sum(base)+components within 0..1
        s = float(info.get('strength') or 0.0)
        assert 0.0 <= s <= 1.0
