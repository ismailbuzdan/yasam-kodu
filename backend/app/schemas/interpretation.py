"""Stage 11A provider-neutral contracts; no HTTP route or provider implementation."""
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.knowledge.kameri.models import Claim, Source
from app.knowledge.kameri.repository import get_knowledge_base
from app.services.human_design_models import Authority, Center, DefinitionKind, HDType, Strategy


class Contract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True, allow_inf_nan=False,
                             hide_input_in_errors=True, revalidate_instances="always")


class InterpretationDepth(StrEnum):
    FREE = "free"
    STANDARD = "standard"
    PREMIUM = "premium"


Language = Literal["tr"]  # Extend by reviewed locale policy, not arbitrary prompt text.
Sign = Literal["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra",
               "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
Body = Literal["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
               "uranus", "neptune", "pluto", "true_north_node", "south_node", "lilith"]
HouseNumber = Annotated[int, Field(ge=1, le=12)]
Gate = Annotated[int, Field(ge=1, le=64)]
NumberValue = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33]
Profile = Literal["1/3", "1/4", "2/4", "2/5", "3/5", "3/6", "4/6", "4/1",
                  "5/1", "5/2", "6/2", "6/3"]
CulturalClaimId = Literal["HIJRI_CTX_001", "HIJRI_CTX_002", "HIJRI_CTX_003"]


class SymbolicBody(Contract):
    body: Body
    sign: Sign
    house: HouseNumber | None
    retrograde: bool


class SymbolicHouse(Contract):
    house: HouseNumber
    sign: Sign


class SymbolicAspect(Contract):
    body1: Body
    body2: Body
    type: Literal["conjunction", "sextile", "square", "trine", "opposition"]


class AstrologySymbols(Contract):
    bodies: Annotated[tuple[SymbolicBody, ...], Field(min_length=1, max_length=13)]
    ascendant: Sign | None
    mc: Sign | None
    houses: Annotated[tuple[SymbolicHouse, ...], Field(max_length=12)]
    aspects: Annotated[tuple[SymbolicAspect, ...], Field(max_length=78)]

    @model_validator(mode="after")
    def unique_symbols(self) -> Self:
        bodies = [body.body for body in self.bodies]
        houses = [house.house for house in self.houses]
        aspects = [(min(a.body1, a.body2), max(a.body1, a.body2), a.type) for a in self.aspects]
        if len(set(bodies)) != len(bodies) or len(set(houses)) != len(houses):
            raise ValueError("Duplicate symbolic position")
        if len(set(aspects)) != len(aspects):
            raise ValueError("Duplicate aspect")
        if any(a.body1 == a.body2 or a.body1 not in bodies or a.body2 not in bodies
               for a in self.aspects):
            raise ValueError("Aspect references unavailable bodies")
        return self


class SymbolicNumber(Contract):
    value: NumberValue
    is_master: bool


class NumerologySymbols(Contract):
    life_path: SymbolicNumber
    birthday: SymbolicNumber
    expression: SymbolicNumber
    soul_urge: SymbolicNumber | None
    personality: SymbolicNumber | None
    maturity: SymbolicNumber
    personal_year: SymbolicNumber | None


class HumanDesignSymbols(Contract):
    type: HDType
    strategy: Strategy
    authority: Authority
    profile: Profile
    definition: DefinitionKind
    defined_centers: Annotated[tuple[Center, ...], Field(max_length=9)]
    undefined_centers: Annotated[tuple[Center, ...], Field(max_length=9)]
    channels: Annotated[tuple[tuple[Gate, Gate], ...], Field(max_length=36)]
    active_gates: Annotated[tuple[Gate, ...], Field(max_length=64)]

    @model_validator(mode="after")
    def no_duplicate_symbols(self) -> Self:
        for values in (self.defined_centers, self.undefined_centers, self.channels, self.active_gates):
            if len(values) != len(set(values)):
                raise ValueError("Duplicate Human Design symbol")
        if set(self.defined_centers) & set(self.undefined_centers):
            raise ValueError("Conflicting center states")
        return self


class KameriContext(Contract):
    kb_version: Literal["kameri-kb-v1"] = "kameri-kb-v1"
    claims: Annotated[tuple[Claim, ...], Field(max_length=2)]
    sources: Annotated[tuple[Source, ...], Field(max_length=2)]
    abstained: bool
    reason: Literal["no_qualified_claims_for_context"] | None

    @model_validator(mode="after")
    def canonical_cultural_context(self) -> Self:
        # IDs alone are insufficient: edited text, policy or citation must fail closed too.
        kb = get_knowledge_base()
        ids = tuple(c.claim_id for c in self.claims)
        if ids not in ((), ("HIJRI_CTX_001", "HIJRI_CTX_002"), ("HIJRI_CTX_003",)):
            raise ValueError("Only a canonical K2B cultural selection is permitted")
        canonical = tuple(c for c in kb.claims if c.claim_id in ids)
        used = {r.source_id for c in canonical for r in c.source_refs}
        sources = tuple(s for s in kb.sources if s.source_id in used)
        if self.claims != canonical or self.sources != sources:
            raise ValueError("Kameri content must match the qualified snapshot")
        if self.abstained != (not ids) or self.reason != (
            "no_qualified_claims_for_context" if not ids else None
        ):
            raise ValueError("Invalid cultural abstention")
        return self


