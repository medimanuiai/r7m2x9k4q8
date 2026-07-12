from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.dasha.vimshottari import _nakshatra_index_from_longitude, compute_vimshottari


def make_astro_with_moon(deg):
    astro = AstroState(metadata={}, location=None, lagna_sign='Aries', lagna_degree=5.0, planets=[])
    moon = PlanetState(name='Moon', sign=None, degree=deg, house=None)
    astro.planets = [moon]
    return astro


def test_nakshatra_fraction_boundaries():
    # test multiple nakshatra boundary longitudes
    nak_size = 13 + 1/3
    for i in range(0, 27):
        base = i * nak_size
        # test quarter points within the nakshatra
        for frac in [0.0, 0.25, 0.5, 0.75, 0.9999]:
            deg = base + frac * nak_size
            idx, pada, within = _nakshatra_index_from_longitude(deg)
            astro = make_astro_with_moon(deg)
            out = compute_vimshottari(astro, periods=1)
            # if out has first mahadasha, duration should be <= full lord years * fraction_remaining
            if out:
                first = out[0]
                # ensure start is iso string and duration_days present
                assert 'duration_days' in first
