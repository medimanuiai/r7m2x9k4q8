from __future__ import annotations

import builtins
from dataclasses import replace
import hashlib
import logging
import os
from pathlib import Path
import random
import socket
import time

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine import astrostate_api
from systems.Parasara.engine.astrostate_api import (
    AstroCapabilitySupply,
    AstroQueryResult,
    AstroStateBuildFailure,
    AstroStateBuildSuccess,
    AstroStateSnapshot,
    AspectFact,
    CapabilitySnapshot,
    CapabilityFactState,
    CapabilityReadiness,
    ConstructionIssue,
    DignityFact,
    StrengthFact,
    freeze_astrostate,
    require_snapshot,
)
from systems.Parasara.engine.capability import CapabilityInspection
from systems.Parasara.engine.enrichments import aspects as aspects_mod
from systems.Parasara.engine.enrichments import functional_roles as roles_mod
from systems.Parasara.engine.enrichments.yoga_engine import (
    build_yoga_snapshot,
    load_yoga_rule_source,
)
from systems.Parasara.engine.interpreters import career as career_mod
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.tools.varga_dump import dump_vargas
from tools import validate_prompt04


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"


def mutable(name: str = "surya_test_chart.json") -> AstroState:
    return chart_to_astrostate(SuryaAdapter.load(str(FIXTURES / name)))


def snapshot(name: str = "surya_test_chart.json") -> AstroStateSnapshot:
    return require_snapshot(freeze_astrostate(mutable(name)))


def minimal(*, lagna: str | None = "Aries", aspects=None) -> AstroState:
    aspect_value = [] if aspects is None else aspects
    return AstroState(
        metadata={}, location=None, lagna_sign=lagna,
        planets=[PlanetState(name="Mars", sign="Aries", degree=1.0, house=1)],
        houses=[], diagnostics={}, enrichments={"aspects": aspect_value}, derived=None,
    )


def assert_fatal_aspect_failure(
    outcome,
    *,
    code: str,
    capability_id: str,
    path: str = "$.enrichments.aspects",
) -> None:
    expected = ConstructionIssue(
        code=code, path=path, capability_id=capability_id,
        recoverable=False, fatal=True,
    )
    assert outcome == AstroStateBuildFailure(issues=(expected,))
    assert not hasattr(outcome, "snapshot")


def test_r1_public_constructors_and_replace_defensively_freeze_nested_values():
    state = snapshot()
    caller_context = {"instant": "2026-01-01T00:00:00Z"}
    replaced_context = replace(state, evaluation_context=caller_context)
    context_digest = replaced_context.logical_digest
    caller_context["instant"] = "2027-01-01T00:00:00Z"
    assert replaced_context.evaluation_context["instant"] == "2026-01-01T00:00:00Z"
    assert replaced_context.logical_digest == context_digest

    caller_metadata = {"nested": {"items": [1, 2]}}
    replaced_core = replace(state.core, metadata=caller_metadata)
    replaced_state = replace(state, core=replaced_core)
    core_digest = replaced_state.logical_digest
    caller_metadata["nested"]["items"].append(3)
    assert replaced_state.core.metadata["nested"]["items"] == (1, 2)
    assert replaced_state.logical_digest == core_digest
    with pytest.raises(TypeError):
        replaced_state.core.metadata["nested"]["new"] = True

    caller_value = {"nested": [1, {"value": 2}]}
    result = AstroQueryResult(
        capability_id="strengths.planet", capability_version="1.0.0",
        state=CapabilityFactState.PRESENT, entity_kind="planet", entity_id="Mars",
        value_present=True, value=caller_value, issues=(),
    )
    caller_value["nested"][1]["value"] = 9
    assert result.value["nested"][1]["value"] == 2
    with pytest.raises(TypeError):
        result.value["nested"][1]["value"] = 3

    strength_source = {"components": [1, {"nested": True}]}
    strength = StrengthFact(
        planet_id="Mars", value=strength_source,
        source_kind="test_source", factual_scope="test_scope",
    )
    strength_source["components"].append(2)
    assert strength.value["components"] == (1, astrostate_api.FrozenMap({"nested": True}))
    with pytest.raises(astrostate_api.AstroCanonicalValueError):
        StrengthFact(
            planet_id="Mars", value={"unsupported"},
            source_kind="test_source", factual_scope="test_scope",
        )

    source_capability = next(
        item for item in state.capabilities
        if item.capability_id == "strengths.planet"
    )
    capability_content = {"nested": ["original"]}
    capability = CapabilitySnapshot(
        capability_id=source_capability.capability_id,
        capability_version=source_capability.capability_version,
        readiness=CapabilityReadiness.READY,
        source_kind="test_source",
        content=capability_content,
        content_empty=False,
        issues=(),
        factual_scope=source_capability.factual_scope,
        core_path=None,
    )
    capability_content["nested"].append("changed")
    capability_list = [
        capability if item.capability_id == capability.capability_id else item
        for item in state.capabilities
    ]
    replaced_capability = replace(state, capabilities=capability_list)
    capability_digest = replaced_capability.logical_digest
    capability_list.clear()
    assert capability.content["nested"] == ("original",)
    assert replaced_capability.logical_digest == capability_digest


