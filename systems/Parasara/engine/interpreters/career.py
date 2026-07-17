"""WP15 typed factual bridge for the existing Career compatibility output."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import PureWindowsPath
from types import SimpleNamespace
from typing import Any

from systems.Parasara.engine import confidence as confidence_mod
from systems.Parasara.engine import explainability
from systems.Parasara.engine.astrostate import AstroState
from systems.Parasara.engine.interpreters.career_models import (
    CAREER_EVALUATOR_VERSION,
    CAREER_FACT_VERSION,
    CAREER_SCHEMA_VERSION,
    CareerCandidateDefinition,
    CareerCandidateEvaluation,
    CareerEvaluationBatch,
    CareerFactKind,
    CareerFactResult,
    CareerHouse10Fact,
    CareerPlanetFact,
    CareerPreparedFacts,
    career_prepared_facts_sha256,
    freeze_ordered_compatibility,
    thaw_ordered_compatibility,
)
from systems.Parasara.engine.rules.canonical import canonical_json_data
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.models import (
    PredicateError,
    PredicateStatus,
    PredicateTraceStep,
)
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    prepare_predicate_state,
)


_KENDRA = frozenset({1, 4, 7, 10})
_BENEFICS = frozenset({"Jupiter", "Venus", "Mercury", "Moon"})


def _source_file(name: str) -> str:
    """Return the legacy repository-relative spelling without touching disk."""

    return str(PureWindowsPath("systems") / "Parasara" / "rules" / "parashara" / "v1" / name)


def _safe_error(
    code: str,
    message: str,
    predicate_id: str,
    details: Mapping[str, Any],
    *,
    recoverable: bool = True,
) -> PredicateError:
    return PredicateError(
        code=code,
        message=message,
        predicate_id=predicate_id,
        details=details,
        recoverable=recoverable,
    )


def _trace(
    step_id: str,
    operation: str,
    details: Mapping[str, Any],
    observation: Any,
    *,
    parent: str | None = None,
    error_code: str | None = None,
) -> PredicateTraceStep:
    return PredicateTraceStep(
        step_id=step_id,
        operation=operation,
        details=details,
        observation=observation,
        parent_step_id=parent,
        error_code=error_code,
    )


def _failed_preparation() -> CareerPreparedFacts:
    error = _safe_error(
        "career_preparation_failed",
        "Career facts could not be prepared safely.",
        "career.preparation",
        {"stage": "preparation"},
        recoverable=False,
    )
    return CareerPreparedFacts(
        schema_version=CAREER_SCHEMA_VERSION,
        fact_version=CAREER_FACT_VERSION,
        planets=(),
        planets_by_id={},
        house10=None,
        predicate_state=None,
        completeness={
            "lagna_present": False,
            "planets_present": False,
            "houses_present": False,
            "birth_datetime_present": False,
        },
        preparation_errors=(error,),
    )


def prepare_career_facts(astro: AstroState) -> CareerPreparedFacts:
    """Defensively snapshot exactly the mutable facts read by Career today."""

    try:
        # Supply only the exact occupancy boundary needed by Career.  Signs,
        # Aspects, roles, dignity, Yoga output, and all other enrichments are
        # intentionally absent from this canonical predicate state.
        predicate_source = SimpleNamespace(
            planets=[
                SimpleNamespace(name=planet.name, house=planet.house, sign=None)
                for planet in astro.planets
            ],
            lagna_sign=None,
            enrichments={},
            derived=None,
            metadata={},
        )
        outcome = prepare_predicate_state(predicate_source)
        if not outcome.succeeded or outcome.state is None:
            return _failed_preparation()

        enrichments = astro.enrichments
        strengths = enrichments.get("planet_strengths", {})
        strength_map = strengths if isinstance(strengths, Mapping) else {}
        planets = []
        by_id = {}
        for index, planet in enumerate(astro.planets):
            info = strength_map.get(planet.name)
            info_map = info if isinstance(info, Mapping) else {}
            enriched_strength_present = "strength" in info_map
            enriched_dignity_present = "dignity" in info_map
            item = CareerPlanetFact(
                planet_id=planet.name,
                source_index=index,
                house=planet.house,
                strength=planet.strength,
                strength_present=planet.strength is not None,
                enriched_strength=info_map.get("strength"),
                enriched_strength_present=enriched_strength_present,
                dignity=planet.dignity,
                dignity_present=planet.dignity is not None,
                enriched_dignity=info_map.get("dignity"),
                enriched_dignity_present=enriched_dignity_present,
            )
            planets.append(item)
            by_id[planet.name] = {
                "source_index": index,
                "house": planet.house,
                "strength": planet.strength,
                "strength_present": planet.strength is not None,
                "enriched_strength": info_map.get("strength"),
                "enriched_strength_present": enriched_strength_present,
                "dignity": planet.dignity,
                "dignity_present": planet.dignity is not None,
                "enriched_dignity": info_map.get("dignity"),
                "enriched_dignity_present": enriched_dignity_present,
            }

        summaries = enrichments.get("house_summaries", [])
        house10_source = next((item for item in summaries if item.get("number") == 10), None)
        house10 = None
        if house10_source is not None:
            occupants_present = "occupants" in house10_source
            occupants = house10_source.get("occupants", [])
            house10 = CareerHouse10Fact(
                lord=house10_source.get("lord"),
                lord_present="lord" in house10_source,
                occupants=tuple(occupants),
                occupants_present=occupants_present,
            )

        metadata = astro.metadata or {}
        completeness = {
            "lagna_present": bool(astro.lagna_sign),
            "planets_present": bool(astro.planets and len(astro.planets) >= 1),
            "houses_present": bool(astro.houses and len(astro.houses) >= 1),
            "birth_datetime_present": bool(metadata.get("birth_datetime_utc")),
        }
        return CareerPreparedFacts(
            schema_version=CAREER_SCHEMA_VERSION,
            fact_version=CAREER_FACT_VERSION,
            planets=tuple(planets),
            planets_by_id=by_id,
            house10=house10,
            predicate_state=outcome.state,
            completeness=completeness,
            preparation_errors=(),
        )
    except Exception:
        # This boundary records a typed safe preparation failure; it never
        # converts a failed fact into factual ``unmatched``.
        return _failed_preparation()


def _strong_context(candidate_id: str, planet: str) -> dict[str, Any]:
    return {
        "id": candidate_id,
        "version": "1.0",
        "family": "parashara",
        "type": "strong_in_10",
        "description": "A strong planet (strength >= 0.75) occupies the 10th house",
        "priority": 10,
        "base_score": 0.20,
        "_source_file": _source_file("m1_rules.yaml"),
        "planet": planet,
        "house": 10,
    }


def _lord_context(candidate_id: str, lord: Any) -> dict[str, Any]:
    return {
        "id": candidate_id,
        "name": "10th House Lord Status",
        "author": "legacy-unverified",
        "created_date": "legacy-unverified",
        "source_reference": "repository:8a04e1c3a5284030e8306b8d0ae11bcb1744fc26",
        "classical_reference": "legacy-unverified",
        "validation_status": "legacy-unverified",
        "sme_required": True,
        "sme_approved": False,
        "type": "lord_status",
        "house": 10,
        "base_score": 0.18,
        "_source_file": _source_file("derived_rules.yml"),
        "lord": lord,
    }


def _rajayoga_context() -> dict[str, Any]:
    return {
        "id": "rajayoga_naive",
        "name": "Naive Raja Yoga",
        "version": 1,
        "category": "rajayoga",
        "provenance": "parashara:m1:seed",
        "sme_approved": False,
        "description": "Naive Raja Yoga: benefic planet from 1st aspects 10th (data-driven, example)",
        "conditions": {
            "type": "AND",
            "children": [
                {"type": "ASPECT", "params": {"from_house": 1, "to_house": 10}},
                {"type": "FUNCTIONAL_ROLE", "params": {"role_in": ["functional_benefic", "yogakaraka", "benefic"]}},
            ],
        },
        "weights": {"base": 1.0, "evidence_bonus": 0.5},
        "evidence_required": 1,
        "tests": [{
            "fixture": "systems/Parasara/fixtures/golden_chart_01.json",
            "expect": {"yoga_id": "rajayoga_naive", "matched": False},
        }],
        "_source_file": _source_file("yogas.yaml"),
        "type": "rajayoga_naive",
    }


def _candidate_catalog(facts: CareerPreparedFacts) -> tuple[CareerCandidateDefinition, ...]:
    definitions = []
    for planet in facts.planets:
        candidate_id = f"strong_in_10_{planet.planet_id}"
        definitions.append(CareerCandidateDefinition(
            candidate_id=candidate_id,
            rule_type="strong_in_10",
            rule_version="1.0",
            source_identity="m1_rules.yaml:strong_planet_in_10",
            normalized_parameters={"planet": planet.planet_id, "house": 10},
            compatibility_context=freeze_ordered_compatibility(_strong_context(candidate_id, planet.planet_id)),
            base_score=0.20,
            matched_score=0.20,
            unmatched_score=0.05,
            source_index=len(definitions),
        ))
    lord = facts.house10.lord if facts.house10 is not None else None
    if lord:
        candidate_id = f"10th_lord_{lord}"
        definitions.append(CareerCandidateDefinition(
            candidate_id=candidate_id,
            rule_type="lord_status",
            rule_version=None,
            source_identity="derived_rules.yml:lord_status_10th",
            normalized_parameters={"lord": lord, "house": 10},
            compatibility_context=freeze_ordered_compatibility(_lord_context(candidate_id, lord)),
            base_score=0.18,
            matched_score=0.18,
            unmatched_score=0.05,
            source_index=len(definitions),
        ))
    definitions.append(CareerCandidateDefinition(
        candidate_id="rajayoga_naive",
        rule_type="rajayoga_naive",
        rule_version="1",
        source_identity="yogas.yaml:rajayoga_naive",
        normalized_parameters={},
        compatibility_context=freeze_ordered_compatibility(_rajayoga_context()),
        base_score=None,
        matched_score=0.18,
        unmatched_score=0.0,
        source_index=len(definitions),
    ))
    return tuple(definitions)


@dataclass(frozen=True, slots=True)
class _ObservedValue:
    value: Any
    present: bool
    source: str


@dataclass(frozen=True, slots=True)
class _BaseEvaluation:
    base_score: float
    base_facts: tuple[CareerFactResult, ...]
    component_facts: tuple[CareerFactResult, ...]
    error: PredicateError | None = None


def _effective_strength(planet: CareerPlanetFact) -> _ObservedValue:
    if planet.enriched_strength_present and planet.enriched_strength is not None:
        return _ObservedValue(planet.enriched_strength, True, "planet_strengths")
    if planet.strength_present:
        return _ObservedValue(planet.strength, True, "planet")
    return _ObservedValue(None, False, "absent")


def _effective_dignity(planet: CareerPlanetFact) -> _ObservedValue:
    if planet.enriched_dignity_present and planet.enriched_dignity:
        return _ObservedValue(planet.enriched_dignity, True, "planet_strengths")
    if planet.dignity_present:
        return _ObservedValue(planet.dignity, True, "planet")
    if planet.enriched_dignity_present:
        return _ObservedValue(planet.enriched_dignity, True, "planet_strengths")
    return _ObservedValue(None, False, "absent")


def _strong_evaluation(
    definition: CareerCandidateDefinition,
    facts: CareerPreparedFacts,
    evaluator: PredicateEvaluator,
    context: PredicateEvaluationContext,
) -> CareerCandidateEvaluation:
    planet_id = definition.normalized_parameters["planet"]
    backing = evaluator.evaluate(
        "PLANET_IN_HOUSE",
        {"planet": planet_id, "house": definition.normalized_parameters["house"]},
        facts.predicate_state,
        context,
    )
    # Career identity retains the complete canonical logical result while
    # deliberately normalizing optional evaluator telemetry.  This keeps both
    # Career logical and full persistence byte-identical across cache warmth,
    # fresh processes, Python lanes, and machine speed.
    backing = replace(backing, cache_hit=False, evaluation_time_ms=None)
    fact_id = f"career.fact.{definition.candidate_id}"
    inputs = {"planet": planet_id, "house": 10, "threshold": 0.75}
    comparison_parent = backing.trace_steps[-1].step_id if backing.trace_steps else None
    if backing.status not in (PredicateStatus.MATCHED, PredicateStatus.UNMATCHED):
        step = _trace(
            f"{fact_id}.comparison", "strong_in_house_compatibility",
            inputs, {"factual_state": "unavailable"},
            parent=comparison_parent,
            error_code=backing.errors[0].code if backing.errors else "canonical_occupancy_unavailable",
        )
        errors = backing.errors or (_safe_error(
            "canonical_occupancy_unavailable", "Canonical occupancy is unavailable.",
            fact_id, {"planet": planet_id, "house": 10},
        ),)
        fact = CareerFactResult(
            fact_id=fact_id, fact_version=CAREER_FACT_VERSION,
            fact_kind=CareerFactKind.STRONG_IN_HOUSE, matched=False,
            status=backing.status, inputs=inputs,
            evidence={"occupancy": canonical_json_data(backing.evidence), "strength_state": "not_evaluated"},
            errors=errors, trace_steps=(*backing.trace_steps, step),
            backing_result=backing, evaluation_time_ms=None,
        )
        adjusted = 0.0
        compatibility_evidence = {}
    elif not backing.matched:
        step = _trace(
            f"{fact_id}.comparison", "strong_in_house_compatibility",
            inputs, {"occupies_house": False, "strength_state": "not_evaluated"},
            parent=comparison_parent,
        )
        fact = CareerFactResult(
            fact_id=fact_id, fact_version=CAREER_FACT_VERSION,
            fact_kind=CareerFactKind.STRONG_IN_HOUSE, matched=False,
            status=PredicateStatus.UNMATCHED, inputs=inputs,
            evidence={"planet": planet_id, "actual_house": backing.evidence.get("actual_house"), "expected_house": 10},
            errors=(), trace_steps=(*backing.trace_steps, step),
            backing_result=backing, evaluation_time_ms=None,
        )
        adjusted = 0.0
        compatibility_evidence = {}
    else:
        planet = next((item for item in facts.planets if item.planet_id == planet_id), None)
        observation = _effective_strength(planet) if planet is not None else _ObservedValue(None, False, "absent")
        compatibility_evidence = {
            "planet": planet_id, "house": 10,
            "strength": observation.value if observation.present else 0.0,
        }
        if not observation.present:
            error = _safe_error(
                "missing_planet_strength_fact", "The selected planet strength fact is unavailable.",
                fact_id, {"planet": planet_id, "house": 10, "fact": "strength"},
            )
            step = _trace(
                f"{fact_id}.comparison", "strong_in_house_compatibility", inputs,
                {"occupies_house": True, "strength_state": "absent", "legacy_value": 0.0},
                parent=comparison_parent, error_code=error.code,
            )
            fact = CareerFactResult(
                fact_id=fact_id, fact_version=CAREER_FACT_VERSION,
                fact_kind=CareerFactKind.STRONG_IN_HOUSE, matched=False,
                status=PredicateStatus.MISSING_CAPABILITY, inputs=inputs,
                evidence={"planet": planet_id, "house": 10, "strength": None, "strength_source": observation.source},
                errors=(error,), trace_steps=(*backing.trace_steps, step),
                backing_result=backing, evaluation_time_ms=None,
            )
            adjusted = definition.unmatched_score
        else:
            matched = observation.value >= 0.75
            status = PredicateStatus.MATCHED if matched else PredicateStatus.UNMATCHED
            step = _trace(
                f"{fact_id}.comparison", "strong_in_house_compatibility", inputs,
                {"occupies_house": True, "strength": observation.value, "strength_source": observation.source, "matched": matched},
                parent=comparison_parent,
            )
            fact = CareerFactResult(
                fact_id=fact_id, fact_version=CAREER_FACT_VERSION,
                fact_kind=CareerFactKind.STRONG_IN_HOUSE, matched=matched, status=status,
                inputs=inputs,
                evidence={"planet": planet_id, "house": 10, "strength": observation.value, "strength_source": observation.source},
                errors=(), trace_steps=(*backing.trace_steps, step),
                backing_result=backing, evaluation_time_ms=None,
            )
            adjusted = definition.matched_score if matched else definition.unmatched_score
    contribution = float(adjusted) if fact.matched and adjusted > 0 else 0.0
    return CareerCandidateEvaluation(
        definition=definition, fact=fact, matched=fact.matched, status=fact.status,
        adjusted_score=round(float(adjusted), 3), contribution=contribution,
        compatibility_evidence=compatibility_evidence,
        trace_lineage=tuple(step.step_id for step in fact.trace_steps),
        evaluation_time_ms=None,
    )


def _lord_evaluation(
    definition: CareerCandidateDefinition,
    facts: CareerPreparedFacts,
) -> CareerCandidateEvaluation:
    lord = definition.normalized_parameters["lord"]
    fact_id = f"career.fact.{definition.candidate_id}"
    planet = next((item for item in facts.planets if item.planet_id == lord), None)
    inputs = {"lord": lord, "accepted_dignities": ("own_sign", "exalted")}
    if planet is None:
        error = _safe_error(
            "missing_house_lord_entity", "The selected house-lord planet is unavailable.",
            fact_id, {"house": 10, "lord": lord},
        )
        step = _trace(
            f"{fact_id}.lookup", "lookup_house_lord_planet", inputs,
            {"entity_state": "absent"}, error_code=error.code,
        )
        fact = CareerFactResult(
            fact_id=fact_id, fact_version=CAREER_FACT_VERSION,
            fact_kind=CareerFactKind.HOUSE_LORD_STATUS, matched=False,
            status=PredicateStatus.MISSING_CAPABILITY, inputs=inputs, evidence={"lord": lord},
            errors=(error,), trace_steps=(step,), backing_result=None, evaluation_time_ms=None,
        )
        adjusted = 0.0
        legacy_evidence = {}
    else:
        observation = _effective_dignity(planet)
        legacy_evidence = {"lord": lord, "dignity": observation.value}
        if not observation.present:
            error = _safe_error(
                "missing_house_lord_dignity_fact", "The selected house-lord dignity fact is unavailable.",
                fact_id, {"house": 10, "lord": lord, "fact": "dignity"},
            )
            step = _trace(
                f"{fact_id}.comparison", "compare_house_lord_dignity", inputs,
                {"dignity_state": "absent"}, error_code=error.code,
            )
            fact = CareerFactResult(
                fact_id=fact_id, fact_version=CAREER_FACT_VERSION,
                fact_kind=CareerFactKind.HOUSE_LORD_STATUS, matched=False,
                status=PredicateStatus.MISSING_CAPABILITY, inputs=inputs,
                evidence={"lord": lord, "dignity": None, "dignity_source": observation.source},
                errors=(error,), trace_steps=(step,), backing_result=None, evaluation_time_ms=None,
            )
            adjusted = definition.unmatched_score
        else:
            matched = observation.value in ("own_sign", "exalted")
            status = PredicateStatus.MATCHED if matched else PredicateStatus.UNMATCHED
            step = _trace(
                f"{fact_id}.comparison", "compare_house_lord_dignity", inputs,
                {"dignity": observation.value, "dignity_source": observation.source, "matched": matched},
            )
            fact = CareerFactResult(
                fact_id=fact_id, fact_version=CAREER_FACT_VERSION,
                fact_kind=CareerFactKind.HOUSE_LORD_STATUS, matched=matched, status=status,
                inputs=inputs, evidence={"lord": lord, "dignity": observation.value, "dignity_source": observation.source},
                errors=(), trace_steps=(step,), backing_result=None, evaluation_time_ms=None,
            )
            adjusted = definition.matched_score if matched else definition.unmatched_score
    contribution = float(adjusted) if fact.matched and adjusted > 0 else 0.0
    return CareerCandidateEvaluation(
        definition=definition, fact=fact, matched=fact.matched, status=fact.status,
        adjusted_score=round(float(adjusted), 3), contribution=contribution,
        compatibility_evidence=legacy_evidence,
        trace_lineage=tuple(step.step_id for step in fact.trace_steps), evaluation_time_ms=None,
    )


def _rajayoga_evaluation(
    definition: CareerCandidateDefinition,
    facts: CareerPreparedFacts,
) -> CareerCandidateEvaluation:
    occ1 = [item.planet_id for item in facts.planets if item.house == 1 and item.planet_id in _BENEFICS]
    occ10 = [item.planet_id for item in facts.planets if item.house == 10 and item.planet_id in _BENEFICS]
    matched = bool(occ1 and occ10)
    status = PredicateStatus.MATCHED if matched else PredicateStatus.UNMATCHED
    fact_id = f"career.fact.{definition.candidate_id}"
    evidence = {"occ1": occ1, "occ10": occ10}
    step = _trace(
        f"{fact_id}.comparison", "rajayoga_legacy_compatibility",
        {"benefic_names": ("Jupiter", "Venus", "Mercury", "Moon"), "houses": (1, 10)},
        {"occ1": occ1, "occ10": occ10, "matched": matched},
    )
    fact = CareerFactResult(
        fact_id=fact_id, fact_version=CAREER_FACT_VERSION,
        fact_kind=CareerFactKind.RAJAYOGA_COMPATIBILITY,
        matched=matched, status=status,
        inputs={"houses": (1, 10), "benefic_names": ("Jupiter", "Venus", "Mercury", "Moon")},
        evidence=evidence, errors=(), trace_steps=(step,), backing_result=None,
        evaluation_time_ms=None,
    )
    adjusted = definition.matched_score if matched else definition.unmatched_score
    return CareerCandidateEvaluation(
        definition=definition, fact=fact, matched=matched, status=status,
        adjusted_score=round(float(adjusted), 3),
        contribution=float(adjusted) if matched and adjusted > 0 else 0.0,
        compatibility_evidence=evidence,
        trace_lineage=(step.step_id,), evaluation_time_ms=None,
    )


def _failed_candidate_evaluation(
    definition: CareerCandidateDefinition,
) -> CareerCandidateEvaluation:
    fact_id = f"career.fact.{definition.candidate_id}"
    error = _safe_error(
        "career_candidate_evaluation_failed",
        "The Career candidate could not be evaluated safely.",
        fact_id,
        {"candidate_id": definition.candidate_id, "rule_type": definition.rule_type},
        recoverable=False,
    )
    step = _trace(
        f"{fact_id}.error",
        "career_candidate_evaluation",
        {"candidate_id": definition.candidate_id},
        {"completed": False, "status": PredicateStatus.ERROR.value},
        error_code=error.code,
    )
    fact = CareerFactResult(
        fact_id=fact_id,
        fact_version=CAREER_FACT_VERSION,
        fact_kind={
            "strong_in_10": CareerFactKind.STRONG_IN_HOUSE,
            "lord_status": CareerFactKind.HOUSE_LORD_STATUS,
            "rajayoga_naive": CareerFactKind.RAJAYOGA_COMPATIBILITY,
        }[definition.rule_type],
        matched=False,
        status=PredicateStatus.ERROR,
        inputs=definition.normalized_parameters,
        evidence={"candidate_id": definition.candidate_id},
        errors=(error,),
        trace_steps=(step,),
        backing_result=None,
        evaluation_time_ms=None,
    )
    return CareerCandidateEvaluation(
        definition=definition,
        fact=fact,
        matched=False,
        status=PredicateStatus.ERROR,
        adjusted_score=0.0,
        contribution=0.0,
        compatibility_evidence={},
        trace_lineage=(step.step_id,),
        evaluation_time_ms=None,
    )


def _failed_base_evaluation() -> _BaseEvaluation:
    fact_id = "career.fact.base_kendra_strength"
    error = _safe_error(
        "career_base_evaluation_failed",
        "The Career base/component facts could not be evaluated safely.",
        fact_id,
        {"stage": "base_components"},
        recoverable=False,
    )
    step = _trace(
        f"{fact_id}.error", "career_base_component_evaluation", {},
        {"completed": False, "legacy_fallback": 0.5}, error_code=error.code,
    )
    fact = CareerFactResult(
        fact_id=fact_id, fact_version=CAREER_FACT_VERSION,
        fact_kind=CareerFactKind.BASE_KENDRA_STRENGTH,
        matched=False, status=PredicateStatus.ERROR,
        inputs={"houses": (1, 4, 7, 10), "empty_fallback": 0.5},
        evidence={"base_score": 0.5, "compatibility_policy": "empty_base_fallback"},
        errors=(error,), trace_steps=(step,), backing_result=None,
        evaluation_time_ms=None,
    )
    return _BaseEvaluation(0.5, (fact,), (), error)


def _base_and_component_facts(
    facts: CareerPreparedFacts,
) -> _BaseEvaluation:
    selected = tuple(item for item in facts.planets if item.house in _KENDRA)
    legacy_strengths = tuple(item.strength or 0.0 for item in selected)
    base_score = sum(legacy_strengths) / len(legacy_strengths) if legacy_strengths else 0.5
    missing = tuple(item.planet_id for item in selected if not item.strength_present)
    base_id = "career.fact.base_kendra_strength"
    base_trace = _trace(
        f"{base_id}.aggregate", "average_kendra_planet_strengths",
        {"houses": (1, 4, 7, 10), "empty_fallback": 0.5},
        {"planets": tuple(item.planet_id for item in selected), "strengths": legacy_strengths, "base_score": base_score},
        error_code="missing_base_strength_fact" if missing else None,
    )
    base_errors = ()
    base_status = PredicateStatus.MATCHED
    if missing:
        base_status = PredicateStatus.MISSING_CAPABILITY
        base_errors = (_safe_error(
            "missing_base_strength_fact", "One or more selected base strength facts are unavailable.",
            base_id, {"planets": missing},
        ),)
    base_fact = CareerFactResult(
        fact_id=base_id, fact_version=CAREER_FACT_VERSION,
        fact_kind=CareerFactKind.BASE_KENDRA_STRENGTH,
        matched=base_status is PredicateStatus.MATCHED, status=base_status,
        inputs={"houses": (1, 4, 7, 10), "empty_fallback": 0.5},
        evidence={
            "selected_planets": tuple(item.planet_id for item in selected),
            "strengths": legacy_strengths, "base_score": base_score,
            "missing_strength_planets": missing,
        },
        errors=base_errors, trace_steps=(base_trace,), backing_result=None,
        evaluation_time_ms=None,
    )

    components = []
    for item, strength in zip(selected, legacy_strengths):
        weight = round(float(strength - 0.5), 3)
        fact_id = f"career.fact.component.planet.{item.source_index}"
        errors = ()
        status = PredicateStatus.MATCHED
        if not item.strength_present:
            status = PredicateStatus.MISSING_CAPABILITY
            errors = (_safe_error(
                "missing_component_strength_fact", "The planet component strength fact is unavailable.",
                fact_id, {"planet": item.planet_id},
            ),)
        trace = _trace(
            f"{fact_id}.weight", "planet_component_weight",
            {"neutral_baseline": 0.5},
            {"planet": item.planet_id, "house": item.house, "legacy_strength": strength, "weight": weight},
            error_code=errors[0].code if errors else None,
        )
        components.append(CareerFactResult(
            fact_id=fact_id, fact_version=CAREER_FACT_VERSION,
            fact_kind=CareerFactKind.BASE_KENDRA_STRENGTH,
            matched=status is PredicateStatus.MATCHED, status=status,
            inputs={"planet": item.planet_id, "house": item.house, "neutral_baseline": 0.5},
            evidence={"planet": item.planet_id, "house": item.house, "weight": weight},
            errors=errors, trace_steps=(trace,), backing_result=None, evaluation_time_ms=None,
        ))

    if facts.house10 is not None:
        occupant_strengths = []
        unavailable = []
        for name in facts.house10.occupants:
            planet = next((item for item in facts.planets if item.planet_id == name), None)
            if planet is None:
                unavailable.append(str(name))
            elif planet.strength is not None:
                occupant_strengths.append(float(planet.strength))
            else:
                unavailable.append(str(name))
        house_strength = round(sum(occupant_strengths) / len(occupant_strengths), 3) if occupant_strengths else 0.0
        weight = round(float(house_strength - 0.5), 3) if occupant_strengths else 0.0
        fact_id = "career.fact.component.house.10"
        errors = ()
        status = PredicateStatus.MATCHED
        if unavailable:
            status = PredicateStatus.MISSING_CAPABILITY
            errors = (_safe_error(
                "missing_house_occupant_strength_fact",
                "One or more 10th-house occupant strength facts are unavailable.",
                fact_id, {"house": 10, "occupants": tuple(unavailable)},
            ),)
        trace = _trace(
            f"{fact_id}.weight", "tenth_house_component_weight",
            {"neutral_baseline": 0.5},
            {"occupants": facts.house10.occupants, "strengths": tuple(occupant_strengths), "house_strength": house_strength, "weight": weight},
            error_code=errors[0].code if errors else None,
        )
        components.append(CareerFactResult(
            fact_id=fact_id, fact_version=CAREER_FACT_VERSION,
            fact_kind=CareerFactKind.TENTH_HOUSE_OCCUPANT_STRENGTH,
            matched=status is PredicateStatus.MATCHED, status=status,
            inputs={"house": 10, "neutral_baseline": 0.5},
            evidence={"house": 10, "occupants": facts.house10.occupants, "weight": weight, "house_strength": house_strength},
            errors=errors, trace_steps=(trace,), backing_result=None, evaluation_time_ms=None,
        ))
    return _BaseEvaluation(float(base_score), (base_fact,), tuple(components))


def evaluate_career_batch(
    prepared_facts: CareerPreparedFacts,
    *,
    evaluator: PredicateEvaluator | None = None,
) -> CareerEvaluationBatch:
    """Evaluate every fixed Career candidate into one immutable typed batch."""

    if not isinstance(prepared_facts, CareerPreparedFacts):
        raise TypeError("prepared_facts must be CareerPreparedFacts")
    digest = career_prepared_facts_sha256(prepared_facts)
    if prepared_facts.preparation_errors:
        return CareerEvaluationBatch(
            schema_version=CAREER_SCHEMA_VERSION,
            evaluator_version=CAREER_EVALUATOR_VERSION,
            prepared_facts_sha256=digest,
            candidates=(), base_facts=(), component_facts=(), base_score=0.5,
            confidence_denominator=0, completeness=prepared_facts.completeness,
            batch_errors=prepared_facts.preparation_errors, evaluation_time_ms=None,
        )

    active_evaluator = PredicateEvaluator() if evaluator is None else evaluator
    if not isinstance(active_evaluator, PredicateEvaluator):
        raise TypeError("evaluator must be PredicateEvaluator or None")
    context = PredicateEvaluationContext()
    evaluations = []
    for definition in _candidate_catalog(prepared_facts):
        try:
            if definition.rule_type == "strong_in_10":
                result = _strong_evaluation(definition, prepared_facts, active_evaluator, context)
            elif definition.rule_type == "lord_status":
                result = _lord_evaluation(definition, prepared_facts)
            else:
                result = _rajayoga_evaluation(definition, prepared_facts)
        except Exception:
            # Safe typed recovery retains the candidate and denominator.  No
            # exception text/type/path is copied and status is never relabeled
            # as factual unmatched.
            result = _failed_candidate_evaluation(definition)
        evaluations.append(result)
    batch_errors = ()
    try:
        base_evaluation = _base_and_component_facts(prepared_facts)
    except Exception:
        base_evaluation = _failed_base_evaluation()
        batch_errors = (base_evaluation.error,)
    return CareerEvaluationBatch(
        schema_version=CAREER_SCHEMA_VERSION,
        evaluator_version=CAREER_EVALUATOR_VERSION,
        prepared_facts_sha256=digest,
        candidates=tuple(evaluations),
        base_facts=base_evaluation.base_facts,
        component_facts=base_evaluation.component_facts,
        base_score=base_evaluation.base_score,
        confidence_denominator=len(evaluations),
        completeness=prepared_facts.completeness,
        batch_errors=batch_errors,
        evaluation_time_ms=None,
    )


def _legacy_evidence(item: CareerCandidateEvaluation) -> dict[str, Any]:
    evidence = item.compatibility_evidence
    if item.definition.rule_type == "strong_in_10":
        return {"planet": evidence.get("planet"), "house": evidence.get("house"), "strength": evidence.get("strength")}
    if item.definition.rule_type == "lord_status":
        return {"lord": evidence.get("lord"), "dignity": evidence.get("dignity")}
    return {"occ1": list(evidence.get("occ1", ())), "occ10": list(evidence.get("occ10", ())) }


def _public_components(batch: CareerEvaluationBatch) -> list[dict[str, Any]]:
    output = []
    for fact in batch.component_facts:
        if fact.fact_kind is CareerFactKind.BASE_KENDRA_STRENGTH:
            output.append({
                "type": "planet",
                "planet": fact.evidence["planet"],
                "house": fact.evidence["house"],
                "weight": fact.evidence["weight"],
            })
        else:
            output.append({
                "type": "house",
                "house": 10,
                "weight": fact.evidence["weight"],
                "occupants": list(fact.evidence["occupants"]),
            })
    return output


def _confidence_input(completeness: Mapping[str, Any]) -> SimpleNamespace:
    return SimpleNamespace(
        lagna_sign="present" if completeness["lagna_present"] else None,
        planets=(True,) if completeness["planets_present"] else (),
        houses=(True,) if completeness["houses_present"] else (),
        metadata={"birth_datetime_utc": True} if completeness["birth_datetime_present"] else {},
    )


def project_career_compatibility(batch: CareerEvaluationBatch) -> dict[str, Any]:
    """Lossily project a typed batch into the unchanged public Career dict."""

    if not isinstance(batch, CareerEvaluationBatch):
        raise TypeError("batch must be CareerEvaluationBatch")
    indicators = []
    evidence_rows = []
    contributions = []
    for item in batch.candidates:
        if item.matched and item.adjusted_score > 0:
            contribution = float(item.adjusted_score)
            contributions.append(contribution)
            context = thaw_ordered_compatibility(item.definition.compatibility_context)
            evidence = _legacy_evidence(item)
            indicators.append({
                "rule_id": item.definition.candidate_id,
                "contribution": contribution,
                "evidence": evidence,
                "context": context,
            })
            evidence_rows.append(explainability.evidence_for_rule(
                item.definition.candidate_id,
                thaw_ordered_compatibility(item.definition.compatibility_context),
                {"match": True, "evidence": _legacy_evidence(item)},
                contribution,
            ))

    components = _public_components(batch)
    for item in indicators:
        components.append({
            "type": "rule",
            "rule_id": item.get("rule_id"),
            "weight": round(float(item.get("contribution") or 0.0), 3),
        })
    scoring = explainability.scoring_breakdown(batch.base_score, contributions)
    final = scoring.get("final_score", batch.base_score)
    rule_matches = [
        {"matched": True, "adjusted_score": item.get("contribution")}
        for item in evidence_rows
    ]
    confidence = confidence_mod.compute_confidence(
        rule_matches,
        max(1, batch.confidence_denominator),
        _confidence_input(batch.completeness),
    )
    summary_text = f"Career score {round(float(final),3)} (confidence {round(float(confidence),3)})"
    return {
        "summary": summary_text,
        "score": round(float(final), 3),
        "confidence": round(float(confidence), 3),
        "components": components,
        "indicators": indicators,
        "evidence": evidence_rows,
        "scoring": scoring,
        "trace_id": "career_001",
    }


def interpret_career(astro: AstroState) -> dict[str, Any]:
    """Existing public wrapper over the one-way WP15 typed bridge."""

    prepared = prepare_career_facts(astro)
    batch = evaluate_career_batch(prepared)
    return project_career_compatibility(batch)


__all__ = (
    "evaluate_career_batch",
    "interpret_career",
    "prepare_career_facts",
    "project_career_compatibility",
)
