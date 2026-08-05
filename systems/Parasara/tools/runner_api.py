"""Bounded JSON bridge for the account-free Birth -> Career MVP."""
from __future__ import annotations

import json
import math
import re
import sys
import tempfile
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


MAX_REQUEST_BYTES = 8_192
MAX_PLACE_LENGTH = 120
MAX_TIMEZONE_LENGTH = 64
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")

SAFE_MESSAGES = {
    "invalid_request": "The request could not be read.",
    "invalid_date": "Enter a valid birth date in YYYY-MM-DD format.",
    "invalid_time": "Enter a valid local birth time in HH:MM format.",
    "invalid_coordinates": "Latitude must be -90 to 90 and longitude -180 to 180.",
    "invalid_timezone": "Enter a valid IANA time zone, such as Asia/Kolkata.",
    "ambiguous_local_time": "That local time is ambiguous in the selected time zone. Choose another exact time.",
    "nonexistent_local_time": "That local time does not exist in the selected time zone.",
    "consent_required": "Confirm consent before generating the reading.",
    "invalid_place": "Keep the display place label to 120 characters or fewer.",
    "request_too_large": "The request is too large.",
    "generation_failed": "The reading could not be generated. Please try again.",
}


class MVPInputError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class ValidatedBirth:
    dob: str
    local_time: str
    latitude: float
    longitude: float
    timezone_name: str
    place_label: str
    local_datetime: datetime
    utc_datetime: datetime
    timezone_offset_minutes: int


def safe_error(code: str) -> dict[str, Any]:
    safe_code = code if code in SAFE_MESSAGES else "generation_failed"
    return {"error": {"code": safe_code, "message": SAFE_MESSAGES[safe_code]}}


def display_location(place_label: str, latitude: float, longitude: float) -> str:
    """Return an honest presentation label without changing stored inputs."""

    trimmed_label = place_label.strip()
    if trimmed_label:
        return trimmed_label
    return f"{float(latitude):.6f}, {float(longitude):.6f}"


def _number(value: Any) -> float:
    if isinstance(value, bool):
        raise MVPInputError("invalid_coordinates")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise MVPInputError("invalid_coordinates") from None
    if not math.isfinite(number):
        raise MVPInputError("invalid_coordinates")
    return number


def local_birth_to_utc(dob: str, local_time: str, timezone_name: str) -> tuple[datetime, datetime, int]:
    if (
        not isinstance(dob, str)
        or len(dob) != 10
        or not DATE_PATTERN.fullmatch(dob)
    ):
        raise MVPInputError("invalid_date")
    try:
        parsed_date = date.fromisoformat(dob)
    except ValueError:
        raise MVPInputError("invalid_date") from None

    if (
        not isinstance(local_time, str)
        or len(local_time) != 5
        or not TIME_PATTERN.fullmatch(local_time)
    ):
        raise MVPInputError("invalid_time")
    parsed_time = time.fromisoformat(local_time)

    if (
        not isinstance(timezone_name, str)
        or not timezone_name
        or len(timezone_name) > MAX_TIMEZONE_LENGTH
    ):
        raise MVPInputError("invalid_timezone")
    naive = datetime.combine(parsed_date, parsed_time)
    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError):
        # Windows Python installations do not include an IANA database by
        # default. The existing project environments already provide pytz,
        # whose bundled database preserves IANA validation and DST behavior.
        try:
            import pytz

            pytz_zone = pytz.timezone(timezone_name)
            try:
                local_datetime = pytz_zone.localize(naive, is_dst=None)
            except pytz.AmbiguousTimeError:
                raise MVPInputError("ambiguous_local_time") from None
            except pytz.NonExistentTimeError:
                raise MVPInputError("nonexistent_local_time") from None
        except MVPInputError:
            raise
        except Exception:
            raise MVPInputError("invalid_timezone") from None
    else:
        local_fold_zero = naive.replace(tzinfo=zone, fold=0)
        local_fold_one = naive.replace(tzinfo=zone, fold=1)
        utc_fold_zero = local_fold_zero.astimezone(timezone.utc)
        utc_fold_one = local_fold_one.astimezone(timezone.utc)
        fold_zero_valid = (
            utc_fold_zero.astimezone(zone).replace(tzinfo=None) == naive
        )
        fold_one_valid = (
            utc_fold_one.astimezone(zone).replace(tzinfo=None) == naive
        )
        if not fold_zero_valid and not fold_one_valid:
            raise MVPInputError("nonexistent_local_time")
        if (
            fold_zero_valid
            and fold_one_valid
            and local_fold_zero.utcoffset() != local_fold_one.utcoffset()
        ):
            raise MVPInputError("ambiguous_local_time")
        local_datetime = local_fold_zero if fold_zero_valid else local_fold_one

    utc_datetime = local_datetime.astimezone(timezone.utc)
    offset = local_datetime.utcoffset()
    offset_minutes = int(offset.total_seconds() // 60) if offset is not None else 0
    return local_datetime, utc_datetime, offset_minutes


def validate_birth_request(data: Any) -> ValidatedBirth:
    if not isinstance(data, dict):
        raise MVPInputError("invalid_request")

    latitude = _number(data.get("lat"))
    longitude = _number(data.get("lon"))
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise MVPInputError("invalid_coordinates")

    if data.get("consent") is not True:
        raise MVPInputError("consent_required")

    place = data.get("place", "")
    if not isinstance(place, str) or len(place) > MAX_PLACE_LENGTH:
        raise MVPInputError("invalid_place")
    place = place.strip()

    local_datetime, utc_datetime, offset_minutes = local_birth_to_utc(
        data.get("dob"),
        data.get("time"),
        data.get("tz"),
    )
    return ValidatedBirth(
        dob=data["dob"],
        local_time=data["time"],
        latitude=latitude,
        longitude=longitude,
        timezone_name=data["tz"],
        place_label=place,
        local_datetime=local_datetime,
        utc_datetime=utc_datetime,
        timezone_offset_minutes=offset_minutes,
    )


def _legacy_engine_chart(public_chart: dict[str, Any]) -> dict[str, Any]:
    """Adapt corrected public houses to the protected normalizer input contract.

    The existing normalizer expects ``planet.house`` to be the Aries-based sign
    ordinal and converts it to Lagna-relative whole-sign houses. MVP-01 exports
    corrected houses, while this private copy preserves the locked Career path.
    """

    engine_chart = deepcopy(public_chart)
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]
    for planet in engine_chart.get("planets", []):
        sign = planet.get("sign")
        if sign in signs:
            planet["house"] = signs.index(sign) + 1
    engine_chart.setdefault("metadata", {})["house_numbering"] = (
        "aries_sign_index_for_protected_normalizer"
    )
    return engine_chart


