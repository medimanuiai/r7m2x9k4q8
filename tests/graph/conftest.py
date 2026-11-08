from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from systems.Parasara.engine.rules.dsl import RuleDslCompiler, AnalysisSucceeded
from systems.Parasara.engine.rules.graph import RuleGraphCompiler, GraphAnalysisSucceeded
from tests.versioning.conftest import SyntheticCatalogBuilder

FIXTURES = Path(__file__).parent / "fixtures"


def document(count=4, edges=(), version="fixture-v1"):
    rows = [dict(rule_id=f"synthetic.{chr(97+i) if i < 26 else 'n'+str(i)}", revision="1.0.0",
                 requires_matches=[], requires_absence=[], optional_supports=[]) for i in range(count)]
    for prerequisite, dependent, kind in edges:
        rows[dependent][kind].append({key: rows[prerequisite][key] for key in ("rule_id", "revision")})
    return dict(graph_schema_version="1.0.0", system="synthetic", rule_set_family="prompt08_fixture",
                rule_set_version=version, rules=rows)


def dsl_payload(count=4, version="fixture-v1"):
    source = (FIXTURES / "rules.yaml").read_text(encoding="utf-8")
    header, body = source.split("rules:\n", 1)
    first = body.split("\n  - id:")[0].rstrip() + "\n"
    return (header.replace("fixture-v1", version) + "rules:\n" + "".join(
        first.replace("synthetic.a", row["rule_id"]).replace("house: 1", f"house: {i % 12 + 1}")
        for i, row in enumerate(document(count)["rules"]))).encode()


def analyze(data=None, *, payload=None, dsl=None, source_id="synthetic/dependencies.json"):
    result = RuleDslCompiler.analyze_source(source_id="synthetic/rules.yaml", payload=dsl or dsl_payload())
    assert isinstance(result, AnalysisSucceeded), result
    return RuleGraphCompiler.analyze_source(source_id=source_id,
        payload=payload if payload is not None else json.dumps(data or document()).encode(),
        analyzed_rule_set=result.analyzed_rule_set, dsl_source_artifact_id="dsl.synthetic")


def codes(result):
    return tuple(item.code for item in result.diagnostics)


@pytest.fixture
def graph_pack(tmp_path):
    def build(data=None, *, payload=None, **lifecycle):
        data = data or document()
        builder = SyntheticCatalogBuilder(tmp_path)
        pack = builder.add_graph(source_id="synthetic/rules.yaml",
            payload=payload or dsl_payload(len(data["rules"]), data["rule_set_version"]),
            graph_source_id="synthetic/dependencies.json", graph_payload=json.dumps(data).encode(), **lifecycle)
        authority = pack.resolver.resolve(pack.config)
        compiled = RuleDslCompiler(resolved_versions=authority).compile_authorized(source_id=pack.dsl_source_id).compiled_rule_set
        compiler = RuleGraphCompiler(resolved_versions=authority)
        result = compiler.compile_authorized(compiled_rule_set=compiled)
        assert result.plan is not None, result
        return pack, authority, compiled, compiler, result.plan
    return build
