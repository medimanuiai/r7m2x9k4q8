# Jyothishyam — Astrology Engine Specification

**Version:** 0.1 (Draft)
**Last Updated:** 2026-05-31
**Status:** 🟡 In Review
**Module:** `backend/astrology_engine.py` + `backend/chart_calculator.py`
**Language:** Python 3.11+
**Core Library:** pyswisseph (Swiss Ephemeris Python bindings)

---

## 1. Overview

The Astrology Engine is the core computation layer of Jyothishyam. It takes birth details as input and produces precise planetary positions, house cusps, nakshatra assignments, Dasha periods, and chart objects using the Swiss Ephemeris — the same engine used by professional astrology software worldwide.

This layer is **purely computational** — no database access, no AI calls. It returns structured data that is stored by the chart service and consumed by the AI engine.

Implementation note: a reference implementation exists at `systems/SuryaSiddhanta/ndastro_engine`. That implementation includes a JSON elevation fallback, optional SRTM lookup, and optional Skyfield-based ephemeris (`de440t.bsp`) for high-accuracy integration tests. See `systems/SuryaSiddhanta/Documentation/SuryaSiddhanta_System.md` and `tests/SuryaSiddhanta/Documentation/SuryaSiddhanta_Testing.md` for developer setup and test commands.

---

## 2. Module Structure

```
backend/
├── astrology_engine.py     ← Swiss Ephemeris wrapper (low-level calculations)
├── chart_calculator.py     ← High-level chart builder (Rasi, Navamsa, yogas)
└── constants/
    ├── planets.py          ← Planet definitions and Swiss Ephemeris IDs
    ├── signs.py            ← Zodiac sign definitions
    ├── nakshatras.py       ← 27 nakshatra definitions with lords and padas
    └── dashas.py           ← Vimshottari dasha sequence and periods
```

---

## 3. `astrology_engine.py`

### 3.1 Dependencies

```python
import swisseph as swe
from datetime import datetime, timezone
import math
```

### 3.2 Supported Ayanamsas

| Constant | Swiss Ephemeris ID | Description |
|---|---|---|
| `LAHIRI` | `swe.SIDM_LAHIRI` | Most used in India (default) |
| `RAMAN` | `swe.SIDM_RAMAN` | B.V. Raman system |
| `KP` | `swe.SIDM_KRISHNAMURTI` | KP system |
| `FAGAN_BRADLEY` | `swe.SIDM_FAGAN_BRADLEY` | Western sidereal |

---

### 3.3 Function: `get_planet_positions`

**Purpose:** Compute sidereal longitudes of all major planets for a given date/time/location.

**Signature:**
```python
def get_planet_positions(
    dt: datetime,          # UTC datetime (timezone-aware)
    lat: float,            # Latitude in decimal degrees
    lon: float,            # Longitude in decimal degrees
    ayanamsa: str = "LAHIRI"
) -> list[PlanetPosition]
```

**Planets Computed:**

| Planet | Sanskrit Name | Swiss Ephemeris Constant |
|---|---|---|
| Sun | Surya | `swe.SUN` |
| Moon | Chandra | `swe.MOON` |
| Mars | Mangal | `swe.MARS` |
| Mercury | Budha | `swe.MERCURY` |
| Jupiter | Guru | `swe.JUPITER` |
| Venus | Shukra | `swe.VENUS` |
| Saturn | Shani | `swe.SATURN` |
| Rahu | Rahu (North Node) | `swe.TRUE_NODE` |
| Ketu | Ketu (South Node) | `swe.TRUE_NODE + 180°` |

> **Note:** Uranus, Neptune, Pluto are computed but flagged as non-traditional for display purposes.

**Return Type — `PlanetPosition` (Pydantic model):**
```python
class PlanetPosition(BaseModel):
    name: str                  # "Sun"
    symbol: str                # "☉"
    longitude: float           # 0–360 degrees (sidereal)
    sign: str                  # "Capricorn"
    sign_number: int           # 1–12
    house: int                 # 1–12 (computed after houses are known)
    degree_in_sign: float      # 0–30
    nakshatra: str             # "Shravana"
    nakshatra_lord: str        # "Moon"
    nakshatra_number: int      # 1–27
    pada: int                  # 1–4
    is_retrograde: bool
    is_combust: bool
    dignity: str               # "exalted", "own_sign", "moolatrikona", "friendly", "neutral", "enemy", "debilitated"
    speed: float               # Daily motion in degrees
```

