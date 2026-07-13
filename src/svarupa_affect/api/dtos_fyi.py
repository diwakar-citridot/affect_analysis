"""API DTOs for AFF FYI / Short Note formulation."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field, field_validator

from ..domain.enums import Durability, StatePole
from .dtos_v2 import TokenUsageDTO


class FyiSignalDTO(BaseModel):
    """One pre-scored AFF signal to formulate into a Short Note."""

    attribute: str = Field(min_length=1)
    relevance: float = Field(ge=0.0, le=1.0)
    state: StatePole
    dimension_name: str = Field(min_length=1)
    durability: Durability = Durability.UNKNOWN
    rationale: str = Field(default="", max_length=2000)
    reasoning: str = Field(
        default="",
        max_length=2000,
        description="AFF processing or scoring reasoning for this signal (from /v2/affect/analyze).",
    )
    span: str = Field(default="", max_length=500)


class FyiFormulateRequest(BaseModel):
    """Formulate up to three AFF Short Notes from pre-scored signals."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_text: str = Field(
        min_length=1,
        description="The user's lived-experience passage that produced the signals.",
    )
    signals: list[FyiSignalDTO] = Field(min_length=1, max_length=3)
    user_state_tier: str = Field(
        default="standard",
        description=(
            "Session safety tier (standard | vulnerable | crisis) — modulates tentativeness."
        ),
    )

    @field_validator("signals")
    @classmethod
    def _non_empty_attributes(cls, signals: list[FyiSignalDTO]) -> list[FyiSignalDTO]:
        for sig in signals:
            if not sig.attribute.strip():
                raise ValueError("each signal must have a non-empty attribute")
        return signals


class FyiCardDTO(BaseModel):
    """One formulated Short Note / FYI card."""

    text: str
    simple_sentence: str
    reasoning: str
    attribute: str
    dimension: str
    status: StatePole
    expandable: bool = True


class FyiMetaResponse(BaseModel):
    layer: str = "AFF"
    artifact: str = "ShortNote"
    prompt_version: str
    api_version: str
    max_signals_per_request: int = 3
    bedrock_model_configured: bool = False


class FyiFormulateResponse(BaseModel):
    request_id: str
    layer: str = "AFF"
    layer_version: str
    artifact: str = "ShortNote"
    prompt_version: str
    llm_used: bool = False
    llm_attempted: bool = False
    llm_failure: str | None = None
    cards: list[FyiCardDTO] = []
    usage: TokenUsageDTO = Field(default_factory=TokenUsageDTO)
