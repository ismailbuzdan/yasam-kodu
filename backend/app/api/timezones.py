from functools import lru_cache

from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.schemas.timezone import TimezoneErrorDetail, TimezoneErrorResponse, TimezoneRequest, TimezoneResponse
from app.services.timezone_service import TimezoneError, TimezoneService


class TimezoneRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request: Request):
            try:
                return await original(request)
            except RequestValidationError as error:
                coordinates = any(item["loc"][-1] in ("latitude", "longitude") for item in error.errors())
                code = "invalid_coordinates" if coordinates else "invalid_datetime"
                return JSONResponse(status_code=422, content={"detail": {"code": code, "message": "Koordinat, tarih ve saat alanlarını kontrol edin."}})
        return handler


router = APIRouter(prefix="/api/v1/timezones", tags=["timezones"], route_class=TimezoneRoute)


@lru_cache
def get_timezone_service() -> TimezoneService:
    return TimezoneService()


@router.post("/resolve", response_model=TimezoneResponse,
             responses={code: {"model": TimezoneErrorResponse} for code in (404, 409, 422, 503)})
def resolve_timezone(request: TimezoneRequest, service: TimezoneService = Depends(get_timezone_service)):
    try:
        return service.resolve(**request.model_dump())
    except TimezoneError as error:
        status = {"timezone_not_found": 404, "ambiguous_local_time": 409, "timezone_data_unavailable": 503}.get(error.code, 422)
        detail = TimezoneErrorDetail(code=error.code, message=str(error), timezone=error.zone, candidates=error.candidates)
        return JSONResponse(status_code=status, content={"detail": detail.model_dump(mode="json")})
