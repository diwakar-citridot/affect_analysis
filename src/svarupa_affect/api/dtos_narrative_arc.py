"""API DTOs for NAR v1 — LLM-native narrative-arc analysis."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from ..domain.enums import LatencyMode
from ..domain.models import Provenance
from .dtos import AttributeScoreDTO, DimensionalSignalDTO, FieldAxisDTO, SharedFeaturesDTO


class NarrativeArcOptions(BaseModel):
    """Per-request tuning for the NAR LLM-primary path."""

    latency_mode: LatencyMode = LatencyMode.STANDARD
    force: bool = Field(
        default=False,
        description="Bypass the pre-LLM salience gate (equivalent to force_llm_primary).",
    )


class NarrativeArcAnalyzeRequest(BaseModel):
    """Analyze one passage for narrative arc via the LLM-primary pipeline."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_text: str = Field(
        min_length=1,
        description="First-person or narrative lived experience.",
    )
    locale: str = "en"
    shared_features: SharedFeaturesDTO | None = Field(
        default=None,
        description="Optional PSY/AFF temporal hints (supporting only, not authoritative).",
    )
    options: NarrativeArcOptions = Field(default_factory=NarrativeArcOptions)


class NarrativeArcMetaResponse(BaseModel):
    """Service metadata for NAR v2 clients."""

    layer: str = "NAR"
    affect_mode: str = "llm_primary"
    prompt_version: str
    api_version: str
    emit_dimensions: list[int] = []
    bedrock_model_configured: bool = False


class NarrativeArcReadingDTO(BaseModel):
    """Detected temporal / arc structure of the expression."""

    shape: str = "none"
    loop_detected: bool = False
    single_snapshot: bool = True
    temporal_structure: str = ""
    mismatch_detected: bool = False
    events: list[str] = []
    rationale: str = ""


class TokenUsageDTO(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0


class NarrativeArcAnalyzeResponse(BaseModel):
    """Public NAR response: fusion envelope + narrative arc + LLM-primary status."""

    request_id: str
    layer: str = "NAR"
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
    narrative_arc: NarrativeArcReadingDTO
    attribute_scores: list[AttributeScoreDTO] = []
    field_axes: list[FieldAxisDTO] = []
    signals: list[DimensionalSignalDTO] = []
    usage: TokenUsageDTO = Field(default_factory=TokenUsageDTO)
    provenance: Provenance
