from datetime import datetime, timezone
from types import SimpleNamespace
from pathlib import Path
import sys

# Ensure package importability
repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root / "systems" / "SuryaSiddhanta"))

from ndastro_engine.core import get_planet_position
from ndastro_engine.models import PlanetPosition
from ndastro_engine.enums import Planets


class _FakeAstrometric:
    def __init__(self, lat_deg, lon_deg, au=1.0, spd_lat=0.1, spd_lon=0.2, spd_au=0.01):
        self._lat = lat_deg
        self._lon = lon_deg
        self._au = au
        self._spd_lat = spd_lat
        self._spd_lon = spd_lon
        self._spd_au = spd_au

    def frame_latlon_and_rates(self, _frame):
        # Create simple objects with the required attributes used by core.get_planet_position()
        class Angle:
            def __init__(self, degrees):
                self.degrees = degrees

        class Distance:
            def __init__(self, au):
                self.au = au

        class RateDegrees:
            def __init__(self, per_day):
                self.per_day = per_day

        latitude = Angle(self._lat)
        longitude = Angle(self._lon)
        distance = Distance(self._au)

        class SpeedLat:
            def __init__(self, per_day):
                class Inner:
                    def __init__(self, per_day):
                        self.per_day = per_day

                self.degrees = Inner(per_day)

        class SpeedLon(SpeedLat):
            pass

        class SpeedDist:
            def __init__(self, au_per_d):
                self.au_per_d = au_per_d

        speed_lat = SpeedLat(self._spd_lat)
        speed_lon = SpeedLon(self._spd_lon)
        speed_dist = SpeedDist(self._spd_au)

        return latitude, longitude, distance, speed_lat, speed_lon, speed_dist


class _FakeObserver:
    def __init__(self, astrometric):
        self._ast = astrometric

    def observe(self, _target):
        return self

    def apparent(self):
        return self._ast


class _FakeEarth:
    def __init__(self, astrometric):
        self._ast = astrometric

    def at(self, _t):
        return _FakeObserver(self._ast)


def test_get_planet_position_with_mocked_eph(monkeypatch):
    # Prepare fake astrometric returning known values
    fake_ast = _FakeAstrometric(lat_deg=1.1, lon_deg=2.2, au=0.5, spd_lat=0.01, spd_lon=0.02, spd_au=0.001)

    # Fake eph dict where 'earth' returns observer and any planet key is acceptable
    fake_eph = {"earth": _FakeEarth(fake_ast), "sun": object()}

    # Minimal fake timescale where utc(...) returns a dummy object
    class _FakeTS:
        def utc(self, dt):
            return SimpleNamespace(tt=0, tdb=0, gmst=0)

    monkeypatch.setattr("ndastro_engine.core.eph", fake_eph, raising=False)
    monkeypatch.setattr("ndastro_engine.core.ts", _FakeTS(), raising=False)

    pos = get_planet_position(Planets.SUN, lat=12.97, lon=77.59, given_time=datetime(1995, 3, 10, 14, 35, tzinfo=timezone.utc))
    assert isinstance(pos, PlanetPosition)
    assert abs(pos.latitude - 1.1) < 1e-9
    assert abs(pos.longitude - 2.2) < 1e-9
    assert abs(pos.distance - 0.5) < 1e-9
    assert abs(pos.speed_latitude - 0.01) < 1e-9
    assert abs(pos.speed_longitude - 0.02) < 1e-9
    assert abs(pos.speed_distance - 0.001) < 1e-9
