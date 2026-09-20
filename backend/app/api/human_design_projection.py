"""Shared public HD projection; no calculation or internal solver diagnostics."""
from app.schemas.human_design import HumanDesignResponse
from app.services.human_design_models import HumanDesignResult


def project_human_design(result: HumanDesignResult) -> HumanDesignResponse:
    return HumanDesignResponse(
        metadata=result.metadata, birth_utc=result.birth_utc, design_utc=result.astronomy.design_utc,
        personality=result.astronomy.personality, design=result.astronomy.design_activations,
        active_gates=result.active_gates, channels=result.channels,
        defined_centers=result.defined_centers, undefined_centers=result.undefined_centers,
        type=result.type, strategy=result.strategy, authority=result.authority, profile=result.profile,
        definition=result.definition, component_count=result.component_count,
        definition_components=result.definition_components,
    )
