"""FastAPI tests for AFF FYI / Short Note endpoints."""

from __future__ import annotations

import re
import uuid

import pytest
from fastapi.testclient import TestClient

from svarupa_affect.api.app import create_app
from svarupa_affect.api.app_v2 import create_v2_app
from svarupa_affect.api.dependencies import get_fyi_layer
from svarupa_affect.application.formulate_fyi import FyiLayer
from svarupa_affect.application.fyi_orchestrator import FyiOrchestrator
from svarupa_affect.infrastructure.kg.dimension_registry import build_dimension_registry
from svarupa_affect.infrastructure.kg.triplet_registry import build_triplet_vocabulary
from svarupa_affect.infrastructure.llm.prompts import fyi_short_note_v2 as prompt_mod
from svarupa_affect.infrastructure.llm.prompts.fyi_short_note_v2 import FyiValidationError

_ALASYA_LIVED_EXPERIENCE = (
    "I've moved it from one side to the other for eight days now. "
    "Every time I think about doing it, the task feels heavier than it should."
)

_ALASYA_SIGNAL = {
    "attribute": "alasya",
    "relevance": 0.6522,
    "state": "excess",
    "dimension_name": "Vyabhicārībhāvas",
    "durability": "transient",
    "rationale": (
        "The eight-day pattern of moving the form without completing it matches "
        "excess inertia where every action requires enormous effort."
    ),
    "span": "I've moved it from one side to the other for eight days now",
}

_FYI_PAYLOAD = {
    "cards": [
        {
            "text": (
                "A small task may sit moved from side to side for many days untouched. "
                "There may be a heaviness where even a trivial action starts to feel enormous."
            ),
            "simple_sentence": (
                "A trivial task can grow heavier the longer waiting replaces action. "
                "Inertia excess can feel like movement that never completes."
            ),
            "reasoning": (
                "Triplet alasya excess on Vyabhicārībhāvas; eight-day task shuffle anchored "
                "Mirror; rationale and grounding shaped Lens toward heaviness."
            ),
            "attribute": "alasya",
            "dimension": "Vyabhicārībhāvas",
            "status": "excess",
        }
    ]
}

_AMARSHA_BAD_RESPONSE = {
    "cards": [
        {
            "text": (
                "You named it precisely — a low burning sensation in your chest, "
                "still present three days on. "
                "There is a kind of anger that stays composed on the surface while "
                "the body quietly holds the heat, replaying what was never answered."
            ),
            "simple_sentence": (
                "Swallowed anger can feel like composure while the chest keeps its own slow count. "
                "The burn doesn't always cool just because the reply was never sent."
            ),
            "reasoning": "Internal notes.",
            "attribute": "amarsha",
            "dimension": "Vyabhicārībhāvas",
            "status": "excess",
        }
    ]
}

_AMARSHA_COMPLIANT_PAYLOAD = {
    "cards": [
        {
            "text": (
                "A low burn in the chest can linger days after a reply is withheld. "
                "There may be a kind of heat held inward while composure stays on the surface."
            ),
            "simple_sentence": (
                "Swallowed heat can keep burning quietly beneath a composed surface. "
                "The body may carry what the moment never releases."
            ),
            "reasoning": (
                "Triplet amarsha excess on Vyabhicārībhāvas; chest burn anchored Mirror; "
                "rationale and grounding drove inward-held heat in Lens."
            ),
            "attribute": "amarsha",
            "dimension": "Vyabhicārībhāvas",
            "status": "excess",
        }
    ]
}

_PERSONAL_PRONOUN = re.compile(
    r"\b(?:i|me|my|mine|you|your|yours|yourself|myself)"
    r"(?:[''](?:ve|d|ll|m|re))?\b",
    re.IGNORECASE,
)


class _RetryThenSucceedProvider:
    """Returns non-compliant payload first, compliant on second call."""

    def __init__(self, bad: dict, good: dict) -> None:
        self._bad = bad
        self._good = good
        self.calls = 0

    async def complete_json(self, **kwargs: object) -> dict:
        self.calls += 1
        return dict(self._bad if self.calls == 1 else self._good)


class _MockFyiProvider:
    def __init__(self, payload: dict) -> None:
        self._payload = payload
        self.calls = 0
        self.last_prompt = ""

    async def complete_json(self, **kwargs: object) -> dict:
        self.calls += 1
        self.last_prompt = str(kwargs.get("prompt", ""))
        return dict(self._payload)


def _build_fyi_layer(provider: _MockFyiProvider | _RetryThenSucceedProvider) -> FyiLayer:
    orchestrator = FyiOrchestrator(
        provider=provider,
        dimension_registry=build_dimension_registry(),
        triplet_vocabulary=build_triplet_vocabulary(),
        model_id="mock-model",
        timeout_s=5.0,
        max_tokens=2048,
    )
    return FyiLayer(orchestrator)


def _assert_impersonal(prose: str) -> None:
    assert not _PERSONAL_PRONOUN.search(prose), f"personal pronoun in: {prose!r}"


