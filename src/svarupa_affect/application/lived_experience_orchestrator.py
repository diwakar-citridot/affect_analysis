"""LLM-primary lived-experience orchestration (AFF v2).

One Bedrock call scores field organization + D2/D8/D9 onto closed KG vocabulary.
Failures degrade to abstention — never fabricate signals.
"""

from __future__ import annotations

import asyncio
import logging
import re
import statistics
from dataclasses import dataclass
from dataclasses import field as dc_field

from ..domain.enums import Durability, LatencyMode
from ..domain.exceptions import ModelUnavailable
from ..domain.models import (
    AffectiveField,
    AppraisalProfile,
    AttributeScore,
    Evidence,
    ExperientialPattern,
    LayerContext,
)
from ..domain.ports import (
    IConceptRegistry,
    ILLMProvider,
    IScorerRegistry,
    ITripletVocabulary,
)
from ..domain.scoring import build_uncertainty_profile, clip, softmax
from ..infrastructure.affect.lexicons import tokenize
from ..infrastructure.llm.prompts import lived_experience_v1 as prompt_mod
from .safety_shell import SafetyShell

logger = logging.getLogger("svarupa_affect.llm_primary")

_FACTUAL_RE = re.compile(
    r"\b(meeting|scheduled|conference room|agenda|minutes|second floor)\b",
    re.IGNORECASE,
)

# Max chars per pole description injected into the closed-vocabulary prompt block.
# Generous because the system prefix is prompt-cached (reads bill at ~0.1x); the
# discriminative detail of a pole description is usually in its later sentences.
_STATUS_DESC_MAXLEN = 700


def _trim_description(text: str, max_len: int = _STATUS_DESC_MAXLEN) -> str:
    """Trim to ``max_len`` at a sentence boundary (mid-sentence cuts lose the
    discriminative tail of a pole description)."""
    if len(text) <= max_len:
        return text
    cut = text[:max_len]
    for stop in (". ", ".\n", "! ", "? "):
        idx = cut.rfind(stop)
        if idx > max_len // 2:
            return cut[: idx + 1]
    return cut


def _add_usage(dst: dict[str, int], src: dict[str, int] | None) -> None:
    """Accumulate token-usage counts into ``dst`` (across samples/retries)."""
    if not src:
        return
    for key, val in src.items():
        dst[key] = dst.get(key, 0) + int(val or 0)


@dataclass(frozen=True)
class LivedExperienceResult:
    field: AffectiveField
    appraisal: AppraisalProfile
    patterns: list[ExperientialPattern]
    scores_by_dimension: dict[int, list[AttributeScore]]
    evidence_by_dimension: dict[int, list[Evidence]]
    process_confidence: float
    used: bool = False
    attempted: bool = False
    abstained: bool = False
    reasons: list[str] = dc_field(default_factory=list)
    failure: str | None = None
    samples: int = 0
    usage: dict[str, int] = dc_field(default_factory=dict)


