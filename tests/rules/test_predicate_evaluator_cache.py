"""WP09 instance-owned canonical evaluator and bounded-cache contract."""

from __future__ import annotations

import ast
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, replace
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from systems.Parasara.engine.astrostate import AstroState
from systems.Parasara.engine.rules import evaluator as evaluator_module
from systems.Parasara.engine.rules.canonical import (
    predicate_result_logical_json_bytes,
    predicate_result_logical_sha256,
)
from systems.Parasara.engine.rules.capabilities import CapabilityReadiness
from systems.Parasara.engine.rules.evaluator import (
    DEFAULT_CACHE_CAPACITY,
    PredicateCacheKey,
    PredicateEvaluator,
    PredicateResultCache,
    build_predicate_cache_key,
    predicate_cache_key_json_bytes,
    predicate_cache_key_sha256,
    predicate_cache_key_to_data,
    predicate_definition_fingerprint_sha256,
)
from systems.Parasara.engine.rules.models import (
    PredicateError,
    PredicateResult,
    PredicateStatus,
)
from systems.Parasara.engine.rules.parameters import ParameterSchema
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    PreparedAstroState,
    PreparedStateVersions,
    prepare_predicate_state,
)
from systems.Parasara.engine.rules.registry import (
    CostClass,
    PredicateDefinition,
    get_production_registry,
)


def planet(name="Mars", *, house=1, sign="Aries"):
    return SimpleNamespace(name=name, house=house, sign=sign, degree=12.0)


def source(*, planets=None):
    return SimpleNamespace(
        planets=[planet()] if planets is None else planets,
        lagna_sign="Aries",
        enrichments={},
        derived=None,
        metadata={},
        diagnostics={},
    )


def prepared(value=None, *, versions=None) -> PreparedAstroState:
    outcome = prepare_predicate_state(
        source() if value is None else value,
        versions=versions,
    )
    assert outcome.succeeded and outcome.state is not None
    return outcome.state


def context(**kwargs):
    return PredicateEvaluationContext(**kwargs)


def evaluate(evaluator, params=None, state=None, ctx=None, **kwargs):
    return evaluator.evaluate(
        "PLANET_IN_HOUSE",
        {"planet": "Mars", "house": 1} if params is None else params,
        prepared() if state is None else state,
        context() if ctx is None else ctx,
        **kwargs,
    )


def canonical_result(status: PredicateStatus) -> PredicateResult:
    errors = ()
    if status is PredicateStatus.ERROR:
        errors = (
            PredicateError(
                code="controlled_error",
                message="Controlled canonical error.",
                predicate_id="PLANET_IN_HOUSE",
                details={},
                recoverable=False,
            ),
        )
    return PredicateResult(
        matched=status is PredicateStatus.MATCHED,
        predicate_id="PLANET_IN_HOUSE",
        predicate_version="1.0.0",
        inputs={"planet": "Mars", "house": 1},
        evidence={} if status not in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED) else {"controlled": True},
        trace_steps=(),
        errors=errors,
        cache_hit=False,
        evaluation_time_ms=None,
        status=status,
    )


def key_for(params=None, state=None) -> PredicateCacheKey:
    definition = get_production_registry().lookup("PLANET_IN_HOUSE")
    assert definition is not None
    supplied = {"planet": "Mars", "house": 1} if params is None else params
    validation = definition.parameter_schema.validate(supplied)
    assert validation.valid and validation.normalized_inputs is not None
    return build_predicate_cache_key(
        definition,
        validation.normalized_inputs,
        prepared() if state is None else state,
        relevant_context={},
    )


@pytest.mark.parametrize("capacity", [None, 0, -1, True, False, 1.5, "2"])
def test_capacity_requires_positive_non_boolean_integer(capacity):
    if capacity is None:
        cache = PredicateResultCache()
        assert cache.capacity == DEFAULT_CACHE_CAPACITY == 256
    else:
        with pytest.raises((TypeError, ValueError)):
            PredicateResultCache(capacity=capacity)


