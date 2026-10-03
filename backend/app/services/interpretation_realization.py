"""Deterministic bounded-realization policy for the non-production foundation path."""
from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence
from typing import Literal, Pattern

from app.services.interpretation_ai_models import (
    AITextRealization, ForbiddenSemanticExtension, NarrativePlanSlot, SemanticEvidenceUnit,
)

RealizationFailureCode = Literal[
    "forbidden_semantic_extension", "excessive_certainty", "prohibited_claim_class",
    "invalid_realization_policy",
]
ProhibitedClaimClass = Literal[
    "medical_or_mental_diagnosis", "deterministic_future_prediction",
    "absolute_behavioral_certainty",
]


class BoundedRealizationError(ValueError):
    """Static policy failure metadata; deliberately excludes generated prose."""

    def __init__(
        self, code: RealizationFailureCode, *, slot_id: str,
        category: ForbiddenSemanticExtension | ProhibitedClaimClass | None = None,
    ):
        self.code = code
        self.slot_id = slot_id
        self.category = category
        suffix = f":{category}" if category is not None else ""
        super().__init__(f"{code}:{slot_id}{suffix}")


def _patterns(*values: str) -> tuple[Pattern[str], ...]:
    return tuple(re.compile(value) for value in values)


# Evidence-specific categories. Patterns use bounded Turkish roots/phrases rather than a general stemmer.
EXTENSION_PATTERNS: dict[ForbiddenSemanticExtension, tuple[Pattern[str], ...]] = {
    "regret": _patterns(r"\bpişman(?:lık\w*)?\b"),
    "impatience": _patterns(r"\bsabırsız(?:lık\w*)?\b", r"\baceleci\w*\b"),
    "impulsiveness": _patterns(
        r"\bdürtüsel\w*\b", r"\bfevri\w*\b", r"\baceleci\w*\b",
        r"\bdüşünmeden\s+hareket\w*\b",
    ),
    "diagnosis": _patterns(
        r"\b(?:depresyon|anksiyete|bipolar|psikoz|şizofreni)\s+"
        r"(?:hastası\s+olduğunuzu|tanısı\w*|bozukluğu\w*)\b",
    ),
    "certain_behavior": _patterns(
        r"\bkesinlikle\b", r"\bsizi\b.{0,80}\b(?:yapar|yapmaktadır)\b",
        r"\bzorunluluğu\s+vardır\b", r"\bdoğal\s+olarak\s+ortaya\s+çıkar\b",
    ),
    "career_success": _patterns(
        r"\bkariyerinizde\b.{0,50}\b(?:başarı\w*|yükseleceksiniz)\b",
    ),
    "certain_outcome": _patterns(
        r"\b(?:kaçınılmaz|garanti(?:dir)?|kesin\s+sonuç)\b",
    ),
}


# Claim classes are prohibited independently of which evidence unit is assigned.
PROHIBITED_CLAIM_PATTERNS: dict[ProhibitedClaimClass, tuple[Pattern[str], ...]] = {
    "medical_or_mental_diagnosis": _patterns(
        r"\b(?:depresyon|anksiyete|bipolar|psikoz|şizofreni)\s+"
        r"(?:hastası\s+olduğunuzu|tanısı\w*|bozukluğu\w*)\b",
        r"\bsizde\b.{0,40}\b(?:anksiyete|depresyon|bipolar|psikoz|şizofreni)\b"
        r".{0,30}\bvardır\b",
    ),
    "deterministic_future_prediction": _patterns(
        r"\bgelecekte\b.{0,80}\b(?:olacak|olacaksınız|yaşayacaksınız|karşılaşacaksınız)\b",
        r"\b(?:evleneceksiniz|zenginleşeceksiniz|kazanacaksınız|kaybedeceksiniz)\b",
        r"\bbaşınıza\b.{0,40}\bgelecek\b",
    ),
    "absolute_behavioral_certainty": _patterns(
        r"\bkesinlikle\b", r"\bsizi\b.{0,80}\b(?:yapar|yapmaktadır)\b",
        r"\bzorunluluğu\s+vardır\b", r"\bdoğal\s+olarak\s+ortaya\s+çıkar\b",
    ),
}


def normalize_turkish_text(text: str) -> str:
    """Preserve Turkish letters while normalizing case, punctuation spacing and Unicode form."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = re.sub(r"[^\w\sçğıöşü]", " ", normalized, flags=re.UNICODE)
    return " ".join(normalized.split())


def _matches(text: str, patterns: tuple[Pattern[str], ...]) -> bool:
    return any(pattern.search(text) is not None for pattern in patterns)


class BoundedRealizationValidator:
    """Reject known high-risk semantic expansion without rewriting generated text.

    This bounded policy is not a general Turkish entailment proof or safety classifier.
    """

    def validate(
        self, realization: AITextRealization, slot: NarrativePlanSlot,
        evidence_units: Sequence[SemanticEvidenceUnit],
    ) -> None:
        if (type(realization) is not AITextRealization or type(slot) is not NarrativePlanSlot
                or realization.slot_id != slot.slot_id):
            raise BoundedRealizationError(
                "invalid_realization_policy", slot_id=getattr(slot, "slot_id", "invalid"))
        unit_ids = tuple(unit.unit_id for unit in evidence_units)
        if (len(unit_ids) != len(set(unit_ids))
                or unit_ids != tuple(slot.evidence_unit_ids)
                or any(type(unit) is not SemanticEvidenceUnit for unit in evidence_units)):
            raise BoundedRealizationError(
                "invalid_realization_policy", slot_id=slot.slot_id)

        text = normalize_turkish_text(realization.text)

        for claim_class, patterns in PROHIBITED_CLAIM_PATTERNS.items():
            if _matches(text, patterns):
                code: RealizationFailureCode = (
                    "excessive_certainty"
                    if claim_class == "absolute_behavioral_certainty"
                    else "prohibited_claim_class"
                )
                raise BoundedRealizationError(
                    code, slot_id=slot.slot_id, category=claim_class)

        assigned_categories = frozenset(
            category for unit in evidence_units for category in unit.forbidden_extensions
        )
        if not assigned_categories <= EXTENSION_PATTERNS.keys():
            raise BoundedRealizationError(
                "invalid_realization_policy", slot_id=slot.slot_id)
        # Registry order is the stable diagnostic priority when one phrase matches multiple classes.
        for category, patterns in EXTENSION_PATTERNS.items():
            if category not in assigned_categories:
                continue
            if _matches(text, patterns):
                raise BoundedRealizationError(
                    "forbidden_semantic_extension", slot_id=slot.slot_id, category=category)
