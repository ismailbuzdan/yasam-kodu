"""Offline NVIDIA NIM tests using synthetic input and an injected httpx-compatible client."""
import asyncio
import json

import httpx
from pydantic import SecretStr, ValidationError
import pytest

from app.core.config import Settings
from app.schemas.interpretation import InterpretationDepth, InterpretationMetadata
from app.services.interpretation_models import InterpretationError
from app.services.interpretation_prompts import PROMPT_VERSION, TOKEN_CAPS
from app.services.interpretation_service import InterpretationService, create_interpretation_service
from app.services.providers.nvidia_interpretation import NvidiaConfig, NvidiaInterpretationProvider
from tests.test_gemini_interpretation import CORPUS, case_input, output


class FakeClient:
    def __init__(self, events):
        self.events, self.calls, self.delays, self.now = list(events), [], [], 0.0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def sleep(self, seconds):
        self.delays.append(seconds)
        self.now += seconds

    async def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        event = self.events.pop(0)
        if isinstance(event, BaseException):
            raise event
        return event


def response(status=200, body=None, headers=None):
    request = httpx.Request("POST", "https://integrate.api.nvidia.com/v1/chat/completions")
    return httpx.Response(status, json=body, headers=headers, request=request)


def completion(value, *, finish="stop", reasoning="PRIVATE_REASONING"):
    return response(body={"choices": [{"finish_reason": finish,
        "message": {"content": json.dumps(value) if isinstance(value, dict) else value,
                    "reasoning_content": reasoning}}]})


def adapter(fake, **kwargs):
    config = NvidiaConfig(model="openai/gpt-oss-20b", api_key=SecretStr("SYNTHETIC_NVIDIA_SECRET"),
                          base_url="https://integrate.api.nvidia.com/v1", **kwargs)
    return NvidiaInterpretationProvider(config, client_factory=lambda **_: fake, sleep=fake.sleep,
                                        clock=lambda: fake.now, wall_clock=lambda: 0)


def invoke(provider, input, depth=InterpretationDepth.STANDARD):
    return asyncio.run(provider.interpret(input, depth=depth, language="tr"))


@pytest.fixture
def symbolic():
    return case_input(next(c for c in CORPUS["cases"] if c["id"] == "exact_time_astrology"))


@pytest.mark.parametrize("case", CORPUS["cases"], ids=lambda item: item["id"])
def test_synthetic_corpus_uses_shared_prompt_and_strict_contract(case):
    input = case_input(case)
    depth = InterpretationDepth(case["depth"])
    fake = FakeClient([completion(output(input, depth, case["theme"]))])
    metadata = InterpretationMetadata(provider="nvidia", model="openai/gpt-oss-20b",
                                      prompt_version=PROMPT_VERSION, config_version="nvidia-nim-chat-json-v1")
    result = asyncio.run(InterpretationService(adapter(fake), metadata).interpret(input, depth=depth))
    assert result.metadata == metadata
    url, request = fake.calls[0]
    assert url == "https://integrate.api.nvidia.com/v1/chat/completions"
    assert request["json"]["model"] == "openai/gpt-oss-20b"
    assert request["json"]["stream"] is False
    assert request["json"]["max_tokens"] == TOKEN_CAPS[depth]
    assert [m["role"] for m in request["json"]["messages"]] == ["system", "user"]
    assert "interpretation_input" in request["json"]["messages"][1]["content"]
    assert "PRIVATE_REASONING" not in result.model_dump_json()
    assert "response_format" not in request["json"] and "tools" not in request["json"]


@pytest.mark.parametrize("status,code,calls", [(401, "interpretation_configuration_error", 1),
    (403, "interpretation_configuration_error", 1), (408, "interpretation_timeout", 3),
    (429, "interpretation_rate_limited", 3), (500, "interpretation_unavailable", 3),
    (502, "interpretation_unavailable", 3), (503, "interpretation_unavailable", 3),
    (504, "interpretation_unavailable", 3)])
def test_http_error_mapping_and_bounds(symbolic, status, code, calls):
    fake = FakeClient([response(status, {"error": {"message": "PRIVATE_PROVIDER_BODY"}}) for _ in range(3)])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake), symbolic)
    assert raised.value.code == code and len(fake.calls) == calls
    assert "PRIVATE_PROVIDER_BODY" not in str(raised.value)