def test_key_exact_projection_normalization_state_equivalence_and_context_neutrality():
    evaluator = PredicateEvaluator()
    first_state = prepared(source(planets=[planet(house=1)]))
    second_state = prepared(source(planets=[planet(house=1)]))
    cold = evaluator.evaluate(
        " planet_in_house ",
        {"planet": "  mars ", "house": 1},
        first_state,
        context(selected_planets=None),
    )
    warm = evaluator.evaluate(
        "PLANET_IN_HOUSE",
        {"house": 1, "planet": "MARS"},
        second_state,
        context(selected_planets=("Moon",)),
    )
    assert cold.cache_hit is False and warm.cache_hit is True
    key = evaluator.cache.keys()[0]
    assert key.system_scope == "parasara"
    assert key.predicate_id == "PLANET_IN_HOUSE"
    assert key.predicate_version == "1.0.0"
    assert key.context_relevance == "none"
    assert dict(predicate_cache_key_to_data(key)) == {
        "context_relevance": "none",
        "definition_sha256": "74fa61910959bea7c312b896a094242638d1cc78d6c5a8d0dbb2967f8f614931",
        "parameters_sha256": "dac54eff78852dde032b18e5eed96ef3102bfd69ede508290d7cf924a1edc2e0",
        "predicate_id": "PLANET_IN_HOUSE",
        "predicate_version": "1.0.0",
        "prepared_state_sha256": "e013c661bb60a5800e9a2037edacd64ac4db97ee8e2a72ebf916560750ad771f",
        "relevant_context_sha256": "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        "system_scope": "parasara",
    }
    assert len(predicate_cache_key_json_bytes(key)) == 473
    assert predicate_cache_key_sha256(key) == "44a01a332388f6f6e30219012e66ebd797b8749e99e04a6c80819f43718ed7d9"
    assert predicate_cache_key_sha256(key) == hashlib.sha256(predicate_cache_key_json_bytes(key)).hexdigest()


def test_key_isolates_parameters_facts_and_prepared_versions():
    base = key_for()
    changed_parameter = key_for({"planet": "Mars", "house": 2})
    changed_fact = key_for(state=prepared(source(planets=[planet(house=2)])))
    changed_versions = key_for(
        state=prepared(
            versions=PreparedStateVersions(
                schema_version="1.0.1",
                producer_version="1.0.1",
                normalization_version="1.0.1",
            )
        )
    )
    assert len({base, changed_parameter, changed_fact, changed_versions}) == 4
    assert len({predicate_cache_key_sha256(item) for item in (base, changed_parameter, changed_fact, changed_versions)}) == 4


def test_key_isolates_capability_readiness_observed_version_and_source_kind():
    state = prepared()
    placement = state.capabilities["planets.house_placement"]

    def with_placement(value):
        capabilities = dict(state.capabilities)
        capabilities["planets.house_placement"] = value
        return replace(state, capabilities=capabilities)

    malformed = with_placement(
        replace(
            placement,
            readiness=CapabilityReadiness.MALFORMED,
            content=None,
            issues=("controlled_malformed",),
        )
    )
    versioned = with_placement(
        replace(
            placement,
            observed_version="2.0.0",
            readiness=CapabilityReadiness.VERSION_MISMATCH,
            content=None,
            issues=("controlled_version",),
        )
    )
    sourced = with_placement(replace(placement, source_kind="prepared_override"))
    keys = (key_for(state=state), key_for(state=malformed), key_for(state=versioned), key_for(state=sourced))
    assert len(set(keys)) == 4
    assert len({item.prepared_state_sha256 for item in keys}) == 4


def test_key_format_supports_explicit_future_context_relevance():
    definition = get_production_registry().lookup("PLANET_IN_HOUSE")
    assert definition is not None
    validation = definition.parameter_schema.validate({"planet": "Mars", "house": 1})
    assert validation.valid and validation.normalized_inputs is not None
    state = prepared()
    neutral = build_predicate_cache_key(
        definition,
        validation.normalized_inputs,
        state,
        relevant_context={},
    )
    selected = build_predicate_cache_key(
        definition,
        validation.normalized_inputs,
        state,
        relevant_context={"selected_planets": ("Mars",)},
        context_relevance="selected_planets",
    )
    assert neutral != selected
    assert neutral.context_relevance == "none"
    assert selected.context_relevance == "selected_planets"


def test_definition_fingerprint_covers_schema_requirements_and_version():
    original = get_production_registry().lookup("PLANET_IN_HOUSE")
    assert original is not None
    schema = ParameterSchema(
        predicate_id="PLANET_IN_HOUSE",
        schema_version="2.0.0",
        specifications=original.parameter_schema.specifications,
    )
    changed = PredicateDefinition(
        predicate_id="PLANET_IN_HOUSE",
        predicate_version="2.0.0",
        description=original.description,
        parameter_schema=schema,
        required_capabilities=original.required_capabilities,
        cacheable=original.cacheable,
        deterministic=original.deterministic,
        cost_class=CostClass.LOW,
        system_scope=original.system_scope,
        handler=original.handler,
    )
    reordered_schema = ParameterSchema(
        predicate_id="PLANET_IN_HOUSE",
        schema_version="1.0.0",
        specifications=tuple(reversed(original.parameter_schema.specifications)),
    )
    schema_changed = replace(original, parameter_schema=reordered_schema)
    requirements_changed = replace(original, required_capabilities=original.required_capabilities[1:])
    fingerprints = {
        predicate_definition_fingerprint_sha256(item)
        for item in (original, changed, schema_changed, requirements_changed)
    }
    assert len(fingerprints) == 4
    assert predicate_definition_fingerprint_sha256(original) == "74fa61910959bea7c312b896a094242638d1cc78d6c5a8d0dbb2967f8f614931"


