"""Apparent geocentric Moon plus explicitly project-owned discrete mappings."""
from datetime import datetime
from fractions import Fraction
from math import isfinite

import swisseph as swe

from app.services import astrology_service as native
from ._astronomy import angle, julian_days, metadata, validate_utc
from .models import LunarResult, MansionResult, Phase, TraditionalError

_PHASES: tuple[Phase, ...] = ('new_moon', 'waxing_crescent', 'first_quarter',
    'waxing_gibbous', 'full_moon', 'waning_gibbous', 'last_quarter', 'waning_crescent')


def phase_for(elongation: float) -> Phase:
    value = angle(elongation)
    # Direct comparisons avoid addition rounding at nextafter(22.5, -inf).
    for index, boundary in enumerate((22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5)):
        if value < boundary:
            return _PHASES[index]
    return 'new_moon'


def mansion_for(longitude: float) -> MansionResult:
    represented = Fraction(angle(longitude))
    return MansionResult(int(represented * 7 // 90) + 1)


def _longitude(tt: float, body: int) -> float:
    values, flags = swe.calc(tt, body, native.FLAGS)
    if flags != native.FLAGS or not all(isfinite(value) for value in values):
        raise TraditionalError('invalid_astronomical_result')
    return native.normalize_longitude(values[0])


def calculate_lunar(instant: datetime) -> LunarResult:
    validate_utc(instant)
    with native._LOCK:
        try:
            native.initialize_ephemeris()
            tt, _ = julian_days(instant)
            sun, moon = _longitude(tt, swe.SUN), _longitude(tt, swe.MOON)
            illumination = swe.pheno(tt, swe.MOON, swe.FLG_MOSEPH)[1]
            if not isfinite(illumination) or not 0 <= illumination <= 1:
                raise TraditionalError('invalid_astronomical_result')
            elongation = native.normalize_longitude(moon - sun)
            return LunarResult(sun, moon, elongation, illumination,
                phase_for(elongation), mansion_for(moon), metadata())
        except (swe.Error, native.AstrologyError, ValueError, OverflowError):
            raise TraditionalError('ephemeris_error') from None
