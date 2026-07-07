"""Mappers for MET v2 API — force ``llm_primary`` and shape the public response."""

from __future__ import annotations

from ..application.analyze_metaphor import MetaphorAnalyzeResult
from ..domain.models import DimensionalSignal, LayerContext
from ..domain.ports import IDimensionRegistry
from ..infrastructure.kg.dimension_registry import build_dimension_registry
from .dtos import AttributeScoreDTO, DimensionalSignalDTO
from .dtos_metaphor import (
    MetaphorAnalyzeRequest,
    MetaphorAnalyzeResponse,
    MetaphorDTO,
)
from .dtos_v2 import TokenUsageDTO


def to_metaphor_context(req: MetaphorAnalyzeRequest) -> LayerContext:
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


def _signal_to_dto(
    signal: DimensionalSignal, registry: IDimensionRegistry
) -> DimensionalSignalDTO:
    return DimensionalSignalDTO(
        request_id=signal.request_id,
        layer=signal.layer,
        layer_version=signal.layer_version,
        dimension_name=registry.name_for(signal.dimension_id),
        relevance=signal.relevance,
        confidence=signal.confidence,
        uncertainty=signal.uncertainty,
        attribute_scores=[
            AttributeScoreDTO(
                attribute=score.attribute,
                relevance=score.relevance,
                state=score.state,
                dimension_name=registry.name_for(score.dimension_id),
                durability=score.durability,
                reasoning=score.reasoning,
            )
            for score in signal.attribute_scores
        ],
        state_hint=signal.state_hint,
        evidence=signal.evidence,
        abstained=signal.abstained,
        provenance=signal.provenance,
    )


def to_metaphor_response(
    result: MetaphorAnalyzeResult,
    registry: IDimensionRegistry | None = None,
) -> MetaphorAnalyzeResponse:
    reg = registry or build_dimension_registry()
    signal_dtos = [_signal_to_dto(s, reg) for s in result.signals]
    abstained = [s.dimension_name for s in signal_dtos if s.abstained]

    attribute_scores: list[AttributeScoreDTO] = []
    for signal in signal_dtos:
        attribute_scores.extend(signal.attribute_scores)
    attribute_scores.sort(key=lambda s: s.relevance, reverse=True)

    layer_version = result.signals[0].layer_version if result.signals else "2.1.0"
    request_id = result.signals[0].request_id if result.signals else ""

    return MetaphorAnalyzeResponse(
        request_id=request_id,
        layer="MET",
        layer_version=layer_version,
        analysis_mode="llm_primary",
        llm_primary_used=result.used,
        llm_primary_attempted=result.attempted,
        llm_primary_failure=result.failure,
        llm_primary_gate_reasons=result.gate_reasons,
        abstained_dimensions=abstained,
        metaphors=[
            MetaphorDTO(
                source=m.source,
                target=m.target,
                source_domain=m.source_domain,
                span=m.span,
                rationale=m.rationale,
            )
            for m in result.metaphors
        ],
        attribute_scores=attribute_scores,
        signals=signal_dtos,
        usage=TokenUsageDTO(**(result.usage or {})),
    )
