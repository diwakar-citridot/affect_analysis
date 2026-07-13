"""LLM-primary psycholinguistic prompt (PSY v1).

Reads the *form* of lived-experience language — pronouns, agency, attribution,
coherence, temporal orientation — and scores onto the closed KG vocabulary of
the Psycholinguistic layer's primary dimensions (D2/D12/D17). Mirrors the AFF
``lived_experience_v1`` contract with a form-first system role.
"""

from __future__ import annotations

import json
import re
from typing import Any

from ....domain.enums import StatePole
from ....domain.ports import IDimensionRegistry
from ....infrastructure.kg.dimension_registry import build_dimension_registry
from . import lived_experience_v1 as aff_prompt

PROMPT_VERSION = "psycholinguistic_v1"

_POLE_KEYS = ("deficiency", "balance", "excess", "gloss")

_SCORED_ITEM_SCHEMA: dict = {
    "type": "object",
    "required": ["attribute", "relevance", "state", "rationale"],
    "properties": {
        "attribute": {"type": "string"},
        "relevance": {"type": "number", "min": 0.0, "max": 1.0},
        "state": {"type": "string", "enum": ["deficiency", "balance", "excess"]},
        "rationale": {"type": "string"},
        "span": {"type": "string"},
    },
}

_PSY_FEATURES_SCHEMA: dict = {
    "type": "object",
    "required": ["attribution_locus", "agency_ratio"],
    "properties": {
        "pronoun_orientation": {"type": "string"},
        "agency_ratio": {"type": "number", "min": 0.0, "max": 1.0},
        "attribution_locus": {
            "type": "string",
            "enum": ["external", "fate", "internal", "mixed", "unclear"],
        },
        "coherence": {"type": "number", "min": 0.0, "max": 1.0},
        "temporal_orientation": {"type": "string"},
        "cognitive_complexity": {"type": "number", "min": 0.0, "max": 1.0},
        "rumination_markers": {"type": "boolean"},
        "passive_constructions": {"type": "boolean"},
        "rationale": {"type": "string"},
    },
}

SYSTEM_PROMPT = (
    "You are the psycholinguistic recognition component of the Svarupa Assistant. "
    "You read the FORM of language in lived experience — pronouns, agency vs passivity, "
    "attribution locus, coherence vs fragmentation, temporal orientation, and rumination "
    "markers — you do NOT diagnose, label the person, prescribe, or predict. "
    "Map linguistic form onto steward-defined concepts only. "
    "Use relevance to mean how worth surfacing a reading is, not certainty about the person. "
    "Prefer abstain when the text is too short or linguistically thin. "
    "D17 tracks attribution lenses (external/material, fate/cosmic, internal/self); "
    "D2 tracks sattva–rajas–tamas via coherence, agency, and fragmentation of form "
    "(not affective tone — that belongs to AFF); "
    "D12 tracks rumination / loop markers in language (not full narrative arc — that "
    "belongs to NAR). "
    "Output JSON only, matching the required schema."
)

_DIAGNOSTIC_DENYLIST = re.compile(
    r"\b(you are|you have|diagnos|disorder|patient suffers|clearly is a|you will|you'll)\b",
    re.IGNORECASE,
)


class PsycholinguisticValidationError(ValueError):
    """Raised when the LLM payload fails schema or philosophy checks."""


def dim_key(dimension_id: int) -> str:
    return f"d{dimension_id}"


def dimension_blocks(emit_dimensions: frozenset[int] | set[int]) -> tuple[str, ...]:
    return tuple(dim_key(d) for d in sorted(emit_dimensions))


def build_schema(emit_dimensions: frozenset[int] | set[int]) -> dict:
    blocks = dimension_blocks(emit_dimensions)
    properties: dict[str, Any] = {
        "abstain": {"type": "boolean"},
        "confidence": {"type": "number", "min": 0.0, "max": 1.0},
        "psycholinguistic_features": _PSY_FEATURES_SCHEMA,
        "background_field": {"type": "object"},
    }
    for block in blocks:
        properties[block] = {"type": "array", "maxItems": 5, "items": _SCORED_ITEM_SCHEMA}
    return {
        "type": "object",
        "required": ["abstain", "confidence", "psycholinguistic_features", *blocks],
        "properties": properties,
    }


