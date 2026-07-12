from systems.Parasara.engine.rules.yoga_loader import load_yoga_rules, validate_yoga_rule
from systems.Parasara.engine.rules.loader import get_rule


def test_load_yoga_rules():
    loaded = load_yoga_rules()
    # Expect at least the three sample rules
    ids = {r.get('id') for r in loaded}
    assert 'rajayoga_naive' in ids
    assert 'dhana_naive' in ids
    assert 'arishta_naive' in ids


def test_rule_registered():
    r = get_rule('rajayoga_naive')
    assert isinstance(r, dict)
    assert r.get('name') == 'Naive Raja Yoga'


def test_validator_detects_missing_fields():
    bad = {'id': 'bad_rule', 'name': 'Bad'}
    try:
        validate_yoga_rule(bad)
        assert False, 'Expected ValueError for missing fields'
    except ValueError:
        assert True
