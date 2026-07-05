# NDAstro engine

[![PyPI version](https://badge.fury.io/py/ndastro-engine.svg)](https://badge.fury.io/py/ndastro-engine)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Wiki](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://dhuruvah-in.github.io/ndastro-core/)
[![Build](https://github.com/dhuruvah-apps/ndastro-core/actions/workflows/publish.yml/badge.svg)](https://github.com/dhuruvah-apps/ndastro-core/actions/workflows/publish.yml)
[![Docs](https://github.com/dhuruvah-apps/ndastro-core/actions/workflows/docs.yml/badge.svg)](https://github.com/dhuruvah-apps/ndastro-core/actions/workflows/docs.yml)

A modern Python library for Vedic astronomical calculations, built on top of [Skyfield](https://rhodesmill.org/skyfield/). NDAstro engine provides a clean, intuitive API for computing planetary positions, sunrise/sunset times, lunar nodes (Rahu/Kethu), ascendant, and other astronomical events for any location on Earth.

## Features

- 🪐 **Planetary Positions** - Calculate positions for Sun, Moon, Mars, Mercury, Jupiter, Venus, and Saturn. Calculations are based on Geocentric - Apparent positions with wobbling True Nodes. 
- 🚀 **Planetary Velocities** - Get speed components (longitude, latitude, distance rates) for all planets
- 🌅 **Sunrise & Sunset** - Accurate sunrise and sunset times for any location
- 🌙 **Lunar Nodes** - Rahu (North Node) and Kethu (South Node) calculations
- ⬆️ **Ascendant Calculation** - Compute rising sign (Lagna) for any time and location
- ⏱️ **Dasa Calculations** - Multi-level dasa periods (Mahadasa, Antardasa, Pratyantardasa, Sookshmadasa) with Vimshottari system built-in; full extensibility for custom dasa systems
- 🔧 **Type-safe Ayanamsa Systems** - `AyanamsaSystem` TypeAlias covering 16 calculation methods (Lahiri, Raman, Krishnamurti, Fagan-Bradley, and more) with IDE autocomplete
- �🔄 **16 Ayanamsa Systems** - Comprehensive support for Vedic and Western sidereal systems:
  - Lahiri, Raman, Krishnamurti (KP New & Old), Fagan-Bradley
  - Traditional: Kali, Janma, Yukteshwar, Suryasiddhanta, Aryabhatta
  - Star-based: True Citra, True Revati, True Pusya, Ushashasi
  - Additional: Madhava, Vishnu, True ayanamsa
- � **House & Nakshatra Enums** - `Houses` with owner lookup; `Nakshatras` (27 lunar mansions) with lord lookup
- �🌍 **WGS84 Coordinates** - Support for standard latitude/longitude coordinates
- 📅 **Date-based Queries** - Calculate astronomical events for any date and time
- 🎯 **High Precision** - Powered by Skyfield using JPL ephemeris data (DE440s)
- ✅ **Verified Accuracy** - All ayanamsa values verified against astro-seek.com reference
- 🔧 **Easy Configuration** - Automatic ephemeris data management
- 🏷️ **Type-safe Enum Codes** - `PlanetCode`, `HouseCode`, `NakshatraCode`, `RasiCode` TypeAliases for safe string lookups via `.code` property and `from_code()` helpers
- 📦 **Modern Python** - Full type hints, clean API, and comprehensive test coverage

## Installation

Install using pip:

```bash
pip install ndastro-engine
```

For development:

```bash
pip install ndastro-engine[dev]
```

## Documentation

Full documentation is available at **[https://ndastro-engine.dhuruvah.in/](https://ndastro-engine.dhuruvah.in/)**

The documentation includes:
- 📖 **Getting Started Guide** - Installation and quick start tutorials
- 📚 **User Guide** - Detailed guides on ayanamsa, planets, retrograde, and sunrise/sunset calculations
- 🔍 **API Reference** - Complete API documentation with examples
- 📝 **Contributing Guide** - Information for contributors

## Quick Start

```python
from datetime import datetime
import pytz
from ndastro_engine.core import get_planet_position, get_planets_position, get_sunrise_sunset
from ndastro_engine.enums import Planets  # Simplified import

# Define location (New York City)
latitude = 40.7128
longitude = -74.0060
time = datetime(2026, 1, 6, 12, 0, 0, tzinfo=pytz.UTC)

# Get Sun's position (returns PlanetPosition named tuple)
position = get_planet_position(Planets.SUN, latitude, longitude, time)
print(f"Sun: Longitude {position.longitude:.2f}°, Latitude {position.latitude:.4f}°")
print(f"     Distance {position.distance:.4f} AU")
print(f"     Speed: {position.speed_longitude:.4f}°/day")

# Get all planetary positions
positions = get_planets_position([], latitude, longitude, time)
for planet, pos in positions.items():
    print(f"{planet.name}: {pos.longitude:.2f}° (moving {pos.speed_longitude:+.4f}°/day)")

# Get sunrise and sunset
sunrise, sunset = get_sunrise_sunset(latitude, longitude, time)
print(f"Sunrise: {sunrise}")
print(f"Sunset: {sunset}")
```

## Usage Examples

### Working with Enum Codes

```python
from ndastro_engine.enums import Planets, Rasis, Houses, Nakshatras, PlanetCode, RasiCode

# Each enum exposes a .code property for type-safe string identifiers
print(Planets.SUN.code)        # "SU"
print(Rasis.ARIES.code)        # "AR"
print(Houses.HOUSE1.code)      # "H01"
print(Nakshatras.ASWINNI.code) # "ASW"

# Convert a code back to the enum
planet = Planets.from_code("MA")   # → Planets.MARS
rasi = Rasis.from_code("SC")        # → Rasis.SCORPIO  (returns None if invalid)
house = Houses.from_code("H7")      # → Houses.HOUSE7
nakshatra = Nakshatras.from_code("REV")  # → Nakshatras.REVATHI

# Rasi.from_string() is now safe — returns None instead of raising KeyError
rasi = Rasis.from_string("invalid")  # → None
```

### Ayanamsa Calculation

```python
from datetime import datetime
from ndastro_engine.ayanamsa import get_ayanamsa

# Calculate ayanamsa for a specific date
date = datetime(2026, 1, 15, 12, 0, 0)

lahiri = get_ayanamsa(date, "lahiri")
raman = get_ayanamsa(date, "raman")
kp = get_ayanamsa(date, "krishnamurti_new")
fagan = get_ayanamsa(date, "fagan_bradley")

print(f"Lahiri Ayanamsa: {lahiri:.4f}°")
print(f"Raman Ayanamsa: {raman:.4f}°")
print(f"KP New Ayanamsa: {kp:.4f}°")
print(f"Fagan-Bradley Ayanamsa: {fagan:.4f}°")
```

### Dasa Calculations

```python
from datetime import datetime
import pytz
from ndastro_engine.dasa import DasaContext, DasaQuery, get_dasa_timeline, get_running_dasa

# Create birth context (Vimshottari is default)
context = DasaContext(
    birth_datetime=datetime(1985, 10, 24, 6, 30, 0, tzinfo=pytz.UTC),
    lat=13.08,          # Chennai latitude
    lon=80.27,          # Chennai longitude
    ayanamsa_system="lahiri"
)

# Get 40-year timeline with 4 levels
timeline = get_dasa_timeline(context, DasaQuery(levels=4, years=40))

# Print first mahadasa
maha = timeline[0]
print(f"Mahadasa {maha.lord}: {maha.start_utc.date()} → {maha.end_utc.date()}")

# Find running dasa at a specific date
query_date = datetime(2026, 4, 18, 12, 0, 0, tzinfo=pytz.UTC)
running = get_running_dasa(query_date, context)
print(f"Current Mahadasa: {running.maha.lord if running.maha else 'N/A'}")
print(f"Current Antardasa: {running.antara.lord if running.antara else 'N/A'}")
```

### Planetary Position Calculation

```python
from datetime import datetime
import pytz
from ndastro_engine.core import get_planet_position
from ndastro_engine.enums import Planets
from ndastro_engine.ayanamsa import get_lahiri_ayanamsa

# Location: Mumbai, India
lat = 19.0760
lon = 72.8777
time = datetime(2026, 1, 15, 12, 0, 0, tzinfo=pytz.UTC)

# Get Jupiter's position (tropical)
position = get_planet_position(Planets.JUPITER, lat, lon, time)
print(f"Jupiter (Tropical): {position.longitude:.2f}°")
print(f"  Speed: {position.speed_longitude:+.4f}°/day")

# For sidereal/Vedic positions, calculate ayanamsa separately
ayanamsa = get_lahiri_ayanamsa(time)
sidereal_longitude = position.longitude - ayanamsa
print(f"Jupiter (Sidereal): {sidereal_longitude:.2f}°")
```

### Get All Planetary Positions at Once

```python
from datetime import datetime
import pytz
from ndastro_engine.core import get_planets_position
from ndastro_engine.enums import Planets

lat = 51.5074  # London
lon = -0.1278
time = datetime(2026, 3, 20, 0, 0, 0, tzinfo=pytz.UTC)

# Get positions for all planets including Rahu, Kethu, and Ascendant
positions = get_planets_position([], lat, lon, time)

for planet, pos in positions.items():
    if planet in [Planets.RAHU, Planets.KETHU, Planets.ASCENDANT]:
        print(f"{planet.name}: {pos.longitude:.2f}°")
    else:
        print(f"{planet.name}: {pos.longitude:.2f}° (Distance: {pos.distance:.4f} AU)")
        print(f"  Speed: {pos.speed_longitude:+.4f}°/day")
```

### Basic Sunrise/Sunset Calculation

```python
from datetime import datetime
from ndastro_engine.astro_engine import get_sunrise_sunset

# Location: London, UK
lat = 51.5074
lon = -0.1278

# Calculate for a specific date
date = datetime(2026, 1, 15)
sunrise, sunset = get_sunrise_sunset(lat, lon, date)

print(f"On {date.date()}, sunrise is at {sunrise.strftime('%H:%M:%S')} UTC")
print(f"On {date.date()}, sunset is at {sunset.strftime('%H:%M:%S')} UTC")
```

### Working with Different Time Zones

```python
from datetime import datetime
import pytz
from ndastro_engine.astro_engine import get_sunrise_sunset

# Location: Tokyo, Japan
lat = 35.6762
lon = 139.6503

# Get times in local timezone
date = datetime(2026, 6, 21)
sunrise_utc, sunset_utc = get_sunrise_sunset(lat, lon, date)

# Convert to Tokyo time
tokyo_tz = pytz.timezone('Asia/Tokyo')
sunrise_local = sunrise_utc.replace(tzinfo=pytz.UTC).astimezone(tokyo_tz)
sunset_local = sunset_utc.replace(tzinfo=pytz.UTC).astimezone(tokyo_tz)

print(f"Sunrise (Tokyo): {sunrise_local.strftime('%H:%M:%S %Z')}")
print(f"Sunset (Tokyo): {sunset_local.strftime('%H:%M:%S %Z')}")
```

## Configuration

The library automatically downloads and caches the required JPL ephemeris data (DE441) on first use. The data is stored in your system's application data directory:

- **Windows**: `%APPDATA%\ndastro`
- **macOS**: `~/Library/Application Support/ndastro`
- **Linux**: `~/.local/share/ndastro`

This data is approximately 150 MB and only needs to be downloaded once.

## API Reference

### `get_planet_position(planet, lat, lon, given_time)`

Calculate the position of a specific planet.

**Parameters:**
- `planet` (Planets): The planet enum (e.g., Planets.SUN, Planets.MOON)
- `lat` (float): Latitude of the observer in decimal degrees
- `lon` (float): Longitude of the observer in decimal degrees
- `given_time` (datetime): The datetime of observation in UTC

**Returns:**
- `PlanetPosition`: Named tuple with attributes:
  - `latitude` (float): Planet's ecliptic latitude in degrees
  - `longitude` (float): Planet's ecliptic longitude in degrees
  - `distance` (float): Distance from Earth in AU
  - `speed_latitude` (float): Rate of latitude change in degrees/day
  - `speed_longitude` (float): Rate of longitude change in degrees/day
  - `speed_distance` (float): Rate of distance change in AU/day

**Example:**
```python
from datetime import datetime
import pytz
from ndastro_engine.core import get_planet_position
from ndastro_engine.enums import Planets

position = get_planet_position(
    Planets.MARS, 
    34.0522, -118.2437,  # Los Angeles
    datetime(2026, 3, 20, tzinfo=pytz.UTC)
)
print(f"Mars longitude: {position.longitude:.2f}°")
print(f"Mars speed: {position.speed_longitude:+.4f}°/day")
```

### `get_planets_position(planets, lat, lon, given_time)`

Calculate positions for all planets, including Rahu, Kethu, and Ascendant.

**Parameters:**
- `planets` (list[Planets]): List of planets to calculate (empty list returns all planets)
- `lat` (float): Latitude of the observer in decimal degrees
- `lon` (float): Longitude of the observer in decimal degrees
- `given_time` (datetime): The datetime of observation in UTC

**Returns:**
- `dict[Planets, PlanetPosition]`: Dictionary mapping each planet to its PlanetPosition named tuple

**Example:**
```python
from datetime import datetime
import pytz
from ndastro_engine.core import get_planets_position

positions = get_planets_position(
    [],  # Empty list gets all planets
    12.97, 77.59,  # Bangalore, India
    datetime(2026, 1, 15, tzinfo=pytz.UTC)
)

for planet, pos in positions.items():
    print(f"{planet.name}: {pos.longitude:.2f}° @ {pos.speed_longitude:+.4f}°/day")
```

### `get_sunrise_sunset(lat, lon, given_time, elevation=914)`

Calculate sunrise and sunset times for a specific location and date.

**Parameters:**
- `lat` (float): Latitude of the location in decimal degrees
- `lon` (float): Longitude of the location in decimal degrees
- `given_time` (datetime): The date for which to calculate sunrise/sunset
- `elevation` (float, optional): Elevation in meters (default: 914m)

**Returns:**
- `tuple[datetime, datetime]`: (sunrise, sunset) as UTC datetime objects

**Example:**
```python
from datetime import datetime
import pytz
from ndastro_engine.core import get_sunrise_sunset

sunrise, sunset = get_sunrise_sunset(
    34.0522, -118.2437,  # Los Angeles
    datetime(2026, 3, 20, tzinfo=pytz.UTC)
)
```

## Requirements

- Python 3.10 or higher
- skyfield >= 1.53
- pytz >= 2025.2

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/jaganathanb/ndastro-core.git
cd ndastro-core

# Install with development dependencies
pip install -e .[dev]

# Verify installation by running tests
pytest tests/ -v
```

**Development Dependencies Include:**
- pytest>=9.0.2 - Testing framework
- pytest-cov>=6.0.0 - Coverage reporting
- pytest-xdist>=3.6.1 - Parallel test execution
- ruff>=0.14.10 - Linting and formatting
- mypy>=1.19.1 - Type checking

### Running Tests

The project includes comprehensive test coverage with multiple ways to run tests:

```bash
# Run all tests with coverage (recommended)
pytest tests/

# Or using the test runner scripts:
# PowerShell (Windows)
.\run_tests.ps1

# Batch (Windows)
run_tests.bat coverage

# Make (cross-platform)
make test
```

**Test Modes:**

```bash
# Run only unit tests
pytest -m unit tests/

# Run fast tests (exclude slow tests)
pytest -m "not slow" tests/

# Run with verbose output
pytest tests/ -v

# Run in parallel (faster for large test suites)
pytest -n 4 tests/

# Generate HTML coverage report
pytest tests/ --cov=ndastro_engine --cov-report=html
# Then open htmlcov/index.html in your browser
```

**Test Coverage:**
- 69 total unit tests covering all core functionality
- Parametrized tests for comprehensive edge case coverage
- Test markers for easy filtering (unit, integration, slow)
- Automated coverage reporting

For detailed testing documentation, see [TESTING.md](TESTING.md).

### Code Quality

The project uses:
- **pytest** for testing with coverage reporting
- **pytest-cov** for coverage analysis
- **pytest-xdist** for parallel test execution
- **ruff** for linting and formatting
- **mypy** for type checking

```bash
# Run linter
ruff check ndastro_engine/ tests/

# Run type checker
mypy ndastro_engine/

# Format code
ruff format ndastro_engine/ tests/

# Run all quality checks
make lint && make type-check && make test
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built on [Skyfield](https://rhodesmill.org/skyfield/) by Brandon Rhodes
- Uses JPL ephemeris data (DE440t) for high-precision calculations
- Inspired by the need for a simple, modern astronomical calculation library

## Support

- 📫 **Email**: jaganathan.eswaran at gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/dhuruvah-apps/ndastro-core/issues)
- 📖 **Documentation**: [GitHub Repository](https://github.com/dhuruvah-apps/ndastro-core)

## Roadmap

### Coming Soon: Vedic Astrology Features 🕉️

The library will soon include comprehensive Vedic (Hindu/Indian) astrology functionalities:

**Panchanga Calculations:**
- Tithi (Lunar day) - All 30 tithis with precise timing
- Nakshatra (Lunar mansion) - 27 nakshatras with pada divisions
- Yoga - 27 yogas based on Sun-Moon positions
- Karana - Half-tithi divisions
- Vara (Weekday) - Traditional Hindu weekday system

**Astrological Timings:**
- Rahu Kala (Inauspicious period)
- Gulika Kala
- Yamaganda Kala
- Abhijit Muhurta (Auspicious time)
- Brahma Muhurta (Pre-dawn period)
- Dur Muhurtam (Inauspicious periods)

**Planetary Calculations:**
- Graha Sphuta (Planetary positions in sidereal zodiac)
- Ayanamsa corrections (Lahiri, Raman, Krishnamurti systems)
- Bhava (House) calculations
- Dasha periods (Vimshottari, Ashtottari, Yogini)
- Planetary strengths (Shadbala, Ashtakavarga)

**Hora & Choghadiya:**
- Hourly lord calculations
- Choghadiya divisions for day/night
- Auspicious/inauspicious period identification

**Festival & Event Calculations:**
- Hindu festival dates (Diwali, Holi, Navratri, etc.)
- Ekadashi dates
- Purnima (Full moon) and Amavasya (New moon)
- Sankranti (Solar transitions)
- Vyatipata and Vaidhriti yogas

**Birth Chart Features:**
- Rashi (Moon sign) calculations
- Lagna (Ascendant) determination
- Navamsa and other divisional charts
- Compatibility matching (Guna Milan)

### Other Planned Features

- Moon phase calculations
- Solar and lunar eclipse predictions
- Planetary positions (Western tropical system)
- Twilight times (civil, nautical, astronomical)
- Constellation identification
- Custom observer elevation support

## Changelog

See [CHANGELOG.md](https://github.com/dhuruvah-apps/ndastro-core/releases) for a list of changes.

---

Made with ❤️ by Jaganathan B
