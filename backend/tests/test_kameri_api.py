"""Public Kamerî API contract, privacy, ownership and error semantics."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
import json
from unittest.mock import Mock

from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from app.api import kameri as api
from app.api.kameri_projection import project_kameri
from app.core.config import Settings
from app.main import create_app
from app.schemas.kameri import KameriMetadataResponse, KameriRequest, KameriResponse
from app.services.traditional.abjad import calculate_abjad
from app.services.traditional.hijri import calculate_hijri
from app.services.traditional.lunar import calculate_lunar
from app.services.traditional.models import TraditionalError
from app.services.traditional.planetary_hours import calculate_planetary_hour

URL = "/api/v1/kameri/calculate"
NAME = "ابج"
BODY = {"local_date": "2000-01-02", "utc_datetime": "2000-01-01T21:30:00Z",
        "latitude": 40.0, "longitude": 30.0, "timezone_id": "Europe/Istanbul",
        "arabic_name": NAME, "arabic_name_confirmed": True}
NOW = datetime(2026, 9, 21, 12, tzinfo=timezone.utc)


@pytest.fixture
def client():
    app = create_app(Settings(app_env="test"))
    app.dependency_overrides[api.validation_now] = lambda: NOW
    app.dependency_overrides[api.validation_today] = lambda: date(2026, 9, 21)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def assert_error(response, code, status=422):
    assert response.status_code == status
    assert response.json() == {"detail": {"code": code, "message": api.MESSAGES[code]}}
    for private in (NAME, BODY["utc_datetime"], BODY["local_date"], "NativeSecret", "/private/path",
                    "traceback", "input_value"):
        assert private not in response.text


def all_keys(value):
    if isinstance(value, dict):
        return set(value) | set().union(*(all_keys(v) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(all_keys(v) for v in value))
    return set()


def test_happy_path_exact_core_projection_once_in_order_and_cross_date(client, monkeypatch, caplog):
    caplog.set_level("DEBUG")
    local = date(2000, 1, 2)
    instant = datetime(2000, 1, 1, 21, 30, tzinfo=timezone.utc)
    expected = project_kameri(calculate_hijri(local), calculate_lunar(instant),
                              calculate_abjad(NAME, confirmed=True),
                              calculate_planetary_hour(instant, 40.0, 30.0, "Europe/Istanbul"))
    calls = []
    for attr, function in (("calculate_hijri", calculate_hijri), ("calculate_lunar", calculate_lunar),
                           ("calculate_abjad", calculate_abjad),
                           ("calculate_planetary_hour", calculate_planetary_hour)):
        def wrapped(*args, _name=attr, _function=function, **kwargs):
            calls.append(_name)
            return _function(*args, **kwargs)
        monkeypatch.setattr(api, attr, Mock(side_effect=wrapped))
    response = client.post(URL, json=BODY)
    assert response.status_code == 200
    assert calls == ["calculate_hijri", "calculate_lunar", "calculate_abjad", "calculate_planetary_hour"]
    assert response.json() == expected.model_dump(mode="json")
    assert KameriResponse.model_validate_json(response.content).model_dump(mode="json") == response.json()
    data = response.json()
    assert data["metadata"] == {"schema_version": "kameri-code-v1",
        "calculation_layers": ["hijri", "lunar", "abjad", "planetary_hour"],
        "interpretation_present": False}
    forbidden = {"arabic_name", "normalized_text", "letters", "events", "sunrise", "sunset",
                 "next_sunrise", "start_jd_ut1", "end_jd_ut1", "position_flags",
                 "phenomena_flags", "event_ephemeris_flags", "search_hours_each_direction"}
    assert not forbidden & all_keys(data)
    assert NAME not in response.text + caplog.text


@pytest.mark.parametrize("field,value,code", [
    ("local_date", "2000-02-30", "invalid_calendar_date"),
    ("local_date", "20000102", "invalid_calendar_date"),
    ("local_date", "1799-12-31", "unsupported_date_range"),
    ("local_date", "2101-01-01", "unsupported_date_range"),
    ("utc_datetime", "2000-01-01T21:30:00", "invalid_utc_datetime"),
    ("utc_datetime", "2000-01-01T21:30:00+03:00", "invalid_utc_datetime"),
    ("utc_datetime", "1799-12-31T00:00:00Z", "unsupported_date_range"),
    ("utc_datetime", "2101-01-01T00:00:00Z", "unsupported_date_range"),
    ("latitude", -90.1, "invalid_coordinates"), ("latitude", 90.1, "invalid_coordinates"),
    ("longitude", -180.1, "invalid_coordinates"), ("longitude", 180.1, "invalid_coordinates"),
    ("latitude", "40", "invalid_coordinates"), ("longitude", True, "invalid_coordinates"),
    ("timezone_id", "", "timezone_data_unavailable"), ("timezone_id", 3, "timezone_data_unavailable"),
    ("arabic_name", "", "invalid_abjad_text"), ("arabic_name", 3, "invalid_abjad_text"),
    ("arabic_name_confirmed", False, "invalid_abjad_text"),
    ("arabic_name_confirmed", "true", "invalid_abjad_text"),
])
def test_schema_validation_never_calls_core(client, monkeypatch, field, value, code):
    spies = [Mock() for _ in range(4)]
    for name, spy in zip(("calculate_hijri", "calculate_lunar", "calculate_abjad",
                          "calculate_planetary_hour"), spies):
        monkeypatch.setattr(api, name, spy)
    assert_error(client.post(URL, json={**BODY, field: value}), code)
    assert not any(spy.called for spy in spies)


@pytest.mark.parametrize("field,code", [
    ("local_date", "invalid_calendar_date"), ("utc_datetime", "invalid_utc_datetime"),
    ("latitude", "invalid_coordinates"), ("longitude", "invalid_coordinates"),
    ("timezone_id", "timezone_data_unavailable"), ("arabic_name_confirmed", "invalid_abjad_text"),
    ("arabic_name", "invalid_abjad_text"),
])
def test_missing_fields(client, field, code):
    assert_error(client.post(URL, json={k: v for k, v in BODY.items() if k != field}), code)


@pytest.mark.parametrize("extra", ["city", "country", "local_time", "birth_date", "extra"])
def test_extra_fields_have_highest_priority(client, extra):
    assert_error(client.post(URL, json={**BODY, extra: "NativeSecret", "local_date": "bad"}),
                 "invalid_request")


@pytest.mark.parametrize("raw", ["", "null", "[]", '"string"', "123", '{"local_date":'])
def test_malformed_or_non_object_body(client, raw):
    assert_error(client.post(URL, content=raw, headers={"Content-Type": "application/json"}),
                 "invalid_request")


def test_empty_object_uses_stable_field_priority(client):
    assert_error(client.post(URL, json={}), "invalid_calendar_date")


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_coordinate_rejected(client, value):
    raw = json.dumps({**BODY, "latitude": value})
    assert_error(client.post(URL, content=raw, headers={"Content-Type": "application/json"}),
                 "invalid_coordinates")


@pytest.mark.parametrize("stamp,status", [
    ("2026-09-21T11:59:59.999999Z", 200), ("2026-09-21T12:00:00Z", 200),
    ("2026-09-21T12:00:00.000001Z", 422),
])
def test_instant_clock_boundary(client, stamp, status):
    response = client.post(URL, json={**BODY, "local_date": "2026-09-21", "utc_datetime": stamp})
    assert response.status_code == status
    if status == 422:
        assert_error(response, "invalid_utc_datetime")


def test_calendar_clock_is_independent_of_utc_date(client):
    client.app.dependency_overrides[api.validation_today] = lambda: date(2026, 9, 20)
    body = {**BODY, "local_date": "2026-09-21", "utc_datetime": "2026-09-20T12:00:00Z"}
    assert_error(client.post(URL, json=body), "invalid_calendar_date")


@pytest.mark.parametrize("name,code", [(" , ", "invalid_abjad_text"),
                                        ("ابج😀", "unsupported_abjad_character")])
def test_core_owned_abjad_validation(client, name, code):
    assert_error(client.post(URL, json={**BODY, "arabic_name": name}), code)


@pytest.mark.parametrize("zone", ["Missing/Zone", "../UTC"])
def test_invalid_timezone_is_input_error(client, zone):
    assert_error(client.post(URL, json={**BODY, "timezone_id": zone}), "timezone_data_unavailable")


@pytest.mark.parametrize("code,status", [
    ("invalid_calendar_date", 422), ("unsupported_date_range", 422),
    ("invalid_utc_datetime", 422), ("invalid_coordinates", 422),
    ("timezone_data_unavailable", 422), ("invalid_abjad_text", 422),
    ("unsupported_abjad_character", 422), ("solar_event_unavailable", 422),
    ("ephemeris_error", 503), ("invalid_astronomical_result", 503),
])
def test_domain_errors_have_static_safe_mapping(client, monkeypatch, code, status, caplog):
    caplog.set_level("DEBUG")
    monkeypatch.setattr(api, "calculate_hijri", Mock(side_effect=TraditionalError(code)))
    response = client.post(URL, json=BODY)
    assert_error(response, code, status)
    assert NAME not in caplog.text


def test_no_partial_success_and_short_circuit_order(client, monkeypatch):
    first, later = Mock(side_effect=TraditionalError("ephemeris_error")), Mock()
    monkeypatch.setattr(api, "calculate_hijri", first)
    for name in ("calculate_lunar", "calculate_abjad", "calculate_planetary_hour"):
        monkeypatch.setattr(api, name, later)
    assert_error(client.post(URL, json=BODY), "ephemeris_error", 503)
    first.assert_called_once()
    later.assert_not_called()


def test_programming_errors_are_not_swallowed(client, monkeypatch):
    monkeypatch.setattr(api, "calculate_hijri", Mock(side_effect=RuntimeError("Programming failure")))
    with pytest.raises(RuntimeError, match="Programming failure"):
        client.post(URL, json=BODY)


def test_determinism_zero_offset_spellings_and_metamorphic_ownership(client):
    first = client.post(URL, json=BODY)
    repeat = client.post(URL, json=BODY)
    explicit = client.post(URL, json={**BODY, "utc_datetime": BODY["utc_datetime"].replace("Z", "+00:00")})
    changed_name = client.post(URL, json={**BODY, "arabic_name": "غ"})
    changed_date = client.post(URL, json={**BODY, "local_date": "2000-01-03"})
    assert all(r.status_code == 200 for r in (first, repeat, explicit, changed_name, changed_date))
    assert first.content == repeat.content == explicit.content
    assert first.json()["abjad"] != changed_name.json()["abjad"]
    for key in ("hijri", "lunar", "planetary_hour"):
        assert first.json()[key] == changed_name.json()[key]
    assert first.json()["hijri"] != changed_date.json()["hijri"]
    for key in ("lunar", "abjad", "planetary_hour"):
        assert first.json()[key] == changed_date.json()[key]


def test_small_parallel_repeatability(client):
    expected = client.post(URL, json=BODY).content
    with ThreadPoolExecutor(max_workers=3) as pool:
        responses = list(pool.map(lambda _: client.post(URL, json=BODY), range(4)))
    assert all(r.status_code == 200 and r.content == expected for r in responses)


def test_request_repr_and_transport_metadata_are_private_and_strict():
    parsed = KameriRequest.model_validate(BODY)
    assert NAME not in repr(parsed)
    metadata = {"schema_version": "kameri-code-v1",
                "calculation_layers": ("hijri", "lunar", "abjad", "planetary_hour"),
                "interpretation_present": False}
    KameriMetadataResponse.model_validate(metadata)
    with pytest.raises(ValidationError):
        KameriMetadataResponse.model_validate({**metadata, "interpretation_present": True})


def test_registration_preserves_disabled_docs_and_cors(client):
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 404
    route = next(r for r in api.router.routes if r.path == URL)
    assert route.response_model is KameriResponse
    assert set(route.responses) == {422, 503}
