from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.enrichments import shadbala


def make_planet(name, sign=None, degree=None, house=None, motion=None, flags=None):
    return PlanetState(name=name, sign=sign, degree=degree, house=house, canonical_id=None, degree_norm=None, vargas=None)


def test_component_structures():
    astro = AstroState(metadata={'is_day': True, 'max_speed': {}}, location=None, lagna_sign='Aries')
    p = PlanetState(name='Sun', sign='Sagittarius', degree=10.5, house=9)
    astro.planets = [p]

    sth = shadbala.compute_sthana_bala(p, astro)
    assert isinstance(sth, dict) and 'value' in sth and 'evidence' in sth

    dig = shadbala.compute_dig_bala(p, astro)
    assert isinstance(dig, dict) and 'value' in dig

    nais = shadbala.compute_naisargika_bala(p, astro)
    assert isinstance(nais, dict) and 'value' in nais

    dr = shadbala.compute_drik_bala(p, astro)
    assert isinstance(dr, dict) and 'value' in dr

    ka = shadbala.compute_kala_bala(p, astro)
    assert isinstance(ka, dict) and 'value' in ka

    ch = shadbala.compute_cheshta_bala(p, astro)
    assert isinstance(ch, dict) and 'value' in ch
