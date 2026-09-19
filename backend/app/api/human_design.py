"""Clock-aware admission and explicit serialization around the unchanged HD core."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.core.birth_date_validation import validate_birth_date
from app.schemas.human_design import (
    ErrorCode, HumanDesignErrorDetail, HumanDesignErrorResponse,
    HumanDesignRequest, HumanDesignResponse,
)
from app.services.human_design_core import calculate_human_design_core
from app.services.human_design_models import HumanDesignError

MESSAGES: dict[ErrorCode, str] = {
    "invalid_request": "İstek gövdesini ve alanlarını kontrol edin.",
    "invalid_utc_datetime": "Geçerli, UTC ve gelecekte olmayan kesin bir doğum zamanı girin.",
    "unsupported_date_range": "Desteklenen doğum yılları 1800–2100 aralığındadır.",
    "ephemeris_error": "Astronomik hesaplama tamamlanamadı.",
    "design_moment_error": "Design zamanı güvenli biçimde hesaplanamadı.",
    "classification_error": "Human Design sınıflandırması tamamlanamadı.",
}


def error_response(code: ErrorCode) -> JSONResponse:
    status = 503 if code in {"ephemeris_error", "design_moment_error", "classification_error"} else 422
    body = HumanDesignErrorResponse(detail=HumanDesignErrorDetail(code=code, message=MESSAGES[code]))
    return JSONResponse(status_code=status, content=body.model_dump(mode="json"))


class HumanDesignRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request: Request):
            try:
                return await original(request)
            except RequestValidationError as error:
                errors = error.errors()
                code: ErrorCode = (
                    "invalid_request" if any(e["type"] in {"extra_forbidden", "json_invalid"} for e in errors)
                    else "unsupported_date_range" if any(e["type"] == "unsupported_date_range" for e in errors)
                    else "invalid_utc_datetime" if any("utc_datetime" in e["loc"] for e in errors)
                    else "invalid_request"
                )
                # Never echo Pydantic input/context, submitted data or exception messages.
                return error_response(code)
        return handler


router = APIRouter(prefix="/api/v1/human-design", tags=["human-design"], route_class=HumanDesignRoute)


def validation_now() -> datetime:
    """UTC admission clock only; override this dependency in tests."""
    return datetime.now(timezone.utc)


@router.post("/calculate", response_model=HumanDesignResponse,
             responses={422: {"model": HumanDesignErrorResponse}, 503: {"model": HumanDesignErrorResponse}})
def calculate_human_design(request: HumanDesignRequest, now: datetime = Depends(validation_now)):
    try:
        validate_birth_date(request.utc_datetime.date(), today=now.date())
    except ValueError:
        return error_response("invalid_utc_datetime")
    if request.utc_datetime > now:
        return error_response("invalid_utc_datetime")
    try:
        result = calculate_human_design_core(request.utc_datetime)
    except HumanDesignError as error:
        return error_response(error.code)
    return HumanDesignResponse(
        metadata=result.metadata, birth_utc=result.birth_utc, design_utc=result.astronomy.design_utc,
        personality=result.astronomy.personality, design=result.astronomy.design_activations,
        active_gates=result.active_gates, channels=result.channels,
        defined_centers=result.defined_centers, undefined_centers=result.undefined_centers,
        type=result.type, strategy=result.strategy, authority=result.authority, profile=result.profile,
        definition=result.definition, component_count=result.component_count,
        definition_components=result.definition_components,
    )