def generate_response(birth: ValidatedBirth) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[3]
    repo_root_text = str(repo_root)
    if repo_root_text not in sys.path:
        sys.path.insert(0, repo_root_text)

    from systems.Parasara.tools.generate_snapshot import generate as generate_snapshot
    from systems.Parasara.tools.surya_to_parasara import generate_chart

    chart = generate_chart(
        birth.latitude,
        birth.longitude,
        birth.utc_datetime,
        birth.timezone_offset_minutes,
        timezone_name=birth.timezone_name,
        place_label=birth.place_label,
    )

    chart_fd, chart_name = tempfile.mkstemp(prefix="mvp_chart_", suffix=".json")
    output_fd, output_name = tempfile.mkstemp(prefix="mvp_career_", suffix=".json")
    chart_path = Path(chart_name)
    output_path = Path(output_name)
    try:
        # Close descriptors immediately; Path handles bounded local temporary files.
        import os

        os.close(chart_fd)
        os.close(output_fd)
        engine_chart = _legacy_engine_chart(chart)
        chart_path.write_text(json.dumps(engine_chart), encoding="utf-8")
        snapshot = generate_snapshot(str(chart_path), str(output_path))
        career = snapshot.get("domains", {}).get("career", {})
        public_indicators = [
            {
                "rule_id": indicator.get("rule_id"),
                "contribution": indicator.get("contribution"),
                "evidence": indicator.get("evidence", {}),
            }
            for indicator in career.get("indicators", [])
            if isinstance(indicator, dict)
        ]
        public_evidence = [
            {
                "rule_id": evidence.get("rule_id"),
                "match": bool(evidence.get("match")),
                "evidence": evidence.get("evidence", {}),
                "contribution": evidence.get("contribution"),
            }
            for evidence in career.get("evidence", [])
            if isinstance(evidence, dict)
        ]
        public_snapshot = {
            "engine": snapshot.get("engine", {}),
            "meta": snapshot.get("meta", {}),
            "domains": {
                "career": {
                    "summary": career.get("summary", ""),
                    "score": career.get("score"),
                    "confidence": career.get("confidence"),
                    "components": career.get("components", []),
                    "indicators": public_indicators,
                    "evidence": public_evidence,
                    "scoring": career.get("scoring", {}),
                }
            },
        }
        return {
            "snapshot": public_snapshot,
            "surya_chart": chart,
            "birth": {
                "place": birth.place_label,
                "display_location": display_location(
                    birth.place_label,
                    birth.latitude,
                    birth.longitude,
                ),
                "timezone": birth.timezone_name,
                "local_datetime": birth.local_datetime.isoformat(),
                "utc_datetime": birth.utc_datetime.isoformat(),
            },
        }
    finally:
        chart_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


def run_request(data: Any) -> dict[str, Any]:
    try:
        return generate_response(validate_birth_request(data))
    except MVPInputError as error:
        return safe_error(error.code)
    except Exception:
        return safe_error("generation_failed")


def main() -> None:
    try:
        raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
        if len(raw) > MAX_REQUEST_BYTES:
            response = safe_error("request_too_large")
        else:
            try:
                data = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                data = None
            response = run_request(data)
    except Exception:
        response = safe_error("generation_failed")
    sys.stdout.write(json.dumps(response, separators=(",", ":")))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
