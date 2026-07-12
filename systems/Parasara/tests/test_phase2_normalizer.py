import sys
from pathlib import Path

# Ensure repo root on path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate


def test_normalizer_on_golden_fixture():
    chart = SuryaAdapter.load('systems/Parasara/fixtures/golden_chart_01.json')
    astro = chart_to_astrostate(chart)
    assert astro is not None
    assert astro.location is not None
    assert isinstance(astro.planets, list)
    assert astro.diagnostics.get('planet_count', 0) >= 0
    # enrichments should include planet_strengths and house_summaries
    assert isinstance(astro.enrichments, dict)
    assert 'planet_strengths' in astro.enrichments
    assert 'house_summaries' in astro.enrichments


def test_normalizer_on_pilot_candidates():
    charts = SuryaAdapter.load_many('systems/Parasara/fixtures/historical_pilot_candidates.json')
    assert len(charts) > 0
    astros = [chart_to_astrostate(c) for c in charts]
    assert all(a.location is not None or a.metadata for a in astros)
