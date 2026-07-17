from __future__ import annotations

import ast
import builtins
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
import hashlib
import os
from pathlib import Path
import random
import socket
import subprocess
import sys
import time
from types import SimpleNamespace
import uuid

import pytest

from systems.Parasara.engine.rules.capabilities import (
    CapabilityFactState,
    CapabilityReadiness,
    CapabilityRequirement,
)
from systems.Parasara.engine.rules.prepared_state import (
    NORMALIZATION_COMPATIBILITY_VERSION,
    PREPARATION_CONTRACT_VERSION,
    PREPARED_STATE_SCHEMA_VERSION,
    SYSTEM_SCOPE,
    CapabilitySupply,
    EvaluationMode,
    PredicateEvaluationContext,
    PreparedAstroState,
    PreparedCapability,
    PreparedPlanet,
    PreparedStateVersions,
    context_canonical_bytes,
    context_canonical_projection,
    context_sha256,
    find_prepared_planet,
    inspect_prepared_capability,
    observe_prepared_exaltation_fact,
    observe_prepared_functional_role,
    observe_prepared_lagna,
    observe_prepared_planet,
    observe_prepared_planet_house,
    prepare_predicate_state,
    retrieve_prepared_aspects,
    state_canonical_bytes,
    state_canonical_projection,
    state_sha256,
)


CAP = {
    name: CapabilityRequirement(
        capability_id=name,
        capability_version="1.0.0",
        required=True,
        when_parameters_present=(),
    )
    for name in (
        "aspects.basic_conjunction_list",
        "aspects.whole_sign_graph",
        "chart.lagna",
        "dignity.exaltation_facts",
        "planets.house_placement",
        "planets.normalized",
        "roles.functional",
    )
}


def planet(name, *, sign="Aries", house=1, flags=None):
    value = SimpleNamespace(name=name, sign=sign, house=house, degree=12.5)
    if flags is not None:
        value.flags = flags
    return value


def astro(*, aspects=None, planets=None, lagna="Aries", roles=None, exaltations=None):
    return SimpleNamespace(
        planets=[planet("Sun"), planet("Moon", sign="Taurus", house=2)] if planets is None else planets,
        lagna_sign=lagna,
        enrichments={} if aspects is None else {"aspects": aspects},
        derived=None if roles is None else {"functional_roles": roles},
        metadata={} if exaltations is None else {"exaltations": exaltations},
        diagnostics={},
    )


def graph(edges=None):
    return {
        "edges": [
            {"source": "Sun", "target": "Moon", "aspect": "7th", "kind": "whole-sign", "trace": {"ignored": True}}
        ] if edges is None else edges,
        "by_planet": {"Sun": [{"diagnostic": True}]},
        "config_version": "legacy-v1",
    }


def prepared(source=None, *, supplies=None, versions=None):
    outcome = prepare_predicate_state(
        astro(
            aspects=graph(),
            roles={"Sun": {"functional_role": "benefic"}},
            exaltations={"Sun": 0},
        ) if source is None else source,
        capability_supplies=supplies,
        versions=versions,
    )
    assert outcome.succeeded is True
    assert outcome.state is not None
    assert outcome.issues == ()
    return outcome.state


def test_exact_models_versions_and_deep_immutability():
    assert PREPARED_STATE_SCHEMA_VERSION == "1.0.0"
    assert PREPARATION_CONTRACT_VERSION == "1.0.0"
    assert NORMALIZATION_COMPATIBILITY_VERSION == "1.0.0"
    assert SYSTEM_SCOPE == "parasara"
    assert [item.name for item in fields(PreparedPlanet)] == ["planet_id", "house", "sign"]
    assert {item.name for item in fields(PreparedCapability)} == {
        "capability_id", "capability_version", "observed_version", "readiness",
        "source_kind", "content_empty", "content", "issues",
    }
    state = prepared()
    assert state.planets[0].planet_id == "Sun"
    assert tuple(state.capabilities) == tuple(sorted(CAP))
    with pytest.raises((FrozenInstanceError, AttributeError)):
        state.lagna_sign = "Leo"
    with pytest.raises(TypeError):
        state.capabilities["chart.lagna"] = None
    with pytest.raises(TypeError):
        state.capabilities["roles.functional"].content["Sun"] = "malefic"


