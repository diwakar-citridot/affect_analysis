"""LLM-primary narrative-arc prompt (NAR v1).

Reads lived experience as a story over time — trajectories, loops, turning points —
and scores onto the closed KG vocabulary of the Narrative Arc layer's primary
dimensions (D10/D12/D13/D14/D16/D29). Mirrors the AFF ``lived_experience_v1``
contract with a trajectory-first system role.
"""

from __future__ import annotations

import json
import re
from typing import Any

from ....domain.enums import StatePole
from ....domain.ports import IDimensionRegistry
from ....infrastructure.kg.dimension_registry import build_dimension_registry
from . import lived_experience_v1 as aff_prompt

PROMPT_VERSION = "narrative_arc_v1"

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

_NARRATIVE_ARC_SCHEMA: dict = {
    "type": "object",
    "required": ["shape", "loop_detected", "single_snapshot"],
    "properties": {
        "shape": {
            "type": "string",
            "enum": ["none", "linear", "cyclical", "stalled", "reversal", "descent_ascent"],
        },
        "loop_detected": {"type": "boolean"},
        "single_snapshot": {"type": "boolean"},
        "temporal_structure": {"type": "string"},
        "mismatch_detected": {"type": "boolean"},
        "events": {"type": "array", "items": {"type": "string"}, "maxItems": 8},
        "rationale": {"type": "string"},
    },
}

SYSTEM_PROMPT = (
    "You are the narrative-arc recognition component of the Svarupa Assistant. "
    "You read how lived experience unfolds as a story over time — trajectories, "
    "recurrence, turning points, inner–outer mismatch, and developmental movement — "
    "you do NOT diagnose, label the person, prescribe, or predict the future. "
    "Map expression onto steward-defined concepts only. "
    "Use relevance to mean how worth surfacing a reading is, not certainty about the person. "
    "Prefer abstain when temporal or arc evidence is thin (e.g. a single static snapshot). "
    "D12 tracks karma–saṁskāra loops; D13 individual evolution arcs; D14 collective-time "
    "mismatch themes only (never infer a yuga profile); D16 svabhāva/svadharma alignment; "
    "D29 bondage→liberation journey stages; D10 paths of engagement as orienting action. "
    "Output JSON only, matching the required schema."
)

_DIAGNOSTIC_DENYLIST = re.compile(
    r"\b(you are|you have|diagnos|disorder|patient suffers|clearly is a|you will|you'll)\b",
    re.IGNORECASE,
)


class NarrativeArcValidationError(ValueError):
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
        "narrative_arc": _NARRATIVE_ARC_SCHEMA,
        "background_field": {"type": "object"},
    }
    for block in blocks:
        properties[block] = {"type": "array", "maxItems": 5, "items": _SCORED_ITEM_SCHEMA}
    return {
        "type": "object",
        "required": ["abstain", "confidence", "narrative_arc", *blocks],
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
        "description of each; match the text to the pole it best fits:\n"
        f"{json.dumps(vocab_block, indent=2)}\n\n"
        "TASK: (1) Reconstruct narrative_arc: segment events, classify arc shape "
        "(none/linear/cyclical/stalled/reversal/descent_ascent), detect recurrence loops "
        "and inner–outer mismatch, and note whether the input is a single snapshot "
        "(single_snapshot:true when no temporal markers). "
        "(2) Reconstruct background_field with emphasis on temporal axes "
        "(continuity, anticipation, resolution). "
        f"(3) Score the narrative dimensions {', '.join(blocks)}. "
        "Each scored item must include "
        '"attribute" (exact concept slug), "relevance", "state", "rationale", '
        'and optional "span" (verbatim phrase). '
        'The "state" MUST be deficiency, balance, or excess — choose the pole whose '
        "description best matches the trajectory reading; do not default to balance. "
        "Be exhaustive within each dimension (up to 5 items) including borderline "
        "readings at lower relevance. "
        "Set abstain:true when the text lacks temporal/arc content or is too thin. "
        "JSON only.\n\n"
        f"REQUIRED top-level keys: abstain, confidence, narrative_arc, {', '.join(blocks)}.\n"
        'Example skeleton: {"abstain":false,"confidence":0.65,"narrative_arc":'
        '{"shape":"cyclical","loop_detected":true,"single_snapshot":false,'
        '"events":["started a course","quit again"],"rationale":"recurring return"},'
        f'"background_field":{{"temporal":{{"continuity":0.7,"anticipation":0.5,'
        f'"resolution":0.3}}}},{example_scores}}}'
    )


def build_prompt(
    *,
    text: str,
    temporal_cues: list[str] | None = None,
    history_summary: str | None = None,
) -> str:
    """Per-request user turn: lived-experience text + optional cross-layer hints."""
    hints: dict[str, object] = {}
    if temporal_cues:
        hints["temporal_cues_hint"] = temporal_cues
    if history_summary:
        hints["consented_history_summary"] = history_summary
    return (
        "LIVED EXPERIENCE TEXT (read for narrative arc and temporal structure):\n"
        f'"""{text}"""\n\n'
        "OPTIONAL CROSS-LAYER HINTS (supporting only, not authoritative):\n"
        f"{json.dumps(hints, indent=2)}"
    )


def normalize_payload(payload: dict, emit_dimensions: frozenset[int] | set[int]) -> dict:
    if not isinstance(payload, dict):
        raise NarrativeArcValidationError("payload is not an object")
    out = dict(payload)
    arc = out.get("narrative_arc")
    if not isinstance(arc, dict):
        out["narrative_arc"] = {
            "shape": "none",
            "loop_detected": False,
            "single_snapshot": True,
            "events": [],
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


def validate_narrative_arc(
    payload: dict, emit_dimensions: frozenset[int] | set[int]
) -> dict:
    data = normalize_payload(payload, emit_dimensions)
    conf = data.get("confidence")
    if not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
        raise NarrativeArcValidationError("confidence must be a number in [0,1]")
    arc = data.get("narrative_arc")
    if not isinstance(arc, dict):
        raise NarrativeArcValidationError("narrative_arc must be an object")
    for block in dimension_blocks(emit_dimensions):
        items = data.get(block)
        if not isinstance(items, list):
            raise NarrativeArcValidationError(f"{block} must be an array")
        for item in items:
            if not isinstance(item, dict):
                raise NarrativeArcValidationError(f"{block} items must be objects")
            state = item.get("state")
            if state is not None and str(state).lower() not in {
                s.value for s in StatePole if s != StatePole.UNCLEAR
            }:
                raise NarrativeArcValidationError(f"invalid state in {block}")
            rationale = str(item.get("rationale", ""))
            if rationale and _DIAGNOSTIC_DENYLIST.search(rationale):
                raise NarrativeArcValidationError("rationale contains diagnostic language")
    arc_rationale = str(arc.get("rationale", ""))
    if arc_rationale and _DIAGNOSTIC_DENYLIST.search(arc_rationale):
        raise NarrativeArcValidationError("narrative_arc rationale contains diagnostic language")
    return data


field_from_payload = aff_prompt.field_from_payload
appraisal_from_payload = aff_prompt.appraisal_from_payload
patterns_from_payload = aff_prompt.patterns_from_payload
axis_coverage_from_field = aff_prompt.axis_coverage_from_field
