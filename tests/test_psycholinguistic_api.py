"""FastAPI tests for PSY v2 psycholinguistic endpoints."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from svarupa_affect.api.app import create_app
from svarupa_affect.api.dependencies import get_psycholinguistic_layer
from svarupa_affect.application.analyze_psycholinguistic import PsycholinguisticLayer
from svarupa_affect.application.psycholinguistic_orchestrator import (
    LAYER_CODE,
    PsycholinguisticOrchestrator,
)
from svarupa_affect.application.safety_shell import SafetyShell
from svarupa_affect.infrastructure.kg.concept_registry import (
    StaticConceptRegistry,
    _load_static_snapshot,
)
from svarupa_affect.infrastructure.kg.dimension_registry import build_dimension_registry
from svarupa_affect.infrastructure.kg.scorer_registry import StaticScorerRegistry
from svarupa_affect.infrastructure.kg.triplet_registry import (
    build_psycholinguistic_triplet_vocabulary,
)
from tests.test_lived_experience_primary import _MockPrimaryProvider

_FORM_TEXT = (
    "Things keep happening to me. The deadlines were missed. "
    "I was left out again. It always ends up this way."
)

_PSY_PAYLOAD = {
    "abstain": False,
    "confidence": 0.7,
    "psycholinguistic_features": {
        "pronoun_orientation": "first_person_passive",
        "agency_ratio": 0.25,
        "attribution_locus": "external",
        "coherence": 0.45,
        "temporal_orientation": "present_rumination",
        "cognitive_complexity": 0.4,
        "rumination_markers": True,
        "passive_constructions": True,
        "rationale": "Passive voice and external attribution dominate.",
    },
    "background_field": {
        "core": {"valence": -0.2, "arousal": 0.45, "vitality": 0.4, "intensity": 0.4},
        "motivation": {"agency": 0.25, "approach": 0.3, "avoidance": 0.55, "control": 0.3},
        "regulation": {"stability": 0.4, "persistence": 0.35, "volatility": 0.4, "regulation": 0.4},
        "relational": {"attachment": 0.4, "trust": 0.4, "social_orientation": 0.0},
        "temporal": {"continuity": 0.55, "anticipation": 0.35, "resolution": 0.3},
    },
    "d17": [
        {
            "attribute": "the_adhibhautika_perspective",
            "relevance": 0.8,
            "state": "excess",
            "rationale": "External locus and passive constructions.",
            "span": "Things keep happening to me",
        }
    ],
    "d2": [],
    "d12": [],
}


def _static_concept_registry() -> StaticConceptRegistry:
    affinity, primary, contributing, by_dimension = _load_static_snapshot(layer_code=LAYER_CODE)
    return StaticConceptRegistry(
        layer_code=LAYER_CODE,
        by_dimension=by_dimension,
        affinity=affinity,
        primary_dimensions=primary,
        contributing_dimensions=contributing,
    )


def _build_psy_layer() -> PsycholinguisticLayer:
    orchestrator = PsycholinguisticOrchestrator(
        provider=_MockPrimaryProvider(_PSY_PAYLOAD),
        concept_registry=_static_concept_registry(),
        scorer_registry=StaticScorerRegistry(layer_code=LAYER_CODE),
        safety_shell=SafetyShell(),
        model_id="mock",
        triplet_vocabulary=build_psycholinguistic_triplet_vocabulary(),
        dimension_registry=build_dimension_registry(),
        layer_code=LAYER_CODE,
    )
    return PsycholinguisticLayer(orchestrator)


def test_psy_meta_returns_prompt_version():
    app = create_app()
    app.dependency_overrides[get_psycholinguistic_layer] = _build_psy_layer
    client = TestClient(app)
    resp = client.get("/v2/psycholinguistic/meta")
    assert resp.status_code == 200
    body = resp.json()
    assert body["layer"] == "PSY"
    assert body["prompt_version"] == "psycholinguistic_v1"
    assert body["emit_dimensions"] == [2, 12, 17]
    app.dependency_overrides.clear()


def test_psy_analyze_with_mocked_layer():
    app = create_app()
    app.dependency_overrides[get_psycholinguistic_layer] = _build_psy_layer
    client = TestClient(app)
    resp = client.post(
        "/v2/psycholinguistic/analyze",
        json={
            "request_id": str(uuid.uuid4()),
            "analysis_text": _FORM_TEXT,
            "options": {"force": True},
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["layer"] == "PSY"
    assert body["llm_primary_used"] is True
    assert body["psycholinguistic_features"]["attribution_locus"] == "external"
    slugs = {a["attribute"] for a in body["attribute_scores"]}
    assert "the_adhibhautika_perspective" in slugs
    app.dependency_overrides.clear()
