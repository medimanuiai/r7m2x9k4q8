import sys
sys.path.insert(0, '.')
from hypothesis import given, settings, strategies as st
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.enrichments.planet_strengths import compute_planet_strengths
from tests.testing_framework.chart_generator import generate_from_constraints

BASE = 'systems/Parasara/fixtures/golden_chart_01.json'

@settings(max_examples=20, derandomize=True)
@given(
    lagna=st.sampled_from(['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'])
)
def test_scores_in_range(lagna):
    outp = 'tests/tmp_prop_chart.json'
    generate_from_constraints(BASE, {'lagna': lagna}, outp)
    chart = SuryaAdapter.load(outp)
    astro = chart_to_astrostate(chart)
    ps = compute_planet_strengths(astro)
    for name, info in ps.items():
        s = float(info.get('strength') or 0.0)
        assert 0.0 <= s <= 1.0
        # confidence/functional_score if present
        fs = info.get('functional_score')
        if fs is not None:
            assert 0.0 <= float(fs) <= 1.0
