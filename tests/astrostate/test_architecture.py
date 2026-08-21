from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "systems" / "Parasara" / "engine"


def parsed(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"))


def function_node(path: Path, name: str) -> ast.FunctionDef:
    return next(
        node for node in ast.walk(parsed(path))
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


def assignment_root(node: ast.AST) -> str | None:
    while isinstance(node, (ast.Attribute, ast.Subscript)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def test_general_astrostate_boundary_does_not_depend_on_consumers_or_producers():
    path = ENGINE / "astrostate_api.py"
    tree = parsed(path)
    imports = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not any(
        part in item
        for item in imports
        for part in (".rules", ".interpreters", ".inference", ".enrichments", ".adapter")
    )
    freeze = function_node(path, "freeze_astrostate")
    calls = {
        node.func.id for node in ast.walk(freeze)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not calls & {
        "compute_aspect_graph", "compute_functional_roles", "compute_planet_strengths",
        "compute_vimshottari", "interpret_career", "evaluate_yoga_rules",
    }


def test_canonical_consumers_do_not_traverse_mutable_astrostate_fields():
    targets = (
        (ENGINE / "interpreters" / "career.py", "prepare_career_snapshot"),
        (ENGINE / "enrichments" / "yoga_engine.py", "evaluate_yoga_snapshot"),
        (ROOT / "systems" / "Parasara" / "tools" / "generate_snapshot.py", "assemble_snapshot_output"),
    )
    forbidden = {"planets", "houses", "enrichments", "derived", "lagna_sign", "metadata"}
    for path, name in targets:
        node = function_node(path, name)
        attributes = {
            item.attr for item in ast.walk(node) if isinstance(item, ast.Attribute)
        }
        assert not attributes & forbidden, (path, name, attributes & forbidden)


def test_protected_predicate_module_has_no_astrostate_dependency():
    path = ENGINE / "rules" / "prepared_state.py"
    imports = {
        node.module or ""
        for node in ast.walk(parsed(path))
        if isinstance(node, ast.ImportFrom)
    }
    assert not any("astrostate" in item.lower() for item in imports)


def test_compatibility_wrappers_are_narrow_and_canonical_entry_points_exist():
    yoga = parsed(ENGINE / "enrichments" / "yoga_engine.py")
    career = parsed(ENGINE / "interpreters" / "career.py")
    snapshot = parsed(ROOT / "systems" / "Parasara" / "tools" / "generate_snapshot.py")
    assert {node.name for node in ast.walk(yoga) if isinstance(node, ast.FunctionDef)} >= {
        "build_yoga_snapshot", "evaluate_yoga_snapshot", "evaluate_yoga_rules",
    }
    assert {node.name for node in ast.walk(career) if isinstance(node, ast.FunctionDef)} >= {
        "prepare_career_snapshot", "interpret_career_snapshot", "interpret_career",
    }
    assert {node.name for node in ast.walk(snapshot) if isinstance(node, ast.FunctionDef)} >= {
        "assemble_snapshot_output", "assemble_output", "generate",
    }


def test_every_canonical_aspect_query_requires_representation():
    tree = parsed(ENGINE / "astrostate_api.py")
    methods = {
        node.name: tuple(arg.arg for arg in node.args.args)
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("get_aspects_")
    }
    assert methods
    assert all("representation" in arguments for arguments in methods.values())


def test_mutable_astrostate_assignments_are_confined_to_reviewed_construction_paths():
    allowed = {
        ENGINE / "normalizer.py",
        ENGINE / "enrichments" / "aspects.py",
        ENGINE / "enrichments" / "varga.py",
        ENGINE / "enrichments" / "yoga_engine.py",
    }
    found = set()
    for path in ENGINE.rglob("*.py"):
        tree = parsed(path)
        targets = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets.extend(node.targets if isinstance(node, ast.Assign) else (node.target,))
        if any(
            isinstance(target, (ast.Attribute, ast.Subscript))
            and assignment_root(target) == "astro"
            for target in targets
        ):
            found.add(path)
    assert found <= allowed


def test_snapshot_query_methods_have_no_mutation_raw_escape_or_impure_calls():
    tree = parsed(ENGINE / "astrostate_api.py")
    snapshot_class = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "AstroStateSnapshot"
    )
    methods = tuple(
        node for node in snapshot_class.body
        if isinstance(node, ast.FunctionDef)
        and node.name.startswith(("get_", "inspect_", "list_", "_aspect", "_entity", "_collection", "_content", "_capability"))
    )
    forbidden_calls = {
        "open", "getenv", "time", "random", "create_connection", "log",
        "compute_aspect_graph", "compute_functional_roles", "compute_planet_strengths",
        "chart_to_astrostate", "SuryaAdapter",
    }
    for method in methods:
        assignments = [
            target
            for node in ast.walk(method)
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign))
            for target in (node.targets if isinstance(node, ast.Assign) else (node.target,))
        ]
        assert not any(assignment_root(target) == "self" for target in assignments)
        names = {
            node.id for node in ast.walk(method) if isinstance(node, ast.Name)
        } | {
            node.attr for node in ast.walk(method) if isinstance(node, ast.Attribute)
        }
        assert not names & forbidden_calls, (method.name, names & forbidden_calls)
        assert "enrichments" not in names


def test_canonical_consumers_have_no_raw_input_or_post_freeze_mutable_access():
    targets = (
        (ENGINE / "interpreters" / "career.py", "prepare_career_snapshot"),
        (ENGINE / "enrichments" / "yoga_engine.py", "evaluate_yoga_snapshot"),
        (ROOT / "systems" / "Parasara" / "tools" / "generate_snapshot.py", "assemble_snapshot_output"),
    )
    forbidden_names = {"Chart", "SuryaAdapter", "request", "payload"}
    forbidden_attributes = {"enrichments", "derived", "lagna_sign", "metadata", "houses", "planets"}
    for path, name in targets:
        node = function_node(path, name)
        names = {
            item.id for item in ast.walk(node) if isinstance(item, ast.Name)
        }
        attributes = {
            item.attr for item in ast.walk(node) if isinstance(item, ast.Attribute)
        }
        assert not names & forbidden_names, (path, name, names & forbidden_names)
        assert not attributes & forbidden_attributes, (path, name, attributes & forbidden_attributes)

    varga_source = (ROOT / "systems" / "Parasara" / "tools" / "varga_dump.py").read_text(encoding="utf-8")
    assert "astro.enrichments" not in varga_source
    assert "astro.metadata" not in varga_source


def test_no_generic_enrichment_escape_or_prompt05_scope_exists():
    path = ENGINE / "astrostate_api.py"
    tree = parsed(path)
    classes = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    assert "get_enrichment" not in functions
    assert not classes & {"DomainPrediction", "OutputAssembler", "DomainInterpreter"}
    snapshot = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "AstroStateSnapshot")
    fields = {
        node.target.id for node in snapshot.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    assert not fields & {"score", "confidence", "narrative", "rule_matches", "domain_output"}
