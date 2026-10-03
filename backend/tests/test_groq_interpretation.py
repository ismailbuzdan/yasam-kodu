"""Offline Groq adapter tests; synthetic symbols and injected HTTP only."""
import asyncio
import json
import logging

import httpx
from pydantic import SecretStr, ValidationError
import pytest

from app.core.config import Settings
from app.schemas.interpretation import InterpretationDepth, InterpretationResult
from app.services.interpretation_models import InterpretationError
from app.services.interpretation_prompts import PROMPT_VERSION, TOKEN_CAPS
from app.services.interpretation_service import create_interpretation_service
from app.services.providers.groq_interpretation import (
    GROQ_BASE_URL, GROQ_CONFIG_VERSION, GROQ_MAX_COMPLETION_TOKENS, GROQ_REASONING_EFFORT,
    GroqConfig, GroqInterpretationProvider, provider_schema,
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
        self.calls.append((url, kwargs))
        event = self.events.pop(0)
        if isinstance(event, BaseException):
            raise event
        return event


def response(status=200, body=None, headers=None, *, raw=None):
    request = httpx.Request("POST", GROQ_BASE_URL + "/chat/completions")
    if raw is not None:
        return httpx.Response(status, content=raw, headers=headers, request=request)
    return httpx.Response(status, json=body, headers=headers, request=request)


def completion(value, *, finish="stop", reasoning="PRIVATE_REASONING"):
    return response(body={"choices": [{"finish_reason": finish, "message": {
        "role": "assistant", "content": json.dumps(value) if isinstance(value, dict) else value,
        "reasoning": reasoning}}]})


def adapter(fake, **kwargs):
    config = GroqConfig(model="openai/gpt-oss-120b", api_key=SecretStr("SYNTHETIC_GROQ_SECRET"),
                        **kwargs)
    return GroqInterpretationProvider(config, client_factory=lambda **_: fake,
                                      sleep=fake.sleep, clock=lambda: fake.now, wall_clock=lambda: 0)


def invoke(provider, input, depth=InterpretationDepth.STANDARD):
    return asyncio.run(provider.interpret(input, depth=depth, language="tr"))


@pytest.fixture
def symbolic():
    return case_input(next(case for case in CORPUS["cases"] if case["id"] == "exact_time_astrology"))


@pytest.mark.parametrize("case", CORPUS["cases"], ids=lambda item: item["id"])
def test_shared_corpus_uses_strict_native_schema_and_canonical_validation(case):
    input = case_input(case)
    depth = InterpretationDepth(case["depth"])
    fake = FakeClient([completion(output(input, depth, case["theme"]))])
    service = create_interpretation_service(Settings(
        _env_file=None, ai_provider="groq", groq_api_key="SYNTHETIC_GROQ_SECRET"))
    service._provider = adapter(fake)
    result = asyncio.run(service.interpret(input, depth=depth))
    assert InterpretationResult.model_validate_json(result.model_dump_json()) == result
    assert result.metadata.provider == "groq"
    assert result.metadata.model == "openai/gpt-oss-120b"
    assert result.metadata.prompt_version == PROMPT_VERSION
    assert result.metadata.config_version == GROQ_CONFIG_VERSION
    url, request = fake.calls[0]
    wire = request["json"]
    assert url == "https://api.groq.com/openai/v1/chat/completions"
    assert wire["model"] == "openai/gpt-oss-120b" and wire["stream"] is False
    assert wire["temperature"] == 0
    assert wire["max_completion_tokens"] == GROQ_MAX_COMPLETION_TOKENS[depth]
    assert wire["reasoning_effort"] == GROQ_REASONING_EFFORT
    assert wire["include_reasoning"] is False
    assert wire["response_format"] == {"type": "json_schema", "json_schema": {
        "name": "life_code_interpretation", "strict": True, "schema": provider_schema()}}
    assert [message["role"] for message in wire["messages"]] == ["system", "user"]
    assert "PRIVATE_REASONING" not in result.model_dump_json()


def test_groq_free_has_json_envelope_room_without_changing_canonical_or_premium_budgets():
    assert GROQ_MAX_COMPLETION_TOKENS[InterpretationDepth.FREE] == 2048
    assert TOKEN_CAPS[InterpretationDepth.FREE] == 800
    assert GROQ_MAX_COMPLETION_TOKENS[InterpretationDepth.PREMIUM] == TOKEN_CAPS[
        InterpretationDepth.PREMIUM
    ] == 6000


def test_provider_schema_is_closed_and_required_recursively():
    def inspect(node):
        if node.get("type") == "object":
            assert node["additionalProperties"] is False
            assert set(node["required"]) == set(node["properties"])
        for value in node.get("properties", {}).values():
            inspect(value)
        if "items" in node:
            inspect(node["items"])

    inspect(provider_schema())


def test_settings_read_env_and_default_model(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "SYNTHETIC_ENV_SECRET")
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    settings = Settings(_env_file=None)
    assert settings.groq_model == "openai/gpt-oss-120b"
    assert settings.groq_api_key.get_secret_value() == "SYNTHETIC_ENV_SECRET"
    assert "SYNTHETIC_ENV_SECRET" not in repr(settings)


@pytest.mark.parametrize("values", [
    {"groq_api_key": ""},
    {"groq_model": ""},
    {"groq_model": "bad model"},
])
def test_factory_fails_closed_for_missing_or_invalid_config(values):
    config = {"ai_provider": "groq", "groq_api_key": "SYNTHETIC_GROQ_SECRET", **values}
    settings = Settings(_env_file=None, **config)
    with pytest.raises(InterpretationError) as raised:
        create_interpretation_service(settings)
    assert raised.value.code == "interpretation_configuration_error"


def test_factory_selects_groq_and_existing_providers_remain_selectable():
    values = [
        ({"ai_provider": "groq", "groq_api_key": "test"}, "groq"),
        ({"ai_provider": "gemini", "gemini_api_key": "test", "gemini_model": "gemini-test"},
         "gemini"),
        ({"ai_provider": "nvidia", "nvidia_api_key": "test"}, "nvidia"),
        ({"ai_provider": "ollama"}, "ollama"),
    ]
    for config, expected in values:
        assert create_interpretation_service(Settings(_env_file=None, **config))._metadata.provider == expected


def test_authorization_endpoint_model_and_secret_are_safe(symbolic, caplog):
    caplog.set_level(logging.DEBUG)
    fake = FakeClient([completion(output(symbolic, InterpretationDepth.STANDARD))])
    invoke(adapter(fake), symbolic)
    url, request = fake.calls[0]
    assert url == GROQ_BASE_URL + "/chat/completions"
    assert request["headers"]["Authorization"] == "Bearer SYNTHETIC_GROQ_SECRET"
    assert request["json"]["model"] == "openai/gpt-oss-120b"
    assert "SYNTHETIC_GROQ_SECRET" not in caplog.text
    assert "SYNTHETIC_GROQ_SECRET" not in json.dumps(request["json"])


@pytest.mark.parametrize("status,code,calls", [
    (400, "interpretation_configuration_error", 1),
    (401, "interpretation_configuration_error", 1),
    (403, "interpretation_configuration_error", 1),
    (404, "interpretation_model_not_found", 1),
    (408, "interpretation_timeout", 3),
    (429, "interpretation_rate_limited", 3),
    (500, "interpretation_unavailable", 3),
    (502, "interpretation_unavailable", 3),
    (503, "interpretation_unavailable", 3),
    (504, "interpretation_unavailable", 3),
])
def test_http_errors_are_canonical_bounded_and_private(symbolic, status, code, calls):
    event = response(status, {"error": {"message": "PRIVATE_PROVIDER_BODY"}})
    fake = FakeClient([event for _ in range(3)])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake), symbolic)
    assert raised.value.code == code and len(fake.calls) == calls
    assert "PRIVATE_PROVIDER_BODY" not in str(raised.value)


