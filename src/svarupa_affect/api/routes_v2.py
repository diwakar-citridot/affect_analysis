"""FastAPI router for AFF v2 — LLM-native lived-experience analysis.

Mounted at ``/v2`` on the main app, or at the root on ``app_v2``.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from .. import __version__
from ..application.analyze_affect import AffectLayer
from ..application.analyze_metaphor import MetaphorLayer
from ..domain.exceptions import ModelUnavailable
from ..infrastructure.config import Settings
from ..infrastructure.kg.scorer_registry import build_scorer_registry
from ..infrastructure.llm.prompts.lived_experience_v1 import PROMPT_VERSION
from ..infrastructure.llm.prompts.metaphor_v1 import PROMPT_VERSION as MET_PROMPT_VERSION
from .dependencies import get_dimension_registry, get_layer, get_metaphor_layer
from .dtos_metaphor import (
    MetaphorAnalyzeRequest,
    MetaphorAnalyzeResponse,
    MetaphorMetaResponse,
)
from .dtos_v2 import (
    LivedExperienceAnalyzeRequest,
    LivedExperienceAnalyzeResponse,
    LivedExperienceMetaResponse,
)
from .mappers_metaphor import to_metaphor_context, to_metaphor_response
from .mappers_v2 import to_v2_context, to_v2_response

router = APIRouter(tags=["affect-v2"])


@router.get("/health")
async def health_v2() -> dict[str, str]:
    return {"status": "ok", "layer": "AFF", "affect_mode": "llm_primary"}


@router.get("/meta", response_model=LivedExperienceMetaResponse)
async def meta_v2() -> LivedExperienceMetaResponse:
    """Capabilities and pinned prompt version for v2 clients."""
    settings = Settings.load()
    registry = build_scorer_registry()
    return LivedExperienceMetaResponse(
        prompt_version=PROMPT_VERSION,
        api_version=__version__,
        emit_dimensions=sorted(registry.emit_dimensions()),
        bedrock_model_configured=bool(settings.aws_region and settings.enable_llm_primary),
    )


@router.post("/analyze", response_model=LivedExperienceAnalyzeResponse)
async def analyze_lived_experience(
    request: LivedExperienceAnalyzeRequest,
    layer: AffectLayer = Depends(get_layer),
    dimension_registry=Depends(get_dimension_registry),
) -> LivedExperienceAnalyzeResponse:
    """Score lived experience onto D2/D8/D9 via one LLM-primary Bedrock call."""
    ctx = to_v2_context(request)
    try:
        result = await layer.analyze_full(ctx)
    except ModelUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "llm_primary_unavailable",
                "message": str(exc),
                "hint": "Configure AWS_REGION and boto3, or set SVARUPA_LLM_STRICT=0.",
            },
        ) from exc
    return to_v2_response(result, dimension_registry)


@router.get("/metaphor/meta", response_model=MetaphorMetaResponse)
async def metaphor_meta_v2(
    layer: MetaphorLayer = Depends(get_metaphor_layer),
) -> MetaphorMetaResponse:
    """Capabilities and pinned prompt version for MET v2 clients."""
    settings = Settings.load()
    return MetaphorMetaResponse(
        prompt_version=MET_PROMPT_VERSION,
        api_version=__version__,
        primary_dimensions=sorted(layer.emit_dimensions),
        bedrock_model_configured=bool(settings.aws_region and settings.enable_llm_primary),
    )


@router.post("/metaphor_analyze", response_model=MetaphorAnalyzeResponse)
async def analyze_metaphor(
    request: MetaphorAnalyzeRequest,
    layer: MetaphorLayer = Depends(get_metaphor_layer),
    dimension_registry=Depends(get_dimension_registry),
) -> MetaphorAnalyzeResponse:
    """Detect metaphors and map their source imagery onto MET primary dims (D1/D5/D6/D15)."""
    ctx = to_metaphor_context(request)
    try:
        result = await layer.analyze_full(ctx)
    except ModelUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "llm_primary_unavailable",
                "message": str(exc),
                "hint": "Configure AWS_REGION and boto3, or set SVARUPA_LLM_STRICT=0.",
            },
        ) from exc
    return to_metaphor_response(result, dimension_registry)
