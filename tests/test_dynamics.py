"""AffectDynamicsAnalyzer: trajectory transitions + interaction templates."""

from __future__ import annotations

from conftest import make_context, run


def test_multi_sentence_trajectory(layer):
    text = "I was terrified when the call came. Then I went numb. But slowly I feel hopeful again."
    pi = run(layer.analyze_full(make_context(text))).phenomenology_input
    assert len(pi.trajectory.sequence) == 3
    assert len(pi.trajectory.transitions) == 2
    assert 0.0 <= pi.trajectory.volatility <= 1.0


def test_fear_hope_interaction_is_tension(layer):
    text = "I keep hoping things will get better, but I am bracing myself for it to all fall apart again."
    pi = run(layer.analyze_full(make_context(text))).phenomenology_input
    tensions = [i for i in pi.interactions if i.is_tension]
    assert any(set(i.components) == {"fear", "hope"} for i in tensions)


def test_single_sentence_has_no_transitions(layer):
    pi = run(layer.analyze_full(make_context("I feel calm."))).phenomenology_input
    assert pi.trajectory.transitions == []
