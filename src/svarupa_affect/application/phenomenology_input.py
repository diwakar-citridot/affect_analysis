"""PhenomenologyInputAssembler (§3.4.1): build the single curated public output.

Internal AFF objects are never exposed directly; this assembles the one versioned,
provenance-stamped contract the Phenomenology layer consumes.
"""

from __future__ import annotations

from ..domain.models import (
    AffectDriver,
    AffectInteraction,
    AffectiveField,
    AffectTrajectory,
    AppraisalProfile,
    EmotionHypothesis,
    EvidenceSummary,
    ExperientialPattern,
    ForegroundEpisode,
    PhenomenologyInput,
    Provenance,
    UncertaintyProfile,
)
from ..domain.scoring import clip


class PhenomenologyInputAssembler:
    def assemble(
        self,
        *,
        request_id: str,
        layer_version: str,
        background_field: AffectiveField,
        appraisal: AppraisalProfile,
        episodes: list[ForegroundEpisode],
        trajectory: AffectTrajectory,
        interactions: list[AffectInteraction],
        drivers: list[AffectDriver],
        patterns: list[ExperientialPattern],
        hypotheses: list[EmotionHypothesis],
        uncertainty: UncertaintyProfile,
        provenance: Provenance,
    ) -> PhenomenologyInput:
        summary = self._evidence_summary(background_field, appraisal, episodes)
        return PhenomenologyInput(
            request_id=request_id,
            layer_version=layer_version,
            background_field=background_field,
            foreground_episodes=episodes,
            appraisal=appraisal,
            trajectory=trajectory,
            interactions=interactions,
            drivers=drivers,
            experiential_patterns=patterns,
            emotion_hypotheses=hypotheses,
            uncertainty=uncertainty,
            evidence_summary=summary,
            provenance=provenance,
        )

    @staticmethod
    def _evidence_summary(
        field: AffectiveField,
        appraisal: AppraisalProfile,
        episodes: list[ForegroundEpisode],
    ) -> EvidenceSummary:
        groups = (
            field.core,
            field.motivation,
            field.regulation,
            field.relational,
            field.temporal,
            field.uncertainty,
        )
        confidences: list[float] = []
        for g in groups:
            for name in type(g).model_fields:
                feat = getattr(g, name)
                confidences.append(feat.confidence)
        for name in type(appraisal).model_fields:
            val = getattr(appraisal, name)
            if hasattr(val, "confidence"):
                confidences.append(val.confidence)

        spans = [ep.span for ep in episodes][:10]
        coverage = (
            sum(field.axis_coverage.values()) / len(field.axis_coverage)
            if field.axis_coverage
            else 0.0
        )
        return EvidenceSummary(
            spans=spans,
            n_features=len(confidences),
            mean_feature_confidence=(
                round(clip(sum(confidences) / len(confidences)), 4) if confidences else 0.0
            ),
            coverage=round(clip(coverage), 4),
            quality=round(field.uncertainty.evidence_quality.value, 4),
        )
