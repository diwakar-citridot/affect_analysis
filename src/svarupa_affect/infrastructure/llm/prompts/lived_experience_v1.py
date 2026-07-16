"""LLM-primary lived-experience prompt (AFF v2).

Scores the affective organization of free-text lived experience onto closed KG vocabulary
(D2/D8/D9) in one structured call. Pinned ``PROMPT_VERSION`` + system contract live here.
"""

from __future__ import annotations

import json
import re

from ....domain.enums import (
    Durability,
    EvidenceKind,
    ExperientialPatternType,
    FieldAxis,
    StatePole,
)
from ....domain.models import (
    AffectiveField,
    AppraisalProfile,
    CoreAffect,
    Evidence,
    ExperientialPattern,
    FieldUncertainty,
    Motivation,
    ReconstructedFeature,
    Regulation,
    Relational,
    Temporal,
)
from ....domain.scoring import clip

PROMPT_VERSION = "lived_experience_v4"

# Per-concept keys rendered into the closed-vocabulary block, in stable order.
# Poles come from the triplet snapshot; ``gloss`` is the legacy single-text fallback.
# ``coordinate`` is the concept's KG location (seat/guna/scale/…) when available.
_POLE_KEYS = ("deficiency", "balance", "excess", "gloss")
_META_KEYS = ("coordinate",)

# Human-readable labels for the primary dimensions in the closed vocabulary.
# The model still SCORES under the output keys d2/d8/d9 (see the task text +
# schema); these names only make the vocabulary block legible.
_DIMENSION_LABELS = {
    2: "Three Gunas",
    8: "Nine Enduring Emotions",
    9: "Thirty-Three Transient States",
}

SYSTEM_PROMPT = (
    "You are the affect-recognition component of the Svarupa Assistant. "
    "You read how lived experience is organized in the supplied text — you do NOT diagnose, "
    "label the person, prescribe, or predict. Map expression onto steward-defined concepts only. "
    "Use relevance to mean how worth surfacing a reading is, not certainty about the person. "
    "Prefer abstain when evidence is thin. "
    "D8 attributes are enduring sthāyībhāvas; D9 are transient vyabhicārībhāvas. "
    "Output JSON only, matching the required schema."
)

_SCORED_ITEM_SCHEMA: dict = {
    "type": "object",
    "required": ["attribute", "relevance", "state", "rationale"],
    "properties": {
        "attribute": {"type": "string"},
        "relevance": {"type": "number", "min": 0.0, "max": 1.0},
        "state": {"type": "string", "enum": ["deficiency", "balance", "excess"]},
        "durability": {"type": "string"},
        "rationale": {"type": "string"},
        "span": {"type": "string"},
    },
}

LIVED_EXPERIENCE_SCHEMA: dict = {
    "type": "object",
    "required": ["abstain", "confidence", "background_field", "d8", "d9", "d2"],
    "properties": {
        "abstain": {"type": "boolean"},
        "confidence": {"type": "number", "min": 0.0, "max": 1.0},
        "background_field": {"type": "object"},
        "appraisal": {"type": "object"},
        "experiential_patterns": {"type": "array"},
        "d8": {"type": "array", "maxItems": 5, "items": _SCORED_ITEM_SCHEMA},
        "d9": {"type": "array", "maxItems": 5, "items": _SCORED_ITEM_SCHEMA},
        "d2": {"type": "array", "maxItems": 3, "items": _SCORED_ITEM_SCHEMA},
    },
}

_FIELD_GROUPS = ("core", "motivation", "regulation", "relational", "temporal")
_TOP_KEY_ALIASES = {
    "backgroundField": "background_field",
    "affective_field": "background_field",
    "affectiveField": "background_field",
    "field": "background_field",
    "overall_confidence": "confidence",
    "overallConfidence": "confidence",
}
_APPRAISAL_KEYS = (
    "novelty",
    "goal_congruence",
    "controllability",
    "expectedness",
    "responsibility",
    "certainty",
    "fairness",
    "agency",
)

_AXIS_RANGES: dict[str, tuple[float, float]] = {
    "core.valence": (-1.0, 1.0),
    "relational.social_orientation": (-1.0, 1.0),
    "goal_congruence": (-1.0, 1.0),
    "fairness": (-1.0, 1.0),
}

_DIAGNOSTIC_DENYLIST = re.compile(
    r"\b(you are|you have|diagnos|disorder|patient suffers|clearly is a)\b",
    re.IGNORECASE,
)


class LivedExperienceValidationError(ValueError):
    """Raised when the LLM payload fails schema or philosophy checks."""


