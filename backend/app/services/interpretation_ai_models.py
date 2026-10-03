"""Internal Phase 1 AI-realization contracts; never expose these as public API models."""
from typing import Annotated, Literal, Self

from pydantic import Field, StringConstraints, model_validator

from app.schemas.interpretation import (
    Contract, FactRef, InterpretationDepth, Language, SectionId, Text,
)

AI_PAYLOAD_VERSION = "ai-interpretation-payload-v1"
EVIDENCE_VERSION = "semantic-evidence-v1"
NARRATIVE_PLAN_VERSION = "narrative-plan-v1"

SlotId = Annotated[str, StringConstraints(
    min_length=1, max_length=100, pattern=r"^(summary|section\.[a-z_]+)\.[0-9]+$")]
SemanticUnitId = Annotated[str, StringConstraints(
    min_length=1, max_length=120, pattern=r"^[a-z0-9][a-z0-9._-]+\.v[0-9]+$")]
ThemeId = Annotated[str, StringConstraints(
    min_length=1, max_length=80, pattern=r"^[a-z][a-z0-9_]*$")]
ForbiddenSemanticExtension = Literal[
    "career_success", "certain_behavior", "certain_outcome", "diagnosis",
    "impatience", "impulsiveness", "regret",
]
FactPath = Annotated[str, StringConstraints(
    min_length=1, max_length=120,
    pattern=r"^(astrology|numerology|human_design)\.[a-z0-9_.]+$")]
SourceId = Annotated[str, StringConstraints(
    min_length=1, max_length=100, pattern=r"^[a-z0-9][a-z0-9._-]+$")]
FactValue = bool | int | str


class AITextRealization(Contract):
    """The only model-authored values are an expected slot ID and its surface text."""

    slot_id: SlotId
    text: Text


class AIInterpretationPayload(Contract):
    """Minimal internal provider output; no tier, basis, provenance or public envelope."""

    schema_version: Literal["ai-interpretation-payload-v1"]
    realizations: Annotated[tuple[AITextRealization, ...], Field(min_length=1, max_length=64)]

    @model_validator(mode="after")
    def unique_slots(self) -> Self:
        ids = tuple(item.slot_id for item in self.realizations)
        if len(ids) != len(set(ids)):
            raise ValueError("AI realization slots must be unique")
        return self


class FactPredicate(Contract):
    path: FactPath
    expected: FactValue


class SemanticEvidenceUnit(Contract):
    """Prototype-only bounded meaning licensed by exact deterministic predicates."""

    unit_id: SemanticUnitId
    version: Literal["semantic-evidence-v1"]
    status: Literal["foundation_prototype_not_production_qualified"]
    system: Literal["astrology", "numerology", "human_design", "kameri"]
    required_facts: Annotated[tuple[FactPredicate, ...], Field(min_length=1, max_length=8)]
    public_basis: Annotated[tuple[FactRef, ...], Field(min_length=1, max_length=8)]
    allowed_sections: Annotated[tuple[SectionId, ...], Field(min_length=1, max_length=15)]
    allowed_statement_tr: Text
    allowed_themes: Annotated[tuple[ThemeId, ...], Field(min_length=1, max_length=8)]
    forbidden_extensions: Annotated[
        tuple[ForbiddenSemanticExtension, ...], Field(max_length=12)
    ] = ()
    source_ids: Annotated[tuple[SourceId, ...], Field(min_length=1, max_length=4)]
    license_classification: Literal["project_authored_prototype"]

    @model_validator(mode="after")
    def coherent_unit(self) -> Self:
        collections = (
            self.required_facts, self.public_basis, self.allowed_sections,
            self.allowed_themes, self.forbidden_extensions, self.source_ids,
        )
        if any(len(values) != len(set(values)) for values in collections):
            raise ValueError("Semantic evidence fields must not contain duplicates")
        required_paths = {predicate.path for predicate in self.required_facts}
        if not set(self.public_basis) <= required_paths:
            raise ValueError("Public basis must be backed by required facts")
        return self


NarrativePurpose = Literal[
    "overall_synthesis", "placement_explanation", "constructive_potential", "tension_balance",
]


class NarrativePlanSlot(Contract):
    """Backend-owned destination and evidence assignment for one model-written paragraph."""

    slot_id: SlotId
    target: Literal["summary", "section"]
    section: SectionId | None
    evidence_unit_ids: Annotated[tuple[SemanticUnitId, ...], Field(min_length=1, max_length=8)]
    canonical_basis: Annotated[tuple[FactRef, ...], Field(min_length=1, max_length=8)]
    purpose: NarrativePurpose
    max_length: Annotated[int, Field(ge=1, le=1200)]

    @model_validator(mode="after")
    def target_matches_section(self) -> Self:
        if (self.target == "summary") != (self.section is None):
            raise ValueError("Summary has no section; section slots require one")
        if len(self.evidence_unit_ids) != len(set(self.evidence_unit_ids)):
            raise ValueError("Slot evidence units must be unique")
        if len(self.canonical_basis) != len(set(self.canonical_basis)):
            raise ValueError("Slot canonical basis must be unique")
        return self


class NarrativePlan(Contract):
    """Deterministic plan. The model never receives ownership of these fields."""

    schema_version: Literal["narrative-plan-v1"]
    depth: InterpretationDepth
    language: Language
    slots: Annotated[tuple[NarrativePlanSlot, ...], Field(min_length=1, max_length=64)]

    @model_validator(mode="after")
    def unique_complete_slot_inventory(self) -> Self:
        ids = tuple(slot.slot_id for slot in self.slots)
        if len(ids) != len(set(ids)):
            raise ValueError("Narrative plan slots must be unique")
        if sum(slot.target == "summary" for slot in self.slots) != 1:
            raise ValueError("Narrative plan requires exactly one summary slot")
        return self


class InterpretationFoundationError(ValueError):
    """Static internal Phase 1 failure; not part of the public error contract."""

    def __init__(self, code: Literal[
        "invalid_catalog", "unsupported_foundation_scope", "invalid_plan",
        "invalid_ai_payload", "invalid_assembly",
    ]):
        self.code = code
        super().__init__(code)
