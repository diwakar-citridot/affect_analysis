"""FastAPI tests for NAR v2 narrative-arc endpoints."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from svarupa_affect.api.app import create_app
from svarupa_affect.api.dependencies import get_narrative_arc_layer
from svarupa_affect.application.analyze_narrative_arc import NarrativeArcLayer
from svarupa_affect.application.narrative_arc_orchestrator import (
    LAYER_CODE,
    NarrativeArcOrchestrator,
)
from svarupa_affect.application.safety_shell import SafetyShell
from svarupa_affect.infrastructure.kg.concept_registry import build_concept_registry
from svarupa_affect.infrastructure.kg.dimension_registry import build_dimension_registry
from svarupa_affect.infrastructure.kg.scorer_registry import build_scorer_registry
from svarupa_affect.infrastructure.kg.triplet_registry import build_narrative_triplet_vocabulary

from tests.test_lived_experience_primary import _MockPrimaryProvider

_LOOP_TEXT = (
    "I started a course but I quit. Then I started a project, but I quit again. "
    "I keep going back to the same pattern."
)

_NAR_PAYLOAD = {
    "abstain": False,
    "confidence": 0.72,
    "narrative_arc": {
        "shape": "cyclical",
        "loop_detected": True,
        "single_snapshot": False,
        "events": ["started a course", "quit again"],
        "rationale": "Recurring return to the same conflict pattern.",
    },
    "background_field": {
        "core": {"valence": -0.2, "arousal": 0.5, "vitality": 0.4, "intensity": 0.45},
        "motivation": {"agency": 0.4, "approach": 0.3, "avoidance": 0.5, "control": 0.35},
        "regulation": {"stability": 0.35, "persistence": 0.3, "volatility": 0.4, "regulation": 0.4},
        "relational": {"attachment": 0.4, "trust": 0.45, "social_orientation": 0.0},
        "temporal": {"continuity": 0.7, "anticipation": 0.5, "resolution": 0.25},
    },
    "d12": [
        {
            "attribute": "agami_karma",
            "relevance": 0.78,
            "state": "excess",
            "rationale": "Fresh choices repeat an old quitting pattern.",
            "span": "quit again",
        }
    ],
    "d10": [],
    "d13": [],
    "d14": [],
    "d16": [],
    "d29": [],
}


def _build_nar_layer() -> NarrativeArcLayer:
    concept_registry = build_concept_registry(layer_code=LAYER_CODE)
    scorer_registry = build_scorer_registry(layer_code=LAYER_CODE)
    orchestrator = NarrativeArcOrchestrator(
        provider=_MockPrimaryProvider(_NAR_PAYLOAD),
        concept_registry=concept_registry,
        scorer_registry=scorer_registry,
        safety_shell=SafetyShell(),
        model_id="mock",
        triplet_vocabulary=build_narrative_triplet_vocabulary(),
        dimension_registry=build_dimension_registry(),
        layer_code=LAYER_CODE,
    )
    return NarrativeArcLayer(orchestrator)


def test_nar_meta_returns_prompt_version():
    client = TestClient(create_app())
    resp = client.get("/v2/narrative-arc/meta")
    assert resp.status_code == 200
    body = resp.json()
    assert body["layer"] == "NAR"
    assert body["prompt_version"] == "narrative_arc_v1"
    assert 12 in body["emit_dimensions"]


def test_nar_analyze_with_mocked_layer():
    app = create_app()
    app.dependency_overrides[get_narrative_arc_layer] = _build_nar_layer
    client = TestClient(app)
    resp = client.post(
        "/v2/narrative-arc/analyze",
        json={
            "request_id": str(uuid.uuid4()),
            "analysis_text": _LOOP_TEXT,
            "options": {"force": True},
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["layer"] == "NAR"
    assert body["llm_primary_used"] is True
    assert body["narrative_arc"]["loop_detected"] is True
    slugs = {a["attribute"] for a in body["attribute_scores"]}
    assert "agami_karma" in slugs
    app.dependency_overrides.clear()
