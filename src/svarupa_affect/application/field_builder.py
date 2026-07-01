"""AffectiveFieldBuilder (§4.2): fuse signal sources into the hierarchical AffectiveField.

Builds two views — a BackgroundField (climate over the whole text) and per-sentence
ForegroundEpisode field snapshots. Every axis becomes a ReconstructedFeature carrying its
own value + confidence + evidence; axis_coverage and contributions are recorded.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..domain.enums import EvidenceKind, FieldAxis
from ..domain.models import (
    AffectiveField,
    CoreAffect,
    CueBundle,
    EmotionEvidence,
    Evidence,
    FieldUncertainty,
    Motivation,
    ReconstructedFeature,
    Regulation,
    Relational,
    SharedFeatures,
    SemanticAffectFeatures,
    Temporal,
    VAD,
)
from ..domain.ports import ILexicalAffect, ILinguisticCues, ISemanticAffectEncoder, IVADModel
from ..domain.scoring import clip
from ..infrastructure.affect.lexicons import sentences

# axis -> (lo, hi, neutral_default)
AXIS_META: dict[str, tuple[float, float, float]] = {
    "core.valence": (-1.0, 1.0, 0.0),
    "core.arousal": (0.0, 1.0, 0.35),
    "core.vitality": (0.0, 1.0, 0.5),
    "core.intensity": (0.0, 1.0, 0.3),
    "motivation.agency": (0.0, 1.0, 0.5),
    "motivation.approach": (0.0, 1.0, 0.4),
    "motivation.avoidance": (0.0, 1.0, 0.3),
    "motivation.control": (0.0, 1.0, 0.5),
    "regulation.stability": (0.0, 1.0, 0.5),
    "regulation.persistence": (0.0, 1.0, 0.4),
    "regulation.volatility": (0.0, 1.0, 0.3),
    "regulation.regulation": (0.0, 1.0, 0.5),
    "relational.attachment": (0.0, 1.0, 0.4),
    "relational.trust": (0.0, 1.0, 0.5),
    "relational.social_orientation": (-1.0, 1.0, 0.0),
    "temporal.continuity": (0.0, 1.0, 0.5),
    "temporal.anticipation": (0.0, 1.0, 0.4),
    "temporal.resolution": (0.0, 1.0, 0.45),
}

_POS_EMO = ("joy", "love", "trust", "anticipation")
_NEG_EMO = ("sadness", "fear", "anger", "disgust", "moral_aversion")


@dataclass(frozen=True)
class FieldSignals:
    """Raw per-text source outputs, kept for appraisal / uncertainty / hypotheses."""

    vad: VAD
    vad_coverage: float
    lexical: EmotionEvidence
    lexical_coverage: float
    cues: CueBundle
    semantic: SemanticAffectFeatures


def _vad_signal(axis: str, vad: VAD) -> float | None:
    v, a, d = vad.valence, vad.arousal, vad.dominance
    return {
        "core.valence": v,
        "core.arousal": a,
        "core.intensity": clip((abs(v) + a) / 2.0),
        "core.vitality": clip(0.5 + 0.4 * v),
        "motivation.approach": clip(max(0.0, v)),
        "motivation.avoidance": clip(max(0.0, -v)),
        "motivation.control": d,
    }.get(axis)


def _lexical_signal(axis: str, ev: EmotionEvidence) -> float | None:
    if not ev.probs:
        return None
    pos = sum(ev.probs.get(e, 0.0) for e in _POS_EMO)
    neg = sum(ev.probs.get(e, 0.0) for e in _NEG_EMO)
    joy = ev.probs.get("joy", 0.0) + ev.probs.get("love", 0.0) + ev.probs.get("anticipation", 0.0)
    activating = (
        ev.probs.get("fear", 0.0)
        + ev.probs.get("anger", 0.0)
        + ev.probs.get("surprise", 0.0)
        + ev.probs.get("anticipation", 0.0)
    )
    return {
        "core.valence": clip(pos - neg, -1.0, 1.0),
        "core.intensity": clip(max(ev.probs.values())),
        "core.vitality": clip(0.5 + 0.5 * (joy - ev.probs.get("sadness", 0.0))),
        "core.arousal": clip(activating),
    }.get(axis)


def _cue_signal(axis: str, cues: CueBundle) -> float | None:
    attr = axis.split(".", 1)[1]
    val = cues.scores.get(attr)
    if axis == "motivation.avoidance":
        moral = cues.scores.get("moral_aversion")
        if moral is not None:
            val = max(val or 0.0, moral)
    return val


def _temporal_signal(axis: str, shared: SharedFeatures | None) -> float | None:
    if not shared or not shared.temporal_cues:
        return None
    tc = {c.lower() for c in shared.temporal_cues}
    ongoing = any(k in tc for k in ("ongoing", "always", "recurring", "chronic"))
    future = any(k in tc for k in ("future", "anticipated", "upcoming"))
    return {
        "temporal.continuity": 0.75 if ongoing else 0.4,
        "temporal.anticipation": 0.7 if future else None,
        "regulation.persistence": 0.7 if ongoing else None,
    }.get(axis)


def _phe_signal(axis: str, shared: SharedFeatures | None) -> float | None:
    """Reuse PHE valence/arousal when present (shared feature cache, not authority)."""
    if not shared:
        return None
    return {
        "core.valence": shared.valence,
        "core.arousal": shared.arousal,
    }.get(axis)


def _semantic_signal(axis: str, semantic: SemanticAffectFeatures) -> float | None:
    val = semantic.axis_scores.get(axis)
    if val is None:
        return None
    if axis == "core.valence":
        return clip(2.0 * val - 1.0, -1.0, 1.0)
    return clip(val)


class AffectiveFieldBuilder:
    def __init__(
        self,
        vad: IVADModel,
        lexical: ILexicalAffect,
        cues: ILinguisticCues,
        semantic: ISemanticAffectEncoder,
        synthesis_path: Path,
    ) -> None:
        self._vad = vad
        self._lexical = lexical
        self._cues = cues
        self._semantic = semantic
        data = json.loads(Path(synthesis_path).read_text(encoding="utf-8"))
        self.version: str = data["version"]
        self._weights: dict[str, dict[str, float]] = data["axes"]

    async def signals_for(self, text: str, history: list[dict[str, str]]) -> FieldSignals:
        vad, vad_cov = await self._vad.score(text)
        lex, lex_cov = await self._lexical.signals(text)
        cues = await self._cues.cues(text, history)
        semantic = await self._semantic.encode(text)
        return FieldSignals(
            vad=vad,
            vad_coverage=vad_cov,
            lexical=lex,
            lexical_coverage=lex_cov,
            cues=cues,
            semantic=semantic,
        )

    def field_from_signals(
        self, sig: FieldSignals, shared: SharedFeatures | None
    ) -> AffectiveField:
        feats: dict[str, ReconstructedFeature] = {}
        axis_coverage: dict[FieldAxis, float] = {}
        contributions: dict[FieldAxis, dict[str, float]] = {}
        field_evidence: list[Evidence] = []

        src_cov = {
            "vad": sig.vad_coverage,
            "lexical": sig.lexical_coverage,
            "cues": sig.cues.coverage,
            "semantic": sig.semantic.coverage,
            "temporal": 1.0 if (shared and shared.temporal_cues) else 0.0,
            "phe": 1.0 if (shared and (shared.valence is not None or shared.arousal is not None)) else 0.0,
        }

        for axis, weights in self._weights.items():
            lo, hi, default = AXIS_META[axis]
            num = 0.0
            wsum = 0.0
            fired_cov = 0.0
            total_w = sum(weights.values()) or 1.0
            contrib: dict[str, float] = {}

            for source, w in weights.items():
                val = self._source_signal(source, axis, sig, shared)
                if val is None:
                    continue
                num += w * val
                wsum += w
                fired_cov += w * src_cov.get(source, 0.0)
                contrib[source] = round(w * val, 4)

            if wsum > 0:
                value = clip(num / wsum, lo, hi)
                coverage = clip(fired_cov / total_w)
            else:
                value, coverage = default, 0.0

            confidence = clip(0.3 + 0.6 * coverage)
            ev = [
                Evidence(
                    kind=EvidenceKind.AXIS,
                    detail=f"{axis} <- {', '.join(contrib) or 'prior'}",
                    source="field_builder",
                    weight=round(coverage, 4),
                )
            ]
            feats[axis] = ReconstructedFeature(
                value=round(value, 4), confidence=round(confidence, 4), evidence=ev
            )
            fa = FieldAxis(axis)
            axis_coverage[fa] = round(coverage, 4)
            if contrib:
                contributions[fa] = contrib

        # add the field's own uncertainty facet (derived from coverage + source spread)
        mean_cov = sum(axis_coverage.values()) / len(axis_coverage)
        ambiguity = self._ambiguity(sig)
        unc_conf = round(clip(0.3 + 0.6 * mean_cov), 4)

        def _unc(axis: str, value: float) -> ReconstructedFeature:
            return ReconstructedFeature(
                value=round(value, 4),
                confidence=unc_conf,
                evidence=[
                    Evidence(
                        kind=EvidenceKind.AXIS,
                        detail=f"{axis} <- field coverage",
                        source="field_builder",
                        weight=round(mean_cov, 4),
                    )
                ],
            )

        feats["uncertainty.ambiguity"] = _unc("uncertainty.ambiguity", ambiguity)
        feats["uncertainty.confidence"] = _unc("uncertainty.confidence", mean_cov)
        feats["uncertainty.evidence_quality"] = _unc(
            "uncertainty.evidence_quality", clip(0.5 * mean_cov + 0.5 * max(src_cov.values()))
        )
        for cue_ev in sig.cues.evidence:
            field_evidence.append(cue_ev)
        field_evidence.extend(sig.semantic.evidence)

        return AffectiveField(
            core=CoreAffect(
                valence=feats["core.valence"],
                arousal=feats["core.arousal"],
                vitality=feats["core.vitality"],
                intensity=feats["core.intensity"],
            ),
            motivation=Motivation(
                agency=feats["motivation.agency"],
                approach=feats["motivation.approach"],
                avoidance=feats["motivation.avoidance"],
                control=feats["motivation.control"],
            ),
            regulation=Regulation(
                stability=feats["regulation.stability"],
                persistence=feats["regulation.persistence"],
                volatility=feats["regulation.volatility"],
                regulation=feats["regulation.regulation"],
            ),
            relational=Relational(
                attachment=feats["relational.attachment"],
                trust=feats["relational.trust"],
                social_orientation=feats["relational.social_orientation"],
            ),
            temporal=Temporal(
                continuity=feats["temporal.continuity"],
                anticipation=feats["temporal.anticipation"],
                resolution=feats["temporal.resolution"],
            ),
            uncertainty=FieldUncertainty(
                ambiguity=feats["uncertainty.ambiguity"],
                confidence=feats["uncertainty.confidence"],
                evidence_quality=feats["uncertainty.evidence_quality"],
            ),
            axis_coverage=axis_coverage,
            contributions=contributions,
            evidence=field_evidence,
        )

    @staticmethod
    def _source_signal(
        source: str, axis: str, sig: FieldSignals, shared: SharedFeatures | None
    ) -> float | None:
        if source == "vad":
            return _vad_signal(axis, sig.vad)
        if source == "lexical":
            return _lexical_signal(axis, sig.lexical)
        if source == "cues":
            return _cue_signal(axis, sig.cues)
        if source == "semantic":
            if not sig.semantic.hypothesis_probs:
                return None
            return _semantic_signal(axis, sig.semantic)
        if source == "temporal":
            return _temporal_signal(axis, shared)
        if source == "phe":
            return _phe_signal(axis, shared)
        return None

    @staticmethod
    def _ambiguity(sig: FieldSignals) -> float:
        """Field ambiguity: low lexical/semantic margin + co-present approach/avoidance."""
        lex_margin = 1.0 - sig.lexical.margin if sig.lexical.probs else 0.4
        sem_margin = 1.0 - sig.semantic.margin if sig.semantic.hypothesis_probs else 0.4
        margin_term = 0.5 * lex_margin + 0.5 * sem_margin
        appr = sig.cues.scores.get("approach", 0.0)
        avoid = max(
            sig.cues.scores.get("avoidance", 0.0),
            sig.semantic.axis_scores.get("motivation.avoidance", 0.0),
        )
        conflict = min(appr, avoid)
        return clip(0.5 * margin_term + 0.5 * conflict * 2.0)