def build_system(vocabulary: dict[int, list[dict[str, object]]]) -> str:
    """Static system prefix: contract + closed vocabulary + task/format rules.

    This content is identical across requests, so the provider sends it as the
    (cacheable) system prefix — see ``BedrockLLMProvider`` prompt caching. Keep it
    byte-stable (sorted keys, no per-request data) or cross-request cache reads
    will miss. Only the lived-experience text + hints (see :func:`build_prompt`)
    vary per request.
    """
    vocab_block = {
        _DIMENSION_LABELS.get(dim, f"d{dim}"): [
            {
                "concept": item["slug"],
                **{k: item[k] for k in _POLE_KEYS if k in item},
                **{k: item[k] for k in _META_KEYS if k in item},
            }
            for item in items
        ]
        for dim, items in sorted(vocabulary.items())
    }
    return (
        f"{SYSTEM_PROMPT}\n\n"
        "CLOSED VOCABULARY (use the exact concept values only; do not invent attributes). "
        "Concepts are grouped by dimension; score each concept under its output key — "
        "Three Gunas→d2, Nine Enduring Emotions→d8, Thirty-Three Transient States→d9. "
        "Each concept lists its poles — deficiency / balance / excess — with a "
        "description of each; match the text to the pole it best fits. "
        "When a concept includes a \"coordinate\" object (seat, ontic mode, valence, "
        "guṇa, scale, causal status, key relation), use it as grounding for how and "
        "where that concept typically shows up — do not invent coordinates:\n"
        f"{json.dumps(vocab_block, indent=2)}\n\n"
        "TASK: Reconstruct background_field (core, motivation, regulation, relational, temporal), "
        "optional appraisal and experiential_patterns, and score d8 (Nine Enduring Emotions — enduring), "
        "d9 (Thirty-Three Transient States — transient), d2 (Three Gunas — sattva/rajas/tamas felt tone). "
        "Each scored item must include "
        '"attribute" (an exact concept value from the vocabulary above), '
        '"relevance", "state", "rationale", and optional "durability", "span". '
        'The "state" is the pole of the attribute and MUST be one of: '
        '"deficiency" (the quality is blocked, flat, numb, absent or under-expressed), '
        '"balance" (the quality is present and well-regulated), or '
        '"excess" (the quality is over-activated, dysregulated or overwhelming). '
        "Choose the pole whose description above best matches the text; where only a "
        "balance description is given, still infer deficiency or excess from the text. "
        "Do not default to balance. "
        "Be exhaustive within each dimension: list every concept whose pole description "
        "plausibly matches the text (up to 5 per dimension), including secondary and "
        "borderline readings at lower relevance — do not stop at the single strongest "
        "concept. A deficiency pole describes the ABSENCE of the concept's quality; "
        "consider deficiency readings even when the concept itself is not overtly present. "
        'For every scored triple, "rationale" MUST be 1–2 sentences explaining why that '
        "attribute and state belong in the response: name the dimension (Three Gunas / "
        "Nine Enduring Emotions / Thirty-Three Transient States), cite how the lived "
        "experience aligns with that concept's pole description (and coordinate when "
        "present), and describe the "
        "recognition in observational language — never diagnose, label the person, or "
        'prescribe. When helpful, add "span" with a short verbatim phrase from the text. '
        "Set abstain:true when affect is absent or too thin. "
        "Keep background_field axes numeric only; omit experiential_patterns and appraisal "
        "unless they materially clarify the reading. JSON only.\n\n"
        "REQUIRED top-level keys (exact names): abstain, confidence, background_field, d8, d9, d2.\n"
        "background_field MUST be an object wrapping core/motivation/regulation/relational/temporal.\n"
        'Example skeleton: {"abstain":false,"confidence":0.65,"background_field":{"core":{"valence":0.1,'
        '"arousal":0.6,"vitality":0.5,"intensity":0.55},"motivation":{"agency":0.5,"approach":0.4,'
        '"avoidance":0.3,"control":0.45},"regulation":{"stability":0.5,"persistence":0.4,"volatility":0.35,'
        '"regulation":0.5},"relational":{"attachment":0.4,"trust":0.5,"social_orientation":0.0},'
        '"temporal":{"continuity":0.5,"anticipation":0.6,"resolution":0.4}},'
        '"d8":[{"attribute":"<concept>","relevance":0.6,"state":"balance",'
        '"rationale":"Brief why this enduring emotion and pole fit the text.",'
        '"span":"optional verbatim phrase"}],"d9":[],"d2":[]}'
    )


