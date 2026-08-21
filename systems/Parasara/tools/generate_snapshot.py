"""Generate a minimal Parāśara output JSON from `fixtures/golden_chart_01.json`.

This is a lightweight assembler used for snapshot verification in tests/SME review.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.astrostate import AstroState
from systems.Parasara.engine.astrostate_api import (
    AstroStateBuildFailure,
    AstroStateSnapshot,
    freeze_astrostate,
    thaw_value,
)
from systems.Parasara.engine.capability import CapabilityReadiness
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.interpreters.career import interpret_career_snapshot


def assemble_snapshot_output(snapshot: AstroStateSnapshot):
    """Compatibility JSON assembler reading one immutable factual snapshot."""

    planet_strengths = {}
    planets = snapshot.get_planets()
    if planets.value_present:
        for planet in planets.value:
            result = snapshot.get_planet_strength(planet.planet_id)
            if result.value_present:
                detail = result.value.value.get("detail")
                planet_strengths[planet.planet_id] = (
                    thaw_value(detail)
                    if detail else result.value.value.get("value")
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
            "lagna_summary": (
                thaw_value(snapshot.get_lagna_summary().value)
                if snapshot.get_lagna_summary().value_present else {}
            ),
            "planet_strengths": public_planet_strengths,
            "houses": _snapshot_houses(snapshot),
            "aspects": _snapshot_aspects(snapshot),
            "yogas": [],
        },
        "domains": {
            "career": interpret_career_snapshot(snapshot),
            "wealth": {"summary": "", "score": 0.5, "confidence": 0.5, "components": [], "indicators": []},
        },
        "dasha_timeline": [],
        "transits": [],
        "explainability": {"indicators_legend": {}, "scoring_formula": {}, "conflict_resolution_policy": {}},
    }


def _snapshot_houses(snapshot: AstroStateSnapshot):
    summaries = snapshot.get_house_summaries()
    if summaries.value_present:
        return [thaw_value(item) for item in summaries.value]
    houses = snapshot.get_houses()
    if not houses.value_present:
        return []
    return [
        {"number": item.house_number, "sign": item.sign}
        for item in houses.value
    ]


def _snapshot_aspects(snapshot: AstroStateSnapshot):
    whole = snapshot.inspect_capability("aspects.whole_sign_graph")
    representation = (
        "whole_sign_graph"
        if whole.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY)
        else "basic_conjunction_list"
    )
    result = snapshot.get_aspect_representation(representation)
    return thaw_value(result.value) if result.value_present else {}


def assemble_output(astro: AstroState | AstroStateSnapshot):
    """Narrow mutable-AstroState compatibility wrapper through freeze."""

    if isinstance(astro, AstroStateSnapshot):
        return assemble_snapshot_output(astro)
    build = freeze_astrostate(astro)
    if isinstance(build, AstroStateBuildFailure):
        raise ValueError("AstroState snapshot construction failed")
    return assemble_snapshot_output(build.snapshot)


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
