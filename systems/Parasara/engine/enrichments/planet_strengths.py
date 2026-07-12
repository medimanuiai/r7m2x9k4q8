from typing import Dict, Any, List
from systems.Parasara.engine.astrostate import AstroState
from systems.Parasara.engine.enrichments.functional_roles import compute_functional_roles


SIGN_ELEMENTS = {
    'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
    'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
    'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
    'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water',
}

# simplified sign lords for lagna summary
SIGN_LORD = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
    'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter',
}


def compute_planet_strengths(astro: AstroState) -> Dict[str, Any]:
    """Return a mapping planet name -> detailed strength object.

    The structure is intentionally simple for M1 and includes:
    - dignity (exalted/debilitated/own/neutral)
    - functional_role (benefic/malefic/neutral)
    - combust, retrograde
    - temporary_friendship (element-based)
    - strength (0..1 numeric)
    """
    out: Dict[str, Any] = {}
    # basic own-sign map (partial, but covers major planets)
    OWN_SIGNS = {
        'Sun': 'Leo', 'Moon': 'Cancer', 'Mars': 'Aries', 'Mercury': 'Gemini',
        'Jupiter': 'Sagittarius', 'Venus': 'Taurus', 'Saturn': 'Capricorn',
        'Rahu': None, 'Ketu': None,
    }

    # fallback natural classification (used if lagna not available)
    NATURAL_BENEFICS = {'Jupiter', 'Venus', 'Mercury', 'Moon'}
    NATURAL_MALEFICS = {'Saturn', 'Mars', 'Rahu', 'Ketu', 'Sun'}

    # house-role weights for a simplified Parashara-inspired functional-role heuristic
    HOUSE_ROLE_WEIGHTS = {
        1: 0.6, 2: 0.8, 3: 0.0, 4: 0.6, 5: 1.0, 6: -1.0,
        7: 0.2, 8: -1.0, 9: 1.0, 10: 0.5, 11: 0.8, 12: -0.9,
    }

    for p in astro.planets:
        name = p.name
        # defensive: skip placeholder names
        if not name or name.lower() == 'empty':
            continue

        flags = getattr(p, 'vargas', None) or {}
        # try reading flags from enrichments if present
        # p may have flags under p.dict() in chart; fall back to basics
        dignity = 'neutral'
        # infer dignity from existing flags if present
        # many charts expose flags under p.__dict__ or in 'flags' key previously
        if hasattr(p, 'degree') and p.degree is not None:
            pass

        # base numeric strength (start neutral)
        strength = 0.4
        # component breakdown for explainability
        components = {
            'dignity_bonus': 0.0,
            'combust_penalty': 0.0,
            'retro_bonus': 0.0,
            'temp_friend_bonus': 0.0,
            'varga_bonus': 0.0,
        }
        # honor explicit properties if present
        # retrograde detection
        retro = False
        try:
            if hasattr(p, 'canonical_id'):
                # use p attributes
                pass
        except Exception:
            pass

        # check if planet has flags/attributes indicating exaltation/debilitation
        raw = getattr(p, '__dict__', {})
        raw_flags = raw.get('flags') if isinstance(raw, dict) else None
        if isinstance(raw_flags, dict):
            if raw_flags.get('exalted'):
                dignity = 'exalted'
                components['dignity_bonus'] += 0.4
                strength = min(1.0, strength + components['dignity_bonus'])
            if raw_flags.get('debilitated'):
                dignity = 'debilitated'
                components['dignity_bonus'] -= 0.35
                strength = max(0.0, strength + components['dignity_bonus'])
            if raw_flags.get('combust'):
                combust = True
                components['combust_penalty'] = -0.2
                strength = max(0.0, strength + components['combust_penalty'])
            else:
                combust = False
        else:
            combust = False

        # own sign / dignity adjustments (prefer explicit flags)
        own_sign = OWN_SIGNS.get(name)
        if own_sign and getattr(p, 'sign', None) == own_sign:
            dignity = 'own_sign'
        if dignity == 'exalted':
            components['dignity_bonus'] += 0.35
            strength = min(1.0, strength + components['dignity_bonus'])
        elif dignity == 'own_sign':
            components['dignity_bonus'] += 0.25
            strength = min(1.0, strength + components['dignity_bonus'])
        elif dignity == 'debilitated':
            components['dignity_bonus'] -= 0.45
            strength = max(0.0, strength + components['dignity_bonus'])

        # retrograde slightly increases influence for our naive metric
        if hasattr(p, 'degree'):
            raw_motion = raw.get('motion') if isinstance(raw, dict) else None
            if isinstance(raw_motion, dict) and raw_motion.get('retrograde'):
                retro = True
                components['retro_bonus'] = 0.05
                strength = min(1.0, strength + components['retro_bonus'])

        # functional role: determine relative to lagna if available
        func = 'neutral'
        lagna = getattr(astro, 'lagna_sign', None)
        if lagna:
            # build reverse map: planet -> list of signs it rules (use SIGN_LORD)
            LORD_SIGNS: Dict[str, List[str]] = {}
            for s, lord in SIGN_LORD.items():
                if lord:
                    LORD_SIGNS.setdefault(lord, []).append(s)

            signs = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
            try:
                lagna_idx = signs.index(lagna)
            except ValueError:
                lagna_idx = None

            weight_sum = 0.0
            owned_signs = LORD_SIGNS.get(name, [])
            for osign in owned_signs:
                try:
                    si = signs.index(osign)
                    # house number relative to lagna
                    if lagna_idx is not None:
                        house_num = ((si - lagna_idx) % 12) + 1
                        weight_sum += HOUSE_ROLE_WEIGHTS.get(house_num, 0.0)
                except ValueError:
                    continue

            if weight_sum > 0.05:
                func = 'benefic'
            elif weight_sum < -0.05:
                func = 'malefic'
            else:
                func = 'neutral'
        else:
            # fallback to natural classification when lagna missing
            if name in NATURAL_BENEFICS:
                func = 'benefic'
            elif name in NATURAL_MALEFICS:
                func = 'malefic'
            else:
                func = 'neutral'

        # temporary friendship by element vs lagna
        lagna = astro.lagna_sign
        lagna_element = SIGN_ELEMENTS.get(lagna)
        planet_element = SIGN_ELEMENTS.get(getattr(p, 'sign', None))
        temp_friend = 'Neutral'
        if lagna_element and planet_element:
            temp_friend = 'Friend' if lagna_element == planet_element else 'Neutral'

        # temporary friendship small bump/penalty
        if temp_friend == 'Friend':
            components['temp_friend_bonus'] = 0.05
            strength = min(1.0, strength + components['temp_friend_bonus'])
        elif temp_friend == 'Enemy':
            components['temp_friend_bonus'] = -0.05
            strength = max(0.0, strength + components['temp_friend_bonus'])

        # small varga/shadbala proxy: if vargas present, nudge up slightly
        try:
            varga_count = len(getattr(p, 'vargas', {}) or {})
            if varga_count:
                vb = min(0.1, 0.02 * varga_count)
                components['varga_bonus'] = vb
                strength = min(1.0, strength + vb)
        except Exception:
            pass

        # final clamp and rounding
        strength = max(0.0, min(1.0, float(strength)))

        # ---- Shadbala (M2 improved proxies, configurable) ----
        # NATURAL_POTENCY: normalized natural strengths (0..1)
        NATURAL_POTENCY = {
            'Sun': 0.7, 'Moon': 0.85, 'Mars': 0.6, 'Mercury': 0.75,
            'Jupiter': 0.9, 'Venus': 0.85, 'Saturn': 0.55, 'Rahu': 0.45, 'Ketu': 0.45
        }

        def _uccha_bala(planet_obj) -> float:
            """Estimate proximity to exaltation (0..1).

            Uses explicit flags if present, otherwise attempts to use
            `astro.metadata['exaltations']` mapping (planet->degree) when available.
            """
            rawf = getattr(planet_obj, '__dict__', {}).get('flags') if isinstance(getattr(planet_obj, '__dict__', {}), dict) else None
            if isinstance(rawf, dict):
                if rawf.get('exalted'):
                    return 1.0
                if rawf.get('debilitated'):
                    return 0.0
            try:
                exalt_map = getattr(astro, 'metadata', {}).get('exaltations') or {}
                ex_deg = exalt_map.get(planet_obj.name)
                if isinstance(ex_deg, (int, float)) and getattr(planet_obj, 'degree', None) is not None:
                    diff = abs(((planet_obj.degree - ex_deg + 180) % 360) - 180)
                    val = max(0.0, 1.0 - (diff / 30.0))
                    return float(max(0.0, min(1.0, val)))
            except Exception:
                pass
            return 0.5

        def _dig_bala(planet_obj) -> float:
            # house-based directional strength
            try:
                h = int(getattr(planet_obj, 'house') or 0)
            except Exception:
                h = 0
            if h == 10:
                return 30.0
            if h == 1:
                return 25.0
            if h == 4:
                return 20.0
            if h == 7:
                return 18.0
            return 10.0

        def _kala_bala(planet_obj) -> float:
            # time-based strength: use astro.metadata['is_day'] when provided
            base = 50.0
            is_day = getattr(astro, 'metadata', {}).get('is_day')
            if is_day is True and name in ('Sun', 'Mars', 'Jupiter'):
                base += 6.0
            if is_day is False and name in ('Moon', 'Venus', 'Mercury'):
                base += 4.0
            return base

        def _cheshta_bala(planet_obj) -> float:
            base = 10.0
            raw = getattr(planet_obj, '__dict__', {})
            motion = raw.get('motion') if isinstance(raw, dict) else None
            speed = None
            if isinstance(motion, dict):
                speed = motion.get('speed')
                if motion.get('retrograde'):
                    base += 8.0
            if speed:
                approx_max = 1.0
                try:
                    approx_max = max(0.1, float(getattr(astro, 'metadata', {}).get('max_speed', {}).get(name, 1.0)))
                except Exception:
                    approx_max = 1.0
                base += min(10.0, (float(speed) / approx_max) * 10.0)
            return base

        def _drik_bala(planet_obj) -> float:
            total = 0.0
            try:
                aspects_graph = getattr(astro, 'enrichments', {}).get('aspects', {}) or {}
                aspects = aspects_graph.get('edges', []) if isinstance(aspects_graph, dict) else []
                for a in aspects:
                    try:
                        if a.get('source') == name:
                            w = a.get('weight') if isinstance(a.get('weight'), (int, float)) else 2.0
                            total += float(w)
                    except Exception:
                        continue
            except Exception:
                total = 0.0
            return total

        def _naisargika(planet_name) -> float:
            return float(NATURAL_POTENCY.get(planet_name, 0.5))

        rupas = round(6.0 * (0.6 + 0.4 * _uccha_bala(p)), 3)
        dig_bala = round(_dig_bala(p), 3)
        kala_bala = round(_kala_bala(p), 3)
        cheshta_bala = round(_cheshta_bala(p), 3)
        drik_bala = round(_drik_bala(p), 3)
        naisargika = round(_naisargika(name), 3)

        shadbala = {
            'rupas': rupas,
            'dig_bala': dig_bala,
            'kala_bala': kala_bala,
            'cheshta_bala': cheshta_bala,
            'drik_bala': drik_bala,
            'naisargika': naisargika,
        }

        # construct output entry for this planet (fill functional role placeholders later)
        out[name] = {
            'planet': name,
            'dignity': dignity,
            'shadbala': shadbala,
            'functional_role': func,
            'combust': combust,
            'retrograde': retro,
            'temporary_friendship': temp_friend,
            'strength': round(strength, 3),
            'strength_components': {k: round(v, 3) for k, v in components.items()},
        }

        # write back strength into planet state objects where possible
        try:
            for pp in astro.planets:
                if pp.name == name:
                    pp.strength = round(strength, 3)
        except Exception:
            pass

    # augment with functional role engine results (table-driven or heuristic)
    try:
        froles = compute_functional_roles(astro)
        for pname, prow in froles.items():
            if pname in out:
                out[pname]['natural_role'] = prow.get('natural_role')
                out[pname]['owns_houses'] = prow.get('owns_houses')
                out[pname]['functional_role'] = prow.get('functional_role')
                out[pname]['functional_score'] = prow.get('functional_score')
                if prow.get('yoga_role'):
                    out[pname]['yoga_role'] = prow.get('yoga_role')
                # write back to planet state
                try:
                    for pp in astro.planets:
                        if pp.name == pname:
                            pp.functional_role = prow.get('functional_role')
                            pp.functional_score = prow.get('functional_score')
                except Exception:
                    pass
    except Exception:
        # best-effort: if functional engine fails, leave existing minimal fields
        pass

    return out


