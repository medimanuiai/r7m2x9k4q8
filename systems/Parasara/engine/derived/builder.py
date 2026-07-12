from typing import Dict, Any
from systems.Parasara.engine.astrostate import AstroState
from systems.Parasara.engine.enrichments.planet_strengths import compute_planet_strengths, compute_house_summaries
from systems.Parasara.engine.enrichments.functional_roles import compute_functional_roles
from systems.Parasara.engine.enrichments.aspects import compute_basic_aspects
from systems.Parasara.engine.derived.models import DerivedState


def build_derived_state(astro: AstroState) -> Dict[str, Any]:
    """Build a consolidated DerivedState dictionary from existing enrichments.

    This function is intentionally lightweight for M1 and composes outputs from
    existing enrichment engines into a single canonical structure that the rule
    engine and interpreters can consume without recalculating.
    """
    derived: Dict[str, Any] = {}

    # Planet strengths (and writes back to astro.planets inside function)
    try:
        planet_strengths = compute_planet_strengths(astro)
    except Exception:
        planet_strengths = getattr(astro, 'enrichments', {}).get('planet_strengths') or {}

    # house summaries
    try:
        house_summ = compute_house_summaries(astro)
    except Exception:
        house_summ = getattr(astro, 'enrichments', {}).get('house_summaries') or []

    # functional roles
    try:
        func_roles = compute_functional_roles(astro)
    except Exception:
        func_roles = {k: v for k, v in (planet_strengths or {}).items()}

    # aspects / relationships
    try:
        aspects = compute_basic_aspects(astro)
    except Exception:
        aspects = getattr(astro, 'enrichments', {}).get('aspects') or []

    derived['planets'] = planet_strengths
    derived['houses'] = house_summ
    derived['functional_roles'] = func_roles
    derived['relationships'] = {'aspects': aspects}

    # small diagnostics and provenance
    derived['diagnostics'] = {
        'planet_count': len(astro.planets),
        'house_count': len(house_summ),
    }

    # validate against Pydantic model for early detection of schema drift
    try:
        # validate and return a canonical model dump
        ds = DerivedState.model_validate(derived)
        return ds.model_dump()
    except Exception:
        return derived
