"""AffectDynamicsAnalyzer (§5.7): reconstruct dynamics, trajectory and interactions.

The foreground episodes form the ordered trajectory; transitions between consecutive
episode fields are classified into DynamicsPattern. Coexisting affects are emitted as
first-class AffectInteraction objects (matched against interaction templates).
"""

from __future__ import annotations

import json
from pathlib import Path

from ..domain.enums import DynamicsPattern, EvidenceKind
from ..domain.models import (
    AffectDynamics,
    AffectInteraction,
    AffectiveField,
    AffectTrajectory,
    EmotionHypothesis,
    Evidence,
    FieldTransition,
    ForegroundEpisode,
)
from ..domain.scoring import clip


def _episode_label(field: AffectiveField) -> str:
    v = field.core.valence.value
    a = field.core.arousal.value
    if v > 0.15:
        return "positive"
    if v < -0.15 and a >= 0.5:
        return "negative-aroused"
    if v < -0.15:
        return "heavy/low"
    return "neutral"


def _classify(v1: float, a1: float, v2: float, a2: float) -> DynamicsPattern:
    dv, da = v2 - v1, a2 - a1
    if dv <= -0.2 and da >= 0.1:
        return DynamicsPattern.ESCALATION
    if dv >= 0.2 and da <= 0.0:
        return DynamicsPattern.RESOLUTION
    if dv >= 0.2:
        return DynamicsPattern.RECOVERY
    if dv <= -0.2:
        return DynamicsPattern.COLLAPSE
    return DynamicsPattern.STABLE


class AffectDynamicsAnalyzer:
    def __init__(self, interactions_path: Path) -> None:
        data = json.loads(Path(interactions_path).read_text(encoding="utf-8"))
        self.version: str = data["version"]
        self._templates: list[dict] = data["templates"]

    def analyze(
        self,
        background: AffectiveField,
        episodes: list[ForegroundEpisode],
        hypotheses: list[EmotionHypothesis],
    ) -> tuple[AffectDynamics, AffectTrajectory, list[AffectInteraction]]:
        valences = [ep.field.core.valence.value for ep in episodes]
        transitions: list[FieldTransition] = []
        dv_signs: list[int] = []

        for i in range(len(episodes) - 1):
            f1, f2 = episodes[i].field, episodes[i + 1].field
            pat = _classify(
                f1.core.valence.value,
                f1.core.arousal.value,
                f2.core.valence.value,
                f2.core.arousal.value,
            )
            transitions.append(
                FieldTransition(
                    from_label=_episode_label(f1),
                    to_label=_episode_label(f2),
                    pattern=pat,
                    span=episodes[i + 1].span,
                )
            )
            dv = f2.core.valence.value - f1.core.valence.value
            dv_signs.append(1 if dv > 0.05 else (-1 if dv < -0.05 else 0))

        reversals = sum(
            1
            for i in range(len(dv_signs) - 1)
            if dv_signs[i] != 0 and dv_signs[i + 1] != 0 and dv_signs[i] != dv_signs[i + 1]
        )
        turning_points = [
            i + 1
            for i in range(len(dv_signs) - 1)
            if dv_signs[i] != 0 and dv_signs[i + 1] != 0 and dv_signs[i] != dv_signs[i + 1]
        ]
        volatility = self._volatility(valences)
        persistence = background.regulation.persistence.value

        patterns = sorted({t.pattern for t in transitions}, key=lambda p: p.value)
        if reversals >= 2:
            patterns.append(DynamicsPattern.OSCILLATION)
        if not patterns:
            patterns = [
                DynamicsPattern.PERSISTENCE if persistence >= 0.55 else DynamicsPattern.STABLE
            ]

        trajectory = AffectTrajectory(
            sequence=episodes,
            transitions=transitions,
            turning_points=turning_points,
            persistence=round(persistence, 4),
            reversals=reversals,
            volatility=round(volatility, 4),
        )
        dynamics = AffectDynamics(patterns=patterns, transitions=transitions)
        interactions = self._interactions(hypotheses)
        return dynamics, trajectory, interactions

    @staticmethod
    def _volatility(valences: list[float]) -> float:
        if len(valences) < 2:
            return 0.0
        mean = sum(valences) / len(valences)
        var = sum((x - mean) ** 2 for x in valences) / len(valences)
        return clip(var**0.5)

    def _interactions(self, hypotheses: list[EmotionHypothesis]) -> list[AffectInteraction]:
        probs = {h.label: h.probability for h in hypotheses if h.probability > 0.1}
        out: list[AffectInteraction] = []
        for tpl in self._templates:
            comps = tpl["components"]
            if all(c in probs for c in comps):
                strength = clip(min(probs[c] for c in comps) * 2.0)
                out.append(
                    AffectInteraction(
                        components=tuple(comps),
                        is_tension=bool(tpl["is_tension"]),
                        strength=round(strength, 4),
                        description=tpl["description"],
                        evidence=[
                            Evidence(
                                kind=EvidenceKind.INTERACTION,
                                detail=f"coexisting {comps[0]} + {comps[1]}",
                                source="dynamics",
                                weight=round(strength, 4),
                            )
                        ],
                    )
                )
        out.sort(key=lambda x: x.strength, reverse=True)
        return out
