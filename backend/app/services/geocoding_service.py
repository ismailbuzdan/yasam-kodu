import logging
from collections.abc import Callable

import httpx

from app.schemas.location import LocationResolveRequest, ResolvedLocation

logger = logging.getLogger(__name__)


class LocationNotFoundError(Exception):
    pass


class LocationAmbiguousError(Exception):
    pass


class GeocodingTimeoutError(Exception):
    pass


class GeocodingUnavailableError(Exception):
    pass


class GeocodingResponseError(Exception):
    pass


HttpGet = Callable[..., httpx.Response]


class GeocodingService:
    """Small provider boundary around Nominatim, kept independent from API routes."""

    def __init__(self, *, base_url: str, user_agent: str, timeout_seconds: float, http_get: HttpGet = httpx.get) -> None:
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.http_get = http_get
        self._cache: dict[str, ResolvedLocation] = {}

    def resolve(self, request: LocationResolveRequest) -> ResolvedLocation:
        cache_key = request.query.casefold()
        if cached := self._cache.get(cache_key):
            return cached

        try:
            response = self.http_get(
                f"{self.base_url}/search",
                params={"q": request.query, "format": "jsonv2", "addressdetails": 1, "limit": 5},
                headers={"User-Agent": self.user_agent, "Accept": "application/json"},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.TimeoutException as error:
            logger.warning("Geocoding provider timed out for query %r", request.query)
            raise GeocodingTimeoutError from error
        except httpx.HTTPError as error:
            logger.warning("Geocoding provider request failed for query %r: %s", request.query, error)
            raise GeocodingUnavailableError from error

        try:
            candidates = response.json()
        except ValueError as error:
            logger.warning("Geocoding provider returned invalid JSON for query %r", request.query)
            raise GeocodingResponseError from error

        if not isinstance(candidates, list):
            raise GeocodingResponseError
        if not candidates:
            raise LocationNotFoundError

        location = self._select_candidate(candidates, request)
        self._cache[cache_key] = location
        return location

    def _select_candidate(self, candidates: list[object], request: LocationResolveRequest) -> ResolvedLocation:
        scored: list[tuple[int, ResolvedLocation]] = []
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            location = self._to_location(candidate, request)
            if location is not None:
                scored.append((self._score(candidate, request), location))

        if not scored:
            raise GeocodingResponseError
        scored.sort(key=lambda item: (-item[0], item[1].display_name.casefold(), item[1].latitude, item[1].longitude))
        best_score, best = scored[0]
        if len(scored) > 1 and scored[1][0] == best_score:
            raise LocationAmbiguousError
        return best

    def _to_location(self, candidate: dict[object, object], request: LocationResolveRequest) -> ResolvedLocation | None:
        try:
            latitude = float(candidate["lat"])
            longitude = float(candidate["lon"])
        except (KeyError, TypeError, ValueError):
            return None
        try:
            return ResolvedLocation(
                display_name=request.query,
                latitude=latitude,
                longitude=longitude,
                country=request.country,
                city=request.city,
                district=request.district,
            )
        except ValueError:
            return None

    @staticmethod
    def _score(candidate: dict[object, object], request: LocationResolveRequest) -> int:
        address = candidate.get("address")
        if not isinstance(address, dict):
            address = {}
        values = [str(value).casefold() for value in address.values() if isinstance(value, str)]

        def matches(value: str | None) -> bool:
            return value is not None and value.casefold() in values

        return (100 if matches(request.district) else 0) + (10 if matches(request.city) else 0) + (1 if matches(request.country) else 0)
