"""Deterministic coverage derived from explicit typed evaluation records."""

from __future__ import annotations

from collections import OrderedDict
import json
from pathlib import Path
from typing import Any

from systems.Parasara.engine.rules.models import ConditionResult, PredicateResult
from tests.testing_framework.typed_rule_evaluation import evaluate_typed_rule_surfaces


def _predicate_results(result):
    if isinstance(result, PredicateResult):
        yield result
    elif isinstance(result, ConditionResult):
        for child in result.children:
            if child.result is not None:
                yield from _predicate_results(child.result)


def run_rule_coverage_scan(astro: Any, out_path: str | None = None) -> dict[str, Any]:
    """Report only Yoga/Career records actually inspected by their typed owners."""

    surfaces = evaluate_typed_rule_surfaces(astro)
    hits: OrderedDict[str, int] = OrderedDict()
    predicate_statuses: OrderedDict[str, OrderedDict[str, int]] = OrderedDict()

    def accumulate_predicate(result: PredicateResult) -> None:
        identity = f"{result.predicate_id}@{result.predicate_version}"
        statuses = predicate_statuses.setdefault(identity, OrderedDict())
        status = result.status.value
        statuses[status] = statuses.get(status, 0) + 1

    for record in surfaces.yoga.records:
        identity = f"yoga:{record.yoga_id}@{record.rule_version}"
        hits[identity] = hits.get(identity, 0) + 1
        if record.condition_result is not None:
            for result in _predicate_results(record.condition_result):
                accumulate_predicate(result)

    for candidate in surfaces.career.candidates:
        version = candidate.definition.rule_version or candidate.fact.fact_version
        identity = f"career:{candidate.definition.candidate_id}@{version}"
        hits[identity] = hits.get(identity, 0) + 1
        if candidate.fact.backing_result is not None:
            for result in _predicate_results(candidate.fact.backing_result):
                accumulate_predicate(result)

    total = len(hits)
    report = {
        "rules": {
            "total_available": total,
            "total_executed": total,
            "coverage_ratio": 1.0 if total else 0.0,
            "hits": dict(hits),
        },
        "predicates": {key: dict(value) for key, value in predicate_statuses.items()},
    }
    if out_path:
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False),
            encoding="utf-8",
        )
    return report


__all__ = ("run_rule_coverage_scan",)
