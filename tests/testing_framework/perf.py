import time
import json
from systems.Parasara.tools.generate_snapshot import generate
from pathlib import Path

BASE = 'systems/Parasara/fixtures/golden_chart_01.json'


def measure_runs(input_chart: str, runs: int = 10):
    times = []
    for i in range(runs):
        t0 = time.perf_counter()
        generate(input_chart, '-')
        t1 = time.perf_counter()
        times.append(t1 - t0)
    times.sort()
    return {'min': times[0], 'median': times[len(times)//2], 'p90': times[int(len(times)*0.9)], 'max': times[-1]}


def baseline_and_check(input_chart: str, baseline_file: str = 'tests/perf_baseline.json', threshold: float = 0.1):
    p = Path(baseline_file)
    stats = measure_runs(input_chart, runs=5)
    if not p.exists():
        with p.open('w', encoding='utf-8') as fh:
            json.dump(stats, fh, indent=2)
        return {'baseline_created': True, 'stats': stats}
    else:
        with p.open('r', encoding='utf-8') as fh:
            base = json.load(fh)
        # compare max against baseline max + threshold
        if stats['max'] > base.get('max', 0) + threshold:
            return {'regression': True, 'stats': stats, 'baseline': base}
        return {'regression': False, 'stats': stats, 'baseline': base}
