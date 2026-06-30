"""IVADModel adapter: valence/arousal/dominance.

Uses ``vaderSentiment`` for valence when available; otherwise a self-contained
lexicon + heuristics (negation, intensifiers, punctuation). Arousal and a coarse
dominance proxy are always heuristic in v1 (per the design's v1 scope decision).
"""

from __future__ import annotations

from ...domain.models import VAD
from ...domain.scoring import clip
from .lexicons import AROUSAL, DOMINANCE, PHRASE_VALENCE, VALENCE, tokenize

_NEGATIONS = {"not", "no", "never", "n't", "without", "hardly", "barely"}
_INTENSIFIERS = {
    "very": 1.4,
    "really": 1.3,
    "so": 1.3,
    "extremely": 1.6,
    "totally": 1.4,
    "completely": 1.5,
    "deeply": 1.4,
    "incredibly": 1.5,
    "absolutely": 1.5,
}

try:  # pragma: no cover - optional dependency
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    _VADER: SentimentIntensityAnalyzer | None = SentimentIntensityAnalyzer()
except Exception:  # noqa: BLE001
    _VADER = None


class VaderTextBlobVAD:
    """Adapter implementing :class:`IVADModel`."""

    name = "vad"

    async def score(self, text: str) -> tuple[VAD, float]:
        tokens = tokenize(text)
        n = max(1, len(tokens))

        valence, val_hits = self._valence(text, tokens)
        arousal, ar_hits = self._arousal(text, tokens)
        dominance, dom_hits = self._dominance(tokens)

        hits = len({*val_hits, *ar_hits, *dom_hits})
        coverage = clip(hits / n * 2.2)  # affect words are sparse; scale up modestly
        return VAD(valence=valence, arousal=arousal, dominance=dominance), coverage

    def _valence(self, text: str, tokens: list[str]) -> tuple[float, set[int]]:
        if _VADER is not None:  # pragma: no cover - depends on optional lib
            compound = _VADER.polarity_scores(text)["compound"]
            hits = {i for i, t in enumerate(tokens) if t in VALENCE}
            return clip(compound, -1.0, 1.0), hits

        score = 0.0
        hits: set[int] = set()
        mult = 1.0
        negate = False
        for i, tok in enumerate(tokens):
            if tok in _INTENSIFIERS:
                mult = _INTENSIFIERS[tok]
                continue
            if tok in _NEGATIONS:
                negate = True
                continue
            w = VALENCE.get(tok)
            if w is not None:
                v = w * mult * (-0.8 if negate else 1.0)
                score += v
                hits.add(i)
            mult, negate = 1.0, False

        # multiword phrases (scanned on the lowered raw text)
        lowered = text.lower()
        n_hits = len(hits)
        for phrase, w in PHRASE_VALENCE.items():
            count = lowered.count(phrase)
            if count:
                score += w * count
                n_hits += count

        if n_hits:
            score /= max(1, n_hits) ** 0.5  # dampen long lists
        # surface the phrase count via a synthetic index set for coverage accounting
        for j in range(len(hits), n_hits):
            hits.add(-(j + 1))
        return clip(score, -1.0, 1.0), hits

    def _arousal(self, text: str, tokens: list[str]) -> tuple[float, set[int]]:
        vals: list[float] = []
        hits: set[int] = set()
        for i, tok in enumerate(tokens):
            a = AROUSAL.get(tok)
            if a is not None:
                vals.append(a)
                hits.add(i)
        base = sum(vals) / len(vals) if vals else 0.35
        base += 0.1 * text.count("!")
        caps_words = sum(1 for w in text.split() if len(w) > 2 and w.isupper())
        base += 0.08 * caps_words
        return clip(base), hits

    def _dominance(self, tokens: list[str]) -> tuple[float, set[int]]:
        vals: list[float] = []
        hits: set[int] = set()
        for i, tok in enumerate(tokens):
            d = DOMINANCE.get(tok)
            if d is not None:
                vals.append(d)
                hits.add(i)
        base = sum(vals) / len(vals) if vals else 0.5
        return clip(base), hits
