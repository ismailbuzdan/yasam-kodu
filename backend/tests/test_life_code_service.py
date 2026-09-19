"""Synthetic aggregation invariants, not new engine accuracy/golden expectations."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, fields, replace
from datetime import date, datetime, timedelta, timezone
import inspect
import socket
import traceback
from unittest.mock import Mock

import pytest
import swisseph as swe

from app.schemas.astrology import AstrologyRequest
from app.schemas.numerology import NumerologyRequest
from app.services import life_code_service as service
from app.services.astrology_service import AstrologyError, AstrologyService
from app.services.human_design_core import calculate_human_design_core
from app.services.human_design_models import HumanDesignError
from app.services.life_code_models import LifeCodeInput, LifeCodeInputError, LifeCodeMetadata, LifeCodeResult
from app.services.numerology_service import NumerologyError, NumerologyService

# Fictional name and coarse coordinates. Calendar date deliberately differs from UTC date.
INPUT = LifeCodeInput("Ada Test", date(2000, 3, 20),
                      datetime(2000, 3, 19, 22, tzinfo=timezone.utc), 30.0, 30.0)


def direct_astrology(value=INPUT):
    return AstrologyService().calculate(AstrologyRequest(
        utc_datetime=value.utc_datetime, latitude=value.latitude,
        longitude=value.longitude, house_system="placidus"))


def direct_numerology(value=INPUT):
    return NumerologyService().calculate(NumerologyRequest(
        full_name=value.full_name, birth_date=value.birth_date, target_year=value.target_year))


def test_lossless_direct_output_equality():
    result = service.calculate_life_code(INPUT)
    assert isinstance(result, LifeCodeResult)
    assert isinstance(result.metadata, LifeCodeMetadata)
    assert result.astrology == direct_astrology()
    assert result.numerology == direct_numerology()
    assert result.human_design == calculate_human_design_core(INPUT.utc_datetime)
    assert result.astrology.model_dump() == direct_astrology().model_dump()
    assert result.numerology.model_dump() == direct_numerology().model_dump()
    assert set(f.name for f in fields(result)) == {"metadata", "astrology", "numerology", "human_design"}
    assert result.metadata.schema_version == "life-code-v1"
    assert result.metadata.calculation_layers == ("astrology", "numerology", "human_design")
    assert result.metadata.interpretation_present is False


def test_original_object_identity_once_order_and_routing(monkeypatch):
    outputs = (direct_astrology(), direct_numerology(), calculate_human_design_core(INPUT.utc_datetime))
    calls = []
    astrology = Mock(side_effect=lambda request: calls.append(("astrology", request)) or outputs[0])
    numerology = Mock(side_effect=lambda request: calls.append(("numerology", request)) or outputs[1])
    hd = Mock(side_effect=lambda stamp: calls.append(("human_design", stamp)) or outputs[2])
    monkeypatch.setattr(service.AstrologyService, "calculate", astrology)
    monkeypatch.setattr(service.NumerologyService, "calculate", numerology)
    monkeypatch.setattr(service, "calculate_human_design_core", hd)
    result = service.calculate_life_code(INPUT)
    assert [label for label, _ in calls] == ["astrology", "numerology", "human_design"]
    assert astrology.call_count == numerology.call_count == hd.call_count == 1
    a, n = calls[0][1], calls[1][1]
    assert a.model_dump() == dict(utc_datetime=INPUT.utc_datetime, latitude=30.0, longitude=30.0, house_system="placidus")
    assert n.model_dump() == dict(full_name=INPUT.full_name, birth_date=INPUT.birth_date, target_year=None)
    hd.assert_called_once_with(INPUT.utc_datetime)
    assert a.utc_datetime == calls[2][1]
    assert result.astrology is outputs[0]
    assert result.numerology is outputs[1]
    assert result.human_design is outputs[2]


def test_local_calendar_date_is_not_utc_date():
    result = service.calculate_life_code(INPUT)
    assert INPUT.birth_date != INPUT.utc_datetime.date()
    assert result.numerology.birthday.raw_sum == 20  # given calendar day, not UTC day 19
    assert result.numerology.life_path.raw_sum == 7  # 2+0+0+0 + 3 + 2+0
    assert result.numerology == direct_numerology()
    assert result.numerology != direct_numerology(replace(INPUT, birth_date=INPUT.utc_datetime.date()))
    assert result.human_design.birth_utc == INPUT.utc_datetime


def test_target_year_only_affects_numerology():
    left = service.calculate_life_code(replace(INPUT, target_year=2026))
    right = service.calculate_life_code(replace(INPUT, target_year=2027))
    assert left.astrology == right.astrology
    assert left.human_design == right.human_design
    assert left.numerology.personal_year != right.numerology.personal_year
    assert left.numerology.model_dump(exclude={"metadata", "personal_year"}) == right.numerology.model_dump(exclude={"metadata", "personal_year"})
    assert service.calculate_life_code(INPUT).numerology.personal_year is None


def test_name_only_affects_name_dependent_numerology():
    left = service.calculate_life_code(INPUT)
    right = service.calculate_life_code(replace(INPUT, full_name="Bora Test"))
    assert left.astrology == right.astrology
    assert left.human_design == right.human_design
    assert left.numerology.expression != right.numerology.expression
    assert left.numerology.life_path == right.numerology.life_path
    assert left.numerology.birthday == right.numerology.birthday
    assert left.numerology.personal_year == right.numerology.personal_year


def test_coordinates_only_affect_astrology():
    left = service.calculate_life_code(INPUT)
    right = service.calculate_life_code(replace(INPUT, latitude=-20.0, longitude=-60.0))
    assert left.numerology == right.numerology
    assert left.human_design == right.human_design
    assert left.astrology.ascendant != right.astrology.ascendant
    assert left.astrology.mc != right.astrology.mc
    assert left.astrology.houses != right.astrology.houses


def test_repeat_and_concurrent_native_state_isolation():
    inputs = [INPUT, replace(INPUT, utc_datetime=datetime(2002, 6, 14, 12, tzinfo=timezone.utc)),
              replace(INPUT, latitude=-20.0, longitude=-60.0, target_year=2027)]
    expected = [service.calculate_life_code(value) for value in inputs]
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending = [pool.submit(service.calculate_life_code, value) for value in inputs * 3]
        actual = [future.result(timeout=15) for future in pending]
    assert actual == expected * 3
    assert service.calculate_life_code(INPUT) == expected[0]
    assert direct_astrology() == expected[0].astrology
    assert calculate_human_design_core(INPUT.utc_datetime) == expected[0].human_design


def test_frozen_envelope_and_explicit_shallow_boundary():
    result = service.calculate_life_code(INPUT)
    for obj, name, value in ((INPUT, "full_name", "Bora Test"),
                             (result, "astrology", None), (result.metadata, "schema_version", "changed")):
        with pytest.raises(FrozenInstanceError):
            setattr(obj, name, value)
    # User-selected contract: original Pydantic children are NOT recursively frozen.
    result.astrology.bodies["sun"].house = 12
    assert result.astrology.bodies["sun"].house == 12
    result.numerology.metadata.target_year = 2027
    assert result.numerology.metadata.target_year == 2027
    # No global result/cache reuse: mutating one returned child cannot pollute a later call.
    assert service.calculate_life_code(INPUT).numerology.metadata.target_year is None


def test_privacy_and_no_network(monkeypatch, caplog):
    caplog.set_level("DEBUG")
    connect = Mock(side_effect=AssertionError("Network forbidden"))
    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(socket, "create_connection", connect)
    result = service.calculate_life_code(INPUT)
    connect.assert_not_called()
    assert INPUT.full_name not in repr(INPUT) + repr(result) + caplog.text
    assert "ADATEST" not in repr(result) + caplog.text
    assert "full_name" not in repr(result)
    assert caplog.records == []
    source = inspect.getsource(service)
    for forbidden in ("app.api", "timezone_service", "geocoding", "httpx", "requests", "datetime.now", "date.today"):
        assert forbidden not in source


@pytest.mark.parametrize("field_name,value", [
    ("birth_date", "2000-03-20"), ("birth_date", INPUT.utc_datetime), ("birth_date", None),
    ("utc_datetime", "2000-03-19T22:00:00Z"), ("utc_datetime", date(2000, 3, 19)),
    ("utc_datetime", datetime(2000, 3, 19, 22)),
    ("utc_datetime", datetime(2000, 3, 19, 22, tzinfo=timezone(timedelta(hours=3)))),
    ("latitude", 91.0), ("latitude", -91.0), ("latitude", float("nan")),
    ("latitude", float("inf")), ("latitude", True), ("latitude", "30"),
    ("longitude", 181.0), ("longitude", -181.0), ("longitude", float("-inf")),
    ("longitude", False), ("longitude", None),
    ("target_year", 0), ("target_year", 10000), ("target_year", True),
    ("target_year", "2026"), ("target_year", 2026.0),
    ("full_name", None), ("full_name", []), ("full_name", ""), ("full_name", "SyntheticMarker" * 20),
])
def test_invalid_input_is_safe_and_never_calls_engines(monkeypatch, field_name, value):
    engines = [Mock(), Mock(), Mock()]
    monkeypatch.setattr(service.AstrologyService, "calculate", engines[0])
    monkeypatch.setattr(service.NumerologyService, "calculate", engines[1])
    monkeypatch.setattr(service, "calculate_human_design_core", engines[2])
    with pytest.raises(LifeCodeInputError) as caught:
        service.calculate_life_code(replace(INPUT, **{field_name: value}))
    assert caught.value.code == "invalid_input"
    assert caught.value.field == field_name
    rendered = "".join(traceback.format_exception(caught.value))
    assert INPUT.full_name not in rendered
    assert "SyntheticMarker" not in rendered
    assert "input_value" not in rendered
    for engine in engines:
        engine.assert_not_called()


def test_wrong_input_object():
    with pytest.raises(LifeCodeInputError, match="input field: input"):
        service.calculate_life_code({})


@pytest.mark.parametrize("year", [1, 9999])
def test_target_year_contract_edges(year):
    result = service.calculate_life_code(replace(INPUT, target_year=year))
    assert result.numerology.metadata.target_year == year
    assert result.numerology.personal_year is not None


def test_future_input_has_no_admission_clock():
    future = replace(INPUT, birth_date=date(2100, 1, 2), utc_datetime=datetime(2100, 1, 1, 22, tzinfo=timezone.utc))
    result = service.calculate_life_code(future)
    assert result.human_design.birth_utc == future.utc_datetime
    assert result.numerology.personal_year is None


@pytest.mark.parametrize("stage,error", [
    (0, AstrologyError("house_calculation_error", "Safe domain failure.")),
    (1, NumerologyError("unsupported_name_characters", "Safe domain failure.")),
    (2, HumanDesignError("design_moment_error", "Safe domain failure.")),
])
def test_engine_error_identity_and_fail_fast(monkeypatch, stage, error):
    engines = [Mock(), Mock(), Mock()]
    engines[stage].side_effect = error
    monkeypatch.setattr(service.AstrologyService, "calculate", engines[0])
    monkeypatch.setattr(service.NumerologyService, "calculate", engines[1])
    monkeypatch.setattr(service, "calculate_human_design_core", engines[2])
    with pytest.raises(type(error)) as caught:
        service.calculate_life_code(INPUT)
    assert caught.value is error
    for index, engine in enumerate(engines):
        assert engine.call_count == int(index <= stage)


def test_native_exception_cause_is_not_displayed(monkeypatch):
    monkeypatch.setattr(swe, "utc_to_jd", Mock(side_effect=swe.Error("SyntheticNativeMarker /private/path")))
    with pytest.raises(AstrologyError) as caught:
        service.calculate_life_code(INPUT)
    assert caught.value.code == "ephemeris_error"
    assert "SyntheticNativeMarker" not in "".join(traceback.format_exception(caught.value))
    assert caught.value.__suppress_context__ is True


def test_name_domain_failure_stays_private(caplog):
    caplog.set_level("DEBUG")
    with pytest.raises(NumerologyError) as caught:
        service.calculate_life_code(replace(INPUT, full_name="SyntheticMarker123"))
    assert caught.value.code == "invalid_name"
    assert "SyntheticMarker123" not in str(caught.value) + caplog.text


def test_hd_support_range_remains_engine_owned():
    with pytest.raises(HumanDesignError) as caught:
        service.calculate_life_code(replace(INPUT, utc_datetime=datetime(1799, 12, 31, tzinfo=timezone.utc)))
    assert caught.value.code == "unsupported_date_range"