def test_invalid_or_unsafe_parameters_never_reach_key_builder(monkeypatch):
    monkeypatch.setattr(
        evaluator_module,
        "build_predicate_cache_key",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("key construction must be skipped")),
    )
    cyclic = []
    cyclic.append(cyclic)
    evaluator = PredicateEvaluator()
    for params in ({"planet": "Mars", "house": True}, {"planet": cyclic, "house": 1}):
        result = evaluate(evaluator, params=params)
        assert result.status is PredicateStatus.INVALID_PARAMETERS
        assert result.cache_hit is False
    assert evaluator.cache_size == 0


def test_cold_warm_results_are_logically_identical_and_telemetry_is_fresh(monkeypatch):
    durations = iter((3.0, 0.25))
    monkeypatch.setattr(evaluator_module, "_elapsed_milliseconds", lambda _start: next(durations))
    evaluator = PredicateEvaluator()
    cold = evaluate(evaluator)
    warm = evaluate(evaluator)
    assert cold == warm
    assert cold.cache_hit is False and warm.cache_hit is True
    assert cold.evaluation_time_ms == 3.0
    assert warm.evaluation_time_ms == 0.25
    assert predicate_result_logical_json_bytes(cold) == predicate_result_logical_json_bytes(warm)
    assert predicate_result_logical_sha256(cold) == predicate_result_logical_sha256(warm)
    assert evaluator.cache.peek(key_for()).evaluation_time_ms is None
    assert evaluator.cache.peek(key_for()).cache_hit is False


def test_cache_bypass_is_cold_and_does_not_touch_storage_or_recency():
    evaluator = PredicateEvaluator(capacity=2)
    evaluate(evaluator, params={"planet": "Mars", "house": 1})
    before = evaluator.cache.keys()
    bypassed = evaluate(
        evaluator,
        params={"planet": "Mars", "house": 2},
        use_cache=False,
    )
    assert bypassed.cache_hit is False
    assert evaluator.cache.keys() == before


@pytest.mark.parametrize(
    "status",
    [
        PredicateStatus.MISSING_CAPABILITY,
        PredicateStatus.INVALID_PARAMETERS,
        PredicateStatus.ERROR,
        PredicateStatus.TIMEOUT,
        PredicateStatus.SKIPPED,
    ],
)
def test_cache_rejects_every_noncacheable_status(status):
    cache = PredicateResultCache(capacity=2)
    assert cache.put(key_for(), canonical_result(status)) is False
    assert cache.size == 0


def test_matched_and_unmatched_are_cached_but_missing_and_error_reexecute(monkeypatch):
    evaluator = PredicateEvaluator()
    matched = evaluate(evaluator)
    assert matched.status is PredicateStatus.MATCHED and evaluator.cache_size == 1
    unmatched = evaluate(evaluator, params={"planet": "Mars", "house": 2})
    assert unmatched.status is PredicateStatus.UNMATCHED and evaluator.cache_size == 2

    missing_evaluator = PredicateEvaluator()
    missing_state = prepared(source(planets=[]))
    first = evaluate(missing_evaluator, state=missing_state)
    second = evaluate(missing_evaluator, state=missing_state)
    assert first.status is second.status is PredicateStatus.MISSING_CAPABILITY
    assert not first.cache_hit and not second.cache_hit and missing_evaluator.cache_size == 0

    calls = 0
    real_invoke = evaluator_module._invoke_handler

    def fail_then_recover(definition, parameters, state, ctx):
        nonlocal calls
        calls += 1
        return canonical_result(PredicateStatus.ERROR) if calls == 1 else real_invoke(definition, parameters, state, ctx)

    monkeypatch.setattr(evaluator_module, "_invoke_handler", fail_then_recover)
    recovering = PredicateEvaluator()
    failed = evaluate(recovering)
    repaired = evaluate(recovering)
    assert failed.status is PredicateStatus.ERROR and repaired.status is PredicateStatus.MATCHED
    assert calls == 2 and recovering.cache_size == 1


