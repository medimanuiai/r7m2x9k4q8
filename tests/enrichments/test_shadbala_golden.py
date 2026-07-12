import json
from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.enrichments import shadbala


def test_shadbala_golden_chart_01():
    with open('tests/enrichments/golden_shadbala_chart_01.json', 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    planets = []
    for p in data.get('planets', []):
        pp = PlanetState(name=p['name'], sign=p.get('sign'), degree=p.get('degree'), house=p.get('house'))
        planets.append(pp)
    astro = AstroState(metadata={'is_day': True, 'exaltations': shadbala._EXALT}, location=None, lagna_sign='Aries', planets=planets)

    out = shadbala.compute_shadbala(astro)
    # basic assertions about structure and traces
    assert 'Sun' in out and 'total_rupas' in out['Sun']
    assert isinstance(out['Sun']['calculation_trace'], list)
    assert out['Sun']['confidence'] >= 0.0
