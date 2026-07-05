"""Utility functions for the ndastro_engine package.

This module provides:
- get_app_data_dir: Get the application data directory for the given app name.
"""

import json
import os
import sys
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Optional

from ndastro_engine.constants import (
    AVERAGE_DAYS_IN_MONTH,
    DEGREE_MAX,
    OS_MAC,
    OS_WIN,
)


# In-memory cache for local elevation data
_ELEVATION_CACHE: Optional[dict] = None


def _load_elevation_cache() -> dict:
    """Load elevation cache from env path or packaged data file.

    Returns an empty dict when no cache is available.
    """
    global _ELEVATION_CACHE
    if _ELEVATION_CACHE is not None:
        return _ELEVATION_CACHE

    # Candidate paths (env var first, then packaged file)
    candidates: list[Path] = []
    env_path = os.getenv("NDASTRO_ELEVATION_SOURCE")
    if env_path:
        candidates.append(Path(env_path))

    packaged = Path(__file__).resolve().parent / "data" / "elevation" / "elevation_cache.json"
    candidates.append(packaged)

    for p in candidates:
        try:
            if p.exists():
                with p.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    if isinstance(data, dict):
                        _ELEVATION_CACHE = data
                        return _ELEVATION_CACHE
        except Exception:
            # ignore malformed files and continue to next candidate
            continue

    _ELEVATION_CACHE = {}
    return _ELEVATION_CACHE


# Lazy-initialised SRTM data handle (if the `srtm` package is installed)
_SRTM_DATA: Optional[object] = None


def _get_srtm_elevation(lat: float, lon: float) -> Optional[float]:
    """Return elevation from SRTM if available; otherwise return None.

    This function lazily imports the `srtm` package so tests that do not
    install it can still run using the JSON cache fallback.
    """
    global _SRTM_DATA
    try:
        if _SRTM_DATA is None:
            import srtm as _srtm  # type: ignore

            # get_data() will download tiles on demand into ~/.cache/srtm by default
            _SRTM_DATA = _srtm.get_data()

        if _SRTM_DATA is not None:
            val = _SRTM_DATA.get_elevation(lat, lon)
            if val is None:
                return None
            return float(val)
    except Exception:
        return None

    return None


@lru_cache(maxsize=256)
def get_elevation_by_latlon(lat: float, lon: float, timeout: float = 10.0) -> float:
    """Get elevation in meters for latitude and longitude.

    Uses a local elevation JSON cache and falls back to 0.0 when lookup fails.

    Args:
        lat (float): Latitude in decimal degrees.
        lon (float): Longitude in decimal degrees.
        timeout (float, optional): Ignored for local lookup. Kept for API compatibility.

    Returns:
        float: Elevation in meters, or 0.0 when unavailable.

    """
    # Prefer SRTM when available and not explicitly disabled via env var.
    use_srtm = os.getenv("NDASTRO_USE_SRTM", "1")
    if use_srtm != "0":
        srtm_val = _get_srtm_elevation(lat, lon)
        if srtm_val is not None:
            return srtm_val

    # Load elevation cache (from env var or packaged data file)
    cache = _load_elevation_cache()
    if not cache:
        return 0.0

    # Exact-match on rounded keys (two decimals)
    key = f"{round(lat,2):.2f},{round(lon,2):.2f}"
    if key in cache:
        try:
            return float(cache[key])
        except (TypeError, ValueError):
            return 0.0

    # Nearest-neighbour fallback: choose the cache entry with minimal manhattan distance
    best_k: Optional[str] = None
    best_score = float("inf")
    for k in cache.keys():
        try:
            klat_str, klon_str = k.split(",")
            klat = float(klat_str)
            klon = float(klon_str)
        except Exception:
            continue
        score = abs(klat - lat) + abs(klon - lon)
        if score < best_score:
            best_score = score
            best_k = k

    if best_k is not None:
        try:
            return float(cache[best_k])
        except (TypeError, ValueError):
            return 0.0

    return 0.0


