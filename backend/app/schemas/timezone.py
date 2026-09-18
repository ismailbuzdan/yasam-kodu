from datetime import date, time
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator


class TimezoneRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    birth_date: date
    birth_time: time

    @field_validator("birth_time")
    @classmethod
    def local_wall_time(cls, value: time) -> time:
        if value.tzinfo is not None:
            raise ValueError("Yerel doğum saati UTC offset içermemelidir.")
        return value


class TimezoneCandidate(BaseModel):
    local_datetime: AwareDatetime
    utc_datetime: AwareDatetime
    utc_offset_minutes: float
    dst: bool
    fold: Literal[0, 1]


class TimezoneResponse(TimezoneCandidate):
    resolved: Literal[True] = True
    status: Literal["valid"] = "valid"
    timezone: str


class TimezoneErrorDetail(BaseModel):
    code: str
    message: str
    timezone: str | None = None
    candidates: list[TimezoneCandidate] = Field(default_factory=list)


class TimezoneErrorResponse(BaseModel):
    detail: TimezoneErrorDetail
