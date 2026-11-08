"""Directed sign facts remain present independently of target occupancy."""
from tests.fwp01.test_input_contract import strict_payload, strict_snapshot
from systems.Parasara.engine.capability import CapabilityFactState


def test_mars_special_aspects_include_sign_and_planet_references():
    state = strict_snapshot(strict_payload(0, [10, 95, 1, 61, 120, 180, 240, 300, 150]))
    graph = state.get_aspect_representation("whole_sign_graph").value
    edges = graph["edges"]
    mars = [edge for edge in edges if edge["source"] == "Mars"]
    assert {edge["trace"]["offset"] for edge in mars} == {4, 7, 8}
    cancer = [edge for edge in mars if edge["trace"]["target_sign"] == "Cancer"]
    assert {edge["target"] for edge in cancer} == {None, "Moon"}
    assert cancer[0]["trace"]["target_house"] == 4
    assert any(edge["target"] is None and not edge["trace"]["matched_planets"] for edge in edges)
    assert not any(edge["source"] in ("Rahu", "Ketu") for edge in edges)
    assert state.get_aspects_from("Rahu", "whole_sign_graph").state is CapabilityFactState.UNSUPPORTED_CAPABILITY
    assert state.get_aspects_from("Ketu", "whole_sign_graph").value_present is False
    keys = [(edge["source"], edge["trace"]["offset"], edge["target"]) for edge in edges]
    assert len(keys) == len(set(keys))
    assert all(edge["trace"]["authority"]["artifacts"][0]["content_sha256"] for edge in edges)
    assert any(fact.target_id == "Moon" for fact in state.get_aspects_from("Mars", "whole_sign_graph").value)


def test_same_sign_is_symmetric_and_cross_sign_degree_proximity_is_not_conjunction():
    data = strict_payload(0, [1, 31.1, 2, 61, 120, 180, 240, 300, 150])
    rows = strict_snapshot(data).get_aspect_representation("basic_conjunction_list").value
    pairs = {(row["from"], row["to"]) for row in rows}
    assert ("Sun", "Mars") in pairs and ("Mars", "Sun") in pairs
    assert ("Sun", "Moon") not in pairs
    assert all((target, source) in pairs for source, target in pairs)
