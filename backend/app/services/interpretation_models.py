"""Provider protocol and static domain failures; no provider, retry or network code."""
from typing import Literal, Protocol

from app.schemas.interpretation import (
    InterpretationContent, InterpretationDepth, InterpretationInput, Language,
)

ErrorCode = Literal[
    "interpretation_invalid_input", "interpretation_timeout", "interpretation_unavailable",
    "interpretation_invalid_response", "interpretation_schema_mismatch",
    "interpretation_rate_limited", "interpretation_refused",
]
MESSAGES: dict[ErrorCode, str] = {
    "interpretation_invalid_input": "Interpretation input is unavailable or invalid.",
    "interpretation_timeout": "Interpretation exceeded its time limit.",
    "interpretation_unavailable": "Interpretation is temporarily unavailable.",
    "interpretation_invalid_response": "Interpretation response is invalid.",
    "interpretation_schema_mismatch": "Interpretation response does not match its contract.",
    "interpretation_rate_limited": "Interpretation capacity is temporarily limited.",
    "interpretation_refused": "Interpretation could not be provided.",
}


class InterpretationError(Exception):
    def __init__(self, code: ErrorCode):
        if code not in MESSAGES:
            raise ValueError("Unknown interpretation error code")
        self.code = code
        super().__init__(MESSAGES[code])


class InterpretationProvider(Protocol):
    async def interpret(
        self, input: InterpretationInput, *, depth: InterpretationDepth, language: Language,
    ) -> InterpretationContent:
        """Return untrusted typed content; caller binds it to input before creating a result."""
        ...