def test_prepared_capability_invariants_and_explicit_unsupported_request():
    with pytest.raises(ValueError):
        PreparedCapability(
            capability_id="chart.lagna", capability_version="1.0.0", observed_version="1.0.0",
            readiness=CapabilityReadiness.READY, source_kind="astro_lagna_sign",
            content_empty=True, content="Aries", issues=(),
        )
    with pytest.raises(ValueError):
        PreparedCapability(
            capability_id="planets.normalized", capability_version="1.0.0", observed_version="1.0.0",
            readiness=CapabilityReadiness.READY_EMPTY, source_kind="normalized_planets",
            content_empty=True, content=(), issues=(),
        )
    unsupported = PreparedCapability(
        capability_id="future.capability", capability_version="1.0.0", observed_version=None,
        readiness=CapabilityReadiness.UNSUPPORTED, source_kind=None,
        content_empty=False, content=None, issues=("catalog_miss",),
    )
    assert unsupported.readiness is CapabilityReadiness.UNSUPPORTED


@pytest.mark.parametrize("bad_house", [True, 0, 13, 1.0, "1"])
def test_prepared_planet_rejects_invalid_house(bad_house):
    with pytest.raises((TypeError, ValueError)):
        PreparedPlanet(planet_id="Sun", house=bad_house, sign="Aries")


def test_preparation_represents_ready_missing_and_malformed_without_failing():
    state = prepared(astro(planets=[planet("Sun", house=None)]))
    assert state.capabilities["planets.normalized"].readiness is CapabilityReadiness.READY
    assert state.capabilities["planets.house_placement"].readiness is CapabilityReadiness.MALFORMED
    assert state.capabilities["aspects.whole_sign_graph"].readiness is CapabilityReadiness.MISSING
    assert state.capabilities["chart.lagna"].readiness is CapabilityReadiness.READY


@pytest.mark.parametrize("bad_house", [True, 0, 13, 1.0, "1"])
def test_malformed_source_house_is_successfully_recorded_not_fatal(bad_house):
    outcome = prepare_predicate_state(astro(planets=[planet("Sun", house=bad_house)]))
    assert outcome.succeeded is True
    assert outcome.state.planets[0].house is None
    assert outcome.state.capabilities["planets.house_placement"].readiness is CapabilityReadiness.MALFORMED
    assert outcome.state.capabilities["planets.house_placement"].content is None


def test_fatal_preparation_has_no_state_and_safe_issue_only():
    outcome = prepare_predicate_state(None)
    assert outcome.succeeded is False
    assert outcome.state is None
    assert [issue.code for issue in outcome.issues] == ["invalid_preparation_input"]
    assert all(not hasattr(issue, "raw_value") for issue in outcome.issues)


def test_duplicate_planets_are_fatal():
    outcome = prepare_predicate_state(astro(planets=[planet("Sun"), planet("Sun")]))
    assert outcome.state is None
    assert [issue.code for issue in outcome.issues] == ["duplicate_planet_id"]


def test_all_seven_capabilities_and_representation_separation():
    graph_state = prepared()
    assert graph_state.capabilities["aspects.whole_sign_graph"].readiness is CapabilityReadiness.READY
    assert graph_state.capabilities["aspects.basic_conjunction_list"].readiness is CapabilityReadiness.MISSING
    edge = graph_state.capabilities["aspects.whole_sign_graph"].content["edges"][0]
    assert dict(edge) == {"aspect": "7th", "kind": "whole-sign", "source": "Sun", "target": "Moon"}
    assert "trace" not in edge
    assert "by_planet" not in graph_state.capabilities["aspects.whole_sign_graph"].content

    basic = [{"from": "Sun", "to": "Moon", "type": "conjunction", "reason": "same_sign"}]
    basic_state = prepared(astro(aspects=basic))
    assert basic_state.capabilities["aspects.basic_conjunction_list"].content[0]["reason"] == "same_sign"
    assert basic_state.capabilities["aspects.whole_sign_graph"].readiness is CapabilityReadiness.MISSING
    assert state_sha256(graph_state) != state_sha256(basic_state)


def test_aspect_empty_order_and_duplicates_are_semantic():
    empty = prepared(astro(aspects=graph([])))
    assert empty.capabilities["aspects.whole_sign_graph"].readiness is CapabilityReadiness.READY_EMPTY
    assert empty.capabilities["aspects.whole_sign_graph"].content["edges"] == ()
    a = {"source": "Sun", "target": "Moon", "aspect": "7th", "kind": "whole-sign"}
    b = {"source": "Moon", "target": "Sun", "aspect": "7th", "kind": "whole-sign"}
    assert state_sha256(prepared(astro(aspects=graph([a, b])))) != state_sha256(prepared(astro(aspects=graph([b, a]))))
    assert state_sha256(prepared(astro(aspects=graph([a])))) != state_sha256(prepared(astro(aspects=graph([a, a]))))


