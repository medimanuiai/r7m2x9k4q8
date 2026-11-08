"""Deterministic, local-only Prompt-06 rule-version selection and governance."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import InitVar, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from pathlib import Path
import re
from typing import Any
import unicodedata

import yaml

from systems.Parasara.engine.rules.canonical import (
    FrozenMapping,
    canonical_json_bytes,
    canonical_json_data,
    freeze_canonical,
)
from systems.Parasara.engine.rules.registry import (
    predicate_registry_fingerprint_sha256,
)


VERSIONING_SCHEMA_VERSION = "1.0.0"
EVALUATION_CONTRACT_VERSION = "1.0.0"
PREDICATE_LIBRARY_IDENTITY = "parashara-predicate-library"
PREDICATE_LIBRARY_VERSION = "1.0.0"
CONDITION_EVALUATOR_IDENTITY = "parashara-condition-evaluator"
CONDITION_EVALUATOR_VERSION = "1.0.0"
CONDITION_EVALUATOR_COMPATIBILITY_CONTRACT = "condition-result@1.0.0"
CONDITION_EVALUATOR_CONTENT_SHA256 = (
    "23392015e5a5d75be8f15ef9fd6aeb79073ab1a60b2c3bca4f5cd3fcc25b4068"
)
COMPATIBILITY_EVALUATION_INSTANT = "1970-01-01T00:00:00Z"
PARASARA_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RULE_SET_CATALOG = (
    PARASARA_ROOT / "config" / "versioning" / "parashara_rule_sets_v1.json"
)

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.@/-]{0,255}$")
_COMPATIBILITY_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.@/+\-]{0,255}$")
_RULE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.{}<>-]{0,127}$")
_UTC_INSTANT = re.compile(
    r"^(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})T"
    r"(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})Z$"
)
_RESOLUTION_TOKEN = object()
_EVALUATION_RECORD_TOKEN = object()
_TEST_RESOLVER_TOKEN = object()


class EngineMode(str, Enum):
    STRICT = "STRICT"
    EXPERIMENTAL = "EXPERIMENTAL"


class SelectionPurpose(str, Enum):
    NEW_EVALUATION = "NEW_EVALUATION"
    REPLAY = "REPLAY"
    ROLLBACK = "ROLLBACK"


class RulePackLifecycle(str, Enum):
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    VALIDATED = "VALIDATED"
    PRODUCTION = "PRODUCTION"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class VersioningErrorCode(str, Enum):
    UNKNOWN_RULE_SET_VERSION = "UNKNOWN_RULE_SET_VERSION"
    RULE_SET_UNAVAILABLE = "RULE_SET_UNAVAILABLE"
    MANIFEST_DIGEST_MISMATCH = "MANIFEST_DIGEST_MISMATCH"
    CONTENT_DIGEST_MISMATCH = "CONTENT_DIGEST_MISMATCH"
    INCOMPATIBLE_COMPONENT_VERSION = "INCOMPATIBLE_COMPONENT_VERSION"
    LIFECYCLE_SELECTION_FORBIDDEN = "LIFECYCLE_SELECTION_FORBIDDEN"
    EVALUATION_INSTANT_MISMATCH = "EVALUATION_INSTANT_MISMATCH"
    HISTORICAL_CONTENT_UNAVAILABLE = "HISTORICAL_CONTENT_UNAVAILABLE"
    INCOMPATIBLE_REPLAY_ENVIRONMENT = "INCOMPATIBLE_REPLAY_ENVIRONMENT"
    AUTHORITY_MISMATCH = "AUTHORITY_MISMATCH"
    RULE_NOT_IN_MANIFEST = "RULE_NOT_IN_MANIFEST"
    RULE_CONTENT_MISMATCH = "RULE_CONTENT_MISMATCH"
    INVALID_VERSIONING_DATA = "INVALID_VERSIONING_DATA"


class VersioningError(ValueError):
    """Typed deterministic selection/binding failure."""

    def __init__(
        self,
        code: VersioningErrorCode,
        message: str,
        *,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        if not isinstance(code, VersioningErrorCode):
            raise TypeError("code must be VersioningErrorCode")
        if not isinstance(message, str) or not message:
            raise ValueError("message must be nonempty")
        self.code = code
        self.details = FrozenMapping({} if details is None else details)
        super().__init__(f"{code.value}: {message}")


def _fail(
    code: VersioningErrorCode,
    message: str,
    **details: Any,
) -> VersioningError:
    return VersioningError(code, message, details=details)


def _text(name: str, value: Any, *, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{name} must be a canonical nonempty string")
    normalized = unicodedata.normalize("NFC", value)
    if normalized != value:
        raise ValueError(f"{name} must use Unicode NFC")
    if pattern is not None and not pattern.fullmatch(value):
        raise ValueError(f"{name} has invalid syntax")
    return value


def _sha(name: str, value: Any) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


def _optional_sha(name: str, value: Any) -> str | None:
    if value is None:
        return None
    return _sha(name, value)


def _evaluation_instant(value: Any) -> str:
    value = _text("evaluation_instant", value)
    if not _UTC_INSTANT.fullmatch(value):
        raise _fail(
            VersioningErrorCode.INVALID_VERSIONING_DATA,
            "evaluation_instant must be normalized UTC ISO-8601 (YYYY-MM-DDTHH:MM:SSZ).",
        )
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError as exc:
        raise _fail(
            VersioningErrorCode.INVALID_VERSIONING_DATA,
            "evaluation_instant is not a valid UTC calendar instant.",
        ) from exc
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise _fail(
            VersioningErrorCode.INVALID_VERSIONING_DATA,
            "evaluation_instant is not canonically normalized.",
        )
    return value


def _frozen_mapping(name: str, value: Any) -> FrozenMapping:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    frozen = freeze_canonical(value, path=f"$.{name}")
    if not isinstance(frozen, FrozenMapping):
        raise TypeError(f"{name} must be a mapping")
    return frozen


def _unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in items:
        if key in output:
            raise ValueError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def _read_json(path: Path, *, unavailable_code: VersioningErrorCode) -> Any:
    try:
        payload = path.read_text(encoding="utf-8")
        return json.loads(
            payload,
            object_pairs_hook=_unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON value: {value}")
            ),
        )
    except FileNotFoundError as exc:
        raise _fail(unavailable_code, "Required versioned content is unavailable.", path=path.as_posix()) from exc
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise _fail(
            VersioningErrorCode.INVALID_VERSIONING_DATA,
            "Versioning JSON could not be loaded canonically.",
            path=path.as_posix(),
        ) from exc


def _file_sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except FileNotFoundError as exc:
        raise _fail(
            VersioningErrorCode.HISTORICAL_CONTENT_UNAVAILABLE,
            "Required historical content is unavailable.",
            path=path.as_posix(),
        ) from exc
    except OSError as exc:
        raise _fail(
            VersioningErrorCode.RULE_SET_UNAVAILABLE,
            "Required versioned content cannot be read.",
            path=path.as_posix(),
        ) from exc


def _resolve_repository_path(repository_root: Path, relative_path: str) -> Path:
    _text("artifact path", relative_path)
    if "\\" in relative_path:
        raise ValueError("artifact paths must use repository-relative POSIX spelling")
    supplied = Path(relative_path)
    if supplied.is_absolute() or ".." in supplied.parts:
        raise ValueError("artifact path must stay below the repository root")
    root = repository_root.resolve()
    resolved = (root / supplied).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("artifact path escapes repository root") from exc
    return resolved


@dataclass(frozen=True, slots=True, kw_only=True)
class EngineConfig:
    config_schema_version: str
    system: str
    engine_version: str
    rule_set_family: str
    rule_set_version: str
    mode: EngineMode
    purpose: SelectionPurpose
    evaluation_instant: str
    output_schema_version: str
    compatibility_profile: str

    def __post_init__(self) -> None:
        for name in (
            "config_schema_version",
            "system",
            "engine_version",
            "rule_set_family",
            "rule_set_version",
            "output_schema_version",
            "compatibility_profile",
        ):
            _text(name, getattr(self, name), pattern=_IDENTITY)
        _evaluation_instant(self.evaluation_instant)
        if self.config_schema_version != VERSIONING_SCHEMA_VERSION:
            raise ValueError("unsupported EngineConfig schema version")
        if self.rule_set_version.casefold() == "latest":
            raise ValueError("latest is not a valid evaluation version")
        if not isinstance(self.mode, EngineMode):
            raise TypeError("mode must be EngineMode")
        if not isinstance(self.purpose, SelectionPurpose):
            raise TypeError("purpose must be SelectionPurpose")


def compatibility_v1_config(
    evaluation_instant: str = COMPATIBILITY_EVALUATION_INSTANT,
) -> EngineConfig:
    """Return the literal legacy-compatible selection; never inspect a catalog."""

    return EngineConfig(
        config_schema_version=VERSIONING_SCHEMA_VERSION,
        system="parashara",
        engine_version="0.1.0",
        rule_set_family="parashara",
        rule_set_version="v1",
        mode=EngineMode.EXPERIMENTAL,
        purpose=SelectionPurpose.NEW_EVALUATION,
        evaluation_instant=evaluation_instant,
        output_schema_version="1.0.0",
        compatibility_profile="parasara_snapshot_v1",
    )


def evaluation_instant_from_snapshot(snapshot: Any) -> str:
    context = getattr(snapshot, "evaluation_context", None)
    if isinstance(context, Mapping):
        instant = context.get("instant")
        if isinstance(instant, str) and instant:
            return instant
    return COMPATIBILITY_EVALUATION_INSTANT


@dataclass(frozen=True, slots=True, kw_only=True)
class ComponentIdentity:
    identity: str
    version: str
    compatibility_contract: str
    content_sha256: str | None = None
    artifact_path: str | None = None
    logical_sha256: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("identity", "version", "compatibility_contract"):
            _text(
                name,
                getattr(self, name),
                pattern=_COMPATIBILITY_IDENTITY if name == "compatibility_contract" else _IDENTITY,
            )
        _optional_sha("content_sha256", self.content_sha256)
        _optional_sha("logical_sha256", self.logical_sha256)
        if self.artifact_path is not None:
            _text("artifact_path", self.artifact_path)
        object.__setattr__(self, "metadata", _frozen_mapping("metadata", self.metadata))


@dataclass(frozen=True, slots=True, kw_only=True)
class KnowledgeDataIdentity:
    identity: str
    version: str
    content_sha256: str
    compatibility_contract: str
    artifacts: tuple[Mapping[str, Any], ...]

    def __post_init__(self) -> None:
        for name in ("identity", "version", "compatibility_contract"):
            _text(name, getattr(self, name), pattern=_IDENTITY)
        _sha("content_sha256", self.content_sha256)
        frozen = freeze_canonical(self.artifacts, path="$.artifacts")
        if not isinstance(frozen, tuple) or any(not isinstance(item, FrozenMapping) for item in frozen):
            raise TypeError("artifacts must be an immutable mapping tuple")
        object.__setattr__(self, "artifacts", frozen)


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleRevisionIdentity:
    rule_id: str
    revision: str
    semantic_content_sha256: str
    source_artifact_id: str
    source_artifact_semantic_sha256: str
    source_order: int
    materialization_contract_id: str | None
    materialization_bindings: Mapping[str, Any] | None
    execution_projections: tuple[str, ...]
    semantic_contract: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text("rule_id", self.rule_id, pattern=_RULE_ID)
        _text("revision", self.revision)
        _sha("semantic_content_sha256", self.semantic_content_sha256)
        _text("source_artifact_id", self.source_artifact_id, pattern=_IDENTITY)
        _sha("source_artifact_semantic_sha256", self.source_artifact_semantic_sha256)
        if type(self.source_order) is not int or self.source_order < 0:
            raise ValueError("source_order must be a nonnegative integer")
        if self.materialization_contract_id is not None:
            _text("materialization_contract_id", self.materialization_contract_id, pattern=_IDENTITY)
        if self.materialization_bindings is not None:
            object.__setattr__(
                self,
                "materialization_bindings",
                _frozen_mapping("materialization_bindings", self.materialization_bindings),
            )
        if not isinstance(self.execution_projections, tuple) or any(
            not isinstance(item, str) or not item for item in self.execution_projections
        ):
            raise TypeError("execution_projections must be a nonempty string tuple")
        if tuple(dict.fromkeys(self.execution_projections)) != self.execution_projections:
            raise ValueError("execution_projections must be unique and ordered")
        object.__setattr__(
            self, "semantic_contract", _frozen_mapping("semantic_contract", self.semantic_contract)
        )
        expected = hashlib.sha256(canonical_json_bytes(self.semantic_contract)).hexdigest()
        if expected != self.semantic_content_sha256:
            raise ValueError("rule semantic_content_sha256 does not match semantic_contract")


def _component_to_data(value: ComponentIdentity) -> dict[str, Any]:
    output: dict[str, Any] = {
        "identity": value.identity,
        "version": value.version,
        "compatibility_contract": value.compatibility_contract,
    }
    if value.content_sha256 is not None:
        output["content_sha256"] = value.content_sha256
    if value.artifact_path is not None:
        output["artifact_path"] = value.artifact_path
    if value.logical_sha256 is not None:
        output["logical_sha256"] = value.logical_sha256
    if value.metadata:
        output["metadata"] = canonical_json_data(value.metadata)
    return output


def _rule_to_data(value: RuleRevisionIdentity) -> dict[str, Any]:
    return {
        "rule_id": value.rule_id,
        "revision": value.revision,
        "semantic_content_sha256": value.semantic_content_sha256,
        "source_artifact_id": value.source_artifact_id,
        "source_artifact_semantic_sha256": value.source_artifact_semantic_sha256,
        "source_order": value.source_order,
        "materialization_contract_id": value.materialization_contract_id,
        "materialization_bindings": (
            None
            if value.materialization_bindings is None
            else canonical_json_data(value.materialization_bindings)
        ),
        "execution_projections": list(value.execution_projections),
        "semantic_contract": canonical_json_data(value.semantic_contract),
    }


@dataclass(frozen=True, slots=True, kw_only=True)
class EvaluationVersionManifest:
    manifest_schema_version: str
    system: str
    engine: ComponentIdentity
    rule_set_family: str
    rule_set_version: str
    ordered_rule_revisions: tuple[RuleRevisionIdentity, ...]
    ordered_source_artifacts: tuple[Mapping[str, Any], ...]
    predicate_library: ComponentIdentity
    condition_evaluator: ComponentIdentity
    inference: ComponentIdentity
    knowledge_data: tuple[KnowledgeDataIdentity, ...]
    output_schema_version: str
    compatibility_profile: str
    dsl: ComponentIdentity | None
    dependency_graph: ComponentIdentity | None
    manifest_fingerprint_sha256: str

    def __post_init__(self) -> None:
        if self.manifest_schema_version != VERSIONING_SCHEMA_VERSION:
            raise ValueError("unsupported manifest schema version")
        for name in ("system", "rule_set_family", "rule_set_version", "output_schema_version", "compatibility_profile"):
            _text(name, getattr(self, name), pattern=_IDENTITY)
        if not isinstance(self.engine, ComponentIdentity):
            raise TypeError("engine must be ComponentIdentity")
        if not isinstance(self.predicate_library, ComponentIdentity):
            raise TypeError("predicate_library must be ComponentIdentity")
        if not isinstance(self.condition_evaluator, ComponentIdentity):
            raise TypeError("condition_evaluator must be ComponentIdentity")
        if not isinstance(self.inference, ComponentIdentity):
            raise TypeError("inference must be ComponentIdentity")
        if not isinstance(self.ordered_rule_revisions, tuple) or any(
            not isinstance(item, RuleRevisionIdentity) for item in self.ordered_rule_revisions
        ):
            raise TypeError("ordered_rule_revisions must contain RuleRevisionIdentity")
        if len({(item.rule_id, item.revision) for item in self.ordered_rule_revisions}) != len(self.ordered_rule_revisions):
            raise ValueError("rule identities/revisions must be unique")
        if tuple(item.source_order for item in self.ordered_rule_revisions) != tuple(
            sorted(item.source_order for item in self.ordered_rule_revisions)
        ):
            raise ValueError("rule identities must use canonical source order")
        artifacts = freeze_canonical(self.ordered_source_artifacts, path="$.ordered_source_artifacts")
        if not isinstance(artifacts, tuple) or any(not isinstance(item, FrozenMapping) for item in artifacts):
            raise TypeError("ordered_source_artifacts must contain mappings")
        object.__setattr__(self, "ordered_source_artifacts", artifacts)
        if not isinstance(self.knowledge_data, tuple) or any(
            not isinstance(item, KnowledgeDataIdentity) for item in self.knowledge_data
        ):
            raise TypeError("knowledge_data must contain KnowledgeDataIdentity")
        if self.dsl is not None and not isinstance(self.dsl, ComponentIdentity):
            raise TypeError("dsl must be ComponentIdentity or None")
        if self.dependency_graph is not None:
            _validate_graph_component(self)
        dsl_artifacts = tuple(item for item in artifacts if item.get("format") == "rule-dsl-yaml")
        if self.dsl is None and dsl_artifacts:
            raise ValueError("DSL source artifacts require a pinned DSL component")
        if self.dsl is not None:
            from systems.Parasara.engine.rules.dsl.models import MAX_DSL_SOURCE_ARTIFACTS

            if len(dsl_artifacts) != MAX_DSL_SOURCE_ARTIFACTS:
                raise ValueError("a DSL manifest requires exactly one rule-dsl-yaml source artifact")
        _sha("manifest_fingerprint_sha256", self.manifest_fingerprint_sha256)
        expected = manifest_fingerprint_sha256(self)
        if expected != self.manifest_fingerprint_sha256:
            raise ValueError("manifest fingerprint does not match canonical content")

    def rule_identity_for(self, value: Any) -> RuleRevisionIdentity:
        rule_id = getattr(value, "rule_id", None)
        revision = getattr(value, "rule_version", None)
        for identity in self.ordered_rule_revisions:
            bindings = _materialization_bindings(identity, rule_id)
            if bindings is None or revision != identity.revision:
                continue
            _verify_rule_projection(identity, value)
            if identity.materialization_contract_id is None:
                return identity
            concrete_contract = {
                "bindings": bindings,
                "rule_id": rule_id,
                "template_semantic_content_sha256": identity.semantic_content_sha256,
            }
            return RuleRevisionIdentity(
                rule_id=rule_id,
                revision=identity.revision,
                semantic_content_sha256=hashlib.sha256(
                    canonical_json_bytes(concrete_contract)
                ).hexdigest(),
                source_artifact_id=identity.source_artifact_id,
                source_artifact_semantic_sha256=identity.source_artifact_semantic_sha256,
                source_order=identity.source_order,
                materialization_contract_id=identity.materialization_contract_id,
                materialization_bindings=bindings,
                execution_projections=identity.execution_projections,
                semantic_contract=concrete_contract,
            )
        raise _fail(
            VersioningErrorCode.RULE_NOT_IN_MANIFEST,
            "Rule identity/revision is not authorized by the selected manifest.",
            rule_id=rule_id,
            rule_version=revision,
            rule_set_version=self.rule_set_version,
        )


def manifest_to_data(value: EvaluationVersionManifest, *, include_fingerprint: bool = True) -> dict[str, Any]:
    if not isinstance(value, EvaluationVersionManifest):
        raise TypeError("value must be EvaluationVersionManifest")
    output = {
        "manifest_schema_version": value.manifest_schema_version,
        "system": value.system,
        "engine": _component_to_data(value.engine),
        "rule_set": {
            "family": value.rule_set_family,
            "version": value.rule_set_version,
            "ordered_rule_revisions": [_rule_to_data(item) for item in value.ordered_rule_revisions],
            "ordered_source_artifacts": [canonical_json_data(item) for item in value.ordered_source_artifacts],
        },
        "predicate_library": _component_to_data(value.predicate_library),
        "condition_evaluator": _component_to_data(value.condition_evaluator),
        "inference": _component_to_data(value.inference),
        "knowledge_data": [
            {
                "identity": item.identity,
                "version": item.version,
                "content_sha256": item.content_sha256,
                "compatibility_contract": item.compatibility_contract,
                "artifacts": [canonical_json_data(artifact) for artifact in item.artifacts],
            }
            for item in value.knowledge_data
        ],
        "output": {
            "schema_version": value.output_schema_version,
            "compatibility_profile": value.compatibility_profile,
        },
        "future_components": {
            "dsl": None if value.dsl is None else _component_to_data(value.dsl),
            "dependency_graph": None if value.dependency_graph is None else _component_to_data(value.dependency_graph),
        },
    }
    if include_fingerprint:
        output["manifest_fingerprint_sha256"] = value.manifest_fingerprint_sha256
    return output


def manifest_canonical_json_bytes(value: EvaluationVersionManifest) -> bytes:
    return canonical_json_bytes(manifest_to_data(value, include_fingerprint=True))


def manifest_fingerprint_sha256(value: EvaluationVersionManifest) -> str:
    return hashlib.sha256(
        canonical_json_bytes(manifest_to_data(value, include_fingerprint=False))
    ).hexdigest()


def _component_from_data(value: Any) -> ComponentIdentity:
    if not isinstance(value, Mapping):
        raise TypeError("component must be a mapping")
    allowed = {
        "identity", "version", "compatibility_contract", "content_sha256",
        "artifact_path", "logical_sha256", "metadata",
    }
    if not {"identity", "version", "compatibility_contract"}.issubset(value) or set(value) - allowed:
        raise ValueError("component has missing or unknown fields")
    return ComponentIdentity(
        identity=value["identity"],
        version=value["version"],
        compatibility_contract=value["compatibility_contract"],
        content_sha256=value.get("content_sha256"),
        artifact_path=value.get("artifact_path"),
        logical_sha256=value.get("logical_sha256"),
        metadata=value.get("metadata", {}),
    )


def _rule_from_data(value: Any) -> RuleRevisionIdentity:
    fields = {
        "rule_id", "revision", "semantic_content_sha256", "source_artifact_id",
        "source_artifact_semantic_sha256", "source_order", "materialization_contract_id",
        "materialization_bindings", "execution_projections", "semantic_contract",
    }
    if not isinstance(value, Mapping) or set(value) != fields:
        raise ValueError("rule identity has missing or unknown fields")
    projections = value["execution_projections"]
    if not isinstance(projections, Sequence) or isinstance(projections, (str, bytes)):
        raise TypeError("execution_projections must be a sequence")
    return RuleRevisionIdentity(
        rule_id=value["rule_id"],
        revision=value["revision"],
        semantic_content_sha256=value["semantic_content_sha256"],
        source_artifact_id=value["source_artifact_id"],
        source_artifact_semantic_sha256=value["source_artifact_semantic_sha256"],
        source_order=value["source_order"],
        materialization_contract_id=value["materialization_contract_id"],
        materialization_bindings=value["materialization_bindings"],
        execution_projections=tuple(projections),
        semantic_contract=value["semantic_contract"],
    )


def manifest_from_data(value: Any) -> EvaluationVersionManifest:
    fields = {
        "manifest_schema_version", "system", "engine", "rule_set", "predicate_library",
        "condition_evaluator", "inference", "knowledge_data", "output",
        "future_components", "manifest_fingerprint_sha256",
    }
    if not isinstance(value, Mapping) or set(value) != fields:
        raise ValueError("manifest has missing or unknown fields")
    rule_set = value["rule_set"]
    output = value["output"]
    future = value["future_components"]
    if not isinstance(rule_set, Mapping) or set(rule_set) != {
        "family", "version", "ordered_rule_revisions", "ordered_source_artifacts"
    }:
        raise ValueError("rule_set section has missing or unknown fields")
    if not isinstance(output, Mapping) or set(output) != {"schema_version", "compatibility_profile"}:
        raise ValueError("output section has missing or unknown fields")
    if not isinstance(future, Mapping) or set(future) != {"dsl", "dependency_graph"}:
        raise ValueError("future_components section has missing or unknown fields")
    graph = None if future["dependency_graph"] is None else _component_from_data(future["dependency_graph"])
    dsl = None if future["dsl"] is None else _component_from_data(future["dsl"])
    knowledge = value["knowledge_data"]
    if not isinstance(knowledge, Sequence) or isinstance(knowledge, (str, bytes)):
        raise TypeError("knowledge_data must be a sequence")
    knowledge_values = []
    for item in knowledge:
        if not isinstance(item, Mapping) or set(item) != {
            "identity", "version", "content_sha256", "compatibility_contract", "artifacts"
        }:
            raise ValueError("knowledge-data identity has missing or unknown fields")
        knowledge_values.append(KnowledgeDataIdentity(**item))
    rules = rule_set["ordered_rule_revisions"]
    artifacts = rule_set["ordered_source_artifacts"]
    if not isinstance(rules, Sequence) or isinstance(rules, (str, bytes)):
        raise TypeError("ordered_rule_revisions must be a sequence")
    if not isinstance(artifacts, Sequence) or isinstance(artifacts, (str, bytes)):
        raise TypeError("ordered_source_artifacts must be a sequence")
    return EvaluationVersionManifest(
        manifest_schema_version=value["manifest_schema_version"],
        system=value["system"],
        engine=_component_from_data(value["engine"]),
        rule_set_family=rule_set["family"],
        rule_set_version=rule_set["version"],
        ordered_rule_revisions=tuple(_rule_from_data(item) for item in rules),
        ordered_source_artifacts=tuple(artifacts),
        predicate_library=_component_from_data(value["predicate_library"]),
        condition_evaluator=_component_from_data(value["condition_evaluator"]),
        inference=_component_from_data(value["inference"]),
        knowledge_data=tuple(knowledge_values),
        output_schema_version=output["schema_version"],
        compatibility_profile=output["compatibility_profile"],
        dsl=dsl,
        dependency_graph=graph,
        manifest_fingerprint_sha256=value["manifest_fingerprint_sha256"],
    )


def _materialization_bindings(identity: RuleRevisionIdentity, rule_id: Any) -> dict[str, str] | None:
    if not isinstance(rule_id, str):
        return None
    if identity.materialization_contract_id is None:
        return {} if rule_id == identity.rule_id else None
    bindings = identity.materialization_bindings
    if bindings is None or len(bindings) != 1:
        return None
    name = next(iter(bindings))
    marker = "{" + name + "}"
    if marker not in identity.rule_id:
        return None
    prefix, suffix = identity.rule_id.split(marker, 1)
    if not rule_id.startswith(prefix) or not rule_id.endswith(suffix):
        return None
    end = len(rule_id) - len(suffix) if suffix else len(rule_id)
    concrete = rule_id[len(prefix):end]
    allowed = bindings[name]
    if concrete not in allowed:
        return None
    return {name: concrete}


def _verify_rule_projection(identity: RuleRevisionIdentity, value: Any) -> None:
    contract = identity.semantic_contract
    projections = contract.get("projections")
    if not isinstance(projections, tuple):
        raise _fail(VersioningErrorCode.RULE_CONTENT_MISMATCH, "Rule semantic contract has no projections.")
    actual = {
        "rule_family": getattr(value, "rule_family", None),
        "category": getattr(value, "category", None),
        "domains": list(getattr(value, "domains", ())),
        "base_weight": getattr(value, "base_weight", None),
        "priority": getattr(value, "priority", None),
        "context": getattr(value, "context", None),
    }
    def matches(item: Any) -> bool:
        expected = canonical_json_data(item)
        observed = dict(actual)
        if expected.get("base_weight") == "runtime_derived":
            expected = dict(expected)
            expected.pop("base_weight")
            observed.pop("base_weight")
        return expected == observed

    if not any(matches(item) for item in projections):
        raise _fail(
            VersioningErrorCode.RULE_CONTENT_MISMATCH,
            "Rule semantics do not match the selected manifest.",
            rule_id=getattr(value, "rule_id", None),
            rule_version=getattr(value, "rule_version", None),
        )


def _semantic_yaml_artifact(path: Path, record_ids: Sequence[str] | None) -> str:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise _fail(
            VersioningErrorCode.HISTORICAL_CONTENT_UNAVAILABLE,
            "Required historical rule source is unavailable.",
            path=path.as_posix(),
        ) from exc
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise _fail(
            VersioningErrorCode.INVALID_VERSIONING_DATA,
            "Rule source could not be parsed.",
            path=path.as_posix(),
        ) from exc
    selected = value
    if record_ids is not None:
        if not isinstance(value, list):
            raise _fail(VersioningErrorCode.INVALID_VERSIONING_DATA, "Selected rule source must contain a list.")
        by_id = {item.get("id"): item for item in value if isinstance(item, Mapping)}
        try:
            selected = [by_id[rule_id] for rule_id in record_ids]
        except KeyError as exc:
            raise _fail(
                VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                "A manifest-selected rule source row is missing.",
                rule_id=str(exc.args[0]),
                path=path.as_posix(),
            ) from exc
    return hashlib.sha256(canonical_json_bytes(selected)).hexdigest()


def _semantic_data_artifact(path: Path) -> Any:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        try:
            return _canonicalize_yaml_data(yaml.safe_load(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise _fail(VersioningErrorCode.RULE_SET_UNAVAILABLE, "Knowledge data cannot be loaded.", path=path.as_posix()) from exc
    return _read_json(path, unavailable_code=VersioningErrorCode.HISTORICAL_CONTENT_UNAVAILABLE)


def _canonicalize_yaml_data(value: Any) -> Any:
    """Normalize YAML scalar keys into the repository's JSON-safe content form."""

    if isinstance(value, Mapping):
        output: dict[str, Any] = {}
        for key, item in value.items():
            normalized = key if isinstance(key, str) else str(key)
            if normalized in output:
                raise _fail(
                    VersioningErrorCode.INVALID_VERSIONING_DATA,
                    "YAML keys collide after canonical string normalization.",
                )
            output[normalized] = _canonicalize_yaml_data(item)
        return output
    if isinstance(value, list):
        return [_canonicalize_yaml_data(item) for item in value]
    return value


