"""WP05 executable parameter-schema and canonical-normalization contract."""

from dataclasses import dataclass, fields, replace
from decimal import Decimal
from enum import IntEnum
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from pydantic import BaseModel

from systems.Parasara.engine.rules.canonical import (
    FrozenMapping,
    canonical_json_bytes,
    predicate_error_json_bytes,
)
from systems.Parasara.engine.rules.models import PredicateError
from systems.Parasara.engine.rules.parameters import (
    CANONICAL_PLANETS,
    FUNCTIONAL_ROLE_VALUES,
    ParameterIssueCode,
    ParameterKind,
    ParameterSchema,
    ParameterSchemaError,
    ParameterSpec,
    ParameterValidationIssue,
    ParameterValidationOutcome,
    invalid_parameters_error,
    validate_predicate_parameters,
)
from systems.Parasara.engine.rules.registry import (
    CostClass,
    PredicateDefinition,
    PredicateDefinitionError,
    PredicateRegistry,
    get_production_registry,
    predicate_registry_fingerprint_bytes,
)


PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
ROLES = (
    "benefic",
    "functional_benefic",
    "functional_malefic",
    "functional_neutral",
    "malefic",
    "yogakaraka",
)
CANONICAL_IDS = (
    "ASPECT_EXISTS",
    "FUNCTIONAL_ROLE",
    "HOUSE_OCCUPANT",
    "PLANET_EXALTED",
    "PLANET_IN_HOUSE",
)
EXPOSED_IDS = (
    "ASPECT",
    "ASPECT_EXISTS",
    "FUNCTIONAL_ROLE",
    "HOUSE_OCCUPANT",
    "PLANET_EXALTED",
    "PLANET_IN_HOUSE",
)


def assert_valid(predicate_id, supplied, expected):
    outcome = validate_predicate_parameters(predicate_id, supplied)
    assert outcome.valid is True
    assert outcome.issues == ()
    assert isinstance(outcome.normalized_inputs, FrozenMapping)
    assert dict(outcome.normalized_inputs) == expected
    return outcome


def assert_invalid(predicate_id, supplied, *codes):
    outcome = validate_predicate_parameters(predicate_id, supplied)
    assert outcome.valid is False
    assert outcome.normalized_inputs is None
    assert tuple(issue.code.value for issue in outcome.issues) == codes
    return outcome


def synthetic_schema(*specifications):
    return ParameterSchema(
        predicate_id="SYNTHETIC",
        schema_version="1.0.0",
        specifications=tuple(specifications),
    )


def synthetic_definition(schema, handler=lambda *_: None):
    return PredicateDefinition(
        predicate_id="SYNTHETIC",
        predicate_version="1.0.0",
        description="A synthetic factual predicate.",
        parameter_schema=schema,
        required_capabilities=(),
        cacheable=True,
        deterministic=True,
        cost_class=CostClass.LOW,
        system_scope="parasara",
        handler=handler,
    )


def test_exact_schema_model_field_inventories_and_immutability():
    assert tuple(field.name for field in fields(ParameterSpec)) == (
        "name", "kind", "required", "aliases", "allowed_values", "has_default", "default"
    )
    assert tuple(field.name for field in fields(ParameterSchema)) == (
        "predicate_id", "schema_version", "specifications"
    )
    assert tuple(field.name for field in fields(ParameterValidationIssue)) == (
        "predicate_id", "parameter_name", "code", "expected", "path"
    )
    assert tuple(field.name for field in fields(ParameterValidationOutcome)) == (
        "valid", "normalized_inputs", "issues"
    )
    schema = get_production_registry().lookup("PLANET_IN_HOUSE").parameter_schema
    with pytest.raises((AttributeError, TypeError)):
        schema.schema_version = "changed"
    with pytest.raises((AttributeError, TypeError)):
        schema.specifications[0].name = "changed"


def test_exact_five_schema_and_six_exposed_id_inventory():
    registry = get_production_registry()
    assert registry.canonical_ids() == CANONICAL_IDS
    assert registry.exposed_ids() == EXPOSED_IDS
    assert all(isinstance(item.parameter_schema, ParameterSchema) for item in registry.canonical_definitions())
    assert registry.lookup("ASPECT").parameter_schema is registry.lookup("ASPECT_EXISTS").parameter_schema
    assert registry.lookup("PLANET_IN_HOUSE").parameter_schema is not registry.lookup("HOUSE_OCCUPANT").parameter_schema


