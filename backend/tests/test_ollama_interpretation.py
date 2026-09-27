"""Offline Ollama adapter tests; synthetic symbols and injected HTTP only."""
import asyncio
import json

import httpx
from pydantic import ValidationError
import pytest

from app.core.config import Settings
from app.schemas.interpretation import InterpretationContent, InterpretationDepth, InterpretationResult
from app.services.interpretation_models import InterpretationError
from app.services.interpretation_prompts import PROMPT_VERSION, TOKEN_CAPS
from app.services.interpretation_service import create_interpretation_service
from app.services.providers.ollama_interpretation import (
    JSON_ENVELOPE_TOKEN_ALLOWANCE, OLLAMA_CONFIG_VERSION, OllamaConfig, OllamaInterpretationProvider,
)
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
        self.calls.append(("POST", url, kwargs))
        event = self.events.pop(0)
        if isinstance(event, BaseException):
            raise event
        return event

    async def get(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs))
        event = self.events.pop(0)
        if isinstance(event, BaseException):
            raise event
        return event


def response(status=200, body=None, *, raw=None):
    request = httpx.Request("POST", "http://localhost:11434/api/chat")
    if raw is not None:
        return httpx.Response(status, content=raw, request=request)
    return httpx.Response(status, json=body, request=request)


def completion(value, *, done=True, reason="stop", thinking="PRIVATE_REASONING"):
    return response(body={"model": "qwen3:4b", "message": {
        "role": "assistant", "content": json.dumps(value) if isinstance(value, dict) else value,
        "thinking": thinking}, "done": done, "done_reason": reason})


def adapter(fake, **kwargs):
    config = OllamaConfig(model="qwen3:4b", base_url="http://localhost:11434", **kwargs)
    return OllamaInterpretationProvider(config, client_factory=lambda **_: fake,
                                        sleep=fake.sleep, clock=lambda: fake.now)


def invoke(provider, input, depth=InterpretationDepth.STANDARD):
    return asyncio.run(provider.interpret(input, depth=depth, language="tr"))


@pytest.fixture
def symbolic():
    return case_input(next(case for case in CORPUS["cases"] if case["id"] == "exact_time_astrology"))


@pytest.mark.parametrize("case", CORPUS["cases"], ids=lambda item: item["id"])
def test_shared_synthetic_corpus_and_request_contract(case):
    input = case_input(case)
    depth = InterpretationDepth(case["depth"])
    fake = FakeClient([completion(output(input, depth, case["theme"]))])
    service = create_interpretation_service(Settings(
        _env_file=None, ai_provider="ollama", ollama_model="qwen3:4b",
        ollama_base_url="http://localhost:11434"))
    service._provider = adapter(fake)
    result = asyncio.run(service.interpret(input, depth=depth))
    assert InterpretationResult.model_validate_json(result.model_dump_json()) == result
    assert result.metadata.provider == "ollama" and result.metadata.model == "qwen3:4b"
    assert result.metadata.prompt_version == PROMPT_VERSION
    assert result.metadata.config_version == OLLAMA_CONFIG_VERSION
    _, url, request = fake.calls[0]
    wire = request["json"]
    assert url == "http://localhost:11434/api/chat"
    assert wire["model"] == "qwen3:4b" and wire["stream"] is False and wire["think"] is False
    assert wire["options"] == {"temperature": 0,
                               "num_predict": TOKEN_CAPS[depth] + JSON_ENVELOPE_TOKEN_ALLOWANCE}
    assert wire["format"] == InterpretationContent.model_json_schema()
    assert [message["role"] for message in wire["messages"]] == ["system", "user"]
    assert "PRIVATE_REASONING" not in result.model_dump_json()