@pytest.mark.parametrize("raw", ["not-json", "{}"])
def test_malformed_and_schema_mismatch_repair_once(symbolic, raw):
    fake = FakeClient([completion(raw), completion(raw)])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake, max_retries=1), symbolic)
    assert raised.value.code == "interpretation_schema_mismatch" and len(fake.calls) == 2
    assert "Previous response failed validation" in fake.calls[1][1]["json"]["messages"][0]["content"]
    assert raw not in fake.calls[1][1]["json"]["messages"][0]["content"]


def test_transport_retry_timeout_and_retry_after(symbolic):
    fake = FakeClient([httpx.ConnectError("PRIVATE"), completion(output(symbolic, InterpretationDepth.STANDARD))])
    invoke(adapter(fake), symbolic)
    assert len(fake.calls) == 2 and fake.delays == [1]
    rate = FakeClient([response(429, {}, {"Retry-After": "3"}), completion(output(symbolic, InterpretationDepth.STANDARD))])
    invoke(adapter(rate), symbolic)
    assert len(rate.calls) == 2 and rate.delays == [3]


@pytest.mark.parametrize("finish", ["length", "tool_calls", None])
def test_non_final_or_missing_content_rejected(symbolic, finish):
    fake = FakeClient([completion(output(symbolic, InterpretationDepth.STANDARD), finish=finish)])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake, max_retries=0), symbolic)
    assert raised.value.code == "interpretation_invalid_response"


@pytest.mark.parametrize("body", [
    {"choices": [{"finish_reason": "content_filter", "message": {"content": "PRIVATE"}}]},
    {"choices": [{"finish_reason": "stop", "message": {"content": "PRIVATE", "refusal": "PRIVATE"}}]},
])
def test_identifiable_refusal_is_mapped_without_exposing_provider_text(symbolic, body):
    fake = FakeClient([response(body=body)])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake), symbolic)
    assert raised.value.code == "interpretation_refusal" and len(fake.calls) == 1
    assert "PRIVATE" not in str(raised.value)


@pytest.mark.parametrize("kwargs", [{"nvidia_api_key": ""}, {"nvidia_model": ""},
    {"nvidia_base_url": "http://not-secure.example/v1"}, {"ai_provider": "unsupported"}])
def test_factory_fails_closed(kwargs):
    values = {"ai_provider": "nvidia", "nvidia_api_key": "SYNTHETIC_NVIDIA_SECRET",
              "nvidia_model": "openai/gpt-oss-20b", **kwargs}
    settings = Settings(_env_file=None, **values)
    with pytest.raises(InterpretationError) as raised:
        create_interpretation_service(settings)
    assert raised.value.code == "interpretation_configuration_error"


def test_factory_selects_nvidia_and_keeps_gemini_possible():
    nvidia = Settings(_env_file=None, ai_provider="nvidia", nvidia_api_key="SYNTHETIC_NVIDIA_SECRET",
                      nvidia_model="openai/gpt-oss-20b")
    assert isinstance(create_interpretation_service(nvidia), InterpretationService)
    gemini = Settings(_env_file=None, ai_provider="gemini", gemini_api_key="SYNTHETIC_GEMINI_SECRET",
                      gemini_model="gemini-3.8-flash")
    assert isinstance(create_interpretation_service(gemini), InterpretationService)


def test_nvidia_request_contains_no_private_life_code_fields(symbolic):
    fake = FakeClient([completion(output(symbolic, InterpretationDepth.STANDARD))])
    invoke(adapter(fake), symbolic)
    wire = fake.calls[0][1]["json"]
    # The immutable system policy may mention forbidden field names as prohibitions; only the
    # structured user data is the privacy projection crossing the provider boundary.
    serialized = wire["messages"][1]["content"]
    for forbidden in ("name", "birth_date", "birth_utc", "latitude", "longitude", "timezone",
                      "diagnostics", "metadata", "request_id", "reasoning_content"):
        assert forbidden not in serialized
    assert "SYNTHETIC_NVIDIA_SECRET" not in json.dumps(wire)


@pytest.mark.parametrize("field,value", [("model", "bad model"), ("base_url", "not-url"),
    ("max_retries", 3), ("timeout_seconds", 0)])
def test_config_validation(field, value):
    values = {"model": "openai/gpt-oss-20b", "api_key": SecretStr("test"),
              "base_url": "https://integrate.api.nvidia.com/v1", field: value}
    with pytest.raises(ValidationError):
        NvidiaConfig(**values)
