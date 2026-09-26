"""Read-only allowlist projection. Never invokes a calculation or copies raw metadata."""
from typing import TYPE_CHECKING

from pydantic import ValidationError

from app.knowledge.kameri.models import HijriMonthContext
from app.knowledge.kameri.repository import get_knowledge_base
from app.knowledge.kameri.selector import select_knowledge
from app.schemas.interpretation import (
    AstrologySymbols, HumanDesignSymbols, InterpretationInput, KameriContext, NumerologySymbols,
    SymbolicAspect, SymbolicBody, SymbolicHouse, SymbolicNumber,
)
from app.services.interpretation_models import InterpretationError

if TYPE_CHECKING:
    from app.services.life_code_models import LifeCodeResult


def project_interpretation(
    result: "LifeCodeResult", *, include_personal_year: bool = False,
    kameri_context: HijriMonthContext | None = None,
) -> InterpretationInput:
    # Local import is solely for the input type check; no engine/service calls.
    from app.services.life_code_models import LifeCodeResult

    if type(result) is not LifeCodeResult or type(include_personal_year) is not bool:
        raise InterpretationError("interpretation_invalid_input")
    if kameri_context is not None and type(kameri_context) is not HijriMonthContext:
        raise InterpretationError("interpretation_invalid_input")
    try:
        astro, num, hd = result.astrology, result.numerology, result.human_design
        if include_personal_year and num.personal_year is not None and num.metadata.target_year is None:
            raise InterpretationError("interpretation_invalid_input")

        def number(value):
            return None if value is None else SymbolicNumber(value=value.value, is_master=value.is_master)

        cultural = None
        if kameri_context is not None:
            # Revalidate even frozen models: unchecked model_copy/construct is not admission.
            context = HijriMonthContext.model_validate(kameri_context.model_dump())
            selection = select_knowledge(context)
            used = {ref.source_id for claim in selection.claims for ref in claim.source_refs}
            cultural = KameriContext(
                claims=selection.claims,
                sources=tuple(s for s in get_knowledge_base().sources if s.source_id in used),
                abstained=selection.abstained, reason=selection.reason,
            )
        return InterpretationInput(
            astrology=AstrologySymbols(
                bodies=tuple(SymbolicBody(body=key, sign=value.sign, house=value.house,
                                          retrograde=value.retrograde)
                             for key, value in sorted(astro.bodies.items())),
                ascendant=astro.ascendant.sign, mc=astro.mc.sign,
                houses=tuple(SymbolicHouse(house=h.house, sign=h.sign)
                             for h in sorted(astro.houses, key=lambda h: h.house)),
                aspects=tuple(SymbolicAspect(body1=a.body1, body2=a.body2, type=a.type)
                              for a in sorted(astro.aspects, key=lambda a: (a.body1, a.body2, a.type))),
            ),
            numerology=NumerologySymbols(
                life_path=number(num.life_path), birthday=number(num.birthday),
                expression=number(num.expression), soul_urge=number(num.soul_urge),
                personality=number(num.personality), maturity=number(num.maturity),
                personal_year=number(num.personal_year) if include_personal_year else None,
            ),
            human_design=HumanDesignSymbols(
                type=hd.type, strategy=hd.strategy, authority=hd.authority, profile=hd.profile.label,
                definition=hd.definition, defined_centers=tuple(hd.defined_centers),
                undefined_centers=tuple(hd.undefined_centers), channels=tuple(hd.channels),
                active_gates=tuple(hd.active_gates),
            ),
            kameri=cultural,
        )
    except (ValidationError, AttributeError, TypeError, ValueError):
        # Never propagate Pydantic input/ctx or a string from a mutable engine result.
        raise InterpretationError("interpretation_invalid_input") from None
