"""Runtime purity, mutation, telemetry, and safe-diagnostic enforcement."""

from __future__ import annotations

import builtins
from copy import deepcopy
import json
import os
from pathlib import Path
import random
import socket
import subprocess
from types import SimpleNamespace
import uuid

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.enrichments import aspects, functional_roles
from systems.Parasara.engine.enrichments.yoga_engine import (
    evaluate_yoga_batch,
    load_yoga_rule_source,
    prepare_legacy_yoga_state,
    project_yoga_compatibility,
    yoga_batch_logical_json_bytes,
    yoga_batch_to_logical_data,
)
from systems.Parasara.engine.interpreters.career import (
    evaluate_career_batch,
    prepare_career_facts,
    project_career_compatibility,
)
from systems.Parasara.engine.interpreters.career_models import (
    career_evaluation_batch_logical_json_bytes,
    career_evaluation_batch_to_logical_data,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules import conditions as conditions_module
from systems.Parasara.engine.rules import evaluator as evaluator_module
from systems.Parasara.engine.rules.canonical import (
    canonical_json_bytes,
    condition_result_logical_json_bytes,
    predicate_result_full_json_bytes,
    predicate_result_logical_json_bytes,
)
from systems.Parasara.engine.rules.conditions import ConditionEvaluator
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.models import (
    ConditionNodeDisposition,
    ConditionResult,
    PredicateResult,
    PredicateStatus,
)
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    prepare_predicate_state,
    prepared_state_json_bytes,
    prepared_state_sha256,
)
from systems.Parasara.engine.rules.registry import (
    get_production_registry,
    predicate_registry_fingerprint_bytes,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"


def _predicate_source():
    return SimpleNamespace(
        planets=[
            SimpleNamespace(name="Mars", sign="Aries", degree=12.0, house=1),
            SimpleNamespace(
                name="Moon",
                sign="Cancer",
                degree=4.0,
                house=4,
                flags={"exalted": False},
            ),
            SimpleNamespace(name="Sun", sign="Aries", degree=10.0, house=1),
        ],
        lagna_sign="Aries",
        enrichments={
            "aspects": {
                "edges": [
                    {
                        "source": "Mars",
                        "target": "Moon",
                        "aspect": "4th",
                        "kind": "whole_sign",
                    }
                ],
                "config_version": "legacy-v1",
            }
        },
        derived={"functional_roles": {"Mars": {"functional_role": "yogakaraka"}}},
        metadata={"exaltations": {"Sun": 10.0}},
        diagnostics={},
    )


def _prepared_predicate_state():
    outcome = prepare_predicate_state(_predicate_source())
    assert outcome.succeeded and outcome.state is not None
    return outcome.state


def _astro(name: str = "surya_test_chart.json"):
    return chart_to_astrostate(SuryaAdapter.load(str(FIXTURES / name)))


def _typed_yoga_fixture():
    astro = _astro()
    source = load_yoga_rule_source()
    preparation = prepare_legacy_yoga_state(astro, source)
    assert preparation.outcome.succeeded and preparation.outcome.state is not None
    return source, preparation


def _forbidden(name):
    def fail(*_args, **_kwargs):
        raise AssertionError(f"forbidden factual-boundary access: {name}")

    return fail


def _install_runtime_guards(monkeypatch):
    monkeypatch.setattr(builtins, "open", _forbidden("open"))
    for name in (
        "open",
        "read_bytes",
        "read_text",
        "write_bytes",
        "write_text",
        "glob",
        "rglob",
        "iterdir",
    ):
        monkeypatch.setattr(Path, name, _forbidden(f"Path.{name}"))
    monkeypatch.setattr(os, "getcwd", _forbidden("os.getcwd"))
    monkeypatch.setattr(os, "getenv", _forbidden("os.getenv"))
    monkeypatch.setattr(socket, "create_connection", _forbidden("network"))
    monkeypatch.setattr(subprocess, "Popen", _forbidden("subprocess"))
    monkeypatch.setattr(subprocess, "run", _forbidden("subprocess"))
    monkeypatch.setattr(random, "random", _forbidden("random"))
    monkeypatch.setattr(random, "randint", _forbidden("random"))
    monkeypatch.setattr(uuid, "uuid4", _forbidden("uuid4"))
    monkeypatch.setattr(aspects, "compute_aspect_graph", _forbidden("Aspect producer"))
    monkeypatch.setattr(
        functional_roles,
        "compute_functional_roles",
        _forbidden("functional-role producer"),
    )
    monkeypatch.setattr(SuryaAdapter, "load", _forbidden("raw Surya provider"))


def test_all_typed_factual_layers_are_io_provider_producer_and_mutation_free(monkeypatch):
    state = _prepared_predicate_state()
    state_bytes = prepared_state_json_bytes(state)
    state_digest = prepared_state_sha256(state)
    registry = get_production_registry()
    registry_identity = id(registry)
    registry_bytes = predicate_registry_fingerprint_bytes(registry)

    yoga_source, yoga_preparation = _typed_yoga_fixture()
    career_astro = _astro()
    career_before = deepcopy(career_astro.model_dump(mode="python"))
    career_prepared = prepare_career_facts(career_astro)

    cases = (
        ("ASPECT", {"from_planet": "Mars", "to_planet": "Moon"}, None),
        ("ASPECT_EXISTS", {"from_planet": "Moon", "to_planet": "Mars"}, None),
        ("PLANET_IN_HOUSE", {"planet": "Mars", "house": 1}, None),
        ("HOUSE_OCCUPANT", {"planet": "Moon", "house": 4}, None),
        ("FUNCTIONAL_ROLE", {"role_in": ["yogakaraka"]}, ("Mars",)),
        ("PLANET_EXALTED", {"planet": "Sun"}, None),
    )
    supplied = [(predicate_id, deepcopy(parameters), selected) for predicate_id, parameters, selected in cases]

    _install_runtime_guards(monkeypatch)

    evaluator = PredicateEvaluator(capacity=16)
    results = []
    for predicate_id, parameters, selected in supplied:
        before = deepcopy(parameters)
        result = evaluator.evaluate(
            predicate_id,
            parameters,
            state,
            PredicateEvaluationContext(selected_planets=selected),
        )
        assert isinstance(result, PredicateResult)
        assert parameters == before
        results.append(result)
    warm = evaluator.evaluate(
        "ASPECT_EXISTS",
        {"to_planet": "Moon", "from_planet": "Mars"},
        state,
        PredicateEvaluationContext(),
    )
    assert warm.cache_hit is True

    condition = ConditionEvaluator(PredicateEvaluator()).evaluate(
        {
            "type": "AND",
            "children": [
                {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 1}},
                {
                    "type": "OR",
                    "children": [
                        {"type": "HOUSE_OCCUPANT", "params": {"planet": "Moon", "house": 5}},
                        {
                            "type": "NOT",
                            "children": [
                                {
                                    "type": "PLANET_IN_HOUSE",
                                    "params": {"planet": "Mars", "house": 2},
                                }
                            ],
                        },
                    ],
                },
            ],
        },
        state,
        PredicateEvaluationContext(),
    )
    assert isinstance(condition, ConditionResult)
    assert all(
        child.disposition
        in (ConditionNodeDisposition.EVALUATED, ConditionNodeDisposition.SKIPPED)
        for child in condition.children
    )

    yoga = evaluate_yoga_batch(
        yoga_preparation.outcome.state,
        PredicateEvaluationContext(),
        yoga_source,
        predicate_evaluator=PredicateEvaluator(),
        compatibility_graph=yoga_preparation.compatibility_graph,
    )
    yoga_public = project_yoga_compatibility(yoga)
    career = evaluate_career_batch(career_prepared)
    career_public = project_career_compatibility(career)

    assert canonical_json_bytes(yoga_batch_to_logical_data(yoga))
    assert canonical_json_bytes(career_evaluation_batch_to_logical_data(career))
    assert isinstance(yoga_public, list) and isinstance(career_public, dict)
    assert prepared_state_json_bytes(state) == state_bytes
    assert prepared_state_sha256(state) == state_digest
    assert id(get_production_registry()) == registry_identity
    assert predicate_registry_fingerprint_bytes(registry) == registry_bytes
    assert career_astro.model_dump(mode="python") == career_before


