"""Groq hosted chat adapter; strict native schema plus canonical local validation."""
import asyncio
from collections.abc import Awaitable, Callable
from email.utils import parsedate_to_datetime
import json
import math
import time
from types import MappingProxyType

import httpx
from pydantic import Field, SecretStr, ValidationError

from app.core.config import Settings
from app.schemas.interpretation import (
    Contract, InterpretationContent, InterpretationDepth, InterpretationInput, Language, VersionId,
)
from app.services.interpretation_models import InterpretationError
from app.services.interpretation_prompts import TOKEN_CAPS, input_data, system_instruction
from app.services.interpretation_service import admit_input
from app.services.interpretation_validation import validate_content_for_input

GROQ_CONFIG_VERSION = "groq-chat-json-schema-v2"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_REASONING_EFFORT = "low"
MAX_RESPONSE_BYTES = 200_000
# Wire generation ceilings include room for the strict JSON envelope. Canonical prose/character
# budgets remain owned by TOKEN_CAPS and InterpretationContent validation.
GROQ_MAX_COMPLETION_TOKENS = MappingProxyType({
    InterpretationDepth.FREE: 2048,
    InterpretationDepth.STANDARD: TOKEN_CAPS[InterpretationDepth.STANDARD],
    InterpretationDepth.PREMIUM: TOKEN_CAPS[InterpretationDepth.PREMIUM],
})


class GroqConfig(Contract):
    model: VersionId
    api_key: SecretStr = Field(repr=False, exclude=True)
    timeout_seconds: float = Field(default=60.0, ge=1, le=120)
    max_retries: int = Field(default=2, ge=0, le=2)

    @classmethod
    def from_settings(cls, settings: Settings) -> "GroqConfig":
        try:
            config = cls(model=settings.groq_model, api_key=settings.groq_api_key,
                         timeout_seconds=settings.ai_request_timeout_seconds,
                         max_retries=settings.ai_max_retries)
            if not config.api_key.get_secret_value().strip():
                raise ValueError
            return config
        except (ValidationError, ValueError, TypeError):
            raise InterpretationError("interpretation_configuration_error") from None


def provider_schema() -> dict:
    """Derive Groq's documented strict subset without weakening final validation."""
    schema = InterpretationContent.model_json_schema()
    definitions = schema.get("$defs", {})

    def convert(node: dict) -> dict:
        if "$ref" in node:
            return convert(definitions[node["$ref"].split("/")[-1]])
        if "anyOf" in node:
            variants = node["anyOf"]
            nonnull = [variant for variant in variants if variant.get("type") != "null"]
            if len(variants) != 2 or len(nonnull) != 1:
                raise InterpretationError("interpretation_configuration_error")
            result = convert(nonnull[0])
            result["type"] = [result["type"], "null"]
            if "enum" in result:
                result["enum"] = [*result["enum"], None]
            return result
        result = {key: node[key] for key in
                  ("type", "enum", "required", "additionalProperties", "minItems", "maxItems")
                  if key in node}
        if "const" in node:
            result["enum"] = [node["const"]]
        if "properties" in node:
            result["properties"] = {key: convert(value) for key, value in node["properties"].items()}
        if "items" in node:
            result["items"] = convert(node["items"])
        return result

    return convert(schema)


def _retry_after(headers: httpx.Headers, now: float) -> float | None:
    value = headers.get("Retry-After")
    if value is None:
        return None
    try:
        seconds = float(value)
    except ValueError:
        try:
            seconds = parsedate_to_datetime(value).timestamp() - now
        except (ValueError, TypeError, OverflowError):
            return None
    return max(0.0, seconds) if math.isfinite(seconds) else None


def _response_code(response: httpx.Response) -> str:
    if response.status_code in {400, 401, 403}:
        return "interpretation_configuration_error"
    if response.status_code == 404:
        return "interpretation_model_not_found"
    if response.status_code == 408:
        return "interpretation_timeout"
    if response.status_code == 429:
        return "interpretation_rate_limited"
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
        body = response.json()
        choices = body["choices"]
        if not isinstance(choices, list) or len(choices) != 1:
            raise ValueError
        choice = choices[0]
        message = choice["message"]
        finish_reason = choice.get("finish_reason")
        if (isinstance(finish_reason, str) and finish_reason.lower() in
                {"content_filter", "refusal", "safety"}) or message.get("refusal") is not None:
            raise InterpretationError("interpretation_refusal")
        content = message["content"]
        if not isinstance(content, str) or not content or finish_reason not in {"stop", "STOP"}:
            raise ValueError
    except InterpretationError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise InterpretationError("interpretation_invalid_response") from None
    try:
        json.loads(content, object_pairs_hook=_unique_pairs,
                   parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, RecursionError):
        raise InterpretationError("interpretation_invalid_response") from None
    try:
        result = InterpretationContent.model_validate_json(content)
    except ValidationError:
        raise InterpretationError("interpretation_schema_mismatch") from None
    return validate_content_for_input(result, input, depth=depth, language=language)


class GroqInterpretationProvider:
    def __init__(self, config: GroqConfig, *, client_factory: Callable = httpx.AsyncClient,
                 sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
                 clock: Callable[[], float] = time.monotonic,
                 wall_clock: Callable[[], float] = time.time):
        try:
            self._config = GroqConfig(model=config.model, api_key=config.api_key,
                                      timeout_seconds=config.timeout_seconds,
                                      max_retries=config.max_retries)
            if not self._config.api_key.get_secret_value().strip():
                raise ValueError
        except (ValidationError, ValueError, AttributeError, TypeError):
            raise InterpretationError("interpretation_configuration_error") from None
        self._client_factory = client_factory
        self._sleep = sleep
        self._clock = clock
        self._wall_clock = wall_clock

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
            response = None
            try:
                response = await client.post(
                    GROQ_BASE_URL + "/chat/completions",
                    headers={"Authorization": "Bearer " + self._config.api_key.get_secret_value(),
                             "Accept": "application/json"},
                    json={
                        "model": self._config.model,
                        "stream": False,
                        "temperature": 0,
                        "max_completion_tokens": GROQ_MAX_COMPLETION_TOKENS[depth],
                        "reasoning_effort": GROQ_REASONING_EFFORT,
                        "include_reasoning": False,
                        "response_format": {
                            "type": "json_schema",
                            "json_schema": {
                                "name": "life_code_interpretation",
                                "strict": True,
                                "schema": provider_schema(),
                            },
                        },
                        "messages": [
                            {"role": "system", "content": system_instruction(depth, repair=repair)},
                            {"role": "user", "content": input_data(input)},
                        ],
                    },
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
                    if response is not None and code == "interpretation_rate_limited":
                        retry_after = _retry_after(response.headers, self._wall_clock())
                        if retry_after is not None:
                            if retry_after > 5:
                                retryable = False
                            delay = max(delay, retry_after)
            except (TimeoutError, httpx.TimeoutException):
                code, retryable, delay = "interpretation_timeout", True, min(2 ** attempt, 5)
            except httpx.TransportError:
                code, retryable, delay = "interpretation_unavailable", True, min(2 ** attempt, 5)
            if not retryable or attempt == self._config.max_retries or delay >= deadline - self._clock():
                raise InterpretationError(code) from None
            if delay:
                await self._sleep(delay)
        raise InterpretationError("interpretation_unavailable")
