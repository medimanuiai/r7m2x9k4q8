"""WP04 contract for predicate definitions, registry lifecycle, and bootstrap."""

from dataclasses import fields
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from systems.Parasara.engine.rules.canonical import FrozenMapping
from systems.Parasara.engine.rules.capabilities import CapabilityRequirement
from systems.Parasara.engine.rules.parameters import (
    FUNCTIONAL_ROLE_VALUES,
    ParameterKind,
    ParameterSchema,
    ParameterSpec,
)
from systems.Parasara.engine.rules.registry import (
    CostClass,
    PredicateDefinition,
    PredicateDefinitionError,
    PredicateRegistry,
    PredicateRegistryError,
    PredicateRegistryFrozenError,
    bootstrap_production_registry,
    get_production_registry,
    predicate_registry_fingerprint_bytes,
)


EXPECTED_FIELDS = (
    "predicate_id",
    "predicate_version",
    "description",
    "parameter_schema",
    "required_capabilities",
    "cacheable",
    "deterministic",
    "cost_class",
    "system_scope",
    "deprecated",
    "replacement",
    "aliases",
    "handler",
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


def _handler(params, astro, context):
    return params, astro, context


def capability_requirement(capability_id="planets.normalized"):
    return CapabilityRequirement(
        capability_id=capability_id,
        capability_version="1.0.0",
        required=True,
        when_parameters_present=(),
    )


def definition(predicate_id="TEST_PREDICATE", **changes):
    version = changes.get("predicate_version", "1.0.0")
    schema_id = predicate_id if isinstance(predicate_id, str) and re.fullmatch(r"[A-Z][A-Z0-9_]*", predicate_id) and predicate_id not in {"AND", "OR", "NOT"} else "TEST_PREDICATE"
    schema_version = version if isinstance(version, str) and re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version) else "1.0.0"
    values = {
        "predicate_id": predicate_id,
        "predicate_version": "1.0.0",
        "description": "A factual test predicate.",
        "parameter_schema": ParameterSchema(
            predicate_id=schema_id,
            schema_version=schema_version,
            specifications=(),
        ),
        "required_capabilities": (capability_requirement(),),
        "cacheable": True,
        "deterministic": True,
        "cost_class": CostClass.LOW,
        "system_scope": "parasara",
        "deprecated": False,
        "replacement": None,
        "aliases": (),
        "handler": _handler,
    }
    values.update(changes)
    return PredicateDefinition(**values)


@pytest.mark.parametrize(
    "missing",
    [
        "predicate_id",
        "predicate_version",
        "description",
        "parameter_schema",
        "required_capabilities",
        "cacheable",
        "deterministic",
        "cost_class",
        "system_scope",
        "handler",
    ],
)
def test_every_required_definition_field_is_enforced(missing):
    values = {
        "predicate_id": "TEST_PREDICATE",
        "predicate_version": "1.0.0",
        "description": "A factual test predicate.",
        "parameter_schema": ParameterSchema(
            predicate_id="TEST_PREDICATE", schema_version="1.0.0", specifications=()
        ),
        "required_capabilities": (),
        "cacheable": True,
        "deterministic": True,
        "cost_class": CostClass.LOW,
        "system_scope": "parasara",
        "handler": _handler,
    }
    values.pop(missing)
    with pytest.raises((TypeError, PredicateDefinitionError)):
        PredicateDefinition(**values)


def test_unknown_definition_field_is_rejected():
    with pytest.raises(TypeError):
        PredicateDefinition(
            predicate_id="TEST_PREDICATE",
            predicate_version="1.0.0",
            description="A factual test predicate.",
            parameter_schema=ParameterSchema(
                predicate_id="TEST_PREDICATE", schema_version="1.0.0", specifications=()
            ),
            required_capabilities=(),
            cacheable=True,
            deterministic=True,
            cost_class=CostClass.LOW,
            system_scope="parasara",
            handler=_handler,
            owner="not-a-locked-field",
        )


def test_definition_has_exact_locked_fields_and_is_frozen():
    item = definition()
    assert tuple(field.name for field in fields(PredicateDefinition)) == EXPECTED_FIELDS
    with pytest.raises((AttributeError, TypeError)):
        item.description = "changed"


