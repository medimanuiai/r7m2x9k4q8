import json
import sys
import os
from pathlib import Path

# Ensure project root is on sys.path for imports during pytest
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.tools import validate_historical
from systems.Parasara.tools.anonymize_pilot import anonymize_file
from jsonschema import Draft7Validator


def test_validate_historical_outputs_ok(capsys):
    # Should print VALIDATION_OK and not raise
    validate_historical.main()
    captured = capsys.readouterr()
    assert 'VALIDATION_OK' in captured.out


def test_surya_adapter_load_and_load_many():
    p_golden = Path('systems/Parasara/fixtures/golden_chart_01.json')
    chart = SuryaAdapter.load(str(p_golden))
    assert chart is not None
    assert chart.metadata is not None

    p_pilot = Path('systems/Parasara/fixtures/historical_pilot_candidates.json')
    charts = SuryaAdapter.load_many(str(p_pilot))
    assert isinstance(charts, list)
    # Expect at least one record in the curated pilot
    assert len(charts) >= 1
    # Basic sanity: first chart has metadata with birth_location
    first = charts[0]
    assert hasattr(first, 'metadata')
    assert isinstance(first.metadata.birth_location, dict)


def test_anonymizer_outputs_valid_schema(tmp_path):
    p_in = Path('systems/Parasara/fixtures/historical_pilot_candidates.json')
    p_out = tmp_path / 'anonymized.json'
    anonymize_file(str(p_in), str(p_out))

    # Validate anonymized file against the historical dataset schema
    schema = json.load(Path('systems/Parasara/schemas/historical_dataset.schema.json').open())
    data = json.load(p_out.open())
    errors = list(Draft7Validator(schema).iter_errors(data))
    assert not errors, f'Anonymized output failed schema validation: {errors}'
