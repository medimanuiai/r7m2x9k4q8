"""Shape-producing legacy algorithms do not authorize strict varga facts."""
import pytest

from systems.Parasara.engine.capability import CapabilityFactState, CapabilityReadiness
from tests.fwp01.test_input_contract import strict_snapshot


@pytest.mark.parametrize("name", ["D3", "D7", "D9", "D30"])
def test_unapproved_varga_is_unsupported_not_ready_empty(name):
    state = strict_snapshot()
    assert state.inspect_capability("vargas.positions").readiness is CapabilityReadiness.UNSUPPORTED
    assert state.get_varga(name).state is CapabilityFactState.UNSUPPORTED_CAPABILITY
    assert state.core.metadata["factual_sources"]["enrichments"]["varga_availability"][name]["readiness"] == "unsupported"
