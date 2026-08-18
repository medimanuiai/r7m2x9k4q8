"""Static Prompt-03 ownership and dependency boundaries."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "systems" / "Parasara" / "engine"


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_exactly_one_generic_inference_engine_and_no_domain_engines():
    definitions = []
    for path in ENGINE.rglob("*.py"):
        tree = ast.parse(source(path))
        definitions.extend((path, node.name) for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name.endswith("InferenceEngine"))
    assert definitions == [(ENGINE / "inference" / "engine.py", "InferenceEngine")]


def test_inference_has_no_chart_predicate_yaml_or_output_dependencies():
    text = "\n".join(source(path) for path in (ENGINE / "inference").glob("*.py"))
    for forbidden in (
        "AstroState", "SuryaAdapter", "PredicateEvaluator", "yaml", "interpret_career",
        "generate_snapshot", "OutputAssembler", "DomainPrediction",
    ):
        assert forbidden not in text


def test_career_no_longer_owns_generic_scoring_or_confidence():
    text = source(ENGINE / "interpreters" / "career.py")
    assert "compute_confidence" not in text
    assert "scoring_breakdown" not in text
    assert "confidence_mod" not in text
    assert text.count(".aggregate(") == 1


def test_predicates_and_rule_engine_do_not_import_inference():
    for path in (ENGINE / "rules").glob("*.py"):
        assert "engine.inference" not in source(path), path

