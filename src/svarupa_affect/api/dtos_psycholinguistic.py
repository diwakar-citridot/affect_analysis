"""API DTOs for PSY v1 — LLM-native psycholinguistic analysis."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from ..domain.enums import LatencyMode
from ..domain.models import Provenance
from .dtos import AttributeScoreDTO, DimensionalSignalDTO, FieldAxisDTO
from .dtos_narrative_arc import TokenUsageDTO


class PsycholinguisticOptions(BaseModel):
    """Per-request tuning for the PSY LLM-primary path."""

    latency_mode: LatencyMode = LatencyMode.STANDARD
    force: bool = Field(
        default=False,
        description="Bypass the pre-LLM salience gate (equivalent to force_llm_primary).",
    )


class PsycholinguisticAnalyzeRequest(BaseModel):
    """Analyze one passage for linguistic form via the LLM-primary pipeline."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_text: str = Field(
        min_length=1,
        description="First-person or narrative lived experience.",
    )
    locale: str = "en"
    options: PsycholinguisticOptions = Field(default_factory=PsycholinguisticOptions)


class PsycholinguisticMetaResponse(BaseModel):
    """Service metadata for PSY v2 clients."""

    layer: str = "PSY"
    affect_mode: str = "llm_primary"
    prompt_version: str
    api_version: str
    emit_dimensions: list[int] = []
    bedrock_model_configured: bool = False


class PsycholinguisticFeaturesDTO(BaseModel):
    """Detected linguistic-form features of the expression."""

    pronoun_orientation: str = ""
    agency_ratio: float = 0.5
    attribution_locus: str = "unclear"
    coherence: float = 0.5
    temporal_orientation: str = ""
    cognitive_complexity: float = 0.5
    rumination_markers: bool = False
    passive_constructions: bool = False
    rationale: str = ""


class PsycholinguisticAnalyzeResponse(BaseModel):
    """Public PSY response: fusion envelope + linguistic features + LLM-primary status."""

    request_id: str
    layer: str = "PSY"
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
    psycholinguistic_features: PsycholinguisticFeaturesDTO
    attribute_scores: list[AttributeScoreDTO] = []
    field_axes: list[FieldAxisDTO] = []
    signals: list[DimensionalSignalDTO] = []
    usage: TokenUsageDTO = Field(default_factory=TokenUsageDTO)
    provenance: Provenance