def test_roles_supply_policy_valid_empty_malformed_version_and_conflict():
    supplied = CapabilitySupply(
        capability_id="roles.functional", capability_version="1.0.0",
        source_kind="explicit_functional_roles", content={"sun": "benefic"},
    )
    state = prepared(astro(), supplies=(supplied,))
    assert state.capabilities["roles.functional"].content == {"Sun": "benefic"}
    empty = prepared(astro(), supplies=(CapabilitySupply(
        capability_id="roles.functional", capability_version="1.0.0",
        source_kind="explicit_functional_roles", content={},
    ),))
    assert empty.capabilities["roles.functional"].readiness is CapabilityReadiness.READY_EMPTY

    malformed = prepared(astro(), supplies=(CapabilitySupply(
        capability_id="roles.functional", capability_version="1.0.0",
        source_kind="explicit_functional_roles", content={"Sun": "unknown"},
    ),))
    assert malformed.capabilities["roles.functional"].readiness is CapabilityReadiness.MALFORMED
    mismatch = prepared(astro(), supplies=(CapabilitySupply(
        capability_id="roles.functional", capability_version="2.0.0",
        source_kind="explicit_functional_roles", content={"Sun": "benefic"},
    ),))
    assert mismatch.capabilities["roles.functional"].readiness is CapabilityReadiness.VERSION_MISMATCH
    conflict = prepared(astro(roles={"Sun": {"functional_role": "benefic"}}), supplies=(supplied,))
    assert conflict.capabilities["roles.functional"].readiness is CapabilityReadiness.MALFORMED
    assert conflict.capabilities["roles.functional"].issues == ("conflicting_supply",)


def test_unknown_and_duplicate_supplies_fail_safely():
    unknown = CapabilitySupply(
        capability_id="unknown.capability", capability_version="1.0.0",
        source_kind="explicit_test", content={},
    )
    outcome = prepare_predicate_state(astro(), capability_supplies=(unknown,))
    assert outcome.state is None
    assert outcome.issues[0].code == "unknown_capability_supply"
    role = CapabilitySupply(
        capability_id="roles.functional", capability_version="1.0.0",
        source_kind="explicit_test", content={},
    )
    duplicate = prepare_predicate_state(astro(), capability_supplies=(role, role))
    assert duplicate.state is None
    assert duplicate.issues[0].code == "duplicate_capability_supply"


def test_unsafe_canonical_compatibility_content_is_a_fatal_contract_failure():
    basic = [{"from": "Sun", "to": "Moon", "type": "conjunction", "unsafe": object()}]
    outcome = prepare_predicate_state(astro(aspects=basic))
    assert outcome.state is None
    assert outcome.issues[0].code == "unsafe_canonical_content"


@pytest.mark.parametrize("value", [False, 0, True, 12.5])
def test_exaltation_preserves_source_and_exact_false_zero_true_numeric(value):
    state = prepared(astro(exaltations={"Sun": value}))
    observation = observe_prepared_exaltation_fact(state, "Sun")
    assert observation.state is CapabilityFactState.PRESENT
    assert observation.value[0]["source_kind"] == "legacy_metadata_exaltations"
    assert type(observation.value[0]["value"]) is type(value)
    assert observation.value[0]["value"] == value


def test_exaltation_flags_empty_missing_malformed_and_conflict():
    flags = prepared(astro(planets=[planet("Sun", flags={"exalted": False})]))
    assert observe_prepared_exaltation_fact(flags, "Sun").value[0]["value"] is False
    empty = prepared(astro(exaltations={}))
    assert empty.capabilities["dignity.exaltation_facts"].readiness is CapabilityReadiness.READY_EMPTY
    missing = prepared(astro())
    assert missing.capabilities["dignity.exaltation_facts"].readiness is CapabilityReadiness.MISSING
    malformed = prepared(astro(exaltations={"Sun": float("nan")}))
    assert malformed.capabilities["dignity.exaltation_facts"].readiness is CapabilityReadiness.MALFORMED
    conflict = prepared(astro(planets=[planet("Sun", flags={"exalted": False})], exaltations={"Sun": 0}))
    assert conflict.capabilities["dignity.exaltation_facts"].readiness is CapabilityReadiness.MALFORMED
    assert conflict.capabilities["dignity.exaltation_facts"].issues == ("conflicting_sources",)


