"""API DTOs (§3.4) — pydantic v2 request/response mirroring affect_input / affect_output.

The response embeds the fusion envelope (with ``dimension_name`` instead of ``dimension_id``)
and the single curated ``PhenomenologyInput`` public contract.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from ..domain.enums import Durability, FieldAxis, LatencyMode, StatePole
from ..domain.models import Evidence, PhenomenologyInput, Provenance, StateHint, UncertaintyProfile


class SharedFeaturesDTO(BaseModel):
    valence: float | None = Field(default=None, ge=-1.0, le=1.0)
    arousal: float | None = Field(default=None, ge=0.0, le=1.0)
    temporal_cues: list[str] = []


class AnalyzeOptions(BaseModel):
    latency_mode: LatencyMode = LatencyMode.STANDARD
    # None = use SVARUPA_ENABLE_LLM_ASSIST from .env
    enable_llm_assist: bool | None = None
    # None = use SVARUPA_FORCE_LLM_ASSIST from .env
    force_llm_assist: bool | None = None
    # None = use SVARUPA_AFFECT_MODE from .env (legacy_deterministic | llm_primary)
    affect_mode: str | None = None
    enable_llm_primary: bool | None = None
    force_llm_primary: bool | None = None


class AnalyzeRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_text: str = Field(min_length=1)
    locale: str = "en"
    conversation_history: list[dict[str, str]] = []
    shared_features: SharedFeaturesDTO | None = None
    candidate_dimensions: list[int] = []
    kg_context: dict[str, str] = {}
    options: AnalyzeOptions = Field(default_factory=AnalyzeOptions)


class AttributeScoreDTO(BaseModel):
    attribute: str
    relevance: float = Field(ge=0.0, le=1.0)
    state: StatePole
    dimension_name: str  # sanskrit_term from svarupa_dimensions
    durability: Durability = Durability.UNKNOWN
    rationale: str | None = None
    span: str | None = None
    reasoning: str | None = None


class FieldAxisDTO(BaseModel):
    """One reconstructed leaf axis from the global affective field (``group.attr``)."""

    axis: str
    value: float
    confidence: float = Field(ge=0.0, le=1.0)
    coverage: float | None = Field(default=None, ge=0.0, le=1.0)


class DimensionalSignalDTO(BaseModel):
    """Fusion envelope for API consumers — ``dimension_name`` is ``sanskrit_term``."""

    request_id: str
    layer: str = "AFF"
    layer_version: str
    dimension_name: str  # sanskrit_term from svarupa_dimensions
    relevance: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    uncertainty: UncertaintyProfile | None = None
    attribute_scores: list[AttributeScoreDTO] = []
    state_hint: StateHint | None = None
    evidence: list[Evidence] = []
    abstained: bool = False
    provenance: Provenance


class AnalyzeResponse(BaseModel):
    request_id: str
    layer: str = "AFF"
    layer_version: str
    attribute_scores: list[AttributeScoreDTO] = []
    field_axes: list[FieldAxisDTO] = []
    signals: list[DimensionalSignalDTO] = []
    phenomenology_input: PhenomenologyInput
    provenance: Provenance
