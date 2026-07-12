from typing import List
from systems.Parasara.engine.models import Chart, Planet, Metadata
from systems.Parasara.engine.astrostate import AstroState, PlanetState, Location
from systems.Parasara.engine.enrichments.canonical_ids import canonical_planet_id, canonical_house_id
from systems.Parasara.engine.enrichments.precision import normalize_longitude, round_degree
from systems.Parasara.engine.enrichments.varga import varga_summary_for_planet
from systems.Parasara.engine.enrichments.planet_strengths import compute_planet_strengths, compute_house_summaries
from systems.Parasara.engine.enrichments.planet_strengths import SIGN_LORD


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
    # prefer Pydantic V2 API when available
    if hasattr(chart.metadata, 'model_dump'):
        md = chart.metadata.model_dump()
    elif hasattr(chart.metadata, 'dict'):
        md = chart.metadata.dict()
    else:
        md = chart.metadata
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
    # capture ascendant info if provided as a planet node in Surya output
    asc_sign = None
    asc_degree = None
    for p in chart.planets:
        name = p.name if hasattr(p, 'name') else p.get('name')
        # filter placeholder names like 'Empty'
        if not name or (isinstance(name, str) and name.lower() == 'empty'):
            continue
        # treat Ascendant/Lagna nodes specially: capture sign/degree, do not add as planet
        if isinstance(name, str) and name.lower() in ('ascendant', 'lagna', 'asc'):
            asc_sign = (getattr(p, 'sign', None) or (p.get('sign') if isinstance(p, dict) else None))
            asc_degree = getattr(p, 'degree', None) or (p.get('degree') if isinstance(p, dict) else None)
            # do not append an Ascendant entry to planets
            continue
        # normalize common spelling differences
        if name == 'Kethu':
            name = 'Ketu'
        deg = getattr(p, 'degree', None) or (p.get('degree') if isinstance(p, dict) else None)
        house_no = getattr(p, 'house', None) or (p.get('house') if isinstance(p, dict) else None)
        planet_sign = (getattr(p, 'sign', None) or (p.get('sign') if isinstance(p, dict) else None))
        planet = PlanetState(
            name=name,
            sign=planet_sign,
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


    # prefer explicit lagna from chart.lagna, fall back to ascendant node if present
    lagna_sign = chart.lagna.sign if chart.lagna else asc_sign
    lagna_degree = chart.lagna.degree if chart.lagna and getattr(chart.lagna, 'degree', None) is not None else asc_degree

    # Build houses if missing (e.g., Surya output may omit houses). For M1 we
    # support whole_sign house system: house 1 = lagna_sign, house 2 = next sign, etc.
    houses = chart.houses or []
    # If houses are not provided by Surya and lagna is present, Surya's planet.house
    # values are Aries-based sign indices (1=Aries..12=Pisces). Convert those to
    # lagna-relative house numbers before building whole-sign houses so that
    # occupants and house numbering are correct (house 1 = lagna).
    if (not houses or len(houses) == 0) and lagna_sign:
        RASI_NAMES = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
        try:
            start = RASI_NAMES.index(lagna_sign)
        except Exception:
            start = 0

        # convert planets' Aries-based house indices to lagna-relative house numbers
        for p in planets:
            try:
                raw_house = int(getattr(p, 'house', None) or 0)
            except Exception:
                raw_house = 0
            if 1 <= raw_house <= 12:
                # raw_house is 1-based Aries index; convert to 0-based for math
                rel = ((raw_house - 1) - start) % 12
                p.house = rel + 1

        houses = []
        for i in range(12):
            idx = (start + i) % 12
            sign = RASI_NAMES[idx]
            number = i + 1
            lord = SIGN_LORD.get(sign)
            occupants = [p.name for p in planets if p.house == number]
            houses.append({'number': number, 'sign': sign, 'lord': lord, 'occupants': occupants})

    astro = AstroState(
        metadata=md,
        location=loc,
        lagna_sign=lagna_sign,
        lagna_degree=lagna_degree if 'lagna_degree' in locals() else None,
        planets=planets,
        houses=houses,
        diagnostics={'planet_count': len(planets)}
    )
    # add simple enrichments at astrostate level
    astro.enrichments = {
        'canonical_planet_ids': {p.name: p.canonical_id for p in planets},
        'normalized_degrees': {p.name: p.degree_norm for p in planets},
    }
    # attach computed planet strengths and house summaries
    try:
        astro.enrichments['planet_strengths'] = compute_planet_strengths(astro)
        astro.enrichments['house_summaries'] = compute_house_summaries(astro)
        # lagna summary for diagnostics
        from systems.Parasara.engine.enrichments.planet_strengths import compute_lagna_summary
        astro.diagnostics['lagna_summary'] = compute_lagna_summary(astro)
        # basic aspects (M1): conjunctions
        from systems.Parasara.engine.enrichments.aspects import compute_basic_aspects
        astro.enrichments['aspects'] = compute_basic_aspects(astro)
        # build consolidated DerivedState and attach
        from systems.Parasara.engine.derived.builder import build_derived_state
        try:
            astro.derived = build_derived_state(astro)
        except Exception:
            astro.derived = None
    except Exception:
        astro.enrichments['planet_strengths'] = {p.name: p.strength for p in planets}
        astro.enrichments['house_summaries'] = chart.houses
        astro.diagnostics['lagna_summary'] = {}
    return astro
