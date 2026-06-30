"""Bridge + hypotheses: disgust / aversion maps to jugupsa (D8)."""

from __future__ import annotations

from conftest import make_context, run

from svarupa_affect.application.analyze_affect import build_default_layer
from svarupa_affect.infrastructure.bridge.tables import JsonBridgeTable
from svarupa_affect.infrastructure.config import Settings


def test_bridge_maps_disgust_to_jugupsa():
    s = Settings.load()
    d8 = JsonBridgeTable(s.bridge_d8)
    assert "jugupsa" in d8.attributes()


def test_explicit_disgust_text_emits_jugupsa():
    layer = build_default_layer()
    text = "I feel sick and repulsed by what I saw. It was gross and disgusting."
    result = run(layer.analyze_full(make_context(text)))
    d8 = next(s for s in result.signals if s.dimension_id == 8)
    assert any(a.attribute == "jugupsa" for a in d8.attribute_scores)


def test_aversion_field_emits_jugupsa_without_disgust_label():
    layer = build_default_layer()
    text = (
        "Something about the way they spoke made me want to turn away. "
        "I could not stomach being in that room."
    )
    result = run(layer.analyze_full(make_context(text)))
    hyps = [h.label for h in result.phenomenology_input.emotion_hypotheses]
    assert "disgust" in hyps or "moral_aversion" in hyps
    d8 = next(s for s in result.signals if s.dimension_id == 8)
    assert any(a.attribute == "jugupsa" for a in d8.attribute_scores)


def test_cannot_stand_disengage_emits_jugupsa():
    layer = build_default_layer()
    text = (
        "I cannot stand how they talk about people behind their backs. "
        "It makes me pull back and disengage from the conversation entirely."
    )
    result = run(layer.analyze_full(make_context(text)))
    d8 = next(s for s in result.signals if s.dimension_id == 8)
    assert not d8.abstained
    assert any(a.attribute == "jugupsa" for a in d8.attribute_scores)


def test_moral_recoil_vignette_emits_jugupsa():
    layer = build_default_layer()
    text = (
        "When my colleague suggested cutting corners on safety checks, "
        "I felt a quiet recoil. I knew I would not be part of that decision."
    )
    result = run(layer.analyze_full(make_context(text)))
    hyps = {h.label for h in result.phenomenology_input.emotion_hypotheses}
    assert hyps & {"disgust", "moral_aversion"}
    d8 = next(s for s in result.signals if s.dimension_id == 8)
    assert not d8.abstained
    assert any(a.attribute == "jugupsa" for a in d8.attribute_scores)
