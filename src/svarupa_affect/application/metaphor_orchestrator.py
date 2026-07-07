"""LLM-primary metaphor orchestration (MET v1).

One Bedrock call detects the live metaphors in a passage, extracts each
source→target structure, and maps the source imagery onto the closed KG
vocabulary of the metaphor layer's PRIMARY dimensions (D1/D5/D6/D15).
Failures degrade to abstention — never fabricate signals. Mirrors the AFF
``LivedExperienceOrchestrator`` contract.
"""

from __future__ import annotations

import asyncio
import logging
import statistics
from dataclasses import dataclass
from dataclasses import field as dc_field

from ..domain.enums import Durability, EvidenceKind, LatencyMode, StatePole
from ..domain.exceptions import ModelUnavailable
from ..domain.models import AttributeScore, Evidence, LayerContext
from ..domain.ports import IConceptRegistry, ILLMProvider, ITripletVocabulary
from ..domain.scoring import dimension_relevance, saturate
from ..infrastructure.affect.lexicons import tokenize
from ..infrastructure.kg.concept_registry import canonical_slug
from ..infrastructure.llm.prompts import metaphor_v1 as prompt_mod

logger = logging.getLogger("svarupa_affect.metaphor_primary")

# Max chars per pole description injected into the closed-vocabulary prompt block.
_STATUS_DESC_MAXLEN = 320
_RELEVANCE_ITEM_FLOOR = 0.15
_TOP_K = 5

# The metaphor layer's primary target ontology.
MET_PRIMARY_DIMENSIONS = frozenset({1, 5, 6, 15})


def _add_usage(dst: dict[str, int], src: dict[str, int] | None) -> None:
    if not src:
        return
    for key, val in src.items():
        dst[key] = dst.get(key, 0) + int(val or 0)


@dataclass(frozen=True)
class MetaphorMapping:
    """One extracted metaphor: source image → target experience."""

    source: str
    target: str
    source_domain: str = ""
    span: str = ""
    rationale: str = ""


@dataclass(frozen=True)
class MetaphorResult:
    metaphors: list[MetaphorMapping]
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


