"""API DTOs for AFF v2 — LLM-native lived-experience analysis.

These types describe the ``/v2`` surface only. Requests always run ``affect_mode=llm_primary``.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from ..domain.enums import LatencyMode
from ..domain.models import PhenomenologyInput, Provenance
from .dtos import AttributeScoreDTO, DimensionalSignalDTO, FieldAxisDTO, SharedFeaturesDTO


class LivedExperienceOptions(BaseModel):
    """Per-request tuning for the v2 LLM-primary path."""

    latency_mode: LatencyMode = LatencyMode.STANDARD
    force: bool = Field(
        default=False,
        description="Bypass the pre-LLM salience gate (equivalent to force_llm_primary).",
    )


class LivedExperienceAnalyzeRequest(BaseModel):
    """Analyze one passage of lived-experience text via the v2 LLM-primary pipeline."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_text: str = Field(
        min_length=1,
        description="First-person or narrative lived experience.",
    )
    locale: str = "en"
    shared_features: SharedFeaturesDTO | None = Field(
        default=None,
        description="Optional PHE/NAR hints (supporting only, not authoritative).",
    )
    options: LivedExperienceOptions = Field(default_factory=LivedExperienceOptions)


class LivedExperienceMetaResponse(BaseModel):
    """Service metadata for v2 clients."""

    layer: str = "AFF"
    affect_mode: str = "llm_primary"
    prompt_version: str
    api_version: str
    emit_dimensions: list[int] = []
    bedrock_model_configured: bool = False


class LivedExperienceAnalyzeResponse(BaseModel):
    """Public v2 response: fusion envelope + phenomenology + LLM-primary status."""

    request_id: str
    layer: str = "AFF"
    layer_version: str
    affect_mode: str = "llm_primary"
    llm_primary_used: bool = False
    llm_primary_attempted: bool = False
    llm_primary_failure: str | None = None
    llm_primary_gate_reasons: list[str] = []
    abstained_dimensions: list[str] = Field(
        default_factory=list,
        description="Dimension names (sanskrit_term) where the layer abstained.",
    )
    attribute_scores: list[AttributeScoreDTO] = []
    field_axes: list[FieldAxisDTO] = []
    signals: list[DimensionalSignalDTO] = []
    phenomenology_input: PhenomenologyInput
    provenance: Provenance