def test_queries_distinguish_absence_unavailability_and_preserve_values():
    state = prepared()
    assert find_prepared_planet(state, "Sun").house == 1
    assert find_prepared_planet(state, "Mars") is None
    assert observe_prepared_planet(state, "Sun").state is CapabilityFactState.PRESENT
    assert observe_prepared_planet(state, "Mars").state is CapabilityFactState.ABSENT_ENTITY
    assert observe_prepared_planet_house(state, "Sun").value == 1
    assert observe_prepared_planet_house(state, "Mars").state is CapabilityFactState.ABSENT_ENTITY
    assert observe_prepared_lagna(state).value == "Aries"
    assert observe_prepared_functional_role(state, "Sun").value == "benefic"
    assert observe_prepared_functional_role(state, "Moon").state is CapabilityFactState.ABSENT_ENTITY
    assert retrieve_prepared_aspects(state, CAP["aspects.whole_sign_graph"]).value["edges"]
    unavailable = prepared(astro(planets=[planet("Sun", house=None)]))
    assert observe_prepared_planet_house(unavailable, "Sun").state is CapabilityFactState.MALFORMED_CAPABILITY
    malformed_planets = prepared(astro(planets=[planet("Sun", sign="Unknown")]))
    assert observe_prepared_planet(malformed_planets, "Sun").state is CapabilityFactState.MALFORMED_CAPABILITY


def test_prepared_inspection_rehydrates_wp06_contract():
    state = prepared()
    inspection = inspect_prepared_capability(state, CAP["chart.lagna"])
    assert inspection.readiness is CapabilityReadiness.READY
    mismatch = CapabilityRequirement(
        capability_id="chart.lagna", capability_version="2.0.0", required=True,
        when_parameters_present=(),
    )
    assert inspect_prepared_capability(state, mismatch).readiness is CapabilityReadiness.VERSION_MISMATCH


def test_source_and_supply_mutation_cannot_change_prepared_state_or_digest():
    source = astro(aspects=graph(), roles={"Sun": {"functional_role": "benefic"}})
    original = deepcopy(source)
    role_content = {"Moon": "malefic"}
    supply = CapabilitySupply(
        capability_id="roles.functional", capability_version="1.0.0",
        source_kind="explicit_test", content=role_content,
    )
    state = prepared(source)
    supplied_state = prepared(astro(), supplies=(supply,))
    supplied_before = state_canonical_bytes(supplied_state)
    before = state_canonical_bytes(state)
    assert source == original
    assert not hasattr(source, "prepared_state_digest")
    source.planets[0].house = 12
    source.enrichments["aspects"]["edges"].reverse()
    source.diagnostics["telemetry"] = {"cache_hit": True}
    role_content["Moon"] = "benefic"
    assert state_canonical_bytes(state) == before
    assert state_canonical_bytes(supplied_state) == supplied_before


def test_state_projection_digest_mapping_order_and_exclusions():
    first = prepared(astro(
        aspects=graph(), roles={"Sun": {"functional_role": "benefic"}, "Moon": {"functional_role": "malefic"}},
        exaltations={"Sun": 0, "Moon": False},
    ))
    second_source = astro(
        aspects=graph(), roles={"Moon": {"functional_role": "malefic"}, "Sun": {"functional_role": "benefic"}},
        exaltations={"Moon": False, "Sun": 0},
    )
    second_source.diagnostics = {"timing": 99, "yogas": ["ignored"]}
    second_source.metadata["unrelated"] = {"public_output": True}
    second = prepared(second_source)
    assert state_canonical_projection(first) == state_canonical_projection(second)
    assert state_canonical_bytes(first) == state_canonical_bytes(second)
    assert state_sha256(first) == hashlib.sha256(state_canonical_bytes(first)).hexdigest()
    changed = prepared(astro(
        aspects=graph(), roles={"Sun": {"functional_role": "malefic"}, "Moon": {"functional_role": "malefic"}},
        exaltations={"Sun": 0, "Moon": False},
    ))
    assert state_sha256(changed) != state_sha256(first)
    versioned = prepared(versions=PreparedStateVersions(producer_version="1.0.1"))
    assert state_sha256(versioned) != state_sha256(prepared())


