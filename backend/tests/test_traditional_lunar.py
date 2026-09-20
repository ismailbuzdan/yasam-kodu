from datetime import datetime, timezone, timedelta
from fractions import Fraction
from math import nextafter, inf, isfinite

import pytest
import swisseph as swe

from app.services.traditional import lunar
from app.services.traditional.models import TraditionalError

UTC = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
PHASES = ('new_moon', 'waxing_crescent', 'first_quarter', 'waxing_gibbous',
          'full_moon', 'waning_gibbous', 'last_quarter', 'waning_crescent')


@pytest.mark.parametrize('index', range(8))
def test_phase_boundary_neighbors(index):
    boundary = 22.5 + index * 45
    assert lunar.phase_for(nextafter(boundary, -inf)) == PHASES[index]
    assert lunar.phase_for(boundary) == PHASES[(index + 1) % 8]
    assert lunar.phase_for(nextafter(boundary, inf)) == PHASES[(index + 1) % 8]


@pytest.mark.parametrize('angle,label', [(0,'new_moon'),(90,'first_quarter'),
    (180,'full_moon'),(270,'last_quarter'),(360,'new_moon')])
def test_primary_angles(angle, label):
    assert lunar.phase_for(angle) == label


@pytest.mark.parametrize('index', range(1, 29))
def test_every_rational_mansion_boundary(index):
    boundary = Fraction(index * 90, 7)
    rounded = float(boundary)
    below = rounded if Fraction(rounded) < boundary else nextafter(rounded, -inf)
    above = rounded if Fraction(rounded) > boundary else nextafter(rounded, inf)
    assert Fraction(below) < boundary < Fraction(above)
    assert lunar.mansion_for(below).index == index
    if index < 28:
        assert lunar.mansion_for(above).index == index + 1
        expected = index if Fraction(rounded) < boundary else index + 1
        assert lunar.mansion_for(rounded).index == expected
    else:
        assert lunar.mansion_for(rounded).index == 1


@pytest.mark.parametrize('value,index', [(0,1),(90,8),(180,15),(270,22),(360,1)])
def test_mansion_anchors(value, index):
    assert lunar.mansion_for(value).index == index


@pytest.mark.parametrize('value', [-1, nextafter(0.0, -inf), inf, -inf, float('nan'), 361])
@pytest.mark.parametrize('mapper', [lunar.phase_for, lunar.mansion_for])
def test_mapper_fail_fast(value, mapper):
    with pytest.raises(TraditionalError, match='invalid_astronomical_result'):
        mapper(value)


def test_native_repeatability_metadata_and_same_instant():
    first = lunar.calculate_lunar(UTC)
    for value in (UTC, datetime.fromisoformat('2000-01-01T12:00:00Z'),
                  datetime.fromisoformat('2000-01-01T12:00:00+00:00')):
        assert lunar.calculate_lunar(value) == first
    assert all(isfinite(v) for v in (first.sun_longitude, first.moon_longitude, first.illuminated_fraction))
    assert 0 <= first.illuminated_fraction <= 1
    assert first.mansion == lunar.mansion_for(first.moon_longitude)
    assert first.metadata.pyswisseph_version == '2.10.3.2'


def test_pheno_uses_tt_moshier_not_elongation_approximation(monkeypatch):
    calls = []
    original = swe.pheno
    def probe(jd, body, flags):
        calls.append((jd, body, flags))
        return original(jd, body, flags)
    monkeypatch.setattr(swe, 'pheno', probe)
    lunar.calculate_lunar(UTC)
    assert calls == [(swe.utc_to_jd(2000,1,1,12,0,0)[0], swe.MOON, swe.FLG_MOSEPH)]


@pytest.mark.parametrize('value', [float('nan'), -0.1, 1.1])
def test_invalid_illumination(monkeypatch, value):
    monkeypatch.setattr(swe, 'pheno', lambda *args: (0, value))
    with pytest.raises(TraditionalError, match='invalid_astronomical_result'):
        lunar.calculate_lunar(UTC)


def test_native_failure_private(monkeypatch):
    def fail(*args):
        raise swe.Error('secret native diagnostic')
    monkeypatch.setattr(swe, 'calc', fail)
    with pytest.raises(TraditionalError, match='ephemeris_error') as error:
        lunar.calculate_lunar(UTC)
    assert error.value.__suppress_context__
    assert 'secret' not in str(error.value)


@pytest.mark.parametrize('value,code', [(datetime(2000,1,1),'invalid_utc_datetime'),
    (UTC.replace(tzinfo=timezone(timedelta(hours=1))),'invalid_utc_datetime'),
    (UTC.replace(year=1799),'unsupported_date_range'), (UTC.replace(year=2101),'unsupported_date_range')])
def test_utc_and_range(value, code):
    with pytest.raises(TraditionalError, match=code):
        lunar.calculate_lunar(value)


@pytest.mark.parametrize('year', [1800, 2100])
def test_supported_native_endpoints(year):
    assert 0 <= lunar.calculate_lunar(UTC.replace(year=year)).moon_longitude < 360


@pytest.mark.parametrize('flags', [0, swe.FLG_SWIEPH, lunar.native.FLAGS | swe.FLG_TOPOCTR])
def test_unexpected_native_flags(monkeypatch, flags):
    monkeypatch.setattr(swe, 'calc', lambda *args: ((1,2,3,4,5,6), flags))
    with pytest.raises(TraditionalError, match='invalid_astronomical_result'):
        lunar.calculate_lunar(UTC)


def test_illumination_is_native_return_not_formula(monkeypatch):
    monkeypatch.setattr(swe, 'pheno', lambda *args: (0, 0.1234567))
    assert lunar.calculate_lunar(UTC).illuminated_fraction == 0.1234567


def test_native_calls_are_initialized_under_shared_lock(monkeypatch):
    events = []
    initializer = lunar.native.initialize_ephemeris
    original = swe.calc
    def initialize():
        assert lunar.native._LOCK._is_owned()
        events.append('init')
        initializer()
    def calc(*args):
        assert lunar.native._LOCK._is_owned() and events == ['init']
        return original(*args)
    monkeypatch.setattr(lunar.native, 'initialize_ephemeris', initialize)
    monkeypatch.setattr(swe, 'calc', calc)
    lunar.calculate_lunar(UTC)


def test_invalid_julian_day(monkeypatch):
    monkeypatch.setattr(swe, 'utc_to_jd', lambda *args: (float('nan'), 2451545.0))
    with pytest.raises(TraditionalError, match='invalid_astronomical_result'):
        lunar.calculate_lunar(UTC)


def test_external_ephemeris_environment_is_rejected(monkeypatch):
    monkeypatch.setenv('SE_EPHE_PATH', 'untrusted')
    with pytest.raises(TraditionalError, match='ephemeris_error'):
        lunar.calculate_lunar(UTC)
