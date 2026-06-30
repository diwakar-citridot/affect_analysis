"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from .. import __version__
from ..infrastructure.logging_config import setup_console_logging
from .dependencies import get_dimension_registry, get_layer
from .routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Svarupa AFF — Multi-Axis Affect Analysis",
        description="Layer 1 (AFF): field-first affective reconstruction of lived experience.",
        version=__version__,
    )
    app.include_router(router)

    @app.on_event("startup")
    def _warm_layer() -> None:
        """Rebuild the composition root so .env / Settings changes apply after restart."""
        setup_console_logging()
        get_layer.cache_clear()
        get_layer()
        get_dimension_registry.cache_clear()
        get_dimension_registry()

    return app


app = create_app()
