"""Models used in ndastro_engine module."""

from typing import NamedTuple


class PlanetPosition(NamedTuple):
    """A named tuple representing the position and speed of a planet.

    Attributes:
        latitude (float): The ecliptic latitude of the planet in degrees.
        longitude (float): The ecliptic longitude of the planet in degrees.
        distance (float): The distance from Earth to the planet in astronomical units.
        speed_latitude (float): The rate of change of latitude in degrees per day.
        speed_longitude (float): The rate of change of longitude in degrees per day.
        speed_distance (float): The rate of change of distance in AU per day.

    """

    latitude: float
    longitude: float
    distance: float
    speed_latitude: float
    speed_longitude: float
    speed_distance: float
