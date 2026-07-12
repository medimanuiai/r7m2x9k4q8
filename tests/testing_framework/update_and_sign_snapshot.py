#!/usr/bin/env python3
import argparse
from pathlib import Path
from systems.Parasara.tools.generate_snapshot import generate
from tests.testing_framework.approve_snapshot import prepare_snapshot_signoff


def update_and_sign(input_chart: str, snapshot_path: str, signer: str, note: str = None):
    Path(snapshot_path).parent.mkdir(parents=True, exist_ok=True)
    generate(input_chart, snapshot_path)
    meta = prepare_snapshot_signoff(snapshot_path, signer, note)
    return snapshot_path, meta


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('input')
    p.add_argument('snapshot')
    p.add_argument('signer')
    p.add_argument('--note', default='')
    args = p.parse_args()
    out, meta = update_and_sign(args.input, args.snapshot, args.signer, args.note)
    print(out)
    print(meta)