class MetaphorOrchestrator:
    def __init__(
        self,
        provider: ILLMProvider,
        concept_registry: IConceptRegistry,
        *,
        model_id: str,
        timeout_s: float = 60.0,
        max_tokens: int = 4096,
        emit_dimensions: frozenset[int] | None = None,
        triplet_vocabulary: ITripletVocabulary | None = None,
        layer_code: str = "MET",
    ) -> None:
        self._provider = provider
        self._registry = concept_registry
        self._triplets = triplet_vocabulary
        self.model_id = model_id
        self.prompt_version = prompt_mod.PROMPT_VERSION
        self._timeout = timeout_s
        self._max_tokens = max_tokens
        self._layer_code = layer_code
        primary = concept_registry.primary_dimensions(layer_code)
        self._emit_dimensions = (
            emit_dimensions
            if emit_dimensions is not None
            else (primary & MET_PRIMARY_DIMENSIONS if primary else MET_PRIMARY_DIMENSIONS)
        )

    async def score(self, ctx: LayerContext) -> MetaphorResult:
        if not ctx.enable_llm_primary:
            return self._neutral(reasons=["llm_primary_disabled"])

        salient, gate_reasons = self._salience_gate(ctx)
        if not salient:
            return self._neutral(reasons=gate_reasons, abstained=True)

        vocabulary = self._vocabulary_blocks()
        if not vocabulary:
            return self._neutral(
                reasons=gate_reasons + ["empty_vocabulary"],
                attempted=True,
                failure="no vocabulary for emit dimensions",
            )

        system = prompt_mod.build_system(vocabulary)
        prompt = prompt_mod.build_prompt(text=ctx.analysis_text)
        n = 3 if ctx.latency_mode == LatencyMode.DEEP else 1

        logger.info(
            "MET-primary starting request_id=%s prompt_version=%s model_id=%s samples=%d",
            ctx.request_id,
            self.prompt_version,
            self.model_id,
            n,
        )

        samples, last_error, usage = await self._collect_samples(
            system, prompt, n, request_id=ctx.request_id
        )
        if not samples:
            return self._neutral(
                reasons=gate_reasons + ["llm_unusable"],
                attempted=True,
                failure=last_error or "LLM returned no valid payload",
                usage=usage,
                process_confidence=0.25,
            )

        merged = self._reconcile(samples)
        conf = float(merged.get("confidence", 0.5))
        metaphors = self._metaphors_from_payload(merged)

        if merged.get("abstain", False) or not metaphors:
            return MetaphorResult(
                metaphors=metaphors,
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

        scores_by_dimension, evidence_by_dimension = self._score_dimensions(merged)
        abstained = all(
            self._dimension_abstained(scores_by_dimension.get(d, []))
            for d in sorted(self._emit_dimensions)
        )
        return MetaphorResult(
            metaphors=metaphors,
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

    # -- helpers ----------------------------------------------------------------------

    def _neutral(
        self,
        *,
        reasons: list[str],
        attempted: bool = False,
        abstained: bool = False,
        failure: str | None = None,
        usage: dict[str, int] | None = None,
        process_confidence: float = 0.2,
    ) -> MetaphorResult:
        return MetaphorResult(
            metaphors=[],
            scores_by_dimension={},
            evidence_by_dimension={},
            process_confidence=process_confidence,
            used=False,
            attempted=attempted,
            abstained=abstained,
            reasons=reasons,
            failure=failure,
            usage=usage or {},
        )

    def _salience_gate(self, ctx: LayerContext) -> tuple[bool, list[str]]:
        if ctx.force_llm_primary:
            return True, ["force_llm_primary"]
        tokens = tokenize(ctx.analysis_text)
        if len(tokens) < 4:
            return False, ["text_too_short"]
        return True, []

    def _allowed_slugs(self, dimension_id: int) -> frozenset[str]:
        return self._registry.slugs(dimension_id, self._layer_code)

    def _vocabulary_blocks(self) -> dict[int, list[dict[str, str]]]:
        """Closed vocabulary for the primary dimensions (D1/D5/D6/D15).

        Each concept carries its three pole descriptions (deficiency / balance /
        excess) from the pinned MET triplet snapshot. Balance falls back to the
        concept gloss, and if no triplet text exists the item degrades to a
        single ``gloss``.
        """
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
                poles = (
                    ("deficiency", states.get("deficiency")),
                    ("balance", states.get("balance") or glosses.get(slug)),
                    ("excess", states.get("excess")),
                )
                for status, text in poles:
                    if text:
                        item[status] = text[:_STATUS_DESC_MAXLEN]
                if len(item) == 1:  # no pole text at all -> single gloss
                    item["gloss"] = glosses.get(slug, slug)[:400]
                items.append(item)
            if items:
                out[dim_id] = items
        return out

    def _metaphors_from_payload(self, merged: dict) -> list[MetaphorMapping]:
        raw = merged.get("metaphors", [])
        out: list[MetaphorMapping] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            source = str(item.get("source", "")).strip()
            target = str(item.get("target", "")).strip()
            if not source and not target:
                continue
            out.append(
                MetaphorMapping(
                    source=source[:160],
                    target=target[:240],
                    source_domain=str(item.get("source_domain", "")).strip()[:80],
                    span=str(item.get("span", "")).strip()[:200],
                    rationale=str(item.get("rationale", "")).strip()[:400],
                )
            )
        return out[:8]

    def _score_dimensions(
        self, merged: dict
    ) -> tuple[dict[int, list[AttributeScore]], dict[int, list[Evidence]]]:
        scores_by_dimension: dict[int, list[AttributeScore]] = {}
        evidence_by_dimension: dict[int, list[Evidence]] = {}
        for dim_id in sorted(self._emit_dimensions):
            items = merged.get(prompt_mod.dim_key(dim_id), [])
            if not isinstance(items, list):
                items = []
            attrs, ev = self._score_one_dimension(items, dimension_id=dim_id)
            scores_by_dimension[dim_id] = attrs
            evidence_by_dimension[dim_id] = ev
        return scores_by_dimension, evidence_by_dimension

    def _score_one_dimension(
        self, items: list[dict], *, dimension_id: int
    ) -> tuple[list[AttributeScore], list[Evidence]]:
        allowed = self._allowed_slugs(dimension_id)
        scores: list[AttributeScore] = []
        evidence: list[Evidence] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            raw_slug = str(item.get("attribute", ""))
            slug = canonical_slug(raw_slug)
            if allowed and slug not in allowed and raw_slug not in allowed:
                continue
            emit_slug = raw_slug if raw_slug in allowed else slug
            raw_rel = float(item.get("relevance", 0.0))
            rel = saturate(raw_rel)
            if rel < _RELEVANCE_ITEM_FLOOR:
                continue
            state = _parse_state(item.get("state"))
            rationale = str(item.get("rationale", "")).strip()
            span_text = str(item.get("span", "")).strip()
            reasoning = _format_reasoning(emit_slug, rationale, span_text, raw_rel, rel, state)
            scores.append(
                AttributeScore(
                    attribute=emit_slug,
                    relevance=round(rel, 4),
                    state=state,
                    dimension_id=dimension_id,
                    durability=Durability.UNKNOWN,
                    reasoning=reasoning,
                )
            )
            detail = f"{emit_slug}: {rationale}" if rationale else emit_slug
            if span_text:
                detail = f'{detail[:180]} — "{span_text[:80]}"'
            evidence.append(
                Evidence(
                    kind=EvidenceKind.MAPPING_PATH,
                    detail=detail[:240],
                    source="metaphor_bridge",
                    weight=round(rel, 4),
                )
            )
        scores.sort(key=lambda s: s.relevance, reverse=True)
        return scores[:_TOP_K], evidence[:_TOP_K]

    @staticmethod
    def _dimension_abstained(attrs: list[AttributeScore]) -> bool:
        if not attrs:
            return True
        return dimension_relevance([a.relevance for a in attrs]) < _RELEVANCE_ITEM_FLOOR

    async def _collect_samples(
        self, system: str, prompt: str, n: int, *, request_id: str | None
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
                            "Return corrected JSON with the exact top-level keys "
                            "abstain, confidence, metaphors, d1, d5, d6, d15."
                        )
                    raw = await self._provider.complete_json(
                        system=system,
                        prompt=attempt_prompt,
                        schema=prompt_mod.METAPHOR_SCHEMA,
                        model_id=self.model_id,
                        temperature=0.2,
                        timeout_s=self._timeout,
                        max_tokens=self._max_tokens,
                        request_id=request_id,
                        attempt=attempt + 1,
                        metrics=metrics,
                    )
                    _add_usage(sample_usage, metrics)
                    return prompt_mod.validate_metaphor(raw), sample_usage
                except (prompt_mod.MetaphorValidationError, ModelUnavailable) as exc:
                    _add_usage(sample_usage, metrics)
                    last_error = str(exc)
                    logger.warning(
                        "MET-primary invalid payload (attempt %d/3): %s", attempt + 1, exc
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
        # metaphors: union deduped by lowercased source
        seen: set[str] = set()
        metaphors: list[dict] = []
        for s in samples:
            for m in s.get("metaphors", []) if isinstance(s.get("metaphors"), list) else []:
                if not isinstance(m, dict):
                    continue
                key = str(m.get("source", "")).strip().lower()
                if key and key in seen:
                    continue
                seen.add(key)
                metaphors.append(m)
        merged["metaphors"] = metaphors[:8]
        for dim in sorted(MET_PRIMARY_DIMENSIONS):
            block = prompt_mod.dim_key(dim)
            merged[block] = _merge_score_blocks([s.get(block, []) for s in samples])
        return merged


def _parse_state(raw: object) -> StatePole:
    if isinstance(raw, str):
        try:
            return StatePole(raw.lower())
        except ValueError:
            return StatePole.UNCLEAR
    return StatePole.UNCLEAR


def _format_reasoning(
    emit_slug: str,
    rationale: str,
    span_text: str,
    raw_rel: float,
    final_rel: float,
    state: StatePole,
) -> str:
    parts: list[str] = []
    if rationale:
        basis = f"Mapped source imagery to {emit_slug} because {rationale}"
        if span_text:
            basis += f' (supporting text: "{span_text}")'
        parts.append(basis + ".")
    elif span_text:
        parts.append(f'Mapped source imagery to {emit_slug} from: "{span_text}".')
    else:
        parts.append(f"Mapped source imagery to {emit_slug} from LLM metaphor scoring.")
    parts.append(f"Relevance: LLM {raw_rel:.2f} → saturated to {final_rel:.4f}.")
    parts.append(f"State: {state.value} (from LLM).")
    return " ".join(parts)


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
