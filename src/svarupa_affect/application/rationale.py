"""Compose public rationales for scored (dimension, attribute, state) triples."""

from __future__ import annotations

from ..domain.enums import StatePole

# Readable dimension families for D2/D8/D9 (matches lived_experience prompt labels).
_DIMENSION_FAMILY: dict[int, str] = {
    2: "Three Gunas",
    8: "Nine Enduring Emotions",
    9: "Thirty-Three Transient States",
}

_STATE_TEXTURE: dict[StatePole, str] = {
    StatePole.DEFICIENCY: "deficiency (under-expressed or absent)",
    StatePole.BALANCE: "balance (present and regulated)",
    StatePole.EXCESS: "excess (over-activated or dysregulated)",
}


def compose_insightful_rationale(
    *,
    dimension_id: int,
    dimension_name: str | None,
    attribute: str,
    state: StatePole,
    llm_rationale: str,
    span: str | None = None,
) -> str:
    """Frame the LLM reading so the triplet and observational basis are explicit."""
    body = llm_rationale.strip().rstrip(".")
    if not body:
        body = "the lived experience aligns with this steward concept at this pole"

    family = _DIMENSION_FAMILY.get(dimension_id, f"dimension {dimension_id}")
    dim_label = family
    if dimension_name and dimension_name.strip():
        dim_label = f"{family} ({dimension_name.strip()})"

    state_label = _STATE_TEXTURE.get(state, state.value)
    text = f"In {dim_label}, {attribute} at {state_label}: {body}."

    span_clean = (span or "").strip()
    if span_clean and span_clean.lower() not in body.lower():
        text += f' Supported by "{span_clean}".'

    return text
