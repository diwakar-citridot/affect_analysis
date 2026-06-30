"""GunaScorer (§5.5): field-native Triguṇa scoring for D2.

Reads agitation / heaviness / equanimity from the reconciled affective field,
experiential patterns, and trajectory — not from emotion-hypothesis bridges.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..domain.enums import Durability, EvidenceKind, FieldAxis
from ..domain.models import (
    AffectiveField,
    AffectTrajectory,
    AttributeScore,
    Evidence,
    ExperientialPattern,
)
from ..domain.scoring import (
    axis_activation,
    dimension_relevance,
    saturate,
    select_d2_pole,
    softmax,
)
from ..infrastructure.kg.concept_registry import canonical_slug
from .field_builder import AXIS_META


@dataclass(frozen=True)
class GunaScoreResult:
    """D2 scoring output: attribute scores, softmax weights for modulation, evidence."""

    attributes: list[AttributeScore]
    modulation_weights: dict[str, float]
    evidence: list[Evidence]
    raw_scores: dict[str, float]


class GunaScorer:
    def __init__(
        self,
        synthesis_path: Path,
        poles_path: Path,
        *,
        allowed_slugs: frozenset[str] | None = None,
    ) -> None:
        synth = json.loads(Path(synthesis_path).read_text(encoding="utf-8"))
        poles = json.loads(Path(poles_path).read_text(encoding="utf-8"))
        self.version: str = synth["version"]
        self.dimension_id: int = int(synth["dimension_id"])
        self._gunas: dict[str, dict] = synth["gunas"]
        self._pole_rules: dict[str, str] = poles["attributes"]
        self._allowed_slugs = allowed_slugs

    def score(
        self,
        field: AffectiveField,
        patterns: list[ExperientialPattern],
        trajectory: AffectTrajectory | None = None,
    ) -> GunaScoreResult:
        pattern_map = {p.type.value: p.strength.value for p in patterns}
        traj_persistence = trajectory.persistence if trajectory else 0.0
        traj_volatility = trajectory.volatility if trajectory else 0.0

        raw: dict[str, float] = {}
        contributors: dict[str, list[str]] = {g: [] for g in self._gunas}

        for guna, spec in self._gunas.items():
            total = 0.0
            for axis_key, cfg in spec.get("axes", {}).items():
                lo, hi, neutral = AXIS_META.get(axis_key, (0.0, 1.0, 0.5))
                feat = field.feature(FieldAxis(axis_key))
                act = axis_activation(
                    feat.value, lo, hi, neutral, cfg.get("direction", "high")
                )
                contrib = cfg["weight"] * act
                if contrib > 0.02:
                    contributors[guna].append(f"{axis_key}({feat.value:.2f})")
                total += contrib
            for ptype, weight in spec.get("patterns", {}).items():
                strength = pattern_map.get(ptype, 0.0)
                contrib = weight * strength
                if contrib > 0.02:
                    contributors[guna].append(f"pattern:{ptype}({strength:.2f})")
                total += contrib
            for tkey, weight in spec.get("trajectory", {}).items():
                tval = traj_persistence if tkey == "persistence" else traj_volatility
                contrib = weight * tval
                if contrib > 0.02:
                    contributors[guna].append(f"trajectory.{tkey}({tval:.2f})")
                total += contrib
            raw[guna] = total

        modulation_weights = softmax(raw)
        relevances = {g: round(saturate(v), 4) for g, v in raw.items()}

        arousal = field.core.arousal.value
        intensity = field.core.intensity.value
        regulation = field.regulation.regulation.value
        approach = field.motivation.approach.value
        persistence = field.regulation.persistence.value
        vitality = field.core.vitality.value
        agency = field.motivation.agency.value

        attributes: list[AttributeScore] = []
        for guna, rel in relevances.items():
            if self._allowed_slugs is not None and guna not in self._allowed_slugs:
                continue
            slug = canonical_slug(guna)
            rule = self._pole_rules.get(slug, self._pole_rules.get(guna, "intensity"))
            pole = select_d2_pole(
                slug,
                rule,
                arousal=arousal,
                intensity=intensity,
                regulation=regulation,
                approach=approach,
                persistence=persistence,
                vitality=vitality,
                agency=agency,
            )
            attributes.append(
                AttributeScore(
                    attribute=slug,
                    relevance=rel,
                    state=pole,
                    dimension_id=self.dimension_id,
                    durability=Durability.ENDURING,
                )
            )
        attributes.sort(key=lambda a: a.relevance, reverse=True)

        evidence = self._build_evidence(contributors, attributes)
        return GunaScoreResult(
            attributes=attributes,
            modulation_weights=modulation_weights,
            evidence=evidence,
            raw_scores=raw,
        )

    @staticmethod
    def _build_evidence(
        contributors: dict[str, list[str]],
        attributes: list[AttributeScore],
    ) -> list[Evidence]:
        out: list[Evidence] = []
        for attr in attributes[:3]:
            parts = contributors.get(attr.attribute, [])
            detail = f"{attr.attribute} <- " + ", ".join(parts[:4]) if parts else attr.attribute
            out.append(
                Evidence(
                    kind=EvidenceKind.AXIS,
                    detail=detail,
                    source="guna_scorer",
                    weight=attr.relevance,
                )
            )
        return out

    def dimension_relevance(self, result: GunaScoreResult) -> float:
        return dimension_relevance([a.relevance for a in result.attributes])


class GunaFamilyModulator:
    """Loads ``guna_families.v1.json`` and applies §5.5 modulation to bridge scores."""

    def __init__(self, families_path: Path) -> None:
        data = json.loads(Path(families_path).read_text(encoding="utf-8"))
        self.version: str = data["version"]
        self._family_to_guna: dict[str, str] = data["family_to_guna"]
        attr_families: dict[str, str] = {}
        for family, attrs in data["families"].items():
            for attr in attrs:
                attr_families[canonical_slug(attr)] = family
        self._attr_families = attr_families

    def apply(
        self,
        attrs: list[AttributeScore],
        modulation_weights: dict[str, float],
        *,
        beta: float = 0.3,
    ) -> list[AttributeScore]:
        from ..domain.scoring import apply_guna_modulation

        return apply_guna_modulation(
            attrs,
            modulation_weights,
            self._attr_families,
            self._family_to_guna,
            beta=beta,
        )
