"""Executable immutable predicate parameter schemas introduced by WP05."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import re
from typing import Any

from systems.Parasara.engine.rules.canonical import FrozenMapping, freeze_canonical
from systems.Parasara.engine.rules.models import PredicateError


CANONICAL_PLANETS = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
)
FUNCTIONAL_ROLE_VALUES = (
    "benefic",
    "functional_benefic",
    "functional_malefic",
    "functional_neutral",
    "malefic",
    "yogakaraka",
)

_PLANET_BY_ASCII_CASE = {value.lower(): value for value in CANONICAL_PLANETS}
_PARAMETER_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_PREDICATE_ID = re.compile(r"^[A-Z][A-Z0-9_]*$")
_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_LOGICAL_OPERATORS = frozenset({"AND", "OR", "NOT"})


class ParameterSchemaError(ValueError):
    """A schema, schema lookup, or error-adapter invariant is invalid."""


class ParameterKind(str, Enum):
    HOUSE = "house"
    PLANET = "planet"
    ROLE_COLLECTION = "role_collection"


class ParameterIssueCode(str, Enum):
    INVALID_CONTAINER = "invalid_container"
    MISSING_REQUIRED = "missing_required"
    UNKNOWN_PARAMETER = "unknown_parameter"
    INVALID_TYPE = "invalid_type"
    INVALID_VALUE = "invalid_value"
    CONFLICTING_ALIAS = "conflicting_alias"
    DUPLICATE_VALUE = "duplicate_value"


_EXPECTED = {
    ParameterKind.HOUSE: "house_integer_1_12",
    ParameterKind.PLANET: "canonical_planet_catalog",
    ParameterKind.ROLE_COLLECTION: "functional_role_catalog",
}


def _normalize_value(kind: ParameterKind, value: Any, allowed_values: tuple[str, ...]):
    if kind is ParameterKind.HOUSE:
        if type(value) is not int:
            return None, ParameterIssueCode.INVALID_TYPE
        if not 1 <= value <= 12:
            return None, ParameterIssueCode.INVALID_VALUE
        return value, None

    if kind is ParameterKind.PLANET:
        if not isinstance(value, str):
            return None, ParameterIssueCode.INVALID_TYPE
        stripped = value.strip()
        if not stripped or not stripped.isascii():
            return None, ParameterIssueCode.INVALID_VALUE
        canonical = _PLANET_BY_ASCII_CASE.get(stripped.lower())
        if canonical is None:
            return None, ParameterIssueCode.INVALID_VALUE
        return canonical, None

    if kind is ParameterKind.ROLE_COLLECTION:
        if type(value) not in (list, tuple):
            return None, ParameterIssueCode.INVALID_TYPE
        if not value:
            return None, ParameterIssueCode.INVALID_VALUE
        if any(not isinstance(item, str) for item in value):
            return None, ParameterIssueCode.INVALID_TYPE
        if len(set(value)) != len(value):
            return None, ParameterIssueCode.DUPLICATE_VALUE
        if any(item not in allowed_values for item in value):
            return None, ParameterIssueCode.INVALID_VALUE
        return tuple(sorted(value)), None

    raise ParameterSchemaError("unsupported parameter kind")


@dataclass(frozen=True, slots=True, kw_only=True)
class ParameterSpec:
    """One exact parameter name and its executable normalization policy."""

    name: str
    kind: ParameterKind
    required: bool
    aliases: tuple[str, ...] = ()
    allowed_values: tuple[str, ...] = ()
    has_default: bool = False
    default: Any = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _PARAMETER_NAME.fullmatch(self.name):
            raise ParameterSchemaError("parameter name must be an exact lowercase identifier")
        try:
            kind = self.kind if isinstance(self.kind, ParameterKind) else ParameterKind(self.kind)
        except (TypeError, ValueError) as exc:
            raise ParameterSchemaError("unsupported parameter kind") from exc
        object.__setattr__(self, "kind", kind)
        if type(self.required) is not bool:
            raise ParameterSchemaError("required must be an actual Boolean")
        if not isinstance(self.aliases, tuple):
            raise ParameterSchemaError("parameter aliases must be an immutable tuple")
        if any(not isinstance(alias, str) or not _PARAMETER_NAME.fullmatch(alias) for alias in self.aliases):
            raise ParameterSchemaError("parameter aliases must be exact lowercase identifiers")
        if self.name in self.aliases or len(set(self.aliases)) != len(self.aliases):
            raise ParameterSchemaError("parameter aliases must be unique and cannot include the canonical name")
        if self.aliases != tuple(sorted(self.aliases)):
            raise ParameterSchemaError("parameter aliases must use lexicographic order")
        if not isinstance(self.allowed_values, tuple):
            raise ParameterSchemaError("allowed_values must be an immutable tuple")
        if kind is ParameterKind.ROLE_COLLECTION:
            if not self.allowed_values:
                raise ParameterSchemaError("role collection requires a closed non-empty vocabulary")
            if any(not isinstance(value, str) or not value for value in self.allowed_values):
                raise ParameterSchemaError("role vocabulary values must be non-empty strings")
            if len(set(self.allowed_values)) != len(self.allowed_values):
                raise ParameterSchemaError("role vocabulary values must be unique")
            if self.allowed_values != tuple(sorted(self.allowed_values)):
                raise ParameterSchemaError("role vocabulary must use lexicographic order")
        elif self.allowed_values:
            raise ParameterSchemaError("allowed_values are unsupported for this parameter kind")
        if type(self.has_default) is not bool:
            raise ParameterSchemaError("has_default must be an actual Boolean")
        if not self.has_default:
            if self.default is not None:
                raise ParameterSchemaError("default must be None when has_default is false")
        else:
            if self.required:
                raise ParameterSchemaError("required parameters cannot declare defaults")
            normalized, issue = _normalize_value(kind, self.default, self.allowed_values)
            if issue is not None:
                raise ParameterSchemaError("declared default does not satisfy its parameter kind")
            object.__setattr__(self, "default", freeze_canonical(normalized, path="$.default"))

    def metadata(self) -> FrozenMapping:
        return FrozenMapping(
            {
                "aliases": self.aliases,
                "allowed_values": self.allowed_values,
                "default": self.default,
                "has_default": self.has_default,
                "kind": self.kind,
                "name": self.name,
                "required": self.required,
            }
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ParameterValidationIssue:
    predicate_id: str
    parameter_name: str | None
    code: ParameterIssueCode
    expected: str
    path: str

    def __post_init__(self) -> None:
        if not isinstance(self.predicate_id, str) or not _PREDICATE_ID.fullmatch(self.predicate_id):
            raise ParameterSchemaError("issue predicate_id must be canonical")
        if self.parameter_name is not None and (
            not isinstance(self.parameter_name, str) or not _PARAMETER_NAME.fullmatch(self.parameter_name)
        ):
            raise ParameterSchemaError("issue parameter_name must be canonical when present")
        try:
            code = self.code if isinstance(self.code, ParameterIssueCode) else ParameterIssueCode(self.code)
        except (TypeError, ValueError) as exc:
            raise ParameterSchemaError("issue code is unsupported") from exc
        object.__setattr__(self, "code", code)
        if not isinstance(self.expected, str) or not self.expected or self.expected.strip() != self.expected:
            raise ParameterSchemaError("issue expected value must be a safe non-empty identifier")
        if not isinstance(self.path, str) or not self.path.startswith("$.parameters"):
            raise ParameterSchemaError("issue path must be a safe parameter path")

    def details(self) -> FrozenMapping:
        return FrozenMapping(
            {
                "expected": self.expected,
                "parameter_name": self.parameter_name,
                "path": self.path,
                "predicate_id": self.predicate_id,
                "reason_code": self.code,
            }
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ParameterValidationOutcome:
    valid: bool
    normalized_inputs: FrozenMapping | None
    issues: tuple[ParameterValidationIssue, ...]

    def __post_init__(self) -> None:
        if type(self.valid) is not bool:
            raise ParameterSchemaError("validation outcome valid must be an actual Boolean")
        if not isinstance(self.issues, tuple) or any(
            not isinstance(issue, ParameterValidationIssue) for issue in self.issues
        ):
            raise ParameterSchemaError("validation outcome issues must be an immutable issue tuple")
        if self.valid:
            if not isinstance(self.normalized_inputs, FrozenMapping) or self.issues:
                raise ParameterSchemaError("successful validation requires normalized inputs and no issues")
        elif self.normalized_inputs is not None or not self.issues:
            raise ParameterSchemaError("failed validation requires issues and no normalized inputs")


def _issue(
    predicate_id: str,
    parameter_name: str | None,
    code: ParameterIssueCode,
    expected: str,
    path: str,
) -> ParameterValidationIssue:
    return ParameterValidationIssue(
        predicate_id=predicate_id,
        parameter_name=parameter_name,
        code=code,
        expected=expected,
        path=path,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class ParameterSchema:
    """Ordered executable schema linked one-to-one with a predicate version."""

    predicate_id: str
    schema_version: str
    specifications: tuple[ParameterSpec, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.predicate_id, str)
            or not _PREDICATE_ID.fullmatch(self.predicate_id)
            or self.predicate_id in _LOGICAL_OPERATORS
        ):
            raise ParameterSchemaError("schema predicate_id must be canonical uppercase ASCII")
        if not isinstance(self.schema_version, str) or not _SEMVER.fullmatch(self.schema_version):
            raise ParameterSchemaError("schema_version must be Stage-01 MAJOR.MINOR.PATCH SemVer")
        if not isinstance(self.specifications, tuple) or any(
            not isinstance(spec, ParameterSpec) for spec in self.specifications
        ):
            raise ParameterSchemaError("specifications must be an immutable ParameterSpec tuple")
        names = [spec.name for spec in self.specifications]
        if len(set(names)) != len(names):
            raise ParameterSchemaError("schema parameter names must be unique")
        canonical_names = set(names)
        aliases: set[str] = set()
        for spec in self.specifications:
            for alias in spec.aliases:
                if alias in canonical_names:
                    raise ParameterSchemaError("parameter alias collides with a canonical parameter")
                if alias in aliases:
                    raise ParameterSchemaError("parameter aliases must be unique across the schema")
                aliases.add(alias)

    def metadata(self) -> FrozenMapping:
        return FrozenMapping(
            {
                "predicate_id": self.predicate_id,
                "schema_version": self.schema_version,
                "specifications": tuple(spec.metadata() for spec in self.specifications),
            }
        )

    def validate(self, supplied: Any) -> ParameterValidationOutcome:
        if not isinstance(supplied, Mapping):
            return ParameterValidationOutcome(
                valid=False,
                normalized_inputs=None,
                issues=(
                    _issue(
                        self.predicate_id,
                        None,
                        ParameterIssueCode.INVALID_CONTAINER,
                        "mapping",
                        "$.parameters",
                    ),
                ),
            )

        try:
            keys = tuple(supplied.keys())
        except Exception:
            return ParameterValidationOutcome(
                valid=False,
                normalized_inputs=None,
                issues=(
                    _issue(
                        self.predicate_id,
                        None,
                        ParameterIssueCode.INVALID_CONTAINER,
                        "readable_mapping",
                        "$.parameters",
                    ),
                ),
            )

        issues: list[ParameterValidationIssue] = []
        normalized: dict[str, Any] = {}
        known_keys: set[str] = set()

        for spec in self.specifications:
            known_keys.add(spec.name)
            known_keys.update(spec.aliases)
            canonical_present = spec.name in keys
            present_aliases = tuple(alias for alias in spec.aliases if alias in keys)
            path = f"$.parameters.{spec.name}"
            if (canonical_present and present_aliases) or len(present_aliases) > 1:
                issues.append(
                    _issue(
                        self.predicate_id,
                        spec.name,
                        ParameterIssueCode.CONFLICTING_ALIAS,
                        _EXPECTED[spec.kind],
                        path,
                    )
                )
                continue
            selected = spec.name if canonical_present else (present_aliases[0] if present_aliases else None)
            if selected is None:
                if spec.required:
                    issues.append(
                        _issue(
                            self.predicate_id,
                            spec.name,
                            ParameterIssueCode.MISSING_REQUIRED,
                            _EXPECTED[spec.kind],
                            path,
                        )
                    )
                elif spec.has_default:
                    normalized[spec.name] = spec.default
                continue
            try:
                raw_value = supplied[selected]
            except Exception:
                issues.append(
                    _issue(
                        self.predicate_id,
                        spec.name,
                        ParameterIssueCode.INVALID_CONTAINER,
                        "readable_mapping",
                        path,
                    )
                )
                continue
            canonical, issue_code = _normalize_value(spec.kind, raw_value, spec.allowed_values)
            if issue_code is not None:
                issues.append(_issue(self.predicate_id, spec.name, issue_code, _EXPECTED[spec.kind], path))
            else:
                normalized[spec.name] = canonical

        unknown_strings = sorted(key for key in keys if isinstance(key, str) and key not in known_keys)
        non_string_count = sum(1 for key in keys if not isinstance(key, str))
        for _ in unknown_strings:
            issues.append(
                _issue(
                    self.predicate_id,
                    None,
                    ParameterIssueCode.UNKNOWN_PARAMETER,
                    "declared_parameter_name",
                    "$.parameters[unknown]",
                )
            )
        for _ in range(non_string_count):
            issues.append(
                _issue(
                    self.predicate_id,
                    None,
                    ParameterIssueCode.UNKNOWN_PARAMETER,
                    "lowercase_string_parameter_name",
                    "$.parameters[unknown]",
                )
            )

        if issues:
            return ParameterValidationOutcome(valid=False, normalized_inputs=None, issues=tuple(issues))
        return ParameterValidationOutcome(
            valid=True,
            normalized_inputs=FrozenMapping(normalized),
            issues=(),
        )


ASPECT_PARAMETER_SCHEMA = ParameterSchema(
    predicate_id="ASPECT_EXISTS",
    schema_version="1.0.0",
    specifications=(
        ParameterSpec(name="from_house", kind=ParameterKind.HOUSE, required=False),
        ParameterSpec(name="to_house", kind=ParameterKind.HOUSE, required=False),
        ParameterSpec(name="from_planet", kind=ParameterKind.PLANET, required=False),
        ParameterSpec(name="to_planet", kind=ParameterKind.PLANET, required=False),
    ),
)
FUNCTIONAL_ROLE_PARAMETER_SCHEMA = ParameterSchema(
    predicate_id="FUNCTIONAL_ROLE",
    schema_version="1.0.0",
    specifications=(
        ParameterSpec(
            name="role_in",
            kind=ParameterKind.ROLE_COLLECTION,
            required=True,
            allowed_values=FUNCTIONAL_ROLE_VALUES,
        ),
    ),
)
HOUSE_OCCUPANT_PARAMETER_SCHEMA = ParameterSchema(
    predicate_id="HOUSE_OCCUPANT",
    schema_version="1.0.0",
    specifications=(
        ParameterSpec(name="house", kind=ParameterKind.HOUSE, required=True),
        ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True),
    ),
)
PLANET_EXALTED_PARAMETER_SCHEMA = ParameterSchema(
    predicate_id="PLANET_EXALTED",
    schema_version="1.0.0",
    specifications=(ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True),),
)
PLANET_IN_HOUSE_PARAMETER_SCHEMA = ParameterSchema(
    predicate_id="PLANET_IN_HOUSE",
    schema_version="1.0.0",
    specifications=(
        ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True),
        ParameterSpec(name="house", kind=ParameterKind.HOUSE, required=True),
    ),
)


def validate_predicate_parameters(predicate: Any, supplied: Any) -> ParameterValidationOutcome:
    """Validate using a canonical definition or any exposed registry ID."""

    from systems.Parasara.engine.rules.registry import PredicateDefinition, get_production_registry

    if isinstance(predicate, PredicateDefinition):
        definition = predicate
    else:
        try:
            definition = get_production_registry().lookup(predicate)
        except Exception as exc:
            raise ParameterSchemaError("predicate definition lookup failed") from exc
        if definition is None:
            raise ParameterSchemaError("unknown predicate definition")
    return definition.parameter_schema.validate(supplied)


def invalid_parameters_error(predicate_id: str, outcome: ParameterValidationOutcome) -> PredicateError:
    """Adapt an invalid outcome to the WP02 canonical safe error model."""

    if not isinstance(outcome, ParameterValidationOutcome) or outcome.valid:
        raise ParameterSchemaError("invalid-parameter adapter requires a failed validation outcome")
    if any(issue.predicate_id != predicate_id for issue in outcome.issues):
        raise ParameterSchemaError("error predicate ID disagrees with validation issues")
    return PredicateError(
        code="invalid_parameters",
        message="Predicate parameters are invalid.",
        predicate_id=predicate_id,
        details={"issues": tuple(issue.details() for issue in outcome.issues)},
        recoverable=True,
    )


__all__ = (
    "ASPECT_PARAMETER_SCHEMA",
    "CANONICAL_PLANETS",
    "FUNCTIONAL_ROLE_PARAMETER_SCHEMA",
    "FUNCTIONAL_ROLE_VALUES",
    "HOUSE_OCCUPANT_PARAMETER_SCHEMA",
    "PLANET_EXALTED_PARAMETER_SCHEMA",
    "PLANET_IN_HOUSE_PARAMETER_SCHEMA",
    "ParameterIssueCode",
    "ParameterKind",
    "ParameterSchema",
    "ParameterSchemaError",
    "ParameterSpec",
    "ParameterValidationIssue",
    "ParameterValidationOutcome",
    "invalid_parameters_error",
    "validate_predicate_parameters",
)
