"""Deterministic structural/input binding, not a general natural-language safety classifier."""
from pydantic import ValidationError

from app.schemas.interpretation import (
    InterpretationContent, InterpretationDepth, InterpretationInput, Language,
)
from app.services.interpretation_models import InterpretationError


def available_fact_refs(input: InterpretationInput) -> frozenset[str]:
    """Only present fields can support a narrative; no paths into excluded raw data."""
    refs: set[str] = set()
    if input.astrology is not None:
        astro = input.astrology
        for body in astro.bodies:
            prefix = f"astrology.bodies.{body.body}"
            refs.update((f"{prefix}.sign", f"{prefix}.retrograde"))
            if body.house is not None:
                refs.add(f"{prefix}.house")
        if astro.ascendant is not None:
            refs.add("astrology.ascendant")
        if astro.mc is not None:
            refs.add("astrology.mc")
        for house in astro.houses:
            refs.add(f"astrology.houses.{house.house}.sign")
        for i, _ in enumerate(astro.aspects):
            refs.add(f"astrology.aspects.{i}.type")
    if input.numerology is not None:
        for name in type(input.numerology).model_fields:
            if getattr(input.numerology, name) is not None:
                refs.update((f"numerology.{name}.value", f"numerology.{name}.is_master"))
    if input.human_design is not None:
        for name in type(input.human_design).model_fields:
            refs.add(f"human_design.{name}")
    return frozenset(refs)


def validate_content_for_input(
    content: InterpretationContent, input: InterpretationInput, *,
    depth: InterpretationDepth, language: Language,
) -> InterpretationContent:
    """Mandatory before application-owned result assembly; no logging or partial fallback."""
    if type(content) is not InterpretationContent or type(input) is not InterpretationInput:
        raise InterpretationError("interpretation_schema_mismatch")
    try:
        content = InterpretationContent.model_validate(content.model_dump(warnings=False))
        input = InterpretationInput.model_validate(input.model_dump(warnings=False))
    except ValidationError:
        raise InterpretationError("interpretation_schema_mismatch") from None
    if content.depth != depth or content.language != language:
        raise InterpretationError("interpretation_schema_mismatch")
    refs = available_fact_refs(input)
    paragraphs = [content.summary] + list(content.at_a_glance or ())
    paragraphs += [theme.narrative for theme in (content.cross_system or ())]
    triad = {"astrology.bodies.sun.sign", "astrology.bodies.moon.sign", "astrology.ascendant"}
    for section in content.sections:
        expected_absence = None
        if section.section == "timeline":
            expected_absence = "unsupported_timeline"
        elif (section.section == "basic_triad" and not triad <= refs
              or section.section == "numerology" and input.numerology is None
              or section.section == "human_design" and input.human_design is None):
            expected_absence = "missing_input"
        if section.unavailable_reason != expected_absence:
            raise InterpretationError("interpretation_invalid_response")
        section_refs = {ref for p in (section.content or ()) for ref in p.basis}
        if section.content is not None:
            if section.section == "basic_triad" and not triad <= section_refs:
                raise InterpretationError("interpretation_invalid_response")
            if section.section in {"numerology", "human_design"} and not any(
                ref.startswith(section.section + ".") for ref in section_refs
            ):
                raise InterpretationError("interpretation_invalid_response")
        paragraphs += list(section.content or ())
    if any(not set(p.basis) <= refs for p in paragraphs):
        raise InterpretationError("interpretation_invalid_response")
    claim_ids = tuple(c.claim_id for c in input.kameri.claims) if input.kameri else ()
    expected_ids = () if depth == InterpretationDepth.FREE else claim_ids
    if tuple(c.claim_id for c in (content.kameri or ())) != expected_ids:
        raise InterpretationError("interpretation_invalid_response")
    return content
