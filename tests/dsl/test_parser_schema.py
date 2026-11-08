"""Strict YAML and closed Prompt-07 schema behavior."""

from __future__ import annotations

import inspect
import sys
import unicodedata

import pytest
from yaml.nodes import ScalarNode

from systems.Parasara.engine.rules.dsl import parser as dsl_parser
from systems.Parasara.engine.rules.dsl import (
    AnalysisSucceeded,
    CompilationFailed,
    DSL_RESOURCE_LIMITS,
    MAX_AST_NODES_PER_DOCUMENT,
    MAX_AST_NODES_PER_RULE,
    MAX_COMPILER_CACHE_ENTRIES,
    MAX_DIAGNOSTICS,
    MAX_IDENTIFIER_LENGTH,
    MAX_MACRO_EXPANSION_DEPTH,
    MAX_MACRO_PARAMETERS,
    MAX_MACROS,
    MAX_MAPPING_ENTRIES,
    MAX_RULES,
    MAX_SEQUENCE_ELEMENTS,
    MAX_SOURCE_BYTES,
    MAX_SOURCE_ID_LENGTH,
    MAX_STRING_LENGTH,
    RuleDslCompiler,
)
from systems.Parasara.engine.rules.dsl.parser import ParsedYamlFailed, ParsedYamlSucceeded, parse_yaml_source


def analyze(payload: bytes | str, source_id: str = "synthetic/test.yaml"):
    return RuleDslCompiler.analyze_source(source_id=source_id, payload=payload)


def codes(result: CompilationFailed) -> tuple[str, ...]:
    return tuple(item.code for item in result.diagnostics)


def test_complete_locked_resource_limit_contract_is_exact():
    assert dict(DSL_RESOURCE_LIMITS) == {
        "source_bytes": 1_048_576,
        "yaml_documents": 1,
        "rules_per_document": 256,
        "dsl_source_artifacts_per_rule_set": 1,
        "macros_per_document": 128,
        "macro_parameters": 16,
        "mapping_entries": 64,
        "sequence_elements": 256,
        "string_code_points": 4_096,
        "identifier_code_points": 128,
        "source_id_code_points": 256,
        "integer_minimum": -(2**31),
        "integer_maximum": 2**31 - 1,
        "decimal_significant_digits": 38,
        "decimal_scale": 12,
        "decimal_magnitude": "1000000",
        "source_ast_depth": 64,
        "source_ast_nodes_per_rule": 4_096,
        "source_ast_nodes_per_document": 16_384,
        "logical_children_per_node": 256,
        "macro_expansion_depth": 16,
        "expanded_nodes_per_rule": 4_096,
        "expanded_nodes_per_document": 16_384,
        "diagnostics": 256,
        "compiler_cache_entries": 64,
    }


def test_valid_minimal_document_builds_immutable_source_and_expanded_models(minimal_payload):
    result = analyze(minimal_payload)
    assert isinstance(result, AnalysisSucceeded)
    document = result.analyzed_rule_set.document
    assert document.system == "synthetic"
    assert document.rules[0].rule_id == "synthetic.mars_in_tenth"
    assert document.rules[0].source_span.source_id == "synthetic/test.yaml"
    assert document.rules[0].when.binding is not None
    with pytest.raises((AttributeError, TypeError)):
        document.rules += document.rules


@pytest.mark.parametrize("source_id", ["synthetic/test.yml", "synthetic/test.json", "test.yaml/../x.yaml"])
def test_only_safe_repository_relative_dot_yaml_source_ids_are_accepted(source_id, minimal_payload):
    result = analyze(minimal_payload, source_id)
    assert isinstance(result, CompilationFailed)
    assert "P07E103_INVALID_FIELD_VALUE" in codes(result)


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (b"\xef\xbb\xbf" + b"dsl: x\n", "P07E001_INVALID_ENCODING"),
        (b"\xff\xfe", "P07E001_INVALID_ENCODING"),
        ("\ud800", "P07E001_INVALID_ENCODING"),
        ("label: " + unicodedata.normalize("NFD", "café"), "P07E001_INVALID_ENCODING"),
        pytest.param(
            b"a" * (MAX_SOURCE_BYTES + 1),
            "P07E002_SOURCE_SIZE_LIMIT",
            id="source-size-limit",
        ),
    ],
)
def test_encoding_normalization_and_source_size_are_fatal(payload, expected):
    result = analyze(payload)
    assert isinstance(result, CompilationFailed)
    assert codes(result) == (expected,)


