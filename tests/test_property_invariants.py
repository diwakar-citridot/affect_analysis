"""Property / invariant tests over the gold texts and crafted inputs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import make_context, run

from svarupa_affect.domain.enums import StatePole

_GOLD = Path(__file__).resolve().parents[1] / "data" / "ground_truth" / "affect_gold.jsonl"


def _gold_texts() -> list[str]:
    return [json.loads(line)["text"] for line in _GOLD.read_text().splitlines() if line.strip()]


@pytest.mark.parametrize("text", _gold_texts())
def test_signals_respect_affinity_and_ranges(layer, text):
    result = run(layer.analyze_full(make_context(text)))
    for s in result.signals:
        assert s.dimension_id in layer.affinity
        assert 0.0 <= s.relevance <= 1.0
        assert 0.0 <= s.confidence <= 1.0
        # relevance and confidence are kept as two separate numbers (never collapsed)
        assert s.relevance is not None and s.confidence is not None


def test_factual_text_abstains(layer):
    result = run(
        layer.analyze_full(
            make_context(
                "The meeting is scheduled for 3pm in conference room B on the second floor."
            )
        )
    )
    assert all(s.abstained for s in result.signals) or not result.signals


def test_tension_implies_ambivalence(layer):
    pi = run(
        layer.analyze_full(
            make_context(
                "I keep hoping things will get better, but I am bracing myself for it to all fall apart again."
            )
        )
    ).phenomenology_input
    if any(i.is_tension for i in pi.interactions):
        assert pi.background_field.ambivalence > 0.0


def test_excess_pole_requires_elevated_intensity(layer):
    result = run(
        layer.analyze_full(
            make_context("I am absolutely furious and I cannot contain my rage right now!")
        )
    )
    pi = result.phenomenology_input
    for s in result.signals:
        for attr in s.attribute_scores:
            if attr.state == StatePole.EXCESS:
                # monotonicity invariant: excess implies above-band arousal/intensity
                assert (
                    pi.background_field.core.arousal.value >= 0.5
                    or pi.background_field.core.intensity.value >= 0.5
                )


def test_only_public_objects_serialized(layer):
    from svarupa_affect.application.mappers import to_response
    from svarupa_affect.infrastructure.kg.dimension_registry import StaticDimensionRegistry

    result = run(layer.analyze_full(make_context("I feel hopeful and calm.")))
    resp = to_response(result, StaticDimensionRegistry())
    dumped = resp.model_dump(mode="json")
    # nothing outside the contract leaks at the top level
    assert set(dumped) <= {
        "request_id",
        "layer",
        "layer_version",
        "attribute_scores",
        "field_axes",
        "signals",
        "phenomenology_input",
        "provenance",
    }
    for sig in dumped["signals"]:
        assert "dimension_id" not in sig
        assert "dimension_name" in sig
        for attr in sig.get("attribute_scores", []):
            assert "dimension_id" not in attr
            assert "dimension_name" in attr
