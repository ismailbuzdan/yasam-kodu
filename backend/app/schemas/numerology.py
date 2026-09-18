from datetime import date
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator


class NumerologyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str = Field(strict=True, min_length=1, max_length=200)
    birth_date: date
    target_year: StrictInt | None = Field(default=None, ge=1, le=9999)

    @field_validator("birth_date", mode="before")
    @classmethod
    def calendar_date_only(cls, value):
        if type(value) is date:
            return value
        if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            raise ValueError("YYYY-MM-DD biçiminde doğum tarihi gereklidir.")
        return date.fromisoformat(value)


class NumerologyNumber(BaseModel):
    raw_sum: int = Field(ge=0)
    value: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33]
    is_master: bool


class NumerologyMetadata(BaseModel):
    system: Literal["pythagorean"] = "pythagorean"
    master_numbers: tuple[int, ...]
    vowels: Literal["AEIOU"] = "AEIOU"
    y_is_vowel: Literal[False] = False
    target_year: int | None


class NumerologyResponse(BaseModel):
    metadata: NumerologyMetadata
    life_path: NumerologyNumber
    birthday: NumerologyNumber
    expression: NumerologyNumber
    soul_urge: NumerologyNumber | None
    personality: NumerologyNumber | None
    maturity: NumerologyNumber
    personal_year: NumerologyNumber | None


class NumerologyErrorDetail(BaseModel):
    code: Literal["invalid_name", "unsupported_name_characters", "invalid_birth_date",
                  "invalid_target_year", "invalid_request"]
    message: str


class NumerologyErrorResponse(BaseModel):
    detail: NumerologyErrorDetail
