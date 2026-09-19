"""Synthetic API adapter tests; behavioral goldens stay source-owned and unchanged."""
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from app.api import human_design as api
from app.core.config import Settings
from app.main import create_app
from app.schemas.human_design import HumanDesignActivation, HumanDesignResponse
from app.services.human_design_core import calculate_human_design_core
from app.services.human_design_models import HumanDesignError

URL = "/api/v1/human-design/calculate"
STAMP = "2000-03-20T00:00:00Z"
NOW = datetime(2026, 9, 19, 12, tzinfo=timezone.utc)
REFS = json.loads((Path(__file__).parent / "fixtures/human_design_references.json").read_text())
CASE_IDS = {"hd_synthetic_03", "hd_rare_profile36", "hd_rare_ego_manifested",
            "hd_rare_ego_projected", "hd_rare_environmental", "hd_rare_reflector", "hd_rare_self"}
CASES = [c for c in REFS["accepted_expectations"] if c["case_id"] in CASE_IDS]


@pytest.fixture
def client():
    app = create_app(Settings(app_env="test"))
    app.dependency_overrides[api.validation_now] = lambda: NOW
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["case_id"])
def test_official_representatives_and_exact_core_adapter(client, monkeypatch, case):
    stamp = datetime.fromisoformat(case["utc_datetime"])
    core = calculate_human_design_core(stamp)
    spy = Mock(wraps=calculate_human_design_core)
    monkeypatch.setattr(api, "calculate_human_design_core", spy)
    response = client.post(URL, json={"utc_datetime": case["utc_datetime"]})
    assert response.status_code == 200
    spy.assert_called_once_with(stamp)
    data = response.json()
    expected = case["expected"]
    for field in ("type", "authority", "definition"):
        assert data[field] == getattr(core, field) == expected[field]
    assert data["profile"] == asdict(core.profile)
    assert data["profile"]["label"] == expected["profile"]
    assert data["strategy"] == core.strategy
    assert data["metadata"] == json.loads(json.dumps(asdict(core.metadata)))
    assert datetime.fromisoformat(data["birth_utc"]) == core.birth_utc
    assert datetime.fromisoformat(data["design_utc"]) == core.astronomy.design_utc
    for side, activations in (("personality", core.astronomy.personality),
                              ("design", core.astronomy.design_activations)):
        assert data[side] == [asdict(a) for a in activations]  # includes exact, unrounded floats
        assert [{k: a[k] for k in ("body", "gate", "line")} for a in data[side]] == expected[side]
        assert len(data[side]) == 13
    for field in ("active_gates", "channels", "defined_centers", "undefined_centers", "definition_components"):
        assert data[field] == json.loads(json.dumps(getattr(core, field)))
        assert data[field] == sorted(data[field])
    assert data["component_count"] == core.component_count
    assert set(data) == set(HumanDesignResponse.model_fields)
    assert HumanDesignResponse.model_validate_json(response.content).model_dump(mode="json") == data
    for forbidden in ("name", "location", "latitude", "personality_jd_ut1", "jd_ut1",
                      "bracket_seconds", "residual_degrees", "iterations"):
        assert f'"{forbidden}"' not in response.text


def test_representative_inventory():
    assert len(CASES) == 7
    assert {c["expected"]["type"] for c in CASES} == {
        "generator", "manifesting_generator", "manifestor", "projector", "reflector"}
    assert {"ego_manifested", "ego_projected", "self_projected", "mental_environmental", "lunar"} <= {
        c["expected"]["authority"] for c in CASES}


@pytest.mark.parametrize("value", [
    "2000-01-01T12:00:00", "2000-01-01", "invalid-private-marker", "2000-02-30T00:00:00Z",
    "2000-01-01T12:00:00+03:00", "2000-01-01T12:00:00-01:00", "2000-01-01T12:00:60Z",
    "2000-01-01T12:00:00.1234567Z", "946728000", 946728000, 946728000.0, True, None, [], {},
])
def test_invalid_datetime_never_reaches_core(client, monkeypatch, value):
    core = Mock()
    monkeypatch.setattr(api, "calculate_human_design_core", core)
    response = client.post(URL, json={"utc_datetime": value})
    assert response.status_code == 422
    assert response.json() == {"detail": {"code": "invalid_utc_datetime", "message": api.MESSAGES["invalid_utc_datetime"]}}
    core.assert_not_called()


