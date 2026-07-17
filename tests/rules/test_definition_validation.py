"""WP12 active F1/F2 condition-definition validation contract."""

from __future__ import annotations

from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

import pytest

from systems.Parasara.engine.rules.canonical import FrozenMapping
from systems.Parasara.engine.rules.conditions import ConditionEvaluator
from systems.Parasara.engine.rules.definition_validation import (
    DEFINITION_SCHEMA_VERSION,
    DefinitionIssue,
    DefinitionIssueSeverity,
    DefinitionValidationOutcome,
    RuleSourceIdentity,
    ValidatedConditionDefinition,
    ValidatedNodeBinding,
    ValidatedNodeKind,
    ValidatedYogaRule,
    YogaRuleSetValidationOutcome,
    definition_semantic_json_bytes,
    definition_semantic_sha256,
    definition_issues_json_bytes,
    definition_issues_sha256,
    definition_source_json_bytes,
    definition_source_sha256,
    validate_condition_definition,
    validate_yoga_rule_file,
    validate_yoga_rules,
)
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.parameters import ParameterIssueCode
from systems.Parasara.engine.rules.prepared_state import (
    PredicateEvaluationContext,
    prepare_predicate_state,
)
from systems.Parasara.engine.rules.registry import PredicateRegistry, get_production_registry


REPO_ROOT = Path(__file__).resolve().parents[2]
YOGAS = REPO_ROOT / "systems" / "Parasara" / "rules" / "parashara" / "v1" / "yogas.yaml"


def source(name="rules/yogas.yaml", *, rule_id=None, rule_index=None):
    return RuleSourceIdentity(source_name=name, rule_id=rule_id, rule_index=rule_index)


def leaf(predicate="PLANET_IN_HOUSE", params=None):
    return {"type": predicate, "params": {"planet": "Mars", "house": 1} if params is None else params}


def valid(node, identity=None):
    outcome = validate_condition_definition(node, source=identity or source("direct"))
    assert outcome.valid and outcome.definition is not None and outcome.issues == ()
    return outcome.definition


def codes(outcome):
    return tuple(issue.code for issue in outcome.issues)


def prepared():
    raw = SimpleNamespace(
        planets=[SimpleNamespace(name="Mars", house=1, sign="Aries", degree=12.0)],
        lagna_sign="Aries", enrichments={}, derived=None, metadata={}, diagnostics={},
    )
    outcome = prepare_predicate_state(raw)
    assert outcome.succeeded and outcome.state is not None
    return outcome.state


def test_exact_model_fields_enums_and_contradictory_outcome_invariants():
    assert DEFINITION_SCHEMA_VERSION == "1.0.0"
    assert [item.name for item in fields(RuleSourceIdentity)] == ["source_name", "rule_id", "rule_index"]
    assert [item.name for item in fields(DefinitionIssue)] == [
        "code", "message", "node_path", "source", "predicate_id", "parameter_name", "details", "severity"
    ]
    assert [item.name for item in fields(ValidatedNodeBinding)] == [
        "node_id", "node_path", "node_kind", "requested_type", "canonical_type",
        "predicate_version", "parameters", "required_capabilities", "child_count",
    ]
    assert [item.name for item in fields(ValidatedConditionDefinition)] == [
        "source", "normalized_condition", "node_bindings"
    ]
    assert [item.name for item in fields(DefinitionValidationOutcome)] == ["valid", "definition", "issues"]
    assert tuple(item.value for item in DefinitionIssueSeverity) == ("error",)
    assert tuple(item.value for item in ValidatedNodeKind) == ("logical", "predicate")
    with pytest.raises(ValueError):
        DefinitionValidationOutcome(valid=True, definition=None, issues=())
    with pytest.raises(ValueError):
        DefinitionValidationOutcome(valid=False, definition=valid(leaf()), issues=())


