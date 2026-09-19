"""HD astronomy + 88-degree solver only. No graph/classification or API layer."""
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from math import isfinite

import swisseph as swe

# Reuse exactly the existing native-state owner; never introduce a second lock.
from app.services import astrology_service as native
from app.services.human_design_mapping import gate_line
from app.services.human_design_models import Activation, AstronomyResult, Body, DesignMoment, HumanDesignError

FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED
BODIES: tuple[Body, ...] = ('sun', 'earth', 'moon', 'north_node', 'south_node',
    'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto')
NATIVE_BODIES = {'sun': swe.SUN, 'moon': swe.MOON, 'north_node': swe.TRUE_NODE,
    'mercury': swe.MERCURY, 'venus': swe.VENUS, 'mars': swe.MARS,
    'jupiter': swe.JUPITER, 'saturn': swe.SATURN, 'uranus': swe.URANUS,
    'neptune': swe.NEPTUNE, 'pluto': swe.PLUTO}
MAX_ITERATIONS = 64


def _normalize(value: float) -> float:
    if not isfinite(value):
        raise HumanDesignError('ephemeris_error', 'Nonfinite ephemeris result.')
    result = value % 360
    return 0.0 if result == 360 else result


def _longitude(jd_ut1: float, body: int) -> float:
    """Caller owns native._LOCK and has initialized this worker."""
    values, flags = swe.calc_ut(jd_ut1, body, FLAGS)
    if flags != FLAGS or not all(isfinite(v) for v in values):
        raise HumanDesignError('ephemeris_error', 'Unexpected ephemeris result or mode.')
    if body == swe.SUN and values[3] <= 0:
        raise HumanDesignError('design_moment_error', 'Unexpected solar progression.')
    return _normalize(values[0])


def solve_design_moment(birth_jd: float, birth_sun: float,
                        sun_at: Callable[[float], float]) -> DesignMoment:
    """Numerical solver, no native state. sun_at must use the same astronomy model."""
    def failure() -> None:
        raise HumanDesignError('design_moment_error', 'Solar arc did not converge safely.')

    if not isfinite(birth_jd) or not isfinite(birth_sun):
        failure()
    target = (birth_sun - 88) % 360

    def residual(jd: float) -> float:
        sun = sun_at(jd)
        if not isfinite(sun):
            failure()
        return ((sun - target + 180) % 360) - 180

    lo, hi = birth_jd - 100, birth_jd - 80
    left, right = residual(lo), residual(hi)
    # This short solar bracket must increase and cannot straddle the +/-180 cut.
    if not (lo < hi < birth_jd and left <= 0 <= right and 0 < right - left < 180):
        failure()
    for iteration in range(1, MAX_ITERATIONS + 1):
        mid = lo + (hi - lo) / 2
        value = residual(mid)
        if not left <= value <= right:
            failure()
        width = (hi - lo) * 86400
        if width <= 0.01 and abs(value) <= 1e-7:
            return DesignMoment(mid, width, value, iteration)
        if mid == lo or mid == hi:
            failure()
        if value < 0:
            lo, left = mid, value
        else:
            hi, right = mid, value
    failure()
    raise AssertionError('unreachable')


def _serialize_utc(jd_ut1: float) -> datetime:
    year, month, day, hour, minute, seconds = swe.jdut1_to_utc(jd_ut1, swe.GREG_CAL)
    if not isfinite(seconds):
        raise HumanDesignError('ephemeris_error', 'Invalid UTC conversion.')
    # round(Fraction) uses exact ties-to-even; timedelta handles carry at minute/day.
    micros = round(Fraction(seconds) * 1_000_000)
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc) + timedelta(microseconds=micros)


def _activations(jd_ut1: float) -> tuple[Activation, ...]:
    positions = {name: _longitude(jd_ut1, body) for name, body in NATIVE_BODIES.items()}
    positions['earth'] = _normalize(positions['sun'] + 180)
    positions['south_node'] = _normalize(positions['north_node'] + 180)
    return tuple(Activation(body, positions[body], *gate_line(positions[body])) for body in BODIES)


def calculate_activations(birth_utc: datetime) -> AstronomyResult:
    if not isinstance(birth_utc, datetime) or birth_utc.utcoffset() != timedelta(0):
        raise HumanDesignError('invalid_utc_datetime', 'An exact aware UTC datetime is required.')
    if not 1800 <= birth_utc.year <= 2100:
        raise HumanDesignError('unsupported_date_range', 'Supported birth years are 1800 through 2100.')
    with native._LOCK:
        try:
            native.initialize_ephemeris()
            _, jd = swe.utc_to_jd(birth_utc.year, birth_utc.month, birth_utc.day,
                birth_utc.hour, birth_utc.minute, birth_utc.second + birth_utc.microsecond / 1e6, swe.GREG_CAL)
            if not isfinite(jd):
                raise HumanDesignError('ephemeris_error', 'Invalid Julian day.')
            personality = _activations(jd)
            design = solve_design_moment(jd, personality[0].longitude, lambda t: _longitude(t, swe.SUN))
            # Compute from the root itself, never from the rounded UTC display value.
            activations = _activations(design.jd_ut1)
            return AstronomyResult(jd, design, _serialize_utc(design.jd_ut1), personality, activations)
        except (swe.Error, native.AstrologyError, ValueError, OverflowError):
            raise HumanDesignError('ephemeris_error', 'Ephemeris calculation failed.') from None