def build_system(
    vocabulary: dict[int, list[dict[str, str]]],
    *,
    dimension_registry: IDimensionRegistry | None = None,
) -> str:
    """Static system prefix: contract + closed vocabulary + task/format rules."""
    reg = dimension_registry or build_dimension_registry()
    vocab_block = {
        reg.name_for(dim): [
            {"concept": item["slug"], **{k: item[k] for k in _POLE_KEYS if k in item}}
            for item in items
        ]
        for dim, items in sorted(vocabulary.items())
    }
    blocks = dimension_blocks(vocabulary)
    mapping = ", ".join(f"{reg.name_for(int(b[1:]))}→{b}" for b in blocks)
    example_scores = ", ".join(f'"{b}":[]' for b in blocks)
    return (
        f"{SYSTEM_PROMPT}\n\n"
        "CLOSED VOCABULARY (use the exact concept values only; do not invent attributes). "
        "Concepts are grouped by dimension; score each concept under its output key — "
        f"{mapping}. "
        "Each concept lists its poles — deficiency / balance / excess — with a "
        "description of each; match the linguistic form to the pole it best fits:\n"
        f"{json.dumps(vocab_block, indent=2)}\n\n"
        "TASK: (1) Reconstruct psycholinguistic_features from linguistic form: "
        "pronoun_orientation, agency_ratio (0=fully passive, 1=fully agentive), "
        "attribution_locus (external/fate/internal/mixed/unclear), coherence, "
        "temporal_orientation, cognitive_complexity, rumination_markers, "
        "passive_constructions. "
        "(2) Reconstruct background_field with emphasis on motivation.agency and "
        "temporal axes (supporting only). "
        f"(3) Score the psycholinguistic dimensions {', '.join(blocks)}. "
        "Each scored item must include "
        '"attribute" (exact concept slug), "relevance", "state", "rationale", '
        'and optional "span" (verbatim phrase). '
        'The "state" MUST be deficiency, balance, or excess — choose the pole whose '
        "description best matches the linguistic form; do not default to balance. "
        "Be exhaustive within each dimension (up to 5 items) including borderline "
        "readings at lower relevance. "
        "Set abstain:true when the text is too thin for form-based reading. "
        "JSON only.\n\n"
        f"REQUIRED top-level keys: abstain, confidence, psycholinguistic_features, "
        f"{', '.join(blocks)}.\n"
        'Example skeleton: {"abstain":false,"confidence":0.65,'
        '"psycholinguistic_features":{"attribution_locus":"external","agency_ratio":0.3,'
        '"rumination_markers":true,"coherence":0.4,"rationale":"passive + external blame"},'
        f'"background_field":{{"motivation":{{"agency":0.3}}}},{example_scores}}}'
    )


def build_prompt(*, text: str) -> str:
    """Per-request user turn: lived-experience text for form analysis."""
    return (
        "LIVED EXPERIENCE TEXT (read for linguistic form — pronouns, agency, "
        "attribution, coherence — not for affective tone alone):\n"
        f'"""{text}"""'
    )


def normalize_payload(payload: dict, emit_dimensions: frozenset[int] | set[int]) -> dict:
    if not isinstance(payload, dict):
        raise PsycholinguisticValidationError("payload is not an object")
    out = dict(payload)
    feats = out.get("psycholinguistic_features")
    if not isinstance(feats, dict):
        out["psycholinguistic_features"] = {
            "attribution_locus": "unclear",
            "agency_ratio": 0.5,
        }
    out["background_field"] = aff_prompt._coerce_background_field(
        out.get("background_field"), out
    )
    for block in dimension_blocks(emit_dimensions):
        if block not in out or not isinstance(out.get(block), list):
            out[block] = []
    if "abstain" not in out:
        out["abstain"] = False
    conf = out.get("confidence")
    if conf is None:
        conf = 0.5
    try:
        out["confidence"] = float(conf)
    except (TypeError, ValueError):
        out["confidence"] = 0.5
    return out


def validate_psycholinguistic(
    payload: dict, emit_dimensions: frozenset[int] | set[int]
) -> dict:
    data = normalize_payload(payload, emit_dimensions)
    conf = data.get("confidence")
    if not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
        raise PsycholinguisticValidationError("confidence must be a number in [0,1]")
    feats = data.get("psycholinguistic_features")
    if not isinstance(feats, dict):
        raise PsycholinguisticValidationError("psycholinguistic_features must be an object")
    for block in dimension_blocks(emit_dimensions):
        items = data.get(block)
        if not isinstance(items, list):
            raise PsycholinguisticValidationError(f"{block} must be an array")
        for item in items:
            if not isinstance(item, dict):
                raise PsycholinguisticValidationError(f"{block} items must be objects")
            state = item.get("state")
            if state is not None and str(state).lower() not in {
                s.value for s in StatePole if s != StatePole.UNCLEAR
            }:
                raise PsycholinguisticValidationError(f"invalid state in {block}")
            rationale = str(item.get("rationale", ""))
            if rationale and _DIAGNOSTIC_DENYLIST.search(rationale):
                raise PsycholinguisticValidationError("rationale contains diagnostic language")
    feat_rationale = str(feats.get("rationale", ""))
    if feat_rationale and _DIAGNOSTIC_DENYLIST.search(feat_rationale):
        raise PsycholinguisticValidationError(
            "psycholinguistic_features rationale contains diagnostic language"
        )
    return data


field_from_payload = aff_prompt.field_from_payload
appraisal_from_payload = aff_prompt.appraisal_from_payload
patterns_from_payload = aff_prompt.patterns_from_payload
axis_coverage_from_field = aff_prompt.axis_coverage_from_field
