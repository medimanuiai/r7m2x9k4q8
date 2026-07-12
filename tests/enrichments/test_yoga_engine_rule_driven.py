import json
from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.rules.yoga_loader import load_yoga_rules
from systems.Parasara.engine.enrichments import aspects, varga, yoga


def load_golden():
    with open('systems/Parasara/fixtures/golden_chart_01.json', 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    planets = []
    for p in data.get('planets', []):
        planets.append(PlanetState(name=p['name'], sign=p.get('sign'), degree=p.get('degree'), house=p.get('house')))
    astro = AstroState(metadata=data.get('metadata', {}), location=None, lagna_sign=data.get('lagna', {}).get('sign'), lagna_degree=data.get('lagna', {}).get('degree'), planets=planets, houses=data.get('houses', []))
    return astro


def test_rule_driven_yoga_engine_matches_yaml_rules():
    astro = load_golden()
    # ensure rules loaded into registry
    loaded = load_yoga_rules()
    assert any(r.get('id') == 'rajayoga_naive' for r in loaded)

    # compute vargas and aspects
    varga.integrate_vargas_into_astro(astro)
    aspects.compute_aspect_graph(astro)

    matches = yoga.evaluate_yoga_rules(astro)
    # expect matches list with entries for our three rules
    ids = {m['yoga_id'] for m in matches}
    assert 'rajayoga_naive' in ids
    assert 'dhana_naive' in ids
    assert 'arishta_naive' in ids

    # confirm that each match has explainability trace and trace_id
    for m in matches:
        assert 'evidence' in m and isinstance(m['evidence'], dict)
        assert 'trace_id' in m and m['trace_id']
