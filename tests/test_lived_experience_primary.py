"""Tests for AFF v2 LLM-primary lived-experience path."""

from __future__ import annotations

import uuid

import pytest

from svarupa_affect.application.rationale import compose_insightful_rationale
from svarupa_affect.application.analyze_affect import AffectLayer, build_default_layer
from svarupa_affect.application.lived_experience_orchestrator import LivedExperienceOrchestrator
from svarupa_affect.application.safety_shell import SafetyShell
from svarupa_affect.domain.enums import Durability, LatencyMode, StatePole
from svarupa_affect.domain.models import LayerContext
from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.kg.concept_registry import build_concept_registry
from svarupa_affect.infrastructure.kg.scorer_registry import build_scorer_registry
from svarupa_affect.infrastructure.llm.prompts import lived_experience_v1 as prompt_mod

from conftest import run


_FEAR_PAYLOAD = {
    "abstain": False,
    "confidence": 0.78,
    "background_field": {
        "core": {"valence": -0.5, "arousal": 0.7, "vitality": 0.4, "intensity": 0.65},
        "motivation": {"agency": 0.35, "approach": 0.2, "avoidance": 0.75, "control": 0.3},
        "regulation": {"stability": 0.4, "persistence": 0.7, "volatility": 0.5, "regulation": 0.35},
        "relational": {"attachment": 0.3, "trust": 0.4, "social_orientation": -0.1},
        "temporal": {"continuity": 0.6, "anticipation": 0.8, "resolution": 0.2},
    },
    "appraisal": {
        "novelty": 0.4,
        "goal_congruence": -0.5,
        "controllability": 0.25,
        "expectedness": 0.3,
        "responsibility": 0.4,
        "certainty": 0.2,
        "fairness": 0.5,
        "agency": 0.35,
    },
    "experiential_patterns": ["hypervigilance"],
    "d8": [
        {
            "attribute": "bhaya",
            "relevance": 0.85,
            "state": "excess",
            "durability": "enduring",
            "rationale": "Language holds ongoing apprehension before an outcome is known",
            "span": "bracing until I hear back",
        }
    ],
    "d9": [
        {
            "attribute": "cinta",
            "relevance": 0.72,
            "state": "excess",
            "durability": "transient",
            "rationale": "Restless worry threads through the waiting",
            "span": "cannot stop checking my phone",
        }
    ],
    "d2": [
        {
            "attribute": "rajas",
            "relevance": 0.7,
            "state": "excess",
            "rationale": "Restless activation and urgency color the waiting as rajasic excess",
        },
        {
            "attribute": "sattva",
            "relevance": 0.2,
            "state": "balance",
            "rationale": "A thread of clarity remains but does not organize the field",
        },
        {
            "attribute": "tamas",
            "relevance": 0.1,
            "state": "deficiency",
            "rationale": "No settling or withdrawal tone is present in the text",
        },
    ],
}


class _MockPrimaryProvider:
    def __init__(self, payload: dict) -> None:
        self._payload = payload
        self.calls = 0

    async def complete_json(self, **kwargs: object) -> dict:
        self.calls += 1
        return dict(self._payload)


def _build_primary_layer(provider: _MockPrimaryProvider) -> AffectLayer:
    settings = Settings.load()
    concept_registry = build_concept_registry()
    scorer_registry = build_scorer_registry()
    safety_shell = SafetyShell(pole_map_d8=settings.pole_map_d8)
    orchestrator = LivedExperienceOrchestrator(
        provider=provider,
        concept_registry=concept_registry,
        scorer_registry=scorer_registry,
        safety_shell=safety_shell,
        model_id="mock-model",
        timeout_s=5.0,
        max_tokens=2048,
    )
    base = build_default_layer()
    return AffectLayer(
        builder=base._builder,
        appraisal=base._appraisal,
        drivers=base._drivers,
        patterns=base._patterns,
        hypotheses=base._hypotheses,
        dynamics=base._dynamics,
        assembler=base._assembler,
        guna_scorer=base._guna_scorer,
        bridges=base._bridges,
        guna_modulator=base._guna_modulator,
        field_assist=base._field_assist,
        lived_experience=orchestrator,
        affect_mode="llm_primary",
        concept_registry=concept_registry,
        scorer_registry=scorer_registry,
        affinity=concept_registry.affinity(),
    )


