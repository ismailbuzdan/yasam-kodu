"""Offline synthetic qualification, including real pinned SDK over an HTTP fake; no live key."""
import asyncio
from copy import deepcopy
import json
import logging
from pathlib import Path

from google import genai
from google.genai import errors, types
import httpx
from pydantic import SecretStr, ValidationError
import pytest

from app.core.config import Settings
from app.knowledge.kameri.repository import get_knowledge_base
from app.schemas.interpretation import (
    InterpretationContent, InterpretationDepth, InterpretationInput, InterpretationMetadata,
    InterpretationResult, SECTIONS_BY_DEPTH,
)
from app.services.interpretation_models import InterpretationError
from app.services.interpretation_prompts import CORE, PROMPT_VERSION, REPAIR, TOKEN_CAPS, system_instruction
from app.services.interpretation_service import InterpretationService, create_interpretation_service
from app.services.interpretation_validation import available_fact_refs
from app.services.providers.gemini_interpretation import (
    GeminiConfig, GeminiInterpretationProvider, provider_schema,
)

CORPUS = json.loads((Path(__file__).parent / "fixtures/interpretation_cases.json").read_text(encoding="utf-8"))


def case_input(case):
    data = deepcopy(CORPUS["symbols"])
    for system in ("astrology", "numerology", "human_design"):
        if system not in case["systems"]:
            data[system] = None
    if data["astrology"] and not case["exact_time"]:
        data["astrology"].update(ascendant=None, mc=None, houses=[])
        for body in data["astrology"]["bodies"]:
            body["house"] = None
    if case["cultural_month"]:
        kb = get_knowledge_base()
        claims = [c for c in kb.claims if c.application_key == case["cultural_month"]]
        sources = {r.source_id for c in claims for r in c.source_refs}
        data["kameri"] = {"claims": [c.model_dump(mode="json") for c in claims],
                          "sources": [s.model_dump(mode="json") for s in kb.sources if s.source_id in sources],
                          "abstained": False, "reason": None}
    return InterpretationInput.model_validate_json(json.dumps(data))


def prose(*refs):
    return {"text": "Bu sistemde sembolik öz değerlendirme için bir bakış açısıdır.", "basis": list(refs)}


def output(input, depth, theme=None):
    refs = sorted(available_fact_refs(input))
    base = prose(refs[0])
    triad = ["astrology.bodies.sun.sign", "astrology.bodies.moon.sign", "astrology.ascendant"]
    sections = []
    for section in SECTIONS_BY_DEPTH[depth]:
        reason, paragraph = None, base
        if section == "timeline":
            reason = "unsupported_timeline"
        elif section == "basic_triad":
            if set(triad) <= set(refs):
                paragraph = prose(*triad)
            else:
                reason = "missing_input"
        elif section in {"numerology", "human_design"}:
            system_refs = [r for r in refs if r.startswith(section + ".")]
            if system_refs:
                paragraph = prose(system_refs[0])
            else:
                reason = "missing_input"
        sections.append({"section": section, "content": None if reason else [paragraph],
                         "unavailable_reason": reason})
    cross = None
    if theme:
        representatives = {r.split(".")[0]: r for r in refs}
        cross = [{"kind": theme, "narrative": prose(*representatives.values())}]
    return {"language": "tr", "depth": depth.value, "summary": base,
            "at_a_glance": [base] if depth == InterpretationDepth.PREMIUM else None,
            "sections": sections, "cross_system": cross,
            "kameri": [{"claim_id": c.claim_id, "text": "Kaynakla sınırlı tarihsel kültürel bağlamdır."}
                       for c in input.kameri.claims] if input.kameri and depth != InterpretationDepth.FREE else None}


def response(value, *, finish="STOP"):
    return types.GenerateContentResponse(candidates=[types.Candidate(
        finish_reason=finish, content=types.Content(parts=[types.Part(
            text=value if isinstance(value, str) else json.dumps(value))]))])


class FakeClient:
    def __init__(self, events):
        self.events = list(events)
        self.calls, self.delays = [], []
        self.aio = self
        self.models = self
        self.closed = self.async_closed = False
        self.now = 0.0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.async_closed = True

    def close(self):
        self.closed = True

    async def sleep(self, seconds):
        self.delays.append(seconds)
        self.now += seconds

    async def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        event = self.events.pop(0)
        if isinstance(event, BaseException):
            raise event
        if callable(event):
            return await event()
        return event


