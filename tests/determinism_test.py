import hashlib
import json
from systems.Parasara.tools.generate_snapshot import generate

INPUT = 'systems/Parasara/fixtures/golden_chart_01.json'

def test_determinism_runs():
    N = 100
    hashes = set()
    for i in range(N):
        out = generate(INPUT, '-')
        s = json.dumps(out, sort_keys=True)
        h = hashlib.sha256(s.encode('utf-8')).hexdigest()
        hashes.add(h)
    assert len(hashes) == 1, f"Determinism failed: {len(hashes)} unique outputs after {N} runs"
