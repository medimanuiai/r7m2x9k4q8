"""Strict non-interpretive house facts; no proxy score or pressure calculation."""
from copy import deepcopy


def compute_house_conditions(astro, graph):
    positions = {planet.name: planet.house for planet in astro.planets}
    rows = []
    for house in astro.houses:
        incoming = [deepcopy(edge) for edge in graph["edges"]
                    if edge["target"] is None and edge["trace"]["target_house"] == house["number"]]
        rows.append({**deepcopy(house), "lord_natal_house": positions[house["lord"]],
            "aspects": {"readiness": "ready" if incoming else "ready_empty",
                        "scope": "seven_classical_planets", "value": incoming},
            "strength": {"readiness": "unsupported", "issues": ["classical_strength_unavailable"]},
            "evidence": {"producer": "fwp01.strict_houses", "version": "1.0.0",
                "basis": "whole_sign_classical_ownership", "lagna": astro.lagna_sign,
                "number": house["number"], "sign": house["sign"], "lord": house["lord"],
                "occupants": list(house["occupants"])}})
    return rows
