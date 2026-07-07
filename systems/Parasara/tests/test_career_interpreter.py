from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.interpreters.career import interpret_career


def test_career_interpreter_outputs_structure():
    chart = SuryaAdapter.load('systems/Parasara/fixtures/golden_chart_01.json')
    astro = chart_to_astrostate(chart)
    res = interpret_career(astro)
    assert 'score' in res and 0.0 <= res['score'] <= 1.0
    assert 'confidence' in res and 0.0 <= res['confidence'] <= 1.0
    assert 'components' in res and isinstance(res['components'], list)
    assert 'indicators' in res and isinstance(res['indicators'], list)
    assert 'evidence' in res and isinstance(res['evidence'], list)
    # evidence entries should have rule_id and contribution
    for e in res['evidence']:
        assert 'rule_id' in e and 'contribution' in e
