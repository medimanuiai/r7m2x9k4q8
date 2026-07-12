#!/usr/bin/env bash
set -euo pipefail
PYTHON=${PYTHON:-python}
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
"$PYTHON" external_refs/Simulation/SuryaSiddhanta/scripts/compare_engines.py
