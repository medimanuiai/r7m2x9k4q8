import json
from datetime import datetime, timedelta
import random

# Generator for deterministic Surya validation testcases
random.seed(0)

def frange(start, stop, step):
    x = start
    while x <= stop:
        yield x
        x += step


def generate_cases(count=500):
    cases = []
    # distributions to ensure coverage
    years = list(range(1900, 2026))
    months = list(range(1, 13))
    days = list(range(1, 29))  # keep safe for all months
    hours = [0, 1, 6, 11, 12, 13, 23]
    minutes = [0, 15, 30, 45]
    # latitudes: -60 to 60
    lats = [-60, -30, -15, 0, 15, 23.5, 34.0, 51.5, 60.0]
    lons = [-180, -122.4194, -74.0060, -0.1278, 77.1025, 139.6917, 151.2093, 12.4964]
    tz_offsets = [-12, -8, -5, 0, 1, 5.5, 8, 10]
    # pick leap years explicitly
    leap_years = [y for y in years if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0))]

    i = 0
    ri = 0
    while len(cases) < count:
        if i % 50 == 0 and i > 0:
            ri += 1
        year = random.choice(years)
        # bias towards including leap years
        if i % 10 == 0:
            year = random.choice(leap_years)
        month = random.choice(months)
        day = random.choice(days)
        hour = random.choice(hours)
        minute = random.choice(minutes)
        dt = datetime(year, month, day, hour, minute)
        # choose timezone offset
        tz = random.choice(tz_offsets)
        lat = random.choice(lats)
        lon = random.choice(lons)

        # input key as ISO UTC
        # assume dt is local and convert to UTC by subtracting tz hours
        dt_utc = dt - timedelta(hours=tz)
        dobutc = dt_utc.isoformat() + 'Z'

        case = {
            'input': {
                'DOBUTC': dobutc,
                'time': dt.time().isoformat(),
                'lat': lat,
                'lon': lon,
                'tz_offset': tz,
            },
            # expected placeholders; to be populated by Skyfield-based validation job
            'expected': {
                'planets': {},
                'id': f'case_{len(cases)+1:04d}',
                'note': 'expected positions to be filled by validation job using Skyfield'
            }
        }
        cases.append(case)
        i += 1

    return cases


def main():
    cases = generate_cases(500)
    with open('tests/surya/planet_position_test_cases.json', 'w', encoding='utf8') as f:
        json.dump(cases, f, indent=2)
    print('Wrote 500 test cases to tests/surya/planet_position_test_cases.json')


if __name__ == '__main__':
    main()