@dataclass
class ParameterDataclass:
    planet: str = "Mars"


class ParameterPydantic(BaseModel):
    planet: str = "Mars"


@pytest.mark.parametrize(
    "value",
    [None, [], (), "", 0, False, (item for item in ()), object(), ParameterDataclass(), ParameterPydantic()],
)
def test_invalid_top_level_containers_are_safe_expected_failures(value):
    outcome = assert_invalid("ASPECT", value, "invalid_container")
    assert outcome.issues[0].parameter_name is None
    assert outcome.issues[0].path == "$.parameters"


def test_unknown_nonstring_wrong_case_and_whitespace_keys_are_invalid():
    assert_invalid("ASPECT", {"from_huose": 1}, "unknown_parameter")
    assert_invalid("ASPECT", {"From_house": 1}, "unknown_parameter")
    assert_invalid("ASPECT", {" from_house": 1}, "unknown_parameter")
    assert_invalid("ASPECT", {1: 1}, "unknown_parameter")


class UnreadableMapping(dict):
    def keys(self):
        raise RuntimeError("SECRET-MAPPING-ERROR")


def test_unreadable_mapping_returns_safe_container_issue_without_exception_text():
    outcome = assert_invalid("ASPECT", UnreadableMapping(), "invalid_container")
    payload = json.dumps(dict(outcome.issues[0].details()))
    assert "SECRET" not in payload


def test_multiple_issues_follow_schema_then_unknown_lexicographic_order():
    outcome = assert_invalid(
        "PLANET_IN_HOUSE",
        {"planet": None, "house": 0, "z_unknown": 1, "a_unknown": 2},
        "invalid_type", "invalid_value", "unknown_parameter", "unknown_parameter",
    )
    assert [issue.parameter_name for issue in outcome.issues] == ["planet", "house", None, None]
    assert [issue.path for issue in outcome.issues] == [
        "$.parameters.planet", "$.parameters.house", "$.parameters[unknown]", "$.parameters[unknown]"
    ]


def test_mapping_order_and_caller_mutation_do_not_change_normalized_inputs():
    roles = ["yogakaraka", "functional_benefic"]
    first = {"house": 7, "planet": " mars "}
    second = {"planet": "MARS", "house": 7}
    assert assert_valid("PLANET_IN_HOUSE", first, {"house": 7, "planet": "Mars"}).normalized_inputs == assert_valid(
        "PLANET_IN_HOUSE", second, {"house": 7, "planet": "Mars"}
    ).normalized_inputs
    outcome = assert_valid("FUNCTIONAL_ROLE", {"role_in": roles}, {"role_in": ("functional_benefic", "yogakaraka")})
    roles.append("malefic")
    assert outcome.normalized_inputs["role_in"] == ("functional_benefic", "yogakaraka")


@pytest.mark.parametrize("house", [1, 6, 12])
def test_strict_house_values_are_accepted(house):
    assert_valid("PLANET_IN_HOUSE", {"planet": "Mars", "house": house}, {"house": house, "planet": "Mars"})


class HouseEnum(IntEnum):
    SEVEN = 7


class CustomNumeric:
    def __int__(self):
        return 7


@pytest.mark.parametrize(
    "house,code",
    [
        (0, "invalid_value"), (-1, "invalid_value"), (13, "invalid_value"), (99, "invalid_value"),
        (True, "invalid_type"), (False, "invalid_type"), (7.0, "invalid_type"), ("7", "invalid_type"),
        ("seven", "invalid_type"), (None, "invalid_type"), (Decimal("7"), "invalid_type"),
        (HouseEnum.SEVEN, "invalid_type"), (CustomNumeric(), "invalid_type"),
    ],
)
def test_house_values_are_never_coerced(house, code):
    assert_invalid("PLANET_IN_HOUSE", {"planet": "Mars", "house": house}, code)


def test_canonical_catalog_is_exact():
    assert CANONICAL_PLANETS == PLANETS


@pytest.mark.parametrize("planet", PLANETS)
def test_all_nine_planets_are_accepted_canonically(planet):
    assert_valid("PLANET_EXALTED", {"planet": planet}, {"planet": planet})


@pytest.mark.parametrize(
    "supplied,canonical",
    [("sun", "Sun"), ("MOON", "Moon"), ("mArS", "Mars"), (" mercury ", "Mercury"),
     ("JUPITER", "Jupiter"), ("venus", "Venus"), (" SATURN ", "Saturn"),
     ("rahu", "Rahu"), (" KETU ", "Ketu")],
)
def test_planet_case_and_outer_whitespace_normalize_only_to_catalog(supplied, canonical):
    assert_valid("PLANET_EXALTED", {"planet": supplied}, {"planet": canonical})


