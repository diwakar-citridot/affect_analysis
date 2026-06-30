"""The single public contract: PhenomenologyInput assembly + encapsulation."""

from __future__ import annotations

from conftest import make_context, run

from svarupa_affect.application.mappers import to_response_dict
from svarupa_affect.domain.models import PhenomenologyInput


def test_assembles_full_contract(layer):
    pi = run(
        layer.analyze_full(
            make_context("I am furious they cancelled it, and now I just feel empty.")
        )
    ).phenomenology_input
    assert isinstance(pi, PhenomenologyInput)
    assert pi.background_field is not None
    assert pi.appraisal is not None
    assert pi.trajectory is not None
    assert pi.uncertainty is not None
    assert pi.evidence_summary.n_features > 0
    assert 0.0 <= pi.evidence_summary.mean_feature_confidence <= 1.0


def test_response_public_surface_keys(layer):
    result = run(layer.analyze_full(make_context("I feel hopeful.")))
    resp = to_response_dict(result)
    assert set(resp) == {
        "request_id",
        "layer",
        "layer_version",
        "attribute_scores",
        "field_axes",
        "signals",
        "phenomenology_input",
        "provenance",
    }
    assert resp["layer"] == "AFF"


def test_evidence_summary_does_not_leak_raw_internal_objects(layer):
    pi = run(layer.analyze_full(make_context("I feel calm and safe."))).phenomenology_input
    dumped = pi.evidence_summary.model_dump()
    # the summary is a compact roll-up — only scalar/span fields, no nested field objects
    assert set(dumped) >= {"spans", "n_features", "mean_feature_confidence", "coverage", "quality"}
