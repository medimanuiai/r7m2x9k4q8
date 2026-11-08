"""Static predicate, parameter, capability, and lowering tests."""

from __future__ import annotations

from systems.Parasara.engine.rules.canonical import FrozenMapping
from systems.Parasara.engine.rules.dsl import AnalysisSucceeded, CompilationFailed, RuleDslCompiler


def compile_text(payload: bytes):
    return RuleDslCompiler.analyze_source(source_id="synthetic/binding.yaml", payload=payload)


def test_predicate_binding_is_exact_and_reuses_registry_schema(minimal_payload):
    result = compile_text(minimal_payload)
    assert isinstance(result, AnalysisSucceeded)
    rule = result.analyzed_rule_set.rules[0]
    binding = rule.predicate_bindings[0]
    assert binding.predicate_id == "PLANET_IN_HOUSE"
    assert binding.predicate_version == "1.0.0"
    assert binding.arguments == {"house": 10, "planet": "Mars"}
    assert len(binding.definition_sha256) == 64
    assert rule.lowered_condition == FrozenMapping(
        {"type": "PLANET_IN_HOUSE", "params": {"house": 10, "planet": "Mars"}}
    )


def test_predicate_alias_and_version_mismatch_are_rejected(minimal_payload):
    alias = compile_text(minimal_payload.replace(b"PLANET_IN_HOUSE", b"ASPECT"))
    assert isinstance(alias, CompilationFailed)
    assert alias.diagnostics[0].code == "P07E211_UNKNOWN_PREDICATE"

    version = compile_text(minimal_payload.replace(b'version: "1.0.0"\n        arguments:', b'version: "9.9.9"\n        arguments:', 1))
    assert isinstance(version, CompilationFailed)
    assert "P07E212_PREDICATE_VERSION_MISMATCH" in tuple(item.code for item in version.diagnostics)


def test_missing_unknown_and_wrong_typed_arguments_are_deterministic(minimal_payload):
    missing = compile_text(minimal_payload.replace(b"          house: 10\n", b""))
    unknown = compile_text(minimal_payload.replace(b"          house: 10\n", b"          house: 10\n          extra: 1\n"))
    wrong = compile_text(minimal_payload.replace(b"          house: 10", b"          house: ten"))
    assert "P07E213_INVALID_ARGUMENT_NAME" in tuple(item.code for item in missing.diagnostics)
    assert "P07E213_INVALID_ARGUMENT_NAME" in tuple(item.code for item in unknown.diagnostics)
    assert "P07E214_ARGUMENT_TYPE_MISMATCH" in tuple(item.code for item in wrong.diagnostics)


def test_rule_capabilities_must_exactly_equal_bound_predicate_union(minimal_payload):
    payload = minimal_payload.replace(
        b"      - id: planets.normalized\n        version: \"1.0.0\"\n",
        b"",
    )
    result = compile_text(payload)
    assert isinstance(result, CompilationFailed)
    assert "P07E215_PREDICATE_CAPABILITY_MISMATCH" in tuple(item.code for item in result.diagnostics)


def test_boolean_operators_lower_in_authored_order(minimal_payload):
    leaf = "{predicate: {id: PLANET_IN_HOUSE, version: \"1.0.0\", arguments: {planet: Mars, house: 10}}}"
    payload = minimal_payload.decode().replace(
        "    when:\n      predicate:\n        id: PLANET_IN_HOUSE\n        version: \"1.0.0\"\n        arguments:\n          planet: Mars\n          house: 10",
        f"    when:\n      all:\n        - {leaf}\n        - not: {leaf}",
    )
    result = compile_text(payload.encode())
    assert isinstance(result, AnalysisSucceeded)
    lowered = result.analyzed_rule_set.rules[0].lowered_condition
    assert lowered["type"] == "AND"
    assert tuple(item["type"] for item in lowered["children"]) == ("PLANET_IN_HOUSE", "NOT")
