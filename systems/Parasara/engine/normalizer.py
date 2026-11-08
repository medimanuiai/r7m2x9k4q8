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


def chart_to_astrostate_strict(chart, *, resolved_versions=None) -> AstroState:
    """Construct facts only through the explicit FWP01 strict boundary."""
    from copy import deepcopy
    from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter, StrictInputError
    from systems.Parasara.engine.models import StrictChart, StrictInputIssue
    from systems.Parasara.engine.identities import CANONICAL_PLANETS, SIGNS, SIGN_LORD

    if not isinstance(chart, StrictChart):
        raise StrictInputError((StrictInputIssue("$", "strict_chart_required"),))
    # Revalidate model instances too: model_construct/mutable nested values cannot
    # turn unvalidated or subsequently corrupted data into a published fact.
    validated = SuryaAdapter.from_mapping_strict(chart.model_dump(mode="python"))
    if resolved_versions is not None:
        from systems.Parasara.engine.versioning import ResolvedEvaluationVersions
        if not isinstance(resolved_versions, ResolvedEvaluationVersions):
            raise StrictInputError((StrictInputIssue("$", "resolved_authority_required"),))
    md = deepcopy(validated.metadata)
    location = md["birth_location"]
    lagna = validated.lagna
    planets = [PlanetState(
        name=row["name"], sign=row["sign"], degree=row["degree"],
        house=row["house"], canonical_id=row["name"].lower(),
        degree_norm=row["sidereal_longitude"],
    ) for row in validated.planets]
    start = SIGNS.index(lagna["sign"])
    houses = []
    for number in range(1, 13):
        sign = SIGNS[(start + number - 1) % 12]
        houses.append(dict(number=number, sign=sign, lord=SIGN_LORD[sign],
            occupants=[name for name in CANONICAL_PLANETS
                       if any(p.name == name and p.house == number for p in planets)]))
    # Existing chart.metadata is the bounded field-level evidence surface; no
    # snapshot type, query, capability ID or legacy model contract is expanded.
    md["factual_sources"] = {
        "producer": "fwp01.strict", "version": "1.0.0",
        "lagna": deepcopy(lagna),
        "planets": {row["name"]: {
            "sidereal_longitude": row["sidereal_longitude"],
            "nakshatra": deepcopy(row["nakshatra"]),
            "motion": (
                {"readiness": "unsupported", "issues": ["node_motion_unavailable"]}
                if row["name"] in ("Rahu", "Ketu") else
                {"readiness": "ready", "value": deepcopy(row["motion"]),
                 "source": "validated_surya_input"}
            ),
            "input_flags": deepcopy(row.get("flags", {})),
            "normalization": {
                "producer": "fwp01.strict", "version": "1.0.0",
                "formula": "whole_sign_from_original_sidereal_longitude",
                "input": row["sidereal_longitude"],
                "output": {key: row[key] for key in ("name", "sign", "degree", "house")},
            },
        } for row in validated.planets},
    }
    astro = AstroState(
        metadata=md,
        location=Location(place=location.get("place", location.get("place_label")),
            latitude=location["latitude"], longitude=location["longitude"],
            timezone_offset_minutes=location["timezone_offset_minutes"]),
        lagna_sign=lagna["sign"], lagna_degree=lagna["degree"],
        planets=planets, houses=houses,
        diagnostics={"planet_count": 9},
        enrichments={"normalized_degrees": {p.name: p.degree_norm for p in planets}},
        derived=None,
    )
    from systems.Parasara.engine.derived.builder import build_derived_state_strict
    derived = build_derived_state_strict(astro, resolved_versions=resolved_versions)
    astro.derived = derived
    astro.enrichments.update(
        aspects=derived["aspects"], house_summaries=derived["houses"],
        unavailable_capabilities=derived["unavailable_capabilities"],
    )
    astro.metadata["factual_sources"]["enrichments"] = {
        key: derived[key] for key in ("conditions", "varga_availability", "role_audit", "unsupported_relations")
    }
    exaltations = {
        name: row["conditions"]["exalted"]["value"]
        for name, row in derived["conditions"].items()
        if row["conditions"]["exalted"]["readiness"] == "ready"
    }
    if exaltations:
        astro.metadata["exaltations"] = exaltations
    return astro


def build_strict_snapshot(chart, *, resolved_versions=None):
    """Publish once; a strict construction failure never retries compatibility."""
    from systems.Parasara.engine.adapter.surya_adapter import StrictInputError
    from systems.Parasara.engine.astrostate_api import (
        AstroStateBuildFailure, AstroStateBuildSuccess, AstroCapabilitySupply,
        ConstructionIssue, freeze_astrostate, snapshot_logical_bytes,
    )
    try:
        astro = chart_to_astrostate_strict(chart, resolved_versions=resolved_versions)
    except StrictInputError as exc:
        issues = tuple(sorted((ConstructionIssue(
            code=item.code, path=item.path, recoverable=False, fatal=True,
        ) for item in exc.issues), key=lambda item: (item.path, item.code)))
        return AstroStateBuildFailure(issues=issues)
    context = {} if resolved_versions is None else {"instant": resolved_versions.config.evaluation_instant}
    supplies = tuple(AstroCapabilitySupply(
        capability_id=capability_id, capability_version="1.0.0",
        source_kind=source_kind, content=content, factual_scope=scope,
    ) for capability_id, source_kind, scope, content in (
        ("aspects.whole_sign_graph", "strict_classical_whole_sign_graph", "seven_classical_planets", astro.enrichments["aspects"]),
        ("aspects.basic_conjunction_list", "strict_same_sign_conjunction", "factual", astro.derived["relationships"]["aspects"]),
        ("houses.summaries", "strict_house_conditions", "factual", {str(row["number"]): row for row in astro.derived["houses"]}),
    ))
    outcome = freeze_astrostate(astro, capability_supplies=supplies, evaluation_context=context)
    if isinstance(outcome, AstroStateBuildSuccess):
        try:
            snapshot_logical_bytes(outcome.snapshot)
        except (UnicodeError, ValueError, OverflowError):
            return AstroStateBuildFailure(issues=(ConstructionIssue(
                code="unsafe_canonical_content", path="$", recoverable=False, fatal=True,
            ),))
        if resolved_versions is not None:
            resolved_versions.authorize_snapshot(outcome.snapshot)
    return outcome
