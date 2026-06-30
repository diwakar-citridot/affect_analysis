"""Domain exceptions for the AFF layer."""

from __future__ import annotations


class AffectError(Exception):
    """Base class for all AFF errors."""


class ModelUnavailable(AffectError):
    """A signal source / model could not be reached."""


class SchemaValidationError(AffectError):
    """LLM output (or other payload) failed schema validation."""


class AbstainSignal(AffectError):
    """Raised internally to indicate the layer should abstain (not an error condition)."""
