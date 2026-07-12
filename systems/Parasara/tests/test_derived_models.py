import sys
sys.path.insert(0, '.')
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.derived.models import DerivedState


def test_derived_state_validates():
    chart = SuryaAdapter.load('systems/Parasara/fixtures/surya_test_chart.json')
    astro = chart_to_astrostate(chart)
    assert getattr(astro, 'derived', None) is not None
    # ensure parsing does not raise
    ds = DerivedState.model_validate(astro.derived)
    assert isinstance(ds, DerivedState)
