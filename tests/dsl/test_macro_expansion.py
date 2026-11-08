"""Typed, hygienic, finite macro expansion."""

from __future__ import annotations

from systems.Parasara.engine.rules.dsl import (
    AnalysisSucceeded,
    CompilationFailed,
    MacroCallNode,
    RuleDslCompiler,
)


def analyze(payload: bytes | str):
    return RuleDslCompiler.analyze_source(source_id="synthetic/macros.yaml", payload=payload)


def diagnostic_codes(result):
    return tuple(item.code for item in result.diagnostics)


def test_typed_macro_expands_hygienically_and_records_trace(macros_payload):
    result = analyze(macros_payload)
    assert isinstance(result, AnalysisSucceeded)
    rule = result.analyzed_rule_set.rules[0]
    assert not isinstance(rule.expanded_condition_ast, MacroCallNode)
    assert rule.lowered_condition["params"] == {"house": 10, "planet": "Mars"}
    assert len(rule.macro_expansion_trace) == 1
    trace = rule.macro_expansion_trace[0]
    assert trace.macro_id == "planet_in_house" and trace.expansion_ordinal == 0
    assert trace.call_span.source_id == "synthetic/macros.yaml"
    assert result.analyzed_rule_set.document.macros[0].body.binding is not None


def test_macro_argument_type_and_unbound_parameter_are_rejected(macros_payload):
    wrong = analyze(macros_payload.replace(b"          house: 10", b"          house: ten"))
    assert "P07E304_MACRO_ARGUMENT_TYPE_MISMATCH" in diagnostic_codes(wrong)

    unbound = analyze(macros_payload.replace(b"{parameter: house}", b"{parameter: missing}"))
    assert "P07E305_MACRO_PARAMETER_NOT_FOUND" in diagnostic_codes(unbound)


def test_direct_and_indirect_macro_cycles_are_distinct(macros_payload):
    direct = macros_payload.replace(
        b"    body:\n      predicate:\n        id: PLANET_IN_HOUSE\n        version: \"1.0.0\"\n        arguments:\n          planet: {parameter: planet}\n          house: {parameter: house}",
        b"    body:\n      macro:\n        id: planet_in_house\n        revision: \"1.0.0\"\n        arguments:\n          planet: {parameter: planet}\n          house: {parameter: house}",
    )
    result = analyze(direct)
    assert "P07E306_MACRO_DIRECT_RECURSION" in diagnostic_codes(result)

    prefix = b"""dsl: parasara-rule-dsl
dsl_version: "1.0.0"
system: synthetic
rule_set: {family: prompt07_macros, version: fixture-v1}
macros:
  - id: first
    revision: "1.0.0"
    parameters: []
    body: {macro: {id: second, revision: "1.0.0", arguments: {}}}
  - id: second
    revision: "1.0.0"
    parameters: []
    body: {macro: {id: first, revision: "1.0.0", arguments: {}}}
rules:
  - id: synthetic.cycle
    revision: "1.0.0"
    family: synthetic
    category: synthetic
    domains: [synthetic]
    label: "Synthetic cycle"
    priority: 0
    base_weight: 0.1
    context: natal
    requires: []
    evidence: {mode: predicate_trace_references}
    when: {macro: {id: first, revision: "1.0.0", arguments: {}}}
"""
    result = analyze(prefix)
    assert "P07E307_MACRO_CYCLE" in diagnostic_codes(result)


def test_duplicate_macro_revision_and_unknown_macro_are_rejected(macros_payload):
    duplicate = macros_payload.replace(b"rules:\n", macros_payload.split(b"macros:\n", 1)[1].split(b"rules:\n", 1)[0] + b"rules:\n")
    result = analyze(duplicate)
    assert "P07E301_DUPLICATE_MACRO_REVISION" in diagnostic_codes(result)

    missing = analyze(macros_payload.replace(b"id: planet_in_house\n        revision", b"id: absent_macro\n        revision", 1))
    assert "P07E302_MACRO_NOT_FOUND" in diagnostic_codes(missing)


