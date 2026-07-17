from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, field, replace
from enum import Enum
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Dict, Any, List
from uuid import UUID, uuid5

import yaml

from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.enrichments import aspects as aspects_mod
from systems.Parasara.engine.enrichments import functional_roles as functional_roles_mod
from systems.Parasara.engine.rules.canonical import (
    CanonicalValueError,
    FrozenMapping,
    canonical_json_bytes,
    condition_result_from_full_data,
    condition_result_from_logical_data,
    condition_result_logical_sha256,
    condition_result_to_full_data,
    condition_result_to_logical_data,
    freeze_canonical,
    predicate_result_from_full_data,
    predicate_result_from_logical_data,
    predicate_result_logical_sha256,
    predicate_result_to_full_data,
    predicate_result_to_logical_data,
)
from systems.Parasara.engine.rules.conditions import ConditionEvaluator
from systems.Parasara.engine.rules.definition_validation import (
    DefinitionIssue,
    DefinitionIssueSeverity,
    RuleSourceIdentity,
    YogaRuleSetValidationOutcome,
    definition_issue_projection,
    definition_issues_sha256,
    validate_yoga_rule_file,
    validate_yoga_rules,
)
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.models import (
    ConditionNodeDisposition,
    ConditionResult,
    PredicateError,
    PredicateResult,
    PredicateStatus,
    PredicateTraceStep,
)
from systems.Parasara.engine.rules.prepared_state import (
    CapabilitySupply,
    PredicateEvaluationContext,
    PreparationIssue,
    PreparationOutcome,
    PreparedAstroState,
    prepare_predicate_state,
    prepared_state_sha256,
)


YOGA_SCHEMA_VERSION = "1.0.0"
YOGA_EVALUATOR_VERSION = "1.0.0"
YOGA_TRACE_NAMESPACE = UUID("a3dbd23e-0618-5d43-94ac-a79008ebf140")
DEFAULT_YOGA_RULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "rules" / "parashara" / "v1" / "yogas.yaml"
)
DEFAULT_YOGA_SOURCE_NAME = "rules/parashara/v1/yogas.yaml"

_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_RULE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


def _planet_by_name(astro: AstroState, name: str) -> PlanetState:
    return next((p for p in getattr(astro, 'planets', []) if p.name == name), None)


class YogaDefinitionDisposition(str, Enum):
    VALID = "valid"
    INVALID = "invalid"


@dataclass(frozen=True, slots=True, kw_only=True)
class YogaRuleSource:
    """One explicitly loaded immutable Yoga source plus its WP12 outcome."""

    source_name: str
    records: tuple[Any, ...]
    validation: YogaRuleSetValidationOutcome

    def __post_init__(self) -> None:
        if not isinstance(self.source_name, str) or not self.source_name:
            raise ValueError("source_name must be nonempty")
        if not isinstance(self.records, tuple):
            raise TypeError("records must be an immutable tuple")
        if not isinstance(self.validation, YogaRuleSetValidationOutcome):
            raise TypeError("validation must be a WP12 Yoga outcome")
        object.__setattr__(self, "records", freeze_canonical(self.records, path="$.records"))


@dataclass(frozen=True, slots=True, kw_only=True)
class YogaLegacyPreparation:
    """Detached compatibility preparation; producer diagnostics are projection-only."""

    outcome: PreparationOutcome
    compatibility_graph: FrozenMapping | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, PreparationOutcome):
            raise TypeError("outcome must be PreparationOutcome")
        if self.compatibility_graph is not None and not isinstance(
            self.compatibility_graph, FrozenMapping
        ):
            object.__setattr__(
                self,
                "compatibility_graph",
                FrozenMapping(self.compatibility_graph, path="$.compatibility_graph"),
            )


