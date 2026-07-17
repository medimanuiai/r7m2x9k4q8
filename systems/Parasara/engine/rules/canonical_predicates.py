"""Canonical WP11 handlers over immutable prepared predicate facts.

The four handlers in this module deliberately keep their factual semantics
explicit.  Small helpers below are limited to shared validation, capability,
trace, and safe-result construction.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable

from systems.Parasara.engine.rules.capabilities import (
    CapabilityFactObservation,
    CapabilityFactState,
    CapabilityInspection,
    CapabilityReadiness,
    capability_error,
)
from systems.Parasara.engine.rules.models import (
    PredicateError,
    PredicateResult,
    PredicateStatus,
    PredicateTraceStep,
)
from systems.Parasara.engine.rules.parameters import CANONICAL_PLANETS, invalid_parameters_error
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    PreparedAstroState,
    find_prepared_planet,
    inspect_prepared_capability,
    observe_prepared_exaltation_fact,
    observe_prepared_functional_role,
    observe_prepared_planet,
    observe_prepared_planet_house,
    retrieve_prepared_aspects,
)
from systems.Parasara.engine.rules.registry import PredicateDefinition, get_production_registry


PREDICATE_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class _Start:
    definition: PredicateDefinition
    inputs: Mapping[str, Any]
    trace: PredicateTraceStep


def _step(
    prefix: str,
    name: str,
    operation: str,
    *,
    details: Mapping[str, Any],
    observation: Any,
    parent: str | None = None,
    error_code: str | None = None,
) -> PredicateTraceStep:
    return PredicateTraceStep(
        step_id=f"{prefix}.{name}",
        operation=operation,
        details=details,
        observation=observation,
        parent_step_id=parent,
        error_code=error_code,
    )


def _final(prefix: str, predicate_id: str, status: PredicateStatus, parent: str) -> PredicateTraceStep:
    return _step(
        prefix,
        "result",
        "final_disposition",
        details={"predicate_id": predicate_id},
        observation={"matched": status is PredicateStatus.MATCHED, "status": status.value},
        parent=parent,
    )


def _make_result(
    predicate_id: str,
    prefix: str,
    status: PredicateStatus,
    inputs: Mapping[str, Any],
    evidence: Mapping[str, Any],
    traces: tuple[PredicateTraceStep, ...],
    errors: tuple[PredicateError, ...] = (),
) -> PredicateResult:
    parent = traces[-1].step_id
    return PredicateResult(
        matched=status is PredicateStatus.MATCHED,
        predicate_id=predicate_id,
        predicate_version=PREDICATE_VERSION,
        inputs=inputs,
        evidence=evidence,
        trace_steps=(*traces, _final(prefix, predicate_id, status, parent)),
        errors=errors,
        cache_hit=False,
        evaluation_time_ms=None,
        status=status,
    )


def _fixed_error(
    predicate_id: str,
    code: str,
    message: str,
    details: Mapping[str, Any],
    *,
    recoverable: bool = True,
) -> PredicateError:
    return PredicateError(
        code=code,
        message=message,
        predicate_id=predicate_id,
        details={"predicate_id": predicate_id, **details},
        recoverable=recoverable,
    )


def _unexpected(
    predicate_id: str,
    prefix: str,
    inputs: Mapping[str, Any] | None,
    traces: tuple[PredicateTraceStep, ...],
) -> PredicateResult:
    parent = traces[-1].step_id if traces else None
    failed = _step(
        prefix,
        "execution",
        "canonical_execution",
        details={"predicate_id": predicate_id},
        observation={"completed": False},
        parent=parent,
        error_code="predicate_execution_error",
    )
    error = _fixed_error(
        predicate_id,
        "predicate_execution_error",
        "Canonical predicate execution failed.",
        {"operation": "canonical_execution"},
        recoverable=False,
    )
    return _make_result(
        predicate_id,
        prefix,
        PredicateStatus.ERROR,
        {} if inputs is None else inputs,
        {},
        (*traces, failed),
        (error,),
    )


def _start(predicate_id: str, prefix: str, parameters: Any) -> _Start | PredicateResult:
    definition = get_production_registry().lookup(predicate_id)
    if (
        not isinstance(definition, PredicateDefinition)
        or definition.predicate_id != predicate_id
        or definition.predicate_version != PREDICATE_VERSION
    ):
        raise ValueError("canonical_predicate_definition_mismatch")
    validation = definition.parameter_schema.validate(parameters)
    error = None if validation.valid else invalid_parameters_error(predicate_id, validation)
    trace = _step(
        prefix,
        "parameters",
        "validate_parameters",
        details={"predicate_id": predicate_id, "predicate_version": PREDICATE_VERSION},
        observation={
            "valid": validation.valid,
            "issue_codes": tuple(issue.code.value for issue in validation.issues),
            "issue_paths": tuple(issue.path for issue in validation.issues),
        },
        error_code=None if error is None else error.code,
    )
    if not validation.valid:
        return _make_result(
            predicate_id,
            prefix,
            PredicateStatus.INVALID_PARAMETERS,
            {},
            {},
            (trace,),
            (error,),
        )
    if validation.normalized_inputs is None:
        raise ValueError("parameter_validation_contract_error")
    return _Start(definition=definition, inputs=validation.normalized_inputs, trace=trace)


def _capability_data(inspection: CapabilityInspection) -> dict[str, Any]:
    return {
        "capability_id": inspection.capability_id,
        "expected_version": inspection.expected_version,
        "observed_version": inspection.observed_version,
        "readiness": inspection.readiness.value,
        "source_kind": inspection.source_kind,
        "content_empty": inspection.content_empty,
        "issues": inspection.issues,
    }


def _ready_empty_error(predicate_id: str, inspection: CapabilityInspection) -> PredicateError:
    return _fixed_error(
        predicate_id,
        "ready_empty_not_allowed",
        "A required predicate capability cannot be empty.",
        {
            "capability_id": inspection.capability_id,
            "expected_version": inspection.expected_version,
            "observed_version": inspection.observed_version,
            "readiness": inspection.readiness.value,
            "source_kind": inspection.source_kind,
            "issues": ("empty_not_ready",),
        },
    )


def _inspect(
    start: _Start,
    state: PreparedAstroState,
    prefix: str,
    *,
    allow_ready_empty: frozenset[str] = frozenset(),
) -> tuple[tuple[CapabilityInspection, ...], tuple[PredicateError, ...], PredicateTraceStep]:
    inspections = tuple(
        inspect_prepared_capability(state, requirement)
        for requirement in start.definition.required_capabilities
    )
    errors: list[PredicateError] = []
    for inspection in inspections:
        if inspection.readiness is CapabilityReadiness.READY:
            continue
        if (
            inspection.readiness is CapabilityReadiness.READY_EMPTY
            and inspection.capability_id in allow_ready_empty
        ):
            continue
        if inspection.readiness is CapabilityReadiness.READY_EMPTY:
            errors.append(_ready_empty_error(start.definition.predicate_id, inspection))
        else:
            errors.append(capability_error(start.definition.predicate_id, inspection))
    trace = _step(
        prefix,
        "capabilities",
        "inspect_required_capabilities",
        details={
            "predicate_id": start.definition.predicate_id,
            "required_capabilities": tuple(
                requirement.capability_id for requirement in start.definition.required_capabilities
            ),
        },
        observation=tuple(_capability_data(item) for item in inspections),
        parent=start.trace.step_id,
        error_code=errors[0].code if errors else None,
    )
    return inspections, tuple(errors), trace


def _require_boundary(state: Any, context: Any) -> None:
    if not isinstance(state, PreparedAstroState) or not isinstance(context, PredicateEvaluationContext):
        raise TypeError("canonical_boundary_type_mismatch")


def _missing_entity(predicate_id: str, planet_id: str, *, code: str = "missing_planet_entity") -> PredicateError:
    return _fixed_error(
        predicate_id,
        code,
        "The requested canonical planet is unavailable.",
        {
            "capability_id": "planets.normalized",
            "entity_kind": "planet",
            "entity_id": planet_id,
            "fact_state": CapabilityFactState.ABSENT_ENTITY.value,
        },
    )


def evaluate_house_occupant(
    parameters: Any,
    state: PreparedAstroState,
    context: PredicateEvaluationContext,
) -> PredicateResult:
    """Evaluate HOUSE_OCCUPANT without aliasing its canonical identity."""

    predicate_id = "HOUSE_OCCUPANT"
    prefix = "house_occupant"
    inputs = None
    traces: tuple[PredicateTraceStep, ...] = ()
    try:
        begun = _start(predicate_id, prefix, parameters)
        if isinstance(begun, PredicateResult):
            return begun
        inputs = begun.inputs
        traces = (begun.trace,)
        _require_boundary(state, context)
        inspections, errors, capability_trace = _inspect(begun, state, prefix)
        traces = (*traces, capability_trace)
        evidence_base = {
            "requested_occupant": inputs["planet"],
            "planet": inputs["planet"],
            "expected_house": inputs["house"],
            "capabilities": tuple(_capability_data(item) for item in inspections),
        }
        if errors:
            return _make_result(
                predicate_id, prefix, PredicateStatus.MISSING_CAPABILITY, inputs,
                {**evidence_base, "entity_state": "unknown"}, traces, errors,
            )
        planet_id = inputs["planet"]
        entity = observe_prepared_planet(state, planet_id)
        entity_error = None if entity.state is CapabilityFactState.PRESENT else _missing_entity(predicate_id, planet_id)
        entity_trace = _step(
            prefix,
            "planet",
            "lookup_requested_occupant",
            details={"planet": planet_id},
            observation={"entity_state": entity.state.value, "issues": entity.issues},
            parent=capability_trace.step_id,
            error_code=None if entity_error is None else entity_error.code,
        )
        traces = (*traces, entity_trace)
        if entity_error is not None:
            return _make_result(
                predicate_id, prefix, PredicateStatus.MISSING_CAPABILITY, inputs,
                {**evidence_base, "entity_state": entity.state.value}, traces, (entity_error,),
            )
        house = observe_prepared_planet_house(state, planet_id)
        if house.state is not CapabilityFactState.PRESENT:
            error = _fixed_error(
                predicate_id,
                "missing_occupant_house",
                "The requested occupant house fact is unavailable.",
                {
                    "capability_id": house.capability_id,
                    "capability_version": house.capability_version,
                    "entity_kind": "planet",
                    "entity_id": planet_id,
                    "fact_state": house.state.value,
                    "issues": house.issues,
                },
            )
            house_trace = _step(
                prefix,
                "house",
                "observe_occupant_house",
                details={"planet": planet_id, "expected_house": inputs["house"]},
                observation={"fact_state": house.state.value, "issues": house.issues},
                parent=entity_trace.step_id,
                error_code=error.code,
            )
            return _make_result(
                predicate_id, prefix, PredicateStatus.MISSING_CAPABILITY, inputs,
                {**evidence_base, "entity_state": "present", "fact_state": house.state.value},
                (*traces, house_trace), (error,),
            )
        equal = house.value == inputs["house"]
        house_trace = _step(
            prefix,
            "house",
            "compare_occupant_house",
            details={"planet": planet_id, "expected_house": inputs["house"]},
            observation={"actual_house": house.value, "equal": equal},
            parent=entity_trace.step_id,
        )
        status = PredicateStatus.MATCHED if equal else PredicateStatus.UNMATCHED
        return _make_result(
            predicate_id,
            prefix,
            status,
            inputs,
            {**evidence_base, "actual_house": house.value, "equal": equal},
            (*traces, house_trace),
        )
    except Exception:
        return _unexpected(predicate_id, prefix, inputs, traces)


def _edge_matches(edge: Mapping[str, Any], filters: Mapping[str, Any], state: PreparedAstroState) -> bool:
    source = edge["source"]
    target = edge["target"]
    if "from_planet" in filters and source != filters["from_planet"]:
        return False
    if "to_planet" in filters and target != filters["to_planet"]:
        return False
    if "from_house" in filters:
        source_planet = find_prepared_planet(state, source)
        if source_planet is None or source_planet.house != filters["from_house"]:
            return False
    if "to_house" in filters:
        target_planet = find_prepared_planet(state, target)
        if target_planet is None or target_planet.house != filters["to_house"]:
            return False
    return True


def _edge_projection(
    edge: Mapping[str, Any],
    state: PreparedAstroState,
    filters: Mapping[str, Any],
) -> dict[str, Any]:
    result = {"source": edge["source"], "target": edge["target"]}
    for name in ("aspect", "kind"):
        if name in edge:
            result[name] = edge[name]
    if "from_house" in filters:
        source_planet = find_prepared_planet(state, edge["source"])
        result["from_house"] = None if source_planet is None else source_planet.house
    if "to_house" in filters:
        target_planet = find_prepared_planet(state, edge["target"])
        result["to_house"] = None if target_planet is None else target_planet.house
    return result


def evaluate_aspect_exists(
    parameters: Any,
    state: PreparedAstroState,
    context: PredicateEvaluationContext,
) -> PredicateResult:
    """Evaluate preserved whole-sign graph edges for ASPECT_EXISTS/ASPECT."""

    predicate_id = "ASPECT_EXISTS"
    prefix = "aspect_exists"
    inputs = None
    traces: tuple[PredicateTraceStep, ...] = ()
    try:
        begun = _start(predicate_id, prefix, parameters)
        if isinstance(begun, PredicateResult):
            return begun
        inputs = begun.inputs
        traces = (begun.trace,)
        _require_boundary(state, context)
        inspections, errors, capability_trace = _inspect(
            begun, state, prefix, allow_ready_empty=frozenset({"aspects.whole_sign_graph"})
        )
        traces = (*traces, capability_trace)
        evidence_base = {
            "filters": inputs,
            "capability": _capability_data(inspections[0]),
            "graph_available": not errors,
        }
        if errors:
            return _make_result(
                predicate_id, prefix, PredicateStatus.MISSING_CAPABILITY, inputs,
                {**evidence_base, "edge_count": None, "matched_indexes": ()}, traces, errors,
            )
        observation = retrieve_prepared_aspects(state, begun.definition.required_capabilities[0])
        if observation.state is not CapabilityFactState.PRESENT:
            error = _fixed_error(
                predicate_id,
                "missing_aspect_graph_fact",
                "The prepared Aspect graph fact is unavailable.",
                {
                    "capability_id": observation.capability_id,
                    "capability_version": observation.capability_version,
                    "fact_state": observation.state.value,
                    "issues": observation.issues,
                },
            )
            graph_trace = _step(
                prefix, "graph", "retrieve_aspect_graph",
                details={"capability_id": observation.capability_id},
                observation={"fact_state": observation.state.value, "issues": observation.issues},
                parent=capability_trace.step_id, error_code=error.code,
            )
            return _make_result(
                predicate_id, prefix, PredicateStatus.MISSING_CAPABILITY, inputs,
                {**evidence_base, "edge_count": None, "matched_indexes": ()},
                (*traces, graph_trace), (error,),
            )
        edges = observation.value["edges"]
        graph_trace = _step(
            prefix, "graph", "retrieve_aspect_graph",
            details={"capability_id": observation.capability_id},
            observation={"fact_state": observation.state.value, "edge_count": len(edges)},
            parent=capability_trace.step_id,
        )
        matched_indexes = tuple(
            index for index, edge in enumerate(edges) if _edge_matches(edge, inputs, state)
        )
        matched_edges = tuple(_edge_projection(edges[index], state, inputs) for index in matched_indexes)
        matched = bool(matched_indexes)
        comparison = _step(
            prefix, "comparison", "match_aspect_filters",
            details={"filters": inputs},
            observation={"edge_count": len(edges), "matched_indexes": matched_indexes},
            parent=graph_trace.step_id,
        )
        return _make_result(
            predicate_id,
            prefix,
            PredicateStatus.MATCHED if matched else PredicateStatus.UNMATCHED,
            inputs,
            {
                **evidence_base,
                "edge_count": len(edges),
                "matched_indexes": matched_indexes,
                "matched_edges": matched_edges,
            },
            (*traces, graph_trace, comparison),
        )
    except Exception:
        return _unexpected(predicate_id, prefix, inputs, traces)


def _candidate_data(
    planet_id: str,
    entity: CapabilityFactObservation,
    role: CapabilityFactObservation | None,
    expected_roles: tuple[str, ...],
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "planet": planet_id,
        "entity_state": entity.state.value,
        "fact_state": None if role is None else role.state.value,
        "matches_expected": False,
    }
    if role is not None and role.state is CapabilityFactState.PRESENT:
        data["observed_role"] = role.value
        data["matches_expected"] = role.value in expected_roles
    if entity.issues:
        data["entity_issues"] = entity.issues
    if role is not None and role.issues:
        data["fact_issues"] = role.issues
    return data


def evaluate_functional_role(
    parameters: Any,
    state: PreparedAstroState,
    context: PredicateEvaluationContext,
) -> PredicateResult:
    """Evaluate prepared role facts only; no role producer is reachable here."""

    predicate_id = "FUNCTIONAL_ROLE"
    prefix = "functional_role"
    inputs = None
    traces: tuple[PredicateTraceStep, ...] = ()
    try:
        begun = _start(predicate_id, prefix, parameters)
        if isinstance(begun, PredicateResult):
            return begun
        inputs = begun.inputs
        traces = (begun.trace,)
        _require_boundary(state, context)
        inspections, errors, capability_trace = _inspect(
            begun, state, prefix, allow_ready_empty=frozenset({"roles.functional"})
        )
        traces = (*traces, capability_trace)
        selection_policy = (
            "all_present" if context.selected_planets is None
            else "explicit_empty" if not context.selected_planets
            else "explicit"
        )
        candidates = (
            tuple(item.planet_id for item in state.planets)
            if context.selected_planets is None
            else context.selected_planets
        )
        evidence_base = {
            "expected_roles": inputs["role_in"],
            "selection_policy": selection_policy,
            "selected_planets": context.selected_planets,
            "capabilities": tuple(_capability_data(item) for item in inspections),
        }
        if errors:
            return _make_result(
                predicate_id, prefix, PredicateStatus.MISSING_CAPABILITY, inputs,
                {**evidence_base, "candidates": (), "matched_planets": ()}, traces, errors,
            )
        observations: list[dict[str, Any]] = []
        unavailable: list[tuple[str, PredicateError]] = []
        matched_planets: list[str] = []
        for planet_id in candidates:
            entity = observe_prepared_planet(state, planet_id)
            role = None
            if entity.state is CapabilityFactState.PRESENT:
                role = observe_prepared_functional_role(state, planet_id)
                if role.state is not CapabilityFactState.PRESENT:
                    unavailable.append((planet_id, _fixed_error(
                        predicate_id,
                        "missing_functional_role_fact",
                        "A selected planet functional-role fact is unavailable.",
                        {
                            "capability_id": role.capability_id,
                            "capability_version": role.capability_version,
                            "entity_kind": "planet",
                            "entity_id": planet_id,
                            "fact_state": role.state.value,
                            "issues": role.issues,
                        },
                    )))
                elif role.value in inputs["role_in"]:
                    matched_planets.append(planet_id)
            else:
                unavailable.append((planet_id, _missing_entity(
                    predicate_id, planet_id, code="missing_functional_role_entity"
                )))
            observations.append(_candidate_data(planet_id, entity, role, inputs["role_in"]))
        candidates_trace = _step(
            prefix, "candidates", "retrieve_candidate_role_facts",
            details={"selection_policy": selection_policy, "candidate_planets": candidates},
            observation=tuple(observations),
            parent=capability_trace.step_id,
            error_code=None if matched_planets or not unavailable else unavailable[0][1].code,
        )
        matched = bool(matched_planets)
        status = (
            PredicateStatus.MATCHED if matched
            else PredicateStatus.MISSING_CAPABILITY if unavailable
            else PredicateStatus.UNMATCHED
        )
        comparison = _step(
            prefix, "comparison", "compare_functional_roles",
            details={"expected_roles": inputs["role_in"]},
            observation={
                "matched_planets": tuple(matched_planets),
                "unavailable_planets": tuple(item[0] for item in unavailable),
            },
            parent=candidates_trace.step_id,
            error_code=None if status is not PredicateStatus.MISSING_CAPABILITY else unavailable[0][1].code,
        )
        result_errors = () if status is not PredicateStatus.MISSING_CAPABILITY else (unavailable[0][1],)
        return _make_result(
            predicate_id,
            prefix,
            status,
            inputs,
            {
                **evidence_base,
                "candidates": tuple(observations),
                "matched_planets": tuple(matched_planets),
            },
            (*traces, candidates_trace, comparison),
            result_errors,
        )
    except Exception:
        return _unexpected(predicate_id, prefix, inputs, traces)


def evaluate_planet_exalted(
    parameters: Any,
    state: PreparedAstroState,
    context: PredicateEvaluationContext,
) -> PredicateResult:
    """Interpret only the two preservation-locked prepared exaltation sources."""

    predicate_id = "PLANET_EXALTED"
    prefix = "planet_exalted"
    inputs = None
    traces: tuple[PredicateTraceStep, ...] = ()
    try:
        begun = _start(predicate_id, prefix, parameters)
        if isinstance(begun, PredicateResult):
            return begun
        inputs = begun.inputs
        traces = (begun.trace,)
        _require_boundary(state, context)
        inspections, errors, capability_trace = _inspect(
            begun, state, prefix, allow_ready_empty=frozenset({"dignity.exaltation_facts"})
        )
        traces = (*traces, capability_trace)
        planet_id = inputs["planet"]
        evidence_base = {
            "planet": planet_id,
            "capabilities": tuple(_capability_data(item) for item in inspections),
        }
        if errors:
            return _make_result(
                predicate_id, prefix, PredicateStatus.MISSING_CAPABILITY, inputs,
                {**evidence_base, "entity_state": "unknown", "records": ()}, traces, errors,
            )
        entity = observe_prepared_planet(state, planet_id)
        entity_error = None if entity.state is CapabilityFactState.PRESENT else _missing_entity(predicate_id, planet_id)
        entity_trace = _step(
            prefix, "planet", "lookup_canonical_planet",
            details={"planet": planet_id},
            observation={"entity_state": entity.state.value, "issues": entity.issues},
            parent=capability_trace.step_id,
            error_code=None if entity_error is None else entity_error.code,
        )
        traces = (*traces, entity_trace)
        if entity_error is not None:
            return _make_result(
                predicate_id, prefix, PredicateStatus.MISSING_CAPABILITY, inputs,
                {**evidence_base, "entity_state": entity.state.value, "records": ()},
                traces, (entity_error,),
            )
        fact = observe_prepared_exaltation_fact(state, planet_id)
        if fact.state is not CapabilityFactState.PRESENT:
            error = _fixed_error(
                predicate_id,
                "missing_exaltation_fact",
                "The requested planet exaltation fact is unavailable.",
                {
                    "capability_id": fact.capability_id,
                    "capability_version": fact.capability_version,
                    "entity_kind": "planet",
                    "entity_id": planet_id,
                    "fact_state": fact.state.value,
                    "issues": fact.issues,
                },
            )
            fact_trace = _step(
                prefix, "fact", "retrieve_exaltation_fact",
                details={"planet": planet_id},
                observation={"fact_state": fact.state.value, "issues": fact.issues},
                parent=entity_trace.step_id, error_code=error.code,
            )
            return _make_result(
                predicate_id, prefix, PredicateStatus.MISSING_CAPABILITY, inputs,
                {**evidence_base, "entity_state": "present", "fact_state": fact.state.value, "records": ()},
                (*traces, fact_trace), (error,),
            )
        records = tuple({"source_kind": item["source_kind"], "value": item["value"]} for item in fact.value)
        fact_trace = _step(
            prefix, "fact", "retrieve_exaltation_fact",
            details={"planet": planet_id},
            observation={"fact_state": fact.state.value, "record_count": len(records)},
            parent=entity_trace.step_id,
        )
        traces = (*traces, fact_trace)
        rule = None
        matched = False
        if len(records) == 1:
            record = records[0]
            if record["source_kind"] == "legacy_planet_flags" and type(record["value"]) is bool:
                rule = "explicit_flag_boolean"
                matched = record["value"]
            elif (
                record["source_kind"] == "legacy_metadata_exaltations"
                and type(record["value"]) is not bool
                and isinstance(record["value"], (int, float))
            ):
                rule = "configured_metadata_entry"
                matched = True
        if rule is None:
            error = _fixed_error(
                predicate_id,
                "unsupported_exaltation_source",
                "The prepared exaltation source/value combination is unsupported.",
                {
                    "entity_kind": "planet",
                    "entity_id": planet_id,
                    "source_kinds": tuple(item["source_kind"] for item in records),
                    "record_count": len(records),
                },
                recoverable=False,
            )
            interpretation = _step(
                prefix, "interpretation", "interpret_exaltation_fact",
                details={"planet": planet_id},
                observation={"supported": False, "source_kinds": error.details["source_kinds"]},
                parent=fact_trace.step_id, error_code=error.code,
            )
            return _make_result(
                predicate_id, prefix, PredicateStatus.MISSING_CAPABILITY, inputs,
                {**evidence_base, "entity_state": "present", "fact_state": "present", "records": records,
                 "interpretation_rule": "unsupported", "factual_state": "unavailable"},
                (*traces, interpretation), (error,),
            )
        interpretation = _step(
            prefix, "interpretation", "interpret_exaltation_fact",
            details={"planet": planet_id, "interpretation_rule": rule},
            observation={"matched": matched, "source_kind": records[0]["source_kind"], "value": records[0]["value"]},
            parent=fact_trace.step_id,
        )
        status = PredicateStatus.MATCHED if matched else PredicateStatus.UNMATCHED
        return _make_result(
            predicate_id,
            prefix,
            status,
            inputs,
            {**evidence_base, "entity_state": "present", "fact_state": "present", "records": records,
             "interpretation_rule": rule, "factual_state": status.value},
            (*traces, interpretation),
        )
    except Exception:
        return _unexpected(predicate_id, prefix, inputs, traces)


CANONICAL_HANDLER_DISPATCH: Mapping[
    str, Callable[[Any, PreparedAstroState, PredicateEvaluationContext], PredicateResult]
] = MappingProxyType({
    "ASPECT_EXISTS": evaluate_aspect_exists,
    "FUNCTIONAL_ROLE": evaluate_functional_role,
    "HOUSE_OCCUPANT": evaluate_house_occupant,
    "PLANET_EXALTED": evaluate_planet_exalted,
})


__all__ = (
    "CANONICAL_HANDLER_DISPATCH",
    "evaluate_aspect_exists",
    "evaluate_functional_role",
    "evaluate_house_occupant",
    "evaluate_planet_exalted",
)
