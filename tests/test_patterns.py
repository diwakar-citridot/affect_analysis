"""ExperientialPatternRecognizer: signatures fire on the right field regions."""

from __future__ import annotations

from conftest import make_field

from svarupa_affect.application.patterns import ExperientialPatternRecognizer
from svarupa_affect.domain.enums import ExperientialPatternType
from svarupa_affect.infrastructure.config import Settings


def _recognizer() -> ExperientialPatternRecognizer:
    return ExperientialPatternRecognizer(Settings.load().patterns)


def test_withdrawal_fires():
    field = make_field({"motivation.avoidance": 0.8, "relational.social_orientation": -0.6})
    types = {p.type for p in _recognizer().recognize(field)}
    assert ExperientialPatternType.WITHDRAWAL in types


def test_striving_fires():
    field = make_field({"motivation.approach": 0.8, "core.vitality": 0.7, "motivation.agency": 0.7})
    types = {p.type for p in _recognizer().recognize(field)}
    assert ExperientialPatternType.STRIVING in types


def test_pattern_strength_and_confidence_in_range():
    field = make_field({"motivation.avoidance": 0.9, "relational.social_orientation": -0.7})
    for p in _recognizer().recognize(field):
        assert 0.0 <= p.strength.value <= 1.0
        assert 0.0 <= p.strength.confidence <= 1.0
        assert p.supporting_axes


def test_neutral_field_fires_nothing_strong():
    patterns = _recognizer().recognize(make_field())
    # neutral field may match a few mild signatures, but none should be saturated
    assert all(p.strength.value < 0.99 for p in patterns)
