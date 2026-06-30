"""AppraisalReconstructor (§4.2a): reconstruct *why* affect is present (appraisal theory).

Blends field axes + linguistic cues into an immutable AppraisalProfile. Each appraisal
dimension is itself a ReconstructedFeature (value + confidence + evidence).
"""

from __future__ import annotations

import json
from pathlib import Path

from ..domain.enums import EvidenceKind
from ..domain.models import (
    AffectiveField,
    AppraisalProfile,
    CueBundle,
    Evidence,
    ReconstructedFeature,
)
from ..domain.scoring import clip


class AppraisalReconstructor:
    def __init__(self, rules_path: Path) -> None:
        data = json.loads(Path(rules_path).read_text(encoding="utf-8"))
        self.version: str = data["version"]

    def reconstruct(self, field: AffectiveField, cues: CueBundle) -> AppraisalProfile:
        s = cues.scores
        conf = field.uncertainty.confidence.value
        c = clip(0.3 + 0.6 * conf)

        valence = field.core.valence.value
        arousal = field.core.arousal.value
        control = field.motivation.control.value
        agency = field.motivation.agency.value
        ambiguity = field.uncertainty.ambiguity.value

        def feat(
            value: float, detail: str, lo: float = 0.0, hi: float = 1.0
        ) -> ReconstructedFeature:
            return ReconstructedFeature(
                value=round(clip(value, lo, hi), 4),
                confidence=round(c, 4),
                evidence=[Evidence(kind=EvidenceKind.AXIS, detail=detail, source="appraisal")],
            )

        novelty = 0.4 + 0.5 * s.get("novelty", 0.0) + 0.3 * (arousal - 0.5)
        self_blame = s.get("self_blame", 0.5) - 0.5
        other_blame = s.get("other_blame", 0.5) - 0.5
        responsibility = 0.5 + (self_blame - other_blame)
        certainty = 0.5 * s.get("certainty", 0.5) + 0.5 * (1.0 - ambiguity)

        return AppraisalProfile(
            novelty=feat(novelty, "novelty <- arousal + novelty cues"),
            goal_congruence=feat(valence, "goal_congruence <- core.valence", lo=-1.0),
            controllability=feat(
                0.6 * control + 0.4 * agency, "controllability <- control + agency"
            ),
            expectedness=feat(s.get("expectedness", 0.5), "expectedness <- expectedness cues"),
            responsibility=feat(responsibility, "responsibility <- self/other blame cues"),
            certainty=feat(certainty, "certainty <- certainty cues + (1-ambiguity)"),
            fairness=feat(s.get("fairness", 0.0), "fairness <- fairness cues", lo=-1.0),
            agency=feat(agency, "agency <- motivation.agency"),
        )
