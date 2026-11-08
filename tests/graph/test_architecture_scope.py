"""Stage-specific graph ownership; no repository-wide verification framework."""
import ast
import inspect
from pathlib import Path

from systems.Parasara.engine.rules.graph import RuleGraphCompiler
from systems.Parasara.engine.rules.rule_engine import RuleEngine

ROOT = Path(__file__).resolve().parents[2]
GRAPH = ROOT / "systems/Parasara/engine/rules/graph"


def test_exact_graph_modules_and_no_runtime_or_external_owners():
    assert {p.name for p in GRAPH.glob("*.py")} == {"__init__.py", "compiler.py", "models.py", "parser.py", "runtime_contract.py"}
    forbidden = {"os", "socket", "requests", "subprocess", "importlib", "random", "time", "datetime", "pickle", "threading", "concurrent"}
    for path in GRAPH.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): assert not {a.name.split(".")[0] for a in node.names} & forbidden
            if isinstance(node, ast.ImportFrom) and node.module: assert node.module.split(".")[0] not in forbidden
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"RuleMatch", "PredicateResult", "ConditionResult", "open", "eval", "exec", "__import__"}
        assert ".evaluate(" not in text
        assert "InferenceEngine(" not in text


def test_only_whole_plan_and_manifest_source_inputs_exist():
    assert tuple(inspect.signature(RuleGraphCompiler.compile_authorized).parameters) == ("self", "compiled_rule_set")
    assert tuple(inspect.signature(RuleEngine.evaluate_plan).parameters) == ("self", "plan", "condition_evaluator", "snapshot", "context")
    for cls in (RuleGraphCompiler, RuleEngine):
        assert not any(name in vars(cls) for name in ("evaluate_subplan", "adopt_plan", "register_plan", "recompute", "incremental", "parallel"))


def test_existing_production_and_dsl_paths_do_not_import_graph():
    relatives = ["systems/Parasara/engine/interpreters", "systems/Parasara/engine/enrichments",
        "systems/Parasara/engine/inference", "systems/Parasara/engine/rules/dsl", "systems/Parasara/rules/parashara/v1"]
    for relative in relatives:
        for path in (ROOT / relative).rglob("*.py"):
            assert "rules.graph" not in path.read_text(encoding="utf-8")
    engine = ROOT / "systems/Parasara/engine"
    assert not any(p for p in engine.rglob("*.py") if any(
        token in p.as_posix().lower() for token in ("prompt09", "prompt_09", "fwp01", "fwp_01")))