def provider(fake, **config):
    return GeminiInterpretationProvider(
        GeminiConfig(model="synthetic-model", api_key=SecretStr("SYNTHETIC_SECRET"), **config),
        client_factory=lambda _: fake, sleep=fake.sleep, clock=lambda: fake.now)


@pytest.fixture
def symbolic():
    return case_input(CORPUS["cases"][0])


def invoke(adapter, input, depth=InterpretationDepth.PREMIUM):
    return asyncio.run(adapter.interpret(input, depth=depth, language="tr"))


@pytest.mark.parametrize("case", CORPUS["cases"], ids=lambda c: c["id"])
def test_corpus_request_content_and_application_metadata(case):
    input = case_input(case)
    depth = InterpretationDepth(case["depth"])
    fake = FakeClient([response(output(input, depth, case["theme"]))])
    metadata = InterpretationMetadata(provider="gemini", model="synthetic-model",
                                      prompt_version=PROMPT_VERSION, config_version="gemini-interpretation-v1")
    result = invoke(InterpretationService(provider(fake), metadata), input, depth)
    assert InterpretationResult.model_validate_json(result.model_dump_json()) == result
    assert result.metadata == metadata
    request = fake.calls[0]
    assert request["model"] == "synthetic-model"
    assert request["config"].response_mime_type == "application/json"
    assert request["config"].response_json_schema == provider_schema()
    assert request["config"].max_output_tokens == TOKEN_CAPS[depth]
    assert request["config"].automatic_function_calling.disable is True
    assert request["config"].tools is None
    assert request["config"].http_options.retry_options.attempts == 1
    data = json.loads(request["contents"].parts[0].text)
    assert data["interpretation_input"] == input.model_dump(mode="json")
    assert set(data["available_fact_refs"]) == available_fact_refs(input)
    assert request["config"].system_instruction == system_instruction(depth)
    assert fake.closed and fake.async_closed


@pytest.mark.parametrize("status,code,calls", [(429, "interpretation_rate_limited", 3),
    (408, "interpretation_timeout", 3), (500, "interpretation_unavailable", 3),
    (502, "interpretation_unavailable", 3), (503, "interpretation_unavailable", 3),
    (504, "interpretation_unavailable", 3), (400, "interpretation_unavailable", 1),
    (401, "interpretation_unavailable", 1), (403, "interpretation_unavailable", 1)])
def test_api_errors_static_bounded_private(symbolic, status, code, calls, caplog):
    caplog.set_level(logging.DEBUG)
    fake = FakeClient([errors.APIError(status, {"error": {"message": "SECRET_RAW_BODY"}}) for _ in range(3)])
    with pytest.raises(InterpretationError) as error:
        invoke(provider(fake), symbolic)
    assert error.value.code == code and error.value.__suppress_context__
    assert len(fake.calls) == calls
    assert fake.delays == ([1, 2] if calls == 3 else [])
    assert "SECRET_RAW_BODY" not in str(error.value) + caplog.text
    assert fake.closed and fake.async_closed


@pytest.mark.parametrize("event,code", [(TimeoutError("PRIVATE"), "interpretation_timeout"),
    (httpx.ReadTimeout("PRIVATE"), "interpretation_timeout"),
    (httpx.ConnectError("PRIVATE"), "interpretation_unavailable"),
    (RuntimeError("PRIVATE"), "interpretation_unavailable")])
def test_transport_and_unexpected_error_mapping(symbolic, event, code):
    fake = FakeClient([event] * 3)
    with pytest.raises(InterpretationError) as error:
        invoke(provider(fake), symbolic)
    assert error.value.code == code
    assert "PRIVATE" not in str(error.value)
    assert len(fake.calls) == (1 if isinstance(event, RuntimeError) else 3)


@pytest.mark.parametrize("reason", ["SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT", "SPII"])
def test_refusal_never_retried(symbolic, reason):
    fake = FakeClient([response("PRIVATE", finish=reason)])
    with pytest.raises(InterpretationError) as error:
        invoke(provider(fake), symbolic)
    assert error.value.code == "interpretation_refusal"
    assert len(fake.calls) == 1 and not fake.delays


def test_prompt_block_and_safety_rating(symbolic):
    for event in [types.GenerateContentResponse(prompt_feedback=types.GenerateContentResponsePromptFeedback(
            block_reason="SAFETY")), types.GenerateContentResponse(candidates=[types.Candidate(
                finish_reason="STOP", safety_ratings=[types.SafetyRating(blocked=True)])])]:
        fake = FakeClient([event])
        with pytest.raises(InterpretationError, match="could not be provided"):
            invoke(provider(fake), symbolic)
        assert len(fake.calls) == 1