def _knowledge_bundle_sha256(repository_root: Path, artifacts: Sequence[Mapping[str, Any]]) -> str:
    rows = []
    for artifact in artifacts:
        if not isinstance(artifact, Mapping) or set(artifact) != {"path", "content_sha256"}:
            raise ValueError("knowledge artifact has missing or unknown fields")
        path = _resolve_repository_path(repository_root, artifact["path"])
        logical = _semantic_data_artifact(path)
        digest = hashlib.sha256(canonical_json_bytes(logical)).hexdigest()
        if digest != artifact["content_sha256"]:
            raise _fail(
                VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                "Knowledge-data content does not match the manifest.",
                path=artifact["path"],
            )
        rows.append({"path": artifact["path"], "content_sha256": digest})
    return hashlib.sha256(canonical_json_bytes(rows)).hexdigest()


def _graph_error(issue: Any) -> VersioningError:
    """Keep graph diagnostics inside the existing versioning error contract."""
    code = issue.code
    mapping = {
        "P08E301_UNAUTHORIZED_SOURCE": VersioningErrorCode.AUTHORITY_MISMATCH,
        "P08E302_AUTHORITY_MISMATCH": VersioningErrorCode.AUTHORITY_MISMATCH,
        "P08E307_DIRECT_EXECUTION_BYPASS": VersioningErrorCode.AUTHORITY_MISMATCH,
        "P08E303_COMPONENT_MISMATCH": VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION,
        "P08E304_DECLARATION_DIGEST_MISMATCH": VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
        "P08E305_GRAPH_DIGEST_MISMATCH": VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
        "P08E306_PLAN_DIGEST_MISMATCH": VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
    }
    return VersioningError(mapping.get(code, VersioningErrorCode.INVALID_VERSIONING_DATA),
        issue.message, details={"graph_code": code, "graph_diagnostic": issue.to_logical_data()})


