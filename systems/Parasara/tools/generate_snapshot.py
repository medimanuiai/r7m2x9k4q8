"""Generate a minimal Parāśara output JSON from `fixtures/golden_chart_01.json`.

This is a lightweight assembler used for snapshot verification in tests/SME review.
"""
import json
from pathlib import Path

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate


def assemble_output(astro):
    return {
        "engine": {
            "name": "jyothishyam-parashara",
            "engine_version": "0.1.0",
            "rule_set_family": "parashara",
            "rule_set_version": "v1",
        },
        "diagnostics": {
            "lagna_summary": {},
            "planet_strengths": {p.name: p.strength for p in astro.planets},
            "yogas": [],
        },
        "domains": {
            "career": {"summary": "", "score": 0.5, "confidence": 0.5, "components": [], "indicators": []},
            "wealth": {"summary": "", "score": 0.5, "confidence": 0.5, "components": [], "indicators": []},
        },
        "dasha_timeline": [],
        "transits": [],
        "explainability": {"indicators_legend": {}, "scoring_formula": {}, "conflict_resolution_policy": {}},
    }


def generate(input_path: str, out_path: str):
    chart = SuryaAdapter.load(input_path)
    astro = chart_to_astrostate(chart)
    out = assemble_output(astro)
    Path(out_path).write_text(json.dumps(out, indent=2, sort_keys=True))
    return out


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('input')
    p.add_argument('out')
    args = p.parse_args()
    generate(args.input, args.out)


if __name__ == '__main__':
    main()
