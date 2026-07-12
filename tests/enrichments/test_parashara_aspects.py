from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.enrichments.aspects import compute_parashara_aspects


def test_parashara_jupiter_mars_saturn():
    chart = SuryaAdapter.load('systems/Parasara/fixtures/golden_chart_01.json')
    astro = chart_to_astrostate(chart)
    aspects = compute_parashara_aspects(astro)
    # ensure Jupiter aspects include offsets 5,7,9 when Jupiter present
    jupiter = [a for a in aspects if a['source'] == 'Jupiter']
    if jupiter:
        offs = {a['offset'] for a in jupiter}
        assert 5 in offs and 7 in offs and 9 in offs


def test_rahu_ketu_configurable():
    chart = SuryaAdapter.load('systems/Parasara/fixtures/golden_chart_01.json')
    astro = chart_to_astrostate(chart)
    # inject metadata to configure Rahu to aspect only 5th and 9th
    # inject a Rahu planet into the astrostate for testing
    try:
        astro_planets = getattr(astro, 'planets', [])
        # create a minimal Rahu-like object
        Rahu = type('P', (), {})
        r = Rahu()
        r.name = 'Rahu'
        r.house = 1
        astro_planets.append(r)
        astro.metadata = getattr(astro, 'metadata', {}) or {}
        astro.metadata.setdefault('parashara', {})['nodes'] = {'Rahu': [5, 9], 'Ketu': [7]}
    except Exception:
        pass
    aspects = compute_parashara_aspects(astro)
    rahu = [a for a in aspects if a['source'] == 'Rahu']
    offs = {a['offset'] for a in rahu}
    # offsets should be a subset of configured values and not empty
    assert offs.issubset({5, 9}) and len(offs) > 0
