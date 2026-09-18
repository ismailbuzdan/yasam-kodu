from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.schemas.astrology import AstrologyErrorResponse, AstrologyRequest, AstrologyResponse
from app.services.astrology_service import AstrologyError, AstrologyService


class AstrologyRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request: Request):
            try:
                return await original(request)
            except RequestValidationError as error:
                fields = {item["loc"][-1] for item in error.errors()}
                code = ("invalid_request" if any(item["type"] == "extra_forbidden" for item in error.errors())
                        else "invalid_coordinates" if fields & {"latitude", "longitude"}
                        else "unsupported_house_system" if "house_system" in fields
                        else "invalid_utc_datetime" if "utc_datetime" in fields
                        else "invalid_request")
                return JSONResponse(status_code=422, content={"detail": {
                    "code": code, "message": "UTC zamanı, koordinatları ve ev sistemini kontrol edin."}})
        return handler


router = APIRouter(prefix="/api/v1/astrology", tags=["astrology"], route_class=AstrologyRoute)


def get_astrology_service() -> AstrologyService:
    return AstrologyService()


@router.post("/calculate", response_model=AstrologyResponse,
             responses={code: {"model": AstrologyErrorResponse} for code in (422, 503)})
def calculate_astrology(request: AstrologyRequest,
                        service: AstrologyService = Depends(get_astrology_service)):
    try:
        return service.calculate(request)
    except AstrologyError as error:
        return JSONResponse(status_code=503 if error.code == "ephemeris_error" else 422,
                            content={"detail": {"code": error.code, "message": str(error)}})
