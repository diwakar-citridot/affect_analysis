"""EmotionHypothesisGenerator (§5.0): derive emotion hypotheses off the field + patterns.

Emotion is never primary — these are *hypotheses* read from the reconstructed field, with
lexical emotion evidence folded in only as one supporting term.
"""

from __future__ import annotations

from ..domain.enums import Durability, EvidenceKind, ExperientialPatternType, FieldAxis
from ..domain.models import (
    AffectiveField,
    EmotionEvidence,
    EmotionHypothesis,
    Evidence,
    ExperientialPattern,
    SemanticAffectFeatures,
)
from ..domain.scoring import clip

# label -> field axes that most support it (for explainability)
_SUPPORT_AXES: dict[str, list[FieldAxis]] = {
    "joy": [FieldAxis.CORE_VALENCE, FieldAxis.CORE_VITALITY],
    "love": [FieldAxis.CORE_VALENCE, FieldAxis.REL_ATTACHMENT],
    "amusement": [FieldAxis.CORE_VALENCE, FieldAxis.CORE_AROUSAL],
    "deflection": [FieldAxis.MOT_APPROACH, FieldAxis.CORE_AROUSAL, FieldAxis.REL_ATTACHMENT],
    "sadness": [FieldAxis.CORE_VALENCE, FieldAxis.CORE_AROUSAL, FieldAxis.CORE_VITALITY],
    "grief": [FieldAxis.CORE_VALENCE, FieldAxis.REL_ATTACHMENT],
    "anger": [FieldAxis.CORE_VALENCE, FieldAxis.CORE_AROUSAL, FieldAxis.MOT_APPROACH],
    "fear": [FieldAxis.CORE_VALENCE, FieldAxis.CORE_AROUSAL, FieldAxis.MOT_AVOIDANCE],
    "anxiety": [FieldAxis.MOT_AVOIDANCE, FieldAxis.TMP_ANTICIPATION],
    "determination": [FieldAxis.MOT_APPROACH, FieldAxis.MOT_AGENCY, FieldAxis.CORE_VITALITY],
    "enthusiasm": [FieldAxis.MOT_APPROACH, FieldAxis.CORE_VITALITY],
    "hope": [FieldAxis.TMP_ANTICIPATION, FieldAxis.MOT_APPROACH],
    "serenity": [FieldAxis.REG_REGULATION, FieldAxis.CORE_AROUSAL],
    "calm": [FieldAxis.REG_REGULATION, FieldAxis.CORE_AROUSAL],
    "disgust": [FieldAxis.CORE_VALENCE, FieldAxis.MOT_AVOIDANCE],
    "moral_aversion": [FieldAxis.MOT_AVOIDANCE, FieldAxis.REG_REGULATION],
    "surprise": [FieldAxis.CORE_AROUSAL],
    "wonder": [FieldAxis.CORE_AROUSAL, FieldAxis.CORE_VALENCE],
    "anticipation": [FieldAxis.TMP_ANTICIPATION],
}

# experiential pattern -> labels it tends to support
_PATTERN_AFFINITY: dict[ExperientialPatternType, set[str]] = {
    ExperientialPatternType.WITHDRAWAL: {"sadness", "fear", "disgust", "moral_aversion"},
    ExperientialPatternType.OPENNESS: {"joy", "love", "hope", "amusement", "wonder", "deflection"},
    ExperientialPatternType.STRIVING: {"determination", "enthusiasm", "hope", "anticipation"},
    ExperientialPatternType.AVOIDANCE: {"fear", "anxiety", "disgust", "anticipation", "moral_aversion", "anger"},
    ExperientialPatternType.RUMINATION: {"sadness", "anxiety"},
    ExperientialPatternType.HYPERVIGILANCE: {"fear", "anxiety", "surprise", "anticipation"},
    ExperientialPatternType.SURRENDER: {"serenity", "calm", "sadness"},
    ExperientialPatternType.RESISTANCE: {"anger", "determination", "surprise"},
    ExperientialPatternType.ATTACHMENT: {"love", "grief"},
    ExperientialPatternType.DETACHMENT: {"calm", "sadness", "moral_aversion"},
}

