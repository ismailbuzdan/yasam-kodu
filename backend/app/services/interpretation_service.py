"""Provider-independent orchestration; no calculation, HTTP endpoint or global client."""
from pydantic import ValidationError

from app.core.config import Settings
from app.schemas.interpretation import (
    InterpretationDepth, InterpretationInput, InterpretationMetadata, InterpretationResult, Language,
)
from app.services.interpretation_models import InterpretationError, InterpretationProvider
from app.services.interpretation_validation import validate_content_for_input


def admit_input(input: InterpretationInput, depth: InterpretationDepth, language: Language) -> InterpretationInput:
    if type(input) is not InterpretationInput or type(depth) is not InterpretationDepth or language != "tr":
        raise InterpretationError("interpretation_invalid_input")
    try:
        return InterpretationInput.model_validate(input.model_dump(warnings=False))
    except (ValidationError, ValueError, TypeError):
        raise InterpretationError("interpretation_invalid_input") from None


class InterpretationService:
    def __init__(self, provider: InterpretationProvider, metadata: InterpretationMetadata):
        self._provider = provider
        self._metadata = InterpretationMetadata.model_validate(metadata.model_dump())

    async def interpret(self, input: InterpretationInput, *, depth: InterpretationDepth,
                        language: Language = "tr") -> InterpretationResult:
        input = admit_input(input, depth, language)
        try:
            content = await self._provider.interpret(input, depth=depth, language=language)
            content = validate_content_for_input(content, input, depth=depth, language=language)
            result = InterpretationResult(content=content, metadata=self._metadata)
            return InterpretationResult.model_validate(result.model_dump())
        except InterpretationError as error:
            # Recreate a static exception, not an adapter exception with SDK fields attached.
            raise InterpretationError(error.code) from None
        except TimeoutError:
            raise InterpretationError("interpretation_timeout") from None
        except ValidationError:
            raise InterpretationError("interpretation_schema_mismatch") from None
        except Exception:
            # This is an external-provider privacy boundary; never expose exception bodies/locals.
            raise InterpretationError("interpretation_unavailable") from None


def create_interpretation_service(settings: Settings) -> InterpretationService:
    from app.services.providers.gemini_interpretation import GeminiInterpretationProvider, GeminiConfig
    from app.services.interpretation_prompts import CONFIG_VERSION, PROMPT_VERSION

    if settings.ai_provider != "gemini":
        raise InterpretationError("interpretation_configuration_error")
    config = GeminiConfig.from_settings(settings)
    return InterpretationService(GeminiInterpretationProvider(config), InterpretationMetadata(
        provider="gemini", model=config.model, prompt_version=PROMPT_VERSION,
        config_version=CONFIG_VERSION))
