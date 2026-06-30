"""FastAPI router (§2.2 api/routes.py): POST /analyze -> AnalyzeRequest -> AnalyzeResponse."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..application.analyze_affect import AffectLayer
from ..application.mappers import to_context, to_response
from .dependencies import get_dimension_registry, get_layer
from .dtos import AnalyzeRequest, AnalyzeResponse

router = APIRouter(tags=["affect"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "layer": "AFF"}


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    request: AnalyzeRequest,
    layer: AffectLayer = Depends(get_layer),
    dimension_registry=Depends(get_dimension_registry),
) -> AnalyzeResponse:
    """Reconstruct the affective field for one expression and return the public surface."""
    ctx = to_context(request)
    result = await layer.analyze_full(ctx)
    return to_response(result, dimension_registry)