@pytest.mark.parametrize("event,code", [
    (httpx.ConnectError("PRIVATE"), "interpretation_unavailable"),
    (httpx.ReadTimeout("PRIVATE"), "interpretation_timeout"),
])
def test_transport_and_timeout_are_bounded(symbolic, event, code):
    fake = FakeClient([event for _ in range(3)])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake), symbolic)
    assert raised.value.code == code and len(fake.calls) == 3


@pytest.mark.parametrize("event,code", [
    (completion("not-json"), "interpretation_invalid_response"),
    (completion("{}"), "interpretation_schema_mismatch"),
    (response(raw=b"not-json"), "interpretation_invalid_response"),
    (completion("", finish="stop"), "interpretation_invalid_response"),
    (completion({}, finish="length"), "interpretation_invalid_response"),
])
def test_invalid_json_schema_and_envelopes_fail_safely(symbolic, event, code):
    fake = FakeClient([event])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake, max_retries=0), symbolic)
    assert raised.value.code == code


def test_schema_failure_uses_one_existing_safe_repair(symbolic):
    fake = FakeClient([completion("{}"), completion("{}")])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake, max_retries=1), symbolic)
    assert raised.value.code == "interpretation_schema_mismatch" and len(fake.calls) == 2
    first = fake.calls[0][1]["json"]["messages"][0]["content"]
    repair = fake.calls[1][1]["json"]["messages"][0]["content"]
    assert "Previous response failed validation" not in first
    assert "Previous response failed validation" in repair
    assert "{}" not in repair


