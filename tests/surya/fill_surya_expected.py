import json
from datetime import datetime

from ndastro_engine.core import get_planets_position, get_lunar_node_positions
from ndastro_engine.nakshatra_enum import Nakshatras


def fill_cases(path='tests/surya/planet_position_test_cases.json'):
    with open(path, 'r', encoding='utf8') as f:
        cases = json.load(f)

    updated = 0
    for case in cases:
        inp = case.get('input', {})
        dob = inp.get('DOBUTC')
        lat = inp.get('lat')
        lon = inp.get('lon')
        if not dob or lat is None or lon is None:
            continue
        # parse iso
        dt = datetime.fromisoformat(dob.replace('Z', '+00:00'))
        # compute positions using ndastro_engine (SuryaSiddhanta)
        pos = get_planets_position([], lat, lon, dt)
        planets = {}
        for p_enum, ppos in pos.items():
            try:
                pname = p_enum.name.capitalize()
            except Exception:
                pname = str(p_enum)
            lon_deg = float(ppos.longitude) % 360.0
            nak = Nakshatras(int(lon_deg // (360.0 / 27.0)) + 1)
            planets[pname] = {
                'longitude': round(lon_deg, 6),
                'nakshatra': {'name': str(nak), 'pada': Nakshatras.current_pada(lon_deg), 'index': nak.value},
            }

        # lunar nodes
        rahu, kethu = get_lunar_node_positions(dt)
        planets['Rahu'] = {'longitude': round(rahu % 360.0, 6)}
        planets['Ketu'] = {'longitude': round(kethu % 360.0, 6)}

        case.setdefault('expected', {})['planets'] = planets
        case.setdefault('expected', {})['id'] = case.get('expected', {}).get('id') or 'generated'
        case.setdefault('tolerance_regression_degrees', 0.1)
        updated += 1

    with open(path, 'w', encoding='utf8') as f:
        json.dump(cases, f, indent=2)

    print(f'Updated {updated} cases in {path}')


if __name__ == '__main__':
    fill_cases()
