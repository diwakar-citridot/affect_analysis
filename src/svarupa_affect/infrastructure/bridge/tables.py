"""IBridgeTable adapter (§4.4).

Loads the versioned ``hyp2sthayi.v2.json`` (D8) and ``hyp2vyabhi.v2.json`` (D9) bridge
tables and maps emotion hypotheses onto Rasa attribute scores, honouring ``field_guard``
regions, ``prefer`` (enduring/transient) and ``pole_rule``.
"""

from __future__ import annotations

import json
from pathlib import Path

from ...domain.enums import Durability, FieldAxis, StatePole
from ...domain.models import AffectiveField, AttributeScore, EmotionHypothesis
from ...domain.scoring import saturate, select_pole
from ..kg.concept_registry import canonical_slug


def _resolve_axis(field: AffectiveField, key: str) -> float:
    """Resolve a field_guard key (hierarchical axis or derived scalar) to its value."""
    aliases = {
        "persistence": field.regulation.persistence.value,
        "temporal_continuity": field.temporal_continuity,
        "motivational_conflict": field.motivational_conflict,
        "valence": field.core.valence.value,
        "arousal": field.core.arousal.value,
        "regulation": field.regulation.regulation.value,
    }
    if key in aliases:
        return aliases[key]
    try:
        return field.feature(FieldAxis(key)).value
    except (ValueError, AttributeError):
        return 0.0


def _passes_guard(field: AffectiveField, guard: dict[str, list[float]]) -> bool:
    for key, (lo, hi) in guard.items():
        v = _resolve_axis(field, key)
        if not (lo <= v <= hi):
            return False
    return True


class JsonBridgeTable:
    """Adapter implementing :class:`IBridgeTable` for one dimension's bridge file."""

    def __init__(self, path: Path, *, allowed_slugs: frozenset[str] | None = None):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.version: str = data["version"]
        self.dimension_id: int = int(data["dimension_id"])
        self._edges: list[dict] = data["edges"]
        self._allowed_slugs = allowed_slugs

    def attributes(self) -> list[str]:
        """Closed attribute vocabulary: bridge edges filtered to DB-tagged concepts."""
        raw = sorted({canonical_slug(e["attribute"]) for e in self._edges})
        if self._allowed_slugs is None:
            return raw
        return sorted(slug for slug in raw if slug in self._allowed_slugs)

    def _edge_allowed(self, attribute: str) -> bool:
        canonical = canonical_slug(attribute)
        if self._allowed_slugs is None:
            return True
        return canonical in self._allowed_slugs or attribute in self._allowed_slugs

    def _emit_slug(self, attribute: str) -> str:
        """Prefer the registry slug spelling when the raw edge attribute is tagged."""
        if self._allowed_slugs is not None and attribute in self._allowed_slugs:
            return attribute
        return canonical_slug(attribute)

    def map(
        self, hypotheses: list[EmotionHypothesis], field: AffectiveField
    ) -> list[AttributeScore]:
        # accumulate raw contribution per attribute, remembering pole rule / durability
        acc: dict[str, float] = {}
        meta: dict[str, dict] = {}
        prob = {h.label: h.probability for h in hypotheses}

        for edge in self._edges:
            hyp = edge["hypothesis"]
            if hyp not in prob:
                continue
            if prob[hyp] < 0.15:
                continue
            guard = edge.get("field_guard")
            if guard and not _passes_guard(field, guard):
                continue
            attr = edge["attribute"]
            if not self._edge_allowed(attr):
                continue
            emit_slug = self._emit_slug(attr)
            acc[emit_slug] = acc.get(emit_slug, 0.0) + edge["weight"] * prob[hyp]
            meta.setdefault(
                emit_slug,
                {
                    "pole_rule": edge.get("pole_rule", "intensity"),
                    "prefer": edge.get("prefer", "enduring"),
                },
            )

        intensity = field.core.intensity.value
        arousal = field.core.arousal.value
        regulation = field.regulation.regulation.value

        scores: list[AttributeScore] = []
        for attr, raw in acc.items():
            rel = round(saturate(raw), 4)
            rule = meta[attr]["pole_rule"]
            pole: StatePole = select_pole(rule, intensity, arousal, regulation)
            durability = (
                Durability.ENDURING if meta[attr]["prefer"] == "enduring" else Durability.TRANSIENT
            )
            scores.append(
                AttributeScore(
                    attribute=attr,
                    relevance=rel,
                    state=pole,
                    dimension_id=self.dimension_id,
                    durability=durability,
                )
            )
        scores.sort(key=lambda s: s.relevance, reverse=True)
        return scores
