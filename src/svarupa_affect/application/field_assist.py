"""LLM field-assist orchestration (§6): ambiguity gate, assist call, reconciliation.

Model-first, LLM-assisted: this runs *only* when the deterministic field flags ambiguity,
behind the ILLMProvider port. Any failure (unavailable / timeout / invalid schema) degrades
silently to the deterministic field — the LLM being absent never crashes the layer.
"""

from __future__ import annotations

import asyncio
import logging
import statistics
from dataclasses import dataclass, field as dc_field

from ..domain.enums import EvidenceKind, LatencyMode
from ..domain.exceptions import ModelUnavailable, SchemaValidationError
from ..domain.models import (
    AffectiveField,
    CoreAffect,
    Evidence,
    LayerContext,
    Motivation,
    ReconstructedFeature,
    Regulation,
)
from ..domain.ports import IKnowledgeSteward, ILLMProvider
from ..domain.scoring import clip
from ..infrastructure.affect.lexicons import tokenize
from ..infrastructure.llm.prompts import field_assist as prompt_mod

logger = logging.getLogger("svarupa_affect.llm_assist")


@dataclass
class AssistResult:
    field: AffectiveField
    used: bool = False
    attempted: bool = False
    samples: int = 0
    agreement: float = 1.0
    reasons: list[str] = dc_field(default_factory=list)
    failure: str | None = None


def is_ambiguous(
    field: AffectiveField, vad_valence: float, lexical_valence: float, margin: float, irony: float
) -> tuple[bool, list[str]]:
    """The expanded field-level ambiguity gate (§6.1)."""
    reasons: list[str] = []
    if field.ambivalence >= 0.5:
        reasons.append("emotional_ambivalence")
    if field.motivational_conflict >= 0.4 or field.motivational_direction.value == "conflicted":
        reasons.append("conflicting_motivations")
    if max(0.0, vad_valence) > 0.2 and max(0.0, -lexical_valence) > 0.2:
        reasons.append("simultaneous_positive_negative")
    if max(0.0, -vad_valence) > 0.2 and max(0.0, lexical_valence) > 0.2:
        reasons.append("simultaneous_positive_negative")
    if irony >= 0.55:
        reasons.append("irony_markers")
    if abs(vad_valence - lexical_valence) >= 0.6:
        reasons.append("source_disagreement")
    if 0.0 < margin < 0.15:
        reasons.append("low_evidence_margin")
    return (len(reasons) > 0, reasons)


def _num(x: object) -> float | None:
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, dict) and isinstance(x.get("value"), (int, float)):
        return float(x["value"])
    return None