def _validate_graph_component(manifest: EvaluationVersionManifest) -> None:
    from systems.Parasara.engine.rules.graph import GRAPH_COMPILER_CONTENT_SHA256, GRAPH_CONTRACT_DATA, GRAPH_CONTRACT_SHA256
    from systems.Parasara.engine.rules.graph.models import diagnostic
    from systems.Parasara.engine.rules.graph.parser import valid_source_id
    component = manifest.dependency_graph
    valid = (isinstance(component, ComponentIdentity) and manifest.dsl is not None
        and (manifest.system, manifest.rule_set_family, manifest.rule_set_version) != ("parashara", "parashara", "v1"))
    if valid:
        valid = ((component.identity, component.version, component.compatibility_contract, component.content_sha256)
            == (GRAPH_CONTRACT_DATA["identity"], GRAPH_CONTRACT_DATA["version"],
                GRAPH_CONTRACT_DATA["compatibility_contract"], GRAPH_COMPILER_CONTENT_SHA256)
            and valid_source_id(component.artifact_path)
            and isinstance(component.logical_sha256, str) and _SHA256.fullmatch(component.logical_sha256)
            and set(component.metadata) == {"graph_schema_version", "graph_contract_sha256", "declarations_sha256", "plan_sha256"}
            and component.metadata["graph_schema_version"] == GRAPH_CONTRACT_DATA["contracts"]["schema"]
            and component.metadata["graph_contract_sha256"] == GRAPH_CONTRACT_SHA256
            and all(isinstance(component.metadata[k], str) and _SHA256.fullmatch(component.metadata[k])
                    for k in ("declarations_sha256", "plan_sha256"))
            and len(manifest.ordered_source_artifacts) == 1
            and manifest.ordered_source_artifacts[0].get("format") == "rule-dsl-yaml")
    if not valid:
        raise _graph_error(diagnostic("P08E303_COMPONENT_MISMATCH"))