def test_r2_core_backed_supplies_are_always_rejected_and_order_independent():
    matching = freeze_astrostate(minimal(), capability_supplies=(AstroCapabilitySupply(
        capability_id="chart.lagna", capability_version="1.0.0",
        source_kind="test_supply", content="Aries",
    ),))
    conflicting = freeze_astrostate(minimal(), capability_supplies=(AstroCapabilitySupply(
        capability_id="chart.lagna", capability_version="1.0.0",
        source_kind="test_supply", content="Taurus",
    ),))
    absent = freeze_astrostate(minimal(lagna=None), capability_supplies=(AstroCapabilitySupply(
        capability_id="chart.lagna", capability_version="1.0.0",
        source_kind="test_supply", content="Aries",
    ),))
    for outcome in (matching, conflicting, absent):
        assert isinstance(outcome, AstroStateBuildFailure)
        assert outcome.issues[0].code == "core_capability_supply_not_allowed"
        assert outcome.issues[0].capability_id == "chart.lagna"

    supplies = (
        AstroCapabilitySupply(
            capability_id="chart.metadata", capability_version="1.0.0",
            source_kind="test_supply", content={"source": "test"},
        ),
        AstroCapabilitySupply(
            capability_id="chart.lagna", capability_version="1.0.0",
            source_kind="test_supply", content="Aries",
        ),
    )
    first = freeze_astrostate(minimal(), capability_supplies=supplies)
    second = freeze_astrostate(minimal(), capability_supplies=tuple(reversed(supplies)))
    assert first == second


def test_r3_whole_sign_aspects_map_target_sign_to_canonical_house():
    built = build_yoga_snapshot(mutable(), load_yoga_rule_source())
    assert isinstance(built, AstroStateBuildSuccess)
    state = built.snapshot
    assert state.get_house(10).value.sign == "Taurus"
    result = state.get_aspects_to_house(10, "whole_sign_graph")
    assert result.state is CapabilityFactState.PRESENT
    assert tuple((item.source_id, item.target_id, item.target_sign) for item in result.value) == (
        ("Saturn", "Mars", "Taurus"),
        ("Saturn", "Venus", "Taurus"),
    )
    assert state.get_aspects_to_house(10, "basic_conjunction_list").value == ()


