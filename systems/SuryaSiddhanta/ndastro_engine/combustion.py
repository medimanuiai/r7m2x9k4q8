"""Provides functions to determine if a planet is in combustion."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, cast

from skyfield.searchlib import find_discrete
from skyfield.timelib import Time
from skyfield.toposlib import Topos

from ndastro_engine.config import eph, ts
from ndastro_engine.constants import DAYS_IN_YEAR
from ndastro_engine.enums import Planets

if TYPE_CHECKING:
    from skyfield.positionlib import Barycentric

# Define Earth
earth = eph["earth"]

ORB_BY_PLANET: dict[str, float] = {
    Planets.MERCURY.astronomical_code: 12.0,
    Planets.VENUS.astronomical_code: 8.0,
    Planets.MARS.astronomical_code: 17.0,
    Planets.JUPITER.astronomical_code: 11.0,
    Planets.SATURN.astronomical_code: 15.0,
}


class CombustFunction:
    """Callable combustion function for Skyfield's find_discrete."""

    step_days = 1.0  # Step size in days for Skyfield's find_discrete

    def __init__(self, planet_name: str, latitude: float, longitude: float, orb: float) -> None:
        """Initialize a new instance of the combustion function.

        Args:
            planet_name: The name of the planet to check (Skyfield code).
            latitude: The latitude of the observation location.
            longitude: The longitude of the observation location.
            orb: Combustion orb in degrees.

        """
        self.planet_name = planet_name
        self.latitude = latitude
        self.longitude = longitude
        self.orb = orb

    def __call__(self, t: Time) -> bool:
        """Return True if the planet is combust at the given time."""
        observer = (earth + Topos(latitude=self.latitude, longitude=self.longitude)).at(t)

        astrometric_planet = cast("Barycentric", observer).observe(eph[self.planet_name]).apparent()
        astrometric_sun = cast("Barycentric", observer).observe(eph[Planets.SUN.astronomical_code]).apparent()

        separation = astrometric_planet.separation_from(astrometric_sun).degrees
        # Return the comparison result directly (handles both scalar and array cases)
        return cast("float", separation) <= self.orb


def _get_combust_function(
    planet_name: str,
    latitude: float,
    longitude: float,
    orb: float,
) -> CombustFunction:
    """Create a CombustFunction instance for a given planet and location."""
    return CombustFunction(planet_name, latitude, longitude, orb)


def find_combust_periods(
    start_date: datetime,
    end_date: datetime,
    planet_name: str,
    latitude: float,
    longitude: float,
) -> list[tuple[datetime, datetime]]:
    """Calculate combustion periods for a planet within a specified date range.

    Args:
        start_date: The start date of the period to check.
        end_date: The end date of the period to check.
        planet_name: The name of the planet to check (Skyfield code).
        latitude: The latitude of the observation location.
        longitude: The longitude of the observation location.

    Returns:
        List of (start, end) datetimes representing combustion periods.

    """
    if planet_name in [
        Planets.SUN.astronomical_code,
        Planets.ASCENDANT.astronomical_code,
        Planets.EMPTY.astronomical_code,
        Planets.RAHU.astronomical_code,
        Planets.KETHU.astronomical_code,
    ]:
        return []

    orb = ORB_BY_PLANET.get(planet_name)
    if orb is None:
        return []

    t0 = ts.utc(start_date)
    t1 = ts.utc(end_date)

    times, values = find_discrete(
        t0,
        t1,
        _get_combust_function(planet_name, latitude, longitude, orb),
    )

    combust_periods: list[tuple[datetime, datetime]] = []
    in_combust = False
    combust_start = None

    for t, combust in zip(times, values, strict=False):
        if combust:
            if not in_combust:
                combust_start = cast("Time", t).utc_datetime()
                in_combust = True
        elif in_combust:
            combust_periods.append((cast("datetime", combust_start), t.utc_datetime()))
            in_combust = False

    if in_combust and combust_start is not None:
        combust_periods.append((cast("datetime", combust_start), cast("datetime", t1.utc_datetime())))

    return combust_periods


def is_planet_in_combust(
    check_date: datetime,
    planet_name: str,
    latitude: float,
    longitude: float,
) -> tuple[bool, datetime | None, datetime | None]:
    """Check if a planet is combust on a specific date.

    Args:
        check_date: The date to check for combustion.
        planet_name: The name of the planet to check (Skyfield code).
        latitude: The latitude of the observation location.
        longitude: The longitude of the observation location.

    Returns:
        A tuple containing a boolean indicating if the planet is combust,
        the start datetime of the combustion period, and the end datetime of the combustion period.
        If the planet is not combust, the start and end datetimes will be None.

    """
    if planet_name in [
        Planets.SUN.astronomical_code,
        Planets.ASCENDANT.astronomical_code,
        Planets.EMPTY.astronomical_code,
        Planets.RAHU.astronomical_code,
        Planets.KETHU.astronomical_code,
    ]:
        return (False, None, None)

    start_date = check_date - timedelta(days=DAYS_IN_YEAR)
    end_date = check_date + timedelta(days=DAYS_IN_YEAR)
    combust_periods = find_combust_periods(
        start_date,
        end_date,
        planet_name,
        latitude,
        longitude,
    )

    for period_start, period_end in combust_periods:
        if period_start <= check_date <= period_end:
            return (True, period_start, period_end)

    return (False, None, None)
