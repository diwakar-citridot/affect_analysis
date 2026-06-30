"""ILinguisticCues adapter: agency / motivation / regulation / relational / temporal /
self-other / appraisal cues that feed the non-VAD field axes.

Rule/keyword based in v1 (a spaCy dependency parse drops in later behind this port).
Only cue keys that actually match markers are returned, so the field builder can treat
absent cues as low-coverage rather than fabricating a value.
"""

from __future__ import annotations

import re

from ...domain.enums import EvidenceKind
from ...domain.models import CueBundle, Evidence
from ...domain.scoring import clip
from .lexicons import tokenize

# Each entry: cue_key -> (positive_phrases, negative_phrases). Score in [0,1] unless the
# cue is directional (see _DIRECTIONAL), where it is mapped to [-1,1].
_CUES: dict[str, tuple[list[str], list[str]]] = {
    "agency": (
        [
            "i will",
            "i can",
            "i decided",
            "i choose",
            "i'll",
            "i am able",
            "i control",
            "i manage",
            "my choice",
            "i decide",
            "i refuse",
            "i intend",
        ],
        [
            "i can't",
            "i cannot",
            "couldn't",
            "helpless",
            "powerless",
            "trapped",
            "stuck",
            "no choice",
            "forced",
            "out of my hands",
            "nothing i can do",
        ],
    ),
    "approach": (
        [
            "want",
            "hope",
            "try",
            "reach",
            "pursue",
            "toward",
            "forward",
            "seek",
            "go for",
            "embrace",
            "look forward",
            "i wish",
            "i long",
        ],
        [],
    ),
    "avoidance": (
        [
            "avoid",
            "escape",
            "hide",
            "run away",
            "away from",
            "turn away",
            "can't face",
            "cannot stand",
            "can't stand",
            "dread",
            "withdraw",
            "pull back",
            "recoil",
            "disengage",
            "not be part",
            "don't want to",
            "shut down",
            "push away",
            "brace",
            "bracing",
            "braced",
            "fall apart",
            "expecting the worst",
            "waiting for",
            "prepared for the worst",
            "guard",
        ],
        [],
    ),
    "moral_aversion": (
        [
            "recoil",
            "turn away",
            "cannot stand",
            "can't stand",
            "disengage",
            "not be part",
            "cutting corners",
            "contempt",
            "contemptuous",
            "corrupt",
            "corruption",
            "degrading",
            "degraded",
            "repugnant",
            "unethical",
            "immoral",
            "sleazy",
            "vile",
            "will not participate",
            "refuse to be part",
        ],
        [],
    ),
    "control": (
        ["in control", "i can handle", "manage", "under control", "i've got this", "steady"],
        ["out of control", "can't control", "spiraling", "falling apart", "lose control"],
    ),
    "stability": (
        ["steady", "consistent", "stable", "grounded", "the same", "every day"],
        [
            "all over the place",
            "back and forth",
            "up and down",
            "one moment",
            "then suddenly",
            "swinging",
            "unstable",
        ],
    ),
    "persistence": (
        [
            "keep",
            "keeps",
            "still",
            "always",
            "constantly",
            "won't go away",
            "for years",
            "for months",
            "never stops",
            "every day",
            "all the time",
            "ongoing",
        ],
        ["passed", "moment", "briefly", "just now"],
    ),
    "volatility": (
        [
            "suddenly",
            "then suddenly",
            "out of nowhere",
            "swing",
            "back and forth",
            "up and down",
            "one minute",
            "all over the place",
            "snapped",
        ],
        ["steady", "calm", "consistent"],
    ),
    "regulation": (
        [
            "calm",
            "breathe",
            "centered",
            "hold it together",
            "okay",
            "i'm fine",
            "manage",
            "grounded",
            "at peace",
        ],
        [
            "overwhelmed",
            "can't stop",
            "flooded",
            "too much",
            "breaking down",
            "falling apart",
            "drowning",
            "can't cope",
        ],
    ),
    "attachment": (
        [
            "miss",
            "need you",
            "can't let go",
            "hold on",
            "depend",
            "attached",
            "close to",
            "love",
            "don't want to lose",
            "cling",
        ],
        ["let go", "don't care", "indifferent", "detached"],
    ),
    "trust": (
        ["trust", "safe", "rely", "count on", "believe in", "faith in", "secure"],
        ["betrayed", "can't trust", "suspicious", "doubt", "lied", "deceived", "unsafe"],
    ),
    "social_orientation": (
        [
            "we ",
            "us ",
            "together",
            "friend",
            "family",
            "reach out",
            "talk to",
            "with others",
            "my partner",
            "loved ones",
            "support",
        ],
        [
            "alone",
            "isolate",
            "by myself",
            "no one",
            "lonely",
            "withdraw",
            "distance",
            "shut out",
            "on my own",
        ],
    ),
    "continuity": (
        [
            "always",
            "still",
            "keep",
            "for years",
            "every day",
            "ongoing",
            "constantly",
            "all the time",
        ],
        [
            "today",
            "right now",
            "this morning",
            "just now",
            "suddenly",
            "in that moment",
            "for a moment",
        ],
    ),
    "anticipation": (
        [
            "will",
            "going to",
            "soon",
            "future",
            "tomorrow",
            "next",
            "what if",
            "expect",
            "afraid that",
            "worried that",
            "looking forward",
            "about to",
            "bracing",
            "again",
            "waiting for",
        ],
        [],
    ),
    "resolution": (
        [
            "finally",
            "resolved",
            "it's over",
            "let go",
            "moved on",
            "settled",
            "at peace",
            "made peace",
            "done with",
            "closure",
        ],
        [
            "still",
            "unresolved",
            "don't know",
            "what if",
            "can't decide",
            "stuck",
            "no answer",
            "going in circles",
        ],
    ),
    "vitality": (
        ["alive", "energy", "energized", "vibrant", "motivated", "awake", "full of life"],
        [
            "tired",
            "exhausted",
            "drained",
            "numb",
            "empty",
            "flat",
            "no energy",
            "lifeless",
            "depleted",
        ],
    ),
    "intensity": (
        [
            "so much",
            "deeply",
            "intense",
            "overwhelming",
            "unbearable",
            "can't bear",
            "powerful",
            "consuming",
        ],
        ["a little", "slightly", "somewhat", "mild"],
    ),
    "arousal": (
        ["racing", "shaking", "can't sleep", "on edge", "restless", "pounding", "tense"],
        ["calm", "relaxed", "still", "quiet"],
    ),
    # ---- appraisal cues -------------------------------------------------------------
    "novelty": (["new", "never before", "first time", "unexpected", "out of nowhere"], []),
    "expectedness": (
        ["expected", "i knew", "as usual", "of course", "always happens"],
        ["unexpected", "surprised", "out of nowhere", "never saw it coming"],
    ),
    "self_blame": (
        [
            "my fault",
            "i should have",
            "i failed",
            "blame myself",
            "because of me",
            "i messed up",
            "i'm to blame",
        ],
        [],
    ),
    "other_blame": (
        [
            "their fault",
            "they did this",
            "because of them",
            "he made me",
            "she made me",
            "they ruined",
            "blame them",
        ],
        [],
    ),
    "certainty": (
        ["definitely", "i'm sure", "i know", "certain", "clearly", "without doubt"],
        ["maybe", "not sure", "i don't know", "confused", "perhaps", "uncertain"],
    ),
    "fairness": (
        ["fair", "deserved", "justified", "right"],
        ["unfair", "not fair", "wrong", "injustice", "don't deserve", "unjust"],
    ),
    "irony": (["yeah right", "as if", "just great", "oh wonderful", "how lovely"], []),
}