def build_prompt(
    *,
    text: str,
    shared_valence: float | None = None,
    shared_arousal: float | None = None,
    temporal_cues: list[str] | None = None,
) -> str:
    """Render the per-request user turn: lived-experience text + optional hints.

    The static grounding (system contract, closed vocabulary, task/format rules)
    lives in :func:`build_system` so it can be cached as a stable prefix. Keeping
    the volatile text here — after the cached prefix — is what makes cross-request
    prompt caching effective.
    """
    hints: dict[str, object] = {}
    if shared_valence is not None:
        hints["shared_valence_hint"] = shared_valence
    if shared_arousal is not None:
        hints["shared_arousal_hint"] = shared_arousal
    if temporal_cues:
        hints["temporal_cues_hint"] = temporal_cues
    return (
        "LIVED EXPERIENCE TEXT:\n"
        f'"""{text}"""\n\n'
        "OPTIONAL CROSS-LAYER HINTS (supporting only, not authoritative):\n"
        f"{json.dumps(hints, indent=2)}"
    )


def _default_background_field() -> dict:
    neutral = 0.5
    return {
        "core": {
            "valence": 0.0,
            "arousal": neutral,
            "vitality": neutral,
            "intensity": 0.3,
        },
        "motivation": {
            "agency": neutral,
            "approach": 0.4,
            "avoidance": 0.3,
            "control": neutral,
        },
        "regulation": {
            "stability": neutral,
            "persistence": 0.4,
            "volatility": 0.3,
            "regulation": neutral,
        },
        "relational": {
            "attachment": 0.4,
            "trust": neutral,
            "social_orientation": 0.0,
        },
        "temporal": {
            "continuity": neutral,
            "anticipation": 0.4,
            "resolution": 0.45,
        },
    }


def _hoist_background_field(payload: dict) -> dict | None:
    nested = {g: payload[g] for g in _FIELD_GROUPS if isinstance(payload.get(g), dict)}
    if nested:
        return nested
    recon = payload.get("reconstruction")
    if isinstance(recon, dict):
        if isinstance(recon.get("background_field"), dict):
            return recon["background_field"]
        nested = {g: recon[g] for g in _FIELD_GROUPS if isinstance(recon.get(g), dict)}
        if nested:
            return nested
    return None


def _coerce_background_field(raw: object, payload: dict) -> dict:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    hoisted = _hoist_background_field(payload)
    if hoisted:
        return hoisted
    return _default_background_field()


def normalize_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise LivedExperienceValidationError("payload is not an object")
    out: dict = {}
    for key, value in payload.items():
        canonical = _TOP_KEY_ALIASES.get(key, key)
        out[canonical] = value
    out["background_field"] = _coerce_background_field(out.get("background_field"), out)
    for key in ("d8", "d9", "d2", "experiential_patterns"):
        if key not in out:
            out[key] = []
    if "appraisal" not in out or not isinstance(out.get("appraisal"), dict):
        out["appraisal"] = {}
    if "abstain" not in out:
        out["abstain"] = False
    conf = out.get("confidence")
    if conf is None and isinstance(out.get("meta"), dict):
        conf = out["meta"].get("confidence")
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


def validate_lived_experience(payload: dict) -> dict:
    data = normalize_payload(payload)
    if not isinstance(data.get("background_field"), dict):
        raise LivedExperienceValidationError("background_field must be an object")
    conf = data.get("confidence")
    if not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
        raise LivedExperienceValidationError("confidence must be a number in [0,1]")
    for block in ("d8", "d9", "d2"):
        items = data.get(block)
        if not isinstance(items, list):
            raise LivedExperienceValidationError(f"{block} must be an array")
        for item in items:
            if not isinstance(item, dict):
                raise LivedExperienceValidationError(f"{block} items must be objects")
            if "attribute" not in item or "relevance" not in item:
                raise LivedExperienceValidationError(f"{block} items need attribute and relevance")
            rel = float(item["relevance"])
            if not (0.0 <= rel <= 1.0):
                raise LivedExperienceValidationError(f"{block} relevance out of range")
            rationale = str(item.get("rationale", "")).strip()
            if not rationale:
                raise LivedExperienceValidationError(f"{block} items need a non-empty rationale")
            if _DIAGNOSTIC_DENYLIST.search(rationale):
                raise LivedExperienceValidationError("rationale uses diagnostic phrasing")
    return data


def _num(val: object, default: float = 0.0) -> float:
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, dict) and isinstance(val.get("value"), (int, float)):
        return float(val["value"])
    return default


