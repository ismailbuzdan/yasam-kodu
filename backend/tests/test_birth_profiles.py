"""Synthetic profile data; no real-person birth information."""
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def client() -> TestClient:
    return TestClient(create_app(Settings(app_env="test", _env_file=None)))


def payload(**overrides: object) -> dict[str, object]:
    profile: dict[str, object] = {
        "first_name": "Örnek",
        "last_name": "Kullanıcı",
        "birth_date": "2004-06-17",
        "birth_time": "14:25",
        "country": "Türkiye",
        "city": "Kayseri",
        "district": None,
        "time_accuracy": "exact",
        "approximate_start_time": None,
        "approximate_end_time": None,
    }
    profile.update(overrides)
    return profile


def post(profile: dict[str, object]):
    with client() as test_client:
        return test_client.post("/api/v1/birth-profiles/validate", json=profile)


def error_fields(response) -> set[str]:
    return {item["loc"][-1] for item in response.json()["detail"]}


def test_valid_exact_profile_is_normalized_and_preserves_unicode() -> None:
    response = post(payload())
    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "profile": {
            "first_name": "Örnek",
            "last_name": "Kullanıcı",
            "birth_date": "2004-06-17",
            "birth_time": "14:25",
            "country": "Türkiye",
            "city": "Kayseri",
            "district": None,
            "time_accuracy": "exact",
            "approximate_start_time": None,
            "approximate_end_time": None,
        },
    }


def test_valid_approximate_profile() -> None:
    response = post(payload(
        time_accuracy="approximate",
        birth_time=None,
        approximate_start_time="05:30",
        approximate_end_time="07:00",
    ))
    assert response.status_code == 200
    assert response.json()["profile"]["birth_time"] is None
    assert response.json()["profile"]["approximate_start_time"] == "05:30"


def test_valid_unknown_profile() -> None:
    response = post(payload(
        time_accuracy="unknown",
        birth_time=None,
        approximate_start_time=None,
        approximate_end_time=None,
    ))
    assert response.status_code == 200
    assert response.json()["profile"]["time_accuracy"] == "unknown"


def test_future_birth_date_is_rejected() -> None:
    response = post(payload(birth_date=(date.today() + timedelta(days=1)).isoformat()))
    assert response.status_code == 422
    assert error_fields(response) == {"birth_date"}


def test_exact_requires_birth_time() -> None:
    response = post(payload(birth_time=None))
    assert response.status_code == 422
    assert error_fields(response) == {"birth_time"}


def test_approximate_requires_start_time() -> None:
    response = post(payload(
        time_accuracy="approximate",
        birth_time=None,
        approximate_start_time=None,
        approximate_end_time="07:00",
    ))
    assert response.status_code == 422
    assert error_fields(response) == {"approximate_start_time"}


def test_approximate_requires_end_time() -> None:
    response = post(payload(
        time_accuracy="approximate",
        birth_time=None,
        approximate_start_time="05:30",
        approximate_end_time=None,
    ))
    assert response.status_code == 422
    assert error_fields(response) == {"approximate_end_time"}


def test_approximate_start_cannot_be_after_end() -> None:
    response = post(payload(
        time_accuracy="approximate",
        birth_time=None,
        approximate_start_time="08:00",
        approximate_end_time="07:00",
    ))
    assert response.status_code == 422
    assert error_fields(response) == {"approximate_end_time"}


def test_invalid_time_is_rejected() -> None:
    response = post(payload(birth_time="25:00"))
    assert response.status_code == 422
    assert error_fields(response) == {"birth_time"}