def test_exact_source_byte_and_source_id_boundaries_are_accepted(minimal_payload):
    padding = MAX_SOURCE_BYTES - len(minimal_payload)
    exact = minimal_payload + b"#" + (b"x" * (padding - 2)) + b"\n"
    assert len(exact) == MAX_SOURCE_BYTES
    assert isinstance(analyze(exact), AnalysisSucceeded)
    assert codes(analyze(exact + b" ")) == ("P07E002_SOURCE_SIZE_LIMIT",)

    exact_id = "x" * (MAX_SOURCE_ID_LENGTH - len(".yaml")) + ".yaml"
    assert len(exact_id) == MAX_SOURCE_ID_LENGTH
    assert isinstance(analyze(minimal_payload, exact_id), AnalysisSucceeded)
    assert isinstance(analyze(minimal_payload, "x" + exact_id), CompilationFailed)


@pytest.mark.parametrize(
    "fragment",
    [
        "value: &anchor x\ncopy: *anchor\n",
        "value: !!python/object/apply:builtins.eval ['1+1']\n",
        "%YAML 1.2\n---\nvalue: x\n",
        "base: &base {x: 1}\nmerged: {<<: *base}\n",
    ],
)
def test_tags_anchors_aliases_merge_keys_and_directives_are_rejected(fragment):
    result = analyze(fragment)
    assert isinstance(result, CompilationFailed)
    assert codes(result) == ("P07E005_FORBIDDEN_YAML_FEATURE",)


def test_multiple_documents_and_duplicate_keys_at_nested_depth_are_rejected(minimal_payload):
    multiple = analyze(minimal_payload + b"\n---\na: b\n")
    assert codes(multiple) == ("P07E006_MULTIPLE_DOCUMENTS",)

    duplicate = analyze(minimal_payload.replace(b"          house: 10", b"          house: 10\n          house: 11"))
    assert codes(duplicate) == ("P07E004_DUPLICATE_KEY",)
    diagnostic = duplicate.diagnostics[0]
    assert diagnostic.source_span is not None
    assert diagnostic.source_span.source_id == "synthetic/test.yaml"
    assert "C:\\" not in diagnostic.message


def test_parser_mapping_sequence_and_string_boundaries_are_exact():
    mapping = "\n".join(f"k{index}: v" for index in range(MAX_MAPPING_ENTRIES)) + "\n"
    assert isinstance(parse_yaml_source(source_id="synthetic/mapping.yaml", payload=mapping), ParsedYamlSucceeded)
    assert isinstance(
        parse_yaml_source(source_id="synthetic/mapping.yaml", payload=mapping + "overflow: v\n"),
        ParsedYamlFailed,
    )

    exact_sequence = "x: [" + ",".join("v" for _ in range(MAX_SEQUENCE_ELEMENTS)) + "]\n"
    overflow_sequence = "x: [" + ",".join("v" for _ in range(MAX_SEQUENCE_ELEMENTS + 1)) + "]\n"
    assert isinstance(parse_yaml_source(source_id="synthetic/sequence.yaml", payload=exact_sequence), ParsedYamlSucceeded)
    assert isinstance(parse_yaml_source(source_id="synthetic/sequence.yaml", payload=overflow_sequence), ParsedYamlFailed)

    assert isinstance(
        parse_yaml_source(source_id="synthetic/string.yaml", payload=f'x: "{"x" * MAX_STRING_LENGTH}"\n'),
        ParsedYamlSucceeded,
    )
    assert isinstance(
        parse_yaml_source(source_id="synthetic/string.yaml", payload=f'x: "{"x" * (MAX_STRING_LENGTH + 1)}"\n'),
        ParsedYamlFailed,
    )


def test_integer_decimal_and_identifier_boundaries_are_exact(minimal_payload):
    limits = DSL_RESOURCE_LIMITS
    for value in (limits["integer_minimum"], limits["integer_maximum"]):
        assert isinstance(parse_yaml_source(source_id="synthetic/integer.yaml", payload=f"x: {value}\n"), ParsedYamlSucceeded)
    for value in (limits["integer_minimum"] - 1, limits["integer_maximum"] + 1):
        assert isinstance(parse_yaml_source(source_id="synthetic/integer.yaml", payload=f"x: {value}\n"), ParsedYamlFailed)

    assert isinstance(parse_yaml_source(
        source_id="synthetic/decimal.yaml", payload="x: 0.123456789012\n"
    ), ParsedYamlSucceeded)
    assert isinstance(parse_yaml_source(
        source_id="synthetic/decimal.yaml", payload="x: 0.1234567890123\n"
    ), ParsedYamlFailed)
    assert isinstance(parse_yaml_source(
        source_id="synthetic/decimal.yaml", payload="x: 1000000.000000000000\n"
    ), ParsedYamlSucceeded)
    assert isinstance(parse_yaml_source(
        source_id="synthetic/decimal.yaml", payload="x: 1000000.000000000001\n"
    ), ParsedYamlFailed)

    exact_rule_id = "s" + "x" * (MAX_IDENTIFIER_LENGTH - 1)
    assert isinstance(analyze(minimal_payload.replace(b"synthetic.mars_in_tenth", exact_rule_id.encode())), AnalysisSucceeded)
    assert isinstance(analyze(minimal_payload.replace(b"synthetic.mars_in_tenth", (exact_rule_id + "x").encode())), CompilationFailed)


