"""Gemini Developer API adapter. No calculation imports, logging, tools or persistence."""
import asyncio
from collections.abc import Awaitable, Callable
from email.utils import parsedate_to_datetime
import json
import math
import time

from google import genai
from google.genai import errors, types
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


class GeminiConfig(Contract):
    model: VersionId
    api_key: SecretStr = Field(repr=False, exclude=True)
    timeout_seconds: float = Field(default=60.0, ge=1, le=120)
    max_retries: int = Field(default=2, ge=0, le=2)

    @classmethod
    def from_settings(cls, settings: Settings) -> "GeminiConfig":
        try:
            config = cls(model=settings.gemini_model, api_key=settings.gemini_api_key,
                         timeout_seconds=settings.ai_request_timeout_seconds,
                         max_retries=settings.ai_max_retries)
            if not config.api_key.get_secret_value().strip():
                raise ValueError
            return config
        except (ValidationError, ValueError, TypeError):
            raise InterpretationError("interpretation_configuration_error") from None


def provider_schema() -> dict:
    """Derive a small JSON dialect from the canonical content, never duplicate its fields.

    Inline local refs, remove unsupported string length/pattern and presentation/default fields,
    replace const with enum and nullable anyOf with a type array. Full constraints remain local.
    """
    schema = InterpretationContent.model_json_schema()
    definitions = schema.get("$defs", {})

    def convert(node: dict) -> dict:
        if "$ref" in node:
            return convert(definitions[node["$ref"].split("/")[-1]])
        if "anyOf" in node:
            variants = node["anyOf"]
            nonnull = [v for v in variants if v.get("type") != "null"]
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


def _client(config: GeminiConfig):
    # Explicit endpoint/key prevent ambient GOOGLE_* settings from selecting a different service.
    return genai.Client(enterprise=False, api_key=config.api_key.get_secret_value(),
                        http_options=types.HttpOptions(
                            base_url="https://generativelanguage.googleapis.com", api_version="v1beta",
                            timeout=int(config.timeout_seconds * 1000),
                            retry_options=types.HttpRetryOptions(attempts=1),
                            client_args={"trust_env": False}, async_client_args={"trust_env": False},
                        ))


def _response_text(response: types.GenerateContentResponse) -> str:
    feedback = response.prompt_feedback
    if feedback and feedback.block_reason not in (None, "BLOCKED_REASON_UNSPECIFIED"):
        raise InterpretationError("interpretation_refusal")
    candidates = response.candidates or []
    if any(c.finish_reason in {"SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT",
                              "SPII", "IMAGE_SAFETY", "MODEL_ARMOR"}
           or any(r.blocked for r in (c.safety_ratings or [])) for c in candidates):
        raise InterpretationError("interpretation_refusal")
    if len(candidates) != 1 or candidates[0].finish_reason != "STOP":
        raise InterpretationError("interpretation_invalid_response")
    content = candidates[0].content
    parts = content.parts if content else None
    if not parts:
        raise InterpretationError("interpretation_invalid_response")
    texts = []
    for part in parts:
        # Avoid response.text: it can drop non-text parts and emit SDK warnings.
        fields = part.model_dump(exclude_none=True)
        if set(fields) - {"text", "thought", "thought_signature"}:
            raise InterpretationError("interpretation_invalid_response")
        if not part.thought:
            if part.text is None:
                raise InterpretationError("interpretation_invalid_response")
            texts.append(part.text)
    text = "".join(texts)
    if not text or len(text.encode("utf-8")) > 200_000:
        raise InterpretationError("interpretation_invalid_response")
    return text


def _decode(text: str, input: InterpretationInput, depth: InterpretationDepth,
            language: Language) -> InterpretationContent:
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError
            result[key] = value
        return result

    try:
        json.loads(text, object_pairs_hook=unique_keys,
                   parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, RecursionError):
        raise InterpretationError("interpretation_invalid_response") from None
    try:
        content = InterpretationContent.model_validate_json(text)
    except ValidationError:
        raise InterpretationError("interpretation_schema_mismatch") from None
    return validate_content_for_input(content, input, depth=depth, language=language)


