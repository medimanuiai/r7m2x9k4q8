"""Module is to hold planet enums."""

from enum import IntEnum
from typing import Literal, TypeAlias, cast

PlanetCode: TypeAlias = Literal["EMPTY", "AS", "SU", "MO", "MA", "ME", "JU", "VE", "SA", "RA", "KE"]
AstronomicalCode: TypeAlias = Literal[
    "sun", "moon", "mars barycenter", "mercury", "jupiter barycenter", "venus", "saturn barycenter", "rahu", "kethu", "earth", "ascendant", ""
]


class Planets(IntEnum):
    """Enum to hold planets."""

    EMPTY = -1
    ASCENDANT = 0
    SUN = 1
    MOON = 2
    MARS = 3
    MERCURY = 4
    JUPITER = 5
    VENUS = 6
    SATURN = 7
    RAHU = 8
    KETHU = 9

    @staticmethod
    def to_string(num: int) -> str:
        """Convert planet number to display name of the planet.

        Args:
            num (int): the planet number

        Returns:
            str: return the planet name

        """
        return Planets(num).name if num in Planets._value2member_map_ else "empty"

    @staticmethod
    def from_astronomical_code(code: AstronomicalCode) -> "Planets":
        """Convert planet's astronomical code to planet enum.

        Args:
            code (AstronomicalCode): the planet's astronomical code

        Returns:
            Planets: the corresponding planet enum

        """
        planet_codes = {
            "empty": Planets.EMPTY,
            "ascendant": Planets.ASCENDANT,
            "sun": Planets.SUN,
            "moon": Planets.MOON,
            "mars barycenter": Planets.MARS,
            "mercury": Planets.MERCURY,
            "jupiter barycenter": Planets.JUPITER,
            "venus": Planets.VENUS,
            "saturn barycenter": Planets.SATURN,
            "rahu": Planets.RAHU,
            "kethu": Planets.KETHU,
        }

        return planet_codes.get(code, Planets.EMPTY)

    @staticmethod
    def from_code(code: PlanetCode) -> "Planets":
        """Convert planet code to planet enum.

        Args:
            code (PlanetCode): the planet code

        Returns:
            Planets: the corresponding planet enum

        """
        planet_codes = {
            "EMPTY": Planets.EMPTY,
            "AS": Planets.ASCENDANT,
            "SU": Planets.SUN,
            "MO": Planets.MOON,
            "MA": Planets.MARS,
            "ME": Planets.MERCURY,
            "JU": Planets.JUPITER,
            "VE": Planets.VENUS,
            "SA": Planets.SATURN,
            "RA": Planets.RAHU,
            "KE": Planets.KETHU,
        }

        return planet_codes.get(code, Planets.EMPTY)

    @staticmethod
    def to_list() -> list[str]:
        """Convert planet enum to list of planet name.

        Returns:
            list[str]: list of planet names

        """
        return [el.name for el in Planets]

    @property
    def code(self) -> PlanetCode:
        """Return the planet code.

        Returns:
            PlanetCode: the planet code

        """
        planet_codes = {
            Planets.EMPTY: "EMPTY",
            Planets.ASCENDANT: "AS",
            Planets.SUN: "SU",
            Planets.MOON: "MO",
            Planets.MARS: "MA",
            Planets.MERCURY: "ME",
            Planets.JUPITER: "JU",
            Planets.VENUS: "VE",
            Planets.SATURN: "SA",
            Planets.RAHU: "RA",
            Planets.KETHU: "KE",
        }

        return cast("PlanetCode", planet_codes.get(self, "EMPTY"))

    @property
    def astronomical_code(self) -> AstronomicalCode:
        """Return the astronomical code for the planet.

        Returns:
            AstronomicalCode: the astronomical code for the planet

        """
        astronomical_codes = {
            Planets.EMPTY: "empty",
            Planets.ASCENDANT: "ascendant",
            Planets.SUN: "sun",
            Planets.MOON: "moon",
            Planets.MARS: "mars barycenter",
            Planets.MERCURY: "mercury",
            Planets.JUPITER: "jupiter barycenter",
            Planets.VENUS: "venus",
            Planets.SATURN: "saturn barycenter",
            Planets.RAHU: "rahu",
            Planets.KETHU: "kethu",
        }

        return cast("AstronomicalCode", astronomical_codes.get(self, "empty"))

    @property
    def color(self) -> str:
        """Return the planet color code.

        Returns:
            str: the planet color code

        """
        planet_colors = {
            Planets.EMPTY: "#000000",  # Black
            Planets.ASCENDANT: "#FFFFFF",  # White
            Planets.SUN: "#FFD700",  # Gold
            Planets.MOON: "#C0C0C0",  # Silver
            Planets.MARS: "#FF0000",  # Red
            Planets.MERCURY: "#008000",  # Green
            Planets.JUPITER: "#FFFF00",  # Yellow
            Planets.VENUS: "#FF69B4",  # Pink
            Planets.SATURN: "#00008B",  # DarkBlue
            Planets.RAHU: "#8A2BE2",  # BlueViolet
            Planets.KETHU: "#8B0000",  # DarkRed
        }

        return planet_colors.get(self, "#000000")  # Default to Black