def test_source_and_issue_models_are_safe_frozen_and_reject_path_or_raw_detail_leaks():
    identity = source(rule_id="demo", rule_index=0)
    with pytest.raises(Exception):
        identity.source_name = "changed"
    for unsafe in (str(YOGAS), "../yogas.yaml", " rules/yogas.yaml", "rules\\yogas.yaml"):
        with pytest.raises(ValueError):
            RuleSourceIdentity(source_name=unsafe)
    with pytest.raises(ValueError):
        DefinitionIssue(
            code="unknown_predicate", message="secret supplied value", node_path="condition.root",
            source=identity, details={},
        )
    with pytest.raises(ValueError):
        DefinitionIssue(
            code="unknown_predicate", message="The condition references an unknown predicate.",
            node_path="condition.root", source=identity,
            details={"exception": "bad supplied secret value"},
        )


def test_valid_nested_tree_is_deeply_immutable_and_preserves_preorder_and_child_order():
    raw = {
        "children": [
            {"params": {"house": 1, "planet": "mars"}, "type": " planet_in_house "},
            {"type": "NOT", "children": [leaf(params={"planet": "Mars", "house": 2})]},
        ],
        "type": " and ",
    }
    definition = valid(raw)
    raw["children"][0]["params"]["house"] = 12
    assert isinstance(definition.normalized_condition, FrozenMapping)
    assert definition.normalized_condition["type"] == "AND"
    assert definition.normalized_condition["children"][0]["params"] == {"house": 1, "planet": "Mars"}
    assert tuple(item.node_path for item in definition.node_bindings) == (
        "condition.root", "condition.root.children.0", "condition.root.children.1",
        "condition.root.children.1.children.0",
    )
    assert tuple(item.canonical_type for item in definition.node_bindings) == (
        "AND", "PLANET_IN_HOUSE", "NOT", "PLANET_IN_HOUSE",
    )
    with pytest.raises(TypeError):
        definition.normalized_condition["type"] = "OR"


def test_alias_binding_uses_canonical_identity_version_parameters_and_ordered_capabilities():
    definition = valid({"type": " aspect ", "params": {"to_house": 10, "from_house": 1}})
    binding = definition.node_bindings[0]
    assert binding.requested_type == "ASPECT"
    assert binding.canonical_type == "ASPECT_EXISTS"
    assert binding.predicate_version == "1.0.0"
    assert binding.parameters == {"from_house": 1, "to_house": 10}
    assert binding.required_capabilities == (("aspects.whole_sign_graph", "1.0.0"),)
    assert definition.normalized_condition == {
        "type": "ASPECT_EXISTS", "params": {"from_house": 1, "to_house": 10}
    }


def test_six_exposed_ids_bind_to_five_canonical_definitions_without_registry_mutation():
    registry = get_production_registry()
    before = registry.metadata_snapshot()
    expected = {
        "ASPECT": "ASPECT_EXISTS", "ASPECT_EXISTS": "ASPECT_EXISTS",
        "FUNCTIONAL_ROLE": "FUNCTIONAL_ROLE", "HOUSE_OCCUPANT": "HOUSE_OCCUPANT",
        "PLANET_EXALTED": "PLANET_EXALTED", "PLANET_IN_HOUSE": "PLANET_IN_HOUSE",
    }
    parameters = {
        "ASPECT": {}, "ASPECT_EXISTS": {},
        "FUNCTIONAL_ROLE": {"role_in": ["benefic"]},
        "HOUSE_OCCUPANT": {"house": 1, "planet": "Mars"},
        "PLANET_EXALTED": {"planet": "Mars"},
        "PLANET_IN_HOUSE": {"house": 1, "planet": "Mars"},
    }
    assert {item: valid(leaf(item, parameters[item])).node_bindings[0].canonical_type for item in expected} == expected
    assert registry.metadata_snapshot() == before


def test_unready_registry_is_one_boundary_issue_not_unknown_predicates():
    outcome = validate_condition_definition(leaf(), source=source("direct"), registry=PredicateRegistry())
    assert codes(outcome) == ("definition_registry_unready",)
    assert outcome.issues[0].node_path == "condition.root"

    incomplete = PredicateRegistry().finalize()
    outcome = validate_condition_definition(leaf(), source=source("direct"), registry=incomplete)
    assert codes(outcome) == ("definition_registry_incompatible",)


