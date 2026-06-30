"""AffectDriverReconstructor (§4.2a): reconstruct *why* affect emerged.

Recognition-framed: "the language ties this to…" — never a causal verdict about the person.
Detects a proximate trigger (e.g. a ``because``-clause), and reads causal / maintaining /
contextual factors from cues + the appraisal profile.
"""

from __future__ import annotations

import re

from ..domain.enums import EvidenceKind
from ..domain.models import AffectDriver, AffectiveField, AppraisalProfile, CueBundle, Evidence
from ..domain.scoring import clip

_TRIGGER_RE = re.compile(
    r"\b(because|since|after|when|due to|now that|ever since|as a result of)\b\s*(.+?)(?:[.!?]|$)",
    re.IGNORECASE,
)


class AffectDriverReconstructor:
    def reconstruct(
        self, text: str, field: AffectiveField, appraisal: AppraisalProfile, cues: CueBundle
    ) -> list[AffectDriver]:
        s = cues.scores
        evidence: list[Evidence] = []

        trigger = "the situation described in the language"
        m = _TRIGGER_RE.search(text)
        if m:
            clause = m.group(2).strip()
            trigger = f'the language ties this to: "{clause[:120]}"'
            idx = m.start(2)
            evidence.append(
                Evidence(
                    kind=EvidenceKind.SPAN,
                    detail=f"trigger clause: {m.group(1)} …",
                    span=(idx, idx + len(clause)),
                    source="drivers",
                    weight=0.7,
                )
            )

        # maintaining factor: rumination / persistence markers
        maintaining = None
        if s.get("persistence", 0.0) >= 0.6 or field.regulation.persistence.value >= 0.6:
            maintaining = "the language suggests it is sustained (recurring / ongoing markers)"
        # causal factor: appraisal of responsibility / low controllability
        causal = None
        if appraisal.controllability.value <= 0.35:
            causal = "appraised as low in controllability"
        elif appraisal.responsibility.value >= 0.65:
            causal = "appraised with self-directed responsibility"
        elif appraisal.responsibility.value <= 0.35:
            causal = "appraised with other-/circumstance-directed responsibility"
        # contextual factor: relational vs situational target
        contextual = None
        if "other" in cues.targets:
            contextual = "a relational context (another person is referenced)"
        elif "situation" in cues.targets:
            contextual = "a situational context"

        confidence = clip(
            0.3 + 0.3 * (1.0 if m else 0.0) + 0.4 * field.uncertainty.confidence.value
        )
        driver = AffectDriver(
            trigger=trigger,
            appraisal=appraisal,
            causal_factor=causal,
            maintaining_factor=maintaining,
            contextual_factor=contextual,
            confidence=round(confidence, 4),
            evidence=evidence,
        )
        return [driver]
