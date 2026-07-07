"""FastAPI dependency wiring (§2.2 api/dependencies.py).

The AffectLayer (with its adapters) is built once and injected via ``Depends``.
"""

from __future__ import annotations

from functools import lru_cache

from ..application.analyze_affect import AffectLayer, build_default_layer
from ..application.analyze_metaphor import MetaphorLayer, build_default_metaphor_layer
from ..infrastructure.kg.concept_registry import StaticConceptRegistry, build_concept_registry
from ..infrastructure.kg.dimension_registry import StaticDimensionRegistry, build_dimension_registry


@lru_cache(maxsize=1)
def get_layer() -> AffectLayer:
    """Composition root: build (and cache) the wired AffectLayer."""
    return build_default_layer()


@lru_cache(maxsize=1)
def get_metaphor_layer() -> MetaphorLayer:
    """Composition root: build (and cache) the wired MetaphorLayer (MET)."""
    return build_default_metaphor_layer()


@lru_cache(maxsize=1)
def get_dimension_registry() -> StaticDimensionRegistry:
    """Cached dimension name registry (MySQL when configured, else static seed)."""
    return build_dimension_registry()


@lru_cache(maxsize=1)
def get_concept_registry() -> StaticConceptRegistry:
    """Cached AFF concept registry (MySQL ``svarupa_concept_layer`` when configured)."""
    return build_concept_registry()