def test_compose_insightful_rationale_frames_triplet():
    text = compose_insightful_rationale(
        dimension_id=8,
        dimension_name="Sthāyībhāvas",
        attribute="bhaya",
        state=StatePole.EXCESS,
        llm_rationale="Language holds ongoing apprehension before an outcome is known",
        span="bracing until I hear back",
    )
    assert "Nine Enduring Emotions" in text
    assert "Sthāyībhāvas" in text
    assert "bhaya" in text
    assert "excess" in text
    assert "apprehension" in text
    assert "bracing until I hear back" in text


def test_validate_lived_experience_accepts_fear_payload():
    validated = prompt_mod.validate_lived_experience(_FEAR_PAYLOAD)
    assert validated["d8"][0]["attribute"] == "bhaya"


def test_build_system_includes_concept_coordinate():
    vocabulary = {
        8: [
            {
                "slug": "bhaya",
                "balance": "steady caution without panic",
                "coordinate": {
                    "seat": "Vital-Emotional",
                    "guna": "Tamas + Rajas",
                    "scale": "Individual",
                },
            }
        ]
    }
    system = prompt_mod.build_system(vocabulary)
    assert prompt_mod.PROMPT_VERSION == "lived_experience_v6"
    assert '"coordinate"' in system
    assert "Vital-Emotional" in system
    assert "do not invent coordinates" in system
    assert "bhaya" in system
    assert "every concept listed under Three Gunas" in system
    assert "contributing / meta-construct" in system
    assert "D2 meta-construct discrimination" in system
    assert prompt_mod.LIVED_EXPERIENCE_SCHEMA["properties"]["d2"]["maxItems"] == 7


def test_build_system_injects_d2_discrimination_notes():
    vocabulary = {
        2: [
            {
                "slug": "two-forms-of-brahman",
                "balance": "manifest and unmanifest both honored",
            },
            {
                "slug": "three-gunas-as-daily-veils",
                "balance": "guna modes as veils",
            },
        ]
    }
    system = prompt_mod.build_system(vocabulary)
    assert '"discrimination"' in system
    assert "sayable/unsayable" in system or "unnamed/formless" in system
    assert "Do not substitute (2) or (3) for (1)" in system
    assert "two-forms-of-brahman" in system
    assert "three-gunas-as-daily-veils" in system


@pytest.mark.parametrize(
    "payload",
    [
        {"abstain": True, "confidence": 0.3, "background_field": None, "d8": [], "d9": [], "d2": []},
        {
            "abstain": False,
            "confidence": 0.6,
            "backgroundField": {"core": {"valence": -0.2, "arousal": 0.5, "vitality": 0.4, "intensity": 0.5}},
            "d8": [],
            "d9": [],
            "d2": [],
        },
        {
            "abstain": False,
            "confidence": 0.6,
            "core": {"valence": 0.1, "arousal": 0.4, "vitality": 0.5, "intensity": 0.4},
            "motivation": {"agency": 0.5, "approach": 0.4, "avoidance": 0.3, "control": 0.5},
            "d8": [],
            "d9": [],
            "d2": [],
        },
    ],
)
def test_validate_lived_experience_normalizes_background_field(payload: dict):
    validated = prompt_mod.validate_lived_experience(payload)
    assert isinstance(validated["background_field"], dict)
    assert isinstance(validated["background_field"].get("core"), dict)