@pytest.mark.parametrize(
    "planet,code",
    [("", "invalid_value"), ("   ", "invalid_value"), ("Pluto", "invalid_value"),
     ("Ascendant", "invalid_value"), ("Lagna", "invalid_value"), ("Ma", "invalid_value"),
     ("Sūrya", "invalid_value"), (7, "invalid_type"), (True, "invalid_type"),
     (None, "invalid_type"), (object(), "invalid_type")],
)
def test_unknown_alias_transliteration_and_nonstring_planets_are_rejected(planet, code):
    assert_invalid("PLANET_EXALTED", {"planet": planet}, code)


def test_valid_catalog_planet_does_not_require_astrostate_membership():
    assert_valid("PLANET_EXALTED", {"planet": "Ketu"}, {"planet": "Ketu"})


def test_aspect_empty_each_filter_and_all_filters_are_canonical():
    assert_valid("ASPECT", {}, {})
    assert_valid("ASPECT", {"from_house": 1}, {"from_house": 1})
    assert_valid("ASPECT", {"to_house": 12}, {"to_house": 12})
    assert_valid("ASPECT", {"from_planet": "mars"}, {"from_planet": "Mars"})
    assert_valid("ASPECT", {"to_planet": " moon "}, {"to_planet": "Moon"})
    supplied = {"to_planet": "MOON", "to_house": 10, "from_planet": "mars", "from_house": 1}
    assert_valid("ASPECT", supplied, {"from_house": 1, "from_planet": "Mars", "to_house": 10, "to_planet": "Moon"})


def test_aspect_alias_and_canonical_share_schema_and_normalization_identity():
    registry = get_production_registry()
    assert registry.lookup("ASPECT").parameter_schema is registry.lookup("ASPECT_EXISTS").parameter_schema
    alias = validate_predicate_parameters("ASPECT", {"from_planet": " mars "})
    canonical = validate_predicate_parameters("ASPECT_EXISTS", {"from_planet": "MARS"})
    assert alias.normalized_inputs == canonical.normalized_inputs
    assert alias.issues == canonical.issues == ()


def test_aspect_omission_differs_from_explicit_none_and_unknown_filter():
    assert_valid("ASPECT", {}, {})
    assert_invalid("ASPECT", {"from_house": None}, "invalid_type")
    assert_invalid("ASPECT", {"from_huose": 1}, "unknown_parameter")


def test_aspect_validation_does_not_require_chart_capability():
    assert_valid("ASPECT", {"from_planet": "Mars"}, {"from_planet": "Mars"})


def test_functional_role_vocabulary_is_exact_and_source_backed():
    assert FUNCTIONAL_ROLE_VALUES == ROLES
    for role in ROLES:
        assert_valid("FUNCTIONAL_ROLE", {"role_in": [role]}, {"role_in": (role,)})


class ArbitraryIterable:
    def __iter__(self):
        return iter(("benefic",))


def test_role_list_and_tuple_sort_deterministically_without_rewriting_literals():
    expected = {"role_in": ("benefic", "functional_malefic", "malefic", "yogakaraka")}
    assert_valid("FUNCTIONAL_ROLE", {"role_in": ["malefic", "benefic", "yogakaraka", "functional_malefic"]}, expected)
    assert_valid("FUNCTIONAL_ROLE", {"role_in": ("yogakaraka", "malefic", "functional_malefic", "benefic")}, expected)
    assert expected["role_in"][0] == "benefic"
    assert "functional_benefic" not in expected["role_in"]


@pytest.mark.parametrize(
    "value,code",
    [(None, "invalid_type"), ([], "invalid_value"), ((), "invalid_value"),
     ("benefic", "invalid_type"), ({"benefic": True}, "invalid_type"),
     ({"benefic"}, "invalid_type"), (frozenset({"benefic"}), "invalid_type"),
     ((item for item in ["benefic"]), "invalid_type"), (iter(["benefic"]), "invalid_type"),
     (ArbitraryIterable(), "invalid_type"), (7, "invalid_type")],
)
def test_role_container_policy_is_strict(value, code):
    assert_invalid("FUNCTIONAL_ROLE", {"role_in": value}, code)