def parse_iso_datetime(datetime_str: str) -> datetime:
    """Parse an ISO datetime string.

    If timezone information is missing, UTC is assumed.

    Args:
        datetime_str (str): ISO datetime string to parse.

    Returns:
        datetime: Parsed timezone-aware datetime.

    Raises:
        ValueError: If the string is not a valid ISO datetime.

    """
    normalized = datetime_str.strip()

    # Python datetime.fromisoformat does not accept a trailing 'Z'.
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        msg = f"Invalid ISO datetime string: {datetime_str}"
        raise ValueError(msg) from exc

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)

    return parsed


def get_app_data_dir(appname: str) -> Path:
    """Get the application data directory for the given app name.

    Parameters
    ----------
    appname : str
        Name of the application.

    Returns
    -------
    Path
        Path to the application data directory.

    """
    home = Path.home()
    if sys.platform == OS_WIN:
        return home / "AppData/Local" / appname

    if sys.platform == OS_MAC:
        return home / "Library/Application Support" / appname

    # Linux and other Unix-like systems (uses XDG spec fallback)
    data_home = os.getenv("XDG_DATA_HOME", "~/.local/share")
    return Path(data_home).expanduser() / appname


def normalize_degree(degree: float) -> float:
    """Normalize the degree to be within 0-360.

    Args:
        degree (float): The degree to normalize.

    Returns:
        float: The normalized degree.

    """
    return (degree % DEGREE_MAX + DEGREE_MAX) % DEGREE_MAX


def dms2dd(degrees: int, minutes: int, seconds: float, sign: int = 1) -> float:
    """Convert degrees, minutes, and seconds to decimal degrees.

    Args:
        degrees (int): The degrees component.
        minutes (int): The minutes component.
        seconds (float): The seconds component.
        sign (int, optional): The sign of the angle. Defaults to 1 (positive).

    Returns:
        float: The angle in decimal degrees.

    """
    decimal_degrees = abs(degrees) + minutes / 60 + seconds / 3600
    return sign * decimal_degrees


def dd2dms(decimal_degrees: float) -> tuple[int, int, float, int]:
    """Convert decimal degrees to degrees, minutes, and seconds.

    Args:
        decimal_degrees (float): The angle in decimal degrees.

    Returns:
        tuple[int, int, float, int]: A tuple containing degrees, minutes, seconds, and sign.

    """
    sign = 1 if decimal_degrees >= 0 else -1
    abs_degrees = abs(decimal_degrees)
    degrees = int(abs_degrees)
    minutes_full = (abs_degrees - degrees) * 60
    minutes = int(minutes_full)
    seconds = (minutes_full - minutes) * 60
    return degrees, minutes, seconds, sign


def dd2dmsstr(decimal_degrees: float) -> str:
    """Convert decimal degrees to a formatted DMS string.

    Args:
        decimal_degrees (float): The angle in decimal degrees.

    Returns:
        str: The angle in DMS format as a string.

    """
    degrees, minutes, seconds, sign = dd2dms(decimal_degrees)
    sign_str = "" if sign >= 0 else "-"
    return f"{sign_str}{degrees}° {minutes}' {seconds:.2f}\""


def decimal_years_to_years_months_days_ghatis(decimal_years: float) -> tuple[int, int, int, int, int, int, int]:
    """Convert decimal years to years, months, days, hours, minutes, seconds, and ghatis.

    Args:
        decimal_years (float): The time duration in decimal years.

    Returns:
        tuple[int, int, int, int, int, int, int]: A tuple containing years, months, days, hours, minutes, seconds, and ghatis.

    """
    years = int(decimal_years)
    remaining_years = decimal_years - years

    months = int(remaining_years * 12)
    remaining_months = (remaining_years * 12 - months) * AVERAGE_DAYS_IN_MONTH  # Average days in a month

    days = int(remaining_months)  # Average days in a month
    remaining_days = remaining_months - days

    hours = int(remaining_days * 24)  # 1 day = 24 hours
    remaining_hours = remaining_days * 24 - hours

    mins = int(remaining_hours * 60)  # 1 hour = 60 minutes
    remaining_mins = remaining_hours * 60 - mins

    secs = int(remaining_mins * 60)  # 1 minute = 60 seconds
    ghatis = int(hours * 60 / 24)  # 1 ghati = 24 minutes

    return years, months, days, hours, mins, secs, ghatis
