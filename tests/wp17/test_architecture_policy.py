"""Central executable architecture policy for the Prompt-01 typed boundary."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "systems" / "Parasara" / "engine"

RETIRED_MODULES = frozenset(
    {
        "systems.Parasara.engine.rules.engine",
        "systems.Parasara.engine.rules.predicates",
        "systems.Parasara.engine.rules.runtime",
        "tests.testing_framework.instrumentation",
    }
)
RETIRED_SYMBOLS = frozenset(
    {
        "RuleMatch",
        "evaluate_rule",
        "evaluate_rule_with_score",
        "in_house",
        "in_sign",
        "is_exalted",
        "lord_of_house",
        "record_predicate",
        "record_rule",
    }
)
REGISTERED_HANDLERS = frozenset(
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


def _imports(path: Path) -> tuple[tuple[int, str], ...]:
    found: list[tuple[int, str]] = []
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Import):
            found.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            found.append((node.lineno, node.module or ""))
    return tuple(found)


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def test_retired_modules_symbols_and_direct_handler_boundaries_stay_absent():
    for module in RETIRED_MODULES:
        assert not (ROOT / (module.replace(".", "/") + ".py")).exists()

    retired: list[tuple[str, int, str]] = []
    direct_calls: list[tuple[str, int, str]] = []
    for path in (*ENGINE.rglob("*.py"), *(ROOT / "tests").rglob("*.py")):
        relative = _relative(path)
        tree = _tree(path)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module_names = (
                    [alias.name for alias in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                )
                for module in module_names:
                    if module in RETIRED_MODULES:
                        retired.append((relative, node.lineno, module))
            if isinstance(node, ast.Call):
                name = _call_name(node)
                if name in RETIRED_SYMBOLS:
                    retired.append((relative, node.lineno, name))
                if (
                    name in REGISTERED_HANDLERS
                    and relative.startswith("systems/Parasara/engine/")
                    and relative != "systems/Parasara/engine/rules/evaluator.py"
                ):
                    direct_calls.append((relative, node.lineno, name))
    assert retired == []
    assert direct_calls == []


def test_production_never_imports_tests_or_testing_helpers():
    violations = [
        (_relative(path), line, module)
        for path in ENGINE.rglob("*.py")
        for line, module in _imports(path)
        if module == "tests" or module.startswith("tests.")
    ]
    assert violations == []


def test_predicate_yoga_and_career_layer_imports_are_one_way():
    predicate_files = (
        ENGINE / "rules" / "canonical_predicates.py",
        ENGINE / "rules" / "conditions.py",
        ENGINE / "rules" / "evaluator.py",
        ENGINE / "rules" / "planet_in_house.py",
        ENGINE / "rules" / "prepared_state.py",
    )
    predicate_forbidden = (
        "systems.Parasara.engine.interpreters",
        "systems.Parasara.engine.enrichments.yoga",
        "systems.Parasara.tools",
        "systems.SuryaSiddhanta",
        "tests",
    )
    yoga_forbidden = (
        "systems.Parasara.engine.interpreters",
        "systems.Parasara.engine.public",
        "systems.Parasara.frontend",
        "systems.Parasara.api",
    )
    career_forbidden = (
        "systems.Parasara.engine.enrichments.yoga",
        "systems.Parasara.engine.rules.loader",
        "systems.Parasara.engine.rules.yoga_loader",
        "systems.Parasara.tools",
        "systems.SuryaSiddhanta",
        "tests",
    )
    violations: list[tuple[str, int, str]] = []
    for path in predicate_files:
        violations.extend(
            (_relative(path), line, module)
            for line, module in _imports(path)
            if module.startswith(predicate_forbidden)
        )
    yoga_path = ENGINE / "enrichments" / "yoga_engine.py"
    violations.extend(
        (_relative(yoga_path), line, module)
        for line, module in _imports(yoga_path)
        if module.startswith(yoga_forbidden)
    )
    for path in (
        ENGINE / "interpreters" / "career.py",
        ENGINE / "interpreters" / "career_models.py",
    ):
        violations.extend(
            (_relative(path), line, module)
            for line, module in _imports(path)
            if module.startswith(career_forbidden)
        )
    assert violations == []


def test_core_models_and_serialization_have_no_runtime_discovery_dependencies():
    """Core identity code must not import clocks, randomness, I/O, or networking.

    Type rejection is implemented without importing those operational modules.
    JSON and hashing are the only serializer services allowed here.
    """

    forbidden_roots = frozenset(
        {
            "asyncio",
            "http",
            "os",
            "pathlib",
            "random",
            "requests",
            "secrets",
            "socket",
            "subprocess",
            "tempfile",
            "time",
            "urllib",
            "uuid",
        }
    )
    paths = (
        ENGINE / "rules" / "canonical.py",
        ENGINE / "rules" / "models.py",
        ENGINE / "interpreters" / "career_models.py",
    )
    violations = [
        (_relative(path), line, module)
        for path in paths
        for line, module in _imports(path)
        if module.split(".", 1)[0] in forbidden_roots
    ]
    assert violations == []


def test_compatibility_projections_are_output_only_and_typed_evaluators_do_not_call_them():
    projection_names = frozenset(
        {"project_yoga_compatibility", "project_career_compatibility"}
    )
    factual_functions = frozenset(
        {
            "evaluate_yoga_batch",
            "evaluate_career_batch",
            "evaluate_condition_canonical",
            "evaluate",
        }
    )
    violations: list[tuple[str, int, str, str]] = []
    for path in (
        ENGINE / "enrichments" / "yoga_engine.py",
        ENGINE / "interpreters" / "career.py",
        ENGINE / "rules" / "conditions.py",
        ENGINE / "rules" / "evaluator.py",
    ):
        for node in ast.walk(_tree(path)):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name not in factual_functions:
                continue
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and _call_name(child) in projection_names:
                    violations.append(
                        (_relative(path), child.lineno, node.name, _call_name(child) or "")
                    )
    assert violations == []


def test_factual_function_annotations_are_typed_not_boolean_tuple_or_dictionary():
    files = (
        ENGINE / "rules" / "canonical_predicates.py",
        ENGINE / "rules" / "planet_in_house.py",
        ENGINE / "rules" / "conditions.py",
        ENGINE / "enrichments" / "yoga_engine.py",
        ENGINE / "interpreters" / "career.py",
    )
    factual_names = frozenset(
        {
            "evaluate_aspect_exists",
            "evaluate_career_batch",
            "evaluate_condition_canonical",
            "evaluate_functional_role",
            "evaluate_house_occupant",
            "evaluate_planet_exalted",
            "evaluate_planet_in_house",
            "evaluate_yoga_batch",
        }
    )
    forbidden = {"bool", "tuple", "dict", "Dict", "Mapping"}
    violations = []
    for path in files:
        for node in ast.walk(_tree(path)):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name not in factual_names or node.returns is None:
                continue
            rendered = ast.unparse(node.returns)
            if rendered.split("[", 1)[0] in forbidden:
                violations.append((_relative(path), node.lineno, node.name, rendered))
    assert violations == []
