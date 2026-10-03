"""Phase 1 deterministic evidence/plan/assembler foundation; no providers or network."""
import json

from pydantic import ValidationError
import pytest

from app.schemas.interpretation import (
    InterpretationContent, InterpretationDepth, InterpretationInput, SECTIONS_BY_DEPTH,
)
from app.services.interpretation_ai_models import (
    AIInterpretationPayload, AITextRealization, AI_PAYLOAD_VERSION, EVIDENCE_VERSION,
    FactPredicate, InterpretationFoundationError, SemanticEvidenceUnit,
)
from app.services.interpretation_assembler import InterpretationAssembler
from app.services.interpretation_evidence import (
    ASTROLOGY_FOUNDATION_CATALOG, SemanticEvidenceBuilder,
)
from app.services.interpretation_plan import NarrativePlanner
from app.services.interpretation_validation import validate_content_for_input
from tests.test_gemini_interpretation import CORPUS, case_input


@pytest.fixture
def symbolic():
    case = next(item for item in CORPUS["cases"] if item["id"] == "exact_time_astrology")
    return case_input(case)


@pytest.fixture
def foundation(symbolic):
    evidence = SemanticEvidenceBuilder().build(symbolic)
    plan = NarrativePlanner().plan(symbolic, evidence, depth=InterpretationDepth.FREE)
    payload = AIInterpretationPayload(
        schema_version=AI_PAYLOAD_VERSION,
        realizations=tuple(AITextRealization(
            slot_id=slot.slot_id,
            text=f"Astrolojik yorumda {slot.purpose} için izinli temalar öne çıkabilir.",
        ) for slot in plan.slots),
    )
    return evidence, plan, payload


def test_ai_payload_is_minimal_and_forbids_model_owned_contract_fields(foundation):
    _, _, payload = foundation
    assert set(type(payload).model_fields) == {"schema_version", "realizations"}
    assert set(AITextRealization.model_fields) == {"slot_id", "text"}
    invalid = payload.model_dump(mode="json")
    invalid["realizations"][0]["basis"] = ["astrology.ascendant"]
    with pytest.raises(ValidationError):
        AIInterpretationPayload.model_validate(invalid)
    for forbidden in ("depth", "tier", "sections", "unavailable_reason", "provenance", "metadata"):
        changed = payload.model_dump(mode="json")
        changed[forbidden] = "model-controlled"
        with pytest.raises(ValidationError):
            AIInterpretationPayload.model_validate(changed)


def test_evidence_builder_is_deterministic_and_matches_fixture(symbolic):
    builder = SemanticEvidenceBuilder()
    first = builder.build(symbolic)
    second = builder.build(symbolic)
    assert first == second
    assert tuple(unit.unit_id for unit in first) == tuple(sorted(unit.unit_id for unit in first))
    assert {unit.unit_id for unit in first} == {
        "astro.sun.aries.house1.initiative.v1",
        "astro.moon.libra.house7.relational_balance.v1",
        "astro.ascendant.aries.direct_expression.v1",
        "astro.mc.capricorn.long_term_structure.v1",
        "astro.sun_moon.opposition.theme_tension.v1",
    }
    assert all(unit.version == EVIDENCE_VERSION for unit in first)
    assert all(unit.status == "foundation_prototype_not_production_qualified" for unit in first)


@pytest.mark.parametrize("path,value,missing_unit", [
    ("astrology.bodies.sun.sign", "taurus", "astro.sun.aries.house1.initiative.v1"),
    ("astrology.bodies.moon.house", 6, "astro.moon.libra.house7.relational_balance.v1"),
    ("astrology.ascendant", "taurus", "astro.ascendant.aries.direct_expression.v1"),
    ("astrology.mc", "aquarius", "astro.mc.capricorn.long_term_structure.v1"),
])
def test_missing_predicate_prevents_unit(symbolic, path, value, missing_unit):
    data = symbolic.model_dump(mode="json")
    if path == "astrology.ascendant":
        data["astrology"]["ascendant"] = value
    elif path == "astrology.mc":
        data["astrology"]["mc"] = value
    else:
        _, _, body_name, field = path.split(".")
        body = next(item for item in data["astrology"]["bodies"] if item["body"] == body_name)
        body[field] = value
    changed = InterpretationInput.model_validate_json(json.dumps(data))
    assert missing_unit not in {unit.unit_id for unit in SemanticEvidenceBuilder().build(changed)}


def test_unknown_fact_path_fails_safe(symbolic):
    prototype = ASTROLOGY_FOUNDATION_CATALOG[2]
    unknown = SemanticEvidenceUnit(
        unit_id="astro.unknown.path.prototype.v1", version=EVIDENCE_VERSION,
        status="foundation_prototype_not_production_qualified", system="astrology",
        required_facts=(FactPredicate(path="astrology.unknown.value", expected="x"),
                        FactPredicate(path="astrology.ascendant", expected="aries")),
        public_basis=("astrology.ascendant",), allowed_sections=("basic_triad",),
        allowed_statement_tr=prototype.allowed_statement_tr, allowed_themes=("direct_expression",),
        forbidden_extensions=("regret",), source_ids=("project-authored-prototype",),
        license_classification="project_authored_prototype",
    )
    assert SemanticEvidenceBuilder((unknown,)).build(symbolic) == ()