def _load_graph_source(manifest: EvaluationVersionManifest, repository_root: Path) -> bytes:
    from systems.Parasara.engine.rules.graph.runtime_contract import LIMITS
    from systems.Parasara.engine.rules.graph.models import diagnostic
    _validate_graph_component(manifest)
    try:
        path = _resolve_repository_path(repository_root, manifest.dependency_graph.artifact_path)
    except (ValueError, OSError) as exc:
        raise _graph_error(diagnostic("P08E301_UNAUTHORIZED_SOURCE")) from exc
    try:
        with path.open("rb") as stream:
            payload = stream.read(LIMITS["source_bytes"] + 1)
    except OSError as exc:
        issue = diagnostic("P08E301_UNAUTHORIZED_SOURCE", stage="source",
            source_id=manifest.dependency_graph.artifact_path)
        raise _fail(VersioningErrorCode.HISTORICAL_CONTENT_UNAVAILABLE,
            "Required historical graph source is unavailable.", graph_code=issue.code,
            graph_diagnostic=issue.to_logical_data()) from exc
    if len(payload) > LIMITS["source_bytes"]:
        raise _graph_error(diagnostic("P08E401_LIMIT_VIOLATION", details=dict(
            resource="source_bytes", limit=LIMITS["source_bytes"], observed=len(payload))))
    return payload


def _authorize_graph_analysis(manifest: EvaluationVersionManifest, analysis: Any) -> None:
    from systems.Parasara.engine.rules.graph.models import GraphAnalysis, diagnostic
    _validate_graph_component(manifest)
    component = manifest.dependency_graph
    if not isinstance(analysis, GraphAnalysis) or analysis.source_id != component.artifact_path:
        raise _graph_error(diagnostic("P08E301_UNAUTHORIZED_SOURCE"))
    artifact = manifest.ordered_source_artifacts[0]
    if (analysis.dsl_compiled_rule_set_sha256 != artifact["compiled_rule_set_sha256"]
        or len(analysis.nodes) != len(manifest.ordered_rule_revisions)):
        raise _graph_error(diagnostic("P08E107_MEMBERSHIP_MISMATCH"))
    for index, (node, rule) in enumerate(zip(analysis.nodes, manifest.ordered_rule_revisions)):
        if ((node.system, node.rule_set_family, node.rule_set_version, node.rule_id, node.revision,
             node.dsl_compiled_semantic_sha256, node.source_artifact_id, node.source_identity,
             node.source_artifact_semantic_sha256, node.source_order)
            != (manifest.system, manifest.rule_set_family, manifest.rule_set_version, rule.rule_id, rule.revision,
                rule.semantic_content_sha256, rule.source_artifact_id, artifact["path"],
                rule.source_artifact_semantic_sha256, index)
            or rule.source_order != index or rule.materialization_contract_id is not None):
            raise _graph_error(diagnostic("P08E107_MEMBERSHIP_MISMATCH"))
    for observed, expected, code in (
        (analysis.declarations_sha256, component.metadata["declarations_sha256"], "P08E304_DECLARATION_DIGEST_MISMATCH"),
        (analysis.graph_sha256, component.logical_sha256, "P08E305_GRAPH_DIGEST_MISMATCH"),
        (analysis.plan_sha256, component.metadata["plan_sha256"], "P08E306_PLAN_DIGEST_MISMATCH"),
    ):
        if observed != expected:
            raise _graph_error(diagnostic(code, details=dict(expected=expected, observed=observed)))


