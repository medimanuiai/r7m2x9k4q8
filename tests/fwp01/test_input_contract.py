"""Strict single/batch contract, safe failures and mutation isolation."""
from copy import deepcopy
import json

import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter, StrictInputError
from systems.Parasara.engine.identities import CANONICAL_PLANETS
from systems.Parasara.tools.surya_to_parasara import build_planet_record, build_lagna_record


def strict_payload(lagna=35.25, longitudes=None):
    values = longitudes or [1.0, 41.0, 89.0, 105.0, 169.0, 211.0, 279.0, 319.0, 139.0]
    return dict(
        metadata=dict(birth_datetime_utc="2001-02-03T14:25:00+05:30",
            birth_location=dict(latitude=0.0, longitude=0.0, timezone_offset_minutes=330),
            ayanamsa="lahiri", sidereal=True, house_system="whole_sign",
            house_numbering="ascendant_relative"),
        lagna=build_lagna_record(lagna, precision="strict_factual"),
        planets=[build_planet_record(name, value, lagna,
            retrograde=None if name in ("Rahu", "Ketu") else False,
            precision="strict_factual") for name, value in zip(CANONICAL_PLANETS, values)],
        houses=[], aspects=[],
    )


def strict_snapshot(payload=None):
    from systems.Parasara.engine.normalizer import build_strict_snapshot
    from systems.Parasara.engine.astrostate_api import require_snapshot
    return require_snapshot(build_strict_snapshot(SuryaAdapter.from_mapping_strict(
        strict_payload() if payload is None else payload)))


def test_single_and_batch_share_contract_and_preserve_indices(tmp_path):
    valid = strict_payload()
    invalid = deepcopy(valid)
    invalid["planets"][0]["degree"] = 30.0
    single = SuryaAdapter.from_mapping_strict(valid)
    batch = SuryaAdapter.from_mappings_strict([valid, invalid, valid])
    assert [item.index for item in batch.records] == [0, 1, 2]
    assert len(batch.charts) == 2
    with pytest.raises(StrictInputError) as failure:
        SuryaAdapter.from_mapping_strict(invalid)
    assert batch.failures[0].issues == failure.value.issues
    path = tmp_path / "charts.json"
    path.write_text(json.dumps([valid, invalid]), encoding="utf-8")
    assert SuryaAdapter.load_many_strict(str(path)).records[1].issues == failure.value.issues
    path.write_text(json.dumps(valid), encoding="utf-8")
    assert SuryaAdapter.load_strict(str(path)) == single
    assert single.metadata["birth_datetime_utc"] == "2001-02-03T08:55:00+00:00"


@pytest.mark.parametrize("field,value", [
    ("degree", 30), ("degree", -0.01), ("degree", True),
    ("sidereal_longitude", 360), ("sidereal_longitude", float("nan")),
    ("sidereal_longitude", float("inf")), ("sidereal_longitude", "1.0"),
    ("sign", "Unknown"), ("house", 0), ("house", 1.0), ("name", "Pluto"),
])
def test_invalid_position_never_coerces(field, value):
    data = strict_payload()
    data["planets"][0][field] = value
    with pytest.raises(StrictInputError):
        SuryaAdapter.from_mapping_strict(data)


@pytest.mark.parametrize("mutation", [
    lambda d: d["planets"].pop(),
    lambda d: d["planets"][0].pop("sidereal_longitude"),
    lambda d: d["planets"][0].update(name="Moon"),
    lambda d: d["planets"][0]["nakshatra"].update(pada=4),
    lambda d: d["planets"][0]["nakshatra"].update(index=27),
    lambda d: d["planets"][0]["motion"].clear(),
    lambda d: d["planets"][0]["flags"].update(exalted=True, debilitated=True),
    lambda d: d["metadata"].update(house_numbering="aries_sign_index_for_protected_normalizer"),
    lambda d: d["metadata"].update(birth_datetime_utc="2001-02-03T08:55:00"),
    lambda d: d["metadata"]["birth_location"].update(latitude=90.1),
    lambda d: d["metadata"]["birth_location"].update(timezone_offset_minutes=True),
    lambda d: d.update(houses=[dict(number=1, sign="Taurus")]),
])
def test_invalid_or_contradictory_required_input_fails(mutation):
    data = strict_payload()
    mutation(data)
    with pytest.raises(StrictInputError) as failure:
        SuryaAdapter.from_mapping_strict(data)
    assert failure.value.issues
    assert "2001-02-03" not in str(failure.value)


