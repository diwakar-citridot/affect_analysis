"""Validation suite for the Narrative Arc (NAR) layer.

Twelve executable checks, one per validation question, grounded in the
Analytical-Layers Technical Specification §3–§12 (Layer 5 — Narrative Arc) and the
31-Dimension Technical Specification §22 mapping.

There is no single ``analyze_full`` composition in the codebase yet, so ``_compose``
wires the deterministic pipeline (segment → temporal-guard → loop/mismatch → arc →
per-dimension signals) exactly as an orchestrator would, then the LLM-assist tests drive
``NarrativeLLMOrchestrator`` on top with fake providers.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from svarupa_narrative.application import arc as A
from svarupa_narrative.application import dimensions as D
from svarupa_narrative.application import events as E
from svarupa_narrative.application import loops as L
from svarupa_narrative.application.narrative_orchestrator import NarrativeLLMOrchestrator
from svarupa_narrative.domain.enums import (
    NAR_AFFINITY,
    NAR_DIMENSION_OUTPUT_KIND,
    OutputKind,
    StatePole,
    TemporalShape,
)
from svarupa_narrative.domain.models import DimensionalSignal, LayerContext, NarrativeArc
from svarupa_narrative.domain.scoring import SNAPSHOT_CAP, nar_confidence
from svarupa_narrative.infrastructure.llm.prompts import narrative_arc_v1 as P

# Representative inputs -----------------------------------------------------------------
SNAPSHOT_TEXT = "I feel scattered and hollow."  # one beat, no temporal markers
LOOP_TEXT = (
    "I started a course but I quit. Then I started a project, but I quit again. "
    "I keep going back to the same pattern."
)
MISMATCH_TEXT = (
    "I'm someone who values deep creative work, but I end up going through the motions "
    "at a job I don't care about."
)


@dataclass(frozen=True)
class Composed:
    events: list
    arc: NarrativeArc
    loop: object
    signals: list[DimensionalSignal]


def _compose(text: str, *, candidates: list[int] | None = None, shared_cues=None) -> Composed:
    """Run the deterministic NAR pipeline end to end (no LLM)."""
    events = E.build_events(text)
    has_temporal = E.has_temporal_content(text, shared_cues)
    loop = L.detect_loop(events, text)
    mismatch, alignment, mismatch_ev = L.detect_mismatch(text)
    arts = A.build_arc(events, loop, has_temporal_content=has_temporal)
    signals = D.build_signals(
        request_id="req-1",
        layer_version="0.1.0",
        full_text=text,
        events=arts.events,
        arc=arts.arc,
        loop=loop,
        mismatch=mismatch,
        alignment=alignment,
        mismatch_evidence=mismatch_ev,
        has_temporal_content=has_temporal,
        candidate_dimensions=candidates,
    )
    return Composed(events=arts.events, arc=arts.arc, loop=loop, signals=signals)


def _by_dim(signals: list[DimensionalSignal]) -> dict[int, DimensionalSignal]:
    return {s.dimension_id: s for s in signals}


# --- Fake LLM providers (spec §8) ------------------------------------------------------


class _FakeProvider:
    """Returns a well-formed stage judgement for D29."""

    async def complete_json(self, **_kw):
        return {
            "signals": [
                {
                    "dimension_id": 29,
                    "output_kind": "stage",
                    "value": {"stage": "seeking"},
                    "relevance": 0.6,
                    "confidence": 0.55,
                    "evidence_spans": ["I keep going back to the same pattern"],
                    "abstain": False,
                }
            ]
        }


class _FailProvider:
    async def complete_json(self, **_kw):
        raise RuntimeError("bedrock unavailable")


# ======================================================================================
# Q1 — Snapshot capping
# ======================================================================================
def test_q1_single_snapshot_caps_trajectory_confidence():
    c = _compose(SNAPSHOT_TEXT)
    assert c.arc.single_snapshot is True
    assert c.arc.shape is TemporalShape.NONE
    d13 = _by_dim(c.signals).get(13)
    assert d13 is not None and d13.output_kind is OutputKind.PHASE
    # a phase/mismatch/stage signal on a snapshot is hard-capped by SNAPSHOT_CAP
    assert d13.confidence < 0.25
    # the math: capped == uncapped × SNAPSHOT_CAP
    assert nar_confidence(0.6, 0.6, 0.6, snapshot=True) == round(
        nar_confidence(0.6, 0.6, 0.6, snapshot=False) * SNAPSHOT_CAP, 4
    )


# ======================================================================================
# Q2 — Loop detection (D12)
# ======================================================================================
def test_q2_loop_detected_as_cyclical_excess():
    c = _compose(LOOP_TEXT)
    assert c.loop.detected is True
    assert c.loop.severity >= 0.3
    assert c.arc.shape is TemporalShape.CYCLICAL
    assert c.arc.loop_detected is True
    d12 = _by_dim(c.signals)[12]
    assert d12.output_kind is OutputKind.POLE
    assert d12.value["pole"] == StatePole.EXCESS.value
    assert d12.state_hint is not None and d12.state_hint.state is StatePole.EXCESS
    # recurrence cue words appear in evidence
    joined = " ".join(e.detail for e in c.loop.evidence).lower()
    assert any(cue in joined for cue in ("keep", "again", "same"))


# ======================================================================================
# Q3 — Output-kind correctness per dimension (D13 phase never pole; D14 mismatch only)
# ======================================================================================
def test_q3_output_kind_per_dimension_matches_spec():
    c = _compose(LOOP_TEXT)  # candidates=None → all affinity dims emitted
    kinds = {s.dimension_id: s.output_kind.value for s in c.signals}
    for dim, expected in NAR_DIMENSION_OUTPUT_KIND.items():
        assert kinds[dim] == expected, f"D{dim} emitted {kinds[dim]}, expected {expected}"
    # D13 is a phase, never a pole
    assert kinds[13] == "phase"
    assert _by_dim(c.signals)[13].state_hint is None  # no pole/state on a phase


# ======================================================================================
# Q4 — D14 ungrounded restraint: mismatch theme only, no yuga profile
# ======================================================================================
def test_q4_d14_emits_mismatch_only_no_profile():
    c = _compose(MISMATCH_TEXT)
    d14 = _by_dim(c.signals)[14]
    assert d14.output_kind is OutputKind.MISMATCH
    assert set(d14.value.keys()) == {"mismatch"}  # a scalar theme, not a profile
    assert "profile" not in d14.value and "yuga" not in d14.value
    assert d14.state_hint is None


# ======================================================================================
# Q5 — Affinity restriction (intersect candidates with NAR affinity)
# ======================================================================================
def test_q5_affinity_restriction_drops_out_of_affinity_candidates():
    # D8 (affect) and D2 (guṇa) are out of NAR affinity and must be ignored.
    c = _compose(LOOP_TEXT, candidates=[8, 2, 12, 13])
    emitted = {s.dimension_id for s in c.signals}
    assert emitted == {12, 13}
    assert emitted <= NAR_AFFINITY
    assert 8 not in emitted and 2 not in emitted


# ======================================================================================
# Q6 — LLM assist scoping (fires only for interpretive dims 16/29/30)
# ======================================================================================
def test_q6_llm_assist_only_for_interpretive_dimensions():
    c = _compose(LOOP_TEXT, candidates=[12, 16, 29, 30])
    orch = NarrativeLLMOrchestrator(_FakeProvider(), model_id="claude-opus-4-8")

    # candidates include interpretive dims → assist attempted and D29 refined
    merged, attempted, failure = asyncio.run(
        orch.augment(c.signals, events=c.events, arc=c.arc, loop=c.loop,
                     candidate_dimensions=[12, 16, 29, 30])
    )
    assert attempted is True and failure is None
    d29 = _by_dim(merged)[29]
    assert d29.value.get("stage") == "seeking" and d29.abstained is False

    # candidates are deterministic-only (arc/loop) → assist must NOT fire
    _merged2, attempted2, _f2 = asyncio.run(
        orch.augment(c.signals, events=c.events, arc=c.arc, loop=c.loop,
                     candidate_dimensions=[12, 13])
    )
    assert attempted2 is False


# ======================================================================================
# Q7 — Consent gating for cross-entry history
# ======================================================================================
def test_q7_history_is_consent_gated_and_not_leaked():
    # opt-in default is off
    ctx = LayerContext(request_id="r", analysis_text="x")
    assert ctx.consent_history is False
    # the prompt never carries history unless a (consented) summary is passed
    dims = [{"id": 29, "name": "Bondage/Liberation", "gloss": ""}]
    without = P.build_prompt(events=["a", "b"], shape="cyclical", loop_detected=True,
                             dimensions=dims, history_summary=None)
    with_hist = P.build_prompt(events=["a", "b"], shape="cyclical", loop_detected=True,
                               dimensions=dims, history_summary="prior consented entries")
    assert "consented_history_summary" not in without
    assert "consented_history_summary" in with_hist


# ======================================================================================
# Q8 — Relevance vs confidence stay separate (cardinal rule)
# ======================================================================================
def test_q8_relevance_and_confidence_are_independent():
    c = _compose(LOOP_TEXT)
    d12 = _by_dim(c.signals)[12]
    # a strong loop: high relevance, but confidence is its own [0,1] number
    assert d12.relevance >= 0.5
    assert 0.0 <= d12.confidence <= 1.0
    # they are not the same field / not forced equal
    assert d12.relevance != d12.confidence


# ======================================================================================
# Q9 — Confidence formula (0.4·e + 0.3·a + 0.3·v) × snapshot_cap; contradiction lowers a
# ======================================================================================
def test_q9_confidence_formula_and_snapshot_cap():
    # exact formula
    assert nar_confidence(1.0, 1.0, 1.0, snapshot=False) == 1.0
    assert nar_confidence(0.0, 0.0, 0.0, snapshot=False) == 0.0
    expected = round(0.4 * 0.5 + 0.3 * 0.8 + 0.3 * 0.6, 4)
    assert nar_confidence(0.5, 0.8, 0.6, snapshot=False) == expected
    # snapshot multiplies by the cap
    assert nar_confidence(0.5, 0.8, 0.6, snapshot=True) == round(expected * SNAPSHOT_CAP, 4)
    # lower agreement (a) strictly lowers confidence
    assert nar_confidence(0.6, 0.2, 0.6, snapshot=False) < nar_confidence(0.6, 0.9, 0.6, snapshot=False)


# ======================================================================================
# Q10 — Explainability / evidence traceability
# ======================================================================================
def test_q10_signals_carry_traceable_evidence():
    c = _compose(LOOP_TEXT)
    d12 = _by_dim(c.signals)[12]
    # D12 traces to recurring events + cue words
    assert d12.evidence, "D12 must cite loop evidence"
    assert d12.reasoning
    # arc itself records ordered events and a rationale
    assert len(c.events) >= 2
    assert all(c.events[i].order == i for i in range(len(c.events)))
    assert c.arc.evidence, "arc must carry rationale evidence"

    mm = _compose(MISMATCH_TEXT)
    d14 = _by_dim(mm.signals)[14]
    # mismatch traces the value statement vs the diverging circumstance
    details = " ".join(e.detail for e in d14.evidence).lower()
    assert "value" in details or "circumstance" in details


# ======================================================================================
# Q11 — Philosophy regression: no prediction / no diagnosis; honest abstention
# ======================================================================================
def test_q11_no_future_prediction_and_honest_abstention():
    # the interpretive prompt explicitly forbids prediction/diagnosis
    assert "do NOT predict the future" in P.SYSTEM_PROMPT
    assert "diagnose" in P.SYSTEM_PROMPT

    # deterministic path for the narrative-only D29 abstains rather than guessing a stage
    c = _compose(LOOP_TEXT, candidates=[29])
    d29 = _by_dim(c.signals).get(29)
    assert d29 is not None
    assert d29.value.get("stage") == "unclear"
    assert d29.abstained is True

    # no signal text makes a forward-looking claim about the person
    banned = ("you will", "you'll", "predict", "diagnos")
    for s in c.signals:
        blob = ((s.reasoning or "") + " ".join(e.detail for e in s.evidence)).lower()
        assert not any(b in blob for b in banned)


# ======================================================================================
# Q12 — Graceful degradation on LLM-assist failure
# ======================================================================================
def test_q12_assist_failure_degrades_to_deterministic():
    c = _compose(LOOP_TEXT, candidates=[12, 16, 29, 30])
    orch = NarrativeLLMOrchestrator(_FailProvider(), model_id="claude-opus-4-8")
    merged, attempted, failure = asyncio.run(
        orch.augment(c.signals, events=c.events, arc=c.arc, loop=c.loop,
                     candidate_dimensions=[12, 16, 29, 30])
    )
    assert attempted is True
    assert failure is not None  # the failure is recorded, not swallowed as success
    # deterministic signals are preserved unchanged (the arc + loop still stand)
    assert len(merged) == len(c.signals)
    assert _by_dim(merged)[12].value["pole"] == StatePole.EXCESS.value
