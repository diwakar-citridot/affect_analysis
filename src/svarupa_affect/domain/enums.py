"""Closed enums for the AFF layer (§3.1 of the design). Dimensions are data, not code."""

from __future__ import annotations

from enum import StrEnum


class StatePole(StrEnum):
    """Canonical triple + unclear (matches svarupa_status)."""

    DEFICIENCY = "deficiency"
    BALANCE = "balance"
    EXCESS = "excess"
    UNCLEAR = "unclear"


class Durability(StrEnum):
    ENDURING = "enduring"
    TRANSIENT = "transient"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class EvidenceKind(StrEnum):
    SPAN = "span"
    AXIS = "axis"
    FIELD = "field"
    EMOTION = "emotion"
    INTERACTION = "interaction"
    DYNAMICS = "dynamics"
    MAPPING_PATH = "mapping_path"


class LatencyMode(StrEnum):
    FAST = "fast"
    STANDARD = "standard"
    DEEP = "deep"


class FieldAxis(StrEnum):
    """Canonical hierarchical AffectiveField axes, addressed as ``group.attr``."""

    # Core affect
    CORE_VALENCE = "core.valence"
    CORE_AROUSAL = "core.arousal"
    CORE_VITALITY = "core.vitality"
    CORE_INTENSITY = "core.intensity"
    # Motivation
    MOT_AGENCY = "motivation.agency"
    MOT_APPROACH = "motivation.approach"
    MOT_AVOIDANCE = "motivation.avoidance"
    MOT_CONTROL = "motivation.control"
    # Regulation
    REG_STABILITY = "regulation.stability"
    REG_PERSISTENCE = "regulation.persistence"
    REG_VOLATILITY = "regulation.volatility"
    REG_REGULATION = "regulation.regulation"
    # Relational
    REL_ATTACHMENT = "relational.attachment"
    REL_TRUST = "relational.trust"
    REL_SOCIAL_ORIENTATION = "relational.social_orientation"
    # Temporal
    TMP_CONTINUITY = "temporal.continuity"
    TMP_ANTICIPATION = "temporal.anticipation"
    TMP_RESOLUTION = "temporal.resolution"
    # Uncertainty facet of the field
    UNC_AMBIGUITY = "uncertainty.ambiguity"
    UNC_CONFIDENCE = "uncertainty.confidence"
    UNC_EVIDENCE_QUALITY = "uncertainty.evidence_quality"


class MotivationalDirection(StrEnum):
    """Derived from motivation.approach vs motivation.avoidance."""

    APPROACH = "approach"
    AVOID = "avoid"
    CONFLICTED = "conflicted"
    NEUTRAL = "neutral"


class ExperientialPatternType(StrEnum):
    """The lived stance recognised between field and emotion."""

    WITHDRAWAL = "withdrawal"
    OPENNESS = "openness"
    STRIVING = "striving"
    AVOIDANCE = "avoidance"
    RUMINATION = "rumination"
    HYPERVIGILANCE = "hypervigilance"
    SURRENDER = "surrender"
    RESISTANCE = "resistance"
    ATTACHMENT = "attachment"
    DETACHMENT = "detachment"


class DynamicsPattern(StrEnum):
    """How the field changes across the narrative."""

    ESCALATION = "escalation"
    RESOLUTION = "resolution"
    OSCILLATION = "oscillation"
    PERSISTENCE = "persistence"
    COLLAPSE = "collapse"
    RECOVERY = "recovery"
    STABLE = "stable"


class UncertaintyType(StrEnum):
    """Typed, independent sources of uncertainty."""

    MODEL = "model"
    INPUT_AMBIGUITY = "input_ambiguity"
    MIXED_AFFECT = "mixed_affect"
    CONTRADICTORY_EVIDENCE = "contradictory_evidence"
    IRONY = "irony"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    COVERAGE = "coverage"