@pytest.mark.parametrize(
    "value,code",
    [(["benefic", "benefic"], "duplicate_value"), (["unknown"], "invalid_value"),
     (["Benefic"], "invalid_value"), ([" benefic"], "invalid_value"),
     (["benefic", 1], "invalid_type")],
)
def test_role_items_are_exact_unique_strings(value, code):
    assert_invalid("FUNCTIONAL_ROLE", {"role_in": value}, code)


def test_functional_role_validation_does_not_compute_roles_or_accept_context_parameter(monkeypatch):
    import systems.Parasara.engine.enrichments.functional_roles as roles_module

    monkeypatch.setattr(roles_module, "compute_functional_roles", lambda *_: (_ for _ in ()).throw(AssertionError("computed")))
    assert_valid("FUNCTIONAL_ROLE", {"role_in": ["benefic"]}, {"role_in": ("benefic",)})
    assert_invalid("FUNCTIONAL_ROLE", {"role_in": ["benefic"], "context.planets": ["Mars"]}, "unknown_parameter")


@pytest.mark.parametrize(
    "predicate_id,valid",
    [
        ("PLANET_IN_HOUSE", {"planet": "mars", "house": 1}),
        ("HOUSE_OCCUPANT", {"house": 12, "planet": "ketu"}),
        ("PLANET_EXALTED", {"planet": "sun"}),
    ],
)
def test_required_predicates_accept_exact_canonical_inputs(predicate_id, valid):
    outcome = validate_predicate_parameters(predicate_id, valid)
    assert outcome.valid


@pytest.mark.parametrize(
    "predicate_id,missing_one,missing_all",
    [
        ("PLANET_IN_HOUSE", {"planet": "Mars"}, {}),
        ("HOUSE_OCCUPANT", {"house": 1}, {}),
        ("PLANET_EXALTED", {}, {}),
    ],
)
def test_required_predicates_reject_missing_keys(predicate_id, missing_one, missing_all):
    one = validate_predicate_parameters(predicate_id, missing_one)
    assert not one.valid and all(issue.code is ParameterIssueCode.MISSING_REQUIRED for issue in one.issues)
    all_missing = validate_predicate_parameters(predicate_id, missing_all)
    assert not all_missing.valid and all(issue.code is ParameterIssueCode.MISSING_REQUIRED for issue in all_missing.issues)


def test_missing_required_issue_order_uses_each_distinct_schema_order():
    assert [i.parameter_name for i in validate_predicate_parameters("PLANET_IN_HOUSE", {}).issues] == ["planet", "house"]
    assert [i.parameter_name for i in validate_predicate_parameters("HOUSE_OCCUPANT", {}).issues] == ["house", "planet"]


def test_required_predicates_reject_unknown_and_wrong_values():
    assert_invalid("PLANET_IN_HOUSE", {"planet": "Mars", "house": 1, "extra": True}, "unknown_parameter")
    assert_invalid("HOUSE_OCCUPANT", {"house": 0, "planet": "Pluto"}, "invalid_value", "invalid_value")
    assert_invalid("PLANET_EXALTED", {"planet": None}, "invalid_type")


def test_synthetic_registered_parameter_alias_normalizes_and_conflicts_deterministically():
    spec = ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True, aliases=("body",))
    schema = synthetic_schema(spec)
    definition = synthetic_definition(schema)
    assert schema.validate({"body": "mars"}).normalized_inputs == FrozenMapping({"planet": "Mars"})
    conflict = schema.validate({"planet": "Mars", "body": "Moon"})
    assert tuple(issue.code for issue in conflict.issues) == (ParameterIssueCode.CONFLICTING_ALIAS,)
    assert definition.parameter_schema is schema


