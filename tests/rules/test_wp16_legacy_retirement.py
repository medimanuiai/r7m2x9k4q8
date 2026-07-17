"""Negative architecture enforcement for the WP16 retirement boundary."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
THIS_FILE = Path(__file__).resolve()
RETIRED_SYMBOLS = frozenset(
    {
        "in_sign",
        "in_house",
        "lord_of_house",
        "is_exalted",
        "evaluate_rule",
        "evaluate_rule_with_score",
        "RuleMatch",
        "record_predicate",
        "record_rule",
    }
)
DIRECT_CANONICAL_HANDLERS = frozenset(
    {
        "evaluate_aspect_exists",
        "evaluate_functional_role",
        "evaluate_house_occupant",
        "evaluate_planet_exalted",
        "evaluate_planet_in_house",
    }
)


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_retired_modules_models_instrumentation_and_bootstrap_are_absent():
    absent = (
        "systems/Parasara/engine/rules/runtime.py",
        "systems/Parasara/engine/rules/engine.py",
        "systems/Parasara/engine/rules/predicates.py",
        "tests/testing_framework/instrumentation.py",
    )
    assert all(not (ROOT / relative).exists() for relative in absent)
    models = _tree(ROOT / "systems/Parasara/engine/models.py")
    assert {
        node.name
        for node in ast.walk(models)
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }.isdisjoint(RETIRED_SYMBOLS)


def test_no_executable_definition_import_or_reference_to_retired_symbols_remains():
    references = []
    paths = (
        *ROOT.glob("systems/Parasara/**/*.py"),
        *ROOT.glob("tests/**/*.py"),
    )
    for path in paths:
        if path.resolve() == THIS_FILE:
            continue
        for node in ast.walk(_tree(path)):
            names = set()
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(node.name)
            elif isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.Attribute):
                names.add(node.attr)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    names.add(alias.name.rsplit(".", 1)[-1])
                    if alias.asname:
                        names.add(alias.asname)
            for name in names & RETIRED_SYMBOLS:
                references.append((path.relative_to(ROOT), node.lineno, name))
    assert references == []


def test_production_dispatches_registered_handlers_only_inside_typed_evaluator():
    calls = []
    engine_root = ROOT / "systems/Parasara/engine"
    for path in engine_root.rglob("*.py"):
        if path.name == "evaluator.py":
            continue
        for node in ast.walk(_tree(path)):
            if not isinstance(node, ast.Call):
                continue
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name in DIRECT_CANONICAL_HANDLERS:
                calls.append((path.relative_to(ROOT), node.lineno, name))
    assert calls == []


def test_tooling_has_no_mutable_registry_or_global_instrumentation_dependency():
    tooling = (
        ROOT / "tests/testing_framework/generate_full_artifacts.py",
        ROOT / "tests/testing_framework/rule_coverage.py",
        ROOT / "tests/testing_framework/typed_rule_evaluation.py",
    )
    forbidden_imports = {"loader", "instrumentation"}
    found = []
    for path in tooling:
        for node in ast.walk(_tree(path)):
            if isinstance(node, ast.Import):
                names = {alias.name.rsplit(".", 1)[-1] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {(node.module or "").rsplit(".", 1)[-1]}
                names.update(alias.name for alias in node.names)
            else:
                continue
            for name in names & forbidden_imports:
                found.append((path.relative_to(ROOT), node.lineno, name))
    assert found == []