def test_verified_unsupported_semantic_bridges_have_no_units(symbolic):
    evidence = SemanticEvidenceBuilder().build(symbolic)
    themes = {theme for unit in evidence for theme in unit.allowed_themes}
    assert "impatience" not in themes  # retrograde=false is present but licenses no such unit.
    assert "regret" not in themes  # Aries ASC is present but licenses no such unit.
    asc = next(unit for unit in evidence if unit.unit_id.startswith("astro.ascendant.aries"))
    assert {"impulsiveness", "impatience", "regret"} <= set(asc.forbidden_extensions)


def test_narrative_plan_is_backend_owned_ordered_and_section_compatible(foundation):
    evidence, plan, _ = foundation
    assert plan.depth is InterpretationDepth.FREE and plan.language == "tr"
    assert tuple(slot.slot_id for slot in plan.slots) == (
        "summary.0", "section.basic_triad.0", "section.basic_triad.1",
        "section.basic_triad.2", "section.strengths.0", "section.strengths.1",
        "section.strengths.2", "section.challenges.0",
    )
    units = {unit.unit_id: unit for unit in evidence}
    for slot in plan.slots:
        if slot.section is not None:
            assert all(slot.section in units[unit_id].allowed_sections
                       for unit_id in slot.evidence_unit_ids)


def test_assembler_rejects_missing_extra_and_duplicate_slots(symbolic, foundation):
    evidence, plan, payload = foundation
    assembler = InterpretationAssembler()
    with pytest.raises(InterpretationFoundationError, match="invalid_ai_payload"):
        assembler.assemble(plan, payload.model_copy(
            update={"realizations": payload.realizations[:-1]}), evidence, symbolic)
    extra = (*payload.realizations, AITextRealization(slot_id="section.character.0", text="extra"))
    with pytest.raises(InterpretationFoundationError, match="invalid_ai_payload"):
        assembler.assemble(plan, payload.model_copy(update={"realizations": extra}), evidence, symbolic)
    duplicate = (*payload.realizations[:-1], payload.realizations[0])
    bypassed = AIInterpretationPayload.model_construct(
        schema_version=AI_PAYLOAD_VERSION, realizations=duplicate)
    with pytest.raises(InterpretationFoundationError, match="invalid_ai_payload"):
        assembler.assemble(plan, bypassed, evidence, symbolic)


def test_assembler_derives_basis_and_free_envelope_deterministically(symbolic, foundation):
    evidence, plan, payload = foundation
    assembler = InterpretationAssembler()
    first = assembler.assemble(plan, payload, evidence, symbolic)
    second = assembler.assemble(plan, payload, evidence, symbolic)
    assert first == second
    assert tuple(section.section for section in first.sections) == SECTIONS_BY_DEPTH[InterpretationDepth.FREE]
    assert first.at_a_glance is None and first.cross_system is None and first.kameri is None
    slots = {slot.slot_id: slot for slot in plan.slots}
    assert first.summary.basis == slots["summary.0"].canonical_basis
    for section in first.sections:
        planned = [slot for slot in plan.slots if slot.section == section.section]
        assert tuple(paragraph.basis for paragraph in section.content) == tuple(
            slot.canonical_basis for slot in planned)
    assert validate_content_for_input(
        first, symbolic, depth=InterpretationDepth.FREE, language="tr") == first


def test_tampered_plan_basis_is_rejected(symbolic, foundation):
    evidence, plan, payload = foundation
    first = plan.slots[0].model_copy(update={"canonical_basis": ("astrology.ascendant",)})
    tampered = plan.model_copy(update={"slots": (first, *plan.slots[1:])})
    with pytest.raises(InterpretationFoundationError, match="invalid_plan"):
        InterpretationAssembler().assemble(tampered, payload, evidence, symbolic)


def test_existing_public_content_contract_is_unchanged():
    assert tuple(InterpretationContent.model_fields) == (
        "language", "depth", "summary", "at_a_glance", "sections", "cross_system", "kameri")
    assert "realizations" not in InterpretationContent.model_fields


def test_foundation_still_does_not_claim_arbitrary_prose_entailment(symbolic, foundation):
    evidence, plan, payload = foundation
    data = payload.model_dump(mode="json")
    data["realizations"][0]["text"] = "Yeni deneyimlere açık olabilirsiniz."
    # Phase 2A catches bounded risks, not every unsupported natural-language implication.
    content = InterpretationAssembler().assemble(
        plan, AIInterpretationPayload.model_validate_json(json.dumps(data)), evidence, symbolic)
    assert content.summary.text == "Yeni deneyimlere açık olabilirsiniz."
