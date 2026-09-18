"""Synthetic, hand-calculated vectors from the Stage 8 convention."""
from datetime import date
import unicodedata

from fastapi.testclient import TestClient
import pytest

from app.api.numerology import validation_today
from app.core.config import Settings
from app.main import create_app
from app.schemas.numerology import NumerologyRequest, NumerologyResponse
from app.services.numerology_service import (
    LETTER_VALUES, NumerologyError, NumerologyService, normalize_name,
    reduce_core_number, reduce_to_single_digit,
)


def calculate(name="Ada Test", birth="2000-02-29", year=2026):
    return NumerologyService().calculate(NumerologyRequest(full_name=name, birth_date=birth, target_year=year))


# Expected values are directly calculated from the requested convention, not engine snapshots.
ADA = {
    "metadata": {"system": "pythagorean", "master_numbers": [11, 22, 33],
                 "vowels": "AEIOU", "y_is_vowel": False, "target_year": 2026},
    "life_path": {"raw_sum": 15, "value": 6, "is_master": False},
    "birthday": {"raw_sum": 29, "value": 11, "is_master": True},
    "expression": {"raw_sum": 16, "value": 7, "is_master": False},
    "soul_urge": {"raw_sum": 7, "value": 7, "is_master": False},
    "personality": {"raw_sum": 9, "value": 9, "is_master": False},
    "maturity": {"raw_sum": 13, "value": 4, "is_master": False},
    "personal_year": {"raw_sum": 23, "value": 5, "is_master": False},
}


@pytest.mark.parametrize("letters,value", [("AJS",1),("BKT",2),("CLU",3),("DMV",4),
                                         ("ENW",5),("FOX",6),("GPY",7),("HQZ",8),("IR",9)])
def test_letter_table(letters, value):
    assert all(LETTER_VALUES[c] == value for c in letters)
    assert set(LETTER_VALUES) == set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


@pytest.mark.parametrize("raw,expected", [(1,1),(9,9),(11,11),(22,22),(33,33),
                                        (29,11),(38,11),(44,8),(199,1),(9999,9)])
def test_master_reduction_chain(raw, expected):
    assert reduce_core_number(raw) == expected


@pytest.mark.parametrize("raw,expected", [(11,2),(22,4),(33,6),(29,2),(38,2),(44,8)])
def test_single_digit_reduction(raw, expected):
    assert reduce_to_single_digit(raw) == expected


@pytest.mark.parametrize("reducer", [reduce_core_number, reduce_to_single_digit])
@pytest.mark.parametrize("value", [0,-1])
def test_reducers_reject_nonpositive(value, reducer):
    with pytest.raises(ValueError):
        reducer(value)


@pytest.mark.parametrize("name,expected", [
    ("Çağrı Şen","CAGRISEN"),("çağrı şen","CAGRISEN"),("ÇAĞRI ŞEN","CAGRISEN"),
    ("ÇĞİıÖŞÜçğıiöşü","CGIIOSUCGIIOSU"),("Iİıi","IIII"),
    ("Ada-Test","ADATEST"),("Ada'Test","ADATEST"),("Ada’Test","ADATEST"),
    (" Ada\tTest\n","ADATEST"),("Ada—Test\u00a0","ADATEST"),
    (unicodedata.normalize("NFD", "Çağrı Şen"),"CAGRISEN"),
])
def test_name_normalization(name, expected):
    assert normalize_name(name) == expected


@pytest.mark.parametrize("name,code", [
    ("","invalid_name"),("  \t","invalid_name"),("—'...","invalid_name"),
    ("Ada2","invalid_name"),("Ada٢","invalid_name"),("Ada🙂","invalid_name"),
    ("Ada+","invalid_name"),("Ada\x00","invalid_name"),
    ("Ада","unsupported_name_characters"),("Αδα","unsupported_name_characters"),
    ("آدا","unsupported_name_characters"),("Écho","unsupported_name_characters"),
    ("ß","unsupported_name_characters"),("Ａ","unsupported_name_characters"),
    ("K","unsupported_name_characters"),
    ("\u0301","unsupported_name_characters"),
])
def test_invalid_name_policy(name, code):
    with pytest.raises(NumerologyError) as error:
        normalize_name(name)
    assert error.value.code == code


