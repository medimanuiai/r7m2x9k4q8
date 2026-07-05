import sys
from pathlib import Path

# Ensure project root is on sys.path for imports during pytest
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from systems.Parasara.engine.enrichments.canonical_ids import canonical_planet_id, canonical_house_id
from systems.Parasara.engine.enrichments.precision import round_degree, normalize_longitude
from systems.Parasara.engine.enrichments.varga import varga_summary_for_planet


def test_canonical_planet_ids():
    assert canonical_planet_id('Sun') == 'sun'
    assert canonical_planet_id('moon') == 'moon'
    assert canonical_planet_id('  Mars  ') == 'mars'


def test_canonical_house_ids():
    assert canonical_house_id(1) == 'house_1'
    assert canonical_house_id('4') == 'house_4'
    assert canonical_house_id(None) == 'house_0'


def test_precision_rounding():
    assert round_degree(12.34567, 2) == 12.35
    assert normalize_longitude(370.1234) == 10.12


def test_varga_summary_simple():
    s = varga_summary_for_planet(10.5)
    assert 'D1' in s and 'D9' in s and 'D60' in s
    # D1 should include the base longitude
    assert round(s['D1'][0], 4) == round(10.5 % 360.0, 4)


def test_chart_to_astrostate_integration():
    from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
    from systems.Parasara.engine.normalizer import chart_to_astrostate
    p = Path('systems/Parasara/fixtures/golden_chart_01.json')
    chart = SuryaAdapter.load(str(p))
    astro = chart_to_astrostate(chart)
    assert hasattr(astro, 'enrichments')
    assert 'canonical_planet_ids' in astro.enrichments
    # planets should include canonical_id and degree_norm
    for pl in astro.planets:
        assert pl.canonical_id is not None
        assert pl.degree_norm is None or isinstance(pl.degree_norm, float)
        assert pl.vargas is None or isinstance(pl.vargas, dict)
