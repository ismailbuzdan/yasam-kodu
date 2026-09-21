"""Resolved-input admission and privacy-safe HTTP projection for Kamerî Code."""
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.api.kameri_projection import project_kameri
from app.api.numerology import validation_today
from app.core.birth_date_validation import validate_birth_date
from app.schemas.kameri import (
    ErrorCode, KameriErrorDetail, KameriErrorResponse, KameriRequest, KameriResponse,
)
from app.services.traditional.abjad import calculate_abjad
from app.services.traditional.hijri import calculate_hijri
from app.services.traditional.lunar import calculate_lunar
from app.services.traditional.models import TraditionalError
from app.services.traditional.planetary_hours import calculate_planetary_hour

MESSAGES: dict[ErrorCode, str] = {
    "invalid_request": "İstek gövdesini ve alanlarını kontrol edin.",
    "invalid_calendar_date": "Geçerli ve gelecekte olmayan bir yerel tarih girin.",
    "unsupported_date_range": "Desteklenen tarih yılları 1800–2100 aralığındadır.",
    "invalid_utc_datetime": "Geçerli, UTC ve gelecekte olmayan kesin bir zaman girin.",
    "invalid_coordinates": "Koordinatlar geçerli aralıkta olmalıdır.",
    "timezone_data_unavailable": "IANA saat dilimi çözümlenemedi.",
    "invalid_abjad_text": "Onaylanmış, 1–200 karakter uzunluğunda geçerli bir Arapça ad girin.",
    "unsupported_abjad_character": "Ad desteklenmeyen bir karakter içeriyor.",
    "ephemeris_error": "Astronomik hesaplama tamamlanamadı.",
    "solar_event_unavailable": "Bu konum ve tarih için gerekli güneş olayı bulunamadı.",
    "invalid_astronomical_result": "Astronomik sonuç güvenli biçimde doğrulanamadı.",
}


def error_response(code: ErrorCode) -> JSONResponse:
    status = 503 if code in {"ephemeris_error", "invalid_astronomical_result"} else 422
    body = KameriErrorResponse(detail=KameriErrorDetail(code=code, message=MESSAGES[code]))
    return JSONResponse(status_code=status, content=body.model_dump(mode="json"))


FIELD_CODES: tuple[tuple[str, ErrorCode], ...] = (
    ("local_date", "invalid_calendar_date"), ("utc_datetime", "invalid_utc_datetime"),
    ("latitude", "invalid_coordinates"), ("longitude", "invalid_coordinates"),
    ("timezone_id", "timezone_data_unavailable"),
    ("arabic_name_confirmed", "invalid_abjad_text"), ("arabic_name", "invalid_abjad_text"),
)


class KameriRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request: Request):
            try:
                return await original(request)
            except RequestValidationError as error:
                errors = error.errors()
                if any(e["type"] in {"extra_forbidden", "json_invalid"} for e in errors):
                    return error_response("invalid_request")
                for field, default_code in FIELD_CODES:
                    matching = [e for e in errors if e["loc"] == ("body", field)]
                    if matching:
                        code = "unsupported_date_range" if any(
                            e["type"] == "unsupported_date_range" for e in matching
                        ) else default_code
                        return error_response(code)
                return error_response("invalid_request")
        return handler


router = APIRouter(prefix="/api/v1/kameri", tags=["kameri"], route_class=KameriRoute)


def validation_now() -> datetime:
    return datetime.now(timezone.utc)


@router.post("/calculate", response_model=KameriResponse,
             responses={422: {"model": KameriErrorResponse}, 503: {"model": KameriErrorResponse}})
def calculate(request: KameriRequest, now: datetime = Depends(validation_now),
              today: date = Depends(validation_today)):
    try:
        validate_birth_date(request.local_date, today=today)
    except ValueError:
        return error_response("invalid_calendar_date")
    if request.utc_datetime > now:
        return error_response("invalid_utc_datetime")
    try:
        hijri = calculate_hijri(request.local_date)
        lunar = calculate_lunar(request.utc_datetime)
        abjad = calculate_abjad(request.arabic_name, confirmed=True)
        planetary_hour = calculate_planetary_hour(
            request.utc_datetime, request.latitude, request.longitude, request.timezone_id,
        )
    except TraditionalError as error:
        return error_response(error.code)
    return project_kameri(hijri, lunar, abjad, planetary_hour)
