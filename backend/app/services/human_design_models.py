"""Internal immutable HD astronomy values; not API schemas."""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Body = Literal['sun', 'earth', 'moon', 'north_node', 'south_node', 'mercury',
               'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
ErrorCode = Literal['invalid_utc_datetime', 'unsupported_date_range',
                    'ephemeris_error', 'design_moment_error']


class HumanDesignError(Exception):
    def __init__(self, code: ErrorCode, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Activation:
    body: Body
    longitude: float
    gate: int
    line: int


@dataclass(frozen=True)
class DesignMoment:
    jd_ut1: float
    bracket_seconds: float
    residual_degrees: float
    iterations: int


@dataclass(frozen=True)
class AstronomyResult:
    personality_jd_ut1: float
    design: DesignMoment
    design_utc: datetime
    personality: tuple[Activation, ...]
    design_activations: tuple[Activation, ...]
