"""Pure scoring math (§5). Deterministic: same input -> identical output.

No I/O, no framework imports. All functions are total and side-effect free.
"""

from __future__ import annotations

import math

from .enums import StatePole, UncertaintyType
from .models import AffectiveField, AttributeScore, UncertaintyProfile

GAMMA = 1.2  # saturation: one strong hypothesis -> ~0.6-0.7
LAMBDA = 0.25  # max-pool vs mean blend for dimension relevance
KAPPA = 0.3  # one severe uncertainty source caps trust
BETA_GUNA = 0.3  # guṇa family modulation strength (§5.5)


def clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def saturate(x: float) -> float:
    """1 - e^(-gamma*x); maps an unbounded non-negative sum into [0,1)."""
    return 1.0 - math.exp(-GAMMA * max(0.0, x))


def to_unit(valence: float) -> float:
    """Map valence in [-1,1] to [0,1]."""
    return clip((valence + 1.0) / 2.0)


def softmax(values: dict[str, float]) -> dict[str, float]:
    if not values:
        return {}
    mx = max(values.values())
    exps = {k: math.exp(v - mx) for k, v in values.items()}
    total = sum(exps.values()) or 1.0
    return {k: v / total for k, v in exps.items()}


def dimension_relevance(scores: list[float]) -> float:
    """Soft max-pool: any strong attribute lifts relevance; many raise it further."""
    if not scores:
        return 0.0
    mx = max(scores)
    mean = sum(scores) / len(scores)
    return clip((1.0 - LAMBDA) * mx + LAMBDA * mean)


def axis_activation(value: float, lo: float, hi: float, neutral: float, direction: str) -> float:
    """How strongly an axis value activates a guṇa contributor (0..1)."""
    if direction == "high":
        span = hi - neutral
        return clip((value - neutral) / span) if span > 0 else 0.0
    if direction == "low":
        span = neutral - lo
        return clip((neutral - value) / span) if span > 0 else 0.0
    if direction == "center":
        half = max((hi - lo) / 2.0, 0.01)
        return clip(1.0 - abs(value - neutral) / half)
    return 0.0


def select_d2_pole(
    attribute: str,
    rule: str,
    *,
    arousal: float,
    intensity: float,
    regulation: float,
    approach: float,
    persistence: float,
    vitality: float,
    agency: float,
) -> StatePole:
    """Map felt guṇa tone onto {deficiency, balance, excess} for D2 attributes."""
    if rule == "activation":
        if arousal >= 0.6 or (intensity >= 0.6 and arousal >= 0.5):
            return StatePole.EXCESS
        if approach >= 0.5 and persistence >= 0.5 and arousal < 0.6:
            return StatePole.EXCESS
        if approach < 0.25 and arousal < 0.3:
            return StatePole.DEFICIENCY
        return StatePole.BALANCE
    if rule == "inertia":
        if vitality <= 0.3 and agency <= 0.35:
            return StatePole.EXCESS
        if vitality >= 0.55 and agency >= 0.5:
            return StatePole.DEFICIENCY
        return StatePole.BALANCE
    if rule == "equanimity":
        return select_pole("equanimity", intensity, arousal, regulation)
    return select_pole("intensity", intensity, arousal, regulation)


def apply_guna_modulation(
    attrs: list[AttributeScore],
    guna_weights: dict[str, float],
    attr_families: dict[str, str],
    family_to_guna: dict[str, str],
    *,
    beta: float = BETA_GUNA,
) -> list[AttributeScore]:
    """Reweight D8/D9 attribute relevances by guṇa family (§5.5)."""
    if not attrs or not guna_weights:
        return attrs
    out: list[AttributeScore] = []
    for attr in attrs:
        family = attr_families.get(attr.attribute)
        guna = family_to_guna.get(family, "") if family else ""
        g = guna_weights.get(guna, 0.0)
        rel = clip(attr.relevance * (1.0 + beta * g))
        out.append(attr.model_copy(update={"relevance": round(rel, 4)}))
    out.sort(key=lambda s: s.relevance, reverse=True)
    return out


def select_pole(rule: str, intensity: float, arousal: float, regulation: float) -> StatePole:
    """Map affect onto {deficiency, balance, excess} via a per-attribute rule (§5.4)."""
    if rule == "equanimity":
        if regulation >= 0.55 and arousal <= 0.5:
            return StatePole.BALANCE
        if arousal >= 0.6:
            return StatePole.EXCESS
        if intensity <= 0.2:
            return StatePole.DEFICIENCY
        return StatePole.BALANCE
    # default 'intensity' rule
    if intensity <= 0.15:
        return StatePole.DEFICIENCY
    if intensity >= 0.6 and arousal >= 0.55:
        return StatePole.EXCESS
    return StatePole.BALANCE


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def build_uncertainty_profile(
    *,
    field: AffectiveField,
    evidence_strength: float,
    source_agreement: float,
    coverage: float,
    mixed_valence: float,
    irony: float,
    length_factor: float,
    model_margin: float,
    single_clause: bool,
) -> UncertaintyProfile:
    """Compose the typed, independent uncertainty sources, then derive one scalar (§5.6)."""
    e = clip(evidence_strength)
    a = clip(source_agreement)
    v = clip(coverage)

    components: dict[UncertaintyType, float] = {
        UncertaintyType.MODEL: clip(1.0 - model_margin),
        UncertaintyType.INPUT_AMBIGUITY: clip(max(field.ambivalence, field.emotional_complexity)),
        UncertaintyType.MIXED_AFFECT: clip(mixed_valence),
        UncertaintyType.CONTRADICTORY_EVIDENCE: clip(1.0 - a),
        UncertaintyType.IRONY: clip(irony),
        UncertaintyType.INSUFFICIENT_CONTEXT: clip(1.0 - length_factor),
        UncertaintyType.COVERAGE: clip(1.0 - v),
    }

    base = clip(0.45 * e + 0.35 * a + 0.20 * v)
    if single_clause:
        base = min(base, 0.9)
    overall = clip(base * (1.0 - KAPPA * max(components.values(), default=0.0)))

    return UncertaintyProfile(
        components={k: round(val, 4) for k, val in components.items()},
        overall=round(overall, 4),
    )
