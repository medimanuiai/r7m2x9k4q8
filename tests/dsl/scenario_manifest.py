"""Emit one cross-interpreter Prompt-07 deterministic scenario digest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from systems.Parasara.engine.rules.canonical import canonical_json_bytes
from systems.Parasara.engine.rules.dsl import AnalysisSucceeded, RuleDslCompiler


def main() -> None:
    rows = []
    for name in ("minimal.yaml", "macros.yaml"):
        payload = (ROOT / "tests/dsl/fixtures" / name).read_bytes()
        result = RuleDslCompiler.analyze_source(
            source_id=f"synthetic/scenario/{name}", payload=payload
        )
        if not isinstance(result, AnalysisSucceeded):
            raise SystemExit("Prompt-07 scenario compilation failed")
        analyzed = result.analyzed_rule_set
        rows.append({
            "name": name,
            "canonical_dsl_sha256": analyzed.canonical_dsl_sha256,
            "expanded_ast_sha256": analyzed.expanded_ast_sha256,
            "compiled_rule_set_sha256": analyzed.compiled_rule_set_sha256,
            "logical": analyzed.logical_projection(),
        })
    payload = canonical_json_bytes({"scenario_schema_version": "1.0.0", "rows": rows})
    print(json.dumps({
        "prompt07_scenario_manifest_sha256": hashlib.sha256(payload).hexdigest(),
        "scenario_bytes": len(payload),
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
