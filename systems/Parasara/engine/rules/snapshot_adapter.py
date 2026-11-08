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
    # The protected projection has global (not per-source) readiness. A graph
    # supporting only classical planets cannot claim node "no aspect" facts.
    # Withhold that partial graph rather than changing the seven-capability
    # contract or falsely publishing empty node relations. Legacy paths are exact.
    partial_whole = whole.source_kind == "strict_classical_whole_sign_graph"
    if whole.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY) and not partial_whole:
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


def prepare_predicate_snapshot_v2(snapshot, *, resolved_versions):
    """Project already published strict facts under one selected V2 authority."""
    from .aspect_contract_v2 import (
        AspectCapabilityV2, PreparationOutcomeV2, SOURCE_SUPPORT, GRAPH,
        SOURCE_KIND, FACTUAL_SCOPE, VERSION, make_prepared_v2, require_v2_authority,
    )
    from .canonical import freeze_canonical
    from .prepared_state import PreparationIssue
    require_v2_authority(resolved_versions)
    if not isinstance(snapshot, AstroStateSnapshot):
        return PreparationOutcomeV2(succeeded=False, state=None,
            issues=(PreparationIssue(code="invalid_snapshot", path="$"),))
    resolved_versions.authorize_snapshot(snapshot)
    legacy = prepare_predicate_snapshot(snapshot)
    if not legacy.succeeded:
        return PreparationOutcomeV2(succeeded=False, state=None, issues=legacy.issues)
    cap = next(item for item in snapshot.capabilities if item.capability_id == GRAPH)
    graph = AspectCapabilityV2(readiness=CapabilityReadiness.MISSING)
    if cap.capability_version != "1.0.0":
        graph = AspectCapabilityV2(readiness=CapabilityReadiness.VERSION_MISMATCH,
            observed_version=cap.capability_version, source_kind=SOURCE_KIND)
    elif cap.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY):
        if cap.source_kind != SOURCE_KIND or cap.factual_scope != FACTUAL_SCOPE:
            graph = AspectCapabilityV2(readiness=CapabilityReadiness.MALFORMED,
                source_kind=SOURCE_KIND, observed_version=VERSION, issues=("aspect_coverage_contradictory",))
        else:
            try:
                content = thaw_value(cap.content)
                if (set(content) != {"edges", "by_planet", "config_version", "source_kind", "factual_scope"}
                        or content.get("source_kind") != SOURCE_KIND or content.get("factual_scope") != FACTUAL_SCOPE):
                    raise ValueError("contradictory scoped provenance")
                graph = AspectCapabilityV2(readiness=cap.readiness, source_kind=SOURCE_KIND,
                    observed_version=VERSION, content=freeze_canonical({
                        "edges": content["edges"], "source_support": SOURCE_SUPPORT,
                        "config_version": content["config_version"],
                    }))
            except (TypeError, ValueError, KeyError) as exc:
                issue = ("aspect_coverage_contradictory" if str(exc) == "aspect_coverage_contradictory"
                         else "aspect_coverage_malformed")
                graph = AspectCapabilityV2(readiness=CapabilityReadiness.MALFORMED,
                    source_kind=SOURCE_KIND, observed_version=VERSION, issues=(issue,))
    elif cap.readiness is CapabilityReadiness.UNSUPPORTED:
        graph = AspectCapabilityV2(readiness=cap.readiness)
    elif cap.readiness is not CapabilityReadiness.MISSING:
        graph = AspectCapabilityV2(readiness=cap.readiness, source_kind=SOURCE_KIND,
            observed_version=VERSION, issues=("aspect_coverage_malformed",) if cap.readiness is CapabilityReadiness.MALFORMED else ())
    return PreparationOutcomeV2(succeeded=True,
        state=make_prepared_v2(legacy.state, graph, resolved_versions))


__all__ = ("prepare_predicate_snapshot", "prepare_predicate_snapshot_v2")
