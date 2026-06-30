"""ILexicalAffect adapter: lexical affect evidence (NRC-style emotion counts).

Uses ``nrclex`` when installed; otherwise the self-contained emotion lexicon.
Produces an :class:`EmotionEvidence` (probability distribution + top-1/top-2 margin),
which is a *contributor* to the field — never a result.
"""

from __future__ import annotations

from ...domain.models import EmotionEvidence
from ...domain.scoring import clip
from .lexicons import EMOTION_LEXICON, PHRASE_EMOTION_LEXICON, tokenize

try:  # pragma: no cover - optional dependency
    from nrclex import NRCLex  # type: ignore

    _HAS_NRCLEX = True
except Exception:  # noqa: BLE001
    _HAS_NRCLEX = False


def _nrclex_counts(text: str) -> dict[str, float] | None:
    """Try NRCLex; return None on import/API mismatch so we fall back to the built-in lexicon."""
    if not _HAS_NRCLEX:  # pragma: no cover - depends on optional lib
        return None
    try:
        obj = NRCLex(text)
        raw = getattr(obj, "raw_emotion_scores", None) or getattr(obj, "affect_frequencies", None)
        if not raw:
            return None
        return {k: float(v) for k, v in raw.items()}
    except Exception:  # noqa: BLE001
        return None


def _phrase_emotion_counts(text: str) -> dict[str, float]:
    lowered = text.lower()
    counts: dict[str, float] = {}
    for emotion, phrases in PHRASE_EMOTION_LEXICON.items():
        for phrase in phrases:
            if phrase in lowered:
                counts[emotion] = counts.get(emotion, 0.0) + 1.0
    return counts


def emotion_evidence(text: str) -> tuple[EmotionEvidence, float]:
    """Return (EmotionEvidence, coverage) from lexical emotion hits."""
    tokens = tokenize(text)
    n = max(1, len(tokens))

    counts: dict[str, float] = {}
    matched = 0
    nrc = _nrclex_counts(text)
    if nrc:
        counts = nrc
        matched = int(sum(counts.values()))
    else:
        for tok in tokens:
            for emotion, words in EMOTION_LEXICON.items():
                if tok in words:
                    counts[emotion] = counts.get(emotion, 0.0) + 1.0
                    matched += 1

    phrase_counts = _phrase_emotion_counts(text)
    for emotion, hits in phrase_counts.items():
        if hits <= 0:
            continue
        counts[emotion] = counts.get(emotion, 0.0) + hits
        matched += int(hits)

    total = sum(counts.values())
    if total <= 0:
        return EmotionEvidence(probs={}, margin=0.0), 0.0

    probs = {k: v / total for k, v in counts.items()}
    ordered = sorted(probs.values(), reverse=True)
    margin = ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0)
    coverage = clip(matched / n * 2.5)
    return EmotionEvidence(probs=probs, margin=clip(margin)), coverage


class NRCLexLexicalAffect:
    """Adapter implementing :class:`ILexicalAffect`."""

    name = "lexical"

    async def signals(self, text: str) -> tuple[EmotionEvidence, float]:
        return emotion_evidence(text)
