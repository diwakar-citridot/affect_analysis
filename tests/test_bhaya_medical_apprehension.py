"""Somatic medical-apprehension text should surface bhaya on D8."""

from __future__ import annotations

from conftest import make_context, run

from svarupa_affect.application.analyze_affect import build_default_layer
from svarupa_affect.application.mappers import to_response

DOCTOR_INBOX = (
    "I see the doctor's name in my inbox and I can't open it right away. "
    "I get up, refill my water, sit back down, and then I open it—but my throat is "
    "tight the whole time and I realize I've been holding my breath until I get to "
    "the actual results."
)


def test_medical_apprehension_surfaces_bhaya_on_d8():
    layer = build_default_layer()
    result = run(layer.analyze_full(make_context(DOCTOR_INBOX)))
    response = to_response(result)
    d8 = next(s for s in response.signals if s.dimension_name == "Sthāyībhāvas")
    attrs = [a.attribute for a in d8.attribute_scores]
    assert "bhaya" in attrs, f"D8 attributes were {attrs}"


def test_fear_or_anxiety_in_top_hypotheses():
    layer = build_default_layer()

    async def _hyps():
        sig = await layer._builder.signals_for(DOCTOR_INBOX, [])
        field = layer._builder.field_from_signals(sig, None)
        patterns = layer._patterns.recognize(field)
        return layer._hypotheses.generate(
            field, patterns, sig.lexical, semantic=sig.semantic
        )

    import asyncio

    hyps = asyncio.run(_hyps())
    labels = {h.label for h in hyps}
    assert labels & {"fear", "anxiety"}, f"hypotheses were {labels}"
