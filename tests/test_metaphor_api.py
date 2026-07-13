"""FastAPI tests for MET v2 metaphor endpoints."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from svarupa_affect.api.app import create_app
from svarupa_affect.api.dependencies import get_metaphor_layer
from svarupa_affect.application.analyze_metaphor import MetaphorLayer
from svarupa_affect.application.metaphor_orchestrator import LAYER_CODE, MetaphorOrchestrator
from svarupa_affect.infrastructure.kg.concept_registry import (
    StaticConceptRegistry,
    _load_static_snapshot,
)
from svarupa_affect.infrastructure.kg.dimension_registry import build_dimension_registry
from svarupa_affect.infrastructure.kg.scorer_registry import StaticScorerRegistry
from svarupa_affect.infrastructure.kg.triplet_registry import build_metaphor_triplet_vocabulary
from tests.test_lived_experience_primary import _MockPrimaryProvider

_METAPHOR_TEXT = "I feel like I'm drowning in deadlines and burnt out at work."

_MET_PAYLOAD = {
    "abstain": False,
    "confidence": 0.74,
    "metaphors": [
        {
            "source": "drowning",
            "target": "overwhelm from deadlines",
            "source_domain": "water",
            "span": "drowning in deadlines",
            "rationale": "Water imagery for overwhelm.",
        },
        {
            "source": "burnt out",
            "target": "exhaustion at work",
            "source_domain": "fire",
            "span": "burnt out",
            "rationale": "Fire/heat imagery for depletion.",
        },
    ],
    "d1": [
        {
            "attribute": "water",
            "relevance": 0.82,
            "state": "excess",
            "rationale": "Drowning imagery.",
            "span": "drowning",
        },
        {
            "attribute": "fire",
            "relevance": 0.7,
            "state": "deficiency",
            "rationale": "Burnt out implies depleted fire.",
            "span": "burnt out",
        },
    ],
    "d5": [],
    "d6": [],
    "d15": [],
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


def _build_met_layer() -> MetaphorLayer:
    orchestrator = MetaphorOrchestrator(
        provider=_MockPrimaryProvider(_MET_PAYLOAD),
        concept_registry=_static_concept_registry(),
        scorer_registry=StaticScorerRegistry(layer_code=LAYER_CODE),
        model_id="mock",
        triplet_vocabulary=build_metaphor_triplet_vocabulary(),
        dimension_registry=build_dimension_registry(),
        layer_code=LAYER_CODE,
    )
    return MetaphorLayer(orchestrator)


def test_met_meta_returns_prompt_version():
    app = create_app()
    app.dependency_overrides[get_metaphor_layer] = _build_met_layer
    client = TestClient(app)
    resp = client.get("/v2/metaphor/meta")
    assert resp.status_code == 200
    body = resp.json()
    assert body["layer"] == "MET"
    assert body["prompt_version"] == "metaphor_v1"
    assert body["emit_dimensions"] == [1, 5, 6, 15]
    app.dependency_overrides.clear()


def test_met_analyze_with_mocked_layer():
    app = create_app()
    app.dependency_overrides[get_metaphor_layer] = _build_met_layer
    client = TestClient(app)
    resp = client.post(
        "/v2/metaphor/analyze",
        json={
            "request_id": str(uuid.uuid4()),
            "analysis_text": _METAPHOR_TEXT,
            "options": {"force": True},
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["layer"] == "MET"
    assert body["llm_primary_used"] is True
    assert any(m["source"] == "drowning" for m in body["metaphors"])
    slugs = {a["attribute"] for a in body["attribute_scores"]}
    assert "water" in slugs
    app.dependency_overrides.clear()
