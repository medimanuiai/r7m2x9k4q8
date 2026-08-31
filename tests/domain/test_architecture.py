from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "systems" / "Parasara" / "engine"


def tree(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"))


def imported_modules(path: Path) -> set[str]:
    output = set()
    for node in ast.walk(tree(path)):
        if isinstance(node, ast.ImportFrom):
            output.add(node.module or "")
        elif isinstance(node, ast.Import):
            output.update(item.name for item in node.names)
    return output


def test_exactly_one_output_assembler_and_one_inference_engine():
    definitions = []
    for path in ENGINE.rglob("*.py"):
        for node in ast.walk(tree(path)):
            if isinstance(node, ast.ClassDef) and node.name in {
                "OutputAssembler", "InferenceEngine"
            }:
                definitions.append((path.relative_to(ROOT).as_posix(), node.name))
    assert sorted(definitions) == sorted([
        ("systems/Parasara/engine/inference/engine.py", "InferenceEngine"),
        ("systems/Parasara/engine/output_assembler.py", "OutputAssembler"),
    ])


def test_domain_contracts_and_assembler_obey_import_direction():
    domain_modules = (
        ENGINE / "domain" / "models.py",
        ENGINE / "domain" / "factories.py",
    )
    for path in domain_modules:
        imports = imported_modules(path)
        assert not any(
            forbidden in module
            for module in imports
            for forbidden in (
                ".adapter", ".astrostate", ".enrichments", ".interpreters",
                ".normalizer", ".dasha",
            )
        )
    assembler_imports = imported_modules(ENGINE / "output_assembler.py")
    assert not any(
        forbidden in module
        for module in assembler_imports
        for forbidden in (
            ".adapter", ".astrostate", ".enrichments", ".interpreters",
            ".inference", ".rules.rule_engine", ".rules.evaluator", ".dasha",
        )
    )


def test_prompt05_contract_and_assembler_do_not_call_clock_or_calculators():
    paths = (
        ENGINE / "domain" / "models.py",
        ENGINE / "domain" / "factories.py",
        ENGINE / "output_assembler.py",
    )
    forbidden_calls = {
        "now", "utcnow", "compute_vimshottari", "calculate_transits",
        "aggregate", "evaluate", "freeze_astrostate", "chart_to_astrostate",
    }
    for path in paths:
        calls = {
            node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
            for node in ast.walk(tree(path))
            if isinstance(node, ast.Call)
            and isinstance(node.func, (ast.Attribute, ast.Name))
        }
        assert not calls & forbidden_calls, (path, calls & forbidden_calls)


def test_only_career_is_a_substantive_domain_interpreter():
    files = tuple(path.name for path in (ENGINE / "interpreters").glob("*.py"))
    assert set(files) <= {"__init__.py", "career.py", "career_models.py"}
    text = (ROOT / "systems" / "Parasara" / "tools" / "generate_snapshot.py").read_text(encoding="utf-8")
    assert "DomainId.WEALTH" not in text
    assert "interpret_wealth" not in text


def test_public_domain_dictionary_construction_is_confined_to_assembler():
    offenders = []
    for path in ENGINE.rglob("*.py"):
        if path.name == "output_assembler.py":
            continue
        source = path.read_text(encoding="utf-8")
        if '"wealth": {' in source or '"domains": {' in source:
            offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []


def test_career_has_one_shared_inference_call_and_no_score_confidence_formula():
    source = (ENGINE / "interpreters" / "career.py").read_text(encoding="utf-8")
    assert source.count(".aggregate(") == 1
    for forbidden in ("compute_confidence", "scoring_breakdown", "confidence_mod"):
        assert forbidden not in source


def test_career_post_inference_helper_graph_has_no_hidden_aggregation():
    module = tree(ENGINE / "interpreters" / "career.py")
    functions = {
        node.name: node
        for node in module.body
        if isinstance(node, ast.FunctionDef)
    }
    reachable = {"build_career_prediction"}
    pending = ["build_career_prediction"]
    while pending:
        current = pending.pop()
        for call in (
            item for item in ast.walk(functions[current]) if isinstance(item, ast.Call)
        ):
            if isinstance(call.func, ast.Name) and call.func.id in functions:
                if call.func.id not in reachable:
                    reachable.add(call.func.id)
                    pending.append(call.func.id)
    aggregate_calls = []
    for name in sorted(reachable):
        for call in (
            item for item in ast.walk(functions[name]) if isinstance(item, ast.Call)
        ):
            if (
                isinstance(call.func, ast.Name)
                and call.func.id == "sum"
            ) or (
                isinstance(call.func, ast.Attribute)
                and call.func.attr in {"fsum", "aggregate"}
            ):
                aggregate_calls.append((name, ast.unparse(call.func)))
    assert aggregate_calls == []


def test_r4_removed_authority_apis_are_not_publicly_exported():
    from systems.Parasara.engine import domain
    from systems.Parasara.engine.domain import (
        DomainPredictionFactory,
        YogaDiagnosticFactory,
    )
    from systems.Parasara.engine.enrichments import yoga_engine
    from systems.Parasara.engine.inference import InferenceEngine
    from systems.Parasara.engine.interpreters import career

    assert not {
        "domain_prediction_from_logical_data",
        "domain_prediction_from_logical_json",
        "yoga_diagnostic_from_logical_data",
        "yoga_diagnostic_from_logical_json",
    } & set(domain.__all__)
    assert "build_career_prediction" not in career.__all__
    assert "infer_career" not in career.__all__
    assert "build_yoga_diagnostics" not in yoga_engine.__all__
    assert not hasattr(InferenceEngine, "compatibility_projection")
    assert not hasattr(DomainPredictionFactory, "from_inference")
    assert not hasattr(YogaDiagnosticFactory, "from_evaluation_record")
