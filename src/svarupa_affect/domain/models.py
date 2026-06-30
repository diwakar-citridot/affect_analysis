"""Immutable domain models for the AFF layer (§3.3).

The canonical internal representation is the hierarchical :class:`AffectiveField`.
Emotion is a *derived* hypothesis over the field. The single public output is
:class:`PhenomenologyInput`; the shared fusion envelope is :class:`DimensionalSignal`.

Every reconstructed attribute is a :class:`ReconstructedFeature` bundling
``value`` + ``confidence`` + ``evidence`` (cardinal rule 7).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from .enums import (
    Durability,
    DynamicsPattern,
    EvidenceKind,
    ExperientialPatternType,
    FieldAxis,
    LatencyMode,
    MotivationalDirection,
    StatePole,
    UncertaintyType,
)
from .invariants import Core, Frozen

# --------------------------------------------------------------------------------------
# Leaf / contributor objects
# --------------------------------------------------------------------------------------


class Evidence(Frozen):
    kind: EvidenceKind
    detail: str
    span: tuple[int, int] | None = None
    source: str | None = None
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class ReconstructedFeature(Frozen):
    """value + its own confidence + evidence. No bare numbers in the hierarchy."""

    value: float
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[Evidence] = []


class VAD(Frozen):
    valence: float = Field(ge=-1.0, le=1.0)
    arousal: float = Field(ge=0.0, le=1.0)
    dominance: float = Field(ge=0.0, le=1.0)


class EmotionEvidence(Frozen):
    """Discrete-emotion probabilities — SUPPORTING evidence for the field, not a result."""

    probs: dict[str, float] = {}
    margin: float = Field(default=0.0, ge=0.0, le=1.0)


class CueBundle(Frozen):
    """Linguistic / agency / temporal / interaction / self-other cue scores (each in [-1,1])."""

    scores: dict[str, float] = {}
    coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    targets: list[str] = []
    evidence: list[Evidence] = []


class SharedFeatures(Frozen):
    """Cross-layer features reused via the per-request cache (PHE valence/arousal, NAR temporal)."""

    valence: float | None = None
    arousal: float | None = None
    temporal_cues: list[str] = []


# --------------------------------------------------------------------------------------
# The hierarchical AffectiveField
# --------------------------------------------------------------------------------------


class CoreAffect(Frozen):
    valence: ReconstructedFeature
    arousal: ReconstructedFeature
    vitality: ReconstructedFeature
    intensity: ReconstructedFeature


class Motivation(Frozen):
    agency: ReconstructedFeature
    approach: ReconstructedFeature
    avoidance: ReconstructedFeature
    control: ReconstructedFeature

    @property
    def direction(self) -> MotivationalDirection:
        a, v = self.approach.value, self.avoidance.value
        if a >= 0.45 and v >= 0.45:
            return MotivationalDirection.CONFLICTED
        if a - v > 0.15:
            return MotivationalDirection.APPROACH
        if v - a > 0.15:
            return MotivationalDirection.AVOID
        return MotivationalDirection.NEUTRAL

    @property
    def conflict(self) -> float:
        return round(min(self.approach.value, self.avoidance.value), 4)


class Regulation(Frozen):
    stability: ReconstructedFeature
    persistence: ReconstructedFeature
    volatility: ReconstructedFeature
    regulation: ReconstructedFeature


class Relational(Frozen):
    attachment: ReconstructedFeature
    trust: ReconstructedFeature
    social_orientation: ReconstructedFeature


class Temporal(Frozen):
    continuity: ReconstructedFeature
    anticipation: ReconstructedFeature
    resolution: ReconstructedFeature


class FieldUncertainty(Frozen):
    ambiguity: ReconstructedFeature
    confidence: ReconstructedFeature
    evidence_quality: ReconstructedFeature


class AffectiveField(Core):
    """The reconstructed affective organization of lived experience — hierarchical.

    Used for both the BackgroundField (climate) and each ForegroundEpisode snapshot.
    """

    core: CoreAffect
    motivation: Motivation
    regulation: Regulation
    relational: Relational
    temporal: Temporal
    uncertainty: FieldUncertainty
    axis_coverage: dict[FieldAxis, float] = {}
    contributions: dict[FieldAxis, dict[str, float]] = {}
    evidence: list[Evidence] = []

    # ---- DERIVED cross-group scalars (computed, never stored) -------------------------
    @property
    def motivational_direction(self) -> MotivationalDirection:
        return self.motivation.direction

    @property
    def motivational_conflict(self) -> float:
        return self.motivation.conflict

    @property
    def ambivalence(self) -> float:
        # co-present approach & avoidance, lifted by field ambiguity
        co = min(self.motivation.approach.value, self.motivation.avoidance.value)
        return round(min(1.0, 0.7 * co * 2.0 + 0.3 * self.uncertainty.ambiguity.value), 4)

    @property
    def emotional_complexity(self) -> float:
        return round(self.uncertainty.ambiguity.value, 4)

    @property
    def temporal_continuity(self) -> float:
        return self.temporal.continuity.value

    def feature(self, axis: FieldAxis) -> ReconstructedFeature:
        """Address any leaf feature by its hierarchical ``group.attr`` axis."""
        group_name, attr = axis.value.split(".", 1)
        group = getattr(self, group_name)
        return getattr(group, attr)


# --------------------------------------------------------------------------------------
# Why affect emerged: appraisal + drivers
# --------------------------------------------------------------------------------------


class AppraisalProfile(Core):
    novelty: ReconstructedFeature
    goal_congruence: ReconstructedFeature
    controllability: ReconstructedFeature
    expectedness: ReconstructedFeature
    responsibility: ReconstructedFeature
    certainty: ReconstructedFeature
    fairness: ReconstructedFeature
    agency: ReconstructedFeature
    evidence: list[Evidence] = []


class AffectDriver(Core):
    """Why an affect is present — reconstructed, recognition-framed, never diagnostic."""

    trigger: str
    appraisal: AppraisalProfile | None = None
    causal_factor: str | None = None
    maintaining_factor: str | None = None
    contextual_factor: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: list[Evidence] = []


# --------------------------------------------------------------------------------------
# The lived stance: experiential patterns
# --------------------------------------------------------------------------------------


class ExperientialPattern(Core):
    type: ExperientialPatternType
    strength: ReconstructedFeature
    supporting_axes: list[FieldAxis] = []
    evidence: list[Evidence] = []


# --------------------------------------------------------------------------------------
# Background vs foreground
# --------------------------------------------------------------------------------------


class ForegroundEpisode(Core):
    """A momentary affective reaction tied to a span, with its own field + drivers + patterns."""

    field: AffectiveField
    span: tuple[int, int]
    text: str = ""
    drivers: list[AffectDriver] = []
    patterns: list[ExperientialPattern] = []


# --------------------------------------------------------------------------------------
# Emotion (derived) + dynamics + interactions
# --------------------------------------------------------------------------------------


class EmotionHypothesis(Core):
    """A hypothesis read off the field (+ patterns). Never the primary representation."""

    label: str
    probability: float = Field(ge=0.0, le=1.0)
    durability: Durability = Durability.UNKNOWN
    supporting_axes: list[FieldAxis] = []
    supporting_patterns: list[ExperientialPatternType] = []
    evidence: list[Evidence] = []


class AffectInteraction(Core):
    components: tuple[str, ...]
    is_tension: bool
    strength: float = Field(ge=0.0, le=1.0)
    description: str
    evidence: list[Evidence] = []


class FieldTransition(Frozen):
    from_label: str
    to_label: str
    pattern: DynamicsPattern
    span: tuple[int, int] | None = None


class AffectDynamics(Frozen):
    patterns: list[DynamicsPattern] = []
    transitions: list[FieldTransition] = []


class AffectTrajectory(Core):
    """The ordered affective path across foreground episodes; handed downstream."""

    sequence: list[ForegroundEpisode] = []
    transitions: list[FieldTransition] = []
    turning_points: list[int] = []
    persistence: float = Field(default=0.0, ge=0.0, le=1.0)
    reversals: int = 0
    volatility: float = Field(default=0.0, ge=0.0, le=1.0)


# --------------------------------------------------------------------------------------
# Typed uncertainty + evidence summary
# --------------------------------------------------------------------------------------


class UncertaintyProfile(Core):
    components: dict[UncertaintyType, float] = {}
    overall: float = Field(default=0.0, ge=0.0, le=1.0)

    def overall_confidence(self) -> float:
        return self.overall


class EvidenceSummary(Core):
    spans: list[tuple[int, int]] = []
    n_features: int = 0
    mean_feature_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    quality: float = Field(default=0.0, ge=0.0, le=1.0)


# --------------------------------------------------------------------------------------
# Provenance
# --------------------------------------------------------------------------------------


class Provenance(Core):
    layer_version: str
    model_id: str | None = None
    prompt_version: str | None = None
    bridge_table_version: str | None = None
    field_synthesis_version: str | None = None
    appraisal_rules_version: str | None = None
    patterns_version: str | None = None
    guna_synthesis_version: str | None = None
    llm_assist_used: bool = False
    llm_assist_attempted: bool = False
    llm_assist_failure: str | None = None
    llm_assist_gate_reasons: list[str] = []
    samples: int = 0


# --------------------------------------------------------------------------------------
# Scoring leaf objects + the shared fusion envelope
# --------------------------------------------------------------------------------------


class AttributeScore(Frozen):
    attribute: str
    relevance: float = Field(ge=0.0, le=1.0)
    state: StatePole
    dimension_id: int
    durability: Durability = Durability.UNKNOWN


class StateHint(Frozen):
    state: StatePole
    confidence: float = Field(ge=0.0, le=1.0)


class DimensionalSignal(Core):
    """The shared envelope, invariant across all seven layers (fusion contract)."""

    request_id: str
    layer: str = "AFF"
    layer_version: str
    dimension_id: int
    relevance: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    uncertainty: UncertaintyProfile | None = None
    attribute_scores: list[AttributeScore] = []
    state_hint: StateHint | None = None
    evidence: list[Evidence] = []
    abstained: bool = False
    provenance: Provenance


# --------------------------------------------------------------------------------------
# THE single public output
# --------------------------------------------------------------------------------------


class PhenomenologyInput(Core):
    """The ONLY object AFF exposes to downstream consumers (esp. the Phenomenology layer)."""

    request_id: str
    layer_version: str
    background_field: AffectiveField
    foreground_episodes: list[ForegroundEpisode] = []
    appraisal: AppraisalProfile
    trajectory: AffectTrajectory
    interactions: list[AffectInteraction] = []
    drivers: list[AffectDriver] = []
    experiential_patterns: list[ExperientialPattern] = []
    emotion_hypotheses: list[EmotionHypothesis] = []
    uncertainty: UncertaintyProfile
    evidence_summary: EvidenceSummary
    provenance: Provenance


# --------------------------------------------------------------------------------------
# Input context
# --------------------------------------------------------------------------------------


class LayerContext(Frozen):
    request_id: str
    analysis_text: str = Field(min_length=1)
    locale: str = "en"
    conversation_history: list[dict[str, str]] = []
    candidate_dimensions: list[int] = []
    shared_features: SharedFeatures | None = None
    kg_context: dict[str, str] = {}
    latency_mode: LatencyMode = LatencyMode.STANDARD
    enable_llm_assist: bool = True
    force_llm_assist: bool = False
