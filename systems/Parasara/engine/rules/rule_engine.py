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

    __slots__ = ("_resolved_versions",)

    def __init__(self, *, resolved_versions: Any | None = None) -> None:
        if resolved_versions is not None:
            from systems.Parasara.engine.versioning import ResolvedEvaluationVersions

            if not isinstance(resolved_versions, ResolvedEvaluationVersions):
                raise TypeError("resolved_versions must be ResolvedEvaluationVersions or None")
        self._resolved_versions = resolved_versions

    @property
    def resolved_versions(self) -> Any | None:
        return self._resolved_versions

    def require_authority(self, resolved_versions: Any) -> None:
        if self._resolved_versions is None:
            raise ValueError("legacy unbound RuleEngine has no evaluation authority")
        self._resolved_versions.require_same(resolved_versions)

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
        """Build a legacy/current match; DSL manifests use evaluate_compiled_rule."""

        self._reject_graph_bypass()
        if (
            self._resolved_versions is not None
            and self._resolved_versions.manifest.dsl is not None
        ):
            from systems.Parasara.engine.versioning import (
                VersioningError,
                VersioningErrorCode,
            )

            raise VersioningError(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "DSL-bound rules must be evaluated through evaluate_compiled_rule.",
            )
        return self._build_match(
            resolved_rule,
            result,
            evaluation_snapshot_digest=evaluation_snapshot_digest,
            evaluation_context=evaluation_context,
            status_override=status_override,
            evidence=evidence,
            errors=errors,
            additional_trace_references=additional_trace_references,
            trace_namespace=trace_namespace,
            trace_components=trace_components,
        )

    def evaluate_compiled_rule(
        self,
        compiled_rule: Any,
        *,
        condition_evaluator: Any,
        state: Any,
        context: Any,
        evaluation_snapshot_digest: str,
        evaluation_context: Mapping[str, Any],
        trace_namespace: UUID = DEFAULT_RULE_TRACE_NAMESPACE,
        trace_components: Sequence[str] = (),
    ) -> RuleMatch:
        """Evaluate one exact sealed DSL artifact through existing evaluation owners."""

        self._reject_graph_bypass()
        result = self._evaluate_compiled_condition(compiled_rule, condition_evaluator, state, context)
        return self._compiled_match(compiled_rule, result,
            evaluation_snapshot_digest=evaluation_snapshot_digest, evaluation_context=evaluation_context,
            trace_namespace=trace_namespace, trace_components=trace_components)

    def _reject_graph_bypass(self):
        if self._resolved_versions is not None and self._resolved_versions.manifest.dependency_graph is not None:
            from systems.Parasara.engine.rules.graph.models import diagnostic
            from systems.Parasara.engine.versioning import _graph_error
            raise _graph_error(diagnostic("P08E307_DIRECT_EXECUTION_BYPASS"))

    def _evaluate_compiled_condition(self, compiled_rule, condition_evaluator, state, context):
        from systems.Parasara.engine.rules.conditions import ConditionEvaluator
        from systems.Parasara.engine.rules.dsl import CompiledRule

        if not isinstance(compiled_rule, CompiledRule):
            raise TypeError("compiled_rule must be a CompiledRule")
        if not isinstance(condition_evaluator, ConditionEvaluator):
            raise TypeError("condition_evaluator must be a ConditionEvaluator")
        if self._resolved_versions is None:
            raise ValueError("compiled rules require a resolved evaluation authority")
        self._resolved_versions.authorize_compiled_rule(compiled_rule)
        condition_evaluator.predicate_evaluator.require_authority(self._resolved_versions)
        return condition_evaluator.evaluate(
            compiled_rule.lowered_condition,
            state,
            context,
            root_node_id=f"dsl.rule.{compiled_rule.resolved_rule.evaluation_plan_position:06d}.condition",
        )
    def _compiled_match(self, compiled_rule, result, **kwargs):
        translated_errors: tuple[RuleMatchError, ...] = ()
        if result.status is PredicateStatus.TIMEOUT:
            translated_errors = (RuleMatchError(
                code="condition_timeout",
                message="The compiled condition evaluation timed out.",
                phase="predicate_evaluation",
                recoverable=True,
                details={"source_status": PredicateStatus.TIMEOUT.value},
                source_predicate_id=(
                    result.predicate_id if isinstance(result, PredicateResult) else None
                ),
                source_trace_id=None,
            ),)
        return self._build_match(
            compiled_rule.resolved_rule,
            result,
            errors=translated_errors,
            **kwargs,
        )

    def evaluate_plan(self, *, plan, condition_evaluator, snapshot, context):
        """Execute one issued plan atomically through the existing condition owner."""
        from systems.Parasara.engine.astrostate_api import AstroStateSnapshot
        from systems.Parasara.engine.rules.conditions import ConditionEvaluator
        from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext, context_canonical_projection
        from systems.Parasara.engine.rules.snapshot_adapter import prepare_predicate_snapshot
        from systems.Parasara.engine.rules.graph.models import (
            DependencyDecision, RuleExecutionTrace, GraphEvaluationProduced, GraphEvaluationFailed,
            diagnostic, versioning_diagnostic, _new_evaluation_record,
        )
        from systems.Parasara.engine.rules.graph.runtime_contract import GRAPH_CONTRACT_DATA, KINDS, LIMITS, digest, dependency_trace_id
        from systems.Parasara.engine.versioning import VersioningError, _graph_error

        def fail(code="P08E308_RUNTIME_INVARIANT", **details):
            raise _graph_error(diagnostic(code, stage="execution", details=details))

        authority = self._resolved_versions
        try:
            if authority is None:
                fail("P08E302_AUTHORITY_MISMATCH")
            authority.authorize_execution_plan(plan)
            if not isinstance(condition_evaluator, ConditionEvaluator):
                fail()
            condition_evaluator.predicate_evaluator.require_authority(authority)
            if not isinstance(snapshot, AstroStateSnapshot) or not isinstance(context, PredicateEvaluationContext):
                fail()
            instant = context.evaluation_instant
            if (instant is None or instant.microsecond or
                instant.strftime("%Y-%m-%dT%H:%M:%SZ") != authority.config.evaluation_instant):
                fail("P08E302_AUTHORITY_MISMATCH")
            authority.authorize_snapshot(snapshot)
            prepared = prepare_predicate_snapshot(snapshot)
            if not prepared.succeeded or prepared.state is None:
                fail(preparation_issues=tuple(sorted({issue.code for issue in prepared.issues}))[:LIMITS["diagnostics"] - 1])
            projection = context_canonical_projection(context)
            snapshot_sha, context_sha = snapshot.logical_digest, digest(projection)
            analysis = plan.graph.analysis
            count = len(analysis.nodes)
            plan_sha = plan.plan_sha256
            matches, traces = [None] * count, [None] * count
            incoming = [[] for _ in range(count)]
            for edge in analysis.edges:
                incoming[edge.dependent].append(edge)
            policy = GRAPH_CONTRACT_DATA["outcome_policy"]
            for ordinal, i in enumerate(plan.execution_order):
                if type(i) is not int or not 0 <= i < count or matches[i] is not None:
                    fail()
                decisions = []
                for edge in incoming[i]:
                    prior, prior_trace = matches[edge.prerequisite], traces[edge.prerequisite]
                    if prior is None or prior_trace is None or prior.status is RuleMatchStatus.EXCLUDED:
                        fail()
                    outcome = prior_trace.root_outcome if prior_trace.condition_evaluated else "dependency_skip"
                    row = policy[outcome]
                    if prior.status.value != row[0]:
                        fail()
                    decisions.append(DependencyDecision(prerequisite=edge.prerequisite, dependent=i,
                        kind=edge.kind, prerequisite_trace_id=prior.trace_id,
                        completion_kind=prior_trace.completion_kind, root_outcome=prior_trace.root_outcome,
                        rule_match_status=prior.status.value, decision=row[KINDS.index(edge.kind) + 1]))
                required = {d.decision for d in decisions if d.kind != "optional_supports"}
                gate = next((g for g in policy["gate_precedence"] if g in required), "passed")
                trace_id = dependency_trace_id(plan_sha, i, snapshot_sha, context_sha)
                reference = RuleTraceReference(trace_id=trace_id, trace_type="dependency", relation="dependency_gate", order=0)
                kwargs = dict(evaluation_snapshot_digest=snapshot_sha, evaluation_context=projection,
                    additional_trace_references=(reference,))
                compiled = plan.compiled_rule_set.rules[i]
                if gate == "passed":
                    result = self._evaluate_compiled_condition(compiled, condition_evaluator, prepared.state, context)
                    if not isinstance(result, (PredicateResult, ConditionResult)) or not isinstance(result.status, PredicateStatus):
                        fail()
                    match = self._compiled_match(compiled, result, **kwargs)
                    completion, root, skip = "condition_evaluated", result.status.value, None
                    expected_status = policy[root][0]
                else:
                    match = self._build_match(compiled.resolved_rule, None,
                        status_override=RuleMatchStatus.SKIPPED, evidence={}, **kwargs)
                    completion, root, skip = "dependency_skip", None, "dependency_" + gate
                    expected_status = "skipped"
                if (not isinstance(match, RuleMatch) or match.status.value != expected_status or
                    (match.rule_id, match.rule_version) != (analysis.nodes[i].rule_id, analysis.nodes[i].revision)):
                    fail()
                matches[i] = match
                traces[i] = RuleExecutionTrace(trace_id=trace_id, plan_sha256=plan_sha,
                    source_order=i, execution_ordinal=ordinal, decisions=tuple(decisions), gate=gate,
                    condition_evaluated=gate == "passed", completion_kind=completion, root_outcome=root, skip_reason=skip)
            if any(m is None for m in matches) or any(t is None for t in traces):
                fail()
            authority.authorize_execution_plan(plan)
            return GraphEvaluationProduced(_new_evaluation_record(resolved_versions=authority, plan=plan,
                snapshot_sha256=snapshot_sha, context_sha256=context_sha, matches=tuple(matches), traces=tuple(traces)))
        except VersioningError as exc:
            return GraphEvaluationFailed((versioning_diagnostic(exc, stage="execution"),))

    def _build_match(
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
        if self._resolved_versions is not None:
            self._resolved_versions.authorize_rule(resolved_rule)
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
