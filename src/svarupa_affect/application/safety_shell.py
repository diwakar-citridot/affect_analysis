"""Deterministic safety shell for AFF v2 LLM-primary scoring.

Whitelist slugs, clamp relevances, apply pole rules, and enforce abstention floors.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..domain.enums import Durability, EvidenceKind, StatePole
from ..domain.models import AffectiveField, AttributeScore, Evidence
from ..domain.scoring import GAMMA, dimension_relevance, saturate, select_pole
from ..infrastructure.kg.concept_registry import canonical_slug

_RELEVANCE_ITEM_FLOOR = 0.15
_TOP_K = 5


class SafetyShell:
    def __init__(self, *, pole_map_d8: Path | None = None, relevance_floor: float = 0.12) -> None:
        self.relevance_floor = relevance_floor
        self._d8_pole_rules: dict[str, str] = {}
        if pole_map_d8 is not None and pole_map_d8.is_file():
            data = json.loads(pole_map_d8.read_text(encoding="utf-8"))
            self._d8_pole_rules = dict(data.get("attributes", {}))

    def apply_dimension_scores(
        self,
        items: list[dict],
        *,
        dimension_id: int,
        field: AffectiveField,
        allowed_slugs: frozenset[str],
        default_durability: Durability,
    ) -> tuple[list[AttributeScore], list[Evidence]]:
        intensity = field.core.intensity.value
        arousal = field.core.arousal.value
        regulation = field.regulation.regulation.value

        scores: list[AttributeScore] = []
        evidence: list[Evidence] = []
        for item in items:
            raw_slug = str(item.get("attribute", ""))
            slug = canonical_slug(raw_slug)
            if allowed_slugs and slug not in allowed_slugs and raw_slug not in allowed_slugs:
                continue
            emit_slug = raw_slug if raw_slug in allowed_slugs else slug
            raw_rel = float(item.get("relevance", 0.0))
            rel = saturate(raw_rel)
            if rel < _RELEVANCE_ITEM_FLOOR:
                continue
            state, state_from_llm, pole_rule = self._resolve_state(
                item, emit_slug, intensity, arousal, regulation
            )
            durability, durability_from_llm = self._resolve_durability(item, default_durability)
            rationale = str(item.get("rationale", "")).strip()
            span_text = str(item.get("span", "")).strip()
            reasoning = _format_attribute_reasoning(
                emit_slug=emit_slug,
                rationale=rationale,
                span_text=span_text,
                raw_relevance=raw_rel,
                final_relevance=rel,
                state=state,
                state_from_llm=state_from_llm,
                pole_rule=pole_rule,
                intensity=intensity,
                arousal=arousal,
                regulation=regulation,
                durability=durability,
                durability_from_llm=durability_from_llm,
            )
            scores.append(
                AttributeScore(
                    attribute=emit_slug,
                    relevance=round(rel, 4),
                    state=state,
                    dimension_id=dimension_id,
                    durability=durability,
                    reasoning=reasoning,
                )
            )
            detail = f"{emit_slug}: {rationale}" if rationale else emit_slug
            evidence.append(
                Evidence(
                    kind=EvidenceKind.MAPPING_PATH,
                    detail=detail[:240],
                    source="rasa_bridge",
                    weight=round(rel, 4),
                )
            )
            if span_text:
                evidence[-1] = evidence[-1].model_copy(
                    update={"detail": f'{detail[:180]} — "{span_text[:80]}"'}
                )

        scores.sort(key=lambda s: s.relevance, reverse=True)
        return scores[:_TOP_K], evidence[:_TOP_K]

    def _resolve_state(
        self,
        item: dict,
        slug: str,
        intensity: float,
        arousal: float,
        regulation: float,
    ) -> tuple[StatePole, bool, str | None]:
        state = item.get("state")
        if isinstance(state, str) and state.lower() in {s.value for s in StatePole}:
            try:
                return StatePole(state.lower()), True, None
            except ValueError:
                pass
        canon = canonical_slug(slug)
        rule = self._d8_pole_rules.get(slug, self._d8_pole_rules.get(canon, "intensity"))
        return select_pole(rule, intensity, arousal, regulation), False, rule

    @staticmethod
    def _resolve_durability(item: dict, default: Durability) -> tuple[Durability, bool]:
        raw = item.get("durability")
        if isinstance(raw, str):
            try:
                return Durability(raw.lower()), True
            except ValueError:
                pass
        return default, False

    def dimension_abstained(self, attrs: list[AttributeScore]) -> bool:
        if not attrs:
            return True
        return dimension_relevance([a.relevance for a in attrs]) < self.relevance_floor


def _format_attribute_reasoning(
    *,
    emit_slug: str,
    rationale: str,
    span_text: str,
    raw_relevance: float,
    final_relevance: float,
    state: StatePole,
    state_from_llm: bool,
    pole_rule: str | None,
    intensity: float,
    arousal: float,
    regulation: float,
    durability: Durability,
    durability_from_llm: bool,
) -> str:
    parts: list[str] = []
    if rationale:
        basis = f"Selected {emit_slug} because {rationale}"
        if span_text:
            basis += f' (supporting text: "{span_text}")'
        parts.append(basis + ".")
    elif span_text:
        parts.append(f'Selected {emit_slug} from supporting text: "{span_text}".')
    else:
        parts.append(f"Selected {emit_slug} from LLM dimension scoring.")

    saturated = saturate(raw_relevance)
    if abs(saturated - raw_relevance) > 0.001:
        parts.append(
            f"Relevance: LLM {raw_relevance:.2f} → saturated to {saturated:.4f} "
            f"(1 − e^(−γ·x), γ={GAMMA}), stored as {final_relevance:.4f}."
        )
    else:
        parts.append(
            f"Relevance: LLM {raw_relevance:.2f} → saturated to {final_relevance:.4f}."
        )

    if state_from_llm:
        parts.append(f"State: {state.value} (from LLM).")
    else:
        parts.append(
            f"State: {state.value} (pole rule '{pole_rule}' on background field: "
            f"intensity={intensity:.2f}, arousal={arousal:.2f}, regulation={regulation:.2f})."
        )

    if durability_from_llm:
        parts.append(f"Durability: {durability.value} (from LLM).")
    else:
        parts.append(f"Durability: {durability.value} (dimension default).")

    return " ".join(parts)