_LEXICAL_TO_LABELS: dict[str, list[str]] = {
    "joy": ["joy", "amusement"],
    "deflection": ["deflection"],
    "love": ["love"],
    "trust": ["love"],
    "sadness": ["sadness", "grief"],
    "fear": ["fear", "anxiety"],
    "anger": ["anger"],
    "disgust": ["disgust"],
    "moral_aversion": ["moral_aversion"],
    "surprise": ["surprise", "wonder"],
    "wonder": ["wonder"],
    "anticipation": ["anticipation", "hope"],
    "calm": ["calm", "serenity"],
}


_SEMANTIC_HYP_WEIGHT = 0.85


class EmotionHypothesisGenerator:
    def generate(
        self,
        field: AffectiveField,
        patterns: list[ExperientialPattern],
        lexical: EmotionEvidence,
        *,
        semantic: SemanticAffectFeatures | None = None,
        top_k: int = 6,
    ) -> list[EmotionHypothesis]:
        v = field.core.valence.value
        a = field.core.arousal.value
        vit = field.core.vitality.value
        app = field.motivation.approach.value
        avo = field.motivation.avoidance.value
        ag = field.motivation.agency.value
        reg = field.regulation.regulation.value
        per = field.regulation.persistence.value
        cont = field.temporal.continuity.value
        ant = field.temporal.anticipation.value
        att = field.relational.attachment.value
        intensity = field.core.intensity.value
        vol = field.regulation.volatility.value
        pos, neg = max(0.0, v), max(0.0, -v)
        equilibrium = 1.0 - abs(v)

        visceral_disgust = neg * (0.45 + 0.55 * avo) * (0.5 + 0.5 * (1.0 - app))
        aversion_disgust = avo * (0.5 + 0.5 * (1.0 - app)) * (0.3 + 0.4 * neg + 0.3 * equilibrium)
        disgust_score = max(visceral_disgust, aversion_disgust)

        raw: dict[str, float] = {
            "joy": pos * (0.5 + 0.5 * a) * (0.5 + 0.5 * vit),
            "love": pos * (0.4 + 0.6 * att),
            "amusement": pos * (0.4 + 0.6 * a),
            "deflection": 0.15
            * app
            * (0.35 + 0.65 * a)
            * (0.40 + 0.30 * equilibrium + 0.20 * max(0.0, v) + 0.15 * att),
            "sadness": neg * (0.6 + 0.4 * (1.0 - a)),
            "grief": neg * (0.4 + 0.6 * att) * (0.5 + 0.5 * (1.0 - a)),
            "anger": neg * a * (0.4 + 0.6 * app) + neg * a * avo * 0.45 * (1.0 - app),
            "fear": neg * a * (0.4 + 0.6 * avo) + a * ant * 0.32 * (0.15 + 0.85 * avo + max(0.0, neg)),
            "anxiety": neg * (0.4 + 0.6 * ant) * (0.4 + 0.6 * avo),
            "determination": pos * (0.3 + 0.7 * app) * (0.4 + 0.6 * ag),
            "enthusiasm": pos * (0.4 + 0.6 * app) * (0.4 + 0.6 * vit),
            "hope": (0.4 + 0.6 * ant) * (0.4 + 0.6 * app) * (0.4 + 0.3 * pos),
            "serenity": (1.0 - abs(v)) * (1.0 - a) * (0.4 + 0.6 * reg),
            "calm": (1.0 - a) * (0.4 + 0.6 * reg) * (0.5 + 0.5 * (1.0 - neg)),
            "disgust": disgust_score,
            "moral_aversion": (0.4 + 0.6 * avo)
            * (0.5 + 0.5 * (1.0 - app))
            * (0.35 + 0.35 * reg + 0.3 * equilibrium)
            * (0.55 + 0.45 * (1.0 - a)),
            "surprise": a
            * (0.4 + 0.6 * intensity)
            * (0.45 + 0.55 * vol)
            * (0.4 + 0.6 * (1.0 - per)),
            "wonder": pos * a * (0.35 + 0.65 * vit) * (0.4 + 0.6 * max(0.0, v)),
            "anticipation": 0.15 + 0.7 * ant,
        }

        # fold lexical evidence as a supporting term
        for emo, prob in lexical.probs.items():
            boost = 0.62 if prob >= 0.5 else 0.45
            for label in _LEXICAL_TO_LABELS.get(emo, []):
                raw[label] = raw.get(label, 0.0) + boost * prob

        if semantic and semantic.hypothesis_probs:
            for label, prob in semantic.hypothesis_probs.items():
                raw[label] = raw.get(label, 0.0) + _SEMANTIC_HYP_WEIGHT * prob

        sadness_lex = lexical.probs.get("sadness", 0.0)
        hope_lex = lexical.probs.get("anticipation", 0.0)
        if sadness_lex >= 0.22 and ag < 0.58:
            raw["sadness"] = raw.get("sadness", 0.0) + 0.42 * sadness_lex
            if hope_lex >= 0.15:
                raw["hope"] = raw.get("hope", 0.0) + 0.18 * hope_lex
            raw["hope"] = raw.get("hope", 0.0) * 0.50

        joy_lex = lexical.probs.get("joy", 0.0)
        calm_lex = lexical.probs.get("calm", 0.0)
        if calm_lex >= 0.25:
            raw["calm"] = raw.get("calm", 0.0) + 0.42 * calm_lex
            raw["sadness"] = raw.get("sadness", 0.0) * 0.55
        if sadness_lex >= 0.25 and joy_lex >= 0.2 and vit < 0.52:
            raw["joy"] = raw.get("joy", 0.0) + 0.28 * joy_lex
            raw["calm"] = raw.get("calm", 0.0) + 0.24 * sadness_lex

        if v >= 0.12 and vit < 0.48 and intensity >= 0.52:
            depletion = (0.5 - vit) + sadness_lex * 0.35
            raw["calm"] = raw.get("calm", 0.0) + 0.32 * depletion
            raw["sadness"] = raw.get("sadness", 0.0) + 0.22 * depletion

        if avo >= 0.42 and app < 0.28 and neg >= 0.15:
            raw["anger"] = raw.get("anger", 0.0) + 0.28 * avo * (1.0 - app)

        ant_lex = lexical.probs.get("anticipation", 0.0)
        if ant_lex >= 0.3 and a >= 0.45:
            raw["anticipation"] = raw.get("anticipation", 0.0) + 0.35 * ant_lex

        # pattern reinforcement
        present = {p.type: p.strength.value for p in patterns}
        for ptype, strength in present.items():
            for label in _PATTERN_AFFINITY.get(ptype, set()):
                raw[label] = raw.get(label, 0.0) + 0.25 * strength

        positive = {k: val for k, val in raw.items() if val > 0.05}
        if not positive:
            return []
        total = sum(positive.values())
        probs = {k: val / total for k, val in positive.items()}
        ranked = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        renorm = sum(p for _, p in ranked) or 1.0

        enduring = per >= 0.55 or cont >= 0.55
        hypotheses: list[EmotionHypothesis] = []
        for label, p in ranked:
            prob = p / renorm
            sup_axes = _SUPPORT_AXES.get(label, [])
            sup_pats = [pt for pt in present if label in _PATTERN_AFFINITY.get(pt, set())]
            durability = (
                Durability.ENDURING
                if (enduring and label in {"sadness", "love", "serenity", "fear", "moral_aversion"})
                else Durability.TRANSIENT
            )
            conf = clip(0.3 + 0.5 * field.uncertainty.confidence.value + 0.2 * prob)
            hypotheses.append(
                EmotionHypothesis(
                    label=label,
                    probability=round(prob, 4),
                    durability=durability,
                    supporting_axes=sup_axes,
                    supporting_patterns=sup_pats,
                    evidence=[
                        Evidence(
                            kind=EvidenceKind.EMOTION,
                            detail=f"hypothesis '{label}' from field axes "
                            f"{[a.value for a in sup_axes]}",
                            source="hypotheses",
                            weight=round(conf, 4),
                        )
                    ],
                )
            )
        return hypotheses