def test_alias_normalization_precedes_unknown_reporting_and_default_is_explicit():
    schema = ParameterSchema(
        predicate_id="SYNTHETIC",
        schema_version="1.0.0",
        specifications=(
            ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True, aliases=("body",)),
            ParameterSpec(name="house", kind=ParameterKind.HOUSE, required=False, has_default=True, default=7),
        ),
    )
    assert schema.validate({"body": "mars"}).normalized_inputs == FrozenMapping({"planet": "Mars", "house": 7})
    outcome = schema.validate({"body": "mars", "unknown": True})
    assert tuple(issue.code for issue in outcome.issues) == (ParameterIssueCode.UNKNOWN_PARAMETER,)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": "Planet", "kind": ParameterKind.PLANET, "required": True},
        {"name": "planet", "kind": "unsupported", "required": True},
        {"name": "planet", "kind": ParameterKind.PLANET, "required": 1},
        {"name": "planet", "kind": ParameterKind.PLANET, "required": True, "aliases": ["body"]},
        {"name": "planet", "kind": ParameterKind.PLANET, "required": True, "aliases": ("planet",)},
        {"name": "planet", "kind": ParameterKind.PLANET, "required": True, "aliases": ("z", "a")},
        {"name": "planet", "kind": ParameterKind.PLANET, "required": True, "allowed_values": ("Mars",)},
        {"name": "role_in", "kind": ParameterKind.ROLE_COLLECTION, "required": True},
        {"name": "role_in", "kind": ParameterKind.ROLE_COLLECTION, "required": True, "allowed_values": ("z", "a")},
        {"name": "house", "kind": ParameterKind.HOUSE, "required": True, "has_default": True, "default": 7},
        {"name": "house", "kind": ParameterKind.HOUSE, "required": False, "default": 7},
        {"name": "house", "kind": ParameterKind.HOUSE, "required": False, "has_default": True, "default": 7.0},
    ],
)
def test_invalid_spec_kinds_constraints_ordering_and_defaults_are_rejected(kwargs):
    with pytest.raises(ParameterSchemaError):
        ParameterSpec(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"predicate_id": "AND", "schema_version": "1.0.0", "specifications": ()},
        {"predicate_id": "synthetic", "schema_version": "1.0.0", "specifications": ()},
        {"predicate_id": "SYNTHETIC", "schema_version": "1", "specifications": ()},
        {"predicate_id": "SYNTHETIC", "schema_version": "1.0.0", "specifications": []},
    ],
)
def test_invalid_schema_identity_version_and_container_are_rejected(kwargs):
    with pytest.raises(ParameterSchemaError):
        ParameterSchema(**kwargs)


@pytest.mark.parametrize(
    "specs",
    [
        (ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True), ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True)),
        (ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True, aliases=("body",)), ParameterSpec(name="house", kind=ParameterKind.HOUSE, required=True, aliases=("body",))),
        (ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True, aliases=("house",)), ParameterSpec(name="house", kind=ParameterKind.HOUSE, required=True)),
    ],
)
def test_schema_rejects_duplicate_names_alias_alias_and_alias_canonical_collisions(specs):
    with pytest.raises(ParameterSchemaError):
        synthetic_schema(*specs)


def test_production_has_zero_parameter_aliases():
    for definition in get_production_registry().canonical_definitions():
        assert all(spec.aliases == () for spec in definition.parameter_schema.specifications)


def test_definition_rejects_wrong_schema_type_identity_and_version():
    with pytest.raises(PredicateDefinitionError):
        replace(get_production_registry().lookup("PLANET_EXALTED"), parameter_schema=FrozenMapping())
    wrong_id = ParameterSchema(predicate_id="OTHER", schema_version="1.0.0", specifications=(ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True),))
    with pytest.raises(PredicateDefinitionError):
        replace(get_production_registry().lookup("PLANET_EXALTED"), parameter_schema=wrong_id)
    wrong_version = ParameterSchema(predicate_id="PLANET_EXALTED", schema_version="2.0.0", specifications=(ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True),))
    with pytest.raises(PredicateDefinitionError):
        replace(get_production_registry().lookup("PLANET_EXALTED"), parameter_schema=wrong_version)


def test_invalid_schema_registration_attempt_leaves_registry_unchanged():
    registry = PredicateRegistry()
    before = registry.canonical_ids()
    with pytest.raises((ParameterSchemaError, PredicateDefinitionError)):
        synthetic_definition(synthetic_schema(
            ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True),
            ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True),
        ))
    assert registry.canonical_ids() == before


def test_schema_metadata_is_frozen_canonical_and_fingerprint_sensitive():
    production = get_production_registry()
    schema = production.lookup("PLANET_EXALTED").parameter_schema
    metadata = schema.metadata()
    assert isinstance(metadata, FrozenMapping)
    assert metadata == schema.metadata()
    with pytest.raises(TypeError):
        metadata["schema_version"] = "changed"

    changed_schema = ParameterSchema(
        predicate_id="PLANET_EXALTED",
        schema_version="1.0.0",
        specifications=(ParameterSpec(name="planet", kind=ParameterKind.PLANET, required=True, aliases=("body",)),),
    )
    changed = replace(production.lookup("PLANET_EXALTED"), parameter_schema=changed_schema)
    isolated = PredicateRegistry()
    for item in production.canonical_definitions():
        isolated.register(changed if item.predicate_id == "PLANET_EXALTED" else item)
    isolated.finalize()
    assert predicate_registry_fingerprint_bytes(isolated) != predicate_registry_fingerprint_bytes(production)


