"""Mapping between API DTOs and domain objects (§2.2 application/mappers.py).

Keeps the API edge thin: requests become a pure ``LayerContext``; the use-case result becomes
an ``AnalyzeResponse`` exposing only the public surface (signals + PhenomenologyInput).
"""

from __future__ import annotations

from ..api.dtos import (
    AnalyzeRequest,
    AnalyzeResponse,
    AttributeScoreDTO,
    DimensionalSignalDTO,
    FieldAxisDTO,
)
from ..domain.enums import FieldAxis
from ..domain.models import AffectiveField, DimensionalSignal, LayerContext, SharedFeatures
from ..domain.ports import IDimensionRegistry
from ..infrastructure.config import Settings
from ..infrastructure.kg.dimension_registry import build_dimension_registry
from .analyze_affect import AnalyzeResult


def _resolve_llm_flags(req: AnalyzeRequest) -> tuple[bool, bool, str, bool, bool]:
    settings = Settings.load()
    enable_assist = (
        settings.enable_llm_assist
        if req.options.enable_llm_assist is None
        else req.options.enable_llm_assist
    )
    force_assist = (
        settings.force_llm_assist
        if req.options.force_llm_assist is None
        else req.options.force_llm_assist
    )
    affect_mode = (
        settings.affect_mode if req.options.affect_mode is None else req.options.affect_mode
    )
    enable_primary = (
        settings.enable_llm_primary
        if req.options.enable_llm_primary is None
        else req.options.enable_llm_primary
    )
    force_primary = (
        settings.force_llm_primary
        if req.options.force_llm_primary is None
        else req.options.force_llm_primary
    )
    return enable_assist, force_assist, affect_mode, enable_primary, force_primary


def to_context(req: AnalyzeRequest) -> LayerContext:
    shared = None
    if req.shared_features is not None:
        shared = SharedFeatures(
            valence=req.shared_features.valence,
            arousal=req.shared_features.arousal,
            temporal_cues=req.shared_features.temporal_cues,
        )
    enable_llm_assist, force_llm_assist, affect_mode, enable_llm_primary, force_llm_primary = (
        _resolve_llm_flags(req)
    )
    return LayerContext(
        request_id=req.request_id,
        analysis_text=req.analysis_text,
        locale=req.locale,
        conversation_history=req.conversation_history,
        candidate_dimensions=req.candidate_dimensions,
        shared_features=shared,
        kg_context=req.kg_context,
        latency_mode=req.options.latency_mode,
        enable_llm_assist=enable_llm_assist,
        force_llm_assist=force_llm_assist,
        affect_mode=affect_mode,
        enable_llm_primary=enable_llm_primary,
        force_llm_primary=force_llm_primary,
    )


def _flatten_field_axes(field: AffectiveField) -> list[FieldAxisDTO]:
    axes: list[FieldAxisDTO] = []
    for axis in FieldAxis:
        feat = field.feature(axis)
        coverage = field.axis_coverage.get(axis)
        axes.append(
            FieldAxisDTO(
                axis=axis.value,
                value=feat.value,
                confidence=feat.confidence,
                coverage=round(coverage, 4) if coverage is not None else None,
            )
        )
    return axes


def _aggregate_attribute_scores(
    signals: list[DimensionalSignalDTO],
) -> list[AttributeScoreDTO]:
    merged: list[AttributeScoreDTO] = []
    for signal in signals:
        merged.extend(signal.attribute_scores)
    merged.sort(key=lambda score: score.relevance, reverse=True)
    return merged


def _signal_to_dto(signal: DimensionalSignal, registry: IDimensionRegistry) -> DimensionalSignalDTO:
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
                rationale=score.rationale,
                span=score.span,
                reasoning=score.reasoning,
            )
            for score in signal.attribute_scores
        ],
        state_hint=signal.state_hint,
        evidence=signal.evidence,
        abstained=signal.abstained,
        provenance=signal.provenance,
    )


def to_response(
    result: AnalyzeResult, registry: IDimensionRegistry | None = None
) -> AnalyzeResponse:
    reg = registry or build_dimension_registry()
    pi = result.phenomenology_input
    signal_dtos = [_signal_to_dto(s, reg) for s in result.signals]
    return AnalyzeResponse(
        request_id=pi.request_id,
        layer="AFF",
        layer_version=pi.layer_version,
        attribute_scores=_aggregate_attribute_scores(signal_dtos),
        field_axes=_flatten_field_axes(pi.background_field),
        signals=signal_dtos,
        phenomenology_input=pi,
        provenance=pi.provenance,
    )


def to_response_dict(result: AnalyzeResult, registry: IDimensionRegistry | None = None) -> dict:
    """JSON-ready dict (used by the CLI and for golden replay)."""
    return to_response(result, registry).model_dump(mode="json")