**Algorithm:**
1. Convert local datetime to Julian Day Number (JDN) using Swiss Ephemeris `swe.utc_to_jd()`.
2. Set ayanamsa: `swe.set_sid_mode(ayanamsa_id)`.
3. For each planet: call `swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL | swe.FLG_SPEED)`.
4. Extract longitude and speed from result tuple.
5. Determine sign: `int(longitude / 30) + 1`.
6. Determine nakshatra: `int(longitude / (360/27)) + 1`.
7. Determine pada: `int((longitude % (360/27)) / (360/108)) + 1`.
8. Determine dignity from sign + planet dignity table.
9. Determine retrograde: speed < 0.
10. Determine combustion: angular distance from Sun < combust threshold per planet.

---

### 3.4 Function: `get_houses`

**Purpose:** Compute house cusps (Bhavas) using a specified house system.

**Signature:**
```python
def get_houses(
    dt: datetime,
    lat: float,
    lon: float,
    ayanamsa: str = "LAHIRI",
    house_system: str = "WHOLE_SIGN"
) -> HouseData
```

**House Systems Supported:**

| Constant | Swiss Ephemeris Flag | Description |
|---|---|---|
| `WHOLE_SIGN` | `b"W"` | Default for Vedic — each sign = 1 house |
| `PLACIDUS` | `b"P"` | Western default |
| `EQUAL` | `b"E"` | Equal house system |
| `KOCH` | `b"K"` | Koch system |

**Return Type — `HouseData`:**
```python
class HouseData(BaseModel):
    ascendant: AscendantInfo
    midheaven: float          # MC longitude
    houses: list[HouseInfo]   # 12 houses
```

```python
class AscendantInfo(BaseModel):
    longitude: float
    sign: str
    sign_number: int
    degree_in_sign: float
    nakshatra: str
    nakshatra_lord: str
    pada: int

class HouseInfo(BaseModel):
    number: int               # 1–12
    sign: str
    sign_number: int
    degree_start: float       # Cusp longitude
```

**Algorithm (Whole Sign — default):**
1. Compute ascendant longitude using `swe.houses_ex()`.
2. Ascendant sign = `int(asc_longitude / 30) + 1`.
3. House 1 = ascendant sign. House N = (ascendant sign + N - 1) % 12.
4. Each house starts at `(house_sign - 1) * 30` degrees.

---

### 3.5 Function: `get_nakshatra`

**Purpose:** Get full nakshatra details for any planetary longitude.

**Signature:**
```python
def get_nakshatra(longitude: float) -> NakshatraInfo
```

**Return Type — `NakshatraInfo`:**
```python
class NakshatraInfo(BaseModel):
    number: int               # 1–27
    name: str                 # "Ashwini"
    lord: str                 # Dasha lord: "Ketu"
    deity: str                # "Ashwini Kumaras"
    symbol: str               # "Horse's head"
    guna: str                 # "Rajas/Tamas/Sattva"
    pada: int                 # 1–4
    pada_sign: str            # Navamsa sign for this pada
    longitude_start: float    # Start of nakshatra in degrees
    longitude_end: float      # End of nakshatra in degrees
```

**27 Nakshatras with Dasha Lords:**

| # | Nakshatra | Lord | Span (degrees) |
|---|---|---|---|
| 1 | Ashwini | Ketu | 0°00' – 13°20' Aries |
| 2 | Bharani | Venus | 13°20' – 26°40' Aries |
| 3 | Krittika | Sun | 26°40' Aries – 10°00' Taurus |
| 4 | Rohini | Moon | 10°00' – 23°20' Taurus |
| 5 | Mrigashira | Mars | 23°20' Taurus – 6°40' Gemini |
| 6 | Ardra | Rahu | 6°40' – 20°00' Gemini |
| 7 | Punarvasu | Jupiter | 20°00' Gemini – 3°20' Cancer |
| 8 | Pushya | Saturn | 3°20' – 16°40' Cancer |
| 9 | Ashlesha | Mercury | 16°40' – 30°00' Cancer |
| 10 | Magha | Ketu | 0°00' – 13°20' Leo |
| 11 | Purva Phalguni | Venus | 13°20' – 26°40' Leo |
| 12 | Uttara Phalguni | Sun | 26°40' Leo – 10°00' Virgo |
| 13 | Hasta | Moon | 10°00' – 23°20' Virgo |
| 14 | Chitra | Mars | 23°20' Virgo – 6°40' Libra |
| 15 | Swati | Rahu | 6°40' – 20°00' Libra |
| 16 | Vishakha | Jupiter | 20°00' Libra – 3°20' Scorpio |
| 17 | Anuradha | Saturn | 3°20' – 16°40' Scorpio |
| 18 | Jyeshtha | Mercury | 16°40' – 30°00' Scorpio |
| 19 | Mula | Ketu | 0°00' – 13°20' Sagittarius |
| 20 | Purva Ashadha | Venus | 13°20' – 26°40' Sagittarius |
| 21 | Uttara Ashadha | Sun | 26°40' Sagittarius – 10°00' Capricorn |
| 22 | Shravana | Moon | 10°00' – 23°20' Capricorn |
| 23 | Dhanishta | Mars | 23°20' Capricorn – 6°40' Aquarius |
| 24 | Shatabhisha | Rahu | 6°40' – 20°00' Aquarius |
| 25 | Purva Bhadrapada | Jupiter | 20°00' Aquarius – 3°20' Pisces |
| 26 | Uttara Bhadrapada | Saturn | 3°20' – 16°40' Pisces |
| 27 | Revati | Mercury | 16°40' – 30°00' Pisces |

