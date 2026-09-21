"""Bounded month-context selection, not personal interpretation."""

from .models import HijriMonthContext, KnowledgeSelection
from .repository import get_knowledge_base


def select_knowledge(context: HijriMonthContext) -> KnowledgeSelection:
    if type(context) is not HijriMonthContext:
        raise TypeError('A validated HijriMonthContext is required')
    claims = tuple(sorted(
        (claim for claim in get_knowledge_base().claims
         if claim.application_mode == 'hijri_month_context'
         and claim.application_key == context.hijri_month),
        key=lambda claim: claim.claim_id,
    ))
    return KnowledgeSelection(
        claims=claims,
        abstained=not claims,
        reason=None if claims else 'no_qualified_claims_for_context',
    )
