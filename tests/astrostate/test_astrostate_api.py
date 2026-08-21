from __future__ import annotations

from dataclasses import fields, replace
import hashlib
import json
from pathlib import Path

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.astrostate_api import (
    AstroCapabilitySupply,
    AstroQueryResult,
    AstroStateBuildFailure,
    AstroStateBuildSuccess,
    AstroStateSnapshot,
    CapabilityFactState,
    CapabilityReadiness,
    ConstructionIssue,
    PlanetFact,
    astro_query_result_json_bytes,
    freeze_astrostate,
    require_snapshot,
    snapshot_from_logical_bytes,
    snapshot_logical_bytes,
    snapshot_logical_projection,
)
from systems.Parasara.engine.enrichments.yoga_engine import evaluate_yoga_rules
from systems.Parasara.engine.interpreters.career import interpret_career
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules.prepared_state import (
    prepare_predicate_state,
    prepared_state_json_bytes,
)
from systems.Parasara.engine.rules.snapshot_adapter import prepare_predicate_snapshot


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"


def mutable(name: str = "surya_test_chart.json") -> AstroState:
    return chart_to_astrostate(SuryaAdapter.load(str(FIXTURES / name)))


def snapshot(name: str = "surya_test_chart.json") -> AstroStateSnapshot:
    return require_snapshot(freeze_astrostate(mutable(name)))


