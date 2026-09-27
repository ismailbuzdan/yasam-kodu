"""Local Ollama chat adapter; no calculation, API key, fallback, logging or persistence."""
import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import json
import time
from urllib.parse import urlparse

import httpx
from pydantic import Field, ValidationError, field_validator

from app.core.config import Settings
from app.schemas.interpretation import (
    Contract, InterpretationContent, InterpretationDepth, InterpretationInput, Language, VersionId,
)
from app.services.interpretation_models import InterpretationError
from app.services.interpretation_prompts import TOKEN_CAPS, input_data, system_instruction
from app.services.interpretation_service import admit_input
from app.services.interpretation_validation import validate_content_for_input

OLLAMA_CONFIG_VERSION = "ollama-chat-json-schema-v1"
MAX_RESPONSE_BYTES = 200_000
JSON_ENVELOPE_TOKEN_ALLOWANCE = 1024


class OllamaConfig(Contract):
    model: VersionId
    base_url: str
    timeout_seconds: float = Field(default=120.0, ge=1, le=600)
    max_retries: int = Field(default=2, ge=0, le=2)

    @field_validator("base_url")
    @classmethod
    def local_base_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.query or parsed.fragment:
            raise ValueError("A valid Ollama base URL is required")
        if parsed.path not in {"", "/"}:
            raise ValueError("Ollama base URL must not include an API path")
        return value.rstrip("/")

    @classmethod
    def from_settings(cls, settings: Settings) -> "OllamaConfig":
        try:
            return cls(model=settings.ollama_model, base_url=settings.ollama_base_url,
                       timeout_seconds=settings.ollama_request_timeout_seconds,
                       max_retries=settings.ai_max_retries)
        except (ValidationError, ValueError, TypeError):
            raise InterpretationError("interpretation_configuration_error") from None


@dataclass(frozen=True)
class OllamaAvailability:
    reachable: bool
    model_available: bool | None


def _response_code(response: httpx.Response) -> str:
    if response.status_code == 404:
        return "interpretation_model_not_found"
    if response.status_code == 408:
        return "interpretation_timeout"
    if response.status_code == 429:
        return "interpretation_rate_limited"
    if response.status_code == 400:
        return "interpretation_configuration_error"
    return "interpretation_unavailable"


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _decode_response(response: httpx.Response, input: InterpretationInput, depth: InterpretationDepth,
                     language: Language) -> InterpretationContent:
    if response.status_code >= 400:
        raise InterpretationError(_response_code(response))
    if len(response.content) > MAX_RESPONSE_BYTES:
        raise InterpretationError("interpretation_invalid_response")
    try:
        body = response.json(object_pairs_hook=_unique_pairs,
                             parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        if not isinstance(body, dict) or body.get("done") is not True or body.get("done_reason") != "stop":
            raise ValueError
        message = body["message"]
        # Qwen thinking is a separate Ollama field and is intentionally never retained or returned.
        if not isinstance(message, dict) or message.get("role") != "assistant" or message.get("tool_calls"):
            raise ValueError
        content = message["content"]
        if not isinstance(content, str) or not content:
            raise ValueError
    except (AttributeError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise InterpretationError("interpretation_invalid_response") from None
    try:
        result = InterpretationContent.model_validate_json(content)
    except ValidationError:
        raise InterpretationError("interpretation_schema_mismatch") from None
    return validate_content_for_input(result, input, depth=depth, language=language)


class OllamaInterpretationProvider:
    def __init__(self, config: OllamaConfig, *, client_factory: Callable = httpx.AsyncClient,
                 sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
                 clock: Callable[[], float] = time.monotonic):
        try:
            self._config = OllamaConfig.model_validate(config.model_dump())
        except (ValidationError, ValueError, AttributeError, TypeError):
            raise InterpretationError("interpretation_configuration_error") from None
        self._client_factory, self._sleep, self._clock = client_factory, sleep, clock

    async def check_availability(self) -> OllamaAvailability:
        """Explicit cheap health probe; interpretation does not call it automatically."""
        try:
            async with self._client_factory(timeout=min(self._config.timeout_seconds, 5.0),
                                            trust_env=False) as client:
                response = await client.get(self._config.base_url + "/api/tags")
            if response.status_code != 200:
                return OllamaAvailability(reachable=True, model_available=None)
            body = response.json()
            models = body.get("models") if isinstance(body, dict) else None
            if not isinstance(models, list):
                return OllamaAvailability(reachable=True, model_available=None)
            available = any(isinstance(item, dict) and self._config.model in
                            {item.get("name"), item.get("model")} for item in models)
            return OllamaAvailability(reachable=True, model_available=available)
        except (httpx.HTTPError, TimeoutError, ValueError, TypeError):
            return OllamaAvailability(reachable=False, model_available=None)

    async def interpret(self, input: InterpretationInput, *, depth: InterpretationDepth,
                        language: Language) -> InterpretationContent:
        input = admit_input(input, depth, language)
        try:
            async with asyncio.timeout(self._config.timeout_seconds):
                async with self._client_factory(timeout=self._config.timeout_seconds,
                                                trust_env=False) as client:
                    return await self._attempts(client, input, depth, language)
        except InterpretationError as error:
            raise InterpretationError(error.code) from None
        except (TimeoutError, httpx.TimeoutException):
            raise InterpretationError("interpretation_timeout") from None
        except httpx.TransportError:
            raise InterpretationError("interpretation_unavailable") from None

    async def _attempts(self, client, input, depth, language):
        deadline = self._clock() + self._config.timeout_seconds
        repair = False
        for attempt in range(self._config.max_retries + 1):
            remaining = deadline - self._clock()
            if remaining <= 0:
                raise InterpretationError("interpretation_timeout")
            try:
                response = await client.post(
                    self._config.base_url + "/api/chat",
                    json={"model": self._config.model, "stream": False, "think": False,
                          "format": InterpretationContent.model_json_schema(),
                          # Canonical prose budgets remain unchanged; local models also need room for
                          # JSON field names, basis arrays and unavailable-section envelopes.
                          "options": {"temperature": 0,
                                      "num_predict": TOKEN_CAPS[depth] + JSON_ENVELOPE_TOKEN_ALLOWANCE},
                          "messages": [{"role": "system", "content": system_instruction(depth, repair=repair)},
                                       {"role": "user", "content": input_data(input)}]},
                    timeout=remaining,
                )
                return _decode_response(response, input, depth, language)
            except InterpretationError as error:
                code = error.code
                if code in {"interpretation_invalid_response", "interpretation_schema_mismatch"}:
                    if repair:
                        raise InterpretationError("interpretation_schema_mismatch") from None
                    repair, retryable, delay = True, True, 0.0
                else:
                    retryable = code in {"interpretation_timeout", "interpretation_unavailable",
                                         "interpretation_rate_limited"}
                    delay = min(2 ** attempt, 5)
            except (TimeoutError, httpx.TimeoutException):
                code, retryable, delay = "interpretation_timeout", True, min(2 ** attempt, 5)
            except httpx.TransportError:
                code, retryable, delay = "interpretation_unavailable", True, min(2 ** attempt, 5)
            if not retryable or attempt == self._config.max_retries or delay >= deadline - self._clock():
                raise InterpretationError(code) from None
            if delay:
                await self._sleep(delay)
        raise InterpretationError("interpretation_unavailable")
