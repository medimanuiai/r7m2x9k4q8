"""Emit deterministic Prompt-06 rule-versioning identities for validator comparison."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.enrichments.yoga_engine import evaluate_yoga_diagnostics
from systems.Parasara.engine.interpreters.career import interpret_career, interpret_career_domain
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.versioning import (
    RuleVersionResolver,
    compatibility_v1_config,
    manifest_canonical_json_bytes,
)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    resolved = RuleVersionResolver().resolve(compatibility_v1_config())
    manifest_bytes = manifest_canonical_json_bytes(resolved.manifest)
    rows: dict[str, object] = {
        "lifecycle": resolved.lifecycle.value,
        "manifest_bytes": len(manifest_bytes),
        "manifest_fingerprint_sha256": resolved.manifest_fingerprint_sha256,
        "manifest_sha256": digest(manifest_bytes),
        "predicate_component_fingerprint_sha256": resolved.predicate_component_fingerprint_sha256,
    }
    charts: dict[str, object] = {}
    for name in ("golden_chart_01.json", "surya_test_chart.json", "surya_generated_chart.json"):
        path = ROOT / "systems" / "Parasara" / "fixtures" / name
        astro = chart_to_astrostate(SuryaAdapter.load(str(path)))
        outcome = interpret_career_domain(astro, resolved_versions=resolved)
        prediction = outcome.prediction
        public = json.dumps(
            interpret_career(astro), ensure_ascii=False, separators=(",", ":"),
        ).encode("utf-8")
        diagnostics = evaluate_yoga_diagnostics(astro, resolved_versions=resolved)
        yoga_rows = [
            {"yoga_id": item.yoga_id, "matched": item.matched, "rule_version": item.rule_version}
            for item in diagnostics
        ]
        yoga_public = json.dumps(
            yoga_rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
        charts[name] = {
            "career_score": prediction.score,
            "career_confidence": prediction.confidence,
            "career_engine_version": prediction.engine_version,
            "career_rule_set_version": prediction.rule_set_version,
            "public_bytes": len(public),
            "public_sha256": digest(public),
            "yoga_count": len(diagnostics),
            "yoga_bytes": len(yoga_public),
            "yoga_sha256": digest(yoga_public),
        }
    rows["charts"] = charts
    print(json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
