"""Mappers for AFF v2 API — force ``llm_primary`` and shape the public response."""

from __future__ import annotations

from ..application.analyze_affect import AnalyzeResult
from ..domain.models import LayerContext, SharedFeatures
from ..domain.ports import IDimensionRegistry
from ..infrastructure.kg.dimension_registry import build_dimension_registry
from .dtos_v2 import (
    LivedExperienceAnalyzeRequest,
    LivedExperienceAnalyzeResponse,
    TokenUsageDTO,
)
from ..application.mappers import to_response


def to_v2_context(req: LivedExperienceAnalyzeRequest) -> LayerContext:
    shared = None
    if req.shared_features is not None:
        shared = SharedFeatures(
            valence=req.shared_features.valence,
            arousal=req.shared_features.arousal,
            temporal_cues=req.shared_features.temporal_cues,
        )
    return LayerContext(
        request_id=req.request_id,
        analysis_text=req.analysis_text,
        locale=req.locale,
        shared_features=shared,
        latency_mode=req.options.latency_mode,
        affect_mode="llm_primary",
        enable_llm_primary=True,
        force_llm_primary=req.options.force,
        enable_llm_assist=False,
        force_llm_assist=False,
    )


def to_v2_response(
    result: AnalyzeResult,
    registry: IDimensionRegistry | None = None,
) -> LivedExperienceAnalyzeResponse:
    reg = registry or build_dimension_registry()
    base = to_response(result, reg)
    prov = base.provenance
    abstained = [s.dimension_name for s in base.signals if s.abstained]
    return LivedExperienceAnalyzeResponse(
        request_id=base.request_id,
        layer=base.layer,
        layer_version=base.layer_version,
        affect_mode=prov.affect_mode or "llm_primary",
        llm_primary_used=prov.llm_primary_used,
        llm_primary_attempted=prov.llm_primary_attempted,
        llm_primary_failure=prov.llm_primary_failure,
        llm_primary_gate_reasons=list(prov.llm_primary_gate_reasons),
        abstained_dimensions=abstained,
        attribute_scores=base.attribute_scores,
        field_axes=base.field_axes,
        signals=base.signals,
        usage=TokenUsageDTO(**(result.usage or {})),
        phenomenology_input=base.phenomenology_input,
        provenance=prov,
    )