@pytest.mark.parametrize(
    "changes",
    [
        {"predicate_id": ""},
        {"predicate_id": " TEST"},
        {"predicate_id": "test"},
        {"predicate_id": "1TEST"},
        {"predicate_id": "TEST-ID"},
        {"predicate_id": "AND"},
        {"predicate_id": "OR"},
        {"predicate_id": "NOT"},
        {"description": ""},
        {"description": " padded "},
        {"parameter_schema": {}},
        {"required_capabilities": ["test_facts"]},
        {"required_capabilities": ("",)},
        {"required_capabilities": ("facts", "facts")},
        {"required_capabilities": ("z_facts", "a_facts")},
        {"cacheable": 1},
        {"deterministic": 1},
        {"cacheable": True, "deterministic": False},
        {"cost_class": "fast"},
        {"system_scope": "Parasara"},
        {"system_scope": "parasara-scope"},
        {"deprecated": 0},
        {"replacement": "TEST_PREDICATE"},
        {"replacement": "test_other"},
        {"aliases": ["TEST_ALIAS"]},
        {"aliases": ("TEST_PREDICATE",)},
        {"aliases": ("AND",)},
        {"aliases": ("TEST_ALIAS", "TEST_ALIAS")},
        {"handler": object()},
    ],
)
def test_definition_rejects_invalid_required_metadata(changes):
    with pytest.raises(PredicateDefinitionError):
        definition(**changes)


@pytest.mark.parametrize("version", ["0.0.0", "1.0.0", "10.20.300"])
def test_semver_accepts_stage01_forms(version):
    assert definition(predicate_version=version).predicate_version == version


@pytest.mark.parametrize(
    "version",
    ["", "1", "1.0", "01.0.0", "1.01.0", "1.0.01", "v1.0.0", "1.0.0-alpha", "1.0.0+build", 1, None],
)
def test_semver_rejects_non_stage01_forms(version):
    with pytest.raises(PredicateDefinitionError):
        definition(predicate_version=version)


def test_nested_metadata_is_immutable_and_caller_isolated():
    source = ["benefic"]
    schema = ParameterSchema(
        predicate_id="TEST_PREDICATE",
        schema_version="1.0.0",
        specifications=(ParameterSpec(
            name="role_in",
            kind=ParameterKind.ROLE_COLLECTION,
            required=False,
            allowed_values=FUNCTIONAL_ROLE_VALUES,
            has_default=True,
            default=source,
        ),),
    )
    item = definition(parameter_schema=schema, aliases=("TEST_ALIAS",))
    source.append("malefic")
    assert item.parameter_schema.specifications[0].default == ("benefic",)
    assert item.aliases == ("TEST_ALIAS",)
    with pytest.raises((AttributeError, TypeError)):
        item.parameter_schema.schema_version = "changed"


def test_registration_duplicate_collision_and_invalid_attempts_are_atomic():
    registry = PredicateRegistry()
    registry.register(definition(aliases=("TEST_ALIAS",)))
    before = registry.canonical_ids()
    with pytest.raises(PredicateRegistryError):
        registry.register(definition())
    with pytest.raises(PredicateRegistryError):
        registry.register(definition("TEST_ALIAS"))
    with pytest.raises(PredicateRegistryError):
        registry.register(definition("OTHER", aliases=("TEST_ALIAS",), handler=lambda *_: None))
    with pytest.raises(PredicateRegistryError):
        registry.register(definition("OTHER"))
    assert registry.canonical_ids() == before


def test_registry_build_finalize_lookup_and_readiness_contract():
    registry = PredicateRegistry()
    registry.register(definition(aliases=("TEST_ALIAS",)))
    assert registry.is_ready is False
    assert registry.is_frozen is False
    registry.finalize()
    assert registry.is_ready is True
    assert registry.is_frozen is True
    assert registry.canonical_ids() == ("TEST_PREDICATE",)
    assert registry.exposed_ids() == ("TEST_ALIAS", "TEST_PREDICATE")
    assert registry.lookup(" test_alias ") is registry.lookup("TEST_PREDICATE")
    assert registry.handler("test_alias") is _handler
    assert registry.lookup("UNKNOWN_PREDICATE") is None


