import json
from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.enrichments import varga


def test_d3_d7_d30_on_golden_chart():
    with open('systems/Parasara/fixtures/golden_chart_01.json', 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    planets = []
    for p in data.get('planets', []):
        pp = PlanetState(name=p['name'], sign=p.get('sign'), degree=p.get('degree'), house=p.get('house'))
        planets.append(pp)
    astro = AstroState(metadata={}, location=None, lagna_sign=data.get('lagna_sign', 'Aries'), lagna_degree=data.get('lagna_degree'), planets=planets)

    d3 = varga.compute_d3(astro)
    d7 = varga.compute_d7(astro)
    d30 = varga.compute_d30(astro)

    # basic structural assertions
    for out in (d3, d7, d30):
        assert isinstance(out, dict)
        for pname, pobj in out.items():
            # ensure target sign present
            k = list(pobj.keys())[0]
            comp = pobj.get(k)
            assert 'target_sign' in comp or 'nav_sign' in comp