def _verify_manifest_artifacts(manifest: EvaluationVersionManifest, repository_root: Path) -> None:
    # Finite opt-in dispatch. Mixed profiles fail before source or graph compilation.
    v2 = any(component is not None and component.version == "2.0.0"
             for component in (manifest.predicate_library, manifest.condition_evaluator, manifest.dsl))
    if v2:
        from systems.Parasara.engine.rules.aspect_contract_v2 import (
            registry_fingerprint, CONDITION_COMPATIBILITY_CONTRACT,
        )
        from systems.Parasara.engine.rules.evaluator_v2 import CONDITION_CONTENT_SHA256
        from systems.Parasara.engine.rules.dsl.compiler_v2 import (
            RuleDslCompilerV2, DSL_COMPILER_CONTENT_SHA256 as V2_COMPILER_SHA256,
        )
        expected_v2 = (
            (PREDICATE_LIBRARY_IDENTITY, "2.0.0", "predicate-result@1.0.0", registry_fingerprint()),
            (CONDITION_EVALUATOR_IDENTITY, "2.0.0", CONDITION_COMPATIBILITY_CONTRACT, CONDITION_CONTENT_SHA256),
            ("parashara-rule-dsl-compiler", "2.0.0", "resolved-rule+condition@1.0.0", V2_COMPILER_SHA256),
        )
        observed_v2 = tuple(None if c is None else (c.identity, c.version, c.compatibility_contract, c.content_sha256)
                            for c in (manifest.predicate_library, manifest.condition_evaluator, manifest.dsl))
        if manifest.dependency_graph is not None or observed_v2 != expected_v2:
            raise _fail(VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION,
                        "V2 requires exact source-scoped components and excludes dependency graphs.")
    source_by_id: dict[str, str] = {}
    for artifact in manifest.ordered_source_artifacts:
        legacy_fields = {"artifact_id", "path", "format", "record_ids", "semantic_content_sha256"}
        dsl_fields = legacy_fields | {"expanded_ast_sha256", "compiled_rule_set_sha256"}
        expected_fields = dsl_fields if artifact.get("format") == "rule-dsl-yaml" else legacy_fields
        if set(artifact) != expected_fields or artifact["format"] not in {"yaml", "engine-contract", "rule-dsl-yaml"}:
            raise _fail(VersioningErrorCode.INVALID_VERSIONING_DATA, "Rule source artifact is invalid.")
        path = _resolve_repository_path(repository_root, artifact["path"])
        record_ids = artifact["record_ids"]
        if artifact["format"] == "yaml":
            digest = _semantic_yaml_artifact(path, record_ids)
        elif artifact["format"] == "rule-dsl-yaml":
            if manifest.dsl is None:
                raise _fail(VersioningErrorCode.INVALID_VERSIONING_DATA, "DSL source has no compiler component.")
            try:
                from systems.Parasara.engine.rules.dsl import (
                    AnalysisSucceeded,
                    MAX_SOURCE_BYTES,
                    RuleDslCompiler,
                )
                if path.stat().st_size > MAX_SOURCE_BYTES:
                    raise ValueError("DSL source exceeds its bounded source size")
                payload = path.read_bytes()
            except (OSError, UnicodeError, ValueError) as exc:
                raise _fail(
                    VersioningErrorCode.HISTORICAL_CONTENT_UNAVAILABLE,
                    "Required historical DSL source is unavailable.",
                    path=artifact["path"],
                ) from exc
            compiler = RuleDslCompilerV2 if v2 else RuleDslCompiler
            analysis = compiler.analyze_source(source_id=artifact["path"], payload=payload)
            if not isinstance(analysis, AnalysisSucceeded):
                raise _fail(
                    VersioningErrorCode.INVALID_VERSIONING_DATA,
                    "DSL source does not satisfy the selected compiler contract.",
                    path=artifact["path"],
                )
            analyzed = analysis.analyzed_rule_set
            digest = analyzed.canonical_dsl_sha256
            if (
                artifact["expanded_ast_sha256"] != analyzed.expanded_ast_sha256
                or artifact["compiled_rule_set_sha256"] != analyzed.compiled_rule_set_sha256
                or tuple(record_ids) != tuple(item.resolved_rule.rule_id for item in analyzed.rules)
            ):
                raise _fail(
                    VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                    "DSL expanded or compiled identity does not match the manifest.",
                    path=artifact["path"],
                )
        else:
            if not path.is_file() or not isinstance(record_ids, tuple) or len(record_ids) != 1:
                raise _fail(VersioningErrorCode.INVALID_VERSIONING_DATA, "Engine-contract source identity is invalid.")
            digest = hashlib.sha256(canonical_json_bytes({
                "artifact_id": artifact["artifact_id"],
                "contract_version": record_ids[0],
            })).hexdigest()
        if digest != artifact["semantic_content_sha256"]:
            raise _fail(
                VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                "Rule source semantics do not match the manifest.",
                path=artifact["path"],
            )
        source_by_id[artifact["artifact_id"]] = digest
    for identity in manifest.ordered_rule_revisions:
        if source_by_id.get(identity.source_artifact_id) != identity.source_artifact_semantic_sha256:
            raise _fail(
                VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                "Rule identity is detached from its source artifact.",
                rule_id=identity.rule_id,
            )
    if manifest.dependency_graph is not None:
        from systems.Parasara.engine.rules.graph import RuleGraphCompiler, GraphAnalysisSucceeded
        graph_result = RuleGraphCompiler.analyze_source(
            source_id=manifest.dependency_graph.artifact_path,
            payload=_load_graph_source(manifest, repository_root),
            analyzed_rule_set=analyzed,
            dsl_source_artifact_id=manifest.ordered_source_artifacts[0]["artifact_id"],
        )
        if not isinstance(graph_result, GraphAnalysisSucceeded):
            raise _graph_error(graph_result.diagnostics[0])
        _authorize_graph_analysis(manifest, graph_result.analysis)
    if not v2 and manifest.predicate_library.content_sha256 != predicate_registry_fingerprint_sha256():
        raise _fail(
            VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION,
            "Predicate registry does not match the selected manifest.",
        )
    if not v2 and manifest.predicate_library.version != PREDICATE_LIBRARY_VERSION:
        raise _fail(VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION, "Predicate library version is incompatible.")
    condition_identity = (
        manifest.condition_evaluator.identity,
        manifest.condition_evaluator.version,
        manifest.condition_evaluator.compatibility_contract,
        manifest.condition_evaluator.content_sha256,
    )
    expected_condition_identity = (
        CONDITION_EVALUATOR_IDENTITY,
        CONDITION_EVALUATOR_VERSION,
        CONDITION_EVALUATOR_COMPATIBILITY_CONTRACT,
        CONDITION_EVALUATOR_CONTENT_SHA256,
    )
    if v2:
        expected_condition_identity = expected_v2[1]
    if condition_identity != expected_condition_identity:
        raise _fail(
            VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION,
            "Condition evaluator identity, contract, or implementation digest is incompatible.",
            expected=expected_condition_identity,
            observed=condition_identity,
        )
    if manifest.dsl is not None:
        from systems.Parasara.engine.rules.dsl import (
            COMPILED_RULE_SET_SCHEMA_VERSION,
            DSL_CANONICALIZATION_CONTRACT,
            DSL_COMPATIBILITY_CONTRACT,
            DSL_COMPILER_CONTENT_SHA256,
            DSL_COMPILER_IDENTITY,
            DSL_COMPILER_VERSION,
            DSL_MACRO_EXPANSION_CONTRACT,
            DSL_SCHEMA_VERSION,
        )
        expected_dsl = (
            DSL_COMPILER_IDENTITY,
            DSL_COMPILER_VERSION,
            DSL_COMPATIBILITY_CONTRACT,
            DSL_COMPILER_CONTENT_SHA256,
        )
        if v2:
            expected_dsl = expected_v2[2]
        observed_dsl = (
            manifest.dsl.identity,
            manifest.dsl.version,
            manifest.dsl.compatibility_contract,
            manifest.dsl.content_sha256,
        )
        expected_metadata = FrozenMapping({
            "canonicalization_contract": DSL_CANONICALIZATION_CONTRACT,
            "compiled_artifact_schema_version": COMPILED_RULE_SET_SCHEMA_VERSION,
            "dsl_schema_version": DSL_SCHEMA_VERSION,
            "macro_expansion_contract": DSL_MACRO_EXPANSION_CONTRACT,
        })
        if observed_dsl != expected_dsl or manifest.dsl.metadata != expected_metadata:
            raise _fail(
                VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION,
                "DSL compiler identity, contracts, metadata, or implementation digest is incompatible.",
            )
    if manifest.inference.artifact_path is None or manifest.inference.content_sha256 is None:
        raise _fail(VersioningErrorCode.INVALID_VERSIONING_DATA, "Inference artifact identity is incomplete.")
    inference_path = _resolve_repository_path(repository_root, manifest.inference.artifact_path)
    if _file_sha256(inference_path) != manifest.inference.content_sha256:
        raise _fail(VersioningErrorCode.CONTENT_DIGEST_MISMATCH, "Inference configuration bytes do not match the manifest.")
    for knowledge in manifest.knowledge_data:
        if _knowledge_bundle_sha256(repository_root, knowledge.artifacts) != knowledge.content_sha256:
            raise _fail(
                VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                "Knowledge-data bundle does not match the manifest.",
                identity=knowledge.identity,
            )


