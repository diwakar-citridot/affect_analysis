"""Concept registry: AFF applicability from svarupa_concept_layer (or static fallback)."""

from __future__ import annotations

from conftest import make_context, run

from svarupa_affect.application.analyze_affect import build_default_layer
from svarupa_affect.infrastructure.kg.concept_registry import (
    StaticConceptRegistry,
    canonical_slug,
)


def test_canonical_slug_aliases():
    assert canonical_slug("shoka") == "soka"
    assert canonical_slug("vishada") == "visada"
    assert canonical_slug("bhaya") == "bhaya"


def test_static_registry_exposes_d8_d9_glosses():
    reg = StaticConceptRegistry()
    glosses = reg.glosses(8, ["rati", "bhaya"])
    assert "rati" in glosses
    assert glosses["bhaya"]


def test_static_registry_affinity():
    reg = StaticConceptRegistry()
    assert reg.affinity() == frozenset({2, 8, 9, 15, 19, 21, 22, 24})
    assert reg.primary_dimensions() == frozenset({2, 8, 9})
    assert 15 in reg.contributing_dimensions()
    assert 21 in reg.contributing_dimensions()
    assert 5 not in reg.affinity()


def test_static_registry_d9_full_vocabulary():
    reg = StaticConceptRegistry()
    assert len(reg.slugs(9)) == 33


def test_static_registry_tridosha_contributing():
    reg = StaticConceptRegistry()
    assert reg.slugs(15) == frozenset({"vata", "pitta", "kapha"})


def test_emission_intersects_db_affinity_with_implemented_scorers():
    """Dimensions in DB affinity but without scorers (e.g. D5) must not emit signals."""
    layer = build_default_layer()
    layer.affinity = frozenset({2, 5, 8, 9})
    result = run(layer.analyze_full(make_context("I feel anxious but also hopeful.")))
    emitted = {s.dimension_id for s in result.signals}
    assert 5 not in emitted
    assert emitted <= {2, 8, 9}


def test_emission_respects_narrowed_affinity():
    layer = build_default_layer()
    layer.affinity = frozenset({8, 9})
    layer._emit_dimensions = layer.affinity & layer._scorer_registry.emit_dimensions()
    result = run(layer.analyze_full(make_context("I feel anxious but also hopeful.")))
    emitted = {s.dimension_id for s in result.signals}
    assert emitted <= {8, 9}
    assert 2 not in emitted


def test_static_registry_resolves_bridge_spellings_for_glosses():
    reg = StaticConceptRegistry()
    glosses = reg.glosses(8, ["shoka"])
    assert glosses["shoka"]
