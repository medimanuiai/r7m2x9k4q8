"""SuryaAdapter: validate and load Surya Siddhanta JSON into Pydantic models."""
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

from systems.Parasara.engine.models import Chart


class SuryaAdapter:
    # Resolve schema path relative to this source file so it works regardless of CWD
    try:
        # file: systems/Parasara/engine/adapter/surya_adapter.py -> parents[2] == systems/Parasara
        SCHEMA_PATH = Path(__file__).resolve().parents[2] / 'schemas' / 'surya_input.schema.json'
    except Exception:
        SCHEMA_PATH = Path('systems/Parasara/schemas/surya_input.schema.json')

    @classmethod
    def validate(cls, data: Any) -> None:
        s = json.load(cls.SCHEMA_PATH.open())
        errors = list(Draft7Validator(s).iter_errors(data))
        if errors:
            msgs = '\n'.join([f"{e.message} at {list(e.path)}" for e in errors])
            raise ValueError(f"Schema validation failed:\n{msgs}")

    @classmethod
    def load(cls, path: str) -> Chart:
        p = Path(path)
        data = json.load(p.open())
        cls.validate(data)
        # Pydantic V2: use model_validate
        chart = Chart.model_validate(data)
        return chart

    @classmethod
    def load_many(cls, path: str):
        p = Path(path)
        data = json.load(p.open())
        if isinstance(data, list):
            charts = []
            for item in data:
                if 'input' in item:
                    charts.append(Chart.model_validate(item['input']))
                elif 'metadata' in item:
                    obj = {
                        'metadata': item.get('metadata'),
                        'lagna': item.get('lagna'),
                        'planets': item.get('planets', []),
                        'houses': item.get('houses', [])
                    }
                    charts.append(Chart.model_validate(obj))
                else:
                    raise ValueError('Unexpected item format in load_many')
            return charts
        raise ValueError('Expected list of records for load_many')
