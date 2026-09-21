"""Public Kamerî Code transport models; internal diagnostics stay private."""
from datetime import date
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError

from app.schemas.human_design import HumanDesignRequest
from app.schemas.numerology import NumerologyRequest


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False, from_attributes=True)


class KameriRequest(ContractModel):
    local_date: date
    utc_datetime: AwareDatetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone_id: str = Field(min_length=1, max_length=100)
    arabic_name: str = Field(min_length=1, max_length=200, repr=False)
    arabic_name_confirmed: Literal[True]

    @field_validator("local_date", mode="before")
    @classmethod
    def calendar_date_only(cls, value):
        value = NumerologyRequest.calendar_date_only(value)
        if not 1800 <= value.year <= 2100:
            raise PydanticCustomError("unsupported_date_range", "Supported years are 1800 through 2100.")
        return value

    @field_validator("utc_datetime", mode="before")
    @classmethod
    def utc_only(cls, value):
        return HumanDesignRequest.parse_datetime(value)


class AstronomyResponse(ContractModel):
    pyswisseph_version: str
    swiss_ephemeris_version: str
    ephemeris: str
    frame: str


class HijriResponse(ContractModel):
    hijri_year: int
    hijri_month: int
    hijri_day: int
    method_id: str
    method_version: str
    calendar_type: str
    classification: str
    day_boundary: str
    input_owner: str
    limitation: str


class MansionResponse(ContractModel):
    index: int
    method_id: str
    method_version: str
    mapping_kind: str
    classification: str
    rule_origin: str
    limitation: str


class LunarResponse(ContractModel):
    sun_longitude: float
    moon_longitude: float
    elongation: float
    illuminated_fraction: float
    phase: str
    mansion: MansionResponse
    astronomy: AstronomyResponse
    method_id: str
    method_version: str
    classification: str
    label_policy: str
    label_rule_origin: str
    limitation: str


class AbjadResponse(ContractModel):
    raw_sum: int
    method_id: str
    normalization_id: str
    method_version: str
    classification: str
    limitation: str


class PlanetaryHourIntervalResponse(ContractModel):
    period: Literal["day", "night"]
    hour: int
    total_offset: int
    ruler: str


class PlanetaryHourAssumptionsResponse(ContractModel):
    observer_height_m: float
    pressure_hpa: float
    temperature_c: float
    limb: str
    refraction: bool
    horizon: str


class PlanetaryHourResponse(ContractModel):
    interval: PlanetaryHourIntervalResponse
    planetary_date: date
    timezone_id: str
    method_id: str
    method_version: str
    classification: str
    event_classification: str
    rule_origin: str
    limitation: str
    assumptions: PlanetaryHourAssumptionsResponse


class KameriMetadataResponse(ContractModel):
    schema_version: Literal["kameri-code-v1"]
    calculation_layers: tuple[Literal["hijri"], Literal["lunar"], Literal["abjad"], Literal["planetary_hour"]]
    interpretation_present: Literal[False]


class KameriResponse(ContractModel):
    metadata: KameriMetadataResponse
    hijri: HijriResponse
    lunar: LunarResponse
    abjad: AbjadResponse
    planetary_hour: PlanetaryHourResponse


ErrorCode = Literal[
    "invalid_request", "invalid_calendar_date", "unsupported_date_range",
    "invalid_utc_datetime", "invalid_coordinates", "timezone_data_unavailable",
    "invalid_abjad_text", "unsupported_abjad_character", "ephemeris_error",
    "solar_event_unavailable", "invalid_astronomical_result",
]


class KameriErrorDetail(ContractModel):
    code: ErrorCode
    message: str


class KameriErrorResponse(ContractModel):
    detail: KameriErrorDetail
