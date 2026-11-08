"""Existing immutable queries, exact catalog and field-level source evidence."""
import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate_strict, build_strict_snapshot
from systems.Parasara.engine.astrostate_api import (
    freeze_astrostate, require_snapshot, get_general_capability_catalog,
    snapshot_logical_bytes, snapshot_from_logical_bytes,
)
from systems.Parasara.engine.capability import CapabilityReadiness
from systems.Parasara.engine.rules.snapshot_adapter import prepare_predicate_snapshot
from tests.fwp01.test_input_contract import strict_payload, strict_snapshot


def test_catalog_versions_queries_and_projection_stay_existing():
    state = strict_snapshot()
    assert len(get_general_capability_catalog()) == len(state.capabilities) == 20
    assert all(cap.capability_version == "1.0.0" for cap in state.capabilities)
    assert state.inspect_capability("planets.normalized", "2.0.0").readiness is CapabilityReadiness.VERSION_MISMATCH
    assert state.inspect_capability("dasha.current").readiness is CapabilityReadiness.MISSING
    assert state.inspect_capability("transits.current").readiness is CapabilityReadiness.MISSING
    assert state.inspect_capability("houses.summaries").source_kind == "strict_house_conditions"
    projection = prepare_predicate_snapshot(state)
    assert projection.state is not None
    assert projection.state.capabilities["aspects.whole_sign_graph"].readiness is CapabilityReadiness.MISSING
    assert projection.state.capabilities["aspects.basic_conjunction_list"].readiness is CapabilityReadiness.READY_EMPTY
    assert snapshot_logical_bytes(snapshot_from_logical_bytes(snapshot_logical_bytes(state))) == snapshot_logical_bytes(state)


def test_input_model_and_construction_mutation_cannot_change_snapshot():
    data = strict_payload()
    chart = SuryaAdapter.from_mapping_strict(data)
    outcome = build_strict_snapshot(chart)
    state = require_snapshot(outcome)
    digest = state.logical_digest
    chart.planets[0]["degree"] = 25
    data["planets"][0]["degree"] = 27
    with pytest.raises(TypeError):
        state.core.metadata["factual_sources"]["planets"]["Sun"]["nakshatra"]["pada"] = 4
    astro = chart_to_astrostate_strict(SuryaAdapter.from_mapping_strict(strict_payload()))
    frozen = require_snapshot(freeze_astrostate(astro))
    before = frozen.logical_digest
    astro.houses[0]["occupants"].append("Sun")
    astro.metadata["factual_sources"]["planets"]["Sun"]["motion"]["value"]["retrograde"] = True
    assert frozen.logical_digest == before
    assert state.logical_digest == digest


@pytest.mark.parametrize("route", ["builder", "shared", "deepcopy", "json_copy"])
def test_strict_aspect_scope_survives_publication_and_projection(route):
    from copy import deepcopy
    from systems.Parasara.engine.astrostate import AstroState
    from systems.Parasara.engine.capability import CapabilityFactState
    from systems.Parasara.engine.rules.canonical_predicates import evaluate_aspect_exists
    from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext
    from systems.Parasara.engine.rules.models import PredicateStatus

    chart = SuryaAdapter.from_mapping_strict(strict_payload(0, [10, 95, 1, 61, 120, 180, 240, 300, 150]))
    if route == "builder":
        outcome = build_strict_snapshot(chart)
    else:
        astro = chart_to_astrostate_strict(chart)
        if route == "deepcopy":
            astro = deepcopy(astro)
        elif route == "json_copy":
            astro = AstroState.model_validate_json(astro.model_dump_json())
        outcome = freeze_astrostate(astro)
    state = require_snapshot(outcome)
    # Test the serialized publication too, so node semantics cannot depend on a
    # live construction object or wrapper-local information.
    restored = snapshot_from_logical_bytes(snapshot_logical_bytes(state))
    for published in (state, restored):
        cap = published.inspect_capability("aspects.whole_sign_graph")
        assert cap.source_kind == "strict_classical_whole_sign_graph"
        assert next(item for item in published.capabilities
                    if item.capability_id == "aspects.whole_sign_graph").factual_scope == "seven_classical_planets"
        assert any(fact.target_id == "Moon" for fact in published.get_aspects_from("Mars", "whole_sign_graph").value)
        for node in ("Rahu", "Ketu"):
            assert published.get_aspects_from(node, "whole_sign_graph").state is CapabilityFactState.UNSUPPORTED_CAPABILITY
        prepared = prepare_predicate_snapshot(published).state
        # Contract-conflict regression: the protected graph has global readiness.
        # Do not replace this safe incomplete result with false node negatives or
        # claim that the supported Mars fact reached the predicate.
        for filters in ({"from_planet": "Mars", "to_planet": "Moon"},
                        {"from_planet": "Rahu"}, {"from_planet": "Ketu"}):
            result = evaluate_aspect_exists(filters, prepared, PredicateEvaluationContext())
            assert result.status is PredicateStatus.MISSING_CAPABILITY
            assert result.matched is False


def test_strict_graph_rejects_scope_loss_and_explicit_legacy_override():
    from systems.Parasara.engine.astrostate_api import AstroStateBuildFailure, AstroCapabilitySupply
    astro = chart_to_astrostate_strict(SuryaAdapter.from_mapping_strict(strict_payload()))
    graph = astro.enrichments["aspects"]
    supply = AstroCapabilitySupply(capability_id="aspects.whole_sign_graph", capability_version="1.0.0",
        source_kind="legacy_whole_sign_graph", factual_scope="legacy_compatibility", content=graph)
    failure = freeze_astrostate(astro, capability_supplies=(supply,))
    assert isinstance(failure, AstroStateBuildFailure)
    assert failure.issues[0].code == "contradictory_strict_aspect_scope"
    del graph["source_kind"]
    del graph["factual_scope"]
    failure = freeze_astrostate(astro)
    assert isinstance(failure, AstroStateBuildFailure)
    assert failure.issues[0].code == "invalid_strict_aspect_scope"


def test_legacy_shared_publication_keeps_its_graph_and_predicate_semantics():
    from pathlib import Path
    from systems.Parasara.engine.normalizer import chart_to_astrostate
    from systems.Parasara.engine.enrichments.aspects import compute_aspect_graph
    from systems.Parasara.engine.rules.canonical_predicates import evaluate_aspect_exists
    from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext
    from systems.Parasara.engine.rules.models import PredicateStatus
    path = Path(__file__).resolve().parents[2] / "systems/Parasara/fixtures/golden_chart_01.json"
    astro = chart_to_astrostate(SuryaAdapter.load(str(path)))
    compute_aspect_graph(astro)
    state = require_snapshot(freeze_astrostate(astro))
    assert state.inspect_capability("aspects.whole_sign_graph").source_kind == "legacy_whole_sign_graph"
    prepared = prepare_predicate_snapshot(state).state
    result = evaluate_aspect_exists({"from_planet": "Mars", "to_planet": "Moon"}, prepared, PredicateEvaluationContext())
    assert result.status is PredicateStatus.MATCHED
