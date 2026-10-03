"""Phase 2A deterministic bounded-realization tests; no providers or network."""
import json

import pytest

from app.schemas.interpretation import InterpretationContent, InterpretationDepth
from app.services.interpretation_ai_models import (
    AIInterpretationPayload, AITextRealization, AI_PAYLOAD_VERSION,
)
from app.services.interpretation_assembler import InterpretationAssembler
from app.services.interpretation_evidence import SemanticEvidenceBuilder
from app.services.interpretation_plan import NarrativePlanner
from app.services.interpretation_realization import (
    BoundedRealizationError, BoundedRealizationValidator,
)
from tests.test_gemini_interpretation import CORPUS, case_input


@pytest.fixture
def bounded_foundation():
    case = next(item for item in CORPUS["cases"] if item["id"] == "exact_time_astrology")
    input = case_input(case)
    evidence = SemanticEvidenceBuilder().build(input)
    plan = NarrativePlanner().plan(input, evidence, depth=InterpretationDepth.FREE)
    payload = AIInterpretationPayload(
        schema_version=AI_PAYLOAD_VERSION,
        realizations=tuple(AITextRealization(
            slot_id=slot.slot_id,
            text="Astrolojik yorumda bu sembolizm izinli temalarla ilişkilendirilebilir.",
        ) for slot in plan.slots),
    )
    return input, evidence, plan, payload


def _slot_context(bounded_foundation, slot_id):
    _, evidence, plan, _ = bounded_foundation
    slot = next(item for item in plan.slots if item.slot_id == slot_id)
    by_id = {unit.unit_id: unit for unit in evidence}
    units = tuple(by_id[unit_id] for unit_id in slot.evidence_unit_ids)
    return slot, units


def _validate_text(bounded_foundation, slot_id, text):
    slot, units = _slot_context(bounded_foundation, slot_id)
    realization = AITextRealization(slot_id=slot_id, text=text)
    BoundedRealizationValidator().validate(realization, slot, units)


@pytest.mark.parametrize(("text", "category"), [
    ("Bu yerleşim aceleci davranmanıza ve sonra pişman olmanıza neden olabilir.",
     "regret"),
    ("Bu enerji sizi sabırsız davranmaya yöneltebilir.", "impatience"),
    ("Bu sembolizm dürtüsel tepki vermenize neden olabilir.", "impulsiveness"),
    ("Bu etki fevri kararlarla ilişkilendirilebilir.", "impulsiveness"),
    ("Bu nedenle düşünmeden hareket edebilirsiniz.", "impulsiveness"),
])
def test_evidence_specific_forbidden_extensions_are_rejected(
        bounded_foundation, text, category):
    with pytest.raises(BoundedRealizationError) as captured:
        _validate_text(bounded_foundation, "section.basic_triad.0", text)
    assert captured.value.code == "forbidden_semantic_extension"
    assert captured.value.category == category
    assert captured.value.slot_id == "section.basic_triad.0"


@pytest.mark.parametrize("variant", [
    "pişman", "pişmanlık", "pişman olabilirsiniz", "pişman olma",
])
def test_regret_morphology_variants_are_rejected(bounded_foundation, variant):
    with pytest.raises(BoundedRealizationError) as captured:
        _validate_text(
            bounded_foundation, "section.basic_triad.0",
            f"Bu sembolizm daha sonra {variant} durumuyla sonuçlanabilir.")
    assert captured.value.code == "forbidden_semantic_extension"
    assert captured.value.category == "regret"


@pytest.mark.parametrize("variant", ["sabırsız", "sabırsızlık"])
def test_impatience_morphology_variants_are_rejected(bounded_foundation, variant):
    with pytest.raises(BoundedRealizationError) as captured:
        _validate_text(
            bounded_foundation, "section.basic_triad.0",
            f"Bu yerleşim {variant} temasıyla ilişkilendirilebilir.")
    assert captured.value.category == "impatience"


def test_retrograde_false_does_not_license_impatience_prose(bounded_foundation):
    input, _, _, _ = bounded_foundation
    sun = next(body for body in input.astrology.bodies if body.body == "sun")
    assert sun.retrograde is False
    with pytest.raises(BoundedRealizationError) as captured:
        _validate_text(
            bounded_foundation, "section.basic_triad.0",
            "Retrograd olmadığı için sabırsızlık ortaya çıkabilir.")
    assert captured.value.category == "impatience"