def test_short_circuit_children_are_truthfully_skipped_without_execution():
    state = _prepared_predicate_state()
    result = ConditionEvaluator(PredicateEvaluator()).evaluate(
        {
            "type": "AND",
            "children": [
                {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 2}},
                {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 1}},
            ],
        },
        state,
        PredicateEvaluationContext(),
    )
    assert isinstance(result, ConditionResult)
    assert result.status is PredicateStatus.UNMATCHED
    assert result.children[0].disposition is ConditionNodeDisposition.EVALUATED
    assert result.children[1].disposition is ConditionNodeDisposition.SKIPPED
    assert result.children[1].result is None
    assert result.children[1].skip_reason == "and_short_circuit_unmatched"


def test_monotonic_telemetry_cannot_change_logical_or_public_output(monkeypatch):
    state = _prepared_predicate_state()
    parameters = {"planet": "Mars", "house": 1}

    ticks = iter((0, 1_000_000, 2_000_000, 5_000_000, 8_000_000, 13_000_000))
    monkeypatch.setattr(evaluator_module, "perf_counter_ns", lambda: next(ticks))
    first = PredicateEvaluator().evaluate(
        "PLANET_IN_HOUSE", parameters, state, PredicateEvaluationContext()
    )
    ticks = iter((0, 50_000_000))
    monkeypatch.setattr(evaluator_module, "perf_counter_ns", lambda: next(ticks))
    second = PredicateEvaluator().evaluate(
        "PLANET_IN_HOUSE", parameters, state, PredicateEvaluationContext()
    )
    assert first.evaluation_time_ms != second.evaluation_time_ms
    assert predicate_result_logical_json_bytes(first) == predicate_result_logical_json_bytes(second)

    node = {
        "type": "AND",
        "children": [
            {"type": "PLANET_IN_HOUSE", "params": parameters},
            {"type": "PLANET_IN_HOUSE", "params": parameters},
        ],
    }
    monkeypatch.setattr(evaluator_module, "perf_counter_ns", lambda: 0)
    monkeypatch.setattr(conditions_module, "perf_counter_ns", lambda: 0)
    condition_a = ConditionEvaluator(PredicateEvaluator()).evaluate(
        node, state, PredicateEvaluationContext()
    )
    monkeypatch.setattr(evaluator_module, "perf_counter_ns", lambda: 90_000_000)
    monkeypatch.setattr(conditions_module, "perf_counter_ns", lambda: 90_000_000)
    condition_b = ConditionEvaluator(PredicateEvaluator()).evaluate(
        node, state, PredicateEvaluationContext()
    )
    assert condition_result_logical_json_bytes(condition_a) == condition_result_logical_json_bytes(
        condition_b
    )

    yoga_source, yoga_preparation = _typed_yoga_fixture()
    yoga_a = evaluate_yoga_batch(
        yoga_preparation.outcome.state,
        PredicateEvaluationContext(),
        yoga_source,
        predicate_evaluator=PredicateEvaluator(),
        compatibility_graph=yoga_preparation.compatibility_graph,
    )
    yoga_b = evaluate_yoga_batch(
        yoga_preparation.outcome.state,
        PredicateEvaluationContext(),
        yoga_source,
        predicate_evaluator=PredicateEvaluator(),
        compatibility_graph=yoga_preparation.compatibility_graph,
    )
    assert yoga_batch_logical_json_bytes(yoga_a) == yoga_batch_logical_json_bytes(yoga_b)
    assert project_yoga_compatibility(yoga_a) == project_yoga_compatibility(yoga_b)


