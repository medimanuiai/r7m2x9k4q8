"""Validate historical pilot candidate file against schema."""
import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator


def main():
    p_schema = Path('systems/Parasara/schemas/historical_dataset.schema.json')
    p_data = Path('systems/Parasara/fixtures/historical_pilot_candidates.json')
    s = json.load(p_schema.open())
    d = json.load(p_data.open())
    errors = list(Draft7Validator(s).iter_errors(d))
    if errors:
        print('VALIDATION_ERRORS')
        for e in errors:
            print(f'- {e.message} (at {list(e.path)})')
        sys.exit(1)
    print('VALIDATION_OK')


if __name__ == '__main__':
    main()
