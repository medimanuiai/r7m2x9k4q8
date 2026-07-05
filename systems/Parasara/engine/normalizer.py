from typing import List
from systems.Parasara.engine.models import Chart, Planet, Metadata
from systems.Parasara.engine.astrostate import AstroState, PlanetState, Location
from systems.Parasara.engine.enrichments.canonical_ids import canonical_planet_id, canonical_house_id
from systems.Parasara.engine.enrichments.precision import normalize_longitude, round_degree
from systems.Parasara.engine.enrichments.varga import varga_summary_for_planet


def compute_dignity(planet: Planet) -> str:
    # Placeholder: simple mapping by sign for demo
    sign = planet.sign or ''
    if sign in ['Aries', 'Leo', 'Sagittarius']:
        return 'fire'  # placeholder category
    if sign in ['Taurus', 'Virgo', 'Capricorn']:
        return 'earth'
    return 'neutral'


def compute_strength(planet: Planet) -> float:
    # Placeholder: strength derived from motion flag or degree
    if planet.motion and planet.motion.get('speed'):
        return min(1.0, float(planet.motion.get('speed')) / 10.0)
    if planet.degree:
        return 0.5
    return 0.1


def chart_to_astrostate(chart: Chart) -> AstroState:
    md = chart.metadata.dict() if hasattr(chart.metadata, 'dict') else chart.metadata
    loc = None
    bl = md.get('birth_location') if isinstance(md, dict) else None
    if bl:
        loc = Location(
            place=bl.get('place'),
            latitude=bl.get('latitude'),
            longitude=bl.get('longitude'),
            timezone_offset_minutes=bl.get('timezone_offset_minutes')
        )

    planets = []
    for p in chart.planets:
        name = p.name if hasattr(p, 'name') else p.get('name')
        deg = getattr(p, 'degree', None) or (p.get('degree') if isinstance(p, dict) else None)
        house_no = getattr(p, 'house', None) or (p.get('house') if isinstance(p, dict) else None)
        planet = PlanetState(
            name=name,
            sign=getattr(p, 'sign', None) or p.get('sign') if isinstance(p, dict) else None,
            degree=deg,
            house=house_no,
        )
        planet.dignity = compute_dignity(p)
        planet.strength = compute_strength(p)
        # canonical id and normalized degree
        planet.canonical_id = canonical_planet_id(name)
        planet.degree_norm = normalize_longitude(deg) if deg is not None else None
        # attach varga summaries (lightweight)
        if planet.degree_norm is not None:
            planet.vargas = varga_summary_for_planet(planet.degree_norm)
        planets.append(planet)

    lagna_sign = chart.lagna.sign if chart.lagna else None

    astro = AstroState(
        metadata=md,
        location=loc,
        lagna_sign=lagna_sign,
        planets=planets,
        houses=chart.houses,
        diagnostics={'planet_count': len(planets)}
    )
    # add simple enrichments at astrostate level
    astro.enrichments = {
        'canonical_planet_ids': {p.name: p.canonical_id for p in planets},
        'normalized_degrees': {p.name: p.degree_norm for p in planets}
    }
    return astro
