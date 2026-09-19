"""Sequential, lossless orchestration of the three existing engines only."""
from pydantic import ValidationError

from app.schemas.astrology import AstrologyRequest
from app.schemas.numerology import NumerologyRequest
from app.services.astrology_service import AstrologyError, AstrologyService
from app.services.human_design_core import calculate_human_design_core
from app.services.human_design_models import HumanDesignError
from app.services.life_code_models import LifeCodeInput, LifeCodeInputError, LifeCodeMetadata, LifeCodeResult
from app.services.numerology_service import NumerologyError, NumerologyService


def calculate_life_code(input: LifeCodeInput) -> LifeCodeResult:
    if not isinstance(input, LifeCodeInput):
        raise LifeCodeInputError("input")
    try:
        # Existing request models own engine-specific invariants. No API/admission clock.
        astrology_request = AstrologyRequest(
            utc_datetime=input.utc_datetime, latitude=input.latitude,
            longitude=input.longitude, house_system="placidus")
        numerology_request = NumerologyRequest(
            full_name=input.full_name, birth_date=input.birth_date, target_year=input.target_year)
    except ValidationError as error:
        # str(ValidationError) contains input, including names. Never propagate it.
        field_name = str(error.errors(include_input=False, include_context=False)[0]["loc"][0])
        raise LifeCodeInputError(field_name) from None
    try:
        astrology = AstrologyService().calculate(astrology_request)
        numerology = NumerologyService().calculate(numerology_request)
        human_design = calculate_human_design_core(input.utc_datetime)
    except (AstrologyError, NumerologyError, HumanDesignError) as error:
        # Preserve the existing domain type/code/message; suppress native cause display.
        # No generic catch, fallback, partial result, HTTP mapping or retry.
        raise error from None
    return LifeCodeResult(LifeCodeMetadata(), astrology, numerology, human_design)