---

### 3.6 Function: `get_dasha_periods`

**Purpose:** Compute the full Vimshottari Dasha sequence from the Moon's nakshatra at birth.

**Signature:**
```python
def get_dasha_periods(
    moon_longitude: float,
    birth_dt: datetime
) -> DashaData
```

**Vimshottari Dasha Sequence & Periods:**

| Planet | Period (Years) |
|---|---|
| Ketu | 7 |
| Venus | 20 |
| Sun | 6 |
| Moon | 10 |
| Mars | 7 |
| Rahu | 18 |
| Jupiter | 16 |
| Saturn | 19 |
| Mercury | 17 |

**Total cycle:** 120 years

**Algorithm:**
1. Find Moon's nakshatra and its dasha lord.
2. Compute balance of first dasha at birth using fraction of nakshatra traversed.
3. Sequence dashas in order starting from Moon's nakshatra lord.
4. For each Maha Dasha, compute 9 Antar Dashas (sub-periods) proportional to Maha Dasha length.
5. Optionally compute Pratyantar Dashas (sub-sub-periods).

**Return Type — `DashaData`:**
```python
class DashaData(BaseModel):
    current_maha_dasha: DashaPeriod
    current_antar_dasha: DashaPeriod
    current_pratyantar_dasha: DashaPeriod | None
    maha_dasha_sequence: list[MahaDasha]

class DashaPeriod(BaseModel):
    planet: str
    start_date: date
    end_date: date
    is_active: bool

class MahaDasha(BaseModel):
    planet: str
    start_date: date
    end_date: date
    duration_years: float
    antar_dashas: list[DashaPeriod]
```

---

## 4. `chart_calculator.py`

### 4.1 Function: `build_rasi_chart`

**Purpose:** Build the complete Rasi (D1) chart object.

**Signature:**
```python
def build_rasi_chart(
    dt: datetime,
    lat: float,
    lon: float,
    ayanamsa: str = "LAHIRI"
) -> RasiChart
```

**Process:**
1. Call `get_planet_positions()`.
2. Call `get_houses()` with Whole Sign system.
3. Assign each planet to a house based on its sign.
4. Compute planet dignities.
5. Identify aspects (Graha Drishti — planetary aspects).
6. Return complete `RasiChart` object.

---

### 4.2 Function: `build_navamsa_chart`

**Purpose:** Build the Navamsa (D9) chart — the 9th divisional chart.

**Navamsa Calculation:**
- Each sign is divided into 9 equal parts of 3°20' each.
- The Navamsa sign for each planet is determined by:
  1. Finding the pada of the planet's nakshatra.
  2. Mapping to the corresponding Navamsa sign per the Navamsa table.

**Signature:**
```python
def build_navamsa_chart(
    rasi_planets: list[PlanetPosition],
    rasi_ascendant: AscendantInfo
) -> NavamsaChart
```

---

### 4.3 Function: `compute_lagnam`

**Purpose:** Compute the Lagna (Ascendant) sign, nakshatra, and degree.

**Signature:**
```python
def compute_lagnam(
    dt: datetime,
    lat: float,
    lon: float,
    ayanamsa: str = "LAHIRI"
) -> AscendantInfo
```

---

### 4.4 Function: `compute_yogas`

**Purpose:** Identify classical Vedic yogas present in the chart.

**Signature:**
```python
def compute_yogas(
    planets: list[PlanetPosition],
    houses: HouseData
) -> list[Yoga]
```

**Return Type — `Yoga`:**
```python
class Yoga(BaseModel):
    name: str                 # "Gajakesari Yoga"
    category: str             # "Raja", "Dhana", "Nabhasa", "Chandra", "Surya"
    description: str          # Interpretation
    is_present: bool
    strength: str             # "strong", "moderate", "weak"
    participating_planets: list[str]
```

**Yogas to Detect (Phase 1 — priority list):**

