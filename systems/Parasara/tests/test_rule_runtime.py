from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules import runtime


def load_astro_from_fixture(path: str):
    adapter = SuryaAdapter()
    chart = adapter.load(path)
    return chart_to_astrostate(chart)


def test_in_sign_and_in_house_and_lord_of_house():
    astro = load_astro_from_fixture('systems/Parasara/fixtures/golden_chart_01.json')

    # Mars is in Aries and house 1 per fixture
    mars = next(p for p in astro.planets if p.name == 'Mars')
    assert runtime.in_sign(mars, 'Aries')
    assert runtime.in_house(mars, 1)

    # Mars should be recorded as lord of house 1 according to houses in fixture
    assert runtime.lord_of_house(astro, 'Mars', 1)


def test_evaluate_rule_matches_and_mismatch():
    astro = load_astro_from_fixture('systems/Parasara/fixtures/golden_chart_01.json')

    r1 = {'type': 'in_sign', 'planet': 'Sun', 'sign': 'Sagittarius'}
    res1 = runtime.evaluate_rule(astro, r1)
    assert res1['match'] is True

    r2 = {'type': 'in_house', 'planet': 'Moon', 'house': 3}
    res2 = runtime.evaluate_rule(astro, r2)
    assert res2['match'] is False
