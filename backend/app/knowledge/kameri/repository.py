"""One local immutable snapshot per process; URLs are citation metadata only."""

from pathlib import Path

from .models import Claim, KnowledgeBase

# Python's module initialization lock publishes only the fully validated snapshot.
# Invalid bundled data fails closed; no fallback to research, network or partial data.
_KB = KnowledgeBase.model_validate_json(
    (Path(__file__).parent / 'data' / 'kameri_kb_v1.json').read_bytes()
)


class ClaimNotFoundError(LookupError):
    """Explicit lookup found no qualified record; never echoes caller input."""

    def __init__(self) -> None:
        super().__init__('Qualified claim not found')


def get_knowledge_base() -> KnowledgeBase:
    return _KB


def get_claim(claim_id: str) -> Claim:
    """Non-personal reference lookup, never an abjad-to-Asma association."""
    if type(claim_id) is str:
        for claim in _KB.claims:
            if claim.claim_id == claim_id:
                return claim
    raise ClaimNotFoundError()