def test_r3_aspect_query_inputs_and_invalid_supplied_identities_are_distinct():
    state = require_snapshot(freeze_astrostate(minimal(aspects=[])))
    assert state.get_aspects_from("Venus", "basic_conjunction_list").state is CapabilityFactState.ABSENT_ENTITY
    assert state.get_aspects_to_planet("Venus", "basic_conjunction_list").state is CapabilityFactState.ABSENT_ENTITY
    assert state.get_aspects_to_house(10, "basic_conjunction_list").state is CapabilityFactState.ABSENT_ENTITY
    with pytest.raises(ValueError):
        state.get_aspects_from("Mars", "invalid")
    with pytest.raises(TypeError):
        state.get_aspects_from("Mars")

    bad_source = freeze_astrostate(minimal(aspects=[{
        "from": "Pluto", "to": "Mars", "type": "conjunction",
    }]))
    assert_fatal_aspect_failure(
        bad_source, code="invalid_basic_aspect_content",
        capability_id="aspects.basic_conjunction_list",
    )

    bad_target = freeze_astrostate(minimal(aspects={
        "edges": [{
            "source": "Mars", "target": "Pluto", "aspect": "7th",
            "trace": {"target_sign": "Libra"},
        }],
        "config_version": "test-v1",
    }))
    assert_fatal_aspect_failure(
        bad_target, code="invalid_whole_sign_aspect_content",
        capability_id="aspects.whole_sign_graph",
    )


def test_r4_personal_export_protection_allows_absent_and_detects_mutation_or_deletion(tmp_path):
    absent_paths = (tmp_path / "missing-1.json", tmp_path / "missing-2.json")
    absent = validate_prompt04._personal_export_manifest(absent_paths)
    assert absent == ()
    assert validate_prompt04._personal_exports_unchanged(absent)

    protected = tmp_path / "personal.json"
    protected.write_bytes(b'{"value":1}')
    baseline = validate_prompt04._personal_export_manifest((protected,))
    assert validate_prompt04._personal_exports_unchanged(baseline)
    protected.write_bytes(b'{"value":2}')
    assert not validate_prompt04._personal_exports_unchanged(baseline)
    protected.write_bytes(b'{"value":1}')
    protected.unlink()
    assert not validate_prompt04._personal_exports_unchanged(baseline)

    renamed = tmp_path / "renamed.json"
    renamed.write_bytes(b'{"value":3}')
    rename_baseline = validate_prompt04._personal_export_manifest((renamed,))
    renamed.rename(tmp_path / "moved.json")
    assert not validate_prompt04._personal_exports_unchanged(rename_baseline)


@pytest.mark.parametrize(
    "unauthorized",
    (
        {"cache_hit": True}, {"duration_ms": 1.0}, {"logs": ["x"]},
        {"domain_output": {"career": {}}}, {"score": 0.5},
        {"confidence": 0.5}, {"request": {"raw": True}},
        {"instant": ["mutable"]},
    ),
)
def test_r5_evaluation_context_rejects_nonfactual_or_mutable_fields(unauthorized):
    source = mutable()
    baseline = require_snapshot(freeze_astrostate(source)).logical_digest
    failed = freeze_astrostate(source, evaluation_context=unauthorized)
    assert isinstance(failed, AstroStateBuildFailure)
    assert failed.issues[0].code == "invalid_evaluation_context"
    assert require_snapshot(freeze_astrostate(source)).logical_digest == baseline


def test_r6_success_issues_must_be_typed_unique_and_canonically_ordered():
    state = snapshot()
    a_issue = ConstructionIssue(code="a_issue", path="$.a")
    z_issue = ConstructionIssue(code="z_issue", path="$.z")
    with pytest.raises(ValueError):
        AstroStateBuildSuccess(snapshot=state, issues=(z_issue, a_issue))
    with pytest.raises(ValueError):
        AstroStateBuildSuccess(snapshot=state, issues=(a_issue, a_issue))
    with pytest.raises(TypeError):
        AstroStateBuildSuccess(snapshot=state, issues=("a_issue",))
    caller = [a_issue, z_issue]
    success = AstroStateBuildSuccess(snapshot=state, issues=caller)
    caller.clear()
    assert success.issues == (a_issue, z_issue)