def test_decimal_significant_digit_guard_accepts_38_and_rejects_39():
    limit = DSL_RESOURCE_LIMITS["decimal_significant_digits"]
    exact = "1" * (limit - 1) + ".1"
    overflow = "1" * limit + ".1"

    def significant_digits(value: str) -> int:
        whole, fraction = value.split(".", 1)
        return len((whole.lstrip("0") + fraction).lstrip("0") or "0")

    assert limit == 38
    assert significant_digits(exact) == 38
    assert significant_digits(overflow) == 39
    assert len(exact.split(".", 1)[1]) <= dsl_parser.MAX_DECIMAL_SCALE
    assert len(overflow.split(".", 1)[1]) <= dsl_parser.MAX_DECIMAL_SCALE

    source_lines, start_line = inspect.getsourcelines(dsl_parser._plain_scalar)
    significant_check = next(
        index for index, line in enumerate(source_lines)
        if "MAX_DECIMAL_SIGNIFICANT_DIGITS" in line
    )
    decimal_conversion = next(
        index for index, line in enumerate(source_lines)
        if "decimal = Decimal(value)" in line
    )
    significant_rejection_line = start_line + next(
        index for index in range(significant_check, decimal_conversion)
        if 'return None, "P07E104_INVALID_NUMERIC_VALUE"' in source_lines[index]
    )
    magnitude_check = next(
        index for index, line in enumerate(source_lines)
        if "abs(decimal) > Decimal(MAX_DECIMAL_MAGNITUDE)" in line
    )
    magnitude_check_line = start_line + magnitude_check
    magnitude_rejection_line = start_line + next(
        index for index in range(magnitude_check + 1, len(source_lines))
        if 'return None, "P07E104_INVALID_NUMERIC_VALUE"' in source_lines[index]
    )

    configured_limits = (
        dsl_parser.MAX_DECIMAL_SIGNIFICANT_DIGITS,
        dsl_parser.MAX_DECIMAL_SCALE,
        dsl_parser.MAX_DECIMAL_MAGNITUDE,
    )

    def traced_validation(value: str):
        executed_lines: set[int] = set()
        previous_trace = sys.gettrace()

        def record_lines(frame, event, argument):
            del argument
            if frame.f_code is dsl_parser._plain_scalar.__code__ and event == "line":
                executed_lines.add(frame.f_lineno)
            return record_lines

        try:
            sys.settrace(record_lines)
            result = dsl_parser._plain_scalar(
                ScalarNode(tag="tag:yaml.org,2002:float", value=value)
            )
        finally:
            sys.settrace(previous_trace)
        assert sys.gettrace() is previous_trace
        return result, executed_lines

    (exact_value, exact_error), exact_lines = traced_validation(exact)
    (overflow_value, overflow_error), overflow_lines = traced_validation(overflow)

    assert configured_limits == (38, 12, "1000000")
    assert configured_limits == (
        dsl_parser.MAX_DECIMAL_SIGNIFICANT_DIGITS,
        dsl_parser.MAX_DECIMAL_SCALE,
        dsl_parser.MAX_DECIMAL_MAGNITUDE,
    )
    assert exact_value is None
    assert exact_error == "P07E104_INVALID_NUMERIC_VALUE"
    assert significant_rejection_line not in exact_lines
    assert {magnitude_check_line, magnitude_rejection_line} <= exact_lines
    assert overflow_value is None
    assert overflow_error == "P07E104_INVALID_NUMERIC_VALUE"
    assert significant_rejection_line in overflow_lines
    assert magnitude_check_line not in overflow_lines


