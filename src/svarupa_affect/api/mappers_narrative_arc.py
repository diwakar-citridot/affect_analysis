"""Mappers for NAR v2 API — force ``llm_primary`` and shape the public response."""

from __future__ import annotations

from ..application.analyze_narrative_arc import NarrativeArcAnalyzeResult
from ..application.mappers import (
    _aggregate_attribute_scores,
    _flatten_field_axes,
    _signal_to_dto,
)
from ..domain.models import LayerContext, SharedFeatures
from ..domain.ports import IDimensionRegistry
from ..infrastructure.kg.dimension_registry import build_dimension_registry
from .dtos_narrative_arc import (
    NarrativeArcAnalyzeRequest,
    NarrativeArcAnalyzeResponse,
    NarrativeArcReadingDTO,
    TokenUsageDTO,
)


def to_narrative_context(req: NarrativeArcAnalyzeRequest) -> LayerContext:
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


def to_narrative_response(
    result: NarrativeArcAnalyzeResult,
    ctx: LayerContext,
    registry: IDimensionRegistry | None = None,
) -> NarrativeArcAnalyzeResponse:
    reg = registry or build_dimension_registry()
    nar = result.narrative_arc
    arc = nar.narrative_arc
    signal_dtos = [_signal_to_dto(s, reg) for s in result.signals]
    prov = result.signals[0].provenance if result.signals else nar.field.provenance
    abstained = [s.dimension_name for s in signal_dtos if s.abstained]
    layer_version = result.signals[0].layer_version if result.signals else ""
    return NarrativeArcAnalyzeResponse(
        request_id=ctx.request_id,
        layer="NAR",
        layer_version=layer_version,
        affect_mode=prov.affect_mode or "llm_primary",
        llm_primary_used=prov.llm_primary_used,
        llm_primary_attempted=prov.llm_primary_attempted,
        llm_primary_failure=prov.llm_primary_failure,
        llm_primary_gate_reasons=list(prov.llm_primary_gate_reasons),
        abstained_dimensions=abstained,
        narrative_arc=NarrativeArcReadingDTO(
            shape=arc.shape,
            loop_detected=arc.loop_detected,
            single_snapshot=arc.single_snapshot,
            temporal_structure=arc.temporal_structure,
            mismatch_detected=arc.mismatch_detected,
            events=list(arc.events),
            rationale=arc.rationale,
        ),
        attribute_scores=_aggregate_attribute_scores(signal_dtos),
        field_axes=_flatten_field_axes(nar.field),
        signals=signal_dtos,
        usage=TokenUsageDTO(**(result.usage or {})),
        provenance=prov,
    )
