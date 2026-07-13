"""NarrativeArcLayer (use case): LLM-primary narrative-arc analysis (NAR v1).

Mirrors the AFF ``AffectLayer.analyze_full`` LLM-primary path: one Bedrock call
produces narrative-arc structure plus a ``DimensionalSignal[]`` fusion envelope.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .. import __version__
from ..domain.enums import StatePole
from ..domain.exceptions import ModelUnavailable
from ..domain.models import (
    AttributeScore,
    DimensionalSignal,
    Evidence,
    LayerContext,
    Provenance,
    StateHint,
    UncertaintyProfile,
)
from ..domain.scoring import dimension_relevance
from ..infrastructure.config import Settings
from .narrative_arc_orchestrator import LAYER_CODE, NarrativeArcOrchestrator, NarrativeArcResult

logger = logging.getLogger("svarupa_affect.narrative")

_RELEVANCE_FLOOR = 0.12


@dataclass(frozen=True)
class NarrativeArcAnalyzeResult:
    signals: list[DimensionalSignal]
    narrative_arc: NarrativeArcResult
    used: bool
    attempted: bool
    abstained: bool
    failure: str | None
    gate_reasons: list[str]
    usage: dict[str, int] = field(default_factory=dict)


class NarrativeArcLayer:
    code: str = LAYER_CODE
    version: str = __version__

    def __init__(
        self,
        orchestrator: NarrativeArcOrchestrator,
        *,
        emit_dimensions: frozenset[int] | None = None,
    ) -> None:
        self._orchestrator = orchestrator
        self._emit_dimensions = (
            emit_dimensions if emit_dimensions is not None else orchestrator._emit_dimensions
        )

    @property
    def emit_dimensions(self) -> frozenset[int]:
        return self._emit_dimensions

    async def analyze_full(self, ctx: LayerContext) -> NarrativeArcAnalyzeResult:
        result = await self._orchestrator.score(ctx)
        provenance = self._provenance(result)
        uncertainty = self._orchestrator.build_uncertainty(result, ctx.analysis_text)
        signals = self._build_signals(ctx, result, uncertainty, provenance)
        return NarrativeArcAnalyzeResult(
            signals=signals,
            narrative_arc=result,
            used=result.used,
            attempted=result.attempted,
            abstained=result.abstained,
            failure=result.failure if (result.attempted and not result.used) else None,
            gate_reasons=list(result.reasons),
            usage=result.usage,
        )

    def _provenance(self, result: NarrativeArcResult) -> Provenance:
        le = self._orchestrator
        return Provenance(
            layer_version=self.version,
            affect_mode="llm_primary",
            model_id=le.model_id,
            prompt_version=le.prompt_version,
            llm_primary_used=result.used,
            llm_primary_attempted=result.attempted,
            llm_primary_failure=result.failure if (result.attempted and not result.used) else None,
            llm_primary_gate_reasons=list(result.reasons),
            samples=result.samples if result.used else 0,
        )

    def _build_signals(
        self,
        ctx: LayerContext,
        result: NarrativeArcResult,
        uncertainty: UncertaintyProfile,
        provenance: Provenance,
    ) -> list[DimensionalSignal]:
        signals: list[DimensionalSignal] = []
        for dimension_id in sorted(self._emit_dimensions):
            attrs = result.scores_by_dimension.get(dimension_id, [])
            relevance = dimension_relevance([a.relevance for a in attrs])
            abstained = relevance < _RELEVANCE_FLOOR or not attrs
            kept = [] if abstained else attrs[:5]
            state_hint = (
                StateHint(state=kept[0].state, confidence=uncertainty.overall)
                if kept
                else StateHint(state=StatePole.UNCLEAR, confidence=uncertainty.overall)
            )
            evidence = list(result.evidence_by_dimension.get(dimension_id, []))[:3]
            signals.append(
                DimensionalSignal(
                    request_id=ctx.request_id,
                    layer=self.code,
                    layer_version=self.version,
                    dimension_id=dimension_id,
                    relevance=round(0.0 if abstained else relevance, 4),
                    confidence=uncertainty.overall,
                    uncertainty=uncertainty,
                    attribute_scores=kept,
                    state_hint=state_hint,
                    evidence=evidence,
                    abstained=abstained,
                    provenance=provenance,
                )
            )
        return signals


def _build_primary_provider(settings: Settings) -> object:
    from ..infrastructure.llm.bedrock_provider import BedrockLLMProvider, NullLLMProvider

    if not settings.enable_llm_primary:
        return NullLLMProvider()
    try:
        provider = BedrockLLMProvider(
            region_name=settings.aws_region,
            read_timeout_s=settings.llm_primary_timeout_s + 10.0,
        )
        logger.info(
            "NAR LLM-primary enabled (Bedrock model_id=%s, timeout=%.0fs)",
            settings.bedrock_model_id,
            settings.llm_primary_timeout_s,
        )
        return provider
    except Exception as exc:  # noqa: BLE001
        if settings.llm_strict:
            raise ModelUnavailable(
                f"NAR llm_primary but Bedrock could not initialize: {exc}"
            ) from exc
        logger.error(
            "NAR LLM-primary provider failed (%s: %s); will abstain on failure",
            type(exc).__name__,
            exc,
        )
        return NullLLMProvider()


def build_default_narrative_arc_layer() -> NarrativeArcLayer:
    """Wire the narrative-arc orchestrator into the use case (DI composition root)."""
    from ..infrastructure.kg.concept_registry import build_concept_registry
    from ..infrastructure.kg.dimension_registry import build_dimension_registry
    from ..infrastructure.kg.scorer_registry import build_scorer_registry
    from ..infrastructure.kg.triplet_registry import build_narrative_triplet_vocabulary
    from .safety_shell import SafetyShell

    settings = Settings.load()
    concept_registry = build_concept_registry(layer_code=LAYER_CODE)
    scorer_registry = build_scorer_registry(layer_code=LAYER_CODE)
    dimension_registry = build_dimension_registry()
    triplet_vocabulary = build_narrative_triplet_vocabulary()
    provider = _build_primary_provider(settings)

    safety_shell = SafetyShell(relevance_floor=settings.abstain_relevance_floor)
    orchestrator = NarrativeArcOrchestrator(
        provider=provider,  # type: ignore[arg-type]
        concept_registry=concept_registry,
        scorer_registry=scorer_registry,
        safety_shell=safety_shell,
        model_id=settings.bedrock_model_id,
        timeout_s=settings.llm_primary_timeout_s,
        max_tokens=settings.llm_primary_max_tokens,
        triplet_vocabulary=triplet_vocabulary,
        dimension_registry=dimension_registry,
        layer_code=LAYER_CODE,
    )
    return NarrativeArcLayer(orchestrator)
