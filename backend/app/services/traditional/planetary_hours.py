"""Sunrise-owned seasonal intervals; no inferred timezone or polar fallback."""
from datetime import date, datetime, timedelta, timezone
from fractions import Fraction
from importlib.metadata import version
from math import isfinite
from zoneinfo import ZoneInfo

import swisseph as swe

from app.services import astrology_service as native
from app.services.timezone_service import load_zone, TimezoneError
from ._astronomy import julian_days, metadata, validate_utc
from .models import (HourInterval, Planet, PlanetaryHourResult, SolarEvents,
                     TraditionalError)

ORDER: tuple[Planet, ...] = ('saturn', 'jupiter', 'mars', 'sun', 'venus', 'mercury', 'moon')
WEEKDAY: tuple[Planet, ...] = ('moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'sun')


def classify_hour(jd_ut1: float, events: SolarEvents, weekday: int) -> HourInterval:
    """Exact rational membership of represented native floats, not display datetimes."""
    values = (jd_ut1, events.sunrise, events.sunset, events.next_sunrise)
    if not all(isfinite(v) for v in values):
        raise TraditionalError('invalid_astronomical_result')
    if type(weekday) is not int or not 0 <= weekday < 7:
        raise TraditionalError('invalid_astronomical_result')
    t, rise, setting, following = map(Fraction, values)
    if not (0 < setting - rise < 1 and 0 < following - setting < 1
            and 0 < following - rise < 2 and rise <= t < following):
        raise TraditionalError('solar_event_unavailable')
    daytime = t < setting
    start, end = (rise, setting) if daytime else (setting, following)
    step = (end - start) / 12
    index = int((t - start) // step)
    offset = index if daytime else index + 12
    ruler = ORDER[(ORDER.index(WEEKDAY[weekday]) + offset) % 7]
    return HourInterval('day' if daytime else 'night', index + 1, offset, ruler,
                        start + index * step, start + (index + 1) * step)


def _event(start: float, kind: int, latitude: float, longitude: float) -> float | None:
    """Caller owns native lock/init. Native -2 is absence, never a fatal error."""
    status, times = swe.rise_trans(start, swe.SUN, kind, (longitude, latitude, 0.0),
                                 1013.25, 15.0, swe.FLG_MOSEPH)
    if status == -2:
        return None
    if status != 0 or not isfinite(times[0]) or times[0] < start:
        raise TraditionalError('invalid_astronomical_result')
    return times[0]


def _events(t: float, latitude: float, longitude: float) -> SolarEvents:
    # Search for the opposite event after each result, never nudge a root by an
    # epsilon. Re-querying the same event at nextafter(root) can rediscover it
    # because the native search converges slightly differently from a new seed.
    def bounded(start: float, kind: int) -> float:
        if not t - 2 <= start <= t + 2:
            raise TraditionalError('solar_event_unavailable')
        value = _event(start, kind, latitude, longitude)
        if value is None or value > t + 2:
            raise TraditionalError('solar_event_unavailable')
        return value

    rise = bounded(t - 2, swe.CALC_RISE)
    for _ in range(5):
        setting = bounded(rise, swe.CALC_SET)
        following = bounded(setting, swe.CALC_RISE)
        r, s, n = map(Fraction, (rise, setting, following))
        if not (0 < s - r < 1 and 0 < n - s < 1):
            raise TraditionalError('solar_event_unavailable')
        if rise <= t < following:
            return SolarEvents(rise, setting, following)
        if t < rise:
            break
        rise = following
    raise TraditionalError('solar_event_unavailable')


def _local_sunrise_date(jd: float, zone: ZoneInfo) -> date:
    year, month, day, hour, minute, seconds = swe.jdut1_to_utc(jd, swe.GREG_CAL)
    if not isfinite(seconds) or not 0 <= seconds < 61:
        raise TraditionalError('invalid_astronomical_result')
    # Determine the civil date without rounding a pre-midnight instant forward.
    # Subsecond precision cannot affect ZoneInfo's whole-second transitions.
    utc = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
    return (utc + timedelta(seconds=int(seconds))).astimezone(zone).date()


def calculate_planetary_hour(instant: datetime, latitude: float, longitude: float,
                             timezone_id: str) -> PlanetaryHourResult:
    validate_utc(instant)
    if not (isfinite(latitude) and isfinite(longitude)
            and -90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise TraditionalError('invalid_coordinates')
    if not isinstance(timezone_id, str) or not timezone_id:
        raise TraditionalError('timezone_data_unavailable')
    try:
        zone = load_zone(timezone_id)
    except TimezoneError:
        raise TraditionalError('timezone_data_unavailable') from None
    with native._LOCK:
        try:
            native.initialize_ephemeris()
            _, t = julian_days(instant)
            events = _events(t, latitude, longitude)
            planetary_date = _local_sunrise_date(events.sunrise, zone)
            interval = classify_hour(t, events, planetary_date.weekday())
            return PlanetaryHourResult(interval, events, planetary_date, timezone_id,
                                       version('tzdata'), metadata())
        except (swe.Error, native.AstrologyError, ValueError, OverflowError):
            raise TraditionalError('ephemeris_error') from None
