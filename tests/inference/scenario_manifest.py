"""Emit deterministic Prompt-03 logical identities for validator comparison."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.inference import (
    InferenceEngine,
    inference_result_logical_json_bytes,
    load_inference_config,
)
from systems.Parasara.engine.interpreters.career import (
    career_data_completeness,
    career_inference_rule_matches,
    evaluate_career_batch,
    infer_career,
    interpret_career,
    prepare_career_facts,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    rows = {}
    for name in ("golden_chart_01.json", "surya_test_chart.json", "surya_generated_chart.json"):
        path = ROOT / "systems" / "Parasara" / "fixtures" / name
        astro = chart_to_astrostate(SuryaAdapter.load(str(path)))
        batch = evaluate_career_batch(prepare_career_facts(astro))
        first = infer_career(batch)
        shuffled = InferenceEngine().aggregate(
            domain="career",
            rule_matches=tuple(reversed(career_inference_rule_matches(batch, load_inference_config()))),
            timing_context=None,
            data_completeness=career_data_completeness(batch),
            config=load_inference_config(),
        )
        logical = inference_result_logical_json_bytes(first)
        if inference_result_logical_json_bytes(shuffled) != logical:
            raise RuntimeError("shuffled inference changed logical output")
        public = json.dumps(
            interpret_career(astro), ensure_ascii=False, separators=(",", ":"),
        ).encode("utf-8")
        rows[name] = {
            "inference_bytes": len(logical),
            "inference_sha256": digest(logical),
            "public_bytes": len(public),
            "public_sha256": digest(public),
        }
    print(json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
