"""FastAPI tests for AFF v2 lived-experience endpoints."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from svarupa_affect.api.app import create_app
from svarupa_affect.api.app_v2 import create_v2_app
from svarupa_affect.api.dependencies import get_layer
from svarupa_affect.application.analyze_affect import AffectLayer

from tests.test_lived_experience_primary import (
    _FEAR_PAYLOAD,
    _MockPrimaryProvider,
    _build_primary_layer,
)


def _primary_layer() -> AffectLayer:
    return _build_primary_layer(_MockPrimaryProvider(_FEAR_PAYLOAD))


def test_v2_health_on_combined_app():
    client = TestClient(create_app())
    resp = client.get("/v2/health")
    assert resp.status_code == 200
    assert resp.json()["affect_mode"] == "llm_primary"


def test_v2_meta_returns_prompt_version():
    client = TestClient(create_app())
    resp = client.get("/v2/meta")
    assert resp.status_code == 200
    body = resp.json()
    assert body["affect_mode"] == "llm_primary"
    assert body["prompt_version"] == "lived_experience_v2"
    assert 8 in body["emit_dimensions"]


def test_v2_analyze_with_mocked_layer():
    app = create_app()
    app.dependency_overrides[get_layer] = _primary_layer
    client = TestClient(app)
    resp = client.post(
        "/v2/analyze",
        json={
            "request_id": str(uuid.uuid4()),
            "analysis_text": "I keep bracing until I hear back and cannot stop checking my phone.",
            "options": {"force": True},
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["affect_mode"] == "llm_primary"
    assert body["llm_primary_used"] is True
    slugs = {a["attribute"] for a in body["attribute_scores"]}
    assert "bhaya" in slugs
    assert "cinta" in slugs
    for score in body["attribute_scores"]:
        assert score.get("reasoning"), f"missing reasoning for {score['attribute']}"
    bhaya = next(a for a in body["attribute_scores"] if a["attribute"] == "bhaya")
    assert "bracing" in bhaya["reasoning"]
    app.dependency_overrides.clear()


def test_v2_standalone_app_analyze():
    app = create_v2_app()
    app.dependency_overrides[get_layer] = _primary_layer
    client = TestClient(app)
    resp = client.post(
        "/analyze",
        json={
            "analysis_text": "I keep bracing until I hear back.",
            "options": {"force": True},
        },
    )
    assert resp.status_code == 200
    assert resp.json()["llm_primary_used"] is True
    app.dependency_overrides.clear()


def test_v2_factual_text_abstains_without_force():
    app = create_v2_app()
    app.dependency_overrides[get_layer] = _primary_layer
    client = TestClient(app)
    resp = client.post(
        "/analyze",
        json={
            "analysis_text": (
                "The meeting is scheduled for 3pm in conference room B on the second floor."
            ),
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["llm_primary_used"] is False
    assert len(body["abstained_dimensions"]) >= 1
    app.dependency_overrides.clear()
