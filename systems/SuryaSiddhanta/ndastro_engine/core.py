"""Core functions for astronomical calculations using Skyfield library."""

from datetime import datetime, timedelta
from math import atan2, degrees, radians, tan
from typing import TYPE_CHECKING, cast

from skyfield.almanac import cos, find_discrete, sin, sunrise_sunset
from skyfield.data.spice import inertial_frames
from skyfield.elementslib import osculating_elements_of
from skyfield.framelib import ecliptic_frame
from skyfield.nutationlib import mean_obliquity
from skyfield.toposlib import wgs84

from ndastro_engine.config import eph, get_effective_settings, ts
from ndastro_engine.constants import (
    DAYS_PER_JULIAN_CENTURY,
    IAU_PRECESSION_LONGITUDE_C1,
    IAU_PRECESSION_LONGITUDE_C2,
    J2000_TT,
    MEAN_NODE_C2,
    MEAN_NODE_C3,
    MEAN_NODE_C4,
    MEAN_NODE_EPOCH_DEG,
    MEAN_NODE_RATE_DEG_PER_CENTURY,
)
from ndastro_engine.enums import Planets
from ndastro_engine.models import PlanetPosition
from ndastro_engine.utils import get_elevation_by_latlon, normalize_degree

if TYPE_CHECKING:
    from skyfield.positionlib import Barycentric
    from skyfield.timelib import Time
    from skyfield.units import Angle, Rate
    from skyfield.vectorlib import VectorSum


def get_planet_position(planet: Planets, lat: float, lon: float, given_time: datetime) -> PlanetPosition:
    """Return the tropical position of the planet for the given latitude, longitude, and datetime.

    Args:
        planet (Planets): The planet to calculate the position for.
        lat (float): The latitude of the observer in decimal degrees.
        lon (float): The longitude of the observer in decimal degrees.
        given_time (datetime): The datetime of the observation in UTC.

    Returns:
        PlanetPosition: The tropical latitude, longitude, distance, and their rates of change of the planet.

    """
    t = ts.utc(given_time)

    if planet in (Planets.RAHU, Planets.KETHU):
        pos = get_lunar_node_positions(given_time)
        return PlanetPosition(
            0.0,
            pos[0] if planet == Planets.RAHU else pos[1],
            0.0,
            0.0,
            0.0,
            0.0,
        )

    if planet == Planets.ASCENDANT:
        asc_lon = get_ascendent_position(lat, lon, given_time)
        return PlanetPosition(
            0.0,
            asc_lon,
            0.0,
            0.0,
            0.0,
            0.0,
        )

    if planet == Planets.EMPTY:
        return PlanetPosition(
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        )

    t = ts.utc(given_time)
    eth: VectorSum = cast("VectorSum", eph["earth"])

    if get_effective_settings().position_reference == "geocentric":
        astrometric = cast("Barycentric", eth.at(t)).observe(eph[planet.astronomical_code]).apparent()
    else:
        elevation = get_elevation_by_latlon(lat, lon)
        observer: VectorSum = eth + wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon, elevation_m=elevation)
        astrometric = cast("Barycentric", observer.at(t)).observe(eph[planet.astronomical_code]).apparent()

    latitude, longitude, distance, speed_latitude, speed_longitude, speed_distance = astrometric.frame_latlon_and_rates(ecliptic_frame)

    return PlanetPosition(
        cast("float", latitude.degrees),
        cast("float", longitude.degrees),
        cast("float", distance.au),
        cast("float", cast("Rate", speed_latitude.degrees).per_day),
        cast("float", cast("Rate", speed_longitude.degrees).per_day),
        cast("float", speed_distance.au_per_d),
    )


def get_planets_position(planets: list[Planets], lat: float, lon: float, given_time: datetime) -> dict[Planets, PlanetPosition]:
    """Return the tropical positions of all planets for the given latitude, longitude, and datetime.

    Args:
        planets (list[Planets]): The list of planets to calculate the positions for.
        lat (float): The latitude of the observer in decimal degrees.
        lon (float): The longitude of the observer in decimal degrees.
        given_time (datetime): The datetime of the observation in UTC.

    Returns:
        dict[Planets, PlanetPosition]: A dictionary mapping each planet to its tropical/sidereal latitude,
            longitude, and distance & their rates of change.

    """
    positions: dict[Planets, PlanetPosition] = {}
    for planet in planets if len(planets) > 0 else Planets:
        positions[planet] = get_planet_position(planet, lat, lon, given_time)

    return positions


