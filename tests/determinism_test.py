import hashlib
import json
from pathlib import Path
from systems.Parasara.tools.generate_snapshot import generate

INPUT = 'systems/Parasara/fixtures/golden_chart_01.json'

def test_determinism_runs(tmp_path):
    N = 100
    hashes = set()
    repository_dash = Path(__file__).resolve().parents[1] / '-'
    dash_before = repository_dash.read_bytes() if repository_dash.exists() else None
    output_path = tmp_path / 'determinism-snapshot.json'
    for i in range(N):
        out = generate(INPUT, str(output_path))
        s = json.dumps(out, sort_keys=True)
        h = hashlib.sha256(s.encode('utf-8')).hexdigest()
        hashes.add(h)
    assert len(hashes) == 1, f"Determinism failed: {len(hashes)} unique outputs after {N} runs"
    dash_after = repository_dash.read_bytes() if repository_dash.exists() else None
    assert dash_after == dash_before, "snapshot generation modified the repository-root '-' artifact"
