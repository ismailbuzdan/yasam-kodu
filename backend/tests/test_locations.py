"""Synthetic provider payloads; fictional labels and generic coordinates."""
import httpx
from fastapi.testclient import TestClient

from app.api.locations import get_geocoding_service
from app.core.config import Settings
from app.main import create_app
from app.schemas.location import LocationResolveRequest
from app.services.geocoding_service import GeocodingService


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> object:
        return self.payload


def candidate(latitude: str, longitude: str, *, district: str | None, city: str, country: str = "Türkiye") -> dict[str, object]:
    address: dict[str, str] = {"country": country, "city": city}
    if district:
        address["town"] = district
    return {"lat": latitude, "lon": longitude, "address": address}


def service_with(payload: object) -> GeocodingService:
    def fake_get(*_args, **_kwargs) -> FakeResponse:
        return FakeResponse(payload)

    return GeocodingService(base_url="https://geocoder.example", user_agent="yasam-kodu-tests/0.1", timeout_seconds=1, http_get=fake_get)


def client_with(service: GeocodingService) -> TestClient:
    app = create_app(Settings(app_env="test", _env_file=None))
    app.dependency_overrides[get_geocoding_service] = lambda: service
    return TestClient(app)


def resolve(service: GeocodingService, **values: str | None):
    request: dict[str, str | None] = {"country": "Türkiye", "city": "Örnek Şehir", "district": "Örnek İlçe"}
    request.update(values)
    with client_with(service) as test_client:
        return test_client.post("/api/v1/locations/resolve", json=request)


def test_resolves_synthetic_district_and_preserves_turkish_text() -> None:
    response = resolve(service_with([candidate("39.9", "32.8", district="Örnek İlçe", city="Örnek Şehir")]))
    assert response.status_code == 200
    assert response.json() == {"resolved": True, "location": {"display_name": "Örnek İlçe, Örnek Şehir, Türkiye", "latitude": 39.9, "longitude": 32.8, "country": "Türkiye", "city": "Örnek Şehir", "district": "Örnek İlçe", "provider": "nominatim"}}


def test_resolves_other_synthetic_districts() -> None:
    second = resolve(service_with([candidate("38.7", "35.5", district="İkinci İlçe", city="İkinci Şehir")]), city="İkinci Şehir", district="İkinci İlçe")
    third = resolve(service_with([candidate("37.9", "32.5", district="Üçüncü İlçe", city="Üçüncü Şehir")]), city="Üçüncü Şehir", district="Üçüncü İlçe")
    assert second.status_code == 200
    assert second.json()["location"]["display_name"] == "İkinci İlçe, İkinci Şehir, Türkiye"
    assert third.status_code == 200
    assert third.json()["location"]["display_name"] == "Üçüncü İlçe, Üçüncü Şehir, Türkiye"


def test_blank_district_uses_city_country_query() -> None:
    service = service_with([candidate("39.7", "32.6", district=None, city="Örnek Şehir")])
    response = resolve(service, district="  ")
    assert response.status_code == 200
    assert response.json()["location"]["display_name"] == "Örnek Şehir, Türkiye"
    assert LocationResolveRequest(country="Türkiye", city="Örnek Şehir", district=" ").query == "Örnek Şehir, Türkiye"


def test_not_found_returns_structured_404() -> None:
    response = resolve(service_with([]))
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "location_not_found"


def test_provider_timeout_returns_structured_504() -> None:
    def timeout(*_args, **_kwargs):
        raise httpx.TimeoutException("slow provider")

    response = resolve(GeocodingService(base_url="https://geocoder.example", user_agent="test", timeout_seconds=1, http_get=timeout))
    assert response.status_code == 504
    assert response.json()["detail"]["code"] == "geocoding_timeout"


def test_provider_error_returns_structured_503() -> None:
    def failing_get(*_args, **_kwargs):
        raise httpx.ConnectError("offline")

    response = resolve(GeocodingService(base_url="https://geocoder.example", user_agent="test", timeout_seconds=1, http_get=failing_get))
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "geocoding_unavailable"


def test_invalid_coordinates_return_malformed_provider_response() -> None:
    response = resolve(service_with([candidate("95", "32.8", district="Örnek İlçe", city="Örnek Şehir")]))
    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "geocoding_invalid_response"


def test_selects_more_specific_candidate_deterministically() -> None:
    service = service_with([candidate("39.8", "32.7", district=None, city="Örnek Şehir"), candidate("39.9", "32.8", district="Örnek İlçe", city="Örnek Şehir")])
    response = resolve(service)
    assert response.status_code == 200
    assert response.json()["location"]["latitude"] == 39.9


def test_equally_scored_candidates_return_ambiguity_error() -> None:
    response = resolve(service_with([candidate("39.9", "32.8", district="Örnek İlçe", city="Örnek Şehir"), candidate("39.8", "32.9", district="Örnek İlçe", city="Örnek Şehir")]))
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "location_ambiguous"
