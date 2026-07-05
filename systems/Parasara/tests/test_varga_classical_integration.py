import sys
from pathlib import Path

# Ensure project root is on sys.path for imports during pytest
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate


def test_varga_d9_d60_present_on_planets():
    p = Path('systems/Parasara/fixtures/golden_chart_01.json')
    chart = SuryaAdapter.load(str(p))
    astro = chart_to_astrostate(chart)
    assert hasattr(astro, 'enrichments')
    # Each planet should have vargas for D9 and D60
    for pl in astro.planets:
        assert pl.vargas is not None
        assert 'D9' in pl.vargas
        assert 'D60' in pl.vargas
        # D9 should include a part with rashi name
        d9 = pl.vargas['D9'][0]
        assert 'rashi_name' in d9 and isinstance(d9['rashi_name'], str)
        # D60 part index must be in 0..59
        d60 = pl.vargas['D60'][0]
        assert 0 <= int(d60['part_index']) < 60
