"""Offline external-reference regression: JPL astronomy + remotely executed swetest.

Swetest shares Swiss algorithms: an integration reference, not independent astronomy.
"""
import hashlib
import json
from pathlib import Path

import pytest

from app.schemas.astrology import AstrologyRequest
from app.services.astrology_service import AstrologyService, angular_distance
from tools.build_astrology_references import load_evidence, parse_swetest

FIXTURES = Path(__file__).parent / "fixtures"
CASES = {c["id"]: c for c in json.loads((FIXTURES / "birth_cases.json").read_text(encoding="utf-8"))["cases"]}
REFERENCES = json.loads((FIXTURES / "astrology_references.json").read_text())["reference_records"]


@pytest.fixture(scope="module", params=REFERENCES, ids=lambda r: r["case_id"])
def reference_and_result(request):
    reference = request.param
    case = CASES[reference["case_id"]]
    result = AstrologyService().calculate(AstrologyRequest(
        utc_datetime=case["timezone"]["expected_utc"], latitude=case["location"]["latitude"],
        longitude=case["location"]["longitude"]))
    return reference, result


@pytest.mark.parametrize("body", ["sun", "moon", "mercury", "jupiter"])
def test_independent_jpl_longitude(reference_and_result, body):
    ref, result = reference_and_result
    expected = ref["expected"]["planet_longitudes"].get(body)
    if expected is None:
        pytest.skip("No independently sourced value")
    assert angular_distance(result.bodies[body].longitude, expected) <= ref["tolerance"]["planet_degrees"]


@pytest.mark.parametrize("angle,key", [("ascendant","ascendant_longitude"),("mc","mc_longitude")])
def test_external_swetest_angles(reference_and_result, angle, key):
    ref, result = reference_and_result
    expected = ref["expected"][key]
    if expected is None:
        pytest.skip("No externally sourced angle")
    assert angular_distance(getattr(result, angle).longitude, expected) <= ref["tolerance"]["angles_degrees"]


@pytest.mark.parametrize("index", range(12))
def test_external_swetest_cusp(reference_and_result, index):
    ref, result = reference_and_result
    assert angular_distance(result.houses[index].longitude, ref["expected"]["house_cusps"][index]) <= ref["tolerance"]["angles_degrees"]


@pytest.mark.parametrize("body", ["sun","moon","mercury","venus","mars","jupiter","saturn",
                                  "uranus","neptune","pluto","true_north_node","lilith"])
def test_external_swetest_body_position_speed_and_house(reference_and_result, body):
    ref, result = reference_and_result
    expected = ref["expected"]["swetest_bodies"][body]
    actual = result.bodies[body]
    assert actual.house == expected["house"]
    assert angular_distance(actual.longitude, expected["longitude"]) <= ref["tolerance"]["swetest_planet_degrees"]
    assert abs(actual.speed_longitude - expected["speed_longitude"]) <= ref["tolerance"]["speed_degrees_per_day"]
    assert actual.retrograde == (expected["speed_longitude"] < 0)


def test_reference_provenance_and_raw_artifacts():
    assert {r["case_id"] for r in REFERENCES} == set(CASES)
    horizons = load_evidence()
    from datetime import datetime
    for ref in REFERENCES:
        for artifact in ref["reference_source"]["artifacts"]:
            content = (FIXTURES / artifact["artifact"]).read_bytes()
            assert hashlib.sha256(content).hexdigest() == artifact["sha256"]
            assert artifact["url"].startswith(("https://ssd.jpl.nasa.gov/", "https://www.astro.com/"))
        dt = datetime.fromisoformat(CASES[ref["case_id"]]["timezone"]["expected_utc"])
        assert ref["expected"]["sun_longitude"] == horizons["sun"][dt]["longitude"]
        assert ref["expected"]["moon_longitude"] == horizons["moon"][dt]["longitude"]
        bodies, cusps, angles = parse_swetest(ref["case_id"])
        assert ref["expected"]["house_cusps"] == cusps
        assert ref["expected"]["swetest_bodies"] == bodies
        assert ref["expected"]["ascendant_longitude"] == angles["Ascendant"]
        assert ref["expected"]["mc_longitude"] == angles["MC"]
