from __future__ import annotations

from pathlib import Path

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.interpreters.career import (
    interpret_career_domain,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "systems" / "Parasara" / "fixtures"


@pytest.fixture
def career_source():
    astro = chart_to_astrostate(SuryaAdapter.load(FIXTURES / "golden_chart_01.json"))
    outcome = interpret_career_domain(astro)
    prediction = outcome.prediction
    batch = prediction.source_evaluation_batch
    inference = prediction.source_inference_result
    return astro, batch, inference, outcome
