from dataclasses import FrozenInstanceError, replace
from types import SimpleNamespace

import pytest

from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.rules.canonical import FrozenMapping
from systems.Parasara.engine.rules.capabilities import (
    CapabilityCatalog,
    CapabilityCatalogMiss,
    CapabilityDefinition,
    CapabilityDefinitionError,
    CapabilityFactState,
    CapabilityReadiness,
    CapabilityRequirement,
    CapabilityRequirementError,
    ContentKind,
    EmptyPolicy,
    capability_catalog_fingerprint_sha256,
    capability_error,
    capability_fact_observation_json_bytes,
    get_production_capability_catalog,
    inspect_capability,
    capability_inspection_json_bytes,
    observe_capability_fact,
    validate_registry_capabilities,
)
from systems.Parasara.engine.rules.registry import (
    PredicateDefinition,
    PredicateRegistry,
    PredicateRegistryError,
    get_production_registry,
    predicate_registry_fingerprint_sha256,
)


CAPABILITIES = {
    "aspects.basic_conjunction_list": (ContentKind.COLLECTION, EmptyPolicy.READY_EMPTY),
    "aspects.whole_sign_graph": (ContentKind.GRAPH, EmptyPolicy.READY_EMPTY),
    "chart.lagna": (ContentKind.SCALAR, EmptyPolicy.EMPTY_NOT_READY),
    "dignity.exaltation_facts": (ContentKind.MAPPING, EmptyPolicy.READY_EMPTY),
    "planets.house_placement": (ContentKind.ENTITY_FIELDS, EmptyPolicy.EMPTY_NOT_READY),
    "planets.normalized": (ContentKind.COLLECTION, EmptyPolicy.EMPTY_NOT_READY),
    "roles.functional": (ContentKind.MAPPING, EmptyPolicy.READY_EMPTY),
}


def requirement(capability_id, version="1.0.0"):
    return CapabilityRequirement(
        capability_id=capability_id,
        capability_version=version,
        required=True,
        when_parameters_present=(),
    )


def astro(**changes):
    values = dict(
        metadata={},
        location=None,
        lagna_sign="Aries",
        planets=[PlanetState(name="Mars", sign="Aries", degree=1.0, house=1)],
        houses=[],
        enrichments={},
        derived=None,
    )
    values.update(changes)
    return AstroState(**values)


def test_production_catalog_has_exact_frozen_seven_definition_contract():
    catalog = get_production_capability_catalog()
    assert catalog.is_ready is True
    assert catalog.is_frozen is True
    assert catalog.capability_ids() == tuple(CAPABILITIES)
    assert len(catalog.definitions()) == 7
    for definition in catalog.definitions():
        kind, policy = CAPABILITIES[definition.capability_id]
        assert definition.capability_version == "1.0.0"
        assert definition.system_scope == "parasara"
        assert definition.content_kind is kind
        assert definition.empty_policy is policy
        assert type(definition.recoverable_when_missing) is bool
        with pytest.raises(FrozenInstanceError):
            definition.description = "changed"


@pytest.mark.parametrize(
    "change",
    [
        {"capability_id": "BAD"},
        {"capability_id": "single"},
        {"capability_id": "bad..id"},
        {"capability_version": "1.0"},
        {"description": " padded "},
        {"system_scope": "other"},
        {"recoverable_when_missing": 1},
    ],
)
def test_definition_rejects_invalid_identity_version_and_strict_fields(change):
    values = dict(
        capability_id="test.capability",
        capability_version="1.0.0",
        description="A factual test capability.",
        system_scope="parasara",
        content_kind=ContentKind.MAPPING,
        empty_policy=EmptyPolicy.READY_EMPTY,
        recoverable_when_missing=True,
    )
    values.update(change)
    with pytest.raises(CapabilityDefinitionError):
        CapabilityDefinition(**values)


def test_catalog_registration_is_atomic_sorted_and_frozen_with_typed_miss():
    catalog = CapabilityCatalog()
    definition = CapabilityDefinition(
        capability_id="zeta.fact",
        capability_version="1.0.0",
        description="A zeta fact.",
        system_scope="parasara",
        content_kind=ContentKind.SCALAR,
        empty_policy=EmptyPolicy.EMPTY_NOT_READY,
        recoverable_when_missing=True,
    )
    catalog.register(definition)
    before = catalog.definitions()
    with pytest.raises(Exception):
        catalog.register(definition)
    assert catalog.definitions() == before
    catalog.finalize()
    assert isinstance(catalog.lookup(" unknown.fact "), CapabilityCatalogMiss)
    assert catalog.lookup(" ZETA.FACT ") is definition
    with pytest.raises(Exception):
        catalog.register(definition)


def test_requirement_contract_is_typed_immutable_and_strict():
    item = CapabilityRequirement(
        capability_id="planets.normalized",
        capability_version="1.0.0",
        required=True,
        when_parameters_present=("planet",),
    )
    assert item.required is True
    with pytest.raises(FrozenInstanceError):
        item.required = False
    with pytest.raises(CapabilityRequirementError):
        replace(item, required=1)
    with pytest.raises(CapabilityRequirementError):
        replace(item, when_parameters_present=["planet"])


