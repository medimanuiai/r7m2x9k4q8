import sys
import os
from pathlib import Path

# Ensure package importability: add systems/SuryaSiddhanta to sys.path
repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root / "systems" / "SuryaSiddhanta"))

from ndastro_engine.utils import normalize_degree, dms2dd, dd2dms, get_elevation_by_latlon


def test_normalize_degree():
    assert normalize_degree(370) == 10
    assert normalize_degree(-10) == 350


def test_dms_roundtrip():
    dec = dms2dd(12, 34, 56.78)
    d, m, s, sign = dd2dms(dec)
    assert d == 12
    assert m == 34
    assert abs(s - 56.78) < 0.01
    assert sign == 1


def test_elevation_json_fallback(monkeypatch):
    fixture = Path(__file__).resolve().parent / "fixtures" / "elevation_cache.json"
    monkeypatch.setenv("NDASTRO_USE_SRTM", "0")
    monkeypatch.setenv("NDASTRO_ELEVATION_SOURCE", str(fixture))

    # Exact match
    val = get_elevation_by_latlon(12.97, 77.59)
    assert val == 920.0

    # Nearby coordinates that round to the same key
    val2 = get_elevation_by_latlon(12.9716, 77.5946)
    assert val2 == 920.0
