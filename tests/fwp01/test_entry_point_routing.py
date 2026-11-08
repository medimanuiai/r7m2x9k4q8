"""Deliberate route selection and same-object authority with one publication."""
from pathlib import Path

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter, StrictInputError
from systems.Parasara.engine import normalizer
from systems.Parasara.engine.astrostate_api import AstroStateBuildSuccess
from systems.Parasara.engine.versioning import RuleVersionResolver, compatibility_v1_config
from tests.fwp01.test_input_contract import strict_payload


def test_existing_three_planet_partial_house_fixture_keeps_legacy_route():
    path = Path(__file__).resolve().parents[2] / "systems/Parasara/fixtures/golden_chart_01.json"
    legacy = SuryaAdapter.load(str(path))
    assert len(legacy.planets) == 3 and len(legacy.houses) == 2
    assert len(normalizer.chart_to_astrostate(legacy).planets) == 3
    with pytest.raises(StrictInputError):
        SuryaAdapter.load_strict(str(path))


def test_strict_failure_cannot_call_compatibility(monkeypatch):
    monkeypatch.setattr(SuryaAdapter, "load", lambda *_: pytest.fail("legacy loader fallback"))
    monkeypatch.setattr(normalizer, "chart_to_astrostate", lambda *_: pytest.fail("legacy normalizer fallback"))
    bad = strict_payload()
    bad["planets"][0]["degree"] = 30
    with pytest.raises(StrictInputError):
        SuryaAdapter.from_mapping_strict(bad)
    assert isinstance(normalizer.build_strict_snapshot(SuryaAdapter.from_mapping_strict(strict_payload())), AstroStateBuildSuccess)


def test_one_freeze_and_supplied_authority_is_not_reresolved(monkeypatch):
    from systems.Parasara.engine import astrostate_api
    authority = RuleVersionResolver().resolve(compatibility_v1_config())
    calls = []
    original = astrostate_api.freeze_astrostate
    def observed(*args, **kwargs):
        calls.append(kwargs)
        return original(*args, **kwargs)
    monkeypatch.setattr(astrostate_api, "freeze_astrostate", observed)
    monkeypatch.setattr(RuleVersionResolver, "resolve", lambda *_a, **_k: pytest.fail("authority reselected"))
    result = normalizer.build_strict_snapshot(SuryaAdapter.from_mapping_strict(strict_payload()), resolved_versions=authority)
    assert isinstance(result, AstroStateBuildSuccess)
    assert len(calls) == 1
    assert result.snapshot.evaluation_context["instant"] == authority.config.evaluation_instant
    authority.authorize_snapshot(result.snapshot)