@pytest.mark.parametrize(
    "scalar",
    ["null", "~", "", "01", "+1", "1e3", "0x10", "0o10", ".inf", ".nan", "2026-09-07", "-0", "-0.0"],
)
def test_forbidden_plain_scalar_forms_are_rejected(minimal_payload, scalar):
    replacement = f"    base_weight: {scalar}\n".encode()
    payload = minimal_payload.replace(b"    base_weight: 0.25\n", replacement)
    result = analyze(payload)
    assert isinstance(result, CompilationFailed)
    assert "P07E007_INVALID_SCALAR" in codes(result) or "P07E104_INVALID_NUMERIC_VALUE" in codes(result)


def test_unknown_fields_are_sorted_and_missing_fields_follow_schema_order(minimal_payload):
    payload = minimal_payload.replace(
        b"dsl: parasara-rule-dsl\n",
        b"z_unknown: value\na_unknown: value\n",
    )
    result = analyze(payload)
    assert isinstance(result, CompilationFailed)
    fields = [item.field_path for item in result.diagnostics]
    assert fields.count("$.dsl") == 1
    unknown_fields = [item.field_path for item in result.diagnostics if item.code == "P07E101_UNKNOWN_FIELD"]
    assert sorted(unknown_fields) == ["$.a_unknown", "$.z_unknown"]


def test_diagnostic_collection_is_capped_with_explicit_final_marker(minimal_payload):
    rules = "\n".join(f"  - id: synthetic.rule_{index:03d}" for index in range(256))
    payload = (
        "dsl: parasara-rule-dsl\n"
        "dsl_version: \"1.0.0\"\n"
        "system: synthetic\n"
        "rule_set: {family: prompt07_fixture, version: fixture-v1}\n"
        "macros: []\n"
        f"rules:\n{rules}\n"
    )
    result = analyze(payload)
    assert isinstance(result, CompilationFailed)
    assert len(result.diagnostics) == MAX_DIAGNOSTICS
    assert result.diagnostics[-1].code == "P07E999_DIAGNOSTIC_LIMIT"


def test_rule_macro_and_macro_parameter_count_boundaries(minimal_payload):
    text = minimal_payload.decode("utf-8")
    prefix, rule_block = text.split("rules:\n", 1)
    rules = "".join(
        rule_block.replace("synthetic.mars_in_tenth", f"synthetic.rule_{index:03d}", 1)
        for index in range(MAX_RULES)
    )
    assert isinstance(analyze((prefix + "rules:\n" + rules).encode()), AnalysisSucceeded)
    overflow_rule = rule_block.replace("synthetic.mars_in_tenth", "synthetic.rule_overflow", 1)
    assert isinstance(analyze((prefix + "rules:\n" + rules + overflow_rule).encode()), CompilationFailed)

    leaf = '{predicate: {id: PLANET_IN_HOUSE, version: "1.0.0", arguments: {planet: Mars, house: 10}}}'
    macros = "".join(
        f'  - id: macro_{index}\n    revision: "1.0.0"\n    parameters: []\n    body: {leaf}\n'
        for index in range(MAX_MACROS)
    )
    exact_macros = text.replace("macros: []\n", "macros:\n" + macros)
    assert isinstance(analyze(exact_macros), AnalysisSucceeded)
    overflow_macro = (
        f'  - id: macro_overflow\n    revision: "1.0.0"\n    parameters: []\n    body: {leaf}\n'
    )
    assert isinstance(analyze(exact_macros.replace("rules:\n", overflow_macro + "rules:\n")), CompilationFailed)

    parameters = "".join(
        f"      - {{name: p{index}, type: house}}\n" for index in range(MAX_MACRO_PARAMETERS)
    )
    macro = (
        'macros:\n  - id: bounded\n    revision: "1.0.0"\n    parameters:\n'
        + parameters
        + f"    body: {leaf}\n"
    )
    assert isinstance(analyze(text.replace("macros: []\n", macro)), AnalysisSucceeded)
    overflow_parameter = f"      - {{name: p{MAX_MACRO_PARAMETERS}, type: house}}\n"
    assert isinstance(
        analyze(text.replace("macros: []\n", macro.replace("    body:", overflow_parameter + "    body:"))),
        CompilationFailed,
    )


