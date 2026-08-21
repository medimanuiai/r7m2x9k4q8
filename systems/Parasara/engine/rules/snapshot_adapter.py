"""One-way immutable AstroState to protected PreparedAstroState projection."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from systems.Parasara.engine.astrostate_api import (
    AstroStateSnapshot,
    thaw_value,
)
from systems.Parasara.engine.capability import CapabilityReadiness
from systems.Parasara.engine.rules.prepared_state import (
    CapabilitySupply,
    PreparationOutcome,
    PreparedStateVersions,
    prepare_predicate_state,
)


_MISSING = object()


def prepare_predicate_snapshot(
    snapshot: Any,
    *,
    versions: PreparedStateVersions | None = None,
) -> PreparationOutcome:
    """Project one immutable snapshot into the exact seven-capability view."""

    if not isinstance(snapshot, AstroStateSnapshot):
        return prepare_predicate_state(None, versions=versions)
    planets = []
    for fact in snapshot.core.planets:
        placement = snapshot.get_planet_house(fact.planet_id)
        planets.append(SimpleNamespace(
            name=fact.planet_id, sign=fact.sign, degree=fact.degree,
            house=placement.value if placement.value_present else None,
        ))

    whole = snapshot.inspect_capability("aspects.whole_sign_graph")
    basic = snapshot.inspect_capability("aspects.basic_conjunction_list")
    aspects = _MISSING
    if whole.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
        result = snapshot.get_aspect_representation("whole_sign_graph")
        aspects = thaw_value(result.value) if result.value_present else []
    elif basic.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
        result = snapshot.get_aspect_representation("basic_conjunction_list")
        aspects = thaw_value(result.value) if result.value_present else []
    enrichments = {} if aspects is _MISSING else {"aspects": aspects}

    derived = None
    supplies: tuple[CapabilitySupply, ...] = ()
    roles = snapshot.inspect_capability("roles.functional")
    if roles.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
        role_result = snapshot.get_functional_roles()
        role_content = {
            item.planet_id: item.value for item in (role_result.value or ())
        }
        role_rows = {
            planet_id: {"functional_role": value}
            for planet_id, value in role_content.items()
        }
        if roles.source_kind == "legacy_yoga_adapter":
            supplies = (CapabilitySupply(
                capability_id="roles.functional", capability_version="1.0.0",
                source_kind="legacy_yoga_adapter", content=role_content,
            ),)
        else:
            derived = {"functional_roles": role_rows}

    metadata: dict[str, Any] = {}
    exaltation = snapshot.inspect_capability("dignity.exaltation_facts")
    if exaltation.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
        records = tuple(
            thaw_value(item)
            for planet in snapshot.get_planets().value or ()
            for item in (
                snapshot.get_exaltation_facts(planet.planet_id).value or ()
            )
        )
        metadata_rows = {
            item["planet_id"]: item["value"]
            for item in records
            if item.get("source_kind") == "legacy_metadata_exaltations"
        }
        if metadata_rows or exaltation.readiness is CapabilityReadiness.READY_EMPTY:
            metadata["exaltations"] = metadata_rows

    source = SimpleNamespace(
        planets=planets, lagna_sign=snapshot.core.lagna_sign,
        enrichments=enrichments, derived=derived, metadata=metadata,
    )
    return prepare_predicate_state(
        source, capability_supplies=supplies, versions=versions,
    )


__all__ = ("prepare_predicate_snapshot",)