@dataclass(frozen=True, slots=True, kw_only=True, eq=False)
class YogaEvaluationRecord:
    yoga_id: str
    name: str
    rule_version: Any
    source: RuleSourceIdentity
    definition_disposition: YogaDefinitionDisposition
    definition_issues: tuple[DefinitionIssue, ...]
    condition_result: PredicateResult | ConditionResult | None
    matched: bool
    status: PredicateStatus
    trace_reference: str
    compatibility_evidence: FrozenMapping = field(default_factory=FrozenMapping)
    compatibility_houses: tuple[Any, ...] = ()
    evaluation_time_ms: float | None = None

    __hash__ = None

    def __post_init__(self) -> None:
        if not isinstance(self.yoga_id, str) or not _RULE_ID.fullmatch(self.yoga_id):
            raise ValueError("yoga_id must be a stable canonical rule identity")
        if not isinstance(self.name, str):
            raise TypeError("name must be a string")
        object.__setattr__(
            self,
            "rule_version",
            freeze_canonical(self.rule_version, path="$.rule_version"),
        )
        if not isinstance(self.source, RuleSourceIdentity) or self.source.rule_index is None:
            raise ValueError("source must carry a stable rule index")
        if not isinstance(self.definition_disposition, YogaDefinitionDisposition):
            raise TypeError("definition_disposition must be YogaDefinitionDisposition")
        if not isinstance(self.definition_issues, tuple) or any(
            not isinstance(item, DefinitionIssue) for item in self.definition_issues
        ):
            raise TypeError("definition_issues must be an immutable DefinitionIssue tuple")
        if self.condition_result is not None and not isinstance(
            self.condition_result, (PredicateResult, ConditionResult)
        ):
            raise TypeError("condition_result must be canonical or None")
        if type(self.matched) is not bool or not isinstance(self.status, PredicateStatus):
            raise TypeError("matched/status have invalid types")
        if self.matched is not (self.status is PredicateStatus.MATCHED):
            raise ValueError("matched is true exactly when status is matched")
        if self.condition_result is not None and (
            self.condition_result.matched is not self.matched
            or self.condition_result.status is not self.status
        ):
            raise ValueError("Yoga status must agree with its canonical condition result")
        if self.definition_disposition is YogaDefinitionDisposition.VALID:
            if self.definition_issues or self.condition_result is None:
                raise ValueError("valid definitions require one result and no issues")
        elif not self.definition_issues:
            raise ValueError("invalid definitions require one or more WP12 issues")
        try:
            parsed_trace = UUID(self.trace_reference)
        except (AttributeError, TypeError, ValueError) as exc:
            raise ValueError("trace_reference must be a UUID string") from exc
        if parsed_trace.version != 5:
            raise ValueError("trace_reference must use deterministic UUIDv5")
        if not isinstance(self.compatibility_evidence, FrozenMapping):
            object.__setattr__(
                self,
                "compatibility_evidence",
                FrozenMapping(self.compatibility_evidence, path="$.compatibility_evidence"),
            )
        if not isinstance(self.compatibility_houses, tuple):
            object.__setattr__(self, "compatibility_houses", tuple(self.compatibility_houses))
        object.__setattr__(
            self,
            "compatibility_houses",
            freeze_canonical(self.compatibility_houses, path="$.compatibility_houses"),
        )
        if self.evaluation_time_ms is not None and (
            isinstance(self.evaluation_time_ms, bool)
            or not isinstance(self.evaluation_time_ms, (int, float))
            or not math.isfinite(self.evaluation_time_ms)
            or self.evaluation_time_ms < 0
        ):
            raise ValueError("evaluation_time_ms must be finite and nonnegative")

    def _logical_values(self) -> tuple[Any, ...]:
        return (
            self.yoga_id,
            self.name,
            self.rule_version,
            self.source,
            self.definition_disposition,
            self.definition_issues,
            self.condition_result,
            self.matched,
            self.status,
            self.trace_reference,
            self.compatibility_evidence,
            self.compatibility_houses,
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, YogaEvaluationRecord):
            return NotImplemented
        return self._logical_values() == other._logical_values()

    @property
    def source_index(self) -> int:
        assert self.source.rule_index is not None
        return self.source.rule_index


@dataclass(frozen=True, slots=True, kw_only=True, eq=False)
class YogaEvaluationBatch:
    schema_version: str
    evaluator_version: str
    prepared_state_digest: str
    records: tuple[YogaEvaluationRecord, ...]
    batch_issues: tuple[DefinitionIssue | PreparationIssue, ...] = ()
    total_duration_ms: float | None = None

    __hash__ = None

    def __post_init__(self) -> None:
        if not _SEMVER.fullmatch(self.schema_version) or not _SEMVER.fullmatch(
            self.evaluator_version
        ):
            raise ValueError("Yoga schema/evaluator versions must be SemVer")
        if not _SHA256.fullmatch(self.prepared_state_digest):
            raise ValueError("prepared_state_digest must be lowercase SHA-256")
        if not isinstance(self.records, tuple) or any(
            not isinstance(item, YogaEvaluationRecord) for item in self.records
        ):
            raise TypeError("records must be an immutable YogaEvaluationRecord tuple")
        if any(item.source_index != index for index, item in enumerate(self.records)):
            raise ValueError("records must preserve zero-based source order")
        if not isinstance(self.batch_issues, tuple) or any(
            not isinstance(item, (DefinitionIssue, PreparationIssue))
            for item in self.batch_issues
        ):
            raise TypeError("batch_issues must contain typed safe issues")
        if self.total_duration_ms is not None and (
            isinstance(self.total_duration_ms, bool)
            or not isinstance(self.total_duration_ms, (int, float))
            or not math.isfinite(self.total_duration_ms)
            or self.total_duration_ms < 0
        ):
            raise ValueError("total_duration_ms must be finite and nonnegative")

    def _logical_values(self) -> tuple[Any, ...]:
        return (
            self.schema_version,
            self.evaluator_version,
            self.prepared_state_digest,
            self.records,
            self.batch_issues,
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, YogaEvaluationBatch):
            return NotImplemented
        return self._logical_values() == other._logical_values()


