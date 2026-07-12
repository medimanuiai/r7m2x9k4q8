#!/usr/bin/env python3
"""Generate full artifacts for a single canonical chart for validation.

Outputs (under tests/reports/artifacts/):
- raw_surya.json
- astrostate.json
- rule_traces.json
- domain_prediction.json
- rashi_chart.svg
- dashas.json
- transits.json
- explainability.json
- test_summary.json
"""
import json
from pathlib import Path
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules import loader
from systems.Parasara.engine.rules import runtime


OUTDIR = Path('tests/reports/artifacts')
OUTDIR.mkdir(parents=True, exist_ok=True)


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


def run_rules_and_trace(astro):
    # ensure rules loaded
    rules_path = Path('systems/Parasara/rules/parashara/v1')
    loader.load_rules_from_dir(str(rules_path))
    traces = []
    career_traces = []
    for rid, rule in loader.RULE_REGISTRY.items():
        try:
            rm = runtime.evaluate_rule_with_score(astro, dict(rule))
        except Exception as e:
            rm = {'rule_id': rid, 'matched': False, 'evidence': {'error': str(e)}, 'adjusted_score': 0.0}
        traces.append(rm)
        # select career-related rules heuristically: house==10 or id contains '10' or type in known set
        is_career = False
        if isinstance(rule, dict):
            if rule.get('house') == 10:
                is_career = True
            if '10' in str(rule.get('id') or ''):
                is_career = True
            if rule.get('type') in ('lord_status', 'strong_in_10', 'rajayoga_naive', 'aspect_on_house'):
                is_career = True
        if is_career:
            career_traces.append(rm)

    p = OUTDIR / 'rule_traces.json'
    p.write_text(json.dumps(traces, indent=2))
    p2 = OUTDIR / 'career_rule_traces.json'
    p2.write_text(json.dumps(career_traces, indent=2))
    return traces, career_traces


def synthesize_domain_prediction(career_traces):
    total = 0.0
    contributors = []
    for t in career_traces:
        score = float(t.get('adjusted_score') or t.get('adjustedScore') or 0.0)
        matched = bool(t.get('matched'))
        if matched:
            total += score
        contributors.append({'rule_id': t.get('rule_id'), 'matched': matched, 'evidence': t.get('evidence'), 'contribution': score})

    # normalize to 0..1 by simple heuristic
    norm = min(1.0, total)
    pred = {
        'domain': 'career',
        'score': round(norm, 3),
        'confidence': 0.75 if norm > 0.1 else 0.35,
        'contributors': contributors,
        'explainability': {'summary': f'{len([c for c in contributors if c["matched"]])} contributing rules'}
    }
    p = OUTDIR / 'domain_prediction.json'
    p.write_text(json.dumps(pred, indent=2))
    return pred


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


def save_explainability(pred):
    p = OUTDIR / 'explainability.json'
    p.write_text(json.dumps(pred.get('explainability', {}), indent=2))
    return pred.get('explainability', {})


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
    pred = synthesize_domain_prediction(career_traces)
    svg = render_rashi_svg(astro)
    dashas, transits = save_dashas_and_transits(astro)
    explain = save_explainability(pred)
    tests_out = run_tests_summary()
    print('Artifacts generated under', OUTDIR)


if __name__ == '__main__':
    main()