class _ExplodingEvaluator(PredicateEvaluator):
    def evaluate(self, *_args, **_kwargs):
        raise RuntimeError(
            "C:\\temporary\\owner\\secret.txt token=WP17_FAKE_TOKEN "
            "object at 0xDEADBEEF\nunstable"
        )


def test_adversarial_exception_text_never_reaches_typed_or_public_diagnostics():
    state = _prepared_predicate_state()
    condition = ConditionEvaluator(_ExplodingEvaluator()).evaluate(
        {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 1}},
        state,
        PredicateEvaluationContext(),
    )
    assert condition.status is PredicateStatus.ERROR

    career = evaluate_career_batch(
        prepare_career_facts(_astro("golden_chart_01.json")),
        evaluator=_ExplodingEvaluator(),
    )
    public = project_career_compatibility(career)
    payloads = (
        predicate_result_full_json_bytes(condition),
        career_evaluation_batch_logical_json_bytes(career),
        json.dumps(public, ensure_ascii=False).encode("utf-8"),
    )
    forbidden = (
        b"temporary",
        b"owner",
        b"secret",
        b"WP17_FAKE_TOKEN",
        b"0xDEADBEEF",
        b"RuntimeError",
        b"traceback",
        b"unstable",
    )
    for payload in payloads:
        assert all(token not in payload for token in forbidden)
