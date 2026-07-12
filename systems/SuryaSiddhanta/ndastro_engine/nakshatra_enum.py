"""Module is to hold start enums."""

from enum import Enum
from typing import Literal, TypeAlias, cast

from ndastro_engine.constants import DEGREE_MAX, DEGREE_PER_NAKSHATRA
from ndastro_engine.planet_enum import AstronomicalCode, Planets

NakshatraCode: TypeAlias = Literal[
    "N01",
    "N02",
    "N03",
    "N04",
    "N05",
    "N06",
    "N07",
    "N08",
    "N09",
    "N10",
    "N11",
    "N12",
    "N13",
    "N14",
    "N15",
    "N16",
    "N17",
    "N18",
    "N19",
    "N20",
    "N21",
    "N22",
    "N23",
    "N24",
    "N25",
    "N26",
    "N27",
]


class Nakshatras(Enum):
    """Enum to hold stars."""

    ASWINNI = 1
    BHARANI = 2
    KAARTHIKAI = 3
    ROGHINI = 4
    MIRUGASIRISAM = 5
    THIRUVAATHIRAI = 6
    PUNARPOOSAM = 7
    POOSAM = 8
    AAYILYAM = 9
    MAGAM = 10
    POORAM = 11
    UTHTHIRAM = 12
    ASTHTHAM = 13
    CHITHTHIRAI = 14
    SUVAATHI = 15
    VISAAGAM = 16
    ANUSHAM = 17
    KETTAI = 18
    MOOLAM = 19
    POORAADAM = 20
    UTHTHIRAADAM = 21
    THIRUVONAM = 22
    AVITTAM = 23
    SHATHAYAM = 24
    POORATTAATHI = 25
    UTHTHIRATTAATHI = 26
    REVATHI = 27

    def __str__(self) -> str:
        """Return the display name of the star.

        Returns:
            str: The display name of the star.

        """
        return self.name

    @property
    def owner(self) -> Planets:
        """Return the owner (planet) of the star.

        Returns:
            str: The name of the planet that owns the star.

        """
        owners = {
            1: "kethu",
            2: "venus",
            3: "sun",
            4: "moon",
            5: "mars barycenter",
            6: "rahu",
            7: "jupiter barycenter",
            8: "saturn barycenter",
            9: "mercury",
            10: "kethu",
            11: "venus",
            12: "sun",
            13: "moon",
            14: "mars barycenter",
            15: "rahu",
            16: "jupiter barycenter",
            17: "saturn barycenter",
            18: "mercury",
            19: "kethu",
            20: "venus",
            21: "sun",
            22: "moon",
            23: "mars barycenter",
            24: "rahu",
            25: "jupiter barycenter",
            26: "saturn barycenter",
            27: "mercury",
        }

        return Planets.from_astronomical_code(cast("AstronomicalCode", owners[self.value]))

    @property
    def code(self) -> NakshatraCode:
        """Return the astronomical code of the star.

        Returns:
            NakshatraCode: The astronomical code of the star.

        """
        nakshatra_codes = {
            Nakshatras.ASWINNI: "N01",
            Nakshatras.BHARANI: "N02",
            Nakshatras.KAARTHIKAI: "N03",
            Nakshatras.ROGHINI: "N04",
            Nakshatras.MIRUGASIRISAM: "N05",
            Nakshatras.THIRUVAATHIRAI: "N06",
            Nakshatras.PUNARPOOSAM: "N07",
            Nakshatras.POOSAM: "N08",
            Nakshatras.AAYILYAM: "N09",
            Nakshatras.MAGAM: "N10",
            Nakshatras.POORAM: "N11",
            Nakshatras.UTHTHIRAM: "N12",
            Nakshatras.ASTHTHAM: "N13",
            Nakshatras.CHITHTHIRAI: "N14",
            Nakshatras.SUVAATHI: "N15",
            Nakshatras.VISAAGAM: "N16",
            Nakshatras.ANUSHAM: "N17",
            Nakshatras.KETTAI: "N18",
            Nakshatras.MOOLAM: "N19",
            Nakshatras.POORAADAM: "N20",
            Nakshatras.UTHTHIRAADAM: "N21",
            Nakshatras.THIRUVONAM: "N22",
            Nakshatras.AVITTAM: "N23",
            Nakshatras.SHATHAYAM: "N24",
            Nakshatras.POORATTAATHI: "N25",
            Nakshatras.UTHTHIRATTAATHI: "N26",
            Nakshatras.REVATHI: "N27",
        }

        return cast("NakshatraCode", nakshatra_codes[self])

    @property
    def start_degree(self) -> float:
        """Return the starting degree of the star.

        Returns:
            float: The starting degree of the star.

        """
        return (self.value - 1) * DEGREE_PER_NAKSHATRA

    @property
    def end_degree(self) -> float:
        """Return the ending degree of the star.

        Returns:
            float: The ending degree of the star.

        """
        return self.value * DEGREE_PER_NAKSHATRA

    @staticmethod
    def planet_advancement(planet_longitude: float) -> float:
        """Calculate the advancement of a planet in its current star.

        Args:
            planet_longitude (float): The longitude of the planet.

        Returns:
            float: The advancement of the planet in its current star, expressed as decimal degrees.

        """
        nakshatra_number = int(planet_longitude // DEGREE_PER_NAKSHATRA) + 1
        nakshatra = Nakshatras(nakshatra_number)

        return planet_longitude - nakshatra.start_degree

    @staticmethod
    def degrees_until_star_end(planet_longitude: float) -> float:
        """Calculate the remaining degrees for a planet to complete its current star.

        Args:
            planet_longitude (float): The longitude of the planet.

        Returns:
            float: The remaining degrees converted to fractions of the nakshatra for the planet to complete its current star.

        """
        # fractions of nakshatra yet to be completed
        nakshatra_number = int(planet_longitude // DEGREE_PER_NAKSHATRA) + 1
        nakshatra = Nakshatras(nakshatra_number)

        # result should be in fractions 0 to 1, so divide by degree per nakshatra
        return (nakshatra.end_degree - planet_longitude) / DEGREE_PER_NAKSHATRA

    @staticmethod
    def current_pada(planet_longitude: float) -> int:
        """Calculate the current pada (1-4) within the planet's current Nakshatra.

        Args:
            planet_longitude (float): The longitude of the planet.

        Returns:
            int: The current pada number from 1 to 4.

        """
        normalized_longitude = planet_longitude % DEGREE_MAX
        advancement = Nakshatras.planet_advancement(normalized_longitude)

        # Use fraction of nakshatra to avoid floating boundary issues.
        pada = int((advancement / DEGREE_PER_NAKSHATRA) * 4) + 1
        return min(pada, 4)

    @staticmethod
    def from_code(code: NakshatraCode) -> "Nakshatras":
        """Convert a Nakshatra code to its corresponding enum member.

        Args:
            code (NakshatraCode): The Nakshatra code.

        Returns:
            Nakshatras: The corresponding enum member.

        """
        code_to_nakshatra = {
            "N01": Nakshatras.ASWINNI,
            "N02": Nakshatras.BHARANI,
            "N03": Nakshatras.KAARTHIKAI,
            "N04": Nakshatras.ROGHINI,
            "N05": Nakshatras.MIRUGASIRISAM,
            "N06": Nakshatras.THIRUVAATHIRAI,
            "N07": Nakshatras.PUNARPOOSAM,
            "N08": Nakshatras.POOSAM,
            "N09": Nakshatras.AAYILYAM,
            "N10": Nakshatras.MAGAM,
            "N11": Nakshatras.POORAM,
            "N12": Nakshatras.UTHTHIRAM,
            "N13": Nakshatras.ASTHTHAM,
            "N14": Nakshatras.CHITHTHIRAI,
            "N15": Nakshatras.SUVAATHI,
            "N16": Nakshatras.VISAAGAM,
            "N17": Nakshatras.ANUSHAM,
            "N18": Nakshatras.KETTAI,
            "N19": Nakshatras.MOOLAM,
            "N20": Nakshatras.POORAADAM,
            "N21": Nakshatras.UTHTHIRAADAM,
            "N22": Nakshatras.THIRUVONAM,
            "N23": Nakshatras.AVITTAM,
            "N24": Nakshatras.SHATHAYAM,
            "N25": Nakshatras.POORATTAATHI,
            "N26": Nakshatras.UTHTHIRATTAATHI,
            "N27": Nakshatras.REVATHI,
        }

        return code_to_nakshatra[code]

    @staticmethod
    def to_string(num: int) -> str:
        """Convert star number to display name of the star.

        Args:
            num (int): the star number

        Returns:
            str: return the star name

        """
        return Nakshatras(num).name

    @staticmethod
    def to_list() -> list[str]:
        """Convert enum to list of enum item name.

        Returns:
            list[str]: list of enum item name

        """
        return [el.name for el in Nakshatras]