def test_production_requirement_inventory_is_exact_and_alias_shares_definition():
    registry = get_production_registry()
    expected = {
        "ASPECT_EXISTS": ("aspects.whole_sign_graph",),
        "FUNCTIONAL_ROLE": ("chart.lagna", "planets.normalized", "roles.functional"),
        "HOUSE_OCCUPANT": ("planets.house_placement", "planets.normalized"),
        "PLANET_EXALTED": ("dignity.exaltation_facts", "planets.normalized"),
        "PLANET_IN_HOUSE": ("planets.house_placement", "planets.normalized"),
    }
    assert registry.lookup("ASPECT") is registry.lookup("ASPECT_EXISTS")
    assert {
        item.predicate_id: tuple(req.capability_id for req in item.required_capabilities)
        for item in registry.canonical_definitions()
    } == expected
    assert validate_registry_capabilities(registry).compatible is True


def test_static_compatibility_rejects_unknown_version_duplicate_and_bad_condition():
    base = get_production_registry().lookup("PLANET_IN_HOUSE")
    assert base is not None
    with pytest.raises(Exception):
        replace(
            base,
            required_capabilities=(
                requirement("planets.normalized"),
                requirement("planets.normalized"),
            ),
        )
    bad_sets = (
        (requirement("unknown.fact"),),
        (requirement("planets.normalized", "2.0.0"),),
        (
            CapabilityRequirement(
                capability_id="planets.normalized",
                capability_version="1.0.0",
                required=True,
                when_parameters_present=("not_a_parameter",),
            ),
        ),
    )
    for requirements in bad_sets:
        candidate = replace(base, required_capabilities=requirements)
        registry = PredicateRegistry()
        registry.register(candidate)
        with pytest.raises(PredicateRegistryError):
            registry.finalize()
        assert registry.is_ready is False


@pytest.mark.parametrize(
    ("capability_id", "state", "readiness", "empty"),
    [
        ("planets.normalized", astro(), CapabilityReadiness.READY, False),
        ("planets.normalized", astro(planets=[]), CapabilityReadiness.MALFORMED, True),
        ("planets.house_placement", astro(), CapabilityReadiness.READY, False),
        ("chart.lagna", astro(), CapabilityReadiness.READY, False),
        ("chart.lagna", astro(lagna_sign=""), CapabilityReadiness.MALFORMED, True),
        ("aspects.basic_conjunction_list", astro(enrichments={"aspects": []}), CapabilityReadiness.READY_EMPTY, True),
        ("aspects.whole_sign_graph", astro(enrichments={"aspects": {"edges": []}}), CapabilityReadiness.READY_EMPTY, True),
        ("roles.functional", astro(derived={"functional_roles": {}}), CapabilityReadiness.READY_EMPTY, True),
        ("dignity.exaltation_facts", astro(metadata={"exaltations": {}}), CapabilityReadiness.READY_EMPTY, True),
    ],
)
def test_readiness_and_empty_policy_matrix(capability_id, state, readiness, empty):
    result = inspect_capability(state, requirement(capability_id))
    assert result.readiness is readiness
    assert result.content_empty is empty
    assert result == inspect_capability(state, requirement(capability_id))


def test_missing_none_wrong_type_malformed_version_and_unsupported_are_distinct():
    missing = inspect_capability(SimpleNamespace(), requirement("planets.normalized"))
    none = inspect_capability(SimpleNamespace(planets=None), requirement("planets.normalized"))
    wrong = inspect_capability(SimpleNamespace(planets={}), requirement("planets.normalized"))
    malformed = inspect_capability(SimpleNamespace(planets=[SimpleNamespace(name="Pluto")]), requirement("planets.normalized"))
    mismatch = inspect_capability(astro(), requirement("planets.normalized", "2.0.0"))
    unsupported = inspect_capability(astro(), requirement("unknown.fact"))
    assert missing.readiness is CapabilityReadiness.MISSING
    assert none.readiness is CapabilityReadiness.MISSING
    assert wrong.readiness is CapabilityReadiness.MALFORMED
    assert malformed.readiness is CapabilityReadiness.MALFORMED
    assert mismatch.readiness is CapabilityReadiness.VERSION_MISMATCH
    assert unsupported.readiness is CapabilityReadiness.UNSUPPORTED


def test_aspect_representations_never_satisfy_each_other_or_mutate_state():
    list_state = astro(enrichments={"aspects": []})
    graph_state = astro(enrichments={"aspects": {"edges": []}})
    before_list = list_state.model_dump()
    before_graph = graph_state.model_dump()
    assert inspect_capability(list_state, requirement("aspects.whole_sign_graph")).readiness is CapabilityReadiness.MISSING
    assert inspect_capability(graph_state, requirement("aspects.basic_conjunction_list")).readiness is CapabilityReadiness.MISSING
    assert list_state.model_dump() == before_list
    assert graph_state.model_dump() == before_graph


