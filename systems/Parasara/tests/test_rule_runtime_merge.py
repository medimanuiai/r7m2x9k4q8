import sys
sys.path.insert(0, '.')
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules import runtime
from systems.Parasara.engine.rules import loader


def test_evaluate_rule_merges_registered_by_type():
    # ensure registry loaded
    rules_path = 'systems/Parasara/rules/parashara/v1'
    loader.load_rules_from_dir(rules_path)
    chart = SuryaAdapter.load('systems/Parasara/fixtures/surya_test_chart.json')
    astro = chart_to_astrostate(chart)
    # call evaluate with only type (no id)
    rm = runtime.evaluate_rule_with_score(astro, {'type': 'rajayoga_naive'})
    assert isinstance(rm, dict)
    # registered rule id should be present
    assert rm.get('context', {}).get('id') == 'rajayoga_naive'
    # provenance should include source file
    prov = rm.get('provenance') or {}
    assert prov.get('source'), 'Expected _source_file provenance in merged context'
