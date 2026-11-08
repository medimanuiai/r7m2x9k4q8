"""Factual precision and unchanged explicitly selected legacy serialization."""
import json
import math

import pytest

from systems.Parasara.tools import surya_to_parasara as producer


@pytest.mark.parametrize("boundary", [30.0 * index for index in range(1, 13)])
def test_both_sides_and_exact_sign_transition(boundary):
    for value in (math.nextafter(boundary, 0.0), boundary, math.nextafter(boundary, math.inf)):
        record = producer.build_planet_record("Sun", value, 35.0,
            retrograde=False, precision="strict_factual")
        longitude = value % 360.0
        assert record["sidereal_longitude"] == longitude
        assert 0 <= record["degree"] < 30
        assert record["sign"] == producer.RASI_NAMES[int(longitude // 30)]
        assert record["nakshatra"] == producer._nakshatra_record(longitude)
        assert json.loads(json.dumps(record)) == record


@pytest.mark.parametrize("value", [0.0, 29.99996, 13.33334, 3.33334, 359.99996])
def test_original_precision_for_planets_and_lagna(value):
    planet = producer.build_planet_record("Sun", value, 0.0,
        retrograde=False, precision="strict_factual")
    lagna = producer.build_lagna_record(value, precision="strict_factual")
    assert planet["sidereal_longitude"] == lagna["sidereal_longitude"] == value
    assert planet["degree"] == lagna["degree"] == value - 30 * int(value // 30)
    assert planet["nakshatra"] == lagna["nakshatra"]


def test_legacy_shape_default_and_known_rounding_are_preserved():
    implicit = producer.build_planet_record("Sun", 29.99996, 0, retrograde=False)
    explicit = producer.build_planet_record("Sun", 29.99996, 0, retrograde=False, precision="legacy_v1")
    assert implicit == explicit
    assert implicit["degree"] == 30.0
    assert "sidereal_longitude" not in implicit
    assert "sidereal_longitude" not in producer.build_lagna_record(29.99996)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True, "30"])
def test_strict_source_rejects_invalid_numeric_value(value):
    with pytest.raises(ValueError, match="invalid_source_longitude"):
        producer.build_lagna_record(value, precision="strict_factual")


def test_unknown_precision_is_never_a_fallback():
    with pytest.raises(ValueError, match="unsupported_precision"):
        producer.build_lagna_record(0, precision="unknown")


def test_unrepresentable_source_does_not_escape_as_raw_overflow_or_index_error():
    for value in (10 ** 1000, math.nextafter(0.0, -math.inf)):
        with pytest.raises(ValueError, match="invalid_source_longitude"):
            producer.build_lagna_record(value, precision="strict_factual")
