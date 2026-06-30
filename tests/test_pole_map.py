"""Pole selection (§5.4): map affect onto {deficiency, balance, excess}."""

from __future__ import annotations

from svarupa_affect.domain.enums import StatePole
from svarupa_affect.domain.scoring import select_pole


def test_intensity_high_arousal_negative_is_excess():
    assert select_pole("intensity", intensity=0.8, arousal=0.8, regulation=0.3) == StatePole.EXCESS


def test_intensity_flat_is_deficiency():
    assert (
        select_pole("intensity", intensity=0.05, arousal=0.2, regulation=0.5)
        == StatePole.DEFICIENCY
    )


def test_intensity_moderate_is_balance():
    assert select_pole("intensity", intensity=0.4, arousal=0.4, regulation=0.5) == StatePole.BALANCE


def test_equanimity_regulated_calm_is_balance():
    assert (
        select_pole("equanimity", intensity=0.4, arousal=0.3, regulation=0.7) == StatePole.BALANCE
    )


def test_equanimity_agitation_is_excess():
    assert select_pole("equanimity", intensity=0.5, arousal=0.8, regulation=0.3) == StatePole.EXCESS
