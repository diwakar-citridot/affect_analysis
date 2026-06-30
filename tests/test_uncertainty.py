"""Typed UncertaintyProfile + confidence propagation (§5.6)."""

from __future__ import annotations

from conftest import make_context, make_field, run

from svarupa_affect.domain.enums import UncertaintyType
from svarupa_affect.domain.scoring import build_uncertainty_profile


def test_components_independent_and_in_range():
    field = make_field(
        {"motivation.approach": 0.6, "motivation.avoidance": 0.6, "uncertainty.ambiguity": 0.7}
    )
    prof = build_uncertainty_profile(
        field=field,
        evidence_strength=0.5,
        source_agreement=0.4,
        coverage=0.3,
        mixed_valence=0.6,
        irony=0.0,
        length_factor=0.2,
        model_margin=0.5,
        single_clause=True,
    )
    assert set(prof.components) <= set(UncertaintyType)
    assert all(0.0 <= v <= 1.0 for v in prof.components.values())
    assert 0.0 <= prof.overall <= 1.0


def test_thin_input_raises_insufficient_context_and_caps_confidence(layer):
    thin = run(layer.analyze_full(make_context("Sad."))).phenomenology_input
    rich = run(
        layer.analyze_full(
            make_context(
                "I feel a deep and steady joy; I am grateful, alive, and connected to the people I love."
            )
        )
    ).phenomenology_input
    # thin/single-clause input is more context-starved and confidence is capped at 0.9
    assert (
        thin.uncertainty.components[UncertaintyType.INSUFFICIENT_CONTEXT]
        >= rich.uncertainty.components[UncertaintyType.INSUFFICIENT_CONTEXT]
    )
    assert thin.uncertainty.overall <= 0.9


def test_coverage_uncertainty_high_when_coverage_low():
    field = make_field()
    prof = build_uncertainty_profile(
        field=field,
        evidence_strength=0.5,
        source_agreement=0.6,
        coverage=0.1,
        mixed_valence=0.0,
        irony=0.0,
        length_factor=0.5,
        model_margin=0.6,
        single_clause=False,
    )
    assert prof.components[UncertaintyType.COVERAGE] >= 0.8
