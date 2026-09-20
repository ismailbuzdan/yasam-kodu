"""Resolved-input admission, one service call and privacy-safe public projection."""
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.api.human_design_projection import project_human_design
from app.api.numerology import validation_today
from app.core.birth_date_validation import validate_birth_date
from app.schemas.life_code import (
    ErrorCode, LifeCodeErrorDetail, LifeCodeErrorResponse, LifeCodeRequest, LifeCodeResponse,
)
from app.services.astrology_service import AstrologyError
from app.services.human_design_models import HumanDesignError
from app.services.life_code_models import LifeCodeInput, LifeCodeInputError
from app.services.life_code_service import calculate_life_code
from app.services.numerology_service import NumerologyError

MESSAGES: dict[ErrorCode, str] = {
    "invalid_request": "İstek gövdesini ve alanlarını kontrol edin.",
    "invalid_name": "1–200 karakter uzunluğunda geçerli bir ad girin.",
    "unsupported_name_characters": "Ad yalnız Latin A-Z ve Türkçe harfler içerebilir.",
    "invalid_birth_date": "Geçerli ve gelecekte olmayan bir doğum tarihi girin.",
    "invalid_target_year": "Hedef yıl 1–9999 arasında bir tam sayı veya null olmalıdır.",
    "invalid_utc_datetime": "Geçerli, UTC ve gelecekte olmayan kesin bir doğum zamanı girin.",
    "invalid_coordinates": "Koordinatlar geçerli aralıkta olmalıdır.",
    "unsupported_date_range": "Desteklenen UTC doğum yılları 1800–2100 aralığındadır.",
    "ephemeris_error": "Astronomik hesaplama tamamlanamadı.",
    "house_calculation_error": "Bu konum için Placidus evleri hesaplanamadı.",
    "design_moment_error": "Design zamanı güvenli biçimde hesaplanamadı.",
    "classification_error": "Human Design sınıflandırması tamamlanamadı.",
}
FIELD_CODES: dict[str, ErrorCode] = {
    "full_name": "invalid_name", "birth_date": "invalid_birth_date",
    "utc_datetime": "invalid_utc_datetime", "latitude": "invalid_coordinates",
    "longitude": "invalid_coordinates", "target_year": "invalid_target_year",
}


def error_response(code: ErrorCode) -> JSONResponse:
    status = 503 if code in {"ephemeris_error", "design_moment_error", "classification_error"} else 422
    body = LifeCodeErrorResponse(detail=LifeCodeErrorDetail(code=code, message=MESSAGES[code]))
    return JSONResponse(status_code=status, content=body.model_dump(mode="json"))


class LifeCodeRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request: Request):
            try:
                return await original(request)
            except RequestValidationError as error:
                errors = error.errors()
                if any(e["type"] in {"extra_forbidden", "json_invalid"} for e in errors):
                    return error_response("invalid_request")
                # Stable field priority. Never serialize input, ctx, location or raw messages.
                for field, code in FIELD_CODES.items():
                    matching = [e for e in errors if e["loc"] == ("body", field)]
                    if matching:
                        if any(e["type"] == "unsupported_date_range" for e in matching):
                            code = "unsupported_date_range"
                        return error_response(code)
                return error_response("invalid_request")
        return handler


router = APIRouter(prefix="/api/v1/life-code", tags=["life-code"], route_class=LifeCodeRoute)


def validation_now() -> datetime:
    """UTC instant clock; calendar admission separately preserves Numerology's local today."""
    return datetime.now(timezone.utc)


@router.post("/calculate", response_model=LifeCodeResponse,
             responses={422: {"model": LifeCodeErrorResponse}, 503: {"model": LifeCodeErrorResponse}})
def calculate(request: LifeCodeRequest, now: datetime = Depends(validation_now),
              today: date = Depends(validation_today)):
    try:
        validate_birth_date(request.birth_date, today=today)
    except ValueError:
        return error_response("invalid_birth_date")
    if request.utc_datetime > now:
        return error_response("invalid_utc_datetime")
    try:
        resolved = LifeCodeInput(
            full_name=request.full_name, birth_date=request.birth_date, utc_datetime=request.utc_datetime,
            latitude=request.latitude, longitude=request.longitude, target_year=request.target_year)
        result = calculate_life_code(resolved)
    except LifeCodeInputError as error:
        return error_response(FIELD_CODES.get(error.field, "invalid_request"))
    except (AstrologyError, NumerologyError, HumanDesignError) as error:
        return error_response(error.code)
    return LifeCodeResponse(metadata=result.metadata, astrology=result.astrology,
                            numerology=result.numerology, human_design=project_human_design(result.human_design))
