"""LLM-primary metaphor prompt (MET v1).

Detects metaphors in lived experience and maps source imagery onto the closed KG
vocabulary of the Metaphor layer's primary dimensions (from the scorer registry).
Mirrors the AFF ``lived_experience_v1`` contract with a metaphor-first system role.
"""

from __future__ import annotations

import json
import re
from typing import Any

from ....domain.enums import StatePole
from ....domain.ports import IDimensionRegistry
from ....infrastructure.kg.dimension_registry import build_dimension_registry

PROMPT_VERSION = "metaphor_v1"

_POLE_KEYS = ("deficiency", "balance", "excess", "gloss")

_SCORED_ITEM_SCHEMA: dict = {
    "type": "object",
    "required": ["attribute", "relevance", "state"],
    "properties": {
        "attribute": {"type": "string"},
        "relevance": {"type": "number", "min": 0.0, "max": 1.0},
        "state": {"type": "string", "enum": ["deficiency", "balance", "excess"]},
        "rationale": {"type": "string"},
        "span": {"type": "string"},
    },
}

_METAPHOR_ITEM_SCHEMA: dict = {
    "type": "object",
    "required": ["source", "target"],
    "properties": {
        "source": {"type": "string"},
        "target": {"type": "string"},
        "source_domain": {"type": "string"},
        "span": {"type": "string"},
        "rationale": {"type": "string"},
    },
}

SYSTEM_PROMPT = (
    "You are the metaphor-recognition component of the Svarupa Assistant. "
    "You read the metaphors a person uses in the supplied lived experience — the places "
    "where everyday experience is expressed through the imagery of another domain "
    '("I\'m drowning", "burnt out", "stuck in the mud", "scattered to the winds"). '
    "For each metaphor you identify its SOURCE (the image/vehicle) and its TARGET "
    "(the experience being described), then map the source onto steward-defined "
    "elemental / energetic / structural concepts only. "
    "You do NOT diagnose, label the person, prescribe, or predict. "
    "Filter out conventional dead metaphors (e.g. 'grasp an idea', 'run out of time') — "
    "surface only live, imagistic metaphors that carry felt quality. "
    "Use relevance to mean how worth surfacing a reading is, not certainty about the person. "
    "Prefer abstain when the text is literal or metaphor is thin. "
    "Output JSON only, matching the required schema."
)

_TOP_KEY_ALIASES = {
    "overall_confidence": "confidence",
    "overallConfidence": "confidence",
    "sourceTarget": "metaphors",
    "metaphor": "metaphors",
    "mappings": "metaphors",
}

_DIAGNOSTIC_DENYLIST = re.compile(
    r"\b(you are|you have|diagnos|disorder|patient suffers|clearly is a)\b",
    re.IGNORECASE,
)


class MetaphorValidationError(ValueError):
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
        "metaphors": {"type": "array", "maxItems": 8, "items": _METAPHOR_ITEM_SCHEMA},
    }
    for block in blocks:
        properties[block] = {"type": "array", "maxItems": 5, "items": _SCORED_ITEM_SCHEMA}
    return {
        "type": "object",
        "required": ["abstain", "confidence", "metaphors", *blocks],
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
        "Concepts are grouped by dimension; score each source domain under its output key — "
        f"{mapping}. "
        "Each concept lists its poles — deficiency / balance / excess — with a description "
        "of each; match the metaphor's source imagery to the pole it best fits:\n"
        f"{json.dumps(vocab_block, indent=2)}\n\n"
        "TASK: (1) Extract the live metaphors in the text. For each, give its "
        '"source" (the concrete image), its "target" (the experience it describes), '
        'an optional "source_domain", and the "span". '
        f"(2) Map the source imagery onto the closed vocabulary, scoring {', '.join(blocks)}. "
        "Each scored item must include "
        '"attribute" (exact concept slug), "relevance", "state", and optional '
        '"rationale", "span". '
        'The "state" MUST be deficiency, balance, or excess — choose the pole whose '
        "description best matches the imagery; do not default to balance. "
        "Score a dimension only where a metaphor genuinely evokes it — leave its array "
        "empty otherwise. "
        "Set abstain:true when the text is literal or metaphor is too thin. JSON only.\n\n"
        f"REQUIRED top-level keys: abstain, confidence, metaphors, {', '.join(blocks)}.\n"
        'Example skeleton: {"abstain":false,"confidence":0.7,'
        '"metaphors":[{"source":"drowning","target":"emotional overwhelm",'
        '"source_domain":"water","span":"I feel like I\'m drowning"}],'
        f"{example_scores}}}"
    )


def build_prompt(*, text: str) -> str:
    """Per-request user turn: lived-experience text to read for metaphors."""
    return (
        "LIVED EXPERIENCE TEXT (read for metaphor — source imagery and felt quality):\n"
        f'"""{text}"""'
    )


def normalize_payload(payload: dict, emit_dimensions: frozenset[int] | set[int]) -> dict:
    if not isinstance(payload, dict):
        raise MetaphorValidationError("payload is not an object")
    out = {_TOP_KEY_ALIASES.get(k, k): v for k, v in payload.items()}
    if not isinstance(out.get("metaphors"), list):
        out["metaphors"] = []
    for block in dimension_blocks(emit_dimensions):
        if not isinstance(out.get(block), list):
            out[block] = []
    out.setdefault("abstain", False)
    conf = out.get("confidence", 0.5)
    if isinstance(conf, str):
        try:
            conf = float(conf)
        except ValueError:
            conf = 0.5
    try:
        out["confidence"] = float(conf)
    except (TypeError, ValueError):
        out["confidence"] = 0.5
    return out


def _validate_scored_block(block: str, items: object) -> None:
    if not isinstance(items, list):
        raise MetaphorValidationError(f"{block} must be an array")
    for item in items:
        if not isinstance(item, dict):
            raise MetaphorValidationError(f"{block} items must be objects")
        if "attribute" not in item or "relevance" not in item:
            raise MetaphorValidationError(f"{block} items need attribute and relevance")
        rel = float(item["relevance"])
        if not (0.0 <= rel <= 1.0):
            raise MetaphorValidationError(f"{block} relevance out of range")
        state = item.get("state")
        if state is not None and str(state).lower() not in {
            s.value for s in StatePole if s != StatePole.UNCLEAR
        }:
            raise MetaphorValidationError(f"invalid state in {block}")
        rationale = str(item.get("rationale", ""))
        if rationale and _DIAGNOSTIC_DENYLIST.search(rationale):
            raise MetaphorValidationError("rationale uses diagnostic phrasing")


def validate_metaphor(payload: dict, emit_dimensions: frozenset[int] | set[int]) -> dict:
    data = normalize_payload(payload, emit_dimensions)
    conf = data.get("confidence")
    if not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
        raise MetaphorValidationError("confidence must be a number in [0,1]")
    for item in data["metaphors"]:
        if not isinstance(item, dict):
            raise MetaphorValidationError("metaphors items must be objects")
        rationale = str(item.get("rationale", ""))
        if rationale and _DIAGNOSTIC_DENYLIST.search(rationale):
            raise MetaphorValidationError("metaphor rationale uses diagnostic phrasing")
    for block in dimension_blocks(emit_dimensions):
        _validate_scored_block(block, data.get(block))
    return data