def compute_house_summaries(astro: AstroState) -> List[Dict[str, Any]]:
    """Create a simple summary per house present in `astro.houses`.

    Each summary includes number, sign, lord, and occupants (planet names).
    """
    summaries: List[Dict[str, Any]] = []
    # try to use precomputed planet_strengths if available
    strengths_map = None
    try:
        strengths_map = getattr(astro, 'enrichments', {}).get('planet_strengths') if getattr(astro, 'enrichments', None) else None
    except Exception:
        strengths_map = None

    # aspects map
    aspects_graph = getattr(astro, 'enrichments', {}).get('aspects', {}) or {}
    aspects = aspects_graph.get('edges', []) if isinstance(aspects_graph, dict) else []

    for h in astro.houses or []:
        num = h.get('number') if isinstance(h, dict) else getattr(h, 'number', None)
        sign = h.get('sign') if isinstance(h, dict) else getattr(h, 'sign', None)
        lord = h.get('lord') if isinstance(h, dict) else getattr(h, 'lord', None)
        occupants = [p.name for p in astro.planets if p.house == num and p.name and p.name.lower() != 'empty']

        # compute lord strength
        lord_strength = None
        if lord and strengths_map and isinstance(strengths_map, dict):
            linfo = strengths_map.get(lord)
            if isinstance(linfo, dict):
                lord_strength = linfo.get('strength')

        # compute benefic and malefic pressure using functional roles and strength
        benefic_pressure = 0.0
        malefic_pressure = 0.0
        for occ in occupants:
            pinfo = None
            if strengths_map and isinstance(strengths_map, dict):
                pinfo = strengths_map.get(occ)
            if not pinfo:
                # fallback: try to find planet object
                pobj = next((pp for pp in astro.planets if pp.name == occ), None)
                if pobj:
                    pinfo = {'functional_role': getattr(pobj, 'functional_role', None), 'functional_score': getattr(pobj, 'functional_score', None), 'strength': getattr(pobj, 'strength', None)}
            if not pinfo:
                continue
            frole = pinfo.get('functional_role')
            fscore = float(pinfo.get('functional_score') or 0.5)
            pstr = float(pinfo.get('strength') or 0.5)
            contrib = fscore * pstr
            if frole in ('functional_benefic', 'yogakaraka'):
                benefic_pressure += contrib
            elif frole in ('functional_malefic',):
                malefic_pressure += contrib

        occ_count = max(1, len(occupants))
        benefic_pressure = round(benefic_pressure / occ_count, 3)
        malefic_pressure = round(malefic_pressure / occ_count, 3)

        # aspected_by: planets that aspect any occupant or the lord
        aspectors = set()
        for a in aspects:
            try:
                fr = a.get('source')
                to = a.get('target')
                if to in occupants or to == lord:
                    aspectors.add(fr)
            except Exception:
                continue

        # simple house score: base 0.5 + (benefic - malefic) * 0.5 (clamped)
        house_score = 0.5 + (benefic_pressure - malefic_pressure) * 0.5
        house_score = max(0.0, min(1.0, round(house_score, 3)))

        summaries.append({
            'number': num,
            'sign': sign,
            'lord': lord,
            'occupants': occupants,
            'lord_strength': round(float(lord_strength), 3) if lord_strength is not None else None,
            'benefic_pressure': benefic_pressure,
            'malefic_pressure': malefic_pressure,
            'aspected_by': sorted(list(aspectors)),
            'house_score': house_score,
        })

    return summaries


def compute_lagna_summary(astro: AstroState) -> Dict[str, Any]:
    """Return a small summary for the lagna (ascendant)."""
    sign = getattr(astro, 'lagna_sign', None)
    if not sign:
        return {}
    # prefer explicit lagna_degree on the astro state
    degree = getattr(astro, 'lagna_degree', None)

    element = SIGN_ELEMENTS.get(sign)
    modality = 'Movable' if sign in ['Aries', 'Cancer', 'Libra', 'Capricorn'] else ('Fixed' if sign in ['Taurus', 'Leo', 'Scorpio', 'Aquarius'] else 'Dual')
    lord = SIGN_LORD.get(sign)
    return {
        'sign': sign,
        'degree': round(float(degree), 3) if degree is not None else None,
        'element': element,
        'modality': modality,
        'lord': lord,
    }
