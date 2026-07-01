"""JsonBridgeTable: hypothesis -> Rasa mapping + field_guard regions."""

from __future__ import annotations

from conftest import make_field

from svarupa_affect.domain.enums import Durability
from svarupa_affect.domain.models import EmotionHypothesis
from svarupa_affect.infrastructure.bridge.tables import JsonBridgeTable
from svarupa_affect.infrastructure.config import Settings


def _bridges():
    s = Settings.load()
    return JsonBridgeTable(s.bridge_d8), JsonBridgeTable(s.bridge_d9)


def test_fear_maps_to_bhaya_d8_when_persistent():
    d8, _ = _bridges()
    field = make_field({"core.valence": -0.5, "core.arousal": 0.7, "regulation.persistence": 0.7})
    hyps = [EmotionHypothesis(label="fear", probability=0.9, durability=Durability.ENDURING)]
    attrs = d8.map(hyps, field)
    assert any(a.attribute == "bhaya" for a in attrs)


def test_fear_guard_blocks_bhaya_when_not_persistent():
    d8, _ = _bridges()
    field = make_field(
        {
            "core.valence": -0.5,
            "core.arousal": 0.7,
            "regulation.persistence": 0.1,
            "motivation.avoidance": 0.05,
            "temporal.anticipation": 0.05,
        }
    )
    hyps = [EmotionHypothesis(label="fear", probability=0.9)]
    attrs = d8.map(hyps, field)
    assert all(a.attribute != "bhaya" for a in attrs)


def test_fear_maps_to_cinta_d9_under_avoidance():
    _, d9 = _bridges()
    field = make_field({"motivation.avoidance": 0.7})
    hyps = [EmotionHypothesis(label="fear", probability=0.8)]
    attrs = d9.map(hyps, field)
    assert any(a.attribute == "cinta" for a in attrs)


def test_relevances_in_range_and_sorted():
    d8, _ = _bridges()
    field = make_field({"core.valence": -0.5, "core.arousal": 0.7, "regulation.persistence": 0.7})
    attrs = d8.map([EmotionHypothesis(label="fear", probability=0.9)], field)
    assert all(0.0 <= a.relevance <= 1.0 for a in attrs)
    assert attrs == sorted(attrs, key=lambda a: a.relevance, reverse=True)


def test_attributes_vocabulary_exposed():
    d8, d9 = _bridges()
    assert "bhaya" in d8.attributes()
    assert "cinta" in d9.attributes()
