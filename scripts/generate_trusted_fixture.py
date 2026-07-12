#!/usr/bin/env python3
"""Generate a trusted chart fixture using the local SuryaSiddhanta implementation.

Usage: python scripts/generate_trusted_fixture.py
Produces: tests/SuryaSiddhanta/fixtures/trusted_chart.json
"""
from pathlib import Path
import sys
import json
from datetime import datetime, timezone, timedelta

# Ensure package importability
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "systems" / "SuryaSiddhanta"))

from ndastro_engine.core import get_planets_position
from ndastro_engine.enums import Planets


def main():
    out = Path("tests/SuryaSiddhanta/fixtures")
    out.mkdir(parents=True, exist_ok=True)

    # Canonical input: local time 1995-03-10 14:35 IST (+05:30).
    # Convert to UTC for Skyfield: 14:35 - 5:30 = 09:05 UTC
    given_time = datetime(1995, 3, 10, 9, 5, tzinfo=timezone.utc)
    lat = 12.9716
    lon = 77.5946

    planets = list(Planets)
    positions = get_planets_position(planets, lat=lat, lon=lon, given_time=given_time)

    data = {"birth_iso": "1995-03-10T14:35:00+05:30", "lat": lat, "lon": lon, "planets": {}}

    for p in planets:
        pos = positions[p]
        data['planets'][p.name] = {"lon_deg": pos.longitude, "lat_deg": pos.latitude, "distance_au": pos.distance}

    with open(out / "trusted_chart.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print('Wrote', out / 'trusted_chart.json')


if __name__ == '__main__':
    main()
