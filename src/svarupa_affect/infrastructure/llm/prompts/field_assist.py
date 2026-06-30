"""Field-reconstruction assist prompt (§6.2/§6.3).

The LLM is asked to **reconstruct the affective organization of lived experience**, not to
classify an emotion. Pinned ``PROMPT_VERSION`` + system contract + JSON schema live here and
are recorded in provenance. A light, dependency-free validator checks the payload before any
field is read (a full JSON Schema validator drops in if ``jsonschema`` is installed).
"""

from __future__ import annotations

import json

from ....domain.models import AffectiveField

PROMPT_VERSION = "field_assist_v1"

SYSTEM_PROMPT = (
    "You are the affect-reconstruction component of the Svarupa Assistant. "
    "You reconstruct the affective organization of lived experience carried by the text. "
    "You do NOT classify the person's emotion, and you make no labels, predictions, "
    "prescriptions, or verdicts about the person. Voice uncertainty honestly. "
    "Every reconstructed value MUST carry a confidence in [0,1] and a justifying verbatim span. "
    "Use ONLY the supplied candidate attribute vocabulary. Output JSON only, matching the schema."
)

# Manual range spec used by the dependency-free validator below.
FIELD_ASSIST_SCHEMA: dict = {
    "type": "object",
    "required": ["background_field", "appraisal", "confidence", "abstain"],
    "properties": {
        "background_field": {
            "type": "object",
            "groups": ["core", "motivation", "regulation", "relational", "temporal"],
        },
        "foreground_episodes": {"type": "array"},
        "appraisal": {
            "type": "object",
            "keys": [
                "novelty",
                "goal_congruence",
                "controllability",
                "expectedness",
                "responsibility",
                "certainty",
                "fairness",
                "agency",
            ],
        },
        "drivers": {"type": "array"},
        "experiential_patterns": {"type": "array"},
        "interactions": {"type": "array"},
        "dynamics": {"type": "array"},
        "unresolved": {"type": "boolean"},
        "candidate_attributes_d8": {"type": "array"},
        "candidate_attributes_d9": {"type": "array"},
        "confidence": {"type": "number", "min": 0.0, "max": 1.0},
        "abstain": {"type": "boolean"},
    },
}


def build_prompt(
    *,
    text: str,
    field: AffectiveField,
    candidate_d8: list[str],
    candidate_d9: list[str],
    glosses: dict[str, str],
    targets: list[str],
) -> str:
    """Render the user prompt: flagged text + deterministic field + closed vocabulary."""
    det = {
        "core": {
            "valence": field.core.valence.value,
            "arousal": field.core.arousal.value,
            "vitality": field.core.vitality.value,
            "intensity": field.core.intensity.value,
        },
        "motivation": {
            "agency": field.motivation.agency.value,
            "approach": field.motivation.approach.value,
            "avoidance": field.motivation.avoidance.value,
            "control": field.motivation.control.value,
        },
        "regulation": {
            "stability": field.regulation.stability.value,
            "persistence": field.regulation.persistence.value,
            "volatility": field.regulation.volatility.value,
            "regulation": field.regulation.regulation.value,
        },
    }
    return (
        "TEXT (analyze the affective organization carried here):\n"
        f'"""{text}"""\n\n'
        f"DETECTED TARGETS: {targets}\n\n"
        "DETERMINISTIC FIELD (your prior; refine, do not blindly echo):\n"
        f"{json.dumps(det, indent=2)}\n\n"
        f"CANDIDATE D8 ATTRIBUTES (closed set): {candidate_d8}\n"
        f"CANDIDATE D9 ATTRIBUTES (closed set): {candidate_d9}\n"
        f"GLOSSES: {json.dumps(glosses)}\n\n"
        "Reconstruct: background mood vs foreground reactions; enduring vs transient affect; "
        "appraisal (novelty, goal_congruence, controllability, expectedness, responsibility, "
        "certainty, fairness, agency); what drives/maintains it; experiential patterns; "
        "tensions/interactions; what is unresolved; what changes across the narrative. "
        "Every numeric value as {value, confidence, span}. Respond with JSON only.\n\n"
        "REQUIRED top-level keys (exact names): background_field, appraisal, confidence, abstain.\n"
        "background_field MUST wrap core/motivation/regulation/relational/temporal groups.\n"
        'Example skeleton: {"background_field":{"core":{"valence":{"value":0,"confidence":0.5,"span":[0,1]}}},'
        '"appraisal":{},"confidence":0.6,"abstain":false}'
    )


class AssistValidationError(ValueError):
    """Raised when the assist payload fails the (light) schema check."""


_FIELD_GROUPS = ("core", "motivation", "regulation", "relational", "temporal")
_TOP_KEY_ALIASES = {
    "backgroundField": "background_field",
    "affective_field": "background_field",
    "affectiveField": "background_field",
    "field": "background_field",
    "overall_confidence": "confidence",
    "overallConfidence": "confidence",
}


def normalize_assist_payload(payload: dict) -> dict:
    """Coerce common LLM shape drift into the canonical assist envelope."""
    if not isinstance(payload, dict):
        raise AssistValidationError("assist payload is not an object")

    out: dict = {}
    for key, value in payload.items():
        canonical = _TOP_KEY_ALIASES.get(key, key)
        out[canonical] = value

    if "background_field" not in out:
        nested = {g: out[g] for g in _FIELD_GROUPS if isinstance(out.get(g), dict)}
        if nested:
            out["background_field"] = nested
        elif isinstance(out.get("reconstruction"), dict):
            recon = out["reconstruction"]
            if isinstance(recon.get("background_field"), dict):
                out["background_field"] = recon["background_field"]
            else:
                nested = {g: recon[g] for g in _FIELD_GROUPS if isinstance(recon.get(g), dict)}
                if nested:
                    out["background_field"] = nested

    if "appraisal" not in out or not isinstance(out.get("appraisal"), dict):
        out["appraisal"] = out.get("appraisal") if isinstance(out.get("appraisal"), dict) else {}

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

    if "abstain" not in out:
        out["abstain"] = False

    return out


def validate_assist(payload: dict) -> dict:
    """Dependency-free validation of the assist payload against FIELD_ASSIST_SCHEMA."""
    normalized = normalize_assist_payload(payload)
    if not isinstance(normalized, dict):
        raise AssistValidationError("assist payload is not an object")
    for key in FIELD_ASSIST_SCHEMA["required"]:
        if key not in normalized:
            raise AssistValidationError(f"missing required key: {key}")
    conf = normalized.get("confidence")
    if not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
        raise AssistValidationError("confidence must be a number in [0,1]")
    if not isinstance(normalized.get("abstain"), bool):
        raise AssistValidationError("abstain must be a boolean")
    if not isinstance(normalized.get("appraisal"), dict):
        raise AssistValidationError("appraisal must be an object")
    return normalized
