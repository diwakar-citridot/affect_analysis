"""FastAPI edge for the AFF layer.

The ASGI apps live in:

- ``svarupa_affect.api.app`` — v1 + v2 (``POST /analyze``, ``POST /v2/affect/analyze``,
  ``POST /v2/narrative-arc/analyze``, ``POST /v2/psycholinguistic/analyze``,
  ``POST /v2/metaphor/analyze``)
- ``svarupa_affect.api.app_v2`` — v2 LLM-primary only

Run::

    uvicorn svarupa_affect.api.app:app --reload
    uvicorn svarupa_affect.api.app_v2:app --reload --port 8001
"""