@pytest.mark.parametrize("value", [None, 1, "", "   ", "bad-id", "ÅSPECT"])
def test_registry_lookup_rejects_non_string_blank_or_malformed_values(value):
    registry = PredicateRegistry()
    registry.register(definition())
    registry.finalize()
    with pytest.raises(PredicateRegistryError):
        registry.lookup(value)


@pytest.mark.parametrize("method,args", [("register", (definition("OTHER", handler=lambda *_: None),)), ("remove", ("TEST_PREDICATE",)), ("replace", (definition(),)), ("reset", ())])
def test_all_mutation_after_freeze_is_rejected(method, args):
    registry = PredicateRegistry()
    registry.register(definition())
    registry.finalize()
    with pytest.raises(PredicateRegistryFrozenError):
        getattr(registry, method)(*args)


def test_finalization_rejects_missing_replacement_and_cycles_without_readiness():
    missing = PredicateRegistry()
    missing.register(definition(replacement="OTHER"))
    with pytest.raises(PredicateRegistryError):
        missing.finalize()
    assert missing.is_ready is False

    cycle = PredicateRegistry()
    cycle.register(definition("FIRST", replacement="SECOND"))
    cycle.register(definition("SECOND", replacement="FIRST", handler=lambda *_: None))
    with pytest.raises(PredicateRegistryError):
        cycle.finalize()
    assert cycle.is_ready is False

    alias_target = PredicateRegistry()
    alias_target.register(definition("FIRST", replacement="SECOND_ALIAS"))
    alias_target.register(
        definition("SECOND", aliases=("SECOND_ALIAS",), handler=lambda *_: None)
    )
    with pytest.raises(PredicateRegistryError):
        alias_target.finalize()


def test_registry_snapshots_do_not_expose_mutable_backing_state():
    registry = PredicateRegistry()
    registry.register(definition())
    registry.finalize()
    assert isinstance(registry.metadata_snapshot(), FrozenMapping)
    assert isinstance(registry.canonical_definitions(), tuple)
    assert not hasattr(registry, "_definitions")
    with pytest.raises(TypeError):
        registry.metadata_snapshot()["TEST_PREDICATE"] = FrozenMapping()


def test_enumeration_is_lexicographic_independent_of_registration_order():
    first = PredicateRegistry()
    first.register(definition("ZETA"))
    first.register(definition("ALPHA", aliases=("ALPHA_ALIAS",), handler=lambda *_: None))
    first.finalize()
    second = PredicateRegistry()
    second.register(definition("ALPHA", aliases=("ALPHA_ALIAS",), handler=lambda *_: None))
    second.register(definition("ZETA", handler=lambda *_: None))
    second.finalize()
    assert first.canonical_ids() == second.canonical_ids() == ("ALPHA", "ZETA")
    assert first.exposed_ids() == second.exposed_ids() == ("ALPHA", "ALPHA_ALIAS", "ZETA")


def test_production_inventory_alias_identity_and_metadata_are_exact():
    registry = get_production_registry()
    assert registry is bootstrap_production_registry()
    assert registry.canonical_ids() == CANONICAL_IDS
    assert registry.exposed_ids() == EXPOSED_IDS
    assert len({id(item.handler) for item in registry.canonical_definitions()}) == 5
    aspect = registry.lookup("ASPECT")
    assert aspect is registry.lookup("ASPECT_EXISTS")
    assert aspect.predicate_id == "ASPECT_EXISTS"
    assert aspect.predicate_version == "1.0.0"
    assert aspect.aliases == ("ASPECT",)
    assert registry.lookup("PLANET_IN_HOUSE") is not registry.lookup("HOUSE_OCCUPANT")
    assert "HOUSE_LORDS_COMBINATION" not in registry.exposed_ids()
    assert not ({"AND", "OR", "NOT"} & set(registry.exposed_ids()))


def test_all_production_metadata_is_complete_explicit_and_immutable():
    registry = get_production_registry()
    for item in registry.canonical_definitions():
        assert item.predicate_version == "1.0.0"
        assert item.description
        assert isinstance(item.parameter_schema, ParameterSchema)
        assert item.required_capabilities
        assert item.cacheable is True
        assert item.deterministic is True
        assert item.cost_class in tuple(CostClass)
        assert item.system_scope == "parasara"
        assert item.deprecated is False
        assert item.replacement is None


