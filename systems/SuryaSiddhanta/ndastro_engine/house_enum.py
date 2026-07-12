"""Module is to hold enums."""

from enum import IntEnum
from typing import Literal, TypeAlias, cast

from ndastro_engine.planet_enum import Planets

HouseCode: TypeAlias = Literal["H01", "H02", "H03", "H04", "H05", "H06", "H07", "H08", "H09", "H10", "H11", "H12"]


class Houses(IntEnum):
    """Enum to hold houses."""

    HOUSE1 = 1
    HOUSE2 = 2
    HOUSE3 = 3
    HOUSE4 = 4
    HOUSE5 = 5
    HOUSE6 = 6
    HOUSE7 = 7
    HOUSE8 = 8
    HOUSE9 = 9
    HOUSE10 = 10
    HOUSE11 = 11
    HOUSE12 = 12

    def __str__(self) -> str:
        """Return name of the house.

        Returns:
            str: name of the house

        """
        return self.name

    @property
    def owner(self) -> Planets:
        """Get the owner of a given house.

        Returns:
            Planets: The owner of the house.

        """
        house_to_planet = {
            1: Planets.MARS,
            2: Planets.VENUS,
            3: Planets.MERCURY,
            4: Planets.MOON,
            5: Planets.SUN,
            6: Planets.MERCURY,
            7: Planets.VENUS,
            8: Planets.MARS,
            9: Planets.JUPITER,
            10: Planets.SATURN,
            11: Planets.SATURN,
            12: Planets.JUPITER,
        }
        return house_to_planet[self.value]

    @property
    def code(self) -> HouseCode:
        """Get the astronomical code for a given house.

        Returns:
            HouseCode: The astronomical code for the house.

        """
        house_codes = {
            1: "H01",
            2: "H02",
            3: "H03",
            4: "H04",
            5: "H05",
            6: "H06",
            7: "H07",
            8: "H08",
            9: "H09",
            10: "H10",
            11: "H11",
            12: "H12",
        }
        return cast("HouseCode", house_codes[self.value])

    @staticmethod
    def from_code(code: HouseCode) -> "Houses":
        """Convert house code to house enum.

        Args:
            code (HouseCode): the house code

        Returns:
            Houses: the corresponding house enum

        """
        house_codes = {
            "H01": Houses.HOUSE1,
            "H02": Houses.HOUSE2,
            "H03": Houses.HOUSE3,
            "H04": Houses.HOUSE4,
            "H05": Houses.HOUSE5,
            "H06": Houses.HOUSE6,
            "H07": Houses.HOUSE7,
            "H08": Houses.HOUSE8,
            "H09": Houses.HOUSE9,
            "H10": Houses.HOUSE10,
            "H11": Houses.HOUSE11,
            "H12": Houses.HOUSE12,
        }
        return house_codes.get(code, Houses.HOUSE1)
