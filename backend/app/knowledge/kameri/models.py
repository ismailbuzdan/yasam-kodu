"""Immutable, closed v1 vocabulary and applicability policy (ADR-020)."""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
ClaimId = Literal['ASMA_NUM_001', 'HIJRI_CTX_001', 'HIJRI_CTX_002', 'HIJRI_CTX_003']
SourceId = Literal['KI-A03', 'KI-B05', 'KI-B07', 'KI-B08']
Version = Literal['kameri-kb-v1']


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid', strict=True)


class Source(FrozenModel):
    source_id: SourceId
    title: Text
    url: Annotated[str, StringConstraints(pattern=r'^https://[^\s]+$')]
    locator: Text
    tier: Literal['A', 'B']
    verified_scope: Text


class SourceRef(FrozenModel):
    source_id: SourceId
    locator: Text


class Claim(FrozenModel):
    claim_id: ClaimId
    kb_version: Version
    feature: Literal['asma_numeric', 'hijri_context']
    method_id: Text
    tradition_id: Text
    classification: Literal['ABJAD_NUMERIC_VALUE', 'CULTURAL_CONTEXT']
    claim_type: Literal['abjad_numeric_value', 'cultural_context']
    statement: Annotated[Text, Field(max_length=300)]
    normalized_theme: Text
    original_context: Text
    source_refs: Annotated[tuple[SourceRef, ...], Field(min_length=1)]
    limitations: Annotated[tuple[Text, ...], Field(min_length=1)]
    does_not_support: Annotated[tuple[Text, ...], Field(min_length=1)]
    religious_claim_boundary: Text
    ai_usage: Literal['restricted']
    application_mode: Literal['reference_only', 'hijri_month_context']
    application_key: Literal[9, 12] | None

    @model_validator(mode='after')
    def enforce_applicability(self) -> Self:
        if self.claim_id == 'ASMA_NUM_001':
            expected = ('asma_numeric', 'ABJAD_NUMERIC_VALUE', 'abjad_numeric_value',
                        'reference_only', None)
        else:
            month = 12 if self.claim_id == 'HIJRI_CTX_003' else 9
            expected = ('hijri_context', 'CULTURAL_CONTEXT', 'cultural_context',
                        'hijri_month_context', month)
        actual = (self.feature, self.classification, self.claim_type,
                  self.application_mode, self.application_key)
        if actual != expected:
            raise ValueError('Claim applicability violates the v1 policy')
        refs = tuple(ref.source_id for ref in self.source_refs)
        if len(refs) != len(set(refs)):
            raise ValueError('Duplicate claim source')
        return self


class KnowledgeBase(FrozenModel):
    schema_version: Version
    sources: tuple[Source, ...]
    claims: tuple[Claim, ...]

    @model_validator(mode='after')
    def enforce_inventory(self) -> Self:
        ids = tuple(claim.claim_id for claim in self.claims)
        if len(ids) != 4 or set(ids) != {
            'ASMA_NUM_001', 'HIJRI_CTX_001', 'HIJRI_CTX_002', 'HIJRI_CTX_003'
        }:
            raise ValueError('The v1 inventory must contain exactly four qualified claims')
        sources = tuple(source.source_id for source in self.sources)
        used = {ref.source_id for claim in self.claims for ref in claim.source_refs}
        if len(sources) != 4 or set(sources) != {'KI-A03', 'KI-B05', 'KI-B07', 'KI-B08'}:
            raise ValueError('The v1 inventory must contain exactly four sources')
        if used != set(sources):
            raise ValueError('Unresolved or unused source')
        return self


class HijriMonthContext(FrozenModel):
    """Already calculated month; no dates, names, abjad or astronomical inputs."""

    hijri_month: Annotated[int, Field(ge=1, le=12)]


class KnowledgeSelection(FrozenModel):
    kb_version: Version = 'kameri-kb-v1'
    claims: tuple[Claim, ...]
    abstained: bool
    reason: Literal['no_qualified_claims_for_context'] | None

    @model_validator(mode='after')
    def enforce_result(self) -> Self:
        if self.abstained != (not self.claims):
            raise ValueError('Abstention must match empty coverage')
        expected = 'no_qualified_claims_for_context' if self.abstained else None
        if self.reason != expected:
            raise ValueError('Invalid abstention reason')
        if any(claim.application_mode != 'hijri_month_context' for claim in self.claims):
            raise ValueError('Reference-only claims cannot enter automatic selection')
        return self