def get_sunrise_sunset(lat: float, lon: float, given_time: datetime, elevation: float | None = None) -> tuple[datetime, datetime]:
    """Calculate the sunrise and sunset times for a given location and date.

    Args:
        lat (float): The latitude of the location in decimal degrees.
        lon (float): The longitude of the location in decimal degrees.
        given_time (datetime): The date and time for which to calculate the sunrise and sunset times.
        elevation (float | None, optional): Elevation in meters.
            If None, it is resolved from latitude/longitude using an elevation API.

    Returns:
        tuple[datetime, datetime]: A tuple containing the sunrise and sunset times as datetime objects.

    """
    # Define location
    effective_elevation = get_elevation_by_latlon(lat, lon) if elevation is None else elevation
    location = wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon, elevation_m=effective_elevation)

    # Define time range for the search (e.g., one day)
    t_start = ts.utc(given_time.date())  # Start of the day
    t_end = ts.utc(given_time.date() + timedelta(days=1))  # End of the day

    # Find sunrise time
    f = sunrise_sunset(eph, location)
    times, events = find_discrete(t_start, t_end, f)

    sunrise, sunset = cast("list[Time]", [time for time, _ in zip(times, events, strict=False)])

    return cast("tuple[datetime, datetime]", (sunrise.utc_datetime(), sunset.utc_datetime()))


def get_ascendent_position(lat: float, lon: float, given_time: datetime) -> float:
    """Calculate the tropical ascendant.

    Args:
        lat (float): The latitude of the observer in decimal degrees.
        lon (float): The longitude of the observer in decimal degrees.
        given_time (datetime): The datetime of the observation.

    Returns:
        float: The longitude of the tropical/sidereal ascendant.

    """
    t = ts.utc(given_time)

    oe = mean_obliquity(t.tdb) / 3600
    oer = radians(oe)

    gmst: float = cast("float", t.gmst)

    lst = (gmst + lon / 15) % 24

    lstr = radians(lst * 15)

    # source: https://astronomy.stackexchange.com/a/55891 by pm-2ring
    ascr = atan2(cos(lstr), -(sin(lstr) * cos(oer) + tan(radians(lat)) * sin(oer)))

    asc = degrees(ascr)

    return normalize_degree(asc)


def get_lunar_node_positions(given_time: datetime) -> tuple[float, float]:
    """Calculate the positions of the lunar nodes (Rahu and Kethu) for a given datetime.

    The calculation method is controlled by the ``node_type`` setting in
    ``ndastro_engine.config``:

    - ``'true'``  (default) — osculating (true) nodes via Skyfield's
      ``osculating_elements_of()``.  Corresponds to JHora ``TrueNodes=1``.
    - ``'mean'``  — mean nodes derived from the IAU 2006 precession model
      (longitude of ascending node of the ecliptic).
      Corresponds to JHora ``TrueNodes=0``.

    Args:
        given_time (datetime): The datetime in UTC for which to calculate the
            lunar node positions.

    Returns:
        tuple[float, float]: Longitudes of Rahu and Kethu in decimal degrees.

    """
    tm = ts.from_datetime(given_time)
    T = (tm.tt - J2000_TT) / DAYS_PER_JULIAN_CENTURY  # Julian centuries from J2000.0

    if get_effective_settings().node_type == "mean":
        # Mean lunar node: use IAU 2006 precession longitude of the ascending
        # node, approximated from the standard polynomial (matches Swiss
        # Ephemeris mean-node output to within ~0.01° for modern dates).
        # Polynomial from IAU SOFA / Meeus Ch. 22 (degrees):
        mean_node_deg = (
            MEAN_NODE_EPOCH_DEG + MEAN_NODE_RATE_DEG_PER_CENTURY * T + MEAN_NODE_C2 * T**2 + MEAN_NODE_C3 * T**3 + MEAN_NODE_C4 * T**4
        ) % 360.0
        rahu_position = normalize_degree(mean_node_deg)
    else:
        # True (osculating) nodes in ecliptic of date (matches JHora / DrikPanchang).
        # osculating_elements_of uses the fixed ECLIPJ2000 frame; add the IAU 2006
        # general precession in longitude (ψ_A) to convert to ecliptic of date.
        earth = eph["earth"]
        moon = eph["moon"]
        position = cast("VectorSum", (moon - earth)).at(tm)
        elements = osculating_elements_of(position, inertial_frames["ECLIPJ2000"])
        eclipj2000_node = cast("float", cast("Angle", elements.longitude_of_ascending_node).degrees)
        precession_deg = (IAU_PRECESSION_LONGITUDE_C1 * T + IAU_PRECESSION_LONGITUDE_C2 * T**2) / 3600.0
        rahu_position = normalize_degree(eclipj2000_node + precession_deg)

    kethu_position = normalize_degree(rahu_position + 180)
    return rahu_position, kethu_position


__all__ = ["get_ascendent_position", "get_lunar_node_positions", "get_planet_position", "get_planets_position", "get_sunrise_sunset"]