def _chain_payload(length: int, *, fanout: int) -> str:
    macros = []
    for index in range(length):
        if index == length - 1:
            body = "{predicate: {id: PLANET_IN_HOUSE, version: \"1.0.0\", arguments: {planet: Mars, house: 10}}}"
        else:
            call = f"{{macro: {{id: macro_{index + 1}, revision: \"1.0.0\", arguments: {{}}}}}}"
            body = call if fanout == 1 else "{all: [" + ", ".join([call] * fanout) + "]}"
        macros.append(
            f"  - id: macro_{index}\n"
            "    revision: \"1.0.0\"\n"
            "    parameters: []\n"
            f"    body: {body}"
        )
    return (
        "dsl: parasara-rule-dsl\n"
        "dsl_version: \"1.0.0\"\n"
        "system: synthetic\n"
        "rule_set: {family: prompt07_macros, version: fixture-v1}\n"
        "macros:\n" + "\n".join(macros) + "\n"
        "rules:\n"
        "  - id: synthetic.limit\n"
        "    revision: \"1.0.0\"\n"
        "    family: synthetic\n"
        "    category: synthetic\n"
        "    domains: [synthetic]\n"
        "    label: \"Synthetic limit\"\n"
        "    priority: 0\n"
        "    base_weight: 0.1\n"
        "    context: natal\n"
        "    requires:\n"
        "      - {id: planets.house_placement, version: \"1.0.0\"}\n"
        "      - {id: planets.normalized, version: \"1.0.0\"}\n"
        "    evidence: {mode: predicate_trace_references}\n"
        "    when: {macro: {id: macro_0, revision: \"1.0.0\", arguments: {}}}\n"
    )


def test_macro_expansion_depth_and_post_substitution_node_budgets_are_enforced():
    exact_depth = analyze(_chain_payload(16, fanout=1))
    assert isinstance(exact_depth, AnalysisSucceeded)

    too_deep = analyze(_chain_payload(17, fanout=1))
    assert isinstance(too_deep, CompilationFailed)
    assert "P07E308_MACRO_EXPANSION_DEPTH_LIMIT" in diagnostic_codes(too_deep)

    too_large = analyze(_chain_payload(14, fanout=2))
    assert isinstance(too_large, CompilationFailed)
    assert "P07E309_MACRO_EXPANDED_NODE_LIMIT" in diagnostic_codes(too_large)


def test_expanded_node_boundaries_per_rule_and_document_are_exact():
    # A twelve-macro binary expansion has 4,095 nodes; the outer NOT makes
    # the normative per-rule boundary exactly 4,096. Deliberately empty
    # capabilities stop after expansion so this limit test stays focused.
    exact = _chain_payload(12, fanout=2).replace(
        '    requires:\n      - {id: planets.house_placement, version: "1.0.0"}\n'
        '      - {id: planets.normalized, version: "1.0.0"}',
        "    requires: []",
    ).replace(
        '    when: {macro: {id: macro_0, revision: "1.0.0", arguments: {}}}',
        '    when: {not: {macro: {id: macro_0, revision: "1.0.0", arguments: {}}}}',
    )
    exact_result = analyze(exact)
    assert isinstance(exact_result, CompilationFailed)
    assert "P07E215_PREDICATE_CAPABILITY_MISMATCH" in diagnostic_codes(exact_result)
    assert "P07E309_MACRO_EXPANDED_NODE_LIMIT" not in diagnostic_codes(exact_result)

    overflow = analyze(_chain_payload(13, fanout=2))
    assert isinstance(overflow, CompilationFailed)
    assert "P07E309_MACRO_EXPANDED_NODE_LIMIT" in diagnostic_codes(overflow)

    prefix, rule_block = exact.split("rules:\n", 1)
    four_rules = "".join(
        rule_block.replace("synthetic.limit", f"synthetic.limit_{index}", 1)
        for index in range(4)
    )
    exact_document = analyze(prefix + "rules:\n" + four_rules)
    assert isinstance(exact_document, CompilationFailed)
    assert "P07E215_PREDICATE_CAPABILITY_MISMATCH" in diagnostic_codes(exact_document)
    assert "P07E309_MACRO_EXPANDED_NODE_LIMIT" not in diagnostic_codes(exact_document)

    leaf_rule = rule_block.replace("synthetic.limit", "synthetic.limit_extra", 1).replace(
        '    when: {not: {macro: {id: macro_0, revision: "1.0.0", arguments: {}}}}',
        '    when: {predicate: {id: PLANET_IN_HOUSE, version: "1.0.0", '
        'arguments: {planet: Mars, house: 10}}}',
    )
    overflow_document = analyze(prefix + "rules:\n" + four_rules + leaf_rule)
    assert isinstance(overflow_document, CompilationFailed)
    assert "P07E309_MACRO_EXPANDED_NODE_LIMIT" in diagnostic_codes(overflow_document)