@pytest.mark.parametrize(
    ("node", "expected"),
    [
        (None, ("condition_node_not_mapping",)),
        ({}, ("condition_type_missing",)),
        ({"type": None, "params": {}}, ("condition_type_not_string",)),
        ({"type": " ", "params": {}}, ("condition_type_blank",)),
        ({"op": "AND", "args": []}, ("condition_type_missing", "condition_unknown_fields")),
        ({"type": "ALL", "children": [leaf()]}, ("unknown_operator",)),
        ({"type": "AND"}, ("condition_children_missing",)),
        ({"type": "AND", "children": None}, ("condition_children_not_list",)),
        ({"type": "AND", "children": []}, ("condition_empty_operator",)),
        ({"type": "OR", "children": []}, ("condition_empty_operator",)),
        ({"type": "NOT", "children": []}, ("condition_not_arity",)),
        ({"type": "NOT", "children": [leaf(), leaf()]}, ("condition_not_arity",)),
        ({"type": "PLANET_IN_HOUSE"}, ("condition_params_missing",)),
        ({"type": "PLANET_IN_HOUSE", "params": None}, ("condition_params_not_mapping",)),
        ({"type": "PLANET_IN_HOUSE", "params": {}, "children": []}, ("condition_unknown_fields",)),
        ({"type": "AND", "children": [leaf()], "params": {}}, ("condition_unknown_fields",)),
        ({"type": "PLANET_IN_HOUSE", "params": {}, "version": "1.0.0"}, ("condition_unknown_fields",)),
        ({"type": "PLANET_IN_HOUSE", "params": {}, "capabilities": []}, ("condition_unknown_fields",)),
    ],
)
def test_structural_and_unsupported_alternate_formats(node, expected):
    assert codes(validate_condition_definition(node, source=source("direct"))) == expected


def test_unknown_predicates_include_house_lords_as_safe_typed_definition_errors():
    for predicate in ("PLANET_IN_HOSE", "HOUSE_LORDS_COMBINATION"):
        outcome = validate_condition_definition({"type": predicate, "params": {}}, source=source("direct"))
        assert codes(outcome) == ("unknown_predicate",)
        assert outcome.issues[0].predicate_id == predicate
        assert predicate not in repr(outcome.issues[0].details)


def test_parameter_issue_order_matches_wp05_and_normalized_definition_has_no_raw_values():
    node = {"type": "PLANET_IN_HOUSE", "params": {"planet": "Pluto", "extra": "secret"}}
    outcome = validate_condition_definition(node, source=source("direct"))
    assert tuple(issue.parameter_name for issue in outcome.issues) == ("planet", "house", None)
    assert codes(outcome) == tuple(f"parameter_{item.value}" for item in (
        ParameterIssueCode.INVALID_VALUE, ParameterIssueCode.MISSING_REQUIRED, ParameterIssueCode.UNKNOWN_PARAMETER,
    ))
    assert "Pluto" not in repr(outcome.issues) and "secret" not in repr(outcome.issues)


def test_preorder_issue_order_is_parent_then_left_to_right_then_wp05_order():
    node = {
        "type": "AND", "children": [
            {"type": "PLANET_IN_HOUSE", "params": {}},
            {"type": "UNKNOWN", "params": {}},
        ], "extra": True,
    }
    outcome = validate_condition_definition(node, source=source("direct"))
    assert tuple((item.code, item.node_path) for item in outcome.issues) == (
        ("condition_unknown_fields", "condition.root"),
        ("parameter_missing_required", "condition.root.children.0"),
        ("parameter_missing_required", "condition.root.children.0"),
        ("unknown_predicate", "condition.root.children.1"),
    )


def _not_chain(depth):
    node = leaf()
    for _ in range(depth - 1):
        node = {"type": "NOT", "children": [node]}
    return node


