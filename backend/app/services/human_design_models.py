"""Internal immutable HD astronomy values; not API schemas."""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Body = Literal['sun', 'earth', 'moon', 'north_node', 'south_node', 'mercury',
               'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
ErrorCode = Literal['invalid_utc_datetime', 'unsupported_date_range',
                    'ephemeris_error', 'design_moment_error', 'classification_error']


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


Center = Literal['head', 'ajna', 'throat', 'g', 'ego', 'sacral', 'solar_plexus', 'spleen', 'root']
HDType = Literal['generator', 'manifesting_generator', 'manifestor', 'projector', 'reflector']
Strategy = Literal['wait_to_respond', 'inform', 'wait_for_invitation', 'wait_lunar_cycle']
Authority = Literal['emotional', 'sacral', 'splenic', 'ego_manifested', 'ego_projected',
                    'self_projected', 'mental_environmental', 'lunar']
DefinitionKind = Literal['none', 'single', 'split', 'triple_split', 'quadruple_split']


@dataclass(frozen=True)
class Profile:
    personality_line: int
    design_line: int
    label: str


@dataclass(frozen=True)
class Mechanics:
    active_gates: tuple[int, ...]
    channels: tuple[tuple[int, int], ...]
    defined_centers: tuple[Center, ...]
    undefined_centers: tuple[Center, ...]
    type: HDType
    strategy: Strategy
    authority: Authority
    profile: Profile
    definition: DefinitionKind
    definition_components: tuple[tuple[Center, ...], ...]

    @property
    def component_count(self) -> int:
        return len(self.definition_components)


@dataclass(frozen=True)
class HumanDesignMetadata:
    pyswisseph_version: str
    swiss_ephemeris_version: str
    spec_revision: str = 'stage9a2-v1'
    ephemeris: str = 'moshier'
    zodiac: str = 'tropical'
    observer: str = 'geocentric'
    longitude_frame: str = 'apparent_ecliptic_of_date'
    node_algorithm: str = 'true_node'
    design_arc_degrees: float = 88.0
    solver_bracket_days: tuple[int, int] = (100, 80)
    solver_max_iterations: int = 64
    solver_max_bracket_seconds: float = 0.01
    solver_max_residual_degrees: float = 1e-7


@dataclass(frozen=True)
class HumanDesignResult(Mechanics):
    birth_utc: datetime
    astronomy: AstronomyResult
    metadata: HumanDesignMetadata
