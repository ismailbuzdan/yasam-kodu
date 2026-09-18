"""Boundary, initialization, and validation tests prompted by the Stage 7 audit."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
import pytest
import swisseph as swe

from app.core.config import Settings
from app.main import create_app
from app.schemas.astrology import AstrologyRequest, BodyPosition
from app.services import astrology_service as engine

ROOT = Path(__file__).parent / "fixtures"
CASES = json.loads((ROOT / "birth_cases.json").read_text(encoding="utf-8"))["cases"]
REFS = {r["case_id"]:r for r in json.loads((ROOT / "astrology_references.json").read_text())["reference_records"]}


def payload(case=CASES[0], **overrides):
    return dict(utc_datetime=case["timezone"]["expected_utc"],latitude=case["location"]["latitude"],
                longitude=case["location"]["longitude"]) | overrides


@pytest.fixture
def client():
    with TestClient(create_app(Settings(app_env="test", _env_file=None))) as client:
        yield client


def test_initialization_before_every_worker_calculation():
    actual_path, actual_utc = swe.set_ephe_path, swe.utc_to_jd
    events = []
    def set_path(path):
        assert Path(path).is_dir()
        assert not list(Path(path).iterdir())
        events.append("init")
        return actual_path(path)
    def utc(*args):
        events.append("utc")
        return actual_utc(*args)
    req = AstrologyRequest(**payload())
    with patch.object(swe,"set_ephe_path",side_effect=set_path), patch.object(swe,"utc_to_jd",side_effect=utc):
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _:engine.AstrologyService().calculate(req),range(12)))
    assert events == ["init","utc"] * 12
    assert all(r == results[0] for r in results)


def test_external_ephemeris_override_rejected(client, monkeypatch):
    monkeypatch.setenv("SE_EPHE_PATH", "external-data-directory")
    response = client.post("/api/v1/astrology/calculate", json=payload())
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "ephemeris_error"


def test_changed_native_time_model_reset():
    req = AstrologyRequest(**payload())
    expected = engine.AstrologyService().calculate(req)
    swe.set_delta_t_userdef(1.0)
    swe.set_tid_acc(-50)
    assert engine.AstrologyService().calculate(req) == expected


@pytest.mark.parametrize("case", CASES, ids=lambda c:c["id"])
def test_native_placement_receives_external_verified_latitudes(case):
    actual = swe.house_pos
    calls = []
    def spy(armc, geolat, eps, coord, hsys):
        calls.append(coord)
        return actual(armc,geolat,eps,coord,hsys)
    with patch.object(swe,"house_pos",side_effect=spy):
        engine.AstrologyService().calculate(AstrologyRequest(**payload(case)))
    for index, name in enumerate(engine.BODIES):
        expected = REFS[case["id"]]["expected"]["swetest_bodies"][name]
        assert abs(calls[index][1] - expected["latitude"]) < 1e-6
    assert calls[-1][1] == 0.0  # South lunar node lies on the ecliptic.


def geometry():
    req = AstrologyRequest(**payload())
    dt = req.utc_datetime
    with engine._LOCK:
        engine.initialize_ephemeris()
        tt, ut = swe.utc_to_jd(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)
        cusps, angles = swe.houses_ex(ut,req.latitude,req.longitude,b"P")
        eps = swe.calc(tt,swe.ECL_NUT,swe.FLG_MOSEPH)[0][0]
    return req.latitude,cusps,angles[2],eps


@pytest.mark.parametrize("index", range(12))
def test_exact_zero_latitude_cusp_belongs_to_starting_house(index):
    lat,cusps,armc,eps = geometry()
    assert engine.placidus_house(cusps[index],0,armc,lat,eps,cusps) == index + 1


def test_native_house_12_to_1_and_longitude_wrap():
    lat,cusps,armc,eps = geometry()
    assert engine.placidus_house((cusps[0] - 0.0001) % 360,0,armc,lat,eps,cusps) == 12
    assert engine.placidus_house((cusps[0] + 0.0001) % 360,0,armc,lat,eps,cusps) == 1
    assert engine.placidus_house(0,0,armc,lat,eps,cusps) == engine.placidus_house(360,0,armc,lat,eps,cusps)


def test_house_pos_native_exception_sanitized(client):
    with patch.object(swe,"house_pos",side_effect=swe.Error("private implementation path")):
        response = client.post("/api/v1/astrology/calculate",json=payload())
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "house_calculation_error"
    assert "private" not in response.text


@pytest.mark.parametrize("value", [0,13,float("nan")])
def test_invalid_native_house_result_rejected(client,value):
    with patch.object(swe,"house_pos",return_value=value):
        response = client.post("/api/v1/astrology/calculate",json=payload())
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "house_calculation_error"


def synthetic_body(longitude):
    return BodyPosition(**engine.position(longitude).model_dump(),house=1,speed_longitude=1,retrograde=False)


@pytest.mark.parametrize("kind,angle", list(engine.ASPECT_ANGLES.items()))
@pytest.mark.parametrize("name,base_orb", [("sun",8),("moon",8),("mars",6)])
@pytest.mark.parametrize("outside", [False,True])
def test_all_aspect_orb_boundaries(kind,angle,name,base_orb,outside):
    orb = 4 if kind == "sextile" else base_orb
    delta = orb + (1e-6 if outside else 0)
    separation = angle - delta if angle == 180 else angle + delta
    aspects = engine.aspects_for({name:synthetic_body(0),"venus":synthetic_body(separation)})
    assert any(a.type == kind for a in aspects) is (not outside)


def test_nodes_lilith_mapping_and_inclusion():
    assert engine.BODIES["true_north_node"] == swe.TRUE_NODE == 11
    assert engine.BODIES["lilith"] == swe.MEAN_APOG == 12
    aspects = engine.aspects_for({"true_north_node":synthetic_body(0),
                                 "south_node":synthetic_body(180),"lilith":synthetic_body(60)})
    assert {(a.body1,a.body2,a.type) for a in aspects} == {
        ("true_north_node","south_node","opposition"),
        ("true_north_node","lilith","sextile"),("south_node","lilith","trine")}


@pytest.mark.parametrize("data,code", [({"extra":1},"invalid_request"),
    ({"latitude":91},"invalid_coordinates"),({"longitude":181},"invalid_coordinates"),
    ({"house_system":"equal"},"unsupported_house_system"),({"utc_datetime":None},"invalid_utc_datetime")])
def test_validation_codes(client,data,code):
    response = client.post("/api/v1/astrology/calculate",json=payload(**data))
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == code


@pytest.mark.parametrize("content", ['[]','null','{"utc_datetime":'])
def test_malformed_or_nonobject_body(client,content):
    response = client.post("/api/v1/astrology/calculate",content=content,headers={"Content-Type":"application/json"})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_request"


def test_explicit_zero_offset_accepted(client):
    value = payload()["utc_datetime"].replace("Z","+00:00")
    assert client.post("/api/v1/astrology/calculate",json=payload(utc_datetime=value)).status_code == 200
