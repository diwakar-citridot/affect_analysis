"""Field + pattern coverage for remaining D8/D9 bridge gaps (vismaya, hasa, autsukya, …)."""

from __future__ import annotations

from conftest import make_context, make_field, rf, run

from svarupa_affect.application.analyze_affect import build_default_layer
from svarupa_affect.application.hypotheses import EmotionHypothesisGenerator
from svarupa_affect.domain.enums import ExperientialPatternType
from svarupa_affect.domain.models import EmotionEvidence, ExperientialPattern


def _hyps(field, patterns=None):
    gen = EmotionHypothesisGenerator()
    return gen.generate(field, patterns or [], EmotionEvidence(probs={}, margin=0.0))


def test_surprise_field_score_nonzero():
    field = make_field(
        {
            "core.arousal": 0.75,
            "core.intensity": 0.7,
            "regulation.volatility": 0.6,
            "regulation.persistence": 0.2,
        }
    )
    labels = {h.label for h in _hyps(field)}
    assert "surprise" in labels


def test_wonder_field_score_nonzero():
    field = make_field(
        {
            "core.valence": 0.6,
            "core.arousal": 0.65,
            "core.vitality": 0.7,
        }
    )
    gen = EmotionHypothesisGenerator()
    labels = {
        h.label
        for h in gen.generate(field, [], EmotionEvidence(probs={}, margin=0.0), top_k=20)
    }
    assert "wonder" in labels


def test_openness_pattern_boosts_amusement():
    field = make_field({"core.valence": 0.5, "core.arousal": 0.55})
    patterns = [
        ExperientialPattern(
            type=ExperientialPatternType.OPENNESS,
            strength=rf(0.5, 0.6),
        )
    ]
    without = {h.label: h.probability for h in _hyps(field)}
    with_pat = {h.label: h.probability for h in _hyps(field, patterns)}
    assert with_pat.get("amusement", 0.0) > without.get("amusement", 0.0)


def test_hypervigilance_pattern_boosts_surprise_and_anticipation():
    field = make_field(
        {
            "core.arousal": 0.7,
            "core.intensity": 0.65,
            "regulation.volatility": 0.55,
            "regulation.persistence": 0.25,
            "temporal.anticipation": 0.6,
        }
    )
    patterns = [
        ExperientialPattern(
            type=ExperientialPatternType.HYPERVIGILANCE,
            strength=rf(0.45, 0.6),
        )
    ]
    labels = {h.label for h in _hyps(field, patterns)}
    assert "surprise" in labels
    assert "anticipation" in labels


def test_astonishment_text_emits_vismaya():
    layer = build_default_layer()
    text = (
        "I stood there stunned, heart racing, unable to process what had just unfolded. "
        "The sudden shift left me wide-eyed and astonished."
    )
    result = run(layer.analyze_full(make_context(text)))
    hyps = [h.label for h in result.phenomenology_input.emotion_hypotheses]
    assert "surprise" in hyps or "wonder" in hyps
    d8 = next(s for s in result.signals if s.dimension_id == 8)
    assert any(a.attribute == "vismaya" for a in d8.attribute_scores)


def test_amusement_text_emits_hasa():
    layer = build_default_layer()
    text = "We laughed until our sides hurt — it was hilarious and genuinely amusing."
    result = run(layer.analyze_full(make_context(text)))
    d8 = next(s for s in result.signals if s.dimension_id == 8)
    assert any(a.attribute == "hasa" for a in d8.attribute_scores)


def test_anticipation_maps_to_autsukya_via_bridge():
    from svarupa_affect.domain.enums import Durability
    from svarupa_affect.domain.models import EmotionHypothesis
    from svarupa_affect.infrastructure.bridge.tables import JsonBridgeTable
    from svarupa_affect.infrastructure.config import Settings

    s = Settings.load()
    d9 = JsonBridgeTable(s.bridge_d9)
    field = make_field({"temporal.anticipation": 0.75, "motivation.approach": 0.55})
    hyps = [
        EmotionHypothesis(
            label="anticipation", probability=0.85, durability=Durability.TRANSIENT
        )
    ]
    attrs = d9.map(hyps, field)
    assert any(a.attribute == "autsukya" for a in attrs)
