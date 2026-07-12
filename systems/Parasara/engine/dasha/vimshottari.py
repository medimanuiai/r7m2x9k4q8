from typing import List, Dict, Any
from datetime import datetime, timedelta

# Canonical Vimshottari order and durations (years)
VIMSHOTTARI_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
VIMSHOTTARI_YEARS = {'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17}


def _normalize_deg(d: float) -> float:
    return d % 360.0


def _nakshatra_index_from_longitude(long_deg: float) -> (int, int, float):
    """Return (nak_index 0-26, pada 1-4, offset_within_nak_degrees)

    Each nakshatra is 13°20' = 13.3333333333 degrees.
    """
    nak_size = 13 + 1/3  # 13.333333333333334
    norm = _normalize_deg(long_deg)
    idx = int(norm // nak_size) % 27
    within = norm - (idx * nak_size)
    pada = int(within // (nak_size / 4)) + 1
    return idx, pada, within


NAKSHATRA_LORDS = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
]


def compute_vimshottari(astro, periods=3) -> List[Dict[str, Any]]:
    """Compute Vimshottari mahadashas with nested antardashas and pratyantardashas.

    Returns a list of mahadasha dicts with nested `antardashas` and each antardasha may include `pratyantardashas`.
    The calculation uses 365.2425 days/year and the canonical 120-year cycle proportions.
    """
    out: List[Dict[str, Any]] = []
    moon = next((p for p in getattr(astro, 'planets', []) or [] if p.name == 'Moon'), None)
    if not moon:
        return out
    # try to read longitude in degrees
    moon_long = getattr(moon, 'degree', None) or getattr(moon, 'longitude', None) or 0.0
    idx, pada, within = _nakshatra_index_from_longitude(float(moon_long))
    nak_lord = NAKSHATRA_LORDS[idx]

    # compute fraction remaining in nakshatra
    nak_size = 13 + 1/3
    fraction_remaining = (nak_size - within) / nak_size
    # mahadasha durations in years
    total_cycle_years = sum(VIMSHOTTARI_YEARS.values())  # should be 120
    years_lord = VIMSHOTTARI_YEARS[nak_lord]
    # start datetime
    start = None
    try:
        start = getattr(astro, 'metadata', {}).get('birth_datetime_utc')
    except Exception:
        start = None
    try:
        if start:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        else:
            start_dt = datetime.utcnow()
    except Exception:
        start_dt = datetime.utcnow()

    days_per_year = 365.2425

    # compute first mahadasha remaining days
    mahadasha_full_days = years_lord * days_per_year
    remaining_days = mahadasha_full_days * fraction_remaining

    # find start index in order
    start_idx = VIMSHOTTARI_ORDER.index(nak_lord)
    cur = start_dt

    for m in range(periods):
        lord = VIMSHOTTARI_ORDER[(start_idx + m) % len(VIMSHOTTARI_ORDER)]
        years = VIMSHOTTARI_YEARS[lord]
        if m == 0:
            duration_days = int(round(remaining_days))
        else:
            duration_days = int(round(years * days_per_year))
        end = cur + timedelta(days=duration_days)
        mah = {'period': 'Mahadasha', 'lord': lord, 'start': cur.isoformat(), 'end': end.isoformat(), 'duration_days': duration_days, 'antardashas': []}

        # compute antardashas for this mahadasha
        mah_years = years if m != 0 else (remaining_days / days_per_year)
        mah_days = duration_days
        for sub in VIMSHOTTARI_ORDER:
            sub_years = VIMSHOTTARI_YEARS[sub]
            ant_days = int(round(mah_days * (sub_years / total_cycle_years)))
            ant_start = mah['start']
            # compute actual start for each antardasha by summing previous durations
            # build incrementally
            break

        # naive incremental build for antardashas
        ant_cur = cur
        for sub in VIMSHOTTARI_ORDER:
            sub_years = VIMSHOTTARI_YEARS[sub]
            ant_days = int(round(mah_days * (sub_years / total_cycle_years)))
            ant_end = ant_cur + timedelta(days=ant_days)
            ant = {'lord': sub, 'start': ant_cur.isoformat(), 'end': ant_end.isoformat(), 'duration_days': ant_days, 'pratyantardashas': []}
            # pratyantardashas: subdivide by same proportion
            pr_cur = ant_cur
            for sub2 in VIMSHOTTARI_ORDER:
                sub2_years = VIMSHOTTARI_YEARS[sub2]
                pr_days = int(round(ant_days * (sub2_years / total_cycle_years)))
                pr_end = pr_cur + timedelta(days=pr_days)
                ant['pratyantardashas'].append({'lord': sub2, 'start': pr_cur.isoformat(), 'end': pr_end.isoformat(), 'duration_days': pr_days})
                pr_cur = pr_end

            mah['antardashas'].append(ant)
            ant_cur = ant_end

        out.append(mah)
        cur = end

    return out

