"""FastAPI router for AFF v2 — LLM-native lived-experience analysis.

Mounted at ``/v2`` on the main app, or at the root on ``app_v2``.

Affect endpoints live under ``/v2/affect/*``; narrative arc under ``/v2/narrative-arc/*``;
psycholinguistic under ``/v2/psycholinguistic/*``; metaphor under ``/v2/metaphor/*``.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from .. import __version__
from ..application.analyze_affect import AffectLayer
from ..application.analyze_metaphor import MetaphorLayer
from ..application.analyze_narrative_arc import NarrativeArcLayer
from ..application.analyze_psycholinguistic import PsycholinguisticLayer
from ..application.formulate_fyi import FyiLayer
from ..domain.exceptions import ModelUnavailable
from ..infrastructure.config import Settings
from ..infrastructure.kg.scorer_registry import build_scorer_registry
from ..infrastructure.llm.prompts.fyi_short_note_v2 import PROMPT_VERSION as FYI_PROMPT_VERSION
from ..infrastructure.llm.prompts.lived_experience_v1 import PROMPT_VERSION
from ..infrastructure.llm.prompts.metaphor_v1 import PROMPT_VERSION as MET_PROMPT_VERSION
from ..infrastructure.llm.prompts.narrative_arc_v1 import PROMPT_VERSION as NAR_PROMPT_VERSION
from ..infrastructure.llm.prompts.psycholinguistic_v1 import PROMPT_VERSION as PSY_PROMPT_VERSION
from .dependencies import (
    get_dimension_registry,
    get_fyi_layer,
    get_layer,
    get_metaphor_layer,
    get_narrative_arc_layer,
    get_psycholinguistic_layer,
)
from .dtos_fyi import FyiFormulateRequest, FyiFormulateResponse, FyiMetaResponse
from .dtos_metaphor import (
    MetaphorAnalyzeRequest,
    MetaphorAnalyzeResponse,
    MetaphorMetaResponse,
)
from .dtos_narrative_arc import (
    NarrativeArcAnalyzeRequest,
    NarrativeArcAnalyzeResponse,
    NarrativeArcMetaResponse,
)
from .dtos_psycholinguistic import (
    PsycholinguisticAnalyzeRequest,
    PsycholinguisticAnalyzeResponse,
    PsycholinguisticMetaResponse,
)
from .dtos_v2 import (
    LivedExperienceAnalyzeRequest,
    LivedExperienceAnalyzeResponse,
    LivedExperienceMetaResponse,
)
from .mappers_fyi import to_fyi_response, to_fyi_signals
from .mappers_metaphor import to_metaphor_context, to_metaphor_response
from .mappers_narrative_arc import to_narrative_context, to_narrative_response
from .mappers_psycholinguistic import to_psycholinguistic_context, to_psycholinguistic_response
from .mappers_v2 import to_v2_context, to_v2_response

router = APIRouter(tags=["v2"])
affect_router = APIRouter(prefix="/affect", tags=["affect-v2"])
narrative_router = APIRouter(prefix="/narrative-arc", tags=["narrative-arc-v2"])
psycholinguistic_router = APIRouter(prefix="/psycholinguistic", tags=["psycholinguistic-v2"])
metaphor_router = APIRouter(prefix="/metaphor", tags=["metaphor-v2"])


@router.get("/health")
async def health_v2() -> dict[str, str]:
    return {"status": "ok", "layer": "AFF", "affect_mode": "llm_primary"}


@affect_router.get("/health")
async def affect_health_v2() -> dict[str, str]:
    return {"status": "ok", "layer": "AFF", "affect_mode": "llm_primary"}


@affect_router.get("/meta", response_model=LivedExperienceMetaResponse)
async def meta_v2() -> LivedExperienceMetaResponse:
    """Capabilities and pinned prompt version for v2 AFF clients."""
    settings = Settings.load()
    registry = build_scorer_registry()
    return LivedExperienceMetaResponse(
        prompt_version=PROMPT_VERSION,
        api_version=__version__,
        emit_dimensions=sorted(registry.emit_dimensions()),
        bedrock_model_configured=bool(settings.aws_region and settings.enable_llm_primary),
    )


@affect_router.post("/analyze", response_model=LivedExperienceAnalyzeResponse)
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


@affect_router.get("/fyi/meta", response_model=FyiMetaResponse)
async def fyi_meta_v2() -> FyiMetaResponse:
    """Capabilities and pinned prompt version for AFF FYI / Short Note clients."""
    settings = Settings.load()
    return FyiMetaResponse(
        prompt_version=FYI_PROMPT_VERSION,
        api_version=__version__,
        bedrock_model_configured=bool(settings.aws_region and settings.enable_llm_primary),
    )


@affect_router.post("/fyi", response_model=FyiFormulateResponse)
async def formulate_fyi_cards(
    request: FyiFormulateRequest,
    layer: FyiLayer = Depends(get_fyi_layer),
) -> FyiFormulateResponse:
    """Formulate up to three AFF Short Notes from pre-scored signals."""
    signals = to_fyi_signals(request)
    try:
        result = await layer.formulate(
            signals,
            analysis_text=request.analysis_text,
            request_id=request.request_id,
            user_state_tier=request.user_state_tier,
        )
    except ModelUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "fyi_formulation_unavailable",
                "message": str(exc),
                "hint": "Configure AWS_REGION and boto3, or set SVARUPA_LLM_STRICT=0.",
            },
        ) from exc
    if result.attempted and not result.used:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "fyi_formulation_failed",
                "message": result.failure or "LLM returned no valid Short Note payload",
            },
        )
    return to_fyi_response(
        request_id=request.request_id,
        prompt_version=layer.prompt_version,
        result=result,
    )


@narrative_router.get("/meta", response_model=NarrativeArcMetaResponse)
async def narrative_meta_v2(
    layer: NarrativeArcLayer = Depends(get_narrative_arc_layer),
) -> NarrativeArcMetaResponse:
    """Capabilities and pinned prompt version for NAR v2 clients."""
    settings = Settings.load()
    return NarrativeArcMetaResponse(
        prompt_version=NAR_PROMPT_VERSION,
        api_version=__version__,
        emit_dimensions=sorted(layer.emit_dimensions),
        bedrock_model_configured=bool(settings.aws_region and settings.enable_llm_primary),
    )


@narrative_router.post("/analyze", response_model=NarrativeArcAnalyzeResponse)
async def analyze_narrative_arc(
    request: NarrativeArcAnalyzeRequest,
    layer: NarrativeArcLayer = Depends(get_narrative_arc_layer),
    dimension_registry=Depends(get_dimension_registry),
) -> NarrativeArcAnalyzeResponse:
    """Read lived experience as narrative arc onto NAR primary dimensions."""
    ctx = to_narrative_context(request)
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
    return to_narrative_response(result, ctx, dimension_registry)


@psycholinguistic_router.get("/meta", response_model=PsycholinguisticMetaResponse)
async def psycholinguistic_meta_v2(
    layer: PsycholinguisticLayer = Depends(get_psycholinguistic_layer),
) -> PsycholinguisticMetaResponse:
    """Capabilities and pinned prompt version for PSY v2 clients."""
    settings = Settings.load()
    return PsycholinguisticMetaResponse(
        prompt_version=PSY_PROMPT_VERSION,
        api_version=__version__,
        emit_dimensions=sorted(layer.emit_dimensions),
        bedrock_model_configured=bool(settings.aws_region and settings.enable_llm_primary),
    )


@psycholinguistic_router.post("/analyze", response_model=PsycholinguisticAnalyzeResponse)
async def analyze_psycholinguistic(
    request: PsycholinguisticAnalyzeRequest,
    layer: PsycholinguisticLayer = Depends(get_psycholinguistic_layer),
    dimension_registry=Depends(get_dimension_registry),
) -> PsycholinguisticAnalyzeResponse:
    """Read lived experience as linguistic form onto PSY primary dimensions."""
    ctx = to_psycholinguistic_context(request)
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
    return to_psycholinguistic_response(result, ctx, dimension_registry)


@metaphor_router.get("/meta", response_model=MetaphorMetaResponse)
async def metaphor_meta_v2(
    layer: MetaphorLayer = Depends(get_metaphor_layer),
) -> MetaphorMetaResponse:
    """Capabilities and pinned prompt version for MET v2 clients."""
    settings = Settings.load()
    return MetaphorMetaResponse(
        prompt_version=MET_PROMPT_VERSION,
        api_version=__version__,
        emit_dimensions=sorted(layer.emit_dimensions),
        bedrock_model_configured=bool(settings.aws_region and settings.enable_llm_primary),
    )


@metaphor_router.post("/analyze", response_model=MetaphorAnalyzeResponse)
async def analyze_metaphor(
    request: MetaphorAnalyzeRequest,
    layer: MetaphorLayer = Depends(get_metaphor_layer),
    dimension_registry=Depends(get_dimension_registry),
) -> MetaphorAnalyzeResponse:
    """Detect metaphors and map their source imagery onto MET primary dimensions."""
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


router.include_router(affect_router)
router.include_router(narrative_router)
router.include_router(psycholinguistic_router)
router.include_router(metaphor_router)
