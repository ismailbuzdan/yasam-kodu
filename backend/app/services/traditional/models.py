"""Immutable internal values. No submitted script or interpretive output."""
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from typing import Literal

ErrorCode = Literal['unsupported_date_range', 'invalid_calendar_date',
    'invalid_utc_datetime', 'invalid_coordinates', 'timezone_data_unavailable',
    'invalid_abjad_text', 'unsupported_abjad_character', 'ephemeris_error',
    'solar_event_unavailable', 'invalid_astronomical_result']


class TraditionalError(Exception):
    def __init__(self, code: ErrorCode):
        # Fixed, input-independent diagnostics; native exceptions are suppressed.
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class HijriResult:
    hijri_year: int
    hijri_month: int
    hijri_day: int
    method_id: str = 'hijri_tabular_civil_friday_v1'
    method_version: str = '1'
    calendar_type: str = 'tabular_civil'
    classification: str = 'CALCULATED_CALENDAR'
    epoch_jdn: int = 1948440
    leap_cycle: tuple[int, ...] = (2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29)
    day_boundary: str = 'local_civil_midnight'
    input_owner: str = 'supplied_local_gregorian_date'
    supported_years: tuple[int, int] = (1800, 2100)
    source_ids: tuple[str, ...] = ('CAL-01', 'CAL-02')
    limitation: str = 'Calculated correspondence; not an observed or proclaimed calendar.'


@dataclass(frozen=True)
class MansionResult:
    index: int
    method_id: str = 'mansion_equal28_tropical_v1'
    method_version: str = '1'
    mapping_kind: str = 'equal_ecliptic_sectors'
    classification: str = 'CALCULATED_SYMBOLIC'
    rule_origin: str = 'PROJECT_CONVENTION'
    source_ids: tuple[str, ...] = ('ADR-017',)
    limitation: str = 'Numeric tropical sectors, not historical stellar mansions.'


Phase = Literal['new_moon', 'waxing_crescent', 'first_quarter', 'waxing_gibbous',
                'full_moon', 'waning_gibbous', 'last_quarter', 'waning_crescent']
Planet = Literal['saturn', 'jupiter', 'mars', 'sun', 'venus', 'mercury', 'moon']


@dataclass(frozen=True)
class AstronomyMetadata:
    pyswisseph_version: str
    swiss_ephemeris_version: str
    ephemeris: str = 'moshier'
    frame: str = 'apparent_geocentric_tropical_ecliptic_of_date'
    time_model: str = 'Swiss utc_to_jd; automatic delta-T and tidal acceleration'
    source_ids: tuple[str, ...] = ('AST-01', 'AST-02', 'ADR-017')


@dataclass(frozen=True)
class LunarResult:
    sun_longitude: float
    moon_longitude: float
    elongation: float
    illuminated_fraction: float
    phase: Phase
    mansion: MansionResult
    metadata: AstronomyMetadata
    method_id: str = 'moon_apparent_geocentric_v1'
    method_version: str = '1'
    classification: str = 'CALCULATED_ASTRONOMICAL'
    label_policy: str = 'phase_bins_8_centered_v1'
    label_rule_origin: str = 'PROJECT_CONVENTION'
    position_flags: int = 260
    phenomena_flags: int = 4
    native_timescale: str = 'TT'
    limitation: str = 'Modeled disk fraction; phase bin is not an exact phase event.'


@dataclass(frozen=True)
class AbjadResult:
    raw_sum: int
    unicode_version: str
    method_id: str = 'abjad_mashriqi_kabir_v1'
    normalization_id: str = 'abjad_text_v1'
    method_version: str = '1'
    classification: str = 'CALCULATED_SYMBOLIC'
    source_ids: tuple[str, ...] = ('ABJ-01', 'ABJ-02', 'TXT-01', 'ADR-017')
    limitation: str = 'Selected written-letter sum; no interpretation or reduction.'


@dataclass(frozen=True)
class SolarEvents:
    sunrise: float
    sunset: float
    next_sunrise: float


@dataclass(frozen=True)
class HourInterval:
    period: Literal['day', 'night']
    hour: int
    total_offset: int
    ruler: Planet
    start_jd_ut1: Fraction
    end_jd_ut1: Fraction


@dataclass(frozen=True)
class HourAssumptions:
    observer_height_m: float = 0.0
    pressure_hpa: float = 1013.25
    temperature_c: float = 15.0
    limb: str = 'upper'
    refraction: bool = True
    horizon: str = 'unobstructed_level'
    search_hours_each_direction: int = 48


@dataclass(frozen=True)
class PlanetaryHourResult:
    interval: HourInterval
    events: SolarEvents
    planetary_date: date
    timezone_id: str
    tzdata_version: str
    metadata: AstronomyMetadata
    assumptions: HourAssumptions = HourAssumptions()
    method_id: str = 'planetary_hours_seasonal_v1'
    method_version: str = '1'
    classification: str = 'CALCULATED_SYMBOLIC'
    event_classification: str = 'CALCULATED_ASTRONOMICAL'
    event_ephemeris_flags: int = 4
    event_timescale: str = 'UT1'
    rule_origin: str = 'PROJECT_CONVENTION'
    source_ids: tuple[str, ...] = ('HOUR-01', 'HOUR-02', 'AST-01', 'TRAD-03', 'ADR-017')
    limitation: str = 'Fixed atmosphere and level horizon; no terrain or polar substitution.'