def _feat(axis_key: str, val: object, process_conf: float) -> ReconstructedFeature:
    lo, hi = _AXIS_RANGES.get(axis_key, (0.0, 1.0))
    if isinstance(val, dict):
        v = _num(val, (lo + hi) / 2.0)
        conf_raw = val.get("confidence")
        if isinstance(conf_raw, (int, float)):
            c = float(conf_raw)
        else:
            c = process_conf
    else:
        v = _num(val, (lo + hi) / 2.0)
        c = process_conf
    return ReconstructedFeature(value=round(clip(v, lo, hi), 4), confidence=round(clip(c), 4))


def field_from_payload(payload: dict, *, process_confidence: float) -> AffectiveField:
    """Map LLM ``background_field`` onto the hierarchical :class:`AffectiveField`."""
    bg = payload["background_field"]
    conf = process_confidence

    def group(name: str, attrs: tuple[str, ...]) -> dict[str, ReconstructedFeature]:
        block = bg.get(name, {}) if isinstance(bg.get(name), dict) else {}
        out: dict[str, ReconstructedFeature] = {}
        for attr in attrs:
            key = f"{name}.{attr}" if name != "core" else f"core.{attr}"
            out[attr] = _feat(key, block.get(attr), conf)
        return out

    core = group("core", ("valence", "arousal", "vitality", "intensity"))
    mot = group("motivation", ("agency", "approach", "avoidance", "control"))
    reg = group("regulation", ("stability", "persistence", "volatility", "regulation"))
    rel = group("relational", ("attachment", "trust", "social_orientation"))
    tmp = group("temporal", ("continuity", "anticipation", "resolution"))

    ambiguity = clip(1.0 - conf)
    return AffectiveField(
        core=CoreAffect(**core),
        motivation=Motivation(**mot),
        regulation=Regulation(**reg),
        relational=Relational(**rel),
        temporal=Temporal(**tmp),
        uncertainty=FieldUncertainty(
            ambiguity=ReconstructedFeature(value=round(ambiguity, 4), confidence=conf),
            confidence=ReconstructedFeature(value=round(conf, 4), confidence=conf),
            evidence_quality=ReconstructedFeature(value=round(conf, 4), confidence=conf),
        ),
        evidence=[
            Evidence(
                kind=EvidenceKind.FIELD,
                detail="background_field from lived_experience_v1",
                source="lived_experience_orchestrator",
                weight=conf,
            )
        ],
    )


def appraisal_from_payload(payload: dict, *, process_confidence: float) -> AppraisalProfile:
    block = payload.get("appraisal", {})
    if not isinstance(block, dict):
        block = {}
    feats = {
        key: _feat(key, block.get(key), process_confidence) for key in _APPRAISAL_KEYS
    }
    return AppraisalProfile(**feats)


def patterns_from_payload(payload: dict, *, process_confidence: float) -> list[ExperientialPattern]:
    raw = payload.get("experiential_patterns", [])
    if not isinstance(raw, list):
        return []
    out: list[ExperientialPattern] = []
    for item in raw:
        label = item if isinstance(item, str) else str(item.get("type", ""))
        try:
            ptype = ExperientialPatternType(label)
        except ValueError:
            continue
        strength = 0.7
        if isinstance(item, dict) and isinstance(item.get("strength"), (int, float)):
            strength = float(item["strength"])
        out.append(
            ExperientialPattern(
                type=ptype,
                strength=ReconstructedFeature(
                    value=round(clip(strength), 4),
                    confidence=process_confidence,
                ),
                evidence=[
                    Evidence(
                        kind=EvidenceKind.FIELD,
                        detail=f"pattern '{label}' from lived_experience_v1",
                        source="lived_experience_orchestrator",
                    )
                ],
            )
        )
    return out


def parse_state(raw: object) -> StatePole:
    if isinstance(raw, str):
        try:
            return StatePole(raw.lower())
        except ValueError:
            return StatePole.UNCLEAR
    return StatePole.UNCLEAR


def parse_durability(raw: object, *, default: Durability) -> Durability:
    if isinstance(raw, str):
        try:
            return Durability(raw.lower())
        except ValueError:
            return default
    return default


def axis_coverage_from_field(field: AffectiveField) -> dict[FieldAxis, float]:
    prefixes = ("core.", "motivation.", "regulation.", "relational.", "temporal.")
    return {
        axis: field.feature(axis).confidence
        for axis in FieldAxis
        if axis.value.startswith(prefixes)
    }
