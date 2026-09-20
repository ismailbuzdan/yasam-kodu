from datetime import date, datetime, timezone
from fractions import Fraction
from math import nextafter, inf

import pytest
import swisseph as swe

from app.services.traditional import planetary_hours as hours
from app.services.traditional.models import SolarEvents, TraditionalError

UTC = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
# 9h daylight, 9h night, each hour 3/4h: all subdivision points binary-exact.
EVENTS = SolarEvents(2451545.0, 2451545.375, 2451545.75)
ORDER = ('saturn','jupiter','mars','sun','venus','mercury','moon')


@pytest.mark.parametrize('weekday,start', list(enumerate(('moon','mars','mercury','jupiter','venus','saturn','sun'))))
@pytest.mark.parametrize('offset', range(24))
def test_all_hours_all_weekdays_exact_and_adjacent(weekday, start, offset):
    boundary = 2451545.0 + offset / 32
    result = hours.classify_hour(boundary, EVENTS, weekday)
    assert result.total_offset == offset
    assert result.hour == offset % 12 + 1
    assert result.period == ('day' if offset < 12 else 'night')
    assert result.ruler == ORDER[(ORDER.index(start) + offset) % 7]
    assert result.start_jd_ut1 == Fraction(boundary)
    assert result.end_jd_ut1 == Fraction(boundary) + Fraction(1, 32)
    assert hours.classify_hour(nextafter(boundary, inf), EVENTS, weekday) == result
    if offset:
        assert hours.classify_hour(nextafter(boundary, -inf), EVENTS, weekday).total_offset == offset - 1
    else:
        with pytest.raises(TraditionalError, match='solar_event_unavailable'):
            hours.classify_hour(nextafter(boundary, -inf), EVENTS, weekday)


def test_nonrepresentable_subdivision_no_rounded_membership():
    events = SolarEvents(2451545.0, 2451545.5, 2451546.0)
    for index in range(1, 24):
        exact = Fraction(2451545) + Fraction(index, 24)
        rounded = float(exact)
        expected = index - (Fraction(rounded) < exact)
        assert hours.classify_hour(rounded, events, 0).total_offset == expected


@pytest.mark.parametrize('events,t', [
    (EVENTS, EVENTS.next_sunrise),
    (SolarEvents(0, 0, 1), 0), (SolarEvents(0, 1, 1.5), 0),
    (SolarEvents(0, .5, 1.5), .5), (SolarEvents(1, .5, 2), 1),
    (SolarEvents(0, .5, .4), .1)])
def test_unavailable_intervals(events, t):
    with pytest.raises(TraditionalError, match='solar_event_unavailable'):
        hours.classify_hour(t, events, 0)


@pytest.mark.parametrize('value', [inf, -inf, float('nan')])
def test_nonfinite(value):
    with pytest.raises(TraditionalError, match='invalid_astronomical_result'):
        hours.classify_hour(value, EVENTS, 0)


def test_real_pre_sunrise_and_day_ownership():
    result = hours.calculate_planetary_hour(UTC.replace(hour=0), 40, 30, 'Europe/Istanbul')
    assert result.planetary_date == date(1999, 12, 31)
    assert result.interval.period == 'night'
    assert result.assumptions.pressure_hpa == 1013.25


@pytest.mark.parametrize('timestamp,zone,expected', [
    ('2000-01-01T23:30:00+00:00', 'Pacific/Kiritimati', date(2000,1,2)),
    ('2020-03-08T06:59:59+00:00', 'America/New_York', date(2020,3,8)),
    ('2020-03-08T07:00:00+00:00', 'America/New_York', date(2020,3,8)),
    ('1900-01-01T22:05:00+00:00', 'Europe/Istanbul', date(1900,1,2)),
    ('1900-01-01T22:03:00+00:00', 'Europe/Istanbul', date(1900,1,1))])
def test_r0_local_date_utc_difference_dst_and_historical(timestamp, zone, expected):
    dt = datetime.fromisoformat(timestamp)
    with hours.native._LOCK:
        hours.native.initialize_ephemeris()
        _, jd = hours.julian_days(dt)
        assert hours._local_sunrise_date(jd, hours.load_zone(zone)) == expected


def test_event_local_date_does_not_round_across_midnight(monkeypatch):
    monkeypatch.setattr(swe, 'jdut1_to_utc', lambda *args: (2000,1,1,23,59,59.9999999))
    assert hours._local_sunrise_date(0, hours.load_zone('UTC')) == date(2000,1,1)