def test_entity_absence_present_false_zero_and_house_nonmatch_remain_factual():
    state = astro(metadata={"exaltations": {"Mars": 0}})
    present = observe_capability_fact(state, requirement("planets.normalized"), entity_kind="planet", entity_id="Mars")
    absent = observe_capability_fact(state, requirement("planets.normalized"), entity_kind="planet", entity_id="Venus")
    house = observe_capability_fact(state, requirement("planets.house_placement"), entity_kind="planet", entity_id="Mars")
    zero = observe_capability_fact(state, requirement("dignity.exaltation_facts"), entity_kind="planet", entity_id="Mars")
    false_state = SimpleNamespace(
        planets=[SimpleNamespace(name="Mars", sign="Aries", degree=1.0, house=1, flags={"exalted": False})],
        metadata={}, enrichments={}, derived=None, lagna_sign="Aries",
    )
    false = observe_capability_fact(false_state, requirement("dignity.exaltation_facts"), entity_kind="planet", entity_id="Mars")
    assert present.state is CapabilityFactState.PRESENT and present.value_present is True
    assert absent.state is CapabilityFactState.ABSENT_ENTITY and absent.value_present is False
    assert house.state is CapabilityFactState.PRESENT and house.value == 1
    assert zero.state is CapabilityFactState.PRESENT and zero.value == 0
    assert false.state is CapabilityFactState.PRESENT and false.value is False


def test_role_adapter_reads_only_explicit_prepared_facts(monkeypatch):
    import systems.Parasara.engine.enrichments.functional_roles as role_module

    monkeypatch.setattr(role_module, "compute_functional_roles", lambda *_: (_ for _ in ()).throw(AssertionError("producer called")))
    assert inspect_capability(astro(), requirement("roles.functional")).readiness is CapabilityReadiness.MISSING
    state = astro(derived={"functional_roles": {"Mars": {"functional_role": "yogakaraka"}}})
    result = observe_capability_fact(state, requirement("roles.functional"), entity_kind="planet", entity_id="Mars")
    assert result.state is CapabilityFactState.PRESENT
    assert result.value == "yogakaraka"


def test_conflicting_exaltation_sources_are_malformed_without_preference():
    state = SimpleNamespace(
        planets=[SimpleNamespace(name="Mars", sign="Aries", degree=1.0, house=1, flags={"exalted": False})],
        metadata={"exaltations": {"Mars": 10}}, enrichments={}, derived=None, lagna_sign="Aries",
    )
    result = inspect_capability(state, requirement("dignity.exaltation_facts"))
    assert result.readiness is CapabilityReadiness.MALFORMED
    assert "conflicting_sources" in result.issues


@pytest.mark.parametrize(
    ("readiness", "code", "recoverable"),
    [
        (CapabilityReadiness.MISSING, "missing_capability", True),
        (CapabilityReadiness.MALFORMED, "malformed_capability", False),
        (CapabilityReadiness.VERSION_MISMATCH, "capability_version_mismatch", True),
        (CapabilityReadiness.UNSUPPORTED, "unsupported_capability", False),
    ],
)
def test_safe_diagnostic_mapping_is_canonical_immutable_and_alias_aware(readiness, code, recoverable):
    source = inspect_capability(astro(), requirement("unknown.fact"))
    inspection = replace(
        source,
        capability_id="unknown.fact" if readiness is CapabilityReadiness.UNSUPPORTED else "planets.normalized",
        readiness=readiness,
        observed_version="2.0.0" if readiness is CapabilityReadiness.VERSION_MISMATCH else None,
        source_kind=None if readiness in (CapabilityReadiness.MISSING, CapabilityReadiness.UNSUPPORTED) else "normalized_planets",
        issues=("safe_issue",),
    )
    error = capability_error("ASPECT", inspection)
    assert error.code == code
    assert error.predicate_id == "ASPECT_EXISTS"
    assert error.recoverable is recoverable
    assert isinstance(error.details, FrozenMapping)
    assert "object at" not in repr(dict(error.details))


def test_registry_fingerprint_is_capability_sensitive_and_deterministic():
    first = predicate_registry_fingerprint_sha256()
    second = predicate_registry_fingerprint_sha256()
    assert first == second
    assert len(first) == 64
    assert len(capability_catalog_fingerprint_sha256()) == 64


def test_inspection_and_observation_have_stable_canonical_bytes():
    state = astro(metadata={"exaltations": {"Mars": 0}})
    inspection = inspect_capability(state, requirement("dignity.exaltation_facts"))
    observation = observe_capability_fact(
        state,
        requirement("dignity.exaltation_facts"),
        entity_kind="planet",
        entity_id="Mars",
    )
    assert capability_inspection_json_bytes(inspection) == capability_inspection_json_bytes(inspection)
    assert capability_fact_observation_json_bytes(observation) == capability_fact_observation_json_bytes(observation)
    assert b'"value":0' in capability_fact_observation_json_bytes(observation)
