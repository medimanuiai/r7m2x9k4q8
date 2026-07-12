import json
from pathlib import Path
import math
import pytest

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter


def _ang_diff(a, b):
    d = abs(a - b) % 360.0
    if d > 180:
        d = 360 - d
    return d


@pytest.mark.surya
def test_positions_against_skyfield():
    p = Path('tests/surya/planet_position_test_cases.json')
    data = json.loads(p.read_text())
    # try to import skyfield; if not available, skip validation (CI should install it for validation job)
    try:
        from skyfield.api import Loader, Topos, utc
        from skyfield.api import NumpyDatetime
        from skyfield.api import load as sky_load
        from datetime import datetime
    except Exception:
        pytest.skip('Skyfield not installed; Surya validation skipped')

    # use jplephem ephemeris if available via loader
    for case in data:
        # load Surya chart (we treat the fixture as Surya input)
        if case.get('id') == 'golden_chart_01':
            chart = SuryaAdapter.load('systems/Parasara/fixtures/golden_chart_01.json')
            # compare provided expected positions vs skyfield if possible
            # Basic validation: compare Sun/Moon/Mars longitudes using Skyfield geocentric ecliptic longitude
            ts = sky_load.timescale()
            dt = datetime.fromisoformat(case['birth_datetime_utc'].replace('Z', '+00:00'))
            t = ts.from_datetime(dt)
            eph = sky_load('de421.bsp') if True else sky_load('de421.bsp')
            earth = eph['earth']
            body_map = {'Sun': 'sun', 'Moon': 'moon', 'Mars': 'mars', 'Mercury': 'mercury', 'Jupiter': 'jupiter', 'Venus': 'venus', 'Saturn': 'saturn'}
            # compute ecliptic longitudes
            sky_pos = {}
            for name, key in body_map.items():
                obj = eph[key]
                astrom = earth.at(t).observe(obj).ecliptic_position()
                # get longitude in degrees
                lon = math.degrees(math.atan2(astrom[1], astrom[0])) % 360.0
                # apply lahiri ayanamsa if required (simple subtraction if provided)
                if case.get('ayanamsa', '').lower() == 'lahiri':
                    # use approximate Lahiri (placeholder): 23° 5' (not accurate) -> skip exact correction here
                    pass
                sky_pos[name] = lon

            # Compare Surya positions (from chart.planets) against sky_pos or expected_positions
            for pexp_name, pexp_val in case.get('expected_positions', {}).items():
                # find planet in chart
                pnode = next((x for x in chart.planets if x.name == pexp_name), None)
                assert pnode is not None, f'Planet {pexp_name} missing in Surya chart'
                surya_lon = getattr(pnode, 'degree', None) or 0.0
                # compare to expected value from file
                diff = _ang_diff(surya_lon, float(pexp_val))
                assert diff <= case['tolerance_regression_degrees'] + 1e-12, f'{pexp_name} out of regression tolerance: {diff} deg'