@pytest.mark.parametrize('month', [1, 6, 12])
@pytest.mark.parametrize('latitude', [-90, 90])
def test_real_polar_absence(month, latitude):
    with pytest.raises(TraditionalError, match='solar_event_unavailable'):
        hours.calculate_planetary_hour(UTC.replace(month=month), latitude, 0, 'UTC')


def test_native_arguments_and_shared_lock(monkeypatch):
    original = swe.rise_trans
    calls = []
    def probe(*args):
        assert hours.native._LOCK._is_owned()
        calls.append(args)
        return original(*args)
    monkeypatch.setattr(swe, 'rise_trans', probe)
    hours.calculate_planetary_hour(UTC, 40, 30, 'Europe/Istanbul')
    assert calls
    for start, body, kind, geo, pressure, temperature, flags in calls:
        assert body == swe.SUN and kind in (swe.CALC_RISE, swe.CALC_SET)
        assert geo == (30,40,0) and (pressure, temperature) == (1013.25,15)
        assert flags == swe.FLG_MOSEPH
        assert 2451543 <= start <= 2451547.001


@pytest.mark.parametrize('status,code', [(-2,'solar_event_unavailable'),(-1,'invalid_astronomical_result')])
def test_status_errors(monkeypatch, status, code):
    monkeypatch.setattr(swe, 'rise_trans', lambda *args: (status, (0,)))
    with pytest.raises(TraditionalError, match=code):
        hours.calculate_planetary_hour(UTC,40,30,'UTC')


def test_native_failure_not_no_event(monkeypatch):
    def fail(*args):
        raise swe.Error('private native error')
    monkeypatch.setattr(swe, 'rise_trans', fail)
    with pytest.raises(TraditionalError, match='ephemeris_error') as error:
        hours.calculate_planetary_hour(UTC,40,30,'UTC')
    assert error.value.__suppress_context__ and 'private' not in str(error.value)


@pytest.mark.parametrize('lat,lon', [(91,0),(0,181),(float('nan'),0),(0,inf)])
def test_coordinate_admission(lat, lon):
    with pytest.raises(TraditionalError, match='invalid_coordinates'):
        hours.calculate_planetary_hour(UTC,lat,lon,'UTC')


@pytest.mark.parametrize('zone', ['', 'Missing/Zone', '../UTC', None])
def test_zone_admission(zone):
    with pytest.raises(TraditionalError, match='timezone_data_unavailable'):
        hours.calculate_planetary_hour(UTC,40,30,zone)


@pytest.mark.parametrize('t,expected', [(10.0, 10.0), (10.5,10.0), (11.0,11.0)])
def test_search_exact_rise_set_ownership_without_epsilon(monkeypatch, t, expected):
    def event(start, kind, lat, lon):
        values = (8.0,9.0,10.0,11.0,12.0,13.0) if kind == swe.CALC_RISE else (8.5,9.5,10.5,11.5,12.5,13.5)
        return next((v for v in values if v >= start), None)
    monkeypatch.setattr(hours, '_event', event)
    result = hours._events(t,0,0)
    assert result.sunrise == expected
    classified = hours.classify_hour(t,result,0)
    assert classified.hour == 1
    assert classified.period == ('night' if t == 10.5 else 'day')


@pytest.mark.parametrize('result', [float('nan'), float('inf'), 0.0])
def test_invalid_native_event_results(monkeypatch, result):
    monkeypatch.setattr(swe, 'rise_trans', lambda *args: (0, (result,)))
    with pytest.raises(TraditionalError, match='invalid_astronomical_result'):
        hours.calculate_planetary_hour(UTC,40,30,'UTC')


def test_search_does_not_accept_far_events(monkeypatch):
    calls = []
    def event(start, *args):
        calls.append(start)
        return start + 100
    monkeypatch.setattr(hours, '_event', event)
    with pytest.raises(TraditionalError, match='solar_event_unavailable'):
        hours._events(1000,0,0)
    assert calls == [998]


def test_disallowed_day_duration(monkeypatch):
    monkeypatch.setattr(hours, '_event', lambda start, *args: start + 1)
    with pytest.raises(TraditionalError, match='solar_event_unavailable'):
        hours._events(1000,0,0)


@pytest.mark.parametrize('weekday', [-1,7,1.5,True])
def test_invalid_weekday(weekday):
    with pytest.raises(TraditionalError, match='invalid_astronomical_result'):
        hours.classify_hour(EVENTS.sunrise,EVENTS,weekday)


@pytest.mark.parametrize('year', [1800,2100])
def test_planetary_hour_supported_endpoints(year):
    result = hours.calculate_planetary_hour(UTC.replace(year=year),40,30,'Europe/Istanbul')
    assert result.planetary_date == date(year,1,1)
