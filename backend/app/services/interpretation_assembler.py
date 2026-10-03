"""Deterministic Phase 1 assembler; not wired into InterpretationService."""
from pydantic import ValidationError

from app.schemas.interpretation import (
    GroundedText, InterpretationContent, InterpretationDepth, InterpretationInput,
    InterpretationSection, SECTIONS_BY_DEPTH,
)
from app.services.interpretation_ai_models import (
    AIInterpretationPayload, InterpretationFoundationError, NarrativePlan, SemanticEvidenceUnit,
)
from app.services.interpretation_models import InterpretationError
from app.services.interpretation_realization import BoundedRealizationValidator
from app.services.interpretation_validation import validate_content_for_input


class InterpretationAssembler:
    """Join model-written text to backend-owned slots and canonical evidence.

    Phase 2A rejects bounded high-risk extensions but does not prove arbitrary prose entailment.
    Model ownership of basis, sections, depth, nullability and provenance remains excluded.
    """

    def __init__(self, validator: BoundedRealizationValidator | None = None):
        self._validator = validator or BoundedRealizationValidator()

    def assemble(
        self, plan: NarrativePlan, payload: AIInterpretationPayload,
        evidence: tuple[SemanticEvidenceUnit, ...], input: InterpretationInput,
    ) -> InterpretationContent:
        if (type(plan) is not NarrativePlan or type(payload) is not AIInterpretationPayload
                or type(input) is not InterpretationInput or plan.depth is not InterpretationDepth.FREE):
            raise InterpretationFoundationError("unsupported_foundation_scope")

        expected_ids = tuple(slot.slot_id for slot in plan.slots)
        received_ids = tuple(item.slot_id for item in payload.realizations)
        if len(received_ids) != len(set(received_ids)) or set(received_ids) != set(expected_ids):
            raise InterpretationFoundationError("invalid_ai_payload")
        text_by_slot = {item.slot_id: item.text for item in payload.realizations}

        evidence_by_id = {unit.unit_id: unit for unit in evidence}
        if len(evidence_by_id) != len(evidence):
            raise InterpretationFoundationError("invalid_catalog")

        grounded_by_slot = {}
        for slot in plan.slots:
            try:
                units = tuple(evidence_by_id[unit_id] for unit_id in slot.evidence_unit_ids)
            except KeyError:
                raise InterpretationFoundationError("invalid_plan") from None
            derived_basis = tuple(dict.fromkeys(ref for unit in units for ref in unit.public_basis))
            if derived_basis != slot.canonical_basis:
                raise InterpretationFoundationError("invalid_plan")
            if slot.section is not None and any(
                    slot.section not in unit.allowed_sections for unit in units):
                raise InterpretationFoundationError("invalid_plan")
            realization = next(
                item for item in payload.realizations if item.slot_id == slot.slot_id)
            self._validator.validate(realization, slot, units)
            text = realization.text
            if len(text) > slot.max_length:
                raise InterpretationFoundationError("invalid_ai_payload")
            grounded_by_slot[slot.slot_id] = GroundedText(text=text, basis=derived_basis)

        summary_slots = [slot for slot in plan.slots if slot.target == "summary"]
        if len(summary_slots) != 1:
            raise InterpretationFoundationError("invalid_plan")
        summary = grounded_by_slot[summary_slots[0].slot_id]

        sections = []
        for section_id in SECTIONS_BY_DEPTH[plan.depth]:
            slots = tuple(slot for slot in plan.slots if slot.section == section_id)
            if not slots:
                raise InterpretationFoundationError("unsupported_foundation_scope")
            sections.append(InterpretationSection(
                section=section_id,
                content=tuple(grounded_by_slot[slot.slot_id] for slot in slots),
                unavailable_reason=None,
            ))
        try:
            content = InterpretationContent(
                language=plan.language, depth=plan.depth, summary=summary,
                at_a_glance=None, sections=tuple(sections), cross_system=None, kameri=None,
            )
            return validate_content_for_input(
                content, input, depth=plan.depth, language=plan.language)
        except (ValidationError, InterpretationError):
            raise InterpretationFoundationError("invalid_assembly") from None
