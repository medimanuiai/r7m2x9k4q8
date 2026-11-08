"""SuryaAdapter: validate and load Surya Siddhanta JSON into Pydantic models."""
import json
import math
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

from systems.Parasara.engine.models import Chart
from systems.Parasara.engine.models import (
    StrictChart, StrictChartBatchItem, StrictChartBatchResult, StrictInputIssue,
)
from systems.Parasara.engine.identities import CANONICAL_PLANETS, SIGNS, SIGN_LORD, normalize_planet_id


class SuryaAdapter:
    # Resolve schema path relative to this source file so it works regardless of CWD
    try:
        # file: systems/Parasara/engine/adapter/surya_adapter.py -> parents[2] == systems/Parasara
        SCHEMA_PATH = Path(__file__).resolve().parents[2] / 'schemas' / 'surya_input.schema.json'
    except Exception:
        SCHEMA_PATH = Path('systems/Parasara/schemas/surya_input.schema.json')

    @classmethod
    def validate(cls, data: Any) -> None:
        s = json.load(cls.SCHEMA_PATH.open())
        errors = list(Draft7Validator(s).iter_errors(data))
        if errors:
            msgs = '\n'.join([f"{e.message} at {list(e.path)}" for e in errors])
            raise ValueError(f"Schema validation failed:\n{msgs}")

    @classmethod
    def load(cls, path: str) -> Chart:
        p = Path(path)
        data = json.load(p.open())
        cls.validate(data)
        # Pydantic V2: use model_validate
        chart = Chart.model_validate(data)
        return chart

    @classmethod
    def load_many(cls, path: str):
        p = Path(path)
        data = json.load(p.open())
        if isinstance(data, list):
            charts = []
            for item in data:
                if 'input' in item:
                    charts.append(Chart.model_validate(item['input']))
                elif 'metadata' in item:
                    obj = {
                        'metadata': item.get('metadata'),
                        'lagna': item.get('lagna'),
                        'planets': item.get('planets', []),
                        'houses': item.get('houses', [])
                    }
                    charts.append(Chart.model_validate(obj))
                else:
                    raise ValueError('Unexpected item format in load_many')
            return charts
        raise ValueError('Expected list of records for load_many')

    @classmethod
    def from_mapping_strict(cls, data: Mapping[str, Any]) -> StrictChart:
        """Explicit nine-body boundary; never dispatch through legacy loaders."""
        copied = _copy_json(data)
        if not isinstance(copied, dict):
            raise StrictInputError((StrictInputIssue("$", "chart_mapping_required"),))
        schema_path = Path(__file__).resolve().parents[2] / "schemas/surya_input_strict.schema.json"
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raise StrictInputError((StrictInputIssue("$", "strict_schema_unavailable"),)) from None
        issues = []
        for error in Draft7Validator(schema).iter_errors(copied):
            path = _safe_path(error.absolute_path)
            code = "schema_validation_failed"
            if error.validator == "required" and "sidereal_longitude" in error.validator_value and "sidereal_longitude" not in error.instance:
                code = "source_longitude_missing"
            if error.validator == "exclusiveMaximum" and tuple(error.absolute_path)[-1:] == ("degree",):
                code = "within_sign_degree_out_of_range"
            issues.append(StrictInputIssue(path, code))
        if issues:
            raise StrictInputError(tuple(issues))
        _validate_strict_semantics(copied)
        return StrictChart.model_validate(copied)

    @classmethod
    def load_strict(cls, path: str) -> StrictChart:
        return cls.from_mapping_strict(_read_strict_json(path))

    @classmethod
    def from_mappings_strict(cls, records: Sequence[Mapping[str, Any]]) -> StrictChartBatchResult:
        if not isinstance(records, (list, tuple)):
            raise StrictInputError((StrictInputIssue("$", "batch_sequence_required"),))
        result = []
        for index, record in enumerate(records):
            try:
                result.append(StrictChartBatchItem(index, cls.from_mapping_strict(record), ()))
            except StrictInputError as exc:
                result.append(StrictChartBatchItem(index, None, exc.issues))
        return StrictChartBatchResult(tuple(result))

    @classmethod
    def load_many_strict(cls, path: str) -> StrictChartBatchResult:
        return cls.from_mappings_strict(_read_strict_json(path))