class InterpretationInput(Contract):
    schema_version: Literal["interpretation-input-v1"] = "interpretation-input-v1"
    astrology: AstrologySymbols | None
    numerology: NumerologySymbols | None
    human_design: HumanDesignSymbols | None
    kameri: KameriContext | None = None
    timeline: None = None  # No deterministic timeline contract exists in Life Code v1.

    @model_validator(mode="after")
    def has_symbols(self) -> Self:
        if all(v is None for v in (self.astrology, self.numerology, self.human_design)):
            raise ValueError("At least one verified calculation layer is required")
        return self


Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1200)]
FactRef = Annotated[str, StringConstraints(min_length=1, max_length=100,
                                          pattern=r"^(astrology|numerology|human_design)\.[a-z0-9_.]+$")]


class GroundedText(Contract):
    text: Text
    basis: Annotated[tuple[FactRef, ...], Field(min_length=1, max_length=8)]


SectionId = Literal["basic_triad", "strengths", "challenges", "character", "emotional",
                    "relationships", "career", "numerology", "human_design", "life_themes",
                    "shadow", "repeated_patterns", "main_potential", "life_lesson", "timeline"]
FREE_SECTIONS = ("basic_triad", "strengths", "challenges")
STANDARD_SECTIONS = FREE_SECTIONS + ("character", "emotional", "relationships", "career",
                                     "numerology", "human_design")
PREMIUM_SECTIONS = STANDARD_SECTIONS + ("life_themes", "shadow", "repeated_patterns",
                                       "main_potential", "life_lesson", "timeline")
SECTIONS_BY_DEPTH = {
    InterpretationDepth.FREE: FREE_SECTIONS,
    InterpretationDepth.STANDARD: STANDARD_SECTIONS,
    InterpretationDepth.PREMIUM: PREMIUM_SECTIONS,
}


class InterpretationSection(Contract):
    section: SectionId
    content: Annotated[tuple[GroundedText, ...], Field(min_length=1, max_length=3)] | None
    unavailable_reason: Literal["missing_input", "unsupported_timeline"] | None

    @model_validator(mode="after")
    def explicit_absence(self) -> Self:
        if (self.content is None) != (self.unavailable_reason is not None):
            raise ValueError("Unavailable section requires a reason and no content")
        if self.section == "timeline":
            if self.content is not None or self.unavailable_reason != "unsupported_timeline":
                raise ValueError("Timeline is unavailable in v1")
        elif self.unavailable_reason == "unsupported_timeline":
            raise ValueError("Invalid unavailable reason")
        return self


class CrossSystemTheme(Contract):
    kind: Literal["reinforced_theme", "complementary_theme", "tension"]
    narrative: GroundedText

    @model_validator(mode="after")
    def at_least_two_systems(self) -> Self:
        if len({ref.split(".")[0] for ref in self.narrative.basis}) < 2:
            raise ValueError("Cross-system comparison requires two distinct systems")
        return self


class CulturalNarrative(Contract):
    claim_id: CulturalClaimId
    text: Text
    # Citations/limitations are hydrated from the canonical input, never model-authored URLs.


class InterpretationContent(Contract):
    """Untrusted provider content; validate shape AND then bind to the supplied input."""
    language: Language
    depth: InterpretationDepth
    summary: GroundedText  # UI label: Genel Özet ve Sonuç.
    at_a_glance: Annotated[tuple[GroundedText, ...], Field(min_length=1, max_length=5)] | None
    sections: Annotated[tuple[InterpretationSection, ...], Field(max_length=15)]
    cross_system: Annotated[tuple[CrossSystemTheme, ...], Field(max_length=5)] | None
    kameri: Annotated[tuple[CulturalNarrative, ...], Field(min_length=1, max_length=2)] | None

    @model_validator(mode="after")
    def depth_contract(self) -> Self:
        if tuple(s.section for s in self.sections) != SECTIONS_BY_DEPTH[self.depth]:
            raise ValueError("Sections must match depth in canonical order")
        if self.depth == InterpretationDepth.PREMIUM:
            if self.at_a_glance is None:
                raise ValueError("Premium requires Tek Bakista")
        elif self.at_a_glance is not None:
            raise ValueError("At a glance is reserved for Premium")
        if self.depth == InterpretationDepth.FREE:
            if self.cross_system is not None or self.kameri is not None:
                raise ValueError("Free excludes cross-system and cultural narratives")
        elif self.cross_system == ():
            raise ValueError("Use null when no defensible cross-system theme exists")
        items = [self.summary] + list(self.at_a_glance or ())
        items += [p for s in self.sections for p in (s.content or ())]
        items += [t.narrative for t in (self.cross_system or ())]
        size = sum(len(p.text) for p in items) + sum(len(c.text) for c in (self.kameri or ()))
        limit = {InterpretationDepth.FREE: 2400, InterpretationDepth.STANDARD: 14000,
                 InterpretationDepth.PREMIUM: 26000}[self.depth]
        if size > limit:
            raise ValueError("Narrative exceeds depth character budget")
        return self


VersionId = Annotated[str, StringConstraints(min_length=1, max_length=80,
                                            pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$")]


class InterpretationMetadata(Contract):
    """Application-owned provenance, not provider-generated content or personal data."""
    prompt_version: VersionId
    config_version: VersionId
    provider: Literal["gemini", "openai", "template"]
    model: VersionId
    input_schema_version: Literal["interpretation-input-v1"] = "interpretation-input-v1"


class InterpretationResult(Contract):
    schema_version: Literal["interpretation-result-v1"] = "interpretation-result-v1"
    content: InterpretationContent
    metadata: InterpretationMetadata
    disclaimer: Literal["symbolic_self_reflection_not_professional_advice"] = (
        "symbolic_self_reflection_not_professional_advice"
    )