class LivedExperienceOrchestrator:
    def __init__(
        self,
        provider: ILLMProvider,
        concept_registry: IConceptRegistry,
        scorer_registry: IScorerRegistry,
        safety_shell: SafetyShell,
        *,
        model_id: str,
        timeout_s: float = 60.0,
        max_tokens: int = 4096,
        emit_dimensions: frozenset[int] | None = None,
        triplet_vocabulary: ITripletVocabulary | None = None,
    ) -> None:
        self._provider = provider
        self._registry = concept_registry
        self._triplets = triplet_vocabulary
        self._scorer_registry = scorer_registry
        self._shell = safety_shell
        self.model_id = model_id
        self.prompt_version = prompt_mod.PROMPT_VERSION
        self._timeout = timeout_s
        self._max_tokens = max_tokens
        db_emit = scorer_registry.emit_dimensions()
        affinity = concept_registry.affinity()
        self._emit_dimensions = (
            emit_dimensions if emit_dimensions is not None else affinity & db_emit
        )

    async def score(self, ctx: LayerContext) -> LivedExperienceResult:
        neutral = self._neutral_result(ctx, reasons=["orchestrator_disabled"])
        if not ctx.enable_llm_primary:
            return neutral.model_copy(update={"reasons": ["llm_primary_disabled"]})

        salient, gate_reasons = self._salience_gate(ctx)
        if not salient:
            field = prompt_mod.field_from_payload(
                {"background_field": _neutral_background()}, process_confidence=0.2
            )
            return LivedExperienceResult(
                field=field,
                appraisal=prompt_mod.appraisal_from_payload({}, process_confidence=0.2),
                patterns=[],
                scores_by_dimension={},
                evidence_by_dimension={},
                process_confidence=0.2,
                used=False,
                attempted=False,
                abstained=True,
                reasons=gate_reasons,
            )

        vocabulary = self._vocabulary_blocks()
        if not vocabulary:
            return neutral.model_copy(
                update={
                    "attempted": True,
                    "failure": "no vocabulary for emit dimensions",
                    "reasons": gate_reasons + ["empty_vocabulary"],
                }
            )

        # Static grounding (contract + closed vocabulary + task rules) is identical
        # across requests, so it goes in the cacheable system prefix; only the text
        # and hints vary per request.
        system = prompt_mod.build_system(vocabulary)
        prompt = prompt_mod.build_prompt(
            text=ctx.analysis_text,
            shared_valence=ctx.shared_features.valence if ctx.shared_features else None,
            shared_arousal=ctx.shared_features.arousal if ctx.shared_features else None,
            temporal_cues=ctx.shared_features.temporal_cues if ctx.shared_features else None,
        )
        n = 3 if ctx.latency_mode == LatencyMode.DEEP else 1

        logger.info(
            "LLM-primary starting request_id=%s prompt_version=%s model_id=%s samples=%d",
            ctx.request_id,
            self.prompt_version,
            self.model_id,
            n,
        )

        samples, last_error, usage = await self._collect_samples(
            system, prompt, n, request_id=ctx.request_id
        )
        if not samples:
            field = prompt_mod.field_from_payload(
                {"background_field": _neutral_background()}, process_confidence=0.25
            )
            return LivedExperienceResult(
                field=field,
                appraisal=prompt_mod.appraisal_from_payload({}, process_confidence=0.25),
                patterns=[],
                scores_by_dimension={},
                evidence_by_dimension={},
                process_confidence=0.25,
                used=False,
                attempted=True,
                abstained=True,
                reasons=gate_reasons + ["llm_unusable"],
                failure=last_error or "LLM returned no valid payload",
                usage=usage,
            )

        merged = self._reconcile(samples)
        if merged.get("abstain", False):
            conf = float(merged.get("confidence", 0.3))
            field = prompt_mod.field_from_payload(merged, process_confidence=conf)
            return LivedExperienceResult(
                field=field,
                appraisal=prompt_mod.appraisal_from_payload(merged, process_confidence=conf),
                patterns=prompt_mod.patterns_from_payload(merged, process_confidence=conf),
                scores_by_dimension={},
                evidence_by_dimension={},
                process_confidence=conf,
                used=True,
                attempted=True,
                abstained=True,
                reasons=gate_reasons + ["llm_abstain"],
                samples=len(samples),
                usage=usage,
            )

        conf = float(merged.get("confidence", 0.5))
        field = prompt_mod.field_from_payload(merged, process_confidence=conf)
        field = field.model_copy(
            update={"axis_coverage": prompt_mod.axis_coverage_from_field(field)}
        )
        appraisal = prompt_mod.appraisal_from_payload(merged, process_confidence=conf)
        patterns = prompt_mod.patterns_from_payload(merged, process_confidence=conf)

        scores_by_dimension, evidence_by_dimension = self._score_dimensions(merged, field)

        abstained = all(
            self._shell.dimension_abstained(scores_by_dimension.get(d, []))
            for d in sorted(self._emit_dimensions)
            if d in (2, 8, 9)
        )

        return LivedExperienceResult(
            field=field,
            appraisal=appraisal,
            patterns=patterns,
            scores_by_dimension=scores_by_dimension,
            evidence_by_dimension=evidence_by_dimension,
            process_confidence=conf,
            used=True,
            attempted=True,
            abstained=abstained,
            reasons=gate_reasons,
            samples=len(samples),
            usage=usage,
        )

    def build_uncertainty(
        self, result: LivedExperienceResult, text: str, n_segments: int = 1
    ):
        length_factor = clip(len(tokenize(text)) / 25.0)
        return build_uncertainty_profile(
            field=result.field,
            evidence_strength=result.field.uncertainty.evidence_quality.value,
            source_agreement=result.process_confidence,
            coverage=(
                sum(result.field.axis_coverage.values()) / len(result.field.axis_coverage)
                if result.field.axis_coverage
                else result.process_confidence
            ),
            mixed_valence=0.0,
            irony=0.0,
            length_factor=length_factor,
            model_margin=result.process_confidence,
            single_clause=n_segments <= 1,
        )

    def _score_dimensions(
        self, merged: dict, field: AffectiveField
    ) -> tuple[dict[int, list[AttributeScore]], dict[int, list[Evidence]]]:
        scores_by_dimension: dict[int, list[AttributeScore]] = {}
        evidence_by_dimension: dict[int, list[Evidence]] = {}
        dim_blocks = {
            8: ("d8", Durability.ENDURING),
            9: ("d9", Durability.TRANSIENT),
            2: ("d2", Durability.ENDURING),
        }
        d2_scores: list[AttributeScore] = []
        for dimension_id in sorted(self._emit_dimensions):
            if dimension_id not in dim_blocks:
                continue
            block_key, default_dur = dim_blocks[dimension_id]
            allowed = self._allowed_slugs(dimension_id)
            items = merged.get(block_key, [])
            if not isinstance(items, list):
                items = []
            attrs, ev = self._shell.apply_dimension_scores(
                items,
                dimension_id=dimension_id,
                field=field,
                allowed_slugs=allowed,
                default_durability=default_dur,
            )
            if dimension_id == 2:
                d2_scores = attrs
            elif d2_scores:
                attrs = _apply_guna_modulation_simple(attrs, _modulation_weights(d2_scores))
            scores_by_dimension[dimension_id] = attrs
            evidence_by_dimension[dimension_id] = ev
        return scores_by_dimension, evidence_by_dimension

    def _salience_gate(self, ctx: LayerContext) -> tuple[bool, list[str]]:
        if ctx.force_llm_primary:
            return True, ["force_llm_primary"]
        if ctx.latency_mode == LatencyMode.FAST and not ctx.force_llm_primary:
            # FAST still runs primary in v2 unless explicitly disabled — only thin text skips
            pass
        tokens = tokenize(ctx.analysis_text)
        if len(tokens) < 4:
            return False, ["text_too_short"]
        lowered = ctx.analysis_text.lower()
        if _FACTUAL_RE.search(lowered) and len(tokens) < 18:
            return False, ["factual_schedule"]
        return True, []

    def _vocabulary_blocks(self) -> dict[int, list[dict[str, str]]]:
        """Closed vocabulary for the primary dimensions (D2/D8/D9).

        Each concept carries its three pole descriptions (deficiency / balance /
        excess) from the pinned triplet snapshot so the model can discriminate
        against explicit poles. Balance falls back to the concept gloss, and if
        no triplet text exists at all the item degrades to a single ``gloss``.
        """
        out: dict[int, list[dict[str, str]]] = {}
        for dim_id in sorted(self._emit_dimensions):
            if dim_id not in (2, 8, 9):
                continue
            slugs = sorted(self._allowed_slugs(dim_id))
            glosses = self._registry.glosses(dim_id, list(slugs))
            items: list[dict[str, str]] = []
            for slug in slugs:
                states = (
                    self._triplets.status_descriptions(dim_id, slug)
                    if self._triplets is not None
                    else {}
                )
                item: dict[str, str] = {"slug": slug}
                poles = (
                    ("deficiency", states.get("deficiency")),
                    ("balance", states.get("balance") or glosses.get(slug)),
                    ("excess", states.get("excess")),
                )
                for status, text in poles:
                    if text:
                        item[status] = _trim_description(text)
                if len(item) == 1:  # no pole text at all -> legacy single gloss
                    item["gloss"] = glosses.get(slug, slug)[:400]
                items.append(item)
            out[dim_id] = items
        return out

    def _allowed_slugs(self, dimension_id: int) -> frozenset[str]:
        slugs = self._scorer_registry.output_slugs(dimension_id)
        if slugs:
            return slugs
        return self._registry.slugs(dimension_id)

    async def _collect_samples(
        self, system: str, prompt: str, n: int, *, request_id: str | None
    ) -> tuple[list[dict], str | None, dict[str, int]]:
        last_error: str | None = None

        async def one() -> tuple[dict | None, dict[str, int]]:
            nonlocal last_error
            sample_usage: dict[str, int] = {}
            for attempt in range(3):
                try:
                    attempt_prompt = prompt
                    if attempt > 0 and last_error:
                        attempt_prompt = (
                            f"{prompt}\n\nPREVIOUS RESPONSE WAS INVALID: {last_error}\n"
                            "Return corrected JSON with background_field as an object wrapping "
                            "core, motivation, regulation, relational, and temporal."
                        )
                    metrics: dict[str, int] = {}
                    raw = await self._provider.complete_json(
                        system=system,
                        prompt=attempt_prompt,
                        schema=prompt_mod.LIVED_EXPERIENCE_SCHEMA,
                        model_id=self.model_id,
                        temperature=0.2,
                        timeout_s=self._timeout,
                        max_tokens=self._max_tokens,
                        request_id=request_id,
                        attempt=attempt + 1,
                        metrics=metrics,
                    )
                    _add_usage(sample_usage, metrics)
                    return prompt_mod.validate_lived_experience(raw), sample_usage
                except (prompt_mod.LivedExperienceValidationError, ModelUnavailable) as exc:
                    _add_usage(sample_usage, metrics)
                    last_error = str(exc)
                    logger.warning(
                        "LLM-primary invalid payload (attempt %d/3): %s", attempt + 1, exc
                    )
                    if isinstance(exc, ModelUnavailable):
                        return None, sample_usage
                    continue
            return None, sample_usage

        results = await asyncio.gather(*[one() for _ in range(n)])
        usage_total: dict[str, int] = {}
        for _, sample_usage in results:
            _add_usage(usage_total, sample_usage)
        return [r for r, _ in results if r is not None], last_error, usage_total

    @staticmethod
    def _reconcile(samples: list[dict]) -> dict:
        if len(samples) == 1:
            return samples[0]
        abstain_votes = sum(1 for s in samples if s.get("abstain"))
        if abstain_votes >= len(samples) / 2:
            return {**samples[0], "abstain": True}
        conf = statistics.fmean(float(s.get("confidence", 0.5)) for s in samples)
        merged = dict(samples[0])
        merged["confidence"] = conf
        merged["abstain"] = False
        bg_samples = [
            s.get("background_field", {})
            for s in samples
            if isinstance(s.get("background_field"), dict)
        ]
        if bg_samples:
            merged["background_field"] = _median_background(bg_samples)
        for block in ("d8", "d9", "d2"):
            merged[block] = _merge_score_blocks([s.get(block, []) for s in samples])
        return merged

    @staticmethod
    def _neutral_result(ctx: LayerContext, *, reasons: list[str]) -> LivedExperienceResult:
        field = prompt_mod.field_from_payload(
            {"background_field": _neutral_background()}, process_confidence=0.2
        )
        return LivedExperienceResult(
            field=field,
            appraisal=prompt_mod.appraisal_from_payload({}, process_confidence=0.2),
            patterns=[],
            scores_by_dimension={},
            evidence_by_dimension={},
            process_confidence=0.2,
            reasons=reasons,
        )