class StrictInputError(ValueError):
    """Only safe codes/structural paths cross the strict construction boundary."""

    def __init__(self, issues: tuple[StrictInputIssue, ...]):
        self.issues = tuple(sorted(set(issues)))
        super().__init__("; ".join(f"{item.code} at {item.path}" for item in self.issues))


def _safe_path(parts) -> str:
    # Schema paths come only from declared fields; never expose arbitrary keys.
    allowed = {
        "metadata", "birth_datetime_utc", "birth_location", "latitude", "longitude",
        "timezone_offset_minutes", "ayanamsa", "sidereal", "house_system", "house_numbering",
        "lagna", "planets", "houses", "sidereal_longitude", "degree", "sign", "name",
        "nakshatra", "index", "pada", "house", "motion", "retrograde", "speed", "flags",
    }
    return "$" + "".join(f"[{part}]" if type(part) is int else "." + (part if part in allowed else "field") for part in parts)


def _copy_json(value, *, depth=0, active=None):
    if depth > 64:
        raise StrictInputError((StrictInputIssue("$", "input_depth_exceeded"),))
    if value is None or type(value) is bool:
        return value
    if type(value) in (str, int):
        # Use the governed serializer's scalar domain, including its active
        # integer conversion policy and UTF-8 encoding, before schema diagnostics
        # can render an unsafe value. Do not change process-wide limits.
        try:
            json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
        except (UnicodeError, ValueError):
            raise StrictInputError((StrictInputIssue("$", "unsafe_canonical_scalar"),)) from None
        return value
    if type(value) is float:
        if math.isfinite(value):
            return 0.0 if value == 0.0 else value
        raise StrictInputError((StrictInputIssue("$", "non_finite_number"),))
    if not isinstance(value, (Mapping, list)):
        raise StrictInputError((StrictInputIssue("$", "non_json_value"),))
    active = set() if active is None else active
    if id(value) in active:
        raise StrictInputError((StrictInputIssue("$", "cyclic_input"),))
    active.add(id(value))
    try:
        if isinstance(value, Mapping):
            if any(type(key) is not str for key in value):
                raise StrictInputError((StrictInputIssue("$", "non_string_key"),))
            for key in value:
                _copy_json(key)
            return {key: _copy_json(item, depth=depth + 1, active=active) for key, item in value.items()}
        return [_copy_json(item, depth=depth + 1, active=active) for item in value]
    finally:
        active.remove(id(value))


def _read_strict_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_key")
            result[key] = value
        return result

    try:
        with Path(path).open("rb") as stream:
            payload = stream.read(8 * 1024 * 1024 + 1)
        if len(payload) > 8 * 1024 * 1024:
            raise StrictInputError((StrictInputIssue("$", "document_too_large"),))
        return json.loads(payload.decode("utf-8"), object_pairs_hook=pairs)
    except StrictInputError:
        raise
    except OSError:
        raise StrictInputError((StrictInputIssue("$", "input_unreadable"),)) from None
    except (UnicodeError, ValueError, RecursionError):
        raise StrictInputError((StrictInputIssue("$", "invalid_json"),)) from None


