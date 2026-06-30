"""FastAPI edge for the AFF layer.

The ASGI app lives in ``svarupa_affect.api.app`` (kept out of this package ``__init__`` to
avoid import cycles with the DTOs/mappers). Run it with:

    uvicorn svarupa_affect.api.app:app --reload
"""
