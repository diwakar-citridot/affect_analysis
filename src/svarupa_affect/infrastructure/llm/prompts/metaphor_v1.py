"""LLM-primary metaphor prompt (MET v1).

Layer 4 (MET) detects the metaphors a person uses, extracts their source→target
structure, and maps the *source* domain onto the closed KG vocabulary of the
metaphor layer's PRIMARY dimensions — the felt-quality ontology those metaphors
natively evoke:

    D1  Pañca Mahābhūtas  — Five Great Elements   (elemental: "drowning" → Water)
    D5  Pañca Kośa        — Five Sheaths           (structural: which layer of self)
    D6  Subtle Energies   — Prāṇa / Chakras / Nāḍīs (energetic: "drained", "buzzing")
    D15 Vāta·Pitta·Kapha  — Tridosha               (constitutional: "burning", "heavy")

Scores in one structured call. Pinned ``PROMPT_VERSION`` + system contract live
here. Mirrors the AFF ``lived_experience_v1`` contract.
"""

from __future__ import annotations

import json
import re

PROMPT_VERSION = "metaphor_v1"

# Per-concept keys rendered into the closed-vocabulary block, in stable order.
# Poles come from the MET triplet snapshot; ``gloss`` is the single-text fallback.
_POLE_KEYS = ("deficiency", "balance", "excess", "gloss")

# Human-readable labels for the primary dimensions in the closed vocabulary.
# The model SCORES under the output keys d1/d5/d6/d15 (see task text + schema);
# these names only make the vocabulary block legible.
_DIMENSION_LABELS = {
    1: "Five Great Elements (elemental)",
    5: "Five Sheaths (structural)",
    6: "Subtle Energies (energetic)",
    15: "Tridosha (constitutional)",
}

# Output key (d{dim}) <-> dimension_id.
_DIM_IDS = (1, 5, 6, 15)


def dim_key(dimension_id: int) -> str:
    return f"d{dimension_id}"


