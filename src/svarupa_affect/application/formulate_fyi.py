"""FyiLayer (use case): formulate AFF Short Notes from pre-scored signals."""

from __future__ import annotations

import logging

from .. import __version__
from ..domain.exceptions import ModelUnavailable
from ..infrastructure.config import Settings
from .fyi_orchestrator import FyiOrchestrator, FyiResult, FyiSignalInput

logger = logging.getLogger("svarupa_affect.fyi_layer")

LAYER_CODE = "AFF"


class FyiLayer:
    code: str = LAYER_CODE
    version: str = __version__

    def __init__(self, orchestrator: FyiOrchestrator) -> None:
        self._orchestrator = orchestrator

    @property
    def prompt_version(self) -> str:
        return self._orchestrator.prompt_version

    async def formulate(
        self,
        signals: list[FyiSignalInput],
        *,
        analysis_text: str,
        request_id: str,
        user_state_tier: str = "standard",
    ) -> FyiResult:
        return await self._orchestrator.formulate(
            signals,
            analysis_text=analysis_text,
            request_id=request_id,
            user_state_tier=user_state_tier,
        )


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
            "FYI LLM enabled (Bedrock model_id=%s, timeout=%.0fs)",
            settings.bedrock_model_id,
            settings.llm_primary_timeout_s,
        )
        return provider
    except Exception as exc:  # noqa: BLE001
        if settings.llm_strict:
            raise ModelUnavailable(
                f"FYI formulation requires Bedrock but provider could not initialize: {exc}"
            ) from exc
        logger.error(
            "FYI LLM provider failed (%s: %s); will abstain on failure",
            type(exc).__name__,
            exc,
        )
        return NullLLMProvider()


def build_default_fyi_layer() -> FyiLayer:
    """Wire the FYI orchestrator into the use case (the DI composition root)."""
    from ..infrastructure.kg.dimension_registry import build_dimension_registry
    from ..infrastructure.kg.triplet_registry import build_triplet_vocabulary

    settings = Settings.load()
    provider = _build_primary_provider(settings)
    orchestrator = FyiOrchestrator(
        provider=provider,  # type: ignore[arg-type]
        dimension_registry=build_dimension_registry(),
        triplet_vocabulary=build_triplet_vocabulary(),
        model_id=settings.bedrock_model_id,
        timeout_s=min(settings.llm_primary_timeout_s, 45.0),
        max_tokens=min(settings.llm_primary_max_tokens, 2048),
    )
    return FyiLayer(orchestrator)
