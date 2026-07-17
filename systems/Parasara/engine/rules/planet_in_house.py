"""Canonical PLANET_IN_HOUSE execution over the prepared predicate boundary."""

from __future__ import annotations

from typing import Any

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
from systems.Parasara.engine.rules.parameters import invalid_parameters_error
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    PreparedAstroState,
    inspect_prepared_capability,
    observe_prepared_planet,
    observe_prepared_planet_house,
)
from systems.Parasara.engine.rules.registry import PredicateDefinition, get_production_registry


PREDICATE_ID = "PLANET_IN_HOUSE"
PREDICATE_VERSION = "1.0.0"

_PARAMETERS_STEP = "planet_in_house.parameters"
_CAPABILITIES_STEP = "planet_in_house.capabilities"
_PLANET_STEP = "planet_in_house.planet"
_HOUSE_STEP = "planet_in_house.house"
_EXECUTION_STEP = "planet_in_house.execution"
_RESULT_STEP = "planet_in_house.result"


def _definition() -> PredicateDefinition:
    definition = get_production_registry().lookup(PREDICATE_ID)
    if not isinstance(definition, PredicateDefinition):
        raise ValueError("canonical_predicate_definition_unavailable")
    if definition.predicate_id != PREDICATE_ID or definition.predicate_version != PREDICATE_VERSION:
        raise ValueError("canonical_predicate_definition_mismatch")
    return definition


def _trace(
    step_id: str,
    operation: str,
    *,
    details: dict[str, Any],
    observation: Any,
    parent_step_id: str | None = None,
    error_code: str | None = None,
) -> PredicateTraceStep:
    return PredicateTraceStep(
        step_id=step_id,
        operation=operation,
        details=details,
        observation=observation,
        parent_step_id=parent_step_id,
        error_code=error_code,
    )


def _result_step(status: PredicateStatus, parent_step_id: str) -> PredicateTraceStep:
    return _trace(
        _RESULT_STEP,
        "final_disposition",
        details={"predicate_id": PREDICATE_ID},
        observation={"matched": status is PredicateStatus.MATCHED, "status": status.value},
        parent_step_id=parent_step_id,
    )


def _capability_data(inspection: CapabilityInspection) -> dict[str, Any]:
    return {
        "capability_id": inspection.capability_id,
        "expected_version": inspection.expected_version,
        "observed_version": inspection.observed_version,
        "readiness": inspection.readiness.value,
        "source_kind": inspection.source_kind,
        "issues": inspection.issues,
    }


def _availability_evidence(
    planet: str,
    expected_house: int,
    inspections: tuple[CapabilityInspection, ...],
    *,
    entity_state: str,
    fact_state: str | None = None,
) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "planet": planet,
        "expected_house": expected_house,
        "entity_state": entity_state,
        "capabilities": tuple(_capability_data(item) for item in inspections),
    }
    if fact_state is not None:
        evidence["fact_state"] = fact_state
    return evidence


def _ready_empty_error(inspection: CapabilityInspection) -> PredicateError:
    return PredicateError(
        code="ready_empty_not_allowed",
        message="A required predicate capability cannot be empty.",
        predicate_id=PREDICATE_ID,
        details={
            "predicate_id": PREDICATE_ID,
            "capability_id": inspection.capability_id,
            "expected_version": inspection.expected_version,
            "observed_version": inspection.observed_version,
            "readiness": inspection.readiness.value,
            "source_kind": inspection.source_kind,
            "entity_kind": "planet",
            "entity_id": None,
            "issues": ("empty_not_ready",),
        },
        recoverable=True,
    )


def _capability_errors(inspections: tuple[CapabilityInspection, ...]) -> tuple[PredicateError, ...]:
    errors: list[PredicateError] = []
    for inspection in inspections:
        if inspection.readiness is CapabilityReadiness.READY:
            continue
        if inspection.readiness is CapabilityReadiness.READY_EMPTY:
            errors.append(_ready_empty_error(inspection))
        else:
            errors.append(capability_error(PREDICATE_ID, inspection, entity_kind="planet"))
    return tuple(errors)


def _missing_entity_error(planet: str) -> PredicateError:
    return PredicateError(
        code="missing_planet_entity",
        message="The requested canonical planet is unavailable.",
        predicate_id=PREDICATE_ID,
        details={
            "predicate_id": PREDICATE_ID,
            "capability_id": "planets.normalized",
            "entity_kind": "planet",
            "entity_id": planet,
            "fact_state": CapabilityFactState.ABSENT_ENTITY.value,
        },
        recoverable=True,
    )