def test_lru_eviction_hit_promotion_replacement_and_noncacheable_neutrality():
    cache = PredicateResultCache(capacity=2)
    one, two, three = (key_for({"planet": "Mars", "house": value}) for value in (1, 2, 3))
    assert cache.put(one, canonical_result(PredicateStatus.MATCHED))
    assert cache.put(two, canonical_result(PredicateStatus.UNMATCHED))
    assert cache.keys() == (one, two)
    assert cache.get(one) is not None
    assert cache.keys() == (two, one)
    assert cache.put(one, canonical_result(PredicateStatus.MATCHED))
    assert cache.size == 2 and cache.keys() == (two, one)
    assert not cache.put(three, canonical_result(PredicateStatus.ERROR))
    assert cache.keys() == (two, one)
    assert cache.put(three, canonical_result(PredicateStatus.UNMATCHED))
    assert cache.keys() == (one, three)
    assert cache.peek(two) is None


def test_clear_freeze_and_instance_isolation():
    first = PredicateEvaluator(capacity=2)
    second = PredicateEvaluator(capacity=2)
    evaluate(first)
    assert first.cache_size == 1 and second.cache_size == 0
    first.freeze_cache()
    first.freeze_cache()
    assert first.cache_frozen is True
    assert evaluate(first).cache_hit is True
    miss = evaluate(first, params={"planet": "Mars", "house": 2})
    assert miss.cache_hit is False and first.cache_size == 1
    first.clear_cache()
    first.clear_cache()
    assert first.cache_size == 0 and first.cache_frozen is True
    assert evaluate(first).cache_hit is False and first.cache_size == 0


def test_concurrent_operations_preserve_capacity_and_single_canonical_value():
    evaluator = PredicateEvaluator(capacity=3)

    def operation(index):
        if index == 7:
            evaluator.freeze_cache()
        elif index == 11:
            evaluator.clear_cache()
        return evaluate(evaluator, params={"planet": "Mars", "house": index % 4 + 1})

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = tuple(pool.map(operation, range(40)))
    assert all(isinstance(item, PredicateResult) for item in results)
    assert evaluator.cache_size <= evaluator.capacity == 3
    assert len(set(evaluator.cache.keys())) == evaluator.cache_size


def test_unknown_mutable_and_newly_migrated_routes_are_typed():
    evaluator = PredicateEvaluator()
    unknown = evaluator.evaluate("UNKNOWN_TEST", {}, prepared(), context())
    occupant = evaluator.evaluate("HOUSE_OCCUPANT", {"planet": "Mars", "house": 1}, prepared(), context())
    alias = evaluator.evaluate("ASPECT", {}, prepared(), context())
    canonical_alias_target = evaluator.evaluate("ASPECT_EXISTS", {}, prepared(), context())
    mutable = evaluator.evaluate(
        "PLANET_IN_HOUSE",
        {"planet": "Mars", "house": 1},
        AstroState(metadata={}, location=None, lagna_sign=None, planets=[], houses=[]),
        context(),
    )
    assert [item.status for item in (unknown, mutable)] == [
        PredicateStatus.ERROR,
        PredicateStatus.ERROR,
    ]
    assert [item.errors[0].code for item in (unknown, mutable)] == [
        "unknown_predicate",
        "canonical_boundary_type_mismatch",
    ]
    assert occupant.status is PredicateStatus.MATCHED
    assert alias.status is canonical_alias_target.status is PredicateStatus.MISSING_CAPABILITY
    assert alias.errors[0].code == canonical_alias_target.errors[0].code == "missing_capability"
    assert alias.predicate_id == canonical_alias_target.predicate_id == "ASPECT_EXISTS"
    assert evaluator.cache_size == 1


def test_planet_in_house_routes_through_wp08_without_exposing_mutable_cache(monkeypatch):
    calls = 0
    original = evaluator_module._invoke_handler

    def spy(definition, parameters, state, ctx):
        nonlocal calls
        calls += 1
        return original(definition, parameters, state, ctx)

    monkeypatch.setattr(evaluator_module, "_invoke_handler", spy)
    evaluator = PredicateEvaluator()
    first = evaluate(evaluator)
    second = evaluate(evaluator)
    assert calls == 1 and first == second
    assert isinstance(evaluator.cache.keys(), tuple)
    with pytest.raises(FrozenInstanceError):
        evaluator.cache.keys()[0].predicate_id = "OTHER"
    with pytest.raises(TypeError):
        second.evidence["planet"] = "Moon"


def test_retired_engine_cannot_reintroduce_global_cache_or_identity_key():
    path = Path("systems/Parasara/engine/rules/engine.py")
    assert not path.exists()


def test_canonical_evaluator_module_static_boundary():
    path = Path(evaluator_module.__file__)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    text = path.read_text(encoding="utf-8")
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not imports & {
        "AstroState", "Chart", "PlanetState", "prepare_predicate_state", "os", "random",
        "uuid", "pickle", "subprocess", "open",
    }
    assert not calls & {"id", "hash", "repr", "asdict", "open"}
    assert "default=str" not in text
