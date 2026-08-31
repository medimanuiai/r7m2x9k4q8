"""Emit the deterministic Prompt-05 logical scenario manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.domain import (
    DashaTimelineFactory,
    DomainBuildProduced,
    TransitSummaryFactory,
    prompt05_model_logical_json_bytes,
)
from systems.Parasara.engine.enrichments.yoga_engine import (
    build_yoga_snapshot,
    evaluate_yoga_snapshot,
    evaluate_yoga_diagnostics,
    load_yoga_rule_source,
)
from systems.Parasara.engine.interpreters.career import interpret_career_domain
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.tools.generate_snapshot import assemble_output


FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> None:
    rows = []
    for fixture in (
        "golden_chart_01.json",
        "surya_test_chart.json",
        "surya_generated_chart.json",
    ):
        astro = chart_to_astrostate(SuryaAdapter.load(FIXTURES / fixture))
        outcome = interpret_career_domain(astro)
        if not isinstance(outcome, DomainBuildProduced):
            raise AssertionError("Career domain build rejected")
        payload = prompt05_model_logical_json_bytes(outcome.prediction)
        public = json.dumps(
            assemble_output(astro), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        rows.append({
            "fixture": fixture,
            "career_bytes": len(payload),
            "career_sha256": digest(payload),
            "public_sha256": digest(public),
        })
    astro = chart_to_astrostate(SuryaAdapter.load(FIXTURES / "golden_chart_01.json"))
    diagnostics = evaluate_yoga_diagnostics(astro)
    rows.append({
        "yoga_digests": [item.logical_digest for item in diagnostics],
        "dasha_unavailable": DashaTimelineFactory.unavailable().logical_digest,
        "transit_unavailable": TransitSummaryFactory.unavailable().logical_digest,
    })
    print(json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
