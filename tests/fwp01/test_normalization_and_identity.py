"""Nine-body construction, every Lagna, aliases and zero-safe placement."""
import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter, StrictInputError
from systems.Parasara.engine.identities import CANONICAL_PLANETS, SIGNS
from systems.Parasara.engine.normalizer import chart_to_astrostate_strict, build_strict_snapshot
from systems.Parasara.engine.astrostate_api import AstroStateBuildFailure
from tests.fwp01.test_input_contract import strict_payload


@pytest.mark.parametrize("index", range(12))
def test_all_lagna_houses_are_relative_and_zero_safe(index):
    payload = strict_payload(index * 30.0, [0.0, 41.0, 89.0, 105.0, 169.0, 211.0, 279.0, 319.0, 139.0])
    astro = chart_to_astrostate_strict(SuryaAdapter.from_mapping_strict(payload))
    assert astro.lagna_degree == 0.0
    assert astro.planets[0].degree == astro.planets[0].degree_norm == 0.0
    assert [p.name for p in astro.planets] == list(CANONICAL_PLANETS)
    assert [h["number"] for h in astro.houses] == list(range(1, 13))
    assert astro.houses[0]["sign"] == SIGNS[index]
    assert astro.planets[0].house == ((0 - index) % 12) + 1


def test_identity_alias_is_only_an_input_spelling():
    payload = strict_payload()
    payload["planets"][-1]["name"] = " kEtHu "
    payload["planets"].reverse()
    astro = chart_to_astrostate_strict(SuryaAdapter.from_mapping_strict(payload))
    assert [p.name for p in astro.planets] == list(CANONICAL_PLANETS)
    assert "Kethu" not in astro.metadata["factual_sources"]["planets"]


def test_mutated_strict_model_is_revalidated_and_never_falls_back():
    chart = SuryaAdapter.from_mapping_strict(strict_payload())
    chart.planets[0]["house"] = 1
    with pytest.raises(StrictInputError, match="house_placement_mismatch"):
        chart_to_astrostate_strict(chart)
    assert isinstance(build_strict_snapshot(chart), AstroStateBuildFailure)