@pytest.mark.parametrize(("text", "code", "category"), [
    ("Bu yerleşim sizi doğal olarak güçlü bir lider yapar.",
     "excessive_certainty", "absolute_behavioral_certainty"),
    ("Bu yerleşim kesinlikle liderlik zorunluluğu yaratır.",
     "excessive_certainty", "absolute_behavioral_certainty"),
    ("Gelecekte büyük bir başarı yaşayacaksınız.",
     "prohibited_claim_class", "deterministic_future_prediction"),
    ("Bu yerleşim depresyon hastası olduğunuzu gösterir.",
     "prohibited_claim_class", "medical_or_mental_diagnosis"),
])
def test_global_prohibited_claims_are_rejected(bounded_foundation, text, code, category):
    with pytest.raises(BoundedRealizationError) as captured:
        _validate_text(bounded_foundation, "section.basic_triad.0", text)
    assert captured.value.code == code
    assert captured.value.category == category


@pytest.mark.parametrize("text", [
    "Astrolojik yorumda bu yerleşim bireysel inisiyatif ve doğrudan ifade "
    "temalarıyla ilişkilendirilebilir.",
    "Bu sembolizm, girişim alma ve kendini doğrudan ortaya koyma temalarıyla "
    "ilişkilendirilebilir.",
    "Bu yerleşim sembolik olarak girişim temasına işaret edebilir.",
    "Bu konu tema olarak ele alınabilir ve yapıcı bir bakışı destekler.",
])
def test_safe_restrained_paraphrases_pass(bounded_foundation, text):
    assert _validate_text(bounded_foundation, "section.basic_triad.0", text) is None


def test_forbidden_category_is_evidence_specific_not_global(bounded_foundation):
    # The MC unit does not forbid regret; bounded extension categories are assignment-specific.
    assert _validate_text(
        bounded_foundation, "section.basic_triad.2",
        "Bu ifade pişmanlık sözcüğünü örnek olarak ele alabilir.") is None


def test_validation_is_deterministic_and_does_not_expose_raw_text(bounded_foundation):
    text = "Bu yerleşim sizi sabırsız davranmaya yöneltebilir."
    failures = []
    for _ in range(2):
        with pytest.raises(BoundedRealizationError) as captured:
            _validate_text(bounded_foundation, "section.basic_triad.0", text)
        failures.append((captured.value.code, captured.value.slot_id,
                         captured.value.category, str(captured.value)))
        assert text not in str(captured.value)
    assert failures[0] == failures[1]


def test_assembler_fails_closed_before_rejected_text_reaches_content(bounded_foundation):
    input, evidence, plan, payload = bounded_foundation
    data = payload.model_dump(mode="json")
    target = next(item for item in data["realizations"]
                  if item["slot_id"] == "section.basic_triad.0")
    target["text"] = "Bu yerleşim aceleci davranmanıza ve sonra pişman olmanıza neden olabilir."
    rejected = AIInterpretationPayload.model_validate_json(json.dumps(data))
    with pytest.raises(BoundedRealizationError):
        InterpretationAssembler().assemble(plan, rejected, evidence, input)


def test_safe_assembly_preserves_backend_basis_and_public_contract(bounded_foundation):
    input, evidence, plan, payload = bounded_foundation
    content = InterpretationAssembler().assemble(plan, payload, evidence, input)
    assert type(content) is InterpretationContent
    assert tuple(InterpretationContent.model_fields) == (
        "language", "depth", "summary", "at_a_glance", "sections", "cross_system", "kameri")
    assert content.summary.basis == plan.slots[0].canonical_basis
    assert content.at_a_glance is None and content.cross_system is None and content.kameri is None


def test_phase_one_slot_failures_remain_fail_closed(bounded_foundation):
    input, evidence, plan, payload = bounded_foundation
    with pytest.raises(ValueError, match="invalid_ai_payload"):
        InterpretationAssembler().assemble(
            plan, payload.model_copy(update={"realizations": payload.realizations[:-1]}),
            evidence, input)