@pytest.mark.parametrize(
    ("fixture", "byte_length", "digest"),
    (
        ("golden_chart_01.json", 5752, "f13f8ea89ba972d4936bc7e4547f4fe6d629cc1603943b02e92a311406086b98"),
        ("surya_test_chart.json", 20380, "0f82ee03920845d155cf299bea81fb9fab24e69fe3c94108101c9fa6e7d0a133"),
        ("surya_generated_chart.json", 19729, "c896599cd87358a2023e6a2937ffb281699f95b4e9a7c5850f2ee2fb6a3cc888"),
    ),
)
def test_r7_varga_dump_full_legacy_bytes_are_exact(tmp_path, fixture, byte_length, digest):
    output = tmp_path / "varga.json"
    dump_vargas(str(FIXTURES / fixture), str(output))
    payload = output.read_bytes()
    assert (len(payload), hashlib.sha256(payload).hexdigest()) == (byte_length, digest)


def test_r8_queries_have_no_io_environment_clock_random_logging_or_producer_calls(monkeypatch):
    state = snapshot()

    def unexpected(*_args, **_kwargs):
        raise AssertionError("query crossed a purity boundary")

    monkeypatch.setattr(builtins, "open", unexpected)
    monkeypatch.setattr(os, "getenv", unexpected)
    monkeypatch.setattr(time, "time", unexpected)
    monkeypatch.setattr(random, "random", unexpected)
    monkeypatch.setattr(socket, "create_connection", unexpected)
    monkeypatch.setattr(logging.Logger, "_log", unexpected)
    monkeypatch.setattr(aspects_mod, "compute_aspect_graph", unexpected)
    monkeypatch.setattr(roles_mod, "compute_functional_roles", unexpected)

    results = (
        state.get_planets(), state.get_houses(), state.get_lagna(),
        state.get_planet_house("Mars"), state.get_planet_dignity("Mars"),
        state.get_house_lord(10), state.get_occupants(10),
        state.get_aspects_from("Mars", "basic_conjunction_list"),
        state.get_aspects_to_planet("Mars", "basic_conjunction_list"),
        state.get_aspects_to_house(10, "basic_conjunction_list"),
        state.get_varga("D9"), state.get_planet_in_varga("Mars", "D9"),
        state.get_functional_role("Mars"), state.get_planet_strength("Mars"),
        state.get_shadbala("Mars"), state.get_current_dasha(),
        state.get_current_transits(), state.inspect_capability("planets.normalized"),
        state.inspect_capabilities(("planets.normalized", "dasha.current")),
        state.list_capabilities(),
    )
    assert len(results) == 20


def test_r9_unexpected_freeze_and_career_defects_propagate(monkeypatch):
    source = mutable()

    def invalid_programming_path(*_args, **_kwargs):
        raise ValueError("injected programming defect")

    monkeypatch.setattr(astrostate_api, "_ready_capability", invalid_programming_path)
    with pytest.raises(ValueError, match="injected programming defect"):
        freeze_astrostate(source)

    monkeypatch.undo()
    state = snapshot()

    def unexpected_query_defect(_self):
        raise RuntimeError("injected query defect")

    monkeypatch.setattr(AstroStateSnapshot, "get_planets", unexpected_query_defect)
    with pytest.raises(RuntimeError, match="injected query defect"):
        career_mod.prepare_career_snapshot(state)


def test_r2_snapshot_replacement_cannot_disagree_with_core_backed_lagna():
    state = require_snapshot(freeze_astrostate(minimal()))
    replaced_core = replace(state.core, lagna_sign=None)

    with pytest.raises(ValueError, match="chart.lagna.*contradicts AstroCore"):
        replace(state, core=replaced_core)


