from pydantic import BaseModel, ConfigDict, Field, field_validator


class LocationResolveRequest(BaseModel):
    """Location text as entered in the birth profile; it is never transliterated."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    country: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    district: str | None = Field(default=None, max_length=200)

    @field_validator("district", mode="before")
    @classmethod
    def empty_district_is_none(cls, value: str | None) -> str | None:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def query(self) -> str:
        return ", ".join(part for part in (self.district, self.city, self.country) if part)


class ResolvedLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(min_length=1, max_length=500)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=200)
    provider: str = Field(default="nominatim", min_length=1, max_length=50)


class LocationResolveResponse(BaseModel):
    resolved: bool = True
    location: ResolvedLocation
