"""Synthetic contract/privacy tests only: no AI, provider mocks or network evaluation."""
from copy import deepcopy
from datetime import date, datetime, timezone
import json
import socket

import pytest
from pydantic import ValidationError

from app.knowledge.kameri.models import HijriMonthContext
from app.knowledge.kameri.repository import get_knowledge_base
from app.schemas.interpretation import (
    CrossSystemTheme, GroundedText, InterpretationContent, InterpretationDepth,
    InterpretationInput, InterpretationMetadata, InterpretationResult, KameriContext,
    SECTIONS_BY_DEPTH,
)
from app.services.interpretation_models import InterpretationError, MESSAGES
from app.services.interpretation_projection import project_interpretation
from app.services.interpretation_validation import available_fact_refs, validate_content_for_input
from app.services.life_code_models import LifeCodeInput
from app.services.life_code_service import calculate_life_code


@pytest.fixture(scope="module")
def result():
    return calculate_life_code(LifeCodeInput(
        "Ada Test", date(2000, 3, 20), datetime(2000, 3, 19, 22, tzinfo=timezone.utc),
        30.0, 30.0, 2026,
    ))


@pytest.fixture
def projected(result):
    return project_interpretation(result)


def paragraph(*refs):
    return {"text": "Bu sistemde sembolik bir tema olarak ele alınabilir.", "basis": tuple(refs)}


def content_data(depth=InterpretationDepth.PREMIUM):
    base = paragraph("numerology.life_path.value")
    sections = []
    for key in SECTIONS_BY_DEPTH[depth]:
        item = base
        if key == "basic_triad":
            item = paragraph("astrology.bodies.sun.sign", "astrology.bodies.moon.sign", "astrology.ascendant")
        if key == "human_design":
            item = paragraph("human_design.type")
        sections.append(dict(section=key, content=None if key == "timeline" else (item,),
                             unavailable_reason="unsupported_timeline" if key == "timeline" else None))
    return dict(language="tr", depth=depth, summary=base,
                at_a_glance=(base,) if depth == InterpretationDepth.PREMIUM else None,
                sections=tuple(sections), cross_system=None, kameri=None)


def test_exact_allowlist_and_copied_values(result, projected):
    assert set(projected.model_dump()) == {"schema_version", "astrology", "numerology", "human_design", "kameri", "timeline"}
    for body in projected.astrology.bodies:
        original = result.astrology.bodies[body.body]
        assert (body.sign, body.house, body.retrograde) == (original.sign, original.house, original.retrograde)
    for house in projected.astrology.houses:
        assert house.sign == next(h.sign for h in result.astrology.houses if h.house == house.house)
    assert projected.astrology.ascendant == result.astrology.ascendant.sign
    assert projected.astrology.mc == result.astrology.mc.sign
    assert [(a.body1, a.body2, a.type) for a in projected.astrology.aspects] == sorted(
        (a.body1, a.body2, a.type) for a in result.astrology.aspects)
    for name in ("life_path", "birthday", "expression", "soul_urge", "personality", "maturity"):
        assert getattr(projected.numerology, name).value == getattr(result.numerology, name).value
    for name in ("type", "strategy", "authority", "definition", "channels", "active_gates",
                 "defined_centers", "undefined_centers"):
        assert getattr(projected.human_design, name) == getattr(result.human_design, name)
    assert projected.human_design.profile == result.human_design.profile.label