def test_r2_capability_constructor_and_replace_enforce_catalog_state_matrix():
    state = snapshot()
    owned = next(
        item for item in state.capabilities
        if item.capability_id == "strengths.planet"
    )
    lagna = next(
        item for item in state.capabilities
        if item.capability_id == "chart.lagna"
    )

    with pytest.raises(ValueError, match="ID must be in the general catalog"):
        CapabilitySnapshot(
            capability_id="unknown.capability", capability_version="1.0.0",
            readiness=CapabilityReadiness.MISSING, source_kind=None,
            content=None, content_empty=False, issues=("catalog_miss",),
            factual_scope="factual",
        )
    with pytest.raises(ValueError, match="requires nonempty content"):
        replace(owned, content=None)
    with pytest.raises(ValueError, match="does not permit ready-empty"):
        CapabilitySnapshot(
            capability_id="planets.house_placement",
            capability_version="1.0.0",
            readiness=CapabilityReadiness.READY_EMPTY,
            source_kind="planet_house_fields",
            content=(), content_empty=True, issues=(), factual_scope="factual",
        )
    with pytest.raises(ValueError, match="unready capability cannot carry factual content"):
        replace(
            owned, readiness=CapabilityReadiness.MALFORMED,
            content={"Mars": {}}, issues=("malformed_content",),
        )
    with pytest.raises(ValueError, match="unready capability requires"):
        replace(
            owned, readiness=CapabilityReadiness.MALFORMED,
            content=None, issues=(),
        )
    with pytest.raises(ValueError, match="version must match"):
        replace(owned, capability_version="2.0.0")
    with pytest.raises(ValueError, match="core reference"):
        replace(lagna, core_path="core.unknown")
    with pytest.raises(ValueError, match="independent content"):
        replace(lagna, content="Leo")

    for readiness, source_kind in (
        (CapabilityReadiness.MISSING, None),
        (CapabilityReadiness.MALFORMED, "test_source"),
        (CapabilityReadiness.VERSION_MISMATCH, "test_source"),
        (CapabilityReadiness.UNSUPPORTED, None),
    ):
        with pytest.raises(ValueError, match="content"):
            CapabilitySnapshot(
                capability_id="strengths.planet", capability_version="1.0.0",
                readiness=readiness, source_kind=source_kind,
                content={"Mars": {"value": 1}}, content_empty=False,
                issues=("fixed_unready_issue",), factual_scope="legacy_composite",
            )

    direct_core = CapabilitySnapshot(
        capability_id="chart.lagna", capability_version="1.0.0",
        readiness=CapabilityReadiness.READY, source_kind="core_reference",
        content=None, content_empty=False, issues=(), factual_scope="factual",
        core_path="core.lagna",
    )
    direct_ready = CapabilitySnapshot(
        capability_id="strengths.planet", capability_version="1.0.0",
        readiness=CapabilityReadiness.READY, source_kind="test_source",
        content={"Mars": {"value": 1}}, content_empty=False, issues=(),
        factual_scope="legacy_composite",
    )
    direct_ready_empty = CapabilitySnapshot(
        capability_id="aspects.basic_conjunction_list", capability_version="1.0.0",
        readiness=CapabilityReadiness.READY_EMPTY,
        source_kind="legacy_basic_conjunction_list", content=(),
        content_empty=True, issues=(), factual_scope="factual",
    )
    assert (direct_core.core_path, direct_ready.content_empty, direct_ready_empty.content) == (
        "core.lagna", False, (),
    )


def test_r2_factual_presence_flags_are_intrinsic_and_replace_safe():
    dignity = DignityFact(
        planet_id="Mars", value="own_sign", value_present=True,
        enriched_value=None, enriched_value_present=False,
        source_kind="planet_and_strength_rows",
    )
    with pytest.raises(ValueError, match="value presence flag"):
        DignityFact(
            planet_id="Mars", value=None, value_present=True,
            enriched_value=None, enriched_value_present=False,
            source_kind="planet_and_strength_rows",
        )
    with pytest.raises(ValueError, match="enriched dignity presence flag"):
        replace(dignity, enriched_value="exalted", enriched_value_present=False)
    with pytest.raises(ValueError, match="value presence flag"):
        replace(dignity, value_present=False)

    present = AstroQueryResult(
        capability_id="chart.lagna", capability_version="1.0.0",
        state=CapabilityFactState.PRESENT, entity_kind="chart", entity_id="lagna",
        value_present=True, value="Leo", issues=(),
    )
    with pytest.raises(ValueError, match="requires one issue-free value"):
        replace(present, value=None)
    with pytest.raises(ValueError, match="requires one issue-free value"):
        replace(present, value_present=False)


