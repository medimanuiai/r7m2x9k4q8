import json
from pathlib import Path
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from tests.testing_framework.coverage_engine import CoverageEngine
from tests.testing_framework.rule_coverage import run_rule_coverage_scan


def generate_report(input_chart: str, out_dir: str = 'tests/reports') -> str:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    chart = SuryaAdapter.load(input_chart)
    astro = chart_to_astrostate(chart)
    ce = CoverageEngine()
    # prefer model_dump if AstroState provides it
    astro_dict = getattr(astro, 'model_dump', None)
    if callable(astro_dict):
        ce.ingest_astro(astro.model_dump())
    else:
        ce.ingest_astro(astro.diagnostics if hasattr(astro, 'diagnostics') else astro.__dict__)

    # Run rule coverage and ingest
    rule_summary = run_rule_coverage_scan(astro)
    ce.ingest_rule_coverage(rule_summary)

    out_path = Path(out_dir) / 'coverage_report.json'
    ce.save(str(out_path))
    return str(out_path)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: generate_coverage_report.py input_chart.json [out_dir]')
        raise SystemExit(2)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else 'tests/reports'
    print(generate_report(inp, out))
