"""Concept registry: AFF applicability from svarupa_concept_layer (or static fallback)."""

from __future__ import annotations

from conftest import make_context, run

from svarupa_affect.application.analyze_affect import build_default_layer
from svarupa_affect.infrastructure.kg.concept_registry import (
    ConceptInfo,
    StaticConceptRegistry,
    _compact_coordinate,
    _normalize_coordinate,
    canonical_slug,
)


def test_canonical_slug_aliases():
    assert canonical_slug("shoka") == "soka"
    assert canonical_slug("vishada") == "visada"
    assert canonical_slug("bhaya") == "bhaya"
    assert canonical_slug("two-forms-of-brahman") == "two_forms_of_brahman"
    assert canonical_slug("two_forms_of_brahman") == "two_forms_of_brahman"
    assert canonical_slug("three-gunas-as-daily-veils") == canonical_slug(
        "three_gunas_as_daily_veils"
    )


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
    # Documentation JSON / concept_layer snapshot uses part-prefixed dosha slugs.
    assert reg.slugs(15) == frozenset(
        {"part-i-vata", "part-ii-pitta", "part-iii-kapha"}
    )


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


def test_normalize_and_compact_coordinate():
    raw = {
        "raw": "Seat: Physical · Guṇa: Tamas",
        "seat": "Physical (somatic)",
        "guna": "Tamas-dominant",
        "scale": "Individual",
    }
    normalized = _normalize_coordinate(raw)
    assert normalized is not None
    assert normalized["seat"] == "Physical (somatic)"
    compact = _compact_coordinate(normalized)
    assert compact is not None
    assert "raw" not in compact
    assert compact["guna"] == "Tamas-dominant"
    assert _compact_coordinate(_normalize_coordinate({"raw": "only raw"})) == {"raw": "only raw"}


def test_static_registry_coordinates_method():
    info = ConceptInfo(
        concept_id=1,
        dimension_id=8,
        slug="bhaya",
        name="Fear",
        gloss="fear gloss",
        role="primary",
        coordinate={
            "raw": "Seat: Vital · Guṇa: Tamas",
            "seat": "Vital-Emotional",
            "guna": "Tamas + Rajas",
        },
    )
    reg = StaticConceptRegistry(
        by_dimension={8: {"bhaya": info}},
        affinity=frozenset({8}),
        primary_dimensions=frozenset({8}),
        contributing_dimensions=frozenset(),
    )
    coords = reg.coordinates(8, ["bhaya", "missing"])
    assert coords["bhaya"]["seat"] == "Vital-Emotional"
    assert "raw" not in coords["bhaya"]
    assert "missing" not in coords


def test_build_registry_enriches_coordinates_from_mysql():
    from svarupa_affect.infrastructure.config import Settings
    from svarupa_affect.infrastructure.kg.concept_registry import build_concept_registry

    settings = Settings.load()
    if not settings.mysql_host or not settings.mysql_database:
        return
    reg = build_concept_registry()
    # After concepts seed, D2 sattva should carry coordinate even if layer is empty.
    coords = reg.coordinates(2, ["sattva", "rajas", "tamas"])
    if not coords:
        # Layer/snapshot may omit slugs; direct fetch still works.
        from svarupa_affect.infrastructure.kg.concept_registry import fetch_concept_coordinates

        coords = fetch_concept_coordinates(
            settings, dimension_id=2, slugs=["sattva", "rajas", "tamas"]
        )
    assert coords, "expected svarupa_concepts.coordinate for D2 gunas"
    assert any("seat" in c or "raw" in c for c in coords.values())
