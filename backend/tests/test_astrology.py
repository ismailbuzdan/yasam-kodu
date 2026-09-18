"""Invariants and real-library smoke tests, NOT independent accuracy references."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest
import swisseph as swe
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.schemas.astrology import AstrologyRequest, AstrologyResponse, BodyPosition
from app.services.astrology_service import (
    AstrologyService, angular_distance, aspects_for, house_for,
    is_retrograde, normalize_longitude, position,
)

CASES = json.loads((Path(__file__).parent / "fixtures/birth_cases.json").read_text(encoding="utf-8"))["cases"]


def payload(case=CASES[0], **overrides):
    return dict(utc_datetime=case["timezone"]["expected_utc"],
                latitude=case["location"]["latitude"],
                longitude=case["location"]["longitude"]) | overrides


@pytest.fixture
def client():
    with TestClient(create_app(Settings(app_env="test", _env_file=None))) as client:
        yield client


@pytest.mark.parametrize("value,expected", [(-1,359),(0,0),(360,0),(721,1),(-720,0),(-1e-16,0)])
def test_longitude_normalization(value, expected):
    assert normalize_longitude(value) == expected


@pytest.mark.parametrize("index,sign", list(enumerate(("aries", "taurus", "gemini", "cancer", "leo", "virgo",
                                                "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"))))
def test_sign_and_degree(index, sign):
    result = position(index * 30 + 12.5)
    assert result.sign == sign
    assert result.degree_in_sign == 12.5
    assert position(index * 30).degree_in_sign == 0
    assert position(360).sign == "aries"


@pytest.mark.parametrize("speed,expected", [(-0.001,True),(0,False),(0.001,False)])
def test_retrograde(speed, expected):
    assert is_retrograde(speed) is expected


@pytest.mark.parametrize("first,second,expected", [(359,1,2),(1,359,2),(0,180,180),(0,360,0)])
def test_circular_distance(first, second, expected):
    assert angular_distance(first, second) == expected


@pytest.mark.parametrize("longitude,house", [(349,12),(350,1),(359,1),(0,1),(19.99,1),(20,2),(320,12)])
def test_house_wrap(longitude, house):
    cusps = tuple((350 + i * 30) % 360 for i in range(12))
    assert house_for(longitude, cusps) == house


def body(longitude):
    return BodyPosition(**position(longitude).model_dump(), speed_longitude=1, retrograde=False, house=1)


@pytest.mark.parametrize("angle,kind", [(0,"conjunction"),(60,"sextile"),(90,"square"),(120,"trine"),(180,"opposition")])
def test_aspects(angle, kind):
    result = aspects_for({"mars": body(0), "venus": body(angle)})
    assert len(result) == 1
    assert result[0].type == kind
    assert result[0].orb == 0
    assert result[0].applying is None


@pytest.mark.parametrize("name,longitude,count", [("sun",8,1),("sun",8.01,0),("mars",6,1),
                                                  ("mars",6.01,0),("sun",64,1),("sun",64.01,0)])
def test_orb_boundaries(name, longitude, count):
    assert len(aspects_for({name: body(0), "venus": body(longitude)})) == count


def test_aspect_wrap():
    aspect = aspects_for({"mars": body(359), "venus": body(1)})[0]
    assert aspect.type == "conjunction"
    assert aspect.separation == aspect.orb == 2


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_real_wrapper_invariants(case):
    request = AstrologyRequest(**payload(case))
    result = AstrologyService().calculate(request)
    assert result == AstrologyService().calculate(request)
    assert set(result.bodies) == {"sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
                                 "uranus", "neptune", "pluto", "true_north_node", "south_node", "lilith"}
    assert result.metadata.ephemeris == "moshier"
    assert len(result.houses) == 12
    for value in [*result.bodies.values(), result.ascendant, result.mc, *result.houses]:
        assert 0 <= value.longitude < 360
        assert 0 <= value.degree_in_sign < 30
    for value in result.bodies.values():
        assert 1 <= value.house <= 12
        assert value.retrograde == (value.speed_longitude < 0)
    north, south = result.bodies["true_north_node"], result.bodies["south_node"]
    assert south.longitude == normalize_longitude(north.longitude + 180)
    assert south.speed_longitude == north.speed_longitude


@pytest.mark.parametrize("field,value,code", [
    ("latitude",91,"invalid_coordinates"),("longitude",-181,"invalid_coordinates"),
    ("latitude","NaN","invalid_coordinates"),("longitude","Infinity","invalid_coordinates"),
    ("utc_datetime","invalid","invalid_utc_datetime"),("utc_datetime",None,"invalid_utc_datetime"),
    ("utc_datetime",0,"invalid_utc_datetime"),("house_system","whole_sign","unsupported_house_system"),
])
def test_invalid_request(client, field, value, code):
    response = client.post("/api/v1/astrology/calculate", json=payload(**{field:value}))
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == code


@pytest.mark.parametrize("suffix", ["", "+03:00"])
def test_requires_aware_zero_offset(client, suffix):
    value = payload()["utc_datetime"].removesuffix("Z") + suffix
    response = client.post("/api/v1/astrology/calculate", json=payload(utc_datetime=value))
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_utc_datetime"


@pytest.mark.parametrize("field", ["utc_datetime", "latitude", "longitude"])
def test_missing_field(client, field):
    data = payload()
    del data[field]
    assert client.post("/api/v1/astrology/calculate", json=data).status_code == 422


@pytest.mark.parametrize("latitude", [-89,89])
def test_high_latitude_has_no_fallback(client, latitude):
    # Synthetic boundary mutation of a shared case, not a new birth reference.
    response = client.post("/api/v1/astrology/calculate", json=payload(latitude=latitude))
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "house_calculation_error"
    assert "bodies" not in response.json()


def test_api_schema(client):
    response = client.post("/api/v1/astrology/calculate", json=payload())
    assert response.status_code == 200
    result = AstrologyResponse.model_validate(response.json())
    assert result.metadata.system == "tropical"
    assert result.metadata.house_system == "placidus"
    assert result.metadata.node_type == "true"
    assert result.metadata.lilith_type == "mean_black_moon"


@pytest.mark.parametrize("method,code,status", [("calc","ephemeris_error",503),
    ("utc_to_jd","ephemeris_error",503),("houses_ex","house_calculation_error",422)])
def test_native_errors_are_sanitized(client, method, code, status):
    with patch(f"app.services.astrology_service.swe.{method}", side_effect=swe.Error("private native path")):
        response = client.post("/api/v1/astrology/calculate", json=payload())
    assert response.status_code == status
    assert response.json()["detail"]["code"] == code
    assert "private" not in response.text


def test_unexpected_ephemeris_mode_rejected(client):
    with patch("app.services.astrology_service.swe.calc", return_value=((0,0,0,0,0,0), swe.FLG_SWIEPH)):
        response = client.post("/api/v1/astrology/calculate", json=payload())
    assert response.status_code == 503


def test_nonfinite_native_speed_rejected(client):
    with patch("app.services.astrology_service.swe.calc",
               return_value=((0,0,0,float("nan"),0,0), swe.FLG_MOSEPH | swe.FLG_SPEED)):
        response = client.post("/api/v1/astrology/calculate", json=payload())
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "ephemeris_error"


def test_out_of_range_ephemeris_date(client):
    request = AstrologyRequest(**payload())
    value = request.utc_datetime.replace(year=9999).isoformat()
    response = client.post("/api/v1/astrology/calculate", json=payload(utc_datetime=value))
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "ephemeris_error"


def test_tt_and_ut1_are_routed_to_correct_functions():
    # Synthetic native boundary values verify wiring, not astronomical accuracy.
    with patch("app.services.astrology_service.swe.utc_to_jd", return_value=(100.5,100.4)), \
         patch("app.services.astrology_service.swe.houses_ex",
               return_value=(tuple(i * 30 for i in range(12)), (0,270,0))) as houses, \
         patch("app.services.astrology_service.swe.calc",
               return_value=((10,0,0,1,0,0), swe.FLG_MOSEPH | swe.FLG_SPEED)) as calc:
        request = AstrologyRequest(**payload())
        AstrologyService().calculate(request)
    houses.assert_called_once_with(100.4, request.latitude, request.longitude, b"P", 0)
    assert all(call.args[0] == 100.5 for call in calc.call_args_list)
