import sys
sys.path.insert(0, '.')
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.enrichments.planet_strengths import compute_planet_strengths


def test_scopio_table_override_mercury():
    chart = SuryaAdapter.load('systems/Parasara/fixtures/surya_test_chart.json')
    if chart.lagna:
        chart.lagna.sign = 'Scorpio'
    astro = chart_to_astrostate(chart)
    ps = compute_planet_strengths(astro)
    mercury = ps.get('Mercury')
    assert mercury is not None
    assert mercury.get('functional_role') == 'functional_malefic', f"Expected table override, got {mercury.get('functional_role')}"
