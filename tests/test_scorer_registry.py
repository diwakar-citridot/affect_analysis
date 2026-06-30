"""Scorer registry: emit dimensions from svarupa_layer_scorer (or static fallback)."""

from __future__ import annotations

from svarupa_affect.application.analyze_affect import build_default_layer
from svarupa_affect.infrastructure.kg.scorer_registry import StaticScorerRegistry, build_scorer_registry


def test_static_scorer_registry_emit_dimensions():
    reg = StaticScorerRegistry()
    assert reg.emit_dimensions() == frozenset({2, 8, 9})


def test_static_scorer_registry_field_and_bridge_kinds():
    reg = StaticScorerRegistry()
    kinds = {s.dimension_id: s.scorer_kind for s in reg.scorers()}
    assert kinds[2] == "field_native"
    assert kinds[8] == "hypothesis_bridge"
    assert kinds[9] == "hypothesis_bridge"


def test_build_default_layer_uses_scorer_emit_set():
    layer = build_default_layer()
    assert layer._emit_dimensions <= layer._scorer_registry.emit_dimensions()
    assert 2 in layer._emit_dimensions
    assert 8 in layer._emit_dimensions


def test_build_scorer_registry_loads_from_mysql_when_configured():
    reg = build_scorer_registry()
    assert reg.emit_dimensions()


def test_narrowed_affinity_updates_emit_set():
    layer = build_default_layer()
    layer.affinity = frozenset({8, 9})
    layer._emit_dimensions = layer.affinity & layer._scorer_registry.emit_dimensions()
    assert 2 not in layer._emit_dimensions
