"""Explicit HD transport models; no calculation or internal solver diagnostics."""
from datetime import datetime, timedelta
import re
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError

from app.services.human_design_models import Authority, Body, Center, DefinitionKind, HDType, Strategy


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False, from_attributes=True)


class HumanDesignRequest(ContractModel):
    utc_datetime: AwareDatetime

    @field_validator("utc_datetime", mode="before")
    @classmethod
    def parse_datetime(cls, value):
        if isinstance(value, str):
            # Calendar date + time only: no epoch coercion or silent sub-microsecond truncation.
            if not re.fullmatch(
                r"[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt ][0-9]{2}:[0-9]{2}"
                r"(?::[0-9]{2}(?:[.,][0-9]{1,6})?)?(?:[Zz]|[+-][0-9]{2}:?[0-9]{2})",
                value,
            ):
                raise ValueError("An ISO 8601 UTC datetime is required.")
            value = datetime.fromisoformat(value.upper().replace("Z", "+00:00"))
        if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
            raise ValueError("An aware zero-offset datetime is required.")
        if not 1800 <= value.year <= 2100:
            raise PydanticCustomError("unsupported_date_range", "Supported years are 1800 through 2100.")
        return value


Gate = Annotated[int, Field(ge=1, le=64)]
Line = Annotated[int, Field(ge=1, le=6)]


class HumanDesignActivation(ContractModel):
    body: Body
    longitude: float = Field(ge=0, lt=360)
    gate: Gate
    line: Line


class HumanDesignProfile(ContractModel):
    personality_line: Line
    design_line: Line
    label: Literal["1/3", "1/4", "2/4", "2/5", "3/5", "3/6",
                   "4/6", "4/1", "5/1", "5/2", "6/2", "6/3"]


class HumanDesignMetadata(ContractModel):
    spec_revision: Literal["stage9a2-v1"]
    pyswisseph_version: str
    swiss_ephemeris_version: str
    ephemeris: Literal["moshier"]
    zodiac: Literal["tropical"]
    observer: Literal["geocentric"]
    longitude_frame: Literal["apparent_ecliptic_of_date"]
    node_algorithm: Literal["true_node"]
    design_arc_degrees: Literal[88.0]
    # Reproducible algorithm settings, not per-request convergence diagnostics.
    solver_bracket_days: tuple[Literal[100], Literal[80]]
    solver_max_iterations: Literal[64]
    solver_max_bracket_seconds: Literal[0.01]
    solver_max_residual_degrees: Literal[1e-7]


class HumanDesignResponse(ContractModel):
    metadata: HumanDesignMetadata
    birth_utc: AwareDatetime
    design_utc: AwareDatetime
    personality: tuple[HumanDesignActivation, ...] = Field(min_length=13, max_length=13)
    design: tuple[HumanDesignActivation, ...] = Field(min_length=13, max_length=13)
    active_gates: tuple[Gate, ...]
    channels: tuple[tuple[Gate, Gate], ...]
    defined_centers: tuple[Center, ...]
    undefined_centers: tuple[Center, ...]
    type: HDType
    strategy: Strategy
    authority: Authority
    profile: HumanDesignProfile
    definition: DefinitionKind
    component_count: int = Field(ge=0, le=4)
    definition_components: tuple[tuple[Center, ...], ...]


ErrorCode = Literal["invalid_request", "invalid_utc_datetime", "unsupported_date_range",
                    "ephemeris_error", "design_moment_error", "classification_error"]


class HumanDesignErrorDetail(ContractModel):
    code: ErrorCode
    message: str


class HumanDesignErrorResponse(ContractModel):
    detail: HumanDesignErrorDetail
