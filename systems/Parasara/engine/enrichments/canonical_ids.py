"""Canonical ID helpers for planets, houses and points."""
from typing import Dict

PLANET_ALIASES: Dict[str, str] = {
    'Sun': 'sun',
    'Moon': 'moon',
    'Mars': 'mars',
    'Mercury': 'mercury',
    'Jupiter': 'jupiter',
    'Venus': 'venus',
    'Saturn': 'saturn',
    'Rahu': 'rahu',
    'Ketu': 'ketu'
}


def canonical_planet_id(name: str) -> str:
    """Return a stable canonical id for a planet name."""
    if not name:
        return 'unknown'
    return PLANET_ALIASES.get(name, name.strip().lower())


def canonical_house_id(house_number: int) -> str:
    """Return a stable canonical id for a house number."""
    try:
        n = int(house_number)
    except Exception:
        n = 0
    return f'house_{n}'
