"""Build the Surya-shaped, Lahiri-sidereal chart used by the MVP web boundary.

The Surya core intentionally continues to return tropical positions.  This
adapter applies the repository's Lahiri ayanamsa before deriving all public
sign, degree, nakshatra, pada, and house-placement fields.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from pathlib import Path as _P
from typing import Any

_ROOT = _P(__file__).resolve().parents[3]
_SURYA = _ROOT / "systems" / "SuryaSiddhanta"
sys.path.insert(0, str(_SURYA))
sys.path.insert(0, str(_ROOT))

from ndastro_engine.ayanamsa import get_ayanamsa
from ndastro_engine.core import get_ascendent_position, get_planets_position
from ndastro_engine.enums import Planets
from ndastro_engine.nakshatra_enum import Nakshatras


RASI_NAMES = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

MVP_PLANETS = (
    Planets.SUN,
    Planets.MOON,
    Planets.MARS,
    Planets.MERCURY,
    Planets.JUPITER,
    Planets.VENUS,
    Planets.SATURN,
    Planets.RAHU,
    Planets.KETHU,
)


def normalize_longitude(longitude: float) -> float:
    return float(longitude) % 360.0


def to_lahiri_sidereal(tropical_longitude: float, ayanamsa_degrees: float) -> float:
    return normalize_longitude(float(tropical_longitude) - float(ayanamsa_degrees))


def longitude_to_rashi(longitude: float) -> str:
    return RASI_NAMES[int(normalize_longitude(longitude) // 30)]


def whole_sign_house(sidereal_longitude: float, ascendant_longitude: float) -> int:
    object_sign_index = int(normalize_longitude(sidereal_longitude) // 30)
    ascendant_sign_index = int(normalize_longitude(ascendant_longitude) // 30)
    return ((object_sign_index - ascendant_sign_index) % 12) + 1


def _nakshatra_record(sidereal_longitude: float) -> dict[str, Any]:
    longitude = normalize_longitude(sidereal_longitude)
    nakshatra = Nakshatras(int(longitude // (360.0 / 27.0)) + 1)
    return {
        "name": str(nakshatra),
        "pada": Nakshatras.current_pada(longitude),
        "index": nakshatra.value,
    }


def build_planet_record(
    name: str,
    sidereal_longitude: float,
    ascendant_longitude: float,
    *,
    retrograde: bool | None,
) -> dict[str, Any]:
    longitude = normalize_longitude(sidereal_longitude)
    record = {
        "name": name,
        "sign": longitude_to_rashi(longitude),
        "degree": round(longitude % 30.0, 4),
        "house": whole_sign_house(longitude, ascendant_longitude),
        "nakshatra": _nakshatra_record(longitude),
        "flags": {"combust": False, "exalted": False, "debilitated": False},
    }
    # The protected Pydantic model requires a motion object. An empty object is
    # the honest schema-compatible representation when node motion is unknown.
    record["motion"] = (
        {"retrograde": retrograde} if retrograde is not None else {}
    )
    return record


def build_lagna_record(sidereal_longitude: float) -> dict[str, Any]:
    longitude = normalize_longitude(sidereal_longitude)
    return {
        "sign": longitude_to_rashi(longitude),
        "degree": round(longitude % 30.0, 4),
        "house": 1,
        "nakshatra": _nakshatra_record(longitude),
    }


def generate_chart(
    lat: float,
    lon: float,
    dt: datetime,
    timezone_offset_minutes: int = 0,
    *,
    timezone_name: str = "UTC",
    place_label: str = "",
) -> dict[str, Any]:
    """Generate a deterministic Lahiri-sidereal chart from a UTC instant."""

    if dt.tzinfo is None:
        dt_utc = dt.replace(tzinfo=timezone.utc)
    else:
        dt_utc = dt.astimezone(timezone.utc)

    ayanamsa_degrees = float(get_ayanamsa(dt_utc, "lahiri"))
    tropical_ascendant = get_ascendent_position(lat, lon, dt_utc)
    sidereal_ascendant = to_lahiri_sidereal(tropical_ascendant, ayanamsa_degrees)

    # Request only real planetary objects. Planets.EMPTY is an enum sentinel,
    # and Ascendant is represented by the dedicated Lagna field below.
    tropical_positions = get_planets_position(list(MVP_PLANETS), lat, lon, dt_utc)
    planets = []
    for planet_enum, position in tropical_positions.items():
        if planet_enum not in MVP_PLANETS:
            continue
        try:
            planet_name = planet_enum.name.capitalize()
        except Exception:
            planet_name = str(planet_enum)
        sidereal_longitude = to_lahiri_sidereal(position.longitude, ayanamsa_degrees)
        # The Surya core currently reports zero node speed, so node motion is
        # unsupported rather than knowingly labelled direct.
        retrograde = None
        if planet_enum not in (Planets.RAHU, Planets.KETHU):
            retrograde = float(position.speed_longitude) < 0.0
        planets.append(
            build_planet_record(
                planet_name,
                sidereal_longitude,
                sidereal_ascendant,
                retrograde=retrograde,
            )
        )

    lagna = build_lagna_record(sidereal_ascendant)

    return {
        "metadata": {
            "birth_datetime_utc": dt_utc.isoformat(),
            "birth_location": {
                "latitude": float(lat),
                "longitude": float(lon),
                "timezone_offset_minutes": int(timezone_offset_minutes),
                "timezone": timezone_name,
                "place_label": place_label,
            },
            "ayanamsa": "lahiri",
            "ayanamsa_degrees": round(ayanamsa_degrees, 8),
            "house_system": "whole_sign",
            "house_numbering": "ascendant_relative",
            "sidereal": True,
            "longitude_source": "surya_tropical_converted_at_web_boundary",
        },
        "lagna": lagna,
        "planets": planets,
        "houses": [],
        "aspects": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lat", type=float, default=12.9716)
    parser.add_argument("--lon", type=float, default=77.5946)
    parser.add_argument("--dt", type=str, default="1990-01-01T12:00:00+00:00")
    parser.add_argument("--tz-offset", type=int, default=0)
    parser.add_argument("--timezone", type=str, default="UTC")
    parser.add_argument(
        "--out",
        type=str,
        default="systems/Parasara/fixtures/surya_generated_chart.json",
    )
    parser.add_argument("--run-snapshot", action="store_true")
    args = parser.parse_args()

    birth_utc = datetime.fromisoformat(args.dt)
    if birth_utc.tzinfo is None:
        birth_utc = birth_utc.replace(tzinfo=timezone.utc)
    chart = generate_chart(
        args.lat,
        args.lon,
        birth_utc,
        args.tz_offset,
        timezone_name=args.timezone,
    )
    out_path = Path(args.out)
    out_path.write_text(json.dumps(chart, indent=2), encoding="utf-8")
    print("Wrote Surya-compatible chart to", out_path)

    if args.run_snapshot:
        from systems.Parasara.tools.generate_snapshot import generate as generate_snapshot

        snapshot_out = "systems/Parasara/tests/snapshots/generated_surya_parasara_output.json"
        generate_snapshot(str(out_path), snapshot_out)
        print("Generated Parasara snapshot to", snapshot_out)


if __name__ == "__main__":
    main()
