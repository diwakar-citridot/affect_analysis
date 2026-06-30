"""Hierarchical field synthesis, per-feature confidence, background/foreground split."""

from __future__ import annotations

from conftest import make_context, make_field, run

from svarupa_affect.application.field_builder import AXIS_META
from svarupa_affect.domain.enums import FieldAxis


def test_every_axis_has_value_confidence_evidence(layer):
    sig = run(layer._builder.signals_for("I feel hopeful and alive today.", []))
    field = layer._builder.field_from_signals(sig, None)
    groups = (
        field.core,
        field.motivation,
        field.regulation,
        field.relational,
        field.temporal,
        field.uncertainty,
    )
    for group in groups:
        for name in type(group).model_fields:
            feat = getattr(group, name)
            assert 0.0 <= feat.confidence <= 1.0
            assert feat.evidence, f"{name} must carry evidence"


def test_axes_within_declared_ranges():
    field = make_field({"core.valence": -0.9, "relational.social_orientation": -0.8})
    for axis, (lo, hi, _) in AXIS_META.items():
        feat = field.feature(FieldAxis(axis))
        assert lo <= feat.value <= hi


def test_background_and_foreground_views(layer):
    text = "I was angry. Then I felt calm."
    result = run(layer.analyze_full(make_context(text)))
    pi = result.phenomenology_input
    assert pi.background_field is not None
    assert len(pi.foreground_episodes) == 2  # two sentences -> two episodes
    for ep in pi.foreground_episodes:
        assert ep.span[0] <= ep.span[1]
        assert ep.field is not None


def test_negative_valence_raises_avoidance(layer):
    sig = run(layer._builder.signals_for("I am scared and I want to hide and run away.", []))
    field = layer._builder.field_from_signals(sig, None)
    assert field.core.valence.value < 0.0
    assert field.motivation.avoidance.value > 0.3