def _wide(count):
    return {"type": "AND", "children": [leaf() for _ in range(count - 1)]}


def test_cycle_depth_and_node_limits_use_one_fatal_stable_issue_without_crash():
    cycle = {"type": "NOT", "children": []}
    cycle["children"].append(cycle)
    assert codes(validate_condition_definition(cycle, source=source("direct"))) == ("condition_cycle",)
    assert valid(_not_chain(64))
    assert codes(validate_condition_definition(_not_chain(65), source=source("direct"))) == ("condition_depth_limit",)
    assert valid(_wide(4096))
    assert codes(validate_condition_definition(_wide(4097), source=source("direct"))) == ("condition_node_limit",)


def test_semantic_bytes_exclude_source_and_alias_spelling_while_source_bytes_include_identity():
    alias = valid({"params": {"from_house": 1}, "type": "ASPECT"}, source("a.yaml", rule_id="a", rule_index=0))
    canonical = valid({"type": "ASPECT_EXISTS", "params": {"from_house": 1}}, source("b.yaml", rule_id="b", rule_index=7))
    assert definition_semantic_json_bytes(alias) == definition_semantic_json_bytes(canonical)
    assert definition_semantic_sha256(alias) == definition_semantic_sha256(canonical)
    assert definition_source_json_bytes(alias) != definition_source_json_bytes(canonical)
    assert definition_source_sha256(alias) != definition_source_sha256(canonical)


def test_validated_normalized_definition_has_wp10_evaluation_parity():
    raw = {"type": "NOT", "children": [leaf(params={"planet": "Mars", "house": 2})]}
    definition = valid(raw)
    evaluator = ConditionEvaluator(PredicateEvaluator())
    context = PredicateEvaluationContext()
    assert evaluator.evaluate(raw, prepared(), context) == evaluator.evaluate(
        definition.normalized_condition, prepared(), context
    )


