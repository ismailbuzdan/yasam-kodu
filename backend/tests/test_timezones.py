import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api.timezones import get_timezone_service
from app.core.config import Settings
from app.main import create_app
from app.services.timezone_service import TimezoneError, TimezoneService, convert_to_utc, load_zone

FIXTURES = json.loads((Path(__file__).parent / "fixtures" / "birth_cases.json").read_text(encoding="utf-8"))
CASES = FIXTURES["cases"]
ASTROLOGY_REFERENCES = json.loads(
    (Path(__file__).parent / "fixtures" / "astrology_references.json").read_text(encoding="utf-8")
)


@pytest.fixture(scope="module")
def service():
    return TimezoneService()


@pytest.fixture
def client(service):
    app = create_app(Settings(app_env="test", _env_file=None))
    app.dependency_overrides[get_timezone_service] = lambda: service
    with TestClient(app) as client:
        yield client


def payload(**overrides):
    case = CASES[0]
    return dict(latitude=case["location"]["latitude"], longitude=case["location"]["longitude"],
                birth_date=case["birth"]["local_date"], birth_time=case["birth"]["local_time"]) | overrides


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_historical_fixtures(client, case):
    # Fixed independent expectations catch accidental use of today's UTC offset.
    result = client.post("/api/v1/timezones/resolve", json=payload(
        latitude=case["location"]["latitude"], longitude=case["location"]["longitude"],
        birth_date=case["birth"]["local_date"], birth_time=case["birth"]["local_time"],
    ))
    assert result.status_code == 200
    body = result.json()
    assert body["timezone"] == case["timezone"]["iana"]
    assert datetime.fromisoformat(body["utc_datetime"]) == datetime.fromisoformat(case["timezone"]["expected_utc"])
    assert body["utc_offset_minutes"] == case["timezone"]["expected_offset_minutes"]
    assert body["dst"] == case["timezone"]["expected_dst"]
    assert datetime.fromisoformat(body["local_datetime"]).replace(tzinfo=None) == datetime.fromisoformat(case["birth"]["local_date"] + "T" + case["birth"]["local_time"])
    assert datetime.fromisoformat(body["utc_datetime"]).utcoffset().total_seconds() == 0


def test_birth_fixture_is_synthetic_and_exact() -> None:
    assert FIXTURES["schema_version"] == 1
    assert all(case["id"].startswith("synthetic_") for case in CASES)
    assert all(case["location"]["district"] is None for case in CASES)
    assert len({case["id"] for case in CASES}) == len(CASES)
    assert all(case["birth"]["time_accuracy"] == "exact" for case in CASES)
    assert all("first_name" not in case and "last_name" not in case for case in CASES)


def test_astrology_reference_fixture_contains_no_unverified_expectations() -> None:
    assert ASTROLOGY_REFERENCES["schema_version"] == 1
    for record in ASTROLOGY_REFERENCES["reference_records"]:
        assert record["case_id"] in {case["id"] for case in CASES}
        assert record["reference_source"]["name"]
        assert record["reference_source"]["retrieved_at"]
        assert record["reference_source"]["artifacts"]
    assert all(value is None for value in ASTROLOGY_REFERENCES["record_template"]["expected"].values())


@pytest.mark.parametrize("field,value,code", [("latitude",91,"invalid_coordinates"),("longitude",-181,"invalid_coordinates"),("birth_date","1999-02-30","invalid_datetime"),("birth_time","25:00","invalid_datetime"),("birth_time","20:00+03:00","invalid_datetime"),("birth_time",None,"invalid_datetime")])
def test_invalid_request(client, field, value, code):
    result = client.post("/api/v1/timezones/resolve", json=payload(**{field:value}))
    assert result.status_code == 422
    assert result.json()["detail"]["code"] == code


def test_ocean_has_no_land_timezone(client):
    result = client.post("/api/v1/timezones/resolve", json=payload(latitude=0,longitude=-140))
    assert result.status_code == 404
    assert result.json()["detail"]["code"] == "timezone_not_found"


def test_new_york_fall_overlap(client):
    result = client.post("/api/v1/timezones/resolve", json=payload(latitude=40.7,longitude=-74.0,birth_date="2020-11-01",birth_time="01:30"))
    assert result.status_code == 409
    detail = result.json()["detail"]
    assert detail["code"] == "ambiguous_local_time"
    assert [datetime.fromisoformat(c["utc_datetime"]).isoformat() for c in detail["candidates"]] == ["2020-11-01T05:30:00+00:00","2020-11-01T06:30:00+00:00"]
    assert [c["fold"] for c in detail["candidates"]] == [0,1]
    assert [c["dst"] for c in detail["candidates"]] == [True,False]


def test_new_york_spring_gap(client):
    result = client.post("/api/v1/timezones/resolve", json=payload(latitude=40.7,longitude=-74.0,birth_date="2020-03-08",birth_time="02:30"))
    assert result.status_code == 422
    assert result.json()["detail"]["code"] == "nonexistent_local_time"


def test_data_unavailable_endpoint(client, monkeypatch, service):
    def unavailable(*args):
        raise TimezoneError("timezone_data_unavailable", "Saat dilimi verisi kullanılamıyor.")
    monkeypatch.setattr(service, "resolve_timezone", unavailable)
    assert client.post("/api/v1/timezones/resolve", json=payload()).status_code == 503


def test_missing_zone_is_domain_error():
    with pytest.raises(TimezoneError, match="kullanılamıyor"):
        load_zone("Unknown/Zone")


def test_naive_utc_is_rejected():
    with pytest.raises(TimezoneError) as error:
        convert_to_utc(datetime(2000,1,1))
    assert error.value.code == "invalid_datetime"


def test_lookup_data_failure():
    service = TimezoneService()
    service._finder = Mock()
    service._finder.timezone_at_land.side_effect = OSError("private path")
    with pytest.raises(TimezoneError) as error:
        service.resolve_timezone(41,36)
    assert error.value.code == "timezone_data_unavailable"


@pytest.mark.parametrize("latitude,longitude", [(float("nan"),0),(0,float("inf")),(-91,0),(0,181)])
def test_service_coordinate_bounds(latitude, longitude):
    with pytest.raises(TimezoneError) as error:
        TimezoneService().resolve_timezone(latitude,longitude)
    assert error.value.code == "invalid_coordinates"
