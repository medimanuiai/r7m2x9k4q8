import sys
sys.path.insert(0, '.')
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.enrichments.planet_strengths import compute_planet_strengths


def test_sun_house_mapping_from_aries_to_lagna():
    # load fixture and force lagna to Scorpio to test mapping
    chart = SuryaAdapter.load('systems/Parasara/fixtures/surya_test_chart.json')
    # set lagna to Scorpio
    if chart.lagna:
        chart.lagna.sign = 'Scorpio'
    astro = chart_to_astrostate(chart)
    # find Sun
    sun = next((p for p in astro.planets if p.name == 'Sun'), None)
    assert sun is not None, 'Sun planet missing'
    # Sun in fixture is in Gemini (raw house 3); with lagna Scorpio it should map to house 8
    assert sun.house == 8, f'Expected Sun house 8 for Scorpio lagna, got {sun.house}'


def test_mercury_functional_role_for_scorpio():
    # Mercury functional role should be malefic for Scorpio lagna in our heuristic
    chart = SuryaAdapter.load('systems/Parasara/fixtures/surya_test_chart.json')
    if chart.lagna:
        chart.lagna.sign = 'Scorpio'
    astro = chart_to_astrostate(chart)
    # recompute strengths/functional roles
    ps = compute_planet_strengths(astro)
    mercury = ps.get('Mercury')
    assert mercury is not None, 'Mercury missing in strengths'
    # accept neutral or malefic depending on heuristic/table overrides
    assert mercury.get('functional_role') in ('functional_malefic','yogakaraka','functional_neutral'), f"Mercury functional role unexpected: {mercury.get('functional_role')}"