def test_validate_fyi_rejects_generic_mirror_without_lived_resonance():
    payload = dict(_FYI_PAYLOAD)
    payload["cards"] = [
        {
            **(_FYI_PAYLOAD["cards"][0]),
            "text": (
                "Life can feel difficult when ordinary demands pile up quietly. "
                "There may be a heaviness where even a trivial action starts to feel enormous."
            ),
            "reasoning": (
                "Triplet alasya excess on Vyabhicārībhāvas; eight-day task shuffle anchored "
                "Mirror; rationale shaped Lens."
            ),
        }
    ]
    with pytest.raises(FyiValidationError, match="does not resonate with lived experience"):
        prompt_mod.validate_fyi(
            payload,
            expected_count=1,
            analysis_text=_ALASYA_LIVED_EXPERIENCE,
            signals=[_ALASYA_SIGNAL],
        )


def test_validate_fyi_rejects_text_that_ignores_rationale():
    payload = dict(_FYI_PAYLOAD)
    payload["cards"] = [
        {
            **(_FYI_PAYLOAD["cards"][0]),
            "text": (
                "A small task may sit moved from side to side for many days untouched. "
                "There may be a sharp brightness where attention keeps leaping ahead."
            ),
            "simple_sentence": (
                "Waiting can feel like motion without arrival. "
                "Attention may keep leaping ahead of the body."
            ),
            "reasoning": (
                "Triplet alasya excess on Vyabhicārībhāvas; task shuffle anchored Mirror; "
                "rationale shaped Lens."
            ),
        }
    ]
    with pytest.raises(FyiValidationError, match="does not resonate with signal rationale"):
        prompt_mod.validate_fyi(
            payload,
            expected_count=1,
            analysis_text=_ALASYA_LIVED_EXPERIENCE,
            signals=[_ALASYA_SIGNAL],
        )


def test_validate_fyi_accepts_resonant_payload_with_context():
    prompt_mod.validate_fyi(
        _FYI_PAYLOAD,
        expected_count=1,
        analysis_text=_ALASYA_LIVED_EXPERIENCE,
        signals=[_ALASYA_SIGNAL],
    )


def test_validate_fyi_accepts_amarsha_compliant_payload():
    validated = prompt_mod.validate_fyi(_AMARSHA_COMPLIANT_PAYLOAD, expected_count=1)
    assert validated["cards"][0]["attribute"] == "amarsha"
    assert validated["cards"][0]["text"].count(".") == 2
    _assert_impersonal(validated["cards"][0]["text"])


def test_validate_fyi_accepts_compliant_payload():
    validated = prompt_mod.validate_fyi(_FYI_PAYLOAD, expected_count=1)
    assert validated["cards"][0]["attribute"] == "alasya"
    _assert_impersonal(validated["cards"][0]["text"])


def test_validate_fyi_rejects_personal_pronouns_in_text():
    with pytest.raises(FyiValidationError, match="must not use I/me/my or you/your"):
        prompt_mod.validate_fyi(_AMARSHA_BAD_RESPONSE, expected_count=1)


def test_validate_fyi_rejects_three_sentence_text():
    payload = {
        "cards": [
            {
                **(_FYI_PAYLOAD["cards"][0]),
                "text": (
                    "A low burn in the chest can linger days after a reply is withheld. "
                    "There may be a kind of heat held inward while composure stays on the surface. "
                    "Something here may be smoldering longer than the silence was meant to settle."
                ),
            }
        ]
    }
    with pytest.raises(FyiValidationError, match="exactly 2 sentences"):
        prompt_mod.validate_fyi(payload, expected_count=1)


def test_validate_fyi_rejects_i_in_text():
    payload = {
        "cards": [
            {
                **(_FYI_PAYLOAD["cards"][0]),
                "text": (
                    "A low burn in the chest can linger days after a reply is withheld. "
                    "There may be a kind of heat held inward while I stay composed on the surface."
                ),
            }
        ]
    }
    with pytest.raises(FyiValidationError, match="must not use I/me/my or you/your"):
        prompt_mod.validate_fyi(payload, expected_count=1)


def test_validate_fyi_rejects_long_lens_sentence():
    payload = {
        "cards": [
            {
                **(_FYI_PAYLOAD["cards"][0]),
                "text": (
                    "A low burn in the chest can linger days after a reply is withheld. "
                    "There may be a kind of anger that stays composed on the surface while "
                    "the body quietly holds the heat and keeps replaying what was never answered."
                ),
            }
        ]
    }
    with pytest.raises(FyiValidationError, match="sentence 2 has"):
        prompt_mod.validate_fyi(payload, expected_count=1)


def test_build_prompt_includes_lived_experience():
    prompt = prompt_mod.build_prompt(
        analysis_text=_ALASYA_LIVED_EXPERIENCE,
        signals=[{"attribute": "alasya", "state": "excess", "grounding_for_state": "..."}],
    )
    assert "LIVED EXPERIENCE TEXT:" in prompt
    assert "eight days" in prompt
    system = prompt_mod.build_system()
    assert "triplet" in system.lower()
    assert "grounding_for_state" in system
    assert "CRISP TEXT" in system
    assert "RESONANCE CHECK" in system


