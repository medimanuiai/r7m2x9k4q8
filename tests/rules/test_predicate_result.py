import json
from dataclasses import asdict

from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.rules.engine import evaluate_predicate, evaluate_condition, register_predicate, clear_cache, PredicateResult
import systems.Parasara.engine.rules.predicates as _preds  # ensure predicates are registered


def make_astro_with_mars():
    astro = AstroState(metadata={}, location=None, lagna_sign=None, planets=[PlanetState(name='Mars', sign='Aries', degree=0.0, house=7)], houses=[])
    return astro


def test_planet_in_house_true_and_cache():
    astro = make_astro_with_mars()
    clear_cache()
    res = evaluate_predicate('PLANET_IN_HOUSE', {'planet': 'Mars', 'house': 7}, astro, {})
    assert isinstance(res, PredicateResult)
    assert res.matched is True
    assert res.predicate_id == 'PLANET_IN_HOUSE'
    assert res.cache_hit is False
    assert res.evaluation_time_ms is not None

    # second call should be cached
    res2 = evaluate_predicate('PLANET_IN_HOUSE', {'planet': 'Mars', 'house': 7}, astro, {})
    assert isinstance(res2, PredicateResult)
    assert res2.cache_hit is True


def test_planet_exalted_false():
    astro = make_astro_with_mars()
    clear_cache()
    res = evaluate_predicate('PLANET_EXALTED', {'planet': 'Mars'}, astro, {})
    assert isinstance(res, PredicateResult)
    assert res.matched is False
    assert res.errors == []


def test_predicate_exception_becomes_structured_failure():
    astro = make_astro_with_mars()
    clear_cache()

    @register_predicate('RAISE_TEST')
    def _raise(params, astro, context):
        raise RuntimeError('boom')

    res = evaluate_predicate('RAISE_TEST', {}, astro, {})
    # structured failure
    assert isinstance(res, PredicateResult)
    assert res.matched is False
    assert len(res.errors) >= 1

    # cleanup
    from systems.Parasara.engine.rules.engine import PREDICATE_REGISTRY
    PREDICATE_REGISTRY.pop('RAISE_TEST', None)


def test_evaluate_condition_returns_predicate_result():
    astro = make_astro_with_mars()
    clear_cache()
    node = {'type': 'PLANET_IN_HOUSE', 'params': {'planet': 'Mars', 'house': 7}}
    pr = evaluate_condition(node, astro, {})
    assert isinstance(pr, PredicateResult)
    assert pr.matched is True


def test_predicateresult_serialization():
    astro = make_astro_with_mars()
    clear_cache()
    res = evaluate_predicate('PLANET_IN_HOUSE', {'planet': 'Mars', 'house': 7}, astro, {})
    # dataclass as dict is JSON serializable with default=str
    d = asdict(res)
    s = json.dumps(d, default=str)
    assert 'predicate_id' in d
    assert isinstance(s, str)
