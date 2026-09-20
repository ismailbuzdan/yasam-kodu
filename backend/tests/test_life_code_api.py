"""Synthetic public aggregation contract, privacy and standalone equivalence tests."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import date, datetime, timezone
import json
from unittest.mock import Mock

from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from app.api import human_design as hd_api, life_code as api
from app.api.human_design_projection import project_human_design
from app.core.config import Settings
from app.main import create_app
from app.schemas.life_code import LifeCodeMetadataResponse, LifeCodeRequest, LifeCodeResponse
from app.services.astrology_service import AstrologyError
from app.services.human_design_models import HumanDesignError
from app.services.life_code_models import LifeCodeInput, LifeCodeInputError
from app.services.life_code_service import calculate_life_code
from app.services.numerology_service import NumerologyError

URL = "/api/v1/life-code/calculate"
NAME = "Synthetic Privacy Sentinel"
BODY = dict(full_name=NAME, birth_date="2000-01-02", utc_datetime="2000-01-01T21:30:00Z",
            latitude=30.0, longitude=30.0, target_year=None)
NOW = datetime(2026, 9, 20, 12, tzinfo=timezone.utc)
METADATA = {"schema_version": "life-code-v1",
            "calculation_layers": ["astrology", "numerology", "human_design"], "interpretation_present": False}


@pytest.fixture
def client():
    app = create_app(Settings(app_env="test"))
    app.dependency_overrides[api.validation_now] = lambda: NOW
    app.dependency_overrides[api.validation_today] = lambda: date(2026, 9, 20)
    app.dependency_overrides[hd_api.validation_now] = lambda: NOW
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def resolved():
    return LifeCodeInput(NAME, date(2000, 1, 2), datetime(2000, 1, 1, 21, 30, tzinfo=timezone.utc), 30.0, 30.0)


def all_keys(value):
    if isinstance(value, dict):
        return set(value) | set().union(*(all_keys(v) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(all_keys(v) for v in value))
    return set()


def assert_error(response, code, status=422):
    assert response.status_code == status
    assert response.json() == {"detail": {"code": code, "message": api.MESSAGES[code]}}
    for private in (NAME, "SYNTHETICPRIVACYSENTINEL", BODY["utc_datetime"], BODY["birth_date"],
                    "SyntheticNativeMarker", "/private/path", "input_value", "traceback", "30.0"):
        assert private not in response.text


def test_happy_path_exact_core_projection_once_and_cross_date(client, monkeypatch, caplog):
    caplog.set_level("DEBUG")
    core = calculate_life_code(resolved())
    spy = Mock(wraps=calculate_life_code)
    monkeypatch.setattr(api, "calculate_life_code", spy)
    response = client.post(URL, json=BODY)
    assert response.status_code == 200
    spy.assert_called_once_with(resolved())
    data = response.json()
    assert set(data) == {"metadata", "astrology", "numerology", "human_design"}
    assert data["metadata"] == METADATA
    assert data["astrology"] == core.astrology.model_dump(mode="json")
    assert data["numerology"] == core.numerology.model_dump(mode="json")
    assert data["human_design"] == project_human_design(core.human_design).model_dump(mode="json")
    assert LifeCodeResponse.model_validate_json(response.content).model_dump(mode="json") == data
    assert data["numerology"]["birthday"]["raw_sum"] == 2  # local calendar date, not UTC day 1
    assert data["human_design"]["birth_utc"] == BODY["utc_datetime"]
    assert data["numerology"]["personal_year"] is None
    forbidden = {"full_name", "normalized_name", "birth_date", "latitude", "personality_jd_ut1",
                 "jd_ut1", "bracket_seconds", "residual_degrees", "iterations", "astronomy"}
    assert not forbidden & all_keys(data)
    assert NAME not in response.text + caplog.text
    assert "SYNTHETICPRIVACYSENTINEL" not in response.text + caplog.text
    assert not [record for record in caplog.records if record.name.startswith("app.")]


def test_standalone_endpoint_equality(client):
    unified = client.post(URL, json=BODY)
    assert unified.status_code == 200
    requests = {
        "astrology": {k: BODY[k] for k in ("utc_datetime", "latitude", "longitude")},
        "numerology": {k: BODY[k] for k in ("full_name", "birth_date", "target_year")},
        "human-design": {"utc_datetime": BODY["utc_datetime"]},
    }
    for engine, body in requests.items():
        standalone = client.post(f"/api/v1/{engine}/calculate", json=body)
        assert standalone.status_code == 200
        assert unified.json()[engine.replace("-", "_")] == standalone.json()


def test_shared_hd_projection_same_core_no_mutation(client, monkeypatch):
    core = calculate_life_code(resolved())
    original = asdict(core.human_design)
    monkeypatch.setattr(api, "calculate_life_code", Mock(return_value=core))
    monkeypatch.setattr(hd_api, "calculate_human_design_core", Mock(return_value=core.human_design))
    assert hd_api.project_human_design is api.project_human_design is project_human_design
    standalone = client.post("/api/v1/human-design/calculate", json={"utc_datetime": BODY["utc_datetime"]})
    response = client.post(URL, json=BODY)
    assert response.status_code == standalone.status_code == 200
    assert response.json()["human_design"] == standalone.json()
    assert asdict(core.human_design) == original
    # Bytes already serialized remain a snapshot even though original internal children are mutable.
    saved = response.content
    core.numerology.metadata.target_year = 2027
    assert response.content == saved
    assert response.json()["numerology"]["metadata"]["target_year"] is None


@pytest.mark.parametrize("change,unchanged", [
    ({"target_year": 2027}, ("astrology", "human_design")),
    ({"full_name": "Bora Test"}, ("astrology", "human_design")),
    ({"latitude": -20.0, "longitude": -60.0}, ("numerology", "human_design")),
])
def test_metamorphic_ownership(client, change, unchanged):
    first, second = client.post(URL, json=BODY), client.post(URL, json={**BODY, **change})
    assert first.status_code == second.status_code == 200
    a, b = first.json(), second.json()
    for key in unchanged:
        assert a[key] == b[key]
    if "target_year" in change:
        assert a["numerology"]["personal_year"] is None
        assert b["numerology"]["personal_year"] is not None
    elif "full_name" in change:
        assert a["numerology"]["expression"] != b["numerology"]["expression"]
        assert a["numerology"]["birthday"] == b["numerology"]["birthday"]
    else:
        assert a["astrology"]["ascendant"] != b["astrology"]["ascendant"]
        assert a["astrology"]["houses"] != b["astrology"]["houses"]


@pytest.mark.parametrize("field,value,code", [
    ("full_name", "", "invalid_name"), ("full_name", NAME * 20, "invalid_name"),
    ("full_name", 123, "invalid_name"), ("full_name", None, "invalid_name"),
    ("birth_date", "2000-02-30", "invalid_birth_date"),
    ("birth_date", "20000102", "invalid_birth_date"),
    ("birth_date", "2000-01-02T00:00:00Z", "invalid_birth_date"),
    ("birth_date", 946771200, "invalid_birth_date"),
    ("utc_datetime", "2000-01-01T21:30:00", "invalid_utc_datetime"),
    ("utc_datetime", "2000-01-01T21:30:00+03:00", "invalid_utc_datetime"),
    ("utc_datetime", "2000-01-01", "invalid_utc_datetime"),
    ("utc_datetime", "SyntheticNativeMarker", "invalid_utc_datetime"),
    ("utc_datetime", 946762200, "invalid_utc_datetime"),
    ("utc_datetime", "2000-01-01T21:30:00.1234567Z", "invalid_utc_datetime"),
    ("utc_datetime", "2000-01-01T21:30:60Z", "invalid_utc_datetime"),
    ("utc_datetime", "1799-12-31T00:00:00Z", "unsupported_date_range"),
    ("utc_datetime", "2101-01-01T00:00:00Z", "unsupported_date_range"),
    ("latitude", -90.1, "invalid_coordinates"), ("latitude", 90.1, "invalid_coordinates"),
    ("longitude", -180.1, "invalid_coordinates"), ("longitude", 180.1, "invalid_coordinates"),
    ("latitude", "30", "invalid_coordinates"), ("longitude", True, "invalid_coordinates"),
    ("target_year", "2026", "invalid_target_year"), ("target_year", True, "invalid_target_year"),
    ("target_year", 0, "invalid_target_year"), ("target_year", 10000, "invalid_target_year"),
    ("target_year", 2026.0, "invalid_target_year"),
])
def test_schema_validation_never_calls_service(client, monkeypatch, caplog, field, value, code):
    caplog.set_level("DEBUG")
    spy = Mock()
    monkeypatch.setattr(api, "calculate_life_code", spy)
    response = client.post(URL, json={**BODY, field: value})
    assert_error(response, code)
    spy.assert_not_called()
    assert NAME not in caplog.text


@pytest.mark.parametrize("field,code", [("full_name", "invalid_name"), ("birth_date", "invalid_birth_date"),
                                       ("utc_datetime", "invalid_utc_datetime"), ("latitude", "invalid_coordinates"),
                                       ("longitude", "invalid_coordinates")])
def test_missing_required_fields(client, field, code):
    assert_error(client.post(URL, json={k: v for k, v in BODY.items() if k != field}), code)


@pytest.mark.parametrize("field", ["house_system", "city", "country", "district", "birth_time", "extra"])
def test_extra_fields_rejected(client, field):
    assert_error(client.post(URL, json={**BODY, field: NAME}), "invalid_request")


@pytest.mark.parametrize("raw", ["", "null", "[]", '"Synthetic Privacy Sentinel"', "123", '{"full_name":'])
def test_malformed_empty_non_object_body(client, raw):
    assert_error(client.post(URL, content=raw, headers={"Content-Type": "application/json"}), "invalid_request")


def test_empty_object_and_error_precedence(client):
    assert_error(client.post(URL, json={}), "invalid_name")
    assert_error(client.post(URL, json={"unexpected": NAME}), "invalid_request")


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_coordinates(client, value):
    response = client.post(URL, content=json.dumps({**BODY, "latitude": value}), headers={"Content-Type": "application/json"})
    assert_error(response, "invalid_coordinates")


@pytest.mark.parametrize("name,code", [("   ", "invalid_name"), ("Synthetic Ω", "unsupported_name_characters")])
def test_real_numerology_name_error_path(client, name, code):
    assert_error(client.post(URL, json={**BODY, "full_name": name}), code)


@pytest.mark.parametrize("stamp,status", [("2026-09-20T11:59:59.999999Z", 200),
                                          ("2026-09-20T12:00:00Z", 200),
                                          ("2026-09-20T12:00:00.000001Z", 422)])
def test_exact_instant_admission(client, monkeypatch, stamp, status):
    spy = Mock(wraps=calculate_life_code)
    monkeypatch.setattr(api, "calculate_life_code", spy)
    response = client.post(URL, json={**BODY, "birth_date": "2026-09-20", "utc_datetime": stamp})
    assert response.status_code == status
    assert spy.call_count == int(status == 200)
    if status == 422:
        assert_error(response, "invalid_utc_datetime")


@pytest.mark.parametrize("today,birth,status", [(date(2026, 9, 20), "2026-09-21", 422),
                                               (date(2026, 9, 21), "2026-09-21", 200)])
def test_calendar_today_preserves_numerology_not_utc_day(client, today, birth, status):
    # Calendar dependency may differ from UTC date. No new timezone/equality rule.
    client.app.dependency_overrides[api.validation_today] = lambda: today
    body = {**BODY, "birth_date": birth, "utc_datetime": "2026-09-20T11:00:00Z"}
    unified = client.post(URL, json=body)
    standalone = client.post("/api/v1/numerology/calculate", json={k: body[k] for k in ("full_name", "birth_date", "target_year")})
    assert unified.status_code == standalone.status_code == status
    if status == 422:
        assert_error(unified, "invalid_birth_date")
    else:
        assert unified.json()["numerology"] == standalone.json()


@pytest.mark.parametrize("stamp", ["1800-01-01T00:00:00Z", "2100-12-31T23:59:59Z"])
def test_supported_utc_edges_with_explicit_clocks(client, stamp):
    client.app.dependency_overrides[api.validation_now] = lambda: datetime(2101, 1, 1, tzinfo=timezone.utc)
    client.app.dependency_overrides[api.validation_today] = lambda: date(2101, 1, 1)
    assert client.post(URL, json={**BODY, "birth_date": stamp[:10], "utc_datetime": stamp}).status_code == 200


@pytest.mark.parametrize("year", [1, 9999])
def test_target_year_edges(client, year):
    response = client.post(URL, json={**BODY, "target_year": year})
    assert response.status_code == 200
    assert response.json()["numerology"]["metadata"]["target_year"] == year


@pytest.mark.parametrize("error_type,code,status", [
    (NumerologyError, "invalid_name", 422), (NumerologyError, "unsupported_name_characters", 422),
    (AstrologyError, "ephemeris_error", 503), (AstrologyError, "house_calculation_error", 422),
    (HumanDesignError, "invalid_utc_datetime", 422), (HumanDesignError, "unsupported_date_range", 422),
    (HumanDesignError, "ephemeris_error", 503), (HumanDesignError, "design_moment_error", 503),
    (HumanDesignError, "classification_error", 503),
])
def test_domain_errors_use_static_messages(client, monkeypatch, caplog, error_type, code, status):
    caplog.set_level("DEBUG")
    secret = f"{NAME} {BODY['utc_datetime']} {BODY['latitude']} SyntheticNativeMarker /private/path traceback"
    spy = Mock(side_effect=error_type(code, secret))
    monkeypatch.setattr(api, "calculate_life_code", spy)
    assert_error(client.post(URL, json=BODY), code, status)
    spy.assert_called_once()
    assert NAME not in caplog.text
    assert "SyntheticNativeMarker" not in caplog.text


@pytest.mark.parametrize("field,code", [*api.FIELD_CODES.items(), ("SyntheticNativeMarker", "invalid_request")])
def test_internal_input_error_mapping(client, monkeypatch, field, code):
    monkeypatch.setattr(api, "calculate_life_code", Mock(side_effect=LifeCodeInputError(field)))
    assert_error(client.post(URL, json=BODY), code)


def test_programming_errors_are_not_swallowed(client, monkeypatch):
    monkeypatch.setattr(api, "calculate_life_code", Mock(side_effect=RuntimeError("Programming failure")))
    with pytest.raises(RuntimeError, match="Programming failure"):
        client.post(URL, json=BODY)


def test_canonical_repeat_and_default_target_year(client):
    responses = [client.post(URL, json=BODY), client.post(URL, json=BODY),
                 client.post(URL, json={**BODY, "utc_datetime": BODY["utc_datetime"].replace("Z", "+00:00")}),
                 client.post(URL, json={k: v for k, v in BODY.items() if k != "target_year"})]
    assert all(r.status_code == 200 for r in responses)
    assert all(r.content == responses[0].content for r in responses)
    assert responses[0].json()["numerology"]["personal_year"] is None


def test_small_parallel_request_repeatability(client):
    bodies = [BODY, {**BODY, "latitude": -20.0, "longitude": -60.0, "target_year": 2027}]
    expected = [client.post(URL, json=body).content for body in bodies]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(client.post, URL, json=body) for body in bodies * 2]
        responses = [future.result(timeout=15) for future in futures]
    assert all(r.status_code == 200 for r in responses)
    assert [r.content for r in responses] == expected * 2


@pytest.mark.parametrize("coords", [(-90, -180), (90, 180)])
def test_coordinate_contract_accepts_inclusive_edges(coords):
    # Domain Placidus failure at poles is separate from coordinate admission.
    parsed = LifeCodeRequest.model_validate({**BODY, "latitude": coords[0], "longitude": coords[1]})
    assert (parsed.latitude, parsed.longitude) == coords


def test_transport_metadata_is_strict():
    with pytest.raises(ValidationError):
        LifeCodeMetadataResponse.model_validate_json(json.dumps({**METADATA, "interpretation_present": True}))
    with pytest.raises(ValidationError):
        LifeCodeMetadataResponse.model_validate_json(json.dumps({**METADATA, "full_name": NAME}))


def test_registration_preserves_disabled_docs(client):
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 404
    route = next(r for r in api.router.routes if r.path == URL)
    assert route.response_model is LifeCodeResponse
    assert set(route.responses) == {422, 503}