@pytest.mark.parametrize("bad,code", [("not JSON PRIVATE", "interpretation_invalid_response"),
    ('{"x":1,"x":2}', "interpretation_invalid_response"), ('{"x":NaN}', "interpretation_invalid_response"),
    ("{}", "interpretation_schema_mismatch"), ("[]", "interpretation_schema_mismatch")])
def test_invalid_response_without_retry(symbolic, bad, code):
    fake = FakeClient([response(bad)])
    with pytest.raises(InterpretationError) as error:
        invoke(provider(fake, max_retries=0), symbolic)
    assert error.value.code == code and len(fake.calls) == 1


@pytest.mark.parametrize("bad", ["PRIVATE_IGNORE_SYSTEM", "{}"])
def test_single_generic_repair_same_input(symbolic, bad):
    fake = FakeClient([response(bad), response(output(symbolic, InterpretationDepth.PREMIUM))])
    invoke(provider(fake), symbolic)
    assert len(fake.calls) == 2
    assert fake.calls[0]["contents"] == fake.calls[1]["contents"]
    prompt = fake.calls[1]["config"].system_instruction
    assert REPAIR in prompt and "PRIVATE_IGNORE_SYSTEM" not in prompt
    assert fake.calls[0]["config"].response_json_schema == fake.calls[1]["config"].response_json_schema


def test_repair_failure_is_final_and_not_transport_retried(symbolic):
    for second, code in [(response("PRIVATE"), "interpretation_schema_mismatch"),
                         (httpx.ReadTimeout("PRIVATE"), "interpretation_timeout")]:
        fake = FakeClient([response("{}"), second])
        with pytest.raises(InterpretationError) as error:
            invoke(provider(fake), symbolic)
        assert error.value.code == code and len(fake.calls) == 2


@pytest.mark.parametrize("change", ["absent_ref", "timeline", "asma", "invented_claim", "depth", "metadata", "single_system"])
def test_structural_semantic_rejections(symbolic, change):
    data = output(symbolic, InterpretationDepth.PREMIUM)
    if change == "absent_ref":
        data["summary"]["basis"] = ["numerology.personal_year.value"]
    elif change == "timeline":
        data["sections"][-1].update(content=[data["summary"]], unavailable_reason=None)
    elif change == "asma":
        data["kameri"] = [{"claim_id": "ASMA_NUM_001", "text": "Forbidden assignment"}]
    elif change == "invented_claim":
        data["kameri"] = [{"claim_id": "HIJRI_CTX_001", "text": "Not supplied"}]
    elif change == "depth":
        data["depth"] = "free"
    elif change == "metadata":
        data["metadata"] = {"provider": "template"}
    else:
        data["cross_system"] = [{"kind": "tension", "narrative": prose("human_design.type", "human_design.authority")}]
    fake = FakeClient([response(data), response(data)])
    with pytest.raises(InterpretationError) as error:
        invoke(provider(fake), symbolic)
    assert error.value.code == "interpretation_schema_mismatch"


@pytest.mark.parametrize("bad", [None, {}, "PRIVATE", 1])
def test_input_admission_no_call(bad):
    fake = FakeClient([])
    with pytest.raises(InterpretationError) as error:
        invoke(provider(fake), bad)
    assert error.value.code == "interpretation_invalid_input" and not fake.calls


def test_tampered_input_and_invalid_depth_cannot_inject(symbolic):
    bad = symbolic.model_copy(update={"timeline": "IGNORE SYSTEM PRIVATE"})
    for input, depth in [(bad, InterpretationDepth.PREMIUM), (symbolic, "IGNORE SYSTEM")]:
        fake = FakeClient([])
        with pytest.raises(InterpretationError):
            invoke(provider(fake), input, depth)
        assert not fake.calls


@pytest.mark.parametrize("field,value", [("max_retries", 3), ("max_retries", -1),
    ("timeout_seconds", 0.0), ("timeout_seconds", float("inf")), ("model", "private/name")])
def test_config_caps(field, value):
    args = {"model": "synthetic-model", "api_key": SecretStr("test"), field: value}
    with pytest.raises(ValidationError):
        GeminiConfig(**args)