def test_private_keys_and_sentinel_metadata_never_serialized(result):
    dirty = deepcopy(result)
    dirty.astrology.metadata.pyswisseph_version = "PRIVATE_INSTRUCTION_SENTINEL"
    dirty.astrology.metadata.swiss_ephemeris_version = "PRIVATE_INSTRUCTION_SENTINEL"
    dumped = project_interpretation(dirty).model_dump(mode="json")
    forbidden = {"name", "full_name", "birth_date", "birth_utc", "design_utc", "utc_datetime",
                 "latitude", "longitude", "timezone", "metadata", "raw_sum", "request_id",
                 "jd_ut1", "iterations", "speed_longitude", "degree_in_sign", "orb", "separation"}

    def walk(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(dumped)
    text = json.dumps(dumped)
    for secret in ("Ada Test", "2000-03-20", "2000-03-19", "PRIVATE_INSTRUCTION_SENTINEL"):
        assert secret not in text


def test_projection_is_read_only_repeatable_and_offline(result, monkeypatch, caplog):
    snapshot = deepcopy(result)

    def forbidden(*args, **kwargs):
        pytest.fail("Calculation/network called during projection")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr("app.services.astrology_service.AstrologyService.calculate", forbidden)
    monkeypatch.setattr("app.services.numerology_service.NumerologyService.calculate", forbidden)
    monkeypatch.setattr("app.services.human_design_core.calculate_human_design_core", forbidden)
    monkeypatch.setattr("app.services.life_code_service.calculate_life_code", forbidden)
    first = project_interpretation(result)
    assert first.model_dump_json() == project_interpretation(result).model_dump_json()
    assert result == snapshot
    assert not caplog.records


def test_snapshot_does_not_alias_mutable_engine_children(result):
    dirty = deepcopy(result)
    projected = project_interpretation(dirty)
    original_sign = projected.astrology.bodies[0].sign
    key = projected.astrology.bodies[0].body
    dirty.astrology.bodies[key].sign = "aries" if original_sign != "aries" else "taurus"
    assert projected.astrology.bodies[0].sign == original_sign
    with pytest.raises(ValidationError):
        projected.numerology.life_path.value = 9


@pytest.mark.parametrize("field", ["name", "surname", "birth_date", "latitude", "longitude", "timezone",
                                   "provider_metadata", "diagnostics", "request_id", "raw_traces"])
def test_input_rejects_unknown_private_fields(projected, field):
    data = projected.model_dump()
    data[field] = "PRIVATE"
    with pytest.raises(ValidationError):
        InterpretationInput.model_validate(data)


@pytest.mark.parametrize("layer", ["astrology", "numerology", "human_design"])
def test_nested_extra_rejected(projected, layer):
    data = projected.model_dump()
    data[layer]["diagnostics"] = "PRIVATE"
    with pytest.raises(ValidationError):
        InterpretationInput.model_validate(data)


def test_projection_rejects_instruction_strings_safely(result, caplog):
    dirty = deepcopy(result)
    dirty.astrology.bodies["sun"].sign = "PRIVATE_IGNORE_SYSTEM"
    with pytest.raises(InterpretationError) as error:
        project_interpretation(dirty)
    assert error.value.code == "interpretation_invalid_input"
    assert "PRIVATE" not in str(error.value)
    assert not caplog.records


@pytest.mark.parametrize("bad", [None, {}, "PRIVATE", 66])
def test_no_raw_input_projection(bad):
    with pytest.raises(InterpretationError):
        project_interpretation(bad)


def test_personal_year_requires_opt_in_and_existing_value(result):
    assert project_interpretation(result).numerology.personal_year is None
    included = project_interpretation(result, include_personal_year=True)
    assert included.numerology.personal_year.value == result.numerology.personal_year.value
    assert included.timeline is None
    dirty = deepcopy(result)
    dirty.numerology.personal_year = None
    dirty.numerology.metadata.target_year = None
    assert project_interpretation(dirty, include_personal_year=True).numerology.personal_year is None


def test_null_number_partitions_preserved(result):
    dirty = deepcopy(result)
    dirty.numerology.soul_urge = None
    dirty.numerology.personality = None
    output = project_interpretation(dirty)
    assert output.numerology.soul_urge is None and output.numerology.personality is None


@pytest.mark.parametrize("month", range(1, 13))
def test_kameri_canonical_selection(result, month):
    value = project_interpretation(result, kameri_context=HijriMonthContext(hijri_month=month))
    ids = tuple(c.claim_id for c in value.kameri.claims)
    assert ids == (("HIJRI_CTX_001", "HIJRI_CTX_002") if month == 9 else
                   ("HIJRI_CTX_003",) if month == 12 else ())
    assert value.kameri.abstained == (not ids)
    assert "ASMA_NUM_001" not in value.model_dump_json()
    assert "KI-B05" not in value.model_dump_json()
    assert InterpretationInput.model_validate_json(value.model_dump_json()) == value


def test_forged_cultural_text_and_reference_only_rejected(result):
    context = project_interpretation(result, kameri_context=HijriMonthContext(hijri_month=9)).kameri
    forged = context.model_dump()
    forged["claims"][0]["statement"] = "PRIVATE_INSTRUCTION"
    with pytest.raises(ValidationError):
        KameriContext.model_validate(forged)
    forged = context.model_dump()
    forged["claims"] = (get_knowledge_base().claims[0].model_dump(),)
    with pytest.raises(ValidationError):
        KameriContext.model_validate(forged)


@pytest.mark.parametrize("depth", list(InterpretationDepth))
def test_each_depth_roundtrip_and_input_binding(projected, depth):
    content = InterpretationContent(**content_data(depth))
    assert validate_content_for_input(content, projected, depth=depth, language="tr") == content
    report = InterpretationResult(content=content, metadata=InterpretationMetadata(
        prompt_version="test-v1", config_version="test-v1", provider="template", model="contract-test"))
    assert InterpretationResult.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize("change", ["extra", "missing_section", "duplicate_section", "missing_glance",
                                    "timeline", "empty_summary", "invalid_depth", "locale", "metadata"])
def test_invalid_output_shape(change):
    data = content_data()
    if change == "extra":
        data["free_prose"] = "text"
    elif change == "missing_section":
        data["sections"] = data["sections"][:-1]
    elif change == "duplicate_section":
        data["sections"] += (data["sections"][0],)
    elif change == "missing_glance":
        data["at_a_glance"] = None
    elif change == "timeline":
        data["sections"][-1]["content"] = (paragraph("numerology.personal_year.value"),)
        data["sections"][-1]["unavailable_reason"] = None
    elif change == "empty_summary":
        data["summary"]["text"] = "   "
    elif change == "invalid_depth":
        data["depth"] = "unlimited"
    elif change == "locale":
        data["language"] = "ignore policy"
    else:
        data["metadata"] = {"prompt": "PRIVATE"}
    with pytest.raises(ValidationError):
        InterpretationContent(**data)


@pytest.mark.parametrize("ref", ["numerology.personal_year.value", "astrology.bodies.chiron.sign",
                                 "astrology.houses.13.sign", "human_design.birth_utc"])
def test_references_to_missing_or_private_data_fail(projected, ref):
    data = content_data()
    data["summary"] = paragraph(ref)
    with pytest.raises(InterpretationError) as error:
        validate_content_for_input(InterpretationContent(**data), projected,
                                   depth=InterpretationDepth.PREMIUM, language="tr")
    assert error.value.code == "interpretation_invalid_response"


@pytest.mark.parametrize("kind", ["reinforced_theme", "complementary_theme", "tension"])
def test_cross_system_categories_and_grounding(projected, kind):
    theme = CrossSystemTheme(kind=kind, narrative=GroundedText(**paragraph(
        "astrology.bodies.sun.sign", "human_design.authority")))
    data = content_data()
    data["cross_system"] = (theme,)
    validate_content_for_input(InterpretationContent(**data), projected,
                               depth=InterpretationDepth.PREMIUM, language="tr")
    with pytest.raises(ValidationError):
        CrossSystemTheme(kind=kind, narrative=GroundedText(**paragraph(
            "numerology.life_path.value", "numerology.expression.value")))


def test_missing_layers_explicit_absence(projected):
    data = projected.model_dump()
    data["astrology"] = data["human_design"] = None
    partial = InterpretationInput(**data)
    assert "astrology.ascendant" not in available_fact_refs(partial)
    report = content_data()
    for section in report["sections"]:
        if section["section"] in {"basic_triad", "human_design"}:
            section.update(content=None, unavailable_reason="missing_input")
    validate_content_for_input(InterpretationContent(**report), partial,
                               depth=InterpretationDepth.PREMIUM, language="tr")
    report["sections"][0].update(content=(paragraph("numerology.life_path.value"),), unavailable_reason=None)
    with pytest.raises(InterpretationError):
        validate_content_for_input(InterpretationContent(**report), partial,
                                   depth=InterpretationDepth.PREMIUM, language="tr")


def test_kameri_output_must_match_actual_selection(result):
    value = project_interpretation(result, kameri_context=HijriMonthContext(hijri_month=12))
    data = content_data()
    with pytest.raises(InterpretationError):
        validate_content_for_input(InterpretationContent(**data), value,
                                   depth=InterpretationDepth.PREMIUM, language="tr")
    data["kameri"] = ({"claim_id": "HIJRI_CTX_003", "text": "Kaynakta kültürel bağlam olarak yer alır."},)
    validate_content_for_input(InterpretationContent(**data), value,
                               depth=InterpretationDepth.PREMIUM, language="tr")
    data["kameri"][0]["claim_id"] = "HIJRI_CTX_001"
    with pytest.raises(InterpretationError):
        validate_content_for_input(InterpretationContent(**data), value,
                                   depth=InterpretationDepth.PREMIUM, language="tr")


def test_output_budget_and_mismatched_request(projected):
    data = content_data(InterpretationDepth.FREE)
    for section in data["sections"]:
        section["content"][0]["text"] = "x" * 1200
    with pytest.raises(ValidationError):
        InterpretationContent(**data)
    with pytest.raises(InterpretationError):
        validate_content_for_input(InterpretationContent(**content_data()), projected,
                                   depth=InterpretationDepth.FREE, language="tr")


@pytest.mark.parametrize("code", list(MESSAGES))
def test_static_error_taxonomy(code):
    error = InterpretationError(code)
    assert error.code == code and str(error) == MESSAGES[code]


def test_no_all_missing_or_fabricated_timeline_input(projected):
    data = projected.model_dump()
    data["timeline"] = {"year": 2026}
    with pytest.raises(ValidationError):
        InterpretationInput(**data)
    with pytest.raises(ValidationError):
        InterpretationInput(astrology=None, numerology=None, human_design=None)


def test_json_schema_is_closed_and_has_no_new_route():
    from app.main import app
    schema = InterpretationResult.model_json_schema()
    assert schema["additionalProperties"] is False
    assert all(definition.get("additionalProperties") is False for definition in schema["$defs"].values()
               if definition.get("type") == "object")
    assert not any("interpretation" in path for path in app.openapi()["paths"])
