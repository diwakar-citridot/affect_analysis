"""AppraisalReconstructor: ranges + goal-congruence tracking valence."""

from __future__ import annotations

from pathlib import Path

from conftest import make_field

from svarupa_affect.application.appraisal import AppraisalReconstructor
from svarupa_affect.domain.models import CueBundle
from svarupa_affect.infrastructure.config import Settings


def _reconstructor() -> AppraisalReconstructor:
    return AppraisalReconstructor(Settings.load().appraisal_rules)


def test_appraisal_dims_in_range():
    ap = _reconstructor().reconstruct(make_field(), CueBundle())
    for name in type(ap).model_fields:
        feat = getattr(ap, name)
        if hasattr(feat, "value"):
            assert -1.0 <= feat.value <= 1.0
            assert 0.0 <= feat.confidence <= 1.0


def test_goal_congruence_tracks_valence():
    pos = _reconstructor().reconstruct(make_field({"core.valence": 0.8}), CueBundle())
    neg = _reconstructor().reconstruct(make_field({"core.valence": -0.8}), CueBundle())
    assert pos.goal_congruence.value > 0
    assert neg.goal_congruence.value < 0


def test_self_blame_cue_raises_responsibility():
    cues = CueBundle(scores={"self_blame": 0.94})
    ap = _reconstructor().reconstruct(make_field(), cues)
    assert ap.responsibility.value > 0.5


def test_rules_path_exists():
    assert Path(Settings.load().appraisal_rules).exists()
