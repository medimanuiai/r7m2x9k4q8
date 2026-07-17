#!/usr/bin/env python3
"""Generate full artifacts for a single canonical chart for validation.

Outputs (under tests/reports/artifacts/):
- raw_surya.json
- astrostate.json
- rule_traces.json
- career_rule_traces.json
- rashi_chart.svg
- dashas.json
- transits.json
- test_summary.json
"""
import json
from pathlib import Path
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.interpreters.career_models import (
    career_evaluation_batch_to_logical_data,
)
from systems.Parasara.engine.rules.canonical import canonical_json_data
from systems.Parasara.engine.enrichments.yoga_engine import yoga_batch_to_logical_data
from tests.testing_framework.typed_rule_evaluation import evaluate_typed_rule_surfaces


OUTDIR = Path('tests/reports/artifacts')


def _output_dir(out_dir=None):
    path = OUTDIR if out_dir is None else Path(out_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_json(path, value):
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False),
        encoding='utf-8',
    )


def save_raw_surya(chart_path: str):
    chart = SuryaAdapter.load(chart_path)
    # prefer model_dump
    try:
        data = chart.model_dump()
    except Exception:
        # fallback to __dict__ like structure
        data = chart.__dict__
    p = OUTDIR / 'raw_surya.json'
    p.write_text(json.dumps(data, indent=2))
    return chart, data


def save_astrostate(chart):
    astro = chart_to_astrostate(chart)
    try:
        ad = astro.model_dump()
    except Exception:
        ad = getattr(astro, '__dict__', {})
    p = OUTDIR / 'astrostate.json'
    p.write_text(json.dumps(ad, indent=2))
    return astro, ad


def run_rules_and_trace(astro, out_dir=None):
    """Write deterministic logical projections from the active typed owners."""

    surfaces = evaluate_typed_rule_surfaces(astro)
    yoga_data = canonical_json_data(yoga_batch_to_logical_data(surfaces.yoga))
    career_data = canonical_json_data(
        career_evaluation_batch_to_logical_data(surfaces.career)
    )
    traces = yoga_data['records']
    career_traces = career_data['candidates']
    destination = _output_dir(out_dir)
    _write_json(destination / 'rule_traces.json', traces)
    _write_json(destination / 'career_rule_traces.json', career_traces)
    return traces, career_traces


def render_rashi_svg(astro):
    # Build mapping house -> planets
    house_map = {i: [] for i in range(1, 13)}
    for p in getattr(astro, 'planets', []) or []:
        h = getattr(p, 'house', None)
        if h and 1 <= h <= 12:
            house_map[h].append(getattr(p, 'name', str(p)))

    # Simple 4x3 grid SVG
    cell_w = 150
    cell_h = 100
    cols = 4
    rows = 3
    width = cell_w * cols
    height = cell_h * rows
    svg_lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    sign_names = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
    # map house numbers 1..12 into grid positions row-major
    for i in range(12):
        r = i // cols
        c = i % cols
        x = c * cell_w
        y = r * cell_h
        hnum = i + 1
        svg_lines.append(f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" fill="white" stroke="black"/>')
        svg_lines.append(f'<text x="{x+8}" y="{y+18}" font-size="12">House {hnum} ({sign_names[i]})</text>')
        # planets
        pl = house_map.get(hnum, [])
        for idx, pn in enumerate(pl):
            svg_lines.append(f'<text x="{x+8}" y="{y+36+14*idx}" font-size="12">{pn}</text>')
    svg_lines.append('</svg>')
    p = OUTDIR / 'rashi_chart.svg'
    p.write_text('\n'.join(svg_lines))
    return str(p)


def save_dashas_and_transits(astro):
    dashas = None
    transits = None
    # try derived/enrichments
    ed = getattr(astro, 'derived', None) or getattr(astro, 'enrichments', {}) or {}
    dashas = ed.get('dashas') or ed.get('dasha') or []
    transits = ed.get('transits') or ed.get('current_transits') or []
    p = OUTDIR / 'dashas.json'
    p.write_text(json.dumps(dashas, indent=2))
    q = OUTDIR / 'transits.json'
    q.write_text(json.dumps(transits, indent=2))
    return dashas, transits


def run_tests_summary():
    # attempt to run pytest and capture summary counts
    import subprocess, shlex, sys
    try:
        cmd = [sys.executable, '-m', 'pytest', '-q']
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        out = res.stdout + '\n' + res.stderr
    except Exception as e:
        out = f'pytest run failed: {e}'
    p = OUTDIR / 'test_summary.txt'
    p.write_text(out)
    return out


def main():
    chart_path = 'systems/Parasara/fixtures/golden_chart_01.json'
    chart, raw = save_raw_surya(chart_path)
    astro, astro_dict = save_astrostate(chart)
    traces, career_traces = run_rules_and_trace(astro)
    svg = render_rashi_svg(astro)
    dashas, transits = save_dashas_and_transits(astro)
    tests_out = run_tests_summary()
    print('Artifacts generated under', OUTDIR)


if __name__ == '__main__':
    main()
