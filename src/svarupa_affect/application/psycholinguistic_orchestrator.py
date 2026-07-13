"""LLM-primary psycholinguistic orchestration (PSY v1).

One Bedrock call reads linguistic form and scores D2/D12/D17 onto closed KG
vocabulary. Failures degrade to abstention — never fabricate signals.
"""

from __future__ import annotations

import asyncio
import logging
import statistics
from dataclasses import dataclass
from dataclasses import field as dc_field
from typing import Any

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
    IDimensionRegistry,
    ILLMProvider,
    IScorerRegistry,
    ITripletVocabulary,
)
from ..domain.scoring import build_uncertainty_profile, clip
from ..infrastructure.affect.lexicons import tokenize
from ..infrastructure.kg.dimension_registry import build_dimension_registry
from ..infrastructure.llm.prompts import psycholinguistic_v1 as prompt_mod
from .lived_experience_orchestrator import (
    _median_background,
    _merge_score_blocks,
    _neutral_background,
    _trim_description,
)
from .safety_shell import SafetyShell

logger = logging.getLogger("svarupa_affect.psycholinguistic_primary")

LAYER_CODE = "PSY"
_STATUS_DESC_MAXLEN = 700


def _add_usage(dst: dict[str, int], src: dict[str, int] | None) -> None:
    if not src:
        return
    for key, val in src.items():
        dst[key] = dst.get(key, 0) + int(val or 0)


@dataclass(frozen=True)
class PsycholinguisticFeatures:
    pronoun_orientation: str = ""
    agency_ratio: float = 0.5
    attribution_locus: str = "unclear"
    coherence: float = 0.5
    temporal_orientation: str = ""
    cognitive_complexity: float = 0.5
    rumination_markers: bool = False
    passive_constructions: bool = False
    rationale: str = ""


@dataclass(frozen=True)
class PsycholinguisticResult:
    field: AffectiveField
    appraisal: AppraisalProfile
    patterns: list[ExperientialPattern]
    features: PsycholinguisticFeatures
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


