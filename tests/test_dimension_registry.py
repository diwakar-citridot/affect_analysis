"""API response maps dimension_id to dimension_name (sanskrit_term) from the registry."""

from __future__ import annotations

from conftest import make_context, run

from svarupa_affect.application.mappers import to_response
from svarupa_affect.infrastructure.kg.dimension_registry import StaticDimensionRegistry


def test_signals_expose_dimension_name(layer):
    result = run(layer.analyze_full(make_context("I feel anxious but also hopeful.")))
    registry = StaticDimensionRegistry()
    response = to_response(result, registry)

    assert response.signals
    for signal in response.signals:
        assert signal.dimension_name
        assert signal.dimension_name != ""
        for score in signal.attribute_scores:
            assert score.dimension_name


def test_affinity_dimension_names(layer):
    result = run(layer.analyze_full(make_context("I keep hoping things get better.")))
    registry = StaticDimensionRegistry()
    names = {s.dimension_name for s in to_response(result, registry).signals}
    assert "Sthāyībhāvas" in names or "Vyabhicārībhāvas" in names or "Triguṇa — Sattva·Rajas·Tamas" in names


def test_top_level_attribute_scores_sorted_by_relevance(layer):
    result = run(layer.analyze_full(make_context("I feel sick and repulsed. It was gross and disgusting.")))
    response = to_response(result, StaticDimensionRegistry())
    assert response.attribute_scores
    relevances = [score.relevance for score in response.attribute_scores]
    assert relevances == sorted(relevances, reverse=True)
    per_signal = [score for signal in response.signals for score in signal.attribute_scores]
    assert len(response.attribute_scores) == len(per_signal)


def test_top_level_field_axes_cover_background_field(layer):
    result = run(layer.analyze_full(make_context("I feel hopeful and calm.")))
    response = to_response(result, StaticDimensionRegistry())
    axis_names = {axis.axis for axis in response.field_axes}
    assert "core.valence" in axis_names
    assert "motivation.approach" in axis_names
    assert len(response.field_axes) == len(axis_names)
