from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.core.birth_date_validation import validate_birth_date
from app.schemas.numerology import NumerologyErrorResponse, NumerologyRequest, NumerologyResponse
from app.services.numerology_service import NumerologyError, NumerologyService

MESSAGES = {
    "invalid_request": "İstek gövdesini ve alanlarını kontrol edin.",
    "invalid_name": "1–200 karakter uzunluğunda geçerli bir ad girin.",
    "invalid_birth_date": "Geçerli ve gelecekte olmayan bir doğum tarihi girin.",
    "invalid_target_year": "Hedef yıl 1–9999 arasında bir tam sayı veya null olmalıdır.",
}


def error_response(code, message):
    return JSONResponse(status_code=422, content={"detail": {"code": code, "message": message}})


class NumerologyRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request: Request):
            try:
                return await original(request)
            except RequestValidationError as error:
                errors = error.errors()
                fields = {item["loc"][-1] for item in errors}
                code = ("invalid_request" if any(item["type"] in {"extra_forbidden", "json_invalid"} for item in errors)
                        else "invalid_name" if "full_name" in fields
                        else "invalid_birth_date" if "birth_date" in fields
                        else "invalid_target_year" if "target_year" in fields
                        else "invalid_request")
                # Never serialize Pydantic input/context: it contains the submitted name.
                return error_response(code, MESSAGES[code])
        return handler


router = APIRouter(prefix="/api/v1/numerology", tags=["numerology"], route_class=NumerologyRoute)


def validation_today() -> date:
    """Admission clock only; override this dependency in tests."""
    return date.today()


@router.post("/calculate", response_model=NumerologyResponse,
             responses={422: {"model": NumerologyErrorResponse}})
def calculate_numerology(request: NumerologyRequest, today: date = Depends(validation_today)):
    try:
        validate_birth_date(request.birth_date, today=today)
    except ValueError:
        return error_response("invalid_birth_date", MESSAGES["invalid_birth_date"])
    try:
        return NumerologyService().calculate(request)
    except NumerologyError as error:
        return error_response(error.code, str(error))
