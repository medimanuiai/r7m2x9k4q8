"""Static DSL ownership and opt-in graph boundary checks."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DSL_ROOT = ROOT / "systems/Parasara/engine/rules/dsl"


def test_dsl_package_has_no_forbidden_runtime_authorities_or_imports():
    forbidden_imports = {
        "os", "subprocess", "socket", "requests", "urllib", "http", "random",
        "datetime", "time", "importlib", "inspect", "ctypes",
    }
    forbidden_calls = {"eval", "exec", "compile", "open", "__import__"}
    for path in sorted(DSL_ROOT.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not ({item.name.split(".")[0] for item in node.names} & forbidden_imports)
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden_imports
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_calls


def test_rulematch_construction_and_condition_truth_stay_in_existing_owners():
    compiler = (DSL_ROOT / "compiler.py").read_text(encoding="utf-8")
    assert "RuleMatch(" not in compiler
    assert "PredicateResult(" not in compiler
    assert "ConditionResult(" not in compiler
    assert ".evaluate(" not in compiler


def test_graph_is_separate_and_dsl_has_no_dependency_behavior():
    candidates = [
        path for path in (ROOT / "systems/Parasara").rglob("*.py")
        if path.name in {"dependency_graph.py", "graph_planner.py"}
    ]
    assert candidates == []
    assert (DSL_ROOT.parent / "graph/compiler.py").is_file()
    for path in sorted(DSL_ROOT.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        assert "topological" not in text.lower()
        assert "dependency-aware" not in text.lower()
        assert "requires_matches" not in text and "optional_supports" not in text
    from systems.Parasara.engine.versioning import RuleVersionResolver, compatibility_v1_config
    assert RuleVersionResolver().resolve(compatibility_v1_config()).manifest.dependency_graph is None


def test_prompt07_validator_composes_actual_prompt01_contract_tests():
    from tools import validate_prompt07

    paths = tuple(ROOT / relative for relative in validate_prompt07.PROMPT01_FOCUSED_PATHS)
    assert paths
    assert all(path.is_file() for path in paths)
    assert any("condition" in path.name for path in paths)
    assert any("predicate" in path.name for path in paths)
    assert any("definition_validation" in path.name for path in paths)
    validator_source = (ROOT / "tools/validate_prompt07.py").read_text(encoding="utf-8")
    assert '"Prompt-01 condition predicate definition contracts"' in validator_source
    assert "*PROMPT01_FOCUSED_PATHS" in validator_source
