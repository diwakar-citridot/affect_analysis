"""Svarupa Assistant — Layer 1: Multi-Axis Affect Analysis (AFF).

Field-first reconstruction of the affective organization of lived experience.
This package implements the design in ``documentation/design/aff_layer_design.md`` (v2.1).
"""

__version__ = "2.1.0"
LAYER_CODE = "AFF"

# Deprecated: use ``build_concept_registry().affinity()`` or ``AffectLayer.affinity``.
# Mirrors ``data/kg/aff_concept_layer.v1.json`` (export of svarupa_concept_layer).
AFFINITY = frozenset({2, 8, 9, 15, 19, 21, 22, 24})


def get_affinity() -> frozenset[int]:
    """AFF dimension affinity from ``svarupa_concept_layer`` (MySQL) or static fallback."""
    from .infrastructure.kg.concept_registry import build_concept_registry

    return build_concept_registry().affinity()
