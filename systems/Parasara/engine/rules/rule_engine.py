"""Generic construction and deterministic ordering boundary for RuleMatch."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
import hashlib
from typing import Any
from uuid import UUID, uuid5

from systems.Parasara.engine.rules.canonical import FrozenMapping, canonical_json_bytes
from systems.Parasara.engine.rules.models import (
    ConditionNodeDisposition,
    ConditionResult,
    PredicateError,
    PredicateResult,
    PredicateStatus,
)
from systems.Parasara.engine.rules.rule_match import (
    RULE_MATCH_SCHEMA_VERSION,
    RuleMatch,
    RuleMatchError,
    RuleMatchStatus,
    RuleTraceReference,
)


DEFAULT_RULE_TRACE_NAMESPACE = UUID("a26e9af7-f03a-5bd1-aa3f-fbdf387778d8")


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolvedRule:
    """Complete immutable metadata required before rule evaluation can publish."""

    system: str
    rule_id: str
    rule_version: str
    rule_family: str
    rule_set_version: str
    category: str
    domains: tuple[str, ...]
    base_weight: float
    priority: int
    context: str
    quality: float | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    evaluation_plan_position: int = 0

    def __post_init__(self) -> None:
        if type(self.evaluation_plan_position) is not int or self.evaluation_plan_position < 0:
            raise ValueError("evaluation_plan_position must be a nonnegative integer")
        # Reuse RuleMatch's strict metadata validation without constructing a
        # partially evaluated result. The remaining identity constraints are
        # applied by the sole producer when evaluation completes.
        object.__setattr__(self, "domains", tuple(sorted(set(self.domains))))
        object.__setattr__(self, "provenance", FrozenMapping(self.provenance, path="$.provenance"))
        metadata = dict(self.metadata)
        metadata["evaluation_plan_position"] = self.evaluation_plan_position
        object.__setattr__(self, "metadata", FrozenMapping(metadata, path="$.metadata"))


def _status(status: PredicateStatus) -> RuleMatchStatus:
    return {
        PredicateStatus.MATCHED: RuleMatchStatus.MATCHED,
        PredicateStatus.UNMATCHED: RuleMatchStatus.UNMATCHED,
        PredicateStatus.SKIPPED: RuleMatchStatus.SKIPPED,
        PredicateStatus.MISSING_CAPABILITY: RuleMatchStatus.MISSING_CAPABILITY,
        PredicateStatus.INVALID_PARAMETERS: RuleMatchStatus.INVALID,
        PredicateStatus.ERROR: RuleMatchStatus.ERROR,
        PredicateStatus.TIMEOUT: RuleMatchStatus.ERROR,
    }[status]


def _predicate_results(result: PredicateResult | ConditionResult | None) -> tuple[PredicateResult, ...]:
    if result is None:
        return ()
    if isinstance(result, PredicateResult):
        return (result,)
    found: list[PredicateResult] = []
    for child in result.children:
        if child.disposition is ConditionNodeDisposition.EVALUATED:
            found.extend(_predicate_results(child.result))
    return tuple(found)


def _predicate_errors(result: PredicateResult | ConditionResult | None) -> tuple[PredicateError, ...]:
    if result is None:
        return ()
    found = list(result.errors)
    if isinstance(result, ConditionResult):
        for child in result.children:
            if child.disposition is ConditionNodeDisposition.EVALUATED:
                found.extend(_predicate_errors(child.result))
    unique: dict[tuple[Any, ...], PredicateError] = {}
    for error in found:
        key = (
            error.code,
            error.message,
            error.predicate_id,
            error.recoverable,
            canonical_json_bytes(error.details),
        )
        unique.setdefault(key, error)
    return tuple(unique.values())


def _rule_error(error: PredicateError) -> RuleMatchError:
    return RuleMatchError(
        code=error.code,
        message=error.message,
        phase="predicate_evaluation",
        recoverable=error.recoverable,
        details=error.details,
        source_predicate_id=error.predicate_id,
        source_trace_id=None,
    )


def _error_key(error: RuleMatchError) -> tuple[Any, ...]:
    return (
        error.phase, error.code, error.message, error.source_predicate_id or "",
        error.source_trace_id or "", canonical_json_bytes(error.details),
    )


class RuleEngine:
    """Owns construction of the universal rule-evaluation result."""

    def build_match(
        self,
        resolved_rule: ResolvedRule,
        result: PredicateResult | ConditionResult | None,
        *,
        evaluation_snapshot_digest: str,
        evaluation_context: Mapping[str, Any],
        status_override: RuleMatchStatus | None = None,
        evidence: Mapping[str, Any] | None = None,
        errors: Sequence[RuleMatchError] = (),
        additional_trace_references: Sequence[RuleTraceReference] = (),
        trace_namespace: UUID = DEFAULT_RULE_TRACE_NAMESPACE,
        trace_components: Sequence[str] = (),
    ) -> RuleMatch:
        if not isinstance(resolved_rule, ResolvedRule):
            raise TypeError("resolved_rule must be a ResolvedRule")
        if result is not None and not isinstance(result, (PredicateResult, ConditionResult)):
            raise TypeError("result must be a canonical result or None")
        if (
            not isinstance(evaluation_snapshot_digest, str)
            or len(evaluation_snapshot_digest) != 64
        ):
            raise ValueError("evaluation_snapshot_digest must be lowercase SHA-256")
        try:
            int(evaluation_snapshot_digest, 16)
        except ValueError as exc:
            raise ValueError("evaluation_snapshot_digest must be lowercase SHA-256") from exc
        if evaluation_snapshot_digest != evaluation_snapshot_digest.lower():
            raise ValueError("evaluation_snapshot_digest must be lowercase SHA-256")
        if not isinstance(evaluation_context, Mapping):
            raise TypeError("evaluation_context must be an immutable-safe mapping")
        context_digest = hashlib.sha256(canonical_json_bytes(evaluation_context)).hexdigest()
        if not isinstance(trace_namespace, UUID) or trace_namespace.version != 5:
            raise ValueError("trace_namespace must be a UUIDv5 namespace")
        if any(not isinstance(item, str) for item in trace_components):
            raise TypeError("trace_components must be strings")
        if result is None and status_override is None:
            raise ValueError("a missing canonical result requires an explicit status")

        status = status_override if status_override is not None else _status(result.status)
        predicate_results = _predicate_results(result)
        condition_trace_id = None
        references: list[RuleTraceReference] = []
        if isinstance(result, ConditionResult):
            condition_trace_id = result.node_id
            references.append(RuleTraceReference(
                trace_id=result.node_id,
                trace_type="condition",
                relation="evaluated_condition",
                order=0,
            ))
        elif isinstance(result, PredicateResult):
            condition_trace_id = (
                result.trace_steps[0].step_id if result.trace_steps else result.predicate_id
            )

        seen_trace_ids = {reference.trace_id for reference in references}
        for predicate in predicate_results:
            trace_id = (
                predicate.trace_steps[0].step_id
                if predicate.trace_steps
                else predicate.predicate_id
            )
            if trace_id not in seen_trace_ids:
                references.append(RuleTraceReference(
                    trace_id=trace_id,
                    trace_type="predicate",
                    relation="factual_leaf",
                    order=len(references),
                ))
                seen_trace_ids.add(trace_id)
        for reference in additional_trace_references:
            if not isinstance(reference, RuleTraceReference):
                raise TypeError("additional_trace_references must be RuleTraceReference values")
            if reference.trace_id not in seen_trace_ids:
                references.append(RuleTraceReference(
                    trace_id=reference.trace_id,
                    trace_type=reference.trace_type,
                    relation=reference.relation,
                    order=len(references),
                ))
                seen_trace_ids.add(reference.trace_id)

        all_errors = [*errors, *(_rule_error(item) for item in _predicate_errors(result))]
        unique_errors: dict[tuple[Any, ...], RuleMatchError] = {}
        for error in all_errors:
            if not isinstance(error, RuleMatchError):
                raise TypeError("errors must contain only RuleMatchError values")
            unique_errors.setdefault(_error_key(error), error)
        ordered_errors = tuple(unique_errors.values())

        logical_evidence = evidence
        if logical_evidence is None:
            logical_evidence = {
                "root_result_id": condition_trace_id,
                "predicate_trace_ids": tuple(reference.trace_id for reference in references if reference.trace_type == "predicate"),
            }
        seed_parts = tuple(trace_components) or (
            resolved_rule.system,
            resolved_rule.rule_id,
            resolved_rule.rule_version,
            str(resolved_rule.evaluation_plan_position),
            evaluation_snapshot_digest,
            context_digest,
            condition_trace_id or status.value,
        )
        seed = "|".join(seed_parts)
        trace_id = str(uuid5(trace_namespace, seed))
        return RuleMatch(
            rule_match_schema_version=RULE_MATCH_SCHEMA_VERSION,
            system=resolved_rule.system,
            rule_id=resolved_rule.rule_id,
            rule_version=resolved_rule.rule_version,
            rule_family=resolved_rule.rule_family,
            rule_set_version=resolved_rule.rule_set_version,
            category=resolved_rule.category,
            domains=resolved_rule.domains,
            status=status,
            matched=status is RuleMatchStatus.MATCHED,
            base_weight=resolved_rule.base_weight,
            priority=resolved_rule.priority,
            context=resolved_rule.context,
            quality=resolved_rule.quality,
            predicate_results=predicate_results,
            evidence=logical_evidence,
            provenance=resolved_rule.provenance,
            metadata=resolved_rule.metadata,
            trace_id=trace_id,
            condition_trace_id=condition_trace_id,
            trace_references=tuple(sorted(references, key=lambda item: (item.order, item.trace_type, item.trace_id, item.relation))),
            errors=ordered_errors,
        )

    @staticmethod
    def order_matches(values: Sequence[RuleMatch]) -> tuple[RuleMatch, ...]:
        if any(not isinstance(item, RuleMatch) for item in values):
            raise TypeError("values must contain only RuleMatch instances")
        return tuple(sorted(
            values,
            key=lambda item: (
                -item.priority,
                item.rule_id,
                item.rule_version,
                item.metadata.get("evaluation_plan_position", 0),
            ),
        ))


__all__ = ("ResolvedRule", "RuleEngine")
