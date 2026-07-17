#!/usr/bin/env python3
"""Bounded explicit WP17 determinism scenarios.

The runner writes artifacts only below ``--artifact-dir`` and emits one compact,
sorted JSON manifest on stdout.  It intentionally does not use pytest discovery.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.enrichments.yoga_engine import (
    YogaRuleSource,
    evaluate_yoga_batch,
    load_yoga_rule_source,
    prepare_legacy_yoga_state,
    project_yoga_compatibility,
    yoga_batch_from_full_json,
    yoga_batch_from_logical_json,
    yoga_batch_full_json_bytes,
    yoga_batch_logical_json_bytes,
)
from systems.Parasara.engine.interpreters.career import (
    evaluate_career_batch,
    interpret_career,
    prepare_career_facts,
)
from systems.Parasara.engine.interpreters.career_models import (
    career_evaluation_batch_from_json_bytes,
    career_evaluation_batch_full_json_bytes,
    career_evaluation_batch_logical_json_bytes,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules.canonical import (
    canonical_json_bytes,
    condition_result_from_full_json,
    condition_result_from_logical_json,
    condition_result_full_json_bytes,
    condition_result_logical_json_bytes,
    predicate_result_from_full_json,
    predicate_result_from_logical_json,
    predicate_result_full_json_bytes,
    predicate_result_logical_json_bytes,
    predicate_result_to_logical_data,
)
from systems.Parasara.engine.rules.conditions import ConditionEvaluator
from systems.Parasara.engine.rules.definition_validation import validate_yoga_rules
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.loader import (
    RULE_REGISTRY,
    load_rules_from_dir,
)
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    prepare_predicate_state,
    prepared_state_json_bytes,
)
from systems.Parasara.engine.rules.registry import get_production_registry
from systems.Parasara.engine.rules.yoga_loader import load_yoga_rules
from tests.testing_framework.generate_full_artifacts import run_rules_and_trace
from tests.testing_framework.rule_coverage import run_rule_coverage_scan


FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"
RULES = ROOT / "systems" / "Parasara" / "rules" / "parashara" / "v1"
YOGA_RULES = RULES / "yogas.yaml"
SCENARIO_ORDER = (
    "01.predicates.all_ids_statuses",
    "02.prepared.equivalent_states",
    "03.cache.cold_warm_alias",
    "04.cache.eviction_and_reevaluation",
    "05.conditions.nested_short_circuit",
    "06.yoga.explicit_permutations",
    "07.loaders.trigger_orders",
    "08.career.fixed_repeated_projection",
    "09.tooling.artifacts_and_coverage",
    "10.serialization.round_trip",
)


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _public_bytes(value) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    ).encode("utf-8")


def _astro(name="surya_test_chart.json"):
    return chart_to_astrostate(SuryaAdapter.load(str(FIXTURES / name)))


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


def _predicate_state():
    outcome = prepare_predicate_state(_predicate_source())
    if not outcome.succeeded or outcome.state is None:
        raise AssertionError("fixed predicate preparation failed")
    return outcome.state


def _record(name: str, logical: bytes, public: bytes | None = None, artifact: bytes | None = None):
    result = {
        "logical_byte_length": len(logical),
        "logical_sha256": _sha(logical),
        "name": name,
    }
    if public is not None:
        result["public_byte_length"] = len(public)
        result["public_sha256"] = _sha(public)
    if artifact is not None:
        result["artifact_byte_length"] = len(artifact)
        result["artifact_sha256"] = _sha(artifact)
    return result


def _predicate_scenario(_artifact_dir: Path):
    state = _predicate_state()
    registry = get_production_registry()
    matched = {
        "ASPECT": ({"from_planet": "Mars", "to_planet": "Moon"}, None),
        "ASPECT_EXISTS": ({"from_planet": "Mars", "to_planet": "Moon"}, None),
        "FUNCTIONAL_ROLE": ({"role_in": ["yogakaraka"]}, ("Mars",)),
        "HOUSE_OCCUPANT": ({"planet": "Moon", "house": 4}, None),
        "PLANET_EXALTED": ({"planet": "Sun"}, None),
        "PLANET_IN_HOUSE": ({"planet": "Mars", "house": 1}, None),
    }
    unmatched = {
        "ASPECT": ({"from_planet": "Moon", "to_planet": "Mars"}, None),
        "ASPECT_EXISTS": ({"from_planet": "Moon", "to_planet": "Mars"}, None),
        "FUNCTIONAL_ROLE": ({"role_in": ["malefic"]}, ("Mars",)),
        "HOUSE_OCCUPANT": ({"planet": "Moon", "house": 5}, None),
        "PLANET_EXALTED": ({"planet": "Moon"}, None),
        "PLANET_IN_HOUSE": ({"planet": "Mars", "house": 2}, None),
    }
    rows = []
    for invoked_id in registry.exposed_ids():
        for fixture, table in (("matched", matched), ("unmatched", unmatched)):
            parameters, selected = table[invoked_id]
            result = PredicateEvaluator().evaluate(
                invoked_id,
                parameters,
                state,
                PredicateEvaluationContext(selected_planets=selected),
            )
            expected_status = fixture
            if result.status.value != expected_status:
                raise AssertionError(
                    f"{invoked_id} {fixture} fixture produced {result.status.value}"
                )
            rows.append(
                {
                    "fixture": fixture,
                    "invoked_id": invoked_id,
                    "result": predicate_result_to_logical_data(result),
                }
            )
        invalid = PredicateEvaluator().evaluate(
            invoked_id,
            {"unknown_parameter": "fixed"},
            state,
            PredicateEvaluationContext(),
        )
        if invalid.status.value != "invalid_parameters":
            raise AssertionError(
                f"{invoked_id} nonfactual fixture produced {invalid.status.value}"
            )
        rows.append(
            {
                "fixture": "nonfactual",
                "invoked_id": invoked_id,
                "result": predicate_result_to_logical_data(invalid),
            }
        )
    logical = canonical_json_bytes(rows)
    return _record(SCENARIO_ORDER[0], logical)


def _prepared_scenario(_artifact_dir: Path):
    first = _predicate_state()
    second = _predicate_state()
    first_bytes = prepared_state_json_bytes(first)
    second_bytes = prepared_state_json_bytes(second)
    if first_bytes != second_bytes or first is second:
        raise AssertionError("equivalent independently prepared states diverged")
    return _record(SCENARIO_ORDER[1], first_bytes)


def _cache_cold_warm_scenario(_artifact_dir: Path):
    state = _predicate_state()
    evaluator = PredicateEvaluator(capacity=4)
    parameters = {"from_planet": "Mars", "to_planet": "Moon"}
    cold = evaluator.evaluate(
        "ASPECT", parameters, state, PredicateEvaluationContext()
    )
    warm = evaluator.evaluate(
        "ASPECT_EXISTS", parameters, state, PredicateEvaluationContext()
    )
    cold_bytes = predicate_result_logical_json_bytes(cold)
    warm_bytes = predicate_result_logical_json_bytes(warm)
    if cold_bytes != warm_bytes or cold.cache_hit or not warm.cache_hit:
        raise AssertionError("cold/warm alias identity diverged")
    logical = canonical_json_bytes(
        {
            "cache_size": evaluator.cache_size,
            "cold_sha256": _sha(cold_bytes),
            "warm_sha256": _sha(warm_bytes),
        }
    )
    return _record(SCENARIO_ORDER[2], logical)


def _cache_eviction_scenario(_artifact_dir: Path):
    state = _predicate_state()
    evaluator = PredicateEvaluator(capacity=2)
    calls = (
        ("PLANET_IN_HOUSE", {"planet": "Mars", "house": 1}),
        ("HOUSE_OCCUPANT", {"planet": "Moon", "house": 4}),
        ("PLANET_IN_HOUSE", {"planet": "Mars", "house": 2}),
    )
    outputs = [
        evaluator.evaluate(name, params, state, PredicateEvaluationContext())
        for name, params in calls
    ]
    reevaluated = evaluator.evaluate(
        calls[0][0], calls[0][1], state, PredicateEvaluationContext()
    )
    logical = canonical_json_bytes(
        {
            "capacity": evaluator.capacity,
            "cache_key_sha256": tuple(
                _sha(canonical_json_bytes({
                    "predicate_id": key.predicate_id,
                    "parameters_sha256": key.parameters_sha256,
                }))
                for key in evaluator.cache.keys()
            ),
            "outputs": tuple(
                _sha(predicate_result_logical_json_bytes(item))
                for item in (*outputs, reevaluated)
            ),
            "reevaluated_cache_hit": reevaluated.cache_hit,
            "size": evaluator.cache_size,
        }
    )
    return _record(SCENARIO_ORDER[3], logical)


def _condition_scenario(_artifact_dir: Path):
    state = _predicate_state()
    node = {
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
                                "type": "HOUSE_OCCUPANT",
                                "params": {"planet": "Moon", "house": 5},
                            }
                        ],
                    },
                    {"type": "HOUSE_OCCUPANT", "params": {"planet": "Moon", "house": 4}},
                ],
            },
            {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 2}},
            {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 1}},
        ],
    }
    result = ConditionEvaluator(PredicateEvaluator()).evaluate(
        node, state, PredicateEvaluationContext()
    )
    logical = condition_result_logical_json_bytes(result)
    return _record(SCENARIO_ORDER[4], logical)


def _yoga_scenario(_artifact_dir: Path):
    astro = _astro()
    original = load_yoga_rule_source()
    permutations = (
        ("normal", (0, 1, 2)),
        ("reverse", (2, 1, 0)),
        ("A", (0, 2, 1)),
        ("B", (1, 0, 2)),
        ("C", (1, 2, 0)),
    )
    logical_rows = []
    public_rows = []
    for label, indexes in permutations:
        records = tuple(original.records[index] for index in indexes)
        source_name = f"wp17-{label}.yaml"
        source = YogaRuleSource(
            source_name=source_name,
            records=records,
            validation=validate_yoga_rules(list(records), source_name=source_name),
        )
        preparation = prepare_legacy_yoga_state(astro, source)
        if not preparation.outcome.succeeded or preparation.outcome.state is None:
            raise AssertionError(f"Yoga permutation {label} did not prepare")
        batch = evaluate_yoga_batch(
            preparation.outcome.state,
            PredicateEvaluationContext(),
            source,
            predicate_evaluator=PredicateEvaluator(),
            compatibility_graph=preparation.compatibility_graph,
        )
        logical_bytes = yoga_batch_logical_json_bytes(batch)
        public_bytes = _public_bytes(project_yoga_compatibility(batch))
        logical_rows.append(
            {"label": label, "bytes": len(logical_bytes), "sha256": _sha(logical_bytes)}
        )
        public_rows.append(
            {"label": label, "bytes": len(public_bytes), "sha256": _sha(public_bytes)}
        )
    return _record(
        SCENARIO_ORDER[5],
        canonical_json_bytes(logical_rows),
        canonical_json_bytes(public_rows),
    )


def _loader_snapshot():
    return {
        "identity": id(RULE_REGISTRY),
        "ids": tuple(sorted(RULE_REGISTRY)),
        "rajayoga_source": Path(
            RULE_REGISTRY["rajayoga_naive"].get("_source_file", "")
        ).name,
    }


def _loader_scenario(_artifact_dir: Path):
    identity = id(RULE_REGISTRY)
    RULE_REGISTRY.clear()
    load_rules_from_dir(str(RULES))
    load_yoga_rules(str(YOGA_RULES))
    generic_then_yoga = _loader_snapshot()
    RULE_REGISTRY.clear()
    load_yoga_rules(str(YOGA_RULES))
    load_rules_from_dir(str(RULES))
    yoga_then_generic = _loader_snapshot()
    if generic_then_yoga["identity"] != identity or yoga_then_generic["identity"] != identity:
        raise AssertionError("loader registry identity was rebound")
    generic_then_yoga["identity"] = "preserved"
    yoga_then_generic["identity"] = "preserved"
    return _record(
        SCENARIO_ORDER[6],
        canonical_json_bytes(
            {
                "generic_then_yoga": generic_then_yoga,
                "yoga_then_generic": yoga_then_generic,
            }
        ),
    )


def _career_scenario(_artifact_dir: Path):
    logical_rows = []
    public_rows = []
    for fixture in (
        "golden_chart_01.json",
        "surya_test_chart.json",
        "surya_generated_chart.json",
    ):
        astro = _astro(fixture)
        prepared = prepare_career_facts(astro)
        first = evaluate_career_batch(prepared)
        second = evaluate_career_batch(prepared)
        first_logical = career_evaluation_batch_logical_json_bytes(first)
        second_logical = career_evaluation_batch_logical_json_bytes(second)
        first_public = _public_bytes(interpret_career(astro))
        second_public = _public_bytes(interpret_career(astro))
        if first_logical != second_logical or first_public != second_public:
            raise AssertionError(f"Career repetition diverged for {fixture}")
        logical_rows.append(
            {"fixture": fixture, "bytes": len(first_logical), "sha256": _sha(first_logical)}
        )
        public_rows.append(
            {"fixture": fixture, "bytes": len(first_public), "sha256": _sha(first_public)}
        )
    return _record(
        SCENARIO_ORDER[7],
        canonical_json_bytes(logical_rows),
        canonical_json_bytes(public_rows),
    )


def _tooling_scenario(artifact_dir: Path):
    astro = _astro("golden_chart_01.json")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    run_rules_and_trace(astro, artifact_dir)
    coverage_path = artifact_dir / "coverage.json"
    run_rule_coverage_scan(astro, str(coverage_path))
    rows = []
    combined = bytearray()
    for name in ("rule_traces.json", "career_rule_traces.json", "coverage.json"):
        payload = (artifact_dir / name).read_bytes()
        rows.append({"name": name, "bytes": len(payload), "sha256": _sha(payload)})
        combined.extend(name.encode("utf-8"))
        combined.extend(b"\0")
        combined.extend(payload)
    logical = canonical_json_bytes(rows)
    return _record(SCENARIO_ORDER[8], logical, artifact=bytes(combined))


def _serialization_scenario(_artifact_dir: Path):
    state = _predicate_state()
    predicate = PredicateEvaluator().evaluate(
        "PLANET_IN_HOUSE",
        {"planet": "Mars", "house": 1},
        state,
        PredicateEvaluationContext(),
    )
    condition = ConditionEvaluator(PredicateEvaluator()).evaluate(
        {
            "type": "AND",
            "children": [
                {"type": "PLANET_IN_HOUSE", "params": {"planet": "Mars", "house": 1}},
                {"type": "HOUSE_OCCUPANT", "params": {"planet": "Moon", "house": 4}},
            ],
        },
        state,
        PredicateEvaluationContext(),
    )
    astro = _astro()
    source = load_yoga_rule_source()
    preparation = prepare_legacy_yoga_state(astro, source)
    yoga = evaluate_yoga_batch(
        preparation.outcome.state,
        PredicateEvaluationContext(),
        source,
        predicate_evaluator=PredicateEvaluator(),
        compatibility_graph=preparation.compatibility_graph,
    )
    career = evaluate_career_batch(prepare_career_facts(astro))
    predicate_without_telemetry = predicate_result_from_logical_json(
        predicate_result_logical_json_bytes(predicate)
    )
    condition_without_telemetry = condition_result_from_logical_json(
        condition_result_logical_json_bytes(condition)
    )
    contracts = (
        (
            "predicate.logical",
            predicate_result_logical_json_bytes(predicate),
            predicate_result_from_logical_json,
            predicate_result_logical_json_bytes,
        ),
        (
            "predicate.full",
            predicate_result_full_json_bytes(predicate_without_telemetry),
            predicate_result_from_full_json,
            predicate_result_full_json_bytes,
        ),
        (
            "condition.logical",
            condition_result_logical_json_bytes(condition),
            condition_result_from_logical_json,
            condition_result_logical_json_bytes,
        ),
        (
            "condition.full",
            condition_result_full_json_bytes(condition_without_telemetry),
            condition_result_from_full_json,
            condition_result_full_json_bytes,
        ),
        (
            "yoga.logical",
            yoga_batch_logical_json_bytes(yoga),
            yoga_batch_from_logical_json,
            yoga_batch_logical_json_bytes,
        ),
        (
            "yoga.full",
            yoga_batch_full_json_bytes(yoga),
            yoga_batch_from_full_json,
            yoga_batch_full_json_bytes,
        ),
        (
            "career.logical",
            career_evaluation_batch_logical_json_bytes(career),
            lambda payload: career_evaluation_batch_from_json_bytes(payload, full=False),
            career_evaluation_batch_logical_json_bytes,
        ),
        (
            "career.full",
            career_evaluation_batch_full_json_bytes(career),
            lambda payload: career_evaluation_batch_from_json_bytes(payload, full=True),
            career_evaluation_batch_full_json_bytes,
        ),
    )
    rows = []
    for name, payload, parse, serialize in contracts:
        restored = serialize(parse(payload))
        if restored != payload:
            raise AssertionError(f"serialization round trip diverged: {name}")
        rows.append({"name": name, "bytes": len(payload), "sha256": _sha(payload)})
    return _record(SCENARIO_ORDER[9], canonical_json_bytes(rows))


SCENARIOS: tuple[Callable[[Path], dict], ...] = (
    _predicate_scenario,
    _prepared_scenario,
    _cache_cold_warm_scenario,
    _cache_eviction_scenario,
    _condition_scenario,
    _yoga_scenario,
    _loader_scenario,
    _career_scenario,
    _tooling_scenario,
    _serialization_scenario,
)


def build_manifest(artifact_dir: Path):
    records = tuple(
        scenario(artifact_dir / f"{index:02d}")
        for index, scenario in enumerate(SCENARIOS, start=1)
    )
    if tuple(item["name"] for item in records) != SCENARIO_ORDER:
        raise AssertionError("scenario manifest order changed")
    return {
        "manifest_version": "1.0.0",
        "scenarios": records,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=2)
    arguments = parser.parse_args(argv)
    if arguments.repeats < 2:
        raise SystemExit("--repeats must be at least 2")
    payloads = tuple(
        canonical_json_bytes(
            build_manifest(arguments.artifact_dir / f"repeat-{index:02d}")
        )
        for index in range(arguments.repeats)
    )
    if any(payload != payloads[0] for payload in payloads[1:]):
        baseline = json.loads(payloads[0])
        changed = json.loads(next(payload for payload in payloads[1:] if payload != payloads[0]))
        names = tuple(
            left["name"]
            for left, right in zip(baseline["scenarios"], changed["scenarios"])
            if left != right
        )
        raise AssertionError(f"same-process scenario manifests diverged: {names}")
    sys.stdout.buffer.write(payloads[0])
    sys.stdout.buffer.write(b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