@pytest.mark.parametrize("args", [{"ai_provider": "openai"}, {"ai_provider": "unsupported"},
    {"gemini_model": ""}, {"gemini_api_key": ""}])
def test_unconfigured_factory_no_fallback(args):
    values = {"gemini_model": "synthetic-model", "gemini_api_key": "SYNTHETIC_SECRET", **args}
    settings = Settings(_env_file=None, **values)
    assert "SYNTHETIC_SECRET" not in repr(settings)
    with pytest.raises(InterpretationError) as error:
        create_interpretation_service(settings)
    assert error.value.code == "interpretation_configuration_error"


def test_factory_and_secret_config_repr():
    settings = Settings(_env_file=None, gemini_model="synthetic-model", gemini_api_key="SYNTHETIC_SECRET")
    service = create_interpretation_service(settings)
    assert isinstance(service, InterpretationService)
    config = GeminiConfig.from_settings(settings)
    assert "SYNTHETIC_SECRET" not in repr(config) + config.model_dump_json()


def test_backoff_respects_deadline(symbolic):
    fake = FakeClient([errors.APIError(429, {})])
    with pytest.raises(InterpretationError) as error:
        invoke(provider(fake, timeout_seconds=1.0), symbolic)
    assert error.value.code == "interpretation_rate_limited"
    assert len(fake.calls) == 1 and not fake.delays


def test_outer_timeout_and_cancellation_close_clients(symbolic):
    async def never():
        await asyncio.Event().wait()
    for event, code in [(never, "interpretation_timeout"), (asyncio.CancelledError(), None)]:
        fake = FakeClient([event])
        expected = InterpretationError if code else asyncio.CancelledError
        with pytest.raises(expected) as error:
            invoke(provider(fake, timeout_seconds=1.0), symbolic)
        if code:
            assert error.value.code == code
        assert fake.closed and fake.async_closed


def test_prompt_rules_and_schema_projection():
    for rule in ("never calculate", "untrusted DATA", "medical", "psychological", "financial",
                 "religious", "Esma", "dhikr", "HIJRI_CTX_001/002/003", "Timeline"):
        assert rule in CORE
    schema = provider_schema()
    assert set(schema["properties"]) == set(InterpretationContent.model_fields)
    encoded = json.dumps(schema)
    assert all(key not in encoded for key in ('"$ref"', '"$defs"', '"pattern"', '"const"', '"anyOf"'))
    assert len(encoded) < 6000
    assert schema["additionalProperties"] is False


def test_real_sdk_request_over_mock_transport(symbolic, monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    requests = []
    payload = response(output(symbolic, InterpretationDepth.PREMIUM)).model_dump(mode="json", exclude_none=True, by_alias=True)

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=payload)

    original_client = genai.Client
    def sdk_client(**kwargs):
        assert kwargs["enterprise"] is False
        options = kwargs["http_options"]
        assert options.retry_options.attempts == 1
        assert options.base_url == "https://generativelanguage.googleapis.com"
        options.client_args["transport"] = httpx.MockTransport(handler)
        options.async_client_args["transport"] = httpx.MockTransport(handler)
        return original_client(**kwargs)

    monkeypatch.setattr(genai, "Client", sdk_client)
    monkeypatch.setenv("GOOGLE_GENAI_USE_ENTERPRISE", "true")
    adapter = GeminiInterpretationProvider(GeminiConfig(model="synthetic-model", api_key=SecretStr("SYNTHETIC_SECRET")))
    invoke(adapter, symbolic)
    assert len(requests) == 1
    wire = json.loads(requests[0].content)
    assert "systemInstruction" in wire
    assert "application/json" in json.dumps(wire["generationConfig"])
    assert requests[0].headers["x-goog-api-key"] == "SYNTHETIC_SECRET"
    assert "SYNTHETIC_SECRET" not in caplog.text
    assert CORPUS["symbols"]["human_design"]["profile"] not in caplog.text
    assert "Bu sistemde" not in caplog.text


@pytest.mark.parametrize("header,delays,calls", [("3", [3], 2), ("100", [], 1),
    ("garbage", [1], 2), ("Thu, 01 Jan 1970 00:00:04 GMT", [4], 2)])