def test_exact_representative_state_and_context_bytes_and_hashes():
    state_bytes = state_canonical_bytes(prepared())
    assert len(state_bytes) == 2154
    assert hashlib.sha256(state_bytes).hexdigest() == "5cccec6fe9d5cb41d8e56c9d1ae52d4436db4c257d3e6a37969c7e07625912e6"
    context = PredicateEvaluationContext(selected_planets=("Moon", "Sun"))
    assert context_canonical_bytes(context) == (
        b'{"evaluation_instant":null,"evaluation_mode":"default",'
        b'"selected_planets":["Sun","Moon"],"system_scope":"parasara"}'
    )
    assert context_sha256(context) == "73eef377109216e800473466dc88474f193b07c431e0288ddd5d6605e20ebb05"


def test_fresh_process_state_and_context_hashes_match_parent():
    code = (
        "from tests.rules.test_prepared_astrostate import prepared;"
        "from systems.Parasara.engine.rules.prepared_state import "
        "PredicateEvaluationContext,state_sha256,context_sha256;"
        "print(state_sha256(prepared()));"
        "print(context_sha256(PredicateEvaluationContext(selected_planets=('Moon','Sun'))))"
    )
    output = subprocess.check_output([sys.executable, "-c", code], text=True).splitlines()
    assert output == [
        state_sha256(prepared()),
        context_sha256(PredicateEvaluationContext(selected_planets=("Moon", "Sun"))),
    ]


def test_context_none_empty_selected_and_exact_digest_contract():
    default = PredicateEvaluationContext()
    empty = PredicateEvaluationContext(selected_planets=())
    selected = PredicateEvaluationContext(selected_planets=(" moon ", "SUN"))
    assert default.system_scope == "parasara"
    assert default.evaluation_mode is EvaluationMode.DEFAULT
    assert default.selected_planets is None
    assert default.evaluation_instant is None
    assert empty.selected_planets == ()
    assert selected.selected_planets == ("Sun", "Moon")
    assert len({context_sha256(default), context_sha256(empty), context_sha256(selected)}) == 3
    assert context_sha256(default) == hashlib.sha256(context_canonical_bytes(default)).hexdigest()
    assert context_canonical_projection(default)["evaluation_instant"] is None


def test_context_duplicate_and_instant_validation():
    with pytest.raises(ValueError):
        PredicateEvaluationContext(selected_planets=("Sun", "sun"))
    with pytest.raises(ValueError):
        PredicateEvaluationContext(evaluation_instant=datetime(2026, 1, 1))
    with pytest.raises(ValueError):
        PredicateEvaluationContext(evaluation_instant=datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=1))))
    instant = datetime(2026, 1, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    context = PredicateEvaluationContext(evaluation_instant=instant)
    assert context_canonical_projection(context)["evaluation_instant"] == "2026-01-01T02:03:04.000005Z"


def test_programming_boundary_has_no_forbidden_imports_or_identity_serializers():
    path = Path(__file__).resolve().parents[2] / "systems/Parasara/engine/rules/prepared_state.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    forbidden = ("surya", "adapter", "normalizer", "enrichments", "domain", "astrostate")
    assert not any(part in item.lower() for item in imports for part in forbidden)
    for banned in ("id(", "repr(", "pickle", "default=str", "os.environ", "time.time", "uuid"):
        assert banned not in source


def test_preparation_calls_no_producer_io_time_random_cache_or_registry_mutation(monkeypatch):
    from systems.Parasara.engine.enrichments import aspects, functional_roles, planet_strengths, varga
    from systems.Parasara.engine.rules.capabilities import capability_catalog_fingerprint_bytes
    from systems.Parasara.engine.rules.registry import predicate_registry_fingerprint_bytes

    def forbidden(*args, **kwargs):
        raise AssertionError("forbidden boundary invoked")

    catalog_before = capability_catalog_fingerprint_bytes()
    registry_before = predicate_registry_fingerprint_bytes()
    for owner, name in (
        (aspects, "compute_aspect_graph"),
        (aspects, "compute_basic_aspects"),
        (functional_roles, "compute_functional_roles"),
        (planet_strengths, "compute_planet_strengths"),
        (varga, "integrate_vargas_into_astro"),
        (builtins, "open"),
        (Path, "open"),
        (os, "getenv"),
        (time, "time"),
        (random, "random"),
        (uuid, "uuid4"),
        (subprocess, "run"),
        (socket, "socket"),
    ):
        monkeypatch.setattr(owner, name, forbidden)

    outcome = prepare_predicate_state(astro(aspects=graph()))
    assert outcome.succeeded is True
    assert capability_catalog_fingerprint_bytes() == catalog_before
    assert predicate_registry_fingerprint_bytes() == registry_before