def compact(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def test_snapshot_has_exact_top_level_contract_and_core_fact_ownership():
    state = snapshot()
    assert tuple(item.name for item in fields(AstroStateSnapshot)) == (
        "schema_version", "producer_version", "normalization_version",
        "system_scope", "evaluation_context", "core", "capabilities",
        "construction_issues",
    )
    assert tuple(item.name for item in fields(PlanetFact)) == (
        "planet_id", "sign", "degree", "normalized_longitude",
    )
    assert state.system_scope == "parasara"
    assert len(state.logical_digest) == 64
    core_backed = {
        item.capability_id: item for item in state.capabilities if item.core_path is not None
    }
    assert core_backed
    assert all(item.content is None for item in core_backed.values())


def test_build_union_is_closed_and_rejects_ambiguous_variants():
    state = snapshot()
    fatal = ConstructionIssue(
        code="controlled_failure", path="$", recoverable=False, fatal=True,
    )
    with pytest.raises(ValueError):
        AstroStateBuildSuccess(snapshot=state, issues=(fatal,))
    with pytest.raises(ValueError):
        AstroStateBuildFailure(issues=())


def test_snapshot_is_deeply_immutable_and_defensively_copied():
    source = mutable()
    state = require_snapshot(freeze_astrostate(source))
    original = state.get_planet("Mars")
    source.planets[2].house = 1
    source.metadata["changed"] = {"nested": [1, 2, 3]}
    assert state.get_planet_house("Mars").value == 10
    assert state.get_planet("Mars") == original
    with pytest.raises(TypeError):
        state.core.metadata["changed"] = True
    with pytest.raises(Exception):
        state.get_planet("Mars").value.sign = "Aries"


def test_duplicate_entities_and_contradictory_legacy_sources_fail_safely():
    duplicate = AstroState(
        metadata={}, location=None, lagna_sign="Aries",
        planets=[
            PlanetState(name="Mars", sign="Aries", degree=1.0, house=1),
            PlanetState(name="mars", sign="Aries", degree=2.0, house=2),
        ], houses=[], enrichments={}, diagnostics={}, derived=None,
    )
    failed = freeze_astrostate(duplicate)
    assert isinstance(failed, AstroStateBuildFailure)
    assert failed.issues[0].code == "duplicate_planet_id"

    conflicting = mutable()
    conflicting.enrichments["normalized_degrees"]["Mars"] = 999.0
    failed = freeze_astrostate(conflicting)
    assert isinstance(failed, AstroStateBuildFailure)
    assert failed.issues[0].code == "contradictory_normalized_longitude"


def test_query_states_cover_present_absent_ready_empty_missing_malformed_and_unsupported():
    state = snapshot()
    assert state.get_planet("Mars").state is CapabilityFactState.PRESENT
    assert state.get_current_dasha().state is CapabilityFactState.CAPABILITY_UNAVAILABLE
    assert state.inspect_capability("future.unknown").readiness is CapabilityReadiness.UNSUPPORTED
    assert state.inspect_capability("planets.normalized", "2.0.0").readiness is CapabilityReadiness.VERSION_MISMATCH

    minimal = AstroState(
        metadata={}, location=None, lagna_sign="Aries",
        planets=[PlanetState(name="Mars", sign="Aries", degree=1.0, house=10)],
        houses=[], diagnostics={}, enrichments={"aspects": []}, derived=None,
    )
    minimal_state = require_snapshot(freeze_astrostate(minimal))
    empty = minimal_state.get_aspects_from("Mars", "basic_conjunction_list")
    assert empty.state is CapabilityFactState.PRESENT and empty.value == ()

    original = next(
        item for item in minimal_state.capabilities
        if item.capability_id == "aspects.basic_conjunction_list"
    )
    malformed_capability = replace(
        original, readiness=CapabilityReadiness.MALFORMED,
        content=None, content_empty=False, issues=("producer_malformed",),
    )
    malformed_state = replace(
        minimal_state,
        capabilities=tuple(
            malformed_capability if item.capability_id == original.capability_id else item
            for item in minimal_state.capabilities
        ),
    )
    malformed = malformed_state.get_aspects_from("Mars", "basic_conjunction_list")
    assert malformed.state is CapabilityFactState.MALFORMED_CAPABILITY
    assert malformed.value_present is False


def test_query_inputs_and_explicit_aspect_representation_are_strict():
    state = snapshot()
    for value in (True, 1.0, "1", 0, 13):
        with pytest.raises(ValueError):
            state.get_house(value)
    with pytest.raises(ValueError):
        state.get_planet("Pluto")
    with pytest.raises(ValueError):
        state.get_varga("navamsa")
    with pytest.raises(ValueError):
        state.get_aspects_from("Mars", None)
    with pytest.raises(ValueError):
        state.get_aspects_from("Mars", "automatic")


def test_query_order_and_capability_mapping_are_deterministic():
    state = snapshot()
    assert tuple(item.planet_id for item in state.get_planets().value) == (
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu",
    )
    assert tuple(item.house_number for item in state.get_houses().value) == tuple(range(1, 13))
    assert state.get_planet_house("mars").capability_id == "planets.house_placement"
    assert state.get_planet_dignity("Mars").capability_id == "dignity.planet"
    assert state.get_house_lord(10).capability_id == "houses.lords"
    assert state.get_occupants(10).value == ("Mars", "Venus")
    assert state.get_functional_role("Mars").capability_id == "roles.functional"
    assert state.get_shadbala("Mars").value.factual_scope == "legacy_partial_proxy"
    assert tuple(item.capability_id for item in state.list_capabilities()) == tuple(
        sorted(item.capability_id for item in state.list_capabilities())
    )


def test_query_results_are_single_capability_immutable_serializable_values():
    result = snapshot().get_planet("Mars")
    assert isinstance(result, AstroQueryResult)
    payload = astro_query_result_json_bytes(result)
    assert json.loads(payload)["capability_id"] == "planets.normalized"
    assert b"logical_digest" not in payload


def test_digest_is_deterministic_context_sensitive_and_self_excluding():
    source = mutable()
    first = require_snapshot(freeze_astrostate(source, evaluation_context={"instant": "2026-01-01T00:00:00Z"}))
    second = require_snapshot(freeze_astrostate(source, evaluation_context={"instant": "2026-01-01T00:00:00Z"}))
    changed = require_snapshot(freeze_astrostate(source, evaluation_context={"instant": "2026-01-02T00:00:00Z"}))
    assert first.logical_digest == second.logical_digest
    assert first.logical_digest != changed.logical_digest
    assert "logical_digest" not in snapshot_logical_projection(first)
    assert first.logical_digest == hashlib.sha256(snapshot_logical_bytes(first)).hexdigest()


def test_canonical_serialization_round_trip_is_exact():
    state = snapshot()
    payload = snapshot_logical_bytes(state)
    restored = snapshot_from_logical_bytes(payload)
    assert restored == state
    assert snapshot_logical_bytes(restored) == payload
    assert restored.logical_digest == state.logical_digest
    with pytest.raises(ValueError):
        snapshot_from_logical_bytes(payload + b"\n")


def test_optional_version_mismatch_is_nonfatal_and_contradictory_supply_is_fatal():
    source = mutable()
    mismatched = freeze_astrostate(source, capability_supplies=(AstroCapabilitySupply(
        capability_id="dasha.current", capability_version="2.0.0",
        source_kind="test_supply", content={"lord": "Mars"},
    ),))
    assert isinstance(mismatched, AstroStateBuildSuccess)
    assert mismatched.snapshot.get_current_dasha().state is CapabilityFactState.VERSION_MISMATCH

    conflict = freeze_astrostate(source, capability_supplies=(AstroCapabilitySupply(
        capability_id="roles.functional", capability_version="1.0.0",
        source_kind="test_supply", content={"Mars": "benefic"},
    ),))
    assert isinstance(conflict, AstroStateBuildFailure)
    assert conflict.issues[0].code == "contradictory_capability_supply"


@pytest.mark.parametrize("fixture", ("golden_chart_01.json", "surya_test_chart.json", "surya_generated_chart.json"))
def test_all_seven_prepared_capabilities_are_byte_equivalent(fixture):
    source = mutable(fixture)
    legacy = prepare_predicate_state(source)
    current = prepare_predicate_snapshot(require_snapshot(freeze_astrostate(source)))
    assert legacy.succeeded and current.succeeded
    assert prepared_state_json_bytes(current.state) == prepared_state_json_bytes(legacy.state)
    assert tuple(current.state.capabilities) == (
        "aspects.basic_conjunction_list", "aspects.whole_sign_graph", "chart.lagna",
        "dignity.exaltation_facts", "planets.house_placement",
        "planets.normalized", "roles.functional",
    )


def test_career_yoga_and_snapshot_public_locks_remain_exact(tmp_path):
    source = mutable("surya_test_chart.json")
    career = compact(interpret_career(source))
    yoga = compact(evaluate_yoga_rules(source))
    assert (len(career), hashlib.sha256(career).hexdigest()) == (
        3495, "fee279260217eabb6a0f037d48d306888571fdf4c1c259630eca4337b5df9974",
    )
    assert (len(yoga), hashlib.sha256(yoga).hexdigest()) == (
        1361, "d6ad3c317cd8f5388e0630e528238f099910499a2863f9c14aab13e7b5de079e",
    )

    from systems.Parasara.tools.generate_snapshot import generate

    output = tmp_path / "snapshot.json"
    generate(str(FIXTURES / "golden_chart_01.json"), str(output))
    approved = ROOT / "systems" / "Parasara" / "tests" / "snapshots" / "output_golden_chart_01.json"
    assert output.read_bytes() == approved.read_bytes()
