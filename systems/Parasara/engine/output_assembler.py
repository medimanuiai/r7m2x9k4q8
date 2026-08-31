"""Serialization-only Prompt-05 OutputAssembler and compatibility profiles.

Only validated immutable Prompt-05 values enter this module.  It deliberately
does not import AstroState, adapters, predicates, rule engines, inference
engines, interpreters, Dasha calculators, or transit calculators.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
from typing import Any

from systems.Parasara.engine.domain.models import (
    DOMAIN_ORDER,
    DashaTimeline,
    DomainId,
    DomainIssue,
    DomainIssueSeverity,
    DomainPrediction,
    DomainStatus,
    TimingOutputStatus,
    TransitSummary,
    YogaDiagnostic,
    compatibility_value_to_python,
)
from systems.Parasara.engine.rules.canonical import (
    FrozenMapping,
    canonical_json_data,
    freeze_canonical,
)


OUTPUT_SCHEMA_VERSION = "1.0.0"
SNAPSHOT_COMPATIBILITY_PROFILE = "parasara_snapshot_v1"


def _text(name: str, value: Any) -> None:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{name} must be a canonical nonempty string")


def _mapping(name: str, value: Any) -> FrozenMapping:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    frozen = freeze_canonical(value, path=f"$.{name}")
    if not isinstance(frozen, FrozenMapping):
        raise TypeError(f"{name} must be a mapping")
    return frozen


@dataclass(frozen=True, slots=True, kw_only=True)
class EngineMetadata:
    name: str
    engine_version: str
    rule_set_family: str
    rule_set_version: str
    public_meta_engine_version: str
    generated_at: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "name", "engine_version", "rule_set_family", "rule_set_version",
            "public_meta_engine_version",
        ):
            _text(name, getattr(self, name))
        if self.generated_at is not None:
            _text("generated_at", self.generated_at)


@dataclass(frozen=True, slots=True, kw_only=True)
class AstroDiagnostics:
    lagna_summary: Mapping[str, Any]
    planet_strengths: Mapping[str, Any]
    houses: tuple[Mapping[str, Any], ...]
    aspects: Any

    def __post_init__(self) -> None:
        object.__setattr__(self, "lagna_summary", _mapping("lagna_summary", self.lagna_summary))
        object.__setattr__(self, "planet_strengths", _mapping("planet_strengths", self.planet_strengths))
        if not isinstance(self.houses, tuple) or any(not isinstance(item, Mapping) for item in self.houses):
            raise TypeError("houses must be an immutable tuple of mappings")
        frozen_houses = freeze_canonical(self.houses, path="$.houses")
        if not isinstance(frozen_houses, tuple):
            raise TypeError("houses must be an immutable tuple")
        object.__setattr__(self, "houses", frozen_houses)
        frozen_aspects = freeze_canonical(self.aspects, path="$.aspects")
        if not isinstance(frozen_aspects, (FrozenMapping, tuple)):
            raise TypeError("aspects must be an immutable mapping or sequence")
        object.__setattr__(self, "aspects", frozen_aspects)


@dataclass(frozen=True, slots=True, kw_only=True)
class ExplainabilityBundle:
    indicators_legend: Mapping[str, Any] = field(default_factory=dict)
    scoring_formula: Mapping[str, Any] = field(default_factory=dict)
    conflict_resolution_policy: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "indicators_legend", "scoring_formula", "conflict_resolution_policy"
        ):
            object.__setattr__(self, name, _mapping(name, getattr(self, name)))


@dataclass(frozen=True, slots=True, kw_only=True)
class OutputAssemblyInput:
    engine_metadata: EngineMetadata
    astro_diagnostics: AstroDiagnostics
    yogas: tuple[YogaDiagnostic, ...]
    domains: tuple[DomainPrediction, ...]
    dasha_timeline: DashaTimeline
    transit_summary: TransitSummary
    explainability: ExplainabilityBundle
    warnings: tuple[DomainIssue, ...]
    errors: tuple[DomainIssue, ...]
    output_schema_version: str
    compatibility_profile: str

    def __post_init__(self) -> None:
        if not isinstance(self.engine_metadata, EngineMetadata):
            raise TypeError("engine_metadata must be EngineMetadata")
        if not isinstance(self.astro_diagnostics, AstroDiagnostics):
            raise TypeError("astro_diagnostics must be AstroDiagnostics")
        if not isinstance(self.yogas, tuple) or any(not isinstance(item, YogaDiagnostic) for item in self.yogas):
            raise TypeError("yogas must be an immutable YogaDiagnostic tuple")
        if not isinstance(self.domains, tuple) or any(not isinstance(item, DomainPrediction) for item in self.domains):
            raise TypeError("domains must be an immutable DomainPrediction tuple")
        if not isinstance(self.dasha_timeline, DashaTimeline):
            raise TypeError("dasha_timeline must be DashaTimeline")
        if not isinstance(self.transit_summary, TransitSummary):
            raise TypeError("transit_summary must be TransitSummary")
        if not isinstance(self.explainability, ExplainabilityBundle):
            raise TypeError("explainability must be ExplainabilityBundle")
        for name in ("warnings", "errors"):
            values = getattr(self, name)
            if not isinstance(values, tuple) or any(not isinstance(item, DomainIssue) for item in values):
                raise TypeError(f"{name} must be an immutable DomainIssue tuple")
        _text("output_schema_version", self.output_schema_version)
        _text("compatibility_profile", self.compatibility_profile)
        self._validate_consistency()

    def _validate_consistency(self) -> None:
        if self.output_schema_version != OUTPUT_SCHEMA_VERSION:
            raise ValueError("unsupported output schema version")
        if self.compatibility_profile != SNAPSHOT_COMPATIBILITY_PROFILE:
            raise ValueError("unsupported compatibility profile")
        domain_ids = tuple(item.domain for item in self.domains)
        if len(set(domain_ids)) != len(domain_ids):
            raise ValueError("domain prediction identities must be unique")
        if tuple(sorted(domain_ids, key=DOMAIN_ORDER.index)) != domain_ids:
            raise ValueError("domain predictions use non-canonical order")
        if any(item.system != "parashara" for item in self.domains):
            raise ValueError("output contains an incompatible interpretation system")
        if any(
            item.rule_set_version is not None
            and item.rule_set_version != self.engine_metadata.rule_set_version
            for item in self.domains
        ):
            raise ValueError("domain/engine rule-set versions disagree")
        if any(
            item.engine_version != self.engine_metadata.engine_version
            for item in self.domains
        ):
            raise ValueError("domain/engine versions disagree")
        if any(
            item.rule_set_version != self.engine_metadata.rule_set_version
            for item in self.yogas
        ):
            raise ValueError("Yoga/engine rule-set versions disagree")
        if any(
            item.source_rule_match.system != "parashara" for item in self.yogas
        ):
            raise ValueError("output contains an incompatible Yoga system")
        yoga_keys = tuple((item.yoga_id, item.rule_version) for item in self.yogas)
        if len(set(yoga_keys)) != len(yoga_keys):
            raise ValueError("Yoga diagnostics must be unique")
        if tuple(item.compatibility.source_order for item in self.yogas) != tuple(
            range(len(self.yogas))
        ):
            raise ValueError("Yoga diagnostics do not preserve approved source order")
        if self.warnings or self.errors:
            raise ValueError(
                "the locked compatibility profile has no warning/error fields"
            )


class OutputAssemblyError(ValueError):
    """Bounded schema/profile failure carrying a non-sensitive typed issue."""

    def __init__(self, issue: DomainIssue) -> None:
        self.issue = issue
        super().__init__(issue.code)


def _assembly_error(message: str) -> OutputAssemblyError:
    return OutputAssemblyError(DomainIssue(
        issue_id="output.issue.compatibility",
        code="ASSEMBLY_SCHEMA_VIOLATION",
        severity=DomainIssueSeverity.ERROR,
        phase="output_assembly",
        message=message,
        recoverable=False,
        details={},
    ))


def project_career_prediction_compatibility(
    prediction: DomainPrediction,
) -> dict[str, Any]:
    """One-way Career projection for the locked current public dictionary."""

    if not isinstance(prediction, DomainPrediction) or prediction.domain is not DomainId.CAREER:
        raise TypeError("prediction must be a Career DomainPrediction")
    if prediction.status not in {
        DomainStatus.EVALUATED,
        DomainStatus.PARTIAL,
        DomainStatus.INSUFFICIENT_EVIDENCE,
    }:
        raise _assembly_error("The Career result is not publishable under this profile.")
    profile = prediction.career_compatibility
    if profile is None or profile.profile_id != "career_public_v1":
        raise _assembly_error("The Career compatibility profile is missing or incompatible.")
    precision = profile.precision

    components = []
    for item in profile.components:
        if item.kind.value == "planet":
            components.append({
                "type": "planet",
                "planet": item.planet,
                "house": item.house,
                "weight": item.weight,
            })
        else:
            components.append({
                "type": "house",
                "house": item.house,
                "weight": item.weight,
                "occupants": list(item.occupants),
            })

    indicators = []
    evidence_rows = []
    compatibility_by_id = {item.indicator_id: item for item in profile.indicators}
    for item in prediction.indicators:
        compatibility = compatibility_by_id[item.indicator_id]
        evidence = compatibility_value_to_python(compatibility.evidence)
        context = compatibility_value_to_python(compatibility.context)
        contribution = float(item.contribution)
        indicators.append({
            "rule_id": item.source_rule_id,
            "contribution": contribution,
            "evidence": evidence,
            "context": context,
        })
        evidence_rows.append({
            "rule_id": item.source_rule_id,
            "rule": deepcopy(context),
            "match": True,
            "evidence": deepcopy(evidence),
            "contribution": round(contribution, 3),
        })
        components.append({
            "type": "rule",
            "rule_id": item.source_rule_id,
            "weight": round(contribution, 3),
        })

    return {
        "summary": prediction.summary,
        "score": round(float(prediction.score), precision),
        "confidence": round(float(prediction.confidence), precision),
        "components": components,
        "indicators": indicators,
        "evidence": evidence_rows,
        "scoring": {
            "base_score": round(profile.base_score, precision),
            "total_contribution": round(profile.total_contribution, precision),
            "final_score": round(float(prediction.score), precision),
            "formula": profile.formula,
        },
        "trace_id": profile.public_trace_id,
    }


def _compatibility_key_order(value: Mapping[str, Any]) -> tuple[str, ...]:
    keys = tuple(value)
    key_set = set(keys)
    if {
        "source_planet", "source_sign", "source_degree", "offset",
        "target_sign", "matched_planets", "explanation",
    } <= key_set:
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


def _yoga_thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _yoga_thaw(value[key]) for key in _compatibility_key_order(value)}
    if isinstance(value, tuple):
        return [_yoga_thaw(item) for item in value]
    return value


def _first_seen(values: list[Any]) -> list[Any]:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def project_yoga_diagnostics_compatibility(
    diagnostics: tuple[YogaDiagnostic, ...],
) -> list[dict[str, Any]]:
    """One-way Yoga projection from RuleMatch-backed diagnostics."""

    if not isinstance(diagnostics, tuple) or any(
        not isinstance(item, YogaDiagnostic) for item in diagnostics
    ):
        raise TypeError("diagnostics must be a YogaDiagnostic tuple")
    output = []
    for diagnostic in diagnostics:
        compatibility = diagnostic.compatibility
        evidence = _yoga_thaw(compatibility.evidence)
        planets = []
        if isinstance(evidence.get("matched_planets"), list):
            planets.extend(evidence["matched_planets"])
        if not planets and isinstance(evidence.get("children"), list):
            for child in evidence["children"]:
                if isinstance(child, dict) and isinstance(child.get("matched_planets"), list):
                    planets.extend(child["matched_planets"])
        aspects_used = evidence.get("matched_edges", [])
        output.append({
            "yoga_id": diagnostic.yoga_id,
            "name": compatibility.name,
            "matched": diagnostic.matched,
            "planets": _first_seen(planets),
            "houses": _yoga_thaw(compatibility.houses),
            "aspects_used": deepcopy(aspects_used),
            "evidence": evidence,
            "trace_id": diagnostic.trace_id,
        })
    return output


class OutputAssembler:
    """The sole active typed public-output assembly service."""

    def assemble(self, value: OutputAssemblyInput) -> dict[str, Any]:
        if not isinstance(value, OutputAssemblyInput):
            raise TypeError("value must be OutputAssemblyInput")
        career = next(
            (item for item in value.domains if item.domain is DomainId.CAREER),
            None,
        )
        if career is None:
            raise _assembly_error("The locked profile requires one Career result.")
        if value.dasha_timeline.status not in {
            TimingOutputStatus.UNAVAILABLE,
            TimingOutputStatus.NOT_REQUESTED,
        }:
            raise _assembly_error("This public profile cannot expose typed Dasha output yet.")
        if value.transit_summary.status not in {
            TimingOutputStatus.UNAVAILABLE,
            TimingOutputStatus.NOT_REQUESTED,
        }:
            raise _assembly_error("This public profile cannot expose typed transit output yet.")
        metadata = value.engine_metadata
        diagnostics = value.astro_diagnostics
        explainability = value.explainability
        return {
            "engine": {
                "name": metadata.name,
                "engine_version": metadata.engine_version,
                "rule_set_family": metadata.rule_set_family,
                "rule_set_version": metadata.rule_set_version,
            },
            "meta": {
                "engine_version": metadata.public_meta_engine_version,
                "generated_at": metadata.generated_at,
            },
            "diagnostics": {
                "lagna_summary": canonical_json_data(diagnostics.lagna_summary),
                "planet_strengths": canonical_json_data(diagnostics.planet_strengths),
                "houses": canonical_json_data(diagnostics.houses),
                "aspects": canonical_json_data(diagnostics.aspects),
                "yogas": project_yoga_diagnostics_compatibility(value.yogas),
            },
            "domains": {
                "career": project_career_prediction_compatibility(career),
                "wealth": {
                    "summary": "",
                    "score": 0.5,
                    "confidence": 0.5,
                    "components": [],
                    "indicators": [],
                },
            },
            "dasha_timeline": [],
            "transits": [],
            "explainability": {
                "indicators_legend": canonical_json_data(explainability.indicators_legend),
                "scoring_formula": canonical_json_data(explainability.scoring_formula),
                "conflict_resolution_policy": canonical_json_data(
                    explainability.conflict_resolution_policy
                ),
            },
        }

    def canonical_json_bytes(self, value: OutputAssemblyInput) -> bytes:
        payload = json.dumps(
            self.assemble(value),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return payload

    def snapshot_json_bytes(self, value: OutputAssemblyInput) -> bytes:
        """Serialize the locked pretty-printed snapshot at the sole boundary."""

        payload = json.dumps(
            self.assemble(value),
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        return payload.replace(b"\n", b"\r\n")

    def logical_digest(self, value: OutputAssemblyInput) -> str:
        return hashlib.sha256(self.canonical_json_bytes(value)).hexdigest()


__all__ = (
    "OUTPUT_SCHEMA_VERSION",
    "SNAPSHOT_COMPATIBILITY_PROFILE",
    "AstroDiagnostics",
    "EngineMetadata",
    "ExplainabilityBundle",
    "OutputAssembler",
    "OutputAssemblyError",
    "OutputAssemblyInput",
    "project_career_prediction_compatibility",
    "project_yoga_diagnostics_compatibility",
)
