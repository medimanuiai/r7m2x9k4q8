"""WP14 negative architecture and dormant Yoga-helper retirement contracts."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.enrichments import yoga as yoga_api
from systems.Parasara.engine.enrichments import yoga_engine
from systems.Parasara.engine.enrichments.yoga_engine import (
    YogaDefinitionDisposition,
    evaluate_yoga_batch,
    load_yoga_rule_source,
    prepare_legacy_yoga_state,
    project_yoga_compatibility,
    yoga_batch_full_json_bytes,
    yoga_batch_logical_json_bytes,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules.definition_validation import (
    definition_issues_json_bytes,
)
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.conditions import ConditionEvaluator
from systems.Parasara.engine.rules.models import ConditionResult, PredicateStatus
from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext
from systems.Parasara.engine.rules.registry import get_production_registry


REPO_ROOT = Path(__file__).resolve().parents[2]
YOGA_ENGINE_PATH = REPO_ROOT / "systems" / "Parasara" / "engine" / "enrichments" / "yoga_engine.py"
YOGA_API_PATH = REPO_ROOT / "systems" / "Parasara" / "engine" / "enrichments" / "yoga.py"
SURYA_TEST = REPO_ROOT / "systems" / "Parasara" / "fixtures" / "surya_test_chart.json"

RETIRED_SYMBOLS = frozenset(
    {
        "_eval_aspect_condition",
        "_eval_functional_role_condition",
        "_eval_house_lords_combination",
        "_eval_house_occupant",
        "_eval_condition",
    }
)
LEGACY_CALLS = frozenset(
    {
        "clear_cache",
        "evaluate_condition",
        "evaluate_predicate",
        "load_yoga_rules",
        "uuid4",
    }
)
CANONICAL_HANDLERS = frozenset(
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


def _names(node: ast.AST | None) -> set[str]:
    if node is None:
        return set()
    return {
        item.id if isinstance(item, ast.Name) else item.attr
        for item in ast.walk(node)
        if isinstance(item, (ast.Name, ast.Attribute))
    }


def _string_exports(tree: ast.Module) -> set[str]:
    exports: set[str] = set()
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets):
            continue
        value = node.value
        if isinstance(value, (ast.List, ast.Tuple)):
            exports.update(
                item.value
                for item in value.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            )
    return exports


def _astro():
    return chart_to_astrostate(SuryaAdapter.load(str(SURYA_TEST)))


def _batch():
    source = load_yoga_rule_source()
    preparation = prepare_legacy_yoga_state(_astro(), source)
    assert preparation.outcome.succeeded and preparation.outcome.state is not None
    batch = evaluate_yoga_batch(
        preparation.outcome.state,
        PredicateEvaluationContext(),
        source,
        predicate_evaluator=PredicateEvaluator(),
        compatibility_graph=preparation.compatibility_graph,
    )
    return source, batch


def test_retired_symbols_are_absent_from_runtime_ast_and_exports():
    engine_tree = _tree(YOGA_ENGINE_PATH)
    api_tree = _tree(YOGA_API_PATH)
    definitions = {
        node.name
        for node in ast.walk(engine_tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }

    assert definitions.isdisjoint(RETIRED_SYMBOLS)
    assert all(not hasattr(yoga_engine, name) for name in RETIRED_SYMBOLS)
    assert _string_exports(engine_tree).isdisjoint(RETIRED_SYMBOLS)
    assert _string_exports(api_tree).isdisjoint(RETIRED_SYMBOLS)
    assert RETIRED_SYMBOLS.isdisjoint(yoga_api.__all__)


def test_yoga_has_no_tuple_boolean_factual_helper_or_local_dispatcher():
    tree = _tree(YOGA_ENGINE_PATH)
    tuple_boolean_functions = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        annotation_names = _names(node.returns)
        if "bool" in annotation_names and ({"tuple", "Tuple"} & annotation_names):
            tuple_boolean_functions.append(node.name)

    assert tuple_boolean_functions == []
    assert {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }.isdisjoint(RETIRED_SYMBOLS)


def test_yoga_static_route_uses_only_typed_boundaries_and_not_direct_handlers():
    tree = _tree(YOGA_ENGINE_PATH)
    imported_modules: set[str] = set()
    imported_names: set[str] = set()
    called_names: set[str] = set()
    string_constants: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module or "")
            imported_names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_names.add(node.func.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            string_constants.add(node.value)

    assert "systems.Parasara.engine.rules.conditions" in imported_modules
    assert "systems.Parasara.engine.rules.evaluator" in imported_modules
    assert "systems.Parasara.engine.rules.definition_validation" in imported_modules
    assert "systems.Parasara.engine.rules.prepared_state" in imported_modules
    assert not any(module.endswith("rules.engine") for module in imported_modules)
    assert not any(module.endswith("rules.predicates") for module in imported_modules)
    assert not any(module.endswith("rules.yoga_loader") for module in imported_modules)
    assert imported_names.isdisjoint(LEGACY_CALLS | CANONICAL_HANDLERS | {"RULE_REGISTRY"})
    assert imported_names.isdisjoint({"Tuple", "compute_functional_roles"})
    assert called_names.isdisjoint(LEGACY_CALLS | CANONICAL_HANDLERS | RETIRED_SYMBOLS)
    assert string_constants.isdisjoint(RETIRED_SYMBOLS)


def test_no_external_python_caller_import_alias_or_definition_remains():
    references: list[tuple[Path, int, str]] = []
    paths = [
        *REPO_ROOT.glob("systems/Parasara/**/*.py"),
        *REPO_ROOT.glob("tests/**/*.py"),
    ]
    for path in paths:
        if path == Path(__file__).resolve():
            continue
        tree = _tree(path)
        for node in ast.walk(tree):
            found: set[str] = set()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                found.add(node.name)
            elif isinstance(node, ast.Name):
                found.add(node.id)
            elif isinstance(node, ast.Attribute):
                found.add(node.attr)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    found.add(alias.name.rsplit(".", 1)[-1])
                    if alias.asname is not None:
                        found.add(alias.asname)
            for name in found & RETIRED_SYMBOLS:
                references.append((path.relative_to(REPO_ROOT), node.lineno, name))

    assert references == []


def test_public_path_executes_wp12_wp07_wp10_and_wp09_boundaries(monkeypatch):
    calls = {"file_validation": 0, "record_validation": 0, "prepare": 0, "condition": 0, "predicate": 0}
    original_file_validation = yoga_engine.validate_yoga_rule_file
    original_record_validation = yoga_engine.validate_yoga_rules
    original_prepare = yoga_engine.prepare_predicate_state
    original_condition = ConditionEvaluator.evaluate
    original_predicate = PredicateEvaluator.evaluate

    def file_validation_spy(*args, **kwargs):
        calls["file_validation"] += 1
        return original_file_validation(*args, **kwargs)

    def record_validation_spy(*args, **kwargs):
        calls["record_validation"] += 1
        return original_record_validation(*args, **kwargs)

    def prepare_spy(*args, **kwargs):
        calls["prepare"] += 1
        return original_prepare(*args, **kwargs)

    def condition_spy(self, *args, **kwargs):
        calls["condition"] += 1
        return original_condition(self, *args, **kwargs)

    def predicate_spy(self, *args, **kwargs):
        calls["predicate"] += 1
        return original_predicate(self, *args, **kwargs)

    monkeypatch.setattr(yoga_engine, "validate_yoga_rule_file", file_validation_spy)
    monkeypatch.setattr(yoga_engine, "validate_yoga_rules", record_validation_spy)
    monkeypatch.setattr(yoga_engine, "prepare_predicate_state", prepare_spy)
    monkeypatch.setattr(ConditionEvaluator, "evaluate", condition_spy)
    monkeypatch.setattr(PredicateEvaluator, "evaluate", predicate_spy)

    rows = yoga_engine.evaluate_yoga_rules(_astro())

    assert [row["matched"] for row in rows] == [True, False, False]
    assert calls["file_validation"] == 1
    assert calls["record_validation"] == 1
    assert calls["prepare"] == 1
    assert calls["condition"] >= 3
    assert calls["predicate"] >= 5


def test_house_lords_stays_unregistered_typed_invalid_and_publicly_stable():
    source, batch = _batch()
    registry = get_production_registry()
    issues = source.validation.issues
    issue_bytes = definition_issues_json_bytes(issues)

    assert registry.lookup("HOUSE_LORDS_COMBINATION") is None
    assert len(issue_bytes) == 320
    assert hashlib.sha256(issue_bytes).hexdigest() == (
        "1e448cf198bf2aa3df5aa9e2cb0fc67ed2384f005f110d814239b380fd7b1fa6"
    )
    assert [
        (item.code, item.source.rule_id, item.source.rule_index, item.node_path, item.predicate_id)
        for item in issues
    ] == [
        (
            "unknown_predicate",
            "dhana_naive",
            1,
            "condition.root.children.0",
            "HOUSE_LORDS_COMBINATION",
        )
    ]

    dhana = batch.records[1]
    assert dhana.definition_disposition is YogaDefinitionDisposition.INVALID
    assert dhana.status is PredicateStatus.ERROR and not dhana.matched
    assert isinstance(dhana.condition_result, ConditionResult)
    first = dhana.condition_result.children[0].result
    assert first is not None and first.status is PredicateStatus.ERROR
    assert [error.code for error in first.errors] == ["unknown_condition_type"]

    row = project_yoga_compatibility(batch)[1]
    assert row == {
        "yoga_id": "dhana_naive",
        "name": "Naive Dhana Yoga",
        "matched": False,
        "planets": [],
        "houses": [],
        "aspects_used": [],
        "evidence": {
            "children": [
                {"reason": "unknown_predicate", "predicate": "HOUSE_LORDS_COMBINATION"},
                {},
            ]
        },
        "trace_id": "b22d9d47-4603-5812-9436-5867f90b73a2",
    }


def test_wp13_typed_full_and_complete_compatibility_hashes_are_unchanged():
    _, batch = _batch()
    logical = yoga_batch_logical_json_bytes(batch)
    full = yoga_batch_full_json_bytes(batch)
    compatibility = json.dumps(
        project_yoga_compatibility(batch), ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")

    assert (len(logical), hashlib.sha256(logical).hexdigest()) == (
        20547,
        "f8cd75725599f26c03e574639395aee3dffd61d3e19d9072cfbac5df8f780ac2",
    )
    assert (len(full), hashlib.sha256(full).hexdigest()) == (
        20948,
        "f1e90b6b5153d2655dd89f9ff5762ca50dc8e5391f5b142de0581d5ef90bfaa4",
    )
    assert (len(compatibility), hashlib.sha256(compatibility).hexdigest()) == (
        1361,
        "d6ad3c317cd8f5388e0630e528238f099910499a2863f9c14aab13e7b5de079e",
    )