def test_validation_does_not_execute_or_prepare_any_astrology(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("runtime work was attempted")

    monkeypatch.setattr(PredicateEvaluator, "evaluate", forbidden)
    monkeypatch.setattr(
        "systems.Parasara.engine.rules.prepared_state.prepare_predicate_state", forbidden
    )
    definition = valid({"type": "ASPECT", "params": {"from_house": 1}})
    assert definition.node_bindings[0].canonical_type == "ASPECT_EXISTS"
    implementation = Path(
        "systems/Parasara/engine/rules/definition_validation.py"
    ).read_text(encoding="utf-8")
    for forbidden_text in ("perf_counter", "random.", "socket.", "os.environ", "prepare_predicate_state("):
        assert forbidden_text not in implementation


def _yoga_rule(rule_id="demo", conditions=None):
    return {
        "id": rule_id, "name": "Demo", "version": 1, "category": "demo",
        "conditions": leaf() if conditions is None else conditions,
        "weights": {"base": 1.0}, "evidence_required": 1, "provenance": "test",
        "sme_approved": False, "tests": [],
    }


def test_strict_current_yoga_file_reports_exact_known_issue_and_returns_other_rules_in_source_order():
    before = get_production_registry().metadata_snapshot()
    outcome = validate_yoga_rule_file(YOGAS, source_name="rules/parashara/v1/yogas.yaml")
    assert not outcome.valid
    assert [item.rule_id for item in outcome.rules] == ["rajayoga_naive", "arishta_naive"]
    assert tuple((item.code, item.node_path, item.source.rule_id, item.source.rule_index) for item in outcome.issues) == (
        ("unknown_predicate", "condition.root.children.0", "dhana_naive", 1),
    )
    issue_bytes = definition_issues_json_bytes(outcome.issues)
    assert b"HOUSE_LORDS_COMBINATION" in issue_bytes
    assert b"C:\\" not in issue_bytes and b"Traceback" not in issue_bytes
    assert len(definition_issues_sha256(outcome.issues)) == 64
    assert get_production_registry().metadata_snapshot() == before

    direct = valid(
        {"type": "AND", "children": [
            {"type": "ASPECT", "params": {"from_house": 1, "to_house": 10}},
            {"type": "FUNCTIONAL_ROLE", "params": {"role_in": ["functional_benefic", "yogakaraka", "benefic"]}},
        ]},
        source("direct"),
    )
    assert definition_semantic_json_bytes(outcome.rules[0].condition) == definition_semantic_json_bytes(direct)


def test_duplicate_ids_anchor_first_and_later_occurrences_are_rejected_without_last_wins():
    first = _yoga_rule("duplicate", leaf(params={"planet": "Mars", "house": 1}))
    second = _yoga_rule("duplicate", leaf(params={"planet": "Mars", "house": 2}))
    outcome = validate_yoga_rules([first, second], source_name="synthetic.yaml")
    assert [item.rule_id for item in outcome.rules] == ["duplicate"]
    assert codes(outcome) == ("duplicate_rule_id",)
    assert outcome.issues[0].source.rule_index == 1


@pytest.mark.parametrize(
    ("records", "expected"),
    [
        ({}, ("yoga_document_root_not_list",)),
        ([None], ("yoga_rule_not_mapping",)),
        ([_yoga_rule(conditions=None) | {"condition": leaf()}], ("yoga_rule_unknown_fields",)),
        ([_yoga_rule() | {"id": " "}], ("yoga_rule_id_invalid",)),
        ([{"id": "missing"}], ("yoga_rule_missing_field",) * 9),
        ([_yoga_rule() | {"conditions": [leaf()]}], ("yoga_conditions_not_mapping",)),
    ],
)
def test_strict_yoga_record_shape_and_wrapper_errors_are_aggregated(records, expected):
    assert codes(validate_yoga_rules(records, source_name="synthetic.yaml")) == expected


def test_file_loading_is_explicit_safe_and_cwd_independent(tmp_path, monkeypatch):
    good = tmp_path / "good.yaml"
    good.write_text("- id: demo\n  name: Demo\n  version: 1\n  category: demo\n  conditions: {type: PLANET_IN_HOUSE, params: {planet: Mars, house: 1}}\n  weights: {base: 1}\n  evidence_required: 1\n  provenance: test\n  sme_approved: false\n  tests: []\n", encoding="utf-8")
    first = validate_yoga_rule_file(good, source_name="good.yaml")
    monkeypatch.chdir(tmp_path.parent)
    second = validate_yoga_rule_file(good, source_name="good.yaml")
    assert first == second and first.valid
    assert codes(validate_yoga_rule_file(tmp_path / "missing.yaml", source_name="missing.yaml")) == ("yoga_file_missing",)
    malformed = tmp_path / "bad.yaml"
    malformed.write_text("- [", encoding="utf-8")
    assert codes(validate_yoga_rule_file(malformed, source_name="bad.yaml")) == ("yoga_invalid_yaml",)
    unsafe = tmp_path / "unsafe.yaml"
    unsafe.write_text("!!python/object:os.system {}", encoding="utf-8")
    assert codes(validate_yoga_rule_file(unsafe, source_name="unsafe.yaml")) == ("yoga_unsafe_yaml",)

    original_read_text = Path.read_text

    def unreadable(self, *args, **kwargs):
        if self == good:
            raise OSError("sensitive operating-system detail")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", unreadable)
    failed = validate_yoga_rule_file(good, source_name="good.yaml")
    assert codes(failed) == ("yoga_file_unreadable",)
    assert "sensitive" not in repr(failed.issues)


def test_yoga_models_are_typed_immutable_and_isolate_caller_mutation():
    record = _yoga_rule()
    outcome = validate_yoga_rules([record], source_name="synthetic.yaml")
    assert isinstance(outcome, YogaRuleSetValidationOutcome) and outcome.valid
    assert isinstance(outcome.rules[0], ValidatedYogaRule)
    record["weights"]["base"] = 99
    assert outcome.rules[0].rule["weights"]["base"] == 1.0
    with pytest.raises(Exception):
        outcome.rules = ()
