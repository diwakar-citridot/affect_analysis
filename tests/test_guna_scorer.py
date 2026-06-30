"""GunaScorer: field-native D2 Triguṇa scoring and D8/D9 modulation."""

from __future__ import annotations

import pytest
from conftest import make_context, make_field, rf, run

from svarupa_affect.application.guna_scorer import GunaFamilyModulator, GunaScorer
from svarupa_affect.domain.enums import Durability, ExperientialPatternType, StatePole
from svarupa_affect.domain.models import AttributeScore, ExperientialPattern
from svarupa_affect.domain.scoring import axis_activation, select_d2_pole
from svarupa_affect.infrastructure.config import Settings


def _scorer() -> GunaScorer:
    s = Settings.load()
    return GunaScorer(s.guna_synthesis, s.pole_map_d2)


def _modulator() -> GunaFamilyModulator:
    return GunaFamilyModulator(Settings.load().guna_families)


def test_axis_activation_high_and_low():
    assert axis_activation(0.8, 0.0, 1.0, 0.5, "high") > 0.5
    assert axis_activation(0.2, 0.0, 1.0, 0.5, "low") > 0.5
    assert axis_activation(0.0, -1.0, 1.0, 0.0, "center") > 0.5


def test_rajas_pole_compulsive_habit():
    pole = select_d2_pole(
        "rajas",
        "activation",
        arousal=0.4,
        intensity=0.45,
        regulation=0.5,
        approach=0.55,
        persistence=0.65,
        vitality=0.5,
        agency=0.5,
    )
    assert pole == StatePole.EXCESS


def test_guna_scorer_rajas_on_striving_field():
    scorer = _scorer()
    field = make_field(
        {
            "motivation.approach": 0.55,
            "regulation.persistence": 0.65,
            "core.arousal": 0.4,
            "core.vitality": 0.55,
            "temporal.anticipation": 0.4,
        }
    )
    patterns = [
        ExperientialPattern(
            type=ExperientialPatternType.STRIVING,
            strength=rf(0.37, 0.6),
        )
    ]
    result = scorer.score(field, patterns)
    assert result.attributes
    top = result.attributes[0]
    assert top.attribute == "rajas"
    assert top.dimension_id == 2
    assert top.durability == Durability.ENDURING
    assert 0.0 < top.relevance <= 1.0
    assert sum(result.modulation_weights.values()) == pytest.approx(1.0, abs=1e-6)


def test_guna_modulation_boosts_agitation_family():
    mod = _modulator()
    attrs = [
        AttributeScore(
            attribute="utsaha",
            relevance=0.4,
            state=StatePole.BALANCE,
            dimension_id=8,
        )
    ]
    boosted = mod.apply(attrs, {"rajas": 0.6, "sattva": 0.2, "tamas": 0.2})
    assert boosted[0].relevance > attrs[0].relevance


def test_email_example_emits_d2_signal(layer):
    text = (
        "I check my work email before I get out of bed most mornings. "
        "It's not that something urgent is waiting—I just want to see what came in overnight, "
        "like knowing that tells me where I stand before the day even starts."
    )
    result = run(layer.analyze_full(make_context(text)))
    d2 = [s for s in result.signals if s.dimension_id == 2]
    assert len(d2) == 1
    signal = d2[0]
    assert not signal.abstained
    assert any(a.attribute == "rajas" for a in signal.attribute_scores)
    rajas = next(a for a in signal.attribute_scores if a.attribute == "rajas")
    assert rajas.relevance >= 0.12