class PsycholinguisticOrchestrator:
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
        dimension_registry: IDimensionRegistry | None = None,
        layer_code: str = LAYER_CODE,
    ) -> None:
        self._provider = provider
        self._registry = concept_registry
        self._triplets = triplet_vocabulary
        self._dimensions = dimension_registry or build_dimension_registry()
        self._scorer_registry = scorer_registry
        self._shell = safety_shell
        self._layer_code = layer_code
        self.model_id = model_id
        self.prompt_version = prompt_mod.PROMPT_VERSION
        self._timeout = timeout_s
        self._max_tokens = max_tokens
        db_emit = scorer_registry.emit_dimensions(layer_code)
        affinity = concept_registry.primary_dimensions(layer_code)
        self._emit_dimensions = (
            emit_dimensions if emit_dimensions is not None else affinity & db_emit
        )

    async def score(self, ctx: LayerContext) -> PsycholinguisticResult:
        if not ctx.enable_llm_primary:
            return self._neutral_result(reasons=["llm_primary_disabled"])

        salient, gate_reasons = self._salience_gate(ctx)
        if not salient:
            return self._neutral_result(reasons=gate_reasons, abstained=True)

        vocabulary = self._vocabulary_blocks()
        if not vocabulary:
            return self._neutral_result(
                reasons=gate_reasons + ["empty_vocabulary"],
                attempted=True,
                failure="no vocabulary for emit dimensions",
            )

        system = prompt_mod.build_system(vocabulary, dimension_registry=self._dimensions)
        prompt = prompt_mod.build_prompt(text=ctx.analysis_text)
        schema = prompt_mod.build_schema(self._emit_dimensions)
        n = 3 if ctx.latency_mode == LatencyMode.DEEP else 1

        logger.info(
            "PSY-primary starting request_id=%s prompt_version=%s model_id=%s samples=%d",
            ctx.request_id,
            self.prompt_version,
            self.model_id,
            n,
        )

        samples, last_error, usage = await self._collect_samples(
            system, prompt, schema, n, request_id=ctx.request_id
        )
        if not samples:
            return self._neutral_result(
                reasons=gate_reasons + ["llm_unusable"],
                attempted=True,
                abstained=True,
                failure=last_error or "LLM returned no valid payload",
                usage=usage,
            )

        merged = self._reconcile(samples)
        conf = float(merged.get("confidence", 0.5))
        field = prompt_mod.field_from_payload(merged, process_confidence=conf)
        field = field.model_copy(
            update={"axis_coverage": prompt_mod.axis_coverage_from_field(field)}
        )
        appraisal = prompt_mod.appraisal_from_payload(merged, process_confidence=conf)
        patterns = prompt_mod.patterns_from_payload(merged, process_confidence=conf)
        features = self._features_from_payload(merged)

        if merged.get("abstain", False):
            return PsycholinguisticResult(
                field=field,
                appraisal=appraisal,
                patterns=patterns,
                features=features,
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

        scores_by_dimension, evidence_by_dimension = self._score_dimensions(merged, field)
        abstained = all(
            self._shell.dimension_abstained(scores_by_dimension.get(d, []))
            for d in sorted(self._emit_dimensions)
        )

        return PsycholinguisticResult(
            field=field,
            appraisal=appraisal,
            patterns=patterns,
            features=features,
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

    def build_uncertainty(self, result: PsycholinguisticResult, text: str, n_segments: int = 1):
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
        for dimension_id in sorted(self._emit_dimensions):
            block_key = prompt_mod.dim_key(dimension_id)
            allowed = self._allowed_slugs(dimension_id)
            items = merged.get(block_key, [])
            if not isinstance(items, list):
                items = []
            attrs, ev = self._shell.apply_dimension_scores(
                items,
                dimension_id=dimension_id,
                dimension_name=self._dimensions.name_for(dimension_id),
                field=field,
                allowed_slugs=allowed,
                default_durability=Durability.UNKNOWN,
            )
            scores_by_dimension[dimension_id] = attrs
            evidence_by_dimension[dimension_id] = ev
        return scores_by_dimension, evidence_by_dimension

    def _salience_gate(self, ctx: LayerContext) -> tuple[bool, list[str]]:
        if ctx.force_llm_primary:
            return True, ["force_llm_primary"]
        tokens = tokenize(ctx.analysis_text)
        if len(tokens) < 4:
            return False, ["text_too_short"]
        return True, []

    def _vocabulary_blocks(self) -> dict[int, list[dict[str, str]]]:
        out: dict[int, list[dict[str, str]]] = {}
        for dim_id in sorted(self._emit_dimensions):
            slugs = sorted(self._allowed_slugs(dim_id))
            glosses = self._registry.glosses(dim_id, list(slugs), self._layer_code)
            items: list[dict[str, str]] = []
            for slug in slugs:
                states = (
                    self._triplets.status_descriptions(dim_id, slug)
                    if self._triplets is not None
                    else {}
                )
                item: dict[str, str] = {"slug": slug}
                for status in ("deficiency", "balance", "excess"):
                    text = states.get(status)
                    if text:
                        item[status] = _trim_description(text)
                # No pole rows in svarupa_concept_descriptions → use svarupa_concepts
                # description/name as the balance pole (not a separate gloss key).
                if not any(k in item for k in ("deficiency", "balance", "excess")):
                    fallback = glosses.get(slug, slug)[:400]
                    if fallback:
                        item["balance"] = fallback
                items.append(item)
            out[dim_id] = items
        return out

    def _allowed_slugs(self, dimension_id: int) -> frozenset[str]:
        slugs = self._scorer_registry.output_slugs(dimension_id, self._layer_code)
        if slugs:
            return slugs
        return self._registry.slugs(dimension_id, self._layer_code)

    async def _collect_samples(
        self,
        system: str,
        prompt: str,
        schema: dict[str, Any],
        n: int,
        *,
        request_id: str | None,
    ) -> tuple[list[dict], str | None, dict[str, int]]:
        last_error: str | None = None

        async def one() -> tuple[dict | None, dict[str, int]]:
            nonlocal last_error
            sample_usage: dict[str, int] = {}
            for attempt in range(3):
                metrics: dict[str, int] = {}
                try:
                    attempt_prompt = prompt
                    if attempt > 0 and last_error:
                        attempt_prompt = (
                            f"{prompt}\n\nPREVIOUS RESPONSE WAS INVALID: {last_error}\n"
                            "Return corrected JSON with psycholinguistic_features as an object."
                        )
                    raw = await self._provider.complete_json(
                        system=system,
                        prompt=attempt_prompt,
                        schema=schema,
                        model_id=self.model_id,
                        temperature=0.2,
                        timeout_s=self._timeout,
                        max_tokens=self._max_tokens,
                        request_id=request_id,
                        attempt=attempt + 1,
                        metrics=metrics,
                    )
                    _add_usage(sample_usage, metrics)
                    return (
                        prompt_mod.validate_psycholinguistic(raw, self._emit_dimensions),
                        sample_usage,
                    )
                except (prompt_mod.PsycholinguisticValidationError, ModelUnavailable) as exc:
                    _add_usage(sample_usage, metrics)
                    last_error = str(exc)
                    logger.warning(
                        "PSY-primary invalid payload (attempt %d/3): %s", attempt + 1, exc
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

    def _reconcile(self, samples: list[dict]) -> dict:
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
        for dim in sorted(self._emit_dimensions):
            block = prompt_mod.dim_key(dim)
            merged[block] = _merge_score_blocks([s.get(block, []) for s in samples])
        return merged

    @staticmethod
    def _features_from_payload(merged: dict) -> PsycholinguisticFeatures:
        feats = merged.get("psycholinguistic_features", {})
        if not isinstance(feats, dict):
            feats = {}

        def _f(key: str, default: float = 0.5) -> float:
            try:
                return float(feats.get(key, default))
            except (TypeError, ValueError):
                return default

        return PsycholinguisticFeatures(
            pronoun_orientation=str(feats.get("pronoun_orientation", "")),
            agency_ratio=_f("agency_ratio", 0.5),
            attribution_locus=str(feats.get("attribution_locus", "unclear")),
            coherence=_f("coherence", 0.5),
            temporal_orientation=str(feats.get("temporal_orientation", "")),
            cognitive_complexity=_f("cognitive_complexity", 0.5),
            rumination_markers=bool(feats.get("rumination_markers", False)),
            passive_constructions=bool(feats.get("passive_constructions", False)),
            rationale=str(feats.get("rationale", "")),
        )

    def _neutral_result(
        self,
        *,
        reasons: list[str],
        attempted: bool = False,
        abstained: bool = False,
        failure: str | None = None,
        usage: dict[str, int] | None = None,
    ) -> PsycholinguisticResult:
        field = prompt_mod.field_from_payload(
            {"background_field": _neutral_background()}, process_confidence=0.2
        )
        return PsycholinguisticResult(
            field=field,
            appraisal=prompt_mod.appraisal_from_payload({}, process_confidence=0.2),
            patterns=[],
            features=PsycholinguisticFeatures(),
            scores_by_dimension={},
            evidence_by_dimension={},
            process_confidence=0.2,
            used=False,
            attempted=attempted,
            abstained=abstained,
            reasons=reasons,
            failure=failure,
            usage=usage or {},
        )
