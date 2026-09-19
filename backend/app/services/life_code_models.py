"""Internal aggregation values, not HTTP or persistence models."""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal

from app.schemas.astrology import AstrologyResponse
from app.schemas.numerology import NumerologyResponse
from app.services.human_design_models import HumanDesignResult


class LifeCodeInputError(ValueError):
    """Safe internal validation text; never renders Pydantic input/context."""

    def __init__(self, field_name: str):
        self.code = "invalid_input"
        self.field = field_name
        super().__init__(f"Invalid Life Code input field: {field_name}.")


@dataclass(frozen=True)
class LifeCodeInput:
    full_name: str = field(repr=False)
    birth_date: date
    utc_datetime: datetime
    latitude: float
    longitude: float
    target_year: int | None = None

    def __post_init__(self) -> None:
        # Internal input is already resolved/typed, not a wire-format parser.
        if type(self.full_name) is not str:
            raise LifeCodeInputError("full_name")
        if type(self.birth_date) is not date:
            raise LifeCodeInputError("birth_date")
        if not isinstance(self.utc_datetime, datetime):
            raise LifeCodeInputError("utc_datetime")
        if self.target_year is not None and type(self.target_year) is not int:
            raise LifeCodeInputError("target_year")
        for name in ("latitude", "longitude"):
            if type(getattr(self, name)) not in (float, int):
                raise LifeCodeInputError(name)


@dataclass(frozen=True)
class LifeCodeMetadata:
    schema_version: Literal["life-code-v1"] = field(default="life-code-v1", init=False)
    calculation_layers: tuple[str, ...] = field(
        default=("astrology", "numerology", "human_design"), init=False)
    interpretation_present: Literal[False] = field(default=False, init=False)


@dataclass(frozen=True)
class LifeCodeResult:
    """Frozen envelope; original Astrology/Numerology children remain mutable.

    Do not mutate engine results. No copied schema, renamed fields or recalculation.
    This is not a recursively immutable snapshot of those existing Pydantic values.
    """
    metadata: LifeCodeMetadata
    astrology: AstrologyResponse
    numerology: NumerologyResponse
    human_design: HumanDesignResult