def _retry_after(error: errors.APIError, now: float) -> float | None:
    response = error.response
    value = response.headers.get("Retry-After") if response is not None else None
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


class GeminiInterpretationProvider:
    def __init__(self, config: GeminiConfig, *, client_factory: Callable = _client,
                 sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
                 clock: Callable[[], float] = time.monotonic,
                 wall_clock: Callable[[], float] = time.time):
        # Revalidate even model_construct/model_copy bypasses; key excluded from dump by design.
        try:
            self._config = GeminiConfig(model=config.model, api_key=config.api_key,
                                        timeout_seconds=config.timeout_seconds, max_retries=config.max_retries)
            if not self._config.api_key.get_secret_value().strip():
                raise ValueError
        except (ValidationError, ValueError, AttributeError, TypeError):
            raise InterpretationError("interpretation_configuration_error") from None
        self._client_factory, self._sleep, self._clock = client_factory, sleep, clock
        self._wall_clock = wall_clock

    async def interpret(self, input: InterpretationInput, *, depth: InterpretationDepth,
                        language: Language) -> InterpretationContent:
        input = admit_input(input, depth, language)
        try:
            async with asyncio.timeout(self._config.timeout_seconds):
                # Scoped lifecycle, not a mutable singleton. Close both transports on all exits.
                client = self._client_factory(self._config)
                try:
                    async with client.aio as async_client:
                        return await self._attempts(async_client, input, depth, language)
                finally:
                    client.close()
        except InterpretationError as error:
            raise InterpretationError(error.code) from None
        except (TimeoutError, httpx.TimeoutException):
            raise InterpretationError("interpretation_timeout") from None
        except Exception:
            raise InterpretationError("interpretation_unavailable") from None

    async def _attempts(self, client, input, depth, language):
        deadline = self._clock() + self._config.timeout_seconds
        repair = False
        data = input_data(input)
        for attempt in range(1 + self._config.max_retries):
            is_repair_request = repair
            remaining = deadline - self._clock()
            if remaining <= 0:
                raise InterpretationError("interpretation_timeout")
            retryable = False
            delay = min(2 ** attempt, 5)
            try:
                response = await client.models.generate_content(
                    model=self._config.model,
                    contents=types.Content(role="user", parts=[types.Part.from_text(text=data)]),
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction(depth, repair=repair),
                        response_mime_type="application/json", response_json_schema=provider_schema(),
                        candidate_count=1, max_output_tokens=TOKEN_CAPS[depth],
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                        http_options=types.HttpOptions(timeout=max(1, int(remaining * 1000)),
                                                       retry_options=types.HttpRetryOptions(attempts=1)),
                    ),
                )
                return _decode(_response_text(response), input, depth, language)
            except InterpretationError as error:
                code = error.code
                if code in {"interpretation_invalid_response", "interpretation_schema_mismatch"}:
                    if repair:
                        raise InterpretationError("interpretation_schema_mismatch") from None
                    repair = True
                    retryable, delay = True, 0
            except (TimeoutError, httpx.TimeoutException):
                code, retryable = "interpretation_timeout", True
            except httpx.TransportError:
                code, retryable = "interpretation_unavailable", True
            except (json.JSONDecodeError, ValidationError):
                # Invalid SDK response envelope, distinct from generated content schema failure.
                code = "interpretation_invalid_response"
            except errors.APIError as error:
                if error.code == 429:
                    code, retryable = "interpretation_rate_limited", True
                elif error.code == 408:
                    code, retryable = "interpretation_timeout", True
                elif error.code in {500, 502, 503, 504}:
                    code, retryable = "interpretation_unavailable", True
                else:
                    code = "interpretation_unavailable"
                if retryable:
                    retry_after = _retry_after(error, self._wall_clock())
                    if retry_after is not None:
                        if retry_after > 5:
                            retryable = False  # Do not retry earlier than the server permits.
                        delay = max(delay, retry_after)
            if is_repair_request or not retryable or attempt == self._config.max_retries:
                raise InterpretationError(code) from None
            if delay >= deadline - self._clock():
                raise InterpretationError(code) from None
            if delay:
                await self._sleep(delay)
        raise InterpretationError("interpretation_unavailable")  # Unreachable defensive boundary.