def _neutral_background() -> dict:
    neutral = 0.5
    val_neutral = 0.0
    return {
        "core": {
            "valence": val_neutral,
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


def _median_background(samples: list[dict]) -> dict:
    out: dict = {}
    for group in ("core", "motivation", "regulation", "relational", "temporal"):
        attrs: dict[str, float] = {}
        for sample in samples:
            block = sample.get(group, {})
            if not isinstance(block, dict):
                continue
            for attr, val in block.items():
                attrs.setdefault(attr, []).append(prompt_mod._num(val))
        if attrs:
            out[group] = {k: statistics.median(v) for k, v in attrs.items()}
    return out


def _merge_score_blocks(blocks: list[object]) -> list[dict]:
    acc: dict[str, list[float]] = {}
    templates: dict[str, dict] = {}
    for block in blocks:
        if not isinstance(block, list):
            continue
        for item in block:
            if not isinstance(item, dict):
                continue
            slug = str(item.get("attribute", ""))
            if not slug:
                continue
            acc.setdefault(slug, []).append(float(item.get("relevance", 0.0)))
            templates[slug] = item
    merged: list[dict] = []
    for slug, rels in acc.items():
        tpl = dict(templates[slug])
        tpl["relevance"] = statistics.median(rels)
        merged.append(tpl)
    merged.sort(key=lambda x: float(x.get("relevance", 0.0)), reverse=True)
    return merged[:5]


def _modulation_weights(d2_attrs: list[AttributeScore]) -> dict[str, float]:
    raw = {a.attribute: a.relevance for a in d2_attrs}
    return softmax(raw)


def _apply_guna_modulation_simple(
    attrs: list[AttributeScore],
    weights: dict[str, float],
    *,
    beta: float = 0.3,
) -> list[AttributeScore]:
    if not attrs or not weights:
        return attrs
    family_map = {
        "rajas": "rajas",
        "sattva": "sattva",
        "tamas": "tamas",
    }
    out: list[AttributeScore] = []
    for attr in attrs:
        guna = family_map.get(attr.attribute, "")
        g = weights.get(guna, weights.get(attr.attribute, 0.0))
        prior_rel = attr.relevance
        rel = clip(attr.relevance * (1.0 + beta * g))
        modulation = (
            f" Guṇa modulation (β={beta}): relevance adjusted from {prior_rel:.4f} to "
            f"{rel:.4f} using D2 softmax weight {g:.4f}"
            + (f" for {guna}." if guna else ".")
        )
        prior_reasoning = attr.reasoning or ""
        out.append(
            attr.model_copy(
                update={
                    "relevance": round(rel, 4),
                    "reasoning": (prior_reasoning + modulation).strip(),
                }
            )
        )
    out.sort(key=lambda s: s.relevance, reverse=True)
    return out
