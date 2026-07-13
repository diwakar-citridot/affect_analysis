"""FastAPI application factory for AFF v2 (LLM-primary only).

Run standalone v2 API::

    PYTHONPATH=src uvicorn svarupa_affect.api.app_v2:app --reload --port 8001

Combined v1+v2 on one server (v2 under ``/v2``)::

    PYTHONPATH=src uvicorn svarupa_affect.api.app:app --reload --port 8000

Endpoints are at the root on ``app_v2``: ``GET /health``, ``GET /affect/meta``,
``POST /affect/analyze``, ``GET /affect/fyi/meta``, ``POST /affect/fyi``,
``GET /narrative-arc/meta``, ``POST /narrative-arc/analyze``,
``GET /psycholinguistic/meta``, ``POST /psycholinguistic/analyze``,
``GET /metaphor/meta``, ``POST /metaphor/analyze``.
On the combined app: ``GET /v2/health``, ``GET /v2/affect/meta``, ``POST /v2/affect/analyze``,
``GET /v2/affect/fyi/meta``, ``POST /v2/affect/fyi``,
``GET /v2/narrative-arc/meta``, ``POST /v2/narrative-arc/analyze``,
``GET /v2/psycholinguistic/meta``, ``POST /v2/psycholinguistic/analyze``,
``GET /v2/metaphor/meta``, ``POST /v2/metaphor/analyze``.
"""

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
from .routes_v2 import router


def create_v2_app() -> FastAPI:
    app = FastAPI(
        title="Svarupa AFF v2 — LLM-Native Lived Experience",
        description=(
            "Layer 1 (AFF) v2: scores free-text lived experience onto closed KG vocabulary "
            "(D2 Triguṇa, D8 Sthāyībhāvas, D9 Vyabhicārībhāvas) via a single Bedrock call."
        ),
        version=__version__,
    )
    app.include_router(router)

    @app.on_event("startup")
    def _warm_v2() -> None:
        setup_console_logging()
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


app = create_v2_app()
