"""Focused MVP-01 contracts for the safe Lahiri-sidereal web boundary."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from systems.Parasara.tools import runner_api
from systems.Parasara.tools import surya_to_parasara as chart_boundary
from ndastro_engine.enums import Planets


SYNTHETIC_REQUEST = {
    "dob": "2001-02-03",
    "time": "14:25",
    "place": "Synthetic sample - not a real person",
    "lat": 12.9716,
    "lon": 77.5946,
    "tz": "Asia/Kolkata",
    "consent": True,
}


@pytest.fixture(scope="module")
def synthetic_response():
    response = runner_api.run_request(SYNTHETIC_REQUEST)
    assert "error" not in response
    return response


@pytest.fixture(scope="module")
def synthetic_blank_place_response():
    response = runner_api.run_request({**SYNTHETIC_REQUEST, "place": ""})
    assert "error" not in response
    return response


@pytest.mark.parametrize("place", ["", "   "])
def test_blank_place_label_uses_coordinates_without_fabricating_a_city(place):
    assert runner_api.display_location(place, 12.9716, 77.5946) == (
        "12.971600, 77.594600"
    )


def test_supplied_place_label_is_trimmed_and_displayed():
    request = {**SYNTHETIC_REQUEST, "place": "  Synthetic test location  "}
    birth = runner_api.validate_birth_request(request)

    assert birth.place_label == "Synthetic test location"
    assert runner_api.display_location(
        birth.place_label, birth.latitude, birth.longitude
    ) == "Synthetic test location"


def test_blank_place_api_envelope_preserves_inputs_and_separate_timezone(
    synthetic_blank_place_response,
):
    birth = synthetic_blank_place_response["birth"]
    location = synthetic_blank_place_response["surya_chart"]["metadata"][
        "birth_location"
    ]

    assert birth["place"] == ""
    assert birth["display_location"] == "12.971600, 77.594600"
    assert birth["timezone"] == "Asia/Kolkata"
    assert location["latitude"] == 12.9716
    assert location["longitude"] == 77.5946
    assert location["place_label"] == ""


def test_local_time_converts_to_expected_utc_instant():
    birth = runner_api.validate_birth_request(SYNTHETIC_REQUEST)

    assert birth.local_datetime.isoformat() == "2001-02-03T14:25:00+05:30"
    assert birth.utc_datetime == datetime(2001, 2, 3, 8, 55, tzinfo=timezone.utc)
    assert birth.timezone_offset_minutes == 330


def _fixed_astronomy(monkeypatch):
    position = SimpleNamespace(longitude=25.0, speed_longitude=0.5)
    sentinel = SimpleNamespace(longitude=0.0, speed_longitude=0.0)
    monkeypatch.setattr(
        chart_boundary,
        "get_planets_position",
        lambda planets, lat, lon, dt: {
            Planets.EMPTY: sentinel,
            Planets.ASCENDANT: sentinel,
            Planets.SUN: position,
        },
    )
    monkeypatch.setattr(
        chart_boundary,
        "get_ascendent_position",
        lambda lat, lon, dt: 55.0,
    )
    monkeypatch.setattr(
        chart_boundary,
        "get_ayanamsa",
        lambda dt, system: 24.0,
    )


def test_lahiri_ayanamsa_is_applied_to_planets_and_ascendant(monkeypatch):
    _fixed_astronomy(monkeypatch)

    chart = chart_boundary.generate_chart(
        12.9716,
        77.5946,
        datetime(2001, 2, 3, 8, 55, tzinfo=timezone.utc),
        330,
        timezone_name="Asia/Kolkata",
        place_label="Synthetic sample",
    )

    assert chart["metadata"]["ayanamsa"] == "lahiri"
    assert chart["metadata"]["ayanamsa_degrees"] == 24.0
    assert chart["metadata"]["birth_datetime_utc"] == "2001-02-03T08:55:00+00:00"
    assert chart["lagna"] == {
        "sign": "Taurus",
        "degree": 1.0,
        "house": 1,
        "nakshatra": {"name": "KAARTHIKAI", "pada": 2, "index": 3},
    }
    assert [planet["name"] for planet in chart["planets"]] == ["Sun"]
    assert chart["planets"][0]["sign"] == "Aries"
    assert chart["planets"][0]["degree"] == 1.0
    assert chart["planets"][0]["house"] == 12


def test_sidereal_sign_degree_nakshatra_and_house_use_corrected_longitude():
    record = chart_boundary.build_planet_record(
        "Synthetic", 13.5, 5.0, retrograde=False
    )

    assert record["sign"] == "Aries"
    assert record["degree"] == 13.5
    assert record["house"] == 1
    assert record["nakshatra"] == {
        "name": "BHARANI",
        "pada": 1,
        "index": 2,
    }


def test_whole_sign_house_is_bounded_for_every_sign_and_non_cancer_lagna():
    # Taurus Lagna: Aries is House 12, Taurus is House 1, and so forth.
    houses = [
        chart_boundary.whole_sign_house(sign * 30 + 1, 31)
        for sign in range(12)
    ]

    assert houses == [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    assert all(isinstance(house, int) and 1 <= house <= 12 for house in houses)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("lat", 90.0001, "invalid_coordinates"),
        ("lat", -90.0001, "invalid_coordinates"),
        ("lon", 180.0001, "invalid_coordinates"),
        ("lon", -180.0001, "invalid_coordinates"),
        ("tz", "Mars/Olympus_Mons", "invalid_timezone"),
        ("dob", "2001-02-29", "invalid_date"),
        ("time", "24:01", "invalid_time"),
        ("consent", False, "consent_required"),
    ],
)
def test_invalid_input_is_rejected_with_stable_codes(field, value, code):
    request = {**SYNTHETIC_REQUEST, field: value}

    with pytest.raises(runner_api.MVPInputError) as raised:
        runner_api.validate_birth_request(request)

    assert raised.value.code == code


def test_repeated_identical_chart_input_is_deterministic(monkeypatch):
    _fixed_astronomy(monkeypatch)
    arguments = (
        12.9716,
        77.5946,
        datetime(2001, 2, 3, 8, 55, tzinfo=timezone.utc),
        330,
    )
    keyword_arguments = {
        "timezone_name": "Asia/Kolkata",
        "place_label": "Synthetic sample",
    }

    first = chart_boundary.generate_chart(*arguments, **keyword_arguments)
    second = chart_boundary.generate_chart(*arguments, **keyword_arguments)

    assert second == first
    assert json.dumps(second, sort_keys=True) == json.dumps(first, sort_keys=True)


def test_synthetic_chart_exports_bounded_whole_sign_houses(synthetic_response):
    chart = synthetic_response["surya_chart"]
    exported = {planet["name"]: planet["house"] for planet in chart["planets"]}

    assert synthetic_response["birth"]["utc_datetime"] == "2001-02-03T08:55:00+00:00"
    assert chart["lagna"]["house"] == 1
    assert all(isinstance(house, int) and 1 <= house <= 12 for house in exported.values())
    assert "Empty" not in exported
    assert "Ascendant" not in exported


def test_synthetic_export_houses_agree_with_career_evidence(synthetic_response):
    chart_houses = {
        planet["name"]: planet["house"]
        for planet in synthetic_response["surya_chart"]["planets"]
    }
    career = synthetic_response["snapshot"]["domains"]["career"]
    component_houses = {
        component["planet"]: component["house"]
        for component in career["components"]
        if component.get("type") == "planet"
    }

    assert component_houses
    assert component_houses == {
        planet: chart_houses[planet] for planet in component_houses
    }
    assert 0 <= career["score"] <= 1
    assert 0 <= career["confidence"] <= 1


def test_node_motion_is_honestly_unsupported(synthetic_response):
    nodes = {
        planet["name"]: planet
        for planet in synthetic_response["surya_chart"]["planets"]
        if planet["name"] in {"Rahu", "Kethu"}
    }

    assert set(nodes) == {"Rahu", "Kethu"}
    assert all(node["motion"] == {} for node in nodes.values())


def test_internal_kethu_identity_and_house_remain_compatible(
    synthetic_blank_place_response,
):
    nodes = {
        planet["name"]: planet["house"]
        for planet in synthetic_blank_place_response["surya_chart"]["planets"]
        if planet["name"] in {"Rahu", "Kethu"}
    }

    assert set(nodes) == {"Rahu", "Kethu"}
    assert all(1 <= house <= 12 for house in nodes.values())


def test_synthetic_request_is_deterministic(synthetic_response):
    repeated = runner_api.run_request(SYNTHETIC_REQUEST)

    assert repeated == synthetic_response


def test_unexpected_errors_never_expose_exception_or_local_path(monkeypatch):
    def fail(_birth):
        raise RuntimeError(r"C:\private\project\sensitive.txt: synthetic-sensitive-value")

    monkeypatch.setattr(runner_api, "generate_response", fail)

    response = runner_api.run_request(SYNTHETIC_REQUEST)
    serialized = json.dumps(response)

    assert response == runner_api.safe_error("generation_failed")
    assert "private" not in serialized
    assert "sensitive" not in serialized
    assert "RuntimeError" not in serialized