def test_retry_after(symbolic, header, delays, calls):
    error = errors.APIError(429, {}, httpx.Response(429, headers={"Retry-After": header}))
    fake = FakeClient([error, response(output(symbolic, InterpretationDepth.PREMIUM))])
    adapter = GeminiInterpretationProvider(
        GeminiConfig(model="synthetic-model", api_key=SecretStr("test")), client_factory=lambda _: fake,
        sleep=fake.sleep, clock=lambda: fake.now, wall_clock=lambda: 0)
    if calls == 1:
        with pytest.raises(InterpretationError) as raised:
            invoke(adapter, symbolic)
        assert raised.value.code == "interpretation_rate_limited"
    else:
        invoke(adapter, symbolic)
    assert fake.delays == delays and len(fake.calls) == calls


@pytest.mark.parametrize("finish", ["MAX_TOKENS", "OTHER", None])
def test_incomplete_candidates_are_not_success(symbolic, finish):
    fake = FakeClient([response(output(symbolic, InterpretationDepth.PREMIUM), finish=finish)])
    with pytest.raises(InterpretationError) as error:
        invoke(provider(fake, max_retries=0), symbolic)
    assert error.value.code == "interpretation_invalid_response"


def test_nontext_and_empty_response_rejected(symbolic):
    for event in [types.GenerateContentResponse(), types.GenerateContentResponse(candidates=[
            types.Candidate(finish_reason="STOP", content=types.Content(parts=[
                types.Part(function_call=types.FunctionCall(name="secret_function", args={}))]))])]:
        fake = FakeClient([event])
        with pytest.raises(InterpretationError) as error:
            invoke(provider(fake, max_retries=0), symbolic)
        assert error.value.code == "interpretation_invalid_response"


def test_retries_and_repair_share_total_budget(symbolic):
    fake = FakeClient([httpx.ConnectError("private"), response("{}"),
                       response(output(symbolic, InterpretationDepth.PREMIUM))])
    invoke(provider(fake), symbolic)
    assert len(fake.calls) == 3
    assert [REPAIR in c["config"].system_instruction for c in fake.calls] == [False, False, True]


def test_service_does_not_trust_custom_provider(symbolic):
    class BadProvider:
        async def interpret(self, *args, **kwargs):
            return {"text": "PRIVATE"}
    metadata = InterpretationMetadata(provider="gemini", model="synthetic-model",
                                      prompt_version=PROMPT_VERSION, config_version="test-v1")
    with pytest.raises(InterpretationError) as error:
        invoke(InterpretationService(BadProvider(), metadata), symbolic)
    assert error.value.code == "interpretation_schema_mismatch"


@pytest.mark.parametrize("event,code", [(RuntimeError("PRIVATE"), "interpretation_unavailable"),
    (TimeoutError("PRIVATE"), "interpretation_timeout"),
    (InterpretationError("interpretation_refusal"), "interpretation_refusal")])
def test_service_sanitizes_provider_exceptions(symbolic, event, code):
    class BadProvider:
        async def interpret(self, *args, **kwargs):
            raise event
    metadata = InterpretationMetadata(provider="gemini", model="synthetic-model",
                                      prompt_version=PROMPT_VERSION, config_version="test-v1")
    with pytest.raises(InterpretationError) as error:
        invoke(InterpretationService(BadProvider(), metadata), symbolic)
    assert error.value.code == code
    assert "PRIVATE" not in str(error.value) and error.value.__suppress_context__


@pytest.mark.parametrize("status,body,code", [(200, "NOT_JSON_PRIVATE", "interpretation_invalid_response"),
    (429, '{"error":{"message":"PRIVATE","code":429}}', "interpretation_rate_limited"),
    (503, '{"error":{"message":"PRIVATE","code":503}}', "interpretation_unavailable")])
def test_real_sdk_failure_envelopes_do_not_leak_or_multiply_retries(symbolic, status, body, code, caplog):
    caplog.set_level(logging.DEBUG)
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(status, content=body, headers={"content-type": "application/json"})
    def factory(config):
        return genai.Client(enterprise=False, api_key=config.api_key.get_secret_value(),
                            http_options=types.HttpOptions(
                                retry_options=types.HttpRetryOptions(attempts=1),
                                client_args={"transport": httpx.MockTransport(handler), "trust_env": False},
                                async_client_args={"transport": httpx.MockTransport(handler), "trust_env": False}))
    adapter = GeminiInterpretationProvider(GeminiConfig(model="synthetic-model", api_key=SecretStr("test"),
                                                        max_retries=0), client_factory=factory)
    with pytest.raises(InterpretationError) as error:
        invoke(adapter, symbolic)
    assert error.value.code == code and len(requests) == 1
    assert "PRIVATE" not in caplog.text + str(error.value)