def load_yoga_rule_source(
    path: str | Path = DEFAULT_YOGA_RULE_PATH,
    *,
    source_name: str = DEFAULT_YOGA_SOURCE_NAME,
) -> YogaRuleSource:
    """Load one explicit file and validate its records through WP12 without registration."""

    supplied = Path(path)
    file_outcome = validate_yoga_rule_file(supplied, source_name=source_name)
    if not supplied.is_absolute() or not supplied.is_file():
        return YogaRuleSource(source_name=source_name, records=(), validation=file_outcome)
    try:
        parsed = yaml.safe_load(supplied.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return YogaRuleSource(source_name=source_name, records=(), validation=file_outcome)
    if type(parsed) is not list:
        return YogaRuleSource(source_name=source_name, records=(), validation=file_outcome)
    try:
        records = freeze_canonical(parsed, path="$.records")
    except CanonicalValueError:
        return YogaRuleSource(source_name=source_name, records=(), validation=file_outcome)
    return YogaRuleSource(
        source_name=source_name,
        records=records,
        validation=validate_yoga_rules(parsed, source_name=source_name),
    )


def _condition_types(node: Any) -> tuple[str, ...]:
    found: list[str] = []

    def visit(value: Any) -> None:
        if not isinstance(value, Mapping):
            return
        raw_type = value.get("type")
        if isinstance(raw_type, str):
            found.append(raw_type.strip().upper())
        children = value.get("children")
        if isinstance(children, (list, tuple)):
            for child in children:
                visit(child)

    visit(node)
    return tuple(found)


def _preparation_failure(code: str, capability_id: str | None = None) -> YogaLegacyPreparation:
    issue = PreparationIssue(code=code, path="$", capability_id=capability_id)
    return YogaLegacyPreparation(
        outcome=PreparationOutcome(succeeded=False, state=None, issues=(issue,))
    )


def prepare_legacy_yoga_state(
    astro: AstroState,
    source: YogaRuleSource,
) -> YogaLegacyPreparation:
    """Prepare current Yoga facts once on an isolated copy; never mutate the caller."""

    if not isinstance(source, YogaRuleSource):
        return _preparation_failure("invalid_yoga_source")
    try:
        isolated = deepcopy(astro)
    except Exception:
        return _preparation_failure("yoga_defensive_copy_failed")
    predicate_types = tuple(
        item
        for record in source.records
        if isinstance(record, Mapping)
        for item in _condition_types(record.get("conditions"))
    )
    graph = None
    if any(item in ("ASPECT", "ASPECT_EXISTS") for item in predicate_types):
        try:
            config_path = Path(__file__).resolve().parents[4] / "rules" / "parashara" / "aspects.yaml"
            graph = aspects_mod.compute_aspect_graph(isolated, config_path=config_path)
        except Exception:
            return _preparation_failure("yoga_aspect_preparation_failed", "aspects.whole_sign_graph")

    supplies: tuple[CapabilitySupply, ...] = ()
    if "FUNCTIONAL_ROLE" in predicate_types:
        try:
            roles = functional_roles_mod.compute_functional_roles(isolated)
            derived = getattr(isolated, "derived", None)
            if isinstance(derived, Mapping):
                clean_derived = dict(derived)
                clean_derived.pop("functional_roles", None)
                isolated.derived = clean_derived
            supplies = (
                CapabilitySupply(
                    capability_id="roles.functional",
                    capability_version="1.0.0",
                    source_kind="legacy_yoga_adapter",
                    content=roles,
                ),
            )
        except Exception:
            return _preparation_failure("yoga_role_preparation_failed", "roles.functional")
    outcome = prepare_predicate_state(isolated, capability_supplies=supplies)
    try:
        frozen_graph = None if graph is None else FrozenMapping(graph, path="$.compatibility_graph")
    except CanonicalValueError:
        return _preparation_failure("yoga_compatibility_graph_unsafe", "aspects.whole_sign_graph")
    return YogaLegacyPreparation(outcome=outcome, compatibility_graph=frozen_graph)


def _result_logical_hash(result: PredicateResult | ConditionResult) -> str:
    if isinstance(result, ConditionResult):
        return condition_result_logical_sha256(result)
    return predicate_result_logical_sha256(result)


def _without_duration(
    result: PredicateResult | ConditionResult,
) -> PredicateResult | ConditionResult:
    """Drop optional wall-time telemetry while retaining cache telemetry and logic."""

    if isinstance(result, PredicateResult):
        return replace(result, evaluation_time_ms=None)
    children = tuple(
        replace(
            child,
            result=None if child.result is None else _without_duration(child.result),
        )
        for child in result.children
    )
    return replace(result, children=children, evaluation_time_ms=None)


def _trace_reference(
    *, yoga_id: str, rule_version: Any, source_index: int,
    state_digest: str, result_hash: str,
) -> str:
    name = "|".join(
        (
            YOGA_EVALUATOR_VERSION,
            yoga_id,
            str(rule_version),
            str(source_index),
            state_digest,
            result_hash,
        )
    )
    return str(uuid5(YOGA_TRACE_NAMESPACE, name))


def _legacy_leaf_evidence(
    node: Mapping[str, Any],
    result: PredicateResult,
    compatibility_graph: Mapping[str, Any] | None,
) -> dict[str, Any]:
    raw_type = str(node.get("type", "")).strip().upper()
    if result.status is not PredicateStatus.MATCHED:
        if raw_type == "HOUSE_LORDS_COMBINATION":
            return {"predicate": raw_type, "reason": "unknown_predicate"}
        return {}
    if raw_type in ("ASPECT", "ASPECT_EXISTS"):
        indexes = result.evidence.get("matched_indexes", ())
        if compatibility_graph is not None and isinstance(
            compatibility_graph.get("edges"), (list, tuple)
        ):
            edges = compatibility_graph["edges"]
            return {"matched_edges": [edges[index] for index in indexes]}
        return {"matched_edges": list(result.evidence.get("matched_edges", ())) }
    if raw_type == "FUNCTIONAL_ROLE":
        return {"matched_planets": list(result.evidence.get("matched_planets", ())) }
    if raw_type == "HOUSE_OCCUPANT":
        return {
            "planet": result.inputs.get("planet"),
            "house": result.inputs.get("house"),
        }
    return {}


def _legacy_evidence(
    node: Any,
    result: PredicateResult | ConditionResult,
    *,
    state: PreparedAstroState,
    context: PredicateEvaluationContext,
    evaluator: ConditionEvaluator,
    compatibility_graph: Mapping[str, Any] | None,
    node_id: str = "condition.root",
) -> dict[str, Any]:
    if not isinstance(node, Mapping):
        return {}
    raw_type = str(node.get("type", "")).strip().upper()
    children = node.get("children")
    if raw_type in ("AND", "OR", "NOT") and isinstance(children, (list, tuple)):
        by_index = {}
        if isinstance(result, ConditionResult):
            by_index = {child.child_index: child for child in result.children}
        evidence_children = []
        for index, child_node in enumerate(children):
            child = by_index.get(index)
            child_result = None if child is None else child.result
            if child_result is None:
                child_result = evaluator.evaluate(
                    child_node,
                    state,
                    context,
                    root_node_id=f"{node_id}.children.{index}.compatibility",
                )
            evidence_children.append(
                _legacy_evidence(
                    child_node,
                    child_result,
                    state=state,
                    context=context,
                    evaluator=evaluator,
                    compatibility_graph=compatibility_graph,
                    node_id=f"{node_id}.children.{index}",
                )
            )
        return {"children": evidence_children}
    if isinstance(result, PredicateResult):
        return _legacy_leaf_evidence(node, result, compatibility_graph)
    return {}


def _safe_record_identity(record: Any, index: int) -> tuple[str, str, Any]:
    if isinstance(record, Mapping):
        raw_id = record.get("id")
        yoga_id = raw_id if isinstance(raw_id, str) and _RULE_ID.fullmatch(raw_id) else f"invalid_yoga_rule_{index}"
        name = record.get("name") if isinstance(record.get("name"), str) else f"Invalid Yoga Rule {index}"
        version = record.get("version")
        try:
            version = freeze_canonical(version, path="$.rule_version")
        except CanonicalValueError:
            version = None
        return yoga_id, name, version
    return f"invalid_yoga_rule_{index}", f"Invalid Yoga Rule {index}", None


def _issues_by_index(source: YogaRuleSource) -> dict[int, tuple[DefinitionIssue, ...]]:
    grouped: dict[int, list[DefinitionIssue]] = {}
    for issue in source.validation.issues:
        if issue.source.rule_index is not None:
            grouped.setdefault(issue.source.rule_index, []).append(issue)
    return {key: tuple(value) for key, value in grouped.items()}


def evaluate_yoga_batch(
    state: PreparedAstroState,
    context: PredicateEvaluationContext,
    source: YogaRuleSource,
    *,
    predicate_evaluator: PredicateEvaluator | None = None,
    compatibility_graph: Mapping[str, Any] | None = None,
) -> YogaEvaluationBatch:
    """Evaluate every source row through one WP09/WP10 instance pair."""

    if not isinstance(state, PreparedAstroState):
        raise TypeError("state must be PreparedAstroState")
    if not isinstance(context, PredicateEvaluationContext):
        raise TypeError("context must be PredicateEvaluationContext")
    if not isinstance(source, YogaRuleSource):
        raise TypeError("source must be YogaRuleSource")
    if predicate_evaluator is None:
        predicate_evaluator = PredicateEvaluator()
    elif not isinstance(predicate_evaluator, PredicateEvaluator):
        raise TypeError("predicate_evaluator must be PredicateEvaluator")
    condition_evaluator = ConditionEvaluator(predicate_evaluator)
    digest = prepared_state_sha256(state)
    valid_by_index = {item.source.rule_index: item for item in source.validation.rules}
    issues_by_index = _issues_by_index(source)
    records: list[YogaEvaluationRecord] = []

    for index, raw_record in enumerate(source.records):
        yoga_id, name, version = _safe_record_identity(raw_record, index)
        issues = issues_by_index.get(index, ())
        valid_rule = valid_by_index.get(index)
        disposition = (
            YogaDefinitionDisposition.VALID
            if valid_rule is not None and not issues
            else YogaDefinitionDisposition.INVALID
        )
        condition = None
        if valid_rule is not None:
            condition = valid_rule.condition.normalized_condition
        elif isinstance(raw_record, Mapping) and isinstance(raw_record.get("conditions"), Mapping):
            condition = raw_record["conditions"]
        result = None
        if condition is not None:
            result = _without_duration(
                condition_evaluator.evaluate(condition, state, context)
            )
        status = PredicateStatus.ERROR if result is None else result.status
        matched = status is PredicateStatus.MATCHED
        if result is None:
            result_hash = definition_issues_sha256(issues)
            compatibility_evidence = FrozenMapping()
        else:
            result_hash = _result_logical_hash(result)
            compatibility_evidence = FrozenMapping(
                _legacy_evidence(
                    condition,
                    result,
                    state=state,
                    context=context,
                    evaluator=condition_evaluator,
                    compatibility_graph=compatibility_graph,
                )
            )
        houses: tuple[Any, ...] = ()
        if isinstance(condition, Mapping) and isinstance(condition.get("params"), Mapping):
            raw_houses = condition["params"].get("houses")
            if isinstance(raw_houses, (list, tuple)):
                houses = tuple(raw_houses)
        records.append(
            YogaEvaluationRecord(
                yoga_id=yoga_id,
                name=name,
                rule_version=version,
                source=RuleSourceIdentity(
                    source_name=source.source_name,
                    rule_id=yoga_id if not yoga_id.startswith("invalid_yoga_rule_") else None,
                    rule_index=index,
                ),
                definition_disposition=disposition,
                definition_issues=issues,
                condition_result=result,
                matched=matched,
                status=status,
                trace_reference=_trace_reference(
                    yoga_id=yoga_id,
                    rule_version=version,
                    source_index=index,
                    state_digest=digest,
                    result_hash=result_hash,
                ),
                compatibility_evidence=compatibility_evidence,
                compatibility_houses=houses,
                evaluation_time_ms=None,
            )
        )
    batch_issues = tuple(
        issue for issue in source.validation.issues if issue.source.rule_index is None
    )
    return YogaEvaluationBatch(
        schema_version=YOGA_SCHEMA_VERSION,
        evaluator_version=YOGA_EVALUATOR_VERSION,
        prepared_state_digest=digest,
        records=tuple(records),
        batch_issues=batch_issues,
        total_duration_ms=None,
    )


def _preparation_error_result(issue: PreparationIssue) -> PredicateResult:
    error = PredicateError(
        code=issue.code,
        message="Yoga compatibility preparation failed safely.",
        predicate_id="YOGA_PREPARATION",
        details={
            "path": issue.path,
            "capability_id": issue.capability_id,
        },
        recoverable=False,
    )
    trace = PredicateTraceStep(
        step_id="yoga_preparation.result",
        operation="yoga_preparation",
        details={"capability_id": issue.capability_id},
        observation={"completed": False},
        error_code=issue.code,
    )
    return PredicateResult(
        matched=False,
        predicate_id="YOGA_PREPARATION",
        predicate_version=YOGA_EVALUATOR_VERSION,
        inputs={},
        evidence={},
        trace_steps=(trace,),
        errors=(error,),
        cache_hit=False,
        evaluation_time_ms=None,
        status=PredicateStatus.ERROR,
    )


def _failure_compatibility_evidence(node: Any) -> FrozenMapping:
    if not isinstance(node, Mapping):
        return FrozenMapping()
    raw_type = str(node.get("type", "")).strip().upper()
    if raw_type == "HOUSE_LORDS_COMBINATION":
        return FrozenMapping({"predicate": raw_type, "reason": "unknown_predicate"})
    children = node.get("children")
    if raw_type in ("AND", "OR", "NOT") and isinstance(children, (list, tuple)):
        return FrozenMapping(
            {"children": tuple(_failure_compatibility_evidence(child) for child in children)}
        )
    return FrozenMapping()


def yoga_batch_from_preparation_failure(
    source: YogaRuleSource,
    issues: tuple[PreparationIssue, ...],
) -> YogaEvaluationBatch:
    """Preserve all source rows when legacy preparation cannot produce a state."""

    if not isinstance(source, YogaRuleSource) or not issues or any(
        not isinstance(item, PreparationIssue) for item in issues
    ):
        raise TypeError("a Yoga source and nonempty PreparationIssue tuple are required")
    digest = hashlib.sha256(
        canonical_json_bytes(tuple(_issue_to_data(item) for item in issues))
    ).hexdigest()
    issues_by_index = _issues_by_index(source)
    valid_indexes = {item.source.rule_index for item in source.validation.rules}
    result = _preparation_error_result(issues[0])
    result_hash = predicate_result_logical_sha256(result)
    records = []
    for index, raw_record in enumerate(source.records):
        yoga_id, name, version = _safe_record_identity(raw_record, index)
        definition_issues = issues_by_index.get(index, ())
        condition = raw_record.get("conditions") if isinstance(raw_record, Mapping) else None
        records.append(
            YogaEvaluationRecord(
                yoga_id=yoga_id,
                name=name,
                rule_version=version,
                source=RuleSourceIdentity(
                    source_name=source.source_name,
                    rule_id=yoga_id if not yoga_id.startswith("invalid_yoga_rule_") else None,
                    rule_index=index,
                ),
                definition_disposition=(
                    YogaDefinitionDisposition.VALID
                    if index in valid_indexes and not definition_issues
                    else YogaDefinitionDisposition.INVALID
                ),
                definition_issues=definition_issues,
                condition_result=result,
                matched=False,
                status=PredicateStatus.ERROR,
                trace_reference=_trace_reference(
                    yoga_id=yoga_id,
                    rule_version=version,
                    source_index=index,
                    state_digest=digest,
                    result_hash=result_hash,
                ),
                compatibility_evidence=_failure_compatibility_evidence(condition),
                compatibility_houses=(),
                evaluation_time_ms=None,
            )
        )
    return YogaEvaluationBatch(
        schema_version=YOGA_SCHEMA_VERSION,
        evaluator_version=YOGA_EVALUATOR_VERSION,
        prepared_state_digest=digest,
        records=tuple(records),
        batch_issues=issues,
        total_duration_ms=None,
    )


def _compatibility_key_order(value: Mapping[str, Any]) -> tuple[str, ...]:
    keys = tuple(value)
    key_set = set(keys)
    if {"source_planet", "source_sign", "source_degree", "offset", "target_sign", "matched_planets", "explanation"} <= key_set:
        preferred = (
            "source_planet", "source_sign", "source_degree", "offset",
            "target_sign", "matched_planets", "explanation",
        )
    elif {"source", "target", "aspect", "kind", "trace"} <= key_set:
        preferred = ("source", "target", "aspect", "kind", "trace")
    elif {"reason", "predicate"} <= key_set:
        preferred = ("reason", "predicate")
    elif {"planet", "house"} <= key_set:
        preferred = ("planet", "house")
    else:
        preferred = (
            "children", "matched_edges", "matched_planets", "reason", "predicate"
        )
    return tuple(key for key in preferred if key in value) + tuple(
        key for key in keys if key not in preferred
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(value[key]) for key in _compatibility_key_order(value)}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _first_seen(values: Sequence[Any]) -> list[Any]:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def project_yoga_compatibility(batch: YogaEvaluationBatch) -> list[dict[str, Any]]:
    """Project typed Yoga records one way into the locked eight-key dictionaries."""

    if not isinstance(batch, YogaEvaluationBatch):
        raise TypeError("batch must be YogaEvaluationBatch")
    output: list[dict[str, Any]] = []
    for record in batch.records:
        evidence = _thaw(record.compatibility_evidence)
        planets: list[Any] = []
        if isinstance(evidence.get("matched_planets"), list):
            planets.extend(evidence["matched_planets"])
        if not planets and isinstance(evidence.get("children"), list):
            for child in evidence["children"]:
                if isinstance(child, dict) and isinstance(child.get("matched_planets"), list):
                    planets.extend(child["matched_planets"])
        aspects_used = evidence.get("matched_edges", [])
        output.append(
            {
                "yoga_id": record.yoga_id,
                "name": record.name,
                "matched": bool(record.matched),
                "planets": _first_seen(planets),
                "houses": _thaw(record.compatibility_houses),
                "aspects_used": deepcopy(aspects_used),
                "evidence": evidence,
                "trace_id": record.trace_reference,
            }
        )
    return output


def _issue_to_data(issue: DefinitionIssue | PreparationIssue) -> dict[str, Any]:
    if isinstance(issue, DefinitionIssue):
        return {"kind": "definition", "value": definition_issue_projection(issue)}
    return {
        "kind": "preparation",
        "value": {
            "code": issue.code,
            "path": issue.path,
            "capability_id": issue.capability_id,
        },
    }


def _result_to_data(result: PredicateResult | ConditionResult | None, *, full: bool) -> tuple[str | None, Any]:
    if result is None:
        return None, None
    if isinstance(result, ConditionResult):
        return "condition", (
            condition_result_to_full_data(result)
            if full else condition_result_to_logical_data(result)
        )
    return "predicate", (
        predicate_result_to_full_data(result)
        if full else predicate_result_to_logical_data(result)
    )


def _record_to_data(record: YogaEvaluationRecord, *, full: bool) -> dict[str, Any]:
    result_kind, result = _result_to_data(record.condition_result, full=full)
    data = {
        "yoga_id": record.yoga_id,
        "name": record.name,
        "rule_version": record.rule_version,
        "source": {
            "source_name": record.source.source_name,
            "rule_id": record.source.rule_id,
            "rule_index": record.source.rule_index,
        },
        "definition_disposition": record.definition_disposition.value,
        "definition_issues": tuple(definition_issue_projection(item) for item in record.definition_issues),
        "condition_result_kind": result_kind,
        "condition_result": result,
        "matched": record.matched,
        "status": record.status.value,
        "trace_reference": record.trace_reference,
        "compatibility_evidence": record.compatibility_evidence,
        "compatibility_houses": record.compatibility_houses,
    }
    if full:
        data["evaluation_time_ms"] = record.evaluation_time_ms
    return data


def yoga_batch_to_logical_data(batch: YogaEvaluationBatch) -> FrozenMapping:
    if not isinstance(batch, YogaEvaluationBatch):
        raise TypeError("batch must be YogaEvaluationBatch")
    return FrozenMapping(
        {
            "schema_version": batch.schema_version,
            "evaluator_version": batch.evaluator_version,
            "prepared_state_digest": batch.prepared_state_digest,
            "records": tuple(_record_to_data(item, full=False) for item in batch.records),
            "batch_issues": tuple(_issue_to_data(item) for item in batch.batch_issues),
        }
    )


def yoga_batch_to_full_data(batch: YogaEvaluationBatch) -> FrozenMapping:
    data = dict(yoga_batch_to_logical_data(batch))
    data["records"] = tuple(_record_to_data(item, full=True) for item in batch.records)
    data["total_duration_ms"] = batch.total_duration_ms
    return FrozenMapping(data)


def yoga_batch_logical_json_bytes(batch: YogaEvaluationBatch) -> bytes:
    return canonical_json_bytes(yoga_batch_to_logical_data(batch))


def yoga_batch_full_json_bytes(batch: YogaEvaluationBatch) -> bytes:
    return canonical_json_bytes(yoga_batch_to_full_data(batch))


def yoga_batch_logical_sha256(batch: YogaEvaluationBatch) -> str:
    return hashlib.sha256(yoga_batch_logical_json_bytes(batch)).hexdigest()


def yoga_batch_full_sha256(batch: YogaEvaluationBatch) -> str:
    return hashlib.sha256(yoga_batch_full_json_bytes(batch)).hexdigest()


def _definition_issue_from_data(data: Mapping[str, Any]) -> DefinitionIssue:
    source = data["source"]
    return DefinitionIssue(
        code=data["code"],
        message=data["message"],
        node_path=data["node_path"],
        source=RuleSourceIdentity(
            source_name=source["source_name"],
            rule_id=source["rule_id"],
            rule_index=source["rule_index"],
        ),
        predicate_id=data["predicate_id"],
        parameter_name=data["parameter_name"],
        details=data["details"],
        severity=DefinitionIssueSeverity(data["severity"]),
    )


def _batch_issue_from_data(data: Mapping[str, Any]) -> DefinitionIssue | PreparationIssue:
    if data["kind"] == "definition":
        return _definition_issue_from_data(data["value"])
    value = data["value"]
    return PreparationIssue(
        code=value["code"], path=value["path"], capability_id=value["capability_id"]
    )


def _record_from_data(data: Mapping[str, Any], *, full: bool) -> YogaEvaluationRecord:
    kind = data["condition_result_kind"]
    raw_result = data["condition_result"]
    if kind == "condition":
        result = (
            condition_result_from_full_data(raw_result)
            if full else condition_result_from_logical_data(raw_result)
        )
    elif kind == "predicate":
        result = (
            predicate_result_from_full_data(raw_result)
            if full else predicate_result_from_logical_data(raw_result)
        )
    elif kind is None and raw_result is None:
        result = None
    else:
        raise CanonicalValueError("invalid Yoga condition result kind")
    return YogaEvaluationRecord(
        yoga_id=data["yoga_id"],
        name=data["name"],
        rule_version=data["rule_version"],
        source=RuleSourceIdentity(
            source_name=data["source"]["source_name"],
            rule_id=data["source"]["rule_id"],
            rule_index=data["source"]["rule_index"],
        ),
        definition_disposition=YogaDefinitionDisposition(data["definition_disposition"]),
        definition_issues=tuple(_definition_issue_from_data(item) for item in data["definition_issues"]),
        condition_result=result,
        matched=data["matched"],
        status=PredicateStatus(data["status"]),
        trace_reference=data["trace_reference"],
        compatibility_evidence=data["compatibility_evidence"],
        compatibility_houses=tuple(data["compatibility_houses"]),
        evaluation_time_ms=data["evaluation_time_ms"] if full else None,
    )


def _batch_from_data(data: Mapping[str, Any], *, full: bool) -> YogaEvaluationBatch:
    required = {
        "schema_version", "evaluator_version", "prepared_state_digest",
        "records", "batch_issues",
    } | ({"total_duration_ms"} if full else set())
    if not isinstance(data, Mapping) or set(data) != required:
        raise CanonicalValueError("invalid Yoga batch projection")
    return YogaEvaluationBatch(
        schema_version=data["schema_version"],
        evaluator_version=data["evaluator_version"],
        prepared_state_digest=data["prepared_state_digest"],
        records=tuple(_record_from_data(item, full=full) for item in data["records"]),
        batch_issues=tuple(_batch_issue_from_data(item) for item in data["batch_issues"]),
        total_duration_ms=data["total_duration_ms"] if full else None,
    )


def _load_json(payload: str | bytes) -> Any:
    def object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise CanonicalValueError("duplicate Yoga JSON key")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise CanonicalValueError(f"non-finite Yoga JSON constant: {value}")

    try:
        text = payload.decode("utf-8") if isinstance(payload, bytes) else payload
        return json.loads(
            text,
            object_pairs_hook=object_without_duplicates,
            parse_constant=reject_constant,
        )
    except CanonicalValueError:
        raise
    except (AttributeError, UnicodeError, json.JSONDecodeError) as exc:
        raise CanonicalValueError("invalid Yoga JSON") from exc


def yoga_batch_from_logical_json(payload: str | bytes) -> YogaEvaluationBatch:
    return _batch_from_data(_load_json(payload), full=False)


def yoga_batch_from_full_json(payload: str | bytes) -> YogaEvaluationBatch:
    return _batch_from_data(_load_json(payload), full=True)


def evaluate_yoga_rules(astro: AstroState) -> List[Dict[str, Any]]:
    """Legacy mutable-AstroState wrapper over the typed WP13 pipeline."""

    source = load_yoga_rule_source()
    preparation = prepare_legacy_yoga_state(astro, source)
    if not preparation.outcome.succeeded or preparation.outcome.state is None:
        batch = yoga_batch_from_preparation_failure(source, preparation.outcome.issues)
    else:
        batch = evaluate_yoga_batch(
            preparation.outcome.state,
            PredicateEvaluationContext(),
            source,
            predicate_evaluator=PredicateEvaluator(),
            compatibility_graph=preparation.compatibility_graph,
        )
    projected = project_yoga_compatibility(batch)
    try:
        if getattr(astro, "enrichments", None) is None:
            astro.enrichments = {}
        astro.enrichments["yogas"] = deepcopy(projected)
    except Exception:
        pass
    return projected


__all__ = (
    "DEFAULT_YOGA_RULE_PATH",
    "YOGA_EVALUATOR_VERSION",
    "YOGA_SCHEMA_VERSION",
    "YOGA_TRACE_NAMESPACE",
    "YogaDefinitionDisposition",
    "YogaEvaluationBatch",
    "YogaEvaluationRecord",
    "YogaLegacyPreparation",
    "YogaRuleSource",
    "evaluate_yoga_batch",
    "evaluate_yoga_rules",
    "load_yoga_rule_source",
    "prepare_legacy_yoga_state",
    "project_yoga_compatibility",
    "yoga_batch_from_full_json",
    "yoga_batch_from_logical_json",
    "yoga_batch_full_json_bytes",
    "yoga_batch_full_sha256",
    "yoga_batch_logical_json_bytes",
    "yoga_batch_logical_sha256",
    "yoga_batch_to_full_data",
    "yoga_batch_to_logical_data",
    "yoga_batch_from_preparation_failure",
)