@pytest.mark.parametrize("body,code", [
    ({}, "invalid_utc_datetime"), ([], "invalid_request"),
    ({"utc_datetime": STAMP, "name": "synthetic-private-marker"}, "invalid_request"),
    ({"utc_datetime": STAMP, "location": "synthetic-private-marker"}, "invalid_request"),
    ({"utc_datetime": STAMP, "latitude": 0, "longitude": 0}, "invalid_request"),
    ({"utc_datetime": "1799-12-31T23:59:59Z"}, "unsupported_date_range"),
    ({"utc_datetime": "2101-01-01T00:00:00Z"}, "unsupported_date_range"),
    ({"utc_datetime": "2101-01-01T00:00:00Z", "extra": True}, "invalid_request"),
])
def test_request_errors_are_private(client, monkeypatch, caplog, body, code):
    core = Mock()
    monkeypatch.setattr(api, "calculate_human_design_core", core)
    response = client.post(URL, json=body)
    assert response.status_code == 422
    assert response.json() == {"detail": {"code": code, "message": api.MESSAGES[code]}}
    assert "synthetic-private-marker" not in response.text + caplog.text
    assert STAMP not in response.text + caplog.text
    core.assert_not_called()


@pytest.mark.parametrize("body", ['{"utc_datetime":"synthetic-private-marker",', "", "null"])
def test_malformed_or_empty_body(client, body):
    response = client.post(URL, content=body, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_request"
    assert "synthetic-private-marker" not in response.text


@pytest.mark.parametrize("stamp", ["1800-01-01T00:00:00Z", "2100-12-31T23:59:59.999999+00:00"])
def test_supported_range_edges(client, stamp):
    client.app.dependency_overrides[api.validation_now] = lambda: datetime(2101, 1, 1, tzinfo=timezone.utc)
    response = client.post(URL, json={"utc_datetime": stamp})
    assert response.status_code == 200
    assert datetime.fromisoformat(response.json()["birth_utc"]) == datetime.fromisoformat(stamp)


@pytest.mark.parametrize("stamp,accepted", [
    ("2026-09-19T11:59:59.999999Z", True), ("2026-09-19T12:00:00Z", True),
    ("2026-09-19T12:00:00.000001Z", False), ("2026-09-20T00:00:00Z", False),
])
def test_exact_future_admission_clock(client, monkeypatch, stamp, accepted):
    spy = Mock(wraps=calculate_human_design_core)
    monkeypatch.setattr(api, "calculate_human_design_core", spy)
    response = client.post(URL, json={"utc_datetime": stamp})
    assert response.status_code == (200 if accepted else 422)
    assert spy.call_count == int(accepted)
    if not accepted:
        assert response.json()["detail"]["code"] == "invalid_utc_datetime"
        assert stamp not in response.text


@pytest.mark.parametrize("code,status", [
    ("invalid_utc_datetime", 422), ("unsupported_date_range", 422),
    ("ephemeris_error", 503), ("design_moment_error", 503), ("classification_error", 503),
])
def test_safe_domain_error_mapping(client, monkeypatch, caplog, code, status):
    private = f"synthetic-private-marker {STAMP} /private/swiss/file swe.Error traceback"
    monkeypatch.setattr(api, "calculate_human_design_core", Mock(side_effect=HumanDesignError(code, private)))
    response = client.post(URL, json={"utc_datetime": STAMP})
    assert response.status_code == status
    assert response.json() == {"detail": {"code": code, "message": api.MESSAGES[code]}}
    assert private not in response.text + caplog.text
    assert STAMP not in response.text + caplog.text


def test_repeatable_json_and_equivalent_utc_spellings(client, caplog):
    responses = [client.post(URL, json={"utc_datetime": stamp}) for stamp in
                 (STAMP, STAMP, STAMP.replace("Z", "+00:00"), STAMP.replace("Z", "+0000"))]
    assert all(r.status_code == 200 for r in responses)
    assert all(r.content == responses[0].content for r in responses)
    assert responses[0].json()["birth_utc"].endswith("Z")
    assert STAMP not in caplog.text


@pytest.mark.parametrize("update", [{"gate": "1"}, {"line": True}, {"longitude": float("nan")},
                                    {"body": "chiron"}, {"longitude": 360.0}, {"extra": 1}])
def test_activation_schema_is_strict(update):
    with pytest.raises(ValidationError):
        HumanDesignActivation.model_validate({"body": "sun", "longitude": 0.0, "gate": 1, "line": 1, **update})


def test_registration_does_not_enable_docs(client):
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 404
    route = next(r for r in api.router.routes if r.path == URL)
    assert route.response_model is HumanDesignResponse
    assert set(route.responses) == {422, 503}
