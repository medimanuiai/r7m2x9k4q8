import json
from datetime import datetime
from pathlib import Path


def prepare_snapshot_signoff(golden_path: str, signer: str, note: str = None):
    p = Path(golden_path)
    meta = p.with_suffix('.meta.json')
    record = {
        'signed_by': signer,
        'signed_at': datetime.utcnow().isoformat() + 'Z',
        'note': note,
        'golden': str(p.name)
    }
    with meta.open('w', encoding='utf-8') as fh:
        json.dump(record, fh, indent=2)
    return str(meta)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('Usage: approve_snapshot.py snapshot.json signer_name [note]')
        raise SystemExit(2)
    print(prepare_snapshot_signoff(sys.argv[1], sys.argv[2], ' '.join(sys.argv[3:])))