def test_full_golden_ada_vector():
    assert calculate().model_dump(mode="json") == ADA


def test_turkish_golden_vector():
    result = calculate("Çağrı Şen")  # Synthetic convention example, not a user record.
    assert (result.expression.raw_sum, result.expression.value) == (40,4)
    assert (result.soul_urge.raw_sum, result.soul_urge.value) == (15,6)
    assert (result.personality.raw_sum, result.personality.value) == (25,7)


@pytest.mark.parametrize("name", ["Ada Test","Çağrı Şen","AEIOU","Bcd Y","Y","A","Ada-Test"])
def test_expression_partition_invariant(name):
    result = calculate(name)
    assert result.expression.raw_sum == (result.soul_urge.raw_sum if result.soul_urge else 0) + (
        result.personality.raw_sum if result.personality else 0)


def test_empty_partitions_and_y_policy():
    assert calculate("AEIOU").personality is None
    result = calculate("Y")
    assert result.soul_urge is None
    assert result.personality.raw_sum == 7


def test_life_path_uses_all_digits_without_component_reduction():
    # 2000 + November + 9th: digit total 2+2+9=13 -> 4.
    # Component reduction with masters would instead give 2+11+9=22.
    result = calculate(birth="2000-11-09")
    assert (result.life_path.raw_sum, result.life_path.value) == (13,4)


@pytest.mark.parametrize("birth,raw,value", [("2000-01-11",11,11),("2000-01-22",22,22),
                                         ("2000-01-29",29,11),("2000-01-31",31,4)])
def test_birthday(birth, raw, value):
    result = calculate(birth=birth).birthday
    assert (result.raw_sum, result.value, result.is_master) == (raw,value,value in (11,22,33))


@pytest.mark.parametrize("birth,expected", [("2000-01-08",11),("2000-09-29",22),("1999-03-11",33)])
def test_life_path_masters(birth, expected):
    result = calculate(birth=birth).life_path
    assert (result.raw_sum,result.value,result.is_master) == (expected,expected,True)


def test_maturity_uses_reduced_values_and_preserves_master():
    # Life path 6, E expression 5 => 11 (not life raw 15 + 5).
    result = calculate("E")
    assert (result.maturity.raw_sum,result.maturity.value,result.maturity.is_master) == (11,11,True)


@pytest.mark.parametrize("birth,year,raw,value", [("2000-01-08",2000,11,2),
                                              ("2000-09-29",2000,22,4),
                                              ("2000-09-29",2029,33,6)])
def test_personal_year_never_preserves_masters(birth,year,raw,value):
    result = calculate(birth=birth,year=year).personal_year
    assert (result.raw_sum,result.value,result.is_master) == (raw,value,False)


def test_service_has_no_implicit_year_and_is_repeatable():
    req = NumerologyRequest(full_name="Ada Test", birth_date="2000-02-29")
    results = [NumerologyService().calculate(req).model_dump_json() for _ in range(10)]
    assert len(set(results)) == 1
    assert NumerologyService().calculate(req).personal_year is None
    # Service is calendar math even for future dates: admission belongs to the API.
    assert calculate(birth="9999-12-31",year=None).personal_year is None


@pytest.fixture
def client():
    app = create_app(Settings(app_env="test", _env_file=None))
    app.dependency_overrides[validation_today] = lambda: date(2026,1,1)
    with TestClient(app) as test_client:
        yield test_client


def payload(**overrides):
    return {"full_name":"Ada Test","birth_date":"2000-02-29","target_year":2026} | overrides


