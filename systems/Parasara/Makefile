validate-schemas:
	python -m pip install -r requirements.txt
	python - <<'PY'
import json,sys
from pathlib import Path
p_schema=Path('systems/Parasara/schemas/surya_input.schema.json')
p_fixture=Path('systems/Parasara/fixtures/golden_chart_01.json')
from jsonschema import Draft7Validator
s=json.load(p_schema.open())
d=json.load(p_fixture.open())
errors=[e.message for e in Draft7Validator(s).iter_errors(d)]
if errors:
    print('VALIDATION_ERRORS')
    for e in errors:
        print(e)
    sys.exit(1)
print('VALIDATION_OK')
PY

test:
	pytest -q systems/Parasara/tests

snapshot:
	echo "No snapshots implemented yet"
