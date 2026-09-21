"""Application firewall: month context never becomes personal Asma or a reading."""

import inspect
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.knowledge.kameri.models import HijriMonthContext, KnowledgeSelection
from app.knowledge.kameri.repository import get_claim
from app.knowledge.kameri.selector import select_knowledge


@pytest.mark.parametrize('month', range(1, 13))
def test_all_months_have_only_qualified_coverage_or_explicit_abstention(month):
    context = HijriMonthContext(hijri_month=month)
    result = select_knowledge(context)
    expected = {9: ('HIJRI_CTX_001', 'HIJRI_CTX_002'), 12: ('HIJRI_CTX_003',)}.get(month, ())
    assert tuple(claim.claim_id for claim in result.claims) == expected
    assert result.abstained == (not expected)
    assert result.reason == (None if expected else 'no_qualified_claims_for_context')
    assert result.kb_version == 'kameri-kb-v1'
    assert result == select_knowledge(context)
    assert all(claim.application_key == month for claim in result.claims)


def test_abjad_66_does_not_select_asma_claim():
    synthetic_abjad = SimpleNamespace(raw_sum=66)
    assert tuple(inspect.signature(select_knowledge).parameters) == ('context',)
    for unapproved in (synthetic_abjad, 66, {'raw_sum': 66}):
        with pytest.raises(TypeError):
            select_knowledge(unapproved)
    for month in range(1, 13):
        assert 'ASMA_NUM_001' not in {
            c.claim_id for c in select_knowledge(HijriMonthContext(hijri_month=month)).claims
        }
    reference = get_claim('ASMA_NUM_001')
    assert reference.application_mode == 'reference_only'
    assert reference.application_key is None
    with pytest.raises(ValidationError):
        KnowledgeSelection(claims=(reference,), abstained=False, reason=None)


@pytest.mark.parametrize('value', [0, 13, -1, 66, True, False, 9.0, '9', None])
def test_month_context_is_strict_and_bounded(value):
    with pytest.raises(ValidationError):
        HijriMonthContext(hijri_month=value)


@pytest.mark.parametrize('field', ['name', 'arabic_input', 'abjad', 'utc_datetime',
                                  'latitude', 'longitude', 'prompt'])
def test_context_rejects_unneeded_personal_and_calculation_inputs(field):
    with pytest.raises(ValidationError):
        HijriMonthContext(hijri_month=9, **{field: 'not accepted'})


@pytest.mark.parametrize('claims,abstained,reason', [
    ((), False, None), ((), True, None),
    ((get_claim('HIJRI_CTX_001'),), True, 'no_qualified_claims_for_context'),
    ((get_claim('HIJRI_CTX_001'),), False, 'no_qualified_claims_for_context'),
])
def test_contradictory_selection_states_rejected(claims, abstained, reason):
    with pytest.raises(ValidationError):
        KnowledgeSelection(claims=claims, abstained=abstained, reason=reason)
