"""Generate a minimal Parāśara output JSON from `fixtures/golden_chart_01.json`.

This is a lightweight assembler used for snapshot verification in tests/SME review.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.interpreters.career import interpret_career


def assemble_output(astro):
    planet_strengths = astro.enrichments.get(
        'planet_strengths', {p.name: p.strength for p in astro.planets}
    )
    public_planet_strengths = {
        name: ({key: value for key, value in row.items() if key != 'shadbala'} if isinstance(row, dict) else row)
        for name, row in planet_strengths.items()
    }
    return {
        "engine": {
            "name": "jyothishyam-parashara",
            "engine_version": "0.1.0",
            "rule_set_family": "parashara",
            "rule_set_version": "v1",
        },
        "meta": {
            "engine_version": "jyothishyam-parashara@0.1.0",
            "generated_at": None,
        },
        "diagnostics": {
            "lagna_summary": astro.diagnostics.get('lagna_summary', {}),
            "planet_strengths": public_planet_strengths,
            "houses": astro.enrichments.get('house_summaries', astro.houses),
            "aspects": astro.enrichments.get('aspects', {}),
            "yogas": [],
        },
        "domains": {
            "career": interpret_career(astro),
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
    # keep generated_at deterministic (None) for snapshot comparisons
    out.setdefault('meta', {})['generated_at'] = None
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
