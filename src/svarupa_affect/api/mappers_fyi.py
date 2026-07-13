"""Mappers for AFF FYI / Short Note API."""

from __future__ import annotations

from .. import __version__
from ..application.fyi_orchestrator import FyiCard, FyiResult, FyiSignalInput
from ..domain.enums import StatePole
from .dtos_fyi import FyiCardDTO, FyiFormulateRequest, FyiFormulateResponse
from .dtos_v2 import TokenUsageDTO


def to_fyi_signals(req: FyiFormulateRequest) -> list[FyiSignalInput]:
    return [
        FyiSignalInput(
            attribute=sig.attribute.strip(),
            relevance=float(sig.relevance),
            state=sig.state.value,
            dimension_name=sig.dimension_name.strip(),
            durability=sig.durability.value,
            rationale=sig.rationale.strip(),
            reasoning=sig.reasoning.strip(),
            span=sig.span.strip(),
        )
        for sig in req.signals
    ]


def to_fyi_response(
    *,
    request_id: str,
    prompt_version: str,
    result: FyiResult,
) -> FyiFormulateResponse:
    return FyiFormulateResponse(
        request_id=request_id,
        layer_version=__version__,
        prompt_version=prompt_version,
        llm_used=result.used,
        llm_attempted=result.attempted,
        llm_failure=result.failure if (result.attempted and not result.used) else None,
        cards=[_card_to_dto(c) for c in result.cards],
        usage=TokenUsageDTO(**(result.usage or {})),
    )


def _card_to_dto(card: FyiCard) -> FyiCardDTO:
    try:
        status = StatePole(card.status)
    except ValueError:
        status = StatePole.UNCLEAR
    return FyiCardDTO(
        text=card.text,
        simple_sentence=card.simple_sentence,
        reasoning=card.reasoning,
        attribute=card.attribute,
        dimension=card.dimension,
        status=status,
        expandable=True,
    )
