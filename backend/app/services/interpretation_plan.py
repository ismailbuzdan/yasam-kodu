"""Free/exact-time foundation planner; additive and unused by the production service."""
from app.schemas.interpretation import InterpretationDepth, InterpretationInput, Language
from app.services.interpretation_ai_models import (
    NARRATIVE_PLAN_VERSION, InterpretationFoundationError, NarrativePlan, NarrativePlanSlot,
    SemanticEvidenceUnit,
)

SUN = "astro.sun.aries.house1.initiative.v1"
MOON = "astro.moon.libra.house7.relational_balance.v1"
ASC = "astro.ascendant.aries.direct_expression.v1"
MC = "astro.mc.capricorn.long_term_structure.v1"
OPPOSITION = "astro.sun_moon.opposition.theme_tension.v1"


def _basis(units: tuple[SemanticEvidenceUnit, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(ref for unit in units for ref in unit.public_basis))


class NarrativePlanner:
    """Assign pre-matched evidence to backend-owned Free slots in canonical order."""

    def plan(
        self, input: InterpretationInput, evidence: tuple[SemanticEvidenceUnit, ...], *,
        depth: InterpretationDepth, language: Language = "tr",
    ) -> NarrativePlan:
        if type(input) is not InterpretationInput or depth is not InterpretationDepth.FREE:
            raise InterpretationFoundationError("unsupported_foundation_scope")
        by_id = {unit.unit_id: unit for unit in evidence}
        if len(by_id) != len(evidence) or not {SUN, MOON, ASC, MC, OPPOSITION} <= set(by_id):
            raise InterpretationFoundationError("unsupported_foundation_scope")

        def slot(slot_id, target, section, unit_ids, purpose, max_length):
            units = tuple(by_id[unit_id] for unit_id in unit_ids)
            if section is not None and any(section not in unit.allowed_sections for unit in units):
                raise InterpretationFoundationError("invalid_plan")
            return NarrativePlanSlot(
                slot_id=slot_id, target=target, section=section,
                evidence_unit_ids=unit_ids, canonical_basis=_basis(units),
                purpose=purpose, max_length=max_length,
            )

        slots = (
            slot("summary.0", "summary", None, (SUN, MOON, ASC, MC, OPPOSITION),
                 "overall_synthesis", 500),
            slot("section.basic_triad.0", "section", "basic_triad", (SUN, ASC),
                 "placement_explanation", 360),
            slot("section.basic_triad.1", "section", "basic_triad", (MOON,),
                 "placement_explanation", 360),
            slot("section.basic_triad.2", "section", "basic_triad", (MC,),
                 "placement_explanation", 360),
            slot("section.strengths.0", "section", "strengths", (SUN,),
                 "constructive_potential", 360),
            slot("section.strengths.1", "section", "strengths", (MOON,),
                 "constructive_potential", 360),
            slot("section.strengths.2", "section", "strengths", (MC,),
                 "constructive_potential", 360),
            slot("section.challenges.0", "section", "challenges", (OPPOSITION,),
                 "tension_balance", 360),
        )
        return NarrativePlan(schema_version=NARRATIVE_PLAN_VERSION, depth=depth,
                             language=language, slots=slots)