def _validate_strict_semantics(data):
    from systems.Parasara.tools.surya_to_parasara import _nakshatra_record

    issues = []

    def issue(path, code):
        issues.append(StrictInputIssue(path, code))

    metadata = data["metadata"]
    try:
        instant = datetime.fromisoformat(metadata["birth_datetime_utc"].replace("Z", "+00:00"))
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError("offset_missing")
        metadata["birth_datetime_utc"] = instant.astimezone(timezone.utc).isoformat()
    except (ValueError, OverflowError):
        issue("$.metadata.birth_datetime_utc", "offset_datetime_required")
    if type(metadata["birth_location"]["timezone_offset_minutes"]) is not int:
        issue("$.metadata.birth_location.timezone_offset_minutes", "integer_required")
    lagna_index = SIGNS.index(data["lagna"]["sign"])

    def position(row, path, *, lagna=False):
        permitted = {"sign", "degree", "sidereal_longitude", "house", "nakshatra"}
        if not lagna:
            permitted |= {"name", "motion", "flags"}
        if set(row) - permitted:
            issue(path, "unknown_position_field")
        longitude = row["sidereal_longitude"]
        sign_index = int(longitude // 30.0)
        if row["sign"] != SIGNS[sign_index] or row["degree"] != longitude - 30.0 * sign_index:
            issue(path, "derived_position_mismatch")
        if "house" in row:
            expected_house = 1 if lagna else ((sign_index - lagna_index) % 12) + 1
            if type(row["house"]) is not int or row["house"] != expected_house:
                issue(path + ".house", "house_placement_mismatch")
        if "nakshatra" in row:
            supplied = row["nakshatra"]
            expected = _nakshatra_record(longitude)
            if (type(supplied["index"]) is not int or type(supplied["pada"]) is not int
                or supplied["index"] != expected["index"] or supplied["pada"] != expected["pada"]
                or supplied["name"].strip().casefold() != expected["name"].casefold()):
                issue(path + ".nakshatra", "nakshatra_mismatch")
            else:
                row["nakshatra"] = expected

    position(data["lagna"], "$.lagna", lagna=True)
    names = []
    for index, row in enumerate(data["planets"]):
        path = f"$.planets[{index}]"
        try:
            row["name"] = normalize_planet_id(row["name"])
            names.append(row["name"])
        except ValueError:
            issue(path + ".name", "unknown_planet")
        position(row, path)
        motion = row["motion"]
        if row["name"] not in ("Rahu", "Ketu") and "retrograde" not in motion:
            issue(path + ".motion", "retrograde_required")
        if "speed" in motion and "retrograde" in motion and motion["retrograde"] != (motion["speed"] < 0):
            issue(path + ".motion", "motion_mismatch")
        flags = row.get("flags", {})
        for key in ("combust", "exalted", "debilitated"):
            if key in flags and type(flags[key]) is not bool:
                issue(path + ".flags", "boolean_flag_required")
        if flags.get("exalted") is True and flags.get("debilitated") is True:
            issue(path + ".flags", "contradictory_dignity_flags")
    if len(set(names)) != len(names):
        issue("$.planets", "duplicate_planet")
    if set(names) != set(CANONICAL_PLANETS):
        issue("$.planets", "required_planets_missing")
    houses = data["houses"]
    if houses:
        numbers = [row.get("number") for row in houses]
        if len(houses) != 12 or any(type(number) is not int for number in numbers) or set(numbers) != set(range(1, 13)):
            issue("$.houses", "complete_houses_required")
        else:
            for index, row in enumerate(houses):
                number = row["number"]
                sign = SIGNS[(lagna_index + number - 1) % 12]
                path = f"$.houses[{index}]"
                if row.get("sign") != sign:
                    issue(path, "house_sign_mismatch")
                if "lord" in row:
                    try:
                        if normalize_planet_id(row["lord"]) != SIGN_LORD[sign]:
                            issue(path, "house_lord_mismatch")
                    except ValueError:
                        issue(path, "house_lord_mismatch")
                if "occupants" in row:
                    try:
                        actual = [normalize_planet_id(value) for value in row["occupants"]]
                        expected = [planet["name"] for planet in data["planets"] if planet["house"] == number]
                        if len(actual) != len(set(actual)) or set(actual) != set(expected):
                            issue(path, "house_occupants_mismatch")
                    except (TypeError, ValueError):
                        issue(path, "house_occupants_mismatch")
    if issues:
        raise StrictInputError(tuple(issues))
    data["planets"].sort(key=lambda row: CANONICAL_PLANETS.index(row["name"]))
    data["houses"].sort(key=lambda row: row["number"])
