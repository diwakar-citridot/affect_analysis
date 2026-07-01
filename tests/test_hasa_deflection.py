"""Tension-diffusing humor (Hāsa) should surface on D8 even without laugh words."""

from __future__ import annotations

import asyncio

from conftest import make_context, run

from svarupa_affect.application.analyze_affect import build_default_layer
from svarupa_affect.application.mappers import to_response
from svarupa_affect.domain.enums import LatencyMode
from svarupa_affect.domain.models import LayerContext
from svarupa_affect.infrastructure.affect.semantic_encoder import build_semantic_encoder
from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.kg.concept_registry import build_concept_registry

BROTHER_DEFLECTION = (
    "The relatives are at our house and everyone's discussing my brother's job prospects "
    "and I can't stop making little comments that diffuse the seriousness. I watch my "
    "brother's face stay tight and I know I'm not helping him—I'm just making it "
    "impossible to actually address what needs to be addressed. Later he tells me he "
    "wishes I'd just stayed out of it. I was trying to help."
)

BROTHER_DEFLECTION_GUILT = BROTHER_DEFLECTION.replace(
    "I was trying to help.", "I hate that I keep doing this."
)


def test_tension_diffusing_text_surfaces_hasa_on_d8():
    layer = build_default_layer()
    result = run(layer.analyze_full(make_context(BROTHER_DEFLECTION)))
    response = to_response(result)
    d8 = next(s for s in response.signals if s.dimension_name == "Sthāyībhāvas")
    attrs = [a.attribute for a in d8.attribute_scores]
    assert "hasa" in attrs, f"D8 attributes were {attrs}"


def test_guilt_heavy_deflection_still_surfaces_hasa_on_d8():
    layer = build_default_layer()
    ctx = LayerContext(
        request_id="test",
        analysis_text=BROTHER_DEFLECTION_GUILT,
        locale="en",
        latency_mode=LatencyMode.STANDARD,
        enable_llm_assist=False,
        force_llm_assist=False,
    )
    result = run(layer.analyze_full(ctx))
    response = to_response(result)
    d8 = next(s for s in response.signals if s.dimension_name == "Sthāyībhāvas")
    attrs = [a.attribute for a in d8.attribute_scores]
    assert "hasa" in attrs, f"D8 attributes were {attrs}"


def test_deflection_or_amusement_in_top_hypotheses():
    layer = build_default_layer()

    async def _hyps(text: str):
        sig = await layer._builder.signals_for(text, [])
        field = layer._builder.field_from_signals(sig, None)
        patterns = layer._patterns.recognize(field)
        return layer._hypotheses.generate(
            field, patterns, sig.lexical, semantic=sig.semantic
        )

    hyps = asyncio.run(_hyps(BROTHER_DEFLECTION_GUILT))
    labels = {h.label for h in hyps}
    assert labels & {"deflection", "amusement"}, f"hypotheses were {labels}"


def test_semantic_encoder_ranks_deflection_for_tension_diffusing_text():
    settings = Settings.load()
    registry = build_concept_registry()
    enc = build_semantic_encoder(settings=settings, concept_registry=registry)
    feat = asyncio.run(enc.encode(BROTHER_DEFLECTION))
    assert feat.hypothesis_probs
    top = sorted(feat.hypothesis_probs.items(), key=lambda kv: kv[1], reverse=True)[:4]
    labels = {k for k, _ in top}
    assert labels & {"deflection", "amusement"}, f"top semantic hypotheses {top}"
