"""Public aggregation contract composing the existing engine response schemas."""
from datetime import date
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StrictInt, field_validator

from app.schemas.astrology import AstrologyResponse
from app.schemas.human_design import HumanDesignRequest, HumanDesignResponse
from app.schemas.numerology import NumerologyRequest, NumerologyResponse


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False, from_attributes=True)


class LifeCodeRequest(ContractModel):
    full_name: str = Field(min_length=1, max_length=200, repr=False)
    birth_date: date
    utc_datetime: AwareDatetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    target_year: StrictInt | None = Field(default=None, ge=1, le=9999)

    @field_validator("birth_date", mode="before")
    @classmethod
    def calendar_date_only(cls, value):
        return NumerologyRequest.calendar_date_only(value)

    @field_validator("utc_datetime", mode="before")
    @classmethod
    def utc_only(cls, value):
        # Reuse the standalone HD input grammar and 1800–2100 support boundary.
        return HumanDesignRequest.parse_datetime(value)


class LifeCodeMetadataResponse(ContractModel):
    schema_version: Literal["life-code-v1"]
    calculation_layers: tuple[Literal["astrology"], Literal["numerology"], Literal["human_design"]]
    interpretation_present: Literal[False]


class LifeCodeResponse(ContractModel):
    metadata: LifeCodeMetadataResponse
    astrology: AstrologyResponse
    numerology: NumerologyResponse
    human_design: HumanDesignResponse


ErrorCode = Literal["invalid_request", "invalid_name", "unsupported_name_characters",
                    "invalid_birth_date", "invalid_target_year", "invalid_utc_datetime",
                    "invalid_coordinates", "unsupported_date_range", "ephemeris_error",
                    "house_calculation_error", "design_moment_error", "classification_error"]


class LifeCodeErrorDetail(ContractModel):
    code: ErrorCode
    message: str


class LifeCodeErrorResponse(ContractModel):
    detail: LifeCodeErrorDetail
