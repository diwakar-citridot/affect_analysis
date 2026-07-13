"""LLM-primary FYI / Short Note orchestration (AFF).

One Bedrock call turns up to three pre-scored AFF signals into Stage-1 Short
Notes per the Response Formulation Spec v8. Failures degrade gracefully — never
fabricate cards on invalid LLM output.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from ..domain.exceptions import ModelUnavailable
from ..domain.ports import IDimensionRegistry, ILLMProvider, ITripletVocabulary
from ..infrastructure.kg.concept_registry import canonical_slug
from ..infrastructure.llm.prompts import fyi_short_note_v2 as prompt_mod

logger = logging.getLogger("svarupa_affect.fyi")

_GROUNDING_MAXLEN = prompt_mod._GROUNDING_MAXLEN  # noqa: SLF001


@dataclass(frozen=True)
class FyiSignalInput:
    """One scored AFF signal ready for Short Note formulation."""

    attribute: str
    relevance: float
    state: str
    dimension_name: str
    durability: str = "unknown"
    rationale: str = ""
    span: str = ""
    reasoning: str = ""


@dataclass(frozen=True)
class FyiCard:
    text: str
    simple_sentence: str
    reasoning: str
    attribute: str
    dimension: str
    status: str


@dataclass(frozen=True)
class FyiResult:
    cards: list[FyiCard]
    used: bool = False
    attempted: bool = False
    failure: str | None = None
    usage: dict[str, int] = field(default_factory=dict)


class FyiOrchestrator:
    def __init__(
        self,
        provider: ILLMProvider,
        *,
        dimension_registry: IDimensionRegistry,
        triplet_vocabulary: ITripletVocabulary | None = None,
        model_id: str,
        timeout_s: float = 45.0,
        max_tokens: int = 2048,
    ) -> None:
        self._provider = provider
        self._dimensions = dimension_registry
        self._triplets = triplet_vocabulary
        self.model_id = model_id
        self.prompt_version = prompt_mod.PROMPT_VERSION
        self._timeout = timeout_s
        self._max_tokens = max_tokens

    async def formulate(
        self,
        signals: list[FyiSignalInput],
        *,
        analysis_text: str,
        request_id: str | None = None,
        user_state_tier: str = "standard",
    ) -> FyiResult:
        if not signals:
            return FyiResult(cards=[], failure="no signals provided")
        if not analysis_text.strip():
            return FyiResult(cards=[], failure="analysis_text is required")
        if len(signals) > prompt_mod._MAX_CARDS:  # noqa: SLF001
            return FyiResult(
                cards=[],
                failure=f"at most {prompt_mod._MAX_CARDS} signals per request",  # noqa: SLF001
            )

        enriched = [self._enrich_signal(s) for s in signals]
        system = prompt_mod.build_system()
        user_prompt = prompt_mod.build_prompt(
            analysis_text=analysis_text,
            signals=enriched,
            user_state_tier=user_state_tier,
        )

        logger.info(
            "FYI formulation starting request_id=%s prompt_version=%s model_id=%s signals=%d",
            request_id,
            self.prompt_version,
            self.model_id,
            len(signals),
        )

        usage: dict[str, int] = {}
        last_error: str | None = None
        for attempt in range(3):
            metrics: dict[str, int] = {}
            try:
                raw = await self._provider.complete_json(
                    system=system,
                    prompt=user_prompt,
                    schema=prompt_mod.FYI_SCHEMA,
                    model_id=self.model_id,
                    temperature=0.2,
                    timeout_s=self._timeout,
                    max_tokens=self._max_tokens,
                    request_id=request_id,
                    attempt=attempt + 1,
                    metrics=metrics,
                )
                validated = prompt_mod.validate_fyi(
                    raw,
                    expected_count=len(signals),
                    analysis_text=analysis_text,
                    signals=enriched,
                )
                cards = self._cards_from_payload(validated, signals)
                self._add_usage(usage, metrics)
                return FyiResult(cards=cards, used=True, attempted=True, usage=usage)
            except (prompt_mod.FyiValidationError, ModelUnavailable) as exc:
                self._add_usage(usage, metrics)
                last_error = str(exc)
                logger.warning("FYI invalid payload (attempt %d/3): %s", attempt + 1, exc)
                if isinstance(exc, ModelUnavailable):
                    return FyiResult(
                        cards=[],
                        attempted=True,
                        failure=last_error,
                        usage=usage,
                    )
                base_prompt = prompt_mod.build_prompt(
                    analysis_text=analysis_text,
                    signals=enriched,
                    user_state_tier=user_state_tier,
                )
                user_prompt = (
                    f"{base_prompt}\n\n"
                    f"PREVIOUS RESPONSE WAS INVALID: {last_error}\n"
                    f"{prompt_mod.correction_hint(last_error)}\n"
                    'Return corrected JSON with key "cards" — one object per signal, same order.'
                )
                continue

        return FyiResult(
            cards=[],
            attempted=True,
            failure=last_error or "LLM returned no valid payload",
            usage=usage,
        )

    # -- helpers ----------------------------------------------------------------------

    def _enrich_signal(self, signal: FyiSignalInput) -> dict[str, object]:
        slug = canonical_slug(signal.attribute)
        dim_id = self._dimensions.id_for_name(signal.dimension_name)
        state_key = signal.state.lower()
        grounding = ""
        if self._triplets is not None and dim_id is not None:
            states = self._triplets.status_descriptions(dim_id, slug)
            grounding = (states.get(state_key) or states.get("balance") or "")[:_GROUNDING_MAXLEN]
        return {
            "triplet": {
                "dimension": signal.dimension_name,
                "attribute": signal.attribute,
                "state": state_key,
            },
            "dimension_register": prompt_mod.dimension_register(signal.dimension_name),
            "state_pole_hint": prompt_mod.state_pole_hint(state_key),
            "attribute": signal.attribute,
            "relevance": round(float(signal.relevance), 4),
            "state": state_key,
            "dimension": signal.dimension_name,
            "durability": signal.durability,
            "rationale": signal.rationale[:400],
            "reasoning": signal.reasoning[:400],
            "span": signal.span[:200],
            "grounding_for_state": grounding,
        }

    @staticmethod
    def _cards_from_payload(validated: dict, signals: list[FyiSignalInput]) -> list[FyiCard]:
        cards: list[FyiCard] = []
        for idx, item in enumerate(validated["cards"]):
            src = signals[idx]
            cards.append(
                FyiCard(
                    text=str(item["text"]),
                    simple_sentence=str(item["simple_sentence"]),
                    reasoning=str(item["reasoning"]),
                    attribute=str(item.get("attribute") or src.attribute),
                    dimension=str(item.get("dimension") or src.dimension_name),
                    status=str(item.get("status") or src.state).lower(),
                )
            )
        return cards

    @staticmethod
    def _add_usage(dst: dict[str, int], src: dict[str, int] | None) -> None:
        if not src:
            return
        for key, val in src.items():
            dst[key] = dst.get(key, 0) + int(val or 0)
