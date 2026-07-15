import json
from systems.Parasara.engine.astrostate import AstroState, PlanetState
from systems.Parasara.engine.enrichments import varga, aspects, shadbala, yoga


def load_golden():
    with open('systems/Parasara/fixtures/golden_chart_01.json', 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    planets = []
    for p in data.get('planets', []):
        planets.append(PlanetState(name=p['name'], sign=p.get('sign'), degree=p.get('degree'), house=p.get('house')))
    astro = AstroState(metadata=data.get('metadata', {}), location=None, lagna_sign=data.get('lagna', {}).get('sign'), lagna_degree=data.get('lagna', {}).get('degree'), planets=planets)
    return astro


def test_aspectgraph_identity_and_consumers():
    astro = load_golden()
    # compute vargas and aspects
    varga.integrate_vargas_into_astro(astro)
    g1 = aspects.compute_aspect_graph(astro)

    # consumers must read from astro.enrichments only
    # run yoga detector
    yogas = yoga.evaluate_yoga_rules(astro)
    # run shadbala drik for Mars
    sa = shadbala.compute_shadbala_for_planet(next(p for p in astro.planets if p.name == 'Mars'), astro)

    # AspectGraph should be attached in astro.enrichments and identical
    g2 = astro.enrichments.get('aspects')
    assert g1 == g2

    # Yoga detection should reference aspects used and include trace ids
    assert isinstance(yogas, list)
    if yogas:
        y = yogas[0]
        assert 'trace_id' in y and y['trace_id']
        assert 'aspects_used' in y and isinstance(y['aspects_used'], list)

    # Shadbala drik evidence should include aspect_edge entries from the AspectGraph
    drik = sa.get('drik_bala')
    assert drik and 'evidence' in drik
    evid = drik['evidence']
    # evidence is a list of component traces; drill into nested evidence lists
    found = False
    for comp in evid:
        inner = comp.get('evidence') if isinstance(comp, dict) else None
        if isinstance(inner, list):
            for it in inner:
                if isinstance(it, dict) and ('edge_trace' in it or 'aspect_edge' in it):
                    found = True
                    break
        if found:
            break
    assert found
