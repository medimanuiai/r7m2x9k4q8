from typing import List, Dict


def generate_html_report(results: List[Dict], coverage: Dict[str, int], out_path: str):
    lines = []
    lines.append('<html><body>')
    lines.append('<h1>Jyothishyam Test Report</h1>')
    lines.append(f'<p>Passed: {sum(1 for r in results if r["result"].get("matched"))} / {len(results)}</p>')
    lines.append('<h2>Results</h2>')
    lines.append('<ul>')
    for r in results:
        ok = r['result'].get('matched')
        lines.append(f"<li>{r['id']}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            lines.append(f"<pre>{r['result'].get('diff')}</pre>")
        lines.append('</li>')
    lines.append('</ul>')
    lines.append('<h2>Coverage</h2>')
    lines.append('<ul>')
    for k, v in coverage.items():
        lines.append(f'<li>{k}: {v}</li>')
    lines.append('</ul>')
    lines.append('</body></html>')
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))
    return out_path
