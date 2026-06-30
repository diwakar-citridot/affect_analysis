"""ExperientialPatternRecognizer (§5.0): recognise the lived stance between field and emotion.

Matches field regions against versioned signatures in ``patterns.v1.json``. A pattern fires
when all its axis conditions hold; its ``strength`` reflects how deep into the activating
region the field sits, and confidence aggregates the supporting features' confidences.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..domain.enums import EvidenceKind, ExperientialPatternType, FieldAxis
from ..domain.models import AffectiveField, Evidence, ExperientialPattern, ReconstructedFeature
from ..domain.scoring import clip
from .field_builder import AXIS_META


class ExperientialPatternRecognizer:
    def __init__(self, patterns_path: Path) -> None:
        data = json.loads(Path(patterns_path).read_text(encoding="utf-8"))
        self.version: str = data["version"]
        self._patterns: list[dict] = data["patterns"]

    def recognize(self, field: AffectiveField) -> list[ExperientialPattern]:
        out: list[ExperientialPattern] = []
        for spec in self._patterns:
            conditions: dict[str, list[float]] = spec["conditions"]
            memberships: list[float] = []
            confidences: list[float] = []
            ok = True
            for axis_key, (lo, hi) in conditions.items():
                feat = field.feature(FieldAxis(axis_key))
                v = feat.value
                if not (lo <= v <= hi):
                    ok = False
                    break
                memberships.append(self._membership(axis_key, v, lo, hi))
                confidences.append(feat.confidence)
            if not ok or not memberships:
                continue

            strength_val = clip(sum(memberships) / len(memberships))
            conf = clip(sum(confidences) / len(confidences))
            supporting = [FieldAxis(a) for a in spec.get("supporting_axes", list(conditions))]
            out.append(
                ExperientialPattern(
                    type=ExperientialPatternType(spec["type"]),
                    strength=ReconstructedFeature(
                        value=round(strength_val, 4),
                        confidence=round(conf, 4),
                        evidence=[
                            Evidence(
                                kind=EvidenceKind.FIELD,
                                detail=f"pattern '{spec['type']}' from {', '.join(conditions)}",
                                source="patterns",
                                weight=round(strength_val, 4),
                            )
                        ],
                    ),
                    supporting_axes=supporting,
                )
            )
        out.sort(key=lambda p: p.strength.value, reverse=True)
        return out

    @staticmethod
    def _membership(axis_key: str, value: float, lo: float, hi: float) -> float:
        """How deep into the activating side of the band the value sits."""
        a_lo, a_hi, _ = AXIS_META[axis_key]
        neutral = 0.0 if a_lo < 0 else 0.5
        band_center = (lo + hi) / 2.0
        t = clip((value - lo) / (hi - lo)) if hi > lo else 1.0
        return 1.0 - t if band_center < neutral else t
