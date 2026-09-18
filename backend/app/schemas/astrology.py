from datetime import datetime, timedelta
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator


class AstrologyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    utc_datetime: AwareDatetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    house_system: Literal["placidus"] = "placidus"

    @field_validator("utc_datetime", mode="before")
    @classmethod
    def datetime_only(cls, value):
        if not isinstance(value, (str, datetime)):
            raise ValueError("ISO 8601 UTC datetime is required.")
        return value

    @field_validator("utc_datetime")
    @classmethod
    def utc_only(cls, value: datetime) -> datetime:
        if value.utcoffset() != timedelta(0):
            raise ValueError("UTC offset must be zero.")
        return value


class Position(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    longitude: float = Field(ge=0, lt=360)
    sign: Literal["aries", "taurus", "gemini", "cancer", "leo", "virgo",
                  "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
    degree_in_sign: float = Field(ge=0, lt=30)


class BodyPosition(Position):
    speed_longitude: float
    retrograde: bool
    house: int = Field(ge=1, le=12)


class HouseCusp(Position):
    house: int = Field(ge=1, le=12)


class Aspect(BaseModel):
    body1: str
    body2: str
    type: Literal["conjunction", "sextile", "square", "trine", "opposition"]
    exact_angle: float
    separation: float = Field(ge=0, le=180)
    orb: float = Field(ge=0)
    applying: None = None


class AstrologyMetadata(BaseModel):
    system: Literal["tropical"] = "tropical"
    house_system: Literal["placidus"] = "placidus"
    node_type: Literal["true"] = "true"
    lilith_type: Literal["mean_black_moon"] = "mean_black_moon"
    ephemeris: Literal["moshier"] = "moshier"
    pyswisseph_version: str
    swiss_ephemeris_version: str
    house_placement: Literal["swiss_house_pos_longitude_latitude"] = "swiss_house_pos_longitude_latitude"


class AstrologyResponse(BaseModel):
    metadata: AstrologyMetadata
    bodies: dict[str, BodyPosition]
    ascendant: Position
    mc: Position
    houses: list[HouseCusp] = Field(min_length=12, max_length=12)
    aspects: list[Aspect]


class AstrologyErrorDetail(BaseModel):
    code: Literal["invalid_utc_datetime", "invalid_coordinates", "ephemeris_error",
                  "house_calculation_error", "unsupported_house_system", "invalid_request"]
    message: str


class AstrologyErrorResponse(BaseModel):
    detail: AstrologyErrorDetail