def test_enrich_signal_includes_triplet_fields():
    from svarupa_affect.application.fyi_orchestrator import FyiOrchestrator, FyiSignalInput

    orch = FyiOrchestrator(
        provider=_MockFyiProvider(_FYI_PAYLOAD),
        dimension_registry=build_dimension_registry(),
        triplet_vocabulary=build_triplet_vocabulary(),
        model_id="mock",
    )
    enriched = orch._enrich_signal(
        FyiSignalInput(
            attribute="amarsha",
            relevance=0.65,
            state="excess",
            dimension_name="Vyabhicārībhāvas",
            span="low burning sensation in my chest",
        )
    )
    assert enriched["triplet"]["attribute"] == "amarsha"
    assert enriched["grounding_for_state"]
    assert "transient" in str(enriched["dimension_register"]).lower()
    assert enriched["state_pole_hint"]


def test_fyi_meta_returns_prompt_version():
    client = TestClient(create_app())
    resp = client.get("/v2/affect/fyi/meta")
    assert resp.status_code == 200
    body = resp.json()
    assert body["artifact"] == "ShortNote"
    assert body["prompt_version"] == "fyi_short_note_v6"
    assert body["max_signals_per_request"] == 3


def test_fyi_formulate_with_mocked_layer():
    provider = _MockFyiProvider(_FYI_PAYLOAD)
    app = create_app()
    app.dependency_overrides[get_fyi_layer] = lambda: _build_fyi_layer(provider)
    client = TestClient(app)
    resp = client.post(
        "/v2/affect/fyi",
        json={
            "request_id": str(uuid.uuid4()),
            "analysis_text": _ALASYA_LIVED_EXPERIENCE,
            "signals": [_ALASYA_SIGNAL],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["llm_used"] is True
    assert body["prompt_version"] == "fyi_short_note_v6"
    card = body["cards"][0]
    _assert_impersonal(card["text"])
    _assert_impersonal(card["simple_sentence"])
    assert card["text"].count(".") == 2
    assert provider.calls >= 1
    app.dependency_overrides.clear()


def test_fyi_retries_and_succeeds_on_second_attempt():
    provider = _RetryThenSucceedProvider(_AMARSHA_BAD_RESPONSE, _AMARSHA_COMPLIANT_PAYLOAD)
    app = create_app()
    app.dependency_overrides[get_fyi_layer] = lambda: _build_fyi_layer(provider)
    client = TestClient(app)
    resp = client.post(
        "/v2/affect/fyi",
        json={
            "analysis_text": (
                "I told myself I was being the bigger person by not responding to that email, "
                "but three days later I still feel a low burning sensation in my chest "
                "whenever I think about it."
            ),
            "signals": [
                {
                    "attribute": "amarsha",
                    "relevance": 0.6522,
                    "state": "excess",
                    "dimension_name": "Vyabhicārībhāvas",
                    "durability": "transient",
                    "rationale": "Persistent low burn, swallowed rather than expressed.",
                    "span": "low burning sensation in my chest",
                }
            ],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["prompt_version"] == "fyi_short_note_v6"
    _assert_impersonal(body["cards"][0]["text"])
    assert provider.calls == 2
    app.dependency_overrides.clear()


def test_fyi_retries_when_llm_returns_noncompliant_payload():
    provider = _MockFyiProvider(_AMARSHA_BAD_RESPONSE)
    app = create_app()
    app.dependency_overrides[get_fyi_layer] = lambda: _build_fyi_layer(provider)
    client = TestClient(app)
    resp = client.post(
        "/v2/affect/fyi",
        json={"analysis_text": _ALASYA_LIVED_EXPERIENCE, "signals": [_ALASYA_SIGNAL]},
    )
    assert resp.status_code == 502
    assert provider.calls == 3
    app.dependency_overrides.clear()


def test_fyi_standalone_app():
    provider = _MockFyiProvider(_FYI_PAYLOAD)
    app = create_v2_app()
    app.dependency_overrides[get_fyi_layer] = lambda: _build_fyi_layer(provider)
    client = TestClient(app)
    resp = client.post(
        "/affect/fyi",
        json={"analysis_text": _ALASYA_LIVED_EXPERIENCE, "signals": [_ALASYA_SIGNAL]},
    )
    assert resp.status_code == 200
    assert resp.json()["llm_used"] is True
    app.dependency_overrides.clear()


def test_fyi_rejects_more_than_three_signals():
    client = TestClient(create_app())
    resp = client.post(
        "/v2/affect/fyi",
        json={"analysis_text": _ALASYA_LIVED_EXPERIENCE, "signals": [_ALASYA_SIGNAL] * 4},
    )
    assert resp.status_code == 422
