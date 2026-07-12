import sys
from pathlib import Path
from datetime import datetime, timezone
import json
import os

import pytest

# Ensure package importability
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root / "systems" / "SuryaSiddhanta"))

from ndastro_engine.core import get_planets_position
from ndastro_engine.enums import Planets


EPHEMERIS_PATH = repo_root / "systems" / "SuryaSiddhanta" / "ndastro_engine" / "data" / "ephemeris" / "de440t.bsp"
TRUSTED_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "trusted_chart.json"


def _has_srtm():
    try:
        import srtm

        return True
    except Exception:
        return False


def _load_trusted():
    with open(TRUSTED_FIXTURE, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.mark.integration
def test_integration_accuracy():
    # Skip if ephemeris missing
    if not EPHEMERIS_PATH.exists():
        pytest.skip(f"Ephemeris not found at {EPHEMERIS_PATH}")

    # Require srtm for accurate elevation lookup
    if not _has_srtm():
        pytest.skip("srtm package not available; install srtm to run accuracy integration tests")

    # Canonical input: local time 1995-03-10 14:35 IST (+05:30) -> 09:05 UTC
    given_time = datetime(1995, 3, 10, 9, 5, tzinfo=timezone.utc)

    lat = 12.9716
    lon = 77.5946

    planets = list(Planets)

    computed = get_planets_position(planets, lat=lat, lon=lon, given_time=given_time)

    # Load trusted fixture
    if not TRUSTED_FIXTURE.exists():
        pytest.skip(f"Trusted fixture not found at {TRUSTED_FIXTURE}; generate it with scripts/generate_trusted_fixture.py")

    trusted = _load_trusted()

    # Compare a subset (planet longitudes) with tolerances
    tol_deg = 0.5
    for p in planets:
        name = p.name
        comp = computed[p].longitude
        if name not in trusted['planets']:
            pytest.fail(f"Trusted fixture missing planet {name}")
        expected = trusted['planets'][name]['lon_deg']
        diff = abs((comp - expected + 180) % 360 - 180)
        assert diff <= tol_deg, f"Planet {name} differs by {diff}° (expected {expected}, got {comp})"