class FieldAssist:
    def __init__(
        self,
        provider: ILLMProvider,
        steward: IKnowledgeSteward,
        *,
        model_id: str = "anthropic.claude-3-5-sonnet",
        timeout_s: float = 60.0,
        max_tokens: int = 4096,
    ) -> None:
        self._provider = provider
        self._steward = steward
        self.model_id = model_id
        self.prompt_version = prompt_mod.PROMPT_VERSION
        self._timeout = timeout_s
        self._max_tokens = max_tokens

    async def maybe_assist(
        self,
        ctx: LayerContext,
        field: AffectiveField,
        *,
        vad_valence: float,
        lexical_valence: float,
        margin: float,
        irony: float,
        candidate_d8: list[str],
        candidate_d9: list[str],
        targets: list[str],
    ) -> AssistResult:
        if not ctx.enable_llm_assist:
            return AssistResult(field=field, used=False, reasons=["assist_disabled"])

        if ctx.latency_mode == LatencyMode.FAST and not ctx.force_llm_assist:
            return AssistResult(field=field, used=False, reasons=["assist_disabled"])

        ambiguous, gate_reasons = is_ambiguous(field, vad_valence, lexical_valence, margin, irony)
        if not ambiguous and not ctx.force_llm_assist:
            return AssistResult(field=field, used=False, reasons=[])

        reasons = list(gate_reasons)
        if ctx.force_llm_assist:
            reasons = ["force_llm_assist", *reasons]

        glosses_d8 = await self._steward.glosses(8, candidate_d8)
        glosses_d9 = await self._steward.glosses(9, candidate_d9)
        prompt = prompt_mod.build_prompt(
            text=ctx.analysis_text,
            field=field,
            candidate_d8=candidate_d8,
            candidate_d9=candidate_d9,
            glosses={**glosses_d8, **glosses_d9},
            targets=targets,
        )
        n = 3 if ctx.latency_mode == LatencyMode.DEEP else 1

        logger.info(
            "LLM field-assist starting request_id=%s prompt_version=%s model_id=%s "
            "samples=%d gate_reasons=%s",
            ctx.request_id,
            self.prompt_version,
            self.model_id,
            n,
            reasons,
        )

        samples, last_error = await self._collect_samples(prompt, n, request_id=ctx.request_id)
        valid = [s for s in samples if not s.get("abstain", False)]
        if not valid:
            return AssistResult(
                field=field,
                used=False,
                attempted=True,
                reasons=reasons + ["assist_unusable"],
                failure=last_error
                or "Bedrock returned no valid assist payload (check server logs)",
            )

        merged = self._reconcile(field, valid)
        agreement = self._agreement(valid)
        return AssistResult(
            field=merged,
            used=True,
            attempted=True,
            samples=len(valid),
            agreement=agreement,
            reasons=reasons,
        )

    async def _collect_samples(
        self, prompt: str, n: int, *, request_id: str | None = None
    ) -> tuple[list[dict], str | None]:
        last_error: str | None = None

        async def one() -> dict | None:
            nonlocal last_error
            for attempt in range(3):  # initial + <=2 repair attempts
                try:
                    raw = await self._provider.complete_json(
                        system=prompt_mod.SYSTEM_PROMPT,
                        prompt=prompt,
                        schema=prompt_mod.FIELD_ASSIST_SCHEMA,
                        model_id=self.model_id,
                        temperature=0.2,
                        timeout_s=self._timeout,
                        max_tokens=self._max_tokens,
                        request_id=request_id,
                        attempt=attempt + 1,
                    )
                    return prompt_mod.validate_assist(raw)
                except (SchemaValidationError, prompt_mod.AssistValidationError) as exc:
                    last_error = str(exc)
                    logger.warning(
                        "LLM field-assist returned invalid payload (attempt %d/3): %s",
                        attempt + 1,
                        exc,
                    )
                    continue
                except ModelUnavailable as exc:
                    last_error = str(exc)
                    logger.error(
                        "LLM field-assist call failed (%s: %s); degrading to deterministic field",
                        type(exc).__name__,
                        exc,
                    )
                    return None
            last_error = last_error or "schema validation failed after repair attempts"
            logger.error("LLM field-assist exhausted repair attempts; dropping the assist")
            return None

        results = await asyncio.gather(*[one() for _ in range(n)])
        return [r for r in results if r is not None], last_error

    @staticmethod
    def _reconcile(field: AffectiveField, samples: list[dict]) -> AffectiveField:
        """Merge assist per-axis {value, confidence} into the hierarchical field (median)."""
        bf = [s.get("background_field", {}) for s in samples]
        assist_conf = statistics.fmean(float(s.get("confidence", 0.5)) for s in samples)

        def merge_group(group_obj, group_name: str, lo_map: dict[str, float]):
            updates = {}
            for attr in type(group_obj).model_fields:
                vals = [
                    _num(g.get(group_name, {}).get(attr))
                    for g in bf
                    if isinstance(g.get(group_name), dict)
                ]
                vals = [v for v in vals if v is not None]
                if not vals:
                    continue
                cur: ReconstructedFeature = getattr(group_obj, attr)
                new_value = clip(statistics.median(vals), lo_map.get(attr, 0.0), 1.0)
                new_conf = clip(0.5 * cur.confidence + 0.5 * assist_conf)
                updates[attr] = ReconstructedFeature(
                    value=round(new_value, 4),
                    confidence=round(new_conf, 4),
                    evidence=[
                        *cur.evidence,
                        Evidence(
                            kind=EvidenceKind.AXIS,
                            detail=f"reconciled with LLM field-assist ({attr})",
                            source="field_assist",
                            weight=round(assist_conf, 4),
                        ),
                    ],
                )
            return group_obj.model_copy(update=updates) if updates else group_obj

        new_core = merge_group(field.core, "core", {"valence": -1.0})
        new_mot = merge_group(field.motivation, "motivation", {})
        new_reg = merge_group(field.regulation, "regulation", {})
        if (
            isinstance(new_core, CoreAffect)
            and isinstance(new_mot, Motivation)
            and isinstance(new_reg, Regulation)
        ):
            return field.model_copy(
                update={"core": new_core, "motivation": new_mot, "regulation": new_reg}
            )
        return field

    @staticmethod
    def _agreement(samples: list[dict]) -> float:
        """Self-consistency agreement across samples (1 - dispersion of core valence)."""
        vals = [_num(s.get("background_field", {}).get("core", {}).get("valence")) for s in samples]
        vals = [v for v in vals if v is not None]
        if len(vals) < 2:
            return 1.0
        return clip(1.0 - (statistics.pstdev(vals)))


def assist_token_count(text: str) -> int:
    """Tiny helper kept for symmetry / cost accounting in tests."""
    return len(tokenize(text))
