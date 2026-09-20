"""Small Kamerî adapter helpers; native state remains owned by Astrology."""
from datetime import datetime, timedelta
from importlib.metadata import version
from math import isfinite

import swisseph as swe

from .models import AstronomyMetadata, TraditionalError


def validate_utc(instant: datetime) -> None:
    if not isinstance(instant, datetime) or instant.utcoffset() != timedelta(0):
        raise TraditionalError('invalid_utc_datetime')
    if not 1800 <= instant.year <= 2100:
        raise TraditionalError('unsupported_date_range')


def julian_days(instant: datetime) -> tuple[float, float]:
    """Caller holds existing native lock and initializes; same conversion as Astrology.

    Existing engines inline this call; no reusable UTC->JD helper exists there.
    Avoid coupling this adapter to HD-specific error types or display rounding.
    """
    tt, ut1 = swe.utc_to_jd(instant.year, instant.month, instant.day, instant.hour,
        instant.minute, instant.second + instant.microsecond / 1e6, swe.GREG_CAL)
    if not isfinite(tt) or not isfinite(ut1):
        raise TraditionalError('invalid_astronomical_result')
    return tt, ut1


def metadata() -> AstronomyMetadata:
    return AstronomyMetadata(version('pyswisseph'), swe.version)


def angle(value: float) -> float:
    """Pure mapper admission: normalized degrees or explicit 360 wrap, no negatives."""
    if not isfinite(value) or not 0 <= value <= 360:
        raise TraditionalError('invalid_astronomical_result')
    return 0.0 if value == 360 else value
