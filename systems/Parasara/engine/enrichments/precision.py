"""Degree and precision utilities for celestial longitudes."""
from typing import Optional


def round_degree(value: Optional[float], places: int = 2) -> Optional[float]:
    """Round a longitude/degree to a fixed number of decimal places.

    Returns None if input is None.
    """
    if value is None:
        return None
    try:
        return round(float(value), places)
    except Exception:
        return None


def normalize_longitude(lon: Optional[float]) -> Optional[float]:
    """Normalize longitude to [0,360) range and round to 2 decimals."""
    if lon is None:
        return None
    try:
        v = float(lon) % 360.0
        if v < 0:
            v += 360.0
        return round_degree(v, 2)
    except Exception:
        return None
