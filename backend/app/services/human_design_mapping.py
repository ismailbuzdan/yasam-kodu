"""ADR-015 project wheel, independently encoded; no research/runtime I/O."""
from fractions import Fraction
from math import isfinite

from app.services.human_design_models import HumanDesignError

GATE_SEQUENCE = (
    41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3,
    27, 24, 2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56,
    31, 33, 7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50,
    28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60,
)


def gate_line(longitude: float) -> tuple[int, int]:
    if not isfinite(longitude):
        raise HumanDesignError('ephemeris_error', 'Nonfinite longitude.')
    # Normalize/subtract EXACTLY, before any binary64 rounding near boundaries.
    offset = (Fraction(longitude) - 302) % 360
    cell = int(offset // Fraction(15, 16))
    return GATE_SEQUENCE[cell // 6], cell % 6 + 1