def _missing_house_error(planet: str, observation: CapabilityFactObservation) -> PredicateError:
    return PredicateError(
        code="missing_planet_house",
        message="The requested planet house fact is unavailable.",
        predicate_id=PREDICATE_ID,
        details={
            "predicate_id": PREDICATE_ID,
            "capability_id": observation.capability_id,
            "capability_version": observation.capability_version,
            "entity_kind": "planet",
            "entity_id": planet,
            "fact_state": observation.state.value,
            "issues": observation.issues,
        },
        recoverable=True,
    )


def _unexpected_error() -> PredicateError:
    return PredicateError(
        code="predicate_execution_error",
        message="Canonical predicate execution failed.",
        predicate_id=PREDICATE_ID,
        details={"predicate_id": PREDICATE_ID, "operation": "canonical_execution"},
        recoverable=False,
    )


def _unexpected_result(
    inputs: Any,
    trace_steps: tuple[PredicateTraceStep, ...],
    version: str,
) -> PredicateResult:
    parent = trace_steps[-1].step_id if trace_steps else None
    failed = _trace(
        _EXECUTION_STEP,
        "canonical_execution",
        details={"predicate_id": PREDICATE_ID},
        observation={"completed": False},
        parent_step_id=parent,
        error_code="predicate_execution_error",
    )
    final = _result_step(PredicateStatus.ERROR, failed.step_id)
    safe_inputs = inputs if inputs is not None else {}
    return PredicateResult(
        matched=False,
        predicate_id=PREDICATE_ID,
        predicate_version=version,
        inputs=safe_inputs,
        evidence={},
        trace_steps=(*trace_steps, failed, final),
        errors=(_unexpected_error(),),
        cache_hit=False,
        evaluation_time_ms=None,
        status=PredicateStatus.ERROR,
    )


