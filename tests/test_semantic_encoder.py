"""Semantic KG-anchor encoder: free-text similarity without phrase-list maintenance."""

from __future__ import annotations

import asyncio

from svarupa_affect.domain.models import SemanticAffectFeatures
from svarupa_affect.infrastructure.affect.semantic_encoder import TfidfSemanticEncoder
from svarupa_affect.infrastructure.config import Settings

DOCTOR_INBOX = (
    "I see the doctor's name in my inbox and I can't open it right away. "
    "I get up, refill my water, sit back down, and then I open it—but my throat is "
    "tight the whole time and I realize I've been holding my breath until I get to "
    "the actual results."
)


def _encoder() -> TfidfSemanticEncoder:
    path = Settings.load().data_dir / "semantic" / "affect_anchors.v1.json"
    return TfidfSemanticEncoder(anchors_path=path)


def test_semantic_encoder_ranks_fear_anxiety_for_medical_apprehension():
    enc = _encoder()
    feat = asyncio.run(enc.encode(DOCTOR_INBOX))
    assert isinstance(feat, SemanticAffectFeatures)
    assert feat.hypothesis_probs
    top = sorted(feat.hypothesis_probs.items(), key=lambda kv: kv[1], reverse=True)[:3]
    labels = {k for k, _ in top}
    assert labels & {"fear", "anxiety"}, f"top hypotheses {top}"


def test_semantic_axis_scores_cover_avoidance_and_anticipation():
    enc = _encoder()
    feat = asyncio.run(enc.encode(DOCTOR_INBOX))
    assert feat.axis_scores.get("motivation.avoidance", 0.0) > 0.2
    assert feat.axis_scores.get("temporal.anticipation", 0.0) > 0.2