| Yoga | Condition |
|---|---|
| Gajakesari | Moon and Jupiter in mutual kendras (1,4,7,10 from each other) |
| Budha-Aditya | Sun and Mercury in the same sign |
| Neecha Bhanga Raja | Debilitated planet + cancellation conditions met |
| Parivartana | Two planets in each other's signs |
| Mahabhagya | Sun/Moon/Lagna in specific odd/even sign combinations (by gender) |
| Kemadruma | No planets in 2nd or 12th from Moon |
| Hamsa (Panch Mahapurusha) | Jupiter in Kendra in own/exalted sign |
| Malavya (Panch Mahapurusha) | Venus in Kendra in own/exalted sign |
| Ruchaka (Panch Mahapurusha) | Mars in Kendra in own/exalted sign |
| Shasha (Panch Mahapurusha) | Saturn in Kendra in own/exalted sign |
| Bhadra (Panch Mahapurusha) | Mercury in Kendra in own/exalted sign |
| Viparita Raja | 6th/8th/12th lord in each other's house |

---

### 4.5 Function: `build_full_chart`

**Purpose:** Orchestrator — builds the complete chart object combining all computations.

**Signature:**
```python
def build_full_chart(
    birth_details: BirthDetails,
    ayanamsa: str = "LAHIRI"
) -> FullChartResult
```

**Input — `BirthDetails`:**
```python
class BirthDetails(BaseModel):
    dob: date
    tob: time
    lat: float
    lon: float
    timezone: str             # IANA timezone string
    ayanamsa: str = "LAHIRI"
```

**Output — `FullChartResult`:**
```python
class FullChartResult(BaseModel):
    ascendant: AscendantInfo
    planets: list[PlanetPosition]
    houses: list[HouseInfo]
    navamsa: NavamsaChart
    dashas: DashaData
    yogas: list[Yoga]
    computed_at: datetime
    engine_version: str
    ayanamsa_value: float     # Actual ayanamsa offset used
```

---

## 5. Planetary Dignity Table

| Planet | Exalted | Debilitated | Own Sign(s) | Moolatrikona |
|---|---|---|---|---|
| Sun | Aries (10°) | Libra (10°) | Leo | Leo (0–20°) |
| Moon | Taurus (3°) | Scorpio (3°) | Cancer | Taurus (4–30°) |
| Mars | Capricorn (28°) | Cancer (28°) | Aries, Scorpio | Aries (0–12°) |
| Mercury | Virgo (15°) | Pisces (15°) | Gemini, Virgo | Virgo (16–20°) |
| Jupiter | Cancer (5°) | Capricorn (5°) | Sagittarius, Pisces | Sagittarius (0–10°) |
| Venus | Pisces (27°) | Virgo (27°) | Taurus, Libra | Libra (0–15°) |
| Saturn | Libra (20°) | Aries (20°) | Capricorn, Aquarius | Aquarius (0–20°) |
| Rahu | — | — | Gemini, Virgo (varies by system) | — |
| Ketu | — | — | Sagittarius, Pisces (varies by system) | — |

---

## 6. Combustion Thresholds

| Planet | Combust within |
|---|---|
| Moon | 12° |
| Mars | 17° |
| Mercury (direct) | 14° |
| Mercury (retrograde) | 12° |
| Jupiter | 11° |
| Venus (direct) | 10° |
| Venus (retrograde) | 8° |
| Saturn | 15° |

---

## 7. Swiss Ephemeris Setup

- Ephemeris data files must be present at path configured in `EPHE_PATH` environment variable.
- Initialize at app startup: `swe.set_ephe_path(settings.EPHE_PATH)`
- Default path: `./ephe/` (bundled with backend Docker image)
- Files required: `seas_18.se1`, `semo_18.se1`, `sepl_18.se1` (covers 1800–2400 CE)

---

## 8. Precision & Edge Cases

| Scenario | Handling |
|---|---|
| Unknown birth time (`tob_unknown = True`) | Use noon (12:00) as approximate; flag all time-sensitive fields as approximate |
| Birth at exactly 0° of a sign | Valid; sign assignment uses `floor(lon / 30)` |
| Rahu/Ketu always retrograde | Set `is_retrograde = True` always |
| Planets at 0° (midnight) | Handle Julian Day correctly for midnight births |
| Birth before 1900 | Swiss Ephemeris supports from 5401 BCE; no special handling needed |
| Polar regions (lat > 66°) | House calculation may be undefined; warn user |

---

## 9. Open Decisions

| # | Decision | Options | Status |
|---|---|---|---|
| AE1 | Default house system | Whole Sign (current) / Placidus | 🟡 Pending |
| AE2 | Rahu/Ketu sign assignment | Gemini-Sag (common) / Virgo-Pisces (KP) | 🟡 Pending |
| AE3 | Pratyantar dasha in v1 | Yes / No | 🟡 Pending |
| AE4 | Additional divisional charts (D3, D7, D10) | Phase 1 / Phase 2 | 🟡 Pending |
| AE5 | Yoga detection depth | 12 yogas (current) / Expand | 🟡 Pending |
| AE6 | Ashtakavarga computation | Phase 1 / Phase 2 | 🟡 Pending |

---

*This document is a living specification. Sections marked 🟡 are pending decisions.*