def test_production_parameter_and_capability_inventory_is_executable_and_exact():
    registry = get_production_registry()
    aspect = registry.lookup("ASPECT_EXISTS")
    assert tuple(spec.name for spec in aspect.parameter_schema.specifications) == (
        "from_house",
        "to_house",
        "from_planet",
        "to_planet",
    )
    assert all(not spec.required for spec in aspect.parameter_schema.specifications)
    assert tuple(item.capability_id for item in aspect.required_capabilities) == (
        "aspects.whole_sign_graph",
    )

    planet_house = registry.lookup("PLANET_IN_HOUSE")
    occupant = registry.lookup("HOUSE_OCCUPANT")
    assert tuple(spec.name for spec in planet_house.parameter_schema.specifications) == ("planet", "house")
    assert tuple(spec.name for spec in occupant.parameter_schema.specifications) == ("house", "planet")
    assert all(spec.required for spec in planet_house.parameter_schema.specifications + occupant.parameter_schema.specifications)
    assert tuple(item.capability_id for item in planet_house.required_capabilities) == tuple(
        item.capability_id for item in occupant.required_capabilities
    ) == ("planets.house_placement", "planets.normalized")

    roles = registry.lookup("FUNCTIONAL_ROLE")
    assert tuple(spec.name for spec in roles.parameter_schema.specifications) == ("role_in",)
    assert roles.parameter_schema.specifications[0].required is True
    assert roles.parameter_schema.specifications[0].has_default is False
    assert tuple(item.capability_id for item in roles.required_capabilities) == (
        "chart.lagna", "planets.normalized", "roles.functional"
    )

    exalted = registry.lookup("PLANET_EXALTED")
    assert tuple(spec.name for spec in exalted.parameter_schema.specifications) == ("planet",)
    assert tuple(item.capability_id for item in exalted.required_capabilities) == (
        "dignity.exaltation_facts", "planets.normalized"
    )


def test_registry_handlers_are_the_canonical_typed_implementations():
    from systems.Parasara.engine.rules import canonical_predicates
    from systems.Parasara.engine.rules.planet_in_house import evaluate_planet_in_house

    registry = get_production_registry()
    assert registry.handler("ASPECT") is canonical_predicates.evaluate_aspect_exists
    assert registry.handler("ASPECT_EXISTS") is canonical_predicates.evaluate_aspect_exists
    assert registry.handler("FUNCTIONAL_ROLE") is canonical_predicates.evaluate_functional_role
    assert registry.handler("HOUSE_OCCUPANT") is canonical_predicates.evaluate_house_occupant
    assert registry.handler("PLANET_EXALTED") is canonical_predicates.evaluate_planet_exalted
    assert registry.handler("PLANET_IN_HOUSE") is evaluate_planet_in_house


def test_isolated_registry_cannot_change_production_inventory():
    production = get_production_registry()
    before = production.exposed_ids()
    isolated = PredicateRegistry()
    isolated.register(definition("ISOLATED"))
    isolated.finalize()
    assert isolated.lookup("ISOLATED") is not None
    assert production.exposed_ids() == before
    assert production.lookup("ISOLATED") is None


def test_fingerprint_is_repeatable_complete_and_free_of_callable_repr():
    first = predicate_registry_fingerprint_bytes()
    second = predicate_registry_fingerprint_bytes()
    assert first == second
    decoded = json.loads(first)
    assert decoded["canonical_ids"] == list(CANONICAL_IDS)
    assert decoded["exposed_ids"] == list(EXPOSED_IDS)
    assert decoded["is_frozen"] is True
    assert decoded["is_ready"] is True
    assert "0x" not in first.decode("utf-8")
    assert len(hashlib.sha256(first).hexdigest()) == 64


