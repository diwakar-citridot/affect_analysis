"""Reduced-confidence fallback path (§4.3, §7.1).

On validation/model failure, build a degraded AffectiveField from VAD only (valence/arousal
and coarse derivations), at a hard-capped confidence. The field still builds — the layer never
crashes and never fabricates rich structure it cannot support.
"""

from __future__ import annotations

from ...domain.enums import EvidenceKind, FieldAxis
from ...domain.models import (
    AffectiveField,
    CoreAffect,
    Evidence,
    FieldUncertainty,
    Motivation,
    ReconstructedFeature,
    Regulation,
    Relational,
    Temporal,
    VAD,
)
from ...domain.scoring import clip

_CAP = 0.4  # fallback confidence is hard-capped


def _f(value: float, conf: float = _CAP) -> ReconstructedFeature:
    return ReconstructedFeature(
        value=round(value, 4),
        confidence=round(min(conf, _CAP), 4),
        evidence=[
            Evidence(
                kind=EvidenceKind.AXIS,
                detail="lexical fallback (VAD only)",
                source="lexical_fallback",
                weight=_CAP,
            )
        ],
    )


def build_fallback_field(vad: VAD, coverage: float) -> AffectiveField:
    v, a, d = vad.valence, vad.arousal, vad.dominance
    conf = min(_CAP, 0.2 + 0.4 * coverage)
    field = AffectiveField(
        core=CoreAffect(
            valence=_f(v, conf),
            arousal=_f(a, conf),
            vitality=_f(clip(0.5 + 0.4 * v), conf),
            intensity=_f(clip((abs(v) + a) / 2.0), conf),
        ),
        motivation=Motivation(
            agency=_f(0.5),
            approach=_f(clip(max(0.0, v))),
            avoidance=_f(clip(max(0.0, -v))),
            control=_f(d, conf),
        ),
        regulation=Regulation(
            stability=_f(0.5), persistence=_f(0.4), volatility=_f(0.3), regulation=_f(0.5)
        ),
        relational=Relational(attachment=_f(0.4), trust=_f(0.5), social_orientation=_f(0.0)),
        temporal=Temporal(continuity=_f(0.5), anticipation=_f(0.4), resolution=_f(0.45)),
        uncertainty=FieldUncertainty(
            ambiguity=_f(0.5), confidence=_f(conf), evidence_quality=_f(clip(0.3 * coverage))
        ),
        axis_coverage={
            FieldAxis.CORE_VALENCE: round(coverage, 4),
            FieldAxis.CORE_AROUSAL: round(coverage, 4),
        },
        contributions={},
        evidence=[
            Evidence(
                kind=EvidenceKind.FIELD,
                detail="degraded fallback field",
                source="lexical_fallback",
                weight=_CAP,
            )
        ],
    )
    return field