def test_safe_json_and_file_failures(tmp_path):
    path = tmp_path / "private-name.json"
    for payload in ['{', '{"metadata":0,"metadata":1}', '"private value"', '{"x":NaN}']:
        path.write_text(payload, encoding="utf-8")
        with pytest.raises(StrictInputError) as failure:
            SuryaAdapter.load_strict(str(path))
        assert str(path) not in str(failure.value)
        assert "private" not in str(failure.value)
    with pytest.raises(StrictInputError, match="input_unreadable"):
        SuryaAdapter.load_strict(str(tmp_path / "absent.json"))


def test_adapter_does_not_mutate_or_retain_input():
    data = strict_payload()
    baseline = deepcopy(data)
    chart = SuryaAdapter.from_mapping_strict(data)
    assert data == baseline
    data["planets"][0]["motion"]["retrograde"] = True
    data["metadata"]["birth_location"]["latitude"] = 50.0
    assert chart.planets[0]["motion"]["retrograde"] is False
    assert chart.metadata["birth_location"]["latitude"] == 0.0


@pytest.mark.parametrize("case", ["degree", "ayanamsa", "place_surrogate", "key_surrogate"])
def test_unsafe_scalars_have_bounded_single_and_indexed_batch_failures(case):
    import sys
    data = strict_payload()
    integer_limit = sys.get_int_max_str_digits()
    if case == "degree":
        data["planets"][0]["degree"] = 10 ** 5000
    elif case == "ayanamsa":
        data["metadata"]["ayanamsa_degrees"] = 10 ** 5000
    elif case == "place_surrogate":
        data["metadata"]["birth_location"]["place_label"] = "\ud800"
    else:
        data["planets"][0]["flags"]["\ud800"] = False
    with pytest.raises(StrictInputError) as failure:
        SuryaAdapter.from_mapping_strict(data)
    assert [(x.path, x.code) for x in failure.value.issues] == [("$", "unsafe_canonical_scalar")]
    assert str(failure.value) == "unsafe_canonical_scalar at $"
    batch = SuryaAdapter.from_mappings_strict([strict_payload(), data, strict_payload()])
    assert [item.index for item in batch.records] == [0, 1, 2]
    assert batch.records[1].issues == failure.value.issues
    assert len(batch.charts) == 2
    from systems.Parasara.engine.normalizer import build_strict_snapshot
    from systems.Parasara.engine.astrostate_api import require_snapshot, snapshot_logical_bytes
    for chart in batch.charts:
        assert snapshot_logical_bytes(require_snapshot(build_strict_snapshot(chart)))
    assert sys.get_int_max_str_digits() == integer_limit


def test_valid_unicode_and_serializer_supported_numbers_remain_exact():
    from systems.Parasara.engine.astrostate_api import snapshot_logical_bytes
    data = strict_payload()
    text = "Jyothishyam — മലയാളം 日本語 🪐"
    data["metadata"]["birth_location"]["place_label"] = text
    data["metadata"]["ayanamsa_degrees"] = 24.123456789012345
    data["planets"][0]["motion"]["speed"] = 1.25
    state = strict_snapshot(data)
    assert state.core.location["place"] == text
    assert state.core.metadata["ayanamsa_degrees"] == data["metadata"]["ayanamsa_degrees"]
    assert text.encode("utf-8") in snapshot_logical_bytes(state)
    # Serialization support, rather than an arbitrary binary64/size cutoff,
    # determines the domain of optional numeric metadata.
    data["metadata"]["ayanamsa_degrees"] = 10 ** 1000
    assert snapshot_logical_bytes(strict_snapshot(data))
