"""LLM field-assist degradation (§6, §7.1): never crash, never fabricate a field."""

from __future__ import annotations

from conftest import make_context, make_field, run

from svarupa_affect.application.field_assist import FieldAssist, is_ambiguous
from svarupa_affect.domain.exceptions import ModelUnavailable
from svarupa_affect.infrastructure.llm.bedrock_provider import NullLLMProvider


def _ambiguous_field():
    return make_field(
        {
            "motivation.approach": 0.6,
            "motivation.avoidance": 0.6,
            "uncertainty.ambiguity": 0.7,
            "core.valence": -0.1,
        }
    )


class _Timeout:
    async def complete_json(self, **kwargs):
        raise ModelUnavailable("timeout")


class _SchemaInvalid:
    async def complete_json(self, **kwargs):
        return {"not": "valid"}  # missing required keys -> validate_assist raises every time


class _Good:
    async def complete_json(self, **kwargs):
        return {
            "background_field": {
                "core": {"valence": {"value": -0.6, "confidence": 0.8, "span": [0, 5]}}
            },
            "appraisal": {},
            "confidence": 0.8,
            "abstain": False,
        }


def _assist(provider):
    return FieldAssist(provider=provider)


def _neutral_field():
    return make_field(
        {"core.valence": -0.1, "motivation.approach": 0.1, "motivation.avoidance": 0.1}
    )


def _call(
    provider, field, *, vad_valence=-0.1, lexical_valence=-0.1, margin=0.1, irony=0.0, **ctx_kw
):
    ctx = make_context("x", enable_llm_assist=True, **ctx_kw)
    return run(
        _assist(provider).maybe_assist(
            ctx,
            field,
            vad_valence=vad_valence,
            lexical_valence=lexical_valence,
            margin=margin,
            irony=irony,
            targets=["self"],
        )
    )


def test_gate_fires_on_ambivalence():
    fired, reasons = is_ambiguous(_ambiguous_field(), -0.1, -0.1, 0.1, 0.0)
    assert fired and reasons


def test_clear_gate_skips_without_force():
    field = _neutral_field()
    assert not is_ambiguous(field, -0.1, -0.1, 0.4, 0.0)[0]
    res = _call(_Good(), field, margin=0.4)
    assert res.used is False
    assert res.attempted is False
    assert res.reasons == []


def test_force_llm_assist_bypasses_clear_gate():
    field = _neutral_field()
    res = _call(_Good(), field, force_llm_assist=True, margin=0.4)
    assert res.attempted is True
    assert res.used is True
    assert res.reasons[0] == "force_llm_assist"


def test_force_requires_enable_llm_assist():
    field = _neutral_field()
    ctx = make_context("x", enable_llm_assist=False, force_llm_assist=True)
    res = run(
        _assist(_Good()).maybe_assist(
            ctx,
            field,
            vad_valence=-0.1,
            lexical_valence=-0.1,
            margin=0.4,
            irony=0.0,
            targets=["self"],
        )
    )
    assert res.attempted is False
    assert "assist_disabled" in res.reasons


def test_mapper_maps_force_llm_assist():
    from svarupa_affect.api.dtos import AnalyzeOptions, AnalyzeRequest
    from svarupa_affect.application.mappers import to_context

    ctx = to_context(
        AnalyzeRequest(
            analysis_text="hello",
            options=AnalyzeOptions(enable_llm_assist=True, force_llm_assist=True),
        )
    )
    assert ctx.force_llm_assist is True


def test_mapper_uses_env_defaults_when_options_omitted(monkeypatch):
    from svarupa_affect.api.dtos import AnalyzeRequest
    from svarupa_affect.application.mappers import to_context

    monkeypatch.setenv("SVARUPA_ENABLE_LLM_ASSIST", "1")
    monkeypatch.setenv("SVARUPA_FORCE_LLM_ASSIST", "1")
    ctx = to_context(AnalyzeRequest(analysis_text="hello"))
    assert ctx.enable_llm_assist is True
    assert ctx.force_llm_assist is True


def test_mapper_request_overrides_env_force(monkeypatch):
    from svarupa_affect.api.dtos import AnalyzeOptions, AnalyzeRequest
    from svarupa_affect.application.mappers import to_context

    monkeypatch.setenv("SVARUPA_FORCE_LLM_ASSIST", "1")
    ctx = to_context(
        AnalyzeRequest(
            analysis_text="hello",
            options=AnalyzeOptions(force_llm_assist=False),
        )
    )
    assert ctx.force_llm_assist is False


def test_timeout_degrades_to_deterministic():
    field = _ambiguous_field()
    res = _call(_Timeout(), field)
    assert res.used is False
    assert res.field is field  # unchanged


def test_schema_invalid_is_dropped():
    field = _ambiguous_field()
    res = _call(_SchemaInvalid(), field)
    assert res.used is False


def test_normalize_top_level_field_groups():
    from svarupa_affect.infrastructure.llm.prompts.field_assist import (
        normalize_assist_payload,
        validate_assist,
    )

    raw = {
        "core": {"valence": {"value": -0.4, "confidence": 0.7, "span": [0, 5]}},
        "appraisal": {"novelty": {"value": 0.3, "confidence": 0.5, "span": [0, 1]}},
        "confidence": 0.75,
    }
    validated = validate_assist(normalize_assist_payload(raw))
    assert "background_field" in validated
    assert "core" in validated["background_field"]


def test_good_assist_reconciles_into_field():
    field = _ambiguous_field()
    res = _call(_Good(), field)
    assert res.used is True
    assert res.field.core.valence.value < 0  # reconciled toward the assist value


def test_null_provider_default_degrades():
    field = _ambiguous_field()
    res = _call(NullLLMProvider(), field)
    assert res.used is False


def test_layer_runs_without_llm(layer):
    # default layer uses NullLLMProvider -> deterministic path, no crash
    out = run(layer.analyze_full(make_context("I am anxious but also hopeful.")))
    assert out.phenomenology_input.provenance.llm_assist_used is False