def test_logical_child_limit_and_ast_depth_are_bounded(minimal_payload):
    children = "\n".join(
        "        - predicate: {id: PLANET_IN_HOUSE, version: \"1.0.0\", arguments: {planet: Mars, house: 10}}"
        for _ in range(257)
    )
    payload = minimal_payload.decode().replace(
        "    when:\n      predicate:\n        id: PLANET_IN_HOUSE\n        version: \"1.0.0\"\n        arguments:\n          planet: Mars\n          house: 10",
        "    when:\n      all:\n" + children,
    )
    result = analyze(payload)
    assert isinstance(result, CompilationFailed)
    assert any(code in codes(result) for code in ("P07E103_INVALID_FIELD_VALUE", "P07E203_AST_NODE_LIMIT"))

    leaf = "{predicate: {id: PLANET_IN_HOUSE, version: \"1.0.0\", arguments: {planet: Mars, house: 10}}}"
    nested = leaf
    for _ in range(65):
        nested = "{not: " + nested + "}"
    depth_payload = minimal_payload.decode().replace(
        "    when:\n      predicate:\n        id: PLANET_IN_HOUSE\n        version: \"1.0.0\"\n        arguments:\n          planet: Mars\n          house: 10",
        "    when: " + nested,
    )
    depth_result = analyze(depth_payload)
    assert isinstance(depth_result, CompilationFailed)
    assert "P07E202_AST_DEPTH_LIMIT" in codes(depth_result)


def _condition_payload(minimal_payload: bytes, expression: str, *, rule_id: str) -> str:
    original = minimal_payload.decode("utf-8")
    block = (
        "    when:\n"
        "      predicate:\n"
        "        id: PLANET_IN_HOUSE\n"
        '        version: "1.0.0"\n'
        "        arguments:\n"
        "          planet: Mars\n"
        "          house: 10"
    )
    return original.replace("synthetic.mars_in_tenth", rule_id, 1).replace(
        block, "    when: " + expression
    )


def test_exact_logical_child_and_ast_depth_boundaries(minimal_payload):
    leaf = '{predicate: {id: PLANET_IN_HOUSE, version: "1.0.0", arguments: {planet: Mars, house: 10}}}'
    children = ", ".join(leaf for _ in range(DSL_RESOURCE_LIMITS["logical_children_per_node"]))
    assert isinstance(analyze(_condition_payload(
        minimal_payload, "{all: [" + children + "]}", rule_id="synthetic.children"
    )), AnalysisSucceeded)

    exact_depth = leaf
    for _ in range(DSL_RESOURCE_LIMITS["source_ast_depth"] - 1):
        exact_depth = "{not: " + exact_depth + "}"
    assert isinstance(analyze(_condition_payload(
        minimal_payload, exact_depth, rule_id="synthetic.depth"
    )), AnalysisSucceeded)
    assert "P07E202_AST_DEPTH_LIMIT" in codes(analyze(_condition_payload(
        minimal_payload, "{not: " + exact_depth + "}", rule_id="synthetic.depth"
    )))


def test_source_ast_node_boundaries_per_rule_and_document(minimal_payload):
    # An unresolved macro leaf keeps this source-budget test from spending
    # time lowering a deliberately 16,384-node condition forest.
    leaf = '{macro: {id: missing, revision: "1.0.0", arguments: {}}}'
    chain = leaf
    for _ in range(61):
        chain = "{not: " + chain + "}"
    branch = "{all: [" + chain + "]}"
    exact_expression = "{all: [" + ", ".join(branch for _ in range(65)) + "]}"
    overflow_branch = "{all: [" + chain + ", " + leaf + "]}"
    overflow_expression = "{all: [" + ", ".join([branch] * 64 + [overflow_branch]) + "]}"

    per_rule_overflow = analyze(_condition_payload(
        minimal_payload, overflow_expression, rule_id="synthetic.node_overflow"
    ))
    assert isinstance(per_rule_overflow, CompilationFailed)
    assert "P07E203_AST_NODE_LIMIT" in codes(per_rule_overflow)

    original = minimal_payload.decode("utf-8")
    prefix, rule_block = original.split("rules:\n", 1)
    condition_block = rule_block[rule_block.index("    when:\n"):].rstrip("\n")
    rules = []
    for index in range(4):
        rules.append(
            rule_block.replace("synthetic.mars_in_tenth", f"synthetic.nodes_{index}", 1)
            .replace(condition_block, "    when: " + exact_expression)
        )
    exact_document = prefix + "rules:\n" + "".join(rules)
    exact = analyze(exact_document)
    assert isinstance(exact, CompilationFailed)
    assert "P07E302_MACRO_NOT_FOUND" in codes(exact)
    assert "P07E203_AST_NODE_LIMIT" not in codes(exact)

    extra = rule_block.replace("synthetic.mars_in_tenth", "synthetic.nodes_extra", 1)
    document_overflow = analyze(exact_document + extra)
    assert isinstance(document_overflow, CompilationFailed)
    assert "P07E203_AST_NODE_LIMIT" in codes(document_overflow)