def test_safe_issue_and_outcome_exact_contracts():
    outcome = assert_invalid("PLANET_IN_HOUSE", {"planet": "TOP-SECRET", "house": 99}, "invalid_value", "invalid_value")
    for issue in outcome.issues:
        assert issue.predicate_id == "PLANET_IN_HOUSE"
        assert issue.expected
        assert issue.path.startswith("$.parameters.")
    text = json.dumps([dict(issue.details()) for issue in outcome.issues], sort_keys=True)
    assert "TOP-SECRET" not in text
    assert "99" not in text
    assert "0x" not in text


def test_invalid_parameter_error_adapter_is_exact_safe_and_immutable():
    supplied = {"planet": "TOP-SECRET-PLANET", "house": object(), "api_key": "SECRET"}
    outcome = validate_predicate_parameters("PLANET_IN_HOUSE", supplied)
    error = invalid_parameters_error("PLANET_IN_HOUSE", outcome)
    assert isinstance(error, PredicateError)
    assert error.code == "invalid_parameters"
    assert error.message == "Predicate parameters are invalid."
    assert error.predicate_id == "PLANET_IN_HOUSE"
    assert error.recoverable is True
    assert isinstance(error.details, FrozenMapping)
    assert isinstance(error.details["issues"], tuple)
    payload = predicate_error_json_bytes(error)
    assert b"TOP-SECRET" not in payload
    assert b"SECRET" not in payload
    assert b"0x" not in payload
    with pytest.raises(TypeError):
        error.details["issues"] = ()


def test_invalid_parameter_adapter_rejects_success_and_wrong_predicate():
    success = validate_predicate_parameters("PLANET_EXALTED", {"planet": "Sun"})
    with pytest.raises(ParameterSchemaError):
        invalid_parameters_error("PLANET_EXALTED", success)
    failure = validate_predicate_parameters("PLANET_EXALTED", {})
    with pytest.raises(ParameterSchemaError):
        invalid_parameters_error("PLANET_IN_HOUSE", failure)


def test_validation_constructs_neither_result_nor_handler_output(monkeypatch):
    import systems.Parasara.engine.rules.models as models

    monkeypatch.setattr(models, "PredicateResult", lambda *a, **k: (_ for _ in ()).throw(AssertionError("result constructed")))
    assert validate_predicate_parameters("PLANET_IN_HOUSE", {"planet": "Mars", "house": 1}).valid


def test_normalized_input_and_safe_error_are_stable_in_a_fresh_process():
    valid = validate_predicate_parameters("FUNCTIONAL_ROLE", {"role_in": ["yogakaraka", "benefic"]})
    invalid = validate_predicate_parameters("PLANET_IN_HOUSE", {"planet": "Pluto", "house": 0})
    error = invalid_parameters_error("PLANET_IN_HOUSE", invalid)
    valid_bytes = canonical_json_bytes(valid.normalized_inputs)
    error_bytes = predicate_error_json_bytes(error)
    script = """
from systems.Parasara.engine.rules.canonical import canonical_json_bytes, predicate_error_json_bytes
from systems.Parasara.engine.rules.parameters import invalid_parameters_error, validate_predicate_parameters
valid = validate_predicate_parameters('FUNCTIONAL_ROLE', {'role_in': ['yogakaraka', 'benefic']})
invalid = validate_predicate_parameters('PLANET_IN_HOUSE', {'planet': 'Pluto', 'house': 0})
print(canonical_json_bytes(valid.normalized_inputs).hex())
print(predicate_error_json_bytes(invalid_parameters_error('PLANET_IN_HOUSE', invalid)).hex())
"""
    root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(root)
    completed = subprocess.run(
        [sys.executable, "-c", script], cwd=root, env=env, check=True, capture_output=True, text=True
    )
    valid_hex, error_hex = completed.stdout.splitlines()
    assert valid_hex == valid_bytes.hex()
    assert error_hex == error_bytes.hex()
    assert hashlib.sha256(valid_bytes).hexdigest() == "0bb07e0f35213a2bdfb1e9629ef74b14417c68078b2e5c2d1532003c5f09ec86"
    assert hashlib.sha256(error_bytes).hexdigest() == "24f2f82219303f5b18c388b6413af22a6ab5f26c2a5ba7757b2babd96ba835ad"