def test_r3_capability_inspection_content_empty_is_constructor_and_replace_safe():
    with pytest.raises(ValueError, match="ready content must be nonempty"):
        CapabilityInspection(
            capability_id="strengths.planet", expected_version="1.0.0",
            observed_version="1.0.0", readiness=CapabilityReadiness.READY,
            source_kind="test_source", content_empty=True, issues=(),
        )
    with pytest.raises(ValueError, match="explicitly empty"):
        CapabilityInspection(
            capability_id="aspects.basic_conjunction_list", expected_version="1.0.0",
            observed_version="1.0.0", readiness=CapabilityReadiness.READY_EMPTY,
            source_kind="test_source", content_empty=False, issues=(),
        )

    ready = CapabilityInspection(
        capability_id="strengths.planet", expected_version="1.0.0",
        observed_version="1.0.0", readiness=CapabilityReadiness.READY,
        source_kind="test_source", content_empty=False, issues=(),
    )
    ready_empty = CapabilityInspection(
        capability_id="aspects.basic_conjunction_list", expected_version="1.0.0",
        observed_version="1.0.0", readiness=CapabilityReadiness.READY_EMPTY,
        source_kind="test_source", content_empty=True, issues=(),
    )
    with pytest.raises(ValueError, match="ready content must be nonempty"):
        replace(ready, content_empty=True)
    with pytest.raises(ValueError, match="explicitly empty"):
        replace(ready_empty, content_empty=False)


@pytest.mark.parametrize(
    "aspects",
    (
        [{"from": "Venus", "to": "Mars", "type": "conjunction"}],
        {
            "edges": [{
                "source": "Venus", "target": "Mars", "aspect": "7th",
                "trace": {"target_sign": "Aries"},
            }],
            "config_version": "test-v1",
        },
    ),
)
def test_r3_canonical_but_absent_aspect_sources_are_fatal(aspects):
    capability_id = (
        "aspects.basic_conjunction_list"
        if isinstance(aspects, list)
        else "aspects.whole_sign_graph"
    )
    code = (
        "invalid_basic_aspect_content"
        if isinstance(aspects, list)
        else "invalid_whole_sign_aspect_content"
    )
    assert_fatal_aspect_failure(
        freeze_astrostate(minimal(aspects=aspects)),
        code=code, capability_id=capability_id,
    )


@pytest.mark.parametrize(
    "aspects",
    (
        [{"from": "Mars", "to": "Venus", "type": "conjunction"}],
        {
            "edges": [{
                "source": "Mars", "target": "Venus", "aspect": "7th",
                "trace": {"target_sign": "Libra"},
            }],
            "config_version": "test-v1",
        },
    ),
)
def test_r3_canonical_but_absent_planet_targets_are_fatal(aspects):
    capability_id = (
        "aspects.basic_conjunction_list"
        if isinstance(aspects, list)
        else "aspects.whole_sign_graph"
    )
    code = (
        "invalid_basic_aspect_content"
        if isinstance(aspects, list)
        else "invalid_whole_sign_aspect_content"
    )
    assert_fatal_aspect_failure(
        freeze_astrostate(minimal(aspects=aspects)),
        code=code, capability_id=capability_id,
    )


def test_r3_whole_sign_target_planet_must_agree_with_trace_sign():
    outcome = freeze_astrostate(minimal(aspects={
        "edges": [{
            "source": "Mars", "target": "Mars", "aspect": "7th",
            "trace": {"target_sign": "Libra"},
        }],
        "config_version": "test-v1",
    }))
    assert_fatal_aspect_failure(
        outcome, code="invalid_whole_sign_aspect_content",
        capability_id="aspects.whole_sign_graph",
    )