SYSTEM_PROMPT = (
    "You are the metaphor-recognition component of the Svarupa Assistant. "
    "You read the metaphors a person uses in the supplied text — the places where "
    "everyday experience is expressed through the imagery of another domain "
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

METAPHOR_SCHEMA: dict = {
    "type": "object",
    "required": ["abstain", "confidence", "metaphors", "d1", "d5", "d6", "d15"],
    "properties": {
        "abstain": {"type": "boolean"},
        "confidence": {"type": "number", "min": 0.0, "max": 1.0},
        "metaphors": {"type": "array", "maxItems": 8, "items": _METAPHOR_ITEM_SCHEMA},
        "d1": {"type": "array", "maxItems": 5, "items": _SCORED_ITEM_SCHEMA},
        "d5": {"type": "array", "maxItems": 5, "items": _SCORED_ITEM_SCHEMA},
        "d6": {"type": "array", "maxItems": 5, "items": _SCORED_ITEM_SCHEMA},
        "d15": {"type": "array", "maxItems": 5, "items": _SCORED_ITEM_SCHEMA},
    },
}

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


def build_system(vocabulary: dict[int, list[dict[str, str]]]) -> str:
    """Static system prefix: contract + closed vocabulary + task/format rules.

    Identical across requests, so the provider sends it as the cacheable system
    prefix (see ``BedrockLLMProvider`` prompt caching). Keep it byte-stable
    (sorted keys, no per-request data) or cross-request cache reads will miss.
    Only the metaphor text (see :func:`build_prompt`) varies per request.
    """
    vocab_block = {
        _DIMENSION_LABELS.get(dim, dim_key(dim)): [
            {"concept": item["slug"], **{k: item[k] for k in _POLE_KEYS if k in item}}
            for item in items
        ]
        for dim, items in sorted(vocabulary.items())
    }
    return (
        f"{SYSTEM_PROMPT}\n\n"
        "CLOSED VOCABULARY (use the exact concept values only; do not invent attributes). "
        "Concepts are grouped by dimension; score each source domain under its output key — "
        "Five Great Elements→d1, Five Sheaths→d5, Subtle Energies→d6, Tridosha→d15. "
        "Each concept lists its poles — deficiency / balance / excess — with a description "
        "of each; match the metaphor's source imagery to the pole it best fits:\n"
        f"{json.dumps(vocab_block, indent=2)}\n\n"
        "TASK: (1) Extract the live metaphors in the text. For each, give its "
        '"source" (the concrete image, e.g. "drowning"), its "target" (the experience '
        'it describes, e.g. "being emotionally overwhelmed"), an optional "source_domain" '
        '(which elemental/energetic/structural family the image belongs to), and the "span". '
        "(2) Map the source imagery onto the closed vocabulary above, scoring d1 (Five "
        "Great Elements), d5 (Five Sheaths), d6 (Subtle Energies), d15 (Tridosha). "
        "Each scored item must include "
        '"attribute" (an exact concept value from the vocabulary above), '
        '"relevance", "state", and optional "rationale", "span". '
        'The "state" is the pole of the attribute and MUST be one of: '
        '"deficiency" (the quality is blocked, flat, drained, absent or under-expressed — '
        'e.g. "burnt out", "empty"), '
        '"balance" (the quality is present and well-proportioned), or '
        '"excess" (the quality is overwhelming, flooding or over-activated — '
        'e.g. "drowning", "on fire"). '
        "Choose the pole whose description above best matches the imagery. "
        "Do not default to balance. Score a dimension only where a metaphor genuinely "
        "evokes it — leave its array empty otherwise. "
        "Set abstain:true when the text is literal or metaphor is too thin. JSON only.\n\n"
        "REQUIRED top-level keys (exact names): abstain, confidence, metaphors, d1, d5, d6, d15.\n"
        'Example skeleton: {"abstain":false,"confidence":0.7,'
        '"metaphors":[{"source":"drowning","target":"emotional overwhelm",'
        '"source_domain":"water","span":"I feel like I\'m drowning"}],'
        '"d1":[{"attribute":"water","relevance":0.8,"state":"excess",'
        '"span":"drowning"}],"d5":[],"d6":[],"d15":[]}'
    )


def build_prompt(*, text: str) -> str:
    """Render the per-request user turn: the text to read for metaphors.

    The static grounding (contract, closed vocabulary, task/format rules) lives in
    :func:`build_system` so it can be cached as a stable prefix. Keeping the
    volatile text here — after the cached prefix — makes cross-request prompt
    caching effective.
    """
    return "TEXT TO ANALYZE FOR METAPHOR:\n" f'"""{text}"""'


def normalize_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise MetaphorValidationError("payload is not an object")
    out: dict = {}
    for key, value in payload.items():
        canonical = _TOP_KEY_ALIASES.get(key, key)
        out[canonical] = value
    for key in ("metaphors", *(dim_key(d) for d in _DIM_IDS)):
        if not isinstance(out.get(key), list):
            out[key] = []
    if "abstain" not in out:
        out["abstain"] = False
    conf = out.get("confidence")
    if isinstance(conf, str):
        try:
            conf = float(conf)
        except ValueError:
            conf = None
    if conf is not None:
        out["confidence"] = conf
    elif "confidence" not in out:
        out["confidence"] = 0.5
    return out


def validate_metaphor(payload: dict) -> dict:
    data = normalize_payload(payload)
    conf = data.get("confidence")
    if not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
        raise MetaphorValidationError("confidence must be a number in [0,1]")
    for item in data["metaphors"]:
        if not isinstance(item, dict):
            raise MetaphorValidationError("metaphors items must be objects")
        rationale = str(item.get("rationale", ""))
        if rationale and _DIAGNOSTIC_DENYLIST.search(rationale):
            raise MetaphorValidationError("metaphor rationale uses diagnostic phrasing")
    for dim in _DIM_IDS:
        block = dim_key(dim)
        items = data.get(block)
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
            rationale = str(item.get("rationale", ""))
            if rationale and _DIAGNOSTIC_DENYLIST.search(rationale):
                raise MetaphorValidationError("rationale uses diagnostic phrasing")
    return data
