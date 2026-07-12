from typing import List, Dict, Optional, Any
import json
def generate_html_report(results: List[Dict[str, Any]], coverage: Dict[str, int], out_path: str, perf_stats: Optional[Dict[str, Any]] = None, missing: Optional[Dict[str, Any]] = None) -> str:
    lines = []
    lines.append('<html><body>')
    lines.append('<h1>Jyothishyam Test Report</h1>')
    passed = sum(1 for r in results if r.get('result', {}).get('matched'))
    lines.append(f'<p>Passed: {passed} / {len(results)}</p>')
    if perf_stats:
        lines.append('<h2>Performance</h2>')
        lines.append('<ul>')
        for k, v in perf_stats.items():
            lines.append(f'<li>{k}: {v}</li>')
        lines.append('</ul>')

    lines.append('<h2>Results</h2>')
    lines.append('<ul>')
    for r in results:
        ok = r.get('result', {}).get('matched')
        lines.append(f"<li>{r.get('id')}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            lines.append('<pre>')
            lines.append(json.dumps(r.get('result', {}).get('diff'), indent=2))
            lines.append('</pre>')
        lines.append('</li>')
    lines.append('</ul>')

    lines.append('<h2>Coverage</h2>')
    lines.append('<ul>')
    for k, v in coverage.items():
        lines.append(f'<li>{k}: {v}</li>')
    lines.append('</ul>')

    if missing:
        lines.append('<h2>Missing Scenarios</h2>')
        lines.append('<pre>')
        lines.append(json.dumps(missing, indent=2))
        lines.append('</pre>')

    lines.append('</body></html>')
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))
    return out_path