def test_input_binding_is_not_bypassed(symbolic):
    value = output(symbolic, InterpretationDepth.STANDARD)
    value["summary"]["basis"] = ["numerology.life_path.value"]
    fake = FakeClient([completion(value)])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake, max_retries=0), symbolic)
    assert raised.value.code == "interpretation_invalid_response"


def test_free_depth_contract_is_not_bypassed(symbolic):
    value = output(symbolic, InterpretationDepth.FREE)
    value["cross_system"] = []
    fake = FakeClient([completion(value)])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake, max_retries=0), symbolic, InterpretationDepth.FREE)
    assert raised.value.code == "interpretation_schema_mismatch"


def test_request_projection_excludes_private_fields(symbolic):
    fake = FakeClient([completion(output(symbolic, InterpretationDepth.STANDARD))])
    invoke(adapter(fake), symbolic)
    user_data = fake.calls[0][1]["json"]["messages"][1]["content"]
    for forbidden in ("name", "birth_date", "birth_utc", "latitude", "longitude", "timezone",
                      "diagnostics", "metadata", "request_id", "reasoning"):
        assert forbidden not in user_data


def test_retry_after_is_honored_within_bound(symbolic):
    fake = FakeClient([
        response(429, {}, {"Retry-After": "3"}),
        completion(output(symbolic, InterpretationDepth.STANDARD)),
    ])
    invoke(adapter(fake), symbolic)
    assert len(fake.calls) == 2 and fake.delays == [3]


@pytest.mark.parametrize("field,value", [
    ("model", "bad model"), ("timeout_seconds", 0), ("max_retries", 3),
])
def test_config_validation(field, value):
    values = {"model": "openai/gpt-oss-120b", "api_key": SecretStr("test"), field: value}
    with pytest.raises(ValidationError):
        GroqConfig(**values)


def test_duplicate_keys_are_rejected(symbolic):
    content = json.dumps(output(symbolic, InterpretationDepth.STANDARD))
    duplicated = content.replace('{"language": "tr",', '{"language": "tr", "language": "tr",', 1)
    fake = FakeClient([completion(duplicated)])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake, max_retries=0), symbolic)
    assert raised.value.code == "interpretation_invalid_response"


def test_refusal_does_not_retry_or_expose_text(symbolic):
    fake = FakeClient([response(body={"choices": [{"finish_reason": "stop", "message": {
        "content": "PRIVATE", "refusal": "PRIVATE_REFUSAL"}}]})])
    with pytest.raises(InterpretationError) as raised:
        invoke(adapter(fake), symbolic)
    assert raised.value.code == "interpretation_refusal" and len(fake.calls) == 1
    assert "PRIVATE" not in str(raised.value)