def evaluate_planet_in_house(
    parameters: Any,
    state: PreparedAstroState,
    context: PredicateEvaluationContext,
) -> PredicateResult:
    """Evaluate only canonical PLANET_IN_HOUSE facts from a prepared state."""

    version = PREDICATE_VERSION
    normalized_inputs = None
    trace_steps: tuple[PredicateTraceStep, ...] = ()
    try:
        definition = _definition()
        version = definition.predicate_version
        validation = definition.parameter_schema.validate(parameters)
        parameter_error = None if validation.valid else invalid_parameters_error(PREDICATE_ID, validation)
        parameter_trace = _trace(
            _PARAMETERS_STEP,
            "validate_parameters",
            details={"predicate_id": PREDICATE_ID, "predicate_version": version},
            observation={
                "valid": validation.valid,
                "issue_codes": tuple(issue.code.value for issue in validation.issues),
                "issue_paths": tuple(issue.path for issue in validation.issues),
            },
            error_code=None if parameter_error is None else parameter_error.code,
        )
        trace_steps = (parameter_trace,)
        if not validation.valid:
            status = PredicateStatus.INVALID_PARAMETERS
            return PredicateResult(
                matched=False,
                predicate_id=PREDICATE_ID,
                predicate_version=version,
                inputs={},
                evidence={},
                trace_steps=(*trace_steps, _result_step(status, parameter_trace.step_id)),
                errors=(parameter_error,),
                cache_hit=False,
                evaluation_time_ms=None,
                status=status,
            )

        normalized_inputs = validation.normalized_inputs
        if not isinstance(state, PreparedAstroState) or not isinstance(context, PredicateEvaluationContext):
            raise TypeError("canonical_boundary_type_mismatch")

        inspections = tuple(
            inspect_prepared_capability(state, requirement)
            for requirement in definition.required_capabilities
        )
        capability_errors = _capability_errors(inspections)
        capability_trace = _trace(
            _CAPABILITIES_STEP,
            "inspect_required_capabilities",
            details={
                "predicate_id": PREDICATE_ID,
                "required_capabilities": tuple(item.capability_id for item in definition.required_capabilities),
            },
            observation=tuple(_capability_data(item) for item in inspections),
            parent_step_id=parameter_trace.step_id,
            error_code=capability_errors[0].code if capability_errors else None,
        )
        trace_steps = (*trace_steps, capability_trace)
        planet = normalized_inputs["planet"]
        expected_house = normalized_inputs["house"]
        if capability_errors:
            status = PredicateStatus.MISSING_CAPABILITY
            evidence = _availability_evidence(
                planet,
                expected_house,
                inspections,
                entity_state="unknown",
            )
            return PredicateResult(
                matched=False,
                predicate_id=PREDICATE_ID,
                predicate_version=version,
                inputs=normalized_inputs,
                evidence=evidence,
                trace_steps=(*trace_steps, _result_step(status, capability_trace.step_id)),
                errors=capability_errors,
                cache_hit=False,
                evaluation_time_ms=None,
                status=status,
            )

        planet_observation = observe_prepared_planet(state, planet)
        if planet_observation.state is not CapabilityFactState.PRESENT:
            error = _missing_entity_error(planet)
            planet_trace = _trace(
                _PLANET_STEP,
                "lookup_canonical_planet",
                details={"planet": planet},
                observation={
                    "entity_state": planet_observation.state.value,
                    "issues": planet_observation.issues,
                },
                parent_step_id=capability_trace.step_id,
                error_code=error.code,
            )
            status = PredicateStatus.MISSING_CAPABILITY
            evidence = _availability_evidence(
                planet,
                expected_house,
                inspections,
                entity_state=planet_observation.state.value,
            )
            return PredicateResult(
                matched=False,
                predicate_id=PREDICATE_ID,
                predicate_version=version,
                inputs=normalized_inputs,
                evidence=evidence,
                trace_steps=(*trace_steps, planet_trace, _result_step(status, planet_trace.step_id)),
                errors=(error,),
                cache_hit=False,
                evaluation_time_ms=None,
                status=status,
            )

        planet_trace = _trace(
            _PLANET_STEP,
            "lookup_canonical_planet",
            details={"planet": planet},
            observation={"entity_state": planet_observation.state.value},
            parent_step_id=capability_trace.step_id,
        )
        trace_steps = (*trace_steps, planet_trace)
        house_observation = observe_prepared_planet_house(state, planet)
        if house_observation.state is not CapabilityFactState.PRESENT:
            error = _missing_house_error(planet, house_observation)
            house_trace = _trace(
                _HOUSE_STEP,
                "observe_planet_house",
                details={"planet": planet, "expected_house": expected_house},
                observation={
                    "fact_state": house_observation.state.value,
                    "issues": house_observation.issues,
                },
                parent_step_id=planet_trace.step_id,
                error_code=error.code,
            )
            status = PredicateStatus.MISSING_CAPABILITY
            evidence = _availability_evidence(
                planet,
                expected_house,
                inspections,
                entity_state=CapabilityFactState.PRESENT.value,
                fact_state=house_observation.state.value,
            )
            return PredicateResult(
                matched=False,
                predicate_id=PREDICATE_ID,
                predicate_version=version,
                inputs=normalized_inputs,
                evidence=evidence,
                trace_steps=(*trace_steps, house_trace, _result_step(status, house_trace.step_id)),
                errors=(error,),
                cache_hit=False,
                evaluation_time_ms=None,
                status=status,
            )

        actual_house = house_observation.value
        equal = actual_house == expected_house
        status = PredicateStatus.MATCHED if equal else PredicateStatus.UNMATCHED
        house_trace = _trace(
            _HOUSE_STEP,
            "compare_planet_house",
            details={"planet": planet, "expected_house": expected_house},
            observation={"actual_house": actual_house, "equal": equal},
            parent_step_id=planet_trace.step_id,
        )
        evidence = {
            "planet": planet,
            "expected_house": expected_house,
            "actual_house": actual_house,
            "equal": equal,
            "capabilities": tuple(_capability_data(item) for item in inspections),
        }
        return PredicateResult(
            matched=equal,
            predicate_id=PREDICATE_ID,
            predicate_version=version,
            inputs=normalized_inputs,
            evidence=evidence,
            trace_steps=(*trace_steps, house_trace, _result_step(status, house_trace.step_id)),
            errors=(),
            cache_hit=False,
            evaluation_time_ms=None,
            status=status,
        )
    except Exception:
        return _unexpected_result(normalized_inputs, trace_steps, version)


__all__ = ("PREDICATE_ID", "PREDICATE_VERSION", "evaluate_planet_in_house")
