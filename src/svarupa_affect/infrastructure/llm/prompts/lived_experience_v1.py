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

PROMPT_VERSION = "lived_experience_v1"

SYSTEM_PROMPT = (
    "You are the affect-recognition component of the Svarupa Assistant. "
    "You read how lived experience is organized in the supplied text — you do NOT diagnose, "
    "label the person, prescribe, or predict. Map expression onto steward-defined concepts only. "
    "Use relevance to mean how worth surfacing a reading is, not certainty about the person. "
    "Prefer abstain when evidence is thin. "
    "D8 attributes are enduring sthāyībhāvas; D9 are transient vyabhicārībhāvas. "
    "Output JSON only, matching the required schema."
)

LIVED_EXPERIENCE_SCHEMA: dict = {
    "type": "object",
    "required": ["abstain", "confidence", "background_field", "d8", "d9", "d2"],
    "properties": {
        "abstain": {"type": "boolean"},
        "confidence": {"type": "number", "min": 0.0, "max": 1.0},
        "background_field": {"type": "object"},
        "appraisal": {"type": "object"},
        "experiential_patterns": {"type": "array"},
        "d8": {"type": "array", "maxItems": 5},
        "d9": {"type": "array", "maxItems": 5},
        "d2": {"type": "array", "maxItems": 3},
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


def build_prompt(
    *,
    text: str,
    vocabulary: dict[int, list[dict[str, str]]],
    shared_valence: float | None = None,
    shared_arousal: float | None = None,
    temporal_cues: list[str] | None = None,
) -> str:
    """Render the user prompt: text + closed vocabulary blocks + optional fusion hints."""
    hints: dict[str, object] = {}
    if shared_valence is not None:
        hints["shared_valence_hint"] = shared_valence
    if shared_arousal is not None:
        hints["shared_arousal_hint"] = shared_arousal
    if temporal_cues:
        hints["temporal_cues_hint"] = temporal_cues

    vocab_block = {
        str(dim): [{"slug": item["slug"], "gloss": item["gloss"]} for item in items]
        for dim, items in sorted(vocabulary.items())
    }
    return (
        "LIVED EXPERIENCE TEXT:\n"
        f'"""{text}"""\n\n'
        f"OPTIONAL CROSS-LAYER HINTS (supporting only, not authoritative):\n"
        f"{json.dumps(hints, indent=2)}\n\n"
        f"CLOSED VOCABULARY (use slug values only; do not invent attributes):\n"
        f"{json.dumps(vocab_block, indent=2)}\n\n"
        "TASK: Reconstruct background_field (core, motivation, regulation, relational, temporal), "
        "optional appraisal and experiential_patterns, and score d8 (enduring), d9 (transient), "
        "d2 (sattva/rajas/tamas felt tone). Each scored item must include "
        '"attribute", "relevance", optional "state", "durability", "rationale", "span". '
        "Set abstain:true when affect is absent or too thin. JSON only.\n\n"
        "REQUIRED top-level keys (exact names): abstain, confidence, background_field, d8, d9, d2.\n"
        "background_field MUST be an object wrapping core/motivation/regulation/relational/temporal.\n"
        'Example skeleton: {"abstain":false,"confidence":0.65,"background_field":{"core":{"valence":0.1,'
        '"arousal":0.6,"vitality":0.5,"intensity":0.55},"motivation":{"agency":0.5,"approach":0.4,'
        '"avoidance":0.3,"control":0.45},"regulation":{"stability":0.5,"persistence":0.4,"volatility":0.35,'
        '"regulation":0.5},"relational":{"attachment":0.4,"trust":0.5,"social_orientation":0.0},'
        '"temporal":{"continuity":0.5,"anticipation":0.6,"resolution":0.4}},"d8":[],"d9":[],"d2":[]}\n'
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
            rationale = str(item.get("rationale", ""))
            if rationale and _DIAGNOSTIC_DENYLIST.search(rationale):
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
