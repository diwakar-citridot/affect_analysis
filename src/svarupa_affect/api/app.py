"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from .. import __version__
from ..infrastructure.logging_config import setup_console_logging
from .dependencies import (
    get_dimension_registry,
    get_fyi_layer,
    get_layer,
    get_metaphor_layer,
    get_narrative_arc_layer,
    get_psycholinguistic_layer,
)
from .routes import router
from .routes_v2 import router as v2_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Svarupa AFF — Multi-Axis Affect Analysis",
        description=(
            "Layer 1 (AFF): field-first affective reconstruction of lived experience. "
            "v1: POST /analyze (legacy_deterministic by default). "
            "v2: POST /v2/affect/analyze (LLM-primary lived experience); "
            "POST /v2/narrative-arc/analyze; "
            "POST /v2/psycholinguistic/analyze; "
            "POST /v2/metaphor/analyze."
        ),
        version=__version__,
    )
    app.include_router(router)
    app.include_router(v2_router, prefix="/v2")

    @app.on_event("startup")
    def _warm_layer() -> None:
        """Rebuild the composition root so .env / Settings changes apply after restart."""
        setup_console_logging()
        from ..infrastructure.runtime_check import validate_runtime

        validate_runtime()
        get_layer.cache_clear()
        get_layer()
        get_metaphor_layer.cache_clear()
        get_metaphor_layer()
        get_fyi_layer.cache_clear()
        get_fyi_layer()
        get_narrative_arc_layer.cache_clear()
        get_narrative_arc_layer()
        get_psycholinguistic_layer.cache_clear()
        get_psycholinguistic_layer()
        get_dimension_registry.cache_clear()
        get_dimension_registry()

    return app


app = create_app()
