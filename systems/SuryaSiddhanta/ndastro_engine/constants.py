"""Constants for ndastro engine.

This module defines constant values used throughout the ndastro_engine package.
"""

OS_WIN = "win32"
OS_MAC = "darwin"
OS_LINUX = "linux"

DEGREE_MAX = 360.0

DEGREE_PER_NAKSHATRA = 13.333333333333334
DEGREE_PER_PADA = 3.3333333333333335
DEGREE_PER_RASI = 30.0
HALF_CIRCLE_DEGREES = 180.0
TOTAL_RASI = 12
TOTAL_NAKSHATRAS = 27
TOTAL_PADA = 4

# Lahiri Ayanamsa constants (referenced to J2000.0)
AYANAMSA_AT_J2000 = 22.460148  # Ayanamsa value at J2000.0 epoch
DEG_PER_JCENTURY = 1.396042  # Linear term (degrees per Julian century)
DEG_PER_SQUARE_JCENTURY = 0.000308  # Quadratic term (degrees per square Julian century)

CENTURY_19 = 1900
CENTURY_20 = 2000
CENTURY_21 = 2100

DAYS_IN_YEAR = 365.256364
AVERAGE_DAYS_IN_MONTH = DAYS_IN_YEAR / 12

# Astronomical time constants
J2000_TT = 2451545.0  # Julian Date of J2000.0 epoch (2000 Jan 1.5 TT)
DAYS_PER_JULIAN_CENTURY = 36525.0  # Exact definition

# IAU 2006 mean lunar node polynomial coefficients (Meeus Ch. 22 / SOFA)
# Omega = longitude of ascending node of Moon's mean orbit, from mean equinox of date
MEAN_NODE_EPOCH_DEG = 125.044520                  # Omega at J2000.0 (degrees)
MEAN_NODE_RATE_DEG_PER_CENTURY = -1934.136261     # Mean retrograde motion (degrees/Julian century)
MEAN_NODE_C2 = 0.002075                           # Quadratic coefficient (degrees/century²)
MEAN_NODE_C3 = 1.0 / 467441.0                     # Cubic coefficient (degrees/century³)
MEAN_NODE_C4 = -1.0 / 60616000.0                  # Quartic coefficient (degrees/century⁴)

# IAU 2006 general precession in ecliptic longitude (ψ_A)
# Used to convert node longitude from J2000 ecliptic to ecliptic of date.
# psi_A ≈ IAU_PRECESSION_LONGITUDE_C1 * T + IAU_PRECESSION_LONGITUDE_C2 * T² (arcseconds)
IAU_PRECESSION_LONGITUDE_C1 = 5038.481507   # arcseconds per Julian century
IAU_PRECESSION_LONGITUDE_C2 = -1.0790069    # arcseconds per century²
ONE_GHATI = 24 / 60  # One Ghati is 24 minutes, which is 0.4 hours
DAYS_IN_CENTURY = DAYS_IN_YEAR * 100

# Angular unit conversion
ARCMIN_PER_DEGREE: int = 60
ARCSEC_PER_DEGREE: int = 3600
