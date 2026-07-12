import json
from pathlib import Path

from systems.Parasara.tools.generate_snapshot import generate


def test_vertical_slice_matches_snapshot(tmp_path):
    input_path = Path('systems/Parasara/fixtures/golden_chart_01.json')
    approved_snapshot = Path('systems/Parasara/tests/snapshots/output_golden_chart_01.json')

    assert input_path.exists(), f"Golden fixture not found: {input_path}"
    assert approved_snapshot.exists(), f"Approved snapshot not found: {approved_snapshot}"

    out_file = tmp_path / 'generated_vertical_slice_career.json'
    # generate returns the dict as well
    generated = generate(str(input_path), str(out_file))

    # load approved snapshot
    approved = json.loads(approved_snapshot.read_text())

    # Normalize keys ordering and compare
    assert generated == approved
