"""WP15 typed factual bridge for the existing Career compatibility output."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import PureWindowsPath
from types import SimpleNamespace
from typing import Any

from systems.Parasara.engine.astrostate import AstroState
from systems.Parasara.engine.astrostate_api import (
    AstroStateBuildFailure,
    AstroStateSnapshot,
    freeze_astrostate,
)
from systems.Parasara.engine.capability import CapabilityFactState, CapabilityReadiness
from systems.Parasara.engine.domain import (
    CareerCompatibilityProjection,
    CareerComponentCompatibility,
    CareerComponentKind,
    CareerIndicatorCompatibility,
    DomainBuildOutcome,
    DomainBuildProduced,
    DomainBuildRejected,
    DomainComponent,
    DomainId,
    DomainIndicator,
    DomainIssue,
    DomainIssueSeverity,
    DomainPrediction,
    DomainPredictionFactory,
    NarrativeSection,
    NarrativeSectionType,
    compatibility_value,
)
from systems.Parasara.engine.inference import (
    CapabilityAvailability,
    DataCompleteness,
    InferenceConfig,
    InferenceEngine,
    InferenceCompatibilityProjection,
    InferenceResult,
    inference_config_logical_sha256,
    load_inference_config,
)
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
from systems.Parasara.engine.output_assembler import (
    project_career_prediction_compatibility,
)
from systems.Parasara.engine.domain.models import _build_domain_indicator
from systems.Parasara.engine.rules.canonical import canonical_json_data
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.models import (
    PredicateError,
    PredicateStatus,
    PredicateTraceStep,
)
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    context_canonical_projection,
    prepare_predicate_state,
)
from systems.Parasara.engine.rules.rule_engine import ResolvedRule, RuleEngine
from systems.Parasara.engine.rules.rule_match import (
    RuleMatch,
    RuleMatchError,
    RuleMatchStatus,
    RuleTraceReference,
    rule_match_logical_sha256,
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


def prepare_career_facts(astro: AstroState | AstroStateSnapshot) -> CareerPreparedFacts:
    """Compatibility adapter into canonical snapshot-based Career preparation."""

    if isinstance(astro, AstroStateSnapshot):
        return prepare_career_snapshot(astro)
    if not isinstance(astro, AstroState):
        return _failed_preparation()
    build = freeze_astrostate(astro)
    if isinstance(build, AstroStateBuildFailure):
        return _failed_preparation()
    return prepare_career_snapshot(build.snapshot)


def prepare_career_snapshot(snapshot: AstroStateSnapshot) -> CareerPreparedFacts:
    """Build the protected Career bridge only from typed factual queries."""

    if not isinstance(snapshot, AstroStateSnapshot):
        return _failed_preparation()

    def prepare() -> CareerPreparedFacts:
        # Supply only the exact occupancy boundary needed by Career.  Signs,
        # Aspects, roles, dignity, Yoga output, and all other enrichments are
        # intentionally absent from this canonical predicate state.
        planets_result = snapshot.get_planets()
        if planets_result.state is not CapabilityFactState.PRESENT:
            return _failed_preparation()
        # The stable query uses canonical catalog order.  Current production
        # construction order is the same protected Career source order.
        queried_planets = planets_result.value
        predicate_source = SimpleNamespace(
            planets=[
                SimpleNamespace(
                    name=planet.planet_id,
                    house=(
                        snapshot.get_planet_house(planet.planet_id).value
                        if snapshot.get_planet_house(planet.planet_id).value_present
                        else None
                    ),
                    sign=None,
                )
                for planet in queried_planets
            ],
            lagna_sign=None,
            enrichments={},
            derived=None,
            metadata={},
        )
        outcome = prepare_predicate_state(predicate_source)
        if not outcome.succeeded or outcome.state is None:
            return _failed_preparation()

        planets = []
        by_id = {}
        for index, planet in enumerate(queried_planets):
            placement = snapshot.get_planet_house(planet.planet_id)
            strength_result = snapshot.get_planet_strength(planet.planet_id)
            dignity_result = snapshot.get_planet_dignity(planet.planet_id)
            strength_map = (
                strength_result.value.value
                if strength_result.value_present else {}
            )
            dignity = dignity_result.value if dignity_result.value_present else None
            base_strength = strength_map.get("value") if isinstance(strength_map, Mapping) else None
            strength_present = bool(
                isinstance(strength_map, Mapping) and strength_map.get("value_present")
            )
            enriched_strength = strength_map.get("enriched_value") if isinstance(strength_map, Mapping) else None
            enriched_strength_present = bool(
                isinstance(strength_map, Mapping) and strength_map.get("enriched_value_present")
            )
            base_dignity = dignity.value if dignity is not None else None
            dignity_present = dignity.value_present if dignity is not None else False
            enriched_dignity = dignity.enriched_value if dignity is not None else None
            enriched_dignity_present = dignity.enriched_value_present if dignity is not None else False
            item = CareerPlanetFact(
                planet_id=planet.planet_id,
                source_index=index,
                house=placement.value if placement.value_present else None,
                strength=base_strength,
                strength_present=strength_present,
                enriched_strength=enriched_strength,
                enriched_strength_present=enriched_strength_present,
                dignity=base_dignity,
                dignity_present=dignity_present,
                enriched_dignity=enriched_dignity,
                enriched_dignity_present=enriched_dignity_present,
            )
            planets.append(item)
            by_id[planet.planet_id] = {
                "source_index": index,
                "house": placement.value if placement.value_present else None,
                "strength": base_strength,
                "strength_present": strength_present,
                "enriched_strength": enriched_strength,
                "enriched_strength_present": enriched_strength_present,
                "dignity": base_dignity,
                "dignity_present": dignity_present,
                "enriched_dignity": enriched_dignity,
                "enriched_dignity_present": enriched_dignity_present,
            }

        lord_result = snapshot.get_house_lord(10)
        occupants_result = snapshot.get_occupants(10)
        summary_result = snapshot.get_house_summary(10)
        summary = summary_result.value if summary_result.value_present else {}
        lord_present = lord_result.value_present or "lord" in summary
        occupants_present = occupants_result.value_present or "occupants" in summary
        house10 = None
        if lord_present or occupants_present:
            house10 = CareerHouse10Fact(
                lord=lord_result.value if lord_result.value_present else None,
                lord_present=lord_present,
                occupants=(
                    tuple(occupants_result.value)
                    if occupants_result.value_present else tuple(summary.get("occupants", ()))
                ),
                occupants_present=occupants_present,
            )

        lagna = snapshot.get_lagna()
        houses = snapshot.get_houses()
        metadata_result = snapshot.get_chart_metadata()
        metadata = metadata_result.value if metadata_result.value_present else {}
        completeness = {
            "lagna_present": lagna.value_present,
            "planets_present": bool(queried_planets),
            "houses_present": bool(houses.value_present and houses.value),
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
    return prepare()


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


_RULE_ENGINE = RuleEngine()
_CAREER_INFERENCE_CONFIG = load_inference_config()


@dataclass(frozen=True, slots=True)
class _CareerRuleMatchLedger:
    """Private complete RuleMatch membership and contribution lineage."""

    rule_matches: tuple[RuleMatch, ...]
    rule_match_digests: tuple[str, ...]
    contribution_lineage: tuple[tuple[str, str, str, str], ...]

    def resolve(self, rule_match: RuleMatch) -> RuleMatch:
        identity = (rule_match.rule_id, rule_match.rule_version, rule_match.trace_id)
        for authoritative in self.rule_matches:
            if (
                authoritative.rule_id,
                authoritative.rule_version,
                authoritative.trace_id,
            ) == identity:
                if rule_match_logical_sha256(rule_match) != rule_match_logical_sha256(
                    authoritative
                ):
                    raise ValueError("Career RuleMatch differs from its ledger member")
                return authoritative
        raise ValueError("Career RuleMatch is not a member of the evaluator ledger")


@dataclass(frozen=True, slots=True)
class _CareerInferenceEvaluation:
    """Private one-run authority consumed only by Career domain construction."""

    batch: CareerEvaluationBatch
    config: InferenceConfig
    config_fingerprint: str
    ledger: _CareerRuleMatchLedger
    inference_result: InferenceResult
    compatibility_projection: InferenceCompatibilityProjection
    components: tuple[DomainComponent, ...]
    indicators: tuple[DomainIndicator, ...]
    career_compatibility: CareerCompatibilityProjection


def _career_rule_status(status: PredicateStatus) -> RuleMatchStatus:
    return {
        PredicateStatus.MATCHED: RuleMatchStatus.MATCHED,
        PredicateStatus.UNMATCHED: RuleMatchStatus.UNMATCHED,
        PredicateStatus.SKIPPED: RuleMatchStatus.SKIPPED,
        PredicateStatus.MISSING_CAPABILITY: RuleMatchStatus.MISSING_CAPABILITY,
        PredicateStatus.INVALID_PARAMETERS: RuleMatchStatus.INVALID,
        PredicateStatus.ERROR: RuleMatchStatus.ERROR,
        PredicateStatus.TIMEOUT: RuleMatchStatus.ERROR,
    }[status]


def _resolved_career_rule(definition: CareerCandidateDefinition) -> ResolvedRule:
    compatibility = thaw_ordered_compatibility(definition.compatibility_context)
    raw_version = definition.rule_version
    raw_priority = compatibility.get("priority")
    priority = raw_priority if type(raw_priority) is int else 0
    raw_family = compatibility.get("family")
    rule_family = raw_family if isinstance(raw_family, str) and raw_family else definition.rule_type
    raw_category = compatibility.get("category")
    category = raw_category if isinstance(raw_category, str) and raw_category else definition.rule_type
    base_weight = definition.base_score
    weights = compatibility.get("weights")
    if base_weight is None and isinstance(weights, Mapping):
        base_weight = weights.get("base")
    if isinstance(base_weight, bool) or not isinstance(base_weight, (int, float)):
        raise ValueError("Career compatibility rule requires a declared finite base weight")
    provenance = {"source_identity": definition.source_identity}
    raw_provenance = compatibility.get("provenance")
    if isinstance(raw_provenance, str) and raw_provenance:
        provenance["source"] = raw_provenance
    for key in (
        "author", "source_reference", "classical_reference",
        "validation_status", "sme_required", "sme_approved",
    ):
        if key in compatibility:
            provenance[key] = compatibility[key]
    metadata = {
        "rule_type": definition.rule_type,
        "source_identity": definition.source_identity,
    }
    for key in ("name", "description"):
        if isinstance(compatibility.get(key), str):
            metadata[key] = compatibility[key]
    if raw_version is None:
        metadata["diagnostic_missing_rule_version"] = True
    if type(raw_priority) is not int:
        metadata["diagnostic_missing_priority"] = True
    return ResolvedRule(
        system="parashara",
        rule_id=definition.candidate_id,
        rule_version=raw_version or "legacy-unversioned",
        rule_family=rule_family,
        rule_set_version="v1",
        category=category,
        domains=("career",),
        base_weight=base_weight,
        priority=priority,
        context="natal",
        quality=None,
        provenance=provenance,
        metadata=metadata,
        evaluation_plan_position=definition.source_index,
    )


def _candidate_evaluation(
    definition: CareerCandidateDefinition,
    fact: CareerFactResult,
    *,
    adjusted_score: float,
    contribution: float,
    compatibility_evidence: Mapping[str, Any],
    evaluation_snapshot_digest: str,
    evaluation_context: PredicateEvaluationContext,
) -> CareerCandidateEvaluation:
    trace_lineage = tuple(step.step_id for step in fact.trace_steps)
    rule_errors = tuple(
        RuleMatchError(
            code=error.code,
            message=error.message,
            phase="career_fact_bridge",
            recoverable=error.recoverable,
            details=error.details,
            source_predicate_id=error.predicate_id,
            source_trace_id=trace_lineage[0] if trace_lineage else None,
        )
        for error in fact.errors
    )
    trace_references = tuple(
        RuleTraceReference(
            trace_id=step_id,
            trace_type="career_fact",
            relation="compatibility_fact",
            order=index,
        )
        for index, step_id in enumerate(trace_lineage)
    )
    resolved_rule = _resolved_career_rule(definition)
    rule_match = _RULE_ENGINE.build_match(
        resolved_rule,
        fact.backing_result,
        evaluation_snapshot_digest=evaluation_snapshot_digest,
        evaluation_context=context_canonical_projection(evaluation_context),
        status_override=_career_rule_status(fact.status),
        evidence={
            "fact_id": fact.fact_id,
            "fact_kind": fact.fact_kind.value,
            "fact_trace_ids": trace_lineage,
        },
        errors=rule_errors,
        additional_trace_references=trace_references,
        trace_components=(
            CAREER_EVALUATOR_VERSION,
            definition.candidate_id,
            resolved_rule.rule_version,
            str(definition.source_index),
            evaluation_snapshot_digest,
            fact.status.value,
            *trace_lineage,
        ),
    )
    return CareerCandidateEvaluation(
        definition=definition,
        fact=fact,
        rule_match=rule_match,
        adjusted_score=round(float(adjusted_score), 3),
        contribution=float(contribution),
        compatibility_evidence=compatibility_evidence,
        trace_lineage=trace_lineage,
        evaluation_time_ms=None,
    )


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
    evaluation_snapshot_digest: str,
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
    return _candidate_evaluation(
        definition,
        fact,
        adjusted_score=adjusted,
        contribution=contribution,
        compatibility_evidence=compatibility_evidence,
        evaluation_snapshot_digest=evaluation_snapshot_digest,
        evaluation_context=context,
    )


def _lord_evaluation(
    definition: CareerCandidateDefinition,
    facts: CareerPreparedFacts,
    context: PredicateEvaluationContext,
    evaluation_snapshot_digest: str,
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
    return _candidate_evaluation(
        definition,
        fact,
        adjusted_score=adjusted,
        contribution=contribution,
        compatibility_evidence=legacy_evidence,
        evaluation_snapshot_digest=evaluation_snapshot_digest,
        evaluation_context=context,
    )


def _rajayoga_evaluation(
    definition: CareerCandidateDefinition,
    facts: CareerPreparedFacts,
    context: PredicateEvaluationContext,
    evaluation_snapshot_digest: str,
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
    return _candidate_evaluation(
        definition,
        fact,
        adjusted_score=adjusted,
        contribution=float(adjusted) if matched and adjusted > 0 else 0.0,
        compatibility_evidence=evidence,
        evaluation_snapshot_digest=evaluation_snapshot_digest,
        evaluation_context=context,
    )


def _failed_candidate_evaluation(
    definition: CareerCandidateDefinition,
    context: PredicateEvaluationContext,
    evaluation_snapshot_digest: str,
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
    return _candidate_evaluation(
        definition,
        fact,
        adjusted_score=0.0,
        contribution=0.0,
        compatibility_evidence={},
        evaluation_snapshot_digest=evaluation_snapshot_digest,
        evaluation_context=context,
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
        if definition.rule_type == "strong_in_10":
            result = _strong_evaluation(definition, prepared_facts, active_evaluator, context, digest)
        elif definition.rule_type == "lord_status":
            result = _lord_evaluation(definition, prepared_facts, context, digest)
        else:
            result = _rajayoga_evaluation(definition, prepared_facts, context, digest)
        evaluations.append(result)
    base_evaluation = _base_and_component_facts(prepared_facts)
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
        batch_errors=(),
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


def _baseline_rule_match(batch: CareerEvaluationBatch, config: InferenceConfig) -> Any:
    """Represent the legacy per-chart base as explicit universal rule meaning."""

    if not batch.base_facts:
        return None
    fact = batch.base_facts[0]
    trace_lineage = tuple(step.step_id for step in fact.trace_steps)
    status = _career_rule_status(fact.status)
    # Missing strength is not adverse evidence. The historical zero-substitution
    # remains in the factual batch for compatibility diagnostics, but inference
    # receives a neutral unavailable baseline instead of a negative weight.
    compatibility = config.career_compatibility
    neutral = float(compatibility["baseline_neutral"])
    base_weight = batch.base_score - neutral if status is RuleMatchStatus.MATCHED else 0.0
    resolved = ResolvedRule(
        system="parashara",
        rule_id=compatibility["baseline_rule_id"],
        rule_version=CAREER_FACT_VERSION,
        rule_family="career_compatibility",
        rule_set_version="v1",
        category=compatibility["baseline_category"],
        domains=("career",),
        base_weight=base_weight,
        priority=compatibility["baseline_priority"],
        context="natal",
        quality=None,
        provenance={"source_identity": "career.fact.base_kendra_strength"},
        metadata={
            "inference_role": "compatibility_baseline",
            "confidence_eligible": False,
            "correlation_key": fact.fact_id,
        },
        evaluation_plan_position=0,
    )
    errors = tuple(RuleMatchError(
        code=error.code,
        message=error.message,
        phase="career_fact_bridge",
        recoverable=error.recoverable,
        details=error.details,
        source_predicate_id=error.predicate_id,
        source_trace_id=trace_lineage[0] if trace_lineage else None,
    ) for error in fact.errors)
    references = tuple(RuleTraceReference(
        trace_id=step_id,
        trace_type="career_fact",
        relation="compatibility_baseline",
        order=index,
    ) for index, step_id in enumerate(trace_lineage))
    return _RULE_ENGINE.build_match(
        resolved,
        fact.backing_result,
        evaluation_snapshot_digest=batch.prepared_facts_sha256,
        evaluation_context={"domain": "career", "context": "natal"},
        status_override=status,
        evidence={
            "fact_id": fact.fact_id,
            "fact_kind": fact.fact_kind.value,
            "base_score": batch.base_score if status is RuleMatchStatus.MATCHED else neutral,
            "fact_trace_ids": trace_lineage,
        },
        errors=errors,
        additional_trace_references=references,
        trace_components=(
            CAREER_EVALUATOR_VERSION, "career.base_kendra_strength",
            batch.prepared_facts_sha256, status.value, *trace_lineage,
        ),
    )


def career_inference_rule_matches(
    batch: CareerEvaluationBatch,
    config: InferenceConfig | None = None,
) -> tuple[Any, ...]:
    if not isinstance(batch, CareerEvaluationBatch):
        raise TypeError("batch must be CareerEvaluationBatch")
    active_config = _CAREER_INFERENCE_CONFIG if config is None else config
    baseline = _baseline_rule_match(batch, active_config)
    values = (*batch.rule_matches, *((baseline,) if baseline is not None else ()))
    return RuleEngine.order_matches(values)


def career_data_completeness(
    batch: CareerEvaluationBatch,
    config: InferenceConfig | None = None,
) -> DataCompleteness:
    if not isinstance(batch, CareerEvaluationBatch):
        raise TypeError("batch must be CareerEvaluationBatch")
    active_config = _CAREER_INFERENCE_CONFIG if config is None else config
    policy = active_config.completeness["career"]
    checks = tuple(bool(batch.completeness[name]) for name in policy["legacy_checks"])
    score = sum(checks) * float(policy["legacy_check_weight"])
    d1 = (
        CapabilityAvailability.AVAILABLE if all(checks)
        else CapabilityAvailability.PARTIAL if any(checks)
        else CapabilityAvailability.UNAVAILABLE
    )
    required = tuple(sorted(policy["required_capabilities"]))
    optional = tuple(sorted(policy["optional_capabilities"]))
    availability = {"d1": d1, "rule_pack": CapabilityAvailability.AVAILABLE}
    missing_required = tuple(
        name for name in required
        if availability.get(name, CapabilityAvailability.NOT_REQUIRED)
        in (CapabilityAvailability.PARTIAL, CapabilityAvailability.UNAVAILABLE)
    )
    missing_optional = tuple(
        name for name in optional
        if availability.get(name, CapabilityAvailability.NOT_REQUIRED)
        in (CapabilityAvailability.PARTIAL, CapabilityAvailability.UNAVAILABLE)
    )
    return DataCompleteness(
        domain="career",
        d1=d1,
        d9=CapabilityAvailability.NOT_REQUIRED,
        d10=CapabilityAvailability.NOT_REQUIRED,
        aspects=CapabilityAvailability.NOT_REQUIRED,
        functional_roles=CapabilityAvailability.NOT_REQUIRED,
        shadbala=CapabilityAvailability.NOT_REQUIRED,
        dasha=CapabilityAvailability.NOT_REQUIRED,
        transits=CapabilityAvailability.NOT_REQUIRED,
        rule_pack=CapabilityAvailability.AVAILABLE,
        required_capabilities=required,
        missing_required=missing_required,
        missing_optional=missing_optional,
        completeness_score=score,
        trace_id=f"career.completeness.{batch.prepared_facts_sha256[:24]}",
    )


def _aggregate_career(
    batch: CareerEvaluationBatch,
    config: InferenceConfig,
    engine: InferenceEngine,
    *,
    rule_matches: tuple[RuleMatch, ...] | None = None,
) -> InferenceResult:
    matches = (
        career_inference_rule_matches(batch, config)
        if rule_matches is None
        else rule_matches
    )
    return engine.aggregate(
        domain="career",
        rule_matches=matches,
        timing_context=None,
        data_completeness=career_data_completeness(batch, config),
        config=config,
    )


def infer_career(
    batch: CareerEvaluationBatch,
    *,
    config: InferenceConfig | None = None,
    engine: InferenceEngine | None = None,
) -> InferenceResult:
    if not isinstance(batch, CareerEvaluationBatch):
        raise TypeError("batch must be CareerEvaluationBatch")
    active_config = _CAREER_INFERENCE_CONFIG if config is None else config
    active_engine = InferenceEngine() if engine is None else engine
    return _aggregate_career(batch, active_config, active_engine)


def _career_domain_components(
    batch: CareerEvaluationBatch,
    result: InferenceResult,
) -> tuple[DomainComponent, ...]:
    """Map locked Career component rows without creating component scores."""

    compatibility = _CAREER_INFERENCE_CONFIG.career_compatibility
    baseline_rule_id = compatibility["baseline_rule_id"]
    source = next(
        (item for item in result.components if baseline_rule_id in item.rule_ids),
        None,
    )
    if source is None:
        return ()
    public_rows = _public_components(batch)
    if len(public_rows) != len(batch.component_facts):
        raise ValueError("Career compatibility component rows lost source identity")
    output = []
    for order, (fact, public_row) in enumerate(zip(batch.component_facts, public_rows)):
        label = (
            str(public_row["planet"])
            if public_row["type"] == "planet"
            else f"House {public_row['house']}"
        )
        output.append(DomainComponent(
            component_id=fact.fact_id,
            domain=DomainId.CAREER,
            label=label,
            score=source.normalized_value,
            weight=float(public_row["weight"]),
            confidence=None,
            source_inference_component_id=source.component_id,
            contribution_ids=source.contribution_ids,
            contributing_rule_ids=source.rule_ids,
            evidence_references=source.evidence_references,
            trace_id=source.trace_id,
            order=order,
        ))
    return tuple(output)


def _career_domain_indicators(
    batch: CareerEvaluationBatch,
    result: InferenceResult,
    ledger: _CareerRuleMatchLedger,
) -> tuple[DomainIndicator, ...]:
    compatibility = _CAREER_INFERENCE_CONFIG.career_compatibility
    baseline_rule_id = compatibility["baseline_rule_id"]
    contribution_by_rule = {
        item.rule_id: item
        for item in result.contributions
        if item.rule_id != baseline_rule_id
    }
    rule_match_by_id = {item.rule_id: item for item in batch.rule_matches}
    output = []
    for item in batch.candidates:
        contribution = contribution_by_rule.get(item.definition.candidate_id)
        if contribution is None or contribution.final_contribution <= 0:
            continue
        rule_match = rule_match_by_id.get(item.definition.candidate_id)
        if rule_match is None:
            raise ValueError("Career indicator lost its authoritative RuleMatch")
        rule_match = ledger.resolve(rule_match)
        context = thaw_ordered_compatibility(item.definition.compatibility_context)
        evidence = _legacy_evidence(item)
        output.append(_build_domain_indicator(
            indicator_id=f"career.indicator.{item.definition.candidate_id}",
            domain=DomainId.CAREER,
            source_rule_id=contribution.rule_id,
            source_rule_version=contribution.rule_version,
            source_contribution_id=contribution.contribution_id,
            label=item.definition.candidate_id,
            direction=contribution.sign,
            contribution=contribution.final_contribution,
            context=contribution.context,
            priority=contribution.priority,
            evidence_summary={
                "legacy_context_ordered": item.definition.compatibility_context,
                "legacy_evidence_ordered": freeze_ordered_compatibility(evidence),
            },
            evidence_references=contribution.evidence_references,
            source_rule_trace_id=contribution.source_rule_trace_id,
            trace_id=contribution.trace_id,
            order=item.definition.source_index,
            source_rule_match=rule_match,
        ))
    return tuple(output)


def _career_domain_narrative(
    result: InferenceResult,
    indicators: tuple[DomainIndicator, ...],
    summary: str,
) -> tuple[NarrativeSection, ...]:
    return (NarrativeSection(
        section_id="career.narrative.headline",
        section_type=NarrativeSectionType.HEADLINE,
        text=summary,
        source_rule_ids=tuple(dict.fromkeys(item.rule_id for item in result.contributions)),
        source_indicator_ids=tuple(item.indicator_id for item in indicators),
        source_issue_ids=(),
        source_trace_ids=(result.trace_id,),
        template_id="career.compatibility.summary",
        template_version=CAREER_EVALUATOR_VERSION,
        order=0,
    ),)


def _career_compatibility_projection(
    batch: CareerEvaluationBatch,
    inference_projection: InferenceCompatibilityProjection,
    components: tuple[DomainComponent, ...],
    indicators: tuple[DomainIndicator, ...],
) -> CareerCompatibilityProjection:
    """Capture the locked public shape as validated, typed source data."""

    public_rows = _public_components(batch)
    component_projection = tuple(
        CareerComponentCompatibility(
            component_id=component.component_id,
            kind=CareerComponentKind(row["type"]),
            planet=(str(row["planet"]) if row["type"] == "planet" else None),
            house=int(row["house"]),
            weight=float(row["weight"]),
            occupants=tuple(str(item) for item in row.get("occupants", ())),
            source_fact_trace_ids=tuple(step.step_id for step in fact.trace_steps),
            order=component.order,
        )
        for component, fact, row in zip(components, batch.component_facts, public_rows)
    )
    candidates = {
        f"career.indicator.{item.definition.candidate_id}": item
        for item in batch.candidates
    }
    indicator_projection = tuple(
        CareerIndicatorCompatibility(
            indicator_id=indicator.indicator_id,
            context=compatibility_value(thaw_ordered_compatibility(
                candidates[indicator.indicator_id].definition.compatibility_context
            )),
            evidence=compatibility_value(
                _legacy_evidence(candidates[indicator.indicator_id])
            ),
            order=indicator.order,
        )
        for indicator in indicators
    )
    return CareerCompatibilityProjection(
        profile_id=inference_projection.profile_id,
        source_batch_digest=batch.logical_digest,
        base_score=inference_projection.base_score,
        total_contribution=inference_projection.total_contribution,
        formula=inference_projection.formula,
        public_trace_id=inference_projection.public_trace_id,
        precision=inference_projection.precision,
        components=component_projection,
        indicators=indicator_projection,
    )


def _evaluate_career_inference(
    batch: CareerEvaluationBatch,
) -> _CareerInferenceEvaluation:
    """Aggregate once and bind every Career authority value in the same run."""

    if not isinstance(batch, CareerEvaluationBatch):
        raise TypeError("batch must be CareerEvaluationBatch")
    config = _CAREER_INFERENCE_CONFIG
    rule_matches = career_inference_rule_matches(batch, config)
    engine = InferenceEngine()
    result = _aggregate_career(
        batch,
        config,
        engine,
        rule_matches=rule_matches,
    )
    contribution_lineage = tuple(
        (
            item.contribution_id,
            item.rule_id,
            item.rule_version,
            item.source_rule_trace_id,
        )
        for item in result.contributions
    )
    ledger = _CareerRuleMatchLedger(
        rule_matches=rule_matches,
        rule_match_digests=tuple(
            rule_match_logical_sha256(item) for item in rule_matches
        ),
        contribution_lineage=contribution_lineage,
    )
    for contribution in result.contributions:
        matching = next(
            (
                item
                for item in rule_matches
                if item.rule_id == contribution.rule_id
                and item.rule_version == contribution.rule_version
                and item.trace_id == contribution.source_rule_trace_id
            ),
            None,
        )
        if matching is None:
            raise ValueError("Career contribution is detached from the evaluator ledger")
        ledger.resolve(matching)
    compatibility_projection = engine._compatibility_projection(result, config)
    components = _career_domain_components(batch, result)
    indicators = _career_domain_indicators(batch, result, ledger)
    career_compatibility = _career_compatibility_projection(
        batch,
        compatibility_projection,
        components,
        indicators,
    )
    return _CareerInferenceEvaluation(
        batch=batch,
        config=config,
        config_fingerprint=inference_config_logical_sha256(config),
        ledger=ledger,
        inference_result=result,
        compatibility_projection=compatibility_projection,
        components=components,
        indicators=indicators,
        career_compatibility=career_compatibility,
    )


def _career_rejection(
    batch: CareerEvaluationBatch,
    result: InferenceResult,
    *,
    code: str,
    message: str,
) -> DomainBuildRejected:
    trace_id = f"career.reject.{batch.prepared_facts_sha256[:24]}"
    return DomainBuildRejected(
        domain=DomainId.CAREER,
        issues=(DomainIssue(
            issue_id=f"career.issue.{code.lower()}",
            code=code,
            severity=DomainIssueSeverity.FATAL,
            phase="domain_mapping",
            message=message,
            recoverable=False,
            source_trace_id=result.trace_id,
            details={},
        ),),
        trace_id=trace_id,
    )


def _build_career_prediction(
    evaluation: _CareerInferenceEvaluation,
) -> DomainBuildOutcome:
    """Consume only the private same-run Career authority value."""

    if not isinstance(evaluation, _CareerInferenceEvaluation):
        raise TypeError("evaluation must be _CareerInferenceEvaluation")
    batch = evaluation.batch
    result = evaluation.inference_result
    components = evaluation.components
    indicators = evaluation.indicators
    summary = (
        f"Career score {round(float(result.normalized_score),3)} "
        f"(confidence {round(float(result.confidence),3)})"
    )
    try:
        prediction = DomainPredictionFactory._from_career_evaluation(
            evaluation,
            domain=DomainId.CAREER,
            summary=summary,
            components=components,
            indicators=indicators,
            narrative_sections=(
                ()
                if result.status.value == "failed" or not result.contributions
                else _career_domain_narrative(result, indicators, summary)
            ),
            engine_version="0.1.0",
            interpreter_version=CAREER_EVALUATOR_VERSION,
            narrative_version=CAREER_EVALUATOR_VERSION,
        )
    except ValueError:
        return _career_rejection(
            batch,
            result,
            code="INVALID_STATUS_COMBINATION",
            message="The Career presentation could not reconcile to its inference result.",
        )
    return DomainBuildProduced(prediction=prediction)


def build_career_prediction(
    batch: CareerEvaluationBatch,
    result: InferenceResult | None,
) -> DomainBuildOutcome:
    """Closed legacy name: caller-owned values cannot mint Career authority."""

    if not isinstance(batch, CareerEvaluationBatch):
        raise TypeError("batch must be CareerEvaluationBatch")
    if result is None:
        return DomainPredictionFactory.missing_inference(domain=DomainId.CAREER)
    raise ValueError(
        "authoritative Career construction begins with AstroState or AstroStateSnapshot"
    )


def interpret_career_domain(astro: AstroState) -> DomainBuildOutcome:
    """Strict mutable-input wrapper returning the typed Career outcome."""

    prepared = prepare_career_facts(astro)
    batch = evaluate_career_batch(prepared)
    return _build_career_prediction(_evaluate_career_inference(batch))


def interpret_career_domain_snapshot(
    snapshot: AstroStateSnapshot,
) -> DomainBuildOutcome:
    """Canonical typed Career interpretation from one immutable snapshot."""

    prepared = prepare_career_snapshot(snapshot)
    batch = evaluate_career_batch(prepared)
    return _build_career_prediction(_evaluate_career_inference(batch))


def project_career_compatibility(
    batch: CareerEvaluationBatch,
    inference_result: InferenceResult | None = None,
) -> dict[str, Any]:
    """Named one-way wrapper from the typed domain result to public Career."""

    if not isinstance(batch, CareerEvaluationBatch):
        raise TypeError("batch must be CareerEvaluationBatch")
    result = infer_career(batch) if inference_result is None else inference_result
    if not isinstance(result, InferenceResult) or result.domain != "career":
        raise TypeError("inference_result must be a Career InferenceResult")
    compatibility = _CAREER_INFERENCE_CONFIG.career_compatibility
    baseline_rule_id = str(compatibility["baseline_rule_id"])
    baseline_category = str(compatibility["baseline_category"])
    baseline = next(
        (item for item in result.components if item.category == baseline_category),
        None,
    )
    base_score = (
        baseline.normalized_value
        if baseline is not None
        else float(_CAREER_INFERENCE_CONFIG.normalization["neutral_score"])
    )
    total = 0.0
    for item in result.contributions:
        if item.rule_id != baseline_rule_id:
            total += item.final_contribution
    precision = int(_CAREER_INFERENCE_CONFIG.normalization["precision"])
    components = _public_components(batch)
    candidates = {item.definition.candidate_id: item for item in batch.candidates}
    indicators = []
    evidence_rows = []
    for contribution in result.contributions:
        if contribution.rule_id == baseline_rule_id or contribution.final_contribution <= 0:
            continue
        candidate = candidates[contribution.rule_id]
        context = thaw_ordered_compatibility(
            candidate.definition.compatibility_context
        )
        evidence = _legacy_evidence(candidate)
        indicators.append({
            "rule_id": contribution.rule_id,
            "contribution": contribution.final_contribution,
            "evidence": evidence,
            "context": context,
        })
        evidence_rows.append({
            "rule_id": contribution.rule_id,
            "rule": context,
            "match": True,
            "evidence": evidence,
            "contribution": round(contribution.final_contribution, precision),
        })
        components.append({
            "type": "rule",
            "rule_id": contribution.rule_id,
            "weight": round(contribution.final_contribution, precision),
        })
    summary = (
        f"Career score {round(float(result.normalized_score),3)} "
        f"(confidence {round(float(result.confidence),3)})"
    )
    return {
        "summary": summary,
        "score": round(float(result.normalized_score), precision),
        "confidence": round(float(result.confidence), precision),
        "components": components,
        "indicators": indicators,
        "evidence": evidence_rows,
        "scoring": {
            "base_score": round(base_score, precision),
            "total_contribution": round(total, precision),
            "final_score": round(float(result.normalized_score), precision),
            "formula": str(compatibility["public_formula"]),
        },
        "trace_id": str(compatibility["public_trace_id"]),
    }


def interpret_career(astro: AstroState) -> dict[str, Any]:
    """Existing public wrapper over the Prompt-05 typed Career boundary."""

    outcome = interpret_career_domain(astro)
    if isinstance(outcome, DomainBuildRejected):
        raise ValueError("Career DomainPrediction construction was rejected")
    return project_career_prediction_compatibility(outcome.prediction)


def interpret_career_snapshot(snapshot: AstroStateSnapshot) -> dict[str, Any]:
    """Public compatibility wrapper over canonical typed Career evaluation."""

    outcome = interpret_career_domain_snapshot(snapshot)
    if isinstance(outcome, DomainBuildRejected):
        raise ValueError("Career DomainPrediction construction was rejected")
    return project_career_prediction_compatibility(outcome.prediction)


__all__ = (
    "evaluate_career_batch",
    "career_data_completeness",
    "career_inference_rule_matches",
    "interpret_career_domain",
    "interpret_career_domain_snapshot",
    "interpret_career",
    "interpret_career_snapshot",
    "prepare_career_snapshot",
    "prepare_career_facts",
    "project_career_compatibility",
)
