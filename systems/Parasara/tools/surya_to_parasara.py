"""Generate a Surya-format chart using the local SuryaSiddhanta engine and
optionally run the Parasara snapshot generator end-to-end.

Usage:
  PYTHONPATH=. python systems/Parasara/tools/surya_to_parasara.py --out chart.json --run-snapshot
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import argparse

# Import local SuryaSiddhanta engine
import sys
from pathlib import Path as _P
# Ensure local SuryaSiddhanta package on path
_ROOT = _P(__file__).resolve().parents[3]
_SURYA = _ROOT / 'systems' / 'SuryaSiddhanta'
sys.path.insert(0, str(_SURYA))
sys.path.insert(0, str(_ROOT))
from ndastro_engine.core import get_planets_position, get_ascendent_position
from ndastro_engine.enums import Planets
from ndastro_engine.nakshatra_enum import Nakshatras

RASI_NAMES = [
    'Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
]


def longitude_to_rashi(longitude: float) -> str:
    idx = int((longitude % 360) // 30)
    return RASI_NAMES[idx]


def build_planet_record(name: str, pos) -> dict:
    lon = float(pos.longitude)
    rashi = longitude_to_rashi(lon)
    house_no = int((lon % 360) // 30) + 1
    nak = Nakshatras(int(lon // (360.0 / 27.0)) + 1)
    return {
        'name': name,
        'sign': rashi,
        'degree': round(lon % 30.0, 4),
        'house': house_no,
        'nakshatra': {'name': str(nak), 'pada': Nakshatras.current_pada(lon), 'index': nak.value},
        'motion': {'retrograde': False},
        'flags': {'combust': False, 'exalted': False, 'debilitated': False}
    }


def generate_chart(lat: float, lon: float, dt: datetime, timezone_offset_minutes: int = 0) -> dict:
    positions = get_planets_position([], lat, lon, dt)
    planets = []
    for p_enum, pos in positions.items():
        # skip internal helper enums if any
        try:
            pname = p_enum.name.capitalize()
        except Exception:
            pname = str(p_enum)
        planets.append(build_planet_record(pname, pos))

    asc_lon = get_ascendent_position(lat, lon, dt)
    lagna = {'sign': longitude_to_rashi(asc_lon), 'degree': round(asc_lon % 30.0, 4)}

    chart = {
        'metadata': {
            'birth_datetime_utc': dt.isoformat(),
            'birth_location': {'latitude': lat, 'longitude': lon, 'timezone_offset_minutes': timezone_offset_minutes},
            'ayanamsa': 'lahiri',
            'house_system': 'whole_sign',
            'sidereal': True
        },
        'lagna': lagna,
        'planets': planets,
        'houses': [],
        'aspects': []
    }
    return chart


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--lat', type=float, default=12.9716)
    p.add_argument('--lon', type=float, default=77.5946)
    p.add_argument('--dt', type=str, default='1990-01-01T12:00:00')
    p.add_argument('--tz-offset', type=int, default=330)
    p.add_argument('--out', type=str, default='systems/Parasara/fixtures/surya_generated_chart.json')
    p.add_argument('--run-snapshot', action='store_true')
    args = p.parse_args()

    dt = datetime.fromisoformat(args.dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    chart = generate_chart(args.lat, args.lon, dt, args.tz_offset)
    out_path = Path(args.out)
    out_path.write_text(json.dumps(chart, indent=2))
    print('Wrote surya chart to', out_path)

    if args.run_snapshot:
        from systems.Parasara.tools.generate_snapshot import generate as gen_snap
        snap_out = 'systems/Parasara/tests/snapshots/generated_surya_parasara_output.json'
        gen_snap(str(out_path), snap_out)
        print('Generated Parasara snapshot to', snap_out)


if __name__ == '__main__':
    main()