@pytest.mark.parametrize("event,code,calls", [
    (httpx.ConnectError("PRIVATE"), "interpretation_unavailable", 3),
    (httpx.ReadTimeout("PRIVATE"), "interpretation_timeout", 3),
    (response(404, {"error": "model not found PRIVATE"}), "interpretation_model_not_found", 1),
    (response(429, {"error": "busy PRIVATE"}), "interpretation_rate_limited", 3),
    (response(500, {"error": "failed PRIVATE"}), "interpretation_unavailable", 3),
])
def test_transport_and_http_failures_are_static_bounded(symbolic, event, code, calls):
    fake = FakeClient([event for _ in range(3)])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake), symbolic)
    assert raised.value.code == code and len(fake.calls) == calls
    assert "PRIVATE" not in str(raised.value)


@pytest.mark.parametrize("event", [
    completion(""), completion("{}"), response(raw="not-json"),
    completion("{}", done=False), completion("{}", reason="length"),
])
def test_empty_invalid_incomplete_response_is_controlled(symbolic, event):
    fake = FakeClient([event])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake, max_retries=0), symbolic)
    assert raised.value.code in {"interpretation_invalid_response", "interpretation_schema_mismatch"}


def test_invalid_schema_gets_one_safe_replacement(symbolic):
    fake = FakeClient([completion("{}"), completion("{}")])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake, max_retries=1), symbolic)
    assert raised.value.code == "interpretation_schema_mismatch" and len(fake.calls) == 2
    assert "Previous response failed validation" in fake.calls[1][2]["json"]["messages"][0]["content"]


def test_request_projection_excludes_private_fields(symbolic):
    fake = FakeClient([completion(output(symbolic, InterpretationDepth.STANDARD))])
    invoke(adapter(fake), symbolic)
    user_data = fake.calls[0][2]["json"]["messages"][1]["content"]
    for forbidden in ("name", "birth_date", "birth_utc", "latitude", "longitude", "timezone",
                      "diagnostics", "metadata", "request_id", "thinking"):
        assert forbidden not in user_data


@pytest.mark.parametrize("body,expected", [
    ({"models": [{"name": "qwen3:4b"}]}, (True, True)),
    ({"models": [{"name": "other:latest"}]}, (True, False)),
    ({"unexpected": []}, (True, None)),
])
def test_explicit_health_distinguishes_model_availability(body, expected):
    fake = FakeClient([response(body=body)])
    result = asyncio.run(adapter(fake).check_availability())
    assert (result.reachable, result.model_available) == expected
    assert fake.calls[0][0:2] == ("GET", "http://localhost:11434/api/tags")


def test_health_reports_unreachable_without_raising():
    fake = FakeClient([httpx.ConnectError("PRIVATE")])
    result = asyncio.run(adapter(fake).check_availability())
    assert result.reachable is False and result.model_available is None


@pytest.mark.parametrize("field,value", [
    ("model", "bad model"), ("base_url", "not-url"),
    ("base_url", "http://localhost:11434/api"), ("timeout_seconds", 0), ("max_retries", 3),
])
def test_config_validation(field, value):
    values = {"model": "qwen3:4b", "base_url": "http://localhost:11434", field: value}
    with pytest.raises(ValidationError):
        OllamaConfig(**values)


def test_factory_supports_all_three_providers_and_no_fallback():
    ollama = create_interpretation_service(Settings(_env_file=None, ai_provider="ollama"))
    assert ollama._metadata.provider == "ollama" and ollama._metadata.model == "qwen3:4b"
    for values, provider in [
        ({"ai_provider": "gemini", "gemini_api_key": "test", "gemini_model": "gemini-test"}, "gemini"),
        ({"ai_provider": "nvidia", "nvidia_api_key": "test"}, "nvidia"),
    ]:
        assert create_interpretation_service(Settings(_env_file=None, **values))._metadata.provider == provider
    with pytest.raises(InterpretationError) as raised:
        create_interpretation_service(Settings(_env_file=None, ai_provider="unknown"))
    assert raised.value.code == "interpretation_configuration_error"
