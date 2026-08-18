"""Typed loader for the versioned shared inference policy."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from systems.Parasara.engine.rules.canonical import (
    FrozenMapping,
    canonical_json_bytes,
    canonical_json_data,
    freeze_canonical,
)


DEFAULT_INFERENCE_CONFIG = (
    Path(__file__).resolve().parents[2] / "config" / "inference" / "career_compat_v1.json"
)


def _nonempty(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


def _number(name: str, value: Any, *, lower: float | None = None, upper: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise TypeError(f"{name} must be finite numeric")
    result = float(value)
    if lower is not None and result < lower:
        raise ValueError(f"{name} must be >= {lower}")
    if upper is not None and result > upper:
        raise ValueError(f"{name} must be <= {upper}")
    return result


def _frozen(name: str, value: Any) -> FrozenMapping:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    result = freeze_canonical(value, path=f"$.{name}")
    if not isinstance(result, FrozenMapping):
        raise TypeError(f"{name} must be a mapping")
    return result


@dataclass(frozen=True, slots=True, kw_only=True)
class InferenceConfig:
    config_schema_version: str
    inference_version: str
    inference_schema_version: str
    system: str
    normalization: Mapping[str, Any]
    contribution: Mapping[str, Any]
    component_grouping: Mapping[str, Any]
    conflict: Mapping[str, Any]
    agreement: Mapping[str, Any]
    confidence: Mapping[str, Any]
    completeness: Mapping[str, Any]
    no_match: Mapping[str, Any]
    trace: Mapping[str, Any]
    career_compatibility: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in ("config_schema_version", "inference_version", "inference_schema_version", "system"):
            _nonempty(name, getattr(self, name))
        for name in (
            "normalization", "contribution", "component_grouping", "conflict", "agreement",
            "confidence", "completeness", "no_match", "trace", "career_compatibility",
        ):
            object.__setattr__(self, name, _frozen(name, getattr(self, name)))
        self._validate_active_policy()

    def _validate_active_policy(self) -> None:
        normalization = self.normalization
        if normalization.get("strategy") != "baseline_additive_clip":
            raise ValueError("unknown normalization strategy")
        lower = _number("score_min", normalization.get("score_min"), lower=0.0, upper=1.0)
        upper = _number("score_max", normalization.get("score_max"), lower=0.0, upper=1.0)
        neutral = _number("neutral_score", normalization.get("neutral_score"), lower=lower, upper=upper)
        if neutral != 0.5 or lower >= upper:
            raise ValueError("active inference normalization requires neutral 0.5 and ordered bounds")
        for section, key in (
            (normalization, "precision"),
            (self.confidence, "precision"), (self.agreement, "precision"),
        ):
            value = section.get(key)
            if type(value) is not int or not 0 <= value <= 12:
                raise ValueError(f"{key} must be an integer precision in [0, 12]")
        if self.contribution.get("rounding_policy") != "no_intermediate_rounding":
            raise ValueError("unknown contribution rounding policy")
        if self.contribution.get("evidence_strength_policy") != "identity":
            raise ValueError("unknown evidence-strength policy")
        if self.contribution.get("priority_multiplier_policy") != "identity":
            raise ValueError("unknown priority-multiplier policy")
        _number("quality_fallback", self.contribution.get("quality_fallback"), lower=0.0, upper=1.0)
        contexts = self.contribution.get("context_multipliers")
        if not isinstance(contexts, Mapping) or not contexts:
            raise ValueError("context_multipliers must be a nonempty mapping")
        for name, value in contexts.items():
            _nonempty("context", name)
            _number("context multiplier", value, lower=0.0)
        order = self.contribution.get("context_order")
        if not isinstance(order, tuple) or set(order) != set(contexts):
            raise ValueError("context_order must enumerate context_multipliers exactly")
        overrides = self.contribution.get("rule_weight_overrides")
        if not isinstance(overrides, Mapping):
            raise ValueError("rule_weight_overrides must be a mapping")
        for rule_id, value in overrides.items():
            _nonempty("rule override ID", rule_id)
            _number("rule weight override", value, lower=0.0)
        if self.confidence.get("strategy") != "career_mvp01_structural":
            raise ValueError("unknown confidence strategy")
        weights = self.confidence.get("factor_weights")
        expected = {
            "rule_coverage", "evidence_strength", "data_completeness", "rule_quality",
            "context_agreement", "independent_evidence", "category_diversity",
        }
        if not isinstance(weights, Mapping) or set(weights) != expected:
            raise ValueError("confidence factor_weights are incomplete")
        for name, value in weights.items():
            _number(f"confidence weight {name}", value, lower=0.0)
        _number("unresolved_conflict_penalty", self.confidence.get("unresolved_conflict_penalty"), lower=0.0, upper=1.0)
        _number("missing_required_penalty", self.confidence.get("missing_required_penalty"), lower=0.0, upper=1.0)
        _number("missing_optional_penalty", self.confidence.get("missing_optional_penalty"), lower=0.0, upper=1.0)
        if self.no_match.get("status") != "insufficient_evidence":
            raise ValueError("active no-match status must be insufficient_evidence")
        _number("no-match normalized score", self.no_match.get("normalized_score"), lower=0.0, upper=1.0)
        _number("no-match confidence", self.no_match.get("confidence"), lower=0.0, upper=1.0)
        career = self.completeness.get("career")
        if not isinstance(career, Mapping):
            raise ValueError("Career completeness policy is required")
        checks = career.get("legacy_checks")
        if not isinstance(checks, tuple) or not checks:
            raise ValueError("Career legacy completeness checks are required")
        _number("legacy_check_weight", career.get("legacy_check_weight"), lower=0.0, upper=1.0)
        if float(career["legacy_check_weight"]) * len(checks) != 1.0:
            raise ValueError("Career legacy completeness weights must total 1.0")
        for name in ("required_capabilities", "optional_capabilities"):
            values = career.get(name)
            if not isinstance(values, tuple) or any(not isinstance(item, str) or not item for item in values):
                raise ValueError(f"Career {name} must be a tuple of capability names")
        compatibility = self.career_compatibility
        for name in ("baseline_rule_id", "baseline_category", "public_formula", "public_trace_id"):
            _nonempty(name, compatibility.get(name))
        _number("baseline_neutral", compatibility.get("baseline_neutral"), lower=0.0, upper=1.0)
        priority = compatibility.get("baseline_priority")
        if type(priority) is not int:
            raise ValueError("baseline_priority must be an integer")


_FIELDS = set(InferenceConfig.__dataclass_fields__)


def inference_config_from_data(value: Any) -> InferenceConfig:
    if not isinstance(value, Mapping) or set(value) != _FIELDS:
        raise ValueError("InferenceConfig has missing or unknown fields")
    return InferenceConfig(**value)


def load_inference_config(path: str | Path = DEFAULT_INFERENCE_CONFIG) -> InferenceConfig:
    supplied = Path(path)
    try:
        payload = supplied.read_text(encoding="utf-8")
        value = json.loads(
            payload,
            object_pairs_hook=_unique_object,
            parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("non-finite configuration number")),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("unable to load inference configuration") from exc
    return inference_config_from_data(value)


def inference_config_to_data(value: InferenceConfig) -> dict[str, Any]:
    if not isinstance(value, InferenceConfig):
        raise TypeError("value must be InferenceConfig")
    return canonical_json_data({name: getattr(value, name) for name in value.__dataclass_fields__})


def inference_config_logical_json_bytes(value: InferenceConfig) -> bytes:
    return canonical_json_bytes(inference_config_to_data(value))


def inference_config_logical_sha256(value: InferenceConfig) -> str:
    return hashlib.sha256(inference_config_logical_json_bytes(value)).hexdigest()


def _unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in items:
        if key in value:
            raise ValueError("duplicate inference configuration key")
        value[key] = item
    return value


__all__ = (
    "DEFAULT_INFERENCE_CONFIG", "InferenceConfig", "inference_config_from_data",
    "inference_config_logical_json_bytes", "inference_config_logical_sha256",
    "inference_config_to_data", "load_inference_config",
)