# Directional cues are mapped to [-1, 1] (negative markers push below zero).
_DIRECTIONAL = {"social_orientation", "goal_congruence", "fairness"}


def _count(text: str, phrases: list[str]) -> tuple[int, list[str]]:
    hits = 0
    found: list[str] = []
    for ph in phrases:
        # word-ish boundary match (phrases may contain spaces)
        pat = re.escape(ph.strip())
        for _ in re.finditer(pat, text):
            hits += 1
            found.append(ph.strip())
    return hits, found


class LinguisticCues:
    """Adapter implementing :class:`ILinguisticCues`."""

    name = "cues"

    async def cues(self, text: str, history: list[dict[str, str]]) -> CueBundle:
        lowered = " " + text.lower() + " "
        scores: dict[str, float] = {}
        evidence: list[Evidence] = []
        fired = 0

        for key, (pos, neg) in _CUES.items():
            p, p_found = _count(lowered, pos)
            n, n_found = _count(lowered, neg)
            if p == 0 and n == 0:
                continue
            fired += 1
            if key in _DIRECTIONAL:
                raw = 0.45 * (p - n)
                value = clip(raw, -1.0, 1.0)
            else:
                raw = 0.5 + 0.22 * p - 0.22 * n
                value = clip(raw, 0.0, 1.0)
            scores[key] = round(value, 4)
            for ph in (p_found + n_found)[:2]:
                idx = text.lower().find(ph)
                span = (idx, idx + len(ph)) if idx >= 0 else None
                evidence.append(
                    Evidence(
                        kind=EvidenceKind.AXIS,
                        detail=f"cue '{key}': \"{ph}\"",
                        span=span,
                        source=self.name,
                        weight=0.6,
                    )
                )

        targets = self._targets(lowered)
        n_tokens = max(1, len(tokenize(text)))
        coverage = clip(fired / 12.0)  # ~12 cue families is "well covered"
        return CueBundle(scores=scores, coverage=coverage, targets=targets, evidence=evidence)

    @staticmethod
    def _targets(lowered: str) -> list[str]:
        targets: list[str] = []
        if re.search(r"\b(i|me|my|myself|i'm|i've)\b", lowered):
            targets.append("self")
        if re.search(
            r"\b(he|she|they|them|him|her|you|partner|friend|family|mother|father|"
            r"mom|dad|husband|wife|boss)\b",
            lowered,
        ):
            targets.append("other")
        if re.search(r"\b(work|job|exam|test|future|world|situation|life|things)\b", lowered):
            targets.append("situation")
        return targets
