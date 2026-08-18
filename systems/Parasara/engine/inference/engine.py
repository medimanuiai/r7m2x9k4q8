"""The sole shared deterministic aggregator for universal RuleMatch values."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
import hashlib
import math
from typing import Any

from systems.Parasara.engine.inference.config import InferenceConfig
from systems.Parasara.engine.inference.models import (
    ConflictRecord,
    ConflictSide,
    Contribution,
    ContributionSign,
    DataCompleteness,
    EvidenceReference,
    ExplanationFactor,
    INFERENCE_SCHEMA_VERSION,
    InferenceComponent,
    InferenceError,
    InferenceResult,
    InferenceStatus,
    TimingContext,
)
from systems.Parasara.engine.rules.canonical import canonical_json_bytes
from systems.Parasara.engine.rules.rule_match import (
    RuleMatch,
    RuleMatchStatus,
    rule_match_logical_sha256,
)


def _stable_id(prefix: str, *parts: str) -> str:
    payload = "|".join((prefix, *parts)).encode("utf-8")
    return f"{prefix}.{hashlib.sha256(payload).hexdigest()[:24]}"


def _clip(value: float, lower: float, upper: float) -> float:
    return min(upper, max(lower, value))


def _config_digest(config: InferenceConfig) -> str:
    data = {
        name: getattr(config, name)
        for name in config.__dataclass_fields__
    }
    return hashlib.sha256(canonical_json_bytes(data)).hexdigest()


def _context_rank(config: InferenceConfig, context: str) -> int:
    order = config.contribution["context_order"]
    try:
        return order.index(context)
    except ValueError:
        return len(order)


def _rule_order(config: InferenceConfig, value: RuleMatch) -> tuple[Any, ...]:
    return (
        _context_rank(config, value.context),
        -value.priority,
        value.rule_id,
        value.rule_version,
        rule_match_logical_sha256(value),
    )


def _correlation_key(rule: RuleMatch) -> str:
    explicit = rule.metadata.get("correlation_key")
    if isinstance(explicit, str) and explicit:
        return explicit
    fact_id = rule.evidence.get("fact_id")
    if isinstance(fact_id, str) and fact_id:
        return fact_id
    if rule.predicate_results:
        return f"predicate:{rule.predicate_results[0].predicate_id}"
    return f"rule:{rule.rule_id}"


def _evidence_references(rule: RuleMatch) -> tuple[EvidenceReference, ...]:
    correlation = _correlation_key(rule)
    references: list[EvidenceReference] = []
    for index, predicate in enumerate(rule.predicate_results):
        trace_id = predicate.trace_steps[0].step_id if predicate.trace_steps else rule.trace_id
        source_id = predicate.predicate_id
        references.append(EvidenceReference(
            evidence_id=_stable_id("evidence", rule.rule_id, source_id, str(index)),
            source_type="predicate",
            source_id=source_id,
            trace_id=trace_id,
            correlation_key=correlation,
            order=len(references),
        ))
    for reference in rule.trace_references:
        if any(item.trace_id == reference.trace_id for item in references):
            continue
        references.append(EvidenceReference(
            evidence_id=_stable_id("evidence", rule.rule_id, reference.trace_id, str(len(references))),
            source_type=reference.trace_type,
            source_id=reference.trace_id,
            trace_id=reference.trace_id,
            correlation_key=correlation,
            order=len(references),
        ))
    if not references:
        references.append(EvidenceReference(
            evidence_id=_stable_id("evidence", rule.rule_id, rule.trace_id, "0"),
            source_type="rule_trace",
            source_id=rule.rule_id,
            trace_id=rule.trace_id,
            correlation_key=correlation,
            order=0,
        ))
    return tuple(references)


def _sign(rule: RuleMatch) -> ContributionSign:
    explicit = rule.metadata.get("inference_sign")
    if explicit is not None:
        try:
            return ContributionSign(explicit)
        except ValueError as exc:
            raise ValueError(f"unknown inference sign for {rule.rule_id}") from exc
    if rule.base_weight > 0:
        return ContributionSign.POSITIVE
    if rule.base_weight < 0:
        return ContributionSign.NEGATIVE
    return ContributionSign.NEUTRAL


def _contribution(rule: RuleMatch, domain: str, config: InferenceConfig) -> Contribution:
    sign = _sign(rule)
    quality = rule.quality
    if quality is None:
        quality = float(config.contribution["quality_fallback"])
    if not 0.0 <= quality <= 1.0:
        raise ValueError(f"rule quality outside [0, 1] for {rule.rule_id}")
    evidence_strength = 1.0
    context_multipliers = config.contribution["context_multipliers"]
    if rule.context not in context_multipliers:
        raise ValueError(f"unconfigured inference context: {rule.context}")
    context_multiplier = float(context_multipliers[rule.context])
    priority_multiplier = 1.0
    overrides = config.contribution["rule_weight_overrides"]
    magnitude = float(overrides.get(rule.rule_id, abs(rule.base_weight)))
    if magnitude < 0.0 or not math.isfinite(magnitude):
        raise ValueError(f"invalid contribution magnitude for {rule.rule_id}")
    if sign is ContributionSign.POSITIVE:
        sign_multiplier = 1.0
    elif sign is ContributionSign.NEGATIVE:
        sign_multiplier = -1.0
    elif sign is ContributionSign.NEUTRAL:
        sign_multiplier = 0.0
    else:
        mixed_net = rule.metadata.get("mixed_net_multiplier")
        if isinstance(mixed_net, bool) or not isinstance(mixed_net, (int, float)) or not -1.0 <= mixed_net <= 1.0:
            raise ValueError("mixed contribution requires mixed_net_multiplier in [-1, 1]")
        sign_multiplier = float(mixed_net)
    final = (
        sign_multiplier * magnitude * quality * evidence_strength
        * context_multiplier * priority_multiplier
    )
    contribution_id = _stable_id(
        "contribution", domain, rule.rule_id, rule.rule_version, rule.rule_set_version,
        rule.trace_id, config.inference_version,
    )
    references = _evidence_references(rule)
    correlation_keys = tuple(sorted({item.correlation_key for item in references}))
    return Contribution(
        contribution_id=contribution_id,
        rule_id=rule.rule_id,
        rule_version=rule.rule_version,
        rule_set_version=rule.rule_set_version,
        domain=domain,
        category=rule.category,
        context=rule.context,
        sign=sign,
        base_weight=rule.base_weight,
        rule_quality=quality,
        evidence_strength=evidence_strength,
        context_multiplier=context_multiplier,
        priority_multiplier=priority_multiplier,
        final_contribution=final,
        priority=rule.priority,
        evidence_references=references,
        correlation_keys=correlation_keys,
        source_rule_trace_id=rule.trace_id,
        trace_id=_stable_id("trace", contribution_id, rule.trace_id),
    )


def _unique_references(values: Sequence[Contribution]) -> tuple[EvidenceReference, ...]:
    found: dict[str, EvidenceReference] = {}
    for contribution in values:
        for reference in contribution.evidence_references:
            found.setdefault(reference.evidence_id, reference)
    return tuple(found.values())


def _components(
    domain: str,
    values: Sequence[Contribution],
    config: InferenceConfig,
) -> tuple[InferenceComponent, ...]:
    grouped: dict[str, list[Contribution]] = defaultdict(list)
    for value in values:
        grouped[value.category].append(value)
    normalization = config.normalization
    precision = normalization["precision"]
    result = []
    for category in sorted(grouped):
        items = grouped[category]
        raw = math.fsum(item.final_contribution for item in items)
        normalized = round(_clip(
            normalization["neutral_score"] + raw,
            normalization["score_min"],
            normalization["score_max"],
        ), precision)
        component_id = _stable_id("component", domain, category, *(item.contribution_id for item in items))
        result.append(InferenceComponent(
            component_id=component_id,
            domain=domain,
            category=category,
            raw_contribution=raw,
            normalized_value=normalized,
            contribution_ids=tuple(item.contribution_id for item in items),
            rule_ids=tuple(item.rule_id for item in items),
            evidence_references=_unique_references(items),
            trace_id=_stable_id("trace", component_id),
        ))
    return tuple(result)


def _side_rank(values: Sequence[Contribution]) -> tuple[Any, ...]:
    return (
        max(item.priority for item in values),
        max(item.rule_quality for item in values),
        max(item.evidence_strength for item in values),
        len({key for item in values for key in item.correlation_keys}),
    )


def _conflicts(domain: str, values: Sequence[Contribution], config: InferenceConfig) -> tuple[ConflictRecord, ...]:
    grouped: dict[tuple[str, str], list[Contribution]] = defaultdict(list)
    for value in values:
        grouped[(value.category, value.context)].append(value)
    records = []
    for (category, context), items in sorted(grouped.items()):
        positive = [item for item in items if item.final_contribution > 0.0]
        negative = [item for item in items if item.final_contribution < 0.0]
        if not positive or not negative:
            continue
        positive_rank = _side_rank(positive)
        negative_rank = _side_rank(negative)
        if positive_rank > negative_rank:
            winner = ConflictSide.POSITIVE
            unresolved = False
        elif negative_rank > positive_rank:
            winner = ConflictSide.NEGATIVE
            unresolved = False
        else:
            winner = ConflictSide.TIED
            unresolved = True
        conflict_id = _stable_id(
            "conflict", domain, category, context,
            *(sorted(item.rule_id for item in (*positive, *negative))),
        )
        records.append(ConflictRecord(
            conflict_id=conflict_id,
            domain=domain,
            positive_rule_ids=tuple(sorted(item.rule_id for item in positive)),
            negative_rule_ids=tuple(sorted(item.rule_id for item in negative)),
            highest_priority=max(item.priority for item in items),
            resolution_method="priority_quality_evidence_independence",
            winning_side=winner,
            unresolved=unresolved,
            confidence_impact=(float(config.confidence["unresolved_conflict_penalty"]) if unresolved else 0.0),
            rationale_code=("exact_structural_tie" if unresolved else f"{winner.value}_ranked_higher"),
            trace_id=_stable_id("trace", conflict_id),
        ))
    return tuple(records)


def _agreement(values: Sequence[Contribution], config: InferenceConfig) -> float:
    scored = [item.final_contribution for item in values if item.final_contribution != 0.0]
    if not scored:
        return 0.0
    absolute = math.fsum(abs(item) for item in scored)
    result = abs(math.fsum(scored)) / absolute if absolute else 0.0
    return round(_clip(result, 0.0, 1.0), config.agreement["precision"])


def _confidence(
    rules: Sequence[RuleMatch],
    contributions: Sequence[Contribution],
    completeness: DataCompleteness,
    agreement: float,
    conflicts: Sequence[ConflictRecord],
    config: InferenceConfig,
) -> float:
    eligible_rules = [item for item in rules if item.metadata.get("confidence_eligible") is not False]
    contribution_by_rule = {item.rule_id: item for item in contributions}
    matched = [item for item in eligible_rules if item.status is RuleMatchStatus.MATCHED and item.rule_id in contribution_by_rule]
    coverage = len(matched) / len(eligible_rules) if eligible_rules else 0.0
    scored = [abs(contribution_by_rule[item.rule_id].final_contribution) for item in matched]
    evidence_strength = math.fsum(scored) / len(scored) if scored else 0.0
    quality = math.fsum(contribution_by_rule[item.rule_id].rule_quality for item in matched) / len(matched) if matched else 0.0
    correlations = {key for item in matched for key in contribution_by_rule[item.rule_id].correlation_keys}
    independence = min(1.0, len(correlations) / len(matched)) if matched else 0.0
    diversity = min(1.0, len({item.category for item in matched}) / len(matched)) if matched else 0.0
    factors = {
        "rule_coverage": coverage,
        "evidence_strength": _clip(evidence_strength, 0.0, 1.0),
        "data_completeness": completeness.completeness_score,
        "rule_quality": quality,
        "context_agreement": agreement,
        "independent_evidence": independence,
        "category_diversity": diversity,
    }
    weights = config.confidence["factor_weights"]
    value = math.fsum(float(weights[name]) * factors[name] for name in sorted(factors))
    value -= math.fsum(item.confidence_impact for item in conflicts if item.unresolved)
    value -= len(completeness.missing_required) * float(config.confidence["missing_required_penalty"])
    value -= len(completeness.missing_optional) * float(config.confidence["missing_optional_penalty"])
    return round(_clip(value, 0.0, 1.0), config.confidence["precision"])


def _factors(
    domain: str,
    contributions: Sequence[Contribution],
    conflicts: Sequence[ConflictRecord],
    completeness: DataCompleteness,
) -> tuple[ExplanationFactor, ...]:
    factors: list[ExplanationFactor] = []
    for direction, selected, kind in (
        (ContributionSign.POSITIVE, [item for item in contributions if item.final_contribution > 0], "dominant_support"),
        (ContributionSign.NEGATIVE, [item for item in contributions if item.final_contribution < 0], "dominant_challenge"),
    ):
        if selected:
            magnitude = max(abs(item.final_contribution) for item in selected)
            dominant = [item for item in selected if abs(item.final_contribution) == magnitude]
            factor_id = _stable_id("factor", domain, kind, *(item.rule_id for item in dominant))
            factors.append(ExplanationFactor(
                factor_id=factor_id, factor_type=kind, direction=direction, magnitude=magnitude,
                source_rule_ids=tuple(sorted(item.rule_id for item in dominant)),
                evidence_references=_unique_references(dominant), trace_id=_stable_id("trace", factor_id),
            ))
    for conflict in conflicts:
        if conflict.unresolved:
            selected = [item for item in contributions if item.rule_id in {*conflict.positive_rule_ids, *conflict.negative_rule_ids}]
            factor_id = _stable_id("factor", domain, "unresolved_conflict", conflict.conflict_id)
            factors.append(ExplanationFactor(
                factor_id=factor_id, factor_type="unresolved_conflict", direction=ContributionSign.MIXED,
                magnitude=conflict.confidence_impact,
                source_rule_ids=tuple(sorted({item.rule_id for item in selected})),
                evidence_references=_unique_references(selected), trace_id=_stable_id("trace", factor_id),
            ))
    if completeness.missing_required:
        factor_id = _stable_id("factor", domain, "missing_required_data", *completeness.missing_required)
        factors.append(ExplanationFactor(
            factor_id=factor_id, factor_type="missing_required_data", direction=ContributionSign.NEUTRAL,
            magnitude=round(1.0 - completeness.completeness_score, 6), source_rule_ids=(),
            evidence_references=(), trace_id=_stable_id("trace", factor_id),
        ))
    return tuple(factors)


def _rule_errors(rules: Sequence[RuleMatch]) -> tuple[InferenceError, ...]:
    errors = []
    for rule in rules:
        for error in rule.errors:
            errors.append(InferenceError(
                code=error.code, message=error.message, phase=error.phase,
                recoverable=error.recoverable, details=error.details,
                source_rule_id=rule.rule_id, source_trace_id=error.source_trace_id or rule.trace_id,
            ))
    return tuple(errors)


class InferenceEngine:
    """Aggregate already-evaluated universal rules without chart access."""

    def aggregate(
        self,
        *,
        domain: str,
        rule_matches: Sequence[RuleMatch],
        timing_context: TimingContext | None,
        data_completeness: DataCompleteness,
        config: InferenceConfig,
    ) -> InferenceResult:
        if not isinstance(domain, str) or not domain.strip() or domain != domain.strip().lower():
            raise ValueError("domain must be a canonical lowercase identifier")
        if not isinstance(config, InferenceConfig):
            raise TypeError("config must be InferenceConfig")
        if not isinstance(data_completeness, DataCompleteness):
            raise TypeError("data_completeness must be DataCompleteness")
        if timing_context is not None and not isinstance(timing_context, TimingContext):
            raise TypeError("timing_context must be TimingContext or None")
        if data_completeness.domain != domain:
            return self._failed(domain, (), data_completeness, config, "invalid_completeness_domain", "Data completeness domain does not match the inference request.")
        if not isinstance(rule_matches, Sequence) or isinstance(rule_matches, (str, bytes)):
            raise TypeError("rule_matches must be a sequence")
        if any(not isinstance(item, RuleMatch) for item in rule_matches):
            raise TypeError("rule_matches must contain only RuleMatch values")
        ordered = tuple(sorted(rule_matches, key=lambda item: _rule_order(config, item)))
        systems = {item.system for item in ordered}
        rule_sets = {item.rule_set_version for item in ordered}
        if systems and (len(systems) != 1 or systems != {config.system}):
            return self._failed(domain, ordered, data_completeness, config, "incompatible_rule_system", "Rule systems are incompatible with inference configuration.")
        if len(rule_sets) > 1:
            return self._failed(domain, ordered, data_completeness, config, "incompatible_rule_set_versions", "Mixed rule-set versions cannot be aggregated.")
        invalid_scope = [item for item in ordered if domain not in item.domains and item.metadata.get("domain_neutral") is not True]
        if invalid_scope:
            return self._failed(domain, ordered, data_completeness, config, "invalid_domain_scope", "One or more rules are outside the requested domain.")

        contributions: list[Contribution] = []
        errors = list(_rule_errors(ordered))
        for rule in ordered:
            if rule.status is not RuleMatchStatus.MATCHED:
                continue
            try:
                contributions.append(_contribution(rule, domain, config))
            except (TypeError, ValueError) as exc:
                errors.append(InferenceError(
                    code="contribution_construction_failed",
                    message="A matched rule could not be converted into a contribution.",
                    phase="contribution",
                    recoverable=False,
                    details={"reason": str(exc)},
                    source_rule_id=rule.rule_id,
                    source_trace_id=rule.trace_id,
                ))
        if any(not error.recoverable for error in errors if error.code == "contribution_construction_failed"):
            return self._failed(
                domain, ordered, data_completeness, config,
                "contribution_construction_failed", "One or more matched rules could not be converted.",
                extra_errors=tuple(errors),
            )
        contributions.sort(key=lambda item: (
            _context_rank(config, item.context), -item.priority, item.rule_id,
            item.rule_version, item.contribution_id,
        ))
        contribution_values = tuple(contributions)
        raw = math.fsum(item.final_contribution for item in contribution_values)
        normalization = config.normalization
        unclipped = normalization["neutral_score"] + raw
        clipped = _clip(unclipped, normalization["score_min"], normalization["score_max"])
        normalized = round(clipped, normalization["precision"])
        conflicts = _conflicts(domain, contribution_values, config)
        agreement = _agreement(contribution_values, config)
        confidence = _confidence(ordered, contribution_values, data_completeness, agreement, conflicts, config)
        no_evidence = not contribution_values
        if no_evidence:
            status = InferenceStatus.INSUFFICIENT_EVIDENCE
            normalized = float(config.no_match["normalized_score"])
            confidence = float(config.no_match["confidence"])
        elif data_completeness.missing_required or any(
            item.status in (RuleMatchStatus.MISSING_CAPABILITY, RuleMatchStatus.INVALID, RuleMatchStatus.ERROR)
            for item in ordered
        ):
            status = InferenceStatus.PARTIAL
        else:
            status = InferenceStatus.EVALUATED
        excluded = tuple(sorted(item.rule_id for item in ordered if item.status in (
            RuleMatchStatus.UNMATCHED, RuleMatchStatus.SKIPPED, RuleMatchStatus.EXCLUDED,
        )))
        unavailable = tuple(sorted(item.rule_id for item in ordered if item.status in (
            RuleMatchStatus.MISSING_CAPABILITY, RuleMatchStatus.INVALID, RuleMatchStatus.ERROR,
        )))
        digest = hashlib.sha256(canonical_json_bytes(tuple(rule_match_logical_sha256(item) for item in ordered))).hexdigest()
        trace_id = _stable_id(
            "inference", domain, config.inference_version, _config_digest(config), digest,
            timing_context.trace_id if timing_context is not None else "timing:none",
            data_completeness.trace_id,
        )
        factors = list(_factors(domain, contribution_values, conflicts, data_completeness))
        if unclipped != clipped and contribution_values:
            factor_id = _stable_id("factor", domain, "score_clipped", str(unclipped), str(normalized))
            factors.append(ExplanationFactor(
                factor_id=factor_id, factor_type="score_clipped",
                direction=ContributionSign.POSITIVE if unclipped > normalized else ContributionSign.NEGATIVE,
                magnitude=abs(unclipped - normalized),
                source_rule_ids=tuple(sorted(item.rule_id for item in contribution_values)),
                evidence_references=_unique_references(contribution_values),
                trace_id=_stable_id("trace", factor_id),
            ))
        return InferenceResult(
            inference_schema_version=config.inference_schema_version,
            inference_version=config.inference_version,
            system=(next(iter(systems)) if systems else config.system),
            rule_set_version=(next(iter(rule_sets)) if rule_sets else "unresolved"),
            domain=domain,
            status=status,
            raw_score=raw,
            normalized_score=normalized,
            confidence=confidence,
            agreement=agreement,
            positive_contributions=tuple(item for item in contribution_values if item.sign is ContributionSign.POSITIVE),
            negative_contributions=tuple(item for item in contribution_values if item.sign is ContributionSign.NEGATIVE),
            neutral_contributions=tuple(item for item in contribution_values if item.sign is ContributionSign.NEUTRAL),
            mixed_contributions=tuple(item for item in contribution_values if item.sign is ContributionSign.MIXED),
            components=_components(domain, contribution_values, config),
            conflicts=conflicts,
            data_completeness=data_completeness,
            explanation_factors=tuple(factors),
            excluded_rule_ids=excluded,
            unavailable_rule_ids=unavailable,
            errors=tuple(errors),
            trace_id=trace_id,
        )

    def _failed(
        self,
        domain: str,
        rules: Sequence[RuleMatch],
        completeness: DataCompleteness,
        config: InferenceConfig,
        code: str,
        message: str,
        *,
        extra_errors: tuple[InferenceError, ...] = (),
    ) -> InferenceResult:
        error = InferenceError(
            code=code, message=message, phase="validation", recoverable=False,
            details={"rule_ids": tuple(sorted(item.rule_id for item in rules))},
        )
        trace_id = _stable_id("inference", domain, config.inference_version, code, *(sorted(item.rule_id for item in rules)))
        systems = sorted({item.system for item in rules})
        rule_sets = sorted({item.rule_set_version for item in rules})
        return InferenceResult(
            inference_schema_version=config.inference_schema_version,
            inference_version=config.inference_version,
            system=systems[0] if len(systems) == 1 else config.system,
            rule_set_version=rule_sets[0] if len(rule_sets) == 1 else "unresolved",
            domain=domain, status=InferenceStatus.FAILED, raw_score=0.0,
            normalized_score=float(config.no_match["normalized_score"]), confidence=0.0,
            agreement=0.0, positive_contributions=(), negative_contributions=(),
            neutral_contributions=(), mixed_contributions=(), components=(), conflicts=(),
            data_completeness=completeness, explanation_factors=(), excluded_rule_ids=(),
            unavailable_rule_ids=tuple(sorted(item.rule_id for item in rules)),
            errors=(*extra_errors, error), trace_id=trace_id,
        )


__all__ = ("InferenceEngine",)