@dataclass(frozen=True, slots=True, kw_only=True, eq=False)
class ResolvedEvaluationVersions:
    config: EngineConfig
    manifest: EvaluationVersionManifest
    lifecycle: RulePackLifecycle
    manifest_fingerprint_sha256: str
    warnings: tuple[str, ...]
    catalog_entry: Mapping[str, Any] = field(repr=False)
    _repository_root: Path = field(repr=False, compare=False)
    _owner_token: object = field(repr=False, compare=False)
    _issued_compiled_rule_sets: dict[int, Any] = field(default_factory=dict, repr=False, compare=False)
    _issued_compiled_rules: dict[int, Any] = field(default_factory=dict, repr=False, compare=False)
    _issued_graph_plan: Any = field(default=None, init=False, repr=False, compare=False)
    _factory_token: InitVar[object | None] = None

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _RESOLUTION_TOKEN:
            raise ValueError("ResolvedEvaluationVersions requires RuleVersionResolver")
        if not isinstance(self.config, EngineConfig) or not isinstance(self.manifest, EvaluationVersionManifest):
            raise TypeError("resolved selection requires typed config and manifest")
        if not isinstance(self.lifecycle, RulePackLifecycle):
            raise TypeError("lifecycle must be RulePackLifecycle")
        _sha("manifest_fingerprint_sha256", self.manifest_fingerprint_sha256)
        if self.manifest_fingerprint_sha256 != self.manifest.manifest_fingerprint_sha256:
            raise ValueError("resolved fingerprint and manifest disagree")
        if not isinstance(self.warnings, tuple) or any(not isinstance(item, str) or not item for item in self.warnings):
            raise TypeError("warnings must be an immutable string tuple")
        if not isinstance(self._repository_root, Path) or not self._repository_root.is_absolute():
            raise TypeError("repository root must be an absolute Path")
        object.__setattr__(self, "catalog_entry", _frozen_mapping("catalog_entry", self.catalog_entry))

    @property
    def predicate_component_fingerprint_sha256(self) -> str:
        return hashlib.sha256(canonical_json_bytes({
            "engine_evaluation_contract": self.manifest.engine.compatibility_contract,
            "predicate_library": _component_to_data(self.manifest.predicate_library),
            "condition_evaluator": _component_to_data(self.manifest.condition_evaluator),
        })).hexdigest()

    def require_same(self, other: Any) -> None:
        if other is not self:
            raise _fail(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "A different resolved authority cannot replace the run authority.",
            )

    def authorize_snapshot(self, snapshot: Any) -> None:
        context = getattr(snapshot, "evaluation_context", None)
        instant = context.get("instant") if isinstance(context, Mapping) else None
        if instant is not None and instant != self.config.evaluation_instant:
            raise _fail(
                VersioningErrorCode.EVALUATION_INSTANT_MISMATCH,
                "EngineConfig and AstroStateSnapshot instants disagree.",
            )

    def authorize_source_artifact(
        self,
        *,
        artifact_path: str | Path | None,
        semantic_content_sha256: str | None,
    ) -> Mapping[str, Any]:
        if artifact_path is None or semantic_content_sha256 is None:
            raise _fail(
                VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                "An authoritative rule source requires its path and semantic digest.",
            )
        _sha("semantic_content_sha256", semantic_content_sha256)
        observed_path = Path(artifact_path).resolve()
        for artifact in self.manifest.ordered_source_artifacts:
            if artifact["format"] != "yaml":
                continue
            expected_path = _resolve_repository_path(
                self._repository_root, artifact["path"]
            )
            if observed_path != expected_path:
                continue
            if semantic_content_sha256 != artifact["semantic_content_sha256"]:
                raise _fail(
                    VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                    "Rule-source semantics disagree with the selected manifest.",
                    path=artifact["path"],
                )
            return artifact
        raise _fail(
            VersioningErrorCode.AUTHORITY_MISMATCH,
            "Rule source path is not authorized by the selected manifest.",
            path=observed_path.as_posix(),
        )

    def load_authorized_dsl_source(
        self,
        *,
        source_id: str,
        compiler_identity: tuple[str, str, str, str],
        compiler_metadata: Mapping[str, Any],
        max_bytes: int,
    ) -> bytes:
        """Load only the exact single source selected by a DSL manifest."""

        if self.manifest.dsl is None:
            raise _fail(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "The selected manifest has no DSL authority.",
                dsl_code="authority",
            )
        observed = (
            self.manifest.dsl.identity,
            self.manifest.dsl.version,
            self.manifest.dsl.compatibility_contract,
            self.manifest.dsl.content_sha256,
        )
        if observed != compiler_identity or self.manifest.dsl.metadata != FrozenMapping(compiler_metadata):
            raise _fail(
                VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION,
                "The selected manifest pins a different DSL compiler.",
                dsl_code="compiler",
            )
        selected = [
            item for item in self.manifest.ordered_source_artifacts
            if item["format"] == "rule-dsl-yaml" and item["path"] == source_id
        ]
        if len(selected) != 1:
            raise _fail(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "The requested DSL source is not selected by the manifest.",
                dsl_code="authority",
            )
        path = _resolve_repository_path(self._repository_root, source_id)
        try:
            if type(max_bytes) is not int or max_bytes < 1 or path.stat().st_size > max_bytes:
                raise OSError("selected DSL source exceeds the compiler source-size bound")
            return path.read_bytes()
        except OSError as exc:
            raise _fail(
                VersioningErrorCode.HISTORICAL_CONTENT_UNAVAILABLE,
                "The selected DSL source is unavailable.",
                dsl_code="authority",
            ) from exc

    def authorize_dsl_analysis(self, value: Any) -> None:
        """Verify all unsealed canonical products against the selected manifest."""

        from systems.Parasara.engine.rules.dsl import AnalyzedRuleSet

        if self.manifest.dsl is None or not isinstance(value, AnalyzedRuleSet):
            raise _fail(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "A typed DSL analysis and DSL manifest are required.",
                dsl_code="authority",
            )
        expected_identity = (
            self.manifest.system,
            self.manifest.rule_set_family,
            self.manifest.rule_set_version,
        )
        observed_identity = (
            value.document.system,
            value.document.rule_set_family,
            value.document.rule_set_version,
        )
        if observed_identity != expected_identity:
            raise _fail(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "DSL document identity disagrees with the selected manifest.",
                dsl_code="authority",
            )
        artifacts = tuple(
            item for item in self.manifest.ordered_source_artifacts
            if item["format"] == "rule-dsl-yaml" and item["path"] == value.document.source_id
        )
        if len(artifacts) != 1:
            raise _fail(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "DSL source identity is not selected by the manifest.",
                dsl_code="authority",
            )
        artifact = artifacts[0]
        if artifact["semantic_content_sha256"] != value.canonical_dsl_sha256:
            raise _fail(
                VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                "Canonical DSL content disagrees with the selected manifest.",
                dsl_code="source",
            )
        if (
            artifact["expanded_ast_sha256"] != value.expanded_ast_sha256
            or artifact["compiled_rule_set_sha256"] != value.compiled_rule_set_sha256
        ):
            raise _fail(
                VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                "DSL expanded or compiled identity disagrees with the selected manifest.",
                dsl_code="compiled",
            )
        expected_rules = self.manifest.ordered_rule_revisions
        if len(expected_rules) != len(value.rules):
            raise _fail(
                VersioningErrorCode.RULE_CONTENT_MISMATCH,
                "DSL rule membership disagrees with the selected manifest.",
                dsl_code="compiled",
            )
        for index, (identity, analyzed) in enumerate(zip(expected_rules, value.rules)):
            if (
                identity.source_order != index
                or (identity.rule_id, identity.revision) != (
                    analyzed.resolved_rule.rule_id,
                    analyzed.resolved_rule.rule_version,
                )
                or identity.semantic_content_sha256 != analyzed.compiled_semantic_sha256
                or canonical_json_bytes(identity.semantic_contract) != canonical_json_bytes(analyzed.semantic_contract)
                or identity.source_artifact_semantic_sha256 != value.canonical_dsl_sha256
            ):
                raise _fail(
                    VersioningErrorCode.RULE_CONTENT_MISMATCH,
                    "DSL rule semantics disagree with the selected manifest.",
                    dsl_code="compiled",
                    source_order=index,
                )
            self.authorize_rule(analyzed.resolved_rule)

    def authorize_compiled_rule_set(self, value: Any) -> None:
        """Authorize and register only exact compiler-created artifact objects."""

        from systems.Parasara.engine.rules.dsl import CompiledRuleSet

        if not isinstance(value, CompiledRuleSet) or not value.is_compiler_sealed():
            raise _fail(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "Compiled rule set was not created by RuleDslCompiler.",
            )
        already_issued = self._issued_compiled_rule_sets.get(id(value))
        if already_issued is not value and any(
            self._issued_compiled_rules.get(id(rule)) is rule for rule in value.rules
        ):
            raise _fail(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "A copied or replacement compiled rule set cannot acquire authority.",
            )
        self.require_same(value.resolved_versions)
        artifact = next(
            (
                item for item in self.manifest.ordered_source_artifacts
                if item["format"] == "rule-dsl-yaml" and item["path"] == value.source_identity
            ),
            None,
        )
        if artifact is None or (
            value.system,
            value.rule_set_family,
            value.rule_set_version,
            value.manifest_fingerprint_sha256,
        ) != (
            self.manifest.system,
            self.manifest.rule_set_family,
            self.manifest.rule_set_version,
            self.manifest_fingerprint_sha256,
        ) or (
            value.canonical_dsl_sha256 != artifact["semantic_content_sha256"]
            or value.expanded_ast_sha256 != artifact["expanded_ast_sha256"]
            or value.compiled_rule_set_sha256 != artifact["compiled_rule_set_sha256"]
        ):
            raise _fail(
                VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                "Compiled rule-set identity disagrees with the selected manifest.",
            )
        if len(value.rules) != len(self.manifest.ordered_rule_revisions):
            raise _fail(VersioningErrorCode.RULE_CONTENT_MISMATCH, "Compiled rule membership disagrees with manifest.")
        for identity, rule in zip(self.manifest.ordered_rule_revisions, value.rules):
            if not rule.is_compiler_sealed() or rule.resolved_versions is not self:
                raise _fail(VersioningErrorCode.AUTHORITY_MISMATCH, "Compiled rule authority is invalid.")
            if (
                (rule.resolved_rule.rule_id, rule.resolved_rule.rule_version)
                != (identity.rule_id, identity.revision)
                or rule.compiled_semantic_sha256 != identity.semantic_content_sha256
                or rule.canonical_dsl_sha256 != value.canonical_dsl_sha256
            ):
                raise _fail(VersioningErrorCode.RULE_CONTENT_MISMATCH, "Compiled rule identity disagrees with manifest.")
            self.authorize_rule(rule.resolved_rule)
        self._issued_compiled_rule_sets[id(value)] = value
        for rule in value.rules:
            self._issued_compiled_rules[id(rule)] = rule

    def authorize_compiled_rule(self, value: Any) -> RuleRevisionIdentity:
        """Reject caller-created, replaced, shallow-copied, or cross-run artifacts."""

        from systems.Parasara.engine.rules.dsl import CompiledRule

        if (
            not isinstance(value, CompiledRule)
            or self._issued_compiled_rules.get(id(value)) is not value
            or not value.is_compiler_sealed()
        ):
            raise _fail(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "Compiled rule is not an exact artifact issued for this authority.",
            )
        self.require_same(value.resolved_versions)
        identity = self.authorize_rule(value.resolved_rule)
        if identity.semantic_content_sha256 != value.compiled_semantic_sha256:
            raise _fail(VersioningErrorCode.RULE_CONTENT_MISMATCH, "Compiled rule digest disagrees with manifest.")
        return identity

    def load_authorized_graph_source(self) -> bytes:
        return _load_graph_source(self.manifest, self._repository_root)

    def authorize_graph_analysis(self, analysis: Any) -> None:
        _authorize_graph_analysis(self.manifest, analysis)

    def _issue_execution_plan(self, plan: Any) -> None:
        from systems.Parasara.engine.rules.graph.models import RuleExecutionPlan, diagnostic
        if (type(plan) is not RuleExecutionPlan or plan.resolved_versions is not self
            or self._issued_graph_plan is not None):
            raise _graph_error(diagnostic("P08E302_AUTHORITY_MISMATCH"))
        self.authorize_compiled_rule_set(plan.compiled_rule_set)
        self.authorize_graph_analysis(plan.graph.analysis)
        object.__setattr__(self, "_issued_graph_plan", plan)

    def authorize_execution_plan(self, plan: Any) -> None:
        from systems.Parasara.engine.rules.graph.models import RuleExecutionPlan, diagnostic
        if type(plan) is not RuleExecutionPlan or self._issued_graph_plan is not plan or plan.resolved_versions is not self:
            raise _graph_error(diagnostic("P08E302_AUTHORITY_MISMATCH"))
        if self._issued_compiled_rule_sets.get(id(plan.compiled_rule_set)) is not plan.compiled_rule_set:
            raise _graph_error(diagnostic("P08E302_AUTHORITY_MISMATCH"))
        self.authorize_compiled_rule_set(plan.compiled_rule_set)
        self.authorize_graph_analysis(plan.graph.analysis)

    def authorize_rule(self, value: Any) -> RuleRevisionIdentity:
        if getattr(value, "system", None) != self.manifest.system:
            raise _fail(VersioningErrorCode.RULE_CONTENT_MISMATCH, "Rule system disagrees with manifest.")
        if getattr(value, "rule_set_version", None) != self.manifest.rule_set_version:
            raise _fail(VersioningErrorCode.RULE_CONTENT_MISMATCH, "Rule-set version disagrees with manifest.")
        return self.manifest.rule_identity_for(value)

    def authorize_inference_config(self, config: Any) -> None:
        if getattr(config, "system", None) != self.manifest.system:
            raise _fail(VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION, "Inference system disagrees with manifest.")
        if getattr(config, "inference_version", None) != self.manifest.inference.version:
            raise _fail(VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION, "Inference version disagrees with manifest.")
        if self.manifest.inference.logical_sha256 is not None:
            from systems.Parasara.engine.inference.config import inference_config_logical_sha256
            if inference_config_logical_sha256(config) != self.manifest.inference.logical_sha256:
                raise _fail(VersioningErrorCode.CONTENT_DIGEST_MISMATCH, "Inference configuration semantics disagree with manifest.")

    def authorize_inference_result(self, result: Any) -> None:
        expected = (
            self.manifest.system,
            self.manifest.rule_set_version,
            self.manifest.inference.version,
        )
        observed = (
            getattr(result, "system", None),
            getattr(result, "rule_set_version", None),
            getattr(result, "inference_version", None),
        )
        if observed != expected:
            raise _fail(VersioningErrorCode.AUTHORITY_MISMATCH, "InferenceResult labels disagree with run authority.")

    def authorize_domain_prediction(self, prediction: Any) -> None:
        expected = (
            self.manifest.system,
            self.manifest.engine.version,
            self.manifest.rule_set_version,
            self.manifest.inference.version,
        )
        observed = (
            getattr(prediction, "system", None),
            getattr(prediction, "engine_version", None),
            getattr(prediction, "rule_set_version", None),
            getattr(prediction, "inference_version", None),
        )
        if observed != expected:
            raise _fail(VersioningErrorCode.AUTHORITY_MISMATCH, "DomainPrediction labels disagree with run authority.")
        source_authority = getattr(prediction, "source_authority", None)
        source_versions = getattr(source_authority, "resolved_versions", None)
        if source_authority is None or source_versions is None:
            raise _fail(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "Evaluated DomainPrediction has no same-run resolved authority.",
            )
        self.require_same(source_versions)

    def authorize_engine_metadata(self, metadata: Any) -> None:
        expected = (
            self.manifest.engine.version,
            self.manifest.rule_set_family,
            self.manifest.rule_set_version,
        )
        observed = (
            getattr(metadata, "engine_version", None),
            getattr(metadata, "rule_set_family", None),
            getattr(metadata, "rule_set_version", None),
        )
        if observed != expected:
            raise _fail(VersioningErrorCode.AUTHORITY_MISMATCH, "Engine metadata labels disagree with run authority.")
        bound_authority = getattr(metadata, "resolved_versions", None)
        if bound_authority is None:
            raise _fail(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "Engine metadata has no same-run resolved authority.",
            )
        self.require_same(bound_authority)

    def authorize_yoga_diagnostic(self, diagnostic: Any) -> None:
        record = getattr(diagnostic, "source_evaluation_record", None)
        source_versions = getattr(record, "resolved_versions", None)
        if record is None or source_versions is None:
            raise _fail(
                VersioningErrorCode.AUTHORITY_MISMATCH,
                "YogaDiagnostic has no same-run resolved authority.",
            )
        self.require_same(source_versions)
        self.authorize_rule(getattr(diagnostic, "source_rule_match", None))

    def create_evaluation_record(
        self,
        *,
        snapshot: Any,
        snapshot_sha256: str,
        domain_results: Sequence[Any],
        yoga_results: Sequence[Any],
        public_output: Mapping[str, Any],
        rule_match_trace_ids: Sequence[str],
        output_sha256: str | None = None,
        normalized_input_sha256: str | None = None,
        replay_of_manifest_sha256: str | None = None,
        trace: Mapping[str, Any] | None = None,
    ) -> "EvaluationRecord":
        return EvaluationRecord(
            record_schema_version=VERSIONING_SCHEMA_VERSION,
            resolved_versions=self,
            evaluation_instant=self.config.evaluation_instant,
            snapshot=snapshot,
            snapshot_sha256=snapshot_sha256,
            domain_results=tuple(domain_results),
            yoga_results=tuple(yoga_results),
            public_output=public_output,
            normalized_input_sha256=normalized_input_sha256,
            rule_match_trace_ids=tuple(rule_match_trace_ids),
            output_sha256=output_sha256,
            replay_of_manifest_sha256=replay_of_manifest_sha256,
            trace={} if trace is None else trace,
            _factory_token=_EVALUATION_RECORD_TOKEN,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class EvaluationRecord:
    record_schema_version: str
    resolved_versions: ResolvedEvaluationVersions
    evaluation_instant: str
    snapshot: Any = field(repr=False, compare=False)
    snapshot_sha256: str
    domain_results: tuple[Any, ...] = field(repr=False, compare=False)
    yoga_results: tuple[Any, ...] = field(repr=False, compare=False)
    public_output: Mapping[str, Any] = field(repr=False, compare=False)
    normalized_input_sha256: str | None
    rule_match_trace_ids: tuple[str, ...]
    output_sha256: str | None
    replay_of_manifest_sha256: str | None
    trace: Mapping[str, Any]
    _factory_token: InitVar[object | None] = None

    def __post_init__(self, _factory_token: object | None) -> None:
        if _factory_token is not _EVALUATION_RECORD_TOKEN:
            raise ValueError("EvaluationRecord requires a resolved evaluation authority")
        if self.record_schema_version != VERSIONING_SCHEMA_VERSION:
            raise ValueError("unsupported evaluation-record schema")
        if not isinstance(self.resolved_versions, ResolvedEvaluationVersions):
            raise TypeError("resolved_versions must be ResolvedEvaluationVersions")
        _evaluation_instant(self.evaluation_instant)
        if self.evaluation_instant != self.resolved_versions.config.evaluation_instant:
            raise _fail(
                VersioningErrorCode.EVALUATION_INSTANT_MISMATCH,
                "EvaluationRecord instant disagrees with its authority.",
            )
        self.resolved_versions.authorize_snapshot(self.snapshot)
        _sha("snapshot_sha256", self.snapshot_sha256)
        from systems.Parasara.engine.astrostate_api import snapshot_logical_sha256

        if snapshot_logical_sha256(self.snapshot) != self.snapshot_sha256:
            raise _fail(
                VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                "EvaluationRecord snapshot digest does not match its immutable input.",
            )
        _optional_sha("normalized_input_sha256", self.normalized_input_sha256)
        _optional_sha("output_sha256", self.output_sha256)
        _optional_sha("replay_of_manifest_sha256", self.replay_of_manifest_sha256)
        if not isinstance(self.rule_match_trace_ids, tuple) or any(
            not isinstance(item, str) or not item for item in self.rule_match_trace_ids
        ):
            raise TypeError("rule_match_trace_ids must be an immutable string tuple")
        if not isinstance(self.domain_results, tuple):
            raise TypeError("domain_results must be an immutable tuple")
        if not isinstance(self.yoga_results, tuple):
            raise TypeError("yoga_results must be an immutable tuple")
        for prediction in self.domain_results:
            self.resolved_versions.authorize_domain_prediction(prediction)
        for diagnostic in self.yoga_results:
            self.resolved_versions.authorize_yoga_diagnostic(diagnostic)
        object.__setattr__(
            self,
            "public_output",
            _frozen_mapping("public_output", self.public_output),
        )
        if self.output_sha256 is None or hashlib.sha256(
            canonical_json_bytes(self.public_output)
        ).hexdigest() != self.output_sha256:
            raise _fail(
                VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
                "EvaluationRecord public-output digest is missing or incorrect.",
            )
        object.__setattr__(self, "trace", _frozen_mapping("trace", self.trace))


def _catalog_entries(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Mapping) or set(value) != {
        "catalog_schema_version", "entries", "migration_inventory"
    }:
        raise ValueError("catalog has missing or unknown fields")
    if value["catalog_schema_version"] != VERSIONING_SCHEMA_VERSION:
        raise ValueError("unsupported catalog schema")
    entries = value["entries"]
    if not isinstance(entries, list):
        raise TypeError("catalog entries must be a list")
    required = {
        "system", "family", "version", "manifest_path", "manifest_file_sha256",
        "lifecycle", "technical_validation_evidence", "astrology_sme_approved",
        "astrology_sme_approval_evidence", "available", "replay_available",
        "rollback_authorized", "warning", "allowed_modes", "allowed_purposes",
    }
    output = []
    seen = set()
    for entry in entries:
        if not isinstance(entry, Mapping) or set(entry) != required:
            raise ValueError("catalog entry has missing or unknown fields")
        key = (entry["system"], entry["family"], entry["version"])
        if key in seen:
            raise ValueError("catalog selection identities must be unique")
        seen.add(key)
        output.append(entry)
    if not isinstance(value["migration_inventory"], list):
        raise TypeError("migration_inventory must be a list")
    return tuple(output)


def _lifecycle_decision(entry: Mapping[str, Any], config: EngineConfig) -> tuple[RulePackLifecycle, tuple[str, ...]]:
    try:
        lifecycle = RulePackLifecycle(entry["lifecycle"])
    except (KeyError, ValueError) as exc:
        raise _fail(VersioningErrorCode.INVALID_VERSIONING_DATA, "Catalog lifecycle is invalid.") from exc
    if not entry["available"]:
        raise _fail(VersioningErrorCode.RULE_SET_UNAVAILABLE, "Selected rule set is unavailable.")
    if config.mode.value not in entry["allowed_modes"] or config.purpose.value not in entry["allowed_purposes"]:
        raise _fail(VersioningErrorCode.LIFECYCLE_SELECTION_FORBIDDEN, "Catalog policy forbids this selection mode/purpose.")
    if config.purpose is SelectionPurpose.REPLAY:
        if not entry["replay_available"]:
            raise _fail(VersioningErrorCode.HISTORICAL_CONTENT_UNAVAILABLE, "Selected historical rule set is not replayable.")
    elif config.purpose is SelectionPurpose.ROLLBACK:
        if lifecycle not in {RulePackLifecycle.PRODUCTION, RulePackLifecycle.DEPRECATED} or not entry["rollback_authorized"]:
            raise _fail(VersioningErrorCode.LIFECYCLE_SELECTION_FORBIDDEN, "Selected rule set is not an authorized rollback target.")
    elif lifecycle is RulePackLifecycle.ARCHIVED:
        raise _fail(VersioningErrorCode.LIFECYCLE_SELECTION_FORBIDDEN, "Archived rule sets are replay-only.")
    if config.mode is EngineMode.STRICT and config.purpose is SelectionPurpose.NEW_EVALUATION:
        if lifecycle is not RulePackLifecycle.PRODUCTION or entry["astrology_sme_approved"] is not True:
            raise _fail(VersioningErrorCode.LIFECYCLE_SELECTION_FORBIDDEN, "Strict production selection requires approved Production content.")
    warnings = ()
    if lifecycle is RulePackLifecycle.DEPRECATED:
        warning = entry["warning"] or "Selected rule set is deprecated."
        warnings = (warning,)
    elif lifecycle is RulePackLifecycle.ARCHIVED:
        warnings = (entry["warning"] or "Selected rule set is archived and replay-only.",)
    elif config.mode is EngineMode.EXPERIMENTAL and entry["warning"]:
        warnings = (entry["warning"],)
    return lifecycle, warnings


class RuleVersionResolver:
    """The sole production owner of exact rule-set version selection."""

    __slots__ = ("_catalog_path", "_repository_root", "_owner_token")

    def __init__(self) -> None:
        self._catalog_path = DEFAULT_RULE_SET_CATALOG
        self._repository_root = REPOSITORY_ROOT
        self._owner_token = object()

    @classmethod
    def for_test(
        cls,
        *,
        catalog_path: str | Path,
        repository_root: str | Path,
        _token: object = _TEST_RESOLVER_TOKEN,
    ) -> "RuleVersionResolver":
        if _token is not _TEST_RESOLVER_TOKEN:
            raise ValueError("test resolver construction is unavailable")
        instance = object.__new__(cls)
        instance._catalog_path = Path(catalog_path).resolve()
        instance._repository_root = Path(repository_root).resolve()
        instance._owner_token = object()
        return instance

    def resolve(
        self,
        config: EngineConfig,
        *,
        snapshot: Any | None = None,
    ) -> ResolvedEvaluationVersions:
        if not isinstance(config, EngineConfig):
            raise TypeError("config must be EngineConfig")
        catalog = _read_json(self._catalog_path, unavailable_code=VersioningErrorCode.RULE_SET_UNAVAILABLE)
        entries = _catalog_entries(catalog)
        selected = [
            entry for entry in entries
            if (entry["system"], entry["family"], entry["version"])
            == (config.system, config.rule_set_family, config.rule_set_version)
        ]
        if len(selected) != 1:
            raise _fail(
                VersioningErrorCode.UNKNOWN_RULE_SET_VERSION,
                "No exact catalog entry exists for the requested rule-set version.",
                system=config.system,
                family=config.rule_set_family,
                version=config.rule_set_version,
            )
        entry = selected[0]
        lifecycle, warnings = _lifecycle_decision(entry, config)
        manifest_path = _resolve_repository_path(self._repository_root, entry["manifest_path"])
        observed_file_sha = _file_sha256(manifest_path)
        if observed_file_sha != entry["manifest_file_sha256"]:
            raise _fail(
                VersioningErrorCode.MANIFEST_DIGEST_MISMATCH,
                "Manifest file digest does not match the catalog.",
                expected=entry["manifest_file_sha256"],
                observed=observed_file_sha,
            )
        try:
            manifest = manifest_from_data(
                _read_json(manifest_path, unavailable_code=VersioningErrorCode.HISTORICAL_CONTENT_UNAVAILABLE)
            )
        except VersioningError:
            raise
        except (TypeError, ValueError) as exc:
            raise _fail(VersioningErrorCode.INVALID_VERSIONING_DATA, "Manifest contract validation failed.") from exc
        if (
            manifest.system,
            manifest.rule_set_family,
            manifest.rule_set_version,
        ) != (config.system, config.rule_set_family, config.rule_set_version):
            raise _fail(VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION, "Manifest selection identity disagrees with EngineConfig.")
        if manifest.engine.version != config.engine_version or manifest.engine.compatibility_contract != EVALUATION_CONTRACT_VERSION:
            raise _fail(VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION, "Engine implementation/contract is incompatible.")
        if (manifest.output_schema_version, manifest.compatibility_profile) != (
            config.output_schema_version, config.compatibility_profile,
        ):
            raise _fail(VersioningErrorCode.INCOMPATIBLE_COMPONENT_VERSION, "Output contract is incompatible.")
        if snapshot is not None:
            context = getattr(snapshot, "evaluation_context", None)
            instant = context.get("instant") if isinstance(context, Mapping) else None
            if instant is not None and instant != config.evaluation_instant:
                raise _fail(
                    VersioningErrorCode.EVALUATION_INSTANT_MISMATCH,
                    "EngineConfig and AstroStateSnapshot instants disagree.",
                )
        _verify_manifest_artifacts(manifest, self._repository_root)
        return ResolvedEvaluationVersions(
            config=config,
            manifest=manifest,
            lifecycle=lifecycle,
            manifest_fingerprint_sha256=manifest.manifest_fingerprint_sha256,
            warnings=warnings,
            catalog_entry=entry,
            _repository_root=self._repository_root,
            _owner_token=self._owner_token,
            _factory_token=_RESOLUTION_TOKEN,
        )


def compare_manifests(
    old: EvaluationVersionManifest,
    new: EvaluationVersionManifest,
) -> FrozenMapping:
    """Return one deterministic semantic comparison without approval claims."""

    if not isinstance(old, EvaluationVersionManifest) or not isinstance(new, EvaluationVersionManifest):
        raise TypeError("old and new must be EvaluationVersionManifest values")
    old_rules = {(item.rule_id, item.revision): item for item in old.ordered_rule_revisions}
    new_rules = {(item.rule_id, item.revision): item for item in new.ordered_rule_revisions}
    removed = sorted(set(old_rules) - set(new_rules))
    added = sorted(set(new_rules) - set(old_rules))
    common = sorted(set(old_rules) & set(new_rules))
    changed = [
        key for key in common
        if old_rules[key].semantic_content_sha256 != new_rules[key].semantic_content_sha256
    ]
    old_order = [(item.rule_id, item.revision) for item in old.ordered_rule_revisions]
    new_order = [(item.rule_id, item.revision) for item in new.ordered_rule_revisions]
    component_names = (
        "engine", "predicate_library", "condition_evaluator", "inference",
        "knowledge_data", "output", "future_components",
    )
    old_data = manifest_to_data(old, include_fingerprint=False)
    new_data = manifest_to_data(new, include_fingerprint=False)
    components = {
        name: {"changed": old_data[name] != new_data[name], "old": old_data[name], "new": new_data[name]}
        for name in component_names
    }
    return FrozenMapping({
        "old_manifest_fingerprint_sha256": old.manifest_fingerprint_sha256,
        "new_manifest_fingerprint_sha256": new.manifest_fingerprint_sha256,
        "added_rules": [{"rule_id": key[0], "revision": key[1]} for key in added],
        "removed_rules": [{"rule_id": key[0], "revision": key[1]} for key in removed],
        "changed_rules": [{"rule_id": key[0], "revision": key[1]} for key in changed],
        "rule_order_changed": old_order != new_order,
        "old_rule_order": [{"rule_id": key[0], "revision": key[1]} for key in old_order],
        "new_rule_order": [{"rule_id": key[0], "revision": key[1]} for key in new_order],
        "components": components,
    })


__all__ = (
    "COMPATIBILITY_EVALUATION_INSTANT",
    "CONDITION_EVALUATOR_IDENTITY",
    "CONDITION_EVALUATOR_COMPATIBILITY_CONTRACT",
    "CONDITION_EVALUATOR_CONTENT_SHA256",
    "CONDITION_EVALUATOR_VERSION",
    "DEFAULT_RULE_SET_CATALOG",
    "EVALUATION_CONTRACT_VERSION",
    "EngineConfig",
    "EngineMode",
    "EvaluationRecord",
    "EvaluationVersionManifest",
    "KnowledgeDataIdentity",
    "PREDICATE_LIBRARY_IDENTITY",
    "PREDICATE_LIBRARY_VERSION",
    "ResolvedEvaluationVersions",
    "RulePackLifecycle",
    "RuleRevisionIdentity",
    "RuleVersionResolver",
    "SelectionPurpose",
    "VERSIONING_SCHEMA_VERSION",
    "VersioningError",
    "VersioningErrorCode",
    "compare_manifests",
    "compatibility_v1_config",
    "evaluation_instant_from_snapshot",
    "manifest_canonical_json_bytes",
    "manifest_fingerprint_sha256",
    "manifest_from_data",
    "manifest_to_data",
)
