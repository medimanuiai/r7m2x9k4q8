"""Shared typed Yoga and Career evaluation for artifact/coverage tooling."""

from __future__ import annotations

from dataclasses import dataclass

from systems.Parasara.engine.astrostate import AstroState
from systems.Parasara.engine.enrichments.yoga_engine import (
    YogaEvaluationBatch,
    evaluate_yoga_batch,
    load_yoga_rule_source,
    prepare_legacy_yoga_state,
    yoga_batch_from_preparation_failure,
)
from systems.Parasara.engine.interpreters.career import (
    evaluate_career_batch,
    prepare_career_facts,
)
from systems.Parasara.engine.interpreters.career_models import CareerEvaluationBatch
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext
from systems.Parasara.engine.rules.prepared_state import PreparationIssue


@dataclass(frozen=True, slots=True)
class TypedRuleSurfaces:
    yoga: YogaEvaluationBatch
    career: CareerEvaluationBatch


def evaluate_typed_rule_surfaces(astro: AstroState) -> TypedRuleSurfaces:
    """Evaluate the two active rule-owning surfaces without mutable registries."""

    source = load_yoga_rule_source()
    try:
        preparation = prepare_legacy_yoga_state(astro, source)
    except Exception:
        preparation = None
    if preparation is None:
        yoga = yoga_batch_from_preparation_failure(
            source,
            (
                PreparationIssue(
                    code="typed_tool_yoga_preparation_failed",
                    path="$",
                    capability_id=None,
                ),
            ),
        )
    elif preparation.outcome.succeeded and preparation.outcome.state is not None:
        yoga = evaluate_yoga_batch(
            preparation.outcome.state,
            PredicateEvaluationContext(),
            source,
            predicate_evaluator=PredicateEvaluator(),
            compatibility_graph=preparation.compatibility_graph,
        )
    else:
        yoga = yoga_batch_from_preparation_failure(
            source, preparation.outcome.issues
        )
    career = evaluate_career_batch(prepare_career_facts(astro))
    return TypedRuleSurfaces(yoga=yoga, career=career)


__all__ = ("TypedRuleSurfaces", "evaluate_typed_rule_surfaces")
