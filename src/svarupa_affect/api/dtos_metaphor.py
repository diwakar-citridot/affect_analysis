"""API DTOs for MET v2 — LLM-native metaphor analysis.

These types describe the ``/v2/metaphor/*`` surface. Requests always run
the LLM-primary metaphor path. Mirrors ``dtos_v2`` (AFF).
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from ..domain.enums import LatencyMode
from ..domain.models import Provenance
from .dtos import AttributeScoreDTO, DimensionalSignalDTO
from .dtos_narrative_arc import TokenUsageDTO


class MetaphorOptions(BaseModel):
    """Per-request tuning for the metaphor LLM-primary path."""

    latency_mode: LatencyMode = LatencyMode.STANDARD
    force: bool = Field(
        default=False,
        description="Bypass the pre-LLM salience gate (force the Bedrock call).",
    )


class MetaphorAnalyzeRequest(BaseModel):
    """Analyze one passage for the metaphors it uses via the LLM-primary pipeline."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_text: str = Field(min_length=1, description="Free text to read for metaphor.")
    locale: str = "en"
    options: MetaphorOptions = Field(default_factory=MetaphorOptions)


class MetaphorMetaResponse(BaseModel):
    """Service metadata for MET v2 clients."""

    layer: str = "MET"
    affect_mode: str = "llm_primary"
    prompt_version: str
    api_version: str
    emit_dimensions: list[int] = []
    bedrock_model_configured: bool = False


class MetaphorDTO(BaseModel):
    """One extracted metaphor: source image → target experience."""

    source: str
    target: str
    source_domain: str = ""
    span: str = ""
    rationale: str = ""


class MetaphorAnalyzeResponse(BaseModel):
    """Public MET response: extracted metaphors + primary-dimension signals."""

    request_id: str
    layer: str = "MET"
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
    metaphors: list[MetaphorDTO] = []
    attribute_scores: list[AttributeScoreDTO] = []
    signals: list[DimensionalSignalDTO] = []
    usage: TokenUsageDTO = Field(default_factory=TokenUsageDTO)
    provenance: Provenance | None = None
