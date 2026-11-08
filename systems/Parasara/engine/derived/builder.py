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


def build_derived_state_strict(astro, *, resolved_versions=None):
    """Compose strict producers without mutating or freezing construction input."""
    from systems.Parasara.engine.enrichments.aspects import (
        compute_aspect_graph_strict, compute_same_sign_conjunctions_strict,
    )
    from systems.Parasara.engine.enrichments.functional_roles import compute_functional_roles_strict
    from systems.Parasara.engine.enrichments.house_conditions import compute_house_conditions
    from systems.Parasara.engine.enrichments.planet_strengths import strict_strength_and_conditions
    from systems.Parasara.engine.enrichments.varga import strict_varga_availability
    graph = compute_aspect_graph_strict(astro, resolved_versions=resolved_versions)
    roles = compute_functional_roles_strict(astro, resolved_versions=resolved_versions)
    unavailable = {
        name: {"readiness": "unsupported", "issues": ["astrology_sme_approval_required"]}
        for name in ("vargas.positions", "strengths.planet", "strengths.shadbala", "dignity.planet")
    }
    unavailable["roles.functional"] = {
        "readiness": roles["readiness"], "issues": roles["issues"],
        "source_kind": "strict_pinned_roles",
    }
    return dict(aspects=graph, houses=compute_house_conditions(astro, graph),
        relationships={"aspects": compute_same_sign_conjunctions_strict(astro)},
        conditions=strict_strength_and_conditions(astro),
        varga_availability=strict_varga_availability(), role_audit=roles,
        unavailable_capabilities=unavailable,
        unsupported_relations={name: dict(readiness="unsupported", issues=["astrology_sme_approval_required"])
                               for name in ("node_aspects", "degree_orb_conjunction")})
