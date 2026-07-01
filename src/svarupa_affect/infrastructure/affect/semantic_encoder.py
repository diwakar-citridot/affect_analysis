"""ISemanticAffectEncoder — KG-anchor similarity for hypotheses and field axes.

Default: deterministic TF-IDF cosine similarity (no GPU, no AWS). Optional Bedrock Titan
embeddings when configured; always degrades to TF-IDF on failure.
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import re
from collections import Counter
from pathlib import Path

from ...domain.enums import EvidenceKind
from ...domain.models import Evidence, SemanticAffectFeatures
from ...domain.scoring import clip
from ..config import Settings
from .lexicons import tokenize

logger = logging.getLogger("svarupa_affect.semantic")

_SALIENCE_FLOOR = 0.20

_MD_HEADER = re.compile(r"^#+\s*")
_POS_HYPOTHESES = frozenset(
    {"joy", "love", "amusement", "hope", "enthusiasm", "serenity", "calm", "wonder"}
)
_NEG_HYPOTHESES = frozenset(
    {"sadness", "grief", "anger", "fear", "anxiety", "disgust", "moral_aversion"}
)
_ACTIVATING_HYPOTHESES = frozenset(
    {"fear", "anxiety", "anger", "surprise", "enthusiasm", "determination", "anticipation"}
)


def _compact_gloss_excerpt(gloss: str, *, max_len: int = 280) -> str:
    lines: list[str] = []
    for raw in gloss.splitlines():
        line = raw.strip()
        if not line or _MD_HEADER.match(line):
            continue
        line = re.sub(r"\s+", " ", line)
        lines.append(line)
        if sum(len(x) + 1 for x in lines) >= max_len:
            break
    text = " ".join(lines) if lines else gloss.strip()
    return text[:max_len].rstrip()


# Vyabhicārī / guṇa concept slugs -> Plutchik hypothesis anchors to enrich from KG glosses.
_CONCEPT_HYPOTHESIS_ENRICHMENT: dict[str, tuple[str, ...]] = {
    "sattva": ("serenity", "calm"),
    "rajas": ("enthusiasm", "determination"),
    "tamas": ("sadness", "calm"),
    "rati": ("love",),
    "hasa": ("amusement", "deflection"),
    "shoka": ("grief", "sadness"),
    "soka": ("grief", "sadness"),
    "krodha": ("anger",),
    "utsaha": ("enthusiasm", "determination"),
    "bhaya": ("fear", "anxiety"),
    "jugupsa": ("disgust", "moral_aversion"),
    "vismaya": ("wonder", "surprise"),
    "shama": ("serenity", "calm"),
    "sama": ("serenity", "calm"),
    "alasya": ("calm", "sadness"),
    "amarsha": ("anger",),
    "apasmara": ("surprise",),
    "asuya": ("moral_aversion", "anger"),
    "autsukya": ("anticipation", "hope"),
    "avahittha": ("deflection", "calm"),
    "avega": ("surprise", "enthusiasm"),
    "capalata": ("anticipation", "enthusiasm"),
    "cinta": ("anxiety",),
    "dainya": ("sadness", "hope"),
    "dhrti": ("serenity", "determination"),
    "garva": ("determination", "joy"),
    "glani": ("sadness", "calm"),
    "harsa": ("joy", "amusement"),
    "jadata": ("sadness", "fear"),
    "mada": ("joy", "amusement"),
    "marana": ("grief", "sadness"),
    "mati": ("determination", "serenity"),
    "moha": ("surprise", "anxiety"),
    "nidra": ("calm", "serenity"),
    "nirveda": ("sadness",),
    "sanka": ("anxiety", "fear"),
    "smrti": ("anticipation",),
    "srama": ("sadness", "calm"),
    "supta": ("calm", "serenity"),
    "trasa": ("fear", "anxiety"),
    "ugrata": ("anger",),
    "unmada": ("enthusiasm", "surprise"),
    "vibodha": ("wonder", "serenity"),
    "visada": ("sadness", "grief"),
    "vitarka": ("anticipation", "determination"),
    "vrida": ("moral_aversion", "sadness"),
    "vyadhi": ("sadness", "grief"),
}


def load_anchor_texts(
    anchors_path: Path,
    *,
    concept_glosses: dict[str, str] | None = None,
) -> tuple[dict[str, str], dict[str, str]]:
    """Load hypothesis + axis anchors; enrich from D8/D9/D2 concept glosses when provided."""
    raw = json.loads(anchors_path.read_text(encoding="utf-8"))
    hypotheses: dict[str, str] = dict(raw["hypotheses"])
    axes: dict[str, str] = dict(raw["axes"])
    if concept_glosses:
        for slug, gloss in concept_glosses.items():
            excerpt = _compact_gloss_excerpt(gloss)
            if not excerpt:
                continue
            if slug == "hasa":
                excerpt = (
                    "Defuse tension with a well-timed observation rather than confrontation; "
                    "gentle humor that diffuses seriousness and cracks rigidity without diminishing others. "
                    + excerpt
                )
            for hyp in _CONCEPT_HYPOTHESIS_ENRICHMENT.get(slug, ()):
                hypotheses[hyp] = f"{hypotheses.get(hyp, '')} {excerpt}".strip()
    return hypotheses, axes


class _TfidfIndex:
    """In-memory TF-IDF vectors for a fixed anchor corpus."""

    def __init__(self, anchors: dict[str, str]) -> None:
        self._keys = list(anchors.keys())
        tokenized = [tokenize(text) for text in anchors.values()]
        df: Counter[str] = Counter()
        for tokens in tokenized:
            df.update(set(tokens))
        n = max(1, len(tokenized))
        self._idf = {term: math.log((1 + n) / (1 + count)) + 1.0 for term, count in df.items()}
        self._vecs = [self._tfidf(tokens) for tokens in tokenized]

    def _tfidf(self, tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}
        tf = Counter(tokens)
        total = float(len(tokens))
        return {term: (count / total) * self._idf.get(term, 0.0) for term, count in tf.items()}

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(a.get(k, 0.0) * v for k, v in b.items())
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        if na <= 0.0 or nb <= 0.0:
            return 0.0
        return dot / (na * nb)

    def similarities(self, text: str) -> dict[str, float]:
        q = self._tfidf(tokenize(text))
        return {key: self._cosine(q, vec) for key, vec in zip(self._keys, self._vecs, strict=True)}


def _normalize_similarities(sims: dict[str, float]) -> dict[str, float]:
    if not sims:
        return {}
    vals = list(sims.values())
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-9:
        return {k: 0.0 for k in sims}
    return {k: round((v - lo) / (hi - lo), 4) for k, v in sims.items()}


def _distribution(sims: dict[str, float]) -> tuple[dict[str, float], float, float]:
    """Raw cosine similarities -> probability mass; abstain when peak match is weak."""
    if not sims:
        return {}, 0.0, 0.0
    peak = max(sims.values())
    if peak < _SALIENCE_FLOOR:
        return {}, 0.0, 0.0
    relative = max(0.08, peak * 0.5)
    positive = {k: v for k, v in sims.items() if v >= relative}
    if not positive:
        return {}, 0.0, 0.0
    total = sum(positive.values())
    probs = {k: round(v / total, 4) for k, v in positive.items()}
    ordered = sorted(probs.values(), reverse=True)
    margin = ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0)
    coverage = clip(len(positive) / max(1, len(sims)))
    return probs, round(coverage, 4), round(clip(margin), 4)


def _axis_valence(hyp_probs: dict[str, float]) -> float | None:
    if not hyp_probs:
        return None
    pos = sum(hyp_probs.get(h, 0.0) for h in _POS_HYPOTHESES)
    neg = sum(hyp_probs.get(h, 0.0) for h in _NEG_HYPOTHESES)
    if pos + neg < 0.05:
        return None
    return clip((pos - neg) / (pos + neg), -1.0, 1.0)


def _axis_from_hypotheses(hyp_probs: dict[str, float], axis: str) -> float | None:
    if not hyp_probs:
        return None
    if axis == "core.valence":
        return _axis_valence(hyp_probs)
    if axis == "core.arousal":
        return clip(sum(hyp_probs.get(h, 0.0) for h in _ACTIVATING_HYPOTHESES))
    if axis == "core.intensity":
        return clip(max(hyp_probs.values()))
    if axis == "motivation.avoidance":
        return clip(
            hyp_probs.get("fear", 0.0)
            + hyp_probs.get("anxiety", 0.0)
            + 0.7 * hyp_probs.get("disgust", 0.0)
            + 0.7 * hyp_probs.get("moral_aversion", 0.0)
        )
    if axis == "motivation.approach":
        return clip(
            hyp_probs.get("hope", 0.0)
            + hyp_probs.get("enthusiasm", 0.0)
            + hyp_probs.get("determination", 0.0)
            + 0.6 * hyp_probs.get("joy", 0.0)
        )
    if axis == "temporal.anticipation":
        return clip(
            hyp_probs.get("anticipation", 0.0)
            + 0.85 * hyp_probs.get("anxiety", 0.0)
            + 0.5 * hyp_probs.get("fear", 0.0)
        )
    if axis == "regulation.persistence":
        enduring = (
            hyp_probs.get("grief", 0.0)
            + hyp_probs.get("sadness", 0.0)
            + 0.7 * hyp_probs.get("fear", 0.0)
        )
        transient = hyp_probs.get("surprise", 0.0) + 0.5 * hyp_probs.get("amusement", 0.0)
        return clip(enduring - 0.35 * transient, 0.0, 1.0)
    if axis == "regulation.regulation":
        return clip(hyp_probs.get("serenity", 0.0) + hyp_probs.get("calm", 0.0))
    return None


def _build_features(
    *,
    hyp_sims: dict[str, float],
    axis_sims: dict[str, float],
    encoder_version: str,
    text: str,
) -> SemanticAffectFeatures:
    hyp_probs, cov_h, margin = _distribution(hyp_sims)
    axis_peak = max(axis_sims.values()) if axis_sims else 0.0
    axis_norm = _normalize_similarities(axis_sims) if axis_peak >= _SALIENCE_FLOOR else {}
    _, cov_a, _ = _distribution(axis_sims) if axis_peak >= _SALIENCE_FLOOR else ({}, 0.0, 0.0)

    axis_scores: dict[str, float] = dict(axis_norm)
    for axis, val in axis_norm.items():
        derived = _axis_from_hypotheses(hyp_probs, axis)
        if derived is not None:
            axis_scores[axis] = round(0.55 * val + 0.45 * derived, 4)

    evidence: list[Evidence] = []
    if hyp_probs:
        top = max(hyp_probs.items(), key=lambda kv: kv[1])
        idx = text.lower().find(top[0][:4]) if len(top[0]) >= 4 else -1
        evidence.append(
            Evidence(
                kind=EvidenceKind.EMOTION,
                detail=f"semantic anchor nearest hypothesis '{top[0]}' (p={top[1]:.3f})",
                span=None,
                source="semantic",
                weight=round(top[1], 4),
            )
        )

    return SemanticAffectFeatures(
        hypothesis_probs=hyp_probs,
        axis_scores=axis_scores,
        coverage=round(clip(0.6 * cov_h + 0.4 * cov_a), 4),
        margin=margin,
        evidence=evidence,
        encoder_version=encoder_version,
    )


class TfidfSemanticEncoder:
    """Deterministic KG-anchor encoder (default)."""

    name = "semantic_tfidf"

    def __init__(
        self,
        *,
        anchors_path: Path,
        concept_glosses: dict[str, str] | None = None,
        version: str = "tfidf_v1",
    ) -> None:
        hypotheses, axes = load_anchor_texts(anchors_path, concept_glosses=concept_glosses)
        self._hyp_anchor_texts = hypotheses
        self._axis_anchor_texts = axes
        self._hyp_index = _TfidfIndex(hypotheses)
        self._axis_index = _TfidfIndex(axes)
        self._version = version

    async def encode(self, text: str) -> SemanticAffectFeatures:
        return _build_features(
            hyp_sims=self._hyp_index.similarities(text),
            axis_sims=self._axis_index.similarities(text),
            encoder_version=self._version,
            text=text,
        )


class BedrockSemanticEncoder:
    """Bedrock Titan embeddings with TF-IDF fallback."""

    name = "semantic_bedrock"

    def __init__(
        self,
        *,
        region_name: str,
        model_id: str,
        fallback: TfidfSemanticEncoder,
        read_timeout_s: float = 30.0,
    ) -> None:
        self._fallback = fallback
        self._model_id = model_id
        self._version = f"bedrock_{model_id}"
        boto3 = self._import_boto3()
        from botocore.config import Config  # type: ignore

        cfg = Config(connect_timeout=10, read_timeout=max(15.0, read_timeout_s), retries={"max_attempts": 2})
        self._client = boto3.client("bedrock-runtime", region_name=region_name, config=cfg)
        self._hyp_anchors = dict(fallback._hyp_anchor_texts)
        self._axis_anchors = dict(fallback._axis_anchor_texts)
        self._hyp_vecs: list[list[float]] | None = None
        self._axis_vecs: list[list[float]] | None = None
        self._hyp_keys: list[str] = []
        self._axis_keys: list[str] = []

    @staticmethod
    def _import_boto3():
        try:
            import boto3  # type: ignore

            return boto3
        except ImportError as exc:
            raise RuntimeError("boto3 required for BedrockSemanticEncoder") from exc

    def _embed_sync(self, text: str) -> list[float]:
        body = json.dumps({"inputText": text[:8000]})
        resp = self._client.invoke_model(modelId=self._model_id, body=body)
        payload = json.loads(resp["body"].read())
        vec = payload.get("embedding")
        if not isinstance(vec, list):
            raise RuntimeError("Bedrock embedding response missing 'embedding'")
        return [float(x) for x in vec]

    async def _embed(self, text: str) -> list[float]:
        return await asyncio.to_thread(self._embed_sync, text)

    @staticmethod
    def _cosine_list(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b, strict=True))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na <= 0.0 or nb <= 0.0:
            return 0.0
        return dot / (na * nb)

    async def _ensure_anchor_vectors(self) -> None:
        if self._hyp_vecs is not None:
            return
        hyp_keys = list(self._hyp_anchors.keys())
        axis_keys = list(self._axis_anchors.keys())
        hyp_vecs = await asyncio.gather(*[self._embed(self._hyp_anchors[k]) for k in hyp_keys])
        axis_vecs = await asyncio.gather(*[self._embed(self._axis_anchors[k]) for k in axis_keys])
        self._hyp_keys = hyp_keys
        self._axis_keys = axis_keys
        self._hyp_vecs = list(hyp_vecs)
        self._axis_vecs = list(axis_vecs)

    async def encode(self, text: str) -> SemanticAffectFeatures:
        try:
            await self._ensure_anchor_vectors()
            q = await self._embed(text)
            assert self._hyp_vecs is not None and self._axis_vecs is not None
            hyp_sims = {
                k: self._cosine_list(q, v) for k, v in zip(self._hyp_keys, self._hyp_vecs, strict=True)
            }
            axis_sims = {
                k: self._cosine_list(q, v)
                for k, v in zip(self._axis_keys, self._axis_vecs, strict=True)
            }
            return _build_features(
                hyp_sims=hyp_sims,
                axis_sims=axis_sims,
                encoder_version=self._version,
                text=text,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Bedrock semantic encoder failed (%s); using TF-IDF fallback", exc)
            return await self._fallback.encode(text)


def _concept_glosses_for_anchors(registry: object | None) -> dict[str, str] | None:
    if registry is None:
        return None
    slugs = ["bhaya", "cinta", "trasa", "soka", "jugupsa", "hasa"]
    glosses: dict[str, str] = {}
    for slug in slugs:
        for dim in (8, 9):
            g = registry.glosses(dim, [slug])  # type: ignore[attr-defined]
            if slug in g:
                glosses[slug] = g[slug]
                break
    return glosses or None


def build_semantic_encoder(
    *,
    settings: Settings | None = None,
    concept_registry: object | None = None,
) -> TfidfSemanticEncoder | BedrockSemanticEncoder:
    """Composition root for semantic encoding (TF-IDF default; Bedrock when configured)."""
    settings = settings or Settings.load()
    anchors_path = settings.data_dir / "semantic" / "affect_anchors.v1.json"
    glosses = _concept_glosses_for_anchors(concept_registry)
    tfidf = TfidfSemanticEncoder(anchors_path=anchors_path, concept_glosses=glosses)

    mode = (settings.semantic_encoder or "tfidf").strip().lower()
    if mode == "bedrock" and settings.aws_region and settings.bedrock_embed_model_id:
        try:
            return BedrockSemanticEncoder(
                region_name=settings.aws_region,
                model_id=settings.bedrock_embed_model_id,
                fallback=tfidf,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not init Bedrock semantic encoder (%s); using TF-IDF", exc)
    return tfidf
