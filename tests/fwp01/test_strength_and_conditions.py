"""Source conditions and unsupported classical calculations never zero-fill."""
from systems.Parasara.engine.capability import CapabilityReadiness, CapabilityFactState
from tests.fwp01.test_input_contract import strict_payload, strict_snapshot


def test_unknown_flags_and_all_classical_components_remain_unavailable():
    state = strict_snapshot()
    for capability in ("strengths.planet", "strengths.shadbala", "dignity.planet"):
        assert state.inspect_capability(capability).readiness is CapabilityReadiness.UNSUPPORTED
    assert state.get_planet_strength("Sun").state is CapabilityFactState.UNSUPPORTED_CAPABILITY
    conditions = state.core.metadata["factual_sources"]["enrichments"]["conditions"]
    for name, row in conditions.items():
        for field in ("combust", "exalted", "debilitated"):
            assert row["conditions"][field]["readiness"] == "missing"
            assert "value" not in row["conditions"][field]
        assert all(item["readiness"] == "unsupported" and "value" not in item
                   for item in row["classical_strength"].values())
        assert row["conditions"]["retrograde"]["readiness"] == (
            "unsupported" if name in ("Rahu", "Ketu") else "ready")


def test_sourced_boolean_condition_is_preserved_without_calculating_dignity():
    data = strict_payload()
    data["planets"][0]["flags"] = dict(exalted=True,
        provenance={"exalted": dict(source="fixture.oracle", version="1.0.0")})
    data["planets"][1]["motion"]["retrograde"] = True
    state = strict_snapshot(data)
    facts = state.core.metadata["factual_sources"]["enrichments"]["conditions"]
    assert facts["Sun"]["conditions"]["exalted"]["value"] is True
    assert facts["Moon"]["conditions"]["retrograde"]["value"]["retrograde"] is True
    assert state.get_exaltation_facts("Sun").value_present
    assert state.inspect_capability("dignity.planet").readiness is CapabilityReadiness.UNSUPPORTED
