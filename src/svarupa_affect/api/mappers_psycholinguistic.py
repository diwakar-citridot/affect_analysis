"""Mappers for PSY v2 API — force ``llm_primary`` and shape the public response."""

from __future__ import annotations

from ..application.analyze_psycholinguistic import PsycholinguisticAnalyzeResult
from ..application.mappers import (
    _aggregate_attribute_scores,
    _flatten_field_axes,
    _signal_to_dto,
)
from ..domain.models import LayerContext
from ..domain.ports import IDimensionRegistry
from ..infrastructure.kg.dimension_registry import build_dimension_registry
from .dtos_narrative_arc import TokenUsageDTO
from .dtos_psycholinguistic import (
    PsycholinguisticAnalyzeRequest,
    PsycholinguisticAnalyzeResponse,
    PsycholinguisticFeaturesDTO,
)


def to_psycholinguistic_context(req: PsycholinguisticAnalyzeRequest) -> LayerContext:
    return LayerContext(
        request_id=req.request_id,
        analysis_text=req.analysis_text,
        locale=req.locale,
        latency_mode=req.options.latency_mode,
        affect_mode="llm_primary",
        enable_llm_primary=True,
        force_llm_primary=req.options.force,
        enable_llm_assist=False,
        force_llm_assist=False,
    )


def to_psycholinguistic_response(
    result: PsycholinguisticAnalyzeResult,
    ctx: LayerContext,
    registry: IDimensionRegistry | None = None,
) -> PsycholinguisticAnalyzeResponse:
    reg = registry or build_dimension_registry()
    psy = result.psycholinguistic
    feats = psy.features
    signal_dtos = [_signal_to_dto(s, reg) for s in result.signals]
    prov = result.signals[0].provenance if result.signals else psy.field.provenance
    abstained = [s.dimension_name for s in signal_dtos if s.abstained]
    layer_version = result.signals[0].layer_version if result.signals else ""
    return PsycholinguisticAnalyzeResponse(
        request_id=ctx.request_id,
        layer="PSY",
        layer_version=layer_version,
        affect_mode=prov.affect_mode or "llm_primary",
        llm_primary_used=prov.llm_primary_used,
        llm_primary_attempted=prov.llm_primary_attempted,
        llm_primary_failure=prov.llm_primary_failure,
        llm_primary_gate_reasons=list(prov.llm_primary_gate_reasons),
        abstained_dimensions=abstained,
        psycholinguistic_features=PsycholinguisticFeaturesDTO(
            pronoun_orientation=feats.pronoun_orientation,
            agency_ratio=feats.agency_ratio,
            attribution_locus=feats.attribution_locus,
            coherence=feats.coherence,
            temporal_orientation=feats.temporal_orientation,
            cognitive_complexity=feats.cognitive_complexity,
            rumination_markers=feats.rumination_markers,
            passive_constructions=feats.passive_constructions,
            rationale=feats.rationale,
        ),
        attribute_scores=_aggregate_attribute_scores(signal_dtos),
        field_axes=_flatten_field_axes(psy.field),
        signals=signal_dtos,
        usage=TokenUsageDTO(**(result.usage or {})),
        provenance=prov,
    )
