from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings
from app.schemas.location import LocationResolveRequest, LocationResolveResponse
from app.services.geocoding_service import (
    GeocodingResponseError,
    GeocodingService,
    GeocodingTimeoutError,
    GeocodingUnavailableError,
    LocationAmbiguousError,
    LocationNotFoundError,
)

router = APIRouter(prefix="/api/v1/locations", tags=["locations"])


@lru_cache
def get_geocoding_service() -> GeocodingService:
    settings = Settings()
    return GeocodingService(
        base_url=settings.geocoding_base_url,
        user_agent=settings.geocoding_user_agent,
        timeout_seconds=settings.geocoding_timeout_seconds,
    )


def location_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


@router.post("/resolve", response_model=LocationResolveResponse, status_code=status.HTTP_200_OK)
def resolve_location(
    request: LocationResolveRequest,
    service: GeocodingService = Depends(get_geocoding_service),
) -> LocationResolveResponse:
    try:
        return LocationResolveResponse(location=service.resolve(request))
    except LocationNotFoundError:
        raise location_error(status.HTTP_404_NOT_FOUND, "location_not_found", "Bu konum için eşleşme bulunamadı.")
    except LocationAmbiguousError:
        raise location_error(status.HTTP_409_CONFLICT, "location_ambiguous", "Birden fazla benzer konum bulundu.")
    except GeocodingTimeoutError:
        raise location_error(status.HTTP_504_GATEWAY_TIMEOUT, "geocoding_timeout", "Konum servisi zamanında yanıt vermedi.")
    except GeocodingUnavailableError:
        raise location_error(status.HTTP_503_SERVICE_UNAVAILABLE, "geocoding_unavailable", "Konum servisi şu anda kullanılamıyor.")
    except GeocodingResponseError:
        raise location_error(status.HTTP_502_BAD_GATEWAY, "geocoding_invalid_response", "Konum servisinden geçerli bir yanıt alınamadı.")
