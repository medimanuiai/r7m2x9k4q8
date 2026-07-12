import json
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from tests.testing_framework.rule_coverage import run_rule_coverage_scan


def test_rule_coverage_runs():
    inp = 'systems/Parasara/fixtures/golden_chart_01.json'
    chart = SuryaAdapter.load(inp)
    astro = chart_to_astrostate(chart)
    rep = run_rule_coverage_scan(astro)
    # ensure coverage recorded structure
    assert 'rules' in rep and 'predicates' in rep
    assert rep['rules']['total_executed'] >= 0
