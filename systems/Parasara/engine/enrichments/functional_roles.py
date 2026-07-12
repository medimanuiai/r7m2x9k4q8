from typing import Dict, Any, List
import os
import yaml

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

# Default heuristic weights (tunable / M1)
HOUSE_BENEFIT = {1: 0.18, 5: 0.18, 9: 0.18, 4: 0.06, 10: 0.06, 2: 0.03, 11: 0.03}
HOUSE_PENALTY = {6: -0.12, 8: -0.12, 12: -0.12}

# kendra and trikona sets
KENDRAS = {1,4,7,10}
TRIKONAS = {1,5,9}


def _load_table_for_lagna(lagna: str) -> Dict[str, Dict[str, Any]]:
    """Load a YAML table override for a given lagna if present.

    Lookup order:
    1. `rules/parashara/functional_roles/<lagna>.yaml` (preferred)
    2. `systems/Parasara/enrichment_tables/functional_roles/<lagna>.yaml` (legacy)
    File maps planet name -> { functional_role:, functional_score:, yoga_role:, owns_houses: [] }
    """
    # primary location (data-driven tables under rules/)
    base1 = os.path.join(os.getcwd(), 'rules', 'parashara', 'functional_roles')
    fname1 = os.path.join(base1, f"{lagna}.yaml")
    if os.path.exists(fname1):
        try:
            with open(fname1, 'r', encoding='utf-8') as fh:
                docs = yaml.safe_load(fh)
                if isinstance(docs, dict):
                    return docs.get('functional_roles', docs)
        except Exception:
            pass

    # fallback legacy location
    base2 = os.path.join(os.getcwd(), 'systems', 'Parasara', 'enrichment_tables', 'functional_roles')
    fname2 = os.path.join(base2, f"{lagna}.yaml")
    if os.path.exists(fname2):
        try:
            with open(fname2, 'r', encoding='utf-8') as fh:
                docs = yaml.safe_load(fh)
                if isinstance(docs, dict):
                    return docs
        except Exception:
            pass
    return {}


def compute_functional_roles(astro) -> Dict[str, Dict[str, Any]]:
    """Compute a table-driven or heuristic functional role mapping for planets.

    Returns mapping planet_name -> {
      natural_role: 'natural_benefic'|'natural_malefic'|'neutral',
      owns_houses: [int],
      functional_score: float 0..1,
      functional_role: 'functional_benefic'|'functional_malefic'|'neutral'|'yogakaraka',
      yoga_role: optional string
    }
    """
    lagna = getattr(astro, 'lagna_sign', None) or ''
    table = _load_table_for_lagna(lagna)
    # build reverse sign->lord map comes from caller usually; fallback basic map
    SIGN_LORD = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
        'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
        'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter',
    }
    # build LORD_SIGNS: planet -> signs
    LORD_SIGNS: Dict[str, List[str]] = {}
    for s, lord in SIGN_LORD.items():
        if lord:
            LORD_SIGNS.setdefault(lord, []).append(s)

    results: Dict[str, Dict[str, Any]] = {}
    for p in astro.planets:
        name = p.name
        # natural role (simple)
        NAT_BEN = {'Jupiter', 'Venus', 'Mercury', 'Moon'}
        NAT_MAL = {'Saturn', 'Mars', 'Rahu', 'Ketu', 'Sun'}
        natural = 'neutral'
        if name in NAT_BEN:
            natural = 'natural_benefic'
        elif name in NAT_MAL:
            natural = 'natural_malefic'

        # owned signs and convert to houses relative to lagna
        owned_signs = LORD_SIGNS.get(name, [])
        owns_houses: List[int] = []
        try:
            lagna_idx = SIGNS.index(lagna) if lagna in SIGNS else None
        except Exception:
            lagna_idx = None
        for osign in owned_signs:
            try:
                si = SIGNS.index(osign)
                if lagna_idx is not None:
                    house_num = ((si - lagna_idx) % 12) + 1
                    owns_houses.append(house_num)
            except ValueError:
                continue
        owns_houses = sorted(list(set(owns_houses)))

        reasons: List[str] = []
        # check for table override
        if table and name in table:
            entry = table.get(name) or {}
            func_role = entry.get('functional_role')
            func_score = float(entry.get('functional_score') or 0.5)
            yoga_role = entry.get('yoga_role')
            if entry.get('owns_houses'):
                reasons.append(f"owns_houses={entry.get('owns_houses')}")
            if yoga_role:
                reasons.append(f"yoga_role={yoga_role}")
            results[name] = {
                'planet': name,
                'natural_role': natural,
                'owns_houses': owns_houses,
                'functional_role': func_role,
                'functional_score': round(func_score, 3),
                'yoga_role': yoga_role,
                'reason': reasons,
            }
            continue

        # heuristic scoring
        score = 0.5
        for h in owns_houses:
            score += HOUSE_BENEFIT.get(h, 0.0)
            score += HOUSE_PENALTY.get(h, 0.0)
        # yogakaraka detection: owns any kendra and any trikona
        yoga_role = None
        if any((h in KENDRAS) for h in owns_houses) and any((h in TRIKONAS) for h in owns_houses):
            yoga_role = 'yogakaraka'
            score += 0.25

        # normalize to 0..1
        score = max(0.0, min(1.0, score))
        if yoga_role:
            func_label = 'yogakaraka'
            reasons.append('owns kendra and trikona -> yogakaraka')
        elif score >= 0.6:
            func_label = 'functional_benefic'
            reasons.append(f'score={round(score,3)} -> benefic')
        elif score <= 0.4:
            func_label = 'functional_malefic'
            reasons.append(f'score={round(score,3)} -> malefic')
        else:
            func_label = 'functional_neutral'
            reasons.append(f'score={round(score,3)} -> neutral')

        results[name] = {
            'planet': name,
            'natural_role': natural,
            'owns_houses': owns_houses,
            'functional_role': func_label,
            'functional_score': round(score, 3),
            'yoga_role': yoga_role,
            'reason': reasons,
        }

    return results
