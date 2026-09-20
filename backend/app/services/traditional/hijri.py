"""Independent integer implementation of ADR-017's date correspondence."""
from datetime import date

from .models import HijriResult, TraditionalError

EPOCH_JDN = 1948440


def _year_start(year: int) -> int:
    return EPOCH_JDN + 354 * (year - 1) + (3 + 11 * year) // 30


def _to_jdn(year: int, month: int, day: int) -> int:
    """Private inverse for already valid positive AH triples."""
    return _year_start(year) + 29 * (month - 1) + month // 2 + day - 1


def _from_jdn(jdn: int) -> HijriResult:
    year = max(1, (jdn - EPOCH_JDN) // 355 + 1)
    while _year_start(year + 1) <= jdn:
        year += 1
    month = 1
    while month < 12 and _to_jdn(year, month + 1, 1) <= jdn:
        month += 1
    return HijriResult(year, month, jdn - _to_jdn(year, month, 1) + 1)


def calculate_hijri(local_date: date) -> HijriResult:
    # A datetime is intentionally not a date-only input, even though it subclasses date.
    if type(local_date) is not date:
        raise TraditionalError('invalid_calendar_date')
    if not 1800 <= local_date.year <= 2100:
        raise TraditionalError('unsupported_date_range')
    # stdlib ordinal is proleptic Gregorian integer arithmetic, never UTC/JD rounding.
    return _from_jdn(local_date.toordinal() + 1721425)
