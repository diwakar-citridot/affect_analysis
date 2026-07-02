"""FastAPI edge for the AFF layer.

The ASGI apps live in:

- ``svarupa_affect.api.app`` — v1 + v2 (``POST /analyze``, ``POST /v2/analyze``)
- ``svarupa_affect.api.app_v2`` — v2 LLM-primary only

Run::

    uvicorn svarupa_affect.api.app:app --reload
    uvicorn svarupa_affect.api.app_v2:app --reload --port 8001
"""