def test_api_golden_contract_and_privacy(client, caplog):
    first = client.post("/api/v1/numerology/calculate",json=payload())
    assert first.status_code == 200
    assert first.json() == ADA
    assert NumerologyResponse.model_validate(first.json()).model_dump(mode="json") == ADA
    assert first.content == client.post("/api/v1/numerology/calculate",json=payload()).content
    assert "Ada Test" not in first.text and "ADATEST" not in first.text
    assert "Ada Test" not in caplog.text


@pytest.mark.parametrize("data,code", [
    (payload(full_name=""),"invalid_name"),(payload(full_name="   "),"invalid_name"),
    (payload(full_name="---"),"invalid_name"),(payload(full_name=123),"invalid_name"),
    (payload(full_name=None),"invalid_name"),(payload(full_name="A"*201),"invalid_name"),
    (payload(full_name="Ada2"),"invalid_name"),(payload(full_name="Ada🙂"),"invalid_name"),
    (payload(full_name="Αδα"),"unsupported_name_characters"),
    (payload(birth_date="2001-02-29"),"invalid_birth_date"),
    (payload(birth_date="2026-01-02"),"invalid_birth_date"),
    (payload(birth_date="0000-01-01"),"invalid_birth_date"),
    (payload(birth_date="2000-2-29"),"invalid_birth_date"),
    (payload(birth_date="2000-02-29T00:00:00Z"),"invalid_birth_date"),
    (payload(birth_date=0),"invalid_birth_date"),(payload(birth_date=True),"invalid_birth_date"),
    (payload(birth_date=None),"invalid_birth_date"),
    (payload(target_year="2026"),"invalid_target_year"),
    (payload(target_year=True),"invalid_target_year"),
    (payload(target_year=2026.0),"invalid_target_year"),
    (payload(target_year=0),"invalid_target_year"),(payload(target_year=10000),"invalid_target_year"),
    (payload(extra="value"),"invalid_request"),
    ({"full_name":"Ada Test"},"invalid_birth_date"),
    ({"birth_date":"2000-02-29"},"invalid_name"),
])
def test_api_invalid_inputs_sanitized(client,data,code,caplog):
    response = client.post("/api/v1/numerology/calculate",json=data)
    assert response.status_code == 422
    assert set(response.json()) == {"detail"}
    assert set(response.json()["detail"]) == {"code","message"}
    assert response.json()["detail"]["code"] == code
    name = data.get("full_name")
    if isinstance(name,str) and name.strip():
        assert name not in response.text
        assert name not in caplog.text


@pytest.mark.parametrize("body", ['[]','null','"text"','{"full_name":','123','true',''])
def test_malformed_or_nonobject_request(client,body):
    response = client.post("/api/v1/numerology/calculate",content=body,headers={"Content-Type":"application/json"})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_request"


@pytest.mark.parametrize("year", [None,1,9999])
def test_optional_year_and_bounds(client,year):
    response = client.post("/api/v1/numerology/calculate",json=payload(target_year=year))
    assert response.status_code == 200
    assert response.json()["metadata"]["target_year"] == year
    if year is None:
        assert response.json()["personal_year"] is None


def test_missing_year_never_uses_validation_clock(client):
    data = payload()
    del data["target_year"]
    first = client.post("/api/v1/numerology/calculate",json=data).json()
    client.app.dependency_overrides[validation_today] = lambda: date(2040,1,1)
    assert client.post("/api/v1/numerology/calculate",json=data).json() == first
    assert first["personal_year"] is None


def test_today_allowed_and_clock_only_controls_admission(client):
    assert client.post("/api/v1/numerology/calculate",json=payload(birth_date="2026-01-01")).status_code == 200
    first = client.post("/api/v1/numerology/calculate",json=payload()).json()
    client.app.dependency_overrides[validation_today] = lambda: date(2040,1,1)
    assert client.post("/api/v1/numerology/calculate",json=payload()).json() == first