@pytest.mark.parametrize(
    ("aspects", "code", "capability_id"),
    (
        (
            [{"from": "Unknown", "to": "Mars", "type": "conjunction"}],
            "invalid_basic_aspect_content",
            "aspects.basic_conjunction_list",
        ),
        (
            {
                "edges": [{
                    "source": "Mars", "target": "Unknown", "aspect": "7th",
                    "trace": {"target_sign": "Aries"},
                }],
                "config_version": "test-v1",
            },
            "invalid_whole_sign_aspect_content",
            "aspects.whole_sign_graph",
        ),
        (
            {
                "edges": [{
                    "source": "Mars", "target": {"planet": "Mars"},
                    "aspect": "7th", "trace": {"target_sign": "Aries"},
                }],
                "config_version": "test-v1",
            },
            "invalid_whole_sign_aspect_content",
            "aspects.whole_sign_graph",
        ),
    ),
)
def test_r3_unknown_or_malformed_aspect_endpoints_are_fatal(
    aspects, code, capability_id,
):
    assert_fatal_aspect_failure(
        freeze_astrostate(minimal(aspects=aspects)),
        code=code, capability_id=capability_id,
    )


def test_r3_reordered_equivalent_invalid_aspects_have_identical_failure_output():
    invalid_rows = [
        {"from": "Venus", "to": "Mars", "type": "conjunction"},
        {"from": "Unknown", "to": "Mars", "type": "conjunction"},
    ]
    first = freeze_astrostate(minimal(aspects=invalid_rows))
    second = freeze_astrostate(minimal(aspects=list(reversed(invalid_rows))))
    assert first == second
    assert_fatal_aspect_failure(
        first, code="invalid_basic_aspect_content",
        capability_id="aspects.basic_conjunction_list",
    )


def test_r2_valid_aspect_entities_sign_house_empty_and_absent_queries_remain_distinct():
    basic = require_snapshot(freeze_astrostate(minimal(aspects=[{
        "from": "Mars", "to": "Mars", "type": "conjunction",
    }])))
    assert basic.get_aspects_from(
        "Mars", "basic_conjunction_list"
    ).state is CapabilityFactState.PRESENT

    whole_planet = require_snapshot(freeze_astrostate(minimal(aspects={
        "edges": [{
            "source": "Mars", "target": "Mars", "aspect": "7th",
            "trace": {"target_sign": "Aries"},
        }],
        "config_version": "test-v1",
    })))
    assert whole_planet.get_aspects_to_planet(
        "Mars", "whole_sign_graph"
    ).state is CapabilityFactState.PRESENT

    whole_source = minimal(aspects={
        "edges": [{
            "source": "Mars", "target": None, "aspect": "7th",
            "trace": {"target_sign": "Taurus"},
        }],
        "config_version": "test-v1",
    })
    whole_source.houses = [{"number": 10, "sign": "Taurus"}]
    whole = require_snapshot(freeze_astrostate(whole_source))
    sign_fact = whole.get_aspects_from("Mars", "whole_sign_graph").value[0]
    assert (sign_fact.target_kind, sign_fact.target_id, sign_fact.target_sign) == (
        "sign", "Taurus", "Taurus",
    )
    house = whole.get_aspects_to_house(10, "whole_sign_graph")
    assert house.state is CapabilityFactState.PRESENT and house.value == (sign_fact,)

    empty = require_snapshot(freeze_astrostate(minimal(aspects=[])))
    ready_empty = empty.get_aspects_from("Mars", "basic_conjunction_list")
    absent = empty.get_aspects_from("Venus", "basic_conjunction_list")
    assert ready_empty.state is CapabilityFactState.PRESENT and ready_empty.value == ()
    assert absent.state is CapabilityFactState.ABSENT_ENTITY and absent.value is None

    missing_source = minimal()
    missing_source.enrichments = {}
    missing = require_snapshot(freeze_astrostate(missing_source))
    missing_result = missing.get_aspects_from("Mars", "basic_conjunction_list")
    assert missing_result.state is CapabilityFactState.CAPABILITY_UNAVAILABLE


