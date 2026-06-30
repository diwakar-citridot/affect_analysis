"""IEmotionEvidence adapter: discrete-emotion probabilities used ONLY as supporting evidence.

In v1 this reuses the lexical emotion distribution; a fine-tuned classifier drops in later
behind the same port with no change above ``infrastructure/``.
"""

from __future__ import annotations

from ...domain.models import EmotionEvidence
from .nrclex_lexical import emotion_evidence


class LexiconEmotionEvidence:
    """Adapter implementing :class:`IEmotionEvidence`."""

    name = "emotion_evidence"

    async def classify(self, text: str) -> tuple[EmotionEvidence, float]:
        return emotion_evidence(text)
