"""Shared test fixtures and helpers."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import pytest

from svarupa_affect.application.analyze_affect import AffectLayer, build_default_layer
from svarupa_affect.application.field_builder import AXIS_META
from svarupa_affect.domain.enums import FieldAxis
from svarupa_affect.domain.models import (
    AffectiveField,
    CoreAffect,
    FieldUncertainty,
    LayerContext,
    Motivation,
    ReconstructedFeature,
    Regulation,
    Relational,
    Temporal,
)


def run(coro: Any) -> Any:
    return asyncio.run(coro)


@pytest.fixture(scope="session")
def layer() -> AffectLayer:
    return build_default_layer()


def make_context(text: str, **kwargs: Any) -> LayerContext:
    return LayerContext(request_id=str(uuid.uuid4()), analysis_text=text, **kwargs)


def rf(value: float, confidence: float = 0.6) -> ReconstructedFeature:
    return ReconstructedFeature(value=value, confidence=confidence)


def make_field(values: dict[str, float] | None = None) -> AffectiveField:
    """Build an AffectiveField from a {``group.attr``: value} dict, neutral defaults elsewhere."""
    vals = values or {}

    def g(axis: str) -> ReconstructedFeature:
        default = AXIS_META.get(axis, (0.0, 1.0, 0.5))[2]
        return rf(vals.get(axis, default))

    return AffectiveField(
        core=CoreAffect(
            valence=g("core.valence"),
            arousal=g("core.arousal"),
            vitality=g("core.vitality"),
            intensity=g("core.intensity"),
        ),
        motivation=Motivation(
            agency=g("motivation.agency"),
            approach=g("motivation.approach"),
            avoidance=g("motivation.avoidance"),
            control=g("motivation.control"),
        ),
        regulation=Regulation(
            stability=g("regulation.stability"),
            persistence=g("regulation.persistence"),
            volatility=g("regulation.volatility"),
            regulation=g("regulation.regulation"),
        ),
        relational=Relational(
            attachment=g("relational.attachment"),
            trust=g("relational.trust"),
            social_orientation=g("relational.social_orientation"),
        ),
        temporal=Temporal(
            continuity=g("temporal.continuity"),
            anticipation=g("temporal.anticipation"),
            resolution=g("temporal.resolution"),
        ),
        uncertainty=FieldUncertainty(
            ambiguity=g("uncertainty.ambiguity"),
            confidence=rf(vals.get("uncertainty.confidence", 0.6)),
            evidence_quality=g("uncertainty.evidence_quality"),
        ),
        axis_coverage={FieldAxis.CORE_VALENCE: 0.6},
    )
