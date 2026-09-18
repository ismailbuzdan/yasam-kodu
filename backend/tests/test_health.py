from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_health() -> None:
    with TestClient(create_app(Settings(app_env="test", _env_file=None))) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "yasam-kodu-api"}


def test_development_cors_allows_local_frontend() -> None:
    with TestClient(create_app(Settings(app_env="development", _env_file=None))) as client:
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_development_cors_allows_profile_post_from_local_frontend() -> None:
    with TestClient(create_app(Settings(app_env="development", _env_file=None))) as client:
        response = client.options("/api/v1/birth-profiles/validate", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        })
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_development_cors_rejects_unknown_origin() -> None:
    with TestClient(create_app(Settings(app_env="development", _env_file=None))) as client:
        response = client.options("/health", headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        })
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_production_has_no_development_cors() -> None:
    with TestClient(create_app(Settings(app_env="production", _env_file=None))) as client:
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert "access-control-allow-origin" not in response.headers