def test_safety_shell_whitelists_and_sorts():
    settings = Settings.load()
    shell = SafetyShell(pole_map_d8=settings.pole_map_d8)
    registry = build_concept_registry()
    field = prompt_mod.field_from_payload(_FEAR_PAYLOAD, process_confidence=0.7)
    allowed = registry.slugs(8)
    scores, _ = shell.apply_dimension_scores(
        _FEAR_PAYLOAD["d8"],
        dimension_id=8,
        dimension_name="Sthāyībhāvas",
        field=field,
        allowed_slugs=allowed,
        default_durability=Durability.ENDURING,
    )
    assert scores
    assert scores[0].attribute == "bhaya"
    assert scores[0].state == StatePole.EXCESS
    assert scores[0].rationale
    assert "Nine Enduring Emotions" in scores[0].rationale
    assert "bhaya" in scores[0].rationale
    assert "excess" in scores[0].rationale
    assert "apprehension" in scores[0].rationale
    assert scores[0].span == "bracing until I hear back"
    assert scores[0].reasoning
    assert "0.85" in scores[0].reasoning
    assert "apprehension" not in scores[0].reasoning


def test_llm_primary_analyze_maps_fear_to_bhaya_and_cinta():
    provider = _MockPrimaryProvider(_FEAR_PAYLOAD)
    layer = _build_primary_layer(provider)
    ctx = LayerContext(
        request_id=str(uuid.uuid4()),
        analysis_text="I keep bracing until I hear back and cannot stop checking my phone.",
        affect_mode="llm_primary",
        enable_llm_primary=True,
        force_llm_primary=True,
    )
    result = run(layer.analyze_full(ctx))
    assert provider.calls >= 1
    d8 = next(s for s in result.signals if s.dimension_id == 8)
    d9 = next(s for s in result.signals if s.dimension_id == 9)
    assert not d8.abstained
    assert any(a.attribute == "bhaya" for a in d8.attribute_scores)
    assert any(a.attribute == "cinta" for a in d9.attribute_scores)
    bhaya = next(a for a in d8.attribute_scores if a.attribute == "bhaya")
    cinta = next(a for a in d9.attribute_scores if a.attribute == "cinta")
    assert bhaya.rationale and "Nine Enduring Emotions" in bhaya.rationale
    assert "apprehension" in bhaya.rationale
    assert bhaya.span and "bracing" in bhaya.span
    assert cinta.rationale and "worry" in cinta.rationale
    assert cinta.span and "checking" in cinta.span
    assert bhaya.reasoning and "0.85" in bhaya.reasoning
    assert result.phenomenology_input.provenance.llm_primary_used is True
    assert result.phenomenology_input.provenance.affect_mode == "llm_primary"


def test_llm_primary_abstains_on_factual_short_text():
    provider = _MockPrimaryProvider(_FEAR_PAYLOAD)
    layer = _build_primary_layer(provider)
    ctx = LayerContext(
        request_id=str(uuid.uuid4()),
        analysis_text="The meeting is scheduled for 3pm in conference room B.",
        affect_mode="llm_primary",
        enable_llm_primary=True,
    )
    result = run(layer.analyze_full(ctx))
    assert provider.calls == 0
    assert all(s.abstained for s in result.signals)


def test_legacy_mode_unchanged_without_llm_primary_flag():
    layer = build_default_layer()
    ctx = LayerContext(
        request_id=str(uuid.uuid4()),
        analysis_text="I am absolutely furious that they cancelled the project.",
        affect_mode="legacy_deterministic",
        enable_llm_primary=False,
    )
    result = run(layer.analyze_full(ctx))
    assert result.phenomenology_input.provenance.affect_mode == "legacy_deterministic"


def test_nirveda_pole_descriptions_discriminate_eval_failure_modes():
    """Regression: nirveda deficiency/excess lead text must survive the 700-char trim."""
    from pathlib import Path

    from svarupa_affect.application.lived_experience_orchestrator import _trim_description
    from svarupa_affect.infrastructure.kg.triplet_registry import build_triplet_vocabulary

    vocab = build_triplet_vocabulary(path=Path("data/kg/aff_triplet_descriptions.v1.json"))
    nirveda = vocab.status_descriptions(9, "nirveda")
    def_trim = _trim_description(nirveda["deficiency"])
    exc_trim = _trim_description(nirveda["excess"])
    assert "contagious" in def_trim.lower()
    assert "not bhaya" in def_trim.lower()
    assert "metallic" in exc_trim.lower()
    assert "unlike balanced" in exc_trim.lower()
