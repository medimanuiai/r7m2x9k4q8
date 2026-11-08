"""Whole-sign ownership/occupancy with independently specified expectations."""
from copy import deepcopy

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter, StrictInputError
from tests.fwp01.test_input_contract import strict_payload, strict_snapshot


def test_taurus_lagna_ownership_occupancy_and_lord_placement():
    state = strict_snapshot()
    assert state.get_house_lord(1).value == "Venus"
    assert state.get_house_lord(12).value == "Mars"
    assert state.get_occupants(12).value == ("Sun",)
    assert state.get_occupants(1).value == ("Moon",)
    summary = state.get_house_summary(1).value
    assert summary["lord_natal_house"] == 7
    assert summary["strength"]["readiness"] == "unsupported"
    assert "house_score" not in summary
    assert "benefic_pressure" not in summary
    assert all(state.get_house_lord(i).value not in ("Rahu", "Ketu") for i in range(1, 13))


def test_complete_supplied_houses_reconcile_and_order_canonically():
    data = strict_payload()
    state = strict_snapshot(data)
    data["houses"] = [dict(number=i, sign=state.get_house(i).value.sign,
        lord=state.get_house_lord(i).value, occupants=list(state.get_occupants(i).value))
        for i in range(12, 0, -1)]
    assert strict_snapshot(data).logical_digest == state.logical_digest
    for field, value in (("lord", "Rahu"), ("sign", "Aries"), ("occupants", ["Sun", "Sun"])):
        invalid = deepcopy(data)
        invalid["houses"][-1][field] = value
        with pytest.raises(StrictInputError):
            SuryaAdapter.from_mapping_strict(invalid)
