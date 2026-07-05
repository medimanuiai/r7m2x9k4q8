"""Simple anonymizer for pilot historical candidates.

Transforms personally identifying fields into coarse placeholders while
keeping the file valid against `historical_dataset.schema.json`.
"""
import json
from pathlib import Path
from typing import Any, Dict


def anonymize_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(rec)
    rec_id = out.get('id', 'unknown')
    # Replace name with redacted placeholder but keep a string for schema
    out['name'] = f'REDACTED-{rec_id}'

    md = out.get('metadata', {})
    bl = md.get('birth_location', {})
    lat = bl.get('latitude')
    lon = bl.get('longitude')
    if isinstance(lat, (int, float)):
        bl['latitude'] = round(float(lat), 1)
    if isinstance(lon, (int, float)):
        bl['longitude'] = round(float(lon), 1)

    # If time is unconfirmed, drop precise UTC time
    if md.get('time_confidence') == 'unconfirmed':
        md['birth_datetime_utc'] = None

    md['anonymized'] = True
    out['metadata'] = md

    prov = out.get('provenance', {})
    notes = prov.get('curation_notes', '')
    notes = (notes + ' ' if notes else '') + 'Anonymized: name redacted; coords rounded to 0.1°.'
    prov['curation_notes'] = notes
    out['provenance'] = prov

    return out


def anonymize_file(path_in: str, path_out: str) -> None:
    p_in = Path(path_in)
    p_out = Path(path_out)
    data = json.load(p_in.open())
    out = [anonymize_record(r) for r in data]
    json.dump(out, p_out.open('w', encoding='utf-8'), indent=2, ensure_ascii=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Anonymize pilot candidate JSON')
    parser.add_argument('--in', dest='path_in', default='systems/Parasara/fixtures/historical_pilot_candidates.json')
    parser.add_argument('--out', dest='path_out', default='systems/Parasara/fixtures/historical_pilot_candidates_anonymized.json')
    args = parser.parse_args()
    anonymize_file(args.path_in, args.path_out)
