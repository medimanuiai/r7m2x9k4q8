"""Module to hold Rasi enums."""

from __future__ import annotations

from enum import IntEnum
from typing import Literal, TypeAlias, cast

from ndastro_engine.planet_enum import Planets

RasiCode: TypeAlias = Literal["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12"]


class Rasis(IntEnum):
    """Enum to represent Rasis."""

    ARIES = 1
    TAURUS = 2
    GEMINI = 3
    CANCER = 4
    LEO = 5
    VIRGO = 6
    LIBRA = 7
    SCORPIO = 8
    SAGITTARIUS = 9
    CAPRICORN = 10
    AQUARIUS = 11
    PISCES = 12

    def __str__(self) -> str:
        """Return a localized string representation of the Rasi.

        Returns:
            str: Localized name of the Rasi.

        """
        return self.name

    @property
    def owner(self) -> Planets | None:
        """Get the owner planet of a given Rasi.

        Args:
            rasi (int): The Rasi number.

        Returns:
            Planets | None: The owner planet of the Rasi or None if invalid Rasi.

        """
        rasi_to_planet = {
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
        return rasi_to_planet[self.value]

    @property
    def code(self) -> RasiCode:
        """Get the astronomical code for a given Rasi.

        Returns:
            RasiCode: The astronomical code for the Rasi.

        """
        rasi_to_code = {
            Rasis.ARIES: "R01",
            Rasis.TAURUS: "R02",
            Rasis.GEMINI: "R03",
            Rasis.CANCER: "R04",
            Rasis.LEO: "R05",
            Rasis.VIRGO: "R06",
            Rasis.LIBRA: "R07",
            Rasis.SCORPIO: "R08",
            Rasis.SAGITTARIUS: "R09",
            Rasis.CAPRICORN: "R10",
            Rasis.AQUARIUS: "R11",
            Rasis.PISCES: "R12",
        }
        return cast("RasiCode", rasi_to_code[self])

    @staticmethod
    def from_code(code: RasiCode) -> Rasis | None:
        """Convert a Rasi code to its corresponding enum member.

        Args:
            code (RasiCode): The Rasi code.

        Returns:
            Rasis | None: The corresponding enum member or None if invalid code.

        """
        code_to_rasi = {
            "R01": Rasis.ARIES,
            "R02": Rasis.TAURUS,
            "R03": Rasis.GEMINI,
            "R04": Rasis.CANCER,
            "R05": Rasis.LEO,
            "R06": Rasis.VIRGO,
            "R07": Rasis.LIBRA,
            "R08": Rasis.SCORPIO,
            "R09": Rasis.SAGITTARIUS,
            "R10": Rasis.CAPRICORN,
            "R11": Rasis.AQUARIUS,
            "R12": Rasis.PISCES,
        }
        return code_to_rasi.get(code)

    @classmethod
    def from_string(cls, rasi: str) -> Rasis | None:
        """Convert a Rasi name to its corresponding enum member.

        Args:
            rasi (str): The name of the Rasi.

        Returns:
            Rasis | None: The corresponding enum member or None if invalid name.

        """
        try:
            return cls[rasi.upper()]
        except KeyError:
            return None

    @classmethod
    def to_string(cls) -> str:
        """Convert a Rasi enum member to its localized display name.

        Returns:
            str: Localized name of the Rasi.

        """
        return cls.name.name

    @staticmethod
    def to_list() -> list[str]:
        """Get a list of all Rasi names.

        Returns:
            list[str]: List of all Rasi names.

        """
        return [el.name for el in Rasis]

    @staticmethod
    def to_4x4list() -> list[list[str]]:
        """Get a 4x4 grid representation of Rasi names.

        Returns:
            list[list[str]]: 4x4 grid of Rasi names.

        """
        rasis = Rasis.to_list()

        return [
            [rasis[11], rasis[0], rasis[1], rasis[2]],
            [rasis[10], "", "", rasis[3]],
            [rasis[9], "", "", rasis[4]],
            [rasis[8], rasis[7], rasis[6], rasis[5]],
        ]


__all__ = ["RasiCode", "Rasis"]
