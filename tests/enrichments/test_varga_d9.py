import json
from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.enrichments import varga


def test_d9_navamsa_basic_on_golden_chart():
    with open('systems/Parasara/fixtures/golden_chart_01.json', 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    planets = []
    for p in data.get('planets', []):
        pp = PlanetState(name=p['name'], sign=p.get('sign'), degree=p.get('degree'), house=p.get('house'))
        planets.append(pp)
    # create astrostate
    astro = AstroState(metadata={}, location=None, lagna_sign=data.get('lagna_sign', 'Aries'), lagna_degree=data.get('lagna_degree'), planets=planets)
    out = varga.compute_d9(astro)
    assert isinstance(out, dict)
    for pname, pobj in out.items():
        nav = pobj.get('navamsa')
        assert isinstance(nav, dict)
        assert nav.get('nav_sign') in varga.SIGNS
        assert 0 <= int(nav.get('nav_in_sign')) <= 8
        assert 0.0 <= float(nav.get('degree_into_navamsa')) < (30.0/9.0)