def test_r3_nonfatal_malformed_availability_remains_distinct_from_invalid_content():
    state = require_snapshot(freeze_astrostate(minimal()))
    original = next(
        item for item in state.capabilities
        if item.capability_id == "strengths.shadbala"
    )
    malformed = replace(
        original,
        readiness=CapabilityReadiness.MALFORMED,
        source_kind="legacy_strength_rows",
        issues=("producer_malformed",),
    )
    capabilities = tuple(
        malformed if item.capability_id == malformed.capability_id else item
        for item in state.capabilities
    )
    published = replace(state, capabilities=capabilities)
    assert published.inspect_capability(
        "strengths.shadbala"
    ).readiness is CapabilityReadiness.MALFORMED
    assert published.get_shadbala(
        "Mars"
    ).state is CapabilityFactState.MALFORMED_CAPABILITY


def test_r2_snapshot_replace_revalidates_aspect_entities():
    state = require_snapshot(freeze_astrostate(minimal(aspects=[])))
    original = next(
        item for item in state.capabilities
        if item.capability_id == "aspects.basic_conjunction_list"
    )
    invalid = replace(
        original,
        readiness=CapabilityReadiness.READY,
        content=({"from": "Venus", "to": "Mars", "type": "conjunction"},),
        content_empty=False,
    )
    capabilities = tuple(
        invalid if item.capability_id == invalid.capability_id else item
        for item in state.capabilities
    )
    with pytest.raises(ValueError, match="snapshot-owned planets"):
        replace(state, capabilities=capabilities)

    supplied = freeze_astrostate(minimal(), capability_supplies=(
        AstroCapabilitySupply(
            capability_id="aspects.basic_conjunction_list",
            capability_version="1.0.0", source_kind="test_supply",
            content=({"from": "Venus", "to": "Mars", "type": "conjunction"},),
        ),
    ))
    assert isinstance(supplied, AstroStateBuildFailure)
    assert supplied.issues[0].code == "invalid_capability_supply"


def test_r2_aspect_fact_representation_fields_are_constructor_and_replace_safe():
    basic = AspectFact(
        representation="basic_conjunction_list", source_kind="planet",
        source_id="Mars", target_kind="planet", target_id="Mars",
        target_sign=None, aspect_kind="conjunction", configuration_version=None,
    )
    with pytest.raises(ValueError, match="basic aspect representation"):
        replace(basic, target_sign="Aries")
    with pytest.raises(ValueError, match="requires a target sign"):
        replace(basic, representation="whole_sign_graph")

    whole = AspectFact(
        representation="whole_sign_graph", source_kind="planet",
        source_id="Mars", target_kind="sign", target_id="Aries",
        target_sign="Aries", aspect_kind="7th", configuration_version="test-v1",
    )
    with pytest.raises(ValueError, match="must match target_sign"):
        replace(whole, target_id="Libra")


def test_r2_canonical_career_runtime_errors_propagate_from_both_paths(monkeypatch):
    prepared = career_mod.prepare_career_facts(mutable())

    def fail_strong(*_args, **_kwargs):
        raise RuntimeError("injected strong defect")

    monkeypatch.setattr(career_mod, "_strong_evaluation", fail_strong)
    with pytest.raises(RuntimeError, match="injected strong defect"):
        career_mod.evaluate_career_batch(prepared)

    monkeypatch.undo()

    def fail_base(*_args, **_kwargs):
        raise RuntimeError("injected base defect")

    monkeypatch.setattr(career_mod, "_base_and_component_facts", fail_base)
    with pytest.raises(RuntimeError, match="injected base defect"):
        career_mod.evaluate_career_batch(prepared)


def test_r2_expected_career_factual_unavailability_remains_typed():
    source = minimal()
    source.planets[0].house = 10
    prepared = career_mod.prepare_career_facts(source)
    assert prepared.preparation_errors == ()

    batch = career_mod.evaluate_career_batch(prepared)
    mars = next(
        item for item in batch.candidates
        if item.definition.candidate_id == "strong_in_10_Mars"
    )
    assert mars.status is career_mod.PredicateStatus.MISSING_CAPABILITY
    assert mars.fact.errors[0].code == "missing_planet_strength_fact"