def test_fresh_process_bootstrap_needs_no_prior_predicate_or_yoga_import():
    root = Path(__file__).resolve().parents[2]
    script = (
        "import hashlib; "
        "from systems.Parasara.engine.rules.registry import predicate_registry_fingerprint_bytes; "
        "b=predicate_registry_fingerprint_bytes(); "
        "print(hashlib.sha256(b).hexdigest()); print(b.decode('utf-8'))"
    )
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(root)
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    digest, payload = completed.stdout.splitlines()
    current = predicate_registry_fingerprint_bytes()
    assert digest == hashlib.sha256(current).hexdigest()
    assert payload == current.decode("utf-8")


@pytest.mark.parametrize(
    "prefix",
    [
        "",
        "import systems.Parasara.engine.rules.canonical_predicates; ",
        "import systems.Parasara.engine.enrichments.yoga_engine; ",
    ],
)
def test_fresh_process_import_order_does_not_change_registry_fingerprint(prefix):
    root = Path(__file__).resolve().parents[2]
    script = (
        prefix
        + "import hashlib; "
        + "from systems.Parasara.engine.rules.registry import predicate_registry_fingerprint_bytes; "
        + "print(hashlib.sha256(predicate_registry_fingerprint_bytes()).hexdigest())"
    )
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(root)
    completed = subprocess.run(
        [sys.executable, "-c", script], cwd=root, env=env, check=True, capture_output=True, text=True
    )
    assert completed.stdout.strip() == hashlib.sha256(predicate_registry_fingerprint_bytes()).hexdigest()


def test_fresh_process_evaluates_all_six_ids_through_typed_boundary():
    root = Path(__file__).resolve().parents[2]
    script = """
import json
import sys
from types import SimpleNamespace
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext, prepare_predicate_state
source = SimpleNamespace(planets=[], lagna_sign=None, enrichments={}, derived=None, metadata={}, diagnostics={})
outcome = prepare_predicate_state(source)
assert outcome.succeeded and outcome.state is not None
ids = ['ASPECT', 'ASPECT_EXISTS', 'FUNCTIONAL_ROLE', 'HOUSE_OCCUPANT', 'PLANET_EXALTED', 'PLANET_IN_HOUSE']
evaluator = PredicateEvaluator()
context = PredicateEvaluationContext()
results = [evaluator.evaluate(item, {}, outcome.state, context).predicate_id for item in ids]
print(json.dumps(results, separators=(',', ':')))
"""
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(root)
    completed = subprocess.run(
        [sys.executable, "-c", script], cwd=root, env=env, check=True, capture_output=True, text=True
    )
    assert json.loads(completed.stdout) == [
        "ASPECT_EXISTS",
        "ASPECT_EXISTS",
        "FUNCTIONAL_ROLE",
        "HOUSE_OCCUPANT",
        "PLANET_EXALTED",
        "PLANET_IN_HOUSE",
    ]


def test_failed_bootstrap_subprocess_publishes_no_partial_registry():
    root = Path(__file__).resolve().parents[2]
    script = """
import systems.Parasara.engine.rules.registry as registry
from systems.Parasara.engine.rules.capabilities import CapabilityRequirement
from systems.Parasara.engine.rules.parameters import ParameterSchema
def handler(*args): return None
item = registry.PredicateDefinition(predicate_id='ONE', predicate_version='1.0.0', description='One.', parameter_schema=ParameterSchema(predicate_id='ONE', schema_version='1.0.0', specifications=()), required_capabilities=(CapabilityRequirement(capability_id='planets.normalized', capability_version='1.0.0', required=True, when_parameters_present=()),), cacheable=True, deterministic=True, cost_class=registry.CostClass.LOW, system_scope='parasara', handler=handler)
registry._built_in_definitions = lambda: (item, item)
try:
    registry.bootstrap_production_registry()
except registry.PredicateRegistryError:
    pass
else:
    raise AssertionError('bootstrap unexpectedly succeeded')
assert registry._production_registry is None
assert registry._bootstrap_state == registry._BOOTSTRAP_FAILED
try:
    registry.bootstrap_production_registry()
except registry.PredicateRegistryError:
    print('failed-without-partial-publication')
else:
    raise AssertionError('failed bootstrap was not detected')
"""
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(root)
    completed = subprocess.run(
        [sys.executable, "-c", script], cwd=root, env=env, check=True, capture_output=True, text=True
    )
    assert completed.stdout.strip() == "failed-without-partial-publication"
