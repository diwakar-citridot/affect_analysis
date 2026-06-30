"""Philosophy regression (§7.2): no diagnostic / second-person verdict / prescription language."""

from __future__ import annotations

import json

import pytest
from conftest import make_context, run

_BANNED = [
    "you are ",
    "you're ",
    "you have a disorder",
    "you suffer from",
    "diagnosis",
    "you should ",
    "you must ",
    "you need to ",
    "i recommend",
    "you will ",
    "the patient",
    "clinically",
]

_TEXTS = [
    "I keep hoping things will get better, but I am bracing for it to fall apart again.",
    "I am furious they cancelled it and now I feel empty and hopeless.",
    "After a long struggle I finally feel calm and at peace.",
]


def _collect_strings(obj) -> list[str]:
    out: list[str] = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            out.extend(_collect_strings(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(_collect_strings(v))
    return out


@pytest.mark.parametrize("text", _TEXTS)
def test_no_verdict_or_prescription_language(layer, text):
    from svarupa_affect.application.mappers import to_response_dict

    resp = to_response_dict(run(layer.analyze_full(make_context(text))))
    blob = " ".join(_collect_strings(resp)).lower()
    for phrase in _BANNED:
        assert phrase not in blob, f"banned phrase surfaced: {phrase!r}"


def test_interaction_descriptions_are_recognition_framed(layer):
    pi = run(layer.analyze_full(make_context(_TEXTS[0]))).phenomenology_input
    for inter in pi.interactions:
        low = inter.description.lower()
        assert "you are" not in low and "you should" not in low
