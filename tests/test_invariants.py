"""Domain invariants (§3.3.0): immutable + versioned + timestamped + evidence/uncertainty-bearing."""

from __future__ import annotations

import pytest
from conftest import make_field

from svarupa_affect.domain.models import ReconstructedFeature


def test_core_objects_are_frozen():
    field = make_field()
    with pytest.raises(Exception):
        field.core = None  # type: ignore[misc]


def test_core_objects_versioned_and_timestamped():
    field = make_field()
    assert field.schema_version
    assert field.created_at is not None


def test_reconstructed_feature_requires_confidence():
    with pytest.raises(Exception):
        ReconstructedFeature(value=0.5)  # type: ignore[call-arg]


def test_confidence_bounds_enforced():
    with pytest.raises(Exception):
        ReconstructedFeature(value=0.5, confidence=1.5)


def test_feature_is_immutable():
    feat = ReconstructedFeature(value=0.5, confidence=0.6)
    with pytest.raises(Exception):
        feat.value = 0.9  # type: ignore[misc]
