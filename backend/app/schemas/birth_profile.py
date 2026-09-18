from datetime import date, time
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class TimeAccuracy(StrEnum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    UNKNOWN = "unknown"


class BirthProfile(BaseModel):
    """Validated birth information. This model is not persisted in this phase."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    birth_date: date
    country: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    district: str | None = Field(default=None, max_length=200)
    time_accuracy: TimeAccuracy
    birth_time: time | None = Field(default=None, validate_default=True)
    approximate_start_time: time | None = Field(default=None, validate_default=True)
    approximate_end_time: time | None = Field(default=None, validate_default=True)

    @field_validator("birth_date")
    @classmethod
    def birth_date_cannot_be_in_the_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Doğum tarihi gelecekte olamaz.")
        return value

    @field_validator("district", mode="before")
    @classmethod
    def normalize_empty_district(cls, value: str | None) -> str | None:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("birth_time")
    @classmethod
    def validate_birth_time(cls, value: time | None, info) -> time | None:
        accuracy = info.data.get("time_accuracy")
        if accuracy is TimeAccuracy.EXACT and value is None:
            raise ValueError("Kesin doğum saati zorunludur.")
        if accuracy is not TimeAccuracy.EXACT and value is not None:
            raise ValueError("Doğum saati yalnızca kesin saat seçiminde gönderilebilir.")
        return value

    @field_validator("approximate_start_time")
    @classmethod
    def validate_approximate_start_time(cls, value: time | None, info) -> time | None:
        accuracy = info.data.get("time_accuracy")
        if accuracy is TimeAccuracy.APPROXIMATE and value is None:
            raise ValueError("Tahmini başlangıç saati zorunludur.")
        if accuracy is not TimeAccuracy.APPROXIMATE and value is not None:
            raise ValueError("Tahmini başlangıç saati yalnızca yaklaşık saat seçiminde gönderilebilir.")
        return value

    @field_validator("approximate_end_time")
    @classmethod
    def validate_approximate_end_time(cls, value: time | None, info) -> time | None:
        accuracy = info.data.get("time_accuracy")
        start_time = info.data.get("approximate_start_time")
        if accuracy is TimeAccuracy.APPROXIMATE and value is None:
            raise ValueError("Tahmini bitiş saati zorunludur.")
        if accuracy is not TimeAccuracy.APPROXIMATE and value is not None:
            raise ValueError("Tahmini bitiş saati yalnızca yaklaşık saat seçiminde gönderilebilir.")
        if value is not None and start_time is not None and start_time > value:
            raise ValueError("Başlangıç saati bitiş saatinden büyük olamaz.")
        return value

    @field_serializer("birth_time", "approximate_start_time", "approximate_end_time")
    def serialize_time(self, value: time | None) -> str | None:
        return value.strftime("%H:%M") if value is not None else None


class BirthProfileValidationResponse(BaseModel):
    valid: bool = True
    profile: BirthProfile
