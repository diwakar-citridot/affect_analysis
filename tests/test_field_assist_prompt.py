"""Field-assist prompt: field reconstruction only (no Rasa vocabulary)."""

from __future__ import annotations

from conftest import make_field

from svarupa_affect.infrastructure.llm.prompts.field_assist import (
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    build_prompt,
)


def test_build_prompt_focuses_on_field_refinement_not_rasa_vocabulary():
    prompt = build_prompt(
        text="sample text",
        field=make_field({"core.valence": 0.1}),
        targets=["self"],
    )
    assert "DETERMINISTIC FIELD" in prompt
    assert "background_field" in prompt
    assert "Do not name Rasa attributes" in prompt
    assert "CANDIDATE D8" not in prompt
    assert "GLOSSES" not in prompt


def test_system_prompt_matches_field_only_scope():
    assert "Rasa" in SYSTEM_PROMPT
    assert "candidate attribute" not in SYSTEM_PROMPT.lower()


def test_prompt_version_bumped_for_slim_contract():
    assert PROMPT_VERSION == "field_assist_v3"
