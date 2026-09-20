from datetime import date, datetime, timedelta

import pytest

from app.services.traditional.hijri import calculate_hijri, _from_jdn, _to_jdn
from app.services.traditional.models import TraditionalError


def triple(result):
    return result.hijri_year, result.hijri_month, result.hijri_day


def test_epoch():
    assert date(622, 7, 19).toordinal() + 1721425 == 1948440
    assert triple(_from_jdn(1948440)) == (1, 1, 1)
    assert _to_jdn(1, 1, 1) == 1948440


@pytest.mark.parametrize('year', range(1, 31))
def test_all_cycle_years_and_month_boundaries(year):
    leap = year in {2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29}
    assert _to_jdn(year + 1, 1, 1) - _to_jdn(year, 1, 1) == 354 + leap
    for month in range(1, 13):
        length = 30 if month % 2 or (month == 12 and leap) else 29
        start = _to_jdn(year, month, 1)
        assert triple(_from_jdn(start)) == (year, month, 1)
        assert triple(_from_jdn(start + length - 1)) == (year, month, length)
        following = (year, month + 1, 1) if month < 12 else (year + 1, 1, 1)
        assert triple(_from_jdn(start + length)) == following


def test_full_supported_range_roundtrip_and_consecutive_calendar():
    first, last = date(1800, 1, 1), date(2100, 12, 31)
    prior = None
    for ordinal in range(first.toordinal(), last.toordinal() + 1):
        actual = calculate_hijri(date.fromordinal(ordinal))
        y, m, d = triple(actual)
        assert _to_jdn(y, m, d) == ordinal + 1721425
        assert 1 <= m <= 12 and 1 <= d <= 30
        if prior:
            py, pm, pd = prior
            assert ((y, m) == (py, pm) and d == pd + 1) or (
                d == 1 and pd in (29, 30) and
                ((y == py and m == pm + 1) or (y == py + 1 and pm == 12 and m == 1)))
        prior = y, m, d


@pytest.mark.parametrize('year,length', [(1800, 1), (1900, 1), (2000, 2), (2100, 1)])
def test_gregorian_century_boundary(year, length):
    first = calculate_hijri(date(year, 2, 28))
    last = calculate_hijri(date(year, 3, 1))
    assert _to_jdn(*triple(last)) - _to_jdn(*triple(first)) == length


@pytest.mark.parametrize('value,code', [
    (date(1799, 12, 31), 'unsupported_date_range'),
    (date(2101, 1, 1), 'unsupported_date_range'),
    (datetime(2000, 1, 1), 'invalid_calendar_date'),
    ('2000-01-01', 'invalid_calendar_date'), (None, 'invalid_calendar_date')])
def test_invalid_date(value, code):
    with pytest.raises(TraditionalError) as error:
        calculate_hijri(value)
    assert error.value.code == code
