"""AffectDriverReconstructor: trigger detection + recognition framing."""

from __future__ import annotations

from conftest import make_field

from svarupa_affect.application.appraisal import AppraisalReconstructor
from svarupa_affect.application.drivers import AffectDriverReconstructor
from svarupa_affect.domain.models import CueBundle
from svarupa_affect.infrastructure.config import Settings


def _appraisal(field, cues):
    return AppraisalReconstructor(Settings.load().appraisal_rules).reconstruct(field, cues)


def test_because_clause_becomes_trigger():
    text = "I feel hopeless because the project failed again."
    field = make_field({"core.valence": -0.6})
    cues = CueBundle(targets=["self", "situation"])
    drivers = AffectDriverReconstructor().reconstruct(text, field, _appraisal(field, cues), cues)
    assert drivers
    assert "ties this to" in drivers[0].trigger.lower()
    assert 0.0 <= drivers[0].confidence <= 1.0


def test_recognition_framed_not_diagnostic():
    text = "I keep ruminating since the loss."
    field = make_field({"regulation.persistence": 0.7, "core.valence": -0.5})
    cues = CueBundle(scores={"persistence": 0.8}, targets=["self"])
    drivers = AffectDriverReconstructor().reconstruct(text, field, _appraisal(field, cues), cues)
    blob = " ".join(
        filter(
            None,
            [
                drivers[0].trigger,
                drivers[0].causal_factor,
                drivers[0].maintaining_factor,
                drivers[0].contextual_factor,
            ],
        )
    )
    assert "you are" not in blob.lower()
    assert "you should" not in blob.lower()
